import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import worlds from '../../../src/data/adventure-worlds.json' with { type: 'json' };
import { rates } from '../../../src/core/campaign.js';

const root = process.cwd();
const out = path.join(root, 'qa/game-completion-20261020/visual-review/m26-q6-endless-claim-live-20261020');
await fs.mkdir(out, { recursive: true });
const report = {
  recordedAt: new Date().toISOString(),
  classification: 'NATURAL_UI_ENDLESS_TEN_WAVES_QUEST_CLAIM_RELOAD',
  journey: 'fresh campaign -> War -> prepare Endless -> start paused -> deploy hero and ranged army -> use visible 2x control -> survive ten waves -> settle natural defeat -> claim Q6 -> save/reload and verify one-time payout',
  note: 'Campaign setup, defense deployment, speed selection, and claim use visible game controls. No campaign, defense, wave, or resource state is injected.',
  errors: [],
  failedResponses: [],
  progress: [],
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

async function waitFor(predicate, label, timeout = 15000) {
  const end = Date.now() + timeout;
  while (Date.now() < end) {
    const value = await read();
    if (predicate(value)) return value;
    await page.waitForTimeout(100);
  }
  throw new Error(`Timed out waiting for ${label}`);
}

async function capture(name) {
  const file = path.join(out, `${name}-825x375.png`);
  await page.screenshot({ path: file });
  report.captures.push(path.relative(root, file));
}

async function openObjectives() {
  const current = await read();
  if (current.view !== 'story') {
    await click('#context');
    await click('[data-choice="menu:story"]');
    await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'story');
  }
  const rival = page.locator('#scene-ui [data-choice^="journal-rival:"]').first();
  if (await rival.count()) await rival.click();
  await click('#scene-ui [data-choice="journal:quests"]');
  await page.locator('#scene-ui [data-quest-id="q6"]').waitFor({ state: 'visible', timeout: 10000 });
}

try {
  await page.goto('http://127.0.0.1:4179/?audit=m26-q6-endless', { waitUntil: 'networkidle' });
  await click('[data-choice="new-campaign"]');
  await click(`[data-choice="campaign-world:${worlds[10].id}"]`);
  await click('[data-choice="begin-selected-world"]');
  await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'hero');
  await click('[data-choice="scene-class:knight"]');
  await click('[data-choice="scene-enter-valley"]');
  const start = await waitFor(value => value.state?.age === 0, 'fresh Stone campaign');
  report.campaignId = start.state.id;
  report.worldId = start.state.adventureWorldId;

  await click('[data-choice="nav:war"]');
  await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'war');
  await click('#scene-ui [data-choice="start-endless"]');
  await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'defense');
  let state = (await read()).state;
  assert.equal(state.defense, null, 'choosing Endless enters preparation without starting an attack');
  await capture('endless-preparation');
  await click('#dock [data-choice="inspect:defense"]');
  await click('#choices [data-choice="start-endless"]');
  const session = await waitFor(value => value.state?.defense?.status === 'ACTIVE' && value.state.defense.paused, 'paused Endless session');
  report.start = { practice: session.state.defense.practice, paused: session.state.defense.paused, towers: session.state.defense.towers.map(tower => tower.fam) };
  assert.equal(session.state.defense.practice, 'endless');
  await capture('endless-start-paused');

  await click('#dock [data-choice="inspect:defense"]');
  await click('#choices [data-choice="deploy-hero"]');
  const ranged = session.state.army.find(stack => stack.type === 'ranged');
  assert.ok(ranged, 'fresh campaign has its ranged role stack');
  await click(`#choices [data-choice="deploy-army:${ranged.id}"]`);
  const deployed = await waitFor(value => value.state?.defense?.heroDeployed && value.state.defense.armyDeployed, 'hero and ranged stack deployment');
  assert.equal(deployed.state.defense.paused, true, 'deployment does not spend assault time');
  await capture('endless-deployed-paused');
  await click('[data-choice="defense-speed"]');
  await waitFor(value => value.state?.defense?.speed === 2, 'visible speed control selects 2x');
  await click('[data-choice="defense-pause"]');
  await waitFor(value => value.state?.defense?.paused === false, 'visible Resume control starts the assault');
  report.speed = 2;

  let lastWave = 0;
  let lastCapture = 0;
  const deadline = Date.now() + 12 * 60 * 1000;
  while (Date.now() < deadline) {
    const current = (await read()).state;
    const defense = current.defense;
    if (!defense) throw new Error('Endless session ended before its natural result was settled');
    if (defense.clearedWaves !== lastWave) {
      lastWave = defense.clearedWaves;
      const progress = { clearedWaves: defense.clearedWaves, scheduledWaves: defense.waves, core: defense.core, elapsedSimSeconds: defense.time, towers: defense.towers.map(tower => ({ family: tower.fam, hp: tower.hp })), army: defense.army ? { role: defense.army.role, hp: defense.army.hp } : null };
      report.progress.push(progress);
      console.log(JSON.stringify({ checkpoint: 'wave', ...progress }));
      if (defense.clearedWaves >= 1 && defense.clearedWaves !== lastCapture) {
        lastCapture = defense.clearedWaves;
        if (defense.clearedWaves === 1 || defense.clearedWaves === 3 || defense.clearedWaves === 6 || defense.clearedWaves === 9 || defense.clearedWaves === 10) await capture(`endless-wave-${defense.clearedWaves}`);
      }
    }
    if (defense.pendingSettlement) break;
    await page.waitForTimeout(500);
  }
  state = (await read()).state;
  assert.ok(state.defense?.pendingSettlement, 'Endless ends naturally on core loss and opens its result');
  assert.equal(state.defense.winner, 'e');
  const clearedWaves = state.defense.clearedWaves;
  report.result = { winner: state.defense.winner, clearedWaves, core: state.defense.core, status: state.defense.status };
  assert.ok(clearedWaves >= 10, `natural defense must survive at least ten complete waves; reached ${clearedWaves}`);
  await capture('endless-result');
  await click('[data-choice="settle-defense"]');
  const settled = await waitFor(value => value.state?.defense == null, 'settle Endless record');
  assert.ok(Object.entries(settled.state.story.flags).some(([key, value]) => key.startsWith('endless:') && value >= 10), 'settlement records a ten-wave best');

  await openObjectives();
  await page.locator('#scene-ui [data-quest-id="q6"]').evaluate(element => element.scrollIntoView({ block: 'center', inline: 'nearest' }));
  const ready = await page.evaluate(() => {
    const state = window.rebornSnapshot();
    const card = document.querySelector('#scene-ui [data-quest-id="q6"]');
    const claim = card?.querySelector('[data-choice="journal-claim:q6"]');
    return { quest: state.quests.q6, progress: card?.querySelector('.quest-progress')?.textContent?.trim() || '', status: card?.querySelector('p')?.textContent?.trim() || '', reward: card?.querySelector('.quest-reward')?.innerText?.replace(/\s+/g, ' ').trim() || '', claimPresent: Boolean(claim), claimDisabled: claim?.disabled ?? null };
  });
  assert.equal(ready.progress, `${clearedWaves} / 10 Endless waves`);
  assert.equal(ready.status, 'Ready to claim');
  assert.match(ready.reward, /500/);
  assert.match(ready.reward, /300/);
  assert.equal(ready.claimPresent, true);
  assert.equal(ready.claimDisabled, false);
  await capture('q6-ready');
  const before = (await read()).state;
  await click('#scene-ui [data-choice="journal-claim:q6"]');
  const after = await waitFor(value => value.state?.quests.q6.claimed, 'claim Q6');
  const elapsed = after.state.clock - before.clock;
  const income = rates(before);
  const payout = Object.fromEntries(['gold', 'stone'].map(resource => [resource,
    after.state.resources[resource] - before.resources[resource] - income[resource] * elapsed / 1000]));
  assert.ok(Math.abs(payout.gold - 500) < 1e-6, 'Q6 grants exactly 500 gold after passive income');
  assert.ok(Math.abs(payout.stone - 300) < 1e-6, 'Q6 grants exactly 300 stone after passive income');
  await page.waitForFunction(id => {
    const current = window.rebornSnapshot();
    const head = window.rebornCommittedHead();
    return current?.id === id && current.quests.q6.claimed && head?.campaignId === id && head.revision >= current.revision;
  }, report.campaignId, { timeout: 10000 });
  await capture('q6-claimed');
  await page.reload({ waitUntil: 'networkidle' });
  await page.waitForFunction(id => window.rebornSnapshot()?.id === id, report.campaignId, { timeout: 10000 });
  await openObjectives();
  const reload = (await read()).state;
  const reloadElapsed = reload.clock - after.state.clock;
  const repeat = Object.fromEntries(['gold', 'stone'].map(resource => [resource,
    reload.resources[resource] - after.state.resources[resource] - income[resource] * reloadElapsed / 1000]));
  assert.equal(reload.quests.q6.claimed, true);
  assert.ok(Math.abs(repeat.gold) < 1e-6, 'reload does not pay Q6 gold twice');
  assert.ok(Math.abs(repeat.stone) < 1e-6, 'reload does not pay Q6 stone twice');
  report.ready = ready;
  report.payout = payout;
  report.repeatPayoutAfterReload = repeat;
  report.errors = [...new Set(report.errors)];
  assert.deepEqual(report.errors, []);
  assert.deepEqual(report.failedResponses, []);
  report.passed = true;
} catch (error) {
  report.passed = false;
  report.failure = String(error);
  report.debug = await page.evaluate(() => ({
    view: document.querySelector('#app')?.dataset.view,
    paused: window.rebornSnapshot()?.defense?.paused,
    speed: window.rebornSnapshot()?.defense?.speed,
    recentActions: (window.rebornActions || []).slice(-8),
    controls: [...document.querySelectorAll('[data-choice="defense-pause"], [data-choice="defense-speed"]')].map(node => {
      const rect = node.getBoundingClientRect();
      const hit = document.elementFromPoint(rect.x + rect.width / 2, rect.y + rect.height / 2);
      return { choice: node.dataset.choice, label: node.getAttribute('aria-label'), text: node.textContent.trim(), parent: node.parentElement?.id || node.parentElement?.className, disabled: node.disabled, bounds: [rect.x, rect.y, rect.width, rect.height], centerHit: hit?.closest('[data-choice]')?.dataset.choice || hit?.tagName };
    }),
    choices: [...document.querySelector('#choices')?.children || []].map(node => {
      const rect = node.getBoundingClientRect();
      return { choice: node.dataset?.choice || '', text: node.textContent.trim().slice(0, 80), bounds: [rect.x, rect.y, rect.width, rect.height].map(value => Math.round(value)), visible: rect.width > 0 && rect.height > 0 };
    }),
    notification: document.querySelector('#notification-text')?.textContent || '',
  }));
} finally {
  report.recordedAt = new Date().toISOString();
  await fs.writeFile(path.join(out, 'report.json'), JSON.stringify(report, null, 2) + '\n');
  await browser.close();
}

if (!report.passed) throw new Error(report.failure);
console.log(JSON.stringify({ passed: report.passed, campaignId: report.campaignId, start: report.start, result: report.result, ready: report.ready, payout: report.payout, repeatPayoutAfterReload: report.repeatPayoutAfterReload, captures: report.captures, errors: report.errors, failedResponses: report.failedResponses }, null, 2));
