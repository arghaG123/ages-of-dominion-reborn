import test from 'node:test';
import assert from 'node:assert/strict';
import { beginActorFrame, drawMount, drawPlate } from '../src/client/actor.js';

function renderer() {
  const created = [];
  const element = (name, values = {}) => {
    const attributes = new Map(Object.entries(values).map(([key, value]) => [key, String(value)]));
    const node = {
      name,
      childNodes: [],
      get attributes() { return [...attributes].map(([key, value]) => ({ name: key, value })); },
      getAttribute(key) { return attributes.get(key) ?? null; },
      setAttribute(key, value) { attributes.set(key, String(value)); },
      removeAttribute(key) { attributes.delete(key); },
      append(...nodes) { this.childNodes.push(...nodes); },
    };
    created.push(node);
    return node;
  };
  return { created, element, world: element('svg') };
}

test('actor redraw reuses loaded sprite images while updating their display attributes', () => {
  const drawing = renderer();
  const plate = { file: 'assets/test-only.png', width: 100, height: 200, maxVisibleCssPx: 130 };
  beginActorFrame();
  drawPlate(drawing.world, drawing.element, plate, 10, 30, 100, { opacity: 1 });
  const firstImage = drawing.created.find(node => node.name === 'image');
  beginActorFrame();
  drawPlate(drawing.world, drawing.element, plate, 50, 80, 80, { opacity: .4 });
  assert.equal(drawing.created.filter(node => node.name === 'image').length, 1);
  assert.equal(firstImage.getAttribute('height'), '80');
  assert.equal(firstImage.getAttribute('opacity'), '0.4');
});

test('mounted sprites crop through local SVG viewports and reuse their native image nodes', () => {
  const drawing = renderer();
  beginActorFrame();
  const mount = drawMount(drawing.world, drawing.element, { x: 300, y: 400, scale: .1, riderClass: 'knight', reduced: true });
  assert.equal(mount.getAttribute('pointer-events'), 'none', 'decorative horse pixels leave map-cell hit testing to the scene grid');
  const firstCount = drawing.created.filter(node => node.name === 'image').length;
  assert.ok(firstCount > 5);
  assert.equal(drawing.created.some(node => node.name === 'clipPath'), false);
  assert.ok(drawing.created.some(node => node.getAttribute('viewBox') === '84 112 872 887'));
  beginActorFrame();
  drawMount(drawing.world, drawing.element, { x: 310, y: 400, scale: .1, riderClass: 'knight', moving: true, time: .25 });
  assert.equal(drawing.created.filter(node => node.name === 'image').length, firstCount);
  assert.ok(drawing.created.some(node => node.getAttribute('transform') === 'translate(-436 0)'));
});
