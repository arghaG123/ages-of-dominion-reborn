import test from 'node:test';
import assert from 'node:assert/strict';
import { defenseWaveLabel } from '../src/client/defense-wave-presentation.js';

test('active defense names the wave in progress rather than the number already cleared', () => {
  assert.equal(defenseWaveLabel({ status: 'ACTIVE', clearedWaves: 13, waves: 20 }), 'Wave 14 of 20');
});

test('a paused active session keeps its current wave label', () => {
  assert.equal(defenseWaveLabel({ status: 'ACTIVE', paused: true, clearedWaves: 3, waves: 6 }), 'Wave 4 of 6');
});

test('settled defense reports clears without inventing an active wave', () => {
  assert.equal(defenseWaveLabel({ status: 'RESOLVED', pendingSettlement: true, clearedWaves: 2, waves: 6 }), 'Waves cleared 2 of 6');
});

test('malformed wave horizons fail closed in presentation copy', () => {
  assert.equal(defenseWaveLabel({ status: 'ACTIVE', clearedWaves: 1, waves: 0 }), 'Wave unavailable');
});
