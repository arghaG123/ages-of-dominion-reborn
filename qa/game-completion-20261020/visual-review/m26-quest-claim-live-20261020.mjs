import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import data from '../../../src/data/reference-data.json' with { type: 'json' };
import worlds from '../../../src/data/adventure-worlds.json' with { type: 'json' };
import { cost, rates } from '../../../src/core/campaign.js';
import { agePrice } from '../../../src/core/rules.js';

const root = process.cwd();
const out = path.join(root, 'qa/game-completion-20261020/visual-review/m26-quest-claim-live-20261020');
await fs.mkdir(out, { recursive: true });
const report = {
  recordedAt: new Date().toISOString(),
  classification: 'NATURAL_UI_QUEST_READY_CLAIM_RELOAD_CONTROLLED_BROWSER_CLOCK',
  journey: 'new campaign -> legal producers -> Town Hall level 2 -> pay Bronze age gate -> claim q2 in Story -> reload and verify claimed state',
  note: 'All campaign actions use visible UI controls. Playwright advances elapsed idle time for resource income and construction only; it does not inject campaign state or resources.',
  viewports: [],
  errors: [],
  failedResponses: [],
};

const browser = await chromium.launch({
  executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe',
  headless: true,
});

async function runAtViewport(size) {
  const context = await browser.newContext({ viewport: { width: size.width, height: size.height }, deviceScaleFactor: 1 });
  const page = await context.newPage();
  await page.clock.install();
  page.on('pageerror', error => report.errors.push({ viewport: size.name, error: String(error) }));
  page.on('console', message => { if (message.type() === 'error') report.errors.push({ viewport: size.name, error: message.text() }); });
  page.on('response', response => { if (response.status() >= 400) report.failedResponses.push({ viewport: size.name, status: response.status(), url: response.url() }); });

  const read = () => page.evaluate(() => window.rebornSnapshot());
  async function clickChoice(id) {
    const button = page.locator(`[data-choice="${id}"]`).first();
    await button.waitFor({ state: 'visible', timeout: 10000 });
    assert.equal(await button.isDisabled(), false, `${id} is enabled`);
    await button.click();
  }
  async function waitForState(predicate, label, timeoutSteps = 100) {
    for (let step = 0; step < timeoutSteps; step += 1) {
      const state = await read();
      if (state && predicate(state)) return state;
      await page.clock.runFor(250);
    }
    throw new Error(`Timed out waiting for ${label}`);
  }
  async function waitForResources(required, label) {
    const ageCapsHours = [8, 7, 6, 5, 4, 3.5, 3, 3];
    for (let step = 0; step < 100; step += 1) {
      const state = await read();
      assert.ok(state, `campaign exists before ${label}`);
      const short = Object.entries(required).filter(([key, value]) => state.resources[key] + 1e-6 < value);
      if (!short.length) return state;
      const income = rates(state);
      const waits = short.map(([key, value]) => {
        assert.ok(income[key] > 0, `a legal producer supplies ${key} for ${label}`);
        return (value - state.resources[key]) / income[key];
      });
      const neededMs = Math.max(1000, Math.ceil(Math.max(...waits) * 1000) + 500);
      await page.clock.fastForward(Math.min(neededMs, Math.floor(ageCapsHours[state.age] * 3600000)));
      await page.waitForTimeout(30);
    }
    throw new Error(`Could not earn resources for ${label}`);
  }
  async function beginBuild(choice, payment, label) {
    await waitForResources(payment, label);
    await clickChoice(choice);
    await page.locator('#build-commit').waitFor({ state: 'visible', timeout: 10000 });
    await page.locator('#build-commit').click();
  }
  async function buildAt(siteId, building) {
    await page.locator('#context').click();
    await clickChoice('site-list');
    await clickChoice(`choose-site:${siteId}`);
    await clickChoice(`build-picker:${siteId}`);
    await beginBuild(`build:${siteId}:${building}`, cost(data, building, 0), `${building} at ${siteId}`);
    await waitForState(state => state.buildJobs.some(job => job.plotId === siteId && job.type === building), `${building} construction start`);
    await page.clock.fastForward(10000);
    await page.waitForTimeout(30);
    return waitForState(state => state.plots.some(plot => plot.id === siteId && plot.type === building && plot.level === 1)
      && !state.buildJobs.some(job => job.plotId === siteId), `${building} completion`);
  }
  async function buildHallToTwo() {
    let state = await read();
    while (state.plots.find(plot => plot.id === 'townhall').level < 2) {
      const level = state.plots.find(plot => plot.id === 'townhall').level;
      await page.locator('#context').click();
      await clickChoice('site-list');
      await clickChoice('choose-site:townhall');
      await beginBuild('build:townhall:townhall', cost(data, 'townhall', level), 'Town Hall level 2');
      await waitForState(value => value.buildJobs.some(job => job.plotId === 'townhall'), 'Town Hall scaffold');
      await page.clock.fastForward(10000);
      await page.waitForTimeout(30);
      state = await waitForState(value => value.plots.find(plot => plot.id === 'townhall').level === 2
        && !value.buildJobs.some(job => job.plotId === 'townhall'), 'Town Hall level 2');
    }
    return state;
  }
  async function openObjectives() {
    await page.locator('#context').click();
    await clickChoice('menu:story');
    await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'story');
    const rival = page.locator('#scene-ui [data-choice^="journal-rival:"]').first();
    if (await rival.count()) await rival.click();
    await page.locator('#scene-ui [data-choice="journal:quests"]').click();
    await page.locator('#scene-ui [data-quest-id="q2"]').waitFor({ state: 'visible' });
  }

  try {
    await page.goto('http://127.0.0.1:4179/?audit=m26-quest-claim', { waitUntil: 'networkidle' });
    await clickChoice('new-campaign');
    await clickChoice(`campaign-world:${worlds[10].id}`);
    await clickChoice('begin-selected-world');
    await clickChoice('scene-class:knight');
    await clickChoice('scene-enter-valley');
    await waitForState(state => state.story.flags.enteredValley === true, 'fresh campaign');
    await page.locator('#context').click();
    await clickChoice('site-list');
    await clickChoice('choose-site:townhall');
    await clickChoice('tutorial-toggle');
    await waitForState(state => state.tutorial.skipped === true, 'optional tutorial skipped');

    for (const [siteId, building] of [['P01', 'farm'], ['P02', 'lumber'], ['P03', 'quarry'], ['P04', 'mine']]) {
      await buildAt(siteId, building);
    }
    await buildHallToTwo();
    const stateBeforeAge = await read();
    await waitForResources(agePrice(0), 'Bronze Age gate');
    const closeInspector = page.locator('#panel-close');
    if (await closeInspector.isVisible().catch(() => false)) await closeInspector.click();
    await clickChoice('kingdom-actions-open');
    await clickChoice('age-advance');
    await page.locator('#build-commit').click();
    const bronzeState = await waitForState(state => state.age === 1, 'Bronze Age');
    assert.equal(bronzeState.age, 1);
    await openObjectives();
    await page.locator('#scene-ui [data-quest-id="q2"]').evaluate(element => element.scrollIntoView({ block: 'center', inline: 'nearest' }));
    await page.waitForTimeout(60);

    const ready = await page.evaluate(() => {
      const state = window.rebornSnapshot();
      const card = document.querySelector('#scene-ui [data-quest-id="q2"]');
      const claim = card?.querySelector('[data-choice="journal-claim:q2"]');
      const rect = card?.getBoundingClientRect();
      const panel = document.querySelector('#scene-ui')?.getBoundingClientRect();
      const claimRect = claim?.getBoundingClientRect();
      return {
        age: state.age,
        resources: { ...state.resources },
        quest: state.quests.q2,
        status: card?.querySelector('p')?.textContent?.trim() || '',
        progress: card?.querySelector('.quest-progress')?.textContent?.trim() || '',
        rewardText: card?.querySelector('.quest-reward')?.innerText?.replace(/\s+/g, ' ').trim() || '',
        claimPresent: Boolean(claim),
        claimDisabled: claim?.disabled ?? null,
        destinationPresent: Boolean(card?.querySelector('[data-choice="quest-destination:q2"]')),
        cardBounds: rect ? { x: rect.x, y: rect.y, width: rect.width, height: rect.height, right: rect.right, bottom: rect.bottom } : null,
        panelBounds: panel ? { x: panel.x, y: panel.y, width: panel.width, height: panel.height, right: panel.right, bottom: panel.bottom } : null,
        claimBounds: claimRect ? { x: claimRect.x, y: claimRect.y, width: claimRect.width, height: claimRect.height, right: claimRect.right, bottom: claimRect.bottom } : null,
        cardFullyInPanel: Boolean(rect && panel && rect.top >= panel.top && rect.bottom <= panel.bottom),
        claimFullyInPanel: Boolean(claimRect && panel && claimRect.top >= panel.top && claimRect.bottom <= panel.bottom),
        visible: Boolean(card && rect && rect.width > 0 && rect.height > 0),
      };
    });
    const readyShot = `q2-ready-${size.name}.png`;
    await page.screenshot({ path: path.join(out, readyShot) });
    assert.equal(ready.age, 1, 'Bronze reached through legal visible controls');
    assert.equal(ready.status, 'Ready to claim');
    assert.equal(ready.progress, '1 / 1 age reached');
    assert.match(ready.rewardText, /200/);
    assert.match(ready.rewardText, /150/);
    assert.equal(ready.claimPresent, true);
    assert.equal(ready.claimDisabled, false);
    assert.equal(ready.destinationPresent, true);
    assert.equal(ready.visible, true);
    assert.equal(ready.cardFullyInPanel, true);
    assert.equal(ready.claimFullyInPanel, true);

    const beforeClaim = await read();
    await page.locator('#scene-ui [data-choice="journal-claim:q2"]').click();
    await page.waitForFunction(() => window.rebornSnapshot().quests.q2.claimed === true);
    const afterClaim = await read();
    const elapsedMs = afterClaim.clock - beforeClaim.clock;
    const income = rates(beforeClaim);
    const rewardDeltas = Object.fromEntries(['gold', 'stone'].map(key => [key,
      afterClaim.resources[key] - beforeClaim.resources[key] - income[key] * elapsedMs / 1000]));
    const claimedUi = await page.evaluate(() => {
      const card = document.querySelector('#scene-ui [data-quest-id="q2"]');
      const button = card?.querySelector('[data-choice="journal-claimed:q2"]');
      const rect = card?.getBoundingClientRect();
      const panel = document.querySelector('#scene-ui')?.getBoundingClientRect();
      return {
        status: card?.querySelector('p')?.textContent?.trim() || '',
        claimPresent: Boolean(card?.querySelector('[data-choice="journal-claim:q2"]')),
        claimedPresent: Boolean(button),
        claimedDisabled: button?.disabled ?? null,
        destinationPresent: Boolean(card?.querySelector('[data-choice="quest-destination:q2"]')),
        cardFullyInPanel: Boolean(rect && panel && rect.top >= panel.top && rect.bottom <= panel.bottom),
        visible: Boolean(rect && rect.width > 0 && rect.height > 0),
      };
    });
    const claimedShot = `q2-claimed-${size.name}.png`;
    await page.screenshot({ path: path.join(out, claimedShot) });
    assert.ok(Math.abs(rewardDeltas.gold - 200) < 1e-6, 'quest pays exactly 200 gold after subtracting clocked income');
    assert.ok(Math.abs(rewardDeltas.stone - 150) < 1e-6, 'quest pays exactly 150 stone after subtracting clocked income');
    assert.equal(claimedUi.status, 'Reward claimed');
    assert.equal(claimedUi.claimPresent, false);
    assert.equal(claimedUi.claimedPresent, true);
    assert.equal(claimedUi.claimedDisabled, true);
    assert.equal(claimedUi.destinationPresent, true);
    assert.equal(claimedUi.visible, true);
    assert.equal(claimedUi.cardFullyInPanel, true);

    await page.reload({ waitUntil: 'networkidle' });
    await openObjectives();
    const afterReload = await read();
    const reloadElapsedMs = afterReload.clock - afterClaim.clock;
    const reloadIncome = rates(afterClaim);
    const repeatReward = Object.fromEntries(['gold', 'stone'].map(key => [key,
      afterReload.resources[key] - afterClaim.resources[key] - reloadIncome[key] * reloadElapsedMs / 1000]));
    const persistedUi = await page.evaluate(() => {
      const card = document.querySelector('#scene-ui [data-quest-id="q2"]');
      return {
        status: card?.querySelector('p')?.textContent?.trim() || '',
        claimPresent: Boolean(card?.querySelector('[data-choice="journal-claim:q2"]')),
        claimedDisabled: card?.querySelector('[data-choice="journal-claimed:q2"]')?.disabled ?? null,
      };
    });
    assert.equal(afterReload.quests.q2.claimed, true);
    assert.ok(Math.abs(repeatReward.gold) < 1e-6, 'reload does not issue gold a second time');
    assert.ok(Math.abs(repeatReward.stone) < 1e-6, 'reload does not issue stone a second time');
    assert.equal(persistedUi.status, 'Reward claimed');
    assert.equal(persistedUi.claimPresent, false);
    assert.equal(persistedUi.claimedDisabled, true);

    report.viewports.push({
      viewport: size.name,
      worldId: worlds[10].id,
      startingAge: stateBeforeAge.age,
      reachedAge: bronzeState.age,
      ready,
      rewardDeltas,
      elapsedForClaimMs: elapsedMs,
      claimedUi,
      reloadPersisted: persistedUi,
      repeatReward,
      reloadElapsedMs,
      screenshots: [readyShot, claimedShot],
    });
  } finally {
    await context.close();
  }
}

try {
  await runAtViewport({ name: '825x375', width: 825, height: 375 });
  await runAtViewport({ name: '1280x720', width: 1280, height: 720 });
} finally {
  await browser.close();
}

report.passed = report.viewports.length === 2
  && report.viewports.every(row => row.reachedAge === 1
    && row.ready.status === 'Ready to claim'
    && row.ready.claimPresent && !row.ready.claimDisabled
    && row.ready.cardFullyInPanel && row.ready.claimFullyInPanel
    && Math.abs(row.rewardDeltas.gold - 200) < 1e-6 && Math.abs(row.rewardDeltas.stone - 150) < 1e-6
    && row.claimedUi.status === 'Reward claimed'
    && !row.claimedUi.claimPresent && row.claimedUi.claimedDisabled
    && row.claimedUi.cardFullyInPanel
    && row.reloadPersisted.status === 'Reward claimed'
    && !row.reloadPersisted.claimPresent
    && Math.abs(row.repeatReward.gold) < 1e-6 && Math.abs(row.repeatReward.stone) < 1e-6)
  && report.errors.length === 0
  && report.failedResponses.length === 0;
await fs.writeFile(path.join(out, 'report.json'), JSON.stringify(report, null, 2));
console.log(JSON.stringify({ passed: report.passed, viewports: report.viewports, errors: report.errors, failedResponses: report.failedResponses, output: path.relative(root, out) }, null, 2));
