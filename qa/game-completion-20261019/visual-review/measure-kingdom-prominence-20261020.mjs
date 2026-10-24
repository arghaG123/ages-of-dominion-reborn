import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
import path from 'node:path';

const root = process.cwd();
const out = path.join(root, 'qa/game-completion-20261019/visual-review/kingdom-prominence-live-20261020');
await fs.mkdir(out, { recursive: true });
const sizes = [
  { name: '825x375', width: 825, height: 375 },
  { name: '933x424', width: 933, height: 424 },
  { name: '1180x820', width: 1180, height: 820 },
  { name: '1280x720', width: 1280, height: 720 },
];
const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
const report = { recordedAt: new Date().toISOString(), classification: 'natural fresh Stone campaign; closed inspector; no injected resources or layout state', measurements: [], errors: [] };

function clip(rect, bounds) {
  const left = Math.max(rect.left, bounds.left);
  const top = Math.max(rect.top, bounds.top);
  const right = Math.min(rect.right, bounds.right);
  const bottom = Math.min(rect.bottom, bounds.bottom);
  return right > left && bottom > top ? { left, top, right, bottom } : null;
}
function unionArea(rects) {
  const xs = [...new Set(rects.flatMap(rect => [rect.left, rect.right]))].sort((a, b) => a - b);
  let area = 0;
  for (let i = 0; i < xs.length - 1; i++) {
    const left = xs[i], right = xs[i + 1];
    const intervals = rects.filter(rect => rect.left < right && rect.right > left).map(rect => [rect.top, rect.bottom]).sort((a, b) => a[0] - b[0]);
    let covered = 0, end = -Infinity;
    for (const [top, bottom] of intervals) {
      covered += Math.max(0, bottom - Math.max(top, end));
      end = Math.max(end, bottom);
    }
    area += (right - left) * covered;
  }
  return area;
}

for (const size of sizes) {
  const context = await browser.newContext({ viewport: { width: size.width, height: size.height }, deviceScaleFactor: 1 });
  const page = await context.newPage();
  page.on('pageerror', error => report.errors.push({ size: size.name, error: String(error) }));
  page.on('console', message => { if (message.type() === 'error') report.errors.push({ size: size.name, error: message.text() }); });
  await page.goto('http://127.0.0.1:4179/', { waitUntil: 'networkidle' });
  await page.locator('[data-choice="new-campaign"]').click();
  await page.locator('[data-choice="scene-class:knight"]').click();
  await page.locator('[data-choice="scene-enter-valley"]').click();
  await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'kingdom' && document.querySelector('#terrain')?.naturalWidth > 0);
  await page.waitForTimeout(180);
  const layout = await page.evaluate(() => {
    const rectOf = element => {
      const rect = element.getBoundingClientRect();
      return { left: rect.left, top: rect.top, right: rect.right, bottom: rect.bottom, width: rect.width, height: rect.height };
    };
    const visible = element => {
      if (!element || !element.getClientRects().length) return false;
      const style = getComputedStyle(element);
      return style.display !== 'none' && style.visibility !== 'hidden' && Number(style.opacity) > 0;
    };
    const nodes = [
      ...document.querySelectorAll('main > header h1, #status, #resources .resource-chip, #context, #save, #nav button, #dock button'),
      ...[...document.querySelectorAll('#scene-ui *')].filter(element => element.children.length === 0 && (element.textContent.trim() || element.matches('button,[role="button"]'))),
    ].filter(visible);
    const seen = new Set();
    const hud = nodes.filter(element => !seen.has(element) && seen.add(element)).map(element => ({
      id: element.id || '',
      label: element.getAttribute('aria-label') || element.textContent.trim().replace(/\s+/g, ' ').slice(0, 80),
      rect: rectOf(element),
    }));
    return {
      requestedViewport: { width: innerWidth, height: innerHeight },
      documentViewport: { width: document.documentElement.clientWidth, height: document.documentElement.clientHeight },
      visualViewport: window.visualViewport ? { width: visualViewport.width, height: visualViewport.height, scale: visualViewport.scale } : null,
      dpr: devicePixelRatio,
      view: document.querySelector('#app')?.dataset.view,
      terrain: rectOf(document.querySelector('#terrain')),
      hud,
      navButtons: [...document.querySelectorAll('#nav button')].map(button => ({ label: button.getAttribute('aria-label'), rect: rectOf(button) })),
      panelOpen: document.querySelector('#panel')?.classList.contains('open'),
    };
  });
  const viewport = { left: 0, top: 0, right: layout.documentViewport.width, bottom: layout.documentViewport.height };
  const terrain = clip(layout.terrain, viewport);
  const visibleHud = layout.hud.map(item => clip(item.rect, terrain)).filter(Boolean);
  const terrainArea = terrain ? (terrain.right - terrain.left) * (terrain.bottom - terrain.top) : 0;
  const covered = unionArea(visibleHud);
  const worldRatio = layout.documentViewport.width > 0 && layout.documentViewport.height > 0
    ? (terrainArea - covered) / (layout.documentViewport.width * layout.documentViewport.height)
    : 0;
  const file = path.join(out, `kingdom-stone-${size.name}.png`);
  await page.screenshot({ path: file });
  report.measurements.push({
    size: size.name,
    requested: size,
    layout,
    terrainInsideViewportArea: terrainArea,
    hudUnionOnTerrain: covered,
    visibleWorldRatio: worldRatio,
    meets80Percent: worldRatio >= 0.8,
    scope: 'optimistic zero-inset rectangle accounting; transparent gaps excluded; safe-area, hit-ancestor, landmark and physical-device checks remain separate',
    file: path.relative(root, file),
  });
  await context.close();
}
await browser.close();
await fs.writeFile(path.join(out, 'kingdom-prominence-live-20261020.json'), JSON.stringify(report, null, 2));
console.log(JSON.stringify({ measurements: report.measurements.map(({ size, layout, visibleWorldRatio, meets80Percent, file }) => ({ size, actual: layout.documentViewport, visibleWorldRatio, meets80Percent, file })), errors: report.errors, report: path.relative(root, path.join(out, 'kingdom-prominence-live-20261020.json')) }, null, 2));
