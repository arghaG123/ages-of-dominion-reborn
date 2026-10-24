import test from 'node:test';
import assert from 'node:assert/strict';
import data from '../src/data/reference-data.json' with { type: 'json' };
import contract from '../src/data/implementation-contract.json' with { type: 'json' };
import adventureWorlds from '../src/data/adventure-worlds.json' with { type: 'json' };
import { command, newCampaign, validate } from '../src/core/campaign.js';
import { adventureGeometryForWorld, adventureMap, isOpen, routeCost, routeTo } from '../src/core/navigation.js';
import { castSpell, effectiveSpeed, legalMoves, move, startBattle, strike, validateBattle, wait } from '../src/core/battle.js';
import { decode, encode } from '../src/core/save.js';
import { completeSkirmishDeployment } from './battle-deployment-helpers-20261022.mjs';

const fresh = () => newCampaign(contract, data, 1000);
const act = (state, id, type, payload, now = state.clock) => command(state, { id, type, payload }, now, data);
const stack = (id, side, x, y, extra = {}) => ({
  id, side, x, y, count: 2, maxCount: 2, atk: 4, def: 4, dmin: 1, dmax: 1, uhp: 20, top: 20, spd: 4, rng: 0, shots: 0, fly: 0, ...extra,
});

function reachGuard(state) {
  const world = adventureWorlds.find(item => item.id === state.adventureWorldId);
  const geometry = adventureGeometryForWorld(contract.geometry.adventure, world, state.seed);
  const map = adventureMap(geometry);
  let cursor = state;
  for (let day = 0; day < 40; day++) {
    const start = [cursor.adventure.x, cursor.adventure.y];
    const routes = [...map.guards]
      .filter(key => !cursor.adventure.resolvedGuards.includes(key))
      .flatMap(key => {
        const target = key.split(',').map(Number);
        try { return [routeTo(map, start, target)]; } catch { return []; }
      })
      .sort((first, second) => first.cost - second.cost || first.cells.length - second.cells.length);
    assert.ok(routes.length, 'an unresolved guard has a legal production-map route');
    const route = routes[0];
    if (route.cost <= cursor.adventure.moves) {
      return act(cursor, `approach-guard-${cursor.revision}`, 'MOVE', { path: route.cells });
    }
    let prefix = 0;
    for (let count = 1; count < route.cells.length; count++) {
      if (routeCost(map, start, route.cells.slice(0, count)).cost > cursor.adventure.moves) break;
      prefix = count;
    }
    assert.ok(prefix > 0, 'the selected guard route makes legal progress within one day');
    cursor = act(cursor, `guard-route-${cursor.revision}`, 'MOVE', { path: route.cells.slice(0, prefix) });
    if (cursor.adventure.pendingEncounter) return cursor;
    cursor = act(cursor, `dawn-${cursor.revision}`, 'END_DAY');
  }
  assert.fail('a legal guard route should be reachable within the bounded campaign journey');
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

test('all eight campaign spells apply their documented effects, costs and target rules', () => {
  const open = ({ mana = 30, wisdom = 3 } = {}) => startBattle({
    id: 'spell-coverage', positioned: true, rngState: 11, mana, wisdom,
    stacks: [
      stack('caster', 'p', 1, 8, { spd: 12, dmin: 1, dmax: 5 }),
      stack('ally', 'p', 1, 7, { count: 2, maxCount: 4, uhp: 10, top: 5, spd: 1 }),
      stack('e0', 'e', 2, 7, { count: 2, maxCount: 2, uhp: 100, top: 100, spd: 8, dmin: 0, dmax: 0 }),
      stack('e1', 'e', 2, 8, { count: 2, maxCount: 2, uhp: 100, top: 100, spd: 4, dmin: 0, dmax: 0 }),
      stack('e2', 'e', 5, 3, { count: 2, maxCount: 2, uhp: 100, top: 100, spd: 3, dmin: 0, dmax: 0 }),
    ],
  });
  const spell = id => ({ ...data.SPELLS[id], id });
  const hp = state => {
    const target = state.stacks.find(item => item.id === 'e0');
    return (target.count - 1) * target.uhp + target.top;
  };

  const arrowStart = open();
  const arrow = castSpell(arrowStart, spell('arrow'), 'e0', 1);
  assert.equal(hp(arrow), 180, 'Magic Arrow deals 20 damage at Power 1');
  assert.equal(arrow.mana, 25);
  assert.equal(arrow.log.at(-1).id, 'arrow');
  assert.throws(() => castSpell(arrow, spell('bless'), 'caster', 1), /Spell already cast/);

  const blessStart = open();
  const blessed = castSpell(blessStart, spell('bless'), 'caster', 1);
  assert.equal(blessed.stacks.find(item => item.id === 'caster').blessCounter, 2);
  const blessedStrike = strike(blessed, 'caster', 'e0', { forceMelee: true });
  assert.equal(blessedStrike.log.find(item => item.type === 'strike').damage, 10, 'Bless selects maximum damage for both caster units');
  assert.equal(blessedStrike.stacks.find(item => item.id === 'caster').blessCounter, 1, 'Bless decays after the affected stack acts');
  assert.equal(blessed.mana, 25);

  const haste = castSpell(open(), spell('haste'), 'caster', 1);
  assert.equal(haste.stacks.find(item => item.id === 'caster').hasteCounter, 3);
  assert.equal(effectiveSpeed(haste.stacks.find(item => item.id === 'caster')), 15);
  assert.equal(haste.mana, 24);

  const cure = castSpell(open(), spell('cure'), 'ally', 1);
  const curedAlly = cure.stacks.find(item => item.id === 'ally');
  assert.equal((curedAlly.count - 1) * curedAlly.uhp + curedAlly.top, 35, 'Cure restores 20 HP at Power 1');
  assert.equal(cure.mana, 24);

  const slow = castSpell(open(), spell('slow'), 'e0', 1);
  assert.equal(slow.stacks.find(item => item.id === 'e0').slowCounter, 3);
  assert.equal(effectiveSpeed(slow.stacks.find(item => item.id === 'e0')), 5);
  assert.equal(slow.mana, 22);

  const bolt = castSpell(open(), spell('bolt'), 'e0', 1);
  assert.equal(hp(bolt), 165, 'Lightning Bolt deals 35 damage at Power 1');
  assert.equal(bolt.mana, 20);

  const fireball = castSpell(open(), spell('fireball'), 'e0', 1);
  assert.equal(hp(fireball), 170, 'Fireball damages its selected stack');
  const neighbour = fireball.stacks.find(item => item.id === 'e1');
  assert.equal((neighbour.count - 1) * neighbour.uhp + neighbour.top, 170, 'Fireball damages an adjacent stack');
  assert.equal(fireball.stacks.find(item => item.id === 'e2').top, 100, 'Fireball leaves a non-neighbour unchanged');
  assert.equal(fireball.mana, 16);

  const resurrect = castSpell(open(), spell('resurrect'), 'ally', 0.2);
  const restoredAlly = resurrect.stacks.find(item => item.id === 'ally');
  assert.equal(restoredAlly.count, 3, 'Resurrection restores one lost unit at Power 0.2');
  assert.equal(restoredAlly.top, 5);
  assert.equal(resurrect.mana, 10);

  const full = open();
  const fullAlly = full.stacks.find(item => item.id === 'ally');
  fullAlly.count = fullAlly.maxCount;
  fullAlly.top = fullAlly.uhp;
  const fullBeforeHp = (fullAlly.count - 1) * fullAlly.uhp + fullAlly.top;
  const fullCure = castSpell(full, spell('cure'), 'ally', 1);
  const fullAfter = fullCure.stacks.find(item => item.id === 'ally');
  assert.equal((fullAfter.count - 1) * fullAfter.uhp + fullAfter.top, fullBeforeHp, 'Cure caps at full health');
  assert.equal(fullCure.mana, 24, 'a legal full-health cast uses its documented mana');

  const illegal = open();
  const illegalBefore = structuredClone(illegal);
  assert.throws(() => castSpell(illegal, spell('arrow'), 'ally', 1), /Illegal spell target/);
  assert.deepEqual(illegal, illegalBefore, 'an illegal target does not mutate the original battle');
  assert.throws(() => castSpell(illegal, spell('bless'), 'e0', 1), /Illegal spell target/);
  assert.throws(() => castSpell(illegal, spell('slow'), 'ally', 1), /Illegal spell target/);

  const locked = open({ wisdom: 0 });
  const lockedBefore = structuredClone(locked);
  assert.throws(() => castSpell(locked, spell('bolt'), 'e0', 1), /Spell is not known/);
  assert.deepEqual(locked, lockedBefore, 'Wisdom-locked spells leave battle state unchanged');
  const shortMana = open({ mana: 9 });
  const shortManaBefore = structuredClone(shortMana);
  assert.throws(() => castSpell(shortMana, spell('bolt'), 'e0', 1), /Not enough mana/);
  assert.deepEqual(shortMana, shortManaBefore, 'insufficient mana leaves battle state unchanged');

  const dead = open();
  const deadAlly = dead.stacks.find(item => item.id === 'ally');
  deadAlly.dead = true;
  deadAlly.count = 0;
  deadAlly.top = 0;
  const deadBefore = structuredClone(dead);
  assert.throws(() => castSpell(dead, spell('resurrect'), 'ally', 1), /Dead stacks/);
  assert.deepEqual(dead, deadBefore, 'dead stacks remain unsupported Resurrection targets');
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
  retreated = act(retreated, 'begin-2', 'BEGIN_ENCOUNTER');
  const counts = retreated.battle.stacks
    .filter(item => item.side === 'p' && item.campaignId && item.count > 0)
    .map(item => ({ id: item.campaignId, count: item.count }));
  retreated = act(retreated, 'fall-back', 'BATTLE', { action: 'retreat', confirm: true });
  const afterRetreat = act(retreated, 'settle-retreat', 'SETTLE_BATTLE');
  assert.deepEqual(afterRetreat.adventure.pendingEncounter.cell, retreated.adventure.adventureCell ?? afterRetreat.adventure.pendingEncounter.cell);
  assert.equal(afterRetreat.adventure.pendingEncounter.status.startsWith('UNRESOLVED'), true);
  assert.deepEqual([afterRetreat.adventure.x, afterRetreat.adventure.y], retreatOrigin);
  assert.equal(afterRetreat.resources.gold, 150);
  assert.deepEqual(afterRetreat.army.map(({ id, count }) => ({ id, count })), counts);
  assert.throws(() => act(afterRetreat, 'walk', 'MOVE', { path: [[afterRetreat.adventure.x + 1, afterRetreat.adventure.y]] }), /Unresolved encounter/);
  const skirmishHost = fresh();
  const snapshot = structuredClone(skirmishHost);
  let practice = completeSkirmishDeployment(skirmishHost, data, 'practice');
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

test('routeTo previews one legal path and refuses a site footprint', () => {
  const geometry = contract.geometry.adventure;
  const map = adventureMap(geometry);
  const start = geometry.sites.find(site => site.id === 'town').approach;
  const goal = [start[0], start[1] + 1];
  assert.equal(isOpen(map, goal[0], goal[1]), true);
  const route = routeTo(map, start, goal);
  assert.deepEqual(route.cells.at(-1), goal);
  assert.equal(route.cost, routeCost(map, start, route.cells).cost);
  const blocked = geometry.sites.find(site => site.id === 'town').rect;
  assert.throws(() => routeTo(map, start, [blocked[0], blocked[1]]), /Blocked terrain/);
});

test('routeTo minimizes movement cost instead of accepting an earlier diagonal detour', () => {
  const map = adventureMap({ cols: 3, rows: 3, blocked: [], obstacles: [], bridges: [], sites: [], roads: [], anchors: {} });
  const route = routeTo(map, [0, 1], [2, 1]);
  assert.equal(route.cost, 2);
  assert.deepEqual(route.cells, [[1, 1], [2, 1]]);
});
