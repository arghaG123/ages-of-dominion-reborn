// Phone and desktop check for the Hero and Forge CSS controls.
import { spawn } from 'node:child_process';
import { mkdtemp, mkdir, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';

const root = process.cwd();
const chrome = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const port = Number(process.env.AOD_PORT || 4627);
const debugPort = Number(process.env.AOD_DEBUG_PORT || 9427);
const outDir = path.join(root, 'qa', 'planner-blocker-report-audit-20261011');
await mkdir(outDir, { recursive: true });
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
function waitForText(stream, text, child) {
  return new Promise((resolve, reject) => {
    let log = '';
    const timer = setTimeout(() => reject(new Error(log || 'timed out')), 15000);
    stream.on('data', chunk => { log += chunk; if (log.includes(text)) { clearTimeout(timer); resolve(log); } });
    child.on('exit', code => { clearTimeout(timer); reject(new Error(`exited ${code}: ${log}`)); });
  });
}
const server = spawn(process.execPath, ['scripts/serve.mjs', '--port', String(port)], { cwd: root, stdio: ['ignore', 'pipe', 'pipe'] });
await waitForText(server.stdout, 'Reborn local preview', server);
const profile = await mkdtemp(path.join(tmpdir(), 'aod-chrome-'));
const browser = spawn(chrome, ['--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check', '--hide-scrollbars', `--remote-debugging-port=${debugPort}`, `--user-data-dir=${profile}`, 'about:blank'], { stdio: 'ignore' });
for (let i = 0; i < 60; i++) {
  try { await (await fetch(`http://127.0.0.1:${debugPort}/json/version`)).json(); break; }
  catch { await sleep(100); }
}
const page = await (await fetch(`http://127.0.0.1:${debugPort}/json/new?http://127.0.0.1:${port}/`, { method: 'PUT' })).json();
const ws = new WebSocket(page.webSocketDebuggerUrl);
await new Promise(resolve => { ws.addEventListener('open', resolve); });
let nextId = 0;
const pending = new Map();
const consoleErrors = [];
ws.addEventListener('message', event => {
  const message = JSON.parse(event.data);
  if (message.id && pending.has(message.id)) pending.get(message.id)(message);
  else if (message.method === 'Runtime.exceptionThrown') consoleErrors.push(String(message.params.exceptionDetails?.text || 'exception'));
  else if (message.method === 'Runtime.consoleAPICalled' && message.params.type === 'error') consoleErrors.push(message.params.args.map(arg => arg.value || arg.description).join(' '));
  else if (message.method === 'Network.loadingFailed') consoleErrors.push(message.params.errorText);
  else if (message.method === 'Network.responseReceived' && message.params.response.status >= 400) consoleErrors.push(`${message.params.response.status} ${message.params.response.url}`);
});
function send(method, params = {}) {
  const id = ++nextId;
  return new Promise((resolve, reject) => {
    pending.set(id, message => { pending.delete(id); if (message.error) reject(new Error(JSON.stringify(message.error))); else resolve(message.result); });
    ws.send(JSON.stringify({ id, method, params }));
  });
}
async function evaluate(expression) {
  const result = await send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true });
  if (result.exceptionDetails) throw new Error(result.exceptionDetails.exception?.description || result.exceptionDetails.text || 'evaluate failed');
  return result.result.value;
}
const report = { screens: [], errors: [] };
try {
  await send('Page.enable');
  await send('Runtime.enable');
  await send('Network.enable');
  await send('Emulation.setDeviceMetricsOverride', { width: 1280, height: 720, deviceScaleFactor: 1, mobile: false });
  await evaluate(`new Promise(resolve => { if (document.readyState === 'complete') resolve(true); else addEventListener('load', () => resolve(true), { once: true }); })`);
  await evaluate(`document.querySelector('[data-choice="new-campaign"]').click()`);
  await sleep(200);
  const measure = `(() => {
    const box = node => { const r = node.getBoundingClientRect(); return { w: r.width, h: r.height }; };
    const controls = [...document.querySelectorAll('#scene-ui button, #scene-ui input, #choices button')].filter(node => box(node).w > 0);
    const small = controls.filter(node => { const r = box(node); return r.w < 48 || r.h < 48; }).map(node => (node.dataset.choice || node.dataset.heroSlot || node.dataset.slot || node.textContent).trim().slice(0, 48));
    const texts = [...document.querySelectorAll('#scene-ui p, #scene-ui button, #scene-ui span, #world text')].map(node => {
      const font = parseFloat(getComputedStyle(node).fontSize) || 0;
      const matrix = node.getScreenCTM?.();
      const scale = node.ownerSVGElement && matrix ? Math.hypot(matrix.a, matrix.b) : 1;
      return { text: (node.textContent || '').trim().slice(0, 40), cssFont: font * scale };
    }).filter(row => row.text);
    const knight = document.querySelector('[data-actor="knight"]');
    const weapon = document.querySelector('[data-hero-slot="weapon"]');
    return {
      view: document.querySelector('#app').dataset.view,
      presentation: knight?.dataset.presentation || '',
      reason: knight?.dataset.bodyReason || '',
      kit: knight?.dataset.kitMatch || '',
      weapon: weapon ? { worn: weapon.dataset.worn, title: weapon.querySelector('[data-slot-title]')?.textContent || '', icon: Boolean(weapon.querySelector('[data-gear-icon]')) } : null,
      svgButtons: document.querySelectorAll('#world [role="button"]').length,
      small,
      minFont: texts.length ? Math.min(...texts.map(row => row.cssFont)) : null,
      classCards: document.querySelectorAll('[data-class-card]').length,
    };
  })()`;
  report.classChoice = await evaluate(measure);
  await evaluate(`document.querySelector('[data-class-card="knight"]').click()`);
  await sleep(100);
  await evaluate(`document.querySelector('[data-choice="enter-valley"]').click()`);
  await sleep(100);
  for (const [width, height] of [[825, 375], [933, 424], [1180, 820], [1280, 720]]) {
    await send('Emulation.setDeviceMetricsOverride', { width, height, deviceScaleFactor: 1, mobile: false });
    await sleep(120);
    for (const name of ['hero', 'forge', 'kingdom', 'adventure']) {
      await evaluate(`document.querySelector('[data-choice="nav:${name}"]').click()`);
      await sleep(180);
      if (width === 825) { const shot = await send('Page.captureScreenshot', { format: 'png' }); await writeFile(path.join(outDir, name + '-825x375.png'), Buffer.from(shot.data, 'base64')); }
      const row = await evaluate(measure);
      const focused = await evaluate(`(() => { const node = document.querySelector('#scene-ui button'); if (!node) return false; node.focus(); return document.activeElement === node; })()`);
      const keyed = await evaluate(`(() => { const node = document.querySelector('#scene-ui [data-slot], #scene-ui [data-hero-slot], #scene-ui [data-class-card]'); if (!node) return false; node.focus(); node.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); return true; })()`);
      report.screens.push({ width, height, name, ...row, focused, keyed });
    }
  }
  const before = await evaluate(`window.rebornSnapshot().day`);
  await send('Emulation.setDeviceMetricsOverride', { width: 375, height: 825, deviceScaleFactor: 1, mobile: true });
  await sleep(100);
  const portrait = await evaluate(`({ rotate: getComputedStyle(document.querySelector('#rotate')).display, app: getComputedStyle(document.querySelector('#app')).display, day: window.rebornSnapshot().day })`);
  await send('Emulation.setDeviceMetricsOverride', { width: 1280, height: 720, deviceScaleFactor: 1, mobile: false });
  await sleep(100);
  const after = await evaluate(`window.rebornSnapshot().day`);
  report.portrait = { ...portrait, before, after };
  const loads = await evaluate(`(async () => {
    const hrefs = [...document.querySelectorAll('#world image, #scene-ui img')].map(node => node.getAttribute('href') || node.getAttribute('src')).filter(Boolean);
    const bad = [];
    for (const href of hrefs) {
      const response = await fetch(href);
      const type = response.headers.get('content-type') || '';
      if (!response.ok || !type.startsWith('image/')) bad.push({ href, ok: response.ok, type });
    }
    return bad;
  })()`);
  report.imageLoadFailures = loads;
} catch (error) {
  report.errors.push(String(error.stack || error));
} finally {
  report.consoleErrors = consoleErrors;
  await writeFile(path.join(outDir, 'layout.json'), JSON.stringify(report, null, 2));
  ws.close();
  browser.kill();
  server.kill();
  await sleep(200);
  const checked = path.resolve(profile);
}
const failed = report.screens.filter(row => row.small.length || (row.minFont != null && row.minFont < 12) || (['hero','forge'].includes(row.name) && row.svgButtons) || (row.name === 'hero' && (!row.weapon || row.weapon.worn !== '0' || row.weapon.icon)));
console.log(JSON.stringify({ errors: report.errors, consoleErrors, classChoice: report.classChoice, failed, portrait: report.portrait, imageLoadFailures: report.imageLoadFailures }, null, 2));
process.exit(report.errors.length || failed.length || report.imageLoadFailures?.length ? 1 : 0);
