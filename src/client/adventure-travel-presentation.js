function cellKey(cell) {
  return Array.isArray(cell) && cell.length >= 2 ? `${cell[0]},${cell[1]}` : null;
}

export function bridgeOnRoute(route, bridges = []) {
  const routeCells = route?.cells ?? route?.path;
  if (!Array.isArray(routeCells) || !Array.isArray(bridges)) return null;
  const path = new Set(routeCells.map(cellKey).filter(Boolean));
  return bridges.find(bridge => (bridge?.cells ?? []).some(cell => path.has(cellKey(cell)))) ?? null;
}

export function travelCommitAction(route, bridges = []) {
  const bridge = bridgeOnRoute(route, bridges);
  const action = bridge ? 'Cross Bridge' : 'Confirm route';
  const cost = Number.isFinite(route?.cost) ? ` · cost ${route.cost}` : '';
  return {
    action,
    label: route ? `${action}${cost}` : 'Confirm route',
    bridgeId: bridge?.id ?? null,
  };
}

export function dwellingRecruitLabel(count, creatureName) {
  const name = typeof creatureName === 'string' && creatureName.trim() ? creatureName.trim() : 'creatures';
  return Number.isSafeInteger(count) && count > 0 ? `Recruit ${count} ${name}` : `Recruit ${name}`;
}
