import test from 'node:test';
import assert from 'node:assert/strict';
import { bridgeOnRoute, dwellingRecruitLabel, travelCommitAction } from '../src/client/adventure-travel-presentation.js';

const bridges = [
  { id: 'west-arch', cells: [[3, 4], [4, 4]] },
  { id: 'central-stone', cells: [[8, 3], [9, 3]] },
];

test('a route through an authored bridge deck gets a bridge action and exact bridge identity', () => {
  const route = { cells: [[2, 4], [3, 4], [4, 4], [5, 4]], cost: 3 };
  assert.equal(bridgeOnRoute(route, bridges)?.id, 'west-arch');
  assert.deepEqual(travelCommitAction(route, bridges), {
    action: 'Cross Bridge',
    label: 'Cross Bridge · cost 3',
    bridgeId: 'west-arch',
  });
});

test('a route that avoids deck cells retains the ordinary confirmation copy', () => {
  const route = { path: [[2, 3], [2, 4], [2, 5]], cost: 2 };
  assert.equal(bridgeOnRoute(route, bridges), null);
  assert.deepEqual(travelCommitAction(route, bridges), {
    action: 'Confirm route',
    label: 'Confirm route · cost 2',
    bridgeId: null,
  });
});

test('an unselected route stays a non-action and never invents a bridge', () => {
  assert.equal(bridgeOnRoute(null, bridges), null);
  assert.deepEqual(travelCommitAction(null, bridges), {
    action: 'Confirm route',
    label: 'Confirm route',
    bridgeId: null,
  });
});

test('a dwelling offer uses recruit language while leaving its actual terms to the payment control', () => {
  assert.equal(dwellingRecruitLabel(5, 'Dire Wolves'), 'Recruit 5 Dire Wolves');
  assert.equal(dwellingRecruitLabel(0, ''), 'Recruit creatures');
});
