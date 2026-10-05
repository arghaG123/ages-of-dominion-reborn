// Painted partial ranger. Joints use corrected roles. Missing hands stay missing.
import binding from '../data/anatomy-binding-v1.json' with { type: 'json' };

export function anatomyBinding() {
  return binding;
}

export function paintedPose(clip, time, reduced = false) {
  const u = reduced ? 0 : ((time % 1) + 1) % 1;
  const swing = Math.sin(u * Math.PI * 2);
  const pose = { head: 0, thighL: 0, thighR: 0, shinL: 0, shinR: 0, bootL: 0, bootR: 0, bow: -8 };
  if (reduced) return pose;
  if (clip === 'walk') {
    pose.thighL = swing * 26;
    pose.thighR = -swing * 26;
    pose.shinL = Math.max(0, swing) * 18;
    pose.shinR = Math.max(0, -swing) * 18;
    pose.bow = -8 - swing * 6;
  } else if (clip === 'mountWalk') {
    pose.thighL = 34;
    pose.thighR = 30;
    pose.shinL = 34;
    pose.shinR = 32;
    pose.bow = -12;
  } else if (clip === 'attack') {
    pose.bow = -55 + u * 80;
    pose.thighL = 8;
    pose.head = -4;
  } else if (clip === 'work') {
    pose.bow = -36 + swing * 18;
    pose.thighL = 6;
  } else if (clip === 'hit') {
    pose.head = 14;
    pose.thighL = 10;
    pose.bow = 16;
  } else if (clip === 'death') {
    pose.head = 20;
    pose.thighL = 22;
    pose.thighR = 16;
    pose.shinL = 12;
    pose.bow = 28;
  }
  return pose;
}

function withinTested(pose) {
  const limits = binding.testedAngles;
  return Math.abs(pose.head) <= limits.head + 0.01
    && Math.abs(pose.thighL) <= limits.thigh + 0.01
    && Math.abs(pose.thighR) <= limits.thigh + 0.01
    && Math.abs(pose.shinL) <= limits.shin + 0.01
    && Math.abs(pose.shinR) <= limits.shin + 0.01
    && Math.abs(pose.bow) <= limits.bow + 0.01;
}

function sized(part) {
  return { width: part.width * part.scale, height: part.height * part.scale };
}

function appendPart(element, parent, part, angle) {
  const size = sized(part);
  const [px, py] = part.pivot;
  const group = element('g', { transform: `rotate(${angle})`, 'data-joint': part.role, 'data-part': part.id });
  const image = element('image', {
    href: part.file,
    x: -size.width * px,
    y: -size.height * py,
    width: size.width,
    height: size.height,
    'data-role': part.role,
  });
  group.append(image);
  parent.append(group);
  return { group, length: size.height * (1 - py) };
}

function drawLeg(element, parent, ids, origin, pose) {
  let host = parent;
  let x = origin[0];
  let y = origin[1];
  ids.forEach((id, index) => {
    const part = binding.parts[id];
    const angle = pose[id] || 0;
    const joint = element('g', {
      transform: index === 0 ? `translate(${x} ${y})` : `translate(0 ${Math.max(0, (host.__len || 0) - binding.socketOverlapPx)})`,
    });
    const placed = appendPart(element, joint, part, angle);
    joint.__len = placed.length;
    host.append(joint);
    host = joint;
  });
}

export function legDrop() {
  const drop = side => binding.legs[side].reduce((total, id, index) => {
    const part = binding.parts[id];
    const length = part.height * part.scale * (1 - part.pivot[1]);
    return total + length - (index ? binding.socketOverlapPx : 0);
  }, 0);
  return Math.max(drop('left'), drop('right'));
}

export function drawBoundActor(world, element, classId, { x = 0, y = 0, scale = 1, facing = 1, clip = 'idle', time = 0, reduced = false } = {}) {
  if (classId !== binding.classId || !binding.overlapPass) return null;
  const pose = paintedPose(clip, time, reduced);
  if (!withinTested(pose)) return null;
  const show = scale * binding.displayScale;
  const root = element('g', {
    transform: `translate(${x} ${y}) scale(${facing * show} ${show})`,
    'data-articulation': 'painted-partial',
    'data-actor': classId,
    'data-clip': clip,
    'data-named-parts': 'corrected',
    'data-missing': binding.missing.join(','),
    'data-mount-mark': 'none',
  });
  const torso = binding.parts.torso;
  const torsoSize = sized(torso);
  const hips = element('g', { transform: `translate(0 ${-legDrop()})`, 'data-joint': 'hips' });
  const left = [binding.hips.left[0] * torsoSize.width, binding.hips.left[1]];
  const right = [binding.hips.right[0] * torsoSize.width, binding.hips.right[1]];
  drawLeg(element, hips, binding.legs.left, left, pose);
  const quiver = binding.accessories.find(item => item.part === 'quiver');
  if (quiver) {
    const part = binding.parts[quiver.part];
    const joint = element('g', {
      transform: `translate(${(quiver.attach[0] - torso.pivot[0]) * torsoSize.width} ${(quiver.attach[1] - torso.pivot[1]) * torsoSize.height})`,
      'data-renamed-from': quiver.renamedFrom,
    });
    appendPart(element, joint, part, 0);
    hips.append(joint);
  }
  const trunk = element('g', { 'data-joint': 'torso' });
  appendPart(element, trunk, torso, 0);
  const headSpec = binding.head;
  const head = binding.parts[headSpec.part];
  const neck = element('g', {
    transform: `translate(${(headSpec.attach[0] - torso.pivot[0]) * torsoSize.width} ${(headSpec.attach[1] - torso.pivot[1]) * torsoSize.height})`,
  });
  appendPart(element, neck, head, pose.head);
  trunk.append(neck);
  const bowSpec = binding.accessories.find(item => item.part === 'bow');
  if (bowSpec) {
    const part = binding.parts.bow;
    const hand = element('g', {
      transform: `translate(${(bowSpec.attach[0] - torso.pivot[0]) * torsoSize.width} ${(bowSpec.attach[1] - torso.pivot[1]) * torsoSize.height})`,
      'data-missing': bowSpec.missing,
      'data-renamed-from': bowSpec.renamedFrom,
    });
    appendPart(element, hand, part, pose.bow);
    trunk.append(hand);
  }
  hips.append(trunk);
  drawLeg(element, hips, binding.legs.right, right, pose);
  root.append(hips);
  world.append(root);
  return root;
}
