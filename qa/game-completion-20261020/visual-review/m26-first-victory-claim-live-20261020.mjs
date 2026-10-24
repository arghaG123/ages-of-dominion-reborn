import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import worlds from '../../../src/data/adventure-worlds.json' with { type: 'json' };
import { rates } from '../../../src/core/campaign.js';

const root = process.cwd();
const out = path.join(root, 'qa/game-completion-20261020/visual-review/m26-first-victory-claim-live-20261020');
await fs.mkdir(out, { recursive: true });
const report = {
  recordedAt: new Date().toISOString(),
  classification: 'NATURAL_UI_FIRST_VICTORY_QUEST_CLAIM_RELOAD',
  journey: 'new campaign -> visible War menu -> campaign duel -> win -> claim q1 -> reload and verify one-time reward',
  note: 'Campaign and battle actions use visible game controls. Auto-resolve is the normal in-game tactical action. No campaign state or resources are injected.',
  viewports: [],
  errors: [],
  failedResponses: [],
};

const browser = await chromium.launch({
  executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe',
  headless: true,
});

async function runAtViewport(size) {
  const context = await browser.newContext({ viewport: { width: size.width, height: size.height }, deviceScaleFactor: 1 });
  const page = await context.newPage();
  page.on('pageerror', error => report.errors.push({ viewport: size.name, error: String(error) }));
  page.on('console', message => { if (message.type() === 'error') report.errors.push({ viewport: size.name, error: message.text() }); });
  page.on('response', response => { if (response.status() >= 400) report.failedResponses.push({ viewport: size.name, status: response.status(), url: response.url() }); });
  const read = () => page.evaluate(() => window.rebornSnapshot());
  const click = async selector => {
    const button = page.locator(selector).first();
    await button.waitFor({ state: 'visible', timeout: 10000 });
    assert.equal(await button.isDisabled(), false, `${selector} is enabled`);
    await button.click();
  };
  const waitForState = async (predicate, label) => {
    await page.waitForFunction(predicate, null, { timeout: 25000 }).catch(error => { throw new Error(`${label}: ${error.message}`); });
    return read();
  };
  const openObjectives = async () => {
    await click('#context');
    await click('[data-choice="menu:story"]');
    await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'story');
    const rival = page.locator('#scene-ui [data-choice^="journal-rival:"]').first();
    if (await rival.count()) await rival.click();
    await click('#scene-ui [data-choice="journal:quests"]');
    await page.locator('#scene-ui [data-quest-id="q1"]').waitFor({ state: 'visible' });
  };

  try {
    await page.goto('http://127.0.0.1:4179/?audit=m26-first-victory', { waitUntil: 'networkidle' });
    await click('[data-choice="new-campaign"]');
    await click(`[data-choice="campaign-world:${worlds[10].id}"]`);
    await click('[data-choice="begin-selected-world"]');
    await click('[data-choice="scene-class:knight"]');
    await click('[data-choice="scene-enter-valley"]');
    const start = await waitForState(() => window.rebornSnapshot()?.age === 0, 'fresh Stone campaign');
    assert.equal(start.quests.q1.claimed, false);
    await click('[data-choice="nav:war"]');
    await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'war');
    await click('[data-choice="start-duel"]');
    await waitForState(() => window.rebornSnapshot()?.battle?.status === 'ACTIVE'
      && document.querySelector('#app')?.dataset.view === 'tactical', 'campaign duel started in Tactical');
    const auto = page.locator('[data-choice="auto"]:visible');
    if (await auto.count() !== 1) {
      const diagnostic = await page.evaluate(() => {
        const state = window.rebornSnapshot();
        const battle = state?.battle;
        const activeId = battle?.queue?.find(id => {
          const stack = battle.stacks.find(row => row.id === id);
          return stack && !stack.dead && !stack.acted;
        });
        return {
          view: document.querySelector('#app')?.dataset.view,
          activeId,
          activeStack: battle?.stacks?.find(row => row.id === activeId) ?? null,
          visibleChoices: [...document.querySelectorAll('#dock button, #choices button')]
            .filter(node => node.getBoundingClientRect().width > 0 && node.getBoundingClientRect().height > 0)
            .map(node => ({ id: node.dataset.choice, label: node.getAttribute('aria-label') || node.textContent.trim() })),
        };
      });
      await page.screenshot({ path: path.join(out, `q1-tactical-diagnostic-${size.name}.png`) });
      throw new Error(`Tactical has no visible Auto control: ${JSON.stringify(diagnostic)}`);
    }
    await auto.click();
    const battleResult = await waitForState(() => window.rebornSnapshot()?.battle?.pendingSettlement === true, 'duel victory');
    const winner = battleResult.battle.outcome?.winner;
    assert.equal(winner, 'p', 'the natural campaign duel ends in a player victory');
    await click('[data-choice="result:tactical"]');
    const settled = await waitForState(() => window.rebornSnapshot()?.battle == null, 'battle settlement');
    assert.ok(Object.entries(settled.story.flags).some(([key, value]) => key.startsWith('cleared:') && value === true), 'victory records the cleared encounter');
    await openObjectives();
    await page.locator('#scene-ui [data-quest-id="q1"]').evaluate(element => element.scrollIntoView({ block: 'center', inline: 'nearest' }));
    const ready = await page.evaluate(() => {
      const state = window.rebornSnapshot();
      const card = document.querySelector('#scene-ui [data-quest-id="q1"]');
      return {
        quest: state.quests.q1,
        progress: card?.querySelector('.quest-progress')?.textContent?.trim() || '',
        status: card?.querySelector('p')?.textContent?.trim() || '',
        reward: card?.querySelector('.quest-reward')?.innerText?.replace(/\s+/g, ' ').trim() || '',
        claim: Boolean(card?.querySelector('[data-choice="journal-claim:q1"]')),
        disabled: card?.querySelector('[data-choice="journal-claim:q1"]')?.disabled ?? null,
      };
    });
    assert.equal(ready.status, 'Ready to claim');
    assert.equal(ready.progress, '1 / 1 battle wins');
    assert.match(ready.reward, /120/);
    assert.equal(ready.claim, true);
    assert.equal(ready.disabled, false);
    const readyShot = `q1-ready-${size.name}.png`;
    await page.screenshot({ path: path.join(out, readyShot) });

    const beforeClaim = await read();
    await click('#scene-ui [data-choice="journal-claim:q1"]');
    await page.waitForFunction(() => window.rebornSnapshot()?.quests.q1?.claimed === true);
    const afterClaim = await read();
    const elapsedMs = afterClaim.clock - beforeClaim.clock;
    const income = rates(beforeClaim);
    const exactPayout = afterClaim.resources.gold - beforeClaim.resources.gold - income.gold * elapsedMs / 1000;
    const claimUi = await page.evaluate(() => {
      const card = document.querySelector('#scene-ui [data-quest-id="q1"]');
      return {
        status: card?.querySelector('p')?.textContent?.trim() || '',
        claimStillPresent: Boolean(card?.querySelector('[data-choice="journal-claim:q1"]')),
        claimedDisabled: card?.querySelector('[data-choice="journal-claimed:q1"]')?.disabled ?? null,
      };
    });
    assert.ok(Math.abs(exactPayout - 120) < 1e-6, `first-victory quest pays exactly 120 gold, got ${exactPayout}`);
    assert.equal(claimUi.status, 'Reward claimed');
    assert.equal(claimUi.claimStillPresent, false);
    assert.equal(claimUi.claimedDisabled, true);
    const claimedShot = `q1-claimed-${size.name}.png`;
    await page.screenshot({ path: path.join(out, claimedShot) });

    await page.reload({ waitUntil: 'networkidle' });
    await openObjectives();
    const afterReload = await read();
    const reloadElapsedMs = afterReload.clock - afterClaim.clock;
    const repeatPayout = afterReload.resources.gold - afterClaim.resources.gold - income.gold * reloadElapsedMs / 1000;
    const reloadUi = await page.evaluate(() => {
      const card = document.querySelector('#scene-ui [data-quest-id="q1"]');
      return {
        status: card?.querySelector('p')?.textContent?.trim() || '',
        claimPresent: Boolean(card?.querySelector('[data-choice="journal-claim:q1"]')),
        claimedDisabled: card?.querySelector('[data-choice="journal-claimed:q1"]')?.disabled ?? null,
      };
    });
    assert.equal(afterReload.quests.q1.claimed, true);
    assert.ok(Math.abs(repeatPayout) < 1e-6, 'reload does not pay the reward again');
    assert.equal(reloadUi.status, 'Reward claimed');
    assert.equal(reloadUi.claimPresent, false);
    assert.equal(reloadUi.claimedDisabled, true);
    assert.equal(report.errors.filter(item => item.viewport === size.name).length, 0);
    assert.equal(report.failedResponses.filter(item => item.viewport === size.name).length, 0);

    report.viewports.push({
      viewport: size.name,
      worldId: worlds[10].id,
      startingAge: start.age,
      winner,
      clearedEncounter: Object.keys(settled.story.flags).find(key => key.startsWith('cleared:') && settled.story.flags[key]),
      ready,
      exactPayout,
      claimUi,
      repeatPayout,
      reloadUi,
      screenshots: [readyShot, claimedShot],
    });
  } finally {
    await context.close();
  }
}

try {
  await runAtViewport({ name: '825x375', width: 825, height: 375 });
  await runAtViewport({ name: '1280x720', width: 1280, height: 720 });
} finally {
  await browser.close();
}

report.passed = report.viewports.length === 2
  && report.viewports.every(row => row.winner === 'p'
    && row.ready.status === 'Ready to claim'
    && row.ready.claim && !row.ready.disabled
    && row.claimUi.status === 'Reward claimed'
    && !row.claimUi.claimStillPresent && row.claimUi.claimedDisabled
    && row.reloadUi.status === 'Reward claimed'
    && !row.reloadUi.claimPresent && row.reloadUi.claimedDisabled
    && Math.abs(row.exactPayout - 120) < 1e-6 && Math.abs(row.repeatPayout) < 1e-6)
  && report.errors.length === 0 && report.failedResponses.length === 0;
await fs.writeFile(path.join(out, 'report.json'), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify({ passed: report.passed, viewports: report.viewports, errors: report.errors, failedResponses: report.failedResponses, output: path.relative(root, out) }, null, 2));
