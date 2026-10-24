import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';

const root = process.cwd();
const classId = process.argv[2] || 'healer';
const age = Number(process.argv[3] || 3);
const candidatePath = process.argv[4] || null;
const eras = ['ancient', 'ancient', 'ancient', 'medieval', 'powder', 'powder', 'mech', 'mech'];
assert.ok(Number.isInteger(age) && age >= 0 && age <= 7, 'age must be an integer from 0 to 7');
const era = eras[age];
const manifest = JSON.parse(await fs.readFile(root + '/src/data/hero-kit-eras-20261017.json', 'utf8'));
const body = manifest.classes?.[classId]?.[era];
assert.ok(body, `missing ${classId}/${era} body binding`);
const asset = await fs.readFile(root + '/' + body.file);
assert.equal(asset.length, body.bytes, 'bound body byte length matches');
assert.equal(crypto.createHash('sha256').update(asset).digest('hex'), body.sha256, 'bound body hash matches');
const candidate = candidatePath ? await fs.readFile(candidatePath) : null;

const out = `${root}/qa/game-completion-20261019/visual-review/hero-kits-live`;
await fs.mkdir(out, { recursive: true });
const prefix = `${classId}-${era}${candidate ? '-candidate' : ''}`;
const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
const context = await browser.newContext({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1 });
const page = await context.newPage();
const errors = [];
page.on('pageerror', error => errors.push(String(error)));
page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
if (candidate) {
  await page.route(`**/${body.file}`, route => route.fulfill({ status: 200, contentType: 'image/png', body: candidate }));
}
await page.goto('http://127.0.0.1:4179/', { waitUntil: 'networkidle' });
for (const choice of ['new-campaign', `scene-class:${classId}`, 'scene-enter-valley']) {
  const control = page.locator(`[data-choice="${choice}"]`).first();
  assert.equal(await control.count(), 1, `control exists: ${choice}`);
  await control.click();
}
const fixture = await page.evaluate(async ({ age, classId }) => {
  const data = await (await fetch('/src/data/reference-data.json')).json();
  const save = await import('/src/core/save.js');
  const storage = await import('/src/core/storage-adapter.js');
  const adapter = new storage.IndexedDBStorageAdapter(window.indexedDB, 'aod-reborn-db');
  let latest = await adapter.loadLive(data);
  if (latest.status !== 'VALID') throw new Error(`Fresh fixture save unavailable: ${latest.status}`);
  let state = latest.state;
  state.age = age;
  state.hero.class = classId;
  for (let attempt = 0; attempt < 4; attempt++) {
    state.revision = Math.max(state.revision, latest.state.revision) + 1;
    try {
      const head = await adapter.replace(latest.head, save.encode(state, data), data, 'hero-kit-fixture');
      return { id: state.id, epoch: head.epoch, revision: head.revision, age, classId };
    } catch (error) {
      if (!String(error?.message).includes('CAS head mismatch') || attempt === 3) throw error;
      latest = await adapter.loadLive(data);
      if (latest.status !== 'VALID' || latest.state.id !== state.id) throw new Error('Fixture campaign changed while writing');
      state = { ...latest.state, age, hero: { ...latest.state.hero, class: classId } };
    }
  }
  throw new Error('Fixture could not acquire the current campaign head');
}, { age, classId });
await page.reload({ waitUntil: 'networkidle' });
await page.waitForTimeout(250);
await page.locator('[data-choice="nav:hero"]').click();
await page.waitForTimeout(150);
const rendered = await page.evaluate(() => {
  const image = document.querySelector('#world [data-body]');
  return {
    age: window.rebornSnapshot()?.age,
    classId: window.rebornSnapshot()?.hero?.class,
    bodyId: image?.getAttribute('data-body') || null,
    bodyHref: image?.getAttribute('href') || null,
    bodyRect: image ? ['x', 'y', 'width', 'height'].map(key => image.getAttribute(key)) : null,
    kitMatch: document.querySelector('#world [data-presentation="standing-body"]')?.getAttribute('data-kit-match') || null,
  };
});
assert.equal(rendered.age, age);
assert.equal(rendered.classId, classId);
assert.equal(rendered.bodyId, body.id);
assert.equal(rendered.bodyHref, body.file);
assert.equal(rendered.kitMatch, '1');
await page.screenshot({ path: `${out}/${prefix}-1280x720.png` });
await page.setViewportSize({ width: 825, height: 375 });
await page.waitForTimeout(250);
const compactLayout = await page.evaluate(() => {
  const rect = selector => {
    const node = document.querySelector(selector);
    if (!node) return null;
    const box = node.getBoundingClientRect();
    return { left: box.left, top: box.top, right: box.right, bottom: box.bottom, width: box.width, height: box.height };
  };
  const intersects = (a, b) => Boolean(a && b && a.left < b.right && a.right > b.left && a.top < b.bottom && a.bottom > b.top);
  const summary = rect('#scene-ui.hero .copy');
  const body = rect('#world [data-body]');
  const dock = rect('#dock');
  const slots = [...document.querySelectorAll('#scene-ui.hero [data-hero-slot]')].map(node => {
    const box = node.getBoundingClientRect();
    return { left: box.left, top: box.top, right: box.right, bottom: box.bottom };
  });
  return {
    summary,
    body,
    dock,
    slots,
    summaryVisible: Boolean(summary && summary.width && getComputedStyle(document.querySelector('#scene-ui.hero .copy')).display !== 'none'),
    overlapsBody: intersects(summary, body),
    overlapsDock: intersects(summary, dock),
    overlapsSlot: slots.some(slot => intersects(summary, slot)),
    horizontalOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth,
    verticalOverflow: document.documentElement.scrollHeight > document.documentElement.clientHeight,
  };
});
assert.equal(compactLayout.summaryVisible, true, 'short-view hero summary remains visible');
assert.equal(compactLayout.overlapsBody, false, 'short-view hero summary stays clear of the standing figure');
assert.equal(compactLayout.overlapsDock, false, 'short-view hero summary stays above the action dock');
assert.equal(compactLayout.overlapsSlot, false, 'short-view hero summary stays clear of all six equipment sockets');
assert.equal(compactLayout.horizontalOverflow, false, 'short-view hero layout has no horizontal overflow');
assert.equal(compactLayout.verticalOverflow, false, 'short-view hero layout has no vertical overflow');
await page.screenshot({ path: `${out}/${prefix}-825x375.png` });
const report = {
  recordedAt: new Date().toISOString(),
  fixture,
  rendered,
  compactLayout,
  errors,
  asset: body.file,
  sha256: body.sha256,
  bytes: body.bytes,
  ...(candidate ? { candidate: { file: candidatePath, sha256: crypto.createHash('sha256').update(candidate).digest('hex'), bytes: candidate.length } } : {}),
};
assert.deepEqual(errors, [], 'console and page errors are empty');
await fs.writeFile(`${out}/${prefix}.json`, JSON.stringify(report, null, 2));
console.log(JSON.stringify(report, null, 2));
await context.close();
await browser.close();
