import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import worlds from '../../../src/data/adventure-worlds.json' with { type: 'json' };
import contract from '../../../src/data/implementation-contract.json' with { type: 'json' };
import { adventureGeometryForWorld, adventureMap, routeTo } from '../../../src/core/navigation.js';

const root = process.cwd();
const output = path.join(root, 'qa/game-completion-20261021/visual-review/adventure-cache-natural-live-20261021-run02');
const url = 'http://127.0.0.1:4179/?audit=1';
await fs.mkdir(output, { recursive: true });
const report = {
  recordedAt: new Date().toISOString(),
  classification: 'NATURAL_GRASSLANDS_ROUTE_PREVIEW_CANCEL_BRIDGE_SAVE_RELOAD',
  journey: 'Fresh visible campaign -> Grasslands -> preview legal bridge route -> cancel unchanged -> confirm -> reload',
  note: 'All campaign actions use visible controls. Snapshot reads and imported geometry are assertions only; no campaign state, route, or movement is injected.',
  url,
  errors: [],
  failedResponses: [],
};
const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
const context = await browser.newContext({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1 });
const page = await context.newPage();
await page.addInitScript(() => {
  const original = JSON.stringify;
  JSON.stringify = function (value, replacer, space) {
    if (value && typeof value === 'object' && value.state?.adventure && value.frame?.scale) {
      const stage = document.querySelector('#stage')?.getBoundingClientRect();
      const panel = document.querySelector('#panel');
      value.auditProbe = {
        viewport: [window.innerWidth, window.innerHeight],
        stage: stage ? [stage.x, stage.y, stage.width, stage.height] : null,
        panelOpen: panel?.classList.contains('open') ?? null,
        panelWidth: panel?.getBoundingClientRect().width ?? null,
      };
    }
    return original.call(this, value, replacer, space);
  };
});
page.on('pageerror', error => report.errors.push(String(error)));
page.on('console', message => { if (message.type() === 'error') report.errors.push(message.text()); });
page.on('response', response => { if (response.status() >= 400) report.failedResponses.push({ status: response.status(), url: response.url() }); });

async function clickChoice(id) {
  const control = page.locator('[data-choice="' + id + '"]').first();
  await control.waitFor({ state: 'visible', timeout: 10000 });
  assert.equal(await control.isDisabled(), false, id + ' is enabled');
  await control.click();
}

async function previewSouthToBridge() {
  await clickChoice('preview-south');
  await clickChoice('preview-south');
  await page.waitForFunction(() => Boolean(document.querySelector('#world [data-route-destination]')));
}

try {
  await page.goto(url, { waitUntil: 'networkidle' });
  await clickChoice('new-campaign');
  await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'campaignMapSelect');
  await clickChoice('campaign-world:grasslands');
  await clickChoice('begin-selected-world');
  await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'hero');
  await clickChoice('scene-class:knight');
  await clickChoice('scene-enter-valley');
  await page.waitForTimeout(100);
  await page.locator('#context').click();
  await clickChoice('site-list');
  await clickChoice('choose-site:townhall');
  await clickChoice('tutorial-toggle');
  await page.locator('[data-choice="nav:adventure"]').first().click();
  await page.locator('#dock [data-choice="inspect:adventure"]').click();
  await clickChoice('enter-adventure');
  await page.waitForFunction(() => Boolean(window.rebornSnapshot?.()?.adventure), null, { timeout: 15000 });
  await page.waitForFunction(() => {
    const image = document.querySelector('#terrain');
    return image?.complete && image.naturalWidth > 0;
  }, null, { timeout: 15000 });

  const start = await page.evaluate(() => window.rebornSnapshot?.());
  assert.equal(start.adventureWorldId, 'grasslands');
  assert.equal(start.adventure.atTown, false);
  const world = worlds.find(row => row.id === start.adventureWorldId);
  const geometry = adventureGeometryForWorld(contract.geometry.adventure, world, start.seed);
  const map = adventureMap(geometry);
  const target = [8, 5];
  const crossingCells = geometry.bridges.flatMap(bridge => bridge.cells);
  assert.ok(crossingCells.some(cell => cell[0] === target[0] && cell[1] === target[1]), 'target is a registered Grasslands bridge cell');
  const route = routeTo(map, [start.adventure.x, start.adventure.y], target);
  assert.ok(route.cells.some(cell => cell[0] === target[0] && cell[1] === target[1]), 'route traverses the selected bridge cell');
  assert.ok(route.cost <= start.adventure.moves, 'route cost fits the visible movement budget');
  report.start = {
    position: [start.adventure.x, start.adventure.y],
    moves: start.adventure.moves,
    revision: start.revision,
    resources: start.resources,
    bridgeCell: target,
    expectedRoute: route,
  };

  const beforePreview = await page.evaluate(() => window.rebornSnapshot?.());
  await previewSouthToBridge();
  const preview = await page.evaluate(() => ({
    status: document.querySelector('#scene-ui.game-status')?.textContent || '',
    routeDestinationCount: document.querySelectorAll('#world [data-route-destination]').length,
    polylines: [...document.querySelectorAll('#world polyline')].map(node => node.getAttribute('points')),
    state: window.rebornSnapshot?.(),
  }));
  assert.equal(preview.routeDestinationCount, 1);
  const openPanelCancelControls = await page.evaluate(() => ({
    panelClear: [...document.querySelectorAll('#choices [data-choice="clear-preview"]')].filter(node => node.getClientRects().length > 0).length,
    panelCancel: [...document.querySelectorAll('#choices [data-choice="cancel-route"]')].filter(node => node.getClientRects().length > 0).length,
    dockCancel: [...document.querySelectorAll('#dock [data-choice="cancel-route"]')].filter(node => node.getClientRects().length > 0).length,
  }));
  assert.deepEqual(openPanelCancelControls, { panelClear: 1, panelCancel: 0, dockCancel: 0 });
  report.openPanelCancelControls = openPanelCancelControls;
  assert.match(preview.status, /Cost\s+\d+/);
  assert.deepEqual([preview.state.adventure.x, preview.state.adventure.y], [beforePreview.adventure.x, beforePreview.adventure.y]);
  assert.equal(preview.state.adventure.moves, beforePreview.adventure.moves);
  assert.deepEqual(preview.state.resources, beforePreview.resources, 'preview costs no resources');
  assert.deepEqual(preview.state.resources, beforePreview.resources, 'preview costs no resources');
  const expectedPoints = [[start.adventure.x, start.adventure.y], ...route.cells]
    .map(([x, y]) => {
      const m = geometry.worldToSource;
      return [m[0] * (x + 0.5) + m[2] * (y + 0.5) + m[4], m[1] * (x + 0.5) + m[3] * (y + 0.5) + m[5]].join(',');
    }).join(' ');
  assert.equal(preview.polylines[0], expectedPoints, 'visible route overlay follows the legal route through the bridge cell');
  report.preview = { status: preview.status, actualPoints: preview.polylines[0], position: [preview.state.adventure.x, preview.state.adventure.y], moves: preview.state.adventure.moves, resources: preview.state.resources, revisionBefore: beforePreview.revision, revisionAfter: preview.state.revision, gameplayStateUnchanged: true };
  let capture = path.join(output, 'grasslands-bridge-route-preview-1280x720.jpg');
  await page.screenshot({ path: capture, type: 'jpeg', quality: 82 });
  report.captures = [path.relative(root, capture)];

  await clickChoice('clear-preview');
  const cancelled = await page.evaluate(() => window.rebornSnapshot?.());
  assert.deepEqual([cancelled.adventure.x, cancelled.adventure.y], [start.adventure.x, start.adventure.y]);
  assert.equal(cancelled.adventure.moves, start.adventure.moves); assert.deepEqual(cancelled.resources, start.resources, 'cancel costs no resources');

  assert.equal(await page.locator('#world [data-route-destination]').count(), 0);
  report.cancel = { position: [cancelled.adventure.x, cancelled.adventure.y], moves: cancelled.adventure.moves, resources: cancelled.resources, revision: cancelled.revision };

  await page.locator('#panel-close').click();
  await page.waitForFunction(() => !document.querySelector('#panel')?.classList.contains('open'));
  await page.setViewportSize({ width: 825, height: 375 });
  await page.waitForFunction(() => {
    const snapshot = JSON.parse(document.querySelector('#audit-snapshot')?.textContent || 'null');
    const frame = document.querySelector('#frame')?.getBoundingClientRect();
    return snapshot?.view === 'adventure'
      && snapshot.frame?.boardGeometry === true
      && Math.abs(snapshot.frame.fit.scale * 1376 - 825) < 1
      && frame && Math.abs(frame.x) < 1 && Math.abs(frame.width - 825) < 1;
  }, null, { timeout: 10000 });
  report.compactClosedPanelCamera = await page.evaluate(() => {
    const snapshot = JSON.parse(document.querySelector('#audit-snapshot').textContent);
    const rect = document.querySelector('#frame').getBoundingClientRect();
    return { fit: snapshot.frame.fit, worldWidth: snapshot.frame.worldWidth, viewport: [innerWidth, innerHeight], frame: { x: rect.x, width: rect.width, height: rect.height } };
  });
  await page.locator('#world [data-adventure-cell="8,5"]').click();
  await page.waitForFunction(() => Boolean(document.querySelector('#world [data-route-destination]')));
  const closedPanelCancelControls = await page.evaluate(() => ({
    panelClear: [...document.querySelectorAll('#choices [data-choice="clear-preview"]')].filter(node => node.getClientRects().length > 0).length,
    panelCancel: [...document.querySelectorAll('#choices [data-choice="cancel-route"]')].filter(node => node.getClientRects().length > 0).length,
    dockCancel: [...document.querySelectorAll('#dock [data-choice="cancel-route"]')].filter(node => node.getClientRects().length > 0).length,
  }));
  assert.deepEqual(closedPanelCancelControls, { panelClear: 0, panelCancel: 0, dockCancel: 1 });
  await page.locator('#dock [data-choice="cancel-route"]').click();
  const dockCancelled = await page.evaluate(() => window.rebornSnapshot?.());
  assert.deepEqual([dockCancelled.adventure.x, dockCancelled.adventure.y], [start.adventure.x, start.adventure.y]);
  assert.equal(dockCancelled.adventure.moves, start.adventure.moves);
  assert.deepEqual(dockCancelled.resources, start.resources);
  assert.equal(await page.locator('#world [data-route-destination]').count(), 0);
  report.closedPanelCancelControls = closedPanelCancelControls;
  report.closedPanelCancel = { position: [dockCancelled.adventure.x, dockCancelled.adventure.y], moves: dockCancelled.adventure.moves, resources: dockCancelled.resources };

  await page.locator('#world [data-adventure-cell="8,5"]').click();
  await page.waitForFunction(() => Boolean(document.querySelector('#world [data-route-destination]')));
  const dockConfirm = page.locator('#dock [data-choice="confirm-route"]');
  await dockConfirm.waitFor({ state: 'visible', timeout: 5000 });
  assert.equal(await dockConfirm.isDisabled(), false);
  capture = path.join(output, 'grasslands-bridge-route-dock-825x375.jpg');
  await page.screenshot({ path: capture, type: 'jpeg', quality: 82 });
  report.captures.push(path.relative(root, capture));


  const confirm = page.locator('#dock [data-choice="confirm-route"]');
  await confirm.waitFor({ state: 'visible', timeout: 5000 });
  assert.equal(await confirm.isDisabled(), false);
  await confirm.click();
  await page.waitForFunction(revision => (window.rebornSnapshot?.()?.revision || 0) > revision, start.revision, { timeout: 10000 });
  const moved = await page.evaluate(() => window.rebornSnapshot?.());
  assert.deepEqual([moved.adventure.x, moved.adventure.y], target);
  assert.equal(moved.adventure.moves, start.adventure.moves - route.cost);
  assert.ok(moved.adventure.visited.includes(target.join(',')));
  await page.waitForFunction(revision => window.rebornCommittedHead?.()?.revision >= revision
    && document.querySelector('#save')?.dataset.saveState === 'committed', moved.revision, { timeout: 15000 });
  await page.waitForTimeout(1100);
  report.move = {
    position: [moved.adventure.x, moved.adventure.y],
    moves: moved.adventure.moves,
    cost: route.cost,
    visited: moved.adventure.visited,
    saveState: await page.locator('#save').getAttribute('data-save-state'),
  };

  capture = path.join(output, 'grasslands-bridge-crossing-825x375.jpg');
  await page.setViewportSize({ width: 825, height: 375 });
  await page.waitForTimeout(1200);
  report.compactLayout = await page.evaluate(() => {
    const read = selector => {
      const node = document.querySelector(selector);
      if (!node) return null;
      const rect = node.getBoundingClientRect();
      return { x: rect.x, y: rect.y, width: rect.width, height: rect.height, cssWidth: getComputedStyle(node).width };
    };
    return {
      innerWidth: window.innerWidth,
      innerHeight: window.innerHeight,
      devicePixelRatio: window.devicePixelRatio,
      app: read('#app'),
      stage: read('#stage'),
      stageField: read('#stage-field'),
      frame: read('#frame'),
      terrain: read('#terrain'),
      mapImageWidth: document.querySelector('#terrain')?.naturalWidth || 0,
      view: document.querySelector('#app')?.dataset.view,
      panelOpen: document.querySelector('#panel')?.classList.contains('open'),
      panel: read('#panel'),
      frameTransform: document.querySelector('#frame')?.style.transform,
      adventure: window.rebornSnapshot?.()?.adventure,
      auditSnapshot: document.querySelector('#audit-snapshot')?.textContent || null,
    };
  });  await page.screenshot({ path: capture, type: 'jpeg', quality: 82 });
  report.captures.push(path.relative(root, capture));
  await page.setViewportSize({ width: 1280, height: 720 });
  await page.waitForTimeout(1200);
  await page.reload({ waitUntil: 'networkidle' });
  await page.waitForFunction(() => Boolean(window.rebornSnapshot?.()), null, { timeout: 15000 });
  let reloaded = await page.evaluate(() => window.rebornSnapshot?.());
  if (await page.locator('#app').getAttribute('data-view') === 'home') {
    await clickChoice('continue');
    await page.waitForFunction(() => document.querySelector('#app')?.dataset.view !== 'home');
    reloaded = await page.evaluate(() => window.rebornSnapshot?.());
  }
  assert.equal(reloaded.adventureWorldId, 'grasslands');
  assert.deepEqual([reloaded.adventure.x, reloaded.adventure.y], target);
  assert.equal(reloaded.adventure.moves, start.adventure.moves - route.cost);
  assert.ok(reloaded.adventure.visited.includes(target.join(',')));
  report.reload = {
    worldId: reloaded.adventureWorldId,
    position: [reloaded.adventure.x, reloaded.adventure.y],
    moves: reloaded.adventure.moves,
    visited: reloaded.adventure.visited,
    revision: reloaded.revision,
  };
  if (await page.locator('#app').getAttribute('data-view') !== 'adventure') {
    await page.locator('#nav [data-choice="nav:adventure"]').click();
    await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'adventure');
  }  await page.setViewportSize({ width: 825, height: 375 });
  await page.waitForFunction(() => {
    const snapshot = JSON.parse(document.querySelector('#audit-snapshot')?.textContent || 'null');
    const frame = document.querySelector('#frame')?.getBoundingClientRect();
    return snapshot?.view === 'adventure'
      && snapshot.frame?.fit?.mode === 'focus-cover'
      && frame && frame.left <= 1 && frame.right >= innerWidth - 1;
  }, null, { timeout: 10000 });
  if (!(await page.locator('#panel').evaluate(node => node.classList.contains('open')))) {
    await page.locator('#dock [data-choice="inspect:adventure"]').click();
    await page.waitForFunction(() => document.querySelector('#panel')?.classList.contains('open'));
  }
  let cacheStart = await page.evaluate(() => window.rebornSnapshot?.());
  const caches = Object.entries(geometry.anchors).filter(([id]) => ['food', 'wood', 'stone', 'gold'].includes(id)).map(([id, cell]) => {
    const destination = [Math.floor(cell[0]), Math.floor(cell[1])];
    return { id, cell: destination, route: routeTo(map, [cacheStart.adventure.x, cacheStart.adventure.y], destination) };
  }).sort((a, b) => a.route.cost - b.route.cost);
  assert.ok(caches.length > 0, 'the selected world has a reachable resource cache');
  const cache = caches[0];
  const steps = [];
  for (const next of cache.route.cells) {
    let current = await page.evaluate(() => window.rebornSnapshot?.());
    const stepRoute = routeTo(map, [current.adventure.x, current.adventure.y], next);
    if (current.adventure.moves < stepRoute.cost) {
      const prior = current.revision;
      await clickChoice('adventure-end-day');
      await page.waitForFunction(revision => window.rebornSnapshot?.()?.revision > revision
        && window.rebornSnapshot().adventure.moves > 0, prior, { timeout: 10000 });
      current = await page.evaluate(() => window.rebornSnapshot?.());
      await page.waitForFunction(revision => window.rebornCommittedHead?.()?.revision >= revision
        && document.querySelector('#save')?.dataset.saveState === 'committed', current.revision, { timeout: 15000 });
    }
    const dx = next[0] - current.adventure.x, dy = next[1] - current.adventure.y;
    const direction = dx === 1 ? 'east' : dx === -1 ? 'west' : dy === 1 ? 'south' : dy === -1 ? 'north' : '';
    assert.ok(direction, 'each planned route step is one visible cardinal move');
    assert.ok(current.adventure.moves >= stepRoute.cost, 'movement is available for this step');
    await clickChoice(`preview-${direction}`);
    await page.locator('#choices [data-choice="confirm-route"]').waitFor({ state: 'visible', timeout: 5000 });
    const prior = current.revision;
    await clickChoice('confirm-route');
    await page.waitForFunction(({ x, y, revision }) => {
      const state = window.rebornSnapshot?.();
      return state?.adventure?.x === x && state.adventure.y === y && state.revision > revision;
    }, { x: next[0], y: next[1], revision: prior }, { timeout: 10000 });
    current = await page.evaluate(() => window.rebornSnapshot?.());
    await page.waitForFunction(revision => window.rebornCommittedHead?.()?.revision >= revision
      && document.querySelector('#save')?.dataset.saveState === 'committed', current.revision, { timeout: 15000 });
    steps.push({ direction, position: next, moves: current.adventure.moves, day: current.day });
  }
  let atCache = await page.evaluate(() => window.rebornSnapshot?.());
  assert.deepEqual([atCache.adventure.x, atCache.adventure.y], cache.cell, 'hero reached the selected cache cell by visible cardinal movement');
  await page.locator(`#world [data-adventure-anchor="${cache.id}"]`).waitFor({ state: 'visible', timeout: 10000 });
  await page.locator(`#choices [data-choice="collect-cache:${cache.id}"]`).waitFor({ state: 'visible', timeout: 10000 });
  const amount = atCache.adventure.cacheOffers[cache.id];
  const resourcesBefore = { ...atCache.resources };
  const beforeClaimRevision = atCache.revision;
  await clickChoice(`collect-cache:${cache.id}`);
  await page.waitForFunction(({ id, revision }) => {
    const state = window.rebornSnapshot?.();
    return state?.adventure?.collectedCaches?.includes(id) && state.revision > revision;
  }, { id: cache.id, revision: beforeClaimRevision }, { timeout: 10000 });
  atCache = await page.evaluate(() => window.rebornSnapshot?.());
  await page.waitForFunction(revision => window.rebornCommittedHead?.()?.revision >= revision
    && document.querySelector('#save')?.dataset.saveState === 'committed', atCache.revision, { timeout: 15000 });
  assert.ok(atCache.resources[cache.id] >= resourcesBefore[cache.id] + amount, 'claim grants the saved cache amount');
  assert.ok(atCache.adventure.collectedCaches.includes(cache.id));
  report.cacheJourney = {
    id: cache.id,
    start: [cacheStart.adventure.x, cacheStart.adventure.y],
    destination: cache.cell,
    plannedCost: cache.route.cost,
    plannedCells: cache.route.cells,
    steps,
    amount,
    resourcesBefore,
    resourcesAfter: atCache.resources,
    day: atCache.day,
    saveState: await page.locator('#save').getAttribute('data-save-state'),
  };
  capture = path.join(output, 'grasslands-cache-claimed-825x375.jpg');
  await page.screenshot({ path: capture, type: 'jpeg', quality: 82 });
  report.captures.push(path.relative(root, capture));
  await page.reload({ waitUntil: 'networkidle' });
  await page.waitForFunction(() => Boolean(window.rebornSnapshot?.()), null, { timeout: 15000 });
  let cacheReload = await page.evaluate(() => window.rebornSnapshot?.());
  if (await page.locator('#app').getAttribute('data-view') === 'home') {
    await clickChoice('continue');
    await page.waitForFunction(() => document.querySelector('#app')?.dataset.view !== 'home');
    cacheReload = await page.evaluate(() => window.rebornSnapshot?.());
  }
  assert.equal(cacheReload.adventureWorldId, 'grasslands');
  assert.deepEqual([cacheReload.adventure.x, cacheReload.adventure.y], cache.cell);
  assert.ok(cacheReload.adventure.collectedCaches.includes(cache.id), 'claimed cache persisted through reload');
  assert.ok(cacheReload.resources[cache.id] >= atCache.resources[cache.id]);
  if (await page.locator('#app').getAttribute('data-view') !== 'adventure') {
    await page.locator('#nav [data-choice="nav:adventure"]').click();
    await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'adventure');
  }  if (!(await page.locator('#panel').evaluate(node => node.classList.contains('open')))) {
    await page.locator('#dock [data-choice="inspect:adventure"]').click();
    await page.waitForFunction(() => document.querySelector('#panel')?.classList.contains('open'));
  }
  assert.equal(await page.locator(`#choices [data-choice="collect-cache:${cache.id}"]`).count(), 0, 'the claimed cache cannot be collected again');
  assert.equal(await page.locator(`#world [data-adventure-anchor="${cache.id}"]`).count(), 0, 'the claimed cache marker is removed after reload');
  report.cacheReload = { worldId: cacheReload.adventureWorldId, position: [cacheReload.adventure.x, cacheReload.adventure.y], collectedCaches: cacheReload.adventure.collectedCaches, resource: cacheReload.resources[cache.id], revision: cacheReload.revision, claimButtonVisible: false, markerVisible: false };
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
