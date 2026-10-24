import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import modeScenes from '../../../src/data/mode-scenes.json' with { type: 'json' };

const root = process.cwd();
const base = path.join(root, 'qa/game-completion-20261020/visual-review');
const fixtureDir = path.join(base, 'defense-all-sites-fixtures');
const out = path.join(base, 'defense-all-sites-live');
await fs.mkdir(out, { recursive: true });
const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
const ages = [];

for (let age = 0; age < 8; age++) {
  const context = await browser.newContext({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1 });
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', error => errors.push(String(error)));
  page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
  await page.goto('http://127.0.0.1:4179/', { waitUntil: 'networkidle' });
  await page.locator('#import-file').setInputFiles(path.join(fixtureDir, `defense-age${age}-all-sites.json`));
  await page.waitForFunction(expected => window.rebornSnapshot()?.age === expected, age);
  await page.locator('[data-choice="nav:war"]').click();
  await page.locator('[data-choice="start-siege"]').first().click();
  await page.waitForFunction(() => window.rebornSnapshot()?.defense?.status === 'ACTIVE');
  await page.waitForFunction(() => document.querySelector('#terrain')?.complete && document.querySelector('#terrain')?.naturalWidth > 0);
  const runtime = await page.evaluate(() => ({
    age: window.rebornSnapshot().age,
    terrain: document.querySelector('#terrain').getAttribute('src'),
    sites: window.rebornSnapshot().defense.towers.map(tower => ({ id: tower.siteId, x: tower.x, y: tower.y })),
    viewport: [innerWidth, innerHeight],
  }));
  assert.equal(runtime.age, age);
  assert.equal(runtime.terrain, modeScenes.defense[age]);
  assert.deepEqual(runtime.sites.map(site => site.id), ['D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8']);
  const screenshot = path.join(out, `defense-age${age}-all-sites-1280x720.png`);
  await page.screenshot({ path: screenshot });
  assert.deepEqual(errors, [], `age ${age} scene has no browser errors`);
  ages.push({ age, runtime, screenshot: path.relative(root, screenshot), errors });
  await context.close();
}

await browser.close();
const report = {
  recordedAt: new Date().toISOString(),
  classification: 'SYNTHETIC_EIGHT_TOWER_SITE_OCCUPANCY_VISUAL_REVIEW_NOT_NATURAL_GAMEPLAY_ACCEPTANCE',
  fixtureNote: 'The isolated fixtures duplicate tower families solely to occupy D1-D8 together and inspect their actual runtime positions. They are not valid purchase histories or balance evidence.',
  ages,
};
await fs.writeFile(path.join(out, 'report.json'), JSON.stringify(report, null, 2));
console.log(JSON.stringify({ classification: report.classification, ages: ages.map(({ age, runtime, errors }) => ({ age, sites: runtime.sites.length, terrain: runtime.terrain, errors })) }, null, 2));
