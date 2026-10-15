// Fresh isolated preview. Checks the scaffold worker uses the joint gait and six worn slots.
import { chromium } from 'file:///C:/Users/TechnoExponent/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import { writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';

const base = process.env.AOD_PREVIEW;
const chrome = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const browser = await chromium.launch({ executablePath: chrome, headless: true });
const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
const errors = [];
page.on('pageerror', error => errors.push(String(error)));
await page.goto(base, { waitUntil: 'domcontentloaded' });
await page.evaluate(() => window.rebornBackground?.(false));
const press = async (choice) => {
  const clicked = await page.evaluate(id => {
    const nodes = [...document.querySelectorAll(`[data-choice="${id}"]`)].filter(node => node.isConnected && !node.disabled);
    const node = nodes.find(item => item.offsetParent) || nodes[0];
    if (!node) return false;
    node.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true, pointerId: 1, pointerType: 'mouse' }));
    node.dispatchEvent(new PointerEvent('pointerup', { bubbles: true, pointerId: 1, pointerType: 'mouse' }));
    node.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
    return true;
  }, choice);
  if (!clicked) throw new Error(`Missing ${choice}`);
};
await press('new-campaign');
await page.waitForFunction(() => document.querySelector('[data-choice="class:ranger"]'));
await press('class:ranger');
await press('enter-valley');
await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'kingdom');
const plot = await page.evaluate(() => {
  const state = window.rebornSnapshot();
  return state.plots.find(item => item.id !== 'townhall' && !item.type && item.level === 0)?.id || null;
});
await page.locator(`[aria-label^="${plot}:"]`).evaluate(node => node.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true })));
const choice = `build:${plot}:lumber`;
const build = await page.evaluate(id => {
  const node = document.querySelector(`[data-choice="${id}"]`);
  if (!node) return null;
  const row = { text: node.textContent.trim(), disabled: node.disabled };
  if (!node.disabled) {
    node.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
  }
  return row;
}, choice);
const label = build?.text || '';
const disabled = build ? build.disabled : true;
await page.waitForTimeout(400);
const figure = await page.evaluate(() => {
  const actor = document.querySelector('[data-gait="per-joint"]');
  const slots = [...document.querySelectorAll('[data-worn-slot]')].map(node => ({
    slot: node.getAttribute('data-worn-slot'),
    state: node.getAttribute('data-worn-state'),
  }));
  const joints = [...document.querySelectorAll('[data-joint]')].map(node => node.getAttribute('data-joint'));
  return {
    actor: actor ? actor.getAttribute('data-actor') : null,
    clip: actor ? actor.getAttribute('data-clip') : null,
    gait: actor ? actor.getAttribute('data-gait') : null,
    arm: actor ? actor.getAttribute('data-arm') : null,
    forearm: actor ? actor.getAttribute('data-forearm') : null,
    slots,
    joints,
  };
});
await page.screenshot({ path: fileURLToPath(new URL('./rig-crops/labeled/kingdom-worker.png', import.meta.url)) });
const report = { plot, label, disabled, figure, errors };
await writeFile(new URL('./rig-live.json', import.meta.url), JSON.stringify(report, null, 2));
console.log(JSON.stringify(report, null, 2));
await browser.close();
const needed = ['thigh', 'shin', 'arm', 'forearm', 'foot', 'torso', 'neck'];
if (!figure.gait || figure.slots.length !== 6 || figure.actor !== 'ranger' || needed.some(name => !figure.joints.includes(name)) || errors.length) process.exit(1);
