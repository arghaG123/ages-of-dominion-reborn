import test from 'node:test';
import assert from 'node:assert/strict';
import data from '../src/data/reference-data.json' with { type: 'json' };
import contract from '../src/data/implementation-contract.json' with { type: 'json' };
import { command, newCampaign, validate } from '../src/core/campaign.js';
import { checksum, decode, load, replaceCampaign, restoreBackup, save, SAVE_KEY } from '../src/core/save.js';

const fresh = () => newCampaign(contract, data, 1000);
const act = (state, id, type, payload) => command(state, { id, type, payload }, state.clock, data);
const wrap = state => {
  const payload = JSON.stringify(state);
  return JSON.stringify({ schema: 1, payload, checksum: checksum(payload) });
};

class ProbeMemory {
  values = new Map();
  corruptLive = false;
  failCleanup = false;
  getItem(k) { return this.values.has(k) ? this.values.get(k) : null; }
  setItem(k, v) { this.values.set(k, this.corruptLive && k === SAVE_KEY ? 'corrupt-live-write' : v); }
  removeItem(k) {
    if (this.failCleanup && k === SAVE_KEY + '-staged') throw new Error('Injected cleanup failure');
    this.values.delete(k);
  }
}

function prepared() {
  const memory = new ProbeMemory();
  let state = fresh();
  save(memory, state, data);
  state = act(state, 'rival', 'CHOOSE_RIVAL', { name: 'Varek Iron-Eye' });
  save(memory, state, data);
  return {
    memory,
    state,
    oldLive: memory.getItem(SAVE_KEY),
    oldBackup: memory.getItem(SAVE_KEY + '-backup'),
  };
}

test('fault injection: corrupt live write keeps the latest valid campaign recoverable', () => {
  // Failure injection, not an observed ordinary browser-storage failure.
  const { memory, oldLive, oldBackup } = prepared();
  const incoming = fresh();
  incoming.hero.class = 'mage';
  memory.corruptLive = true;
  assert.throws(() => replaceCampaign(memory, incoming, data), /Live save verification failed/);
  memory.corruptLive = false;
  assert.notEqual(memory.getItem(SAVE_KEY), oldLive);
  assert.equal(memory.getItem(SAVE_KEY), 'corrupt-live-write');
  assert.notEqual(memory.getItem(SAVE_KEY + '-backup'), oldBackup);
  const loaded = load(memory, data);
  assert.equal(loaded.status, 'DAMAGED');
  assert.equal(loaded.state, null);
  assert.equal(loaded.backup?.story.rival, 'Varek Iron-Eye');
  assert.equal(memory.getItem(SAVE_KEY + '-damaged'), 'corrupt-live-write');
  const staged = memory.getItem(SAVE_KEY + '-staged');
  assert.ok(staged);
  assert.equal(decode(staged, data).hero.class, 'mage');
  const restored = restoreBackup(memory, data);
  assert.equal(restored.story.rival, 'Varek Iron-Eye');
  assert.equal(load(memory, data).status, 'VALID');
  assert.equal(load(memory, data).state.story.rival, 'Varek Iron-Eye');
});

test('fault injection: staged cleanup debt does not disguise a durable commit', () => {
  // Failure injection, not an observed ordinary browser-storage failure.
  const { memory, state: prior } = prepared();
  const incoming = fresh();
  incoming.hero.class = 'mage';
  memory.failCleanup = true;
  const stored = replaceCampaign(memory, incoming, data);
  memory.failCleanup = false;
  assert.equal(stored.hero.class, 'mage');
  assert.ok(stored.revision > prior.revision);
  const loaded = load(memory, data);
  assert.equal(loaded.status, 'VALID');
  assert.equal(loaded.state.hero.class, 'mage');
  assert.equal(loaded.state.story.rival, null);
  assert.equal(loaded.state.revision, stored.revision);
  assert.equal(memory.getItem(SAVE_KEY + '-staged'), memory.getItem(SAVE_KEY));
  assert.throws(() => save(memory, prior, data), /stale/);
  save(memory, loaded.state, data);
  assert.equal(memory.getItem(SAVE_KEY + '-staged'), null);
  assert.equal(load(memory, data).state.hero.class, 'mage');
});

test('present null story and quest fields stay damaged and keep their bytes', () => {
  const edits = [
    ['chapter-null', s => { s.story.chapter = null; }],
    ['choices-null', s => { s.story.choices = null; }],
    ['futureSeen-null', s => { s.story.futureSeen = null; }],
    ['milestones-null', s => { s.story.milestones = null; }],
    ['quests-null', s => { s.quests = null; }],
    ['q1-null', s => { s.quests.q1 = null; }],
    ['flags-null', s => { s.story.flags = null; }],
  ];
  for (const [id, edit] of edits) {
    const sample = fresh();
    edit(sample);
    assert.throws(() => validate(sample, data), id);
    const raw = wrap(sample);
    assert.throws(() => decode(raw, data), id);
    const memory = new ProbeMemory();
    memory.setItem(SAVE_KEY, raw);
    const loaded = load(memory, data);
    assert.equal(loaded.status, 'DAMAGED', id);
    assert.equal(memory.getItem(SAVE_KEY), raw, id);
  }
});

test('absent legacy story fields still migrate; wrong-type and chapter mismatch stay damaged', () => {
  const legacy = fresh();
  delete legacy.story.chapter;
  delete legacy.story.choices;
  delete legacy.story.futureSeen;
  delete legacy.story.milestones;
  delete legacy.story.flags;
  delete legacy.quests;
  const migrated = decode(wrap(legacy), data);
  assert.equal(migrated.story.chapter, 0);
  assert.deepEqual(migrated.story.choices, []);
  assert.equal(migrated.story.futureSeen, false);
  assert.deepEqual(migrated.story.milestones, {});
  assert.deepEqual(migrated.story.flags, {});
  for (const quest of data.QUEST_TEMPLATES) assert.equal(migrated.quests[quest.id].claimed, false);

  for (const edit of [
    s => { s.story.chapter = '7'; },
    s => { s.quests.q1.claimed = 'yes'; },
    s => { s.story.chapter = 1; s.story.choices = []; },
  ]) {
    const sample = fresh();
    edit(sample);
    const raw = wrap(sample);
    assert.throws(() => decode(raw, data));
    const memory = new ProbeMemory();
    memory.setItem(SAVE_KEY, raw);
    assert.equal(load(memory, data).status, 'DAMAGED');
    assert.equal(memory.getItem(SAVE_KEY), raw);
  }
});
