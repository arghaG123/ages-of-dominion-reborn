import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
import selection from '../src/data/reviewed-source-selection.json' with { type: 'json' };
import padFit from '../src/data/building-pad-fit-v1.json' with { type: 'json' };

const sha = path => crypto.createHash('sha256').update(fs.readFileSync(path)).digest('hex');

test('pad-fit building and actor selection bindings match on-disk derivatives', () => {
  assert.equal(padFit.status, 'PROPOSAL_NOT_ACCEPTED');
  for (const [type, art] of Object.entries(padFit.buildings)) {
    const row = selection.delivery[art.selectionKey];
    assert.ok(row, type);
    assert.ok(fs.existsSync(row.file), row.file);
    assert.equal(sha(row.file), row.sha256, art.selectionKey);
    assert.equal(row.runtimeApproved, false);
    assert.equal(row.ownerAcceptance, 'UNVERIFIED');
  }
  for (const key of ['rig-knight', 'creature-wolf', 'barracks-stone']) {
    const row = selection.delivery[key];
    assert.ok(fs.existsSync(row.file), key);
    assert.equal(sha(row.file), row.sha256, key);
  }
  // Prior Hall derivative identity stays on the recorded hash.
  assert.equal(selection.delivery['townhall-stone'].sha256, 'f359a8b72100be8ad78eaf61eede19bc8b2db3bd0a1d071050a51edce22cc37c');
});
