import test from 'node:test';
import assert from 'node:assert/strict';
import { discoveredSite, adventureMinimap, visibleAdventureAnchors, adventureTravelerMode, adventureAnchorLabelOverlapsTraveler, availableDwellingTypes, rosterSelection, canConfirmRoute, settlementStarted, shouldShowResumeNote, tutorialCueText, tutorialAnchorChoice, labelPositions, heroSkillStateCopy, defenseSummary, damagedSaveRecoveryCopy } from '../src/client/screen-presentation.js';
import contract from '../src/data/implementation-contract.json' with { type: 'json' };

test('the dwelling hides offer types already recorded in campaign history', () => {
  assert.deepEqual(availableDwellingTypes(['wolf', 'bandit', 'wolf'], [{ type: 'wolf', claimed: true }]), ['bandit']);
  assert.deepEqual(availableDwellingTypes(['wolf', 'bandit'], [{ type: 'wolf', claimed: false }]), ['bandit'], 'a fixed declined/cancelled offer cannot be rerolled');
  assert.deepEqual(availableDwellingTypes(['wolf'], []), ['wolf']);
  assert.deepEqual(availableDwellingTypes(['wolf'], null), ['wolf']);
});

test('the town stays recognizable while undiscovered adventure sites respect saved fog', () => {
  const sites = contract.geometry.adventure.sites;
  assert.equal(discoveredSite(sites.find(site => site.id === 'town'), null), true);
  for (const site of sites.filter(entry => entry.id !== 'town')) {
    assert.equal(discoveredSite(site, null), false);
    assert.equal(discoveredSite(site, { atTown: true, visited: [site.approach.join(',')] }), false);
    assert.equal(discoveredSite(site, { atTown: false, visited: [] }), false);
    assert.equal(discoveredSite(site, { atTown: false, visited: [site.approach.join(',')] }), true);
    assert.equal(discoveredSite(site, { atTown: false, visited: [`${site.rect[0]},${site.rect[1]}`] }), true);
  }
});

test('the guard tutorial explains how to find an encounter before asking the player to fight', () => {
  assert.equal(tutorialCueText(6, { view: 'adventure', onRoad: true, pendingEncounter: false }), 'Explore nearby roads to find a guard.');
  assert.equal(tutorialCueText(6, { view: 'adventure', onRoad: true, pendingEncounter: true }), 'Fight the guard.');
  assert.equal(tutorialCueText(6, { view: 'adventure', onRoad: false, pendingEncounter: false }), 'Fight the guard.');
  assert.equal(tutorialCueText(5, { view: 'adventure', onRoad: false }), 'Leave town.');
  assert.equal(tutorialCueText(6, { skipped: true }), '');
});

test('the building tutorial names the control that can be used now', () => {
  assert.equal(tutorialCueText(0, { view: 'kingdom' }), 'Select the highlighted empty site.');
  assert.equal(tutorialCueText(0, { view: 'kingdom', buildSiteSelected: true }), 'Choose a building.');
  assert.equal(tutorialCueText(0, { view: 'kingdom', buildPickerOpen: true }), 'Build a Lumber Camp.');
  assert.equal(tutorialCueText(1, { view: 'kingdom', buildSiteSelected: true, buildPickerOpen: true }), 'Build a Farm.');
  assert.equal(tutorialCueText(2, { view: 'kingdom', buildPickerOpen: true }), 'Build a Quarry.');
  assert.equal(tutorialCueText(3, { view: 'kingdom', buildPickerOpen: true }), 'Build a Barracks.');
  assert.equal(tutorialAnchorChoice(0, {}), '');
  assert.equal(tutorialAnchorChoice(0, { siteSelected: true }), 'build-picker:');
  assert.equal(tutorialAnchorChoice(0, { pickerOpen: true }), 'lumber');
  assert.equal(tutorialAnchorChoice(4, {}), 'muster-recruit:');
  assert.equal(tutorialAnchorChoice(5, {}), 'enter-adventure');
});

test('the adventure inset stays fog-bound and traces only a previewed route', () => {
  const geometry = contract.geometry.adventure;
  const approach = geometry.sites.find(site => site.id === 'town').approach;
  const next = [approach[0], approach[1] + 1];
  const target = [approach[0], approach[1] + 2];
  const minimap = adventureMinimap(geometry, {
    atTown: false,
    x: next[0],
    y: next[1],
    visited: [approach.join(','), next.join(',')],
  }, { cells: [target], cost: 1 });
  assert.deepEqual(minimap.player, { x: next[0] + 0.5, y: next[1] + 0.5 });
  assert.ok(minimap.exploredCells.some(cell => cell.x === next[0] && cell.y === next[1]));
  assert.ok(minimap.roadSegments.length > 0);
  assert.deepEqual(minimap.routeTrail.at(-1), { x: target[0] + 0.5, y: target[1] + 0.5 });
  assert.ok(minimap.landmarks.some(site => site.id === 'town'));
  assert.equal(minimap.landmarks.some(site => site.id === 'ruin'), false);
  const guardCell = geometry.anchors['guard-ruin'];
  const revealedGuard = adventureMinimap(geometry, {
    atTown: false,
    x: next[0],
    y: next[1],
    visited: [approach.join(','), next.join(','), `${Math.floor(guardCell[0])},${Math.floor(guardCell[1])}`],
  });
  assert.ok(revealedGuard.pointsOfInterest.some(point => point.id === 'guard-ruin' && point.kind === 'guard'));
  assert.equal(adventureMinimap(geometry, { atTown: true, visited: [] }), null);
});

test('resolved Adventure guards disappear from the world and minimap markers', () => {
  const geometry = contract.geometry.adventure;
  const guard = geometry.anchors['guard-mine'];
  const guardCell = `${Math.floor(guard[0])},${Math.floor(guard[1])}`;
  const heroAnchor = geometry.anchors.hero;
  const heroCell = `${Math.floor(heroAnchor[0])},${Math.floor(heroAnchor[1])}`;
  const visited = [heroCell, guardCell];
  const unresolved = { atTown: false, x: 10, y: 5, moves: 0, visited, resolvedGuards: [] };
  assert.ok(visibleAdventureAnchors(geometry, unresolved).some(point => point.id === 'guard-mine'));
  assert.equal(visibleAdventureAnchors(geometry, unresolved).some(point => point.id === 'hero'), false, 'the live traveler replaces the fixed spawn anchor');
  const unresolvedMap = adventureMinimap(geometry, unresolved);
  assert.ok(unresolvedMap.pointsOfInterest.some(point => point.id === 'guard-mine' && point.kind === 'guard'));
  assert.equal(unresolvedMap.pointsOfInterest.some(point => point.id === 'hero'), false);

  const resolved = { ...unresolved, resolvedGuards: [guardCell] };
  assert.equal(visibleAdventureAnchors(geometry, resolved).some(point => point.id === 'guard-mine'), false);
  assert.equal(adventureMinimap(geometry, resolved).pointsOfInterest.some(point => point.id === 'guard-mine'), false);
});

test('Adventure uses the on-foot hero at a committed site approach without changing travel rules', () => {
  const geometry = contract.geometry.adventure;
  for (const site of geometry.sites.filter(entry => entry.id !== 'town')) {
    assert.equal(adventureTravelerMode(geometry, { atTown: false, x: site.approach[0], y: site.approach[1] }), 'on-foot', `${site.id} approach shows the walking hero`);
  }
  const dwelling = geometry.sites.find(site => site.id === 'dwelling');
  const arrival = { atTown: false, x: dwelling.approach[0], y: dwelling.approach[1] };
  assert.equal(adventureTravelerMode(geometry, arrival, true), 'mounted', 'the rider remains mounted while a committed route is still animating');
  assert.equal(adventureTravelerMode(geometry, { ...arrival, pendingEncounter: { status: 'UNRESOLVED' } }), 'mounted', 'a guard encounter keeps the mounted traveler visible');
  assert.equal(adventureTravelerMode(geometry, { ...arrival, atTown: true }), 'mounted', 'town presentation does not inherit the on-foot site mode');
  assert.equal(adventureTravelerMode(geometry, { atTown: false, x: 8, y: 8 }), 'mounted', 'ordinary road travel remains mounted');
});

test('Adventure anchor labels stay off the traveler while retaining distant discoveries', () => {
  const matrix = contract.geometry.adventure.worldToSource;
  const project = ([x, y]) => [matrix[0] * x + matrix[2] * y + matrix[4], matrix[1] * x + matrix[3] * y + matrix[5]];
  const traveler = project([12.5, 7.5]);
  const diagonalCache = project([11.5, 6.5]);
  const distantCache = project([2.5, 1.5]);
  assert.equal(adventureAnchorLabelOverlapsTraveler(diagonalCache, traveler, 0.6), true, 'a cache beside the hero hides its overlapping name');
  assert.equal(adventureAnchorLabelOverlapsTraveler(distantCache, traveler, 0.6), false, 'distant cache labels remain visible');
  assert.equal(adventureAnchorLabelOverlapsTraveler(diagonalCache, traveler, 0), false, 'an invalid scale does not suppress labels');
});

test('stale roster selection follows retained entities without selecting an unavailable stack', () => {
  const army = [{ id: 'melee-old', age: 0 }, { id: 'archer-new', age: 3 }];
  assert.equal(rosterSelection(army, 'archer-new'), army[1]);
  assert.equal(rosterSelection(army.slice(0, 1), 'archer-new'), army[0]);
  assert.equal(rosterSelection([], 'archer-new'), null);
});

test('route preview confirmation requires a valid affordable movement cost', () => {
  assert.equal(canConfirmRoute(null, 5), false);
  assert.equal(canConfirmRoute({ cost: 4 }, 5), true);
  assert.equal(canConfirmRoute({ cost: 5 }, 5), true);
  assert.equal(canConfirmRoute({ cost: 6 }, 5), false);
  assert.equal(canConfirmRoute({ cost: -1 }, 5), false);
  assert.equal(canConfirmRoute({ cost: 2.5 }, 5), false);
  assert.equal(canConfirmRoute({ cost: 2 }, 2.5), false);
});

test('battle and Defense settlement closes the contextual panel before the result card renders', () => {
  assert.equal(settlementStarted({}, { battle: { pendingSettlement: true } }), true);
  assert.equal(settlementStarted({ battle: { pendingSettlement: true } }, { battle: { pendingSettlement: true } }), false);
  assert.equal(settlementStarted({}, { defense: { pendingSettlement: true } }), true);
  assert.equal(settlementStarted({}, { battle: { pendingSettlement: false }, defense: { pendingSettlement: false } }), false);
});

test('away-time report appears on the campaign gate instead of over a game screen', () => {
  assert.equal(shouldShowResumeNote('credited 0s', 'tactical', { battle: { pendingSettlement: true } }), false);
  assert.equal(shouldShowResumeNote('credited 0s', 'defense', { defense: { status: 'ACTIVE' } }), false);
  assert.equal(shouldShowResumeNote('credited 0s', 'kingdom', { battle: null, defense: null }), false);
  assert.equal(shouldShowResumeNote('credited 0s', 'home', {}), true);
  assert.equal(shouldShowResumeNote('credited 0s', 'home', { battle: { status: 'ACTIVE' } }), false);
  assert.equal(shouldShowResumeNote('', 'kingdom', {}), false);
});

test('crowded labels stay separated within the smallest landscape play area', () => {
  const rows = Array.from({ length: 6 }, (_, index) => ({ text: `Formation ${index}`, x: index % 2 ? 410 : 430, y: 140, priority: index === 4 ? 1 : 0 }));
  const labels = labelPositions(rows, 825, 375, () => ({ width: 130, height: 22 }));
  assert.equal(labels[0].text, 'Formation 4');
  for (const [index, label] of labels.entries()) {
    assert.ok(label.left >= 8 && label.left + label.width <= 817);
    assert.ok(label.top >= 60 && label.top + label.height <= 299);
    for (const other of labels.slice(index + 1)) assert.ok(label.top + label.height <= other.top || other.top + other.height <= label.top);
  }
});

test('defense HUD reports true phase, Endless clears and nonnegative core health', () => {
  assert.equal(defenseSummary(null).title, 'Prepare your defense');
  const session = { practice: 'endless', time: 0, clearedWaves: 12, waves: 16, core: 9.1, paused: true };
  assert.deepEqual(defenseSummary(session), { title: 'Prepare your defense', wave: '12 waves cleared', core: '10 gate HP' });
  assert.equal(defenseSummary({ ...session, time: 200 }).title, 'Paused');
  assert.equal(defenseSummary({ ...session, paused: false }).title, 'Hold the gate');
  assert.equal(defenseSummary({ ...session, status: 'ACTIVE', practice: 'siege', clearedWaves: 0, waves: 5, core: 400, paused: true, time: 0 }).wave, 'Wave 1 of 5');
  assert.equal(defenseSummary({ ...session, status: 'ACTIVE', practice: 'siege', clearedWaves: 2, waves: 5, core: 400, paused: true, time: 900 }).wave, 'Wave 3 of 5');
  assert.equal(defenseSummary({ ...session, status: 'ACTIVE', practice: 'endless', clearedWaves: 12, paused: false }).wave, 'Wave 13 · 12 cleared');
  assert.deepEqual(defenseSummary({ ...session, core: -3, pendingSettlement: true, winner: 'e' }), { title: 'Defeat', wave: '12 waves cleared', core: '0 gate HP' });
});

test('skill cards distinguish an active offer from learned ranks without inventing a lock', () => {
  assert.equal(heroSkillStateCopy(0, false), 'No active offer.');
  assert.equal(heroSkillStateCopy(0, true), 'Available to learn.');
  assert.equal(heroSkillStateCopy(1, true), 'Learned rank 1; rank 2 is available.');
  assert.equal(heroSkillStateCopy(2, false), 'Learned rank 2 of 3.');
  assert.equal(heroSkillStateCopy(3, false), 'Learned rank 3 of 3.');
});

test('damaged-save recovery only offers backup and export actions when those bytes exist', () => {
  const noRecoveryBytes = damagedSaveRecoveryCopy();
  assert.match(noRecoveryBytes, /import a valid local campaign/);
  assert.match(noRecoveryBytes, /start a new campaign/);
  assert.doesNotMatch(noRecoveryBytes, /backup|export/);
  const backupOnly = damagedSaveRecoveryCopy({ hasBackup: true });
  assert.match(backupOnly, /restore the valid backup/);
  assert.doesNotMatch(backupOnly, /export the damaged bytes/);
  const rawOnly = damagedSaveRecoveryCopy({ hasDamagedBytes: true });
  assert.match(rawOnly, /export the damaged bytes/);
  assert.doesNotMatch(rawOnly, /restore the valid backup/);
  const both = damagedSaveRecoveryCopy({ hasBackup: true, hasDamagedBytes: true });
  assert.match(both, /restore the valid backup/);
  assert.match(both, /export the damaged bytes/);
});

test('adventure destination labels sit below the artwork rather than covering the rider', () => {
  const labels = labelPositions([{ text: 'Your hero', x: 435, y: 126, placement: 'below', priority: 10 }, { text: 'Town', x: 430, y: 117, placement: 'below' }], 825, 375, () => ({ width: 64, height: 22 }));
  assert.ok(labels[0].top >= 134);
  assert.ok(labels[1].top >= labels[0].top + labels[0].height);
});

test('a site label flips above the traveler when the lower safe area is full', () => {
  const labels = labelPositions([
    { text: 'Your hero', x: 230, y: 284, placement: 'below', priority: 10 },
    { text: 'Wood cache', x: 230, y: 284, placement: 'below', priority: 9 },
  ], 825, 375, () => ({ width: 76, height: 18 }));
  assert.equal(labels.length, 2);
  assert.ok(labels.every(label => label.top >= 60 && label.top + label.height <= 299));
  assert.ok(labels[1].top + labels[1].height <= 284, 'the cache label moves above the shared hero/cache tile');
  assert.ok(labels[0].top + labels[0].height <= labels[1].top || labels[1].top + labels[1].height <= labels[0].top);
});

test('Adventure labels respect the visible bottom-dock clearance', () => {
  const labels = labelPositions([
    { text: 'Town', x: 90, y: 620, placement: 'below', safeBottom: 590 },
  ], 1280, 720, () => ({ width: 60, height: 20 }));
  assert.equal(labels.length, 1);
  assert.ok(labels[0].top >= 60);
  assert.ok(labels[0].top + labels[0].height <= 590);
  assert.ok(labels[0].top < 620, 'a landmark at the bottom edge flips above the map dock');
});

test('Adventure labels avoid the visible minimap when placing explored landmarks', () => {
  const minimap = { left: 14, top: 64, right: 146, bottom: 196 };
  const labels = labelPositions([
    { text: 'Ancient ruins · explored', x: 92, y: 140, placement: 'below', avoidRects: [minimap] },
  ], 825, 375, () => ({ width: 144, height: 22 }));
  assert.equal(labels.length, 1);
  const label = labels[0];
  const intersects = label.left < minimap.right && label.left + label.width > minimap.left
    && label.top < minimap.bottom && label.top + label.height > minimap.top;
  assert.equal(intersects, false);
  assert.ok(label.top >= 60 && label.top + label.height <= 299);
  assert.ok(label.top >= minimap.bottom, 'the label moves below the minimap inside the safe Adventure area');
});

test('Adventure labels do not move to an unrelated minimap row when horizontally separate', () => {
  const labels = labelPositions([
    { text: 'Creature dwelling', x: 857, y: 678, placement: 'below', safeBottom: 595,
      avoidRects: [{ left: 14, top: 64, right: 146, bottom: 196 }] },
  ], 922, 720, () => ({ width: 106, height: 22 }));
  assert.equal(labels.length, 1);
  assert.equal(labels[0].top, 573, 'the label clamps at the lower safe edge beside its own site');
});

test('off-screen Adventure landmarks do not get clamped into a misleading edge label', () => {
  const labels = labelPositions([
    { text: 'Town', x: -120, y: 800, placement: 'below' },
  ], 922, 720, () => ({ width: 60, height: 20 }));
  assert.equal(labels.length, 1);
  assert.equal(labels[0].visible, false);
});
