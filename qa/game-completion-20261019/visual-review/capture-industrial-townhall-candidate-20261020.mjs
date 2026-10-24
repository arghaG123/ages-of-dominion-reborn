import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';

const root = process.cwd();
const asset = '/assets/derivatives/visual-repair-20261020/buildings/industrial/townhall-industrial-candidate-v1.png';
const out = path.join(root, 'qa/game-completion-20261019/visual-review/kingdom-ages-live-20261020');
const prompt = `Use case: stylized-concept
Asset type: transparent production game sprite for an eight-age landscape strategy game
Primary request: create one Industrial Age Town Hall: a single, compact late-19th-century civic building that reads clearly as the town's administrative center.
Scene/backdrop: genuinely transparent background. Isolated asset only.
Subject: a substantial red-brown brick municipal hall with pale limestone trim, a modest central clock tower, tall arched windows, and a clear front entrance. Era-appropriate industrial architecture, refined but believable.
Style/medium: high-quality semi-realistic 3D strategy-game building art with natural material texture, realistic proportions, warm daylight, and grounded photographic lighting.
Composition/framing: elevated three-quarter isometric view showing the front and right sides; no horizon. Center the complete building, keep its small foundation footprint at the bottom center, leave 8% transparent breathing room, and make the building fill most of the square canvas.
Constraints: preserve a clean alpha edge and only a subtle contact shadow directly beneath the compact building footprint. No scenery or ground plane.
Avoid: factories, rail yards, trains, roads, large platforms, surrounding walls, detached outbuildings, people, vehicles, foliage, labels, text, watermarks, green outlines, magenta/black matte, square tiles, deep cast shadows, or clipped architecture.`;
await fs.mkdir(out, { recursive: true });
const sizes = [
  { name: '1280x720', width: 1280, height: 720 },
  { name: '825x375', width: 825, height: 375 },
];
const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
const report = {
  recordedAt: new Date().toISOString(),
  candidate: asset,
  generatedWith: 'Codex built-in image_gen',
  prompt,
  replaces: {
    file: 'assets/derivatives/image-residual-executor-20261007/environment/buildings/industrial/townhall-industrial.png',
    source: 'assets/production/production-01-20261003/images/14-townhall-industrial.png',
    sourceSHA256: '243cd0e8413b10d83567a2849356aeb2a107304a5dddf14fbb937fe5f8fe51fb',
  },
  fixtureKind: 'isolated persisted Industrial age and Town Hall',
  captures: [],
  errors: [],
};

for (const size of sizes) {
  const context = await browser.newContext({ viewport: { width: size.width, height: size.height }, deviceScaleFactor: 1 });
  const page = await context.newPage();
  page.on('pageerror', error => report.errors.push({ viewport: size.name, error: String(error) }));
  page.on('console', message => { if (message.type() === 'error') report.errors.push({ viewport: size.name, error: message.text() }); });
  await page.goto('http://127.0.0.1:4179/', { waitUntil: 'networkidle' });
  for (const choice of ['new-campaign', 'scene-class:knight', 'scene-enter-valley']) await page.locator(`[data-choice="${choice}"]`).click();
  await page.evaluate(async () => {
    const stored = await window.rebornBackground(true);
    if (!stored) throw new Error('Could not durably suspend the fixture campaign before replacing its age');
  });
  const fixture = await page.evaluate(async () => {
    const state = window.rebornSnapshot();
    const data = await (await fetch('/src/data/reference-data.json')).json();
    const save = await import('/src/core/save.js');
    const storage = await import('/src/core/storage-adapter.js');
    state.age = 5;
    state.plots.find(plot => plot.id === 'townhall').level = 7;
    state.resources = { food: 100000, wood: 100000, stone: 100000, gold: 100000 };
    state.walls.level = 2;
    state.revision++;
    const adapter = new storage.IndexedDBStorageAdapter(window.indexedDB, 'aod-reborn-db');
    const before = await adapter.loadLive(data);
    if (before.status !== 'VALID') throw new Error(`Fixture source save is ${before.status}`);
    const head = await adapter.replace(before.head, save.encode(state, data), data, 'kingdom');
    return { age: state.age, hallLevel: state.plots.find(plot => plot.id === 'townhall').level, wallLevel: state.walls.level, revision: head.revision };
  });
  await page.reload({ waitUntil: 'networkidle' });
  await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'kingdom' && document.querySelector('#world image[aria-label="Town Hall"]'));
  await page.evaluate(async () => {
    const stored = await window.rebornBackground(true);
    if (!stored) throw new Error('Could not durably suspend the rendered Industrial fixture');
  });
  const rendered = await page.evaluate(async assetUrl => {
    const response = await fetch(assetUrl);
    if (!response.ok) throw new Error(`Candidate returned ${response.status}`);
    const image = document.querySelector('#world image[aria-label="Town Hall"]');
    if (!image) throw new Error('Live Town Hall layer is missing');
    const [data, contract, projection, sizing] = await Promise.all([
      (await fetch('/src/data/reference-data.json')).json(),
      (await fetch('/src/data/implementation-contract.json')).json(),
      import('/src/client/projection.js'),
      import('/src/client/visible-size.js'),
    ]);
    const site = contract.geometry.kingdom.sites.find(row => row.id === 'townhall');
    const [x, y, width, height] = site.rect;
    const matrix = contract.geometry.kingdom.worldToSource;
    const feet = projection.project(matrix, [x + width / 2, y + height]);
    const left = projection.project(matrix, [x, y + height]);
    const right = projection.project(matrix, [x + width, y + height]);
    const oldRect = image.getBoundingClientRect();
    const oldWidth = Number(image.getAttribute('width'));
    const oldHeight = Number(image.getAttribute('height'));
    const oldY = Number(image.getAttribute('y'));
    const scale = oldRect.width / oldWidth;
    const offsetY = oldRect.y - oldY * scale;
    const source = { width: 1254, height: 1254, foot: [0.5, 0.95], maxVisibleCssPx: 180 };
    const padWidth = Math.hypot(right[0] - left[0], right[1] - left[1]) || 1;
    const requestedHeight = padWidth * 1.08 * source.height / source.width;
    const fitted = sizing.footAwareVisibleBox(source, requestedHeight, scale, feet[1], offsetY, 12);
    image.setAttribute('href', assetUrl);
    image.setAttribute('x', feet[0] - source.foot[0] * fitted.width);
    image.setAttribute('y', feet[1] - source.foot[1] * fitted.height);
    image.setAttribute('width', fitted.width);
    image.setAttribute('height', fitted.height);
    image.setAttribute('data-candidate-version', 'industrial-townhall-v1');
    await new Promise((resolve, reject) => {
      const probe = new Image();
      probe.onload = resolve;
      probe.onerror = () => reject(new Error('Candidate image failed to decode'));
      probe.src = assetUrl;
    });
    const rect = image.getBoundingClientRect();
    return {
      view: document.querySelector('#app')?.dataset.view,
      age: window.rebornSnapshot()?.age,
      hallLevel: window.rebornSnapshot()?.plots?.find(plot => plot.id === 'townhall')?.level,
      source: image.getAttribute('href'),
      world: ['x', 'y', 'width', 'height'].map(key => Number(image.getAttribute(key))),
      screen: [rect.x, rect.y, rect.width, rect.height],
      candidateDecoded: true,
      safeTopPx: rect.y,
    };
  }, asset);
  assert.equal(rendered.view, 'kingdom');
  assert.equal(rendered.age, 5);
  assert.equal(rendered.hallLevel, 7);
  assert.ok(rendered.safeTopPx >= 12 - 0.01);
  const file = path.join(out, `industrial-townhall-candidate-v1-${size.name}.png`);
  await page.screenshot({ path: file });
  report.captures.push({ viewport: size.name, fixture, rendered, file: path.relative(root, file) });
  await context.close();
}

await browser.close();
await fs.writeFile(path.join(out, 'industrial-townhall-candidate-v1.json'), JSON.stringify(report, null, 2));
assert.deepEqual(report.errors, []);
console.log(JSON.stringify({ captures: report.captures.length, errors: report.errors, report: path.relative(root, path.join(out, 'industrial-townhall-candidate-v1.json')) }, null, 2));
