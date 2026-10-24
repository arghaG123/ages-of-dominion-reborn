import test from 'node:test';
import assert from 'node:assert/strict';
import data from '../src/data/reference-data.json' with { type: 'json' };
import contract from '../src/data/implementation-contract.json' with { type: 'json' };
import adventureWorlds from '../src/data/adventure-worlds.json' with { type: 'json' };
import { newCampaign, validate, command } from '../src/core/campaign.js';
import { adventureGeometryForWorld, adventureMap, isOpen, routeCost, routeTo, stepCost } from '../src/core/navigation.js';
import { decode, encode } from '../src/core/save.js';

const fresh = () => newCampaign(contract, data, 1000);
const act = (state, id, type, payload, now = state.clock) => command(state, { id, type, payload }, now, data);
const selectedGeometry = state => adventureGeometryForWorld(
  contract.geometry.adventure,
  adventureWorlds.find(world => world.id === state.adventureWorldId),
  state.seed,
);

function travelTo(state, map, target, label) {
  let cursor = state;
  for (let day = 0; day < 20; day++) {
    const start = [cursor.adventure.x, cursor.adventure.y];
    const route = routeTo(map, start, target);
    if (route.cost <= cursor.adventure.moves) {
      return act(cursor, `${label}-${cursor.revision}`, 'MOVE', { path: route.cells });
    }
    let prefix = 0;
    for (let count = 1; count < route.cells.length; count++) {
      if (routeCost(map, start, route.cells.slice(0, count)).cost > cursor.adventure.moves) break;
      prefix = count;
    }
    assert.ok(prefix > 0, `${label} route can progress within the daily movement limit`);
    cursor = act(cursor, `${label}-step-${cursor.revision}`, 'MOVE', { path: route.cells.slice(0, prefix) });
    cursor = act(cursor, `${label}-dawn-${cursor.revision}`, 'END_DAY');
  }
  assert.fail(`${label} should be reachable in a bounded natural route`);
}

test('domain validation rejects the probed illegal saves', () => {
  const changes = {
    negativeArmyCount: state => { state.army[0].count = -5; },
    unknownArmyRole: state => { state.army[0].type = 'invented'; },
    unknownTowerFamily: state => { state.towers[0].fam = 'invented'; },
    invalidDay: state => { state.day = -1; },
    unknownPlotID: state => { state.plots[1].id = 'invented'; },
    outOfBoundsJourney: state => { state.adventure = { x: 999, y: 999, moves: 5, visited: [], resolvedGuards: [], pendingEncounter: null, atTown: false }; },
    overCapacityMana: state => { state.hero.mana = 1e9; },
    equipmentWrongSlot: state => { state.hero.equip.weapon = { id: 'wrong-slot', kind: 'gear', slot: 'boots', age: 0, quality: 0 }; },
    arbitraryBattlePayload: state => { state.battle = { invented: true }; },
  };
  for (const change of Object.values(changes)) {
    const state = fresh();
    change(state);
    assert.throws(() => validate(state, data));
  }
});

test('returning and reloading keep the remaining movement until End Day', () => {
  let state = act(fresh(), 'enter', 'ENTER_ADVENTURE');
  const start = [state.adventure.x, state.adventure.y];
  const geometry = selectedGeometry(state);
  const map = adventureMap(geometry);
  const approach = geometry.sites.find(site => site.id === 'town').approach;
  assert.deepEqual(start, geometry.anchors.hero.map(Math.floor), 'the selected world places the hero at its registered safe start');
  assert.doesNotThrow(() => routeTo(map, start, approach), 'the production town approach is reachable from the safe start');
  state = travelTo(state, map, approach, 'reach-town-approach');
  state = act(state, 'town-dawn', 'END_DAY');
  assert.deepEqual([state.adventure.x, state.adventure.y], approach);
  const townMoves = state.adventure.moves;
  const directions = [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]];
  const outbound = directions.map(([dx, dy]) => [approach[0] + dx, approach[1] + dy]).find(cell => {
    if (map.guards.has(cell.join(','))) return false;
    try {
      const cost = stepCost(map, approach, cell);
      return cost + routeTo(map, cell, approach).cost <= townMoves;
    } catch { return false; }
  });
  assert.ok(outbound, 'the town entrance has an affordable adjacent cell and return route');
  const outboundCost = stepCost(map, approach, outbound);
  state = act(state, 'away-from-town', 'MOVE', { path: [outbound] });
  const returnRoute = routeTo(map, outbound, approach);
  state = act(state, 'to-town', 'MOVE', { path: returnRoute.cells });
  assert.equal(state.adventure.moves, townMoves - outboundCost - returnRoute.cost);
  const returned = act(state, 'return', 'RETURN_TOWN');
  assert.equal(returned.adventure.moves, state.adventure.moves);
  assert.equal(returned.adventure.atTown, true);
  const reopened = act(returned, 'again', 'ENTER_ADVENTURE');
  assert.equal(reopened.adventure.moves, state.adventure.moves);
  const loaded = decode(encode(reopened, data), data);
  assert.equal(loaded.adventure.moves, state.adventure.moves);
  assert.deepEqual(loaded.adventure.visited, reopened.adventure.visited);
  const ended = act(loaded, 'dawn', 'END_DAY');
  assert.equal(ended.day, loaded.day + 1);
  assert.equal(ended.adventure.moves, 5);
  assert.equal(ended.resources.food, 250);
  assert.ok(data.WEATHER[ended.weather]);
});

test('illegal routes and unresolved guards do not spend movement or reroll', () => {
  let state = act(fresh(), 'enter', 'ENTER_ADVENTURE');
  const geometry = selectedGeometry(state);
  const map = adventureMap(geometry);
  const before = structuredClone(state);
  assert.throws(() => act(state, 'bad-route', 'MOVE', { path: [[state.adventure.x + 2, state.adventure.y]] }));
  assert.deepEqual(state, before);
  const guard = [...map.guards][0].split(',').map(Number);
  const adjacent = [];
  for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) {
    if (!dx && !dy) continue;
    const cell = [guard[0] + dx, guard[1] + dy];
    if (!isOpen(map, cell[0], cell[1]) || map.guards.has(cell.join(','))) continue;
    try { stepCost(map, cell, guard); adjacent.push(cell); } catch { /* closed corner */ }
  }
  let pair;
  for (const origin of adjacent) for (const after of adjacent) {
    if (origin.join(',') === after.join(',')) continue;
    try { stepCost(map, guard, after); pair ??= { origin, after }; } catch { /* closed corner */ }
  }
  assert.ok(pair, 'the chosen guard has a legal entry and exit pair');
  const { origin, after } = pair;
  state.adventure.x = guard[0];
  state.adventure.y = guard[1];
  state.adventure.moves = 5;
  state.adventure.visited = [`${guard[0]},${guard[1]}`];
  state.adventure.pendingEncounter = { id: 'guard-open', cell: guard, status: 'UNRESOLVED_COMBAT_BLOCKED' };
  const held = structuredClone(state);
  assert.throws(() => act(state, 'leave-guard', 'MOVE', { path: [after] }), /Unresolved encounter/);
  assert.deepEqual(state, held);
  state = act(fresh(), 'enter-2', 'ENTER_ADVENTURE');
  state.adventure.x = origin[0];
  state.adventure.y = origin[1];
  state.adventure.moves = 5;
  const bypass = [guard, after];
  const untouched = structuredClone(state);
  assert.throws(() => act(state, 'bypass', 'MOVE', { path: bypass }), /Unresolved guard/);
  assert.deepEqual(state, untouched);
  const stopped = act(state, 'stop', 'MOVE', { path: [guard] });
  assert.equal(stopped.adventure.moves, 5 - stepCost(map, origin, guard));
  assert.deepEqual(stopped.adventure.pendingEncounter.cell, guard);
  assert.deepEqual(stopped.adventure.pendingEncounter.origin, origin);
  const pack = structuredClone(stopped.adventure.pendingEncounter.pack);
  const reloaded = decode(encode(stopped, data), data);
  assert.deepEqual(reloaded.adventure.pendingEncounter.pack, pack);
  assert.throws(() => act(reloaded, 'again', 'MOVE', { path: [after] }));
  assert.deepEqual(reloaded.adventure.pendingEncounter.pack, pack);
  assert.deepEqual(act(stopped, 'stop', 'MOVE', { path: [guard] }), stopped);
});
