import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
import path from 'node:path';
import { KINGDOM_AGES, kingdomPainting } from '../../../src/client/kingdom-view.js';

const root = process.cwd();
const base = path.join(root, 'qa/game-completion-20261020/visual-review');
const fixtures = path.join(base, 'kingdom-mature-fixtures');
const out = path.join(base, 'kingdom-mature-all-viewport-live');
const sizes = [
  { width: 825, height: 375 },
  { width: 933, height: 424 },
  { width: 1280, height: 720 },
];
await fs.mkdir(out, { recursive: true });
const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
const captures = [];

try {
  for (let age = 0; age < KINGDOM_AGES.length; age += 1) {
    for (const size of sizes) {
      const context = await browser.newContext({ viewport: size, deviceScaleFactor: 1 });
      const page = await context.newPage();
      const errors = [];
      const failedResponses = [];
      page.on('pageerror', error => errors.push(String(error)));
      page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
      page.on('response', response => { if (response.status() >= 400) failedResponses.push({ status: response.status(), url: response.url() }); });
      await page.goto('http://127.0.0.1:4179/', { waitUntil: 'networkidle' });
      await page.locator('#import-file').setInputFiles(path.join(fixtures, `kingdom-age${age}-mature.json`));
      await page.waitForFunction(expected => window.rebornSnapshot()?.age === expected, age);
      await page.locator('[data-choice="nav:kingdom"]').click();
      await page.waitForFunction(() => document.querySelector('#terrain')?.complete && document.querySelector('#terrain')?.naturalWidth > 0);
      await page.waitForTimeout(180);

      const runtime = await page.evaluate(() => {
        const terrain = document.querySelector('#terrain');
        const world = document.querySelector('#world');
        const visible = element => {
          const rect = element.getBoundingClientRect();
          const style = getComputedStyle(element);
          return rect.width > 0 && rect.height > 0 && style.visibility !== 'hidden' && style.display !== 'none';
        };
        const controls = [...document.querySelectorAll('button,[role="button"]')].filter(visible).map(element => {
          const rect = element.getBoundingClientRect();
          // Building sprites extend above their clickable ground polygon. Test the
          // actual plot hit region instead of the union box around sprite plus plot.
          const hitArea = element.matches('[data-plot]')
            ? element.querySelector('polygon[fill="transparent"]') || element
            : element;
          const hitRect = hitArea.getBoundingClientRect();
          const x = hitRect.left + hitRect.width / 2;
          const y = hitRect.top + hitRect.height / 2;
          const hit = document.elementFromPoint(x, y);
          return {
            label: element.getAttribute('aria-label') || element.dataset.choice || element.textContent.trim().slice(0, 48),
            within: rect.left >= 0 && rect.top >= 0 && rect.right <= innerWidth && rect.bottom <= innerHeight,
            centerReceivesInput: hit === element || Boolean(hit?.closest?.('button,[role="button"]') === element),
            rect: { x: Math.round(rect.x), y: Math.round(rect.y), width: Math.round(rect.width), height: Math.round(rect.height) },
            hitArea: { x: Math.round(hitRect.x), y: Math.round(hitRect.y), width: Math.round(hitRect.width), height: Math.round(hitRect.height) },
          };
        });
        const state = window.rebornSnapshot();
        return {
          age: state.age,
          view: document.querySelector('#app')?.dataset.view,
          terrain: terrain?.getAttribute('src'),
          terrainLoaded: Boolean(terrain?.complete && terrain.naturalWidth > 0),
          terrainSize: [terrain?.naturalWidth, terrain?.naturalHeight],
          viewport: [innerWidth, innerHeight],
          plotCount: world?.querySelectorAll('[data-plot]').length ?? null,
          plottedImages: world?.querySelectorAll('[data-plot] image').length ?? null,
          ownedPlots: state.plots.filter(plot => plot.type).length,
          wallLevel: state.walls.level,
          documentSize: [document.documentElement.scrollWidth, document.documentElement.scrollHeight],
          controls,
        };
      });
      const plotInteractions = [];
      if (size.width === 825) {
        const plotIds = await page.locator('[data-plot]').evaluateAll(elements => elements.map(element => element.getAttribute('data-plot')));
        for (const plotId of plotIds) {
          try {
            await page.locator(`[data-plot="${plotId}"] polygon[fill="transparent"]`).last().click({ timeout: 1500 });
            await page.waitForFunction(() => document.querySelector('#panel')?.classList.contains('open'), null, { timeout: 1500 });
            plotInteractions.push({ plotId, panelOpened: true });
          } catch (error) {
            plotInteractions.push({ plotId, panelOpened: false, error: String(error) });
          } finally {
            if (await page.locator('#panel').evaluate(element => element.classList.contains('open'))) {
              await page.locator('#panel-close').click();
              await page.waitForFunction(() => !document.querySelector('#panel')?.classList.contains('open'));
            }
          }
        }
      }
      const screenshot = path.join(out, `kingdom-age${age}-${size.width}x${size.height}.png`);
      await page.screenshot({ path: screenshot });
      const expectedTerrain = kingdomPainting({ age, walls: { level: 1 }, buildJobs: [] }).file;
      captures.push({
        age,
        ageName: KINGDOM_AGES[age],
        ...runtime,
        expectedTerrain,
        allControlsWithin: runtime.controls.every(control => control.within),
        allControlsCenterHit: runtime.controls.every(control => control.centerReceivesInput),
        noDocumentOverflow: runtime.documentSize[0] <= size.width && runtime.documentSize[1] <= size.height,
        plotInteractions,
        plotInteractionFailures: plotInteractions.filter(interaction => !interaction.panelOpened),
        screenshot: path.relative(root, screenshot),
        errors,
        failedResponses,
      });
      await context.close();
    }
  }
} finally {
  await browser.close();
}

const report = {
  recordedAt: new Date().toISOString(),
  classification: 'SYNTHETIC_MATURE_KINGDOM_RESPONSIVE_VISUAL_REVIEW_NOT_EARNED_PROGRESSION_OR_ACCEPTANCE',
  fixtureNote: 'Valid age-specific mature Kingdom save fixtures occupy the normal plots to inspect placement and responsive layout. They do not establish earned progression, purchase legality, city balance, natural journey completion, or owner acceptance.',
  sizes,
  captures,
  result: captures.length === 24 && captures.every(capture => capture.view === 'kingdom' && capture.terrainLoaded && capture.terrain === capture.expectedTerrain && capture.plotCount === 18 && capture.ownedPlots === 18 && capture.allControlsWithin && capture.allControlsCenterHit && capture.noDocumentOverflow && capture.errors.length === 0 && capture.failedResponses.length === 0 && (capture.viewport[0] !== 825 || capture.plotInteractions.length === 18 && capture.plotInteractionFailures.length === 0))
    ? 'FOCUSED PASS'
    : 'FOCUSED FAIL',
  wholeGame: 'INCOMPLETE',
};
await fs.writeFile(path.join(out, 'report.json'), JSON.stringify(report, null, 2));
console.log(JSON.stringify({
  classification: report.classification,
  result: report.result,
  captures: captures.map(({ age, ageName, viewport, terrainLoaded, plotCount, plottedImages, ownedPlots, wallLevel, allControlsWithin, allControlsCenterHit, noDocumentOverflow, plotInteractions, plotInteractionFailures, errors, failedResponses }) => ({ age, ageName, viewport, terrainLoaded, plotCount, plottedImages, ownedPlots, wallLevel, allControlsWithin, allControlsCenterHit, noDocumentOverflow, plotInteractions: plotInteractions.length, plotInteractionFailures, errors: errors.length, failedResponses: failedResponses.length })),
}, null, 2));
