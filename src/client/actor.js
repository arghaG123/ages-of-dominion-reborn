// Measured part assembly. Joints rotate. The whole sheet is never shown as the actor.
import atlas from '../data/actor-atlas.json' with { type: 'json' };
import reviewMount from '../data/mount-review-v1.json' with { type: 'json' };
import staticMounts from '../data/static-mounts-v1.json' with { type: 'json' };
import plates from '../data/plate-catalog.json' with { type: 'json' };
import { hoofContact, pose } from './rig.js';

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

let clipSerial = 0;
function sheetCrop(element, href, box, pivot) {
  const [bx, by, bw, bh] = box;
  const [px, py] = pivot;
  const id = `part-clip-${clipSerial++}`;
  const clip = element('clipPath', { id, clipPathUnits: 'userSpaceOnUse' });
  clip.append(element('rect', { x: 0, y: 0, width: bw, height: bh }));
  const group = element('g', { transform: `translate(${-bw * px} ${-bh * py})` });
  group.append(clip);
  group.append(element('image', { href, x: -bx, y: -by, width: 1024, height: 1024, 'clip-path': `url(#${id})` }));
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
    });
    group.append(part.node);
    group.__len = part.length;
    host.append(group);
    host = group;
    first = false;
  });
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

export function drawActor(world, element, classId, { x, y, scale = 0.2, facing = 1, clip = 'idle', time = 0, reduced = false } = {}) {
  const spec = atlas.classes[classId] || atlas.classes.knight;
  // Sheet crops still mix background, labels, and grouped parts. Do not place them in the world.
  if (!atlas.worldReady || !spec?.parts?.torso) return null;
  const pose = clipAngles(clip, time, reduced);
  const marks = landmarks(spec);
  const root = element('g', {
    transform: `translate(${x} ${y}) scale(${facing * scale} ${scale})`,
    'data-actor': classId,
    'data-clip': clip,
    'data-spine': String(pose.spine),
    'data-arm': String(pose.arm),
  });
  root.append(element('ellipse', { cx: 0, cy: 6, rx: 70, ry: 16, fill: '#00000066' }));
  const body = element('g', { transform: `rotate(${pose.spine})`, 'data-joint': 'spine' });
  const torso = spec.parts.torso;
  chain(element, body, spec, spec.file, ['thigh', 'shin', 'foot'], [pose.thighL, pose.shinL, 0], marks.farHip[0], marks.farHip[1]);
  const trunk = partNode(element, spec, 'torso', spec.file);
  if (trunk) {
    const placed = element('g', { 'data-joint': 'torso' });
    placed.append(trunk.node);
    body.append(placed);
    const head = partNode(element, spec, 'head', spec.file);
    if (head) {
      const neck = element('g', { transform: `translate(${marks.neck[0]} ${marks.neck[1]}) rotate(${pose.head})`, 'data-joint': 'neck' });
      neck.append(head.node);
      placed.append(neck);
    }
  }
  chain(element, body, spec, spec.file, ['thigh', 'shin', 'foot'], [pose.thighR, pose.shinR, 0], marks.nearHip[0], marks.nearHip[1]);
  const armHost = body.querySelector?.('[data-joint="torso"]') || body;
  const armParts = ['arm', 'forearm', 'weapon'].filter(name => spec.parts[name]);
  const armAngles = { arm: pose.arm, forearm: pose.forearm, weapon: pose.weapon };
  chain(element, armHost, spec, spec.file, armParts, armParts.map(name => armAngles[name]), marks.shoulder[0], marks.shoulder[1]);
  root.append(body);
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

export function drawMount(world, element, { x, y, scale = 0.28, facing = 1, time = 0, reduced = false, moving = false, riderClass = null } = {}) {
  const mount = atlas.mounts.horse;
  // The horse crop still includes its floor plane. It is not a world sprite.
  if (!atlas.mountReady || !mount?.bodyFile || !mount.legs?.length) return null;
  const gait = mountGait(moving && !reduced ? time : 0, reduced || !moving);
  const [bx, by, bw, bh] = mount.body;
  const root = element('g', { transform: `translate(${x} ${y}) scale(${facing * scale} ${scale})`, 'data-mount': 'horse', 'data-moving': moving ? '1' : '0' });
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
      x: bw * saddle[0], y: -bh * saddle[1], scale: 0.22, facing: 1,
      clip: moving && !reduced ? 'mountWalk' : 'idle', time, reduced: reduced || !moving,
    });
  }
  world.append(root);
  return root;
}

export function plateOffset(time, { fly = false, clip = 'idle', reduced = false } = {}) {
  if (reduced) return { y: 0, rot: 0 };
  const u = ((time % 1) + 1) % 1;
  const wave = Math.sin(u * Math.PI * 2);
  if (fly) return { y: -10 + wave * -8, rot: wave * 6 };
  if (clip === 'walk' || clip === 'attack') return { y: Math.abs(wave) * -5, rot: clip === 'attack' ? -12 + u * 24 : wave * 3 };
  if (clip === 'hit') return { y: 2, rot: 14 };
  if (clip === 'death') return { y: 8, rot: 70 };
  return { y: wave * 1.2, rot: 0 };
}

export function staticMountForAge(age) {
  return Object.values(staticMounts.mounts).find(mount => age >= mount.minAge && age <= mount.maxAge) || null;
}

export function drawStaticMount(world, element, mount, x, y, { facing = 1, time = 0, reduced = false, moving = false } = {}) {
  if (!mount?.file || mount.displayHeight > 64 || mount.gait !== 'single-pose') return null;
  const [x0, y0, x1, y1] = mount.tightBBox;
  const bboxH = y1 - y0;
  const pixel = mount.displayHeight / bboxH;
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
  });
  root.append(element('image', {
    href: mount.file,
    x: -(x0 + (x1 - x0) / 2) * pixel,
    y: -y1 * pixel + bob,
    width: mount.width * pixel,
    height: mount.height * pixel,
  }));
  world.append(root);
  return root;
}

export function drawPlate(world, element, plate, x, y, height, { opacity = 1, time = 0, fly = false, clip = 'idle', reduced = false } = {}) {
  if (!plate?.file) return false;
  const drawnHeight = plate.staticMaxHeight ? Math.min(height, plate.staticMaxHeight) : height;
  const width = drawnHeight * ((plate.width || drawnHeight) / (plate.height || drawnHeight));
  const single = plate.pose === 'single';
  const motion = single
    ? { y: reduced ? 0 : Math.sin((((time % 1) + 1) % 1) * Math.PI * 2) * 1.5, rot: 0 }
    : plateOffset(time, { fly, clip, reduced });
  const group = element('g', {
    transform: `translate(${x} ${y + motion.y}) rotate(${motion.rot})`,
    'data-plate-motion': clip,
    'data-articulation': single ? 'single-pose' : 'plate',
    'data-plate-height': String(drawnHeight),
    'data-plate-provisional': plate.provisional ? '1' : '0',
  });
  group.append(element('ellipse', { cx: 0, cy: 2, rx: Math.max(8, width * 0.28), ry: 5, fill: '#00000066', opacity }));
  group.append(element('image', { href: plate.file, x: -width / 2, y: -drawnHeight, width, height: drawnHeight, opacity, 'data-plate': plate.file }));
  world.append(group);
  return true;
}

export function creaturePlate(type) { return plates.creatures[type] || null; }
export function troopPlate(age, role) { return plates.troops[`${age}-${role}`] || null; }
export function attackerPlate(age, role) { return plates.attackers[`${age}-${role}`] || null; }
export function towerPlate(age, family) { return plates.towers[`${age}-${family}`] || null; }
export function projectilePlate(family) { return plates.projectiles[family] || null; }
export function plateForStack(stack) {
  if (!stack) return null;
  if (stack.kind === 'creature') return creaturePlate(stack.type);
  if (stack.kind === 'role') return troopPlate(stack.age ?? 0, stack.type);
  return null;
}
export { atlas, plates };
