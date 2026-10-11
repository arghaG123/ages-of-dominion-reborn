import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
import plates from '../src/data/plate-catalog.json' with { type: 'json' };
import binding from '../src/data/anatomy-binding-v1.json' with { type: 'json' };

const bound = {
  '0-heavy': ['assets/derivatives/actors/v5/troop-stone-heavy.png', 'dde192c590f148b9883b29e69f0dbba3c4fa2a78257aeace17d352c173359a37'],
  '1-melee': ['assets/derivatives/actors/v4/troop-bronze-melee.png', 'd9c6c3c6f773eaa4ffbd892a3b04e8af083ae1f84426d42c0332bce6da0ef593'],
  '1-ranged': ['assets/derivatives/actors/v4/troop-bronze-ranged.png', '37dd82bc78e87c77e483ab4544141eb26590cc1e98b02328ea40f0164da221aa'],
  '2-ranged': ['assets/derivatives/actors/v4/troop-iron-ranged.png', '5adcd8ffd5ce1c349abda1c913ca1a7c44281571fcaa5bfb38348ae6241d7780'],
  '4-melee': ['assets/derivatives/actors/v4/troop-gunpowder-melee.png', '307adeb670a6f81f25b4e0b1118e645da712d5b752429cd2a726cb89498c00d4'],
  '4-ranged': ['assets/derivatives/actors/v4/troop-gunpowder-ranged.png', 'd4ee6bebee78ef0bb3f6659e55b099f5ad0307831bfe931bd164ce542dcdd403'],
  '6-melee': ['assets/derivatives/actors/v4/troop-modern-melee.png', 'de22ca26babb42396a2741c9f54a5ac3e9f4da36c49732a01c4679bc4567d779'],
  '7-melee': ['assets/derivatives/actors/v4/troop-future-melee.png', 'fe23ac2e32c9cba7294873a33435dbb3c3e529f560c6424f9fa1553453c3f445'],
};

test('ready static plates are the consumer and the previous files stay on disk', () => {
  for (const [key, [file, hash]] of Object.entries(bound)) {
    const plate = plates.troops[key];
    assert.equal(plate.file, file);
    assert.equal(plate.staticMaxHeight, 130);
    assert.equal(plate.pose, 'single');
    const bytes = fs.readFileSync(file);
    assert.equal(crypto.createHash('sha256').update(bytes).digest('hex'), hash);
    assert.equal(fs.existsSync(plate.previousFile), true);
  }
  const drawn = JSON.stringify(binding.parts);
  assert.equal(drawn.includes('rigs/v7/healer'), false);
  assert.equal(drawn.includes('paladin'), false);
  assert.equal(binding.classId, 'ranger');
});
