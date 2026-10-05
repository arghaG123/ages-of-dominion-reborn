import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
import { portraitCard, portraitRejected } from '../src/client/portraits.js';

test('class cards stay era-gated and the mounted master stays rejected', () => {
  assert.equal(portraitCard('mage', 0).era, 'ancient');
  assert.equal(portraitCard('knight', 0), null);
  assert.equal(portraitCard('knight', 3).era, 'medieval');
  assert.match(portraitRejected()['knight-mounted-master'], /not a Stone actor/);
  for (const id of ['mage', 'ranger', 'paladin', 'healer']) {
    const card = portraitCard(id, 0);
    const hash = crypto.createHash('sha256').update(fs.readFileSync(card.file)).digest('hex');
    assert.equal(hash, card.sha256);
    assert.equal(card.file.includes('knight-mounted'), false);
  }
});
