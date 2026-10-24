import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import fs from 'node:fs/promises';
import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';

const root = process.cwd();
const origin = 'http://127.0.0.1:4179';
const manifestPath = `${root}/src/data/hero-kit-eras-20261017.json`;
const manifest = JSON.parse(await fs.readFile(manifestPath, 'utf8'));
const eras = ['ancient', 'medieval', 'powder', 'mech'];
const rows = [];
for (const [classId, kits] of Object.entries(manifest.classes)) {
  for (const era of eras) {
    const body = kits[era];
    assert.ok(body?.file, `missing ${classId}/${era}`);
    const bytes = await fs.readFile(`${root}/${body.file}`);
    const sha256 = crypto.createHash('sha256').update(bytes).digest('hex');
    assert.equal(bytes.length, body.bytes, `${classId}/${era} byte length`);
    assert.equal(sha256, body.sha256, `${classId}/${era} SHA-256`);
    assert.equal(bytes.readUInt32BE(16), body.width, `${classId}/${era} width`);
    assert.equal(bytes.readUInt32BE(20), body.height, `${classId}/${era} height`);
    assert.equal(bytes[25], 6, `${classId}/${era} RGBA alpha`);
    rows.push({ classId, era, id: body.id, file: body.file, sha256, bytes: bytes.length, width: body.width, height: body.height, depictedKitEvidence: body.depictedKitEvidence });
  }
}
assert.equal(rows.length, 32, 'all eight classes and four eras are represented');

const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 2256 }, deviceScaleFactor: 1 });
const errors = [];
page.on('pageerror', error => errors.push(String(error)));
page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
await page.goto(origin, { waitUntil: 'networkidle' });
const cards = rows.map(row => `
  <figure>
    <figcaption><b>${row.classId}</b><span>${row.era}</span></figcaption>
    <img src="${origin}/${row.file}" alt="${row.classId}, ${row.era} kit">
    <small>${row.width} × ${row.height} · ${row.id}</small>
  </figure>`).join('');
await page.setContent(`<!doctype html><html><head><meta charset="utf-8"><style>
  *{box-sizing:border-box}html,body{margin:0;width:1440px;height:2256px;background:#11171b;color:#ede2c9;font:14px/1.2 "Segoe UI",sans-serif}
  main{width:1440px;height:2256px;padding:8px;display:grid;grid-template-columns:repeat(4,minmax(0,1fr));grid-template-rows:repeat(8,minmax(0,1fr));gap:6px;min-height:0}
  figure{margin:0;min-width:0;min-height:0;overflow:hidden;display:grid;grid-template-rows:24px minmax(0,1fr) 16px;gap:2px;padding:5px;border:1px solid #a08a60;background:linear-gradient(155deg,#172126,#0d1316)}
  figcaption{display:flex;justify-content:space-between;align-items:center;text-transform:uppercase;letter-spacing:.05em;color:#f1d793}
  figcaption span{color:#d8d0bd;font-size:12px}
  img{display:block;width:100%;height:100%;min-width:0;min-height:0;max-height:100%;object-fit:contain;background-color:#394247;background-image:linear-gradient(45deg,#596268 25%,transparent 25%),linear-gradient(-45deg,#596268 25%,transparent 25%),linear-gradient(45deg,transparent 75%,#596268 75%),linear-gradient(-45deg,transparent 75%,#596268 75%);background-size:24px 24px;background-position:0 0,0 12px,12px -12px,-12px 0}
  small{overflow:hidden;color:#b6b8b1;font-size:10px;white-space:nowrap;text-overflow:ellipsis}
</style></head><body><main>${cards}</main></body></html>`, { waitUntil: 'load' });
await page.waitForFunction(() => [...document.images].length === 32 && [...document.images].every(image => image.complete && image.naturalWidth > 0));
const layout = await page.evaluate(() => {
  const box = node => { const r = node.getBoundingClientRect(); return [r.x, r.y, r.width, r.height]; };
  return {
    document: [document.documentElement.scrollWidth, document.documentElement.scrollHeight],
    main: box(document.querySelector('main')),
    firstCard: box(document.querySelector('figure')),
    lastCard: box(document.querySelector('figure:last-child')),
    firstImage: box(document.querySelector('figure img')),
    lastImage: box(document.querySelector('figure:last-child img')),
  };
});
await page.screenshot({ path: `${root}/qa/game-completion-20261019/visual-review/hero-body-matrix-live-20261020-current.png` });
const report = { recordedAt: new Date().toISOString(), viewport: [1440, 2256], count: rows.length, errors, layout, rows };
assert.deepEqual(errors, [], 'matrix browser has no errors');
await fs.writeFile(`${root}/qa/game-completion-20261019/visual-review/hero-body-matrix-live-20261020-current.json`, JSON.stringify(report, null, 2));
console.log(JSON.stringify({ recordedAt: report.recordedAt, viewport: report.viewport, count: report.count, errors: report.errors, layout, output: 'hero-body-matrix-live-20261020-current.png' }, null, 2));
await browser.close();
