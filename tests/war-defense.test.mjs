import test from 'node:test';
import assert from 'node:assert/strict';
import data from '../src/data/reference-data.json' with { type: 'json' };
import contract from '../src/data/implementation-contract.json' with { type: 'json' };
import { command, newCampaign } from '../src/core/campaign.js';
import { advanceDefense, createDefense } from '../src/core/defense.js';
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
    id: 'leak', role: 'brute', wave: 0, spawned: false, hp: 50, damage: 7, speed: 1000,
    spawnAt: 0, progress: 0, slowUntil: 0, slowFraction: 0, leaked: false,
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
