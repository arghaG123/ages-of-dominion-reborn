import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import worlds from '../../../src/data/adventure-worlds.json' with { type: 'json' };
import contract from '../../../src/data/implementation-contract.json' with { type: 'json' };
import { adventureGeometryForWorld, adventureMap, routeTo } from '../../../src/core/navigation.js';

const root = process.cwd();
const out = path.join(root, 'qa/game-completion-20261021/visual-review/adventure-grasslands-west-bridge-full-crossing-natural-live-20261021-run03');
const url = 'http://127.0.0.1:4179/?audit=1';
const approach = [6, 5];
const farBank = [4, 3];
await fs.mkdir(out, { recursive: true });
const report = {
  recordedAt: new Date().toISOString(),
  classification: 'NATURAL_UI_GRASSLANDS_WEST_MILL_BRIDGE_FULL_CROSSING_SAVE_RELOAD',
  journey: 'fresh visible Grasslands campaign -> reach east approach -> end day -> cross both west mill deck cells -> save and reload on west bank',
  note: 'All campaign and movement actions use visible UI controls. Geometry and read-only snapshots are assertions only; no state or position is injected.',
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

async function waitForTravelerAtCell(cell, label) {
  return page.evaluate(({ cell, label }) => new Promise((resolve, reject) => {
    const cellNode = document.querySelector(`#world [data-adventure-cell="${cell.join(',')}"]`);
    const values = cellNode?.getAttribute('points')?.match(/-?\d+(?:\.\d+)?/g)?.map(Number) || [];
    if (!cellNode || values.length < 6) return reject(new Error(`registered cell geometry missing for ${label}`));
    const points = [];
    for (let index = 0; index < values.length; index += 2) points.push([values[index], values[index + 1]]);
    const expected = [
      points.reduce((sum, point) => sum + point[0], 0) / points.length,
      points.reduce((sum, point) => sum + point[1], 0) / points.length - 8,
    ];
    let stable = 0;
    let frames = 0;
    let last = null;
    const sample = () => {
      const marker = document.querySelector('#world [data-map-marker="traveler"]');
      if (!marker) return reject(new Error(`traveler marker missing while waiting for ${label}`));
      const world = document.querySelector('#world');
      const mount = document.querySelector('#world [data-mount="horse"]');
      const mode = world?.getAttribute('data-adventure-traveler-mode');
      const moving = mode === 'mounted' && mount?.getAttribute('data-moving') === '1';
      const current = [Number(marker.getAttribute('cx')), Number(marker.getAttribute('cy'))];
      last = { current, expected, mode, moving };
      const onExpectedCell = Math.abs(current[0] - expected[0]) < 2.5 && Math.abs(current[1] - expected[1]) < 2.5;
      stable = onExpectedCell && !moving ? stable + 1 : 0;
      frames += 1;
      if (stable >= 4) return resolve({ cell, frames, marker: current, expected, mode });
      if (frames > 360) return reject(new Error(`traveler did not reach the registered cell after ${label}: ${JSON.stringify(last)}`));
      requestAnimationFrame(sample);
    };
    requestAnimationFrame(sample);
  }), { cell, label });
}

async function saveIsCommitted(campaignId) {
  await page.waitForFunction(id => {
    const state = window.rebornSnapshot();
    const head = window.rebornCommittedHead();
    return state?.id === id && head?.campaignId === id && head.revision >= state.revision
      && document.querySelector('#save')?.dataset.saveState === 'committed';
  }, campaignId, { timeout: 15000 });
}

try {
  await page.goto(url, { waitUntil: 'networkidle' });
  await clickChoice('new-campaign');
  await clickChoice('campaign-world:grasslands');
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
  assert.equal(start.adventureWorldId, 'grasslands');
  const world = worlds.find(row => row.id === 'grasslands');
  const geometry = adventureGeometryForWorld(contract.geometry.adventure, world, start.seed);
  const map = adventureMap(geometry);
  const bridge = geometry.bridges.find(row => row.id === 'grasslands-west-mill-crossing');
  assert.ok(bridge);
  assert.deepEqual(bridge.cells, [[4, 4], [5, 4]]);
  assert.ok(bridge.approaches.some(cell => cell[0] === farBank[0] && cell[1] === farBank[1]));
  assert.ok(bridge.approaches.some(cell => cell[0] === approach[0] && cell[1] === approach[1]));
  assert.equal(map.blocked.has('3,3'), true, 'the old recorded approach is blocked by the Mill footprint');
  assert.equal(map.blocked.has(farBank.join(',')), false, 'the corrected west bank is open');
  assert.equal(map.blocked.has(approach.join(',')), false, 'the east bank is open');
  assert.ok(bridge.cells.every(([x, y]) => !map.blocked.has(`${x},${y}`)));

  const liveCells = await page.locator('#world [data-adventure-cell]').evaluateAll(nodes => Object.fromEntries(nodes.map(node => [
    node.getAttribute('data-adventure-cell'), node.getAttribute('data-open') === '1',
  ])));
  assert.equal(Object.keys(liveCells).length, 160);
  const deckKeys = new Set(geometry.bridges.flatMap(row => row.cells.map(([x, y]) => `${x},${y}`)));
  for (const [x, y] of geometry.blocked) {
    const key = `${x},${y}`;
    assert.equal(liveCells[key], deckKeys.has(key), `live water cell ${key} is blocked unless it is a registered deck`);
  }
  for (const [x, y] of bridge.cells) assert.equal(liveCells[`${x},${y}`], true, `live deck cell ${x},${y} is walkable`);
  report.map = { worldId: start.adventureWorldId, seed: start.seed, layoutId: geometry.layoutId, start: [start.adventure.x, start.adventure.y], blockedCells: geometry.blocked.length, oldApproach: [3, 3], correctedApproaches: [farBank, approach], bridge: { id: bridge.id, cells: bridge.cells, approaches: bridge.approaches }, renderedCells: Object.keys(liveCells).length };

  const startPosition = [start.adventure.x, start.adventure.y];
  const routeToApproach = routeTo(map, startPosition, approach);
  assert.ok(routeToApproach.cost <= start.adventure.moves, 'the east bridge bank is reachable today');
  const approachCell = page.locator(`#world [data-adventure-cell="${approach.join(',')}"]`);
  await approachCell.dispatchEvent('click', { bubbles: true });
  await page.waitForFunction(() => Boolean(document.querySelector('#world [data-route-destination]')));
  const approachPreview = await page.evaluate(() => window.rebornSnapshot().adventure);
  assert.deepEqual([approachPreview.x, approachPreview.y], startPosition);
  assert.equal(approachPreview.moves, start.adventure.moves);
  const approachPreviewPath = path.join(out, 'grasslands-west-bridge-east-bank-preview-825x375.png');
  await page.screenshot({ path: approachPreviewPath });
  await clickChoice('confirm-route');
  await page.waitForFunction(([x, y]) => {
    const state = window.rebornSnapshot();
    return state?.adventure?.x === x && state?.adventure?.y === y;
  }, approach);
  report.approachArrival = await waitForTravelerAtCell(approach, 'approach travel');
  const atApproach = await page.evaluate(() => window.rebornSnapshot());
  assert.deepEqual([atApproach.adventure.x, atApproach.adventure.y], approach);
  await saveIsCommitted(report.campaignId);
  report.approachTravel = { from: startPosition, to: approach, path: routeToApproach.cells, cost: routeToApproach.cost, movesRemaining: atApproach.adventure.moves };
  const approachCapture = path.join(out, 'grasslands-west-bridge-east-bank-arrival-825x375.png');
  await page.screenshot({ path: approachCapture });
  report.captures = [path.relative(root, approachPreviewPath), path.relative(root, approachCapture)];

  const beforeRestDay = atApproach.day;
  await clickChoice('inspect:adventure');
  await clickChoice('adventure-end-day');
  await page.waitForFunction(([day, dailyMoves]) => {
    const state = window.rebornSnapshot();
    return state?.day > day && state?.adventure?.moves >= dailyMoves;
  }, [beforeRestDay, start.adventure.moves]);
  const rested = await page.evaluate(() => window.rebornSnapshot());
  report.rest = { day: rested.day, movesRestored: rested.adventure.moves };
  await page.locator('#panel-close').click();

  const beforeCrossing = await page.evaluate(() => window.rebornSnapshot());
  const crossingStart = [beforeCrossing.adventure.x, beforeCrossing.adventure.y];
  assert.deepEqual(crossingStart, approach);
  const crossing = routeTo(map, crossingStart, farBank);
  assert.ok(bridge.cells.every(([x, y]) => crossing.cells.some(cell => cell[0] === x && cell[1] === y)), 'the actual bank-to-bank route crosses both deck cells');
  assert.ok(crossing.cost <= beforeCrossing.adventure.moves, 'the far bank is reachable after resting');
  const farBankCell = page.locator(`#world [data-adventure-cell="${farBank.join(',')}"]`);
  await farBankCell.dispatchEvent('click', { bubbles: true });
  await page.waitForFunction(() => Boolean(document.querySelector('#world [data-route-destination]')));
  const crossingPreview = await page.evaluate(() => window.rebornSnapshot().adventure);
  assert.deepEqual([crossingPreview.x, crossingPreview.y], crossingStart, 'preview stays on the east bank');
  assert.equal(crossingPreview.moves, beforeCrossing.adventure.moves, 'preview does not spend movement');
  const crossingPreviewPath = path.join(out, 'grasslands-west-mill-bridge-full-crossing-preview-825x375.png');
  await page.screenshot({ path: crossingPreviewPath });
  report.crossingPreview = { from: crossingStart, to: farBank, path: crossing.cells, cost: crossing.cost, deckCells: bridge.cells };
  await clickChoice('confirm-route');
  await page.waitForFunction(([x, y]) => {
    const state = window.rebornSnapshot();
    return state?.adventure?.x === x && state?.adventure?.y === y;
  }, farBank);
  report.farBankArrival = await waitForTravelerAtCell(farBank, 'west bridge crossing');
  const crossed = await page.evaluate(() => window.rebornSnapshot());
  assert.ok(bridge.cells.every(([x, y]) => crossed.adventure.visited.includes(`${x},${y}`)), 'both west bridge cells are discovered');
  await saveIsCommitted(report.campaignId);
  report.crossing = { from: crossingStart, to: farBank, path: crossing.cells, cost: crossing.cost, movesRemaining: crossed.adventure.moves, visited: crossed.adventure.visited, saveState: await page.locator('#save').getAttribute('data-save-state') };
  const crossedCapture = path.join(out, 'grasslands-west-bridge-far-bank-825x375.png');
  await page.screenshot({ path: crossedCapture });
  report.captures.push(path.relative(root, crossingPreviewPath), path.relative(root, crossedCapture));

  await page.reload({ waitUntil: 'networkidle' });
  await page.waitForFunction(id => window.rebornSnapshot()?.id === id, report.campaignId, { timeout: 10000 });
  const reloaded = await page.evaluate(() => window.rebornSnapshot());
  assert.deepEqual([reloaded.adventure.x, reloaded.adventure.y], farBank);
  assert.deepEqual(reloaded.adventure.visited, crossed.adventure.visited);
  assert.deepEqual(report.errors, []);
  assert.deepEqual(report.failedResponses, []);
  report.reload = { position: [reloaded.adventure.x, reloaded.adventure.y], day: reloaded.day, moves: reloaded.adventure.moves, visitedBridgeCells: bridge.cells };
  report.result = 'PASS_BOUNDED_NATURAL_GRASSLANDS_WEST_MILL_BRIDGE_FULL_CROSSING_SAVE_RELOAD; NOT_FULL_WORLD_OR_MOCK_ACCEPTANCE';
} catch (error) {
  report.result = 'FAIL';
  report.error = String(error?.stack || error);
  throw error;
} finally {
  await fs.writeFile(path.join(out, 'report.json'), JSON.stringify(report, null, 2));
  await browser.close();
}
