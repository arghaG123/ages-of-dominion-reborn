import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';

const root = process.cwd();
const out = path.join(root, 'qa/game-completion-20261020/visual-review/hero-class-roster-live');
const sizes = [
  { width: 825, height: 375 },
  { width: 933, height: 424 },
  { width: 1280, height: 720 },
];
const classes = ['knight', 'ranger', 'warlock', 'mage', 'paladin', 'barbarian', 'necromancer', 'healer'];
await fs.mkdir(out, { recursive: true });
const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
const runs = [];

try {
  for (const size of sizes) {
    const context = await browser.newContext({ viewport: size, deviceScaleFactor: 1 });
    const page = await context.newPage();
    const errors = [];
    const failedResponses = [];
    page.on('pageerror', error => errors.push(String(error)));
    page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
    page.on('response', response => { if (response.status() >= 400) failedResponses.push({ status: response.status(), url: response.url() }); });
    await page.goto('http://127.0.0.1:4179/', { waitUntil: 'networkidle' });
    await page.locator('[data-choice="new-campaign"]').click();
    await page.waitForFunction(() => window.rebornSnapshot()?.hero?.class === 'knight' && document.querySelector('#app')?.dataset.view === 'hero');
    await page.waitForFunction(() => [...document.querySelectorAll('[data-class-card]')].length === 8);
    await page.waitForTimeout(250);

    const visual = await page.evaluate(() => {
      const visible = element => {
        const rect = element.getBoundingClientRect();
        const style = getComputedStyle(element);
        return rect.width > 0 && rect.height > 0 && style.visibility !== 'hidden' && style.display !== 'none';
      };
      const cards = [...document.querySelectorAll('[data-class-card]')].map(element => {
        const rect = element.getBoundingClientRect();
        const image = element.querySelector('img');
        const visibleName = element.querySelector('.portrait-choice-label');
        const nameRect = visibleName?.getBoundingClientRect();
        const x = rect.left + rect.width / 2;
        const y = rect.top + rect.height / 2;
        const hit = document.elementFromPoint(x, y);
        return {
          id: element.dataset.classCard,
          label: element.getAttribute('aria-label'),
          visibleName: visibleName?.textContent.trim() || '',
          nameVisible: Boolean(visibleName && visible(visibleName) && nameRect.width > 0 && nameRect.height > 0),
          current: element.dataset.current === '1',
          within: visible(element) && rect.left >= 0 && rect.top >= 0 && rect.right <= innerWidth && rect.bottom <= innerHeight,
          minimumTarget: rect.width >= 48 && rect.height >= 48,
          centerReceivesInput: hit === element || hit?.closest?.('button,[role="button"]') === element,
          bounds: { x: Math.round(rect.x), y: Math.round(rect.y), width: Math.round(rect.width), height: Math.round(rect.height) },
          image: image ? { src: image.getAttribute('src'), loaded: image.complete && image.naturalWidth > 0, dimensions: [image.naturalWidth, image.naturalHeight], className: image.className } : null,
        };
      });
      const enter = document.querySelector('[data-choice="scene-enter-valley"]');
      const enterRect = enter?.getBoundingClientRect();
      return {
        view: document.querySelector('#app')?.dataset.view,
        viewport: [innerWidth, innerHeight],
        documentSize: [document.documentElement.scrollWidth, document.documentElement.scrollHeight],
        cardChoiceOpen: document.querySelector('#scene-ui')?.dataset.classChoice,
        cards,
        enterWithin: Boolean(enter && enterRect.width > 0 && enterRect.height > 0 && enterRect.left >= 0 && enterRect.top >= 0 && enterRect.right <= innerWidth && enterRect.bottom <= innerHeight),
      };
    });
    const screenshot = path.join(out, `hero-class-roster-${size.width}x${size.height}.png`);
    await page.screenshot({ path: screenshot });

    const selectionRuns = [];
    for (const classId of classes) {
      const card = page.locator(`[data-class-card="${classId}"]`);
      try {
        await card.click({ timeout: 2500 });
        await page.waitForFunction(expected => window.rebornSnapshot()?.hero?.class === expected && document.querySelector(`[data-class-card="${expected}"]`)?.dataset.current === '1', classId, { timeout: 2500 });
        selectionRuns.push({ classId, selected: true });
      } catch (error) {
        selectionRuns.push({ classId, selected: false, error: String(error) });
      }
    }
    const finalClass = await page.evaluate(() => window.rebornSnapshot()?.hero?.class);
    await page.locator('[data-choice="scene-enter-valley"]').click();
    await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'kingdom');
    const entry = await page.evaluate(() => ({
      view: document.querySelector('#app')?.dataset.view,
      heroClass: window.rebornSnapshot()?.hero?.class,
      enteredValley: window.rebornSnapshot()?.story?.flags?.enteredValley,
    }));
    const runtime = {
      ...visual,
      screenshot: path.relative(root, screenshot),
      selectionRuns,
      finalClass,
      entry,
      errors,
      failedResponses,
      allCardsWithin: visual.cards.length === 8 && visual.cards.every(card => card.within),
      allCardCentersHit: visual.cards.length === 8 && visual.cards.every(card => card.centerReceivesInput),
      allClassNamesVisible: visual.cards.length === 8 && visual.cards.every(card => card.nameVisible && card.visibleName === card.label),
      allTargetsAtLeast48: visual.cards.length === 8 && visual.cards.every(card => card.minimumTarget),
      allPortraitImagesLoaded: visual.cards.every(card => card.image?.loaded),
      allClassesSelectable: selectionRuns.length === 8 && selectionRuns.every(run => run.selected),
      noDocumentOverflow: visual.documentSize[0] <= size.width && visual.documentSize[1] <= size.height,
    };
    runs.push(runtime);
    await context.close();
  }
} finally {
  await browser.close();
}

const report = {
  recordedAt: new Date().toISOString(),
  classification: 'ISOLATED_FRESH_CAMPAIGN_HERO_CLASS_SELECTION_UI_REVIEW_NOT_FULL_GAMEPLAY_OR_OWNER_ACCEPTANCE',
  fixtureNote: 'Each run begins from a new isolated browser profile, selects every class through the real class-card UI, then enters Kingdom with the last selected class. No existing save is read or changed.',
  classes,
  sizes,
  runs,
  result: runs.length === 3 && runs.every(run => run.view === 'hero' && run.cardChoiceOpen === 'true' && run.allCardsWithin && run.allCardCentersHit && run.allClassNamesVisible && run.allTargetsAtLeast48 && run.allPortraitImagesLoaded && run.allClassesSelectable && run.noDocumentOverflow && run.entry.view === 'kingdom' && run.entry.heroClass === 'healer' && run.entry.enteredValley === true && run.errors.length === 0 && run.failedResponses.length === 0)
    ? 'FOCUSED PASS'
    : 'FOCUSED FAIL',
  wholeGame: 'INCOMPLETE',
};
await fs.writeFile(path.join(out, 'report.json'), JSON.stringify(report, null, 2));
console.log(JSON.stringify({
  classification: report.classification,
  result: report.result,
  runs: runs.map(({ viewport, cardChoiceOpen, cards, allCardsWithin, allCardCentersHit, allClassNamesVisible, allTargetsAtLeast48, allPortraitImagesLoaded, allClassesSelectable, finalClass, entry, noDocumentOverflow, errors, failedResponses }) => ({ viewport, cardChoiceOpen, cards: cards.map(card => ({ id: card.id, label: card.label, visibleName: card.visibleName, nameVisible: card.nameVisible, minimumTarget: card.minimumTarget, imageLoaded: card.image?.loaded, within: card.within, hit: card.centerReceivesInput })), allCardsWithin, allCardCentersHit, allClassNamesVisible, allTargetsAtLeast48, allPortraitImagesLoaded, allClassesSelectable, finalClass, entry, noDocumentOverflow, errors: errors.length, failedResponses: failedResponses.length })),
}, null, 2));
