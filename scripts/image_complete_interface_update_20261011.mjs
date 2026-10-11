// Records the 11 October local Image repairs in the successor interface without touching rows'
// original receipts: static standing-body contract, despilled live plates, projectile frame crops,
// adopted Slinger. imageWorkComplete stays false (scenes FAIL, rigs absent, Healer body missing).
import fs from 'node:fs';
import crypto from 'node:crypto';

const interfacePath = 'docs/plan/IMAGE-COMPLETE-INTERFACE-2026-10-11.json';
const face = JSON.parse(fs.readFileSync(interfacePath, 'utf8'));
const bodies = JSON.parse(fs.readFileSync('src/data/hero-bodies-20261011.json', 'utf8'));
const despill = JSON.parse(fs.readFileSync('qa/image-complete-20261011/plate-despill.json', 'utf8'));
const sha = file => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');

for (const row of face.rows) {
  const classId = /^class-([a-z]+)-standing-body$/.exec(row.id)?.[1];
  const body = classId && bodies.bodies[classId];
  if (!body) continue;
  row.output = { path: body.file, sha256: body.sha256, bytes: body.bytes, dimensions: { width: body.width, height: body.height } };
  row.sourceToOutput = body.sourceToOutput;
  row.groundContact = body.groundContact;
  row.status = 'READY_STATIC_STANDING';
  row.gates = { ...(row.gates || {}), matte: 'PASS', spatial: 'PARTIAL', articulation: 'NOT_A_RIG', runtime: 'PASS_HERO_ROOM', owner: 'UNVERIFIED' };
  row.limitations = [...new Set([...(row.limitations || []), 'Static standing body for the Hero room only; not a rig, not an atlas.'])];
  row.consumer = { file: 'src/data/hero-bodies-20261011.json', screen: 'hero', maxVisibleCssPx: body.maxVisibleCssPx };
}

face.localRepairs20261011 = {
  standingBodies: { contract: 'src/data/hero-bodies-20261011.json', contractSHA256: sha('src/data/hero-bodies-20261011.json'), ready: Object.keys(bodies.bodies), missing: Object.keys(bodies.missing || {}), qa: 'qa/image-complete-20261011/body-matte-repair.json' },
  livePlateDespill: { qa: 'qa/image-complete-20261011/plate-despill.json', repaired: despill.summary.repaired, keptOriginal: despill.summary.kept, residualAbove1pct: despill.summary.residualAbove1pct, consumer: 'src/data/plate-overrides-20261007.json', consumerSHA256: sha('src/data/plate-overrides-20261007.json'), method: despill.method },
  projectileFrames: despill.rows.filter(r => r.action === 'DESPILL_FRAME').map(r => ({ id: r.id, file: r.file, roi: r.roi, sourceToOutput: [1, 0, 0, 1, -r.offset[0], -r.offset[1]] })),
  adoptedTroopPlates: [{ key: '0-ranged', file: 'assets/derivatives/image-vertex-repair-20261009/actors/troops/troop-stone-ranged.png', note: 'Reviewed Slinger replaces the provisional platform plate; 130 CSS cap.' }],
  originalsUntouched: true,
};
face.readySubset = [...new Set([...face.readySubset, ...Object.keys(bodies.bodies).map(id => `class-${id}-standing-body`)])];
face.imageWorkComplete = false;
face.localProcessingComplete = false;
face.openGates = {
  sceneSpatial: '32 of 32 scene rows FAIL spatial registration; terrain paint does not match frozen legal geometry (Kingdom [60,-10,25,35,170,165], Adventure 16x10, Tactical 7x10, Defense 9x15). Requires registered source-bound terrain edits; none produced locally on 11 October.',
  rigs: 'No articulated rigs or semantic atlases exist for the seven bodies; Hero room uses static standing bodies.',
  healerBody: 'Healer standing body never collected (missing).',
  residualMagenta: despill.summary.residualAbove1pct,
};
face.note += ' 11 October 2026 local pass: seven bodies cleaned into static standing contract; 90 live plates despilled and one frame cropped per projectile sheet; Slinger adopted. No paid generation was performed; reserve/budget records unchanged.';
fs.writeFileSync(interfacePath, JSON.stringify(face, null, 2) + '\n');
console.log(JSON.stringify({ rows: face.rows.length, readySubset: face.readySubset.length, repaired: despill.summary.repaired }));
