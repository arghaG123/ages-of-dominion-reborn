import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';

const root = process.cwd();
const out = path.join(root, 'qa/game-completion-20261020/visual-review');
const sizes = [{ width: 825, height: 375 }, { width: 933, height: 424 }];
const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
const reports = [];
const errors = [];

for (const size of sizes) {
  const context = await browser.newContext({ viewport: size, deviceScaleFactor: 1 });
  const page = await context.newPage();
  page.on('pageerror', error => errors.push({ size, error: String(error) }));
  page.on('console', message => { if (message.type() === 'error') errors.push({ size, error: message.text() }); });
  await page.goto('http://127.0.0.1:4179/', { waitUntil: 'networkidle' });
  await page.locator('[data-choice="new-campaign"]').click();
  await page.locator('[data-choice="scene-class:knight"]').click();
  await page.locator('[data-choice="scene-enter-valley"]').click();
  await page.locator('#context').click();
  await page.locator('[data-choice="menu:settings"]').click();
  await page.waitForTimeout(100);

  const measured = await page.evaluate(() => {
    const root = document.querySelector('#scene-ui.support');
    if (!root) throw new Error('Settings support sheet is missing');
    const rect = node => {
      const r = node.getBoundingClientRect();
      return { x: r.x, y: r.y, width: r.width, height: r.height, top: r.top, bottom: r.bottom };
    };
    const rootRect = rect(root);
    const audio = root.querySelector('[data-choice="settings-audio"]');
    return {
      view: document.querySelector('#app')?.dataset.view,
      viewport: { width: innerWidth, height: innerHeight },
      appHeader: rect(document.querySelector('#app > header')),
      root: { rect: rootRect, clientHeight: root.clientHeight, scrollHeight: root.scrollHeight, scrollTop: root.scrollTop, overflowY: getComputedStyle(root).overflowY },
      children: [...root.children].map(node => ({ tag: node.tagName, choice: node.dataset.choice || null, text: node.innerText?.trim() || '', rect: rect(node) })),
      audio: audio ? { text: audio.innerText, rect: rect(audio) } : null,
      audioHitTarget: audio ? document.elementFromPoint(rect(audio).x + rect(audio).width / 2, rect(audio).y + rect(audio).height / 2)?.dataset?.choice || null : null,
      body: { width: document.body.scrollWidth, height: document.body.scrollHeight },
    };
  });
  const suffix = `${size.width}x${size.height}`;
  const screenshot = path.join(out, `settings-all-controls-${suffix}.png`);
  await page.screenshot({ path: screenshot });

  assert.equal(measured.view, 'settings');
  assert.ok(measured.audio, `${suffix}: audio action is in the Settings sheet`);
  assert.ok(measured.root.scrollHeight <= measured.root.clientHeight + 1, `${suffix}: all settings fit without scrolling`);
  assert.ok(measured.root.rect.top >= 0 && measured.root.rect.bottom <= size.height, `${suffix}: sheet is inside the viewport`);
  assert.ok(measured.root.rect.top >= measured.appHeader.bottom - 1, `${suffix}: sheet clears the game header`);
  assert.ok(measured.children.every(child => child.rect.top >= measured.root.rect.top - 1 && child.rect.bottom <= measured.root.rect.bottom + 1), `${suffix}: all settings rows are visible`);
  assert.equal(measured.audioHitTarget, 'settings-audio', `${suffix}: audio action owns its visible hit target`);
  reports.push({ ...measured, screenshot: path.relative(root, screenshot) });
  await context.close();
}

assert.deepEqual(errors, []);
const report = { recordedAt: new Date().toISOString(), reports, errors };
const reportFile = path.join(out, 'settings-layout-20261020.json');
await fs.writeFile(reportFile, JSON.stringify(report, null, 2));
await browser.close();
console.log(JSON.stringify({ sizes: reports.map(item => ({ viewport: item.viewport, sheet: item.root.rect, scrolling: item.root.scrollHeight - item.root.clientHeight, audio: item.audio.rect, hitTarget: item.audioHitTarget })), errors, report: path.relative(root, reportFile) }, null, 2));
