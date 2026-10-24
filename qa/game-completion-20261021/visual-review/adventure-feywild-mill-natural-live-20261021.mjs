import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import worlds from '../../../src/data/adventure-worlds.json' with { type: 'json' };
import contract from '../../../src/data/implementation-contract.json' with { type: 'json' };
import { adventureGeometryForWorld, adventureMap, routeTo } from '../../../src/core/navigation.js';

const root = process.cwd();
const out = path.join(root, 'qa/game-completion-20261021/visual-review/adventure-feywild-mill-natural-live-20261021-run03');
const url = 'http://127.0.0.1:4179/?audit=1';
const target = [11, 7];
const expectedWater = [[3, 5], [10, 4], [11, 4], [11, 6], [12, 6], [1, 7], [0, 8], [10, 9], [11, 9]];
await fs.mkdir(out, { recursive: true });
const report = {
  recordedAt: new Date().toISOString(),
  classification: 'NATURAL_UI_FEYWILD_MILL_HOTSPOT_ROUTE_CLAIM_SAVE_RELOAD',
  journey: 'fresh visible campaign -> Feywild -> travel to pictured windmill -> claim provisions -> reload',
  note: 'Campaign state and travel are performed through visible UI controls. Geometry and snapshots are read-only assertions; no campaign state or position is injected.',
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

  const start = await page.evaluate(() => window.rebornSnapshot());
  assert.equal(start.adventureWorldId, 'feywild');
  const world = worlds.find(row => row.id === 'feywild');
  const geometry = adventureGeometryForWorld(contract.geometry.adventure, world, start.seed);
  const map = adventureMap(geometry);
  const mill = geometry.sites.find(site => site.id === 'mill');
  assert.deepEqual(mill.rect, [12, 7, 2, 2]);
  assert.deepEqual(mill.approach, target);
  assert.deepEqual(geometry.anchors.hero, [8.5, 5.5]);
  assert.deepEqual(geometry.blocked, expectedWater);
  const liveCells = await page.locator('#world [data-adventure-cell]').evaluateAll(nodes => Object.fromEntries(nodes.map(node => [
    node.getAttribute('data-adventure-cell'), node.getAttribute('data-open') === '1',
  ])));
  assert.equal(Object.keys(liveCells).length, 160);
  for (const [x, y] of expectedWater) assert.equal(liveCells[`${x},${y}`], false, `live cell ${x},${y} is blocked water`);
  for (let x = mill.rect[0]; x < mill.rect[0] + mill.rect[2]; x += 1) {
    for (let y = mill.rect[1]; y < mill.rect[1] + mill.rect[3]; y += 1) {
      assert.equal(liveCells[`${x},${y}`], false, `live windmill footprint ${x},${y} is protected`);
    }
  }

  const from = [start.adventure.x, start.adventure.y];
  const route = routeTo(map, from, target);
  assert.equal(route.cost, start.adventure.moves, 'the natural movement allowance reaches the mill approach in one day');
  const targetCell = page.locator(`#world [data-adventure-cell="${target.join(',')}"]`);
  await targetCell.click();
  await page.waitForFunction(() => Boolean(document.querySelector('#world [data-route-destination]')));
  const preview = await page.evaluate(() => window.rebornSnapshot());
  assert.deepEqual([preview.adventure.x, preview.adventure.y], from);
  assert.equal(preview.adventure.moves, start.adventure.moves);
  const previewCapture = path.join(out, 'feywild-windmill-route-preview-825x375.png');
  await page.screenshot({ path: previewCapture });
  report.previewCapture = path.relative(root, previewCapture);
  await clickChoice('confirm-route');
  await page.waitForFunction(([x, y]) => {
    const current = window.rebornSnapshot();
    return current?.adventure?.x === x && current?.adventure?.y === y;
  }, target);
  await page.waitForFunction(() => document.querySelector('#world')?.getAttribute('data-adventure-site-approach') === 'mill', null, { timeout: 10000 });
  await page.waitForFunction(() => document.querySelector('#world [data-site-id="mill"] polygon[data-site-hotspot="mill"]'));
  const arrived = await page.evaluate(() => ({
    state: window.rebornSnapshot(),
    hotspot: {
      site: document.querySelector('#world [data-site-id="mill"]')?.getAttribute('data-site-id'),
      artMode: document.querySelector('#world [data-site-id="mill"]')?.getAttribute('data-art-mode'),
      polygon: document.querySelector('#world [data-site-id="mill"] polygon[data-site-hotspot="mill"]')?.getAttribute('points'),
      travelerMode: document.querySelector('#world')?.getAttribute('data-adventure-traveler-mode'),
      approached: document.querySelector('#world')?.getAttribute('data-adventure-site-approach'),
    },
  }));
  assert.deepEqual([arrived.state.adventure.x, arrived.state.adventure.y], target);
  assert.equal(arrived.hotspot.site, 'mill');
  assert.equal(arrived.hotspot.artMode, 'map-hotspot');
  assert.equal(arrived.hotspot.travelerMode, 'on-foot');
  assert.equal(arrived.hotspot.approached, 'mill');
  const beforeClaim = arrived.state.resources.food;
  const reward = arrived.state.adventure.siteOffers.millFood;
  await clickChoice('inspect:adventure');
  await page.waitForFunction(() => document.querySelector('#panel')?.classList.contains('open'));
  await page.locator('[data-choice="claim-site:mill"]:visible').waitFor({ state: 'visible', timeout: 10000 });
  report.claimPanel = await page.evaluate(() => ({
    panelOpen: document.querySelector('#panel')?.classList.contains('open'),
    sheet: document.querySelector('#panel')?.dataset.sheet,
    claimLabel: document.querySelector('[data-choice="claim-site:mill"]')?.textContent,
  }));
  await clickChoice('claim-site:mill');
  await page.waitForFunction(() => window.rebornSnapshot()?.adventure?.claimedSites?.includes('mill'));
  const claimed = await page.evaluate(() => window.rebornSnapshot());
  assert.equal(claimed.resources.food, beforeClaim + reward);
  await page.waitForFunction(id => {
    const current = window.rebornSnapshot();
    const head = window.rebornCommittedHead();
    return current?.id === id && head?.campaignId === id && head.revision >= current.revision
      && document.querySelector('#save')?.dataset.saveState === 'committed';
  }, report.campaignId, { timeout: 15000 });
  report.arrival = { position: target, route: route.cells, cost: route.cost, movesRemaining: claimed.adventure.moves, hotspot: arrived.hotspot };
  report.claim = { site: 'mill', foodBefore: beforeClaim, reward, foodAfter: claimed.resources.food, claimedSites: claimed.adventure.claimedSites };
  const arrivalCapture = path.join(out, 'feywild-windmill-arrival-claimed-825x375.png');
  await page.screenshot({ path: arrivalCapture });
  report.captures = [path.relative(root, arrivalCapture)];

  await page.reload({ waitUntil: 'networkidle' });
  await page.waitForFunction(id => window.rebornSnapshot()?.id === id, report.campaignId, { timeout: 10000 });
  const reloaded = await page.evaluate(() => window.rebornSnapshot());
  assert.equal(reloaded.adventureWorldId, 'feywild');
  assert.deepEqual([reloaded.adventure.x, reloaded.adventure.y], target);
  assert.ok(reloaded.adventure.claimedSites.includes('mill'));
  assert.equal(reloaded.resources.food, claimed.resources.food);
  report.reload = { position: [reloaded.adventure.x, reloaded.adventure.y], food: reloaded.resources.food, claimedSites: reloaded.adventure.claimedSites };
  assert.deepEqual(report.errors, []);
  assert.deepEqual(report.failedResponses, []);
  report.result = 'PASS_BOUNDED_NATURAL_FEYWILD_MILL_HOTSPOT_CLAIM_SAVE_RELOAD; NOT_FULL_WORLD_OR_MOCK_ACCEPTANCE';
} catch (error) {
  report.result = 'FAIL';
  report.error = String(error?.stack || error);
  throw error;
} finally {
  await fs.writeFile(path.join(out, 'report.json'), JSON.stringify(report, null, 2));
  await browser.close();
}
