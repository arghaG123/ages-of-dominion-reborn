// Fixed-step defense. Pause adds no catch-up attacks. 2x multiplies the same 1/60 step.
import contract from '../data/implementation-contract.json' with { type: 'json' };
import referenceData from '../data/reference-data.json' with { type: 'json' };

import { ROLE_MULTIPLIER, seededOrder, towerStats, unitStats, wavePlan } from './mechanics.js';

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
    // Source extension batches restart the composition index at 0. Difficulty keeps 1+0.12*globalWave.
    const difficulty = scaleByWave ? baseDifficulty * (1 + 0.12 * wave) : baseDifficulty;
    const plan = wavePlan(scaleByWave ? offset : wave, age, difficulty);
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
    const pad = pads[index];
    if (!pad) throw new Error('No open defense cell');
    return {
      id: tower.id, fam: tower.fam, siteId: pad.id, x: pad.x, y: pad.y, cooldown: 0, xp: 0,
      dmg: stats.dmg, rate: stats.rate, rng: stats.rng, splash: stats.splash, slow: stats.slow, aura: stats.aura,
      hp: stats.hp, maxHp: stats.hp,
    };
  });
  return {
    id: `${practice}-${state.day}-${state.revision}`,
    practice, status: 'ACTIVE', pendingSettlement: false, difficulty, age: state.age,
    core: (400 + 180 * (state.walls?.level || 0) + 60 * state.age) * (practice === 'endless' ? 1.4 : 1),
    time: 0, accumulator: 0, speed: 1, paused: false,
    waves, clearedWaves: 0, earlyCalls: [], heroDeployed: false, armyDeployed: false, army: null,
    extensions: 0, rngState: planned.rngState,
    towers, queue: planned.queue, enemies: [], projectiles: [], laneLength: lane.length,
  };
}

export function defensePreparationMarkers(state, data = referenceData) {
  if (!state || !Array.isArray(state.towers)) return { enemies: [], towers: [], hero: null, army: null, queue: [], projectiles: [] };
  const towers = state.towers.map((tower, index) => {
    const pad = pads[index];
    if (!pad) return null;
    const stats = towerStats(tower, data);
    return { id: tower.id, fam: tower.fam, hp: stats.hp, maxHp: stats.hp, at: [pad.x, pad.y], alive: true };
  }).filter(Boolean);
  return { enemies: [], towers, hero: null, army: null, queue: [], projectiles: [] };
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
  if (session.heroDeployed && (!finiteField(session.heroDamage, Number.MIN_VALUE) || session.heroDamage <= 0 || !finiteField(session.heroAt) || !finiteField(session.heroCooldown) || !finiteField(session.heroX) || !finiteField(session.heroY) || !finiteField(session.heroRange, Number.MIN_VALUE) || !finiteField(session.heroRate, Number.MIN_VALUE) || !finiteField(session.heroHp) || !finiteField(session.heroMaxHp, Number.MIN_VALUE))) throw new Error('Invalid defense');
  if (session.heroXp != null && !finiteField(session.heroXp)) throw new Error('Invalid defense experience');
  if (session.armyDeployed) {
    const army = session.army;
    if (!army || typeof army.stackId !== 'string' || !finiteField(army.at) || !finiteField(army.x) || !finiteField(army.y) || !finiteField(army.hp) || !finiteField(army.maxHp, Number.MIN_VALUE) || !finiteField(army.damage, Number.MIN_VALUE) || !finiteField(army.cooldown)) throw new Error('Invalid army deployment');
    if (army.unitHp != null && !finiteField(army.unitHp, Number.MIN_VALUE)) throw new Error('Invalid army deployment');
    if (army.block != null && !finiteField(army.block)) throw new Error('Invalid army deployment');
    if (army.shots != null && (!Number.isFinite(army.shots) || army.shots < 0)) throw new Error('Invalid army deployment');
    if (army.xp != null && !finiteField(army.xp)) throw new Error('Invalid defense experience');
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
    if (!finiteField(tower.xp)) throw new Error('Invalid defense experience');
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

// Source bHurt credits 0.045 of the dealt blow, then 5, or 18 for a boss, once when this blow kills.
// Overkill still uses the full blow. A second blow on a dead enemy credits nothing. Wrecked towers do not lose rank.
function hurtEnemy(enemy, amount, source) {
  if (!(amount > 0) || enemy.hp <= 0 || enemy.leaked) return false;
  const killing = enemy.hp <= amount;
  enemy.hp -= amount;
  if (source && typeof source === 'object') {
    source.xp = (source.xp || 0) + amount * 0.045;
    if (killing) source.xp += enemy.boss ? 18 : 5;
  }
  return killing;
}

function padById(siteId) {
  const pad = pads.find(item => item.id === siteId);
  if (!pad) throw new Error('Invalid defense cell');
  return pad;
}

function cellOccupied(session, siteId) {
  if (!siteId) return false;
  if (session.towers.some(tower => tower.siteId === siteId)) return true;
  if (session.heroSite === siteId) return true;
  if (session.army?.siteId === siteId) return true;
  return false;
}

function nearestProgress(x, y) {
  let best = 0;
  let gap = Infinity;
  lane.forEach((point, index) => {
    const distanceToPad = Math.hypot(point[0] - x, point[1] - y);
    if (distanceToPad < gap) { gap = distanceToPad; best = index; }
  });
  return best;
}

const BOARD_COLS = geo.cols;
const BOARD_ROWS = geo.rows;
const RANGED_LANE_SCALE = 0.45;

function onBoard(x, y) {
  return Number.isFinite(x) && Number.isFinite(y) && x >= 0 && x < BOARD_COLS && y >= 0 && y < BOARD_ROWS;
}
function stackFactor(army) {
  if (!(army?.unitHp > 0) || !(army.hp > 0)) return 1;
  return Math.max(1, Math.ceil(army.hp / army.unitHp) * 0.4 + 0.6);
}
function blockMultiplier(block) {
  return Math.max(0.1, 1 - 0.06 * (Number.isFinite(block) ? block : 0));
}
function heroPoint(session) {
  if (Number.isFinite(session.heroX) && Number.isFinite(session.heroY)) return [session.heroX, session.heroY];
  return pointAt(session.heroAt || 0);
}
function armyPoint(session) {
  const army = session.army;
  if (Number.isFinite(army?.x) && Number.isFinite(army?.y)) return [army.x, army.y];
  return pointAt(army?.at || 0);
}
function placeOnLane(progress) {
  const at = pointAt(progress);
  return { x: at[0], y: at[1] };
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
    if (session.heroDeployed && (session.heroHp ?? 1) > 0) {
      const gap = distance(at, heroPoint(session));
      if (gap < best && gap <= profile.range) { best = gap; target = { kind: 'hero' }; }
    }
    if (session.armyDeployed && session.army.hp > 0) {
      const gap = distance(at, armyPoint(session));
      if (gap < best && gap <= profile.range) { best = gap; target = { kind: 'army' }; }
    }
    if (target && best <= profile.range) {
      if (target.kind === 'hero') session.heroHp = Math.max(0, (session.heroHp ?? 0) - enemy.damage);
      else if (target.kind === 'army') session.army.hp = Math.max(0, session.army.hp - enemy.damage);
      else {
        hurtTower(target, enemy.damage);
        emitProjectile(session, 'archer', at, [target.x, target.y]);
      }
      enemy.attackCooldown = profile.delay;
    }
  }
}

function stepArmy(session) {
  const army = session.army;
  if (!session.armyDeployed || !army || !(army.hp > 0)) return;
  if (!Number.isFinite(army.x) || !Number.isFinite(army.y)) return;
  if (army.role === 'ranged' || army.range > 0) {
    army.x = army.homeX;
    army.y = army.homeY;
    return;
  }
  const living = livingEnemies(session).filter(entered);
  let target = null;
  let best = Infinity;
  for (const enemy of living) {
    const fromHome = distance([army.homeX, army.homeY], pointAt(enemy.progress));
    if (army.role !== 'fly' && fromHome > (army.engage || 2.6)) continue;
    const gap = distance([army.x, army.y], pointAt(enemy.progress));
    if (gap < best) { best = gap; target = enemy; }
  }
  const speed = (army.speed || 0.64) * (army.role === 'fly' ? 1.4 : 1) * STEP;
  const goal = target ? pointAt(target.progress) : [army.homeX, army.homeY];
  const dist = distance([army.x, army.y], goal);
  if (!(dist > (target ? 1 : 0.02))) return;
  const travel = target ? Math.min(dist - 0.95, speed) : Math.min(dist, speed);
  if (!(travel > 0)) return;
  army.x += (goal[0] - army.x) / dist * travel;
  army.y += (goal[1] - army.y) / dist * travel;
}

function settleAfterDamage(session) {
  session.clearedWaves = countCleared(session);
  syncEnemies(session);
  if (session.status !== 'ACTIVE') return;
  if (session.core <= 0) finish(session, 'e');
  else if (session.queue.every(enemy => enemy.spawned) && session.queue.every(enemy => enemy.hp <= 0)) {
    if (session.practice === 'endless') extendEndless(session);
    else finish(session, 'p');
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
          || (session.heroDeployed && (session.heroHp ?? 1) > 0 && distance(at, heroPoint(session)) <= ranged.range)
          || (session.armyDeployed && session.army.hp > 0 && distance(at, armyPoint(session)) <= ranged.range);
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
      const army = session.army;
      const armyContact = session.armyDeployed && army?.hp > 0 && !(army.range > 0) && distance(armyPoint(session), pointAt(enemy.progress)) <= CONTACT;
      const heroContact = session.heroDeployed && (session.heroHp ?? 1) > 0 && distance(heroPoint(session), pointAt(enemy.progress)) <= CONTACT;
      if (armyContact) {
        army.hp = Math.max(0, army.hp - enemy.damage * blockMultiplier(army.block));
        hurtEnemy(enemy, army.damage * stackFactor(army), army);
        enemy.attackCooldown = MELEE_DELAY;
      } else if (heroContact) {
        const bucket = { xp: session.heroXp || 0 };
        hurtEnemy(enemy, session.heroDamage, bucket);
        session.heroXp = bucket.xp;
        session.heroHp = Math.max(0, (session.heroHp ?? 0) - enemy.damage);
        enemy.attackCooldown = MELEE_DELAY;
      }
    }
  }
  stepArmy(session);
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
    hurtEnemy(target, amount, tower);
    if (!(tower.slow > 0) && !(tower.aura > 0) && tower.fam !== 'slow' && tower.fam !== 'support') {
      emitProjectile(session, tower.fam, [tower.x, tower.y], pointAt(target.progress));
    }
    if (tower.splash > 0) {
      const centre = pointAt(target.progress);
      for (const other of living) {
        if (other !== target && distance(centre, pointAt(other.progress)) <= tower.splash) hurtEnemy(other, amount * 0.6, tower);
      }
    }
    if (tower.slow > 0) { target.slowUntil = session.time + 1.4; target.slowFraction = tower.slow; }
    tower.cooldown = 1 / tower.rate;
  }
  if (session.heroDeployed && (session.heroHp ?? 1) > 0) {
    session.heroCooldown = Math.max(0, (session.heroCooldown || 0) - STEP);
    if (session.heroCooldown <= 0) {
      const origin = heroPoint(session);
      const range = session.heroRange || 2.2;
      let foe = null;
      let best = Infinity;
      for (const enemy of livingEnemies(session)) {
        if (!entered(enemy)) continue;
        const gap = distance(origin, pointAt(enemy.progress));
        if (gap <= range && gap < best) { best = gap; foe = enemy; }
      }
      if (foe) {
        const crowded = livingEnemies(session).some(enemy => entered(enemy) && distance(origin, pointAt(enemy.progress)) <= 1);
        const bucket = { xp: session.heroXp || 0 };
        hurtEnemy(foe, session.heroDamage * (crowded ? 0.5 : 1), bucket);
        session.heroXp = bucket.xp;
        emitProjectile(session, 'hero', origin, pointAt(foe.progress));
      }
      session.heroCooldown = 1 / (session.heroRate || 1.1);
    }
  }
  if (session.armyDeployed && session.army.hp > 0 && session.army.range > 0) {
    session.army.cooldown = Math.max(0, session.army.cooldown - STEP);
    if (session.army.cooldown <= 0 && session.army.shots > 0) {
      const origin = armyPoint(session);
      let foe = null;
      let best = -Infinity;
      for (const enemy of livingEnemies(session)) {
        if (!entered(enemy)) continue;
        const gap = distance(origin, pointAt(enemy.progress));
        if (gap > session.army.range) continue;
        const threat = (enemy.boss ? 200 : 0) + enemy.damage * enemy.speed * 10 - gap;
        if (threat > best) { best = threat; foe = enemy; }
      }
      if (foe) {
        const crowded = livingEnemies(session).some(enemy => entered(enemy) && distance(origin, pointAt(enemy.progress)) <= 1);
        hurtEnemy(foe, session.army.damage * stackFactor(session.army) * (crowded ? 0.5 : 1), session.army);
        session.army.shots -= 1;
        emitProjectile(session, 'army', origin, pointAt(foe.progress));
      }
      session.army.cooldown = 1 / ARMY_RATE;
    }
  }
  settleAfterDamage(session);
}

export function advanceDefense(session, dt, { paused = false, speed = session.speed } = {}) {
  validateDefense(session);
  const next = clone(session);
  if (next.status !== 'ACTIVE') return next;
  if (paused) { next.paused = true; next.speed = speed === 2 ? 2 : 1; next.accumulator = 0; return next; }
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

export function deployHero(session, damage, siteId = null) {
  validateDefense(session);
  if (session.status !== 'ACTIVE') throw new Error('No active defense');
  if (session.heroDeployed) throw new Error('Hero already deployed');
  if (!(damage > 0)) throw new Error('Invalid hero deployment');
  const next = clone(session);
  next.heroDeployed = true;
  next.heroDamage = damage;
  next.heroXp = 0;
  next.heroCooldown = 0;
  next.heroRange = 2.2;
  next.heroRate = 1.1;
  next.heroHp = 400;
  next.heroMaxHp = 400;
  if (siteId) {
    if (cellOccupied(next, siteId)) throw new Error('Defense cell is occupied');
    const pad = padById(siteId);
    next.heroSite = siteId;
    next.heroAt = nearestProgress(pad.x, pad.y);
    next.heroX = pad.x;
    next.heroY = pad.y;
  } else {
    next.heroSite = null;
    next.heroAt = Math.max(ENTRY + 0.2, next.laneLength * 0.45);
    const placed = placeOnLane(next.heroAt);
    next.heroX = placed.x;
    next.heroY = placed.y;
  }
  validateDefense(next);
  return next;
}

export function deployArmy(session, stack, siteId = null) {
  validateDefense(session);
  if (session.status !== 'ACTIVE') throw new Error('No active defense');
  if (session.armyDeployed) throw new Error('Army already deployed');
  if (!stack || typeof stack.id !== 'string' || !(stack.count > 0)) throw new Error('Invalid army stack');
  const stats = unitStats(stack, referenceData);
  const next = clone(session);
  if (siteId && cellOccupied(next, siteId)) throw new Error('Defense cell is occupied');
  const pad = siteId ? padById(siteId) : null;
  const at = pad ? nearestProgress(pad.x, pad.y) : Math.max(ENTRY + 0.35, next.laneLength * 0.55);
  const placed = pad ? { x: pad.x, y: pad.y } : placeOnLane(at);
  const ranged = (stats.rng || 0) > 0;
  next.armyDeployed = true;
  next.army = {
    stackId: stack.id,
    kind: stack.kind,
    type: stack.type,
    count: stack.count,
    siteId: siteId || null,
    at,
    x: placed.x,
    y: placed.y,
    homeX: placed.x,
    homeY: placed.y,
    hp: stats.hp * stack.count,
    maxHp: stats.hp * stack.count,
    unitHp: stats.hp,
    damage: Math.max(1, Math.round((stats.dmin + stats.dmax) / 2)),
    range: ranged ? Math.max(1, stats.rng * RANGED_LANE_SCALE) : 0,
    shots: stats.shots || 0,
    block: stats.block || 0,
    fly: stats.fly || 0,
    role: ranged ? 'ranged' : (stats.fly > 0 ? 'fly' : 'melee'),
    speed: (stats.spd || 4) * 0.16,
    engage: 2.6,
    xp: 0,
    cooldown: 0,
  };
  validateDefense(next);
  return next;
}

export function castDefense(session, damage, target) {
  validateDefense(session);
  if (session.status !== 'ACTIVE' || !session.heroDeployed || (session.heroHp ?? 1) <= 0) throw new Error('No deployed hero');
  if (!(damage > 0) || !Number.isFinite(damage)) throw new Error('Invalid defense cast');
  const explicit = Boolean(target) && ('x' in target || 'y' in target);
  const centre = explicit ? [target.x, target.y] : heroPoint(session);
  if (!onBoard(centre[0], centre[1])) throw new Error('Invalid defense cast');
  const before = clone(session);
  const next = clone(session);
  for (const enemy of next.queue) {
    if (!enemy.spawned || enemy.hp <= 0 || enemy.leaked) continue;
    if (distance(centre, pointAt(enemy.progress)) <= 1.6) hurtEnemy(enemy, damage, null);
  }
  next.time = before.time;
  next.accumulator = before.accumulator;
  next.paused = before.paused;
  next.speed = before.speed;
  settleAfterDamage(next);
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

export function adoptDefense(session) {
  if (!session || typeof session !== 'object') return session;
  if (session.heroDeployed) {
    if (!Number.isFinite(session.heroX) && Number.isFinite(session.heroAt)) {
      const at = pointAt(session.heroAt);
      session.heroX = at[0];
      session.heroY = at[1];
    }
    if (!Number.isFinite(session.heroRange)) session.heroRange = 2.2;
    if (!Number.isFinite(session.heroRate)) session.heroRate = 1.1;
    if (!Number.isFinite(session.heroHp)) session.heroHp = 400;
    if (!Number.isFinite(session.heroMaxHp)) session.heroMaxHp = 400;
    if (!Number.isFinite(session.heroXp)) session.heroXp = 0;
  }
  if (session.armyDeployed && session.army && !Number.isFinite(session.army.x) && Number.isFinite(session.army.at)) {
    const at = pointAt(session.army.at);
    session.army.x = at[0];
    session.army.y = at[1];
    if (!Number.isFinite(session.army.homeX)) session.army.homeX = at[0];
    if (!Number.isFinite(session.army.homeY)) session.army.homeY = at[1];
  }
  return session;
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
    hero: session.heroDeployed ? { at: heroPoint(session), hp: session.heroHp ?? 0 } : null,
    army: session.armyDeployed && session.army.hp > 0 ? { at: armyPoint(session), hp: session.army.hp, maxHp: session.army.maxHp, stackId: session.army.stackId } : null,
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
