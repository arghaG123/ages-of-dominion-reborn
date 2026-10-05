import test from 'node:test';
import assert from 'node:assert/strict';
import data from '../src/data/reference-data.json' with { type: 'json' };
import contract from '../src/data/implementation-contract.json' with { type: 'json' };
import { command, newCampaign } from '../src/core/campaign.js';
import { advanceDefense, createDefense, deployArmy, deployHero, defenseMarkers, validateDefense } from '../src/core/defense.js';
import { playOut } from '../src/core/battle.js';

const fresh = () => newCampaign(contract, data, 1000);
const act = (state, id, type, payload, now = 1000) => command(state, { id, type, payload }, now, data);

test('the five war options start, and skirmish and challenge leave campaign gold alone', () => {
  const host = fresh();
  const snapshot = structuredClone(host);
  let skirmish = act(host, 'skirmish', 'START_SKIRMISH');
  skirmish = act(skirmish, 'skirmish-auto', 'BATTLE', { action: 'auto' });
  skirmish = act(skirmish, 'skirmish-settle', 'SETTLE_BATTLE');
  assert.equal(skirmish.resources.gold, snapshot.resources.gold);
  assert.equal(skirmish.hero.xp, snapshot.hero.xp);
  assert.deepEqual(skirmish.army.map(stack => stack.count), snapshot.army.map(stack => stack.count));

  let challengeA = act(fresh(), 'challenge-a', 'START_CHALLENGE', { seed: 99, code: 'valley' });
  let challengeB = act(fresh(), 'challenge-b', 'START_CHALLENGE', { seed: 99, code: 'valley' });
  const resolvedA = playOut(challengeA.battle);
  const resolvedB = playOut(challengeB.battle);
  assert.equal(resolvedA.outcome.winner, resolvedB.outcome.winner);
  challengeA.battle = resolvedA;
  challengeA = act(challengeA, 'challenge-settle', 'SETTLE_BATTLE');
  assert.equal(challengeA.resources.gold, 150);
  assert.equal(challengeA.story.flags['challenge:challenge-valley'], resolvedA.outcome.winner);

  let duel = act(fresh(), 'duel', 'START_DUEL');
  assert.equal(duel.battle.practice, 'campaign');
  duel = act(duel, 'duel-auto', 'BATTLE', { action: 'auto' });
  const winner = duel.battle.outcome.winner;
  duel = act(duel, 'duel-settle', 'SETTLE_BATTLE');
  assert.equal(duel.battle, null);
  if (winner === 'p') assert.equal(duel.resources.gold, 300);
  assert.throws(() => act(duel, 'duel-again', 'SETTLE_BATTLE'), /No pending battle result/);

  const siege = act(fresh(), 'siege', 'START_SIEGE');
  assert.equal(siege.defense.practice, 'siege');
  const endless = act(fresh(), 'endless', 'START_ENDLESS');
  assert.equal(endless.defense.practice, 'endless');
  assert.equal(endless.defense.waves, 3);
});

test('defense pause stores no attack, 2x takes twice the steps, and hero deployment is free', () => {
  let state = act(fresh(), 'siege', 'START_SIEGE');
  const paused = act(state, 'pause', 'DEFENSE', { dt: 1, paused: true });
  assert.equal(paused.defense.time, 0);
  assert.equal(paused.defense.core, state.defense.core);
  const one = act(state, 'one', 'DEFENSE', { dt: 1 / 60, speed: 1 });
  const two = act(state, 'two', 'DEFENSE', { dt: 1 / 60, speed: 2 });
  assert.equal(one.defense.steps, 1);
  assert.equal(two.defense.steps, 2);
  const gold = state.resources.gold;
  state = act(state, 'deploy', 'DEPLOY_DEFENSE');
  assert.equal(state.resources.gold, gold);
  assert.equal(state.defense.heroDeployed, true);
  assert.throws(() => act(state, 'deploy-again', 'DEPLOY_DEFENSE'), /already deployed/);
});

test('a leaked attacker damages the core once and a cleared siege wave pays one early call', () => {
  const session = createDefense(fresh(), data, { practice: 'siege', waves: 1 });
  session.towers = [];
  session.queue = [{
    id: 'leak', role: 'brute', boss: false, wave: 0, spawned: false, hp: 50, damage: 7, speed: 1000,
    spawnAt: 0, progress: 0, slowUntil: 0, slowFraction: 0, leaked: false,
    attackCooldown: 0, telegraphId: null, buffUntil: 0,
  }];
  const leaked = advanceDefense(session, 0.25);
  assert.equal(leaked.core, session.core - (7 * 3 + 20));
  const again = advanceDefense(leaked, 0.25);
  assert.equal(again.core, leaked.core);

  let state = act(fresh(), 'siege', 'START_SIEGE');
  state.defense.towers.forEach(tower => { tower.dmg = 500; tower.rate = 10; tower.rng = 30; });
  state.defense.queue.forEach(enemy => { if (enemy.wave === 0) enemy.hp = 1; });
  for (let n = 0; n < 40 && state.defense.clearedWaves < 1; n++) state = act(state, `step-${n}`, 'DEFENSE', { dt: 0.25, speed: 2 });
  assert.ok(state.defense.clearedWaves >= 1);
  const before = state.resources.gold;
  state = act(state, 'call', 'EARLY_CALL');
  assert.equal(state.resources.gold, before + 25);
  assert.throws(() => act(state, 'call-again', 'EARLY_CALL'), /eligible/);
});

test('defense saves reject corruption and endless keeps extending without a victory payout', () => {
  const base = fresh();
  const defense = createDefense(base, data, { practice: 'siege', waves: 3 });
  validateDefense(defense);
  const corruptions = [
    [session => { session.time = -1; }, /time/],
    [session => { session.queue = 'corrupt'; }, /queue/],
    [session => { session.towers[0].dmg = -10; }, /damage/],
    [session => { session.queue = []; }, /queue/],
    [session => { session.status = 'RESOLVED'; session.pendingSettlement = true; session.winner = 'p'; }, /victory/],
  ];
  for (const [edit, message] of corruptions) {
    const session = structuredClone(defense);
    edit(session);
    assert.throws(() => validateDefense(session), message);
    const hosted = structuredClone(base);
    hosted.defense = session;
    const gold = hosted.resources.gold;
    assert.throws(() => act(hosted, 'bad-defense', 'DEFENSE', { dt: 1 / 60 }), message);
    assert.equal(hosted.resources.gold, gold);
    assert.equal(hosted.revision, base.revision);
  }

  let endless = createDefense(base, data, { practice: 'endless', waves: 3 });
  endless.towers = [];
  endless = deployHero(endless, 9);
  const identity = { damage: endless.heroDamage, at: endless.heroAt, rng: endless.rngState };
  const clear = session => {
    for (const enemy of session.queue) if (!enemy.spawned) { enemy.hp = 0; enemy.spawnAt = 0; }
    return advanceDefense(session, 1 / 60);
  };
  endless = clear(endless);
  assert.equal(endless.waves, 6);
  assert.equal(endless.extensions, 1);
  assert.equal(endless.status, 'ACTIVE');
  endless = clear(endless);
  assert.equal(endless.waves, 9);
  assert.equal(endless.extensions, 2);
  assert.equal(endless.status, 'ACTIVE');
  assert.equal(endless.winner, undefined);
  assert.equal(endless.heroDeployed, true);
  assert.equal(endless.heroDamage, identity.damage);
  assert.equal(endless.heroAt, identity.at);
  assert.notEqual(endless.rngState, identity.rng);
  const reloaded = JSON.parse(JSON.stringify(endless));
  validateDefense(reloaded);
  const extended = clear(reloaded);
  assert.equal(extended.waves, 12);
  assert.equal(extended.extensions, 3);
  assert.equal(extended.heroDeployed, true);

  let campaign = act(fresh(), 'endless-loss', 'START_ENDLESS');
  const gold = campaign.resources.gold;
  campaign.defense.towers.forEach(tower => { tower.rate = 0; });
  campaign.defense.core = 1;
  for (const enemy of campaign.defense.queue) { enemy.spawnAt = 0; enemy.speed = 1000; enemy.damage = 50; }
  campaign = act(campaign, 'endless-tick', 'DEFENSE', { dt: 0.25 });
  assert.equal(campaign.defense.winner, 'e');
  campaign = act(campaign, 'endless-settle', 'SETTLE_DEFENSE');
  assert.equal(campaign.defense, null);
  assert.equal(campaign.resources.gold, gold);
  const record = Object.entries(campaign.story.flags).find(([key]) => key.startsWith('endless:'));
  assert.equal(typeof record?.[1], 'number');
});

test('final-wave boss, army deploy, entry targeting and role shots are distinct', () => {
  const base = fresh();
  const siege = createDefense(base, data, { practice: 'siege', waves: 2 });
  const bosses = siege.queue.filter(enemy => enemy.boss);
  assert.equal(bosses.length, 1);
  assert.equal(bosses[0].wave, 1);
  assert.ok(bosses[0].hp > siege.queue.find(enemy => !enemy.boss && enemy.wave === 1).hp * 3);
  assert.ok(siege.queue.some(enemy => enemy.role === 'brute'));
  assert.ok(siege.queue.some(enemy => enemy.role === 'runner'));

  let state = act(base, 'siege', 'START_SIEGE');
  const gold = state.resources.gold;
  const stackId = state.army[0].id;
  state = act(state, 'army', 'DEPLOY_ARMY', { stackId });
  assert.equal(state.resources.gold, gold);
  assert.equal(state.defense.armyDeployed, true);
  assert.equal(state.defense.army.stackId, stackId);
  assert.throws(() => act(state, 'army-again', 'DEPLOY_ARMY', { stackId }), /already deployed/);

  const session = createDefense(base, data, { practice: 'siege', waves: 1 });
  session.towers.forEach(tower => { tower.dmg = 0; tower.rate = 0; });
  for (const enemy of session.queue) { enemy.spawnAt = 999; enemy.spawned = false; enemy.progress = 0; }
  const archer = session.queue.find(enemy => enemy.role === 'archer');
  assert.ok(archer);
  archer.spawnAt = 0;
  archer.progress = 0.5;
  archer.spawned = true;
  archer.hp = 40;
  archer.attackCooldown = 0;
  session.enemies = session.queue.filter(enemy => enemy.spawned);
  const beforeHp = session.towers.reduce((sum, tower) => sum + tower.hp, 0);
  let stepped = session;
  for (let n = 0; n < 120; n++) stepped = advanceDefense(stepped, 1 / 60);
  const afterHp = stepped.towers.reduce((sum, tower) => sum + tower.hp, 0);
  assert.ok(afterHp < beforeHp);
  assert.ok(defenseMarkers(stepped).projectiles.length >= 0);
  assert.ok(stepped.towers.every(tower => tower.fam));

  const preEntry = createDefense(base, data, { practice: 'siege', waves: 1 });
  for (const enemy of preEntry.queue) { enemy.spawned = false; enemy.spawnAt = 999; enemy.progress = 0; enemy.hp = 1; }
  const runner = preEntry.queue.find(enemy => enemy.role === 'runner');
  runner.spawned = true;
  runner.spawnAt = 0;
  runner.progress = 0.1;
  runner.hp = 1000;
  preEntry.enemies = preEntry.queue.filter(enemy => enemy.spawned);
  preEntry.towers.forEach(tower => { tower.dmg = 500; tower.rate = 20; tower.rng = 30; tower.cooldown = 0; });
  const held = advanceDefense(preEntry, 1 / 60);
  assert.equal(held.queue.find(enemy => enemy.id === runner.id).hp, 1000);
});


