import test from 'node:test';
import assert from 'node:assert/strict';
import data from '../src/data/reference-data.json' with { type: 'json' };
import contract from '../src/data/implementation-contract.json' with { type: 'json' };
import { command, futureConclusion, newCampaign, questReady, stackTitle, validate } from '../src/core/campaign.js';
import { decode, encode, load, save, storeSlot, loadSlot } from '../src/core/save.js';
import { GEAR_SLOTS } from '../src/core/rules.js';

const fresh = () => newCampaign(contract, data, 1000);
const act = (state, id, type, payload, now = 1000) => command(state, { id, type, payload }, now, data);
class Memory {
  values = new Map();
  getItem(k) { return this.values.has(k) ? this.values.get(k) : null; }
  setItem(k, v) { this.values.set(k, v); }
  removeItem(k) { this.values.delete(k); }
}

test('seven chapters, future conclusion and rival survive reload without a second grant', () => {
  let state = act(fresh(), 'rival', 'CHOOSE_RIVAL', { name: 'Varek Iron-Eye' });
  assert.throws(() => act(state, 'bad-rival', 'CHOOSE_RIVAL', { name: 'nobody' }), /already chosen/);
  const before = state.resources.food;
  assert.throws(() => act(state, 'bad-choice', 'STORY_CHOICE', { index: 9 }), /Invalid choice/);
  assert.equal(state.resources.food, before);
  state = act(state, 'c0', 'STORY_CHOICE', { index: 0 });
  assert.equal(state.resources.food, before + data.STORY[0].ch[0].fx.food);
  assert.equal(state.story.chapter, 1);
  assert.equal(state.story.flags.generous, true);
  const once = state.resources.food;
  state = act(state, 'c0', 'STORY_CHOICE', { index: 0 });
  assert.equal(state.resources.food, once);
  for (let chapter = 1; chapter < data.STORY.length; chapter++) {
    const before = structuredClone(state.resources);
    assert.throws(() => act(state, 'early-' + chapter, 'STORY_CHOICE', { index: 0 }, state.clock), /not open/);
    assert.deepEqual(state.resources, before);
    state.age = chapter;
    state = act(state, 'c' + chapter, 'STORY_CHOICE', { index: 0 }, state.clock);
  }
  assert.equal(state.story.chapter, 7);
  assert.throws(() => act(state, 'late', 'ACK_FUTURE', {}, state.clock), /not open/);
  state.age = 7;
  const resources = structuredClone(state.resources);
  state = act(state, 'future', 'ACK_FUTURE', {}, state.clock);
  assert.deepEqual(state.resources, resources);
  assert.equal(state.story.futureSeen, true);
  assert.match(futureConclusion(state, data), /The Valley We Keep/);
  assert.match(futureConclusion(state, data), /Varek Iron-Eye/);
  assert.match(futureConclusion(state, data), /shared the first fire/);
  assert.throws(() => act(state, 'future-2', 'ACK_FUTURE', {}, state.clock), /already kept/);
  const memory = new Memory();
  save(memory, state, data);
  assert.equal(load(memory, data).state.story.futureSeen, true);
  assert.equal(decode(encode(state, data), data).story.choices.length, 7);
});

test('a false cleared flag is not a win and cannot be saved', () => {
  const state = fresh();
  state.story.flags['cleared:one'] = false;
  assert.equal(questReady(state, data, 'q1'), false);
  assert.throws(() => validate(state, data), /Invalid battle record/);
  state.story.flags['cleared:one'] = true;
  assert.equal(questReady(state, data, 'q1'), true);
});

test('quest claims are once-only and full gear means six slots', () => {
  let state = fresh();
  assert.throws(() => act(state, 'q', 'CLAIM_QUEST', { id: 'q1' }), /not complete/);
  state.story.flags['cleared:one'] = true;
  const gold = state.resources.gold;
  state = act(state, 'q1', 'CLAIM_QUEST', { id: 'q1' });
  assert.equal(state.resources.gold, gold + data.QUEST_TEMPLATES[0].rw.gold);
  assert.throws(() => act(state, 'q1b', 'CLAIM_QUEST', { id: 'q1' }, state.clock), /already claimed/);
  assert.equal(state.resources.gold, gold + data.QUEST_TEMPLATES[0].rw.gold);
  for (const slot of GEAR_SLOTS.slice(0, 5)) state.hero.equip[slot] = { id: 'gear-' + slot, kind: 'gear', slot, age: 0, quality: 0 };
  assert.equal(questReady(state, data, 'q5'), false);
  state.hero.equip.accessory = { id: 'gear-accessory', kind: 'gear', slot: 'accessory', age: 0, quality: 0 };
  assert.equal(questReady(state, data, 'q5'), true);
  state = act(state, 'q5', 'CLAIM_QUEST', { id: 'q5' }, state.clock);
  assert.equal(state.quests.q5.claimed, true);
  state.story.milestones = {};
  state = act(state, 'm0', 'CLAIM_MILESTONE', { age: 0 }, state.clock);
  assert.equal(state.story.milestones[0], true);
  assert.throws(() => act(state, 'm0b', 'CLAIM_MILESTONE', { age: 0 }, state.clock), /already claimed/);
  assert.throws(() => act(state, 'm7', 'CLAIM_MILESTONE', { age: 7 }, state.clock), /not reached/);
  const memory = new Memory();
  save(memory, state, data);
  storeSlot(memory, 1, state, data);
  assert.equal(loadSlot(memory, 1, data).quests.q5.claimed, true);
  assert.equal(load(memory, data).state.story.milestones[0], true);
  assert.throws(() => storeSlot(memory, 0, state, data), /Invalid save slot/);
});

test('creature and role stacks resolve without using the other table', () => {
  assert.equal(Object.keys(data.CREATURES).length, 8);
  assert.equal(Object.values(data.CREATURES).filter(creature => creature.fly).length, 4);
  assert.equal(Object.keys(data.ROLES).length, 3);
  for (const type of Object.keys(data.CREATURES)) {
    const title = stackTitle({ id: 'c-' + type, kind: 'creature', type, age: 3, count: 4, rank: 2 }, data);
    assert.match(title, new RegExp(data.CREATURES[type].n.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')));
    assert.match(title, /×4 rank 2/);
    if (data.CREATURES[type].fly) assert.match(title, /flyer/);
  }
  for (const role of Object.keys(data.ROLES)) {
    for (let age = 0; age < 8; age++) {
      const title = stackTitle({ id: role + age, kind: 'role', type: role, age, count: 5, rank: 0 }, data);
      assert.equal(title, `${data.ROLES[role].names[age]} ×5 rank 0`);
    }
  }
  assert.throws(() => stackTitle({ kind: 'creature', type: 'melee', count: 1, rank: 0, age: 0 }, data), /Invalid creature/);
});

test('tutorial review returns the cues and battle steps advance in order', () => {
  let state = act(fresh(), 'skip', 'TUTORIAL_SKIP', {});
  assert.equal(state.tutorial.skipped, true);
  state = act(state, 'review', 'TUTORIAL_REVIEW', {}, state.clock);
  assert.equal(state.tutorial.skipped, false);
  assert.equal(state.tutorial.step, 0);
  const clock = state.clock;
  state = act(state, 'motion', 'SETTINGS', { ...state.settings, reducedMotion: true }, clock);
  assert.equal(state.settings.reducedMotion, true);
  assert.equal(state.clock, clock);
  state.tutorial.step = 6;
  state = act(state, 'skirmish', 'START_SKIRMISH', {}, state.clock);
  assert.equal(state.tutorial.step, 7);
  state.battle = null;
  state = act(state, 'siege', 'START_SIEGE', {}, state.clock);
  assert.equal(state.tutorial.step, 8);
});
