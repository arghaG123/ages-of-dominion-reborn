import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';

const root = process.cwd();
const out = path.join(root, 'qa/game-completion-20261020/visual-review/kingdom-site-clearance-inspection-live');
await fs.mkdir(out, { recursive: true });
const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
const runs = [];

try {
  for (const viewport of [{ width: 825, height: 375 }, { width: 1280, height: 720 }]) {
    const context = await browser.newContext({ viewport, deviceScaleFactor: 1 });
    const page = await context.newPage();
    const errors = [];
    const failedResponses = [];
    page.on('pageerror', error => errors.push(String(error)));
    page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
    page.on('response', response => { if (response.status() >= 400) failedResponses.push(`${response.status()} ${response.url()}`); });
    await page.goto('http://127.0.0.1:4179/?audit=1', { waitUntil: 'networkidle' });
    await page.locator('[data-choice="new-campaign"]').click();
    await page.locator('[data-choice="scene-class:knight"]').click();
    await page.locator('[data-choice="scene-enter-valley"]').click();
    await page.waitForFunction(() => window.rebornSnapshot()?.story?.flags?.enteredValley === true);
    await page.locator('#context').click();
    await page.locator('[data-choice="site-list"]').click();
    await page.locator('[data-choice="choose-site:townhall"]').click();
    const tutorialToggle = page.locator('[data-choice="tutorial-toggle"]');
    if (await tutorialToggle.isVisible().catch(() => false)) await tutorialToggle.click();
    await page.waitForFunction(() => document.querySelectorAll('#world .plot').length === 18);
    await page.addStyleTag({ content: `
      #world .plot > polygon:last-child {
        fill: rgba(255, 213, 104, .22) !important;
        stroke: rgba(255, 229, 163, .82) !important;
        stroke-width: 2px !important;
      }
      #world .plot[data-plot="townhall"] > polygon:last-child {
        fill: rgba(109, 198, 220, .28) !important;
        stroke: rgba(174, 237, 251, .95) !important;
      }
    ` });
    const geometry = await page.evaluate(() => ({
      age: window.rebornSnapshot()?.age,
      view: document.querySelector('#app')?.dataset.view,
      plotCount: document.querySelectorAll('#world .plot').length,
      plots: [...document.querySelectorAll('#world .plot')].map(node => {
        const rect = node.getBoundingClientRect();
        return { id: node.dataset.plot, state: node.dataset.padState, bounds: [rect.x, rect.y, rect.width, rect.height].map(Math.round), clearing: node.dataset.clearing || null };
      }),
      document: [document.documentElement.scrollWidth, document.documentElement.scrollHeight],
    }));
    assert.equal(geometry.age, 0);
    assert.equal(geometry.view, 'kingdom');
    assert.equal(geometry.plotCount, 18);
    assert.equal(geometry.plots.filter(plot => plot.state === 'empty').length, 17);
    assert.deepEqual(errors, []);
    assert.deepEqual(failedResponses, []);
    const screenshot = path.join(out, `${viewport.width}x${viewport.height}.png`);
    await page.screenshot({ path: screenshot });
    runs.push({ viewport: [viewport.width, viewport.height], classification: 'FRESH_UI_CAMPAIGN_WITH_TEMPORARY_PLOT_TARGET_OVERLAY_FOR_VISUAL_INSPECTION', geometry, screenshot: path.relative(root, screenshot), errors, failedResponses });
    await context.close();
  }
} finally {
  await browser.close();
}

const report = {
  recordedAt: new Date().toISOString(),
  classification: 'VISUAL_SITE_CLEARANCE_INSPECTION_AID_NOT_PRODUCTION_RENDER_OR_ACCEPTANCE',
  note: 'Each browser profile starts a real fresh campaign through the UI. CSS temporarily highlights existing hit polygons so their positions can be compared with the natural ground; no production styles or saved campaign data are changed.',
  runs,
};
await fs.writeFile(path.join(out, 'report.json'), JSON.stringify(report, null, 2));
console.log(JSON.stringify({ classification: report.classification, captures: runs.length, plotCounts: runs.map(run => run.geometry.plotCount), errors: runs.reduce((n, run) => n + run.errors.length, 0), failedResponses: runs.reduce((n, run) => n + run.failedResponses.length, 0), report: path.relative(root, path.join(out, 'report.json')) }, null, 2));
