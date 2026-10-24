import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
import heroBodies from '../src/data/hero-bodies-20261011.json' with { type: 'json' };
import { bodyMatchesKit, fitBody, heroBody, kitEra, selectGearIcon } from '../src/client/hero-room.js';

test('hero body contract: eight static standing bodies exist with pinned bytes', () => {
  const ids = Object.keys(heroBodies.bodies);
  assert.equal(ids.length, 8);
  assert.ok(heroBodies.bodies.healer, 'Healer standing body must be present');
  for (const [id, body] of Object.entries(heroBodies.bodies)) {
    assert.ok(fs.existsSync(body.file), `${id} body file missing: ${body.file}`);
    const sha = crypto.createHash('sha256').update(fs.readFileSync(body.file)).digest('hex');
    assert.equal(sha, body.sha256, `${id} body bytes changed`);
    assert.equal(body.articulation, 'NOT_APPLICABLE');
    assert.equal(body.cropROIConvention, 'half-open-xyxy');
    assert.ok(body.cropROI[2] > body.cropROI[0] && body.cropROI[3] > body.cropROI[1]);
    assert.equal(body.notRig, true);
    if (id === 'healer') {
      assert.equal(body.status, 'COMPLETE_BODY_CANDIDATE');
      assert.equal(body.assembly.method, 'complete-body-extraction');
      assert.ok(body.foot[1] > 0.98, 'feet sit on the bottom of the plate');
      assert.equal(body.matteRepair.staffExtendedBelowBoots, 0);
    } else {
      assert.equal(body.status, 'PARTIAL');
      assert.ok(body.foot[1] > 0.9 && body.foot[1] <= 1, `${id} foot anchor must sit at the matte bottom`);
    }
  }
});

test('fitBody rests the feet on the floor line and honours the 600 CSS cap', () => {
  const knight = heroBody('knight');
  const box = fitBody(knight, 688, 700, 560, 1);
  assert.ok(Math.abs(box.y + box.height * knight.foot[1] - 700) < 0.001, 'feet must land on footY');
  assert.ok(box.height <= 560 && box.height > 500);
  const capped = fitBody(knight, 688, 700, 560, 2);
  assert.ok(capped.cssHeight <= 600, `CSS height ${capped.cssHeight} exceeds the contract cap`);
  assert.equal(fitBody(null, 0, 0, 100, 1), null);
});

test('kitEra maps the eight ages onto the four MASTER-PLAN kit eras', () => {
  assert.deepEqual([0, 3, 4, 7].map(kitEra), ['ancient', 'medieval', 'powder', 'mech']);
  assert.equal(kitEra(99), 'ancient');
});

test('Paladin Ancient and Mech kit repairs resolve to complete transparent PNG sources', () => {
  for (const [age, era] of [[0, 'ancient'], [6, 'mech']]) {
    const body = heroBody('paladin', age);
    const bytes = fs.readFileSync(body.file);
    const sha = crypto.createHash('sha256').update(bytes).digest('hex');
    assert.equal(body.depictedKitEra, era);
    assert.equal(body.width, 1024);
    assert.equal(body.height, 1536);
    assert.equal(bytes.readUInt32BE(16), body.width, `${era} PNG width matches its catalog row`);
    assert.equal(bytes.readUInt32BE(20), body.height, `${era} PNG height matches its catalog row`);
    assert.equal(bytes[25], 6, `${era} PNG carries RGBA alpha`);
    assert.equal(bytes.length, body.bytes, `${era} byte length matches its catalog row`);
    assert.equal(sha, body.sha256, `${era} SHA-256 matches its catalog row`);
    assert.ok(body.foot[1] > 0.97, `${era} foot anchor reaches the ground line`);
  }
});

test('Ranger Ancient uses the versioned transparent cutout with its reviewed foot anchor', () => {
  const body = heroBody('ranger', 0);
  const bytes = fs.readFileSync(body.file);
  const sha = crypto.createHash('sha256').update(bytes).digest('hex');
  assert.equal(body.id, 'class-ranger-ancient-v2');
  assert.equal(body.file.endsWith('/class-ranger-ancient-v2.png'), true);
  assert.equal(body.width, 1100);
  assert.equal(body.height, 1429);
  assert.equal(bytes.readUInt32BE(16), body.width);
  assert.equal(bytes.readUInt32BE(20), body.height);
  assert.equal(bytes[25], 6, 'the replacement retains RGBA transparency');
  assert.equal(bytes.length, body.bytes);
  assert.equal(sha, body.sha256);
  assert.deepEqual(body.foot, [0.683957, 1]);
  assert.equal(body.depictedKitEra, 'ancient');
});

test('Healer Medieval uses the versioned matte repair, with centered boot contact and true alpha', () => {
  const body = heroBody('healer', 3);
  const bytes = fs.readFileSync(body.file);
  const sha = crypto.createHash('sha256').update(bytes).digest('hex');
  assert.equal(body.id, 'class-healer-medieval-v2');
  assert.equal(body.file.endsWith('/class-healer-medieval-v2.png'), true);
  assert.equal(body.width, 966);
  assert.equal(body.height, 1628);
  assert.equal(bytes.readUInt32BE(16), body.width);
  assert.equal(bytes.readUInt32BE(20), body.height);
  assert.equal(bytes[25], 6, 'the replacement retains RGBA transparency');
  assert.equal(bytes.length, body.bytes);
  assert.equal(sha, body.sha256);
  assert.deepEqual(body.foot, [0.586, 1]);
  assert.equal(body.depictedKitEra, 'medieval');
});

test('Warlock Mech uses the versioned transparent cutout without a floor matte', () => {
  const body = heroBody('warlock', 6);
  const bytes = fs.readFileSync(body.file);
  const sha = crypto.createHash('sha256').update(bytes).digest('hex');
  assert.equal(body.id, 'class-warlock-mech-v2');
  assert.equal(body.file.endsWith('/class-warlock-mech-v2.png'), true);
  assert.equal(body.width, 805);
  assert.equal(body.height, 1954);
  assert.equal(bytes.readUInt32BE(16), body.width);
  assert.equal(bytes.readUInt32BE(20), body.height);
  assert.equal(bytes[25], 6, 'the replacement retains RGBA transparency');
  assert.equal(bytes.length, body.bytes);
  assert.equal(sha, body.sha256);
  assert.deepEqual(body.foot, [0.578, 1]);
  assert.equal(body.depictedKitEra, 'mech');
});

test('the reviewed steel knight is not worn Stone gear, and icons follow the item age', () => {
  const knight = heroBody('knight');
  assert.equal(knight.depictedKitEra, 'medieval');
  assert.equal(bodyMatchesKit(knight, 0), false);
  assert.equal(bodyMatchesKit(knight, 3), true);
  assert.equal(bodyMatchesKit(heroBody('ranger'), 0), false);
  const icons = [
    { id: 'stone', slot: 'weapon', age: 0 },
    { id: 'bronze', slot: 'weapon', age: 1 },
  ];
  assert.equal(selectGearIcon(icons, 'weapon', { kind: 'gear', slot: 'weapon', age: 0, quality: 0 }).id, 'stone');
  assert.equal(selectGearIcon(icons, 'weapon', { kind: 'gear', slot: 'weapon', age: 1, quality: 0 }).id, 'bronze');
  assert.equal(selectGearIcon(icons, 'weapon', null), null);
  assert.equal(selectGearIcon(icons, 'accessory', { kind: 'artifact', age: 0 }), null);
});
