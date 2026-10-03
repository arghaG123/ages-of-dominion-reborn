import test from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';

const root = new URL('../', import.meta.url);
const read = name => JSON.parse(readFileSync(new URL(name, root), 'utf8'));
const sha = name => createHash('sha256').update(readFileSync(new URL(name, root))).digest('hex');
const candidate = read('qa/recovery-executor-20261003/kingdom-layout-candidate-v2.json');
const scene = read('src/data/stone-scene.json');

test('v2 stays beside the live contract and the uniform frame', () => {
  assert.equal(sha('docs/plan/IMPLEMENTATION-CONTRACT.json'), '43553411b583a6df5fdcf620d2b3efecd82a0cd6f783895165a5910e577b0fcd');
  assert.equal(candidate.activeContractSHA256, '43553411b583a6df5fdcf620d2b3efecd82a0cd6f783895165a5910e577b0fcd');
  assert.equal(candidate.activeContractEdited, false);
  assert.equal(candidate.activeSceneEdited, false);
  assert.equal(scene.hall.matrix[0][0], 0.1312);
  assert.equal(candidate.liveHallScale, 0.1312);
  assert.equal(candidate.hall.matrix[0][0], 0.34);
  assert.equal(candidate.hall.matrix[1][1], 0.34);
  assert.equal(candidate.hall.spriteSourceRect[1], 40);
  assert.equal(candidate.hall.spriteSourceRect[3], 372.52);
  assert.equal(candidate.status, 'READY_FOR_REVIEW');
  assert.equal(candidate.ownerAcceptance, 'NOT_OWNER_ACCEPTED');
  assert.equal(candidate.id, 'kingdom-layout-candidate-v2');
});

test('the townhall pad follows the visible foot and the cobble stays an approach', () => {
  assert.equal(candidate.contact.builtAroundCobble, false);
  assert.equal(candidate.contact.method, 'visible-stone-foot');
  assert.equal(candidate.contact.aabbUsedAsSite, true);
  assert.ok(candidate.contact.sourceSamples.length >= 40);
  assert.ok(candidate.contact.plinthDistanceToContactPx > 4);
  assert.ok(candidate.contact.tolerancePx >= candidate.contact.plinthDistanceToContactPx);
  assert.ok(candidate.contact.tolerancePx >= 20);
  assert.ok(candidate.contact.cobbleDistanceToContactPx > candidate.contact.plinthDistanceToContactPx);
  assert.match(candidate.contact.cobbleRole, /approach/);
  assert.match(candidate.contact.hidden, /rear/i);
  assert.equal(candidate.contact.matteRepair.startsWith('none'), true);
  const hall = candidate.geometry.sites.find(site => site.id === 'townhall');
  assert.deepEqual(hall.rect, candidate.contact.aabb);
});

test('review chrome, mature doors and the collected painting stay honest', () => {
  assert.equal(candidate.viewport.reviewChromePx, 92);
  assert.equal(candidate.viewport.runtimeChromeBudgetPx, 112);
  assert.equal(candidate.viewport.identical, false);
  const stages = candidate.viewport.review.map(item => item.stageHeight);
  assert.deepEqual(stages, [283, 332, 728, 628]);
  const tablet = candidate.viewport.review.find(item => item.viewport[0] === 1180);
  assert.equal(tablet.occludedSites.some(item => item.id === 'P11' && item.footprintCrossesPanel && item.centreClear), true);
  assert.ok(candidate.mature.blocking > 0);
  assert.ok(candidate.mature.acceptable > 0);
  assert.equal(candidate.mature.structures.length, 17);
  assert.ok(candidate.mature.structures.every(item => item.door && item.body && item.depth === item.door[1]));
  assert.match(candidate.mature.note, /not treated as proof/);
  assert.equal(candidate.painting.sha256, '5dfdc20e8724acf48781ceae15d00a35899c855a26408a8e7656f84165f23c76');
  assert.equal(sha(candidate.painting.file), candidate.painting.sha256);
  assert.deepEqual(candidate.painting.size, [1376, 768]);
  assert.equal(candidate.painting.spatialFidelity, 'FAIL');
  assert.equal(candidate.painting.ownerAcceptance, 'NOT_OWNER_ACCEPTED');
  assert.equal(candidate.painting.usableSiteCount, 'UNVERIFIED');
  assert.equal(candidate.painting.guidesMatch, false);
  assert.equal(candidate.guide.ownerAcceptance, 'NOT_OWNER_ACCEPTED');
  assert.equal(sha(candidate.guide.file), candidate.guide.sha256);
  assert.equal(candidate.deliveryPlan.repurchase, 'not requested');
});
