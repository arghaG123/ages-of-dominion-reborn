const CROSSING_VIEWS = {
  'grasslands:central-stone-bridge': {
    worldId: 'grasslands',
    bridgeId: 'central-stone-bridge',
    geometryVersion: 4,
    file: 'assets/derivatives/adventure-crossing-focus-20261023/grasslands-central-bridge-focus-v1.png',
    sourceSize: [1672, 940],
    sourceRect: [774, 223, 342, 192],
    visualStatus: 'registered-focus-scene-live-review-required',
  },
};

export function crossingPresentation(worldId, adventure, bridges = [], previewRoute = null) {
  if (!worldId || !adventure || !Array.isArray(bridges)) return null;
  if (!Number.isInteger(adventure.x) || !Number.isInteger(adventure.y)) return null;
  const routeCells = previewRoute?.cells ?? previewRoute?.path ?? [];
  const planned = new Set((Array.isArray(routeCells) ? routeCells : [])
    .filter(cell => Array.isArray(cell) && cell.length >= 2 && cell.every(Number.isInteger))
    .map(([x, y]) => `${x},${y}`));
  const current = `${adventure.x},${adventure.y}`;
  const bridge = bridges.find(entry => {
    const deck = entry?.cells ?? [];
    if (deck.some(cell => `${cell[0]},${cell[1]}` === current)) return true;
    const routeUsesDeck = deck.some(cell => planned.has(`${cell[0]},${cell[1]}`));
    const currentAtApproach = (entry?.approaches ?? []).some(cell => `${cell[0]},${cell[1]}` === current);
    return routeUsesDeck && currentAtApproach;
  });
  if (!bridge) return null;
  const registration = CROSSING_VIEWS[`${worldId}:${bridge.id}`];
  if (!registration) return null;
  return { ...registration, cells: bridge.cells, approaches: bridge.approaches ?? [] };
}

export function shouldAutoCloseCrossingPanel({ crossingFocus, panelOpen, menuSheet = false, resourceSheet = false, explicitNavigation = false }) {
  return Boolean(crossingFocus && panelOpen && !menuSheet && !resourceSheet && !explicitNavigation);
}

export function routeWithCurrentCell(route, currentCell) {
  if (!route || !Array.isArray(currentCell) || currentCell.length !== 2) return route;
  const cells = route.cells ?? route.path;
  if (!Array.isArray(cells)) return route;
  if (cells[0]?.[0] === currentCell[0] && cells[0]?.[1] === currentCell[1]) return route;
  return { ...route, cells: [currentCell, ...cells] };
}
