// Fixed-step defense. Pause adds no catch-up attacks. 2x multiplies the same 1/60 step.
import contract from '../data/implementation-contract.json' with { type: 'json' };
import { ROLE_MULTIPLIER, seededOrder, towerStats, wavePlan } from './mechanics.js';

export const STEP = 1 / 60;
const FRAME_CAP = 0.25;
const MAX_STEPS = 32;
const geo = contract.geometry.defense;
const lane = geo.lane;
const pads = geo.sites.map(site => {
  const [x, y, w, h] = site.rect;
  return { id: site.id, x: x + w / 2, y: y + h / 2 };
});

function clone(value) { return structuredClone(value); }
function pointAt(progress) {
  const clamped = Math.max(0, Math.min(lane.length - 1, progress));
  const index = Math.floor(clamped);
  const next = Math.min(lane.length - 1, index + 1);
  const t = clamped - index;
  return [lane[index][0] + (lane[next][0] - lane[index][0]) * t, lane[index][1] + (lane[next][1] - lane[index][1]) * t];
}
function distance(a, b) { return Math.hypot(a[0] - b[0], a[1] - b[1]); }

function schedule(age, difficulty, waves, rngState) {
  const roles = ['brute', 'runner', 'archer', 'sapper', 'shaman'];
  const queue = [];
  let cursor = 0;
  const random = { rngState };
  for (let wave = 0; wave < waves; wave++) {
    const plan = wavePlan(wave, age, difficulty);
    const bag = [];
    for (const role of roles) for (let n = 0; n < plan.counts[role]; n++) bag.push(role);
    const ordered = seededOrder(bag, random);
    ordered.forEach((role, index) => {
      const multiplier = ROLE_MULTIPLIER[role];
      queue.push({
        id: `w${wave}-${index}`, role, wave, spawned: false,
        hp: Math.round(plan.hp * multiplier.hp),
        damage: plan.damage * multiplier.damage,
        speed: plan.speed * multiplier.speed,
        spawnAt: cursor + index * plan.gap,
        progress: 0, slowUntil: 0, slowFraction: 0, leaked: false,
      });
    });
    cursor += ordered.length * plan.gap + 1.2;
  }
  return { queue, rngState: random.rngState };
}

export function createDefense(state, data, { practice, waves, difficulty = 1 }) {
  if (!['siege', 'endless'].includes(practice)) throw new Error('Invalid defense');
  const planned = schedule(state.age, difficulty, waves, state.rngState);
  const towers = state.towers.map((tower, index) => {
    const stats = towerStats(tower, data);
    const pad = pads[index % pads.length];
    return { id: tower.id, fam: tower.fam, x: pad.x, y: pad.y, cooldown: 0, dmg: stats.dmg, rate: stats.rate, rng: stats.rng, splash: stats.splash, slow: stats.slow, aura: stats.aura };
  });
  return {
    id: `${practice}-${state.day}-${state.revision}`,
    practice, status: 'ACTIVE', pendingSettlement: false, difficulty, age: state.age,
    core: 400 + 180 * (state.walls?.level || 0) + 60 * state.age,
    time: 0, accumulator: 0, speed: 1, paused: false,
    waves, clearedWaves: 0, earlyCalls: [], heroDeployed: false, extensions: 0, rngState: planned.rngState,
    towers, queue: planned.queue, enemies: [], laneLength: lane.length,
  };
}

export function validateDefense(session) {
  if (session == null) return true;
  if (!session || !['siege', 'endless'].includes(session.practice) || !['ACTIVE', 'RESOLVED'].includes(session.status)) throw new Error('Invalid defense');
  if (typeof session.pendingSettlement !== 'boolean' || !Number.isFinite(session.core)) throw new Error('Invalid defense');
  if (![1, 2].includes(session.speed) || typeof session.paused !== 'boolean') throw new Error('Invalid defense');
  if (session.pendingSettlement && session.status !== 'RESOLVED') throw new Error('Invalid defense');
  return true;
}

function finish(session, winner) {
  session.status = 'RESOLVED';
  session.pendingSettlement = true;
  session.winner = winner;
}

function tick(session) {
  session.time += STEP;
  for (const enemy of session.queue) {
    if (!enemy.spawned && session.time >= enemy.spawnAt) {
      enemy.spawned = true;
      session.enemies.push(enemy);
    }
  }
  for (const enemy of session.enemies) {
    if (enemy.hp <= 0 || enemy.leaked) continue;
    const slowed = session.time < enemy.slowUntil ? 1 - (enemy.slowFraction || 0.4) : 1;
    enemy.progress += enemy.speed * slowed * STEP;
    if (enemy.progress >= session.laneLength - 1) {
      enemy.leaked = true;
      enemy.hp = 0;
      session.core -= enemy.damage * 3 + 20;
    }
  }
  const aura = session.towers.filter(tower => tower.aura > 0);
  for (const tower of session.towers) {
    if (!(tower.rate > 0)) continue;
    tower.cooldown -= STEP;
    if (tower.cooldown > 0) continue;
    const living = session.enemies.filter(enemy => enemy.hp > 0 && !enemy.leaked && enemy.progress > 0);
    let target = null;
    let best = Infinity;
    for (const enemy of living) {
      const gap = distance([tower.x, tower.y], pointAt(enemy.progress));
      if (gap < best) { best = gap; target = enemy; }
    }
    if (!target || best > tower.rng) continue;
    const support = aura.reduce((sum, other) => sum + (distance([other.x, other.y], [tower.x, tower.y]) <= other.rng ? other.aura : 0), 0);
    const amount = tower.dmg * (1 + support);
    target.hp -= amount;
    if (tower.splash > 0) {
      const centre = pointAt(target.progress);
      for (const other of living) {
        if (other !== target && distance(centre, pointAt(other.progress)) <= tower.splash) other.hp -= amount * 0.6;
      }
    }
    if (tower.slow > 0) { target.slowUntil = session.time + 1.4; target.slowFraction = tower.slow; }
    tower.cooldown = 1 / tower.rate;
  }
  if (session.heroDeployed) {
    session.heroCooldown = (session.heroCooldown || 0) - STEP;
    if (session.heroCooldown <= 0) {
      const foe = session.enemies.find(enemy => enemy.hp > 0 && !enemy.leaked && Math.abs(enemy.progress - session.heroAt) <= 1.05);
      if (foe) foe.hp -= session.heroDamage;
      session.heroCooldown = 1 / 2.6;
    }
  }
  const waves = new Set(session.queue.map(enemy => enemy.wave));
  let cleared = 0;
  for (const wave of waves) {
    const members = session.queue.filter(enemy => enemy.wave === wave);
    if (members.every(enemy => enemy.spawned && enemy.hp <= 0 && !enemy.leaked)) cleared += 1;
  }
  session.clearedWaves = cleared;
  if (session.core <= 0) finish(session, 'e');
  else if (session.queue.every(enemy => enemy.spawned) && session.enemies.every(enemy => enemy.hp <= 0)) {
    if (session.practice === 'endless' && session.extensions < 1) {
      session.extensions += 1;
      const more = schedule(session.age, session.difficulty * (1 + 0.12 * session.waves), 3, session.rngState || 1);
      const shift = session.time + 1.2;
      for (const enemy of more.queue) {
        enemy.wave += session.waves;
        enemy.spawnAt += shift;
        enemy.id = `x${enemy.id}`;
        session.queue.push(enemy);
      }
      session.waves += 3;
    } else finish(session, 'p');
  }
}

export function advanceDefense(session, dt, { paused = false, speed = session.speed } = {}) {
  const next = clone(session);
  if (next.status !== 'ACTIVE') return next;
  if (paused) { next.paused = true; next.accumulator = 0; return next; }
  next.paused = false;
  next.speed = speed === 2 ? 2 : 1;
  let accumulator = next.accumulator + Math.min(Math.max(dt, 0), FRAME_CAP) * next.speed;
  let steps = 0;
  while (accumulator >= STEP && steps < MAX_STEPS) {
    tick(next);
    accumulator -= STEP;
    steps += 1;
    if (next.status !== 'ACTIVE') break;
  }
  next.accumulator = next.status === 'ACTIVE' ? accumulator : 0;
  next.steps = steps;
  return next;
}

export function deployHero(session, damage) {
  if (session.heroDeployed) throw new Error('Hero already deployed');
  if (!(damage > 0)) throw new Error('Invalid hero deployment');
  const next = clone(session);
  next.heroDeployed = true;
  next.heroDamage = damage;
  next.heroAt = Math.max(1, next.laneLength * 0.45);
  next.heroCooldown = 0;
  return next;
}

export function earlyCall(session) {
  if (session.practice !== 'siege') throw new Error('Early call is a siege reward');
  const wave = session.clearedWaves - 1;
  if (wave < 0 || session.earlyCalls.includes(wave)) throw new Error('No eligible early call');
  const next = clone(session);
  next.earlyCalls = [...session.earlyCalls, wave];
  return next;
}
