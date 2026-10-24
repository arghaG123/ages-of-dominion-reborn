import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import worlds from '../../../src/data/adventure-worlds.json' with { type: 'json' };
import contract from '../../../src/data/implementation-contract.json' with { type: 'json' };
import { adventureGeometryForWorld, adventureMap } from '../../../src/core/navigation.js';

const root = process.cwd();
const output = path.join(root, 'qa/game-completion-20261021/visual-review/adventure-fog-repair-live-20261021');
const url = 'http://127.0.0.1:4179/?audit=1';
await fs.mkdir(output, { recursive: true });
const report = {
  recordedAt: new Date().toISOString(),
  classification: 'NATURAL_GRASSLANDS_FOG_REPAIR_WITH_LEGAL_MOVE_AND_RELOAD',
  journey: 'Fresh UI campaign -> choose Grasslands -> enter Adventure -> inspect fog -> legal one-cell move -> save/reload',
  note: 'Campaign state is created and changed through visible controls. Snapshot reads are assertions only; no campaign, visited cells, route, or movement state is injected.',
  url,
  errors: [],
  failedResponses: [],
};

const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
const context = await browser.newContext({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1 });
const page = await context.newPage();
page.on('pageerror', error => report.errors.push(String(error)));
page.on('console', message => { if (message.type() === 'error') report.errors.push(message.text()); });
page.on('response', response => { if (response.status() >= 400) report.failedResponses.push({ status: response.status(), url: response.url() }); });

async function clickChoice(id) {
  const control = page.locator('[data-choice="' + id + '"]').first();
  await control.waitFor({ state: 'visible', timeout: 10000 });
  assert.equal(await control.isDisabled(), false, id + ' is enabled');
  await control.click();
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

  const initialFog = await page.evaluate(() => {
    const fog = document.querySelector('#world .fog');
    const style = fog ? getComputedStyle(fog) : null;
    return {
      fill: style?.fill || '',
      fillOpacity: style?.fillOpacity || '',
      mask: fog?.getAttribute('mask') || '',
      state: fog?.getAttribute('data-fog-state') || '',
      visitedCells: window.rebornSnapshot?.()?.adventure?.visited?.length || 0,
      world: document.querySelector('#world')?.getAttribute('data-adventure-world-id') || '',
    };
  });
  assert.equal(initialFog.fill, 'rgba(16, 23, 27, 0.82)', 'unvisited map cells use the strengthened fog veil');
  assert.equal(initialFog.state, 'saved-unvisited');
  assert.equal(initialFog.world, 'grasslands');
  assert.ok(initialFog.visitedCells > 0 && initialFog.visitedCells < 160, 'only a small part of the 16x10 map is explored');
  report.initialFog = initialFog;

  if (await page.locator('#panel-close').isVisible()) await page.locator('#panel-close').click();
  await page.waitForFunction(() => !document.querySelector('#panel')?.classList.contains('open'));
  let capture = path.join(output, 'grasslands-fog-1280x720.png');
  await page.screenshot({ path: capture });
  report.captures = [path.relative(root, capture)];

  await page.setViewportSize({ width: 825, height: 375 });
  await page.waitForTimeout(150);
  capture = path.join(output, 'grasslands-fog-825x375.png');
  await page.screenshot({ path: capture });
  report.captures.push(path.relative(root, capture));
  await page.setViewportSize({ width: 1280, height: 720 });
  await page.waitForTimeout(150);

  const geometry = adventureGeometryForWorld(contract.geometry.adventure, worlds.find(world => world.id === 'grasslands'), start.seed);
  const map = adventureMap(geometry);
  const directions = [['north', 0, -1], ['east', 1, 0], ['south', 0, 1], ['west', -1, 0]];
  const direction = directions.find(([, dx, dy]) => {
    const x = start.adventure.x + dx, y = start.adventure.y + dy;
    const key = x + ',' + y;
    return !map.blocked.has(key) && !map.guards.has(key);
  });
  assert.ok(direction, 'legal cardinal step available');
  const [, dx, dy] = direction;
  const destination = [start.adventure.x + dx, start.adventure.y + dy];
  await clickChoice('preview-' + direction[0]);
  const confirm = page.locator('#choices [data-choice="confirm-route"]');
  await confirm.waitFor({ state: 'visible', timeout: 5000 });
  assert.equal(await confirm.isDisabled(), false);
  await confirm.click();
  await page.waitForFunction(revision => (window.rebornSnapshot?.()?.revision || 0) > revision, start.revision, { timeout: 10000 });
  const moved = await page.evaluate(() => window.rebornSnapshot?.());
  assert.deepEqual([moved.adventure.x, moved.adventure.y], destination);
  assert.ok(moved.adventure.visited.includes(destination.join(',')));
  await page.waitForFunction(revision => window.rebornCommittedHead?.()?.revision >= revision
    && document.querySelector('#save')?.dataset.saveState === 'committed', moved.revision, { timeout: 15000 });
  report.move = { direction: direction[0], destination, movesLeft: moved.adventure.moves, visitedCells: moved.adventure.visited.length };

  capture = path.join(output, 'grasslands-after-legal-move-1280x720.png');
  await page.screenshot({ path: capture });
  report.captures.push(path.relative(root, capture));
  await page.reload({ waitUntil: 'networkidle' });
  await page.waitForFunction(() => Boolean(window.rebornSnapshot?.()), null, { timeout: 15000 });
  let reloaded = await page.evaluate(() => window.rebornSnapshot?.());
  if (await page.locator('#app').getAttribute('data-view') === 'home') {
    await clickChoice('continue');
    await page.waitForFunction(() => document.querySelector('#app')?.dataset.view !== 'home');
    reloaded = await page.evaluate(() => window.rebornSnapshot?.());
  }
  assert.equal(reloaded.adventureWorldId, 'grasslands');
  assert.deepEqual([reloaded.adventure.x, reloaded.adventure.y], destination);
  assert.ok(reloaded.adventure.visited.includes(destination.join(',')));
  report.reload = {
    worldId: reloaded.adventureWorldId,
    position: [reloaded.adventure.x, reloaded.adventure.y],
    visitedCells: reloaded.adventure.visited.length,
    fogFill: await page.locator('#world .fog').evaluate(node => getComputedStyle(node).fill),
  };
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
