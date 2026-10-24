import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
import path from 'node:path';

const root = process.cwd();
const out = path.join(root, 'qa/game-completion-20261022/visual-review/tactical-skirmish-natural-live-20261022-run01');
await fs.mkdir(out, { recursive: true });
const report = { recordedAt: new Date().toISOString(), classification: 'NATURAL_UI_PRACTICE_SKIRMISH_BROWSER_JOURNEY', viewport: '1280x720', url: 'http://127.0.0.1:4179/?audit=1', errors: [], failedResponses: [] };
const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
const context = await browser.newContext({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1 });
const page = await context.newPage();
page.on('pageerror', error => report.errors.push(String(error)));
page.on('console', message => { if (message.type() === 'error') report.errors.push(message.text()); });
page.on('response', response => { if (response.status() >= 400) report.failedResponses.push({ status: response.status(), url: response.url() }); });
const click = async choice => {
  const control = page.locator(`[data-choice="${choice}"]:visible`).first();
  await control.waitFor({ state: 'visible', timeout: 10000 });
  if (await control.isDisabled()) throw new Error(`Disabled UI choice: ${choice}`);
  await control.click();
};
const state = async () => page.evaluate(() => structuredClone(window.rebornSnapshot()));
await page.goto(report.url, { waitUntil: 'networkidle' });
await click('new-campaign');
await click('campaign-world:astral-peaks');
await click('begin-selected-world');
await click('scene-class:knight');
await click('scene-enter-valley');
await page.waitForFunction(() => window.rebornSnapshot()?.story?.flags?.enteredValley === true, null, { timeout: 10000 });
const campaignId = await page.evaluate(() => window.rebornSnapshot().id);
const preBattle = await state();
await click('nav:war');
await click('start-skirmish');
await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'tactical' && window.rebornSnapshot()?.battle?.practice === 'skirmish', null, { timeout: 10000 });
report.skirmishStart = await page.evaluate(() => ({
  campaign: window.rebornSnapshot().id,
  view: document.querySelector('#app')?.dataset.view,
  battle: structuredClone(window.rebornSnapshot().battle),
  visibleChoices: [...document.querySelectorAll('[data-choice]')].filter(node => node.getClientRects().length).map(node => ({ id: node.dataset.choice, text: node.textContent.trim(), disabled: node.disabled })),
}));
await page.screenshot({ path: path.join(out, 'skirmish-start-1280x720.png') });
const battleBeforeMove = (await state()).battle;
const activeId = battleBeforeMove.queue.find(id => { const stack = battleBeforeMove.stacks.find(item => item.id === id); return stack && !stack.dead && !stack.acted; });
const active = battleBeforeMove.stacks.find(stack => stack.id === activeId);
report.firstActor = { id: activeId, side: active.side, position: [active.x, active.y] };
await click('intent:move');
await click('inspect:tactical');
await page.waitForFunction(() => document.querySelector('[data-choice^="move:"]'), null, { timeout: 5000 });
const moves = await page.locator('[data-choice^="move:"]:visible').evaluateAll(nodes => nodes.filter(node => !node.disabled).map(node => node.dataset.choice.slice(5).split(',').map(Number)));
if (!moves.length) throw new Error('No enabled legal move choices were rendered');
const enemyStacks = battleBeforeMove.stacks.filter(stack => stack.side === 'e' && !stack.dead);
const targetMove = moves.map(cell => ({ cell, distance: Math.min(...enemyStacks.map(enemy => Math.max(Math.abs(cell[0] - enemy.x), Math.abs(cell[1] - enemy.y)))) })).sort((a, b) => a.distance - b.distance)[0].cell;
await click(`move:${targetMove[0]},${targetMove[1]}`);
await page.waitForFunction(({ id, cell }) => { const stack = window.rebornSnapshot()?.battle?.stacks.find(item => item.id === id); return stack?.x === cell[0] && stack?.y === cell[1]; }, { id: activeId, cell: targetMove }, { timeout: 10000 });
report.manualMove = { from: [active.x, active.y], to: targetMove, legalMoveCount: moves.length, battle: (await state()).battle };
await page.screenshot({ path: path.join(out, 'skirmish-after-legal-move-1280x720.png') });
report.afterMoveChoices = await page.locator('[data-choice]:visible').evaluateAll(nodes => nodes.map(node => ({ id: node.dataset.choice, text: node.textContent.trim(), disabled: node.disabled })));
const auto = page.locator('[data-choice="auto"]:visible').first();
if (await auto.count()) {
  await auto.click();
  await page.waitForFunction(() => window.rebornSnapshot()?.battle?.pendingSettlement, null, { timeout: 20000 });
} else {
  report.remainingControlChoices = report.afterMoveChoices.map(item => item.id);
  throw new Error('Tactical screen did not expose Auto after the manual turn');
}
const battleResult = await state();
report.result = { outcome: battleResult.battle.outcome, winner: battleResult.battle.outcome?.winner, pendingSettlement: battleResult.battle.pendingSettlement, round: battleResult.battle.round };
await page.screenshot({ path: path.join(out, 'skirmish-result-before-settlement-1280x720.png') });
await click('result:tactical');
await page.waitForFunction(() => !window.rebornSnapshot()?.battle && document.querySelector('#app')?.dataset.view === 'war', null, { timeout: 10000 });
const postSettlement = await state();
report.settlement = {
  battleClosed: !postSettlement.battle,
  practiceIsolation: JSON.stringify({ age: postSettlement.age, day: postSettlement.day, resources: postSettlement.resources, army: postSettlement.army, hero: postSettlement.hero, inventory: postSettlement.inventory, adventure: postSettlement.adventure }) === JSON.stringify({ age: preBattle.age, day: preBattle.day, resources: preBattle.resources, army: preBattle.army, hero: preBattle.hero, inventory: preBattle.inventory, adventure: preBattle.adventure }),
  before: { age: preBattle.age, day: preBattle.day, resources: preBattle.resources, army: preBattle.army },
  after: { age: postSettlement.age, day: postSettlement.day, resources: postSettlement.resources, army: postSettlement.army },
};
await page.waitForFunction(expectedId => { const current = window.rebornSnapshot(); const head = window.rebornCommittedHead(); return current?.id === expectedId && head?.campaignId === expectedId && head.revision >= current.revision; }, campaignId, { timeout: 10000 });
await page.reload({ waitUntil: 'networkidle' });
await page.waitForFunction(expectedId => { const current = window.rebornSnapshot(); const head = window.rebornCommittedHead(); return current?.id === expectedId && !current.battle && head?.campaignId === expectedId && head.revision >= current.revision; }, campaignId, { timeout: 10000 });
report.reload = { campaignId: (await state()).id, battleClosed: !(await state()).battle, age: (await state()).age, day: (await state()).day };
report.errors = report.errors;
report.passed = report.skirmishStart.battle.stacks.some(stack => stack.side === 'p') && report.skirmishStart.battle.stacks.some(stack => stack.side === 'e') && report.firstActor.side === 'p' && report.manualMove.legalMoveCount > 0 && report.result.winner === 'p' && report.settlement.battleClosed && report.settlement.practiceIsolation && report.reload.battleClosed && report.errors.length === 0 && report.failedResponses.length === 0;
report.screenshots = ['skirmish-start-1280x720.png', 'skirmish-after-legal-move-1280x720.png', 'skirmish-result-before-settlement-1280x720.png'];
await fs.writeFile(path.join(out, 'report.json'), JSON.stringify(report, null, 2));
console.log(JSON.stringify({ passed: report.passed, firstActor: report.firstActor, manualMove: { from: report.manualMove.from, to: report.manualMove.to, legalMoveCount: report.manualMove.legalMoveCount }, result: report.result, settlement: report.settlement, reload: report.reload, errors: report.errors, failedResponses: report.failedResponses, output: path.relative(root, out) }, null, 2));
await context.close();
await browser.close();
