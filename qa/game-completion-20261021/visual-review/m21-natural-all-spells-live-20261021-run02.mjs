import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import worlds from '../../../src/data/adventure-worlds.json' with { type: 'json' };
import contract from '../../../src/data/implementation-contract.json' with { type: 'json' };
import { adventureGeometryForWorld, adventureMap, routeTo, stepCost } from '../../../src/core/navigation.js';

const root = process.cwd();
const output = path.join(root, 'qa/game-completion-20261021/visual-review/m21-natural-all-spells-live-20261021-run02');
const maxBattles = Number(process.argv[2] || 80);
if (!Number.isInteger(maxBattles) || maxBattles < 1 || maxBattles > 560) throw new Error('Pass a natural battle limit from 1 to 560.');
await fs.mkdir(output, { recursive: true });

const report = {
  recordedAt: new Date().toISOString(),
  classification: 'NATURAL_UI_CAMPAIGN_CONTROLLED_BROWSER',
  journey: 'fresh isolated browser -> visible new campaign and skill monument -> earn Wisdom 3 through natural Tactical Duels and visible offers -> cast each of eight spells through legal visible actions across campaign battles -> verify each effect and reload persistence -> settle battles visibly',
  viewport: { width: 1280, height: 720, deviceScaleFactor: 1 },
  selectedClass: 'mage',
  maxBattles,
  battles: [],
  naturalSpellCasts: [],
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
      : ['armorer', 'firstaid', 'leadership', 'luck', 'archery', 'offense', 'tactics', 'logistics'].find(skill => available.includes(skill));
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
async function spendAvailableKnowledgePoints() {
  let state = await snapshot();
  if (state.hero.points < 1) return;
  report.knowledgePointSpends ||= [];
  const panelClose = page.locator('#panel-close');
  if (await panelClose.isVisible()) await panelClose.click();
  await click('[data-choice="nav:hero"]', 'Hero navigation to spend the earned attribute point');
  await click('#dock [data-choice="inspect:hero"]', 'Open Hero details');
  await click('#choices [data-choice="hero-tab:skills"]', 'Open Hero skill and attribute page');
  let guard = 0;
  while (guard++ < 100) {
    state = await snapshot();
    if (state.hero.points < 1) break;
    const control = page.locator('#choices [data-choice="spend:kno"]');
    if (await control.count() !== 1 || await control.isDisabled()) throw new Error(`The visible Knowledge allocation is unavailable with ${state.hero.points} unspent points.`);
    const before = { points: state.hero.points, mana: state.hero.mana, level: state.hero.level };
    await click('#choices [data-choice="spend:kno"]', 'Spend one visible attribute point on Knowledge');
    await waitForRevision(state.revision);
    const after = await snapshot();
    report.knowledgePointSpends.push({ before, after: { points: after.hero.points, mana: after.hero.mana, level: after.hero.level, knowledge: after.hero.growth.kno + after.hero.bonus.kno } });
  }
  await click('[data-choice="nav:war"]', 'Return to War after spending Knowledge points');
}

function poolHp(stack) {
  return stack.count > 0 ? (stack.count - 1) * stack.uhp + stack.top : 0;
}
function maximumPoolHp(stack) { return stack.maxCount * stack.uhp; }
function currentActor(battle) {
  const id = battle.queue.find(candidate => {
    const stack = battle.stacks.find(item => item.id === candidate);
    return stack && !stack.dead && !stack.acted;
  });
  return battle.stacks.find(stack => stack.id === id) || null;
}
const spellCosts = { arrow: 5, bless: 5, haste: 6, cure: 6, slow: 8, bolt: 10, fireball: 14, resurrect: 20 };
async function castVisibleNaturalSpell(spellId, context) {
  const beforeState = await snapshot();
  let battle = beforeState.battle;
  assert.equal(battle?.status, 'ACTIVE', `${spellId} begins in an active natural campaign battle`);
  assert.ok(beforeState.hero.skills.wisdom >= 3, `${spellId} follows naturally earned Wisdom 3`);
  assert.ok(battle.mana >= spellCosts[spellId], `${spellId} has enough naturally saved mana`);
  let actor = currentActor(battle);
  if (actor?.side !== 'p' || battle.castThisRound) throw new Error(`${spellId} was not attempted on an available player commander turn.`);
  await click('#dock [data-choice="intent:spell"]', `Open visible spell choices for ${spellId}`);
  const prefix = `spellcast:${spellId}:`;
  await page.waitForFunction(value => [...document.querySelectorAll('#choices [data-choice]')].some(node => node.dataset.choice.startsWith(value)), prefix, { timeout: 5000 });
  const choiceIds = await page.locator('#choices [data-choice]').evaluateAll((nodes, value) => nodes.map(node => node.dataset.choice).filter(choice => choice.startsWith(value)), prefix);
  const candidates = choiceIds.map(choice => ({ choice, id: choice.slice(prefix.length), stack: battle.stacks.find(item => item.id === choice.slice(prefix.length)) })).filter(row => row.stack);
  const chooseByPriority = rows => rows.sort((a, b) => a.score - b.score || a.id.localeCompare(b.id))[0];
  let selected;
  if (spellId === 'cure') {
    selected = chooseByPriority(candidates.filter(row => row.stack.side === 'p').map(row => ({ ...row, score: poolHp(row.stack) - maximumPoolHp(row.stack) })));
  } else if (spellId === 'resurrect') {
    selected = candidates.find(row => row.stack.side === 'p' && row.stack.count < row.stack.maxCount);
  } else if (spellId === 'bless') {
    selected = candidates.find(row => row.stack.side === 'p' && (row.stack.blessCounter || 0) === 0);
  } else if (spellId === 'haste') {
    selected = candidates.find(row => row.stack.side === 'p' && (row.stack.hasteCounter || 0) === 0);
  } else if (spellId === 'slow') {
    selected = candidates.find(row => row.stack.side === 'e' && (row.stack.slowCounter || 0) === 0);
  } else if (spellId === 'fireball') {
    selected = chooseByPriority(candidates.filter(row => row.stack.side === 'e').map(row => ({ ...row, score: -battle.stacks.filter(item => item.side === 'e' && !item.dead && item.id !== row.id && Math.max(Math.abs(item.x - row.stack.x), Math.abs(item.y - row.stack.y)) <= 1).length })));
  } else selected = candidates.find(row => row.stack.side === 'e');
  if (!selected) throw new Error(`${spellId} had no legal visible target in ${context}; offers were ${choiceIds.join(', ')}.`);
  const before = { mana: battle.mana, round: battle.round, stacks: structuredClone(battle.stacks) };
  await click(`#choices [data-choice="${selected.choice}"]`, `Cast ${spellId} on visible target ${selected.id}`);
  let afterState = await snapshot();
  battle = afterState.battle;
  const logged = battle.log.some(entry => entry.type === 'spell' && entry.id === spellId && entry.targetId === selected.id);
  const beforeTarget = before.stacks.find(stack => stack.id === selected.id);
  const afterTarget = battle.stacks.find(stack => stack.id === selected.id);
  const damagedEnemies = before.stacks.filter(stack => stack.side === 'e').map(stack => {
    const current = battle.stacks.find(item => item.id === stack.id);
    return { id: stack.id, before: { count: stack.count, top: stack.top, dead: stack.dead }, after: { count: current?.count, top: current?.top, dead: current?.dead }, damaged: !current || current.dead || current.count < stack.count || poolHp(current) < poolHp(stack) };
  }).filter(row => row.damaged);
  const beforePool = poolHp(beforeTarget);
  const afterPool = poolHp(afterTarget);
  let effectPassed = false;
  if (['arrow', 'bolt', 'fireball'].includes(spellId)) effectPassed = damagedEnemies.length > 0;
  else if (spellId === 'bless') effectPassed = (afterTarget.blessCounter || 0) > (beforeTarget.blessCounter || 0);
  else if (spellId === 'haste') effectPassed = (afterTarget.hasteCounter || 0) > (beforeTarget.hasteCounter || 0);
  else if (spellId === 'slow') effectPassed = (afterTarget.slowCounter || 0) > (beforeTarget.slowCounter || 0);
  else if (spellId === 'cure') effectPassed = afterPool > beforePool;
  else if (spellId === 'resurrect') effectPassed = afterTarget.count > beforeTarget.count;
  assert.ok(logged, `${spellId} is recorded in the natural battle log.`);
  assert.ok(effectPassed, `${spellId} has its expected battlefield effect.`);
  const castRecord = {
    spellId, context, targetId: selected.id,
    before: { mana: before.mana, round: before.round, target: { count: beforeTarget.count, maxCount: beforeTarget.maxCount, top: beforeTarget.top, uhp: beforeTarget.uhp, blessCounter: beforeTarget.blessCounter, hasteCounter: beforeTarget.hasteCounter, slowCounter: beforeTarget.slowCounter }, enemyStacks: before.stacks.filter(stack => stack.side === 'e').map(stack => ({ id: stack.id, count: stack.count, top: stack.top, dead: stack.dead })) },
    after: { mana: battle.mana, round: battle.round, target: { count: afterTarget.count, maxCount: afterTarget.maxCount, top: afterTarget.top, uhp: afterTarget.uhp, blessCounter: afterTarget.blessCounter, hasteCounter: afterTarget.hasteCounter, slowCounter: afterTarget.slowCounter }, damagedEnemies, log: battle.log.filter(entry => entry.type === 'spell' && entry.id === spellId).at(-1) },
    effectPassed, reloadPersisted: false,
  };
  const panelClose = page.locator('#panel-close');
  if (await panelClose.isVisible()) await panelClose.click();
  await saveScreenshot(`natural-spell-${spellId}-cast`);
  await page.reload({ waitUntil: 'networkidle' });
  await page.waitForFunction(value => window.rebornSnapshot()?.battle?.log?.some(entry => entry.type === 'spell' && entry.id === value), spellId, { timeout: 10000 });
  const reloaded = await snapshot();
  const persistedTarget = reloaded.battle.stacks.find(stack => stack.id === selected.id);
  castRecord.reloadPersisted = reloaded.hero.skills.wisdom >= 3
    && reloaded.battle.log.some(entry => entry.type === 'spell' && entry.id === spellId && entry.targetId === selected.id)
    && reloaded.battle.mana === castRecord.after.mana
    && (['arrow', 'bolt', 'fireball'].includes(spellId)
      ? castRecord.after.damagedEnemies.every(row => { const current = reloaded.battle.stacks.find(stack => stack.id === row.id); return current && (current.dead === row.after.dead && current.count === row.after.count && current.top === row.after.top); })
      : spellId === 'bless' ? persistedTarget.blessCounter === castRecord.after.target.blessCounter
      : spellId === 'haste' ? persistedTarget.hasteCounter === castRecord.after.target.hasteCounter
      : spellId === 'slow' ? persistedTarget.slowCounter === castRecord.after.target.slowCounter
      : spellId === 'cure' ? poolHp(persistedTarget) >= afterPool
      : spellId === 'resurrect' ? persistedTarget.count >= castRecord.after.target.count
      : false);
  assert.ok(castRecord.reloadPersisted, `${spellId} effect and spell log survive reload.`);
  report.naturalSpellCasts.push(castRecord);
  return castRecord;
}
async function settleVisibleCampaignBattle(context) {
  let state = await snapshot();
  if (state.battle?.status === 'ACTIVE' && !state.battle.pendingSettlement) {
    await click('#dock [data-choice="auto"]', `Auto-resolve ${context} after the visible spell cast`);
    await page.waitForFunction(() => window.rebornSnapshot()?.battle?.pendingSettlement === true, null, { timeout: 15000 });
    state = await snapshot();
  }
  if (!state.battle?.pendingSettlement) throw new Error(`${context} did not reach a visible campaign result.`);
  const winner = state.battle.outcome?.winner;
  await click('#scene-ui [data-choice="result:tactical"]', `Settle ${context} through its result card`);
  await page.waitForFunction(() => window.rebornSnapshot()?.battle == null, null, { timeout: 10000 });
  const settled = await snapshot();
  if (winner !== 'p') throw new Error(`${context} ended ${winner || 'without a winner'}; campaign spell evidence cannot continue safely.`);
  if (settled.hero.offers.some(offer => !offer.chosen && !offer.declined)) await resolveVisibleSkillOffers();
  await spendAvailableKnowledgePoints();
  return { winner, mana: settled.hero.mana, level: settled.hero.level, wisdom: settled.hero.skills.wisdom, army: settled.army.map(stack => ({ id: stack.id, type: stack.type, count: stack.count })) };
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
    await spendAvailableKnowledgePoints();
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
      visibleSpellIds: await page.locator('#choices [data-choice^="spell:"]').evaluateAll(nodes => nodes.map(node => node.dataset.choice.slice('spell:'.length)).sort()),
    };
    await saveScreenshot('earned-wisdom3-spellbook');

    await click('[data-choice="nav:war"]', 'War navigation for natural spell battles');
    for (const spellId of ['arrow', 'bless', 'haste', 'slow', 'bolt', 'fireball']) {
      const campaign = await snapshot();
      if (campaign.hero.mana < spellCosts[spellId]) throw new Error(`Natural campaign mana ${campaign.hero.mana} cannot pay for ${spellId} (${spellCosts[spellId]}).`);
      await click('[data-choice="start-duel"]', `Start natural campaign duel for ${spellId}`);
      await page.waitForFunction(() => {
        const current = window.rebornSnapshot()?.battle;
        if (current?.status !== 'ACTIVE' || current.castThisRound) return false;
        const actorId = current.queue.find(id => { const stack = current.stacks.find(item => item.id === id); return stack && !stack.dead && !stack.acted; });
        return current.stacks.find(stack => stack.id === actorId)?.side === 'p';
      }, null, { timeout: 10000 });
      const cast = await castVisibleNaturalSpell(spellId, `campaign Tactical Duel ${spellId}`);
      cast.settlement = await settleVisibleCampaignBattle(`campaign Tactical Duel ${spellId}`);
    }

    report.naturalGuardAttempts = [];
    for (let attempt = 0; attempt < 6 && (!report.cureCastPassed || !report.resurrectionCastPassed); attempt++) {
      await startNaturalGuardBattle();
      const guardRecord = { attempt: attempt + 1, encounter: structuredClone(report.naturalGuard), playerActions: [] };
      report.naturalGuardAttempts.push(guardRecord);
      let battle = await snapshot();
      for (let actionIndex = 0; actionIndex < 100; actionIndex++) {
        const current = battle.battle;
        if (!current || current.status !== 'ACTIVE' || current.pendingSettlement) break;
        const actor = currentActor(current);
        const allies = current.stacks.filter(stack => stack.side === 'p' && !stack.dead && stack.count > 0);
        const damaged = allies.filter(stack => poolHp(stack) < maximumPoolHp(stack));
        const casualty = allies.find(stack => stack.count < stack.maxCount);
        if (actor?.side === 'p' && !current.castThisRound && !report.cureCastPassed && damaged.length) {
          const cast = await castVisibleNaturalSpell('cure', `natural guard encounter ${attempt + 1} after battlefield damage`);
          report.cureCastPassed = cast.effectPassed && cast.reloadPersisted;
          report.cureBefore = cast.before;
          report.cureAfter = cast.after;
          guardRecord.cure = cast;
          battle = await snapshot();
          continue;
        }
        if (actor?.side === 'p' && !current.castThisRound && report.cureCastPassed && !report.resurrectionCastPassed && casualty) {
          const cast = await castVisibleNaturalSpell('resurrect', `natural guard encounter ${attempt + 1} after casualty loss`);
          report.resurrectionCastPassed = cast.effectPassed && cast.reloadPersisted;
          report.resurrectionBefore = { target: cast.before.target, mana: cast.before.mana, round: cast.before.round };
          report.resurrectionAfter = { target: cast.after.target, mana: cast.after.mana, spellLog: cast.after.log };
          report.resurrectionReload = { spellPersisted: cast.reloadPersisted, mana: cast.after.mana, target: cast.after.target, casualtyRestoredPersisted: cast.reloadPersisted && cast.after.target.count > cast.before.target.count };
          guardRecord.resurrection = cast;
          battle = await snapshot();
          continue;
        }
        if (actor?.side === 'p') {
          await click('#dock [data-choice="defend"]', 'Defend with the current stack to allow natural guard actions');
          guardRecord.playerActions.push({ round: current.round, action: 'defend', stackId: actor.id, wounded: damaged.map(stack => ({ id: stack.id, count: stack.count, maxCount: stack.maxCount, top: stack.top, uhp: stack.uhp })) });
        } else await wait(100);
        battle = await snapshot();
      }
      const current = await snapshot();
      if (current.battle?.pendingSettlement || current.battle?.status === 'ACTIVE') {
        guardRecord.settlement = await settleVisibleCampaignBattle(`natural guard encounter ${attempt + 1}`);
        report.finalCampaignAfterSettlement = { ...guardRecord.settlement, adventure: { pendingEncounter: (await snapshot()).adventure?.pendingEncounter, resolvedGuards: (await snapshot()).adventure?.resolvedGuards } };
      }
    }
    if (!report.cureCastPassed) report.cureBlocker = 'No natural guard battle exposed a wounded living stack with a visible Cure opportunity before settlement.';
    if (!report.resurrectionCastPassed) report.resurrectionBlocker = 'No natural guard battle produced a living casualty stack for visible Resurrection before the bounded encounter attempts ended.';
  }

  const expectedSpells = ['arrow', 'bless', 'haste', 'cure', 'slow', 'bolt', 'fireball', 'resurrect'];
  report.naturalSpellCoverage = Object.fromEntries(expectedSpells.map(spellId => {
    const casts = report.naturalSpellCasts.filter(row => row.spellId === spellId);
    return [spellId, { count: casts.length, effect: casts.some(row => row.effectPassed), reload: casts.some(row => row.reloadPersisted) }];
  }));
  report.passed = report.progressionAtStop.wisdom >= 3 && report.wisdomReload?.after.wisdom === 3
    && report.spellbook?.resurrectionVisible === true && expectedSpells.every(spellId => report.naturalSpellCoverage[spellId].count >= 1 && report.naturalSpellCoverage[spellId].effect && report.naturalSpellCoverage[spellId].reload)
    && report.errors.length === 0;
} catch (error) {
  report.failure = String(error?.stack || error);
} finally {
  try { await fs.writeFile(path.join(output, 'report.json'), `${JSON.stringify(report, null, 2)}\n`, 'utf8'); }
  finally { await context.close(); await browser.close(); }
}

console.log(JSON.stringify({ output: path.relative(root, output), passed: report.passed, stopReason: report.stopReason, progressionAtStop: report.progressionAtStop, battleCount: report.battles.length, skillSelections: report.skillSelections, naturalSpellCoverage: report.naturalSpellCoverage, errors: report.errors, failure: report.failure }, null, 2));
if (!report.passed) process.exitCode = 1;
