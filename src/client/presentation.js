// Live placement for review. This does not edit the active Kingdom contract.
export const STAGE = [1376, 768];
export const ACTIVE_AFFINE = [60, -10, 25, 35, 170, 165];
// Natural ground clearings without permanent grids; outline only for selection, focus, preview or tutorial.
// The affine and Hall scale stay frozen.
export const KINGDOM_PAD_PRESENTATION = 'kingdom-pad-state-v3';

// Hero equipment room (reference 19-hero-equipment): full standing body centred, three slot cards
// on each side, stat strip along the floor. `card` is the body box; the portrait card for a class
// without a standing body (Healer) is fitted inside the same box.
export const HERO_SLOT_COLUMNS = { left: ['helm', 'weapon', 'offhand'], right: ['armor', 'boots', 'accessory'] };
export function armyRankStars(rank) {
  if (!Number.isInteger(rank) || rank < 0 || rank > 4) throw new RangeError('Army rank must be between 0 and 4');
  return `${'★'.repeat(rank)}${'☆'.repeat(4 - rank)}`;
}

export function armyRosterCapacity(count, capacity) {
  if (!Number.isInteger(count) || !Number.isInteger(capacity) || count < 0 || capacity < 1 || count > capacity) {
    throw new RangeError('Army formation count must fit its capacity');
  }
  return { value: count, max: capacity, ratio: count / capacity, label: `${count} of ${capacity} formations` };
}

export function heroStage() {
  const slot = { width: 272, height: 128, gap: 20, top: 104 };
  const column = index => ({ y: slot.top + index * (slot.height + slot.gap), width: slot.width, height: slot.height });
  return {
    card: { x: 448, y: 72, width: 480, height: 628 },
    figure: { x: 688, y: 700 },
    ground: { x1: 40, y: 700, x2: 1330 },
    title: { x: 72, y: 72 },
    slots: {
      left: HERO_SLOT_COLUMNS.left.map((id, index) => ({ id, x: 72, ...column(index) })),
      right: HERO_SLOT_COLUMNS.right.map((id, index) => ({ id, x: 1032, ...column(index) })),
    },
    classGrid: { x: 72, y: 104, width: 272, height: 140, gap: 14, columns: 1 },
    // Two side panels sit under the slot columns, above the dock band.
    progress: { x: 72, y: 556, width: 272, height: 134 },
    stats: { x: 1032, y: 556, width: 272, height: 134 },
  };
}

export function heroFocus(stage = heroStage()) {
  const cardBottom = stage.card.y + stage.card.height;
  return {
    minX: 0,
    minY: 0,
    maxX: STAGE[0],
    maxY: Math.max(STAGE[1], cardBottom, stage.ground.y),
  };
}

export function cardInsideStage(stage = heroStage(), source = STAGE) {
  const box = stage.card;
  return box.x >= 0 && box.y >= 0 && box.x + box.width <= source[0] && box.y + box.height <= source[1];
}

// Visual perimeter only. Legal site rectangles stay on the active contract.
// The front line sits on the road anchor so the gate opening meets the road.
// Side runs split at mid-depth: the far half is behind buildings, the near half is in front.
export function wallPresentation(geo) {
  const gateX = geo.anchors?.gate?.[0] ?? 7.7;
  const bottom = 9.45;
  const gap = 1;
  const left = 0.7;
  const right = 12.6;
  const top = 0.15;

  // Clearing perimeter, outside P01–P17 and north of the painted foreground huts.
  // The contract gate anchor stays south of this front line.
  const nw = [left, top];
  const ne = [right, top];
  const midW = [left, 4.7];
  const sw = [left, bottom];
  const midE = [right, 4.7];
  const se = [right, bottom];

  const segment = (id, depth, a, b) => ({ id, depth, a, b, kind: 'run' });
  const corner = (id, depth, at) => ({ id, depth, at });
  return {
    version: 'walls-isometric-v4',
    contractUnchanged: true,
    gate: [gateX, bottom],
    road: [gateX, bottom],
    opening: gap,
    corners: [
      corner('nw', 'back', nw),
      corner('ne', 'back', ne),
      corner('sw', 'front', sw),
      corner('se', 'front', se),
    ],
    segments: [
      segment('back', 'back', nw, ne),
      segment('side-west-far', 'back', nw, midW),
      segment('side-east-far', 'back', ne, midE),
      segment('side-west-near', 'front', midW, sw),
      segment('side-east-near', 'front', midE, se),
      segment('front-west', 'front', sw, [gateX - gap / 2, bottom]),
      segment('front-east', 'front', [gateX + gap / 2, bottom], se),
    ],
  };
}
