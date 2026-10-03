import test from 'node:test';
import assert from 'node:assert/strict';
import data from '../src/data/reference-data.json' with { type: 'json' };
import contract from '../src/data/implementation-contract.json' with { type: 'json' };
import { newCampaign, validate, command } from '../src/core/campaign.js';
import { adventureMap, isOpen, routeCost } from '../src/core/navigation.js';
import { decode, encode } from '../src/core/save.js';

const fresh = () => newCampaign(contract, data, 1000);
const act = (state, id, type, payload, now = 1000) => command(state, { id, type, payload }, now, data);

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
  const map = adventureMap(contract.geometry.adventure);
  const approach = contract.geometry.adventure.sites.find(site => site.id === 'town').approach;
  let state = act(fresh(), 'enter', 'ENTER_ADVENTURE');
  const start = [state.adventure.x, state.adventure.y];
  const queue = [{ cell: start, path: [], cost: 0 }];
  const seen = new Set();
  let path;
  while (queue.length) {
    queue.sort((a, b) => a.cost - b.cost);
    const node = queue.shift();
    const key = node.cell.join(',');
    if (seen.has(key)) continue;
    seen.add(key);
    if (key === approach.join(',')) { path = node; break; }
    for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) {
      if (!dx && !dy) continue;
      const step = [node.cell[0] + dx, node.cell[1] + dy];
      try {
        const next = [...node.path, step];
        const cost = routeCost(map, start, next).cost;
        if (cost <= 5) queue.push({ cell: step, path: next, cost });
      } catch { /* closed cells are not candidates */ }
    }
  }
  state = act(state, 'to-town', 'MOVE', { path: path.path });
  assert.equal(state.adventure.moves, 1);
  const returned = act(state, 'return', 'RETURN_TOWN');
  assert.equal(returned.adventure.moves, 1);
  assert.equal(returned.adventure.atTown, true);
  const reopened = act(returned, 'again', 'ENTER_ADVENTURE');
  assert.equal(reopened.adventure.moves, 1);
  const loaded = decode(encode(reopened, data), data);
  assert.equal(loaded.adventure.moves, 1);
  assert.deepEqual(loaded.adventure.visited, reopened.adventure.visited);
  const ended = act(loaded, 'dawn', 'END_DAY');
  assert.equal(ended.day, 2);
  assert.equal(ended.adventure.moves, 5);
  assert.equal(ended.resources.food, 250);
  assert.ok(data.WEATHER[ended.weather]);
});

test('illegal routes and unresolved guards do not spend movement or reroll', () => {
  const map = adventureMap(contract.geometry.adventure);
  let state = act(fresh(), 'enter', 'ENTER_ADVENTURE');
  const before = structuredClone(state);
  assert.throws(() => act(state, 'bad-route', 'MOVE', { path: [[4, 5]] }));
  assert.deepEqual(state, before);
  const guard = [...map.guards][0].split(',').map(Number);
  let after;
  for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) {
    if (isOpen(map, guard[0] + dx, guard[1] + dy)) after = [guard[0] + dx, guard[1] + dy];
  }
  state.adventure = { x: guard[0], y: guard[1], moves: 5, visited: [`${guard[0]},${guard[1]}`], resolvedGuards: [], pendingEncounter: { id: 'guard-open', cell: guard, status: 'UNRESOLVED_COMBAT_BLOCKED' }, atTown: false };
  const held = structuredClone(state);
  assert.throws(() => act(state, 'leave-guard', 'MOVE', { path: [after] }), /Unresolved encounter/);
  assert.deepEqual(state, held);
  const approach = [guard[0] - 0, guard[1]];
  let origin;
  for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) {
    const cell = [guard[0] + dx, guard[1] + dy];
    if ((dx || dy) && isOpen(map, cell[0], cell[1]) && !(dx && dy)) origin = cell;
  }
  state = act(fresh(), 'enter-2', 'ENTER_ADVENTURE');
  state.adventure.x = origin[0];
  state.adventure.y = origin[1];
  state.adventure.moves = 5;
  const bypass = [guard, after].filter(cell => cell.join(',') !== origin.join(','));
  const untouched = structuredClone(state);
  assert.throws(() => act(state, 'bypass', 'MOVE', { path: bypass }), /Unresolved guard/);
  assert.deepEqual(state, untouched);
  const stopped = act(state, 'stop', 'MOVE', { path: [guard] });
  assert.equal(stopped.adventure.moves, 4);
  assert.deepEqual(stopped.adventure.pendingEncounter.cell, guard);
  assert.deepEqual(stopped.adventure.pendingEncounter.origin, origin);
  const pack = structuredClone(stopped.adventure.pendingEncounter.pack);
  const reloaded = decode(encode(stopped, data), data);
  assert.deepEqual(reloaded.adventure.pendingEncounter.pack, pack);
  assert.throws(() => act(reloaded, 'again', 'MOVE', { path: [after] }));
  assert.deepEqual(reloaded.adventure.pendingEncounter.pack, pack);
  assert.deepEqual(act(stopped, 'stop', 'MOVE', { path: [guard] }), stopped);
});
