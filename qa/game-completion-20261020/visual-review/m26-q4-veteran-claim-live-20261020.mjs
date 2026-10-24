import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import worlds from '../../../src/data/adventure-worlds.json' with { type: 'json' };
import { rates } from '../../../src/core/campaign.js';

const root = process.cwd();
const out = path.join(root, 'qa/game-completion-20261020/visual-review/m26-q4-veteran-claim-live-20261020');
await fs.mkdir(out, { recursive: true });
const report = {
  recordedAt: new Date().toISOString(),
  classification: 'NATURAL_UI_VETERAN_RANK_QUEST_CLAIM_RELOAD',
  journey: 'fresh campaign -> visible War menu -> repeat campaign duels with normal Tactical Auto action until a stack reaches Veteran -> inspect and claim Q4 -> save/reload and verify one-time payout',
  note: 'All battles and claims use visible game controls. No campaign state, stack XP, or resources are injected.',
  battles: [],
  errors: [],
  failedResponses: [],
  captures: [],
};

const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
const context = await browser.newContext({ viewport: { width: 825, height: 375 }, deviceScaleFactor: 1 });
const page = await context.newPage();
page.on('pageerror', error => report.errors.push(String(error)));
page.on('console', message => { if (message.type() === 'error') report.errors.push(message.text()); });
page.on('response', response => { if (response.status() >= 400) report.failedResponses.push({ status: response.status(), url: response.url() }); });
const read = () => page.evaluate(() => ({ state: window.rebornSnapshot(), view: document.querySelector('#app')?.dataset.view }));

async function click(selector) {
  const target = page.locator(selector).first();
  await target.waitFor({ state: 'visible', timeout: 10000 });
  assert.equal(await target.isDisabled(), false, `${selector} is enabled`);
  await target.click();
}

async function waitForState(predicate, label, timeout = 20000) {
  const end = Date.now() + timeout;
  while (Date.now() < end) {
    const value = await read();
    if (value.state && predicate(value.state, value.view)) return value;
    await page.waitForTimeout(100);
  }
  throw new Error(`Timed out waiting for ${label}`);
}

async function openObjectives() {
  if (await read().then(value => value.view) !== 'story') {
    await click('#context');
    await click('[data-choice="menu:story"]');
    await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'story');
  }
  const rival = page.locator('#scene-ui [data-choice^="journal-rival:"]').first();
  if (await rival.count()) await rival.click();
  await click('#scene-ui [data-choice="journal:quests"]');
  await page.locator('#scene-ui [data-quest-id="q4"]').waitFor({ state: 'visible', timeout: 10000 });
}

try {
  await page.goto('http://127.0.0.1:4179/?audit=m26-q4-veteran', { waitUntil: 'networkidle' });
  await click('[data-choice="new-campaign"]');
  await click(`[data-choice="campaign-world:${worlds[10].id}"]`);
  await click('[data-choice="begin-selected-world"]');
  await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'hero');
  await click('[data-choice="scene-class:knight"]');
  await click('[data-choice="scene-enter-valley"]');
  const start = await waitForState(state => state.age === 0, 'fresh Stone campaign');
  report.campaignId = start.state.id;
  report.worldId = start.state.adventureWorldId;
  assert.equal(start.state.quests.q4.claimed, false);

  for (let index = 1; index <= 8; index += 1) {
    await click('[data-choice="nav:war"]');
    await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'war');
    await click('[data-choice="start-duel"]');
    await waitForState(state => state.battle?.status === 'ACTIVE', `campaign duel ${index} starts`);
    const auto = page.locator('[data-choice="auto"]:visible').first();
    await auto.waitFor({ state: 'visible', timeout: 10000 });
    await auto.click();
    const result = await waitForState(state => state.battle?.pendingSettlement === true, `campaign duel ${index} resolves`);
    const winner = result.state.battle.outcome?.winner;
    const battleXp = result.state.battle.stacks.filter(stack => stack.campaignId)
      .map(stack => ({ campaignId: stack.campaignId, dealt: stack.dealt || 0, survivors: stack.count }));
    assert.equal(winner, 'p', `campaign duel ${index} is won through normal Tactical Auto`);
    await click('[data-choice="result:tactical"]');
    const settled = await waitForState(state => state.battle == null, `campaign duel ${index} settles`);
    const rows = settled.state.army.map(stack => ({ id: stack.id, type: stack.type, kind: stack.kind, count: stack.count, xp: stack.xp, rank: stack.rank }));
    report.battles.push({ index, winner, battleXp, armyAfter: rows });
    if (settled.state.army.some(stack => stack.rank >= 1)) break;
  }

  const ranked = (await read()).state;
  const veteran = ranked.army.find(stack => stack.rank >= 1);
  assert.ok(veteran, 'natural campaign battles promote at least one surviving stack to Veteran');
  await openObjectives();
  await page.locator('#scene-ui [data-quest-id="q4"]').evaluate(element => element.scrollIntoView({ block: 'center', inline: 'nearest' }));
  const ready = await page.evaluate(() => {
    const state = window.rebornSnapshot();
    const card = document.querySelector('#scene-ui [data-quest-id="q4"]');
    const claim = card?.querySelector('[data-choice="journal-claim:q4"]');
    return {
      quest: state.quests.q4,
      progress: card?.querySelector('.quest-progress')?.textContent?.trim() || '',
      status: card?.querySelector('p')?.textContent?.trim() || '',
      reward: card?.querySelector('.quest-reward')?.innerText?.replace(/\s+/g, ' ').trim() || '',
      claimPresent: Boolean(claim),
      claimDisabled: claim?.disabled ?? null,
    };
  });
  assert.match(ready.progress, /1 \/ 1 Veteran stack/);
  assert.equal(ready.status, 'Ready to claim');
  assert.match(ready.reward, /250/);
  assert.equal(ready.claimPresent, true);
  assert.equal(ready.claimDisabled, false);
  const readyCapture = path.join(out, 'q4-ready-825x375.png');
  await page.screenshot({ path: readyCapture });
  report.captures.push(path.relative(root, readyCapture));

  const before = (await read()).state;
  await click('#scene-ui [data-choice="journal-claim:q4"]');
  const after = await waitForState(state => state.quests.q4.claimed, 'claim Q4');
  const elapsed = after.state.clock - before.clock;
  const income = rates(before);
  const payout = after.state.resources.gold - before.resources.gold - income.gold * elapsed / 1000;
  assert.ok(Math.abs(payout - 250) < 1e-6, `Q4 grants exactly 250 gold after passive income; got ${payout}`);
  await page.setViewportSize({ width: 1280, height: 720 });
  await page.waitForTimeout(150);
  const claimedCapture = path.join(out, 'q4-claimed-1280x720.png');
  await page.screenshot({ path: claimedCapture });
  report.captures.push(path.relative(root, claimedCapture));
  await page.waitForFunction(id => {
    const state = window.rebornSnapshot();
    const head = window.rebornCommittedHead();
    return state?.id === id && state.quests.q4.claimed && head?.campaignId === id && head.revision >= state.revision;
  }, report.campaignId, { timeout: 10000 });
  await page.reload({ waitUntil: 'networkidle' });
  await page.waitForFunction(id => window.rebornSnapshot()?.id === id, report.campaignId, { timeout: 10000 });
  await openObjectives();
  const reload = (await read()).state;
  const reloadElapsed = reload.clock - after.state.clock;
  const repeatPayout = reload.resources.gold - after.state.resources.gold - income.gold * reloadElapsed / 1000;
  assert.equal(reload.quests.q4.claimed, true);
  assert.ok(Math.abs(repeatPayout) < 1e-6, 'reload does not pay Q4 twice');
  report.veteran = veteran;
  report.ready = ready;
  report.payout = payout;
  report.repeatPayoutAfterReload = repeatPayout;
  report.errors = [...new Set(report.errors)];
  assert.deepEqual(report.errors, []);
  assert.deepEqual(report.failedResponses, []);
  report.passed = true;
} catch (error) {
  report.passed = false;
  report.failure = String(error);
} finally {
  report.recordedAt = new Date().toISOString();
  await fs.writeFile(path.join(out, 'report.json'), JSON.stringify(report, null, 2) + '\n');
  await browser.close();
}

if (!report.passed) throw new Error(report.failure);
console.log(JSON.stringify({ passed: report.passed, campaignId: report.campaignId, battles: report.battles.length, veteran: report.veteran, ready: report.ready, payout: report.payout, repeatPayoutAfterReload: report.repeatPayoutAfterReload, captures: report.captures, errors: report.errors }, null, 2));
