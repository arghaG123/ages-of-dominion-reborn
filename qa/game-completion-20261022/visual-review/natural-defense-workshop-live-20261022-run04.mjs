import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
import path from 'node:path';

const root = process.cwd();
const out = path.join(root, 'qa/game-completion-20261022/visual-review/natural-defense-workshop-live-20261022-run04');
await fs.mkdir(out, { recursive: true });
const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
const context = await browser.newContext({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1 });
const page = await context.newPage();
page.setDefaultTimeout(20000);
const report = { recordedAt: new Date().toISOString(), classification: 'NATURAL_UI_BUILD_WORKSHOP_ADD_TOWER_CAMPAIGN_SIEGE', url: 'http://127.0.0.1:4173/?audit=1', viewport: '1280x720', errors: [], failedResponses: [] };
page.on('pageerror', error => report.errors.push(String(error)));
page.on('console', message => { if (message.type() === 'error') report.errors.push(message.text()); });
page.on('response', response => { if (response.status() >= 400) report.failedResponses.push({ status: response.status(), url: response.url() }); });
const snapshot = () => page.evaluate(() => window.rebornSnapshot?.() || null);
const shot = name => page.screenshot({ path: path.join(out, `${name}-1280x720.png`) });

await page.goto(report.url, { waitUntil: 'networkidle' });
await page.locator('[data-choice="new-campaign"]').click();
await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'campaignMapSelect');
await page.locator('[data-choice="begin-selected-world"]').click();
await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'hero');
await page.locator('[data-choice="scene-class:knight"]').click();
await page.locator('[data-choice="scene-enter-valley"]').click();
await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'kingdom');
report.beforeWorkshop = await snapshot();
const workshopPlot = await page.evaluate(() => window.rebornSnapshot()?.plots.find(plot => plot.id !== 'townhall' && plot.level === 0)?.id || null);
report.workshopPlot = workshopPlot;
await page.locator(`[data-choice="site:${workshopPlot}"]`).click();
await page.locator(`[data-choice="build-picker:${workshopPlot}"]`).click();
const workshopControl = page.locator(`[data-choice="build:${workshopPlot}:workshop"]:visible`);
report.workshopBuildControl = await workshopControl.getAttribute('aria-label').catch(() => null);
report.workshopBuildDisabled = await workshopControl.isDisabled();
await workshopControl.click();
await page.locator('#build-commit').click();
await page.waitForFunction(plotId => {
  const state = window.rebornSnapshot?.();
  return state?.plots.find(plot => plot.id === plotId)?.type === 'workshop'
    && state.plots.find(plot => plot.id === plotId)?.level === 1
    && !state.buildJobs.some(job => job.plotId === plotId);
}, workshopPlot, { timeout: 60000 });
report.afterWorkshop = await snapshot();
await shot('kingdom-workshop-complete');
const quarryPlot = await page.evaluate(plotId => window.rebornSnapshot()?.plots.find(plot => plot.id !== 'townhall' && plot.id !== plotId && plot.level === 0)?.id || null, workshopPlot);
report.quarryPlot = quarryPlot;
await page.locator('[data-choice="nav:kingdom"]').click();
await page.locator(`[data-choice="site:${quarryPlot}"]`).click();
await page.locator(`[data-choice="build-picker:${quarryPlot}"]`).click();
await page.locator(`[data-choice="build:${quarryPlot}:quarry"]:visible`).click();
await page.locator('#build-commit').click();
await page.waitForFunction(plotId => {
  const state = window.rebornSnapshot?.();
  return state?.plots.find(plot => plot.id === plotId)?.type === 'quarry'
    && state.plots.find(plot => plot.id === plotId)?.level === 1
    && !state.buildJobs.some(job => job.plotId === plotId);
}, quarryPlot, { timeout: 60000 });
report.afterQuarry = await snapshot();
await shot('kingdom-quarry-complete');
await page.locator('#panel-close').click();
report.daysForTowerStone = 0;
for (let day = 0; day < 6 && (await snapshot()).resources.stone < 90; day += 1) {
  const beforeDay = (await snapshot()).day;
  const actionButton = page.locator('#dock [data-choice="kingdom-actions-open"]');
  if (await actionButton.isVisible()) await actionButton.click();
  await page.locator('#choices [data-choice="end-day"]:visible').click();
  await page.waitForFunction(expectedDay => window.rebornSnapshot?.()?.day === expectedDay + 1, beforeDay, { timeout: 10000 });
  report.daysForTowerStone += 1;
}
report.afterNaturalProduction = await snapshot();
await shot('kingdom-after-natural-stone-production');
if (report.afterNaturalProduction.resources.stone < 90) throw new Error(`Quarry did not naturally produce enough stone for Splash tower; current ${report.afterNaturalProduction.resources.stone}`);
await page.locator('[data-choice="nav:war"]').click();
await page.locator('[data-choice="start-siege"]').first().click();
await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'defense');
report.beforeExtraTower = await snapshot();
await page.locator('[data-choice="buy-tower:support"]:visible').click();
await page.waitForFunction(() => window.rebornSnapshot?.()?.towers.some(tower => tower.fam === 'support'));
report.afterExtraTower = await snapshot();
await shot('siege-prepared-with-support');
await page.getByRole('button', { name: 'Start Campaign Siege' }).last().click();
await page.waitForFunction(() => {
  const defense = window.rebornSnapshot?.()?.defense;
  return defense?.status === 'ACTIVE' && defense.paused === true;
});
await page.locator('[data-choice="deploy-hero"]:visible').click();
await page.locator('[data-choice^="deploy-army:"]:visible').first().click();
await page.waitForFunction(() => {
  const defense = window.rebornSnapshot?.()?.defense;
  return defense?.heroDeployed === true && defense?.armyDeployed === true;
});
await page.locator('[data-choice="defense-speed"]').click();
await page.locator('[data-choice="defense-pause"]').click();
await page.waitForFunction(() => window.rebornSnapshot?.()?.defense?.paused === false);
await shot('siege-running-2x');
await page.waitForFunction(() => window.rebornSnapshot?.()?.defense?.pendingSettlement === true, undefined, { timeout: 180000 });
report.result = await snapshot();
await shot('siege-result-pending');
await page.locator('#dock [data-choice="inspect:defense"]').click();
await page.locator('[data-choice="settle-defense"]:visible').click();
await page.waitForFunction(() => window.rebornSnapshot?.()?.defense == null);
report.afterSettlement = await snapshot();
await shot('siege-settlement');
await page.reload({ waitUntil: 'networkidle' });
await page.waitForFunction(() => ['kingdom','defense'].includes(document.querySelector('#app')?.dataset.view));
report.afterReload = await snapshot();
await shot('campaign-after-reload');
report.passed = !report.workshopBuildDisabled
  && report.beforeWorkshop.id === report.afterWorkshop.id
  && report.afterWorkshop.plots.find(plot => plot.id === workshopPlot)?.type === 'workshop'
  && report.afterExtraTower.towers.length === 3
  && report.afterExtraTower.towers.some(tower => tower.fam === 'support')
  && report.result?.defense?.pendingSettlement === true
  && report.result?.defense?.clearedWaves === 5
  && report.result?.defense?.winner === 'p'
  && report.afterSettlement.id === report.afterReload.id
  && report.afterSettlement.defense == null && report.afterReload.defense == null
  && report.errors.length === 0 && report.failedResponses.length === 0;
await fs.writeFile(path.join(out, 'report.json'), JSON.stringify(report, null, 2));
console.log(JSON.stringify({ passed: report.passed, campaignId: report.afterWorkshop?.id, workshopPlot, workshopBuildDisabled: report.workshopBuildDisabled, towersBefore: report.beforeExtraTower?.towers, towersAfter: report.afterExtraTower?.towers, result: report.result?.defense && { status: report.result.defense.status, clearedWaves: report.result.defense.clearedWaves, waves: report.result.defense.waves, winner: report.result.defense.winner, core: report.result.defense.core }, afterSettlement: report.afterSettlement && { defense: report.afterSettlement.defense, army: report.afterSettlement.army.map(stack => ({ id: stack.id, count: stack.count })) }, errors: report.errors, failedResponses: report.failedResponses, output: path.relative(root, out) }, null, 2));
await context.close();
await browser.close();
