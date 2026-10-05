import { mkdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';

const base = process.argv[2] || 'http://127.0.0.1:4173';
const outDir = fileURLToPath(new URL('../qa/visual-integration-20261004/', import.meta.url));
await mkdir(outDir, { recursive: true });
const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
const viewports = [[825, 375], [933, 424], [1180, 820], [1280, 720]];
const report = { base, deviceScaleFactor: 1, viewports: [], failures: [] };

function pngSize(buffer) {
  return { width: buffer.readUInt32BE(16), height: buffer.readUInt32BE(20) };
}

async function shot(page, name) {
  const file = path.join(outDir, name);
  const buffer = await page.screenshot({ type: 'png' });
  await writeFile(file, buffer);
  const size = pngSize(buffer);
  const hash = crypto.createHash('sha256').update(buffer).digest('hex');
  return { file: path.basename(file), ...size, sha256: hash };
}

async function openPanel(page) {
  const open = await page.locator('#panel').evaluate(node => node.classList.contains('open'));
  if (!open) await page.click('#context');
}
async function closePanel(page) {
  const open = await page.locator('#panel').evaluate(node => node.classList.contains('open'));
  if (open) await page.click('#context');
}

async function prepare(page) {
  page.on('dialog', dialog => dialog.accept());
  await page.goto(base + '/', { waitUntil: 'networkidle' });
  await page.evaluate(() => localStorage.clear());
  await page.reload({ waitUntil: 'networkidle' });
  await page.waitForSelector('[data-presentation="title-card"]');
}

async function metrics(page) {
  return page.evaluate(() => {
    const stage = document.querySelector('#stage').getBoundingClientRect();
    const card = document.querySelector('[data-presentation="portrait-card"] image, [data-presentation="title-card"] image');
    const cardBox = card ? card.getBoundingClientRect() : null;
    const header = document.querySelector('header').getBoundingClientRect();
    const buttons = [...document.querySelectorAll('button')].map(node => {
      const box = node.getBoundingClientRect();
      return { choice: node.dataset.choice || node.id, width: box.width, height: box.height };
    });
    const stakes = [...document.querySelectorAll('[data-stake]')].map(node => node.getAttribute('data-stake'));
    const walls = document.querySelector('[data-walls]');
    const traveler = document.querySelector('[data-mounted]');
    const figure = document.querySelector('[data-articulation="schematic"]');
    return {
      innerWidth: window.innerWidth,
      innerHeight: window.innerHeight,
      devicePixelRatio: window.devicePixelRatio,
      panelOpen: document.querySelector('#panel').classList.contains('open'),
      headerBottom: header.bottom,
      stage: { top: stage.top, width: stage.width, height: stage.height },
      card: cardBox ? { top: cardBox.top, bottom: cardBox.bottom, left: cardBox.left, right: cardBox.right, width: cardBox.width, height: cardBox.height } : null,
      cardPresentation: document.querySelector('[data-presentation]')?.getAttribute('data-presentation') || null,
      cardBoxAttr: document.querySelector('[data-card-box]')?.getAttribute('data-card-box') || null,
      articulation: figure?.getAttribute('data-articulation') || null,
      clip: figure?.getAttribute('data-clip') || null,
      planted: figure?.getAttribute('data-planted') || null,
      stakes,
      walls: walls ? { state: walls.getAttribute('data-walls'), level: walls.getAttribute('data-walls-level'), version: walls.getAttribute('data-walls-presentation') } : null,
      traveler: traveler ? { mounted: traveler.getAttribute('data-mounted'), clip: traveler.getAttribute('data-clip'), planted: traveler.getAttribute('data-planted'), mark: traveler.getAttribute('data-mount-mark') } : null,
      terrain: document.querySelector('#terrain')?.dataset?.terrainStatus || null,
      hall: Boolean(document.querySelector('#world image[aria-label*="Hall"]')),
      message: document.querySelector('#message')?.textContent || '',
      selected: document.querySelector('#selected')?.textContent || '',
      shortButtons: buttons.filter(button => button.height > 0 && (button.height < 47.5 || button.width < 47.5)),
    };
  });
}

for (const [width, height] of viewports) {
  const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: 1 });
  await prepare(page);
  const home = await metrics(page);
  const homeShot = await shot(page, `${width}x${height}-home.png`);
  if (home.card && (home.card.top < home.headerBottom - 1 || home.card.bottom > home.stage.top + home.stage.height + 1)) {
    report.failures.push(`${width}x${height} title card crosses chrome or stage`);
  }
  await openPanel(page);
  await page.click('[data-choice="new-campaign"]');
  await page.click('[data-choice="class:mage"]');
  await page.waitForSelector('[data-presentation="portrait-card"]');
  await openPanel(page);
  await page.click('[data-choice="clip:walk"]');
  await closePanel(page);
  const hero = await metrics(page);
  const heroShot = await shot(page, `${width}x${height}-hero-mage-walk.png`);
  if (!hero.card || hero.card.top < hero.headerBottom - 1 || hero.card.height < 40) report.failures.push(`${width}x${height} mage card clipped or tiny`);
  if (hero.shortButtons.length) report.failures.push(`${width}x${height} controls ${JSON.stringify(hero.shortButtons.slice(0, 4))}`);
  await openPanel(page);
  await page.click('[data-choice="enter-valley"]');
  await closePanel(page);
  await page.waitForSelector('[data-walls="unbuilt"]');
  const kingdom = await metrics(page);
  const kingdomShot = await shot(page, `${width}x${height}-kingdom-day1.png`);
  if (kingdom.stakes.length !== 17 || kingdom.walls?.state !== 'unbuilt' || !kingdom.hall) {
    report.failures.push(`${width}x${height} day1 stakes ${kingdom.stakes.length} walls ${kingdom.walls?.state} hall ${kingdom.hall}`);
  }
  await page.click('[data-choice="nav:adventure"]');
  await openPanel(page);
  await page.click('[data-choice="enter-adventure"]');
  await page.click('[data-choice="preview-east"]');
  await closePanel(page);
  const travel = await metrics(page);
  const travelShot = await shot(page, `${width}x${height}-adventure-travel.png`);
  if (travel.traveler?.mounted !== '1') report.failures.push(`${width}x${height} traveler missing`);
  report.viewports.push({ width, height, home, homeShot, hero, heroShot, kingdom, kingdomShot, travel, travelShot });
  await page.close();
}

const clipPage = await browser.newPage({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1 });
await prepare(clipPage);
await openPanel(clipPage);
await clipPage.click('[data-choice="new-campaign"]');
await clipPage.click('[data-choice="class:mage"]');
await openPanel(clipPage);
await clipPage.click('[data-choice="clip:walk"]');
await closePanel(clipPage);
const frames = [];
for (let index = 0; index < 4; index++) {
  await clipPage.waitForTimeout(250);
  frames.push({ ...await shot(clipPage, `1280x720-hero-walk-frame-${index}.png`), atMs: index * 250, clip: 'walk' });
}
await openPanel(clipPage);
await clipPage.click('[data-choice="enter-valley"]');
await clipPage.click('[data-choice="nav:adventure"]');
await openPanel(clipPage);
await clipPage.click('[data-choice="enter-adventure"]');
await clipPage.click('[data-choice="preview-east"]');
await clipPage.click('[data-choice="confirm-route"]');
await closePanel(clipPage);
const travelFrames = [];
for (let index = 0; index < 4; index++) {
  await clipPage.waitForTimeout(120);
  travelFrames.push({ ...await shot(clipPage, `1280x720-travel-frame-${index}.png`), atMs: index * 120, clip: 'mountWalk' });
}
report.travelFrames = travelFrames;
await clipPage.click('[data-choice="nav:forge"]');
await clipPage.waitForTimeout(200);
const forge = await metrics(clipPage);
const forgeShot = await shot(clipPage, '1280x720-forge.png');
await clipPage.click('[data-choice="nav:army"]');
const armyShot = await shot(clipPage, '1280x720-army.png');
await clipPage.click('[data-choice="nav:war"]');
await openPanel(clipPage);
const warShot = await shot(clipPage, '1280x720-war.png');
await clipPage.click('button:has-text("Skirmish")');
await clipPage.waitForTimeout(300);
const tactical = await metrics(clipPage);
const tacticalShot = await shot(clipPage, '1280x720-tactical.png');
await openPanel(clipPage);
const retreat = clipPage.locator('button', { hasText: 'Retreat' });
if (await retreat.count()) await retreat.click();
const apply = clipPage.locator('button', { hasText: 'Apply the battle result' });
if (await apply.count()) await apply.click();
await closePanel(clipPage);
const support = {};
for (const name of ['market', 'defense', 'story', 'settings', 'help']) {
  await clipPage.click(`[data-choice="nav:${name}"]`);
  await closePanel(clipPage);
  await clipPage.waitForTimeout(150);
  support[name] = { metrics: await metrics(clipPage), shot: await shot(clipPage, `1280x720-${name}.png`) };
}
await clipPage.click('[data-choice="nav:war"]');
await openPanel(clipPage);
await clipPage.click('[data-choice="start-siege"]');
await clipPage.waitForTimeout(200);
support.siege = { metrics: await metrics(clipPage), shot: await shot(clipPage, '1280x720-defense-siege.png') };
await clipPage.close();
report.samples = { forge, forgeShot, armyShot, warShot, tactical, tacticalShot, support, frames, video: 'frame sequence; ffmpeg is not installed, so no encoded clip was written' };
await writeFile(path.join(outDir, 'evidence.json'), JSON.stringify(report, null, 2));
console.log(JSON.stringify({ failures: report.failures, shots: report.viewports.length, video: report.samples.video }, null, 2));
await browser.close();
if (report.failures.length) process.exit(1);
