import test from 'node:test';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import assert from 'node:assert/strict';
import { drawActor, isWearLayerSupported, paintWornSlots, shouldDrawRigWeapon, WORN_ANCHORS } from '../src/client/actor.js';
import { bodyHasHeldWeapon, forgeWeaponPreviewArt, forgeWeaponPreviewPose, heroBody, wornGearArt, wornMarks, wornWeaponArt } from '../src/client/hero-room.js';

function element(name, attributes = {}) {
  return {
    name,
    attributes: { ...attributes },
    children: [],
    append(child) { this.children.push(child); },
    prepend(child) { this.children.unshift(child); },
    querySelector(selector) {
      const id = selector.startsWith('#') ? selector.slice(1) : selector;
      const visit = node => node.attributes?.id === id || node.children?.some(visit);
      return this.children.find(visit) || null;
    },
  };
}

function find(node, predicate) {
  if (predicate(node)) return node;
  for (const child of node.children || []) {
    const result = find(child, predicate);
    if (result) return result;
  }
  return null;
}

function svgElement(name, attributes = {}) {
  const values = Object.entries(attributes).map(([key, value]) => ({ name: key, value: String(value) }));
  const node = {
    name,
    attributes: values,
    children: [],
    parentElement: null,
    append(child) { child.parentElement = this; this.children.push(child); },
    getAttribute(key) { return this.attributes.find(attribute => attribute.name === key)?.value ?? null; },
    setAttribute(key, value) {
      const found = this.attributes.find(attribute => attribute.name === key);
      if (found) found.value = String(value);
      else this.attributes.push({ name: key, value: String(value) });
    },
    removeAttribute(key) { this.attributes = this.attributes.filter(attribute => attribute.name !== key); },
    querySelector(selector) {
      const match = selector.match(/^\[([^=]+)="([^"]+)"\]$/);
      if (!match) return null;
      const [, key, value] = match;
      const visit = parent => {
        for (const child of parent.children) {
          if (child.getAttribute(key) === value) return child;
          const nested = visit(child);
          if (nested) return nested;
        }
        return null;
      };
      return visit(this);
    },
  };
  return node;
}

function svgFind(node, predicate) {
  if (predicate(node)) return node;
  for (const child of node.children || []) {
    const result = svgFind(child, predicate);
    if (result) return result;
  }
  return null;
}

function hasSvgAncestor(node, key, value) {
  for (let parent = node.parentElement; parent; parent = parent.parentElement) {
    if (parent.getAttribute(key) === value) return true;
  }
  return false;
}

test('every campaign age selects a verified native-alpha held weapon layer', () => {
  const files = [
    'assets/derivatives/worn-gear-20261018/flint-club-stone.png',
    'assets/derivatives/worn-gear-20261020/weapon-bronze.png',
    'assets/derivatives/worn-gear-20261020/weapon-iron.png',
    'assets/derivatives/worn-gear-20261020/weapon-medieval.png',
    'assets/derivatives/worn-gear-20261020/weapon-gunpowder.png',
    'assets/derivatives/worn-gear-20261020/weapon-industrial.png',
    'assets/derivatives/worn-gear-20261020/weapon-modern.png',
    'assets/derivatives/worn-gear-20261020/weapon-future.png',
  ];
  files.forEach((file, age) => {
    const layer = wornWeaponArt({ kind: 'gear', slot: 'weapon', age }, 'knight');
    assert.equal(layer.file, file);
    assert.equal(isWearLayerSupported('weapon', layer), true);
    assert.equal(layer.aspect, 1.5);
    assert.deepEqual(layer.sourceAnchor, [0.78, 0.72]);
    assert.equal(layer.rotate, age === 3 ? -96 : 0);
    const asset = readFileSync(fileURLToPath(new URL(`../${file}`, import.meta.url)));
    assert.deepEqual([...asset.subarray(0, 8)], [137, 80, 78, 71, 13, 10, 26, 10], `${file} is a PNG`);
    assert.equal(asset.readUInt32BE(16), 1536, `${file} width`);
    assert.equal(asset.readUInt32BE(20), 1024, `${file} height`);
    assert.equal(asset[25], 6, `${file} has an RGBA alpha channel`);
    assert.equal(forgeWeaponPreviewArt(age), file, 'forge recipe illustration uses the same age weapon without implying worn support');
    assert.deepEqual(forgeWeaponPreviewPose(age), { x: 285, y: 288.333, width: 500, height: 333.333, rotation: -33 }, 'the full-size source-backed workpiece lies across the anvil');
  });
  assert.equal(wornWeaponArt({ kind: 'gear', slot: 'weapon', age: 7 }, 'mage'), null,
    'class-specific role props are not replaced with a generic sword');
  assert.equal(bodyHasHeldWeapon({ depictedKitEvidence: 'Reviewed steel armor and a longsword.' }), true);
  assert.equal(bodyHasHeldWeapon({ depictedKitEvidence: 'Hide, linen and a leather cap.' }), false);
  assert.equal(wornWeaponArt({ kind: 'artifact', slot: 'weapon', age: 7 }), null);
  assert.equal(wornWeaponArt({ kind: 'gear', slot: 'armor', age: 7 }), null);
  assert.equal(wornWeaponArt({ kind: 'gear', slot: 'weapon', age: 8 }), null);
  assert.equal(forgeWeaponPreviewArt(-1), null);
  assert.equal(forgeWeaponPreviewArt(8), null);
  assert.equal(forgeWeaponPreviewPose(-1), null);
  assert.equal(forgeWeaponPreviewPose(8), null);
});

test('Medieval and Future Knight bodies are unarmed so each equipped weapon supplies the visible prop', () => {
  const cases = [
    { age: 3, id: 'class-knight-medieval-unarmed-v1', width: 822, height: 1914, weapon: 'assets/derivatives/worn-gear-20261020/weapon-medieval.png' },
    { age: 7, id: 'class-knight-mech-unarmed-v1', width: 767, height: 2051, weapon: 'assets/derivatives/worn-gear-20261020/weapon-future.png' },
  ];
  for (const { age, id, width, height, weapon: weaponFile } of cases) {
    const body = heroBody('knight', age);
    assert.equal(body.id, id);
    assert.equal(body.depictedKitEra, age === 3 ? 'medieval' : 'mech');
    assert.equal(bodyHasHeldWeapon(body), false);

    const png = readFileSync(fileURLToPath(new URL(`../${body.file}`, import.meta.url)));
    assert.deepEqual([...png.subarray(0, 8)], [137, 80, 78, 71, 13, 10, 26, 10]);
    assert.equal(png.readUInt32BE(16), width);
    assert.equal(png.readUInt32BE(20), height);
    assert.equal(png[25], 6, 'the base figure keeps native alpha');

    const marks = wornMarks({
      age,
      hero: {
        class: 'knight',
        equip: { weapon: { id: `age-${age}-sword`, kind: 'gear', slot: 'weapon', age, quality: 0 } },
      },
    });
    const weapon = marks.find(mark => mark.slot === 'weapon');
    assert.equal(weapon.appearance, 'attached-asset');
    assert.equal(weapon.appearanceFile, weaponFile);
  }
});

test('Future Knight wearable layers use native alpha and are limited to their reviewed class and age', () => {
  const cases = [
    { slot: 'helm', width: 1144, height: 1375, file: 'assets/derivatives/visual-repair-20261020/hero-gear/class-knight-future-helm-v1.png' },
    { slot: 'offhand', width: 1312, height: 1199, file: 'assets/derivatives/visual-repair-20261020/hero-gear/class-knight-future-offhand-v1.png' },
    { slot: 'armor', width: 1222, height: 1287, file: 'assets/derivatives/visual-repair-20261020/hero-gear/class-knight-future-armor-v1.png' },
    { slot: 'boots', width: 1536, height: 1024, file: 'assets/derivatives/visual-repair-20261020/hero-gear/class-knight-future-boots-v2.png' },
    { slot: 'accessory', width: 1254, height: 1254, file: 'assets/derivatives/visual-repair-20261020/hero-gear/class-knight-future-accessory-v1.png' },
  ];
  for (const { slot, width, height, file } of cases) {
    const layer = wornGearArt({ kind: 'gear', slot, age: 7 }, 'knight');
    assert.equal(layer.file, file);
    assert.equal(isWearLayerSupported(slot, layer), true);
    if (slot === 'boots') assert.deepEqual(layer.fit, { w: 0.62, h: 0.25 });
    if (slot === 'accessory') assert.deepEqual(layer.fit, { w: 0.22, h: 0.16 });
    assert.equal(wornGearArt({ kind: 'gear', slot, age: 6 }, 'knight'), null);
    assert.equal(wornGearArt({ kind: 'gear', slot, age: 7 }, 'mage'), null);

    const png = readFileSync(fileURLToPath(new URL(`../${layer.file}`, import.meta.url)));
    assert.deepEqual([...png.subarray(0, 8)], [137, 80, 78, 71, 13, 10, 26, 10]);
    assert.equal(png.readUInt32BE(16), width);
    assert.equal(png.readUInt32BE(20), height);
    assert.equal(png[25], 6, `${slot} retains native alpha`);

    const marks = wornMarks({
      age: 7,
      hero: { class: 'knight', equip: { [slot]: { id: `future-${slot}`, kind: 'gear', slot, age: 7 } } },
    });
    const mark = marks.find(item => item.slot === slot);
    assert.equal(mark.appearance, 'attached-asset');
    assert.equal(mark.appearanceFile, layer.file);
  }
});

test('catalogue icons stay in sockets unless an explicit native-alpha attachment layer exists', () => {
  const hero = element('g');
  const aspect = 1.5;
  const transparentClub = {
    id: 'flint-club', icon: 'assets/gear/weapon-stone.png',
    wearLayer: {
      file: 'assets/derivatives/worn-gear-20261018/flint-club-stone.png',
      aspect, sourceAnchor: [0.78, 0.72], assetRole: 'held-prop', nativeAlpha: true,
      rotate: -96,
    },
  };
  const iconOnlyHelm = {
    id: 'helm',
    icon: 'assets/gear/helm.png',
    wearLayer: {
      file: 'assets/gear/helm.png', aspect: 1, sourceAnchor: [0.5, 0.5],
      assetRole: 'wearable-layer', nativeAlpha: false,
    },
  };
  assert.equal(isWearLayerSupported('weapon', transparentClub.wearLayer), true);
  assert.equal(shouldDrawRigWeapon(null), true, 'actors without a worn-kit context keep their default rig prop');
  assert.equal(shouldDrawRigWeapon({ items: {} }), false, 'a live actor with no equipped weapon has no rig prop');
  assert.equal(shouldDrawRigWeapon({ items: { weapon: transparentClub } }), false,
    'a native-alpha held prop replaces the rig weapon rather than drawing twice');
  assert.equal(shouldDrawRigWeapon({ items: { weapon: { id: 'icon-only', icon: 'assets/gear/weapon-stone.png' } } }), true,
    'an unsupported body layer keeps the rig weapon fallback');
  assert.equal(isWearLayerSupported('helm', iconOnlyHelm.wearLayer), false,
    'a catalogue product plate is not body-compatible wearable art');
  paintWornSlots(hero, element, { items: { weapon: transparentClub, helm: iconOnlyHelm } }, {
    x: 10, y: 20, width: 200, height: 500,
  });

  const weapon = find(hero, node => node.name === 'g' && node.attributes['data-worn-slot'] === 'weapon');
  const weaponImage = find(weapon, node => node.name === 'image');
  assert.equal(weapon.attributes['data-worn-appearance'], 'attached-asset');
  assert.equal(weaponImage.attributes.href, transparentClub.wearLayer.file);
  assert.equal(weaponImage.attributes.filter, undefined, 'native transparent art keeps its original alpha');
  assert.equal(weaponImage.attributes['data-wear-layer-role'], 'held-prop');
  const layer = find(weapon, node => node.name === 'g' && node.attributes['data-slot-layer'] === 'weapon');
  assert.equal(layer.attributes['data-anchor'], WORN_ANCHORS.weapon.join(','));
  assert.equal(layer.attributes['data-source-anchor'], '0.78,0.72');
  assert.match(layer.attributes.transform, /rotate\(-96\)/);
  assert.ok(Math.abs(Number(weaponImage.attributes.width) / Number(weaponImage.attributes.height) - aspect) < 1e-9,
    'the held prop keeps its source aspect ratio');

  const helm = find(hero, node => node.name === 'g' && node.attributes['data-worn-slot'] === 'helm');
  assert.equal(helm.attributes['data-worn-appearance'], 'socket-only');
  assert.equal(find(helm, node => node.name === 'image'), null,
    'unsupported helmet art stays in its UI socket, not over the head');

  const iconOnly = element('g');
  paintWornSlots(iconOnly, element, { items: { helm: iconOnlyHelm } }, {
    x: 10, y: 20, width: 200, height: 500,
  });
  assert.equal(find(iconOnly, node => node.name === 'image'), null);

  const emptyHero = element('g');
  paintWornSlots(emptyHero, element, { items: {} }, {
    x: 10, y: 20, width: 200, height: 500,
  });
  const empty = find(emptyHero, node => node.name === 'g' && node.attributes['data-worn-slot'] === 'boots');
  assert.equal(empty.attributes['data-worn-state'], 'empty');
  assert.equal(find(empty, node => node.name === 'image'), null, 'unequipped slots do not paint a visual item');
});

test('paired boots inherit each animated leg through a walking stride', () => {
  const worn = { items: { boots: { id: 'future-boots', wearLayer: wornGearArt({ kind: 'gear', slot: 'boots', age: 7 }, 'knight') } } };
  const readStride = time => {
    const world = svgElement('svg');
    const root = drawActor(world, svgElement, 'knight', { x: 120, y: 240, scale: 0.4, clip: 'walk', time, worn });
    const overlays = [];
    const collect = node => {
      if (node.getAttribute?.('data-boot-overlay')) overlays.push(node);
      for (const child of node.children || []) collect(child);
    };
    collect(root);
    return Object.fromEntries(overlays.map(overlay => {
      const side = overlay.getAttribute('data-boot-overlay');
      let thigh = overlay.parentElement;
      while (thigh && thigh.getAttribute('data-joint') !== 'thigh') thigh = thigh.parentElement;
      let shin = overlay.parentElement;
      while (shin && shin.getAttribute('data-joint') !== 'shin') shin = shin.parentElement;
      return [side, { thigh: thigh?.getAttribute('data-angle'), shin: shin?.getAttribute('data-angle') }];
    }));
  };
  const leftForward = readStride(0.25);
  const rightForward = readStride(0.75);
  assert.deepEqual(Object.keys(leftForward).sort(), ['far', 'near']);
  assert.notEqual(leftForward.far.thigh, rightForward.far.thigh);
  assert.notEqual(leftForward.far.shin, rightForward.far.shin);
  assert.notEqual(leftForward.near.thigh, rightForward.near.thigh);
  assert.notEqual(leftForward.near.shin, rightForward.near.shin);
});

test('articulated actor wear layers inherit the matching head, spine, and wrist joints', () => {
  const world = svgElement('svg');
  const worn = {
    items: {
      weapon: { id: 'future-weapon', wearLayer: wornWeaponArt({ kind: 'gear', slot: 'weapon', age: 7 }, 'knight') },
      helm: { id: 'future-helm', wearLayer: wornGearArt({ kind: 'gear', slot: 'helm', age: 7 }, 'knight') },
      offhand: { id: 'future-offhand', wearLayer: wornGearArt({ kind: 'gear', slot: 'offhand', age: 7 }, 'knight') },
      armor: { id: 'future-armor', wearLayer: wornGearArt({ kind: 'gear', slot: 'armor', age: 7 }, 'knight') },
      boots: { id: 'future-boots', wearLayer: wornGearArt({ kind: 'gear', slot: 'boots', age: 7 }, 'knight') },
      accessory: { id: 'future-accessory', wearLayer: wornGearArt({ kind: 'gear', slot: 'accessory', age: 7 }, 'knight') },
    },
  };
  const root = drawActor(world, svgElement, 'knight', { x: 120, y: 240, scale: 0.4, clip: 'attack', time: 0.35, worn });
  assert.ok(root, 'the reviewed joint actor is available');

  const slot = name => svgFind(root, node => node.getAttribute?.('data-worn-slot') === name);
  const weapon = slot('weapon');
  const helm = slot('helm');
  const armor = slot('armor');
  assert.equal(weapon.getAttribute('data-attached-to'), 'hand');
  assert.ok(hasSvgAncestor(weapon, 'data-joint', 'weapon'));
  assert.ok(hasSvgAncestor(weapon, 'data-joint', 'forearm'));
  assert.ok(hasSvgAncestor(weapon, 'data-joint', 'arm'));
  assert.ok(hasSvgAncestor(weapon, 'data-joint', 'spine'));
  assert.equal(helm.getAttribute('data-attached-to'), 'head');
  assert.ok(hasSvgAncestor(helm, 'data-joint', 'neck'));
  assert.ok(hasSvgAncestor(helm, 'data-joint', 'spine'));
  assert.equal(armor.getAttribute('data-attached-to'), 'spine');
  assert.equal(armor.parentElement.getAttribute('data-joint'), 'spine');
  for (const name of ['offhand', 'accessory']) {
    assert.equal(slot(name).getAttribute('data-attached-to'), 'spine');
    assert.equal(slot(name).parentElement.getAttribute('data-joint'), 'spine');
  }
  const bootOverlays = [];
  const collectBoots = node => {
    if (node.getAttribute?.('data-boot-overlay')) bootOverlays.push(node);
    for (const child of node.children || []) collectBoots(child);
  };
  collectBoots(root);
  assert.equal(bootOverlays.length, 2, 'the reviewed pair layer is split into one overlay per foot');
  assert.deepEqual(bootOverlays.map(node => node.getAttribute('data-boot-overlay')), ['far', 'near']);
  for (const overlay of bootOverlays) {
    const boot = overlay.parentElement;
    assert.equal(boot.getAttribute('data-worn-slot'), 'boots');
    assert.equal(boot.getAttribute('data-attached-to'), 'foot');
    assert.equal(boot.parentElement.getAttribute('data-joint'), 'foot');
    assert.ok(hasSvgAncestor(boot, 'data-joint', 'shin'));
    assert.ok(hasSvgAncestor(boot, 'data-joint', 'thigh'));
    assert.ok(hasSvgAncestor(boot, 'data-joint', 'spine'));
  }
  assert.equal(svgFind(root, node => node.getAttribute?.('data-worn-slot') === 'weapon' && node.parentElement === root), null,
    'supported weapon art is no longer painted as a root-level overlay');
});
