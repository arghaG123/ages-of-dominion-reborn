import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
import path from 'node:path';

const root = process.cwd();
const out = path.join(root, 'qa/game-completion-20261022/visual-review/natural-defense-settlement-live-20261022-run01');
await fs.mkdir(out, { recursive: true });
const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
const context = await browser.newContext({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1 });
const page = await context.newPage();
page.setDefaultTimeout(20000);
const report = { recordedAt: new Date().toISOString(), classification: 'NATURAL_UI_CAMPAIGN_SIEGE_FIVE_WAVE_SETTLEMENT_RELOAD', url: 'http://127.0.0.1:4173/?audit=1', viewport: '1280x720', errors: [], failedResponses: [] };
page.on('pageerror', error => report.errors.push(String(error)));
page.on('console', message => { if (message.type() === 'error') report.errors.push(message.text()); });
page.on('response', response => { if (response.status() >= 400) report.failedResponses.push({ status: response.status(), url: response.url() }); });
const getState = () => page.evaluate(() => JSON.parse(document.querySelector('#audit-snapshot')?.textContent || 'null')?.state || null);
const shot = name => page.screenshot({ path: path.join(out, `${name}-1280x720.png`) });

await page.goto(report.url, { waitUntil: 'networkidle' });
await page.locator('[data-choice="new-campaign"]').click();
await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'campaignMapSelect');
await page.locator('[data-choice="begin-selected-world"]').click();
await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'hero');
await page.locator('[data-choice="scene-class:knight"]').click();
await page.locator('[data-choice="scene-enter-valley"]').click();
await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'kingdom');
report.campaignId = (await getState())?.id;
await page.locator('[data-choice="nav:war"]').click();
await page.locator('[data-choice="start-siege"]').first().click();
await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'defense');
await page.getByRole('button', { name: 'Start Campaign Siege' }).last().click();
await page.waitForFunction(() => {
  const defense = JSON.parse(document.querySelector('#audit-snapshot')?.textContent || 'null')?.state?.defense;
  return defense?.status === 'ACTIVE' && defense.paused === true;
});
await page.locator('[data-choice="deploy-hero"]:visible').click();
await page.locator('[data-choice^="deploy-army:"]:visible').first().click();
await page.waitForFunction(() => {
  const defense = JSON.parse(document.querySelector('#audit-snapshot')?.textContent || 'null')?.state?.defense;
  return defense?.heroDeployed === true && defense?.armyDeployed === true;
});
await page.locator('[data-choice="defense-speed"]').click();
await page.waitForFunction(() => JSON.parse(document.querySelector('#audit-snapshot')?.textContent || 'null')?.state?.defense?.speed === 2);
report.preRun = await page.evaluate(() => {
  const state = JSON.parse(document.querySelector('#audit-snapshot')?.textContent || 'null')?.state;
  return { campaignId: state?.id, age: state?.age, day: state?.day, resources: state?.resources, army: state?.army.map(stack => ({ id: stack.id, count: stack.count })), defense: state?.defense && { status: state.defense.status, speed: state.defense.speed, heroDeployed: state.defense.heroDeployed, armyDeployed: state.defense.armyDeployed } };
});
await shot('siege-deployed-speed-2x-paused');
await page.locator('[data-choice="defense-pause"]').click();
await page.waitForFunction(() => JSON.parse(document.querySelector('#audit-snapshot')?.textContent || 'null')?.state?.defense?.paused === false);
await shot('siege-running-speed-2x');
await page.waitForFunction(() => {
  const defense = JSON.parse(document.querySelector('#audit-snapshot')?.textContent || 'null')?.state?.defense;
  return defense?.pendingSettlement === true;
}, undefined, { timeout: 180000 });
report.resultBeforeSettlement = await page.evaluate(() => {
  const state = JSON.parse(document.querySelector('#audit-snapshot')?.textContent || 'null')?.state;
  return { campaignId: state?.id, age: state?.age, day: state?.day, resources: state?.resources, army: state?.army.map(stack => ({ id: stack.id, count: stack.count })), defense: state?.defense && { status: state.defense.status, practice: state.defense.practice, clearedWaves: state.defense.clearedWaves, waves: state.defense.waves, pendingSettlement: state.defense.pendingSettlement, winner: state.defense.winner, core: state.defense.core } };
});
await shot('siege-result-pending');
await page.locator('#dock [data-choice="inspect:defense"]').click();
await page.locator('[data-choice="settle-defense"]:visible').click();
await page.waitForFunction(() => JSON.parse(document.querySelector('#audit-snapshot')?.textContent || 'null')?.state?.defense == null);
report.afterSettlement = await page.evaluate(() => {
  const state = JSON.parse(document.querySelector('#audit-snapshot')?.textContent || 'null')?.state;
  return { campaignId: state?.id, age: state?.age, day: state?.day, resources: state?.resources, army: state?.army.map(stack => ({ id: stack.id, count: stack.count })), defense: state?.defense || null };
});
await shot('siege-settled');
await page.reload({ waitUntil: 'networkidle' });
await page.waitForFunction(() => ['kingdom','defense'].includes(document.querySelector('#app')?.dataset.view));
report.reloadState = await page.evaluate(() => {
  const state = JSON.parse(document.querySelector('#audit-snapshot')?.textContent || 'null')?.state;
  return { campaignId: state?.id, age: state?.age, day: state?.day, resources: state?.resources, army: state?.army.map(stack => ({ id: stack.id, count: stack.count })), defense: state?.defense || null };
});
await shot('siege-reload-after-settlement');
report.passed = report.campaignId === report.preRun.campaignId
  && report.resultBeforeSettlement?.campaignId === report.campaignId
  && report.resultBeforeSettlement?.defense?.pendingSettlement === true
  && report.resultBeforeSettlement?.defense?.clearedWaves === 5
  && report.resultBeforeSettlement?.defense?.winner === 'p'
  && report.afterSettlement?.campaignId === report.campaignId && report.afterSettlement.defense === null
  && report.reloadState?.campaignId === report.campaignId && report.reloadState.defense === null
  && JSON.stringify(report.afterSettlement.resources) === JSON.stringify(report.reloadState.resources)
  && JSON.stringify(report.afterSettlement.army) === JSON.stringify(report.reloadState.army)
  && report.errors.length === 0 && report.failedResponses.length === 0;
await fs.writeFile(path.join(out, 'report.json'), JSON.stringify(report, null, 2));
console.log(JSON.stringify({ passed: report.passed, campaignId: report.campaignId, preRun: report.preRun, resultBeforeSettlement: report.resultBeforeSettlement, afterSettlement: report.afterSettlement, reloadState: report.reloadState, errors: report.errors, failedResponses: report.failedResponses, output: path.relative(root, out) }, null, 2));
await context.close();
await browser.close();
