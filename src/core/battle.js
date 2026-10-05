// Positioned tactical commands. Scalar damage stays in mechanics.js.
// Auto combat calls these same predicates. Positive morale does not grant an extra turn.
import contract from '../data/implementation-contract.json' with { type: 'json' };
import { applyDamage, calcDamage, previewRetaliation, unitStats } from './mechanics.js';
import { draw } from './rng.js';
import { heroStats, spellEffect } from './rules.js';

const geo = contract.geometry.tactical;
export const BOARD = { cols: geo.cols, rows: geo.rows };
export const COMMANDER = [Math.floor(geo.anchors.commander[0]), Math.floor(geo.anchors.commander[1])];
const ALLIED_CELLS = ['L1', 'L2', 'L3'].map(id => [Math.floor(geo.anchors[id][0]), Math.floor(geo.anchors[id][1])]);
const ENEMY_CELLS = ['R1', 'R2', 'R3'].map(id => [Math.floor(geo.anchors[id][0]), Math.floor(geo.anchors[id][1])]);
const river = new Set(geo.blocked.map(([x, y]) => `${x},${y}`));
for (const crossing of geo.bridges) for (const [x, y] of crossing.cells) river.delete(`${x},${y}`);
const obstacles = new Set((geo.obstacles ?? []).map(([x, y]) => `${x},${y}`));
const STEPS = [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]];

function clone(value) { return structuredClone(value); }
function key(x, y) { return `${x},${y}`; }
function living(stacks, side) {
  return stacks.filter(stack => stack.side === side && !stack.dead && stack.count > 0);
}
function hard(x, y) { return river.has(key(x, y)) || obstacles.has(key(x, y)); }

export function chebyshev(a, b) {
  return Math.max(Math.abs(a.x - b.x), Math.abs(a.y - b.y));
}

export function effectiveSpeed(stack) {
  const bonus = (stack.hasteCounter > 0 ? 3 : 0) - (stack.slowCounter > 0 ? 3 : 0);
  return Math.max(1, stack.spd + bonus);
}

function stackById(battle, id) {
  const stack = battle.stacks.find(item => item.id === id);
  if (!stack) throw new Error('Unknown stack');
  return stack;
}

export function activeStackId(battle) {
  return battle.queue.find(id => {
    const stack = battle.stacks.find(item => item.id === id);
    return stack && !stack.dead && !stack.acted;
  });
}

function occupied(battle, x, y, selfId) {
  return battle.stacks.some(stack => stack.id !== selfId && !stack.dead && stack.count > 0 && stack.x === x && stack.y === y);
}

function enterable(battle, x, y, stack) {
  if (!Number.isInteger(x) || !Number.isInteger(y) || x < 0 || y < 0 || x >= BOARD.cols || y >= BOARD.rows) return false;
  if (x === COMMANDER[0] && y === COMMANDER[1]) return false;
  if (occupied(battle, x, y, stack.id)) return false;
  if (hard(x, y) && !(stack.fly > 0)) return false;
  return true;
}

export function legalMoves(battle, id) {
  const stack = stackById(battle, id);
  if (battle.status !== 'ACTIVE' || activeStackId(battle) !== id || stack.dead || stack.x == null) return [];
  const flyer = stack.fly > 0;
  const speed = effectiveSpeed(stack);
  const best = new Map([[key(stack.x, stack.y), 0]]);
  const queue = [[stack.x, stack.y]];
  while (queue.length) {
    const [x, y] = queue.shift();
    const cost = best.get(key(x, y));
    if (cost >= speed) continue;
    for (const [dx, dy] of STEPS) {
      const nx = x + dx;
      const ny = y + dy;
      if (!enterable(battle, nx, ny, stack)) continue;
      if (dx !== 0 && dy !== 0 && !flyer && (!enterable(battle, x + dx, y, stack) || !enterable(battle, x, y + dy, stack))) continue;
      const nextKey = key(nx, ny);
      const nextCost = cost + 1;
      if (best.has(nextKey) && best.get(nextKey) <= nextCost) continue;
      best.set(nextKey, nextCost);
      queue.push([nx, ny]);
    }
  }
  const cells = [];
  for (const [cell, cost] of best) {
    if (cost < 1) continue;
    const [x, y] = cell.split(',').map(Number);
    if (hard(x, y)) continue;
    cells.push([x, y]);
  }
  return cells;
}

export function meleeApproaches(battle, attackerId, defenderId) {
  const attacker = stackById(battle, attackerId);
  const defender = stackById(battle, defenderId);
  if (chebyshev(attacker, defender) === 1) return [null];
  return legalMoves(battle, attackerId).filter(cell => chebyshev({ x: cell[0], y: cell[1] }, defender) === 1);
}

export function legalTargets(battle, id) {
  const attacker = stackById(battle, id);
  const enemies = living(battle.stacks, attacker.side === 'p' ? 'e' : 'p');
  const melee = [];
  const ranged = [];
  for (const enemy of enemies) {
    if (meleeApproaches(battle, id, enemy.id).length) melee.push(enemy.id);
    if (attacker.rng > 0 && attacker.shots > 0 && chebyshev(attacker, enemy) <= attacker.rng) ranged.push(enemy.id);
  }
  return { melee, ranged, moves: legalMoves(battle, id) };
}

/** Complete melee transaction: adjacent strikes omit approach; reachable strikes include one legal cell. */
export function meleeCommand(battle, attackerId, defenderId) {
  const approaches = meleeApproaches(battle, attackerId, defenderId);
  if (!approaches.length) throw new Error('No melee approach');
  const approach = approaches.find(cell => Array.isArray(cell)) ?? null;
  return {
    action: 'strike',
    stackId: attackerId,
    targetId: defenderId,
    forceMelee: true,
    ...(approach ? { approach } : {}),
  };
}

function finiteCounter(stack, name) {
  const value = stack[name] ?? 0;
  if (!Number.isInteger(value) || value < 0) throw new Error('Invalid battle effect');
}

export function validateBattle(battle) {
  if (battle == null) return true;
  if (!battle || typeof battle.id !== 'string' || !battle.id) throw new Error('Invalid battle');
  if (!['tactical', 'defense'].includes(battle.kind)) throw new Error('Invalid battle');
  if (!['PENDING', 'ACTIVE', 'RESOLVED'].includes(battle.status)) throw new Error('Invalid battle');
  if (!['campaign', 'skirmish', 'challenge'].includes(battle.practice)) throw new Error('Invalid battle');
  if (!Number.isInteger(battle.rngState) || battle.rngState < 0 || battle.rngState > 0xffffffff) throw new Error('RNG above 32 bits');
  if (!Number.isFinite(battle.mana) || battle.mana < 0) throw new Error('Negative mana');
  if (!Array.isArray(battle.stacks) || !Array.isArray(battle.queue)) throw new Error('Invalid battle');
  if (battle.round == null || !Number.isInteger(battle.round) || battle.round < 1) throw new Error('Invalid battle');
  if (typeof battle.pendingSettlement !== 'boolean' || typeof battle.settled !== 'boolean') throw new Error('Invalid battle phase');
  if (battle.pendingSettlement && battle.status !== 'RESOLVED') throw new Error('Invalid battle phase');
  if (battle.status === 'RESOLVED') {
    const winner = battle.outcome?.winner;
    if (!['p', 'e', 'none', 'retreat'].includes(winner)) throw new Error('Invalid battle outcome');
    const players = living(battle.stacks, 'p').length;
    const enemies = living(battle.stacks, 'e').length;
    if (winner === 'p' && enemies) throw new Error('False resolved victory');
    if (winner === 'e' && players) throw new Error('False resolved victory');
    if (winner === 'none' && (players || enemies)) throw new Error('False resolved victory');
    if (battle.pendingSettlement && winner === 'p' && battle.outcome.reward !== true) throw new Error('Corrupt settlement');
    if (battle.pendingSettlement && winner !== 'p' && battle.outcome.reward === true) throw new Error('Corrupt settlement');
  } else if (battle.outcome != null) throw new Error('Invalid battle outcome');
  const ids = new Set();
  const occupiedCells = new Set();
  let placed = 0;
  for (const stack of battle.stacks) {
    if (ids.has(stack.id) || typeof stack.id !== 'string' || !stack.id) throw new Error('Invalid battle');
    ids.add(stack.id);
    if (!['p', 'e'].includes(stack.side) || !Number.isInteger(stack.count) || stack.count < 0) throw new Error('Invalid battle');
    if (Boolean(stack.dead) !== (stack.count === 0)) throw new Error('Invalid battle');
    if (!stack.dead && (!Number.isInteger(stack.spd) || stack.spd < 1)) throw new Error('Invalid speed');
    if (!stack.dead && (!Number.isFinite(stack.uhp) || stack.uhp <= 0 || !(stack.top > 0 && stack.top <= stack.uhp))) throw new Error('Invalid hit points');
    if (stack.dead && stack.top != null && stack.top !== 0) throw new Error('Invalid hit points');
    if (!stack.dead) {
      if (!Number.isFinite(stack.dmin) || !Number.isFinite(stack.dmax) || stack.dmin < 0 || stack.dmax < stack.dmin) throw new Error('Invalid damage');
      if (!Number.isInteger(stack.maxCount) || stack.maxCount < 1 || stack.count > stack.maxCount) throw new Error('Invalid maxCount');
      finiteCounter(stack, 'hasteCounter');
      finiteCounter(stack, 'slowCounter');
      finiteCounter(stack, 'blessCounter');
    }
    const positioned = battle.positioned || stack.x != null || stack.y != null;
    if (positioned && !stack.dead) {
      if (!Number.isInteger(stack.x) || !Number.isInteger(stack.y)) throw new Error('Out of bounds position');
      if (stack.x < 0 || stack.y < 0 || stack.x >= BOARD.cols || stack.y >= BOARD.rows) throw new Error('Out of bounds position');
      if (stack.x === COMMANDER[0] && stack.y === COMMANDER[1]) throw new Error('Commander cell is not a stack cell');
      // Flight may cross obstacles. A saved stack must still finish on a legal cell.
      if (hard(stack.x, stack.y)) throw new Error('Blocked-water flyer destination');
      const cell = key(stack.x, stack.y);
      if (occupiedCells.has(cell)) throw new Error('Occupied cell');
      occupiedCells.add(cell);
      placed += 1;
    }
  }
  if (placed > 6) throw new Error('Too many stacks');
  if (battle.status === 'ACTIVE' && battle.queue.length < 1) throw new Error('Empty active queue');
  const seenQueue = new Set();
  for (const id of battle.queue) {
    if (!ids.has(id) || seenQueue.has(id)) throw new Error('Unknown queue id');
    seenQueue.add(id);
  }
  if (battle.status === 'ACTIVE' && !activeStackId(battle)) throw new Error('Empty active queue');
  return true;
}

function normalize(stack) {
  return {
    ...stack,
    acted: false,
    waited: false,
    retaliated: false,
    defending: false,
    dead: stack.count === 0,
    hasteCounter: stack.hasteCounter || 0,
    slowCounter: stack.slowCounter || 0,
    blessCounter: stack.blessCounter || 0,
    fly: stack.fly || 0,
    dealt: stack.dealt || 0,
    maxCount: stack.maxCount ?? stack.count,
    shots: stack.shots ?? 0,
    rng: stack.rng ?? 0,
  };
}

export function turnOrder(battle) {
  const ready = battle.stacks.filter(stack => !stack.dead && stack.count > 0).map(stack => ({ id: stack.id, speed: effectiveSpeed(stack), tie: draw(battle) }));
  ready.sort((a, b) => b.speed - a.speed || a.tie - b.tie || (a.id < b.id ? -1 : 1));
  return ready.map(entry => entry.id);
}

export function startBattle(spec) {
  const battle = {
    id: spec.id,
    kind: spec.kind || 'tactical',
    status: 'ACTIVE',
    practice: spec.practice || 'campaign',
    positioned: spec.positioned === true,
    rngState: spec.rngState >>> 0,
    round: 1,
    stacks: spec.stacks.map(normalize),
    queue: [],
    log: [],
    castThisRound: false,
    wisdom: spec.wisdom || 0,
    mana: spec.mana ?? 0,
    hero: spec.hero ?? null,
    encounterId: spec.encounterId ?? null,
    origin: spec.origin ?? null,
    adventureCell: spec.adventureCell ?? null,
    difficulty: spec.difficulty ?? 1,
    unfielded: spec.unfielded ?? [],
    outcome: null,
    pendingSettlement: false,
    settled: false,
  };
  battle.queue = turnOrder(battle);
  validateBattle(battle);
  return battle;
}

function requireTurn(battle, id) {
  if (battle.status !== 'ACTIVE' || activeStackId(battle) !== id) throw new Error('Not this stack\'s turn');
  return stackById(battle, id);
}

function decay(stack) {
  if (stack.hasteCounter > 0) stack.hasteCounter -= 1;
  if (stack.slowCounter > 0) stack.slowCounter -= 1;
  if (stack.blessCounter > 0) stack.blessCounter -= 1;
}

function adjacentEnemy(battle, stack) {
  return living(battle.stacks, stack.side === 'p' ? 'e' : 'p').some(enemy => chebyshev(stack, enemy) <= 1);
}

function endAction(battle) {
  finishIfDecided(battle);
  if (battle.status === 'ACTIVE' && !activeStackId(battle)) nextRound(battle);
}

export function wait(battle, id) {
  const next = clone(battle);
  const stack = requireTurn(next, id);
  if (stack.waited) throw new Error('Wait already used');
  stack.waited = true;
  next.queue = next.queue.filter(item => item !== id).concat(id);
  next.log.push({ type: 'wait', id });
  validateBattle(next);
  return next;
}

export function defend(battle, id) {
  const next = clone(battle);
  const stack = requireTurn(next, id);
  stack.defending = true;
  stack.acted = true;
  decay(stack);
  next.log.push({ type: 'defend', id });
  endAction(next);
  validateBattle(next);
  return next;
}

export function move(battle, id, to) {
  if (!Array.isArray(to) || to.length !== 2) throw new Error('Illegal move');
  const next = clone(battle);
  const stack = requireTurn(next, id);
  const legal = legalMoves(next, id).some(cell => cell[0] === to[0] && cell[1] === to[1]);
  if (!legal) throw new Error('Illegal move');
  stack.x = to[0];
  stack.y = to[1];
  stack.acted = true;
  decay(stack);
  next.log.push({ type: 'move', id, to: [to[0], to[1]] });
  endAction(next);
  validateBattle(next);
  return next;
}

export function strike(battle, attackerId, defenderId, options = {}) {
  const next = clone(battle);
  const attacker = requireTurn(next, attackerId);
  const defender = stackById(next, defenderId);
  if (attacker.dead || defender.dead || attacker.side === defender.side) throw new Error('Illegal target');
  const positioned = next.positioned || attacker.x != null || defender.x != null;
  const ranged = attacker.rng > 0 && !options.forceMelee;
  if (positioned) {
    if (attacker.x === COMMANDER[0] && attacker.y === COMMANDER[1]) throw new Error('Commander cell is not a stack cell');
    if (ranged) {
      if (attacker.shots <= 0) throw new Error('No ammunition');
      if (chebyshev(attacker, defender) > attacker.rng) throw new Error('Out of range');
    } else if (options.approach) {
      const approach = options.approach;
      const legal = legalMoves(next, attackerId).some(cell => cell[0] === approach[0] && cell[1] === approach[1]);
      if (!legal || chebyshev({ x: approach[0], y: approach[1] }, defender) !== 1) throw new Error('Approach is not reachable');
      attacker.x = approach[0];
      attacker.y = approach[1];
    } else if (chebyshev(attacker, defender) !== 1) throw new Error('Not adjacent');
  } else if (ranged && attacker.shots <= 0) throw new Error('No ammunition');
  const adjacent = positioned ? adjacentEnemy(next, attacker) : Boolean(options.adjacentEnemy);
  const hero = options.hero ?? next.hero ?? null;
  attacker.bless = attacker.blessCounter > 0;
  const preview = previewRetaliation(attacker, defender, { ...options, ranged, adjacentEnemy: adjacent, hero });
  const rolled = calcDamage(attacker, defender, { ...options, ranged, adjacentEnemy: adjacent, hero, rng: () => draw(next) });
  const applied = applyDamage(defender, rolled.dmg);
  defender.count = applied.count;
  defender.top = applied.top;
  defender.dead = applied.dead;
  attacker.dealt += rolled.dmg;
  if (ranged) attacker.shots -= 1;
  attacker.acted = true;
  decay(attacker);
  next.log.push({ type: 'strike', attackerId, defenderId, damage: rolled.dmg, killed: applied.killed, ranged, preview });
  if (!ranged && !applied.dead && !defender.retaliated && defender.count > 0) {
    defender.bless = defender.blessCounter > 0;
    const back = calcDamage(defender, attacker, { hero, rng: () => draw(next), ranged: false });
    const answer = applyDamage(attacker, back.dmg);
    attacker.count = answer.count;
    attacker.top = answer.top;
    attacker.dead = answer.dead;
    defender.dealt += back.dmg;
    defender.retaliated = true;
    next.log.push({ type: 'retaliate', attackerId: defenderId, defenderId: attackerId, damage: back.dmg, killed: answer.killed });
  }
  endAction(next);
  validateBattle(next);
  return next;
}

function healPool(target, amount) {
  const cap = target.maxCount * target.uhp;
  const pool = Math.min(cap, (target.count - 1) * target.uhp + target.top + (amount || 0));
  target.count = Math.max(1, Math.ceil(pool / target.uhp));
  target.top = pool - (target.count - 1) * target.uhp;
  target.dead = false;
}

export function castSpell(battle, spell, targetId, power) {
  const next = clone(battle);
  if (next.status !== 'ACTIVE' || next.castThisRound) throw new Error('Spell already cast');
  const actorId = activeStackId(next);
  const actor = actorId ? stackById(next, actorId) : null;
  if (!actor || actor.side !== 'p') throw new Error('The commander acts on the player turn');
  if (!spell || spell.lv > 1 + (next.wisdom || 0)) throw new Error('Spell is not known');
  if ((next.mana ?? 0) < spell.mana) throw new Error('Not enough mana');
  const target = stackById(next, targetId);
  const amount = spellEffect(spell.id, power);
  if (spell.id === 'arrow' || spell.id === 'bolt' || spell.id === 'fireball') {
    const victims = spell.id === 'fireball'
      ? living(next.stacks, 'e').filter(stack => chebyshev(stack, target) <= 1)
      : [target];
    if (target.side !== 'e' || target.dead || !victims.length) throw new Error('Illegal spell target');
    for (const victim of victims) {
      const applied = applyDamage(victim, amount ?? spell.mana);
      victim.count = applied.count;
      victim.top = applied.top;
      victim.dead = applied.dead;
    }
  } else if (spell.id === 'bless') {
    if (target.side !== 'p' || target.dead) throw new Error('Illegal spell target');
    target.blessCounter = Math.floor(power) + 1;
  } else if (spell.id === 'haste') {
    if (target.side !== 'p' || target.dead) throw new Error('Illegal spell target');
    target.hasteCounter = 3;
  } else if (spell.id === 'slow') {
    if (target.side !== 'e' || target.dead) throw new Error('Illegal spell target');
    target.slowCounter = 3;
  } else if (spell.id === 'cure' || spell.id === 'resurrect') {
    if (target.side !== 'p' || target.dead || target.count <= 0) throw new Error('Dead stacks are not a supported resurrection target');
    healPool(target, amount || 0);
  } else throw new Error('Unsupported spell');
  next.mana -= spell.mana;
  next.castThisRound = true;
  next.log.push({ type: 'spell', id: spell.id, targetId });
  finishIfDecided(next);
  validateBattle(next);
  return next;
}

export function retreat(battle) {
  if (!battle || battle.status !== 'ACTIVE') throw new Error('Battle is not active');
  const next = clone(battle);
  next.status = 'RESOLVED';
  next.pendingSettlement = true;
  next.outcome = { winner: 'retreat', practice: next.practice, reward: false };
  next.log.push({ type: 'retreat' });
  validateBattle(next);
  return next;
}

function nextRound(battle) {
  battle.round += 1;
  battle.castThisRound = false;
  for (const stack of battle.stacks) {
    stack.acted = false;
    stack.waited = false;
    stack.retaliated = false;
    stack.defending = false;
  }
  battle.queue = turnOrder(battle);
}

function finishIfDecided(battle) {
  const players = living(battle.stacks, 'p').length;
  const enemies = living(battle.stacks, 'e').length;
  if (players && enemies) return;
  battle.status = 'RESOLVED';
  battle.pendingSettlement = true;
  battle.outcome = { winner: players ? 'p' : enemies ? 'e' : 'none', practice: battle.practice, reward: Boolean(players) };
}

function chooseDamageSpell(battle, spells) {
  const known = (spells ?? []).filter(spell => spell && spell.lv <= 1 + (battle.wisdom || 0) && spell.mana <= (battle.mana ?? 0) && ['arrow', 'bolt', 'fireball'].includes(spell.id));
  if (!known.length || battle.castThisRound) return null;
  const enemies = living(battle.stacks, 'e');
  if (!enemies.length) return null;
  const fireball = known.find(spell => spell.id === 'fireball');
  if (fireball) {
    const clustered = enemies.find(target => enemies.filter(other => chebyshev(other, target) <= 1).length > 1);
    if (clustered) return { spell: fireball, targetId: clustered.id };
  }
  const single = known.find(spell => spell.id === 'bolt') || known.find(spell => spell.id === 'arrow') || fireball;
  if (!single) return null;
  const target = [...enemies].sort((a, b) => (a.count * a.uhp + a.top) - (b.count * b.uhp + b.top))[0];
  return { spell: single, targetId: target.id };
}

export function autoStep(battle, options = {}) {
  if (battle.status !== 'ACTIVE') return clone(battle);
  const id = activeStackId(battle);
  if (!id) return clone(battle);
  const stack = stackById(battle, id);
  if (stack.side === 'p') {
    const spell = chooseDamageSpell(battle, options.spells);
    if (spell) return castSpell(battle, spell.spell, spell.targetId, options.hero?.pow ?? battle.hero?.pow ?? 0);
  }
  const foes = living(battle.stacks, stack.side === 'p' ? 'e' : 'p');
  if (!foes.length) return clone(battle);
  const hero = options.hero ?? battle.hero ?? null;
  const positioned = battle.positioned || stack.x != null;
  if (!positioned) {
    const ranged = stack.rng > 0 && stack.shots > 0;
    return strike(battle, id, foes[0].id, { ...options, hero, ranged, forceMelee: !ranged });
  }
  if (stack.rng > 0 && stack.shots > 0) {
    const shot = foes.filter(enemy => chebyshev(stack, enemy) <= stack.rng).sort((a, b) => chebyshev(stack, a) - chebyshev(stack, b))[0];
    if (shot) return strike(battle, id, shot.id, { hero });
  }
  for (const enemy of foes) {
    if (chebyshev(stack, enemy) === 1) return strike(battle, id, enemy.id, { hero, forceMelee: true });
    const approaches = meleeApproaches(battle, id, enemy.id).filter(Boolean);
    if (approaches.length) return strike(battle, id, enemy.id, { hero, forceMelee: true, approach: approaches[0] });
  }
  const here = Math.min(...foes.map(enemy => chebyshev(stack, enemy)));
  let best = null;
  for (const cell of legalMoves(battle, id)) {
    const dist = Math.min(...foes.map(enemy => chebyshev({ x: cell[0], y: cell[1] }, enemy)));
    if (dist < here && (!best || dist < best.dist)) best = { cell, dist };
  }
  if (best) return move(battle, id, best.cell);
  return defend(battle, id);
}

export function playOut(battle, options = {}) {
  let next = clone(battle);
  let guard = 0;
  while (next.status === 'ACTIVE' && guard < 400) {
    next = autoStep(next, options);
    guard += 1;
  }
  return next;
}

export function autoBattle(spec, options = {}) {
  return playOut(startBattle(spec), options);
}

export function deploy(battle, stack) {
  if (!stack || stack.dead || stack.count <= 0) throw new Error('Dead stack cannot deploy');
  if (battle.stacks.some(item => item.id === stack.id)) throw new Error('Stack is already deployed');
  const next = clone(battle);
  next.stacks.push({ ...normalize(stack), acted: true });
  if (next.stacks.filter(item => !item.dead).length > 6) throw new Error('Too many stacks');
  validateBattle(next);
  return next;
}

function fieldStacks(state, data, sources, cells, side) {
  const fielded = [];
  const unfielded = [];
  sources.forEach((source, index) => {
    if (fielded.length >= cells.length) { unfielded.push(source.id ?? `${side}-extra-${index}`); return; }
    const stats = unitStats(source, data);
    const cell = cells[fielded.length];
    fielded.push({
      id: source.id ?? `${side}${index}`,
      campaignId: side === 'p' ? source.id : null,
      side,
      x: cell[0],
      y: cell[1],
      count: source.count,
      maxCount: source.count,
      atk: stats.atk,
      def: stats.def,
      dmin: stats.dmin,
      dmax: stats.dmax,
      uhp: stats.hp,
      top: stats.hp,
      spd: stats.spd,
      rng: stats.rng,
      shots: stats.shots,
      fly: stats.fly,
      kind: source.kind,
      type: source.type,
      age: source.age,
    });
  });
  return { fielded, unfielded };
}

export function createEncounterBattle(state, data) {
  const pending = state.adventure?.pendingEncounter;
  if (!pending || !String(pending.status).startsWith('UNRESOLVED')) throw new Error('No unresolved encounter');
  const allies = fieldStacks(state, data, state.army.filter(stack => stack.count > 0).slice(0, 3), ALLIED_CELLS, 'p');
  const enemies = fieldStacks(state, data, (pending.pack?.stacks ?? []).map((stack, index) => ({ ...stack, id: `e${index}`, kind: 'creature', rank: stack.rank ?? 0 })), ENEMY_CELLS, 'e');
  if (!allies.fielded.length || !enemies.fielded.length) throw new Error('Incomplete encounter');
  const stats = heroStats(state, data);
  const benched = state.army.filter(stack => stack.count > 0).slice(3).map(stack => stack.id);
  return startBattle({
    id: `battle-${pending.id}`,
    positioned: true,
    practice: 'campaign',
    rngState: state.rngState,
    mana: state.hero.mana,
    wisdom: state.hero.skills.wisdom,
    hero: { atk: stats.atk, def: stats.def, pow: stats.pow, kno: stats.kno, luck: stats.luck, skills: { ...state.hero.skills }, shootBon: 0 },
    stacks: [...allies.fielded, ...enemies.fielded],
    encounterId: pending.id,
    origin: pending.origin ?? [state.adventure.x, state.adventure.y],
    adventureCell: [state.adventure.x, state.adventure.y],
    difficulty: pending.difficulty ?? 1,
    unfielded: [...benched, ...allies.unfielded, ...enemies.unfielded],
  });
}

export function createDuelBattle(state, data) {
  const allies = fieldStacks(state, data, state.army.filter(stack => stack.count > 0).slice(0, 3), ALLIED_CELLS, 'p');
  const pack = [];
  const enemy = { id: 'duel-e', kind: 'creature', type: 'wolf', age: state.age, count: 4, rank: 0, xp: 0 };
  pack.push(enemy);
  const enemies = fieldStacks(state, data, pack, ENEMY_CELLS, 'e');
  const stats = heroStats(state, data);
  return startBattle({
    id: `duel-${state.day}-${state.revision}`,
    positioned: true,
    practice: 'campaign',
    rngState: state.rngState,
    mana: state.hero.mana,
    wisdom: state.hero.skills.wisdom,
    hero: { atk: stats.atk, def: stats.def, pow: stats.pow, kno: stats.kno, luck: stats.luck, skills: { ...state.hero.skills }, shootBon: 0 },
    stacks: [...allies.fielded, ...enemies.fielded],
    encounterId: `duel-${state.day}`,
    difficulty: 1,
  });
}

export function createChallengeBattle(seed, code) {
  if (!Number.isInteger(seed) || seed < 0 || seed > 0xffffffff || typeof code !== 'string' || !code || code.length > 64) throw new Error('Invalid challenge');
  const stack = (id, side, x, y, count, identity) => ({
    id, side, x, y, count, maxCount: count, atk: 4, def: 3, dmin: 2, dmax: 3, uhp: 10, top: 10, spd: 5, rng: 0, shots: 0, fly: 0,
    kind: identity.kind, type: identity.type, age: 0,
  });
  const battle = startBattle({
    id: `challenge-${code}`,
    positioned: true,
    practice: 'challenge',
    rngState: seed >>> 0,
    mana: 0,
    wisdom: 0,
    stacks: [
      stack('ch-p', 'p', 1, 8, 6, { kind: 'role', type: 'melee' }),
      stack('ch-e', 'e', 5, 1, 4, { kind: 'creature', type: 'wolf' }),
    ],
    difficulty: 1,
  });
  battle.challenge = { schema: 1, scenarioId: 'duel-v1', seed: seed >>> 0, label: code };
  return battle;
}

export function createSkirmishBattle(state) {
  const stack = (id, side, x, y, count, identity) => ({
    id, side, x, y, count, maxCount: count, atk: 4, def: 3, dmin: 2, dmax: 3, uhp: 10, top: 10, spd: 5, rng: 0, shots: 0, fly: 0,
    kind: identity.kind, type: identity.type, age: state.age,
  });
  return startBattle({
    id: `skirmish-${state.day}-${state.revision}`,
    positioned: true,
    practice: 'skirmish',
    rngState: state.rngState,
    mana: 0,
    wisdom: 0,
    stacks: [
      stack('sk-p', 'p', 1, 8, 6, { kind: 'role', type: 'melee' }),
      stack('sk-e', 'e', 5, 1, 4, { kind: 'creature', type: 'wolf' }),
    ],
    difficulty: 0,
  });
}
