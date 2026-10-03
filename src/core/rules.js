// Documented scalar rules. Damage, waves, encounters, loot, hero experience and End Day
// live in mechanics.js. Positive morale does not grant an extra turn while that owner
// decision is pending.

export const SKILL_IDS = ['offense', 'archery', 'armorer', 'wisdom', 'leadership', 'luck', 'tactics', 'logistics', 'firstaid'];
export const GEAR_SLOTS = ['helm', 'weapon', 'offhand', 'armor', 'boots', 'accessory'];
export const QUALITY = [1, 1.8, 2.8, 4];
export const OFFHAND_ARTIFACTS = ['aegis', 'codex', 'orb', 'banner'];
export const RIVALS = [
  'Varek Iron-Eye', 'Malakor the Flayed', 'Thalric Ash-Bane',
  'Bran the Relentless', 'Karn Blood-Tide', 'Soren the Unforgiving'
];

const PRIMARY = { weapon: 'atk', offhand: 'def', armor: 'def', helm: 'kno', boots: 'move', accessory: 'pow' };

export function agePrice(age) {
  if (!Number.isInteger(age) || age < 0 || age > 6) throw new Error('Invalid age gate');
  const m = 2.15 ** (age + 1);
  return { food: Math.round(300 * m), wood: Math.round(280 * m), stone: Math.round(220 * m), gold: Math.round(180 * m) };
}

export function scaledCost(base, age) {
  if (!base || !Number.isInteger(age) || age < 0 || age > 7) throw new Error('Invalid purchase');
  return Object.fromEntries(Object.entries(base).map(([k, n]) => [k, Math.round(n * (1 + 0.75 * age))]));
}

export function recruitCost(data, role, age) {
  const base = data.ROLES[role]?.cost;
  if (!base) throw new Error('Invalid role');
  const per = scaledCost(base, age);
  return Object.fromEntries(Object.entries(per).map(([k, n]) => [k, n * 5]));
}

export function towerPurchaseCost(data, family, age) {
  const base = data.TOWERS[family]?.cost;
  if (!base) throw new Error('Invalid tower');
  return scaledCost(base, age);
}

export function forgeOffer(age, armoryLevel, requestedQuality = null) {
  if (!Number.isInteger(armoryLevel) || armoryLevel < 1) throw new Error('Armory required');
  if (!Number.isInteger(age) || age < 0 || age > 7) throw new Error('Invalid age');
  const cap = Math.min(3, Math.floor((armoryLevel - 1) / 2));
  const quality = requestedQuality == null ? cap : requestedQuality;
  if (!Number.isInteger(quality) || quality < 0 || quality > cap) throw new Error('Quality is above the Armory');
  const factor = (age + 1) * (quality + 1);
  return { quality, cap, cost: { wood: 80 * factor, stone: 60 * factor, gold: 70 * factor } };
}

export function gearBonus(item) {
  if (!item || item.kind !== 'gear') return {};
  const base = item.slot === 'weapon' || item.slot === 'armor' ? 2 : 1;
  const amount = Math.max(1, Math.round((base + 0.9 * item.age) * QUALITY[item.quality] / 1.6));
  return { [PRIMARY[item.slot]]: amount };
}

export function heroStats(state, data) {
  const hero = state.hero;
  const start = data.CLASSES[hero.class].start;
  const stats = { atk: start.atk, def: start.def, pow: start.pow, kno: start.kno, move: 0, morale: 0, luck: 0 };
  for (const key of ['atk', 'def', 'pow', 'kno']) {
    stats[key] += hero.growth?.[key] || 0;
    stats[key] += hero.bonus?.[key] || 0;
  }
  const items = [...Object.values(hero.equip).filter(Boolean)];
  for (const item of items) {
    if (item.kind === 'gear') {
      for (const [k, n] of Object.entries(gearBonus(item))) stats[k] += n;
    } else if (item.kind === 'artifact') {
      for (const [k, n] of Object.entries(data.ARTIFACTS[item.artifactId].b)) {
        if (k in stats) stats[k] += n;
      }
    }
  }
  stats.morale += hero.skills.leadership;
  stats.luck += hero.skills.luck;
  return stats;
}

export function manaMax(state, data) {
  return 10 * heroStats(state, data).kno;
}

export function dailyMoves(state, data) {
  return 5 + (state.hero.skills.logistics || 0) + heroStats(state, data).move;
}

export function gateHp(state) {
  return 400 + 180 * state.walls.level + 60 * state.age;
}

export function spellEffect(id, power) {
  if (!Number.isFinite(power)) throw new Error('Invalid power');
  if (id === 'arrow' || id === 'cure') return 10 + 10 * power;
  if (id === 'bolt') return 10 + 25 * power;
  if (id === 'fireball') return 10 + 20 * power;
  if (id === 'resurrect') return 50 * power;
  return null;
}

export function marketQuote(side, resource) {
  if (!['food', 'wood', 'stone'].includes(resource)) throw new Error('Invalid market good');
  if (side === 'buy') return { spend: { gold: 120 }, gain: { [resource]: 100 } };
  if (side === 'sell') return { spend: { [resource]: 100 }, gain: { gold: 60 } };
  throw new Error('Invalid market side');
}

export function validItem(item, data) {
  if (!item || typeof item.id !== 'string' || !item.id) return false;
  if (!GEAR_SLOTS.includes(item.slot)) return false;
  if (item.kind === 'gear') return Number.isInteger(item.age) && item.age >= 0 && item.age <= 7 && Number.isInteger(item.quality) && item.quality >= 0 && item.quality <= 3 && PRIMARY[item.slot];
  if (item.kind === 'artifact') {
    if (!data.ARTIFACTS[item.artifactId]) return false;
    if (item.slot === 'accessory') return true;
    return item.slot === 'offhand' && OFFHAND_ARTIFACTS.includes(item.artifactId);
  }
  return false;
}
