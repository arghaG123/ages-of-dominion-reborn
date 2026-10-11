import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
import heroBodies from '../src/data/hero-bodies-20261011.json' with { type: 'json' };
import { bodyMatchesKit, fitBody, heroBody, kitEra, selectGearIcon } from '../src/client/hero-room.js';

test('hero body contract: seven static standing bodies exist with pinned bytes, Healer recorded missing', () => {
  const ids = Object.keys(heroBodies.bodies);
  assert.equal(ids.length, 7);
  assert.ok(heroBodies.missing?.healer, 'Healer must be recorded as missing, not invented');
  for (const [id, body] of Object.entries(heroBodies.bodies)) {
    assert.ok(fs.existsSync(body.file), `${id} body file missing: ${body.file}`);
    const sha = crypto.createHash('sha256').update(fs.readFileSync(body.file)).digest('hex');
    assert.equal(sha, body.sha256, `${id} body bytes changed`);
    assert.equal(body.status, 'PARTIAL');
    assert.equal(body.articulation, 'NOT_APPLICABLE');
    assert.equal(body.cropROIConvention, 'half-open-xyxy');
    assert.ok(body.cropROI[2] > body.cropROI[0] && body.cropROI[3] > body.cropROI[1]);
    assert.equal(body.notRig, true);
    assert.ok(body.foot[1] > 0.9 && body.foot[1] <= 1, `${id} foot anchor must sit at the matte bottom`);
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
