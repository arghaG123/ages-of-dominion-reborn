import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import data from '../../../src/data/reference-data.json' with { type: 'json' };
import contract from '../../../src/data/implementation-contract.json' with { type: 'json' };
import worlds from '../../../src/data/adventure-worlds.json' with { type: 'json' };
import { adventureGeometryForWorld, adventureMap, routeTo } from '../../../src/core/navigation.js';
import { dwellingCost, dwellingPool } from '../../../src/core/mechanics.js';
import { rates } from '../../../src/core/campaign.js';

const root = process.cwd();
const out = path.join(root, 'qa/game-completion-20261020/visual-review/adventure-site-foot-live');
await fs.mkdir(out, { recursive: true });
const viewportSizes = ['825x375', '933x424', '1280x720'];
const selectedWorld = worlds.find(world => world.id === 'jade-karst');
assert.ok(selectedWorld, 'the natural journey uses its registered Jade Karst campaign world');
let dwellingSite;
let expectedRoute;
let liveMap;

const report = {
  recordedAt: new Date().toISOString(),
  classification: 'NATURAL_UI_ADVENTURE_DWELLING_CLAIM_RELOAD_NOT_FULL_JOURNEY_OR_OWNER_ACCEPTANCE',
  journey: 'fresh campaign -> build Barracks -> leave town -> preview/cancel route -> confirm legal road route to dwelling -> on-foot site arrival -> ask for fixed offer -> back to road and reopen the same offer -> save/reload -> claim creatures -> verify Q3 ready -> claim its reward once -> save/reload -> verify roster and both rewards',
  url: 'http://127.0.0.1:4179/?audit=1',
  route: null,
  viewportSizes,
  errors: [],
  notFound: [],
  captures: [],
};

const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
const context = await browser.newContext({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1 });
const page = await context.newPage();
page.on('pageerror', error => report.errors.push(String(error)));
page.on('console', message => { if (message.type() === 'error') report.errors.push(message.text()); });
page.on('response', response => { if (response.status() === 404) report.notFound.push(response.url()); });
const snapshot = () => page.evaluate(() => ({ state: window.rebornSnapshot(), head: window.rebornCommittedHead(), view: document.querySelector('#app')?.dataset.view }));
async function clickChoice(selector) {
  const control = page.locator(selector).first();
  await control.waitFor({ state: 'visible', timeout: 10000 });
  assert.equal(await control.isDisabled(), false, `${selector} is enabled`);
  await control.click();
}
async function openObjectives() {
  if (await page.evaluate(() => document.querySelector('#app')?.dataset.view) === 'home'
    && await page.locator('[data-choice="continue"]:visible').count()) await clickChoice('[data-choice="continue"]');
  if (await page.evaluate(() => document.querySelector('#app')?.dataset.view) !== 'story') {
    await clickChoice('#context');
    await clickChoice('[data-choice="menu:story"]');
    await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'story');
  }
  const rival = page.locator('#scene-ui [data-choice^="journal-rival:"]').first();
  if (await rival.count()) await rival.click();
  await clickChoice('#scene-ui [data-choice="journal:quests"]');
  await page.locator('#scene-ui [data-quest-id="q3"]').waitFor({ state: 'visible', timeout: 10000 });
}
async function waitForState(predicate, label, timeout = 10000) {
  const deadline = Date.now() + timeout;
  while (Date.now() < deadline) {
    const value = await snapshot();
    if (value.state && predicate(value.state)) return value;
    await page.waitForTimeout(100);
  }
  throw new Error(`Timed out waiting for ${label}`);
}
async function capture(name, size) {
  const [width, height] = size.split('x').map(Number);
  await page.setViewportSize({ width, height });
  await page.waitForTimeout(120);
  const file = path.join(out, `${name}-${size}.png`);
  await page.screenshot({ path: file });
  report.captures.push({ name, size, file: path.relative(root, file) });
  if (await page.locator('#panel.open').count()) {
    const layout = await page.evaluate(() => {
      const bounds = selector => {
        const node = document.querySelector(selector);
        const rect = node?.getBoundingClientRect();
        return rect ? { left: rect.left, right: rect.right, top: rect.top, bottom: rect.bottom } : null;
      };
      const actor = document.querySelector('#world [data-actor="knight"][data-adventure-travel-mode="on-foot"]');
      const matrix = actor?.getScreenCTM();
      const actorAnchor = matrix ? new DOMPoint(0, 0).matrixTransform(matrix) : null;
      return {
        panel: bounds('#panel'),
        hero: bounds('#world [data-actor="knight"][data-adventure-travel-mode="on-foot"]'),
        heroAnchor: actorAnchor ? { x: actorAnchor.x, y: actorAnchor.y } : null,
        site: bounds('#world [data-site-id="dwelling"]'),
        viewport: { width: window.innerWidth, height: window.innerHeight },
      };
    });
    assert.ok(layout.panel && layout.hero && layout.heroAnchor && layout.site, 'the on-foot hero, dwelling art, and inspector have measurable screen bounds');
    (report.panelComposition ||= []).push({ size, ...layout });
    assert.ok(layout.heroAnchor.x >= 0 && layout.heroAnchor.x < layout.panel.left && layout.heroAnchor.y >= 0 && layout.heroAnchor.y <= layout.viewport.height, 'the on-foot hero anchor stays visible outside the inspector');
    assert.ok(layout.site.left >= 0 && layout.site.right <= layout.panel.left, 'the dwelling art stays fully visible beside the inspector');
  }
}

try {
  await page.goto(report.url, { waitUntil: 'networkidle' });
  await clickChoice('[data-choice="new-campaign"]');
  await clickChoice('[data-choice="campaign-world:jade-karst"]');
  await clickChoice('[data-choice="begin-selected-world"]');
  await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'hero');
  await clickChoice('[data-choice="scene-class:knight"]');
  await clickChoice('[data-choice="scene-enter-valley"]');
  await page.waitForFunction(() => window.rebornSnapshot()?.age === 0 && document.querySelector('#app')?.dataset.view === 'kingdom');
  report.campaignId = (await snapshot()).state.id;

  const emptyPlot = (await snapshot()).state.plots.find(plot => plot.id !== 'townhall' && plot.level === 0);
  assert.ok(emptyPlot, 'the fresh Kingdom has an empty site for Barracks');
  await clickChoice(`[data-choice="site:${emptyPlot.id}"]`);
  await clickChoice(`[data-choice="build-picker:${emptyPlot.id}"]`);
  await clickChoice(`[data-choice="build:${emptyPlot.id}:barracks"]`);
  await page.locator('#build-commit').click();
  const barracksBuilt = await waitForState(value => {
    const plot = value.plots.find(row => row.id === emptyPlot.id);
    return plot?.type === 'barracks' && plot.level === 1 && !value.buildJobs.some(job => job.plotId === emptyPlot.id);
  }, 'finish Barracks construction', 20000);
  await page.waitForFunction(id => {
    const state = window.rebornSnapshot();
    const head = window.rebornCommittedHead();
    return state?.id === id && head?.campaignId === id && head.revision >= state.revision;
  }, report.campaignId, { timeout: 10000 });
  report.building = { plotId: emptyPlot.id, type: 'barracks', level: 1, resourcesAfterBuild: { ...barracksBuilt.state.resources } };

  await clickChoice('[data-choice="nav:adventure"]');
  await clickChoice('[data-choice="enter-adventure"]');
  const start = await waitForState(value => value.adventure?.atTown === false, 'enter Adventure');
  report.start = start.state.adventure;
  report.resourcesBefore = { ...start.state.resources };
  const liveGeometry = adventureGeometryForWorld(contract.geometry.adventure, selectedWorld, start.state.seed);
  liveMap = adventureMap(liveGeometry);
  dwellingSite = liveGeometry.sites.find(site => site.id === 'dwelling');
  assert.ok(dwellingSite, 'the selected world has its registered dwelling approach');
  expectedRoute = routeTo(liveMap, [start.state.adventure.x, start.state.adventure.y], dwellingSite.approach);
  assert.ok(expectedRoute.cost <= start.state.adventure.moves, 'the natural starting movement allowance reaches the dwelling approach');
  assert.equal(expectedRoute.cells.some(cell => liveMap.guards.has(cell.join(','))), false, 'the on-foot visual journey does not require a battle shortcut');
  report.route = { worldId: selectedWorld.id, layoutId: liveGeometry.layoutId, start: [start.state.adventure.x, start.state.adventure.y], destination: dwellingSite.approach, cost: expectedRoute.cost, cells: expectedRoute.cells };

  const beforeCancel = await page.evaluate(() => window.rebornSnapshot().adventure);
  const target = page.locator(`#world [data-adventure-cell="${dwellingSite.approach.join(',')}"]`);
  assert.equal(await target.count(), 1, 'the legal approach cell is present in the live world');
  await target.click();
  await page.waitForFunction(() => Boolean(document.querySelector('[data-choice="confirm-route"]')));
  const preview = await page.evaluate(() => ({
    destinationCount: document.querySelectorAll('#world [data-route-destination]').length,
    title: document.querySelector('[data-choice="confirm-route"]')?.title || '',
  }));
  assert.equal(preview.destinationCount, 1, 'the map shows one selected route destination');
  assert.match(preview.title, new RegExp(`cost ${expectedRoute.cost}`), 'route preview exposes its true movement cost');
  await clickChoice('[data-choice="cancel-route"]');
  assert.deepEqual(await page.evaluate(() => window.rebornSnapshot().adventure), beforeCancel, 'canceling the route does not spend movement or change position');
  assert.equal(await page.locator('#world [data-route-destination]').count(), 0, 'cancel clears its destination marker');
  report.cancel = { preservedPosition: [beforeCancel.x, beforeCancel.y], preservedMoves: beforeCancel.moves };

  await page.locator(`#world [data-adventure-cell="${dwellingSite.approach.join(',')}"]`).click();
  await clickChoice('[data-choice="confirm-route"]');
  const arrived = await waitForState(value => value.adventure?.x === dwellingSite.approach[0] && value.adventure?.y === dwellingSite.approach[1], 'arrive at the dwelling approach');
  assert.equal(arrived.state.adventure.moves, start.state.adventure.moves - expectedRoute.cost, 'arrival spends exactly the committed route cost');
  assert.equal(arrived.state.adventure.pendingEncounter, null, 'the route reaches the site without an encounter');
  assert.ok(arrived.state.adventure.visited.includes(dwellingSite.approach.join(',')), 'the site approach is discovered through natural travel');
  await page.waitForFunction(() => document.querySelector('#world')?.dataset.adventureTravelerMode === 'on-foot', null, { timeout: 5000 });
  assert.equal(await page.locator('#world[data-adventure-site-approach="dwelling"]').count(), 1, 'the approach presents the correct site-specific visual mode');
  assert.equal(await page.locator('#world [data-actor="knight"][data-adventure-travel-mode="on-foot"]').count(), 1, 'the live class rig is shown on foot at the site');
  assert.equal(await page.locator('#world [data-mount]').count(), 0, 'the mount is removed from the interaction point');
  assert.equal(await page.locator('#world [data-site-id="dwelling"]').count(), 1, 'the discovered dwelling art is present');
  report.arrival = { adventure: arrived.state.adventure, travelerMode: 'on-foot', siteVisible: 'dwelling', mountVisible: false };

  await capture('dwelling-on-foot', '825x375');
  await capture('dwelling-on-foot', '933x424');
  await capture('dwelling-on-foot', '1280x720');

  await clickChoice('[data-choice="inspect:adventure"]');
  await page.waitForFunction(() => document.querySelector('#panel')?.classList.contains('open'));
  await capture('dwelling-context-panel', '825x375');
  await capture('dwelling-context-panel', '1280x720');
  const offerControl = page.locator('[data-choice^="offer-dwelling:"]:visible').first();
  await offerControl.waitFor({ state: 'visible', timeout: 5000 });
  const offerChoice = await offerControl.getAttribute('data-choice');
  await offerControl.click();
  await page.waitForFunction(() => Boolean(window.rebornSnapshot()?.dwelling));
  const offered = (await snapshot()).state;
  assert.ok(offered.dwelling.type, 'the visible offer has a fixed creature type');
  assert.equal(JSON.stringify(offered.resources), JSON.stringify(report.resourcesBefore), 'asking for an offer does not pay or grant resources');
  assert.ok(await page.locator('[data-choice="claim-dwelling"]:visible').count(), 'the offer presents its contextual claim action');
  const payment = dwellingCost(data, offered.dwelling.type, offered.dwelling.multiplier);
  const claimButton = page.locator('[data-choice="claim-dwelling"]:visible').first();
  assert.equal(await claimButton.isDisabled(), false, 'Barracks capacity and campaign resources allow this creature offer');
  report.offer = { choice: offerChoice, terms: offered.dwelling, payment, resourcesUnchanged: true };
  const termsBeforeBack = offered.dwelling;
  await clickChoice('[data-choice="back-dwelling"]');
  await page.waitForFunction(() => !document.querySelector('#panel')?.classList.contains('open'));
  const afterBack = (await snapshot()).state;
  assert.deepEqual(afterBack.dwelling, termsBeforeBack, 'Back closes the inspector without declining or rerolling the offer');
  assert.deepEqual(afterBack.resources, report.resourcesBefore, 'Back to road does not spend resources');
  await clickChoice('[data-choice="inspect:adventure"]');
  await page.waitForFunction(() => document.querySelector('#panel')?.classList.contains('open'));
  assert.deepEqual((await snapshot()).state.dwelling, termsBeforeBack, 'reopening the site presents the same fixed offer');
  report.backAction = { panelClosed: true, offerPreserved: true, resourcesUnchanged: true };
  await page.setViewportSize({ width: 825, height: 375 });
  await page.locator('#choices').evaluate(node => { node.scrollTop = 0; });
  await page.waitForTimeout(120);
  const claimBounds = await page.locator('[data-choice="claim-dwelling"]:visible').boundingBox();
  const panelBounds = await page.locator('#panel').boundingBox();
  const claimDom = await page.evaluate(() => [...document.querySelectorAll('[data-choice="claim-dwelling"]')].map(node => {
    const box = node.getBoundingClientRect();
    const style = getComputedStyle(node);
    return { text: node.textContent.trim(), box: { left: box.left, top: box.top, right: box.right, bottom: box.bottom }, display: style.display, visibility: style.visibility, opacity: style.opacity, parent: node.parentElement?.id || node.parentElement?.className || node.parentElement?.tagName };
  }));
  report.offer.phoneBounds = { claim: claimBounds, claimDom, panel: panelBounds, choicesScrollTop: await page.locator('#choices').evaluate(node => node.scrollTop) };
  await capture('dwelling-offer-context', '825x375');
  assert.ok(claimBounds && panelBounds && claimBounds.y >= panelBounds.y && claimBounds.y + claimBounds.height <= panelBounds.y + panelBounds.height, 'the creature claim action is immediately visible without scrolling at 825x375');
  report.offer.claimVisibleWithoutScrollAt825x375 = true;

  await page.setViewportSize({ width: 1280, height: 720 });
  await page.waitForTimeout(120);
  await page.locator('#save').click();
  await page.waitForFunction(id => {
    const state = window.rebornSnapshot();
    const head = window.rebornCommittedHead();
    return state?.id === id && head?.campaignId === id && head.revision >= state.revision;
  }, report.campaignId, { timeout: 10000 });
  await page.reload({ waitUntil: 'networkidle' });
  await page.waitForFunction(id => window.rebornSnapshot()?.id === id, report.campaignId, { timeout: 10000 });
  let afterReload = await snapshot();
  if (afterReload.view === 'home' && await page.locator('[data-choice="continue"]:visible').count()) {
    await clickChoice('[data-choice="continue"]');
    afterReload = await snapshot();
  }
  if (afterReload.view !== 'adventure') {
    await clickChoice('[data-choice="nav:adventure"]');
    if (await page.locator('[data-choice="enter-adventure"]:visible').count()) await clickChoice('[data-choice="enter-adventure"]');
    await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'adventure');
    afterReload = await snapshot();
  }
  if (!await page.locator('#panel.open').count()) {
    await clickChoice('[data-choice="inspect:adventure"]');
    await page.waitForFunction(() => document.querySelector('#panel')?.classList.contains('open'));
  }
  assert.equal(afterReload.state.id, report.campaignId, 'reload retains the same campaign identity');
  assert.deepEqual(afterReload.state.dwelling, offered.dwelling, 'reload preserves the exact fixed dwelling offer');
  assert.deepEqual([afterReload.state.adventure.x, afterReload.state.adventure.y], dwellingSite.approach, 'reload preserves the site approach');
  assert.equal(afterReload.state.adventure.moves, arrived.state.adventure.moves, 'reload does not refill or spend movement');
  assert.equal(await page.locator('#world[data-adventure-traveler-mode="on-foot"][data-adventure-site-approach="dwelling"]').count(), 1, 'site interaction remains on foot after reload');
  assert.equal(await page.locator('#world [data-site-id="dwelling"]').count(), 1, 'site art remains visible after reload');
  report.reload = { campaignId: afterReload.state.id, adventure: afterReload.state.adventure, dwelling: afterReload.state.dwelling, travelerMode: 'on-foot' };
  await capture('dwelling-offer-reloaded', '1280x720');

  const beforeClaim = afterReload.state;
  await clickChoice('[data-choice="claim-dwelling"]');
  const claimed = await waitForState(value => value.dwelling?.claimed === true, 'claim the offered creatures');
  assert.deepEqual(claimed.state.dwelling, { ...offered.dwelling, claimed: true }, 'claiming marks the exact open offer as claimed');
  for (const [resource, amount] of Object.entries(payment)) {
    assert.equal(beforeClaim.resources[resource] - claimed.state.resources[resource], amount, `${resource} is charged exactly once at the displayed price`);
  }
  for (const resource of Object.keys(beforeClaim.resources)) {
    if (!(resource in payment)) assert.equal(claimed.state.resources[resource], beforeClaim.resources[resource], `${resource} is unchanged by the claim`);
  }
  const creatureStacks = claimed.state.army.filter(stack => stack.kind === 'creature' && stack.type === offered.dwelling.type);
  assert.equal(creatureStacks.length, 1, 'the accepted offer creates one creature stack');
  assert.equal(creatureStacks[0].count, offered.dwelling.count, 'the stack contains the exact offered creature count');
  assert.equal(claimed.state.army.length, beforeClaim.army.length + 1, 'the Barracks capacity admits exactly one new stack');
  assert.equal(claimed.state.dwellingHistory.filter(row => row.type === offered.dwelling.type && row.claimed).length, 1, 'the offer history records one successful claim');
  const expectedAvailableTypes = dwellingPool(data, claimed.state.age).filter(type => !claimed.state.dwellingHistory.some(row => row.type === type)).sort();
  await page.waitForFunction(expected => {
    const actual = [...document.querySelectorAll('[data-choice^="offer-dwelling:"]')]
      .map(node => node.getAttribute('data-choice').slice('offer-dwelling:'.length)).sort();
    return JSON.stringify(actual) === JSON.stringify(expected);
  }, expectedAvailableTypes, { timeout: 5000 });
  assert.equal(await page.locator(`[data-choice="offer-dwelling:${offered.dwelling.type}"]`).count(), 0, 'a claimed creature type is no longer offered by the UI');
  report.remainingOfferTypes = expectedAvailableTypes;
  await page.waitForFunction(id => {
    const state = window.rebornSnapshot();
    const head = window.rebornCommittedHead();
    return state?.id === id && head?.campaignId === id && head.revision >= state.revision;
  }, report.campaignId, { timeout: 10000 });
  await page.setViewportSize({ width: 825, height: 375 });
  await capture('dwelling-site-after-claim', '825x375');
  await page.reload({ waitUntil: 'networkidle' });
  await page.waitForFunction(id => {
    const state = window.rebornSnapshot();
    const head = window.rebornCommittedHead();
    return state?.id === id && state.dwelling?.claimed === true && head?.campaignId === id && head.revision >= state.revision;
  }, report.campaignId, { timeout: 10000 });
  const claimedReload = await page.evaluate(() => window.rebornSnapshot());
  assert.equal(claimedReload.dwelling.claimed, true, 'the claimed offer stays closed after reload');
  assert.equal(claimedReload.army.filter(stack => stack.kind === 'creature' && stack.type === offered.dwelling.type).length, 1, 'reload does not duplicate the recruited creature stack');
  assert.equal(claimedReload.army.find(stack => stack.kind === 'creature' && stack.type === offered.dwelling.type).count, offered.dwelling.count, 'reload preserves the creature count');
  assert.deepEqual(claimedReload.resources, claimed.state.resources, 'reload preserves the once-paid resource balances');
  assert.equal(claimedReload.dwellingHistory.filter(row => row.type === offered.dwelling.type && row.claimed).length, 1, 'reload preserves exactly one claim transaction');
  if (await page.locator('[data-choice="continue"]:visible').count()) await clickChoice('[data-choice="continue"]');
  if (await page.evaluate(() => document.querySelector('#app')?.dataset.view) !== 'army') await clickChoice('[data-choice="nav:army"]');
  await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'army', null, { timeout: 5000 });
  const creatureId = claimedReload.army.find(stack => stack.kind === 'creature' && stack.type === offered.dwelling.type).id;
  const creatureCard = page.locator(`[data-choice="roster:${creatureId}"]`).first();
  await creatureCard.waitFor({ state: 'visible', timeout: 5000 });
  await creatureCard.click();
  await page.waitForFunction(id => document.querySelector(`[data-choice="roster:${id}"]`)?.getAttribute('aria-pressed') === 'true', creatureId);
  const rosterScreen = await creatureCard.evaluate(node => {
    const box = node.getBoundingClientRect();
    const image = node.querySelector('img');
    return {
      label: node.querySelector('.roster-unit-label')?.textContent?.trim() || '',
      accessibleName: node.getAttribute('aria-label') || '',
      selected: node.getAttribute('aria-pressed') === 'true',
      imageLoaded: Boolean(image?.complete && image.naturalWidth > 0),
      bounds: { left: box.left, top: box.top, right: box.right, bottom: box.bottom },
      viewport: { width: window.innerWidth, height: window.innerHeight },
    };
  });
  assert.match(rosterScreen.label, new RegExp(offered.dwelling.type, 'i'), 'the claimed creature has a named Army roster card');
  assert.match(rosterScreen.accessibleName, new RegExp(offered.dwelling.type, 'i'), 'the creature card exposes its accessible name');
  assert.equal(rosterScreen.selected, true, 'the claimed creature can be selected after reload');
  assert.equal(rosterScreen.imageLoaded, true, 'the selected creature card uses loaded age-correct artwork');
  assert.ok(rosterScreen.bounds.left >= 0 && rosterScreen.bounds.top >= 0 && rosterScreen.bounds.right <= rosterScreen.viewport.width && rosterScreen.bounds.bottom <= rosterScreen.viewport.height, 'the claimed creature card stays fully within the compact landscape viewport');
  const rosterCapture = path.join(out, 'army-after-dwelling-claim-825x375.png');
  await page.screenshot({ path: rosterCapture });
  report.captures.push({ name: 'army-after-dwelling-claim', size: '825x375', file: path.relative(root, rosterCapture) });
  report.rosterScreen = rosterScreen;
  report.claim = { payment, creatureType: offered.dwelling.type, count: offered.dwelling.count, armyStacksBefore: beforeClaim.army.length, armyStacksAfter: claimed.state.army.length, resourcesBefore: beforeClaim.resources, resourcesAfter: claimedReload.resources, claimed: claimedReload.dwelling.claimed, historyRows: claimedReload.dwellingHistory.filter(row => row.type === offered.dwelling.type && row.claimed).length };
  report.reloadAfterClaim = { campaignId: claimedReload.id, claimed: claimedReload.dwelling.claimed, creatureStack: claimedReload.army.find(stack => stack.kind === 'creature' && stack.type === offered.dwelling.type), resources: claimedReload.resources };

  await openObjectives();
  await page.locator('#scene-ui [data-quest-id="q3"]').evaluate(element => element.scrollIntoView({ block: 'center', inline: 'nearest' }));
  const q3Ready = await page.evaluate(() => {
    const state = window.rebornSnapshot();
    const card = document.querySelector('#scene-ui [data-quest-id="q3"]');
    const claim = card?.querySelector('[data-choice="journal-claim:q3"]');
    return {
      quest: state.quests.q3,
      progress: card?.querySelector('.quest-progress')?.textContent?.trim() || '',
      status: card?.querySelector('p')?.textContent?.trim() || '',
      reward: card?.querySelector('.quest-reward')?.innerText?.replace(/\s+/g, ' ').trim() || '',
      claimPresent: Boolean(claim),
      claimDisabled: claim?.disabled ?? null,
    };
  });
  assert.equal(q3Ready.progress, '1 / 1 wild creature');
  assert.equal(q3Ready.status, 'Ready to claim');
  assert.match(q3Ready.reward, /200/);
  assert.match(q3Ready.reward, /150/);
  assert.equal(q3Ready.claimPresent, true);
  assert.equal(q3Ready.claimDisabled, false);
  await capture('q3-ready', '825x375');
  const beforeQ3 = await snapshot();
  await clickChoice('#scene-ui [data-choice="journal-claim:q3"]');
  const afterQ3 = await waitForState(state => state.quests.q3.claimed === true, 'claim wild-creature quest');
  const q3ElapsedMs = afterQ3.state.clock - beforeQ3.state.clock;
  const q3Income = rates(beforeQ3.state);
  const q3Payout = Object.fromEntries(['food', 'gold'].map(resource => [resource,
    afterQ3.state.resources[resource] - beforeQ3.state.resources[resource] - q3Income[resource] * q3ElapsedMs / 1000]));
  assert.ok(Math.abs(q3Payout.food - 200) < 1e-6, 'Q3 grants exactly 200 food after passive income');
  assert.ok(Math.abs(q3Payout.gold - 150) < 1e-6, 'Q3 grants exactly 150 gold after passive income');
  assert.equal(await page.locator('#scene-ui [data-choice="journal-claim:q3"]').count(), 0, 'claimed Q3 no longer offers its claim action');
  await capture('q3-claimed', '1280x720');
  await page.waitForFunction(id => {
    const state = window.rebornSnapshot();
    const head = window.rebornCommittedHead();
    return state?.id === id && state.quests.q3.claimed && head?.campaignId === id && head.revision >= state.revision;
  }, report.campaignId, { timeout: 10000 });
  await page.reload({ waitUntil: 'networkidle' });
  await page.waitForFunction(id => window.rebornSnapshot()?.id === id, report.campaignId, { timeout: 10000 });
  await openObjectives();
  const afterQ3Reload = await page.evaluate(() => window.rebornSnapshot());
  const reloadElapsedMs = afterQ3Reload.clock - afterQ3.state.clock;
  const reloadIncome = rates(afterQ3.state);
  const q3RepeatPayout = Object.fromEntries(['food', 'gold'].map(resource => [resource,
    afterQ3Reload.resources[resource] - afterQ3.state.resources[resource] - reloadIncome[resource] * reloadElapsedMs / 1000]));
  assert.equal(afterQ3Reload.quests.q3.claimed, true);
  assert.ok(Math.abs(q3RepeatPayout.food) < 1e-6, 'reload does not pay Q3 food twice');
  assert.ok(Math.abs(q3RepeatPayout.gold) < 1e-6, 'reload does not pay Q3 gold twice');
  report.q3 = { ready: q3Ready, payout: q3Payout, reloadRepeatPayout: q3RepeatPayout, claimed: afterQ3Reload.quests.q3.claimed };
  report.errors = [...new Set(report.errors)];
  report.notFound = [...new Set(report.notFound)];
  assert.deepEqual(report.errors, [], 'the natural on-foot journey has no browser errors');
  assert.deepEqual(report.notFound, [], 'the natural on-foot journey has no missing assets');
  report.passed = true;
} catch (error) {
  report.passed = false;
  report.failure = String(error);
} finally {
  report.recordedAt = new Date().toISOString();
  await fs.writeFile(path.join(out, 'report.json'), JSON.stringify(report, null, 2) + '\n');
  await browser.close();
}

if (!report.passed) throw new Error(report.failure);
  console.log(JSON.stringify({ passed: report.passed, campaignId: report.campaignId, route: report.route, arrival: report.arrival, offer: report.offer, backAction: report.backAction, remainingOfferTypes: report.remainingOfferTypes, claim: report.claim, rosterScreen: report.rosterScreen, reloadAfterClaim: report.reloadAfterClaim, captures: report.captures.length, errors: report.errors, notFound: report.notFound }, null, 2));
