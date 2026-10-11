import test from 'node:test';
import assert from 'node:assert/strict';
import { acceptMapActivation, defaultIntent, keepIntent, modeRows, moveLabel, retreatNotice, stackCaption, strikeLabel, spellLabel } from '../src/client/tactical-ui.js';

const legal = { moves: [[2, 9], [1, 8]], melee: ['e1'], ranged: [], };

test('tactical modes prefer a move and keep a still-legal choice', () => {
  assert.equal(defaultIntent(legal, 0), 'move');
  assert.equal(keepIntent('melee', legal, 0, false), 'melee');
  assert.equal(keepIntent('shoot', legal, 0, false), 'move');
  assert.equal(keepIntent('wait', { moves: [], melee: [], ranged: [] }, 0, true), 'defend');
});

test('tactical labels name the cell and the target without packing every action into one row', () => {
  const rows = modeRows({ moves: legal.moves, melee: legal.melee, ranged: [], spells: 2, waited: false });
  assert.equal(rows.length, 8);
  assert.deepEqual(rows.map(row => row.id), ['move', 'melee', 'shoot', 'spell', 'defend', 'wait', 'auto', 'retreat']);
  assert.equal(rows.find(row => row.id === 'shoot').enabled, false);
  assert.equal(moveLabel([0, 9]), 'Move to column 1, row 10');
  assert.equal(strikeLabel('melee', 'Wolf ×3 rank 0', 3), 'Strike Wolf ×3 rank 0 · 3 left');
  assert.equal(spellLabel('Stone Spikes', 'Wolf ×3 rank 0', 4), 'Stone Spikes on Wolf ×3 rank 0 · 4 mana');
});

test('map activation accepts one still-legal release and drops a stale or illegal one', () => {
  const armed = { key: 'move:2,9', kind: 'move', cell: [2, 9] };
  assert.deepEqual(acceptMapActivation({ armed, released: armed, intent: 'move', legal }), { action: 'move', to: [2, 9] });
  assert.equal(acceptMapActivation({ armed, released: { key: 'move:1,8', kind: 'move', cell: [1, 8] }, intent: 'move', legal }), null);
  assert.equal(acceptMapActivation({ armed, released: armed, intent: 'defend', legal }), null);
  assert.equal(acceptMapActivation({ armed, released: armed, intent: 'move', legal: { moves: [], melee: [], ranged: [] } }), null);
  assert.deepEqual(acceptMapActivation({
    armed: { key: 'melee:e1', kind: 'melee', id: 'e1' },
    released: { key: 'melee:e1', kind: 'melee', id: 'e1' },
    intent: 'melee',
    legal,
  }), { action: 'melee', targetId: 'e1' });
  assert.deepEqual(acceptMapActivation({
    armed: { key: 'shoot:e1', kind: 'shoot', id: 'e1' },
    released: { key: 'shoot:e1', kind: 'shoot', id: 'e1' },
    intent: 'shoot',
    legal: { moves: [], melee: [], ranged: ['e1'] },
  }), { action: 'strike', targetId: 'e1' });
});

test('retreat notice names the consequences and keeps cancel free of a resolution', () => {
  const campaign = retreatNotice('campaign');
  assert.match(campaign.body, /no victory gold/i);
  assert.match(campaign.body, /Cancel spends no turn/i);
  assert.equal(campaign.confirm, 'Confirm retreat');
  assert.equal(campaign.cancel, 'Cancel');
  const practice = retreatNotice('skirmish');
  assert.match(practice.body, /does not change campaign resources/i);
  assert.match(stackCaption({ title: 'Slinger', count: 5, hp: 22, maxHp: 55, action: 'move' }), /Slinger · 5 · 22\/55 hp · move/);
});
