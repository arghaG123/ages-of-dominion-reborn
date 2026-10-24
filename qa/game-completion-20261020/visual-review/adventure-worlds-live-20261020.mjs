import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
import path from 'node:path';
import worlds from '../../../src/data/adventure-worlds.json' with { type: 'json' };

const root = process.cwd();
const out = path.join(root, 'qa/game-completion-20261020/visual-review/adventure-worlds-live-current-20261020');
await fs.mkdir(out, { recursive: true });
const sizes = [
  { name: '825x375', width: 825, height: 375 },
  { name: '933x424', width: 933, height: 424 },
  { name: '1280x720', width: 1280, height: 720 },
];
const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
const report = { recordedAt: new Date().toISOString(), url: 'http://127.0.0.1:4179/', results: [], errors: [], failedResponses: [] };

for (const size of sizes) {
  const context = await browser.newContext({ viewport: { width: size.width, height: size.height }, deviceScaleFactor: 1 });
  const page = await context.newPage();
  page.on('pageerror', error => report.errors.push({ size: size.name, error: String(error) }));
  page.on('console', message => { if (message.type() === 'error') report.errors.push({ size: size.name, error: message.text() }); });
  page.on('response', response => { if (response.status() >= 400) report.failedResponses.push({ size: size.name, status: response.status(), url: response.url() }); });
  await page.goto(report.url, { waitUntil: 'networkidle' });
  await page.locator('[data-choice="new-campaign"]').click();
  await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'campaignMapSelect');

  const picker = await page.evaluate(() => {
    const terrain = document.querySelector('#terrain');
    const panel = document.querySelector('#panel');
    const rect = panel.getBoundingClientRect();
    return {
      view: document.querySelector('#app').dataset.view,
      optionCount: document.querySelectorAll('#choices [data-world-id]').length,
      generatedThumbnailCount: Array.from(document.querySelectorAll('#choices .campaign-world-option img')).filter(image => new URL(image.src).pathname.includes('/assets/derivatives/adventure-world-')).length,
      panelOpen: panel.classList.contains('open'),
      panel: [rect.x, rect.y, rect.width, rect.height],
      terrainVisible: getComputedStyle(terrain).display !== 'none' && terrain.getBoundingClientRect().width > 0,
      previewSource: document.querySelector('#world').dataset.campaignWorldPreviewSource || '',
    };
  });
  await page.screenshot({ path: path.join(out, `world-picker-${size.name}.png`) });
  const selectedWorlds = [];
  for (const world of worlds) {
    const option = page.locator(`[data-choice="campaign-world:${world.id}"]`);
    await option.click();
    await page.waitForFunction(id => document.querySelector('#world')?.dataset.selectedWorld === id, world.id);
    await page.waitForFunction(() => {
      const image = document.querySelector('#terrain');
      return image?.complete && image.naturalWidth > 0 && image.naturalHeight > 0;
    });
    const selected = await page.evaluate(() => {
      const terrain = document.querySelector('#terrain');
      const chosen = document.querySelector('#world').dataset.selectedWorld;
      const selectedOption = document.querySelector('#choices .campaign-world-option[aria-pressed="true"]');
      return { id: chosen, source: new URL(terrain.getAttribute('src'), document.baseURI).pathname, selectedOption: selectedOption?.dataset.worldId || '' };
    });
    const expectedMapFile = world.mapFile || world.terrainFile;
    selectedWorlds.push({ expected: world.id, ...selected, passed: selected.id === world.id && selected.selectedOption === world.id && selected.source.endsWith(expectedMapFile.replaceAll('\\', '/')) });
    if (size.width === 1280) await page.screenshot({ path: path.join(out, `picker-${world.id}-${size.name}.png`) });
  }

  const chosen = worlds[10];
  await page.locator(`[data-choice="campaign-world:${chosen.id}"]`).click();
  await page.locator('[data-choice="begin-selected-world"]').click();
  await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'hero');
  await page.locator('[data-choice="scene-class:knight"]').click();
  await page.locator('[data-choice="scene-enter-valley"]').click();
  await page.locator('[data-choice="nav:adventure"]').click();
  await page.locator('#dock [data-choice="inspect:adventure"]').click();
  await page.locator('#choices [data-choice="enter-adventure"]').click();
  await page.waitForFunction(id => document.querySelector('#world')?.dataset.adventureWorldId === id, chosen.id);
  await page.waitForFunction(() => {
    const image = document.querySelector('#terrain');
    return image?.complete && image.naturalWidth > 0 && image.naturalHeight > 0;
  });
  const adventure = await page.evaluate(() => ({
    view: document.querySelector('#app').dataset.view,
    mapId: document.querySelector('#world').dataset.adventureWorldId,
    terrainSource: new URL(document.querySelector('#terrain').getAttribute('src'), document.baseURI).pathname,
    terrainWidth: document.querySelector('#terrain').naturalWidth,
    terrainHeight: document.querySelector('#terrain').naturalHeight,
    referenceSource: document.querySelector('#world').dataset.adventureReferenceFile,
    renderModel: document.querySelector('#world').dataset.adventureRenderModel,
    waterFeature: document.querySelector('#world').dataset.adventureWater || '',
    bridgeCount: Number(document.querySelector('#world').dataset.adventureBridgeCount || 0),
    playableCrossings: Number(document.querySelector('#world').dataset.adventurePlayableCrossings || 0),
    movementCells: document.querySelectorAll('#world [data-adventure-cell]').length,
    siteArtOverlays: document.querySelectorAll('#world .adventure-site').length,
    siteSpriteOverlays: document.querySelectorAll('#world .adventure-site[data-art-mode="sprite"] image').length,
    siteHotspots: document.querySelectorAll('#world .adventure-site[data-art-mode="map-hotspot"] [data-site-hotspot]').length,
    townArt: document.querySelector('#world .adventure-site[data-site-id="town"] image')?.getAttribute('href') || '',
    resourcePickups: document.querySelectorAll('#world .adventure-resource-marker').length,
    enemyPatrols: document.querySelectorAll('#world .adventure-enemy-marker').length,
    channelOverlayCount: document.querySelectorAll('#world [data-adventure-channel]').length,
    bridgeOverlayCount: document.querySelectorAll('#world .adventure-bridge').length,
    routeCount: document.querySelectorAll('#world .adventure-road-network [data-route-index]').length / 4,
    ownerMapMarkers: document.querySelectorAll('#world [data-world-site-marker]').length,
    imageLoaded: document.querySelector('#terrain').naturalWidth > 0,
  }));
  await page.screenshot({ path: path.join(out, `adventure-${size.name}.png`) });
  await page.locator('#panel-close').click();
  await page.waitForFunction(() => !document.querySelector('#panel')?.classList.contains('open'));
  await page.screenshot({ path: path.join(out, `adventure-panel-closed-${size.name}.png`) });
  await page.locator('#dock [data-choice="inspect:adventure"]').click();
  await page.waitForFunction(() => document.querySelector('#panel')?.classList.contains('open'));

  const initialMarker = await page.locator('#world [data-map-marker="traveler"]').count();
  let movement = { attempted: false, committed: false, action: null, saveState: '', woodAnchorVisible: false, woodAnchorSource: '', cacheClaimed: false, cacheReward: 0, woodAfterClaim: 0 };
  if (initialMarker) {
    movement.attempted = true;
    await page.locator('#world [data-adventure-cell="9,7"][data-open="1"]').click({ force: true });
    const confirm = page.locator('#choices [data-choice="confirm-route"]');
    await confirm.waitFor({ state: 'visible' });
    if (!(await confirm.isDisabled())) await confirm.click();
    await page.waitForFunction(() => window.rebornActions?.some(action => action.type === 'MOVE'));
    await page.waitForFunction(() => document.querySelector('#save')?.dataset.saveState === 'committed');
    await page.locator('#choices [data-choice="adventure-end-day"]').click();
    await page.waitForFunction(() => window.rebornActions?.some(action => action.type === 'END_DAY'));
    await page.waitForFunction(() => document.querySelector('#save')?.dataset.saveState === 'committed');
    await page.locator('#world [data-adventure-cell="7,9"][data-open="1"]').click({ force: true });
    const woodConfirm = page.locator('#choices [data-choice="confirm-route"]');
    await woodConfirm.waitFor({ state: 'visible' });
    if (!(await woodConfirm.isDisabled())) await woodConfirm.click();
    await page.waitForFunction(() => window.rebornActions?.filter(action => action.type === 'MOVE').length >= 2);
    await page.waitForFunction(() => document.querySelector('#save')?.dataset.saveState === 'committed');
    await page.waitForFunction(() => document.querySelector('#world [data-adventure-anchor="wood"]') !== null);
    await page.locator('#choices [data-choice="collect-cache:wood"]').waitFor({ state: 'visible' });
    if (size.width === 1280) await page.screenshot({ path: path.join(out, 'adventure-wood-cache-discovered-1280x720.png') });
    const discovery = await page.evaluate(() => ({
      woodAnchorVisible: document.querySelector('#world [data-adventure-anchor="wood"]') !== null,
      woodAnchorSource: document.querySelector('#world [data-adventure-anchor="wood"] image')?.getAttribute('href') || '',
    }));
    const cacheBefore = await page.evaluate(() => {
      const snapshot = window.rebornSnapshot?.();
      return { offer: snapshot?.adventure?.cacheOffers?.wood || 0, wood: snapshot?.resources?.wood || 0 };
    });
    await page.locator('#choices [data-choice="collect-cache:wood"]').click();
    await page.waitForFunction(() => window.rebornActions?.some(action => action.type === 'CLAIM_ADVENTURE_CACHE'));
    await page.waitForFunction(() => document.querySelector('#save')?.dataset.saveState === 'committed');
    await page.waitForFunction(() => document.querySelector('#world [data-adventure-anchor="wood"]') === null);
    if (size.width === 1280) await page.screenshot({ path: path.join(out, 'adventure-wood-cache-collected-1280x720.png') });
    movement = await page.evaluate(before => ({
      attempted: true,
      committed: window.rebornActions?.some(action => action.type === 'MOVE') === true,
      action: window.rebornActions?.filter(action => action.type === 'MOVE').at(-1) || null,
      saveState: document.querySelector('#save')?.dataset.saveState || '',
      cacheClaimed: window.rebornActions?.some(action => action.type === 'CLAIM_ADVENTURE_CACHE') === true,
      cacheReward: window.rebornSnapshot?.().adventure?.cacheOffers?.wood || 0,
      woodAfterClaim: window.rebornSnapshot?.().resources?.wood || 0,
      woodGain: (window.rebornSnapshot?.().resources?.wood || 0) - before.wood,
      expectedCacheOffer: before.offer,
      cacheHiddenAfterClaim: document.querySelector('#world [data-adventure-anchor="wood"]') === null,
      bridgeCrossingObserved: window.rebornSnapshot?.().adventure?.visited?.includes('9,8') === true,
    }), cacheBefore);
    movement = { ...movement, ...discovery };
  }
  await page.reload({ waitUntil: 'networkidle' });
  await page.waitForFunction(id => document.querySelector('#world')?.dataset.adventureWorldId === id, chosen.id, { timeout: 10000 });
  const reloadedWorld = await page.locator('#world').getAttribute('data-adventure-world-id');
  const reloadedWoodCacheHidden = await page.locator('#world [data-adventure-anchor="wood"]').count() === 0;
  await page.screenshot({ path: path.join(out, `adventure-reload-${size.name}.png`) });
  let guardDiscovery = { attempted: false, visible: false, source: '', pendingEncounter: false };
  if (size.width === 1280 && movement.woodAnchorVisible) {
    const moveTo = async cell => {
      const count = await page.evaluate(() => window.rebornActions?.filter(action => action.type === 'MOVE').length || 0);
      await page.locator(`#world [data-adventure-cell="${cell[0]},${cell[1]}"][data-open="1"]`).click({ force: true });
      const confirm = page.locator('#choices [data-choice="confirm-route"]');
      await confirm.waitFor({ state: 'visible' });
      if (!(await confirm.isDisabled())) await confirm.click();
      await page.waitForFunction(prior => window.rebornActions?.filter(action => action.type === 'MOVE').length > prior, count);
      await page.waitForFunction(() => document.querySelector('#save')?.dataset.saveState === 'committed');
    };
    if (!(await page.locator('#panel').evaluate(panel => panel.classList.contains('open')))) {
      await page.locator('#dock [data-choice="inspect:adventure"]').click();
      await page.waitForFunction(() => document.querySelector('#panel')?.classList.contains('open'));
    }
    await page.locator('#choices [data-choice="adventure-end-day"]').click();
    await page.waitForFunction(() => window.rebornActions?.some(action => action.type === 'END_DAY'));
    await page.waitForFunction(() => document.querySelector('#save')?.dataset.saveState === 'committed');
    await moveTo([8, 7]);
    await page.locator('#choices [data-choice="adventure-end-day"]').click();
    await page.waitForFunction(() => window.rebornActions?.filter(action => action.type === 'END_DAY').length >= 2);
    await page.waitForFunction(() => document.querySelector('#save')?.dataset.saveState === 'committed');
    await moveTo([10, 5]);
    await page.waitForFunction(() => document.querySelector('#world [data-adventure-anchor="guard-mine"]') !== null);
    guardDiscovery = await page.evaluate(() => ({
      attempted: true,
      visible: document.querySelector('#world [data-adventure-anchor="guard-mine"]') !== null,
      source: document.querySelector('#world [data-adventure-anchor="guard-mine"] image')?.getAttribute('href') || '',
      pendingEncounter: document.querySelector('#choices [data-choice="begin-encounter"]') !== null,
    }));
    await page.screenshot({ path: path.join(out, 'adventure-wild-guard-discovered-1280x720.png') });
  }
  report.results.push({
    size: size.name,
    picker,
    selectedWorlds,
    allWorldsSelectable: selectedWorlds.length === worlds.length && selectedWorlds.every(row => row.passed),
    adventure,
    adventureTerrainIsGenerated: adventure.terrainSource.endsWith((chosen.mapFile || chosen.terrainFile).replaceAll('\\', '/'))
      && adventure.referenceSource === chosen.file
      && adventure.renderModel === 'integrated-map-art-plus-live-interactions',
    movement,
    reloadRetainedWorld: reloadedWorld === chosen.id,
    reloadedWoodCacheHidden,
    guardDiscovery,
  });
  await context.close();
}

await browser.close();
report.passed = report.results.length === sizes.length
  && report.results.every(result => result.allWorldsSelectable && result.picker.optionCount === 12 && result.picker.generatedThumbnailCount === 12 && result.picker.terrainVisible && result.picker.previewSource.includes('assets/derivatives/adventure-world-') && !result.picker.previewSource.includes('/assets/mocks/') && result.adventure.mapId === worlds[10].id && result.adventure.imageLoaded && result.adventureTerrainIsGenerated && result.adventure.movementCells === 160 && result.adventure.siteArtOverlays > 0 && result.adventure.siteHotspots > 0 && result.adventure.siteSpriteOverlays === 0 && result.adventure.townArt === '' && result.adventure.ownerMapMarkers === 0 && result.adventure.waterFeature === 'winding-river-and-waterfall' && result.adventure.bridgeCount === 2 && result.adventure.playableCrossings === 1 && result.adventure.channelOverlayCount === 0 && result.adventure.bridgeOverlayCount === 0 && result.adventure.routeCount === 0 && result.movement.committed && result.movement.bridgeCrossingObserved && result.movement.saveState === 'committed' && result.movement.woodAnchorVisible && result.movement.woodAnchorSource.includes('wood-cache-v1.png') && result.movement.cacheClaimed && result.movement.cacheReward > 0 && result.movement.expectedCacheOffer === result.movement.cacheReward && result.movement.woodGain === result.movement.cacheReward && result.movement.cacheHiddenAfterClaim && result.reloadRetainedWorld && result.reloadedWoodCacheHidden && (result.size !== '1280x720' || (result.guardDiscovery.visible && result.guardDiscovery.pendingEncounter && result.guardDiscovery.source.includes('wild-pack-v1.png'))))
  && report.errors.length === 0 && report.failedResponses.length === 0;
await fs.writeFile(path.join(out, 'report.json'), JSON.stringify(report, null, 2));
console.log(JSON.stringify({
  passed: report.passed,
  sizes: report.results.map(result => ({ size: result.size, picker: result.picker, allWorldsSelectable: result.allWorldsSelectable, adventure: result.adventure, adventureTerrainIsGenerated: result.adventureTerrainIsGenerated, movement: result.movement, reloadRetainedWorld: result.reloadRetainedWorld, reloadedWoodCacheHidden: result.reloadedWoodCacheHidden, guardDiscovery: result.guardDiscovery })),
  errors: report.errors,
  failedResponses: report.failedResponses,
  output: path.relative(root, out),
}, null, 2));
