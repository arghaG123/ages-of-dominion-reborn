import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import worlds from '../../../src/data/adventure-worlds.json' with { type: 'json' };
import contract from '../../../src/data/implementation-contract.json' with { type: 'json' };
import { adventureGeometryForWorld, adventureMap } from '../../../src/core/navigation.js';
import { visibleAdventureAnchors } from '../../../src/client/screen-presentation.js';

const root = process.cwd();
const siteId = process.argv[2] || 'mine';
assert.ok(['ruin', 'mill', 'mine'].includes(siteId), `supported claimable site: ${siteId}`);
const runId = process.argv[3] || 'run01';
assert.match(runId, /^run\d{2}$/, 'run id has the form runNN');
const output = path.join(root, `qa/game-completion-20261021/visual-review/adventure-${siteId}-natural-live-20261021-${runId}`);
const url = 'http://127.0.0.1:4179/?audit=1';
await fs.mkdir(output, { recursive: true });
const report = {
  recordedAt: new Date().toISOString(),
  classification: `NATURAL_GRASSLANDS_${siteId.toUpperCase()}_CLAIM_ON_FOOT_SAVE_RELOAD`,
  journey: `Fresh visible Grasslands campaign -> cardinal route to ${siteId} approach -> on-foot arrival -> claim offer -> save/reload`,
  note: 'Campaign, position, and resources are never injected. A read-only path search excludes unresolved guards; each move and the claim use visible game controls. SVG actor DOM bounds include transparent source-image margins, so on-foot visibility is reviewed in the saved pixels rather than inferred from that rectangle.',
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
const directions = [
  { id: 'north', dx: 0, dy: -1 },
  { id: 'east', dx: 1, dy: 0 },
  { id: 'south', dx: 0, dy: 1 },
  { id: 'west', dx: -1, dy: 0 },
];
const key = cell => `${cell[0]},${cell[1]}`;

async function clickChoice(id) {
  const control = page.locator(`[data-choice="${id}"]`).first();
  await control.waitFor({ state: 'visible', timeout: 10000 });
  assert.equal(await control.isDisabled(), false, `${id} is enabled`);
  await control.click();
}

function cardinalPath(map, start, goal) {
  const origin = key(start), destination = key(goal);
  const queue = [start];
  const previous = new Map([[origin, null]]);
  for (let index = 0; index < queue.length && !previous.has(destination); index += 1) {
    const [x, y] = queue[index];
    for (const { dx, dy } of directions) {
      const next = [x + dx, y + dy], id = key(next);
      if (next[0] < 0 || next[1] < 0 || next[0] >= map.cols || next[1] >= map.rows) continue;
      if (map.blocked.has(id) || map.guards.has(id) || previous.has(id)) continue;
      previous.set(id, key([x, y]));
      queue.push(next);
    }
  }
  if (!previous.has(destination)) return null;
  const cells = [];
  let cursor = destination;
  while (cursor !== origin) {
    cells.push(cursor.split(',').map(Number));
    cursor = previous.get(cursor);
    if (cursor == null) throw new Error('Broken cardinal route');
  }
  return cells.reverse();
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
  await page.locator('#nav [data-choice="nav:adventure"]').first().click();
  await page.locator('#dock [data-choice="inspect:adventure"]').click();
  await clickChoice('enter-adventure');
  await page.waitForFunction(() => Boolean(window.rebornSnapshot?.()?.adventure), null, { timeout: 15000 });
  await page.waitForFunction(() => {
    const terrain = document.querySelector('#terrain');
    return terrain?.complete && terrain.naturalWidth > 0;
  }, null, { timeout: 15000 });

  const start = await page.evaluate(() => window.rebornSnapshot?.());
  assert.equal(start.adventureWorldId, 'grasslands');
  assert.equal(start.adventure.atTown, false);
  const world = worlds.find(row => row.id === start.adventureWorldId);
  const geometry = adventureGeometryForWorld(contract.geometry.adventure, world, start.seed);
  const map = adventureMap(geometry);
  const site = geometry.sites.find(row => row.id === siteId);
  assert.ok(site, `the selected map has a ${siteId} approach`);
  const destination = site.approach;
  const pathCells = cardinalPath(map, [start.adventure.x, start.adventure.y], destination);
  assert.ok(pathCells?.length, `the ${siteId} approach has a legal guard-free cardinal route`);
  const offerKey = siteId === 'ruin' ? 'ruinXp' : siteId === 'mill' ? 'millFood' : 'mineGold';
  report.start = { position: [start.adventure.x, start.adventure.y], moves: start.adventure.moves, revision: start.revision, seed: start.seed };
  report.site = { id: site.id, approach: destination, pathCells, pathLength: pathCells.length, offerKey, offer: start.adventure.siteOffers[offerKey] };

  await page.setViewportSize({ width: 825, height: 375 });
  await page.waitForTimeout(120);
  for (const next of pathCells) {
    let current = await page.evaluate(() => window.rebornSnapshot?.());
    if (current.adventure.moves < 1) {
      const beforeEnd = current.revision;
      await clickChoice('adventure-end-day');
      await page.waitForFunction(revision => window.rebornSnapshot?.()?.revision > revision
        && window.rebornSnapshot().adventure.moves > 0, beforeEnd, { timeout: 10000 });
      current = await page.evaluate(() => window.rebornSnapshot?.());
      await page.waitForFunction(revision => window.rebornCommittedHead?.()?.revision >= revision
        && document.querySelector('#save')?.dataset.saveState === 'committed', current.revision, { timeout: 15000 });
    }
    const direction = directions.find(item => item.dx === next[0] - current.adventure.x && item.dy === next[1] - current.adventure.y);
    assert.ok(direction, 'every route step is cardinal');
    assert.ok(current.adventure.moves >= 1, 'a movement point is available');
    const beforeMove = current.revision;
    await clickChoice(`preview-${direction.id}`);
    await page.locator('#choices [data-choice="confirm-route"]').waitFor({ state: 'visible', timeout: 5000 });
    await clickChoice('confirm-route');
    await page.waitForFunction(({ x, y, revision }) => {
      const state = window.rebornSnapshot?.();
      return state?.adventure?.x === x && state.adventure.y === y && state.revision > revision;
    }, { x: next[0], y: next[1], revision: beforeMove }, { timeout: 10000 });
    current = await page.evaluate(() => window.rebornSnapshot?.());
    await page.waitForFunction(revision => window.rebornCommittedHead?.()?.revision >= revision
      && document.querySelector('#save')?.dataset.saveState === 'committed', current.revision, { timeout: 15000 });
    report.steps.push({ position: next, moves: current.adventure.moves, day: current.day, revision: current.revision });
  }

  let reached = await page.evaluate(() => window.rebornSnapshot?.());
  assert.deepEqual([reached.adventure.x, reached.adventure.y], destination);
  await page.waitForFunction(() => document.querySelector('#world')?.dataset.adventureTravelerMode === 'on-foot', null, { timeout: 5000 });
  const traveler = await page.evaluate(() => {
    const world = document.querySelector('#world');
    const actor = world.querySelector('[data-actor], [data-mount]');
    const rect = actor?.getBoundingClientRect();
    const stage = document.querySelector('#stage').getBoundingClientRect();
    return {
      mode: world.dataset.adventureTravelerMode,
      actor: actor ? { kind: actor.hasAttribute('data-actor') ? 'actor' : 'mount', id: actor.getAttribute('data-actor') || actor.getAttribute('data-mount'), domBoundsIncludeTransparentSourceMargins: true, bounds: rect && { left: rect.left, top: rect.top, right: rect.right, bottom: rect.bottom }, visualReviewCaptureRequired: true, role: actor.getAttribute('role'), accessibleName: actor.getAttribute('aria-label') } : null,
    };
  });
  assert.equal(traveler.mode, 'on-foot');
  assert.ok(traveler.actor, `an Adventure traveler actor rendered at the ${siteId} approach`);
  assert.equal(traveler.actor.role, 'img');
  assert.equal(traveler.actor.accessibleName, 'Your hero on foot');
  const labelTexts = await page.locator('#labels span').allTextContents();
  assert.ok(!labelTexts.includes('Your hero'), 'the visible hero tag is omitted over the on-foot character');
  const minimapLabelCollisions = await page.evaluate(() => {
    const minimap = document.querySelector('#adventure-minimap');
    if (!minimap) return [];
    const map = minimap.getBoundingClientRect();
    return Array.from(document.querySelectorAll('#labels span')).map(label => {
      const rect = label.getBoundingClientRect();
      return { text: label.textContent, left: rect.left, top: rect.top, right: rect.right, bottom: rect.bottom };
    }).filter(label => label.left < map.right && label.right > map.left && label.top < map.bottom && label.bottom > map.top);
  });
  assert.deepEqual(minimapLabelCollisions, [], 'visible Adventure labels stay outside the minimap');
  const compactScale = await page.evaluate(() => JSON.parse(document.querySelector('#audit-snapshot')?.textContent || 'null')?.frame?.fit?.scale);
  const matrix = geometry.worldToSource;
  const project = (x, y) => [matrix[0] * x + matrix[2] * y + matrix[4], matrix[1] * x + matrix[3] * y + matrix[5]];
  const travelerPoint = project(reached.adventure.x + 0.5, reached.adventure.y + 0.5);
  const nearbyAnchors = visibleAdventureAnchors(geometry, reached.adventure).filter(point => {
    const anchorPoint = project(point.x, point.y);
    return Math.abs((anchorPoint[0] - travelerPoint[0]) * compactScale) < 96
      && Math.abs((anchorPoint[1] - travelerPoint[1]) * compactScale) < 150;
  });
  const anchorLabelText = point => point.kind === 'guard'
    ? (point.id === 'guard-ruin' ? 'Bandit patrol' : 'Wild creature pack')
    : `${point.id[0].toUpperCase()}${point.id.slice(1)} cache`;
  for (const point of nearbyAnchors) assert.ok(!labelTexts.includes(anchorLabelText(point)), `${anchorLabelText(point)} is hidden beside the traveler`);
  report.visualLabels = { visibleTexts: labelTexts, minimapLabelCollisions, nearbyAccessibleAnchors: nearbyAnchors.map(point => ({ id: point.id, label: anchorLabelText(point), visibleMarkerCount: 1 })), onFootHeroVisibleLabel: labelTexts.includes('Your hero'), onFootHeroAccessibleName: traveler.actor.accessibleName, compactScale };
  const claim = page.locator(`#choices [data-choice="claim-site:${siteId}"]`);
  await claim.waitFor({ state: 'visible', timeout: 5000 });
  const beforeClaim = reached;
  const amount = beforeClaim.adventure.siteOffers[offerKey];
  assert.equal(amount, report.site.offer);
  await clickChoice(`claim-site:${siteId}`);
  await page.waitForFunction(({ revision, siteId }) => {
    const state = window.rebornSnapshot?.();
    return state?.adventure?.claimedSites?.includes(siteId) && state.revision > revision;
  }, { revision: beforeClaim.revision, siteId }, { timeout: 10000 });
  reached = await page.evaluate(() => window.rebornSnapshot?.());
  await page.waitForFunction(revision => window.rebornCommittedHead?.()?.revision >= revision
    && document.querySelector('#save')?.dataset.saveState === 'committed', reached.revision, { timeout: 15000 });
  let grant;
  if (siteId === 'mine') {
    assert.equal(reached.resources.gold, beforeClaim.resources.gold + amount, 'Mine grant is exactly the saved gold offer');
    grant = { field: 'gold', before: beforeClaim.resources.gold, after: reached.resources.gold, amount: reached.resources.gold - beforeClaim.resources.gold };
  } else if (siteId === 'mill') {
    assert.equal(reached.resources.food, beforeClaim.resources.food + amount, 'Mill grant is exactly the saved food offer');
    grant = { field: 'food', before: beforeClaim.resources.food, after: reached.resources.food, amount: reached.resources.food - beforeClaim.resources.food };
  } else {
    const totalXp = hero => hero.xp + Array.from({ length: Math.max(0, hero.level - 1) }, (_, index) => (index + 1) * 140).reduce((sum, value) => sum + value, 0);
    const credited = totalXp(reached.hero) - totalXp(beforeClaim.hero);
    assert.equal(credited, amount, 'Ruin grant is exactly the saved XP offer at the fresh Hall level');
    grant = { field: 'heroXp', before: totalXp(beforeClaim.hero), after: totalXp(reached.hero), amount: credited, heroLevel: reached.hero.level, unspentPoints: reached.hero.points };
  }
  report.claim = { grant, offer: amount, claimedSites: reached.adventure.claimedSites, traveler, day: reached.day, revision: reached.revision };
  const screenshot = path.join(output, `grasslands-${siteId}-claimed-on-foot-825x375.jpg`);
  await page.screenshot({ path: screenshot, type: 'jpeg', quality: 84 });
  report.capture = path.relative(root, screenshot);

  await page.reload({ waitUntil: 'networkidle' });
  await page.waitForFunction(() => Boolean(window.rebornSnapshot?.()), null, { timeout: 15000 });
  let reloaded = await page.evaluate(() => window.rebornSnapshot?.());
  if (await page.locator('#app').getAttribute('data-view') === 'home') {
    await clickChoice('continue');
    await page.waitForFunction(() => document.querySelector('#app')?.dataset.view !== 'home');
    reloaded = await page.evaluate(() => window.rebornSnapshot?.());
  }
  if (await page.locator('#app').getAttribute('data-view') !== 'adventure') {
    await page.locator('#nav [data-choice="nav:adventure"]').click();
    await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'adventure');
  }
  if (!(await page.locator('#panel').evaluate(node => node.classList.contains('open')))) {
    await page.locator('#dock [data-choice="inspect:adventure"]').click();
    await page.waitForFunction(() => document.querySelector('#panel')?.classList.contains('open'));
  }
  assert.equal(reloaded.adventureWorldId, 'grasslands');
  assert.deepEqual([reloaded.adventure.x, reloaded.adventure.y], destination);
  assert.ok(reloaded.adventure.claimedSites.includes(siteId));
  if (siteId === 'mine') assert.equal(reloaded.resources.gold, beforeClaim.resources.gold + amount);
  else if (siteId === 'mill') assert.equal(reloaded.resources.food, beforeClaim.resources.food + amount);
  else assert.equal(reloaded.hero.xp + Array.from({ length: Math.max(0, reloaded.hero.level - 1) }, (_, index) => (index + 1) * 140).reduce((sum, value) => sum + value, 0), report.claim.grant.after);
  assert.equal(await page.locator(`#choices [data-choice="claim-site:${siteId}"]`).count(), 0);
  const claimedCopy = await page.locator('#choices').innerText();
  assert.match(claimedCopy, /already been explored/i, `the reopened ${siteId} is shown as already claimed`);
  report.reload = { position: [reloaded.adventure.x, reloaded.adventure.y], day: reloaded.day, resources: reloaded.resources, heroXp: reloaded.hero.xp, heroLevel: reloaded.hero.level, claimedSites: reloaded.adventure.claimedSites, repeatedClaimButtonCount: 0, claimedCopy, revision: reloaded.revision };
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
