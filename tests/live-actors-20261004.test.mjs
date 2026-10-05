import assert from 'node:assert/strict';
import test from 'node:test';
import atlas from '../src/data/actor-atlas.json' with { type: 'json' };
import plates from '../src/data/plate-catalog.json' with { type: 'json' };
import buildings from '../src/data/age-buildings.json' with { type: 'json' };
import { clipAngles, creaturePlate, mountGait, troopPlate } from '../src/client/actor.js';
import { armedChoice, parseChallenge } from '../src/client/choices.js';

const classes = ['knight', 'ranger', 'warlock', 'mage', 'paladin', 'barbarian', 'necromancer', 'healer'];

test('each class assembles its own measured rig', () => {
  const files = new Set();
  for (const id of classes) {
    const spec = atlas.classes[id];
    assert.ok(spec.file.includes(`rigs/${id}.png`));
    assert.ok(spec.parts.torso && spec.parts.head && spec.parts.thigh && spec.parts.shin);
    files.add(spec.file);
  }
  assert.equal(files.size, 8);
  assert.notEqual(atlas.classes.knight.file, atlas.classes.mage.file);
});

test('clips move limbs and mount hooves do not all lift together', () => {
  const idle = clipAngles('idle', 0.2);
  const attack = clipAngles('attack', 0.8);
  assert.notEqual(idle.arm, attack.arm);
  assert.notEqual(clipAngles('death', 0).spine, idle.spine);
  const gait = mountGait(0.2);
  assert.equal(gait.length, 4);
  assert.ok(gait.some(angle => angle < 0));
  assert.ok(gait.some(angle => angle > 0));
  assert.equal(mountGait(0.2, true).every(angle => angle === 6), true);
});

test('army plates follow creature and age, and reject the steam-walker rifleman', () => {
  assert.notEqual(creaturePlate('bear').file, creaturePlate('wolf').file);
  assert.ok(creaturePlate('harpy'));
  assert.ok(troopPlate(2, 'melee'), '1K iron melee legionary stays available');
  assert.equal(plates.troops['5-heavy'].file, 'assets/derivatives/substitutions/v3/troop-industrial-heavy.png');
  assert.equal(troopPlate(5, 'heavy').file, 'assets/derivatives/substitutions/v3/troop-industrial-heavy.png');
  assert.equal(plates.rejected['troop-industrial-heavy'].includes('rifleman'), true);
});

test('choice identity survives a scrolled retarget', () => {
  assert.equal(armedChoice('build:P04:barracks', 'build:P04:mine'), 'build:P04:barracks');
  assert.equal(armedChoice('', 'build:P04:mine'), 'build:P04:mine');
});

test('challenge seed and code are validated locally', () => {
  assert.equal(parseChallenge('99', 'valley').seed, 99);
  assert.equal(parseChallenge('99', 'valley').code, 'valley');
  assert.ok(parseChallenge('-1', 'valley').error);
  assert.ok(parseChallenge('1.5', 'valley').error);
  assert.ok(parseChallenge('12', '').error);
  assert.ok(parseChallenge('4294967296', 'valley').error);
});

test('eight ages have measured building feet', () => {
  for (const age of ['stone', 'bronze', 'iron', 'medieval', 'gunpowder', 'industrial', 'modern', 'future']) {
    const farm = buildings.ages[age].farm;
    assert.ok(farm.file.endsWith(`farm-${age}.png`));
    assert.ok(farm.foot[1] > 0.5 && farm.foot[1] <= 1);
  }
  assert.equal(buildings.status, 'MEASURED_NOT_OWNER_ACCEPTED');
});
