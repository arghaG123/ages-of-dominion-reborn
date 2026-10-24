import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';

const root = process.cwd();
const sizes = {
  '825x375': { width: 825, height: 375 },
  '1280x720': { width: 1280, height: 720 },
};
const sizeName = process.argv[2] || '825x375';
if (!sizes[sizeName]) throw new Error(`Unsupported viewport: ${sizeName}`);
const out = path.join(root, 'qa/game-completion-20261020/visual-review/tactical-spell-live');
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
async function capture(name) {
  const file = path.join(out, `${name}-${sizeName}.png`);
  await page.screenshot({ path: file });
  return path.relative(root, file);
}

await click('new-campaign');
await click('scene-class:knight');
await click('scene-enter-valley');
await click('nav:adventure');
await click('enter-adventure');
await page.locator('[data-adventure-cell="9,8"]').click();
await click('confirm-route');
await page.waitForTimeout(250);
await page.locator('[data-adventure-cell="10,5"]').click();
await click('confirm-route');
await page.waitForTimeout(250);
await click('begin-encounter');
await page.waitForTimeout(350);
const before = await page.evaluate(() => window.rebornSnapshot());
assert.equal(before.battle?.status, 'ACTIVE', 'natural guard encounter is active');
const spellIntent = page.locator('#dock [data-choice="intent:spell"]');
assert.equal(await spellIntent.count(), 1, 'the spell action is present in the battle dock');
assert.equal(await spellIntent.isDisabled(), false, 'the natural player turn has a legal spell');
await spellIntent.click();
await page.waitForTimeout(150);
const offered = await page.locator('#choices [data-choice^="spellcast:"]').evaluateAll(nodes => nodes.map(node => {
  const rect = node.getBoundingClientRect();
  return {
    id: node.dataset.choice,
    name: node.getAttribute('aria-label') || node.innerText.trim(),
    rect: [rect.x, rect.y, rect.width, rect.height].map(value => Math.round(value)),
  };
}));
assert.ok(offered.length > 0, 'spell choices are exposed for the real battle');
const magicArrow = page.locator('#choices [data-choice^="spellcast:"]').filter({ hasText: 'Magic Arrow' }).first();
assert.equal(await magicArrow.count(), 1, 'Magic Arrow can target the visible guard');
const panel = page.locator('#panel');
await page.locator('#choices [data-choice^="spellcast:"]').last().scrollIntoViewIfNeeded();
const lastTargetProbe = await page.evaluate(() => {
  const panel = document.querySelector('#panel');
  const target = [...document.querySelectorAll('#choices [data-choice^="spellcast:"]')].at(-1);
  const panelRect = panel.getBoundingClientRect();
  const rect = target.getBoundingClientRect();
  return {
    name: target.getAttribute('aria-label') || target.innerText.trim(),
    scrollHeight: panel.scrollHeight,
    clientHeight: panel.clientHeight,
    scrollTop: panel.scrollTop,
    rect: [rect.x, rect.y, rect.width, rect.height].map(value => Math.round(value)),
    panelRect: [panelRect.x, panelRect.y, panelRect.width, panelRect.height].map(value => Math.round(value)),
    hitTarget: document.elementFromPoint(rect.x + rect.width / 2, rect.y + rect.height / 2)?.closest('[data-choice]')?.dataset.choice || null,
  };
});
assert.ok(lastTargetProbe.rect[1] >= lastTargetProbe.panelRect[1], 'the final spell target scrolls below the inspector header');
assert.ok(lastTargetProbe.rect[1] + lastTargetProbe.rect[3] <= lastTargetProbe.panelRect[1] + lastTargetProbe.panelRect[3], 'the final spell target fits inside the scrollable inspector');
assert.ok(lastTargetProbe.hitTarget?.startsWith('spellcast:'), 'the final spell target owns its touch center');
const spellPanelBottom = await capture('spell-targets-bottom');
await panel.evaluate(node => { node.scrollTop = 0; });
const spellPanel = await capture('spell-targets');
const magicArrowNow = page.locator('#choices [data-choice^="spellcast:"]').filter({ hasText: 'Magic Arrow' }).first();
const targetChoice = await magicArrowNow.getAttribute('data-choice');
await magicArrowNow.click();
await page.waitForTimeout(500);
const after = await page.evaluate(() => window.rebornSnapshot());
assert.equal(after.battle?.status, 'ACTIVE', 'casting does not settle or discard the battle');
const cast = after.battle.log?.findLast?.(entry => entry.type === 'spell')
  || [...(after.battle.log || [])].reverse().find(entry => entry.type === 'spell');
assert.ok(cast, 'the committed battle log records the spell');
assert.equal(cast.id, 'arrow', 'the selected Magic Arrow spell is recorded by its stable data ID');
assert.ok(after.battle.mana < before.battle.mana, 'mana is spent exactly through the visible cast action');
const spellResult = await capture('spell-cast');
assert.deepEqual(errors, [], 'the UI journey produces no browser errors');
const report = {
  recordedAt: new Date().toISOString(),
  viewport: sizeName,
  journey: 'fresh campaign -> Knight -> Valley -> legal travel -> natural guard battle -> Magic Arrow',
  battle: {
    statusBefore: before.battle.status,
    statusAfter: after.battle.status,
    activeActorId: before.battle.queue?.find(id => {
      const stack = before.battle.stacks.find(item => item.id === id);
      return stack && !stack.dead && !stack.acted;
    }) || null,
    manaBefore: before.battle.mana,
    manaAfter: after.battle.mana,
    cast,
  },
  targetChoice,
  lastTargetProbe,
  offeredSpellTargets: offered,
  captures: { spellPanel, spellPanelBottom, spellResult },
  errors,
};
await fs.writeFile(path.join(out, `tactical-spell-${sizeName}.json`), JSON.stringify(report, null, 2));
console.log(JSON.stringify(report, null, 2));
await context.close();
await browser.close();
