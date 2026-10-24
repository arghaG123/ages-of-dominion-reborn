import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import modeScenes from '../../../src/data/mode-scenes.json' with { type: 'json' };
import { checksum } from '../../../src/core/save.js';

const root = process.cwd();
const out = path.join(root, 'qa/game-completion-20261020/visual-review/tactical-all-ages-hud-live');
await fs.mkdir(out, { recursive: true });
const sizes = [
  { width: 825, height: 375 },
  { width: 933, height: 424 },
  { width: 1280, height: 720 },
];
const reference = JSON.parse(await fs.readFile(path.join(root, 'qa/game-completion-20261020/visual-review/tactical-age6-visual-fixture.json'), 'utf8'));
const base = JSON.parse(reference.payload);
const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
const runs = [];

function fixture(age) {
  const state = structuredClone(base);
  state.id = `tactical-age-${age}-visual-review`;
  state.age = age;
  const payload = JSON.stringify(state);
  return JSON.stringify({ schema: 1, payload, checksum: checksum(payload) });
}

async function inspect(page) {
  return page.evaluate(() => {
    const box = node => {
      if (!node) return null;
      const r = node.getBoundingClientRect();
      return { x: Math.round(r.x), y: Math.round(r.y), width: Math.round(r.width), height: Math.round(r.height), right: Math.round(r.right), bottom: Math.round(r.bottom) };
    };
    const visible = node => {
      const style = getComputedStyle(node);
      const r = node.getBoundingClientRect();
      return style.display !== 'none' && style.visibility !== 'hidden' && Number(style.opacity) > 0 && r.width > 0 && r.height > 0;
    };
    const terrain = document.querySelector('#terrain');
    const world = document.querySelector('#world');
    const dock = document.querySelector('#dock');
    const status = document.querySelector('#scene-ui.game-status.battle');
    const controls = [...document.querySelectorAll('#dock button, #scene-ui button')].filter(visible).map(node => {
      const r = node.getBoundingClientRect();
      const target = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2);
      return {
        choice: node.dataset.choice || node.getAttribute('aria-label') || node.textContent.trim(),
        within: r.left >= 0 && r.top >= 0 && r.right <= innerWidth && r.bottom <= innerHeight,
        centerReceivesInput: Boolean(target && (target === node || node.contains(target))),
      };
    });
    const terrainBox = box(terrain);
    const statusBox = box(status);
    const dockBox = box(dock);
    return {
      age: window.rebornSnapshot()?.age,
      view: document.querySelector('#app')?.dataset.view,
      battle: window.rebornSnapshot()?.battle?.status,
      terrainSource: terrain?.getAttribute('src'),
      terrainLoaded: Boolean(terrain?.complete && terrain.naturalWidth > 0),
      terrainSize: terrain ? [terrain.naturalWidth, terrain.naturalHeight] : null,
      board: world?.getAttribute('data-board'),
      registration: world?.getAttribute('data-registration'),
      viewport: [innerWidth, innerHeight],
      world: box(world),
      terrain: terrainBox,
      cellCount: world?.querySelectorAll('[data-cell]').length ?? 0,
      visibleCellCount: [...(world?.querySelectorAll('[data-cell]') ?? [])].filter(node => {
        const r = node.getBoundingClientRect();
        return r.width > 1 && r.height > 1 && r.right > 0 && r.bottom > 0 && r.left < innerWidth && r.top < innerHeight;
      }).length,
      panelOpen: document.querySelector('#panel')?.classList.contains('open') ?? false,
      status: statusBox,
      dock: dockBox,
      statusBeforeDock: Boolean(statusBox && dockBox && statusBox.right + 8 < dockBox.x),
      visibleControls: controls,
      documentWidth: document.documentElement.scrollWidth,
      documentHeight: document.documentElement.scrollHeight,
    };
  });
}

try {
  for (let age = 0; age < 8; age++) {
    for (const size of sizes) {
      const context = await browser.newContext({ viewport: size, deviceScaleFactor: 1 });
      const page = await context.newPage();
      const errors = [];
      const failedResponses = [];
      page.on('pageerror', error => errors.push(String(error)));
      page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
      page.on('response', response => { if (response.status() >= 400) failedResponses.push({ status: response.status(), url: response.url() }); });
      await page.route('**/favicon.ico', route => route.fulfill({ status: 204, body: '' }));
      await page.goto('http://127.0.0.1:4179/', { waitUntil: 'networkidle' });
      await page.locator('#import-file').setInputFiles({
        name: `age-${age}-tactical-visual.json`,
        mimeType: 'application/json',
        buffer: Buffer.from(fixture(age)),
      });
      await page.waitForFunction(expected => window.rebornSnapshot()?.age === expected, age);
      await page.locator('[data-choice="nav:war"]').click();
      await page.locator('[data-choice="start-skirmish"]').click();
      await page.waitForFunction(() => window.rebornSnapshot()?.battle?.status === 'ACTIVE' && document.querySelector('#app')?.dataset.view === 'tactical');
      await page.waitForFunction(() => document.querySelector('#terrain')?.complete && document.querySelector('#terrain')?.naturalWidth > 0);
      const runtime = await inspect(page);
      assert.equal(runtime.age, age);
      assert.equal(runtime.battle, 'ACTIVE');
      assert.equal(runtime.terrainSource, modeScenes.tactical[age]);
      assert.equal(runtime.terrainLoaded, true);
      assert.equal(runtime.board, 'tactical-painted-v1');
      assert.equal(runtime.cellCount, 70);
      assert.equal(runtime.panelOpen, false);
      assert.equal(runtime.statusBeforeDock, true, `age ${age} ${size.width} status does not overlap the action dock`);
      assert.equal(runtime.visibleControls.filter(control => !control.within || !control.centerReceivesInput).length, 0, `age ${age} ${size.width} tactical controls fit and receive input`);
      assert.equal(errors.length, 0, `age ${age} ${size.width} browser errors: ${JSON.stringify(errors)}`);
      assert.equal(failedResponses.length, 0, `age ${age} ${size.width} failed responses: ${JSON.stringify(failedResponses)}`);
      const screenshot = path.join(out, `tactical-age${age}-${size.width}x${size.height}.png`);
      await page.screenshot({ path: screenshot });
      runs.push({ age, viewport: size, runtime, errors, failedResponses, screenshot: path.relative(root, screenshot) });
      await context.close();
    }
  }
} finally {
  await browser.close();
}

const report = {
  recordedAt: new Date().toISOString(),
  classification: 'ISOLATED_VALID_VISUAL_FIXTURES_NOT_NATURAL_AGE_PROGRESSION_OR_OWNER_ACCEPTANCE',
  journey: 'valid campaign envelope with age-only visual fixture -> War -> Skirmish -> inspect registered Tactical ground and HUD',
  ages: modeScenes.tactical.map((_, age) => age),
  sizes,
  runs,
  result: 'FOCUSED PASS',
  wholeGame: 'INCOMPLETE',
};
await fs.writeFile(path.join(out, 'report.json'), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify({ result: report.result, captures: runs.length, errors: runs.reduce((sum, row) => sum + row.errors.length, 0), failedResponses: runs.reduce((sum, row) => sum + row.failedResponses.length, 0) }, null, 2));
