// Independently authored campaign; approved tables are injected as data.
import contract from '../data/implementation-contract.json' with { type: 'json' };
import { adventureMap, routeCost } from './navigation.js';
import { addRankXp, dwellingCost, dwellingPool, dwellingTerms, endDay, grantHeroXp, makePack, rankForXp, rollLoot } from './mechanics.js';
import { GEAR_SLOTS, RIVALS, SKILL_IDS, agePrice, dailyMoves, forgeOffer, gateHp, heroStats, manaMax, marketQuote, recruitCost, towerPurchaseCost, validItem } from './rules.js';
import { castSpell, createChallengeBattle, createDuelBattle, createEncounterBattle, createSkirmishBattle, defend, move as battleMove, playOut, retreat, strike, validateBattle, wait as battleWait } from './battle.js';
import { advanceDefense, createDefense, deployHero, earlyCall, validateDefense } from './defense.js';
export const SCHEMA = 1;
export { gateHp, heroStats, manaMax, dailyMoves };
const producers = { farm: ['food', .55], lumber: ['wood', .45], quarry: ['stone', .35], mine: ['gold', .25] };
const unique = new Set(['barracks', 'workshop', 'hall', 'armory']);
const resources = ['food', 'wood', 'stone', 'gold'];
const map = adventureMap(contract.geometry.adventure);
const townApproach = contract.geometry.adventure.sites.find(site => site.id === 'town').approach;
const heroAnchor = contract.geometry.adventure.anchors.hero;
export function newCampaign(contract, data, now, seed = 123456789) {
  const state = {
    schema: SCHEMA, id: `campaign-${seed}`, revision: 0, seed, rngState: seed >>> 0,
    age: 0, day: 1, resources: { food: 250, wood: 250, stone: 160, gold: 150 },
    plots: contract.geometry.kingdom.sites.map(s => ({ id: s.id, type: s.id === 'townhall' ? 'townhall' : null, level: s.id === 'townhall' ? 1 : 0 })),
    walls: { level: 0 }, buildJobs: [], clock: now,
    hero: { id: 'hero-1', class: 'knight', level: 1, xp: 0, points: 0, growth: { atk: 0, def: 0, pow: 0, kno: 0 }, bonus: { atk: 0, def: 0, pow: 0, kno: 0 }, offers: [], mana: 10, skills: Object.fromEntries(SKILL_IDS.map(k => [k, 0])), equip: Object.fromEntries(contract.slots.map(k => [k, null])) },
    army: [{ id: 'army-1', kind: 'role', type: 'melee', age: 0, count: 12, rank: 0, xp: 0 }, { id: 'army-2', kind: 'role', type: 'ranged', age: 0, count: 8, rank: 0, xp: 0 }],
    towers: [{ id: 'tower-1', fam: 'arrow', tier: 0, rank: 0, xp: 0 }, { id: 'tower-2', fam: 'slow', tier: 0, rank: 0, xp: 0 }],
    inventory: [], story: { flags: {} }, quests: {}, tutorial: { step: 0, skipped: false },
    settings: { music: .6, sfx: .8, reducedMotion: false }, weather: 'clear', adventure: null, battle: null, defense: null, dwelling: null,
    settledTransactions: {}
  };
  validate(state, data); return state;
}
const PRIMARIES = ['atk', 'def', 'pow', 'kno'];
function bag(value) {
  return value && PRIMARIES.every(key => Number.isInteger(value[key]) && value[key] >= 0) && Object.keys(value).length === 4;
}
export function validate(s, data) {
  if (s?.schema !== SCHEMA) throw new Error('Unsupported save schema');
  if (!Number.isInteger(s.age) || s.age < 0 || s.age > 7 || !Number.isFinite(s.clock) || s.clock < 0 || !Number.isInteger(s.revision) || s.revision < 0) throw new Error('Invalid age/clock/revision');
  if (!Number.isInteger(s.day) || s.day < 1 || !Number.isInteger(s.rngState) || s.rngState < 0 || s.rngState > 0xffffffff) throw new Error('Invalid day or random state');
  if (s.weather != null && !data.WEATHER[s.weather]) throw new Error('Invalid weather');
  if (resources.some(k => !Number.isFinite(s.resources?.[k]) || s.resources[k] < 0) || Object.keys(s.resources).length !== 4) throw new Error('Invalid campaign resources');
  const siteIds = new Set(contract.geometry.kingdom.sites.map(site => site.id));
  if (!Array.isArray(s.plots) || s.plots.length !== 18 || new Set(s.plots.map(p => p.id)).size !== 18) throw new Error('Invalid campaign sites');
  for (const p of s.plots) if (!siteIds.has(p.id) || !Number.isInteger(p.level) || p.level < 0 || (p.type && !data.BUILDINGS[p.type]) || (p.type === null && p.level !== 0)) throw new Error('Invalid plot');
  const hall = s.plots.find(p => p.id === 'townhall');
  if (!hall || hall.type !== 'townhall' || hall.level < 1 || s.plots.some(p => p.id !== 'townhall' && (p.type === 'townhall' || p.type === 'walls'))) throw new Error('Invalid hall/perimeter');
  for (const type of unique) if (s.plots.filter(p => p.type === type).length > 1) throw new Error('Duplicate unique facility');
  if (!Number.isInteger(s.walls?.level) || s.walls.level < 0 || !Array.isArray(s.buildJobs) || !s.settledTransactions || typeof s.settledTransactions !== 'object') throw new Error('Invalid jobs/perimeter');
  const jobs = new Set();
  for (const j of s.buildJobs) {
    const wallsOk = j.plotId === 'walls' && j.type === 'walls' && j.targetLevel === s.walls.level + 1;
    const plotOk = j.plotId !== 'walls' && s.plots.some(p => p.id === j.plotId && p.type === j.type && j.targetLevel === p.level + 1);
    if (jobs.has(j.plotId) || typeof j.id !== 'string' || !j.id || !data.BUILDINGS[j.type] || !Number.isFinite(j.completesAt) || j.completesAt < 0 || !Number.isInteger(j.targetLevel) || j.targetLevel < 1 || !(wallsOk || plotOk)) throw new Error('Invalid construction job');
    jobs.add(j.plotId);
  }
  const hero = s.hero;
  if (!data.CLASSES[hero?.class] || !Number.isInteger(hero.level) || hero.level < 1 || !Number.isFinite(hero.xp) || hero.xp < 0 || !Number.isInteger(hero.points) || hero.points < 0 || !bag(hero.growth) || !bag(hero.bonus)) throw new Error('Invalid hero');
  const gained = PRIMARIES.reduce((sum, key) => sum + hero.growth[key], 0);
  const bought = PRIMARIES.reduce((sum, key) => sum + hero.bonus[key], 0);
  if (gained !== hero.level - 1 || bought + hero.points !== hero.level - 1) throw new Error('Invalid hero progression');
  if (!Number.isFinite(hero.mana) || hero.mana < 0 || hero.mana > manaMax(s, data)) throw new Error('Invalid mana');
  if (SKILL_IDS.some(k => !Number.isInteger(hero.skills?.[k]) || hero.skills[k] < 0 || hero.skills[k] > 3) || Object.keys(hero.skills).length !== SKILL_IDS.length) throw new Error('Invalid skills');
  if (!Array.isArray(hero.offers)) throw new Error('Invalid skill offer');
  for (const offer of hero.offers) {
    if (!Number.isInteger(offer.level) || !Array.isArray(offer.choices) || offer.choices.length < 1 || offer.choices.length > 2 || new Set(offer.choices).size !== offer.choices.length || offer.choices.some(id => !SKILL_IDS.includes(id))) throw new Error('Invalid skill offer');
  }
  if (GEAR_SLOTS.some(slot => !(slot in hero.equip))) throw new Error('Invalid equipment slots');
  for (const slot of GEAR_SLOTS) {
    const item = hero.equip[slot];
    if (item && (!validItem(item, data) || item.slot !== slot)) throw new Error('Invalid equipment slot');
  }
  if (!Array.isArray(s.inventory) || !Array.isArray(s.army) || !Array.isArray(s.towers)) throw new Error('Invalid campaign collections');
  for (const item of s.inventory) if (!validItem(item, data)) throw new Error('Invalid item');
  const equipped = Object.values(hero.equip).filter(Boolean);
  const artifactIds = equipped.filter(item => item.kind === 'artifact').map(item => item.artifactId);
  if (new Set(artifactIds).size !== artifactIds.length) throw new Error('Duplicate artifact');
  for (const stack of s.army) {
    if (!['role', 'creature'].includes(stack.kind) || !Number.isInteger(stack.age) || stack.age < 0 || stack.age > 7 || !Number.isInteger(stack.count) || stack.count < 1 || !Number.isInteger(stack.rank) || stack.rank < 0 || stack.rank > 4 || !Number.isFinite(stack.xp) || stack.xp < 0 || stack.rank !== rankForXp(stack.xp)) throw new Error('Invalid army stack');
    if (stack.kind === 'role' && !data.ROLES[stack.type]) throw new Error('Invalid army role');
    if (stack.kind === 'creature' && !data.CREATURES[stack.type]) throw new Error('Invalid creature');
  }
  if (s.army.length > 2 + (s.plots.find(p => p.type === 'barracks')?.level ?? 0)) throw new Error('Army capacity');
  for (const tower of s.towers) {
    if (!data.TOWERS[tower.fam] || !Number.isInteger(tower.tier) || tower.tier < 0 || tower.tier > 7 || !Number.isInteger(tower.rank) || tower.rank < 0 || tower.rank > 4 || !Number.isFinite(tower.xp) || tower.xp < 0 || tower.rank !== rankForXp(tower.xp)) throw new Error('Invalid tower');
  }
  if (s.adventure != null) {
    const a = s.adventure;
    if (!Number.isInteger(a.x) || !Number.isInteger(a.y) || !map || !Number.isInteger(a.moves) || a.moves < 0 || a.moves > dailyMoves(s, data) || typeof a.atTown !== 'boolean' || !Array.isArray(a.visited) || !Array.isArray(a.resolvedGuards)) throw new Error('Invalid journey');
    const open = a.x >= 0 && a.y >= 0 && a.x < map.cols && a.y < map.rows && !map.blocked.has(`${a.x},${a.y}`);
    if (!open) throw new Error('Invalid journey');
    if (a.pendingEncounter != null) {
      const pending = a.pendingEncounter;
      if (typeof pending.id !== 'string' || !Array.isArray(pending.cell) || pending.cell.length !== 2 || typeof pending.status !== 'string') throw new Error('Invalid encounter');
    }
  }
  if (s.dwelling != null) {
    const offer = s.dwelling;
    if (typeof offer.type !== 'string' || !data.CREATURES[offer.type] || !Number.isInteger(offer.count) || offer.count < 1 || typeof offer.multiplier !== 'number' || typeof offer.claimed !== 'boolean') throw new Error('Invalid dwelling');
    if (!dwellingPool(data, s.age).includes(offer.type)) throw new Error('Invalid dwelling tier');
  }
  if (!s.settings || typeof s.settings.reducedMotion !== 'boolean' || !Number.isFinite(s.settings.music) || !Number.isFinite(s.settings.sfx) || s.settings.music < 0 || s.settings.music > 1 || s.settings.sfx < 0 || s.settings.sfx > 1) throw new Error('Invalid settings');
  if (!s.story || typeof s.story.flags !== 'object' || !s.tutorial || !Number.isInteger(s.tutorial.step) || s.tutorial.step < 0 || typeof s.tutorial.skipped !== 'boolean') throw new Error('Invalid campaign progress');
  if (s.story?.rival != null && !RIVALS.includes(s.story.rival)) throw new Error('Invalid rival');
  validateBattle(s.battle);
  validateDefense(s.defense);
  const ids = [hero.id, ...s.army.map(a => a.id), ...s.towers.map(t => t.id), ...s.inventory.map(i => i.id), ...equipped.map(i => i.id), ...s.buildJobs.map(j => j.id)];
  if (ids.some(id => typeof id !== 'string' || !id) || new Set(ids).size !== ids.length) throw new Error('Invalid campaign entity identity');
  return true;
}
function levelOf(s, type) {
  if (type === 'walls') return s.walls.level;
  return s.plots.find(p => p.type === type)?.level ?? 0;
}
function armyCapacity(s) { return 2 + levelOf(s, 'barracks'); }
function dwellingSite() { return contract.geometry.adventure.sites.find(site => site.id === 'dwelling'); }
function atDwelling(s) {
  const site = dwellingSite();
  if (!site || !s.adventure || s.adventure.atTown) return false;
  return s.adventure.x === site.approach[0] && s.adventure.y === site.approach[1];
}
function pay(s, payment) {
  if (Object.entries(payment).some(([k, n]) => !Number.isFinite(n) || n < 0 || s.resources[k] < n)) throw new Error('Not enough resources');
  for (const [k, n] of Object.entries(payment)) s.resources[k] -= n;
}
function gain(s, payment) { for (const [k, n] of Object.entries(payment)) s.resources[k] += n; }
function tutorial(s, input) {
  if (s.tutorial.skipped || input.type === 'TUTORIAL_SKIP' || input.type === 'TUTORIAL_REVIEW') return;
  const building = input.payload?.building;
  const step = s.tutorial.step;
  if (step === 0 && input.type === 'BUILD' && building === 'lumber') s.tutorial.step = 1;
  else if (step === 1 && input.type === 'BUILD' && building === 'farm') s.tutorial.step = 2;
  else if (step === 2 && input.type === 'BUILD' && building === 'quarry') s.tutorial.step = 3;
  else if (step === 3 && input.type === 'BUILD' && building === 'barracks') s.tutorial.step = 4;
  else if (step === 4 && input.type === 'RECRUIT') s.tutorial.step = 5;
  else if (step === 5 && input.type === 'ENTER_ADVENTURE') s.tutorial.step = 6;
}
export function cost(data, type, level) {
  const building = data.BUILDINGS[type];
  if (!building || !Number.isInteger(level) || level < 0) throw new Error('Invalid building/level');
  return Object.fromEntries(Object.entries(building.c).map(([k, amount]) => [k, Math.round(amount * building.g ** level)]));
}
export function rates(state) {
  const result = Object.fromEntries(resources.map(k => [k, 0]));
  for (const p of state.plots) if (producers[p.type]) { const [key, rate] = producers[p.type]; result[key] += p.level * rate; }
  return result;
}
const emptyReport = () => ({ elapsedMs: 0, creditedMs: 0, capped: false, income: { food: 0, wood: 0, stone: 0, gold: 0 }, completed: [] });
function settle(state, now, data, caps = [8, 7, 6, 5, 4, 3.5, 3, 3]) {
  validate(state, data);
  if (!Number.isFinite(now) || now < 0) throw new Error('Invalid time');
  if (now <= state.clock) return { state: structuredClone(state), report: emptyReport() }; // Never complete early or credit reversed time.
  const s = structuredClone(state), start = s.clock, creditedEnd = Math.min(now, start + caps[s.age] * 3600000);
  const report = { elapsedMs: now - start, creditedMs: creditedEnd - start, capped: creditedEnd < now, income: { food: 0, wood: 0, stone: 0, gold: 0 }, completed: [] };
  let cursor = start;
  const boundaries = [...new Set(s.buildJobs.filter(j => j.completesAt <= creditedEnd).map(j => Math.max(start, j.completesAt)))].sort((a, b) => a - b);
  const finish = job => {
    const p = job.plotId === 'walls' ? s.walls : s.plots.find(p => p.id === job.plotId);
    p.level = job.targetLevel;
    report.completed.push({ plotId: job.plotId, type: job.type, targetLevel: job.targetLevel });
  };
  for (const end of [...boundaries, creditedEnd]) {
    const income = rates(s);
    for (const k of resources) {
      const gained = income[k] * (end - cursor) / 1000;
      s.resources[k] += gained;
      report.income[k] += gained;
    }
    for (const job of s.buildJobs.filter(j => j.completesAt <= end)) finish(job);
    s.buildJobs = s.buildJobs.filter(j => j.completesAt > end); cursor = end;
  }
  // Jobs beyond the income cap still complete at the actual resume time, and they earn nothing for the uncredited gap.
  for (const job of s.buildJobs.filter(j => j.completesAt <= now)) finish(job);
  s.buildJobs = s.buildJobs.filter(j => j.completesAt > now); s.clock = now; s.revision++;
  validate(s, data); return { state: s, report };
}
export function advance(state, now, data, caps) { return settle(state, now, data, caps).state; }
export function advanceReported(state, now, data, caps) { return settle(state, now, data, caps); }
export function formatResume(report) {
  if (!report || (report.creditedMs <= 0 && report.completed.length === 0)) return '';
  const minutes = Math.floor(report.creditedMs / 60000);
  const seconds = Math.floor((report.creditedMs % 60000) / 1000);
  const gained = resources.filter(k => report.income[k] > 0).map(k => `${k} +${report.income[k].toFixed(2)}`);
  const built = report.completed.map(job => `${job.type} level ${job.targetLevel}`);
  return `Away time credited ${minutes}m ${seconds}s.${report.capped ? ' The age production cap stopped the rest.' : ''} ${gained.length ? 'Gained ' + gained.join(', ') + '.' : 'No production was credited.'} ${built.length ? 'Completed ' + built.join(', ') + '.' : 'No construction finished.'}`;
}
function applyBattleResult(s, data) {
  const battle = s.battle;
  if (!battle || battle.status !== 'RESOLVED' || !battle.pendingSettlement || battle.settled) throw new Error('No pending battle result');
  if (battle.practice === 'skirmish' || battle.practice === 'challenge') {
    if (battle.practice === 'challenge') s.story.flags[`challenge:${battle.id}`] = battle.outcome?.winner ?? 'none';
    s.battle = null;
    return;
  }
  if (battle.practice !== 'campaign') throw new Error('Unsupported battle');
  const flag = `battle:${battle.id}`;
  if (s.story.flags[flag]) throw new Error('Battle already settled');
  const winner = battle.outcome?.winner;
  for (const stack of battle.stacks) {
    if (!stack.campaignId) continue;
    const army = s.army.find(item => item.id === stack.campaignId);
    if (!army) continue;
    let count = stack.count;
    if (winner === 'p') {
      const rate = [0, 0.15, 0.3, 0.45][s.hero.skills.firstaid] || 0;
      const losses = Math.max(0, (stack.maxCount ?? count) - count);
      count = Math.min(stack.maxCount ?? count, count + Math.round(losses * rate));
    }
    army.count = count;
    if (winner !== 'retreat' && army.count > 0) addRankXp(army, Math.round((stack.dealt || 0) * 0.05) + (winner === 'p' ? 20 : 6));
  }
  s.army = s.army.filter(stack => stack.count > 0);
  s.hero.mana = Math.min(manaMax(s, data), Math.max(0, battle.mana ?? s.hero.mana));
  s.rngState = battle.rngState >>> 0;
  if (winner === 'p') {
    s.resources.gold += 150;
    const hall = s.plots.find(plot => plot.id === 'townhall');
    grantHeroXp(s, data, Math.round(110 * (battle.difficulty || 1)), hall?.level ?? 1);
    rollLoot(s, data, battle.difficulty || 1).forEach((drop, index) => {
      s.inventory.push({ ...drop, id: `loot-${s.revision}-${index}-${drop.slot}` });
    });
    if (s.adventure && Array.isArray(battle.adventureCell)) {
      s.adventure.x = battle.adventureCell[0];
      s.adventure.y = battle.adventureCell[1];
      const cell = s.adventure.pendingEncounter?.cell;
      if (cell) {
        const guard = `${cell[0]},${cell[1]}`;
        if (!s.adventure.resolvedGuards.includes(guard)) s.adventure.resolvedGuards.push(guard);
      }
      s.adventure.pendingEncounter = null;
    }
    s.story.flags[`cleared:${battle.encounterId}`] = true;
  } else if (winner === 'retreat' && s.adventure && Array.isArray(battle.origin)) {
    s.adventure.x = battle.origin[0];
    s.adventure.y = battle.origin[1];
  } else if (s.adventure && Array.isArray(battle.adventureCell)) {
    s.adventure.x = battle.adventureCell[0];
    s.adventure.y = battle.adventureCell[1];
  }
  s.story.flags[flag] = winner;
  s.battle = null;
}
function settleDefense(s, data) {
  const session = s.defense;
  if (!session || session.status !== 'RESOLVED' || !session.pendingSettlement) throw new Error('No pending defense result');
  if (session.practice === 'endless') {
    s.story.flags[`endless:${session.id}`] = session.clearedWaves;
    s.defense = null;
    return;
  }
  if (session.winner === 'p') {
    const difficulty = session.difficulty || 1;
    s.resources.gold += Math.round(150 * difficulty);
    s.resources.food += Math.round(100 * difficulty);
    const hall = s.plots.find(plot => plot.id === 'townhall');
    grantHeroXp(s, data, Math.round(90 * difficulty), hall?.level ?? 1);
    rollLoot(s, data, difficulty * 0.6).forEach((drop, index) => {
      s.inventory.push({ ...drop, id: `siege-${s.revision}-${index}-${drop.slot || drop.artifactId || 'drop'}` });
    });
  }
  s.story.flags[`siege:${session.id}`] = session.winner;
  s.defense = null;
}
export function command(state, input, now, data) {
  validate(state, data);
  if (typeof input?.id !== 'string' || !input.id || input.id.length > 128 || !Number.isFinite(now) || now < state.clock) throw new Error('Invalid transaction/time');
  const fingerprint = JSON.stringify({ type: input.type, payload: input.payload });
  if (Object.hasOwn(state.settledTransactions, input.id)) {
    if (state.settledTransactions[input.id] !== fingerprint) throw new Error('Transaction ID conflict');
    return structuredClone(state);
  }
  const s = advance(state, now, data);
  const payload = input.payload ?? {};
  const battlePending = s.battle && (s.battle.status === 'ACTIVE' || s.battle.pendingSettlement);
  const defensePending = s.defense && (s.defense.status === 'ACTIVE' || s.defense.pendingSettlement);
  if (battlePending && input.type !== 'BATTLE' && input.type !== 'SETTLE_BATTLE') throw new Error('Battle result is pending');
  if (defensePending && !['DEFENSE', 'SETTLE_DEFENSE', 'EARLY_CALL', 'DEPLOY_DEFENSE'].includes(input.type)) throw new Error('Defense result is pending');
  if (input.type === 'BUILD') {
    const { plotId, building } = payload;
    const p = plotId === 'walls' ? s.walls : s.plots.find(p => p.id === plotId);
    if (!p || !data.BUILDINGS[building] || s.buildJobs.some(j => j.plotId === plotId)) throw new Error('Invalid or occupied build destination');
    if ((plotId === 'townhall') !== (building === 'townhall') || (plotId === 'walls') !== (building === 'walls') || (p.type && p.type !== building)) throw new Error('Wrong building site');
    if (unique.has(building) && s.plots.some(q => q.id !== plotId && q.type === building)) throw new Error('Facility already exists');
    const payment = cost(data, building, p.level);
    if (Object.entries(payment).some(([k, n]) => s.resources[k] < n)) throw new Error('Not enough resources');
    const sum = Object.values(payment).reduce((a, b) => a + b, 0), duration = building === 'quarry' && p.level === 0 ? 3000 : Math.round(3000 + Math.min(1, Math.max(0, (sum - 300) / 2200)) * 5000);
    for (const [k, n] of Object.entries(payment)) s.resources[k] -= n;
    if (plotId !== 'walls') p.type = building;
    s.buildJobs.push({ id: input.id, plotId, type: building, targetLevel: p.level + 1, completesAt: now + duration });
  } else if (input.type === 'AGE_UP') {
    if (s.age >= 7) throw new Error('Already the last age');
    const hall = s.plots.find(p => p.id === 'townhall');
    if (!hall || hall.level < s.age + 2) throw new Error('Town Hall level too low');
    pay(s, agePrice(s.age));
    s.age += 1;
  } else if (input.type === 'RECRUIT') {
    if (levelOf(s, 'barracks') < 1) throw new Error('Barracks required');
    if (!data.ROLES[payload.role]) throw new Error('Invalid role');
    const same = s.army.find(a => a.kind === 'role' && a.type === payload.role && a.age === s.age);
    if (!same && s.army.length >= armyCapacity(s)) throw new Error('Army capacity');
    pay(s, recruitCost(data, payload.role, s.age));
    if (same) same.count += 5;
    else s.army.push({ id: `army-${input.id}`, kind: 'role', type: payload.role, age: s.age, count: 5, rank: 0, xp: 0 });
  } else if (input.type === 'BUY_TOWER') {
    if (!data.TOWERS[payload.family]) throw new Error('Invalid tower');
    if (s.towers.some(t => t.fam === payload.family)) throw new Error('Tower family already owned');
    if (s.towers.length >= 2 + levelOf(s, 'workshop')) throw new Error('Workshop capacity');
    pay(s, towerPurchaseCost(data, payload.family, s.age));
    s.towers.push({ id: `tower-${input.id}`, fam: payload.family, tier: s.age, rank: 0, xp: 0 });
  } else if (input.type === 'RETROFIT') {
    const tower = s.towers.find(t => t.id === payload.towerId);
    if (!tower) throw new Error('Unknown tower');
    if (tower.tier === s.age) throw new Error('Retrofit is a no-op');
    const old = tower.tier;
    pay(s, { wood: 120 * (old + 1), stone: 100 * (old + 1), gold: 80 * (old + 1) });
    tower.tier = s.age;
  } else if (input.type === 'FORGE') {
    if (!GEAR_SLOTS.includes(payload.slot)) throw new Error('Invalid slot');
    const offer = forgeOffer(s.age, levelOf(s, 'armory'), payload.quality ?? null);
    pay(s, offer.cost);
    s.inventory.push({ id: `item-${input.id}`, kind: 'gear', slot: payload.slot, age: s.age, quality: offer.quality });
  } else if (input.type === 'EQUIP') {
    const index = s.inventory.findIndex(item => item.id === payload.itemId);
    if (index < 0) throw new Error('Item is not in the bag');
    const item = s.inventory[index];
    const previous = s.hero.equip[item.slot];
    if (item.kind === 'artifact' && Object.values(s.hero.equip).some(other => other && other.kind === 'artifact' && other.artifactId === item.artifactId)) throw new Error('Duplicate artifact');
    s.inventory.splice(index, 1);
    if (previous) s.inventory.push(previous);
    s.hero.equip[item.slot] = item;
    s.hero.mana = Math.min(s.hero.mana, manaMax(s, data));
  } else if (input.type === 'UNEQUIP') {
    const item = s.hero.equip[payload.slot];
    if (!item) throw new Error('Empty slot');
    s.hero.equip[payload.slot] = null;
    s.inventory.push(item);
    s.hero.mana = Math.min(s.hero.mana, manaMax(s, data));
  } else if (input.type === 'MARKET') {
    if (s.age < 1) throw new Error('Market opens in the Bronze Age');
    const quote = marketQuote(payload.side, payload.resource);
    pay(s, quote.spend);
    gain(s, quote.gain);
  } else if (input.type === 'SET_CLASS') {
    if (!data.CLASSES[payload.class]) throw new Error('Invalid class');
    if (s.hero.xp !== 0 || s.inventory.length || Object.values(s.hero.equip).some(Boolean) || s.adventure || s.battle) throw new Error('Class is already committed');
    s.hero.class = payload.class;
    s.hero.mana = manaMax(s, data);
  } else if (input.type === 'CHOOSE_RIVAL') {
    if (s.story.rival) throw new Error('Rival is already chosen');
    if (!RIVALS.includes(payload.name)) throw new Error('Invalid rival');
    s.story.rival = payload.name;
  } else if (input.type === 'ENTER_ADVENTURE') {
    if (s.battle) throw new Error('Journey already open');
    if (s.adventure) {
      if (!s.adventure.atTown) throw new Error('Journey already open');
      s.adventure.atTown = false;
    } else {
      const x = Math.floor(heroAnchor[0]);
      const y = Math.floor(heroAnchor[1]);
      s.adventure = { x, y, moves: dailyMoves(s, data), visited: [`${x},${y}`], resolvedGuards: [], pendingEncounter: null, atTown: false };
    }
  } else if (input.type === 'MOVE') {
    if (!s.adventure || s.adventure.atTown) throw new Error('Not traveling');
    if (s.adventure.pendingEncounter && String(s.adventure.pendingEncounter.status).startsWith('UNRESOLVED')) throw new Error('Unresolved encounter');
    const start = [s.adventure.x, s.adventure.y];
    const route = routeCost(map, start, payload.path);
    let guardAt = -1;
    route.cells.forEach((cell, index) => {
      const key = `${cell[0]},${cell[1]}`;
      if (guardAt < 0 && map.guards.has(key) && !s.adventure.resolvedGuards.includes(key)) guardAt = index;
    });
    if (guardAt >= 0 && guardAt < route.cells.length - 1) throw new Error('Unresolved guard');
    if (route.cost > s.adventure.moves) throw new Error('Not enough movement');
    s.adventure.moves -= route.cost;
    s.adventure.x = route.destination[0];
    s.adventure.y = route.destination[1];
    for (const [x, y] of route.cells) {
      const cell = `${x},${y}`;
      if (!s.adventure.visited.includes(cell)) s.adventure.visited.push(cell);
    }
    if (guardAt >= 0) {
      const cell = route.cells[guardAt];
      const origin = guardAt === 0 ? start : route.cells[guardAt - 1];
      s.adventure.pendingEncounter = { id: `guard-${cell[0]},${cell[1]}`, cell, origin, status: 'UNRESOLVED', pack: makePack(s, data, s.age, { boss: false, row: 2 }) };
    }
  } else if (input.type === 'REST') {
    if (!s.adventure || s.adventure.atTown || s.adventure.moves < 1) throw new Error('Not enough movement');
    s.adventure.moves -= 1;
    s.hero.mana = manaMax(s, data);
  } else if (input.type === 'RETURN_TOWN') {
    if (!s.adventure || s.adventure.atTown || s.adventure.x !== townApproach[0] || s.adventure.y !== townApproach[1]) throw new Error('Not at the town approach');
    if (s.adventure.pendingEncounter && String(s.adventure.pendingEncounter.status).startsWith('UNRESOLVED')) throw new Error('Unresolved encounter');
    s.adventure.atTown = true;
  } else if (input.type === 'BEGIN_ENCOUNTER') {
    if (s.battle) throw new Error('Battle already open');
    s.battle = createEncounterBattle(s, data);
    s.battle.id = `battle-${s.adventure.pendingEncounter.id}-r${s.revision}`;
  } else if (input.type === 'BATTLE') {
    if (!s.battle || s.battle.status !== 'ACTIVE') throw new Error('No active battle');
    const action = payload.action;
    if (action === 'move') s.battle = battleMove(s.battle, payload.stackId, payload.to);
    else if (action === 'strike') s.battle = strike(s.battle, payload.stackId, payload.targetId, { forceMelee: payload.forceMelee === true, approach: payload.approach });
    else if (action === 'defend') s.battle = defend(s.battle, payload.stackId);
    else if (action === 'wait') s.battle = battleWait(s.battle, payload.stackId);
    else if (action === 'spell') {
      const spell = data.SPELLS[payload.spell];
      if (!spell) throw new Error('Unsupported spell');
      s.battle = castSpell(s.battle, { ...spell, id: payload.spell }, payload.targetId, s.battle.hero?.pow ?? 0);
    } else if (action === 'auto') s.battle = playOut(s.battle, { spells: Object.entries(data.SPELLS).map(([id, spell]) => ({ ...spell, id })) });
    else if (action === 'retreat') {
      if (payload.confirm !== true) throw new Error('Retreat must be confirmed');
      s.battle = retreat(s.battle);
    } else throw new Error('Unsupported battle command');
  } else if (input.type === 'SETTLE_BATTLE') applyBattleResult(s, data);
  else if (input.type === 'START_SKIRMISH') {
    if (s.battle || s.defense) throw new Error('Battle already open');
    if (s.adventure?.pendingEncounter && String(s.adventure.pendingEncounter.status).startsWith('UNRESOLVED')) throw new Error('Unresolved encounter');
    s.battle = createSkirmishBattle(s);
  } else if (input.type === 'START_DUEL') {
    if (s.battle || s.defense) throw new Error('Battle already open');
    s.battle = createDuelBattle(s, data);
  } else if (input.type === 'START_CHALLENGE') {
    if (s.battle || s.defense) throw new Error('Battle already open');
    s.battle = createChallengeBattle(payload.seed, payload.code);
  } else if (input.type === 'START_SIEGE') {
    if (s.battle || s.defense) throw new Error('Battle already open');
    s.defense = createDefense(s, data, { practice: 'siege', waves: 5 });
  } else if (input.type === 'START_ENDLESS') {
    if (s.battle || s.defense) throw new Error('Battle already open');
    s.defense = createDefense(s, data, { practice: 'endless', waves: 3 });
  } else if (input.type === 'DEFENSE') {
    if (!s.defense || s.defense.status !== 'ACTIVE') throw new Error('No active defense');
    s.defense = advanceDefense(s.defense, payload.dt ?? 0, { paused: payload.paused === true, speed: payload.speed });
  } else if (input.type === 'DEPLOY_DEFENSE') {
    if (!s.defense || s.defense.status !== 'ACTIVE') throw new Error('No active defense');
    const gold = s.resources.gold;
    s.defense = deployHero(s.defense, heroStats(s, data).atk);
    if (s.resources.gold !== gold) throw new Error('Deployment fee');
  } else if (input.type === 'EARLY_CALL') {
    if (!s.defense) throw new Error('No active defense');
    const gold = s.resources.gold;
    s.defense = earlyCall(s.defense);
    s.resources.gold = gold + 25 * (s.age + 1);
  } else if (input.type === 'SETTLE_DEFENSE') settleDefense(s, data);
  else if (input.type === 'END_DAY') {
    endDay(s, data);
    if (s.adventure) s.adventure.moves = dailyMoves(s, data);
  } else if (input.type === 'SPEND_POINT') {
    if (s.hero.points < 1 || !PRIMARIES.includes(payload.stat)) throw new Error('No spendable point');
    s.hero.points -= 1;
    s.hero.bonus[payload.stat] += 1;
    if (payload.stat === 'kno') s.hero.mana = manaMax(s, data);
  } else if (input.type === 'CHOOSE_SKILL') {
    const offer = s.hero.offers.find(item => !item.chosen && !item.declined);
    if (!offer || !offer.choices.includes(payload.skill) || s.hero.skills[payload.skill] >= 3) throw new Error('Invalid skill offer');
    s.hero.skills[payload.skill] += 1;
    offer.chosen = payload.skill;
  } else if (input.type === 'DECLINE_SKILL') {
    const offer = s.hero.offers.find(item => !item.chosen && !item.declined);
    if (!offer) throw new Error('Invalid skill offer');
    offer.declined = true;
  } else if (input.type === 'OFFER_DWELLING') {
    if (!atDwelling(s)) throw new Error('Not at the dwelling');
    if (s.dwelling && !s.dwelling.claimed) {
      if (payload.type && payload.type !== s.dwelling.type) throw new Error('Offer already open');
      // Saved terms stay. Cancel and reload must not roll a new pack.
    } else {
      const terms = dwellingTerms(s.story.flags || {});
      if (!dwellingPool(data, s.age).includes(payload.type)) throw new Error('Invalid dwelling tier');
      s.dwelling = { type: payload.type, count: terms.count, multiplier: terms.multiplier, claimed: false };
    }
  } else if (input.type === 'CANCEL_DWELLING') {
    if (!s.dwelling || s.dwelling.claimed) throw new Error('No dwelling offer');
  } else if (input.type === 'CLAIM_DWELLING') {
    if (!s.dwelling || s.dwelling.claimed) throw new Error('No dwelling offer');
    if (s.army.length >= armyCapacity(s)) throw new Error('Army capacity');
    if (!atDwelling(s)) throw new Error('Not at the dwelling');
    if (!dwellingPool(data, s.age).includes(s.dwelling.type)) throw new Error('Invalid dwelling tier');
    const payment = dwellingCost(data, s.dwelling.type, s.dwelling.multiplier);
    pay(s, payment);
    s.army.push({ id: `army-${input.id}`, kind: 'creature', type: s.dwelling.type, age: s.age, count: s.dwelling.count, rank: 0, xp: 0 });
    s.dwelling.claimed = true;
  } else if (input.type === 'SETTINGS') {
    const music = payload.music ?? s.settings.music;
    const sfx = payload.sfx ?? s.settings.sfx;
    if (!Number.isFinite(music) || !Number.isFinite(sfx) || music < 0 || music > 1 || sfx < 0 || sfx > 1) throw new Error('Invalid audio setting');
    s.settings = { music, sfx, reducedMotion: Boolean(payload.reducedMotion) };
  } else if (input.type === 'TUTORIAL_SKIP') s.tutorial.skipped = true;
  else if (input.type === 'TUTORIAL_REVIEW') s.tutorial.skipped = false;
  else throw new Error('Unsupported command');
  tutorial(s, input);
  s.settledTransactions[input.id] = fingerprint; s.revision++;
  validate(s, data); return s;
}
