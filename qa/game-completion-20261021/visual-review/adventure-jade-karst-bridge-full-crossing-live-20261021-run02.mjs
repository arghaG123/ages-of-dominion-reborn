import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import worlds from '../../../src/data/adventure-worlds.json' with { type: 'json' };
import contract from '../../../src/data/implementation-contract.json' with { type: 'json' };
import { adventureGeometryForWorld, adventureMap, routeTo } from '../../../src/core/navigation.js';

const root = process.cwd();
const output = path.join(root, 'qa/game-completion-20261021/visual-review/adventure-jade-karst-bridge-full-crossing-live-20261021-run02');
const url = 'http://127.0.0.1:4179/?audit=1';
await fs.mkdir(output, { recursive: true });
const report = {
  recordedAt: new Date().toISOString(),
  classification: 'NATURAL_JADE_KARST_FULL_BRIDGE_CROSSING_MOTION_SAVE_RELOAD',
  journey: 'Fresh visible campaign -> Jade Karst -> approach registered bridge -> preview -> confirm -> capture mounted travel -> reload',
  note: 'All campaign actions use visible controls in a fresh browser context. Imported geometry computes the expected route but does not alter campaign state, route, or movement.',
  url,
  errors: [],
  failedResponses: [],
  captures: [],
};
const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
const context = await browser.newContext({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1 });
const page = await context.newPage();
page.on('pageerror', error => report.errors.push(String(error)));
page.on('console', message => { if (message.type() === 'error') report.errors.push(message.text()); });
page.on('response', response => { if (response.status() >= 400) report.failedResponses.push({ status: response.status(), url: response.url() }); });

async function clickChoice(id) {
  const control = page.locator('[data-choice="' + id + '"]').first();
  await control.waitFor({ state: 'visible', timeout: 12000 });
  assert.equal(await control.isDisabled(), false, id + ' is enabled');
  await control.click();
}

async function previewCell(cell) {
  await page.locator('#world [data-adventure-cell="' + cell.join(',') + '"]').click();
  await page.waitForFunction(() => Boolean(document.querySelector('#world [data-route-destination]')));
}

async function confirmVisibleRoute() {
  const panelControl = page.locator('#choices [data-choice="confirm-route"]').first();
  if (await panelControl.isVisible()) {
    assert.equal(await panelControl.isDisabled(), false);
    await panelControl.click();
    return;
  }
  const dockControl = page.locator('#dock [data-choice="confirm-route"]').first();
  await dockControl.waitFor({ state: 'visible', timeout: 5000 });
  assert.equal(await dockControl.isDisabled(), false);
  await dockControl.click();
}

async function committedState() {
  await page.waitForFunction(() => {
    const state = window.rebornSnapshot?.();
    const head = window.rebornCommittedHead?.();
    return state && head && head.revision >= state.revision
      && document.querySelector('#save')?.dataset.saveState === 'committed';
  }, null, { timeout: 15000 });
  return page.evaluate(() => window.rebornSnapshot?.());
}

async function routeView() {
  return page.evaluate(() => {
    const route = [...document.querySelectorAll('#world polyline')]
      .find(node => node.getAttribute('stroke') === '#09262c');
    const target = document.querySelector('#world [data-route-destination]');
    return {
      status: document.querySelector('#scene-ui.game-status')?.textContent || '',
      points: route?.getAttribute('points') || null,
      destinationCount: document.querySelectorAll('#world [data-route-destination]').length,
      destination: target ? [target.getAttribute('cx'), target.getAttribute('cy')] : null,
      state: window.rebornSnapshot?.(),
    };
  });
}

async function saveCapture(name) {
  const file = path.join(output, name);
  await page.screenshot({ path: file, type: 'jpeg', quality: 88 });
  report.captures.push(path.relative(root, file));
}

try {
  await page.goto(url, { waitUntil: 'networkidle' });
  await clickChoice('new-campaign');
  await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'campaignMapSelect');
  await clickChoice('campaign-world:jade-karst');
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
  assert.equal(start.adventureWorldId, 'jade-karst');
  assert.equal(start.adventure.atTown, false);
  assert.equal(start.settings.reducedMotion, false);
  const world = worlds.find(row => row.id === start.adventureWorldId);
  const geometry = adventureGeometryForWorld(contract.geometry.adventure, world, start.seed);
  const map = adventureMap(geometry);
  const crossing = geometry.bridges.find(row => row.id === 'jade-karst-west-bridge-4-6');
  assert.ok(crossing, 'current Jade Karst bridge is registered');
  const [nearBank, farBank] = crossing.approaches;
  const approachRoute = routeTo(map, [start.adventure.x, start.adventure.y], nearBank);
  assert.ok(approachRoute.cost <= start.adventure.moves, 'visible daily movement reaches the bridge approach');
  report.sourceGeometry = {
    mapFile: world.mapFile,
    referenceFile: world.file,
    worldToSource: geometry.worldToSource,
    bridge: crossing,
    blockedCellsIncludeBridgeDeck: crossing.cells.every(([x, y]) => geometry.blocked.some(cell => cell[0] === x && cell[1] === y)),
  };
  assert.equal(report.sourceGeometry.blockedCellsIncludeBridgeDeck, true);
  report.start = { position: [start.adventure.x, start.adventure.y], moves: start.adventure.moves, revision: start.revision };
  report.approachRoute = approachRoute;

  await previewCell(nearBank);
  let preview = await routeView();
  assert.equal(preview.destinationCount, 1);
  assert.match(preview.status, /Cost\s+\d+/);
  assert.deepEqual([preview.state.adventure.x, preview.state.adventure.y], [start.adventure.x, start.adventure.y]);
  assert.equal(preview.state.adventure.moves, start.adventure.moves, 'preview does not spend movement');
  await saveCapture('jade-karst-bridge-approach-preview-1280x720.jpg');
  await confirmVisibleRoute();
  let moved = await committedState();
  assert.deepEqual([moved.adventure.x, moved.adventure.y], nearBank);
  await page.waitForFunction(() => document.querySelector('#world [data-mount="horse"]')?.getAttribute('data-moving') === '0', null, { timeout: 5000 });
  report.approachMove = {
    position: [moved.adventure.x, moved.adventure.y],
    moves: moved.adventure.moves,
    cost: approachRoute.cost,
    visited: moved.adventure.visited,
  };

  const crossingRoute = routeTo(map, nearBank, farBank);
  assert.deepEqual(crossingRoute.cells.filter(([x, y]) => crossing.cells.some(cell => cell[0] === x && cell[1] === y)),
    crossing.cells, 'legal visible route traverses the full registered bridge deck in order');
  if (crossingRoute.cost > moved.adventure.moves) {
    await clickChoice('adventure-end-day');
    moved = await committedState();
  }
  assert.ok(crossingRoute.cost <= moved.adventure.moves, 'movement refresh makes the full bridge route available');
  report.crossingRoute = crossingRoute;

  await previewCell(farBank);
  preview = await routeView();
  assert.equal(preview.destinationCount, 1);
  assert.match(preview.status, /Cost\s+\d+/);
  assert.deepEqual([preview.state.adventure.x, preview.state.adventure.y], nearBank, 'preview leaves the traveler on the near bank');
  assert.ok(preview.state.adventure.moves >= crossingRoute.cost);
  await saveCapture('jade-karst-bridge-full-route-preview-1280x720.jpg');

  await page.locator('#panel-close').click();
  await page.waitForFunction(() => !document.querySelector('#panel')?.classList.contains('open'));
  await page.setViewportSize({ width: 825, height: 375 });
  await page.waitForFunction(() => {
    const frame = document.querySelector('#frame')?.getBoundingClientRect();
    return frame && Math.abs(frame.x) < 1 && Math.abs(frame.width - 825) < 1;
  }, null, { timeout: 10000 });
  await saveCapture('jade-karst-bridge-route-phone-825x375.jpg');

  await confirmVisibleRoute();
  await page.waitForFunction(position => {
    const state = window.rebornSnapshot?.();
    return state && state.adventure?.x === position[0] && state.adventure?.y === position[1];
  }, farBank, { timeout: 10000 });
  const crossingState = await page.evaluate(() => window.rebornSnapshot?.());
  assert.equal(crossingState.settings.reducedMotion, false);
  report.crossingCommit = {
    position: [crossingState.adventure.x, crossingState.adventure.y],
    moves: crossingState.adventure.moves,
    visited: crossingState.adventure.visited,
    revision: crossingState.revision,
  };

  const samplePromise = page.evaluate(() => new Promise(resolve => {
    const samples = [];
    const began = performance.now();
    function sample(now) {
      const marker = document.querySelector('#world [data-map-marker="traveler"]');
      const mount = document.querySelector('#world [data-mount="horse"]');
      samples.push({
        elapsedMs: Math.round(now - began),
        marker: marker ? [Number(marker.getAttribute('cx')), Number(marker.getAttribute('cy')) + 8] : null,
        mode: document.querySelector('#world')?.getAttribute('data-adventure-traveler-mode') || null,
        moving: mount?.getAttribute('data-moving') || null,
        gait: mount?.getAttribute('data-gait') || null,
        mountTransform: mount?.getAttribute('transform') || null,
        hooves: mount ? [...mount.querySelectorAll('[data-joint^="hoof-"]')].map(node => ({
          joint: node.getAttribute('data-joint'),
          transform: node.getAttribute('transform'),
          pose: node.getAttribute('data-hoof'),
        })) : [],
      });
    if (now - began < 1500) requestAnimationFrame(sample);
      else resolve(samples);
    }
    requestAnimationFrame(sample);
  }));
  await page.waitForTimeout(80);
  await saveCapture('jade-karst-bridge-motion-120ms-825x375.jpg');
  await page.waitForTimeout(330);
  await saveCapture('jade-karst-bridge-motion-420ms-825x375.jpg');
  await page.waitForTimeout(330);
  await saveCapture('jade-karst-bridge-motion-720ms-825x375.jpg');
  const motionSamples = await samplePromise;
  report.motion = {
    frameCount: motionSamples.length,
    movingFrames: motionSamples.filter(row => row.moving === '1').length,
    mountedFrames: motionSamples.filter(row => row.mode === 'mounted' && row.gait === 'legged').length,
    distinctMarkerPositions: new Set(motionSamples.map(row => JSON.stringify(row.marker))).size,
    samples: motionSamples.filter((_, index) => index % 5 === 0),
  };
  assert.ok(report.motion.movingFrames >= 5, 'natural crossing includes multiple rendered moving frames');
  assert.ok(report.motion.mountedFrames >= 5, 'mounted traveler stays attached during the crossing');
  assert.ok(report.motion.distinctMarkerPositions >= 4, 'traveler interpolates along the committed crossing route');

  await committedState();
  await page.reload({ waitUntil: 'networkidle' });
  await page.waitForFunction(() => Boolean(window.rebornSnapshot?.()?.adventure), null, { timeout: 15000 });
  const reload = await page.evaluate(() => window.rebornSnapshot?.());
  assert.equal(reload.adventureWorldId, 'jade-karst');
  assert.deepEqual([reload.adventure.x, reload.adventure.y], farBank, 'far-bank position survives reload');
  assert.ok(reload.adventure.visited.includes(farBank.join(',')));
  report.reload = {
    worldId: reload.adventureWorldId,
    position: [reload.adventure.x, reload.adventure.y],
    moves: reload.adventure.moves,
    visited: reload.adventure.visited,
    revision: reload.revision,
    saveState: await page.locator('#save').getAttribute('data-save-state'),
  };
  await saveCapture('jade-karst-bridge-far-bank-after-reload-825x375.jpg');
  assert.deepEqual(report.errors, [], 'no browser or console errors');
  assert.deepEqual(report.failedResponses, [], 'no failed HTTP responses');
  report.passed = true;
} catch (error) {
  report.passed = false;
  report.failure = String(error?.stack || error);
} finally {
  report.finishedAt = new Date().toISOString();
  await fs.writeFile(path.join(output, 'report.json'), JSON.stringify(report, null, 2) + '\n');
  await context.close();
  await browser.close();
}

if (!report.passed) {
  console.error(report.failure);
  process.exitCode = 1;
} else {
  console.log(JSON.stringify({
    passed: report.passed,
    output: path.relative(root, output),
    approach: report.approachRoute,
    crossing: report.crossingRoute,
    motion: { frameCount: report.motion.frameCount, movingFrames: report.motion.movingFrames, mountedFrames: report.motion.mountedFrames, distinctMarkerPositions: report.motion.distinctMarkerPositions },
    reload: report.reload,
    captures: report.captures,
  }, null, 2));
}
