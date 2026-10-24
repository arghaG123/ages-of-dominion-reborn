import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
import path from 'node:path';
import worlds from '../../../src/data/adventure-worlds.json' with { type: 'json' };

const root = process.cwd();
const out = path.join(root, 'qa/game-completion-20261020/visual-review/story-live-20261020');
await fs.mkdir(out, { recursive: true });
const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
const report = { recordedAt: new Date().toISOString(), classification: 'NATURAL_UI_STORY_RIVAL_CHOICE_QUESTS_AND_RELOAD', viewports: [], errors: [], failedResponses: [] };

for (const size of [{ name: '825x375', width: 825, height: 375 }, { name: '1280x720', width: 1280, height: 720 }]) {
  const context = await browser.newContext({ viewport: { width: size.width, height: size.height }, deviceScaleFactor: 1 });
  const page = await context.newPage();
  page.on('pageerror', error => report.errors.push({ viewport: size.name, error: String(error) }));
  page.on('console', message => { if (message.type() === 'error') report.errors.push({ viewport: size.name, error: message.text() }); });
  page.on('response', response => { if (response.status() >= 400) report.failedResponses.push({ viewport: size.name, status: response.status(), url: response.url() }); });
  const capture = async name => {
    await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'story');
    const file = name + '-' + size.name + '.png';
    await page.screenshot({ path: path.join(out, file) });
    return file;
  };

  await page.goto('http://127.0.0.1:4179/', { waitUntil: 'networkidle' });
  await page.locator('[data-choice="new-campaign"]').click();
  await page.locator('[data-choice="campaign-world:' + worlds[10].id + '"]').click();
  await page.locator('[data-choice="begin-selected-world"]').click();
  await page.locator('[data-choice="scene-class:knight"]').click();
  await page.locator('[data-choice="scene-enter-valley"]').click();
  await page.locator('#context').click();
  await page.locator('[data-choice="menu:story"]').click();
  await page.getByRole('button', { name: 'Varek Iron-Eye' }).click();

  const selected = await page.evaluate(() => {
    const snapshot = window.rebornSnapshot();
    const image = document.querySelector('[data-rival-portrait]');
    const imageRect = image?.getBoundingClientRect();
    const panelRect = document.querySelector('#panel')?.getBoundingClientRect();
    let overlap = 0;
    if (imageRect && panelRect && imageRect.width > 0 && imageRect.height > 0) {
      const width = Math.max(0, Math.min(imageRect.right, panelRect.right) - Math.max(imageRect.left, panelRect.left));
      const height = Math.max(0, Math.min(imageRect.bottom, panelRect.bottom) - Math.max(imageRect.top, panelRect.top));
      overlap = width * height / (imageRect.width * imageRect.height);
    }
    const center = imageRect ? document.elementFromPoint(imageRect.left + imageRect.width / 2, imageRect.top + imageRect.height / 2) : null;
    return {
      rival: snapshot.story.rival,
      chapter: snapshot.story.chapter,
      title: document.querySelector('#selected')?.textContent?.trim() || '',
      chapterChoices: [...document.querySelectorAll('#scene-ui [data-choice^="journal-choice:"]')].map(node => node.textContent.trim()),
      rivalPortraitPresent: Boolean(image),
      rivalPortraitPanelOverlap: Number(overlap.toFixed(3)),
      portraitCenterHit: center?.closest('#panel') ? 'covered-by-panel' : center?.tagName || 'none',
      foodBeforeChoice: snapshot.resources.food,
      sceneText: document.querySelector('#scene-ui')?.innerText?.slice(0, 700) || '',
    };
  });
  const selectedShot = await capture('story-chronicle-rival');

  await page.locator('#scene-ui [data-choice="journal:quests"]').click();
  const quests = await page.evaluate(() => ({
    count: document.querySelectorAll('#scene-ui [data-quest-id]').length,
    names: [...document.querySelectorAll('#scene-ui [data-quest-id]')].map(node => node.querySelector('h3')?.textContent?.trim() || node.innerText.split('\\n')[0]),
  }));
  const questsShot = await capture('story-quests');

  await page.locator('#scene-ui [data-choice="journal:chronicle"]').click();
  await page.locator('#scene-ui .journal-archive summary').click();
  const archive = await page.evaluate(() => ({
    open: document.querySelector('#scene-ui .journal-archive')?.open ?? false,
    chapters: [...document.querySelectorAll('#scene-ui [data-chapter]')].map(node => ({
      id: node.dataset.chapter,
      open: node.dataset.open,
      title: node.innerText.split('\\n')[0],
      hasChapterArt: node.style.backgroundImage.length > 0,
    })),
  }));
  const archiveShot = await capture('story-chapter-archive');

  await page.locator('#scene-ui [data-choice="journal-choice:0"]').click();
  const afterChoice = await page.evaluate(() => {
    const snapshot = window.rebornSnapshot();
    return {
      rival: snapshot.story.rival,
      chapter: snapshot.story.chapter,
      choice: snapshot.story.choices[0],
      food: snapshot.resources.food,
      message: document.querySelector('#message')?.textContent?.trim() || '',
      storyText: document.querySelector('#scene-ui')?.innerText?.slice(0, 600) || '',
    };
  });
  const branchShot = await capture('story-after-choice');

  await page.reload({ waitUntil: 'networkidle' });
  await page.locator('#context').click();
  await page.locator('[data-choice="menu:story"]').click();
  const afterReload = await page.evaluate(() => {
    const snapshot = window.rebornSnapshot();
    return {
      rival: snapshot.story.rival,
      chapter: snapshot.story.chapter,
      choice: snapshot.story.choices[0],
      food: snapshot.resources.food,
      message: document.querySelector('#message')?.textContent?.trim() || '',
      rivalPortraitPresent: Boolean(document.querySelector('[data-rival-portrait]')),
    };
  });
  const reloadShot = await capture('story-after-reload');

  report.viewports.push({
    viewport: size.name,
    selected,
    quests,
    archive,
    afterChoice,
    afterReload,
    screenshots: [selectedShot, questsShot, archiveShot, branchShot, reloadShot],
  });
  await context.close();
}

await browser.close();
report.passed = report.viewports.length === 2
  && report.viewports.every(item => item.selected.rival === 'Varek Iron-Eye'
    && item.selected.chapter === 0
    && item.quests.count === 6
    && item.archive.open === true
    && item.archive.chapters.length === 7
    && item.afterChoice.choice === 'generous'
    && item.afterChoice.food === item.selected.foodBeforeChoice + 120
    && item.afterReload.choice === 'generous'
    && item.afterReload.rival === 'Varek Iron-Eye'
    && item.afterReload.food === item.afterChoice.food)
  && report.errors.length === 0
  && report.failedResponses.length === 0;
await fs.writeFile(path.join(out, 'report.json'), JSON.stringify(report, null, 2));
console.log(JSON.stringify({ passed: report.passed, viewports: report.viewports, errors: report.errors, failedResponses: report.failedResponses, output: path.relative(root, out) }, null, 2));
