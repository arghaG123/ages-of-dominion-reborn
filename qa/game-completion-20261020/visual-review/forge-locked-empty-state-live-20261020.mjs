import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
import path from 'node:path';

const root = process.cwd();
const out = path.join(root, 'qa/game-completion-20261020/visual-review/forge-locked-state-live');
await fs.mkdir(out, { recursive: true });
const sizes = [
  { name: '825x375', width: 825, height: 375 },
  { name: '933x424', width: 933, height: 424 },
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

  await page.goto(report.url, { waitUntil: 'networkidle' });
  await page.locator('[data-choice="new-campaign"]').click();
  await page.locator('[data-choice="scene-class:knight"]').click();
  await page.locator('[data-choice="scene-enter-valley"]').click();
  await page.locator('#context').click();
  await page.locator('[data-choice="menu:forge"]').click();
  await page.waitForFunction(() => {
    const backdrop = document.querySelector('#world image[data-chamber-backdrop="forge"]');
    if (!backdrop) return false;
    const source = new URL(backdrop.getAttribute('href') || '', document.baseURI).href;
    return performance.getEntriesByName(source).some(entry => entry.responseEnd > entry.startTime);
  }, null, { timeout: 5000 });

  const closed = await page.evaluate(() => {
    const app = document.querySelector('#app');
    const dock = document.querySelector('#dock');
    const action = dock.querySelector('[data-choice="inspect:forge"]');
    const actionRect = action.getBoundingClientRect();
    const dockRect = dock.getBoundingClientRect();
    const gate = document.querySelector('#scene-ui.forge [data-forge-gate]');
    const gateRect = gate.getBoundingClientRect();
    const gateStyle = getComputedStyle(gate);
    const backdrop = document.querySelector('#world image[data-chamber-backdrop="forge"]');
    const backdropSource = new URL(backdrop?.getAttribute('href') || '', document.baseURI).href;
    const backdropLoaded = performance.getEntriesByName(backdropSource).some(entry => entry.responseEnd > entry.startTime);
    const hit = document.elementFromPoint(actionRect.left + actionRect.width / 2, actionRect.top + actionRect.height / 2);
    return {
      view: app.dataset.view,
      compactState: app.dataset.forgeActionOnly,
      backdropLoaded,
      actionName: action.getAttribute('aria-label'),
      dockRect: [dockRect.x, dockRect.y, dockRect.width, dockRect.height],
      actionRect: [actionRect.x, actionRect.y, actionRect.width, actionRect.height],
      actionCenterOwned: hit?.closest('[data-choice]')?.dataset.choice === 'inspect:forge',
      gateText: gate.textContent,
      gateVisible: gateStyle.display !== 'none' && gateRect.width > 0 && gateRect.height > 0,
      gateRect: [gateRect.x, gateRect.y, gateRect.width, gateRect.height],
      viewport: [innerWidth, innerHeight],
    };
  });
  await page.screenshot({ path: path.join(out, `forge-locked-${size.name}.png`) });

  const passedClosed = closed.view === 'forge'
    && closed.compactState === 'true'
    && closed.backdropLoaded
    && closed.actionName === 'Craft and inventory'
    && closed.actionCenterOwned
    && Math.round(closed.dockRect[2]) === 48
    && Math.round(closed.dockRect[3]) === 48
    && closed.gateVisible
    && closed.gateText.includes('Build an Armory in the Kingdom');

  await page.locator('[data-choice="inspect:forge"]').click();
  const opened = await page.evaluate(() => {
    const panel = document.querySelector('#panel');
    const button = document.querySelector('#choices [data-choice="forge-return-kingdom"]');
    const tutorialButton = document.querySelector('#choices [data-choice="tutorial-toggle"]');
    const panelRect = panel.getBoundingClientRect();
    const buttonRect = button?.getBoundingClientRect();
    const tutorialRect = tutorialButton?.getBoundingClientRect();
    const visible = Boolean(button && button.getClientRects().length && buttonRect.top >= panelRect.top && buttonRect.bottom <= panelRect.bottom && buttonRect.left >= panelRect.left && buttonRect.right <= panelRect.right && getComputedStyle(button).visibility !== 'hidden');
    const tutorialVisible = Boolean(tutorialButton && tutorialButton.getClientRects().length && tutorialRect.top >= panelRect.top && tutorialRect.bottom <= panelRect.bottom && tutorialRect.left >= panelRect.left && tutorialRect.right <= panelRect.right && getComputedStyle(tutorialButton).visibility !== 'hidden');
    return {
      panelOpen: panel.classList.contains('open'),
      text: panel.innerText,
      goButton: Boolean(button && button.innerText.trim() === 'Return to Kingdom'),
      goButtonVisible: visible,
      goButtonRect: buttonRect ? [buttonRect.x, buttonRect.y, buttonRect.width, buttonRect.height] : null,
      tutorialVisible,
      tutorialRect: tutorialRect ? [tutorialRect.x, tutorialRect.y, tutorialRect.width, tutorialRect.height] : null,
      panelRect: [panelRect.x, panelRect.y, panelRect.width, panelRect.height],
      panelCompact: panelRect.height <= 320,
      slots: document.querySelectorAll('#choices [data-choice^="forge-slot:"]').length,
    };
  });
  await page.screenshot({ path: path.join(out, `forge-locked-inspector-${size.name}.png`) });
  if (opened.goButton) await page.locator('[data-choice="forge-return-kingdom"]').click();
  const returnedToKingdom = await page.locator('#app').getAttribute('data-view') === 'kingdom';
  const passedOpen = opened.panelOpen && opened.goButton && opened.goButtonVisible && opened.tutorialVisible && opened.panelCompact && opened.slots === 0 && returnedToKingdom;
  report.results.push({ size: size.name, passed: passedClosed && passedOpen, closed, opened, returnedToKingdom });
  await context.close();
}

await browser.close();
report.passed = report.results.length === sizes.length && report.results.every(result => result.passed) && report.errors.length === 0 && report.failedResponses.length === 0;
await fs.writeFile(path.join(out, 'report.json'), JSON.stringify(report, null, 2));
console.log(JSON.stringify({ passed: report.passed, sizes: report.results.map(result => ({ size: result.size, passed: result.passed, compactDock: result.closed.dockRect, gateVisible: result.closed.gateVisible, returnToKingdom: result.returnedToKingdom })), errors: report.errors, failedResponses: report.failedResponses, output: path.relative(root, out) }, null, 2));
