import assert from 'node:assert/strict';
import { writeFile } from 'node:fs/promises';
import { drawActor, clipAngles } from '../../src/client/actor.js';

function element(name, attrs = {}) {
  const node = {
    name,
    attrs,
    children: [],
    append(child) { this.children.push(child); },
    querySelector(selector) {
      const want = selector.match(/data-joint="([^"]+)"/)?.[1];
      const walk = (item) => {
        if (item.attrs?.['data-joint'] === want) return item;
        for (const child of item.children) {
          const found = walk(child);
          if (found) return found;
        }
        return null;
      };
      return walk(node);
    },
  };
  return node;
}

function joints(root) {
  const found = [];
  const walk = (item) => {
    if (item.attrs?.['data-joint']) found.push(item.attrs['data-joint']);
    if (item.attrs?.transform?.includes('rotate')) found.push(item.attrs.transform);
    for (const child of item.children) walk(child);
  };
  walk(root);
  return found;
}

const classes = ['knight', 'ranger', 'warlock', 'mage', 'paladin', 'barbarian', 'necromancer', 'healer'];
const worn = { items: { weapon: { id: 'flint-club', bonus: 'atk+1', icon: 'assets/x.png', iconId: 'gear-stone-weapon' } } };
const report = [];
for (const classId of classes) {
  const early = drawActor({ append() {} }, element, classId, { clip: 'walk', time: 0.25, worn });
  assert.ok(early, `${classId} drawActor returned before the gait`);
  assert.equal(early.attrs['data-gait'], 'per-joint');
  const slots = [];
  const walk = (item) => {
    if (item.attrs?.['data-worn-slot']) slots.push(item.attrs['data-worn-slot']);
    for (const child of item.children) walk(child);
  };
  walk(early);
  assert.deepEqual(slots, ['helm', 'weapon', 'offhand', 'armor', 'boots', 'accessory']);
  const planted = drawActor({ append() {} }, element, classId, { clip: 'walk', time: 0.25 });
  const swung = drawActor({ append() {} }, element, classId, { clip: 'walk', time: 0.75 });
  assert.notEqual(joints(planted).join('|'), joints(swung).join('|'), `${classId} walk joints did not move`);
  report.push({ classId, gait: early.attrs['data-gait'], slots, thigh: early.attrs['data-thigh'] });
}
const walkA = clipAngles('walk', 0.25);
const walkB = clipAngles('walk', 0.75);
assert.notEqual(walkA.thighL, walkA.shinL);
assert.notEqual(walkA.arm, walkA.forearm);
assert.notEqual(walkA.thighL, walkB.thighL);
await writeFile(new URL('./rig-gait.json', import.meta.url), JSON.stringify({ pass: true, classes: report }, null, 2));
console.log('rig gait pass', classes.length);
