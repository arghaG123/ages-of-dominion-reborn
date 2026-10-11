// Isolated browser check for Retreat dispatch and phone Army captions.
import { spawn } from 'node:child_process';
import { mkdtemp, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = process.cwd();
const chrome = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const port = 4531;
const debugPort = 9351;
const outDir = path.join(root, 'qa', 'whole-project-audit-20261011');

function waitFor(stream, text, child) {
  return new Promise((resolve, reject) => {
    let log = '';
    const timer = setTimeout(() => reject(new Error(log || 'timed out')), 15000);
    const onData = chunk => {
      log += chunk;
      if (log.includes(text)) {
        clearTimeout(timer);
        resolve(log);
      }
    };
    stream.on('data', onData);
    child.on('exit', code => {
      clearTimeout(timer);
      reject(new Error(`exited ${code}: ${log}`));
    });
  });
}

const server = spawn(process.execPath, ['scripts/serve.mjs', '--port', String(port)], { cwd: root, stdio: ['ignore', 'pipe', 'pipe'] });
await waitFor(server.stdout, 'Reborn local preview', server);
const profile = await mkdtemp(path.join(tmpdir(), 'aod-chrome-'));
const browser = spawn(chrome, [
  '--headless=new',
  '--disable-gpu',
  '--no-first-run',
  '--no-default-browser-check',
  `--remote-debugging-port=${debugPort}`,
  `--user-data-dir=${profile}`,
  'about:blank',
], { stdio: 'ignore' });

async function version() {
  for (let i = 0; i < 40; i++) {
    try { return await (await fetch(`http://127.0.0.1:${debugPort}/json/version`)).json(); }
    catch { await new Promise(resolve => setTimeout(resolve, 100)); }
  }
  throw new Error('Chrome DevTools did not open');
}
await version();
const page = await (await fetch(`http://127.0.0.1:${debugPort}/json/new?http://127.0.0.1:${port}/`, { method: 'PUT' })).json();
const ws = new WebSocket(page.webSocketDebuggerUrl);
await new Promise(resolve => { ws.addEventListener('open', resolve); });
let nextId = 0;
const pending = new Map();
ws.addEventListener('message', event => {
  const message = JSON.parse(event.data);
  if (message.id && pending.has(message.id)) pending.get(message.id)(message);
});
function send(method, params = {}) {
  const id = ++nextId;
  return new Promise((resolve, reject) => {
    pending.set(id, message => {
      pending.delete(id);
      if (message.error) reject(new Error(JSON.stringify(message.error)));
      else resolve(message.result);
    });
    ws.send(JSON.stringify({ id, method, params }));
  });
}
async function evaluate(expression) {
  const result = await send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true });
  if (result.exceptionDetails) throw new Error(result.exceptionDetails.text || 'evaluate failed');
  return result.result.value;
}
async function click(selector) {
  const clicked = await evaluate(`(() => { const node = document.querySelector(${JSON.stringify(selector)}); if (!node) return false; node.click(); return true; })()`);
  if (!clicked) throw new Error(`missing ${selector}`);
  await new Promise(resolve => setTimeout(resolve, 50));
}

const report = { errors: [], checks: [], screenChecks: [] };
async function capture(name) {
  const shot = await send('Page.captureScreenshot', {format:'png'});
  await writeFile(path.join(outDir,name+'.png'),Buffer.from(shot.data,'base64'));
}
try {
  await send('Page.enable');
  await send('Runtime.enable');
  await send('Emulation.setDeviceMetricsOverride', { width: 825, height: 375, deviceScaleFactor: 1, mobile: false });
  await evaluate(`new Promise(resolve => { if (document.readyState === 'complete') resolve(true); else addEventListener('load', () => resolve(true), { once: true }); })`);
  await capture('01-home');
  await click('[data-choice="new-campaign"]');
  await click('[data-choice="class:ranger"]');
  await click('[data-choice="enter-valley"]');
  await send('Emulation.setDeviceMetricsOverride', { width: 1280, height: 720, deviceScaleFactor: 1, mobile: false });
  for (const name of ['kingdom','adventure','hero','army','forge','market','tactical','defense','story','war','settings','help']) {
    await click(`[data-choice="nav:${name}"]`);
    await new Promise(resolve=>setTimeout(resolve,100));
    const detail=await evaluate(`(() => ({view:document.querySelector('#app').dataset.view,title:document.querySelector('#selected').textContent,buttons:[...document.querySelectorAll('button')].filter(x=>x.getBoundingClientRect().width>0).length,bodyCharacters:document.body.innerText.length,failedImages:[...document.querySelectorAll('img')].filter(x=>x.currentSrc&&!x.complete||x.currentSrc&&x.complete&&x.naturalWidth===0).map(x=>x.getAttribute('src'))}))()`);
    report.screenChecks.push({screen:name,pass:detail.view===name&&detail.failedImages.length===0,detail});
    if (['kingdom','adventure','hero','army','forge','tactical'].includes(name)) await capture('screen-'+name);
  }
  await send('Emulation.setDeviceMetricsOverride', { width: 825, height: 375, deviceScaleFactor: 1, mobile: false });
  await click('[data-choice="nav:war"]');
  await click('#context');
  await evaluate(`(() => { const node = [...document.querySelectorAll('button')].find(button => button.textContent === 'Skirmish'); if (!node) return false; node.click(); return true; })()`);
  await capture('tactical-skirmish');
  await click('#dock [data-choice="retreat"]');
  const retreat = await evaluate(`(() => {
    const before = { view: document.querySelector('#app').dataset.view, actions: (window.rebornActions || []).length, dialogOpen: !document.querySelector('#retreat').hidden };
    document.querySelector('[data-choice="nav:kingdom"]').click();
    const after = { view: document.querySelector('#app').dataset.view, actions: (window.rebornActions || []).length, dialogOpen: !document.querySelector('#retreat').hidden };
    return { before, after };
  })()`);
  report.checks.push({
    id: 'programmatic-navigation',
    pass: retreat.after.view === 'tactical' && retreat.after.dialogOpen && retreat.after.actions === retreat.before.actions,
    detail: retreat,
  });
  await evaluate(`document.querySelector('#retreat-cancel').click()`);
  const closed = await evaluate(`document.querySelector('#retreat').hidden && document.querySelector('#app').dataset.view === 'tactical'`);
  report.checks.push({ id: 'retreat-cancel', pass: closed === true });

  await click('[data-choice="nav:army"]');
  const viewports = [[825, 375], [933, 424], [1180, 820], [1280, 720]];
  for (const [width, height] of viewports) {
    await send('Emulation.setDeviceMetricsOverride', { width, height, deviceScaleFactor: 1, mobile: false });
    await new Promise(resolve => setTimeout(resolve, 80));
    const detail = await evaluate(`(() => {
      const stage = document.querySelector('#stage').getBoundingClientRect();
      const board = document.querySelector('#board');
      const captions = [...board.querySelectorAll('span')].map(node => {
        const font = Number.parseFloat(getComputedStyle(node).fontSize);
        const rect = node.getBoundingClientRect();
        return {
          text: node.textContent,
          font,
          inside: rect.top >= stage.top - 1 && rect.bottom <= stage.bottom + 1 && rect.left >= stage.left - 1 && rect.right <= stage.right + 1,
        };
      });
      const images = [...board.querySelectorAll('img')].map(node => {
        const rect = node.getBoundingClientRect();
        return {
          src: node.dataset.plate,
          width: rect.width,
          height: rect.height,
          inside: rect.width > 1 && rect.height > 1 && rect.top >= stage.top - 1 && rect.bottom <= stage.bottom + 1 && rect.left >= stage.left - 1 && rect.right <= stage.right + 1,
        };
      });
      return {
        view: document.querySelector('#app').dataset.view,
        frameHidden: document.querySelector('#frame').hidden,
        fitsWithoutScroll: board.scrollHeight <= board.clientHeight + 1,
        captions,
        images,
      };
    })()`);
    const pass = detail.view === 'army'
      && detail.frameHidden
      && detail.fitsWithoutScroll
      && detail.captions.length >= 4
      && detail.captions.every(row => row.font >= 14 && row.inside)
      && detail.images.length >= 3
      && detail.images.every(row => row.inside);
    report.checks.push({ id: `army-${width}x${height}`, pass, detail });
  }
} catch (error) {
  report.errors.push(String(error.stack || error));
} finally {
  report.pass = report.errors.length === 0 && report.checks.every(check => check.pass);
  await writeFile(path.join(outDir, 'browser-retreat-army.json'), JSON.stringify(report, null, 2));
  ws.close();
  browser.kill();
  server.kill();
  await new Promise(resolve => setTimeout(resolve, 300));
  const checkedProfile=path.resolve(profile);
  if (!checkedProfile.startsWith(path.resolve(tmpdir())+path.sep) || !path.basename(checkedProfile).startsWith('aod-chrome-')) throw new Error('Unsafe temporary-profile target');
  await rm(checkedProfile, { recursive: true, force: true }).catch(() => {});
}
console.log(JSON.stringify({ pass: report.pass, errors: report.errors, checks: report.checks.map(check => ({ id: check.id, pass: check.pass })) }, null, 2));
process.exit(report.pass ? 0 : 1);
