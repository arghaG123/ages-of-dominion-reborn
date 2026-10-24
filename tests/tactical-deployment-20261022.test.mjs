import test from 'node:test';
import assert from 'node:assert/strict';
import data from '../src/data/reference-data.json' with { type: 'json' };
import contract from '../src/data/implementation-contract.json' with { type: 'json' };
import { command, newCampaign, validate } from '../src/core/campaign.js';
import { legalDeploymentCells } from '../src/core/battle.js';
import { decode, encode } from '../src/core/save.js';

const fresh = () => newCampaign(contract, data, 1_000);
const act = (state, id, type, payload = {}) => command(state, { id, type, payload }, state.clock, data);

test('Skirmish deployment uses copied campaign formations, legal placement, cancel and reload', () => {
  const original = fresh();
  original.tutorial.step = 6;
  const armyBefore = structuredClone(original.army);
  const resourcesBefore = structuredClone(original.resources);
  let state = act(original, 'setup', 'START_SKIRMISH');
  assert.equal(state.battle.status, 'PENDING');
  assert.equal(state.battle.deployment.movableIds.length, Math.min(3, original.army.length));
  assert.ok(state.battle.deployment.movableIds.length > 0);
  assert.equal(state.tutorial.step, 7);
  assert.ok(state.battle.stacks.filter(stack => stack.side === 'p').every(stack => stack.campaignId === null));

  const firstId = state.battle.deployment.movableIds[0];
  const legal = legalDeploymentCells(state.battle, firstId);
  assert.ok(legal.length > 0);
  assert.ok(legal.every(([x, y]) => x >= 0 && x < 3 && y >= 6 && y < 10));
  for (const [id, cell, reason] of [
    [firstId, [5, 6], 'outside the allied zone'],
    [firstId, [3, 7], 'water'],
    [firstId, [0, 5], 'cliff'],
    [firstId, [0, 9], 'commander cell'],
  ]) {
    assert.throws(() => act(state, `bad-${reason.replaceAll(' ', '-')}`, 'DEPLOY_BATTLE_STACK', { stackId: id, cell }), /Illegal deployment cell/);
  }
  assert.throws(() => act(state, 'start-empty', 'START_DEPLOYED_BATTLE'), /Place every formation/);

  state = act(state, 'place-first', 'DEPLOY_BATTLE_STACK', { stackId: firstId, cell: legal.find(([x, y]) => x === 1 && y === 7) ?? legal[0] });
  const secondId = state.battle.deployment.movableIds[1];
  if (secondId) assert.throws(() => act(state, 'occupy-first', 'DEPLOY_BATTLE_STACK', { stackId: secondId, cell: [state.battle.stacks.find(stack => stack.id === firstId).x, state.battle.stacks.find(stack => stack.id === firstId).y] }), /Illegal deployment cell/);
  state = decode(encode(state, data), data);
  assert.equal(state.battle.status, 'PENDING');
  assert.deepEqual(state.battle.deployment.placedIds, [firstId]);
  validate(state, data);

  const cancelled = act(state, 'cancel', 'CANCEL_BATTLE_SETUP');
  assert.equal(cancelled.battle, null);
  assert.equal(cancelled.tutorial.step, 6);
  assert.deepEqual(cancelled.army, armyBefore);
  assert.deepEqual(cancelled.resources, resourcesBefore);
});

test('Ready starts only after every copied formation is placed and Duel keeps fixed deployment', () => {
  let state = fresh();
  state = act(state, 'setup', 'START_SKIRMISH');
  const ids = [...state.battle.deployment.movableIds];
  const occupied = new Set();
  let sequence = 0;
  for (const stackId of ids) {
    const cell = legalDeploymentCells(state.battle, stackId).find(([x, y]) => !occupied.has(`${x},${y}`));
    assert.ok(cell);
    occupied.add(cell.join(','));
    state = act(state, `place-${sequence++}`, 'DEPLOY_BATTLE_STACK', { stackId, cell });
  }
  state = act(state, 'ready', 'START_DEPLOYED_BATTLE');
  assert.equal(state.battle.status, 'ACTIVE');
  assert.equal(state.battle.deployment, undefined);
  assert.ok(state.battle.queue.length > 0);
  assert.ok(ids.every(id => Number.isInteger(state.battle.stacks.find(stack => stack.id === id)?.x)));

  const fixed = act(fresh(), 'duel', 'START_DUEL');
  assert.equal(fixed.battle.status, 'ACTIVE');
  assert.equal(fixed.battle.deployment, undefined);
  assert.ok(fixed.battle.stacks.every(stack => Number.isInteger(stack.x) && Number.isInteger(stack.y)));
});
