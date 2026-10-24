import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import worlds from '../../../src/data/adventure-worlds.json' with { type: 'json' };
import contract from '../../../src/data/implementation-contract.json' with { type: 'json' };
import { adventureGeometryForWorld, adventureMap } from '../../../src/core/navigation.js';

const root = process.cwd();
const url = 'http://127.0.0.1:4179/?audit=1';
const output = path.join(root, 'qa/game-completion-20261020/visual-review/adventure-all-worlds-label-clearance-live-20261020');
await fs.mkdir(output, { recursive: true });
const report = {
  recordedAt: new Date().toISOString(),
  classification: 'NATURAL_UI_ALL_CAMPAIGN_WORLDS',
  journey: 'For each of 12 worlds: new campaign -> select map -> enter valley -> leave town -> one legal move -> save/reload',
  url,
  note: 'Each world uses an isolated browser profile and visible controls. No campaign, selected world, map position, or movement state is injected.',
  results: [],
};

const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
async function clickChoice(page, id) {
  const control = page.locator(`[data-choice="${id}"]`).first();
  await control.waitFor({ state: 'visible', timeout: 10000 });
  assert.equal(await control.isDisabled(), false, `${id} is enabled`);
  await control.click();
}

for (const world of worlds) {
  const result = { worldId: world.id, errors: [], failedResponses: [] };
  const context = await browser.newContext({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1 });
  const page = await context.newPage();
  page.on('pageerror', error => result.errors.push(String(error)));
  page.on('console', message => { if (message.type() === 'error') result.errors.push(message.text()); });
  page.on('response', response => { if (response.status() >= 400) result.failedResponses.push({ status: response.status(), url: response.url() }); });
  try {
    await page.goto(url, { waitUntil: 'networkidle' });
    await clickChoice(page, 'new-campaign');
    await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'campaignMapSelect');
    await clickChoice(page, `campaign-world:${world.id}`);
    await clickChoice(page, 'begin-selected-world');
    await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'hero');
    await clickChoice(page, 'scene-class:knight');
    await clickChoice(page, 'scene-enter-valley');
    await page.waitForTimeout(100);
    await page.locator('#context').click();
    await clickChoice(page, 'site-list');
    await clickChoice(page, 'choose-site:townhall');
    await clickChoice(page, 'tutorial-toggle');
    await page.locator('[data-choice="nav:adventure"]').first().click();
    await page.locator('#dock [data-choice="inspect:adventure"]').click();
    await clickChoice(page, 'enter-adventure');
    await page.waitForFunction(() => Boolean(window.rebornSnapshot?.()?.adventure), null, { timeout: 15000 });

    const start = await page.evaluate(() => window.rebornSnapshot?.());
    assert.equal(start.adventureWorldId, world.id, 'selected world is saved in the campaign');
    assert.equal(start.adventure.atTown, false, 'the hero entered Adventure');
    await page.waitForFunction(() => {
      const image = document.querySelector('#terrain');
      return image?.complete && image.naturalWidth > 0;
    }, null, { timeout: 15000 });
    const image = await page.evaluate(() => ({
      source: new URL(document.querySelector('#terrain').getAttribute('src'), document.baseURI).pathname,
      width: document.querySelector('#terrain').naturalWidth,
      height: document.querySelector('#terrain').naturalHeight,
      world: document.querySelector('#world').dataset.adventureWorldId,
      renderModel: document.querySelector('#world').dataset.adventureRenderModel,
    }));
    assert.equal(image.world, world.id, 'rendered map has the selected world ID');
    assert.ok(image.source.endsWith((world.mapFile || world.terrainFile).replaceAll('\\', '/')), 'rendered terrain file matches the selected world');
    assert.ok(image.width >= 1024 && image.height >= 500, 'full-size map artwork loaded');
    result.image = image;
    result.seed = start.seed;

    const geometry = adventureGeometryForWorld(contract.geometry.adventure, world, start.seed);
    const map = adventureMap(geometry);
    const directions = [['north', 0, -1], ['east', 1, 0], ['south', 0, 1], ['west', -1, 0]];
    const direction = directions.find(([, dx, dy]) => {
      const x = start.adventure.x + dx, y = start.adventure.y + dy;
      const key = `${x},${y}`;
      return !map.blocked.has(key) && !map.guards.has(key);
    });
    assert.ok(direction, 'a legal cardinal step is available from the town entrance');
    const [, dx, dy] = direction;
    const destination = [start.adventure.x + dx, start.adventure.y + dy];
    await clickChoice(page, `preview-${direction[0]}`);
    const confirm = page.locator('#choices [data-choice="confirm-route"]');
    await confirm.waitFor({ state: 'visible', timeout: 5000 });
    assert.equal(await confirm.isDisabled(), false, 'visible one-cell route can be confirmed');
    await confirm.click();
    await page.waitForFunction(revision => (window.rebornSnapshot?.()?.revision || 0) > revision, start.revision, { timeout: 10000 });
    const moved = await page.evaluate(() => window.rebornSnapshot?.());
    assert.equal(moved.adventure.x, destination[0], 'movement reached the visible route destination x');
    assert.equal(moved.adventure.y, destination[1], 'movement reached the visible route destination y');
    assert.ok(moved.adventure.visited.includes(destination.join(',')), 'moved cell became discovered');
    await page.waitForFunction(revision => window.rebornCommittedHead?.()?.revision >= revision
      && document.querySelector('#save')?.dataset.saveState === 'committed', moved.revision, { timeout: 15000 });
    result.move = { direction: direction[0], destination, movesLeft: moved.adventure.moves };
    await page.locator('#panel-close').click();
    await page.waitForFunction(() => !document.querySelector('#panel')?.classList.contains('open'));
    const capture = path.join(output, `${world.id}-1280x720.png`);
    await page.screenshot({ path: capture });
    result.capture = path.relative(root, capture);

    await page.reload({ waitUntil: 'networkidle' });
    await page.waitForFunction(() => Boolean(window.rebornSnapshot?.()), null, { timeout: 15000 });
    let reloaded = await page.evaluate(() => window.rebornSnapshot?.());
    if (await page.locator('#app').getAttribute('data-view') === 'home') {
      await clickChoice(page, 'continue');
      await page.waitForFunction(() => document.querySelector('#app')?.dataset.view !== 'home');
      reloaded = await page.evaluate(() => window.rebornSnapshot?.());
    }
    assert.equal(reloaded.adventureWorldId, world.id, 'selected map survived reload');
    assert.deepEqual([reloaded.adventure.x, reloaded.adventure.y], destination, 'route position survived reload');
    assert.ok(reloaded.adventure.visited.includes(destination.join(',')), 'discovered terrain survived reload');
    result.reload = { worldId: reloaded.adventureWorldId, position: [reloaded.adventure.x, reloaded.adventure.y], revision: reloaded.revision };
    assert.deepEqual(result.errors, [], 'no browser errors');
    assert.deepEqual(result.failedResponses, [], 'no failed browser responses');
    result.passed = true;
  } catch (error) {
    result.passed = false;
    result.failure = String(error);
  } finally {
    report.results.push(result);
    await context.close();
  }
}

await browser.close();
report.recordedAt = new Date().toISOString();
report.passed = report.results.length === worlds.length && report.results.every(result => result.passed);
await fs.writeFile(path.join(output, 'report.json'), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify({ passed: report.passed, worlds: report.results.length, failures: report.results.filter(result => !result.passed), report: path.relative(root, path.join(output, 'report.json')) }, null, 2));
if (!report.passed) process.exitCode = 1;
