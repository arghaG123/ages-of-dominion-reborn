import { spawn } from 'node:child_process';
import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';

const port = 4181;
const base = `http://127.0.0.1:${port}`;
const outDir = fileURLToPath(new URL('../qa/code-ready-20261004/manual/', import.meta.url));
await mkdir(outDir, { recursive: true });
const server = spawn(process.execPath, ['scripts/serve.mjs', '--port', String(port)], { stdio: ['ignore', 'pipe', 'pipe'] });
process.on('exit', () => server.kill());
await new Promise((resolve, reject) => {
  const timer = setTimeout(() => reject(new Error('preview server did not start')), 5000);
  server.stdout.on('data', chunk => {
    if (String(chunk).includes(String(port))) {
      clearTimeout(timer);
      resolve();
    }
  });
  server.stderr.on('data', chunk => {
    const text = String(chunk);
    if (text.includes('already in use')) {
      clearTimeout(timer);
      reject(new Error(text));
    }
  });
});

const report = {
  started: new Date().toISOString(),
  base,
  acceleration: 'none — construction uses the live clock',
  fixtures: [],
  steps: [],
  failures: [],
};
const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });

async function shot(page, name) {
  const file = path.join(outDir, name);
  const buffer = await page.screenshot({ type: 'png' });
  await writeFile(file, buffer);
  return { file: path.basename(file), sha256: crypto.createHash('sha256').update(buffer).digest('hex'), width: buffer.readUInt32BE(16), height: buffer.readUInt32BE(20) };
}
async function note(page, name) {
  const message = await page.locator('#message').textContent();
  const selected = await page.locator('#selected').textContent();
  const image = await shot(page, name);
  report.steps.push({ name, message, selected, image });
  return message || '';
}
async function openPanel(page) {
  if (!await page.locator('#panel').evaluate(node => node.classList.contains('open'))) await page.click('#context');
}
async function closePanel(page) {
  if (await page.locator('#panel').evaluate(node => node.classList.contains('open'))) await page.click('#context');
}
async function clickChoice(page, choice) {
  await openPanel(page);
  await page.evaluate(id => {
    const node = document.querySelector(`[data-choice="${id}"]`);
    if (!node) throw new Error('missing choice ' + id);
    node.click();
  }, choice);
}

async function buildAndWait(page, plot, type) {
  await page.evaluate(id => {
    const node = document.querySelector(`[aria-label^="${id}:"]`);
    if (!node) throw new Error('missing plot ' + id);
    node.dispatchEvent(new MouseEvent('click', { bubbles: true }));
  }, plot);
  await clickChoice(page, `build:${plot}:${type}`);
  await page.waitForTimeout(4600);
  return note(page, `build-${type}.png`);
}

const page = await browser.newPage({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1 });
page.on('dialog', dialog => dialog.accept());
await page.goto(base + '/', { waitUntil: 'networkidle' });
await page.evaluate(() => localStorage.clear());
await page.reload({ waitUntil: 'networkidle' });
await clickChoice(page, 'new-campaign');
await note(page, '01-knight-pending.png');
const pending = await page.locator('[data-card-status="pending-review"]').count();
if (!pending) report.failures.push('pending knight card missing');
await clickChoice(page, 'class:ranger');
await clickChoice(page, 'clip:walk');
await closePanel(page);
await page.waitForTimeout(400);
await note(page, '02-ranger-walk.png');
if (!await page.locator('[data-articulation="painted-partial"]').count()) report.failures.push('ranger painted figure missing');
await clickChoice(page, 'enter-valley');
await page.waitForSelector('[data-walls="unbuilt"]');
await closePanel(page);
await note(page, '03-kingdom-day1.png');

for (const [plot, type] of [['P01', 'lumber'], ['P02', 'farm'], ['P03', 'quarry'], ['P04', 'barracks']]) {
  const message = await buildAndWait(page, plot, type);
  const selected = await page.locator('#selected').textContent();
  if (!selected.toLowerCase().includes(type === 'lumber' ? 'lumber' : type)) report.failures.push(`build ${type}: ${selected} / ${message}`);
}
await clickChoice(page, 'nav:army');
await clickChoice(page, 'recruit:melee');
await note(page, '04-recruited.png');
await clickChoice(page, 'plate-review-next');
await clickChoice(page, 'plate-review-next');
await closePanel(page);
await note(page, '05-iron-plate-review.png');
const iron = await page.locator('[data-plate-review="2-melee"]').count();
if (!iron) report.failures.push('iron melee review missing');
for (let step = 0; step < 3; step += 1) await clickChoice(page, 'plate-review-next');
await closePanel(page);
await note(page, '06-industrial-walker-review.png');

await clickChoice(page, 'nav:adventure');
await clickChoice(page, 'enter-adventure');
for (const choice of ['preview-east', 'preview-east', 'preview-north', 'preview-north', 'preview-north']) {
  await clickChoice(page, choice);
}
const beforeMoves = await page.locator('#selected').textContent();
await clickChoice(page, 'confirm-route');
await page.waitForTimeout(700);
const confirmAgain = page.locator('[data-choice="confirm-route"]');
if (await confirmAgain.count() && await confirmAgain.isEnabled()) await confirmAgain.click();
else report.steps.push({ name: 'double-confirm', message: 'Confirm stayed disabled after the first spend.' });
const doubleSpend = await note(page, '07-travel-double-confirm.png');
report.steps.at(-1).beforeMoves = beforeMoves;
if (!doubleSpend.toLowerCase().includes('preview') && !doubleSpend.toLowerCase().includes('movement') && !doubleSpend.toLowerCase().includes('guard')) {
  report.failures.push('double confirm did not stay refused or resolved: ' + doubleSpend);
}
if (await page.locator('[data-choice="begin-encounter"]').count()) await clickChoice(page, 'begin-encounter');
else report.failures.push('guard encounter did not open: ' + doubleSpend);
await page.waitForTimeout(300);
let settled = false;
for (let turn = 0; turn < 24 && !settled; turn += 1) {
  const melee = page.locator('[data-choice^="nav:"] , button').filter({ hasText: /^Melee / }).first();
  const move = page.locator('button').filter({ hasText: /^Move / }).first();
  const apply = page.locator('button', { hasText: 'Apply the battle result' });
  if (await apply.count()) {
    await openPanel(page);
    await apply.click();
    settled = true;
    break;
  }
  await openPanel(page);
  if (await melee.count()) await melee.click();
  else if (await move.count()) await move.click();
  else {
    const defend = page.locator('button', { hasText: 'Defend' });
    if (await defend.count()) await defend.click();
    else break;
  }
  await page.waitForTimeout(200);
}
await note(page, '08-after-manual-tactical.png');
if (!settled) report.failures.push('manual tactical did not reach settlement');
const equip = page.locator('[data-choice^="equip:"]');
if (await equip.count()) {
  await openPanel(page);
  await equip.first().click();
  await note(page, '09-equipped-loot.png');
} else report.steps.push({ name: 'loot', message: 'The battle roll added no item. Nothing was granted.' });

await clickChoice(page, 'nav:kingdom');
await openPanel(page);
await page.locator('button', { hasText: 'End day' }).click();
await clickChoice(page, 'nav:adventure');
await note(page, '10-after-end-day.png');
await clickChoice(page, 'nav:forge');
await note(page, '11-forge-without-armory.png');
await clickChoice(page, 'nav:market');
await note(page, '12-market-stone.png');
await clickChoice(page, 'nav:story');
await note(page, '13-story.png');
await clickChoice(page, 'nav:settings');
await note(page, '14-settings.png');
await clickChoice(page, 'nav:help');
await note(page, '15-help.png');

await clickChoice(page, 'nav:home');
await openPanel(page);
await page.locator('button', { hasText: 'Save slot 1' }).click();
await page.reload({ waitUntil: 'networkidle' });
await clickChoice(page, 'nav:home');
await openPanel(page);
await page.locator('button', { hasText: 'Load slot 1' }).click();
await note(page, '16-reloaded-slot.png');

async function restoreSlot() {
  await clickChoice(page, 'nav:home');
  await openPanel(page);
  await page.locator('button', { hasText: 'Load slot 1' }).click();
  await page.waitForTimeout(200);
}
for (const name of ['skirmish', 'duel', 'challenge', 'endless', 'siege']) {
  if (name === 'endless' || name === 'siege') await restoreSlot();
  await clickChoice(page, 'nav:war');
  if (name === 'skirmish') await page.locator('button', { hasText: 'Skirmish' }).click();
  else if (name === 'duel') await page.locator('button', { hasText: 'Tactical Duel' }).click();
  else if (name === 'challenge') await clickChoice(page, 'challenge-start');
  else if (name === 'endless') await page.locator('button', { hasText: 'Endless' }).click();
  else await clickChoice(page, 'start-siege');
  await page.waitForTimeout(300);
  await note(page, `17-war-${name}.png`);
  if (name === 'siege' || name === 'endless') {
    const pause = page.locator('button', { hasText: 'Pause' });
    if (await pause.count()) await pause.click();
    report.fixtures.push(`${name} was paused from the Defense controls. Full wave clearance was not waited out. The campaign was then reloaded from slot 1.`);
  } else {
    const retreat = page.locator('button', { hasText: 'Retreat' });
    if (await retreat.count()) {
      await retreat.click();
      const apply = page.locator('button', { hasText: 'Apply the battle result' });
      if (await apply.count()) await apply.click();
    }
  }
}

const sizes = [[825, 375], [933, 424], [1180, 820], [1280, 720]];
for (const [width, height] of sizes) {
  const sized = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: 1 });
  sized.on('dialog', dialog => dialog.accept());
  await sized.goto(base + '/', { waitUntil: 'domcontentloaded' });
  await openPanel(sized);
  await closePanel(sized);
  const closed = await shot(sized, `${width}x${height}-panel-closed.png`);
  await openPanel(sized);
  const opened = await shot(sized, `${width}x${height}-panel-open.png`);
  const buttons = await sized.locator('button').evaluateAll(nodes => nodes.map(node => {
    const box = node.getBoundingClientRect();
    return { choice: node.dataset.choice || node.id, width: box.width, height: box.height };
  }));
  const short = buttons.filter(button => button.height > 0 && (button.height < 47.5 || button.width < 47.5));
  if (short.length) report.failures.push(`${width}x${height} short controls ${JSON.stringify(short.slice(0, 3))}`);
  report.steps.push({ name: `${width}x${height}`, closed, opened, short: short.length });
  await sized.close();
}

await browser.close();
server.kill();
report.finished = new Date().toISOString();
await writeFile(path.join(outDir, 'report.json'), JSON.stringify(report, null, 2));
console.log(JSON.stringify({ failures: report.failures, steps: report.steps.length }, null, 2));
if (report.failures.length) process.exitCode = 1;
