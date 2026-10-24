import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import contract from '../../../src/data/implementation-contract.json' with { type: 'json' };
import worlds from '../../../src/data/adventure-worlds.json' with { type: 'json' };
import data from '../../../src/data/reference-data.json' with { type: 'json' };
import { dwellingCost } from '../../../src/core/mechanics.js';
import { adventureGeometryForWorld, adventureMap, routeTo, stepCost } from '../../../src/core/navigation.js';

const root = process.cwd();
const runId = process.argv[2] || 'run01';
assert.match(runId, /^run\d{2}$/, 'run id has the form runNN');
const out = path.join(root, `qa/game-completion-20261022/visual-review/adventure-mesa-savanna-owner-map-natural-live-20261022-${runId}`);
await fs.mkdir(out, { recursive: true });

const selectedWorld = worlds.find(world => world.id === 'mesa-savanna');
assert.ok(selectedWorld, 'the crossing campaign uses the registered Red Mesa Frontier world');
const bridgeOrder = ['mesa-west-north-rope-bridge', 'mesa-west-south-rope-bridge', 'mesa-east-north-rope-bridge', 'mesa-east-south-rope-bridge'];
const report = {
  recordedAt: new Date().toISOString(),
  classification: 'NATURAL_UI_MESA_SAVANNA_OWNER_MAP_FOUR_BRIDGES_SIX_SITES_TOWN_RETURN_REENTRY_WITH_RELOAD_BOUNDED_NOT_FULL_MAP_OR_OWNER_ACCEPTANCE',
  journey: 'fresh visible campaign -> build Barracks -> enter Red Mesa Frontier -> naturally traverse all four registered bridge decks -> visit and interact with all six registered sites -> return to Town and re-enter Adventure -> persist and reload position, rewards and discoveries',
  url: 'http://127.0.0.1:4179/?audit=1',
  viewport: '1280x720',
  bridgeOrder,
  campaignId: null,
  layoutId: null,
  seed: null,
  renderBinding: null,
  start: null,
  crossings: [],
  siteInteractions: [],
  townReturn: null,
  townReentry: null,
  captures: [],
  responsiveCaptures: [],
  errors: [],
  notFound: [],
};
let totalDaysEnded = 0;

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
async function waitForState(predicate, label, timeout = 12000) {
  const deadline = Date.now() + timeout;
  while (Date.now() < deadline) {
    const value = await snapshot();
    if (value.state && predicate(value.state)) return value;
    await page.waitForTimeout(100);
  }
  throw new Error(`Timed out waiting for ${label}`);
}
function sameCell(a, b) { return a[0] === b[0] && a[1] === b[1]; }
function planCrossing(map, position, bridge) {
  const directions = [[bridge.approaches[0], bridge.approaches[1]], [bridge.approaches[1], bridge.approaches[0]]];
  const candidates = [];
  for (const [from, to] of directions) {
    try {
      const approachRoute = sameCell(position, from) ? { cells: [], cost: 0, destination: from } : routeTo(map, position, from);
      if (approachRoute.cells.some(cell => bridge.cells.some(deck => sameCell(cell, deck)))) continue;
      const crossingRoute = routeTo(map, from, to);
      if (!sameCell(crossingRoute.destination, to)) continue;
      if (!bridge.cells.every(deck => crossingRoute.cells.some(cell => sameCell(cell, deck)))) continue;
      const cells = [...approachRoute.cells, ...crossingRoute.cells];
      if (cells.some(cell => map.guards.has(cell.join(',')))) continue;
      candidates.push({ from, to, approachRoute, crossingRoute, cells });
    } catch {
      // Try the opposite safe bank before classifying this layout as unroutable.
    }
  }
  candidates.sort((first, second) => first.approachRoute.cost - second.approachRoute.cost
    || first.approachRoute.cells.length - second.approachRoute.cells.length);
  return candidates[0] ?? null;
}
async function endDay(from) {
  const before = await snapshot();
  const oldMoves = before.state.adventure.moves;
  if (!await page.locator('#panel.open').count()) {
    await clickChoice('[data-choice="inspect:adventure"]');
    await page.waitForFunction(() => document.querySelector('#panel')?.classList.contains('open'));
  }
  await clickChoice('[data-choice="adventure-end-day"]');
  await waitForState(state => state.adventure?.x === from[0] && state.adventure?.y === from[1]
    && state.adventure.moves > oldMoves, 'restore daily Adventure movement');
  totalDaysEnded += 1;
  await page.locator('#panel-close').click();
  await page.waitForFunction(() => !document.querySelector('#panel')?.classList.contains('open'));
}
async function moveNaturally(from, cell) {
  const cost = stepCost(liveMap, from, cell);
  let before = await snapshot();
  if (before.state.adventure.moves < cost) {
    await endDay(from);
    before = await snapshot();
  }
  assert.ok(before.state.adventure.moves >= cost, `movement is available for ${cell.join(',')}`);
  const target = page.locator(`#world [data-adventure-cell="${cell.join(',')}"]`);
  assert.equal(await target.count(), 1, `the next legal cell ${cell.join(',')} is visible in the live map`);
  await target.click();
  await page.waitForFunction(() => Boolean(document.querySelector('[data-choice="confirm-route"]')));
  const title = await page.locator('[data-choice="confirm-route"]').first().getAttribute('title');
  assert.match(title || '', new RegExp(`cost ${cost}`), `the adjacent step preview reports cost ${cost}`);
  await clickChoice('[data-choice="confirm-route"]');
  const moved = await waitForState(state => state.adventure?.x === cell[0] && state.adventure?.y === cell[1], `move to ${cell.join(',')}`);
  assert.equal(moved.state.adventure.moves, before.state.adventure.moves - cost, `step ${cell.join(',')} spends its movement cost once`);
  assert.equal(moved.state.adventure.pendingEncounter, null, `step ${cell.join(',')} does not bypass a guard`);
  return cost;
}
async function capture(name) {
  const file = path.join(out, `${name}-1280x720.png`);
  await page.screenshot({ path: file });
  report.captures.push({ name, viewport: '1280x720', file: path.relative(root, file) });
}
async function captureResponsive(name, width, height) {
  await page.setViewportSize({ width, height });
  await page.waitForTimeout(120);
  const layout = await page.evaluate(() => {
    const world = document.querySelector('#world');
    const r = world?.getBoundingClientRect();
    const hero = document.querySelector('#world [data-actor="knight"]')?.getBoundingClientRect();
    return {
      viewport: { width: innerWidth, height: innerHeight },
      world: r ? { left: r.left, top: r.top, right: r.right, bottom: r.bottom, width: r.width, height: r.height } : null,
      mapCellCount: document.querySelectorAll('#world [data-adventure-cell]').length,
      hero: hero ? { left: hero.left, top: hero.top, right: hero.right, bottom: hero.bottom } : null,
      documentScroll: { width: document.documentElement.scrollWidth, height: document.documentElement.scrollHeight },
    };
  });
  const file = path.join(out, `${name}-${width}x${height}.png`);
  await page.screenshot({ path: file });
  report.responsiveCaptures.push({ name, viewport: `${width}x${height}`, layout, file: path.relative(root, file) });
}

let liveGeometry;
let liveMap;
try {
  await page.goto(report.url, { waitUntil: 'networkidle' });
  await clickChoice('[data-choice="new-campaign"]');
  await clickChoice('[data-choice="campaign-world:mesa-savanna"]');
  await clickChoice('[data-choice="begin-selected-world"]');
  await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'hero');
  await clickChoice('[data-choice="scene-class:knight"]');
  await clickChoice('[data-choice="scene-enter-valley"]');
  await page.waitForFunction(() => window.rebornSnapshot()?.age === 0 && document.querySelector('#app')?.dataset.view === 'kingdom');
  const campaign = await snapshot();
  report.campaignId = campaign.state.id;

  const emptyPlot = campaign.state.plots.find(plot => plot.id !== 'townhall' && plot.level === 0);
  assert.ok(emptyPlot, 'the fresh campaign has an available Barracks plot');
  await clickChoice(`[data-choice="site:${emptyPlot.id}"]`);
  await clickChoice(`[data-choice="build-picker:${emptyPlot.id}"]`);
  await clickChoice(`[data-choice="build:${emptyPlot.id}:barracks"]`);
  await page.locator('#build-commit').click();
  await waitForState(state => {
    const plot = state.plots.find(row => row.id === emptyPlot.id);
    return plot?.type === 'barracks' && plot.level === 1 && !state.buildJobs.some(job => job.plotId === emptyPlot.id);
  }, 'finish Barracks construction', 20000);

  await clickChoice('[data-choice="nav:adventure"]');
  await clickChoice('[data-choice="enter-adventure"]');
  const start = await waitForState(state => state.adventure?.atTown === false, 'enter the Red Mesa Frontier map');
  report.start = { ...start.state.adventure };
  report.seed = start.state.seed;
  liveGeometry = adventureGeometryForWorld(contract.geometry.adventure, selectedWorld, start.state.seed);
  liveMap = adventureMap(liveGeometry);
  report.layoutId = liveGeometry.layoutId;
  const liveWorld = page.locator('#world[data-adventure-world-id="mesa-savanna"][data-adventure-bridge-count="4"][data-adventure-playable-crossings="4"][data-adventure-render-model="integrated-map-art-plus-live-interactions"]');
  assert.equal(await liveWorld.count(), 1, 'the live renderer binds Red Mesa Frontier owner art with its four registered playable crossings');
  assert.equal(await liveWorld.getAttribute('data-adventure-terrain-file'), selectedWorld.file, 'the visible map uses the selected owner painting');
  report.renderBinding = {
    worldId: await liveWorld.getAttribute('data-adventure-world-id'),
    terrainFile: await liveWorld.getAttribute('data-adventure-terrain-file'),
    renderModel: await liveWorld.getAttribute('data-adventure-render-model'),
    registeredBridgeCount: Number(await liveWorld.getAttribute('data-adventure-bridge-count')),
    playableCrossingCount: Number(await liveWorld.getAttribute('data-adventure-playable-crossings')),
    artMode: 'painted source bridges remain in the integrated owner painting; no duplicate generic bridge stamp is expected',
    sourceSize: selectedWorld.geometry.sourceSize,
  };
  await capture('mesa-savanna-start');
  for (const [width, height] of [[825, 375], [933, 424]]) await captureResponsive('mesa-savanna-start', width, height);
  await page.setViewportSize({ width: 1280, height: 720 });
  await page.waitForTimeout(120);

  let position = [start.state.adventure.x, start.state.adventure.y];
  for (const bridgeId of bridgeOrder) {
    const bridge = liveGeometry.bridges.find(item => item.id === bridgeId);
    assert.ok(bridge, `${bridgeId} exists in the selected campaign geometry`);
    const plan = planCrossing(liveMap, position, bridge);
    assert.ok(plan, `${bridgeId} has a guard-free route from the current hero position for the campaign's actual seed`);
    const beforeCrossing = [...position];
    const daysBeforeCrossing = totalDaysEnded;
    let totalCost = 0;
    const crossed = [];
    let from = [...position];
    for (const cell of plan.cells) {
      totalCost += await moveNaturally(from, cell);
      crossed.push([...cell]);
      from = [...cell];
    }
    position = [...plan.to];
    const state = (await snapshot()).state;
    assert.deepEqual([state.adventure.x, state.adventure.y], plan.to, `${bridgeId} reaches the far bank`);
    assert.equal(state.adventure.pendingEncounter, null, `${bridgeId} crossing remains a natural peaceful journey`);
    for (const deck of bridge.cells) {
      assert.ok(crossed.some(cell => sameCell(cell, deck)), `${bridgeId} journey visits deck ${deck.join(',')}`);
      assert.ok(state.adventure.visited.includes(deck.join(',')), `${bridgeId} deck ${deck.join(',')} is discovered in the campaign`);
    }
    await capture(`after-${bridgeId}`);
    report.crossings.push({
      bridgeId,
      start: beforeCrossing,
      nearBank: plan.from,
      farBank: plan.to,
      approachCells: plan.approachRoute.cells,
      deckCells: bridge.cells,
      crossingCells: plan.crossingRoute.cells,
      committedCells: crossed,
      movementCost: totalCost,
      daysEnded: totalDaysEnded - daysBeforeCrossing,
      finalPosition: position,
      allDeckVisited: bridge.cells.every(deck => state.adventure.visited.includes(deck.join(','))),
    });
  }

  for (const siteId of ['shrine', 'ruin', 'mill', 'mine', 'dwelling']) {
    const site = liveGeometry.sites.find(item => item.id === siteId);
    assert.ok(site, `${siteId} is registered in the Red Mesa Frontier source geometry`);
    const siteStart = [...position];
    const route = sameCell(position, site.approach) ? { cells: [], cost: 0, destination: site.approach } : routeTo(liveMap, position, site.approach);
    assert.deepEqual(route.destination, site.approach, `${siteId} approach is reachable through the live map`);
    assert.equal(route.cells.some(cell => liveMap.guards.has(cell.join(','))), false, `${siteId} journey does not shortcut a guard`);
    let from = [...position];
    for (const cell of route.cells) {
      await moveNaturally(from, cell);
      from = [...cell];
    }
    position = [...site.approach];
    await page.waitForFunction(id => document.querySelector('#world')?.dataset.adventureSiteApproach === id, siteId);
    const onFootTraveler = page.locator('#world [data-actor="knight"][data-adventure-travel-mode="on-foot"]');
    assert.equal(await onFootTraveler.count(), 1, `${siteId} presents the on-foot traveler at its approach`);
    assert.equal(await onFootTraveler.getAttribute('pointer-events'), 'none', 'the decorative on-foot rig does not block map-cell input');
    if (!await page.locator('#panel.open').count()) {
      await clickChoice('[data-choice="inspect:adventure"]');
      await page.waitForFunction(() => document.querySelector('#panel')?.classList.contains('open'));
    }
    const before = (await snapshot()).state;
    let interaction;
    if (siteId === 'shrine') {
      assert.equal(before.hero.offers.some(offer => !offer.chosen && !offer.declined), false,
        'the fresh campaign has no unrelated pending skill offer before studying the shrine');
      await clickChoice('[data-choice="study-skill-monument"]');
      const offered = await waitForState(state => state.hero.offers.some(offer => offer.source === 'adventure-shrine' && !offer.chosen && !offer.declined),
        'the Red Mesa Frontier shrine creates its saved skill offer');
      const offer = offered.state.hero.offers.find(item => item.source === 'adventure-shrine' && !item.chosen && !item.declined);
      assert.ok(offer?.choices?.length, 'the shrine offer contains skill choices');
      const choice = page.locator('[data-choice^="shrine-skill:"]').first();
      await choice.waitFor({ state: 'visible', timeout: 10000 });
      const choiceKey = await choice.getAttribute('data-choice');
      const skillId = choiceKey?.slice('shrine-skill:'.length);
      assert.ok(skillId && offer.choices.includes(skillId), 'the visible skill choice belongs to the saved shrine offer');
      await clickChoice(`[data-choice="shrine-skill:${skillId}"]`);
      const resolved = await waitForState(state => state.adventure?.claimedSites?.includes('shrine'), 'resolve the shrine lesson once');
      assert.equal(resolved.state.hero.skills[skillId], before.hero.skills[skillId] + 1, 'the shrine increases the selected skill by one rank');
      interaction = { siteId, start: siteStart, approach: position, route: route.cells, routeCost: route.cost, skillId, choices: offer.choices, claimed: true, skillRankBefore: before.hero.skills[skillId], skillRankAfter: resolved.state.hero.skills[skillId] };
    } else if (siteId === 'dwelling') {
      const offerControl = page.locator('[data-choice^="offer-dwelling:"]').first();
      await offerControl.waitFor({ state: 'visible', timeout: 10000 });
      const offerChoice = await offerControl.getAttribute('data-choice');
      assert.ok(offerChoice, 'the discovered dwelling presents a visible creature offer');
      await clickChoice(`[data-choice="${offerChoice}"]`);
      const offered = await waitForState(state => Boolean(state.dwelling?.type), 'the dwelling fixes a creature offer');
      const payment = dwellingCost(data, offered.state.dwelling.type, offered.state.dwelling.multiplier);
      const claimControl = page.locator('[data-choice="claim-dwelling"]');
      await claimControl.waitFor({ state: 'visible', timeout: 10000 });
      assert.equal(await claimControl.isDisabled(), false, 'Barracks capacity and campaign resources allow the dwelling offer');
      const claimBefore = offered.state;
      await clickChoice('[data-choice="claim-dwelling"]');
      const claimed = await waitForState(state => state.dwelling?.claimed === true, 'claim the offered dwelling creatures');
      for (const [resource, amount] of Object.entries(payment)) {
        assert.equal(claimBefore.resources[resource] - claimed.state.resources[resource], amount, `${resource} is charged exactly once at the displayed dwelling price`);
      }
      const creatureStacks = claimed.state.army.filter(stack => stack.kind === 'creature' && stack.type === offered.state.dwelling.type);
      assert.equal(creatureStacks.length, 1, 'the accepted dwelling offer creates one creature stack');
      assert.equal(creatureStacks[0].count, offered.state.dwelling.count, 'the stack contains the exact offered creature count');
      interaction = { siteId, start: siteStart, approach: position, route: route.cells, routeCost: route.cost, offerChoice, terms: offered.state.dwelling, payment, claimed: true };
    } else {
      const control = page.locator(`[data-choice="claim-site:${siteId}"]`);
      await control.waitFor({ state: 'visible', timeout: 10000 });
      const choiceText = (await control.textContent())?.trim() || '';
      await clickChoice(`[data-choice="claim-site:${siteId}"]`);
      const claimed = await waitForState(state => state.adventure?.claimedSites?.includes(siteId), `claim the ${siteId} site reward once`);
      if (siteId === 'mill') {
        const amount = before.adventure.siteOffers.millFood;
        assert.equal(claimed.state.resources.food - before.resources.food, amount, 'the mill grants its saved food offer once');
        interaction = { siteId, start: siteStart, approach: position, route: route.cells, routeCost: route.cost, choiceText, amount, resource: 'food', claimed: true };
      } else if (siteId === 'mine') {
        const amount = before.adventure.siteOffers.mineGold;
        assert.equal(claimed.state.resources.gold - before.resources.gold, amount, 'the mine grants its saved gold offer once');
        interaction = { siteId, start: siteStart, approach: position, route: route.cells, routeCost: route.cost, choiceText, amount, resource: 'gold', claimed: true };
      } else {
        const xpBefore = before.hero.xp;
        const xpAfter = claimed.state.hero.xp;
        assert.ok(xpAfter > xpBefore || claimed.state.hero.level > before.hero.level, 'the ruin grants hero experience once');
        interaction = { siteId, start: siteStart, approach: position, route: route.cells, routeCost: route.cost, choiceText, xpBefore, xpAfter, levelBefore: before.hero.level, levelAfter: claimed.state.hero.level, claimed: true };
      }
    }
    const afterInteraction = (await snapshot()).state;
    if (siteId === 'dwelling') assert.equal(afterInteraction.dwelling?.claimed, true, 'the dwelling offer is recorded in its dedicated campaign state');
    else assert.equal(afterInteraction.adventure.claimedSites.includes(siteId), true, `${siteId} is recorded as claimed in the campaign`);
    await capture(`after-site-${siteId}`);
    report.siteInteractions.push(interaction);
    if (await page.locator('#panel.open').count()) {
      await page.locator('#panel-close').click();
      await page.waitForFunction(() => !document.querySelector('#panel')?.classList.contains('open'));
    }
  }

  const town = liveGeometry.sites.find(site => site.id === 'town');
  assert.ok(town, 'the Red Mesa Frontier Town approach remains registered');
  const townStart = [...position];
  const townRoute = sameCell(position, town.approach) ? { cells: [], cost: 0, destination: town.approach } : routeTo(liveMap, position, town.approach);
  assert.deepEqual(townRoute.destination, town.approach, 'the hero can naturally return to the Town approach');
  assert.equal(townRoute.cells.some(cell => liveMap.guards.has(cell.join(','))), false, 'the return route does not bypass a guard');
  let townFrom = [...position];
  for (const cell of townRoute.cells) {
    await moveNaturally(townFrom, cell);
    townFrom = [...cell];
  }
  position = [...town.approach];
  const atTownApproach = (await snapshot()).state.adventure;
  assert.deepEqual([atTownApproach.x, atTownApproach.y], position, 'natural travel reaches the exact Town approach');
  await capture('mesa-savanna-town-approach');
  await clickChoice('[data-choice="return-town"]');
  const returnedTown = await waitForState(state => state.adventure?.atTown === true, 'return to the Kingdom from the Red Mesa Frontier Town approach');
  await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'kingdom');
  assert.deepEqual([returnedTown.state.adventure.x, returnedTown.state.adventure.y], town.approach, 'Town return preserves the exact map position');
  report.townReturn = { start: townStart, route: townRoute.cells, routeCost: townRoute.cost, townApproach: town.approach, atTown: returnedTown.state.adventure.atTown, kingdomView: true };
  await capture('returned-to-kingdom');
  await clickChoice('[data-choice="nav:adventure"]');
  if (await page.locator('[data-choice="enter-adventure"]:visible').count()) await clickChoice('[data-choice="enter-adventure"]');
  const reentered = await waitForState(state => state.adventure?.atTown === false, 're-enter the existing Red Mesa Frontier journey');
  assert.deepEqual([reentered.state.adventure.x, reentered.state.adventure.y], town.approach, 're-entry resumes at the same Town approach');
  assert.ok(['shrine', 'ruin', 'mill', 'mine'].every(siteId => reentered.state.adventure.claimedSites.includes(siteId)), 'Adventure site claims remain while returning and re-entering');
  assert.equal(reentered.state.dwelling?.claimed, true, 'the dwelling purchase remains claimed while returning and re-entering');
  report.townReentry = { position: [reentered.state.adventure.x, reentered.state.adventure.y], atTown: reentered.state.adventure.atTown, visitedCount: reentered.state.adventure.visited.length, claimedSites: [...reentered.state.adventure.claimedSites] };
  position = [...town.approach];
  await capture('mesa-savanna-reentered-adventure');

  const beforeReload = await snapshot();
  await page.waitForFunction(id => {
    const state = window.rebornSnapshot();
    const head = window.rebornCommittedHead();
    return state?.id === id && head?.campaignId === id && head.revision >= state.revision;
  }, report.campaignId, { timeout: 10000 });
  await page.reload({ waitUntil: 'networkidle' });
  await page.waitForFunction(id => window.rebornSnapshot()?.id === id, report.campaignId, { timeout: 10000 });
  let afterReload = await snapshot();
  if (afterReload.view === 'home') {
    await clickChoice('[data-choice="continue"]');
    afterReload = await snapshot();
  }
  if (afterReload.view !== 'adventure') {
    await clickChoice('[data-choice="nav:adventure"]');
    if (await page.locator('[data-choice="enter-adventure"]:visible').count()) await clickChoice('[data-choice="enter-adventure"]');
    await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'adventure');
    afterReload = await snapshot();
  }
  assert.equal(afterReload.state.id, report.campaignId, 'reload preserves the original campaign');
  assert.deepEqual([afterReload.state.adventure.x, afterReload.state.adventure.y], position, 'reload restores the final site approach after the bridge and interaction itinerary');
  for (const bridgeId of bridgeOrder) {
    const bridge = liveGeometry.bridges.find(item => item.id === bridgeId);
    for (const deck of bridge.cells) assert.ok(afterReload.state.adventure.visited.includes(deck.join(',')), `${bridgeId} deck persists after reload`);
  }
  assert.equal(await page.locator('#world[data-adventure-world-id="mesa-savanna"][data-adventure-bridge-count="4"]').count(), 1, 'the Red Mesa Frontier owner painting and four bridge registrations return after reload');
  report.reload = {
    campaignId: afterReload.state.id,
    position: [afterReload.state.adventure.x, afterReload.state.adventure.y],
    allDecksRemainVisited: liveGeometry.bridges.flatMap(bridge => bridge.cells).every(([x, y]) => afterReload.state.adventure.visited.includes(`${x},${y}`)),
    revision: beforeReload.head?.revision,
    browserView: afterReload.view,
  };
  report.totalDaysEnded = totalDaysEnded;
  assert.equal(report.reload.allDecksRemainVisited, true, 'all four bridge decks and the final position persist across reload');
  for (const siteId of ['shrine', 'ruin', 'mill', 'mine']) {
    assert.ok(afterReload.state.adventure.claimedSites.includes(siteId), `${siteId} reward state persists after reload`);
  }
  report.reload.siteClaimsPersisted = ['shrine', 'ruin', 'mill', 'mine'].every(siteId => afterReload.state.adventure.claimedSites.includes(siteId));
  report.reload.dwellingClaimPersisted = afterReload.state.dwelling?.claimed === true;
  assert.equal(report.reload.siteClaimsPersisted, true, 'all four Adventure site interactions persist after reload');
  assert.equal(report.reload.dwellingClaimPersisted, true, 'the dwelling purchase persists after reload');
  report.passed = true;
} catch (error) {
  report.passed = false;
  report.error = String(error?.stack || error);
} finally {
  await fs.writeFile(path.join(out, 'report.json'), JSON.stringify(report, null, 2));
  await context.close();
  await browser.close();
}

assert.equal(report.passed, true, report.error || 'natural Red Mesa Frontier journey passed');
console.log(JSON.stringify(report, null, 2));
