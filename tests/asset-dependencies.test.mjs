import test from 'node:test';
import assert from 'node:assert/strict';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { collectAssetDependencies } from '../scripts/asset-dependencies.mjs';
import worlds from '../src/data/adventure-worlds.json' with { type: 'json' };
import { SKILL_IDS } from '../src/core/rules.js';
import data from '../src/data/reference-data.json' with { type: 'json' };

const root = path.resolve(fileURLToPath(new URL('..', import.meta.url)));
test('package closure keeps every production map, skill icon and Kingdom wall phase', async () => {
  const closure = await collectAssetDependencies(root);
  assert.deepEqual(closure.missing, []);
  assert.deepEqual(closure.unresolvedTemplates, []);
  for (const world of Array.isArray(worlds) ? worlds : worlds.worlds) {
    assert.ok(closure.files.includes(world.productionMapFile), world.id);
  }
  for (const id of SKILL_IDS) {
    assert.ok(closure.files.includes(`assets/derivatives/image-residual-executor-20261007/environment/icons/skills/skill-${id}.png`), id);
  }
  for (const id of Object.keys(data.SPELLS)) {
    assert.ok(closure.files.includes(`assets/derivatives/image-residual-executor-20261007/environment/icons/spells/spell-${id}.png`), id);
  }
  assert.equal(closure.files.filter(file => file.includes('/kingdom-families-20261018/')).length, 28);
  assert.equal(closure.files.filter(file => file.includes('/kingdom-stone-populated-20261021/')).length, 4);
});

test('review output paths and reference maps do not become package image dependencies', async () => {
  const closure = await collectAssetDependencies(root);
  assert.ok(!closure.files.some(file => file.includes('/owner-approved-vast-adventure-maps-20261020/')));
  assert.ok(!closure.files.includes('assets/derivatives/image-residual-executor-20261007/actors/mounts/knight-mounted-master.png'));
});
