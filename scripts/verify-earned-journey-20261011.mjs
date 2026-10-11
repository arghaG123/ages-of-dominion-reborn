// Earned-gameplay journey in an isolated headless Chrome profile (raw CDP, no debug grants).
// Real UI commands only: build, wait real construction time, recruit, travel, fight, settle,
// reload, forge/equip, siege, war modes, story, settings, slots. Writes machine-readable
// evidence and bounded captures to qa/code-image-complete-20261011/.
import { spawn } from 'node:child_process';
import { mkdtemp, mkdir, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';

const root = process.cwd();
const chrome = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const port = Number(process.env.AOD_PORT || 4533);
const debugPort = Number(process.env.AOD_DEBUG_PORT || 9353);
const outDir = path.join(root, 'qa', 'code-image-complete-20261011');
await mkdir(outDir, { recursive: true });

const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
function waitForText(stream, text, child) {
  return new Promise((resolve, reject) => {
    let log = '';
    const timer = setTimeout(() => reject(new Error(log || 'timed out')), 15000);
    stream.on('data', chunk => { log += chunk; if (log.includes(text)) { clearTimeout(timer); resolve(log); } });
    child.on('exit', code => { clearTimeout(timer); reject(new Error(`exited ${code}: ${log}`)); });
  });
}

const server = spawn(process.execPath, ['scripts/serve.mjs', '--port', String(port)], { cwd: root, stdio: ['ignore', 'pipe', 'pipe'] });
await waitForText(server.stdout, 'Reborn local preview', server);
const profile = await mkdtemp(path.join(tmpdir(), 'aod-chrome-'));
const browser = spawn(chrome, ['--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check', '--hide-scrollbars', `--remote-debugging-port=${debugPort}`, `--user-data-dir=${profile}`, 'about:blank'], { stdio: 'ignore' });
for (let i = 0; i < 60; i++) {
  try { await (await fetch(`http://127.0.0.1:${debugPort}/json/version`)).json(); break; }
  catch { await sleep(100); }
}
const page = await (await fetch(`http://127.0.0.1:${debugPort}/json/new?http://127.0.0.1:${port}/`, { method: 'PUT' })).json();
const ws = new WebSocket(page.webSocketDebuggerUrl);
await new Promise(resolve => { ws.addEventListener('open', resolve); });
let nextId = 0;
const pending = new Map();
const consoleErrors = [];
ws.addEventListener('message', event => {
  const message = JSON.parse(event.data);
  if (message.id && pending.has(message.id)) pending.get(message.id)(message);
  else if (message.method === 'Runtime.exceptionThrown') consoleErrors.push({ kind: 'exception', text: message.params.exceptionDetails?.exception?.description || message.params.exceptionDetails?.text });
  else if (message.method === 'Runtime.consoleAPICalled' && (message.params.type === 'error' || message.params.type === 'warning')) consoleErrors.push({ kind: message.params.type, text: message.params.args.map(arg => arg.value ?? arg.description).join(' ') });
  else if (message.method === 'Network.loadingFailed') consoleErrors.push({ kind: 'network', text: message.params.errorText });
  else if (message.method === 'Network.responseReceived' && message.params.response.status >= 400) consoleErrors.push({ kind: 'http', text: `${message.params.response.status} ${message.params.response.url}` });
});
function send(method, params = {}) {
  const id = ++nextId;
  return new Promise((resolve, reject) => {
    pending.set(id, message => { pending.delete(id); if (message.error) reject(new Error(JSON.stringify(message.error))); else resolve(message.result); });
    ws.send(JSON.stringify({ id, method, params }));
  });
}
async function evaluate(expression) {
  const result = await send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true });
  if (result.exceptionDetails) throw new Error(result.exceptionDetails.exception?.description || result.exceptionDetails.text || 'evaluate failed');
  return result.result.value;
}
const snap = () => evaluate('window.rebornSnapshot()');
const view = () => evaluate(`document.querySelector('#app').dataset.view`);
async function click(selector, { optional = false } = {}) {
  const clicked = await evaluate(`(() => { const node = document.querySelector(${JSON.stringify(selector)}); if (!node) return false; node.click(); return true; })()`);
  if (!clicked && !optional) throw new Error(`missing ${selector}`);
  await sleep(60);
  return clicked;
}
async function clickText(text) {
  const clicked = await evaluate(`(() => { const node = [...document.querySelectorAll('button')].find(button => button.textContent.trim() === ${JSON.stringify(text)}); if (!node) return false; node.click(); return true; })()`);
  if (!clicked) throw new Error(`missing button ${text}`);
  await sleep(60);
}
async function waitUntil(expression, timeoutMs, label) {
  const started = Date.now();
  while (Date.now() - started < timeoutMs) {
    if (await evaluate(expression)) return Date.now() - started;
    await sleep(250);
  }
  throw new Error(`timeout waiting for ${label || expression}`);
}
async function setViewport(width, height) {
  await send('Emulation.setDeviceMetricsOverride', { width, height, deviceScaleFactor: 1, mobile: false });
  await evaluate('new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))');
  await sleep(80);
}
async function capture(name) {
  const shot = await send('Page.captureScreenshot', { format: 'png' });
  await writeFile(path.join(outDir, name + '.png'), Buffer.from(shot.data, 'base64'));
}
async function screenHealth() {
  return evaluate(`(() => {
    const stage = document.querySelector('#stage').getBoundingClientRect();
    const buttons = [...document.querySelectorAll('button')].filter(node => { const r = node.getBoundingClientRect(); return r.width > 0 && r.height > 0; });
    const small = buttons.filter(node => { const r = node.getBoundingClientRect(); return r.width < 48 || r.height < 48; }).map(node => node.textContent.trim().slice(0, 40));
    const controls = [...document.querySelectorAll('button,[role="button"],input:not([hidden]),select,textarea')].filter(node => { const r = node.getBoundingClientRect(); const style = getComputedStyle(node); return r.width > 0 && r.height > 0 && style.visibility !== 'hidden' && style.display !== 'none'; });
    const smallControls = controls.filter(node => { const r = node.getBoundingClientRect(); return r.width < 48 - 0.5 || r.height < 48 - 0.5; }).map(node => (node.dataset.choice || node.dataset.heroSlot || node.dataset.slot || node.getAttribute('aria-label') || node.textContent || '').trim().slice(0, 40));
    const texts = [...document.querySelectorAll('#world text, #scene-ui p, #scene-ui button, #scene-ui span')].map(node => {
      const style = getComputedStyle(node);
      const font = parseFloat(style.fontSize) || 0;
      const matrix = node.getScreenCTM?.();
      const scale = matrix ? Math.hypot(matrix.a, matrix.b) : 1;
      return { text: (node.textContent || '').slice(0, 32), cssFont: font * (node.ownerSVGElement ? scale : 1) };
    }).filter(row => row.text.trim());
    const smallTexts = texts.filter(row => row.cssFont < 12);
    const failedImages = [...document.querySelectorAll('img')].filter(node => node.getAttribute('src') && node.complete && node.naturalWidth === 0).map(node => node.getAttribute('src'));
    const svgImages = [...document.querySelectorAll('#world image')].map(node => node.getAttribute('href'));
    return { view: document.querySelector('#app').dataset.view, buttons: buttons.length, small, smallControls, smallTexts, failedImages, svgImages: svgImages.length, stage: { w: Math.round(stage.width), h: Math.round(stage.height) }, title: document.querySelector('#selected').textContent, message: document.querySelector('#message').textContent.slice(0, 160) };
  })()`);
}

const report = { date: new Date().toISOString(), fixtureFree: true, steps: [], checks: [], errors: [], screens: [] };
// Resources tick in real time between snapshots; compare earned amounts within 2 units.
const near = (a, b, eps = 2) => Math.abs(a - b) < eps;
const check = (id, pass, detail) => { report.checks.push({ id, pass: Boolean(pass), detail }); if (!pass) console.error('FAIL', id, JSON.stringify(detail).slice(0, 400)); };
const step = (id, detail) => report.steps.push({ id, at: Date.now(), detail });

async function autoBattle(label, maxMs = 90000) {
  const started = Date.now();
  while (Date.now() - started < maxMs) {
    const s = await snap();
    if (!s.battle) return { ended: true, settled: true };
    if (s.battle.pendingSettlement || s.battle.status !== 'ACTIVE') return { ended: true, settled: false, winner: s.battle.outcome?.winner, log: s.battle.log?.length };
    const clicked = await evaluate(`(() => { const node = document.querySelector('#dock [data-choice="auto"]'); if (!node || node.disabled) return false; node.click(); return true; })()`);
    if (!clicked) await sleep(200);
  }
  throw new Error(`${label} did not resolve`);
}

async function buildOnEmptyPad(type) {
  const before = await snap();
  const picked = await evaluate(`(() => {
    const pad = [...document.querySelectorAll('.plot[data-pad-state="empty"]')].find(node => !node.getAttribute('aria-label').startsWith('townhall'));
    if (!pad) return null;
    pad.dispatchEvent(new MouseEvent('click', { bubbles: true, clientX: 0, clientY: 0 }));
    return pad.getAttribute('aria-label');
  })()`);
  if (!picked) throw new Error('no empty pad');
  await sleep(60);
  const clicked = await evaluate(`(() => { const node = [...document.querySelectorAll('#choices [data-choice^="build:"]')].find(node => node.dataset.choice.endsWith(':${type}') && !node.disabled); if (!node) return false; node.click(); return true; })()`);
  if (!clicked) throw new Error(`cannot build ${type}: ` + await evaluate(`[...document.querySelectorAll('#choices [data-choice^="build:"]')].map(n => n.textContent).join(' | ')`));
  const after = await snap();
  const job = after.buildJobs.find(j => j.type === type);
  check(`build-${type}-job`, job && after.buildJobs.length === before.buildJobs.length + 1, { picked, job });
  const waited = await waitUntil(`(() => { const s = window.rebornSnapshot(); return !s.buildJobs.some(j => j.type === ${JSON.stringify(type)}); })()`, 15000, `${type} completion`);
  const done = await snap();
  check(`build-${type}-complete`, done.plots.some(p => p.type === type && p.level === 1), { waitedMs: waited });
  return done;
}

try {
  await send('Page.enable');
  await send('Runtime.enable');
  await send('Network.enable');
  await setViewport(1280, 720);
  await evaluate(`new Promise(resolve => { if (document.readyState === 'complete') resolve(true); else addEventListener('load', () => resolve(true), { once: true }); })`);
  check('home-empty-profile', (await evaluate('localStorage.length')) === 0 && (await view()) === 'home', {});
  await capture('01-home-1280');

  // 1. New campaign, class choice in the Hero room, enter the valley.
  await click('[data-choice="new-campaign"]');
  check('class-choice-hero-room', (await view()) === 'hero' && (await evaluate(`document.querySelectorAll('[data-class-card]').length`)) === 8, {});
  await evaluate(`document.querySelector('[data-class-card="knight"]').dispatchEvent(new MouseEvent('click', { bubbles: true }))`);
  await sleep(60);
  const heroBody = await evaluate(`(() => {
    const actor = document.querySelector('[data-actor="knight"]');
    const image = actor?.querySelector('image');
    return { presentation: actor?.dataset.presentation || '', kit: actor?.dataset.kitMatch || '', reason: actor?.dataset.bodyReason || '', href: image?.getAttribute('href') || '', css: image?.dataset.visibleCssHeight || '' };
  })()`);
  check('hero-presentation-honest', heroBody.reason === 'kit-era-mismatch' || heroBody.kit === 'unverified' || (heroBody.kit === '1' && heroBody.href.includes('standing-body')), heroBody);
  const imageLoads = await evaluate(`(async () => {
    const hrefs = [...document.querySelectorAll('#world image, #scene-ui img')].map(node => node.getAttribute('href') || node.getAttribute('src')).filter(Boolean);
    const results = [];
    for (const href of hrefs) {
      const response = await fetch(href);
      const type = response.headers.get('content-type') || '';
      results.push({ href, ok: response.ok, type });
    }
    return results.filter(row => !row.ok || !row.type.startsWith('image/'));
  })()`);
  check('hero-images-load', imageLoads.length === 0, imageLoads);
  await sleep(1200);
  await capture('02-class-choice-1280');
  await click('[data-choice="enter-valley"]');
  check('enter-valley', (await view()) === 'kingdom', {});
  const start = await snap();
  check('day1-start-state', start.age === 0 && start.day === 1 && start.resources.food === 250 && start.resources.wood === 250 && start.resources.stone === 160 && start.resources.gold === 150 && start.plots.filter(p => p.id !== 'townhall' && p.level === 0).length === 17 && start.walls.level === 0 && start.army.length === 2, { resources: start.resources, army: start.army.map(a => `${a.type}x${a.count}`) });
  await capture('03-kingdom-day1-1280');

  // 2. Build the tutorial facilities for real and wait the real construction time.
  for (const type of ['lumber', 'farm', 'quarry', 'barracks']) await buildOnEmptyPad(type);
  const woodBefore = (await snap()).resources.wood;
  await sleep(4000);
  const woodAfter = (await snap()).resources.wood;
  check('completed-lumber-earns-income', woodAfter > woodBefore && woodAfter - woodBefore < 0.45 * 4.6, { woodBefore, woodAfter });
  await capture('04-kingdom-built-1280');

  // 3. Recruit through a real Barracks.
  await click('[data-choice="nav:army"]');
  const armyBefore = await snap();
  await click('[data-choice="recruit:melee"]');
  const armyAfter = await snap();
  const melee = armyAfter.army.find(a => a.kind === 'role' && a.type === 'melee');
  check('recruit-five-melee', melee && melee.count === armyBefore.army.find(a => a.type === 'melee').count + 5 && Math.abs((armyBefore.resources.food - armyAfter.resources.food) - 225) < 2 && Math.abs((armyBefore.resources.gold - armyAfter.resources.gold) - 50) < 2, { before: armyBefore.resources, after: armyAfter.resources });
  const slinger = await evaluate(`(() => { const node = document.querySelector('#board img[data-plate*="troop-stone-ranged"]'); return node ? { src: node.dataset.plate, ok: node.naturalWidth > 0, h: node.getBoundingClientRect().height } : null; })()`);
  check('army-shows-new-slinger', slinger && slinger.src.includes('image-vertex-repair-20261009') && slinger.ok && slinger.h > 40 && slinger.h <= 131, slinger);
  await sleep(600);
  await capture('05-army-1280');

  // 4. Travel to the mine guard, fight it with the real engine, settle once.
  await click('[data-choice="nav:adventure"]');
  await click('[data-choice="enter-adventure"]');
  for (const dir of ['north', 'north', 'east', 'east', 'north']) await click(`#choices [data-choice="preview-${dir}"]`);
  const previewCost = await evaluate(`document.querySelector('#choices [data-choice="confirm-route"]').textContent`);
  const beforeMove = await snap();
  await click('#choices [data-choice="confirm-route"]');
  const moved = await snap();
  check('route-preview-then-commit', beforeMove.adventure.moves === 5 && moved.adventure.moves === 0 && moved.adventure.x === 10 && moved.adventure.y === 5 && moved.adventure.pendingEncounter?.status === 'UNRESOLVED', { previewCost, at: [moved.adventure.x, moved.adventure.y], moves: moved.adventure.moves });
  await sleep(1500);
  await capture('06-adventure-guard-1280');
  await click('#choices [data-choice="begin-encounter"]');
  check('encounter-opens-tactical', (await view()) === 'tactical' && (await snap()).battle?.status === 'ACTIVE', {});
  await sleep(400);
  await capture('07-tactical-guard-1280');
  const fight = await autoBattle('guard battle');
  const resolved = await snap();
  check('guard-battle-resolved', fight.ended && resolved.battle?.pendingSettlement, fight);
  const preSettle = await snap();
  await click('[data-choice="settle-battle"]');
  const settled = await snap();
  check('guard-settled-once', !settled.battle && settled.adventure.pendingEncounter == null && (settled.adventure.resolvedGuards.includes('10,5') || preSettle.battle.outcome?.winner !== 'p'), { winner: preSettle.battle.outcome?.winner, xp: settled.hero.xp, inventory: settled.inventory.length, army: settled.army.map(a => `${a.type}x${a.count}`), resolvedGuards: settled.adventure.resolvedGuards });
  check('guard-win-pays-xp', preSettle.battle.outcome?.winner !== 'p' || settled.hero.xp > 0, { xp: settled.hero.xp });
  // The settled command must not re-apply.
  const again = await evaluate(`(() => { const node = document.querySelector('[data-choice="settle-battle"]'); return node ? 'present' : 'absent'; })()`);
  check('settle-button-gone', again === 'absent', {});

  // 5. Reload persists the exact state.
  await evaluate('location.reload()');
  await sleep(1500);
  const reloaded = await snap();
  // Revision may advance on load (catch-up production tick); the earned facts must survive exactly.
  check('reload-persists-state', reloaded.revision >= settled.revision && reloaded.hero.xp === settled.hero.xp && reloaded.adventure.x === settled.adventure.x && reloaded.adventure.y === settled.adventure.y && JSON.stringify(reloaded.army) === JSON.stringify(settled.army) && JSON.stringify(reloaded.adventure.resolvedGuards) === JSON.stringify(settled.adventure.resolvedGuards), { revision: [settled.revision, reloaded.revision], xp: [settled.hero.xp, reloaded.hero.xp], position: [[settled.adventure.x, settled.adventure.y], [reloaded.adventure.x, reloaded.adventure.y]], army: [settled.army.map(a => `${a.type}x${a.count}`), reloaded.army.map(a => `${a.type}x${a.count}`)], view: await view() });

  // 6. End day refills movement, return to town through the approach.
  await click('[data-choice="nav:kingdom"]');
  await click('[data-choice="end-day"]');
  const dayTwo = await snap();
  check('end-day-no-invented-income', dayTwo.day === 2 && dayTwo.adventure.moves === 5, { day: dayTwo.day, moves: dayTwo.adventure.moves, weather: dayTwo.weather });
  await click('[data-choice="nav:adventure"]');
  for (const dir of ['west', 'north', 'west']) await click(`#choices [data-choice="preview-${dir}"]`);
  await click('#choices [data-choice="confirm-route"]');
  const atTown = await snap();
  check('reached-town-approach', atTown.adventure.x === 8 && atTown.adventure.y === 4, { at: [atTown.adventure.x, atTown.adventure.y] });
  await click('#choices [data-choice="return-town"]');
  check('return-town', (await view()) === 'kingdom' && (await snap()).adventure.atTown === true, {});

  // 7. Wait for real production to afford an Armory, then forge and equip through the UI.
  const armoryWait = await waitUntil(`(() => { const r = window.rebornSnapshot().resources; return r.wood >= 120 && r.stone >= 120 && r.gold >= 80; })()`, 9 * 60000, 'armory affordability');
  step('armory-affordable', { waitedMs: armoryWait });
  await click('[data-choice="nav:kingdom"]');
  await buildOnEmptyPad('armory');
  const forgeWait = await waitUntil(`(() => { const r = window.rebornSnapshot().resources; return r.wood >= 80 && r.stone >= 60 && r.gold >= 70; })()`, 9 * 60000, 'forge affordability');
  step('forge-affordable', { waitedMs: forgeWait });
  await click('[data-choice="nav:forge"]');
  await click('[data-choice="forge-slot:weapon"]');
  const beforeForge = await snap();
  const forgeRoom = await evaluate(`(() => { const piece = document.querySelector('[data-forge-piece="weapon"]'); return { anvil: Boolean(document.querySelector('[data-forge-anvil]')), menu: document.querySelectorAll('[data-forge-menu] ~ g[data-slot]').length, piece: piece ? piece.getBoundingClientRect().height : 0, pieceOk: piece ? piece.getAttribute('href') : null }; })()`);
  check('forge-room-composed', forgeRoom.anvil && forgeRoom.menu === 6 && forgeRoom.piece > 60 && forgeRoom.piece <= 261, forgeRoom);
  await click('#choices [data-choice="forge-confirm"]');
  const forged = await snap();
  check('forge-weapon-crude', forged.inventory.length === beforeForge.inventory.length + 1 && forged.inventory.at(-1).slot === 'weapon' && forged.inventory.at(-1).quality === 0 && Math.abs((beforeForge.resources.wood - forged.resources.wood) - 80) < 2, { item: forged.inventory.at(-1), wood: [beforeForge.resources.wood, forged.resources.wood] });
  const itemId = forged.inventory.at(-1).id;
  await click(`#choices [data-choice="equip:${itemId}"]`);
  const delta = await evaluate(`document.querySelector('#forge-delta')?.textContent || ''`);
  await click(`#panel [data-choice="equip-confirm:${itemId}"]`);
  const equipped = await snap();
  check('equip-weapon-applies', equipped.hero.equip.weapon?.id === itemId && !equipped.inventory.some(i => i.id === itemId), { delta: delta.slice(0, 200), worn: equipped.hero.equip.weapon });
  await sleep(600);
  await capture('08-forge-1280');
  await click('[data-choice="nav:hero"]');
  const wornCard = await evaluate(`(() => { const node = document.querySelector('[data-hero-slot="weapon"]'); return node ? { worn: node.dataset.worn, title: node.querySelector('[data-slot-title]')?.textContent, icon: node.querySelector('[data-gear-icon]')?.getAttribute('href') || null } : null; })()`);
  check('hero-room-shows-worn-weapon', wornCard?.worn === '1' && wornCard.title && wornCard.title !== 'Empty', wornCard);
  await sleep(1200);
  await capture('09-hero-equipped-1280');

  // 8. Campaign siege with the real towers, hero and one stack; settle once; reload keeps the settlement.
  await click('[data-choice="nav:defense"]');
  // Buy whatever tower the earned gold allows (the guidance says an unprepared defense can fall).
  const towerBought = await evaluate(`(() => { const node = [...document.querySelectorAll('#choices [data-choice^="buy-tower:"]')].find(b => !b.disabled); if (!node) return null; node.click(); return node.dataset.choice; })()`);
  const preSiege = await snap();
  step('siege-preparation', { towerBought, towers: preSiege.towers.map(t => t.fam), gold: preSiege.resources.gold, army: preSiege.army.map(a => `${a.type}x${a.count}`) });
  await click('[data-choice="start-siege"]');
  await click('[data-choice="deploy-hero"]');
  await click('#choices [data-choice^="deploy-army:"]');
  const deployed = await snap();
  check('siege-deploy-free', deployed.defense?.heroDeployed && deployed.defense?.armyDeployed && near(deployed.resources.gold, preSiege.resources.gold), { gold: [preSiege.resources.gold, deployed.resources.gold] });
  await click('[data-choice="defense-speed"]');
  await sleep(800);
  await capture('10-defense-wave-1280');
  const siegeMs = await waitUntil(`(() => { const s = window.rebornSnapshot(); return Boolean(s.defense?.pendingSettlement); })()`, 8 * 60000, 'siege outcome');
  const siegeDone = await snap();
  step('siege-outcome', { ms: siegeMs, winner: siegeDone.defense.winner, cleared: siegeDone.defense.clearedWaves, waves: siegeDone.defense.waves, core: siegeDone.defense.core });
  await click('[data-choice="settle-defense"]');
  const siegeSettled = await snap();
  check('siege-settled-once', !siegeSettled.defense, { winner: siegeDone.defense.winner, goldBefore: siegeDone.resources.gold, goldAfter: siegeSettled.resources.gold, xp: [siegeDone.hero.xp, siegeSettled.hero.xp], army: siegeSettled.army.map(a => `${a.type}x${a.count}`) });
  // A loss is a legitimate settled outcome (documented in the Defense guidance); the result is recorded, not forced.
  check('siege-outcome-settled-consistently', siegeDone.defense.winner === 'p' ? siegeSettled.resources.gold > siegeDone.resources.gold || siegeSettled.hero.xp !== siegeDone.hero.xp : siegeSettled.army.length <= siegeDone.army.length, { winner: siegeDone.defense.winner, cleared: siegeDone.defense.clearedWaves, waves: siegeDone.defense.waves, armyBefore: siegeDone.army.map(a => `${a.type}x${a.count}`), armyAfter: siegeSettled.army.map(a => `${a.type}x${a.count}`), bounded: 'settlement consistency only' });
  check('siege-natural-win', siegeDone.defense.winner === 'p' && siegeDone.defense.clearedWaves === siegeDone.defense.waves && siegeDone.defense.core > 0, { winner: siegeDone.defense.winner, cleared: siegeDone.defense.clearedWaves, waves: siegeDone.defense.waves, core: siegeDone.defense.core });
  await evaluate('location.reload()');
  await sleep(1500);
  const afterReload = await snap();
  check('siege-settlement-survives-reload', !afterReload.defense && near(afterReload.resources.gold, siegeSettled.resources.gold) && afterReload.hero.xp === siegeSettled.hero.xp, { gold: afterReload.resources.gold });

  // 9. War: skirmish (practice), duel (campaign), challenge (shared seed), endless start/extension.
  await click('[data-choice="nav:war"]');
  await capture('11-war-1280');
  const campaignBefore = await snap();
  await clickText('Skirmish');
  check('skirmish-opens', (await view()) === 'tactical' && (await snap()).battle?.practice === 'skirmish', {});
  const skirmish = await autoBattle('skirmish');
  await click('[data-choice="settle-battle"]', { optional: true });
  const afterSkirmish = await snap();
  check('skirmish-does-not-touch-campaign', !afterSkirmish.battle && near(afterSkirmish.resources.gold, campaignBefore.resources.gold) && afterSkirmish.hero.xp === campaignBefore.hero.xp && afterSkirmish.inventory.length === campaignBefore.inventory.length && JSON.stringify(afterSkirmish.army) === JSON.stringify(campaignBefore.army), { skirmish, gold: afterSkirmish.resources.gold });
  await click('[data-choice="nav:war"]');
  await clickText('Tactical Duel');
  const duelOpened = await snap();
  check('duel-opens', duelOpened.battle?.practice === 'campaign' && duelOpened.battle?.id?.startsWith('duel-') && (await view()) === 'tactical', { practice: duelOpened.battle?.practice, id: duelOpened.battle?.id });
  const duel = await autoBattle('duel');
  const duelPending = await snap();
  await click('[data-choice="settle-battle"]');
  const afterDuel = await snap();
  check('duel-settles-once', !afterDuel.battle, { duel, winner: duelPending.battle?.outcome?.winner, gold: [campaignBefore.resources.gold, afterDuel.resources.gold], xp: [campaignBefore.hero.xp, afterDuel.hero.xp] });
  await click('[data-choice="nav:war"]');
  await click('[data-choice="challenge-start"]');
  check('challenge-opens', (await snap()).battle?.practice === 'challenge', {});
  const challenge = await autoBattle('challenge');
  const challengePending = await snap();
  await click('[data-choice="nav:war"]', { optional: true });
  const exportPresent = await evaluate(`Boolean(document.querySelector('[data-choice="challenge-result"]'))`);
  await click('[data-choice="nav:tactical"]');
  await click('[data-choice="settle-battle"]');
  const afterChallenge = await snap();
  check('challenge-practice-isolated', !afterChallenge.battle && near(afterChallenge.resources.gold, afterDuel.resources.gold) && afterChallenge.hero.xp === afterDuel.hero.xp && afterChallenge.inventory.length === afterDuel.inventory.length, { challenge, exportPresent, seed: challengePending.battle?.challenge?.seed });

  // 10. Story, quests, milestone, settings, slots.
  await click('[data-choice="nav:story"]');
  await clickText('Varek Iron-Eye');
  const chapterChoice = await evaluate(`(() => { const heading = [...document.querySelectorAll('#choices .choice-heading')].find(n => n.textContent === 'Chapter'); const node = heading?.nextElementSibling; if (!node || node.tagName !== 'BUTTON') return null; node.click(); return node.textContent; })()`);
  await clickText('Record milestone: Stone Age');
  const story = await snap();
  check('story-rival-chapter-milestone', story.story.rival === 'Varek Iron-Eye' && story.story.choices.length >= 1 && story.story.milestones[0], { chapterChoice, choices: story.story.choices, milestones: story.story.milestones });
  await capture('12-story-1280');
  await click('[data-choice="nav:settings"]');
  await clickText('Reduced motion off');
  await clickText('Music down');
  const settings = await snap();
  check('settings-apply', settings.settings.reducedMotion === true && settings.settings.music < 0.6, settings.settings);
  await click('[data-choice="nav:home"]');
  await click('#context');
  await clickText('Save slot 1');
  await clickText('Load slot 1');
  const slotLoaded = await snap();
  check('slot-roundtrip', slotLoaded.revision >= settings.revision && slotLoaded.settings.reducedMotion === true && slotLoaded.hero.xp === settings.hero.xp && slotLoaded.day === settings.day && JSON.stringify(slotLoaded.army) === JSON.stringify(settings.army) && slotLoaded.story.rival === settings.story.rival, { revision: [settings.revision, slotLoaded.revision], xp: [settings.hero.xp, slotLoaded.hero.xp], day: [settings.day, slotLoaded.day] });

  // 11. Endless truly extends; practice never alters the campaign.
  await click('[data-choice="nav:war"]');
  const beforeEndless = await snap();
  await click('[data-choice="start-endless"]');
  await click('[data-choice="deploy-hero"]');
  await click('#choices [data-choice^="deploy-army:"]');
  await click('[data-choice="defense-speed"]');
  const endlessStart = await snap();
  let endlessExtended = false;
  let endlessPeak = null;
  try {
    await waitUntil(`(() => { const s = window.rebornSnapshot(); return !s.defense || s.defense.waves > ${endlessStart.defense.waves} || s.defense.pendingSettlement; })()`, 4 * 60000, 'endless extension or end');
    const e = await snap();
    endlessPeak = e.defense;
    endlessExtended = Boolean(e.defense && e.defense.waves > endlessStart.defense.waves && e.defense.clearedWaves >= endlessStart.defense.waves);
    step('endless-progress', { waves: e.defense?.waves, cleared: e.defense?.clearedWaves, pending: e.defense?.pendingSettlement, winner: e.defense?.winner });
    if (e.defense?.pendingSettlement) await click('[data-choice="settle-defense"]');
  } catch (error) { step('endless-timeout', { error: String(error) }); }
  const afterEndless = await snap();
  check('endless-extends-or-ends', endlessExtended || afterEndless.defense == null || afterEndless.defense.pendingSettlement, { endlessExtended, waves: afterEndless.defense?.waves, bounded: 'historical predicate; a loss still passes this row' });
  check('endless-extends-after-initial-wave', endlessExtended, { startWaves: endlessStart.defense?.waves, cleared: endlessPeak?.clearedWaves, waves: endlessPeak?.waves });
  check('endless-practice-isolated', near(afterEndless.resources.gold, beforeEndless.resources.gold) && afterEndless.hero.xp === beforeEndless.hero.xp, { gold: [beforeEndless.resources.gold, afterEndless.resources.gold] });

  // 12. Screens at four landscape viewports plus portrait interruption.
  for (const [width, height] of [[825, 375], [933, 424], [1180, 820], [1280, 720]]) {
    await setViewport(width, height);
    for (const name of ['kingdom', 'adventure', 'hero', 'army', 'forge', 'tactical', 'defense', 'story', 'war', 'settings']) {
      await click(`[data-choice="nav:${name}"]`);
      await sleep(name === 'hero' || name === 'army' ? 700 : 150);
      const health = await screenHealth();
      report.screens.push({ width, height, name, ...health });
      if (['kingdom', 'hero', 'army', 'forge', 'adventure', 'defense'].includes(name) && (width === 825 || width === 1180)) await capture(`screen-${name}-${width}x${height}`);
    }
  }
  const before = await snap();
  await setViewport(375, 825);
  const portrait = await evaluate(`({ rotate: getComputedStyle(document.querySelector('#rotate')).display, app: getComputedStyle(document.querySelector('#app')).display })`);
  await setViewport(1280, 720);
  const afterPortrait = await snap();
  check('portrait-guidance-keeps-state', portrait.rotate === 'block' && portrait.app === 'none' && afterPortrait.day === before.day && afterPortrait.hero.xp === before.hero.xp && JSON.stringify(afterPortrait.army) === JSON.stringify(before.army) && afterPortrait.inventory.length === before.inventory.length, { ...portrait, revision: [before.revision, afterPortrait.revision] });
  const failedImages = report.screens.filter(s => s.failedImages.length);
  check('no-broken-images-any-viewport', failedImages.length === 0, failedImages.slice(0, 5));
  const smallButtons = report.screens.filter(s => s.small.length).map(s => ({ name: s.name, width: s.width, small: s.small }));
  check('meaningful-targets-48px', smallButtons.length === 0, smallButtons.slice(0, 8));
  const heroForge = report.screens.filter(s => s.name === 'hero' || s.name === 'forge');
  const heroForgeSmall = heroForge.filter(s => (s.smallControls || []).length || (s.smallTexts || []).length).map(s => ({ name: s.name, width: s.width, controls: s.smallControls, texts: s.smallTexts?.slice(0, 4) }));
  check('hero-forge-targets-and-text', heroForge.length > 0 && heroForgeSmall.length === 0, heroForgeSmall.slice(0, 6));
} catch (error) {
  report.errors.push(String(error.stack || error));
  try { await capture('error-state'); } catch { /* browser gone */ }
} finally {
  report.consoleErrors = consoleErrors;
  report.pass = report.errors.length === 0 && report.checks.every(c => c.pass) && consoleErrors.filter(e => e.kind !== 'warning').length === 0;
  report.summary = { checks: report.checks.length, passed: report.checks.filter(c => c.pass).length, failed: report.checks.filter(c => !c.pass).map(c => c.id), consoleErrors: consoleErrors.length };
  await writeFile(path.join(outDir, 'earned-journey.json'), JSON.stringify(report, null, 2));
  ws.close();
  browser.kill();
  server.kill();
  await sleep(300);
  const checkedProfile = path.resolve(profile);
  if (checkedProfile.startsWith(path.resolve(tmpdir()) + path.sep) && path.basename(checkedProfile).startsWith('aod-chrome-')) await rm(checkedProfile, { recursive: true, force: true }).catch(() => {});
}
console.log(JSON.stringify({ pass: report.pass, summary: report.summary, errors: report.errors }, null, 2));
process.exit(report.pass ? 0 : 1);
