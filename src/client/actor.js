// Measured part assembly. Joints rotate. The whole sheet is never shown as the actor.
import atlas from '../data/actor-atlas.json' with { type: 'json' };
import reviewMount from '../data/mount-review-v1.json' with { type: 'json' };
import staticMounts from '../data/static-mounts-v1.json' with { type: 'json' };
import plates from '../data/plate-catalog.json' with { type: 'json' };
import plateOverrides from '../data/plate-overrides-20261007.json' with { type: 'json' };
import { hoofContact, pose } from './rig.js';
import { visibleBox } from './visible-size.js';

let worldCssPerUnit = 1;
let actorImages = new Map();
let reusableImages = new Map();
export function beginActorFrame() {
  reusableImages = actorImages;
  actorImages = new Map();
}
function actorImage(element, attributes) {
  const key = attributes.href;
  const available = reusableImages.get(key);
  const image = available?.pop() || element('image', attributes);
  if (!image?.attributes || typeof image.getAttribute !== 'function' || typeof image.setAttribute !== 'function' || typeof image.removeAttribute !== 'function') return image;
  for (const attribute of [...image.attributes]) {
    if (!(attribute.name in attributes)) image.removeAttribute(attribute.name);
  }
  for (const [name, value] of Object.entries(attributes)) {
    if (image.getAttribute(name) !== String(value)) image.setAttribute(name, value);
  }
  if (!actorImages.has(key)) actorImages.set(key, []);
  actorImages.get(key).push(image);
  return image;
}
export function setWorldCssScale(scale) {
  worldCssPerUnit = Number.isFinite(scale) && scale > 0 ? scale : 1;
}
// Reviewed subject failures. The role name stays canonical. The plate must not be treated as that subject.
const PLATE_LIMITS = {
  troops: {},
};
function plateView(group, key, plate) {
  if (!plate) return null;
  const extra = plateOverrides[group]?.[key];
  const view = extra ? { ...plate, ...extra } : { ...plate };
  if (PLATE_LIMITS[group]?.[key]) view.semanticLimit = PLATE_LIMITS[group][key];
  return view;
}

export function clipAngles(clip, t, reduced = false) {
  const u = reduced ? 0 : ((t % 1) + 1) % 1;
  const swing = Math.sin(u * Math.PI * 2);
  const pose = { thighL: 8, thighR: -6, shinL: 4, shinR: 6, arm: 14, forearm: 8, weapon: 16, spine: 0, head: 0 };
  if (clip === 'walk') {
    pose.thighL = swing * 32;
    pose.thighR = -swing * 32;
    pose.shinL = Math.max(0, swing) * 28;
    pose.shinR = Math.max(0, -swing) * 28;
    pose.arm = -swing * 22;
    pose.forearm = 12;
  } else if (clip === 'work') {
    pose.arm = -55 + swing * 46;
    pose.forearm = -24 + swing * 20;
    pose.weapon = -10 + swing * 16;
    pose.thighL = 10;
  } else if (clip === 'attack') {
    pose.arm = -78 + u * 150;
    pose.forearm = -36 + u * 48;
    pose.weapon = -50 + u * 100;
    pose.spine = -8;
    pose.head = -4;
  } else if (clip === 'cast') {
    pose.arm = -70 + swing * 25;
    pose.forearm = -45 + swing * 15;
    pose.weapon = -30 + swing * 20;
    pose.spine = -6;
    pose.head = -2;
  } else if (clip === 'buff') {
    pose.arm = -48 + swing * 18;
    pose.forearm = -28 + swing * 10;
    pose.weapon = -12 + swing * 12;
    pose.spine = -4;
    pose.head = -4;
  } else if (clip === 'heal') {
    pose.arm = -42 + swing * 14;
    pose.forearm = -24 + swing * 10;
    pose.weapon = -8 + swing * 8;
    pose.spine = -3;
    pose.head = -3;
  } else if (clip === 'debuff') {
    pose.spine = 8;
    pose.head = 6;
    pose.arm = 18;
    pose.forearm = 12;
  } else if (clip === 'hit') {
    pose.spine = 26;
    pose.head = 18;
    pose.arm = 34;
    pose.forearm = 20;
  } else if (clip === 'death') {
    pose.spine = 78;
    pose.thighL = 20;
    pose.thighR = 12;
    pose.shinL = 16;
    pose.arm = 42;
    pose.head = 20;
  } else if (clip === 'mountWalk') {
    pose.thighL = 34;
    pose.thighR = 30;
    pose.shinL = 48;
    pose.shinR = 44;
    pose.spine = -4;
  }
  return pose;
}

export function mountGait(t, reduced = false) {
  const u = reduced ? 0 : ((t % 1) + 1) % 1;
  return [0, 0.5, 0.25, 0.75].map(phase => {
    const local = (u - phase + 1) % 1;
    return !reduced && local > 0.12 && local < 0.42 ? -32 : 6;
  });
}

function sheetCrop(element, href, box, pivot) {
  const [bx, by, bw, bh] = box;
  const [px, py] = pivot;
  const group = element('g', { transform: `translate(${-bw * px} ${-bh * py})` });
  const crop = element('svg', { x: 0, y: 0, width: bw, height: bh, viewBox: `${bx} ${by} ${bw} ${bh}`, overflow: 'hidden', preserveAspectRatio: 'none' });
  crop.append(actorImage(element, { href: new URL(`../../${href}`, import.meta.url).href, x: 0, y: 0, width: 1024, height: 1024 }));
  group.append(crop);
  return { node: group, length: bh * (1 - py) };
}
function partNode(element, spec, name, href) {
  const box = spec.parts?.[name];
  if (!box) return null;
  return sheetCrop(element, href, box, spec.pivots[name] || [0.5, 0.1]);
}

function chain(element, parent, spec, href, names, angles, x, y) {
  let host = parent;
  let first = true;
  names.forEach((name, index) => {
    const part = partNode(element, spec, name, href);
    if (!part) return;
    const group = element('g', {
      transform: first
        ? `translate(${x} ${y}) rotate(${angles[index] || 0})`
        : `translate(0 ${host.__len || 0}) rotate(${angles[index] || 0})`,
      'data-joint': name,
      'data-angle': String(angles[index] || 0),
    });
    group.append(part.node);
    group.__len = part.length;
    host.append(group);
    host = group;
    first = false;
  });
  return host;
}

function landmarks(spec) {
  const torso = spec.parts.torso;
  const pivot = spec.pivots?.torso || [0.5, 0.92];
  const hipY = -torso[3] * (1 - pivot[1]);
  return {
    farHip: [-torso[2] * 0.22, hipY],
    nearHip: [torso[2] * 0.18, hipY + torso[3] * 0.02],
    neck: [(pivot[0] - 0.5) * torso[2], -torso[3] * 0.9],
    shoulder: [torso[2] * 0.3, -torso[3] * 0.72],
  };
}

function inkLine(element, parent, a, b, width = 5) {
  parent.append(element('line', {
    x1: a[0], y1: a[1], x2: b[0], y2: b[1], stroke: '#f1e4cf', 'stroke-width': width, 'stroke-linecap': 'round',
  }));
}

// Named rig slices and the floored horse are not world sprites. Feet stay on y=0 unless the clip lifts them.
export function drawSchematic(world, element, x, y, { facing = 1, scale = 1, clip = 'idle', time = 0, reduced = false, mounted = false, moving = false, rider = 'stick' } = {}) {
  const clipName = mounted ? 'mountWalk' : clip;
  const sample = pose(clipName, time, { reduced: reduced || (mounted && !moving) });
  const u = reduced ? 0 : ((time % 1) + 1) % 1;
  const swing = Math.sin(u * Math.PI * 2);
  const root = element('g', {
    transform: `translate(${x} ${y}) scale(${facing * scale} ${scale})`,
    'data-articulation': 'schematic',
    'data-clip': clipName,
    'data-mounted': mounted ? '1' : '0',
    'data-planted': String(hoofContact(sample)),
    'data-named-parts': 'withheld',
    'data-mount-mark': mounted ? 'schematic-horse' : 'none',
    'data-rider': mounted ? rider : 'none',
  });
  root.append(element('ellipse', { cx: mounted ? -4 : 0, cy: 4, rx: mounted ? 46 : 16, ry: 5, fill: '#00000066' }));
  if (mounted) {
    const phases = [0, 0.25, 0.5, 0.75];
    const hips = [[24, -24], [12, -24], [-16, -22], [-28, -22]];
    hips.forEach((hip, index) => {
      const local = (u - phases[index] + 1) % 1;
      const lifted = moving && !reduced && local > 0.12 && local < 0.42;
      const knee = [hip[0] + (lifted ? 8 : 1), lifted ? -16 : -12];
      const hoof = [hip[0] + (lifted ? 12 : 2), lifted ? -14 : 0];
      inkLine(element, root, hip, knee, 5);
      inkLine(element, root, knee, hoof, 5);
    });
    root.append(element('path', {
      d: 'M-40,-24 C-46,-40 -36,-52 -16,-50 C2,-56 18,-48 28,-38 L40,-54 C52,-66 64,-62 62,-50 C60,-42 50,-40 42,-36 C34,-26 16,-22 0,-24 C-16,-22 -30,-22 -40,-24 Z',
      fill: '#8c6239', stroke: '#f1e4cf', 'stroke-width': 2,
    }));
    root.append(element('path', { d: 'M-38,-36 C-48,-30 -52,-18 -46,-12', fill: 'none', stroke: '#5c3a22', 'stroke-width': 3, 'stroke-linecap': 'round' }));
    root.append(element('ellipse', { cx: -6, cy: -50, rx: 11, ry: 4, fill: '#5c3a22', stroke: '#f1e4cf' }));
    if (rider !== 'omit') {
      inkLine(element, root, [-6, -52], [-8, -74], 4);
      root.append(element('circle', { cx: -8, cy: -82, r: 7, fill: '#f1e4cf' }));
      inkLine(element, root, [-8, -68], [6, -56], 3);
    }
  } else {
    const acting = clip === 'attack' || clip === 'work';
    const hit = clip === 'hit' ? 10 : clip === 'death' ? 28 : 0;
    const liftL = clip === 'walk' && !reduced ? Math.max(0, swing) * 18 : 0;
    const liftR = clip === 'walk' && !reduced ? Math.max(0, -swing) * 18 : 0;
    const hip = [hit * 0.2, -34];
    const chest = [hit * 0.45, -58];
    const head = [hit * 0.7, -76];
    const hand = [acting ? 16 - swing * 10 : 12, acting ? -70 : -50];
    inkLine(element, root, hip, [-8 + swing * 6, -18]);
    inkLine(element, root, [-8 + swing * 6, -18], [-10, -liftL]);
    inkLine(element, root, hip, [8 - swing * 6, -18]);
    inkLine(element, root, [8 - swing * 6, -18], [10, -liftR]);
    inkLine(element, root, hip, chest);
    inkLine(element, root, chest, head);
    inkLine(element, root, chest, hand);
    root.append(element('circle', { cx: head[0], cy: head[1], r: 7, fill: '#f1e4cf' }));
    if (acting) inkLine(element, root, hand, [hand[0] + 8, hand[1] + 22], 3);
  }
  world.append(root);
  return root;
}

// Fractions of the standing figure. The icon is drawn at this anchor, not in a floating card.
export const WORN_ANCHORS = {
  helm: [0.5, 0.08],
  weapon: [0.88, 0.53],
  offhand: [0.13, 0.53],
  armor: [0.5, 0.36],
  boots: [0.5, 0.92],
  accessory: [0.5, 0.19],
};
const WORN_PLACES = WORN_ANCHORS;

// Body attachments are stricter than item icons. Only a reviewed native-alpha wearable
// layer or held prop with a local source and declared role may appear on the anatomy.
export function isWearLayerSupported(slot, layer) {
  const role = slot === 'weapon' ? 'held-prop' : 'wearable-layer';
  return Boolean(
    WORN_PLACES[slot] &&
    layer &&
    typeof layer.file === 'string' &&
    layer.file.startsWith('assets/') &&
    !/^https?:/i.test(layer.file) &&
    layer.assetRole === role &&
    layer.nativeAlpha === true &&
    Number.isFinite(layer.aspect) && layer.aspect > 0 &&
    (!layer.fit || (Number.isFinite(layer.fit.w) && layer.fit.w > 0 && layer.fit.w <= 1.5 && Number.isFinite(layer.fit.h) && layer.fit.h > 0 && layer.fit.h <= 1.5)) &&
    Array.isArray(layer.sourceAnchor) && layer.sourceAnchor.length === 2 &&
    layer.sourceAnchor.every(value => Number.isFinite(value) && value >= 0 && value <= 1)
  );
}

export function shouldDrawRigWeapon(worn) {
  if (worn == null) return true;
  const weapon = worn.items?.weapon;
  return Boolean(weapon) && !isWearLayerSupported('weapon', weapon.wearLayer);
}

// Box fractions are intentionally sized against a standing figure, then fit without stretching.
// The destination is the real attachment point, not the centre of a floating inventory plate.
const SLOT_FIT = {
  helm: { w: 0.28, h: 0.15, rotate: 0, source: [0.5, 0.5] },
  weapon: { w: 0.54, h: 0.31, rotate: 0, source: [0.72, 0.52] },
  offhand: { w: 0.33, h: 0.27, rotate: 0, source: [0.5, 0.5] },
  armor: { w: 0.56, h: 0.34, rotate: 0, source: [0.5, 0.5] },
  boots: { w: 0.32, h: 0.16, rotate: 0, source: [0.5, 0.5] },
  accessory: { w: 0.13, h: 0.11, rotate: 0, source: [0.5, 0.5] },
};

export function paintWornSlots(group, element, worn, box, { slots = Object.keys(WORN_PLACES), attachedTo = null } = {}) {
  if (!group || !box) return;
  const items = worn?.items || {};
  for (const slot of slots) {
    const item = items[slot] || null;
    const wearLayer = item?.wearLayer || null;
    const attached = isWearLayerSupported(slot, wearLayer);
    const [fx, fy] = WORN_PLACES[slot];
    const attributes = {
      'data-worn-slot': slot,
      'data-worn-state': item ? 'worn' : 'empty',
      'data-worn-appearance': attached ? 'attached-asset' : item ? 'socket-only' : 'empty',
      'data-worn-item': item?.id || '',
    };
    if (attachedTo) attributes['data-attached-to'] = attachedTo;
    const node = element('g', attributes);
    if (attached) {
      const fit = SLOT_FIT[slot];
      const fitted = wearLayer.fit || fit;
      const maxWidth = box.width * fitted.w;
      const maxHeight = box.height * fitted.h;
      const drawHeight = Math.min(maxHeight, maxWidth / wearLayer.aspect);
      const drawWidth = drawHeight * wearLayer.aspect;
      const cx = box.x + box.width * fx;
      const cy = box.y + box.height * fy;
      const [sourceX, sourceY] = wearLayer.sourceAnchor;
      const rotation = Number.isFinite(wearLayer.rotate) ? wearLayer.rotate : fit.rotate;
      const layer = element('g', {
        transform: `translate(${cx} ${cy}) rotate(${rotation})`,
        'data-slot-layer': slot,
        'data-anchor': `${fx},${fy}`,
        'data-source-anchor': `${sourceX},${sourceY}`,
      });
      layer.append(element('image', {
        href: wearLayer.file,
        class: 'worn-gear-art',
        preserveAspectRatio: 'xMidYMid meet',
        x: -drawWidth * sourceX,
        y: -drawHeight * sourceY,
        width: drawWidth,
        height: drawHeight,
        'data-wear-layer-role': wearLayer.assetRole,
        'data-wear-layer-source': wearLayer.file,
      }));
      node.append(layer);
    }
    group.append(node);
  }
}


function paintWornBootPair(body, element, worn, box, feet) {
  const item = worn?.items?.boots || null;
  const layer = item?.wearLayer || null;
  const split = layer?.pairSplit;
  const anchorY = layer?.pairAnchorY;
  const supportedPair = isWearLayerSupported('boots', layer)
    && Number.isFinite(split) && split > 0 && split < 1
    && Number.isFinite(anchorY) && anchorY >= 0 && anchorY <= 1
    && feet?.far && feet?.near;
  if (!supportedPair) {
    paintWornSlots(body, element, worn, box, { slots: ['boots'], attachedTo: 'spine' });
    return;
  }

  const fit = layer.fit || SLOT_FIT.boots;
  const maxWidth = box.width * fit.w;
  const maxHeight = box.height * fit.h;
  const drawHeight = Math.min(maxHeight, maxWidth / layer.aspect);
  const shoeWidth = drawHeight * layer.aspect * split;
  for (const [side, foot, sourceX] of [['far', feet.far, 0], ['near', feet.near, split]]) {
    const overlay = element('g', {
      'data-worn-slot': 'boots',
      'data-worn-state': 'worn',
      'data-worn-appearance': 'attached-asset',
      'data-worn-item': item.id || '',
      'data-attached-to': 'foot',
      'data-boot-side': side,
    });
    const crop = element('svg', {
      x: -shoeWidth / 2,
      y: (foot.__len || 0) - drawHeight * anchorY,
      width: shoeWidth,
      height: drawHeight,
      viewBox: `${sourceX} 0 ${split} 1`,
      preserveAspectRatio: 'none',
      overflow: 'hidden',
      'data-boot-overlay': side,
    });
    crop.append(element('image', {
      href: layer.file,
      x: 0,
      y: 0,
      width: 1,
      height: 1,
      preserveAspectRatio: 'none',
      'data-wear-layer-role': layer.assetRole,
      'data-wear-layer-source': layer.file,
    }));
    overlay.append(crop);
    foot.append(overlay);
  }
}

const JOINTS = ['head', 'torso', 'arm', 'forearm', 'thigh', 'shin', 'foot'];

export function drawActor(world, element, classId, { x, y, scale = 0.2, facing = 1, clip = 'idle', time = 0, reduced = false, worn = null } = {}) {
  const spec = atlas.classes[classId] || atlas.classes.knight;
  const limbs = spec?.parts || {};
  if (!atlas.worldReady || JOINTS.some(name => !limbs[name])) return null;
  const pose = clipAngles(clip, time, reduced);
  const marks = landmarks(spec);
  const root = element('g', {
    transform: `translate(${x} ${y}) scale(${facing * scale} ${scale})`,
    'data-actor': classId,
    'data-clip': clip,
    'data-gait': 'per-joint',
    'data-spine': String(pose.spine),
    'data-arm': String(pose.arm),
    'data-forearm': String(pose.forearm),
    'data-thigh': String(pose.thighL),
    'data-shin': String(pose.shinL),
  });
  root.append(element('ellipse', { cx: 0, cy: 6, rx: 70, ry: 16, fill: '#00000066' }));
  const body = element('g', { transform: `rotate(${pose.spine})`, 'data-joint': 'spine' });
  const torso = spec.parts.torso;
  const farFoot = chain(element, body, spec, spec.file, ['thigh', 'shin', 'foot'], [pose.thighL, pose.shinL, 0], marks.farHip[0], marks.farHip[1]);
  const trunk = partNode(element, spec, 'torso', spec.file);
  let headJoint = null;
  if (trunk) {
    const placed = element('g', { 'data-joint': 'torso' });
    placed.append(trunk.node);
    body.append(placed);
    const head = partNode(element, spec, 'head', spec.file);
    if (head) {
      const neck = element('g', { transform: `translate(${marks.neck[0]} ${marks.neck[1]}) rotate(${pose.head})`, 'data-joint': 'neck' });
      neck.append(head.node);
      placed.append(neck);
      headJoint = neck;
    }
  }
  const nearFoot = chain(element, body, spec, spec.file, ['thigh', 'shin', 'foot'], [pose.thighR, pose.shinR, 0], marks.nearHip[0], marks.nearHip[1]);
  const armHost = body.querySelector?.('[data-joint="torso"]') || body;
  const rigWeapon = shouldDrawRigWeapon(worn);
  const armParts = ['arm', 'forearm', ...(rigWeapon ? ['weapon'] : [])].filter(name => spec.parts[name]);
  const armAngles = { arm: pose.arm, forearm: pose.forearm, weapon: pose.weapon };
  const armEnd = chain(element, armHost, spec, spec.file, armParts, armParts.map(name => armAngles[name]), marks.shoulder[0], marks.shoulder[1]);
  root.append(body);
  const span = torso[3] + 40;
  const wornBox = { x: -span * 0.35, y: -span, width: span * 0.7, height: span };
  paintWornSlots(body, element, worn, wornBox, { slots: ['offhand', 'armor', 'accessory'], attachedTo: 'spine' });
  paintWornBootPair(body, element, worn, wornBox, { far: farFoot, near: nearFoot });
  const headBox = headJoint
    ? { ...wornBox, x: wornBox.x - marks.neck[0], y: wornBox.y - marks.neck[1] }
    : wornBox;
  paintWornSlots(headJoint || body, element, worn, headBox, { slots: ['helm'], attachedTo: headJoint ? 'head' : 'spine' });
  const weapon = worn?.items?.weapon?.wearLayer;
  if (isWearLayerSupported('weapon', weapon) && armEnd) {
    const [fx, fy] = WORN_ANCHORS.weapon;
    const handBox = { ...wornBox, x: wornBox.x - wornBox.width * fx, y: wornBox.y - wornBox.height * fy };
    const hand = element('g', {
      transform: `translate(0 ${armEnd.__len || 0}) rotate(${pose.weapon})`,
      'data-joint': 'weapon',
      'data-angle': String(pose.weapon),
    });
    paintWornSlots(hand, element, worn, handBox, { slots: ['weapon'], attachedTo: 'hand' });
    armEnd.append(hand);
  } else {
    paintWornSlots(root, element, worn, wornBox, { slots: ['weapon'], attachedTo: 'root' });
  }
  world.append(root);
  return root;
}

export function mountReview() {
  return reviewMount;
}

// One painted horse image. Hooves are not separate parts, so the gait stays a still pose plus a small bob.
export function drawReviewMount(world, element, { x, y, facing = 1, time = 0, reduced = false, moving = false } = {}) {
  if (reviewMount.status !== 'BOUNDED_REVIEW_SAMPLE_RESIDUAL_HAIRLINE' || reviewMount.gait !== 'single-pose') return null;
  const [x0, y0, x1, y1] = reviewMount.tightBBox;
  const bboxW = x1 - x0;
  const bboxH = y1 - y0;
  const pixel = reviewMount.displayHeight / bboxH;
  const bob = moving && !reduced ? Math.sin((((time % 1) + 1) % 1) * Math.PI * 2) * 1.5 : 0;
  const mirror = reviewMount.sourceFaces === 'left' ? -facing : facing;
  const root = element('g', {
    transform: `translate(${x} ${y}) scale(${mirror} 1)`,
    'data-mount': 'horse',
    'data-mount-file': reviewMount.file,
    'data-mount-status': reviewMount.status,
    'data-gait': reviewMount.gait,
    'data-hoof-articulation': reviewMount.hoofArticulation,
    'data-moving': moving && !reduced ? 'bob-only' : 'still',
    'pointer-events': 'none',
  });
  root.append(element('image', {
    href: reviewMount.file,
    x: -(x0 + bboxW / 2) * pixel,
    y: -y1 * pixel + bob,
    width: reviewMount.width * pixel,
    height: reviewMount.height * pixel,
  }));
  const [sx, sy] = reviewMount.saddle;
  world.append(root);
  return {
    root,
    saddle: {
      x: x + mirror * ((sx - (x0 + bboxW / 2)) * pixel),
      y: y + ((sy - y1) * pixel) + bob,
    },
  };
}

export function drawMount(world, element, { x, y, scale = 0.28, facing = 1, time = 0, reduced = false, moving = false, riderClass = null, worn = null } = {}) {
  const mount = atlas.mounts.horse;
  // The horse crop still includes its floor plane. It is not a world sprite.
  if (!mount?.bodyFile || !mount.legs?.length) return null;
  const gait = mountGait(moving && !reduced ? time : 0, reduced || !moving);
  const [bx, by, bw, bh] = mount.body;
  const root = element('g', { transform: `translate(${x} ${y}) scale(${facing * scale} ${scale})`, 'data-mount': 'horse', 'data-gait': 'legged', 'data-moving': moving ? '1' : '0', 'pointer-events': 'none' });
  root.append(element('ellipse', { cx: bw * 0.45, cy: 8, rx: bw * 0.32, ry: 18, fill: '#00000066' }));
  const body = sheetCrop(element, mount.bodyFile, mount.body, [0, 1]);
  root.append(body.node);
  mount.legs.forEach((leg, index) => {
    const [lx, ly, lw] = leg;
    const angle = gait[index] || 0;
    const group = element('g', {
      transform: `translate(${lx - bx + lw / 2} ${ly - by - bh}) rotate(${angle})`,
      'data-hoof': angle < 0 ? 'lifted' : 'planted',
      'data-joint': `hoof-${index}`,
    });
    group.append(sheetCrop(element, mount.file, leg, [0.5, 0]).node);
    root.append(group);
  });
  if (riderClass) {
    const saddle = mount.saddle || [0.46, 0.58];
    drawActor(root, element, riderClass, {
      x: bw * saddle[0], y: -bh * saddle[1], scale: mount.riderScale || 0.22, facing: 1,
      clip: moving && !reduced ? 'mountWalk' : 'idle', time, reduced: reduced || !moving,
      worn,
    });
  }
  const centred = element('g', { transform: `translate(${-bw / 2} 0)` });
  centred.append(...root.childNodes);
  root.append(centred);
  world.append(root);
  return root;
}

export function plateOffset(time, { fly = false, clip = 'idle', reduced = false } = {}) {
  if (reduced) return { y: 0, rot: 0 };
  const u = ((time % 1) + 1) % 1;
  const wave = Math.sin(u * Math.PI * 2);
  const arc = Math.sin(u * Math.PI);
  if (clip === 'cast') return { y: (fly ? -10 : 0) - arc * 6, rot: -arc * 6 };
  if (clip === 'buff') return { y: (fly ? -10 : 0) - arc * 4, rot: 0 };
  if (clip === 'heal') return { y: (fly ? -10 : 0) - arc * 5, rot: 0 };
  if (clip === 'debuff') return { y: (fly ? -6 : 0) + arc * 3, rot: 0 };
  if (fly) return { y: -10 + wave * -8, rot: wave * 6 };
  if (clip === 'walk' || clip === 'attack') return { y: Math.abs(wave) * -5, rot: clip === 'attack' ? -12 + u * 24 : wave * 3 };
  if (clip === 'hit') return { y: 2, rot: 14 };
  if (clip === 'death') return { y: 8, rot: 70 };
  return { y: 0, rot: 0 };
}

export function staticMountForAge(age) {
  return Object.values(staticMounts.mounts).find(mount => age >= mount.minAge && age <= mount.maxAge) || null;
}

export function drawStaticMount(world, element, mount, x, y, { facing = 1, time = 0, reduced = false, moving = false, riderClass = null, worn = null } = {}) {
  if (!mount?.file || mount.displayHeight > 64 || mount.gait !== 'single-pose') return null;
  const [x0, y0, x1, y1] = mount.tightBBox;
  const bboxH = y1 - y0;
  const rawPixel = mount.displayHeight / bboxH;
  const drawn = visibleBox({
    width: mount.width * rawPixel,
    height: mount.height * rawPixel,
    maxVisibleCssPx: 64,
    staticMaxHeight: mount.displayHeight,
  }, mount.height * rawPixel, worldCssPerUnit);
  const pixel = drawn.height / mount.height;
  const bob = moving && !reduced ? Math.sin((((time % 1) + 1) % 1) * Math.PI * 2) * 1.5 : 0;
  const root = element('g', {
    transform: `translate(${x} ${y}) scale(${facing} 1)`,
    'data-mount': mount.id,
    'data-mount-file': mount.file,
    'data-mount-status': mount.matte,
    'data-gait': mount.gait,
    'data-hoof-articulation': mount.hoofArticulation,
    'data-rider': mount.rider,
    'data-display-height': String(mount.displayHeight),
    'data-moving': moving && !reduced ? 'bob-only' : 'still',
    'pointer-events': 'none',
  });
  root.append(element('image', {
    href: mount.file,
    x: -(x0 + (x1 - x0) / 2) * pixel,
    y: -y1 * pixel + bob,
    width: mount.width * pixel,
    height: mount.height * pixel,
  }));
  if (riderClass) {
    const seatY = -y1 * pixel + bob + drawn.height * 0.22;
    const seatX = 0;
    const driver = drawActor(root, element, riderClass, {
      x: seatX, y: seatY, scale: 0.12, facing: 1,
      clip: moving && !reduced ? 'mountWalk' : 'idle', time, reduced: reduced || !moving,
      worn,
    });
    if (driver) {
      driver.setAttribute('data-vehicle-driver', riderClass);
    }
  }
  world.append(root);
  return root;
}

export function drawPlate(world, element, plate, x, y, height, { opacity = 1, time = 0, fly = false, clip = 'idle', reduced = false } = {}) {
  if (!plate?.file) return false;
  const fitted = visibleBox({
    ...plate,
    defaultVisibleCssPx: plate.maxVisibleCssPx || plate.staticMaxHeight ? undefined : 130,
  }, height, worldCssPerUnit);
  const drawnHeight = fitted.height;
  const width = fitted.width;
  const single = plate.pose === 'single';
  const motion = single && clip === 'idle'
    ? { y: 0, rot: 0 }
    : plateOffset(time, { fly, clip, reduced });
  const group = element('g', {
    transform: `translate(${x} ${y + motion.y}) rotate(${motion.rot})`,
    'data-plate-motion': clip,
    'data-articulation': single ? 'single-pose' : 'plate',
    'data-plate-height': String(drawnHeight),
    'data-plate-css-height': String(fitted.cssHeight),
    'data-plate-css-cap': fitted.capCss == null ? '' : String(fitted.capCss),
    'data-plate-provisional': plate.provisional ? '1' : '0',
    'data-semantic-limit': plate.semanticLimit || '',
  });
  group.append(element('ellipse', { cx: 0, cy: 2, rx: Math.max(8, width * 0.28), ry: 5, fill: '#00000066', opacity }));
  group.append(actorImage(element, { href: plate.file, x: -width / 2, y: -drawnHeight, width, height: drawnHeight, opacity, 'data-plate': plate.file }));
  world.append(group);
  return true;
}

export function creaturePlate(type) { return plateView('creatures', type, plates.creatures[type] || null); }
export function troopPlate(age, role) { return plateView('troops', `${age}-${role}`, plates.troops[`${age}-${role}`] || null); }
export function attackerPlate(age, role) { return plateView('attackers', `${age}-${role}`, plates.attackers[`${age}-${role}`] || null); }
export function towerPlate(age, family) { return plateView('towers', `${age}-${family}`, plates.towers[`${age}-${family}`] || null); }
export function projectilePlate(family) { return plateView('projectiles', family, plates.projectiles[family] || null); }
export function plateForStack(stack) {
  if (!stack) return null;
  if (stack.kind === 'creature') return creaturePlate(stack.type);
  if (stack.kind === 'role') return troopPlate(stack.age ?? 0, stack.type);
  return null;
}
export { atlas, plates };
