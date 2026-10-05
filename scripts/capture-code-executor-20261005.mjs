// Isolated Chrome capture for the 5 Oct code pass. Uses its own profile and port.
import { spawn } from 'node:child_process';
import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(fileURLToPath(new URL('..', import.meta.url)));
const out = path.join(root, 'qa', 'code-executor-20261005');
const chrome = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const port = 4197;
const debugPort = 9337;
const profile = path.join(process.env.TEMP || out, 'aod-code-executor-chrome-20261005');
const sizes = [[825, 375], [933, 424], [1180, 820], [1280, 720]];

function sleep(ms) { return new Promise(resolve => setTimeout(resolve, ms)); }

async function waitOk(url, asJson) {
  let last = '';
  for (let attempt = 0; attempt < 40; attempt += 1) {
    try {
      const response = await fetch(url);
      if (response.ok) return asJson ? await response.json() : await response.text();
      last = String(response.status);
    } catch (error) { last = error.message; }
    await sleep(250);
  }
  throw new Error(`No response at ${url}: ${last}`);
}

function connect(wsUrl) {
  const ws = new WebSocket(wsUrl);
  let id = 0;
  const pending = new Map();
  const opened = new Promise((resolve, reject) => {
    ws.addEventListener('open', resolve);
    ws.addEventListener('error', () => reject(new Error('debugger socket failed')));
  });
  ws.addEventListener('message', event => {
    const message = JSON.parse(event.data);
    if (message.id && pending.has(message.id)) {
      const done = pending.get(message.id);
      pending.delete(message.id);
      if (message.error) done.reject(new Error(JSON.stringify(message.error)));
      else done.resolve(message.result);
    }
  });
  return {
    ready: opened,
    send(method, params = {}) {
      const msgId = ++id;
      return new Promise((resolve, reject) => {
        pending.set(msgId, { resolve, reject });
        ws.send(JSON.stringify({ id: msgId, method, params }));
      });
    },
    close() { ws.close(); },
  };
}

async function evaluate(session, expression) {
  const result = await session.send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true });
  if (result.exceptionDetails) throw new Error(result.exceptionDetails.text || 'page exception');
  return result.result?.value;
}

async function shot(session, file) {
  const image = await session.send('Page.captureScreenshot', { format: 'png' });
  await writeFile(file, Buffer.from(image.data, 'base64'));
}

const server = spawn(process.execPath, ['scripts/serve.mjs', '--port', String(port)], { cwd: root, stdio: ['ignore', 'pipe', 'pipe'] });
let serverLog = '';
server.stdout.on('data', chunk => { serverLog += chunk; });
server.stderr.on('data', chunk => { serverLog += chunk; });
const browser = spawn(chrome, [
  `--remote-debugging-port=${debugPort}`,
  `--user-data-dir=${profile}`,
  '--headless=new',
  '--disable-gpu',
  '--disable-extensions',
  '--no-first-run',
  '--no-default-browser-check',
  'about:blank',
], { stdio: 'ignore' });

const report = { port, sizes, shots: [], errors: [] };
try {
  await waitOk(`http://127.0.0.1:${port}/`, false);
  await waitOk(`http://127.0.0.1:${debugPort}/json/version`, true);
  const created = await fetch(`http://127.0.0.1:${debugPort}/json/new?${encodeURIComponent(`http://127.0.0.1:${port}/`)}`, { method: 'PUT' });
  if (!created.ok) throw new Error(`Could not open a page target: ${created.status}`);
  const page = await created.json();
  const session = connect(page.webSocketDebuggerUrl);
  await session.ready;
  await session.send('Page.enable');
  await session.send('Runtime.enable');
  await session.send('Page.navigate', { url: `http://127.0.0.1:${port}/` });
  await sleep(600);
  await evaluate(session, `document.querySelector('[data-choice="new-campaign"]').click()`);
  await evaluate(session, `document.querySelector('[data-choice="class:ranger"]').click()`);
  await evaluate(session, `document.querySelector('[data-choice="enter-valley"]').click()`);
  await evaluate(session, `document.querySelector('#context').click()`);
  await mkdir(path.join(out, 'pixels'), { recursive: true });
  for (const [width, height] of sizes) {
    await session.send('Emulation.setDeviceMetricsOverride', { width, height, deviceScaleFactor: 1, mobile: width < 1000 });
    await sleep(250);
    const file = path.join(out, 'pixels', `kingdom-${width}x${height}.png`);
    await shot(session, file);
    const readout = await evaluate(session, `({
      message: document.querySelector('#message')?.textContent || '',
      empty: document.querySelectorAll('[data-pad-state="empty"]').length,
      presentation: document.querySelector('[data-presentation]')?.getAttribute('data-presentation') || '',
      dock: [...document.querySelectorAll('#dock button')].map(node => node.textContent),
    })`);
    report.shots.push({ file: path.relative(root, file).replaceAll('\\', '/'), width, height, screen: 'kingdom', readout });
  }
  await session.send('Emulation.setDeviceMetricsOverride', { width: 1280, height: 720, deviceScaleFactor: 1, mobile: false });
  await evaluate(session, `document.querySelector('[data-choice="nav:war"]').click()`);
  await evaluate(session, `[...document.querySelectorAll('button')].find(node => node.textContent === 'Skirmish').click()`);
  await sleep(200);
  const tactical = await evaluate(session, `({
    message: document.querySelector('#message')?.textContent || '',
    dock: [...document.querySelectorAll('#dock button')].map(node => node.textContent),
    panel: [...document.querySelectorAll('#choices button')].map(node => node.textContent).slice(0, 12),
    pressed: document.querySelector('#dock button[aria-pressed="true"]')?.textContent || '',
    movesInDock: [...document.querySelectorAll('#dock button')].filter(node => node.textContent.startsWith('Move to')).length,
  })`);
  const tacticalFile = path.join(out, 'pixels', 'tactical-1280x720.png');
  await shot(session, tacticalFile);
  report.shots.push({ file: path.relative(root, tacticalFile).replaceAll('\\', '/'), width: 1280, height: 720, screen: 'tactical', readout: tactical });
  await session.send('Emulation.setDeviceMetricsOverride', { width: 825, height: 375, deviceScaleFactor: 1, mobile: true });
  await sleep(200);
  const phoneFile = path.join(out, 'pixels', 'tactical-825x375.png');
  await shot(session, phoneFile);
  const phoneRead = await evaluate(session, `({
    panel: [...document.querySelectorAll('#choices button')].slice(0, 3).map(node => ({ text: node.textContent, height: node.getBoundingClientRect().height })),
    labels: [...document.querySelectorAll('#world text')].map(node => node.textContent),
  })`);
  report.shots.push({ file: path.relative(root, phoneFile).replaceAll('\\', '/'), width: 825, height: 375, screen: 'tactical', readout: { ...tactical, phoneRead } });
  const more = [
    ['adventure', `document.querySelector('[data-choice="nav:adventure"]').click(); document.querySelector('[data-choice="enter-adventure"]')?.click();`],
    ['defense', `document.querySelector('[data-choice="nav-more"]').click(); document.querySelector('[data-choice="nav:defense"]').click();`],
    ['forge', `document.querySelector('[data-choice="nav:forge"]').click();`],
    ['settings', `document.querySelector('[data-choice="nav:settings"]').click();`],
    ['help', `document.querySelector('[data-choice="nav:help"]').click();`],
  ];
  await session.send('Emulation.setDeviceMetricsOverride', { width: 1280, height: 720, deviceScaleFactor: 1, mobile: false });
  for (const [name, expression] of more) {
    await evaluate(session, expression);
    await sleep(200);
    const extra = path.join(out, 'pixels', `${name}-1280x720.png`);
    await shot(session, extra);
    const readout = await evaluate(session, `({
      selected: document.querySelector('#selected')?.textContent || '',
      message: document.querySelector('#message')?.textContent || '',
      choices: [...document.querySelectorAll('#choices button,#dock button')].map(node => node.textContent).slice(0, 8),
    })`);
    report.shots.push({ file: path.relative(root, extra).replaceAll('\\', '/'), width: 1280, height: 720, screen: name, readout });
  }
  session.close();
  report.serverLog = serverLog.trim();
} catch (error) {
  report.errors.push(String(error.stack || error));
  report.serverLog = serverLog.trim();
} finally {
  browser.kill();
  server.kill();
}
await mkdir(out, { recursive: true });
await writeFile(path.join(out, 'report.json'), JSON.stringify(report, null, 2));
if (report.errors.length) {
  console.error(report.errors.join('\n'));
  process.exit(1);
}
console.log(JSON.stringify(report.shots.map(shot => ({ file: shot.file, dock: shot.readout.dock, pressed: shot.readout.pressed, empty: shot.readout.empty, movesInDock: shot.readout.movesInDock })), null, 2));
