import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';

const root = process.cwd();
const out = path.join(root, 'qa/game-completion-20261020/visual-review/natural-campaign-build-reload');
await fs.mkdir(out, { recursive: true });
const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
const context = await browser.newContext({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1 });
const page = await context.newPage();
const errors = [];
const notFound = [];
page.on('pageerror', error => errors.push(String(error)));
page.on('console', message => { if (message.type() === 'error') errors.push({ text: message.text(), location: message.location() }); });
page.on('response', response => { if (response.status() === 404) notFound.push(response.url()); });
await page.route('**/favicon.ico', route => route.fulfill({ status: 204, body: '' }));
await page.goto('http://127.0.0.1:4179/', { waitUntil: 'networkidle' });
assert.equal(await page.locator('[data-choice="new-campaign"]').count(), 1, 'fresh profile exposes New Campaign');
await page.locator('[data-choice="new-campaign"]').click();
const classChoices = await page.locator('[data-choice^="scene-class:"]').evaluateAll(nodes => nodes.map(node => node.dataset.choice));
assert.equal(classChoices.length, 8, 'all eight classes are presented');
await page.locator('[data-choice="scene-class:knight"]').click();
await page.locator('[data-choice="scene-enter-valley"]').click();
await page.waitForFunction(() => window.rebornSnapshot()?.age === 0 && document.querySelector('#app')?.dataset.view === 'kingdom');
const campaignId = await page.evaluate(() => window.rebornSnapshot().id);
const firstEmpty = await page.evaluate(() => window.rebornSnapshot().plots.find(plot => plot.id !== 'townhall' && plot.level === 0)?.id);
assert.ok(firstEmpty, 'fresh campaign exposes an empty plot');
await page.locator(`[data-choice="site:${firstEmpty}"]`).click();
await page.locator(`[data-choice="build:${firstEmpty}:lumber"]`).click();
assert.equal(await page.locator('#build-confirm').isHidden(), false, 'construction confirmation is visible');
await page.locator('#build-commit').click();
await page.waitForFunction(id => {
  const state = window.rebornSnapshot();
  return state?.plots.find(plot => plot.id === id)?.type === 'lumber'
    && state.plots.find(plot => plot.id === id)?.level === 1
    && !state.buildJobs.some(job => job.plotId === id);
}, firstEmpty, { timeout: 20000 });
await page.waitForFunction(expectedId => {
  const state = window.rebornSnapshot();
  const head = window.rebornCommittedHead();
  return state?.id === expectedId && head?.campaignId === expectedId && head?.revision >= state.revision;
}, campaignId, { timeout: 10000 });
const beforeReload = await page.evaluate(() => ({
  view: document.querySelector('#app')?.dataset.view,
  state: window.rebornSnapshot(),
  head: window.rebornCommittedHead(),
}));
const initialCapture = path.join(out, 'kingdom-after-lumber-build-before-reload.png');
await page.screenshot({ path: initialCapture });
await page.reload({ waitUntil: 'networkidle' });
await page.waitForFunction(({ id, plotId }) => {
  const state = window.rebornSnapshot();
  const head = window.rebornCommittedHead();
  return state?.id === id
    && state.plots.find(plot => plot.id === plotId)?.type === 'lumber'
    && state.plots.find(plot => plot.id === plotId)?.level === 1
    && head?.campaignId === id
    && head?.revision >= state.revision;
}, { id: campaignId, plotId: firstEmpty }, { timeout: 10000 });
const afterReload = await page.evaluate(() => ({
  view: document.querySelector('#app')?.dataset.view,
  state: window.rebornSnapshot(),
  head: window.rebornCommittedHead(),
}));
const reloadCapture = path.join(out, 'kingdom-after-lumber-build-after-reload.png');
await page.screenshot({ path: reloadCapture });
assert.equal(afterReload.state.id, beforeReload.state.id, 'campaign identity survives reload');
assert.equal(afterReload.state.age, beforeReload.state.age, 'age survives reload');
assert.equal(afterReload.state.plots.find(plot => plot.id === firstEmpty)?.type, 'lumber', 'built structure survives reload');
assert.equal(afterReload.state.plots.find(plot => plot.id === firstEmpty)?.level, 1, 'building level survives reload');
assert.deepEqual(errors, []);
assert.deepEqual(notFound, []);
const report = {
  recordedAt: new Date().toISOString(),
  classification: 'NATURAL_UI_BROWSER_J01_J02_SUBJOURNEY_NOT_FULL_JOURNEY_OR_OWNER_ACCEPTANCE',
  route: 'fresh isolated browser profile -> new campaign -> choose Knight -> enter Kingdom -> build Lumber Camp -> durable acknowledgement -> reload -> verify state',
  campaignId,
  firstEmpty,
  beforeReload: { view: beforeReload.view, revision: beforeReload.state.revision, head: beforeReload.head, building: beforeReload.state.plots.find(plot => plot.id === firstEmpty) },
  afterReload: { view: afterReload.view, revision: afterReload.state.revision, head: afterReload.head, building: afterReload.state.plots.find(plot => plot.id === firstEmpty) },
  captures: [path.relative(root, initialCapture), path.relative(root, reloadCapture)],
  errors,
  notFound,
};
await fs.writeFile(path.join(out, 'report.json'), JSON.stringify(report, null, 2));
console.log(JSON.stringify(report, null, 2));
await context.close();
await browser.close();
