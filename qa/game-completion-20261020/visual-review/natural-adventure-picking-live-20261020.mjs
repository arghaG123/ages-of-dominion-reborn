import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';

const root = process.cwd();
const out = path.join(root, 'qa/game-completion-20261020/visual-review/adventure-live');
await fs.mkdir(out, { recursive: true });
const report = {
  recordedAt: new Date().toISOString(),
  classification: 'NATURAL_UI_ADVENTURE_ROUTE_AND_SAVE',
  journey: 'new campaign -> skip optional tutorial in the UI -> leave town -> preview and confirm one visible road cell -> save/reload',
  url: 'http://127.0.0.1:4179/?audit=1',
  note: 'The campaign and route are created and advanced through visible controls. No campaign state, route, or resources are injected.',
  errors: [],
  captures: [],
};

const browser = await chromium.launch({
  executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe',
  headless: true,
});
const context = await browser.newContext({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1 });
const page = await context.newPage();
page.on('pageerror', error => report.errors.push(String(error)));
page.on('console', message => { if (message.type() === 'error') report.errors.push(message.text()); });

const read = () => page.evaluate(() => JSON.parse(document.querySelector('#audit-snapshot')?.textContent || 'null'));
async function clickChoice(id) {
  const control = page.locator('[data-choice="' + id + '"]').first();
  await control.waitFor({ state: 'visible', timeout: 10000 });
  assert.equal(await control.isDisabled(), false, id + ' is enabled');
  await control.click();
}
async function capture(name, size) {
  const [width, height] = size.split('x').map(Number);
  await page.setViewportSize({ width, height });
  await page.waitForTimeout(100);
  const file = path.join(out, name + '-' + size + '.png');
  await page.screenshot({ path: file });
  report.captures.push({ name, size, file: path.relative(root, file) });
}
async function waitForAdventure(predicate, label) {
  for (let attempt = 0; attempt < 50; attempt += 1) {
    const state = (await read())?.state;
    if (state?.adventure && predicate(state.adventure)) return state;
    await page.waitForTimeout(100);
  }
  throw new Error('Timed out waiting for ' + label);
}

try {
  await page.goto(report.url, { waitUntil: 'networkidle' });
  await clickChoice('new-campaign');
  await clickChoice('scene-class:knight');
  await clickChoice('scene-enter-valley');
  await page.waitForTimeout(100);
  await page.locator('#context').click();
  await clickChoice('site-list');
  await clickChoice('choose-site:townhall');
  await clickChoice('tutorial-toggle');
  await page.locator('[data-choice="nav:adventure"]').first().click();
  await clickChoice('enter-adventure');
  await waitForAdventure(value => value.atTown === false && value.moves === 5, 'fresh trip outside town');
  report.campaignId = (await read()).state.id;
  report.before = (await read()).state.adventure;
  report.mountInputOwner = await page.locator('#world [data-mount]').first().getAttribute('pointer-events');
  assert.equal(report.mountInputOwner, 'none', 'the horse art is decorative and the underlying map cell owns the pointer');
  await capture('adventure-exploration-before-route', '825x375');
  await capture('adventure-exploration-before-route', '1280x720');

  const roadCell = page.locator('#world [data-adventure-cell="8,7"]');
  assert.equal(await roadCell.count(), 1, 'the intended adjacent route cell is rendered once');
  await roadCell.click();
  await page.waitForTimeout(80);
  const preview = await page.evaluate(() => ({
    destinationCount: document.querySelectorAll('#world [data-route-destination]').length,
    confirmations: [...document.querySelectorAll('[data-choice="confirm-route"]')].map(button => ({ disabled: button.disabled, label: button.getAttribute('aria-label') })),
  }));
  assert.equal(preview.destinationCount, 1, 'one route destination is previewed');
  assert.equal(preview.confirmations.some(button => !button.disabled), true, 'the legal one-step route can be confirmed');
  report.preview = preview;
  await capture('adventure-route-preview-8-7', '1280x720');
  await page.locator('[data-choice="confirm-route"]').first().click();
  const moved = await waitForAdventure(value => value.x === 8 && value.y === 7, 'one confirmed road step');
  assert.equal(moved.adventure.moves, 4, 'a one-cell route spends one move');
  assert.ok(moved.adventure.visited.includes('8,7'), 'the destination is added to discovered terrain');
  report.afterMove = moved.adventure;
  await capture('adventure-after-route-8-7', '825x375');
  await capture('adventure-after-route-8-7', '1280x720');

  await page.locator('#save').click();
  await page.waitForTimeout(120);
  await page.reload({ waitUntil: 'networkidle' });
  const snapshot = await read();
  if (snapshot?.view === 'home' && await page.locator('[data-choice="continue"]').isVisible()) await clickChoice('continue');
  const reloaded = await waitForAdventure(value => value.x === 8 && value.y === 7 && value.moves === 4, 'saved route after reload');
  assert.equal(reloaded.id, report.campaignId, 'reload retains the same campaign identity');
  assert.ok(reloaded.adventure.visited.includes('8,7'), 'reload retains the newly visited cell');
  report.reload = { campaignId: reloaded.id, adventure: reloaded.adventure };
  report.errors = [...new Set(report.errors)];
  assert.deepEqual(report.errors, [], 'the natural route journey has no browser errors');
  report.passed = true;
} catch (error) {
  report.passed = false;
  report.failure = String(error);
} finally {
  report.recordedAt = new Date().toISOString();
  await fs.writeFile(path.join(out, 'natural-adventure-picking-live-20261020.json'), JSON.stringify(report, null, 2) + '\n');
  await browser.close();
}

if (!report.passed) throw new Error(report.failure);
console.log(JSON.stringify({ passed: report.passed, campaignId: report.campaignId, before: report.before, afterMove: report.afterMove, reload: report.reload, captureCount: report.captures.length, errors: report.errors }));
