import test from 'node:test';
import assert from 'node:assert/strict';
import data from '../src/data/reference-data.json' with { type: 'json' };
import contract from '../src/data/implementation-contract.json' with { type: 'json' };
import { command, newCampaign, validate } from '../src/core/campaign.js';
import { legalTargets, meleeCommand, startBattle, strike, validateBattle } from '../src/core/battle.js';
import { decode, encode, load, save, SAVE_KEY } from '../src/core/save.js';
import { camera } from '../src/client/projection.js';

const fresh = () => newCampaign(contract, data, 1000);
const act = (state, id, type, payload, now = 1000) => command(state, { id, type, payload }, now, data);
const dwelling = contract.geometry.adventure.sites.find(site => site.id === 'dwelling');

function atDwelling(state) {
  state.adventure = {
    x: dwelling.approach[0], y: dwelling.approach[1], moves: 1,
    visited: [`${dwelling.approach[0]},${dwelling.approach[1]}`],
    resolvedGuards: [], pendingEncounter: null, atTown: false,
  };
  validate(state, data);
  return state;
}

const stack = (id, side, x, y, extra = {}) => ({
  id, side, x, y, count: 2, maxCount: 2, atk: 4, def: 4, dmin: 1, dmax: 1, uhp: 20, top: 20, spd: 4, rng: 0, shots: 0, fly: 0, ...extra,
});

test('dwelling claim checks capacity, site and tier before payment and keeps the saved offer', () => {
  const away = fresh();
  away.resources.gold = 10000;
  const awayGold = away.resources.gold;
  assert.throws(() => act(away, 'offer', 'OFFER_DWELLING', { type: 'wolf' }), /dwelling/);
  assert.equal(away.army.length, 2);
  assert.equal(away.resources.gold, awayGold);
  assert.equal(away.dwelling, null);

  let hosted = atDwelling(fresh());
  hosted.resources.gold = 10000;
  hosted = act(hosted, 'offer', 'OFFER_DWELLING', { type: 'wolf' });
  const saved = structuredClone(hosted.dwelling);
  assert.throws(() => act(hosted, 'bear', 'OFFER_DWELLING', { type: 'bear' }), /tier|already open/);
  const cancelled = act(hosted, 'cancel', 'CANCEL_DWELLING');
  assert.deepEqual(cancelled.dwelling, saved);
  const reloaded = decode(encode(cancelled, data), data);
  assert.deepEqual(reloaded.dwelling, saved);
  const before = structuredClone(reloaded);
  assert.throws(() => act(reloaded, 'claim', 'CLAIM_DWELLING', {}), /Army capacity/);
  assert.deepEqual(reloaded.army, before.army);
  assert.equal(reloaded.resources.gold, before.resources.gold);
  assert.deepEqual(reloaded.dwelling, saved);

  let room = atDwelling(fresh());
  const plot = room.plots.find(item => item.id === 'P01');
  plot.type = 'barracks';
  plot.level = 1;
  room.resources.gold = 10000;
  room = act(room, 'offer-room', 'OFFER_DWELLING', { type: 'wolf' });
  const claimed = act(room, 'claim-room', 'CLAIM_DWELLING', {});
  assert.equal(claimed.army.length, 3);
  assert.equal(claimed.army[2].type, 'wolf');
  assert.equal(claimed.resources.gold, 10000 - 35);
  assert.equal(claimed.dwelling.claimed, true);
  assert.throws(() => validate({ ...claimed, army: claimed.army.concat({ ...claimed.army[2], id: 'extra' }) }, data), /Army capacity/);
});

test('tactical saves reject corrupt numbers, empty queues, false victories and flyer water endings', () => {
  const battle = startBattle({
    id: 'probe', positioned: true, rngState: 4, mana: 10, wisdom: 1,
    stacks: [stack('p', 'p', 1, 3, { spd: 5 }), stack('e', 'e', 4, 3, { spd: 1 })],
  });
  const corrupt = (mutate, pattern) => {
    const copy = structuredClone(battle);
    mutate(copy);
    assert.throws(() => validateBattle(copy), pattern);
  };
  corrupt(b => { b.mana = -10; }, /mana/);
  corrupt(b => { b.queue = []; }, /queue/);
  corrupt(b => { b.stacks[0].dmin = -100; }, /damage/);
  corrupt(b => { b.stacks[0].maxCount = 0; }, /maxCount/);
  corrupt(b => { b.rngState = 2 ** 40; }, /32 bits/);
  corrupt(b => { b.status = 'RESOLVED'; b.pendingSettlement = true; b.outcome = { winner: 'p', reward: true }; }, /False resolved victory/);
  corrupt(b => { b.status = 'RESOLVED'; b.pendingSettlement = true; b.outcome = { winner: 'p', reward: false }; b.stacks[1].count = 0; b.stacks[1].dead = true; b.stacks[1].top = 0; }, /Corrupt settlement/);
  const flyer = structuredClone(battle);
  flyer.stacks[0].fly = 1;
  flyer.stacks[0].x = 3;
  flyer.stacks[0].y = 5;
  assert.throws(() => validateBattle(flyer), /Blocked-water/);
  assert.equal(validateBattle(battle), true);
});

test('advertised melee sends the legal approach and still rejects a remote hit', () => {
  const battle = startBattle({
    id: 'melee', positioned: true, rngState: 4, mana: 10, wisdom: 1,
    stacks: [stack('p', 'p', 1, 3, { spd: 5 }), stack('e', 'e', 4, 3, { spd: 1 })],
  });
  assert.deepEqual(legalTargets(battle, 'p').melee, ['e']);
  const payload = meleeCommand(battle, 'p', 'e');
  assert.equal(payload.forceMelee, true);
  assert.deepEqual(payload.approach, [3, 3]);
  assert.throws(() => strike(battle, 'p', 'e', { forceMelee: true }), /Not adjacent/);
  assert.equal(battle.stacks[0].x, 1);
  const struck = strike(battle, 'p', 'e', { forceMelee: true, approach: payload.approach });
  assert.equal(struck.stacks.find(item => item.id === 'p').x, 3);
  assert.ok(struck.log.some(entry => entry.type === 'strike'));
});

test('a damaged live save can be replaced without dropping the preserved bytes or the backup', () => {
  const memory = { values: new Map(), getItem(k) { return this.values.has(k) ? this.values.get(k) : null; }, setItem(k, v) { this.values.set(k, v); }, removeItem(k) { this.values.delete(k); } };
  const first = fresh();
  save(memory, first, data);
  const second = act(first, 'rival', 'CHOOSE_RIVAL', { name: 'Varek Iron-Eye' });
  save(memory, second, data);
  memory.setItem(SAVE_KEY, 'broken-save');
  const loaded = load(memory, data);
  assert.equal(loaded.status, 'DAMAGED');
  assert.deepEqual(loaded.backup, first);
  const next = newCampaign(contract, data, 5000, 99);
  save(memory, next, data);
  assert.equal(memory.getItem(SAVE_KEY + '-damaged'), 'broken-save');
  assert.deepEqual(load(memory, data).state.id, next.id);
  assert.equal(load(memory, data).state.clock, 5000);
});

test('short landscape stages keep one camera and at least 80 percent of the stage width', () => {
  for (const [width, height] of [[825, 263], [933, 312], [1180, 708], [1280, 608]]) {
    const fit = camera([1376, 768], width, height);
    const shown = Math.min(width, 1376 * fit.scale);
    assert.ok(shown / width >= 0.8, `${width}x${height} shows ${shown}`);
    assert.ok(fit.scale > 0);
  }
});
