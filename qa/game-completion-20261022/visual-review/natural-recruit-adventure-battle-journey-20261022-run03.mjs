import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import contract from '../../../src/data/implementation-contract.json' with { type: 'json' };
import { adventureGeometryForWorld, adventureMap, routeTo } from '../../../src/core/navigation.js';
import adventureWorlds from '../../../src/data/adventure-worlds.json' with { type: 'json' };

const root = process.cwd();
const [viewportWidth, viewportHeight] = (process.argv[2] || '1280x720').split('x').map(Number);
assert.ok(Number.isInteger(viewportWidth) && Number.isInteger(viewportHeight) && viewportWidth >= 700 && viewportHeight >= 350, 'provide a landscape test viewport such as 825x375');
const heroClass = process.argv[3] || 'knight';
assert.ok(['knight', 'ranger', 'warlock', 'mage', 'paladin', 'barbarian', 'necromancer', 'healer'].includes(heroClass), 'provide a supported campaign hero class');
const outName = process.env.AOD_BATTLE_REVIEW_OUT || (heroClass !== 'knight' ? `natural-spell-cast-${heroClass}-${viewportWidth}x${viewportHeight}` : viewportWidth === 1280 && viewportHeight === 720 ? 'natural-recruit-adventure-battle' : `natural-recruit-adventure-battle-${viewportWidth}x${viewportHeight}`);
const out = path.join(root, 'qa/game-completion-20261022/visual-review', outName);
await fs.mkdir(out, { recursive: true });
const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
const context = await browser.newContext({ viewport: { width: viewportWidth, height: viewportHeight }, deviceScaleFactor: 1 });
const page = await context.newPage();
const errors = [];
const notFound = [];
page.on('pageerror', error => errors.push(String(error)));
page.on('console', message => { if (message.type() === 'error') errors.push({ text: message.text(), location: message.location() }); });
page.on('response', response => { if (response.status() === 404) notFound.push(response.url()); });
await page.route('**/favicon.ico', route => route.fulfill({ status: 204, body: '' }));
await page.goto('http://127.0.0.1:4179/', { waitUntil: 'networkidle' });
assert.equal(await page.locator('[data-choice="new-campaign"]').count(), 1, 'fresh profile exposes New Campaign');
await page.locator('[data-choice="new-campaign"]').click();
await page.locator('[data-choice="campaign-world:grasslands"]').click();
await page.locator('[data-choice="begin-selected-world"]').click();
await page.locator(`[data-choice="scene-class:${heroClass}"]`).click();
await page.locator('[data-choice="scene-enter-valley"]').click();
await page.waitForFunction(() => window.rebornSnapshot()?.age === 0 && document.querySelector('#app')?.dataset.view === 'kingdom');
const campaignId = await page.evaluate(() => window.rebornSnapshot().id);

let heroSpellbookCapture = null;
if (heroClass === 'warlock') {
  await page.locator('[data-choice="nav:hero"]').click();
  await page.locator('[data-choice="inspect:hero"]:visible').first().click();
  await page.locator('[data-choice="hero-tab:spells"]:visible').first().click();
  await page.locator('[data-choice="spell:arrow"]:visible').first().click();
  const arrowAccessibleName = await page.locator('[data-choice="spell:arrow"]:visible').first().getAttribute('aria-label');
  assert.match(arrowAccessibleName || '', /Magic Arrow/);
  heroSpellbookCapture = 'hero-spellbook.png';
  await page.screenshot({ path: path.join(out, heroSpellbookCapture) });
  await page.locator('[data-choice="nav:kingdom"]').click();
}

const emptyPlot = await page.evaluate(() => window.rebornSnapshot().plots.find(plot => plot.id !== 'townhall' && plot.level === 0)?.id);
assert.ok(emptyPlot, 'Kingdom has an empty site for Barracks');
await page.locator(`[data-choice="site:${emptyPlot}"]`).click();
await page.locator(`[data-choice="build-picker:${emptyPlot}"]`).click();
await page.locator(`[data-choice="build:${emptyPlot}:barracks"]`).click();
await page.locator('#build-commit').click();
await page.waitForFunction(id => {
  const plot = window.rebornSnapshot()?.plots.find(row => row.id === id);
  return plot?.type === 'barracks' && plot.level === 1 && !window.rebornSnapshot().buildJobs.some(job => job.plotId === id);
}, emptyPlot, { timeout: 20000 });
await page.waitForFunction(expectedId => {
  const state = window.rebornSnapshot();
  const head = window.rebornCommittedHead();
  return state?.id === expectedId && head?.campaignId === expectedId && head.revision >= state.revision;
}, campaignId, { timeout: 10000 });

await page.locator('[data-choice="nav:army"]').click();
await page.locator('[data-choice="inspect:army"]').click();
const beforeRecruit = await page.evaluate(() => window.rebornSnapshot());
const meleeBefore = beforeRecruit.army.find(stack => stack.kind === 'role' && stack.type === 'melee');
assert.ok(meleeBefore, 'starter Melee formation exists');
assert.equal(await page.locator('[data-choice="recruit:melee"]').isDisabled(), false, 'Barracks enables recruitment within starting resources');
await page.locator('[data-choice="recruit:melee"]').click();
await page.waitForFunction(count => window.rebornSnapshot()?.army.find(stack => stack.kind === 'role' && stack.type === 'melee')?.count === count + 5, meleeBefore.count, { timeout: 10000 });
const afterRecruit = await page.evaluate(() => window.rebornSnapshot());
assert.equal(afterRecruit.army.length, 2, 'recruitment reinforces the existing role stack');
assert.equal(afterRecruit.army.find(stack => stack.type === 'melee').count, meleeBefore.count + 5, 'five Melee units were recruited');
await page.screenshot({ path: path.join(out, 'army-after-recruit.png') });

await page.locator('[data-choice="nav:adventure"]').click();
assert.ok(await page.locator('[data-choice="enter-adventure"]').count() >= 1, 'Adventure offers a real leave-town action');
await page.locator('[data-choice="enter-adventure"]:visible').first().click();
await page.waitForFunction(() => Boolean(window.rebornSnapshot()?.adventure) && document.querySelector('#app')?.dataset.view === 'adventure');
const adventureStart = await page.evaluate(() => ({ ...window.rebornSnapshot().adventure }));
const campaignSeed = await page.evaluate(() => window.rebornSnapshot().seed);
const selectedWorld = adventureWorlds.find(world => world.id === 'grasslands');
const selectedGeometry = adventureGeometryForWorld(contract.geometry.adventure, selectedWorld, campaignSeed);
const map = adventureMap(selectedGeometry);
const routeOptions = [...map.guards].map(key => key.split(',').map(Number)).map(cell => {
  try { return { cell, ...routeTo(map, [adventureStart.x, adventureStart.y], cell) }; }
  catch { return null; }
}).filter(Boolean).sort((a, b) => a.cost - b.cost);
const targetRoute = routeOptions.find(route => route.cost <= adventureStart.moves);
assert.ok(targetRoute, 'No mapped guard is reachable this day: ' + JSON.stringify({ adventureStart, guards: [...map.guards], routeOptions, anchors: selectedGeometry.anchors }));
const [gx, gy] = targetRoute.destination;
const guardKey = `${gx},${gy}`;
const targetGuard = Object.entries(selectedGeometry.anchors).find(([id, cell]) => id.startsWith('guard-') && `${Math.floor(cell[0])},${Math.floor(cell[1])}` === guardKey)?.[0];
assert.ok(targetGuard, `The naturally chosen guard cell ${guardKey} has a registered visual anchor`);
await page.locator(`[data-adventure-cell="${gx},${gy}"]`).click({ force: true });
await page.waitForFunction(() => {
  const node = document.querySelector('[data-choice="confirm-route"]');
  return node && !node.disabled;
}, null, { timeout: 5000 });
const routePreview = await page.evaluate(() => ({
  status: document.querySelector('[data-scene-status]')?.textContent || document.querySelector('#status')?.textContent,
  destination: [...document.querySelectorAll('[data-choice="confirm-route"]')].map(node => ({ text: node.textContent, title: node.title })),
}));
await page.locator('[data-choice="confirm-route"]:visible').first().click();
await page.waitForFunction(() => window.rebornSnapshot()?.adventure?.pendingEncounter?.status === 'UNRESOLVED', null, { timeout: 10000 });
const encounter = await page.evaluate(() => ({
  adventure: window.rebornSnapshot().adventure,
  view: document.querySelector('#app')?.dataset.view,
}));
assert.deepEqual([encounter.adventure.x, encounter.adventure.y], targetRoute.destination, 'route confirmation moves the hero to the chosen guard');
assert.equal(encounter.adventure.pendingEncounter.cell.join(','), targetRoute.destination.join(','), 'guard encounter occurs at the destination');
const staleSpawnMarkerBefore = await page.locator('#world [data-adventure-anchor="hero"]').count();
assert.equal(staleSpawnMarkerBefore, 0, 'the fixed spawn anchor is hidden once the live traveler is rendered');
const guardMarkerBefore = await page.locator(`#world [data-adventure-anchor="${targetGuard}"]`).count();
assert.equal(guardMarkerBefore, 1, 'the discovered unresolved guard has one world marker before battle');
const minimapGuardBefore = await page.locator(`[data-point-of-interest="${targetGuard}"]`).count();
assert.equal(minimapGuardBefore, 1, 'the discovered unresolved guard has one minimap marker before battle');
await page.waitForTimeout(1800); // Let the live travel motion finish before judging the visual position.
await page.screenshot({ path: path.join(out, 'adventure-guard-encounter.png') });

await page.locator('[data-choice="begin-encounter"]:visible').first().click();
await page.waitForFunction(() => Boolean(window.rebornSnapshot()?.battle) && document.querySelector('#app')?.dataset.view === 'tactical');
const battleStart = await page.evaluate(() => window.rebornSnapshot().battle);
assert.ok(battleStart.stacks.some(stack => stack.side === 'p') && battleStart.stacks.some(stack => stack.side === 'e'), 'encounter creates both allied and enemy formations');
await page.screenshot({ path: path.join(out, 'tactical-encounter-start.png') });
const activeBeforeMove = await page.evaluate(() => {
  const battle = window.rebornSnapshot().battle;
  const id = battle.queue.find(candidate => {
    const stack = battle.stacks.find(item => item.id === candidate);
    return stack && !stack.dead && !stack.acted;
  });
  return { id, actor: battle.stacks.find(stack => stack.id === id), enemies: battle.stacks.filter(stack => stack.side === 'e' && !stack.dead) };
});
assert.equal(activeBeforeMove.actor.side, 'p', 'natural encounter begins with an allied turn');
let spellCast = null;
if (heroClass === 'warlock') {
  const manaBeforeSpell = await page.evaluate(() => window.rebornSnapshot().battle.mana);
  assert.equal(await page.locator('[data-choice="intent:spell"]:visible').first().isDisabled(), false, 'Warlock has an affordable battle spell');
  await page.locator('[data-choice="intent:spell"]:visible').first().click();
  await page.waitForFunction(() => document.querySelector('[data-choice^="spellcast:arrow:"]'), null, { timeout: 5000 });
  const spellChoice = await page.locator('[data-choice^="spellcast:arrow:"]:visible').first().getAttribute('data-choice');
  assert.ok(spellChoice, 'Magic Arrow exposes an enemy target');
  await page.locator(`[data-choice="${spellChoice}"]:visible`).first().click();
  await page.waitForFunction(mana => {
    const battle = window.rebornSnapshot()?.battle;
    return battle?.castThisRound && battle.mana === mana - 5 && battle.log?.at(-1)?.type === 'spell' && battle.log.at(-1).id === 'arrow';
  }, manaBeforeSpell, { timeout: 10000 });
  spellCast = await page.evaluate(() => ({ mana: window.rebornSnapshot().battle.mana, lastAction: window.rebornSnapshot().battle.log.at(-1) }));
  await page.waitForTimeout(500);
  await page.screenshot({ path: path.join(out, 'tactical-after-magic-arrow.png') });
  await page.locator('#panel-close:visible').click();
}
await page.locator('[data-choice="intent:move"]:visible').first().click();
await page.locator('[data-choice="inspect:tactical"]:visible').first().click();
await page.waitForFunction(() => document.querySelector('[data-choice^="move:"]'), null, { timeout: 5000 });
const availableMoves = await page.locator('[data-choice^="move:"]:visible').evaluateAll(nodes => nodes.map(node => node.dataset.choice.slice(5).split(',').map(Number)));
assert.ok(availableMoves.length > 0, 'Move intent exposes legal destinations');
const targetMove = availableMoves.map(cell => ({ cell, distance: Math.min(...activeBeforeMove.enemies.map(enemy => Math.max(Math.abs(cell[0] - enemy.x), Math.abs(cell[1] - enemy.y)))) })).sort((a, b) => a.distance - b.distance)[0].cell;
await page.locator(`[data-choice="move:${targetMove[0]},${targetMove[1]}"]:visible`).first().click();
await page.waitForFunction(({ id, cell }) => {
  const stack = window.rebornSnapshot()?.battle?.stacks.find(item => item.id === id);
  return stack?.x === cell[0] && stack?.y === cell[1];
}, { id: activeBeforeMove.id, cell: targetMove }, { timeout: 10000 });
await page.screenshot({ path: path.join(out, 'tactical-after-manual-move.png') });
await page.waitForFunction(() => window.rebornSnapshot()?.battle?.pendingSettlement || document.querySelector('[data-choice="auto"]'), null, { timeout: 15000 });
if (!await page.evaluate(() => window.rebornSnapshot()?.battle?.pendingSettlement)) {
  await page.locator('[data-choice="auto"]:visible').first().click();
  await page.waitForFunction(() => window.rebornSnapshot()?.battle?.pendingSettlement, null, { timeout: 20000 });
}
const pendingBattle = await page.evaluate(() => window.rebornSnapshot().battle);
assert.ok(pendingBattle.pendingSettlement, 'the Tactical auto-resolve action reaches a settlement result');
await page.screenshot({ path: path.join(out, 'tactical-result-before-settlement.png') });
const winner = pendingBattle.outcome?.winner;
assert.equal(winner, 'p', 'the recruited natural party defeats the reachable Adventure guard');
await page.locator('[data-choice="result:tactical"]:visible').first().click();
await page.waitForFunction(() => !window.rebornSnapshot()?.battle, null, { timeout: 10000 });
const postBattle = await page.evaluate(() => ({ state: window.rebornSnapshot(), head: window.rebornCommittedHead() }));
if (winner === 'p') {
  assert.equal(postBattle.state.adventure.pendingEncounter, null, 'victory resolves the guard');
  assert.ok(postBattle.state.story.flags[`cleared:${pendingBattle.encounterId}`], 'victory persists the cleared encounter flag');
  assert.ok(postBattle.state.adventure.resolvedGuards.includes(guardKey), 'victory persists the resolved guard grid key');
}
const guardMarkerAfter = await page.locator(`#world [data-adventure-anchor="${targetGuard}"]`).count();
assert.equal(guardMarkerAfter, 0, 'settling victory removes the resolved guard from the world map');
const minimapGuardAfter = await page.locator(`[data-point-of-interest="${targetGuard}"]`).count();
assert.equal(minimapGuardAfter, 0, 'settling victory removes the resolved guard from the minimap');
await page.waitForFunction(expectedId => {
  const state = window.rebornSnapshot();
  const head = window.rebornCommittedHead();
  return state?.id === expectedId && head?.campaignId === expectedId && head.revision >= state.revision;
}, campaignId, { timeout: 10000 });
await page.reload({ waitUntil: 'networkidle' });
await page.waitForFunction(({ id }) => {
  const state = window.rebornSnapshot();
  const head = window.rebornCommittedHead();
  return state?.id === id && !state.battle && head?.campaignId === id && head.revision >= state.revision;
}, { id: campaignId }, { timeout: 10000 });
const reloaded = await page.evaluate(() => window.rebornSnapshot());
assert.equal(reloaded.age, 0, 'age survives browser reload');
assert.equal(reloaded.army.find(stack => stack.type === 'melee').count, postBattle.state.army.find(stack => stack.type === 'melee').count, 'settled post-battle formation survives browser reload');
assert.ok(!reloaded.battle, 'settled battle remains closed after reload');
assert.ok(reloaded.adventure.resolvedGuards.includes(guardKey), 'resolved guard state survives browser reload');
await page.locator('[data-choice="nav:adventure"]').click();
const resumeAdventure = page.locator('[data-choice="enter-adventure"]:visible').first();
if (await resumeAdventure.count()) await resumeAdventure.click();
await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'adventure');
const guardMarkerAfterReload = await page.locator(`#world [data-adventure-anchor="${targetGuard}"]`).count();
assert.equal(guardMarkerAfterReload, 0, 'the resolved guard stays hidden when the Adventure map is reopened after reload');
const staleSpawnMarkerAfterReload = await page.locator('#world [data-adventure-anchor="hero"]').count();
assert.equal(staleSpawnMarkerAfterReload, 0, 'the fixed spawn anchor does not return after reload');
const minimapGuardAfterReload = await page.locator(`[data-point-of-interest="${targetGuard}"]`).count();
assert.equal(minimapGuardAfterReload, 0, 'the resolved guard stays hidden on the minimap after reload');
await page.screenshot({ path: path.join(out, 'adventure-after-battle-reload.png') });
assert.deepEqual(errors, [], 'no browser runtime errors');
assert.deepEqual(notFound, [], 'no missing requests');
const report = {
  recordedAt: new Date().toISOString(),
  classification: 'NATURAL_UI_BROWSER_JOURNEY_FRESH_PROFILE_BUILD_RECRUIT_ADVENTURE_TACTICAL_AND_RELOAD_NOT_FULL_JOURNEY_OR_OWNER_ACCEPTANCE',
  viewport: `${viewportWidth}x${viewportHeight}`,
  route: `fresh isolated profile -> new ${heroClass} campaign -> ${heroSpellbookCapture ? 'inspect spellbook -> ' : ''}build Barracks -> recruit 5 Melee -> leave town -> preview and confirm guard route -> Tactical ${spellCast ? 'cast Magic Arrow -> ' : ''}manual Move -> UI auto-resolve remainder -> settle -> durable acknowledgement -> reload`,
  campaignId,
  construction: { plotId: emptyPlot, building: 'barracks', level: 1 },
  recruitment: { before: meleeBefore.count, after: afterRecruit.army.find(stack => stack.type === 'melee').count, armyStacks: afterRecruit.army.length },
  adventure: { start: adventureStart, route: { destination: targetRoute.destination, cost: targetRoute.cost, cells: targetRoute.cells }, guardId: targetGuard, guardKey, markerCounts: { staleSpawnBeforeBattle: staleSpawnMarkerBefore, worldBeforeBattle: guardMarkerBefore, minimapBeforeBattle: minimapGuardBefore, worldAfterSettlement: guardMarkerAfter, minimapAfterSettlement: minimapGuardAfter, worldAfterReload: guardMarkerAfterReload, staleSpawnAfterReload: staleSpawnMarkerAfterReload, minimapAfterReload: minimapGuardAfterReload }, preview: routePreview, encounter: encounter.adventure.pendingEncounter, resolvedGuards: reloaded.adventure.resolvedGuards },
  battle: { id: battleStart.id, encounterId: battleStart.encounterId, winner, pendingSettlement: pendingBattle.pendingSettlement, afterSettlementOpen: Boolean(postBattle.state.battle), settledMeleeCount: postBattle.state.army.find(stack => stack.type === 'melee').count, persistedMeleeCount: reloaded.army.find(stack => stack.type === 'melee').count },
  manualMove: { activeStackId: activeBeforeMove.id, start: [activeBeforeMove.actor.x, activeBeforeMove.actor.y], destination: targetMove, legalChoiceCount: availableMoves.length },
  spellCast,
  screenshots: [...(heroSpellbookCapture ? [heroSpellbookCapture] : []), 'army-after-recruit.png', 'adventure-guard-encounter.png', 'tactical-encounter-start.png', ...(spellCast ? ['tactical-after-magic-arrow.png'] : []), 'tactical-after-manual-move.png', 'tactical-result-before-settlement.png', 'adventure-after-battle-reload.png'],
  errors,
  notFound,
};
await fs.writeFile(path.join(out, 'report.json'), JSON.stringify(report, null, 2));
console.log(JSON.stringify(report, null, 2));
await context.close();
await browser.close();
