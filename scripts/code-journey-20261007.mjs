import { spawn } from 'node:child_process';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(fileURLToPath(new URL('..', import.meta.url)));
const qa = path.join(root, 'qa/code-whole-build-20261007');
const shots = path.join(qa, 'shots');
const chrome = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const port = 9333;
const game = process.argv[2];
if (!game) throw new Error('Pass the game URL');

let chromeProc;

async function waitJson() {
  for (let attempt = 0; attempt < 40; attempt += 1) {
    try {
      const response = await fetch(`http://127.0.0.1:${port}/json/version`);
      if (response.ok) return response.json();
    } catch { /* Chrome is still starting. */ }
    await new Promise(resolve => setTimeout(resolve, 250));
  }
  throw new Error('Chrome debugging port did not open');
}

class Page {
  constructor(wsUrl) {
    this.ws = new WebSocket(wsUrl);
    this.next = 1;
    this.pending = new Map();
    this.ws.addEventListener('message', event => {
      const message = JSON.parse(event.data);
      if (message.id && this.pending.has(message.id)) {
        const { resolve, reject } = this.pending.get(message.id);
        this.pending.delete(message.id);
        if (message.error) reject(new Error(JSON.stringify(message.error)));
        else resolve(message.result);
      }
    });
  }
  ready() {
    return new Promise((resolve, reject) => {
      this.ws.addEventListener('open', resolve, { once: true });
      this.ws.addEventListener('error', reject, { once: true });
    });
  }
  send(method, params = {}) {
    const id = this.next++;
    this.ws.send(JSON.stringify({ id, method, params }));
    return new Promise((resolve, reject) => this.pending.set(id, { resolve, reject }));
  }
  async eval(expression) {
    const result = await this.send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
    if (result.exceptionDetails) throw new Error(result.exceptionDetails.text);
    return result.result.value;
  }
  async shot(name) {
    const image = await this.send('Page.captureScreenshot', { format: 'png' });
    const file = path.join(shots, name);
    await fs.writeFile(file, Buffer.from(image.data, 'base64'));
    return file;
  }
}

await fs.mkdir(shots, { recursive: true });
await fs.rm(path.join(qa, 'chrome-profile'), { recursive: true, force: true });
chromeProc = spawn(chrome, [
  '--headless=new',
  '--disable-gpu',
  '--no-first-run',
  `--remote-debugging-port=${port}`,
  `--user-data-dir=${path.join(qa, 'chrome-profile')}`,
  '--window-size=1280,720',
  'about:blank',
], { stdio: 'ignore' });
const version = await waitJson();
const browser = new Page(version.webSocketDebuggerUrl);
await browser.ready();
const created = await browser.send('Target.createTarget', { url: 'about:blank' });
const list = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
const target = list.find(item => item.id === created.targetId);
const page = new Page(target.webSocketDebuggerUrl);
await page.ready();
await page.send('Page.enable');
await page.send('Runtime.enable');

const viewports = [[825, 375], [933, 424], [1180, 820], [1280, 720]];
const report = { game, shots: [], checks: [] };

async function resize(width, height) {
  await page.send('Emulation.setDeviceMetricsOverride', { width, height, deviceScaleFactor: 1, mobile: width < 1000 });
  await page.eval('new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))');
}
async function click(selector) {
  return page.eval(`(() => { const node = document.querySelector(${JSON.stringify(selector)}); if (!node) return 'missing'; node.click(); return node.dataset.choice || node.textContent; })()`);
}
async function clickText(text) {
  return page.eval(`(() => { const node = [...document.querySelectorAll('button')].find(item => item.textContent === ${JSON.stringify(text)}); if (!node) return 'missing'; node.click(); return 'clicked'; })()`);
}

await page.send('Page.navigate', { url: game });
await page.eval('new Promise(resolve => setTimeout(resolve, 400))');
for (const [width, height] of viewports) {
  await resize(width, height);
  const file = await page.shot(`home-${width}x${height}.png`);
  const buttons = await page.eval(`(() => [...document.querySelectorAll('#gate-actions button')].map(node => ({ text: node.textContent, w: node.getBoundingClientRect().width, h: node.getBoundingClientRect().height })))()`);
  report.shots.push(file);
  report.checks.push({ screen: 'home', viewport: [width, height], buttons, small: buttons.filter(button => button.w < 48 || button.h < 48) });
}

await resize(1280, 720);
await click('[data-choice="new-campaign"]');
await page.eval('new Promise(resolve => setTimeout(resolve, 200))');
report.shots.push(await page.shot('class-select.png'));
const classes = await page.eval(`(() => [...document.querySelectorAll('[data-class-name]')].map(node => node.dataset.className))()`);
report.checks.push({ screen: 'class-select', classes });
await click('[data-choice="class:knight"]');
await click('[data-choice="enter-valley"]');
await page.eval('new Promise(resolve => setTimeout(resolve, 200))');
report.shots.push(await page.shot('kingdom-stone-empty.png'));
const pads = await page.eval(`(() => ({ pads: document.querySelectorAll('.plot').length, walls: document.querySelector('[data-walls]')?.dataset.walls, hall: document.querySelector('[aria-label="Town Hall"]') ? 'present' : 'absent' }))()`);
report.checks.push({ screen: 'kingdom', ...pads });

for (const screen of ['market', 'story', 'war', 'settings', 'help', 'army', 'forge']) {
  await click(`[data-choice="nav:${screen}"]`);
  await page.eval('new Promise(resolve => setTimeout(resolve, 150))');
  report.shots.push(await page.shot(`${screen}.png`));
  const layout = await page.eval(`document.querySelector('#world')?.dataset.supportLayout || document.querySelector('#world')?.dataset.chamber || document.querySelector('#world')?.dataset.screen || ''`);
  report.checks.push({ screen, layout });
}

await click('[data-choice="nav:war"]');
await clickText('Skirmish');
await page.eval('new Promise(resolve => setTimeout(resolve, 250))');
report.shots.push(await page.shot('skirmish.png'));
await click('[data-choice="retreat"]');
await page.eval('new Promise(resolve => setTimeout(resolve, 100))');
const open = await page.eval(`(() => ({ field: document.querySelector('#stage-field')?.inert === true, worldAncestor: Boolean(document.querySelector('#world')?.closest('[inert]')), dialog: document.querySelector('#retreat')?.hidden === false }))()`);
report.checks.push({ screen: 'retreat-open', ...open });
report.shots.push(await page.shot('retreat-open.png'));
await page.eval(`document.querySelector('#retreat-cancel').focus(); document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));`);
await page.eval('new Promise(resolve => setTimeout(resolve, 100))');
const closed = await page.eval(`(() => ({ hidden: document.querySelector('#retreat')?.hidden === true, field: document.querySelector('#stage-field')?.inert === true, focus: document.activeElement?.dataset?.choice || document.activeElement?.id || '' }))()`);
report.checks.push({ screen: 'retreat-escape', ...closed });

await fs.writeFile(path.join(qa, 'journey-report.json'), JSON.stringify(report, null, 2));
console.log(JSON.stringify(report.checks, null, 2));
chromeProc.kill();
process.exit(0);
