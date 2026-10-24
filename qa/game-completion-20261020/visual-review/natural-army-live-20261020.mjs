import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';

const root = process.cwd();
const out = path.join(root, 'qa/game-completion-20261020/visual-review/army-live');
await fs.mkdir(out, { recursive: true });
const report = {
  recordedAt: new Date().toISOString(),
  classification: 'FRESH_NATURAL_UI_JOURNEY_ISOLATED_BROWSER',
  journey: 'new campaign -> build Barracks -> select the Stone melee formation -> recruit/reinforce five -> save and reload',
  url: 'http://127.0.0.1:4179/?audit=1',
  errors: [],
  checks: {},
  screenshots: {},
};
const browser = await chromium.launch({
  executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe',
  headless: true,
});
const context = await browser.newContext({ viewport: { width: 825, height: 375 }, deviceScaleFactor: 1 });
const page = await context.newPage();
page.on('pageerror', error => report.errors.push(String(error)));
page.on('console', message => { if (message.type() === 'error') report.errors.push(message.text()); });

const read = () => page.evaluate(() => JSON.parse(document.querySelector('#audit-snapshot')?.textContent || 'null'));
async function clickChoice(id) {
  const control = page.locator(`[data-choice="${id}"]`).first();
  await control.waitFor({ state: 'visible', timeout: 10000 });
  assert.equal(await control.isDisabled(), false, `${id} is enabled`);
  await control.click();
}
async function waitForState(predicate, label, timeout = 15000) {
  await page.waitForFunction(
    source => {
      const snapshot = JSON.parse(document.querySelector('#audit-snapshot')?.textContent || 'null');
      return Boolean(snapshot) && new Function('snapshot', `return (${source})(snapshot);`)(snapshot);
    },
    predicate.toString(),
    { timeout, polling: 200 },
  );
  const snapshot = await read();
  assert.ok(snapshot?.state, `${label} has a campaign snapshot`);
  return snapshot.state;
}
async function capture(name, viewport = '825x375') {
  const file = path.join(out, `${name}-${viewport}.png`);
  await page.screenshot({ path: file });
  return path.relative(root, file);
}

try {
  await page.goto(report.url, { waitUntil: 'networkidle' });
  await clickChoice('new-campaign');
  await clickChoice('scene-class:knight');
  await clickChoice('scene-enter-valley');
  await waitForState(snapshot => snapshot?.state?.story?.flags?.enteredValley === true, 'fresh Valley entry');

  await page.locator('#context').click();
  await clickChoice('site-list');
  await clickChoice('choose-site:P01');
  await clickChoice('build:P01:barracks');
  await page.locator('#build-commit').click();
  let state = await waitForState(
    snapshot => snapshot?.state?.buildJobs?.some(job => job.plotId === 'P01' && job.type === 'barracks'),
    'Barracks construction starts',
  );
  report.checks.barracksStarted = state.buildJobs.find(job => job.plotId === 'P01');
  state = await waitForState(
    snapshot => snapshot?.state?.plots?.some(plot => plot.id === 'P01' && plot.type === 'barracks' && plot.level === 1)
      && !snapshot.state.buildJobs.some(job => job.plotId === 'P01'),
    'Barracks construction completes',
  );
  report.checks.barracksBuilt = { level: state.plots.find(plot => plot.id === 'P01')?.level, resources: { ...state.resources } };

  await clickChoice('nav:army');
  await clickChoice('roster:army-1');
  await clickChoice('catalog:0-melee');
  report.screenshots.recruitPreview = await capture('recruit-preview');
  report.checks.preview = {
    selectedRole: await page.locator('[data-choice="catalog:0-melee"]').getAttribute('aria-pressed'),
    recruitButtonVisible: await page.locator('[data-choice="muster-recruit:melee"]').isVisible(),
    recruitButtonLabel: await page.locator('[data-choice="muster-recruit:melee"]').getAttribute('aria-label'),
    formationCount: state.army.length,
  };
  await clickChoice('muster-recruit:melee');
  state = await waitForState(
    snapshot => snapshot?.state?.army?.some(stack => stack.id === 'army-1' && stack.count === 17),
    'Clubman formation increases from 12 to 17',
  );
  const stack = state.army.find(entry => entry.id === 'army-1');
  const rosterCard = page.locator('[data-choice="roster:army-1"]');
  report.checks.recruited = {
    stack: { ...stack },
    formationCount: state.army.length,
    capacity: 2 + state.plots.find(plot => plot.type === 'barracks')?.level,
    caption: await rosterCard.locator('.roster-unit-label').textContent(),
    accessibleName: await rosterCard.getAttribute('aria-label'),
    rankStars: await rosterCard.locator('.roster-rank-stars').textContent(),
    nextActionLabel: await page.locator('[data-choice="muster-recruit:melee"]').getAttribute('aria-label'),
    resources: { ...state.resources },
  };
  report.screenshots.armyRecruitedPhone = await capture('army-recruited');

  await page.locator('#save').click();
  await page.waitForTimeout(150);
  await page.reload({ waitUntil: 'networkidle' });
  state = await waitForState(
    snapshot => snapshot?.state?.army?.some(entry => entry.id === 'army-1' && entry.count === 17),
    'recruited formation survives reload',
  );
  report.checks.reload = { army: state.army.map(entry => ({ id: entry.id, type: entry.type, count: entry.count, rank: entry.rank })), age: state.age };
  if ((await read()).view === 'home' && await page.locator('[data-choice="continue"]').isVisible()) await clickChoice('continue');
  if ((await read()).view !== 'army') await clickChoice('nav:army');
  await page.setViewportSize({ width: 1280, height: 720 });
  await page.waitForTimeout(200);
  report.screenshots.armyRecruitedDesktop = await capture('army-recruited', '1280x720');
  report.checks.desktop = {
    viewport: [page.viewportSize().width, page.viewportSize().height],
    rosterCards: await page.locator('.board-row[data-army-row="roster"] [data-stack-caption]').count(),
    selectedCountText: await page.locator('[data-choice="roster:army-1"]').getAttribute('aria-label'),
  };
} catch (error) {
  report.error = String(error);
} finally {
  report.errors = [...new Set(report.errors)];
  report.passed = !report.error
    && report.errors.length === 0
    && report.checks.barracksBuilt?.level === 1
    && report.checks.preview?.recruitButtonVisible === true
    && report.checks.preview?.recruitButtonLabel?.startsWith('Reinforce +5')
    && report.checks.recruited?.stack?.count === 17
    && report.checks.recruited?.formationCount === 2
    && report.checks.recruited?.capacity === 3
    && report.checks.recruited?.nextActionLabel?.startsWith('Reinforce +5')
    && report.checks.reload?.army?.some(entry => entry.id === 'army-1' && entry.count === 17)
    && report.checks.desktop?.rosterCards === 2;
  await fs.writeFile(path.join(out, 'natural-army-live-20261020.json'), JSON.stringify(report, null, 2));
  await context.close();
  await browser.close();
}
console.log(JSON.stringify({ passed: report.passed, report, output: path.join(out, 'natural-army-live-20261020.json') }, null, 2));
if (!report.passed) process.exitCode = 1;
