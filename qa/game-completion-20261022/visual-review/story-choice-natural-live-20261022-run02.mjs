import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
import path from 'node:path';

const root = process.cwd();
const out = path.join(root, 'qa/game-completion-20261022/visual-review/story-choice-natural-live-20261022-run02');
await fs.mkdir(out, { recursive: true });
const sizes = [
  { name: '825x375', width: 825, height: 375 },
  { name: '1280x720', width: 1280, height: 720 },
];
const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
const report = { recordedAt: new Date().toISOString(), sizes: [], errors: [], failedResponses: [] };

for (const size of sizes) {
  const context = await browser.newContext({ viewport: { width: size.width, height: size.height }, deviceScaleFactor: 1 });
  const page = await context.newPage();
  page.setDefaultTimeout(10000);
  page.on('pageerror', error => report.errors.push({ size: size.name, error: String(error) }));
  page.on('console', message => { if (message.type() === 'error') report.errors.push({ size: size.name, error: message.text() }); });
  page.on('response', response => { if (response.status() >= 400) report.failedResponses.push({ size: size.name, status: response.status(), url: response.url() }); });
  const capture = async name => {
    await page.screenshot({ path: path.join(out, `${name}-${size.name}.png`) });
    return page.evaluate(name => {
      const rect = node => {
        const r = node.getBoundingClientRect();
        return { x: Math.round(r.x), y: Math.round(r.y), width: Math.round(r.width), height: Math.round(r.height), bottom: Math.round(r.bottom), right: Math.round(r.right) };
      };
      const state = JSON.parse(document.querySelector('#audit-snapshot')?.textContent || 'null')?.state;
      const buttons = [...document.querySelectorAll('.journal-rival-choices button')];
      const dockButtons = [...document.querySelectorAll('#nav button')];
      const rivals = buttons.slice(0, 6).map(button => ({ label: button.getAttribute('aria-label') || button.textContent.trim(), rect: rect(button), visible: button.getBoundingClientRect().width > 0 && getComputedStyle(button).visibility !== 'hidden' }));
      const navRects = dockButtons.map(button => ({ label: button.getAttribute('aria-label') || button.textContent.trim(), rect: rect(button) }));
      const overlaps = (a, b) => a.x < b.x + b.width && a.x + a.width > b.x && a.y < b.y + b.height && a.y + a.height > b.y;
      const overlappingNavigation = rivals.flatMap(rival => navRects.filter(nav => overlaps(rival.rect, nav.rect)).map(nav => ({ rival: rival.label, navigation: nav.label })));
      return {
        name,
        view: document.querySelector('#app')?.dataset.view,
        viewport: [innerWidth, innerHeight],
        content: document.querySelector('#content') ? rect(document.querySelector('#content')) : null,
        choices: document.querySelector('.journal-rival-choices') ? rect(document.querySelector('.journal-rival-choices')) : null,
        rivalButtons: rivals,
        navigationButtons: navRects,
        overlappingNavigation,
        scroll: { top: document.querySelector('#choices')?.scrollTop ?? null, height: document.querySelector('#choices')?.scrollHeight ?? null, clientHeight: document.querySelector('#choices')?.clientHeight ?? null },
        story: state?.story ?? null,
        age: state?.age ?? null,
        day: state?.day ?? null,
        message: document.querySelector('#message')?.textContent ?? '',
      };
    }, name);
  };

  await page.goto('http://127.0.0.1:4173/?audit=story-choice', { waitUntil: 'networkidle' });
  await page.locator('[data-choice="new-campaign"]').click();
  await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'campaignMapSelect');
  await page.locator('[data-choice="begin-selected-world"]').click();
  await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'hero');
  await page.locator('[data-choice="scene-class:knight"]').click();
  await page.locator('[data-choice="scene-enter-valley"]').click();
  await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'kingdom');
  await page.locator('#context').click();
  await page.locator('[data-choice="menu:story"]').click();
  await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'story');
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(750);
  const initial = await capture('story-rival-choice-initial');

  await page.getByRole('button', { name: 'Varek Iron-Eye', exact: true }).click();
  await page.waitForFunction(() => JSON.parse(document.querySelector('#audit-snapshot')?.textContent || 'null')?.state?.story?.rival === 'Varek Iron-Eye');
  const rivalChosen = await capture('story-rival-selected');
  await page.getByRole('button', { name: 'Share the fire', exact: true }).click();
  await page.waitForFunction(() => JSON.parse(document.querySelector('#audit-snapshot')?.textContent || 'null')?.state?.story?.choices?.length === 1);
  const chapterChosen = await capture('story-chapter-choice-selected');

  await page.reload({ waitUntil: 'networkidle' });
  await page.waitForFunction(() => {
    const state = JSON.parse(document.querySelector('#audit-snapshot')?.textContent || 'null')?.state;
    return document.querySelector('#app')?.dataset.view === 'story' && state?.story?.rival === 'Varek Iron-Eye' && state?.story?.choices?.length === 1;
  });
  const reloaded = await capture('story-choice-reloaded');
  const reloadPersisted = reloaded.story?.rival === 'Varek Iron-Eye' && reloaded.story?.choices?.length === 1 && reloaded.story?.choices?.[0] === chapterChosen.story?.choices?.[0];
  report.sizes.push({ size: size.name, initial, rivalChosen, chapterChosen, reloaded, reloadPersisted });
  await context.close();
}

await browser.close();
report.journeyPassed = report.sizes.length === sizes.length
  && report.sizes.every(result => result.reloadPersisted)
  && report.errors.length === 0 && report.failedResponses.length === 0;
report.visualPass = report.sizes.length === sizes.length && report.sizes.every(result => result.initial.overlappingNavigation.length === 0);
report.passed = report.journeyPassed && report.visualPass;
report.visualFindings = report.sizes.flatMap(result => result.initial.overlappingNavigation.length ? [{ size: result.size, issue: 'rival-choice-hitboxes-overlap-primary-navigation', overlaps: result.initial.overlappingNavigation }] : []);
await fs.writeFile(path.join(out, 'report.json'), JSON.stringify(report, null, 2));
console.log(JSON.stringify({
  passed: report.passed,
  journeyPassed: report.journeyPassed,
  visualPass: report.visualPass,
  visualFindings: report.visualFindings,
  sizes: report.sizes.map(result => ({
    size: result.size,
    reloadPersisted: result.reloadPersisted,
    initialRivalButtons: result.initial.rivalButtons,
    rivalNavOverlaps: result.initial.overlappingNavigation,
    chosenRival: result.rivalChosen.story?.rival,
    chapterChoices: result.chapterChosen.story?.choices,
    reloaded: result.reloaded.story,
  })),
  errors: report.errors,
  failedResponses: report.failedResponses,
  output: path.relative(root, out),
}, null, 2));
