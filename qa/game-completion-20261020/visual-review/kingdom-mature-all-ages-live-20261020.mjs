import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import { KINGDOM_AGES, kingdomPainting } from '../../../src/client/kingdom-view.js';

const root = process.cwd();
const base = path.join(root, 'qa/game-completion-20261020/visual-review');
const fixtures = path.join(base, 'kingdom-mature-fixtures');
const out = path.join(base, 'kingdom-mature-all-ages-live');
await fs.mkdir(out, { recursive: true });
const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
const captures = [];

for (let age = 0; age < KINGDOM_AGES.length; age++) {
  const context = await browser.newContext({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1 });
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', error => errors.push(String(error)));
  page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
  await page.goto('http://127.0.0.1:4179/', { waitUntil: 'networkidle' });
  await page.locator('#import-file').setInputFiles(path.join(fixtures, `kingdom-age${age}-mature.json`));
  await page.waitForFunction(expected => window.rebornSnapshot()?.age === expected, age);
  await page.locator('[data-choice="nav:kingdom"]').click();
  await page.waitForFunction(() => document.querySelector('#terrain')?.complete && document.querySelector('#terrain')?.naturalWidth > 0);
  await page.waitForTimeout(500);
  const runtime = await page.evaluate(() => {
    const image = document.querySelector('#terrain');
    const world = document.querySelector('#world');
    const state = window.rebornSnapshot();
    return {
      age: state.age,
      view: document.querySelector('#app')?.dataset.view,
      terrain: image?.getAttribute('src'),
      terrainSize: [image?.naturalWidth, image?.naturalHeight],
      viewport: [innerWidth, innerHeight],
      plotCount: world?.querySelectorAll('[data-plot]').length ?? null,
      plottedImages: world?.querySelectorAll('[data-plot] image').length ?? null,
      ownedPlots: state.plots.filter(plot => plot.type).length,
      walls: state.walls.level,
    };
  });
  assert.equal(runtime.age, age);
  assert.equal(runtime.view, 'kingdom');
  assert.equal(runtime.terrain, kingdomPainting({ age, walls: { level: 1 }, buildJobs: [] }).file);
  assert.equal(runtime.plotCount, 18);
  assert.equal(runtime.ownedPlots, 18);
  const screenshot = path.join(out, `kingdom-age${age}-mature-1280x720.png`);
  await page.screenshot({ path: screenshot });
  assert.deepEqual(errors, [], `age ${age} mature Kingdom preview has no browser errors`);
  captures.push({ age, ageName: KINGDOM_AGES[age], ...runtime, screenshot: path.relative(root, screenshot), errors });
  await context.close();
}

await browser.close();
const report = {
  recordedAt: new Date().toISOString(),
  classification: 'SYNTHETIC_MATURE_KINGDOM_VISUAL_REVIEW_NOT_EARNED_PROGRESSION_OR_ACCEPTANCE',
  fixtureNote: 'These fixtures occupy all 17 normal plots, the Town Hall and level-1 walls to inspect placement across ages. They do not establish earned progression, purchase legality, city balance, or natural journey completion.',
  captures,
};
await fs.writeFile(path.join(out, 'report.json'), JSON.stringify(report, null, 2));
console.log(JSON.stringify({ classification: report.classification, captures: captures.map(({ age, ageName, view, terrain, terrainSize, plotCount, plottedImages, ownedPlots, walls, errors }) => ({ age, ageName, view, terrain, terrainSize, plotCount, plottedImages, ownedPlots, walls, errors })) }, null, 2));
