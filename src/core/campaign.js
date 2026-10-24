// Independently authored campaign; approved tables are injected as data.
import contract from '../data/implementation-contract.json' with { type: 'json' };
import adventureWorlds from '../data/adventure-worlds.json' with { type: 'json' };
import { adventureGeometryForWorld, adventureMap, isOpen, routeCost, routeTo } from './navigation.js';
import { addRankXp, createSkillOffer, dwellingCost, dwellingPool, dwellingTerms, endDay, grantHeroXp, makePack, rankForXp, rollLoot } from './mechanics.js';
import { GEAR_SLOTS, RIVALS, SKILL_IDS, agePrice, dailyMoves, forgeOffer, gateHp, heroStats, manaMax, marketQuote, recruitCost, towerPurchaseCost, validItem } from './rules.js';
import { activeStackId, adoptBattle, autoStep, castSpell, createChallengeBattle, createDuelBattle, createEncounterBattle, createSkirmishBattle, defend, move as battleMove, placeDeployment, playOut, retreat, skipBonus, startDeployedBattle, strike, validateBattle, wait as battleWait } from './battle.js';
import { adoptDefense, advanceDefense, castDefense, createDefense, deployArmy, deployHero, earlyCall, validateDefense } from './defense.js';
export const SCHEMA = 1;
export { gateHp, heroStats, manaMax, dailyMoves };
const producers = { farm: ['food', .55], lumber: ['wood', .45], quarry: ['stone', .35], mine: ['gold', .25] };
const unique = new Set(['barracks', 'workshop', 'hall', 'armory']);
const resources = ['food', 'wood', 'stone', 'gold'];
export const DEFAULT_ADVENTURE_WORLD_ID = adventureWorlds[0].id;
const adventureWorldIds = new Set(adventureWorlds.map(world => world.id));
const adventureWorld = id => adventureWorlds.find(world => world.id === id);
const adventureGeometry = (id, seed) => adventureGeometryForWorld(contract.geometry.adventure, adventureWorld(id), seed);
const adventureMapForWorld = (id, seed) => adventureMap(adventureGeometry(id, seed));
const ADVENTURE_GEOMETRY_VERSION = 4;

function nearestReachableCell(geometry, map, target, preferred = []) {
  const start = geometry.anchors.hero.map(Math.floor);
  const preferredSet = new Set(preferred);
  const candidates = [];
  for (let y = 0; y < map.rows; y += 1) for (let x = 0; x < map.cols; x += 1) {
    if (!isOpen(map, x, y) || map.guards?.has(`${x},${y}`)) continue;
    candidates.push([x, y]);
  }
  candidates.sort((first, second) => {
    const firstId = first.join(','), secondId = second.join(',');
    const firstDistance = Math.abs(first[0] - target[0]) + Math.abs(first[1] - target[1]);
    const secondDistance = Math.abs(second[0] - target[0]) + Math.abs(second[1] - target[1]);
    return firstDistance - secondDistance
      || Number(preferredSet.has(secondId)) - Number(preferredSet.has(firstId))
      || first[1] - second[1] || first[0] - second[0];
  });
  for (const candidate of candidates) {
    try {
      if (candidate[0] === start[0] && candidate[1] === start[1]) return candidate;
      routeTo(map, start, candidate);
      return candidate;
    } catch { /* Choose the nearest reachable cell that keeps the journey valid. */ }
  }
  throw new Error('No reachable Adventure recovery cell');
}

function currentGuardCells(geometry) {
  return Object.entries(geometry.anchors)
    .filter(([id]) => id.startsWith('guard-'))
    .map(([id, point]) => ({ id, cell: point.map(Math.floor), key: point.map(Math.floor).join(',') }))
    .sort((first, second) => first.id.localeCompare(second.id));
}

function nearestGuardCell(guards, point) {
  return [...guards].sort((first, second) => {
    const distance = row => Math.abs(row.cell[0] - point[0]) + Math.abs(row.cell[1] - point[1]);
    return distance(first) - distance(second) || first.id.localeCompare(second.id);
  })[0];
}

function remapLegacyResolvedGuards(adventure, geometry) {
  if (!Array.isArray(adventure.resolvedGuards)) return;
  const guards = currentGuardCells(geometry);
  const pending = adventure.pendingEncounter;
  const pendingCell = pending && String(pending.status).startsWith('UNRESOLVED')
    && Array.isArray(pending.cell) && pending.cell.length === 2 && pending.cell.every(Number.isInteger)
    ? pending.cell
    : null;
  const pendingTarget = pendingCell && guards.length ? nearestGuardCell(guards, pendingCell)?.key : null;
  const used = new Set();
  const output = [];
  const oldCells = [];
  for (const value of adventure.resolvedGuards) {
    if (typeof value !== 'string' || !/^\d+,\d+$/.test(value)) {
      output.push(value);
      continue;
    }
    if (pendingCell && value === pendingCell.join(',')) continue;
    if (guards.some(row => row.key === value) && value !== pendingTarget && !used.has(value)) {
      used.add(value);
      output.push(value);
    } else {
      oldCells.push(value.split(',').map(Number));
    }
  }
  for (const oldCell of oldCells) {
    const target = nearestGuardCell(guards.filter(row => row.key !== pendingTarget && !used.has(row.key)), oldCell);
    if (!target) {
      // Keep excess historical clear markers instead of silently reducing progress.
      output.push(oldCell.join(','));
      continue;
    }
    used.add(target.key);
    output.push(target.key);
  }
  adventure.resolvedGuards = [...new Set(output)];
}

function relocateLegacyEncounter(state, geometry, map) {
  const adventure = state.adventure;
  const pending = adventure.pendingEncounter;
  if (!pending || !String(pending.status).startsWith('UNRESOLVED')) return false;
  if (!Array.isArray(pending.cell) || pending.cell.length !== 2 || !pending.cell.every(Number.isInteger)) return false;
  const guards = currentGuardCells(geometry).filter(row => !adventure.resolvedGuards.includes(row.key));
  if (!guards.length) return false;
  const { cell: targetCell } = nearestGuardCell(guards, pending.cell);
  const cell = targetCell;
  const oldOrigin = Array.isArray(pending.origin) && pending.origin.length === 2 && pending.origin.every(Number.isInteger)
    ? pending.origin
    : geometry.anchors.hero.map(Math.floor);
  const neighbors = [[0,-1],[-1,0],[1,0],[0,1]].map(([dx,dy]) => [cell[0] + dx, cell[1] + dy])
    .filter(([x,y]) => isOpen(map, x, y) && !map.guards.has(`${x},${y}`))
    .sort((first, second) => {
      const firstDistance = Math.abs(first[0] - oldOrigin[0]) + Math.abs(first[1] - oldOrigin[1]);
      const secondDistance = Math.abs(second[0] - oldOrigin[0]) + Math.abs(second[1] - oldOrigin[1]);
      return firstDistance - secondDistance || first[1] - second[1] || first[0] - second[0];
    });
  const start = geometry.anchors.hero.map(Math.floor);
  let origin = null;
  for (const candidate of neighbors) {
    try {
      if (candidate[0] === start[0] && candidate[1] === start[1]) { origin = candidate; break; }
      routeTo(map, start, candidate);
      origin = candidate;
      break;
    } catch { /* Try the next adjacent open cell. */ }
  }
  if (!origin) return false;
  adventure.x = cell[0];
  adventure.y = cell[1];
  const guardKey = cell.join(',');
  pending.id = `guard-${guardKey}`;
  pending.cell = cell;
  pending.origin = origin;
  if (!adventure.visited.includes(guardKey)) adventure.visited.push(guardKey);
  if (state.battle) {
    state.battle.adventureCell = cell;
    state.battle.origin = origin;
  }
  return true;
}

function reachableFromMapStart(geometry, map, cell) {
  const start = geometry.anchors.hero.map(Math.floor);
  if (cell[0] === start[0] && cell[1] === start[1]) return true;
  try { routeTo(map, start, cell); return true; }
  catch { return false; }
}

function migrateAdventureGeometry(state) {
  const adventure = state.adventure;
  if (!adventure || typeof adventure !== 'object' || Array.isArray(adventure)) return;
  const fromVersion = missing(adventure, 'geometryVersion') ? 1 : adventure.geometryVersion;
  if (![1, 2, 3].includes(fromVersion)) return;
  // v1 and v2 may need remapping; v3 to v4 only adjusts two site hitboxes.
  // Only coordinates that are invalid or disconnected from the current safe start move.
  const geometry = adventureGeometry(state.adventureWorldId, state.seed);
  const map = adventureMap(geometry);
  if (missing(adventure, 'resolvedGuards')) adventure.resolvedGuards = [];
  if (fromVersion <= 2) remapLegacyResolvedGuards(adventure, geometry);
  if (missing(adventure, 'visited')) adventure.visited = [];
  const visited = Array.isArray(adventure.visited) ? adventure.visited : [];
  const preferred = visited.filter(value => typeof value === 'string' && /^\d+,\d+$/.test(value));
  const oldPosition = Number.isInteger(adventure.x) && Number.isInteger(adventure.y)
    ? [adventure.x, adventure.y]
    : geometry.anchors.hero.map(Math.floor);
  const pending = adventure.pendingEncounter;
  const pendingCell = pending?.cell;
  const preserveVersion3Encounter = fromVersion === 3
    && pending && String(pending.status).startsWith('UNRESOLVED')
    && Array.isArray(pendingCell) && pendingCell.length === 2 && pendingCell.every(Number.isInteger)
    && pendingCell[0] === oldPosition[0] && pendingCell[1] === oldPosition[1]
    && map.guards.has(pendingCell.join(','))
    && Array.isArray(pending.origin) && pending.origin.length === 2 && pending.origin.every(Number.isInteger)
    && isOpen(map, ...pending.origin) && reachableFromMapStart(geometry, map, pending.origin);
  const relocatedEncounter = fromVersion <= 2
    ? relocateLegacyEncounter(state, geometry, map)
    : fromVersion === 3 && pending && String(pending.status).startsWith('UNRESOLVED') && !preserveVersion3Encounter
      ? relocateLegacyEncounter(state, geometry, map)
      : false;
  if (!relocatedEncounter && !preserveVersion3Encounter
    && (!isOpen(map, ...oldPosition) || map.guards.has(oldPosition.join(','))
      || !reachableFromMapStart(geometry, map, oldPosition))) {
    [adventure.x, adventure.y] = nearestReachableCell(geometry, map, oldPosition, preferred);
  }
  if (!Number.isInteger(adventure.x) || !Number.isInteger(adventure.y)) {
    [adventure.x, adventure.y] = geometry.anchors.hero.map(Math.floor);
  }
  if (state.battle && Array.isArray(state.battle.adventureCell)) {
    state.battle.adventureCell = [adventure.x, adventure.y];
    if (Array.isArray(state.battle.origin)
      && (!isOpen(map, ...state.battle.origin) || !reachableFromMapStart(geometry, map, state.battle.origin))) {
      state.battle.origin = nearestReachableCell(geometry, map, state.battle.origin, preferred);
    }
  }
  const recovered = `${adventure.x},${adventure.y}`;
  if (Array.isArray(adventure.visited) && !adventure.visited.includes(recovered)) adventure.visited.push(recovered);
  adventure.geometryVersion = ADVENTURE_GEOMETRY_VERSION;
}
export function newCampaign(contract, data, now, seed = 123456789, adventureWorldId = DEFAULT_ADVENTURE_WORLD_ID) {
  const state = {
    schema: SCHEMA, id: `campaign-${seed}`, revision: 0, seed, rngState: seed >>> 0,
    adventureWorldId,
    age: 0, day: 1, resources: { food: 250, wood: 250, stone: 160, gold: 150 },
    plots: contract.geometry.kingdom.sites.map(s => ({ id: s.id, type: s.id === 'townhall' ? 'townhall' : null, level: s.id === 'townhall' ? 1 : 0 })),
    walls: { level: 0 }, buildJobs: [], clock: now,
    hero: { id: 'hero-1', class: 'knight', level: 1, xp: 0, points: 0, growth: { atk: 0, def: 0, pow: 0, kno: 0 }, bonus: { atk: 0, def: 0, pow: 0, kno: 0 }, offers: [], mana: 10, skills: Object.fromEntries(SKILL_IDS.map(k => [k, 0])), equip: Object.fromEntries(contract.slots.map(k => [k, null])) },
    army: [{ id: 'army-1', kind: 'role', type: 'melee', age: 0, count: 12, rank: 0, xp: 0 }, { id: 'army-2', kind: 'role', type: 'ranged', age: 0, count: 8, rank: 0, xp: 0 }],
    towers: [{ id: 'tower-1', fam: 'arrow', tier: 0, rank: 0, xp: 0 }, { id: 'tower-2', fam: 'slow', tier: 0, rank: 0, xp: 0 }],
    inventory: [], story: { rival: null, flags: {}, chapter: 0, choices: [], futureSeen: false, milestones: {} },
    quests: Object.fromEntries(data.QUEST_TEMPLATES.map(quest => [quest.id, { claimed: false }])),
    tutorial: { step: 0, skipped: false },
    settings: { music: .6, sfx: .8, reducedMotion: false }, weather: 'clear', adventure: null, battle: null, defense: null, dwelling: null, dwellingHistory: [],
    practice: { challenges: {} },
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
  if (!adventureWorldIds.has(s.adventureWorldId)) throw new Error('Invalid Adventure world');
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
    if (offer.source != null && (offer.source !== 'adventure-shrine' || offer.siteId !== 'shrine')) throw new Error('Invalid skill offer source');
    if (offer.source === 'adventure-shrine' && (!s.adventure
      || (s.adventure.claimedSites.includes('shrine') && !offer.chosen && !offer.declined)
      || ((offer.chosen || offer.declined) && !s.adventure.claimedSites.includes('shrine')))) throw new Error('Invalid shrine offer state');
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
    const geometry = adventureGeometry(s.adventureWorldId, s.seed);
    const map = adventureMap(geometry);
    if (!Number.isInteger(a.geometryVersion) || a.geometryVersion !== ADVENTURE_GEOMETRY_VERSION) throw new Error('Invalid Adventure geometry version');
    if (!Number.isInteger(a.x) || !Number.isInteger(a.y) || !map || !Number.isInteger(a.moves) || a.moves < 0 || a.moves > dailyMoves(s, data) || typeof a.atTown !== 'boolean' || !Array.isArray(a.visited) || !Array.isArray(a.resolvedGuards)) throw new Error('Invalid journey');
    const cacheIds = resources.filter(id => Object.hasOwn(geometry.anchors, id));
    if (!a.cacheOffers || typeof a.cacheOffers !== 'object' || Array.isArray(a.cacheOffers) || Object.keys(a.cacheOffers).length !== cacheIds.length || cacheIds.some(id => !Number.isInteger(a.cacheOffers[id]) || a.cacheOffers[id] < 1) || !Array.isArray(a.collectedCaches) || new Set(a.collectedCaches).size !== a.collectedCaches.length || a.collectedCaches.some(id => !cacheIds.includes(id))) throw new Error('Invalid Adventure caches');
    const siteOfferKeys = ['millFood', 'mineGold', 'ruinXp'];
    const claimedSiteIds = ['mill', 'mine', 'ruin', 'shrine'];
    if (!a.siteOffers || typeof a.siteOffers !== 'object' || Array.isArray(a.siteOffers) || Object.keys(a.siteOffers).sort().join(',') !== siteOfferKeys.join(',') || siteOfferKeys.some(id => !Number.isInteger(a.siteOffers[id]) || a.siteOffers[id] < 1) || !Array.isArray(a.claimedSites) || new Set(a.claimedSites).size !== a.claimedSites.length || a.claimedSites.some(id => !claimedSiteIds.includes(id))) throw new Error('Invalid Adventure site offers');
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
  if (s.dwellingHistory != null) {
    if (!Array.isArray(s.dwellingHistory)) throw new Error('Invalid dwelling history');
    const historyIds = new Set();
    for (const row of s.dwellingHistory) {
      if (!row || typeof row.id !== 'string' || !row.id || historyIds.has(row.id) || row.siteId !== 'dwelling') throw new Error('Invalid dwelling history');
      historyIds.add(row.id);
      if (!data.CREATURES[row.type] || typeof row.claimed !== 'boolean' || !Number.isInteger(row.count) || row.count < 1 || typeof row.multiplier !== 'number' || row.multiplier <= 0) throw new Error('Invalid dwelling history');
    }
    const logical = new Set();
    for (const row of s.dwellingHistory) {
      const key = `${row.siteId}:${row.type}`;
      if (logical.has(key)) throw new Error('Invalid dwelling history');
      logical.add(key);
    }
    if (s.dwelling) {
      const row = s.dwellingHistory.find(item => item.type === s.dwelling.type && item.siteId === 'dwelling');
      if (!row || row.id !== s.dwelling.id || row.count !== s.dwelling.count || row.multiplier !== s.dwelling.multiplier || row.claimed !== s.dwelling.claimed) throw new Error('Invalid dwelling history');
    }
  }
  if (s.practice != null) {
    const challenges = s.practice.challenges;
    if (!challenges || typeof challenges !== 'object' || Array.isArray(challenges)) throw new Error('Invalid practice record');
    for (const [key, row] of Object.entries(challenges)) {
      if (!key || !row || !['p', 'e', 'none', 'retreat'].includes(row.winner)) throw new Error('Invalid practice record');
    }
  }
  if (!s.settings || typeof s.settings.reducedMotion !== 'boolean' || !Number.isFinite(s.settings.music) || !Number.isFinite(s.settings.sfx) || s.settings.music < 0 || s.settings.music > 1 || s.settings.sfx < 0 || s.settings.sfx > 1) throw new Error('Invalid settings');
  if (!s.story || typeof s.story.flags !== 'object' || Array.isArray(s.story.flags) || !s.tutorial || !Number.isInteger(s.tutorial.step) || s.tutorial.step < 0 || typeof s.tutorial.skipped !== 'boolean') throw new Error('Invalid campaign progress');
  for (const [key, value] of Object.entries(s.story.flags)) {
    if (key.startsWith('cleared:') && value !== true) throw new Error('Invalid battle record');
  }
  if (!Number.isInteger(s.story.chapter) || s.story.chapter < 0 || s.story.chapter > data.STORY.length || !Array.isArray(s.story.choices) || s.story.choices.length !== s.story.chapter || typeof s.story.futureSeen !== 'boolean') throw new Error('Invalid story');
  for (let index = 0; index < s.story.chapter; index++) {
    if (!data.STORY[index].ch.some(choice => choice.flag === s.story.choices[index])) throw new Error('Invalid story choice');
  }
  if (s.story.futureSeen && (s.story.chapter < data.STORY.length || s.age < 7)) throw new Error('Invalid future conclusion');
  if (!s.story.milestones || typeof s.story.milestones !== 'object') throw new Error('Invalid milestone');
  for (const [age, claimed] of Object.entries(s.story.milestones)) {
    const index = Number(age);
    if (!Number.isInteger(index) || index < 0 || index > 7 || claimed !== true || String(index) !== age) throw new Error('Invalid milestone');
  }
  const questIds = data.QUEST_TEMPLATES.map(quest => quest.id);
  if (!s.quests || Object.keys(s.quests).length !== questIds.length || questIds.some(id => typeof s.quests[id]?.claimed !== 'boolean')) throw new Error('Invalid quests');
  if (s.story?.rival != null && !RIVALS.includes(s.story.rival)) throw new Error('Invalid rival');
  validateBattle(s.battle);
  validateDefense(s.defense);
  if (s.defense) {
    const owned = new Map(s.towers.map(tower => [tower.id, tower.fam]));
    if (s.defense.towers.length !== owned.size || s.defense.towers.some(tower => owned.get(tower.id) !== tower.fam)) throw new Error('Defense towers are not the owned set');
  }
  const ids = [hero.id, ...s.army.map(a => a.id), ...s.towers.map(t => t.id), ...s.inventory.map(i => i.id), ...equipped.map(i => i.id), ...s.buildJobs.map(j => j.id)];
  if (ids.some(id => typeof id !== 'string' || !id) || new Set(ids).size !== ids.length) throw new Error('Invalid campaign entity identity');
  return true;
}
function passEnemyTurns(battle) {
  let next = battle;
  let guard = 0;
  while (next?.status === 'ACTIVE' && guard < 64) {
    const id = activeStackId(next);
    const stack = next.stacks.find(item => item.id === id);
    if (!stack || stack.side !== 'e') break;
    next = autoStep(next);
    guard += 1;
  }
  return next;
}
function levelOf(s, type) {
  if (type === 'walls') return s.walls.level;
  return s.plots.find(p => p.type === type)?.level ?? 0;
}
function armyCapacity(s) { return 2 + levelOf(s, 'barracks'); }
function dwellingSite(state) { return adventureGeometry(state.adventureWorldId, state.seed).sites.find(site => site.id === 'dwelling'); }
function ensureDwellingHistory(s) {
  if (Array.isArray(s.dwellingHistory)) return;
  s.dwellingHistory = [];
  const seen = new Set();
  if (s.dwelling) {
    seen.add(s.dwelling.type);
    s.dwellingHistory.push({
      id: s.dwelling.id || `dwelling:dwelling:${s.dwelling.type}`,
      siteId: 'dwelling',
      type: s.dwelling.type,
      count: s.dwelling.count,
      multiplier: s.dwelling.multiplier,
      claimed: s.dwelling.claimed === true,
      migrated: true,
    });
  }
  for (const stack of s.army) {
    if (stack.kind !== 'creature' || seen.has(stack.type)) continue;
    seen.add(stack.type);
    s.dwellingHistory.push({ id: `dwelling:dwelling:${stack.type}`, siteId: 'dwelling', type: stack.type, count: stack.count, multiplier: 1, claimed: true, migrated: true });
  }
}
function atDwelling(s) {
  const site = dwellingSite(s);
  if (!site || !s.adventure || s.adventure.atTown) return false;
  return s.adventure.x === site.approach[0] && s.adventure.y === site.approach[1];
}
function atAdventureSite(s, siteId) {
  const site = adventureGeometry(s.adventureWorldId, s.seed).sites.find(row => row.id === siteId);
  return Boolean(site && s.adventure && !s.adventure.atTown
    && s.adventure.x === site.approach[0] && s.adventure.y === site.approach[1]);
}
function pay(s, payment) {
  if (Object.entries(payment).some(([k, n]) => !Number.isFinite(n) || n < 0 || s.resources[k] < n)) throw new Error('Not enough resources');
  for (const [k, n] of Object.entries(payment)) s.resources[k] -= n;
}
function gain(s, payment) { for (const [k, n] of Object.entries(payment)) s.resources[k] += n; }
function missing(owner, key) {
  // Legacy migration fills only genuinely absent properties. Present null/wrong-type stays for validation.
  return owner == null || !Object.prototype.hasOwnProperty.call(owner, key);
}
function makeAdventureCacheOffers(state) {
  const anchors = adventureGeometry(state.adventureWorldId, state.seed).anchors;
  return Object.fromEntries(resources.filter(id => Object.hasOwn(anchors, id)).map(id => {
    let hash = 2166136261;
    const source = `${state.seed}:${state.adventureWorldId}:${id}`;
    for (let index = 0; index < source.length; index += 1) hash = Math.imul(hash ^ source.charCodeAt(index), 16777619);
    const base = ({ food: 110, wood: 130, stone: 100, gold: 210 })[id] + ((hash >>> 0) % 41);
    return [id, Math.round(base * (1 + state.age * 0.3))];
  }));
}
function makeAdventureSiteOffers(cacheOffers) {
  return { ruinXp: 90, millFood: cacheOffers.food, mineGold: cacheOffers.gold };
}
export function adoptProgress(state, data) {
  // Fill recognized missing legacy fields only. A present malformed value stays for validation and must not reset history.
  if (missing(state, 'adventureWorldId')) state.adventureWorldId = DEFAULT_ADVENTURE_WORLD_ID;
  if (missing(state, 'story')) state.story = { flags: {} };
  if (!state.story || typeof state.story !== 'object' || Array.isArray(state.story)) return state;
  if (missing(state.story, 'flags')) state.story.flags = {};
  if (missing(state.story, 'chapter')) state.story.chapter = 0;
  if (missing(state.story, 'choices')) state.story.choices = [];
  if (missing(state.story, 'futureSeen')) state.story.futureSeen = false;
  if (missing(state.story, 'milestones')) state.story.milestones = {};
  if (missing(state, 'quests')) state.quests = Object.fromEntries(data.QUEST_TEMPLATES.map(quest => [quest.id, { claimed: false }]));
  else if (state.quests && typeof state.quests === 'object' && !Array.isArray(state.quests)) {
    for (const quest of data.QUEST_TEMPLATES) if (missing(state.quests, quest.id)) state.quests[quest.id] = { claimed: false };
  }
  if (state.adventure && typeof state.adventure === 'object' && !Array.isArray(state.adventure)) {
    if (missing(state.adventure, 'cacheOffers')) state.adventure.cacheOffers = makeAdventureCacheOffers(state);
    if (missing(state.adventure, 'collectedCaches')) state.adventure.collectedCaches = [];
    if (missing(state.adventure, 'siteOffers')) state.adventure.siteOffers = state.adventure.cacheOffers && typeof state.adventure.cacheOffers === 'object'
      ? makeAdventureSiteOffers(state.adventure.cacheOffers)
      : null;
    if (missing(state.adventure, 'claimedSites')) state.adventure.claimedSites = [];
    migrateAdventureGeometry(state);
  }
  ensureDwellingHistory(state);
  adoptBattle(state.battle);
  adoptDefense(state.defense);
  return state;
}
export function stackTitle(stack, data) {
  if (stack.kind === 'creature') {
    const creature = data.CREATURES[stack.type];
    if (!creature) throw new Error('Invalid creature');
    return `${creature.n}${creature.fly ? ' flyer' : ''} ×${stack.count} rank ${stack.rank}`;
  }
  const role = data.ROLES[stack.type];
  const name = role?.names?.[stack.age];
  if (!name) throw new Error('Invalid army role');
  return `${name} ×${stack.count} rank ${stack.rank}`;
}
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
  else if (step === 6 && (input.type === 'BEGIN_ENCOUNTER' || input.type === 'START_DUEL' || input.type === 'START_SKIRMISH')) s.tutorial.step = 7;
  else if (step === 7 && (input.type === 'START_SIEGE' || input.type === 'START_ENDLESS' || input.type === 'DEFENSE')) s.tutorial.step = 8;
}
export function futureConclusion(s, data) {
  const rival = s.story.rival ?? 'no named rival';
  const kept = Boolean(s.story.flags.green || s.story.flags.generous || s.story.flags.council || s.story.flags.cautious);
  const taken = Boolean(s.story.flags.ruthless || s.story.flags.conqueror || s.story.flags.crown || s.story.flags.industry);
  const stance = kept ? 'Stewardship kept the fields and the old ground.' : taken ? 'The saved banner held the valley and its new tools.' : 'The valley remains, marked by the choices that were saved.';
  const logs = (s.story.choices || []).map((flag, index) => data?.STORY?.[index]?.ch?.find(choice => choice.flag === flag)?.log).filter(Boolean);
  const echo = logs.length ? logs.join(' ') : 'No chapter record was saved.';
  return `The Valley We Keep. ${stance} ${rival} is still part of that record. ${echo} Reading this conclusion grants nothing.`;
}
export function questReady(s, data, id) {
  const template = data.QUEST_TEMPLATES.find(quest => quest.id === id);
  if (!template || s.quests[id]?.claimed) return false;
  if (template.need === 'wins') return Object.entries(s.story.flags).filter(([key, value]) => key.startsWith('cleared:') && value === true).length >= template.v;
  if (template.need === 'age') return s.age >= template.v;
  if (template.need === 'creature') return s.army.some(stack => stack.kind === 'creature');
  if (template.need === 'rank') return s.army.some(stack => stack.rank >= template.v);
  if (template.need === 'gear') return GEAR_SLOTS.every(slot => s.hero.equip[slot]);
  if (template.need === 'best') return Math.max(0, ...Object.entries(s.story.flags).filter(([key]) => key.startsWith('endless:')).map(([, value]) => value)) >= template.v;
  return false;
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

// Internal defense simulation. It does not purchase, grant, or append a dedupe record.
export function advanceActiveDefense(state, dt) {
  if (!state?.defense || state.defense.status !== 'ACTIVE' || state.defense.paused) return state;
  const next = structuredClone(state);
  next.defense = advanceDefense(next.defense, dt, { paused: false, speed: next.defense.speed });
  return next;
}
export function formatResume(report) {
  if (!report || (report.creditedMs < 1000 && report.completed.length === 0)) return '';
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
    if (battle.practice === 'challenge') {
      if (!s.practice) s.practice = { challenges: {} };
      s.practice.challenges[battle.id] = {
        winner: battle.outcome?.winner ?? 'none',
        seed: battle.challenge?.seed ?? null,
        label: battle.challenge?.label ?? null,
      };
    }
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
    grantHeroXp(s, data, Math.round(110 * (battle.difficulty || 1)), levelOf(s, 'hall'));
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
function grantDefenseExperience(s, session) {
  for (const runtime of session.towers) {
    const tower = s.towers.find(item => item.id === runtime.id);
    if (tower) addRankXp(tower, Math.round(runtime.xp || 0));
  }
  if (session.armyDeployed && session.army?.stackId) {
    const stack = s.army.find(item => item.id === session.army.stackId);
    if (stack && stack.count > 0) addRankXp(stack, Math.round(session.army.xp || 0));
  }
}
function settleDefense(s, data) {
  const session = s.defense;
  if (!session || session.status !== 'RESOLVED' || !session.pendingSettlement) throw new Error('No pending defense result');
  if (session.armyDeployed && session.army) {
    const stack = s.army.find(item => item.id === session.army.stackId);
    if (stack && session.army.maxHp > 0) {
      const survivors = session.army.unitHp > 0
        ? (session.army.hp <= 0 ? 0 : Math.min(stack.count, Math.ceil(Math.max(0, session.army.hp) / session.army.unitHp)))
        : Math.max(0, Math.floor(stack.count * (Math.max(0, session.army.hp) / session.army.maxHp) + 1e-9));
      stack.count = survivors;
      if (stack.count === 0) s.army = s.army.filter(item => item.id !== stack.id);
    }
  }
  // Session XP is fractional. One rounded grant per owned id. A wrecked tower keeps its rank.
  grantDefenseExperience(s, session);
  if (session.practice === 'endless') {
    s.story.flags[`endless:${session.id}`] = session.clearedWaves;
    s.defense = null;
    return;
  }
  if (session.winner === 'p') {
    const difficulty = session.difficulty || 1;
    s.resources.gold += Math.round(150 * difficulty);
    s.resources.food += Math.round(100 * difficulty);
    grantHeroXp(s, data, Math.round(90 * difficulty), levelOf(s, 'hall'));
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
  ensureDwellingHistory(s);
  const payload = input.payload ?? {};
  const battlePending = s.battle && (s.battle.status === 'PENDING' || s.battle.status === 'ACTIVE' || s.battle.pendingSettlement);
  const defensePending = s.defense && (s.defense.status === 'ACTIVE' || s.defense.pendingSettlement);
  const localPreferences = ['SETTINGS', 'TUTORIAL_SKIP', 'TUTORIAL_REVIEW'].includes(input.type);
  if (battlePending && !localPreferences && !['BATTLE', 'SETTLE_BATTLE', 'DEPLOY_BATTLE_STACK', 'START_DEPLOYED_BATTLE', 'CANCEL_BATTLE_SETUP'].includes(input.type)) throw new Error('Battle result is pending');
  if (defensePending && !localPreferences && !['DEFENSE', 'SETTLE_DEFENSE', 'EARLY_CALL', 'DEPLOY_DEFENSE', 'DEPLOY_ARMY', 'DEFENSE_CAST'].includes(input.type)) throw new Error('Defense result is pending');
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
  } else if (input.type === 'STORY_CHOICE') {
    // Chapter N opens at age N and pays once. Later ages do not replay an earlier reward.
    const chapter = data.STORY[s.story.chapter];
    if (!chapter || s.age < s.story.chapter) throw new Error('Chapter is not open in this age');
    const choice = chapter?.ch?.[payload.index];
    if (!choice) throw new Error('Invalid choice');
    gain(s, choice.fx || {});
    s.story.flags[choice.flag] = true;
    s.story.choices.push(choice.flag);
    s.story.chapter += 1;
  } else if (input.type === 'ACK_FUTURE') {
    if (s.age < 7 || s.story.chapter < data.STORY.length) throw new Error('Future conclusion is not open');
    if (s.story.futureSeen) throw new Error('Future conclusion already kept');
    s.story.futureSeen = true;
  } else if (input.type === 'CLAIM_QUEST') {
    const template = data.QUEST_TEMPLATES.find(quest => quest.id === payload.id);
    if (!template) throw new Error('Invalid quest');
    if (s.quests[template.id].claimed) throw new Error('Quest already claimed');
    if (!questReady(s, data, template.id)) throw new Error('Quest is not complete');
    gain(s, template.rw || {});
    s.quests[template.id].claimed = true;
  } else if (input.type === 'CLAIM_MILESTONE') {
    const age = payload.age;
    if (!Number.isInteger(age) || age < 0 || age > 7) throw new Error('Invalid milestone');
    if (s.age < age) throw new Error('Milestone is not reached');
    if (s.story.milestones[age]) throw new Error('Milestone already claimed');
    s.story.milestones[age] = true;
  } else if (input.type === 'ENTER_ADVENTURE') {
    if (s.battle) throw new Error('Journey already open');
    if (s.adventure) {
      if (!s.adventure.atTown) throw new Error('Journey already open');
      s.adventure.atTown = false;
    } else {
      const geometry = adventureGeometry(s.adventureWorldId, s.seed);
      const heroAnchor = geometry.anchors.hero;
      const x = Math.floor(heroAnchor[0]);
      const y = Math.floor(heroAnchor[1]);
      const cacheOffers = makeAdventureCacheOffers(s);
      s.adventure = { geometryVersion: ADVENTURE_GEOMETRY_VERSION, x, y, moves: dailyMoves(s, data), visited: [`${x},${y}`], resolvedGuards: [], cacheOffers, collectedCaches: [], siteOffers: makeAdventureSiteOffers(cacheOffers), claimedSites: [], pendingEncounter: null, atTown: false };
    }
  } else if (input.type === 'MOVE') {
    if (!s.adventure || s.adventure.atTown) throw new Error('Not traveling');
    if (s.adventure.pendingEncounter && String(s.adventure.pendingEncounter.status).startsWith('UNRESOLVED')) throw new Error('Unresolved encounter');
    const map = adventureMapForWorld(s.adventureWorldId, s.seed);
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
  } else if (input.type === 'CLAIM_ADVENTURE_CACHE') {
    if (!s.adventure || s.adventure.atTown) throw new Error('Not traveling');
    if (s.adventure.pendingEncounter && String(s.adventure.pendingEncounter.status).startsWith('UNRESOLVED')) throw new Error('Clear the guard first');
    const id = payload.id;
    const anchor = adventureGeometry(s.adventureWorldId, s.seed).anchors[id];
    if (!resources.includes(id) || !anchor) throw new Error('Invalid cache');
    const cell = `${Math.floor(anchor[0])},${Math.floor(anchor[1])}`;
    if (`${s.adventure.x},${s.adventure.y}` !== cell) throw new Error('Reach the cache first');
    if (s.adventure.collectedCaches.includes(id)) throw new Error('Cache already collected');
    gain(s, { [id]: s.adventure.cacheOffers[id] });
    s.adventure.collectedCaches.push(id);
  } else if (input.type === 'CLAIM_ADVENTURE_SITE') {
    if (!s.adventure || s.adventure.atTown) throw new Error('Not traveling');
    if (s.adventure.pendingEncounter && String(s.adventure.pendingEncounter.status).startsWith('UNRESOLVED')) throw new Error('Clear the guard first');
    const id = payload.id;
    if (!['ruin', 'mill', 'mine'].includes(id) || !atAdventureSite(s, id)) throw new Error('Reach a claimable Adventure site first');
    if (s.adventure.claimedSites.includes(id)) throw new Error('Adventure site already claimed');
    if (id === 'ruin') grantHeroXp(s, data, s.adventure.siteOffers.ruinXp, levelOf(s, 'hall'));
    else if (id === 'mill') gain(s, { food: s.adventure.siteOffers.millFood });
    else gain(s, { gold: s.adventure.siteOffers.mineGold });
    s.adventure.claimedSites.push(id);
  } else if (input.type === 'OFFER_ADVENTURE_SHRINE_SKILL') {
    if (!s.adventure || s.adventure.atTown) throw new Error('Not traveling');
    if (s.adventure.pendingEncounter && String(s.adventure.pendingEncounter.status).startsWith('UNRESOLVED')) throw new Error('Clear the guard first');
    if (!atAdventureSite(s, 'shrine')) throw new Error('Reach the skill shrine first');
    if (s.adventure.claimedSites.includes('shrine')) throw new Error('Skill shrine already visited');
    if (s.hero.offers.some(offer => !offer.chosen && !offer.declined)) throw new Error('Resolve the pending skill offer first');
    const offer = createSkillOffer(s);
    if (offer) s.hero.offers.push({ ...offer, source: 'adventure-shrine', siteId: 'shrine' });
    else s.adventure.claimedSites.push('shrine');
  } else if (input.type === 'REST') {
    if (!s.adventure || s.adventure.atTown || s.adventure.moves < 1) throw new Error('Not enough movement');
    s.adventure.moves -= 1;
    s.hero.mana = manaMax(s, data);
  } else if (input.type === 'RETURN_TOWN') {
    const townApproach = adventureGeometry(s.adventureWorldId, s.seed).sites.find(site => site.id === 'town')?.approach;
    if (!s.adventure || s.adventure.atTown || !townApproach || s.adventure.x !== townApproach[0] || s.adventure.y !== townApproach[1]) throw new Error('Not at the town approach');
    if (s.adventure.pendingEncounter && String(s.adventure.pendingEncounter.status).startsWith('UNRESOLVED')) throw new Error('Unresolved encounter');
    s.adventure.atTown = true;
  } else if (input.type === 'BEGIN_ENCOUNTER') {
    if (s.battle) throw new Error('Battle already open');
    s.battle = createEncounterBattle(s, data);
    s.battle.id = `battle-${s.adventure.pendingEncounter.id}-r${s.revision}`;
    s.battle = passEnemyTurns(s.battle);
  } else if (input.type === 'BATTLE') {
    if (!s.battle || s.battle.status !== 'ACTIVE') throw new Error('No active battle');
    const action = payload.action;
    if (action === 'opponent') {
      const id = activeStackId(s.battle);
      const stack = s.battle.stacks.find(item => item.id === id);
      if (!stack || stack.side === 'p') throw new Error('Player turn');
    } else if (action === 'move') s.battle = battleMove(s.battle, payload.stackId, payload.to);
    else if (action === 'strike') s.battle = strike(s.battle, payload.stackId, payload.targetId, { forceMelee: payload.forceMelee === true, approach: payload.approach });
    else if (action === 'defend') s.battle = defend(s.battle, payload.stackId);
    else if (action === 'wait') s.battle = battleWait(s.battle, payload.stackId);
    else if (action === 'skip-bonus') s.battle = skipBonus(s.battle, payload.stackId);
    else if (action === 'spell') {
      const spell = data.SPELLS[payload.spell];
      if (!spell) throw new Error('Unsupported spell');
      s.battle = castSpell(s.battle, { ...spell, id: payload.spell }, payload.targetId, s.battle.hero?.pow ?? 0);
    } else if (action === 'auto') s.battle = playOut(s.battle, { spells: Object.entries(data.SPELLS).map(([id, spell]) => ({ ...spell, id })) });
    else if (action === 'retreat') {
      if (payload.confirm !== true) throw new Error('Retreat must be confirmed');
      s.battle = retreat(s.battle);
    }     else throw new Error('Unsupported battle command');
    if (action !== 'retreat' && action !== 'auto') s.battle = passEnemyTurns(s.battle);
  } else if (input.type === 'SETTLE_BATTLE') applyBattleResult(s, data);
  else if (input.type === 'START_SKIRMISH') {
    if (s.battle || s.defense) throw new Error('Battle already open');
    if (s.adventure?.pendingEncounter && String(s.adventure.pendingEncounter.status).startsWith('UNRESOLVED')) throw new Error('Unresolved encounter');
    s.battle = createSkirmishBattle(s, data, s.tutorial.step);
  } else if (input.type === 'DEPLOY_BATTLE_STACK') {
    if (!s.battle || s.battle.status !== 'PENDING' || !s.battle.deployment) throw new Error('No deployment setup');
    s.battle = placeDeployment(s.battle, payload.stackId, payload.cell);
  } else if (input.type === 'START_DEPLOYED_BATTLE') {
    if (!s.battle || s.battle.status !== 'PENDING' || !s.battle.deployment) throw new Error('No deployment setup');
    s.battle = passEnemyTurns(startDeployedBattle(s.battle));
  } else if (input.type === 'CANCEL_BATTLE_SETUP') {
    if (!s.battle || s.battle.status !== 'PENDING' || !s.battle.deployment) throw new Error('No deployment setup');
    const previousStep = s.battle.deployment.previousTutorialStep;
    s.battle = null;
    if (!s.tutorial.skipped && Number.isInteger(previousStep) && s.tutorial.step === previousStep + 1) s.tutorial.step = previousStep;
  } else if (input.type === 'START_DUEL') {
    if (s.battle || s.defense) throw new Error('Battle already open');
    s.battle = passEnemyTurns(createDuelBattle(s, data));
  } else if (input.type === 'START_CHALLENGE') {
    if (s.battle || s.defense) throw new Error('Battle already open');
    if (payload.schema != null && payload.schema !== 1) throw new Error('Unsupported challenge schema.');
    if (payload.scenarioId != null && payload.scenarioId !== 'duel-v1') throw new Error('Unsupported challenge scenario.');
    const label = payload.label ?? payload.code;
    s.battle = passEnemyTurns(createChallengeBattle(payload.seed, label));
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
    s.defense = deployHero(s.defense, heroStats(s, data).atk * 3, payload.siteId ?? null);
    if (s.resources.gold !== gold) throw new Error('Deployment fee');
  } else if (input.type === 'DEPLOY_ARMY') {
    if (!s.defense || s.defense.status !== 'ACTIVE') throw new Error('No active defense');
    const stack = s.army.find(item => item.id === payload.stackId);
    if (!stack) throw new Error('Unknown army stack');
    const gold = s.resources.gold;
    s.defense = deployArmy(s.defense, stack, payload.siteId ?? null);
    if (s.resources.gold !== gold) throw new Error('Deployment fee');
  } else if (input.type === 'DEFENSE_CAST') {
    if (!s.defense || s.defense.status !== 'ACTIVE' || !s.defense.heroDeployed) throw new Error('No deployed hero');
    if (s.hero.mana < 40) throw new Error('Not enough mana');
    const stats = heroStats(s, data);
    const next = castDefense(s.defense, stats.pow * 4 + s.hero.level * 6, payload);
    s.hero.mana -= 40;
    s.defense = next;
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
    if (offer.source === 'adventure-shrine') s.adventure.claimedSites.push('shrine');
  } else if (input.type === 'DECLINE_SKILL') {
    const offer = s.hero.offers.find(item => !item.chosen && !item.declined);
    if (!offer) throw new Error('Invalid skill offer');
    offer.declined = true;
    if (offer.source === 'adventure-shrine') s.adventure.claimedSites.push('shrine');
  } else if (input.type === 'OFFER_DWELLING') {
    // One offer per creature type at this site. Cancel keeps the open terms and does not reroll.
    if (!atDwelling(s)) throw new Error('Not at the dwelling');
    if (s.dwelling && !s.dwelling.claimed) {
      if (payload.type && payload.type !== s.dwelling.type) throw new Error('Offer already open');
    } else {
      if (s.dwellingHistory.some(row => row.type === payload.type)) throw new Error('Dwelling type already offered');
      const terms = dwellingTerms(s.story.flags || {});
      if (!dwellingPool(data, s.age).includes(payload.type)) throw new Error('Invalid dwelling tier');
      const offer = { id: `dwelling:dwelling:${payload.type}`, siteId: 'dwelling', type: payload.type, count: terms.count, multiplier: terms.multiplier, claimed: false };
      s.dwelling = offer;
      s.dwellingHistory.push({ ...offer });
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
    const row = s.dwellingHistory.find(item => item.type === s.dwelling.type);
    if (row) {
      row.claimed = true;
      row.payment = payment;
      row.transactionId = input.id;
    }
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
