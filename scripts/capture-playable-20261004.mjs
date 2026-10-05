// Natural Stone loop through visible controls. Uses its own browser context, not an existing save.
import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import { createHash } from 'node:crypto';
import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';

const root = 'C:/dev/ages-of-dominion-reborn';
const outDir = path.join(root, 'qa/code-playable-20261004');
const base = process.env.PLAY_URL || 'http://127.0.0.1:4183';
const report = { started: new Date().toISOString(), base, viewport: [], steps: [], failures: [], inventory: {}, defense: {}, seed: null };
await mkdir(outDir, { recursive: true });

const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
const context = await browser.newContext({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1 });
const page = await context.newPage();
const errors = [];
page.on('pageerror', error => errors.push(String(error)));

async function shot(name) {
  const file = path.join(outDir, name);
  const buffer = await page.screenshot({ type: 'png' });
  await writeFile(file, buffer);
  return { file: name, sha256: createHash('sha256').update(buffer).digest('hex'), bytes: buffer.length };
}
async function snap() {
  return page.evaluate(() => window.rebornSnapshot());
}
async function clickChoice(id) {
  const locator = page.locator(`[data-choice="${id}"]`).locator('visible=true');
  if (!(await locator.count())) throw new Error('missing visible choice ' + id);
  await locator.first().click();
}
async function note(name) {
  const message = await page.locator('#message').textContent();
  const selected = await page.locator('#selected').textContent();
  const status = await page.locator('#status').textContent();
  const image = await shot(name);
  report.steps.push({ name, message, selected, status, image });
  console.log(name, selected, (message || '').slice(0, 140));
  return message || '';
}
async function waitPlot(type) {
  const deadline = Date.now() + 12000;
  while (Date.now() < deadline) {
    const state = await snap();
    if (state.plots.some(plot => plot.type === type && plot.level >= 1 && !state.buildJobs.some(job => job.type === type))) return state;
    await page.waitForTimeout(400);
  }
  throw new Error('construction did not finish ' + type);
}

await page.goto(base + '/', { waitUntil: 'networkidle' });
await page.evaluate(() => localStorage.clear());
await page.reload({ waitUntil: 'networkidle' });
await clickChoice('new-campaign');
await clickChoice('class:ranger');
await clickChoice('enter-valley');
const opened = await snap();
report.seed = opened.seed;
if (opened.seed !== 123456789) report.failures.push('seed ' + opened.seed);
await note('01-kingdom-day1.png');

for (const [width, height] of [[825, 375], [933, 424], [1180, 820], [1280, 720]]) {
  await page.setViewportSize({ width, height });
  await page.waitForTimeout(200);
  const image = await shot(`kingdom-${width}x${height}.png`);
  const dock = await page.locator('#dock button:visible').evaluateAll(nodes => nodes.map(node => node.textContent));
  report.viewport.push({ width, height, deviceScaleFactor: 1, image, dock });
  const short = await page.locator('#dock button:visible, #nav button:visible, header button:visible').evaluateAll(nodes => nodes.filter(node => {
    const box = node.getBoundingClientRect();
    return box.height > 0 && (box.height < 47.5 || box.width < 47.5);
  }).map(node => node.dataset.choice || node.id || node.textContent));
  if (short.length) report.failures.push(`${width}x${height} short controls ${JSON.stringify(short.slice(0, 4))}`);
}
await page.setViewportSize({ width: 1280, height: 720 });

for (const [plot, type] of [['P01', 'lumber'], ['P02', 'farm'], ['P03', 'quarry'], ['P04', 'barracks']]) {
  await page.evaluate(id => {
    const node = document.querySelector(`[aria-label^="${id}:"]`);
    if (!node) throw new Error('missing plot ' + id);
    node.dispatchEvent(new MouseEvent('click', { bubbles: true }));
  }, plot);
  await clickChoice(`build:${plot}:${type}`);
  await waitPlot(type);
  await note(`build-${type}.png`);
}
await clickChoice('go-recruit');
const beforeRecruit = await snap();
await clickChoice('recruit:melee');
const recruited = await snap();
const melee = recruited.army.find(stack => stack.type === 'melee');
if (!melee || melee.count !== beforeRecruit.army.find(stack => stack.type === 'melee').count + 5) report.failures.push('recruit did not add 5 melee');
await note('02-recruited.png');

await clickChoice('nav:adventure');
await note('03-adventure-town.png');
await clickChoice('enter-adventure');
for (const choice of ['preview-east', 'preview-east', 'preview-north', 'preview-north', 'preview-north']) await clickChoice(choice);
const beforeMove = await snap();
await clickChoice('confirm-route');
await page.waitForTimeout(500);
const moved = await snap();
if (moved.adventure.moves >= beforeMove.adventure.moves) report.failures.push('route did not spend movement');
if (await page.locator('[data-choice="confirm-route"]:visible').count() && await page.locator('[data-choice="confirm-route"]:visible').isEnabled()) {
  report.failures.push('confirm stayed enabled after spending the route');
}
await note('04-travel.png');
if (!(await page.locator('[data-choice="begin-encounter"]:visible').count())) report.failures.push('guard encounter did not open');
else await clickChoice('begin-encounter');
await note('05-tactical.png');

const beforeBattle = await snap();
report.inventory.before = beforeBattle.inventory.map(item => item.id);
let settled = false;
for (let turn = 0; turn < 40 && !settled; turn += 1) {
  const action = await page.evaluate(() => {
    const visible = [...document.querySelectorAll('#dock button')].filter(node => !node.disabled && node.offsetParent);
    const apply = visible.find(node => node.dataset.choice === 'settle-battle');
    if (apply) { apply.click(); return 'apply'; }
    const fight = visible.find(node => node.dataset.choice?.startsWith('melee:'))
      || visible.find(node => node.dataset.choice?.startsWith('shoot:'))
      || visible.find(node => node.dataset.choice === 'defend')
      || visible.find(node => node.dataset.choice?.startsWith('move:'))
      || visible.find(node => node.dataset.choice === 'wait');
    if (fight) { fight.click(); return fight.dataset.choice; }
    return 'stuck';
  });
  if (action === 'apply') { settled = true; break; }
  if (action === 'stuck') break;
  await page.waitForTimeout(120);
}
if (!settled) report.failures.push('manual tactical did not settle');
const afterBattle = await snap();
report.inventory.afterBattle = afterBattle.inventory.map(item => ({ id: item.id, slot: item.slot, kind: item.kind, quality: item.quality }));
if (afterBattle.adventure?.pendingEncounter) report.failures.push('guard remained after settlement: ' + JSON.stringify(afterBattle.adventure.pendingEncounter.status));
report.inventory.attackBeforeGear = null;
await note('06-battle-result.png');

if (afterBattle.inventory.length) {
  await clickChoice('nav:forge');
  const equip = page.locator('[data-choice^="equip:"]:visible').first();
  await equip.click();
  const worn = await snap();
  report.inventory.equipped = worn.hero.equip;
  await clickChoice('nav:hero');
  report.inventory.heroMessage = await page.locator('#message').textContent();
  await note('07-equipped.png');
} else {
  report.inventory.note = 'The guard settled with an empty bag. No reload was used to seek a drop.';
  await note('07-no-loot.png');
}

await clickChoice('nav:kingdom');
await page.click('#context');
await clickChoice('end-day').catch(async () => {
  const clicked = await page.evaluate(() => {
    const node = [...document.querySelectorAll('#choices button')].find(button => button.textContent.startsWith('End day'));
    if (!node) return false;
    node.click();
    return true;
  });
  if (!clicked) report.failures.push('End day was not available');
});
await page.click('#context');
await clickChoice('nav:adventure');
const here = await snap();
let guard = 0;
while (here && guard < 8) {
  const state = await snap();
  if (state.adventure?.atTown) break;
  if (state.adventure?.x === 8 && state.adventure?.y === 4) {
    await clickChoice('return-town');
    break;
  }
  const dx = Math.sign(8 - state.adventure.x);
  const dy = Math.sign(4 - state.adventure.y);
  const choice = dx !== 0 ? (dx < 0 ? 'preview-west' : 'preview-east') : (dy < 0 ? 'preview-north' : 'preview-south');
  await clickChoice(choice);
  const moves = state.adventure.moves;
  await clickChoice('confirm-route');
  await page.waitForTimeout(400);
  const next = await snap();
  if (next.adventure.moves === moves && (next.adventure.x !== 8 || next.adventure.y !== 4)) {
    report.failures.push('return step did not move from ' + state.adventure.x + ',' + state.adventure.y);
    break;
  }
  guard += 1;
}
await note('08-returned.png');
if (!(await snap()).adventure?.atTown && (await snap()).adventure) report.failures.push('still outside town');

await clickChoice('nav:kingdom');
const deadline = Date.now() + 8 * 60 * 1000;
let prepared = false;
while (Date.now() < deadline) {
  const state = await snap();
  const workshop = state.plots.find(plot => plot.type === 'workshop' && plot.level >= 1);
  if (!workshop && state.resources.wood >= 70 && state.resources.stone >= 95) {
    const plot = state.plots.find(item => item.type == null).id;
    await page.evaluate(id => document.querySelector(`[aria-label^="${id}:"]`).dispatchEvent(new MouseEvent('click', { bubbles: true })), plot);
    await clickChoice(`build:${plot}:workshop`);
    await waitPlot('workshop');
    await note('09-workshop.png');
  }
  if (!afterBattle.inventory.length && !state.inventory.length && !report.inventory.crafted && state.resources.wood >= 200 && state.resources.stone >= 180 && state.resources.gold >= 150 && !state.plots.some(plot => plot.type === 'armory')) {
    const plot = state.plots.find(item => item.type == null).id;
    await page.evaluate(id => document.querySelector(`[aria-label^="${id}:"]`).dispatchEvent(new MouseEvent('click', { bubbles: true })), plot);
    await clickChoice(`build:${plot}:armory`);
    await waitPlot('armory');
    await clickChoice('nav:forge');
    if (await page.locator('[data-choice="forge-confirm"]:visible').count()) {
      await clickChoice('forge-confirm');
      const forged = await snap();
      if (forged.inventory.length && await page.locator('[data-choice^="equip:"]:visible').count()) await page.locator('[data-choice^="equip:"]:visible').first().click();
      report.inventory.crafted = true;
      report.inventory.equipped = (await snap()).hero.equip;
      await note('07b-crafted.png');
      await clickChoice('nav:kingdom');
    }
  }
  const craftFirst = !afterBattle.inventory.length && !report.inventory.crafted && Date.now() < deadline - 60000;
  if (!craftFirst && workshop && !state.towers.some(tower => tower.fam === 'splash') && state.resources.wood >= 80 && state.resources.stone >= 90 && state.resources.gold >= 45) {
    if (!(await page.locator('[data-choice="nav:defense"]:visible').count())) await clickChoice('nav-more');
    await clickChoice('nav:defense');
    await clickChoice('buy-tower:splash');
    prepared = true;
    await note('10-splash.png');
    break;
  }
  await page.waitForTimeout(2000);
}
if (!prepared) report.failures.push('splash tower was not affordable in time');
else {
  await clickChoice('start-siege');
  await clickChoice('deploy-hero');
  await clickChoice('deploy-army:army-1');
  await clickChoice('defense-speed');
  await note('11-defense-running.png');
  const defenseDeadline = Date.now() + 4 * 60 * 1000;
  let defenseSettled = false;
  while (Date.now() < defenseDeadline) {
    if (await page.locator('[data-choice="settle-defense"]:visible').count()) {
      const pending = await snap();
      report.defense = { winner: pending.defense?.winner, cleared: pending.defense?.clearedWaves, core: pending.defense?.core, waves: pending.defense?.waves };
      await clickChoice('settle-defense');
      defenseSettled = true;
      break;
    }
    await page.waitForTimeout(1000);
  }
  if (!defenseSettled) report.failures.push('defense did not settle');
  await note('12-defense-result.png');
  const looted = await snap();
  report.inventory.afterDefense = looted.inventory.map(item => ({ id: item.id, slot: item.slot, kind: item.kind, quality: item.quality }));
  if (looted.inventory.length) {
    if (!(await page.locator('[data-choice="nav:forge"]:visible').count())) await clickChoice('nav-more');
    await clickChoice('nav:forge');
    await page.locator('[data-choice^="equip:"]:visible').first().click();
    await clickChoice('nav:hero');
    report.inventory.heroMessage = await page.locator('#message').textContent();
    report.inventory.equipped = (await snap()).hero.equip;
    await note('14-equipped.png');
  } else if (!report.inventory.crafted) report.failures.push('no legal item reached the bag');
}
await page.click('#save');
const saved = await snap();
report.saved = { revision: saved.revision, siege: Object.keys(saved.story.flags).filter(key => key.startsWith('siege:')), inventory: saved.inventory.length, equip: saved.hero.equip, flags: saved.story.flags };
await page.reload({ waitUntil: 'networkidle' });
const reloaded = await snap();
if (JSON.stringify(reloaded.story.flags) !== JSON.stringify(saved.story.flags)) report.failures.push('reload dropped story flags');
if (JSON.stringify(reloaded.hero.equip) !== JSON.stringify(saved.hero.equip)) report.failures.push('reload dropped equipment');
if (reloaded.inventory.length !== saved.inventory.length) report.failures.push('reload changed the bag');
await note('13-reloaded.png');
report.errors = errors;
report.finished = new Date().toISOString();
await writeFile(path.join(outDir, 'report.json'), JSON.stringify(report, null, 2));
console.log(JSON.stringify({ failures: report.failures, inventory: report.inventory, defense: report.defense, errors }, null, 2));
await browser.close();
if (report.failures.length || errors.length) process.exit(1);
