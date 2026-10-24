import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';

const root = process.cwd();
const out = path.join(root, 'qa/game-completion-20261020/visual-review/war-modes-live');
await fs.mkdir(out, { recursive: true });

const modes = ['skirmish', 'duel', 'challenge'];
const viewports = [{ width: 825, height: 375 }, { width: 1280, height: 720 }];
const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
const runs = [];

function campaignMark(state) {
  return {
    age: state.age,
    day: state.day,
    resources: { ...state.resources },
    hero: { xp: state.hero.xp, level: state.hero.level, mana: state.hero.mana },
    inventory: state.inventory.map(item => item.id),
    army: state.army.map(stack => ({ id: stack.id, count: stack.count, xp: stack.xp, rank: stack.rank })),
    rngState: state.rngState,
  };
}

async function auditLayout(page) {
  return page.evaluate(() => {
    const bounds = node => {
      if (!node) return null;
      const rect = node.getBoundingClientRect();
      return { x: Math.round(rect.x), y: Math.round(rect.y), width: Math.round(rect.width), height: Math.round(rect.height) };
    };
    const visible = node => {
      const style = getComputedStyle(node);
      const rect = node.getBoundingClientRect();
      return style.display !== 'none' && style.visibility !== 'hidden' && Number(style.opacity) > 0 && rect.width > 0 && rect.height > 0;
    };
    const exposed = [...document.querySelectorAll('#choices button, #choices input, #dock button, #scene-ui button')]
      .filter(visible)
      .map(node => {
        const rect = node.getBoundingClientRect();
        const x = rect.left + rect.width / 2;
        const y = rect.top + rect.height / 2;
        const top = document.elementFromPoint(x, y);
        const within = rect.left >= -1 && rect.top >= -1 && rect.right <= innerWidth + 1 && rect.bottom <= innerHeight + 1;
        return {
          choice: node.dataset.choice || node.getAttribute('aria-label') || node.textContent.trim().slice(0, 60),
          disabled: Boolean(node.disabled),
          within,
          centerReceivesInput: Boolean(top && (top === node || node.contains(top))),
          rect: { x: Math.round(rect.x), y: Math.round(rect.y), width: Math.round(rect.width), height: Math.round(rect.height) },
        };
      });
    return {
      viewport: { width: innerWidth, height: innerHeight },
      view: document.querySelector('#app')?.dataset.view,
      panelOpen: document.querySelector('#panel')?.classList.contains('open') ?? false,
      panel: bounds(document.querySelector('#panel')),
      dock: bounds(document.querySelector('#dock')),
      scene: bounds(document.querySelector('#stage-field')),
      documentWidth: document.documentElement.scrollWidth,
      documentHeight: document.documentElement.scrollHeight,
      exposed,
    };
  });
}

for (const viewport of viewports) {
  for (const mode of modes) {
    const context = await browser.newContext({ viewport, deviceScaleFactor: 1, acceptDownloads: true });
    const page = await context.newPage();
    const errors = [];
    const failedResponses = [];
    page.on('pageerror', error => errors.push(String(error)));
    page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
    page.on('response', response => { if (response.status() >= 400) failedResponses.push({ status: response.status(), url: response.url() }); });
    await page.route('**/favicon.ico', route => route.fulfill({ status: 204, body: '' }));
    await page.goto(`http://127.0.0.1:4179/?qa=war-${mode}-${viewport.width}x${viewport.height}`, { waitUntil: 'networkidle' });

    await page.locator('[data-choice="new-campaign"]').click();
    await page.locator('[data-choice="scene-class:knight"]').click();
    await page.locator('[data-choice="scene-enter-valley"]').click();
    await page.waitForFunction(() => window.rebornSnapshot()?.age === 0 && document.querySelector('#app')?.dataset.view === 'kingdom');
    const campaignId = await page.evaluate(() => window.rebornSnapshot().id);
    const before = campaignMark(await page.evaluate(() => window.rebornSnapshot()));

    await page.locator('[data-choice="nav:war"]:visible').click();
    await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'war');
    const warScreen = await auditLayout(page);
    assert.equal(warScreen.exposed.filter(control => !control.within || !control.centerReceivesInput).length, 0, 'all visible War mode cards fit and receive input');
    await page.screenshot({ path: path.join(out, `war-menu-${mode}-${viewport.width}x${viewport.height}.png`) });

    let challengeForm = null;
    let challengeDescriptorExport = null;
    let challengeResultExport = null;
    if (mode === 'skirmish') {
      await page.locator('[data-choice="start-skirmish"]:visible').click();
    } else if (mode === 'duel') {
      await page.locator('[data-choice="start-duel"]:visible').click();
    } else {
      await page.locator('[data-choice="open-challenge"]:visible').click();
      await page.waitForFunction(() => document.querySelector('#panel')?.classList.contains('open'));
      const captions = await page.locator('#choices > label.challenge-field').allTextContents();
      assert.deepEqual(captions.map(value => value.trim()), ['Seed', 'Scenario code'], 'challenge inputs have visible field labels');
      challengeForm = await auditLayout(page);
      await page.screenshot({ path: path.join(out, `challenge-form-${viewport.width}x${viewport.height}.png`) });

      await page.locator('[data-choice="challenge-import"]').scrollIntoViewIfNeeded();
      const chooserPromise = page.waitForEvent('filechooser');
      await page.locator('[data-choice="challenge-import"]').click();
      const chooser = await chooserPromise;
      await chooser.setFiles({
        name: 'shared-challenge.json',
        mimeType: 'application/json',
        buffer: Buffer.from(JSON.stringify({ schema: 1, scenarioId: 'duel-v1', seed: 123456789, label: 'visual-check' })),
      });
      await page.waitForFunction(() => document.querySelector('#message')?.textContent.includes('Challenge file loaded'));
      await page.waitForFunction(() => document.querySelector('[data-choice="challenge-seed"]')?.value === '123456789');
      assert.equal(await page.locator('[data-choice="challenge-code"]').getAttribute('aria-label'), 'Scenario code');
      await page.screenshot({ path: path.join(out, `challenge-import-${viewport.width}x${viewport.height}.png`) });

      await page.locator('[data-choice="challenge-export"]').scrollIntoViewIfNeeded();
      const descriptorDownloadPromise = page.waitForEvent('download');
      await page.locator('[data-choice="challenge-export"]').click();
      const descriptorDownload = await descriptorDownloadPromise;
      assert.equal(descriptorDownload.suggestedFilename(), 'aod-challenge.json');
      const descriptorPath = await descriptorDownload.path();
      const descriptor = JSON.parse(await fs.readFile(descriptorPath, 'utf8'));
      assert.deepEqual(descriptor, { schema: 1, scenarioId: 'duel-v1', seed: 123456789, label: 'visual-check' });
      challengeDescriptorExport = descriptor;

      await page.locator('[data-choice="challenge-copy"]').scrollIntoViewIfNeeded();
      await page.locator('[data-choice="challenge-copy"]').click();
      assert.match(await page.locator('#message').innerText(), /Local code: [A-Za-z0-9_-]+/);

      await page.locator('[data-choice="challenge-seed"]').fill('4294967296');
      await page.locator('[data-choice="challenge-code"]').fill('visual-check');
      await page.locator('[data-choice="challenge-start"]').click();
      await page.waitForFunction(() => document.querySelector('#message')?.textContent.includes('Seed must be an integer'));
      assert.equal(await page.evaluate(() => window.rebornSnapshot().battle), null, 'out-of-range challenge seed is rejected before battle start');
      await page.screenshot({ path: path.join(out, `challenge-invalid-${viewport.width}x${viewport.height}.png`) });
      await page.locator('[data-choice="challenge-seed"]').fill('123456789');
      await page.locator('[data-choice="challenge-start"]').click();
    }

    await page.waitForFunction(() => window.rebornSnapshot()?.battle?.status === 'ACTIVE' && document.querySelector('#app')?.dataset.view === 'tactical');
    const battle = await page.evaluate(() => window.rebornSnapshot().battle);
    assert.equal(battle.practice, mode === 'duel' ? 'campaign' : mode);
    assert.deepEqual(campaignMark(await page.evaluate(() => window.rebornSnapshot())), before, `${mode} start does not change campaign progression or resources`);
    if (mode === 'challenge') {
      assert.equal(battle.challenge.seed, 123456789);
      assert.equal(battle.challenge.label, 'visual-check');
    }
    const tacticalStart = await auditLayout(page);
    assert.equal(tacticalStart.panelOpen, false, 'starting a challenge closes its setup panel before tactical play');
    assert.equal(tacticalStart.exposed.filter(control => !control.within || !control.centerReceivesInput).length, 0, `${mode} tactical controls are fully exposed and hitable`);
    await page.screenshot({ path: path.join(out, `tactical-start-${mode}-${viewport.width}x${viewport.height}.png`) });
    const auto = page.locator('[data-choice="auto"]:visible');
    assert.equal(await auto.count(), 1, `${mode} exposes one auto-resolve control`);
    await auto.click();
    await page.waitForFunction(() => window.rebornSnapshot()?.battle?.pendingSettlement === true, null, { timeout: 25000 });
    const result = await page.evaluate(() => ({
      winner: window.rebornSnapshot().battle.outcome?.winner,
      round: window.rebornSnapshot().battle.round,
      casualties: window.rebornSnapshot().battle.stacks.filter(stack => stack.side === 'p').reduce((sum, stack) => sum + (stack.maxCount ?? stack.count) - stack.count, 0),
    }));
    const resultScreen = await auditLayout(page);
    assert.equal(resultScreen.exposed.filter(control => !control.within || !control.centerReceivesInput).length, 0, `${mode} result controls are fully exposed and hitable`);
    await page.screenshot({ path: path.join(out, `battle-result-${mode}-${viewport.width}x${viewport.height}.png`) });
    if (mode === 'challenge') {
      assert.equal(await page.locator('[data-choice="challenge-result"]:visible').count(), 1, 'challenge result export appears in its result dialog');
      const resultDownloadPromise = page.waitForEvent('download');
      await page.locator('[data-choice="challenge-result"]:visible').click();
      const resultDownload = await resultDownloadPromise;
      assert.equal(resultDownload.suggestedFilename(), 'aod-challenge-result.json');
      const resultPath = await resultDownload.path();
      const record = JSON.parse(await fs.readFile(resultPath, 'utf8'));
      assert.equal(record.descriptor.seed, 123456789);
      assert.equal(record.descriptor.label, 'visual-check');
      assert.equal(record.outcome.winner, result.winner);
      assert.equal(record.digest.length, 8);
      challengeResultExport = { seed: record.descriptor.seed, label: record.descriptor.label, winner: record.outcome.winner, digest: record.digest };
    }
    await page.locator('[data-choice="result:tactical"]:visible').click();
    await page.waitForFunction(() => window.rebornSnapshot()?.battle == null);
    const settledState = await page.evaluate(() => window.rebornSnapshot());
    const after = { mark: campaignMark(settledState), practice: settledState.practice ?? null, flags: settledState.story.flags };

    if (mode === 'skirmish') {
      assert.deepEqual(after.mark, before, 'Skirmish settlement leaves campaign progression and resources untouched');
    } else if (mode === 'challenge') {
      assert.deepEqual(after.mark, before, 'Challenge settlement leaves campaign progression and resources untouched');
      const record = Object.values(after.practice?.challenges ?? {}).find(row => row.seed === 123456789 && row.label === 'visual-check');
      assert.ok(record, 'challenge outcome is recorded under the seed and label');
      assert.equal(record.winner, result.winner);
    } else {
      const flag = Object.entries(after.flags).find(([key]) => key.startsWith('battle:duel-'));
      assert.ok(flag, 'Tactical Duel settlement records its campaign battle result exactly once');
      if (result.winner === 'p') assert.equal(after.mark.resources.gold, before.resources.gold + 150, 'victory pays the duel gold reward once');
    }

    await page.waitForFunction(id => {
      const state = window.rebornSnapshot();
      const head = window.rebornCommittedHead();
      return state?.id === id && head?.campaignId === id && head.revision >= state.revision;
    }, campaignId, { timeout: 10000 });
    await page.reload({ waitUntil: 'networkidle' });
    await page.waitForFunction(id => {
      const state = window.rebornSnapshot();
      const head = window.rebornCommittedHead();
      return state?.id === id && !state.battle && head?.campaignId === id && head.revision >= state.revision;
    }, campaignId, { timeout: 10000 });
    const reloaded = campaignMark(await page.evaluate(() => window.rebornSnapshot()));
    assert.deepEqual(reloaded, after.mark, `${mode} settlement persists through reload without a second payout`);
    assert.equal(errors.length, 0, `${mode} has no browser errors: ${JSON.stringify(errors)}`);
    assert.equal(failedResponses.length, 0, `${mode} has no failed network responses: ${JSON.stringify(failedResponses)}`);

    runs.push({
      mode,
      viewport,
      campaignId,
      practice: battle.practice,
      challenge: battle.challenge ?? null,
      challengeDescriptorExport,
      challengeResultExport,
      result,
      before,
      after: after.mark,
      warScreen,
      challengeForm,
      tacticalStart,
      resultScreen,
      errors,
      failedResponses,
      reloadPersisted: true,
    });
    await context.close();
  }
}

await browser.close();
const report = {
  generatedAt: new Date().toISOString(),
  source: 'natural visible-control campaign journeys in isolated browser contexts',
  modes,
  viewports,
  runs,
  result: 'FOCUSED PASS',
  wholeGame: 'INCOMPLETE',
};
await fs.writeFile(path.join(out, 'report.json'), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify({ result: report.result, runs: runs.map(run => ({ mode: run.mode, viewport: `${run.viewport.width}x${run.viewport.height}`, winner: run.result.winner, errors: run.errors.length, failedResponses: run.failedResponses.length })) }, null, 2));
