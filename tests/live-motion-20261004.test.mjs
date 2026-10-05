import test from 'node:test';
import assert from 'node:assert/strict';
import data from '../src/data/reference-data.json' with { type: 'json' };
import contract from '../src/data/implementation-contract.json' with { type: 'json' };
import { command, newCampaign } from '../src/core/campaign.js';
import { activeStackId } from '../src/core/battle.js';
import { createFrameClock, travelProgress, travelSample } from '../src/client/motion.js';
import { clipAngles, mountGait, plateOffset } from '../src/client/actor.js';
import { challengeDescriptor, decodeChallengeCode, encodeChallengeCode, reproduceChallenge, validateDescriptor } from '../src/core/challenge.js';
import { forgeOffer, gearBonus } from '../src/core/rules.js';

const fresh = () => newCampaign(contract, data, 1000);
const act = (state, id, type, payload, now = state.clock) => command(state, { id, type, payload }, now, data);

test('the frame clock freezes while paused and advances while running', () => {
  let paused = true;
  let frames = 0;
  const queued = [];
  const clock = createFrameClock({
    paused: () => paused,
    requestFrame: fn => { queued.push(fn); return ++frames; },
    cancelFrame: () => {},
    onFrame: () => {},
  });
  clock.start();
  clock.start();
  queued.shift()(100);
  assert.equal(clock.sample().sim, 0);
  paused = false;
  queued.shift()(250);
  assert.equal(clock.sample().paused, false);
  assert.ok(clock.sample().sim > 0);
});

test('travel samples the route and a reload has no second charge', () => {
  const mid = travelSample([[0, 0], [2, 0]], 0.5);
  assert.equal(mid.x, 1.5);
  assert.equal(mid.facing, 1);
  assert.equal(travelSample([[2, 0], [1, 0]], 0.5).facing, -1);
  assert.equal(travelProgress(0, 0.45, 0.9), 0.5);
  const planted = mountGait(0, true);
  assert.ok(planted.every(angle => angle > 0));
  const moving = mountGait(0.2, false);
  assert.ok(moving.some(angle => angle < 0));
  assert.ok(moving.some(angle => angle > 0));
  assert.notEqual(clipAngles('walk', 0.1).thighL, clipAngles('walk', 0.6).thighL);
  assert.ok(plateOffset(0.25, { fly: true }).y < plateOffset(0, { fly: false, reduced: true }).y);

  let state = fresh();
  state = act(state, 'leave', 'ENTER_ADVENTURE');
  const before = state.adventure.moves;
  state = act(state, 'step', 'MOVE', { path: [[state.adventure.x + 1, state.adventure.y]] });
  assert.equal(state.adventure.moves, before - 1);
  const again = structuredClone(state);
  assert.equal(again.adventure.moves, state.adventure.moves);
  assert.equal(again.resources.gold, state.resources.gold);
});

test('duel-v1 roundtrips and reproduces across two campaigns', () => {
  const descriptor = challengeDescriptor(99, 'valley');
  assert.equal(descriptor.scenarioId, 'duel-v1');
  const code = encodeChallengeCode(descriptor);
  assert.deepEqual(decodeChallengeCode(code).descriptor, descriptor);
  assert.ok(decodeChallengeCode('@@@').error);
  assert.ok(decodeChallengeCode('x'.repeat(481)).error);
  assert.ok(validateDescriptor({ schema: 2, scenarioId: 'duel-v1', seed: 1, label: 'a' }).error);
  assert.ok(validateDescriptor({ schema: 1, scenarioId: 'other', seed: 1, label: 'a' }).error);
  const rich = fresh();
  rich.resources.gold = 900;
  rich.hero.class = 'mage';
  rich.age = 3;
  const poor = fresh();
  const first = reproduceChallenge(99, 'valley');
  const second = reproduceChallenge(99, 'other-label');
  assert.equal(first.digest, reproduceChallenge(99, 'valley').digest);
  assert.equal(first.outcome.winner, second.outcome.winner);
  assert.notEqual(first.descriptor.label, second.descriptor.label);
  let challenge = act(poor, 'start', 'START_CHALLENGE', { schema: 1, scenarioId: 'duel-v1', seed: 99, label: 'valley', code: 'valley' });
  assert.equal(challenge.resources.gold, 150);
  assert.equal(challenge.battle.stacks[0].kind, 'role');
  assert.equal(challenge.battle.stacks[1].type, 'wolf');
  assert.equal(challenge.battle.challenge.scenarioId, 'duel-v1');
  assert.throws(() => act(rich, 'bad', 'START_CHALLENGE', { schema: 9, seed: 1, code: 'valley' }), /schema/);
  let duel = act(fresh(), 'duel', 'START_DUEL');
  const actor = activeStackId(duel.battle);
  assert.throws(() => act(duel, 'illegal', 'BATTLE', { action: 'move', stackId: actor, to: [-1, -1] }), /Illegal|bounds|Not this/);
  assert.throws(() => act(fresh(), 'spend', 'SPEND_POINT', { stat: 'atk' }), /No spendable point/);
  assert.throws(() => act(fresh(), 'skill', 'CHOOSE_SKILL', { skill: 'offense' }), /Invalid skill offer/);
  const offer = forgeOffer(0, 1, 0);
  assert.deepEqual(offer.cost, { wood: 80, stone: 60, gold: 70 });
  assert.ok(gearBonus({ kind: 'gear', slot: 'weapon', age: 0, quality: 0 }).atk > 0);
});
