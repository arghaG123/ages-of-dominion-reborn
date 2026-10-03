// Local articulated rig. Clips move joints. They do not bob a single sprite.
export const GROUND = 120;

const limb = (hip, angle, length) => [hip[0] + Math.sin(angle) * length, hip[1] + Math.cos(angle) * length];

function legs(phase, lift) {
  const hip = [0, 78];
  const swing = Math.sin(phase * Math.PI * 2) * lift;
  const kneeL = limb(hip, -0.3 + swing, 22);
  const kneeR = limb(hip, 0.3 - swing, 22);
  const hoofL = limb(kneeL, -0.1 + swing * 0.4, 20);
  const hoofR = limb(kneeR, 0.1 - swing * 0.4, 20);
  hoofL[1] = GROUND;
  hoofR[1] = GROUND;
  if (lift > 0) {
    const raised = Math.max(0, Math.sin(phase * Math.PI * 2));
    hoofL[1] = GROUND - raised * lift;
    hoofR[1] = GROUND - Math.max(0, -Math.sin(phase * Math.PI * 2)) * lift;
  }
  return { hip, kneeL, kneeR, hoofL, hoofR };
}

function mountLegs(phase, moving) {
  // Four-beat walk. Each hoof lifts on its own beat and plants on the ground line.
  const plants = [0, 0.25, 0.5, 0.75];
  const names = ['hoofFL', 'hoofFR', 'hoofHL', 'hoofHR'];
  const hips = [[-14, 74], [14, 74], [-16, 86], [16, 86]];
  const hooves = {};
  hips.forEach((hip, i) => {
    const local = (phase - plants[i] + 1) % 1;
    const lifted = moving && local > 0.12 && local < 0.4;
    hooves[names[i]] = [hip[0] + (lifted ? Math.sin(local * Math.PI * 2) * 8 : 0), lifted ? GROUND - 10 : GROUND];
  });
  return { body: [0, 70], ...hooves };
}

export function pose(clip, t, { reduced = false } = {}) {
  const u = reduced ? 0 : ((t % 1) + 1) % 1;
  const root = [80, reduced ? 0 : clip === 'walk' || clip === 'mountWalk' ? 0 : Math.sin(u * Math.PI * 2) * 0.4];
  let spine = -0.05;
  let arm = 0.4;
  const human = legs(clip === 'walk' && !reduced ? u : 0, clip === 'walk' && !reduced ? 16 : 0);
  if (clip === 'work') arm = -1.2 + Math.sin(u * Math.PI * 2) * 0.8;
  if (clip === 'attack') arm = -2.2 + u * 2.4;
  if (clip === 'hit') { spine = 0.45; arm = 1.2; }
  if (clip === 'death') { spine = 1.35; arm = 1.6; root[1] = 16; }
  if (clip === 'idle') arm = 0.35 + Math.sin(u * Math.PI * 2) * 0.05;
  const mount = clip === 'mountWalk' ? mountLegs(u, !reduced) : null;
  const chest = [root[0], 52 + root[1]];
  const head = [chest[0] + Math.sin(spine) * 16, chest[1] - Math.cos(spine) * 16];
  const hand = limb(chest, arm, 24);
  return { clip, t: u, ground: GROUND, root, spine, chest, head, hand, ...human, mount };
}

export function hoofContact(sample) {
  const hooves = sample.mount
    ? [sample.mount.hoofFL, sample.mount.hoofFR, sample.mount.hoofHL, sample.mount.hoofHR]
    : [sample.hoofL, sample.hoofR];
  return hooves.filter(([, y]) => Math.abs(y - GROUND) < 1e-6).length;
}
