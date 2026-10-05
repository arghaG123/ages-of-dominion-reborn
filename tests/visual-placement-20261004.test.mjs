import test from 'node:test';
import assert from 'node:assert/strict';
import contract from '../src/data/implementation-contract.json' with { type: 'json' };
import scene from '../src/data/stone-scene.json' with { type: 'json' };
import { pose, hoofContact } from '../src/client/rig.js';
import { ACTIVE_AFFINE, cardInsideStage, heroFocus, heroStage, wallPresentation } from '../src/client/presentation.js';

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

test('Stone day 1 keeps the active affine, hall, seventeen sites and a separate wall trace', () => {
  assert.deepEqual(contract.geometry.kingdom.worldToSource, ACTIVE_AFFINE);
  assert.deepEqual(scene.camera, ACTIVE_AFFINE);
  assert.equal(scene.hall.matrix[0][0], 0.1312);
  const sites = contract.geometry.kingdom.sites;
  assert.equal(sites.length, 18);
  assert.equal(sites.filter(site => site.id !== 'townhall').length, 17);
  const walls = wallPresentation(contract.geometry.kingdom);
  assert.equal(walls.contractUnchanged, true);
  assert.equal(walls.version, 'walls-presentation-v1');
  assert.ok(walls.points.length >= 6);
  const gate = contract.geometry.kingdom.anchors.gate[0];
  assert.ok(walls.points[0][0] < gate);
  assert.ok(walls.points.at(-1)[0] > gate);
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
