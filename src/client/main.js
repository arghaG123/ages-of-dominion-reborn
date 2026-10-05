import data from '../data/reference-data.json' with { type: 'json' };
import contract from '../data/implementation-contract.json' with { type: 'json' };
import selection from '../data/reviewed-source-selection.json' with { type: 'json' };
import scene from '../data/stone-scene.json' with { type: 'json' };
import ageBuildings from '../data/age-buildings.json' with { type: 'json' };
import { newCampaign, command, advanceReported, formatResume, cost, heroStats, manaMax, dailyMoves, gateHp, futureConclusion, questReady, stackTitle } from '../core/campaign.js';
import { activeStackId, legalTargets, meleeCommand } from '../core/battle.js';
import { save, load, SAVE_KEY, rememberView, rememberedView, encode, decode, restoreBackup, storeSlot, loadSlot, replaceCampaign } from '../core/save.js';
import { camera, inverse, project, kingdomFocusBounds, targetSourceSize } from './projection.js';
import { defenseMarkers } from '../core/defense.js';
import { attackerPlate, drawActor, drawMount, drawPlate, drawReviewMount, drawSchematic, drawStaticMount, plateForStack, projectilePlate, staticMountForAge, towerPlate, troopPlate } from './actor.js';
import { drawBoundActor } from './anatomy.js';
import { pendingPortrait, portraitCard } from './portraits.js';
import { heroFocus, heroStage, wallPresentation } from './presentation.js';
import { armedChoice, parseChallenge } from './choices.js';
import { createFrameClock, travelProgress, travelSample } from './motion.js';
import { applySettings, arm, blip, nextSuspended, suspendAudio, resumeAudio } from './audio.js';
import { SKILL_IDS, GEAR_SLOTS, RIVALS, forgeOffer, gearBonus, recruitCost, spellEffect, towerPurchaseCost } from '../core/rules.js';
import { unitStats } from '../core/mechanics.js';
import { adventureMap, routeCost } from '../core/navigation.js';
import { challengeDescriptor, validateDescriptor, encodeChallengeCode, decodeChallengeCode, challengeResult } from '../core/challenge.js';

const $ = id => document.getElementById(id);
const svgNS = 'http://www.w3.org/2000/svg';
const ages = ['stone', 'bronze', 'iron', 'medieval', 'gunpowder', 'industrial', 'modern', 'future'];
const screens = ['home', 'kingdom', 'adventure', 'hero', 'army', 'forge', 'market', 'tactical', 'defense', 'story', 'war', 'settings', 'help'];
const blocked = {
  tactical: 'Choose a move, a spell, or wait.',
  defense: 'Hold the lane. Pause stops the attack.',
  war: 'Skirmish and Challenge do not pay campaign gold. Siege and Duel settle campaign rewards once.',
  skills: 'A skill offer waits until you choose or decline it.',
  loot: 'Offers stay with this save.'
};
const primaryNav = new Set(['kingdom', 'adventure', 'hero', 'war']);
const initial = load(localStorage, data);
let state = initial.state, selected = 'P01', suspended = false, timer, frameClock, resumeNote = '', clip = 'idle', opponentRender = false, saveFault = '';
let frameFit = { width: 1, height: 1, fit: { scale: 1, offset: [0, 0] } };
let armed = null;
let suppressClick = false;
let motionTime = 0;
let worldOnly = false;
let travelPreview = null;
let travelMotion = null;
let forgeSlot = 'weapon';
let plateReviewAge = null;
let moreOpen = false;
let challengeDraft = { seed: '123456789', code: 'valley-1', error: '', copy: '' };
let view = initial.status === 'VALID' ? rememberedView(localStorage, screens) : 'home';
const tutorialCue = ['Build a Lumber Camp.', 'Build a Farm.', 'Build a Quarry.', 'Build a Barracks.', 'Recruit a stack.', 'Leave town.', 'Fight the guard.', 'Hold the lane.'];
const tutorialChoice = ['lumber', 'farm', 'quarry', 'barracks', 'recruit:', 'enter-adventure', 'begin-encounter', 'start-siege'];
const slotName = { helm: 'Helmet', weapon: 'Weapon', offhand: 'Shield', armor: 'Chest', boots: 'Greaves', accessory: 'Ring' };
const say = text => { $('message').textContent = text; };
const animTime = () => (state?.settings?.reducedMotion ? 0 : motionTime);
const levelOf = type => state.plots.find(plot => plot.type === type)?.level ?? 0;
if (initial.status === 'DAMAGED') {
  view = 'home';
  say(initial.error + ' The damaged save is still stored.');
}

function persist() {
  try { save(localStorage, state, data); rememberView(localStorage, view, screens); saveFault = ''; }
  catch (error) { saveFault = error.message; }
}
function replaceLive(next, nextView, success) {
  let stored;
  try { stored = replaceCampaign(localStorage, next, data); }
  catch (error) {
    saveFault = error.message;
    render();
    return false;
  }
  state = stored;
  view = nextView;
  saveFault = '';
  rememberView(localStorage, view, screens);
  installLifecycle();
  render();
  if (success) say(success);
  $('status').textContent = 'Saved locally';
  return true;
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
  if (!state || state.tutorial.skipped || state.tutorial.step > 7) return '';
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
function button(label, onClick, disabled = false, choiceId = '', dock = false) {
  const build = () => {
    const node = document.createElement('button');
    node.type = 'button';
    node.textContent = label;
    node.disabled = disabled;
    if (disabled) node.title = label;
    if (choiceId) node.dataset.choice = choiceId;
    node.addEventListener('pointerdown', () => { armed = { id: choiceId, fn: onClick }; });
    node.addEventListener('click', event => {
      const released = event.currentTarget.dataset.choice || '';
      if (armed?.id && released && armed.id !== released) {
        event.preventDefault();
        event.stopPropagation();
        return;
      }
      onClick();
    });
    return node;
  };
  const node = build();
  if (dock) $('dock').append(build());
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
  $('terrain').alt = ages[state.age] + ' kingdom ground';
  $('terrain').dataset.terrainStatus = 'baked-unaccepted';
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
      'aria-label': 'Town Hall',
    }));
  }
  for (const road of geo.roads) world.append(element('polyline', { points: road.map(p => project(matrix, p).join(',')).join(' '), fill: 'none', stroke: '#9c8870', 'stroke-width': 10 }));
  const walls = wallPresentation(geo);
  world.append(element('polyline', {
    points: walls.points.map(point => project(matrix, point).join(',')).join(' '),
    fill: 'none',
    stroke: state.walls.level ? '#e6d3a1' : '#8a7560',
    'stroke-width': state.walls.level ? 8 : 6,
    'stroke-dasharray': state.walls.level ? '' : '16 10',
    'data-walls': state.walls.level ? 'built' : 'unbuilt',
    'data-walls-level': String(state.walls.level),
    'data-walls-presentation': walls.version,
    'pointer-events': 'none',
  }));
  const tone = ['#5d6b52', '#6a6248', '#6a5344', '#534c66', '#6a6248', '#5a4e44', '#445866', '#3e5560'][state.age] || '#5d6b52';
  const scale = frameFit.fit.scale || 1;
  for (const site of geo.sites) {
    const plot = state.plots.find(p => p.id === site.id), [x, y, w, h] = site.rect, centre = project(matrix, [x + w / 2, y + h / 2]);
    const job = state.buildJobs.find(j => j.plotId === plot.id);
    const group = element('g', { class: 'plot' + (plot.id === selected ? ' selected' : ''), tabindex: 0, role: 'button', 'aria-label': `${plot.id}: ${plot.type ?? 'empty plot'} level ${plot.level}` });
    const measured = plot.level && plot.type && !(plot.id === 'townhall' && ages[state.age] === 'stone')
      ? ageBuildings.ages[ages[state.age]]?.[plot.type]
      : null;
    if (measured?.file && !job) {
      const left = project(matrix, [x, y + h]);
      const right = project(matrix, [x + w, y + h]);
      const feet = project(matrix, [x + w / 2, y + h]);
      const padWidth = Math.hypot(right[0] - left[0], right[1] - left[1]) || 1;
      const drawW = padWidth * 1.08;
      const drawH = drawW * (measured.height / measured.width);
      const footX = measured.foot[0] * drawW;
      const footY = measured.foot[1] * drawH;
      group.append(element('image', {
        href: measured.file, x: feet[0] - footX, y: feet[1] - footY, width: drawW, height: drawH,
        'aria-label': `${data.BUILDINGS[plot.type].n} via ${ageBuildings.version}; ${ageBuildings.status}`,
        'pointer-events': 'none',
      }));
    } else {
      const footprint = element('polygon', { class: job ? 'scaffold' : plot.level ? 'building' : 'empty', points: [[x, y], [x + w, y], [x + w, y + h], [x, y + h]].map(v => project(matrix, v).join(',')).join(' ') });
      if (job) { footprint.setAttribute('fill', '#d5b57355'); footprint.setAttribute('stroke', '#d5b573'); }
      else if (plot.level && plot.id !== 'townhall') { footprint.setAttribute('fill', tone); footprint.setAttribute('stroke', '#e6d3a1'); }
      else if (!plot.level) { footprint.setAttribute('stroke', '#e6d3a1'); }
      group.append(footprint);
      if (!plot.level && plot.id !== 'townhall') {
        group.append(element('line', {
          x1: centre[0], y1: centre[1] - 12, x2: centre[0], y2: centre[1] + 10,
          stroke: '#f1e4cf', 'stroke-width': 3, 'pointer-events': 'none', 'data-stake': plot.id,
        }));
      }
      if (plot.type && plot.id !== 'townhall' && !measured) {
        const label = element('text', { x: centre[0], y: centre[1] + targetSourceSize(scale) * 0.42, 'text-anchor': 'middle', fill: '#f1e9d9', 'font-size': Math.max(14, 16 / scale), 'pointer-events': 'none' });
        label.textContent = data.BUILDINGS[plot.type].n;
        group.append(label);
      }
    }
    const diameter = targetSourceSize(scale);
    group.append(element('rect', { x: centre[0] - diameter / 2, y: centre[1] - diameter / 2, width: diameter, height: diameter, fill: 'transparent' }));
    if (job) {
      group.append(element('circle', { cx: centre[0], cy: centre[1], r: Math.max(6, 10 / scale), fill: '#f1e9d9', stroke: '#d5b573', 'pointer-events': 'none' }));
      const worker = { x: centre[0], y: centre[1], clip: 'work', time: animTime(), reduced: state.settings.reducedMotion };
      if (!drawActor(group, element, state.hero.class, { ...worker, scale: 0.08 }) && !drawBoundActor(group, element, state.hero.class, { ...worker, scale: 0.22 })) {
        drawSchematic(group, element, centre[0], centre[1], { scale: 0.28, clip: 'work', time: animTime(), reduced: state.settings.reducedMotion });
      }
    }
    group.onclick = () => { selected = plot.id; render(); };
    group.onkeydown = event => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); selected = plot.id; render(); } };
    world.append(group);
  }
  if (worldOnly) return;
  const plot = state.plots.find(p => p.id === selected);
  $('selected').textContent = plot.type ? `${data.BUILDINGS[plot.type].n} · level ${plot.level}` : selected + ' · empty plot';
  const types = plot.type ? [plot.type] : Object.keys(data.BUILDINGS).filter(k => !['townhall', 'walls'].includes(k));
  const stepType = ['lumber', 'farm', 'quarry', 'barracks'][state.tutorial.step];
  const wantsWorkshop = !state.plots.some(item => item.type === 'workshop') && state.tutorial.step >= 4;
  for (const type of types) {
    const payment = cost(data, type, plot.level);
    const price = Object.entries(payment).map(([k, v]) => v + ' ' + k).join(', ');
    const short = Object.entries(payment).filter(([k, v]) => state.resources[k] < v).map(([k, v]) => `${Math.ceil(v - state.resources[k])} ${k}`);
    const busy = state.buildJobs.some(j => j.plotId === plot.id);
    const reason = busy ? 'Construction is already underway here.' : short.length ? `Need ${short.join(', ')}.` : '';
    const label = `${plot.type ? 'Upgrade ' : 'Build '}${data.BUILDINGS[type].n} — ${price}${reason ? ' — ' + reason : ''}`;
    const dock = !plot.type && (type === stepType || (wantsWorkshop && type === 'workshop'));
    $('choices').append(button(label, () => act('BUILD', { plotId: plot.id, building: type }), busy || short.length > 0, `build:${plot.id}:${type}`, dock));
  }
  const hallPay = cost(data, 'townhall', hallPlot?.level ?? 1);
  const hallShort = Object.entries(hallPay).filter(([k, v]) => state.resources[k] < v).map(([k, v]) => `${Math.ceil(v - state.resources[k])} ${k}`);
  $('choices').append(button('Upgrade Town Hall — ' + Object.entries(hallPay).map(([k, v]) => v + ' ' + k).join(', ') + (hallShort.length ? ' — Need ' + hallShort.join(', ') : ''), () => act('BUILD', { plotId: 'townhall', building: 'townhall' }), hallShort.length > 0 || state.buildJobs.some(j => j.plotId === 'townhall')));
  const wallPay = cost(data, 'walls', state.walls.level);
  const wallShort = Object.entries(wallPay).filter(([k, v]) => state.resources[k] < v).map(([k, v]) => `${Math.ceil(v - state.resources[k])} ${k}`);
  $('choices').append(button((state.walls.level ? 'Upgrade Walls' : 'Build Walls') + ' — ' + Object.entries(wallPay).map(([k, v]) => v + ' ' + k).join(', ') + (wallShort.length ? ' — Need ' + wallShort.join(', ') : ''), () => act('BUILD', { plotId: 'walls', building: 'walls' }), wallShort.length > 0 || state.buildJobs.some(j => j.plotId === 'walls'), 'build:walls'));
  $('choices').append(button('Advance age', () => act('AGE_UP', {})));
  $('choices').append(button('End day', () => act('END_DAY', {}), false, 'end-day'));
  if (state.tutorial.step >= 4) $('choices').append(button('Recruit', () => { view = 'army'; render(); }, false, 'go-recruit', true));
  const emptySites = state.plots.filter(item => item.id !== 'townhall' && item.level === 0).length;
  const wallLine = state.walls.level ? `Walls level ${state.walls.level}` : 'Walls are a separate site and are still unbuilt';
  const jobs = state.buildJobs.map(job => {
    const left = Math.max(0, Math.ceil((job.completesAt - state.clock) / 1000));
    return `${data.BUILDINGS[job.type].n} finishes in ${left}s`;
  });
  say(`${data.AGES[state.age].n}. Hall level ${hallPlot?.level ?? 0}. ${emptySites} of 17 sites are empty. ${wallLine}. ${jobs.length ? jobs.join('. ') + '. ' : ''}Day ${state.day}, ${state.weather}. ${cue()}`);
}

function measureFrame() {
  const rect = $('stage').getBoundingClientRect();
  const panel = $('panel');
  const inset = panel.classList.contains('open') ? panel.getBoundingClientRect().width + 8 : 0;
  const width = Math.max(1, rect.width - inset);
  const height = Math.max(1, rect.height);
  const focus = view === 'kingdom'
    ? kingdomFocusBounds(contract.geometry.kingdom, scene.hall)
    : (view === 'hero' || view === 'home') ? heroFocus() : null;
  frameFit = { width, height, inset, rect, fit: camera([1376, 768], width, height, focus, view === 'kingdom' ? 24 : focus ? 12 : 0) };
}
function fitScene() {
  const fit = frameFit.fit;
  const frame = $('frame');
  frame.style.width = '1376px';
  frame.style.height = '768px';
  frame.style.transformOrigin = '0 0';
  frame.style.transform = `translate(${fit.offset[0]}px, ${fit.offset[1]}px) scale(${fit.scale})`;
  $('world').setAttribute('preserveAspectRatio', 'none');
  $('terrain').style.objectFit = 'fill';
}
function sourceFromPointer(event) {
  measureFrame();
  const rect = frameFit.rect;
  const fit = frameFit.fit;
  return [(event.clientX - rect.left - fit.offset[0]) / fit.scale, (event.clientY - rect.top - fit.offset[1]) / fit.scale];
}

function cellPoints(matrix, x, y, w = 1, h = 1) {
  return [[x, y], [x + w, y], [x + w, y + h], [x, y + h]].map(v => project(matrix, v).join(',')).join(' ');
}

function adventure() {
  const world = $('world');
  const geo = contract.geometry.adventure, matrix = geo.worldToSource;
  world.append(element('rect', { width: 1376, height: 768, fill: '#1b3328' }));
  world.append(element('ellipse', { cx: 980, cy: 180, rx: 420, ry: 160, fill: '#3d6a48' }));
  world.append(element('ellipse', { cx: 280, cy: 560, rx: 360, ry: 180, fill: '#254433' }));
  for (const road of geo.roads) {
    const points = road.map(p => project(matrix, [p[0] + .5, p[1] + .5]).join(',')).join(' ');
    world.append(element('polyline', { points, fill: 'none', stroke: '#6b5344', 'stroke-width': 22, 'stroke-linecap': 'round' }));
    world.append(element('polyline', { points, fill: 'none', stroke: '#c4a574', 'stroke-width': 8, 'stroke-linecap': 'round' }));
  }
  for (const [x, y] of geo.blocked ?? []) world.append(element('polygon', { class: 'water', points: cellPoints(matrix, x, y) }));
  for (const site of geo.sites) {
    const [x, y, w, h] = site.rect;
    world.append(element('polygon', { class: 'site', points: cellPoints(matrix, x, y, w, h) }));
    const centre = project(matrix, [x + w / 2, y + h / 2]);
    const label = element('text', { x: centre[0], y: centre[1] - 16, 'text-anchor': 'middle', fill: '#f1e9d9', 'font-size': 14, 'pointer-events': 'none' });
    label.textContent = site.id;
    world.append(label);
  }
  if (state.adventure) {
    const seen = new Set(state.adventure.visited);
    for (let y = 0; y < geo.rows; y++) for (let x = 0; x < geo.cols; x++) {
      if (!seen.has(`${x},${y}`)) world.append(element('polygon', { class: 'fog', points: cellPoints(matrix, x, y), fill: '#10171b88' }));
    }
  }
  for (const [name, cell] of Object.entries(geo.anchors)) {
    const centre = project(matrix, [cell[0], cell[1]]);
    const kind = name.startsWith('guard') ? 'guard' : name === 'hero' ? 'anchor' : 'pickup';
    world.append(element('circle', { class: kind, cx: centre[0], cy: centre[1], r: name.startsWith('guard') ? 10 : 7 }));
  }
  if (state.adventure && !state.adventure.atTown) {
    const map = adventureMap(geo);
    const committed = [state.adventure.x, state.adventure.y];
    let shown = [committed[0] + 0.5, committed[1] + 0.5];
    let facing = 1;
    let moving = false;
    if (travelMotion && !state.settings.reducedMotion) {
      const u = travelProgress(travelMotion.started, motionTime, travelMotion.duration);
      const sample = travelSample(travelMotion.points, u);
      shown = [sample.x, sample.y];
      facing = sample.facing;
      moving = u < 1;
      if (u >= 1) travelMotion = null;
    }
    if (travelPreview?.cells?.length) {
      const previewPoints = [[state.adventure.x, state.adventure.y], ...travelPreview.cells]
        .map(cell => project(matrix, [cell[0] + 0.5, cell[1] + 0.5]).join(','));
      world.append(element('polyline', { points: previewPoints.join(' '), fill: 'none', stroke: '#70b9c5', 'stroke-width': 4, 'stroke-dasharray': '8 6' }));
    }
    const placeTraveler = (at) => {
      const agedMount = staticMountForAge(state.age);
      if (agedMount && drawStaticMount(world, element, agedMount, at[0], at[1], {
        facing, moving, time: animTime(), reduced: state.settings.reducedMotion,
      })) return;
      if (drawMount(world, element, {
        x: at[0], y: at[1], scale: 0.07, facing, moving,
        time: animTime(), reduced: state.settings.reducedMotion,
        riderClass: state.hero.class,
      })) return;
      const review = drawReviewMount(world, element, {
        x: at[0], y: at[1], facing, moving,
        time: animTime(), reduced: state.settings.reducedMotion,
      });
      if (review) {
        const rider = drawBoundActor(world, element, state.hero.class, {
          x: review.saddle.x + facing * -2,
          y: review.saddle.y + 34,
          scale: 0.34,
          facing,
          clip: moving && !state.settings.reducedMotion ? 'mountWalk' : 'idle',
          time: animTime(),
          reduced: state.settings.reducedMotion || !moving,
        });
        if (rider) {
          rider.setAttribute('data-mount-mark', 'review-horse-v4');
          rider.setAttribute('data-rider', 'painted-partial');
        } else {
          drawSchematic(world, element, review.saddle.x, review.saddle.y + 16, {
            scale: 0.7, facing, moving, mounted: false, clip: 'idle',
            time: animTime(), reduced: state.settings.reducedMotion,
          });
        }
        return;
      }
      const horse = drawSchematic(world, element, at[0], at[1], {
        scale: 2.2, facing, moving, mounted: true, rider: 'omit', clip: moving ? 'walk' : 'idle',
        time: animTime(), reduced: state.settings.reducedMotion,
      });
      const rider = drawBoundActor(world, element, state.hero.class, {
        x: at[0] + facing * -10,
        y: at[1] - 28,
        scale: 0.46,
        facing,
        clip: moving && !state.settings.reducedMotion ? 'mountWalk' : 'idle',
        time: animTime(),
        reduced: state.settings.reducedMotion || !moving,
      });
      if (!rider) {
        horse.remove();
        drawSchematic(world, element, at[0], at[1], {
          scale: 2.2, facing, moving, mounted: true, clip: moving ? 'walk' : 'idle',
          time: animTime(), reduced: state.settings.reducedMotion,
        });
      } else {
        rider.setAttribute('data-mount-mark', 'schematic-horse');
        rider.setAttribute('data-rider', 'painted-partial');
      }
    };
    if (worldOnly) {
      placeTraveler(project(matrix, shown));
      return;
    }
    placeTraveler(project(matrix, shown));
    $('selected').textContent = `Travel ${state.adventure.x},${state.adventure.y} · moves ${state.adventure.moves}`;
    const queueStep = (dx, dy) => {
      const from = travelPreview?.cells?.at(-1) || committed;
      const next = [from[0] + dx, from[1] + dy];
      const path = [...(travelPreview?.cells || []), next];
      try {
        const route = routeCost(map, committed, path);
        travelPreview = { path, cells: route.cells, cost: route.cost };
        render();
      } catch (error) { say(error.message); }
    };
    $('choices').append(button('North', () => queueStep(0, -1), false, 'preview-north', true));
    $('choices').append(button('South', () => queueStep(0, 1), false, 'preview-south', true));
    $('choices').append(button('West', () => queueStep(-1, 0), false, 'preview-west', true));
    $('choices').append(button('East', () => queueStep(1, 0), false, 'preview-east', true));
    $('choices').append(button(travelPreview ? `Confirm route · cost ${travelPreview.cost}` : 'Confirm route', () => {
      if (!travelPreview) { say('Preview a route before confirming.'); return; }
      const from = [state.adventure.x, state.adventure.y];
      const path = travelPreview.path;
      const moves = state.adventure.moves;
      act('MOVE', { path });
      if (state.adventure.moves < moves) {
        travelMotion = { points: [from, ...path], started: motionTime, duration: Math.max(0.35, path.length * 0.45) };
        travelPreview = null;
        render();
      }
    }, !travelPreview, 'confirm-route', true));
    $('choices').append(button('Clear preview', () => { travelPreview = null; render(); }, !travelPreview));
    $('choices').append(button('Rest', () => act('REST', {})));
    const approach = geo.sites.find(site => site.id === 'town').approach;
    const atApproach = state.adventure.x === approach[0] && state.adventure.y === approach[1];
    const returnReason = state.adventure.pendingEncounter ? 'Clear the guard before returning.' : atApproach ? '' : 'Reach the town approach first.';
    $('choices').append(button(returnReason ? `Return — ${returnReason}` : 'Return to town', () => { travelMotion = null; act('RETURN_TOWN', {}); view = 'kingdom'; render(); }, Boolean(returnReason), 'return-town', true));
    if (state.adventure.pendingEncounter && !state.battle) $('choices').append(button('Fight the guard', () => { travelMotion = null; act('BEGIN_ENCOUNTER', {}); if (state.battle) { view = 'tactical'; render(); } }, false, 'begin-encounter', true));
    const preview = travelPreview ? ` Preview cost ${travelPreview.cost}. Confirm spends that cost once.` : '';
    say((state.adventure.pendingEncounter ? 'An unresolved guard is waiting. Movement stays spent until that guard is cleared.' : 'Road steps cost 1. Water and site footprints are blocked.') + preview + cue());
  } else if (!worldOnly) {
    $('selected').textContent = 'Adventure';
    $('choices').append(button('Leave town', () => { clip = 'walk'; travelPreview = null; travelMotion = null; act('ENTER_ADVENTURE', {}); }, false, 'enter-adventure', true));
    const remaining = state.adventure ? state.adventure.moves : dailyMoves(state, data);
    say(`Saved movement is ${remaining}. Leaving town again does not refill it. ${cue()}`);
  }
}

function paintCard(world, card, presentation) {
  const stage = heroStage();
  world.append(element('line', {
    x1: stage.ground.x1, y1: stage.ground.y, x2: stage.ground.x2, y2: stage.ground.y,
    stroke: '#6d5a46', 'stroke-width': 4, 'data-ground': 'figure',
  }));
  if (card) {
    const box = stage.card;
    const group = element('g', {
      'data-actor': presentation === 'title-card' ? 'title' : state?.hero?.class || 'title',
      'data-clip': clip,
      'data-presentation': presentation,
      'data-articulation': 'card-bounded',
      'data-card-box': `${box.x},${box.y},${box.width},${box.height}`,
    });
    group.append(element('image', {
      href: card.file, x: box.x, y: box.y, width: box.width, height: box.height,
      'data-card-era': card.era,
      'data-card-status': presentation === 'pending-card' ? 'pending-review' : 'bounded-card',
    }));
    world.append(group);
  }
  const figure = { x: stage.figure.x, y: stage.figure.y, clip, time: animTime(), reduced: state?.settings?.reducedMotion, facing: 1 };
  if (!drawBoundActor(world, element, state?.hero?.class, { ...figure, scale: 0.85 })) {
    drawSchematic(world, element, stage.figure.x, stage.figure.y, { ...figure, scale: 2.1 });
  }
}
function paintHero() {
  const world = $('world');
  world.append(element('rect', { width: 1376, height: 768, fill: '#1b2822' }));
  const card = portraitCard(state.hero.class, state.age);
  const pending = pendingPortrait(state.hero.class, state.age);
  paintCard(world, card || pending, card ? 'portrait-card' : pending ? 'pending-card' : 'portrait-card');

  if (!card && !pending) {
    const note = element('text', { x: heroStage().card.x, y: heroStage().card.y + 48, fill: '#f1dba5', 'font-size': 28 });
    note.textContent = 'The knight portrait opens in the Medieval age.';
    world.append(note);
  }
}
function itemTitle(item) {
  if (!item) return 'empty';
  if (item.kind === 'artifact') return data.ARTIFACTS[item.artifactId]?.n || item.artifactId;
  const named = data.GEAR[item.slot]?.names?.[item.age];
  const quality = data.QUAL[item.quality]?.n || `Q${item.quality + 1}`;
  return `${named || slotName[item.slot] || item.slot} · ${quality}`;
}
function bonusText(item) {
  if (!item) return 'no item';
  const bonus = item.kind === 'gear' ? gearBonus(item) : (data.ARTIFACTS[item.artifactId]?.b || {});
  const text = Object.entries(bonus).map(([key, amount]) => `${key} +${amount}`).join(', ');
  return text || 'no stat change';
}
function hero() {
  clearWorld();
  const stats = heroStats(state, data);
  $('selected').textContent = data.CLASSES[state.hero.class].n;
  paintHero();
  for (const name of ['idle', 'walk', 'work', 'attack', 'hit', 'death']) {
    $('choices').append(button(name, () => { clip = name; render(); }, false, `clip:${name}`));
  }
  const classOpen = state.hero.xp === 0 && !state.inventory.length && !Object.values(state.hero.equip).some(Boolean) && !state.adventure && !state.battle;
  if (classOpen) {
    for (const id of Object.keys(data.CLASSES)) $('choices').append(button(data.CLASSES[id].n, () => act('SET_CLASS', { class: id }), false, `class:${id}`, true));
    $('choices').append(button('Enter the valley', () => { view = 'kingdom'; render(); }, false, 'enter-valley', true));
  }
  if (state.hero.points > 0) {
    for (const stat of ['atk', 'def', 'pow', 'kno']) {
      $('choices').append(button(`Spend point on ${stat}`, () => act('SPEND_POINT', { stat }), false, `spend:${stat}`));
    }
  }
  const offer = state.hero.offers.find(item => !item.chosen && !item.declined);
  for (const id of SKILL_IDS) {
    const skill = data.SKILLS[id];
    const level = state.hero.skills[id];
    const offered = offer?.choices.includes(id) && level < 3;
    $('choices').append(button(`${skill.ic} ${skill.n} ${level}/3`, () => {
      if (offered) act('CHOOSE_SKILL', { skill: id });
      else say(`${skill.n}: ${skill.d} Level ${level} of 3.`);
    }, false, `skill:${id}`));
  }
  if (offer) $('choices').append(button('Decline skill offer', () => act('DECLINE_SKILL', {}), false, 'decline-skill'));
  const wisdom = state.hero.skills.wisdom || 0;
  for (const [id, spell] of Object.entries(data.SPELLS)) {
    const eligible = spell.lv <= 1 + wisdom;
    const effect = spellEffect(id, stats.pow);
    $('choices').append(button(`${spell.ic} ${spell.n}`, () => {
      say(eligible
        ? `${spell.n} is available. ${spell.d}${effect == null ? '' : ` Effect ${effect}.`} Mana ${spell.mana}.`
        : `${spell.n} needs Wisdom ${spell.lv - 1}. It is not available.`);
    }, !eligible, `spell:${id}`));
  }
  const equipped = GEAR_SLOTS.map(slot => `${slotName[slot]}: ${itemTitle(state.hero.equip[slot])}`).join('; ');
  say(`Attack ${stats.atk}, Defense ${stats.def}, Power ${stats.pow}, Knowledge ${stats.kno}. Mana ${state.hero.mana}/${manaMax(state, data)}. Daily moves ${dailyMoves(state, data)}. Points ${state.hero.points}. ${equipped}. ${blocked.skills}`);
}

function paintArmy() {
  const world = $('world');
  world.append(element('rect', { width: 1376, height: 768, fill: '#24342c' }));
  const reviewAge = plateReviewAge == null ? state.age : plateReviewAge;
  let reviewX = 180;
  for (const role of ['melee', 'ranged', 'heavy']) {
    const plate = troopPlate(reviewAge, role);
    if (!drawPlate(world, element, plate, reviewX, 210, 130, { time: animTime(), clip: 'idle', reduced: state.settings.reducedMotion })) {
      const missing = element('text', { x: reviewX, y: 160, 'text-anchor': 'middle', fill: '#f1e9d9', 'font-size': 16 });
      missing.textContent = role;
      world.append(missing);
    }
    const caption = element('text', { x: reviewX, y: 236, 'text-anchor': 'middle', fill: '#f1dba5', 'font-size': 16, 'data-plate-review': `${reviewAge}-${role}` });
    caption.textContent = `${data.AGES[reviewAge].n} ${data.ROLES[role].names[reviewAge]}`;
    world.append(caption);
    reviewX += 220;
  }
  const agedMount = staticMountForAge(reviewAge);
  if (agedMount) {
    drawStaticMount(world, element, agedMount, 900, 200, { time: animTime(), reduced: state.settings.reducedMotion });
    const mountCaption = element('text', { x: 900, y: 236, 'text-anchor': 'middle', fill: '#f1dba5', 'font-size': 16, 'data-mount-review': agedMount.id });
    mountCaption.textContent = data.AGES[reviewAge].n + ' transport';
    world.append(mountCaption);
  }
  let x = 160;
  for (const stack of state.army) {
    const plate = plateForStack(stack);
    const fly = stack.kind === 'creature' && Boolean(data.CREATURES[stack.type]?.fly);
    if (!drawPlate(world, element, plate, x, 460, 220, { time: animTime(), fly, clip: 'walk', reduced: state.settings.reducedMotion })) {
      const text = element('text', { x, y: 360, 'text-anchor': 'middle', fill: '#f1e9d9', 'font-size': 18 });
      text.textContent = stack.type;
      world.append(text);
    }
    const caption = element('text', { x, y: 490, 'text-anchor': 'middle', fill: '#f1e9d9', 'font-size': 16 });
    caption.textContent = stackTitle(stack, data);
    world.append(caption);
    x += 260;
  }
}
function army() {
  clearWorld();
  $('selected').textContent = 'Army';
  paintArmy();
  const capacity = 2 + levelOf('barracks');
  for (const stack of state.army) {
    const label = stackTitle(stack, data);
    $('choices').append(button(label, () => {
      const stats = unitStats(stack, data);
      say(`${label}. Count ${stack.count}. Rank ${stack.rank}. XP ${stack.xp}. Attack ${stats.atk}, defense ${stats.def}, damage ${stats.dmin}-${stats.dmax}, HP ${stats.hp}, speed ${stats.spd}${stats.fly ? ', flies' : ''}.`);
    }, false, `stack:${stack.id}`));
  }
  for (const role of Object.keys(data.ROLES)) {
    const costText = Object.entries(recruitCost(data, role, state.age)).map(([key, amount]) => `${amount} ${key}`).join(', ');
    const payment = recruitCost(data, role, state.age);
    const short = Object.entries(payment).filter(([key, amount]) => state.resources[key] < amount).map(([key, amount]) => `${Math.ceil(amount - state.resources[key])} ${key}`);
    const noBarracks = levelOf('barracks') < 1;
    const full = state.army.length >= capacity && !state.army.some(stack => stack.kind === 'role' && stack.type === role && stack.age === state.age);
    const reason = noBarracks ? 'Barracks required.' : full ? 'Roster is full.' : short.length ? `Need ${short.join(', ')}.` : '';
    $('choices').append(button(`Recruit 5 ${data.ROLES[role].n} — ${costText}${reason ? ' — ' + reason : ''}`, () => act('RECRUIT', { role }), noBarracks || full || short.length > 0, `recruit:${role}`, role === 'melee'));
  }
  for (const [type, creature] of Object.entries(data.CREATURES)) {
    $('choices').append(button(`${creature.ic} ${creature.n}`, () => {
      const stats = unitStats({ kind: 'creature', type, age: state.age, rank: 0, xp: 0, count: 1 }, data);
      const costText = Object.entries(creature.cost).map(([key, amount]) => `${amount} ${key}`).join(', ');
      say(`${creature.n}, tier ${creature.t}, age ${data.AGES[state.age].n}. Attack ${stats.atk}, defense ${stats.def}, HP ${stats.hp}, damage ${stats.dmin}-${stats.dmax}, speed ${stats.spd}${stats.fly ? ', flies' : ''}. Dwelling cost ${costText}.`);
    }, false, `codex:${type}`));
  }
  const reviewAge = plateReviewAge == null ? state.age : plateReviewAge;
  $('choices').append(button(`Review ${data.AGES[(reviewAge + 7) % 8].n} plates`, () => { plateReviewAge = (reviewAge + 7) % 8; render(); }, false, 'plate-review-prev'));
  $('choices').append(button(`Review ${data.AGES[(reviewAge + 1) % 8].n} plates`, () => { plateReviewAge = (reviewAge + 1) % 8; render(); }, false, 'plate-review-next'));
  say(`Army ${state.army.length}/${capacity}. Capacity is 2 plus Barracks level. Recruitment pays five of the current age. Plate review does not change the age.`);
}

function paintForge() {
  const world = $('world');
  world.append(element('rect', { width: 1376, height: 768, fill: '#24342c' }));
  const columns = [['helm', 'weapon', 'offhand'], ['armor', 'boots', 'accessory']];
  let offer = null;
  try { offer = forgeOffer(state.age, levelOf('armory'), null); } catch { offer = null; }
  columns.forEach((slots, column) => {
    slots.forEach((slot, row) => {
      const x = column === 0 ? 360 : 980;
      const y = 220 + row * 180;
      const item = state.hero.equip[slot];
      const label = element('text', { x, y: y - 78, 'text-anchor': 'middle', fill: '#f1e9d9', 'font-size': 18 });
      label.textContent = `${slotName[slot]}: ${itemTitle(item)}`;
      world.append(label);
      world.append(element('rect', {
        x: x - 90, y: y - 64, width: 180, height: 96,
        fill: slot === forgeSlot ? '#3d3424' : '#152128', stroke: '#c9a35b',
        'data-slot': slot, 'data-selected': slot === forgeSlot ? '1' : '0',
      }));
    });
  });
  const worn = state.hero.equip[forgeSlot];
  const summary = element('text', { x: 688, y: 700, 'text-anchor': 'middle', fill: '#f1dba5', 'font-size': 22, 'data-forge-summary': '1' });
  const costText = offer ? Object.entries(offer.cost).map(([key, amount]) => `${amount} ${key}`).join(', ') : 'Armory required';
  const quality = offer ? (data.QUAL[offer.quality]?.n || `quality ${offer.quality}`) : 'no result';
  const nextItem = offer ? { kind: 'gear', slot: forgeSlot, age: state.age, quality: offer.quality } : null;
  summary.textContent = `${slotName[forgeSlot]} · worn ${itemTitle(worn)} (${bonusText(worn)}) · next ${nextItem ? itemTitle(nextItem) : quality} (${nextItem ? bonusText(nextItem) : 'no result'}) · ${costText}`;
  world.append(summary);
}
function forge() {
  clearWorld();
  $('selected').textContent = 'Forge';
  paintForge();
  let offer = null;
  let offerError = '';
  try { offer = forgeOffer(state.age, levelOf('armory'), null); }
  catch (error) { offerError = error.message; }
  for (const slot of GEAR_SLOTS) {
    $('choices').append(button(slotName[slot], () => { forgeSlot = slot; render(); }, false, `forge-slot:${slot}`));
    const worn = state.hero.equip[slot];
    if (worn) $('choices').append(button(`Unequip ${slotName[slot]}`, () => act('UNEQUIP', { slot })));
  }
  if (offer) {
    const named = data.GEAR[forgeSlot]?.names?.[state.age] || slotName[forgeSlot];
    const quality = data.QUAL[offer.quality]?.n || `quality ${offer.quality}`;
    const costText = Object.entries(offer.cost).map(([key, amount]) => `${amount} ${key}`).join(', ');
    const short = Object.entries(offer.cost).filter(([key, amount]) => state.resources[key] < amount).map(([key, amount]) => `${Math.ceil(amount - state.resources[key])} ${key}`);
    $('choices').append(button(`Forge ${named} · ${quality} — ${costText}${short.length ? ' — Need ' + short.join(', ') : ''}`, () => act('FORGE', { slot: forgeSlot, quality: offer.quality }), short.length > 0, 'forge-confirm', true));
  }
  for (const item of state.inventory) {
    const worn = state.hero.equip[item.slot];
    $('choices').append(button(`Equip ${itemTitle(item)}`, () => {
      say(`Bag ${itemTitle(item)} gives ${bonusText(item)}. Worn ${slotName[item.slot]} gives ${bonusText(worn)}.`);
      act('EQUIP', { itemId: item.id });
    }, false, `equip:${item.id}`, true));
  }
  const worn = state.hero.equip[forgeSlot];
  say(offer
    ? `Selected ${slotName[forgeSlot]}. Worn ${itemTitle(worn)} (${bonusText(worn)}). Armory level ${levelOf('armory')} unlocks quality ${offer.quality} at ${Object.entries(offer.cost).map(([k, n]) => n + ' ' + k).join(', ')}. Bag holds ${state.inventory.length}. There is no Enhance, Reforge or Socket action.`
    : `${offerError} Bag holds ${state.inventory.length}.`);
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
  world.append(element('rect', { width: 1376, height: 768, fill: mode === 'defense' ? '#243028' : '#2a3328' }));
  world.append(element('ellipse', { cx: 420, cy: 220, rx: 380, ry: 160, fill: '#31543c' }));
  world.append(element('ellipse', { cx: 980, cy: 540, rx: 420, ry: 180, fill: '#1d3328' }));
  if (mode === 'defense' && geo.lane) {
    const lane = geo.lane.map(point => project(matrix, point).join(',')).join(' ');
    world.append(element('polyline', { points: lane, fill: 'none', stroke: '#6b5344', 'stroke-width': 34, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }));
    world.append(element('polyline', { points: lane, fill: 'none', stroke: '#c4a574', 'stroke-width': 12, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }));
    const entry = project(matrix, geo.lane[0]);
    const gate = project(matrix, geo.lane.at(-1));
    world.append(element('circle', { cx: entry[0], cy: entry[1], r: 16, fill: '#c83e38', stroke: '#f1e9d9' }));
    world.append(element('rect', { x: gate[0] - 22, y: gate[1] - 34, width: 44, height: 48, fill: '#8a7560', stroke: '#e6d3a1', 'stroke-width': 3 }));
  }
  for (const road of geo.roads ?? []) {
    const points = road.map(p => project(matrix, [p[0] + .5, p[1] + .5]).join(',')).join(' ');
    world.append(element('polyline', { points, fill: 'none', stroke: '#6b5344', 'stroke-width': 18 }));
    world.append(element('polyline', { points, fill: 'none', stroke: '#c4a574', 'stroke-width': 6 }));
  }
  for (const site of geo.sites ?? []) {
    const [x, y, w, h] = site.rect;
    world.append(element('polygon', { points: [[x, y], [x + w, y], [x + w, y + h], [x, y + h]].map(v => project(matrix, v).join(',')).join(' '), fill: '#40544a55', stroke: '#d5b573' }));
  }
}

function drawFigure(world, origin, stack, alive) {
  const plate = plateForStack(stack);
  const fly = Boolean(stack.fly) || (stack.kind === 'creature' && Boolean(data.CREATURES[stack.type]?.fly));
  const clipName = alive ? (fly ? 'walk' : 'idle') : 'death';
  if (plate) drawPlate(world, element, plate, origin[0], origin[1] + 8, alive ? 28 : 22, { opacity: alive ? 1 : 0.35, time: animTime(), fly, clip: clipName, reduced: state.settings.reducedMotion });
  else world.append(element('circle', { cx: origin[0], cy: origin[1], r: 5, fill: alive ? '#d5b573' : '#6d6458' }));
}

function tactical() {
  const world = $('world');
  const geo = contract.geometry.tactical;
  const matrix = geo.worldToSource;
  const battle = state.battle;
  const active = battle?.status === 'ACTIVE' ? activeStackId(battle) : null;
  const legal = active ? legalTargets(battle, active) : { melee: [], ranged: [], moves: [] };
  world.append(element('rect', { width: 1376, height: 768, fill: '#243028' }));
  world.append(element('ellipse', { cx: 480, cy: 260, rx: 420, ry: 180, fill: '#31543c' }));
  for (let y = 0; y < geo.rows; y++) for (let x = 0; x < geo.cols; x++) {
    const blockedCell = (geo.blocked ?? []).some(cell => cell[0] === x && cell[1] === y) && !(geo.bridges ?? []).some(bridge => bridge.cells.some(cell => cell[0] === x && cell[1] === y));
    const obstacle = (geo.obstacles ?? []).some(cell => cell[0] === x && cell[1] === y);
    const legalCell = Boolean(active) && (legal.moves.some(cell => cell[0] === x && cell[1] === y) || battle.stacks.some(stack => stack.id === active && stack.x === x && stack.y === y));
    world.append(element('polygon', { points: cellPoints(matrix, x, y), fill: blockedCell ? '#3d6d8844' : legalCell ? '#70b9c533' : obstacle ? '#4a403844' : '#40544a14', stroke: legalCell ? '#70b9c5' : '#6d7a7244' }));
  }
  $('selected').textContent = battle ? `Battle round ${battle.round}` : 'No battle';
  if (!battle) {
    if (!worldOnly) {
      $('choices').append(button('Go to Adventure', () => { view = 'adventure'; render(); }, false, 'go-adventure', true));
      $('choices').append(button('Open War', () => { view = 'war'; render(); }, false, 'go-war', true));
      say('No battle is open. Leave town and fight the valley guard, or open War for a skirmish, duel, siege, endless defense or challenge. Gate strength is ' + gateHp(state) + '.');
    }
    return;
  }
  for (const stack of battle.stacks) {
    if (stack.x == null || stack.dead) continue;
    const centre = project(matrix, [stack.x + 0.5, stack.y + 0.5]);
    const shown = 7;
    const livingFigures = Math.max(0, Math.min(shown, Math.round(shown * stack.count / (stack.maxCount || stack.count))));
    for (let figure = 0; figure < shown; figure++) {
      const column = figure % 4;
      const row = Math.floor(figure / 4);
      drawFigure(world, [centre[0] + (column - 1.5) * 14, centre[1] + row * 16], stack, figure < livingFigures);
    }
    const label = element('text', { x: centre[0], y: centre[1] - 28, 'text-anchor': 'middle', fill: '#f1e9d9', 'font-size': 12 });
    label.textContent = `${stack.count} ${stack.type || stack.role || ''}`.trim();
    world.append(label);
  }
  if (worldOnly) return;
  if (battle.pendingSettlement) $('choices').append(button('Apply the battle result', () => act('SETTLE_BATTLE', {}), false, 'settle-battle', true));
  if (active) {
    const stack = battle.stacks.find(item => item.id === active);
    if (stack.side !== 'p') {
      if (opponentRender) { say('The opponent is acting.'); return; }
      opponentRender = true;
      try { act('BATTLE', { action: 'opponent' }); }
      finally { opponentRender = false; }
      return;
    }
    for (const cell of legal.moves) $('choices').append(button(`Move ${stack.id} to ${cell[0]},${cell[1]}`, () => act('BATTLE', { action: 'move', stackId: active, to: cell }), false, `move:${cell[0]},${cell[1]}`, true));
    for (const target of legal.melee) {
      const payload = meleeCommand(battle, active, target);
      $('choices').append(button(`Melee ${target}`, () => act('BATTLE', payload), false, `melee:${target}`, true));
    }
    for (const target of legal.ranged) $('choices').append(button(`Shoot ${target}`, () => act('BATTLE', { action: 'strike', stackId: active, targetId: target }), false, `shoot:${target}`, true));
    $('choices').append(button('Defend', () => act('BATTLE', { action: 'defend', stackId: active }), false, 'defend', true));
    $('choices').append(button(stack.waited ? 'Wait — this stack already waited' : 'Wait', () => act('BATTLE', { action: 'wait', stackId: active }), stack.waited, 'wait', true));
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
  const phase = battle.pendingSettlement ? 'The result is waiting. Apply it once.' : active ? blocked.tactical : 'The round is changing.';
  say(`${battle.practice} battle, round ${battle.round}. ${battle.stacks.filter(item => !item.dead).length} stacks remain. ${last ? 'Last action ' + last.type + '.' : 'No action yet.'} ${phase}`);
}

function defense() {
  board('defense');
  const session = state.defense;
  const world = $('world');
  const matrix = contract.geometry.defense.worldToSource;
  const markers = defenseMarkers(session);
  for (const tower of markers.towers) {
    const at = project(matrix, tower.at);
    const plate = towerPlate(state.age, tower.fam);
    if (!drawPlate(world, element, plate, at[0], at[1] + 8, 52, { opacity: tower.alive ? 1 : 0.4, time: animTime(), clip: 'attack', reduced: state.settings.reducedMotion })) {
      world.append(element('rect', { x: at[0] - 12, y: at[1] - 20, width: 24, height: 32, fill: '#8c7447' }));
    }
    const hpLabel = element('text', { x: at[0], y: at[1] - 28, 'text-anchor': 'middle', fill: '#f1e9d9', 'font-size': 13, 'pointer-events': 'none' });
    hpLabel.textContent = `${tower.fam} ${Math.max(0, Math.round(tower.hp))}`;
    world.append(hpLabel);
  }
  for (const enemy of markers.enemies) {
    const at = project(matrix, enemy.at);
    const plate = attackerPlate(state.age, enemy.role);
    const height = enemy.boss ? 64 : 40;
    if (!drawPlate(world, element, plate, at[0], at[1] + 6, height, { opacity: enemy.entered ? 1 : 0.45, time: animTime(), clip: 'walk', reduced: state.settings.reducedMotion })) {
      world.append(element('circle', { cx: at[0], cy: at[1], r: enemy.boss ? 14 : 8, fill: '#c83e38', opacity: enemy.entered ? 1 : 0.45 }));
    }
    if (enemy.telegraphId) world.append(element('circle', { cx: at[0], cy: at[1], r: 18, fill: 'none', stroke: '#f1e9d9', 'stroke-width': 2 }));
  }
  for (const shot of markers.projectiles) {
    const at = project(matrix, shot.at);
    if (!drawPlate(world, element, projectilePlate(shot.fam), at[0], at[1] + 6, 18, { time: animTime(), clip: 'attack', reduced: state.settings.reducedMotion })) {
      world.append(element('circle', { cx: at[0], cy: at[1], r: 3, fill: '#f1e9d9' }));
    }
  }
  if (markers.army) {
    const at = project(matrix, markers.army.at);
    const stack = state.army.find(item => item.id === markers.army.stackId);
    if (!drawPlate(world, element, plateForStack(stack), at[0], at[1] + 8, 48, { time: animTime(), clip: 'walk', reduced: state.settings.reducedMotion })) {
      world.append(element('polygon', { points: `${at[0]},${at[1] - 14} ${at[0] + 12},${at[1] + 10} ${at[0] - 12},${at[1] + 10}`, fill: '#9bb7d0' }));
    }
  }
  if (markers.hero) {
    const at = project(matrix, markers.hero.at);
    const heroFigure = { x: at[0], y: at[1] + 8, clip: 'attack', time: animTime(), reduced: state.settings.reducedMotion };
    if (!drawActor(world, element, state.hero.class, { ...heroFigure, scale: 0.12 }) && !drawBoundActor(world, element, state.hero.class, { ...heroFigure, scale: 0.28 })) {
      drawSchematic(world, element, at[0], at[1] + 8, { scale: 0.35, clip: 'attack', time: animTime(), reduced: state.settings.reducedMotion });
    }
  }
  if (worldOnly) return;
  const phaseName = !session ? 'Preparation' : session.pendingSettlement ? (session.winner === 'p' ? 'Victory pending' : 'Defeat pending') : session.paused ? 'Paused' : 'Running';
  $('selected').textContent = session ? `${phaseName} · ${session.practice} · core ${Math.max(0, Math.round(session.core))}` : 'Defense preparation';
  if (session?.status === 'ACTIVE') {
    $('choices').append(button(session.paused ? 'Resume' : 'Pause', () => act('DEFENSE', { paused: !session.paused, dt: 0 }), false, 'defense-pause', true));
    $('choices').append(button(session.speed === 2 ? 'Speed 1x' : 'Speed 2x', () => act('DEFENSE', { speed: session.speed === 2 ? 1 : 2, dt: 0 }), false, 'defense-speed', true));
    $('choices').append(button(session.heroDeployed ? 'Deploy hero — already on the field' : 'Deploy hero', () => act('DEPLOY_DEFENSE', {}), session.heroDeployed, 'deploy-hero', true));
    for (const stack of state.army) {
      $('choices').append(button((session.armyDeployed ? 'Deployed — ' : 'Deploy ') + stackTitle(stack, data), () => act('DEPLOY_ARMY', { stackId: stack.id }), session.armyDeployed, `deploy-army:${stack.id}`, true));
    }
    if (session.practice === 'siege') {
      const wave = session.clearedWaves - 1;
      const ready = wave >= 0 && !session.earlyCalls.includes(wave);
      $('choices').append(button(ready ? `Early call wave ${wave + 1}` : 'Early call — clear a wave first', () => act('EARLY_CALL', {}), !ready, 'early-call'));
    }
  }
  if (session?.pendingSettlement) $('choices').append(button('Apply the defense result', () => act('SETTLE_DEFENSE', {}), false, 'settle-defense', true));
  if (!session) {
    $('choices').append(button('Start campaign siege', () => { act('START_SIEGE', {}); if (state.defense) render(); }, Boolean(state.battle), 'start-siege', true));
    const room = state.towers.length < 2 + levelOf('workshop');
    for (const family of Object.keys(data.TOWERS)) {
      const owned = state.towers.some(tower => tower.fam === family);
      const payment = towerPurchaseCost(data, family, state.age);
      const price = Object.entries(payment).map(([key, amount]) => amount + ' ' + key).join(', ');
      const short = Object.entries(payment).filter(([key, amount]) => state.resources[key] < amount).map(([key, amount]) => `${Math.ceil(amount - state.resources[key])} ${key}`);
      const reason = owned ? 'That family is already built.' : !room ? 'Siege Workshop level adds a tower slot.' : short.length ? `Need ${short.join(', ')}.` : '';
      $('choices').append(button(`Buy ${data.TOWERS[family].n} — ${price}${reason ? ' — ' + reason : ''}`, () => act('BUY_TOWER', { family }), owned || !room || short.length > 0, `buy-tower:${family}`, family === 'splash'));
    }
  }
  const upcoming = markers.queue.slice(0, 6).map(enemy => `${enemy.role}${enemy.boss ? ' boss' : ''}`).join(', ');
  const towerLine = markers.towers.map(tower => `${tower.fam} ${Math.max(0, Math.round(tower.hp))}`).join(', ');
  let guidance = 'Preparation. The starter towers already cover the lane. Archers and sappers cut them down if you send the lane out alone. Build a Siege Workshop, buy a Rock Chucker, then deploy the hero and one stack. An unprepared defense can fall, and that result still settles once.';
  if (session?.pendingSettlement) guidance = session.winner === 'p' ? 'The lane held. Apply the result. The reward is paid once.' : 'The core fell. Apply the result. Losses are recorded once.';
  else if (session?.paused) guidance = 'Paused. Resume continues this same wave. Nothing is caught up while paused.';
  else if (session) guidance = `Running. Cleared ${session.clearedWaves} of ${session.waves}. Core ${Math.max(0, Math.round(session.core))}. Towers ${towerLine}. ${session.heroDeployed ? 'Hero is deployed.' : 'Deploy the hero.'} ${session.armyDeployed ? 'A stack is deployed.' : 'Deploy one stack.'}`;
  const preview = upcoming ? ` Next ${upcoming}.` : '';
  say(guidance + preview);
}

function story() {
  clearWorld();
  $('selected').textContent = state.story.rival ?? 'Choose a rival';
  if (!state.story.rival) for (const name of RIVALS) $('choices').append(button(name, () => act('CHOOSE_RIVAL', { name })));
  const chapter = data.STORY[state.story.chapter];
  const chapterOpen = Boolean(chapter) && state.age >= state.story.chapter;
  if (chapterOpen) {
    for (const [index, choice] of chapter.ch.entries()) $('choices').append(button(choice.t, () => act('STORY_CHOICE', { index })));
  } else if (state.age >= 7 && state.story.chapter >= data.STORY.length && !state.story.futureSeen) $('choices').append(button('Keep the valley', () => act('ACK_FUTURE', {})));
  for (const template of data.QUEST_TEMPLATES) {
    const claimed = state.quests[template.id].claimed;
    const ready = questReady(state, data, template.id);
    $('choices').append(button((claimed ? 'Claimed: ' : ready ? 'Claim: ' : 'Open: ') + template.n, () => act('CLAIM_QUEST', { id: template.id }), claimed || !ready));
  }
  for (let age = 0; age <= 7; age++) {
    const claimed = Boolean(state.story.milestones[age]);
    $('choices').append(button((claimed ? 'Recorded: ' : 'Record milestone: ') + data.AGES[age].n, () => act('CLAIM_MILESTONE', { age }), claimed || state.age < age));
  }
  const logs = state.story.choices.map((flag, index) => data.STORY[index]?.ch.find(choice => choice.flag === flag)?.log).filter(Boolean);
  const waiting = chapter && !chapterOpen ? `${chapter.t} opens in ${data.AGES[state.story.chapter].n}. ` : '';
  const body = chapterOpen ? chapter.t + '. ' + chapter.d : state.age >= 7 && state.story.chapter >= data.STORY.length ? futureConclusion(state, data) : waiting + 'Each chapter opens with its age and pays once. The Valley We Keep opens in the Future age and grants nothing.';
  say(body + (logs.length ? ' Saved record: ' + logs.join(' ') : '') + ' Choices, the rival and claims stay in the save. ' + blocked.loot);
}

function draftDescriptor() {
  const parsed = parseChallenge(challengeDraft.seed, challengeDraft.code);
  if (parsed.error) return parsed;
  try { return { descriptor: challengeDescriptor(parsed.seed, parsed.code) }; }
  catch (error) { return { error: error.message }; }
}
function war() {
  clearWorld();
  $('selected').textContent = 'War';
  $('choices').append(button('Skirmish', () => { act('START_SKIRMISH', {}); if (state.battle) { view = 'tactical'; render(); } }));
  $('choices').append(button('Campaign Siege', () => { act('START_SIEGE', {}); if (state.defense) { view = 'defense'; render(); } }, false, 'start-siege', true));
  $('choices').append(button('Tactical Duel', () => { act('START_DUEL', {}); if (state.battle) { view = 'tactical'; render(); } }));
  $('choices').append(button('Endless', () => { act('START_ENDLESS', {}); if (state.defense) { view = 'defense'; render(); } }, false, 'start-endless', true));
  const seedInput = document.createElement('input');
  seedInput.type = 'text';
  seedInput.inputMode = 'numeric';
  seedInput.setAttribute('aria-label', 'Challenge seed');
  seedInput.dataset.choice = 'challenge-seed';
  seedInput.value = challengeDraft.seed;
  seedInput.addEventListener('input', () => { challengeDraft.seed = seedInput.value; challengeDraft.error = ''; });
  const codeInput = document.createElement('input');
  codeInput.type = 'text';
  codeInput.maxLength = 64;
  codeInput.setAttribute('aria-label', 'Challenge label');
  codeInput.dataset.choice = 'challenge-code';
  codeInput.value = challengeDraft.code;
  codeInput.addEventListener('input', () => { challengeDraft.code = codeInput.value; challengeDraft.error = ''; });
  $('choices').append(seedInput, codeInput);
  $('choices').append(button('Start challenge', () => {
    const parsed = draftDescriptor();
    if (parsed.error) { challengeDraft.error = parsed.error; render(); return; }
    const before = { gold: state.resources.gold, xp: state.hero.xp, age: state.age, items: state.inventory.length };
    act('START_CHALLENGE', { schema: 1, scenarioId: 'duel-v1', seed: parsed.descriptor.seed, label: parsed.descriptor.label, code: parsed.descriptor.label });
    if (state.resources.gold !== before.gold || state.hero.xp !== before.xp || state.age !== before.age || state.inventory.length !== before.items) {
      say('Challenge must not change campaign gold, experience, age or items.');
      return;
    }
    if (state.battle) { view = 'tactical'; render(); }
  }, false, 'challenge-start'));
  $('choices').append(button('Export challenge file', () => {
    const parsed = draftDescriptor();
    if (parsed.error) { challengeDraft.error = parsed.error; render(); return; }
    download('aod-challenge.json', JSON.stringify(parsed.descriptor));
  }, false, 'challenge-export'));
  $('choices').append(button('Copy challenge code', () => {
    const parsed = draftDescriptor();
    if (parsed.error) { challengeDraft.error = parsed.error; render(); return; }
    challengeDraft.copy = encodeChallengeCode(parsed.descriptor);
    challengeDraft.error = '';
    say('Local code: ' + challengeDraft.copy);
  }, false, 'challenge-copy'));
  $('choices').append(button('Import challenge file', () => $('challenge-file').click(), false, 'challenge-import'));
  if (state.battle?.practice === 'challenge' && state.battle.status === 'RESOLVED') {
    $('choices').append(button('Export challenge result', () => {
      const record = challengeResult(state.battle, state.battle.challenge);
      download('aod-challenge-result.json', JSON.stringify(record));
    }, false, 'challenge-result'));
  }
  if (challengeDraft.error) say(challengeDraft.error);
  else say('duel-v1 uses the fixed legal stacks. The label does not change the roster, map or rewards. Skirmish and Challenge do not pay campaign gold.');
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
  say(`Music ${state.settings.music}, sound ${state.settings.sfx}. Local music is a generated motif on its own bus; the click is only the sound bus. Haptics are unavailable. No account or network setting is present.`);
}

function resumeDestination() {
  if (state?.battle) return state.battle.kind === 'defense' ? 'defense' : 'tactical';
  const name = rememberedView(localStorage, screens);
  return name === 'home' ? 'kingdom' : name;
}
function home() {
  clearWorld();
  const world = $('world');
  world.append(element('rect', { width: 1376, height: 768, fill: '#1b2822' }));
  const accepted = state ? portraitCard(state.hero.class, state.age) : portraitCard('mage', 0);
  const pending = state ? pendingPortrait(state.hero.class, state.age) : null;
  const card = accepted || pending;
  paintCard(world, card, !state ? 'title-card' : accepted ? 'portrait-card' : 'pending-card');
  const title = element('text', { x: 660, y: 88, fill: '#f1e9d9', 'font-size': 32 });
  title.textContent = 'Ages of Dominion';
  world.append(title);
  $('selected').textContent = 'Ages of Dominion';
  if (initial.backup) $('choices').append(button('Restore valid backup', () => {
    try {
      const next = restoreBackup(localStorage, data);
      state = next;
      view = 'kingdom';
      saveFault = '';
      installLifecycle();
      render();
      say('Restored the last valid backup. Damaged bytes stay stored.');
    } catch (error) { saveFault = error.message; render(); }
  }));
  if (state) $('choices').append(button('Export campaign', () => download('aod-campaign.json', encode(state, data))));
  $('choices').append(button('Import campaign', () => $('import-file').click()));
  if (state) {
    for (let index = 1; index <= 3; index++) {
      $('choices').append(button('Save slot ' + index, () => { try { storeSlot(localStorage, index, state, data); say('Slot ' + index + ' stored.'); } catch (error) { say(error.message); } }));
      $('choices').append(button('Load slot ' + index, () => {
        try {
          const next = loadSlot(localStorage, index, data);
          if (!next) { say('Slot ' + index + ' is empty.'); return; }
          replaceLive(next, 'kingdom', 'Slot ' + index + ' loaded.');
        } catch (error) { saveFault = error.message; render(); }
      }));
    }
  }
  if (initial.status === 'DAMAGED' && localStorage.getItem(SAVE_KEY) != null) $('choices').append(button('Export damaged save', () => {
    const blob = new Blob([localStorage.getItem(SAVE_KEY)], { type: 'application/json' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob); link.download = 'aod-damaged-save.json'; link.click(); URL.revokeObjectURL(link.href);
  }));
  if (state) $('choices').append(button('Continue', () => { view = resumeDestination(); render(); }, false, 'continue', true));
  $('choices').append(button('New campaign', () => {
    if (state && !confirm('Replace the current campaign on this device?')) return;
    replaceLive(newCampaign(contract, data, Date.now()), 'hero', 'Choose a class, then enter the valley.');
  }, false, 'new-campaign', true));
  if (saveFault) say(saveFault);
  else if (!state && initial.status === 'DAMAGED') say(initial.error + ' Damaged bytes stay stored. Import a valid local campaign, restore a backup, or start a new one.');
  else if (!state) say('Ages of Dominion. No campaign is stored on this device. Start a new one and choose a class, or import a local file.');
}

function help() {
  clearWorld();
  $('selected').textContent = 'Help, credits and privacy';
  say('Help: use Kingdom to build, Adventure to travel, Tactical and Defense for battles, and Story for the seven chapters, quests and age records. The Future conclusion is The Valley We Keep and grants nothing by itself. Credits: Ages of Dominion Reborn is an offline local campaign. Privacy: there is no account, no network request and no device permission. Saves, slots and exports stay on this device.');
}
function download(name, text) {
  const blob = new Blob([text], { type: 'application/json' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob); link.download = name; link.click(); URL.revokeObjectURL(link.href);
  say('Export downloaded. It is a local file, not an upload.');
}
const draw = { home, kingdom, adventure, hero, army, forge, market, tactical, defense, story, war, settings, help };

function setPanel(open) {
  $('panel').classList.toggle('open', open);
  $('context').setAttribute('aria-expanded', String(open));
}
function render() {
  const panel = $('panel');
  const scroll = panel.scrollTop;
  const focusId = document.activeElement?.dataset?.choice || '';
  resources();
  $('choices').replaceChildren();
  $('dock').replaceChildren();
  clearWorld();
  const nav = $('nav');
  const shown = new Set(primaryNav);
  if (state?.battle) shown.add('tactical');
  if (state?.defense || view === 'defense') shown.add('defense');
  if (state?.inventory?.length) shown.add('forge');
  if (view !== 'home') shown.add(view);
  let navNodes = [...nav.children];
  const expected = [...screens.map(name => `nav:${name}`), 'nav-more'];
  if (navNodes.length !== expected.length || navNodes.some((node, index) => node.dataset.choice !== expected[index])) {
    nav.replaceChildren();
    navNodes = screens.map(name => {
      const node = button(name[0].toUpperCase() + name.slice(1), () => { view = name; render(); }, false, `nav:${name}`);
      nav.append(node);
      return node;
    });
    nav.append(button(moreOpen ? 'Fewer' : 'More', () => { moreOpen = !moreOpen; render(); }, false, 'nav-more'));
    navNodes = [...nav.children];
  }
  nav.classList.toggle('expanded', moreOpen);
  navNodes.forEach((node, index) => {
    if (index < screens.length) {
      const name = screens[index];
      if (shown.has(name)) delete node.dataset.nav;
      else node.dataset.nav = 'more';
      if (name === view) node.setAttribute('aria-current', 'true');
      else node.removeAttribute('aria-current');
    } else node.textContent = moreOpen ? 'Fewer' : 'More';
  });
  if (!state && view !== 'home') view = 'home';
  if (state && view !== 'home') rememberView(localStorage, view, screens);
  measureFrame();
  $('status').textContent = saveFault ? 'Save failed' : state ? `${data.AGES[state.age].n} · day ${state.day}` : initial.status === 'DAMAGED' ? 'Damaged save' : initial.status === 'EMPTY' ? 'No campaign stored' : 'No campaign';
  draw[view]();
  if (saveFault && view !== 'home') say(saveFault);
  if (state && view !== 'home') {
    $('choices').append(button(state.tutorial.skipped ? 'Review tutorial' : 'Skip tutorial', () => act(state.tutorial.skipped ? 'TUTORIAL_REVIEW' : 'TUTORIAL_SKIP', {})));
    const mark = tutorialChoice[state.tutorial.step];
    if (mark && !state.tutorial.skipped) {
      const nodes = [...$('choices').querySelectorAll('[data-choice]'), ...$('dock').querySelectorAll('[data-choice]')];
      for (const node of nodes) {
        if (node.dataset.choice === mark || node.dataset.choice.endsWith(':' + mark) || node.dataset.choice.startsWith(mark)) node.dataset.anchor = 'tutorial';
      }
    }
  }
  fitScene();
  panel.scrollTop = scroll;
  if (focusId) {
    const escaped = CSS.escape(focusId);
    (panel.querySelector(`[data-choice="${escaped}"]`) || $('dock').querySelector(`[data-choice="${escaped}"]`))?.focus();
  }
  const resume = $('resume');
  if (resumeNote && view !== 'home') {
    resume.hidden = false;
    resume.textContent = resumeNote + ' Dismissing this report does not credit the clock again.';
    button('Dismiss report', () => { resumeNote = ''; render(); }, false, 'dismiss-resume', true);
  } else {
    resume.hidden = true;
    resume.textContent = '';
  }
}

function paintLiveWorld() {
  if (!state || armed || worldOnly) return;
  if (!['hero', 'army', 'adventure', 'tactical', 'defense', 'kingdom'].includes(view)) return;
  worldOnly = true;
  try {
    $('world').replaceChildren();
    if (view === 'hero') paintHero();
    else if (view === 'army') paintArmy();
    else draw[view]();
  } finally { worldOnly = false; }
}
function installLifecycle() {
  if (!frameClock) {
    frameClock = createFrameClock({
      paused: () => suspended || document.hidden || Boolean(state?.settings?.reducedMotion),
      onFrame: sample => {
        motionTime = sample.render;
        if (!sample.paused) paintLiveWorld();
      },
    });
    frameClock.start();
  }
  if (timer) return;
  timer = setInterval(() => {
    if (!state || suspended) return;
    const now = Date.now();
    state = advanceReported(state, now, data).state;
    if (view === 'defense' && state.defense?.status === 'ACTIVE' && !state.defense.paused) {
      try { state = command(state, { id: crypto.randomUUID(), type: 'DEFENSE', payload: { dt: 0.25, speed: state.defense.speed } }, now, data); } catch { /* A rejected step does not invent a later attack. */ }
    }
    if (!armed && (view === 'kingdom' || view === 'adventure' || view === 'defense')) render();
  }, 250);
}
$('save').onclick = () => { if (state) persist(); };
$('context').onclick = () => { setPanel(!$('panel').classList.contains('open')); render(); };
document.addEventListener('pointerup', event => {
  if (!armed) return;
  const released = event.target?.closest?.('button')?.dataset?.choice || '';
  const chosen = armed;
  armed = null;
  window.rebornChoice = { armed: chosen.id, released, applied: armedChoice(chosen.id, released) };
  if (chosen.id && released && chosen.id !== released) {
    suppressClick = true;
    chosen.fn();
  }
});
document.addEventListener('click', event => {
  if (!suppressClick) return;
  suppressClick = false;
  event.stopPropagation();
  event.preventDefault();
}, true);
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
  if (hit) { selected = hit.id; render(); }
});
function applyBackground(event, hidden) {
  const next = nextSuspended(suspended, event, hidden);
  if (next === suspended) return;
  suspended = next;
  if (next) { suspendAudio(); if (state) { catchUp(Date.now(), false); persist(); } }
  else { resumeAudio(); if (state) catchUp(Date.now(), true); render(); }
}
window.rebornBackground = hidden => applyBackground('visibility', hidden);
window.addEventListener('blur', () => applyBackground('blur', true));
document.addEventListener('visibilitychange', () => applyBackground('visibility', document.hidden));
window.addEventListener('focus', () => applyBackground('focus', document.hidden));
window.addEventListener('pagehide', () => applyBackground('pagehide', true));
window.addEventListener('resize', render);
if (state) { catchUp(Date.now(), true); persist(); installLifecycle(); }
if (initial.status === 'DAMAGED') view = 'home';
render();
$('challenge-file').addEventListener('change', event => {
  const file = event.target.files?.[0];
  event.target.value = '';
  if (!file) return;
  file.text().then(text => {
    if (text.length > 4096) { challengeDraft.error = 'Challenge file is too large.'; render(); return; }
    let parsed;
    try { parsed = JSON.parse(text); }
    catch { challengeDraft.error = 'Challenge file is not JSON.'; render(); return; }
    const described = parsed && (parsed.schema != null || parsed.scenarioId || parsed.label)
      ? validateDescriptor({ schema: parsed.schema, scenarioId: parsed.scenarioId, seed: parsed.seed, label: parsed.label ?? parsed.code })
      : null;
    const next = described || parseChallenge(parsed?.seed, parsed?.code);
    if (next.error) { challengeDraft.error = next.error; render(); return; }
    const descriptor = next.descriptor || challengeDescriptor(next.seed, next.code);
    challengeDraft = { seed: String(descriptor.seed), code: descriptor.label, error: '', copy: '' };
    view = 'war';
    render();
    say('Challenge file loaded. Start runs this seed and code locally.');
  });
});
$('import-file').addEventListener('change', event => {
  const file = event.target.files?.[0];
  event.target.value = '';
  if (!file) return;
  file.text().then(text => {
    let next;
    try { next = decode(text, data); }
    catch (error) { saveFault = error.message; render(); return; }
    replaceLive(next, 'kingdom', 'Imported campaign loaded.');
  });
});
window.rebornSnapshot = () => state ? JSON.parse(JSON.parse(encode(state, data)).payload) : null;
