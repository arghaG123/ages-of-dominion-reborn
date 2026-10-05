import test from 'node:test';
import assert from 'node:assert/strict';
import data from '../src/data/reference-data.json' with { type: 'json' };
import contract from '../src/data/implementation-contract.json' with { type: 'json' };
import { advance, command, newCampaign } from '../src/core/campaign.js';
import { encode, load, replaceCampaign, save, SAVE_KEY } from '../src/core/save.js';

const fresh = () => newCampaign(contract, data, 1000);
const act = (state, id, type, payload, now = state.clock) => command(state, { id, type, payload }, now, data);
const finish = state => advance(state, state.buildJobs[0].completesAt, data);

function memory() {
  return {
    values: new Map(),
    getItem(k) { return this.values.has(k) ? this.values.get(k) : null; },
    setItem(k, v) { this.values.set(k, v); },
    removeItem(k) { this.values.delete(k); },
  };
}

test('connected starter journey: build/recruit/adventure/defense/story/save without fixture grants', () => {
  // Natural control path using starter resources only. Time is advanced to finish builds (labeled accelerated construction, not a resource grant).
  let state = fresh();
  const startFood = state.resources.food;
  const startGold = state.resources.gold;
  assert.equal(state.plots.filter(plot => plot.level > 0).length, 1);
  assert.equal(state.walls.level, 0);

  state = act(state, 'lumber', 'BUILD', { plotId: 'P01', building: 'lumber' });
  state = finish(state);
  state = act(state, 'farm', 'BUILD', { plotId: 'P02', building: 'farm' }, state.clock);
  state = finish(state);
  state = act(state, 'quarry', 'BUILD', { plotId: 'P03', building: 'quarry' }, state.clock);
  state = finish(state);
  state = act(state, 'barracks', 'BUILD', { plotId: 'P04', building: 'barracks' }, state.clock);
  state = finish(state);
  assert.equal(state.tutorial.step, 4);
  assert.ok(state.resources.food < startFood || state.resources.wood < 250);

  state = act(state, 'recruit', 'RECRUIT', { role: 'melee' }, state.clock);
  assert.ok(state.army[0].count > 12);
  assert.ok(state.resources.gold < startGold);
  assert.equal(state.tutorial.step, 5);

  state = act(state, 'leave', 'ENTER_ADVENTURE', {}, state.clock);
  assert.equal(state.adventure.atTown, false);
  assert.equal(state.tutorial.step, 6);
  const moves = state.adventure.moves;
  assert.throws(() => act(state, 'water', 'MOVE', { path: [[4, 5]] }, state.clock), /Illegal|Blocked/);
  assert.equal(state.adventure.moves, moves);
  // Synthetic: War/Defense from an open journey without a full fog/guard clear this pass.
  state = act(state, 'rival', 'CHOOSE_RIVAL', { name: 'Varek Iron-Eye' }, state.clock);
  state = act(state, 'chapter', 'STORY_CHOICE', { index: 0 }, state.clock);
  assert.equal(state.story.chapter, 1);
  assert.throws(() => act(state, 'chapter-again', 'STORY_CHOICE', { index: 0 }, state.clock), /not open|age|Chapter/i);

  const beforeSiegeGold = state.resources.gold;
  state = act(state, 'siege', 'START_SIEGE', {}, state.clock);
  assert.equal(state.defense.practice, 'siege');
  assert.ok(state.defense.queue.some(enemy => enemy.boss));
  state = act(state, 'deploy-hero', 'DEPLOY_DEFENSE', {}, state.clock);
  state = act(state, 'deploy-army', 'DEPLOY_ARMY', { stackId: state.army[0].id }, state.clock);
  assert.equal(state.resources.gold, beforeSiegeGold);
  state = act(state, 'pause', 'DEFENSE', { dt: 1, paused: true }, state.clock);
  assert.equal(state.defense.time, 0);
  state = act(state, 'tick', 'DEFENSE', { dt: 0.25, speed: 2 }, state.clock);
  assert.ok(state.defense.time > 0);

  const store = memory();
  save(store, state, data);
  const reloaded = load(store, data);
  assert.equal(reloaded.status, 'VALID');
  assert.equal(reloaded.state.story.rival, 'Varek Iron-Eye');
  assert.equal(reloaded.state.defense.armyDeployed, true);
  assert.equal(reloaded.state.tutorial.step, state.tutorial.step);

  const other = fresh();
  other.hero.class = 'mage';
  const replaced = replaceCampaign(store, other, data);
  assert.equal(load(store, data).state.hero.class, 'mage');
  assert.ok(replaced.revision > state.revision);
  assert.throws(() => save(store, state, data), /stale/);
});

test('negative actions: duplicate settle and skirmish isolation stay blocked', () => {
  let state = act(fresh(), 'skirmish', 'START_SKIRMISH');
  const gold = state.resources.gold;
  const xp = state.hero.xp;
  state = act(state, 'auto', 'BATTLE', { action: 'auto' }, state.clock);
  if (state.battle.status === 'RESOLVED' || state.battle.pendingSettlement) {
    state = act(state, 'settle', 'SETTLE_BATTLE', {}, state.clock);
    assert.throws(() => act(state, 'settle-again', 'SETTLE_BATTLE', {}, state.clock), /pending|No pending/i);
  }
  assert.equal(state.resources.gold, gold);
  assert.equal(state.hero.xp, xp);
});
