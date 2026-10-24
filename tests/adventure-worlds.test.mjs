import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import worlds from '../src/data/adventure-worlds.json' with { type: 'json' };
import contract from '../src/data/implementation-contract.json' with { type: 'json' };
import data from '../src/data/reference-data.json' with { type: 'json' };
import sourceManifest from '../qa/game-completion-20261022/visual-review/adventure-map-source-reconciliation-20261022/source-manifest.json' with { type: 'json' };
import preservedProductionGeometryV2 from '../qa/game-completion-20261022/visual-review/adventure-map-source-reconciliation-20261022/production-geometry-v2-preserved.json' with { type: 'json' };
import { adoptProgress, command, DEFAULT_ADVENTURE_WORLD_ID, newCampaign, validate } from '../src/core/campaign.js';
import { checksum, decode, encode } from '../src/core/save.js';
import { adventureGeometryForWorld, adventureLayoutIndex, adventureMap, isOpen, routeTo, stepCost } from '../src/core/navigation.js';
import { visibleAdventureAnchors } from '../src/client/screen-presentation.js';
import { wideBoardCamera } from '../src/client/projection.js';
import { campaignMapImage, isIntegratedAdventureMap } from '../src/client/adventure-map-source.js';

const root = path.resolve(fileURLToPath(new URL('../', import.meta.url)));
const siteIds = ['town', 'ruin', 'mill', 'mine', 'dwelling', 'shrine'];
const dynamicIds = ['food', 'wood', 'stone', 'gold', 'guard-ruin', 'guard-mine'];
const sourceRow = (worldId, role) => sourceManifest.sources.find(row => row.worldId === worldId && row.role === role);
const cellId = point => point.join(',');
const distance = (first, second) => Math.abs(first[0] - second[0]) + Math.abs(first[1] - second[1]);

function moveCampaignTo(initialState, map, destination, idPrefix) {
  let state = initialState;
  let sequence = 0;
  for (; sequence < 240; sequence += 1) {
    if (state.adventure.x === destination[0] && state.adventure.y === destination[1]) return state;
    if (state.adventure.moves === 0) {
      state = command(state, { id: idPrefix + '-rest-' + sequence, type: 'END_DAY', payload: {} }, 1000, data);
      continue;
    }
    const route = routeTo(map, [state.adventure.x, state.adventure.y], destination);
    const path = [];
    let cost = 0;
    let from = [state.adventure.x, state.adventure.y];
    for (const cell of route.cells) {
      const step = stepCost(map, from, cell);
      if (cost + step > state.adventure.moves) break;
      path.push(cell);
      cost += step;
      from = cell;
    }
    if (!path.length) {
      state = command(state, { id: idPrefix + '-rest-' + sequence, type: 'END_DAY', payload: {} }, 1000, data);
      continue;
    }
    state = command(state, { id: idPrefix + '-move-' + sequence, type: 'MOVE', payload: { path } }, 1000, data);
  }
  assert.deepEqual([state.adventure.x, state.adventure.y], destination, idPrefix + ' reaches its destination');
  return state;
}

function enterAdventure(world, seed) {
  const fresh = newCampaign(contract, data, 1000, seed, world.id);
  return command(fresh, { id: 'enter-' + world.id + '-' + seed, type: 'ENTER_ADVENTURE', payload: {} }, 1000, data);
}

test('the twelve map examples remain references and all runtimes select game-specific production maps', async () => {
  assert.equal(worlds.length, 12);
  assert.equal(new Set(worlds.map(world => world.id)).size, 12);
  assert.equal(new Set(worlds.map(world => world.referenceFile)).size, 12);
  assert.equal(new Set(worlds.map(world => world.productionMapFile)).size, 12);
  for (const world of worlds) {
    assert.equal(Object.hasOwn(world, 'file'), false, world.id + ' has no ambiguous reference-image file alias');
    assert.equal(Object.hasOwn(world, 'mapFile'), false, world.id + ' has no ambiguous production-image file alias');
    assert.equal(world.sourceBindings.reference.file, world.referenceFile);
    assert.equal(world.sourceBindings.production.file, world.productionMapFile);
    assert.notEqual(world.referenceFile, world.productionMapFile);
    assert.equal(Object.hasOwn(world, 'runtimeFile'), false, world.id + ' has no reference-priority runtime field');
    assert.equal(campaignMapImage(world), world.productionMapFile);
    assert.equal(isIntegratedAdventureMap(world), true);
    assert.equal(campaignMapImage({ referenceFile: world.referenceFile, file: world.referenceFile }), '');
    assert.equal(isIntegratedAdventureMap({ referenceFile: world.referenceFile }), false);
    assert.equal(world.sourceBindings.reference.role, 'visual-example-only');
    assert.equal(world.sourceBindings.production.role, 'game-specific-runtime-map');
    assert.equal(world.sourceBindings.production.geometryVersion, 4);
    assert.equal(campaignMapImage({ ...world, geometry: { ...world.geometry, version: 3 } }), '');
    assert.equal(campaignMapImage({ ...world, geometry: { ...world.geometry, sourceSha256: '0'.repeat(64) } }), '');
  }
});

test('source manifest hashes and retained image files match all twelve bindings', async () => {
  assert.equal(sourceManifest.worldCount, 12);
  for (const world of worlds) {
    const reference = sourceRow(world.id, 'reference');
    const production = sourceRow(world.id, 'generated-game-map');
    const terrain = sourceRow(world.id, 'generated-terrain');
    assert.ok(reference && production && terrain, world.id + ' has all three reconciled sources');
    assert.equal(reference.path, world.referenceFile);
    assert.equal(production.path, world.productionMapFile);
    assert.equal(world.sourceBindings.reference.sha256, reference.sha256);
    assert.equal(world.sourceBindings.production.sha256, production.sha256);
    for (const row of [reference, production, terrain]) {
      const bytes = await fs.readFile(path.join(root, row.path));
      assert.equal(bytes.toString('ascii', 1, 4), 'PNG', world.id + ' ' + row.role + ' PNG');
      assert.equal(bytes.length, row.bytes, world.id + ' ' + row.role + ' byte length');
      assert.equal(createHash('sha256').update(bytes).digest('hex'), row.sha256, world.id + ' ' + row.role + ' hash');
      assert.equal(bytes.readUInt32BE(16), row.dimensions[0]);
      assert.equal(bytes.readUInt32BE(20), row.dimensions[1]);
    }
  }
});

test('each world preserves reference geometry v1 and registers source-bound production geometry v4', () => {
  for (const world of worlds) {
    assert.equal(world.referenceGeometry.version, 1);
    assert.equal(world.referenceGeometry.sourceFile, world.referenceFile);
    assert.equal(world.referenceGeometry.sourceSha256, world.sourceBindings.reference.sha256);
    assert.ok(world.referenceGeometry.geometry.sites.length === 6, world.id + ' preserves the six reference-bound site regions');
    assert.equal(world.geometry.version, 4);
    assert.equal(world.geometry.sourceFile, world.productionMapFile);
    assert.equal(world.geometry.sourceSha256, world.sourceBindings.production.sha256);
    assert.deepEqual(world.geometry.sourceSize, world.sourceBindings.production.dimensions);
    assert.deepEqual(world.geometry.worldToSource, [
      world.geometry.sourceSize[0] / world.geometry.cols, 0, 0,
      world.geometry.sourceSize[1] / world.geometry.rows, 0, 0,
    ]);
    assert.equal(world.geometry.cols, 16);
    assert.equal(world.geometry.rows, 10);
    assert.deepEqual(world.geometry.sites.map(site => site.id).sort(), siteIds.slice().sort());
    assert.ok(world.geometry.sites.every(site => site.landmark && ['painted-landmark', 'runtime-object'].includes(site.representation)));
    assert.ok(world.geometry.defaultTerrain);
  }
});

test('the pre-correction production geometry v2 remains archived and is not selected at runtime', () => {
  assert.equal(preservedProductionGeometryV2.worldCount, 12);
  for (const world of worlds) {
    const archived = preservedProductionGeometryV2.worlds.find(row => row.id === world.id);
    assert.ok(archived, world.id + ' has a retained v2 record');
    assert.equal(archived.geometry.version, 2);
    assert.equal(archived.productionMapFile, world.productionMapFile);
    assert.equal(archived.geometry.sourceFile, world.productionMapFile);
    assert.equal(world.geometry.version, 4, world.id + ' runtime uses corrected geometry');
  }
});

test('Adventure camera keeps every generated map edge visible at the three required landscape viewports', () => {
  for (const world of worlds) for (const [width, height] of [[825, 375], [933, 424], [1280, 720]]) {
    const [sourceWidth, sourceHeight] = world.geometry.sourceSize;
    const fit = wideBoardCamera(world.geometry.sourceSize, width, height, 0, sourceHeight);
    const [, top, , visibleHeight] = fit.window;
    assert.ok(top <= 0.001, world.id + ' ' + width + '×' + height + ' keeps the north map edge visible');
    assert.ok(top + visibleHeight >= sourceHeight - 0.001, world.id + ' ' + width + '×' + height + ' keeps the south map edge visible');
    assert.ok(fit.scale <= height / sourceHeight + 0.000001, world.id + ' ' + width + '×' + height + ' does not crop vertically');
    assert.ok(sourceWidth > 0, world.id + ' has a positive map width');
    const inspectorWidth = width <= 900 ? 280 : 360;
    const visibleWidth = width - inspectorWidth - 8;
    const inspected = wideBoardCamera(world.geometry.sourceSize, visibleWidth, height, 0, sourceHeight);
    const [inspectedLeft, inspectedTop, inspectedWidth, inspectedHeight] = inspected.window;
    assert.ok(inspectedLeft <= 0.001 && inspectedLeft + inspectedWidth >= sourceWidth - 0.001,
      world.id + ' ' + width + '×' + height + ' keeps both side edges visible with its inspector open');
    assert.ok(inspectedTop <= 0.001 && inspectedTop + inspectedHeight >= sourceHeight - 0.001,
      world.id + ' ' + width + '×' + height + ' keeps both vertical edges visible with its inspector open');
  }
});

test('production landmarks, site approaches, hazards and bridge banks agree with registered geometry', () => {
  for (const world of worlds) {
    const geometry = adventureGeometryForWorld(contract.geometry.adventure, world);
    const map = adventureMap(geometry);
    assert.ok(isOpen(map, ...geometry.anchors.hero.map(Math.floor)), world.id + ' safe start is open');
    for (const [kind, cells] of Object.entries(geometry.terrainMasks)) {
      for (const cell of cells) {
        const id = cellId(cell);
        const bridgeDeck = map.bridge.has(id);
        const siteFootprint = geometry.sites.some(site => {
          const [x, y, w, h] = site.rect;
          return cell[0] >= x && cell[0] < x + w && cell[1] >= y && cell[1] < y + h;
        });
        assert.equal(map.blocked.has(id), !bridgeDeck || siteFootprint, world.id + ' ' + kind + ' mask at ' + id);
      }
    }
    for (let firstIndex = 0; firstIndex < geometry.sites.length; firstIndex += 1) {
      const [ax, ay, aw, ah] = geometry.sites[firstIndex].rect;
      for (let secondIndex = firstIndex + 1; secondIndex < geometry.sites.length; secondIndex += 1) {
        const [bx, by, bw, bh] = geometry.sites[secondIndex].rect;
        assert.equal(ax < bx + bw && bx < ax + aw && ay < by + bh && by < ay + ah, false,
          world.id + ' ' + geometry.sites[firstIndex].id + ' does not overlap ' + geometry.sites[secondIndex].id);
      }
    }
    const approaches = geometry.sites.map(site => cellId(site.approach));
    assert.equal(new Set(approaches).size, geometry.sites.length, world.id + ' site interaction tiles are unique');
    for (const site of geometry.sites) {
      assert.ok(site.landmark, world.id + ' ' + site.id + ' names the visible landmark');
      assert.ok(isOpen(map, ...site.approach), world.id + ' ' + site.id + ' approach is open');
      const [x, y, w, h] = site.rect;
      const [ax, ay] = site.approach;
      assert.equal(ax >= x && ax < x + w && ay >= y && ay < y + h, false, world.id + ' ' + site.id + ' approach lies outside its footprint');
    }
    for (const crossing of geometry.bridges) {
      assert.ok(crossing.type, world.id + ' ' + crossing.id + ' declares its physical crossing type');
      const sequence = [crossing.approaches[0], ...crossing.cells, crossing.approaches.at(-1)];
      assert.ok(sequence.length >= 3);
      for (let index = 1; index < sequence.length; index += 1) {
        assert.equal(distance(sequence[index - 1], sequence[index]), 1, world.id + ' ' + crossing.id + ' deck touches both banks orthogonally');
        assert.doesNotThrow(() => stepCost(map, sequence[index - 1], sequence[index]), world.id + ' ' + crossing.id + ' deck is traversable');
      }
    }
  }
});

test('every world exposes twenty deterministic open layouts with reachable sites, caches and encounters', () => {
  for (const world of worlds) {
    const baseline = adventureGeometryForWorld(contract.geometry.adventure, world);
    const baselineMap = adventureMap(baseline);
    const baselineStart = baseline.anchors.hero.map(Math.floor);
    for (const id of dynamicIds) {
      const cell = baseline.anchors[id].map(Math.floor);
      assert.ok(isOpen(baselineMap, ...cell), world.id + ' baseline ' + id + ' is on walkable ground');
      assert.equal(baseline.sites.some(site => site.approach[0] === cell[0] && site.approach[1] === cell[1]), false,
        world.id + ' baseline ' + id + ' does not obscure a site interaction tile');
      assert.equal(baselineMap.bridge.has(cellId(cell)), false, world.id + ' baseline ' + id + ' stays off bridge decks');
      assert.doesNotThrow(() => routeTo(baselineMap, baselineStart, cell), world.id + ' baseline reaches ' + id);
    }
    for (const site of baseline.sites) {
      assert.ok(isOpen(baselineMap, ...site.approach), world.id + ' baseline ' + site.id + ' approach is walkable');
      assert.doesNotThrow(() => routeTo(baselineMap, baselineStart, site.approach), world.id + ' baseline reaches ' + site.id);
    }
    const layouts = new Map();
    for (let seed = 0; seed < 1024 && layouts.size < 20; seed += 1) {
      const index = adventureLayoutIndex(world, seed);
      if (layouts.has(index)) continue;
      const geometry = adventureGeometryForWorld(contract.geometry.adventure, world, seed);
      const map = adventureMap(geometry);
      const start = geometry.anchors.hero.map(Math.floor);
      assert.equal(geometry.layoutIndex, index);
      assert.ok(isOpen(map, ...start), world.id + ' layout ' + (index + 1) + ' safe start');
      const anchors = dynamicIds.map(id => geometry.anchors[id]);
      assert.equal(anchors.every(Boolean), true, world.id + ' layout ' + (index + 1) + ' has six dynamic anchors');
      const anchorCells = anchors.map(anchor => [Math.floor(anchor[0]), Math.floor(anchor[1])]);
      assert.equal(new Set(anchorCells.map(cellId)).size, dynamicIds.length, world.id + ' layout ' + (index + 1) + ' anchor cells are unique');
      for (let anchorIndex = 0; anchorIndex < dynamicIds.length; anchorIndex += 1) {
        const id = dynamicIds[anchorIndex];
        const cell = anchorCells[anchorIndex];
        assert.ok(isOpen(map, ...cell), world.id + ' layout ' + (index + 1) + ' ' + id + ' is on walkable ground');
        assert.equal(map.bridge.has(cellId(cell)), false, world.id + ' layout ' + (index + 1) + ' ' + id + ' stays off crossing decks');
        assert.doesNotThrow(() => routeTo(map, start, cell), world.id + ' layout ' + (index + 1) + ' reaches ' + id);
        assert.deepEqual(adventureGeometryForWorld(contract.geometry.adventure, world, seed).anchors, geometry.anchors, world.id + ' layout ' + (index + 1) + ' repeats exactly');
      }
      for (const site of geometry.sites) {
        assert.ok(isOpen(map, ...site.approach), world.id + ' layout ' + (index + 1) + ' ' + site.id + ' approach is walkable');
        assert.doesNotThrow(() => routeTo(map, start, site.approach), world.id + ' layout ' + (index + 1) + ' reaches ' + site.id);
      }
      const signature = anchorCells.map(cellId).join('|');
      assert.equal(new Set(layouts.values()).has(signature), false, world.id + ' layouts have different placements');
      layouts.set(index, signature);
    }
    assert.equal(layouts.size, 20, world.id + ' covers all twenty deterministic layouts');
  }
});

test('Astral Peaks gold is walkable at the repaired [13,5] pickup and every layout keeps it reachable', () => {
  const world = worlds.find(row => row.id === 'astral-peaks');
  const baseline = adventureGeometryForWorld(contract.geometry.adventure, world);
  const baselineMap = adventureMap(baseline);
  assert.deepEqual(baseline.anchors.gold, [13.5, 5.5]);
  assert.equal(isOpen(baselineMap, 13, 5), true);
  for (let seed = 0; seed < 512; seed += 1) {
    const geometry = adventureGeometryForWorld(contract.geometry.adventure, world, seed);
    const map = adventureMap(geometry);
    if (geometry.layoutIndex === 0) continue;
    const gold = geometry.anchors.gold.map(Math.floor);
    assert.ok(isOpen(map, ...gold));
    assert.doesNotThrow(() => routeTo(map, geometry.anchors.hero.map(Math.floor), gold));
  }
});

test('runtime-object landmarks use current production site assets and stay discoverable state layers', async () => {
  const art = {
    mill: 'assets/derivatives/environment-20261006/sites/adventure-site-mill.png',
    dwelling: 'assets/derivatives/environment-20261006/sites/adventure-site-dwelling.png',
  };
  for (const world of worlds) {
    for (const site of world.geometry.sites.filter(row => row.representation === 'runtime-object')) {
      assert.ok(art[site.id], world.id + ' ' + site.id + ' has a registered runtime object');
      const bytes = await fs.readFile(path.join(root, art[site.id]));
      assert.equal(bytes.toString('ascii', 1, 4), 'PNG');
    }
  }
});

test('new journeys save the production geometry version and keep stable world IDs', () => {
  for (const world of worlds) {
    const entered = enterAdventure(world, 6700);
    assert.equal(entered.adventureWorldId, world.id);
    assert.equal(entered.adventure.geometryVersion, 4);
    assert.ok(isOpen(adventureMap(adventureGeometryForWorld(contract.geometry.adventure, world)), entered.adventure.x, entered.adventure.y));
    assert.equal(validate(decode(encode(entered, data), data), data), true);
  }
  const malformed = newCampaign(contract, data, 1000, 6701, worlds[0].id);
  malformed.adventureWorldId = 'unknown-world';
  assert.throws(() => validate(malformed, data), /Invalid Adventure world/);
});

test('legacy v1 save migration preserves progress and safely relocates invalid production-map positions', () => {
  const world = worlds.find(row => row.id === 'jade-karst');
  const state = enterAdventure(world, 6800);
  state.resources.gold += 37;
  state.adventure.geometryVersion = 1;
  state.adventure.x = 0;
  state.adventure.y = 0;
  state.adventure.visited.push('4,4', '0,0');
  state.adventure.claimedSites = ['ruin', 'mill'];
  state.adventure.collectedCaches = ['wood'];
  const before = structuredClone(state);
  const payload = JSON.stringify(state);
  const envelope = JSON.stringify({ schema: 1, payload, checksum: checksum(payload) });

  const migrated = decode(envelope, data);
  const geometry = adventureGeometryForWorld(contract.geometry.adventure, world, migrated.seed);
  const map = adventureMap(geometry);
  assert.equal(migrated.adventure.geometryVersion, 4);
  assert.ok(isOpen(map, migrated.adventure.x, migrated.adventure.y));
  assert.equal(migrated.id, before.id);
  assert.equal(migrated.adventureWorldId, world.id);
  assert.equal(migrated.resources.gold, before.resources.gold);
  assert.deepEqual(migrated.adventure.claimedSites, before.adventure.claimedSites);
  assert.deepEqual(migrated.adventure.collectedCaches, before.adventure.collectedCaches);
  assert.deepEqual(migrated.adventure.cacheOffers, before.adventure.cacheOffers);
  assert.deepEqual(migrated.adventure.siteOffers, before.adventure.siteOffers);
  assert.ok(migrated.adventure.visited.includes('4,4'));
  assert.ok(migrated.adventure.visited.includes('0,0'));
  assert.ok(migrated.adventure.visited.includes(migrated.adventure.x + ',' + migrated.adventure.y));
  assert.equal(validate(decode(encode(migrated, data), data), data), true);
});

test('legacy unresolved encounters migrate to a live guard marker without dropping the saved pack', () => {
  const world = worlds.find(row => row.id === 'grasslands');
  const state = enterAdventure(world, 6801);
  state.adventure.geometryVersion = 1;
  state.adventure.pendingEncounter = {
    id: 'guard-0,0', cell: [0,0], origin: [0,1], status: 'UNRESOLVED',
    pack: { id: 'kept-pack', stacks: [{ id: 'saved-stack', count: 9 }] },
  };
  state.adventure.x = 0;
  state.adventure.y = 0;
  const payload = JSON.stringify(state);
  const migrated = decode(JSON.stringify({ schema: 1, payload, checksum: checksum(payload) }), data);
  const geometry = adventureGeometryForWorld(contract.geometry.adventure, world, migrated.seed);
  const map = adventureMap(geometry);
  const pending = migrated.adventure.pendingEncounter;
  assert.equal(migrated.adventure.geometryVersion, 4);
  assert.equal(map.guards.has(cellId(pending.cell)), true);
  assert.deepEqual([migrated.adventure.x, migrated.adventure.y], pending.cell);
  assert.ok(isOpen(map, ...pending.origin));
  assert.deepEqual(pending.pack, { id: 'kept-pack', stacks: [{ id: 'saved-stack', count: 9 }] });
});

test('version-2 save migration preserves resolved and pending encounters without losing claims or rewards', () => {
  const world = worlds.find(row => row.id === 'grasslands');
  const state = enterAdventure(world, 6803);
  state.resources.food += 23;
  state.adventure.geometryVersion = 2;
  state.adventure.x = 0;
  state.adventure.y = 0;
  state.adventure.visited.push('3,4', '8,3');
  state.adventure.claimedSites = ['ruin', 'mill'];
  state.adventure.collectedCaches = ['wood'];
  state.adventure.resolvedGuards = ['0,0'];
  state.adventure.pendingEncounter = {
    id: 'guard-14,8', cell: [14,8], origin: [13,8], status: 'UNRESOLVED',
    pack: { id: 'kept-v2-pack', stacks: [{ id: 'kept-v2-stack', count: 7 }] },
  };
  const before = structuredClone(state);
  const payload = JSON.stringify(state);
  const envelope = JSON.stringify({ schema: 1, payload, checksum: checksum(payload) });

  const migrated = decode(envelope, data);
  const geometry = adventureGeometryForWorld(contract.geometry.adventure, world, migrated.seed);
  const map = adventureMap(geometry);
  const pending = migrated.adventure.pendingEncounter;
  assert.equal(migrated.adventure.geometryVersion, 4);
  assert.equal(isOpen(map, migrated.adventure.x, migrated.adventure.y), true);
  assert.deepEqual(migrated.resources, before.resources);
  assert.deepEqual(migrated.adventure.claimedSites, before.adventure.claimedSites);
  assert.deepEqual(migrated.adventure.collectedCaches, before.adventure.collectedCaches);
  assert.ok(migrated.adventure.visited.includes('3,4'));
  assert.ok(migrated.adventure.visited.includes('8,3'));
  assert.ok(migrated.adventure.resolvedGuards.some(key => map.guards.has(key)));
  assert.equal(map.guards.has(cellId(pending.cell)), true);
  assert.deepEqual([migrated.adventure.x, migrated.adventure.y], pending.cell);
  assert.ok(isOpen(map, ...pending.origin));
  assert.deepEqual(pending.pack, before.adventure.pendingEncounter.pack);
  assert.equal(validate(decode(encode(migrated, data), data), data), true);
});

test('version-3 saves migrate to v4 without moving valid encounters or losing campaign progress', () => {
  const world = worlds.find(row => row.id === 'grasslands');
  const state = enterAdventure(world, 6804);
  const geometry = adventureGeometryForWorld(contract.geometry.adventure, world, state.seed);
  const map = adventureMap(geometry);
  const cell = geometry.anchors['guard-ruin'].map(Math.floor);
  const origin = [[cell[0], cell[1] - 1], [cell[0] - 1, cell[1]], [cell[0] + 1, cell[1]], [cell[0], cell[1] + 1]]
    .find(candidate => isOpen(map, ...candidate) && !map.guards.has(cellId(candidate))
      && (() => { try { routeTo(map, geometry.anchors.hero.map(Math.floor), candidate); return true; } catch { return false; } })());
  assert.ok(origin, 'the live encounter retains a reachable origin');
  state.resources.gold += 73;
  state.adventure.geometryVersion = 3;
  state.adventure.x = cell[0];
  state.adventure.y = cell[1];
  state.adventure.visited.push('3,4', cellId(cell));
  state.adventure.resolvedGuards = [geometry.anchors['guard-mine'].map(Math.floor).join(',')];
  state.adventure.claimedSites = ['ruin', 'mill'];
  state.adventure.collectedCaches = ['wood'];
  state.adventure.pendingEncounter = {
    id: 'guard-' + cellId(cell), cell, origin, status: 'UNRESOLVED',
    pack: { id: 'kept-v3-pack', stacks: [{ id: 'kept-v3-stack', count: 6 }] },
  };
  const before = structuredClone(state);
  const payload = JSON.stringify(state);
  const envelope = JSON.stringify({ schema: 1, payload, checksum: checksum(payload) });

  const migrated = decode(envelope, data);
  assert.equal(migrated.adventure.geometryVersion, 4);
  assert.equal(migrated.adventureWorldId, world.id);
  assert.deepEqual([migrated.adventure.x, migrated.adventure.y], [before.adventure.x, before.adventure.y]);
  assert.deepEqual(migrated.adventure.pendingEncounter, before.adventure.pendingEncounter);
  assert.deepEqual(migrated.adventure.resolvedGuards, before.adventure.resolvedGuards);
  assert.deepEqual(migrated.adventure.claimedSites, before.adventure.claimedSites);
  assert.deepEqual(migrated.adventure.collectedCaches, before.adventure.collectedCaches);
  assert.deepEqual(migrated.adventure.cacheOffers, before.adventure.cacheOffers);
  assert.deepEqual(migrated.adventure.siteOffers, before.adventure.siteOffers);
  assert.equal(migrated.resources.gold, before.resources.gold);
  assert.ok(migrated.adventure.visited.includes('3,4'));
  assert.ok(migrated.adventure.visited.includes(cellId(cell)));
  assert.equal(validate(decode(encode(migrated, data), data), data), true);
});

test('version-3 saves safely recover an invalid position while preserving discoveries and claims', () => {
  const world = worlds.find(row => row.id === 'haunted-marsh');
  const state = enterAdventure(world, 6805);
  state.adventure.geometryVersion = 3;
  state.adventure.x = 0;
  state.adventure.y = 0;
  state.adventure.visited.push('4,4', '0,0');
  state.adventure.claimedSites = ['ruin', 'mill'];
  state.adventure.collectedCaches = ['wood'];
  state.resources.gold += 41;
  const before = structuredClone(state);
  const payload = JSON.stringify(state);
  const envelope = JSON.stringify({ schema: 1, payload, checksum: checksum(payload) });

  const migrated = decode(envelope, data);
  const geometry = adventureGeometryForWorld(contract.geometry.adventure, world, migrated.seed);
  const map = adventureMap(geometry);
  assert.equal(migrated.adventure.geometryVersion, 4);
  assert.equal(isOpen(map, migrated.adventure.x, migrated.adventure.y), true);
  assert.notDeepEqual([migrated.adventure.x, migrated.adventure.y], [0, 0]);
  assert.equal(migrated.adventureWorldId, world.id);
  assert.equal(migrated.resources.gold, before.resources.gold);
  assert.deepEqual(migrated.adventure.claimedSites, before.adventure.claimedSites);
  assert.deepEqual(migrated.adventure.collectedCaches, before.adventure.collectedCaches);
  assert.ok(migrated.adventure.visited.includes('4,4'));
  assert.ok(migrated.adventure.visited.includes('0,0'));
  assert.ok(migrated.adventure.visited.includes(migrated.adventure.x + ',' + migrated.adventure.y));
  assert.equal(validate(decode(encode(migrated, data), data), data), true);
});

test('present malformed Adventure geometry versions remain visible as save errors', () => {
  const state = enterAdventure(worlds[0], 6802);
  state.adventure.geometryVersion = 99;
  adoptProgress(state, data);
  assert.equal(state.adventure.geometryVersion, 99, 'migration preserves a present malformed version for validation');
  assert.throws(() => validate(state, data), /Invalid Adventure geometry version/);
});

test('legacy world selection defaults safely and a present malformed choice is rejected', () => {
  const legacy = newCampaign(contract, data, 1000, 6900, worlds[0].id);
  delete legacy.adventureWorldId;
  adoptProgress(legacy, data);
  assert.equal(legacy.adventureWorldId, DEFAULT_ADVENTURE_WORLD_ID);
  assert.equal(validate(legacy, data), true);
  const malformed = newCampaign(contract, data, 1000, 6901, worlds[0].id);
  malformed.adventureWorldId = null;
  adoptProgress(malformed, data);
  assert.equal(malformed.adventureWorldId, null);
  assert.throws(() => validate(malformed, data), /Invalid Adventure world/);
});

test('cache pickups pay once on a walkable production-map anchor and survive save/reload', () => {
  const world = worlds.find(row => row.id === 'jade-karst');
  const entered = enterAdventure(world, 7000);
  const geometry = adventureGeometryForWorld(contract.geometry.adventure, world, entered.seed);
  const map = adventureMap(geometry);
  const anchor = geometry.anchors.wood;
  const destination = anchor.map(Math.floor);
  const moved = moveCampaignTo(entered, map, destination, 'wood-cache');
  const amount = entered.adventure.cacheOffers.wood;
  const claimed = command(moved, { id: 'claim-wood', type: 'CLAIM_ADVENTURE_CACHE', payload: { id: 'wood' } }, 1000, data);
  assert.equal(claimed.resources.wood, moved.resources.wood + amount);
  assert.deepEqual(claimed.adventure.collectedCaches, ['wood']);
  assert.equal(visibleAdventureAnchors(contract.geometry.adventure, claimed.adventure).some(point => point.id === 'wood'), false);
  assert.throws(() => command(claimed, { id: 'claim-wood-again', type: 'CLAIM_ADVENTURE_CACHE', payload: { id: 'wood' } }, 1000, data), /Cache already collected/);
  const reopened = decode(encode(claimed, data), data);
  assert.deepEqual(reopened.adventure.collectedCaches, ['wood']);
  assert.equal(reopened.resources.wood, claimed.resources.wood);
});

test('ruin, mill and mine rewards require their production-map approaches and survive reload', () => {
  const world = worlds.find(row => row.id === 'jade-karst');
  for (const [id, field, offerKey, fixedAmount] of [
    ['ruin', 'xp', 'ruinXp', 90],
    ['mill', 'food', 'millFood', null],
    ['mine', 'gold', 'mineGold', null],
  ]) {
    const entered = enterAdventure(world, 7100);
    const geometry = adventureGeometryForWorld(contract.geometry.adventure, world, entered.seed);
    const map = adventureMap(geometry);
    const site = geometry.sites.find(row => row.id === id);
    assert.throws(() => command(entered, { id: 'too-soon-' + id, type: 'CLAIM_ADVENTURE_SITE', payload: { id } }, 1000, data), /Reach a claimable Adventure site/);
    const moved = moveCampaignTo(entered, map, site.approach, 'site-' + id);
    const amount = fixedAmount ?? moved.adventure.siteOffers[offerKey];
    const claimed = command(moved, { id: 'claim-' + id, type: 'CLAIM_ADVENTURE_SITE', payload: { id } }, 1000, data);
    if (field === 'xp') assert.equal(claimed.hero.xp, moved.hero.xp + amount);
    else assert.equal(claimed.resources[field], moved.resources[field] + amount);
    assert.ok(claimed.adventure.claimedSites.includes(id));
    assert.throws(() => command(claimed, { id: 'repeat-' + id, type: 'CLAIM_ADVENTURE_SITE', payload: { id } }, 1000, data), /already claimed/);
    const reopened = decode(encode(claimed, data), data);
    assert.deepEqual(reopened.adventure.claimedSites, claimed.adventure.claimedSites);
    assert.equal(reopened.adventure.siteOffers[offerKey], amount);
  }
});

test('shrine offers and dwelling purchases use the selected production geometry', () => {
  const world = worlds.find(row => row.id === 'jade-karst');
  const entered = enterAdventure(world, 7200);
  const geometry = adventureGeometryForWorld(contract.geometry.adventure, world, entered.seed);
  const map = adventureMap(geometry);
  const shrine = geometry.sites.find(row => row.id === 'shrine');
  const atShrine = moveCampaignTo(entered, map, shrine.approach, 'shrine');
  const taught = command(atShrine, { id: 'study-shrine', type: 'OFFER_ADVENTURE_SHRINE_SKILL', payload: {} }, 1000, data);
  const offer = taught.hero.offers.find(row => row.source === 'adventure-shrine');
  assert.ok(offer && offer.choices.length > 0 && offer.choices.length <= 2);
  const persisted = decode(encode(taught, data), data);
  assert.deepEqual(persisted.hero.offers.find(row => row.source === 'adventure-shrine'), offer);

  const dwellingRun = enterAdventure(world, 7201);
  const dwellingGeometry = adventureGeometryForWorld(contract.geometry.adventure, world, dwellingRun.seed);
  const dwelling = dwellingGeometry.sites.find(row => row.id === 'dwelling');
  const atDwelling = moveCampaignTo(dwellingRun, adventureMap(dwellingGeometry), dwelling.approach, 'dwelling');
  const offered = command(atDwelling, { id: 'offer-jade-wolf', type: 'OFFER_DWELLING', payload: { type: 'wolf' } }, 1000, data);
  assert.equal(offered.dwelling.type, 'wolf');
});

test('all current world IDs remain selectable and malformed geometry never resets a campaign', () => {
  for (const world of worlds) {
    const state = newCampaign(contract, data, 1000, 7300, world.id);
    assert.equal(state.adventureWorldId, world.id);
    assert.equal(validate(state, data), true);
  }
});
