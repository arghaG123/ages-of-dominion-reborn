import assert from 'node:assert/strict';
import test from 'node:test';
import { adaptProducerRow, asAffine, asVec2, asWH, applyAffine } from '../src/client/consumer-adapter.js';
import { retreatFocusTarget } from '../src/client/tactical-ui.js';
import { visibleBox } from '../src/client/visible-size.js';

test('dimension and contact normalizers reject malformed values and accept both shapes', () => {
  assert.deepEqual(asWH([12, 8]), { width: 12, height: 8 });
  assert.deepEqual(asWH({ width: 3, height: 4 }), { width: 3, height: 4 });
  assert.equal(asWH([0, 4]), null);
  assert.equal(asWH([1.5, 4]), null);
  assert.deepEqual(asVec2({ x: 2, y: 9 }), [2, 9]);
  assert.equal(asVec2({ x: '2', y: 9 }), null);
  assert.equal(asAffine([1, 0, 0, 1, 0]), null);
  assert.deepEqual(applyAffine([1, 0, 0, 1, -4, -7], [4, 9]), [0, 2]);
});

test('a missing transform is not replaced with an identity matrix', () => {
  const asset = adaptProducerRow({
    id: 'building-example',
    role: 'building-farm',
    status: 'READY',
    source: { path: 'assets/a.png', sha256: 'abc', roi: [0, 0, 10, 10] },
    output: { path: 'assets/b.png', sha256: 'def', dimensions: { width: 10, height: 10 } },
    groundContact: [[12, 3]],
    sourceToOutput: null,
    frame: 'ORIGIN_TOP_LEFT_NATIVE',
  }, { producer: 'ENVIRONMENT', hashOk: true });
  assert.equal(asset.sourceToOutput, null);
  assert.equal(asset.groundContact, null);
  assert.equal(asset.gates.spatial, 'BLOCKED');
  assert.equal(asset.gates.runtime, 'BLOCKED');
});

test('outline derivatives and support screens are not promoted', () => {
  const troop = adaptProducerRow({
    id: 'troop-stone-melee',
    role: 'static-troop',
    status: 'READY',
    source: { path: 'native.png', sha256: 'a' },
    output: { path: 'broken.png', sha256: 'b', dimensions: [100, 100] },
    sourceToOutput: [1, 0, 0, 1, 0, 0],
    gates: { matte: 'PASS', spatial: 'PASS' },
  }, { producer: 'ACTORS', hashOk: true });
  assert.equal(troop.gates.matte, 'FAIL');
  assert.equal(troop.gates.runtime, 'BLOCKED');
  assert.notEqual(troop.outputPath, null);

  const support = adaptProducerRow({
    id: 'support-env-home',
    role: 'support-screen',
    status: 'READY',
    output: { path: 'mock.jpg', sha256: 'c', dimensions: { width: 1280, height: 720 } },
  }, { producer: 'ENVIRONMENT', support: true, hashOk: true });
  assert.equal(support.use, 'REFERENCE_ONLY');
  assert.equal(support.gates.runtime, 'BLOCKED');
});

test('a no-output joint row is metadata and a failed link stays failed', () => {
  const joint = adaptProducerRow({
    id: 'healer-head-to-torso',
    role: 'joint-link',
    status: 'FAIL',
    source: { path: '', sha256: '' },
    output: null,
  }, { producer: 'ACTORS' });
  assert.equal(joint.outputPath, null);
  assert.equal(joint.use, 'JOINT_METADATA');
  assert.equal(joint.gates.articulation, 'FAIL');
  assert.equal(joint.gates.runtime, 'BLOCKED');
});

test('source contacts outside the crop are mapped by the recorded affine', () => {
  const asset = adaptProducerRow({
    id: 'farm-example',
    role: 'building-farm',
    status: 'READY',
    age: 0,
    source: { path: 's.png', sha256: 'abc', roi: [0, 20, 40, 60] },
    output: { path: 'o.png', sha256: 'def', dimensions: { width: 40, height: 40 } },
    sourceToOutput: [1, 0, 0, 1, 0, -20],
    frame: 'ORIGIN_TOP_LEFT_NATIVE',
    groundContact: [[10, 50]],
    footprint: [[0, 40], [39, 40], [39, 59], [0, 59]],
    entrance: [10, 58],
    heightEnvelope: [0, 20, 40, 59],
    gates: { spatial: 'PASS', matte: 'PASS' },
  }, { producer: 'ENVIRONMENT', hashOk: true });
  assert.equal(asset.coordinateFrame, 'OUTPUT_CROP');
  assert.deepEqual(asset.groundContact, [[10, 30]]);
  assert.equal(asset.gates.spatial, 'PARTIAL');
  assert.notEqual(asset.gates.runtime, 'PASS');
});

test('retreat focus returns to the trigger after cancel and stays in the dialog while open', () => {
  assert.equal(retreatFocusTarget({ open: true, restoreTrigger: false, activeChoice: 'retreat' }), 'retreat-cancel');
  assert.equal(retreatFocusTarget({ open: false, restoreTrigger: true, activeChoice: 'retreat-cancel' }), 'retreat');
  assert.equal(retreatFocusTarget({ open: false, restoreTrigger: false, activeChoice: 'move' }), 'move');
  assert.equal(retreatFocusTarget({ open: false, restoreTrigger: false, activeChoice: 'retreat-confirm' }), '');
});

test('visible size uses the lower of the CSS cap and the world cap on both sides', () => {
  const tight = visibleBox({ width: 100, height: 200, maxVisibleCssPx: 64, staticMaxHeight: 130 }, 200, 0.5);
  assert.ok(Math.max(tight.cssWidth, tight.cssHeight) <= 64.001);
  assert.ok(tight.cssWidth <= 64.001 && tight.cssHeight <= 64.001);
  const world = visibleBox({ width: 100, height: 100, staticMaxHeight: 130 }, 200, 2);
  assert.ok(Math.max(world.cssWidth, world.cssHeight) <= 130.001);
  assert.ok(world.height <= 130);
});
