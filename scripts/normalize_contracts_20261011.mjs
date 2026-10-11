// Align the standing-body contract and the live interface vocabulary.
// Does not rewrite plate bytes. Historical receipt paths stay on each row.
import fs from 'node:fs';
import crypto from 'node:crypto';

const bodyPath = 'src/data/hero-bodies-20261011.json';
const interfacePath = 'docs/plan/IMAGE-COMPLETE-INTERFACE-2026-10-11.json';
const bodies = JSON.parse(fs.readFileSync(bodyPath, 'utf8'));

for (const body of Object.values(bodies.bodies)) {
  const roi = body.cropROI;
  if (!body.cropROIConvention && Array.isArray(roi) && roi.length === 4) {
    const [x0, y0, width, height] = roi;
    body.cropROI = [x0, y0, x0 + width, y0 + height];
    body.cropROIConvention = 'half-open-xyxy';
  }
  body.frames = {
    source: 'NATIVE',
    intermediate: 'SOURCE_BODY',
    part: 'STANDING',
    canvas: 'OUTPUT',
    trim: 'half-open-xyxy',
  };
  body.articulation = 'NOT_APPLICABLE';
  body.status = 'PARTIAL';
  body.staticApplicability = 'HERO_ROOM_STANDING';
  body.displayCap = {
    cssPx: 600,
    basis: 'HEIGHT',
    purpose: 'HERO_ROOM_STANDING full figure. Ordinary plates stay 130. Gear, mounts and effects stay 64. This cap is not a Forge or world-actor permission.',
  };
  if (body.notRig) body.rigEligibility = 'NOT_APPLICABLE';
}
bodies.vocabulary = {
  status: ['READY', 'PARTIAL', 'FAIL', 'BLOCKED', 'NO_NEW_IMAGE_NEEDED'],
  gates: ['PASS', 'PARTIAL', 'FAIL', 'NOT_APPLICABLE', 'UNVERIFIED'],
  intendedUse: ['SPRITE', 'HERO_ROOM_STANDING', 'CODE_NATIVE'],
};
bodies.displayCaps = {
  ordinaryStaticCssPx: 130,
  gearMountEffectCssPx: 64,
  heroRoomStandingCssPx: 600,
};
bodies.maxVisibleCssPx = 600;
bodies.note += ' Contract revision 2026-10-11: cropROI is half-open XYXY; status is PARTIAL because kit era and rigs are incomplete; the 600 CSS cap is the Hero-room figure only.';
fs.writeFileSync(bodyPath, JSON.stringify(bodies, null, 2) + '\n');

const face = JSON.parse(fs.readFileSync(interfacePath, 'utf8'));
face.schema = 6;
face.vocabulary = bodies.vocabulary;
face.displayCaps = bodies.displayCaps;
const standing = new Set(Object.values(bodies.bodies).map(body => body.id));
for (const row of face.rows) {
  if (!standing.has(row.id)) continue;
  const body = Object.values(bodies.bodies).find(item => item.id === row.id);
  row.status = 'PARTIAL';
  row.intendedUse = 'HERO_ROOM_STANDING';
  row.maxDisplayCssPx = 600;
  row.limitBasis = 'HEIGHT';
  row.cropROI = body.cropROI;
  row.cropROIConvention = 'half-open-xyxy';
  row.gates = {
    ...(row.gates || {}),
    articulation: 'NOT_APPLICABLE',
    runtime: 'PARTIAL',
    semantics: body.depictedKitEra ? 'PARTIAL' : 'UNVERIFIED',
  };
  row.consumer = {
    file: bodyPath,
    screen: 'hero',
    maxVisibleCssPx: 600,
    purpose: 'HERO_ROOM_STANDING',
  };
  row.limitations = [...new Set([...(row.limitations || []), 'Static Hero-room use only. Articulation is NOT_APPLICABLE. The 600 CSS cap is this purpose, not the 130 plate cap.'])];
}
face.readySubset = (face.readySubset || []).filter(id => {
  if (standing.has(id)) return false;
  const row = face.rows.find(item => item.id === id);
  return row?.status === 'READY';
});
face.imageWorkComplete = false;
face.localProcessingComplete = false;
face.contractRevision = '2026-10-11-repair';
const sha = crypto.createHash('sha256').update(fs.readFileSync(bodyPath)).digest('hex');
face.localRepairs20261011.standingBodies.contractSHA256 = sha;
face.localRepairs20261011.standingBodies.status = 'PARTIAL';
face.localRepairs20261011.standingBodies.ready = [];
fs.writeFileSync(interfacePath, JSON.stringify(face, null, 2) + '\n');
const readyRows = face.rows.filter(row => (face.readySubset || []).includes(row.id));
const bad = readyRows.filter(row => row.status !== 'READY').map(row => row.id);
console.log(JSON.stringify({ bodies: Object.keys(bodies.bodies).length, readySubset: face.readySubset.length, badReady: bad, contractSHA256: sha }));
