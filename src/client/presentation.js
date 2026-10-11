// Live placement for review. This does not edit the active Kingdom contract.
export const STAGE = [1376, 768];
export const ACTIVE_AFFINE = [60, -10, 25, 35, 170, 165];
// Empty sites are brass outlines and a stake. The painted ground stays visible.
// The affine and Hall scale stay frozen.
export const KINGDOM_PAD_PRESENTATION = 'kingdom-pad-state-v2';

export function heroStage() {
  return {
    card: { x: 48, y: 40, width: 460, height: 460 },
    figure: { x: 278, y: 700 },
    ground: { x1: 40, y: 700, x2: 1330 },
  };
}

export function heroFocus(stage = heroStage()) {
  const cardBottom = stage.card.y + stage.card.height;
  return {
    minX: stage.card.x - 24,
    minY: Math.max(0, stage.card.y - 16),
    maxX: stage.ground.x2 + 20,
    maxY: Math.max(cardBottom, stage.ground.y) + 24,
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
