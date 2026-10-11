// Live placement for review. This does not edit the active Kingdom contract.
export const STAGE = [1376, 768];
export const ACTIVE_AFFINE = [60, -10, 25, 35, 170, 165];
// Empty sites are brass outlines and a stake. The painted ground stays visible.
// The affine and Hall scale stay frozen.
export const KINGDOM_PAD_PRESENTATION = 'kingdom-pad-state-v2';

// Hero equipment room (reference 19-hero-equipment): full standing body centred, three slot cards
// on each side, stat strip along the floor. `card` is the body box; the portrait card for a class
// without a standing body (Healer) is fitted inside the same box.
export const HERO_SLOT_COLUMNS = { left: ['helm', 'weapon', 'offhand'], right: ['armor', 'boots', 'accessory'] };
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

// Separate unbuilt perimeter. Site rectangles stay on the active contract.
export function wallPresentation(geo) {
  let minX = Infinity;
  let minY = Infinity;
  let maxX = -Infinity;
  let maxY = -Infinity;
  for (const site of geo.sites) {
    const [x, y, w, h] = site.rect;
    minX = Math.min(minX, x);
    minY = Math.min(minY, y);
    maxX = Math.max(maxX, x + w);
    maxY = Math.max(maxY, y + h);
  }
  const pad = 0.55;
  const left = minX - pad;
  const top = minY - pad;
  const right = maxX + pad;
  const bottom = maxY + pad;
  const gateX = geo.anchors?.gate?.[0] ?? (left + right) / 2;
  const gap = 0.7;
  return {
    version: 'walls-presentation-v1',
    contractUnchanged: true,
    points: [
      [gateX - gap, bottom],
      [left, bottom],
      [left, top],
      [right, top],
      [right, bottom],
      [gateX + gap, bottom],
    ],
  };
}
