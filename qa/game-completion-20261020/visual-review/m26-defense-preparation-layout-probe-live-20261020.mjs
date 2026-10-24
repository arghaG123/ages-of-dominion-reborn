import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import worlds from '../../../src/data/adventure-worlds.json' with { type: 'json' };
import fs from 'node:fs/promises';
import path from 'node:path';

const root = process.cwd();
const out = path.join(root, 'qa/game-completion-20261020/visual-review/defense-preparation-layout-probe');
await fs.mkdir(out, { recursive: true });
const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
const context = await browser.newContext({ viewport: { width: 825, height: 375 } });
const page = await context.newPage();
async function click(selector) {
  const target = page.locator(selector).first();
  await target.waitFor({ state: 'visible', timeout: 10000 });
  await target.click();
}
await page.goto('http://127.0.0.1:4179/?audit=m26-defense-layout', { waitUntil: 'networkidle' });
await click('[data-choice="new-campaign"]');
await click(`[data-choice="campaign-world:${worlds[10].id}"]`);
await click('[data-choice="begin-selected-world"]');
await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'hero');
await click('[data-choice="scene-class:knight"]');
await click('[data-choice="scene-enter-valley"]');
await page.locator('[data-choice="nav:war"]').first().click();
await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'war');
await click('#scene-ui [data-choice="start-endless"]');
await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'defense');
await click('#dock [data-choice="inspect:defense"]');
await page.waitForTimeout(100);
const layout = await page.evaluate(() => {
  const panel = document.querySelector('#panel');
  const choices = document.querySelector('#choices');
  const box = element => {
    const rect = element.getBoundingClientRect();
    const css = getComputedStyle(element);
    return { tag: element.tagName, choice: element.dataset.choice || '', text: element.textContent.trim().replace(/\s+/g, ' ').slice(0, 100), rect: [rect.x, rect.y, rect.width, rect.height], display: css.display, position: css.position, overflow: css.overflow, gridColumn: css.gridColumn, flex: css.flex };
  };
  return {
    view: document.querySelector('#app')?.dataset.view,
    sheet: panel.dataset.sheet,
    panel: box(panel),
    panelChildren: [...panel.children].map(box),
    choices: { ...box(choices), clientHeight: choices.clientHeight, scrollHeight: choices.scrollHeight, scrollTop: choices.scrollTop, children: [...choices.children].map(box) },
  };
});
const screenshot = path.join(out, 'prep-825x375.png');
await page.screenshot({ path: screenshot });
await fs.writeFile(path.join(out, 'report.json'), JSON.stringify({ layout, screenshot: path.relative(root, screenshot) }, null, 2) + '\n');
await browser.close();
console.log(JSON.stringify({ layout, screenshot: path.relative(root, screenshot) }, null, 2));
