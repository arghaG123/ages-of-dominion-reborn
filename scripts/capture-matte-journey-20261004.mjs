import { spawn } from 'node:child_process';
import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import data from '../src/data/reference-data.json' with { type: 'json' };
import contract from '../src/data/implementation-contract.json' with { type: 'json' };
import { newCampaign, command, advance } from '../src/core/campaign.js';
import { encode } from '../src/core/save.js';

const port = 4192;
const base = `http://127.0.0.1:${port}`;
const outDir = fileURLToPath(new URL('../qa/code-matte-journey-20261004/', import.meta.url));
await mkdir(outDir, { recursive: true });
await mkdir(path.join(outDir, 'crops'), { recursive: true });
await mkdir(path.join(outDir, 'checkpoints'), { recursive: true });
await mkdir(path.join(outDir, 'frames'), { recursive: true });

const now = 1_700_000_000_000;
let forgeState = newCampaign(contract, data, now);
forgeState.resources = { food: 5000, wood: 5000, stone: 5000, gold: 5000 };
forgeState = command(forgeState, { id: 'armory', type: 'BUILD', payload: { plotId: 'P05', building: 'armory' } }, now, data);
forgeState = advance(forgeState, forgeState.buildJobs[0].completesAt, data);
const forgeFile = path.join(outDir, 'checkpoints', 'forge-fixture.json');
await writeFile(forgeFile, encode(forgeState, data));

let ageState = newCampaign(contract, data, now, 20261004);
ageState.plots.find(plot => plot.id === 'townhall').level = 8;
ageState.resources = { food: 500000, wood: 500000, stone: 500000, gold: 500000 };
const ageFile = path.join(outDir, 'checkpoints', 'age-fixture-stone.json');
await writeFile(ageFile, encode(ageState, data));

const server = spawn(process.execPath, ['scripts/serve.mjs', '--port', String(port)], { stdio: ['ignore', 'pipe', 'pipe'] });
process.on('exit', () => server.kill());
await new Promise((resolve, reject) => {
  const timer = setTimeout(() => reject(new Error('preview server did not start')), 8000);
  server.stdout.on('data', chunk => {
    if (String(chunk).includes(String(port))) { clearTimeout(timer); resolve(); }
  });
  server.stderr.on('data', chunk => {
    if (String(chunk).includes('already in use')) { clearTimeout(timer); reject(new Error(String(chunk))); }
  });
});

const report = {
  seed: 123456789,
  ageFixtureSeed: 20261004,
  acceleration: {
    construction: 'none — live build clock',
    siege: 'in-game Speed 2x only',
    endless: 'in-game Speed 2x only',
    ages: 'FIXTURE — Town Hall level 8 and 500000 of each resource injected before import. Age clicks are the live Advance age control.',
    forge: 'FIXTURE — Armory built and 5000 of each resource injected. Equip, unequip, swap and reload use the Forge controls.',
  },
  steps: [],
  failures: [],
  frames: [],
};
const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
const page = await browser.newPage({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1 });
page.on('dialog', dialog => dialog.accept());

async function shot(target, name) {
  const file = path.join(outDir, name);
  const buffer = await target.screenshot({ type: 'png' });
  await writeFile(file, buffer);
  return { file: path.basename(file), sha256: crypto.createHash('sha256').update(buffer).digest('hex'), width: buffer.readUInt32BE(16), height: buffer.readUInt32BE(20) };
}
async function crop(name, selector) {
  const box = await page.evaluate(sel => {
    const node = document.querySelector(sel);
    if (!node) return null;
    const rect = node.getBoundingClientRect();
    return { x: rect.x, y: rect.y, width: rect.width, height: rect.height };
  }, selector);
  if (!box || box.width < 2 || box.height < 2) return null;
  const view = page.viewportSize();
  const x = Math.max(0, Math.min(box.x, view.width - 1));
  const y = Math.max(0, Math.min(box.y, view.height - 1));
  const width = Math.max(1, Math.min(box.width, view.width - x));
  const height = Math.max(1, Math.min(box.height, view.height - y));
  const file = path.join(outDir, 'crops', name);
  const buffer = await page.screenshot({ type: 'png', clip: { x, y, width, height } });
  await writeFile(file, buffer);
  return { file: `crops/${name}`, sha256: crypto.createHash('sha256').update(buffer).digest('hex'), width, height };
}
async function note(name) {
  const message = await page.locator('#message').textContent();
  const selected = await page.locator('#selected').textContent();
  const status = await page.locator('#status').textContent();
  const image = await shot(page, name);
  report.steps.push({ name, message, selected, status, image });
  return message || '';
}
async function openPanel() {
  if (!await page.locator('#panel').evaluate(node => node.classList.contains('open'))) await page.click('#context');
}
async function closePanel() {
  if (await page.locator('#panel').evaluate(node => node.classList.contains('open'))) await page.click('#context');
}
async function clickChoice(choice) {
  await openPanel();
  await page.evaluate(id => {
    const node = document.querySelector(`[data-choice="${id}"]`);
    if (!node) throw new Error('missing choice ' + id);
    node.click();
  }, choice);
}
async function clickText(text) {
  await openPanel();
  const clicked = await page.evaluate(label => {
    const node = [...document.querySelectorAll('button')].find(button => button.textContent.includes(label) && !button.disabled);
    if (!node) return false;
    node.click();
    return true;
  }, text);
  if (!clicked) throw new Error('missing button ' + text);
}
async function buildAndWait(plot, type) {
  await page.evaluate(id => {
    const node = document.querySelector(`[aria-label^="${id}:"]`);
    if (!node) throw new Error('missing plot ' + id);
    node.dispatchEvent(new MouseEvent('click', { bubbles: true }));
  }, plot);
  await clickChoice(`build:${plot}:${type}`);
  await page.waitForTimeout(4600);
  return note(`build-${type}.png`);
}
async function importSave(file) {
  await clickChoice('nav:home');
  await page.setInputFiles('#import-file', file);
  await page.waitForTimeout(300);
}

await page.goto(base + '/', { waitUntil: 'networkidle' });
await page.evaluate(() => localStorage.clear());
await page.reload({ waitUntil: 'networkidle' });
await clickChoice('new-campaign');
await note('01-knight-pending.png');
if (!await page.locator('[data-card-status="pending-review"]').count()) report.failures.push('pending knight card missing');
if (!await page.locator('[data-card-label="pending-ancient-knight"]').count()) report.failures.push('pending knight label missing');
await crop('knight-pending-card.png', '[data-card-status="pending-review"]');

const sizes = [[825, 375], [933, 424], [1180, 820], [1280, 720]];
for (const [width, height] of sizes) {
  await page.setViewportSize({ width, height });
  await openPanel();
  const opened = await shot(page, `${width}x${height}-hero-panel-open.png`);
  await closePanel();
  const closed = await shot(page, `${width}x${height}-hero-panel-closed.png`);
  const buttons = await page.locator('button').evaluateAll(nodes => nodes.map(node => {
    const box = node.getBoundingClientRect();
    return { choice: node.dataset.choice || node.id || node.textContent, width: box.width, height: box.height };
  }));
  const short = buttons.filter(button => button.height > 0 && (button.height < 47.5 || button.width < 47.5));
  if (short.length) report.failures.push(`${width}x${height} hero short controls ${JSON.stringify(short.slice(0, 3))}`);
  report.steps.push({ name: `hero-${width}x${height}`, opened, closed, short: short.length });
}
await page.setViewportSize({ width: 1280, height: 720 });

await clickChoice('class:ranger');
await clickChoice('clip:walk');
await closePanel();
await page.waitForTimeout(350);
await note('02-ranger-walk.png');
for (let frame = 0; frame < 4; frame += 1) {
  report.frames.push({ name: `ranger-walk-${frame}`, image: await shot(page, `frames/ranger-walk-${frame}.png`) });
  await page.waitForTimeout(180);
}
if (!await page.locator('[data-articulation="painted-partial"]').count()) report.failures.push('ranger painted figure missing');
await clickChoice('enter-valley');
await page.waitForSelector('[data-walls="unbuilt"]');
await closePanel();
await note('03-kingdom-day1.png');

for (const [plot, type] of [['P01', 'lumber'], ['P02', 'farm'], ['P03', 'quarry'], ['P04', 'barracks']]) {
  const message = await buildAndWait(plot, type);
  const selected = await page.locator('#selected').textContent();
  if (!selected.toLowerCase().includes(type === 'lumber' ? 'lumber' : type)) report.failures.push(`build ${type}: ${selected} / ${message}`);
}
await clickChoice('nav:army');
await clickChoice('recruit:melee');
await note('04-recruited.png');
await clickChoice('plate-review-next');
await clickChoice('plate-review-next');
await closePanel();
await note('05-iron-plate-review.png');
const ironHeavy = await page.locator('[data-plate-review="2-heavy"]').count();
if (!ironHeavy) report.failures.push('iron heavy review missing');
const ironPlate = await page.locator('[data-plate="assets/derivatives/actors/v4/troop-iron-heavy.png"]').count();
if (!ironPlate) report.failures.push('v4 iron elephant is not the iron heavy consumer');
await crop('iron-heavy.png', '[data-plate="assets/derivatives/actors/v4/troop-iron-heavy.png"]');
for (let step = 0; step < 2; step += 1) await clickChoice('plate-review-next');
await closePanel();
await note('06-gunpowder-plate-review.png');
if (!await page.locator('[data-plate="assets/derivatives/actors/v4/troop-gunpowder-heavy.png"]').count()) report.failures.push('v4 cannon is not the gunpowder heavy consumer');
await crop('gunpowder-heavy.png', '[data-plate="assets/derivatives/actors/v4/troop-gunpowder-heavy.png"]');
for (let step = 0; step < 3; step += 1) await clickChoice('plate-review-next');
await closePanel();
await note('07-future-plate-review.png');
if (!await page.locator('[data-plate="assets/derivatives/actors/v4/troop-future-ranged.png"]').count()) report.failures.push('v4 future ranged missing');
if (!await page.locator('[data-plate="assets/derivatives/actors/v4/troop-future-heavy.png"]').count()) report.failures.push('v4 future heavy missing');
if (!await page.locator('[data-mount-review="hero-mount-future-transport"]').count()) report.failures.push('future transport review missing');
await crop('future-ranged.png', '[data-plate="assets/derivatives/actors/v4/troop-future-ranged.png"]');
await crop('future-heavy.png', '[data-plate="assets/derivatives/actors/v4/troop-future-heavy.png"]');
await crop('future-transport.png', '[data-mount="hero-mount-future-transport"]');

await clickChoice('nav:adventure');
await clickChoice('enter-adventure');
for (const choice of ['preview-east', 'preview-east', 'preview-north', 'preview-north', 'preview-north']) await clickChoice(choice);
await clickChoice('confirm-route');
await page.waitForTimeout(700);
const confirmAgain = page.locator('[data-choice="confirm-route"]');
if (await confirmAgain.count() && await confirmAgain.isEnabled()) {
  await confirmAgain.click();
  report.failures.push('second confirm stayed enabled');
}
await closePanel();
await note('08-mounted-travel.png');
const horse = await page.locator('[data-mount="horse"]').first();
const rider = await page.locator('[data-rider="painted-partial"]').first();
report.steps.push({
  name: 'mount-attributes',
  gait: await horse.getAttribute('data-gait'),
  hooves: await horse.getAttribute('data-hoof-articulation'),
  moving: await horse.getAttribute('data-moving'),
  rider: await rider.count() ? await rider.getAttribute('data-rider') : null,
  mountMark: await rider.count() ? await rider.getAttribute('data-mount-mark') : null,
});
if ((await horse.getAttribute('data-gait')) !== 'single-pose') report.failures.push('horse gait is not single-pose');
await crop('mounted-horse.png', '[data-mount="horse"]');
await crop('mounted-rider.png', '[data-rider="painted-partial"]');
for (let frame = 0; frame < 4; frame += 1) {
  report.frames.push({ name: `mount-${frame}`, image: await shot(page, `frames/mount-${frame}.png`) });
  await page.waitForTimeout(180);
}
if (await page.locator('[data-choice="begin-encounter"]').count()) await clickChoice('begin-encounter');
else report.failures.push('guard encounter did not open');
let settled = false;
for (let turn = 0; turn < 24 && !settled; turn += 1) {
  await openPanel();
  const action = await page.evaluate(() => {
    const buttons = [...document.querySelectorAll('button')];
    const apply = buttons.find(button => button.textContent.includes('Apply the battle result'));
    if (apply) { apply.click(); return 'apply'; }
    const melee = buttons.find(button => button.textContent.startsWith('Melee '));
    if (melee) { melee.click(); return 'melee'; }
    const move = buttons.find(button => button.textContent.startsWith('Move '));
    if (move) { move.click(); return 'move'; }
    const defend = buttons.find(button => button.textContent === 'Defend');
    if (defend) { defend.click(); return 'defend'; }
    return 'stuck';
  });
  if (action === 'apply') { settled = true; break; }
  if (action === 'stuck') break;
  await page.waitForTimeout(150);
}
await note('09-after-tactical.png');
if (!settled) report.failures.push('manual tactical did not reach settlement');
const equip = page.locator('[data-choice^="equip:"]');
if (await equip.count()) {
  const before = await page.evaluate(() => window.rebornSnapshot());
  await openPanel();
  await equip.first().click();
  const after = await page.evaluate(() => window.rebornSnapshot());
  await note('10-natural-equip.png');
  report.steps.push({ name: 'natural-equip-stats', beforeAttack: before?.hero, afterEquip: after?.hero?.equip, bag: after?.inventory?.length });
  await clickText('Unequip');
  const unequipped = await page.evaluate(() => window.rebornSnapshot());
  await note('11-natural-unequip.png');
  if (Object.values(unequipped.hero.equip).some(Boolean)) report.failures.push('natural unequip left an item worn');
  if (!unequipped.inventory.length) report.failures.push('natural unequip did not return the item');
  await clickChoice('nav:home');
  await clickText('Save slot 1');
  await page.reload({ waitUntil: 'networkidle' });
  await clickChoice('nav:home');
  await clickText('Load slot 1');
  const reloaded = await page.evaluate(() => window.rebornSnapshot());
  await note('12-natural-reload.png');
  if (reloaded.inventory.length !== unequipped.inventory.length) report.failures.push('natural reload lost the bag item');
} else report.steps.push({ name: 'natural-loot', message: 'The battle roll added no bag item. The six-slot fixture covers equip.' });

await clickChoice('nav:war');
await clickChoice('start-siege');
await page.waitForTimeout(400);
await clickText('Speed 2x');
await clickText('Pause');
await note('13-siege-paused.png');
const paused = await page.locator('#message').textContent();
await clickText('Resume');
await note('14-siege-resumed.png');
let siegeSettled = false;
for (let i = 0; i < 80 && !siegeSettled; i += 1) {
  const apply = page.locator('button', { hasText: 'Apply the defense result' });
  if (await apply.count()) { await openPanel(); await page.evaluate(() => [...document.querySelectorAll('button')].find(button => button.textContent.includes('Apply the defense result'))?.click()); siegeSettled = true; break; }
  await page.waitForTimeout(500);
}
await note('15-siege-settled.png');
const siegeState = await page.evaluate(() => window.rebornSnapshot());
report.steps.push({ name: 'siege-result', paused, settled: siegeSettled, age: siegeState?.age, defense: siegeState?.defense, flags: siegeState?.story?.flags });
if (!siegeSettled) report.failures.push('finite siege did not reach settlement');
if (siegeState?.defense) report.failures.push('siege session remained after settlement');
await clickChoice('nav:home');
await clickText('Save slot 1');
await page.reload({ waitUntil: 'networkidle' });
await clickChoice('nav:home');
await clickText('Load slot 1');
const siegeReload = await page.evaluate(() => window.rebornSnapshot());
await note('16-siege-reload.png');
if (siegeReload?.defense) report.failures.push('siege reload restored an open defense');

await clickChoice('nav:war');
await clickText('Endless');
await page.waitForTimeout(2500);
await clickText('Speed 2x');
await note('17-endless-running.png');
await clickText('Pause');
await note('18-endless-paused.png');
await page.waitForTimeout(800);
await clickText('Resume');
let endlessSettled = false;
for (let i = 0; i < 80 && !endlessSettled; i += 1) {
  const apply = page.locator('button', { hasText: 'Apply the defense result' });
  if (await apply.count()) { await openPanel(); await page.evaluate(() => [...document.querySelectorAll('button')].find(button => button.textContent.includes('Apply the defense result'))?.click()); endlessSettled = true; break; }
  await page.waitForTimeout(500);
}
await note('19-endless-settled.png');
const endlessState = await page.evaluate(() => window.rebornSnapshot());
const endlessFlag = Object.entries(endlessState?.story?.flags || {}).find(([key]) => key.startsWith('endless:'));
report.steps.push({ name: 'endless-result', settled: endlessSettled, flag: endlessFlag, defense: endlessState?.defense });
if (!endlessSettled) report.failures.push('endless did not reach its core-loss settlement');
if (!endlessFlag) report.failures.push('endless settlement did not record a wave flag');

await importSave(forgeFile);
await note('20-forge-fixture-imported.png');
const attacks = [];
for (const slot of ['helm', 'weapon', 'offhand', 'armor', 'boots', 'accessory']) {
  await clickChoice('nav:forge');
  await clickChoice(`forge-slot:${slot}`);
  await clickChoice('forge-confirm');
  const bag = await page.evaluate(() => window.rebornSnapshot());
  const item = bag.inventory.find(entry => entry.slot === slot);
  if (!item) { report.failures.push(`forge produced no ${slot}`); continue; }
  await clickChoice(`equip:${item.id}`);
  await clickChoice('nav:hero');
  attacks.push({ slot, message: await page.locator('#message').textContent() });
}
await note('21-six-slots-worn.png');
const worn = await page.evaluate(() => window.rebornSnapshot());
if (Object.values(worn.hero.equip).filter(Boolean).length !== 6) report.failures.push('six slots were not worn');
await clickChoice('nav:forge');
await clickChoice('forge-slot:weapon');
await clickChoice('forge-confirm');
const swapBag = await page.evaluate(() => window.rebornSnapshot());
const spare = swapBag.inventory.find(entry => entry.slot === 'weapon');
if (!spare) report.failures.push('swap forge did not put a weapon in the bag');
else await clickChoice(`equip:${spare.id}`);
const swapped = await page.evaluate(() => window.rebornSnapshot());
if (!swapped.inventory.some(entry => entry.slot === 'weapon')) report.failures.push('equip swap did not return the worn weapon');
await clickText('Unequip Weapon');
await clickChoice('nav:home');
await clickText('Save slot 2');
await page.reload({ waitUntil: 'networkidle' });
await clickChoice('nav:home');
await clickText('Load slot 2');
const forgeReload = await page.evaluate(() => window.rebornSnapshot());
await note('22-forge-reload.png');
report.steps.push({ name: 'forge-stats', attacks, worn: forgeReload?.hero?.equip, bag: forgeReload?.inventory?.map(item => item.slot) });
if (forgeReload?.hero?.equip?.weapon) report.failures.push('weapon unequip did not persist');
if (Object.values(forgeReload?.hero?.equip || {}).filter(Boolean).length !== 5) report.failures.push('five remaining worn slots did not persist');

await importSave(ageFile);
const ages = [];
for (let age = 0; age < 7; age += 1) {
  await clickChoice('nav:kingdom');
  const before = await page.locator('#status').textContent();
  await clickText('Advance age');
  const after = await page.evaluate(() => window.rebornSnapshot());
  const image = await shot(page, `checkpoints/age-${after.age}.png`);
  ages.push({ before, age: after.age, resources: after.resources, hall: after.plots.find(plot => plot.id === 'townhall').level, image: image.file });
  if (after.age !== age + 1) report.failures.push(`age advance stopped at ${after.age} from ${before}`);
  await writeFile(path.join(outDir, 'checkpoints', `age-${after.age}.json`), JSON.stringify({ age: after.age, resources: after.resources, seed: after.seed }));
}
await clickChoice('nav:army');
await closePanel();
await note('23-future-army.png');
await clickChoice('nav:adventure');
await clickChoice('enter-adventure');
await closePanel();
await note('24-future-mount.png');
if (!await page.locator('[data-mount="hero-mount-future-transport"]').count()) report.failures.push('future travel did not show the 64px transport');
if (await page.locator('[data-rider="painted-partial"]').count()) report.failures.push('future transport attached an unmeasured rider');
await crop('future-travel-transport.png', '[data-mount="hero-mount-future-transport"]');
for (const [width, height] of sizes) {
  await page.setViewportSize({ width, height });
  await openPanel();
  const opened = await shot(page, `${width}x${height}-future-panel-open.png`);
  const buttons = await page.locator('button').evaluateAll(nodes => nodes.map(node => {
    const box = node.getBoundingClientRect();
    return { choice: node.dataset.choice || node.textContent, width: box.width, height: box.height };
  }));
  const short = buttons.filter(button => button.height > 0 && (button.height < 47.5 || button.width < 47.5));
  if (short.length) report.failures.push(`${width}x${height} future short controls ${JSON.stringify(short.slice(0, 3))}`);
  report.steps.push({ name: `future-${width}x${height}`, opened, short: short.length });
}
report.steps.push({ name: 'age-checkpoints', ages });

await browser.close();
server.kill();
report.finished = new Date().toISOString();
await writeFile(path.join(outDir, 'report.json'), JSON.stringify(report, null, 2));
console.log(JSON.stringify({ failures: report.failures, steps: report.steps.length }, null, 2));
if (report.failures.length) process.exitCode = 1;
