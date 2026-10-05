import test from 'node:test';
import assert from 'node:assert/strict';
import data from '../src/data/reference-data.json' with { type: 'json' };
import contract from '../src/data/implementation-contract.json' with { type: 'json' };
import { command, newCampaign, validate } from '../src/core/campaign.js';
import { legalTargets, meleeCommand, startBattle, strike, validateBattle } from '../src/core/battle.js';
import { checksum, decode, encode, load, replaceCampaign, restoreBackup, save, SAVE_KEY } from '../src/core/save.js';
import scene from '../src/data/stone-scene.json' with { type: 'json' };
import { camera, inverse, kingdomFocusBounds, project, TARGET_PX, targetSourceSize } from '../src/client/projection.js';

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
  const memory = {
    values: new Map(), failAt: null,
    getItem(k) { return this.values.has(k) ? this.values.get(k) : null; },
    setItem(k, v) { if (k === this.failAt) throw new Error('Quota exceeded'); this.values.set(k, v); },
    removeItem(k) { this.values.delete(k); },
  };
  const first = fresh();
  save(memory, first, data);
  const second = act(first, 'rival', 'CHOOSE_RIVAL', { name: 'Varek Iron-Eye' });
  save(memory, second, data);
  const backup = memory.getItem(SAVE_KEY + '-backup');
  memory.setItem(SAVE_KEY, 'broken-save');
  const loaded = load(memory, data);
  assert.equal(loaded.status, 'DAMAGED');
  assert.deepEqual(loaded.backup, first);
  memory.failAt = SAVE_KEY;
  const next = newCampaign(contract, data, 5000, 99);
  assert.throws(() => save(memory, next, data), /Quota/);
  assert.equal(memory.getItem(SAVE_KEY), 'broken-save');
  assert.equal(memory.getItem(SAVE_KEY + '-backup'), backup);
  assert.equal(memory.getItem(SAVE_KEY + '-damaged'), 'broken-save');
  memory.failAt = null;
  save(memory, next, data);
  assert.equal(memory.getItem(SAVE_KEY + '-damaged'), 'broken-save');
  assert.equal(memory.getItem(SAVE_KEY + '-backup'), backup);
  assert.deepEqual(decode(backup, data), first);
  assert.equal(load(memory, data).state.id, next.id);
  assert.equal(load(memory, data).state.clock, 5000);
  assert.throws(() => restoreBackup(memory, data), /Live save is valid/);
  assert.equal(load(memory, data).state.id, next.id);
  memory.setItem(SAVE_KEY, 'broken-again');
  const restored = restoreBackup(memory, data);
  assert.deepEqual(restored, first);
  assert.equal(load(memory, data).state.revision, first.revision);
  assert.equal(memory.getItem(SAVE_KEY + '-damaged'), 'broken-save');
});

test('a quota failure while replacing a valid campaign keeps the latest live recoverable', () => {
  const memory = {
    values: new Map(), failAt: null,
    getItem(k) { return this.values.has(k) ? this.values.get(k) : null; },
    setItem(k, v) { if (k === this.failAt) throw new Error('Quota exceeded'); this.values.set(k, v); },
    removeItem(k) { this.values.delete(k); },
  };
  const first = fresh();
  save(memory, first, data);
  const second = act(first, 'rival', 'CHOOSE_RIVAL', { name: 'Varek Iron-Eye' });
  save(memory, second, data);
  const liveBefore = memory.getItem(SAVE_KEY);
  memory.failAt = SAVE_KEY;
  const third = act(second, 'rival2', 'STORY_CHOICE', { index: 0 }, second.clock);
  assert.throws(() => save(memory, third, data), /Quota/);
  assert.deepEqual(load(memory, data).state.story.rival, 'Varek Iron-Eye');
  // Promotion already copied the latest valid live into backup; do not roll that back to older bookkeeping.
  assert.equal(memory.getItem(SAVE_KEY + '-backup'), liveBefore);
  assert.equal(decode(memory.getItem(SAVE_KEY + '-backup'), data).story.rival, 'Varek Iron-Eye');
  // Verified staged bytes of the failed write remain until a later durable commit clears them.
  assert.equal(decode(memory.getItem(SAVE_KEY + '-staged'), data).story.chapter, 1);
});

test('a save from before story fields still loads', () => {
  const memory = {
    values: new Map(),
    getItem(k) { return this.values.has(k) ? this.values.get(k) : null; },
    setItem(k, v) { this.values.set(k, v); },
    removeItem(k) { this.values.delete(k); },
  };
  const legacy = fresh();
  delete legacy.story.chapter;
  delete legacy.story.choices;
  delete legacy.story.futureSeen;
  delete legacy.story.milestones;
  delete legacy.quests;
  const payload = JSON.stringify(legacy);
  memory.setItem(SAVE_KEY, JSON.stringify({ schema: 1, payload, checksum: checksum(payload) }));
  const loaded = load(memory, data);
  assert.equal(loaded.status, 'VALID');
  assert.equal(loaded.state.story.chapter, 0);
  assert.equal(loaded.state.quests.q5.claimed, false);
  assert.equal(loaded.state.story.rival, null);
});

function memoryStore() {
  return {
    values: new Map(), failAt: null, corruptStaged: false,
    getItem(k) {
      if (this.corruptStaged && k === SAVE_KEY + '-staged') return 'corrupt-staged';
      return this.values.has(k) ? this.values.get(k) : null;
    },
    setItem(k, v) { if (k === this.failAt) throw new Error('Quota exceeded'); this.values.set(k, v); },
    removeItem(k) { this.values.delete(k); },
  };
}
function wrap(state) {
  const payload = JSON.stringify(state);
  return JSON.stringify({ schema: 1, payload, checksum: checksum(payload) });
}

test('intentional replacement keeps a lower revision and autosave still refuses it', () => {
  const memory = memoryStore();
  const first = fresh();
  save(memory, first, data);
  const live = act(first, 'rival', 'CHOOSE_RIVAL', { name: 'Varek Iron-Eye' });
  save(memory, live, data);
  const liveBefore = memory.getItem(SAVE_KEY);
  const older = fresh();
  older.hero.class = 'mage';
  assert.throws(() => save(memory, older, data), /stale/);
  assert.equal(load(memory, data).state.story.rival, 'Varek Iron-Eye');
  memory.failAt = SAVE_KEY;
  assert.throws(() => replaceCampaign(memory, older, data), /Quota/);
  assert.equal(memory.getItem(SAVE_KEY + '-backup'), liveBefore);
  assert.equal(decode(memory.getItem(SAVE_KEY + '-backup'), data).story.rival, 'Varek Iron-Eye');
  assert.equal(decode(memory.getItem(SAVE_KEY + '-staged'), data).hero.class, 'mage');
  assert.equal(load(memory, data).state.story.rival, 'Varek Iron-Eye');
  memory.failAt = null;
  memory.corruptStaged = true;
  assert.throws(() => replaceCampaign(memory, older, data), /Staged save verification failed/);
  assert.equal(load(memory, data).state.story.rival, 'Varek Iron-Eye');
  memory.corruptStaged = false;
  const stored = replaceCampaign(memory, older, data);
  assert.ok(stored.revision > live.revision);
  assert.equal(load(memory, data).state.hero.class, 'mage');
  assert.equal(load(memory, data).state.story.rival, null);
  assert.equal(load(memory, data).state.revision, stored.revision);
  assert.equal(decode(memory.getItem(SAVE_KEY + '-backup'), data).story.rival, 'Varek Iron-Eye');
  assert.throws(() => save(memory, live, data), /stale/);
  assert.throws(() => save(memory, older, data), /stale/);
  assert.throws(() => decode(JSON.stringify({ schema: 2, payload: '{}', checksum: '00000000' }), data), /Unsupported save envelope/);
  assert.equal(load(memory, data).state.hero.class, 'mage');
});

test('malformed present story fields stay damaged and keep their bytes', () => {
  const samples = [];
  const mismatch = fresh();
  mismatch.story.chapter = 1;
  mismatch.story.choices = [];
  samples.push(mismatch);
  const claimed = fresh();
  claimed.story.chapter = 1;
  claimed.story.choices = [data.STORY[0].ch[0].flag];
  claimed.quests.q1.claimed = 'yes';
  samples.push(claimed);
  const chapter = fresh();
  chapter.story.chapter = 1.5;
  samples.push(chapter);
  for (const sample of samples) {
    assert.throws(() => validate(sample, data));
    const raw = wrap(sample);
    const memory = memoryStore();
    memory.setItem(SAVE_KEY, raw);
    const loaded = load(memory, data);
    assert.equal(loaded.status, 'DAMAGED');
    assert.equal(loaded.state, null);
    assert.equal(memory.getItem(SAVE_KEY), raw);
    assert.throws(() => decode(raw, data));
  }
});

test('all 18 kingdom targets stay inside short stages, safe area and an open panel', () => {
  const geo = contract.geometry.kingdom;
  const focus = kingdomFocusBounds(geo, scene.hall);
  const closed = [[825, 263], [933, 312], [1180, 708], [1280, 608]];
  const open = [[577, 263], [685, 312], [892, 708], [992, 608]];
  const safe = [[777, 215], [885, 264], [1132, 660], [1232, 560]];
  const sparse = focus;
  const mature = kingdomFocusBounds(geo, scene.hall);
  assert.deepEqual(sparse, mature);
  for (const [width, height] of [...closed, ...open, ...safe]) {
    const fit = camera([1376, 768], width, height, focus, 24);
    assert.equal(fit.offset.length, 2);
    assert.ok(fit.scale > 0);
    const place = point => [point[0] * fit.scale + fit.offset[0], point[1] * fit.scale + fit.offset[1]];
    for (const site of geo.sites) {
      const [x, y, w, h] = site.rect;
      const source = project(geo.worldToSource, [x + w / 2, y + h / 2]);
      const centre = place(source);
      assert.ok(centre[0] >= 24 && centre[1] >= 24 && centre[0] <= width - 24 && centre[1] <= height - 24, `${site.id} at ${centre} on ${width}x${height}`);
      const size = targetSourceSize(fit.scale);
      assert.ok(Math.abs(size * fit.scale - TARGET_PX) < 1e-6);
      const half = TARGET_PX / 2;
      assert.ok(centre[0] - half >= -1e-6 && centre[1] - half >= -1e-6 && centre[0] + half <= width + 1e-6 && centre[1] + half <= height + 1e-6, site.id);
      for (const edge of [[centre[0] - half + 0.5, centre[1]], [centre[0] + half - 0.5, centre[1]], [centre[0], centre[1] - half + 0.5], [centre[0], centre[1] + half - 0.5]]) {
        const back = [(edge[0] - fit.offset[0]) / fit.scale, (edge[1] - fit.offset[1]) / fit.scale];
        assert.ok(Math.abs(back[0] - source[0]) <= size / 2 && Math.abs(back[1] - source[1]) <= size / 2, site.id);
        inverse(geo.worldToSource, back);
      }
    }
  }
});
