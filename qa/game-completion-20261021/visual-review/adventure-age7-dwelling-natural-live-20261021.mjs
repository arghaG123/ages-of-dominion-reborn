import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import data from '../../../src/data/reference-data.json' with { type: 'json' };
import { cost, rates } from '../../../src/core/campaign.js';
import { agePrice } from '../../../src/core/rules.js';
import contract from '../../../src/data/implementation-contract.json' with { type: 'json' };
import worlds from '../../../src/data/adventure-worlds.json' with { type: 'json' };
import { adventureGeometryForWorld, adventureMap, routeTo } from '../../../src/core/navigation.js';
import { dwellingCost, dwellingPool } from '../../../src/core/mechanics.js';

const root = process.cwd();
const runId = process.argv[2] || 'run02';
assert.match(runId, /^run\d{2}$/, 'run id has the form runNN');
const out = path.join(root, 'qa/game-completion-20261021/visual-review/adventure-age7-dwelling-natural-live-20261021-' + runId);
await fs.mkdir(out, { recursive: true });
const report = {
  recordedAt: new Date().toISOString(),
  classification: 'NATURAL_UI_FUTURE_AGE_DWELLING_DRONE_CLAIM_RELOAD_NOT_FULL_GAME_OR_OWNER_ACCEPTANCE',
  journey: 'new campaign -> skip optional tutorial -> build four income sites -> upgrade Hall and walls -> pay the Stone, Bronze, Iron, Medieval, Gunpowder, Industrial, and Modern age gates -> capture natural Future Adventure -> build a Barracks -> travel by visible route previews to the registered dwelling -> ask for Drones -> save/reload the fixed offer -> claim the visible offer -> save/reload and inspect the Army roster',
  url: 'http://127.0.0.1:4179/?audit=1',
  note: 'All campaign, construction, movement, offer, claim, and save actions use visible controls. Playwright fast-forwards only idle elapsed time for natural resource production, construction, or day restoration. No campaign state, route, movement, or resources are injected. The earlier verified all-age runner supplies the naturally progressed campaign path through Future Age.',
  errors: [],
  failedResponses: [],
  ages: [],
  screenshots: [],
};
const browser = await chromium.launch({
  executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe',
  headless: true,
});
const context = await browser.newContext({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1 });
const page = await context.newPage();
await page.clock.install();
page.on('pageerror', error => report.errors.push(String(error)));
page.on('console', message => { if (message.type() === 'error') report.errors.push(message.text()); });
page.on('response', response => { if (response.status() >= 400) report.failedResponses.push({ status: response.status(), url: response.url() }); });

const read = () => page.evaluate(() => JSON.parse(document.querySelector('#audit-snapshot')?.textContent || 'null'));
async function clickChoice(id) {
  const control = page.locator('[data-choice="' + id + '"]').first();
  await control.waitFor({ state: 'visible', timeout: 10000 });
  assert.equal(await control.isDisabled(), false, id + ' is enabled');
  await control.click();
}
async function waitForState(predicate, label, timeoutSteps = 100) {
  for (let step = 0; step < timeoutSteps; step += 1) {
    const snapshot = await read();
    if (snapshot?.state && predicate(snapshot.state)) return snapshot.state;
    await page.clock.runFor(250);
  }
  throw new Error('Timed out waiting for ' + label);
}
async function clearInspector() {
  const close = page.locator('#panel-close');
  if (await close.isVisible().catch(() => false)) await close.click();
}
async function clearSceneSelection() {
  await clearInspector();
  const target = page.locator('#world');
  const bounds = await target.boundingBox();
  assert.ok(bounds, 'Kingdom world has a visible canvas');
  if (await page.locator('#world .plot.selected').count() === 0) return;
  for (const y of [0.45, 0.52, 0.6, 0.4, 0.3, 0.7]) {
    for (const x of [0.92, 0.08, 0.85, 0.15, 0.78, 0.22, 0.5]) {
      await page.mouse.click(bounds.x + bounds.width * x, bounds.y + bounds.height * y);
      if (await page.locator('#world .plot.selected').count() === 0) return;
      await clearInspector();
    }
  }
  throw new Error('Could not clear the selected-site outline on the Kingdom canvas');
}
async function waitForResources(required, label) {
  const ageCapsHours = [8, 7, 6, 5, 4, 3.5, 3, 3];
  for (let step = 0; step < 100; step += 1) {
    const state = (await read())?.state;
    assert.ok(state, 'campaign exists before ' + label);
    const short = Object.entries(required).filter(([key, value]) => state.resources[key] + 1e-6 < value);
    if (!short.length) return state;
    const income = rates(state);
    const waits = short.map(([key, value]) => {
      assert.ok(income[key] > 0, 'a legal producer supplies ' + key + ' for ' + label);
      return (value - state.resources[key]) / income[key];
    });
    const neededMs = Math.max(1000, Math.ceil(Math.max(...waits) * 1000) + 500);
    const capMs = Math.floor(ageCapsHours[state.age] * 3600000);
    const elapsed = Math.min(neededMs, capMs);
    await page.clock.fastForward(elapsed);
    await page.waitForTimeout(30);
  }
  throw new Error('Could not earn resources for ' + label + ': ' + JSON.stringify(required));
}
async function beginBuild(choice, payment, label) {
  await waitForResources(payment, label);
  await clickChoice(choice);
  await page.locator('#build-commit').waitFor({ state: 'visible', timeout: 10000 });
  await page.locator('#build-commit').click();
}
async function buildAt(siteId, building) {
  await clearInspector();
  await page.locator('#context').click();
  await clickChoice('site-list');
  await clickChoice('choose-site:' + siteId);
  await clickChoice('build-picker:' + siteId);
  await beginBuild('build:' + siteId + ':' + building, cost(data, building, 0), building + ' at ' + siteId);
  await waitForState(state => state.buildJobs.some(job => job.plotId === siteId && job.type === building), building + ' construction start');
  await page.clock.fastForward(10000);
  await page.waitForTimeout(30);
  return waitForState(state => state.plots.some(plot => plot.id === siteId && plot.type === building && plot.level === 1)
    && !state.buildJobs.some(job => job.plotId === siteId), building + ' completion');
}
async function buildHall(targetLevel) {
  let state = (await read()).state;
  while (state.plots.find(plot => plot.id === 'townhall').level < targetLevel) {
    const level = state.plots.find(plot => plot.id === 'townhall').level;
    const payment = cost(data, 'townhall', level);
    await clearInspector();
    await page.locator('#context').click();
    await clickChoice('site-list');
    await clickChoice('choose-site:townhall');
    await beginBuild('build:townhall:townhall', payment, 'Town Hall level ' + (level + 1));
    await waitForState(value => value.buildJobs.some(job => job.plotId === 'townhall'), 'Town Hall scaffold');
    await page.clock.fastForward(10000);
    await page.waitForTimeout(30);
    state = await waitForState(value => value.plots.find(plot => plot.id === 'townhall').level === level + 1
      && !value.buildJobs.some(job => job.plotId === 'townhall'), 'Town Hall level ' + (level + 1));
  }
  return state;
}
async function buildWall(targetLevel, age) {
  let state = (await read()).state;
  while (state.walls.level < targetLevel) {
    const level = state.walls.level;
    const payment = cost(data, 'walls', level);
    await clearInspector();
    await clickChoice('kingdom-actions-open');
    await beginBuild('build:walls', payment, 'Walls level ' + (level + 1) + ' in ' + data.AGES[age].n);
    state = await waitForState(value => value.buildJobs.some(job => job.plotId === 'walls'), 'wall scaffold');
    const scaffold = await sceneState();
    assert.equal(scaffold.wallPhase, 'scaffold', 'wall construction renders its same-age scaffold');
    report.ages[age].wallPhases.push(scaffold);
    report.screenshots.push(await captureScene('age-' + age + '-wall-scaffold', ['1280x720']));
    await page.clock.fastForward(10000);
    await page.waitForTimeout(30);
    state = await waitForState(value => value.walls.level === level + 1
      && !value.buildJobs.some(job => job.plotId === 'walls'), 'Walls level ' + (level + 1));
    const completed = await sceneState();
    report.ages[age].wallPhases.push(completed);
    report.screenshots.push(await captureScene('age-' + age + '-wall-level-' + (level + 1), ['1280x720']));
  }
  return state;
}
async function sceneState() {
  await page.waitForTimeout(40);
  return page.evaluate(() => {
    const terrain = document.querySelector('#terrain');
    const wall = document.querySelector('#world [data-walls-phase]');
    const rendered = [...document.querySelectorAll('#world image[aria-label]')].map(image => {
      const box = image.getBBox();
      return { label: image.getAttribute('aria-label'), href: image.getAttribute('href'), box: [box.x, box.y, box.width, box.height].map(value => Math.round(value * 10) / 10) };
    });
    return {
      view: document.querySelector('#app')?.dataset.view,
      terrainStatus: terrain?.dataset.terrainStatus,
      terrain: terrain?.getAttribute('src'),
      terrainLoaded: Boolean(terrain?.complete && terrain?.naturalWidth > 0),
      wallPhase: wall?.getAttribute('data-walls-phase'),
      wallLevel: Number(wall?.getAttribute('data-walls-level')),
      wallKind: wall?.getAttribute('data-walls-kind'),
      wallPainting: wall?.getAttribute('data-walls-painting'),
      wallStamps: Number(wall?.getAttribute('data-wall-stamps')),
      renderedBuildings: rendered,
    };
  });
}
async function captureScene(name, sizes) {
  await clearSceneSelection();
  const records = [];
  for (const size of sizes) {
    const [width, height] = size.split('x').map(Number);
    await page.setViewportSize({ width, height });
    await page.waitForTimeout(100);
    const file = path.join(out, name + '-' + size + '.png');
    await page.screenshot({ path: file });
    records.push({ name, size, file: path.relative(root, file) });
  }
  return { scene: await sceneState(), captures: records };
}
async function captureAdventureAge(age) {
  await page.locator('[data-choice="nav:adventure"]').first().click();
  let state = (await read()).state;
  if (!state.adventure || state.adventure.atTown) await clickChoice('enter-adventure');
  state = await waitForState(value => value.age === age && value.adventure?.atTown === false, 'Adventure map in ' + data.AGES[age].n);
  const scene = await sceneState();
  assert.equal(scene.view, 'adventure');
  assert.equal(scene.terrainLoaded, true, data.AGES[age].n + ' Adventure terrain loads');
  const details = await page.evaluate(() => ({
    board: document.querySelector('#world')?.getAttribute('data-board'),
    mountedTraveler: document.querySelectorAll('#world [data-mount]').length === 1,
    visibleSites: document.querySelectorAll('#world .adventure-site').length,
    visitedCells: JSON.parse(document.querySelector('#audit-snapshot')?.textContent || 'null')?.state?.adventure?.visited?.length || 0,
    terrainRouteOverlay: document.querySelector('#world [data-terrain-route-overlay="future"]') ? {
      routeCount: new Set([...document.querySelectorAll('#world [data-terrain-route-overlay="future"] [data-route-index]')].map(node => node.getAttribute('data-route-index'))).size,
      layerCount: document.querySelectorAll('#world [data-terrain-route-overlay="future"] polyline').length,
    } : null,
  }));
  assert.equal(details.mountedTraveler, true, data.AGES[age].n + ' has one mounted traveler');
  report.ages[age].adventureScene = { ...scene, ...details };
  // The Future dwelling journey plans its own visible route on the selected world.

  report.screenshots.push(await captureScene('age-' + age + '-adventure', ['825x375', '1280x720']));
  // The Future age-specific dwelling journey below plans its own visible route for the selected world.

  await page.locator('[data-choice="nav:kingdom"]').first().click();
  await page.locator('#app[data-view="kingdom"]').waitFor({ state: 'attached', timeout: 10000 });
}


function assertNaturalResourceSettlement(before, after, label) {
  const elapsedMs = after.clock - before.clock;
  assert.ok(elapsedMs >= 0, label + ' follows the campaign clock');
  const income = rates(before);
  const deltas = {};
  for (const key of Object.keys(before.resources)) {
    const expected = income[key] * elapsedMs / 1000;
    const actual = after.resources[key] - before.resources[key];
    deltas[key] = { expected, actual };
    assert.ok(Math.abs(actual - expected) < 0.02, label + ' retains ' + key + ' apart from natural production');
  }
  return { elapsedMs, deltas };
}

async function visitAndClaimFutureDrone() {
  const initial = (await read()).state;
  assert.equal(initial.age, 7, 'the visible age gates naturally reach Future Age');
  assert.ok(dwellingPool(data, initial.age).includes('drone'), 'Drone is in the registered Future Age dwelling pool');
  await clickChoice('nav:adventure');
  await page.locator('#app[data-view="adventure"]').waitFor({ state: 'attached', timeout: 10000 });
  let state = (await read()).state;
  if (!state.adventure || state.adventure.atTown) {
    if (await page.locator('[data-choice="enter-adventure"]:visible').count()) await clickChoice('enter-adventure');
    state = await waitForState(value => value.age === 7 && value.adventure?.atTown === false, 'Future Adventure outside town');
  }
  assert.equal(state.age, 7);
  const world = worlds.find(row => row.id === state.adventureWorldId);
  assert.ok(world, 'the campaign uses its registered Adventure world');
  const geometry = adventureGeometryForWorld(contract.geometry.adventure, world, state.seed);
  const map = adventureMap(geometry);
  const site = geometry.sites.find(row => row.id === 'dwelling');
  assert.ok(site, 'the registered Future Adventure has a dwelling approach');
  assert.equal(state.adventure.pendingEncounter, null, 'there is no unresolved encounter before route travel');
  const route = routeTo(map, [state.adventure.x, state.adventure.y], site.approach);
  assert.equal(route.cells.some(cell => map.guards.has(cell.join(','))), false, 'the route avoids unresolved guard cells');
  report.futureDwellingRoute = {
    worldId: world.id,
    layoutId: geometry.layoutId,
    from: [state.adventure.x, state.adventure.y],
    to: site.approach,
    calculatedCost: route.cost,
    cells: route.cells,
    routeBasis: 'registered geometry and navigation rules used as read-only assertions; movement is committed one visible map step at a time',
  };

  const movesBefore = state.adventure.moves;
  while (state.adventure.x !== site.approach[0] || state.adventure.y !== site.approach[1]) {
    const live = (await read()).state;
    assert.equal(live.age, 7);
    assert.equal(live.adventure.pendingEncounter, null);
    const liveRoute = routeTo(map, [live.adventure.x, live.adventure.y], site.approach);
    const next = liveRoute.cells[0];
    const edge = routeTo(map, [live.adventure.x, live.adventure.y], next);
    if (live.adventure.moves < edge.cost) {
      const dayBefore = live.day;
      const movesBeforeDay = live.adventure.moves;
      await clickChoice('adventure-end-day');
      state = await waitForState(value => value.day > dayBefore && value.adventure?.moves > movesBeforeDay, 'natural Adventure day movement restoration');
      report.futureDwellingRoute.dayRestores = (report.futureDwellingRoute.dayRestores || 0) + 1;
      continue;
    }
    const beforeStep = live.adventure;
    const cell = page.locator('#world [data-adventure-cell="' + next.join(',') + '"]');
    assert.equal(await cell.count(), 1, 'each next road cell is rendered in the live Adventure world');
    await cell.click();
    await page.locator('#world [data-route-destination]').waitFor({ state: 'attached', timeout: 5000 });
    const preview = await page.evaluate(() => ({
      snapshot: window.rebornSnapshot(),
      cost: document.querySelector('[data-choice="confirm-route"]')?.title || '',
      destinations: document.querySelectorAll('#world [data-route-destination]').length,
    }));
    assert.equal(preview.destinations, 1, 'one visible destination is selected for each movement step');
    assert.deepEqual([preview.snapshot.adventure.x, preview.snapshot.adventure.y], [beforeStep.x, beforeStep.y], 'route preview leaves position unchanged');
    assert.equal(preview.snapshot.adventure.moves, beforeStep.moves, 'route preview leaves movement unchanged');
    const confirm = page.locator('[data-choice="confirm-route"]:visible').first();
    await confirm.waitFor({ state: 'visible', timeout: 5000 });
    assert.equal(await confirm.isDisabled(), false);
    await confirm.click();
    state = await waitForState(value => value.adventure?.x === next[0] && value.adventure?.y === next[1], 'confirmed visible Future route step');
    assert.equal(state.adventure.moves, beforeStep.moves - edge.cost, 'each confirmed step charges the navigation cost exactly once');
    assert.equal(state.adventure.pendingEncounter, null, 'the committed route step does not enter an encounter');
    report.futureDwellingRoute.steps = (report.futureDwellingRoute.steps || []);
    report.futureDwellingRoute.steps.push({
      from: [beforeStep.x, beforeStep.y],
      to: next,
      cost: edge.cost,
      movesBefore: beforeStep.moves,
      movesAfter: state.adventure.moves,
    });
  }

  assert.ok(state.adventure.visited.includes(site.approach.join(',')), 'natural travel discovers the dwelling approach');
  await page.waitForFunction(() => document.querySelector('#world')?.dataset.adventureTravelerMode === 'on-foot', null, { timeout: 5000 });
  assert.equal(await page.locator('#world [data-actor="knight"][data-adventure-travel-mode="on-foot"]').count(), 1, 'the existing Knight rig is shown on foot at the dwelling');
  assert.equal(await page.locator('#world [data-mount]').count(), 0, 'the mount is removed at the site interaction point');
  assert.equal(await page.locator('#world [data-site-id="dwelling"]').count(), 1, 'the registered dwelling art is visible');
  report.futureDwellingRoute.movesBefore = movesBefore;
  report.futureDwellingRoute.movesAfter = state.adventure.moves;

  const capture = async (name, width, height) => {
    await page.setViewportSize({ width, height });
    await page.waitForTimeout(120);
    const file = path.join(out, name + '-' + width + 'x' + height + '.png');
    await page.screenshot({ path: file });
    report.screenshots.push({ name, size: width + 'x' + height, file: path.relative(root, file) });
  };
  await capture('future-age-dwelling-on-foot', 825, 375);
  await capture('future-age-dwelling-on-foot', 1280, 720);
  await clickChoice('inspect:adventure');
  await page.locator('#panel.open').waitFor({ state: 'attached', timeout: 5000 });
  await capture('future-age-dwelling-context-panel', 825, 375);
  await capture('future-age-dwelling-context-panel', 1280, 720);

  const offerButton = page.locator('[data-choice="offer-dwelling:drone"]:visible').first();
  await offerButton.waitFor({ state: 'visible', timeout: 5000 });
  const beforeOffer = (await read()).state;
  assert.equal(beforeOffer.age, 7);
  const resourcesBeforeOffer = { ...beforeOffer.resources };
  await offerButton.click();
  const offered = await waitForState(value => value.dwelling?.type === 'drone' && value.dwelling.claimed === false, 'visible Future Age Drone offer');
  const offerElapsedMs = offered.clock - beforeOffer.clock;
  assert.ok(offerElapsedMs >= 0, 'the offer transaction follows the saved campaign clock');
  const offerIncome = rates(beforeOffer);
  const offerAccrual = {};
  for (const key of Object.keys(resourcesBeforeOffer)) {
    const natural = offerIncome[key] * offerElapsedMs / 1000;
    const actual = offered.resources[key] - resourcesBeforeOffer[key];
    offerAccrual[key] = { natural, actual };
    assert.ok(Math.abs(actual - natural) < 0.02, key + ' changes only by natural production while asking for the offer');
  }
  const payment = dwellingCost(data, offered.dwelling.type, offered.dwelling.multiplier);
  assert.deepEqual(dwellingCost(data, 'drone', offered.dwelling.multiplier), payment);
  report.futureDroneOffer = { terms: offered.dwelling, payment, resourcesBeforeOffer, resourcesAfterAsk: { ...offered.resources }, offerElapsedMs, offerAccrual };
  await clickChoice('back-dwelling');
  await page.locator('#panel.open').waitFor({ state: 'detached', timeout: 5000 });
  assert.deepEqual((await read()).state.dwelling, offered.dwelling, 'leaving the inspector preserves the fixed Drone terms');
  await clickChoice('inspect:adventure');
  await page.locator('#panel.open').waitFor({ state: 'attached', timeout: 5000 });
  assert.deepEqual((await read()).state.dwelling, offered.dwelling, 'reopening the site preserves the same Drone offer');
  await capture('future-age-drone-offer', 825, 375);

  await waitForResources(payment, 'natural Future Age Drone offer payment');
  const enough = (await read()).state;
  assert.ok(Object.entries(payment).every(([key, value]) => enough.resources[key] + 1e-6 >= value), 'natural production supplies the displayed offer price');
  await page.locator('#save').click();
  await page.waitForFunction(id => {
    const current = window.rebornSnapshot();
    const head = window.rebornCommittedHead();
    return current?.id === id && head?.campaignId === id && head.revision >= current.revision
      && document.querySelector('#save')?.dataset.saveState === 'committed';
  }, report.startCampaignId, { timeout: 15000 });
  await page.reload({ waitUntil: 'networkidle' });
  let afterReload = await read();
  if (afterReload?.view === 'home' && await page.locator('[data-choice="continue"]:visible').count()) {
    await clickChoice('continue');
    afterReload = await read();
  }
  if (afterReload?.view !== 'adventure') {
    await clickChoice('nav:adventure');
    if (await page.locator('[data-choice="enter-adventure"]:visible').count()) await clickChoice('enter-adventure');
    await page.locator('#app[data-view="adventure"]').waitFor({ state: 'attached', timeout: 10000 });
    afterReload = await read();
  }
  if (!await page.locator('#panel.open').count()) {
    await clickChoice('inspect:adventure');
    await page.locator('#panel.open').waitFor({ state: 'attached', timeout: 5000 });
  }
  assert.equal(afterReload.state.id, report.startCampaignId, 'offer reload preserves campaign identity');
  assert.equal(afterReload.state.age, 7, 'the save remains Future Age');
  assert.deepEqual(afterReload.state.dwelling, offered.dwelling, 'reload preserves the exact Drone offer');
  const naturalReloadAccrual = assertNaturalResourceSettlement(enough, afterReload.state, 'offer reload');
  report.futureDroneOffer.reloadBeforeClaim = { campaignId: afterReload.state.id, age: afterReload.state.age, dwelling: afterReload.state.dwelling, resources: afterReload.state.resources, naturalReloadAccrual };

  const beforeClaim = afterReload.state;
  const claimButton = page.locator('[data-choice="claim-dwelling"]:visible').first();
  await claimButton.waitFor({ state: 'visible', timeout: 5000 });
  assert.equal(await claimButton.isDisabled(), false, 'the Future Drone claim is enabled after natural production');
  await claimButton.click();
  state = await waitForState(value => value.dwelling?.claimed === true, 'claimed Future Drone offer');
  const claimElapsedMs = state.clock - beforeClaim.clock;
  assert.ok(claimElapsedMs >= 0, 'the claim transaction follows the saved campaign clock');
  const claimIncome = rates(beforeClaim);
  const claimAccrual = {};
  for (const key of Object.keys(beforeClaim.resources)) {
    const natural = claimIncome[key] * claimElapsedMs / 1000;
    const charged = payment[key] || 0;
    const expectedNetChange = natural - charged;
    const actualNetChange = state.resources[key] - beforeClaim.resources[key];
    claimAccrual[key] = { natural, charged, expectedNetChange, actualNetChange };
    assert.ok(Math.abs(actualNetChange - expectedNetChange) < 0.02, key + ' reflects exactly the offer charge plus campaign-clock production');
  }
  const drones = state.army.filter(stack => stack.kind === 'creature' && stack.type === 'drone');
  assert.equal(drones.length, 1, 'one drone stack is recruited');
  assert.equal(drones[0].count, offered.dwelling.count, 'the stack matches the visible offer count');
  assert.equal(state.dwellingHistory.filter(row => row.type === 'drone' && row.claimed).length, 1, 'history records one claimed Drone offer');
  report.futureDroneOffer.claim = { payment, claimElapsedMs, naturalAccrual: claimAccrual, stack: drones[0], resourcesBefore: beforeClaim.resources, resourcesAfter: state.resources, historyRows: state.dwellingHistory.filter(row => row.type === 'drone' && row.claimed).length };
  await page.waitForFunction(id => {
    const current = window.rebornSnapshot();
    const head = window.rebornCommittedHead();
    return current?.id === id && head?.campaignId === id && head.revision >= current.revision;
  }, report.startCampaignId, { timeout: 15000 });
  await page.reload({ waitUntil: 'networkidle' });
  await page.waitForFunction(id => {
    const current = window.rebornSnapshot();
    return current?.id === id && current.age === 7 && current.dwelling?.type === 'drone'
      && current.dwelling.claimed === true
      && current.army.some(stack => stack.kind === 'creature' && stack.type === 'drone' && stack.count === 5);
  }, report.startCampaignId, { timeout: 15000 });
  const reloaded = await page.evaluate(() => window.rebornSnapshot());
  const postClaimReloadAccrual = assertNaturalResourceSettlement(state, reloaded, 'post-claim reload');
  assert.equal(reloaded.army.filter(stack => stack.kind === 'creature' && stack.type === 'drone').length, 1, 'reload does not duplicate the Drone stack');
  report.reloadAfterClaim = { campaignId: reloaded.id, age: reloaded.age, dwelling: reloaded.dwelling, droneStacks: reloaded.army.filter(stack => stack.kind === 'creature' && stack.type === 'drone'), resources: reloaded.resources, naturalAccrual: postClaimReloadAccrual };
  if (await page.locator('[data-choice="continue"]:visible').count()) await clickChoice('continue');
  if (await page.evaluate(() => document.querySelector('#app')?.dataset.view) !== 'army') await clickChoice('nav:army');
  await page.locator('#app[data-view="army"]').waitFor({ state: 'attached', timeout: 10000 });
  const droneId = reloaded.army.find(stack => stack.kind === 'creature' && stack.type === 'drone').id;
  const droneCard = page.locator('[data-choice="roster:' + droneId + '"]').first();
  await droneCard.waitFor({ state: 'visible', timeout: 5000 });
  await droneCard.click();
  await page.waitForFunction(id => document.querySelector('[data-choice="roster:' + id + '"]')?.getAttribute('aria-pressed') === 'true', droneId, { timeout: 5000 });
  const droneRoster = await droneCard.evaluate(node => ({
    label: node.querySelector('.roster-unit-label')?.textContent?.trim() || '',
    accessibleName: node.getAttribute('aria-label') || '',
    selected: node.getAttribute('aria-pressed') === 'true',
    imageLoaded: Boolean(node.querySelector('img')?.complete && node.querySelector('img')?.naturalWidth > 0),
    viewport: { width: innerWidth, height: innerHeight },
    bounds: (() => { const r = node.getBoundingClientRect(); return { left: r.left, top: r.top, right: r.right, bottom: r.bottom }; })(),
  }));
  assert.match(droneRoster.label, /Drone/i, 'the selected Future Drone has a named roster card');
  assert.match(droneRoster.accessibleName, /Drone/i, 'the Army card exposes its accessible name');
  assert.equal(droneRoster.imageLoaded, true, 'the age-correct Drone roster artwork loads');
  assert.ok(droneRoster.bounds.left >= 0 && droneRoster.bounds.top >= 0 && droneRoster.bounds.right <= droneRoster.viewport.width && droneRoster.bounds.bottom <= droneRoster.viewport.height, 'Drone card fits in the desktop viewport');
  report.droneRoster = droneRoster;
  await capture('future-age-drone-army-roster', 1280, 720);
  await page.setViewportSize({ width: 825, height: 375 });
  await page.waitForTimeout(120);
  const compactDroneLabel = await droneCard.evaluate(node => {
    const label = node.querySelector('.roster-unit-label');
    const style = getComputedStyle(label);
    const range = document.createRange();
    range.selectNodeContents(label);
    const lines = [...range.getClientRects()].map(rect => ({ top: rect.top, bottom: rect.bottom }));
    const card = node.getBoundingClientRect();
    const bounds = label.getBoundingClientRect();
    return {
      text: label.textContent.trim(),
      whiteSpace: style.whiteSpace,
      textOverflow: style.textOverflow,
      lineCount: lines.length,
      labelBounds: { top: bounds.top, bottom: bounds.bottom },
      cardBounds: { top: card.top, bottom: card.bottom },
      lines,
    };
  });
  assert.equal(compactDroneLabel.text, 'Drone Swarm flyer ×5', 'the compact roster caption keeps its full unit name');
  assert.equal(compactDroneLabel.whiteSpace, 'normal', 'the compact roster caption can wrap');
  assert.equal(compactDroneLabel.textOverflow, 'clip', 'the compact roster caption no longer uses ellipsis');
  assert.ok(compactDroneLabel.lineCount >= 2, 'the full compact roster caption uses visible wrapped lines');
  assert.ok(compactDroneLabel.labelBounds.bottom <= compactDroneLabel.cardBounds.bottom, 'the wrapped caption stays inside its compact roster card');
  report.droneRoster.compactWrap = compactDroneLabel;
  await capture('future-age-drone-army-roster', 825, 375);
  return report.futureDroneOffer;
}

try {
  await page.goto(report.url, { waitUntil: 'networkidle' });
  await clickChoice('new-campaign');
  await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'campaignMapSelect');
  await clickChoice('campaign-world:grasslands');
  await clickChoice('begin-selected-world');
  await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'hero');
  await clickChoice('scene-class:knight');
  await clickChoice('scene-enter-valley');
  await waitForState(state => state.story.flags.enteredValley === true, 'fresh Stone campaign');
  await page.locator('#context').click();
  await clickChoice('site-list');
  await clickChoice('choose-site:townhall');
  await clickChoice('tutorial-toggle');
  await waitForState(state => state.tutorial.skipped === true, 'optional tutorial skipped');
  report.tutorialSkippedThroughVisibleControl = true;
  report.startClock = (await read()).state.clock;
  report.startCampaignId = (await read()).state.id;
  assert.equal((await read()).state.adventureWorldId, 'grasslands', 'the visible world-selection action starts the registered Grasslands world');
  report.selectedWorld = (await read()).state.adventureWorldId;
  report.screenshots.push(await captureScene('age-0-no-wall', ['825x375', '1280x720']));

  const producers = [
    ['P01', 'farm'],
    ['P02', 'lumber'],
    ['P03', 'quarry'],
    ['P04', 'mine'],
  ];
  for (const [siteId, building] of producers) await buildAt(siteId, building);
  report.producers = (await read()).state.plots.filter(plot => ['farm', 'lumber', 'quarry', 'mine'].includes(plot.type))
    .map(plot => ({ id: plot.id, type: plot.type, level: plot.level }));
  report.incomeRates = rates((await read()).state);
  report.screenshots.push(await captureScene('age-0-producers-no-wall', ['825x375', '1280x720']));

  report.ages[0] = { age: 0, name: data.AGES[0].n, wallPhases: [] };
  await buildHall(2);
  await clearInspector();
  await buildWall(1, 0);
  let currentScene = await sceneState();
  assert.equal(currentScene.wallPhase, 'built');
  assert.equal(currentScene.wallLevel, 1);
  assert.equal(currentScene.terrainStatus, 'kingdom-painting');
  assert.equal(currentScene.terrainLoaded, true);
  assert.equal(currentScene.wallStamps, 0);
  report.ages[0].wallPhases.push(currentScene);
  report.screenshots.push(await captureScene('age-0-built-wall', ['825x375', '1280x720']));
  await captureAdventureAge(0);

  for (let age = 0; age < 7; age += 1) {
    let state = (await read()).state;
    await buildHall(age + 2);
    await buildWall(age + 1, age);
    state = (await read()).state;
    const hallLevel = state.plots.find(plot => plot.id === 'townhall').level;
    assert.ok(hallLevel >= age + 2, data.AGES[age].n + ' has the required Hall level');
    await waitForResources(agePrice(age), 'legal ' + data.AGES[age].n + ' age advance');
    await clearInspector();
    await clickChoice('kingdom-actions-open');
    await clickChoice('age-advance');
    await page.locator('#build-commit').click();
    state = await waitForState(value => value.age === age + 1, 'advance to ' + data.AGES[age + 1].n);
    report.ages[age].advancedTo = data.AGES[age + 1].n;
    report.ages[age].balanceAfterPayment = { ...state.resources };
    const nextAge = age + 1;
    report.ages[nextAge] = { age: nextAge, name: data.AGES[nextAge].n, wallPhases: [] };
    const transitionedScene = await sceneState();
    assert.equal(transitionedScene.view, 'kingdom');
    assert.equal(transitionedScene.terrainLoaded, true);
    assert.equal(transitionedScene.wallLevel, age + 1);
    report.ages[nextAge].wallPhases.push(transitionedScene);
    report.screenshots.push(await captureScene('age-' + nextAge + '-entered', ['825x375', '1280x720']));
    await captureAdventureAge(nextAge);
  }


  let futureState = (await read()).state;
  assert.equal(futureState.age, 7, 'the seven visible age-gate journeys end in Future Age');
  await buildAt('P05', 'barracks');
  futureState = (await read()).state;
  assert.ok(futureState.plots.some(plot => plot.id === 'P05' && plot.type === 'barracks' && plot.level === 1), 'the Barracks is naturally built at P05');
  report.futureBarracks = { siteId: 'P05', type: 'barracks', level: 1, resources: { ...futureState.resources } };
  report.futureDroneOffer = await visitAndClaimFutureDrone();
  report.finalState = {
    age: (await read()).state.age,
    hallLevel: (await read()).state.plots.find(plot => plot.id === 'townhall').level,
    barracks: (await read()).state.plots.find(plot => plot.id === 'P05').type,
    droneCount: (await read()).state.army.filter(stack => stack.kind === 'creature' && stack.type === 'drone').reduce((sum, stack) => sum + stack.count, 0),
    elapsedControlledMs: (await read()).state.clock - report.startClock,
  };

} catch (error) {
  report.error = String(error);
} finally {
  report.errors = [...new Set(report.errors)];
  report.passed = !report.error
    && report.errors.length === 0
    && report.failedResponses.length === 0
    && report.ages.length === 8
    && report.ages.every(age => age && age.wallPhases.length >= 1)
    && report.finalState?.age === 7
    && report.finalState?.barracks === 'barracks'
    && report.finalState?.droneCount === 5
    && report.futureDroneOffer?.reloadBeforeClaim?.dwelling?.type === 'drone'
    && report.reloadAfterClaim?.dwelling?.claimed === true
    && report.reloadAfterClaim?.droneStacks?.length === 1;
  await fs.writeFile(path.join(out, 'adventure-age7-dwelling-natural-live-20261021.json'), JSON.stringify(report, null, 2));
  await context.close();
  await browser.close();
}
console.log(JSON.stringify({ passed: report.passed, error: report.error, ages: report.ages.map(age => ({ age: age.age, name: age.name, phases: age.wallPhases.map(phase => phase.wallPhase) })), rates: report.incomeRates, futureDwellingRoute: report.futureDwellingRoute, futureDroneOffer: report.futureDroneOffer, finalState: report.finalState, reloadAfterClaim: report.reloadAfterClaim, errors: report.errors, failedResponses: report.failedResponses, report: path.join(out, 'adventure-age7-dwelling-natural-live-20261021.json') }, null, 2));
if (!report.passed) process.exitCode = 1;
