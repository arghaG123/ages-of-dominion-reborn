// Visible pointer journeys for the gates the 13 October session left blocked.
// Seeded command() calls are not used. Costs, XP, and enemy lists stay as authored.
import { chromium } from 'file:///C:/Users/TechnoExponent/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import { writeFile, mkdir } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';

const base = process.env.AOD_PREVIEW || 'http://127.0.0.1:4537/';
const out = new URL('./open-gates.json', import.meta.url);
const results = [];
const note = (id, status, detail) => results.push({ id, status, detail });

async function wake(page) {
  await page.evaluate(() => { window.focus(); window.rebornBackground?.(false); });
}
async function press(page, choice) {
  await wake(page);
  const clicked = await page.evaluate(id => {
    const nodes = [...document.querySelectorAll(`[data-choice="${id}"]`)].filter(node => node.isConnected && !node.disabled);
    const node = nodes.find(item => item.offsetParent) || nodes[0];
    if (!node) return false;
    node.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true, pointerId: 1, pointerType: 'mouse' }));
    node.dispatchEvent(new PointerEvent('pointerup', { bubbles: true, pointerId: 1, pointerType: 'mouse' }));
    node.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
    return true;
  }, choice);
  if (!clicked) throw new Error(`Missing ${choice}`);
}
async function pressText(page, starts) {
  await wake(page);
  const clicked = await page.evaluate(prefix => {
    const node = [...document.querySelectorAll('button')].find(item => item.isConnected && item.textContent.trim().startsWith(prefix));
    if (!node) return '';
    node.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true, pointerId: 1, pointerType: 'mouse' }));
    node.dispatchEvent(new PointerEvent('pointerup', { bubbles: true, pointerId: 1, pointerType: 'mouse' }));
    node.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
    return node.textContent.trim();
  }, starts);
  if (!clicked) throw new Error(`Missing button ${starts}`);
  return clicked;
}
async function buttonText(page, starts) {
  return page.evaluate(prefix => {
    const node = [...document.querySelectorAll('button')].find(item => item.textContent.trim().startsWith(prefix));
    return node ? { text: node.textContent.trim(), disabled: node.disabled } : null;
  }, starts);
}
async function gotoScreen(page, name) {
  const view = await page.locator('#app').getAttribute('data-view');
  if (view === name) return;
  if (view === 'home') {
    await press(page, 'continue');
    await page.waitForFunction(() => document.querySelector('#app')?.dataset.view !== 'home');
  }
  const combat = await page.locator('#app').getAttribute('data-combat');
  if (combat === '1') throw new Error(`Cannot open ${name} during combat`);
  const hidden = await page.locator(`[data-choice="nav:${name}"]`).getAttribute('data-nav');
  if (hidden === 'more') await press(page, 'nav-more');
  await press(page, `nav:${name}`);
  await page.waitForFunction(expected => document.querySelector('#app')?.dataset.view === expected, name);
}
async function snap(page) {
  return page.evaluate(() => window.rebornSnapshot());
}
async function message(page) {
  return page.locator('#message').innerText();
}
async function emptyPlot(page) {
  const state = await snap(page);
  return state.plots.find(plot => plot.id !== 'townhall' && !plot.type && plot.level === 0)?.id || null;
}
async function build(page, type) {
  const plot = await emptyPlot(page);
  if (!plot) return { status: 'BLOCKED', text: 'No empty plot' };
  await page.locator(`[aria-label^="${plot}:"]`).evaluate(node => node.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true })));
  const choice = `build:${plot}:${type}`;
  const before = await buttonText(page, '');
  const label = await page.evaluate(id => {
    const node = document.querySelector(`[data-choice="${id}"]`);
    return node ? { text: node.textContent.trim(), disabled: node.disabled } : null;
  }, choice);
  if (!label) return { status: 'FAIL', text: `No build control for ${type}` };
  if (label.disabled) return { status: 'BLOCKED', text: label.text, plot, before };
  const resources = await page.locator('#resources').innerText();
  await press(page, choice);
  return { status: 'STARTED', text: label.text, plot, resources, after: await message(page) };
}
async function waitLevel(page, plot, level, timeout = 8000) {
  const start = Date.now();
  let last = null;
  while (Date.now() - start < timeout) {
    await wake(page);
    last = await page.evaluate(id => document.querySelector(`[aria-label^="${id}:"]`)?.getAttribute('aria-label') || '', plot);
    if (last.includes(`level ${level}`)) return { label: last };
    await new Promise(resolve => setTimeout(resolve, 250));
  }
  return { label: last, timedOut: true };
}
async function waitResources(page, need, timeout) {
  const start = Date.now();
  let last = null;
  while (Date.now() - start < timeout) {
    await wake(page);
    last = (await snap(page)).resources;
    if (Object.entries(need).every(([key, amount]) => last[key] >= amount)) return { ok: true, resources: last };
    await new Promise(resolve => setTimeout(resolve, 500));
  }
  return { ok: false, resources: last };
}
async function step(page, id, fn) {
  try {
    const detail = await fn();
    note(id, detail.status || 'PASS', detail);
  } catch (error) {
    note(id, 'FAIL', String(error && error.stack || error));
  }
}

const browser = await chromium.launch({
  headless: true,
  executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe',
});
const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
page.setDefaultTimeout(20000);
page.on('dialog', dialog => dialog.accept());
await page.goto(base, { waitUntil: 'domcontentloaded' });
await page.waitForSelector('#app');
await wake(page);

await step(page, 'worn-slots-empty', async () => {
  await press(page, 'new-campaign');
  await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'hero');
  await press(page, 'scene-class:healer');
  await page.waitForFunction(() => document.querySelector('[data-actor="healer"]'));
  const slots = await page.evaluate(() => [...document.querySelectorAll('[data-worn-slot]')].map(node => ({
    slot: node.dataset.wornSlot,
    state: node.dataset.wornState,
    bonus: node.dataset.wornBonus || '',
  })));
  const cells = await page.evaluate(() => new Promise(resolve => {
    requestAnimationFrame(() => resolve(document.querySelectorAll('[data-adventure-cell]').length));
  }));
  return { status: slots.length === 6 && slots.every(slot => slot.state === 'empty') ? 'PASS' : 'FAIL', slots, adventureCellsOnHero: cells };
});

await step(page, 'bronze-hall-gate', async () => {
  await press(page, 'scene-enter-valley');
  await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'kingdom');
  const before = await message(page);
  const label = await pressText(page, 'Advance age');
  const after = await message(page);
  return { status: after.includes('Town Hall level too low') ? 'BLOCKED' : 'FAIL', label, before, after };
});

await step(page, 'producers', async () => {
  const lumber = await build(page, 'lumber');
  if (lumber.status !== 'STARTED') return lumber;
  const lumberDone = await waitLevel(page, lumber.plot, 1);
  const quarry = await build(page, 'quarry');
  if (quarry.status !== 'STARTED') return { status: 'BLOCKED', lumber, quarry, lumberDone };
  const quarryDone = await waitLevel(page, quarry.plot, 1);
  const barracks = await build(page, 'barracks');
  if (barracks.status !== 'STARTED') return { status: 'BLOCKED', lumberDone, quarryDone, barracks };
  const barracksDone = await waitLevel(page, barracks.plot, 1);
  return {
    status: lumberDone.label?.includes('level 1') && quarryDone.label?.includes('level 1') && barracksDone.label?.includes('level 1') ? 'PASS' : 'FAIL',
    lumber: lumberDone, quarry: quarryDone, barracks: barracksDone,
  };
});

await step(page, 'dire-wolf', async () => {
  await gotoScreen(page, 'adventure');
  await press(page, 'enter-adventure');
  await page.waitForSelector('[data-adventure-cell]', { state: 'attached' });
  const survived = await page.evaluate(() => new Promise(resolve => {
    requestAnimationFrame(() => resolve(document.querySelectorAll('[data-adventure-cell]').length));
  }));
  const cell = page.locator('[data-adventure-cell="10,8"][data-open="1"]');
  if (!(await cell.count())) {
    return { status: 'BLOCKED', text: '10,8 is not an open adventure cell', cells: survived };
  }
  await cell.evaluate(node => node.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true })));
  const preview = await page.locator('[data-choice="confirm-route"]').first().innerText();
  await press(page, 'confirm-route');
  await page.waitForFunction(() => (document.querySelector('#selected')?.textContent || '').includes('Travel 10,8'), null, { timeout: 8000 });
  const ask = await page.evaluate(() => document.querySelector('[data-choice="offer-dwelling:wolf"]')?.textContent || '');
  if (ask) await press(page, 'offer-dwelling:wolf');
  const claim = await page.evaluate(() => {
    const node = document.querySelector('[data-choice="claim-dwelling"]');
    return node ? { text: node.textContent.trim(), disabled: node.disabled } : null;
  });
  if (!claim) return { status: 'BLOCKED', preview, ask, text: await message(page), cells: survived };
  if (claim.disabled) return { status: 'BLOCKED', preview, claim, cells: survived };
  await press(page, 'claim-dwelling');
  const state = await snap(page);
  const creature = state.army.find(stack => stack.kind === 'creature');
  await page.locator('#save').click();
  await page.reload({ waitUntil: 'domcontentloaded' });
  await page.waitForSelector('#app');
  await wake(page);
  if (await page.locator('#app').getAttribute('data-view') === 'home') await press(page, 'continue');
  const reloaded = await snap(page);
  const kept = reloaded.army.find(stack => stack.kind === 'creature');
  return { status: kept ? 'PASS' : 'FAIL', preview, claim, creature, kept, cells: survived };
});

await step(page, 'armory', async () => {
  await gotoScreen(page, 'kingdom');
  const ready = await waitResources(page, { wood: 120, stone: 120, gold: 80 }, 180000);
  const started = await build(page, 'armory');
  if (started.status !== 'STARTED') return { status: 'BLOCKED', ready, ...started };
  const done = await waitLevel(page, started.plot, 1, 12000);
  return { status: done.label?.includes('level 1') ? 'PASS' : 'FAIL', ready, started, done };
});

await step(page, 'worn-forge', async () => {
  await gotoScreen(page, 'kingdom');
  const ready = await waitResources(page, { wood: 80, stone: 60, gold: 70 }, 240000);
  await gotoScreen(page, 'forge');
  const offer = await buttonText(page, 'Forge ');
  if (!offer) return { status: 'BLOCKED', ready, text: await message(page) };
  if (offer.disabled) return { status: 'BLOCKED', ready, offer };
  const before = (await snap(page)).hero;
  await pressText(page, 'Forge ');
  const bag = await page.evaluate(() => {
    const node = [...document.querySelectorAll('[data-choice^="equip:"]')][0];
    return node ? node.dataset.choice : '';
  });
  if (!bag) return { status: 'FAIL', ready, offer, text: await message(page) };
  await press(page, bag);
  const confirm = await page.evaluate(() => {
    const node = document.querySelector('[data-choice^="equip-confirm:"]');
    return node ? node.dataset.choice : '';
  });
  if (confirm) await press(page, confirm);
  await gotoScreen(page, 'hero');
  const slots = await page.evaluate(() => [...document.querySelectorAll('[data-worn-slot]')].map(node => ({
    slot: node.dataset.wornSlot,
    state: node.dataset.wornState,
    bonus: node.dataset.wornBonus || '',
    icon: node.querySelector('[data-gear-icon]')?.getAttribute('data-gear-icon') || '',
  })));
  const after = await snap(page);
  const worn = slots.find(slot => slot.state === 'worn');
  return {
    status: worn && after.hero.growth ? 'PASS' : 'FAIL',
    ready, offer, beforeAttack: before, afterStats: after.hero, slots,
  };
});

await step(page, 'bronze-price', async () => {
  await gotoScreen(page, 'kingdom');
  const hall = await buttonText(page, 'Upgrade Town Hall');
  const advance = await pressText(page, 'Advance age');
  const after = await message(page);
  const reached = (await snap(page)).age > 0;
  return { status: reached ? 'PASS' : 'BLOCKED', hall, advance, after };
});

await step(page, 'wisdom-3', async () => {
  const before = (await snap(page)).hero;
  await gotoScreen(page, 'war');
  await pressText(page, 'Tactical Duel');
  await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'tactical');
  await pressText(page, 'Auto');
  await page.waitForSelector('[data-choice="settle-battle"]', { timeout: 20000 });
  await press(page, 'settle-battle');
  const after = (await snap(page)).hero;
  await gotoScreen(page, 'hero');
  const spells = await page.evaluate(() => [...document.querySelectorAll('[data-choice^="spell:"]')].map(node => ({
    choice: node.dataset.choice, text: node.textContent.trim(), disabled: node.disabled,
  })));
  const wisdom = after.skills?.wisdom || 0;
  return { status: wisdom >= 3 ? 'PASS' : 'BLOCKED', beforeXp: before.xp, beforeLevel: before.level, afterXp: after.xp, afterLevel: after.level, wisdom, spells };
});

await step(page, 'siege-result', async () => {
  await gotoScreen(page, 'war');
  await press(page, 'start-siege');
  await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'defense');
  await press(page, 'defense-speed');
  const start = Date.now();
  let last = null;
  while (Date.now() - start < 180000) {
    await wake(page);
    last = await page.evaluate(() => {
      const snap = window.rebornSnapshot();
      return {
        selected: document.querySelector('#selected')?.textContent || '',
        status: snap?.defense?.status || null,
        pending: snap?.defense?.pendingSettlement || false,
        winner: snap?.defense?.winner || null,
        core: snap?.defense?.core ?? null,
      };
    });
    if (last.pending || last.status === 'RESOLVED') break;
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
  if (!(last?.pending || last?.status === 'RESOLVED')) return { status: 'BLOCKED', last };
  await press(page, 'settle-defense');
  const settled = await message(page);
  const defense = (await snap(page)).defense;
  return { status: defense ? 'FAIL' : 'PASS', last, settled };
});

await step(page, 'endless', async () => {
  const combat = await page.locator('#app').getAttribute('data-combat');
  if (combat === '1') {
    const selected = await page.locator('#selected').innerText();
    return { status: 'BLOCKED', text: selected };
  }
  await gotoScreen(page, 'war');
  const before = await message(page);
  await press(page, 'start-endless');
  const view = await page.locator('#app').getAttribute('data-view');
  const after = await message(page);
  const defense = (await snap(page)).defense;
  return { status: defense?.practice === 'endless' ? 'PASS' : 'BLOCKED', view, before, after, practice: defense?.practice || null };
});

await browser.close();
await mkdir(fileURLToPath(new URL('./shots/', import.meta.url)), { recursive: true });
const acceptance = results.some(row => row.status === 'FAIL') ? 'FAIL' : 'INCOMPLETE';
await writeFile(out, JSON.stringify({
  generatedAt: new Date().toISOString(),
  base,
  viewport: '1280x720',
  acceptance,
  product: 'INCOMPLETE',
  results,
}, null, 2));
console.log(results.map(row => `${row.id} ${row.status}`).join('\n'));
