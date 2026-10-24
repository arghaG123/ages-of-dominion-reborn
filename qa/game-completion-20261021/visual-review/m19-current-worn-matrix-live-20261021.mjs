import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import fs from 'node:fs/promises';
import path from 'node:path';
import kitManifest from '../../../src/data/hero-kit-eras-20261017.json' with { type: 'json' };
import { bodyHasHeldWeapon, bodyMatchesKit, heroBody, kitEra, wornMarks } from '../../../src/client/hero-room.js';

const root = process.cwd();
const output = path.join(root, 'qa/game-completion-20261021/visual-review/m19-current-worn-matrix-live-20261021.json');
const eras = [
  { id: 'ancient', age: 0 },
  { id: 'medieval', age: 3 },
  { id: 'powder', age: 4 },
  { id: 'mech', age: 7 },
];
const slots = ['helm', 'weapon', 'offhand', 'armor', 'boots', 'accessory'];
const rows = [];
const imageCache = new Map();

async function imageRecord(file) {
  if (!imageCache.has(file)) {
    const bytes = await fs.readFile(path.join(root, file));
    imageCache.set(file, {
      file,
      bytes: bytes.length,
      sha256: crypto.createHash('sha256').update(bytes).digest('hex'),
      width: bytes.readUInt32BE(16),
      height: bytes.readUInt32BE(20),
      colorType: bytes[25],
    });
  }
  return imageCache.get(file);
}

for (const classId of Object.keys(kitManifest.classes)) {
  for (const era of eras) {
    const body = heroBody(classId, era.age);
    assert.ok(body?.file, `body exists for ${classId}/${era.id}`);
    const bodyImage = await imageRecord(body.file);
    assert.equal(bodyImage.bytes, body.bytes, `${classId}/${era.id} body byte length`);
    assert.equal(bodyImage.sha256, body.sha256, `${classId}/${era.id} body hash`);
    assert.equal(bodyMatchesKit(body, era.age), true, `${classId}/${era.id} body is assigned to its active kit era`);
    assert.equal(kitEra(era.age), era.id, `${era.id} row uses an age from its kit era`);

    // Synthetic all-slots-worn state enumerates the current painter bindings; it is not a natural player journey.
    const state = {
      age: era.age,
      hero: {
        class: classId,
        equip: Object.fromEntries(slots.map(slot => [slot, {
          id: `matrix-${classId}-${era.id}-${slot}`,
          kind: 'gear',
          slot,
          age: era.age,
          quality: 0,
        }])),
      },
    };
    const marks = wornMarks(state);
    assert.equal(marks.length, slots.length, `${classId}/${era.id} has six decisions`);
    const decisions = [];
    for (const mark of marks) {
      const heldWeaponBakedIntoBody = mark.slot === 'weapon' && bodyHasHeldWeapon(body);
      const status = mark.appearance === 'attached-asset'
        ? 'attached-asset'
        : heldWeaponBakedIntoBody
          ? 'static-baked-weapon'
          : 'socket-only';
      decisions.push({
        slot: mark.slot,
        itemAge: era.age,
        itemId: mark.id,
        painterAppearance: mark.appearance,
        status,
        ...(mark.appearanceFile ? { image: await imageRecord(mark.appearanceFile), anchor: mark.anchor } : {}),
      });
    }
    rows.push({ classId, era: era.id, age: era.age, body: bodyImage, bodyKitMatch: true, heldWeaponBakedIntoBody: bodyHasHeldWeapon(body), decisions });
  }
}

assert.equal(rows.length, 32, 'eight classes cover four kit eras');
assert.equal(rows.reduce((sum, row) => sum + row.decisions.length, 0), 192, 'all six slots are enumerated for all 32 rows');
const summary = Object.fromEntries(['attached-asset', 'static-baked-weapon', 'socket-only'].map(status => [
  status,
  rows.flatMap(row => row.decisions).filter(decision => decision.status === status).length,
]));
assert.deepEqual(summary, { 'attached-asset': 9, 'static-baked-weapon': 24, 'socket-only': 159 });
const images = [...imageCache.values()];
assert.ok(images.every(image => image.width > 0 && image.height > 0 && image.colorType === 6), 'bound body and wearable files decode as RGBA PNGs');

const report = {
  recordedAt: new Date().toISOString(),
  classification: 'CURRENT_SOURCE_BOUND_32_KIT_192_SLOT_MATRIX',
  summary: { classKitRows: rows.length, slotDecisions: 192, ...summary, uniqueBoundImages: images.length },
  interpretation: {
    attachedAsset: 'Current painter has a distinct wearable/held-prop asset for the selected item age and slot.',
    staticBakedWeapon: 'The body plate contains a weapon, so the painter suppresses the selected-item layer; item-specific replacement is not visible.',
    socketOnly: 'The item is recorded in its slot, but no current item-specific body layer is bound.',
  },
  limits: 'The all-slots-worn rows are synthetic source-consumer fixtures. They verify current bindings and file integrity, not natural acquisition, equip persistence, pixel fit, motion integration, or owner acceptance. Existing natural Future Knight captures are reviewed separately.',
  rows,
};
await fs.writeFile(output, JSON.stringify(report, null, 2));
console.log(JSON.stringify({ recordedAt: report.recordedAt, summary: report.summary, output: path.relative(root, output) }, null, 2));
