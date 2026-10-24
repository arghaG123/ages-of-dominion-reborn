import fs from 'node:fs';
import fsp from 'node:fs/promises';
import http from 'node:http';
import path from 'node:path';
import assert from 'node:assert/strict';
import { chromium } from 'file:///C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import data from '../../../src/data/reference-data.json' with { type: 'json' };
import contract from '../../../src/data/implementation-contract.json' with { type: 'json' };
import { newCampaign, command } from '../../../src/core/campaign.js';
import { encode } from '../../../src/core/save.js';

const ROOT_DIR = path.resolve('.');
const OUT_DIR = path.resolve('qa/priority-repair-20261023/remaining-high-medium');
fs.mkdirSync(OUT_DIR, { recursive: true });

const MIME_TYPES = {
  '.html': 'text/html',
  '.mjs': 'text/javascript',
  '.js': 'text/javascript',
  '.json': 'application/json',
  '.css': 'text/css',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.webp': 'image/webp',
  '.avif': 'image/avif',
  '.svg': 'image/svg+xml',
};

async function startIsolatedServer() {
  const server = http.createServer(async (req, res) => {
    try {
      const relative = decodeURIComponent(new URL(req.url, 'http://127.0.0.1').pathname);
      const target = path.resolve(ROOT_DIR, '.' + (relative === '/' ? '/index.html' : relative));
      if (path.relative(ROOT_DIR, target).startsWith('..')) throw new Error('Outside root');
      const body = await fsp.readFile(target);
      res.writeHead(200, {
        'Content-Type': MIME_TYPES[path.extname(target)] ?? 'application/octet-stream',
        'Cache-Control': 'no-store',
      });
      res.end(body);
    } catch {
      res.writeHead(404);
      res.end('Not found');
    }
  });
  await new Promise((resolve, reject) => {
    server.once('error', reject);
    server.listen(0, '127.0.0.1', resolve);
  });
  const addr = server.address();
  return {
    url: `http://127.0.0.1:${addr.port}`,
    close: () => new Promise(resolve => server.close(() => resolve())),
  };
}

function buildStarterCampaign({ id = 'campaign-priority-repair-starter-20261023' } = {}) {
  const state = newCampaign(contract, data, 1700000000000, 123456789);
  state.id = id;
  state.tutorial.skipped = true;
  return state;
}

let stateSeq = 0;

function buildSpellTestState({
  mana = 30,
  wisdom = 3,
  castThisRound = false,
  reducedMotion = false,
  noTargetMode = false,
} = {}) {
  let state = newCampaign(contract, data, 1700000000000, 123456789);
  state.id = `campaign-priority-repair-20261023-${++stateSeq}`;
  state.tutorial.skipped = true;
  state.hero.xp = 120;
  state.hero.skills.wisdom = Math.max(0, Math.min(3, wisdom));
  state.settings.reducedMotion = reducedMotion;
  state = command(state, { id: 'start-sk', type: 'START_SKIRMISH', payload: {} }, 1700000001000, data);
  const movIds = state.battle.deployment.movableIds;
  state = command(state, { id: 'dep-1', type: 'DEPLOY_BATTLE_STACK', payload: { stackId: movIds[0], cell: [1, 6] } }, 1700000001100, data);
  state = command(state, { id: 'dep-2', type: 'DEPLOY_BATTLE_STACK', payload: { stackId: movIds[1], cell: [2, 7] } }, 1700000001200, data);
  state = command(state, { id: 'start-dep', type: 'START_DEPLOYED_BATTLE', payload: {} }, 1700000001300, data);
  state.battle.mana = mana;
  state.battle.wisdom = wisdom;
  state.battle.castThisRound = castThisRound;
  const playerStacks = state.battle.stacks.filter(s => s.side === 'p' && !s.dead);
  const enemyStacks = state.battle.stacks.filter(s => s.side === 'e' && !s.dead);
  if (!noTargetMode) {
    if (playerStacks[0]) {
      playerStacks[0].startCount = Math.max(playerStacks[0].startCount || playerStacks[0].count, 6);
      playerStacks[0].count = 4;
      playerStacks[0].top = Math.max(1, Math.floor(playerStacks[0].uhp / 2));
    }
    if (playerStacks[1]) {
      playerStacks[1].startCount = Math.max(playerStacks[1].startCount || playerStacks[1].count, 6);
      playerStacks[1].count = 3;
      playerStacks[1].top = Math.max(1, Math.floor(playerStacks[1].uhp / 2));
    }
  }
  if (enemyStacks[0] && enemyStacks[1]) {
    enemyStacks[1].x = enemyStacks[0].x;
    enemyStacks[1].y = enemyStacks[0].y > 0 ? enemyStacks[0].y - 1 : enemyStacks[0].y + 1;
  }
  state.battle.queue = [
    ...playerStacks.map(s => s.id),
    ...enemyStacks.map(s => s.id),
  ];
  return state;
}

async function importState(page, stateObj, expectedView = 'kingdom') {
  const raw = encode(stateObj, data);
  const tmpFile = path.join(OUT_DIR, '_tmp-import.json');
  fs.writeFileSync(tmpFile, raw, 'utf8');
  await page.setInputFiles('#import-file', tmpFile);
  await page.waitForFunction(targetId => {
    const snap = window.rebornSnapshot?.();
    const stageField = document.getElementById('stage-field');
    return snap?.id === targetId && !stageField?.inert;
  }, stateObj.id, { timeout: 5000 });
  if (expectedView === 'tactical') {
    const view = await page.evaluate(() => document.getElementById('app')?.dataset?.view);
    if (view !== 'tactical') {
      await page.click('[data-choice="resume-session"]');
      await page.waitForFunction(() => document.getElementById('app')?.dataset?.view === 'tactical', { timeout: 5000 });
    }
  } else if (expectedView) {
    await page.waitForFunction(v => document.getElementById('app')?.dataset?.view === v, expectedView, { timeout: 5000 });
  }
  fs.rmSync(tmpFile, { force: true });
}

async function measureTacticalViewport(page) {
  return page.evaluate(() => {
    const vw = window.innerWidth;
    const vh = window.innerHeight;
    const stageRect = document.getElementById('stage')?.getBoundingClientRect();
    const hudRects = [
      document.getElementById('topbar')?.getBoundingClientRect(),
      document.getElementById('dock')?.getBoundingClientRect(),
      document.querySelector('.tactical-hero-plaque')?.getBoundingClientRect(),
      document.querySelector('.tactical-initiative-rail')?.getBoundingClientRect(),
    ].filter(Boolean);
    const panelOpen = document.getElementById('panel')?.classList.contains('open');
    const panelRect = panelOpen ? document.getElementById('panel')?.getBoundingClientRect() : null;
    const hudArea = hudRects.reduce((sum, r) => sum + Math.max(0, r.width) * Math.max(0, r.height), 0);
    const totalArea = vw * vh;
    const usefulWorldRatio = Number(((totalArea - hudArea) / totalArea).toFixed(4));
    const plaque = document.querySelector('.tactical-hero-plaque');
    const plaqueRect = plaque?.getBoundingClientRect();
    const spellBtn = document.querySelector('#dock [data-tactical-action="spell"]');
    const statusAllowance = document.querySelector('#scene-ui [data-spell-allowance], [data-spell-allowance]');
    return {
      viewport: `${vw}x${vh}`,
      usefulWorldRatio,
      panelOpen: Boolean(panelOpen),
      panelWidth: panelRect ? Math.round(panelRect.width) : 0,
      stageWidth: stageRect ? Math.round(stageRect.width) : 0,
      stageHeight: stageRect ? Math.round(stageRect.height) : 0,
      plaque: plaque ? {
        text: plaque.innerText.replace(/\s+/g, ' ').trim(),
        ariaLabel: plaque.getAttribute('aria-label'),
        width: Math.round(plaqueRect.width),
        height: Math.round(plaqueRect.height),
      } : null,
      spellButton: spellBtn ? {
        disabled: spellBtn.disabled,
        reason: spellBtn.dataset.spellReason || null,
        ariaLabel: spellBtn.getAttribute('aria-label'),
        title: spellBtn.title,
      } : null,
      statusAllowance: statusAllowance ? {
        reason: statusAllowance.dataset.spellAllowance,
        text: statusAllowance.textContent.trim(),
      } : null,
      messageText: document.getElementById('message')?.textContent?.trim() || '',
    };
  });
}

async function sampleWorldFiguresAndEffects(page) {
  return page.evaluate(() => {
    const figures = [...document.querySelectorAll('#world g[data-stack-id]')].map(g => {
      const plateNode = g.querySelector('[data-plate-motion]');
      const imgNode = g.querySelector('image');
      const actorNode = g.querySelector('[data-clip]');
      return {
        stackId: g.dataset.stackId,
        side: g.dataset.stackSide,
        clip: g.dataset.clip,
        targetClip: g.dataset.targetClip || null,
        spellRole: g.dataset.spellRole || null,
        spellId: g.dataset.spellId || null,
        spellCategory: g.dataset.spellCategory || null,
        selfTarget: g.dataset.selfTarget === '1',
        articulation: plateNode?.dataset?.articulation || actorNode?.dataset?.articulation || null,
        file: imgNode?.getAttribute('href') || imgNode?.getAttribute('xlink:href') || null,
        plateMotion: plateNode?.dataset?.plateMotion || null,
        plateTransform: plateNode?.getAttribute('transform') || null,
        actorClip: actorNode?.dataset?.clip || null,
      };
    });
    const spellEffects = [...document.querySelectorAll('#world [data-spell-effect]')].map(g => ({
      targetId: g.dataset.spellEffect,
      spellId: g.dataset.spellId,
      category: g.dataset.spellCategory,
      motif: g.dataset.effectMotif || null,
      selfTarget: g.dataset.selfTarget === '1',
      reducedMotion: g.dataset.reducedMotion === '1',
    }));
    const spellCasters = [...document.querySelectorAll('#world [data-spell-caster]')].map(g => ({
      casterId: g.dataset.spellCaster,
      spellId: g.dataset.spellId,
      category: g.dataset.spellCategory,
      reducedMotion: g.dataset.reducedMotion === '1',
    }));
    const committedFeedback = [...document.querySelectorAll('#world [data-committed-feedback]')].map(g => ({
      kind: g.dataset.committedFeedback,
      sourceId: g.dataset.sourceId,
      targetId: g.dataset.targetId || null,
    }));
    return { figures, spellEffects, spellCasters, committedFeedback };
  });
}

async function castSpellAndSampleWorld(page, spellChoicePrefix, screenshotName = null) {
  const spellLocator = page.locator('#dock [data-tactical-action="spell"]');
  await spellLocator.waitFor({ state: 'visible', timeout: 3000 });
  await spellLocator.click();
  await page.waitForSelector('#choices [data-spell-guidance]', { timeout: 3000 });
  const guidanceText = await page.$eval('#choices [data-spell-guidance]', el => el.textContent.trim());
  const choiceSelector = `#choices button[data-choice^="${spellChoicePrefix}"]`;
  await page.waitForSelector(choiceSelector, { timeout: 3000 });
  const choiceId = await page.$eval(choiceSelector, el => el.dataset.choice);
  await page.locator(choiceSelector).first().click();

  const sample = await sampleWorldFiguresAndEffects(page);

  if (screenshotName) {
    await page.screenshot({ path: path.join(OUT_DIR, screenshotName) });
  }
  return { choiceId, guidanceText, sample };
}

async function clickWorldTarget(page, selector) {
  await page.waitForSelector(selector, { timeout: 3000 });
  const pt = await page.evaluate((sel) => {
    const el = document.querySelector(sel);
    if (!el) return null;
    const r = el.getBoundingClientRect();
    return { x: r.left + r.width / 2, y: r.top + r.height / 2 };
  }, selector);
  assert(pt, `Expected to find ${selector} in #world`);
  await page.mouse.click(pt.x, pt.y);
}

const srv = await startIsolatedServer();
const browser = await chromium.launch({
  executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe',
  headless: true,
});
const report = {
  verifiedAt: new Date().toISOString(),
  url: srv.url,
  isolatedContext: true,
  existingUserOriginsTouched: false,
  skirmishTwoRoundRepro: {},
  viewports: {},
  spellsVerified: {},
  allowanceStatesVerified: {},
  zeroManaVerified: {},
  reducedMotionVerified: {},
  combatAndSettlementReload: {},
  smokeChecks: {
    deploymentHitProbes: [],
    towerHitProbes: [],
    kingdomWarNav: {},
  },
};

try {
  // =========================================================================
  // PART A: Exact 2-Round Stone Skirmish Reproduction (H-01, D-01, D-02)
  // =========================================================================
  const ctxSkirmish = await browser.newContext({ viewport: { width: 825, height: 375 } });
  const skPage = await ctxSkirmish.newPage();
  await skPage.goto(`${srv.url}/?audit-repro`, { waitUntil: 'networkidle' });
  await importState(skPage, buildStarterCampaign({ id: 'campaign-skirmish-repro-20261023' }));

  // Navigate to War via Kingdom nav bar
  await skPage.click('[data-choice="nav:war"]');
  await skPage.waitForFunction(() => document.getElementById('app')?.dataset?.view === 'war', { timeout: 3000 });
  // Start Skirmish
  await skPage.click('#scene-ui [data-choice="start-skirmish"]');
  await skPage.waitForFunction(() => document.getElementById('app')?.dataset?.view === 'tactical', { timeout: 3000 });

  // Place Clubman at 1,7 and Slinger at 2,7
  await clickWorldTarget(skPage, '#world polygon[data-cell="1,7"][data-kind="deployment"]');
  await skPage.locator('[data-choice^="deployment-stack:"]').nth(1).click();
  await clickWorldTarget(skPage, '#world polygon[data-cell="2,7"][data-kind="deployment"]');

  const startBtnDisabled = await skPage.$eval('[data-choice="start-deployed-battle"]', el => el.disabled);
  assert.equal(startBtnDisabled, false, 'Start Battle should be enabled after placing Clubman and Slinger');
  await skPage.click('[data-choice="start-deployed-battle"]');

  // Round 1: Clubman active, Mana 9 (starter hero knowledge=1 -> 5 + 4 = 9 or 10)
  const round1Before = await measureTacticalViewport(skPage);
  const bearId = await skPage.evaluate(() => {
    const g = [...document.querySelectorAll('#world g[data-stack-id]')].find(el => el.dataset.stackSide === 'e' && el.dataset.stackId.includes('bear'));
    return g?.dataset?.stackId || document.querySelector('#world g[data-stack-side="e"]')?.dataset?.stackId;
  });

  // Cast Magic Arrow on Cave Bear in Round 1
  const round1Arrow = await castSpellAndSampleWorld(skPage, `spellcast:arrow:${bearId}`, 'practice-arrow-immediate.png');
  assert.equal(round1Arrow.guidanceText, 'Choose one listed cast. Your hero casts once per battle round.');
  const bearFig = round1Arrow.sample.figures.find(f => f.stackId === bearId);
  assert(['hit', 'death'].includes(bearFig?.clip), `Expected Cave Bear to show hit/death clip on Magic Arrow, got ${bearFig?.clip}`);
  assert(round1Arrow.sample.spellEffects.some(e => e.spellId === 'arrow' && e.category === 'damage' && e.motif === 'damage-impact'));

  // Move Clubman immediately in Round 1 (keepIntent automatically enters 'move' after round spell is used)
  await skPage.waitForSelector('#world polygon[data-open="1"]', { timeout: 3000 });
  const openMoveCell = await skPage.evaluate(() => {
    const polys = [...document.querySelectorAll('#world polygon[data-open="1"]')];
    const hits = polys.filter(poly => {
      const r = poly.getBoundingClientRect();
      return document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2) === poly;
    }).sort((a, b) => b.getBoundingClientRect().left - a.getBoundingClientRect().left);
    return (hits[0] || polys[0])?.dataset?.cell;
  });
  await clickWorldTarget(skPage, `#world polygon[data-cell="${openMoveCell}"][data-open="1"]`);
  const moveSample = await sampleWorldFiguresAndEffects(skPage);
  await skPage.screenshot({ path: path.join(OUT_DIR, 'practice-committed-move.png') });
  const movedClubmanFigures = moveSample.figures.filter(f => f.side === 'p' && f.clip === 'walk');
  assert.equal(movedClubmanFigures.length, 6, `Expected 6 Clubman figures in walk clip after committed move (cell ${openMoveCell}), got ${movedClubmanFigures.length}`);

  // Now it is Slinger's turn in Round 1: verify D-01 round-used explanation while 5 mana remains
  const slingerTurnMetrics = await measureTacticalViewport(skPage);
  assert.equal(slingerTurnMetrics.spellButton.disabled, true);
  assert.equal(slingerTurnMetrics.spellButton.reason, 'round-used');
  assert.equal(slingerTurnMetrics.statusAllowance.reason, 'round-used');
  assert.match(slingerTurnMetrics.statusAllowance.text, /Round cast used \(1\/round\)/);
  assert.match(slingerTurnMetrics.plaque.text, /Mana [56]/, 'Expected remaining mana (5 or 6) visible on Slinger turn in Round 1');

  // Defend with Slinger to advance to Round 2
  await skPage.click('#dock [data-tactical-action="defend"]');

  // Round 2: Clubman's turn again! Verify casting is available again in Round 2
  const round2Before = await measureTacticalViewport(skPage);
  assert.equal(round2Before.spellButton.disabled, false, 'Spell button should re-enable in Round 2');
  assert.equal(round2Before.spellButton.reason, 'available');

  const clubmanId = await skPage.evaluate(() => {
    const g = [...document.querySelectorAll('#world g[data-stack-id]')].find(el => el.dataset.stackSide === 'p');
    return g?.dataset?.stackId;
  });

  // Cast Bless on Clubman ×12 in Round 2 (spends final 5 mana -> 0 mana)
  const round2Bless = await castSpellAndSampleWorld(skPage, `spellcast:bless:${clubmanId}`, 'practice-bless-immediate.png');
  const clubmanFiguresAfterBless = round2Bless.sample.figures.filter(f => f.stackId === clubmanId);
  assert.equal(clubmanFiguresAfterBless.length, 6, 'Expected 6 Clubman figures after Bless');
  for (const fig of clubmanFiguresAfterBless) {
    assert.equal(fig.clip, 'cast', 'Self-cast Bless on Clubman must preserve caster clip="cast"');
    assert.equal(fig.targetClip, 'buff', 'Self-cast Bless on Clubman must expose targetClip="buff"');
    assert.equal(fig.selfTarget, true, 'Self-cast Bless on Clubman must mark selfTarget=true');
    assert.notEqual(fig.plateMotion, 'hit', 'Friendly Bless must NEVER put Clubman into hit motion');
    assert.notEqual(fig.plateMotion, 'death', 'Friendly Bless must NEVER put Clubman into death motion');
    assert(!/rotate\(14\)|rotate\(70\)/.test(fig.plateTransform || ''), `Friendly Bless must not rotate Clubman by 14 or 70 deg: got ${fig.plateTransform}`);
    assert.match(fig.plateTransform || '', /rotate\((?:0|-[0-9.]+)\)/, 'Self-cast Bless on plate figure should use non-recoil cast tilt (<= 0 deg)');
  }
  assert(round2Bless.sample.spellEffects.some(e => e.spellId === 'bless' && e.category === 'buff' && e.motif === 'buff-crest' && e.selfTarget));

  // Save committed-cast-probe.json in the exact schema used by independent-combined
  const committedCastProbe = round2Bless.sample.figures.map(f => ({
    stackId: f.stackId,
    articulation: f.articulation,
    file: f.file,
    motion: f.plateMotion || f.clip,
    targetClip: f.targetClip,
    spellCategory: f.spellCategory,
    selfTarget: f.selfTarget,
    transform: f.plateTransform,
  }));
  fs.writeFileSync(path.join(OUT_DIR, 'committed-cast-probe.json'), JSON.stringify(committedCastProbe, null, 2), 'utf8');

  // Verify D-02 after Bless spends final 5 mana -> Mana 0 visible and accessible!
  const round2AfterBlessMetrics = await measureTacticalViewport(skPage);
  assert.match(round2AfterBlessMetrics.plaque.text, /XP 0 · Mana 0/, `Expected 'XP 0 · Mana 0' on hero plaque after Bless, got '${round2AfterBlessMetrics.plaque.text}'`);
  assert.match(round2AfterBlessMetrics.plaque.ariaLabel, /battle mana 0\./, `Expected 'battle mana 0.' in plaque aria-label, got '${round2AfterBlessMetrics.plaque.ariaLabel}'`);
  await skPage.screenshot({ path: path.join(OUT_DIR, 'zero-mana-visible-825.png') });

  report.skirmishTwoRoundRepro = {
    round1Before,
    round1Arrow: {
      guidanceText: round1Arrow.guidanceText,
      bearClip: bearFig?.clip,
      spellEffects: round1Arrow.sample.spellEffects,
    },
    movedClubmanWalkCount: movedClubmanFigures.length,
    slingerTurnRound1: slingerTurnMetrics,
    round2Before,
    round2Bless: {
      clubmanFigures: clubmanFiguresAfterBless,
      spellEffects: round2Bless.sample.spellEffects,
    },
    round2AfterBlessZeroMana: round2AfterBlessMetrics,
  };
  await ctxSkirmish.close();

  // =========================================================================
  // PART B: Comprehensive Spell Categories, Allowance States & Reduced Motion at 825x375
  // =========================================================================
  const context825 = await browser.newContext({ viewport: { width: 825, height: 375 } });
  const page = await context825.newPage();
  await page.goto(`${srv.url}/?audit-spells`, { waitUntil: 'networkidle' });

  const baseState = buildSpellTestState({ mana: 30, wisdom: 3 });
  await importState(page, baseState, 'tactical');
  const beforeCastMetrics = await measureTacticalViewport(page);
  assert(beforeCastMetrics.usefulWorldRatio >= 0.8, `Expected usefulWorldRatio >= 0.80 at 825x375, got ${beforeCastMetrics.usefulWorldRatio}`);
  assert.equal(beforeCastMetrics.spellButton.disabled, false);
  assert.equal(beforeCastMetrics.spellButton.reason, 'available');
  assert.match(beforeCastMetrics.plaque.text, /Mana 30/);
  assert.match(beforeCastMetrics.plaque.ariaLabel, /battle mana 30\./);

  const player0Id = baseState.battle.stacks.find(s => s.side === 'p').id;
  const player1Id = baseState.battle.stacks.filter(s => s.side === 'p')[1].id;
  const enemy0Id = baseState.battle.stacks.find(s => s.side === 'e').id;

  // 1a. Offensive AoE spell: fireball + round-used immediately after
  const fireballResult = await castSpellAndSampleWorld(
    page,
    `spellcast:fireball:${enemy0Id}`,
    'tactical-825x375-spell-damage-and-round-used.png'
  );
  assert.equal(fireballResult.guidanceText, 'Choose one listed cast. Your hero casts once per battle round.');
  const fbCaster = fireballResult.sample.figures.find(f => f.stackId === player0Id);
  const fbTarget = fireballResult.sample.figures.find(f => f.stackId === enemy0Id);
  assert.equal(fbCaster?.clip, 'cast');
  assert(['hit', 'death'].includes(fbTarget?.clip), `Expected fireball target clip hit/death, got ${fbTarget?.clip}`);
  assert(fireballResult.sample.spellEffects.length >= 2, 'Expected fireball AoE spell effects on primary + adjacent splash target');
  report.spellsVerified.fireball = fireballResult;

  const afterCastMetrics = await measureTacticalViewport(page);
  assert.equal(afterCastMetrics.spellButton.disabled, true);
  assert.equal(afterCastMetrics.spellButton.reason, 'round-used');
  assert.equal(afterCastMetrics.statusAllowance.reason, 'round-used');
  assert.match(afterCastMetrics.statusAllowance.text, /Round cast used \(1\/round\)/);
  report.allowanceStatesVerified.roundUsed = afterCastMetrics;

  // 1b. Offensive single-target spells: arrow and bolt
  for (const spellId of ['arrow', 'bolt']) {
    await importState(page, buildSpellTestState({ mana: 30, wisdom: 3 }), 'tactical');
    const res = await castSpellAndSampleWorld(page, `spellcast:${spellId}:${enemy0Id}`);
    const targetFig = res.sample.figures.find(f => f.stackId === enemy0Id);
    assert(['hit', 'death'].includes(targetFig?.clip), `Expected ${spellId} target clip hit/death, got ${targetFig?.clip}`);
    assert(res.sample.spellEffects.some(e => e.spellId === spellId && e.category === 'damage'));
    report.spellsVerified[spellId] = res;
  }

  // 1c. Beneficial buff spells: self-cast bless (casterId === targetId), allied bless (casterId !== targetId), and allied haste
  await importState(page, buildSpellTestState({ mana: 30, wisdom: 3 }), 'tactical');
  const selfBlessResult = await castSpellAndSampleWorld(
    page,
    `spellcast:bless:${player0Id}`,
    'tactical-825x375-spell-buff-self.png'
  );
  const selfFig = selfBlessResult.sample.figures.find(f => f.stackId === player0Id);
  assert.equal(selfFig?.clip, 'cast');
  assert.equal(selfFig?.targetClip, 'buff');
  assert.equal(selfFig?.selfTarget, true);
  assert.notEqual(selfFig?.plateMotion, 'hit');
  assert.notEqual(selfFig?.plateMotion, 'death');
  assert(!/rotate\(14\)|rotate\(70\)/.test(selfFig?.plateTransform || ''), 'Self-cast bless must not rotate plate into hit/death recoil');
  assert(selfBlessResult.sample.spellEffects.some(e => e.spellId === 'bless' && e.category === 'buff' && e.selfTarget));
  report.spellsVerified.blessSelf = selfBlessResult;

  await importState(page, buildSpellTestState({ mana: 30, wisdom: 3 }), 'tactical');
  const allyBlessResult = await castSpellAndSampleWorld(page, `spellcast:bless:${player1Id}`);
  const allyBlessTarget = allyBlessResult.sample.figures.find(f => f.stackId === player1Id);
  assert.equal(allyBlessTarget?.clip, 'buff');
  assert.equal(allyBlessTarget?.plateMotion, 'buff');
  assert(!/rotate\(14\)|rotate\(70\)/.test(allyBlessTarget?.plateTransform || ''));
  report.spellsVerified.blessAlly = allyBlessResult;

  await importState(page, buildSpellTestState({ mana: 30, wisdom: 3 }), 'tactical');
  const hasteResult = await castSpellAndSampleWorld(page, `spellcast:haste:${player1Id}`);
  const hasteTarget = hasteResult.sample.figures.find(f => f.stackId === player1Id);
  assert.equal(hasteTarget?.clip, 'buff');
  assert.equal(hasteTarget?.plateMotion, 'buff');
  assert(!/rotate\(14\)|rotate\(70\)/.test(hasteTarget?.plateTransform || ''));
  report.spellsVerified.haste = hasteResult;

  // 1d. Healing and Resurrection spells: cure (self and ally) and resurrect
  await importState(page, buildSpellTestState({ mana: 30, wisdom: 3 }), 'tactical');
  const cureSelfResult = await castSpellAndSampleWorld(page, `spellcast:cure:${player0Id}`);
  const cureSelfTarget = cureSelfResult.sample.figures.find(f => f.stackId === player0Id);
  assert.equal(cureSelfTarget?.clip, 'cast');
  assert.equal(cureSelfTarget?.targetClip, 'heal');
  assert.equal(cureSelfTarget?.selfTarget, true);
  assert(!/rotate\(14\)|rotate\(70\)/.test(cureSelfTarget?.plateTransform || ''));
  report.spellsVerified.cureSelf = cureSelfResult;

  await importState(page, buildSpellTestState({ mana: 30, wisdom: 3 }), 'tactical');
  const cureResult = await castSpellAndSampleWorld(page, `spellcast:cure:${player1Id}`);
  const cureTarget = cureResult.sample.figures.find(f => f.stackId === player1Id);
  assert.equal(cureTarget?.clip, 'heal');
  assert.equal(cureTarget?.plateMotion, 'heal');
  assert(!/rotate\(14\)|rotate\(70\)/.test(cureTarget?.plateTransform || ''));
  report.spellsVerified.cureAlly = cureResult;

  await importState(page, buildSpellTestState({ mana: 30, wisdom: 3 }), 'tactical');
  const resurrectResult = await castSpellAndSampleWorld(
    page,
    `spellcast:resurrect:${player1Id}`,
    'tactical-825x375-spell-heal-resurrect.png'
  );
  const resTarget = resurrectResult.sample.figures.find(f => f.stackId === player1Id);
  assert.equal(resTarget?.clip, 'heal');
  assert.equal(resTarget?.plateMotion, 'heal');
  assert(!/rotate\(14\)|rotate\(70\)/.test(resTarget?.plateTransform || ''));
  assert(resurrectResult.sample.spellEffects.some(e => e.spellId === 'resurrect' && e.category === 'heal' && e.motif === 'resurrect-crown'));
  report.spellsVerified.resurrect = resurrectResult;

  // 1e. Debuff spell: slow
  await importState(page, buildSpellTestState({ mana: 30, wisdom: 3 }), 'tactical');
  const slowResult = await castSpellAndSampleWorld(
    page,
    `spellcast:slow:${enemy0Id}`,
    'tactical-825x375-spell-debuff-slow.png'
  );
  const slowTarget = slowResult.sample.figures.find(f => f.stackId === enemy0Id);
  assert.equal(slowTarget?.clip, 'debuff');
  assert.equal(slowTarget?.plateMotion, 'debuff');
  assert(!/rotate\(14\)|rotate\(70\)/.test(slowTarget?.plateTransform || ''));
  assert(slowResult.sample.spellEffects.some(e => e.spellId === 'slow' && e.category === 'debuff' && e.motif === 'slow-shackle'));
  report.spellsVerified.slow = slowResult;

  // 1f. D-02 Zero mana visibility + D-01 insufficient-mana guidance at 825x375
  await importState(page, buildSpellTestState({ mana: 0, wisdom: 3, castThisRound: false }), 'tactical');
  const zeroManaClosedMetrics = await measureTacticalViewport(page);
  assert.match(zeroManaClosedMetrics.plaque.text, /XP 120 · Mana 0/);
  assert.match(zeroManaClosedMetrics.plaque.ariaLabel, /battle mana 0\./);
  assert.equal(zeroManaClosedMetrics.plaque.height, beforeCastMetrics.plaque.height, 'Zero-mana text must not increase .tactical-hero-plaque height');
  assert.equal(zeroManaClosedMetrics.spellButton.disabled, true);
  assert.equal(zeroManaClosedMetrics.spellButton.reason, 'insufficient-mana');
  assert.equal(zeroManaClosedMetrics.statusAllowance.reason, 'insufficient-mana');
  assert.match(zeroManaClosedMetrics.statusAllowance.text, /Insufficient mana \(0\/5\)/);
  await page.screenshot({ path: path.join(OUT_DIR, 'tactical-825x375-zero-mana-and-guidance.png') });
  report.zeroManaVerified['825x375'] = zeroManaClosedMetrics;
  report.allowanceStatesVerified.insufficientMana = zeroManaClosedMetrics;

  // 1f-bis. D-01 no-known-spell guidance (wisdom = -1 so no spell lv <= 1 + wisdom)
  await importState(page, buildSpellTestState({ mana: 15, wisdom: -1, castThisRound: false }), 'tactical');
  const noSpellMetrics = await measureTacticalViewport(page);
  assert.equal(noSpellMetrics.spellButton.disabled, true);
  assert.equal(noSpellMetrics.spellButton.reason, 'no-known-spell');
  assert.equal(noSpellMetrics.statusAllowance.reason, 'no-known-spell');
  assert.match(noSpellMetrics.statusAllowance.text, /No known spell/);
  report.allowanceStatesVerified.noKnownSpell = noSpellMetrics;

  // 1f-ter. D-01 no-target guidance (affordable hostile spellbook with no living enemy target)
  const noTargetMetrics = await page.evaluate(async () => {
    const mod = await import('/src/client/tactical-ui.js');
    const state = mod.battleSpellAvailability(
      { castThisRound: false, mana: 12, wisdom: 1, stacks: [{ id: 'p1', side: 'p', dead: false, count: 4 }, { id: 'e1', side: 'e', dead: true, count: 0 }] },
      { arrow: { mana: 5, lv: 1, type: 'dmg' }, bolt: { mana: 10, lv: 2, type: 'dmg' } }
    );
    const rows = mod.modeRows({ moves: [], melee: [], ranged: [], spells: state.offers.length, waited: false, castThisRound: false, mana: state.mana, minSpellMana: state.minSpellMana, knownSpells: state.knownSpells });
    return {
      state,
      spellRow: rows.find(r => r.id === 'spell'),
      sentence: mod.intentSentence('spell', 'Warrior', state),
    };
  });
  assert.equal(noTargetMetrics.state.enabled, false);
  assert.equal(noTargetMetrics.state.reason, 'no-target');
  assert.equal(noTargetMetrics.spellRow?.reason, 'no-target');
  assert.match(noTargetMetrics.sentence, /no legal target/i);
  report.allowanceStatesVerified.noTarget = noTargetMetrics;

  // 1g. Reduced motion spell cast
  await importState(page, buildSpellTestState({ mana: 30, wisdom: 3, reducedMotion: true }), 'tactical');
  const rmResult = await castSpellAndSampleWorld(
    page,
    `spellcast:cure:${player0Id}`,
    'tactical-825x375-reduced-motion-spell.png'
  );
  const rmFig = rmResult.sample.figures.find(f => f.stackId === player0Id);
  assert.equal(rmFig?.clip, 'idle', 'Under reducedMotion, animated figure clip stays idle');
  assert(rmResult.sample.spellEffects.some(e => e.spellId === 'cure' && e.reducedMotion === true), 'Reduced motion still renders static spell effect feedback on #world');
  assert(rmResult.sample.committedFeedback.some(c => c.kind === 'spell' && c.sourceId === player0Id), 'Reduced motion renders static committed feedback marker on #world');
  report.reducedMotionVerified = rmResult;

  // 1h. Melee attack, lethal result timing, single settlement, and reload without replayed effects or duplicate rewards
  const duelState = buildSpellTestState({ mana: 20, wisdom: 3 });
  const pStack = duelState.battle.stacks.find(s => s.side === 'p' && !s.dead);
  for (const eStack of duelState.battle.stacks.filter(s => s.side === 'e')) {
    eStack.dead = true;
    eStack.count = 0;
    eStack.top = 0;
  }
  const lastEnemy = duelState.battle.stacks.find(s => s.side === 'e');
  lastEnemy.dead = false;
  lastEnemy.count = 1;
  lastEnemy.top = 1;
  lastEnemy.x = pStack.x + 1;
  lastEnemy.y = pStack.y;
  duelState.battle.queue = [pStack.id, lastEnemy.id];
  const goldBeforeDuel = duelState.resources.gold;
  const xpBeforeDuel = duelState.hero.xp;

  await importState(page, duelState, 'tactical');
  await page.click('#dock [data-tactical-action="attack"]');
  await clickWorldTarget(page, `#world rect[data-target="${lastEnemy.id}"]`);

  // Battle is now RESOLVED with pendingSettlement = true
  await page.waitForSelector('#scene-ui [data-choice="result:tactical"]', { timeout: 3000 });
  const goldBeforeSettle = await page.evaluate(() => document.querySelector('[data-resource="gold"]')?.textContent?.trim());
  await page.click('#scene-ui [data-choice="result:tactical"]');
  await page.waitForFunction(() => document.getElementById('app')?.dataset?.combat === '0', { timeout: 3000 });
  const postSettleState = await page.evaluate(() => ({
    view: document.getElementById('app')?.dataset?.view,
    combat: document.getElementById('app')?.dataset?.combat,
    goldText: document.querySelector('[data-resource="gold"]')?.textContent?.trim(),
  }));

  await page.reload({ waitUntil: 'networkidle' });
  const postReloadState = await page.evaluate(() => ({
    view: document.getElementById('app')?.dataset?.view,
    combat: document.getElementById('app')?.dataset?.combat,
    goldText: document.querySelector('[data-resource="gold"]')?.textContent?.trim(),
    spellEffectsOnReload: document.querySelectorAll('#world [data-spell-effect]').length,
  }));
  assert.equal(postReloadState.combat, '0', 'Reload after settling battle must not reopen resolved battle');
  assert.equal(postReloadState.goldText, postSettleState.goldText, 'Reload must not duplicate settled battle rewards');
  assert.equal(postReloadState.spellEffectsOnReload, 0, 'Reload must not replay transient spell effects');
  report.combatAndSettlementReload = {
    goldBeforeDuel,
    xpBeforeDuel,
    goldBeforeSettle,
    postSettleState,
    postReloadState,
  };

  report.viewports['825x375'] = {
    beforeCast: beforeCastMetrics,
    afterCastRoundUsed: afterCastMetrics,
    zeroMana: zeroManaClosedMetrics,
  };
  await context825.close();

  // =========================================================================
  // PART C: Multi-Viewport Verification (825x375, 933x424, 1280x720)
  //         - Spell + Zero Mana at 933x424 & 1280x720
  //         - Tactical Deployment 11/11 cell center hits + Cancel/Start
  //         - Kingdom War navigation clearance
  //         - Defense pause/resume + ~64x64px tower inspection center hits
  // =========================================================================
  for (const [vw, vh] of [[825, 375], [933, 424], [1280, 720]]) {
    const ctx = await browser.newContext({ viewport: { width: vw, height: vh } });
    const vpPage = await ctx.newPage();
    await vpPage.goto(`${srv.url}/?audit-vp-${vw}x${vh}`, { waitUntil: 'networkidle' });

    if (vw !== 825) {
      await importState(vpPage, buildSpellTestState({ mana: 5, wisdom: 3 }), 'tactical');
      const castRes = await castSpellAndSampleWorld(
        vpPage,
        `spellcast:arrow:${enemy0Id}`,
        `tactical-${vw}x${vh}-spell-and-zero-mana.png`
      );
      const metricsAfter = await measureTacticalViewport(vpPage);
      assert.match(metricsAfter.plaque.text, /Mana 0/, `Expected Mana 0 after spending last 5 mana at ${vw}x${vh}`);
      assert.match(metricsAfter.plaque.ariaLabel, /battle mana 0\./);
      assert.equal(metricsAfter.spellButton.reason, 'round-used');
      report.viewports[`${vw}x${vh}`] = {
        metricsAfterFiveManaCastToZero: metricsAfter,
        spellEffectsCount: castRes.sample.spellEffects.length,
      };
    }

    // Smoke check 1: Kingdom -> War navigation clearance & Skirmish Deployment 11/11 legal cells
    await importState(vpPage, buildStarterCampaign({ id: `campaign-smoke-${vw}x${vh}` }));
    const warNavProbe = await vpPage.evaluate(() => {
      const btn = document.querySelector('[data-choice="nav:war"]');
      if (!btn) return null;
      const r = btn.getBoundingClientRect();
      const cx = r.left + r.width / 2;
      const cy = r.top + r.height / 2;
      const topEl = document.elementFromPoint(cx, cy);
      return {
        width: Math.round(r.width),
        height: Math.round(r.height),
        selfHit: Boolean(topEl && (topEl === btn || btn.contains(topEl))),
      };
    });
    assert(warNavProbe?.selfHit, `Expected War nav button to self-hit at ${vw}x${vh}`);
    report.smokeChecks.kingdomWarNav[`${vw}x${vh}`] = warNavProbe;

    await vpPage.click('[data-choice="nav:war"]');
    await vpPage.waitForFunction(() => document.getElementById('app')?.dataset?.view === 'war', { timeout: 3000 });
    await vpPage.click('#scene-ui [data-choice="start-skirmish"]');
    await vpPage.waitForFunction(() => document.getElementById('app')?.dataset?.view === 'tactical', { timeout: 3000 });

    const cellsProbe = await vpPage.evaluate(() => {
      const polys = [...document.querySelectorAll('#world polygon[data-kind="deployment"]')];
      return polys.map(poly => {
        const r = poly.getBoundingClientRect();
        const cx = r.left + r.width / 2;
        const cy = r.top + r.height / 2;
        const hitEl = document.elementFromPoint(cx, cy);
        return {
          cell: poly.dataset.cell,
          hit: hitEl?.dataset?.cell || null,
        };
      });
    });
    assert.equal(cellsProbe.length, 11, `Expected 11 legal deployment cells at ${vw}x${vh}, got ${cellsProbe.length}`);
    for (const c of cellsProbe) {
      assert.equal(c.hit, c.cell, `Deployment cell ${c.cell} center hit ${c.hit} at ${vw}x${vh}`);
    }
    report.smokeChecks.deploymentHitProbes.push({ size: { width: vw, height: vh }, cells: cellsProbe });

    // Verify Cancel setup returns to War
    await vpPage.click('[data-choice="cancel-battle-setup"]');
    await vpPage.waitForFunction(() => document.getElementById('app')?.dataset?.view === 'war', { timeout: 3000 });

    // Smoke check 2: Defense starts paused, pause/resume works, and ~64x64px tower inspection targets self-hit
    await vpPage.click('#scene-ui [data-choice="start-siege"]');
    await vpPage.waitForFunction(() => document.getElementById('app')?.dataset?.view === 'defense', { timeout: 3000 });
    await vpPage.waitForSelector('#choices [data-choice="start-siege"]', { timeout: 3000 });
    await vpPage.click('#choices [data-choice="start-siege"]');
    await vpPage.waitForSelector('#world [data-inspect-tower]', { timeout: 3000 });
    const selectedPaused = await vpPage.$eval('#selected', el => el.textContent.trim());
    assert.match(selectedPaused, /^Paused · siege · Wave 1 of 5 · core 400/);

    const towerProbe = await vpPage.evaluate(() => {
      const circles = [...document.querySelectorAll('#world [data-inspect-tower]')];
      return circles.map(c => {
        const r = c.getBoundingClientRect();
        const cx = r.left + r.width / 2;
        const cy = r.top + r.height / 2;
        const hitEl = document.elementFromPoint(cx, cy);
        return {
          name: c.getAttribute('aria-label'),
          hit: hitEl?.getAttribute('aria-label') || null,
          width: r.width,
          height: r.height,
        };
      });
    });
    assert.equal(towerProbe.length, 2, `Expected 2 starter tower inspect targets at ${vw}x${vh}`);
    for (const t of towerProbe) {
      assert.equal(t.hit, t.name, `Expected tower target ${t.name} to self-hit at ${vw}x${vh}, got ${t.hit}`);
      assert(t.width >= 60 && t.width <= 68, `Expected ~64px tower target width at ${vw}x${vh}, got ${t.width}`);
      assert(t.height >= 60 && t.height <= 68, `Expected ~64px tower target height at ${vw}x${vh}, got ${t.height}`);
    }
    report.smokeChecks.towerHitProbes.push({ size: { width: vw, height: vh }, targets: towerProbe });

    // Resume and Pause again
    await vpPage.click('#dock [data-choice="defense-pause"], [data-choice="defense-pause"]');
    const selectedRunning = await vpPage.$eval('#selected', el => el.textContent.trim());
    assert.match(selectedRunning, /^Running · siege · Wave 1 of 5/);
    await vpPage.click('#dock [data-choice="defense-pause"], [data-choice="defense-pause"]');
    const selectedPausedAgain = await vpPage.$eval('#selected', el => el.textContent.trim());
    assert.match(selectedPausedAgain, /^Paused · siege · Wave 1 of 5/);

    await ctx.close();
  }

  fs.writeFileSync(path.join(OUT_DIR, 'deployment-hit-probes.json'), JSON.stringify(report.smokeChecks.deploymentHitProbes, null, 2), 'utf8');
  fs.writeFileSync(path.join(OUT_DIR, 'tower-hit-probes.json'), JSON.stringify(report.smokeChecks.towerHitProbes, null, 2), 'utf8');
  fs.writeFileSync(path.join(OUT_DIR, 'verification-summary.json'), JSON.stringify(report, null, 2), 'utf8');
  console.log('LIVE_VERIFICATION_PASS', JSON.stringify({
    viewports: Object.keys(report.viewports),
    spellsVerified: Object.keys(report.spellsVerified),
    usefulWorld825: report.viewports['825x375'].beforeCast.usefulWorldRatio,
    plaqueHeightWithMana: report.viewports['825x375'].beforeCast.plaque.height,
    plaqueHeightZeroMana: report.viewports['825x375'].zeroMana.plaque.height,
    deploymentProbes: report.smokeChecks.deploymentHitProbes.length,
    towerProbes: report.smokeChecks.towerHitProbes.length,
  }));
} finally {
  await browser.close();
  await srv.close();
}
