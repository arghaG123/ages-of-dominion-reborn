import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import modeScenes from '../../../src/data/mode-scenes.json' with { type: 'json' };
import { checksum } from '../../../src/core/save.js';

const root = process.cwd();
const out = path.join(root, process.env.AOD_ADVENTURE_REVIEW_OUT || 'qa/game-completion-20261020/visual-review/adventure-all-ages-live');
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
  state.id = `adventure-age-${age}-visual-review`;
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
    const controls = [...document.querySelectorAll('#dock button, #scene-ui button')].filter(visible).map(node => {
      const r = node.getBoundingClientRect();
      const target = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2);
      return {
        choice: node.dataset.choice || node.getAttribute('aria-label') || node.textContent.trim(),
        disabled: Boolean(node.disabled),
        within: r.left >= 0 && r.top >= 0 && r.right <= innerWidth && r.bottom <= innerHeight,
        centerReceivesInput: Boolean(target && (target === node || node.contains(target))),
      };
    });
    const cells = [...(world?.querySelectorAll('[data-adventure-cell]') ?? [])];
    return {
      age: window.rebornSnapshot()?.age,
      view: document.querySelector('#app')?.dataset.view,
      atTown: window.rebornSnapshot()?.adventure?.atTown,
      visitedCells: window.rebornSnapshot()?.adventure?.visited?.length ?? 0,
      terrainSource: terrain?.getAttribute('src'),
      terrainLoaded: Boolean(terrain?.complete && terrain.naturalWidth > 0),
      terrainSize: terrain ? [terrain.naturalWidth, terrain.naturalHeight] : null,
      board: world?.getAttribute('data-board'),
      registration: world?.getAttribute('data-registration'),
      viewport: [innerWidth, innerHeight],
      world: box(world),
      terrain: box(terrain),
      adventureCellCount: cells.length,
      visibleAdventureCellCount: cells.filter(node => {
        const r = node.getBoundingClientRect();
        return r.width > 1 && r.height > 1 && r.right > 0 && r.bottom > 0 && r.left < innerWidth && r.top < innerHeight;
      }).length,
      minimap: box(document.querySelector('#adventure-minimap')),
      fog: (() => {
        const overlay = document.querySelector('[data-fog-state="saved-unvisited"]');
        const maskId = overlay?.getAttribute('mask')?.slice(5, -1);
        const mask = maskId ? document.getElementById(maskId) : null;
        const filterId = mask?.querySelector('g[filter]')?.getAttribute('filter')?.slice(5, -1);
        return { count: document.querySelectorAll('[data-fog-state="saved-unvisited"]').length, mask: Boolean(mask), filter: Boolean(filterId && document.getElementById(filterId)), bounds: box(overlay) };
      })(),
      panelOpen: document.querySelector('#panel')?.classList.contains('open') ?? false,
      dock: box(document.querySelector('#dock')),
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
        name: `age-${age}-adventure-visual.json`,
        mimeType: 'application/json',
        buffer: Buffer.from(fixture(age)),
      });
      await page.waitForFunction(expected => window.rebornSnapshot()?.age === expected, age);
      await page.locator('[data-choice="nav:adventure"]').click();
      await page.locator('[data-choice="enter-adventure"]:visible').click();
      await page.waitForFunction(expected => window.rebornSnapshot()?.age === expected && window.rebornSnapshot()?.adventure?.atTown === false, age);
      await page.waitForFunction(() => document.querySelector('#terrain')?.complete && document.querySelector('#terrain')?.naturalWidth > 0);
      const runtime = await inspect(page);
      assert.equal(runtime.age, age);
      assert.equal(runtime.view, 'adventure');
      assert.equal(runtime.atTown, false);
      assert.equal(runtime.terrainSource, modeScenes.adventure[age]);
      assert.equal(runtime.terrainLoaded, true);
      assert.equal(runtime.board, 'adventure-painted-v1');
      assert.ok(runtime.adventureCellCount > 0);
      assert.ok(runtime.visibleAdventureCellCount > 0);
      assert.ok(runtime.minimap && runtime.minimap.width > 0, 'valley minimap is visible after leaving town');
      assert.deepEqual(runtime.fog, { ...runtime.fog, count: 1, mask: true, filter: true }, 'saved-unvisited cells use one feathered, non-interactive fog surface');
      assert.equal(runtime.panelOpen, false);
      assert.equal(runtime.visibleControls.filter(control => !control.within || !control.centerReceivesInput).length, 0, `age ${age} ${size.width} adventure controls fit and receive input`);
      assert.equal(errors.length, 0, `age ${age} ${size.width} browser errors: ${JSON.stringify(errors)}`);
      assert.equal(failedResponses.length, 0, `age ${age} ${size.width} failed responses: ${JSON.stringify(failedResponses)}`);
      const screenshot = path.join(out, `adventure-age${age}-${size.width}x${size.height}.png`);
      await page.screenshot({ path: screenshot });
      let fogDisabledScreenshot = '';
      if (age === 4 && size.width === 1280) {
        fogDisabledScreenshot = path.join(out, 'adventure-age4-1280x720-fog-disabled-diagnostic.png');
        await page.addStyleTag({ content: '#world [data-fog-state="saved-unvisited"] { display: none !important; }' });
        await page.screenshot({ path: fogDisabledScreenshot });
      }
      runs.push({ age, viewport: size, runtime, errors, failedResponses, screenshot: path.relative(root, screenshot), fogDisabledScreenshot: fogDisabledScreenshot ? path.relative(root, fogDisabledScreenshot) : '' });
      await context.close();
    }
  }
} finally {
  await browser.close();
}

const report = {
  recordedAt: new Date().toISOString(),
  classification: 'ISOLATED_VALID_VISUAL_FIXTURES_NOT_NATURAL_AGE_PROGRESSION_OR_OWNER_ACCEPTANCE',
  journey: 'valid campaign envelope with age-only visual fixture -> Adventure -> leave town -> inspect registered scene, map and HUD',
  ages: modeScenes.adventure.map((_, age) => age),
  sizes,
  runs,
  result: 'FOCUSED PASS',
  wholeGame: 'INCOMPLETE',
};
await fs.writeFile(path.join(out, 'report.json'), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify({ result: report.result, captures: runs.length, errors: runs.reduce((sum, row) => sum + row.errors.length, 0), failedResponses: runs.reduce((sum, row) => sum + row.failedResponses.length, 0) }, null, 2));
