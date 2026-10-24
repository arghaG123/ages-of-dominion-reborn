import test from 'node:test';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import fs from 'node:fs';
import contract from '../src/data/implementation-contract.json' with { type: 'json' };
import scene from '../src/data/stone-scene.json' with { type: 'json' };
import ageBuildings from '../src/data/age-buildings.json' with { type: 'json' };
import wallSegments from '../src/data/wall-segments-20261016.json' with { type: 'json' };
import { pose, hoofContact } from '../src/client/rig.js';
import { ACTIVE_AFFINE, armyRankStars, armyRosterCapacity, cardInsideStage, heroFocus, heroStage, wallPresentation } from '../src/client/presentation.js';
import { project } from '../src/client/projection.js';
import { footAwareVisibleBox } from '../src/client/visible-size.js';

test('the hero card stays inside the stage and the camera focus contains it', () => {
  const stage = heroStage();
  assert.equal(cardInsideStage(stage), true);
  assert.ok(stage.card.y >= 40);
  const focus = heroFocus(stage);
  assert.ok(focus.minX <= stage.card.x);
  assert.ok(focus.minY <= stage.card.y);
  assert.ok(focus.maxX >= stage.card.x + stage.card.width);
  assert.ok(focus.maxY >= stage.card.y + stage.card.height);
  assert.ok(focus.maxY >= stage.ground.y);
});

test('age Town Hall layers keep their measured foot in-frame at both landscape scales', () => {
  const geo = contract.geometry.kingdom;
  const site = geo.sites.find(row => row.id === 'townhall');
  const [x, y, width, height] = site.rect;
  const feet = project(geo.worldToSource, [x + width / 2, y + height]);
  const left = project(geo.worldToSource, [x, y + height]);
  const right = project(geo.worldToSource, [x + width, y + height]);
  const requested = Math.hypot(right[0] - left[0], right[1] - left[1]) * 1.08;
  for (const [age, buildings] of Object.entries(ageBuildings.ages)) {
    const hall = buildings.townhall;
    for (const scale of [0.6, 0.94]) {
      const fitted = footAwareVisibleBox({ ...hall, maxVisibleCssPx: hall.maxVisibleCssPx || 180 }, requested * (hall.height / hall.width), scale, feet[1], 0, 12);
      const top = feet[1] * scale - fitted.height * hall.foot[1] * scale;
      assert.ok(top >= 12 - 0.01, `${age} Town Hall stays below the viewport top at scale ${scale}`);
      assert.ok(fitted.cssHeight > 0, `${age} Town Hall remains visible at scale ${scale}`);
    }
  }
});

test('repaired Town Hall ages use the reviewed versioned assets and measured pivots', () => {
  const expected = {
    gunpowder: { hash: 'a89172e609aa5bb559b24a93c640ae11996ff340dfd3724432f6c1f7a7e21091', foot: [0.5, 0.95] },
    industrial: { hash: '2014c11adac68355f50d4dbd4324bfc1893217722d0309129fffcd659cd6f11d', foot: [0.5, 0.95] },
    modern: { hash: 'b63a3c2276f77dd8926fdd555e64c038813849401c67bfb095f97c3712c8b8fb', foot: [0.5, 0.877] },
  };
  for (const [age, reviewed] of Object.entries(expected)) {
    const hall = ageBuildings.ages[age].townhall;
    const bytes = fs.readFileSync(hall.file);
    assert.equal(bytes.subarray(1, 4).toString('ascii'), 'PNG', `${age} Town Hall is a PNG`);
    assert.equal(crypto.createHash('sha256').update(bytes).digest('hex'), reviewed.hash, `${age} file hash`);
    assert.equal(hall.sourceSHA256, reviewed.hash, `${age} source hash matches`);
    assert.deepEqual([hall.width, hall.height], [1254, 1254], `${age} source dimensions`);
    assert.deepEqual(hall.foot, reviewed.foot, `${age} measured ground pivot`);
    assert.equal(hall.generation.tool, 'Codex built-in image_gen');
    assert.deepEqual(hall.generation.reviewedAt, ['1280x720', '825x375']);
  }
});

test('Stone day 1 keeps the active affine, hall, seventeen sites and a separate wall trace', () => {
  assert.deepEqual(contract.geometry.kingdom.worldToSource, ACTIVE_AFFINE);
  assert.deepEqual(scene.camera, ACTIVE_AFFINE);
  assert.equal(scene.hall.matrix[0][0], 0.1312);
  const sites = contract.geometry.kingdom.sites;
  assert.equal(sites.length, 18);
  assert.equal(sites.filter(site => site.id !== 'townhall').length, 17);
  const walls = wallPresentation(contract.geometry.kingdom);
  assert.equal(walls.contractUnchanged, true);
  assert.equal(walls.version, 'walls-isometric-v4');
  const byId = Object.fromEntries(walls.segments.map(segment => [segment.id, segment]));
  const cornerAt = id => walls.corners.find(corner => corner.id === id).at;
  assert.deepEqual(byId.back.a, cornerAt('nw'));
  assert.deepEqual(byId.back.b, cornerAt('ne'));
  assert.deepEqual(byId['side-west-far'].a, cornerAt('nw'));
  assert.deepEqual(byId['side-west-far'].b, byId['side-west-near'].a);
  assert.deepEqual(byId['side-west-near'].b, cornerAt('sw'));
  assert.deepEqual(byId['side-east-far'].a, cornerAt('ne'));
  assert.deepEqual(byId['side-east-near'].b, cornerAt('se'));
  assert.deepEqual(byId['front-west'].a, cornerAt('sw'));
  assert.deepEqual(byId['front-east'].b, cornerAt('se'));
  const gate = contract.geometry.kingdom.anchors.gate[0];
  assert.ok(byId['front-west'].b[0] < gate);
  assert.ok(byId['front-east'].a[0] > gate);
  assert.equal(walls.gate[0], gate);
  assert.equal(walls.road[0], gate);
  assert.equal(walls.gate[1], walls.road[1]);
  assert.equal(byId.back.depth, 'back');
  assert.equal(byId['side-west-far'].depth, 'back');
  assert.equal(byId['side-west-near'].depth, 'front');
  assert.equal(byId['front-west'].depth, 'front');
  for (const age of contract.ages) {
    for (const part of ['run', 'corner', 'gate']) {
      const piece = wallSegments.ages[age][part];
      assert.ok(piece.width > 0 && piece.height > 0);
      assert.equal(fs.existsSync(piece.file), true);
    }
  }
});

test('schematic walk and mount clips plant and lift feet without using a card transform', () => {
  const standing = pose('walk', 0, { reduced: true });
  assert.equal(hoofContact(standing), 2);
  const walking = pose('walk', 0.25, { reduced: false });
  assert.ok(hoofContact(walking) < 2);
  const plantedMount = pose('mountWalk', 0, { reduced: true });
  assert.equal(hoofContact(plantedMount), 4);
  const movingMount = pose('mountWalk', 0.2, { reduced: false });
  assert.ok(hoofContact(movingMount) < 4);
  assert.ok(hoofContact(movingMount) >= 1);
});

test('army roster shows four bounded rank positions and accessible formation capacity', () => {
  assert.equal(armyRankStars(0), '☆☆☆☆');
  assert.equal(armyRankStars(2), '★★☆☆');
  assert.equal(armyRankStars(4), '★★★★');
  assert.throws(() => armyRankStars(5), RangeError);
  assert.deepEqual(armyRosterCapacity(3, 4), { value: 3, max: 4, ratio: 0.75, label: '3 of 4 formations' });
  assert.throws(() => armyRosterCapacity(3, 2), RangeError);
});
