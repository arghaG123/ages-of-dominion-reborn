import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
import path from 'node:path';
import worlds from '../../../src/data/adventure-worlds.json' with { type: 'json' };

const root = process.cwd();
const url = 'http://127.0.0.1:4179/?audit=owner-map-runtime-recheck';
const output = path.join(root, 'qa/game-completion-20261021/visual-review/adventure-owner-map-runtime-live-recheck-20261021');
await fs.mkdir(output, { recursive: false });
const report = {
  recordedAt: new Date().toISOString(),
  classification: 'ISOLATED_NATURAL_UI_OWNER_MAP_SOURCE_RECHECK',
  purpose: 'Inspect the actual campaign picker and Adventure DOM image sources for all 12 worlds through visible user controls in fresh isolated browser contexts.',
  url,
  results: [],
};
const browser = await chromium.launch({
  executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe',
  headless: true,
});
async function clickChoice(page, id) {
  const control = page.locator('[data-choice="' + id + '"]').first();
  await control.waitFor({ state: 'visible', timeout: 15000 });
  if (await control.isDisabled()) throw new Error('Disabled choice: ' + id);
  await control.click();
}
for (const world of worlds) {
  const result = { worldId: world.id, errors: [], failedResponses: [] };
  const context = await browser.newContext({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1 });
  const page = await context.newPage();
  page.on('pageerror', error => result.errors.push(String(error)));
  page.on('console', message => { if (message.type() === 'error') result.errors.push(message.text()); });
  page.on('response', response => {
    if (response.status() >= 400) result.failedResponses.push({ status: response.status(), url: response.url() });
  });
  try {
    await page.goto(url, { waitUntil: 'networkidle' });
    await clickChoice(page, 'new-campaign');
    await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'campaignMapSelect', null, { timeout: 15000 });
    await clickChoice(page, 'campaign-world:' + world.id);
    await page.waitForFunction(() => {
      const image = document.querySelector('#terrain');
      return image?.complete && image.naturalWidth > 0;
    }, null, { timeout: 15000 });
    result.picker = await page.evaluate(id => {
      const image = document.querySelector('#terrain');
      const worldNode = document.querySelector('#world');
      const thumb = document.querySelector('.campaign-world-option[data-world-id="' + id + '"] img');
      const pathOf = node => node ? new URL(node.getAttribute('src'), document.baseURI).pathname : null;
      return {
        terrainSource: pathOf(image),
        selectedPreviewAttribute: worldNode?.dataset.campaignWorldPreviewSource || null,
        selectedThumbnailSource: pathOf(thumb),
        width: image?.naturalWidth || 0,
        height: image?.naturalHeight || 0,
      };
    }, world.id);
    const expectedOwnerPath = '/' + world.file.replaceAll('\\', '/');
    result.ownerFile = world.file;
    result.expectedOwnerPath = expectedOwnerPath;
    result.pickerShowsOwnerFile = result.picker.terrainSource === expectedOwnerPath
      && result.picker.selectedThumbnailSource === expectedOwnerPath;

    await clickChoice(page, 'begin-selected-world');
    await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'hero', null, { timeout: 15000 });
    await clickChoice(page, 'scene-class:knight');
    await clickChoice(page, 'scene-enter-valley');
    await page.waitForTimeout(100);
    await page.locator('#context').click();
    await clickChoice(page, 'site-list');
    await clickChoice(page, 'choose-site:townhall');
    await clickChoice(page, 'tutorial-toggle');
    await page.locator('[data-choice="nav:adventure"]').first().click();
    await page.locator('#dock [data-choice="inspect:adventure"]').click();
    await clickChoice(page, 'enter-adventure');
    await page.waitForFunction(() => Boolean(window.rebornSnapshot?.()?.adventure), null, { timeout: 15000 });
    await page.waitForFunction(() => {
      const image = document.querySelector('#terrain');
      return image?.complete && image.naturalWidth > 0;
    }, null, { timeout: 15000 });
    result.runtime = await page.evaluate(() => {
      const image = document.querySelector('#terrain');
      const worldNode = document.querySelector('#world');
      const minimapImages = [...(document.querySelectorAll('#adventure-minimap image[data-minimap-terrain]') ?? [])];
      const pathOf = value => value ? new URL(value, document.baseURI).pathname : null;
      return {
        worldId: worldNode?.dataset.adventureWorldId || null,
        terrainSource: pathOf(image?.getAttribute('src')),
        terrainAttribute: worldNode?.dataset.adventureTerrainFile || null,
        referenceAttribute: worldNode?.dataset.adventureReferenceFile || null,
        minimapSources: minimapImages.map(node => node.getAttribute('href')),
        width: image?.naturalWidth || 0,
        height: image?.naturalHeight || 0,
        renderModel: worldNode?.dataset.adventureRenderModel || null,
      };
    });
    result.runtimeShowsOwnerFile = result.runtime.terrainSource === expectedOwnerPath;
    result.minimapShowsOwnerFile = result.runtime.minimapSources.length === 2
      && result.runtime.minimapSources.every(source => source === world.file);
    result.screenshot = path.relative(root, path.join(output, world.id + '-1280x720.png'));
    await page.screenshot({ path: path.join(root, result.screenshot) });
  } catch (error) {
    result.error = String(error?.stack || error);
  } finally {
    await context.close();
    report.results.push(result);
    console.log(JSON.stringify({
      worldId: result.worldId,
      pickerShowsOwnerFile: result.pickerShowsOwnerFile ?? null,
      runtimeShowsOwnerFile: result.runtimeShowsOwnerFile ?? null,
      minimapShowsOwnerFile: result.minimapShowsOwnerFile ?? null,
      error: result.error ?? null,
    }));
  }
}
await browser.close();
report.summary = {
  worlds: report.results.length,
  pickerOwnerMatches: report.results.filter(row => row.pickerShowsOwnerFile).length,
  runtimeOwnerMatches: report.results.filter(row => row.runtimeShowsOwnerFile).length,
  minimapOwnerMatches: report.results.filter(row => row.minimapShowsOwnerFile).length,
  browserErrorWorlds: report.results.filter(row => row.errors.length || row.error).length,
  failedResponseWorlds: report.results.filter(row => row.failedResponses.length).length,
};
await fs.writeFile(path.join(output, 'report.json'), JSON.stringify(report, null, 2) + '\n', 'utf8');
console.log('SUMMARY ' + JSON.stringify(report.summary));