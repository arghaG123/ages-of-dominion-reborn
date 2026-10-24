import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
import path from 'node:path';
import worlds from '../../../src/data/adventure-worlds.json' with { type: 'json' };
import contract from '../../../src/data/implementation-contract.json' with { type: 'json' };
import { adventureGeometryForWorld, adventureLayoutIndex, adventureMap, routeTo, stepCost } from '../../../src/core/navigation.js';

const root = process.cwd();
const url = process.env.AOD_PREVIEW_URL || 'http://127.0.0.1:4179/';
const out = path.join(root, 'qa/game-completion-20261020/visual-review/adventure-seeded-layout-live-20261020');
await fs.mkdir(out, { recursive: true });
const sizes = [
  { name: '825x375', width: 825, height: 375 },
  { name: '933x424', width: 933, height: 424 },
  { name: '1280x720', width: 1280, height: 720 },
];
const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
const report = { recordedAt: new Date().toISOString(), url, results: [], errors: [], failedResponses: [] };

for (const size of sizes) {
  const context = await browser.newContext({ viewport: { width: size.width, height: size.height }, deviceScaleFactor: 1 });
  const page = await context.newPage();
  page.on('pageerror', error => report.errors.push({ size: size.name, error: String(error) }));
  page.on('console', message => { if (message.type() === 'error') report.errors.push({ size: size.name, error: message.text() }); });
  page.on('response', response => { if (response.status() >= 400) report.failedResponses.push({ size: size.name, status: response.status(), url: response.url() }); });
  await page.goto(url, { waitUntil: 'networkidle' });
  await page.locator('[data-choice="new-campaign"]').click();
  await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'campaignMapSelect');
  const picker = await page.evaluate(() => {
    const terrain = document.querySelector('#terrain');
    const panel = document.querySelector('#panel');
    const rect = panel.getBoundingClientRect();
    return {
      view: document.querySelector('#app').dataset.view,
      optionCount: document.querySelectorAll('#choices [data-world-id]').length,
      panelOpen: panel.classList.contains('open'),
      panel: [rect.x, rect.y, rect.width, rect.height],
      terrainVisible: getComputedStyle(terrain).display !== 'none' && terrain.getBoundingClientRect().width > 0,
      previewSource: document.querySelector('#world').dataset.campaignWorldPreviewSource || '',
    };
  });
  await page.screenshot({ path: path.join(out, `world-picker-${size.name}.png`) });
  const selectedWorlds = [];
  for (const world of worlds) {
    await page.locator(`[data-choice="campaign-world:${world.id}"]`).click();
    await page.waitForFunction(id => document.querySelector('#world')?.dataset.selectedWorld === id, world.id);
    await page.waitForFunction(() => {
      const image = document.querySelector('#terrain');
      return image?.complete && image.naturalWidth > 0 && image.naturalHeight > 0;
    });
    const selected = await page.evaluate(() => ({
      id: document.querySelector('#world').dataset.selectedWorld,
      source: new URL(document.querySelector('#terrain').getAttribute('src'), document.baseURI).pathname,
      selectedOption: document.querySelector('#choices .campaign-world-option[aria-pressed="true"]')?.dataset.worldId || '',
    }));
    const expected = world.mapFile || world.terrainFile;
    selectedWorlds.push({ expected: world.id, ...selected, passed: selected.id === world.id
      && selected.selectedOption === world.id && selected.source.endsWith(expected.replaceAll('\\', '/')) });
    if (size.width === 1280) await page.screenshot({ path: path.join(out, `picker-${world.id}-${size.name}.png`) });
  }

  const chosen = worlds.find(world => world.id === 'jade-karst');
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

  const state0 = await page.evaluate(() => window.rebornSnapshot?.());
  const geometry = adventureGeometryForWorld(contract.geometry.adventure, chosen, state0.seed);
  const map = adventureMap(geometry);
  const layoutIndex = adventureLayoutIndex(chosen, state0.seed);
  const adventure = await page.evaluate(() => ({
    view: document.querySelector('#app').dataset.view,
    mapId: document.querySelector('#world').dataset.adventureWorldId,
    terrainSource: new URL(document.querySelector('#terrain').getAttribute('src'), document.baseURI).pathname,
    terrainWidth: document.querySelector('#terrain').naturalWidth,
    terrainHeight: document.querySelector('#terrain').naturalHeight,
    referenceSource: document.querySelector('#world').dataset.adventureReferenceFile,
    renderModel: document.querySelector('#world').dataset.adventureRenderModel,
    movementCells: document.querySelectorAll('#world [data-adventure-cell]').length,
    resourceMarkersAtStart: document.querySelectorAll('#world .adventure-resource-marker').length,
    movementActionsFit: (() => {
      const panel = document.querySelector('#panel').getBoundingClientRect();
      const rest = document.querySelector('#choices [data-choice="rest"]');
      const bounds = rest?.getBoundingClientRect();
      return Boolean(bounds && bounds.top >= panel.top && bounds.bottom <= panel.bottom);
    })(),
    inactiveRouteActionsHidden: (() => {
      const panelConfirm = document.querySelector('#choices [data-choice="confirm-route"]');
      const panelClear = document.querySelector('#choices [data-choice="clear-preview"]');
      const dockConfirm = document.querySelector('#dock [data-choice="confirm-route"]');
      return Boolean(panelConfirm?.hidden && panelClear?.hidden && (!dockConfirm || dockConfirm.hidden));
    })(),
    travelControls: (() => {
      const panel = document.querySelector('#panel').getBoundingClientRect();
      const group = document.querySelector('#choices .adventure-travel-controls');
      const groupRect = group?.getBoundingClientRect();
      const buttons = Array.from(group?.querySelectorAll('button') || []).map(button => {
        const rect = button.getBoundingClientRect();
        return { label: button.getAttribute('aria-label'), left: rect.left, top: rect.top, right: rect.right, bottom: rect.bottom, width: rect.width, height: rect.height };
      });
      return {
        count: buttons.length,
        accessibleNames: buttons.map(button => button.label),
        withinPanel: Boolean(groupRect && groupRect.left >= panel.left && groupRect.right <= panel.right
          && groupRect.top >= panel.top && groupRect.bottom <= panel.bottom
          && buttons.every(button => button.width >= 48 && button.height >= 48 && button.left >= panel.left
            && button.right <= panel.right && button.top >= panel.top && button.bottom <= panel.bottom)),
      };
    })(),
    imageLoaded: document.querySelector('#terrain').naturalWidth > 0,
  }));
  adventure.seed = state0.seed;
  adventure.layoutIndex = layoutIndex;
  adventure.layoutId = geometry.layoutId;
  adventure.layoutAnchors = Object.fromEntries(['food', 'wood', 'stone', 'gold', 'guard-ruin', 'guard-mine']
    .map(id => [id, geometry.anchors[id]]));
  await page.screenshot({ path: path.join(out, `adventure-${size.name}.png`) });

  const ensurePanel = async () => {
    if (!(await page.locator('#panel').evaluate(panel => panel.classList.contains('open')))) {
      await page.locator('#dock [data-choice="inspect:adventure"]').click();
      await page.waitForFunction(() => document.querySelector('#panel')?.classList.contains('open'));
    }
  };
  const closePanel = async () => {
    if (await page.locator('#panel').evaluate(panel => panel.classList.contains('open'))) {
      await page.locator('#panel-close').click();
      await page.waitForFunction(() => !document.querySelector('#panel')?.classList.contains('open'));
    }
  };
  const waitForTravelSettled = async () => {
    let previous = '';
    let stable = 0;
    for (let attempt = 0; attempt < 40; attempt += 1) {
      const position = await page.locator('#world [data-map-marker="traveler"]').evaluate(marker => `${marker.getAttribute('cx')},${marker.getAttribute('cy')}`);
      stable = position === previous ? stable + 1 : 0;
      if (stable >= 2) return;
      previous = position;
      await page.waitForTimeout(80);
    }
    throw new Error('Adventure traveler animation did not settle within 3.2 seconds');
  };
  await ensurePanel();
  const movement = { attempted: true, committedMoves: 0, routeControlVerified: false, cacheClaimed: false, bridgeCellsVisited: [], saveState: '' };
  const waitForSavedRevision = revision => page.waitForFunction(target => {
    const head = window.rebornCommittedHead?.();
    return head?.revision >= target && document.querySelector('#save')?.dataset.saveState === 'committed';
  }, revision);
  const finishDay = async () => {
    await ensurePanel();
    const before = await page.evaluate(() => window.rebornSnapshot?.());
    await page.locator('#choices [data-choice="adventure-end-day"]').click();
    await page.waitForFunction(revision => (window.rebornSnapshot?.()?.revision || 0) > revision, before.revision);
    await waitForSavedRevision(before.revision + 1);
  };
  const moveToward = async (goal, maxSegments = 80) => {
    for (let segment = 0; segment < maxSegments; segment += 1) {
      const state = await page.evaluate(() => window.rebornSnapshot?.());
      if (state.adventure.x === goal[0] && state.adventure.y === goal[1]) return;
      if (state.adventure.pendingEncounter?.status?.startsWith('UNRESOLVED')) throw new Error('Unexpected guard intercepted route');
      if (state.adventure.moves <= 0) { await finishDay(); continue; }
      const route = routeTo(map, [state.adventure.x, state.adventure.y], goal);
      const segmentCells = [];
      let cost = 0;
      let previous = [state.adventure.x, state.adventure.y];
      for (const cell of route.cells) {
        const step = stepCost(map, previous, cell);
        if (cost + step > state.adventure.moves) break;
        segmentCells.push(cell);
        cost += step;
        previous = cell;
      }
      if (!segmentCells.length) { await finishDay(); continue; }
      const beforeRevision = state.revision;
      const beforeMoves = await page.evaluate(() => window.rebornActions?.filter(action => action.type === 'MOVE').length || 0);
      const [x, y] = segmentCells.at(-1);
      await closePanel();
      await page.locator(`#world [data-adventure-cell="${x},${y}"][data-open="1"]`).click({ force: true });
      const confirm = page.locator('#dock [data-choice="confirm-route"]');
      await confirm.waitFor({ state: 'visible', timeout: 2500 }).catch(async () => {
        const detail = await page.evaluate(() => ({
          position: { x: window.rebornSnapshot?.().adventure?.x, y: window.rebornSnapshot?.().adventure?.y, moves: window.rebornSnapshot?.().adventure?.moves },
          view: document.querySelector('#app')?.dataset.view || '',
          panelOpen: document.querySelector('#panel')?.classList.contains('open') === true,
          status: document.querySelector('#scene-ui.game-status')?.innerText || '',
          confirmHidden: document.querySelector('#dock [data-choice="confirm-route"]')?.hidden ?? null,
          cellCount: document.querySelectorAll('#world [data-adventure-cell]').length,
        }));
        throw new Error(`Route preview did not open for ${x},${y}: ${JSON.stringify(detail)}`);
      });
      if (!await confirm.isDisabled()) {
        movement.routeControlVerified = true;
        movement.routeControlLabel = await confirm.getAttribute('aria-label');
        if (size.width === 825 && segment === 0) await page.screenshot({ path: path.join(out, 'route-preview-825x375.png') });
      }
      if (await confirm.isDisabled()) {
        const detail = await page.evaluate(() => ({
          state: { x: window.rebornSnapshot?.().adventure?.x, y: window.rebornSnapshot?.().adventure?.y, moves: window.rebornSnapshot?.().adventure?.moves },
          status: document.querySelector('#status')?.textContent || '',
          choiceText: document.querySelector('#choices')?.innerText || '',
          confirmTitle: document.querySelector('#dock [data-choice="confirm-route"]')?.title || '',
          confirmLabel: document.querySelector('#dock [data-choice="confirm-route"]')?.getAttribute('aria-label') || '',
        }));
        throw new Error(`Route confirmation unexpectedly disabled for ${x},${y}: ${JSON.stringify(detail)}`);
      }
      await confirm.click();
      await page.waitForFunction(count => (window.rebornActions?.filter(action => action.type === 'MOVE').length || 0) > count, beforeMoves);
      await page.waitForFunction(revision => (window.rebornSnapshot?.()?.revision || 0) > revision, beforeRevision);
      await waitForSavedRevision(beforeRevision + 1);
      await waitForTravelSettled();
      movement.committedMoves += 1;
    }
    const state = await page.evaluate(() => window.rebornSnapshot?.());
    if (state.adventure.x !== goal[0] || state.adventure.y !== goal[1]) throw new Error(`Route did not reach ${goal.join(',')}`);
  };

  const wood = geometry.anchors.wood.map(Math.floor);
  await moveToward(wood);
  await ensurePanel();
  await page.locator('#world [data-adventure-anchor="wood"]').waitFor({ state: 'visible' });
  await page.locator('#choices [data-choice="collect-cache:wood"]').waitFor({ state: 'visible' });
  movement.cacheLabelLayout = await page.evaluate(() => {
    const labels = Array.from(document.querySelectorAll('#labels span')).map(node => {
      const rect = node.getBoundingClientRect();
      return { text: node.textContent.trim(), left: rect.left, top: rect.top, right: rect.right, bottom: rect.bottom };
    });
    const hero = labels.find(label => label.text === 'Your hero');
    const cache = labels.find(label => label.text === 'Wood cache');
    const separated = Boolean(hero && cache && (hero.right <= cache.left || cache.right <= hero.left
      || hero.bottom <= cache.top || cache.bottom <= hero.top));
    const withinSafeArea = label => Boolean(label && label.top >= 60 && label.bottom <= window.innerHeight - 76);
    return { labels, cacheVisible: Boolean(cache), heroVisible: Boolean(hero), separated, withinSafeArea: withinSafeArea(cache) && withinSafeArea(hero) };
  });
  await page.screenshot({ path: path.join(out, `wood-cache-discovered-${size.name}.png`) });
  const beforeClaim = await page.evaluate(() => window.rebornSnapshot?.());
  await page.locator('#choices [data-choice="collect-cache:wood"]').click();
  await page.waitForFunction(revision => (window.rebornSnapshot?.()?.revision || 0) > revision, beforeClaim.revision);
  await waitForSavedRevision(beforeClaim.revision + 1);
  await page.waitForFunction(() => document.querySelector('#world [data-adventure-anchor="wood"]') === null);
  movement.cacheClaimed = true;
  movement.cacheReward = beforeClaim.adventure.cacheOffers.wood;
  movement.woodGain = (await page.evaluate(() => window.rebornSnapshot?.().resources.wood)) - beforeClaim.resources.wood;
  const current = await page.evaluate(() => window.rebornSnapshot?.());
  const bridgeCell = [...map.bridge].map(value => value.split(',').map(Number))
    .sort((first, second) => Math.abs(first[0] - current.adventure.x) + Math.abs(first[1] - current.adventure.y)
      - Math.abs(second[0] - current.adventure.x) - Math.abs(second[1] - current.adventure.y))[0];
  await moveToward(bridgeCell);
  movement.bridgeCellsVisited = (await page.evaluate(() => window.rebornSnapshot?.().adventure.visited))
    .filter(cell => map.bridge.has(cell));
  movement.saveState = await page.locator('#save').getAttribute('data-save-state');
  await page.screenshot({ path: path.join(out, `wood-cache-collected-${size.name}.png`) });

  await page.reload({ waitUntil: 'networkidle' });
  await page.waitForFunction(() => Boolean(window.rebornSnapshot?.()), null, { timeout: 15000 });
  const snapshotAfterReload = await page.evaluate(() => window.rebornSnapshot?.());
  if (!snapshotAfterReload.adventure || snapshotAfterReload.adventureWorldId !== chosen.id) {
    throw new Error(`Adventure journey did not survive reload: ${JSON.stringify({ worldId: snapshotAfterReload.adventureWorldId, adventure: snapshotAfterReload.adventure })}`);
  }
  const reloadedView = await page.locator('#app').getAttribute('data-view');
  const continuedFromGate = reloadedView === 'home';
  if (continuedFromGate) {
    await page.locator('#gate-actions [data-choice="continue"]').click();
    await page.waitForFunction(() => document.querySelector('#app')?.dataset.view !== 'home');
  }
  if (await page.locator('#app').getAttribute('data-view') !== 'adventure') {
    await page.locator('[data-choice="nav:adventure"]').click();
    await page.waitForFunction(id => document.querySelector('#world')?.dataset.adventureWorldId === id, chosen.id);
  }
  await ensurePanel();
  const afterReload = await page.evaluate(() => window.rebornSnapshot?.());
  const reload = {
    worldId: afterReload.adventureWorldId,
    seed: afterReload.seed,
    continuedFromGate,
    adventureActive: Boolean(afterReload.adventure && !afterReload.adventure.atTown),
    woodCacheCollected: afterReload.adventure?.collectedCaches?.includes('wood') === true,
    woodMarkerHidden: await page.locator('#world [data-adventure-anchor="wood"]').count() === 0,
  };
  await page.screenshot({ path: path.join(out, `adventure-after-reload-${size.name}.png`) });

  const guard = geometry.anchors['guard-mine'].map(Math.floor);
  await moveToward(guard);
  await page.waitForFunction(() => document.querySelector('#world [data-adventure-anchor="guard-mine"]') !== null);
  await page.waitForFunction(() => document.querySelector('#choices [data-choice="begin-encounter"]') !== null);
  const guardDiscovery = await page.evaluate(() => ({
    visible: document.querySelector('#world [data-adventure-anchor="guard-mine"]') !== null,
    encounterReady: document.querySelector('#choices [data-choice="begin-encounter"]') !== null,
    pendingEncounter: window.rebornSnapshot?.().adventure.pendingEncounter?.status || '',
  }));
  await page.screenshot({ path: path.join(out, `guard-discovered-${size.name}.png`) });

  report.results.push({
    size: size.name,
    picker,
    selectedWorlds,
    allWorldsSelectable: selectedWorlds.length === worlds.length && selectedWorlds.every(row => row.passed),
    adventure,
    movement,
    reload,
    guardDiscovery,
  });
  await context.close();
}

await browser.close();
report.distinctSeeds = new Set(report.results.map(result => result.adventure.seed)).size;
report.distinctLayouts = new Set(report.results.map(result => result.adventure.layoutIndex)).size;
report.passed = report.results.length === sizes.length
  && report.distinctSeeds === sizes.length
  && report.results.every(result => result.allWorldsSelectable && result.picker.optionCount === 12 && result.picker.terrainVisible
    && result.picker.previewSource.includes('assets/derivatives/adventure-world-')
    && result.adventure.mapId === 'jade-karst' && result.adventure.imageLoaded && result.adventure.movementCells === 160
    && result.adventure.inactiveRouteActionsHidden
    && result.adventure.movementActionsFit
    && result.adventure.travelControls.count === 4 && result.adventure.travelControls.withinPanel
    && result.adventure.travelControls.accessibleNames.join('|') === 'Travel north|Travel south|Travel west|Travel east'
    && result.adventure.seed !== 123456789 && result.adventure.layoutIndex >= 0 && result.adventure.layoutIndex < 20
    && result.movement.routeControlVerified && result.movement.cacheClaimed
    && result.movement.cacheLabelLayout?.cacheVisible && result.movement.cacheLabelLayout?.separated
    && result.movement.cacheLabelLayout?.withinSafeArea
    && result.movement.cacheReward > 0 && result.movement.woodGain === result.movement.cacheReward
    && result.movement.bridgeCellsVisited.length > 0 && result.movement.saveState === 'committed'
    && result.reload.worldId === 'jade-karst' && result.reload.seed === result.adventure.seed
    && result.reload.adventureActive && result.reload.woodCacheCollected && result.reload.woodMarkerHidden
    && result.guardDiscovery.visible && result.guardDiscovery.encounterReady && result.guardDiscovery.pendingEncounter.startsWith('UNRESOLVED'))
  && report.errors.length === 0 && report.failedResponses.length === 0;
await fs.writeFile(path.join(out, 'report.json'), JSON.stringify(report, null, 2));
console.log(JSON.stringify({
  passed: report.passed,
  distinctSeeds: report.distinctSeeds,
  distinctLayouts: report.distinctLayouts,
  results: report.results.map(result => ({ size: result.size, seed: result.adventure.seed, layoutIndex: result.adventure.layoutIndex, layoutAnchors: result.adventure.layoutAnchors, movement: result.movement, reload: result.reload, guardDiscovery: result.guardDiscovery })),
  errors: report.errors,
  failedResponses: report.failedResponses,
  output: path.relative(root, out),
}, null, 2));
