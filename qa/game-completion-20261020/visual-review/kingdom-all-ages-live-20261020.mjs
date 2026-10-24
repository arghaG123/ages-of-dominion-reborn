import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import { KINGDOM_AGES, kingdomPainting } from '../../../src/client/kingdom-view.js';

const root = process.cwd();
const base = path.join(root, 'qa/game-completion-20261020/visual-review');
const fixtures = path.join(base, 'defense-all-sites-fixtures');
const out = path.join(base, 'kingdom-all-ages-live');
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
  await page.locator('#import-file').setInputFiles(path.join(fixtures, `defense-age${age}-all-sites.json`));
  await page.waitForFunction(expected => window.rebornSnapshot()?.age === expected, age);
  await page.locator('[data-choice="nav:kingdom"]').click();
  await page.waitForFunction(() => document.querySelector('#terrain')?.complete && document.querySelector('#terrain')?.naturalWidth > 0);
  const runtime = await page.evaluate(() => {
    const image = document.querySelector('#terrain');
    const world = document.querySelector('#world');
    return {
      age: window.rebornSnapshot().age,
      view: document.querySelector('#app')?.dataset.view,
      terrain: image?.getAttribute('src'),
      size: [image?.naturalWidth, image?.naturalHeight],
      viewport: [innerWidth, innerHeight],
      plots: world?.querySelectorAll('[data-plot]').length ?? null,
      ownedPlots: window.rebornSnapshot().plots.filter(plot => plot.type).map(plot => ({ id: plot.id, type: plot.type, level: plot.level })),
    };
  });
  assert.equal(runtime.age, age);
  assert.equal(runtime.view, 'kingdom');
  assert.equal(runtime.terrain, kingdomPainting({ age, walls: { level: 0 }, buildJobs: [] }).file);
  const screenshot = path.join(out, `kingdom-age${age}-1280x720.png`);
  await page.screenshot({ path: screenshot });
  assert.deepEqual(errors, [], `age ${age} Kingdom view has no browser errors`);
  captures.push({ age, ageName: KINGDOM_AGES[age], ...runtime, screenshot: path.relative(root, screenshot), errors });
  await context.close();
}

await browser.close();
const report = {
  recordedAt: new Date().toISOString(),
  classification: 'SYNTHETIC_AGE_FIXTURE_VISUAL_REVIEW_NOT_NATURAL_PROGRESSION_OR_ACCEPTANCE',
  fixtureNote: 'The age fixtures isolate render coverage by age; they do not establish earned progression or campaign continuity.',
  captures,
};
await fs.writeFile(path.join(out, 'report.json'), JSON.stringify(report, null, 2));
console.log(JSON.stringify({ classification: report.classification, captures: captures.map(({ age, ageName, view, terrain, size, plots, ownedPlots, errors }) => ({ age, ageName, view, terrain, size, plots, ownedPlots, errors })) }, null, 2));
