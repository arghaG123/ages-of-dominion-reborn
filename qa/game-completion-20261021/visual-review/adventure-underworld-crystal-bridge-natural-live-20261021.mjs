import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import worlds from '../../../src/data/adventure-worlds.json' with { type: 'json' };
import contract from '../../../src/data/implementation-contract.json' with { type: 'json' };
import { adventureGeometryForWorld, adventureMap, routeTo } from '../../../src/core/navigation.js';

const root = process.cwd();
const out = path.join(root, 'qa/game-completion-20261021/visual-review/adventure-underworld-crystal-bridge-natural-live-20261021-run02');
const url = 'http://127.0.0.1:4179/?audit=1';
const westApproach = [5, 7];
const farBank = [8, 7];
await fs.mkdir(out, { recursive: true });
const report = {
  recordedAt: new Date().toISOString(),
  classification: 'NATURAL_UI_UNDERWORLD_FULL_CRYSTAL_BRIDGE_CROSSING_SAVE_RELOAD',
  journey: 'fresh visible campaign -> select Underworld -> travel to west bridge bank -> end day -> cross both bridge cells to far bank -> save and reload',
  note: 'All campaign and movement actions use visible UI event handlers. Imported geometry and read-only state snapshots are assertions only.',
  url,
  errors: [],
  failedResponses: [],
};
const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
const context = await browser.newContext({ viewport: { width: 825, height: 375 }, deviceScaleFactor: 1 });
const page = await context.newPage();
page.on('pageerror', error => report.errors.push(String(error)));
page.on('console', message => { if (message.type() === 'error') report.errors.push(message.text()); });
page.on('response', response => { if (response.status() >= 400) report.failedResponses.push({ status: response.status(), url: response.url() }); });

async function clickChoice(choice) {
  const control = page.locator(`[data-choice="${choice}"]:visible`).first();
  await control.waitFor({ state: 'visible', timeout: 10000 });
  assert.equal(await control.isDisabled(), false, `${choice} is enabled`);
  await control.click();
}

try {
  await page.goto(url, { waitUntil: 'networkidle' });
  await clickChoice('new-campaign');
  await clickChoice('campaign-world:underworld');
  await clickChoice('begin-selected-world');
  await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'hero');
  await clickChoice('scene-class:knight');
  await clickChoice('scene-enter-valley');
  await page.waitForFunction(() => window.rebornSnapshot()?.age === 0 && document.querySelector('#app')?.dataset.view === 'kingdom');
  report.campaignId = await page.evaluate(() => window.rebornSnapshot().id);
  await clickChoice('nav:adventure');
  await clickChoice('enter-adventure');
  await page.waitForFunction(() => window.rebornSnapshot()?.adventure?.atTown === false);
  await page.waitForFunction(() => {
    const image = document.querySelector('#terrain');
    return image?.complete && image.naturalWidth > 0;
  });

  const start = await page.evaluate(() => window.rebornSnapshot());
  assert.equal(start.adventureWorldId, 'underworld');
  const world = worlds.find(row => row.id === 'underworld');
  const geometry = adventureGeometryForWorld(contract.geometry.adventure, world, start.seed);
  const map = adventureMap(geometry);
  const expectedBlockers = [[6, 4], [6, 5], [6, 6], [6, 8]];
  assert.deepEqual(geometry.blocked, expectedBlockers);
  assert.deepEqual(geometry.obstacles, [[7, 6]]);
  const bridge = geometry.bridges[0];
  assert.deepEqual(bridge.cells, [[6, 7], [7, 7]]);
  assert.deepEqual(bridge.approaches, [[5, 7], [8, 7]]);

  const liveCells = await page.locator('#world [data-adventure-cell]').evaluateAll(nodes => Object.fromEntries(nodes.map(node => [
    node.getAttribute('data-adventure-cell'), node.getAttribute('data-open') === '1',
  ])));
  assert.equal(Object.keys(liveCells).length, 160);
  for (const [x, y] of [...expectedBlockers, ...geometry.obstacles]) assert.equal(liveCells[`${x},${y}`], false);
  for (const [x, y] of bridge.cells) assert.equal(liveCells[`${x},${y}`], true);

  const startCell = [start.adventure.x, start.adventure.y];
  const route = routeTo(map, startCell, westApproach);
  assert.ok(route.cost <= start.adventure.moves, 'the west bank is reachable in the current movement budget');
  const expectedCrossing = routeTo(map, westApproach, farBank);
  assert.ok(bridge.cells.every(([x, y]) => expectedCrossing.cells.some(cell => cell[0] === x && cell[1] === y)), 'the next-day route crosses both deck cells');
  assert.ok(expectedCrossing.cost <= start.adventure.moves, 'the movement allowance reaches the far bank after resting');
  report.map = { worldId: start.adventureWorldId, seed: start.seed, layoutId: geometry.layoutId, start: startCell, blockers: expectedBlockers, serpentObstacle: [7, 6], bridgeCells: bridge.cells, approaches: bridge.approaches };

  const targetCell = page.locator(`#world [data-adventure-cell="${westApproach.join(',')}"]`);
  await targetCell.dispatchEvent('click', { bubbles: true });
  await page.waitForFunction(() => Boolean(document.querySelector('#world [data-route-destination]')));
  const preview = await page.evaluate(() => ({
    destinations: document.querySelectorAll('#world [data-route-destination]').length,
    routePoints: document.querySelector('#world polyline')?.getAttribute('points') || '',
    state: window.rebornSnapshot().adventure,
  }));
  assert.equal(preview.destinations, 1);
  assert.deepEqual([preview.state.x, preview.state.y], startCell, 'preview does not move the hero');
  assert.equal(preview.state.moves, start.adventure.moves, 'preview does not spend movement');
  assert.equal(preview.routePoints.trim().split(/\s+/).length, route.cells.length + 1, 'the live overlay draws every path vertex through the deck');
  report.westApproachPreview = { target: westApproach, route: route.cells, cost: route.cost, movementUnchanged: true, routePoints: preview.routePoints };
  const previewCapture = path.join(out, 'underworld-crystal-bridge-west-bank-preview-825x375.png');
  await page.screenshot({ path: previewCapture });
  report.captures = [path.relative(root, previewCapture)];

  await clickChoice('confirm-route');
  await page.waitForFunction(([x, y]) => {
    const state = window.rebornSnapshot();
    return state?.adventure?.x === x && state?.adventure?.y === y;
  }, westApproach);
  const moved = await page.evaluate(() => window.rebornSnapshot());
  assert.equal(moved.adventure.moves, start.adventure.moves - route.cost);
  await page.waitForFunction(id => {
    const state = window.rebornSnapshot();
    const head = window.rebornCommittedHead();
    return state?.id === id && head?.campaignId === id && head.revision >= state.revision
      && document.querySelector('#save')?.dataset.saveState === 'committed';
  }, report.campaignId, { timeout: 15000 });
  report.movementSegments = [{ from: startCell, to: westApproach, route: route.cells, cost: route.cost, movesRemaining: moved.adventure.moves, visited: moved.adventure.visited, saveState: await page.locator('#save').getAttribute('data-save-state') }];

  await page.evaluate(() => new Promise((resolve, reject) => {
    let previous = '';
    let stable = 0;
    let frames = 0;
    const sample = () => {
      const marker = document.querySelector('#world [data-map-marker="traveler"]');
      if (!marker) return reject(new Error('traveler marker missing while waiting for natural movement animation'));
      const current = `${marker.getAttribute('cx')},${marker.getAttribute('cy')}`;
      stable = current === previous ? stable + 1 : 0;
      previous = current;
      frames += 1;
      if (stable >= 4) return resolve();
      if (frames > 240) return reject(new Error('traveler did not settle after the visible movement'));
      requestAnimationFrame(sample);
    };
    requestAnimationFrame(sample);
  }));
  const dayBeforeRest = moved.day;
  await clickChoice('inspect:adventure');
  await clickChoice('adventure-end-day');
  await page.waitForFunction(([day, dailyMoves]) => {
    const state = window.rebornSnapshot();
    return state?.day > day && state?.adventure?.moves >= dailyMoves;
  }, [dayBeforeRest, start.adventure.moves]);
  const rested = await page.evaluate(() => window.rebornSnapshot());
  report.movementSegments.push({ action: 'END_DAY', day: rested.day, movesRestored: rested.adventure.moves });
  await page.locator('#panel-close').click();

  const liveStart = await page.evaluate(() => window.rebornSnapshot());
  const liveFrom = [liveStart.adventure.x, liveStart.adventure.y];
  const crossing = routeTo(map, liveFrom, farBank);
  assert.deepEqual(liveFrom, westApproach);
  assert.ok(crossing.cells.length > 0);
  assert.ok(bridge.cells.every(([x, y]) => crossing.cells.some(cell => cell[0] === x && cell[1] === y)), 'live far-bank route crosses both deck cells');
  assert.ok(crossing.cost <= liveStart.adventure.moves, 'the live movement allowance reaches the far bank');
  const crossingTarget = page.locator(`#world [data-adventure-cell="${farBank.join(',')}"]`);
  await crossingTarget.click();
  await page.waitForFunction(() => Boolean(document.querySelector('#world [data-route-destination]')));
  const crossingPreview = await page.evaluate(() => ({
    state: window.rebornSnapshot().adventure,
    routePoints: document.querySelector('#world polyline')?.getAttribute('points') || '',
  }));
  assert.deepEqual([crossingPreview.state.x, crossingPreview.state.y], liveFrom, 'crossing preview leaves the traveler on the west bank');
  assert.equal(crossingPreview.state.moves, liveStart.adventure.moves, 'preview does not spend movement');
  assert.equal(crossingPreview.routePoints.trim().split(/\s+/).length, crossing.cells.length + 1, 'live overlay draws every crossing route vertex');
  report.crossingPreview = { from: liveFrom, target: farBank, route: crossing.cells, cost: crossing.cost, movementUnchanged: true, routePoints: crossingPreview.routePoints };
  const crossingCapture = path.join(out, 'underworld-crystal-bridge-full-crossing-preview-825x375.png');
  await page.screenshot({ path: crossingCapture });
  report.captures.push(path.relative(root, crossingCapture));

  await clickChoice('confirm-route');
  await page.waitForFunction(([x, y]) => {
    const state = window.rebornSnapshot();
    return state?.adventure?.x === x && state?.adventure?.y === y;
  }, farBank);
  await page.evaluate(() => new Promise((resolve, reject) => {
    let previous = '';
    let stable = 0;
    let frames = 0;
    const sample = () => {
      const marker = document.querySelector('#world [data-map-marker="traveler"]');
      if (!marker) return reject(new Error('traveler marker missing while waiting for bridge animation'));
      const current = `${marker.getAttribute('cx')},${marker.getAttribute('cy')}`;
      stable = current === previous ? stable + 1 : 0;
      previous = current;
      frames += 1;
      if (stable >= 4) return resolve();
      if (frames > 240) return reject(new Error('traveler did not settle after the bridge crossing'));
      requestAnimationFrame(sample);
    };
    requestAnimationFrame(sample);
  }));
  const crossed = await page.evaluate(() => window.rebornSnapshot());
  assert.equal(crossed.adventure.moves, liveStart.adventure.moves - crossing.cost);
  assert.ok(bridge.cells.every(([x, y]) => crossed.adventure.visited.includes(`${x},${y}`)), 'both bridge cells are discovered during the natural full crossing');
  await page.waitForFunction(id => {
    const state = window.rebornSnapshot();
    const head = window.rebornCommittedHead();
    return state?.id === id && head?.campaignId === id && head.revision >= state.revision
      && document.querySelector('#save')?.dataset.saveState === 'committed';
  }, report.campaignId, { timeout: 15000 });
  report.movementSegments.push({ from: liveFrom, to: farBank, route: crossing.cells, cost: crossing.cost, movesRemaining: crossed.adventure.moves, visitedBridgeCells: bridge.cells, saveState: await page.locator('#save').getAttribute('data-save-state') });
  const farBankCapture = path.join(out, 'underworld-crystal-bridge-far-bank-825x375.png');
  await page.screenshot({ path: farBankCapture });
  report.captures.push(path.relative(root, farBankCapture));

  await page.reload({ waitUntil: 'networkidle' });
  await page.waitForFunction(id => window.rebornSnapshot()?.id === id, report.campaignId, { timeout: 10000 });
  const afterReload = await page.evaluate(() => window.rebornSnapshot());
  assert.deepEqual([afterReload.adventure.x, afterReload.adventure.y], farBank);
  assert.deepEqual(afterReload.adventure.visited, crossed.adventure.visited);
  assert.ok(bridge.cells.every(([x, y]) => afterReload.adventure.visited.includes(`${x},${y}`)), 'bridge discovery survives reload');
  report.reload = { position: [afterReload.adventure.x, afterReload.adventure.y], moves: afterReload.adventure.moves, visited: afterReload.adventure.visited };
  assert.deepEqual(report.errors, []);
  assert.deepEqual(report.failedResponses, []);
  report.result = 'PASS_BOUNDED_NATURAL_UNDERWORLD_FULL_BRIDGE_CROSSING_FAR_BANK_SAVE_RELOAD; NOT_FULL_WORLD_OR_MOCK_ACCEPTANCE';
} catch (error) {
  report.result = 'FAIL';
  report.error = String(error?.stack || error);
  throw error;
} finally {
  await fs.writeFile(path.join(out, 'report.json'), JSON.stringify(report, null, 2));
  await browser.close();
}
