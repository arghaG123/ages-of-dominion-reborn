// Adventure navigation from the registered geometry. Costs follow the adopted rule:
// road and plains cost 1, any other walkable terrain costs 2, water and footprints are blocked,
// and a diagonal step adds 1 only when both adjacent side cells are open.

const key = (x, y) => `${x},${y}`;
const seededAnchorIds = ['food', 'wood', 'stone', 'gold', 'guard-ruin', 'guard-mine'];
// A campaign seed selects one of twenty authored-feeling placements per world.
// The terrain painting and its fixed sites stay stable; only resource and
// encounter anchors move, so replayability does not require duplicated art.
const layoutCount = 20;
const layoutCache = new Map();

function hashText(value) {
  let hash = 2166136261;
  for (const char of String(value)) {
    hash ^= char.codePointAt(0);
    hash = Math.imul(hash, 16777619);
  }
  return hash >>> 0;
}

function reachableFrom(map, start) {
  const queue = [start];
  const seen = new Set([key(start[0], start[1])]);
  const steps = [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]];
  for (let index = 0; index < queue.length; index += 1) {
    const [x, y] = queue[index];
    for (const [dx, dy] of steps) {
      const nx = x + dx, ny = y + dy, id = key(nx, ny);
      if (seen.has(id) || !isOpen(map, nx, ny)) continue;
      if (dx && dy && (!isOpen(map, x + dx, y) || !isOpen(map, x, y + dy))) continue;
      seen.add(id);
      queue.push([nx, ny]);
    }
  }
  return seen;
}

export function adventureLayoutIndex(world, seed) {
  if (seed == null) return 0;
  return hashText(`${world?.id ?? 'world'}:${seed}`) % layoutCount;
}

function makeSeededLayouts(geometry, world, baseMap) {
  const cacheKey = `${world?.id ?? 'default'}:${geometry.version ?? 1}:${geometry.sourceSha256 ?? ''}`;
  if (layoutCache.has(cacheKey)) return layoutCache.get(cacheKey);
  const hero = geometry.anchors?.hero ?? [8.5, 8.5];
  const heroCell = [Math.floor(hero[0]), Math.floor(hero[1])];
  const reachable = reachableFrom(baseMap, heroCell);
  const approaches = new Set([
    ...(geometry.sites ?? []).map(site => site.approach?.join(',')),
    ...(geometry.bridges ?? []).flatMap(bridge => (bridge.approaches ?? []).map(point => point.join(','))),
  ].filter(Boolean));
  const cells = [];
  for (let y = 1; y < geometry.rows - 1; y += 1) {
    for (let x = 1; x < geometry.cols - 1; x += 1) {
      if (!reachable.has(key(x, y)) || approaches.has(key(x, y))) continue;
      if (baseMap.bridge.has(key(x, y))) continue;
      if (Math.abs(x - heroCell[0]) + Math.abs(y - heroCell[1]) < 3) continue;
      const footprintMargin = world?.id === 'archipelago' ? 0 : 1;
      const insideSite = (geometry.sites ?? []).some(site => {
        const [sx, sy, sw, sh] = site.rect;
        return x >= sx - footprintMargin && x < sx + sw + footprintMargin
          && y >= sy - footprintMargin && y < sy + sh + footprintMargin;
      });
      if (insideSite) continue;
      cells.push([x, y]);
    }
  }

  const baseline = Object.fromEntries(seededAnchorIds
    .filter(id => geometry.anchors?.[id])
    .map(id => [id, geometry.anchors[id]]));
  const baselineCells = new Set(Object.values(baseline)
    .map(([x, y]) => key(Math.floor(x), Math.floor(y))));
  const layouts = [baseline];
  for (let variant = 1; variant < layoutCount; variant += 1) {
    const rankedCells = new Map(seededAnchorIds.map(id => [id, cells
      .slice()
      .sort((first, second) => hashText(`${world?.id}:${variant}:${id}:${key(...first)}`)
        - hashText(`${world?.id}:${variant}:${id}:${key(...second)}`))]));
    const used = [];
    const anchors = {};
    const placeAnchor = index => {
      if (index === seededAnchorIds.length) return true;
      const id = seededAnchorIds[index];
      for (const cell of rankedCells.get(id)) {
        if (baselineCells.has(key(...cell))
          || used.some(([x, y]) => Math.abs(cell[0] - x) + Math.abs(cell[1] - y) < 3)) continue;
        used.push(cell);
        anchors[id] = [cell[0] + 0.5, cell[1] + 0.5];
        if (id.startsWith('guard-') && !siteApproachesRemainReachable(geometry, baseMap, anchors, heroCell)) {
          used.pop();
          delete anchors[id];
          continue;
        }
        if (placeAnchor(index + 1)) return true;
        used.pop();
        delete anchors[id];
      }
      return false;
    };
    if (!placeAnchor(0)) {
      throw new Error(`No spaced reachable anchor layout available for ${world?.id ?? 'world'} layout ${variant + 1}`);
    }
    layouts.push(anchors);
  }
  layoutCache.set(cacheKey, layouts);
  return layouts;
}

function reachableWithoutGuards(map, start) {
  const queue = [start];
  const seen = new Set([key(start[0], start[1])]);
  const steps = [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]];
  for (let index = 0; index < queue.length; index += 1) {
    const [x, y] = queue[index];
    for (const [dx, dy] of steps) {
      const nx = x + dx, ny = y + dy, id = key(nx, ny);
      if (seen.has(id) || map.guards?.has(id) || !isOpen(map, nx, ny)) continue;
      if (dx && dy && (!isOpen(map, x + dx, y) || !isOpen(map, x, y + dy))) continue;
      seen.add(id);
      queue.push([nx, ny]);
    }
  }
  return seen;
}

function siteApproachesRemainReachable(geometry, baseMap, anchors, start) {
  const guardCells = Object.entries(anchors)
    .filter(([id]) => id.startsWith('guard-'))
    .map(([, cell]) => cell.map(Math.floor));
  const guards = new Set(guardCells.map(([x, y]) => key(x, y)));
  const map = { ...baseMap, guards };
  const reachable = reachableWithoutGuards(map, start);
  const reachableCell = cell => cell[0] === start[0] && cell[1] === start[1]
    || reachable.has(key(cell[0], cell[1]));
  if (!Object.entries(anchors).filter(([id]) => !id.startsWith('guard-'))
    .every(([, cell]) => reachableCell(cell.map(Math.floor)))) return false;
  if (!(geometry.sites ?? []).every(site => reachableCell(site.approach))) return false;
  return guardCells.every(([x, y]) => isOpen(map, x, y)
    && [[0, -1], [-1, 0], [1, 0], [0, 1]].some(([dx, dy]) => reachableCell([x + dx, y + dy])));
}

// Each game-specific Adventure map has its own terrain crossings. The shared
// contract supplies common rules; terrain barriers and bridge cells are authored
// against the selected production image.
export function adventureGeometryForWorld(geometry, world, seed) {
  const authored = world?.geometry ?? {};
  const sites = geometry.sites ?? [];
  const siteOverrides = new Map((authored.sites ?? []).map(site => [site.id, site]));
  const merged = {
    ...geometry,
    ...authored,
    blocked: authored.blocked ?? [],
    bridges: authored.bridges ?? [],
    obstacles: authored.obstacles ?? geometry.obstacles ?? [],
    roads: authored.roads ?? geometry.roads ?? [],
    sites: sites.map(site => ({ ...site, ...(siteOverrides.get(site.id) ?? {}) })),
    anchors: { ...(geometry.anchors ?? {}), ...(authored.anchors ?? {}) },
  };
  const map = adventureMap(merged);
  const hero = merged.anchors?.hero;
  if (!hero || !isOpen(map, Math.floor(hero[0]), Math.floor(hero[1]))) {
    throw new Error(`${world?.id ?? 'world'} has no walkable Adventure safe start`);
  }
  for (const site of merged.sites) {
    const [x, y] = site.approach ?? [];
    if (!isOpen(map, x, y)) throw new Error(`${world?.id ?? 'world'} ${site.id} approach is blocked`);
  }
  for (const [id, anchor] of Object.entries(merged.anchors)) {
    if (id === 'hero' || id.startsWith('guard-')) continue;
    if (!isOpen(map, Math.floor(anchor[0]), Math.floor(anchor[1]))) {
      throw new Error(`${world?.id ?? 'world'} ${id} is not placed on walkable terrain`);
    }
  }
  const index = adventureLayoutIndex(world, seed);
  const anchors = makeSeededLayouts(merged, world, map)[index];
  return {
    ...merged,
    anchors: { ...merged.anchors, ...anchors },
    layoutId: `${world?.id ?? 'adventure'}-layout-${index + 1}`,
    layoutIndex: index,
  };
}

export function adventureMap(geometry) {
  const blocked = new Set((geometry.blocked ?? []).map(([x, y]) => key(x, y)));
  for (const [x, y] of geometry.obstacles ?? []) blocked.add(key(x, y));
  const terrain = new Map();
  for (const [kind, cells] of Object.entries(geometry.terrainMasks ?? {})) {
    for (const [x, y] of cells ?? []) {
      terrain.set(key(x, y), kind);
      blocked.add(key(x, y));
    }
  }
  const bridge = new Set();
  for (const crossing of geometry.bridges ?? []) {
    for (const [x, y] of crossing.cells ?? []) {
      bridge.add(key(x, y));
      blocked.delete(key(x, y));
    }
  }
  for (const site of geometry.sites ?? []) {
    const [x, y, w, h] = site.rect;
    for (let c = Math.floor(x); c < Math.ceil(x + w); c++) {
      for (let r = Math.floor(y); r < Math.ceil(y + h); r++) {
        if (c < x + w && c + 1 > x && r < y + h && r + 1 > y) blocked.add(key(c, r));
      }
    }
  }
  const roads = new Set();
  for (const road of geometry.roads ?? []) {
    for (const [x, y] of road) if (Number.isInteger(x) && Number.isInteger(y)) roads.add(key(x, y));
  }
  for (const id of bridge) roads.add(id);
  const guards = new Set();
  for (const [name, cell] of Object.entries(geometry.anchors ?? {})) {
    if (String(name).startsWith('guard')) guards.add(key(Math.floor(cell[0]), Math.floor(cell[1])));
  }
  const walkableTerrain = new Map((geometry.walkableTerrain ?? []).map(([x, y, kind]) => [key(x, y), kind]));
  return { cols: geometry.cols, rows: geometry.rows, blocked, roads, bridge, guards, terrain, walkableTerrain, defaultTerrain: geometry.defaultTerrain ?? 'plains' };
}

export function isOpen(map, x, y) {
  return Number.isInteger(x) && Number.isInteger(y) && x >= 0 && y >= 0 && x < map.cols && y < map.rows && !map.blocked.has(key(x, y));
}

export function stepCost(map, from, to, terrainAt) {
  const [x, y] = from;
  const [tx, ty] = to;
  const dx = tx - x;
  const dy = ty - y;
  if (!Number.isInteger(tx) || !Number.isInteger(ty) || Math.abs(dx) > 1 || Math.abs(dy) > 1 || (dx === 0 && dy === 0)) throw new Error('Illegal step');
  if (!isOpen(map, tx, ty)) throw new Error('Blocked terrain');
  if (dx !== 0 && dy !== 0 && (map.bridge?.has(key(x, y)) || map.bridge?.has(key(tx, ty)))) {
    throw new Error('Bridge decks must be traversed orthogonally');
  }
  if (dx !== 0 && dy !== 0 && (!isOpen(map, x + dx, y) || !isOpen(map, x, y + dy))) throw new Error('Diagonal corner blocked');
  const kind = map.roads.has(key(tx, ty)) ? 'road'
    : typeof terrainAt === 'function' ? terrainAt(tx, ty)
      : map.walkableTerrain?.get(key(tx, ty)) ?? map.defaultTerrain ?? 'plains';
  let cost = kind === 'road' || kind === 'plains' ? 1 : 2;
  if (dx !== 0 && dy !== 0) cost += 1;
  return cost;
}

export function routeTo(map, start, goal, terrainAt) {
  const [sx, sy] = start;
  const [gx, gy] = goal;
  if (!Number.isInteger(sx) || !Number.isInteger(sy) || !Number.isInteger(gx) || !Number.isInteger(gy)) throw new Error('Invalid route');
  if (sx === gx && sy === gy) throw new Error('Already here');
  if (!isOpen(map, gx, gy)) throw new Error('Blocked terrain');
  const origin = key(sx, sy);
  const best = new Map([[origin, { cost: 0, steps: 0 }]]);
  const prev = new Map([[origin, null]]);
  let sequence = 0;
  const queue = [{ cell: [sx, sy], cost: 0, steps: 0, sequence: sequence++ }];
  const steps = [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]];
  let reached = false;
  while (queue.length) {
    queue.sort((first, second) => first.cost - second.cost || first.steps - second.steps || first.sequence - second.sequence);
    const current = queue.shift();
    const at = current.cell;
    const atId = key(at[0], at[1]);
    const known = best.get(atId);
    if (!known || known.cost !== current.cost || known.steps !== current.steps) continue;
    if (at[0] === gx && at[1] === gy) { reached = true; break; }
    for (const [dx, dy] of steps) {
      const next = [at[0] + dx, at[1] + dy];
      const id = key(next[0], next[1]);
      // Route previews stop at an unresolved guard. The campaign MOVE command
      // permits a guard only as the final cell, so previews must not plan a
      // route that crosses an encounter on the way to a different destination.
      if (map.guards?.has(id) && id !== key(gx, gy)) continue;
      let edgeCost;
      try { edgeCost = stepCost(map, at, next, terrainAt); } catch { continue; }
      const cost = current.cost + edgeCost;
      const count = current.steps + 1;
      const prior = best.get(id);
      if (prior && (prior.cost < cost || (prior.cost === cost && prior.steps <= count))) continue;
      best.set(id, { cost, steps: count });
      prev.set(id, at);
      queue.push({ cell: next, cost, steps: count, sequence: sequence++ });
    }
  }
  if (reached) {
    const path = [];
    let cursor = [gx, gy];
    while (key(cursor[0], cursor[1]) !== origin) {
      path.push(cursor);
      cursor = prev.get(key(cursor[0], cursor[1]));
      if (!cursor) throw new Error('No legal route');
    }
    path.reverse();
    return routeCost(map, start, path, terrainAt);
  }
  throw new Error('No legal route');
}

export function routeCost(map, start, path, terrainAt) {
  if (!Array.isArray(path) || path.length === 0 || path.length > 64) throw new Error('Invalid route');
  let at = start;
  let total = 0;
  const cells = [];
  for (const step of path) {
    total += stepCost(map, at, step, terrainAt);
    at = step;
    cells.push(step);
  }
  return { cost: total, cells, destination: at };
}
