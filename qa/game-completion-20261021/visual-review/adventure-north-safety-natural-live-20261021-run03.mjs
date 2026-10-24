import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import worlds from '../../../src/data/adventure-worlds.json' with { type: 'json' };
import contract from '../../../src/data/implementation-contract.json' with { type: 'json' };
import { adventureGeometryForWorld, adventureMap } from '../../../src/core/navigation.js';

const root = process.cwd();
const worldId = process.argv[2] || 'grasslands';
assert.ok(worlds.some(row => row.id === worldId), `known Adventure world: ${worldId}`);
const output = path.join(root, `qa/game-completion-20261021/visual-review/adventure-north-safety-${worldId}-live-20261021-run03`);
const url = 'http://127.0.0.1:4179/?audit=1';
await fs.mkdir(output, { recursive: true });
const report = {
  recordedAt: new Date().toISOString(),
  classification: 'NATURAL_CARDINAL_JOURNEY_TO_NORTH_EDGE_FADE_PREVIEW',
  journey: `Fresh visible campaign -> ${worldId} -> cardinal moves to an unblocked outer map cell -> save/reload`,
  note: 'Campaign, world, and movement state are never injected. A read-only path search selects an open reachable north-edge cell while excluding guards; every step is then previewed and committed through visible game controls. Preview only: apply an 18% alpha fade to the top of the terrain image to soften the 128px north inset seam; validate natural gameplay and header clearance separately.',
  url,
  errors: [],
  failedResponses: [],
  steps: [],
};
const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
const context = await browser.newContext({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1 });
const page = await context.newPage();
page.on('pageerror', error => report.errors.push(String(error)));
page.on('console', message => { if (message.type() === 'error') report.errors.push(message.text()); });
page.on('response', response => { if (response.status() >= 400) report.failedResponses.push({ status: response.status(), url: response.url() }); });

async function clickChoice(id) {
  const control = page.locator(`[data-choice="${id}"]`).first();
  await control.waitFor({ state: 'visible', timeout: 10000 });
  assert.equal(await control.isDisabled(), false, `${id} is enabled`);
  await control.click();
}

const directions = [
  { id: 'north', dx: 0, dy: -1 },
  { id: 'east', dx: 1, dy: 0 },
  { id: 'south', dx: 0, dy: 1 },
  { id: 'west', dx: -1, dy: 0 },
];
const cellKey = (cell) => `${cell[0]},${cell[1]}`;
function cardinalPath(map, start, goal) {
  const origin = cellKey(start), target = cellKey(goal);
  const queue = [start];
  const prior = new Map([[origin, null]]);
  for (let index = 0; index < queue.length && !prior.has(target); index += 1) {
    const [x, y] = queue[index];
    for (const { dx, dy } of directions) {
      const next = [x + dx, y + dy], key = cellKey(next);
      if (next[0] < 0 || next[1] < 0 || next[0] >= map.cols || next[1] >= map.rows) continue;
      if (map.blocked.has(key) || map.guards.has(key) || prior.has(key)) continue;
      prior.set(key, cellKey([x, y]));
      queue.push(next);
    }
  }
  if (!prior.has(target)) return null;
  const cells = [];
  let cursor = target;
  while (cursor !== origin) {
    cells.push(cursor.split(',').map(Number));
    cursor = prior.get(cursor);
    if (cursor == null) throw new Error('Broken cardinal path reconstruction');
  }
  return cells.reverse();
}

async function cameraEvidence(position, geometry) {
  return page.evaluate(({ position, matrix }) => {
    const snapshot = JSON.parse(document.querySelector('#audit-snapshot')?.textContent || 'null');
    const frame = document.querySelector('#frame')?.getBoundingClientRect();
    const stage = document.querySelector('#stage')?.getBoundingClientRect();
    const header = document.querySelector('#app > header')?.getBoundingClientRect();
    const actors = [...document.querySelectorAll('#world [data-actor], #world [data-mount]')].map(node => {
      const rect = node.getBoundingClientRect();
      return {
        kind: node.getAttribute('data-actor') ? 'actor' : 'mount',
        id: node.getAttribute('data-actor') || node.getAttribute('data-mount'),
        bounds: { left: rect.left, top: rect.top, right: rect.right, bottom: rect.bottom },
        withinViewport: rect.left >= 0 && rect.top >= 0 && rect.right <= innerWidth && rect.bottom <= innerHeight,
      };
    });
    const sourceX = matrix[0] * (position[0] + 0.5) + matrix[2] * (position[1] + 0.5) + matrix[4];
    const sourceY = matrix[1] * (position[0] + 0.5) + matrix[3] * (position[1] + 0.5) + matrix[5];
    const fit = snapshot?.frame?.fit;
    const heroScreen = fit && stage
      ? [stage.x + fit.offset[0] + sourceX * fit.scale, stage.y + fit.offset[1] + sourceY * fit.scale]
      : null;
    return {
      viewport: [innerWidth, innerHeight],
      fit,
      frame: frame ? { left: frame.left, top: frame.top, right: frame.right, bottom: frame.bottom } : null,
      stage: stage ? { left: stage.left, top: stage.top, right: stage.right, bottom: stage.bottom } : null,
      header: header ? { left: header.left, top: header.top, right: header.right, bottom: header.bottom } : null,
      heroScreen,
      heroVisible: Boolean(heroScreen && heroScreen[0] >= 0 && heroScreen[0] <= innerWidth && heroScreen[1] >= 0 && heroScreen[1] <= innerHeight),
      actors,
      allActorsWithinViewport: actors.length > 0 && actors.every(actor => actor.withinViewport),
      frameCoversViewport: Boolean(frame && frame.left <= 1 && frame.top <= 1 && frame.right >= innerWidth - 1 && frame.bottom >= innerHeight - 1),
      boardGeometry: snapshot?.frame?.boardGeometry ?? false,
      edgeSafety: snapshot?.frame?.edgeSafety ?? null,
      stageBackground: getComputedStyle(document.querySelector('#stage')).backgroundImage,
      traveler: [...new Set(document.querySelectorAll('#world [data-adventure-travel-mode], #world [data-rider], #world [data-mount=\"horse\"]'))].map(node => { const rect = node.getBoundingClientRect(); return { tag: node.tagName.toLowerCase(), mode: node.getAttribute('data-adventure-travel-mode'), rider: node.getAttribute('data-rider'), mount: node.getAttribute('data-mount'), bounds: { left: rect.left, top: rect.top, right: rect.right, bottom: rect.bottom }, withinViewport: rect.left >= 0 && rect.top >= 0 && rect.right <= innerWidth && rect.bottom <= innerHeight }; }),
      position: window.rebornSnapshot?.()?.adventure ? [window.rebornSnapshot().adventure.x, window.rebornSnapshot().adventure.y] : null,
    };
  }, { position, matrix: geometry.worldToSource });
}

try {
  await page.goto(url, { waitUntil: 'networkidle' });
  await clickChoice('new-campaign');
  await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'campaignMapSelect');
  await clickChoice(`campaign-world:${worldId}`);
  await clickChoice('begin-selected-world');
  await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'hero');
  await clickChoice('scene-class:knight');
  await clickChoice('scene-enter-valley');
  await page.waitForTimeout(100);
  await page.locator('#context').click();
  await clickChoice('site-list');
  await clickChoice('choose-site:townhall');
  await clickChoice('tutorial-toggle');
  await page.locator('#nav [data-choice="nav:adventure"]').first().click();
  await page.locator('#dock [data-choice="inspect:adventure"]').click();
  await clickChoice('enter-adventure');
  await page.waitForFunction(() => Boolean(window.rebornSnapshot?.()?.adventure), null, { timeout: 15000 });
  await page.waitForFunction(() => {
    const image = document.querySelector('#terrain');
    return image?.complete && image.naturalWidth > 0;
  }, null, { timeout: 15000 });

  const initial = await page.evaluate(() => window.rebornSnapshot?.());
  assert.equal(initial.adventureWorldId, worldId);
  assert.equal(initial.adventure.atTown, false);
  const world = worlds.find(row => row.id === initial.adventureWorldId);
  const geometry = adventureGeometryForWorld(contract.geometry.adventure, world, initial.seed);
  const map = adventureMap(geometry);
  const start = [initial.adventure.x, initial.adventure.y];
  const border = [];
  for (let y = 0; y < map.rows; y += 1) {
    for (let x = 0; x < map.cols; x += 1) {
      if (y !== 0) continue;
      const cell = [x, y], key = cellKey(cell);
      if (key === cellKey(start) || map.blocked.has(key) || map.guards.has(key)) continue;
      const cells = cardinalPath(map, start, cell);
      if (cells) border.push({ cell, cells });
    }
  }
  border.sort((a, b) => a.cells.length - b.cells.length || a.cell[1] - b.cell[1] || a.cell[0] - b.cell[0]);
  assert.ok(border.length > 0, 'at least one guard-free reachable outer-edge cell exists');
  const target = border[0];
  report.start = { position: start, moves: initial.adventure.moves, revision: initial.revision, seed: initial.seed, worldId: initial.adventureWorldId };
  report.edge = { position: target.cell, pathLength: target.cells.length, path: target.cells, candidateCount: border.length, mapSize: [map.cols, map.rows] };

  await page.setViewportSize({ width: 825, height: 375 });
  await page.addStyleTag({ content: '#terrain { -webkit-mask-image: linear-gradient(to bottom, transparent 0%, #000 18%); mask-image: linear-gradient(to bottom, transparent 0%, #000 18%); }' });
  await page.waitForTimeout(150);
  if (!(await page.locator('#panel').evaluate(node => node.classList.contains('open')))) {
    await page.locator('#dock [data-choice="inspect:adventure"]').click();
    await page.waitForFunction(() => document.querySelector('#panel')?.classList.contains('open'));
  }
  let current = await page.evaluate(() => window.rebornSnapshot?.());
  report.compactStartCamera = await cameraEvidence(start, geometry);
  assert.equal(report.compactStartCamera.boardGeometry, true);
  assert.equal(report.compactStartCamera.frameCoversViewport, true);
  assert.equal(report.compactStartCamera.heroVisible, true);

  for (const next of target.cells) {
    current = await page.evaluate(() => window.rebornSnapshot?.());
    if (current.adventure.moves < 1) {
      const beforeEndDay = current.revision;
      await clickChoice('adventure-end-day');
      await page.waitForFunction(revision => window.rebornSnapshot?.()?.revision > revision
        && window.rebornSnapshot().adventure.moves > 0, beforeEndDay, { timeout: 10000 });
      current = await page.evaluate(() => window.rebornSnapshot?.());
      await page.waitForFunction(revision => window.rebornCommittedHead?.()?.revision >= revision
        && document.querySelector('#save')?.dataset.saveState === 'committed', current.revision, { timeout: 15000 });
    }
    const dx = next[0] - current.adventure.x, dy = next[1] - current.adventure.y;
    const direction = directions.find(item => item.dx === dx && item.dy === dy);
    assert.ok(direction, 'the planned edge route contains only cardinal moves');
    const prior = current.revision;
    await clickChoice(`preview-${direction.id}`);
    await page.locator('#choices [data-choice="confirm-route"]').waitFor({ state: 'visible', timeout: 5000 });
    await clickChoice('confirm-route');
    await page.waitForFunction(({ x, y, revision }) => {
      const state = window.rebornSnapshot?.();
      return state?.adventure?.x === x && state.adventure.y === y && state.revision > revision;
    }, { x: next[0], y: next[1], revision: prior }, { timeout: 10000 });
    current = await page.evaluate(() => window.rebornSnapshot?.());
    await page.waitForFunction(revision => window.rebornCommittedHead?.()?.revision >= revision
      && document.querySelector('#save')?.dataset.saveState === 'committed', current.revision, { timeout: 15000 });
    const camera = await cameraEvidence(next, geometry);
    assert.deepEqual(camera.position, next, 'the saved hero position matches the visible move');
    assert.equal(camera.boardGeometry, true);
    if (next[1] === 0) {
      assert.equal(camera.edgeSafety?.side, 'north', 'north-edge safety mode is active');
      assert.ok(camera.edgeSafety.stageOffsetY >= 128, 'the frame has a 128px north-edge safety inset');
      assert.equal(camera.edgeSafety.backdropWorldId, worldId, 'the matching world terrain is used behind the inset');
      assert.ok(camera.stageBackground.includes(world.terrainFile), 'the stage background resolves the world terrain source');
      assert.ok(camera.traveler.length > 0, 'the traveler has measurable bounds');
      assert.ok(camera.traveler.every(item => item.withinViewport), 'the traveler and mount remain inside the viewport');
      assert.ok(camera.traveler.every(item => item.bounds.top >= camera.header.bottom + 8), 'the traveler and mount clear the header with an 8px gap');
      assert.equal(camera.heroVisible, true, 'the hero remains on screen');
    } else {
      assert.equal(camera.frameCoversViewport, true, 'the terrain frame covers the compact viewport away from the north edge');
      assert.equal(camera.heroVisible, true, 'the hero remains on screen during the edge journey');
    }
    report.steps.push({ direction: direction.id, position: next, moves: current.adventure.moves, day: current.day, revision: current.revision, camera });
  }

  current = await page.evaluate(() => window.rebornSnapshot?.());
  assert.deepEqual([current.adventure.x, current.adventure.y], target.cell);
  assert.ok(target.cell[0] === 0 || target.cell[0] === map.cols - 1 || target.cell[1] === 0 || target.cell[1] === map.rows - 1);
  assert.ok(current.adventure.visited.includes(cellKey(target.cell)), 'outer-edge cell is in the saved explored area');
  report.destination = { position: target.cell, moves: current.adventure.moves, day: current.day, visited: current.adventure.visited, revision: current.revision };
  const screenshot = path.join(output, `${worldId}-north-edge-safe-825x375.jpg`);
  await page.screenshot({ path: screenshot, type: 'jpeg', quality: 82 });
  report.captures = [path.relative(root, screenshot)];

  await page.reload({ waitUntil: 'networkidle' });
  await page.waitForFunction(() => Boolean(window.rebornSnapshot?.()), null, { timeout: 15000 });
  let reloaded = await page.evaluate(() => window.rebornSnapshot?.());
  if (await page.locator('#app').getAttribute('data-view') === 'home') {
    await clickChoice('continue');
    await page.waitForFunction(() => document.querySelector('#app')?.dataset.view !== 'home');
    reloaded = await page.evaluate(() => window.rebornSnapshot?.());
  }
  assert.equal(reloaded.adventureWorldId, worldId);
  assert.deepEqual([reloaded.adventure.x, reloaded.adventure.y], target.cell);
  assert.ok(reloaded.adventure.visited.includes(cellKey(target.cell)));
  report.reload = { worldId: reloaded.adventureWorldId, position: [reloaded.adventure.x, reloaded.adventure.y], visited: reloaded.adventure.visited, revision: reloaded.revision };
  assert.deepEqual(report.errors, []);
  assert.deepEqual(report.failedResponses, []);
  report.passed = true;
} catch (error) {
  report.passed = false;
  report.failure = String(error);
} finally {
  await context.close();
  await browser.close();
  report.recordedAt = new Date().toISOString();
  await fs.writeFile(path.join(output, 'report.json'), JSON.stringify(report, null, 2) + '\n');
}
console.log(JSON.stringify({ passed: report.passed, failure: report.failure || null, report: path.relative(root, path.join(output, 'report.json')) }, null, 2));
if (!report.passed) process.exitCode = 1;
