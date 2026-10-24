import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import data from '../../../src/data/reference-data.json' with { type: 'json' };
import adventureWorlds from '../../../src/data/adventure-worlds.json' with { type: 'json' };
import { cost, rates } from '../../../src/core/campaign.js';
import { agePrice } from '../../../src/core/rules.js';

const root = process.cwd();
const adventureWorld = adventureWorlds.find(world => world.id === 'astral-peaks');
assert.ok(adventureWorld && adventureWorld.runtimeFile === adventureWorld.file, 'Astral Cloudpeaks uses its approved owner painting');
const out = path.join(root, 'qa/game-completion-20261022/visual-review/natural-all-age-kingdom-live-run02');
await fs.mkdir(out, { recursive: true });
const report = {
  recordedAt: new Date().toISOString(),
  classification: 'NATURAL_UI_CAMPAIGN_CONTROLLED_BROWSER_CLOCK',
  journey: 'new campaign -> select Astral Cloudpeaks -> skip the optional tutorial -> build four income sites -> upgrade Hall and walls -> pay each legal age gate -> capture every age in Kingdom and Adventure -> traverse all four cells of the north-west Astral viaduct across age transitions -> save/reload Future',
  url: 'http://127.0.0.1:4179/?audit=1',
  world: { id: adventureWorld.id, title: adventureWorld.title, file: adventureWorld.file, runtimeFile: adventureWorld.runtimeFile },
  note: 'All construction, age advancement, map entry, route, and save actions use visible game controls. Playwright fast-forwards only idle elapsed time to verify legal production and construction; no campaign state or resources are injected. The supplied Astral painting is expected to remain the registered world scene through all eight ages.',
  errors: [],
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
    worldId: document.querySelector('#world')?.getAttribute('data-adventure-world-id'),
    registeredBridgeCount: Number(document.querySelector('#world')?.getAttribute('data-adventure-bridge-count')),
    playableCrossingCount: Number(document.querySelector('#world')?.getAttribute('data-adventure-playable-crossings')),
    mountedTraveler: document.querySelectorAll('#world [data-mount]').length === 1,
    visibleSites: document.querySelectorAll('#world .adventure-site').length,
    visitedCells: JSON.parse(document.querySelector('#audit-snapshot')?.textContent || 'null')?.state?.adventure?.visited?.length || 0,
    terrainRouteOverlay: document.querySelector('#world [data-terrain-route-overlay="gunpowder"]') ? {
      routeCount: new Set([...document.querySelectorAll('#world [data-terrain-route-overlay="gunpowder"] [data-route-index]')].map(node => node.getAttribute('data-route-index'))).size,
      layerCount: document.querySelectorAll('#world [data-terrain-route-overlay="gunpowder"] polyline').length,
    } : null,
  }));
  assert.equal(details.mountedTraveler, true, data.AGES[age].n + ' has one mounted traveler');
  assert.equal(details.worldId, adventureWorld.id, data.AGES[age].n + ' retains the selected Astral Cloudpeaks world');
  assert.equal(details.registeredBridgeCount, 4, data.AGES[age].n + ' renders the four registered Astral bridges');
  assert.equal(details.playableCrossingCount, 4, data.AGES[age].n + ' exposes four playable Astral crossings');
  assert.equal(scene.terrain, adventureWorld.runtimeFile, data.AGES[age].n + ' uses the supplied Astral painting');
  report.ages[age].adventureScene = { ...scene, ...details };
  report.screenshots.push(await captureScene('age-' + age + '-adventure', ['825x375', '1280x720']));
  const deckStepByAge = new Map([[2, [5, 3]], [4, [6, 3]], [6, [7, 3]], [7, [8, 3]]]);
  const deckStep = deckStepByAge.get(age);
  if (deckStep) {
    const [x, y] = deckStep;
    const deckCell = page.locator(`#world [data-adventure-cell="${x},${y}"]`);
    assert.equal(await deckCell.count(), 1, `Astral viaduct cell ${x},${y} is present at age ${age}`);
    await deckCell.click();
    await page.waitForTimeout(80);
    assert.equal(await page.locator('#world [data-route-destination]').count(), 1, `Astral route preview reaches ${x},${y}`);
    const confirm = page.locator('[data-choice="confirm-route"]').first();
    await confirm.waitFor({ state: 'visible', timeout: 10000 });
    assert.equal(await confirm.isDisabled(), false, `Astral viaduct step ${x},${y} can be confirmed`);
    await confirm.click();
    state = await waitForState(value => value.age === age && value.adventure?.x === x && value.adventure?.y === y, `confirmed Astral viaduct step ${x},${y}`);
    report.ages[age].adventureRoute = { destination: `${x},${y}`, afterMove: state.adventure };
    if (age === 7) {
      const visited = new Set(state.adventure.visited.map(cell => Array.isArray(cell) ? cell.join(',') : cell));
      for (const deckX of [5, 6, 7, 8]) assert.ok(visited.has(`${deckX},3`), `the four-cell Astral north viaduct is visited through ${deckX},3`);
      report.northViaductComplete = true;
    }
    report.screenshots.push(await captureScene(`age-${age}-astral-viaduct-step`, ['825x375', '1280x720']));
  }
  await page.locator('[data-choice="nav:kingdom"]').first().click();
  await page.locator('#app[data-view="kingdom"]').waitFor({ state: 'attached', timeout: 10000 });
}

try {
  await page.goto(report.url, { waitUntil: 'networkidle' });
  await clickChoice('new-campaign');
  await clickChoice('campaign-world:astral-peaks');
  await clickChoice('begin-selected-world');
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

  await buildWall(8, 7);
  const finalScene = await sceneState();
  assert.equal(finalScene.wallPhase, 'tall');
  assert.equal(finalScene.wallLevel, 8);
  assert.equal(finalScene.terrainLoaded, true);
  report.ages[7].wallPhases.push(finalScene);
  report.screenshots.push(await captureScene('age-7-future-wall-tall', ['825x375', '1280x720']));
  report.finalState = {
    age: (await read()).state.age,
    hallLevel: (await read()).state.plots.find(plot => plot.id === 'townhall').level,
    wallLevel: (await read()).state.walls.level,
    resources: { ...(await read()).state.resources },
    elapsedControlledMs: (await read()).state.clock - report.startClock,
  };

  await page.locator('#save').click();
  await page.waitForTimeout(100);
  await page.reload({ waitUntil: 'networkidle' });
  let snapshot = await read();
  if (snapshot?.view === 'home' && await page.locator('[data-choice="continue"]').isVisible()) await clickChoice('continue');
  const reloaded = await waitForState(state => state.age === 7 && state.walls.level === 8, 'Future wall state after reload');
  report.reload = {
    age: reloaded.age,
    wallLevel: reloaded.walls.level,
    hallLevel: reloaded.plots.find(plot => plot.id === 'townhall').level,
    stateId: reloaded.id,
  };
  assert.equal(report.reload.age, 7);
  assert.equal(report.reload.wallLevel, 8);
} catch (error) {
  report.error = String(error);
} finally {
  report.errors = [...new Set(report.errors)];
  report.passed = !report.error
    && report.errors.length === 0
    && report.ages.length === 8
    && report.ages.every(age => age && age.wallPhases.length >= 1)
    && report.northViaductComplete === true
    && report.finalState?.age === 7
    && report.reload?.age === 7
    && report.reload?.wallLevel === 8;
  await fs.writeFile(path.join(out, 'report.json'), JSON.stringify(report, null, 2));
  await context.close();
  await browser.close();
}
console.log(JSON.stringify({ passed: report.passed, error: report.error, ages: report.ages.map(age => ({ age: age.age, name: age.name, phases: age.wallPhases.map(phase => phase.wallPhase) })), rates: report.incomeRates, finalState: report.finalState, reload: report.reload, errors: report.errors, report: path.join(out, 'report.json') }, null, 2));
if (!report.passed) process.exitCode = 1;
