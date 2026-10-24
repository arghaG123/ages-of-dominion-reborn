import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';

const root = process.cwd();
const out = path.join(root, 'qa/game-completion-20261019/visual-review/kingdom-ages-live-20261020');
await fs.mkdir(out, { recursive: true });
const ages = ['Stone', 'Bronze', 'Iron', 'Medieval', 'Gunpowder', 'Industrial', 'Modern', 'Future'];
const sizes = [
  { name: '1280x720', width: 1280, height: 720 },
  { name: '825x375', width: 825, height: 375 },
];
const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
const report = { recordedAt: new Date().toISOString(), fixtureKind: 'isolated valid persisted age and Hall-level state', captures: [], errors: [] };

for (const size of sizes) for (let age = 0; age < ages.length; age++) {
  const context = await browser.newContext({ viewport: { width: size.width, height: size.height }, deviceScaleFactor: 1 });
  const page = await context.newPage();
  page.on('pageerror', error => report.errors.push({ viewport: size.name, age: ages[age], error: String(error) }));
  page.on('console', message => { if (message.type() === 'error') report.errors.push({ viewport: size.name, age: ages[age], error: message.text() }); });
  await page.goto('http://127.0.0.1:4179/', { waitUntil: 'networkidle' });
  for (const choice of ['new-campaign', 'scene-class:knight', 'scene-enter-valley']) await page.locator(`[data-choice="${choice}"]`).click();
  await page.evaluate(async () => {
    const stored = await window.rebornBackground(true);
    if (!stored) throw new Error('Could not durably suspend the fixture campaign before replacing its age');
  });
  const written = await page.evaluate(async ageIndex => {
    const state = window.rebornSnapshot();
    const data = await (await fetch('/src/data/reference-data.json')).json();
    const save = await import('/src/core/save.js');
    const storage = await import('/src/core/storage-adapter.js');
    state.age = ageIndex;
    state.plots.find(plot => plot.id === 'townhall').level = ageIndex + 2;
    state.resources = { food: 100000, wood: 100000, stone: 100000, gold: 100000 };
    state.walls.level = 2;
    state.revision++;
    const adapter = new storage.IndexedDBStorageAdapter(window.indexedDB, 'aod-reborn-db');
    const before = await adapter.loadLive(data);
    if (before.status !== 'VALID') throw new Error(`Fixture source save is ${before.status}`);
    const head = await adapter.replace(before.head, save.encode(state, data), data, 'kingdom');
    return { id: state.id, age: state.age, townHallLevel: state.plots.find(plot => plot.id === 'townhall').level, wallLevel: state.walls.level, revision: head.revision };
  }, age);
  await page.reload({ waitUntil: 'networkidle' });
  const view = await page.locator('#app').getAttribute('data-view');
  if (view !== 'kingdom') await page.locator('[data-choice="nav:kingdom"]').click();
  await page.waitForFunction(() => {
    const terrain = document.querySelector('#terrain');
    return document.querySelector('#app')?.dataset.view === 'kingdom' && terrain?.complete && terrain.naturalWidth > 0;
  });
  await page.waitForTimeout(180);
  const rendered = await page.evaluate(() => ({
    view: document.querySelector('#app')?.dataset.view,
    age: window.rebornSnapshot()?.age,
    hallLevel: window.rebornSnapshot()?.plots?.find(plot => plot.id === 'townhall')?.level,
    wallLevel: window.rebornSnapshot()?.walls?.level,
    terrain: document.querySelector('#terrain')?.getAttribute('src'),
    terrainLoaded: document.querySelector('#terrain')?.naturalWidth > 0,
    wallPhase: document.querySelector('#terrain')?.dataset.wallPhase,
    registration: document.querySelector('#world')?.getAttribute('data-registration'),
    hallLayer: (() => {
      const image = document.querySelector('#world image[aria-label="Town Hall"]');
      if (!image) return null;
      const rect = image.getBoundingClientRect();
      return { source: image.getAttribute('href'), world: ['x', 'y', 'width', 'height'].map(key => Number(image.getAttribute(key))), screen: [rect.x, rect.y, rect.width, rect.height] };
    })(),
    bodyOverflow: [document.body.scrollWidth, document.body.scrollHeight],
  }));
  assert.equal(rendered.view, 'kingdom');
  assert.equal(rendered.age, age);
  assert.equal(rendered.hallLevel, age + 2);
  assert.equal(rendered.wallLevel, 2);
  assert.equal(rendered.wallPhase, 'tall');
  assert.equal(rendered.terrainLoaded, true);
  assert.ok(rendered.hallLayer, `${ages[age]} has a live Town Hall layer`);
  assert.ok(rendered.hallLayer.screen[1] >= (age === 0 ? -1 : 12), `${ages[age]} Town Hall stays in-frame`);
  const file = path.join(out, `kingdom-${String(age).padStart(2, '0')}-${ages[age].toLowerCase()}-${size.name}.png`);
  await page.screenshot({ path: file });
  report.captures.push({ viewport: size.name, age: ages[age], fixture: written, rendered, file: path.relative(root, file) });
  await context.close();
}

await browser.close();
await fs.writeFile(path.join(out, 'kingdom-live-age-review.json'), JSON.stringify(report, null, 2));
assert.deepEqual(report.errors, []);
console.log(JSON.stringify({ captures: report.captures.length, errors: report.errors, report: path.relative(root, path.join(out, 'kingdom-live-age-review.json')) }, null, 2));
