// Natural Stone journey through ordinary controls. Forge fixture is not used here.
import { chromium } from 'file:///C:/Users/TechnoExponent/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import { spawn } from 'node:child_process';
import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';

const root = 'C:/dev/ages-of-dominion-reborn';
const qa = path.join(root, 'qa/planner-recheck-20261005');
await mkdir(qa, { recursive: true });
const port = 4243;
const server = spawn(process.execPath, ['scripts/serve.mjs', '--port', String(port)], { cwd: root, stdio: ['ignore', 'pipe', 'pipe'] });
let log = '';
server.stdout.on('data', chunk => { log += chunk; });
server.stderr.on('data', chunk => { log += chunk; });
const report = { evidenceType: 'natural isolated fresh save; no injected resources', steps: [], errors: [] };
let browser;

const snap = page => page.evaluate(() => {
  const state = window.rebornSnapshot();
  return {
    revision: state.revision,
    resources: state.resources,
    day: state.day,
    army: state.army,
    inventory: state.inventory,
    equip: state.hero.equip,
    plots: state.plots.filter(plot => plot.level || plot.type).map(plot => ({ id: plot.id, type: plot.type, level: plot.level })),
    jobs: state.buildJobs.map(job => job.type),
    adventure: state.adventure,
    battle: state.battle ? { status: state.battle.status, winner: state.battle.outcome?.winner || null, round: state.battle.round } : null,
    defense: state.defense ? { status: state.defense.status, winner: state.defense.winner || null, cleared: state.defense.clearedWaves, pending: state.defense.pendingSettlement, hero: state.defense.heroDeployed, army: state.defense.armyDeployed, core: state.defense.core } : null,
  };
});

async function note(page, id) {
  const state = await snap(page);
  report.steps.push({ id, state });
  return state;
}

async function openPanel(page) {
  if (!(await page.locator('#panel').evaluate(node => node.classList.contains('open')))) await page.locator('#context').click();
}

async function build(page, type) {
  await page.locator('[data-choice="nav:kingdom"]').click();
  await openPanel(page);
  for (let attempt = 0; attempt < 8; attempt++) {
    const button = page.locator(`#choices [data-choice$=":${type}"], #dock [data-choice$=":${type}"]`).first();
    if (await button.count() && await button.isEnabled()) {
      await button.click();
      return true;
    }
    const empty = await page.evaluate(index => {
      const node = [...document.querySelectorAll('[data-pad-state="empty"]')][index];
      if (!node) return null;
      const box = node.getBoundingClientRect();
      return { x: box.x + box.width / 2, y: box.y + box.height / 2, label: node.getAttribute('aria-label') };
    }, attempt);
    if (!empty) break;
    await page.mouse.click(empty.x, empty.y);
  }
  return false;
}

async function waitBuilt(page, type) {
  const started = Date.now();
  while (Date.now() - started < 15000) {
    const state = await snap(page);
    if (state.plots.some(plot => plot.type === type && plot.level >= 1)) return state;
    await page.waitForTimeout(400);
  }
  return snap(page);
}

try {
  for (let i = 0; i < 50; i++) {
    if (log.includes('Reborn local preview')) break;
    if (server.exitCode !== null) throw new Error(log || 'server exited');
    await new Promise(resolve => setTimeout(resolve, 100));
  }
  browser = await chromium.launch({ headless: true, executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe' });
  const context = await browser.newContext({ viewport: { width: 825, height: 375 } });
  const page = await context.newPage();
  page.on('pageerror', error => report.errors.push(String(error)));
  await page.goto(`http://127.0.0.1:${port}`);
  await page.locator('[data-choice="new-campaign"]').first().click();
  await page.locator('[data-choice="class:ranger"]').first().click();
  await page.locator('[data-choice="enter-valley"]').first().click();
  const buttons = await page.locator('#dock button').evaluateAll(nodes => nodes.map(node => node.getBoundingClientRect().height));
  report.dockHeights = buttons;
  report.dockAtLeast48 = buttons.length > 0 && buttons.every(height => height >= 48);
  const before = await note(page, 'fresh-kingdom');
  const woodBefore = before.resources.wood;
  for (const type of ['lumber', 'farm', 'quarry', 'barracks']) {
    const started = await build(page, type);
    report.steps.push({ id: `build-click-${type}`, started });
    await waitBuilt(page, type);
  }
  const producing = await note(page, 'buildings-up');
  const produced = Date.now();
  let gained = producing;
  while (Date.now() - produced < 6000) {
    gained = await snap(page);
    if (gained.resources.wood > woodBefore - 25) break;
    await page.waitForTimeout(500);
  }
  report.steps.push({ id: 'after-real-production-window', state: gained, woodBefore, woodNow: gained.resources.wood });
  await openPanel(page);
  const armyNav = page.locator('[data-choice="nav:army"]');
  if (await armyNav.evaluate(node => getComputedStyle(node).display === 'none')) await page.locator('[data-choice="nav-more"]').click();
  await armyNav.click();
  const recruit = page.locator('[data-choice="recruit:melee"]').first();
  if (await recruit.isEnabled()) await recruit.click();
  const recruited = await note(page, 'after-recruit');
  await page.locator('[data-choice="nav:adventure"]').click();
  await openPanel(page);
  await page.locator('[data-choice="enter-adventure"]').first().click();
  await note(page, 'left-town');
  for (let step = 0; step < 12; step++) {
    const here = await snap(page);
    if (here.adventure?.pendingEncounter || here.battle) break;
    if ((here.adventure?.moves ?? 0) < 1) {
      await page.locator('[data-choice="nav:kingdom"]').click();
      await openPanel(page);
      await page.locator('[data-choice="end-day"]').click();
      await page.locator('[data-choice="nav:adventure"]').click();
      continue;
    }
    const target = [10, 5];
    const dx = target[0] - here.adventure.x;
    const dy = target[1] - here.adventure.y;
    const dirs = [];
    if (Math.abs(dx) >= Math.abs(dy)) {
      if (dx) dirs.push(dx > 0 ? 'east' : 'west');
      if (dy) dirs.push(dy > 0 ? 'south' : 'north');
    } else {
      if (dy) dirs.push(dy > 0 ? 'south' : 'north');
      if (dx) dirs.push(dx > 0 ? 'east' : 'west');
    }
    let moved = false;
    for (const dir of dirs) {
      await page.locator(`[data-choice="preview-${dir}"]`).first().click();
      const confirm = page.locator('[data-choice="confirm-route"]').first();
      if (await confirm.isEnabled()) {
        await confirm.click();
        await page.waitForTimeout(250);
        const next = await snap(page);
        if (next.adventure?.pendingEncounter || next.adventure.x !== here.adventure.x || next.adventure.y !== here.adventure.y) {
          moved = true;
          break;
        }
      }
    }
    if (!moved) break;
  }
  const atGuard = await note(page, 'travel-stop');
  if (atGuard.adventure?.pendingEncounter && !atGuard.battle) {
    await page.locator('[data-choice="begin-encounter"]').first().click();
  }
  for (let turn = 0; turn < 24; turn++) {
    const battle = await snap(page);
    if (!battle.battle) break;
    if (battle.battle.status !== 'ACTIVE') {
      const settle = page.locator('[data-choice="settle-battle"]');
      if (await settle.count()) await settle.first().click();
      break;
    }
    const melee = page.locator('#dock [data-choice="intent:melee"]');
    if (await melee.count() && await melee.isEnabled()) {
      await melee.click();
      const pad = await page.evaluate(() => {
        const node = document.querySelector('[data-target]');
        if (!node) return null;
        const box = node.getBoundingClientRect();
        return { x: box.x + box.width / 2, y: box.y + box.height / 2, id: node.dataset.target };
      });
      if (pad) { await page.mouse.click(pad.x, pad.y); continue; }
    }
    const shoot = page.locator('#dock [data-choice="intent:shoot"]');
    if (await shoot.count() && await shoot.isEnabled()) {
      await shoot.click();
      const pad = await page.evaluate(() => {
        const node = document.querySelector('[data-kind="shoot"]');
        if (!node) return null;
        const box = node.getBoundingClientRect();
        return { x: box.x + box.width / 2, y: box.y + box.height / 2 };
      });
      if (pad) { await page.mouse.click(pad.x, pad.y); continue; }
    }
    const move = page.locator('#dock [data-choice="intent:move"]');
    if (await move.count() && await move.isEnabled()) {
      await move.click();
      const cell = await page.evaluate(() => {
        const node = [...document.querySelectorAll('[data-open="1"]')].find(item => item.getBoundingClientRect().width > 2);
        if (!node) return null;
        const box = node.getBoundingClientRect();
        return { x: box.x + box.width / 2, y: box.y + box.height / 2 };
      });
      if (cell) { await page.mouse.click(cell.x, cell.y); continue; }
    }
    const defend = page.locator('#dock [data-choice="defend"]');
    if (await defend.count() && await defend.isEnabled()) { await defend.click(); continue; }
    break;
  }
  const fought = await note(page, 'after-guard');
  if (fought.inventory.length && !fought.defense && !fought.battle) {
    const forgeNav = page.locator('[data-choice="nav:forge"]');
    if (await forgeNav.evaluate(node => getComputedStyle(node).display === 'none')) await page.locator('[data-choice="nav-more"]').click();
    await forgeNav.click();
    await openPanel(page);
    await page.locator('#choices [data-choice^="equip:"]').first().click();
    await page.locator('#panel [data-choice^="equip-confirm:"]').first().click();
    await note(page, 'equipped-loot');
  } else if (!fought.inventory.length) report.loot = 'none this fight; no reroll';
  if (!fought.battle) {
    await page.locator('[data-choice="nav:adventure"]').click();
    for (let step = 0; step < 10; step++) {
      const here = await snap(page);
      if (here.adventure?.atTown) break;
      if (here.adventure && here.adventure.x === 8 && here.adventure.y === 4) {
        const back = page.locator('[data-choice="return-town"]').first();
        if (await back.count() && await back.isEnabled()) { await back.click(); break; }
      }
      if ((here.adventure?.moves ?? 0) < 1) {
        await page.locator('[data-choice="nav:kingdom"]').click();
        await openPanel(page);
        await page.locator('[data-choice="end-day"]').click();
        await page.locator('[data-choice="nav:adventure"]').click();
        continue;
      }
      const dx = 8 - here.adventure.x;
      const dy = 4 - here.adventure.y;
      const dirs = [];
      if (Math.abs(dy) >= Math.abs(dx)) {
        if (dy) dirs.push(dy > 0 ? 'south' : 'north');
        if (dx) dirs.push(dx > 0 ? 'east' : 'west');
      } else {
        if (dx) dirs.push(dx > 0 ? 'east' : 'west');
        if (dy) dirs.push(dy > 0 ? 'south' : 'north');
      }
      let moved = false;
      for (const dir of dirs) {
        await page.locator(`[data-choice="preview-${dir}"]`).first().click();
        const confirm = page.locator('[data-choice="confirm-route"]').first();
        if (await confirm.isEnabled()) {
          await confirm.click();
          await page.waitForTimeout(200);
          moved = true;
          break;
        }
      }
      if (!moved) break;
    }
    await note(page, 'return-attempt');
    const defenseNav = page.locator('[data-choice="nav:defense"]');
    if (await defenseNav.evaluate(node => getComputedStyle(node).display === 'none')) await page.locator('[data-choice="nav-more"]').click();
    await defenseNav.click();
    await openPanel(page);
    const start = page.locator('[data-choice="start-siege"]').first();
    if (await start.count() && await start.isEnabled()) await start.click();
    const hero = page.locator('[data-choice="deploy-hero"]').first();
    if (await hero.count() && await hero.isEnabled()) await hero.click();
    const stack = page.locator('[data-choice^="deploy-army:"]').first();
    if (await stack.count() && await stack.isEnabled()) await stack.click();
    const defenseStarted = Date.now();
    while (Date.now() - defenseStarted < 150000) {
      const running = await snap(page);
      if (running.defense?.pending || running.defense?.status !== 'ACTIVE') break;
      await page.waitForTimeout(500);
    }
    await note(page, 'defense-before-settle');
    report.defenseTerminal = await page.evaluate(() => window.rebornSnapshot().defense);
    await page.screenshot({ path: path.join(qa, 'natural-defense-terminal.png') });
    const settleDefense = page.locator('[data-choice="settle-defense"]');
    if (await settleDefense.count()) await settleDefense.first().click();
    report.defenseSettlementActions = await page.evaluate(() => (window.rebornActions || []).filter(x => x.type === 'SETTLE_DEFENSE'));
    await note(page, 'after-defense');
  }
  await page.locator('#save').click();
  const saved = await note(page, 'before-reload');
  await page.reload();
  const loaded = await note(page, 'after-reload');
  report.reloadMatches = JSON.stringify(saved.equip) === JSON.stringify(loaded.equip) && JSON.stringify(saved.army) === JSON.stringify(loaded.army);
  await page.setViewportSize({ width: 500, height: 900 });
  await page.waitForTimeout(200);
  report.portrait = await page.evaluate(() => ({
    rotate: getComputedStyle(document.querySelector('#rotate')).display,
    app: getComputedStyle(document.querySelector('#app')).display,
    resources: window.rebornSnapshot().resources,
  }));
} catch (error) {
  report.errors.push(String(error.stack || error));
} finally {
  await browser?.close();
  server.kill();
  await writeFile(path.join(qa, 'journey-report.json'), JSON.stringify(report, null, 2));
}
console.log(JSON.stringify({ errors: report.errors, steps: report.steps.map(step => step.id), dockAtLeast48: report.dockAtLeast48, reloadMatches: report.reloadMatches, loot: report.loot, portrait: report.portrait, last: report.steps.at(-1) }, null, 2));

