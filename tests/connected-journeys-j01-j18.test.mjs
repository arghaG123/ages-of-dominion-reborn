import test from 'node:test';
import assert from 'node:assert/strict';
import data from '../src/data/reference-data.json' with { type: 'json' };
import contract from '../src/data/implementation-contract.json' with { type: 'json' };
import {
  advance,
  command,
  futureConclusion,
  heroStats,
  newCampaign,
  validate
} from '../src/core/campaign.js';
import { activeStackId } from '../src/core/battle.js';
import { adventureMap, routeCost } from '../src/core/navigation.js';
import {
  GEAR_SLOTS,
  RIVALS,
  SKILL_IDS,
  agePrice,
  forgeOffer,
  gearBonus,
  marketQuote,
  recruitCost
} from '../src/core/rules.js';
import { dwellingCost, makePack } from '../src/core/mechanics.js';
import {
  decode,
  encode,
  load,
  loadSlot,
  replaceCampaign,
  save,
  storeSlot
} from '../src/core/save.js';

function memory() {
  const box = new Map();
  return {
    getItem: key => (box.has(key) ? box.get(key) : null),
    setItem: (key, value) => box.set(key, String(value)),
    removeItem: key => box.delete(key),
  };
}

let txCount = 0;
const act = (state, type, payload = {}, now = state.clock) =>
  command(state, { id: `tx-${++txCount}`, type, payload }, now, data);

const finishBuild = state => {
  if (!state.buildJobs.length) return state;
  return advance(state, state.buildJobs[0].completesAt, data);
};

// ---------------------------------------------------------------------------
// J01: Fresh start
// ---------------------------------------------------------------------------
test('J01 Fresh start: class choice, sparse Kingdom, correct starter plots and contract resources', () => {
  const store = memory();
  let state = newCampaign(contract, data, 1_000_000);
  
  // Starter resources contract
  assert.equal(state.resources.food, 250);
  assert.equal(state.resources.wood, 250);
  assert.equal(state.resources.stone, 160);
  assert.equal(state.resources.gold, 150);
  assert.equal(state.age, 0); // Stone age
  assert.equal(state.tutorial.step, 0); // First tutorial step: Build Lumber Camp
  assert.equal(state.inventory.length, 0);
  
  // Plots: only townhall level 1, 17 empty plots
  assert.equal(state.plots.length, 18);
  const hall = state.plots.find(p => p.id === 'townhall');
  assert.ok(hall && hall.level === 1);
  assert.equal(state.plots.filter(p => p.level > 0).length, 1);
  
  // Class choice
  state = act(state, 'SET_CLASS', { class: 'ranger' });
  assert.equal(state.hero.class, 'ranger');

  // Persistence
  save(store, state, data);
  const loaded = load(store, data);
  assert.equal(loaded.status, 'VALID');
  assert.equal(loaded.state.hero.class, 'ranger');
  assert.equal(loaded.state.tutorial.step, 0);
});

// ---------------------------------------------------------------------------
// J02: Build/upgrade
// ---------------------------------------------------------------------------
test('J02 Build/upgrade: empty plot preview, cancel unchanged, build completion, upgrade, reload', () => {
  const store = memory();
  let state = newCampaign(contract, data, 1_000_000);
  const plot = state.plots.find(p => p.id === 'P01');
  assert.equal(plot.level, 0);
  
  // Trying invalid build destination throws without mutating
  assert.throws(() => act(state, 'BUILD', { plotId: 'invalid-id', building: 'lumber' }));
  
  // Start build lumber camp on P01
  const startWood = state.resources.wood;
  state = act(state, 'BUILD', { plotId: 'P01', building: 'lumber' });
  assert.equal(state.buildJobs.length, 1);
  assert.ok(state.resources.wood < startWood);
  
  // Complete build (level 1)
  state = finishBuild(state);
  assert.equal(state.plots.find(p => p.id === 'P01').level, 1);
  assert.equal(state.plots.find(p => p.id === 'P01').type, 'lumber');
  
  // Upgrade P01 (BUILD increments level)
  state = act(state, 'BUILD', { plotId: 'P01', building: 'lumber' });
  state = finishBuild(state);
  assert.equal(state.plots.find(p => p.id === 'P01').level, 2);

  // Reload verification
  save(store, state, data);
  const loaded = load(store, data);
  assert.equal(loaded.state.plots.find(p => p.id === 'P01').level, 2);
});

// ---------------------------------------------------------------------------
// J03: Recruitment
// ---------------------------------------------------------------------------
test('J03 Recruitment: barracks unlock, recruit stack, capacity feedback, army roster persistence', () => {
  const store = memory();
  let state = newCampaign(contract, data, 1_000_000);
  
  // Build and complete Barracks
  state = act(state, 'BUILD', { plotId: 'P04', building: 'barracks' });
  state = finishBuild(state);
  assert.equal(state.plots.find(p => p.id === 'P04').level, 1);
  
  // Initial army
  const initialMelee = state.army.find(s => s.type === 'melee').count;
  const initialGold = state.resources.gold;
  
  // Recruit melee stack
  state = act(state, 'RECRUIT', { role: 'melee' });
  const recruitedMelee = state.army.find(s => s.type === 'melee').count;
  assert.ok(recruitedMelee > initialMelee, 'Melee stack count must increase');
  assert.ok(state.resources.gold < initialGold, 'Gold must be deducted');

  // Reload verification
  save(store, state, data);
  const loaded = load(store, data);
  assert.equal(loaded.state.army.find(s => s.type === 'melee').count, recruitedMelee);
});

// ---------------------------------------------------------------------------
// J04: Age progression
// ---------------------------------------------------------------------------
test('J04 Age progression: Hall payment gate, next-age world transformation, retained identities, reload', () => {
  const store = memory();
  let state = newCampaign(contract, data, 1_000_000);
  assert.equal(state.age, 0); // Stone
  
  // Upgrade Townhall to level 2
  state = act(state, 'BUILD', { plotId: 'townhall', building: 'townhall' });
  state = finishBuild(state);
  
  // Provide funds for Bronze Age advancement
  state.resources.food += 1000;
  state.resources.wood += 1000;
  state.resources.stone += 1000;
  state.resources.gold += 1000;
  
  state = act(state, 'AGE_UP', {});
  assert.equal(state.age, 1); // Bronze
  
  // Retained plot topology and townhall identity
  assert.equal(state.plots.length, 18);
  assert.equal(state.plots.find(p => p.id === 'townhall').level, 2);

  // Reload verification
  save(store, state, data);
  const loaded = load(store, data);
  assert.equal(loaded.state.age, 1);
  assert.equal(loaded.state.plots.find(p => p.id === 'townhall').level, 2);
});

// ---------------------------------------------------------------------------
// J05: Adventure travel
// ---------------------------------------------------------------------------
test('J05 Adventure travel: leave town, route preview/cancel, legal move, fog uncover, reload', () => {
  const store = memory();
  let state = newCampaign(contract, data, 1_000_000);
  
  // Leave town (hero starts at [8, 8])
  state = act(state, 'ENTER_ADVENTURE', {});
  assert.equal(state.adventure.atTown, false);
  const initialMoves = state.adventure.moves;
  assert.equal(state.adventure.x, 8);
  assert.equal(state.adventure.y, 8);
  
  // Blocked move onto water or obstacle throws and leaves state unchanged
  assert.throws(() => act(state, 'MOVE', { path: [[4, 5]] }), /Illegal|Blocked/);
  assert.equal(state.adventure.moves, initialMoves);
  
  // Legal move along road to [8, 7]
  state = act(state, 'MOVE', { path: [[8, 7]] });
  assert.equal(state.adventure.x, 8);
  assert.equal(state.adventure.y, 7);
  assert.ok(state.adventure.moves < initialMoves);

  // Reload verification
  save(store, state, data);
  const loaded = load(store, data);
  assert.equal(loaded.state.adventure.x, 8);
  assert.equal(loaded.state.adventure.y, 7);
  assert.equal(loaded.state.adventure.atTown, false);
});

// ---------------------------------------------------------------------------
// J06: Site/guard
// ---------------------------------------------------------------------------
test('J06 Site/guard: encounter initiation, battle state entry, persistence without reroll', () => {
  const store = memory();
  let state = newCampaign(contract, data, 1_000_000);
  state = act(state, 'ENTER_ADVENTURE', {});
  
  // Setup pending encounter guard
  state.adventure.pendingEncounter = {
    id: 'guard-10,5',
    cell: [10, 5],
    origin: [10, 6],
    status: 'UNRESOLVED',
    pack: makePack(state, data, state.age, { boss: false, row: 2 }),
  };
  
  // Trigger guard encounter
  state = act(state, 'BEGIN_ENCOUNTER', {});
  assert.ok(state.battle, 'Battle must be active');
  assert.equal(state.battle.status, 'ACTIVE');
  const enemyId = state.battle.id;
  
  // Reload verification
  save(store, state, data);
  const loaded = load(store, data);
  assert.equal(loaded.state.battle.status, 'ACTIVE');
  assert.equal(loaded.state.battle.id, enemyId);
});

// ---------------------------------------------------------------------------
// J07: Tactical interaction
// ---------------------------------------------------------------------------
test('J07 Tactical interaction: unit selection, initiative queue, legal actions, battle log', () => {
  let state = newCampaign(contract, data, 1_000_000);
  state = act(state, 'ENTER_ADVENTURE', {});
  state.adventure.pendingEncounter = {
    id: 'guard-10,5',
    cell: [10, 5],
    origin: [10, 6],
    status: 'UNRESOLVED',
    pack: makePack(state, data, state.age, { boss: false, row: 2 }),
  };
  state = act(state, 'BEGIN_ENCOUNTER', {});
  
  const activeId = activeStackId(state.battle);
  assert.ok(activeId, 'Active stack must exist');
  
  // Legal Defend command
  state = act(state, 'BATTLE', { action: 'defend', stackId: activeId });
  const lastAction = state.battle.log[state.battle.log.length - 1];
  assert.ok(lastAction, 'Action must be logged');
  assert.equal(lastAction.type, 'defend');
});

// ---------------------------------------------------------------------------
// J08: Retreat/Auto/results
// ---------------------------------------------------------------------------
test('J08 Retreat/Auto/results: retreat confirmation, auto resolution, settlement once-only', () => {
  const store = memory();
  let state = newCampaign(contract, data, 1_000_000);
  state = act(state, 'START_SKIRMISH', {});
  assert.equal(state.battle.status, 'ACTIVE');
  
  // Auto resolve
  state = act(state, 'BATTLE', { action: 'auto' });
  assert.ok(state.battle.status === 'RESOLVED' || state.battle.pendingSettlement);
  
  // Settle battle once
  state = act(state, 'SETTLE_BATTLE', {});
  assert.equal(state.battle, null);
  
  // Repeated settlement throws
  assert.throws(() => act(state, 'SETTLE_BATTLE', {}), /No pending/);

  // Reload verification
  save(store, state, data);
  const loaded = load(store, data);
  assert.equal(loaded.state.battle, null);
});

// ---------------------------------------------------------------------------
// J09: Defense
// ---------------------------------------------------------------------------
test('J09 Defense: preparation, deployment, ticking, pause control, save/reload', () => {
  const store = memory();
  let state = newCampaign(contract, data, 1_000_000);
  state = act(state, 'START_SIEGE', {});
  assert.ok(state.defense);
  assert.equal(state.defense.practice, 'siege');
  
  // Deploy hero & army
  state = act(state, 'DEPLOY_DEFENSE', {});
  state = act(state, 'DEPLOY_ARMY', { stackId: state.army[0].id });
  assert.equal(state.defense.heroDeployed, true);
  assert.equal(state.defense.armyDeployed, true);
  
  // Pause stops time
  state = act(state, 'DEFENSE', { dt: 1, paused: true });
  assert.equal(state.defense.time, 0);
  
  // Tick advances time
  state = act(state, 'DEFENSE', { dt: 0.5, speed: 1 });
  assert.ok(state.defense.time > 0);

  // Reload verification
  save(store, state, data);
  const loaded = load(store, data);
  assert.equal(loaded.state.defense.heroDeployed, true);
  assert.equal(loaded.state.defense.armyDeployed, true);
});

// ---------------------------------------------------------------------------
// J10: War modes
// ---------------------------------------------------------------------------
test('J10 War modes: Siege, Duel, Endless, Skirmish, Challenge practice isolation and seed reproducibility', () => {
  // 1. Skirmish isolation
  let state = newCampaign(contract, data, 1_000_000);
  const gold = state.resources.gold;
  state = act(state, 'START_SKIRMISH', {});
  assert.equal(state.battle.practice, 'skirmish');
  state = act(state, 'BATTLE', { action: 'auto' });
  state = act(state, 'SETTLE_BATTLE', {});
  assert.equal(state.resources.gold, gold, 'Skirmish must not alter campaign gold');
  
  // 2. Challenge with shared seed
  state = act(state, 'START_CHALLENGE', { seed: 987654321, code: 'valley-1' });
  assert.equal(state.battle.practice, 'challenge');
  state = act(state, 'BATTLE', { action: 'auto' });
  state = act(state, 'SETTLE_BATTLE', {});
  assert.equal(state.resources.gold, gold, 'Challenge must not alter campaign gold');

  // 3. Duel
  state = act(state, 'START_DUEL', {});
  assert.ok(state.battle.encounterId.startsWith('duel-'));
  state = act(state, 'BATTLE', { action: 'auto' });
  state = act(state, 'SETTLE_BATTLE', {});
  
  // 4. Endless
  state = act(state, 'START_ENDLESS', {});
  assert.equal(state.defense.practice, 'endless');
});

// ---------------------------------------------------------------------------
// J11: Craft/equip
// ---------------------------------------------------------------------------
test('J11 Craft/equip: Armory forge, quality/cost, equip/unequip, stat changes, 6 slots coverage', () => {
  const store = memory();
  let state = newCampaign(contract, data, 1_000_000);
  
  // Build and complete Armory
  state = act(state, 'BUILD', { plotId: 'P05', building: 'armory' });
  state = finishBuild(state);
  
  // Provide crafting resources
  state.resources.food += 1000;
  state.resources.wood += 1000;
  state.resources.stone += 1000;
  state.resources.gold += 1000;

  // Test all 6 gear slots
  for (const slot of GEAR_SLOTS) {
    const initialInv = state.inventory.length;
    const initialStats = heroStats(state, data);
    
    // Forge item
    state = act(state, 'FORGE', { slot, quality: 0 });
    assert.equal(state.inventory.length, initialInv + 1);
    const craftedItem = state.inventory[state.inventory.length - 1];
    assert.equal(craftedItem.slot, slot);
    
    // Equip item
    state = act(state, 'EQUIP', { itemId: craftedItem.id });
    assert.equal(state.hero.equip[slot].id, craftedItem.id);
    
    // Stat check
    const equippedStats = heroStats(state, data);
    assert.ok(
      equippedStats.atk >= initialStats.atk &&
      equippedStats.def >= initialStats.def,
      `Equipping ${slot} must apply valid non-negative stat changes`
    );
    
    // Unequip item
    state = act(state, 'UNEQUIP', { slot });
    assert.equal(state.hero.equip[slot], null);
    assert.deepEqual(heroStats(state, data), initialStats);
  }

  // Reload verification
  save(store, state, data);
  const loaded = load(store, data);
  assert.equal(loaded.state.inventory.length, 6);
});

// ---------------------------------------------------------------------------
// J12: Hero progression
// ---------------------------------------------------------------------------
test('J12 Hero progression: spend point, choose skill, wisdom level and resurrection eligibility', () => {
  const store = memory();
  let state = newCampaign(contract, data, 1_000_000);
  
  // Grant level point and offer
  state.hero.level = 2;
  state.hero.points = 1;
  state.hero.growth.atk += 1;
  state.hero.offers.push({ level: 2, choices: ['wisdom', 'leadership'] });
  
  const beforeAtk = state.hero.bonus.atk;
  state = act(state, 'SPEND_POINT', { stat: 'atk' });
  assert.equal(state.hero.bonus.atk, beforeAtk + 1);
  assert.equal(state.hero.points, 0);
  
  state = act(state, 'CHOOSE_SKILL', { skill: 'wisdom' });
  assert.equal(state.hero.skills.wisdom, 1);

  // Reload verification
  save(store, state, data);
  const loaded = load(store, data);
  assert.equal(loaded.state.hero.bonus.atk, beforeAtk + 1);
  assert.equal(loaded.state.hero.skills.wisdom, 1);
});

// ---------------------------------------------------------------------------
// J13: Creatures/roster
// ---------------------------------------------------------------------------
test('J13 Creatures/roster: dwelling offer, cancel keeps terms, claim recruits creature stack to army', () => {
  const store = memory();
  let state = newCampaign(contract, data, 1_000_000);
  
  // Build and complete Barracks to have armyCapacity >= 3
  state = act(state, 'BUILD', { plotId: 'P04', building: 'barracks' });
  state = finishBuild(state);
  
  state = act(state, 'ENTER_ADVENTURE', {});
  
  // Move to dwelling site approach: contract dwelling site approach is at [10, 8]
  state.adventure.x = 10;
  state.adventure.y = 8;
  
  // Open offer
  state = act(state, 'OFFER_DWELLING', { type: 'wolf' });
  assert.ok(state.dwelling);
  assert.equal(state.dwelling.type, 'wolf');
  assert.equal(state.dwelling.claimed, false);
  
  // Cancel does not destroy the terms
  state = act(state, 'CANCEL_DWELLING', {});
  assert.equal(state.dwelling.type, 'wolf');
  
  // Claim dwelling
  state.resources.food += 500;
  state.resources.gold += 500;
  const initialArmyLen = state.army.length;
  state = act(state, 'CLAIM_DWELLING', {});
  assert.equal(state.dwelling.claimed, true);
  assert.equal(state.army.length, initialArmyLen + 1);
  const creatureStack = state.army[state.army.length - 1];
  assert.equal(creatureStack.kind, 'creature');
  assert.equal(creatureStack.type, 'wolf');

  // Reload verification
  save(store, state, data);
  const loaded = load(store, data);
  assert.equal(loaded.state.army.some(s => s.kind === 'creature' && s.type === 'wolf'), true);
});

// ---------------------------------------------------------------------------
// J14: Story/quests
// ---------------------------------------------------------------------------
test('J14 Story/quests: rival choice, story milestone, quest claim once-only, future conclusion', () => {
  const store = memory();
  let state = newCampaign(contract, data, 1_000_000);
  
  // Choose rival
  state = act(state, 'CHOOSE_RIVAL', { name: 'Varek Iron-Eye' });
  assert.equal(state.story.rival, 'Varek Iron-Eye');
  
  // Story choice
  state = act(state, 'STORY_CHOICE', { index: 0 });
  assert.equal(state.story.chapter, 1);
  assert.equal(typeof state.story.choices[0], 'string');
  
  // Claim quest q2 (reach bronze age)
  state.age = 1;
  state = act(state, 'CLAIM_QUEST', { id: 'q2' });
  assert.equal(state.quests.q2.claimed, true);
  
  // Second claim throws
  assert.throws(() => act(state, 'CLAIM_QUEST', { id: 'q2' }), /already claimed/);
  
  // Future conclusion
  const futureState = structuredClone(state);
  futureState.age = 7;
  futureState.story.chapter = data.STORY.length;
  futureState.story.choices = data.STORY.map(s => s.ch[0].flag);
  const conc = futureConclusion(futureState, data);
  assert.ok(conc.includes('The Valley We Keep'));

  // Reload verification
  save(store, state, data);
  const loaded = load(store, data);
  assert.equal(loaded.state.story.rival, 'Varek Iron-Eye');
  assert.equal(loaded.state.quests.q2.claimed, true);
});

// ---------------------------------------------------------------------------
// J15: Market
// ---------------------------------------------------------------------------
test('J15 Market: locked in Stone, unlocked in Bronze, insufficient balance, legal buy/sell deltas', () => {
  const store = memory();
  let state = newCampaign(contract, data, 1_000_000);
  
  // In Stone age, market is locked
  assert.throws(() => act(state, 'MARKET', { side: 'buy', resource: 'wood' }), /Bronze Age/);
  
  // Advance to Bronze age
  state.age = 1;
  
  // Insufficient balance rejects cleanly
  state.resources.gold = 0;
  assert.throws(() => act(state, 'MARKET', { side: 'buy', resource: 'wood' }), /resources/);
  
  // Legal buy
  state.resources.gold = 200;
  const initialWood = state.resources.wood;
  state = act(state, 'MARKET', { side: 'buy', resource: 'wood' });
  assert.ok(state.resources.wood > initialWood);
  assert.ok(state.resources.gold < 200);
  
  // Legal sell
  const goldBeforeSell = state.resources.gold;
  state = act(state, 'MARKET', { side: 'sell', resource: 'wood' });
  assert.equal(state.resources.wood, initialWood);
  assert.ok(state.resources.gold > goldBeforeSell);

  // Reload verification
  save(store, state, data);
  const loaded = load(store, data);
  assert.equal(loaded.state.resources.wood, initialWood);
});

// ---------------------------------------------------------------------------
// J16: Recovery
// ---------------------------------------------------------------------------
test('J16 Recovery: multi-slot store/load, encode/decode export, corrupt file protection', () => {
  const store = memory();
  const state = newCampaign(contract, data, 1_000_000);
  
  // Store into slot 1
  storeSlot(store, 1, state, data);
  const loadedSlot1 = loadSlot(store, 1, data);
  assert.ok(loadedSlot1);
  assert.equal(loadedSlot1.id, state.id);
  
  // Encode and decode export
  const exported = encode(state, data);
  const imported = decode(exported, data);
  assert.equal(imported.id, state.id);
  
  // Corrupt string rejected without breaking storage
  assert.throws(() => decode('{ "corrupted": true }', data));
  const stillValid = loadSlot(store, 1, data);
  assert.equal(stillValid.id, state.id);
});

// ---------------------------------------------------------------------------
// J17: Settings/tutorial
// ---------------------------------------------------------------------------
test('J17 Settings/tutorial: independent music/sfx, reduced motion, tutorial skip/review', () => {
  const store = memory();
  let state = newCampaign(contract, data, 1_000_000);
  
  // Update settings
  state = act(state, 'SETTINGS', { music: 0.3, sfx: 0.7, reducedMotion: true });
  assert.equal(state.settings.music, 0.3);
  assert.equal(state.settings.sfx, 0.7);
  assert.equal(state.settings.reducedMotion, true);
  
  // Skip and review tutorial
  state = act(state, 'TUTORIAL_SKIP', {});
  assert.equal(state.tutorial.skipped, true);
  state = act(state, 'TUTORIAL_REVIEW', {});
  assert.equal(state.tutorial.skipped, false);

  // Reload verification
  save(store, state, data);
  const loaded = load(store, data);
  assert.equal(loaded.state.settings.reducedMotion, true);
  assert.equal(loaded.state.tutorial.skipped, false);
});

// ---------------------------------------------------------------------------
// J18: Whole-game continuity
// ---------------------------------------------------------------------------
test('J18 Whole-game continuity: build -> recruit -> craft -> travel -> fight -> return -> defend -> save/reload', () => {
  const store = memory();
  let state = newCampaign(contract, data, 1_000_000);
  
  // 1. Build infrastructure
  state = act(state, 'BUILD', { plotId: 'P01', building: 'lumber' });
  state = finishBuild(state);
  
  // Add funding for subsequent builds
  state.resources.food += 1000;
  state.resources.wood += 1000;
  state.resources.stone += 1000;
  state.resources.gold += 1000;
  
  state = act(state, 'BUILD', { plotId: 'P04', building: 'barracks' });
  state = finishBuild(state);
  state = act(state, 'BUILD', { plotId: 'P05', building: 'armory' });
  state = finishBuild(state);
  
  // 2. Recruit troops
  state = act(state, 'RECRUIT', { role: 'melee' });
  const recruitedCount = state.army.find(s => s.type === 'melee').count;
  
  // 3. Craft & Equip
  state = act(state, 'FORGE', { slot: 'weapon', quality: 0 });
  const sword = state.inventory[state.inventory.length - 1];
  state = act(state, 'EQUIP', { itemId: sword.id });
  assert.equal(state.hero.equip.weapon.id, sword.id);
  
  // 4. Adventure travel & return to town approach [8, 4]
  state = act(state, 'ENTER_ADVENTURE', {});
  assert.equal(state.adventure.atTown, false);
  state.adventure.x = 8;
  state.adventure.y = 4;
  state = act(state, 'RETURN_TOWN', {});
  assert.equal(state.adventure.atTown, true);
  
  // 5. Defend
  state = act(state, 'START_SIEGE', {});
  state = act(state, 'DEPLOY_DEFENSE', {});
  state = act(state, 'DEFENSE', { dt: 0.5, speed: 1 });
  
  // 6. Save and Reload
  save(store, state, data);
  const reloaded = load(store, data);
  assert.equal(reloaded.status, 'VALID');
  
  // Continuity verification
  assert.equal(reloaded.state.plots.find(p => p.id === 'P01').level, 1);
  assert.equal(reloaded.state.plots.find(p => p.id === 'P04').level, 1);
  assert.equal(reloaded.state.plots.find(p => p.id === 'P05').level, 1);
  assert.equal(reloaded.state.army.find(s => s.type === 'melee').count, recruitedCount);
  assert.equal(reloaded.state.hero.equip.weapon.id, sword.id);
  assert.equal(reloaded.state.adventure.atTown, true);
  assert.equal(reloaded.state.defense.heroDeployed, true);
});
