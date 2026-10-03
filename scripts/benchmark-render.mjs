import fs from 'node:fs';
import contract from '../src/data/implementation-contract.json' with { type: 'json' };
import { project, camera } from '../src/client/projection.js';
import { adventureMap, isOpen, stepCost } from '../src/core/navigation.js';

const failures = [];
const check = (name, ok, detail) => { if (!ok) failures.push({ name, detail }); };
const inside = (g, point) => {
  const [x, y] = project(g.worldToSource, point);
  return x >= 0 && y >= 0 && x <= g.sourceSize[0] && y <= g.sourceSize[1];
};
for (const [mode, g] of Object.entries(contract.geometry)) {
  for (const site of g.sites ?? []) {
    const [x, y, w, h] = site.rect;
    for (const point of [[x, y], [x + w, y], [x + w, y + h], [x, y + h]]) check(`${mode}:${site.id}`, inside(g, point), point);
  }
  for (const [w, h] of contract.viewports) {
    const fit = camera(g.sourceSize, w, h);
    check(`${mode} fit ${w}x${h}`, fit.scale > 0 && fit.offset[0] >= -1e-9 && fit.offset[1] >= -1e-9, fit);
  }
}
const map = adventureMap(contract.geometry.adventure);
check('bridge deck open', isOpen(map, 4, 6) && isOpen(map, 5, 6), null);
check('river blocked beside bridge', !isOpen(map, 4, 5), null);
check('road step', stepCost(map, [8, 8], [8, 7]) === 1, null);
const kingdom = contract.geometry.kingdom;
const lines = kingdom.roads.map(road => road.map(point => project(kingdom.worldToSource, point).map(n => n.toFixed(1)).join(',')).join(' '));
const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1376 768"><rect width="1376" height="768" fill="#1c2824"/>${lines.map(points => `<polyline points="${points}" fill="none" stroke="#b7a48a" stroke-width="8"/>`).join('')}${kingdom.sites.map(site => {
  const [x, y, w, h] = site.rect;
  const points = [[x, y], [x + w, y], [x + w, y + h], [x, y + h]].map(point => project(kingdom.worldToSource, point).map(n => n.toFixed(1)).join(',')).join(' ');
  return `<polygon points="${points}" fill="none" stroke="#d7c08a" stroke-width="2"/>`;
}).join('')}</svg>`;
fs.mkdirSync('qa/benchmark', { recursive: true });
fs.writeFileSync('qa/benchmark/kingdom-registration.svg', svg);
const report = { checkedAt: new Date().toISOString(), failures, status: failures.length ? 'FAIL' : 'PASS', note: 'Registration geometry only. This is not a visual acceptance of production art.' };
fs.writeFileSync('qa/benchmark/render-check.json', JSON.stringify(report, null, 2) + '\n');
if (failures.length) { console.error(report); process.exit(1); }
console.log('Scoped registration render check PASS');
