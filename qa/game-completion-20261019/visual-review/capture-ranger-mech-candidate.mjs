import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';

const root = process.cwd();
const out = root + '/qa/game-completion-20261019/visual-review';
const candidatePath = root + '/assets/derivatives/mock-led-20261016/bodies/eras/class-ranger-mech-v2.png';
const candidate = await fs.readFile(candidatePath);
const manifest = JSON.parse(await fs.readFile(root + '/src/data/hero-kit-eras-20261017.json', 'utf8'));
const body = manifest.classes.ranger.mech;
const candidateSha256 = crypto.createHash('sha256').update(candidate).digest('hex');
assert.equal(candidate.length, body.bytes);
assert.equal(candidateSha256, body.sha256);

const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
const context = await browser.newContext({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1 });
const page = await context.newPage();
const errors = [];
page.on('pageerror', error => errors.push(String(error)));
page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
await page.goto('http://127.0.0.1:4179/', { waitUntil: 'networkidle' });
for (const choice of ['new-campaign', 'scene-class:ranger', 'scene-enter-valley']) {
  const button = page.locator('[data-choice="' + choice + '"]').first();
  assert.equal(await button.count(), 1, 'control exists: ' + choice);
  await button.click();
}
const setup = await page.evaluate(async () => {
  const state = window.rebornSnapshot();
  const data = await (await fetch('/src/data/reference-data.json')).json();
  const save = await import('/src/core/save.js');
  const storage = await import('/src/core/storage-adapter.js');
  state.age = 6;
  state.hero.class = 'ranger';
  state.plots.find(plot => plot.id === 'townhall').level = 8;
  state.resources = { food: 100000, wood: 100000, stone: 100000, gold: 100000 };
  state.revision++;
  const adapter = new storage.IndexedDBStorageAdapter(window.indexedDB, 'aod-reborn-db');
  const before = await adapter.loadLive(data);
  if (before.status !== 'VALID') throw new Error('Fresh fixture save unavailable: ' + before.status);
  const head = await adapter.replace(before.head, save.encode(state, data), data, 'hero');
  return { id: state.id, epoch: head.epoch, revision: head.revision, age: state.age, classId: state.hero.class };
});
await page.reload({ waitUntil: 'networkidle' });
await page.waitForTimeout(250);
await page.locator('[data-choice="nav:hero"]').click();
await page.waitForTimeout(150);
const rendered = await page.evaluate(() => ({
  age: window.rebornSnapshot()?.age,
  classId: window.rebornSnapshot()?.hero?.class,
  bodyId: document.querySelector('#world [data-body]')?.getAttribute('data-body'),
  bodyHref: document.querySelector('#world [data-body]')?.getAttribute('href'),
  bodyRect: (() => {
    const image = document.querySelector('#world [data-body]');
    return image ? ['x', 'y', 'width', 'height'].map(key => image.getAttribute(key)) : null;
  })(),
}));
assert.equal(rendered.age, 6);
assert.equal(rendered.classId, 'ranger');
assert.equal(rendered.bodyId, 'class-ranger-mech-v2');
assert.equal(rendered.bodyHref, body.file);
await page.screenshot({ path: out + '/ranger-mech-live-1280x720.png' });
await page.setViewportSize({ width: 825, height: 375 });
await page.waitForTimeout(250);
await page.screenshot({ path: out + '/ranger-mech-live-825x375.png' });
const report = { recordedAt: new Date().toISOString(), fixture: setup, rendered, errors, asset: body.file, sha256: body.sha256, bytes: body.bytes };
await fs.writeFile(out + '/ranger-mech-live.json', JSON.stringify(report, null, 2));
console.log(JSON.stringify(report, null, 2));
await context.close();
await browser.close();
