import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import worlds from '../../../src/data/adventure-worlds.json' with { type: 'json' };
import contract from '../../../src/data/implementation-contract.json' with { type: 'json' };
import { adventureGeometryForWorld, adventureMap, routeTo, stepCost } from '../../../src/core/navigation.js';

const root = process.cwd();
const out = path.join(root, 'qa/game-completion-20261021/visual-review/adventure-feywild-footbridge-natural-live-20261021-run04');
const url = 'http://127.0.0.1:4179/?audit=1';
const target = [1, 6];
const expectedWater = [[3, 5], [10, 4], [11, 4], [11, 6], [12, 6], [1, 7], [0, 8], [10, 9], [11, 9]];
await fs.mkdir(out, { recursive: true });
const report = {
  recordedAt: new Date().toISOString(),
  classification: 'NATURAL_UI_FEYWILD_FOOTBRIDGE_CROSSING_SAVE_RELOAD',
  journey: 'fresh visible campaign -> Feywild -> route from east to west bank through the footbridge -> save and reload',
  note: 'Campaign and all movement use visible UI controls. Read-only state, geometry, and path calculations are assertions only; no campaign state or position is injected.',
  url,
  errors: [],
  failedResponses: [],
  movementSegments: [],
  captures: [],
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

function furthestAffordable(map, from, route, budget) {
  let cost = 0;
  let previous = from;
  let destination = from;
  for (const cell of route.cells) {
    const step = stepCost(map, previous, cell);
    if (cost + step > budget) break;
    cost += step;
    destination = cell;
    previous = cell;
  }
  assert.notDeepEqual(destination, from, 'at least one legal movement step fits today');
  return { destination, cost };
}

try {
  await page.goto(url, { waitUntil: 'networkidle' });
  await clickChoice('new-campaign');
  await clickChoice('campaign-world:feywild');
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

  const initial = await page.evaluate(() => window.rebornSnapshot());
  assert.equal(initial.adventureWorldId, 'feywild');
  const world = worlds.find(row => row.id === 'feywild');
  const geometry = adventureGeometryForWorld(contract.geometry.adventure, world, initial.seed);
  const map = adventureMap(geometry);
  const bridge = geometry.bridges.find(row => row.id === 'feywild-waterfall-footbridge-2-6');
  assert.ok(bridge);
  assert.deepEqual(geometry.blocked, expectedWater);
  const liveCells = await page.locator('#world [data-adventure-cell]').evaluateAll(nodes => Object.fromEntries(nodes.map(node => [
    node.getAttribute('data-adventure-cell'), node.getAttribute('data-open') === '1',
  ])));
  assert.equal(Object.keys(liveCells).length, 160);
  for (const [x, y] of expectedWater) assert.equal(liveCells[`${x},${y}`], false, `live cell ${x},${y} is blocked water`);
  for (const [x, y] of bridge.cells) assert.equal(liveCells[`${x},${y}`], true, `bridge deck ${x},${y} is walkable`);
  report.map = {
    worldId: 'feywild',
    seed: initial.seed,
    layoutId: geometry.layoutId,
    start: [initial.adventure.x, initial.adventure.y],
    blockers: expectedWater,
    bridge: { id: bridge.id, cells: bridge.cells, approaches: bridge.approaches },
    renderedCells: Object.keys(liveCells).length,
  };

  let state = initial;
  for (let segment = 0; segment < 4; segment += 1) {
    const from = [state.adventure.x, state.adventure.y];
    if (from[0] === target[0] && from[1] === target[1]) break;
    const route = routeTo(map, from, target);
    const move = route.cost <= state.adventure.moves
      ? { destination: target, cost: route.cost }
      : furthestAffordable(map, from, route, state.adventure.moves);
    const targetControl = page.locator(`#world [data-adventure-cell="${move.destination.join(',')}"]`);
    await targetControl.click();
    await page.waitForFunction(() => Boolean(document.querySelector('#world [data-route-destination]')));
    const preview = await page.evaluate(() => window.rebornSnapshot());
    assert.deepEqual([preview.adventure.x, preview.adventure.y], from, 'preview does not move the hero');
    assert.equal(preview.adventure.moves, state.adventure.moves, 'preview does not spend movement');
    if (move.destination[0] === target[0] && move.destination[1] === target[1]) {
      const previewCapture = path.join(out, 'feywild-footbridge-crossing-route-preview-825x375.png');
      await page.screenshot({ path: previewCapture });
      report.captures.push(path.relative(root, previewCapture));
      report.crossingPreview = { from, to: target, path: routeTo(map, from, target).cells, cost: move.cost };
    }
    await clickChoice('confirm-route');
    await page.waitForFunction(([x, y]) => {
      const current = window.rebornSnapshot();
      return current?.adventure?.x === x && current?.adventure?.y === y;
    }, move.destination);
    state = await page.evaluate(() => window.rebornSnapshot());
    assert.equal(state.adventure.moves, preview.adventure.moves - move.cost);
    await page.waitForFunction(id => {
      const current = window.rebornSnapshot();
      const head = window.rebornCommittedHead();
      return current?.id === id && head?.campaignId === id && head.revision >= current.revision
        && document.querySelector('#save')?.dataset.saveState === 'committed';
    }, report.campaignId, { timeout: 15000 });
    report.movementSegments.push({ from, to: move.destination, path: routeTo(map, from, move.destination).cells, cost: move.cost, movesRemaining: state.adventure.moves, saveState: await page.locator('#save').getAttribute('data-save-state') });

    if (state.adventure.x === target[0] && state.adventure.y === target[1]) break;
    if (state.adventure.moves === 0) {
      const priorDay = state.day;
      await clickChoice('adventure-end-day');
      await page.waitForFunction(day => {
        const current = window.rebornSnapshot();
        return current?.day > day && current.adventure.moves > 0;
      }, priorDay);
      state = await page.evaluate(() => window.rebornSnapshot());
    }
  }

  state = await page.evaluate(() => window.rebornSnapshot());
  assert.deepEqual([state.adventure.x, state.adventure.y], target, 'the visible journey reaches the west bank');
  for (const [x, y] of bridge.cells) assert.ok(state.adventure.visited.includes(`${x},${y}`), `travel discovers bridge cell ${x},${y}`);
  const fullRoute = routeTo(map, [initial.adventure.x, initial.adventure.y], target);
  assert.ok(bridge.cells.every(([x, y]) => fullRoute.cells.some(cell => cell[0] === x && cell[1] === y)));
  const capture = path.join(out, 'feywild-footbridge-far-bank-825x375.png');
  await page.screenshot({ path: capture });
  report.fullRoute = { destination: target, route: fullRoute.cells, cost: fullRoute.cost, bridgeCells: bridge.cells };
  report.captures.push(path.relative(root, capture));

  await page.reload({ waitUntil: 'networkidle' });
  await page.waitForFunction(id => window.rebornSnapshot()?.id === id, report.campaignId, { timeout: 10000 });
  const reloaded = await page.evaluate(() => window.rebornSnapshot());
  assert.deepEqual([reloaded.adventure.x, reloaded.adventure.y], target);
  for (const [x, y] of bridge.cells) assert.ok(reloaded.adventure.visited.includes(`${x},${y}`));
  report.reload = { position: [reloaded.adventure.x, reloaded.adventure.y], day: reloaded.day, moves: reloaded.adventure.moves, visited: reloaded.adventure.visited };
  assert.deepEqual(report.errors, []);
  assert.deepEqual(report.failedResponses, []);
  report.result = 'PASS_BOUNDED_NATURAL_FEYWILD_FOOTBRIDGE_CROSSING_SAVE_RELOAD; NOT_FULL_WORLD_OR_MOCK_ACCEPTANCE';
} catch (error) {
  report.result = 'FAIL';
  report.error = String(error?.stack || error);
  throw error;
} finally {
  await fs.writeFile(path.join(out, 'report.json'), JSON.stringify(report, null, 2));
  await browser.close();
}
