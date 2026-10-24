// Legal earned-scope proof. Every change goes through command() and the documented clock.
// Income jumps use the age production cap inside settle(). Nothing is granted, and no
// tower or enemy stat is rewritten to force a result.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import data from '../src/data/reference-data.json' with { type: 'json' };
import contract from '../src/data/implementation-contract.json' with { type: 'json' };
import adventureWorlds from '../src/data/adventure-worlds.json' with { type: 'json' };
import { command, cost, futureConclusion, newCampaign, questReady, stackTitle } from '../src/core/campaign.js';
import { activeStackId } from '../src/core/battle.js';
import { adventureGeometryForWorld, adventureMap, isOpen, routeCost } from '../src/core/navigation.js';
import { QUALITY, RIVALS, agePrice, forgeOffer, gearBonus, marketQuote, recruitCost } from '../src/core/rules.js';
import { dwellingCost } from '../src/core/mechanics.js';
import { completeSkirmishDeployment } from './battle-deployment-helpers-20261022.mjs';
import { SAVE_KEY, decode, encode, load, restoreBackup, save, storeSlot, loadSlot } from '../src/core/save.js';

const CAP_MS = [8, 7, 6, 5, 4, 3.5, 3, 3].map(hours => hours * 3600000);
function memory() {
  const box = new Map();
  return {
    getItem: key => (box.has(key) ? box.get(key) : null),
    setItem: (key, value) => box.set(key, String(value)),
    removeItem: key => box.delete(key),
  };
}

test('every class can be chosen before the hero is committed', () => {
  assert.equal(Object.keys(data.CLASSES).length, 8);
  for (const id of Object.keys(data.CLASSES)) {
    let state = newCampaign(contract, data, 1_700_000_000_000, 99);
    state = command(state, { id: `class-${id}`, type: 'SET_CLASS', payload: { class: id } }, state.clock, data);
    assert.equal(state.hero.class, id);
    const other = id === 'knight' ? 'ranger' : 'knight';
    state = command(state, { id: `switch-${id}`, type: 'SET_CLASS', payload: { class: other } }, state.clock, data);
    assert.equal(state.hero.class, other);
    assert.throws(
      () => command(state, { id: `bad-${id}`, type: 'SET_CLASS', payload: { class: 'not-a-class' } }, state.clock, data),
      /Invalid class/,
    );
  }
});

test('earned scope reaches the legal campaign gates', () => {
  let now = 1_700_000_000_000;
  let state = newCampaign(contract, data, now, 123456789);
  const world = adventureWorlds.find(item => item.id === state.adventureWorldId);
  const geometry = adventureGeometryForWorld(contract.geometry.adventure, world, state.seed);
  const map = adventureMap(geometry);
  let n = 0;
  const evidence = {
    method: 'command-and-documented-income-cap',
    grants: 0,
    statMutations: 0,
    stops: [],
  };
  const go = (type, payload = {}, delay = 0) => {
    if (delay) now += delay;
    if (now < state.clock) throw new Error(`Clock moved backwards for ${type}`);
    state = command(state, { id: `earned-${n++}`, type, payload }, now, data);
  };
  const afford = payment => Object.entries(payment).every(([key, amount]) => state.resources[key] >= amount);
  const tick = (times = 1) => {
    for (let i = 0; i < times; i++) go('SETTINGS', { ...state.settings }, CAP_MS[state.age]);
  };
  const pump = () => {
    let guard = 0;
    while (state.buildJobs.length && guard < 40) {
      const end = Math.max(...state.buildJobs.map(job => job.completesAt));
      const jump = Math.min(CAP_MS[state.age], Math.max(1, end - now));
      go('SETTINGS', { ...state.settings }, jump);
      guard += 1;
    }
    if (state.buildJobs.length) throw new Error(`Construction still open: ${state.buildJobs.map(job => job.type).join(',')}`);
  };
  const build = (building, plotId) => {
    const level = plotId === 'walls' ? state.walls.level : state.plots.find(plot => plot.id === plotId).level;
    const payment = cost(data, building, level);
    let spins = 0;
    while (!afford(payment) && spins < 40) { tick(1); spins += 1; }
    if (!afford(payment)) throw new Error(`Cannot afford ${building} level ${level}: have ${JSON.stringify(state.resources)} need ${JSON.stringify(payment)}`);
    go('BUILD', { plotId, building });
  };
  const pad = () => {
    const plot = state.plots.find(item => item.type == null && !state.buildJobs.some(job => job.plotId === item.id));
    if (!plot) throw new Error('No empty pad');
    return plot.id;
  };
  const raise = (plotId, building, target) => {
    let guard = 0;
    while (guard < 40) {
      pump();
      const level = plotId === 'walls' ? state.walls.level : state.plots.find(plot => plot.id === plotId).level;
      if (level >= target) return;
      build(building, plotId);
      guard += 1;
    }
    throw new Error(`${building} stopped below ${target}`);
  };
  const playDefense = (limitSteps, speed = 2) => {
    let steps = 0;
    while (state.defense?.status === 'ACTIVE' && steps < limitSteps) {
      go('DEFENSE', { dt: 0.25, speed });
      steps += 1;
    }
    return steps;
  };
  const settleBattle = () => {
    if (state.battle?.status === 'ACTIVE') go('BATTLE', { action: 'auto' });
    assert.equal(state.battle.status, 'RESOLVED');
    const winner = state.battle.outcome?.winner;
    go('SETTLE_BATTLE', {});
    return winner;
  };

  assert.equal(Object.keys(data.ROLES).length, 3);
  assert.equal(Object.keys(data.CREATURES).length, 8);
  assert.equal(Object.keys(data.TOWERS).length, 4);
  assert.equal(Object.keys(data.ARTIFACTS).length, 10);
  assert.equal(Object.keys(data.SKILLS).length, 9);
  assert.equal(Object.keys(data.SPELLS).length, 8);
  assert.equal(data.STORY.length, 7);
  assert.deepEqual(QUALITY, [1, 1.8, 2.8, 4]);
  assert.equal(state.plots.filter(plot => plot.id !== 'townhall').length, 17);
  assert.equal(state.plots.find(plot => plot.id === 'townhall').type, 'townhall');

  go('SET_CLASS', { class: 'knight' });
  go('CHOOSE_RIVAL', { name: RIVALS[0] });
  assert.throws(() => go('CHOOSE_RIVAL', { name: RIVALS[1] }), /already chosen/);

  for (const building of ['lumber', 'farm', 'quarry', 'barracks']) build(building, pad());
  pump();
  assert.equal(state.tutorial.step, 4);
  go('RECRUIT', { role: 'melee' });
  assert.equal(state.tutorial.step, 5);
  const later = ['workshop', 'mine', 'mine', 'mine', 'farm', 'farm', 'lumber', 'lumber', 'quarry', 'quarry', 'quarry'];
  assert.equal(later.length, 11);
  for (const building of later) build(building, pad());
  build('walls', 'walls');
  pump();
  tick(1);
  build('armory', pad());
  build('hall', pad());
  pump();
  assert.equal(state.walls.level, 1);
  go('RECRUIT', { role: 'ranged' });

  go('ENTER_ADVENTURE', {});
  assert.equal(state.tutorial.step, 6);
  const beforeSkirmish = { gold: state.resources.gold, army: JSON.stringify(state.army), xp: state.hero.xp };
  state = completeSkirmishDeployment(state, data, 'earned-skirmish');
  assert.equal(state.battle.practice, 'skirmish');
  assert.equal(settleBattle(), 'p');
  assert.equal(state.resources.gold, beforeSkirmish.gold);
  assert.equal(JSON.stringify(state.army), beforeSkirmish.army);
  assert.equal(state.hero.xp, beforeSkirmish.xp);
  assert.equal(state.tutorial.step, 7);

  const beforeChallenge = { gold: state.resources.gold, army: JSON.stringify(state.army), xp: state.hero.xp };
  go('START_CHALLENGE', { schema: 1, scenarioId: 'duel-v1', seed: 7, label: 'earned-scope' });
  assert.equal(state.battle.practice, 'challenge');
  settleBattle();
  assert.equal(state.resources.gold, beforeChallenge.gold);
  assert.equal(JSON.stringify(state.army), beforeChallenge.army);
  assert.equal(state.hero.xp, beforeChallenge.xp);

  assert.ok(state.towers.some(tower => tower.fam === 'arrow'));
  const workshop = state.plots.find(plot => plot.type === 'workshop');
  raise(workshop.id, 'workshop', 2);
  raise(state.plots.find(plot => plot.type === 'armory').id, 'armory', 7);
  go('FORGE', { slot: 'weapon', quality: 3 });
  go('EQUIP', { itemId: state.inventory.at(-1).id });
  for (let extra = 0; extra < 12; extra++) {
    if (!afford(recruitCost(data, 'melee', state.age))) tick(1);
    go('RECRUIT', { role: 'melee' });
  }
  go('BUY_TOWER', { family: 'splash' });
  go('BUY_TOWER', { family: 'support' });
  go('START_SIEGE', {});
  assert.equal(state.defense.practice, 'siege');
  assert.equal(state.defense.waves, 5);
  const roles = new Set(state.defense.queue.map(enemy => enemy.role));
  for (const role of ['brute', 'runner', 'archer', 'sapper', 'shaman']) assert.ok(roles.has(role), role);
  go('DEPLOY_DEFENSE', {});
  go('DEPLOY_ARMY', { stackId: 'army-1' });
  playDefense(4000);
  assert.equal(state.defense.status, 'RESOLVED');
  assert.equal(state.defense.winner, 'p');
  assert.equal(state.defense.clearedWaves, state.defense.waves);
  assert.ok(state.defense.core > 0);
  const siegeGoldBefore = state.resources.gold;
  const pending = encode(state, data);
  const resumed = decode(pending, data);
  assert.equal(resumed.defense.pendingSettlement, true);
  const settled = command(resumed, { id: 'earned-siege-settle', type: 'SETTLE_DEFENSE', payload: {} }, resumed.clock, data);
  const paid = settled.resources.gold - siegeGoldBefore;
  assert.ok(paid > 0);
  assert.equal(settled.defense, null);
  assert.throws(
    () => command(settled, { id: 'earned-siege-settle-again', type: 'SETTLE_DEFENSE', payload: {} }, settled.clock, data),
    /No pending defense/,
  );
  const reloaded = decode(encode(settled, data), data);
  assert.equal(reloaded.resources.gold, settled.resources.gold);
  state = reloaded;
  now = state.clock;
  assert.equal(state.tutorial.step, 8);
  evidence.siege = { winner: 'p', clearedWaves: 5, waves: 5, coreSurvived: true, goldPaidOnce: paid };

  for (let warm = 0; warm < 60; warm++) {
    go('START_DUEL', {});
    settleBattle();
    const offer = state.hero.offers.find(item => !item.chosen && !item.declined);
    if (offer) go('CHOOSE_SKILL', { skill: offer.choices.includes('wisdom') ? 'wisdom' : offer.choices[0] });
    while (state.hero.points > 0) go('SPEND_POINT', { stat: 'atk' });
  }
  evidence.endlessPrep = { level: state.hero.level, growth: { ...state.hero.growth }, bonus: { ...state.hero.bonus }, ranks: state.army.map(stack => stack.rank) };
  go('START_ENDLESS', {});
  const endlessStart = state.defense.waves;
  assert.equal(endlessStart, 3);
  go('DEPLOY_DEFENSE', {});
  const army = state.army.find(stack => stack.count > 0);
  go('DEPLOY_ARMY', { stackId: army.id });
  let endlessSteps = 0;
  while (state.defense?.status === 'ACTIVE' && endlessSteps < 20000 && !(state.defense.clearedWaves >= 10 && state.defense.extensions >= 1 && state.defense.core <= 0)) {
    go('DEFENSE', { dt: 0.25, speed: 2 });
    endlessSteps += 1;
    if (state.defense.clearedWaves >= 10 && state.defense.extensions >= 1 && state.defense.status === 'ACTIVE' && endlessSteps > 16000) break;
  }
  evidence.endless = {
    steps: endlessSteps,
    status: state.defense?.status ?? 'settled',
    waves: state.defense?.waves,
    clearedWaves: state.defense?.clearedWaves,
    extensions: state.defense?.extensions,
    core: state.defense?.core,
    initialWaves: endlessStart,
  };
  assert.ok(state.defense.extensions >= 1);
  assert.ok(state.defense.waves > endlessStart);
  assert.ok(state.defense.clearedWaves >= endlessStart);
  if (state.defense.status === 'RESOLVED') {
    const cleared = state.defense.clearedWaves;
    const extended = state.defense.waves;
    go('SETTLE_DEFENSE', {});
    state = decode(encode(state, data), data);
    now = state.clock;
    if (questReady(state, data, 'q6')) {
      go('CLAIM_QUEST', { id: 'q6' });
      assert.equal(state.quests.q6.claimed, true);
      assert.throws(() => go('CLAIM_QUEST', { id: 'q6' }), /already claimed/);
    } else evidence.stops.push(`Endless extended from 3 to ${extended} waves and cleared ${cleared} before the core fell. Quest q6 needs 10 cleared waves. Tower rank has no command, and this seed did not clear the tenth wave.`);
  } else evidence.stops.push(`Endless still ${state.defense.status} after ${endlessSteps} steps at cleared ${state.defense.clearedWaves} / waves ${state.defense.waves}. Quest q6 stays unclaimed because an endless session records its best only when the core falls.`);

  const sites = {
    farm: state.plots.filter(plot => plot.type === 'farm').map(plot => plot.id),
    lumber: state.plots.filter(plot => plot.type === 'lumber').map(plot => plot.id),
    quarry: state.plots.filter(plot => plot.type === 'quarry').map(plot => plot.id),
    mine: state.plots.filter(plot => plot.type === 'mine').map(plot => plot.id),
  };
  for (const id of sites.farm) raise(id, 'farm', 4);
  for (const id of sites.lumber) raise(id, 'lumber', 5);
  for (const id of sites.quarry) raise(id, 'quarry', 4);
  for (const id of sites.mine) raise(id, 'mine', 5);
  raise(state.plots.find(plot => plot.type === 'hall').id, 'hall', 1);
  raise(state.plots.find(plot => plot.type === 'armory').id, 'armory', 7);
  raise('townhall', 'townhall', 8);
  tick(2);

  const armory = state.plots.find(plot => plot.type === 'armory').level;
  evidence.forge = [];
  for (const quality of [0, 1, 2, 3]) {
    const offer = forgeOffer(state.age, armory, quality);
    const before = { ...state.resources };
    go('FORGE', { slot: 'weapon', quality });
    const item = state.inventory.at(-1);
    assert.equal(item.quality, quality);
    assert.equal(item.age, state.age);
    assert.equal(before.wood - state.resources.wood, offer.cost.wood);
    assert.equal(before.stone - state.resources.stone, offer.cost.stone);
    assert.equal(before.gold - state.resources.gold, offer.cost.gold);
    evidence.forge.push({ quality, cost: offer.cost, bonus: gearBonus(item) });
  }
  const weaponBonuses = evidence.forge.map(row => row.bonus.atk);
  assert.ok(weaponBonuses.every((value, index) => index === 0 || value > weaponBonuses[index - 1]));
  for (const slot of ['helm', 'offhand', 'armor', 'boots', 'accessory']) go('FORGE', { slot, quality: 3 });
  for (const slot of ['helm', 'weapon', 'offhand', 'armor', 'boots', 'accessory']) {
    const item = [...state.inventory].reverse().find(entry => entry.slot === slot && entry.kind === 'gear' && (slot !== 'weapon' || entry.quality === 3));
    go('EQUIP', { itemId: item.id });
  }
  assert.ok(['helm', 'weapon', 'offhand', 'armor', 'boots', 'accessory'].every(slot => state.hero.equip[slot]?.kind === 'gear'));
  if (questReady(state, data, 'q5')) go('CLAIM_QUEST', { id: 'q5' });

  go('STORY_CHOICE', { index: 0 });
  go('CLAIM_MILESTONE', { age: 0 });
  while (state.age < 7) {
    const price = agePrice(state.age);
    let spins = 0;
    while (!afford(price) && spins < 12) { tick(1); spins += 1; }
    if (!afford(price)) throw new Error(`Age ${state.age} price unpaid: ${JSON.stringify(price)} have ${JSON.stringify(state.resources)}`);
    const nextAge = state.age + 1;
    go('AGE_UP', {});
    assert.equal(state.age, nextAge);
    if (state.age === 1) {
      const buy = marketQuote('buy', 'wood');
      const sell = marketQuote('sell', 'food');
      go('MARKET', { side: 'buy', resource: 'wood' });
      go('MARKET', { side: 'sell', resource: 'food' });
      evidence.market = { buy, sell, age: state.age };
      go('RETROFIT', { towerId: state.towers.find(tower => tower.fam === 'arrow').id });
      const barracks = state.plots.find(plot => plot.type === 'barracks');
      raise(barracks.id, 'barracks', 2);
      go('RECRUIT', { role: 'heavy' });
      const heavy = state.army.find(stack => stack.kind === 'role' && stack.type === 'heavy' && stack.age === 1);
      evidence.bronzeHeavy = { name: data.ROLES.heavy.names[1], title: stackTitle(heavy, data), image: 'plate remains infantry; this row is the data name only' };
    }
    if (state.story.chapter < data.STORY.length) go('STORY_CHOICE', { index: 0 });
    go('CLAIM_MILESTONE', { age: state.age });
  }
  assert.equal(state.story.chapter, 7);
  go('ACK_FUTURE', {});
  assert.equal(state.story.futureSeen, true);
  assert.match(futureConclusion(state, data), /grants nothing/);
  assert.throws(() => go('ACK_FUTURE', {}), /already kept/);
  if (!state.story.milestones[7]) go('CLAIM_MILESTONE', { age: 7 });
  assert.equal(Object.keys(state.story.milestones).length, 8);
  if (questReady(state, data, 'q2')) go('CLAIM_QUEST', { id: 'q2' });

  const approach = geometry.sites.find(site => site.id === 'dwelling').approach;
  const neighbors = (x, y) => {
    const found = [];
    for (let dx = -1; dx <= 1; dx++) for (let dy = -1; dy <= 1; dy++) {
      if (!dx && !dy) continue;
      if (!isOpen(map, x + dx, y + dy)) continue;
      if (dx && dy && (!isOpen(map, x + dx, y) || !isOpen(map, x, y + dy))) continue;
      if (dx && dy && (map.bridge.has(`${x},${y}`) || map.bridge.has(`${x + dx},${y + dy}`))) continue;
      found.push([x + dx, y + dy]);
    }
    return found;
  };
  const shortest = (from, to) => {
    const goal = `${to[0]},${to[1]}`;
    const previous = new Map([[`${from[0]},${from[1]}`, null]]);
    const queue = [from];
    while (queue.length) {
      const [x, y] = queue.shift();
      if (`${x},${y}` === goal) break;
      for (const next of neighbors(x, y)) {
        const key = `${next[0]},${next[1]}`;
        if (previous.has(key)) continue;
        previous.set(key, [x, y]);
        queue.push(next);
      }
    }
    if (!previous.has(goal)) return null;
    const cells = [];
    let cursor = to;
    while (`${cursor[0]},${cursor[1]}` !== `${from[0]},${from[1]}`) {
      cells.push(cursor);
      cursor = previous.get(`${cursor[0]},${cursor[1]}`);
    }
    return cells.reverse();
  };
  let walks = 0;
  while ((state.adventure.x !== approach[0] || state.adventure.y !== approach[1]) && walks < 40) {
    walks += 1;
    if (state.adventure.atTown) go('ENTER_ADVENTURE', {});
    if (state.adventure.pendingEncounter) {
      go('BEGIN_ENCOUNTER', {});
      settleBattle();
      continue;
    }
    if (state.adventure.moves < 1) { go('END_DAY', {}); continue; }
    const path = shortest([state.adventure.x, state.adventure.y], approach);
    if (!path?.length) throw new Error('No dwelling path');
    let cut = path;
    const guardAt = path.findIndex(cell => map.guards.has(`${cell[0]},${cell[1]}`) && !state.adventure.resolvedGuards.includes(`${cell[0]},${cell[1]}`));
    if (guardAt >= 0) cut = path.slice(0, guardAt + 1);
    while (cut.length > 1 && routeCost(map, [state.adventure.x, state.adventure.y], cut).cost > state.adventure.moves) cut = cut.slice(0, -1);
    if (routeCost(map, [state.adventure.x, state.adventure.y], cut).cost > state.adventure.moves) { go('END_DAY', {}); continue; }
    go('MOVE', { path: cut });
  }
  assert.deepEqual([state.adventure.x, state.adventure.y], approach);
  const barracks = state.plots.find(plot => plot.type === 'barracks');
  raise(barracks.id, 'barracks', Math.max(barracks.level, state.army.length + Object.keys(data.CREATURES).length - 2));
  const dwellingPayments = [];
  for (const type of Object.keys(data.CREATURES)) {
    go('OFFER_DWELLING', { type });
    const payment = dwellingCost(data, state.dwelling.type, state.dwelling.multiplier);
    let spins = 0;
    while (!afford(payment) && spins < 40) { tick(1); spins += 1; }
    const before = { ...state.resources };
    go('CLAIM_DWELLING', {});
    dwellingPayments.push({ type, count: state.army.find(stack => stack.type === type).count, spent: Object.fromEntries(Object.keys(payment).map(key => [key, before[key] - state.resources[key]])) });
    assert.throws(() => go('OFFER_DWELLING', { type }), /already offered/);
  }
  assert.equal(new Set(state.army.filter(stack => stack.kind === 'creature').map(stack => stack.type)).size, 8);
  if (questReady(state, data, 'q3')) go('CLAIM_QUEST', { id: 'q3' });
  evidence.dwelling = { poolAtAge7: Object.keys(data.CREATURES).length, payments: dwellingPayments, ownedCreatures: state.army.filter(stack => stack.kind === 'creature').map(stack => stack.type) };

  const artifacts = new Set();
  let duels = 0;
  let duelWins = 0;
  while (artifacts.size < 10 && duels < 800) {
    duels += 1;
    const mana = state.hero.mana;
    go('START_DUEL', {});
    assert.equal(state.battle.practice, 'campaign');
    const winner = settleBattle();
    if (winner === 'p') {
      duelWins += 1;
      for (const item of state.inventory) if (item.kind === 'artifact') artifacts.add(item.artifactId);
      for (const item of Object.values(state.hero.equip)) if (item?.kind === 'artifact') artifacts.add(item.artifactId);
    }
    if (state.hero.mana < 5) go('END_DAY', {});
    if (mana < 0) break;
  }
  evidence.artifacts = { duels, duelWins, found: [...artifacts], missing: Object.keys(data.ARTIFACTS).filter(id => !artifacts.has(id)) };
  if (artifacts.size < 10) evidence.stops.push(`Legal duel loot found ${artifacts.size}/10 artifacts after ${duels} duels. Missing ${evidence.artifacts.missing.join(', ') || 'none'}.`);
  else assert.equal(artifacts.size, 10);

  raise(state.plots.find(plot => plot.type === 'hall').id, 'hall', 7);
  let skillPicks = Object.values(state.hero.skills).reduce((sum, level) => sum + level, 0);
  let pointSpent = state.hero.bonus.atk > 0;
  for (let guard = 0; guard < 800; guard++) {
    const offer = state.hero.offers.find(item => !item.chosen && !item.declined);
    if (offer) {
      const skill = offer.choices.find(id => id === 'wisdom' && state.hero.skills[id] < 3) || offer.choices.find(id => state.hero.skills[id] < 3);
      if (!skill) { go('DECLINE_SKILL', {}); continue; }
      go('CHOOSE_SKILL', { skill });
      skillPicks += 1;
      continue;
    }
    if (!pointSpent && state.hero.points > 0) { go('SPEND_POINT', { stat: 'atk' }); pointSpent = true; continue; }
    if (state.hero.skills.wisdom >= 3 && state.army.some(stack => stack.rank >= 1) && pointSpent) break;
    const winner = (() => { go('START_DUEL', {}); return settleBattle(); })();
    if (winner !== 'p' && state.army.every(stack => stack.rank < 1)) {
      evidence.stops.push('Rank quest stopped because later duels were not won and no stack reached rank 1.');
      break;
    }
  }
  evidence.skills = { picks: skillPicks, ranks: { ...state.hero.skills }, pointSpent, armyRanks: state.army.map(stack => ({ id: stack.id, rank: stack.rank })) };
  const cast = [];
  const spellbook = Object.entries(data.SPELLS).map(([id, spell]) => ({ ...spell, id }));
  const spellOrder = ['bless', 'haste', 'cure', 'slow', 'arrow', 'bolt', 'fireball', 'resurrect'];
  for (let attempt = 0; attempt < 12 && cast.length < spellbook.length; attempt++) {
    for (let refill = 0; refill < 3; refill++) go('END_DAY', {});
    go('START_DUEL', {});
    let spellGuard = 0;
    while (state.battle?.status === 'ACTIVE' && spellGuard < 80) {
      spellGuard += 1;
      const actorId = activeStackId(state.battle);
      const actor = state.battle.stacks.find(stack => stack.id === actorId);
      if (!actor || actor.side !== 'p') { go('BATTLE', { action: 'opponent' }); continue; }
      const spell = spellOrder.map(id => spellbook.find(item => item.id === id)).find(item => item && !cast.includes(item.id) && item.lv <= 1 + state.hero.skills.wisdom && item.mana <= state.battle.mana);
      if (!spell) break;
      const allies = state.battle.stacks.filter(stack => stack.side === 'p' && !stack.dead);
      const enemies = state.battle.stacks.filter(stack => stack.side === 'e' && !stack.dead);
      const wounded = allies.find(stack => stack.count < stack.maxCount || stack.top < stack.uhp);
      if (spell.id === 'resurrect' && !wounded) {
        go('BATTLE', { action: 'defend', stackId: actor.id });
        continue;
      }
      const target = spell.id === 'resurrect' ? wounded : ['bless', 'haste', 'cure'].includes(spell.id) ? allies[0] : enemies[0];
      if (!target) break;
      const beforePool = (target.count - 1) * target.uhp + target.top;
      const manaBefore = state.battle.mana;
      try {
        go('BATTLE', { action: 'spell', spell: spell.id, targetId: target.id });
        cast.push(spell.id);
        if (spell.id === 'resurrect') {
          const after = state.battle.stacks.find(stack => stack.id === target.id);
          const afterPool = (after.count - 1) * after.uhp + after.top;
          evidence.resurrect = {
            before: { count: target.count, top: target.top, pool: beforePool, maxCount: target.maxCount, unitHp: target.uhp },
            after: { count: after.count, top: after.top, pool: afterPool },
            recovered: afterPool - beforePool,
            manaBefore,
            manaAfter: state.battle.mana,
          };
          assert.ok(afterPool > beforePool, 'Resurrection must recover HP on a wounded living stack');
        }
        if (state.battle?.status === 'ACTIVE') {
          const follow = activeStackId(state.battle);
          const follower = state.battle.stacks.find(stack => stack.id === follow);
          if (follower?.side === 'p') go('BATTLE', { action: 'defend', stackId: follow });
        }
      } catch (error) {
        if (error.message !== 'Spell already cast') evidence.stops.push(`Spell ${spell.id} refused: ${error.message}`);
        break;
      }
    }
    if (state.battle?.status === 'ACTIVE') go('BATTLE', { action: 'auto' });
    if (state.battle?.pendingSettlement) go('SETTLE_BATTLE', {});
  }
  evidence.spells = { cast, wisdom: state.hero.skills.wisdom, uncast: spellOrder.filter(id => !cast.includes(id)) };
  if (evidence.spells.uncast.length) evidence.stops.push(`Spells not cast under the wisdom/mana gate: ${evidence.spells.uncast.join(', ')}.`);
  if (questReady(state, data, 'q4')) go('CLAIM_QUEST', { id: 'q4' });
  if (questReady(state, data, 'q1')) go('CLAIM_QUEST', { id: 'q1' });
  assert.ok(state.army.some(stack => stack.rank >= 1));
  assert.ok(pointSpent);
  assert.ok(skillPicks > 0);

  go('SETTINGS', { music: 0, sfx: 0.2, reducedMotion: true });
  assert.equal(state.settings.music, 0);
  assert.equal(state.settings.sfx, 0.2);
  assert.equal(state.settings.reducedMotion, true);
  go('SETTINGS', { music: 0.6, sfx: 0.8, reducedMotion: false });
  assert.throws(() => go('SET_CLASS', { class: 'ranger' }), /already committed/);

  const storage = memory();
  save(storage, state, data);
  const loaded = load(storage, data);
  assert.equal(loaded.status, 'VALID');
  assert.equal(loaded.state.age, 7);
  storeSlot(storage, 1, state, data);
  assert.equal(loadSlot(storage, 1, data).age, 7);
  save(storage, state, data);
  storage.setItem(SAVE_KEY, '{"schema":1,"payload":"{}","checksum":"dead"}');
  const restored = restoreBackup(storage, data);
  assert.equal(restored.age, 7);

  evidence.age = state.age;
  evidence.chapter = state.story.chapter;
  evidence.futureSeen = state.story.futureSeen;
  evidence.milestones = Object.keys(state.story.milestones).length;
  evidence.rival = state.story.rival;
  evidence.equipped = Object.fromEntries(Object.entries(state.hero.equip).map(([slot, item]) => [slot, item ? { age: item.age, quality: item.quality, kind: item.kind } : null]));
  evidence.quests = Object.fromEntries(Object.entries(state.quests).map(([id, quest]) => [id, quest.claimed]));
  evidence.day = state.day;
  fs.mkdirSync('qa/code-image-repair-20261011', { recursive: true });
  const earnedScopeOut = process.env.EARNED_SCOPE_OUT || 'qa/remaining-repair-20261011/earned-scope.json';
  const earnedDir = earnedScopeOut.slice(0, Math.max(earnedScopeOut.lastIndexOf('/'), earnedScopeOut.lastIndexOf('\\')));
  fs.mkdirSync(earnedDir, { recursive: true });
  fs.writeFileSync(earnedScopeOut, JSON.stringify(evidence, null, 2));
  assert.equal(state.age, 7);
  assert.equal(state.story.futureSeen, true);
  assert.equal(evidence.siege.winner, 'p');
});
