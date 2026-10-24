import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import worlds from '../../../src/data/adventure-worlds.json' with { type: 'json' };
import contract from '../../../src/data/implementation-contract.json' with { type: 'json' };
import { adventureGeometryForWorld, adventureMap, routeTo } from '../../../src/core/navigation.js';

const root = process.cwd();
const worldId = 'haunted-marsh';
const expectedBlockers = [[5, 2], [6, 2], [7, 2]];
const out = path.join(root, 'qa/game-completion-20261021/visual-review/adventure-haunted-marsh-water-mask-natural-live-20261021-run01');
const url = 'http://127.0.0.1:4179/?audit=1';
await fs.mkdir(out, { recursive: true });
const report = {
  recordedAt: new Date().toISOString(),
  classification: 'NATURAL_UI_HAUNTED_MARSH_MAP_LOAD_MOVE_SAVE_RELOAD',
  journey: 'fresh visible campaign -> select Haunted Marsh -> enter Adventure -> inspect registered bog-pool blockers -> commit a legal adjacent step -> save and reload',
  note: 'All campaign and movement actions use visible controls. Imported map geometry and read-only snapshots are assertions only.',
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
  await clickChoice(`campaign-world:${worldId}`);
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
  const world = worlds.find(row => row.id === worldId);
  assert.equal(start.adventureWorldId, worldId);
  const geometry = adventureGeometryForWorld(contract.geometry.adventure, world, start.seed);
  const map = adventureMap(geometry);
  assert.deepEqual(geometry.blocked, expectedBlockers);
  const liveCells = await page.locator('#world [data-adventure-cell]').evaluateAll(nodes => nodes.map(node => ({
    cell: node.getAttribute('data-adventure-cell'),
    open: node.getAttribute('data-open') === '1',
  })));
  assert.equal(liveCells.length, 160, 'the live map renders its complete 16-by-10 navigation grid');
  const liveByCell = new Map(liveCells.map(row => [row.cell, row.open]));
  for (const [x, y] of expectedBlockers) {
    assert.equal(map.blocked.has(`${x},${y}`), true);
    assert.equal(liveByCell.get(`${x},${y}`), false, `live renderer marks bog-pool cell ${x},${y} non-walkable`);
  }
  report.map = {
    worldId,
    seed: start.seed,
    layoutId: geometry.layoutId,
    start: [start.adventure.x, start.adventure.y],
    blockers: expectedBlockers,
    blockedInLiveRenderer: true,
    renderedCells: liveCells.length,
  };
  const firstCapture = path.join(out, 'haunted-marsh-water-mask-start-825x375.png');
  await page.screenshot({ path: firstCapture });
  report.captures = [path.relative(root, firstCapture)];

  const startCell = [start.adventure.x, start.adventure.y];
  const candidates = [[startCell[0], startCell[1] + 1], [startCell[0] + 1, startCell[1]], [startCell[0] - 1, startCell[1]], [startCell[0], startCell[1] - 1]];
  const target = candidates.find(([x, y]) => {
    try { return routeTo(map, startCell, [x, y]).cost <= start.adventure.moves && !map.guards.has(`${x},${y}`); }
    catch { return false; }
  });
  assert.ok(target, 'a legal first step is reachable on the natural movement allowance');
  const route = routeTo(map, startCell, target);
  await page.locator(`#world [data-adventure-cell="${target.join(',')}"]`).dispatchEvent('click', { bubbles: true });
  await page.waitForFunction(() => Boolean(document.querySelector('#world [data-route-destination]')));
  const preview = await page.evaluate(() => ({
    destinationCount: document.querySelectorAll('#world [data-route-destination]').length,
    state: window.rebornSnapshot().adventure,
  }));
  assert.equal(preview.destinationCount, 1);
  assert.deepEqual([preview.state.x, preview.state.y], startCell, 'preview does not move the hero');
  assert.equal(preview.state.moves, start.adventure.moves, 'preview does not spend movement');
  await clickChoice('confirm-route');
  await page.waitForFunction(([x, y]) => {
    const state = window.rebornSnapshot();
    return state?.adventure?.x === x && state?.adventure?.y === y;
  }, target);
  const moved = await page.evaluate(() => window.rebornSnapshot());
  assert.equal(moved.adventure.moves, start.adventure.moves - route.cost);
  await page.waitForFunction(id => {
    const state = window.rebornSnapshot();
    const head = window.rebornCommittedHead();
    return state?.id === id && head?.campaignId === id && head.revision >= state.revision
      && document.querySelector('#save')?.dataset.saveState === 'committed';
  }, report.campaignId, { timeout: 15000 });
  report.move = { from: startCell, to: target, route: route.cells, cost: route.cost, movesRemaining: moved.adventure.moves, visited: moved.adventure.visited, saveState: await page.locator('#save').getAttribute('data-save-state') };
  const movedCapture = path.join(out, 'haunted-marsh-water-mask-after-move-825x375.png');
  await page.screenshot({ path: movedCapture });
  report.captures.push(path.relative(root, movedCapture));

  await page.reload({ waitUntil: 'networkidle' });
  await page.waitForFunction(id => window.rebornSnapshot()?.id === id, report.campaignId, { timeout: 10000 });
  const afterReload = await page.evaluate(() => window.rebornSnapshot());
  assert.deepEqual([afterReload.adventure.x, afterReload.adventure.y], target, 'committed map position survives a real reload');
  assert.deepEqual(afterReload.adventure.visited, moved.adventure.visited, 'discovery survives reload');
  report.reload = { position: [afterReload.adventure.x, afterReload.adventure.y], moves: afterReload.adventure.moves, visited: afterReload.adventure.visited };
  assert.deepEqual(report.errors, [], 'the live journey has no browser errors');
  assert.deepEqual(report.failedResponses, [], 'the live journey has no failed HTTP responses');
  report.result = 'PASS_BOUNDED_LIVE_MAP_LOAD_LEGAL_MOVE_SAVE_RELOAD; NOT_FULL_JOURNEY_OR_MAP_ART_ACCEPTANCE';
} catch (error) {
  report.result = 'FAIL';
  report.error = String(error?.stack || error);
  throw error;
} finally {
  await fs.writeFile(path.join(out, 'report.json'), JSON.stringify(report, null, 2));
  await browser.close();
}
