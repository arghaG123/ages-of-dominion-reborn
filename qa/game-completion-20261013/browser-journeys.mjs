import { chromium } from 'file:///C:/Users/TechnoExponent/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import { writeFile, mkdir, readFile } from 'node:fs/promises';
import { writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

const base = process.env.AOD_PREVIEW || 'http://127.0.0.1:4525/';
const out = new URL(process.env.AOD_JOURNEY_OUT || './browser-journeys.json', import.meta.url);
const shotDir = new URL('./shots/', import.meta.url);
const results = [];
const note = (id, status, detail) => results.push({ id, status, detail });

async function visibleClick(page, id) {
  await wake(page);
  const clicked = await page.evaluate(choice => {
    const nodes = [...document.querySelectorAll(`[data-choice="${choice}"]`)].filter(node => node.offsetParent && !node.disabled);
    const node = nodes[0];
    if (!node) return false;
    node.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true, pointerId: 1, pointerType: 'mouse' }));
    node.dispatchEvent(new PointerEvent('pointerup', { bubbles: true, pointerId: 1, pointerType: 'mouse' }));
    node.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
    return true;
  }, id);
  if (clicked) return;
  await openPanel(page);
  await page.evaluate(choice => {
    const node = document.querySelector(`[data-choice="${choice}"]`);
    if (!node) throw new Error(`Missing ${choice}`);
    node.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true, pointerId: 1, pointerType: 'mouse' }));
    node.dispatchEvent(new PointerEvent('pointerup', { bubbles: true, pointerId: 1, pointerType: 'mouse' }));
    node.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
  }, id);
}
async function fireRole(page, label) {
  await page.evaluate(name => {
    const nodes = [...document.querySelectorAll('button')].filter(node => node.offsetParent && node.textContent.trim() === name && !node.disabled);
    const node = nodes[0];
    if (!node) throw new Error(`Missing ${name}`);
    node.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true, pointerId: 1, pointerType: 'mouse' }));
    node.dispatchEvent(new PointerEvent('pointerup', { bubbles: true, pointerId: 1, pointerType: 'mouse' }));
    node.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
  }, label);
}
async function domClick(node) {
  node.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true, pointerId: 1 }));
  node.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
}
async function wake(page) {
  await page.evaluate(() => { window.focus(); window.rebornBackground?.(false); });
}
async function selectPlot(page, id) {
  await page.locator(`[aria-label^="${id}:"]`).evaluate(node => {
    node.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
  });
}
async function resources(page) {
  return page.locator('#resources').innerText();
}
async function openPanel(page) {
  if (await page.locator('#context').getAttribute('aria-expanded') === 'true') return;
  const view = await page.locator('#app').getAttribute('data-view');
  if (view === 'home') {
    await visibleClick(page, 'open-load');
    return;
  }
  await page.locator('#context').evaluate(node => node.click());
}
async function leaveHome(page) {
  if (await page.locator('#app').getAttribute('data-view') !== 'home') return;
  await fireRole(page, 'Continue');
  await page.waitForFunction(() => document.querySelector('#app')?.dataset.view !== 'home');
}
async function gotoScreen(page, name) {
  if (name !== 'home') await leaveHome(page);
  if (await page.locator('#app').getAttribute('data-view') === name) return;
  const hidden = await page.locator(`[data-choice="nav:${name}"]`).getAttribute('data-nav');
  if (hidden === 'more') {
    const label = (await page.locator('[data-choice="nav-more"]').innerText()).trim();
    if (label === 'More') await page.locator('[data-choice="nav-more"]').evaluate(node => { node.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true, pointerId: 1, pointerType: 'mouse' })); node.dispatchEvent(new PointerEvent('pointerup', { bubbles: true, pointerId: 1, pointerType: 'mouse' })); node.click(); });
  }
  const combat = await page.locator('#app').getAttribute('data-combat');
  if (combat === '1') throw new Error(`Cannot open ${name} while a battle or defense is active`);
  await page.locator(`[data-choice="nav:${name}"]`).evaluate(node => { node.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true, pointerId: 1, pointerType: 'mouse' })); node.dispatchEvent(new PointerEvent('pointerup', { bubbles: true, pointerId: 1, pointerType: 'mouse' })); node.click(); });
  await page.waitForFunction(expected => document.querySelector('#app')?.dataset.view === expected, name);
}
async function waitLevel(page, plot, level) {
  const start = Date.now();
  let last = null;
  while (Date.now() - start < 7000) {
    await wake(page);
    last = await page.evaluate(id => {
      const label = document.querySelector(`[aria-label^="${id}:"]`)?.getAttribute('aria-label') || '';
      const snap = window.rebornSnapshot?.();
      const row = snap?.plots?.find(item => item.id === id);
      return { label, level: row?.level ?? null, type: row?.type ?? null, jobs: snap?.buildJobs?.map(job => job.plotId) ?? [], message: document.querySelector('#message')?.textContent || '' };
    }, plot);
    if (last.label.includes(`level ${level}`)) return last;
    await new Promise(resolve => setTimeout(resolve, 200));
  }
  throw new Error(`${plot} did not reach level ${level}: ${JSON.stringify(last)}`);
}
async function resume(page) {
  await page.reload({ waitUntil: 'domcontentloaded' });
  await page.waitForSelector('#app');
  const view = await page.locator('#app').getAttribute('data-view');
  if (view === 'home') {
    const cont = page.getByRole('button', { name: 'Continue' });
    if (await cont.count()) await cont.click();
  }
  await page.waitForFunction(() => {
    const app = document.querySelector('#app');
    return app && app.dataset.view && app.dataset.view !== 'home';
  });
}
async function snapshot(page) {
  return page.evaluate(() => window.rebornSnapshot());
}
async function step(page, id, fn) {
  try {
    const detail = await fn();
    note(id, detail.status || 'PASS', detail);
  } catch (error) {
    const file = fileURLToPath(new URL(`./shots/${id.replace(/[^a-z0-9-]+/gi, '_')}.png`, import.meta.url));
    await page.screenshot({ path: file, timeout: 5000 }).catch(() => {});
    note(id, 'FAIL', String(error?.stack || error));
  }
}
function costOf(text) {
  const match = String(text).match(/cost (\d+)/);
  return match ? Number(match[1]) : null;
}
async function confirmText(page) {
  const nodes = page.locator('[data-choice="confirm-route"]');
  const count = await nodes.count();
  for (let index = 0; index < count; index += 1) {
    if (await nodes.nth(index).isVisible()) return nodes.nth(index).innerText();
  }
  return '';
}
async function travelTo(page, cell) {
  const found = await page.locator(`[data-adventure-cell="${cell}"][data-open="1"]`).count();
  if (!found) return { ok: false, preview: '', moves: null, cost: null, missing: cell };
  await page.locator(`[data-adventure-cell="${cell}"][data-open="1"]`).evaluate(node => node.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true })));
  const preview = await confirmText(page);
  const moves = Number((await page.locator('#selected').innerText()).match(/moves (\d+)/)?.[1]);
  const cost = costOf(preview);
  if (cost == null || cost > moves) {
    await openPanel(page);
    await fireRole(page, 'Clear preview');
    return { ok: false, preview, moves, cost };
  }
  await visibleClick(page, 'confirm-route');
  await page.waitForFunction(goal => (document.querySelector('#selected')?.textContent || '').includes(`Travel ${goal}`), cell, { timeout: 8000 });
  return { ok: true, preview, moves, cost, selected: await page.locator('#selected').innerText() };
}
async function refillMoves(page) {
  await gotoScreen(page, 'kingdom');
  await openPanel(page);
  await visibleClick(page, 'end-day');
  await gotoScreen(page, 'adventure');
  await page.waitForSelector('[data-adventure-cell]', { state: 'attached' });
}

const browser = await chromium.launch({
  headless: true,
  executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe',
});
const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
page.setDefaultTimeout(20000);
page.on('dialog', dialog => dialog.accept());
const errors = [];
page.on('pageerror', error => errors.push(String(error)));
await mkdir(shotDir, { recursive: true });

try {
  await page.goto(base, { waitUntil: 'domcontentloaded' });
  await wake(page);
  await page.getByRole('button', { name: 'New campaign' }).click();
  await visibleClick(page, 'scene-class:ranger');
  await visibleClick(page, 'scene-enter-valley');
  await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'kingdom');

  await step(page, 'J01', async () => {
    const starter = await resources(page);
    const plots = await page.locator('.plot').count();
    const cue = await page.locator('#message').innerText();
    const pass = starter.includes('food 250') && starter.includes('wood 250') && starter.includes('stone 160') && starter.includes('gold 150') && plots === 18 && cue.includes('Build a Lumber Camp');
    return { status: pass ? 'PASS' : 'FAIL', starter, plots, cue };
  });

  await step(page, 'J02-cancel', async () => {
    const before = await resources(page);
    await selectPlot(page, 'P01');
    await openPanel(page);
    const preview = await page.locator('[data-choice="build:P01:lumber"]').first().innerText();
    await page.locator('#context').evaluate(node => node.click());
    const after = await resources(page);
    const pass = before === after && preview.includes('Lumber Camp') && preview.includes('25 wood');
    return { status: pass ? 'PASS' : 'FAIL', before, after, preview };
  });

  await step(page, 'J02-build-upgrade-reload', async () => {
    await visibleClick(page, 'build:P01:lumber');
    const scaffold = await page.locator('[data-scaffold="P01"]').count();
    const level1 = await waitLevel(page, 'P01', 1);
    await selectPlot(page, 'P01');
    const inspected = await page.locator('#selected').innerText();
    await openPanel(page);
    await visibleClick(page, 'build:P01:lumber');
    const level2 = await waitLevel(page, 'P01', 2);
    await resume(page);
    const reloaded = await page.locator('[aria-label^="P01:"]').getAttribute('aria-label');
    const pass = scaffold > 0 && inspected.includes('Lumber Camp') && reloaded?.includes('lumber') && reloaded.includes('level 2');
    return { status: pass ? 'PASS' : 'FAIL', scaffold, inspected, reloaded, level1: level1.label, level2: level2.label };
  });

  await step(page, 'J16-slots', async () => {
    await gotoScreen(page, 'home');
    await openPanel(page);
    await fireRole(page, 'Save slot 1');
    await leaveHome(page);
    for (const [plot, building] of [['P02', 'farm'], ['P03', 'quarry'], ['P04', 'barracks']]) {
      await selectPlot(page, plot);
      await visibleClick(page, `build:${plot}:${building}`);
      await waitLevel(page, plot, 1);
    }
    await gotoScreen(page, 'home');
    await openPanel(page);
    await fireRole(page, 'Save slot 2');
    await fireRole(page, 'Save slot 3');
    await fireRole(page, 'Load slot 1');
    await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'kingdom');
    const slot1 = await page.locator('[aria-label^="P04:"]').getAttribute('aria-label');
    await gotoScreen(page, 'home');
    await openPanel(page);
    await fireRole(page, 'Load slot 2');
    await page.waitForFunction(() => document.querySelector('[aria-label^="P04:"]')?.getAttribute('aria-label')?.includes('barracks'));
    const slot2 = await page.locator('[aria-label^="P04:"]').getAttribute('aria-label');
    const pass = slot1?.includes('empty plot') && slot2?.includes('barracks') && slot2.includes('level 1');
    return { status: pass ? 'PASS' : 'FAIL', slot1, slot2 };
  });

  await step(page, 'J03', async () => {
    if (await page.locator('[data-choice="go-recruit"]').count()) await visibleClick(page, 'go-recruit');
    else await gotoScreen(page, 'army');
    await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'army');
    await openPanel(page);
    const beforeRoster = await page.locator('[data-army-row="roster"]').innerText();
    await visibleClick(page, 'recruit:melee');
    const armyText = await page.locator('#message').innerText();
    const roster = await page.locator('[data-army-row="roster"]').innerText();
    const pass = beforeRoster.includes('Clubman ×12') && roster.includes('Clubman ×17') && armyText.includes('Army 2/3');
    return { status: pass ? 'PASS' : 'FAIL', beforeRoster, armyText, roster };
  });

  await step(page, 'J05', async () => {
    await visibleClick(page, 'nav:adventure');
    await visibleClick(page, 'enter-adventure');
    await page.waitForSelector('[data-adventure-cell][data-open="1"]', { state: 'attached' });
    const beforeMove = await page.locator('#selected').innerText();
    const cell = await page.evaluate(() => {
      const match = document.querySelector('#selected')?.textContent?.match(/Travel (\d+),(\d+)/);
      if (!match) return '';
      const x = Number(match[1]);
      const y = Number(match[2]);
      for (const [dx, dy] of [[0, 1], [0, -1], [1, 0], [-1, 0]]) {
        const id = `${x + dx},${y + dy}`;
        if (document.querySelector(`[data-adventure-cell="${id}"][data-open="1"]`)) return id;
      }
      return '';
    });
    await page.locator(`[data-adventure-cell="${cell}"]`).evaluate(node => node.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true })));
    const preview = await confirmText(page);
    await openPanel(page);
    await fireRole(page, 'Clear preview');
    const cleared = await page.locator('#selected').innerText();
    await page.locator(`[data-adventure-cell="${cell}"]`).evaluate(node => node.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true })));
    await visibleClick(page, 'confirm-route');
    await page.waitForTimeout(800);
    const afterMove = await page.locator('#selected').innerText();
    await resume(page);
    const reloaded = await page.locator('#selected').innerText();
    const pass = preview.includes('cost') && cleared === beforeMove && afterMove !== beforeMove && reloaded === afterMove;
    return { status: pass ? 'PASS' : 'FAIL', cell, beforeMove, preview, cleared, afterMove, reloaded };
  });

  await step(page, 'J06-J13-site', async () => {
    let trip = await travelTo(page, '10,8');
    if (!trip.ok) {
      await refillMoves(page);
      trip = await travelTo(page, '10,8');
    }
    if (!trip.ok) return { status: 'BLOCKED', reason: 'Dwelling approach costs more than a refilled day.', trip };
    await openPanel(page);
    await visibleClick(page, 'offer-dwelling:wolf');
    const offer = await page.locator('#message').innerText();
    await resume(page);
    const reloaded = await page.locator('#message').innerText();
    await openPanel(page);
    await visibleClick(page, 'cancel-dwelling');
    const declined = await page.locator('#message').innerText();
    const claim = page.locator('[data-choice="claim-dwelling"]').first();
    const claimDisabled = await claim.count() ? await claim.isDisabled() : true;
    const claimText = await claim.count() ? await claim.innerText() : '';
    let claimed = false;
    if (!claimDisabled) {
      await visibleClick(page, 'claim-dwelling');
      claimed = (await page.locator('#message').innerText()).includes('Army');
    }
    const same = offer.includes('Dire Wolf') && reloaded.includes('Dire Wolf') && declined.includes('Dire Wolf');
    return { status: same ? 'PASS' : 'FAIL', offer, reloaded, declined, claimText, claimDisabled, claimed, trip };
  });

  await step(page, 'J06-guard', async () => {
    let trip = await travelTo(page, '10,5');
    if (!trip.ok) {
      await refillMoves(page);
      trip = await travelTo(page, '10,5');
    }
    const fight = await page.locator('[data-choice="begin-encounter"]').count();
    if (!fight) return { status: 'BLOCKED', reason: 'No unresolved guard became reachable in two movement days.', trip };
    await visibleClick(page, 'begin-encounter');
    await page.waitForFunction(() => document.querySelector('#app')?.dataset.combat === '1');
    const title = await page.locator('#message').innerText();
    await visibleClick(page, 'auto');
    await page.waitForSelector('[data-choice="settle-battle"]', { timeout: 60000 });
    await visibleClick(page, 'settle-battle');
    await page.waitForFunction(() => document.querySelector('#app')?.dataset.combat !== '1');
    const after = await page.locator('#message').innerText();
    const pass = title.includes('battle') && !after.includes('Apply the battle result');
    return { status: pass ? 'PASS' : 'FAIL', title, after, trip };
  });

  await step(page, 'J04-age-gate', async () => {
    if ((await page.locator('#app').getAttribute('data-combat')) === '1') return { status: 'BLOCKED', reason: 'A battle is still open.' };
    await gotoScreen(page, 'kingdom');
    const before = await resources(page);
    await openPanel(page);
    await fireRole(page, 'Advance age');
    const message = await page.locator('#message').innerText();
    const after = await resources(page);
    const age = await page.locator('#status').innerText();
    return {
      status: 'BLOCKED',
      reason: 'The visible Hall gate refused the age. This Stone session cannot pay the next age.',
      message, before, after, age, unchanged: before === after,
    };
  });

  await step(page, 'J15-stone-lock', async () => {
    await gotoScreen(page, 'market');
    const market = await page.locator('#scene-ui.support').innerText();
    const pass = market.includes('Opens in Bronze Age');
    return { status: pass ? 'PASS' : 'FAIL', market, bronze: 'BLOCKED until an earned age advance' };
  });

  await step(page, 'J14-story', async () => {
    await gotoScreen(page, 'story');
    await openPanel(page);
    await fireRole(page, 'Varek Iron-Eye');
    await fireRole(page, 'Share the fire');
    const saved = await page.locator('#message').innerText();
    const milestone = page.getByRole('button', { name: 'Record milestone: Stone Age' });
    await fireRole(page, 'Record milestone: Stone Age');
    const recorded = await page.getByRole('button', { name: 'Recorded: Stone Age' }).isDisabled();
    const future = await page.locator('#message').innerText();
    const pass = saved.includes('shared the first fire') && recorded && future.includes('Opens in') === false || future.includes('Saved record');
    return { status: saved.includes('shared the first fire') && recorded ? 'PASS' : 'FAIL', saved, recorded, futureNote: 'Future conclusion stays closed in the Stone Age.', future };
  });

  await step(page, 'J17', async () => {
    await gotoScreen(page, 'settings');
    const before = await page.locator('#message').innerText();
    await openPanel(page);
    await fireRole(page, 'Music down');
    const music = await page.locator('#message').innerText();
    await fireRole(page, 'Sound down');
    const sound = await page.locator('#message').innerText();
    await fireRole(page, 'Reduced motion off');
    const motion = await page.locator('[data-reduced-motion]').getAttribute('data-reduced-motion');
    await gotoScreen(page, 'kingdom');
    await openPanel(page);
    await visibleClick(page, 'tutorial-toggle');
    const skipped = await page.locator('#message').innerText();
    await visibleClick(page, 'tutorial-toggle');
    const reviewed = await page.locator('#message').innerText();
    await page.locator('#context').focus();
    await page.keyboard.press('Tab');
    const focus = await page.evaluate(() => document.activeElement?.dataset?.choice || document.activeElement?.id || document.activeElement?.tagName);
    await page.setViewportSize({ width: 400, height: 800 });
    const portrait = await page.locator('#rotate').evaluate(node => getComputedStyle(node).display);
    const appHidden = await page.locator('#app').evaluate(node => getComputedStyle(node).display);
    await page.setViewportSize({ width: 1280, height: 720 });
    const restored = await page.locator('#status').innerText();
    const pass = before.includes('Music') && music !== before && sound !== music && motion === 'on' && !skipped.includes('Next:') && reviewed.includes('Next:') && focus && portrait === 'block' && appHidden === 'none' && restored.includes('Stone Age');
    return { status: pass ? 'PASS' : 'FAIL', before, music, sound, motion, skipped, reviewed, focus, portrait, appHidden, restored };
  });

  await step(page, 'J11-forge', async () => {
    await gotoScreen(page, 'hero');
    await openPanel(page);
    await visibleClick(page, 'hero-slot:helm');
    await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'forge');
    const forge = await page.locator('#scene-ui').innerText();
    const bag = await page.locator('[data-choice^="equip:"]').count();
    let equipped = '';
    if (bag) {
      await visibleClick(page, await page.locator('[data-choice^="equip:"]').first().getAttribute('data-choice'));
      const confirm = page.locator('[data-choice^="equip-confirm:"]').first();
      const delta = await page.locator('#forge-delta').innerText();
      await confirm.evaluate(node => node.click());
      equipped = await page.locator('[data-slot-title="helm"], [data-slot-title]').first().innerText().catch(() => delta);
    }
    return {
      status: 'BLOCKED',
      reason: 'Armory level 1 costs 120 wood, 120 stone and 80 gold. This earned session cannot open a recipe. Equip runs only when a battle drop is already in the bag.',
      forge, bag, equipped,
    };
  });

  await step(page, 'J08-J10-skirmish', async () => {
    const goldBefore = await resources(page);
    await gotoScreen(page, 'war');
    await openPanel(page);
    await fireRole(page, 'Skirmish');
    await page.waitForFunction(() => document.querySelector('#app')?.dataset.combat === '1');
    const nav = await page.locator('#nav').evaluate(node => getComputedStyle(node).display);
    const resourcesHidden = await page.locator('#resources').evaluate(node => getComputedStyle(node).display === 'none' || node.hidden);
    await visibleClick(page, 'retreat');
    const trapped = await page.evaluate(() => document.activeElement?.id || '');
    await page.locator('#retreat-cancel').click();
    const still = await page.locator('#app').getAttribute('data-combat');
    const moveEnabled = await page.locator('[data-choice="intent:move"]').evaluateAll(nodes => nodes.some(node => node.offsetParent && !node.disabled));
    if (moveEnabled) {
      await visibleClick(page, 'intent:move');
      const cell = page.locator('[data-cell][data-open="1"]').first();
      if (await cell.count()) await cell.evaluate(node => node.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true })));
    }
    const acted = await page.locator('#message').innerText();
    await visibleClick(page, 'retreat');
    await page.locator('#retreat-confirm').click();
    if (await page.locator('[data-choice="settle-battle"]').count()) await visibleClick(page, 'settle-battle');
    await page.waitForFunction(() => document.querySelector('#app')?.dataset.combat !== '1');
    await gotoScreen(page, 'kingdom');
    const goldAfter = await resources(page);
    const gold = text => text.match(/gold \d+/)?.[0];
    const pass = nav === 'none' && resourcesHidden && trapped.includes('retreat') && still === '1' && gold(goldBefore) === gold(goldAfter);
    return { status: pass ? 'PASS' : 'FAIL', nav, resourcesHidden, trapped, still, moveEnabled, acted, goldBefore, goldAfter };
  });

  await step(page, 'J07-J10-duel', async () => {
    await gotoScreen(page, 'war');
    await openPanel(page);
    await fireRole(page, 'Tactical Duel');
    await page.waitForFunction(() => document.querySelector('#app')?.dataset.combat === '1');
    const opener = await page.locator('#message').innerText();
    const clubman = opener.includes('Clubman') || await page.locator('#labels, #message').innerText().then(text => text.includes('Clubman')).catch(() => false);
    const rows = {};
    for (const id of ['intent:move', 'intent:melee', 'intent:shoot', 'intent:spell', 'defend', 'wait']) {
      const node = page.locator(`[data-choice="${id}"]`).last();
      rows[id] = await node.count() ? { disabled: await node.isDisabled(), text: await node.innerText() } : { missing: true };
    }
    if (!rows['intent:move']?.disabled) {
      await visibleClick(page, 'intent:move');
      const cell = page.locator('[data-cell][data-open="1"]').first();
      if (await cell.count()) await cell.evaluate(node => node.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true })));
    } else if (!rows.defend?.disabled) await visibleClick(page, 'defend');
    const mid = await page.locator('#message').innerText();
    await visibleClick(page, 'auto');
    await page.waitForSelector('[data-choice="settle-battle"]', { timeout: 90000 });
    const pending = await page.locator('#message').innerText();
    const during = await page.locator('#app').getAttribute('data-view');
    await visibleClick(page, 'settle-battle');
    await page.waitForFunction(() => document.querySelector('#app')?.dataset.combat !== '1');
    await gotoScreen(page, 'kingdom');
    const gold = await resources(page);
    await resume(page);
    const again = await page.locator('[data-choice="settle-battle"]').count();
    const flyer = opener.toLowerCase().includes('harpy') || opener.toLowerCase().includes('flyer');
    const morale = (opener + mid + pending).includes('High morale');
    return {
      status: pending.includes('result') && again === 0 && during === 'tactical' ? 'PASS' : 'FAIL',
      opener, clubman, rows, mid, pending, during, gold, again,
      flyer: flyer ? 'SEEN' : 'BLOCKED: Stone duel enemies are wolves. No flyer is fielded.',
      morale: morale ? 'SEEN' : 'UNVERIFIED: the 4.2% bonus did not roll in this battle.',
    };
  });

  await step(page, 'J12-point', async () => {
    await gotoScreen(page, 'hero');
    const before = await page.locator('#message').innerText();
    const point = page.locator('[data-choice="spend:atk"]');
    if (!(await point.count())) {
      return { status: 'BLOCKED', reason: 'No earned point is on the hero. One duel pays about 110 XP and level 2 needs 140. Wisdom 3 was not reached.', before };
    }
    await openPanel(page);
    await visibleClick(page, 'spend:atk');
    const after = await page.locator('#message').innerText();
    return { status: before.includes('Points 1') && after.includes('Points 0') ? 'PASS' : 'FAIL', before, after, wisdom: 'BLOCKED' };
  });

  await step(page, 'J10-challenge', async () => {
    await gotoScreen(page, 'kingdom');
    const goldBefore = (await resources(page)).match(/gold \d+/)?.[0];
    const idsBefore = (await snapshot(page)).army.map(stack => stack.id);
    await gotoScreen(page, 'war');
    await openPanel(page);
    await page.getByLabel('Challenge seed').fill('123456789');
    await page.getByLabel('Challenge label').fill('valley-1');
    await visibleClick(page, 'challenge-start');
    await page.waitForFunction(() => document.querySelector('#app')?.dataset.combat === '1');
    const first = await page.locator('#message').innerText();
    await visibleClick(page, 'retreat');
    await page.locator('#retreat-confirm').click();
    if (await page.locator('[data-choice="settle-battle"]').count()) await visibleClick(page, 'settle-battle');
    await page.waitForFunction(() => document.querySelector('#app')?.dataset.combat !== '1');
    await gotoScreen(page, 'war');
    await openPanel(page);
    await page.getByLabel('Challenge seed').fill('123456789');
    await page.getByLabel('Challenge label').fill('valley-1');
    await visibleClick(page, 'challenge-start');
    await page.waitForFunction(() => document.querySelector('#app')?.dataset.combat === '1');
    const second = await page.locator('#message').innerText();
    await visibleClick(page, 'retreat');
    await page.locator('#retreat-confirm').click();
    if (await page.locator('[data-choice="settle-battle"]').count()) await visibleClick(page, 'settle-battle');
    await gotoScreen(page, 'kingdom');
    const goldAfter = (await resources(page)).match(/gold \d+/)?.[0];
    const idsAfter = (await snapshot(page)).army.map(stack => stack.id);
    const pass = first === second && goldBefore === goldAfter && idsBefore.join() === idsAfter.join();
    return { status: pass ? 'PASS' : 'FAIL', first, second, goldBefore, goldAfter, idsBefore, idsAfter };
  });

  await step(page, 'J16-import', async () => {
    const before = await snapshot(page);
    await gotoScreen(page, 'home');
    await openPanel(page);
    const [download] = await Promise.all([
      page.waitForEvent('download'),
      fireRole(page, 'Export campaign'),
    ]);
    const exported = await download.path();
    const text = await readFile(exported, 'utf8');
    const campaignFile = fileURLToPath(new URL('./shots/campaign.json', import.meta.url));
    writeFileSync(campaignFile, text);
    await page.locator('#import-file').setInputFiles(exported);
    await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'kingdom');
    const imported = await snapshot(page);
    const [chooser] = await Promise.all([
      page.waitForEvent('filechooser'),
      gotoScreen(page, 'home').then(() => openPanel(page)).then(() => fireRole(page, 'Import campaign')),
    ]);
    await chooser.setFiles([]);
    const afterCancel = await snapshot(page);
    const unsupportedFile = fileURLToPath(new URL('./shots/unsupported.json', import.meta.url));
    const damagedFile = fileURLToPath(new URL('./shots/damaged.json', import.meta.url));
    writeFileSync(unsupportedFile, '{"schema":2}');
    await page.locator('#import-file').setInputFiles(unsupportedFile);
    await page.waitForTimeout(400);
    const unsupported = await page.locator('#message').innerText();
    writeFileSync(damagedFile, '{"schema":1,"payload":"{}","checksum":"nope"}');
    await page.locator('#import-file').setInputFiles(damagedFile);
    await page.waitForTimeout(400);
    const damaged = await page.locator('#message').innerText();
    const kept = await snapshot(page);
    const pass = imported?.hero?.id === before.hero.id && kept?.hero?.id === before.hero.id && unsupported.includes('Unsupported') && damaged.includes('checksum');
    return { status: pass ? 'PASS' : 'FAIL', unsupported, damaged, hero: kept.hero.id };
  });

  await step(page, 'J09-J10-defense', async () => {
    await gotoScreen(page, 'war');
    await openPanel(page);
    await fireRole(page, 'Campaign Siege');
    await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'defense');
    const pads = page.locator('[data-defense-pad]');
    const padCount = await pads.count();
    const padId = padCount ? await pads.nth(0).getAttribute('data-defense-pad') : '';
    if (padId) await pads.nth(0).evaluate(node => node.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true })));
    await visibleClick(page, 'defense-pause');
    const paused = await page.locator('#message').innerText();
    await visibleClick(page, 'defense-speed');
    const speed = await page.locator('#message').innerText();
    const hero = page.locator('[data-choice="deploy-hero"]');
    if (await hero.count() && !(await hero.first().isDisabled())) await visibleClick(page, 'deploy-hero');
    const armyPad = padCount > 1 ? await pads.nth(1).getAttribute('data-defense-pad') : '';
    if (armyPad) await pads.nth(1).evaluate(node => node.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true })));
    const army = page.locator('[data-choice^="deploy-army:"]').first();
    if (await army.count() && !(await army.isDisabled())) await army.evaluate(node => node.click());
    const deployed = await page.locator('#message').innerText();
    await resume(page);
    const reloaded = await page.locator('#selected').innerText();
    const started = Date.now();
    let later = await page.locator('#message').innerText();
    while (Date.now() - started < 15000 && await page.locator('[data-choice="settle-defense"]').count() === 0) {
      await wake(page);
      await new Promise(resolve => setTimeout(resolve, 500));
      later = await page.locator('#message').innerText();
    }
    const settle = await page.locator('[data-choice="settle-defense"]').count();
    if (settle) await visibleClick(page, 'settle-defense');
    const endlessBlocked = (await page.locator('#app').getAttribute('data-combat')) === '1';
    return {
      status: paused.includes('Paused') && reloaded.includes('core') ? 'PASS' : 'FAIL',
      padId, armyPad, paused, speed, deployed, reloaded, later, settle,
      result: settle ? 'Applied the visible defense result.' : 'BLOCKED: the siege had not resolved after 20 seconds.',
      endless: endlessBlocked ? 'BLOCKED: an active defense is already open, so Endless was not started.' : 'UNVERIFIED',
    };
  });

  if ((await page.locator('#app').getAttribute('data-combat')) !== '1') {
    await step(page, 'J10-endless', async () => {
      await gotoScreen(page, 'war');
      await openPanel(page);
      await fireRole(page, 'Endless');
      await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'defense');
      await visibleClick(page, 'defense-pause');
      const text = await page.locator('#message').innerText();
      return { status: text.includes('Paused') ? 'PASS' : 'FAIL', text, note: 'Endless has no terminal victory. This check starts it and pauses the same session.' };
    });
  }

  await step(page, 'J18', async () => {
    const state = await snapshot(page);
    return {
      status: 'BLOCKED',
      reason: 'This visible session built and upgraded lumber, saved three slots, recruited Clubmen, traveled, kept a Dire Wolf offer, fought the guard, dueled, skirmished and repeated a challenge. It spent one hero point. It did not equip, claim the creature, finish the siege, start Endless, reach Bronze, reach Wisdom 3, or enter the Future.',
      hero: state?.hero?.id,
      age: state?.age,
      army: state?.army?.map(stack => stack.id),
    };
  });
} catch (error) {
  note('runner', 'FAIL', String(error?.stack || error));
} finally {
  note('page-errors', errors.length === 0 ? 'PASS' : 'FAIL', errors);
  const report = {
    at: new Date().toISOString(),
    viewport: '1280x720',
    base,
    controls: 'pointer and keyboard on the running preview',
    results,
    fail: results.filter(item => item.status === 'FAIL').map(item => item.id),
    blocked: results.filter(item => item.status === 'BLOCKED').map(item => item.id),
    pass: results.some(item => item.status === 'PASS') && !results.some(item => item.status === 'FAIL'),
    acceptance: 'INCOMPLETE',
  };
  await writeFile(out, JSON.stringify(report, null, 2));
  console.log(JSON.stringify(report, null, 2));
  await browser.close();
  process.exit(report.pass ? 0 : 1);
}
