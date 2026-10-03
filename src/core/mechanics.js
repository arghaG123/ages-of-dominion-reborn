// Independently authored mechanics from the source-equation addendum.
// Numeric behavior is transcribed. Old modules are not imported.
import { draw, drawInt } from './rng.js';
import { GEAR_SLOTS, SKILL_IDS, manaMax } from './rules.js';

export const AGE_POWER = [0.91, 0.99, 1.17, 1.06, 0.99, 0.74, 0.68, 0.72];
export const RANK_XP = [0, 60, 180, 420, 900];
export const PRIMARY_ORDER = ['atk', 'def', 'pow', 'kno'];
export const LOOT_GEAR_SLOTS = [...GEAR_SLOTS];
export const MORALE_EFFECT = 'PENDING_OWNER_DECISION';

const WEATHER_ORDER = ['clear', 'rain', 'fog', 'storm', 'blizz', 'sand', 'heat'];

function requireRange(name, value, min, max, integer = true) {
  const ok = integer ? Number.isInteger(value) : Number.isFinite(value);
  if (!ok || value < min || value > max) throw new Error(`Invalid ${name}`);
}

export function rankForXp(xp) {
  if (!Number.isFinite(xp) || xp < 0) throw new Error('Invalid rank experience');
  let rank = 0;
  for (let i = 1; i < RANK_XP.length; i++) if (xp >= RANK_XP[i]) rank = i;
  return rank;
}

export function unitStats(stack, data) {
  requireRange('age', stack?.age, 0, 7);
  requireRange('rank', stack?.rank, 0, 4);
  let derived;
  if (stack.kind === 'role') {
    const role = data.ROLES[stack.type];
    if (!role) throw new Error('Invalid role');
    const scale = 1 + 0.55 * stack.age;
    derived = {
      name: role.names[stack.age],
      atk: role.atk + 2 * stack.age,
      def: role.def + 2 * stack.age,
      hp: Math.round(role.hp * scale),
      dmin: Math.round(role.dmin * scale),
      dmax: Math.round(role.dmax * scale),
      spd: role.spd + (stack.age > 3 ? 1 : 0),
      rng: role.rng,
      shots: role.shots,
      block: role.block,
      fly: 0,
    };
  } else if (stack.kind === 'creature') {
    const creature = data.CREATURES[stack.type];
    if (!creature) throw new Error('Invalid creature');
    const scale = 1 + 0.3 * stack.age;
    derived = {
      name: (stack.age > 2 ? 'Elder ' : '') + creature.n,
      atk: creature.atk + stack.age,
      def: creature.def + stack.age,
      hp: Math.round(creature.hp * scale),
      dmin: Math.round(creature.dmin * scale),
      dmax: Math.round(creature.dmax * scale),
      spd: creature.spd,
      rng: creature.rng,
      shots: creature.shots || 0,
      block: creature.block,
      fly: creature.fly || 0,
    };
  } else throw new Error('Invalid stack kind');
  const rank = stack.rank;
  derived.atk += rank;
  derived.def += rank;
  derived.hp = Math.round(derived.hp * (1 + 0.08 * rank));
  derived.dmin = Math.round(derived.dmin * (1 + 0.08 * rank));
  derived.dmax = Math.round(derived.dmax * (1 + 0.08 * rank));
  if (rank >= 2) derived.spd += 1;
  if (rank >= 4) derived.spd += 1;
  if (derived.dmin > derived.dmax) throw new Error('Invalid damage bounds');
  return derived;
}

export function towerStats(tower, data) {
  requireRange('tier', tower?.tier, 0, 7);
  requireRange('rank', tower?.rank, 0, 4);
  const table = data.TOWERS[tower?.fam];
  if (!table || !table.names[tower.tier]) throw new Error('Invalid tower');
  const scale = 1 + 0.5 * tower.tier;
  const rank = tower.rank;
  return {
    name: table.names[tower.tier],
    dmg: table.dmg * scale * (1 + 0.12 * rank),
    rate: table.rate,
    rng: table.rng + (rank >= 3 ? 0.3 : 0),
    hp: Math.round((table.hp + 80 * tower.tier) * (1 + 0.15 * rank)),
    splash: table.splash || 0,
    slow: table.slow || 0,
    aura: table.aura || 0,
  };
}

function skill(hero, id) {
  const level = hero?.skills?.[id] ?? 0;
  if (!Number.isInteger(level) || level < 0 || level > 3) throw new Error('Invalid skill level');
  return level;
}

export function calcDamage(attacker, defender, options = {}) {
  if (!attacker || !defender) throw new Error('Invalid combatant');
  requireRange('count', attacker.count, 1, 100000);
  if (!Number.isInteger(attacker.dmin) || !Number.isInteger(attacker.dmax) || attacker.dmin > attacker.dmax || attacker.dmin < 0) throw new Error('Invalid damage bounds');
  const rng = options.rng ?? Math.random;
  const hero = options.hero ?? null;
  const mods = options.mods ?? {};
  const ranged = Boolean(options.ranged);
  const boss = Boolean(options.boss);
  const playerAttacker = attacker.side === 'p';
  const attack = attacker.atk + (playerAttacker ? (hero?.atk || 0) : (boss || attacker.boss ? 2 : 0));
  const defense = defender.def + (defender.side === 'p' ? (hero?.def || 0) : 0) + (defender.defending ? 3 : 0);
  let base = 0;
  const rolled = Math.min(attacker.count, 60);
  for (let i = 0; i < rolled; i++) {
    base += attacker.bless ? attacker.dmax : attacker.dmin + Math.floor(rng() * (attacker.dmax - attacker.dmin + 1));
  }
  if (attacker.count > 60) base *= attacker.count / 60;
  const delta = attack - defense;
  let multiplier = delta > 0 ? 1 + Math.min(3, 0.05 * delta) : 1 - Math.min(0.7, 0.025 * -delta);
  if (playerAttacker) {
    if (!ranged) multiplier *= 1 + [0, 0.1, 0.2, 0.3][skill(hero, 'offense')];
    else multiplier *= 1 + [0, 0.1, 0.25, 0.5][skill(hero, 'archery')] + (hero?.shootBon || 0);
  }
  if (defender.side === 'p') multiplier *= 1 - [0, 0.05, 0.1, 0.15][skill(hero, 'armorer')];
  if (ranged) {
    if (options.adjacentEnemy || attacker.adjacentEnemy) multiplier *= 0.5;
    multiplier *= 1 - (mods.shootPen || 0) + (mods.shootBon || 0);
  }
  if (defender.defending) multiplier *= 0.85;
  let lucky = false;
  const luck = hero?.luck || 0;
  if (playerAttacker && luck > 0 && rng() < luck * 0.042) {
    multiplier *= 2;
    lucky = true;
  }
  return { dmg: Math.max(1, Math.round(base * multiplier)), lucky };
}

export function applyDamage(target, damage) {
  if (!Number.isFinite(damage) || damage < 0) throw new Error('Invalid damage');
  requireRange('count', target.count, 0, 100000);
  if (target.count === 0) return { count: 0, top: 0, dead: true, killed: 0 };
  if (!Number.isFinite(target.uhp) || target.uhp <= 0) throw new Error('Invalid unit HP');
  if (target.top <= 0 || target.top > target.uhp) throw new Error('Invalid top HP');
  const pool = (target.count - 1) * target.uhp + target.top - damage;
  if (pool <= 0) return { count: 0, top: 0, dead: true, killed: target.count };
  const count = Math.ceil(pool / target.uhp);
  return { count, top: pool - (count - 1) * target.uhp, dead: false, killed: target.count - count };
}

export function previewStrike(attacker, defender, options = {}) {
  const hero = { ...(options.hero || {}), luck: 0 };
  const low = calcDamage(attacker, defender, { ...options, hero, rng: () => 0 });
  const high = calcDamage(attacker, defender, { ...options, hero, rng: () => 0.999999 });
  const dmin = Math.min(low.dmg, high.dmg);
  const dmax = Math.max(low.dmg, high.dmg);
  const slain = (amount) => applyDamage({ count: defender.count, uhp: defender.uhp ?? defender.hp, top: defender.top ?? defender.uhp ?? defender.hp }, amount).killed;
  return { dmin, dmax, slainMin: slain(dmin), slainMax: slain(dmax) };
}

export function previewRetaliation(attacker, defender, options = {}) {
  const hit = previewStrike(attacker, defender, options);
  if (options.ranged || defender.retaliated) return { hit, retalMin: null, retalMax: null };
  const project = (damage) => {
    const next = applyDamage({ count: defender.count, uhp: defender.uhp, top: defender.top ?? defender.uhp }, damage);
    if (next.dead) return null;
    const answer = previewStrike(
      { ...defender, side: defender.side, count: next.count, dmin: defender.dmin, dmax: defender.dmax, atk: defender.atk, def: defender.def },
      { ...attacker, side: attacker.side, count: attacker.count, uhp: attacker.uhp, top: attacker.top ?? attacker.uhp },
      { ...options, ranged: false, hero: options.hero, adjacentEnemy: false },
    );
    return answer;
  };
  return { hit, retalMin: project(hit.dmax), retalMax: project(hit.dmin) };
}

export function endDay(state, data) {
  if (!Number.isInteger(state.day) || state.day < 1) throw new Error('Invalid day');
  state.day += 1;
  const index = drawInt(state, WEATHER_ORDER.length);
  state.weather = WEATHER_ORDER[index];
  if (!data.WEATHER[state.weather]) throw new Error('Invalid weather');
  const cap = manaMax(state, data);
  state.hero.mana = Math.min(cap, state.hero.mana + cap * 0.5);
  return state.weather;
}

function choosePrimary(state, data) {
  const weights = data.CLASSES[state.hero.class].g;
  const roll = draw(state);
  let acc = 0;
  let chosen = PRIMARY_ORDER[0];
  for (const key of PRIMARY_ORDER) {
    acc += weights[key];
    if (roll <= acc) { chosen = key; break; }
  }
  return chosen;
}

function offerSkills(state) {
  const pool = SKILL_IDS.filter(id => state.hero.skills[id] < 3);
  const choices = [];
  while (choices.length < 2 && pool.length) choices.push(pool.splice(drawInt(state, pool.length), 1)[0]);
  if (!choices.length) return null;
  return { level: state.hero.level, choices, declined: false };
}

export function grantHeroXp(state, data, rewardXp, hallLevel) {
  requireRange('reward', rewardXp, 0, 1000000, false);
  requireRange('hall', hallLevel, 0, 20);
  const credit = Math.round(rewardXp * (1 + 0.15 * hallLevel));
  state.hero.xp += credit;
  while (state.hero.xp >= state.hero.level * 140) {
    state.hero.xp -= state.hero.level * 140;
    state.hero.level += 1;
    const primary = choosePrimary(state, data);
    state.hero.growth[primary] += 1;
    state.hero.points += 1;
    state.hero.mana = manaMax(state, data);
    if (state.hero.level % 3 === 0) {
      const offer = offerSkills(state);
      if (offer) state.hero.offers.push(offer);
    }
  }
  return credit;
}

export function addRankXp(stack, amount) {
  if (!Number.isFinite(amount) || amount < 0) throw new Error('Invalid rank experience');
  stack.xp += amount;
  stack.rank = rankForXp(stack.xp);
  return stack.rank;
}

export function rollLoot(state, data, difficulty) {
  requireRange('difficulty', difficulty, 0, 100, false);
  const drops = [];
  const gearChance = 0.35 + 0.06 * difficulty;
  if (draw(state) < gearChance) {
    const first = draw(state);
    const quality = first < 0.12 ? 2 : (draw(state) < 0.4 ? 1 : 0);
    const slot = LOOT_GEAR_SLOTS[drawInt(state, LOOT_GEAR_SLOTS.length)];
    drops.push({ id: `loot-${state.rngState}`, kind: 'gear', slot, age: state.age, quality });
  }
  const artifactChance = 0.07 + 0.03 * difficulty;
  if (draw(state) < artifactChance) {
    const ids = Object.keys(data.ARTIFACTS);
    drops.push({ id: `loot-${state.rngState}`, kind: 'artifact', artifactId: ids[drawInt(state, ids.length)], slot: 'accessory' });
  }
  return drops;
}

export function creaturePool(data, age) {
  requireRange('age', age, 0, 7);
  const cap = Math.min(4, Math.max(1, Math.ceil((age + 2) / 2)));
  let floor = age >= 6 ? 3 : age >= 4 ? 2 : 1;
  floor = Math.min(floor, cap);
  return Object.keys(data.CREATURES).filter(id => {
    const tier = data.CREATURES[id].t;
    return tier >= floor && tier <= cap;
  });
}

export function makePack(state, data, age, { boss = false, row = 2 } = {}) {
  requireRange('age', age, 0, 7);
  requireRange('row', row, 0, 20);
  const pool = creaturePool(data, age);
  if (!pool.length) throw new Error('Empty creature pool');
  const power = (1 + 0.22 * row) * (boss ? 1.8 : 1) * AGE_POWER[age];
  const stacks = [];
  const count = boss ? 3 + drawInt(state, 2) : 2 + drawInt(state, 2);
  let carry = 0;
  for (let i = 0; i < count; i++) {
    const type = pool[drawInt(state, pool.length)];
    const tier = data.CREATURES[type].t;
    const exact = (6 + 2 * row) * power / (1 + 0.8 * tier) + carry;
    const heads = Math.max(2, Math.round(exact));
    carry = exact - heads;
    stacks.push({ kind: 'creature', type, age, rank: 0, count: heads });
  }
  return { stacks, boss, power, row, carry };
}

export function hostPower(army, heroAttack, heroDefense) {
  let total = 0;
  for (const stack of army) {
    if (!stack || !stack.count || stack.count <= 0) continue;
    const heavy = stack.type === 'heavy' ? 1.3 : 1;
    total += stack.count * heavy * (1 + 0.44 * stack.age) * (1 + 0.18 * stack.rank);
  }
  return Math.max(0, total / 38 * (1 + 0.04 * ((heroAttack || 0) + (heroDefense || 0))));
}

export function encounterVerdict(enemyPower, host) {
  if (host <= 0.001) return 'Deadly';
  const ratio = enemyPower / host;
  if (ratio <= 0.75) return 'Easy';
  if (ratio <= 1.25) return 'Even';
  if (ratio <= 1.75) return 'Risky';
  return 'Deadly';
}

export function dwellingTerms(flags = {}) {
  let count = 5;
  let multiplier = 1;
  if (flags.generous && flags.ruthless) { count = 6; multiplier = 0.85; }
  else if (flags.generous) { count = 7; multiplier = 0.8; }
  else if (flags.ruthless) { count = 5; multiplier = 0.85; }
  if (flags.creature) count += 1;
  return { count, multiplier };
}

export function dwellingCost(data, type, multiplier) {
  const base = data.CREATURES[type]?.cost;
  if (!base || !Number.isFinite(multiplier) || multiplier <= 0) throw new Error('Invalid dwelling offer');
  return Object.fromEntries(Object.entries(base).map(([key, amount]) => [key, multiplier === 1 ? Math.round(amount) : Math.max(1, Math.round(amount * multiplier))]));
}

export function dwellingPool(data, age) {
  requireRange('age', age, 0, 7);
  const cap = Math.max(1, Math.ceil((age + 1) / 2));
  return Object.keys(data.CREATURES).filter(id => data.CREATURES[id].t <= cap);
}

export function wavePlan(index, age, difficulty) {
  requireRange('wave', index, 0, 1000);
  requireRange('age', age, 0, 7);
  if (!Number.isFinite(difficulty) || difficulty <= 0) throw new Error('Invalid difficulty');
  const base = 1 + 0.5 * age;
  const counts = {
    brute: 3 + Math.floor(0.8 * index),
    runner: 2 + Math.floor(0.6 * index),
    archer: 1 + Math.floor(0.8 * index),
    sapper: index >= 2 ? 1 + Math.floor(0.4 * index) : 0,
    shaman: index >= 4 ? 1 + Math.floor(0.3 * index) : 0,
  };
  return {
    counts,
    total: Object.values(counts).reduce((sum, n) => sum + n, 0),
    hp: Math.round(26 * base * difficulty * (1 + 0.3 * index)),
    damage: 7 * base * difficulty * (1 + 0.15 * index),
    speed: 0.85 + 0.03 * index,
    gap: Math.max(0.35, 1 - 0.05 * index),
  };
}

export const ROLE_MULTIPLIER = {
  brute: { hp: 1.25, speed: 0.85, damage: 1.2 },
  runner: { hp: 0.6, speed: 1.6, damage: 0.7 },
  archer: { hp: 0.75, speed: 0.9, damage: 0.9 },
  sapper: { hp: 0.9, speed: 0.95, damage: 2.2 },
  shaman: { hp: 0.8, speed: 0.9, damage: 1.1 },
};

export function seededOrder(items, state) {
  const tagged = items.map(item => ({ item, tie: draw(state) }));
  tagged.sort((a, b) => a.tie - b.tie);
  return tagged.map(entry => entry.item);
}
