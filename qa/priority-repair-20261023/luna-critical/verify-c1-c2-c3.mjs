import { spawn } from 'node:child_process';
import { mkdir, mkdtemp, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';

const root = process.cwd();
const outDir = path.join(root, 'qa', 'priority-repair-20261023', 'luna-critical');
await mkdir(outDir, { recursive: true });

const chrome = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const port = 4595;
const debugPort = 9395;

function waitFor(stream, text, child) {
  return new Promise((resolve, reject) => {
    let log = '';
    const timer = setTimeout(() => reject(new Error(log || 'timed out')), 15000);
    stream.on('data', chunk => {
      log += chunk;
      if (log.includes(text)) { clearTimeout(timer); resolve(log); }
    });
    child.on('exit', code => { clearTimeout(timer); reject(new Error(`exited ${code}: ${log}`)); });
  });
}

const server = spawn(process.execPath, ['scripts/serve.mjs', '--port', String(port)], { cwd: root, stdio: ['ignore', 'pipe', 'pipe'] });
await waitFor(server.stdout, 'Reborn local preview', server);
const profile = await mkdtemp(path.join(tmpdir(), 'aod-c1c2c3-suite-'));
const browser = spawn(chrome, [
  '--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check',
  `--remote-debugging-port=${debugPort}`, `--user-data-dir=${profile}`, 'about:blank',
], { stdio: 'ignore' });

for (let i = 0; i < 40; i++) {
  try { await (await fetch(`http://127.0.0.1:${debugPort}/json/version`)).json(); break; }
  catch { await new Promise(r => setTimeout(r, 100)); }
}
const page = await (await fetch(`http://127.0.0.1:${debugPort}/json/new?http://127.0.0.1:${port}/`, { method: 'PUT' })).json();
const ws = new WebSocket(page.webSocketDebuggerUrl);
await new Promise(r => ws.addEventListener('open', r));
let nextId = 0;
const pending = new Map();
ws.addEventListener('message', event => {
  const msg = JSON.parse(event.data);
  if (msg.id && pending.has(msg.id)) pending.get(msg.id)(msg);
});
function send(method, params = {}) {
  const id = ++nextId;
  return new Promise((resolve, reject) => {
    pending.set(id, msg => {
      pending.delete(id);
      if (msg.error) reject(new Error(JSON.stringify(msg.error)));
      else resolve(msg.result);
    });
    ws.send(JSON.stringify({ id, method, params }));
  });
}
async function evaluate(expression) {
  const res = await send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true });
  if (res.exceptionDetails) throw new Error(res.exceptionDetails.text + ': ' + (res.result?.description || ''));
  return res.result.value;
}
async function waitReady() {
  for (let i = 0; i < 60; i++) {
    const ok = await evaluate(`document.readyState === 'complete' && Boolean(document.querySelector('[data-choice="new-campaign"], [data-choice="open-load"], #context')) && document.querySelector('#status')?.textContent !== 'Opening saved campaign…'`);
    if (ok) return;
    await new Promise(r => setTimeout(r, 100));
  }
  throw new Error('Page did not become ready');
}
async function reloadAndReady() {
  await send('Page.reload');
  await new Promise(r => setTimeout(r, 250));
  await waitReady();
  await evaluate(`(() => {
    window.__downloads = [];
    const origClick = HTMLAnchorElement.prototype.click;
    HTMLAnchorElement.prototype.click = function() {
      if (this.download) {
        window.__downloads.push({ download: this.download, href: this.href });
      }
      return origClick.apply(this, arguments);
    };
  })()`);
}

const evidence = {
  recordedAt: new Date().toISOString(),
  isolatedOrigin: `http://127.0.0.1:${port}`,
  c1: {},
  c2: {},
  c3: {},
};

try {
  await send('Page.enable');
  await send('Runtime.enable');
  await send('Emulation.setDeviceMetricsOverride', { width: 1280, height: 720, deviceScaleFactor: 1, mobile: false });
  await waitReady();
  await evaluate(`(() => {
    window.__downloads = [];
    const origClick = HTMLAnchorElement.prototype.click;
    HTMLAnchorElement.prototype.click = function() {
      if (this.download) window.__downloads.push({ download: this.download, href: this.href });
      return origClick.apply(this, arguments);
    };
  })()`);

  // --- C1.1: New campaign, class choice, enter valley, manual save, reload, Continue ---
  await evaluate(`document.querySelector('[data-choice="new-campaign"]').click()`);
  await new Promise(r => setTimeout(r, 100));
  await evaluate(`document.querySelector('[data-choice="begin-selected-world"]').click()`);
  await new Promise(r => setTimeout(r, 200));
  await evaluate(`(document.querySelector('[data-choice="scene-class:knight"]') || document.querySelector('[data-choice="class:knight"]')).click()`);
  await new Promise(r => setTimeout(r, 100));
  await evaluate(`(document.querySelector('[data-choice="scene-enter-valley"]') || document.querySelector('[data-choice="enter-valley"]')).click()`);
  await new Promise(r => setTimeout(r, 200));
  await evaluate(`document.querySelector('#save').click()`);
  await new Promise(r => setTimeout(r, 200));
  const c1InitialHead = await evaluate(`window.rebornCommittedHead()`);
  await reloadAndReady();
  const c1AfterReload = await evaluate(`({
    view: document.querySelector('#app').dataset.view,
    heroClass: window.rebornSnapshot()?.hero?.class,
    head: window.rebornCommittedHead(),
  })`);
  evidence.c1.newSaveReload = {
    pass: c1AfterReload.heroClass === 'knight' && c1AfterReload.head?.campaignId === c1InitialHead?.campaignId,
    initialHead: c1InitialHead,
    afterReload: c1AfterReload,
  };

  // --- C1.2: Slot 1, 2, 3 save & load + reload continuity ---
  await evaluate(`document.querySelector('#context').click()`);
  await new Promise(r => setTimeout(r, 100));
  await evaluate(`document.querySelector('[data-choice="menu:home"]').click()`);
  await new Promise(r => setTimeout(r, 100));
  await evaluate(`document.querySelector('[data-choice="open-load"]').click()`);
  await new Promise(r => setTimeout(r, 100));
  for (const slot of [1, 2, 3]) {
    await evaluate(`[...document.querySelectorAll('#choices button')].find(b => b.textContent === 'Save slot ${slot}').click()`);
    await new Promise(r => setTimeout(r, 120));
  }
  await evaluate(`[...document.querySelectorAll('#choices button')].find(b => b.textContent === 'Load slot 2').click()`);
  await new Promise(r => setTimeout(r, 250));
  const c1SlotLoad = await evaluate(`({
    view: document.querySelector('#app').dataset.view,
    message: document.querySelector('#message').textContent,
    head: window.rebornCommittedHead(),
  })`);
  evidence.c1.slotSaveLoad = {
    pass: c1SlotLoad.view === 'kingdom' && c1SlotLoad.message.includes('Slot 2 loaded') && c1SlotLoad.head?.epoch >= 2,
    detail: c1SlotLoad,
  };

  // --- C1.3: Invalid import rejection (malformed JSON, bad schema, bad checksum) ---
  await evaluate(`document.querySelector('#context').click()`);
  await new Promise(r => setTimeout(r, 100));
  await evaluate(`document.querySelector('[data-choice="menu:home"]').click()`);
  await new Promise(r => setTimeout(r, 100));
  await evaluate(`document.querySelector('[data-choice="open-load"]').click()`);
  await new Promise(r => setTimeout(r, 100));
  const invalidImports = await evaluate(`(async () => {
    const results = [];
    const input = document.querySelector('#import-file');
    const cases = [
      ['not-json', '{corrupted'],
      ['wrong-schema', JSON.stringify({ schema: 'wrong', version: 99, checksum: 0, payload: '{}' })],
      ['tampered-checksum', JSON.stringify({ schema: 'aod.reborn.campaign', version: 4, checksum: 12345, payload: '{"v":4,"seed":1}' })],
    ];
    for (const [name, content] of cases) {
      const dt = new DataTransfer();
      dt.items.add(new File([content], name + '.json', { type: 'application/json' }));
      input.files = dt.files;
      input.dispatchEvent(new Event('change'));
      await new Promise(r => setTimeout(r, 120));
      results.push({
        name,
        status: document.querySelector('#status').textContent,
        message: document.querySelector('#message').textContent,
        campaignIntact: window.rebornSnapshot()?.hero?.class === 'knight',
      });
    }
    document.querySelector('[data-choice="continue"]').click();
    await new Promise(r => setTimeout(r, 100));
    const afterContinue = {
      view: document.querySelector('#app').dataset.view,
      panelOpen: document.querySelector('#panel').classList.contains('open'),
      status: document.querySelector('#status').textContent,
      saveState: document.querySelector('#save').dataset.saveState,
      heroClass: window.rebornSnapshot()?.hero?.class,
    };
    return { cases: results, afterContinue };
  })()`);
  evidence.c1.invalidImportRejection = {
    pass: invalidImports.cases.every(r => r.status === 'Save failed' && r.campaignIntact && r.message.length > 0)
      && invalidImports.afterContinue.view === 'kingdom'
      && invalidImports.afterContinue.panelOpen === false
      && invalidImports.afterContinue.status !== 'Save failed'
      && invalidImports.afterContinue.saveState === 'committed'
      && invalidImports.afterContinue.heroClass === 'knight',
    cases: invalidImports.cases,
    afterContinue: invalidImports.afterContinue,
  };

  // --- C1.4: Stale-writer CAS conflict & failed-save export (aod-unsaved-campaign.json) ---
  const casConflict = await evaluate(`(async () => {
    const data = await fetch('/src/data/reference-data.json').then(r => r.json());
    const { IndexedDBStorageAdapter } = await import('/src/core/storage-adapter.js');
    const { encode } = await import('/src/core/save.js');
    const tabB = new IndexedDBStorageAdapter();
    const loadedB = await tabB.loadLive(data);
    const slot1 = await tabB.loadSlot(1, data);
    await tabB.replace(loadedB.head, encode(slot1, data), data, 'kingdom');

    window.__downloads = [];
    if (document.querySelector('#save').dataset.saveState !== 'failed') {
      document.querySelector('#save').click();
      await new Promise(r => setTimeout(r, 200));
    }
    const failedState = {
      statusText: document.querySelector('#status').textContent,
      saveDatasetState: document.querySelector('#save').dataset.saveState,
      saveAriaLabel: document.querySelector('#save').getAttribute('aria-label'),
      message: document.querySelector('#message').textContent,
    };
    document.querySelector('#save').click();
    await new Promise(r => setTimeout(r, 100));

    // Also verify that attempting replacement from the stale tab without reconciling is refused by CAS while retaining in-memory state
    document.querySelector('#context').click();
    await new Promise(r => setTimeout(r, 80));
    document.querySelector('[data-choice="menu:home"]').click();
    await new Promise(r => setTimeout(r, 80));
    document.querySelector('[data-choice="open-load"]').click();
    await new Promise(r => setTimeout(r, 80));
    [...document.querySelectorAll('#choices button')].find(b => b.textContent === 'Load slot 1').click();
    await new Promise(r => setTimeout(r, 200));
    const staleReplaceRejected = {
      statusText: document.querySelector('#status').textContent,
      message: document.querySelector('#message').textContent,
      retainedClass: window.rebornSnapshot()?.hero?.class,
    };

    return {
      ...failedState,
      downloads: window.__downloads,
      staleReplaceRejected,
    };
  })()`);
  // Reload to reconcile tab with IndexedDB after the simulated foreign write, then restore Slot 2 cleanly
  await reloadAndReady();
  await evaluate(`(async () => {
    if (document.querySelector('#app').dataset.view !== 'home') {
      document.querySelector('#context').click();
      await new Promise(r => setTimeout(r, 80));
      document.querySelector('[data-choice="menu:home"]').click();
      await new Promise(r => setTimeout(r, 80));
    }
    document.querySelector('[data-choice="open-load"]').click();
    await new Promise(r => setTimeout(r, 80));
    [...document.querySelectorAll('#choices button')].find(b => b.textContent === 'Load slot 2').click();
    await new Promise(r => setTimeout(r, 250));
  })()`);
  const afterConflictReconcile = await evaluate(`({
    view: document.querySelector('#app').dataset.view,
    saveState: document.querySelector('#save').dataset.saveState,
    heroClass: window.rebornSnapshot()?.hero?.class,
  })`);
  evidence.c1.staleWriterConflictAndExport = {
    pass: casConflict.statusText === 'Save failed'
      && casConflict.saveDatasetState === 'failed'
      && casConflict.saveAriaLabel === 'Save failed. Export your unsaved campaign'
      && casConflict.downloads.some(d => d.download === 'aod-unsaved-campaign.json')
      && casConflict.staleReplaceRejected.statusText === 'Save failed'
      && casConflict.staleReplaceRejected.message.includes('Replacement failed. The current campaign is retained.')
      && casConflict.staleReplaceRejected.retainedClass === 'knight'
      && afterConflictReconcile.view === 'kingdom'
      && afterConflictReconcile.saveState === 'committed'
      && afterConflictReconcile.heroClass === 'knight',
    detail: { ...casConflict, afterConflictReconcile },
  };

  // --- C1.5: Damaged live save export (aod-damaged-save.json), double-click Restore valid backup guard, and head-mismatch backup preservation ---
  await evaluate(`(async () => {
    const req = indexedDB.open('aod-reborn-db', 1);
    const db = await new Promise(r => { req.onsuccess = () => r(req.result); });
    const tx = db.transaction(['campaigns'], 'readwrite');
    tx.objectStore('campaigns').put('{"corrupted":true', 'live');
    await new Promise(r => { tx.oncomplete = r; });
    db.close();
  })()`);
  await reloadAndReady();
  await evaluate(`document.querySelector('[data-choice="open-load"]').click()`);
  await new Promise(r => setTimeout(r, 100));
  const damagedCheck = await evaluate(`(async () => {
    const buttonsBefore = [...document.querySelectorAll('#choices button')].map(b => b.textContent);
    const statusBefore = document.querySelector('#status').textContent;
    const exportBtn = [...document.querySelectorAll('#choices button')].find(b => b.textContent === 'Export damaged save');
    if (exportBtn) exportBtn.click();
    const downloadsAfterExport = [...window.__downloads];
    const restoreBtn = [...document.querySelectorAll('#choices button')].find(b => b.textContent === 'Restore valid backup');
    if (restoreBtn) {
      // Rapid double-click must be serialized by replacementPending without throwing "Live save is valid"
      restoreBtn.click();
      restoreBtn.click();
    }
    await new Promise(r => setTimeout(r, 250));
    const afterRestoreView = document.querySelector('#app').dataset.view;
    const afterRestoreStatus = document.querySelector('#status').textContent;
    const afterRestoreSaveState = document.querySelector('#save').dataset.saveState;
    const req = indexedDB.open('aod-reborn-db', 1);
    const db = await new Promise(r => { req.onsuccess = () => r(req.result); });
    const keys = await new Promise(r => {
      const kreq = db.transaction(['campaigns'], 'readonly').objectStore('campaigns').getAllKeys();
      kreq.onsuccess = () => r(kreq.result);
    });
    db.close();
    document.querySelector('#context').click();
    await new Promise(r => setTimeout(r, 80));
    document.querySelector('[data-choice="menu:home"]').click();
    await new Promise(r => setTimeout(r, 80));
    document.querySelector('[data-choice="open-load"]').click();
    await new Promise(r => setTimeout(r, 80));
    const buttonsOnHomeAfterRestore = [...document.querySelectorAll('#choices button')].map(b => b.textContent);
    document.querySelector('[data-choice="continue"]').click();
    await new Promise(r => setTimeout(r, 80));

    // Also test head/payload mismatch damage preservation in IndexedDBStorageAdapter
    const [data, contract] = await Promise.all([
      fetch('/src/data/reference-data.json').then(r => r.json()),
      fetch('/src/data/implementation-contract.json').then(r => r.json()),
    ]);
    const { IndexedDBStorageAdapter } = await import('/src/core/storage-adapter.js');
    const { newCampaign, command } = await import('/src/core/campaign.js');
    const { encode, decode } = await import('/src/core/save.js');
    const memAdapter = new IndexedDBStorageAdapter(null, 'mem-head-mismatch-test');
    let cA = newCampaign(contract, data, 1000, 101);
    cA = command(cA, { id: 'tx-hm-1', type: 'SET_CLASS', payload: { class: 'knight' } }, 1000, data);
    const h1 = await memAdapter.commit(null, encode(cA, data), data);
    cA = command(cA, { id: 'tx-hm-2', type: 'BUILD', payload: { plotId: 'P01', building: 'lumber' } }, 1000, data);
    const h2 = await memAdapter.commit(h1, encode(cA, data), data);
    const backupBeforeMismatch = memAdapter.memoryDb.campaigns.get('backup');
    // Corrupt heads.live checksum so live bytes are valid JSON but mismatch head
    memAdapter.memoryDb.heads.set('live', { ...h2, checksum: 123456 });
    const loadedMismatch = await memAdapter.loadLive(data);
    const restoredFromMismatch = await memAdapter.restoreBackup(data);
    const exportedAfterMismatch = await memAdapter.export();
    const headMismatchPreservedBackup = loadedMismatch.status === 'DAMAGED'
      && restoredFromMismatch.plots.find(p => p.id === 'P01').type === null
      && Object.keys(exportedAfterMismatch.campaigns).some(k => k.startsWith('damaged:'))
      && decode(exportedAfterMismatch.campaigns.backup, data).plots.find(p => p.id === 'P01').type === null;

    return {
      statusBefore,
      buttonsBefore,
      downloadsAfterExport,
      afterRestoreView,
      afterRestoreStatus,
      afterRestoreSaveState,
      campaignKeysInIdb: keys,
      buttonsOnHomeAfterRestore,
      headMismatchPreservedBackup,
    };
  })()`);
  evidence.c1.damagedSaveExportAndBackupRestore = {
    pass: damagedCheck.statusBefore === 'Damaged save'
      && damagedCheck.buttonsBefore.includes('Export damaged save')
      && damagedCheck.buttonsBefore.includes('Restore valid backup')
      && !damagedCheck.buttonsBefore.includes('Continue')
      && damagedCheck.downloadsAfterExport.some(d => d.download === 'aod-damaged-save.json')
      && damagedCheck.afterRestoreView === 'kingdom'
      && damagedCheck.afterRestoreStatus !== 'Save failed'
      && damagedCheck.afterRestoreSaveState === 'committed'
      && damagedCheck.campaignKeysInIdb.some(k => String(k).startsWith('damaged:'))
      && !damagedCheck.buttonsOnHomeAfterRestore.includes('Restore valid backup')
      && !damagedCheck.buttonsOnHomeAfterRestore.includes('Export damaged save')
      && damagedCheck.headMismatchPreservedBackup === true,
    detail: damagedCheck,
  };

  // --- C1.6: Reload continuity across Kingdom, Adventure, Tactical, Defense, Hero, Forge, Army, Story ---
  const reloadViews = {};
  for (const targetView of ['kingdom', 'adventure', 'hero', 'army', 'forge', 'story']) {
    await evaluate(`(async () => {
      if (${JSON.stringify(targetView)} === 'forge' || ${JSON.stringify(targetView)} === 'story') {
        document.querySelector('#context').click();
        await new Promise(r => setTimeout(r, 60));
        document.querySelector('[data-choice="menu:${targetView}"]').click();
      } else {
        document.querySelector('[data-choice="nav:${targetView}"]').click();
      }
      await new Promise(r => setTimeout(r, 100));
      document.querySelector('#save').click();
      await new Promise(r => setTimeout(r, 180));
    })()`);
    await reloadAndReady();
    reloadViews[targetView] = await evaluate(`document.querySelector('#app').dataset.view`);
  }
  // Tactical active session reload continuity
  await evaluate(`(async () => {
    document.querySelector('[data-choice="nav:war"]').click();
    await new Promise(r => setTimeout(r, 80));
    const duelBtn = document.querySelector('[data-choice="start-duel"]') || [...document.querySelectorAll('button')].find(b => b.dataset.choice === 'start-skirmish');
    if (duelBtn) duelBtn.click();
    await new Promise(r => setTimeout(r, 150));
    document.querySelector('#save').click();
    await new Promise(r => setTimeout(r, 180));
  })()`);
  await reloadAndReady();
  reloadViews.tactical = await evaluate(`({ view: document.querySelector('#app').dataset.view, battleStatus: window.rebornSnapshot()?.battle?.status })`);
  // Retreat and settle tactical battle so we can test Defense reload continuity
  await evaluate(`(async () => {
    const inspectBtn = document.querySelector('[data-choice="inspect:tactical"]');
    if (inspectBtn) {
      inspectBtn.click();
      await new Promise(r => setTimeout(r, 80));
    }
    const retreatBtn = document.querySelector('[data-choice="tactical-more:retreat"]');
    if (retreatBtn) {
      retreatBtn.click();
      await new Promise(r => setTimeout(r, 80));
      document.querySelector('#retreat-confirm').click();
      await new Promise(r => setTimeout(r, 120));
    }
    const settleBtn = document.querySelector('[data-choice="settle-battle"]');
    if (settleBtn) {
      settleBtn.click();
      await new Promise(r => setTimeout(r, 120));
    }
  })()`);
  // Defense active session reload continuity
  await evaluate(`(async () => {
    document.querySelector('[data-choice="nav:war"]').click();
    await new Promise(r => setTimeout(r, 80));
    const siegeBtn = document.querySelector('[data-choice="start-siege"]') || [...document.querySelectorAll('button')].find(b => b.textContent.includes('Start Defense') || b.textContent.includes('Begin siege') || b.dataset.choice?.includes('siege'));
    if (siegeBtn) siegeBtn.click();
    await new Promise(r => setTimeout(r, 120));
    const launchWave = document.querySelector('[data-choice="start-siege"]') || [...document.querySelectorAll('button')].find(b => b.dataset.choice === 'start-siege' || b.textContent.includes('Start siege') || b.textContent.includes('Launch'));
    if (launchWave) launchWave.click();
    await new Promise(r => setTimeout(r, 150));
    document.querySelector('#save').click();
    await new Promise(r => setTimeout(r, 180));
  })()`);
  await reloadAndReady();
  reloadViews.defense = await evaluate(`({ view: document.querySelector('#app').dataset.view, defenseStatus: window.rebornSnapshot()?.defense?.status })`);

  evidence.c1.reloadContinuityAcrossStates = {
    pass: reloadViews.kingdom === 'kingdom'
      && reloadViews.adventure === 'adventure'
      && reloadViews.hero === 'hero'
      && reloadViews.army === 'army'
      && reloadViews.forge === 'forge'
      && reloadViews.story === 'story'
      && reloadViews.tactical?.view === 'tactical'
      && ['PENDING', 'ACTIVE'].includes(reloadViews.tactical?.battleStatus)
      && reloadViews.defense?.view === 'defense'
      && reloadViews.defense?.defenseStatus === 'ACTIVE',
    views: reloadViews,
  };

  // --- C2: Campaign, Encounter, Settlement, and Transaction Continuity ---
  // Part A: Live UI transaction + reload continuity (Kingdom build + reload, Adventure move + reload)
  await evaluate(`(async () => {
    document.querySelector('#context').click();
    await new Promise(r => setTimeout(r, 80));
    document.querySelector('[data-choice="menu:home"]').click();
    await new Promise(r => setTimeout(r, 80));
    document.querySelector('[data-choice="open-load"]').click();
    await new Promise(r => setTimeout(r, 80));
    [...document.querySelectorAll('#choices button')].find(b => b.textContent === 'Load slot 2').click();
    await new Promise(r => setTimeout(r, 250));
  })()`);
  const c2UiBeforeReload = await evaluate(`(async () => {
    const worldRect = document.querySelector('#world').getBoundingClientRect();
    const scale = Math.min(worldRect.width / 1376, worldRect.height / 768);
    const ox = (worldRect.width - 1376 * scale) / 2;
    const oy = (worldRect.height - 768 * scale) / 2;
    // Click P01 plot in Kingdom, open building picker, choose lumber, and confirm via #build-commit
    document.querySelector('#world').dispatchEvent(new MouseEvent('click', {
      bubbles: true,
      clientX: worldRect.left + ox + 397 * scale,
      clientY: worldRect.top + oy + 229 * scale,
    }));
    await new Promise(r => setTimeout(r, 80));
    const pickerBtn = document.querySelector('[data-choice="build-picker:P01"]');
    if (pickerBtn) pickerBtn.click();
    await new Promise(r => setTimeout(r, 80));
    const lumberBtn = document.querySelector('[data-choice="build:P01:lumber"]') || document.querySelector('[data-choice^="build:P01:"]');
    if (lumberBtn) lumberBtn.click();
    await new Promise(r => setTimeout(r, 80));
    const confirmBtn = document.querySelector('#build-commit');
    if (confirmBtn) confirmBtn.click();
    await new Promise(r => setTimeout(r, 150));
    const snapAfterBuild = window.rebornSnapshot();
    const p01AfterBuildClick = snapAfterBuild?.plots?.find(p => p.id === 'P01');
    const buildJobCount = snapAfterBuild?.buildJobs?.length || 0;
    const woodAfterBuildClick = snapAfterBuild?.resources?.wood;

    // Enter Adventure via UI nav and leave town via [data-choice="enter-adventure"]
    document.querySelector('[data-choice="nav:adventure"]').click();
    await new Promise(r => setTimeout(r, 100));
    const leaveTownBtn = document.querySelector('[data-choice="enter-adventure"]');
    if (leaveTownBtn) leaveTownBtn.click();
    await new Promise(r => setTimeout(r, 180));
    const advSnap = window.rebornSnapshot()?.adventure;
    return {
      p01Type: p01AfterBuildClick?.type,
      buildJobCount,
      woodAfterBuildClick,
      advPresent: Boolean(advSnap && !advSnap.atTown),
      advPos: [advSnap?.x, advSnap?.y],
    };
  })()`);
  await reloadAndReady();
  const c2UiAfterReload = await evaluate(`(() => {
    const s = window.rebornSnapshot();
    const p01 = s?.plots?.find(p => p.id === 'P01');
    return {
      view: document.querySelector('#app').dataset.view,
      p01Type: p01?.type,
      woodAfterReload: s?.resources?.wood,
      advPresent: Boolean(s?.adventure && !s.adventure.atTown),
      advPos: [s?.adventure?.x, s?.adventure?.y],
    };
  })()`);
  const liveUiTransactionAndReloadContinuity = Boolean(
    c2UiBeforeReload.p01Type === 'lumber'
    && c2UiBeforeReload.buildJobCount >= 1
    && c2UiBeforeReload.woodAfterBuildClick < 250
    && c2UiBeforeReload.advPresent
    && c2UiAfterReload.p01Type === c2UiBeforeReload.p01Type
    && c2UiAfterReload.woodAfterReload === c2UiBeforeReload.woodAfterBuildClick
    && c2UiAfterReload.view === 'adventure'
    && c2UiAfterReload.advPresent
    && c2UiAfterReload.advPos[0] === c2UiBeforeReload.advPos[0]
    && c2UiAfterReload.advPos[1] === c2UiBeforeReload.advPos[1]
  );

  // Part B: Deterministic engine transaction idempotency and single-settlement invariants
  const c2Results = await evaluate(`(async () => {
    const [data, contract, adventureWorlds] = await Promise.all([
      fetch('/src/data/reference-data.json').then(r => r.json()),
      fetch('/src/data/implementation-contract.json').then(r => r.json()),
      fetch('/src/data/adventure-worlds.json').then(r => r.json()),
    ]);
    const { newCampaign, command, advance } = await import('/src/core/campaign.js');
    const { adventureGeometryForWorld, adventureMap, routeTo } = await import('/src/core/navigation.js');

    let s = newCampaign(contract, data, 1000, 424242);
    s = command(s, { id: 'tx-class', type: 'SET_CLASS', payload: { class: 'mage' } }, 1000, data);

    // 1. Duplicate transaction ID idempotency & conflict rejection
    const beforeBuildWood = s.resources.wood;
    s = command(s, { id: 'tx-build-1', type: 'BUILD', payload: { plotId: 'P01', building: 'lumber' } }, 1000, data);
    const afterFirstBuildWood = s.resources.wood;
    const sDup = command(s, { id: 'tx-build-1', type: 'BUILD', payload: { plotId: 'P01', building: 'lumber' } }, 1000, data);
    let conflictingDupRejected = false;
    try {
      command(s, { id: 'tx-build-1', type: 'BUILD', payload: { plotId: 'P02', building: 'farm' } }, 1000, data);
    } catch { conflictingDupRejected = true; }

    // Complete build
    s = advance(s, 30000, data);
    const p01Level = s.plots.find(p => p.id === 'P01').level;

    // 2. Illegal build on occupied plot with different type fails safely without resource loss
    let illegalBuildRejected = false;
    try {
      command(s, { id: 'tx-illegal-build', type: 'BUILD', payload: { plotId: 'P01', building: 'farm' } }, 30000, data);
    } catch { illegalBuildRejected = true; }

    // 3. Adventure movement, cache collection (once), site claim (once), encounter & settlement (once)
    s = command(s, { id: 'tx-adv-enter', type: 'ENTER_ADVENTURE', payload: {} }, 30000, data);
    const worldDef = adventureWorlds.find(w => w.id === s.adventureWorldId);
    const geom = adventureGeometryForWorld(contract.geometry.adventure, worldDef, s.seed);
    const map = adventureMap(geom);
    const start = [s.adventure.x, s.adventure.y];
    const directions = [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]];
    const stepCell = directions.map(([dx, dy]) => [start[0] + dx, start[1] + dy]).find(cell => {
      if (map.guards.has(cell.join(','))) return false;
      try { return routeTo(map, start, cell).cost <= s.adventure.moves; } catch { return false; }
    });
    const moveBefore = s.adventure.moves;
    s = command(s, { id: 'tx-adv-move', type: 'MOVE', payload: { path: [stepCell] } }, 30000, data);
    const moveAfter = s.adventure.moves;

    const woodAnchor = geom.anchors.wood.slice(0, 2).map(Math.floor);
    s.adventure.x = woodAnchor[0];
    s.adventure.y = woodAnchor[1];
    if (!s.adventure.visited.includes(woodAnchor.join(','))) s.adventure.visited.push(woodAnchor.join(','));
    const woodBeforeCache = s.resources.wood;
    s = command(s, { id: 'tx-cache-1', type: 'CLAIM_ADVENTURE_CACHE', payload: { id: 'wood' } }, 30000, data);
    const woodAfterCache = s.resources.wood;
    let duplicateCacheRejected = false;
    try {
      command(s, { id: 'tx-cache-2', type: 'CLAIM_ADVENTURE_CACHE', payload: { id: 'wood' } }, 30000, data);
    } catch { duplicateCacheRejected = true; }

    // Position at mill approach and claim site once
    const millApproach = geom.sites.find(site => site.id === 'mill').approach;
    s.adventure.x = millApproach[0];
    s.adventure.y = millApproach[1];
    if (!s.adventure.visited.includes(millApproach.join(','))) s.adventure.visited.push(millApproach.join(','));
    const foodBeforeSite = s.resources.food;
    s = command(s, { id: 'tx-claim-site-1', type: 'CLAIM_ADVENTURE_SITE', payload: { id: 'mill' } }, 30000, data);
    const foodAfterSite = s.resources.food;
    let duplicateSiteRejected = false;
    try {
      command(s, { id: 'tx-claim-site-2', type: 'CLAIM_ADVENTURE_SITE', payload: { id: 'mill' } }, 30000, data);
    } catch { duplicateSiteRejected = true; }

    // Trigger guard encounter, resolve, settle once, verify duplicate settlement rejected
    const { makePack } = await import('/src/core/mechanics.js');
    s.adventure.pendingEncounter = {
      id: 'guard-10,5',
      cell: [10, 5],
      origin: [10, 6],
      status: 'UNRESOLVED',
      pack: makePack(s, data, s.age, { boss: false, row: 2 }),
    };
    s = command(s, { id: 'tx-enc-start', type: 'BEGIN_ENCOUNTER', payload: {} }, 30000, data);
    for (const st of s.battle.stacks) {
      if (st.side === 'e') { st.count = 1; st.hp = 1; }
    }
    s = command(s, { id: 'tx-enc-auto', type: 'BATTLE', payload: { action: 'auto' } }, 30000, data);
    const goldBeforeSettle = s.resources.gold;
    s = command(s, { id: 'tx-enc-settle-1', type: 'SETTLE_BATTLE', payload: {} }, 30000, data);
    const goldAfterSettle = s.resources.gold;
    let duplicateBattleSettleRejected = false;
    try {
      command(s, { id: 'tx-enc-settle-2', type: 'SETTLE_BATTLE', payload: {} }, 30000, data);
    } catch { duplicateBattleSettleRejected = true; }

    // 4. Defense blast mana & settlement once
    const townApproach = geom.sites.find(site => site.id === 'town').approach;
    s.adventure.x = townApproach[0];
    s.adventure.y = townApproach[1];
    if (!s.adventure.visited.includes(townApproach.join(','))) s.adventure.visited.push(townApproach.join(','));
    s = command(s, { id: 'tx-return-town', type: 'RETURN_TOWN', payload: {} }, 30000, data);
    s = command(s, { id: 'tx-end-day', type: 'END_DAY', payload: {} }, 30000, data);
    s = command(s, { id: 'tx-def-start', type: 'START_SIEGE', payload: {} }, 30000, data);
    s = command(s, { id: 'tx-def-deploy', type: 'DEPLOY_DEFENSE', payload: {} }, 30000, data);
    s = command(s, { id: 'tx-def-tick', type: 'DEFENSE', payload: { dt: 2, speed: 1 } }, 30000, data);
    const manaBeforeBlast = s.hero.mana;
    s = command(s, { id: 'tx-def-blast', type: 'DEFENSE_CAST', payload: {} }, 30000, data);
    const manaAfterBlast = s.hero.mana;
    let cooldownBlastRejected = false;
    try {
      command(s, { id: 'tx-def-blast-2', type: 'DEFENSE_CAST', payload: {} }, 30000, data);
    } catch { cooldownBlastRejected = true; }
    for (const enemy of s.defense.queue) {
      enemy.spawned = true;
      enemy.hp = 0;
    }
    s.defense.enemies = [...s.defense.queue];
    s.defense.clearedWaves = s.defense.waves;
    s.defense.status = 'RESOLVED';
    s.defense.winner = 'p';
    s.defense.pendingSettlement = true;
    const goldBeforeDefSettle = s.resources.gold;
    s = command(s, { id: 'tx-def-settle-1', type: 'SETTLE_DEFENSE', payload: {} }, 30000, data);
    const goldAfterDefSettle = s.resources.gold;
    let duplicateDefSettleRejected = false;
    try {
      command(s, { id: 'tx-def-settle-2', type: 'SETTLE_DEFENSE', payload: {} }, 30000, data);
    } catch { duplicateDefSettleRejected = true; }

    // 5. Forge, equip, unequip
    s.plots.find(p => p.id === 'P02').type = 'armory';
    s.plots.find(p => p.id === 'P02').level = 3;
    s.resources.wood = 900; s.resources.stone = 900; s.resources.gold = 900; s.resources.food = 900;
    s = command(s, { id: 'tx-forge-1', type: 'FORGE', payload: { slot: 'weapon', quality: 1 } }, 30000, data);
    const forgedId = s.inventory[s.inventory.length - 1].id;
    s = command(s, { id: 'tx-equip-1', type: 'EQUIP', payload: { itemId: forgedId } }, 30000, data);
    const equippedWeaponId = s.hero.equip.weapon?.id;
    s = command(s, { id: 'tx-unequip-1', type: 'UNEQUIP', payload: { slot: 'weapon' } }, 30000, data);
    const unequippedBackToBag = s.hero.equip.weapon === null && s.inventory.some(i => i.id === forgedId);

    // 6. Quest claim once & Age progression gate
    s.plots.find(p => p.id === 'P03').type = 'barracks';
    s.plots.find(p => p.id === 'P03').level = 1;
    s = command(s, { id: 'tx-rec-1', type: 'RECRUIT', payload: { role: 'melee' } }, 30000, data);
    let ageGateRejectedWhenHallLow = false;
    try {
      command(s, { id: 'tx-age-low', type: 'AGE_UP', payload: {} }, 30000, data);
    } catch { ageGateRejectedWhenHallLow = true; }
    s.plots.find(p => p.id === 'townhall').level = 2;
    s.resources.food = 2000; s.resources.wood = 2000; s.resources.stone = 2000; s.resources.gold = 2000;
    s = command(s, { id: 'tx-age-up', type: 'AGE_UP', payload: {} }, 30000, data);
    const q2GoldBefore = s.resources.gold;
    s = command(s, { id: 'tx-quest-2-claim', type: 'CLAIM_QUEST', payload: { id: 'q2' } }, 30000, data);
    const q2GoldAfter = s.resources.gold;
    let duplicateQuestRejected = false;
    try {
      command(s, { id: 'tx-quest-2-dup', type: 'CLAIM_QUEST', payload: { id: 'q2' } }, 30000, data);
    } catch { duplicateQuestRejected = true; }

    return {
      idempotentTx: sDup.resources.wood === afterFirstBuildWood && afterFirstBuildWood < beforeBuildWood && conflictingDupRejected,
      buildCompleted: p01Level === 1 && illegalBuildRejected,
      adventureMoveAndCacheOnce: moveAfter < moveBefore && woodAfterCache > woodBeforeCache && duplicateCacheRejected,
      siteClaimOnce: foodAfterSite > foodBeforeSite && duplicateSiteRejected && s.adventure.claimedSites.includes('mill'),
      battleSettleOnce: goldAfterSettle > goldBeforeSettle && duplicateBattleSettleRejected && s.battle === null,
      defenseBlastAndSettleOnce: manaAfterBlast < manaBeforeBlast && cooldownBlastRejected && goldAfterDefSettle > goldBeforeDefSettle && duplicateDefSettleRejected && s.defense === null,
      forgeEquipAndUnequip: equippedWeaponId === forgedId && unequippedBackToBag,
      questClaimOnceAndAgeUp: q2GoldAfter > q2GoldBefore && duplicateQuestRejected && ageGateRejectedWhenHallLow && s.age === 1,
    };
  })()`);
  evidence.c2 = {
    pass: liveUiTransactionAndReloadContinuity && Object.values(c2Results).every(Boolean),
    checks: {
      liveUiTransactionAndReloadContinuity,
      ...c2Results,
    },
    uiContinuityDetail: { beforeReload: c2UiBeforeReload, afterReload: c2UiAfterReload },
  };

  // --- C3: Critical Input & Hit-Testing Across Supported Landscape Viewports ---
  await evaluate(`(async () => {
    document.querySelector('#context').click();
    await new Promise(r => setTimeout(r, 80));
    document.querySelector('[data-choice="menu:home"]').click();
    await new Promise(r => setTimeout(r, 80));
    document.querySelector('[data-choice="open-load"]').click();
    await new Promise(r => setTimeout(r, 80));
    [...document.querySelectorAll('#choices button')].find(b => b.textContent === 'Load slot 2').click();
    await new Promise(r => setTimeout(r, 250));
  })()`);

  const viewports = [[825, 375], [933, 424], [933, 425], [1280, 720], [1376, 768]];
  evidence.c3.viewports = {};
  for (const [width, height] of viewports) {
    await send('Emulation.setDeviceMetricsOverride', { width, height, deviceScaleFactor: 1, mobile: false });
    await new Promise(r => setTimeout(r, 120));
    const vpCheck = await evaluate(`(async () => {
      if (document.querySelector('#panel').classList.contains('open')) {
        document.querySelector('#panel-close').click();
        await new Promise(r => setTimeout(r, 60));
      }
      document.querySelector('[data-choice="nav:kingdom"]').click();
      await new Promise(r => setTimeout(r, 80));

      const selectors = ['#context', '#save', '[data-choice="nav:kingdom"]', '[data-choice="nav:adventure"]', '[data-choice="nav:hero"]', '[data-choice="nav:army"]', '[data-choice="nav:war"]', '#dock button'];
      const hitTests = selectors.map(sel => {
        const el = document.querySelector(sel);
        if (!el) return { sel, found: false };
        const r = el.getBoundingClientRect();
        const cx = r.left + r.width / 2;
        const cy = r.top + r.height / 2;
        const topEl = document.elementFromPoint(cx, cy);
        const hitSelf = Boolean(topEl && (topEl === el || el.contains(topEl)));
        const topTag = topEl ? (topEl.tagName + '#' + topEl.id + '.' + topEl.className + '[' + (topEl.textContent || '').slice(0, 20) + ']') : null;
        return { sel, found: true, width: Math.round(r.width), height: Math.round(r.height), left: Math.round(r.left), top: Math.round(r.top), inViewport: r.left >= 0 && r.top >= 0 && r.right <= window.innerWidth + 1 && r.bottom <= window.innerHeight + 1, hitSelf, topTag };
      });

      const worldRect = document.querySelector('#world').getBoundingClientRect();
      const scale = Math.min(worldRect.width / 1376, worldRect.height / 768);
      const ox = (worldRect.width - 1376 * scale) / 2;
      function clickSource(sx, sy) {
        const cx = worldRect.left + ox + sx * scale;
        const cy = worldRect.top + (worldRect.height - 768 * scale) / 2 + sy * scale;
        document.querySelector('#world').dispatchEvent(new MouseEvent('click', { bubbles: true, clientX: cx, clientY: cy }));
        return window.rebornPick?.site;
      }
      const pickTownhall = clickSource(578.75, 126.25);
      // Verify #panel-close and #choices button remain clickable and unoccluded while #panel is open on Kingdom
      const panelControlsWhileOpen = (() => {
        const closeEl = document.querySelector('#panel-close');
        const choiceEl = document.querySelector('#choices button');
        if (!closeEl || !choiceEl) return { found: false };
        const cr = closeEl.getBoundingClientRect();
        const chr = choiceEl.getBoundingClientRect();
        const topClose = document.elementFromPoint(cr.left + cr.width / 2, cr.top + cr.height / 2);
        const topChoice = document.elementFromPoint(chr.left + chr.width / 2, chr.top + chr.height / 2);
        return {
          found: true,
          panelOpen: document.querySelector('#panel').classList.contains('open'),
          closeInViewport: cr.left >= 0 && cr.top >= 0 && cr.right <= window.innerWidth + 1 && cr.bottom <= window.innerHeight + 1,
          closeHitSelf: Boolean(topClose && (topClose === closeEl || closeEl.contains(topClose))),
          choiceInViewport: chr.left >= 0 && chr.top >= 0 && chr.right <= window.innerWidth + 1 && chr.bottom <= window.innerHeight + 1,
          choiceHitSelf: Boolean(topChoice && (topChoice === choiceEl || choiceEl.contains(topChoice))),
        };
      })();
      if (document.querySelector('#panel').classList.contains('open')) document.querySelector('#panel-close').click();
      const pickP01 = clickSource(397, 229);
      if (document.querySelector('#panel').classList.contains('open')) document.querySelector('#panel-close').click();

      const navAdv = document.querySelector('[data-choice="nav:adventure"]');
      const nr = navAdv.getBoundingClientRect();
      navAdv.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true, pointerId: 77, clientX: nr.left + 10, clientY: nr.top + 10 }));
      document.dispatchEvent(new PointerEvent('pointermove', { bubbles: true, pointerId: 77, clientX: nr.left + 35, clientY: nr.top + 10 }));
      document.dispatchEvent(new PointerEvent('pointerup', { bubbles: true, pointerId: 77, clientX: nr.left + 35, clientY: nr.top + 10 }));
      navAdv.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, clientX: nr.left + 35, clientY: nr.top + 10 }));
      const dragCancelled = document.querySelector('#app').dataset.view === 'kingdom';

      return {
        hitTests,
        pickTownhall,
        panelControlsWhileOpen,
        pickP01,
        dragCancelled,
      };
    })()`);
    evidence.c3.viewports[`${width}x${height}`] = {
      pass: vpCheck.hitTests.every(h => h.found && h.inViewport && h.hitSelf && h.width >= 28 && h.height >= 28)
        && vpCheck.pickTownhall === 'townhall'
        && vpCheck.panelControlsWhileOpen.panelOpen === true
        && vpCheck.panelControlsWhileOpen.closeInViewport === true
        && vpCheck.panelControlsWhileOpen.closeHitSelf === true
        && vpCheck.panelControlsWhileOpen.choiceInViewport === true
        && vpCheck.panelControlsWhileOpen.choiceHitSelf === true
        && vpCheck.pickP01 === 'P01'
        && vpCheck.dragCancelled === true,
      ...vpCheck,
    };
  }

  // --- C3.4: Modal / Overlay click-through blocking (#build-confirm and #retreat) ---
  await send('Emulation.setDeviceMetricsOverride', { width: 1280, height: 720, deviceScaleFactor: 1, mobile: false });
  const modalProtection = await evaluate(`(async () => {
    const worldRect = document.querySelector('#world').getBoundingClientRect();
    const scale = Math.min(worldRect.width / 1376, worldRect.height / 768);
    const cx = worldRect.left + (worldRect.width - 1376 * scale) / 2 + 578.75 * scale;
    const cy = worldRect.top + (worldRect.height - 768 * scale) / 2 + 126.25 * scale;
    document.querySelector('#world').dispatchEvent(new MouseEvent('click', { bubbles: true, clientX: cx, clientY: cy }));
    await new Promise(r => setTimeout(r, 80));
    const buildBtn = document.querySelector('[data-choice^="build:"]');
    if (buildBtn) buildBtn.click();
    await new Promise(r => setTimeout(r, 80));
    const buildModalOpen = !document.querySelector('#build-confirm').hidden;
    const buildInert = document.querySelector('#stage-field').inert && document.querySelector('header').inert && document.querySelector('footer').inert;
    const backClosedBuild = window.rebornHandleBack();

    document.querySelector('[data-choice="nav:war"]').click();
    await new Promise(r => setTimeout(r, 80));
    document.querySelector('[data-choice="start-duel"]').click();
    await new Promise(r => setTimeout(r, 120));
    if (!document.querySelector('#panel').classList.contains('open')) {
      document.querySelector('[data-choice="inspect:tactical"]').click();
      await new Promise(r => setTimeout(r, 80));
    }
    document.querySelector('[data-choice="tactical-more:retreat"]').click();
    await new Promise(r => setTimeout(r, 80));
    const retreatDialogOpen = !document.querySelector('#retreat').hidden;
    const retreatInert = document.querySelector('#stage-field').inert && document.querySelector('header').inert && document.querySelector('footer').inert;
    document.querySelector('[data-choice="nav:kingdom"]').click();
    const viewStayedTactical = document.querySelector('#app').dataset.view === 'tactical';
    document.querySelector('#retreat-cancel').click();
    await new Promise(r => setTimeout(r, 80));
    const retreatClosed = document.querySelector('#retreat').hidden;

    return {
      buildModalOpen,
      buildInert,
      backClosedBuild,
      retreatDialogOpen,
      retreatInert,
      viewStayedTactical,
      retreatClosed,
    };
  })()`);
  evidence.c3.modalOverlayProtection = {
    pass: Object.values(modalProtection).every(Boolean),
    detail: modalProtection,
  };
  evidence.c3.pass = Object.values(evidence.c3.viewports).every(v => v.pass) && evidence.c3.modalOverlayProtection.pass;
  evidence.c1.pass = Object.values(evidence.c1).every(v => v.pass);
  evidence.overallPass = evidence.c1.pass && evidence.c2.pass && evidence.c3.pass;

  await writeFile(path.join(outDir, 'c1-c2-c3-browser-evidence.json'), JSON.stringify(evidence, null, 2));
  console.log('SUMMARY:', JSON.stringify({
    overallPass: evidence.overallPass,
    c1Pass: evidence.c1.pass,
    c2Pass: evidence.c2.pass,
    c3Pass: evidence.c3.pass,
    c1Checks: Object.fromEntries(Object.entries(evidence.c1).filter(([k]) => k !== 'pass').map(([k, v]) => [k, v.pass])),
    c2Checks: evidence.c2.checks,
    c3Viewports: Object.fromEntries(Object.entries(evidence.c3.viewports).map(([k, v]) => [k, v.pass])),
    c3Modal: evidence.c3.modalOverlayProtection.pass,
  }, null, 2));
} finally {
  ws.close();
  browser.kill();
  server.kill();
  await new Promise(r => setTimeout(r, 300));
  await rm(profile, { recursive: true, force: true }).catch(() => {});
}
