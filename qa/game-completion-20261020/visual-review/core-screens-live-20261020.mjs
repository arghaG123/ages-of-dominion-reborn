import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
import path from 'node:path';
import worlds from '../../../src/data/adventure-worlds.json' with { type: 'json' };

const root = process.cwd();
const out = path.join(root, 'qa/game-completion-20261020/visual-review/core-screens-live-20261020');
await fs.mkdir(out, { recursive: true });
const sizes = [
  { name: '825x375', width: 825, height: 375 },
  { name: '1280x720', width: 1280, height: 720 },
];
const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
const report = { recordedAt: new Date().toISOString(), url: 'http://127.0.0.1:4179/', results: [], errors: [], failedResponses: [] };

for (const size of sizes) {
  const context = await browser.newContext({ viewport: { width: size.width, height: size.height }, deviceScaleFactor: 1 });
  const page = await context.newPage();
  page.on('pageerror', error => report.errors.push({ size: size.name, error: String(error) }));
  page.on('console', message => { if (message.type() === 'error') report.errors.push({ size: size.name, error: message.text() }); });
  page.on('response', response => { if (response.status() >= 400) report.failedResponses.push({ size: size.name, status: response.status(), url: response.url() }); });
  const screens = [];
  const capture = async (name, expectedView) => {
    await page.waitForFunction(view => document.querySelector('#app')?.dataset.view === view, expectedView, { timeout: 10000 });
    await page.waitForFunction(() => {
      const terrain = document.querySelector('#terrain');
      return terrain?.complete && (terrain.naturalWidth || 0) > 0;
    }, null, { timeout: 10000 });
    await page.screenshot({ path: path.join(out, `${name}-${size.name}.png`) });
    screens.push(await page.evaluate(name => {
      const app = document.querySelector('#app');
      const panel = document.querySelector('#panel');
      const rect = panel.getBoundingClientRect();
      return {
        name,
        view: app.dataset.view,
        panelOpen: panel.classList.contains('open'),
        panel: [Math.round(rect.x), Math.round(rect.y), Math.round(rect.width), Math.round(rect.height)],
        title: document.querySelector('#selected')?.textContent || '',
        scrollHeight: panel.scrollHeight,
        clientHeight: panel.clientHeight,
        terrainLoaded: document.querySelector('#terrain')?.complete && (document.querySelector('#terrain')?.naturalWidth || 0) > 0,
        terrainSource: document.querySelector('#terrain')?.getAttribute('src') || '',
        terrainStatus: document.querySelector('#terrain')?.dataset.terrainStatus || '',
      };
    }, name));
  };

  await page.goto(report.url, { waitUntil: 'networkidle' });
  await capture('campaign-home', 'home');
  await page.locator('[data-choice="new-campaign"]').click();
  await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'campaignMapSelect');
  await page.locator(`[data-choice="campaign-world:${worlds[10].id}"]`).click();
  await capture('campaign-world-picker', 'campaignMapSelect');
  await page.locator('[data-choice="begin-selected-world"]').click();
  await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'hero');
  await page.locator('[data-choice="scene-class:knight"]').click();
  await page.locator('[data-choice="scene-enter-valley"]').click();
  await page.locator('[data-choice="nav:kingdom"]').click();
  await capture('kingdom', 'kingdom');
  const plotSummary = await page.evaluate(() => [...document.querySelectorAll('#world [data-plot]')].map(node => ({
    id: node.dataset.plot,
    state: node.dataset.padState,
    art: node.dataset.siteArt || '',
    box: (() => { const b = node.getBBox(); return [Math.round(b.x), Math.round(b.y), Math.round(b.width), Math.round(b.height)]; })(),
  })));
  await page.locator('#dock [data-choice="kingdom-actions-open"]').click();
  await capture('kingdom-actions', 'kingdom');
  await page.locator('[data-choice="nav:adventure"]').click();
  await page.locator('#dock [data-choice="inspect:adventure"]').click();
  await page.locator('#choices [data-choice="enter-adventure"]').click();
  await capture('adventure', 'adventure');
  await page.locator('[data-choice="nav:hero"]').click();
  await page.locator('#dock [data-choice="inspect:hero"]').click();
  await capture('hero-and-spellbook', 'hero');
  await page.locator('#choices [data-choice="skill:firstaid"]').click();
  await page.waitForFunction(() => {
    const detail = document.querySelector('#choices [data-skill-detail="firstaid"]');
    return detail?.textContent.includes('Recover 15/30/45% of losses after a won battle');
  });
  await capture('hero-skill-detail', 'hero');
  const skillDetailReview = await page.evaluate(() => {
    const detail = document.querySelector('#choices [data-skill-detail="firstaid"]');
    const copy = detail?.querySelector('p');
    const panel = document.querySelector('#panel');
    const bounds = detail?.getBoundingClientRect();
    const panelBounds = panel?.getBoundingClientRect();
    return {
      text: detail?.textContent || '',
      visible: Boolean(bounds && panelBounds && bounds.width > 0 && bounds.height > 0 && bounds.top >= panelBounds.top && bounds.bottom <= panelBounds.bottom),
      noHorizontalClip: Boolean(copy && copy.scrollWidth <= copy.clientWidth + 1),
      noVerticalClip: Boolean(copy && copy.scrollHeight <= copy.clientHeight + 1),
      detailBounds: bounds ? { left: bounds.left, right: bounds.right, top: bounds.top, bottom: bounds.bottom, width: bounds.width, height: bounds.height } : null,
      screenshot: 'hero-skill-detail',
    };
  });
  await page.locator('#context').click();
  await page.locator('#choices [data-choice="menu:forge"]').click();
  await capture('forge', 'forge');
  await page.locator('#dock [data-choice="inspect:forge"]').click();
  await capture('equipment-panel', 'forge');
  await page.locator('[data-choice="nav:army"]').click();
  await capture('army-roster', 'army');
  await page.locator('#dock [data-choice="inspect:army"]').click();
  await capture('army-details', 'army');
  await page.locator('[data-choice="nav:war"]').click();
  await capture('battle-modes', 'war');
  await page.locator('#scene-ui [data-choice="start-skirmish"]').click();
  await capture('tactical-battle', 'tactical');
  report.results.push({ size: size.name, screens, plotSummary, skillDetailReview });
  await context.close();
}

await browser.close();
report.passed = report.results.length === sizes.length
  && report.results.every(result => result.screens.length === 13 && result.screens.every(screen => screen.terrainLoaded))
  && report.results.every(result => result.skillDetailReview.visible && result.skillDetailReview.noHorizontalClip && result.skillDetailReview.noVerticalClip && result.skillDetailReview.text.includes('after a won battle'))
  && report.errors.length === 0 && report.failedResponses.length === 0;
await fs.writeFile(path.join(out, 'report.json'), JSON.stringify(report, null, 2));
console.log(JSON.stringify({
  passed: report.passed,
  results: report.results.map(result => ({ size: result.size, screens: result.screens.map(screen => ({ name: screen.name, view: screen.view, panelOpen: screen.panelOpen, panel: screen.panel, title: screen.title })), plotSummary: result.plotSummary, skillDetailReview: result.skillDetailReview })),
  errors: report.errors,
  failedResponses: report.failedResponses,
  output: path.relative(root, out),
}, null, 2));
