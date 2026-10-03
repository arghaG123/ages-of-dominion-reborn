import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';

const pageUrl = fileURLToPath(new URL('../design-preview/kingdom-layout-candidate.html', import.meta.url));
const outDir = fileURLToPath(new URL('../qa/recovery-executor-20261003/layout-preview/', import.meta.url));
await mkdir(outDir, { recursive: true });
const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
const report = { failures: [], shots: [] };

function clientFor(rect, sx, sy) {
  const scale = Math.min(rect.width / 1376, rect.height / 768);
  const ox = (rect.width - 1376 * scale) / 2;
  const oy = (rect.height - 768 * scale) / 2;
  return { x: rect.left + ox + sx * scale, y: rect.top + oy + sy * scale };
}

async function openView(width, height, query) {
  const page = await browser.newPage({ viewport: { width, height } });
  const failed = [];
  page.on('pageerror', error => failed.push(String(error)));
  await page.goto('file:///' + pageUrl.replace(/\\/g, '/') + query, { waitUntil: 'load' });
  await page.waitForSelector('#frames svg image');
  const loaded = await page.evaluate(() => {
    const images = [...document.querySelectorAll('#frames img')];
    return images.every(img => img.naturalWidth > 0);
  });
  if (!loaded) failed.push('terrain image did not load');
  return { page, failed };
}

const views = [[825, 375, ''], [933, 424, ''], [1180, 820, '?fixture=1'], [1280, 720, '?view=compare&fixture=1']];
for (const [width, height, query] of views) {
  const { page, failed } = await openView(width, height, query);
  await page.screenshot({ path: path.join(outDir, `${width}x${height}${query.includes('compare') ? '-compare' : ''}.png`) });
  report.shots.push([width, height, query]);
  report.failures.push(...failed.map(item => width + ' ' + item));
  await page.close();
}

const { page, failed } = await openView(825, 375, '?panel=1');
report.failures.push(...failed.map(item => 'pick ' + item));
const town = await page.evaluate(() => {
  const svg = document.querySelector('#frames svg');
  const rect = svg.getBoundingClientRect().toJSON();
  const hall = globalThis.KINGDOM_CANDIDATE.candidate.geometry.sites.find(site => site.id === 'townhall').rect;
  const cam = globalThis.KINGDOM_CANDIDATE.candidate.camera;
  const [a, b, c, d, e, f] = cam;
  const x = hall[0] + hall[2] / 2, y = hall[1] + hall[3] / 2;
  return { rect, sx: a * x + c * y + e, sy: b * x + d * y + f };
});
const townPoint = clientFor(town.rect, town.sx, town.sy);
await page.mouse.click(townPoint.x, townPoint.y);
const townPick = await page.evaluate(() => window.candidatePick);
if (townPick?.site !== 'townhall') report.failures.push('townhall pick ' + JSON.stringify(townPick));
await page.setViewportSize({ width: 1280, height: 720 });
await page.waitForTimeout(100);
const plot = await page.evaluate(() => {
  const svg = document.querySelector('#frames svg');
  const rect = svg.getBoundingClientRect().toJSON();
  const site = globalThis.KINGDOM_CANDIDATE.candidate.geometry.sites.find(item => item.id === 'P01').rect;
  const [a, b, c, d, e, f] = globalThis.KINGDOM_CANDIDATE.candidate.camera;
  const x = site[0] + site[2] / 2, y = site[1] + site[3] / 2;
  return { rect, sx: a * x + c * y + e, sy: b * x + d * y + f };
});
const plotPoint = clientFor(plot.rect, plot.sx, plot.sy);
await page.mouse.click(plotPoint.x, plotPoint.y);
const plotPick = await page.evaluate(() => window.candidatePick);
if (plotPick?.site !== 'P01') report.failures.push('P01 pick ' + JSON.stringify(plotPick));
await page.screenshot({ path: path.join(outDir, '1280x720-after-resize-pick.png') });
const blocked = await page.evaluate(() => {
  const panel = document.querySelector('#panel').getBoundingClientRect();
  return { x: panel.left + panel.width / 2, y: panel.top + 40 };
});
await page.mouse.click(blocked.x, blocked.y);
const covered = await page.evaluate(() => window.candidatePick);
if (covered?.site !== 'P01') report.failures.push('panel click changed pick ' + JSON.stringify(covered));
await page.close();
await writeFile(path.join(outDir, 'capture.json'), JSON.stringify(report, null, 2) + '\n');
await browser.close();
if (report.failures.length) {
  console.error(JSON.stringify(report.failures, null, 2));
  process.exit(1);
}
console.log(JSON.stringify({ shots: report.shots, town: townPick.site, resized: plotPick.site }));
