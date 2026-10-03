import test from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFileSync, readdirSync, existsSync } from 'node:fs';
import { project, inverse } from '../src/client/projection.js';
import scene from '../src/data/stone-scene.json' with { type: 'json' };

const root = new URL('../', import.meta.url);
const read = name => JSON.parse(readFileSync(new URL(name, root), 'utf8'));
const candidate = read('qa/recovery-executor-20261003/kingdom-layout-candidate.json');
const contract = read('docs/plan/IMPLEMENTATION-CONTRACT.json');
const cam = candidate.camera;

function hit(rect, point) {
  const [x, y, w, h] = rect;
  return point[0] >= x && point[0] <= x + w && point[1] >= y && point[1] <= y + h;
}
function inside(point, poly) {
  let [x, y] = point, on = false;
  for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
    const [xi, yi] = poly[i], [xj, yj] = poly[j];
    if ((yi > y) !== (yj > y) && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi) on = !on;
  }
  return on;
}

test('candidate is reviewable and leaves the active contract alone', () => {
  const bytes = readFileSync(new URL('docs/plan/IMPLEMENTATION-CONTRACT.json', root));
  assert.equal(createHash('sha256').update(bytes).digest('hex'), candidate.activeContractSHA256);
  assert.equal(candidate.activeContractEdited, false);
  assert.equal(candidate.status, 'READY_FOR_REVIEW');
  assert.equal(candidate.ownerAcceptance, 'NOT_OWNER_ACCEPTED');
  assert.equal(candidate.rejectedTranslationApplied, false);
  assert.deepEqual(scene.hall.matrix[0][0], 0.1312);
  assert.notEqual(candidate.hall.matrix[0][0], 0.1312);
  assert.equal(candidate.hall.matrix[0][0], candidate.hall.matrix[1][1]);
  assert.equal(candidate.hall.matrix[0][1], 0);
  assert.equal(candidate.hall.matrix[1][0], 0);
  assert.ok(!String(candidate.scaleRule).includes('authoritative'));
  const shifted = scene.hall.matrix[1][2] + 193;
  assert.ok(Math.abs(candidate.hall.matrix[1][2] - shifted) > 20);
});

test('Hall envelope stays in frame and the entrance cobble meets the terrace front', () => {
  const [sx, , tx] = candidate.hall.matrix[0];
  const ty = candidate.hall.matrix[1][2];
  const roofY = ty + sx * 21;
  const dirtY = ty + sx * 999;
  assert.ok(roofY >= 24 && roofY <= 64, roofY);
  assert.ok(dirtY <= 744, dirtY);
  const [ix, iy] = candidate.hall.anchorImage;
  const landed = [tx + sx * ix, ty + sx * iy];
  const hall = candidate.geometry.sites.find(site => site.id === 'townhall');
  const [x, y, w, h] = hall.rect;
  const front = project(cam, [x + w / 2, y + h]);
  assert.ok(Math.abs(front[0] - landed[0]) < 1.5);
  assert.ok(Math.abs(front[1] - landed[1]) < 1.5);
  const back = inverse(cam, landed);
  assert.ok(hit(hall.rect, [back[0], y + h - 0.01]));
});

test('eighteen sites stay apart, off the Hall sprite, and pickable beside the open panel', () => {
  const sites = candidate.geometry.sites;
  assert.equal(sites.length, 18);
  assert.equal(sites.filter(site => site.id.startsWith('P')).length, 17);
  assert.equal(sites.filter(site => site.region === 'upper').length, 9);
  assert.equal(sites.filter(site => site.region === 'lower').length, 8);
  const [left, top, right, bottom] = candidate.hall.spriteSourceRect;
  const sprite = [[left, top], [right, top], [right, bottom], [left, bottom]];
  for (const site of sites) {
    const [x, y, w, h] = site.rect;
    assert.ok(x >= 0 && y >= 0 && x + w <= 14 && y + h <= 11);
    for (const other of sites) {
      if (other === site) continue;
      const [ox, oy, ow, oh] = other.rect;
      assert.ok(Math.max(x, ox) >= Math.min(x + w, ox + ow) || Math.max(y, oy) >= Math.min(y + h, oy + oh));
    }
    if (site.id === 'townhall') continue;
    for (let i = 0; i < 5; i++) for (let j = 0; j < 5; j++) {
      assert.equal(inside(project(cam, [x + w * i / 4, y + h * j / 4]), sprite), false, site.id);
    }
  }
  const tight = candidate.viewportSafe.find(item => item.viewport[0] === 1180);
  for (const site of sites) {
    const [x, y, w, h] = site.rect;
    const centre = project(cam, [x + w / 2, y + h / 2]);
    assert.ok(centre[0] < tight.panelLeftSourceX - 8, site.id);
  }
});

test('roads stay off the seventeen plots and the guide is a 1376x768 review file', () => {
  const pads = candidate.geometry.sites.filter(site => site.id.startsWith('P')).map(site => {
    const [x, y, w, h] = site.rect;
    return [[x, y], [x + w, y], [x + w, y + h], [x, y + h]].map(point => project(cam, point));
  });
  for (const road of candidate.geometry.roads) {
    const line = road.map(point => project(cam, point));
    for (let i = 1; i < line.length; i++) {
      const [x0, y0] = line[i - 1], [x1, y1] = line[i];
      const length = Math.hypot(x1 - x0, y1 - y0);
      const nx = -(y1 - y0) / length, ny = (x1 - x0) / length;
      for (let t = 0; t <= length; t += 6) {
        const x = x0 + ((x1 - x0) * t) / length, y = y0 + ((y1 - y0) * t) / length;
        for (const side of [-8, 8]) {
          const point = [x + nx * side, y + ny * side];
          assert.equal(pads.some(poly => inside(point, poly)), false);
        }
      }
    }
  }
  const guide = readFileSync(new URL(candidate.guide.file, root));
  assert.equal(createHash('sha256').update(guide).digest('hex'), candidate.guide.sha256);
  assert.equal(guide.readUInt32BE(16), 1376);
  assert.equal(guide.readUInt32BE(20), 768);
  assert.equal(candidate.guide.status, 'READY_FOR_REVIEW');
  assert.equal(candidate.guide.ownerAcceptance, 'NOT_OWNER_ACCEPTED');
  assert.equal(contract.geometry.kingdom.sites[0].rect[2], 3);
});

test('collection discovery follows the files on disk', () => {
  const rows = [];
  for (const batch of readdirSync(new URL('assets/production', root))) {
    const report = new URL(`assets/production/${batch}/collection-report.json`, root);
    if (!existsSync(report)) continue;
    for (const output of read(report).outputs) rows.push(batch + ':' + output.id + ':' + output.sha256);
  }
  const snapshot = read('qa/recovery-executor-20261003/collection-snapshot.json');
  assert.ok(rows.length >= snapshot.rows.length);
  assert.equal(new Set(rows).size, rows.length);
  assert.ok(rows.some(row => row.startsWith('production-13-20261003:')));
});
