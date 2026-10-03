import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import { mkdir, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';

const out = fileURLToPath(new URL('./browser-v2/', import.meta.url));
await mkdir(out, { recursive: true });
const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
const viewports = [[825, 375], [933, 424], [1180, 820], [1280, 720]];
const report = [];

function sourcePoint(pageBox, scale, offset, point) {
  return [pageBox.x + offset[0] + point[0] * scale, pageBox.y + offset[1] + point[1] * scale];
}

for (const [width, height] of viewports) {
  const page = await browser.newPage({ viewport: { width, height } });
  const errors = [];
  page.on('pageerror', error => errors.push(String(error)));
  await page.goto('file:///C:/dev/ages-of-dominion-reborn/design-preview/kingdom-layout-candidate.html?panel=1&fixture=1');
  await page.waitForSelector('svg image');
  await page.waitForSelector('#sites button');
  const metrics = await page.evaluate(() => window.candidateMetrics);
  const layout = await page.evaluate(() => {
    const svg = document.querySelector('svg');
    const rect = svg.getBoundingClientRect();
    const panel = document.querySelector('#panel').getBoundingClientRect();
    const scale = Math.min(rect.width / 1376, rect.height / 768);
    const offset = [(rect.width - 1376 * scale) / 2, (rect.height - 768 * scale) / 2];
    const buttons = [...document.querySelectorAll('#sites button')].map(button => {
      const box = button.getBoundingClientRect();
      return { id: button.dataset.site, x: box.x, y: box.y, w: box.width, h: box.height };
    });
    return {
      rect: rect.toJSON(), panel: panel.toJSON(), scale, offset,
      panelSourceX: (panel.left - rect.left - offset[0]) / scale,
      contact: document.querySelector('svg polyline') !== null,
      buttons,
    };
  });
  const sites = await page.evaluate(() => {
    const c = globalThis.KINGDOM_CANDIDATE.candidate;
    const [a, b, d, e, tx, ty] = c.camera;
    return c.geometry.sites.map(site => {
      const [x, y, w, h] = site.rect;
      return { id: site.id, source: [a * (x + w / 2) + d * (y + h / 2) + tx, b * (x + w / 2) + e * (y + h / 2) + ty] };
    });
  });
  const hits = [];
  for (const site of sites) {
    const [x, y] = sourcePoint(layout.rect, layout.scale, layout.offset, site.source);
    const covered = x >= layout.panel.x && x <= layout.panel.x + layout.panel.width && y >= layout.panel.y && y <= layout.panel.y + layout.panel.height;
    if (covered) {
      hits.push({ expected: site.id, coveredByPanel: true });
      continue;
    }
    await page.mouse.click(x, y);
    const hit = await page.evaluate(() => window.candidatePick);
    hits.push({ expected: site.id, actual: hit?.site, coveredByPanel: false });
  }
  await page.locator('#sites button[data-site="P11"]').click();
  const listFocus = await page.evaluate(() => window.candidateFocus);
  const boxes = layout.buttons;
  let overlap = 0;
  for (let i = 0; i < boxes.length; i++) for (let j = i + 1; j < boxes.length; j++) {
    const a = boxes[i], b = boxes[j];
    if (a.x < b.x + b.w && b.x < a.x + a.w && a.y < b.y + b.h && b.y < a.y + a.h) overlap += 1;
  }
  const short = boxes.filter(box => box.h < 48 || box.w < 48);
  await page.screenshot({ path: out + `${width}x${height}-proposed.png` });
  await page.locator('[data-view="compare"]').click();
  await page.screenshot({ path: out + `${width}x${height}-compare.png` });
  await page.locator('[data-view="collected"]').click();
  await page.waitForFunction(() => document.querySelector('.caption')?.textContent.includes('FAIL'));
  const collected = await page.evaluate(() => ({
    src: document.querySelector('.pane img')?.getAttribute('src'),
    caption: document.querySelector('.caption')?.textContent,
    fidelity: window.candidateMetrics.paintingFidelity,
    hallImages: document.querySelectorAll('svg image').length,
  }));
  await page.screenshot({ path: out + `${width}x${height}-collected.png` });
  await page.locator('[data-view="current"]').click();
  await page.screenshot({ path: out + `${width}x${height}-current.png` });
  let letterboxMiss = null;
  if (layout.offset[0] > 5 || layout.offset[1] > 5) {
    await page.mouse.click(layout.rect.x + 2, layout.rect.y + 2);
    letterboxMiss = (await page.evaluate(() => window.candidatePick))?.site === null;
  }
  report.push({
    viewport: [width, height], metrics, panelSourceX: layout.panelSourceX, contact: layout.contact,
    hits, missed: hits.filter(hit => !hit.coveredByPanel && hit.expected !== hit.actual),
    covered: hits.filter(hit => hit.coveredByPanel).map(hit => hit.expected),
    listFocus, overlap, short: short.length, collected, letterboxMiss, errors,
  });
  await page.close();
}

const game = [];
for (const [width, height] of viewports) {
  const page = await browser.newPage({ viewport: { width, height } });
  const errors = [];
  page.on('pageerror', error => errors.push(String(error)));
  page.on('response', response => { if (response.status() >= 400) errors.push(response.status() + ' ' + response.url()); });
  page.on('dialog', dialog => dialog.accept());
  await page.goto('http://127.0.0.1:4179/index.html');
  await page.getByRole('button', { name: 'Kingdom' }).click();
  await page.locator('#context').click();
  const dismiss = page.getByRole('button', { name: 'Dismiss resume report' });
  if (await dismiss.count()) await dismiss.click();
  const hud = await page.evaluate(() => {
    const rail = document.querySelector('#resources').getBoundingClientRect();
    const icons = [...document.querySelectorAll('#resources img')].map(img => ({ w: img.getBoundingClientRect().width, h: img.getBoundingClientRect().height }));
    return { rail: rail.height, icons, hidden: document.querySelector('#resources').hidden };
  });
  await page.screenshot({ path: out + `game-${width}x${height}-kingdom.png` });
  await page.getByRole('button', { name: 'War' }).click();
  await page.getByRole('button', { name: 'Skirmish' }).click();
  const dismissBattle = page.getByRole('button', { name: 'Dismiss resume report' });
  if (await dismissBattle.count()) await dismissBattle.click();
  const before = await page.locator('#message').textContent();
  const action = page.locator('#choices button', { hasText: /^(Move|Defend|Melee|Shoot)/ }).first();
  const actionName = await action.textContent();
  await action.click();
  const after = await page.locator('#message').textContent();
  const log = await page.evaluate(() => window.rebornSnapshot()?.battle?.log?.at(-1) ?? null);
  await page.screenshot({ path: out + `game-${width}x${height}-tactical.png` });
  game.push({ viewport: [width, height], hud, actionName, changed: before !== after, before, after, log, errors });
  await page.close();
}

await browser.close();
const body = { candidate: report, game };
await writeFile(fileURLToPath(new URL('./browser-v2-checks.json', import.meta.url)), JSON.stringify(body, null, 2) + '\n');
const summary = {
  candidate: report.map(row => ({
    viewport: row.viewport, chrome: row.metrics.chromePx, stage: row.metrics.stageHeight,
    missed: row.missed, covered: row.covered, list: row.listFocus, overlap: row.overlap, short: row.short,
    collected: row.collected.fidelity, letterboxMiss: row.letterboxMiss, errors: row.errors,
  })),
  game: game.map(row => ({ viewport: row.viewport, hud: row.hud, actionName: row.actionName, changed: row.changed, errors: row.errors })),
};
console.log(JSON.stringify(summary, null, 2));
