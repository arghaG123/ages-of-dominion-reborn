import test from 'node:test';
import assert from 'node:assert/strict';
import { crossingPresentation, routeWithCurrentCell, shouldAutoCloseCrossingPanel } from '../src/client/adventure-crossing-presentation.js';
import { travelCommitAction } from '../src/client/adventure-travel-presentation.js';

const bridges = [
  { id: 'central-stone-bridge', cells: [[8, 3], [9, 3]], approaches: [[7, 3], [10, 3]] },
  { id: 'west-river-arch', cells: [[3, 4], [4, 4]], approaches: [[2, 4], [5, 4]] },
];
test('the crossing focus is registered only on its authored grasslands bridge cells', () => {
 const focus = crossingPresentation('grasslands', { x: 9, y: 3 }, bridges);
  assert.equal(focus.bridgeId, 'central-stone-bridge');
  assert.equal(focus.file, 'assets/derivatives/adventure-crossing-focus-20261023/grasslands-central-bridge-focus-v1.png');
  assert.deepEqual(focus.sourceRect, [774, 223, 342, 192]);
  assert.equal(crossingPresentation('grasslands', { x: 10, y: 3 }, bridges), null);
  assert.equal(crossingPresentation('frozen-north', { x: 9, y: 3 }, bridges), null);
});

test('a previewed route focuses the authored bridge before movement is committed', () => {
  const focus = crossingPresentation('grasslands', { x: 7, y: 3 }, bridges, { path: [[8, 3]], cost: 1 });
  assert.equal(focus.bridgeId, 'central-stone-bridge');
  assert.equal(crossingPresentation('grasslands', { x: 7, y: 3 }, bridges, { cells: [[7, 4], [6, 4]], cost: 2 }), null);
  assert.equal(crossingPresentation('grasslands', { x: 6, y: 5 }, bridges, { cells: [[6, 4], [7, 4], [8, 3]], cost: 8 }), null);
});

test('a route leaving the bridge deck keeps the crossing action and exact one-move cost', () => {
  const route = { cells: [[10, 3]], cost: 1 };
  const displayedRoute = routeWithCurrentCell(route, [9, 3]);
  assert.deepEqual(displayedRoute.cells, [[9, 3], [10, 3]]);
  assert.deepEqual(travelCommitAction(displayedRoute, bridges), {
    action: 'Cross Bridge',
    label: 'Cross Bridge · cost 1',
    bridgeId: 'central-stone-bridge',
  });
  assert.deepEqual(route.cells, [[10, 3]]);
});

test('a missing route or position is passed through without inventing a crossing', () => {
  assert.equal(routeWithCurrentCell(null, [9, 3]), null);
  assert.deepEqual(routeWithCurrentCell({ path: [[4, 4]], cost: 1 }, null), { path: [[4, 4]], cost: 1 });
});

test('crossing focus closes incidental panels but preserves an explicit Travel and sites request', () => {
  const crossingFocus = { bridgeId: 'central-stone-bridge' };
  assert.equal(shouldAutoCloseCrossingPanel({ crossingFocus, panelOpen: true }), true);
  assert.equal(shouldAutoCloseCrossingPanel({ crossingFocus, panelOpen: true, explicitNavigation: true }), false);
  assert.equal(shouldAutoCloseCrossingPanel({ crossingFocus, panelOpen: true, menuSheet: true }), false);
  assert.equal(shouldAutoCloseCrossingPanel({ crossingFocus, panelOpen: true, resourceSheet: true }), false);
  assert.equal(shouldAutoCloseCrossingPanel({ crossingFocus: null, panelOpen: true }), false);
});
