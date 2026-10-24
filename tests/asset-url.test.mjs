import test from 'node:test';
import assert from 'node:assert/strict';
import { resolveAssetUrl } from '../src/client/asset-url.js';

test('asset mapping preserves dynamic names, query strings and fragments', () => {
  const map = { 'assets/skill-bolt.png': 'assets/skill-bolt.lossless.webp' };
  assert.equal(resolveAssetUrl(`assets/skill-${'bolt'}.png?v=2#part`, map), 'assets/skill-bolt.lossless.webp?v=2#part');
  assert.equal(resolveAssetUrl('./assets/skill-bolt.png', map), 'assets/skill-bolt.lossless.webp');
  assert.equal(resolveAssetUrl('http://localhost:4175/dist/assets/skill-bolt.png?v=2#part', map), 'http://localhost:4175/dist/assets/skill-bolt.lossless.webp?v=2#part');
  assert.equal(resolveAssetUrl('file:///app/assets/skill-bolt.png', map), 'file:///app/assets/skill-bolt.lossless.webp');
  assert.equal(resolveAssetUrl('https://appassets.androidplatform.net/assets/www/assets/skill-bolt.png?v=2', map), 'https://appassets.androidplatform.net/assets/www/assets/skill-bolt.lossless.webp?v=2');
  for (const value of ['#gradient', 'data:image/png;base64,AA==', 'assets/unconverted.png', '', null, undefined]) {
    assert.equal(resolveAssetUrl(value, map), value);
  }
});

test('source development continues to use originals without a generated build map', () => {
  assert.equal(resolveAssetUrl('assets/skill-bolt.png'), 'assets/skill-bolt.png');
});
