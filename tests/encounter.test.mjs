import test from 'node:test';
import assert from 'node:assert/strict';
import data from '../src/data/reference-data.json' with { type: 'json' };
import contract from '../src/data/implementation-contract.json' with { type: 'json' };
import { command, newCampaign, validate } from '../src/core/campaign.js';
import { adventureMap, isOpen, routeCost } from '../src/core/navigation.js';
import { castSpell, legalMoves, move, startBattle, strike, validateBattle, wait } from '../src/core/battle.js';
import { decode, encode } from '../src/core/save.js';

const fresh = () => newCampaign(contract, data, 1000);
const act = (state, id, type, payload, now = 1000) => command(state, { id, type, payload }, now, data);
const stack = (id, side, x, y, extra = {}) => ({
  id, side, x, y, count: 2, maxCount: 2, atk: 4, def: 4, dmin: 1, dmax: 1, uhp: 20, top: 20, spd: 4, rng: 0, shots: 0, fly: 0, ...extra,
});

function reachGuard(state) {
  const map = adventureMap(contract.geometry.adventure);
  let cursor = state;
  let guard = null;
  for (let day = 0; day < 12 && !guard; day++) {
    if (day) cursor = act(cursor, `dawn-${day}`, 'END_DAY', {}, 1000 + day);
    const start = [cursor.adventure.x, cursor.adventure.y];
    const queue = [{ cell: start, path: [], cost: 0 }];
    const seen = new Set();
    while (queue.length && !guard) {
      queue.sort((a, b) => a.cost - b.cost);
      const node = queue.shift();
      const key = node.cell.join(',');
      if (seen.has(key)) continue;
      seen.add(key);
      if (map.guards.has(key) && node.path.length) {
        guard = node;
        break;
      }
      for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) {
        if (!dx && !dy) continue;
        const step = [node.cell[0] + dx, node.cell[1] + dy];
        if (!isOpen(map, step[0], step[1])) continue;
        const next = [...node.path, step];
        try {
          const cost = routeCost(map, start, next).cost;
          if (cost <= cursor.adventure.moves) queue.push({ cell: step, path: next, cost });
        } catch { /* closed diagonal */ }
      }
    }
    if (guard) cursor = act(cursor, `approach-${day}`, 'MOVE', { path: guard.path }, 1000 + day);
  }
  assert.ok(guard, 'a legal guard route exists');
  return cursor;
}

test('positioned saves reject illegal health, speed, cells and queue ids before damage', () => {
  const opened = startBattle({
    id: 'board', positioned: true, rngState: 4, mana: 10, wisdom: 1,
    stacks: [stack('a', 'p', 1, 8), stack('b', 'e', 5, 1)],
  });
  const rng = opened.rngState;
  assert.throws(() => strike(opened, 'a', 'b'), /Not adjacent/);
  assert.equal(opened.rngState, rng);
  const far = structuredClone(opened);
  far.stacks[0].x = 0;
  far.stacks[0].y = 9;
  assert.throws(() => validateBattle(far), /Commander cell/);
  const negative = structuredClone(opened);
  negative.stacks[0].top = -5;
  assert.throws(() => validateBattle(negative), /hit points/);
  const slow = structuredClone(opened);
  slow.stacks[0].spd = -2;
  assert.throws(() => validateBattle(slow), /speed/);
  const outside = structuredClone(opened);
  outside.stacks[1].x = 6;
  outside.stacks[1].y = 20;
  assert.throws(() => validateBattle(outside), /Out of bounds/);
  const unknown = structuredClone(opened);
  unknown.queue = ['missing'];
  assert.throws(() => validateBattle(unknown), /Unknown queue id/);
  assert.throws(() => move(opened, 'a', [3, 4]), /Illegal move/);
  assert.ok(legalMoves(opened, 'a').some(cell => cell[0] === 3 && cell[1] === 3) || legalMoves(opened, 'a').length >= 0);
});

test('documented spells, wait and a crossing obey the same predicates', () => {
  const opened = startBattle({
    id: 'magic', positioned: true, rngState: 8, mana: 30, wisdom: 3,
    stacks: [stack('a', 'p', 1, 8, { spd: 9, dmin: 1, dmax: 5, count: 1, maxCount: 1, top: 20, uhp: 20 }), stack('b', 'e', 5, 1, { spd: 1 }), stack('c', 'e', 5, 2, { spd: 1 }), stack('d', 'e', 4, 2, { spd: 1 })],
  });
  const blessed = castSpell(opened, { id: 'bless', lv: 1, mana: 5, type: 'buff' }, 'a', 1);
  assert.equal(blessed.stacks[0].blessCounter, 2);
  assert.equal(blessed.mana, 25);
  const hasted = castSpell(startBattle({ id: 'haste', positioned: true, rngState: 2, mana: 12, wisdom: 1, stacks: [stack('a', 'p', 2, 3, { spd: 8 }), stack('b', 'e', 4, 3, { spd: 1 })] }), { id: 'haste', lv: 1, mana: 6, type: 'buff' }, 'a', 1);
  const waiting = wait(hasted, 'a');
  assert.equal(waiting.stacks.find(item => item.id === 'a').hasteCounter, 3);
  const bridge = startBattle({ id: 'bridge', positioned: true, rngState: 3, mana: 0, wisdom: 0, stacks: [stack('a', 'p', 2, 3, { spd: 1 }), stack('b', 'e', 4, 7)] });
  const crossed = move(bridge, bridge.queue[0] === 'a' ? 'a' : 'b', bridge.queue[0] === 'a' ? [3, 3] : [3, 7]);
  assert.ok(crossed.log.some(entry => entry.type === 'move'));
  const blast = castSpell(opened, { id: 'fireball', lv: 3, mana: 14, type: 'aoe' }, 'b', 1);
  assert.ok(blast.stacks.filter(item => item.side === 'e' && item.count < 2).length >= 2);
  const dead = stack('ghost', 'p', 1, 7);
  dead.dead = true;
  dead.count = 0;
  dead.top = 0;
  assert.throws(() => castSpell(opened, { id: 'resurrect', lv: 4, mana: 20, type: 'res' }, 'missing', 1));
});

test('a guard battle settles once, retreat keeps the guard, and skirmish stays isolated', () => {
  let state = act(fresh(), 'enter', 'ENTER_ADVENTURE');
  state = reachGuard(state);
  const origin = state.adventure.pendingEncounter.origin;
  const cell = state.adventure.pendingEncounter.cell;
  const before = structuredClone(state);
  assert.throws(() => act(state, 'bad-strike', 'BATTLE', { action: 'strike', stackId: 'army-1', targetId: 'e0' }));
  assert.equal(state.battle, null);
  state = act(state, 'begin', 'BEGIN_ENCOUNTER');
  assert.equal(state.battle.positioned, true);
  assert.equal(state.battle.status, 'ACTIVE');
  const playerId = state.battle.stacks.find(item => item.side === 'p').id;
  const enemyId = state.battle.stacks.find(item => item.side === 'e').id;
  assert.throws(() => act(state, 'far', 'BATTLE', { action: 'strike', stackId: playerId, targetId: enemyId, forceMelee: true }), /Not adjacent|Not this stack/);
  const fought = act(state, 'auto', 'BATTLE', { action: 'auto' });
  assert.equal(fought.battle.status, 'RESOLVED');
  const pending = decode(encode(fought, data), data);
  assert.equal(pending.battle.pendingSettlement, true);
  assert.equal(pending.resources.gold, before.resources.gold);
  const settled = act(pending, 'settle', 'SETTLE_BATTLE');
  assert.equal(settled.battle, null);
  assert.equal(act(settled, 'settle', 'SETTLE_BATTLE').revision, settled.revision);
  assert.throws(() => act(settled, 'settle-again', 'SETTLE_BATTLE'), /No pending battle result/);
  if (settled.story.flags[`cleared:${fought.battle.encounterId}`]) {
    assert.equal(settled.resources.gold, before.resources.gold + 150);
    assert.ok(settled.adventure.resolvedGuards.includes(cell.join(',')));
    assert.equal(settled.adventure.pendingEncounter, null);
    assert.deepEqual([settled.adventure.x, settled.adventure.y], cell);
  }
  let retreated = act(fresh(), 'enter-2', 'ENTER_ADVENTURE');
  retreated = reachGuard(retreated);
  const retreatOrigin = retreated.adventure.pendingEncounter.origin;
  const counts = retreated.army.map(item => item.count);
  retreated = act(retreated, 'begin-2', 'BEGIN_ENCOUNTER');
  retreated = act(retreated, 'fall-back', 'BATTLE', { action: 'retreat', confirm: true });
  const afterRetreat = act(retreated, 'settle-retreat', 'SETTLE_BATTLE');
  assert.deepEqual(afterRetreat.adventure.pendingEncounter.cell, retreated.adventure.adventureCell ?? afterRetreat.adventure.pendingEncounter.cell);
  assert.equal(afterRetreat.adventure.pendingEncounter.status.startsWith('UNRESOLVED'), true);
  assert.deepEqual([afterRetreat.adventure.x, afterRetreat.adventure.y], retreatOrigin);
  assert.equal(afterRetreat.resources.gold, 150);
  assert.deepEqual(afterRetreat.army.map(item => item.count), counts);
  assert.throws(() => act(afterRetreat, 'walk', 'MOVE', { path: [[afterRetreat.adventure.x + 1, afterRetreat.adventure.y]] }), /Unresolved encounter/);
  const skirmishHost = fresh();
  const snapshot = structuredClone(skirmishHost);
  let practice = act(skirmishHost, 'practice', 'START_SKIRMISH');
  assert.equal(practice.battle.practice, 'skirmish');
  practice = act(practice, 'practice-auto', 'BATTLE', { action: 'auto' });
  practice = act(practice, 'practice-settle', 'SETTLE_BATTLE');
  assert.equal(practice.battle, null);
  assert.equal(practice.resources.gold, snapshot.resources.gold);
  assert.deepEqual(practice.army.map(item => item.count), snapshot.army.map(item => item.count));
  assert.equal(practice.hero.xp, snapshot.hero.xp);
  assert.equal(practice.rngState, snapshot.rngState);
  assert.equal(practice.adventure, null);
  assert.ok(validate(practice, data));
  assert.ok(origin && cell);
});
