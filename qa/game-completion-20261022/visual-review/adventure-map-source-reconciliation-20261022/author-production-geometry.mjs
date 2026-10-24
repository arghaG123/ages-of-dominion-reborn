import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const folder = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(folder, '../../../..');
const worldsPath = path.join(root, 'src/data/adventure-worlds.json');
const manifestPath = path.join(folder, 'source-manifest.json');
const worlds = JSON.parse(fs.readFileSync(worldsPath, 'utf8'));
const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
const rows = 10, cols = 16;
const defaultTerrainByWorld = {
  grasslands: 'plains', tundra: 'snow', 'haunted-marsh': 'bog', 'desert-volcano': 'sand',
  underworld: 'stone', feywild: 'forest', archipelago: 'sand', 'mesa-savanna': 'savanna',
  'astral-peaks': 'alpine', 'blood-moon': 'ash', 'jade-karst': 'forest', 'sunken-jungle': 'jungle',
};
const point = (x, y) => [x, y];
const bridge = (id, cells, approaches, type = 'bridge') => ({ id, type, cells, approaches });
const site = (id, rect, approach, landmark, representation = 'painted-landmark') => ({
  id, rect, approach, landmark, representation,
});

// Every coordinate is authored against the 16x10 grid on the generated map
// contact/grid images in this folder. Water, cliff and lava cells are drawn
// from the generated production map, not the example references.
const authored = {
  grasslands: {
    water: [[0,4],[1,4],[3,4],[4,4],[6,4],[8,3],[9,3],[8,4],[9,4],[11,4],[12,4],[13,5],[14,5],[14,6],[15,6]],
    cliffs: [[0,0],[0,1],[15,0],[15,1],[15,8],[15,9]],
    bridges: [
      bridge('west-river-arch', [[3,4],[4,4]], [[2,4],[5,4]]),
      bridge('central-stone-bridge', [[8,3],[9,3]], [[7,3],[10,3]]),
      bridge('east-river-arch', [[11,4],[12,4]], [[10,4],[13,4]]),
    ],
    roads: [[[5,5],[6,5],[7,5],[8,5],[9,5],[10,5]], [[3,3],[4,3],[5,3]], [[10,6],[11,6],[12,6]]],
    sites: [
      site('town',[7,1,4,2],[8,3],'walled river citadel'),
      site('ruin',[0,6,2,2],[2,6],'weathered cliffside sanctuary'),
      site('mill',[2,2,2,2],[4,3],'hilltop windmill'),
      site('mine',[13,7,2,2],[12,7],'gold hoist and mine camp'),
      site('dwelling',[4,5,2,2],[4,4],'farmstead village'),
      site('shrine',[7,4,1,1],[7,5],'roadside standing-stone shrine'),
    ],
    anchors: { hero:[6.5,5.5], food:[6.5,6.5], wood:[1.5,8.5], stone:[12.5,2.5], gold:[11.5,8.5], 'guard-ruin':[2.5,5.5], 'guard-mine':[12.5,5.5] },
    crossings: 3,
  },
  tundra: {
    cliffs: [[0,0],[1,0],[2,0],[3,0],[12,0],[13,0],[14,0],[15,0],[0,8],[0,9],[15,8],[15,9]],
    bridges: [],
    roads: [[[5,5],[6,5],[7,5],[8,5],[9,5],[10,5]], [[6,4],[7,4],[8,4],[9,4],[10,4]], [[8,7],[9,7],[10,7]]],
    sites: [
      site('town',[8,1,4,3],[9,4],'torchlit mountain citadel'),
      site('ruin',[14,4,2,2],[13,4],'icebound guardian statue'),
      site('mill',[9,6,2,2],[9,5],'timber sawmill camp'),
      site('mine',[13,7,2,2],[12,7],'gold mine hoist'),
      site('dwelling',[3,2,3,2],[6,3],'cliffside lodge settlement'),
      site('shrine',[0,4,2,3],[2,5],'glacier shrine statue'),
    ],
    anchors: { hero:[7.5,5.5], food:[11.5,8.5], wood:[6.5,7.5], stone:[10.5,5.5], gold:[14.5,6.5], 'guard-ruin':[13.5,3.5], 'guard-mine':[12.5,5.5] },
    crossings: 0,
  },
  'haunted-marsh': {
    bog: [[5,2],[6,2],[7,2],[8,2],[12,8],[13,8],[14,8]],
    cliffs: [[0,0],[15,0],[15,9]],
    bridges: [],
    roads: [[[4,5],[5,5],[6,5],[7,5],[8,5],[9,5],[10,5]], [[8,4],[9,4],[10,4],[11,4],[12,4]], [[5,7],[6,7],[7,7]]],
    sites: [
      site('town',[10,0,3,3],[9,3],'stormlit necropolis keep'),
      site('ruin',[2,2,2,2],[4,3],'haunted grove of stone remnants'),
      site('mill',[13,2,2,2],[12,3],'marshside windmill'),
      site('mine',[4,6,3,2],[7,6],'sunken quarry and hoist'),
      site('dwelling',[0,1,2,2],[3,1],'marsh village and timber homes'),
      site('shrine',[7,3,2,2],[8,5],'lantern shrine on the causeway'),
    ],
    anchors: { hero:[8.5,6.5], food:[13.5,5.5], wood:[2.5,7.5], stone:[9.5,7.5], gold:[4.5,4.5], 'guard-ruin':[4.5,2.5], 'guard-mine':[7.5,7.5] },
    crossings: 0,
  },
  'desert-volcano': {
    water: [[8,4],[9,4],[8,5],[9,5]],
    lava: [[0,0],[1,0],[0,1],[1,1],[2,1],[0,2],[1,2],[2,2],[2,3],[0,4]],
    cliffs: [[0,3],[1,3],[0,8],[1,8],[15,2],[15,3],[15,4]],
    bridges: [],
    roads: [[[6,3],[7,3],[8,3],[9,3],[10,3],[11,3]], [[5,6],[6,6],[7,6],[8,6],[9,6],[10,6]], [[11,5],[12,5]]],
    sites: [
      site('town',[8,0,4,3],[8,3],'sandstone palace and city gate'),
      site('ruin',[0,5,2,2],[2,5],'skull-cave ruin'),
      site('mill',[6,4,2,2],[6,6],'oasis watermill','runtime-object'),
      site('mine',[3,3,2,2],[5,3],'desert mine entrance'),
      site('dwelling',[5,1,2,2],[6,3],'oasis caravan quarter'),
      site('shrine',[12,5,3,3],[11,5],'sun-temple portal'),
    ],
    anchors: { hero:[7.5,6.5], food:[10.5,6.5], wood:[5.5,5.5], stone:[14.5,2.5], gold:[4.5,5.5], 'guard-ruin':[2.5,4.5], 'guard-mine':[5.5,4.5] },
    crossings: 0,
  },
  underworld: {
    water: [[0,2],[1,2],[2,2],[7,7],[8,7],[9,7],[9,8]],
    cliffs: [[0,9],[1,9],[2,9],[14,9],[15,9]],
    bridges: [],
    roads: [[[4,5],[5,5],[6,5],[7,5],[8,5],[9,5]], [[8,3],[9,3],[10,3],[11,3],[12,3]], [[8,6],[9,6],[10,6]]],
    sites: [
      site('town',[0,5,3,3],[3,6],'underground fortress district'),
      site('ruin',[12,6,3,2],[11,6],'serpent-skull cavern'),
      site('mill',[5,6,2,2],[5,5],'crystal-stream watermill','runtime-object'),
      site('mine',[13,2,2,2],[12,3],'deep gold mine works'),
      site('dwelling',[13,0,3,2],[12,1],'glowing mushroom grotto'),
      site('shrine',[5,3,2,2],[6,5],'crystal altar and portal'),
    ],
    anchors: { hero:[4.5,5.5], food:[4.5,3.5], wood:[2.5,4.5], stone:[9.5,5.5], gold:[12.5,5.5], 'guard-ruin':[11.5,7.5], 'guard-mine':[12.5,4.5] },
    crossings: 0,
  },
  feywild: {
    water: [[5,4],[6,4]],
    cliffs: [[0,0],[15,0],[0,9],[15,9]],
    bridges: [],
    roads: [[[6,5],[7,5],[8,5],[9,5],[10,5]], [[4,3],[5,3],[6,3],[7,3]], [[8,6],[9,6],[10,6]]],
    sites: [
      site('town',[8,1,4,3],[9,4],'illuminated sylvan city'),
      site('ruin',[1,4,3,2],[4,5],'moss-covered stone circle'),
      site('mill',[4,1,2,2],[5,3],'fairy-grove watermill','runtime-object'),
      site('mine',[6,3,2,1],[7,4],'blue crystal quarry'),
      site('dwelling',[12,1,2,2],[14,2],'lanternlit woodland homes'),
      site('shrine',[7,6,3,2],[8,5],'central crystal spring shrine'),
    ],
    anchors: { hero:[7.5,5.5], food:[3.5,7.5], wood:[2.5,8.5], stone:[11.5,5.5], gold:[12.5,7.5], 'guard-ruin':[5.5,5.5], 'guard-mine':[10.5,7.5] },
    crossings: 0,
  },
  archipelago: {
    water: [[0,0],[1,0],[7,0],[10,0],[11,0],[15,0],[0,1],[10,1],[11,1],[15,1],[0,2],[3,2],[4,2],[6,2],[9,2],[10,2],[15,2],[0,3],[6,3],[7,3],[9,3],[10,3],[15,3],[0,4],[1,4],[2,4],[6,4],[8,4],[9,4],[12,4],[13,4],[14,4],[15,4],[4,5],[5,5],[12,5],[13,5],[14,5],[15,5],[4,6],[5,6],[6,6],[12,6],[13,6],[14,6],[15,6],[0,7],[1,7],[2,7],[6,7],[7,7],[8,7],[15,7],[0,8],[1,8],[2,8],[3,8],[4,8],[5,8],[8,8],[9,8],[10,8],[15,8],[0,9],[1,9],[2,9],[3,9],[4,9],[5,9],[8,9],[9,9],[10,9],[15,9]],
    cliffs: [[2,0],[15,8]],
    bridges: [
      bridge('west-island-sandbar', [[3,2],[4,2]], [[2,2],[5,2]], 'sandbar'),
      bridge('central-island-causeway', [[6,3],[7,3]], [[5,3],[8,3]], 'causeway'),
      bridge('harbor-sandbar', [[8,4],[9,4]], [[7,4],[10,4]], 'sandbar'),
      bridge('southwestern-reef-causeway', [[4,5],[5,5]], [[3,5],[6,5]], 'causeway'),
    ],
    roads: [[[8,4],[9,4],[10,4],[11,4],[11,5],[11,6],[11,7],[12,7]], [[5,3],[6,3],[7,3]]],
    sites: [
      site('town',[8,5,3,2],[9,4],'central harbor city and east dockwalk'),
      site('ruin',[8,0,2,2],[8,3],'overgrown island temple'),
      site('mill',[4,4,2,1],[6,3],'shoreline watermill','runtime-object'),
      site('mine',[1,1,1,3],[2,2],'volcanic island mine cave'),
      site('dwelling',[12,1,2,2],[12,3],'northern island village'),
      site('shrine',[1,5,2,2],[3,5],'seaside beacon shrine'),
    ],
    anchors: { hero:[7.5,5.5], food:[7.5,6.5], wood:[5.5,7.5], stone:[13.5,8.5], gold:[11.5,7.5], 'guard-ruin':[7.5,2.5], 'guard-mine':[3.5,3.5] },
    crossings: 4,
  },
  'mesa-savanna': {
    cliffs: [[0,2],[0,3],[0,7],[1,7],[2,7],[15,2],[15,3],[15,4],[0,9],[15,9]],
    bridges: [],
    roads: [[[4,2],[5,2],[6,2],[7,2],[8,2],[9,2]], [[5,5],[6,5],[7,5],[8,5],[9,5],[10,5]], [[9,3],[10,3],[11,3],[12,3]]],
    sites: [
      site('town',[1,1,3,2],[4,2],'mesa-top stone citadel'),
      site('ruin',[13,4,2,2],[12,5],'great fossil arch ruin'),
      site('mill',[6,6,2,2],[6,5],'savanna windmill','runtime-object'),
      site('mine',[13,1,2,2],[12,2],'canyon mine entrance'),
      site('dwelling',[8,1,2,2],[8,3],'lonely mesa watchtower'),
      site('shrine',[2,4,3,2],[4,6],'ancient stone-circle shrine'),
    ],
    anchors: { hero:[5.5,3.5], food:[7.5,5.5], wood:[2.5,8.5], stone:[11.5,7.5], gold:[12.5,3.5], 'guard-ruin':[12.5,6.5], 'guard-mine':[11.5,3.5] },
    crossings: 0,
  },
  'astral-peaks': {
    cliffs: [[0,0],[1,0],[2,0],[0,1],[14,2],[15,2],[15,3],[0,7],[1,7],[15,8],[0,9],[15,9]],
    bridges: [],
    roads: [[[4,4],[5,4],[6,4],[7,4],[8,4],[9,4],[10,4],[11,4],[12,4]], [[7,5],[8,5],[9,5],[10,5]], [[12,6],[13,6]]],
    sites: [
      site('town',[0,4,4,2],[4,4],'western observatory city'),
      site('ruin',[9,4,2,2],[8,5],'moon-arch ruins'),
      site('mill',[6,5,2,2],[8,6],'cloud-valley watermill','runtime-object'),
      site('mine',[14,6,2,2],[13,6],'blue crystal quarry'),
      site('dwelling',[13,0,3,2],[12,2],'high-aerie creature roost'),
      site('shrine',[11,4,1,2],[12,5],'lunar gate sanctuary'),
    ],
    anchors: { hero:[5.5,5.5], food:[8.5,7.5], wood:[2.5,7.5], stone:[9.5,8.5], gold:[13.5,5.5], 'guard-ruin':[8.5,3.5], 'guard-mine':[13.5,7.5] },
    crossings: 0,
  },
  'blood-moon': {
    lava: [[0,2],[5,1],[6,1],[6,2],[7,6],[8,6],[11,8],[12,8]],
    cliffs: [[0,0],[1,0],[15,0],[15,1],[0,9],[15,9]],
    bridges: [],
    roads: [[[4,3],[5,3],[6,3],[7,3],[8,3],[9,3]], [[6,5],[7,5],[8,5],[9,5],[10,5]], [[2,6],[3,6],[4,6]]],
    sites: [
      site('town',[7,0,3,3],[8,3],'eclipse fortress and gate'),
      site('ruin',[1,1,2,3],[3,3],'blood-red obelisk ruin'),
      site('mill',[4,4,2,2],[6,4],'ashland millworks','runtime-object'),
      site('mine',[1,6,2,2],[3,6],'crystal mine and hoist'),
      site('dwelling',[13,6,2,2],[12,6],'red-crystal creature den','runtime-object'),
      site('shrine',[10,4,2,2],[9,4],'ritual fire shrine'),
    ],
    anchors: { hero:[7.5,5.5], food:[5.5,7.5], wood:[3.5,5.5], stone:[9.5,7.5], gold:[12.5,5.5], 'guard-ruin':[3.5,4.5], 'guard-mine':[4.5,7.5] },
    crossings: 0,
  },
  'jade-karst': {
    water: [[11,3],[12,3],[11,4],[12,4],[11,5],[12,5],[6,6],[7,6],[6,7],[7,7]],
    cliffs: [[0,0],[15,0],[0,8],[0,9],[15,8],[15,9]],
    bridges: [
      bridge('east-river-stone-arch', [[11,4],[12,4]], [[10,4],[13,4]]),
      bridge('southern-karst-arch', [[6,6],[7,6]], [[5,6],[8,6]]),
    ],
    roads: [[[5,3],[6,3],[7,3],[8,3],[9,3],[10,3]], [[8,4],[9,4],[10,4],[11,4],[12,4]], [[4,6],[5,6],[6,6],[7,6],[8,6]]],
    sites: [
      site('town',[7,2,3,2],[8,4],'central karst palace'),
      site('ruin',[1,2,2,2],[3,3],'weathered cliff pagoda'),
      site('mill',[8,0,2,2],[10,1],'terraced windmill'),
      site('mine',[14,5,2,2],[13,5],'river-cliff mine works'),
      site('dwelling',[3,1,2,2],[5,2],'bamboo hamlet'),
      site('shrine',[10,6,2,2],[10,5],'blue waterfall shrine'),
    ],
    anchors: { hero:[7.5,5.5], food:[3.5,6.5], wood:[4.5,8.5], stone:[13.5,8.5], gold:[13.5,6.5], 'guard-ruin':[4.5,4.5], 'guard-mine':[12.5,7.5] },
    crossings: 2,
  },
  'sunken-jungle': {
    water: [[0,5],[1,5],[2,5],[4,5],[5,5],[7,5],[8,5],[0,6],[1,6],[2,6],[7,6],[8,6],[4,7],[5,7],[6,7],[7,7],[8,7]],
    cliffs: [[0,0],[15,0],[0,9],[15,9]],
    bridges: [
      bridge('west-ruin-stone-crossing', [[4,5],[5,5]], [[3,5],[6,5]]),
      bridge('central-jungle-causeway', [[7,5],[8,5]], [[6,5],[9,5]], 'causeway'),
      bridge('lower-stone-stepping-route', [[7,6],[8,6]], [[6,6],[9,6]], 'stepping-stones'),
    ],
    roads: [[[4,3],[5,3],[6,3],[7,3],[8,3],[9,3],[10,3]], [[6,4],[7,4],[8,4],[9,4]], [[9,5],[10,5],[11,5],[12,5]]],
    sites: [
      site('town',[5,0,3,2],[6,2],'upper jungle temple settlement'),
      site('ruin',[1,2,2,2],[3,3],'left-bank stone ruin'),
      site('mill',[10,5,2,2],[12,5],'jungle river waterwheel'),
      site('mine',[1,0,2,2],[3,1],'overgrown mine cave'),
      site('dwelling',[13,0,2,2],[12,2],'eastern canopy village'),
      site('shrine',[10,3,2,2],[9,4],'blue river shrine'),
    ],
    anchors: { hero:[7.5,3.5], food:[11.5,7.5], wood:[2.5,8.5], stone:[8.5,8.5], gold:[3.5,6.5], 'guard-ruin':[4.5,3.5], 'guard-mine':[13.5,4.5] },
    crossings: 3,
  },
};

const source = (worldId, role) => manifest.sources.find(row => row.worldId === worldId && row.role === role);
const flattenMasks = masks => Object.values(masks).flatMap(cells => cells ?? []);
const key = ([x, y]) => `${x},${y}`;
for (const world of worlds) {
  const spec = authored[world.id];
  if (!spec) throw new Error(`Missing production geometry for ${world.id}`);
  const ref = source(world.id, 'reference');
  const production = source(world.id, 'generated-game-map');
  if (!ref || !production) throw new Error(`Missing source manifest binding for ${world.id}`);
  const oldGeometry = world.referenceGeometry?.geometry ?? world.geometry;
  const bridges = spec.bridges ?? [];
  const deck = new Set(bridges.flatMap(row => row.cells.map(key)));
  const terrainMasks = {
    water: spec.water ?? [],
    bog: spec.bog ?? [],
    lava: spec.lava ?? [],
    cliff: spec.cliffs ?? [],
  };
  const blocked = flattenMasks(terrainMasks).filter(cell => !deck.has(key(cell)));
  const allOpenOverrides = new Set([...deck, ...spec.sites.map(row => key(row.approach))]);
  for (let firstIndex = 0; firstIndex < spec.sites.length; firstIndex += 1) {
    const [ax, ay, aw, ah] = spec.sites[firstIndex].rect;
    for (let secondIndex = firstIndex + 1; secondIndex < spec.sites.length; secondIndex += 1) {
      const [bx, by, bw, bh] = spec.sites[secondIndex].rect;
      if (ax < bx + bw && bx < ax + aw && ay < by + bh && by < ay + ah) {
        throw new Error(`${world.id} site footprints overlap: ${spec.sites[firstIndex].id} and ${spec.sites[secondIndex].id}`);
      }
    }
  }
  for (const row of spec.sites) {
    const [x, y, w, h] = row.rect;
    if (x < 0 || y < 0 || x + w > cols || y + h > rows) throw new Error(`${world.id} ${row.id} footprint out of bounds`);
    if (blocked.some(([bx, by]) => bx >= x && bx < x + w && by >= y && by < y + h)) {
      throw new Error(`${world.id} ${row.id} footprint overlaps a blocked terrain cell`);
    }
    const [ax, ay] = row.approach;
    if (blocked.some(cell => key(cell) === key(row.approach))) throw new Error(`${world.id} ${row.id} approach is on blocked terrain`);
    if (spec.sites.some(other => {
      if (other.id === row.id) return false;
      const [sx, sy, sw, sh] = other.rect;
      return ax >= sx && ax < sx + sw && ay >= sy && ay < sy + sh;
    })) throw new Error(`${world.id} ${row.id} approach overlaps another site`);
  }
  const siteApproaches = spec.sites.map(row => key(row.approach));
  if (new Set(siteApproaches).size !== siteApproaches.length) throw new Error(`${world.id} site interaction tiles overlap`);
  for (const row of bridges) {
    for (const cell of row.cells) {
      if (!flattenMasks(terrainMasks).some(other => key(other) === key(cell))) throw new Error(`${world.id} ${row.id} deck is not traced over a water/hazard cell`);
    }
    const sequence = [row.approaches[0], ...row.cells, row.approaches.at(-1)];
    for (let index = 1; index < sequence.length; index += 1) {
      const distance = Math.abs(sequence[index][0] - sequence[index - 1][0]) + Math.abs(sequence[index][1] - sequence[index - 1][1]);
      if (distance !== 1) throw new Error(`${world.id} ${row.id} deck and banks are not contiguous orthogonal cells`);
    }
    for (const bank of row.approaches) {
      if (blocked.some(cell => key(cell) === key(bank))) throw new Error(`${world.id} ${row.id} bank is blocked`);
      if (spec.sites.some(site => {
        const [x, y, w, h] = site.rect;
        return bank[0] >= x && bank[0] < x + w && bank[1] >= y && bank[1] < y + h;
      })) throw new Error(`${world.id} ${row.id} bank overlaps a site footprint`);
    }
  }
  for (const [name, cell] of Object.entries(spec.anchors)) {
    const [x, y] = cell.map(Math.floor);
    if (x < 0 || y < 0 || x >= cols || y >= rows || (blocked.some(other => key(other) === `${x},${y}`) && !allOpenOverrides.has(`${x},${y}`))) {
      throw new Error(`${world.id} ${name} anchor is not on an open cell`);
    }
    if (spec.sites.some(row => x >= row.rect[0] && x < row.rect[0] + row.rect[2] && y >= row.rect[1] && y < row.rect[1] + row.rect[3])) {
      throw new Error(`${world.id} ${name} anchor overlaps a site footprint`);
    }
    if (name !== 'hero' && spec.sites.some(row => row.approach[0] === x && row.approach[1] === y)) {
      throw new Error(`${world.id} ${name} anchor overlaps the ${spec.sites.find(row => row.approach[0] === x && row.approach[1] === y).id} site approach`);
    }
    if (name !== 'hero' && deck.has(`${x},${y}`)) throw new Error(`${world.id} ${name} anchor overlaps a crossing deck`);
  }
  world.referenceFile ??= world.file;
  world.productionMapFile ||= world.mapFile;
  if (!world.referenceFile || !world.productionMapFile) throw new Error('Missing explicit reference or production map source for ' + world.id);
  world.sourceBindings = {
    reference: { role: 'visual-example-only', file: ref.path, sha256: ref.sha256, dimensions: ref.dimensions, geometryVersion: 1 },
    production: { role: 'game-specific-runtime-map', file: production.path, sha256: production.sha256, dimensions: production.dimensions, geometryVersion: 4 },
  };
  world.referenceGeometry = { version: 1, sourceFile: ref.path, sourceSha256: ref.sha256, geometry: oldGeometry };
  delete world.runtimeFile;
  delete world.file;
  delete world.mapFile;
  world.mapFeatures = {
    water: terrainMasks.water.length ? (world.id === 'archipelago' ? 'ocean-and-island-channels'
      : world.id === 'jade-karst' ? 'winding-karst-river'
        : world.id === 'sunken-jungle' ? 'jungle-river-and-pools'
          : world.id === 'desert-volcano' ? 'oasis-pools'
            : world.id === 'underworld' ? 'crystal-cavern-pools'
              : world.id === 'feywild' ? 'crystal-spring' : 'river') : null,
    bridges: bridges.filter(row => row.type === 'bridge').length,
    playableCrossings: bridges.length,
    art: 'integrated-generated-game-map',
  };
  world.geometry = {
    version: 4,
    sourceFile: production.path,
    sourceSha256: production.sha256,
    sourceSize: production.dimensions,
    cols, rows,
    worldToSource: [production.dimensions[0] / cols, 0, 0, production.dimensions[1] / rows, 0, 0],
    defaultTerrain: defaultTerrainByWorld[world.id],
    walkableTerrain: [],
    terrainMasks,
    blocked,
    obstacles: [],
    bridges,
    roads: spec.roads,
    sites: spec.sites,
    anchors: spec.anchors,
  };
}

fs.writeFileSync(worldsPath, `${JSON.stringify(worlds, null, 2)}\n`);
console.log(`Authored version-4 production geometry for ${worlds.length} worlds; preserved each version-1 reference geometry and the separately archived version-2 geometry.`);
