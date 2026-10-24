import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import contract from '../../../src/data/implementation-contract.json' with { type: 'json' };
import data from '../../../src/data/reference-data.json' with { type: 'json' };
import worlds from '../../../src/data/adventure-worlds.json' with { type: 'json' };
import { cost, heroStats, manaMax, rates } from '../../../src/core/campaign.js';
import { agePrice, forgeOffer, recruitCost, towerPurchaseCost } from '../../../src/core/rules.js';
import { towerStats, unitStats } from '../../../src/core/mechanics.js';
import { bodyHasHeldWeapon, heroBody } from '../../../src/client/hero-room.js';

const root = process.cwd();
const out = path.join(root, 'qa/game-completion-20261021/visual-review/army-showcase-live-20261021');
await fs.mkdir(out, { recursive: true });
const report = {
  recordedAt: new Date().toISOString(),
  classification: 'NATURAL_UI_CAMPAIGN_CONTROLLED_BROWSER_CLOCK',
  journey: 'new campaign -> naturally resolve each age-gated story chapter and the Future conclusion -> build four income sites, Armory and Barracks -> forge/equip one legal age weapon and recruit one current-age formation in each of eight ages -> inspect Hero/Army -> pay each age gate -> capture Kingdom/Army/Adventure -> save/reload Future -> build Siege Workshop -> buy and field four age-appropriate tower families -> survive Endless -> claim Q6 exactly once',
  url: 'http://127.0.0.1:4179/?audit=1',
  note: 'All construction, age advancement, map entry, and save actions use visible game controls. Playwright fast-forwards only idle elapsed time to verify legal production and construction; no campaign state or resources are injected. Adventure is entered in Stone and its age-specific visible terrain is captured at every legal age transition.',
  errors: [],
  ages: [],
  storyChapters: [],
  futureConclusion: null,
  armyAgePresentations: [],
  armyRecruits: [],
  weapons: [],
  screenshots: [],
};
const browser = await chromium.launch({
  executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe',
  headless: true,
});
const context = await browser.newContext({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1 });
const page = await context.newPage();
await page.clock.install();
page.on('pageerror', error => report.errors.push(String(error)));
page.on('console', message => { if (message.type() === 'error') report.errors.push(message.text()); });
page.on('response', response => { if (response.status() >= 400) report.errors.push('HTTP ' + response.status() + ' ' + response.url()); });

const read = () => page.evaluate(() => JSON.parse(document.querySelector('#audit-snapshot')?.textContent || 'null'));
async function clickChoice(id) {
  const control = page.locator('[data-choice="' + id + '"]').first();
  await control.waitFor({ state: 'visible', timeout: 10000 });
  assert.equal(await control.isDisabled(), false, id + ' is enabled');
  await control.click();
}
async function waitForState(predicate, label, timeoutSteps = 100) {
  for (let step = 0; step < timeoutSteps; step += 1) {
    const snapshot = await read();
    if (snapshot?.state && predicate(snapshot.state)) return snapshot.state;
    await page.clock.runFor(250);
  }
  throw new Error('Timed out waiting for ' + label);
}
async function clearInspector() {
  const close = page.locator('#panel-close');
  if (await close.isVisible().catch(() => false)) await close.click();
}
async function clearSceneSelection() {
  await clearInspector();
  const target = page.locator('#world');
  const bounds = await target.boundingBox();
  assert.ok(bounds, 'Kingdom world has a visible canvas');
  if (await page.locator('#world .plot.selected').count() === 0) return;
  for (const y of [0.45, 0.52, 0.6, 0.4, 0.3, 0.7]) {
    for (const x of [0.92, 0.08, 0.85, 0.15, 0.78, 0.22, 0.5]) {
      await page.mouse.click(bounds.x + bounds.width * x, bounds.y + bounds.height * y);
      if (await page.locator('#world .plot.selected').count() === 0) return;
      await clearInspector();
    }
  }
  throw new Error('Could not clear the selected-site outline on the Kingdom canvas');
}
async function scrollElementIntoPanel(panelSelector, targetSelector, label) {
  const panel = page.locator(panelSelector);
  let adjustments = 0;
  const measure = () => page.evaluate(({ panelSelector, targetSelector }) => {
    const panel = document.querySelector(panelSelector);
    const target = document.querySelector(targetSelector);
    if (!panel || !target) return null;
    const panelBounds = panel.getBoundingClientRect();
    const bounds = target.getBoundingClientRect();
    return {
      panelBounds: { top: panelBounds.top, bottom: panelBounds.bottom, height: panelBounds.height },
      bounds: { top: bounds.top, bottom: bounds.bottom, height: bounds.height },
      scrollTop: panel.scrollTop,
      scrollHeight: panel.scrollHeight,
      clientHeight: panel.clientHeight,
      fullyInPanel: bounds.top >= panelBounds.top && bounds.bottom <= panelBounds.bottom,
    };
  }, { panelSelector, targetSelector });
  // Viewport changes can trigger a delayed scene-fit pass. Wait for it before
  // treating the current scroll position as final.
  await page.waitForTimeout(150);
  for (let attempt = 0; attempt < 12; attempt += 1) {
    const geometry = await measure();
    if (!geometry) throw new Error(`${label} target or panel is missing`);
    if (geometry.fullyInPanel) {
      // Recheck after layout settles so resize-driven geometry changes cannot
      // produce a false visible result.
      await page.waitForTimeout(120);
      const settled = await measure();
      if (settled?.fullyInPanel) return { ...settled, adjustments, method: 'visible-panel-scroll-position' };
    }
    const delta = geometry.bounds.bottom > geometry.panelBounds.bottom
      ? geometry.bounds.bottom - geometry.panelBounds.bottom + 6
      : geometry.bounds.top - geometry.panelBounds.top - 6;
    await panel.evaluate((element, amount) => {
      const maximum = Math.max(0, element.scrollHeight - element.clientHeight);
      element.scrollTop = Math.max(0, Math.min(maximum, element.scrollTop + amount));
    }, delta);
    adjustments += 1;
    await page.waitForTimeout(100);
  }
  throw new Error(`${label} did not scroll into its visible panel: ${JSON.stringify(await page.evaluate(({ panelSelector, targetSelector }) => {
    const panel = document.querySelector(panelSelector);
    const target = document.querySelector(targetSelector);
    const p = panel?.getBoundingClientRect();
    const t = target?.getBoundingClientRect();
    return { scrollTop: panel?.scrollTop, scrollHeight: panel?.scrollHeight, clientHeight: panel?.clientHeight, panel: p && { top: p.top, bottom: p.bottom }, target: t && { top: t.top, bottom: t.bottom } };
  }, { panelSelector, targetSelector }))}`);
}
function defensePointAt(progress) {
  const lane = contract.geometry.defense.lane;
  const clamped = Math.max(0, Math.min(lane.length - 1, progress));
  const index = Math.floor(clamped);
  const next = Math.min(lane.length - 1, index + 1);
  const t = clamped - index;
  return [lane[index][0] + (lane[next][0] - lane[index][0]) * t, lane[index][1] + (lane[next][1] - lane[index][1]) * t];
}
function bestDefenseBlast(state) {
  const defense = state.defense;
  if (!defense?.heroDeployed || defense.heroHp <= 0 || state.hero.mana < 40) return null;
  const damage = heroStats(state, data).pow * 4 + state.hero.level * 6;
  const enemies = defense.queue.filter(enemy => enemy.spawned && enemy.hp > 0 && !enemy.leaked)
    .map(enemy => ({ ...enemy, point: defensePointAt(enemy.progress) }));
  let best = null;
  for (let y = 0; y < contract.geometry.defense.rows; y += 1) {
    for (let x = 0; x < contract.geometry.defense.cols; x += 1) {
      const center = [x + 0.5, y + 0.5];
      const hits = enemies.filter(enemy => Math.hypot(enemy.point[0] - center[0], enemy.point[1] - center[1]) <= 1.6);
      const effectiveDamage = hits.reduce((sum, enemy) => sum + Math.min(damage, enemy.hp), 0);
      const kills = hits.filter(enemy => enemy.hp <= damage).length;
      const score = effectiveDamage + kills * 2;
      if (!best || score > best.score || (score === best.score && hits.length > best.hits.length)) {
        best = { x, y, center, hits, damage, effectiveDamage, kills, score };
      }
    }
  }
  return best && (best.hits.length >= 2 || best.kills > 0 || best.hits.some(enemy => enemy.boss)) ? best : null;
}
async function waitForResources(required, label) {
  const ageCapsHours = [8, 7, 6, 5, 4, 3.5, 3, 3];
  for (let step = 0; step < 100; step += 1) {
    const state = (await read())?.state;
    assert.ok(state, 'campaign exists before ' + label);
    const short = Object.entries(required).filter(([key, value]) => state.resources[key] + 1e-6 < value);
    if (!short.length) return state;
    const income = rates(state);
    const waits = short.map(([key, value]) => {
      assert.ok(income[key] > 0, 'a legal producer supplies ' + key + ' for ' + label);
      return (value - state.resources[key]) / income[key];
    });
    const neededMs = Math.max(1000, Math.ceil(Math.max(...waits) * 1000) + 500);
    const capMs = Math.floor(ageCapsHours[state.age] * 3600000);
    const elapsed = Math.min(neededMs, capMs);
    await page.clock.fastForward(elapsed);
    await page.waitForTimeout(30);
  }
  throw new Error('Could not earn resources for ' + label + ': ' + JSON.stringify(required));
}
async function beginBuild(choice, payment, label) {
  await waitForResources(payment, label);
  await clickChoice(choice);
  await page.locator('#build-commit').waitFor({ state: 'visible', timeout: 10000 });
  await page.locator('#build-commit').click();
}
async function buildAt(siteId, building) {
  await clearInspector();
  await page.locator('#context').click();
  await clickChoice('site-list');
  await clickChoice('choose-site:' + siteId);
  await clickChoice('build-picker:' + siteId);
  await beginBuild('build:' + siteId + ':' + building, cost(data, building, 0), building + ' at ' + siteId);
  await waitForState(state => state.buildJobs.some(job => job.plotId === siteId && job.type === building), building + ' construction start');
  await page.clock.fastForward(10000);
  await page.waitForTimeout(30);
  return waitForState(state => state.plots.some(plot => plot.id === siteId && plot.type === building && plot.level === 1)
    && !state.buildJobs.some(job => job.plotId === siteId), building + ' completion');
}
async function buildSiteToLevel(siteId, building, targetLevel) {
  let state = (await read()).state;
  while ((state.plots.find(plot => plot.id === siteId)?.level || 0) < targetLevel) {
    const level = state.plots.find(plot => plot.id === siteId)?.level || 0;
    const payment = cost(data, building, level);
    await clearInspector();
    await page.locator('#context').click();
    await clickChoice('site-list');
    await clickChoice('choose-site:' + siteId);
    await beginBuild(`build:${siteId}:${building}`, payment, `${building} level ${level + 1} at ${siteId}`);
    await waitForState(value => value.buildJobs.some(job => job.plotId === siteId && job.type === building), `${building} level ${level + 1} scaffold`);
    await page.clock.fastForward(10000);
    await page.waitForTimeout(30);
    state = await waitForState(value => value.plots.find(plot => plot.id === siteId)?.level === level + 1
      && !value.buildJobs.some(job => job.plotId === siteId), `${building} level ${level + 1}`);
  }
  return state;
}
async function recruitOneFormationPerAge(age) {
  const roleByAge = ['heavy', 'melee', 'ranged', 'heavy', 'melee', 'ranged', 'heavy', 'melee'];
  const role = roleByAge[age];
  assert.ok(role, 'each of the eight campaign ages has an assigned natural roster selection');
  const before = (await read()).state;
  assert.equal(before.age, age, 'recruit uses the currently reached campaign age');
  assert.equal(before.plots.find(plot => plot.id === 'P06')?.type, 'barracks', 'a legal Barracks exists on its reserved site');
  assert.ok(before.plots.find(plot => plot.id === 'P06').level >= age + 1, 'Barracks level expands capacity before each age recruit');
  assert.ok(!before.army.some(stack => stack.kind === 'role' && stack.age === age && stack.type === role), 'age-specific formation is a new stack');
  const payment = recruitCost(data, role, age);
  await waitForResources(payment, `${data.AGES[age].n} ${data.ROLES[role].n} recruitment`);
  if (await page.locator('#app[data-view="army"]').count() === 0) {
    await page.locator('[data-choice="nav:army"]').first().click();
    await page.locator('#app[data-view="army"]').waitFor({ state: 'attached', timeout: 10000 });
  }
  await clickChoice(`catalog:${age}-${role}`);
  const recruit = page.locator(`[data-choice="muster-recruit:${role}"]`).first();
  await recruit.waitFor({ state: 'visible', timeout: 10000 });
  assert.equal(await recruit.isDisabled(), false, `${data.AGES[age].n} recruitment is enabled after legal payment and capacity checks`);
  await recruit.click();
  const recruited = await waitForState(state => state.age === age
    && state.army.some(stack => stack.kind === 'role' && stack.age === age && stack.type === role && stack.count === 5), `${data.AGES[age].n} ${data.ROLES[role].n} formation`);
  const stack = recruited.army.find(entry => entry.kind === 'role' && entry.age === age && entry.type === role);
  report.armyRecruits.push({ age, ageName: data.AGES[age].n, role, roleName: data.ROLES[role].names[age], stackId: stack.id, count: stack.count, barracksLevel: recruited.plots.find(plot => plot.id === 'P06').level, capacity: 2 + recruited.plots.find(plot => plot.id === 'P06').level, resourcesAfterPayment: { ...recruited.resources } });
}
async function buildHall(targetLevel) {
  let state = (await read()).state;
  while (state.plots.find(plot => plot.id === 'townhall').level < targetLevel) {
    const level = state.plots.find(plot => plot.id === 'townhall').level;
    const payment = cost(data, 'townhall', level);
    await clearInspector();
    await page.locator('#context').click();
    await clickChoice('site-list');
    await clickChoice('choose-site:townhall');
    await beginBuild('build:townhall:townhall', payment, 'Town Hall level ' + (level + 1));
    await waitForState(value => value.buildJobs.some(job => job.plotId === 'townhall'), 'Town Hall scaffold');
    await page.clock.fastForward(10000);
    await page.waitForTimeout(30);
    state = await waitForState(value => value.plots.find(plot => plot.id === 'townhall').level === level + 1
      && !value.buildJobs.some(job => job.plotId === 'townhall'), 'Town Hall level ' + (level + 1));
  }
  return state;
}
async function buildWall(targetLevel, age) {
  let state = (await read()).state;
  while (state.walls.level < targetLevel) {
    const level = state.walls.level;
    const payment = cost(data, 'walls', level);
    await clearInspector();
    await clickChoice('kingdom-actions-open');
    await beginBuild('build:walls', payment, 'Walls level ' + (level + 1) + ' in ' + data.AGES[age].n);
    state = await waitForState(value => value.buildJobs.some(job => job.plotId === 'walls'), 'wall scaffold');
    const scaffold = await sceneState();
    assert.equal(scaffold.wallPhase, 'scaffold', 'wall construction renders its same-age scaffold');
    report.ages[age].wallPhases.push(scaffold);
    report.screenshots.push(await captureScene('age-' + age + '-wall-scaffold', ['1280x720']));
    await page.clock.fastForward(10000);
    await page.waitForTimeout(30);
    state = await waitForState(value => value.walls.level === level + 1
      && !value.buildJobs.some(job => job.plotId === 'walls'), 'Walls level ' + (level + 1));
    const completed = await sceneState();
    report.ages[age].wallPhases.push(completed);
    report.screenshots.push(await captureScene('age-' + age + '-wall-level-' + (level + 1), ['1280x720']));
  }
  return state;
}
async function sceneState() {
  await page.waitForTimeout(40);
  return page.evaluate(() => {
    const terrain = document.querySelector('#terrain');
    const wall = document.querySelector('#world [data-walls-phase]');
    const rendered = [...document.querySelectorAll('#world image[aria-label]')].map(image => {
      const box = image.getBBox();
      return { label: image.getAttribute('aria-label'), href: image.getAttribute('href'), box: [box.x, box.y, box.width, box.height].map(value => Math.round(value * 10) / 10) };
    });
    return {
      view: document.querySelector('#app')?.dataset.view,
      terrainStatus: terrain?.dataset.terrainStatus,
      terrain: terrain?.getAttribute('src'),
      terrainLoaded: Boolean(terrain?.complete && terrain?.naturalWidth > 0),
      wallPhase: wall?.getAttribute('data-walls-phase'),
      wallLevel: Number(wall?.getAttribute('data-walls-level')),
      wallKind: wall?.getAttribute('data-walls-kind'),
      wallPainting: wall?.getAttribute('data-walls-painting'),
      wallStamps: Number(wall?.getAttribute('data-wall-stamps')),
      renderedBuildings: rendered,
    };
  });
}
async function captureScene(name, sizes) {
  await clearSceneSelection();
  const records = [];
  for (const size of sizes) {
    const [width, height] = size.split('x').map(Number);
    await page.setViewportSize({ width, height });
    await page.waitForTimeout(100);
    const file = path.join(out, name + '-' + size + '.png');
    await page.screenshot({ path: file });
    records.push({ name, size, file: path.relative(root, file) });
  }
  return { scene: await sceneState(), captures: records };
}
async function openStoryChronicle() {
  await page.locator('#context').click();
  await clickChoice('menu:story');
  await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'story');
  if (!(await read()).state.story.rival) await clickChoice('journal-rival:Varek Iron-Eye');
  const chronicle = page.locator('#scene-ui [data-choice="journal:chronicle"]');
  if (await chronicle.count()) await chronicle.click();
}
async function resolveAgeStoryChapter(index) {
  const before = (await read()).state;
  assert.equal(before.age, index, `Chapter ${index + 1} opens at its campaign age`);
  assert.equal(before.story.chapter, index, `Chapter ${index + 1} is the next earned chapter`);
  await openStoryChronicle();
  const visual = await page.evaluate(() => {
    const host = document.querySelector('#scene-ui');
    const art = [...document.querySelectorAll('#world image')].map(node => node.getAttribute('href') || '')
      .find(href => href.includes('supporting-chapter') || href.includes('story-chapter-')) || '';
    return {
      narrative: host?.querySelector('p[data-conclusion]')?.textContent?.trim() || '',
      decisions: [...(host?.querySelectorAll('.journal-decisions button') || [])].map(node => node.textContent.trim()),
      backdrop: art,
    };
  });
  const expectedBackdrop = index === 3
    ? 'assets/derivatives/visual-repair-20261020/scenes/story-chapter-4-divided-gate-v2.png'
    : `assets/production/production-12-20261003/images/${String(index + 1).padStart(2, '0')}-supporting-chapter-${index + 1}.png`;
  assert.equal(visual.backdrop, expectedBackdrop, `${data.AGES[index].n} story scene binds its chapter artwork`);
  assert.equal(visual.decisions.length, data.STORY[index].ch.length, `Chapter ${index + 1} shows its real choices`);
  const chapterCaptures = [];
  if (index === 3) {
    for (const size of ['825x375', '1280x720']) {
      const [width, height] = size.split('x').map(Number);
      await page.setViewportSize({ width, height });
      await page.waitForTimeout(120);
      const file = path.join(out, `story-chapter-4-divided-gate-${size}.png`);
      await page.screenshot({ path: file });
      chapterCaptures.push({ size, file: path.relative(root, file) });
    }
    await page.setViewportSize({ width: 1280, height: 720 });
  }
  const choice = data.STORY[index].ch[0];
  await clickChoice('journal-choice:0');
  const after = await waitForState(state => state.story.chapter === index + 1, `resolve Chapter ${index + 1}`);
  const elapsedMs = after.clock - before.clock;
  const actualReward = {};
  for (const resource of ['food', 'wood', 'stone', 'gold']) {
    const delta = after.resources[resource] - before.resources[resource] - rates(before)[resource] * elapsedMs / 1000;
    actualReward[resource] = delta;
    assert.ok(Math.abs(delta - (choice.fx?.[resource] || 0)) < 1e-6, `Chapter ${index + 1} pays its exact ${resource} choice reward once`);
  }
  report.storyChapters.push({ index, age: before.age, ageName: data.AGES[before.age].n, title: data.STORY[index].t, narrative: visual.narrative, backdrop: visual.backdrop, chosen: choice.flag, expectedReward: choice.fx || {}, actualReward, captures: chapterCaptures });
  await page.locator('[data-choice="nav:kingdom"]').first().click();
  await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'kingdom');
}
async function acknowledgeFutureConclusion() {
  const before = (await read()).state;
  assert.equal(before.age, 7, 'Future conclusion is tested in Future age');
  assert.equal(before.story.chapter, data.STORY.length, 'all seven story choices precede the conclusion');
  assert.equal(before.story.futureSeen, false, 'the Future conclusion is still available');
  await openStoryChronicle();
  const conclusion = await page.locator('#scene-ui p[data-conclusion="open"]').textContent();
  assert.match(conclusion || '', /The Valley We Keep/);
  const captures = [];
  for (const size of ['825x375', '1280x720']) {
    const [width, height] = size.split('x').map(Number);
    await page.setViewportSize({ width, height });
    await page.waitForTimeout(100);
    const file = path.join(out, `story-future-conclusion-${size}.png`);
    await page.screenshot({ path: file });
    captures.push({ size, file: path.relative(root, file) });
  }
  await page.setViewportSize({ width: 1280, height: 720 });
  await clickChoice('journal-keep-valley');
  const after = await waitForState(state => state.story.futureSeen, 'acknowledge The Valley We Keep');
  const elapsedMs = after.clock - before.clock;
  const resourceDelta = Object.fromEntries(['food', 'wood', 'stone', 'gold'].map(resource => [
    resource,
    after.resources[resource] - before.resources[resource] - rates(before)[resource] * elapsedMs / 1000,
  ]));
  assert.ok(Object.values(resourceDelta).every(value => Math.abs(value) < 1e-6), 'acknowledging the Future conclusion grants no resources');
  report.futureConclusion = { title: 'The Valley We Keep', acknowledged: true, resourceDelta, captures };
  await page.locator('[data-choice="nav:kingdom"]').first().click();
  await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'kingdom');
}
async function captureArmyAge(age) {
  const ageKeys = ['stone', 'bronze', 'iron', 'medieval', 'gunpowder', 'industrial', 'modern', 'future'];
  assert.equal((await read()).state.age, age, 'Army review uses the naturally reached campaign age');
  if (await page.locator('#app[data-view="army"]').count() === 0) {
    await page.locator('[data-choice="nav:army"]').first().click();
    await page.locator('#app[data-view="army"]').waitFor({ state: 'attached', timeout: 10000 });
  }
  await page.waitForTimeout(300);
  const presentation = await page.evaluate(() => {
    const board = document.querySelector('#board');
    const rect = node => {
      const value = node?.getBoundingClientRect();
      return value ? { left: value.left, top: value.top, right: value.right, bottom: value.bottom, width: value.width, height: value.height } : null;
    };
    const intersects = (a, b) => Boolean(a && b && a.left < b.right && a.right > b.left && a.top < b.bottom && a.bottom > b.top);
    const roster = board?.querySelector('[data-army-row="roster"]');
    const recruitment = board?.querySelector('[data-army-row="review"]');
    const inspector = board?.querySelector('.roster-inspector');
    const focusedFormation = roster?.querySelector('.board-card[data-roster-focus="true"]');
    const recruitmentRect = rect(recruitment);
    const rosterRect = rect(roster);
    const inspectorRect = rect(inspector);
    const focusedFormationRect = rect(focusedFormation);
    return {
      view: document.querySelector('#app')?.dataset.view,
      age: JSON.parse(document.querySelector('#audit-snapshot')?.textContent || 'null')?.state?.age,
      backdrop: board?.dataset.armyGround || '',
      rosterCount: roster?.querySelectorAll('[data-stack-caption]').length || 0,
      rosterCardCount: roster?.querySelectorAll('.board-card').length || 0,
      focusedFormation: focusedFormation?.querySelector('[data-stack-caption]')?.getAttribute('data-stack-caption') || '',
      focusedFormationVisibleOnOpen: Boolean(rosterRect && focusedFormationRect && focusedFormationRect.left >= rosterRect.left - 1 && focusedFormationRect.right <= rosterRect.right + 1),
      rosterLabel: board?.querySelector('.roster-capacity')?.textContent?.trim() || '',
      selectedRecruitTitle: board?.querySelector('.roster-inspector h2')?.textContent?.trim() || '',
      recruitLabel: board?.querySelector('.army-recruitment-kicker')?.textContent?.trim() || '',
      showcase: [...(board?.querySelectorAll('.army-showcase-unit') || [])].map(node => {
        const image = node.querySelector('img');
        return {
          role: node.dataset.armyShowcaseRole || '',
          label: node.textContent?.trim() || '',
          accessibleName: node.getAttribute('aria-label') || '',
          image: image?.getAttribute('src') || '',
          imageLoaded: Boolean(image?.complete && image?.naturalWidth > 0),
          rect: rect(node),
        };
      }),
      showcaseRect: rect(board?.querySelector('.army-showcase')),
      cards: [...(recruitment?.querySelectorAll('[data-plate-review]') || [])].map(node => {
        const card = node.closest('.board-card') || node;
        const image = card.querySelector('img');
        return {
          key: node.getAttribute('data-plate-review'),
          label: node.textContent?.trim() || '',
          image: image?.getAttribute('src') || '',
          imageLoaded: Boolean(image?.complete && image?.naturalWidth > 0),
          rect: rect(card),
        };
      }),
      inspector: rect(inspector),
      layout: {
        documentWidth: document.documentElement.scrollWidth,
        viewportWidth: innerWidth,
        rosterOverlapsRecruitment: intersects(rosterRect, recruitmentRect),
        inspectorOverlapsRoster: intersects(inspectorRect, rosterRect),
        inspectorOverlapsRecruitment: intersects(inspectorRect, recruitmentRect),
      },
    };
  });
  assert.equal(presentation.view, 'army', 'Army scene is active');
  assert.equal(presentation.age, age, 'Army scene shows the current campaign age');
  assert.equal(presentation.backdrop, `assets/derivatives/professional-20261018/army/army-${ageKeys[age]}-muster-v1.png`, 'Army backdrop matches the reached age');
  assert.match(presentation.rosterLabel, /Your army · \d+ \/ \d+ formations/, 'capacity remains legible in the formation roster');
  assert.equal(presentation.focusedFormationVisibleOnOpen, true, 'the current formation is fully visible when the Army screen opens');
  assert.equal(presentation.recruitLabel, `Recruitment · ${data.AGES[age].n}`, 'recruitment cards use the current age');
  const expectedArmyCount = age + 3;
  assert.equal(presentation.rosterCount, expectedArmyCount, 'a new age-appropriate role formation has joined the existing army');
  assert.equal(presentation.rosterLabel, `Your army · ${expectedArmyCount} / ${expectedArmyCount} formations`, 'the expanded formation capacity matches the naturally recruited army');
  assert.equal(presentation.selectedRecruitTitle, data.ROLES[report.armyRecruits[age].role].names[age], 'the current-age recruit remains selected in its inspector');
  assert.deepEqual(presentation.cards.map(card => card.key), ['' + age + '-melee', '' + age + '-ranged', '' + age + '-heavy'], 'all three age-specific role options are present');
  assert.deepEqual(presentation.showcase.map(unit => unit.role), ['melee', 'ranged', 'heavy'], 'the scene shows one current-age formation for each army role');
  assert.ok(presentation.showcase.every(unit => unit.image && unit.imageLoaded && unit.label && unit.accessibleName.includes(unit.label)), `all muster figures have loaded age-specific art, a caption and an accessible name: ${JSON.stringify(presentation.showcase)}`);
  assert.ok(presentation.showcase.every(unit => unit.rect && presentation.showcaseRect && unit.rect.left >= presentation.showcaseRect.left && unit.rect.right <= presentation.showcaseRect.right && unit.rect.top >= presentation.showcaseRect.top && unit.rect.bottom <= presentation.showcaseRect.bottom), 'all selectable figures stay inside the muster scene');
  report.armyAgePresentations.push(presentation);
  assert.ok(presentation.cards.every(card => card.image && card.imageLoaded && card.label), `all age-specific role cards show loaded art and readable captions: ${JSON.stringify(presentation.cards)}`);
  assert.equal(presentation.layout.rosterOverlapsRecruitment, false, 'formation row does not overlap recruitment row');
  assert.equal(presentation.layout.inspectorOverlapsRoster, false, 'formation inspector does not cover the roster');
  assert.equal(presentation.layout.inspectorOverlapsRecruitment, true, 'age-specific recruitment options are contained in the inspector column');
  presentation.viewportLayouts = [];
  for (const size of ['825x375', '933x424', '1280x720']) {
    const [width, height] = size.split('x').map(Number);
    await page.setViewportSize({ width, height });
    await page.waitForTimeout(100);
    const currentLayout = await page.evaluate(() => {
      const row = document.querySelector('#board [data-army-row="roster"]');
      const rect = node => {
        const value = node?.getBoundingClientRect();
        return value ? { left: value.left, right: value.right, width: value.width } : null;
      };
      const rowRect = rect(row);
      const cards = [...(row?.querySelectorAll('[data-stack-caption]') || [])].map(label => label.closest('.board-card'));
      const openScrollLeft = row?.scrollLeft || 0;
      const selectedCard = row?.querySelector('.board-card[data-roster-focus="true"]');
      const selectedAtOpen = rect(selectedCard);
      const selectedFormationVisible = Boolean(rowRect && selectedAtOpen && selectedAtOpen.left >= rowRect.left - 1 && selectedAtOpen.right <= rowRect.right + 1);
      if (row) row.scrollLeft = 0;
      const startRowRect = rect(row);
      const firstAtStart = rect(cards[0]);
      const firstFormationAccessible = Boolean(startRowRect && firstAtStart && firstAtStart.left >= startRowRect.left - 1 && firstAtStart.right <= startRowRect.right + 1);
      const dockButton = document.querySelector('#dock [data-choice="inspect:army"]')?.getBoundingClientRect();
      const firstCardAtStart = cards[0]?.getBoundingClientRect();
      const dockOverlapsFirstFormation = Boolean(dockButton && firstCardAtStart
        && dockButton.left < firstCardAtStart.right && dockButton.right > firstCardAtStart.left
        && dockButton.top < firstCardAtStart.bottom && dockButton.bottom > firstCardAtStart.top);
      const clientWidth = row?.clientWidth || 0;
      const scrollWidth = row?.scrollWidth || 0;
      const hasFormationOverflow = scrollWidth > clientWidth + 1;
      const scrollLeftAtStart = openScrollLeft;
      if (hasFormationOverflow) row.scrollLeft = scrollWidth;
      const rowAtEnd = rect(row);
      const lastAtEnd = rect(cards.at(-1));
      const lastFormationAccessible = Boolean(rowAtEnd && lastAtEnd && lastAtEnd.left >= rowAtEnd.left - 1 && lastAtEnd.right <= rowAtEnd.right + 1);
      const maxScrollLeft = row ? row.scrollLeft : 0;
      if (row) row.scrollLeft = openScrollLeft;
      const scene = document.querySelector('#board .army-showcase')?.getBoundingClientRect();
      const inspector = document.querySelector('#board .roster-inspector')?.getBoundingClientRect();
      const figures = [...(document.querySelectorAll('#board .army-showcase-unit') || [])].map(node => {
        const box = node.getBoundingClientRect();
        return { left: box.left, right: box.right, top: box.top, bottom: box.bottom };
      });
      const figuresInsideScene = Boolean(scene && figures.length === 3 && figures.every(box => box.left >= scene.left && box.right <= scene.right && box.top >= scene.top && box.bottom <= scene.bottom));
      return {
        viewportWidth: innerWidth,
        documentWidth: document.documentElement.scrollWidth,
        hasHorizontalOverflow: document.documentElement.scrollWidth > innerWidth,
        dockOverlapsFirstFormation,
        sceneInspectorSeparated: Boolean(scene && inspector && (scene.right <= inspector.left || scene.left >= inspector.right)),
        figuresInsideScene,
        formationRail: { clientWidth, scrollWidth, hasOverflow: hasFormationOverflow, scrollLeftAtStart, maxScrollLeft, selectedFormationVisible, firstFormationAccessible, lastFormationAccessible },
      };
    });
    assert.equal(currentLayout.hasHorizontalOverflow, false, `Army view has no horizontal overflow at ${size}`);
    assert.equal(currentLayout.dockOverlapsFirstFormation, false, `the Army detail action leaves the first formation fully clear at ${size}`);
    assert.equal(currentLayout.sceneInspectorSeparated, true, `muster scene and recruitment inspector stay in separate columns at ${size}`);
    assert.equal(currentLayout.figuresInsideScene, true, `all three formation figures stay inside the scene at ${size}`);
    assert.equal(currentLayout.formationRail.selectedFormationVisible, true, `the active formation stays visible at ${size}`);
    assert.equal(currentLayout.formationRail.firstFormationAccessible, true, `first formation is fully accessible at ${size}`);
    assert.equal(currentLayout.formationRail.lastFormationAccessible, true, `last formation is fully accessible at the roster rail end at ${size}: ${JSON.stringify(currentLayout)}`);
    if (age === 7) assert.equal(currentLayout.formationRail.hasOverflow, true, `full Future roster has a scrollable formation rail at ${size}`);
    presentation.viewportLayouts.push({ size, dockOverlapsFirstFormation: currentLayout.dockOverlapsFirstFormation, sceneInspectorSeparated: currentLayout.sceneInspectorSeparated, figuresInsideScene: currentLayout.figuresInsideScene, ...currentLayout.formationRail });
    const file = path.join(out, `army-age-${age}-${size}.png`);
    await page.screenshot({ path: file });
    report.screenshots.push({ name: `army-age-${age}`, size, file: path.relative(root, file) });
  }
  if (age === 3) {
    const beforeShowcaseSelection = (await read()).state;
    const restoreRole = report.armyRecruits[age].role;
    const testedRole = restoreRole === 'melee' ? 'heavy' : 'melee';
    await page.locator(`#board .army-showcase-unit[data-army-showcase-role="${testedRole}"]`).click();
    const selectedRoleTitle = await page.locator('#board .roster-inspector h2').textContent();
    assert.equal(selectedRoleTitle?.trim(), data.ROLES[testedRole].names[age], 'selecting a muster figure opens that role in the recruitment inspector');
    const afterShowcaseSelection = (await read()).state;
    const selectionElapsedMs = afterShowcaseSelection.clock - beforeShowcaseSelection.clock;
    for (const resource of ['food', 'wood', 'stone', 'gold']) {
      const earned = afterShowcaseSelection.resources[resource] - beforeShowcaseSelection.resources[resource]
        - rates(beforeShowcaseSelection)[resource] * selectionElapsedMs / 1000;
      assert.ok(Math.abs(earned) < 1e-6, `showcase selection does not spend ${resource} beyond passive income`);
    }
    assert.deepEqual(afterShowcaseSelection.army, beforeShowcaseSelection.army, 'showcase selection does not change owned formations');
    await page.locator(`#board .board-row[data-army-row="review"] .board-card[data-choice="catalog:${age}-${restoreRole}"]`).click();
    assert.equal((await page.locator('#board .roster-inspector h2').textContent())?.trim(), data.ROLES[restoreRole].names[age], 'the recruitment cards still select their matching role after using the showcase');
    presentation.showcaseSelection = { testedRole, selectedRoleTitle: selectedRoleTitle?.trim(), campaignResourcesUnchanged: true, ownedArmyUnchanged: true, restoredRole: restoreRole };
  }
  presentation.captures = ['825x375', '933x424', '1280x720'];
  await page.locator('[data-choice="nav:kingdom"]').first().click();
  await page.locator('#app[data-view="kingdom"]').waitFor({ state: 'attached', timeout: 10000 });
}
async function forgeAndCheckAgeWeapon(age) {
  const state = (await read()).state;
  assert.equal(state.age, age, 'weapon is forged for the current campaign age');
  const armoryLevel = state.plots.find(plot => plot.type === 'armory')?.level || 0;
  assert.ok(armoryLevel >= 1, 'an earned Armory unlocks forging');
  const offer = forgeOffer(age, armoryLevel);
  await clearInspector();
  await page.locator('#context').click();
  await clickChoice('menu:forge');
  const weaponSlot = page.locator('[data-choice="scene-forge-slot:weapon"]').first();
  if (await weaponSlot.getAttribute('data-selected') !== '1') await clickChoice('scene-forge-slot:weapon');
  await waitForResources(offer.cost, 'age ' + age + ' weapon forge');
  await clickChoice('inspect:forge');
  await clickChoice('forge-confirm');
  await page.locator('#build-commit').click();
  const inventory = await waitForState(value => value.inventory.some(item => item.slot === 'weapon' && item.age === age), 'age ' + age + ' forged weapon');
  const item = inventory.inventory.find(entry => entry.slot === 'weapon' && entry.age === age);
  await clickChoice('inventory-item:' + item.id);
  await clickChoice('equip-confirm:' + item.id);
  const equipped = await waitForState(value => value.hero.equip.weapon?.id === item.id, 'age ' + age + ' weapon equips');
  assert.ok(!equipped.inventory.some(entry => entry.id === item.id), 'equipped age weapon leaves the bag');
  await page.locator('[data-choice="nav:hero"]').first().click();
  await page.locator('#app[data-view="hero"]').waitFor({ state: 'attached', timeout: 10000 });
  const layer = page.locator('[data-slot-layer="weapon"] image');
  const presentation = await page.locator('[data-worn-slot="weapon"]').getAttribute('data-worn-appearance');
  const expected = weaponFiles[age];
  const bodyCarriesBuiltInWeapon = bodyHasHeldWeapon(heroBody('knight', age));
  const expectedHeroAppearance = bodyCarriesBuiltInWeapon ? 'socket-only' : 'attached-asset';
  assert.equal(presentation, expectedHeroAppearance, 'age ' + age + ' avoids duplicating a weapon already painted into the Hero plate');
  const href = await layer.count() ? await layer.first().getAttribute('href') : '';
  if (expectedHeroAppearance === 'attached-asset') {
    await layer.first().waitFor({ state: 'attached', timeout: 10000 });
    assert.equal(href, expected, 'age ' + age + ' displays its own weapon on the Hero');
  } else {
    assert.equal(await layer.count(), 0, 'age ' + age + ' does not double-paint its plate weapon');
  }
  const record = { age, itemId: item.id, quality: item.quality, armoryLevel, cost: offer.cost, heroAppearance: presentation, heroHref: href, adventureHref: expected };
  report.weapons.push(record);
  for (const size of ['825x375', '933x424', '1280x720']) {
    const [width, height] = size.split('x').map(Number);
    await page.setViewportSize({ width, height });
    await page.waitForTimeout(100);
    const file = path.join(out, 'hero-weapon-age-' + age + '-' + size + '.png');
    await page.screenshot({ path: file });
    report.screenshots.push({ name: 'hero-weapon-age-' + age, size, file: path.relative(root, file) });
  }
  await page.locator('[data-choice="nav:kingdom"]').first().click();
  await page.locator('#app[data-view="kingdom"]').waitFor({ state: 'attached', timeout: 10000 });
}
async function forgeAndEquipFutureSlot(slot) {
  let state = (await read()).state;
  assert.equal(state.age, 7, 'the six-slot loadout is forged in Future');
  const armoryLevel = state.plots.find(plot => plot.type === 'armory')?.level || 0;
  assert.ok(armoryLevel >= 1, 'a naturally built Armory unlocks each Future slot');
  const offer = forgeOffer(7, armoryLevel);
  await clearInspector();
  await page.locator('#context').click();
  await clickChoice('menu:forge');
  if (!report.forgeLayoutCaptures) {
    report.forgeLayoutCaptures = [];
    for (const size of ['825x375', '933x424', '1280x720']) {
      const [width, height] = size.split('x').map(Number);
      await page.setViewportSize({ width, height });
      await page.waitForTimeout(120);
      const file = path.join(out, 'forge-slots-before-loadout-' + size + '.png');
      await page.screenshot({ path: file });
      const geometry = await page.evaluate(() => {
        const rect = selector => {
          const node = document.querySelector(selector);
          if (!node) return null;
          const box = node.getBoundingClientRect();
          return { left: box.left, right: box.right, top: box.top, bottom: box.bottom };
        };
        const rail = rect('#scene-ui.forge .col');
        const dock = rect('#dock');
        return { rail, dock, overlap: Boolean(rail && dock && rail.left < dock.right && rail.right > dock.left && rail.top < dock.bottom && rail.bottom > dock.top) };
      });
      assert.equal(geometry.overlap, false, 'Forge slot rail stays clear of the action panel at ' + size);
      report.forgeLayoutCaptures.push({ size, file: path.relative(root, file), geometry });
    }
    await page.setViewportSize({ width: 1280, height: 720 });
  }
  const sceneSlot = page.locator(`[data-choice="scene-forge-slot:${slot}"]`).first();
  await sceneSlot.waitFor({ state: 'visible', timeout: 10000 });
  if (await sceneSlot.getAttribute('data-selected') !== '1') await sceneSlot.click();
  await waitForResources(offer.cost, 'Future ' + slot + ' forge');
  await clickChoice('inspect:forge');
  const panelState = await page.evaluate(() => ({
    panelOpen: document.querySelector('#panel')?.classList.contains('open') || false,
    panelForgeActions: document.querySelectorAll('#panel [data-choice="forge-confirm"]').length,
    dockForgeDuplicates: document.querySelectorAll('#dock [data-choice="forge-confirm"]').length,
  }));
  assert.equal(panelState.panelOpen, true, 'Forge inspector is open for the current slot');
  assert.equal(panelState.panelForgeActions, 1, 'Forge inspector owns one primary craft action');
  assert.equal(panelState.dockForgeDuplicates, 0, 'closed-panel action clones are removed while the inspector is open');
  report.forgeInspectorSurface = panelState;
  if (!report.forgeInspectorCaptures) {
    report.forgeInspectorCaptures = [];
    for (const size of ['825x375', '933x424', '1280x720']) {
      const [width, height] = size.split('x').map(Number);
      await page.setViewportSize({ width, height });
      await page.waitForTimeout(120);
      const file = path.join(out, 'forge-inspector-before-loadout-' + size + '.png');
      await page.screenshot({ path: file });
      const priceLayout = await page.evaluate(() => {
        const action = document.querySelector('#panel [data-choice="forge-confirm"]');
        const costs = action?.querySelector('.cost-icons');
        return {
          actionWidth: action?.clientWidth || 0,
          actionScrollWidth: action?.scrollWidth || 0,
          costsWidth: costs?.clientWidth || 0,
          costsScrollWidth: costs?.scrollWidth || 0,
        };
      });
      assert.ok(priceLayout.actionWidth > 0 && priceLayout.actionScrollWidth <= priceLayout.actionWidth + 1, 'Forge price fits the inspector action at ' + size);
      assert.ok(priceLayout.costsWidth > 0 && priceLayout.costsScrollWidth <= priceLayout.costsWidth + 1, 'Forge resource symbols wrap within the inspector at ' + size);
      report.forgeInspectorCaptures.push({ size, file: path.relative(root, file), priceLayout });
    }
    await page.setViewportSize({ width: 1280, height: 720 });
  }
  const inventoryBeforePreview = (await read()).state;
  const selectedForCompare = inventoryBeforePreview.inventory[0];
  assert.ok(selectedForCompare, 'the Future armory has a naturally earned carried item to inspect');
  const selectedTitle = selectedForCompare.kind === 'artifact'
    ? data.ARTIFACTS[selectedForCompare.artifactId]?.n || selectedForCompare.artifactId
    : `${data.GEAR[selectedForCompare.slot]?.names?.[selectedForCompare.age] || selectedForCompare.slot} · ${data.QUAL[selectedForCompare.quality]?.n || 'gear'}`;
  await clickChoice('inventory-item:' + selectedForCompare.id);
  await page.locator('#panel .forge-selected-summary').waitFor({ state: 'visible', timeout: 10000 });
  report.forgeInventoryReview = { selectedItemId: selectedForCompare.id, selectedTitle, slot: selectedForCompare.slot, viewports: [] };
  for (const size of ['825x375', '933x424', '1280x720']) {
    const [width, height] = size.split('x').map(Number);
    await page.setViewportSize({ width, height });
    await page.waitForTimeout(120);
    const selectionLayout = await page.evaluate(itemId => {
      const rect = node => {
        const box = node?.getBoundingClientRect();
        return box ? { left: box.left, right: box.right, top: box.top, bottom: box.bottom, width: box.width, height: box.height } : null;
      };
      const grid = document.querySelector('#scene-ui.forge .forge-inventory-grid');
      const panel = document.querySelector('#panel');
      const summary = panel?.querySelector('.forge-selected-summary');
      const selected = grid?.querySelector(`[data-item-id="${itemId}"]`);
      const equip = panel?.querySelector(`[data-choice="equip-confirm:${itemId}"]`);
      const cancel = panel?.querySelector('[data-choice="equip-cancel"]');
      const hero = document.querySelector('#world [data-forge-hero]');
      const rail = document.querySelector('#scene-ui.forge .forge-slots');
      const gridRect = rect(grid);
      const panelRect = rect(panel);
      const summaryRect = rect(summary);
      const heroRect = rect(hero);
      const railRect = rect(rail);
      const overlaps = (a, b) => Boolean(a && b && a.left < b.right && a.right > b.left && a.top < b.bottom && a.bottom > b.top);
      return {
        cardCount: grid?.querySelectorAll('.forge-inventory-card').length || 0,
        cardsWithArt: [...(grid?.querySelectorAll('.forge-inventory-card') || [])].filter(card => {
          const image = card.querySelector('img[data-gear-icon]');
          return Boolean(image?.complete && image.naturalWidth > 0);
        }).length,
        selected: selected?.getAttribute('aria-current') === 'true',
        summaryText: summary?.textContent?.trim() || '',
        summaryVisible: Boolean(summaryRect && summaryRect.top >= panelRect.top && summaryRect.bottom <= Math.min(panelRect.bottom, innerHeight)),
        equipVisible: Boolean(equip && equip.getBoundingClientRect().width > 0 && equip.getBoundingClientRect().top >= 0 && equip.getBoundingClientRect().bottom <= innerHeight),
        cancelPresent: Boolean(cancel),
        gridRect,
        panelRect,
        summaryRect,
        gridOverlapsPanel: Boolean(gridRect && panelRect && gridRect.left < panelRect.right && gridRect.right > panelRect.left && gridRect.top < panelRect.bottom && gridRect.bottom > panelRect.top),
        heroPresent: Boolean(heroRect && heroRect.width > 0 && heroRect.height > 0),
        heroRect,
        heroOverlapsPanel: overlaps(heroRect, panelRect),
        heroOverlapsInventory: overlaps(heroRect, gridRect),
        heroOverlapsSlots: overlaps(heroRect, railRect),
      };
    }, selectedForCompare.id);
    assert.equal(selectionLayout.cardCount, inventoryBeforePreview.inventory.length, 'every carried item appears in the armory grid at ' + size);
    assert.equal(selectionLayout.cardsWithArt, inventoryBeforePreview.inventory.length, 'every gear card shows loaded item art at ' + size);
    assert.equal(selectionLayout.selected, true, 'the chosen item is visibly selected at ' + size);
    assert.ok(selectionLayout.summaryText.includes(selectedTitle), 'selected item preview names the selected gear at ' + size);
    assert.equal(selectionLayout.summaryVisible, true, 'selected-item preview is fully visible in the inspector at ' + size);
    assert.equal(selectionLayout.equipVisible, true, 'Equip action stays visible with the selected preview at ' + size);
    assert.equal(selectionLayout.cancelPresent, true, 'Cancel comparison remains available at ' + size);
    assert.equal(selectionLayout.gridOverlapsPanel, false, 'inventory artwork stays clear of the inspector at ' + size);
    const file = path.join(out, 'forge-item-selected-' + size + '.png');
    await page.screenshot({ path: file });
    report.forgeInventoryReview.viewports.push({ size, ...selectionLayout, screenshot: path.relative(root, file) });
  }
  const desktopForge = report.forgeInventoryReview.viewports.find(item => item.size === '1280x720');
  assert.equal(desktopForge.heroPresent, true, 'desktop armory includes the campaign-age hero figure');
  assert.equal(desktopForge.heroOverlapsPanel, false, 'desktop hero stays clear of the inspector');
  assert.equal(desktopForge.heroOverlapsInventory, false, 'desktop hero stays clear of the item tray');
  assert.equal(desktopForge.heroOverlapsSlots, false, 'desktop hero stays clear of the equipped-slot rail');
  const inventoryBeforeCancel = (await read()).state;
  await page.locator('#panel [data-choice="equip-cancel"]').click();
  await page.locator('#scene-ui.forge .forge-inventory-card[aria-current="true"]').waitFor({ state: 'detached', timeout: 10000 });
  const inventoryAfterCancel = (await read()).state;
  assert.deepEqual(inventoryAfterCancel.inventory.map(item => item.id), inventoryBeforeCancel.inventory.map(item => item.id), 'cancel leaves every carried item unchanged');
  assert.deepEqual(inventoryAfterCancel.hero.equip, inventoryBeforeCancel.hero.equip, 'cancel leaves worn equipment unchanged');
  const cancelElapsedMs = inventoryAfterCancel.clock - inventoryBeforeCancel.clock;
  assert.ok(cancelElapsedMs >= 0, 'cancel does not move the campaign clock backwards');
  const passiveRates = rates(inventoryBeforeCancel);
  const resourceDelta = Object.fromEntries(Object.keys(inventoryBeforeCancel.resources).map(key => [key, inventoryAfterCancel.resources[key] - inventoryBeforeCancel.resources[key]]));
  for (const [key, gained] of Object.entries(resourceDelta)) {
    const expectedPassiveIncome = passiveRates[key] * cancelElapsedMs / 1000;
    assert.ok(Math.abs(gained - expectedPassiveIncome) < 0.00001, `cancel does not spend ${key}; observed delta is only clocked production`);
  }
  report.forgeInventoryReview.cancelNoGameplayMutation = true;
  report.forgeInventoryReview.cancelResourceDeltaMatchesPassiveProduction = true;
  report.forgeInventoryReview.cancelElapsedMs = cancelElapsedMs;
  report.forgeInventoryReview.cancelResourceDelta = resourceDelta;
  await clickChoice('scene-forge-slot:' + slot);
  await page.setViewportSize({ width: 1280, height: 720 });
  await clickChoice('forge-confirm');
  await page.locator('#build-commit').click();
  let snapshot = await waitForState(value => value.inventory.some(item => item.slot === slot && item.age === 7), 'Future ' + slot + ' enters inventory');
  const item = snapshot.inventory.find(entry => entry.slot === slot && entry.age === 7);
  await clickChoice('inventory-item:' + item.id);
  await clickChoice('equip-confirm:' + item.id);
  state = await waitForState(value => value.hero.equip[slot]?.id === item.id, 'Future ' + slot + ' equips');
  assert.ok(!state.inventory.some(entry => entry.id === item.id), 'equipped Future ' + slot + ' leaves the bag');
  await page.locator('[data-choice="nav:hero"]').first().click();
  await page.locator('#app[data-view="hero"]').waitFor({ state: 'attached', timeout: 10000 });
  const socket = page.locator(`#world [data-worn-slot="${slot}"]`);
  assert.equal(await socket.getAttribute('data-worn-state'), 'worn', 'Future ' + slot + ' is marked worn on the Hero');
  assert.equal(await socket.getAttribute('data-worn-item'), item.id, 'Future ' + slot + ' visual record matches the equipped item');
  const card = page.locator(`[data-hero-slot="${slot}"]`);
  assert.equal(await card.getAttribute('data-worn'), '1', 'Future ' + slot + ' loadout card is filled');
  const icon = await card.locator('img[data-gear-icon]').getAttribute('src');
  assert.ok(icon, 'Future ' + slot + ' loadout card has its reviewed gear icon');
  const record = { slot, itemId: item.id, quality: item.quality, cost: offer.cost, wornState: await socket.getAttribute('data-worn-state'), appearance: await socket.getAttribute('data-worn-appearance'), heroCardIcon: icon };
  report.futureLoadout ??= [];
  report.futureLoadout.push(record);
  await page.locator('[data-choice="nav:kingdom"]').first().click();
  await page.locator('#app[data-view="kingdom"]').waitFor({ state: 'attached', timeout: 10000 });
}
const weaponFiles = [
  'assets/derivatives/worn-gear-20261018/flint-club-stone.png',
  'assets/derivatives/worn-gear-20261020/weapon-bronze.png',
  'assets/derivatives/worn-gear-20261020/weapon-iron.png',
  'assets/derivatives/worn-gear-20261020/weapon-medieval.png',
  'assets/derivatives/worn-gear-20261020/weapon-gunpowder.png',
  'assets/derivatives/worn-gear-20261020/weapon-industrial.png',
  'assets/derivatives/worn-gear-20261020/weapon-modern.png',
  'assets/derivatives/worn-gear-20261020/weapon-future.png',
];

async function captureAdventureAge(age) {
  await page.locator('[data-choice="nav:adventure"]').first().click();
  let state = (await read()).state;
  if (!state.adventure || state.adventure.atTown) await clickChoice('enter-adventure');
  state = await waitForState(value => value.age === age && value.adventure?.atTown === false, 'Adventure map in ' + data.AGES[age].n);
  const scene = await sceneState();
  assert.equal(scene.view, 'adventure');
  assert.equal(scene.terrainLoaded, true, data.AGES[age].n + ' Adventure terrain loads');
  const details = await page.evaluate(() => ({
    board: document.querySelector('#world')?.getAttribute('data-board'),
    mountedTraveler: document.querySelectorAll('#world [data-mount]').length === 1,
    weaponAppearance: document.querySelector('#world [data-mount] [data-actor="knight"] [data-worn-slot="weapon"]')?.getAttribute('data-worn-appearance') || '',
    weaponLayerCount: document.querySelectorAll('#world [data-mount] [data-actor="knight"] [data-slot-layer="weapon"] image').length,
    weaponHref: document.querySelector('#world [data-mount] [data-actor="knight"] [data-slot-layer="weapon"] image')?.getAttribute('href') || '',
    genericWeaponJointCount: document.querySelectorAll('#world [data-mount] [data-actor="knight"] [data-joint="weapon"]').length,
    visibleSites: document.querySelectorAll('#world .adventure-site').length,
    visitedCells: JSON.parse(document.querySelector('#audit-snapshot')?.textContent || 'null')?.state?.adventure?.visited?.length || 0,
    terrainRouteOverlay: document.querySelector('#world [data-terrain-route-overlay="gunpowder"]') ? {
      routeCount: new Set([...document.querySelectorAll('#world [data-terrain-route-overlay="gunpowder"] [data-route-index]')].map(node => node.getAttribute('data-route-index'))).size,
      layerCount: document.querySelectorAll('#world [data-terrain-route-overlay="gunpowder"] polyline').length,
    } : null,
  }));
  assert.equal(details.mountedTraveler, true, data.AGES[age].n + ' has one mounted traveler');
  assert.equal(details.weaponAppearance, 'attached-asset', data.AGES[age].n + ' Adventure rider shows the equipped age weapon');
  assert.equal(details.weaponLayerCount, 1, data.AGES[age].n + ' Adventure rider has one weapon attachment');
  assert.equal(details.weaponHref, weaponFiles[age], data.AGES[age].n + ' Adventure rider uses the matching age art');
  assert.equal(details.genericWeaponJointCount, 0, data.AGES[age].n + ' Adventure rider has no duplicate rig weapon');
  Object.assign(report.weapons[age], { adventureAppearance: details.weaponAppearance, adventureHref: details.weaponHref, genericWeaponJointCount: details.genericWeaponJointCount });
  report.ages[age].adventureScene = { ...scene, ...details };
  if (age === 4) {
    assert.equal(scene.terrain, worlds[10].mapFile, 'Gunpowder Adventure preserves the selected Jade Karst campaign world art');
    assert.equal(details.terrainRouteOverlay, null, 'integrated campaign art is not obscured by an unrelated age route overlay');
    const adjacentOpenCell = page.locator('#world [data-adventure-cell="6,4"]');
    assert.equal(await adjacentOpenCell.count(), 1, 'Gunpowder Adventure renders the reachable Jade Karst approach cell once');
    await adjacentOpenCell.click();
    await page.waitForTimeout(80);
    assert.equal(await page.locator('#world [data-route-destination]').count(), 1, 'Gunpowder route preview selects one reachable destination');
    const confirm = page.locator('[data-choice="confirm-route"]').first();
    await confirm.waitFor({ state: 'visible', timeout: 10000 });
    assert.equal(await confirm.isDisabled(), false, 'Gunpowder one-step route confirmation is enabled');
    await confirm.click();
    state = await waitForState(value => value.age === 4 && value.adventure?.x === 6 && value.adventure?.y === 4 && value.adventure?.moves === 3, 'confirmed Gunpowder one-step route');
    report.ages[age].adventureRoute = { destination: '6,4', afterMove: state.adventure };
    report.screenshots.push(await captureScene('age-4-adventure-after-route', ['1280x720']));
  }
  report.screenshots.push(await captureScene('age-' + age + '-adventure', ['825x375', '1280x720']));
  if (age === 2) {
    assert.equal(scene.terrain, worlds[10].mapFile, 'Iron Adventure preserves the selected Jade Karst campaign world art');
    const adjacentOpenCell = page.locator('#world [data-adventure-cell="7,4"]');
    assert.equal(await adjacentOpenCell.count(), 1, 'Iron Adventure renders the reachable Jade Karst approach cell once');
    await adjacentOpenCell.click();
    await page.waitForTimeout(80);
    assert.equal(await page.locator('#world [data-route-destination]').count(), 1, 'Iron route preview selects one reachable destination');
    const confirm = page.locator('[data-choice="confirm-route"]').first();
    await confirm.waitFor({ state: 'visible', timeout: 10000 });
    assert.equal(await confirm.isDisabled(), false, 'Iron one-step route confirmation is enabled');
    const preview = await sceneState();
    report.ages[age].adventureRoute = { preview, destination: '7,4' };
    report.screenshots.push(await captureScene('age-2-adventure-route-preview', ['1280x720']));
    await confirm.click();
    state = await waitForState(value => value.age === 2 && value.adventure?.x === 7 && value.adventure?.y === 4 && value.adventure?.moves === 4, 'confirmed Iron one-step route');
    report.ages[age].adventureRoute.afterMove = state.adventure;
    report.screenshots.push(await captureScene('age-2-adventure-after-route', ['825x375', '1280x720']));
  }
  await page.locator('[data-choice="nav:kingdom"]').first().click();
  await page.locator('#app[data-view="kingdom"]').waitFor({ state: 'attached', timeout: 10000 });
}

try {
  await page.goto(report.url, { waitUntil: 'networkidle' });
  await clickChoice('new-campaign');
  await clickChoice(`campaign-world:${worlds[10].id}`);
  await clickChoice('begin-selected-world');
  await clickChoice('scene-class:knight');
  await clickChoice('scene-enter-valley');
  await waitForState(state => state.story.flags.enteredValley === true, 'fresh Stone campaign');
  await page.locator('#context').click();
  await clickChoice('site-list');
  await clickChoice('choose-site:townhall');
  await clickChoice('tutorial-toggle');
  await waitForState(state => state.tutorial.skipped === true, 'optional tutorial skipped');
  report.tutorialSkippedThroughVisibleControl = true;
  report.startClock = (await read()).state.clock;
  report.startCampaignId = (await read()).state.id;
  report.screenshots.push(await captureScene('age-0-no-wall', ['825x375', '1280x720']));
  await resolveAgeStoryChapter(0);

  const producers = [
    ['P01', 'farm'],
    ['P02', 'lumber'],
    ['P03', 'quarry'],
    ['P04', 'mine'],
  ];
  for (const [siteId, building] of producers) await buildAt(siteId, building);
  await buildAt('P05', 'armory');
  await buildAt('P06', 'barracks');
  report.producers = (await read()).state.plots.filter(plot => ['farm', 'lumber', 'quarry', 'mine'].includes(plot.type))
    .map(plot => ({ id: plot.id, type: plot.type, level: plot.level }));
  report.armory = (await read()).state.plots.find(plot => plot.type === 'armory');
  report.barracks = (await read()).state.plots.find(plot => plot.type === 'barracks');
  report.incomeRates = rates((await read()).state);
  report.screenshots.push(await captureScene('age-0-producers-no-wall', ['825x375', '1280x720']));

  report.ages[0] = { age: 0, name: data.AGES[0].n, wallPhases: [] };
  await buildHall(2);
  await clearInspector();
  await page.locator('#context').click();
  await clickChoice('site-list');
  await clickChoice('choose-site:townhall');
  await buildWall(1, 0);
  let currentScene = await sceneState();
  assert.equal(currentScene.wallPhase, 'built');
  assert.equal(currentScene.wallLevel, 1);
  assert.equal(currentScene.terrainStatus, 'kingdom-painting');
  assert.equal(currentScene.terrainLoaded, true);
  assert.equal(currentScene.wallStamps, 0);
  report.ages[0].wallPhases.push(currentScene);
  report.screenshots.push(await captureScene('age-0-built-wall', ['825x375', '1280x720']));
  await forgeAndCheckAgeWeapon(0);
  await recruitOneFormationPerAge(0);
  await captureArmyAge(0);
  await captureAdventureAge(0);

  for (let age = 0; age < 7; age += 1) {
    let state = (await read()).state;
    await buildHall(age + 2);
    await buildWall(age + 1, age);
    state = (await read()).state;
    const hallLevel = state.plots.find(plot => plot.id === 'townhall').level;
    assert.ok(hallLevel >= age + 2, data.AGES[age].n + ' has the required Hall level');
    await waitForResources(agePrice(age), 'legal ' + data.AGES[age].n + ' age advance');
    await clearInspector();
    await clickChoice('kingdom-actions-open');
    await clickChoice('age-advance');
    await page.locator('#build-commit').click();
    state = await waitForState(value => value.age === age + 1, 'advance to ' + data.AGES[age + 1].n);
    report.ages[age].advancedTo = data.AGES[age + 1].n;
    report.ages[age].balanceAfterPayment = { ...state.resources };
    const nextAge = age + 1;
    report.ages[nextAge] = { age: nextAge, name: data.AGES[nextAge].n, wallPhases: [] };
    const transitionedScene = await sceneState();
    assert.equal(transitionedScene.view, 'kingdom');
    assert.equal(transitionedScene.terrainLoaded, true);
    assert.equal(transitionedScene.wallLevel, age + 1);
    report.ages[nextAge].wallPhases.push(transitionedScene);
    report.screenshots.push(await captureScene('age-' + nextAge + '-entered', ['825x375', '1280x720']));
    if (nextAge < data.STORY.length) await resolveAgeStoryChapter(nextAge);
    else await acknowledgeFutureConclusion();
    await forgeAndCheckAgeWeapon(nextAge);
    await buildSiteToLevel('P06', 'barracks', nextAge + 1);
    await recruitOneFormationPerAge(nextAge);
    await captureArmyAge(nextAge);
    await captureAdventureAge(nextAge);
  }

  await buildWall(8, 7);
  const finalScene = await sceneState();
  assert.equal(finalScene.wallPhase, 'tall');
  assert.equal(finalScene.wallLevel, 8);
  assert.equal(finalScene.terrainLoaded, true);
  report.ages[7].wallPhases.push(finalScene);
  report.screenshots.push(await captureScene('age-7-future-wall-tall', ['825x375', '1280x720']));
  for (const slot of ['helm', 'offhand', 'armor', 'boots', 'accessory']) await forgeAndEquipFutureSlot(slot);
  await page.locator('[data-choice="nav:hero"]').first().click();
  await page.locator('#app[data-view="hero"]').waitFor({ state: 'attached', timeout: 10000 });
  const finalLoadout = await page.evaluate(() => ({
    slots: [...document.querySelectorAll('#world [data-worn-slot]')].map(node => ({
      slot: node.getAttribute('data-worn-slot'),
      state: node.getAttribute('data-worn-state'),
      itemId: node.getAttribute('data-worn-item'),
      appearance: node.getAttribute('data-worn-appearance'),
    })),
    cards: [...document.querySelectorAll('[data-hero-slot]')].map(node => ({
      slot: node.getAttribute('data-hero-slot'),
      worn: node.getAttribute('data-worn'),
      icon: node.querySelector('img[data-gear-icon]')?.getAttribute('src') || '',
    })),
  }));
  assert.equal(finalLoadout.slots.length, 6, 'Future Hero figure exposes all six equipment sockets');
  assert.ok(finalLoadout.slots.every(slot => slot.state === 'worn' && slot.itemId), 'all six Future sockets are visibly worn');
  assert.ok(['helm', 'weapon', 'offhand', 'armor', 'boots', 'accessory'].every(name => finalLoadout.slots.find(slot => slot.slot === name)?.appearance === 'attached-asset'),
    'all six Future Knight slots are visibly fitted to the figure');
  assert.equal(finalLoadout.cards.length, 6, 'Future Hero panel exposes all six loadout cards');
  assert.ok(finalLoadout.cards.every(card => card.worn === '1' && card.icon), 'all six Future loadout cards show gear icons');
  report.futureLoadoutVisual = finalLoadout;
  for (const size of ['825x375', '933x424', '1280x720']) {
    const [width, height] = size.split('x').map(Number);
    await page.setViewportSize({ width, height });
    await page.waitForTimeout(120);
    const file = path.join(out, 'hero-future-six-slot-loadout-' + size + '.png');
    await page.screenshot({ path: file });
    report.screenshots.push({ name: 'hero-future-six-slot-loadout', size, file: path.relative(root, file) });
  }
  await page.locator('#context').click();
  await clickChoice('menu:story');
  await page.waitForFunction(() => document.querySelector('#app')?.dataset.view === 'story');
  if (!(await read()).state.story.rival) await clickChoice('journal-rival:Varek Iron-Eye');
  await clickChoice('journal:quests');
  await page.waitForFunction(() => Boolean(document.querySelector('#scene-ui [data-equipment-goal="q5"]')));
  const goalScreens = [];
  for (const size of ['1280x720', '825x375']) {
    const [width, height] = size.split('x').map(Number);
    await page.setViewportSize({ width, height });
    await page.waitForTimeout(120);
    const panelScroll = await scrollElementIntoPanel('#scene-ui', '#scene-ui [data-equipment-goal="q5"]', `Q5 ${size}`);
    const capture = await page.evaluate(() => {
      const goal = document.querySelector('#scene-ui [data-equipment-goal="q5"]');
      const panel = document.querySelector('#scene-ui')?.getBoundingClientRect();
      const bounds = goal?.getBoundingClientRect();
      const quest = document.querySelector('#scene-ui [data-quest-id="q5"]');
      return {
        state: goal?.dataset.goalState || '',
        title: goal?.querySelector('.equipment-goal-title')?.textContent?.trim() || '',
        progress: goal?.querySelector('.equipment-goal-progress')?.textContent?.trim() || '',
        meter: goal?.querySelector('[role="progressbar"]')?.getAttribute('aria-valuenow') || '',
        meterMax: goal?.querySelector('[role="progressbar"]')?.getAttribute('aria-valuemax') || '',
        slots: [...(goal?.querySelectorAll('[data-equipment-slot]') || [])].map(slot => ({
          slot: slot.dataset.equipmentSlot,
          equipped: slot.dataset.equipped,
          ratio: slot.querySelector('span')?.textContent?.trim() || '',
          icon: slot.querySelector('img')?.dataset.gearIcon || (slot.querySelector('svg') ? 'slot-glyph' : ''),
          accessibleName: slot.getAttribute('aria-label') || '',
        })),
        reward: goal?.querySelector('.equipment-goal-reward')?.innerText?.replace(/\s+/g, ' ').trim() || '',
        q5Status: quest?.querySelector('p')?.textContent?.trim() || '',
        q5ClaimReady: Boolean(quest?.querySelector('[data-choice="journal-claim:q5"]')),
        panelBounds: panel ? { x: panel.x, y: panel.y, right: panel.right, bottom: panel.bottom, height: panel.height } : null,
        bounds: bounds ? { x: bounds.x, y: bounds.y, right: bounds.right, bottom: bounds.bottom, height: bounds.height } : null,
        fullyInPanel: Boolean(panel && bounds && bounds.top >= panel.top && bounds.bottom <= panel.bottom),
        scrollTop: document.querySelector('#scene-ui')?.scrollTop || 0,
      };
    });
    const file = path.join(out, 'objectives-future-equipment-goal-' + size + '.png');
    await page.screenshot({ path: file });
    goalScreens.push({ size, ...capture, panelScroll, file: path.relative(root, file) });
    report.futureEquipmentGoal = { slots: goalScreens[0].slots, viewports: goalScreens };
    assert.equal(capture.state, 'ready', 'six Future slots complete Q5 without claiming its reward');
    assert.equal(capture.title, 'Arm the Garrison');
    assert.equal(capture.progress, '6 / 6 slots equipped');
    assert.equal(capture.meter, '6');
    assert.equal(capture.meterMax, '6');
    assert.deepEqual(capture.slots.map(slot => slot.slot), ['helm', 'weapon', 'offhand', 'armor', 'boots', 'accessory']);
    assert.ok(capture.slots.every(slot => slot.equipped === 'true' && slot.ratio === '1 / 1' && slot.icon && slot.accessibleName.includes(':')));
    assert.match(capture.reward, /400 gold/);
    assert.equal(capture.q5Status, 'Ready to claim');
    assert.equal(capture.q5ClaimReady, true);
    assert.equal(capture.fullyInPanel, true);
  }
  const beforeGoalClaim = (await read()).state;
  await page.locator('#scene-ui [data-choice="journal-claim:q5"]').click();
  const afterGoalClaim = await waitForState(value => value.quests.q5.claimed === true, 'claim the complete equipment goal');
  const goalClaimElapsedMs = afterGoalClaim.clock - beforeGoalClaim.clock;
  const goalGoldDelta = afterGoalClaim.resources.gold - beforeGoalClaim.resources.gold
    - rates(beforeGoalClaim).gold * goalClaimElapsedMs / 1000;
  const claimedGoalUi = await page.evaluate(() => {
    const goal = document.querySelector('#scene-ui [data-equipment-goal="q5"]');
    const quest = document.querySelector('#scene-ui [data-quest-id="q5"]');
    return {
      goalState: goal?.dataset.goalState || '',
      questStatus: quest?.querySelector('p')?.textContent?.trim() || '',
      claimPresent: Boolean(quest?.querySelector('[data-choice="journal-claim:q5"]')),
      claimedDisabled: quest?.querySelector('[data-choice="journal-claimed:q5"]')?.disabled ?? null,
      rewardText: goal?.querySelector('.equipment-goal-reward')?.innerText?.replace(/\s+/g, ' ').trim() || '',
    };
  });
  assert.ok(Math.abs(goalGoldDelta - 400) < 1e-6, 'Q5 UI claim pays exactly 400 gold after clocked passive income');
  assert.equal(claimedGoalUi.goalState, 'claimed');
  assert.equal(claimedGoalUi.questStatus, 'Reward claimed');
  assert.equal(claimedGoalUi.claimPresent, false);
  assert.equal(claimedGoalUi.claimedDisabled, true);
  assert.match(claimedGoalUi.rewardText, /Reward claimed.*400 gold/);
  const claimedGoalFile = path.join(out, 'objectives-future-equipment-goal-claimed-825x375.png');
  await page.setViewportSize({ width: 825, height: 375 });
  const claimedGoalPanelScroll = await scrollElementIntoPanel('#scene-ui', '#scene-ui [data-equipment-goal="q5"]', 'claimed Q5 825x375');
  await page.screenshot({ path: claimedGoalFile });
  report.futureEquipmentGoal.rewardClaim = { goalGoldDelta, elapsedMs: goalClaimElapsedMs, ...claimedGoalUi, panelScroll: claimedGoalPanelScroll, screenshot: path.relative(root, claimedGoalFile) };
  await page.locator('[data-choice="nav:hero"]').first().click();
  await page.locator('#app[data-view="hero"]').waitFor({ state: 'attached', timeout: 10000 });
  await page.setViewportSize({ width: 1280, height: 720 });
  report.finalState = {
    age: (await read()).state.age,
    hallLevel: (await read()).state.plots.find(plot => plot.id === 'townhall').level,
    wallLevel: (await read()).state.walls.level,
    resources: { ...(await read()).state.resources },
    barracksLevel: (await read()).state.plots.find(plot => plot.id === 'P06')?.level || 0,
    armyStacks: (await read()).state.army.map(stack => ({ id: stack.id, age: stack.age, type: stack.type, count: stack.count })),
    elapsedControlledMs: (await read()).state.clock - report.startClock,
  };

  const beforeReload = (await read()).state;
  await page.locator('#save').click();
  await page.waitForTimeout(100);
  await page.reload({ waitUntil: 'networkidle' });
  let snapshot = await read();
  if (snapshot?.view === 'home' && await page.locator('[data-choice="continue"]').isVisible()) await clickChoice('continue');
  const reloaded = await waitForState(state => state.age === 7 && state.walls.level === 8, 'Future wall state after reload');
  const reloadElapsedMs = reloaded.clock - beforeReload.clock;
  const reloadGoldDelta = reloaded.resources.gold - beforeReload.resources.gold
    - rates(beforeReload).gold * reloadElapsedMs / 1000;
  report.reload = {
    age: reloaded.age,
    wallLevel: reloaded.walls.level,
    hallLevel: reloaded.plots.find(plot => plot.id === 'townhall').level,
    barracksLevel: reloaded.plots.find(plot => plot.id === 'P06')?.level || 0,
    armyStacks: reloaded.army.map(stack => ({ id: stack.id, age: stack.age, type: stack.type, count: stack.count })),
    equippedSlots: Object.fromEntries(['helm', 'weapon', 'offhand', 'armor', 'boots', 'accessory'].map(slot => [slot, reloaded.hero.equip[slot]?.id || ''])),
    q5Claimed: Boolean(reloaded.quests.q5.claimed),
    q5RepeatRewardGold: reloadGoldDelta,
    q5ReloadElapsedMs: reloadElapsedMs,
    storyChapter: reloaded.story.chapter,
    storyChoices: [...reloaded.story.choices],
    futureSeen: reloaded.story.futureSeen,
    stateId: reloaded.id,
  };
  assert.equal(report.reload.age, 7);
  assert.equal(report.reload.wallLevel, 8);
  assert.equal(report.reload.barracksLevel, 8, 'all legal Barracks upgrades survive save and reload');
  assert.equal(report.reload.q5Claimed, true, 'the equipment quest claim survives save and reload');
  assert.ok(Math.abs(report.reload.q5RepeatRewardGold) < 1e-6, 'reload does not issue the equipment reward a second time');
  assert.equal(report.reload.armyStacks.length, 10, 'the full army capacity is naturally retained after reload');
  assert.equal(report.armyRecruits.length, 8, 'one current-age role stack is naturally recruited at every age');
  assert.ok(report.armyRecruits.every((entry, age) => entry.age === age && entry.count === 5 && entry.barracksLevel === age + 1), 'eight age-specific recruits use legal Barracks capacity and costs');
  assert.ok(Object.values(report.reload.equippedSlots).every(Boolean), 'all six Future slots survive save and reload');
  assert.equal(report.storyChapters.length, data.STORY.length, 'each of the seven age-gated story chapters was resolved through visible controls');
  assert.ok(report.storyChapters.every((chapter, index) => chapter.index === index && chapter.age === index), 'chapters were resolved at their corresponding natural age');
  assert.equal(report.futureConclusion?.acknowledged, true, 'the Future conclusion was naturally acknowledged');
  assert.equal(report.reload.storyChapter, data.STORY.length, 'all story chapter progress survives save and reload');
  assert.deepEqual(report.reload.storyChoices, data.STORY.map(chapter => chapter.ch[0].flag), 'each chosen story branch survives save and reload');
  assert.equal(report.reload.futureSeen, true, 'the Future conclusion acknowledgment survives save and reload');

  await page.locator('[data-choice="nav:kingdom"]').first().click();
  await page.locator('#app[data-view="kingdom"]').waitFor({ state: 'attached', timeout: 10000 });
  await buildAt('P07', 'workshop');
  await buildSiteToLevel('P07', 'workshop', 2);
  let endlessState = (await read()).state;
  assert.equal(endlessState.plots.find(plot => plot.id === 'P07')?.level, 2, 'a normally built Siege Workshop opens two additional tower slots');
  const q6ManaPreparation = {
    heroClass: endlessState.hero.class,
    knowledge: heroStats(endlessState, data).kno,
    manaMaximum: manaMax(endlessState, data),
    initialMana: endlessState.hero.mana,
    endDays: [],
  };
  let manaDays = 0;
  while (endlessState.hero.mana < 40 && manaDays < 4) {
    const priorDay = endlessState.day;
    const endDayButton = page.locator('#choices [data-choice="end-day"]').first();
    if (!(await endDayButton.isVisible().catch(() => false))) {
      const close = page.locator('#panel-close');
      if (await close.isVisible().catch(() => false)) await close.click();
      const manage = page.locator('#dock [data-choice="kingdom-actions-open"]');
      await manage.waitFor({ state: 'visible', timeout: 10000 });
      await manage.click();
    }
    await clickChoice('end-day');
    endlessState = await waitForState(state => state.day === priorDay + 1, 'normal End Day mana recovery');
    q6ManaPreparation.endDays.push({ day: endlessState.day, mana: endlessState.hero.mana, maximum: manaMax(endlessState, data) });
    manaDays += 1;
  }
  q6ManaPreparation.manaAtDeployment = endlessState.hero.mana;
  assert.ok(endlessState.hero.mana >= 40, `the naturally equipped Knight must recover enough mana for the visible defense blast (KNO ${q6ManaPreparation.knowledge}, max ${q6ManaPreparation.manaMaximum}, current ${endlessState.hero.mana})`);
  await page.locator('[data-choice="nav:war"]').first().click();
  await page.locator('#app[data-view="war"]').waitFor({ state: 'attached', timeout: 10000 });
  await clickChoice('start-endless');
  await page.locator('#app[data-view="defense"]').waitFor({ state: 'attached', timeout: 10000 });
  await page.locator('#dock [data-choice="inspect:defense"]').click();
  await page.locator('#choices [data-choice="start-endless"]').waitFor({ state: 'visible', timeout: 10000 });
  endlessState = (await read()).state;
  const preparationBudget = {};
  const addPreparationCost = payment => {
    for (const [resource, amount] of Object.entries(payment)) preparationBudget[resource] = (preparationBudget[resource] || 0) + amount;
  };
  for (const family of ['splash', 'support']) addPreparationCost(towerPurchaseCost(data, family, 7));
  for (const tower of endlessState.towers.filter(tower => tower.tier < 7)) {
    const factor = tower.tier + 1;
    addPreparationCost({ wood: 120 * factor, stone: 100 * factor, gold: 80 * factor });
  }
  await waitForResources(preparationBudget, 'Future tower purchases and current-age retrofits');
  const endlessViewportCaptures = [];
  for (const size of ['825x375', '1280x720']) {
    const [width, height] = size.split('x').map(Number);
    await page.setViewportSize({ width, height });
    await page.locator('#choices').evaluate(element => { element.scrollTop = 0; });
    await page.waitForTimeout(80);
    const file = path.join(out, 'endless-preparation-four-families-' + size + '.png');
    await page.screenshot({ path: file });
    const topLayout = await page.evaluate(() => {
      const panel = document.querySelector('#panel')?.getBoundingClientRect();
      const choices = document.querySelector('#choices')?.getBoundingClientRect();
      const start = document.querySelector('#choices [data-choice="start-endless"]')?.getBoundingClientRect();
      return {
        panel: panel ? { top: panel.top, bottom: panel.bottom } : null,
        choices: choices ? { top: choices.top, bottom: choices.bottom, clientHeight: document.querySelector('#choices').clientHeight, scrollHeight: document.querySelector('#choices').scrollHeight } : null,
        start: start ? { top: start.top, bottom: start.bottom, withinPanel: Boolean(panel && start.top >= panel.top && start.bottom <= panel.bottom), withinChoices: Boolean(choices && start.top >= choices.top && start.bottom <= choices.bottom) } : null,
      };
    });
    assert.equal(topLayout.start?.withinPanel, true, 'the primary Start Endless action stays inside the visible preparation panel');
    assert.equal(topLayout.start?.withinChoices, true, 'the primary Start Endless action stays inside the visible action rail');
    let rosterScreenshot = '';
    let scrolledRetrofit = null;
    if (size === '825x375') {
      const retrofit = page.locator('#choices [data-choice="retrofit:tower-1"]');
      await retrofit.scrollIntoViewIfNeeded();
      scrolledRetrofit = await page.evaluate(() => {
        const choices = document.querySelector('#choices')?.getBoundingClientRect();
        const retrofit = document.querySelector('#choices [data-choice="retrofit:tower-1"]')?.getBoundingClientRect();
        const start = document.querySelector('#choices [data-choice="start-endless"]')?.getBoundingClientRect();
        return { retrofitWithinRail: Boolean(choices && retrofit && retrofit.top >= choices.top && retrofit.bottom <= choices.bottom), stickyStartWithinRail: Boolean(choices && start && start.top >= choices.top && start.bottom <= choices.bottom), scrollTop: document.querySelector('#choices')?.scrollTop || 0 };
      });
      assert.equal(scrolledRetrofit.retrofitWithinRail, true, 'the compact roster scrolls its retrofit control into the panel action rail');
      assert.equal(scrolledRetrofit.stickyStartWithinRail, true, 'Start Endless remains available while the compact roster scrolls');
      rosterScreenshot = path.join(out, 'endless-preparation-roster-825x375.png');
      await page.screenshot({ path: rosterScreenshot });
      await page.locator('#choices').evaluate(element => { element.scrollTop = 0; });
    }
    const controls = await page.locator('#choices [data-choice^="buy-tower:"]').evaluateAll(nodes => nodes.map(node => {
      const box = node.getBoundingClientRect();
      return { family: node.dataset.choice.slice('buy-tower:'.length), label: node.getAttribute('aria-label'), enabled: !node.disabled && node.getAttribute('aria-disabled') !== 'true', x: box.x, y: box.y, width: box.width, height: box.height };
    }));
    assert.ok(controls.length >= 2, 'Endless preparation exposes the two additional tower purchases');
    assert.ok(controls.every(control => control.width > 0 && control.height > 0 && control.label), 'tower purchase controls have visible bounds and accessible cost names');
    assert.deepEqual(controls.filter(control => control.enabled).map(control => control.family).sort(), ['splash', 'support'], 'only unowned tower families are purchasable');
    const retrofitControls = await page.locator('#choices [data-choice^="retrofit:"]').evaluateAll(nodes => nodes.map(node => {
      const box = node.getBoundingClientRect();
      return { towerId: node.dataset.choice.slice('retrofit:'.length), label: node.getAttribute('aria-label'), enabled: !node.disabled && node.getAttribute('aria-disabled') !== 'true', x: box.x, y: box.y, width: box.width, height: box.height };
    }));
    assert.equal(retrofitControls.length, 2, 'the two Stone starter towers expose current-age retrofit actions');
    assert.ok(retrofitControls.every(control => control.enabled && control.width > 0 && control.height > 0 && control.label), 'affordable retrofits have visible bounds and accessible prices');
    endlessViewportCaptures.push({ size, file: path.relative(root, file), topLayout, rosterScreenshot: rosterScreenshot ? path.relative(root, rosterScreenshot) : '', scrolledRetrofit, controls, retrofitControls });
  }
  for (const towerId of ['tower-1', 'tower-2']) {
    const tower = endlessState.towers.find(item => item.id === towerId);
    assert.ok(tower && tower.tier < 7, `${towerId} is eligible for a Future retrofit`);
    const factor = tower.tier + 1;
    await waitForResources({ wood: 120 * factor, stone: 100 * factor, gold: 80 * factor }, `retrofit ${tower.fam} to Future`);
    await clickChoice('retrofit:' + towerId);
    endlessState = await waitForState(state => state.towers.find(item => item.id === towerId)?.tier === 7, `retrofit ${tower.fam} to Future`);
  }
  await waitForResources(towerPurchaseCost(data, 'splash', 7), 'Future Splash Tower');
  await clickChoice('buy-tower:splash');
  endlessState = await waitForState(state => state.towers.some(tower => tower.fam === 'splash'), 'buy Future Splash Tower');
  await waitForResources(towerPurchaseCost(data, 'support', 7), 'Future Support Tower');
  await clickChoice('buy-tower:support');
  endlessState = await waitForState(state => state.towers.some(tower => tower.fam === 'support'), 'buy Future Support Tower');
  assert.equal(endlessState.towers.length, 4, 'two legal purchases fill the level-2 Workshop tower capacity');
  assert.ok(endlessState.towers.every(tower => tower.tier === 7), 'all four owned tower families are at Future tier before deployment');
  const siegeArmy = endlessState.army
    .filter(stack => stack.kind === 'role' && stack.type === 'heavy' && stack.age === 6 && stack.count > 0)
    .map(stack => ({ stack, stats: unitStats(stack, data) }))
    .sort((a, b) => (b.stack.count * b.stats.hp) - (a.stack.count * a.stats.hp))[0];
  assert.ok(siegeArmy, 'the naturally recruited Modern heavy formation is present for Campaign Siege');
  const siegeEvidence = { progress: [], heroCasts: [] };
  report.q6 = {
    workshop: { siteId: 'P07', level: endlessState.plots.find(plot => plot.id === 'P07')?.level || 0 },
    towersBeforeSiege: endlessState.towers.map(tower => ({ family: tower.fam, tier: tower.tier, rank: tower.rank })),
    preparationViewports: endlessViewportCaptures,
    siegeArmy: { id: siegeArmy.stack.id, age: siegeArmy.stack.age, role: siegeArmy.stack.type, count: siegeArmy.stack.count, rank: siegeArmy.stack.rank, hpPerUnit: siegeArmy.stats.hp, damagePerUnit: [siegeArmy.stats.dmin, siegeArmy.stats.dmax], block: siegeArmy.stats.block },
    siege: siegeEvidence,
    manaPreparation: q6ManaPreparation,
  };
  await clickChoice('defense-mode:siege');
  await clickChoice('start-siege');
  let siege = await waitForState(state => state.defense?.practice === 'siege' && state.defense.paused, 'paused five-wave Future Campaign Siege');
  assert.equal(siege.defense.waves, 5, 'Campaign Siege schedules five waves');
  assert.deepEqual(siege.defense.towers.map(tower => tower.fam).sort(), ['arrow', 'slow', 'splash', 'support']);
  await page.locator('#dock [data-choice="inspect:defense"]').click();
  await clickChoice('deploy-hero');
  siege = await waitForState(state => state.defense?.heroDeployed, 'deploy the Future Hero for Campaign Siege');
  await clickChoice('deploy-army:' + siegeArmy.stack.id);
  siege = await waitForState(state => state.defense?.armyDeployed, 'deploy the Modern heavy formation for Campaign Siege');
  assert.equal(siege.defense.paused, true, 'deployment preserves the paused Siege setup phase');
  await clickChoice('defense-speed');
  siege = await waitForState(state => state.defense?.speed === 2 && state.defense.paused, 'select 2x without resuming Siege');
  const siegeDeployedScreenshot = path.join(out, 'siege-deployed-paused-825x375.png');
  await page.setViewportSize({ width: 825, height: 375 });
  await page.screenshot({ path: siegeDeployedScreenshot });
  await clickChoice('defense-pause');
  siege = await waitForState(state => state.defense?.paused === false, 'resume Future Campaign Siege');
  let siegeLastWave = 0;
  const siegeDeadline = Date.now() + 2 * 60 * 1000;
  while (Date.now() < siegeDeadline) {
    await page.clock.runFor(5000);
    siege = (await read()).state;
    const defense = siege.defense;
    if (!defense) throw new Error('Campaign Siege session disappeared before settlement');
    if (defense.clearedWaves !== siegeLastWave) {
      siegeLastWave = defense.clearedWaves;
      const progress = { clearedWaves: defense.clearedWaves, scheduledWaves: defense.waves, core: defense.core, elapsedSimSeconds: defense.time, towers: defense.towers.map(tower => ({ family: tower.fam, hp: tower.hp, xp: tower.xp })), heroHp: defense.heroHp, army: defense.army ? { role: defense.army.role, hp: defense.army.hp } : null };
      siegeEvidence.progress.push(progress);
      console.log(JSON.stringify({ checkpoint: 'future-siege-wave', ...progress }));
      if ([1, 3, 5].includes(siegeLastWave)) {
        const file = path.join(out, `future-siege-wave-${siegeLastWave}-825x375.png`);
        await page.screenshot({ path: file });
        siegeEvidence.progress[siegeEvidence.progress.length - 1].screenshot = path.relative(root, file);
      }
    }
    if (!defense.pendingSettlement) {
      const blast = bestDefenseBlast(siege);
      if (blast) {
        const manaBefore = siege.hero.mana;
        if (!defense.paused) {
          await clickChoice('defense-pause');
          siege = await waitForState(state => state.defense?.paused, 'pause to aim the Siege hero blast');
        }
        await clickChoice('defense-cast');
        const cell = page.locator(`#world [data-kind="blast"][data-cell="${blast.x},${blast.y}"]`);
        await cell.waitFor({ state: 'attached', timeout: 5000 });
        await cell.click();
        siege = await waitForState(state => state.hero.mana <= manaBefore - 40 + 1e-6, 'spend mana on the visible Siege hero blast');
        siegeEvidence.heroCasts.push({ wave: siege.defense?.clearedWaves ?? defense.clearedWaves, cell: [blast.x, blast.y], center: blast.center, manaBefore, manaAfter: siege.hero.mana, spellDamage: blast.damage, targets: blast.hits.map(enemy => ({ id: enemy.id, role: enemy.role, boss: enemy.boss, hp: enemy.hp })), predictedKills: blast.kills, effectiveDamage: blast.effectiveDamage });
        if (siege.defense?.status === 'ACTIVE' && !siege.defense.pendingSettlement) {
          await clickChoice('defense-pause');
          siege = await waitForState(state => state.defense?.paused === false, 'resume after the Siege hero blast');
        }
      }
    }
    if (defense.pendingSettlement) break;
  }
  siege = (await read()).state;
  assert.ok(siege.defense?.pendingSettlement, 'Future Campaign Siege ends naturally and opens its result');
  assert.equal(siege.defense.winner, 'p', 'the naturally fielded Future defenses win Campaign Siege');
  siegeEvidence.result = { winner: siege.defense.winner, clearedWaves: siege.defense.clearedWaves, scheduledWaves: siege.defense.waves, core: siege.defense.core, elapsedSimSeconds: siege.defense.time };
  const siegeResultScreenshot = path.join(out, 'siege-victory-pending-825x375.png');
  await page.screenshot({ path: siegeResultScreenshot });
  siegeEvidence.result.screenshot = path.relative(root, siegeResultScreenshot);
  const beforeSiegeSettlement = siege;
  await clickChoice('settle-defense');
  endlessState = await waitForState(state => state.defense == null, 'settle Campaign Siege rewards and tower experience');
  siegeEvidence.reward = { gold: endlessState.resources.gold - beforeSiegeSettlement.resources.gold, food: endlessState.resources.food - beforeSiegeSettlement.resources.food };
  siegeEvidence.armyAfterSettlement = endlessState.army.find(stack => stack.id === siegeArmy.stack.id) || null;
  const towersAfterSiege = endlessState.towers.map(tower => ({ family: tower.fam, tier: tower.tier, rank: tower.rank, xp: tower.xp }));
  assert.ok(endlessState.towers.find(tower => tower.fam === 'splash')?.rank >= 3, 'naturally earned Siege experience raises the Future Splash Tower to rank 3 or higher');
  report.q6.towersAfterSiege = towersAfterSiege;
  const recoveredMana = { days: 0, initial: endlessState.hero.mana, maximum: manaMax(endlessState, data), readings: [] };
  await page.locator('[data-choice="nav:kingdom"]').first().click();
  await page.locator('#app[data-view="kingdom"]').waitFor({ state: 'attached', timeout: 10000 });
  while (endlessState.hero.mana < 40 && recoveredMana.days < 4) {
    const priorDay = endlessState.day;
    const endDayButton = page.locator('#choices [data-choice="end-day"]').first();
    if (!(await endDayButton.isVisible().catch(() => false))) {
      const close = page.locator('#panel-close');
      if (await close.isVisible().catch(() => false)) await close.click();
      const manage = page.locator('#dock [data-choice="kingdom-actions-open"]');
      await manage.waitFor({ state: 'visible', timeout: 10000 });
      await manage.click();
    }
    await clickChoice('end-day');
    endlessState = await waitForState(state => state.day === priorDay + 1, 'normal End Day recovery before Future Endless');
    recoveredMana.days += 1;
    recoveredMana.readings.push({ day: endlessState.day, mana: endlessState.hero.mana, maximum: manaMax(endlessState, data) });
  }
  assert.ok(endlessState.hero.mana >= 40, 'the naturally recovered Hero has enough mana for an Endless blast');
  report.q6.manaPreparation = { ...q6ManaPreparation, afterSiege: recoveredMana };
  await page.locator('[data-choice="nav:war"]').first().click();
  await page.locator('#app[data-view="war"]').waitFor({ state: 'attached', timeout: 10000 });
  await clickChoice('start-endless');
  await page.locator('#app[data-view="defense"]').waitFor({ state: 'attached', timeout: 10000 });
  await page.locator('#dock [data-choice="inspect:defense"]').click();
  await page.locator('#choices [data-choice="start-endless"]').waitFor({ state: 'visible', timeout: 10000 });
  endlessState = (await read()).state;
  const selectedArmy = endlessState.army
    .filter(stack => stack.kind === 'role' && stack.type === 'ranged' && stack.count > 0)
    .map(stack => ({ stack, stats: unitStats(stack, data) }))
    .sort((a, b) => (b.stack.count * (b.stats.dmin + b.stats.dmax)) - (a.stack.count * (a.stats.dmin + a.stats.dmax)))[0]
    || endlessState.army.filter(stack => stack.kind === 'role' && stack.count > 0)
      .map(stack => ({ stack, stats: unitStats(stack, data) }))
      .sort((a, b) => (b.stack.count * b.stats.hp) - (a.stack.count * a.stats.hp))[0];
  assert.ok(selectedArmy, 'a surviving earned formation remains for Future Endless');
  await clickChoice('start-endless');
  let endless = await waitForState(state => state.defense?.practice === 'endless' && state.defense.paused, 'paused Future Endless session after tower training');
  assert.deepEqual(endless.defense.towers.map(tower => tower.fam).sort(), ['arrow', 'slow', 'splash', 'support']);
  const ownedSplash = endlessState.towers.find(tower => tower.fam === 'splash');
  const runtimeSplash = endless.defense.towers.find(tower => tower.fam === 'splash');
  assert.ok(runtimeSplash && runtimeSplash.dmg > towerStats({ ...ownedSplash, rank: 0 }, data).dmg, 'the Endless session applies the Splash Tower rank to its runtime damage');
  await page.locator('#dock [data-choice="inspect:defense"]').click();
  await clickChoice('deploy-hero');
  endless = await waitForState(state => state.defense?.heroDeployed, 'deploy the Future Hero');
  await clickChoice('deploy-army:' + selectedArmy.stack.id);
  endless = await waitForState(state => state.defense?.armyDeployed, 'deploy the surviving mature roster stack');
  assert.equal(endless.defense.paused, true, 'deployment preserves the paused Endless setup phase');
  const deployedScreenshot = path.join(out, 'endless-deployed-paused-825x375.png');
  await page.setViewportSize({ width: 825, height: 375 });
  await page.screenshot({ path: deployedScreenshot });
  await clickChoice('defense-pause');
  endless = await waitForState(state => state.defense?.paused === false, 'resume Future Endless');
  Object.assign(report.q6, {
    workshop: { siteId: 'P07', level: endlessState.plots.find(plot => plot.id === 'P07')?.level || 0 },
    towers: endlessState.towers.map(tower => ({ family: tower.fam, tier: tower.tier, rank: tower.rank })),
    towersAfterSiege,
    preparationViewports: endlessViewportCaptures,
    selectedArmy: { id: selectedArmy.stack.id, age: selectedArmy.stack.age, role: selectedArmy.stack.type, count: selectedArmy.stack.count, rank: selectedArmy.stack.rank, hpPerUnit: selectedArmy.stats.hp, damagePerUnit: [selectedArmy.stats.dmin, selectedArmy.stats.dmax], block: selectedArmy.stats.block },
    siegeArmy: { id: siegeArmy.stack.id, age: siegeArmy.stack.age, role: siegeArmy.stack.type, count: siegeArmy.stack.count, rank: siegeArmy.stack.rank, hpPerUnit: siegeArmy.stats.hp, damagePerUnit: [siegeArmy.stats.dmin, siegeArmy.stats.dmax], block: siegeArmy.stats.block },
    siege: siegeEvidence,
    manaPreparation: { ...q6ManaPreparation, afterSiege: recoveredMana },
    deployedScreenshot: path.relative(root, deployedScreenshot),
    speed: 2,
    progress: [],
    heroCasts: [],
  });
  let lastWave = 0;
  const capturedWaves = new Set();
  const endlessDeadline = Date.now() + 5 * 60 * 1000;
  while (Date.now() < endlessDeadline) {
    await page.clock.runFor(5000);
    endless = (await read()).state;
    const defense = endless.defense;
    if (!defense) throw new Error('Future Endless session disappeared before settlement');
    if (defense.clearedWaves !== lastWave) {
      lastWave = defense.clearedWaves;
      const progress = { clearedWaves: defense.clearedWaves, scheduledWaves: defense.waves, core: defense.core, elapsedSimSeconds: defense.time, towers: defense.towers.map(tower => ({ family: tower.fam, hp: tower.hp })), heroHp: defense.heroHp, army: defense.army ? { role: defense.army.role, hp: defense.army.hp } : null };
      report.q6.progress.push(progress);
      console.log(JSON.stringify({ checkpoint: 'future-endless-wave', ...progress }));
      if ([1, 3, 6, 9, 10].includes(lastWave) && !capturedWaves.has(lastWave)) {
        capturedWaves.add(lastWave);
        await page.setViewportSize({ width: lastWave === 10 ? 1280 : 825, height: lastWave === 10 ? 720 : 375 });
        const file = path.join(out, `future-endless-wave-${lastWave}-${lastWave === 10 ? '1280x720' : '825x375'}.png`);
        await page.screenshot({ path: file });
        report.q6.progress[report.q6.progress.length - 1].screenshot = path.relative(root, file);
      }
    }
    if (!defense.pendingSettlement) {
      const blast = bestDefenseBlast(endless);
      if (blast) {
        const manaBefore = endless.hero.mana;
        if (!defense.paused) {
          await clickChoice('defense-pause');
          endless = await waitForState(state => state.defense?.paused, 'pause to aim the hero blast');
        }
        await clickChoice('defense-cast');
        const cell = page.locator(`#world [data-kind="blast"][data-cell="${blast.x},${blast.y}"]`);
        await cell.waitFor({ state: 'attached', timeout: 5000 });
        await cell.click();
        endless = await waitForState(state => state.hero.mana <= manaBefore - 40 + 1e-6, 'spend mana on the visible hero blast');
        report.q6.heroCasts.push({ wave: endless.defense?.clearedWaves ?? defense.clearedWaves, cell: [blast.x, blast.y], center: blast.center, manaBefore, manaAfter: endless.hero.mana, spellDamage: blast.damage, targets: blast.hits.map(enemy => ({ id: enemy.id, role: enemy.role, boss: enemy.boss, hp: enemy.hp })), predictedKills: blast.kills, effectiveDamage: blast.effectiveDamage });
        if (endless.defense?.status === 'ACTIVE' && !endless.defense.pendingSettlement) {
          await clickChoice('defense-pause');
          endless = await waitForState(state => state.defense?.paused === false, 'resume after the hero blast');
        }
      }
    }
    if (defense.pendingSettlement) break;
  }
  endless = (await read()).state;
  assert.ok(endless.defense?.pendingSettlement, 'Future Endless ends naturally and opens its result');
  assert.equal(endless.defense.winner, 'e');
  const clearedWaves = endless.defense.clearedWaves;
  report.q6.result = { winner: endless.defense.winner, clearedWaves, core: endless.defense.core, scheduledWaves: endless.defense.waves, elapsedSimSeconds: endless.defense.time };
  assert.ok(clearedWaves >= 10, `the naturally progressed Future campaign must survive ten Endless waves; reached ${clearedWaves}`);
  const resultScreenshot = path.join(out, 'future-endless-result-825x375.png');
  await page.setViewportSize({ width: 825, height: 375 });
  await page.screenshot({ path: resultScreenshot });
  report.q6.result.screenshot = path.relative(root, resultScreenshot);
  await clickChoice('settle-defense');
  const settledEndless = await waitForState(state => state.defense == null, 'settle Future Endless loss');
  assert.ok(Math.max(...Object.entries(settledEndless.story.flags).filter(([key]) => key.startsWith('endless:')).map(([, waves]) => waves)) >= 10, 'settlement records the ten-wave campaign best');
  await page.locator('#context').click();
  await clickChoice('menu:story');
  await page.locator('#app[data-view="story"]').waitFor({ state: 'attached', timeout: 10000 });
  if (!settledEndless.story.rival) await clickChoice('journal-rival:' + data.RIVALS[0]);
  await clickChoice('journal:quests');
  await page.waitForFunction(() => Boolean(document.querySelector('#scene-ui [data-quest-id="q6"]')));
  const q6Goal = page.locator('#scene-ui [data-quest-id="q6"]');
  const q6ViewportCaptures = [];
  for (const size of ['825x375', '1280x720']) {
    const [width, height] = size.split('x').map(Number);
    await page.setViewportSize({ width, height });
    const panelScroll = await scrollElementIntoPanel('#scene-ui', '#scene-ui [data-quest-id="q6"]', `Q6 ${size}`);
    await page.waitForTimeout(100);
    const view = await q6Goal.evaluate(element => {
      const panel = document.querySelector('#scene-ui')?.getBoundingClientRect();
      const bounds = element.getBoundingClientRect();
      const claim = element.querySelector('[data-choice="journal-claim:q6"]');
      return { text: element.innerText.replace(/\s+/g, ' ').trim(), status: element.querySelector('p')?.textContent?.trim() || '', progress: element.querySelector('.quest-progress')?.textContent?.trim() || '', reward: element.querySelector('.quest-reward')?.innerText?.replace(/\s+/g, ' ').trim() || '', claimPresent: Boolean(claim), claimDisabled: claim?.disabled ?? null, panelBounds: panel ? { top: panel.top, bottom: panel.bottom, height: panel.height } : null, cardBounds: { top: bounds.top, bottom: bounds.bottom, height: bounds.height }, fullyInPanel: Boolean(panel && bounds.top >= panel.top && bounds.bottom <= panel.bottom) };
    });
    const file = path.join(out, 'q6-endless-ready-' + size + '.png');
    await page.screenshot({ path: file });
    q6ViewportCaptures.push({ size, ...view, panelScroll, file: path.relative(root, file) });
    report.q6.partialReady = q6ViewportCaptures;
    assert.match(view.progress, /^10 \/ 10 Endless waves$/);
    assert.equal(view.status, 'Ready to claim');
    assert.match(view.reward, /500/);
    assert.match(view.reward, /300/);
    assert.equal(view.claimPresent, true);
    assert.equal(view.claimDisabled, false);
    assert.equal(view.fullyInPanel, true, `Q6 is fully visible in the journal panel: ${JSON.stringify(view)}`);
  }
  const beforeQ6Claim = (await read()).state;
  await page.locator('#scene-ui [data-choice="journal-claim:q6"]').click();
  const afterQ6Claim = await waitForState(state => state.quests.q6.claimed, 'claim the endless survival reward');
  const q6Elapsed = afterQ6Claim.clock - beforeQ6Claim.clock;
  const q6Income = rates(beforeQ6Claim);
  const q6Payout = Object.fromEntries(['gold', 'stone'].map(resource => [resource,
    afterQ6Claim.resources[resource] - beforeQ6Claim.resources[resource] - q6Income[resource] * q6Elapsed / 1000]));
  assert.ok(Math.abs(q6Payout.gold - 500) < 1e-6, 'Q6 grants exactly 500 gold after passive income');
  assert.ok(Math.abs(q6Payout.stone - 300) < 1e-6, 'Q6 grants exactly 300 stone after passive income');
  const q6ClaimScreenshot = path.join(out, 'q6-endless-claimed-825x375.png');
  await page.setViewportSize({ width: 825, height: 375 });
  await q6Goal.evaluate(element => element.scrollIntoView({ block: 'center', inline: 'nearest' }));
  await page.screenshot({ path: q6ClaimScreenshot });
  const beforeQ6Reload = afterQ6Claim;
  await page.locator('#save').click();
  await page.waitForTimeout(100);
  await page.reload({ waitUntil: 'networkidle' });
  let q6Reload = await waitForState(state => state.id === report.reload.stateId, 'Future campaign after Q6 reload');
  if (await page.locator('[data-choice="continue"]').isVisible().catch(() => false)) {
    await clickChoice('continue');
    q6Reload = await waitForState(state => state.id === report.reload.stateId, 'continue the saved Future campaign');
  }
  const q6ReloadElapsed = q6Reload.clock - beforeQ6Reload.clock;
  const q6RepeatPayout = Object.fromEntries(['gold', 'stone'].map(resource => [resource,
    q6Reload.resources[resource] - beforeQ6Reload.resources[resource] - q6Income[resource] * q6ReloadElapsed / 1000]));
  assert.equal(q6Reload.quests.q6.claimed, true, 'Q6 claim survives save and reload');
  assert.ok(Math.abs(q6RepeatPayout.gold) < 1e-6, 'reload does not pay Q6 gold twice');
  assert.ok(Math.abs(q6RepeatPayout.stone) < 1e-6, 'reload does not pay Q6 stone twice');
  report.q6.ready = q6ViewportCaptures;
  report.q6.payout = q6Payout;
  report.q6.repeatPayoutAfterReload = q6RepeatPayout;
  report.q6.claimedScreenshot = path.relative(root, q6ClaimScreenshot);
} catch (error) {
  report.error = String(error);
  report.errorStack = error?.stack || '';
} finally {
  report.errors = [...new Set(report.errors)];
  report.passed = !report.error
    && report.errors.length === 0
    && report.ages.length === 8
    && report.ages.every(age => age && age.wallPhases.length >= 1)
    && report.storyChapters.length === data.STORY.length
    && report.futureConclusion?.acknowledged === true
    && report.finalState?.age === 7
    && report.reload?.age === 7
    && report.reload?.wallLevel === 8
    && Object.values(report.reload?.equippedSlots || {}).length === 6
    && Object.values(report.reload?.equippedSlots || {}).every(Boolean)
    && report.weapons.length === 8
    && report.futureLoadout?.length === 5
    && report.futureLoadout.every(item => item.wornState === 'worn' && item.heroCardIcon)
    && report.futureLoadoutVisual?.slots?.length === 6
    && report.futureEquipmentGoal?.viewports?.length === 2
    && report.futureEquipmentGoal.viewports.every(view => view.fullyInPanel && view.q5ClaimReady && view.slots.length === 6)
    && Math.abs(report.futureEquipmentGoal?.rewardClaim?.goalGoldDelta - 400) < 1e-6
    && report.futureEquipmentGoal.rewardClaim.goalState === 'claimed'
    && Math.abs(report.reload?.q5RepeatRewardGold) < 1e-6
    && report.q6?.workshop?.level === 2
    && report.q6?.towers?.length === 4
    && report.q6?.result?.clearedWaves >= 10
    && report.q6.ready?.length === 2
    && Math.abs(report.q6?.payout?.gold - 500) < 1e-6
    && Math.abs(report.q6?.payout?.stone - 300) < 1e-6
    && Math.abs(report.q6?.repeatPayoutAfterReload?.gold) < 1e-6
    && Math.abs(report.q6?.repeatPayoutAfterReload?.stone) < 1e-6
    && report.futureLoadoutVisual.slots.every(slot => slot.state === 'worn' && slot.itemId)
    && ['helm', 'weapon', 'offhand', 'armor', 'boots', 'accessory'].every(name => report.futureLoadoutVisual.slots.find(slot => slot.slot === name)?.appearance === 'attached-asset')
    && report.futureLoadoutVisual?.cards?.length === 6
    && report.futureLoadoutVisual.cards.every(card => card.worn === '1' && card.icon)
    && report.armyAgePresentations.length === 8
    && report.armyAgePresentations.every((entry, age) => entry.age === age
      && entry.cards.length === 3 && entry.cards.every(card => card.imageLoaded)
      && entry.showcase.length === 3 && entry.showcase.every(unit => unit.imageLoaded)
      && entry.focusedFormationVisibleOnOpen
      && entry.viewportLayouts.length === 3 && entry.viewportLayouts.every(layout => !layout.dockOverlapsFirstFormation && layout.sceneInspectorSeparated && layout.figuresInsideScene && layout.selectedFormationVisible))
    && report.armyAgePresentations.find(entry => entry.age === 3)?.showcaseSelection?.campaignResourcesUnchanged === true
    && report.armyAgePresentations.find(entry => entry.age === 3)?.showcaseSelection?.ownedArmyUnchanged === true
    && report.armyRecruits.length === 8
    && report.reload?.armyStacks?.length === 10
    && report.weapons.every((weapon, age) => weapon.age === age
      && weapon.heroAppearance === 'attached-asset'
      && weapon.heroHref === weaponFiles[age]
      && weapon.adventureAppearance === 'attached-asset'
      && weapon.adventureHref === weaponFiles[age]
      && weapon.genericWeaponJointCount === 0);
  await fs.writeFile(path.join(out, 'army-showcase-live-20261021.json'), JSON.stringify(report, null, 2));
  await context.close();
  await browser.close();
}
console.log(JSON.stringify({ passed: report.passed, error: report.error, ages: report.ages.map(age => ({ age: age.age, name: age.name, phases: age.wallPhases.map(phase => phase.wallPhase) })), rates: report.incomeRates, finalState: report.finalState, reload: report.reload, errors: report.errors, report: path.join(out, 'army-showcase-live-20261021.json') }, null, 2));
if (!report.passed) process.exitCode = 1;
