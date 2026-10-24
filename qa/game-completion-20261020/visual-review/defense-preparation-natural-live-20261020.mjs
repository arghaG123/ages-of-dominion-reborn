import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';

const root = process.cwd();
const output = path.join(root, 'qa/game-completion-20261020/visual-review/defense-preparation-live');
await fs.mkdir(output, { recursive: true });
const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
const report = { recordedAt: new Date().toISOString(), classification: 'NATURAL_FRESH_CAMPAIGN_DEFENSE_PREPARATION_CONTROL_AND_VISUAL_CHECK', url: 'http://127.0.0.1:4179/?audit=1', viewports: [], errors: [] };

for (const viewport of [{ name: '825x375', width: 825, height: 375 }, { name: '1280x720', width: 1280, height: 720 }]) {
  const context = await browser.newContext({ viewport: { width: viewport.width, height: viewport.height }, deviceScaleFactor: 1 });
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', error => errors.push(String(error)));
  page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
  await page.goto(report.url, { waitUntil: 'networkidle' });
  await page.locator('[data-choice="new-campaign"]').click();
  await page.locator('[data-choice="scene-class:knight"]').click();
  await page.locator('[data-choice="scene-enter-valley"]').click();
  await page.waitForFunction(() => window.rebornSnapshot()?.hero?.class === 'knight' && window.rebornSnapshot()?.age === 0);
  await page.locator('[data-choice="nav:war"]').click();
  await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'war');
  const warScreenshot = path.join(output, `war-${viewport.name}.png`);
  await page.screenshot({ path: warScreenshot });
  const before = await page.evaluate(() => window.rebornSnapshot());
  await page.locator('#scene-ui [data-choice="start-siege"]').click();
  await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'defense');
  let state = await page.evaluate(() => window.rebornSnapshot());
  assert.equal(state.defense, null, 'opening preparation must not create or start a defense');
  assert.deepEqual(state.resources, before.resources, 'opening preparation must preserve campaign resources');
  assert.equal(await page.locator('#resources').isVisible(), true, 'preparation must show campaign resource balances');
  const initialTowerMarkers = await page.locator('#world [data-tower-instance]').evaluateAll(nodes => nodes.map(node => node.getAttribute('data-tower-instance')));
  assert.deepEqual(initialTowerMarkers, state.towers.map(tower => tower.id), 'owned towers must appear on their session-start pads during preparation');
  const statusLayout = await page.evaluate(() => {
    const status = document.querySelector('#scene-ui').getBoundingClientRect();
    const resources = document.querySelector('#resources').getBoundingClientRect();
    return { status: [status.x, status.y, status.width, status.height], resources: [resources.x, resources.y, resources.width, resources.height], overlap: status.left < resources.right && status.right > resources.left && status.top < resources.bottom && status.bottom > resources.top };
  });
  assert.equal(statusLayout.overlap, false, `defense title must not overlap resource balances at ${viewport.name}`);
  const preparationClosed = path.join(output, `siege-preparation-closed-${viewport.name}.png`);
  await page.screenshot({ path: preparationClosed });
  await page.locator('#dock [data-choice="inspect:defense"]').click();
  await page.waitForFunction(() => document.querySelector('#panel')?.classList.contains('open'));
  assert.equal(await page.locator('#choices [data-choice="buy-tower:splash"]').getAttribute('aria-disabled'), 'true', 'a missing Workshop must keep extra tower purchase unavailable');
  assert.match(await page.locator('#choices [data-choice="buy-tower:splash"]').getAttribute('aria-label'), /Workshop/i, 'the unavailable tower slot must explain its real requirement');
  const preparationOpen = path.join(output, `siege-preparation-actions-${viewport.name}.png`);
  await page.screenshot({ path: preparationOpen });
  await page.locator('#choices [data-choice="defense-mode:endless"]').click();
  assert.equal(await page.locator('#choices [data-choice="start-endless"]').innerText(), 'Start Endless');
  state = await page.evaluate(() => window.rebornSnapshot());
  assert.equal(state.defense, null, 'changing the planned mode must not start an assault');
  await page.locator('#choices [data-choice="defense-mode:siege"]').click();
  await page.locator('[data-choice="nav:kingdom"]').click();
  assert.equal((await page.evaluate(() => window.rebornSnapshot())).defense, null, 'preparation can be left to build in Kingdom');
  await page.locator('[data-choice="nav:war"]').click();
  await page.locator('#scene-ui [data-choice="start-siege"]').click();
  await page.locator('#dock [data-choice="inspect:defense"]').click();
  await page.locator('#choices [data-choice="start-siege"]').click();
  await page.waitForFunction(() => window.rebornSnapshot()?.defense?.status === 'ACTIVE' && window.rebornSnapshot()?.defense?.paused === true);
  const paused = await page.evaluate(() => window.rebornSnapshot());
  assert.equal(paused.defense.practice, 'siege');
  const pausedScreenshot = path.join(output, `siege-started-paused-${viewport.name}.png`);
  await page.screenshot({ path: pausedScreenshot });
  await page.locator('#dock [data-choice="inspect:defense"]').click();
  await page.locator('#choices [data-choice="deploy-hero"]').click();
  const armyButton = page.locator('#choices [data-choice^="deploy-army:"]').first();
  await armyButton.click();
  await page.waitForFunction(() => window.rebornSnapshot()?.defense?.heroDeployed && window.rebornSnapshot()?.defense?.armyDeployed);
  const deployed = await page.evaluate(() => window.rebornSnapshot());
  assert.equal(deployed.defense.paused, true, 'the player can deploy before the wave advances');
  assert.equal(deployed.defense.time, 0, 'preparation and deployment consume no attack time');
  const deployedScreenshot = path.join(output, `siege-deployed-paused-${viewport.name}.png`);
  await page.screenshot({ path: deployedScreenshot });
  report.viewports.push({
    viewport: viewport.name,
    age: deployed.age,
    preparationHasNoSession: true,
    preparationBalancesVisible: true,
    initialTowerMarkers,
    statusLayout,
    workshopRequirementExplained: true,
    modeCanChangeWithoutStarting: true,
    returnToKingdomKeepsPreparationSafe: true,
    started: { status: paused.defense.status, practice: paused.defense.practice, paused: paused.defense.paused },
    deployed: { hero: deployed.defense.heroDeployed, army: deployed.defense.armyDeployed, paused: deployed.defense.paused, time: deployed.defense.time },
    screenshots: [warScreenshot, preparationClosed, preparationOpen, pausedScreenshot, deployedScreenshot].map(file => path.relative(root, file)),
    errors,
  });
  report.errors.push(...errors.map(error => ({ viewport: viewport.name, error })));
  await context.close();
}

await browser.close();
await fs.writeFile(path.join(output, 'report.json'), JSON.stringify(report, null, 2));
assert.deepEqual(report.errors, []);
console.log(JSON.stringify({ classification: report.classification, viewports: report.viewports.map(item => ({ viewport: item.viewport, preparationHasNoSession: item.preparationHasNoSession, started: item.started, deployed: item.deployed, errors: item.errors })), errors: report.errors }, null, 2));
