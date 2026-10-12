// Hero equipment room. Draws the realistic standing class body (hero-bodies-20261011), six slot
// cards with gear icons, class choice cards and the stat strip into the 1376x768 world.
// The backdrop is native SVG (no interior painting exists); it is labelled as such in data-backdrop.
import heroBodies from '../data/hero-bodies-20261011.json' with { type: 'json' };
import gearIcons from '../data/gear-icons-20261007.json' with { type: 'json' };
import { HERO_SLOT_COLUMNS, heroStage } from './presentation.js';
import { visibleBox } from './visible-size.js';

// Four kit eras across eight ages (MASTER-PLAN): ancient, medieval, powder, mech.
export function kitEra(age) {
  return ['ancient', 'ancient', 'ancient', 'medieval', 'powder', 'powder', 'mech', 'mech'][age] || 'ancient';
}

export function heroBody(classId) {
  return heroBodies.bodies?.[classId] || null;
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
  const wall = element('linearGradient', { id: 'hero-wall', x1: 0, y1: 0, x2: 0, y2: 1 });
  wall.append(element('stop', { offset: '0', 'stop-color': '#1d1a17' }), element('stop', { offset: '0.55', 'stop-color': '#2c2622' }), element('stop', { offset: '1', 'stop-color': '#3a302a' }));
  const floor = element('linearGradient', { id: 'hero-floor', x1: 0, y1: 0, x2: 0, y2: 1 });
  floor.append(element('stop', { offset: '0', 'stop-color': '#4a3f36' }), element('stop', { offset: '1', 'stop-color': '#221c18' }));
  const glow = element('radialGradient', { id: 'hero-glow', cx: '0.5', cy: '0.45', r: '0.55' });
  glow.append(element('stop', { offset: '0', 'stop-color': '#c9a35b', 'stop-opacity': '0.28' }), element('stop', { offset: '1', 'stop-color': '#c9a35b', 'stop-opacity': '0' }));
  defs.append(wall, floor, glow);
  world.append(defs);
  world.append(element('rect', { width: 1376, height: 768, fill: 'url(#hero-wall)', 'data-backdrop': 'native-svg-room' }));
  world.append(element('rect', { x: 0, y: stage.ground.y - 6, width: 1376, height: 768 - stage.ground.y + 6, fill: 'url(#hero-floor)' }));
  world.append(element('ellipse', { cx: stage.figure.x, cy: stage.ground.y, rx: 420, ry: 300, fill: 'url(#hero-glow)' }));
  world.append(element('ellipse', { cx: stage.figure.x, cy: stage.ground.y + 2, rx: 150, ry: 18, fill: '#00000066', 'data-ground': 'shadow' }));
  world.append(element('line', { x1: stage.ground.x1, y1: stage.ground.y, x2: stage.ground.x2, y2: stage.ground.y, stroke: '#8c7447', 'stroke-width': 2, opacity: 0.6 }));
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

function paintEquippedSockets(group, element, state, fitted) {
  if (!state?.hero?.equip || !fitted) return;
  const sockets = [
    { slot: 'weapon', x: fitted.x + fitted.width * 0.76, y: fitted.y + fitted.height * 0.44, size: 84 },
    { slot: 'offhand', x: fitted.x - 24, y: fitted.y + fitted.height * 0.48, size: 84 },
    { slot: 'helm', x: fitted.x + (fitted.width - 76) / 2, y: fitted.y - 28, size: 76 },
  ];
  for (const s of sockets) {
    const item = state.hero.equip[s.slot];
    if (!item) continue;
    const icon = selectGearIcon(gearIcons.icons, s.slot, item);
    if (icon?.file) {
      const g = element('g', { 'data-socket': s.slot, 'data-socket-item': item.id || s.slot });
      g.append(element('image', {
        href: icon.file,
        x: s.x,
        y: s.y,
        width: s.size,
        height: s.size,
        'data-gear-icon': icon.id,
      }));
      group.append(g);
    }
  }
}

// Slot cards, class cards and copy live in the CSS overlay. The world keeps the figure and the room.
export function drawHeroRoom(world, element, ctx) {
  const stage = heroStage();
  const state = ctx.state;
  world.setAttribute('data-screen', 'hero-room');
  paintBackdrop(world, element, stage);
  const classId = state.hero.class;
  const body = heroBody(classId);
  const portrait = ctx.portraitCard(classId, state.age) || ctx.pendingPortrait(classId, state.age);
  const kitMatches = body && bodyMatchesKit(body, state.age);
  if (body) {
    const fitted = fitBody(body, stage.figure.x, stage.ground.y, stage.card.height, ctx.cssScale);
    const matchStatus = kitMatches ? '1' : body.depictedKitEra ? 'mismatch' : 'unverified';
    const group = element('g', { 'data-actor': classId, 'data-clip': 'idle', 'data-presentation': 'standing-body', 'data-articulation': 'static-standing', 'data-kit-match': matchStatus, 'data-card-box': `${stage.card.x},${stage.card.y},${stage.card.width},${stage.card.height}` });
    group.append(element('image', { href: body.file, x: fitted.x, y: fitted.y, width: fitted.width, height: fitted.height, 'data-body': body.id, 'data-body-sha256': body.sha256, 'data-depicted-kit': body.depictedKitEra || 'unverified', 'data-visible-css-height': String(Math.round(fitted.cssHeight)) }));
    paintEquippedSockets(group, element, state, fitted);
    world.append(group);
  } else {
    paintPortrait(world, element, ctx, stage, classId, portrait, 'no-standing-body');
  }
  return stage;
}
