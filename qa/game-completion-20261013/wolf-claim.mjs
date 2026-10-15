import { chromium } from 'file:///C:/Users/TechnoExponent/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import { writeFile } from 'node:fs/promises';

const base = process.env.AOD_PREVIEW || 'http://127.0.0.1:4537/';
const browser = await chromium.launch({ headless: true, executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe' });
const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
page.setDefaultTimeout(20000);
page.on('dialog', dialog => dialog.accept());
const wake = () => page.evaluate(() => { window.focus(); window.rebornBackground?.(false); });
async function press(choice) {
  await wake();
  const ok = await page.evaluate(id => {
    const node = [...document.querySelectorAll(`[data-choice="${id}"]`)].find(item => item.isConnected && !item.disabled);
    if (!node) return false;
    node.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true, pointerId: 1, pointerType: 'mouse' }));
    node.dispatchEvent(new PointerEvent('pointerup', { bubbles: true, pointerId: 1, pointerType: 'mouse' }));
    node.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
    return true;
  }, choice);
  if (!ok) throw new Error(`Missing ${choice}`);
}
await page.goto(base, { waitUntil: 'domcontentloaded' });
await page.waitForSelector('#app');
await wake();
await press('new-campaign');
await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'hero');
await press('scene-enter-valley');
await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'kingdom');
const plot = await page.evaluate(() => window.rebornSnapshot().plots.find(item => item.id !== 'townhall' && !item.type).id);
await page.locator(`[aria-label^="${plot}:"]`).evaluate(node => node.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true })));
const preview = await page.locator(`[data-choice="build:${plot}:barracks"]`).innerText();
await press(`build:${plot}:barracks`);
const started = Date.now();
let label = '';
while (Date.now() - started < 8000) {
  await wake();
  label = await page.locator(`[aria-label^="${plot}:"]`).getAttribute('aria-label');
  if (label.includes('level 1')) break;
  await new Promise(resolve => setTimeout(resolve, 250));
}
await press('nav:adventure');
await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'adventure');
await press('enter-adventure');
const cells = await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => resolve(document.querySelectorAll('[data-adventure-cell]').length))));
await page.locator('[data-adventure-cell="10,8"][data-open="1"]').evaluate(node => node.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true })));
const route = await page.locator('[data-choice="confirm-route"]').first().innerText();
await press('confirm-route');
await page.waitForFunction(() => (document.querySelector('#selected')?.textContent || '').includes('Travel 10,8'));
const ask = await page.locator('[data-choice="offer-dwelling:wolf"]').innerText();
await press('offer-dwelling:wolf');
const claim = await page.evaluate(() => {
  const node = document.querySelector('[data-choice="claim-dwelling"]');
  return { text: node.textContent.trim(), disabled: node.disabled };
});
let claimed = null;
if (!claim.disabled) {
  await press('claim-dwelling');
  claimed = (await page.evaluate(() => window.rebornSnapshot())).army.find(stack => stack.kind === 'creature');
  await page.locator('#save').click();
  await page.reload({ waitUntil: 'domcontentloaded' });
  await page.waitForSelector('#app');
  await wake();
  if (await page.locator('#app').getAttribute('data-view') === 'home') await press('continue');
}
const kept = await page.evaluate(() => window.rebornSnapshot()?.army?.find(stack => stack.kind === 'creature') || null);
const report = {
  generatedAt: new Date().toISOString(),
  base,
  preview, label, cells, route, ask, claim, claimed, kept,
  status: kept ? 'PASS' : 'BLOCKED',
};
await writeFile(new URL('./wolf-claim.json', import.meta.url), JSON.stringify(report, null, 2));
console.log(JSON.stringify({ status: report.status, claim: report.claim, kept: report.kept, label: report.label }));
await browser.close();
