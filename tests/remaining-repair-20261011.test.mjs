import test from 'node:test';
import assert from 'node:assert/strict';
import data from '../src/data/reference-data.json' with { type: 'json' };
import contract from '../src/data/implementation-contract.json' with { type: 'json' };
import { command, newCampaign, validate } from '../src/core/campaign.js';
import { castDefense, createDefense, deployArmy, deployHero, defenseMarkers, advanceDefense, validateDefense } from '../src/core/defense.js';
import { activeStackId, startBattle, validateBattle } from '../src/core/battle.js';
import { decode, encode } from '../src/core/save.js';
import { unitStats } from '../src/core/mechanics.js';

const fresh = () => newCampaign(contract, data, 1_700_000_000_000, 123456789);
const act = (state, id, type, payload = {}) => command(state, { id, type, payload }, state.clock, data);

function stamp(session) {
  for (const enemy of session.queue) {
    enemy.spawned = true;
    enemy.progress = 2;
  }
  session.enemies = session.queue.filter(enemy => enemy.spawned);
  return session;
}

function pointOf(session, id) {
  const marker = defenseMarkers(session).enemies.find(enemy => enemy.id === id);
  assert.ok(marker, id);
  return { x: marker.at[0], y: marker.at[1] };
}

test('a blast that clears the last enemy resolves siege or extends endless', () => {
  for (const practice of ['siege', 'endless']) {
    const session = deployHero(stamp(createDefense(fresh(), data, { practice, waves: 1 })), 4);
    const last = session.queue.at(-1);
    for (const enemy of session.queue) enemy.hp = enemy === last ? 1 : 0;
    session.enemies = session.queue.filter(enemy => enemy.spawned);
    const xp = session.towers.map(tower => tower.xp);
    const time = session.time;
    validateDefense(session);
    const cast = castDefense(session, 14, pointOf(session, last.id));
    assert.equal(cast.time, time);
    assert.equal(cast.queue.find(enemy => enemy.id === last.id).hp <= 0, true);
    assert.deepEqual(cast.towers.map(tower => tower.xp), xp);
    assert.equal(cast.pendingSettlement, practice === 'siege');
    if (practice === 'siege') {
      assert.equal(cast.status, 'RESOLVED');
      assert.equal(cast.winner, 'p');
      assert.equal(cast.clearedWaves, 1);
      assert.throws(() => castDefense(cast, 14, { x: 1, y: 1 }), /deployed hero/);
    } else {
      assert.equal(cast.status, 'ACTIVE');
      assert.equal(cast.winner, undefined);
      assert.equal(cast.clearedWaves, 1);
      assert.equal(cast.waves, 4);
      assert.equal(cast.extensions, 1);
      assert.equal(cast.pendingSettlement, false);
    }
  }
});

test('blast targeting uses world distance, spends 40 mana once, and rejects a bad point', () => {
  const opened = fresh();
  opened.hero.class = 'mage';
  opened.hero.mana = 40;
  let state = act(opened, 'siege', 'START_SIEGE');
  state = act(state, 'deploy', 'DEPLOY_DEFENSE');
  const foe = state.defense.queue[0];
  foe.spawned = true;
  foe.progress = 2;
  foe.hp = 80;
  state.defense.enemies = state.defense.queue.filter(enemy => enemy.spawned);
  const far = { x: 0.2, y: 0.2 };
  const missed = act(state, 'miss', 'DEFENSE_CAST', far);
  assert.equal(missed.hero.mana, 0);
  assert.equal(missed.defense.queue[0].hp, 80);
  assert.equal(missed.defense.status, 'ACTIVE');
  assert.equal(missed.defense.time, state.defense.time);

  const hitPoint = pointOf(missed.defense, foe.id);
  missed.hero.mana = 40;
  const hit = act(missed, 'hit', 'DEFENSE_CAST', hitPoint);
  assert.equal(hit.hero.mana, 0);
  assert.ok(hit.defense.queue[0].hp < 80);
  assert.equal(hit.defense.towers[0].xp, state.defense.towers[0].xp);
  const again = act(hit, 'hit', 'DEFENSE_CAST', hitPoint);
  assert.equal(again.hero.mana, 0);
  assert.equal(again.defense.queue[0].hp, hit.defense.queue[0].hp);

  const paused = structuredClone(missed);
  paused.hero.mana = 40;
  paused.defense.paused = true;
  paused.defense.accumulator = 0;
  const progress = paused.defense.queue[0].progress;
  const held = act(paused, 'paused-cast', 'DEFENSE_CAST', far);
  assert.equal(held.defense.paused, true);
  assert.equal(held.defense.time, paused.defense.time);
  assert.equal(held.defense.queue[0].progress, progress);
  assert.equal(held.hero.mana, 0);

  const rejected = structuredClone(state);
  const mana = rejected.hero.mana;
  const before = JSON.stringify(rejected.defense);
  assert.throws(() => act(rejected, 'oob', 'DEFENSE_CAST', { x: 20, y: 1 }), /cast/);
  assert.equal(rejected.hero.mana, mana);
  assert.equal(JSON.stringify(rejected.defense), before);
  assert.throws(() => act(rejected, 'nan', 'DEFENSE_CAST', { x: Number.NaN, y: 1 }), /cast/);
  assert.equal(rejected.hero.mana, mana);
});

test('clearing one spawned wave does not award a premature victory', () => {
  const session = deployHero(stamp(createDefense(fresh(), data, { practice: 'siege', waves: 2 })), 4);
  for (const enemy of session.queue) {
    if (enemy.wave === 0) enemy.hp = enemy === session.queue.find(item => item.wave === 0) ? 1 : 0;
    else { enemy.spawned = false; enemy.progress = 0; enemy.hp = 30; }
  }
  const living = session.queue.find(enemy => enemy.wave === 0 && enemy.hp > 0);
  session.enemies = session.queue.filter(enemy => enemy.spawned);
  validateDefense(session);
  const cast = castDefense(session, 50, pointOf(session, living.id));
  assert.equal(cast.status, 'ACTIVE');
  assert.equal(cast.clearedWaves >= 1, true);
  assert.equal(cast.winner, undefined);
  assert.equal(cast.pendingSettlement, false);
  assert.ok(cast.queue.some(enemy => enemy.wave === 1 && enemy.hp > 0));
});

test('a blast ignores a leaked enemy and does not revive it', () => {
  const session = deployHero(stamp(createDefense(fresh(), data, { practice: 'siege', waves: 1 })), 4);
  const leaked = session.queue[0];
  const boss = session.queue.find(enemy => enemy.boss);
  leaked.leaked = true;
  leaked.hp = 0;
  leaked.progress = 2;
  boss.progress = 2;
  boss.hp = 1;
  const centre = pointOf(session, boss.id);
  boss.progress = 8;
  boss.hp = 40;
  for (const enemy of session.queue) if (enemy !== boss && enemy !== leaked) enemy.hp = 0;
  session.enemies = session.queue.filter(enemy => enemy.spawned);
  validateDefense(session);
  const cast = castDefense(session, 14, centre);
  const after = cast.queue.find(enemy => enemy.id === leaked.id);
  assert.equal(after.leaked, true);
  assert.equal(after.hp, 0);
  assert.equal(cast.queue.find(enemy => enemy.id === boss.id).hp, 40);
  assert.equal(cast.towers.every(tower => tower.xp === 0), true);
});

test('forged morale, negative defense experience and contradictory dwelling terms are rejected', () => {
  const battle = startBattle({
    id: 'bonus', positioned: true, rngState: 1, mana: 0, morale: 3,
    stacks: [
      { id: 'p', side: 'p', x: 1, y: 8, count: 2, maxCount: 2, atk: 1, def: 1, dmin: 1, dmax: 1, uhp: 20, top: 20, spd: 2 },
      { id: 'e', side: 'e', x: 5, y: 2, count: 2, maxCount: 2, atk: 1, def: 1, dmin: 1, dmax: 1, uhp: 20, top: 20, spd: 1 },
    ],
  });
  battle.currentBonusId = 'p';
  battle.stacks[0].bonusPending = true;
  battle.stacks[0].moraleChecked = true;
  battle.stacks[0].moraleBonusGranted = false;
  battle.queue = ['e', 'p'];
  assert.throws(() => validateBattle(battle), /morale bonus/);
  assert.notEqual(activeStackId(battle), 'p');
  const hosted = fresh();
  hosted.battle = battle;
  assert.throws(() => encode(hosted, data), /morale bonus/);

  const legacy = startBattle({
    id: 'legacy', positioned: true, rngState: 1, mana: 0,
    stacks: [
      { id: 'p', side: 'p', x: 1, y: 8, count: 2, maxCount: 2, atk: 1, def: 1, dmin: 1, dmax: 1, uhp: 20, top: 20, spd: 2 },
      { id: 'e', side: 'e', x: 5, y: 2, count: 2, maxCount: 2, atk: 1, def: 1, dmin: 1, dmax: 1, uhp: 20, top: 20, spd: 1 },
    ],
  });
  legacy.stacks[0].acted = true;
  delete legacy.stacks[0].moraleChecked;
  assert.equal(validateBattle(legacy), true);
  const carried = fresh();
  carried.battle = legacy;
  const restored = decode(encode(carried, data), data);
  assert.equal(restored.battle.stacks[0].moraleChecked, true);
  assert.equal(restored.battle.stacks[0].bonusPending, false);

  const defense = fresh();
  defense.defense = createDefense(defense, data, { practice: 'siege', waves: 1 });
  defense.defense.towers[0].xp = -100;
  assert.throws(() => validate(defense, data), /experience/);
  assert.throws(() => encode(defense, data), /experience/);

  const dwelling = fresh();
  dwelling.dwelling = { id: 'dwelling:dwelling:wolf', siteId: 'dwelling', type: 'wolf', count: 2, multiplier: 1, claimed: false };
  dwelling.dwellingHistory = [{ ...dwelling.dwelling, count: 99, multiplier: 0.5 }];
  assert.throws(() => validate(dwelling, data), /dwelling history/);
  assert.throws(() => encode(dwelling, data), /dwelling history/);

  const matched = fresh();
  matched.dwelling = { id: 'dwelling:dwelling:wolf', siteId: 'dwelling', type: 'wolf', count: 2, multiplier: 1, claimed: false };
  matched.dwellingHistory = [{ ...matched.dwelling }];
  assert.equal(validate(matched, data), true);
  assert.equal(decode(encode(matched, data), data).dwelling.count, 2);
});

test('deployed stacks use the source count factor, block, scaled range and survivor count', () => {
  const melee = fresh().army[0];
  const stats = unitStats(melee, data);
  const session = deployArmy(createDefense(fresh(), data, { practice: 'siege', waves: 1 }), melee);
  assert.equal(session.army.damage, Math.max(1, Math.round((stats.dmin + stats.dmax) / 2)));
  assert.equal(session.army.unitHp, stats.hp);
  assert.equal(session.army.block, stats.block);
  assert.equal(session.army.role, 'melee');
  assert.equal(session.army.range, 0);
  const factor = Math.max(1, Math.ceil(session.army.hp / session.army.unitHp) * 0.4 + 0.6);
  assert.equal(factor, 5.4);
  session.towers.forEach(tower => { tower.hp = 0; });
  const foe = session.queue.find(enemy => enemy.role === 'brute' && !enemy.boss);
  foe.spawned = true;
  foe.progress = session.army.at;
  foe.speed = 0;
  foe.hp = 500;
  foe.attackCooldown = 0;
  session.enemies = session.queue.filter(enemy => enemy.spawned);
  const stepped = advanceDefense(session, 1 / 60);
  const dealt = session.army.damage * factor;
  const blocked = foe.damage * Math.max(0.1, 1 - 0.06 * stats.block);
  assert.ok(Math.abs((500 - stepped.queue.find(enemy => enemy.id === foe.id).hp) - dealt) < 1e-9);
  assert.ok(Math.abs((session.army.hp - stepped.army.hp) - blocked) < 1e-9);

  const rangedStack = fresh().army[1];
  const rangedStats = unitStats(rangedStack, data);
  const ranged = deployArmy(createDefense(fresh(), data, { practice: 'siege', waves: 1 }), rangedStack);
  assert.equal(ranged.army.range, Math.max(1, rangedStats.rng * 0.45));
  assert.equal(ranged.army.range, 2.7);
  assert.equal(ranged.army.shots, rangedStats.shots);
  assert.equal(ranged.army.role, 'ranged');
  ranged.towers.forEach(tower => { tower.hp = 0; });
  const target = ranged.queue[0];
  target.spawned = true;
  target.progress = ranged.army.at;
  target.speed = 0;
  target.hp = 500;
  ranged.army.cooldown = 0;
  ranged.enemies = ranged.queue.filter(enemy => enemy.spawned);
  const shot = advanceDefense(ranged, 1 / 60);
  const rangedFactor = Math.max(1, Math.ceil(ranged.army.hp / ranged.army.unitHp) * 0.4 + 0.6);
  const expected = ranged.army.damage * rangedFactor * 0.5;
  assert.ok(Math.abs((500 - shot.queue[0].hp) - expected) < 1e-9);
  assert.equal(shot.army.shots, ranged.army.shots - 1);
  assert.equal(shot.projectiles.some(projectile => projectile.fam === 'slow'), false);

  let host = fresh();
  host = act(host, 'open', 'START_SIEGE');
  host = act(host, 'army', 'DEPLOY_ARMY', { stackId: melee.id });
  host.defense.towers.forEach(tower => { tower.hp = 0; tower.rate = 0; });
  for (const enemy of host.defense.queue) { enemy.spawned = true; enemy.hp = 0; }
  host.defense.enemies = host.defense.queue.filter(enemy => enemy.spawned);
  host.defense.army.hp = host.defense.army.unitHp * 1.1;
  host.defense.clearedWaves = host.defense.waves;
  host.defense.status = 'RESOLVED';
  host.defense.pendingSettlement = true;
  host.defense.winner = 'p';
  host.defense.accumulator = 0;
  const settled = act(host, 'settle-count', 'SETTLE_DEFENSE');
  assert.equal(settled.army.find(stack => stack.id === melee.id).count, 2);
});
