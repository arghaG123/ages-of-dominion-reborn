// Fresh-campaign age advances and Wisdom 3. Real buttons only.
// Resource adds are the exact hall or age shortfall on this origin's save.
import { chromium } from 'file:///C:/Users/TechnoExponent/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import { writeFile } from 'node:fs/promises';
import { agePrice } from '../../src/core/rules.js';
import { cost } from '../../src/core/campaign.js';
import data from '../../src/data/reference-data.json' with { type: 'json' };

const base = process.env.AOD_PREVIEW || 'http://127.0.0.1:4561/';
const out = new URL('./age-wisdom-journey.json', import.meta.url);
const ages = ['Stone', 'Bronze', 'Iron', 'Medieval', 'Gunpowder', 'Industrial', 'Modern', 'Future'];
const spellIds = ['slow', 'bolt', 'fireball', 'resurrect'];

const report = {
  recordedAt: new Date().toISOString(),
  origin: base,
  paidCall: false,
  xpGrant: false,
  sourceEdits: false,
  sceneTraceRerun: false,
  rigRepack: false,
  apkRebuilt: false,
  ages: [],
  grants: [],
  wisdom: { status: 'UNVERIFIED', offers: [], duels: 0, wins: 0 },
};

async function save() {
  report.updatedAt = new Date().toISOString();
  await writeFile(out, JSON.stringify(report, null, 2));
}

function checksum(text) {
  let hash = 2166136261;
  for (let i = 0; i < text.length; i += 1) hash = Math.imul(hash ^ text.charCodeAt(i), 16777619);
  return (hash >>> 0).toString(16).padStart(8, '0');
}

async function wake(page) {
  await page.evaluate(() => { window.focus(); window.rebornBackground?.(false); });
}

async function snap(page) {
  return page.evaluate(() => window.rebornSnapshot());
}

async function message(page) {
  return page.locator('#message').innerText();
}

async function pressChoice(page, id) {
  await wake(page);
  return page.evaluate(choice => {
    const nodes = [...document.querySelectorAll(`[data-choice="${choice}"]`)].filter(node => node.isConnected && !node.disabled);
    const node = nodes.find(item => item.offsetParent) || nodes[0];
    if (!node) return '';
    node.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true, pointerId: 1, pointerType: 'mouse' }));
    node.dispatchEvent(new PointerEvent('pointerup', { bubbles: true, pointerId: 1, pointerType: 'mouse' }));
    node.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
    return node.textContent.trim();
  }, id);
}

async function pressText(page, starts) {
  const pressed = await pressTextNow(page, starts);
  return pressed.label;
}
async function pressTextNow(page, starts) {
  await wake(page);
  return page.evaluate(prefix => {
    const node = [...document.querySelectorAll('button')].find(item => item.isConnected && !item.disabled && item.textContent.trim().startsWith(prefix));
    if (!node) return { label: '', message: document.querySelector('#message')?.textContent || '' };
    node.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true, pointerId: 1, pointerType: 'mouse' }));
    node.dispatchEvent(new PointerEvent('pointerup', { bubbles: true, pointerId: 1, pointerType: 'mouse' }));
    node.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
    return { label: node.textContent.trim(), message: document.querySelector('#message')?.textContent || '' };
  }, starts);
}

async function buttonInfo(page, starts) {
  return page.evaluate(prefix => {
    const node = [...document.querySelectorAll('button')].find(item => item.textContent.trim().startsWith(prefix));
    return node ? { text: node.textContent.trim(), disabled: node.disabled } : null;
  }, starts);
}

async function gotoScreen(page, name) {
  const view = await page.locator('#app').getAttribute('data-view');
  if (view === name) return;
  if (view === 'home') {
    await pressChoice(page, 'continue');
    await page.waitForFunction(() => document.querySelector('#app')?.dataset.view !== 'home');
  }
  const hidden = await page.locator(`[data-choice="nav:${name}"]`).getAttribute('data-nav');
  if (hidden === 'more') await pressChoice(page, 'nav-more');
  const label = await pressChoice(page, `nav:${name}`);
  if (!label) throw new Error(`Missing nav ${name}`);
  await page.waitForFunction(expected => document.querySelector('#app')?.dataset.view === expected, name);
}

function deficit(have, need) {
  const added = {};
  for (const key of ['food', 'wood', 'stone', 'gold']) {
    const short = (need[key] || 0) - (have[key] || 0);
    if (short > 0) added[key] = short;
  }
  return added;
}

async function writeResources(page, added) {
  const applied = await page.evaluate(payload => {
    const amounts = payload.added;
    const state = window.rebornSnapshot();
    const before = { food: state.resources.food, wood: state.resources.wood, stone: state.resources.stone, gold: state.resources.gold };
    const actually = {};
    for (const key of ['food', 'wood', 'stone', 'gold']) {
      const amount = amounts[key] || 0;
      if (amount > 0) {
        state.resources[key] = before[key] + amount;
        actually[key] = amount;
      }
    }
    const encode = current => {
      const body = JSON.stringify(current);
      let hash = 2166136261;
      for (let i = 0; i < body.length; i += 1) hash = Math.imul(hash ^ body.charCodeAt(i), 16777619);
      return JSON.stringify({ schema: 1, payload: body, checksum: (hash >>> 0).toString(16).padStart(8, '0') });
    };
    for (const key of ['aod-reborn-v1-staged', 'aod-reborn-v1-backup', 'aod-reborn-v1-damaged', 'aod-reborn-v1-slot-1', 'aod-reborn-v1-slot-2', 'aod-reborn-v1-slot-3']) {
      localStorage.removeItem(key);
    }
    let trimmed = false;
    try {
      localStorage.setItem('aod-reborn-v1', encode(state));
    } catch (error) {
      if (!String(error && error.message || error).includes('quota')) throw error;
      state.inventory = [];
      const flags = {};
      for (const [key, value] of Object.entries(state.story.flags || {})) {
        if (!key.startsWith('battle:') && !key.startsWith('cleared:')) flags[key] = value;
      }
      state.story.flags = flags;
      trimmed = true;
      localStorage.removeItem('aod-reborn-v1');
      localStorage.setItem('aod-reborn-v1', encode(state));
    }
    return { before, actually, after: state.resources, trimmed };
  }, { added });
  await page.reload({ waitUntil: 'domcontentloaded' });
  await page.waitForSelector('#app');
  await wake(page);
  const view = await page.locator('#app').getAttribute('data-view');
  if (view === 'home') {
    await pressChoice(page, 'continue');
    await page.waitForFunction(() => document.querySelector('#app')?.dataset.view !== 'home');
  }
  return applied;
}

async function resolveOffers(page, bucket) {
  let guard = 0;
  while (guard < 20) {
    guard += 1;
    const state = await snap(page);
    const offer = state.hero.offers.find(item => !item.chosen && !item.declined);
    if (!offer) return state;
    await gotoScreen(page, 'hero');
    const row = {
      level: offer.level,
      choices: [...offer.choices],
      wisdomBefore: state.hero.skills.wisdom,
      xp: state.hero.xp,
      heroLevel: state.hero.level,
    };
    if (offer.choices.includes('wisdom')) {
      row.button = await pressChoice(page, 'skill:wisdom');
      row.action = 'wisdom';
    } else {
      row.button = await pressChoice(page, 'decline-skill');
      row.action = 'declined';
    }
    const after = await snap(page);
    row.wisdomAfter = after.hero.skills.wisdom;
    row.message = await message(page);
    bucket.push(row);
    if (row.action === 'wisdom' && row.wisdomAfter === row.wisdomBefore) {
      report.wisdom.status = 'BLOCKED';
      report.wisdom.blockedReason = 'Wisdom was offered and the skill button did not raise it.';
      return after;
    }
  }
  return snap(page);
}

async function duelBatch(page, count) {
  return page.evaluate(limit => {
    const click = node => {
      if (!node || node.disabled) return '';
      node.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true, pointerId: 1, pointerType: 'mouse' }));
      node.dispatchEvent(new PointerEvent('pointerup', { bubbles: true, pointerId: 1, pointerType: 'mouse' }));
      node.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
      return node.textContent.trim();
    };
    const choice = id => click([...document.querySelectorAll(`[data-choice="${id}"]`)].find(node => node.isConnected && !node.disabled));
    const text = prefix => click([...document.querySelectorAll('button')].find(node => node.isConnected && !node.disabled && node.textContent.trim().startsWith(prefix)));
    const openOffer = state => state.hero.offers.find(item => !item.chosen && !item.declined);
    const slim = state => ({
      level: state.hero.level,
      xp: state.hero.xp,
      wisdom: state.hero.skills.wisdom,
      points: state.hero.points,
      army: state.army.map(stack => ({ type: stack.type, count: stack.count, rank: stack.rank })),
      age: state.age,
      resources: { ...state.resources },
    });
    const offers = [];
    let duels = 0;
    let wins = 0;
    let xpGained = 0;
    let error = '';
    const started = performance.now();
    let last = slim(window.rebornSnapshot());
    for (let index = 0; index < limit; index += 1) {
      if (last.wisdom >= 3) break;
      if (!last.army.length) { error = 'Army is gone'; break; }
      const xpBefore = last.xp;
      const levelBefore = last.level;
      if (document.querySelector('#app')?.dataset.view !== 'war') {
        if (!choice('nav:war') && !choice('go-war')) { error = 'War control missing'; break; }
      }
      if (!text('Tactical Duel')) { error = `Tactical Duel missing: ${document.querySelector('#message')?.textContent || ''}`; break; }
      if (document.querySelector('#app')?.dataset.view !== 'tactical') {
        error = `Duel did not open: ${document.querySelector('#message')?.textContent || ''}`;
        break;
      }
      if (!document.querySelector('[data-choice="settle-battle"]')) {
        if (!choice('auto')) { error = 'Auto missing'; break; }
      }
      if (!choice('settle-battle')) { error = `Apply missing: ${document.querySelector('#message')?.textContent || ''}`; break; }
      let state = window.rebornSnapshot();
      duels += 1;
      const gained = (state.hero.level === levelBefore && state.hero.xp >= xpBefore)
        ? state.hero.xp - xpBefore
        : null;
      if (state.hero.level > levelBefore) wins += 1;
      else if (state.hero.xp > xpBefore || (state.hero.level === levelBefore && state.hero.xp === xpBefore)) {
        // A win that does not cross a level still raises XP. A loss leaves both unchanged.
        if (state.hero.xp > xpBefore) wins += 1;
      }
      if (gained != null && gained !== 0 && gained !== 110) xpGained = gained;
      let guard = 0;
      let offer = openOffer(state);
      while (offer && guard < 8) {
        guard += 1;
        if (document.querySelector('#app')?.dataset.view !== 'hero') choice('nav:hero');
        const row = { level: offer.level, choices: [...offer.choices], wisdomBefore: state.hero.skills.wisdom, heroLevel: state.hero.level, xp: state.hero.xp };
        if (offer.choices.includes('wisdom')) {
          row.button = choice('skill:wisdom');
          row.action = 'wisdom';
        } else {
          row.button = choice('decline-skill');
          row.action = 'declined';
        }
        state = window.rebornSnapshot();
        row.wisdomAfter = state.hero.skills.wisdom;
        row.message = document.querySelector('#message')?.textContent || '';
        offers.push(row);
        if (row.action === 'wisdom' && row.wisdomAfter === row.wisdomBefore) {
          error = 'Wisdom choice did not raise wisdom';
          break;
        }
        offer = openOffer(state);
      }
      last = slim(state);
      if (error) break;
    }
    const end = window.rebornSnapshot();
    const consumed = 140 * (end.hero.level - 1) * end.hero.level / 2 + end.hero.xp;
    return {
      duels,
      wins,
      offers,
      unexpectedXpDelta: xpGained,
      ms: Math.round(performance.now() - started),
      hero: slim(end),
      consumed,
      error,
      message: document.querySelector('#message')?.textContent || '',
    };
  }, count);
}

async function waitHall(page, level) {
  const start = Date.now();
  let last = null;
  while (Date.now() - start < 20000) {
    await wake(page);
    last = await snap(page);
    const hall = last.plots.find(plot => plot.id === 'townhall');
    if (hall.level >= level && !last.buildJobs.some(job => job.plotId === 'townhall')) return last;
    await new Promise(resolve => setTimeout(resolve, 250));
  }
  return last;
}

async function main() {
  const browser = await chromium.launch({
    headless: true,
    executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe',
  });
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
  page.setDefaultTimeout(300000);
  page.on('dialog', dialog => dialog.accept());
  await page.goto(base, { waitUntil: 'domcontentloaded' });
  await page.waitForSelector('#app');
  await wake(page);
  await pressChoice(page, 'new-campaign');
  await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'hero');
  const entered = await pressChoice(page, 'scene-enter-valley');
  if (!entered) await pressChoice(page, 'enter-valley');
  await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'kingdom');
  const fresh = await snap(page);
  report.campaignId = fresh.id;
  report.seed = fresh.seed;
  report.starter = {
    age: fresh.age,
    ageName: ages[fresh.age],
    hall: fresh.plots.find(plot => plot.id === 'townhall').level,
    resources: fresh.resources,
    army: fresh.army.map(stack => ({ type: stack.type, count: stack.count })),
    hero: { class: fresh.hero.class, level: fresh.hero.level, xp: fresh.hero.xp, wisdom: fresh.hero.skills.wisdom },
  };
  await save();

  let wisdomState = fresh;
  let guard = 0;
  while (wisdomState.hero.skills.wisdom < 3 && guard < 250) {
    guard += 1;
    const batch = await duelBatch(page, 40);
    report.wisdom.duels += batch.duels;
    report.wisdom.wins += batch.wins;
    report.wisdom.offers.push(...batch.offers);
    report.wisdom.lastBatchMs = batch.ms;
    report.wisdom.hero = batch.hero;
    report.wisdom.consumedXp = batch.consumed;
    report.wisdom.xpMatchesWins = batch.consumed === report.wisdom.wins * 110;
    if (batch.unexpectedXpDelta) report.wisdom.unexpectedXpDelta = batch.unexpectedXpDelta;
    if (batch.error) {
      report.wisdom.status = 'BLOCKED';
      report.wisdom.blockedReason = batch.error;
      report.wisdom.message = batch.message;
      break;
    }
    wisdomState = await snap(page);
    console.log(JSON.stringify({
      duels: report.wisdom.duels,
      wins: report.wisdom.wins,
      level: wisdomState.hero.level,
      xp: wisdomState.hero.xp,
      wisdom: wisdomState.hero.skills.wisdom,
      offers: report.wisdom.offers.length,
      ms: batch.ms,
      army: wisdomState.army.map(stack => stack.count),
    }));
    await save();
    if (!batch.duels) {
      report.wisdom.status = 'BLOCKED';
      report.wisdom.blockedReason = batch.error || 'No duel was played';
      break;
    }
  }
  if (wisdomState.hero.skills.wisdom >= 3 && report.wisdom.xpMatchesWins) report.wisdom.status = 'PASS';
  else if (wisdomState.hero.skills.wisdom < 3 && report.wisdom.status !== 'BLOCKED') {
    report.wisdom.status = 'BLOCKED';
    report.wisdom.blockedReason = 'The duel loop ended before Wisdom 3.';
  }
  await gotoScreen(page, 'hero');
  report.wisdom.spells = await page.evaluate(ids => ids.map(id => {
    const node = document.querySelector(`[data-choice="spell:${id}"]`);
    return node ? { id, text: node.textContent.trim(), disabled: node.disabled } : { id, text: '', disabled: true, missing: true };
  }), spellIds);
  report.wisdom.level = wisdomState.hero.level;
  report.wisdom.xp = wisdomState.hero.xp;
  report.wisdom.wisdom = wisdomState.hero.skills.wisdom;
  const resurrection = report.wisdom.spells.find(spell => spell.id === 'resurrect');
  if (report.wisdom.status === 'PASS' && (report.wisdom.wisdom !== 3 || resurrection?.disabled !== false)) {
    report.wisdom.status = 'BLOCKED';
    report.wisdom.blockedReason = 'Wisdom or Resurrection did not match the hero screen.';
  }
  await save();

  await gotoScreen(page, 'kingdom');
  for (let step = 0; step < 7; step += 1) {
    let state = await snap(page);
    const fromAge = state.age;
    if (fromAge >= 7) break;
    const hallUpgrades = [];
    let stopped = '';
    while (state.plots.find(plot => plot.id === 'townhall').level < fromAge + 2) {
      await gotoScreen(page, 'kingdom');
      const button = await buttonInfo(page, 'Upgrade Town Hall');
      const hall = state.plots.find(plot => plot.id === 'townhall').level;
      const price = cost(data, 'townhall', hall);
      const before = { ...state.resources };
      const short = deficit(before, price);
      const row = { hallBefore: hall, price, before, button, added: {} };
      if (!button) { stopped = 'Upgrade Town Hall button is missing'; break; }
      if (button.disabled && !Object.keys(short).length) {
        if (state.buildJobs.some(job => job.plotId === 'townhall')) {
          state = await waitHall(page, hall + 1);
          continue;
        }
        stopped = `Upgrade Town Hall is disabled without a resource shortfall: ${button.text}`;
        row.error = stopped;
        hallUpgrades.push(row);
        break;
      }
      if (Object.keys(short).length) {
        if (!button.disabled) { stopped = 'Short resources did not disable Upgrade Town Hall'; break; }
        const applied = await writeResources(page, short);
        row.added = applied.actually;
        row.grantBefore = applied.before;
        if (applied.trimmed) report.storageTrim = true;
        report.grants.push({ kind: 'hall', unblockedAge: ages[fromAge], hall, amount: applied.actually, before: applied.before, price, storageTrim: applied.trimmed === true });
        await gotoScreen(page, 'kingdom');
        row.buttonAfterGrant = await buttonInfo(page, 'Upgrade Town Hall');
        if (!row.buttonAfterGrant || row.buttonAfterGrant.disabled) {
          stopped = `Upgrade Town Hall stayed disabled after the shortfall grant: ${row.buttonAfterGrant?.text || 'missing'}`;
          row.error = stopped;
          hallUpgrades.push(row);
          break;
        }
      }
      const hallPress = await pressTextNow(page, 'Upgrade Town Hall');
      row.pressed = hallPress.label;
      row.message = hallPress.message;
      state = await waitHall(page, hall + 1);
      row.hallAfter = state.plots.find(plot => plot.id === 'townhall').level;
      row.resourcesAfter = { ...state.resources };
      hallUpgrades.push(row);
      if (row.hallAfter === hall) { stopped = row.message || 'Town Hall did not finish'; break; }
    }
    state = await snap(page);
    const ageButton = await buttonInfo(page, 'Advance age');
    const price = agePrice(fromAge);
    const before = { ...state.resources };
    const hall = state.plots.find(plot => plot.id === 'townhall').level;
    let pressed = '';
    let ageMessage = '';
    let added = {};
    if (!stopped) {
      const firstPress = await pressTextNow(page, 'Advance age');
      pressed = firstPress.label;
      ageMessage = firstPress.message;
      state = await snap(page);
      if (state.age === fromAge) {
        added = deficit(before, price);
        const resourceBlock = ageMessage.includes('Not enough resources') || Object.keys(added).length > 0;
        if (!resourceBlock) stopped = ageMessage || 'Age did not advance';
        else if (!Object.keys(added).length) stopped = ageMessage || 'Not enough resources without a positive shortfall';
        else {
          const applied = await writeResources(page, added);
          added = applied.actually;
          if (applied.trimmed) report.storageTrim = true;
          report.grants.push({ kind: 'age', unblockedAge: ages[fromAge], hall, amount: applied.actually, before: applied.before, price, button: 'Advance age', storageTrim: applied.trimmed === true });
          await gotoScreen(page, 'kingdom');
          const secondPress = await pressTextNow(page, 'Advance age');
          pressed = secondPress.label;
          ageMessage = secondPress.message;
          state = await snap(page);
          if (state.age !== fromAge + 1) stopped = ageMessage || 'Age did not advance after the shortfall grant';
        }
      }
    }
    const ageRow = {
      fromAge,
      fromName: ages[fromAge],
      hall,
      agePrice: price,
      beforeResources: before,
      grant: added,
      button: ageButton?.text || '',
      pressed,
      message: ageMessage,
      resultingAge: state.age,
      resultingName: ages[state.age] || '',
      hallUpgrades,
      error: stopped,
      status: !stopped && state.age === fromAge + 1 ? 'PASS' : 'BLOCKED',
    };
    report.ages.push(ageRow);
    await save();
    console.log(JSON.stringify({ age: ageRow.fromName, status: ageRow.status, to: ageRow.resultingName, error: stopped, grant: added }));
    if (ageRow.status !== 'PASS') break;
  }
  const finalState = await snap(page);
  report.final = {
    age: finalState.age,
    ageName: ages[finalState.age],
    hall: finalState.plots.find(plot => plot.id === 'townhall').level,
    resources: finalState.resources,
    wisdom: finalState.hero.skills.wisdom,
    level: finalState.hero.level,
    xp: finalState.hero.xp,
  };
  report.ageStatus = report.ages.length === 7 && report.ages.every(row => row.status === 'PASS') && finalState.age === 7 ? 'PASS' : 'BLOCKED';
  report.desktopCandidate = report.ageStatus === 'PASS' && report.wisdom.status === 'PASS';
  await save();
  await browser.close();
}

main().catch(async error => {
  report.fatal = String(error && error.stack || error);
  await save();
  console.error(report.fatal);
  process.exitCode = 1;
});
