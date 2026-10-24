import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import worlds from '../../../src/data/adventure-worlds.json' with { type: 'json' };
import contract from '../../../src/data/implementation-contract.json' with { type: 'json' };
import { adventureGeometryForWorld, adventureMap, routeTo, stepCost } from '../../../src/core/navigation.js';

const root = process.cwd();
const url = 'http://127.0.0.1:4179/?audit=1';
const output = path.join(root, 'qa/game-completion-20261020/visual-review/adventure-site-interactions-label-clearance-live-20261020');
await fs.mkdir(output, { recursive: true });
const report = {
  recordedAt: new Date().toISOString(),
  classification: 'NATURAL_UI_ADVENTURE_SITE_JOURNEY',
  journey: 'new campaign -> select Jade map -> start Adventure -> travel through visible route controls -> claim ruins XP, skill, mill food and mine gold once each -> save and reload',
  url,
  note: 'All campaign, route, site reward, and skill choices are made through rendered UI controls. No campaign, route, or reward state is injected.',
  errors: [],
  failedResponses: [],
  captures: [],
  sites: {},
};
let stage = 'initializing';

const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
const context = await browser.newContext({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1 });
const page = await context.newPage();
page.on('pageerror', error => report.errors.push(String(error)));
page.on('console', message => { if (message.type() === 'error') report.errors.push(message.text()); });
page.on('response', response => { if (response.status() >= 400) report.failedResponses.push({ status: response.status(), url: response.url() }); });

const snapshot = () => page.evaluate(() => window.rebornSnapshot?.() || null);
async function clickChoice(id) {
  const control = page.locator(`[data-choice="${id}"]`).first();
  await control.waitFor({ state: 'visible', timeout: 10000 });
  assert.equal(await control.isDisabled(), false, `${id} is enabled`);
  await control.click();
}
async function waitForRevision(after) {
  await page.waitForFunction(revision => (window.rebornSnapshot?.()?.revision || 0) > revision, after, { timeout: 10000 });
  const revision = (await snapshot()).revision;
  await page.waitForFunction(target => window.rebornCommittedHead?.()?.revision >= target
    && document.querySelector('#save')?.dataset.saveState === 'committed', revision, { timeout: 15000 });
}
async function waitForAdventure(predicate, label) {
  await page.waitForFunction(() => Boolean(window.rebornSnapshot?.()?.adventure), null, { timeout: 15000 });
  for (let attempt = 0; attempt < 50; attempt += 1) {
    const state = await snapshot();
    if (predicate(state.adventure, state)) return state;
    await page.waitForTimeout(100);
  }
  throw new Error(`Timed out waiting for ${label}`);
}
async function capture(name, width, height) {
  await page.setViewportSize({ width, height });
  await page.waitForTimeout(120);
  const file = path.join(output, `${name}-${width}x${height}.png`);
  await page.screenshot({ path: file });
  report.captures.push({ name, size: `${width}x${height}`, file: path.relative(root, file) });
}
async function openAdventurePanel() {
  if (!(await page.locator('#panel').evaluate(panel => panel.classList.contains('open')))) {
    await page.locator('#dock [data-choice="inspect:adventure"]').click();
    await page.waitForFunction(() => document.querySelector('#panel')?.classList.contains('open'));
  }
}
async function closeAdventurePanel() {
  if (await page.locator('#panel').evaluate(panel => panel.classList.contains('open'))) {
    await page.locator('#panel-close').click();
    await page.waitForFunction(() => !document.querySelector('#panel')?.classList.contains('open'));
  }
}
async function finishDay() {
  await openAdventurePanel();
  const before = await snapshot();
  await clickChoice('adventure-end-day');
  await waitForRevision(before.revision);
}
async function moveToward(map, goal, label) {
  for (let segment = 0; segment < 80; segment += 1) {
    const state = await snapshot();
    const adventure = state.adventure;
    if (adventure.x === goal[0] && adventure.y === goal[1]) return;
    if (adventure.pendingEncounter?.status?.startsWith('UNRESOLVED')) throw new Error(`Unexpected guard interrupted travel to ${label}`);
    if (adventure.moves <= 0) { await finishDay(); continue; }
    const start = [adventure.x, adventure.y];
    const directions = [
      ['north', 0, -1], ['east', 1, 0], ['south', 0, 1], ['west', -1, 0],
    ];
    const options = [];
    for (const [direction, dx, dy] of directions) {
      const next = [start[0] + dx, start[1] + dy];
      const key = next.join(',');
      if (map.blocked.has(key) || map.guards.has(key)) continue;
      try {
        const step = stepCost(map, start, next);
        const tail = next[0] === goal[0] && next[1] === goal[1] ? { cost: 0 } : routeTo(map, next, goal);
        options.push({ direction, next, step, score: step + tail.cost });
      } catch {}
    }
    options.sort((first, second) => first.score - second.score || first.direction.localeCompare(second.direction));
    const choice = options[0];
    if (!choice) throw new Error(`No visible cardinal route to ${label} from ${start.join(',')}`);
    const beforeRevision = state.revision;
    await openAdventurePanel();
    await clickChoice(`preview-${choice.direction}`);
    const confirm = page.locator('#choices [data-choice="confirm-route"]');
    await confirm.waitFor({ state: 'visible', timeout: 5000 });
    if (await confirm.isDisabled()) {
      await clickChoice('clear-preview');
      await finishDay();
      continue;
    }
    await confirm.click();
    await waitForRevision(beforeRevision);
    await page.waitForTimeout(520);
  }
  const state = await snapshot();
  throw new Error(`Could not reach ${label}; stopped at ${state.adventure.x},${state.adventure.y}`);
}
async function inspectActionLayout(name, choice) {
  const button = page.locator(`[data-choice="${choice}"]`).first();
  await button.waitFor({ state: 'visible', timeout: 5000 });
  const original = page.viewportSize();
  const measurements = [];
  for (const [width, height] of [[825, 375], [933, 424], [1280, 720]]) {
    await capture(`${name}-action`, width, height);
    const geometry = await page.evaluate(selector => {
      const panel = document.querySelector('#panel').getBoundingClientRect();
      const control = document.querySelector(selector).getBoundingClientRect();
      return {
        size: `${window.innerWidth}x${window.innerHeight}`,
        scrollTop: document.querySelector('#panel').scrollTop,
        panel: { left: panel.left, top: panel.top, right: panel.right, bottom: panel.bottom },
        control: { left: control.left, top: control.top, right: control.right, bottom: control.bottom, width: control.width, height: control.height },
        panelOpen: document.querySelector('#panel').classList.contains('open'),
        visible: getComputedStyle(document.querySelector(selector)).visibility !== 'hidden'
          && getComputedStyle(document.querySelector(selector)).display !== 'none'
          && control.top >= panel.top && control.bottom <= panel.bottom,
      };
    }, `[data-choice="${choice}"]`);
    measurements.push(geometry);
    assert.equal(geometry.panelOpen, true, `${name} panel is open at ${geometry.size}`);
    assert.equal(geometry.visible, true, `${name} action is visibly rendered at ${geometry.size}`);
    assert.ok(geometry.control.width >= 48 && geometry.control.height >= 40, `${name} action has a usable target at ${geometry.size}`);
    assert.ok(geometry.control.left >= 0 && geometry.control.right <= width, `${name} action fits viewport horizontally at ${geometry.size}`);
  }
  await page.setViewportSize(original);
  await page.waitForTimeout(100);
  report.sites[name].actionLayout = measurements;
}

try {
  await page.goto(url, { waitUntil: 'networkidle' });
  stage = 'select new campaign';
  await clickChoice('new-campaign');
  await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'campaignMapSelect');
  await clickChoice('campaign-world:jade-karst');
  await clickChoice('begin-selected-world');
  await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'hero');
  stage = 'create campaign';
  await clickChoice('scene-class:knight');
  await clickChoice('scene-enter-valley');
  await page.waitForTimeout(120);
  await page.locator('#context').click();
  await clickChoice('site-list');
  await clickChoice('choose-site:townhall');
  stage = 'open Adventure';
  await clickChoice('tutorial-toggle');
  await page.locator('[data-choice="nav:adventure"]').first().click();
  await page.locator('#dock [data-choice="inspect:adventure"]').click();
  stage = 'enter Adventure';
  await clickChoice('enter-adventure');
  const start = await waitForAdventure(adventure => adventure.atTown === false, 'Adventure start');
  report.campaignId = start.id;
  report.worldId = start.adventureWorldId;
  report.seed = start.seed;
  const world = worlds.find(row => row.id === start.adventureWorldId);
  const geometry = adventureGeometryForWorld(contract.geometry.adventure, world, start.seed);
  const map = adventureMap(geometry);
  report.layoutId = geometry.layoutId;
  report.layoutIndex = geometry.layoutIndex;

  const ruin = geometry.sites.find(site => site.id === 'ruin');
  await moveToward(map, ruin.approach, 'ruins');
  await openAdventurePanel();
  let state = await waitForAdventure(adventure => adventure.x === ruin.approach[0] && adventure.y === ruin.approach[1], 'ruins entrance');
  report.sites.ruin = {
    coordinates: ruin.approach,
    rewardBefore: state.hero.xp,
    offer: state.adventure.siteOffers.ruinXp,
    claimedBefore: state.adventure.claimedSites.includes('ruin'),
  };
  await capture('ruins-ready', 825, 375);
  await openAdventurePanel();
  await inspectActionLayout('ruin', 'claim-site:ruin');
  const beforeRuin = await snapshot();
  await clickChoice('claim-site:ruin');
  await waitForRevision(beforeRuin.revision);
  state = await snapshot();
  assert.equal(state.adventure.claimedSites.includes('ruin'), true, 'ruins are recorded as claimed');
  assert.ok(state.hero.xp > beforeRuin.hero.xp, 'ruins grant experience through the campaign rule');
  report.sites.ruin.claimed = true;
  report.sites.ruin.rewardAfter = state.hero.xp - beforeRuin.hero.xp;
  await capture('ruins-claimed', 933, 424);

  const shrine = geometry.sites.find(site => site.id === 'shrine');
  await moveToward(map, shrine.approach, 'skill monument');
  await openAdventurePanel();
  state = await waitForAdventure(adventure => adventure.x === shrine.approach[0] && adventure.y === shrine.approach[1], 'skill monument entrance');
  report.sites.shrine = { coordinates: shrine.approach, claimedBefore: state.adventure.claimedSites.includes('shrine') };
  await capture('shrine-ready', 825, 375);
  await openAdventurePanel();
  await inspectActionLayout('shrine', 'study-skill-monument');
  const beforeStudy = await snapshot();
  await clickChoice('study-skill-monument');
  await waitForRevision(beforeStudy.revision);
  state = await snapshot();
  const offer = state.hero.offers.find(row => row.source === 'adventure-shrine' && !row.chosen && !row.declined);
  assert.ok(offer && offer.choices.length === 2, 'the monument offers two saved skill choices');
  report.sites.shrine.offer = { id: offer.id, choices: offer.choices };
  const selectedSkill = offer.choices[0];
  await clickChoice(`shrine-skill:${selectedSkill}`);
  await waitForRevision(state.revision);
  state = await snapshot();
  assert.equal(state.adventure.claimedSites.includes('shrine'), true, 'resolving the lesson consumes the shrine once');
  assert.equal(state.hero.offers.find(row => row.id === offer.id)?.chosen, selectedSkill, 'the selected skill is saved on the offer');
  report.sites.shrine.chosen = selectedSkill;
  await capture('shrine-resolved', 1280, 720);

  for (const [siteId, resource] of [['mill', 'food'], ['mine', 'gold']]) {
    const site = geometry.sites.find(row => row.id === siteId);
    await moveToward(map, site.approach, siteId);
    await openAdventurePanel();
    state = await waitForAdventure(adventure => adventure.x === site.approach[0] && adventure.y === site.approach[1], `${siteId} entrance`);
    const offerKey = siteId === 'mill' ? 'millFood' : 'mineGold';
    report.sites[siteId] = {
      coordinates: site.approach,
      reward: state.adventure.siteOffers[offerKey],
      resourceBefore: state.resources[resource],
      claimedBefore: state.adventure.claimedSites.includes(siteId),
    };
    await capture(`${siteId}-ready`, 825, 375);
    await openAdventurePanel();
    await inspectActionLayout(siteId, `claim-site:${siteId}`);
    const before = await snapshot();
    await clickChoice(`claim-site:${siteId}`);
    await waitForRevision(before.revision);
    state = await snapshot();
    const actual = state.resources[resource] - before.resources[resource];
    assert.equal(actual, before.adventure.siteOffers[offerKey], `${siteId} grants its saved one-time ${resource} offer`);
    assert.equal(state.adventure.claimedSites.includes(siteId), true, `${siteId} is recorded as claimed`);
    assert.equal(await page.locator(`#choices [data-choice="claim-site:${siteId}"]`).count(), 0, `${siteId} cannot be claimed twice through the UI`);
    report.sites[siteId].claimed = true;
    report.sites[siteId].resourceGain = actual;
  }

  await page.reload({ waitUntil: 'networkidle' });
  await page.waitForFunction(() => Boolean(window.rebornSnapshot?.()), null, { timeout: 15000 });
  let reloaded = await snapshot();
  if (await page.locator('#app').getAttribute('data-view') === 'home') {
    await clickChoice('continue');
    await page.waitForFunction(() => document.querySelector('#app')?.dataset.view !== 'home');
  }
  reloaded = await snapshot();
  assert.equal(reloaded.id, report.campaignId, 'same campaign reloads');
  assert.equal(reloaded.adventureWorldId, 'jade-karst', 'selected world persists');
  assert.deepEqual([...reloaded.adventure.claimedSites].sort(), ['mill', 'mine', 'ruin', 'shrine'], 'one-time site claims persist');
  assert.equal(reloaded.hero.offers.find(row => row.source === 'adventure-shrine')?.chosen, selectedSkill, 'chosen monument lesson persists');
  report.reload = { revision: reloaded.revision, worldId: reloaded.adventureWorldId, claimedSites: reloaded.adventure.claimedSites, selectedSkill };
  report.errors = [...new Set(report.errors)];
  assert.deepEqual(report.errors, [], 'no browser errors');
  assert.deepEqual(report.failedResponses, [], 'no failed browser responses');
  report.passed = true;
} catch (error) {
  report.passed = false;
  report.failure = String(error);
  report.stage = stage;
  report.debug = await page.evaluate(() => ({
    view: document.querySelector('#app')?.dataset.view || '',
    context: document.querySelector('#context')?.textContent || '',
    status: document.querySelector('#status')?.textContent || '',
    panel: document.querySelector('#panel')?.innerText || '',
    panelRect: document.querySelector('#panel') ? (() => { const r = document.querySelector('#panel').getBoundingClientRect(); return { top: r.top, bottom: r.bottom, scrollTop: document.querySelector('#panel').scrollTop, scrollHeight: document.querySelector('#panel').scrollHeight, clientHeight: document.querySelector('#panel').clientHeight }; })() : null,
    choices: [...document.querySelectorAll('#choices [data-choice]')].map(node => ({ id: node.dataset.choice, text: node.textContent.trim(), hidden: node.hidden, disabled: node.disabled })),
    snapshot: window.rebornSnapshot?.() || null,
  }));
  report.errors = report.errors.map(error => String(error));
} finally {
  report.recordedAt = new Date().toISOString();
  await fs.writeFile(path.join(output, 'report.json'), JSON.stringify(report, null, 2) + '\n');
  await browser.close();
}

console.log(JSON.stringify(report, null, 2));
if (!report.passed) process.exitCode = 1;
