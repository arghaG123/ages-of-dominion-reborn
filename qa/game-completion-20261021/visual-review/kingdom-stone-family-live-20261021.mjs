import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import data from '../../../src/data/reference-data.json' with { type: 'json' };
import worlds from '../../../src/data/adventure-worlds.json' with { type: 'json' };
import { cost, rates } from '../../../src/core/campaign.js';

const root = process.cwd();
const out = path.join(root, 'qa/game-completion-20261021/visual-review/kingdom-stone-family-live-20261021-run2');
await fs.mkdir(out, { recursive: true });
const report = { recordedAt: new Date().toISOString(), url: 'http://127.0.0.1:4179/?audit=1', isolatedCampaign: true, phases: [], errors: [] };
const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
const context = await browser.newContext({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1 });
const page = await context.newPage();
await page.clock.install();
page.on('pageerror', error => report.errors.push(String(error)));
page.on('console', message => { if (message.type() === 'error') report.errors.push(message.text()); });
page.on('response', response => { if (response.status() >= 400) report.errors.push('HTTP ' + response.status() + ' ' + response.url()); });
const read = () => page.evaluate(() => JSON.parse(document.querySelector('#audit-snapshot')?.textContent || 'null'));

async function clickChoice(id) {
  const control = page.locator('[data-choice="' + id + '"]').first();
  await control.waitFor({ state: 'visible', timeout: 10000 });
  assert.equal(await control.isDisabled(), false, id + ' is enabled');
  await control.click();
}
async function waitForState(predicate, label) {
  for (let step = 0; step < 120; step += 1) {
    const snapshot = await read();
    if (snapshot?.state && predicate(snapshot.state)) return snapshot.state;
    await page.clock.runFor(250);
  }
  throw new Error('Timed out waiting for ' + label);
}
async function clearInspector() {
  const close = page.locator('#panel-close');
  if (await close.isVisible().catch(() => false)) await close.click();
}
async function clearSceneSelection() {
  await clearInspector();
  const target = page.locator('#world');
  const bounds = await target.boundingBox();
  assert.ok(bounds, 'Kingdom world is visible');
  if (await page.locator('#world .plot.selected').count() === 0) return;
  for (const y of [0.45, 0.52, 0.6, 0.4, 0.3, 0.7]) {
    for (const x of [0.92, 0.08, 0.85, 0.15, 0.78, 0.22, 0.5]) {
      await page.mouse.click(bounds.x + bounds.width * x, bounds.y + bounds.height * y);
      if (await page.locator('#world .plot.selected').count() === 0) return;
      await clearInspector();
    }
  }
  throw new Error('Could not clear selected Kingdom site');
}
async function waitForResources(required, label) {
  const ageCapsHours = [8, 7, 6, 5, 4, 3.5, 3, 3];
  for (let step = 0; step < 100; step += 1) {
    const state = (await read())?.state;
    assert.ok(state, 'campaign exists before ' + label);
    const short = Object.entries(required).filter(([key, value]) => state.resources[key] + 1e-6 < value);
    if (!short.length) return state;
    const income = rates(state);
    const waits = short.map(([key, value]) => {
      assert.ok(income[key] > 0, 'a legal producer supplies ' + key + ' for ' + label);
      return (value - state.resources[key]) / income[key];
    });
    const elapsed = Math.min(Math.ceil(Math.max(...waits) * 1000) + 500, Math.floor(ageCapsHours[state.age] * 3600000));
    await page.clock.fastForward(Math.max(1000, elapsed));
    await page.waitForTimeout(30);
  }
  throw new Error('Could not earn resources for ' + label);
}
async function beginBuild(choice, payment, label) {
  await waitForResources(payment, label);
  await clickChoice(choice);
  await page.locator('#build-commit').waitFor({ state: 'visible', timeout: 10000 });
  await page.locator('#build-commit').click();
}
async function capturePhase(name, expectedPhase) {
  await clearSceneSelection();
  await page.waitForFunction(() => {
    const image = document.querySelector('#terrain');
    return image && image.complete && image.naturalWidth > 0 && image.naturalHeight > 0;
  });
  const scene = await page.evaluate(() => {
    const terrain = document.querySelector('#terrain');
    const wall = document.querySelector('#world [data-walls-phase]');
    return {
      view: document.querySelector('#app')?.dataset.view,
      wallPhase: wall?.getAttribute('data-walls-phase'),
      wallLevel: Number(wall?.getAttribute('data-walls-level')),
      terrain: terrain?.getAttribute('src'),
      terrainLoaded: Boolean(terrain?.complete && terrain?.naturalWidth > 0),
      dimensions: [terrain?.naturalWidth, terrain?.naturalHeight],
      plotCount: document.querySelectorAll('#world .plot').length,
      siteCount: document.querySelectorAll('#world .plot[data-pad-state]').length,
    };
  });
  assert.equal(scene.view, 'kingdom');
  assert.equal(scene.wallPhase, expectedPhase);
  assert.equal(scene.terrainLoaded, true);
  assert.equal(scene.terrain.includes('kingdom-stone-populated-20261021/'), true);
  assert.deepEqual(scene.dimensions, [1678, 937]);
  assert.equal(scene.plotCount, 18);
  for (const [width, height] of [[1280, 720], [825, 375]]) {
    await page.setViewportSize({ width, height });
    await page.waitForTimeout(140);
    const file = path.join(out, name + '-' + width + 'x' + height + '.png');
    await page.screenshot({ path: file });
    report.phases.push({ name, size: width + 'x' + height, scene, screenshot: path.relative(root, file) });
  }
}

try {
  await page.goto(report.url, { waitUntil: 'networkidle' });
  await clickChoice('new-campaign');
  await clickChoice('campaign-world:' + worlds[10].id);
  await clickChoice('begin-selected-world');
  await clickChoice('scene-class:knight');
  await clickChoice('scene-enter-valley');
  await waitForState(state => state.story.flags.enteredValley === true, 'fresh Stone campaign');
  await page.locator('#context').click();
  await clickChoice('site-list');
  await clickChoice('choose-site:townhall');
  await clickChoice('tutorial-toggle');
  await waitForState(state => state.tutorial.skipped === true, 'tutorial skip');
  await capturePhase('stone-ground', 'none');

  await clearInspector();
  await page.locator('#context').click();
  await clickChoice('site-list');
  await clickChoice('choose-site:P01');
  await clickChoice('build-picker:P01');
  await beginBuild('build:P01:quarry', cost(data, 'quarry', 0), 'quarry');
  await waitForState(state => state.buildJobs.some(job => job.plotId === 'P01' && job.type === 'quarry'), 'quarry construction');
  await page.clock.fastForward(10000);
  await waitForState(state => state.plots.some(plot => plot.id === 'P01' && plot.type === 'quarry' && plot.level === 1) && !state.buildJobs.some(job => job.plotId === 'P01'), 'quarry completion');

  async function buildWall(targetLevel) {
    let state = (await read()).state;
    while (state.walls.level < targetLevel) {
      const level = state.walls.level;
      await clearInspector();
      await clickChoice('kingdom-actions-open');
      await beginBuild('build:walls', cost(data, 'walls', level), 'Walls level ' + (level + 1));
      await waitForState(value => value.buildJobs.some(job => job.plotId === 'walls'), 'wall scaffold');
      await capturePhase('stone-scaffold-level-' + (level + 1), 'scaffold');
      await page.clock.fastForward(10000);
      state = await waitForState(value => value.walls.level === level + 1 && !value.buildJobs.some(job => job.plotId === 'walls'), 'Walls level ' + (level + 1));
      await capturePhase(level === 0 ? 'stone-wall' : 'stone-wall-tall', level === 0 ? 'built' : 'tall');
    }
    return state;
  }
  await buildWall(2);
  report.finalState = (await read()).state;
  report.errors = [...new Set(report.errors)];
  report.passed = report.errors.length === 0 && report.phases.length === 10;
  await fs.writeFile(path.join(out, 'report.json'), JSON.stringify(report, null, 2) + '\n');
  console.log(JSON.stringify({ passed: report.passed, phases: report.phases.map(item => item.name + '@' + item.size), errors: report.errors, report: path.relative(root, path.join(out, 'report.json')) }, null, 2));
  assert.equal(report.passed, true);
} finally {
  await browser.close();
}