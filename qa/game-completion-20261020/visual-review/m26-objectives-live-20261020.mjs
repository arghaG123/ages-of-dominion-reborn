import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
import path from 'node:path';
import worlds from '../../../src/data/adventure-worlds.json' with { type: 'json' };

const root = process.cwd();
const out = path.join(root, 'qa/game-completion-20261020/visual-review/m26-objectives-live-20261020');
await fs.mkdir(out, { recursive: true });
const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
const report = { recordedAt: new Date().toISOString(), classification: 'NATURAL_UI_OBJECTIVES_AND_AGE_MILESTONE', viewports: [], errors: [], failedResponses: [] };

for (const size of [{ name: '825x375', width: 825, height: 375 }, { name: '1280x720', width: 1280, height: 720 }]) {
  const context = await browser.newContext({ viewport: { width: size.width, height: size.height }, deviceScaleFactor: 1 });
  const page = await context.newPage();
  page.on('pageerror', error => report.errors.push({ viewport: size.name, error: String(error) }));
  page.on('console', message => { if (message.type() === 'error') report.errors.push({ viewport: size.name, error: message.text() }); });
  page.on('response', response => { if (response.status() >= 400) report.failedResponses.push({ viewport: size.name, status: response.status(), url: response.url() }); });

  await page.goto('http://127.0.0.1:4179/', { waitUntil: 'networkidle' });
  await page.locator('[data-choice="new-campaign"]').click();
  await page.locator('[data-choice="campaign-world:' + worlds[10].id + '"]').click();
  await page.locator('[data-choice="begin-selected-world"]').click();
  await page.locator('[data-choice="scene-class:knight"]').click();
  await page.locator('[data-choice="scene-enter-valley"]').click();
  await page.locator('#context').click();
  await page.locator('[data-choice="menu:story"]').click();
  await page.getByRole('button', { name: 'Varek Iron-Eye' }).click();
  await page.locator('#scene-ui [data-choice="journal:quests"]').click();

  const initial = await page.evaluate(() => {
    const snapshot = window.rebornSnapshot();
    const questCards = [...document.querySelectorAll('#scene-ui [data-quest-id]')].map(card => ({
      id: card.dataset.questId,
      text: card.innerText,
      claimPresent: Boolean(card.querySelector(`[data-choice="journal-claim:${card.dataset.questId}"]`)),
      destinationPresent: Boolean(card.querySelector(`[data-choice^="quest-destination:"]`)),
    }));
    const choice = document.querySelector('#choices');
    const records = [...document.querySelectorAll('#choices button')]
      .filter(button => /^(Record|Recorded) milestone:/.test(button.textContent.trim()))
      .map(button => ({ text: button.textContent.trim(), disabled: button.disabled }));
    return {
      resources: { ...snapshot.resources },
      age: snapshot.age,
      story: { rival: snapshot.story.rival, choices: snapshot.story.choices },
      quests: snapshot.quests,
      questCards,
      ageRecordButtons: records,
      choicesScroll: choice ? { clientHeight: choice.clientHeight, scrollHeight: choice.scrollHeight, scrollTop: choice.scrollTop } : null,
      storyPanel: (() => { const node = document.querySelector('#scene-ui'); const box = node?.getBoundingClientRect(); return box ? { x: box.x, y: box.y, width: box.width, height: box.height, right: box.right, bottom: box.bottom, scrollHeight: node.scrollHeight, clientHeight: node.clientHeight } : null; })(),
    };
  });
  const initialShot = 'objectives-initial-' + size.name + '.png';
  await page.screenshot({ path: path.join(out, initialShot) });

  const destinations = [];
  for (const [id, expectedView] of [['q1', 'war'], ['q2', 'kingdom'], ['q3', 'adventure'], ['q4', 'army'], ['q5', 'forge'], ['q6', 'war']]) {
    await page.locator(`#scene-ui [data-choice="quest-destination:${id}"]`).click();
    await page.waitForFunction(expected => document.querySelector('#app')?.dataset.view === expected, expectedView);
    destinations.push({ questId: id, expectedView, actualView: await page.locator('#app').getAttribute('data-view') });
    await page.locator('#context').click();
    await page.locator('[data-choice="menu:story"]').click();
    await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'story');
  }

  const notReadyClick = await page.evaluate(() => {
    const snapshot = window.rebornSnapshot();
    const card = document.querySelector('#scene-ui [data-quest-id="q1"]');
    return {
      resources: { ...snapshot.resources },
      claimed: snapshot.quests.q1.claimed,
      rival: snapshot.story.rival,
      choices: snapshot.story.choices,
      message: document.querySelector('#message')?.textContent?.trim() || '',
      status: card?.querySelector('p')?.textContent?.trim() || '',
      claimPresent: Boolean(card?.querySelector('[data-choice="journal-claim:q1"]')),
      destinationPresent: Boolean(card?.querySelector('[data-choice="quest-destination:q1"]')),
    };
  });

  await page.locator('#scene-ui [data-choice="journal-milestone:0"]').click();
  const afterClaim = await page.evaluate(() => {
    const snapshot = window.rebornSnapshot();
      const button = document.querySelector('#scene-ui [data-choice="journal-milestone:0"]');
    return {
      resources: { ...snapshot.resources },
      milestones: snapshot.story.milestones,
      buttonFound: Boolean(button),
      buttonDisabled: button?.disabled ?? null,
      message: document.querySelector('#message')?.textContent?.trim() || '',
    };
  });
  const claimedShot = 'objectives-stone-milestone-claimed-' + size.name + '.png';
  await page.screenshot({ path: path.join(out, claimedShot) });

  await page.reload({ waitUntil: 'networkidle' });
  await page.locator('#context').click();
  await page.locator('[data-choice="menu:story"]').click();
  await page.locator('#scene-ui [data-choice="journal:quests"]').click();
  const afterReload = await page.evaluate(() => {
    const snapshot = window.rebornSnapshot();
    const button = document.querySelector('#scene-ui [data-choice="journal-milestone:0"]');
    return {
      resources: { ...snapshot.resources },
      milestones: snapshot.story.milestones,
      buttonFound: Boolean(button),
      buttonDisabled: button?.disabled ?? null,
    };
  });

  report.viewports.push({ viewport: size.name, width: size.width, initial, destinations, notReadyClick, afterClaim, afterReload, screenshots: [initialShot, claimedShot] });
  await context.close();
}

await browser.close();
report.passed = report.viewports.length === 2
  && report.viewports.every(item => item.initial.age === 0
    && item.initial.questCards.length === 6
    && item.initial.questCards.every(card => card.claimPresent === false && card.destinationPresent === true)
    && item.destinations.length === 6
    && item.destinations.every(route => route.expectedView === route.actualView)
    && item.initial.storyPanel.x <= 16
    && item.initial.storyPanel.right <= item.width * 0.5
    && item.initial.storyPanel.scrollHeight >= item.initial.storyPanel.clientHeight
    && item.initial.ageRecordButtons.length === 8
    && item.notReadyClick.claimed === false
    && item.notReadyClick.rival === item.initial.story.rival
    && JSON.stringify(item.notReadyClick.choices) === JSON.stringify(item.initial.story.choices)
    && item.notReadyClick.status === 'In progress'
    && item.notReadyClick.claimPresent === false
    && item.notReadyClick.destinationPresent === true
    && JSON.stringify(item.notReadyClick.resources) === JSON.stringify(item.initial.resources)
    && item.afterClaim.milestones['0'] === true
    && item.afterClaim.buttonFound === true
    && item.afterClaim.buttonDisabled === true
    && JSON.stringify(item.afterClaim.resources) === JSON.stringify(item.initial.resources)
    && item.afterReload.milestones['0'] === true
    && item.afterReload.buttonDisabled === true
    && JSON.stringify(item.afterReload.resources) === JSON.stringify(item.initial.resources))
  && report.errors.length === 0
  && report.failedResponses.length === 0;
await fs.writeFile(path.join(out, 'report.json'), JSON.stringify(report, null, 2));
console.log(JSON.stringify({ passed: report.passed, viewports: report.viewports, errors: report.errors, failedResponses: report.failedResponses, output: path.relative(root, out) }, null, 2));
