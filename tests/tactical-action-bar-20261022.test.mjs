import test from 'node:test';
import assert from 'node:assert/strict';
import { primaryModeRows, secondaryModeRows } from '../src/client/tactical-ui.js';

test('tactical action bar keeps the mock four visible actions and exposes bonus skip in the wait slot', () => {
  const normal = primaryModeRows({ melee: ['e1'], ranged: ['e2'], spells: 3, waited: false });
  assert.deepEqual(normal.map(row => row.label), ['Attack', 'Defend', 'Wait', 'Spell']);
  assert.equal(normal[0].enabled, true);
  assert.equal(normal[0].detail, '2 legal targets');
  assert.equal(normal[3].enabled, true);
  assert.equal(normal[3].reason, 'available');
  assert.equal(normal[3].detail, '3 casts · 1/round');

  const bonus = primaryModeRows({
    melee: [],
    ranged: [],
    spells: 0,
    waited: false,
    bonus: true,
    castThisRound: true,
    mana: 8,
    knownSpells: ['arrow'],
    minSpellCost: 4,
  });
  assert.deepEqual(bonus.map(row => row.label), ['Attack', 'Defend', 'Skip bonus', 'Spell']);
  assert.equal(bonus[0].enabled, false);
  assert.equal(bonus[2].enabled, true);
  assert.equal(bonus[3].enabled, false);
  assert.equal(bonus[3].reason, 'round-used');
  assert.equal(bonus[3].detail, 'Round cast used (1/round)');

  const zeroMana = primaryModeRows({
    melee: [],
    ranged: [],
    spells: 0,
    waited: false,
    castThisRound: false,
    mana: 0,
    knownSpells: ['arrow'],
    minSpellCost: 4,
  });
  assert.equal(zeroMana[3].enabled, false);
  assert.equal(zeroMana[3].reason, 'insufficient-mana');
  assert.equal(zeroMana[3].detail, 'Insufficient mana (0/4)');
});

test('movement, auto resolution and retreat remain available in secondary tactical actions', () => {
  const rows = secondaryModeRows({ moves: [[2, 7], [3, 7]] });
  assert.deepEqual(rows.map(row => row.id), ['move', 'auto', 'retreat']);
  assert.equal(rows[0].enabled, true);
  assert.equal(rows[0].detail, '2 open cells');
  assert.equal(rows[1].enabled, true);
  assert.equal(rows[2].enabled, true);

  assert.equal(secondaryModeRows({ moves: [] })[0].enabled, false);
});

