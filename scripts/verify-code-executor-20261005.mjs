// Isolated browser proof for map input, retreat, Forge deltas, and screen-space labels.
import { chromium } from 'file:///C:/Users/TechnoExponent/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import { spawn } from 'node:child_process';
import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';

const root = 'C:/dev/ages-of-dominion-reborn';
const qa = path.join(root, 'qa/code-executor-20261005');
const shots = path.join(qa, 'pixels');
await mkdir(shots, { recursive: true });
const port = 4219;
const server = spawn(process.execPath, ['scripts/serve.mjs', '--port', String(port)], { cwd: root, stdio: ['ignore', 'pipe', 'pipe'] });
let log = '';
server.stdout.on('data', chunk => { log += chunk; });
server.stderr.on('data', chunk => { log += chunk; });
const report = { evidenceType: 'isolated browser 2026-10-05', errors: [], checks: [] };
let browser;

function check(id, pass, detail) {
  report.checks.push({ id, pass: Boolean(pass), ...detail });
  if (!pass) report.errors.push(id + ' ' + JSON.stringify(detail));
}

async function boot(contextOptions) {
  const context = await browser.newContext(contextOptions);
  const page = await context.newPage();
  page.on('pageerror', error => report.errors.push(String(error)));
  await page.goto(`http://127.0.0.1:${port}`);
  await page.locator('[data-choice="new-campaign"]').first().click();
  await page.locator('[data-choice="class:ranger"]').first().click();
  await page.locator('[data-choice="enter-valley"]').first().click();
  return { context, page };
}

async function openSkirmish(page) {
  if (!(await page.locator('#panel').evaluate(node => node.classList.contains('open')))) await page.locator('#context').click();
  await page.locator('[data-choice="nav:war"]').click();
  await page.getByRole('button', { name: 'Skirmish', exact: true }).first().click();
  await page.waitForTimeout(450);
}

async function openCell(page) {
  const targets = await page.evaluate(() => [...document.querySelectorAll('[data-cell]')].map(node => ({
    cell: node.dataset.cell,
    open: node.dataset.open,
    handler: typeof node.onclick,
    box: node.getBoundingClientRect().toJSON(),
  })));
  return { targets, open: targets.find(row => row.open === '1' && row.box.width > 2 && row.box.height > 2) };
}

try {
  for (let i = 0; i < 50; i++) {
    if (log.includes('Reborn local preview')) break;
    if (server.exitCode !== null) throw new Error(log || 'server exited');
    await new Promise(resolve => setTimeout(resolve, 100));
  }
  browser = await chromium.launch({ headless: true, executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe' });
  const phone = { viewport: { width: 825, height: 375 } };
  const { context, page } = await boot(phone);
  const kingdomMessage = await page.locator('#message').textContent();
  check('kingdom-player-text', !/provisional|baked painting|ground file/i.test(kingdomMessage || ''), { kingdomMessage });
  await page.screenshot({ path: path.join(shots, 'kingdom-825x375.png') });

  await openSkirmish(page);
  const labels = await page.evaluate(() => [...document.querySelectorAll('#labels span')].map(node => {
    const box = node.getBoundingClientRect();
    const style = getComputedStyle(node);
    return { text: node.textContent, fontSize: style.fontSize, width: box.width, height: box.height };
  }));
  const readable = labels.length > 0 && labels.every(row => parseFloat(row.fontSize) >= 14 && row.height >= 14);
  check('tactical-label-screen-space', readable, { labels });
  await page.screenshot({ path: path.join(shots, 'tactical-825x375.png') });

  const first = await openCell(page);
  const before = await page.evaluate(() => ({ revision: window.rebornSnapshot().revision, actions: window.rebornActions || [] }));
  if (!first.open) throw new Error('No legal move cell ' + JSON.stringify(first.targets.slice(0, 4)));
  check('map-handlers-not-bound-to-replaced-nodes', first.targets.every(row => row.handler !== 'function'), { sample: first.targets.length });
  await page.mouse.click(first.open.box.x + first.open.box.width / 2, first.open.box.y + first.open.box.height / 2);
  await page.waitForTimeout(150);
  const moved = await page.evaluate(() => window.rebornSnapshot());
  const actions = await page.evaluate(() => window.rebornActions || []);
  const moves = actions.slice(before.actions.length).filter(row => row.action === 'move');
  const actor = moved.battle?.stacks?.find(stack => stack.side === 'p' && stack.x === Number(first.open.cell.split(',')[0]) && stack.y === Number(first.open.cell.split(',')[1]));
  check('map-one-move-after-frames', moves.length === 1 && Boolean(actor), { cell: first.open.cell, moves, revision: [before.revision, moved.revision] });

  const closed = first.targets.find(row => row.open !== '1' && row.box.width > 2);
  const beforeInvalid = await page.evaluate(() => (window.rebornActions || []).length);
  if (closed) {
    await page.mouse.click(closed.box.x + closed.box.width / 2, closed.box.y + closed.box.height / 2);
    await page.waitForTimeout(80);
  }
  const afterInvalid = await page.evaluate(() => (window.rebornActions || []).length);
  check('map-ignores-closed-cell', !closed || afterInvalid === beforeInvalid, { closed: closed?.cell, beforeInvalid, afterInvalid });

  if (await page.locator('#panel').evaluate(node => !node.classList.contains('open'))) await page.locator('#context').click();
  const keyMove = page.locator('#choices [data-choice^="move:"]').first();
  const keyCount = await keyMove.count();
  if (keyCount) {
    const beforeKey = await page.evaluate(() => (window.rebornActions || []).filter(row => row.action === 'move').length);
    await keyMove.focus();
    await page.keyboard.press('Enter');
    await page.waitForTimeout(120);
    const afterKey = await page.evaluate(() => (window.rebornActions || []).filter(row => row.action === 'move').length);
    check('keyboard-move', afterKey === beforeKey + 1, { beforeKey, afterKey });
  } else check('keyboard-move', false, { reason: 'no panel move after the map move' });

  const retreatBefore = await page.evaluate(() => {
    const snap = window.rebornSnapshot();
    return { gold: snap.resources.gold, mana: snap.hero.mana, rng: snap.rngState, actions: (window.rebornActions || []).length, status: snap.battle?.status || null, log: snap.battle?.log?.length || 0, stacks: snap.battle?.stacks };
  });
  await page.locator('#dock [data-choice="retreat"]').click();
  const dialogOpen = await page.locator('#retreat').evaluate(node => !node.hidden && node.getAttribute('role') === 'dialog');
  const opened = await page.evaluate(() => {
    const snap = window.rebornSnapshot();
    return { gold: snap.resources.gold, mana: snap.hero.mana, rng: snap.rngState, actions: (window.rebornActions || []).length, status: snap.battle?.status || null, log: snap.battle?.log?.length || 0, stacks: snap.battle?.stacks };
  });
  check('retreat-open-spends-nothing', dialogOpen && opened.status === 'ACTIVE' && opened.gold === retreatBefore.gold && opened.mana === retreatBefore.mana && opened.rng === retreatBefore.rng && opened.actions === retreatBefore.actions && opened.log === retreatBefore.log && JSON.stringify(opened.stacks) === JSON.stringify(retreatBefore.stacks), { retreatBefore, opened, body: await page.locator('#retreat-body').textContent() });
  await page.locator('#retreat-cancel').click();
  const cancelled = await page.evaluate(() => {
    const snap = window.rebornSnapshot();
    return { hidden: document.querySelector('#retreat').hidden, status: snap.battle?.status || null, actions: (window.rebornActions || []).length, log: snap.battle?.log?.length || 0 };
  });
  check('retreat-cancel-spends-nothing', cancelled.hidden && cancelled.status === 'ACTIVE' && cancelled.actions === retreatBefore.actions && cancelled.log === retreatBefore.log, { cancelled });
  await page.locator('#dock [data-choice="retreat"]').click();
  await page.locator('#retreat-confirm').click();
  await page.waitForTimeout(100);
  const confirmed = await page.evaluate(() => {
    const snap = window.rebornSnapshot();
    return { battle: snap.battle, gold: snap.resources.gold, actions: window.rebornActions || [] };
  });
  const retreats = confirmed.actions.filter(row => row.action === 'retreat');
  const settles = confirmed.actions.filter(row => row.type === 'SETTLE_BATTLE');
  check('retreat-confirm-once', retreats.length === 1 && settles.length === 1 && confirmed.battle == null && confirmed.gold === retreatBefore.gold, { gold: confirmed.gold, retreats: retreats.length, settles: settles.length });
  await context.close();

  const reduced = await boot(phone);
  if (!(await reduced.page.locator('#panel').evaluate(node => node.classList.contains('open')))) await reduced.page.locator('#context').click();
  await reduced.page.locator('[data-choice="nav-more"]').click();
  await reduced.page.locator('[data-choice="nav:settings"]').click();
  await reduced.page.locator('#choices').getByRole('button', { name: 'Reduced motion off' }).click();
  await openSkirmish(reduced.page);
  const reducedCell = await openCell(reduced.page);
  const reducedBefore = await reduced.page.evaluate(() => (window.rebornActions || []).filter(row => row.action === 'move').length);
  await reduced.page.mouse.click(reducedCell.open.box.x + reducedCell.open.box.width / 2, reducedCell.open.box.y + reducedCell.open.box.height / 2);
  await reduced.page.waitForTimeout(120);
  const reducedAfter = await reduced.page.evaluate(() => (window.rebornActions || []).filter(row => row.action === 'move').length);
  check('map-reduced-motion', Boolean(reducedCell.open) && reducedAfter === reducedBefore + 1, { cell: reducedCell.open?.cell, reducedBefore, reducedAfter });
  await reduced.context.close();

  const touchContext = await browser.newContext({ ...phone, hasTouch: true });
  const touchPage = await touchContext.newPage();
  touchPage.on('pageerror', error => report.errors.push(String(error)));
  await touchPage.goto(`http://127.0.0.1:${port}`);
  await touchPage.locator('[data-choice="new-campaign"]').first().click();
  await touchPage.locator('[data-choice="class:knight"]').first().click();
  await touchPage.locator('[data-choice="enter-valley"]').first().click();
  await openSkirmish(touchPage);
  const touchCell = await openCell(touchPage);
  await touchPage.touchscreen.tap(touchCell.open.box.x + touchCell.open.box.width / 2, touchCell.open.box.y + touchCell.open.box.height / 2);
  await touchPage.waitForTimeout(150);
  const touchMoves = await touchPage.evaluate(() => (window.rebornActions || []).filter(row => row.action === 'move').length);
  check('map-touch-one-move', touchMoves === 1, { cell: touchCell.open?.cell, touchMoves });
  await touchContext.close();

  const resized = await boot({ viewport: { width: 933, height: 424 } });
  await openSkirmish(resized.page);
  await resized.page.setViewportSize({ width: 1280, height: 720 });
  await resized.page.waitForTimeout(200);
  const resizedCell = await openCell(resized.page);
  await resized.page.mouse.click(resizedCell.open.box.x + resizedCell.open.box.width / 2, resizedCell.open.box.y + resizedCell.open.box.height / 2);
  await resized.page.waitForTimeout(120);
  const resizedMoves = await resized.page.evaluate(() => (window.rebornActions || []).filter(row => row.action === 'move').length);
  check('map-after-resize', resizedMoves === 1, { cell: resizedCell.open?.cell, resizedMoves });
  await resized.page.screenshot({ path: path.join(shots, 'tactical-1280x720.png') });
  await resized.context.close();

  const sizes = [[825, 375], [933, 424], [1180, 820], [1280, 720]];
  for (const [width, height] of sizes) {
    const fixture = await pageFixture(browser, width, height);
    const box = await fixture.page.evaluate(() => {
      const panel = document.querySelector('#panel').getBoundingClientRect();
      const delta = document.querySelector('#panel [data-forge-delta]').getBoundingClientRect();
      const confirm = document.querySelector('#panel [data-forge-decision] [data-choice^="equip-confirm:"]').getBoundingClientRect();
      return { panel, delta, confirm, text: document.querySelector('#panel [data-forge-delta]').textContent };
    });
    const inside = box.delta.top >= box.panel.top - 1 && box.delta.bottom <= box.panel.bottom + 1 && box.confirm.top >= box.panel.top - 1 && box.confirm.bottom <= box.panel.bottom + 1;
    const beside = box.delta.bottom <= box.confirm.top + 2 && box.confirm.top - box.delta.bottom < 24;
    check(`forge-delta-${width}x${height}`, inside && beside && /to/.test(box.text), { box });
    await fixture.page.screenshot({ path: path.join(shots, `forge-${width}x${height}.png`) });
    await fixture.context.close();
  }
} catch (error) {
  report.errors.push(String(error.stack || error));
} finally {
  await browser?.close();
  server.kill();
  report.serverLog = log;
  await writeFile(path.join(qa, 'browser-report.json'), JSON.stringify(report, null, 2));
}
console.log(JSON.stringify({ errors: report.errors, checks: report.checks.map(row => ({ id: row.id, pass: row.pass })) }, null, 2));

async function pageFixture(browser, width, height) {
  const setup = await browser.newContext();
  const setupPage = await setup.newPage();
  await setupPage.goto(`http://127.0.0.1:${port}`);
  const seeded = await setupPage.evaluate(async () => {
    const { default: data } = await import('/src/data/reference-data.json', { with: { type: 'json' } });
    const { default: contract } = await import('/src/data/implementation-contract.json', { with: { type: 'json' } });
    const { newCampaign, command } = await import('/src/core/campaign.js');
    const { encode, SAVE_KEY, VIEW_KEY } = await import('/src/core/save.js');
    let campaign = newCampaign(contract, data, Date.now(), 123456789);
    const slot = campaign.plots.find(item => item.id !== 'townhall');
    slot.type = 'armory';
    slot.level = 1;
    campaign = command(campaign, { id: 'browser-forge', type: 'FORGE', payload: { slot: 'weapon', quality: 0 } }, Date.now(), data);
    return { encoded: encode(campaign, data), saveKey: SAVE_KEY, viewKey: VIEW_KEY, items: campaign.inventory.length };
  });
  await setup.close();
  if (!seeded.items) throw new Error('Forge fixture produced no item');
  const context = await browser.newContext({ viewport: { width, height } });
  await context.addInitScript(fixture => {
    localStorage.setItem(fixture.saveKey, fixture.encoded);
    localStorage.setItem(fixture.viewKey, 'forge');
  }, seeded);
  const page = await context.newPage();
  page.on('pageerror', error => report.errors.push(String(error)));
  await page.goto(`http://127.0.0.1:${port}`);
  if (!(await page.locator('#panel').evaluate(node => node.classList.contains('open')))) await page.locator('#context').click();
  await page.locator('#choices [data-choice^="equip:"]').first().click();
  return { context, page };
}
