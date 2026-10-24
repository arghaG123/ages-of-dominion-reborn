import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import contract from '../../../src/data/implementation-contract.json' with { type: 'json' };
import worlds from '../../../src/data/adventure-worlds.json' with { type: 'json' };
import { adventureGeometryForWorld, adventureMap, routeTo } from '../../../src/core/navigation.js';

const root = process.cwd();
const out = path.join(root, 'qa/game-completion-20261021/visual-review/m21-spellbook-context-and-cancel-live-20261021');
await fs.mkdir(out, { recursive: true });
const sizes = [
  { name: '825x375', width: 825, height: 375 },
  { name: '933x424', width: 933, height: 424 },
  { name: '1180x820', width: 1180, height: 820 },
  { name: '1280x720', width: 1280, height: 720 },
];
const selectedWorld = worlds[0];
const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
const report = { recordedAt: new Date().toISOString(), classification: 'NATURAL_UI_M21_SPELLBOOK_LAYOUT_AND_TACTICAL_CANCEL', viewports: [], errors: [], failedResponses: [] };

for (const size of sizes) {
  const context = await browser.newContext({ viewport: { width: size.width, height: size.height }, deviceScaleFactor: 1 });
  const page = await context.newPage();
  const worldAssetResponses = [];
  page.on('pageerror', error => report.errors.push({ viewport: size.name, error: String(error) }));
  page.on('console', message => { if (message.type() === 'error') report.errors.push({ viewport: size.name, error: message.text() }); });
  page.on('response', response => {
    if (response.url().includes(selectedWorld.mapFile.split('/').at(-1))) worldAssetResponses.push({ status: response.status(), url: response.url() });
    if (response.status() >= 400) report.failedResponses.push({ viewport: size.name, status: response.status(), url: response.url() });
  });
  await page.route('**/favicon.ico', route => route.fulfill({ status: 204, body: '' }));
  await page.goto('http://127.0.0.1:4179/', { waitUntil: 'networkidle' });

  await page.locator('[data-choice="new-campaign"]').click();
  await page.locator(`[data-choice="campaign-world:${selectedWorld.id}"]`).click();
  await page.locator('[data-choice="begin-selected-world"]').click();
  await page.locator('[data-choice="scene-class:warlock"]').click();
  await page.locator('[data-choice="scene-enter-valley"]').click();
  await page.locator('[data-choice="nav:hero"]').click();
  await page.locator('#dock [data-choice="inspect:hero"]').click();
  await page.locator('#choices [data-choice="hero-tab:spells"]').click();
  await page.locator('#choices [data-choice="spell:arrow"]').click();
  const spellbook = await page.evaluate(() => {
    const world = document.querySelector('#world');
    const field = document.querySelector('#stage-field');
    const panel = document.querySelector('#panel');
    const spell = document.querySelector('#choices [data-choice="spell:arrow"]');
    const mapImage = getComputedStyle(field).backgroundImage;
    const bounds = selector => {
      const box = document.querySelector(selector).getBoundingClientRect();
      return [box.x, box.y, box.width, box.height].map(Math.round);
    };
    return {
      screen: world.dataset.screen || '',
      context: world.dataset.heroContext || '',
      board: world.dataset.board || '',
      worldId: world.dataset.adventureWorldId || '',
      terrainFile: world.dataset.adventureTerrainFile || '',
      backgroundImage: mapImage,
      backgroundLoaded: mapImage.includes('adventure-world-maps-generated'),
      layout: {
        app: bounds('#app'), stage: bounds('#stage'), field: bounds('#stage-field'), frame: bounds('#frame'),
        terrainHidden: document.querySelector('#terrain').hidden,
        terrainDisplay: getComputedStyle(document.querySelector('#terrain')).display,
        worldChildren: world.childElementCount,
        fieldBackgroundSize: getComputedStyle(field).backgroundSize,
        frameBackground: getComputedStyle(document.querySelector('#frame')).backgroundColor,
        fieldBackgroundColor: getComputedStyle(field).backgroundColor,
        footerBounds: bounds('#app > footer'),
        genericMessageDisplay: getComputedStyle(document.querySelector('#message')).display,
        tutorialActionDisplay: getComputedStyle(document.querySelector('#choices > [data-choice="tutorial-toggle"]')).display,
        visibleSpellCards: [...document.querySelectorAll('#choices button[data-choice^="spell:"]')].filter(node => node.getClientRects().length).length,
      },
      selectedSpell: spell?.getAttribute('aria-current') === 'true',
      feedback: document.querySelector('#choices .spellbook-heading')?.textContent?.trim() || '',
      panelOpen: panel.classList.contains('open'),
      panelBounds: (() => { const box = panel.getBoundingClientRect(); return [box.x, box.y, box.width, box.height].map(Math.round); })(),
    };
  });
  assert.equal(spellbook.context, 'adventure', 'Spellbook retains the selected campaign world behind the panel');
  assert.equal(spellbook.worldId, selectedWorld.id, 'the background is the selected campaign world');
  assert.equal(spellbook.terrainFile, selectedWorld.mapFile || selectedWorld.terrainFile, 'the world terrain binding matches the campaign record');
  assert.equal(spellbook.backgroundLoaded, true, 'the selected campaign terrain is the full-field Spellbook background');
  assert.ok(spellbook.panelBounds[0] < 24 && spellbook.panelBounds[0] + spellbook.panelBounds[2] < size.width / 2, 'the spellbook occupies the lower-left half of the world');
  assert.ok(spellbook.layout.footerBounds[0] >= spellbook.panelBounds[0] + spellbook.panelBounds[2], 'the bottom navigation stays clear of the spellbook panel');
  assert.equal(spellbook.layout.genericMessageDisplay, 'none', 'generic Hero equipment summary is hidden on the Spellbook');
  assert.equal(spellbook.layout.tutorialActionDisplay, 'none', 'the tutorial action does not interrupt the spell grid');
  assert.equal(spellbook.layout.visibleSpellCards, 8, 'all eight spell cards remain visible');
  await page.waitForFunction(file => getComputedStyle(document.querySelector('#stage-field')).backgroundImage.includes(file.split('/').at(-1)), selectedWorld.mapFile || selectedWorld.terrainFile);
  assert.ok(worldAssetResponses.some(response => response.status === 200), 'the selected campaign map asset loaded successfully');
  assert.equal(spellbook.selectedSpell, true, 'spell feedback remains available over the world scene');
  const spellbookShot = `spellbook-world-${size.name}.png`;
  await page.screenshot({ path: path.join(out, spellbookShot) });

  await page.locator('[data-choice="nav:kingdom"]').click();
  await page.locator('[data-choice="nav:adventure"]').click();
  await page.locator('[data-choice="enter-adventure"]:visible').first().click();
  await page.waitForFunction(() => Boolean(window.rebornSnapshot()?.adventure));
  const campaign = await page.evaluate(() => window.rebornSnapshot());
  const map = adventureMap(adventureGeometryForWorld(contract.geometry.adventure, selectedWorld, campaign.seed));
  const guardCell = [...map.guards].map(key => key.split(',').map(Number)).map(cell => {
    try { return { cell, cost: routeTo(map, [campaign.adventure.x, campaign.adventure.y], cell).cost }; } catch { return null; }
  }).filter(Boolean).sort((a, b) => a.cost - b.cost)[0]?.cell;
  assert.ok(guardCell, 'the selected campaign world has a routeable guard');
  for (let step = 0; step < 8; step += 1) {
    const currentState = await page.evaluate(() => window.rebornSnapshot());
    const current = currentState.adventure;
    const route = routeTo(map, [current.x, current.y], guardCell);
    let destination = null;
    if (route.cost <= current.moves) destination = guardCell;
    else {
      destination = route.cells.filter(cell => !map.guards.has(cell.join(','))).map(cell => {
        try { return { cell, cost: routeTo(map, [current.x, current.y], cell).cost }; } catch { return null; }
      }).filter(option => option && option.cost <= current.moves).at(-1)?.cell || null;
    }
    if (!destination) {
      if (!(await page.locator('#panel [data-choice="adventure-end-day"]:visible').count())) {
        await page.locator('#dock [data-choice="inspect:adventure"]:visible').click();
      }
      await page.locator('[data-choice="adventure-end-day"]:visible').first().click();
      await page.waitForFunction(({ day, moves }) => {
        const state = window.rebornSnapshot();
        return state?.day > day || state?.adventure?.moves > moves;
      }, { day: currentState.day, moves: current.moves });
      continue;
    }
    await page.locator(`[data-adventure-cell="${destination[0]},${destination[1]}"]`).click({ force: true });
    await page.locator('[data-choice="confirm-route"]:visible').first().click();
    if (destination.join(',') === guardCell.join(',')) break;
    await page.waitForFunction(({ x, y }) => {
      const adventure = window.rebornSnapshot()?.adventure;
      return adventure?.x === x && adventure?.y === y;
    }, { x: destination[0], y: destination[1] });
    await page.waitForTimeout(2200);
  }
  await page.waitForFunction(() => window.rebornSnapshot()?.adventure?.pendingEncounter?.status === 'UNRESOLVED');
  await page.locator('[data-choice="begin-encounter"]:visible').first().click();
  await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'tactical' && window.rebornSnapshot()?.battle?.status === 'ACTIVE');
  const beforeCancel = await page.evaluate(() => {
    const battle = window.rebornSnapshot().battle;
    return { mana: battle.mana, castThisRound: battle.castThisRound, logLength: battle.log.length, round: battle.round };
  });
  const spellAction = page.locator('#dock [data-choice="intent:spell"]:visible').first();
  assert.equal(await spellAction.isDisabled(), false, 'a real campaign turn offers at least one cast');
  await spellAction.click();
  const cancel = page.locator('#choices [data-choice="cancel-spell-selection"]:visible');
  assert.equal(await cancel.count(), 1, 'the open target list has a visible cancel action');
  const targetsBeforeCancel = await page.locator('#choices [data-choice^="spellcast:"]:visible').count();
  assert.ok(targetsBeforeCancel > 0, 'legal cast targets are listed before cancellation');
  const cancelShot = `spell-targets-before-cancel-${size.name}.png`;
  await page.screenshot({ path: path.join(out, cancelShot) });
  await cancel.click();
  const afterCancel = await page.evaluate(() => {
    const battle = window.rebornSnapshot().battle;
    return {
      mana: battle.mana,
      castThisRound: battle.castThisRound,
      logLength: battle.log.length,
      round: battle.round,
      panelOpen: document.querySelector('#panel').classList.contains('open'),
      cancelVisible: Boolean(document.querySelector('#choices [data-choice="cancel-spell-selection"]')),
    };
  });
  assert.deepEqual({ mana: afterCancel.mana, castThisRound: afterCancel.castThisRound, logLength: afterCancel.logLength, round: afterCancel.round }, beforeCancel, 'cancel leaves the battle state, mana and log unchanged');
  assert.equal(afterCancel.panelOpen, false, 'cancel closes the target panel');
  await page.reload({ waitUntil: 'networkidle' });
  await page.waitForFunction(() => window.rebornSnapshot()?.battle?.status === 'ACTIVE');
  const afterCancelReload = await page.evaluate(() => {
    const battle = window.rebornSnapshot().battle;
    return { mana: battle.mana, castThisRound: battle.castThisRound, logLength: battle.log.length, round: battle.round };
  });
  assert.deepEqual(afterCancelReload, beforeCancel, 'the canceled action remains a no-op after reload');

  await page.locator('#dock [data-choice="intent:spell"]:visible').first().click();
  const arrowTarget = page.locator('#choices [data-choice^="spellcast:arrow:"]:visible').first();
  assert.equal(await arrowTarget.count(), 1, 'Magic Arrow has a legal target after cancellation');
  await arrowTarget.click();
  await page.waitForFunction(mana => {
    const battle = window.rebornSnapshot()?.battle;
    return battle?.castThisRound && battle.mana === mana - 5 && battle.log?.at(-1)?.type === 'spell' && battle.log.at(-1).id === 'arrow';
  }, beforeCancel.mana, { timeout: 10000 });
  const afterCast = await page.evaluate(() => {
    const battle = window.rebornSnapshot().battle;
    return { mana: battle.mana, castThisRound: battle.castThisRound, log: battle.log.filter(item => item.type === 'spell').at(-1) };
  });
  const castShot = `magic-arrow-after-cancel-${size.name}.png`;
  await page.screenshot({ path: path.join(out, castShot) });
  await page.reload({ waitUntil: 'networkidle' });
  await page.waitForFunction(() => window.rebornSnapshot()?.battle?.log?.some(item => item.type === 'spell' && item.id === 'arrow'));
  const afterCastReload = await page.evaluate(() => {
    const battle = window.rebornSnapshot().battle;
    return { mana: battle.mana, castThisRound: battle.castThisRound, spell: battle.log.filter(item => item.type === 'spell').at(-1) };
  });
  assert.equal(afterCastReload.mana, afterCast.mana, 'spent mana persists after reload');
  assert.equal(afterCastReload.spell.id, 'arrow', 'the natural cast persists after reload');
  report.viewports.push({ viewport: size.name, spellbook, screenshots: { spellbook: spellbookShot, targetsBeforeCancel: cancelShot, castAfterCancel: castShot }, cancellation: { before: beforeCancel, after: afterCancel, afterReload: afterCancelReload, targetCount: targetsBeforeCancel }, cast: { after: afterCast, afterReload: afterCastReload } });
  await context.close();
}

await browser.close();
report.passed = report.viewports.length === sizes.length && report.errors.length === 0 && report.failedResponses.length === 0;
await fs.writeFile(path.join(out, 'report.json'), JSON.stringify(report, null, 2));
console.log(JSON.stringify({ passed: report.passed, viewports: report.viewports, errors: report.errors, failedResponses: report.failedResponses, output: path.relative(root, out) }, null, 2));
