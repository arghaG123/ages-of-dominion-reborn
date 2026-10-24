import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';

const root = process.cwd();
const out = path.join(root, 'qa/game-completion-20261020/visual-review/kingdom-context-actions-live');
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
    await page.locator('[data-choice="choose-site:P01"]').click();
    await page.waitForFunction(() => document.querySelector('#panel')?.classList.contains('open'));
    const inspector = page.locator('#choices');
    assert.equal(await inspector.locator('button.cost-action').count(), 0, 'an empty site has no unrelated cost list');
    assert.equal(await inspector.locator('[data-choice^="build-picker:"]').count(), 1, 'an empty site exposes one contextual build action');
    assert.equal(await inspector.locator('[data-choice="kingdom-actions-open"]').count(), 1, 'global actions remain reachable from the site inspector');
    const selectedInspector = await inspector.locator('button:visible').evaluateAll(nodes => nodes.map(node => ({
      action: node.dataset.choice,
      label: node.getAttribute('aria-label') || node.textContent.trim(),
    })));
    const inspectPath = path.join(out, `${viewport.width}x${viewport.height}-site.png`);
    await page.screenshot({ path: inspectPath });

    await page.locator('[data-choice="build-picker:P01"]').click();
    await page.waitForFunction(() => document.querySelector('#panel')?.dataset.sheet === 'kingdom-build');
    const buildChoices = page.locator('#choices .kingdom-build-choice');
    assert.equal(await buildChoices.count(), 8, 'all 8 legal building types are available in the focused picker');
    await page.waitForFunction(() => [...document.querySelectorAll('#choices .kingdom-build-choice .cost-art')].every(image => image.complete));
    const pickerAudit = await buildChoices.evaluateAll(nodes => nodes.map(node => ({
      choice: node.dataset.choice,
      accessibleName: node.getAttribute('aria-label'),
      height: node.getBoundingClientRect().height,
      artLoaded: Boolean(node.querySelector('.cost-art')?.complete && node.querySelector('.cost-art')?.naturalWidth),
      missingCostText: [...node.querySelectorAll('.cost-amount')].some(amount => !amount.textContent.trim()),
    })));
    assert.ok(pickerAudit.every(item => item.height >= 48), 'every build option owns a 48px target');
    assert.ok(pickerAudit.every(item => item.accessibleName), 'every build option has a full accessible name');
    assert.ok(pickerAudit.every(item => item.artLoaded), 'every building option displays its current-age building art');
    assert.ok(pickerAudit.every(item => !item.missingCostText), 'cost figures are present');
    const pickerPath = path.join(out, `${viewport.width}x${viewport.height}-build-picker.png`);
    await page.screenshot({ path: pickerPath, fullPage: false });
    await buildChoices.last().scrollIntoViewIfNeeded();
    const lastChoiceBounds = await buildChoices.last().evaluate(node => {
      const rect = node.getBoundingClientRect();
      const panel = document.querySelector('#panel').getBoundingClientRect();
      return { top: rect.top, bottom: rect.bottom, panelTop: panel.top, panelBottom: panel.bottom };
    });
    assert.ok(lastChoiceBounds.top >= lastChoiceBounds.panelTop && lastChoiceBounds.bottom <= lastChoiceBounds.panelBottom, 'the final building option can scroll fully into the panel');
    const pickerEndPath = path.join(out, `${viewport.width}x${viewport.height}-build-picker-end.png`);
    await page.screenshot({ path: pickerEndPath, fullPage: false });

    const before = await page.evaluate(() => ({
      resources: { ...window.rebornSnapshot().resources },
      level: window.rebornSnapshot().plots.find(plot => plot.id === 'P01').level,
    }));
    const lumber = page.locator('[data-choice="build:P01:lumber"]');
    assert.equal(await lumber.getAttribute('aria-disabled'), null, 'fresh campaign can preview the Lumber Camp');
    await lumber.click();
    await page.waitForFunction(() => !document.querySelector('#build-confirm')?.hidden);
    assert.match(await page.locator('#build-title').textContent(), /Lumber Camp/);
    await page.locator('#build-cancel').click();
    const afterCancel = await page.evaluate(() => ({
      resources: { ...window.rebornSnapshot().resources },
      level: window.rebornSnapshot().plots.find(plot => plot.id === 'P01').level,
    }));
    assert.deepEqual(afterCancel, before, 'cancel leaves the site and balances unchanged');

    await page.locator('[data-choice^="build-picker-back:"]').click();
    await page.locator('[data-choice="kingdom-actions-open"]').click();
    await page.waitForFunction(() => document.querySelector('#panel')?.dataset.sheet === 'kingdom-actions');
    const actionPath = path.join(out, `${viewport.width}x${viewport.height}-kingdom-actions.png`);
    await page.screenshot({ path: actionPath });
    const day = await page.evaluate(() => window.rebornSnapshot().day);
    assert.equal(await page.locator('[data-choice="build:townhall"]').count(), 1);
    assert.equal(await page.locator('[data-choice="build:walls"]').count(), 1);
    assert.equal(await page.locator('[data-choice="end-day"]').count(), 1);
    await page.locator('[data-choice="end-day"]').click();
    await page.waitForFunction(previous => window.rebornSnapshot()?.day === previous + 1, day);
    assert.deepEqual(errors, []);
    assert.deepEqual(failedResponses, []);
    runs.push({
      viewport: [viewport.width, viewport.height],
      classification: 'FRESH_UI_CAMPAIGN_CONTEXT_ACTION_INTERACTION_AND_VISUAL_REVIEW',
      selectedInspector: { visibleButtons: selectedInspector, noUnrelatedBuildCosts: true },
      buildOptions: pickerAudit,
      cancelPreservedCampaign: true,
      actions: ['Town Hall', 'Walls', 'end day'],
      dayAdvanced: true,
      screenshots: [inspectPath, pickerPath, pickerEndPath, actionPath].map(file => path.relative(root, file)),
      errors,
      failedResponses,
    });
    await context.close();
  }
} finally {
  await browser.close();
}

const report = {
  recordedAt: new Date().toISOString(),
  classification: 'BOUNDED_LIVE_UI_VISUAL_AND_INTERACTION_EVIDENCE_NOT_FULL_GAME_OR_OWNER_ACCEPTANCE',
  note: 'Each viewport uses an isolated browser profile and a campaign created through the real UI. Build preview is canceled, proving the test does not spend resources or alter a user save.',
  runs,
};
await fs.writeFile(path.join(out, 'report.json'), JSON.stringify(report, null, 2));
console.log(JSON.stringify({ captures: runs.length, buildOptions: runs.map(run => run.buildOptions.length), dayAdvanced: runs.every(run => run.dayAdvanced), errors: runs.reduce((sum, run) => sum + run.errors.length, 0), failedResponses: runs.reduce((sum, run) => sum + run.failedResponses.length, 0), report: path.relative(root, path.join(out, 'report.json')) }, null, 2));
