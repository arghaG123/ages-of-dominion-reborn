import test from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import contract from '../src/data/implementation-contract.json' with { type: 'json' };
import data from '../src/data/reference-data.json' with { type: 'json' };
import scene from '../src/data/stone-scene.json' with { type: 'json' };
import report from '../qa/recovery-v3-20261003/report.json' with { type: 'json' };
import { newCampaign, command } from '../src/core/campaign.js';
import { project } from '../src/client/projection.js';

test('eight ages, six slots and blocked combat stay in scope', () => {
  assert.deepEqual(contract.ages, ['stone', 'bronze', 'iron', 'medieval', 'gunpowder', 'industrial', 'modern', 'future']);
  assert.deepEqual(contract.slots, ['helm', 'weapon', 'offhand', 'armor', 'boots', 'accessory']);
  assert.equal(contract.geometry.kingdom.sites.length, 18);
  const state = newCampaign(contract, data, 1000);
  assert.equal(state.plots.find(plot => plot.id === 'townhall').level, 1);
  assert.equal(state.walls.level, 0);
  assert.throws(() => command(state, { id: 'fight', type: 'RESOLVE_COMBAT', payload: {} }, 1000, data), /Unsupported/);
});

test('Stone Hall contact uses the shared kingdom camera without a second transform', () => {
  const hall = contract.geometry.kingdom.sites.find(site => site.id === 'townhall');
  const [x, y, w, h] = hall.rect;
  const destination = project(contract.geometry.kingdom.worldToSource, [x + w / 2, y + h / 2]);
  const [cx, cy] = report.hall.registration.centroid;
  const matrix = scene.hall.matrix;
  const placed = [matrix[0][0] * cx + matrix[0][1] * cy + matrix[0][2], matrix[1][0] * cx + matrix[1][1] * cy + matrix[1][2]];
  assert.ok(Math.abs(placed[0] - destination[0]) < 0.2);
  assert.ok(Math.abs(placed[1] - destination[1]) < 0.2);
  assert.equal(matrix[0][0], matrix[1][1]);
  assert.equal(matrix[0][1], 0);
  assert.equal(matrix[1][0], 0);
  assert.deepEqual(scene.camera, contract.geometry.kingdom.worldToSource);
  assert.equal(scene.runtimeApproved, false);
  assert.equal(scene.ownerAcceptance, 'UNVERIFIED');
  const bytes = readFileSync(new URL('../' + scene.hall.file, import.meta.url));
  assert.equal(createHash('sha256').update(bytes).digest('hex'), scene.hall.sha256);
});
