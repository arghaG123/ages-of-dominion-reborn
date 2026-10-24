import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';

const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
const captures = [];
const errors = [];
for (const size of [{ width: 1280, height: 720 }, { width: 825, height: 375 }]) {
  const name = `${size.width}x${size.height}`;
  const context = await browser.newContext({ viewport: size });
  const page = await context.newPage();
  page.on('pageerror', error => errors.push(String(error)));
  page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
  await page.goto('http://127.0.0.1:4179/', { waitUntil: 'networkidle' });
  const result = await page.evaluate(() => {
    const gate = document.querySelector('#gate');
    const copy = document.querySelector('#gate-copy');
    const actions = document.querySelector('#gate-actions');
    const rect = node => { const r = node.getBoundingClientRect(); return [r.x, r.y, r.width, r.height]; };
    return {
      campaignState: gate?.dataset.campaignState,
      gate: rect(gate),
      copy: rect(copy),
      actions: rect(actions),
      actionButtons: [...actions.children].map(child => ({ text: child.innerText, rect: rect(child) })),
      overflow: [document.body.scrollWidth, document.body.scrollHeight],
    };
  });
  if (result.campaignState !== 'empty') throw new Error(`${name} did not start with an empty campaign gate: ${result.campaignState}`);
  if (size.height > 500) {
    const [, gateY, , gateHeight] = result.gate;
    const [, copyY, , copyHeight] = result.copy;
    const [, actionsY, , actionsHeight] = result.actions;
    if (actionsY < copyY + copyHeight + 80 || actionsY + actionsHeight > gateY + gateHeight - 120) {
      throw new Error(`${name} empty actions did not land in the intended middle band: ${JSON.stringify(result)}`);
    }
  }
  const file = `qa/game-completion-20261019/visual-review/home-empty-live-${name}.png`;
  await page.screenshot({ path: file });
  captures.push({ name, file, result });
  await context.close();
}
if (errors.length) throw new Error(`Browser errors: ${errors.join('\n')}`);
const report = { recordedAt: new Date().toISOString(), captures, errors };
await fs.writeFile('qa/game-completion-20261019/visual-review/empty-home-layout.json', JSON.stringify(report, null, 2));
console.log(JSON.stringify(report, null, 2));
await browser.close();
