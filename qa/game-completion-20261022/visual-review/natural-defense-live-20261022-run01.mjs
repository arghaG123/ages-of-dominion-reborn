import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
import path from 'node:path';

const root = process.cwd();
const out = path.join(root, 'qa/game-completion-20261022/visual-review/natural-defense-live-20261022-run01');
await fs.mkdir(out, { recursive: true });
const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
const context = await browser.newContext({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1 });
const page = await context.newPage();
page.setDefaultTimeout(15000);
const report = { recordedAt: new Date().toISOString(), classification: 'NATURAL_UI_CAMPAIGN_SIEGE_DEPLOYMENT_ONE_WAVE_PAUSE_RELOAD', url: 'http://127.0.0.1:4173/?audit=1', viewport: '1280x720', errors: [], failedResponses: [] };
page.on('pageerror', error => report.errors.push(String(error)));
page.on('console', message => { if (message.type() === 'error') report.errors.push(message.text()); });
page.on('response', response => { if (response.status() >= 400) report.failedResponses.push({ status: response.status(), url: response.url() }); });
const state = () => page.evaluate(() => JSON.parse(document.querySelector('#audit-snapshot')?.textContent || 'null')?.state || null);
const visibleChoices = () => page.evaluate(() => [...document.querySelectorAll('#dock [data-choice], #choices [data-choice], #scene-ui [data-choice]')]
  .filter(node => { const b = node.getBoundingClientRect(); return b.width > 0 && b.height > 0 && getComputedStyle(node).visibility !== 'hidden'; })
  .map(node => ({ id: node.dataset.choice, label: node.getAttribute('aria-label') || node.textContent.trim(), disabled: node.disabled })));
const shot = name => page.screenshot({ path: path.join(out, `${name}-1280x720.png`) });

await page.goto(report.url, { waitUntil: 'networkidle' });
await page.locator('[data-choice="new-campaign"]').click();
await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'campaignMapSelect');
await page.locator('[data-choice="begin-selected-world"]').click();
await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'hero');
await page.locator('[data-choice="scene-class:knight"]').click();
await page.locator('[data-choice="scene-enter-valley"]').click();
await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'kingdom');
report.campaignId = (await state())?.id;
await page.locator('[data-choice="nav:war"]').click();
await shot('war-options');
await page.locator('[data-choice="start-siege"]').first().click();
await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'defense');
await shot('siege-preparation');
await page.getByRole('button', { name: 'Start Campaign Siege' }).last().click();
await page.waitForFunction(() => {
  const defense = JSON.parse(document.querySelector('#audit-snapshot')?.textContent || 'null')?.state?.defense;
  return defense?.status === 'ACTIVE' && defense.paused === true;
});
report.deploymentControls = await visibleChoices();
await shot('siege-start-paused');
await page.locator('[data-choice="deploy-hero"]:visible').click();
await page.waitForFunction(() => JSON.parse(document.querySelector('#audit-snapshot')?.textContent || 'null')?.state?.defense?.heroDeployed === true);
await page.locator('[data-choice^="deploy-army:"]:visible').first().click();
await page.waitForFunction(() => JSON.parse(document.querySelector('#audit-snapshot')?.textContent || 'null')?.state?.defense?.armyDeployed === true);
report.deployedState = await page.evaluate(() => {
  const saved = JSON.parse(document.querySelector('#audit-snapshot')?.textContent || 'null')?.state;
  return { heroDeployed: saved?.defense?.heroDeployed, armyDeployed: saved?.defense?.armyDeployed, defense: saved?.defense?.status, campaignId: saved?.id };
});
await shot('siege-deployed-paused');
await page.locator('[data-choice="defense-pause"]').click();
await page.waitForFunction(() => JSON.parse(document.querySelector('#audit-snapshot')?.textContent || 'null')?.state?.defense?.paused === false);
await shot('siege-running');
await page.waitForFunction(() => {
  const defense = JSON.parse(document.querySelector('#audit-snapshot')?.textContent || 'null')?.state?.defense;
  return defense?.clearedWaves >= 1 || defense?.pendingSettlement === true;
}, undefined, { timeout: 90000 });
report.waveState = await page.evaluate(() => {
  const saved = JSON.parse(document.querySelector('#audit-snapshot')?.textContent || 'null')?.state;
  return {
    campaignId: saved?.id,
    defense: saved?.defense?.status,
    paused: saved?.defense?.paused,
    clearedWaves: saved?.defense?.clearedWaves,
    pendingSettlement: saved?.defense?.pendingSettlement,
    winner: saved?.defense?.winner,
    core: saved?.defense?.core,
    heroDeployed: saved?.defense?.heroDeployed,
    armyDeployed: saved?.defense?.armyDeployed,
    resources: saved?.resources,
    army: saved?.army.map(stack => ({ id: stack.id, count: stack.count })),
  };
});
if (report.waveState.paused !== true && report.waveState.pendingSettlement !== true) {
  await page.locator('[data-choice="defense-pause"]').click();
  await page.waitForFunction(() => JSON.parse(document.querySelector('#audit-snapshot')?.textContent || 'null')?.state?.defense?.paused === true);
}
await shot('siege-wave-paused');
await page.reload({ waitUntil: 'networkidle' });
await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'defense');
report.reloadState = await page.evaluate(() => {
  const saved = JSON.parse(document.querySelector('#audit-snapshot')?.textContent || 'null')?.state;
  return {
    campaignId: saved?.id,
    defense: saved?.defense?.status,
    paused: saved?.defense?.paused,
    clearedWaves: saved?.defense?.clearedWaves,
    pendingSettlement: saved?.defense?.pendingSettlement,
    winner: saved?.defense?.winner,
    core: saved?.defense?.core,
    heroDeployed: saved?.defense?.heroDeployed,
    armyDeployed: saved?.defense?.armyDeployed,
    resources: saved?.resources,
    army: saved?.army.map(stack => ({ id: stack.id, count: stack.count })),
  };
});
await shot('siege-reloaded-paused');
report.passed = report.campaignId === report.deployedState.campaignId
  && report.waveState?.campaignId === report.campaignId
  && report.reloadState?.campaignId === report.campaignId
  && report.deployedState.heroDeployed === true && report.deployedState.armyDeployed === true
  && report.reloadState.defense === 'ACTIVE' && report.reloadState.paused === true
  && report.reloadState.clearedWaves >= 1
  && JSON.stringify(report.reloadState.resources) === JSON.stringify(report.waveState.resources)
  && JSON.stringify(report.reloadState.army) === JSON.stringify(report.waveState.army)
  && report.errors.length === 0 && report.failedResponses.length === 0;
await fs.writeFile(path.join(out, 'report.json'), JSON.stringify(report, null, 2));
console.log(JSON.stringify({ passed: report.passed, campaignId: report.campaignId, deploymentControls: report.deploymentControls, deployedState: report.deployedState, waveState: report.waveState, reloadState: report.reloadState, errors: report.errors, failedResponses: report.failedResponses, output: path.relative(root, out) }, null, 2));
await context.close();
await browser.close();
