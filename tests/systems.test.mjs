import test from 'node:test';
import assert from 'node:assert/strict';
import data from '../src/data/reference-data.json' with { type: 'json' };
import contract from '../src/data/implementation-contract.json' with { type: 'json' };
import { newCampaign, command, advance } from '../src/core/campaign.js';
import { adventureMap, stepCost } from '../src/core/navigation.js';
import { agePrice, forgeOffer, gearBonus, gateHp, heroStats, manaMax, spellEffect } from '../src/core/rules.js';
import { hoofContact, pose } from '../src/client/rig.js';

const fresh = () => newCampaign(contract, data, 1000);
const act = (s, id, type, payload, now = 1000) => command(s, { id, type, payload }, now, data);
const finishBuild = (s) => advance(s, s.buildJobs[0].completesAt, data);

test('age gate, market and retrofit refuse before payment', () => {
  const s = fresh();
  assert.throws(() => act(s, 'age', 'AGE_UP'), /Town Hall/);
  assert.equal(s.resources.gold, 150);
  assert.throws(() => act(s, 'm', 'MARKET', { side: 'buy', resource: 'wood' }), /Bronze/);
  assert.throws(() => act(s, 'r', 'RETROFIT', { towerId: 'tower-1' }), /no-op/);
  assert.equal(s.resources.wood, 250);
  assert.equal(gateHp(s), 400);
});

test('completed barracks reinforces the current-age stack once', () => {
  let s = act(fresh(), 'b', 'BUILD', { plotId: 'P01', building: 'barracks' });
  s = finishBuild(s);
  const next = act(s, 'recr', 'RECRUIT', { role: 'melee' }, s.clock);
  assert.equal(next.army[0].count, 17);
  assert.equal(next.resources.food, 25);
  assert.equal(next.resources.gold, 100);
  assert.deepEqual(act(next, 'recr', 'RECRUIT', { role: 'melee' }, next.clock), next);
  assert.throws(() => act(next, 'recr', 'RECRUIT', { role: 'heavy' }, next.clock), /conflict/);
  assert.equal(next.army.length, 2);
});

test('armory forges one item, equip changes attack, unequip returns it', () => {
  let s = act(fresh(), 'a', 'BUILD', { plotId: 'P02', building: 'armory' });
  s = finishBuild(s);
  s.resources.wood += 100; s.resources.stone += 100; s.resources.gold += 100;
  s = act(s, 'f', 'FORGE', { slot: 'weapon' }, s.clock);
  assert.equal(s.inventory.length, 1);
  assert.deepEqual(gearBonus(s.inventory[0]), { atk: 1 });
  s = act(s, 'e', 'EQUIP', { itemId: s.inventory[0].id }, s.clock);
  assert.equal(heroStats(s, data).atk, 4);
  assert.equal(s.inventory.length, 0);
  s = act(s, 'u', 'UNEQUIP', { slot: 'weapon' }, s.clock);
  assert.equal(s.inventory.length, 1);
  assert.equal(s.hero.equip.weapon, null);
  assert.throws(() => forgeOffer(0, 0), /Armory/);
});

test('bronze market buy and sell are exact and idempotent', () => {
  const priced = agePrice(0);
  assert.deepEqual(priced, { food: 645, wood: 602, stone: 473, gold: 387 });
  let s = fresh();
  s.plots.find(p => p.id === 'townhall').level = 2;
  s.resources = { food: 1000, wood: 1000, stone: 1000, gold: 1000 };
  s = act(s, 'age', 'AGE_UP');
  assert.equal(s.age, 1);
  assert.equal(s.resources.gold, 1000 - 387);
  s = act(s, 'buy', 'MARKET', { side: 'buy', resource: 'wood' }, s.clock);
  assert.equal(s.resources.wood, 1000 - 602 + 100);
  assert.equal(s.resources.gold, 1000 - 387 - 120);
  const again = act(s, 'buy', 'MARKET', { side: 'buy', resource: 'wood' }, s.clock);
  assert.deepEqual(again.resources, s.resources);
  s = act(s, 'sell', 'MARKET', { side: 'sell', resource: 'stone' }, s.clock);
  assert.equal(s.resources.stone, 1000 - 473 - 100);
  assert.equal(s.resources.gold, 1000 - 387 - 120 + 60);
});

test('class, rival and settings reject invalid input without a partial write', () => {
  let s = act(fresh(), 'c', 'SET_CLASS', { class: 'mage' });
  assert.equal(s.hero.class, 'mage');
  assert.equal(manaMax(s, data), 40);
  assert.equal(s.hero.mana, 40);
  assert.throws(() => act(s, 'bad', 'SET_CLASS', { class: 'dragon' }, s.clock), /Invalid class/);
  s = act(s, 'v', 'CHOOSE_RIVAL', { name: 'Varek Iron-Eye' }, s.clock);
  assert.throws(() => act(s, 'v2', 'CHOOSE_RIVAL', { name: 'Varek Iron-Eye' }, s.clock), /already chosen/);
  assert.throws(() => act(s, 'set', 'SETTINGS', { music: 2, sfx: 0 }, s.clock), /audio/);
  assert.equal(s.settings.music, 0.6);
});

test('journey blocks water, spends a road step once, and rest refills mana only', () => {
  const map = adventureMap(contract.geometry.adventure);
  assert.throws(() => stepCost(map, [3, 5], [4, 5]), /Blocked/);
  assert.equal(stepCost(map, [8, 8], [8, 7]), 1);
  assert.equal(stepCost(map, [2, 2], [3, 3], () => 'forest'), 3);
  let s = act(fresh(), 'go', 'ENTER_ADVENTURE');
  const open = s;
  assert.throws(() => act(s, 'bad', 'MOVE', { path: [[4, 5]] }, s.clock), /Illegal step/);
  assert.equal(s.adventure.moves, open.adventure.moves);
  s.hero.mana = 1;
  s = act(s, 'step', 'MOVE', { path: [[8, 7]] }, s.clock);
  assert.equal(s.adventure.moves, 4);
  assert.deepEqual([s.adventure.x, s.adventure.y], [8, 7]);
  s = act(s, 'rest', 'REST', {}, s.clock);
  assert.equal(s.adventure.moves, 3);
  assert.equal(s.hero.mana, 10);
  assert.equal(s.army[0].count, 12);
  assert.equal(s.resources.food, 250);
});

test('tutorial advances only on the requested action', () => {
  let s = act(fresh(), 'f', 'BUILD', { plotId: 'P03', building: 'farm' });
  assert.equal(s.tutorial.step, 0);
  s = act(s, 'l', 'BUILD', { plotId: 'P04', building: 'lumber' }, s.clock);
  assert.equal(s.tutorial.step, 1);
  s = act(s, 'skip', 'TUTORIAL_SKIP', {}, s.clock);
  assert.equal(s.tutorial.skipped, true);
});

test('spell magnitudes and articulated clips stay inside their documented bounds', () => {
  assert.equal(spellEffect('arrow', 3), 40);
  assert.equal(spellEffect('bolt', 2), 60);
  assert.equal(spellEffect('fireball', 1), 30);
  assert.equal(spellEffect('resurrect', 2), 100);
  assert.equal(spellEffect('bless', 1), null);
  const idle = pose('idle', 0.25);
  const walk = pose('walk', 0.25);
  assert.equal(hoofContact(idle), 2);
  assert.ok(hoofContact(walk) >= 1);
  assert.notEqual(walk.hoofL[1], idle.hoofL[1]);
  assert.notEqual(pose('death', 0.2).spine, idle.spine);
  assert.notEqual(pose('attack', 0).hand[0], pose('attack', 0.5).hand[0]);
  const standing = pose('mountWalk', 0.3, { reduced: true });
  const gait = pose('mountWalk', 0.3);
  assert.equal(hoofContact(standing), 4);
  assert.ok(hoofContact(gait) >= 1 && hoofContact(gait) < 4);
});
