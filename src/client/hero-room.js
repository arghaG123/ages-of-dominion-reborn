// Hero equipment room. Draws the realistic standing class body (hero-bodies-20261011), six slot
// cards with gear icons, class choice cards and the stat strip into the 1376x768 world.
// The backdrop is native SVG (no interior painting exists); it is labelled as such in data-backdrop.
import heroBodies from '../data/hero-bodies-20261011.json' with { type: 'json' };
import gearIcons from '../data/gear-icons-20261007.json' with { type: 'json' };
import { HERO_SLOT_COLUMNS, heroStage } from './presentation.js';
import { visibleBox } from './visible-size.js';
import { isWearLayerSupported, paintWornSlots, WORN_ANCHORS } from './actor.js';
import { gearBonus } from '../core/rules.js';
import kitEras from '../data/hero-kit-eras-20261017.json' with { type: 'json' };

// Four kit eras across eight ages (MASTER-PLAN): ancient, medieval, powder, mech.
export function kitEra(age) {
  return ['ancient', 'ancient', 'ancient', 'medieval', 'powder', 'powder', 'mech', 'mech'][age] || 'ancient';
}

// Without an age, this is the reviewed base plate. With an age, it is that age's kit era
// when a reviewed plate for the era exists.
export function heroBody(classId, age = null) {
  const body = heroBodies.bodies?.[classId] || null;
  if (!body || !Number.isInteger(age)) return body;
  const era = kitEra(age);
  const variant = kitEras.classes?.[classId]?.[era];
  if (!variant?.file) return body;
  return {
    ...body,
    file: variant.file,
    sha256: variant.sha256,
    bytes: variant.bytes,
    width: variant.width,
    height: variant.height,
    foot: variant.foot,
    id: variant.id || `${classId}-${era}`,
    depictedKitEra: era,
    depictedKitEvidence: variant.depictedKitEvidence || body.depictedKitEvidence || '',
  };
}

// A standing plate is worn-kit art only when its reviewed era is the campaign kit era.
// An unverified plate may still be shown, and the caller must say that the era is unverified.
export function bodyMatchesKit(body, age) {
  if (!body?.depictedKitEra) return false;
  return body.depictedKitEra === kitEra(age);
}

// Worn gear keeps the icon for that item's own age. Empty slots and artifacts have no gear plate.
export function selectGearIcon(icons, slot, item) {
  if (!item || item.kind === 'artifact' || !Number.isInteger(item.age)) return null;
  return (icons || []).find(icon => icon.slot === slot && icon.age === item.age) || null;
}

const weaponWearLayer = (file, rotate = 0) => ({
  file,
  aspect: 1.5,
  sourceAnchor: [0.78, 0.72],
  assetRole: 'held-prop',
  nativeAlpha: true,
  rotate,
});
const WORN_WEAPONS_BY_AGE = {
  0: weaponWearLayer('assets/derivatives/worn-gear-20261018/flint-club-stone.png'),
  1: weaponWearLayer('assets/derivatives/worn-gear-20261020/weapon-bronze.png'),
  2: weaponWearLayer('assets/derivatives/worn-gear-20261020/weapon-iron.png'),
  3: weaponWearLayer('assets/derivatives/worn-gear-20261020/weapon-medieval.png', -96),
  4: weaponWearLayer('assets/derivatives/worn-gear-20261020/weapon-gunpowder.png'),
  5: weaponWearLayer('assets/derivatives/worn-gear-20261020/weapon-industrial.png'),
  6: weaponWearLayer('assets/derivatives/worn-gear-20261020/weapon-modern.png'),
  7: weaponWearLayer('assets/derivatives/worn-gear-20261020/weapon-future.png'),
};
export function wornWeaponArt(item, classId = 'knight') {
  if (classId !== 'knight' || item?.kind !== 'gear' || item.slot !== 'weapon') return null;
  return WORN_WEAPONS_BY_AGE[item.age] || null;
}

// The forge can preview the age's generic workpiece for any class. This art is a recipe/carried-item
// illustration only; class-specific held-prop rules remain enforced by wornWeaponArt above.
export function forgeWeaponPreviewArt(age) {
  return Number.isInteger(age) ? WORN_WEAPONS_BY_AGE[age]?.file || null : null;
}

// Large source-backed workpiece pose for the Forge anvil in the 1376x768 scene.
// Keep the full diagonal blade left of the M22 recipe panel while it rests across the anvil.
const FORGE_WORKPIECE_FRAME = Object.freeze({ x: 285, y: 288.333, width: 500, height: 333.333, rotation: -33 });
export function forgeWeaponPreviewPose(age) {
  return forgeWeaponPreviewArt(age) ? { ...FORGE_WORKPIECE_FRAME } : null;
}

const HERO_WEARABLES = {
  knight: {
    helm: {
      7: {
        file: 'assets/derivatives/visual-repair-20261020/hero-gear/class-knight-future-helm-v1.png',
        aspect: 1144 / 1375,
        sourceAnchor: [0.5, 0.5],
        assetRole: 'wearable-layer',
        nativeAlpha: true,
      },
    },
    offhand: {
      7: {
        file: 'assets/derivatives/visual-repair-20261020/hero-gear/class-knight-future-offhand-v1.png',
        aspect: 1312 / 1199,
        sourceAnchor: [0.12, 0.83],
        assetRole: 'wearable-layer',
        nativeAlpha: true,
      },
    },
    armor: {
      7: {
        file: 'assets/derivatives/visual-repair-20261020/hero-gear/class-knight-future-armor-v1.png',
        aspect: 1222 / 1287,
        sourceAnchor: [0.5, 0.5],
        assetRole: 'wearable-layer',
        nativeAlpha: true,
      },
    },
    boots: {
      7: {
        file: 'assets/derivatives/visual-repair-20261020/hero-gear/class-knight-future-boots-v2.png',
        aspect: 1.5,
        sourceAnchor: [0.5, 0.45],
        fit: { w: 0.62, h: 0.25 },
        pairSplit: 0.5,
        pairAnchorY: 0.94,
        assetRole: 'wearable-layer',
        nativeAlpha: true,
      },
    },
    accessory: {
      7: {
        file: 'assets/derivatives/visual-repair-20261020/hero-gear/class-knight-future-accessory-v1.png',
        aspect: 1,
        sourceAnchor: [0.5, 0.5],
        fit: { w: 0.22, h: 0.16 },
        assetRole: 'wearable-layer',
        nativeAlpha: true,
      },
    },
  },
};
export function wornGearArt(item, classId = 'knight') {
  if (item?.kind !== 'gear') return null;
  if (item.slot === 'weapon') return wornWeaponArt(item, classId);
  return HERO_WEARABLES[classId]?.[item.slot]?.[item.age] || null;
}

export function bodyHasHeldWeapon(body) {
  return /\b(?:longsword|sword|staff|bow|rifle|carbine|club|cane|pistol|blade)\b/i.test(body?.depictedKitEvidence || '');
}

// Fits the body so its feet rest on `footY` and its height is at most `height` world px,
// then applies the CSS cap from the contract. Returns the drawn box or null.
export function fitBody(body, footX, footY, height, cssScale) {
  if (!body) return null;
  const fitted = visibleBox({ width: body.width, height: body.height, maxVisibleCssPx: body.maxVisibleCssPx || heroBodies.maxVisibleCssPx }, height, cssScale);
  const x = footX - body.foot[0] * fitted.width;
  const y = footY - body.foot[1] * fitted.height;
  return { x, y, width: fitted.width, height: fitted.height, cssHeight: fitted.cssHeight };
}

function paintBackdrop(world, element, stage) {
  const defs = element('defs', {});
  const material = 'assets/production/production-12-20261003/images/15-supporting-ui-materials.png';
  // The reviewed material board contains real stone grain in this rectangle.
  // Crop in SVG at native density; no reference-screen UI is installed as a room.
  const masonry = element('pattern', { id: 'hero-masonry', patternUnits: 'userSpaceOnUse', width: 280, height: 144 });
  for (let row = 0; row < 2; row++) for (let column = -1; column < 3; column++) {
    const x = column * 140 + (row ? 70 : 0), y = row * 72;
    const tile = element('svg', { x: x + 2, y: y + 2, width: 136, height: 68, viewBox: '38 172 136 68', preserveAspectRatio: 'none' });
    tile.append(element('image', { href: material, width: 1024, height: 1024 }));
    masonry.append(tile);
  }
  defs.append(masonry);
  const wall = element('linearGradient', { id: 'hero-wall', x1: 0, y1: 0, x2: 0, y2: 1 });
  wall.append(element('stop', { offset: '0', 'stop-color': '#1d1a17' }), element('stop', { offset: '0.55', 'stop-color': '#2c2622' }), element('stop', { offset: '1', 'stop-color': '#3a302a' }));
  const floor = element('linearGradient', { id: 'hero-floor', x1: 0, y1: 0, x2: 0, y2: 1 });
  floor.append(element('stop', { offset: '0', 'stop-color': '#4a3f36' }), element('stop', { offset: '1', 'stop-color': '#221c18' }));
  const glow = element('radialGradient', { id: 'hero-glow', cx: '0.5', cy: '0.45', r: '0.55' });
  glow.append(element('stop', { offset: '0', 'stop-color': '#c9a35b', 'stop-opacity': '0.28' }), element('stop', { offset: '1', 'stop-color': '#c9a35b', 'stop-opacity': '0' }));
  defs.append(wall, floor, glow);
  world.append(defs);
  world.append(element('rect', { x: -260, y: -40, width: 1896, height: 848, fill: 'url(#hero-wall)', 'data-backdrop': 'native-svg-room' }));
  world.append(element('image', { href: 'assets/production/production-12-20261003/images/04-supporting-chapter-4.png', x: -260, y: -40, width: 1896, height: 848, preserveAspectRatio: 'xMidYMid slice', opacity: 0.28 }));
  world.append(element('image', { href: 'assets/derivatives/mock-led-20261016/chambers/chamber-armory.png', x: -260, y: -40, width: 1896, height: 848, preserveAspectRatio: 'xMidYMid slice', opacity: 0.96, 'data-chamber-art': 'chamber-armory' }));
  world.append(element('rect', { width: 1376, height: 560, fill: 'url(#hero-masonry)', opacity: 0.12, 'data-material-source': material }));
  for (const x of [104, 1188]) {
    world.append(element('path', { d: `M${x},0 h64 v560 h-64 Z`, fill: '#201b16', stroke: '#66543b', 'stroke-width': 4, opacity: 0.26 }));
    world.append(element('path', { d: `M${x + 10},0 v548`, stroke: '#9c8052', 'stroke-width': 3, opacity: 0.16 }));
  }
  world.append(element('path', { d: 'M-260,540 H1636 V808 H-260 Z', fill: 'url(#hero-floor)', opacity: 0.25 }));
  // Floor joints follow the room's central vanishing point; feet land on this floor.
  for (const x of [-600, -120, 300, 688, 1076, 1496, 1976]) world.append(element('path', { d: `M688,510 L${x},768`, fill: 'none', stroke: '#1b1713', 'stroke-width': 3, opacity: 0.28 }));
  for (const y of [552, 585, 633, 696, 767]) world.append(element('path', { d: `M0,${y} H1376`, fill: 'none', stroke: '#211a14', 'stroke-width': 3, opacity: 0.32 }));
  world.append(element('path', { d: 'M0,0 H1376 V768 H0 Z', fill: 'url(#hero-glow)', 'pointer-events': 'none' }));
  world.append(element('ellipse', { cx: stage.figure.x, cy: stage.ground.y, rx: 420, ry: 300, fill: 'url(#hero-glow)' }));
  world.append(element('ellipse', { cx: stage.figure.x, cy: stage.ground.y + 4, rx: 168, ry: 24, fill: 'rgba(216, 177, 90, 0.16)', stroke: 'rgba(216, 177, 90, 0.52)', 'stroke-width': 2 }));
  world.append(element('ellipse', { cx: stage.figure.x, cy: stage.ground.y + 2, rx: 150, ry: 18, fill: '#00000088', 'data-ground': 'shadow' }));
}

function paintPortrait(world, element, ctx, stage, classId, portrait, reason) {
  const box = stage.card;
  const side = Math.min(box.width, box.height - 120);
  const group = element('g', {
    'data-actor': classId,
    'data-clip': 'idle',
    'data-presentation': 'portrait-card',
    'data-articulation': 'card-bounded',
    'data-body-reason': reason,
    'data-card-box': `${box.x},${box.y},${box.width},${box.height}`,
  });
  group.append(element('rect', { x: box.x + (box.width - side) / 2 - 10, y: box.y + 50, width: side + 20, height: side + 20, rx: 8, fill: '#1c2428', stroke: '#c9a35b', 'stroke-width': 3, 'data-ground': 'plinth' }));
  if (portrait) {
    group.append(element('image', { href: portrait.file, x: box.x + (box.width - side) / 2, y: box.y + 60, width: side, height: side, 'data-card-era': portrait.era, 'data-card-status': 'bounded-card' }));
  }
  world.append(group);
}

// Equipped items only. A Compare selection stays in the bag and is not a worn mark.
export function wornMarks(state) {
  const items = wornPayload(state).items;
  return Object.keys(WORN_ANCHORS).map(slot => {
    const item = items[slot] || null;
    const attached = isWearLayerSupported(slot, item?.wearLayer);
    return {
      slot,
      worn: Boolean(item),
      id: item?.id || '',
      bonus: item?.bonus || '',
      socketIcon: item?.icon || '',
      iconId: item?.iconId || '',
      appearance: attached ? 'attached-asset' : item ? 'socket-only' : 'empty',
      appearanceFile: attached ? item.wearLayer.file : '',
      anchor: attached ? WORN_ANCHORS[slot] : null,
    };
  });
}

export function heroKitCaption(state) {
  const body = heroBody(state?.hero?.class, state?.age);
  const era = kitEra(state?.age);
  const worn = wornMarks(state).filter(mark => mark.worn);
  const attached = worn.filter(mark => mark.appearance === 'attached-asset');
  const socketOnly = worn.filter(mark => mark.appearance === 'socket-only');
  const wornLine = attached.length || socketOnly.length
    ? [
      attached.length ? 'Attached ' + attached.map(mark => mark.slot).join(', ') + '.' : '',
      socketOnly.length ? 'Equipped ' + socketOnly.map(mark => mark.slot).join(', ') + ' remain represented in their slots.' : '',
    ].filter(Boolean).join(' ')
    : 'Empty slots stay empty.';
  if (!body) return 'No standing body exists for this class. The portrait card stands in.';
  if (bodyMatchesKit(body, state?.age)) return `Standing plate is the ${era} kit. ${wornLine}`;
  if (body.depictedKitEra) return `This plate is ${body.depictedKitEra} kit. It is not the ${era} kit. ${wornLine}`;
  return 'The era of this standing plate is unverified. It is not proof of worn gear.';
}

function wornPayload(state) {
  const items = {};
  for (const slot of ['helm', 'weapon', 'offhand', 'armor', 'boots', 'accessory']) {
    const item = state?.hero?.equip?.[slot];
    if (!item) continue;
    const bonus = item.kind === 'gear' ? gearBonus(item) : {};
    const icon = selectGearIcon(gearIcons.icons, slot, item);
    const body = slot === 'weapon' ? heroBody(state?.hero?.class, state?.age) : null;
    const bodyAlreadyShowsWeapon = bodyHasHeldWeapon(body);
    const wearLayer = slot === 'weapon' && bodyAlreadyShowsWeapon
      ? null
      : wornGearArt(item, state?.hero?.class);
    items[slot] = {
      id: item.id || slot,
      bonus: Object.entries(bonus).map(([key, amount]) => `${key}+${amount}`).join(','),
      icon: icon?.file || '',
      iconId: icon?.id || '',
      wearLayer,
    };
  }
  return { items };
}

function paintEquippedSockets(group, element, state, fitted) {
  paintWornSlots(group, element, wornPayload(state), fitted);
}

// Slot cards, class cards and copy live in the CSS overlay. The world keeps the figure and the room.
export function drawHeroRoom(world, element, ctx) {
  const stage = heroStage();
  if (ctx.inventoryMode) {
    stage.figure.x = 420;
    stage.card.x = 180;
  }
  const state = ctx.state;
  world.setAttribute('data-screen', 'hero-room');
  paintBackdrop(world, element, stage);
  const classId = state.hero.class;
  const body = heroBody(classId, state.age);
  const portrait = ctx.portraitCard(classId, state.age) || ctx.pendingPortrait(classId, state.age);
  const kitMatches = body && bodyMatchesKit(body, state.age);
  if (body) {
    const fitted = fitBody(body, stage.figure.x, stage.ground.y, stage.card.height, ctx.cssScale);
    const matchStatus = kitMatches ? '1' : body.depictedKitEra ? 'mismatch' : 'unverified';
    const reason = kitMatches ? '' : body.depictedKitEra ? 'kit-era-mismatch' : 'unverified';
    const props = (body.assembly?.classFocusProps || []).join(',');
    const group = element('g', { 'data-actor': classId, 'data-clip': 'idle', 'data-presentation': 'standing-body', 'data-articulation': 'static-standing', 'data-kit-match': matchStatus, 'data-body-reason': reason, 'data-class-focus': props, 'data-card-box': `${stage.card.x},${stage.card.y},${stage.card.width},${stage.card.height}` });
    group.append(element('image', { href: body.file, x: fitted.x, y: fitted.y, width: fitted.width, height: fitted.height, 'data-body': body.id, 'data-body-sha256': body.sha256, 'data-depicted-kit': body.depictedKitEra || 'unverified', 'data-visible-css-height': String(Math.round(fitted.cssHeight)) }));
    paintEquippedSockets(group, element, state, fitted);
    world.append(group);
  } else {
    paintPortrait(world, element, ctx, stage, classId, portrait, 'no-standing-body');
  }
  return stage;
}
