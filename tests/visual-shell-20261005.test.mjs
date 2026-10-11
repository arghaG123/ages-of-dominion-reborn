import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import modeScenes from '../src/data/mode-scenes.json' with { type: 'json' };
import { KINGDOM_PAD_PRESENTATION, cardInsideStage, heroStage } from '../src/client/presentation.js';
import { plateOffset } from '../src/client/actor.js';

test('mode paintings cover eight ages and the hero card has no side figure', () => {
  assert.equal(KINGDOM_PAD_PRESENTATION, 'kingdom-pad-state-v2');
  for (const mode of ['adventure', 'tactical', 'defense']) {
    assert.equal(modeScenes[mode].length, 8);
    for (const file of modeScenes[mode]) assert.equal(fs.existsSync(file), true);
  }
  const stage = heroStage();
  assert.equal(cardInsideStage(stage), true);
  assert.ok(stage.figure.x < stage.card.x + stage.card.width);
  assert.deepEqual(plateOffset(0.25, { clip: 'walk', reduced: true }), { y: 0, rot: 0 });
});
