import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { saveButtonFeedback } from '../src/client/save-feedback.js';

test('save button intent and accessible label stay aligned with durable state', () => {
  assert.deepEqual(saveButtonFeedback('committed'), { action: 'save', label: 'Save campaign' });
  assert.deepEqual(saveButtonFeedback('pending'), { action: 'wait', label: 'Saving campaign' });
  assert.deepEqual(saveButtonFeedback('failed'), {
    action: 'export-unsaved',
    label: 'Save failed. Export your unsaved campaign',
  });
});

test('failed save button exports the in-memory candidate instead of retrying stale CAS', () => {
  const source = fs.readFileSync(new URL('../src/client/main.js', import.meta.url), 'utf8');
  assert.match(source, /const feedback = saveButtonFeedback\(status\.kind\)/);
  assert.match(source, /const feedback = saveButtonFeedback\(saveQueue\.status\.kind\);[\s\S]*?if \(feedback\.action === 'export-unsaved'\) \{[\s\S]*?download\('aod-unsaved-campaign\.json', encode\(state, data\)\)/);
  assert.match(source, /if \(feedback\.action !== 'save'\) return;/);
});
