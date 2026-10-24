import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
import path from 'node:path';

const root = process.cwd();
const out = path.join(root, 'qa/game-completion-20261022/visual-review/support-flows-natural-live-20261022-run01');
await fs.mkdir(out, { recursive: true });
const sizes = [
  { name: '825x375', width: 825, height: 375 },
  { name: '1280x720', width: 1280, height: 720 },
];
const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
const report = { recordedAt: new Date().toISOString(), url: 'http://127.0.0.1:4173/?audit=1', results: [], errors: [], failedResponses: [] };

for (const size of sizes) {
  const context = await browser.newContext({ viewport: { width: size.width, height: size.height }, deviceScaleFactor: 1 });
  const page = await context.newPage();
  page.setDefaultTimeout(10000);
  page.on('pageerror', error => report.errors.push({ size: size.name, error: String(error) }));
  page.on('console', message => { if (message.type() === 'error') report.errors.push({ size: size.name, error: message.text() }); });
  page.on('response', response => { if (response.status() >= 400) report.failedResponses.push({ size: size.name, status: response.status(), url: response.url() }); });
  const screens = [];
  const capture = async (name, expectedView, expectedSheet = null) => {
    await page.waitForFunction(({ view, sheet }) => {
      const app = document.querySelector('#app');
      const panel = document.querySelector('#panel');
      return app?.dataset.view === view && (!sheet || panel?.dataset.sheet === sheet);
    }, { view: expectedView, sheet: expectedSheet });
    await page.screenshot({ path: path.join(out, `${name}-${size.name}.png`) });
    screens.push(await page.evaluate(name => {
      const panel = document.querySelector('#panel');
      const b = panel.getBoundingClientRect();
      const choices = [...document.querySelectorAll('#choices [data-choice], #choices button')].map(node => ({
        id: node.dataset.choice || '',
        label: node.getAttribute('aria-label') || node.textContent.trim(),
        disabled: node.disabled,
      }));
      return {
        name,
        view: document.querySelector('#app').dataset.view,
        sheet: panel.dataset.sheet,
        panelOpen: panel.classList.contains('open'),
        panel: [Math.round(b.x), Math.round(b.y), Math.round(b.width), Math.round(b.height)],
        selected: document.querySelector('#selected')?.textContent || '',
        status: document.querySelector('#status')?.textContent || '',
        choices,
        panelScroll: [panel.scrollTop, panel.scrollHeight, panel.clientHeight],
      };
    }, name));
  };

  await page.goto(report.url, { waitUntil: 'networkidle' });
  await page.locator('[data-choice="new-campaign"]').click();
  await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'campaignMapSelect');
  await page.locator('[data-choice="begin-selected-world"]').click();
  await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'hero');
  await page.locator('[data-choice="scene-class:knight"]').click();
  await page.locator('[data-choice="scene-enter-valley"]').click();
  await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'kingdom');
  await page.locator('#dock [data-choice="kingdom-actions-open"]').click();
  await capture('tutorial-first-cue', 'kingdom');
  await page.locator('[data-choice="tutorial-toggle"]').click();
  await page.waitForFunction(() => JSON.parse(document.querySelector('#audit-snapshot')?.textContent || 'null')?.state?.tutorial?.skipped === true);
  await capture('tutorial-skipped', 'kingdom');
  await page.locator('[data-choice="tutorial-toggle"]').click();
  await page.waitForFunction(() => JSON.parse(document.querySelector('#audit-snapshot')?.textContent || 'null')?.state?.tutorial?.skipped === false);
  await capture('tutorial-reviewed', 'kingdom');

  await page.locator('#context').click();
  await capture('menu', 'kingdom', 'menu');
  await page.locator('[data-choice="menu:settings"]').click();
  await capture('settings', 'settings');
  const settingsBefore = await page.evaluate(() => JSON.parse(document.querySelector('#audit-snapshot')?.textContent || 'null')?.state?.settings || null);
  await page.locator('[data-choice="settings-volume:music"]').focus();
  await page.locator('[data-choice="settings-volume:music"]').press('ArrowLeft');
  await page.locator('[data-choice="settings-volume:sound"]').focus();
  await page.locator('[data-choice="settings-volume:sound"]').press('ArrowRight');
  await page.waitForFunction(() => {
    const settings = JSON.parse(document.querySelector('#audit-snapshot')?.textContent || 'null')?.state?.settings;
    return settings?.music === 0.5 && settings?.sfx === 0.9;
  });
  await capture('settings-independent-audio', 'settings');
  await page.locator('[data-choice="settings-motion"]').click();
  await page.waitForFunction(() => document.querySelector('[data-choice="settings-motion"]')?.dataset.reducedMotion === 'on');
  const settingsAfter = await page.evaluate(() => JSON.parse(document.querySelector('#audit-snapshot')?.textContent || 'null')?.state?.settings || null);
  await capture('settings-reduced-motion-on', 'settings');

  await page.locator('#context').click();
  await page.locator('[data-choice="menu:help"]').click();
  await capture('help', 'help');
  await page.locator('#context').click();
  await page.locator('[data-choice="menu:story"]').click();
  await capture('story', 'story');
  await page.locator('#context').click();
  await page.locator('[data-choice="menu:market"]').click();
  await capture('market-stone-locked', 'market');

  await page.locator('#context').click();
  await page.locator('[data-choice="menu:home"]').click();
  await capture('campaign-saves', 'home');
  await page.locator('[data-choice="open-load"]').click();
  await capture('campaign-slot-panel', 'home');
  await page.getByRole('button', { name: 'Save slot 1' }).click();
  await page.waitForFunction(() => document.querySelector('#message')?.textContent.includes('Slot 1 stored'));
  const slotSaved = await page.evaluate(() => document.querySelector('#message')?.textContent || '');
  await page.getByRole('button', { name: 'Load slot 1' }).click();
  await page.waitForFunction(() => document.querySelector('#message')?.textContent.includes('Slot 1 loaded'));
  const slotLoaded = await page.evaluate(() => document.querySelector('#message')?.textContent || '');
  await capture('campaign-slot-reload', 'kingdom');

  await page.locator('[data-choice="nav:war"]').click();
  await capture('war-options', 'war');
  await page.locator('[data-choice="start-siege"]').first().click();
  await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'defense');
  await capture('defense-preparation', 'defense', 'defense-preparation');
  await page.getByRole('button', { name: 'Start Campaign Siege' }).last().click();
  await page.waitForFunction(() => document.querySelector('#panel')?.dataset.sheet === 'defense-session');
  await page.waitForTimeout(900);
  await capture('defense-start-paused', 'defense', 'defense-session');
  const defenseBeforePause = await page.evaluate(() => JSON.parse(document.querySelector('#audit-snapshot')?.textContent || 'null')?.state?.defense || null);
  await page.locator('[data-choice="defense-pause"]').click();
  await page.waitForFunction(() => JSON.parse(document.querySelector('#audit-snapshot')?.textContent || 'null')?.state?.defense?.paused === false);
  await capture('defense-running', 'defense', 'defense-session');
  await page.locator('[data-choice="defense-pause"]').click();
  await page.waitForFunction(() => JSON.parse(document.querySelector('#audit-snapshot')?.textContent || 'null')?.state?.defense?.paused === true);
  await capture('defense-paused', 'defense', 'defense-session');
  await page.locator('#context').click();
  await page.locator('[data-choice="menu:help"]').click();
  await capture('help-during-defense', 'help');
  const sessionRetained = await page.evaluate(() => {
    const state = JSON.parse(document.querySelector('#audit-snapshot')?.textContent || 'null')?.state;
    return { defense: state?.defense?.status || null, paused: state?.defense?.paused ?? null };
  });
  await page.locator('[data-choice="resume-session"]').click();
  await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'defense');
  await capture('defense-resumed', 'defense', 'defense-session');

  report.results.push({ size: size.name, screens, settingsBefore, settingsAfter, slotSaved, slotLoaded, defenseBeforePause, sessionRetained });
  await context.close();
}

await browser.close();
report.passed = report.results.length === sizes.length
  && report.results.every(result => result.screens.length === 20)
  && report.results.every(result => result.settingsBefore?.music === 0.6 && result.settingsBefore?.sfx === 0.8 && result.settingsAfter?.music === 0.5 && result.settingsAfter?.sfx === 0.9 && result.settingsAfter?.reducedMotion === true)
  && report.results.every(result => result.slotSaved.includes('Slot 1 stored') && result.slotLoaded.includes('Slot 1 loaded'))
  && report.results.every(result => result.defenseBeforePause?.status === 'ACTIVE' && result.sessionRetained.defense === 'ACTIVE' && result.sessionRetained.paused === true)
  && report.errors.length === 0 && report.failedResponses.length === 0;
await fs.writeFile(path.join(out, 'report.json'), JSON.stringify(report, null, 2));
console.log(JSON.stringify({
  passed: report.passed,
  results: report.results.map(result => ({ size: result.size, screens: result.screens.map(screen => ({ name: screen.name, view: screen.view, sheet: screen.sheet, panel: screen.panel, scroll: screen.panelScroll })), settingsBefore: result.settingsBefore, settingsAfter: result.settingsAfter, slotSaved: result.slotSaved, slotLoaded: result.slotLoaded, defenseBeforePause: result.defenseBeforePause && { status: result.defenseBeforePause.status, wave: result.defenseBeforePause.clearedWaves, paused: result.defenseBeforePause.paused }, sessionRetained: result.sessionRetained })),
  errors: report.errors,
  failedResponses: report.failedResponses,
  output: path.relative(root, out),
}, null, 2));
