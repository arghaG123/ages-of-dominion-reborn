import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
import path from 'node:path';
import worlds from '../../../src/data/adventure-worlds.json' with { type: 'json' };

const root = process.cwd();
const out = path.join(root, 'qa/game-completion-20261020/visual-review/m21-spellbook-feedback-live-20261020');
await fs.mkdir(out, { recursive: true });
const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
const report = { recordedAt: new Date().toISOString(), classification: 'NATURAL_UI_SPELL_SELECTION_FEEDBACK', viewports: [], errors: [], failedResponses: [] };

for (const size of [{ name: '825x375', width: 825, height: 375 }, { name: '1280x720', width: 1280, height: 720 }]) {
  const context = await browser.newContext({ viewport: { width: size.width, height: size.height }, deviceScaleFactor: 1 });
  const page = await context.newPage();
  page.on('pageerror', error => report.errors.push({ viewport: size.name, error: String(error) }));
  page.on('console', message => { if (message.type() === 'error') report.errors.push({ viewport: size.name, error: message.text() }); });
  page.on('response', response => { if (response.status() >= 400) report.failedResponses.push({ viewport: size.name, status: response.status(), url: response.url() }); });

  await page.goto('http://127.0.0.1:4179/', { waitUntil: 'networkidle' });
  await page.locator('[data-choice="new-campaign"]').click();
  await page.locator(`[data-choice="campaign-world:${worlds[10].id}"]`).click();
  await page.locator('[data-choice="begin-selected-world"]').click();
  await page.locator('[data-choice="scene-class:warlock"]').click();
  await page.locator('[data-choice="scene-enter-valley"]').click();
  await page.locator('[data-choice="nav:hero"]').click();
  await page.locator('#dock [data-choice="inspect:hero"]').click();
  await page.locator('#choices [data-choice="hero-tab:spells"]').click();

  const initial = await page.evaluate(() => {
    const snapshot = window.rebornSnapshot();
    const panel = document.querySelector('#panel');
    const rect = panel.getBoundingClientRect();
    const cards = [...document.querySelectorAll('#choices .hero-spell-grid button')];
    return {
      mana: snapshot.hero.mana,
      maximumMana: snapshot.hero.maxMana,
      count: cards.length,
      available: cards.filter(card => card.getAttribute('aria-disabled') !== 'true').length,
      locked: cards.filter(card => card.getAttribute('aria-disabled') === 'true').length,
      heading: document.querySelector('#choices .spellbook-heading')?.textContent?.trim() || '',
      panel: { x: rect.x, y: rect.y, width: rect.width, height: rect.height, bottom: rect.bottom },
    };
  });
  const initialShot = `spellbook-initial-${size.name}.png`;
  await page.screenshot({ path: path.join(out, initialShot) });

  await page.locator('#choices [data-choice="spell:arrow"]').click();
  const selected = await page.evaluate(() => {
    const snapshot = window.rebornSnapshot();
    const heading = document.querySelector('#choices .spellbook-heading');
    const rect = heading?.getBoundingClientRect();
    const card = document.querySelector('#choices [data-choice="spell:arrow"]');
    return {
      mana: snapshot.hero.mana,
      text: heading?.textContent?.trim() || '',
      feedbackState: heading?.dataset.spellFeedback || '',
      visible: Boolean(rect && rect.width > 0 && rect.height > 0 && rect.top >= 0 && rect.bottom <= innerHeight && rect.left >= 0 && rect.right <= innerWidth),
      bounds: rect ? { x: rect.x, y: rect.y, width: rect.width, height: rect.height, bottom: rect.bottom } : null,
      selectedCard: card?.getAttribute('aria-current') === 'true',
      cards: [...document.querySelectorAll('#choices .hero-spell-grid button')].map(node => {
        const box = node.getBoundingClientRect();
        return { name: node.getAttribute('aria-label')?.split('.')[0] || '', visible: box.width > 0 && box.height > 0 && box.top >= 0 && box.bottom <= innerHeight };
      }),
    };
  });
  const selectedShot = `spellbook-arrow-selected-${size.name}.png`;
  await page.screenshot({ path: path.join(out, selectedShot) });

  report.viewports.push({ viewport: size.name, initial, selected, screenshots: [initialShot, selectedShot] });
  await context.close();
}

await browser.close();
report.passed = report.viewports.length === 2
  && report.viewports.every(item => item.initial.count === 8
    && item.initial.available === 4
    && item.initial.locked === 4
    && item.selected.feedbackState === 'available'
    && item.selected.text.includes('Magic Arrow')
    && item.selected.text.includes('damage')
    && item.selected.text.includes('mana')
    && item.selected.visible
    && item.selected.selectedCard
    && item.selected.mana === item.initial.mana
    && item.selected.cards.length === 8)
  && report.errors.length === 0
  && report.failedResponses.length === 0;
await fs.writeFile(path.join(out, 'report.json'), JSON.stringify(report, null, 2));
console.log(JSON.stringify({ passed: report.passed, viewports: report.viewports, errors: report.errors, failedResponses: report.failedResponses, output: path.relative(root, out) }, null, 2));
