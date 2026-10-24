import test from 'node:test';
import assert from 'node:assert/strict';
import {
  acceptMapActivation,
  battleSpellAvailability,
  defaultIntent,
  intentSentence,
  keepIntent,
  modeRows,
  moveLabel,
  retreatBlocksBackground,
  retreatNotice,
  spellAvailability,
  spellLabel,
  stackCaption,
  strikeLabel,
  tacticalHeroPlaqueCopy,
  viewDuringRetreat,
} from '../src/client/tactical-ui.js';

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

test('an open Retreat blocks background navigation and keeps the battle on Tactical', () => {
  assert.equal(retreatBlocksBackground({ retreatArmed: true, inDialog: false }), true);
  assert.equal(retreatBlocksBackground({ retreatArmed: true, inDialog: true }), false);
  assert.equal(retreatBlocksBackground({ retreatArmed: false, inDialog: false }), false);
  assert.equal(viewDuringRetreat('kingdom', { retreatArmed: true, battleActive: true }), 'tactical');
  assert.equal(viewDuringRetreat('tactical', { retreatArmed: true, battleActive: true }), 'tactical');
  assert.equal(viewDuringRetreat('kingdom', { retreatArmed: false, battleActive: true }), 'kingdom');
  assert.equal(viewDuringRetreat('kingdom', { retreatArmed: true, battleActive: false }), 'kingdom');
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

test('spell guidance states one cast per round and distinguishes round-used, insufficient-mana, no-known-spell, and no-target', () => {
  assert.equal(intentSentence('spell', 'Warrior'), 'Choose one listed cast. Your hero casts once per battle round.');
  assert.match(intentSentence('spell', 'Warrior', { castThisRound: true, mana: 9, knownSpells: ['arrow'], minSpellCost: 4 }), /Round cast used/i);
  assert.match(intentSentence('spell', 'Warrior', { castThisRound: false, mana: 0, knownSpells: ['arrow'], minSpellCost: 4 }), /0\/4/i);

  const used = spellAvailability({ spells: 0, castThisRound: true, mana: 8, knownSpells: ['arrow', 'bless'], minSpellCost: 4 });
  assert.equal(used.reason, 'round-used');
  assert.equal(used.detail, 'Round cast used (1/round)');

  const lowMana = spellAvailability({ spells: 0, castThisRound: false, mana: 0, knownSpells: ['arrow'], minSpellCost: 4 });
  assert.equal(lowMana.reason, 'insufficient-mana');
  assert.equal(lowMana.detail, 'Insufficient mana (0/4)');

  const noKnown = spellAvailability({ spells: 0, castThisRound: false, mana: 10, knownSpells: [] });
  assert.equal(noKnown.reason, 'no-known-spell');
  assert.equal(noKnown.detail, 'No known spell');

  const noTarget = spellAvailability({ spells: 0, castThisRound: false, mana: 10, knownSpells: ['resurrect'], minSpellCost: 9 });
  assert.equal(noTarget.reason, 'no-target');
  assert.equal(noTarget.detail, 'No legal spell target');

  const fromBattle = battleSpellAvailability(
    { castThisRound: true, mana: 6, wisdom: 1, stacks: [] },
    { arrow: { mana: 4, lv: 1, type: 'dmg' }, bless: { mana: 5, lv: 1, type: 'buff' } }
  );
  assert.equal(fromBattle.reason, 'round-used');
});

test('battleSpellAvailability evaluates live battle stacks across all five cast states and zero-count targets', () => {
  const spellbook = {
    arrow: { mana: 5, lv: 1, type: 'dmg' },
    bolt: { mana: 10, lv: 2, type: 'dmg' },
  };
  const ready = battleSpellAvailability(
    { castThisRound: false, mana: 8, wisdom: 1, stacks: [{ id: 'p1', side: 'p', dead: false, count: 4 }, { id: 'e1', side: 'e', dead: false, count: 3 }] },
    spellbook
  );
  assert.equal(ready.enabled, true);
  assert.equal(ready.reason, 'available');
  assert.equal(ready.offers.length, 1);

  const noTarget = battleSpellAvailability(
    { castThisRound: false, mana: 8, wisdom: 1, stacks: [{ id: 'p1', side: 'p', dead: false, count: 4 }, { id: 'e1', side: 'e', dead: false, count: 0 }] },
    spellbook
  );
  assert.equal(noTarget.enabled, false);
  assert.equal(noTarget.reason, 'no-target');
  assert.match(intentSentence('spell', 'Warrior', noTarget), /no legal target/i);

  const lowMana = battleSpellAvailability(
    { castThisRound: false, mana: 3, wisdom: 1, stacks: [{ id: 'e1', side: 'e', dead: false, count: 3 }] },
    spellbook
  );
  assert.equal(lowMana.reason, 'insufficient-mana');
  assert.equal(lowMana.detail, 'Insufficient mana (3/5)');

  const noKnown = battleSpellAvailability(
    { castThisRound: false, mana: 12, wisdom: -1, stacks: [{ id: 'e1', side: 'e', dead: false, count: 3 }] },
    spellbook
  );
  assert.equal(noKnown.reason, 'no-known-spell');
  assert.match(intentSentence('spell', 'Warrior', noKnown), /no known spell at current Wisdom/i);
});

test('tactical hero plaque copy keeps zero mana visible and accessible in ariaLabel', () => {
  const withMana = tacticalHeroPlaqueCopy({
    heroName: 'Aegis',
    classTitle: 'Warrior',
    level: 2,
    xp: 22,
    mana: 9,
  });
  assert.equal(withMana.subtext, 'XP 22 · Mana 9');
  assert.match(withMana.ariaLabel, /battle mana 9\./);

  const zeroMana = tacticalHeroPlaqueCopy({
    heroName: 'Aegis',
    classTitle: 'Warrior',
    level: 2,
    xp: 22,
    mana: 0,
  });
  assert.equal(zeroMana.subtext, 'XP 22 · Mana 0');
  assert.match(zeroMana.ariaLabel, /battle mana 0\./);
});
