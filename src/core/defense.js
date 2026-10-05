// Fixed-step defense. Pause adds no catch-up attacks. 2x multiplies the same 1/60 step.
import contract from '../data/implementation-contract.json' with { type: 'json' };

import { ROLE_MULTIPLIER, seededOrder, towerStats, wavePlan } from './mechanics.js';

export const STEP = 1 / 60;
const FRAME_CAP = 0.25;
const MAX_STEPS = 32;
const ROLES = ['brute', 'runner', 'archer', 'sapper', 'shaman'];
const ENTRY = 0.35;
const RANGED = {
  archer: { range: 2.16, delay: 1.3 },
  sapper: { range: 1.62, delay: 1.6 },
  shaman: { range: 2.484, delay: 2.0 },
};
const MELEE_DELAY = 1.4;
const HERO_RATE = 2.6;
const ARMY_RATE = 2.6;
const CONTACT = 1.05;
const PROJECTILE_LIFE = 0.28;
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
function entered(enemy) { return enemy.spawned && enemy.progress >= ENTRY && enemy.hp > 0 && !enemy.leaked; }
function livingEnemies(session) {
  return session.queue.filter(enemy => enemy.spawned && enemy.hp > 0 && !enemy.leaked);
}
function livingTowers(session) {
  return session.towers.filter(tower => tower.hp > 0);
}
function pickTarget(session, tower) {
  // Geometric coverage is already inside tower.rng. Archers and sappers stop
  // and damage a tower while it is busy with the nearest walker, so a tower
  // shoots an enemy who can hit it before any other enemy in range.
  const living = livingEnemies(session).filter(enemy => entered(enemy) && distance([tower.x, tower.y], pointAt(enemy.progress)) <= tower.rng);
  const threats = living.filter(enemy => {
    const profile = RANGED[enemy.role];
    if (!profile || enemy.role === 'shaman') return false;
    return distance([tower.x, tower.y], pointAt(enemy.progress)) <= profile.range;
  });
  const pool = threats.length ? threats : living;
  let target = null;
  let best = Infinity;
  for (const enemy of pool) {
    const gap = distance([tower.x, tower.y], pointAt(enemy.progress));
    if (gap < best) { best = gap; target = enemy; }
  }
  return target ? { target, gap: best } : null;
}
function emitProjectile(session, fam, from, to) {
  session.projectiles.push({
    id: `p-${session.time.toFixed(4)}-${session.projectiles.length}`,
    fam, from: [...from], to: [...to], born: session.time, life: PROJECTILE_LIFE,
  });
}

function schedule(age, baseDifficulty, startWave, count, rngState, scaleByWave) {
  const queue = [];
  let cursor = 0;
  const random = { rngState };
  for (let offset = 0; offset < count; offset++) {
    const wave = startWave + offset;
    const difficulty = scaleByWave ? baseDifficulty * (1 + 0.12 * wave) : baseDifficulty;
    const plan = wavePlan(wave, age, difficulty);
    const bag = [];
    for (const role of ROLES) for (let n = 0; n < plan.counts[role]; n++) bag.push(role);
    const ordered = seededOrder(bag, random);
    const waveStart = cursor;
    ordered.forEach((role, index) => {
      const multiplier = ROLE_MULTIPLIER[role];
      queue.push({
        id: `w${wave}-${index}`, role, boss: false, wave, spawned: false,
        hp: Math.round(plan.hp * multiplier.hp),
        damage: plan.damage * multiplier.damage,
        speed: plan.speed * multiplier.speed,
        spawnAt: waveStart + index * plan.gap,
        progress: 0, slowUntil: 0, slowFraction: 0, leaked: false,
        attackCooldown: 0, telegraphId: null, buffUntil: 0,
      });
    });
    cursor = waveStart + ordered.length * plan.gap + 1.2;
    if (offset === count - 1) {
      queue.push({
        id: `w${wave}-boss`, role: 'brute', boss: true, wave, spawned: false,
        hp: Math.round(plan.hp * 7),
        damage: plan.damage * 2.4,
        speed: plan.speed * 0.65,
        spawnAt: waveStart + ordered.length * plan.gap + 1.2,
        progress: 0, slowUntil: 0, slowFraction: 0, leaked: false,
        attackCooldown: 0, telegraphId: null, buffUntil: 0,
      });
      cursor = waveStart + ordered.length * plan.gap + 1.2 + plan.gap;
    }
  }
  return { queue, rngState: random.rngState };
}

export function createDefense(state, data, { practice, waves, difficulty = 1 }) {
  if (!['siege', 'endless'].includes(practice)) throw new Error('Invalid defense');
  const planned = schedule(state.age, difficulty, 0, waves, state.rngState, false);
  const towers = state.towers.map((tower, index) => {
    const stats = towerStats(tower, data);
    const pad = pads[index % pads.length];
    return {
      id: tower.id, fam: tower.fam, x: pad.x, y: pad.y, cooldown: 0,
      dmg: stats.dmg, rate: stats.rate, rng: stats.rng, splash: stats.splash, slow: stats.slow, aura: stats.aura,
      hp: stats.hp, maxHp: stats.hp,
    };
  });
  return {
    id: `${practice}-${state.day}-${state.revision}`,
    practice, status: 'ACTIVE', pendingSettlement: false, difficulty, age: state.age,
    core: 400 + 180 * (state.walls?.level || 0) + 60 * state.age,
    time: 0, accumulator: 0, speed: 1, paused: false,
    waves, clearedWaves: 0, earlyCalls: [], heroDeployed: false, armyDeployed: false, army: null,
    extensions: 0, rngState: planned.rngState,
    towers, queue: planned.queue, enemies: [], projectiles: [], laneLength: lane.length,
  };
}

function finiteField(value, min = 0) {
  return Number.isFinite(value) && value >= min;
}

export function validateDefense(session) {
  if (session == null) return true;
  if (!session || !['siege', 'endless'].includes(session.practice) || !['ACTIVE', 'RESOLVED'].includes(session.status)) throw new Error('Invalid defense');
  if (typeof session.id !== 'string' || !session.id) throw new Error('Invalid defense');
  if (typeof session.pendingSettlement !== 'boolean' || session.pendingSettlement !== (session.status === 'RESOLVED')) throw new Error('Invalid defense phase');
  if (!Number.isFinite(session.core)) throw new Error('Invalid defense');
  if (!finiteField(session.time)) throw new Error('Invalid defense time');
  if (!finiteField(session.accumulator) || session.accumulator >= STEP) throw new Error('Invalid defense');
  if (![1, 2].includes(session.speed) || typeof session.paused !== 'boolean') throw new Error('Invalid defense');
  if (session.paused && session.accumulator !== 0) throw new Error('Invalid defense');
  if (!Number.isInteger(session.age) || session.age < 0 || session.age > 7) throw new Error('Invalid defense');
  if (!finiteField(session.difficulty, Number.MIN_VALUE) || session.difficulty <= 0) throw new Error('Invalid defense');
  if (!Number.isInteger(session.waves) || session.waves < 1 || !Number.isInteger(session.clearedWaves) || session.clearedWaves < 0 || session.clearedWaves > session.waves) throw new Error('Invalid defense');
  if (!Number.isInteger(session.extensions) || session.extensions < 0) throw new Error('Invalid defense');
  if (!Number.isInteger(session.rngState) || session.rngState < 0 || session.rngState > 0xffffffff) throw new Error('Invalid defense');
  if (session.laneLength !== lane.length) throw new Error('Invalid defense');
  if (!Array.isArray(session.queue) || session.queue.length < 1) throw new Error('Empty active queue');
  if (!Array.isArray(session.enemies) || !Array.isArray(session.towers) || !Array.isArray(session.earlyCalls) || !Array.isArray(session.projectiles)) throw new Error('Invalid defense queue');
  if (typeof session.heroDeployed !== 'boolean' || typeof session.armyDeployed !== 'boolean') throw new Error('Invalid defense');
  if (session.heroDeployed && (!finiteField(session.heroDamage, Number.MIN_VALUE) || session.heroDamage <= 0 || !finiteField(session.heroAt) || !finiteField(session.heroCooldown))) throw new Error('Invalid defense');
  if (session.armyDeployed) {
    const army = session.army;
    if (!army || typeof army.stackId !== 'string' || !finiteField(army.at) || !finiteField(army.hp) || !finiteField(army.maxHp, Number.MIN_VALUE) || !finiteField(army.damage, Number.MIN_VALUE) || !finiteField(army.cooldown)) throw new Error('Invalid army deployment');
  } else if (session.army != null) throw new Error('Invalid army deployment');
  for (const shot of session.projectiles) {
    if (!shot || typeof shot.id !== 'string' || typeof shot.fam !== 'string' || !finiteField(shot.born) || !finiteField(shot.life, Number.MIN_VALUE)) throw new Error('Invalid projectile');
    if (!Array.isArray(shot.from) || !Array.isArray(shot.to) || shot.from.length !== 2 || shot.to.length !== 2) throw new Error('Invalid projectile');
  }
  const ids = new Set();
  const seenWaves = new Set();
  for (const enemy of session.queue) {
    if (!enemy || typeof enemy.id !== 'string' || !enemy.id || ids.has(enemy.id)) throw new Error('Invalid defense queue');
    ids.add(enemy.id);
    if (!ROLES.includes(enemy.role) || typeof enemy.boss !== 'boolean' || !Number.isInteger(enemy.wave) || enemy.wave < 0 || enemy.wave >= session.waves) throw new Error('Invalid defense queue');
    seenWaves.add(enemy.wave);
    if (typeof enemy.spawned !== 'boolean' || typeof enemy.leaked !== 'boolean') throw new Error('Invalid defense queue');
    if (!Number.isFinite(enemy.hp) || !finiteField(enemy.damage) || !finiteField(enemy.speed) || !finiteField(enemy.spawnAt) || !finiteField(enemy.progress)) throw new Error('Invalid defense queue');
    if (!finiteField(enemy.slowUntil) || !finiteField(enemy.slowFraction) || enemy.slowFraction > 1) throw new Error('Invalid defense effect');
    if (!finiteField(enemy.attackCooldown) || !finiteField(enemy.buffUntil)) throw new Error('Invalid defense effect');
    if (enemy.telegraphId != null && typeof enemy.telegraphId !== 'string') throw new Error('Invalid defense queue');
    if (enemy.leaked && enemy.hp > 0) throw new Error('Invalid defense queue');
    if (!enemy.spawned && (enemy.progress !== 0 || enemy.leaked)) throw new Error('Invalid defense queue');
  }
  for (let wave = 0; wave < session.waves; wave++) if (!seenWaves.has(wave)) throw new Error('Invalid defense queue');
  const spawned = session.queue.filter(enemy => enemy.spawned);
  if (session.enemies.length !== spawned.length) throw new Error('Invalid defense queue');
  const listed = new Set();
  for (const enemy of session.enemies) {
    const source = session.queue.find(item => item.id === enemy?.id);
    if (!source || !source.spawned || listed.has(source.id)) throw new Error('Invalid defense queue');
    listed.add(source.id);
    if (enemy.hp !== source.hp || enemy.progress !== source.progress || enemy.leaked !== source.leaked) throw new Error('Invalid defense queue');
  }
  let cleared = 0;
  for (let wave = 0; wave < session.waves; wave++) {
    const members = session.queue.filter(enemy => enemy.wave === wave);
    if (members.every(enemy => enemy.spawned && enemy.hp <= 0 && !enemy.leaked)) cleared += 1;
  }
  if (session.clearedWaves !== cleared) throw new Error('Invalid defense');
  const calls = new Set();
  for (const wave of session.earlyCalls) {
    if (!Number.isInteger(wave) || wave < 0 || wave >= session.waves || calls.has(wave) || wave >= session.clearedWaves) throw new Error('Invalid defense');
    calls.add(wave);
  }
  const towerIds = new Set();
  for (const tower of session.towers) {
    if (!tower || typeof tower.id !== 'string' || !tower.id || towerIds.has(tower.id) || typeof tower.fam !== 'string') throw new Error('Invalid defense');
    towerIds.add(tower.id);
    if (!finiteField(tower.x) || !finiteField(tower.y) || !finiteField(tower.cooldown) || !finiteField(tower.dmg)) throw new Error('Invalid tower damage');
    if (!finiteField(tower.rate) || !finiteField(tower.rng) || !finiteField(tower.splash) || !finiteField(tower.slow) || !finiteField(tower.aura) || tower.slow > 1) throw new Error('Invalid defense');
    if (!Number.isFinite(tower.hp) || !finiteField(tower.maxHp, Number.MIN_VALUE)) throw new Error('Invalid tower damage');
  }
  const allSpawned = session.queue.every(enemy => enemy.spawned);
  const allDown = session.queue.every(enemy => enemy.hp <= 0);
  const coreDead = session.core <= 0;
  if (session.status === 'ACTIVE') {
    if (session.winner != null) throw new Error('False resolved victory');
    if (coreDead || (allSpawned && allDown)) throw new Error('Invalid defense phase');
  } else if (session.winner === 'e') {
    if (!(session.core <= 0)) throw new Error('False resolved victory');
  } else if (session.winner === 'p') {
    if (session.practice !== 'siege' || coreDead || !allSpawned || !allDown) throw new Error('False resolved victory');
  } else throw new Error('False resolved victory');
  return true;
}

function syncEnemies(session) {
  session.enemies = session.queue.filter(enemy => enemy.spawned);
}

function extendEndless(session) {
  // Endless has no terminal victory. Each clear adds three waves at baseDifficulty*(1+0.12*waveIndex).
  // Deployment, tower identity and the running RNG stay on this session.
  const more = schedule(session.age, session.difficulty, session.waves, 3, session.rngState, true);
  const shift = session.time + 1.2;
  for (const enemy of more.queue) {
    enemy.spawnAt += shift;
    session.queue.push(enemy);
  }
  session.rngState = more.rngState;
  session.waves += 3;
  session.extensions += 1;
}

function finish(session, winner) {
  session.status = 'RESOLVED';
  session.pendingSettlement = true;
  session.winner = winner;
  session.accumulator = 0;
  session.projectiles = [];
}

function countCleared(session) {
  let cleared = 0;
  for (let wave = 0; wave < session.waves; wave++) {
    const members = session.queue.filter(enemy => enemy.wave === wave);
    if (members.length && members.every(enemy => enemy.spawned && enemy.hp <= 0 && !enemy.leaked)) cleared += 1;
  }
  return cleared;
}

function hurtTower(tower, amount) {
  tower.hp = Math.max(0, tower.hp - amount);
}

function enemyAttack(session, enemy) {
  const profile = RANGED[enemy.role];
  const at = pointAt(enemy.progress);
  if (enemy.role === 'shaman') {
    for (const ally of livingEnemies(session)) {
      if (ally === enemy) continue;
      if (distance(at, pointAt(ally.progress)) <= profile.range) {
        ally.buffUntil = Math.max(ally.buffUntil, session.time + 1.8);
        ally.hp += enemy.damage * 0.15;
      }
    }
    enemy.attackCooldown = profile.delay;
    return;
  }
  if (enemy.role === 'sapper') {
    let target = session.towers.find(tower => tower.id === enemy.telegraphId && tower.hp > 0);
    if (!target) {
      let best = Infinity;
      for (const tower of livingTowers(session)) {
        const gap = distance(at, [tower.x, tower.y]);
        if (gap < best) { best = gap; target = tower; }
      }
      enemy.telegraphId = target?.id ?? null;
    }
    if (target && distance(at, [target.x, target.y]) <= profile.range) {
      hurtTower(target, enemy.damage);
      emitProjectile(session, 'sapper', at, [target.x, target.y]);
      enemy.attackCooldown = profile.delay;
      return;
    }
  }
  if (enemy.role === 'archer') {
    let target = null;
    let best = Infinity;
    for (const tower of livingTowers(session)) {
      const gap = distance(at, [tower.x, tower.y]);
      if (gap < best) { best = gap; target = tower; }
    }
    if (session.heroDeployed) {
      const gap = Math.abs(enemy.progress - session.heroAt);
      if (gap < best && gap <= profile.range) { best = gap; target = { kind: 'hero' }; }
    }
    if (session.armyDeployed && session.army.hp > 0) {
      const gap = Math.abs(enemy.progress - session.army.at);
      if (gap < best && gap <= profile.range) { best = gap; target = { kind: 'army' }; }
    }
    if (target && best <= profile.range) {
      if (target.kind === 'hero') session.heroDamage = Math.max(1, session.heroDamage * 0.92);
      else if (target.kind === 'army') session.army.hp = Math.max(0, session.army.hp - enemy.damage);
      else {
        hurtTower(target, enemy.damage);
        emitProjectile(session, 'archer', at, [target.x, target.y]);
      }
      enemy.attackCooldown = profile.delay;
    }
  }
}

function tick(session) {
  session.time += STEP;
  session.projectiles = session.projectiles.filter(shot => session.time - shot.born < shot.life);
  for (const enemy of session.queue) {
    if (!enemy.spawned && session.time >= enemy.spawnAt) enemy.spawned = true;
  }
  syncEnemies(session);
  for (const enemy of session.queue) {
    if (!enemy.spawned || enemy.hp <= 0 || enemy.leaked) continue;
    enemy.attackCooldown = Math.max(0, enemy.attackCooldown - STEP);
    const slowed = session.time < enemy.slowUntil ? 1 - (enemy.slowFraction || 0.4) : 1;
    const buffed = session.time < enemy.buffUntil ? 1.12 : 1;
    const ranged = RANGED[enemy.role];
    let hold = false;
    if (entered(enemy) && ranged && enemy.attackCooldown <= 0) {
      const at = pointAt(enemy.progress);
      if (enemy.role === 'sapper') {
        if (!enemy.telegraphId) {
          let best = Infinity; let pick = null;
          for (const tower of livingTowers(session)) {
            const gap = distance(at, [tower.x, tower.y]);
            if (gap < best) { best = gap; pick = tower.id; }
          }
          enemy.telegraphId = pick;
        }
        const tower = session.towers.find(item => item.id === enemy.telegraphId && item.hp > 0);
        if (tower && distance(at, [tower.x, tower.y]) <= ranged.range) hold = true;
      } else if (enemy.role === 'shaman') {
        const threat = livingTowers(session).some(tower => distance(at, [tower.x, tower.y]) <= ranged.range)
          || livingEnemies(session).some(ally => ally !== enemy && distance(at, pointAt(ally.progress)) <= ranged.range);
        if (threat) hold = true;
      } else if (enemy.role === 'archer') {
        // A nearby attacker is not a target. Holding for allies froze archers
        // outside every living tower and left the wave unable to clear or leak.
        const threat = livingTowers(session).some(tower => distance(at, [tower.x, tower.y]) <= ranged.range)
          || (session.heroDeployed && Math.abs(enemy.progress - session.heroAt) <= ranged.range)
          || (session.armyDeployed && session.army.hp > 0 && Math.abs(enemy.progress - session.army.at) <= ranged.range);
        if (threat) hold = true;
      }
    }
    if (!hold) enemy.progress += enemy.speed * slowed * buffed * STEP;
    if (enemy.progress >= session.laneLength - 1) {
      enemy.leaked = true;
      enemy.hp = 0;
      session.core -= enemy.damage * 3 + 20;
      continue;
    }
    if (entered(enemy) && enemy.attackCooldown <= 0 && ranged) enemyAttack(session, enemy);
    if (entered(enemy) && !ranged && enemy.attackCooldown <= 0) {
      if (session.armyDeployed && session.army.hp > 0 && Math.abs(enemy.progress - session.army.at) <= CONTACT) {
        session.army.hp = Math.max(0, session.army.hp - enemy.damage);
        enemy.hp -= session.army.damage;
        enemy.attackCooldown = MELEE_DELAY;
      } else if (session.heroDeployed && Math.abs(enemy.progress - session.heroAt) <= CONTACT) {
        enemy.hp -= session.heroDamage;
        enemy.attackCooldown = MELEE_DELAY;
      }
    }
  }
  const aura = livingTowers(session).filter(tower => tower.aura > 0);
  for (const tower of session.towers) {
    if (!(tower.rate > 0) || tower.hp <= 0) continue;
    tower.cooldown = Math.max(0, tower.cooldown - STEP);
    if (tower.cooldown > 0) continue;
    const picked = pickTarget(session, tower);
    if (!picked) continue;
    const { target } = picked;
    const living = livingEnemies(session).filter(entered);
    const support = aura.reduce((sum, other) => sum + (distance([other.x, other.y], [tower.x, tower.y]) <= other.rng ? other.aura : 0), 0);
    const amount = tower.dmg * (1 + support);
    target.hp -= amount;
    emitProjectile(session, tower.fam, [tower.x, tower.y], pointAt(target.progress));
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
    session.heroCooldown = Math.max(0, (session.heroCooldown || 0) - STEP);
    if (session.heroCooldown <= 0) {
      const foe = livingEnemies(session).find(enemy => entered(enemy) && Math.abs(enemy.progress - session.heroAt) <= CONTACT);
      if (foe) {
        foe.hp -= session.heroDamage;
        emitProjectile(session, 'hero', pointAt(session.heroAt), pointAt(foe.progress));
      }
      session.heroCooldown = 1 / HERO_RATE;
    }
  }
  if (session.armyDeployed && session.army.hp > 0) {
    session.army.cooldown = Math.max(0, session.army.cooldown - STEP);
    if (session.army.cooldown <= 0) {
      const foe = livingEnemies(session).find(enemy => entered(enemy) && Math.abs(enemy.progress - session.army.at) <= CONTACT);
      if (foe) {
        foe.hp -= session.army.damage;
        emitProjectile(session, 'army', pointAt(session.army.at), pointAt(foe.progress));
      }
      session.army.cooldown = 1 / ARMY_RATE;
    }
  }
  session.clearedWaves = countCleared(session);
  syncEnemies(session);
  if (session.core <= 0) finish(session, 'e');
  else if (session.queue.every(enemy => enemy.spawned) && session.queue.every(enemy => enemy.hp <= 0)) {
    if (session.practice === 'endless') extendEndless(session);
    else finish(session, 'p');
  }
}

export function advanceDefense(session, dt, { paused = false, speed = session.speed } = {}) {
  validateDefense(session);
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
  validateDefense(next);
  return next;
}

export function deployHero(session, damage) {
  validateDefense(session);
  if (session.status !== 'ACTIVE') throw new Error('No active defense');
  if (session.heroDeployed) throw new Error('Hero already deployed');
  if (!(damage > 0)) throw new Error('Invalid hero deployment');
  const next = clone(session);
  next.heroDeployed = true;
  next.heroDamage = damage;
  next.heroAt = Math.max(ENTRY + 0.2, next.laneLength * 0.45);
  next.heroCooldown = 0;
  validateDefense(next);
  return next;
}

export function deployArmy(session, stack) {
  validateDefense(session);
  if (session.status !== 'ACTIVE') throw new Error('No active defense');
  if (session.armyDeployed) throw new Error('Army already deployed');
  if (!stack || typeof stack.id !== 'string' || !(stack.count > 0)) throw new Error('Invalid army stack');
  const next = clone(session);
  const unitHp = 24 + 6 * (stack.rank || 0) + 4 * (stack.age || 0);
  next.armyDeployed = true;
  next.army = {
    stackId: stack.id,
    kind: stack.kind,
    type: stack.type,
    at: Math.max(ENTRY + 0.35, next.laneLength * 0.55),
    hp: unitHp * stack.count,
    maxHp: unitHp * stack.count,
    damage: 4 + 2 * (stack.rank || 0) + (stack.kind === 'creature' ? 1 : 0),
    cooldown: 0,
  };
  validateDefense(next);
  return next;
}

export function earlyCall(session) {
  validateDefense(session);
  if (session.practice !== 'siege') throw new Error('Early call is a siege reward');
  const wave = session.clearedWaves - 1;
  if (wave < 0 || session.earlyCalls.includes(wave)) throw new Error('No eligible early call');
  const next = clone(session);
  next.earlyCalls = [...session.earlyCalls, wave];
  validateDefense(next);
  return next;
}

export function defenseMarkers(session) {
  if (!session) return { enemies: [], towers: [], hero: null, army: null, queue: [], projectiles: [] };
  const t = session.time;
  return {
    enemies: session.queue.filter(enemy => enemy.spawned && enemy.hp > 0 && !enemy.leaked).map(enemy => ({
      id: enemy.id, role: enemy.role, boss: enemy.boss, hp: enemy.hp, at: pointAt(enemy.progress),
      entered: enemy.progress >= ENTRY, telegraphId: enemy.telegraphId,
    })),
    towers: session.towers.map(tower => ({ id: tower.id, fam: tower.fam, hp: tower.hp, maxHp: tower.maxHp, at: [tower.x, tower.y], alive: tower.hp > 0 })),
    hero: session.heroDeployed ? { at: pointAt(session.heroAt) } : null,
    army: session.armyDeployed && session.army.hp > 0 ? { at: pointAt(session.army.at), hp: session.army.hp, maxHp: session.army.maxHp, stackId: session.army.stackId } : null,
    queue: session.queue.filter(enemy => !enemy.spawned).map(enemy => ({ id: enemy.id, role: enemy.role, boss: enemy.boss, wave: enemy.wave, spawnAt: enemy.spawnAt })),
    projectiles: session.projectiles.map(shot => {
      const u = Math.min(1, (t - shot.born) / shot.life);
      return {
        id: shot.id, fam: shot.fam,
        at: [shot.from[0] + (shot.to[0] - shot.from[0]) * u, shot.from[1] + (shot.to[1] - shot.from[1]) * u],
      };
    }),
  };
}
