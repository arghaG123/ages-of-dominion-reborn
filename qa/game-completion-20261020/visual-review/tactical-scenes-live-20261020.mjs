import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import modeScenes from '../../../src/data/mode-scenes.json' with { type: 'json' };

const root = process.cwd();
const age = Number(process.argv[2] || 4);
const sizeName = process.argv[3] || '825x375';
const sizes = {
  '825x375': { width: 825, height: 375 },
  '933x424': { width: 933, height: 424 },
  '1280x720': { width: 1280, height: 720 },
};
assert.ok(sizes[sizeName], `supported viewport ${sizeName}`);
const out = path.join(root, 'qa/game-completion-20261020/visual-review/tactical-scenes-live');
await fs.mkdir(out, { recursive: true });
const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
const context = await browser.newContext({ viewport: sizes[sizeName], deviceScaleFactor: 1 });
const page = await context.newPage();
const errors = [];
page.on('pageerror', error => errors.push(String(error)));
page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
await page.goto('http://127.0.0.1:4179/', { waitUntil: 'networkidle' });
await page.locator('#import-file').setInputFiles(path.join(root, `qa/game-completion-20261020/visual-review/tactical-age${age}-visual-fixture.json`));
await page.waitForFunction(expectedAge => window.rebornSnapshot()?.age === expectedAge, age);
await page.locator('[data-choice="nav:war"]').click();
await page.locator('[data-choice="start-skirmish"]').click();
await page.waitForFunction(() => window.rebornSnapshot()?.battle?.status === 'ACTIVE');
await page.waitForFunction(() => document.querySelector('#terrain')?.complete && document.querySelector('#terrain')?.naturalWidth > 0);
await page.waitForTimeout(180);
const runtime = await page.evaluate(() => {
  const terrain = document.querySelector('#terrain');
  const world = document.querySelector('#world');
  const rect = world.getBoundingClientRect();
  const image = terrain.getBoundingClientRect();
  return {
    age: window.rebornSnapshot().age,
    battle: window.rebornSnapshot().battle.status,
    source: terrain.getAttribute('src'),
    imageLoaded: terrain.complete && terrain.naturalWidth > 0,
    naturalSize: [terrain.naturalWidth, terrain.naturalHeight],
    board: world.getAttribute('data-board'),
    viewport: [innerWidth, innerHeight],
    worldRect: [rect.x, rect.y, rect.width, rect.height].map(Math.round),
    terrainRect: [image.x, image.y, image.width, image.height].map(Math.round),
    cellCount: world.querySelectorAll('[data-cell]').length,
    visibleCellCount: [...world.querySelectorAll('[data-cell]')].filter(node => {
      const box = node.getBoundingClientRect();
      return box.width > 1 && box.height > 1 && box.right > 0 && box.bottom > 0 && box.left < innerWidth && box.top < innerHeight;
    }).length,
  };
});
assert.equal(runtime.age, age);
assert.equal(runtime.battle, 'ACTIVE');
assert.equal(runtime.source, modeScenes.tactical[age]);
assert.equal(runtime.imageLoaded, true);
assert.equal(runtime.board, 'tactical-painted-v1');
assert.ok(runtime.cellCount >= 70);
assert.deepEqual(errors, []);
const screenshot = path.join(out, `tactical-age${age}-${sizeName}.png`);
await page.screenshot({ path: screenshot });
const report = {
  recordedAt: new Date().toISOString(),
  classification: `ISOLATED_VALID_AGE${age}_VISUAL_FIXTURE_NOT_NATURAL_GAMEPLAY_ACCEPTANCE`,
  journey: `load valid visual-only age${age} campaign fixture -> War -> Skirmish -> inspect tactical scene`,
  runtime,
  screenshot: path.relative(root, screenshot),
  errors,
};
await fs.writeFile(path.join(out, `tactical-age${age}-${sizeName}.json`), JSON.stringify(report, null, 2));
console.log(JSON.stringify(report, null, 2));
await context.close();
await browser.close();
