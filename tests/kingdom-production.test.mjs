import test from 'node:test';
import assert from 'node:assert/strict';
import data from '../src/data/reference-data.json' with { type: 'json' };
import contract from '../src/data/implementation-contract.json' with { type: 'json' };
import { rates, newCampaign, cost, command } from '../src/core/campaign.js';
import { plotProduction, constructionDurationMs, formatConstructionDuration } from '../src/client/kingdom-production.js';

test('selected producer reports only its real rate, including its level', () => {
  const state = { plots: [
    { id: 'P01', type: 'lumber', level: 2 },
    { id: 'P02', type: 'lumber', level: 1 },
    { id: 'P03', type: 'farm', level: 3 },
  ] };

  const lumber = plotProduction(state, 'P01', rates);
  assert.equal(lumber.resource, 'wood');
  assert.ok(Math.abs(lumber.rate - 0.9) < 1e-12);
  const farm = plotProduction(state, 'P03', rates);
  assert.equal(farm.resource, 'food');
  assert.ok(Math.abs(farm.rate - 1.65) < 1e-12);
});

test('construction readout mirrors the duration committed by BUILD', () => {
  for (const building of ['lumber', 'quarry', 'townhall']) {
    const state = newCampaign(contract, data, 1000);
    const plot = building === 'townhall' ? state.plots.find(item => item.id === 'townhall') : state.plots.find(item => !item.type);
    const payment = cost(data, building, plot.level);
    state.resources = { ...state.resources, ...payment };
    const after = command(state, { id: 'duration-' + building, type: 'BUILD', payload: { plotId: plot.id, building } }, state.clock, data);
    const job = after.buildJobs.find(item => item.plotId === plot.id);
    assert.ok(job, building + ' should create a real construction job');
    assert.equal(job.completesAt - state.clock, constructionDurationMs(building, plot.level, payment));
  }
  assert.equal(formatConstructionDuration(3000), '3 seconds');
  assert.equal(formatConstructionDuration(3045), '3.1 seconds');
  assert.equal(formatConstructionDuration(8000), '8 seconds');
});

test('non-producing and missing sites have no production readout', () => {
  const state = { plots: [
    { id: 'P01', type: 'hall', level: 1 },
    { id: 'P02', type: null, level: 0 },
  ] };

  assert.equal(plotProduction(state, 'P01', rates), null);
  assert.equal(plotProduction(state, 'P02', rates), null);
  assert.equal(plotProduction(state, 'P99', rates), null);
});
