import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';

const root = process.cwd();
const sizes = {
  '825x375': { width: 825, height: 375 },
  '933x424': { width: 933, height: 424 },
  '1280x720': { width: 1280, height: 720 },
};
const sizeName = process.argv[2] || '825x375';
if (!sizes[sizeName]) throw new Error(`Unsupported viewport: ${sizeName}`);
const out = path.join(root, 'qa/game-completion-20261020/visual-review/defense-live');
await fs.mkdir(out, { recursive: true });
const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
const context = await browser.newContext({ viewport: sizes[sizeName], deviceScaleFactor: 1 });
const page = await context.newPage();
const errors = [];
page.on('pageerror', error => errors.push(String(error)));
page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
await page.goto('http://127.0.0.1:4179/', { waitUntil: 'networkidle' });
async function click(choice) {
  const control = page.locator(`[data-choice="${choice}"]`).first();
  assert.equal(await control.count(), 1, `visible UI control ${choice} exists`);
  assert.equal(await control.isDisabled(), false, `UI control ${choice} is enabled`);
  await control.click();
}
async function snapshot() { return page.evaluate(() => window.rebornSnapshot()); }
async function capture(name) {
  const file = path.join(out, `${name}-${sizeName}.png`);
  await page.screenshot({ path: file });
  return path.relative(root, file);
}

await click('new-campaign');
await click('scene-class:knight');
await click('scene-enter-valley');
await click('nav:war');
const warModes = await capture('war-modes');
await click('start-siege');
let state = await snapshot();
assert.equal(state.defense?.status, 'ACTIVE', 'starting Campaign Siege opens a defense session');
assert.equal(state.defense.paused, true, 'the new session starts in preparation pause');
const preparation = await capture('defense-preparation');
await click('deploy-hero');
const armyChoice = page.locator('#dock [data-choice^="deploy-army:"]:not([disabled])').first();
assert.equal(await armyChoice.count(), 1, 'an available army stack can be deployed');
const deployedStack = await armyChoice.getAttribute('data-choice');
await armyChoice.click();
state = await snapshot();
assert.equal(state.defense.heroDeployed, true, 'the selected hero is deployed');
assert.equal(state.defense.armyDeployed, true, 'the selected army stack is deployed');
const deployed = await capture('defense-deployed');
await click('defense-pause');
await page.waitForTimeout(1800);
state = await snapshot();
assert.equal(state.defense.paused, false, 'Resume starts the first defense wave');
const wave = await capture('defense-wave');
assert.deepEqual(errors, [], 'the live Defense journey produces no browser errors');
const controls = await page.locator('button[data-choice]').evaluateAll(nodes => nodes.filter(node => {
  const rect = node.getBoundingClientRect();
  return rect.width > 0 && rect.height > 0 && rect.left >= 0 && rect.top >= 0 && rect.right <= innerWidth && rect.bottom <= innerHeight;
}).map(node => {
  const rect = node.getBoundingClientRect();
  const x = rect.left + rect.width / 2, y = rect.top + rect.height / 2;
  const hit = document.elementFromPoint(x, y)?.closest('button[data-choice]')?.dataset.choice || null;
  return { choice: node.dataset.choice, name: node.getAttribute('aria-label') || node.innerText.trim(), rect: [rect.x, rect.y, rect.width, rect.height].map(Math.round), centerOwner: hit };
}));
const report = {
  recordedAt: new Date().toISOString(),
  viewport: sizeName,
  journey: 'fresh campaign -> War -> Campaign Siege -> pause/preparation -> deploy hero and army -> first live wave',
  defense: {
    phase: state.defense.practice,
    paused: state.defense.paused,
    heroDeployed: state.defense.heroDeployed,
    armyDeployed: state.defense.armyDeployed,
    selectedStack: deployedStack,
    wave: state.defense.clearedWaves,
    time: state.defense.time,
    core: state.defense.core,
    spawnedAttackers: state.defense.queue.filter(enemy => enemy.spawned && enemy.hp > 0 && !enemy.leaked).length,
    queuedAttackers: state.defense.queue?.length ?? null,
  },
  captures: { warModes, preparation, deployed, wave },
  controls,
  errors,
};
await fs.writeFile(path.join(out, `defense-live-${sizeName}.json`), JSON.stringify(report, null, 2));
console.log(JSON.stringify(report, null, 2));
await context.close();
await browser.close();
