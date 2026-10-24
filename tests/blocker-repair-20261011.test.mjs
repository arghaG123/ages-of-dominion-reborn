import test from 'node:test';
import assert from 'node:assert/strict';
import data from '../src/data/reference-data.json' with { type: 'json' };
import contract from '../src/data/implementation-contract.json' with { type: 'json' };
import adventureWorlds from '../src/data/adventure-worlds.json' with { type: 'json' };
import { adoptProgress, command, newCampaign, validate } from '../src/core/campaign.js';
import { adventureGeometryForWorld } from '../src/core/navigation.js';
import { autoStep, castSpell, defend, legalMoves, move, skipBonus, startBattle, strike, validateBattle, wait } from '../src/core/battle.js';
import { advanceDefense, castDefense, createDefense, deployArmy, deployHero } from '../src/core/defense.js';
import { MORALE_COEFFICIENT, unitStats } from '../src/core/mechanics.js';
import { battleMorale } from '../src/core/rules.js';
import { nextUnit } from '../src/core/rng.js';
import { decode, encode } from '../src/core/save.js';
import { modeRows } from '../src/client/tactical-ui.js';

const fresh = () => newCampaign(contract, data, 1000);
const act = (state, id, type, payload, now = 1000) => command(state, { id, type, payload }, now, data);
function atDwelling(state) {
  const world = adventureWorlds.find(item => item.id === state.adventureWorldId);
  const dwelling = adventureGeometryForWorld(contract.geometry.adventure, world, state.seed).sites.find(site => site.id === 'dwelling');
  state.adventure = {
    x: dwelling.approach[0], y: dwelling.approach[1], moves: 1,
    visited: [`${dwelling.approach[0]},${dwelling.approach[1]}`],
    resolvedGuards: [], pendingEncounter: null, atTown: false,
  };
  adoptProgress(state, data);
  return state;
}

function seedWhere(predicate) {
  for (let seed = 1; seed < 2000000; seed += 1) {
    if (predicate(nextUnit({ rngState: seed }).unit)) return seed;
  }
  throw new Error('No matching seed');
}

const successSeed = seedWhere(unit => unit < 0.042);
const failureSeed = seedWhere(unit => unit >= 0.126);

function battle() {
  return startBattle({
    id: 'morale',
    positioned: true,
    rngState: 1,
    mana: 0,
    wisdom: 0,
    morale: 0,
    stacks: [
      { id: 'p', side: 'p', x: 1, y: 8, count: 4, maxCount: 4, atk: 4, def: 2, dmin: 1, dmax: 1, uhp: 30, top: 30, spd: 2, rng: 0, shots: 0 },
      { id: 'e', side: 'e', x: 5, y: 2, count: 4, maxCount: 4, atk: 1, def: 1, dmin: 1, dmax: 1, uhp: 30, top: 30, spd: 1, rng: 0, shots: 0 },
    ],
  });
}

function playerMove(opened) {
  const cell = legalMoves(opened, 'p')[0];
  assert.ok(cell, 'player has a legal move');
  return { cell, moved: move(opened, 'p', cell) };
}

test('positive morale grants one unchainable bonus action and ignores excluded actions', () => {
  assert.equal(MORALE_COEFFICIENT, 0.042);
  assert.equal(startBattle({ id: 'cap', rngState: 1, mana: 0, wisdom: 0, morale: 9, stacks: battle().stacks }).morale, 3);
  assert.equal(startBattle({ id: 'floor', rngState: 1, mana: 0, wisdom: 0, morale: -8, stacks: battle().stacks }).morale, -3);
  assert.throws(() => startBattle({ id: 'bad', rngState: 1, mana: 0, wisdom: 0, morale: Number.NaN, stacks: battle().stacks }), /morale/);

  const quiet = battle();
  const quietRng = quiet.rngState;
  const held = playerMove(quiet).moved;
  assert.equal(held.rngState, quietRng);
  assert.equal(held.log.some(entry => entry.type === 'morale'), false);

  const negative = battle();
  negative.morale = -2;
  const negativeRng = negative.rngState;
  assert.equal(playerMove(negative).moved.rngState, negativeRng);

  const missed = battle();
  missed.morale = 3;
  missed.rngState = failureSeed;
  const failed = playerMove(missed).moved;
  const failedCheck = failed.log.find(entry => entry.type === 'morale');
  assert.equal(failedCheck.outcome, 'none');
  assert.equal(failedCheck.chance, 0.126);
  assert.ok(failedCheck.roll >= failedCheck.chance);
  assert.equal(failed.currentBonusId, null);
  assert.equal(failed.stacks.find(stack => stack.id === 'p').acted, true);

  const opened = battle();
  opened.morale = 1;
  opened.rngState = successSeed;
  const granted = playerMove(opened).moved;
  const check = granted.log.find(entry => entry.type === 'morale');
  assert.equal(check.outcome, 'bonus');
  assert.equal(check.text, 'High morale — extra action');
  assert.equal(check.chance, 0.042);
  assert.ok(check.roll < check.chance);
  assert.equal(granted.currentBonusId, 'p');
  assert.equal(new Set(granted.queue).size, granted.queue.length);
  const actor = granted.stacks.find(stack => stack.id === 'p');
  assert.equal(actor.acted, false);
  assert.equal(actor.bonusPending, true);
  assert.equal(actor.moraleChecked, true);
  assert.throws(() => wait(granted, 'p'), /bonus action/);
  assert.throws(() => skipBonus(granted, 'e'), /bonus|turn/);

  const skipped = skipBonus(granted, 'p');
  assert.equal(skipped.log.filter(entry => entry.type === 'morale').length, 1);
  assert.equal(skipped.currentBonusId, null);
  assert.equal(skipped.stacks.find(stack => stack.id === 'p').bonusPending, false);
  const defended = defend(skipped, 'e');
  assert.equal(defended.round, 2);
  assert.equal(defended.stacks.find(stack => stack.id === 'p').moraleChecked, false);
  assert.equal(defended.currentBonusId, null);

  const braced = battle();
  braced.morale = 3;
  braced.rngState = successSeed;
  const braceRng = braced.rngState;
  const defending = defend(braced, 'p');
  assert.equal(defending.rngState, braceRng);
  assert.equal(defending.log.some(entry => entry.type === 'morale'), false);

  const waiting = battle();
  waiting.morale = 3;
  const waitedRng = waiting.rngState;
  const delayed = wait(waiting, 'p');
  assert.equal(delayed.rngState, waitedRng);
  assert.equal(delayed.log.some(entry => entry.type === 'morale'), false);

  const illegal = battle();
  const illegalRng = illegal.rngState;
  assert.throws(() => move(illegal, 'p', [-1, -1]), /Illegal move/);
  assert.equal(illegal.rngState, illegalRng);

  const rows = modeRows({ moves: [[1, 8]], melee: [], ranged: [], spells: 0, waited: false, bonus: true });
  assert.equal(rows.find(row => row.id === 'wait').enabled, false);
  assert.equal(rows.find(row => row.id === 'skip-bonus').label, 'Skip bonus');
});

test('morale does not fire for a dead actor, a killing blow, a bonus action, or a spell', () => {
  const fragile = (morale) => startBattle({
    id: `dead-${morale}`,
    positioned: true,
    rngState: 4,
    mana: 0,
    wisdom: 0,
    morale,
    stacks: [
      { id: 'p', side: 'p', x: 1, y: 3, count: 1, maxCount: 1, atk: 1, def: 0, dmin: 1, dmax: 1, uhp: 1, top: 1, spd: 8, rng: 0, shots: 0 },
      { id: 'e', side: 'e', x: 2, y: 3, count: 3, maxCount: 3, atk: 8, def: 0, dmin: 40, dmax: 40, uhp: 40, top: 40, spd: 1, rng: 0, shots: 0 },
    ],
  });
  const killed = strike(fragile(3), 'p', 'e', { forceMelee: true });
  const killedQuiet = strike(fragile(0), 'p', 'e', { forceMelee: true });
  assert.equal(killed.stacks.find(stack => stack.id === 'p').dead, true);
  assert.equal(killed.log.some(entry => entry.type === 'morale'), false);
  assert.equal(killed.rngState, killedQuiet.rngState);

  const finisher = (morale) => startBattle({
    id: `win-${morale}`,
    positioned: true,
    rngState: 4,
    mana: 0,
    wisdom: 0,
    morale,
    stacks: [
      { id: 'p', side: 'p', x: 1, y: 3, count: 6, maxCount: 6, atk: 8, def: 4, dmin: 40, dmax: 40, uhp: 30, top: 30, spd: 8, rng: 0, shots: 0 },
      { id: 'e', side: 'e', x: 2, y: 3, count: 1, maxCount: 1, atk: 0, def: 0, dmin: 1, dmax: 1, uhp: 1, top: 1, spd: 1, rng: 0, shots: 0 },
    ],
  });
  const won = strike(finisher(3), 'p', 'e', { forceMelee: true });
  const wonQuiet = strike(finisher(0), 'p', 'e', { forceMelee: true });
  assert.equal(won.status, 'RESOLVED');
  assert.equal(won.log.some(entry => entry.type === 'morale'), false);
  assert.equal(won.rngState, wonQuiet.rngState);

  const chaining = battle();
  chaining.morale = 3;
  chaining.rngState = successSeed;
  const extra = playerMove(chaining).moved;
  const again = defend(extra, 'p');
  assert.equal(again.log.filter(entry => entry.type === 'morale').length, 1);
  assert.equal(again.currentBonusId, null);

  const caster = battle();
  caster.mana = 20;
  caster.wisdom = 3;
  caster.morale = 3;
  caster.rngState = successSeed;
  const cast = castSpell(caster, { id: 'bless', lv: 1, mana: 5 }, 'p', 1);
  assert.equal(cast.log.some(entry => entry.type === 'morale'), false);
  assert.equal(cast.castThisRound, true);
});

test('auto and manual morale use the same roll, and reload does not grant it twice', () => {
  const opened = battle();
  opened.morale = 1;
  opened.rngState = successSeed;
  const stepped = autoStep(opened);
  const moveLog = stepped.log.find(entry => entry.type === 'move');
  assert.ok(moveLog);
  const manual = move(opened, moveLog.id, moveLog.to);
  assert.equal(manual.rngState, stepped.rngState);
  assert.deepEqual(manual.log.filter(entry => entry.type === 'morale'), stepped.log.filter(entry => entry.type === 'morale'));

  let state = fresh();
  state.battle = battle();
  state.battle.morale = 1;
  state.battle.rngState = successSeed;
  validate(state, data);
  const cell = legalMoves(state.battle, 'p')[0];
  state = act(state, 'move-once', 'BATTLE', { action: 'move', stackId: 'p', to: cell });
  const replay = act(state, 'move-once', 'BATTLE', { action: 'move', stackId: 'p', to: cell });
  assert.deepEqual(replay.battle.log, state.battle.log);
  assert.equal(replay.battle.rngState, state.battle.rngState);
  const restored = decode(encode(state, data), data);
  assert.equal(restored.battle.currentBonusId, 'p');
  assert.equal(restored.battle.log.filter(entry => entry.type === 'morale').length, 1);
  const legacy = structuredClone(state.battle);
  delete legacy.stacks[0].moraleChecked;
  legacy.stacks[0].acted = true;
  legacy.stacks[0].bonusPending = false;
  legacy.currentBonusId = null;
  assert.equal(validateBattle(legacy), true);
  legacy.stacks[0].bonusPending = true;
  legacy.stacks[0].acted = true;
  assert.throws(() => validateBattle(legacy), /morale bonus/);
});

test('hero experience uses the completed Hero Hall, and resurrection restores a living stack once', () => {
  const host = fresh();
  host.plots.find(plot => plot.id === 'townhall').level = 4;
  const hall = host.plots.find(plot => plot.id === 'P01');
  hall.type = 'hall';
  hall.level = 3;
  const session = createDefense(host, data, { practice: 'siege', waves: 1 });
  for (const enemy of session.queue) {
    enemy.spawned = true;
    enemy.hp = 0;
  }
  session.enemies = session.queue.filter(enemy => enemy.spawned);
  session.clearedWaves = session.waves;
  session.status = 'RESOLVED';
  session.pendingSettlement = true;
  session.winner = 'p';
  session.towers[0].xp = 60;
  host.defense = session;
  let settled = act(host, 'settle-hall', 'SETTLE_DEFENSE');
  assert.equal(settled.hero.level, 1);
  assert.equal(settled.hero.xp, 131);
  assert.equal(settled.towers[0].xp, 60);
  assert.equal(settled.towers[0].rank, 1);
  assert.throws(() => act(settled, 'settle-again', 'SETTLE_DEFENSE'), /pending/);
  assert.equal(settled.hero.xp, 131);
  assert.equal(settled.towers[0].rank, 1);

  const unfinished = fresh();
  const building = unfinished.plots.find(plot => plot.id === 'P01');
  building.type = 'hall';
  building.level = 2;
  unfinished.buildJobs.push({ id: 'job-hall', plotId: 'P01', type: 'hall', targetLevel: 3, completesAt: 999999 });
  const pending = createDefense(unfinished, data, { practice: 'siege', waves: 1 });
  for (const enemy of pending.queue) { enemy.spawned = true; enemy.hp = 0; }
  pending.enemies = pending.queue.filter(enemy => enemy.spawned);
  pending.clearedWaves = pending.waves;
  pending.status = 'RESOLVED';
  pending.pendingSettlement = true;
  pending.winner = 'p';
  unfinished.defense = pending;
  settled = act(unfinished, 'settle-unfinished', 'SETTLE_DEFENSE');
  assert.equal(settled.plots.find(plot => plot.type === 'hall').level, 2);
  assert.equal(settled.hero.xp, 117);

  const wounded = startBattle({
    id: 'resurrect',
    positioned: true,
    rngState: 2,
    mana: 20,
    wisdom: 3,
    stacks: [
      { id: 'p', side: 'p', x: 1, y: 8, count: 2, maxCount: 4, atk: 1, def: 1, dmin: 1, dmax: 1, uhp: 10, top: 5, spd: 4, rng: 0, shots: 0 },
      { id: 'e', side: 'e', x: 5, y: 2, count: 2, maxCount: 2, atk: 1, def: 1, dmin: 1, dmax: 1, uhp: 10, top: 10, spd: 1, rng: 0, shots: 0 },
    ],
  });
  const healed = castSpell(wounded, { id: 'resurrect', lv: 4, mana: 20 }, 'p', 0.2);
  const stack = healed.stacks.find(item => item.id === 'p');
  assert.equal(stack.count, 3);
  assert.equal(stack.top, 5);
  assert.equal(healed.mana, 0);
  assert.throws(() => castSpell(healed, { id: 'resurrect', lv: 4, mana: 20 }, 'p', 1), /Spell already cast/);
  const dead = structuredClone(wounded);
  dead.stacks.push({ id: 'fallen', side: 'p', x: 2, y: 8, count: 0, maxCount: 2, atk: 1, def: 1, dmin: 1, dmax: 1, uhp: 10, top: 0, spd: 1, rng: 0, shots: 0, dead: true });
  assert.throws(() => castSpell(dead, { id: 'resurrect', lv: 4, mana: 20 }, 'fallen', 1), /Dead stacks/);
});

test('defense experience credits one lethal blow and the hero blast spends mana without experience', () => {
  const session = createDefense(fresh(), data, { practice: 'siege', waves: 1 });
  session.towers.forEach((tower, index) => {
    tower.rng = 100;
    tower.dmg = 10;
    tower.splash = 0;
    tower.cooldown = 0;
    tower.xp = 0;
    if (index > 0) tower.hp = 0;
  });
  const target = session.queue.find(enemy => enemy.boss);
  target.spawned = true;
  target.progress = 2;
  target.hp = 1;
  session.enemies = session.queue.filter(enemy => enemy.spawned);
  const shot = advanceDefense(session, 1 / 60);
  assert.ok(Math.abs(shot.towers[0].xp - (10 * 0.045 + 18)) < 1e-9);
  assert.equal(shot.towers[1].xp, 0);

  const splash = createDefense(fresh(), data, { practice: 'siege', waves: 1 });
  splash.towers.forEach((tower, index) => {
    tower.rng = 100;
    tower.dmg = 10;
    tower.splash = 5;
    tower.cooldown = 0;
    tower.xp = 0;
    if (index > 0) tower.hp = 0;
  });
  const pair = splash.queue.filter(enemy => !enemy.boss).slice(0, 2);
  pair.forEach(enemy => { enemy.spawned = true; enemy.progress = 2; enemy.hp = 100; });
  splash.enemies = splash.queue.filter(enemy => enemy.spawned);
  const splashed = advanceDefense(splash, 1 / 60);
  assert.ok(Math.abs(splashed.towers[0].xp - ((10 + 6) * 0.045)) < 1e-9);

  let state = fresh();
  state.hero.class = 'mage';
  state.hero.mana = 40;
  state = act(state, 'siege', 'START_SIEGE');
  state = act(state, 'deploy', 'DEPLOY_DEFENSE');
  const foe = state.defense.queue[0];
  foe.spawned = true;
  foe.progress = state.defense.heroAt;
  foe.hp = 50;
  state.defense.enemies = state.defense.queue.filter(enemy => enemy.spawned);
  const before = state.defense.towers[0].xp;
  state = act(state, 'cast', 'DEFENSE_CAST');
  assert.equal(state.hero.mana, 0);
  assert.equal(state.defense.queue[0].hp, 36);
  assert.equal(state.defense.towers[0].xp, before);
  assert.throws(() => act(state, 'cast-2', 'DEFENSE_CAST'), /mana/);
  assert.equal(state.hero.mana, 0);

  const melee = fresh().army[0];
  const stats = unitStats(melee, data);
  const deployed = deployArmy(createDefense(fresh(), data, { practice: 'siege', waves: 1 }), melee);
  assert.equal(deployed.army.damage, Math.max(1, Math.round((stats.dmin + stats.dmax) / 2)));
  assert.equal(deployed.army.hp, stats.hp * melee.count);
  assert.throws(() => deployHero(deployed, 4, deployed.towers[0].siteId), /occupied/);
});

test('dwelling history keeps one offer per type and blocks a second claim', () => {
  let state = atDwelling(fresh());
  state.age = 7;
  state.plots.find(plot => plot.id === 'P01').type = 'barracks';
  state.plots.find(plot => plot.id === 'P01').level = 8;
  state.resources.food = 100000;
  state.resources.wood = 100000;
  state.resources.stone = 100000;
  state.resources.gold = 100000;
  const types = Object.keys(data.CREATURES);
  assert.equal(types.length, 8);
  for (const type of types) {
    state = act(state, `offer-${type}`, 'OFFER_DWELLING', { type });
    const saved = structuredClone(state.dwelling);
    assert.throws(() => act(state, `switch-${type}`, 'OFFER_DWELLING', { type: types.find(item => item !== type) }), /already open/);
    const cancelled = act(state, `cancel-${type}`, 'CANCEL_DWELLING');
    assert.deepEqual(cancelled.dwelling, saved);
    state = act(cancelled, `claim-${type}`, 'CLAIM_DWELLING');
    assert.equal(state.dwelling.claimed, true);
    assert.equal(state.dwellingHistory.find(row => row.type === type).claimed, true);
    assert.throws(() => act(state, `again-${type}`, 'OFFER_DWELLING', { type }), /already offered/);
    const replay = act(state, `claim-${type}`, 'CLAIM_DWELLING');
    assert.equal(replay.army.filter(stack => stack.type === type).length, 1);
  }
  assert.equal(new Set(state.army.filter(stack => stack.kind === 'creature').map(stack => stack.type)).size, 8);

  const legacy = fresh();
  delete legacy.dwellingHistory;
  legacy.army.push({ id: 'army-wolf', kind: 'creature', type: 'wolf', age: 0, count: 2, rank: 0, xp: 0 });
  legacy.plots.find(plot => plot.id === 'P01').type = 'barracks';
  legacy.plots.find(plot => plot.id === 'P01').level = 2;
  const migrated = act(atDwelling(legacy), 'touch', 'SETTINGS', { music: 0.6, sfx: 0.8, reducedMotion: false });
  assert.equal(migrated.dwellingHistory.find(row => row.type === 'wolf').claimed, true);
  assert.throws(() => act(migrated, 'reopen-wolf', 'OFFER_DWELLING', { type: 'wolf' }), /already offered/);
  assert.equal(migrated.army.filter(stack => stack.type === 'wolf').length, 1);
});

test('battle morale snapshot subtracts storm and keeps the Ancient Banner', () => {
  const state = fresh();
  state.hero.skills.leadership = 2;
  state.hero.equip.accessory = { id: 'banner-1', kind: 'artifact', artifactId: 'banner', slot: 'accessory' };
  state.weather = 'storm';
  assert.equal(battleMorale(state, data), 2);
  state.weather = 'clear';
  assert.equal(battleMorale(state, data), 3);
});
