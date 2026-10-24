import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import modeScenes from '../../../src/data/mode-scenes.json' with { type: 'json' };
import { checksum } from '../../../src/core/save.js';

const root = process.cwd();
const age = Number(process.argv[2] || 3);
const candidate = path.resolve(process.argv[3] || 'assets/derivatives/visual-repair-20261020/scenes/tactical-medieval-clean-candidate-v1.png');
const selectedSource = modeScenes.tactical[age];
const selectedFile = path.resolve(selectedSource);
const isBoundCandidate = selectedFile === candidate;
const sizes = [
  { name: '825x375', width: 825, height: 375 },
  { name: '933x424', width: 933, height: 424 },
  { name: '1280x720', width: 1280, height: 720 },
];
assert.ok(Number.isInteger(age) && age >= 0 && age < 8);
await fs.access(candidate);
const out = path.join(root, `qa/game-completion-20261020/visual-review/${isBoundCandidate ? `tactical-clean-live-age${age}` : `tactical-clean-candidate-age${age}`}`);
await fs.mkdir(out, { recursive: true });
const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
const reference = JSON.parse(await fs.readFile(path.join(root, 'qa/game-completion-20261020/visual-review/tactical-age6-visual-fixture.json'), 'utf8'));
const state = structuredClone(JSON.parse(reference.payload));
state.id = `tactical-clean-candidate-age${age}-visual-review`;
state.age = age;
const payload = JSON.stringify(state);
const fixturePath = path.join(out, 'fixture.json');
await fs.writeFile(fixturePath, JSON.stringify({ schema: 1, payload, checksum: checksum(payload) }));
const runs = [];

try {
  for (const size of sizes) {
    const context = await browser.newContext({ viewport: { width: size.width, height: size.height }, deviceScaleFactor: 1 });
    const page = await context.newPage();
    const errors = [];
    const failedResponses = [];
    page.on('pageerror', error => errors.push(String(error)));
    page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
    page.on('response', response => { if (response.status() >= 400) failedResponses.push(`${response.status()} ${response.url()}`); });
    const source = modeScenes.tactical[age];
    if (!isBoundCandidate) await page.route(`**/${path.posix.basename(source)}`, route => route.fulfill({ path: candidate, contentType: 'image/png' }));
    await page.goto('http://127.0.0.1:4179/', { waitUntil: 'networkidle' });
    await page.locator('#import-file').setInputFiles(fixturePath);
    await page.waitForFunction(expectedAge => window.rebornSnapshot()?.age === expectedAge, age);
    await page.locator('[data-choice="nav:war"]').click();
    await page.locator('[data-choice="start-skirmish"]').click();
    await page.waitForFunction(() => window.rebornSnapshot()?.battle?.status === 'ACTIVE');
    await page.waitForFunction(() => document.querySelector('#terrain')?.complete && document.querySelector('#terrain')?.naturalWidth > 0);
    await page.waitForTimeout(120);
    const runtime = await page.evaluate(() => {
      const terrain = document.querySelector('#terrain');
      const world = document.querySelector('#world');
      return {
        age: window.rebornSnapshot()?.age,
        battle: window.rebornSnapshot()?.battle?.status,
        terrainSource: terrain?.getAttribute('src'),
        naturalSize: terrain ? [terrain.naturalWidth, terrain.naturalHeight] : null,
        board: world?.getAttribute('data-board'),
        cellCount: world?.querySelectorAll('[data-cell]').length ?? 0,
        visibleCellCount: [...(world?.querySelectorAll('[data-cell]') ?? [])].filter(node => {
          const r = node.getBoundingClientRect();
          return r.width > 1 && r.height > 1 && r.right > 0 && r.bottom > 0 && r.left < innerWidth && r.top < innerHeight;
        }).length,
      };
    });
    assert.equal(runtime.age, age);
    assert.equal(runtime.battle, 'ACTIVE');
    assert.equal(runtime.terrainSource, source);
    assert.deepEqual(runtime.naturalSize, [1678, 937]);
    assert.equal(runtime.board, 'tactical-painted-v1');
    assert.ok(runtime.cellCount >= 70);
    assert.deepEqual(errors, []);
    assert.deepEqual(failedResponses, []);
    const screenshot = path.join(out, `${size.name}.png`);
    await page.screenshot({ path: screenshot });
    runs.push({ viewport: [size.width, size.height], runtime, screenshot: path.relative(root, screenshot), errors, failedResponses });
    await context.close();
  }
} finally {
  await browser.close();
}

const report = {
  recordedAt: new Date().toISOString(),
  classification: isBoundCandidate ? 'BOUND_TACTICAL_SCENE_LIVE_SOURCE_REVIEW_NOT_OWNER_ACCEPTANCE' : 'IMAGEGEN_TACTICAL_SCENE_CANDIDATE_LIVE_REVIEW_NOT_BOUND_OR_ACCEPTED',
  age,
  selectedPathAtRun: selectedSource,
  candidate: path.relative(root, candidate),
  boundInModeScenes: isBoundCandidate,
  originalFixture: path.relative(root, fixturePath),
  visualLimit: 'Live browser screenshots and cell overlays are reviewed manually; this capture does not prove exact terrain-cell registration or owner acceptance.',
  runs,
};
await fs.writeFile(path.join(out, 'report.json'), JSON.stringify(report, null, 2));
console.log(JSON.stringify({ classification: report.classification, age, candidate: report.candidate, captures: runs.length, errors: runs.reduce((n, run) => n + run.errors.length, 0), failedResponses: runs.reduce((n, run) => n + run.failedResponses.length, 0), report: path.relative(root, path.join(out, 'report.json')) }, null, 2));
