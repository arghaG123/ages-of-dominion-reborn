import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';

const base = process.argv[2] || 'http://127.0.0.1:4173';
const outDir = fileURLToPath(new URL('../qa/recovery-executor-20261003/hud/', import.meta.url));
await mkdir(outDir, { recursive: true });
const shot = name => path.join(outDir, name);
async function openPanel(page) {
  const open = await page.locator('#panel').evaluate(node => node.classList.contains('open'));
  if (!open) await page.click('#context');
}
const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
const viewports = [[825, 375], [933, 424], [1180, 820], [1280, 720]];
const report = { base, viewports: [], flow: null, failures: [] };

function clientForSource(rect, sx, sy) {
  const scale = Math.min(rect.width / 1376, rect.height / 768);
  const ox = (rect.width - 1376 * scale) / 2;
  const oy = (rect.height - 768 * scale) / 2;
  return { x: rect.left + ox + sx * scale, y: rect.top + oy + sy * scale, scale };
}

for (const [width, height] of viewports) {
  const page = await browser.newPage({ viewport: { width, height } });
  const failed = [];
  page.on('requestfailed', request => failed.push(request.url()));
  page.on('response', response => { if (response.status() >= 400) failed.push(response.status() + ' ' + response.url()); });
  await page.goto(base + '/', { waitUntil: 'networkidle' });
  await page.evaluate(() => localStorage.clear());
  await page.reload({ waitUntil: 'networkidle' });
  await page.waitForSelector('#resources img');
  const measure = await page.evaluate(() => {
    const frame = document.querySelector('#frame').getBoundingClientRect();
    const stage = document.querySelector('#stage').getBoundingClientRect();
    const panel = document.querySelector('#panel');
    const icons = [...document.querySelectorAll('#resources img')].map(img => {
      const box = img.getBoundingClientRect();
      return { src: img.getAttribute('src'), width: box.width, height: box.height, natural: [img.naturalWidth, img.naturalHeight] };
    });
    return {
      frame: { width: frame.width, height: frame.height },
      stage: { width: stage.width, height: stage.height },
      panelOpen: panel.classList.contains('open'),
      frameWidthFraction: frame.width / window.innerWidth,
      scrollWidth: document.documentElement.scrollWidth,
      icons,
    };
  });
  const longSides = measure.icons.map(icon => Math.max(icon.width, icon.height));
  if (measure.panelOpen) report.failures.push(width + ' panel started open');
  if (measure.frameWidthFraction < 0.95 || measure.frameWidthFraction > 1.01 || measure.scrollWidth > width + 1) report.failures.push(width + ' frame fraction ' + measure.frameWidthFraction + ' scroll ' + measure.scrollWidth);
  if (measure.icons.length !== 4 || longSides.some(side => Math.abs(side - 18) > 0.25)) report.failures.push(width + ' resource long sides ' + longSides.join(','));
  if (failed.length) report.failures.push(width + ' requests ' + failed.join(' | '));
  await page.screenshot({ path: shot(width + 'x' + height + '-kingdom-closed.png') });
  report.viewports.push({ width, height, ...measure, failed });
  await page.close();
}

const page = await browser.newPage({ viewport: { width: 825, height: 375 } });
await page.goto(base + '/', { waitUntil: 'networkidle' });
await page.evaluate(() => localStorage.clear());
await page.reload({ waitUntil: 'networkidle' });
await page.waitForSelector('#resources img');
await openPanel(page);
await page.screenshot({ path: shot('825x375-kingdom-open.png') });
const town = await page.evaluate(() => document.querySelector('#world').getBoundingClientRect().toJSON());
const townPoint = clientForSource(town, 578.75, 126.25);
await page.mouse.click(townPoint.x, townPoint.y);
const townPick = await page.evaluate(() => ({ pick: window.rebornPick, open: document.querySelector('#panel').classList.contains('open'), selected: document.querySelector('#selected').textContent }));
if (townPick.pick?.site !== 'townhall' || !townPick.open) report.failures.push('townhall pick ' + JSON.stringify(townPick));
await page.setViewportSize({ width: 1280, height: 720 });
await page.waitForTimeout(100);
const wide = await page.evaluate(() => document.querySelector('#world').getBoundingClientRect().toJSON());
const plot = clientForSource(wide, 397, 229);
await page.mouse.click(plot.x, plot.y);
const plotPick = await page.evaluate(() => window.rebornPick);
if (plotPick?.site !== 'P01') report.failures.push('P01 pick ' + JSON.stringify(plotPick));
const margin = await page.evaluate(() => document.querySelector('#frame').getBoundingClientRect().toJSON());
await page.mouse.click(margin.left + 2, margin.top + Math.min(20, margin.height / 2));
const miss = await page.evaluate(() => window.rebornPick);
if (miss?.site) report.failures.push('margin pick hit ' + miss.site);
await page.click('#nav button:nth-child(3)');
await openPanel(page);
await page.getByRole('button', { name: 'Leave town' }).click();
for (let step = 0; step < 4; step++) await page.getByRole('button', { name: 'Step north' }).click();
const spent = await page.evaluate(() => window.rebornSnapshot().adventure);
if (spent.moves !== 1 || spent.y !== 4 || spent.atTown) report.failures.push('after travel ' + JSON.stringify(spent));
await page.getByRole('button', { name: 'Return at the town approach' }).click();
const returned = await page.evaluate(() => window.rebornSnapshot().adventure);
if (!returned.atTown || returned.moves !== 1) report.failures.push('after return ' + JSON.stringify(returned));
await page.click('#nav button:nth-child(3)');
await openPanel(page);
await page.getByRole('button', { name: 'Leave town' }).click();
const reopened = await page.evaluate(() => window.rebornSnapshot().adventure);
if (reopened.atTown || reopened.moves !== 1) report.failures.push('after reopen ' + JSON.stringify(reopened));
await page.click('#nav button:nth-child(2)');
await openPanel(page);
await page.getByRole('button', { name: 'End day' }).click();
const ended = await page.evaluate(() => { const state = window.rebornSnapshot(); return { day: state.day, moves: state.adventure.moves, weather: state.weather }; });
if (ended.day !== 2 || ended.moves !== 5) report.failures.push('after end day ' + JSON.stringify(ended));
await page.click('#nav button:nth-child(4)');
await openPanel(page);
const offense = await page.evaluate(() => {
  const img = document.querySelector('#choices img');
  const box = img.getBoundingClientRect();
  return { src: img.getAttribute('src'), width: box.width, height: box.height };
});
if (Math.abs(Math.max(offense.width, offense.height) - 36) > 0.25) report.failures.push('offense size ' + JSON.stringify(offense));
await page.screenshot({ path: shot('825x375-hero-offense.png') });
report.flow = { townPick, plotPick, miss, spent, returned, reopened, ended, offense };
await writeFile(path.join(outDir, 'hud-capture.json'), JSON.stringify(report, null, 2) + '\n');
await browser.close();
if (report.failures.length) {
  console.error(JSON.stringify(report.failures, null, 2));
  process.exit(1);
}
console.log(JSON.stringify({ viewports: report.viewports.map(item => [item.width, item.frameWidthFraction, item.icons.map(icon => [icon.width, icon.height])]), flow: { site: townPick.pick.site, resized: plotPick.site, moves: [spent.moves, returned.moves, reopened.moves, ended.moves], day: ended.day, offense } }));
