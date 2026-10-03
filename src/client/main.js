import data from '../data/reference-data.json' with { type: 'json' };
import contract from '../data/implementation-contract.json' with { type: 'json' };
import selection from '../data/reviewed-source-selection.json' with { type: 'json' };
import scene from '../data/stone-scene.json' with { type: 'json' };
import { newCampaign, command, advanceReported, formatResume, cost, heroStats, manaMax, dailyMoves, gateHp } from '../core/campaign.js';
import { activeStackId, legalTargets, meleeCommand } from '../core/battle.js';
import { save, load, SAVE_KEY, rememberView, rememberedView, encode } from '../core/save.js';
import { camera, inverse, project } from './projection.js';
import { pose } from './rig.js';
import { applySettings, arm, blip } from './audio.js';
import { RIVALS } from '../core/rules.js';

const $ = id => document.getElementById(id);
const svgNS = 'http://www.w3.org/2000/svg';
const ages = ['stone', 'bronze', 'iron', 'medieval', 'gunpowder', 'industrial', 'modern', 'future'];
const screens = ['home', 'kingdom', 'adventure', 'hero', 'army', 'forge', 'market', 'tactical', 'defense', 'story', 'war', 'settings'];
const blocked = {
  tactical: 'Stacks are markers until reviewed unit paintings replace them. The battle rules are live.',
  defense: 'Defense uses a fixed 1/60 step. Pause and background do not fire. There is no kill income.',
  war: 'Skirmish and Challenge do not pay campaign gold. Siege and Duel settle campaign rewards once.',
  skills: 'Skill offers and experience use the documented thresholds. Positive morale does not grant an extra turn while that choice is open.',
  loot: 'Loot and dwelling offers persist with the saved random state.'
};
const initial = load(localStorage, data);
let state = initial.state, selected = 'P01', suspended = false, timer, resumeNote = '', clip = 'idle';
let view = initial.status === 'VALID' ? rememberedView(localStorage, screens) : 'kingdom';
const tutorialCue = ['Build a Lumber Camp.', 'Build a Farm.', 'Build a Quarry.', 'Build a Barracks.', 'Recruit a stack.', 'Leave town.', 'A guard opens a positioned battle. Defense waves are still not a simulation.'];
const say = text => { $('message').textContent = text; };
if (initial.status === 'EMPTY') state = newCampaign(contract, data, Date.now());
if (initial.status === 'DAMAGED') {
  view = 'home';
  say(initial.error + ' The damaged save is still stored.');
}

function persist() {
  try { save(localStorage, state, data); rememberView(localStorage, view, screens); $('status').textContent = 'Saved locally'; }
  catch (error) { $('status').textContent = 'Save failed'; say(error.message); }
}
function catchUp(now, announce) {
  if (!state) return;
  const step = advanceReported(state, now, data);
  state = step.state;
  if (announce) {
    const text = formatResume(step.report);
    if (text) resumeNote = text;
  }
}
function cue() {
  if (!state || state.tutorial.skipped || state.tutorial.step > 6) return '';
  return ' Next: ' + tutorialCue[state.tutorial.step];
}
function act(type, payload) {
  try {
    state = command(state, { id: crypto.randomUUID(), type, payload }, Date.now(), data);
    applySettings(state.settings);
    persist();
    blip();
    render();
  } catch (error) { say(error.message); }
}
function element(name, attrs) {
  const node = document.createElementNS(svgNS, name);
  for (const [k, v] of Object.entries(attrs)) node.setAttribute(k, v);
  return node;
}
function button(label, onClick, disabled = false) {
  const node = document.createElement('button');
  node.type = 'button';
  node.textContent = label;
  node.disabled = disabled;
  node.onclick = onClick;
  return node;
}
function resources() {
  $('resources').replaceChildren();
  const show = view === 'kingdom' || view === 'adventure';
  $('resources').hidden = !show;
  if (!show || !state) return;
  for (const k of ['food', 'wood', 'stone', 'gold']) {
    const span = document.createElement('span');
    const chosen = selection.delivery?.['resource-' + k];
    const iconFile = chosen?.uiFile || chosen?.file;
    if (iconFile) {
      const icon = document.createElement('img');
      icon.src = iconFile;
      icon.alt = '';
      const long = chosen.uiLongSide || 18;
      const aspect = (chosen.uiWidth || 1) / (chosen.uiHeight || 1);
      if (aspect >= 1) { icon.style.width = long + 'px'; icon.style.height = (long / aspect) + 'px'; }
      else { icon.style.height = long + 'px'; icon.style.width = (long * aspect) + 'px'; }
      span.append(icon, ' ' + k + ' ' + Math.floor(state.resources[k]));
    } else span.textContent = k + ' ' + Math.floor(state.resources[k]);
    $('resources').append(span);
  }
}
function clearWorld() { $('world').replaceChildren(); $('terrain').hidden = true; }

function kingdom() {
  const chosen = selection.kingdomTerrain[ages[state.age]];
  const file = chosen.displayFile || chosen.sourceFile;
  $('terrain').hidden = false;
  if ($('terrain').getAttribute('src') !== file) $('terrain').src = file;
  $('terrain').alt = ages[state.age] + ' kingdom terrain, not yet accepted';
  const world = $('world');
  const geo = contract.geometry.kingdom, matrix = geo.worldToSource;
  const hallPlot = state.plots.find(p => p.id === 'townhall');
  if (ages[state.age] === 'stone' && hallPlot && hallPlot.level >= 1 && scene.hall) {
    const placed = scene.hall.matrix;
    world.append(element('image', {
      href: scene.hall.file,
      x: 0,
      y: 0,
      width: scene.hall.width,
      height: scene.hall.height,
      transform: `matrix(${placed[0][0]} ${placed[1][0]} ${placed[0][1]} ${placed[1][1]} ${placed[0][2]} ${placed[1][2]})`,
      'aria-label': 'Stone Hall placed on the shared camera. Registration is not accepted.',
    }));
  }
  for (const road of geo.roads) world.append(element('polyline', { points: road.map(p => project(matrix, p).join(',')).join(' '), fill: 'none', stroke: '#9c8870', 'stroke-width': 10 }));
  for (const site of geo.sites) {
    const plot = state.plots.find(p => p.id === site.id), [x, y, w, h] = site.rect, centre = project(matrix, [x + w / 2, y + h / 2]);
    const job = state.buildJobs.find(j => j.plotId === plot.id);
    const group = element('g', { class: 'plot' + (plot.id === selected ? ' selected' : ''), tabindex: 0, role: 'button', 'aria-label': `${plot.id}: ${plot.type ?? 'empty plot'} level ${plot.level}` });
    group.append(element('polygon', { class: job ? 'scaffold' : plot.level ? 'building' : 'empty', points: [[x, y], [x + w, y], [x + w, y + h], [x, y + h]].map(v => project(matrix, v).join(',')).join(' ') }));
    const text = element('text', { x: centre[0], y: centre[1] + 5 });
    text.textContent = job ? '…' : plot.type ? plot.level : '+';
    group.append(text);
    const box = world.getBoundingClientRect(), scale = camera([1376, 768], box.width, box.height).scale || 1, diameter = 48 / scale;
    group.append(element('rect', { x: centre[0] - diameter / 2, y: centre[1] - diameter / 2, width: diameter, height: diameter, fill: 'transparent' }));
    group.onclick = () => { selected = plot.id; render(); };
    group.onkeydown = event => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); selected = plot.id; render(); } };
    world.append(group);
  }
  const plot = state.plots.find(p => p.id === selected);
  $('selected').textContent = plot.type ? `${data.BUILDINGS[plot.type].n} · level ${plot.level}` : selected + ' · empty plot';
  const types = plot.type ? [plot.type] : Object.keys(data.BUILDINGS).filter(k => !['townhall', 'walls'].includes(k));
  for (const type of types) {
    const payment = cost(data, type, plot.level);
    const label = (plot.type ? 'Upgrade ' : 'Build ') + data.BUILDINGS[type].n + ' — ' + Object.entries(payment).map(([k, v]) => v + ' ' + k).join(', ');
    $('choices').append(button(label, () => act('BUILD', { plotId: plot.id, building: type }), state.buildJobs.some(j => j.plotId === plot.id)));
  }
  $('choices').append(button('Upgrade Town Hall', () => act('BUILD', { plotId: 'townhall', building: 'townhall' })));
  $('choices').append(button('Build Walls', () => act('BUILD', { plotId: 'walls', building: 'walls' })));
  $('choices').append(button('Advance age', () => act('AGE_UP', {})));
  $('choices').append(button('End day', () => act('END_DAY', {})));
  say(`Walls are level ${state.walls.level}. Day ${state.day}, weather ${state.weather}. The Stone Hall stays on the shared camera and is not accepted. A contact-scale framing proposal is recorded and the contract is unchanged. ${cue()}`);
}

function sourceFromPointer(event) {
  const rect = $('world').getBoundingClientRect();
  const fit = camera([1376, 768], rect.width, rect.height);
  return [(event.clientX - rect.left - fit.offset[0]) / fit.scale, (event.clientY - rect.top - fit.offset[1]) / fit.scale];
}

function cellPoints(matrix, x, y, w = 1, h = 1) {
  return [[x, y], [x + w, y], [x + w, y + h], [x, y + h]].map(v => project(matrix, v).join(',')).join(' ');
}

function adventure() {
  const world = $('world');
  const geo = contract.geometry.adventure, matrix = geo.worldToSource;
  world.append(element('rect', { width: 1376, height: 768, fill: '#24342c' }));
  for (const [x, y] of geo.blocked ?? []) world.append(element('polygon', { class: 'water', points: cellPoints(matrix, x, y) }));
  for (const site of geo.sites) {
    const [x, y, w, h] = site.rect;
    world.append(element('polygon', { class: 'site', points: cellPoints(matrix, x, y, w, h) }));
  }
  for (const road of geo.roads) world.append(element('polyline', { points: road.map(p => project(matrix, [p[0] + .5, p[1] + .5]).join(',')).join(' '), fill: 'none', stroke: '#9c8870', 'stroke-width': 8 }));
  if (state.adventure) {
    const seen = new Set(state.adventure.visited);
    for (let y = 0; y < geo.rows; y++) for (let x = 0; x < geo.cols; x++) {
      if (!seen.has(`${x},${y}`)) world.append(element('polygon', { class: 'fog', points: cellPoints(matrix, x, y) }));
    }
  }
  for (const [name, cell] of Object.entries(geo.anchors)) {
    const centre = project(matrix, [cell[0], cell[1]]);
    const kind = name.startsWith('guard') ? 'guard' : name === 'hero' ? 'anchor' : 'pickup';
    world.append(element('circle', { class: kind, cx: centre[0], cy: centre[1], r: name.startsWith('guard') ? 10 : 7 }));
  }
  if (state.adventure && !state.adventure.atTown) {
    const here = project(matrix, [state.adventure.x + .5, state.adventure.y + .5]);
    const sample = pose(clip, performance.now() / 1000, { reduced: state.settings.reducedMotion });
    const scale = 0.35;
    const line = (a, b) => world.append(element('line', { x1: here[0] + a[0] * scale, y1: here[1] + (a[1] - 120) * scale, x2: here[0] + b[0] * scale, y2: here[1] + (b[1] - 120) * scale, stroke: '#f1e9d9', 'stroke-width': 3 }));
    line(sample.hip, sample.chest); line(sample.chest, sample.head); line(sample.chest, sample.hand);
    line(sample.hip, sample.kneeL); line(sample.kneeL, sample.hoofL); line(sample.hip, sample.kneeR); line(sample.kneeR, sample.hoofR);
    $('selected').textContent = `Travel ${state.adventure.x},${state.adventure.y} · moves ${state.adventure.moves}`;
    $('choices').append(button('Step north', () => act('MOVE', { path: [[state.adventure.x, state.adventure.y - 1]] })));
    $('choices').append(button('Step south', () => act('MOVE', { path: [[state.adventure.x, state.adventure.y + 1]] })));
    $('choices').append(button('Step west', () => act('MOVE', { path: [[state.adventure.x - 1, state.adventure.y]] })));
    $('choices').append(button('Step east', () => act('MOVE', { path: [[state.adventure.x + 1, state.adventure.y]] })));
    $('choices').append(button('Rest', () => act('REST', {})));
    $('choices').append(button('Return at the town approach', () => { act('RETURN_TOWN', {}); view = 'kingdom'; render(); }));
    if (state.adventure.pendingEncounter && !state.battle) $('choices').append(button('Fight the guard', () => { act('BEGIN_ENCOUNTER', {}); if (state.battle) { view = 'tactical'; render(); } }));
    say((state.adventure.pendingEncounter ? 'An unresolved guard is waiting. Movement stays spent until that guard is cleared.' : 'Road steps cost 1. Water and site footprints are blocked.') + cue());
  } else {
    $('selected').textContent = 'Adventure';
    $('choices').append(button('Leave town', () => { clip = 'walk'; act('ENTER_ADVENTURE', {}); }));
    const remaining = state.adventure ? state.adventure.moves : dailyMoves(state, data);
    say(`Saved movement is ${remaining}. Leaving town again does not refill it. ${cue()}`);
  }
}

function hero() {
  clearWorld();
  const stats = heroStats(state, data);
  $('selected').textContent = data.CLASSES[state.hero.class].n;
  for (const id of Object.keys(data.CLASSES)) $('choices').append(button(data.CLASSES[id].n, () => act('SET_CLASS', { class: id })));
  const offense = selection.delivery?.['skill-offense'];
  if (offense?.uiFile) {
    const icon = document.createElement('img');
    icon.src = offense.uiFile;
    icon.alt = 'Offense';
    const long = 36;
    const aspect = (offense.uiWidth || 1) / (offense.uiHeight || 1);
    if (aspect >= 1) { icon.style.width = long + 'px'; icon.style.height = (long / aspect) + 'px'; }
    else { icon.style.height = long + 'px'; icon.style.width = (long * aspect) + 'px'; }
    $('choices').prepend(icon);
  }
  say(`Attack ${stats.atk}, Defense ${stats.def}, Power ${stats.pow}, Knowledge ${stats.kno}. Mana ${state.hero.mana}/${manaMax(state, data)}. Daily moves ${dailyMoves(state, data)}. Points ${state.hero.points}. ${blocked.skills}`);
}

function army() {
  clearWorld();
  $('selected').textContent = 'Army';
  for (const stack of state.army) $('choices').append(button(`${data.ROLES[stack.type].names[stack.age]} ×${stack.count}`, () => say(data.ROLES[stack.type].d || 'Current-age stack'), false));
  for (const role of Object.keys(data.ROLES)) $('choices').append(button('Recruit 5 ' + data.ROLES[role].n, () => act('RECRUIT', { role })));
  say('Recruitment needs a completed Barracks and pays five at the current age. Capacity is 2 plus Barracks level.');
}

function forge() {
  clearWorld();
  $('selected').textContent = 'Forge';
  for (const slot of contract.slots) {
    const item = state.hero.equip[slot];
    $('choices').append(button((item ? 'Unequip ' : 'Forge ') + slot, () => item ? act('UNEQUIP', { slot }) : act('FORGE', { slot })));
  }
  for (const item of state.inventory) $('choices').append(button('Equip ' + item.slot, () => act('EQUIP', { itemId: item.id })));
  say('Forging needs a completed Armory. Quality follows its level. There is no Enhance, Reforge or Socket action.');
}

function market() {
  clearWorld();
  $('selected').textContent = 'Market';
  for (const resource of ['food', 'wood', 'stone']) {
    $('choices').append(button('Buy 100 ' + resource + ' for 120 gold', () => act('MARKET', { side: 'buy', resource })));
    $('choices').append(button('Sell 100 ' + resource + ' for 60 gold', () => act('MARKET', { side: 'sell', resource })));
  }
  say(state.age < 1 ? 'The market opens in the Bronze Age.' : 'Batches are exactly 100. Gold is the price, not a traded good.');
}

function board(mode) {
  const world = $('world');
  const geo = contract.geometry[mode], matrix = geo.worldToSource;
  world.append(element('rect', { width: 1376, height: 768, fill: '#2a241d' }));
  for (const road of geo.roads ?? []) world.append(element('polyline', { points: road.map(p => project(matrix, [p[0] + .5, p[1] + .5]).join(',')).join(' '), fill: 'none', stroke: '#b7a48a', 'stroke-width': 8 }));
  for (const site of geo.sites ?? []) {
    const [x, y, w, h] = site.rect;
    world.append(element('polygon', { points: [[x, y], [x + w, y], [x + w, y + h], [x, y + h]].map(v => project(matrix, v).join(',')).join(' '), fill: '#40544a88', stroke: '#d5b573' }));
  }
}

function tactical() {
  const world = $('world');
  const geo = contract.geometry.tactical;
  const matrix = geo.worldToSource;
  world.append(element('rect', { width: 1376, height: 768, fill: '#243028' }));
  for (let y = 0; y < geo.rows; y++) for (let x = 0; x < geo.cols; x++) {
    const blockedCell = (geo.blocked ?? []).some(cell => cell[0] === x && cell[1] === y) && !(geo.bridges ?? []).some(bridge => bridge.cells.some(cell => cell[0] === x && cell[1] === y));
    const obstacle = (geo.obstacles ?? []).some(cell => cell[0] === x && cell[1] === y);
    world.append(element('polygon', { points: cellPoints(matrix, x, y), fill: blockedCell ? '#3d6d8866' : obstacle ? '#4a403866' : '#40544a33', stroke: '#6d7a72' }));
  }
  const battle = state.battle;
  $('selected').textContent = battle ? `Battle round ${battle.round}` : 'Tactical';
  if (!battle) {
    say(blocked.tactical + ' Gate strength elsewhere is ' + gateHp(state) + '.');
    return;
  }
  const active = battle.status === 'ACTIVE' ? activeStackId(battle) : null;
  const legal = active ? legalTargets(battle, active) : { melee: [], ranged: [], moves: [] };
  for (const stack of battle.stacks) {
    if (stack.x == null || stack.dead) continue;
    const centre = project(matrix, [stack.x + 0.5, stack.y + 0.5]);
    world.append(element('circle', { cx: centre[0], cy: centre[1], r: 18, fill: stack.side === 'p' ? '#d5b573' : '#c83e38', stroke: stack.id === active ? '#f1e9d9' : 'none', 'stroke-width': 4 }));
    const label = element('text', { x: centre[0], y: centre[1] + 4, 'text-anchor': 'middle', fill: '#10171b', 'font-size': 12 });
    label.textContent = String(stack.count);
    world.append(label);
  }
  if (battle.pendingSettlement) $('choices').append(button('Apply the battle result', () => act('SETTLE_BATTLE', {})));
  if (active) {
    const stack = battle.stacks.find(item => item.id === active);
    for (const cell of legal.moves) $('choices').append(button(`Move ${stack.id} to ${cell[0]},${cell[1]}`, () => act('BATTLE', { action: 'move', stackId: active, to: cell })));
    for (const target of legal.melee) {
      const payload = meleeCommand(battle, active, target);
      $('choices').append(button(`Melee ${target}`, () => act('BATTLE', payload)));
    }
    for (const target of legal.ranged) $('choices').append(button(`Shoot ${target}`, () => act('BATTLE', { action: 'strike', stackId: active, targetId: target })));
    $('choices').append(button('Defend', () => act('BATTLE', { action: 'defend', stackId: active })));
    $('choices').append(button('Wait', () => act('BATTLE', { action: 'wait', stackId: active }), stack.waited));
    if (stack.side === 'p' && !battle.castThisRound) {
      for (const [spellId, spell] of Object.entries(data.SPELLS)) {
        if (spell.lv > 1 + (battle.wisdom || 0) || spell.mana > battle.mana) continue;
        const targets = battle.stacks.filter(item => !item.dead && (spell.type === 'dmg' || spell.type === 'aoe' || spell.type === 'debuff' ? item.side === 'e' : item.side === 'p'));
        for (const target of targets) $('choices').append(button(`${spell.n} on ${target.id}`, () => act('BATTLE', { action: 'spell', spell: spellId, targetId: target.id })));
      }
    }
    $('choices').append(button('Auto', () => act('BATTLE', { action: 'auto' })));
    $('choices').append(button('Retreat', () => act('BATTLE', { action: 'retreat', confirm: true })));
  }
  const last = battle.log?.[battle.log.length - 1];
  say(`Development art. ${battle.practice} battle, ${battle.stacks.filter(item => !item.dead).length} stacks. ${last ? last.type : 'No action yet.'} ${blocked.tactical}`);
}

function defense() {
  board('defense');
  const session = state.defense;
  $('selected').textContent = session ? `${session.practice} core ${Math.max(0, Math.round(session.core))}` : 'Defense';
  if (session?.status === 'ACTIVE') {
    $('choices').append(button(session.paused ? 'Resume' : 'Pause', () => act('DEFENSE', { paused: !session.paused, dt: 0 })));
    $('choices').append(button(session.speed === 2 ? 'Speed 1x' : 'Speed 2x', () => act('DEFENSE', { speed: session.speed === 2 ? 1 : 2, dt: 0 })));
    $('choices').append(button('Deploy hero', () => act('DEPLOY_DEFENSE', {}), session.heroDeployed));
    if (session.practice === 'siege') $('choices').append(button('Early call', () => act('EARLY_CALL', {})));
  }
  if (session?.pendingSettlement) $('choices').append(button('Apply the defense result', () => act('SETTLE_DEFENSE', {})));
  if (!session) {
    for (const tower of state.towers) $('choices').append(button('Retrofit ' + tower.fam + ' tier ' + tower.tier, () => act('RETROFIT', { towerId: tower.id })));
    for (const family of Object.keys(data.TOWERS)) $('choices').append(button('Buy ' + data.TOWERS[family].n, () => act('BUY_TOWER', { family })));
  }
  const wave = session ? `Wave ${session.clearedWaves}/${session.waves}. ` : '';
  say(wave + blocked.defense);
}

function story() {
  clearWorld();
  $('selected').textContent = state.story.rival ?? 'Choose a rival';
  if (!state.story.rival) for (const name of RIVALS) $('choices').append(button(name, () => act('CHOOSE_RIVAL', { name })));
  say('Seven saved subjects remain in the story data. The Future conclusion is The Valley We Keep: the same valley uses its new tools, and no mechanical reward is granted from this text. ' + blocked.loot);
}

function war() {
  clearWorld();
  $('selected').textContent = 'War';
  $('choices').append(button('Skirmish', () => { act('START_SKIRMISH', {}); if (state.battle) { view = 'tactical'; render(); } }));
  $('choices').append(button('Campaign Siege', () => { act('START_SIEGE', {}); if (state.defense) { view = 'defense'; render(); } }));
  $('choices').append(button('Tactical Duel', () => { act('START_DUEL', {}); if (state.battle) { view = 'tactical'; render(); } }));
  $('choices').append(button('Endless', () => { act('START_ENDLESS', {}); if (state.defense) { view = 'defense'; render(); } }));
  $('choices').append(button('Challenge', () => { act('START_CHALLENGE', { seed: state.seed >>> 0, code: `day-${state.day}` }); if (state.battle) { view = 'tactical'; render(); } }));
}

function settings() {
  clearWorld();
  $('selected').textContent = 'Settings';
  $('choices').append(button(state.settings.reducedMotion ? 'Reduced motion on' : 'Reduced motion off', () => act('SETTINGS', { ...state.settings, reducedMotion: !state.settings.reducedMotion })));
  $('choices').append(button('Music down', () => act('SETTINGS', { ...state.settings, music: Math.max(0, Math.round((state.settings.music - 0.2) * 10) / 10) })));
  $('choices').append(button('Music up', () => act('SETTINGS', { ...state.settings, music: Math.min(1, Math.round((state.settings.music + 0.2) * 10) / 10) })));
  $('choices').append(button('Sound down', () => act('SETTINGS', { ...state.settings, sfx: Math.max(0, Math.round((state.settings.sfx - 0.2) * 10) / 10) })));
  $('choices').append(button('Sound up', () => act('SETTINGS', { ...state.settings, sfx: Math.min(1, Math.round((state.settings.sfx + 0.2) * 10) / 10) })));
  $('choices').append(button('Arm local audio', () => { arm(state.settings); blip(); say('Local tones use separate music and sound gains. Nothing is downloaded.'); }));
  say(`Music ${state.settings.music}, sound ${state.settings.sfx}. Haptics are unavailable. No account or network setting is present.`);
}

function resumeDestination() {
  if (state?.battle) return state.battle.kind === 'defense' ? 'defense' : 'tactical';
  const name = rememberedView(localStorage, screens);
  return name === 'home' ? 'kingdom' : name;
}
function home() {
  clearWorld();
  $('selected').textContent = 'Ages of Dominion';
  if (state) $('choices').append(button('Continue', () => { view = resumeDestination(); render(); }));
  if (initial.backup) $('choices').append(button('Restore valid backup', () => { localStorage.removeItem(SAVE_KEY); state = initial.backup; view = 'kingdom'; persist(); installLifecycle(); render(); }));
  if (initial.status === 'DAMAGED') $('choices').append(button('Export damaged save', () => {
    const blob = new Blob([localStorage.getItem(SAVE_KEY)], { type: 'application/json' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob); link.download = 'aod-damaged-save.json'; link.click(); URL.revokeObjectURL(link.href);
  }));
  $('choices').append(button('New campaign', () => {
    if (state && !confirm('Replace the current campaign on this device?')) return;
    state = newCampaign(contract, data, Date.now());
    view = 'hero';
    installLifecycle();
    persist(); render();
  }));
  if (!state) say('No valid campaign is loaded.');
}

const draw = { home, kingdom, adventure, hero, army, forge, market, tactical, defense, story, war, settings };

function setPanel(open) {
  $('panel').classList.toggle('open', open);
  $('context').setAttribute('aria-expanded', String(open));
}
function render() {
  resources();
  $('choices').replaceChildren();
  clearWorld();
  const nav = $('nav');
  nav.replaceChildren();
  for (const name of screens) {
    const node = button(name[0].toUpperCase() + name.slice(1), () => { view = name; render(); });
    if (name === view) node.setAttribute('aria-current', 'true');
    nav.append(node);
  }
  if (!state && view !== 'home') view = 'home';
  if (state && view !== 'home') rememberView(localStorage, view, screens);
  $('status').textContent = state ? `${data.AGES[state.age].n} · day ${state.day}` : 'No campaign';
  draw[view]();
  if (resumeNote && view !== 'home') {
    say(resumeNote + ' Dismissing this report does not credit the clock again.');
    $('choices').prepend(button('Dismiss resume report', () => { resumeNote = ''; render(); }));
  }
}

function installLifecycle() {
  if (timer) return;
  timer = setInterval(() => {
    if (!state || suspended) return;
    const now = Date.now();
    state = advanceReported(state, now, data).state;
    if (view === 'defense' && state.defense?.status === 'ACTIVE' && !state.defense.paused) {
      try { state = command(state, { id: crypto.randomUUID(), type: 'DEFENSE', payload: { dt: 0.25, speed: state.defense.speed } }, now, data); } catch { /* A rejected step does not invent a later attack. */ }
    }
    if (view === 'kingdom' || view === 'adventure' || view === 'defense') render();
  }, 250);
}
$('save').onclick = () => { if (state) persist(); };
$('context').onclick = () => setPanel(!$('panel').classList.contains('open'));
$('world').addEventListener('click', event => {
  if (view !== 'kingdom' || !state) return;
  const [sourceX, sourceY] = sourceFromPointer(event);
  if (sourceX < 0 || sourceY < 0 || sourceX > 1376 || sourceY > 768) {
    window.rebornPick = { point: [sourceX, sourceY], site: null };
    return;
  }
  const point = inverse(contract.geometry.kingdom.worldToSource, [sourceX, sourceY]);
  const hit = contract.geometry.kingdom.sites.find(site => {
    const [x, y, w, h] = site.rect;
    return point[0] >= x && point[0] <= x + w && point[1] >= y && point[1] <= y + h;
  });
  window.rebornPick = { point, site: hit?.id ?? null };
  if (hit) { selected = hit.id; setPanel(true); render(); }
});
function suspend() { suspended = true; if (state) { catchUp(Date.now(), false); persist(); } }
window.addEventListener('blur', suspend);
document.addEventListener('visibilitychange', () => { if (document.hidden) suspend(); else { suspended = false; catchUp(Date.now(), true); render(); } });
window.addEventListener('focus', () => { suspended = false; });
window.addEventListener('pagehide', suspend);
window.addEventListener('resize', render);
if (state) { catchUp(Date.now(), true); persist(); installLifecycle(); }
if (initial.status === 'DAMAGED') view = 'home';
render();
window.rebornSnapshot = () => state ? JSON.parse(JSON.parse(encode(state, data)).payload) : null;
