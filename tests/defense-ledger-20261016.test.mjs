import test from 'node:test';
import assert from 'node:assert/strict';
import data from '../src/data/reference-data.json' with { type: 'json' };
import contract from '../src/data/implementation-contract.json' with { type: 'json' };
import { advanceActiveDefense, command, newCampaign } from '../src/core/campaign.js';

test('internal defense steps do not append a transaction for every tick', () => {
  let state = newCampaign(contract, data, 1000);
  state = command(state, { id: 'siege-1', type: 'START_SIEGE', payload: {} }, 1000, data);
  const before = Object.keys(state.settledTransactions).length;
  const revision = state.revision;
  for (let i = 0; i < 40; i++) state = advanceActiveDefense(state, 0.25);
  assert.equal(Object.keys(state.settledTransactions).length, before);
  assert.equal(state.revision, revision);
  assert.equal(state.defense.status, 'ACTIVE');
  assert.ok(state.defense.steps > 0);
});
