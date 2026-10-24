import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
import { KINGDOM_AGES, kingdomPainting } from '../../../src/client/kingdom-view.js';

const root = process.cwd();
const output = `${root}/qa/game-completion-20261019/visual-review/kingdom-wall-matrix.png`;
const rows = [];
for (let age = 0; age < KINGDOM_AGES.length; age += 1) {
  const states = [
    ['Open ground', { age, walls: { level: 0 }, buildJobs: [] }],
    ['Scaffold', { age, walls: { level: 0 }, buildJobs: [{ plotId: 'walls' }] }],
    ['Built', { age, walls: { level: 1 }, buildJobs: [] }],
    ['Taller', { age, walls: { level: 2 }, buildJobs: [] }],
  ];
  for (const [label, state] of states) rows.push({ age, ageName: KINGDOM_AGES[age], label, ...kingdomPainting(state) });
}
const cells = rows.map(item => `<article><b>${item.ageName} · ${item.label}</b><small>${item.wallKind}</small><img src="http://127.0.0.1:4179/${item.file}" /></article>`).join('');
const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
const page = await browser.newPage({ viewport: { width: 1600, height: 1900 }, deviceScaleFactor: 1 });
await page.setContent(`<html><head><style>*{box-sizing:border-box}body{margin:0;padding:10px;background:#12181b;color:#f3e9d3;font:13px Segoe UI,sans-serif}.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}article{height:225px;overflow:hidden;position:relative;border:1px solid #ad9462;background:#1e282c}b,small{display:block;padding:2px 6px}small{position:absolute;right:0;top:0;background:#111c;color:#d9c79e}img{display:block;width:100%;height:194px;object-fit:cover}</style></head><body><div class="grid">${cells}</div></body></html>`, { waitUntil: 'networkidle' });
await page.waitForFunction(() => [...document.images].every(image => image.complete && image.naturalWidth > 0));
const imageReport = await page.locator('article img').evaluateAll(images => images.map(image => ({ file: image.getAttribute('src').replace('http://127.0.0.1:4179/', ''), width: image.naturalWidth, height: image.naturalHeight })));
await page.screenshot({ path: output });
await fs.writeFile(output.replace('.png', '.json'), JSON.stringify({ recordedAt: new Date().toISOString(), count: rows.length, rows: rows.map(({ age, ageName, label, phase, file, wallKind }) => ({ age, ageName, label, phase, file, wallKind })), imageReport }, null, 2));
console.log(JSON.stringify({ output: output.slice(root.length + 1), count: rows.length, missing: imageReport.filter(image => image.width === 0).length }, null, 2));
await browser.close();
