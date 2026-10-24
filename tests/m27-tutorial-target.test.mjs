import test from 'node:test';
import assert from 'node:assert/strict';
import { plotPresentation, tutorialBuildSiteId } from '../src/client/kingdom-view.js';

const sites = [{ id: 'townhall' }, { id: 'P01' }, { id: 'P02' }];
const state = (step, plots = [
  { id: 'townhall', type: 'townhall', level: 1 },
  { id: 'P01', type: null, level: 0 },
  { id: 'P02', type: null, level: 0 },
], buildJobs = [], skipped = false) => ({ tutorial: { step, skipped }, plots, buildJobs });

test('M27 building steps highlight exactly the first empty idle non-town plot', () => {
  for (const step of [0, 1, 2, 3]) assert.equal(tutorialBuildSiteId(state(step), sites), 'P01');
});

test('M27 skips occupied, built, and in-progress sites before selecting a target', () => {
  const current = state(1, [
    { id: 'townhall', type: 'townhall', level: 1 },
    { id: 'P01', type: null, level: 0 },
    { id: 'P02', type: null, level: 0 },
  ], [{ plotId: 'P01' }]);
  assert.equal(tutorialBuildSiteId(current, sites), 'P02');
  current.plots[1] = { id: 'P01', type: 'farm', level: 1 };
  current.buildJobs = [];
  assert.equal(tutorialBuildSiteId(current, sites), 'P02');
});

test('M27 has no plot highlight after building steps, when skipped, or when no site is available', () => {
  assert.equal(tutorialBuildSiteId(state(4), sites), '');
  assert.equal(tutorialBuildSiteId(state(1, undefined, undefined, true), sites), '');
  assert.equal(tutorialBuildSiteId(state(1, [{ id: 'townhall', type: 'townhall', level: 1 }]), sites), '');
});
test('M27 keeps the tutorial presentation when its target is selected', () => {
  const presentation = plotPresentation({
    plot: { id: 'P01', type: null, level: 0 },
    job: null,
    measured: null,
    tutorialSiteId: 'P01',
    selected: true,
  });
  assert.equal(presentation.outline, 'tutorial');
});
