import { defenseWaveLabel } from './defense-wave-presentation.js';

export const SITE_TITLES = {
  town: 'Town', ruin: 'Ancient ruins', mill: 'Water mill',
  mine: 'Mine', dwelling: 'Creature dwelling', shrine: 'Shrine',
};

const TUTORIAL_CUES = [
  'Build a Lumber Camp.',
  'Build a Farm.',
  'Build a Quarry.',
  'Build a Barracks.',
  'Recruit or reinforce a stack.',
  'Leave town.',
  'Fight the guard.',
  'Hold the lane.',
];

const TUTORIAL_ANCHORS = ['lumber', 'farm', 'quarry', 'barracks', 'muster-recruit:', 'enter-adventure', 'begin-encounter', 'start-siege'];

export function tutorialCueText(step, { view, onRoad, pendingEncounter, skipped = false, buildPickerOpen = false, buildSiteSelected = false } = {}) {
  if (skipped || !Number.isInteger(step) || step < 0 || step >= TUTORIAL_CUES.length) return '';
  if (step === 6 && view === 'adventure' && onRoad && !pendingEncounter) return 'Explore nearby roads to find a guard.';
  if (step <= 3 && view === 'kingdom' && !buildPickerOpen) {
    return buildSiteSelected ? 'Choose a building.' : 'Select the highlighted empty site.';
  }
  return TUTORIAL_CUES[step];
}

// The highlighted control is the one the player can use at this step.
// An empty site comes before the building picker, and the picker comes before a named build.
export function tutorialAnchorChoice(step, { pickerOpen = false, siteSelected = false } = {}) {
  if (!Number.isInteger(step) || step < 0 || step >= TUTORIAL_ANCHORS.length) return '';
  if (step <= 3) {
    if (pickerOpen) return TUTORIAL_ANCHORS[step];
    if (siteSelected) return 'build-picker:';
    return '';
  }
  return TUTORIAL_ANCHORS[step];
}

export function availableDwellingTypes(pool, history = []) {
  const offered = new Set((Array.isArray(history) ? history : [])
    .map(row => row?.type)
    .filter(type => typeof type === 'string'));
  return (Array.isArray(pool) ? pool : []).filter(type => typeof type === 'string' && !offered.has(type));
}

export function discoveredSite(site, adventure) {
  if (site.id === 'town') return true;
  if (!adventure || adventure.atTown) return false;
  const visited = new Set(adventure.visited);
  if (site.approach && visited.has(site.approach.join(','))) return true;
  const [left, top, width, height] = site.rect;
  for (let column = Math.floor(left); column < Math.ceil(left + width); column++) {
    for (let row = Math.floor(top); row < Math.ceil(top + height); row++) {
      if (visited.has(`${column},${row}`)) return true;
    }
  }
  return false;
}

export function visibleAdventureAnchors(geometry, adventure) {
  if (!adventure || adventure.atTown) return [];
  const visited = new Set(adventure.visited || []);
  const resolvedGuards = new Set(adventure.resolvedGuards || []);
  const collectedCaches = new Set(adventure.collectedCaches || []);
  return Object.entries(geometry.anchors || {})
    .filter(([id, cell]) => {
      // The live traveler and minimap player marker replace this fixed spawn point after entry.
      if (id === 'hero') return false;
      const key = `${Math.floor(cell[0])},${Math.floor(cell[1])}`;
      if (!visited.has(key)) return false;
      if (id.startsWith('guard-')) return !resolvedGuards.has(key);
      return !collectedCaches.has(id);
    })
    .map(([id, cell]) => ({
      id,
      kind: id.startsWith('guard-') ? 'guard' : 'cache',
      x: cell[0],
      y: cell[1],
    }));
}

export function adventureTravelerMode(geometry, adventure, moving = false) {
  if (!adventure || adventure.atTown || adventure.pendingEncounter || moving) return 'mounted';
  return geometry.sites.some(site => site.id !== 'town'
    && site.approach[0] === adventure.x
    && site.approach[1] === adventure.y)
    ? 'on-foot'
    : 'mounted';
}

export function adventureAnchorLabelOverlapsTraveler(anchorPoint, travelerPoint, scale) {
  if (!Array.isArray(anchorPoint) || anchorPoint.length < 2 || !Array.isArray(travelerPoint) || travelerPoint.length < 2
    || ![...anchorPoint.slice(0, 2), ...travelerPoint.slice(0, 2), scale].every(Number.isFinite) || scale <= 0) return false;
  return Math.abs((anchorPoint[0] - travelerPoint[0]) * scale) < 96
    && Math.abs((anchorPoint[1] - travelerPoint[1]) * scale) < 150;
}

export function adventureMinimap(geometry, adventure, preview = null) {
  if (!adventure || adventure.atTown) return null;
  const visited = new Set(adventure.visited || []);
  const exploredCells = [];
  for (let row = 0; row < geometry.rows; row += 1) {
    for (let column = 0; column < geometry.cols; column += 1) {
      if (visited.has(`${column},${row}`)) exploredCells.push({ x: column, y: row });
    }
  }
  const blockedCells = (geometry.blocked || [])
    .filter(([column, row]) => visited.has(`${column},${row}`))
    .map(([x, y]) => ({ x, y }));
  const roadSegments = geometry.roads.flatMap(road => road.slice(1).map((cell, index) => ({
    from: { x: road[index][0] + 0.5, y: road[index][1] + 0.5 },
    to: { x: cell[0] + 0.5, y: cell[1] + 0.5 },
  }))).filter(segment => visited.has(`${Math.floor(segment.from.x)},${Math.floor(segment.from.y)}`)
    && visited.has(`${Math.floor(segment.to.x)},${Math.floor(segment.to.y)}`));
  const current = { ...adventure, visited: [...visited] };
  const landmarks = geometry.sites.filter(site => discoveredSite(site, current) && site.approach)
    .map(site => ({ id: site.id, x: site.approach[0] + 0.5, y: site.approach[1] + 0.5 }));
  const pointsOfInterest = visibleAdventureAnchors(geometry, adventure).filter(point => point.id !== 'hero');
  const player = { x: adventure.x + 0.5, y: adventure.y + 0.5 };
  const routeTrail = Array.isArray(preview?.cells) && preview.cells.length
    ? [player, ...preview.cells.map(([x, y]) => ({ x: x + 0.5, y: y + 0.5 }))]
    : [];
  return { columns: geometry.cols, rows: geometry.rows, exploredCells, blockedCells, roadSegments, landmarks, pointsOfInterest, player, routeTrail };
}

export function rosterSelection(army, selectedId) {
  return army.find(stack => stack.id === selectedId) || army[0] || null;
}

export function canConfirmRoute(preview, availableMoves) {
  return Boolean(preview
    && Number.isInteger(preview.cost)
    && preview.cost >= 0
    && Number.isInteger(availableMoves)
    && availableMoves >= preview.cost);
}

export function settlementStarted(before, after) {
  return ['battle', 'defense'].some(key => Boolean(after?.[key]?.pendingSettlement && !before?.[key]?.pendingSettlement));
}

export function shouldShowResumeNote(note, view, state) {
  return Boolean(note && view === 'home' && !state?.battle && !state?.defense);
}

export function labelPositions(rows, width, height, measure) {
  const placed = [];
  const safeTop = 60;
  const safeBottom = height - 76;
  for (const row of [...rows].sort((first, second) => (second.priority || 0) - (first.priority || 0))) {
    const size = measure(row);
    const rowSafeBottom = Number.isFinite(row.safeBottom) ? Math.min(safeBottom, row.safeBottom) : safeBottom;
    const left = Math.max(8, Math.min(width - size.width - 8, row.x - size.width / 2));
    if (row.x < 0 || row.x > width || row.y < 0 || row.y > height) {
      placed.push({ ...row, left, top: Math.max(safeTop, Math.min(rowSafeBottom - size.height, row.y)), ...size, visible: false });
      continue;
    }
    const below = row.y + 8;
    const above = row.y - size.height - 8;
    const preferred = row.placement === 'below' ? below : above;
    const opposite = row.placement === 'below' ? above : below;
    const avoidRects = Array.isArray(row.avoidRects) ? row.avoidRects : [];
    const positions = [preferred,
      ...avoidRects.filter(box => left < box.right + 4 && left + size.width + 4 > box.left)
        .flatMap(box => [box.top - size.height - 5, box.bottom + 5]),
      ...placed.filter(box => left < box.left + box.width + 4 && left + size.width + 4 > box.left)
        .flatMap(box => [box.top - size.height - 5, box.top + box.height + 5])];
    const onPreferredSide = top => row.placement === 'below' ? top >= below : top + size.height <= above;
    const onOppositeSide = top => row.placement === 'below' ? top <= above : top >= below;
    const fits = top => top >= safeTop && top + size.height <= rowSafeBottom;
    const collides = top => placed.some(box => left < box.left + box.width + 4 && left + size.width + 4 > box.left
      && top < box.top + box.height + 4 && top + size.height + 4 > box.top)
      || avoidRects.some(box => left < box.right + 4 && left + size.width + 4 > box.left - 4
        && top < box.bottom + 4 && top + size.height + 4 > box.top - 4);
    const nearest = candidates => candidates
      .filter(top => fits(top) && !collides(top))
      .sort((first, second) => Math.abs(first - preferred) - Math.abs(second - preferred))[0];
    const top = nearest(positions.filter(onPreferredSide))
      ?? nearest([opposite, ...positions].filter(onOppositeSide));
    const fallback = Math.max(safeTop, Math.min(rowSafeBottom - size.height, preferred));
    placed.push({ ...row, left, top: top ?? fallback, ...size, visible: true });
  }
  return placed;
}

export function heroSkillStateCopy(level, offered) {
  if (offered) return level > 0 ? 'Learned rank ' + level + '; rank ' + (level + 1) + ' is available.' : 'Available to learn.';
  return level > 0 ? 'Learned rank ' + level + ' of 3.' : 'No active offer.';
}

export function defenseSummary(session) {
  if (!session) return { title: 'Prepare your defense', wave: '', core: '' };
  const title = session.pendingSettlement ? (session.winner === 'p' ? 'Victory' : 'Defeat')
    : session.paused ? (session.time === 0 ? 'Prepare your defense' : 'Paused') : 'Hold the gate';
  const cleared = Number.isSafeInteger(session.clearedWaves) && session.clearedWaves >= 0 ? session.clearedWaves : 0;
  const active = session.status === 'ACTIVE' && !session.pendingSettlement;
  const wave = session.practice === 'endless'
    ? active ? `Wave ${cleared + 1} · ${cleared} cleared` : `${cleared} waves cleared`
    : defenseWaveLabel(session);
  return {
    title,
    wave,
    core: `${Math.max(0, Math.ceil(session.core))} gate HP`,
  };
}

export function damagedSaveRecoveryCopy({ hasBackup = false, hasDamagedBytes = false } = {}) {
  const actions = [];
  if (hasBackup) actions.push('restore the valid backup');
  if (hasDamagedBytes) actions.push('export the damaged bytes');
  actions.push('import a valid local campaign', 'start a new campaign');
  const finalAction = actions.pop();
  return 'The stored campaign is damaged. You can ' + actions.join(', ') + (actions.length ? ' or ' : '') + finalAction + '.';
}
