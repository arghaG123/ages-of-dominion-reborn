import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';

const root = process.cwd();
const viewportSizes = {
  '1280x720': { width: 1280, height: 720 },
  '825x375': { width: 825, height: 375 },
};
const viewportName = process.argv[2] || '1280x720';
if (!viewportSizes[viewportName]) throw new Error(`Unsupported viewport: ${viewportName}`);
const outputRun = process.argv[3] || `natural-run${viewportName === '1280x720' ? '' : `-${viewportName}`}`;
if (!/^[a-z0-9-]+$/i.test(outputRun)) throw new Error(`Unsupported output folder: ${outputRun}`);
const out = `${root}/qa/game-completion-20261019/visual-review/${outputRun}`;
await fs.mkdir(out, { recursive: true });
const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
const context = await browser.newContext({ viewport: viewportSizes[viewportName], deviceScaleFactor: 1 });
const page = await context.newPage();
const errors = [];
page.on('pageerror', error => errors.push(String(error)));
page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
await page.goto('http://127.0.0.1:4179/', { waitUntil: 'networkidle' });
const captures = [];
async function capture(name) {
  await page.waitForTimeout(200);
  const file = `${out}/${name}-${viewportName}.png`;
  await page.screenshot({ path: file });
  captures.push({ name, file: file.slice(root.length + 1), view: await page.locator('#app').getAttribute('data-view') });
}
async function click(choice) {
  const locator = page.locator(`[data-choice="${choice}"]`).first();
  if (!(await locator.count())) throw new Error(`Missing active control: ${choice}`);
  if (await locator.isDisabled()) throw new Error(`Control is disabled: ${choice}`);
  await locator.click();
}

await capture('home');
await click('new-campaign');
await click('scene-class:paladin');
await click('scene-enter-valley');
await capture('kingdom');
await click('nav:adventure');
await capture('adventure-town');
await click('enter-adventure');
await capture('adventure-map');
const initialState = await page.evaluate(() => window.rebornSnapshot());
const openCells = await page.locator('[data-adventure-cell][data-open="1"]').evaluateAll(nodes => nodes.map(node => node.getAttribute('data-adventure-cell')));
const mapState = {
  snapshotKeys: Object.keys(initialState || {}),
  adventure: initialState?.adventure || null,
  openCellCount: openCells.length,
  openCells,
};
assert.equal(initialState?.adventure?.atTown, false, 'leaving town starts the natural valley journey');
assert.ok(openCells.includes('9,8'), 'the adjacent eastern valley cell is open');
const movesBefore = initialState.adventure.moves;
await page.locator('[data-adventure-cell="9,8"]').click();
await page.waitForTimeout(100);
const previewText = await page.locator('#scene-ui.game-status').innerText();
assert.match(previewText, /Confirm to travel/);
await capture('adventure-route-preview');
const confirm = page.locator('#dock [data-choice="confirm-route"]');
assert.equal(await confirm.count(), 1, 'the route confirmation is exposed in the action dock');
assert.equal(await confirm.isDisabled(), false, 'the one-step route is affordable');
await confirm.click();
await page.waitForTimeout(300);
const travelled = await page.evaluate(() => window.rebornSnapshot());
assert.equal(travelled.adventure.x, 9, 'confirming travel commits the route destination');
assert.equal(travelled.adventure.y, 8);
assert.equal(travelled.adventure.moves, movesBefore - 1, 'the route spends exactly its one movement point');
assert.ok(travelled.adventure.visited.includes('9,8'), 'the destination is recorded as discovered');
await capture('adventure-after-travel');
mapState.afterOneStep = travelled.adventure;

assert.ok(openCells.includes('10,5'), 'the mine guard cell is open');
await page.locator('[data-adventure-cell="10,5"]').click();
await page.waitForTimeout(100);
const guardPreview = await page.locator('#scene-ui.game-status').innerText();
assert.match(guardPreview, /Confirm to travel/);
await capture('adventure-guard-route-preview');
await page.locator('#dock [data-choice="confirm-route"]').click();
await page.waitForTimeout(200);
const pending = await page.evaluate(() => window.rebornSnapshot());
assert.equal(pending.adventure.pendingEncounter?.status, 'UNRESOLVED');
assert.deepEqual(pending.adventure.pendingEncounter?.cell, [10, 5]);
await click('begin-encounter');
await page.waitForTimeout(300);
await capture('tactical-guard');
const battleBeforeAuto = await page.evaluate(() => window.rebornSnapshot());
const auto = page.locator('#dock [data-choice="auto"]');
assert.equal(await auto.count(), 1, 'Auto is exposed as an explicit tactical action');
assert.equal(await auto.isDisabled(), false, 'Auto is available on the player turn');
await auto.click();
await page.waitForTimeout(500);
const battleAfterAuto = await page.evaluate(() => window.rebornSnapshot());
assert.ok(battleAfterAuto.battle?.pendingSettlement, 'the legal auto resolver finishes and records a battle result');
await capture('tactical-result-before-apply');
assert.ok(battleAfterAuto.battle?.outcome?.winner, 'the resolved encounter records its winner');
await click('result:tactical');
await page.waitForTimeout(300);
const settled = await page.evaluate(() => window.rebornSnapshot());
assert.equal(settled.battle, null, 'the result action settles the campaign battle');
if (battleAfterAuto.battle.outcome.winner === 'p') {
  assert.equal(settled.adventure.pendingEncounter, null, 'victory resolves the guard encounter');
  assert.ok(settled.adventure.resolvedGuards.includes('10,5'));
} else {
  assert.equal(settled.adventure.pendingEncounter?.status, 'UNRESOLVED', 'non-victory leaves the guard open for a later return');
}
await capture('tactical-result-settled');
const settledRevision = settled.revision;
await page.waitForTimeout(600);
await page.reload({ waitUntil: 'networkidle' });
await page.waitForTimeout(500);
const afterReload = await page.evaluate(() => window.rebornSnapshot());
assert.equal(afterReload.id, settled.id, 'reload restores the same campaign identity');
assert.ok(afterReload.revision >= settledRevision, 'reload restores at least the settled campaign revision');
assert.equal(afterReload.battle, null, 'reload does not revive a settled battle');
assert.deepEqual(afterReload.adventure.resolvedGuards, settled.adventure.resolvedGuards,
  'the guard result stays settled after a real browser reload');
assert.deepEqual(afterReload.army.map(stack => [stack.id, stack.count]), settled.army.map(stack => [stack.id, stack.count]),
  'battle losses and retained army IDs survive reload');
await capture('settled-campaign-after-reload');
mapState.pendingEncounter = pending.adventure.pendingEncounter;
mapState.battleBeforeAuto = { stacks: battleBeforeAuto.battle?.stacks?.length, status: battleBeforeAuto.battle?.status };
mapState.battleAfterAuto = { winner: battleAfterAuto.battle?.outcome?.winner, status: battleAfterAuto.battle?.status, pendingSettlement: battleAfterAuto.battle?.pendingSettlement };
mapState.afterSettlement = { battle: settled.battle, adventure: settled.adventure, army: settled.army.map(stack => ({ id: stack.id, count: stack.count })) };
mapState.afterReload = { id: afterReload.id, revision: afterReload.revision, battle: afterReload.battle, adventure: afterReload.adventure, army: afterReload.army.map(stack => ({ id: stack.id, count: stack.count })) };

const result = { recordedAt: new Date().toISOString(), url: page.url(), captures, mapState, errors };
await fs.writeFile(`${out}/natural-run.json`, JSON.stringify(result, null, 2));
console.log(JSON.stringify(result, null, 2));
await context.close();
await browser.close();
