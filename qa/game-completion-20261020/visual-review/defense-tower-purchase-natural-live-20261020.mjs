import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';

const root = process.cwd();
const output = path.join(root, 'qa/game-completion-20261020/visual-review/defense-preparation-live');
await fs.mkdir(output, { recursive: true });
const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
const context = await browser.newContext({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1 });
const page = await context.newPage();
const errors = [];
page.on('pageerror', error => errors.push(String(error)));
page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
await page.goto('http://127.0.0.1:4179/?audit=1', { waitUntil: 'networkidle' });
await page.locator('[data-choice="new-campaign"]').click();
await page.locator('[data-choice="scene-class:knight"]').click();
await page.locator('[data-choice="scene-enter-valley"]').click();
await page.waitForFunction(() => window.rebornSnapshot()?.hero?.class === 'knight' && window.rebornSnapshot()?.age === 0);

async function build(plotId, building) {
  if (await page.locator('#panel.open').count()) await page.locator('#panel-close').click();
  await page.locator(`[data-choice="site:${plotId}"]`).click();
  const buildChoice = page.locator(`#choices [data-choice="build:${plotId}:${building}"]`);
  await buildChoice.waitFor({ state: 'visible' });
  await buildChoice.click();
  await page.locator('#build-commit').click();
  await page.waitForFunction(({ plotId: id, building: type }) => {
    const state = window.rebornSnapshot();
    return state?.plots?.find(plot => plot.id === id)?.type === type && !state.buildJobs.some(job => job.plotId === id);
  }, { plotId, building }, { timeout: 15000 });
}

await build('P01', 'workshop');
await build('P02', 'quarry');
await page.waitForFunction(() => window.rebornSnapshot()?.resources?.stone >= 50, { timeout: 20000 });
const before = await page.evaluate(() => window.rebornSnapshot());
assert.equal(before.plots.find(plot => plot.id === 'P01').type, 'workshop');
assert.equal(before.plots.find(plot => plot.id === 'P01').level, 1);
assert.equal(before.plots.find(plot => plot.id === 'P02').type, 'quarry');
assert.equal(before.plots.find(plot => plot.id === 'P02').level, 1);
await page.locator('[data-choice="nav:war"]').click();
await page.locator('#scene-ui [data-choice="start-siege"]').click();
await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'defense');
await page.locator('#dock [data-choice="inspect:defense"]').click();
const supportPurchase = page.locator('#choices [data-choice="buy-tower:support"]');
assert.equal(await supportPurchase.getAttribute('aria-disabled'), null, 'the natural Workshop plus affordable resources should enable Support tower purchase');
const purchaseCost = await supportPurchase.getAttribute('aria-label');
const beforePurchase = await page.evaluate(() => window.rebornSnapshot());
await page.screenshot({ path: path.join(output, 'siege-ready-to-buy-support-1280x720.png') });
await supportPurchase.click();
const purchased = await page.evaluate(() => window.rebornSnapshot());
assert.equal(purchased.defense, null, 'buying a tower in preparation must not start the attack');
assert.equal(purchased.towers.length, before.towers.length + 1);
assert.equal(purchased.towers.at(-1).fam, 'support');
assert.equal(purchased.resources.wood, beforePurchase.resources.wood - 80);
const elapsedSeconds = (purchased.clock - beforePurchase.clock) / 1000;
assert.ok(Math.abs(purchased.resources.stone - (beforePurchase.resources.stone + 0.35 * elapsedSeconds - 50)) < 1e-6, 'quarry income is credited before the exact tower cost');
assert.equal(purchased.resources.gold, beforePurchase.resources.gold - 60);
const previewTowers = await page.locator('#world [data-tower-instance]').evaluateAll(nodes => nodes.map(node => ({ id: node.getAttribute('data-tower-instance'), family: node.getAttribute('data-tower-family') })));
assert.deepEqual(previewTowers.map(tower => tower.id), purchased.towers.map(tower => tower.id), 'every owned tower is visible in the preparation field');
await page.screenshot({ path: path.join(output, 'siege-support-purchased-preparation-1280x720.png') });
await page.locator('#choices [data-choice="start-siege"]').click();
await page.waitForFunction(() => window.rebornSnapshot()?.defense?.status === 'ACTIVE' && window.rebornSnapshot()?.defense?.paused === true);
const active = await page.evaluate(() => window.rebornSnapshot());
assert.equal(active.defense.towers.length, purchased.towers.length);
assert.deepEqual(active.defense.towers.map(tower => tower.siteId), ['D1', 'D2', 'D3']);
assert.equal(active.defense.towers[2].fam, 'support');
assert.deepEqual(errors, []);

const result = {
  recordedAt: new Date().toISOString(),
  classification: 'NATURAL_WORKSHOP_QUARRY_TOWER_PURCHASE_AND_SESSION_PAD_CONTINUITY',
  viewport: '1280x720',
  builtInKingdom: ['P01:workshop:level1', 'P02:quarry:level1'],
  purchasedFamily: 'support',
  purchaseAccessibleLabel: purchaseCost,
  elapsedSecondsDuringPurchase: elapsedSeconds,
  exactCost: { wood: 80, stone: 50, gold: 60 },
  towerCountBeforePurchase: before.towers.length,
  towerCountAfterPurchase: purchased.towers.length,
  visiblePreparationTowers: previewTowers,
  sessionSiteIds: active.defense.towers.map(tower => tower.siteId),
  sessionFamilies: active.defense.towers.map(tower => tower.fam),
  sessionPausedBeforeDeployment: active.defense.paused,
  errors,
  screenshots: ['siege-ready-to-buy-support-1280x720.png', 'siege-support-purchased-preparation-1280x720.png'].map(file => path.join(output, file)),
};
await fs.writeFile(path.join(output, 'natural-tower-purchase-report.json'), JSON.stringify(result, null, 2));
await context.close();
await browser.close();
console.log(JSON.stringify(result, null, 2));
