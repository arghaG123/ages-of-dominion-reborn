import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import modeScenes from '../../../src/data/mode-scenes.json' with { type: 'json' };

const root = process.cwd();
const sizes = {
  '825x375': { width: 825, height: 375 },
  '933x424': { width: 933, height: 424 },
  '1280x720': { width: 1280, height: 720 },
};
const sizeName = process.argv[2] || '825x375';
const age = Number(process.argv[3] || 4);
assert.ok(sizes[sizeName], `supported viewport ${sizeName}`);
assert.ok(Number.isInteger(age) && age >= 0 && age <= 7, `supported age ${age}`);
const out = path.join(root, 'qa/game-completion-20261020/visual-review/defense-scenes-live');
await fs.mkdir(out, { recursive: true });
const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
const context = await browser.newContext({ viewport: sizes[sizeName], deviceScaleFactor: 1 });
const page = await context.newPage();
const errors = [];
page.on('pageerror', error => errors.push(String(error)));
page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
await page.goto('http://127.0.0.1:4179/', { waitUntil: 'networkidle' });
await page.locator('#import-file').setInputFiles(path.join(root, `qa/game-completion-20261020/visual-review/defense-age${age}-visual-fixture.json`));
await page.waitForFunction(expectedAge => window.rebornSnapshot()?.age === expectedAge, age);
await page.locator('[data-choice="nav:war"]').click();
await page.locator('[data-choice="start-siege"]').first().click();
await page.waitForFunction(() => window.rebornSnapshot()?.defense?.status === 'ACTIVE');
await page.waitForFunction(() => document.querySelector('#terrain')?.complete && document.querySelector('#terrain')?.naturalWidth > 0);
const preparationState = await page.evaluate(() => window.rebornSnapshot());
assert.equal(preparationState.defense.paused, true);
const runtime = await page.evaluate(() => {
  const terrain = document.querySelector('#terrain');
  const world = document.querySelector('#world');
  const rect = world.getBoundingClientRect();
  return {
    age: window.rebornSnapshot().age,
    phase: window.rebornSnapshot().defense.practice,
    source: terrain.getAttribute('src'),
    imageLoaded: terrain.complete && terrain.naturalWidth > 0,
    naturalSize: [terrain.naturalWidth, terrain.naturalHeight],
    board: world.getAttribute('data-board'),
    viewport: [innerWidth, innerHeight],
    worldRect: [rect.x, rect.y, rect.width, rect.height].map(Math.round),
    cellCount: world.querySelectorAll('[data-cell]').length,
  };
});
assert.equal(runtime.age, age);
assert.equal(runtime.phase, 'siege');
assert.equal(runtime.source, modeScenes.defense[age]);
assert.equal(runtime.imageLoaded, true);
assert.equal(runtime.board, 'defense-painted-v1');
async function click(choice) {
  const control = page.locator(`[data-choice="${choice}"]`).first();
  assert.equal(await control.count(), 1, `visible UI control ${choice} exists`);
  assert.equal(await control.isDisabled(), false, `UI control ${choice} is enabled`);
  await control.click();
}
async function capture(name) {
  const file = path.join(out, `defense-age${age}-${name}-${sizeName}.png`);
  await page.screenshot({ path: file });
  return path.relative(root, file);
}
const preparation = await capture('preparation');
await click('deploy-hero');
const armyChoice = page.locator('#dock [data-choice^="deploy-army:"]:not([disabled])').first();
assert.equal(await armyChoice.count(), 1);
const selectedStack = await armyChoice.getAttribute('data-choice');
await armyChoice.click();
let state = await page.evaluate(() => window.rebornSnapshot());
assert.equal(state.defense.heroDeployed, true);
assert.equal(state.defense.armyDeployed, true);
const deployed = await capture('deployed');
await click('defense-pause');
await page.waitForTimeout(1800);
state = await page.evaluate(() => window.rebornSnapshot());
assert.equal(state.defense.paused, false);
const wave = await capture('wave');
assert.deepEqual(errors, [], 'the isolated Defense journey produces no browser errors');
const report = {
  recordedAt: new Date().toISOString(),
  classification: `ISOLATED_VALID_AGE${age}_VISUAL_FIXTURE_NOT_NATURAL_GAMEPLAY_ACCEPTANCE`,
  viewport: sizeName,
  journey: `load valid age${age} visual fixture -> War -> Campaign Siege -> deploy hero/army -> first wave`,
  runtime,
  defense: {
    phase: state.defense.practice,
    paused: state.defense.paused,
    heroDeployed: state.defense.heroDeployed,
    armyDeployed: state.defense.armyDeployed,
    selectedStack,
    wave: state.defense.clearedWaves,
    time: state.defense.time,
    spawnedAttackers: state.defense.queue.filter(enemy => enemy.spawned && enemy.hp > 0 && !enemy.leaked).length,
    queuedAttackers: state.defense.queue?.length ?? null,
  },
  captures: { preparation, deployed, wave },
  errors,
};
await fs.writeFile(path.join(out, `defense-age${age}-${sizeName}.json`), JSON.stringify(report, null, 2));
console.log(JSON.stringify(report, null, 2));
await context.close();
await browser.close();
