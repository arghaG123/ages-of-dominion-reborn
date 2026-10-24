import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';

const root = process.cwd();
const out = path.join(root, 'qa/game-completion-20261019/visual-review/kingdom-ages-live-20261020');
const candidates = [
  {
    name: 'gunpowder', age: 4, hallLevel: 6,
    asset: '/assets/derivatives/visual-repair-20261020/buildings/gunpowder/townhall-gunpowder-candidate-v1.png',
    sha256: 'a89172e609aa5bb559b24a93c640ae11996ff340dfd3724432f6c1f7a7e21091',
    width: 1254, height: 1254, foot: [0.5, 0.95],
    prompt: `Use case: stylized-concept
Asset type: transparent production game sprite for an eight-age landscape strategy game
Primary request: one Gunpowder Age Town Hall, a single late-17th-century civic seat for a growing walled town.
Scene/backdrop: genuinely transparent background. Isolated asset only.
Subject: a compact, symmetrical red-brown brick and warm limestone civic hall with a modest central clock/bell cupola, a clear public entrance, tall period windows, and restrained Baroque stone detail. It should read as an administrative town hall, not a military fortress.
Style/medium: high-quality semi-realistic 3D strategy-game building art with convincing masonry, slate, and carved-stone textures; natural warm daylight; grounded photographic lighting.
Composition/framing: elevated three-quarter isometric game-camera view showing the front and right sides, with a moderate top-down angle and no horizon. Center the complete building; keep the small foundation footprint at bottom center; leave useful transparent breathing room; make the subject fill most of a square canvas.
Constraints: genuinely transparent clean alpha edges and only a subtle contact shadow directly beneath the compact footprint. No scenery or ground plane.
Avoid: castle complexes, curtain walls, ramparts, gatehouses, detached outbuildings, large platforms, yards, roads, people, vehicles, trees, labels, text, watermarks, green outlines, magenta/black matte, exaggerated scale, or clipped architecture.`,
    replaces: {
      file: 'assets/derivatives/image-residual-executor-20261007/environment/buildings/gunpowder/townhall-gunpowder.png',
      source: 'assets/production/production-01-20261003/images/13-townhall-gunpowder.png',
      sourceSHA256: '941fea03f24ef7387cdc52d8b120bf3821e54bd5758955dee1badc3dd1b7946d',
    },
  },
  {
    name: 'modern', age: 6, hallLevel: 8,
    asset: '/assets/derivatives/visual-repair-20261020/buildings/modern/townhall-modern-candidate-v1.png',
    sha256: 'b63a3c2276f77dd8926fdd555e64c038813849401c67bfb095f97c3712c8b8fb',
    width: 1254, height: 1254, foot: [0.5, 0.877],
    prompt: `Use case: stylized-concept
Asset type: transparent production game sprite for an eight-age landscape strategy game
Primary request: one contemporary Modern Age Town Hall for the central civic district of a thriving 21st-century city.
Scene/backdrop: genuinely transparent background. Isolated asset only.
Subject: a distinctive low-rise civic hall with pale warm stone, clear glass curtain walls, an elegant public entrance, a modest stepped roofline and one restrained civic clock feature. It should look like an accessible city administration building, not a corporate skyscraper.
Style/medium: high-quality semi-realistic 3D strategy-game building art, natural concrete and glass materials, realistic scale and proportions, daylight with controlled soft shadows, matching premium environmental game art.
Composition/framing: elevated three-quarter isometric game-camera view showing the front and right sides at a moderate top-down angle, no horizon. Center the complete building, keep its compact foundation footprint at bottom center, leave useful transparent breathing room, and fill most of a square canvas.
Constraints: genuinely transparent clean alpha edges; only a subtle contact shadow directly beneath the compact building footprint. No ground plane or environment.
Avoid: black slabs, opaque shadow rectangles, office towers, roads, parking lots, large platforms, surrounding walls, extra buildings, people, vehicles, trees, labels, text, watermarks, green outlines, magenta/black matte, or clipped architecture.`,
    replaces: {
      file: 'assets/derivatives/image-residual-executor-20261007/environment/buildings/modern/townhall-modern.png',
      source: 'assets/production/production-01-20261003/images/15-townhall-modern.png',
      sourceSHA256: 'a35479785aecf268668716c3e5b1ef8866743b0f380d926e0437ff149a6cde73',
    },
  },
];
const sizes = [
  { name: '1280x720', width: 1280, height: 720 },
  { name: '825x375', width: 825, height: 375 },
];
await fs.mkdir(out, { recursive: true });
const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
const report = { recordedAt: new Date().toISOString(), fixtureKind: 'isolated persisted age and Town Hall', generatedWith: 'Codex built-in image_gen', candidates, captures: [], errors: [] };

for (const candidate of candidates) for (const size of sizes) {
  const context = await browser.newContext({ viewport: { width: size.width, height: size.height }, deviceScaleFactor: 1 });
  const page = await context.newPage();
  page.on('pageerror', error => report.errors.push({ viewport: size.name, age: candidate.name, error: String(error) }));
  page.on('console', message => { if (message.type() === 'error') report.errors.push({ viewport: size.name, age: candidate.name, error: message.text() }); });
  await page.goto('http://127.0.0.1:4179/', { waitUntil: 'networkidle' });
  for (const choice of ['new-campaign', 'scene-class:knight', 'scene-enter-valley']) await page.locator(`[data-choice="${choice}"]`).click();
  await page.evaluate(async () => {
    const stored = await window.rebornBackground(true);
    if (!stored) throw new Error('Could not durably suspend the fixture campaign before replacing its age');
  });
  const fixture = await page.evaluate(async ({ age, hallLevel }) => {
    const state = window.rebornSnapshot();
    const data = await (await fetch('/src/data/reference-data.json')).json();
    const save = await import('/src/core/save.js');
    const storage = await import('/src/core/storage-adapter.js');
    state.age = age;
    state.plots.find(plot => plot.id === 'townhall').level = hallLevel;
    state.resources = { food: 100000, wood: 100000, stone: 100000, gold: 100000 };
    state.walls.level = 2;
    state.revision++;
    const adapter = new storage.IndexedDBStorageAdapter(window.indexedDB, 'aod-reborn-db');
    const before = await adapter.loadLive(data);
    if (before.status !== 'VALID') throw new Error(`Fixture source save is ${before.status}`);
    const head = await adapter.replace(before.head, save.encode(state, data), data, 'kingdom');
    return { age: state.age, hallLevel: state.plots.find(plot => plot.id === 'townhall').level, wallLevel: state.walls.level, revision: head.revision };
  }, { age: candidate.age, hallLevel: candidate.hallLevel });
  await page.reload({ waitUntil: 'networkidle' });
  await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'kingdom' && document.querySelector('#world image[aria-label="Town Hall"]'));
  await page.evaluate(async () => {
    const stored = await window.rebornBackground(true);
    if (!stored) throw new Error('Could not durably suspend the rendered Town Hall fixture');
  });
  const rendered = await page.evaluate(async candidate => {
    const response = await fetch(candidate.asset);
    if (!response.ok) throw new Error(`Candidate returned ${response.status}`);
    const bytes = await response.arrayBuffer();
    const digest = Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', bytes)), value => value.toString(16).padStart(2, '0')).join('');
    if (digest !== candidate.sha256) throw new Error(`Candidate SHA256 mismatch: ${digest}`);
    const image = document.querySelector('#world image[aria-label="Town Hall"]');
    if (!image) throw new Error('Live Town Hall layer is missing');
    const [contract, projection, sizing] = await Promise.all([
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
    const oldY = Number(image.getAttribute('y'));
    const scale = oldRect.width / oldWidth;
    const offsetY = oldRect.y - oldY * scale;
    const source = { width: candidate.width, height: candidate.height, foot: candidate.foot, maxVisibleCssPx: 180 };
    const padWidth = Math.hypot(right[0] - left[0], right[1] - left[1]) || 1;
    const requestedHeight = padWidth * 1.08 * source.height / source.width;
    const fitted = sizing.footAwareVisibleBox(source, requestedHeight, scale, feet[1], offsetY, 12);
    image.setAttribute('href', candidate.asset);
    image.setAttribute('x', feet[0] - source.foot[0] * fitted.width);
    image.setAttribute('y', feet[1] - source.foot[1] * fitted.height);
    image.setAttribute('width', fitted.width);
    image.setAttribute('height', fitted.height);
    image.setAttribute('data-candidate-version', `${candidate.name}-townhall-v1`);
    await new Promise((resolve, reject) => {
      const probe = new Image();
      probe.onload = resolve;
      probe.onerror = () => reject(new Error('Candidate image failed to decode'));
      probe.src = candidate.asset;
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
      hashVerified: digest,
      safeTopPx: rect.y,
    };
  }, candidate);
  assert.equal(rendered.view, 'kingdom');
  assert.equal(rendered.age, candidate.age);
  assert.equal(rendered.hallLevel, candidate.hallLevel);
  assert.ok(rendered.safeTopPx >= 12 - 0.01);
  const file = path.join(out, `${candidate.name}-townhall-candidate-v1-${size.name}.png`);
  await page.screenshot({ path: file });
  report.captures.push({ candidate: candidate.name, viewport: size.name, fixture, rendered, file: path.relative(root, file) });
  await context.close();
}

await browser.close();
await fs.writeFile(path.join(out, 'other-townhall-candidates-live-20261020.json'), JSON.stringify(report, null, 2));
assert.deepEqual(report.errors, []);
console.log(JSON.stringify({ captures: report.captures.length, errors: report.errors, report: path.relative(root, path.join(out, 'other-townhall-candidates-live-20261020.json')) }, null, 2));
