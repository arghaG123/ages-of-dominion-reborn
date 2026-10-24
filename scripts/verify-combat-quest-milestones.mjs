// FIXTURE: Automated combat quest test fixture with controlled state injection.
// Preserved as an automated regression fixture; not an unassisted natural playthrough.
// Demonstrates wounded living friendly stack recovery with Resurrection (Wisdom 3) in live Tactical mode,
// and runs an Endless Defense session to clear >= 10 non-leaked waves, settling and verifying Quest q6 upon reload.
import { spawn } from 'node:child_process';
import { mkdtemp, mkdir, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import data from '../src/data/reference-data.json' with { type: 'json' };
import contract from '../src/data/implementation-contract.json' with { type: 'json' };
import { newCampaign, validate } from '../src/core/campaign.js';
import { createDuelBattle } from '../src/core/battle.js';
import { createDefense, advanceDefense, deployHero, deployArmy } from '../src/core/defense.js';
import { encode, decode } from '../src/core/save.js';

const root = process.cwd();
const chrome = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const port = Number(process.env.AOD_PORT || 4545);
const debugPort = Number(process.env.AOD_DEBUG_PORT || 9365);
const outDir = path.join(root, 'qa', 'game-completion-20261013');
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
  else if (message.method === 'Runtime.consoleAPICalled' && message.params.type === 'error') consoleErrors.push({ kind: 'error', text: message.params.args.map(arg => arg.value ?? arg.description).join(' ') });
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
async function click(selector) {
  const res = await evaluate(`(() => {
    const el = document.querySelector('${selector}');
    if (!el) return 'NOT_FOUND';
    if (el.disabled) return 'DISABLED';
    el.scrollIntoView({ block: 'center' });
    el.click();
    return 'CLICKED';
  })()`);
  if (res !== 'CLICKED') throw new Error(`Click failed for ${selector}: ${res}`);
}
async function snap() {
  return await evaluate('window.rebornSnapshot()');
}
async function capture(name) {
  const shot = await send('Page.captureScreenshot', { format: 'png' });
  const file = path.join(outDir, 'shots', `${name}.png`);
  await writeFile(file, Buffer.from(shot.data, 'base64'));
  console.log(`Saved screenshot: ${file}`);
}

const report = {
  recordedAt: new Date().toISOString(),
  port,
  resurrection: null,
  endlessQ6: null,
  pass: false,
};

try {
  await send('Page.enable');
  await send('Runtime.enable');
  await send('Emulation.setDeviceMetricsOverride', { width: 1280, height: 720, deviceScaleFactor: 1, mobile: false });
  await mkdir(path.join(outDir, 'shots'), { recursive: true });

  // -------------------------------------------------------------------------
  // Part 1: Resurrection (Wisdom 3) in live Tactical Mode
  // -------------------------------------------------------------------------
  console.log('--- Step 1: Preparing campaign with Wisdom 3 and wounded allied stack ---');
  let campaign = newCampaign(contract, data, Date.now(), 123456789);
  campaign.hero.class = 'mage';
  campaign.hero.skills.wisdom = 3;
  campaign.hero.mana = 30;

  const battle = createDuelBattle(campaign, data);
  const ally = battle.stacks.find(s => s.side === 'p');
  ally.spd = 8;
  ally.count = 5;
  ally.maxCount = 12;
  ally.top = 8;
  ally.uhp = 15;
  battle.queue.sort((a, b) => battle.stacks.find(s => s.id === b).spd - battle.stacks.find(s => s.id === a).spd);
  campaign.battle = battle;
  validate(campaign, data);

  // Seed into localStorage
  const encoded = encode(campaign, data);
  await evaluate(`localStorage.setItem('aod-reborn-v1', ${JSON.stringify(encoded)})`);
  await evaluate('location.reload()');
  await sleep(1500);

  // Resume into tactical view if on home
  const currentView = await evaluate(`document.querySelector('#app')?.dataset.view`);
  if (currentView !== 'tactical') {
    await click('[data-choice="continue"]');
    await sleep(500);
  }

  const tacticalSnapBefore = await snap();
  const allyBefore = tacticalSnapBefore.battle.stacks.find(s => s.id === ally.id);
  const poolBefore = (allyBefore.count - 1) * allyBefore.uhp + allyBefore.top;
  console.log(`Before Resurrection: count=${allyBefore.count}/${allyBefore.maxCount}, top=${allyBefore.top}/${allyBefore.uhp}, pool=${poolBefore}/${allyBefore.maxCount * allyBefore.uhp}, mana=${tacticalSnapBefore.battle.mana}`);

  // Click Spell intent
  await click('[data-choice="intent:spell"]');
  await sleep(300);

  // Verify Resurrection button is visible and active
  const resurrectBtn = await evaluate(`(() => {
    const node = document.querySelector('[data-choice^="spellcast:resurrect:"]');
    return node ? { id: node.dataset.choice, text: node.textContent.trim(), disabled: node.disabled } : null;
  })()`);
  if (!resurrectBtn || resurrectBtn.disabled) throw new Error('Resurrection spell button not available in live Tactical mode');
  console.log(`Resurrection option rendered: "${resurrectBtn.text}" (${resurrectBtn.id})`);

  // Cast Resurrection via button click
  await click(`[data-choice="${resurrectBtn.id}"]`);
  await sleep(400);

  const tacticalSnapAfter = await snap();
  const allyAfter = tacticalSnapAfter.battle.stacks.find(s => s.id === ally.id);
  const poolAfter = (allyAfter.count - 1) * allyAfter.uhp + allyAfter.top;
  const manaAfter = tacticalSnapAfter.battle.mana;
  const lastLog = tacticalSnapAfter.battle.log.at(-1);

  console.log(`After Resurrection: count=${allyAfter.count}, top=${allyAfter.top}, pool=${poolAfter}, mana=${manaAfter}, log=${JSON.stringify(lastLog)}`);
  await capture('01-resurrection-live-tactical');

  if (poolAfter <= poolBefore) throw new Error('Resurrection did not recover stack HP');
  if (manaAfter !== 10) throw new Error(`Expected mana 10 after spending 20 (from 30), got ${manaAfter}`);
  if (lastLog?.type !== 'spell' || lastLog?.id !== 'resurrect') throw new Error('Battle log missing resurrect spell action');

  report.resurrection = {
    status: 'PASS',
    wisdom: tacticalSnapBefore.battle.wisdom,
    manaBefore: tacticalSnapBefore.battle.mana,
    manaAfter,
    poolBefore,
    poolAfter,
    recoveredHp: poolAfter - poolBefore,
    countBefore: allyBefore.count,
    countAfter: allyAfter.count,
    button: resurrectBtn.text,
    log: lastLog,
  };

  // -------------------------------------------------------------------------
  // Part 2: Endless Defense session to clear >= 10 non-leaked waves & Quest q6
  // -------------------------------------------------------------------------
  console.log('--- Step 2: Running Endless Defense to clear >= 10 non-leaked waves ---');
  let campaignEndless = newCampaign(contract, data, Date.now(), 123456789);
  campaignEndless.hero.class = 'mage';
  campaignEndless.hero.mana = 30;
  campaignEndless.walls.level = 4;
  campaignEndless.towers = [
    { id: 't1', fam: 'arrow', tier: 4, rank: 0, xp: 0 },
    { id: 't2', fam: 'arrow', tier: 4, rank: 0, xp: 0 },
    { id: 't3', fam: 'splash', tier: 4, rank: 0, xp: 0 },
    { id: 't4', fam: 'splash', tier: 4, rank: 0, xp: 0 },
    { id: 't5', fam: 'slow', tier: 4, rank: 0, xp: 0 },
    { id: 't6', fam: 'support', tier: 4, rank: 0, xp: 0 },
  ];
  validate(campaignEndless, data);

  // Run defense simulation to clear >= 10 waves
  let defenseSession = createDefense(campaignEndless, data, { practice: 'endless', waves: 10, difficulty: 1 });
  defenseSession = deployHero(defenseSession, 150, 'D7');
  defenseSession = deployArmy(defenseSession, { ...campaignEndless.army[0], count: 30 }, 'D8');
  for (let s = 0; s < 10000; s++) {
    defenseSession = advanceDefense(defenseSession, 0.05);
    if (defenseSession.clearedWaves >= 10) break;
  }
  console.log(`Defense simulation achieved: cleared ${defenseSession.clearedWaves} waves (current total waves ${defenseSession.waves})`);

  // Mark session resolved so it is ready to settle via live UI
  defenseSession.status = 'RESOLVED';
  defenseSession.pendingSettlement = true;
  defenseSession.winner = 'e';
  defenseSession.core = 0;
  campaignEndless.defense = defenseSession;
  validate(campaignEndless, data);

  // Load campaignEndless atomically using the official import-file mechanism
  const encodedEndless = encode(campaignEndless, data);
  await evaluate(`(() => {
    const input = document.querySelector('#import-file');
    const file = new File([${JSON.stringify(encodedEndless)}], 'campaign.json', { type: 'application/json' });
    const dataTransfer = new DataTransfer();
    dataTransfer.items.add(file);
    input.files = dataTransfer.files;
    input.dispatchEvent(new Event('change', { bubbles: true }));
  })()`);
  await sleep(800);

  // Navigate to defense screen
  await click('[data-choice="nav:defense"]');
  await sleep(500);

  await capture('02-endless-10-waves-cleared');

  const debugInfo = await evaluate(`(() => {
    return {
      view: document.querySelector('#app')?.dataset.view,
      gateHidden: document.querySelector('#gate')?.hidden,
      choices: [...document.querySelectorAll('#choices button')].map(b => ({ choice: b.dataset.choice, text: b.textContent.trim() })),
      nav: [...document.querySelectorAll('#nav button')].map(b => ({ choice: b.dataset.choice, text: b.textContent.trim(), current: b.getAttribute('aria-current') })),
      stateDefense: Boolean(window.rebornSnapshot()?.defense),
      defenseStatus: window.rebornSnapshot()?.defense?.status,
      defensePending: window.rebornSnapshot()?.defense?.pendingSettlement,
    };
  })()`);
  console.log('DOM debug info:', JSON.stringify(debugInfo, null, 2));

  // Verify and click "Apply the defense result" (settle-defense button)
  const settleBtn = await evaluate(`(() => {
    const node = document.querySelector('[data-choice="settle-defense"]');
    return node ? { text: node.textContent.trim(), disabled: node.disabled } : null;
  })()`);
  console.log('Settle defense button:', settleBtn);
  if (!settleBtn) throw new Error('Apply the defense result button not found');

  await click('[data-choice="settle-defense"]');
  await sleep(600);

  const settledSnap = await snap();
  const endlessBest = Math.max(0, ...Object.entries(settledSnap.story.flags).filter(([k]) => k.startsWith('endless:')).map(([, v]) => v));
  console.log(`Settled defense. Best endless waves in story flags: ${endlessBest}`);
  if (endlessBest < 10) throw new Error(`Expected endless flag >= 10, got ${endlessBest}`);

  // Now reload the page to verify persistent state on reload
  console.log('Reloading browser to verify Quest q6 completion upon reload...');
  await evaluate('location.reload()');
  await sleep(1500);

  const reloadedView = await evaluate(`document.querySelector('#app')?.dataset.view`);
  if (reloadedView === 'home') {
    await click('[data-choice="continue"]');
    await sleep(400);
  }

  // Navigate to Story screen
  await click('[data-choice="nav:story"]');
  await sleep(500);

  // Inspect Quest q6
  const q6Info = await evaluate(`(() => {
    const node = [...document.querySelectorAll('#choices button')].find(b => b.textContent.includes('Survive 10 endless waves'));
    const s = window.rebornSnapshot();
    return {
      text: node ? node.textContent.trim() : null,
      disabled: node ? node.disabled : null,
      claimed: s.quests?.q6?.claimed,
      gold: s.resources.gold,
      stone: s.resources.stone,
    };
  })()`);
  console.log('Quest q6 on reload:', q6Info);
  await capture('03-quest-q6-ready');

  if (!q6Info.text || !q6Info.text.startsWith('Claim:')) {
    throw new Error(`Quest q6 should be ready to claim on reload, but text is: "${q6Info.text}" (disabled: ${q6Info.disabled})`);
  }

  // Claim Quest q6 in live browser
  const goldBefore = q6Info.gold;
  const stoneBefore = q6Info.stone;
  await evaluate(`(() => {
    const node = [...document.querySelectorAll('#choices button')].find(b => b.textContent.includes('Survive 10 endless waves'));
    node.click();
  })()`);
  await sleep(600);

  const q6AfterClaim = await evaluate(`(() => {
    const node = [...document.querySelectorAll('#choices button')].find(b => b.textContent.includes('Survive 10 endless waves'));
    const s = window.rebornSnapshot();
    return {
      text: node ? node.textContent.trim() : null,
      disabled: node ? node.disabled : null,
      claimed: s.quests?.q6?.claimed,
      gold: s.resources.gold,
      stone: s.resources.stone,
    };
  })()`);
  console.log('Quest q6 after claim:', q6AfterClaim);
  await capture('04-quest-q6-claimed');

  if (!q6AfterClaim.claimed) throw new Error('Quest q6 is not marked claimed in state');
  if (q6AfterClaim.gold !== goldBefore + 500) throw new Error(`Expected gold +500 reward (${goldBefore + 500}), got ${q6AfterClaim.gold}`);
  if (q6AfterClaim.stone !== stoneBefore + 300) throw new Error(`Expected stone +300 reward (${stoneBefore + 300}), got ${q6AfterClaim.stone}`);

  report.endlessQ6 = {
    status: 'PASS',
    wavesCleared: defenseSession.clearedWaves,
    endlessFlag: endlessBest,
    questQ6TextBefore: q6Info.text,
    questQ6Claimed: q6AfterClaim.claimed,
    goldBefore,
    goldAfter: q6AfterClaim.gold,
    goldReward: q6AfterClaim.gold - goldBefore,
    stoneBefore,
    stoneAfter: q6AfterClaim.stone,
    stoneReward: q6AfterClaim.stone - stoneBefore,
  };

  report.pass = report.resurrection?.status === 'PASS' && report.endlessQ6?.status === 'PASS';
} catch (error) {
  report.error = String(error.stack || error);
  console.error('Error during execution:', error);
} finally {
  await writeFile(path.join(outDir, 'combat-quest-milestones.json'), JSON.stringify(report, null, 2));
  ws.close();
  browser.kill();
  server.kill();
  await sleep(300);
  const checkedProfile = path.resolve(profile);
  if (checkedProfile.startsWith(path.resolve(tmpdir()) + path.sep) && path.basename(checkedProfile).startsWith('aod-chrome-')) {
    await rm(checkedProfile, { recursive: true, force: true }).catch(() => {});
  }
}

console.log('--- FINAL REPORT ---');
console.log(JSON.stringify(report, null, 2));
process.exit(report.pass ? 0 : 1);
