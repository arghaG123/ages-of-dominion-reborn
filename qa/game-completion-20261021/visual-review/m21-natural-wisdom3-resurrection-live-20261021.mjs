import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import worlds from '../../../src/data/adventure-worlds.json' with { type: 'json' };
import contract from '../../../src/data/implementation-contract.json' with { type: 'json' };
import { adventureGeometryForWorld, adventureMap, routeTo, stepCost } from '../../../src/core/navigation.js';

const root = process.cwd();
const output = path.join(root, 'qa/game-completion-20261021/visual-review/m21-natural-wisdom3-resurrection-live-20261021-run08');
const maxBattles = Number(process.argv[2] || 80);
if (!Number.isInteger(maxBattles) || maxBattles < 1 || maxBattles > 560) throw new Error('Pass a natural battle limit from 1 to 560.');
await fs.mkdir(output, { recursive: true });

const report = {
  recordedAt: new Date().toISOString(),
  classification: 'NATURAL_UI_CAMPAIGN_CONTROLLED_BROWSER',
  journey: 'fresh isolated browser -> new campaign through visible world/class choices -> travel by confirmed Adventure routes to the skill monument -> choose only visibly offered skills -> repeat visible campaign Tactical Duels and legal Auto/settlement -> reload at earned Wisdom 3 -> cast Resurrection on a living stack after a natural in-battle casualty -> reload and settle',
  viewport: { width: 1280, height: 720, deviceScaleFactor: 1 },
  selectedClass: 'mage',
  maxBattles,
  battles: [],
  skillSelections: [],
  errors: [],
  screenshots: {},
  passed: false,
};

const browser = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
const context = await browser.newContext({ viewport: report.viewport, deviceScaleFactor: 1 });
const page = await context.newPage();
page.on('pageerror', error => report.errors.push({ kind: 'pageerror', text: String(error) }));
page.on('console', message => { if (message.type() === 'error') report.errors.push({ kind: 'console', text: message.text() }); });
page.on('requestfailed', request => report.errors.push({ kind: 'requestfailed', url: request.url(), text: request.failure()?.errorText || '' }));

const wait = ms => page.waitForTimeout(ms);
async function click(selector, label = selector) {
  const control = page.locator(selector).first();
  await control.waitFor({ state: 'visible', timeout: 10000 });
  assert.equal(await control.isDisabled(), false, `${label} is enabled`);
  await control.click();
  await wait(130);
}
async function snapshot() {
  return page.evaluate(() => window.rebornSnapshot());
}
async function saveScreenshot(name) {
  const file = path.join(output, `${name}.png`);
  await page.screenshot({ path: file });
  report.screenshots[name] = path.relative(root, file);
}
async function waitForRevision(after) {
  await page.waitForFunction(revision => (window.rebornSnapshot()?.revision || 0) > revision, after, { timeout: 10000 });
}
async function openAdventurePanel() {
  if (!(await page.locator('#panel').evaluate(panel => panel.classList.contains('open')))) {
    await click('#dock [data-choice="inspect:adventure"]', 'Open Adventure details');
  }
}
async function finishAdventureDay() {
  await openAdventurePanel();
  const before = await snapshot();
  await click('#choices [data-choice="adventure-end-day"]', 'Restore Adventure movement for a new day');
  await waitForRevision(before.revision);
}
async function moveToward(map, goal, label, allowGuardGoal = false) {
  for (let segment = 0; segment < 80; segment += 1) {
    const state = await snapshot();
    const adventure = state.adventure;
    if (adventure.x === goal[0] && adventure.y === goal[1]) return;
    if (adventure.pendingEncounter?.status?.startsWith('UNRESOLVED')) throw new Error(`A guard interrupted travel to ${label}.`);
    if (adventure.moves <= 0) { await finishAdventureDay(); continue; }
    const start = [adventure.x, adventure.y];
    const directions = [['north', 0, -1], ['east', 1, 0], ['south', 0, 1], ['west', -1, 0]];
    const options = [];
    const goalKey = goal.join(',');
    for (const [direction, dx, dy] of directions) {
      const next = [start[0] + dx, start[1] + dy];
      const key = next.join(',');
      if (map.blocked.has(key) || (map.guards.has(key) && !(allowGuardGoal && key === goalKey))) continue;
      try {
        const step = stepCost(map, start, next);
        const tail = next[0] === goal[0] && next[1] === goal[1] ? { cost: 0 } : routeTo(map, next, goal);
        options.push({ direction, score: step + tail.cost });
      } catch {}
    }
    options.sort((first, second) => first.score - second.score || first.direction.localeCompare(second.direction));
    const route = options[0];
    if (!route) throw new Error(`No legal cardinal route to ${label} from ${start.join(',')}.`);
    const beforeRevision = state.revision;
    await openAdventurePanel();
    await click(`#choices [data-choice="preview-${route.direction}"]`, `Preview ${route.direction} route step`);
    const confirm = page.locator('#choices [data-choice="confirm-route"]');
    await confirm.waitFor({ state: 'visible', timeout: 5000 });
    if (await confirm.isDisabled()) {
      await click('#choices [data-choice="clear-preview"]', 'Clear route preview');
      await finishAdventureDay();
      continue;
    }
    await confirm.click();
    await waitForRevision(beforeRevision);
    await wait(150);
  }
  const state = await snapshot();
  throw new Error(`Could not reach ${label}; stopped at ${state.adventure.x},${state.adventure.y}.`);
}
async function visitNaturalShrine() {
  await click('[data-choice="nav:adventure"]', 'Adventure navigation');
  await click('#dock [data-choice="inspect:adventure"]', 'Open Adventure details');
  await click('#choices [data-choice="enter-adventure"]', 'Enter Adventure');
  await page.waitForFunction(() => Boolean(window.rebornSnapshot()?.adventure && !window.rebornSnapshot().adventure.atTown), null, { timeout: 15000 });
  const state = await snapshot();
  const world = worlds.find(entry => entry.id === state.adventureWorldId);
  const geometry = adventureGeometryForWorld(contract.geometry.adventure, world, state.seed);
  const map = adventureMap(geometry);
  const shrine = geometry.sites.find(site => site.id === 'shrine');
  report.shrineJourney = { worldId: state.adventureWorldId, seed: state.seed, coordinates: shrine.approach, route: 'visible cardinal previews and confirmed routes; day-end control restores movement' };
  await moveToward(map, shrine.approach, 'the skill monument');
  await openAdventurePanel();
  const before = await snapshot();
  await click('#choices [data-choice="study-skill-monument"]', 'Study at the skill monument');
  await waitForRevision(before.revision);
  const offeredState = await snapshot();
  const offer = offeredState.hero.offers.find(row => row.source === 'adventure-shrine' && !row.chosen && !row.declined);
  if (!offer) throw new Error('The naturally reached skill monument did not create a pending offer.');
  const chosen = offer.choices.includes('wisdom') && offeredState.hero.skills.wisdom < 3 ? 'wisdom' : offer.choices[0];
  await click(`#choices [data-choice="shrine-skill:${chosen}"]`, `Choose the offered shrine skill ${chosen}`);
  await waitForRevision(offeredState.revision);
  const after = await snapshot();
  report.shrineJourney.offer = { choices: offer.choices, chosen, resultingWisdom: after.hero.skills.wisdom, claimed: after.adventure.claimedSites.includes('shrine') };
  assert.equal(report.shrineJourney.offer.claimed, true, 'resolving the shrine offer consumes the monument once');
}
async function startNaturalGuardBattle() {
  await click('[data-choice="nav:adventure"]', 'Adventure navigation');
  await openAdventurePanel();
  const state = await snapshot();
  const world = worlds.find(entry => entry.id === state.adventureWorldId);
  const geometry = adventureGeometryForWorld(contract.geometry.adventure, world, state.seed);
  const map = adventureMap(geometry);
  const start = [state.adventure.x, state.adventure.y];
  const targets = [...map.guards].map(value => value.split(',').map(Number)).filter(([x, y]) => {
    const key = `${x},${y}`;
    return !state.adventure.resolvedGuards.includes(key);
  }).map(cell => {
    try { return { cell, cost: routeTo(map, start, cell).cost }; }
    catch { return null; }
  }).filter(Boolean).sort((first, second) => first.cost - second.cost);
  const target = targets[0];
  if (!target) throw new Error('No reachable unresolved natural guard is available from the skill monument.');
  report.naturalGuard = { cell: target.cell, routeCost: target.cost };
  await moveToward(map, target.cell, 'a natural guard encounter', true);
  await page.waitForFunction(() => String(window.rebornSnapshot()?.adventure?.pendingEncounter?.status || '').startsWith('UNRESOLVED'), null, { timeout: 10000 });
  const pending = await snapshot();
  report.naturalGuard.pendingEncounter = {
    id: pending.adventure.pendingEncounter.id,
    cell: pending.adventure.pendingEncounter.cell,
    difficulty: pending.adventure.pendingEncounter.difficulty,
    stacks: pending.adventure.pendingEncounter.pack?.stacks?.map(stack => ({ type: stack.type, count: stack.count })) || [],
  };
  await openAdventurePanel();
  await click('#choices [data-choice="begin-encounter"]', 'Begin the natural guard encounter');
  await page.waitForFunction(() => window.rebornSnapshot()?.battle?.status === 'ACTIVE', null, { timeout: 15000 });
}
async function resolveVisibleSkillOffers() {
  await click('[data-choice="nav:hero"]', 'Hero navigation');
  await click('#dock [data-choice="inspect:hero"]', 'Open Hero details');
  let guard = 0;
  while (guard++ < 6) {
    const available = await page.locator('#choices button[data-choice^="skill:"][data-skill-offer="available"]').evaluateAll(nodes => nodes.map(node => node.dataset.choice.slice('skill:'.length)));
    if (!available.length) break;
    const state = await snapshot();
    const pending = state.hero.offers.find(offer => !offer.chosen && !offer.declined);
    if (!pending) throw new Error('Visible skill offer cards exist without a saved pending offer.');
    const chosen = (available.includes('wisdom') && state.hero.skills.wisdom < 3)
      ? 'wisdom'
      : ['firstaid', 'offense', 'armorer', 'archery', 'leadership', 'luck', 'tactics', 'logistics'].find(skill => available.includes(skill));
    if (!chosen) throw new Error(`No legal visible skill choice in offer ${pending.choices.join(', ')}.`);
    await click(`#choices [data-choice="skill:${chosen}"]`, `offered ${chosen}`);
    await page.locator('#build-confirm').waitFor({ state: 'visible', timeout: 5000 });
    await click('#build-commit', 'Confirm skill choice');
    await page.waitForFunction(skill => {
      const state = window.rebornSnapshot();
      return state?.hero?.skills?.[skill] > 0 || !state?.hero?.offers?.some(offer => !offer.chosen && !offer.declined);
    }, chosen, { timeout: 5000 });
    const after = await snapshot();
    report.skillSelections.push({ level: pending.level, offered: [...pending.choices], chosen, resultingRank: after.hero.skills[chosen], wisdom: after.hero.skills.wisdom });
  }
  await click('[data-choice="nav:war"]', 'War navigation');
}

try {
  await page.goto('http://127.0.0.1:4179/', { waitUntil: 'networkidle' });
  await click('[data-choice="new-campaign"]', 'New campaign');
  await click('[data-choice="campaign-world:jade-karst"]', 'Select Jade Karst campaign world');
  await click('[data-choice="begin-selected-world"]', 'Begin selected world');
  await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'hero', { timeout: 10000 });
  await click('[data-choice="scene-class:mage"]', 'Select Mage');
  await click('[data-choice="scene-enter-valley"]', 'Enter the valley');
  await visitNaturalShrine();
  await click('[data-choice="nav:war"]', 'War navigation');
  const initial = await snapshot();
  report.campaign = { id: initial.id, seed: initial.seed, age: initial.age, startingArmy: initial.army.map(stack => ({ id: stack.id, type: stack.type, count: stack.count })) };

  let stop = 'battle limit reached before Wisdom 3';
  for (let index = 0; index < maxBattles; index++) {
    const before = await snapshot();
    if (before.hero.skills.wisdom >= 3) {
      stop = 'Wisdom 3 earned';
      break;
    }
    if (!before.army.some(stack => stack.count > 0)) {
      stop = 'campaign army depleted through natural battle losses';
      break;
    }
    await click('[data-choice="start-duel"]', 'Tactical Duel');
    await page.waitForFunction(() => window.rebornSnapshot()?.battle?.status === 'ACTIVE', { timeout: 10000 });
    await click('#dock [data-choice="auto"]', 'Auto legal tactical actions');
    await page.waitForFunction(() => window.rebornSnapshot()?.battle?.pendingSettlement === true, { timeout: 15000 });
    const battle = await snapshot();
    const outcome = {
      index: index + 1,
      id: battle.battle.id,
      winner: battle.battle.outcome?.winner,
      rounds: battle.battle.round,
      mana: battle.battle.mana,
      alliedStacks: battle.battle.stacks.filter(stack => stack.side === 'p').map(stack => ({
        id: stack.id, campaignId: stack.campaignId, count: stack.count, maxCount: stack.maxCount,
        top: stack.top, uhp: stack.uhp, dead: stack.dead,
      })),
      enemyStacks: battle.battle.stacks.filter(stack => stack.side === 'e').map(stack => ({ id: stack.id, count: stack.count, dead: stack.dead })),
    };
    await click('#scene-ui [data-choice="result:tactical"]', 'Return to campaign and settle the duel');
    await page.waitForFunction(() => window.rebornSnapshot()?.battle == null, { timeout: 10000 });
    const after = await snapshot();
    outcome.hero = { level: after.hero.level, xp: after.hero.xp, wisdom: after.hero.skills.wisdom, mana: after.hero.mana };
    outcome.armyAfter = after.army.map(stack => ({ id: stack.id, type: stack.type, count: stack.count }));
    report.battles.push(outcome);
    if (battle.battle.outcome?.winner !== 'p') {
      stop = `natural Tactical Duel ended ${battle.battle.outcome?.winner || 'without a winner'}`;
      break;
    }
    if (after.hero.offers.some(offer => !offer.chosen && !offer.declined)) await resolveVisibleSkillOffers();
  }

  let state = await snapshot();
  report.progressionAtStop = { level: state.hero.level, xp: state.hero.xp, wisdom: state.hero.skills.wisdom, mana: state.hero.mana, army: state.army.map(stack => ({ id: stack.id, type: stack.type, count: stack.count })) };
  report.stopReason = stop;

  if (state.hero.skills.wisdom >= 3) {
    const beforeReload = { level: state.hero.level, xp: state.hero.xp, wisdom: state.hero.skills.wisdom, offers: state.hero.offers };
    await page.reload({ waitUntil: 'networkidle' });
    await page.waitForFunction(() => window.rebornSnapshot()?.hero?.skills?.wisdom >= 3, { timeout: 10000 });
    state = await snapshot();
    report.wisdomReload = { before: beforeReload, after: { level: state.hero.level, xp: state.hero.xp, wisdom: state.hero.skills.wisdom } };
    await click('[data-choice="nav:hero"]', 'Hero navigation');
    await click('#dock [data-choice="inspect:hero"]', 'Open Hero details');
    await click('[data-choice="hero-tab:spells"]', 'Open Spellbook');
    const resurrectCard = page.locator('#choices [data-choice="spell:resurrect"]');
    report.spellbook = {
      wisdom: state.hero.skills.wisdom,
      resurrectionVisible: await resurrectCard.count() === 1,
      resurrectionLabel: await resurrectCard.getAttribute('aria-label'),
    };
    await saveScreenshot('earned-wisdom3-spellbook');

    await startNaturalGuardBattle();
    let battle = await snapshot();
    const maxSetupTurns = 24;
    for (let turn = 0; turn < maxSetupTurns; turn++) {
      const living = battle.battle.stacks.filter(stack => stack.side === 'p' && !stack.dead && stack.count > 0);
      const wounded = living.find(stack => stack.count < stack.maxCount);
      if (wounded && battle.battle.status === 'ACTIVE') {
        const targetChoice = `spellcast:resurrect:${wounded.id}`;
        report.resurrectionBefore = { target: { id: wounded.id, count: wounded.count, maxCount: wounded.maxCount, top: wounded.top, uhp: wounded.uhp }, mana: battle.battle.mana, round: battle.battle.round };
        await click('#dock [data-choice="intent:spell"]', 'Spell intent');
        await page.waitForFunction(choice => Boolean(document.querySelector(`#choices [data-choice="${CSS.escape(choice)}"]`)), targetChoice, { timeout: 5000 });
        await click(`#choices [data-choice="${targetChoice}"]`, 'Resurrection on naturally wounded stack');
        const afterCast = await snapshot();
        const healed = afterCast.battle.stacks.find(stack => stack.id === wounded.id);
        report.resurrectionAfter = { target: { id: healed.id, count: healed.count, maxCount: healed.maxCount, top: healed.top, uhp: healed.uhp }, mana: afterCast.battle.mana, spellLog: afterCast.battle.log.filter(entry => entry.type === 'spell').at(-1) };
        report.resurrectionCastPassed = report.resurrectionAfter.spellLog?.id === 'resurrect'
          && report.resurrectionAfter.mana < report.resurrectionBefore.mana
          && wounded.count < wounded.maxCount
          && healed.count > wounded.count;
        const panelClose = page.locator('#panel-close');
        if (await panelClose.isVisible()) await panelClose.click();
        await wait(120);
        await saveScreenshot('natural-resurrection-cast');
        await page.reload({ waitUntil: 'networkidle' });
        await page.waitForFunction(() => window.rebornSnapshot()?.battle?.log?.some(entry => entry.type === 'spell' && entry.id === 'resurrect'), { timeout: 10000 });
        const reloadedBattle = await snapshot();
        report.resurrectionReload = {
          spellPersisted: reloadedBattle.battle.log.some(entry => entry.type === 'spell' && entry.id === 'resurrect'),
          mana: reloadedBattle.battle.mana,
          target: (() => { const stack = reloadedBattle.battle.stacks.find(item => item.id === wounded.id); return { id: stack.id, count: stack.count, maxCount: stack.maxCount, top: stack.top, uhp: stack.uhp }; })(),
        };
        report.resurrectionReload.casualtyRestoredPersisted = report.resurrectionReload.target.count === healed.count
          && report.resurrectionReload.target.count > wounded.count;
        if (reloadedBattle.battle.status === 'ACTIVE') {
          await click('#dock [data-choice="auto"]', 'Finish the campaign duel through legal Auto actions');
          await page.waitForFunction(() => window.rebornSnapshot()?.battle?.pendingSettlement === true, { timeout: 15000 });
          await click('#scene-ui [data-choice="result:tactical"]', 'Return to campaign and settle the final duel');
          await page.waitForFunction(() => window.rebornSnapshot()?.battle == null, { timeout: 10000 });
          const settled = await snapshot();
          report.finalCampaignAfterSettlement = {
            level: settled.hero.level,
            wisdom: settled.hero.skills.wisdom,
            mana: settled.hero.mana,
            army: settled.army.map(stack => ({ id: stack.id, type: stack.type, count: stack.count })),
            adventure: { pendingEncounter: settled.adventure?.pendingEncounter, resolvedGuards: settled.adventure?.resolvedGuards },
          };
        }
        break;
      }
      if (battle.battle.pendingSettlement) break;
      const waitAction = page.locator('#dock [data-choice="wait"]');
      const defend = page.locator('#dock [data-choice="defend"]');
      const canWait = await waitAction.count() === 1 && !(await waitAction.isDisabled());
      const nextAction = canWait ? waitAction : defend;
      if (await nextAction.count() !== 1 || await nextAction.isDisabled()) break;
      const activeId = battle.battle.queue.find(id => {
        const queued = battle.battle.stacks.find(item => item.id === id);
        return queued && !queued.dead && !queued.acted;
      });
      report.resurrectionSetup ||= [];
      report.resurrectionSetup.push({ round: battle.battle.round, action: canWait ? 'wait' : 'defend', active: activeId || null, stacks: living.map(stack => ({ id: stack.id, count: stack.count, maxCount: stack.maxCount, top: stack.top, uhp: stack.uhp })) });
      await nextAction.click();
      await wait(180);
      battle = await snapshot();
    }
    if (state.hero.skills.wisdom >= 3 && report.resurrectionCastPassed !== true) {
      report.resurrectionCastPassed = false;
      report.resurrectionBlocker = 'No living allied stack lost a unit during the bounded natural Tactical Duel setup turns, or the battle resolved first.';
      if (battle.battle.pendingSettlement) await click('#scene-ui [data-choice="result:tactical"]', 'Return to campaign and settle the final duel');
    }
  }

  report.passed = report.progressionAtStop.wisdom >= 3 && report.wisdomReload?.after.wisdom === 3
    && report.spellbook?.resurrectionVisible === true && report.resurrectionCastPassed === true
    && report.resurrectionReload?.spellPersisted === true && report.resurrectionReload?.casualtyRestoredPersisted === true
    && report.errors.length === 0;
} catch (error) {
  report.failure = String(error?.stack || error);
} finally {
  try { await fs.writeFile(path.join(output, 'report.json'), `${JSON.stringify(report, null, 2)}\n`, 'utf8'); }
  finally { await context.close(); await browser.close(); }
}

console.log(JSON.stringify({ output: path.relative(root, output), passed: report.passed, stopReason: report.stopReason, progressionAtStop: report.progressionAtStop, battleCount: report.battles.length, skillSelections: report.skillSelections, resurrectionCastPassed: report.resurrectionCastPassed, errors: report.errors, failure: report.failure }, null, 2));
if (!report.passed) process.exitCode = 1;
