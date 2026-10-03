// Adventure navigation from the registered geometry. Costs follow the adopted rule:
// road and plains cost 1, any other walkable terrain costs 2, water and footprints are blocked,
// and a diagonal step adds 1 only when both adjacent side cells are open.

const key = (x, y) => `${x},${y}`;

export function adventureMap(geometry) {
  const blocked = new Set((geometry.blocked ?? []).map(([x, y]) => key(x, y)));
  for (const [x, y] of geometry.obstacles ?? []) blocked.add(key(x, y));
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
  const guards = new Set();
  for (const [name, cell] of Object.entries(geometry.anchors ?? {})) {
    if (String(name).startsWith('guard')) guards.add(key(Math.floor(cell[0]), Math.floor(cell[1])));
  }
  return { cols: geometry.cols, rows: geometry.rows, blocked, roads, bridge, guards };
}

export function isOpen(map, x, y) {
  return Number.isInteger(x) && Number.isInteger(y) && x >= 0 && y >= 0 && x < map.cols && y < map.rows && !map.blocked.has(key(x, y));
}

export function stepCost(map, from, to, terrainAt = () => 'plains') {
  const [x, y] = from;
  const [tx, ty] = to;
  const dx = tx - x;
  const dy = ty - y;
  if (!Number.isInteger(tx) || !Number.isInteger(ty) || Math.abs(dx) > 1 || Math.abs(dy) > 1 || (dx === 0 && dy === 0)) throw new Error('Illegal step');
  if (!isOpen(map, tx, ty)) throw new Error('Blocked terrain');
  if (dx !== 0 && dy !== 0 && (!isOpen(map, x + dx, y) || !isOpen(map, x, y + dy))) throw new Error('Diagonal corner blocked');
  const kind = map.roads.has(key(tx, ty)) ? 'road' : terrainAt(tx, ty);
  let cost = kind === 'road' || kind === 'plains' ? 1 : 2;
  if (dx !== 0 && dy !== 0) cost += 1;
  return cost;
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
