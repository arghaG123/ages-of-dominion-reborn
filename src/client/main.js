import data from '../data/reference-data.json' with { type: 'json' };
import contract from '../data/implementation-contract.json' with { type: 'json' };
import selection from '../data/reviewed-source-selection.json' with { type: 'json' };
import scene from '../data/stone-scene.json' with { type: 'json' };
import modeScenes from '../data/mode-scenes.json' with { type: 'json' };
import adventureWorlds from '../data/adventure-worlds.json' with { type: 'json' };
import ageBuildings from '../data/age-buildings.json' with { type: 'json' };
import gearIcons from '../data/gear-icons-20261007.json' with { type: 'json' };
import consumerCatalog from '../data/consumer-catalog-20261007.json' with { type: 'json' };
import { SITE_TITLES, discoveredSite, adventureMinimap, visibleAdventureAnchors, adventureTravelerMode, adventureAnchorLabelOverlapsTraveler, availableDwellingTypes, rosterSelection, canConfirmRoute, settlementStarted, shouldShowResumeNote, tutorialCueText, tutorialAnchorChoice, labelPositions, heroSkillStateCopy, defenseSummary, damagedSaveRecoveryCopy } from './screen-presentation.js';
import { kingdomPainting, plotPresentation, tutorialBuildSiteId, wallHostAttrs } from './kingdom-view.js';
import { plotProduction, constructionDurationMs, formatConstructionDuration } from './kingdom-production.js';
import { resourceChipLabel } from './resource-bar.js';
import { campaignMapImage, isIntegratedAdventureMap } from './adventure-map-source.js';
import { dwellingRecruitLabel, travelCommitAction } from './adventure-travel-presentation.js';
import { crossingPresentation, routeWithCurrentCell, shouldAutoCloseCrossingPanel } from './adventure-crossing-presentation.js';
import { defenseWaveLabel } from './defense-wave-presentation.js';

import { newCampaign, command, advanceReported, advanceActiveDefense, formatResume, cost, rates, heroStats, manaMax, dailyMoves, gateHp, questReady, stackTitle } from '../core/campaign.js';
import { activeStackId, legalDeploymentCells, legalTargets, meleeCommand } from '../core/battle.js';
import { SAVE_KEY, encode, decode, IndexedDBStorageAdapter } from '../core/save.js';
import { SaveQueue } from '../core/save-queue.js';
import { saveButtonFeedback } from './save-feedback.js';
import { camera, coverCamera, inverse, project, kingdomFocusBounds, targetSourceSize, wideBoardCamera, worldViewportWidth } from './projection.js';
import { defenseMarkers, defensePreparationMarkers } from '../core/defense.js';
import { attackerPlate, beginActorFrame, creaturePlate, drawActor, drawMount, drawPlate, drawReviewMount, drawStaticMount, plateForStack, projectilePlate, setWorldCssScale, staticMountForAge, towerPlate, troopPlate } from './actor.js';
import { drawBoundActor } from './anatomy.js';
import { pendingPortrait, portraitCard } from './portraits.js';
import { armyRankStars, armyRosterCapacity, heroFocus, heroStage, KINGDOM_PAD_PRESENTATION } from './presentation.js';
import { drawHeroRoom, heroBody, kitEra, selectGearIcon, wornWeaponArt, forgeWeaponPreviewArt, forgeWeaponPreviewPose } from './hero-room.js';
import { storyHeaderTitle, storyScreen, storyChamberLine } from './story-view.js';
import { armedChoice, parseChallenge } from './choices.js';
import { acceptMapActivation, battleSpellAvailability, defaultIntent, intentSentence, keepIntent, modeRows, moveLabel, primaryModeRows, retreatBlocksBackground, retreatFocusTarget, retreatNotice, secondaryModeRows, spellLabel, stackCaption, strikeLabel, tacticalHeroPlaqueCopy, viewDuringRetreat } from './tactical-ui.js';
import { footAwareVisibleBox, visibleBox } from './visible-size.js';
import { createFrameClock, travelProgress, travelSample } from './motion.js';
import { activeCommittedFeedback, committedBattleEvents, motionFor } from './committed-motion.js';
import { applySettings, arm, blip, nextSuspended, suspendAudio, resumeAudio } from './audio.js';
import { SKILL_IDS, GEAR_SLOTS, RIVALS, agePrice, forgeOffer, gearBonus, marketQuote, recruitCost, spellEffect, towerPurchaseCost } from '../core/rules.js';
import { dwellingCost, dwellingPool, unitStats } from '../core/mechanics.js';
import { adventureGeometryForWorld, adventureMap, isOpen, routeTo } from '../core/navigation.js';
import { challengeDescriptor, validateDescriptor, encodeChallengeCode, decodeChallengeCode, challengeResult } from '../core/challenge.js';

const $ = id => document.getElementById(id);
const svgNS = 'http://www.w3.org/2000/svg';
const ages = ['stone', 'bronze', 'iron', 'medieval', 'gunpowder', 'industrial', 'modern', 'future'];
const screens = ['home', 'kingdom', 'adventure', 'hero', 'army', 'forge', 'market', 'tactical', 'defense', 'story', 'war', 'settings', 'help'];
const RESUMABLE_SCREENS = new Set(screens.filter(name => !['home', 'settings', 'help'].includes(name)));
const isResumableView = name => RESUMABLE_SCREENS.has(name);
const blocked = {
  tactical: 'Choose a move, a spell, or wait.',
  defense: 'Hold the lane. Pause stops the attack.',
  war: 'Skirmish and Challenge do not pay campaign gold. Siege and Duel settle campaign rewards once.',
  skills: 'A skill offer waits until you choose or decline it.',
  loot: 'Offers stay with this save.'
};
const primaryNav = ['kingdom', 'adventure', 'hero', 'army', 'war'];
const menuDestinations = [['forge', 'Forge'], ['market', 'Market'], ['story', 'Story'], ['settings', 'Settings'], ['help', 'Help'], ['home', 'Campaign & saves']];
const TITLE_BACKDROP = 'assets/production/production-11-20261003/images/30-supporting-title.png';
const CHAPTER_BACKDROPS = [
  'assets/production/production-12-20261003/images/01-supporting-chapter-1.png',
  'assets/production/production-12-20261003/images/02-supporting-chapter-2.png',
  'assets/production/production-12-20261003/images/03-supporting-chapter-3.png',
  'assets/derivatives/visual-repair-20261020/scenes/story-chapter-4-divided-gate-v2.png',
  'assets/production/production-12-20261003/images/05-supporting-chapter-5.png',
  'assets/production/production-12-20261003/images/06-supporting-chapter-6.png',
  'assets/production/production-12-20261003/images/07-supporting-chapter-7.png',
  'assets/production/production-12-20261003/images/08-supporting-chapter-8.png',
];
const CHAMBER_BACKDROPS = {
  forge: 'assets/derivatives/mock-led-20261016/chambers/chamber-forge.png',
  armory: 'assets/derivatives/mock-led-20261016/chambers/chamber-armory.png',
  garrison: 'assets/derivatives/mock-led-20261016/chambers/chamber-garrison.png',
  market: 'assets/derivatives/mock-led-20261016/chambers/chamber-market.png',
};
const ARMY_BACKDROPS = {
  0: 'assets/derivatives/professional-20261018/army/army-stone-muster-v1.png',
  1: 'assets/derivatives/professional-20261018/army/army-bronze-muster-v1.png',
  2: 'assets/derivatives/professional-20261018/army/army-iron-muster-v1.png',
  3: 'assets/derivatives/professional-20261018/army/army-medieval-muster-v1.png',
  4: 'assets/derivatives/professional-20261018/army/army-gunpowder-muster-v1.png',
  5: 'assets/derivatives/professional-20261018/army/army-industrial-muster-v1.png',
  6: 'assets/derivatives/professional-20261018/army/army-modern-muster-v1.png',
  7: 'assets/derivatives/professional-20261018/army/army-future-muster-v1.png',
};
const ADVENTURE_SITE_ART = {
  town: 'assets/derivatives/adventure-world-objects-generated-20261020/sites/fortified-town-rock-island-v1.png',
  ruin: 'assets/derivatives/environment-20261006/sites/adventure-site-ruin.png',
  mill: 'assets/derivatives/environment-20261006/sites/adventure-site-mill.png',
  mine: 'assets/derivatives/environment-20261006/sites/adventure-site-mine.png',
  dwelling: 'assets/derivatives/environment-20261006/sites/adventure-site-dwelling.png',
  shrine: 'assets/derivatives/environment-20261006/sites/adventure-site-shrine.png',
};
const ADVENTURE_RESOURCE_ART = {
  food: 'assets/derivatives/adventure-world-objects-generated-20261020/resources/food-cache-v1.png',
  wood: 'assets/derivatives/adventure-world-objects-generated-20261020/resources/wood-cache-v1.png',
  stone: 'assets/derivatives/adventure-world-objects-generated-20261020/resources/stone-cache-v1.png',
  gold: 'assets/derivatives/adventure-world-objects-generated-20261020/resources/gold-cache-v1.png',
};
const ADVENTURE_GUARD_ART = {
  'guard-ruin': 'assets/derivatives/adventure-world-objects-generated-20261020/enemies/bandit-patrol-v1.png',
  'guard-mine': 'assets/derivatives/adventure-world-objects-generated-20261020/enemies/wild-pack-v1.png',
};
const ACTION_ART = {
  melee: 'assets/delivery/stone-starter-20261003/derivatives/v4-ui/skill-offense.png',
  shoot: 'assets/derivatives/image-residual-executor-20261007/environment/icons/skills/skill-archery.png',
  defend: 'assets/derivatives/image-residual-executor-20261007/environment/icons/skills/skill-armorer.png',
  spell: 'assets/derivatives/image-residual-executor-20261007/environment/icons/spells/spell-bolt.png',
};
const RIVAL_PORTRAITS = {
  'Varek Iron-Eye': 'assets/derivatives/portraits/rival-varek-iron-eye.png',
  'Soren the Unforgiving': 'assets/derivatives/portraits/rival-soren-the-unforgiving.png',
  'Malakor the Flayed': 'assets/derivatives/portraits/rival-malakor-the-flayed.png',
  'Bran the Relentless': 'assets/derivatives/portraits/rival-bran-the-relentless.png',
  'Thalric Ash-Bane': 'assets/derivatives/portraits/rival-thalric-ash-bane.png',
  'Karn Blood-Tide': 'assets/derivatives/portraits/rival-karn-blood-tide.png',
};
const navGlyphs = {
  kingdom: 'M3 21 V9 L6 9 V12 H8 V7 L12 3 L16 7 V12 H18 V9 L21 9 V21 H14.5 V15 H9.5 V21 Z',
  adventure: 'M12 2 A10 10 0 1 0 11.99 2 Z M12 4.5 A7.5 7.5 0 1 1 4.5 12 A7.5 7.5 0 0 1 12 4.5 Z M12 6.5 L14.6 10.4 L18.5 12 L14.6 13.6 L12 17.5 L9.4 13.6 L5.5 12 L9.4 10.4 Z',
  hero: 'M12 2.5 L15 6 L19 5 L18 11 C18 15.5 15.5 19.5 12 21.5 C8.5 19.5 6 15.5 6 11 L5 5 L9 6 Z M9.5 11.5 L11.2 13 L11.2 16.5 H12.8 V13 L14.5 11.5 Z',
  army: 'M5 2 H7.5 V22 H5 Z M8.5 3.5 H20 L16 8.5 L20 13.5 H8.5 Z M11 6.5 L14 8.5 L11 10.5 Z',
  war: 'M12 2.5 L19.5 6 V12.5 C19.5 17.2 12 21.5 12 21.5 C12 21.5 4.5 17.2 4.5 12.5 V6 Z M8.5 8 L15.5 15 M15.5 8 L8.5 15',
};
const headerGlyphs = {
  menu: 'M4 5.5 H20 V8 H4 Z M4 10.75 H20 V13.25 H4 Z M4 16 H20 V18.5 H4 Z',
  save: 'M4 3 H17 L21 7 V21 H4 Z M7 3 V10 H16 V3 Z M8 14 V19 H17 V14 Z M12 4 H14 V8 H12 Z',
  back: 'M20 12 H5 M12 5 L5 12 L12 19',
};
const idbAdapter = typeof indexedDB !== 'undefined' ? new IndexedDBStorageAdapter(indexedDB) : null;
let initial;
$('status').textContent = 'Opening saved campaign…';
try {
  if (!idbAdapter) throw new Error('Durable storage is unavailable. Your existing saves are preserved.');
  await idbAdapter.open();
  const existing = await idbAdapter.loadLive(data);
  try {
    await idbAdapter.migrateFromLocalStorage(localStorage, data);
    initial = await idbAdapter.loadLive(data);
  } catch (error) {
    if (!['VALID', 'DAMAGED'].includes(existing.status)) throw error;
    initial = { ...existing, migrationWarning: error.message };
  }
} catch (error) {
  initial = { status: 'UNAVAILABLE', state: null, error: error.message };
}
const saveQueue = new SaveQueue(idbAdapter, data, initial.head ?? null);
const GRAPHICS_QUALITY_KEY = 'aod.reborn.graphics-quality.v1';
const GRAPHICS_QUALITY_VALUES = ['low', 'medium', 'high'];
function readGraphicsQuality() {
  try {
    const value = localStorage.getItem(GRAPHICS_QUALITY_KEY);
    return GRAPHICS_QUALITY_VALUES.includes(value) ? value : 'high';
  } catch { return 'high'; }
}
let graphicsQuality = readGraphicsQuality();
document.documentElement.dataset.graphicsQuality = graphicsQuality;
function setGraphicsQuality(value) {
  if (!GRAPHICS_QUALITY_VALUES.includes(value)) return false;
  graphicsQuality = value;
  document.documentElement.dataset.graphicsQuality = value;
  try { localStorage.setItem(GRAPHICS_QUALITY_KEY, value); } catch { /* The selected preset still applies for this page. */ }
  render();
  return true;
}
let replacementPending = false;
let lastSavedView = isResumableView(initial.view) ? initial.view : 'kingdom';
function freshCampaign(worldId = campaignWorldSelection) {
  const seedBytes = new Uint32Array(1);
  crypto.getRandomValues(seedBytes);
  const seed = seedBytes[0] || 0x9e3779b9;
  const next = newCampaign(contract, data, Date.now(), seed, worldId);
  next.id = `campaign-${crypto.randomUUID()}`;
  return next;
}
let state = initial.state, selected = '', suspended = false, timer, frameClock, resumeNote = '', clip = 'idle', opponentRender = false, saveFault = '';
let campaignWorldSelection = state?.adventureWorldId || adventureWorlds[0].id;
let frameFit = { width: 1, height: 1, fit: { scale: 1, offset: [0, 0] } };
let armed = null;
let suppressClick = false;
let motionTime = 0;
let worldOnly = false;
let valleyEntered = false;
let travelMotion = null;
let travelPreview = null;
let adventurePanelRequested = false;
let forgeSlot = 'weapon';
let forgePreview = null;
let tacticalIntent = null;
let tacticalBattleId = null;
let deploymentSelection = null;
let attackModeMenuOpen = false;
let retreatArmed = false;
let retreatRestorePending = false;
let retreatSettling = false;
let mapArm = null;
let swallowMapClick = false;
let labelQueue = [];
let focusChoice = '';
let plateReviewAge = null;
let selectedArmyId = null;
let selectedRecruitRole = 'melee';
let armyCatalogOpen = false;
let selectedCodexCreature = '';
let armyTutorialDefaultedFor = '';
let selectedHeroSlot = null;
let heroDetailTab = 'skills';
let heroInventorySelectedId = null;
let heroSkillDetailId = 'offense';
let journalTab = 'chronicle';
let storyQuickFocus = '';
let settingsReturnView = 'kingdom';
let menuSheet = false;
let marketEditing = false;
let resourceSheet = false;
let siteChoices = null;
let kingdomBuildSite = '';
let kingdomActionSheet = false;
let battleEvents = [];
let pendingBuild = null;
let buildInvoker = '';
const auditMode = new URLSearchParams(location.search).has('audit');
let challengeDraft = { seed: '123456789', code: 'valley-1', error: '', copy: '' };
let blastAim = false;
let defensePad = '';
let defenseTowerId = null;
let defensePlan = 'siege';
let view = initial.status === 'VALID' && screens.includes(initial.view) ? (initial.view === 'home' || isResumableView(initial.view) ? initial.view : 'home') : initial.status === 'VALID' ? 'kingdom' : 'home';
let lastRenderedView = null;
let lastPanelContentKey = '';

const slotName = { helm: 'Helm', weapon: 'Weapon', offhand: 'Offhand', armor: 'Armor', boots: 'Boots', accessory: 'Accessory' };
const say = text => { $('message').textContent = text; };
const animTime = () => (state?.settings?.reducedMotion ? 0 : motionTime);
const levelOf = type => state.plots.find(plot => plot.type === type)?.level ?? 0;
const kingdomBuildingNames = { 1: { workshop: 'Clay Workshop' }, 4: { workshop: 'Artillery Foundry' } };
const kingdomBuildingName = type => kingdomBuildingNames[state.age]?.[type] || data.BUILDINGS[type].n;
if (initial.status === 'DAMAGED') {
  view = 'home';
  say(initial.error + ' The damaged save is still stored.');
}

function updateSaveFeedback() {
  const status = saveQueue.status;
  saveFault = status.kind === 'pending' ? 'saving' : status.kind === 'failed' ? status.error : '';
  const feedback = saveButtonFeedback(status.kind);
  $('save').dataset.saveState = status.kind;
  $('save').setAttribute('aria-label', feedback.label);
}
function persist() {
  if (!state || replacementPending) return Promise.resolve(false);
  let raw;
  try { raw = encode(state, data); }
  catch (error) { saveFault = error.message; return Promise.resolve(false); }
  const destination = isResumableView(view) ? view : lastSavedView;
  const pending = saveQueue.write(raw, destination);
  updateSaveFeedback();
  return pending.then(ok => {
    lastSavedView = destination;
    updateSaveFeedback();
    return ok;
  }).catch(error => {
    updateSaveFeedback();
    saveFault = error.message;
    if ($('status')) $('status').textContent = 'Save failed';
    if (view !== 'home') say(saveFault);
    return false;
  });
}
async function replaceLive(next, nextView, success) {
  if (replacementPending) return false;
  let raw;
  try { raw = encode(next, data); }
  catch (error) { saveFault = error.message; render(); return false; }
  replacementPending = true;
  const work = saveQueue.write(raw, nextView, true);
  updateSaveFeedback();
  render();
  try {
    await work;
    state = decode(raw, data);
    battleEvents = [];
    initial = { ...initial, status: 'VALID', head: saveQueue.head, state, error: undefined, raw: undefined };
    resumeNote = '';
    view = nextView;
    lastSavedView = nextView;
    replacementPending = false;
    updateSaveFeedback();
    installLifecycle();
    render();
    if (success) say(success);
    return true;
  } catch (error) {
    replacementPending = false;
    updateSaveFeedback();
    saveFault = error.message;
    render();
    say('Replacement failed. The current campaign is retained. ' + error.message);
    return false;
  }
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
  const step = state.tutorial.step;
  const onRoad = Boolean(state.adventure && !state.adventure.atTown);
  const show = (step <= 3 && view === 'kingdom')
    || (step === 4 && view === 'army')
    || (step === 5 && view === 'adventure' && !onRoad)
    || (step === 6 && (view === 'adventure' || view === 'tactical'))
    || (step === 7 && (view === 'war' || view === 'defense' || view === 'kingdom'));
  const buildSiteSelected = Boolean(selected && state.plots?.some(plot => plot.id === selected && plot.level === 0 && plot.type == null));
  const text = tutorialCueText(step, {
    view,
    onRoad,
    pendingEncounter: Boolean(state.adventure?.pendingEncounter && !state.battle),
    buildPickerOpen: Boolean(kingdomBuildSite),
    buildSiteSelected,
  });
  return show ? ' Next: ' + text : '';
}
function act(type, payload) {
  if (replacementPending) return;
  try {
    const before = state;
    const actionId = crypto.randomUUID();
    state = command(state, { id: actionId, type, payload }, Date.now(), data);
    $('notification').hidden = true;
    if (settlementStarted(before, state)) setPanel(false);
    if (type === 'SETTLE_BATTLE') { view = before.adventure?.pendingEncounter?.id === before.battle?.encounterId ? 'adventure' : 'war'; setPanel(false); }
    if (type === 'CANCEL_BATTLE_SETUP') { view = 'war'; setPanel(false); }
    if (type === 'SETTLE_DEFENSE') { view = before.defense?.practice === 'endless' ? 'war' : 'kingdom'; setPanel(false); }
    const events = committedBattleEvents(before?.battle, state?.battle, actionId, motionTime);
    if (!state?.battle || before?.battle?.id !== state?.battle?.id) {
      battleEvents = [];
    } else if (state.settings.reducedMotion) {
      if (type === 'SETTINGS' && !before?.settings?.reducedMotion) battleEvents = [];
      else if (events.length) battleEvents = events;
    } else {
      if (type === 'SETTINGS' && before?.settings?.reducedMotion) battleEvents = [];
      if (events.length) {
        battleEvents = events;
      } else {
        battleEvents = battleEvents.filter(event => event.sessionId === state.battle.id && event.start + event.duration > motionTime);
      }
    }
    window.rebornActions = window.rebornActions || [];
    window.rebornActions.push({ type, action: payload?.action ?? null, to: payload?.to ?? null, targetId: payload?.targetId ?? null });
    applySettings(state.settings);
    persist();
    blip();
    render();
  } catch (error) {
    say(error.message);
    $('notification-text').textContent = error.message;
    $('notification').hidden = false;
  }
}
function element(name, attrs) {
  const node = document.createElementNS(svgNS, name);
  for (const [k, v] of Object.entries(attrs)) node.setAttribute(k, v);
  return node;
}
function queueLabel(text, x, y, details = {}) {
  if (!text) return;
  labelQueue.push({ text, x, y, ...details });
}
function flushLabels() {
  const host = $('labels');
  if (!host) return;
  host.replaceChildren();
  if (frameFit.crossingFocus) { labelQueue = []; return; }
  const fit = frameFit.fit;
  const labelBounds = host.getBoundingClientRect();
  const minimapBounds = view === 'adventure' ? $('adventure-minimap')?.getBoundingClientRect() : null;
  const avoidRects = minimapBounds && minimapBounds.width > 0 && minimapBounds.height > 0
    ? [{ left: minimapBounds.left - labelBounds.left, top: minimapBounds.top - labelBounds.top,
      right: minimapBounds.right - labelBounds.left, bottom: minimapBounds.bottom - labelBounds.top }]
    : [];
  const rows = labelQueue.map((row, index) => {
    const safeBottom = row.safeBottom ?? (view === 'adventure' && frameFit.height > 100 ? frameFit.height - 125 : undefined);
    return {
      ...row,
      key: index,
      x: fit.offset[0] + row.x * fit.scale,
      y: fit.offset[1] + row.y * fit.scale,
      ...(safeBottom == null ? {} : { safeBottom }),
      ...(avoidRects.length ? { avoidRects } : {}),
    };
  });
  const nodes = new Map();
  for (const row of rows) {
    const span = document.createElement('span');
    span.textContent = row.text;
    if (row.side) span.dataset.side = row.side;
    if (row.fullText) span.title = row.fullText;
    if (row.health != null) {
      span.classList.add('unit-label');
      span.style.setProperty('--health', String(row.health));
    }
    host.append(span);
    nodes.set(row.key, span);
  }
  for (const row of labelPositions(rows, frameFit.width, frameFit.height, entry => {
    const rect = nodes.get(entry.key).getBoundingClientRect();
    return { width: rect.width, height: rect.height };
  })) {
    const span = nodes.get(row.key);
    if (!span) continue;
    if (row.visible === false) { span.remove(); continue; }
    span.style.left = `${row.left}px`;
    span.style.top = `${row.top}px`;
  }
}
function stackHealth(stack) {
  const maxCount = stack.maxCount || stack.count || 0;
  const uhp = stack.uhp || 0;
  const now = stack.dead ? 0 : Math.max(0, (stack.count - 1) * uhp + (stack.top || 0));
  return { hp: Math.round(now), maxHp: Math.round(maxCount * uhp) };
}
function confirmRetreat() {
  if (!retreatArmed || retreatSettling || !state?.battle || state.battle.status !== 'ACTIVE') return;
  const battleId = state.battle.id;
  retreatArmed = false;
  retreatSettling = true;
  try {
    act('BATTLE', { action: 'retreat', confirm: true });
    if (state.battle?.id === battleId && state.battle.pendingSettlement && state.battle.outcome?.winner === 'retreat') act('SETTLE_BATTLE', {});
  } finally { retreatSettling = false; }
}
function paintRetreat() {
  const layer = $('retreat');
  const open = Boolean(retreatArmed && view === 'tactical' && state?.battle?.status === 'ACTIVE');
  const field = $('stage-field');
  if (field) field.inert = open;
  for (const id of ['context', 'save']) $(id).inert = open;
  document.querySelector('header').inert = open;
  document.querySelector('footer').inert = open;
  layer.inert = !open;
  if (!open) { layer.hidden = true; return; }
  const notice = retreatNotice(state.battle.practice);
  layer.hidden = false;
  $('retreat-title').textContent = notice.title;
  $('retreat-body').textContent = notice.body;
  $('retreat-cancel').textContent = notice.cancel;
  $('retreat-confirm').textContent = notice.confirm;
  if (focusChoice === 'retreat-cancel') {
    focusChoice = '';
    $('retreat-cancel').focus();
  }
}
function previewBuild(plotId, building, invoker) {
  pendingBuild = { plotId, building };
  buildInvoker = invoker || '';
  armed = null;
  render();
  $('build-cancel').focus();
}
function previewAction(command, payload, title, payment, detail, invoker) {
  pendingBuild = { command, payload, title, payment, detail };
  buildInvoker = invoker;
  armed = null;
  render();
  $('build-cancel').focus();
}
function closeBuild() {
  pendingBuild = null;
  render();
  document.querySelector(`[data-choice="${CSS.escape(buildInvoker)}"]`)?.focus();
}
function paintBuildPreview() {
  const open = Boolean(pendingBuild);
  $('build-confirm').hidden = !open;
  $('build-confirm').inert = !open;
  if (!open) return;
  const plot = pendingBuild.command ? null : pendingBuild.plotId === 'walls' ? state.walls : state.plots.find(p => p.id === pendingBuild.plotId);
  const payment = pendingBuild.payment || cost(data, pendingBuild.building, plot.level);
  $('build-title').textContent = pendingBuild.title || `${plot.level ? 'Upgrade' : 'Build'} ${kingdomBuildingName(pendingBuild.building)}`;
  $('build-price').textContent = Object.entries(payment).map(([key, amount]) => `${amount} ${key}`).join(' · ');
  const buildDetail = pendingBuild.detail || (pendingBuild.plotId === 'walls' ? 'Kingdom boundary' : pendingBuild.plotId) + '. Level ' + plot.level + ' → ' + (plot.level + 1) + '. Resources are spent only when you confirm.';
  const buildTime = pendingBuild.command ? '' : ' Construction time: ' + formatConstructionDuration(constructionDurationMs(pendingBuild.building, plot.level, payment)) + '.';
  $('build-detail').textContent = buildDetail + buildTime;
  $('build-commit').textContent = ({ FORGE: 'Confirm craft', AGE_UP: 'Confirm age advance', MARKET: 'Confirm trade', CHOOSE_SKILL: 'Choose skill' })[pendingBuild.command] || 'Confirm construction';
  $('stage-field').inert = true;
  document.querySelector('header').inert = true;
  document.querySelector('footer').inert = true;
  $('context').inert = true;
  $('save').inert = true;
}
function button(label, onClick, disabled = false, choiceId = '', dock = false) {
  const build = () => {
    const node = document.createElement('button');
    node.type = 'button';
    node.textContent = label;
    node.disabled = disabled;
    if (disabled) node.title = label;
    if (choiceId) node.dataset.choice = choiceId;
    node.addEventListener('pointerdown', event => { armed = { id: choiceId, fn: onClick, x: event.clientX, y: event.clientY, pointerId: event.pointerId, cancelled: false }; });
    node.addEventListener('click', event => {
      const inDialog = Boolean(event.currentTarget.closest('#retreat'));
      if (retreatBlocksBackground({ retreatArmed, inDialog })) {
        event.preventDefault();
        event.stopPropagation();
        armed = null;
        return;
      }
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
  if (dock && !$('panel').classList.contains('open')) $('dock').append(build());
  return node;
}
function resourceIcon(key) {
  const chosen = selection.delivery?.['resource-' + key];
  const file = chosen?.uiFile || chosen?.file;
  if (!file) return null;
  const icon = document.createElement('img');
  icon.src = file;
  icon.alt = '';
  return icon;
}
function costButton(title, payment, onClick, disabled, choiceId = '', dock = false, detail = '', artFile = '') {
  const price = Object.entries(payment).map(([key, amount]) => `${amount} ${key}`).join(', ');
  const accessible = detail ? `${title}. ${price}. ${detail}` : `${title}. ${price}`;
  const make = () => {
    const node = button(title, () => {
      if (disabled) { say(detail || 'This action is unavailable.'); return; }
      onClick();
    }, false, choiceId, false);
    if (disabled) { node.setAttribute('aria-disabled', 'true'); node.setAttribute('aria-describedby', 'message'); }
    node.classList.add('cost-action');
    node.setAttribute('aria-label', accessible);
    if (detail) node.title = detail;
    let label = null;
    if (artFile) {
      label = document.createElement('span');
      label.className = 'cost-label';
      const art = document.createElement('img');
      art.className = 'cost-art';
      art.src = artFile;
      art.alt = '';
      label.append(art);
      const name = document.createElement('span');
      name.className = 'cost-name';
      name.textContent = title;
      label.append(name);
    }
    const costs = document.createElement('span');
    costs.className = 'cost-icons';
    for (const [key, amount] of Object.entries(payment)) {
      const icon = resourceIcon(key);
      if (icon) costs.append(icon);
      const figure = document.createElement('span');
      figure.className = 'cost-amount';
      figure.textContent = String(amount);
      costs.append(figure);
    }
    if (label) node.replaceChildren(label, costs);
    else node.append(costs);
    return node;
  };
  const node = make();
  if (dock && !$('panel').classList.contains('open')) $('dock').append(make());
  return node;
}
function dockIcon(label, detail, mark, onClick, disabled, choiceId) {
  const decorate = node => {
    node.classList.add('icon-medallion');
    node.setAttribute('aria-label', detail ? `${label}. ${detail}` : label);
    node.title = detail || label;
    node.append(glyph(mark));
    return node;
  };
  const panelNode = decorate(button('', onClick, disabled, choiceId));
  if ($('panel').classList.contains('open')) {
    const caption = document.createElement('span');
    caption.className = 'context-action-label';
    caption.textContent = label;
    panelNode.append(caption);
    $('choices').append(panelNode);
    return panelNode;
  }
  const dockNode = decorate(button('', onClick, disabled, choiceId));
  $('dock').append(dockNode);
  return dockNode;
}
function glyph(d) {
  const svg = document.createElementNS(svgNS, 'svg');
  svg.setAttribute('viewBox', '0 0 24 24');
  svg.setAttribute('aria-hidden', 'true');
  svg.classList.add('glyph');
  const path = document.createElementNS(svgNS, 'path');
  path.setAttribute('d', d);
  path.setAttribute('fill', 'currentColor');
  path.setAttribute('fill-rule', 'evenodd');
  svg.append(path);
  return svg;
}
function resources() {
  const show = Boolean(state) && view !== 'home' && view !== 'campaignMapSelect' && view !== 'tactical' && (view !== 'defense' || !state.defense);
  $('resources').hidden = !show;
  if (!show || !state) return;
  for (const k of ['food', 'wood', 'stone', 'gold']) {
    let span = $('resources').querySelector(`[data-resource="${k}"]`);
    if (!span) {
      span = document.createElement('span');
      span.className = 'resource-chip';
      span.dataset.resource = k;
      $('resources').append(span);
    }
    const chosen = selection.delivery?.['resource-' + k];
    const iconFile = chosen?.uiFile || chosen?.file;
    if (iconFile && span.querySelector('img')?.getAttribute('src') !== iconFile) {
      span.querySelector('img')?.remove();
      const icon = document.createElement('img');
      icon.src = iconFile;
      icon.alt = '';
      icon.width = 18;
      icon.height = 18;
      span.append(icon);
    }
    const chip = resourceChipLabel(k[0].toUpperCase() + k.slice(1), state.resources[k]);
    let amount = span.querySelector('.amount');
    if (!amount) {
      amount = document.createElement('span');
      amount.className = 'amount';
      span.append(amount);
    }
    amount.textContent = chip.text;
    span.title = chip.title;
    span.setAttribute('aria-label', chip.accessible);
  }
}
function clearSceneUi() {
  const host = $('scene-ui');
  if (!host) return;
  host.hidden = true;
  host.className = '';
  host.replaceChildren();
}
function clearWorld() {
  const world = $('world');
  world.replaceChildren();
  delete world.dataset.board;
  delete world.dataset.registration;
  delete world.dataset.chamber;
  delete world.dataset.screen;
  delete world.dataset.heroContext;
  delete world.dataset.supportLayout;
  delete world.dataset.campaignWorldPreviewSource;
  world.removeAttribute('pointer-events');
  const stageField = $('stage-field');
  stageField.classList.remove('hero-spellbook-context');
  stageField.style.removeProperty('--spellbook-world-image');
  $('terrain').hidden = true;
  clearSceneUi();
}
function choiceHeading(text) {
  const node = document.createElement('p');
  node.className = 'choice-heading';
  node.textContent = text;
  $('choices').append(node);
}
function showTerrain(file, alt, status) {
  const terrain = $('terrain');
  terrain.hidden = false;
  if (file && terrain.getAttribute('src') !== file) terrain.src = file;
  terrain.alt = alt;
  terrain.dataset.terrainStatus = status;
}
function modeGround(mode) {
  const age = state?.age ?? 0;
  const campaignWorld = mode === 'adventure'
    ? adventureWorlds.find(world => world.id === state?.adventureWorldId)
    : null;
  const file = campaignMapImage(campaignWorld) || modeScenes[mode]?.[age];
  const biome = modeScenes.modeBiomes?.[mode]?.[age] || modeScenes.biomes?.[age] || 'forest';
  if (file) showTerrain(file, campaignWorld
    ? `${campaignWorld.title} campaign world map`
    : `${data.AGES[age].n} ${biome} ${mode} ground`, campaignMapImage(campaignWorld) ? 'generated-game-specific-world-map-v4' : modeScenes.status);
  return file;
}
function adventureGeometryForCampaign() {
  const world = adventureWorlds.find(entry => entry.id === state?.adventureWorldId);
  return adventureGeometryForWorld(contract.geometry.adventure, world, state?.seed);
}
function adventureInteractionFocus() {
  const adventure = state?.adventure;
  if (!adventure || adventure.atTown) return '';
  const site = adventureGeometryForCampaign().sites.find(entry => entry.id !== 'town'
    && entry.approach[0] === adventure.x && entry.approach[1] === adventure.y);
  if (!site) return '';
  if (['ruin', 'mill', 'mine'].includes(site.id)) {
    return adventure.claimedSites?.includes(site.id) ? '' : `claim-site:${site.id}`;
  }
  if (site.id === 'shrine' && !adventure.claimedSites?.includes('shrine')) {
    const offer = state.hero.offers.find(item => item.source === 'adventure-shrine' && !item.chosen && !item.declined);
    if (offer) return `shrine-skill:${offer.choices[0]}`;
    const activeOffer = state.hero.offers.some(item => !item.chosen && !item.declined);
    return !activeOffer && !SKILL_IDS.every(id => state.hero.skills[id] >= 3) ? 'study-skill-monument' : '';
  }
  return '';
}

function supportCard(title, body, attrs = {}) {
  const card = document.createElement('article');
  for (const [key, value] of Object.entries(attrs)) card.dataset[key] = value;
  const heading = document.createElement('h3');
  heading.textContent = title;
  card.append(heading);
  if (body) {
    const copy = document.createElement('p');
    copy.textContent = body;
    card.append(copy);
  }
  return card;
}
function questProgressReadout(s, template) {
  const target = template.need === 'gear' ? GEAR_SLOTS.length : Math.max(1, template.v || 1);
  let value = 0;
  let unit = 'steps';
  if (template.need === 'wins') {
    value = Object.entries(s.story.flags || {}).filter(([key, won]) => key.startsWith('cleared:') && won === true).length;
    unit = 'battle wins';
  } else if (template.need === 'age') {
    value = s.age;
    unit = 'age reached';
  } else if (template.need === 'creature') {
    value = s.army.some(stack => stack.kind === 'creature') ? 1 : 0;
    unit = 'wild creature';
  } else if (template.need === 'rank') {
    value = s.army.some(stack => stack.rank >= template.v) ? 1 : 0;
    unit = 'Veteran stack';
  } else if (template.need === 'gear') {
    value = GEAR_SLOTS.filter(slot => s.hero.equip[slot]).length;
    unit = 'equipped slots';
  } else if (template.need === 'best') {
    value = Math.max(0, ...Object.entries(s.story.flags || {}).filter(([key]) => key.startsWith('endless:')).map(([, waves]) => Number(waves) || 0));
    unit = 'Endless waves';
  }
  return { value, target, label: `${Math.min(value, target)} / ${target} ${unit}` };
}
function equipmentGoalPanel(s) {
  const template = data.QUEST_TEMPLATES.find(quest => quest.need === 'gear');
  if (!template) return null;
  const equippedCount = GEAR_SLOTS.filter(slot => s.hero.equip[slot]).length;
  const claimed = Boolean(s.quests?.[template.id]?.claimed);
  const complete = equippedCount === GEAR_SLOTS.length;
  const section = document.createElement('section');
  section.className = 'journal-equipment-goal';
  section.dataset.equipmentGoal = template.id;
  section.dataset.goalState = claimed ? 'claimed' : complete ? 'ready' : 'progress';
  section.setAttribute('aria-label', `Equipment goal: Arm the Garrison. ${equippedCount} of ${GEAR_SLOTS.length} slots equipped.`);

  const heading = document.createElement('h3');
  heading.textContent = 'Equipment Goal';
  const title = document.createElement('p');
  title.className = 'equipment-goal-title';
  title.textContent = 'Arm the Garrison';
  const progress = document.createElement('p');
  progress.className = 'equipment-goal-progress';
  progress.textContent = `${equippedCount} / ${GEAR_SLOTS.length} slots equipped`;

  const meter = document.createElement('div');
  meter.className = 'meter equipment-goal-meter';
  meter.setAttribute('role', 'progressbar');
  meter.setAttribute('aria-label', `Arm the Garrison: ${equippedCount} of ${GEAR_SLOTS.length} equipment slots`);
  meter.setAttribute('aria-valuemin', '0');
  meter.setAttribute('aria-valuemax', String(GEAR_SLOTS.length));
  meter.setAttribute('aria-valuenow', String(equippedCount));
  meter.style.setProperty('--level', String(equippedCount / GEAR_SLOTS.length));

  const slots = document.createElement('div');
  slots.className = 'journal-equipment-slots';
  slots.setAttribute('aria-label', 'Equipment slots');
  for (const slot of GEAR_SLOTS) {
    const item = s.hero.equip[slot];
    const tile = document.createElement('div');
    tile.className = 'journal-equipment-slot';
    tile.dataset.equipmentSlot = slot;
    tile.dataset.equipped = String(Boolean(item));
    tile.setAttribute('aria-label', `${slotName[slot]}: ${item ? itemTitle(item) : 'Empty'}`);
    const icon = selectGearIcon(gearIcons.icons, slot, item);
    if (icon?.file) {
      const image = document.createElement('img');
      image.src = icon.file;
      image.alt = '';
      image.dataset.gearIcon = icon.id;
      tile.append(image);
    } else {
      const image = element('svg', { viewBox: '-24 -24 48 48', 'aria-hidden': 'true', focusable: 'false' });
      image.append(slotGlyph(slot, 0, 0));
      tile.append(image);
    }
    const ratio = document.createElement('span');
    ratio.textContent = item ? '1 / 1' : '0 / 1';
    tile.append(ratio);
    slots.append(tile);
  }

  const reward = document.createElement('p');
  reward.className = 'equipment-goal-reward';
  reward.append(document.createTextNode(claimed ? 'Reward claimed · ' : 'Reward for completion · '));
  for (const [key, amount] of Object.entries(template.rw || {})) {
    const item = document.createElement('span');
    item.className = 'equipment-goal-reward-item';
    const icon = resourceIcon(key);
    if (icon) item.append(icon);
    const count = document.createElement('span');
    count.textContent = `${amount} ${key}`;
    item.append(count);
    reward.append(item);
  }
  section.append(heading, title, progress, meter, slots, reward);
  return section;
}
function mountSupportChrome(kind, title, subtitle) {
  const host = $('scene-ui');
  host.hidden = false;
  host.className = kind === 'settings' ? 'support settings' : 'support';
  const head = document.createElement('header');
  const heading = document.createElement('h2');
  heading.textContent = title;
  head.append(heading);
  if (subtitle) {
    const line = document.createElement('p');
    line.textContent = subtitle;
    head.append(line);
  }
  const grid = document.createElement('div');
  grid.className = 'support-grid';
  grid.dataset.supportLayout = kind;
  if (kind === 'market') {
    for (const [label, key] of [['Food', 'food'], ['Wood', 'wood'], ['Stone', 'stone'], ['Gold', 'gold']]) {
      const amount = state ? String(Math.floor(state.resources[key])) : '0';
      const note = key === 'gold' ? 'Price, not a batch' : state && state.age < 1 ? 'Opens in Bronze Age' : 'Batch of 100';
      const card = supportCard(label, `${amount}. ${note}`, { marketGood: key });
      card.querySelector('p').className = 'amount';
      const icon = resourceIcon(key);
      if (icon) card.prepend(icon);
      if (key !== 'gold' && state) {
        for (const side of ['buy', 'sell']) {
          const quote = marketQuote(side, key);
          const locked = state.age < 1;
          const short = Object.entries(quote.spend).some(([resource, price]) => state.resources[resource] < price);
          card.append(costButton(side === 'buy' ? 'Buy 100' : 'Sell 100', quote.spend, () => previewAction('MARKET', { side, resource: key }, `${side === 'buy' ? 'Buy' : 'Sell'} 100 ${key}`, quote.spend, `Receive ${side === 'buy' ? `100 ${key}` : `${quote.gain.gold} gold`}.`, `exchange:${side}:${key}`), locked || short, `exchange:${side}:${key}`, false, locked ? 'Opens in the Bronze Age.' : short ? 'Not enough resources.' : ''));
        }
      }
      grid.append(card);
    }
  } else if (kind === 'story') {
    head.classList.add('story-header');
    const rivalPortrait = state?.story?.rival && RIVAL_PORTRAITS[state.story.rival];
    if (rivalPortrait) {
      const portrait = document.createElement('img');
      portrait.className = 'story-rival-portrait';
      portrait.src = rivalPortrait;
      portrait.alt = `Portrait of ${state.story.rival}`;
      portrait.dataset.rivalPortrait = state.story.rival;
      head.prepend(portrait);
    }
    const tabs = document.createElement('div');
    tabs.className = 'journal-tabs';
    tabs.setAttribute('aria-label', 'Story controls');
    for (const [id, label] of [['chronicle', 'Chronicle'], ['quests', 'Objectives']]) {
      const tab = button(label, () => { journalTab = id; if (id === 'quests') setPanel(false); render(); }, false, `journal:${id}`);
      tab.setAttribute('aria-pressed', String(journalTab === id));
      tabs.append(tab);
    }
    tabs.append(button('Settings', () => openSettings(view), false, 'story-settings'));
    head.append(tabs);
    const rivalChooser = document.createElement('section');
    rivalChooser.className = 'journal-rival-chooser';
    if (!state?.story?.rival) {
      const label = document.createElement('h3');
      label.textContent = 'Choose a rival';
      const choices = document.createElement('div');
      choices.className = 'journal-rival-choices';
      for (const name of RIVALS) choices.append(button(name, () => act('CHOOSE_RIVAL', { name }), false, `journal-rival:${name}`));
      rivalChooser.append(label, choices);
    }
    if (journalTab === 'quests') {
      for (const template of data.QUEST_TEMPLATES) {
        const claimed = Boolean(state.quests[template.id].claimed);
        const ready = questReady(state, data, template.id);
        const progress = questProgressReadout(state, template);
        const card = supportCard(template.n, claimed ? 'Reward claimed' : ready ? 'Ready to claim' : 'In progress', {
          questId: template.id,
          questState: claimed ? 'claimed' : ready ? 'ready' : 'progress',
        });
        const progressLine = document.createElement('p');
        progressLine.className = 'quest-progress';
        progressLine.textContent = progress.label;
        card.append(progressLine);
        const meter = document.createElement('div');
        meter.className = 'meter quest-meter';
        meter.setAttribute('role', 'progressbar');
        meter.setAttribute('aria-label', `${template.n}: ${progress.label}`);
        meter.setAttribute('aria-valuemin', '0');
        meter.setAttribute('aria-valuemax', String(progress.target));
        meter.setAttribute('aria-valuenow', String(Math.min(progress.value, progress.target)));
        meter.style.setProperty('--level', String(progress.target ? Math.min(1, progress.value / progress.target) : 0));
        card.append(meter);
        const reward = document.createElement('div');
        reward.className = 'quest-reward';
        const rewardLabel = document.createElement('span');
        rewardLabel.textContent = 'Reward';
        reward.append(rewardLabel);
        for (const [key, amount] of Object.entries(template.rw || {})) {
          const item = document.createElement('span');
          item.className = 'quest-reward-item';
          const icon = resourceIcon(key);
          if (icon) item.append(icon);
          const count = document.createElement('span');
          count.textContent = String(amount);
          item.append(count);
          reward.append(item);
        }
        card.append(reward);
        const actions = document.createElement('div');
        actions.className = 'quest-actions';
        if (ready && !claimed) actions.append(button('Claim reward', () => act('CLAIM_QUEST', { id: template.id }), false, `journal-claim:${template.id}`));
        else if (claimed) actions.append(button('Claimed', () => {}, true, `journal-claimed:${template.id}`));
        const destinations = {
          q1: ['Open War', 'war'],
          q2: ['Open Kingdom', 'kingdom'],
          q3: ['Open Adventure', 'adventure'],
          q4: ['Open Army', 'army'],
          q5: ['Open Forge', 'forge'],
          q6: ['Open War', 'war'],
        };
        const [destinationLabel, destination] = destinations[template.id] || ['Open campaign', 'home'];
        actions.append(button(destinationLabel, () => {
          view = state?.battle?.status === 'ACTIVE' || state?.battle?.pendingSettlement ? 'tactical'
            : state?.defense?.status === 'ACTIVE' || state?.defense?.pendingSettlement ? 'defense'
              : destination;
          setPanel(false);
          render();
        }, false, `quest-destination:${template.id}`));
        card.append(actions);
        grid.append(card);
      }
      grid.classList.add('journal-objectives');
      const milestonePanel = document.createElement('section');
      milestonePanel.className = 'journal-milestones';
      const milestoneTitle = document.createElement('h3');
      const recordedCount = Object.values(state.story.milestones || {}).filter(Boolean).length;
      milestoneTitle.textContent = `Age milestones · ${recordedCount} of 8 recorded`;
      const currentAge = document.createElement('p');
      currentAge.textContent = `Current age: ${data.AGES[state.age].n}`;
      const milestoneMeter = document.createElement('div');
      milestoneMeter.className = 'meter milestone-meter';
      milestoneMeter.setAttribute('role', 'progressbar');
      milestoneMeter.setAttribute('aria-label', `Age milestones: ${recordedCount} of 8 recorded`);
      milestoneMeter.setAttribute('aria-valuemin', '0');
      milestoneMeter.setAttribute('aria-valuemax', '8');
      milestoneMeter.setAttribute('aria-valuenow', String(recordedCount));
      milestoneMeter.style.setProperty('--level', String(recordedCount / 8));
      const ageGrid = document.createElement('div');
      ageGrid.className = 'journal-milestone-grid';
      for (let age = 0; age < data.AGES.length; age += 1) {
        const recorded = Boolean(state.story.milestones[age]);
        const available = state.age >= age;
        const label = recorded ? `Recorded · ${data.AGES[age].n}` : available ? `Record · ${data.AGES[age].n}` : `Locked · ${data.AGES[age].n}`;
        const milestone = button(label, () => act('CLAIM_MILESTONE', { age }), recorded || !available, `journal-milestone:${age}`);
        milestone.dataset.ageMilestone = String(age);
        milestone.dataset.milestoneState = recorded ? 'recorded' : available ? 'available' : 'locked';
        ageGrid.append(milestone);
      }
      milestonePanel.append(milestoneTitle, currentAge, milestoneMeter, ageGrid);
      const gearGoal = equipmentGoalPanel(state);
      host.replaceChildren(head, rivalChooser, grid, ...(gearGoal ? [gearGoal] : []), milestonePanel);
      return;
    }
    for (let index = 0; index < data.STORY.length; index += 1) {
      const open = Boolean(state && state.age >= index);
      const chosen = state?.story?.choices?.[index];
      const parts = (data.STORY[index].t || '').split(' — ');
      const savedChoice = data.STORY[index].ch.find(choice => choice.flag === chosen);
      const statusText = savedChoice ? savedChoice.log : open ? 'Open' : 'Opens in ' + data.AGES[index].n;
      const card = supportCard(parts[0] || `Chapter ${index + 1}`, `${parts[1] || ''} ${statusText}`.trim(), {
        chapter: String(index),
        open: open ? '1' : '0',
      });
      const art = CHAPTER_BACKDROPS[index];
      if (art) {
        card.style.backgroundImage = `linear-gradient(180deg, rgba(12, 16, 20, 0.72) 0%, rgba(12, 16, 20, 0.92) 100%), url("${art}")`;
        card.style.backgroundSize = 'cover';
        card.style.backgroundPosition = 'center';
      }
      grid.append(card);
    }
    const line = storyChamberLine(state, data);
    const future = document.createElement('p');
    future.dataset.conclusion = line.conclusion;
    const current = storyScreen(state, data);
    future.textContent = current.text || line.text;
    if (!current.choices.length && !current.keepValley && !current.concluded) {
      const previousIndex = state.story.chapter - 1;
      const previous = data.STORY[previousIndex]?.ch.find(choice => choice.flag === state.story.choices[previousIndex]);
      const nextAge = data.AGES[state.story.chapter]?.n;
      future.textContent = `${previous?.log || ''}${nextAge ? ` Your next chapter opens in the ${nextAge}. Develop your Kingdom to continue.` : ''}`.trim();
    }
    const decisions = document.createElement('div');
    decisions.className = 'journal-decisions';
    for (const [index, choice] of (data.STORY[state.story.chapter]?.ch || []).entries()) {
      if (state?.story?.rival && current.choices.length) decisions.append(button(choice.t, () => act('STORY_CHOICE', { index }), false, `journal-choice:${index}`));
    }
    if (current.keepValley) decisions.append(button('Keep the valley', () => act('ACK_FUTURE', {}), false, 'journal-keep-valley'));
    const archive = document.createElement('details');
    archive.className = 'journal-archive';
    const summary = document.createElement('summary');
    summary.textContent = 'Chapter archive';
    archive.append(summary, grid);
    host.replaceChildren(head, rivalChooser, future, decisions, archive);
    return;
  } else if (kind === 'war') {
    const modes = [
      ['Skirmish', 'Practice tactics without risking your campaign', 'start-skirmish', () => { act('START_SKIRMISH', {}); if (state.battle) { view = 'tactical'; render(); } }],
      ['Campaign Siege', 'Prepare your towers before holding the gate', 'start-siege', () => prepareDefense('siege')],
      ['Tactical Duel', 'Command your army in a campaign battle', 'start-duel', () => { act('START_DUEL', {}); if (state.battle) { view = 'tactical'; render(); } }],
      ['Endless', 'Prepare, then survive an unending assault', 'start-endless', () => prepareDefense('endless')],
      ['Challenge', 'Share a battle seed. Campaign unchanged.', 'open-challenge', () => { setPanel(true); const seed = document.querySelector('[data-choice="challenge-seed"]'); if (seed) seed.focus(); }],
    ];
    for (const [name, detail, choiceId, run] of modes) {
      const card = document.createElement('button');
      card.type = 'button';
      card.className = 'support-card';
      card.dataset.warMode = name;
      card.dataset.choice = choiceId;
      const heading = document.createElement('h3');
      heading.textContent = name;
      const copy = document.createElement('p');
      copy.textContent = detail;
      card.append(heading, copy);
      card.addEventListener('click', run);
      grid.append(card);
    }
  } else if (kind === 'settings') {
    const music = state?.settings?.music ?? 0;
    const sfx = state?.settings?.sfx ?? 0;
    const reduced = Boolean(state?.settings?.reducedMotion);
    const panel = document.createElement('section');
    panel.className = 'settings-panel';
    panel.setAttribute('aria-label', 'Game settings');
    grid.className = 'support-grid settings-audio';
    for (const [label, value] of [['Music', music], ['Sound', sfx]]) {
      const card = supportCard(label, '', { level: label.toLowerCase() });
      card.classList.add('settings-row');
      const meter = document.createElement('input');
      meter.type = 'range';
      meter.min = '0';
      meter.max = '1';
      meter.step = '0.1';
      meter.value = String(value);
      meter.setAttribute('aria-label', label + ' volume');
      meter.dataset.choice = 'settings-volume:' + label.toLowerCase();
      meter.disabled = !state;
      meter.addEventListener('change', () => act('SETTINGS', { ...state.settings, [label === 'Music' ? 'music' : 'sfx']: Number(meter.value) }));
      card.append(meter);
      grid.append(card);
    }
    const options = document.createElement('div');
    options.className = 'settings-options';
    const graphics = supportCard('Graphics', '');
    graphics.classList.add('settings-row');
    const graphicsSelect = document.createElement('select');
    graphicsSelect.setAttribute('aria-label', 'Graphics quality');
    graphicsSelect.dataset.choice = 'settings-graphics-quality';
    for (const [value, label] of [['low', 'Low'], ['medium', 'Medium'], ['high', 'High']]) {
      const option = document.createElement('option');
      option.value = value;
      option.textContent = label;
      graphicsSelect.append(option);
    }
    graphicsSelect.value = graphicsQuality;
    graphicsSelect.addEventListener('change', () => setGraphicsQuality(graphicsSelect.value));
    graphics.append(graphicsSelect);

    const accessibility = supportCard('Accessibility', '');
    accessibility.classList.add('settings-row');
    const motion = button(reduced ? 'On' : 'Off', () => act('SETTINGS', { ...state.settings, reducedMotion: !reduced }), !state, 'settings-motion');
    motion.setAttribute('aria-label', 'Reduced motion ' + (reduced ? 'on' : 'off'));
    motion.setAttribute('aria-pressed', String(reduced));
    motion.dataset.reducedMotion = reduced ? 'on' : 'off';
    accessibility.append(motion);

    const language = supportCard('Language', '');
    language.classList.add('settings-row');
    const languageSelect = document.createElement('select');
    languageSelect.setAttribute('aria-label', 'Language. English is the only in-game language currently available.');
    languageSelect.disabled = true;
    const english = document.createElement('option');
    english.value = 'en';
    english.textContent = 'English';
    languageSelect.append(english);
    language.append(languageSelect);
    options.append(graphics, accessibility, language);

    const saveKind = saveQueue.status.kind;
    const saveLabel = saveKind === 'committed' ? 'Saved locally' : saveKind === 'pending' ? 'Saving locally' : 'Save unavailable';
    const localSave = supportCard('Local save', saveLabel);
    localSave.className = 'settings-row settings-save-row';
    localSave.dataset.saveState = saveKind;
    localSave.append(button('Open saves', () => { view = 'home'; menuSheet = false; setPanel(false); render(); }, false, 'settings-open-saves'));
    const local = document.createElement('p');
    local.className = 'settings-note';
    local.textContent = 'Local tones only. No account and no network permission.';
    const actions = document.createElement('div');
    actions.className = 'settings-actions';
    const back = button('Back', closeSettings, false, 'settings-back');
    const enable = button('Enable audio', () => { arm(state.settings); blip(); }, !state, 'settings-audio');
    actions.append(back, enable);
    panel.append(head, grid, options, localSave, local, actions);
    host.replaceChildren(panel);
    return;  } else if (kind === 'help') {
    for (const [name, body] of [
      ['Help', 'Build, recruit, travel, fight, equip, and return. The tutorial can be skipped and reviewed.'],
      ['Credits', 'Ages of Dominion Reborn. Offline local campaign.'],
      ['Privacy', 'No account, no network request, and no device permission.'],
    ]) grid.append(supportCard(name, body, { helpColumn: name.toLowerCase() }));
  }
  host.replaceChildren(head, grid);
}
function paintChamber(title, subtitle, kind = '') {
  const world = $('world');
  world.setAttribute('data-chamber', view);
  world.setAttribute('data-support-layout', kind || 'chamber');
  world.append(element('rect', { x: -260, y: -40, width: 1896, height: 848, fill: '#12100d' }));
  const chapterIndex = Math.min(7, Math.max(0, state?.story?.chapter ?? state?.age ?? 0));
  const bgFile = kind === 'story'
    ? (CHAPTER_BACKDROPS[chapterIndex] || CHAMBER_BACKDROPS.story)
    : (CHAMBER_BACKDROPS[kind] || CHAPTER_BACKDROPS[chapterIndex]);
  if (bgFile) {
    world.append(element('image', {
      href: bgFile,
      x: -260,
      y: -40,
      width: 1896,
      height: 848,
      preserveAspectRatio: 'xMidYMid slice',
      opacity: '0.92',
      'data-chamber-backdrop': kind || view,
    }));
  }
  if (kind !== 'story') {
    world.append(element('rect', { x: 48, y: 44, width: 1280, height: 664, rx: 18, fill: 'rgba(14, 18, 22, 0.22)', stroke: '#c9a35b', 'stroke-width': 2.5 }));
    world.append(element('rect', { x: 48, y: 44, width: 12, height: 664, rx: 4, fill: '#9f7f47' }));
  }
  if (kind) mountSupportChrome(kind, title, subtitle);
}
function slotGlyph(slot, x, y) {
  const group = element('g', { transform: `translate(${x} ${y})`, 'data-slot-icon': slot, fill: 'none', stroke: '#e6d3a1', 'stroke-width': 3, 'stroke-linecap': 'round' });
  const path = {
    helm: 'M-16,10 Q-18,-8 0,-18 Q18,-8 16,10 Z M-8,10 H8',
    weapon: 'M-4,-20 L6,8 M-10,2 H2 M2,8 L10,16',
    offhand: 'M-14,-6 Q0,-20 14,-6 L10,16 H-10 Z',
    armor: 'M-16,-8 Q0,-20 16,-8 L12,16 H-12 Z M0,-8 V16',
    boots: 'M-12,-16 H4 V4 H14 V14 H-12 Z',
    accessory: 'M0,-16 A8,8 0 1 1 0,0 A8,8 0 1 1 0,-16',
  }[slot];
  if (path) group.append(element('path', { d: path }));
  return group;
}
function wornKit() {
  const items = {};
  for (const slot of GEAR_SLOTS) {
    const item = state.hero.equip[slot];
    if (!item) continue;
    const bonus = item.kind === 'gear' ? gearBonus(item) : (data.ARTIFACTS[item.artifactId]?.b || {});
    const icon = selectGearIcon(gearIcons.icons, slot, item);
    const wearLayer = slot === 'weapon' && item.kind === 'gear' ? wornWeaponArt(item, state.hero.class) : null;
    items[slot] = {
      id: item.id || slot,
      bonus: Object.entries(bonus).map(([key, amount]) => `${key}+${amount}`).join(','),
      icon: icon?.file || '',
      iconId: icon?.id || '',
      wearLayer,
    };
  }
  return { items };
}
function paintMaterialWalls(world, _geo, _matrix, depth) {
  // The age painting already contains this wall state. Do not stretch segment stamps over it.
  world.append(element('g', wallHostAttrs(state, depth)));
}
function groundToken(world, x, y, label) {
  world.append(element('ellipse', { cx: x, cy: y + 4, rx: 16, ry: 6, fill: '#00000055', 'data-token': label }));
  world.append(element('circle', { cx: x, cy: y - 8, r: 10, fill: '#c9a35b', stroke: '#1a140c', 'stroke-width': 2, 'data-token': label }));
}

function kingdom() {
  const painting = kingdomPainting(state);
  showTerrain(painting.file, `${painting.age} kingdom ${painting.wallKind}`, 'kingdom-painting');
  $('terrain').dataset.wallKind = painting.wallKind;
  $('terrain').dataset.wallPhase = painting.phase;
  $('terrain').dataset.wallStamps = String(painting.stamps.length);
  const world = $('world');
  const geo = contract.geometry.kingdom, matrix = geo.worldToSource;
  const hallPlot = state.plots.find(p => p.id === 'townhall');
  paintMaterialWalls(world, geo, matrix, 'back');
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
  const tone = ['#5d6b52', '#6a6248', '#6a5344', '#534c66', '#6a6248', '#5a4e44', '#445866', '#3e5560'][state.age] || '#5d6b52';
  const scale = frameFit.fit.scale || 1;
  const tutorialSite = tutorialBuildSiteId(state, geo.sites);
  for (const site of geo.sites) {
    const plot = state.plots.find(p => p.id === site.id), [x, y, w, h] = site.rect, centre = project(matrix, [x + w / 2, y + h / 2]);
    const job = state.buildJobs.find(j => j.plotId === plot.id);
    const padState = job ? 'scaffold' : plot.level ? 'built' : 'empty';
    const group = element('g', {
      class: 'plot' + (plot.id === selected ? ' selected' : ''),
      tabindex: 0,
      role: 'button',
      'data-plot': plot.id,
      'data-choice': `site:${plot.id}`,
      'aria-label': `${plot.id}: ${plot.type ?? 'empty plot'} level ${plot.level}`,
      'data-pad-state': padState,
      'data-presentation': KINGDOM_PAD_PRESENTATION,
    });
    const measured = plot.level && plot.type && !(plot.id === 'townhall' && ages[state.age] === 'stone')
      ? ageBuildings.ages[ages[state.age]]?.[plot.type]
      : null;
    const presentation = plotPresentation({
      plot, job, measured, tutorialSiteId: tutorialSite, selected: plot.id === selected,
    });
    group.setAttribute('data-pad-state', presentation.state);
    group.setAttribute('data-pad', presentation.pad ? 'filled' : 'none');
    if (presentation.art) group.setAttribute('data-site-art', presentation.art);
    if (measured?.file && !job) {
      const left = project(matrix, [x, y + h]);
      const right = project(matrix, [x + w, y + h]);
      const feet = project(matrix, [x + w / 2, y + h]);
      const padWidth = Math.hypot(right[0] - left[0], right[1] - left[1]) || 1;
      const requestedH = (padWidth * 1.08) * (measured.height / measured.width);
      const fitted = footAwareVisibleBox({
        width: measured.width,
        height: measured.height,
        maxVisibleCssPx: measured.maxVisibleCssPx || 180,
        foot: measured.foot,
      }, requestedH, scale, feet[1], frameFit.fit.offset[1], 12);
      const drawW = fitted.width;
      const drawH = fitted.height;
      const footX = measured.foot[0] * drawW;
      const footY = measured.foot[1] * drawH;
      group.append(element('image', {
        href: measured.file, x: feet[0] - footX, y: feet[1] - footY, width: drawW, height: drawH,
        'aria-label': kingdomBuildingName(plot.type),
        'pointer-events': 'none',
      }));
    } else if (job) {
      const corners = [[x, y], [x + w, y], [x + w, y + h], [x, y + h]].map(point => project(matrix, point));
      const scaffold = element('g', { 'data-scaffold': plot.id, 'pointer-events': 'none' });
      // Ground foundation footing
      scaffold.append(element('polygon', {
        points: corners.map(p => p.join(',')).join(' '),
        fill: '#4a3b2c33',
        stroke: '#5c4328',
        'stroke-width': 2,
        'stroke-linecap': 'round',
      }));
      // 4 upright timber corner posts with drop shadows
      const postH = 26;
      for (const c of corners) {
        scaffold.append(element('ellipse', {
          cx: c[0], cy: c[1] + 1, rx: 4, ry: 2, fill: '#00000044',
        }));
        scaffold.append(element('line', {
          x1: c[0], y1: c[1], x2: c[0], y2: c[1] - postH,
          stroke: '#3b2814', 'stroke-width': 4, 'stroke-linecap': 'round',
        }));
        scaffold.append(element('line', {
          x1: c[0], y1: c[1], x2: c[0], y2: c[1] - postH,
          stroke: '#8a6538', 'stroke-width': 2, 'stroke-linecap': 'round',
        }));
      }
      // Cross braces on near face
      scaffold.append(element('line', {
        x1: corners[2][0], y1: corners[2][1] - 3, x2: corners[3][0], y2: corners[3][1] - postH + 3,
        stroke: '#b8860b', 'stroke-width': 1.5,
      }));
      scaffold.append(element('line', {
        x1: corners[3][0], y1: corners[3][1] - 3, x2: corners[2][0], y2: corners[2][1] - postH + 3,
        stroke: '#7c5a24', 'stroke-width': 1.5,
      }));
      // Platform staging plank across top
      scaffold.append(element('line', {
        x1: corners[3][0], y1: corners[3][1] - postH, x2: corners[2][0], y2: corners[2][1] - postH,
        stroke: '#c4a574', 'stroke-width': 3, 'stroke-linecap': 'round',
      }));
      // Material stack (dressed stone / timber bundle)
      scaffold.append(element('rect', {
        x: centre[0] - 12, y: centre[1] - 6, width: 24, height: 10, rx: 2,
        fill: '#8a6b47', stroke: '#3b2814', 'stroke-width': 1,
      }));
      group.append(scaffold);
      if (plot.id === selected) {
        group.append(element('polygon', {
          class: 'scaffold-selected',
          points: corners.map(p => p.join(',')).join(' '),
          fill: 'none',
          stroke: '#e6d3a1',
          'stroke-width': 3,
          'data-site-outline': 'selected',
          'pointer-events': 'none',
        }));
      }
      if (plot.type && plot.id !== 'townhall' && !measured) queueLabel(kingdomBuildingName(plot.type), centre[0], centre[1]);
    } else if (plot.level && plot.id !== 'townhall' && !measured) {
      const footprint = element('polygon', {
        class: 'building',
        points: [[x, y], [x + w, y], [x + w, y + h], [x, y + h]].map(v => project(matrix, v).join(',')).join(' '),
        fill: tone,
        'fill-opacity': '0.28',
        stroke: plot.id === selected ? '#e6d3a1' : 'none',
        'stroke-width': plot.id === selected ? 3 : 0,
        'data-site-outline': plot.id === selected ? 'selected' : 'built',
      });
      group.append(footprint);
      queueLabel(kingdomBuildingName(plot.type), centre[0], centre[1]);
    } else if (plot.id === selected && presentation.outline !== 'tutorial') {
      group.append(element('polygon', {
        class: 'selected',
        points: [[x, y], [x + w, y], [x + w, y + h], [x, y + h]].map(v => project(matrix, v).join(',')).join(' '),
        fill: 'none',
        stroke: '#e6d3a1',
        'stroke-width': 3,
        'data-site-outline': 'selected',
        'pointer-events': 'none',
      }));
    } else if (presentation.state === 'empty' && presentation.outline !== 'selected') {
      if (presentation.clearing) group.setAttribute('data-clearing', presentation.clearing);
      if (presentation.outline === 'tutorial') {
        group.append(element('polygon', {
          class: 'empty',
          points: [[x, y], [x + w, y], [x + w, y + h], [x, y + h]].map(v => project(matrix, v).join(',')).join(' '),
          fill: 'none',
          stroke: '#70b9c5',
          'stroke-width': 2,
          'stroke-dasharray': '6 4',
          'data-site-outline': 'tutorial',
          'pointer-events': 'none',
        }));
      }
    }
    group.append(element('polygon', { points: cellPoints(matrix, x, y, w, h), fill: 'transparent', 'pointer-events': 'all' }));
    if (job) {
      group.append(element('circle', { cx: centre[0], cy: centre[1], r: Math.max(6, 10 / scale), fill: '#f1e9d9', stroke: '#d5b573', 'pointer-events': 'none' }));
      const worker = { x: centre[0], y: centre[1], clip: 'work', time: animTime(), reduced: Boolean(state.settings.reducedMotion), worn: wornKit() };
      if (!drawActor(group, element, state.hero.class, { ...worker, scale: 0.08 }) && !drawBoundActor(group, element, state.hero.class, { ...worker, scale: 0.22 })) {
        groundToken(group, centre[0], centre[1], 'scaffold');
      }
    }
    const selectPlot = event => {
      event?.stopPropagation?.();
      let candidates = [site];
      if (event?.detail > 0) {
        const point = inverse(matrix, sourceFromPointer(event));
        candidates = geo.sites.filter(({rect:[sx,sy,sw,sh]}) => point[0] >= sx && point[0] <= sx+sw && point[1] >= sy && point[1] <= sy+sh);
      }
      siteChoices = candidates.length > 1 ? candidates.map(item=>item.id) : null;
      selected = candidates.length === 1 ? candidates[0].id : plot.id;
      kingdomBuildSite = '';
      kingdomActionSheet = false;
      menuSheet = false; resourceSheet = false;
      setPanel(true); render();
    };
    group.addEventListener('click', selectPlot);
    const onPlotKey = event => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); selectPlot(); } };
    group.addEventListener('keydown', onPlotKey);
    world.append(group);
  }
  paintMaterialWalls(world, geo, matrix, 'front');
  if (worldOnly) return;
  const plot = selected ? state.plots.find(p => p.id === selected) : null;
  const buildingArt = type => ageBuildings.ages[ages[state.age]]?.[type]?.file || '';
  const priceReason = payment => {
    const short = Object.entries(payment)
      .filter(([key, amount]) => state.resources[key] < amount)
      .map(([key, amount]) => `${Math.ceil(amount - state.resources[key])} ${key}`);
    return short.length ? `Need ${short.join(', ')}.` : '';
  };
  if (kingdomActionSheet) {
    $('selected').textContent = 'Kingdom actions';
    choiceHeading('Stewardship');
    $('choices').append(button('Back to the Kingdom', () => { kingdomActionSheet = false; selected = ''; setPanel(false); render(); }, false, 'kingdom-actions-back'));
    const hallPay = cost(data, 'townhall', hallPlot?.level ?? 1);
    const hallBusy = state.buildJobs.some(job => job.plotId === 'townhall');
    const hallReason = hallBusy ? 'Town Hall construction is already underway.' : priceReason(hallPay);
    $('choices').append(costButton('Upgrade Town Hall', hallPay, () => previewBuild('townhall', 'townhall', 'build:townhall'), Boolean(hallReason), 'build:townhall', false, hallReason, buildingArt('townhall')));
    const wallPay = cost(data, 'walls', state.walls.level);
    const wallBusy = state.buildJobs.some(job => job.plotId === 'walls');
    const wallReason = wallBusy ? 'Wall construction is already underway.' : priceReason(wallPay);
    $('choices').append(costButton(state.walls.level ? 'Upgrade Walls' : 'Build Walls', wallPay, () => previewBuild('walls', 'walls', 'build:walls'), Boolean(wallReason), 'build:walls', false, wallReason, buildingArt('walls')));
    if (state.age < 7) {
      const payment = agePrice(state.age);
      const reason = hallPlot.level < state.age + 2 ? `Town Hall level ${state.age + 2} required.` : priceReason(payment);
      $('choices').append(costButton('Advance age', payment, () => previewAction('AGE_UP', {}, `Advance to ${data.AGES[state.age + 1].n}`, payment, 'Existing items and buildings keep their identities. Confirm spends these resources once.', 'age-advance'), Boolean(reason), 'age-advance', false, reason));
    }
    $('choices').append(button('End day', () => act('END_DAY', {}), false, 'end-day'));
    if (state.tutorial.step >= 4) $('choices').append(button('Recruit', () => { kingdomActionSheet = false; view = 'army'; setPanel(false); render(); }, false, 'go-recruit'));
  } else if (kingdomBuildSite) {
    const target = state.plots.find(item => item.id === kingdomBuildSite);
    if (target && target.level === 0) {
      $('selected').textContent = `Build at ${target.id}`;
      choiceHeading('Choose a building');
      $('choices').append(button('Back to selected site', () => { kingdomBuildSite = ''; render(); }, false, `build-picker-back:${target.id}`));
      const grid = document.createElement('div');
      grid.className = 'kingdom-build-grid';
      for (const type of Object.keys(data.BUILDINGS).filter(key => !['townhall', 'walls'].includes(key))) {
        const payment = cost(data, type, target.level);
        const busy = state.buildJobs.some(job => job.plotId === target.id);
        const duplicate = ['barracks', 'workshop', 'hall', 'armory'].includes(type) && state.plots.some(other => other.id !== target.id && other.type === type);
        const reason = busy ? 'Construction is already underway here.' : duplicate ? `${kingdomBuildingName(type)} already exists. Select that building to upgrade it.` : priceReason(payment);
        const label = `Build ${kingdomBuildingName(type)}`;
        const item = costButton(label, payment, () => previewBuild(target.id, type, `build:${target.id}:${type}`), Boolean(reason), `build:${target.id}:${type}`, false, reason, buildingArt(type));
        item.classList.add('kingdom-build-choice');
        grid.append(item);
      }
      $('choices').append(grid);
    } else {
      kingdomBuildSite = '';
      $('selected').textContent = 'Select a site';
    }
  } else if (!plot) {
    $('selected').textContent = `Kingdom · day ${state.day} · ${state.weather} · ${state.walls.level ? `walls ${state.walls.level}` : 'no walls'}`;
  } else {
    $('selected').textContent = plot.type ? `${kingdomBuildingName(plot.type)} · level ${plot.level}` : `${selected} · empty site`;
    if (plot.type) {
      const payment = cost(data, plot.type, plot.level);
      const busy = state.buildJobs.some(job => job.plotId === plot.id);
      const reason = busy ? 'Construction is already underway here.' : priceReason(payment);
      const label = `Upgrade ${kingdomBuildingName(plot.type)}`;
      $('choices').append(costButton(label, payment, () => previewBuild(plot.id, plot.type, `build:${plot.id}:${plot.type}`), Boolean(reason), `build:${plot.id}:${plot.type}`, false, reason, buildingArt(plot.type)));
      const output = plotProduction(state, plot.id, rates);
      if (output) {
        const resourceName = output.resource[0].toUpperCase() + output.resource.slice(1);
        const amount = new Intl.NumberFormat('en-US', { maximumFractionDigits: 2 }).format(output.rate);
        const readout = document.createElement('div');
        readout.className = 'kingdom-production-readout';
        readout.dataset.sceneCopy = 'kingdom-production';
        readout.setAttribute('role', 'group');
        readout.setAttribute('aria-label', `${kingdomBuildingName(plot.type)} production: ${amount} ${output.resource} per second`);
        const resourceArt = selection.delivery?.[`resource-${output.resource}`];
        const iconFile = resourceArt?.uiFile || resourceArt?.file;
        if (iconFile) {
          const icon = document.createElement('img');
          icon.src = iconFile;
          icon.alt = '';
          icon.width = 22;
          icon.height = 22;
          readout.append(icon);
        }
        const text = document.createElement('span');
        text.textContent = `${amount} ${resourceName} per second`;
        readout.append(text);
        $('choices').append(readout);
      }
    } else {
      const busy = state.buildJobs.some(job => job.plotId === plot.id);
      const choose = button(busy ? 'Construction underway' : 'Choose a building', () => {
        if (busy) { say('Construction is already underway here.'); return; }
        kingdomBuildSite = plot.id;
        render();
      }, false, `build-picker:${plot.id}`);
      choose.classList.add('kingdom-context-action');
      choose.prepend(glyph('M3 17.5 L13.8 3.5 L17 6 L6.2 20 Z M13.2 4.3 L16.5 7.2 M3.8 17.7 L6.6 20.2 M2 22 H15'));
      if (busy) { choose.setAttribute('aria-disabled', 'true'); choose.setAttribute('aria-describedby', 'message'); choose.title = 'Construction is already underway here.'; }
      $('choices').append(choose);
    }
    $('choices').append(button('Kingdom actions', () => { kingdomActionSheet = true; render(); }, false, 'kingdom-actions-open'));
  }
  const focusCopy = kingdomActionSheet
    ? 'Choose a Kingdom action.'
    : kingdomBuildSite
      ? `Choose a building for ${kingdomBuildSite}.`
      : plot
        ? `${plot.id}: ${plot.type ? `${kingdomBuildingName(plot.type)}, level ${plot.level}` : 'empty site'}.`
        : `${state.plots.filter(item => item.id !== 'townhall' && item.level === 0).length} sites are empty. Walls ${state.walls.level ? `level ${state.walls.level}` : 'are unbuilt'}.`;
  const underway = state.buildJobs.length ? ` ${state.buildJobs.length} construction ${state.buildJobs.length === 1 ? 'project' : 'projects'} underway.` : '';
  say(`${data.AGES[state.age].n} · Day ${state.day} · ${state.weather}. ${focusCopy}${underway}${cue()}`);
}

function measureFrame() {
  const rect = $('stage').getBoundingClientRect();
  const panel = $('panel');
  const panelOpen = panel.classList.contains('open');
  const sidePanelOpen = panelOpen && view !== 'kingdom';
  const inset = sidePanelOpen ? panel.getBoundingClientRect().width + 8 : 0;
  const width = Math.max(1, rect.width - inset);
  const worldWidth = worldViewportWidth(rect.width, width, sidePanelOpen, window.innerWidth);
  const height = Math.max(1, rect.height);
  const isChamber = ['market', 'story', 'war', 'settings', 'help', 'army'].includes(view);
  const focus = view === 'kingdom'
    ? kingdomFocusBounds(contract.geometry.kingdom, scene.hall)
    : view === 'hero' ? heroFocus()
    : isChamber ? { minX: 72, minY: 56, maxX: 1304, maxY: 696 } : null;
  const boardGeometry = view === 'adventure'
    ? adventureGeometryForCampaign()
    : ['tactical', 'defense'].includes(view) ? contract.geometry[view] : null;
  const adventureWorld = view === 'adventure' ? adventureWorlds.find(world => world.id === state?.adventureWorldId) : null;
  const crossingReady = Boolean(campaignMapImage(adventureWorld) && adventureWorld?.geometry?.version === 4);
  const crossingFocus = crossingReady && state?.adventure
    ? crossingPresentation(state.adventureWorldId, state.adventure, boardGeometry?.bridges, travelPreview)
    : null;
  const sourceSize = boardGeometry?.sourceSize ?? [1376, 768];
  const boardVerticalExtent = boardGeometry
    ? [[0, 0], [boardGeometry.cols, 0], [boardGeometry.cols, boardGeometry.rows], [0, boardGeometry.rows]]
      .map(point => project(boardGeometry.worldToSource, point)[1])
    : [0, 0];
  const boardTop = Math.min(...boardVerticalExtent);
  const boardBottom = Math.max(...boardVerticalExtent);
  const cameraWidth = view === 'adventure' && panelOpen ? width : worldWidth;
  let fit = view === 'home'
    ? coverCamera([1376, 768], worldWidth, height)
    : boardGeometry
      ? wideBoardCamera(sourceSize, cameraWidth, height, boardTop, boardBottom)
      : camera([1376, 768], worldWidth, height, focus, view === 'kingdom' ? 24 : focus ? 12 : 0);
  const stage = $('stage');
  const terrain = $('terrain');
  stage.style.backgroundImage = '';
  terrain.style.maskImage = '';
  terrain.style.webkitMaskImage = '';
  stage.style.backgroundSize = '';
  stage.style.backgroundPosition = '';
  delete stage.dataset.adventureEdgeBackdrop;
  frameFit = { width, height, inset, rect, fit, worldWidth, sourceSize, boardGeometry: Boolean(boardGeometry), crossingFocus, edgeSafety: null };
  setWorldCssScale(frameFit.fit.scale);
}
function fitScene() {
  const fit = frameFit.fit;
  const [sourceWidth, sourceHeight] = frameFit.sourceSize ?? [1376, 768];
  const frame = $('frame');
  frame.style.width = `${sourceWidth}px`;
  frame.style.height = `${sourceHeight}px`;
  frame.style.transformOrigin = '0 0';
  frame.style.transform = `translate(${fit.offset[0]}px, ${fit.offset[1]}px) scale(${fit.scale})`;
  const viewBox = frameFit.crossingFocus?.sourceRect ?? [0, 0, sourceWidth, sourceHeight];
  $('world').setAttribute('viewBox', viewBox.join(' '));
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

function paintAdventureHeroPanel(host) {
  const className = data.CLASSES[state.hero.class]?.n || 'Hero';
  const body = portraitCard(state.hero.class, state.age) || heroBody(state.hero.class, state.age) || pendingPortrait(state.hero.class, state.age);
  const mana = manaMax(state, data);
  const totalUnits = state.army.reduce((sum, stack) => sum + stack.count, 0);
  const stackLabel = `${state.army.length} ${state.army.length === 1 ? 'stack' : 'stacks'}`;
  const unitLabel = `${totalUnits} ${totalUnits === 1 ? 'unit' : 'units'}`;
  let panel = host.querySelector('.adventure-hero-panel');
  if (!panel) panel = document.createElement('section');
  panel.className = 'adventure-hero-panel';
  panel.setAttribute('role', 'group');
  panel.setAttribute('aria-label', `Hero and army status: ${className}, level ${state.hero.level}, ${state.hero.xp} experience, ${state.hero.mana} of ${mana} mana; ${stackLabel}, ${unitLabel}.`);
  const existingPanels = [...host.querySelectorAll('.adventure-hero-panel')];
  for (const duplicate of existingPanels) if (duplicate !== panel) duplicate.remove();
  if (panel.parentElement !== host) host.append(panel);
  let portrait = panel.querySelector('img');
  if (body?.file) {
    if (!portrait) { portrait = document.createElement('img'); portrait.alt = ''; panel.prepend(portrait); }
    if (portrait.getAttribute('src') !== body.file) portrait.src = body.file;
  } else portrait?.remove();
  let copy = panel.querySelector('.adventure-hero-copy');
  if (!copy) { copy = document.createElement('div'); copy.className = 'adventure-hero-copy'; panel.append(copy); }
  let kicker = copy.querySelector('.adventure-hero-kicker');
  if (!kicker) { kicker = document.createElement('span'); kicker.className = 'adventure-hero-kicker'; copy.append(kicker); }
  kicker.textContent = 'HERO';
  let name = copy.querySelector('strong');
  if (!name) { name = document.createElement('strong'); copy.append(name); }
  name.textContent = `${className} · Level ${state.hero.level}`;
  let progress = copy.querySelector('p');
  if (!progress) { progress = document.createElement('p'); copy.append(progress); }
  progress.textContent = `XP ${state.hero.xp} · Mana ${state.hero.mana}/${mana}`;
  let army = panel.querySelector('.adventure-army-summary');
  if (!army) { army = document.createElement('p'); army.className = 'adventure-army-summary'; panel.append(army); }
  army.textContent = `Army · ${stackLabel} · ${unitLabel}`;
}

function paintAdventureQuickAccess(host) {
  const existing = [...host.querySelectorAll('.adventure-quick-access')];
  const tray = existing[0] || document.createElement('div');
  for (const duplicate of existing.slice(1)) duplicate.remove();
  tray.replaceChildren();
  tray.className = 'adventure-quick-access';
  tray.setAttribute('role', 'group');
  tray.setAttribute('aria-label', 'Adventure quick actions');
  const openStory = section => {
    storyQuickFocus = section;
    view = 'story';
    menuSheet = false;
    setPanel(true);
    render();
  };
  const actions = [
    ['quests', 'Quests', 'Open saved quests', 'M5 3 H19 V21 H5 Z M8 7 H16 M8 11 H16 M8 15 H14', () => openStory('quests')],
    ['bag', 'Bag', 'Open hero inventory', 'M5 8 H19 L18 21 H6 Z M8 8 V6 A4 4 0 0 1 16 6 V8', () => { heroDetailTab = 'inventory'; selectedHeroSlot = null; view = 'hero'; menuSheet = false; setPanel(true); render(); }],
    ['camp', 'Camp', 'Open rest and end-day actions', 'M12 3 L2 21 H22 Z M12 3 V21 M7 13 H10 V16', () => { adventurePanelRequested = true; setPanel(true); render(); }],
    ['diplomacy', 'Diplomacy', 'Open rival and story records', 'M3 5 H16 V14 H9 L4 18 V14 H3 Z M13 11 H21 V18 H18 V21 L14 18 H12', () => openStory('rival')],
  ];
  for (const [id, label, detail, icon, onClick] of actions) {
    const control = button('', onClick, false, `adventure-quick:${id}`);
    control.classList.add('adventure-quick-action');
    control.setAttribute('aria-label', `${label}. ${detail}.`);
    control.title = `${label} · ${detail}`;
    control.append(glyph(icon));
    tray.append(control);
  }
  host.append(tray);
}

function paintTacticalHeroPlaque(host, battle) {
  const hero = state?.hero;
  if (!hero) return;
  const className = data.CLASSES[hero.class]?.n || 'Hero';
  const portrait = portraitCard(hero.class, state.age) || heroBody(hero.class, state.age) || pendingPortrait(hero.class, state.age);
  const stats = battle.hero || heroStats(state, data);
  const plaqueCopy = tacticalHeroPlaqueCopy({
    className,
    level: hero.level,
    xp: hero.xp,
    stats,
    mana: battle.mana,
    morale: battle.morale,
  });
  let panel = host.querySelector('.tactical-hero-plaque');
  if (!panel) panel = document.createElement('section');
  panel.className = 'tactical-hero-plaque';
  panel.setAttribute('role', 'group');
  panel.setAttribute('aria-label', plaqueCopy.ariaLabel);
  for (const duplicate of [...host.querySelectorAll('.tactical-hero-plaque')]) if (duplicate !== panel) duplicate.remove();
  if (panel.parentElement !== host) host.append(panel);

  let image = panel.querySelector('img');
  if (portrait?.file) {
    if (!image) { image = document.createElement('img'); image.alt = ''; panel.prepend(image); }
    if (image.getAttribute('src') !== portrait.file) image.src = portrait.file;
  } else image?.remove();

  let copy = panel.querySelector('.tactical-hero-copy');
  if (!copy) { copy = document.createElement('div'); copy.className = 'tactical-hero-copy'; panel.append(copy); }
  let identity = copy.querySelector('strong');
  if (!identity) { identity = document.createElement('strong'); copy.append(identity); }
  identity.textContent = plaqueCopy.identityText;
  let experience = copy.querySelector('[data-hero-experience]');
  if (!experience) { experience = document.createElement('span'); experience.dataset.heroExperience = ''; copy.append(experience); }
  experience.textContent = plaqueCopy.experienceText;
  let commandStats = copy.querySelector('[data-hero-command-stats]');
  if (!commandStats) { commandStats = document.createElement('span'); commandStats.dataset.heroCommandStats = ''; copy.append(commandStats); }
  commandStats.textContent = plaqueCopy.commandStatsText;
  let morale = copy.querySelector('[data-hero-morale]');
  if (!morale) { morale = document.createElement('span'); morale.dataset.heroMorale = ''; copy.append(morale); }
  morale.textContent = plaqueCopy.moraleText;
}

function paintTacticalRoundBadge(host, battle) {
  let badge = host.querySelector('.tactical-round-badge');
  if (!badge) badge = document.createElement('div');
  badge.className = 'tactical-round-badge';
  badge.setAttribute('role', 'status');
  badge.setAttribute('aria-label', `Round ${battle.round}, ${data.AGES[state.age]?.n || 'Campaign'}, day ${state.day}`);
  badge.innerHTML = '';
  const round = document.createElement('strong');
  round.textContent = `Round ${battle.round}`;
  const day = document.createElement('span');
  day.textContent = `${data.AGES[state.age]?.n || 'Campaign'} · Day ${state.day}`;
  badge.append(round, day);
  for (const duplicate of [...host.querySelectorAll('.tactical-round-badge')]) if (duplicate !== badge) duplicate.remove();
  if (badge.parentElement !== host) host.append(badge);
}

function paintDeploymentTray(status, battle) {
  const deployment = battle.deployment;
  const placed = new Set(deployment.placedIds);
  const alliedIds = new Set(deployment.movableIds);
  const roster = document.createElement('div');
  roster.className = 'deployment-roster';
  roster.setAttribute('role', 'group');
  roster.setAttribute('aria-label', `Battle formations. ${placed.size} of ${deployment.movableIds.length} allied formations placed. Opposing formations are fixed.`);
  for (const stack of battle.stacks.filter(item => !item.dead && item.count > 0)) {
    const isAlly = alliedIds.has(stack.id);
    const isPlaced = isAlly && placed.has(stack.id);
    const selected = isAlly && deploymentSelection === stack.id;
    const name = battleTitle(stack);
    const card = isAlly
      ? button('', () => { deploymentSelection = stack.id; render(); }, false, `deployment-stack:${stack.id}`)
      : document.createElement('div');
    card.classList.add('deployment-card');
    card.dataset.side = stack.side;
    card.dataset.selected = String(selected);
    if (isAlly) {
      card.setAttribute('aria-label', `${name}. ${isPlaced ? `Placed at ${stack.x + 1}, ${stack.y + 1}` : 'Not placed'}. Select formation.`);
      card.setAttribute('aria-pressed', String(selected));
    } else {
      card.setAttribute('role', 'group');
      card.setAttribute('aria-label', `Opponent formation: ${name}. Fixed at ${stack.x + 1}, ${stack.y + 1}.`);
    }
    const plate = plateForStack(stack);
    if (plate?.file) {
      const image = document.createElement('img');
      image.src = plate.file;
      image.alt = '';
      image.loading = 'lazy';
      card.append(image);
    }
    const copy = document.createElement('span');
    copy.className = 'deployment-card-copy';
    const title = document.createElement('strong');
    title.textContent = name.replace(/ ×\d+ rank \d+$/, '');
    const count = document.createElement('small');
    count.textContent = `×${stack.count} · ${isAlly ? (isPlaced ? 'Placed' : 'Ready') : 'Opponent'}`;
    copy.append(title, count);
    card.append(copy);
    roster.append(card);
  }
  const instructions = document.createElement('p');
  instructions.className = 'deployment-instructions';
  instructions.textContent = `${placed.size}/${deployment.movableIds.length} allied formations placed · Select one, then choose a glowing legal cell.`;
  const actions = document.createElement('div');
  actions.className = 'deployment-actions';
  actions.append(button('Start Battle', () => act('START_DEPLOYED_BATTLE', {}), placed.size !== deployment.movableIds.length, 'start-deployed-battle', true));
  actions.append(button('Cancel setup', () => act('CANCEL_BATTLE_SETUP', {}), false, 'cancel-battle-setup'));
  status.append(instructions, roster, actions);
}

function sceneStatus(title, detail, kind = 'travel') {
  const host = $('scene-ui');
  host.hidden = false;
  host.className = `game-status ${kind}`;
  const heading = document.createElement('h2');
  heading.textContent = title;
  const line = document.createElement('p');
  line.textContent = detail;
  host.replaceChildren(heading, line);
  return host;
}

function paintAdventureMinimap(geometry, adventure, preview, terrainFile = '') {
  const mapState = adventureMinimap(geometry, adventure, preview);
  if (!mapState) return;
  const host = document.createElement('div');
  host.id = 'adventure-minimap';
  host.setAttribute('role', 'img');
  host.setAttribute('aria-label', mapState.routeTrail.length > 1
    ? 'Valley map. Explored roads and places are marked; gold marks supplies, red marks guards, and the blue trail is your selected route.'
    : 'Valley map. Explored roads and discovered places are marked; gold marks supplies and red marks guards.');
  const viewSize = 10;
  const map = element('svg', {
    viewBox: `${mapState.player.x - viewSize / 2} ${mapState.player.y - viewSize / 2} ${viewSize} ${viewSize}`,
    'aria-hidden': 'true',
    focusable: 'false',
  });
  const sourceSize = geometry.sourceSize ?? [1376, 768];
  const defs = element('defs', {});
  const clip = element('clipPath', { id: 'adventure-map-clip' });
  clip.append(element('circle', { cx: mapState.player.x, cy: mapState.player.y, r: viewSize / 2 }));
  defs.append(clip);
  const content = element('g', { 'clip-path': 'url(#adventure-map-clip)' });
  content.append(element('rect', { x: 0, y: 0, width: mapState.columns, height: mapState.rows, class: 'minimap-base' }));
  const matrix = geometry.worldToSource;
  const [a, b, c, d, e, f] = Array.isArray(matrix) ? matrix : [];
  const determinant = a * d - b * c;
  const canProjectTerrain = Boolean(terrainFile && Number.isFinite(determinant) && Math.abs(determinant) > 0.0001);
  if (canProjectTerrain) {
    const sourceToWorld = [
      d / determinant,
      -b / determinant,
      -c / determinant,
      a / determinant,
      (c * f - d * e) / determinant,
      (b * e - a * f) / determinant,
    ];
    const sourceTransform = `matrix(${sourceToWorld.join(' ')})`;
    const terrainImage = (opacity, style = '') => element('image', {
      href: terrainFile,
      x: 0,
      y: 0,
      width: sourceSize[0],
      height: sourceSize[1],
      preserveAspectRatio: 'none',
      opacity,
      style,
      'data-minimap-terrain': terrainFile,
      'pointer-events': 'none',
    });
    const mutedMap = element('g', { transform: sourceTransform, 'data-minimap-unexplored': 'muted' });
    mutedMap.append(terrainImage('0.7', 'filter:saturate(.64) brightness(.72)'));
    content.append(mutedMap);
    content.append(element('rect', {
      x: 0, y: 0, width: mapState.columns, height: mapState.rows,
      fill: '#07110f', opacity: '0.34', 'pointer-events': 'none',
    }));

    const filterId = 'adventure-minimap-explore-soft-edge';
    const maskId = 'adventure-minimap-explored-mask';
    const filter = element('filter', {
      id: filterId,
      x: mapState.player.x - viewSize / 2 - 1,
      y: mapState.player.y - viewSize / 2 - 1,
      width: viewSize + 2,
      height: viewSize + 2,
      filterUnits: 'userSpaceOnUse',
    });
    filter.append(element('feGaussianBlur', { stdDeviation: '0.18' }));
    const mask = element('mask', {
      id: maskId,
      x: mapState.player.x - viewSize / 2,
      y: mapState.player.y - viewSize / 2,
      width: viewSize,
      height: viewSize,
      maskUnits: 'userSpaceOnUse',
      maskContentUnits: 'userSpaceOnUse',
    });
    mask.append(element('rect', {
      x: mapState.player.x - viewSize / 2,
      y: mapState.player.y - viewSize / 2,
      width: viewSize,
      height: viewSize,
      fill: '#000',
    }));
    const explored = element('g', { fill: '#fff', filter: `url(#${filterId})` });
    for (const cell of mapState.exploredCells) {
      explored.append(element('rect', { x: cell.x, y: cell.y, width: 1, height: 1 }));
    }
    mask.append(explored);
    defs.append(filter, mask);
    const exploredMap = element('g', { mask: `url(#${maskId})`, 'data-minimap-explored': String(mapState.exploredCells.length) });
    const sharpMap = element('g', { transform: sourceTransform });
    sharpMap.append(terrainImage('0.94', 'filter:saturate(1.06) brightness(1.08)'));
    exploredMap.append(sharpMap);
    content.append(exploredMap);
  } else {
    for (const cell of mapState.exploredCells) {
      content.append(element('rect', { x: cell.x, y: cell.y, width: 1, height: 1, class: 'minimap-explored' }));
    }
  }
  for (const cell of mapState.blockedCells) {
    content.append(element('rect', { x: cell.x, y: cell.y, width: 1, height: 1, class: 'minimap-water' }));
  }
  for (const segment of mapState.roadSegments) {
    content.append(element('line', {
      x1: segment.from.x,
      y1: segment.from.y,
      x2: segment.to.x,
      y2: segment.to.y,
      class: 'minimap-road',
    }));
  }
  for (const landmark of mapState.landmarks) {
    content.append(element('circle', {
      cx: landmark.x,
      cy: landmark.y,
      r: 0.24,
      class: 'minimap-landmark',
      'data-landmark': landmark.id,
    }));
  }
  for (const point of mapState.pointsOfInterest) {
    content.append(element('circle', {
      cx: point.x,
      cy: point.y,
      r: 0.19,
      class: `minimap-poi ${point.kind}`,
      'data-point-of-interest': point.id,
    }));
  }
  if (mapState.routeTrail.length > 1) {
    const points = mapState.routeTrail.map(point => `${point.x},${point.y}`).join(' ');
    content.append(element('polyline', { points, class: 'minimap-route' }));
  }
  content.append(element('circle', { cx: mapState.player.x, cy: mapState.player.y, r: 0.34, class: 'minimap-player-halo' }));
  content.append(element('circle', { cx: mapState.player.x, cy: mapState.player.y, r: 0.14, class: 'minimap-player' }));
  map.append(defs, content);
  host.append(map);
  const label = document.createElement('span');
  label.className = 'minimap-label';
  label.textContent = 'VALLEY';
  host.append(label);
  $('stage-field').append(host);
}

function showCombatResult(kind) {
  const session = kind === 'defense' ? state.defense : state.battle;
  if (!session?.pendingSettlement) return;
  const action = kind === 'defense' ? 'SETTLE_DEFENSE' : 'SETTLE_BATTLE';
  let settled;
  try { settled = command(state, { id: crypto.randomUUID(), type: action, payload: {} }, state.clock, data); }
  catch { return; }
  const winner = kind === 'defense' ? session.winner : session.outcome?.winner;
  const host = $('scene-ui');
  host.hidden = false;
  host.className = `combat-result ${kind === 'tactical' ? 'tactical-result' : 'defense-result'}`;
  const title = document.createElement('h2');
  title.textContent = winner === 'p' ? 'Victory' : winner === 'retreat' ? 'Retreated' : 'Defeat';
  const note = document.createElement('p');
  const practice = ['skirmish', 'challenge'].includes(session.practice);
  note.textContent = practice
    ? 'Practice battle · Your campaign is unchanged'
    : `${data.AGES[state.age]?.n || 'Campaign'} · Day ${state.day} · Your forces return from the battlefield`;
  const survivors = document.createElement('div');
  survivors.className = 'result-forces';
  const participatingIds = kind === 'defense'
    ? new Set(session.armyDeployed && session.army?.stackId ? [session.army.stackId] : [])
    : new Set((session.stacks || []).filter(stack => stack.side === 'p').map(stack => stack.campaignId).filter(Boolean));
  const originalForces = practice
    ? (session.stacks || []).filter(stack => stack.side === 'p')
    : state.army.filter(stack => participatingIds.has(stack.id));
  for (const original of originalForces) {
    const remaining = practice ? original : settled.army.find(stack => stack.id === original.id);
    const initialCount = practice ? (original.maxCount ?? original.count) : original.count;
    const remainingCount = practice ? original.count : (remaining?.count || 0);
    const lost = Math.max(0, initialCount - remainingCount);
    const xpEarned = !practice && remaining ? Math.max(0, Math.round(remaining.xp - original.xp)) : 0;
    const titleStack = practice ? { ...original, count: initialCount, rank: original.rank ?? 0 } : original;
    const accessibleTitle = stackTitle(titleStack, data);
    const resultTitle = accessibleTitle.replace(/ ×\d+ rank \d+$/, '');
    const resultRank = practice ? (original.rank ?? 0) : (remaining?.rank ?? original.rank ?? 0);
    const plate = plateForStack(original);
    const card = document.createElement('div');
    card.className = 'result-force-card';
    if (plate?.file) {
      const art = document.createElement('img');
      art.src = plate.file;
      art.alt = '';
      card.append(art);
    }
    card.append(sceneCopy(resultTitle, 'result-force-name'));
    card.append(sceneCopy(`Count ${remainingCount}`, 'survivors'));
    card.append(sceneCopy(`Rank ${resultRank}`, 'result-force-rank'));
    card.append(sceneCopy(lost ? `${lost} lost` : 'No losses', 'casualties'));
    if (xpEarned) card.append(sceneCopy(`XP +${xpEarned}`, 'result-unit-xp'));
    card.setAttribute('aria-label', `${accessibleTitle}. ${remainingCount} survivors, ${lost} lost, ${xpEarned} unit experience gained.`);
    survivors.append(card);
  }
  const rewards = document.createElement('div');
  rewards.className = 'result-rewards';
  if (!practice && winner === 'p') rewards.append(sceneCopy('Campaign rewards', 'result-rewards-heading'));
  for (const resource of ['food', 'wood', 'stone', 'gold']) {
    const gain = settled.resources[resource] - state.resources[resource];
    if (gain <= 0) continue;
    const entry = document.createElement('span');
    const icon = resourceIcon(resource);
    if (icon) entry.append(icon);
    entry.append(document.createTextNode(`+${Math.round(gain)}`));
    entry.setAttribute('aria-label', `${resource} gained ${Math.round(gain)}`);
    rewards.append(entry);
  }
  const newItems = settled.inventory.filter(item => !state.inventory.some(original => original.id === item.id));
  for (const item of newItems) {
    const recovered = sceneCopy(`${itemTitle(item)} recovered`, 'loot');
    recovered.setAttribute('aria-label', `Recovered ${itemTitle(item)}`);
    const icon = selectGearIcon(gearIcons.icons, item.slot, item);
    if (icon?.file) {
      const image = document.createElement('img');
      image.src = icon.file;
      image.alt = '';
      image.setAttribute('aria-hidden', 'true');
      image.dataset.lootGearIcon = icon.id;
      recovered.prepend(image);
    }
    rewards.append(recovered);
  }
  const experience = (settled.hero.xp - state.hero.xp);
  if (settled.hero.level > state.hero.level) rewards.append(sceneCopy(`Level ${settled.hero.level}`, 'level-gain'));
  else if (experience > 0) rewards.append(sceneCopy(`+${experience} XP`, 'experience'));
  const extraActions = [];
  if (kind === 'tactical' && session.practice === 'challenge' && session.challenge) {
    extraActions.push(button('Export challenge result', () => {
      const record = challengeResult(session, session.challenge);
      download('aod-challenge-result.json', JSON.stringify(record));
    }, false, 'challenge-result'));
  }
  const confirm = button('Return to campaign', () => act(action, {}), false, `result:${kind}`);
  host.replaceChildren(title, note, survivors, ...(rewards.childElementCount ? [rewards] : []), ...extraActions, confirm);
}

function paintAdventureSites(depth = {}) {
  const geo = adventureGeometryForCampaign();
  const matrix = geo.worldToSource;
  const world = $('world');
  const campaignWorld = adventureWorlds.find(entry => entry.id === state?.adventureWorldId);
  const integratedMap = isIntegratedAdventureMap(campaignWorld);
  const map = adventureMap(geo);
  const sites = geo.sites.filter(site => discoveredSite(site, state.adventure));
  const travelerPoint = state.adventure && !state.adventure.atTown
    ? project(matrix, [state.adventure.x + 0.5, state.adventure.y + 0.5])
    : null;
  sites.sort((first, second) => project(matrix, [first.rect[0], first.rect[1] + first.rect[3]])[1] - project(matrix, [second.rect[0], second.rect[1] + second.rect[3]])[1]);
  for (const site of sites) {
    const [left, top, width, height] = site.rect;
    const feet = project(matrix, [left + width / 2, top + height]);
    if (Number.isFinite(depth.before) && feet[1] > depth.before) continue;
    if (Number.isFinite(depth.after) && feet[1] <= depth.after) continue;
    const preview = () => {
      if (!state.adventure || state.adventure.atTown) { setPanel(true); render(); return; }
      try {
        const route = routeTo(map, [state.adventure.x, state.adventure.y], site.approach);
        travelPreview = { path: route.cells, cells: route.cells, cost: route.cost, destination: SITE_TITLES[site.id] };
        render();
      } catch (error) { setPanel(true); say(error.message); }
    };
    const building = null;
    const asset = consumerCatalog.assets.find(row => row.id === `adventure-site-${site.id}`);
    const file = ADVENTURE_SITE_ART[site.id];
    if (!file) continue;
    const dimensions = site.id === 'town' ? { width: 1536, height: 1024 } : building || asset?.dimensions || { width: 1024, height: 1024 };
    const fitted = visibleBox({ ...dimensions, maxVisibleCssPx: site.id === 'town' ? 220 : 160 }, site.id === 'town' ? 230 : 112, frameFit.fit.scale || 1);
    const foot = site.id === 'town' ? [0.5, 0.92] : building?.foot || [0.5, 0.94];
    const claimed = state.adventure?.claimedSites?.includes(site.id) ?? false;
    const status = claimed ? ' Already explored.' : '';
    const group = element('g', { class: 'adventure-site', 'data-site-id': site.id, 'data-claimed': String(claimed), 'data-landmark-description': site.landmark || '', 'data-choice': `adventure-site:${site.id}`, 'data-art-mode': integratedMap ? 'map-hotspot' : 'sprite', role: 'button', tabindex: 0, 'aria-label': `${SITE_TITLES[site.id]}.${status} Preview a route to its entrance` });
    if (integratedMap) {
      if (site.representation === 'runtime-object') {
        group.append(element('ellipse', { cx: feet[0], cy: feet[1] - 4, rx: fitted.width * 0.38, ry: 10, fill: '#11180b55', 'pointer-events': 'none' }));
        group.append(element('image', { class: 'adventure-site-object', href: file, x: feet[0] - fitted.width * foot[0], y: feet[1] - fitted.height * foot[1], width: fitted.width, height: fitted.height, 'pointer-events': 'none', 'data-functional-site-object': site.id, 'data-claimed': String(claimed) }));
      }
      group.append(element('polygon', {
        class: 'adventure-site-hotspot',
        points: cellPoints(matrix, left, top, width, height),
        fill: 'transparent',
        'pointer-events': 'all',
        'data-site-hotspot': site.id,
      }));
    } else {
      group.append(element('ellipse', { cx: feet[0], cy: feet[1] - 4, rx: fitted.width * 0.38, ry: 10, fill: '#11180b55', 'pointer-events': 'none' }));
      group.append(element('image', { href: file, x: feet[0] - fitted.width * foot[0], y: feet[1] - fitted.height * foot[1], width: fitted.width, height: fitted.height, 'pointer-events': 'none' }));
      group.append(element('rect', { x: feet[0] - fitted.width * foot[0], y: feet[1] - fitted.height * foot[1], width: fitted.width, height: fitted.height, fill: 'transparent', 'pointer-events': 'all' }));
    }
    group.addEventListener('click', event => { event.stopPropagation(); preview(); });
    group.addEventListener('keydown', event => {
      if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); preview(); }
    });
    world.append(group);
    const hideSiteLabel = travelerPoint
      && adventureAnchorLabelOverlapsTraveler(feet, travelerPoint, frameFit.fit.scale);
    if (!hideSiteLabel) queueLabel(claimed ? `${SITE_TITLES[site.id]} · explored` : SITE_TITLES[site.id], feet[0], feet[1], { placement: 'below' });
  }
}

function paintRegisteredAdventureRoads(world, geo, matrix) {
  const routeLayer = element('g', {
    'data-terrain-route-overlay': 'gunpowder',
    'pointer-events': 'none',
    'aria-hidden': 'true',
  });
  const layers = [
    { stroke: '#382918', 'stroke-width': 24, opacity: 0.09, filter: 'blur(1.2px)' },
    { stroke: '#987c53', 'stroke-width': 15, opacity: 0.18 },
    { stroke: '#dcc493', 'stroke-width': 7, opacity: 0.16 },
  ];
  for (const [index, road] of geo.roads.entries()) {
    const points = road.map(point => project(matrix, [point[0] + .5, point[1] + .5]).join(',')).join(' ');
    for (const [layer, style] of layers.entries()) {
      routeLayer.append(element('polyline', {
        ...style,
        points,
        fill: 'none',
        'stroke-linecap': 'round',
        'stroke-linejoin': 'round',
        'data-route-index': index,
        'data-route-layer': layer,
      }));
    }
  }
  world.append(routeLayer);
}

function paintAdventureChannel(world, geo, matrix, campaignWorld) {
  return;
  const blocked = geo.blocked || [];
  if (!blocked.length) return;
  const style = ADVENTURE_CHANNEL_STYLES[campaignWorld?.channelTheme] || ADVENTURE_CHANNEL_STYLES.river;
  const channel = element('g', {
    class: 'adventure-channel',
    'data-adventure-channel': campaignWorld?.channelTheme || 'river',
    'pointer-events': 'none',
    'aria-hidden': 'true',
  });
  const gradientId = `adventure-channel-water-${campaignWorld?.id || 'default'}`;
  const rippleId = `adventure-channel-ripples-${campaignWorld?.id || 'default'}`;
  const defs = element('defs', {});
  const gradient = element('linearGradient', {
    id: gradientId,
    x1: project(matrix, [4, 0])[0],
    y1: project(matrix, [4, 0])[1],
    x2: project(matrix, [6, 0])[0],
    y2: project(matrix, [6, 0])[1],
    gradientUnits: 'userSpaceOnUse',
  });
  for (const [offset, color, opacity] of [
    ['0%', style.deep, 0.74], ['28%', style.water, 0.78], ['62%', style.water, 0.78], ['100%', style.deep, 0.74],
  ]) gradient.append(element('stop', { offset, 'stop-color': color, 'stop-opacity': opacity }));
  const ripples = element('pattern', {
    id: rippleId,
    patternUnits: 'userSpaceOnUse',
    width: 112,
    height: 94,
    patternTransform: 'rotate(-11)',
  });
  for (let index = 0; index < 6; index += 1) {
    const x = (index * 31) % 98 - 8;
    const y = 8 + index * 14;
    const length = 18 + (index * 17) % 36;
    ripples.append(element('path', {
      d: `M${x} ${y} q${length * 0.28} -5 ${length * 0.52} 0 t${length * 0.48} 1`,
      fill: 'none',
      stroke: style.light,
      'stroke-width': index % 2 ? 1.5 : 2,
      'stroke-linecap': 'round',
      opacity: 0.24 + (index % 3) * 0.05,
    }));
  }
  defs.append(gradient, ripples);
  channel.append(defs);
  const channelSamples = Array.from({ length: geo.rows * 4 + 1 }, (_, index) => {
    const row = index / 4;
    const centre = 5 + Math.sin(row * 0.66) * 0.12 + Math.sin(row * 1.31 + 0.4) * 0.045;
    return { row, centre };
  });
  const leftBank = channelSamples.map(({ row, centre }) => project(matrix, [centre - 0.92, row]));
  const rightBank = channelSamples.map(({ row, centre }) => project(matrix, [centre + 0.92, row]));
  const riverPath = `${smoothAdventurePoints([...leftBank, ...rightBank.reverse()])} Z`;
  channel.append(element('path', {
    d: riverPath,
    fill: '#091b1e',
    stroke: '#091b1e',
    'stroke-width': 18,
    opacity: 0.30,
    transform: 'translate(0 4)',
  }));
  channel.append(element('path', {
    d: riverPath,
    fill: `url(#${gradientId})`,
    stroke: style.deep,
    'stroke-width': 5,
    'stroke-linejoin': 'round',
    opacity: 0.88,
    'data-water-cells': blocked.length,
  }));
  channel.append(element('path', {
    d: riverPath,
    fill: `url(#${rippleId})`,
    opacity: 0.52,
    'pointer-events': 'none',
  }));
  for (const edge of [leftBank, rightBank]) {
    const edgePath = smoothAdventurePoints(edge);
    channel.append(element('path', {
      d: edgePath,
      fill: 'none',
      stroke: style.bank,
      'stroke-width': 8,
      'stroke-linecap': 'round',
      'stroke-linejoin': 'round',
      'stroke-dasharray': '31 20 12 34 7 22',
      opacity: 0.38,
    }));
    channel.append(element('path', {
      d: edgePath,
      fill: 'none',
      stroke: style.edge,
      'stroke-width': 2,
      'stroke-linecap': 'round',
      'stroke-dasharray': '13 47 6 29',
      opacity: 0.34,
    }));
  }
  for (let row = 1; row < geo.rows; row += 2) {
    const centre = 5 + Math.sin((row + 0.5) * 0.66) * 0.12 + Math.sin((row + 0.5) * 1.31 + 0.4) * 0.045;
    const first = project(matrix, [centre - 0.42, row + 0.5]);
    const mid = project(matrix, [centre + 0.06, row + 0.56 + Math.sin(row * 1.7) * 0.07]);
    const last = project(matrix, [centre + 0.46, row + 0.5]);
    channel.append(element('path', {
      d: `M${first[0]} ${first[1]} Q${mid[0]} ${mid[1]} ${last[0]} ${last[1]}`,
      stroke: style.glint,
      'stroke-width': 1.7,
      'stroke-linecap': 'round',
      opacity: 0.24,
      'stroke-dasharray': '8 19 13 24',
    }));
  }
  world.append(channel);
}

function smoothAdventurePoints(points) {
  if (points.length < 3) return `M${points.map(point => point.join(' ')).join(' L')}`;
  let path = `M${points[0][0]} ${points[0][1]}`;
  for (let index = 0; index < points.length - 1; index += 1) {
    const previous = points[Math.max(0, index - 1)];
    const current = points[index];
    const next = points[index + 1];
    const following = points[Math.min(points.length - 1, index + 2)];
    const firstControl = [current[0] + (next[0] - previous[0]) / 6, current[1] + (next[1] - previous[1]) / 6];
    const secondControl = [next[0] - (following[0] - current[0]) / 6, next[1] - (following[1] - current[1]) / 6];
    path += ` C${firstControl[0]} ${firstControl[1]} ${secondControl[0]} ${secondControl[1]} ${next[0]} ${next[1]}`;
  }
  return path;
}

function smoothAdventureRoute(road, matrix) {
  return smoothAdventurePoints(road.map(point => project(matrix, [point[0] + 0.5, point[1] + 0.5])));
}

function paintAdventureRoadNetwork(world, geo, matrix, campaignWorld) {
  const routes = element('g', {
    class: 'adventure-road-network',
    'data-terrain-route-overlay': 'registered-campaign-v1',
    'data-world-id': campaignWorld?.id || '',
    'pointer-events': 'none',
    'aria-hidden': 'true',
  });
  for (const [index, road] of (geo.roads || []).entries()) {
    const path = smoothAdventureRoute(road, matrix);
    routes.append(element('path', {
      d: path, fill: 'none', stroke: '#251d14', 'stroke-width': 13, opacity: 0.07,
      'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'data-route-index': index,
    }));
    routes.append(element('path', {
      d: path, fill: 'none', stroke: '#765a38', 'stroke-width': 7, opacity: 0.24,
      'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'data-route-index': index,
    }));
    routes.append(element('path', {
      d: path, fill: 'none', stroke: '#c6ac7a', 'stroke-width': 2.2, opacity: 0.12,
      'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'data-route-index': index,
    }));
    routes.append(element('path', {
      d: path, fill: 'none', stroke: '#f0d9aa', 'stroke-width': 0.9, opacity: 0.12,
      'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-dasharray': '1 7 2 13',
      'data-route-index': index, 'data-route-texture': 'stone-grain',
    }));
  }
  world.append(routes);
}

function paintAdventureBridge(world, geo, matrix, campaignWorld) {
  return;
  const bridge = geo.bridges?.[0];
  if (!bridge) return;
  const [x, y, width, height] = bridge.rect;
  const [a, b, c, d] = matrix;
  const centre = project(matrix, [x + width / 2, y + height / 2]);
  const group = element('g', {
    class: 'adventure-bridge',
    'data-adventure-bridge': bridge.id,
    'data-bridge-material': campaignWorld?.bridgeMaterial || 'stone',
    'data-bridge-art': ADVENTURE_BRIDGE_ART,
    'pointer-events': 'none',
    'aria-hidden': 'true',
  });
  const sprite = element('g', { transform: `matrix(${a} ${b} ${c} ${d} ${centre[0]} ${centre[1]})` });
  sprite.append(element('image', {
    href: ADVENTURE_BRIDGE_ART,
    x: -width / 2,
    y: -height / 2,
    width,
    height,
    preserveAspectRatio: 'none',
    style: `filter:${ADVENTURE_BRIDGE_FILTERS[campaignWorld?.bridgeMaterial] || 'none'}`,
    'pointer-events': 'none',
  }));
  group.append(sprite);
  world.append(group);
}

function paintAdventureAnchor(world, geometry, matrix, point, map, hideLabel = false, engagedGuard = false) {
  const isGuard = point.kind === 'guard';
  const resourceId = point.id;
  const file = isGuard ? ADVENTURE_GUARD_ART[point.id] : ADVENTURE_RESOURCE_ART[resourceId];
  if (!file) return;
  const label = isGuard
    ? (point.id === 'guard-ruin' ? 'Bandit patrol' : 'Wild creature pack')
    : `${resourceId[0].toUpperCase()}${resourceId.slice(1)} cache`;
  const centre = project(matrix, [point.x, point.y]);
  const fitted = visibleBox({ width: 1536, height: 1024, maxVisibleCssPx: isGuard ? 78 : 60 }, isGuard ? 70 : 48, frameFit.fit.scale || 1);
  const group = element('g', {
    class: isGuard ? 'adventure-enemy-marker' : 'adventure-resource-marker',
    'data-adventure-anchor': point.id,
    'data-anchor-kind': point.kind,
    ...(engagedGuard ? { 'data-engaged-guard': 'true' } : {}),
    'data-choice': `adventure-anchor:${point.id}`,
    role: 'button',
    tabindex: 0,
    'aria-label': `${label}. Preview a route to this location`,
  });
  group.append(element('ellipse', {
    cx: centre[0], cy: centre[1] - 2,
    rx: fitted.width * 0.31, ry: 8,
    fill: '#10130f88',
    'pointer-events': 'none',
  }));
  group.append(element('image', {
    href: file,
    x: centre[0] - fitted.width / 2,
    y: centre[1] - fitted.height * 0.92,
    width: fitted.width,
    height: fitted.height,
    preserveAspectRatio: 'xMidYMax meet',
    'pointer-events': 'none',
  }));
  if (engagedGuard) {
    group.append(element('ellipse', {
      cx: centre[0], cy: centre[1] - 2,
      rx: fitted.width * 0.68, ry: fitted.height * 0.62,
      fill: '#a84e3826', stroke: '#f1a078', 'stroke-width': 6,
      'pointer-events': 'none', 'data-encounter-focus': '1',
    }));
  }
  group.append(element('rect', {
    x: centre[0] - fitted.width / 2,
    y: centre[1] - fitted.height,
    width: fitted.width,
    height: fitted.height,
    fill: 'transparent',
    'pointer-events': 'all',
  }));
  const preview = () => {
    if (!state.adventure || state.adventure.atTown) return;
    const target = [Math.floor(point.x), Math.floor(point.y)];
    if (state.adventure.x === target[0] && state.adventure.y === target[1]) { setPanel(true); render(); return; }
    try {
      const route = routeTo(map, [state.adventure.x, state.adventure.y], target);
      travelPreview = { path: route.cells, cells: route.cells, cost: route.cost, destination: label };
      render();
    } catch (error) { setPanel(true); say(error.message); }
  };
  group.addEventListener('click', event => { event.stopPropagation(); preview(); });
  group.addEventListener('keydown', event => {
    if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); preview(); }
  });
  world.append(group);
  if (engagedGuard) queueLabel(label, centre[0], centre[1] - 110, { priority: 15, placement: 'above' });
  else if (!hideLabel) queueLabel(label, centre[0], centre[1], { priority: isGuard ? 14 : 9, placement: 'below' });
}

function paintAdventureFog(world, geo, matrix, visited) {
  const stage = geo.sourceSize ?? [1376, 768];
  const filterId = 'adventure-fog-edge';
  const maskId = 'adventure-fog-mask';
  const defs = element('defs', {});
  const filter = element('filter', {
    id: filterId,
    x: -32,
    y: -32,
    width: stage[0] + 64,
    height: stage[1] + 64,
    filterUnits: 'userSpaceOnUse',
    colorInterpolationFilters: 'sRGB',
  });
  filter.append(element('feGaussianBlur', { stdDeviation: 14 }));
  const mask = element('mask', {
    id: maskId,
    x: 0,
    y: 0,
    width: stage[0],
    height: stage[1],
    maskUnits: 'userSpaceOnUse',
    maskContentUnits: 'userSpaceOnUse',
  });
  mask.append(element('rect', { x: 0, y: 0, width: stage[0], height: stage[1], fill: '#000' }));
  const unvisited = element('g', { fill: '#fff', filter: `url(#${filterId})` });
  for (let y = 0; y < geo.rows; y++) for (let x = 0; x < geo.cols; x++) {
    if (!visited.has(`${x},${y}`)) unvisited.append(element('polygon', { points: cellPoints(matrix, x, y) }));
  }
  mask.append(unvisited);
  defs.append(filter, mask);
  world.append(defs);
  world.append(element('rect', {
    class: 'fog',
    x: 0,
    y: 0,
    width: stage[0],
    height: stage[1],
    fill: '#10171b',
    opacity: 0.32,
    mask: `url(#${maskId})`,
    'data-fog-state': 'saved-unvisited',
    'pointer-events': 'none',
  }));
}

function adventure() {
  const world = $('world');
  const geo = adventureGeometryForCampaign(), matrix = geo.worldToSource;
  const ground = modeGround('adventure');
  const campaignWorld = adventureWorlds.find(entry => entry.id === state?.adventureWorldId);
  const registeredGeometry = Boolean(campaignMapImage(campaignWorld) && campaignWorld?.geometry?.version === 4);
  const crossingFocus = registeredGeometry && ground && state?.adventure
    ? crossingPresentation(campaignWorld?.id || state.adventureWorldId, state.adventure, geo.bridges, travelPreview)
    : null;
  if (crossingFocus) {
    world.setAttribute('data-adventure-crossing-focus', crossingFocus.bridgeId);
    const [x, y, width, height] = crossingFocus.sourceRect;
    world.append(element('image', {
      href: crossingFocus.file, x, y, width, height, preserveAspectRatio: 'none',
      'data-adventure-crossing-background': crossingFocus.bridgeId, 'pointer-events': 'none',
    }));
  } else world.removeAttribute('data-adventure-crossing-focus');
  const map = adventureMap(geo);
  world.removeAttribute('data-campaign-world-preview-source');
  world.setAttribute('data-board', ground ? 'adventure-live-world-v4' : 'adventure-provisional-v1');
  world.setAttribute('data-registration', registeredGeometry ? 'game-specific-world-coordinate-layers-v4' : modeScenes.registration);
  if (campaignWorld) {
    world.setAttribute('data-adventure-world-id', campaignWorld.id);
    world.setAttribute('aria-label', `${campaignWorld.title} campaign world map`);
    world.setAttribute('data-adventure-terrain-file', campaignMapImage(campaignWorld) || '');
    world.setAttribute('data-adventure-reference-example-file', campaignWorld.referenceFile || '');
    world.setAttribute('data-adventure-map-version', String(campaignWorld.sourceBindings?.production?.geometryVersion || ''));
    world.setAttribute('data-adventure-geometry-source-file', campaignWorld.geometry?.sourceFile || '');
    world.setAttribute('data-adventure-water', campaignWorld.mapFeatures?.water || 'none');
    world.setAttribute('data-adventure-bridge-count', String(campaignWorld.mapFeatures?.bridges || 0));
    world.setAttribute('data-adventure-playable-crossings', String(campaignWorld.mapFeatures?.playableCrossings || 0));
  } else {
    world.removeAttribute('data-adventure-world-id');
    world.removeAttribute('data-adventure-terrain-file');
    world.removeAttribute('data-adventure-reference-example-file');
    world.removeAttribute('data-adventure-map-version');
    world.removeAttribute('data-adventure-geometry-source-file');
    world.setAttribute('aria-label', 'Campaign scene');
  }
  if (registeredGeometry) {
    world.setAttribute('data-adventure-render-model', isIntegratedAdventureMap(campaignWorld)
      ? 'integrated-map-art-plus-live-interactions'
      : 'generated-terrain-plus-live-sites-resources-enemies-routes');
    if (!crossingFocus && !isIntegratedAdventureMap(campaignWorld)) paintAdventureRoadNetwork(world, geo, matrix, campaignWorld);
  } else {
    world.removeAttribute('data-adventure-render-model');
    world.removeAttribute('data-adventure-water');
    world.removeAttribute('data-adventure-bridge-count');
    world.removeAttribute('data-adventure-playable-crossings');
  }
  if (!ground) {
    const sourceSize = geo.sourceSize ?? [1376, 768];
    world.append(element('rect', { width: sourceSize[0], height: sourceSize[1], fill: '#1b3328' }));
    for (const road of geo.roads) {
      const points = road.map(p => project(matrix, [p[0] + .5, p[1] + .5]).join(',')).join(' ');
      world.append(element('polyline', { points, fill: 'none', stroke: '#6b5344', 'stroke-width': 22, 'stroke-linecap': 'round' }));
      world.append(element('polyline', { points, fill: 'none', stroke: '#c4a574', 'stroke-width': 8, 'stroke-linecap': 'round' }));
    }
    for (const [x, y] of geo.blocked ?? []) world.append(element('polygon', { class: 'water', points: cellPoints(matrix, x, y) }));
    for (const site of geo.sites) {
      const [x, y, w, h] = site.rect;
      world.append(element('polygon', { class: 'site', points: cellPoints(matrix, x, y, w, h) }));
    }
  }
  if (!registeredGeometry && ground && state.age === 4 && modeScenes.candidates?.['adventure-gunpowder']?.routeOverlay === 'contract-roads-v1') {
    paintRegisteredAdventureRoads(world, geo, matrix);
  }
  if (state.adventure) {
    const seen = new Set(state.adventure.visited);
    // Save-state membership stays cell-exact; only the visual edge is softly feathered.
    paintAdventureFog(world, geo, matrix, seen);
  }
  const onRoad = Boolean(state.adventure && !state.adventure.atTown);
  const visibleAnchors = onRoad ? visibleAdventureAnchors(geo, state.adventure) : [];
  const travelerLabelPoint = onRoad ? project(matrix, [state.adventure.x + 0.5, state.adventure.y + 0.5]) : null;
  for (const point of visibleAnchors) {
    const anchorPoint = project(matrix, [point.x, point.y]);
    const closeToTraveler = travelerLabelPoint && adventureAnchorLabelOverlapsTraveler(anchorPoint, travelerLabelPoint, frameFit.fit.scale);
    const pendingCell = state.adventure?.pendingEncounter?.cell;
    const engagedGuard = point.kind === 'guard' && Array.isArray(pendingCell)
      && pendingCell[0] === Math.floor(point.x) && pendingCell[1] === Math.floor(point.y);
    paintAdventureAnchor(world, geo, matrix, point, map, Boolean(closeToTraveler), engagedGuard);
  }
  if (state.adventure && !state.adventure.atTown) {
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
    const travelerMode = adventureTravelerMode(geo, state.adventure, moving);
    const approachedSite = travelerMode === 'on-foot'
      ? geo.sites.find(site => site.id !== 'town' && site.approach[0] === state.adventure.x && site.approach[1] === state.adventure.y)
      : null;
    world.setAttribute('data-adventure-traveler-mode', travelerMode);
    if (approachedSite) world.setAttribute('data-adventure-site-approach', approachedSite.id);
    else world.removeAttribute('data-adventure-site-approach');
    if (travelPreview?.cells?.length) {
      const routeScale = frameFit.crossingFocus ? frameFit.crossingFocus.sourceRect[2] / frameFit.sourceSize[0] : 1;
      const routeCells = [[state.adventure.x, state.adventure.y], ...travelPreview.cells];
      const previewPoints = routeCells.map(cell => project(matrix, [cell[0] + 0.5, cell[1] + 0.5]).join(','));
      world.append(element('polyline', { points: previewPoints.join(' '), fill: 'none', stroke: '#09262c', 'stroke-width': 16 * routeScale, 'stroke-linecap': 'round', 'stroke-linejoin': 'round', opacity: '0.9' }));
      world.append(element('polyline', { points: previewPoints.join(' '), fill: 'none', stroke: '#8de0d4', 'stroke-width': 7 * routeScale, 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-dasharray': '12 8' }));
      const destinationCell = travelPreview.cells.at(-1);
      const destination = project(matrix, [destinationCell[0] + 0.5, destinationCell[1] + 0.5]);
      world.append(element('circle', { cx: destination[0], cy: destination[1], r: 22 * routeScale, fill: '#09262ca8', stroke: '#f1d99e', 'stroke-width': 4 * routeScale, 'data-route-destination': '1' }));
      world.append(element('circle', { cx: destination[0], cy: destination[1], r: 7 * routeScale, fill: '#8de0d4', stroke: '#fff2cb', 'stroke-width': 2 * routeScale }));
      queueLabel(travelPreview.destination || 'Destination', destination[0], destination[1], { priority: 16, placement: 'above' });
    }
    const placeTraveler = (at) => {
      if (travelerMode === 'on-foot') {
        const walker = drawActor(world, element, state.hero.class, {
          x: at[0],
          y: at[1],
          scale: 0.2,
          facing,
          clip: moving ? 'walk' : 'idle',
          time: animTime(),
          reduced: Boolean(state.settings.reducedMotion),
          worn: wornKit(),
        }) || drawBoundActor(world, element, state.hero.class, {
          x: at[0],
          y: at[1],
          scale: 0.46,
          facing,
          clip: moving ? 'walk' : 'idle',
          time: animTime(),
          reduced: Boolean(state.settings.reducedMotion),
          worn: wornKit(),
        });
        if (walker) {
          walker.setAttribute('data-adventure-travel-mode', 'on-foot');
          walker.setAttribute('pointer-events', 'none');
          walker.setAttribute('role', 'img');
          walker.setAttribute('aria-label', 'Your hero on foot');
        }
        else groundToken(world, at[0], at[1], state.hero.class);
        return;
      }
      const agedMount = staticMountForAge(state.age);
      if (state.age < 6 && drawMount(world, element, {
        x: at[0], y: at[1], scale: 0.056 / (frameFit.fit.scale || 1), facing, moving,
        time: animTime(), reduced: state.settings.reducedMotion,
        riderClass: state.hero.class, worn: wornKit(),
      })) return;
      if (agedMount && drawStaticMount(world, element, agedMount, at[0], at[1], {
        facing, moving, time: animTime(), reduced: state.settings.reducedMotion,
        riderClass: state.hero.class, worn: wornKit(),
      })) return;
      const review = drawReviewMount(world, element, {
        x: at[0], y: at[1], facing, moving,
        time: animTime(), reduced: state.settings.reducedMotion,
      });
      if (review) {
        const riderClip = moving && !state.settings.reducedMotion ? 'mountWalk' : 'idle';
        const rider = drawActor(world, element, state.hero.class, {
          x: review.saddle.x + facing * -2,
          y: review.saddle.y + 34,
          scale: 0.1,
          facing,
          clip: riderClip,
          time: animTime(),
          reduced: Boolean(state.settings.reducedMotion) || !moving,
          worn: wornKit(),
        }) || drawBoundActor(world, element, state.hero.class, {
          x: review.saddle.x + facing * -2,
          y: review.saddle.y + 34,
          scale: 0.34,
          facing,
          clip: riderClip,
          time: animTime(),
          reduced: state.settings.reducedMotion || !moving,
        });
        if (rider) {
          rider.setAttribute('data-mount-mark', 'review-horse-v4');
          rider.setAttribute('data-rider', 'painted-partial');
        } else groundToken(world, review.saddle.x, review.saddle.y, state.hero.class);
        return;
      }
      const rider = drawActor(world, element, state.hero.class, {
        x: at[0],
        y: at[1],
        scale: 0.1,
        facing,
        clip: moving ? 'walk' : 'idle',
        time: animTime(),
        reduced: Boolean(state.settings.reducedMotion),
        worn: wornKit(),
      }) || drawBoundActor(world, element, state.hero.class, {
        x: at[0],
        y: at[1],
        scale: 0.46,
        facing,
        clip: 'idle',
        time: animTime(),
        reduced: true,
      });
      if (!rider) groundToken(world, at[0], at[1], state.hero.class);
      else rider.setAttribute('data-rider', rider.getAttribute('data-gait') === 'per-joint' ? 'per-joint' : 'painted-partial');
    };
    const showRoute = route => {
      travelPreview = { path: route.cells, cells: route.cells, cost: route.cost };
      render();
    };
    for (let y = 0; y < geo.rows; y += 1) {
      for (let x = 0; x < geo.cols; x += 1) {
        const open = isOpen(map, x, y);
        const hit = element('polygon', {
          points: cellPoints(matrix, x, y),
          fill: '#00000000',
          stroke: 'none',
          'data-adventure-cell': `${x},${y}`,
          'data-open': open ? '1' : '0',
        });
        if (open) {
          hit.style.cursor = 'pointer';
          hit.onclick = event => {
            event.stopPropagation();
            try { showRoute(routeTo(map, committed, [x, y])); }
            catch (error) { say(error.message); }
          };
        }
        world.append(hit);
      }
    }
    const traveler = project(matrix, shown);
    if (!crossingFocus) world.append(element('circle', { cx: traveler[0], cy: traveler[1] - 8, r: 22, fill: '#70b9c533', stroke: '#c4e5d9', 'stroke-width': 3, 'data-map-marker': 'traveler' }));
    paintAdventureSites({ before: traveler[1] });
    placeTraveler(traveler);
    paintAdventureSites({ after: traveler[1] });
    if (travelerMode !== 'on-foot') queueLabel('Your hero', traveler[0], traveler[1], { priority: 10, placement: 'below' });
    if (worldOnly) return;
    const movesLabel = `${state.adventure.moves} ${state.adventure.moves === 1 ? 'move' : 'moves'}`;
    const routeBlocked = Boolean(travelPreview && !canConfirmRoute(travelPreview, state.adventure.moves));
    const routeLimitCopy = routeBlocked
      ? `${travelPreview.cost} needed · ${state.adventure.moves} left. Shorten route or end day.`
      : '';
    const travelAction = travelCommitAction(routeWithCurrentCell(travelPreview, committed), geo.bridges);
    sceneStatus(travelPreview?.destination || (travelAction.bridgeId ? 'Bridge crossing' : campaignWorld?.title) || 'Explore the valley', travelPreview
      ? routeBlocked
        ? routeLimitCopy
        : `Cost ${travelPreview.cost} · ${state.adventure.moves} moves left · ${travelAction.bridgeId ? 'Cross Bridge' : 'Confirm'} to travel.`
      : `${movesLabel} left.`);
    paintAdventureMinimap(geo, state.adventure, travelPreview, ground);
    paintAdventureHeroPanel($('stage-field'));
    paintAdventureQuickAccess($('stage-field'));
    $('selected').textContent = `${campaignWorld?.title || 'Valley journey'} · ${movesLabel}`;
    const queueStep = (dx, dy) => {
      const from = travelPreview?.cells?.at(-1) || committed;
      try { showRoute(routeTo(map, committed, [from[0] + dx, from[1] + dy])); }
      catch (error) { say(error.message); }
    };
    const dwellingSite = geo.sites.find(site => site.id === 'dwelling');
    const reachedSite = geo.sites.find(site => site.id !== 'town'
      && site.approach[0] === state.adventure.x
      && site.approach[1] === state.adventure.y);
    if (reachedSite && ['ruin', 'mill', 'mine'].includes(reachedSite.id)) {
      const siteId = reachedSite.id;
      const claimed = state.adventure.claimedSites?.includes(siteId) ?? false;
      choiceHeading(SITE_TITLES[siteId]);
      if (!claimed) {
        if (siteId === 'ruin') {
          const xp = Math.round(state.adventure.siteOffers.ruinXp * (1 + 0.15 * levelOf('hall')));
          $('choices').append(button(`Study the ruins · +${xp} XP`, () => act('CLAIM_ADVENTURE_SITE', { id: siteId }), false, `claim-site:${siteId}`));
        } else if (siteId === 'mill') {
          const amount = state.adventure.siteOffers.millFood;
          $('choices').append(button(`Collect provisions · +${amount} food`, () => act('CLAIM_ADVENTURE_SITE', { id: siteId }), false, `claim-site:${siteId}`));
        } else {
          const amount = state.adventure.siteOffers.mineGold;
          $('choices').append(button(`Recover gold · +${amount}`, () => act('CLAIM_ADVENTURE_SITE', { id: siteId }), false, `claim-site:${siteId}`));
        }
      } else $('choices').append(sceneCopy('This site has already been explored.', 'adventure-site-claimed'));
    }
    const skillShrine = reachedSite?.id === 'shrine';
    if (skillShrine) {
      const shrineOffer = state.hero.offers.find(item => item.source === 'adventure-shrine' && !item.chosen && !item.declined);
      const activeOffer = state.hero.offers.find(item => !item.chosen && !item.declined);
      choiceHeading('Skill monument');
      if (shrineOffer) {
        for (const id of shrineOffer.choices) {
          const skill = data.SKILLS[id];
          const level = state.hero.skills[id];
          $('choices').append(button(`Learn ${skill.n} · ${level + 1}/3`, () => act('CHOOSE_SKILL', { skill: id }), false, `shrine-skill:${id}`));
        }
        $('choices').append(button('Decline this lesson', () => act('DECLINE_SKILL', {}), false, 'decline-shrine-skill'));
      } else if (state.adventure.claimedSites?.includes('shrine')) {
        $('choices').append(sceneCopy('The monument has already shared its lesson.', 'shrine-claimed'));
      } else if (activeOffer) {
        $('choices').append(sceneCopy('Resolve your pending skill offer before studying this monument.', 'shrine-pending-skill'));
      } else if (SKILL_IDS.every(id => state.hero.skills[id] >= 3)) {
        $('choices').append(sceneCopy('Every skill has been mastered; the monument is quiet.', 'shrine-skills-mastered'));
      } else {
        $('choices').append(button('Study the monument', () => act('OFFER_ADVENTURE_SHRINE_SKILL', {}), false, 'study-skill-monument'));
      }
    }
    const atDwelling = Boolean(dwellingSite && state.adventure.x === dwellingSite.approach[0] && state.adventure.y === dwellingSite.approach[1]);
    if (atDwelling) {
      choiceHeading('Creature dwelling');
      const open = state.dwelling && !state.dwelling.claimed ? state.dwelling : null;
      if (open) {
        const payment = dwellingCost(data, open.type, open.multiplier);
        const short = Object.entries(payment).filter(([key, amount]) => state.resources[key] < amount).map(([key, amount]) => `${Math.ceil(amount - state.resources[key])} ${key}`);
        const full = state.army.length >= 2 + levelOf('barracks');
        const reason = full ? 'Roster is full.' : short.length ? `Need ${short.join(', ')}.` : '';
        $('choices').append(costButton(dwellingRecruitLabel(open.count, data.CREATURES[open.type].n), payment, () => act('CLAIM_DWELLING', {}), Boolean(reason), 'claim-dwelling', true, reason));
        $('choices').append(button('Back to road', () => { setPanel(false); render(); }, false, 'back-dwelling'));
      } else {
        const availableTypes = availableDwellingTypes(dwellingPool(data, state.age), state.dwellingHistory);
        if (!availableTypes.length) $('choices').append(sceneCopy('There are no new creature offers at this dwelling.', 'dwelling-offers-exhausted'));
        for (const type of availableTypes) {
          $('choices').append(button(`Ask the ${data.CREATURES[type].n} dwelling`, () => act('OFFER_DWELLING', { type }), false, `offer-dwelling:${type}`));
        }
      }
    }
    const currentCache = visibleAnchors.find(point => point.kind === 'cache'
      && Math.floor(point.x) === state.adventure.x
      && Math.floor(point.y) === state.adventure.y);
    if (currentCache) {
      const amount = state.adventure.cacheOffers[currentCache.id];
      choiceHeading('Supplies found');
      const collect = button(`Collect cache · +${amount} ${currentCache.id}`, () => {
        travelPreview = null;
        act('CLAIM_ADVENTURE_CACHE', { id: currentCache.id });
      }, false, `collect-cache:${currentCache.id}`);
      const icon = resourceIcon(currentCache.id);
      if (icon) collect.prepend(icon);
      collect.classList.add('adventure-cache-collect');
      collect.setAttribute('aria-label', `Collect ${amount} ${currentCache.id} from the cache`);
      $('choices').append(collect);
    }
    choiceHeading('Travel');
    const travelControls = document.createElement('div');
    travelControls.className = 'adventure-travel-controls';
    travelControls.setAttribute('role', 'group');
    travelControls.setAttribute('aria-label', 'Travel one step');
    const directions = [
      ['North', 0, -1, 'M12 2 L22 14 H15 V22 H9 V14 H2 Z'],
      ['South', 0, 1, 'M2 10 H9 V2 H15 V10 H22 L12 22 Z'],
      ['West', -1, 0, 'M2 12 L14 2 V9 H22 V15 H14 V22 Z'],
      ['East', 1, 0, 'M22 12 L10 22 V15 H2 V9 H10 V2 Z'],
    ];
    for (const [name, dx, dy, icon] of directions) {
      const control = button('', () => queueStep(dx, dy), false, `preview-${name.toLowerCase()}`);
      control.classList.add('adventure-travel-direction');
      control.setAttribute('aria-label', `Travel ${name.toLowerCase()}`);
      control.title = `Travel ${name.toLowerCase()}`;
      control.append(glyph(icon));
      travelControls.append(control);
    }
    $('choices').append(travelControls);
    choiceHeading('Discovered places');
    for (const site of geo.sites.filter(entry => discoveredSite(entry, state.adventure))) {
      $('choices').append(button(SITE_TITLES[site.id], () => {
        try {
          const route = routeTo(map, committed, site.approach);
          travelPreview = { path: route.cells, cells: route.cells, cost: route.cost, destination: SITE_TITLES[site.id] };
          render();
        } catch (error) { say(error.message); }
      }, false, `travel-site:${site.id}`));
    }
    const confirmRoute = button(travelAction.label, () => {
      if (!travelPreview) { say('Preview a route before confirming.'); return; }
      if (travelPreview.cost > state.adventure.moves) { say(routeLimitCopy); return; }
      const from = [state.adventure.x, state.adventure.y];
      const path = travelPreview.path;
      const moves = state.adventure.moves;
      act('MOVE', { path });
      if (state.adventure.moves < moves) {
        travelMotion = { points: [from, ...path], started: motionTime, duration: Math.max(0.35, path.length * 0.45) };
        travelPreview = null;
        if (adventurePanelRequested) setPanel(false);
        render();
      }
    }, !travelPreview || routeBlocked, 'confirm-route', true);
    if (travelAction.bridgeId) confirmRoute.setAttribute('data-crossing-id', travelAction.bridgeId);
    confirmRoute.hidden = !travelPreview;
    $('choices').append(confirmRoute);
    const clearRoute = button('Clear preview', () => { travelPreview = null; render(); }, !travelPreview, 'clear-preview');
    clearRoute.hidden = !travelPreview;
    $('choices').append(clearRoute);
    const routeControl = $('dock').querySelector('[data-choice="confirm-route"]');
    if (routeControl) {
      routeControl.hidden = !travelPreview;
      routeControl.classList.add('icon-medallion');
      routeControl.setAttribute('aria-label', travelPreview
        ? routeBlocked
          ? `Cannot ${travelAction.action.toLowerCase()} · ${routeLimitCopy}`
          : `${travelAction.action} · cost ${travelPreview.cost} · ${movesLabel} available`
        : 'Confirm route');
      routeControl.title = travelPreview
        ? routeBlocked ? routeLimitCopy : `${travelAction.action} · cost ${travelPreview.cost} · ${movesLabel} available`
        : 'Preview a route before confirming';
      if (travelAction.bridgeId) routeControl.setAttribute('data-crossing-id', travelAction.bridgeId);
      routeControl.replaceChildren(glyph('M4 12 L9 17 L20 5 L22 7 L9 21 L2 14 Z'));
      if (frameFit.crossingFocus && travelAction.bridgeId === frameFit.crossingFocus.bridgeId) {
        routeControl.classList.add('crossing-confirm-action');
        const label = document.createElement('span');
        label.className = 'crossing-action-label';
        label.textContent = travelAction.action;
        routeControl.append(label);
      } else routeControl.classList.remove('crossing-confirm-action');
      if (travelPreview) { const badge = document.createElement('span'); badge.className = 'action-badge'; badge.textContent = String(travelPreview.cost); routeControl.append(badge); }
    }
    if (travelPreview && !$('panel').classList.contains('open')) dockIcon('Cancel route', 'Clear the preview without spending movement', 'M5 4 L12 10 L19 4 L21 6 L14 12 L21 18 L19 20 L12 14 L5 20 L3 18 L10 12 L3 6 Z', () => { travelPreview = null; render(); }, false, 'cancel-route');
    $('choices').append(button('Rest · spend 1 move to restore mana', () => { travelPreview = null; act('REST', {}); }, state.adventure.moves < 1, 'rest'));
    $('choices').append(button('End day · Restore daily movement', () => { travelPreview = null; act('END_DAY', {}); }, false, 'adventure-end-day', state.adventure.moves === 0));
    const approach = geo.sites.find(site => site.id === 'town').approach;
    const atApproach = state.adventure.x === approach[0] && state.adventure.y === approach[1];
    const returnReason = state.adventure.pendingEncounter ? 'Clear the guard before returning.' : atApproach ? '' : 'Reach the town approach first.';
    $('choices').append(button(returnReason ? `Return — ${returnReason}` : 'Return to town', () => { travelMotion = null; act('RETURN_TOWN', {}); view = 'kingdom'; render(); }, Boolean(returnReason), 'return-town', true));
    const returnControl = $('dock').querySelector('[data-choice="return-town"]');
    if (returnControl) { returnControl.classList.add('icon-medallion'); returnControl.setAttribute('aria-label', returnReason ? `Return — ${returnReason}` : 'Return to town'); returnControl.replaceChildren(glyph(navGlyphs.kingdom)); }
    if (state.adventure.pendingEncounter && !state.battle) $('choices').append(button('Fight the guard', () => { travelMotion = null; act('BEGIN_ENCOUNTER', {}); if (state.battle) { view = 'tactical'; render(); } }, false, 'begin-encounter', true));
    const preview = travelPreview ? ` Preview cost ${travelPreview.cost}. Confirm spends that cost once.` : '';
    const dwellingLine = atDwelling ? (state.dwelling && !state.dwelling.claimed ? ` The dwelling offers ${state.dwelling.count} ${data.CREATURES[state.dwelling.type].n}.` : ' A creature dwelling is here. Ask for an offer.') : '';
    const travelRule = geo.blocked.length
      ? (geo.bridges.length
        ? `${geo.bridges.length} marked water crossing${geo.bridges.length === 1 ? '' : 's'} ${geo.bridges.length === 1 ? 'connects' : 'connect'} the traversable banks. Site footprints stay blocked.`
        : 'Deep water is blocked; follow the connected island routes. Site footprints stay blocked.')
      : 'This world has no blocked water channel; site footprints stay blocked.';
    say((state.adventure.pendingEncounter ? 'An unresolved guard is waiting. Movement stays spent until that guard is cleared.' : `Road steps cost 1. ${travelRule}`) + preview + dwellingLine + cue());
  } else if (!worldOnly) {
    paintAdventureSites();
    sceneStatus(campaignWorld?.title || 'Beyond the gates', 'Leave town to explore. Discover landmarks, meet guards and find creatures.', 'adventure-town');
    $('selected').textContent = campaignWorld?.title || 'Adventure';
    $('choices').append(button('Leave town', () => { clip = 'walk'; travelPreview = null; travelMotion = null; act('ENTER_ADVENTURE', {}); }, false, 'enter-adventure', true));
    const remaining = state.adventure ? state.adventure.moves : dailyMoves(state, data);
    const line = state.adventure
      ? `Saved movement is ${remaining}. Leaving town again does not refill it.`
      : `Daily movement is ${remaining}. Leave town to spend it on the road.`;
    say(line + cue());
  }
}

const classChoiceOpen = () => Boolean(state) && !valleyEntered && !state.story.flags.enteredValley && state.hero.xp === 0 && !state.inventory.length && !Object.values(state.hero.equip).some(Boolean) && !state.adventure && !state.battle;
function sceneCopy(text, name) {
  const node = document.createElement('p');
  node.textContent = text;
  if (name) node.setAttribute('data-' + name.replace(/[A-Z]/g, character => '-' + character.toLowerCase()), '1');
  return node;
}
function slotMark(slot) {
  return {
    helm: 'M8 16 V11 Q8 4 12 4 Q16 4 16 11 V16 Z',
    weapon: 'M11 3 H13 V15 L17 21 H7 L11 15 Z',
    offhand: 'M12 3 L18 7 V13 Q12 20 6 13 V7 Z',
    armor: 'M6 7 L12 3 L18 7 V17 H6 Z',
    boots: 'M6 6 H13 V13 H18 V18 H6 Z',
    accessory: 'M12 5 A3.5 3.5 0 1 0 11.9 5 Z',
  }[slot];
}
function heroSlotButton(slot) {
  const item = state.hero.equip[slot];
  const node = button('', () => { selectedHeroSlot = slot; setPanel(true); render(); }, false, `scene-hero-slot:${slot}`);
  node.dataset.heroSlot = slot;
  node.dataset.worn = item ? '1' : '0';
  const displayTitle = item ? itemTitle(item) : slotName[slot];
  node.dataset.slotTitle = displayTitle;
  node.title = `${slotName[slot]} · ${item ? itemTitle(item) : 'Empty'}`;
  node.setAttribute('aria-label', `${slotName[slot]}: ${item ? itemTitle(item) : 'Empty'}`);
  const icon = item ? selectGearIcon(gearIcons.icons, slot, item) : null;
  if (icon?.file) {
    const img = document.createElement('img');
    img.src = icon.file;
    img.setAttribute('href', icon.file);
    img.alt = '';
    img.dataset.gearIcon = icon.id;
    node.append(img);
  } else {
    const preview = selectGearIcon(gearIcons.icons, slot, { kind: 'gear', slot, age: state.age, quality: 0 });
    if (preview?.file) {
      const art = document.createElement('img');
      art.src = preview.file;
      art.alt = '';
      art.className = 'socket-ghost';
      node.append(art);
    } else node.append(glyph(slotMark(slot)));
    const empty = document.createElement('span');
    empty.className = 'socket-empty';
    empty.setAttribute('aria-hidden', 'true');
    empty.textContent = '+';
    node.append(empty);
  }
  const label = document.createElement('span');
  label.className = 'hero-slot-label';
  label.setAttribute('data-slot-title', '');
  label.textContent = displayTitle;
  node.append(label);
  return node;
}
function mountHeroChrome() {
  const host = $('scene-ui');
  if (heroDetailTab === 'spells' && !selectedHeroSlot && state?.adventureWorldId && !classChoiceOpen()) {
    host.hidden = true;
    host.className = '';
    host.replaceChildren();
    return;
  }
  host.hidden = false;
  host.className = 'hero';
  const left = document.createElement('div');
  left.className = 'col equipment-left';
  const mid = document.createElement('div');
  mid.className = 'copy';
  const right = document.createElement('div');
  right.className = 'col equipment-right';
  const classId = state.hero.class;
  const era = kitEra(state.age);
  const classOpen = classChoiceOpen();
  const inventoryMode = heroDetailTab === 'inventory' && !classOpen;
  host.dataset.heroDetailTab = inventoryMode ? 'inventory' : heroDetailTab;
  const heroNote = sceneCopy(`${data.CLASSES[classId].n} · Level ${state.hero.level}`, 'kitNote');
  mid.append(heroNote);
  host.dataset.classChoice = classOpen ? 'true' : 'false';
  let inventorySlots = null;
  if (classOpen) {
    left.classList.add('portraits');
    for (const id of Object.keys(data.CLASSES)) {
      const node = button('', () => act('SET_CLASS', { class: id }), false, `scene-class:${id}`);
      node.classList.add('portrait-choice');
      node.dataset.classCard = id;
      node.dataset.current = id === classId ? '1' : '0';
      node.setAttribute('aria-label', data.CLASSES[id].n);
      if (id === classId) node.setAttribute('aria-current', 'true');
      const reviewedPortrait = portraitCard(id, state.age);
      const card = reviewedPortrait || heroBody(id, state.age) || pendingPortrait(id, state.age);
      if (card?.file) {
        const img = document.createElement('img');
        img.src = card.file;
        img.alt = '';
        if (!reviewedPortrait) img.className = 'portrait-body-crop';
        node.append(img);
      } else node.append(glyph(navGlyphs.hero));
      const label = document.createElement('span');
      label.className = 'portrait-choice-label';
      label.setAttribute('aria-hidden', 'true');
      label.textContent = data.CLASSES[id].n;
      node.append(label);
      left.append(node);
    }
    const valleyLabel = valleyEntered ? 'Return to the kingdom' : 'Enter the valley';
    right.append(button(valleyLabel, () => { valleyEntered = true; state.story.flags.enteredValley = true; view = 'kingdom'; persist(); render(); }, false, 'scene-enter-valley'));
  } else if (inventoryMode) {
    inventorySlots = document.createElement('div');
    inventorySlots.className = 'hero-inventory-slots';
    inventorySlots.setAttribute('aria-label', 'Six equipment slots');
    GEAR_SLOTS.forEach((slot, index) => {
      const socket = heroSlotButton(slot);
      socket.dataset.slotNumber = String(index + 1);
      socket.dataset.slotName = slotName[slot];
      inventorySlots.append(socket);
    });
  } else {
    GEAR_SLOTS.slice(0, 3).forEach(slot => left.append(heroSlotButton(slot)));
    GEAR_SLOTS.slice(3).forEach(slot => right.append(heroSlotButton(slot)));
  }
  const stats = heroStats(state, data);
  heroNote.dataset.mobileSummary = `${data.CLASSES[classId].n} · Lv ${state.hero.level}\nATK ${stats.atk} · DEF ${stats.def} · PWR ${stats.pow} · KNO ${stats.kno}\nMP ${state.hero.mana}/${manaMax(state, data)} · XP ${state.hero.xp} · ${state.hero.points} pts`;
  mid.append(sceneCopy(`ATK ${stats.atk} · DEF ${stats.def} · PWR ${stats.pow} · KNO ${stats.kno}`, 'stat'));
  mid.append(sceneCopy(`Mana ${state.hero.mana}/${manaMax(state, data)} · XP ${state.hero.xp} · ${state.hero.points} points`, 'progress'));
  if (inventoryMode) {
    const back = button('', () => {
      heroDetailTab = 'skills';
      selectedHeroSlot = null;
      setPanel(false);
      render();
    }, false, 'hero-inventory-back');
    back.classList.add('hero-inventory-back');
    back.setAttribute('aria-label', 'Back to Hero details');
    back.title = 'Back to Hero details';
    back.append(glyph(headerGlyphs.back));
    host.replaceChildren(inventorySlots, mid, back, buildHeroInventoryPanel());
  }
  else host.replaceChildren(left, mid, right);
}
function paintHero() {
  const world = $('world');
  const campaignWorld = adventureWorlds.find(entry => entry.id === state?.adventureWorldId);
  const terrainFile = campaignMapImage(campaignWorld);
  if (heroDetailTab === 'spells' && !selectedHeroSlot && terrainFile && !classChoiceOpen()) {
    const stageField = $('stage-field');
    stageField.classList.add('hero-spellbook-context');
    stageField.style.setProperty('--spellbook-world-image', `url("${new URL(terrainFile, document.baseURI).href}")`);
    $('terrain').alt = `${campaignWorld.title} campaign world behind the Spellbook`;
    world.dataset.screen = 'hero-spellbook';
    world.dataset.heroContext = 'adventure';
    world.dataset.adventureWorldId = campaignWorld.id;
    world.dataset.adventureTerrainFile = terrainFile;
    world.setAttribute('aria-label', `${campaignWorld.title} campaign world behind the Spellbook`);
    world.setAttribute('pointer-events', 'none');
    return;
  }
  drawHeroRoom(world, element, {
    state, data, slotName,
    cssScale: frameFit.fit.scale || 1,
    portraitCard, pendingPortrait,
    inventoryMode: heroDetailTab === 'inventory' && !classChoiceOpen(),
  });
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
function statProjection(item) {
  const before = heroStats(state, data);
  const worn = state.hero.equip[item.slot];
  const next = { ...before };
  const remove = worn ? (worn.kind === 'gear' ? gearBonus(worn) : (data.ARTIFACTS[worn.artifactId]?.b || {})) : {};
  const add = item.kind === 'gear' ? gearBonus(item) : (data.ARTIFACTS[item.artifactId]?.b || {});
  for (const key of ['atk', 'def', 'pow', 'kno']) {
    next[key] = before[key] - (remove[key] || 0) + (add[key] || 0);
  }
  return ['atk', 'def', 'pow', 'kno'].filter(key => next[key] !== before[key]).map(key => `${key} ${before[key]} to ${next[key]}`).join(', ') || 'stats unchanged';
}
function currentHeroInventoryItem() {
  const selected = state.inventory.find(item => item.id === heroInventorySelectedId) || state.inventory[0] || null;
  heroInventorySelectedId = selected?.id || null;
  return selected;
}
function appendHeroInventoryDetails(host, item) {
  const detail = document.createElement('section');
  detail.className = 'hero-inventory-detail';
  detail.setAttribute('aria-label', item ? `Selected ${itemTitle(item)}` : 'Selected inventory item');
  if (!item) {
    const empty = document.createElement('p');
    empty.className = 'hero-inventory-empty';
    empty.textContent = 'No carried items. Items found or crafted appear here.';
    detail.append(empty);
    host.append(detail);
    return;
  }
  const icon = selectGearIcon(gearIcons.icons, item.slot, item);
  if (icon?.file) {
    const image = document.createElement('img');
    image.src = icon.file;
    image.alt = '';
    image.className = 'hero-inventory-selected-icon';
    detail.append(image);
  }
  const copy = document.createElement('div');
  copy.className = 'hero-inventory-selected-copy';
  const title = document.createElement('h3');
  title.textContent = itemTitle(item);
  const identity = document.createElement('p');
  const itemAge = Number.isInteger(item.age) ? data.AGES[item.age]?.n : 'Artifact';
  identity.textContent = `${slotName[item.slot] || item.slot || 'Artifact'} · ${itemAge}`;
  const bonus = document.createElement('p');
  bonus.textContent = `Effects · ${bonusText(item)}`;
  const projection = document.createElement('p');
  projection.textContent = `Compared with worn gear · ${statProjection(item)}`;
  const worn = item.slot ? state.hero.equip[item.slot] : null;
  const wornLine = document.createElement('p');
  wornLine.textContent = `Equipped · ${itemTitle(worn)}`;
  copy.append(title, identity, bonus, projection, wornLine);
  detail.append(copy);
  const actions = document.createElement('div');
  actions.className = 'hero-inventory-actions';
  if (item.slot && GEAR_SLOTS.includes(item.slot)) {
    actions.append(button('Equip', () => act('EQUIP', { itemId: item.id }), false, `hero-inventory-equip:${item.id}`));
    if (worn) actions.append(button(`Unequip ${slotName[item.slot]}`, () => act('UNEQUIP', { slot: item.slot }), false, `hero-inventory-unequip:${item.slot}`));
    actions.append(button('Compare in Forge', () => { forgePreview = item.id; forgeSlot = item.slot; view = 'forge'; render(); }, false, `hero-inventory-compare:${item.id}`));
  }
  detail.append(actions);
  host.append(detail);
}
function buildHeroInventoryPanel() {
  const panel = document.createElement('section');
  panel.className = 'hero-inventory-panel';
  panel.setAttribute('aria-label', 'Armory inventory');
  const heading = document.createElement('header');
  heading.className = 'hero-inventory-heading';
  const title = document.createElement('h2');
  title.textContent = 'Armory';
  const count = document.createElement('span');
  count.textContent = `${state.inventory.length} carried ${state.inventory.length === 1 ? 'item' : 'items'}`;
  const tabs = document.createElement('div');
  tabs.className = 'hero-inventory-shortcuts';
  tabs.append(
    button('Skills', () => { heroDetailTab = 'skills'; setPanel(true); render(); }, false, 'hero-inventory-skills'),
    button('Spellbook', () => { heroDetailTab = 'spells'; setPanel(true); render(); }, false, 'hero-inventory-spells'),
  );
  heading.append(title, count, tabs);
  const grid = document.createElement('div');
  grid.className = 'hero-inventory-grid';
  grid.setAttribute('aria-label', 'Carried equipment');
  if (!state.inventory.length) {
    const empty = document.createElement('p');
    empty.className = 'hero-inventory-empty';
    empty.textContent = 'No carried items yet.';
    grid.append(empty);
  }
  for (const item of state.inventory) {
    const selected = item.id === currentHeroInventoryItem()?.id;
    const icon = selectGearIcon(gearIcons.icons, item.slot, item);
    const card = button('', () => {
      heroInventorySelectedId = item.id;
      selectedHeroSlot = null;
      setPanel(true);
      render();
    }, false, `hero-inventory:${item.id}`);
    card.className = 'hero-inventory-card';
    card.setAttribute('aria-label', `${itemTitle(item)}. ${bonusText(item)}. ${statProjection(item)}. Select for details.`);
    card.setAttribute('aria-pressed', String(selected));
    if (icon?.file) {
      const image = document.createElement('img');
      image.src = icon.file;
      image.alt = '';
      card.append(image);
    }
    const itemName = document.createElement('span');
    itemName.textContent = itemTitle(item);
    const itemBonus = document.createElement('small');
    itemBonus.textContent = bonusText(item);
    card.append(itemName, itemBonus);
    grid.append(card);
  }
  const selectedItem = currentHeroInventoryItem();
  panel.append(heading, grid);
  appendHeroInventoryDetails(panel, selectedItem);
  return panel;
}
function hero() {
  clearWorld();
  const stats = heroStats(state, data);
  $('selected').textContent = data.CLASSES[state.hero.class].n;
  paintHero();
  mountHeroChrome();
  if (selectedHeroSlot && !classChoiceOpen()) {
    $('selected').textContent = slotName[selectedHeroSlot];
    const item = state.hero.equip[selectedHeroSlot];
    choiceHeading(slotName[selectedHeroSlot]);
    $('choices').append(sceneCopy(item ? `${itemTitle(item)}. ${bonusText(item)}.` : 'This equipment socket is empty.', 'equipment-detail'));
    if (item) $('choices').append(button('Unequip', () => act('UNEQUIP', { slot: selectedHeroSlot }), false, `hero-unequip:${selectedHeroSlot}`));
    for (const carried of state.inventory.filter(entry => entry.slot === selectedHeroSlot)) {
      $('choices').append(button(`Compare ${itemTitle(carried)}`, () => { forgePreview = carried.id; forgeSlot = selectedHeroSlot; view = 'forge'; render(); }, false, `hero-compare:${carried.id}`));
    }
    $('choices').append(button('Open forge', () => { forgeSlot = selectedHeroSlot; view = 'forge'; render(); }, false, `hero-forge:${selectedHeroSlot}`));
    $('choices').append(button('Back to Hero details', () => { selectedHeroSlot = null; setPanel(true); render(); }, false, 'hero-slot-details-back'));
    return;
  }
  const classOpen = classChoiceOpen();
  if (classOpen) {
    const ids = Object.keys(data.CLASSES);
    choiceHeading('Class');
    for (const id of ids) $('choices').append(button(data.CLASSES[id].n, () => act('SET_CLASS', { class: id }), false, `class:${id}`));
    const valleyLabel = valleyEntered ? 'Return to the kingdom' : 'Enter the valley';
    $('choices').append(button(valleyLabel, () => { valleyEntered = true; state.story.flags.enteredValley = true; view = 'kingdom'; persist(); render(); }, false, 'enter-valley'));
  }
  const offer = state.hero.offers.find(item => !item.chosen && !item.declined);
  if (!classOpen) {
    const tabs = document.createElement('div');
    tabs.className = 'hero-detail-tabs';
    tabs.setAttribute('role', 'group');
    tabs.setAttribute('aria-label', 'Hero details');
    for (const [id, label] of [['skills', 'Skill tree'], ['spells', 'Spellbook'], ['inventory', 'Inventory']]) {
      const node = button(label, () => { heroDetailTab = id; setPanel(id !== 'inventory'); render(); }, false, `hero-tab:${id}`);
      node.classList.add('hero-detail-tab');
      node.setAttribute('aria-pressed', String(heroDetailTab === id));
      tabs.append(node);
    }
    $('choices').append(tabs);
    if (heroDetailTab === 'inventory') {
      appendHeroInventoryDetails($('choices'), currentHeroInventoryItem());
    } else if (heroDetailTab === 'skills') {
      if (state.hero.points > 0) {
        choiceHeading(`Attribute points · ${state.hero.points}`);
        const statGrid = document.createElement('div');
        statGrid.className = 'hero-stat-grid';
        const statNames = { atk: 'Attack', def: 'Defense', pow: 'Power', kno: 'Knowledge' };
        for (const stat of Object.keys(statNames)) {
          const node = button(`${statNames[stat]} +1`, () => act('SPEND_POINT', { stat }), false, `spend:${stat}`);
          node.classList.add('hero-stat-point');
          node.setAttribute('aria-label', `Spend one attribute point on ${statNames[stat]}; current ${stats[stat]}`);
          statGrid.append(node);
        }
        $('choices').append(statGrid);
      }
      choiceHeading('Skills');
      const skills = document.createElement('div');
      skills.className = 'sigil-grid hero-sigil-grid';
      const detailId = SKILL_IDS.includes(heroSkillDetailId) ? heroSkillDetailId : 'offense';
      const detail = document.createElement('section');
      detail.className = 'hero-skill-detail';
      detail.dataset.skillDetail = detailId;
      detail.setAttribute('role', 'status');
      detail.setAttribute('aria-live', 'polite');
      const detailTitle = document.createElement('h3');
      const detailCopy = document.createElement('p');
      const updateSkillDetail = id => {
        heroSkillDetailId = id;
        const selected = data.SKILLS[id];
        const selectedLevel = state.hero.skills[id];
        const offered = offer?.choices.includes(id) && selectedLevel < 3;
        const stateCopy = heroSkillStateCopy(selectedLevel, offered);
        detail.dataset.skillDetail = id;
        detailTitle.textContent = selected.n + ' · ' + stateCopy;
        detailCopy.textContent = `${selected.d}${id === 'leadership' ? ' Positive morale grants one immediate bonus action per stack each round: 4.2% per morale point, capped at 12.6%; bonus actions cannot chain or Wait.' : ''}`;
        for (const card of skills.querySelectorAll('button.sigil')) card.removeAttribute('aria-current');
        skills.querySelector(`[data-choice="skill:${CSS.escape(id)}"]`)?.setAttribute('aria-current', 'true');
      };
      for (const id of SKILL_IDS) {
        const skill = data.SKILLS[id];
        const level = state.hero.skills[id];
        const offered = offer?.choices.includes(id) && level < 3;
        const node = button('', () => {
          updateSkillDetail(id);
          detail.scrollIntoView({ block: 'nearest' });
          if (offered) previewAction('CHOOSE_SKILL', { skill: id }, `Learn ${skill.n}`, {}, `${skill.d} Rank ${level} → ${level + 1}. This consumes the saved skill offer; primary stat points stay unchanged.`, `skill:${id}`);
        }, false, `skill:${id}`);
        node.classList.add('sigil');
        node.dataset.skillOffer = offered ? 'available' : 'not-offered';
        node.dataset.skillState = offered ? 'available' : level > 0 ? 'learned' : 'not-offered';
        if (id === detailId) node.setAttribute('aria-current', 'true');
        const cardStateCopy = heroSkillStateCopy(level, offered);
        node.setAttribute('aria-label', skill.n + '. ' + cardStateCopy + ' ' + skill.d);
        const img = document.createElement('img');
        img.src = `assets/derivatives/image-residual-executor-20261007/environment/icons/skills/skill-${id}.png`;
        img.alt = '';
        const offerBadge = offered ? document.createElement('span') : null;
        if (offerBadge) {
          offerBadge.className = 'sigil-offer-badge';
          offerBadge.textContent = 'OFFER';
        }
        const rank = document.createElement('span');
        rank.className = 'sigil-rank';
        rank.textContent = `${level}/3`;
        const name = document.createElement('span');
        name.className = 'sigil-name';
        name.textContent = skill.n;
        node.append(img, ...(offerBadge ? [offerBadge] : []), name, rank);
        skills.append(node);
      }
      $('choices').append(skills);
      updateSkillDetail(detailId);
      detail.append(detailTitle, detailCopy);
      $('choices').append(detail);
      if (offer) $('choices').append(button('Decline skill offer', () => act('DECLINE_SKILL', {}), false, 'decline-skill'));
    } else {
      const wisdom = state.hero.skills.wisdom || 0;
      const currentMana = state.hero.mana;
      const maximumMana = manaMax(state, data);
      choiceHeading('Spellbook · Mana ' + currentMana + '/' + maximumMana);
      const spellHeading = $('choices').lastElementChild;
      spellHeading.classList.add('spellbook-heading');
      spellHeading.dataset.spellFeedback = 'empty';
      spellHeading.setAttribute('role', 'status');
      spellHeading.setAttribute('aria-live', 'polite');
      const spells = document.createElement('div');
      spells.className = 'sigil-grid hero-sigil-grid hero-spell-grid';
      spells.dataset.spellFeedback = 'empty';
      for (const [id, spell] of Object.entries(data.SPELLS)) {
        const eligible = spell.lv <= 1 + wisdom;
        const hasMana = currentMana >= spell.mana;
        const feedbackState = !eligible ? 'locked' : hasMana ? 'available' : 'low-mana';
        const manaCopy = 'Mana ' + currentMana + '/' + maximumMana + '; spell cost ' + spell.mana;
        const effect = spellEffect(id, stats.pow);
        const node = button('', () => {
          spells.dataset.spellFeedback = 'selected';
          for (const card of spells.querySelectorAll('button.sigil')) card.removeAttribute('aria-current');
          node.setAttribute('aria-current', 'true');
          spellHeading.dataset.spellFeedback = feedbackState;
          const availability = !eligible
            ? 'Locked · Requires Wisdom ' + (spell.lv - 1)
            : hasMana ? 'Available in battle' : 'Unlocked · Not enough mana';
          spellHeading.textContent = spell.n + ' · ' + availability + ' · ' + manaCopy + ' · ' + spell.d + (effect == null ? '' : ' · Effect ' + effect);
        }, false, 'spell:' + id);
        node.dataset.spellState = feedbackState;
        if (!eligible) node.setAttribute('aria-disabled', 'true');
        node.classList.add('sigil');
        const availability = !eligible
          ? 'Locked until Wisdom ' + (spell.lv - 1) + '.'
          : hasMana ? 'Unlocked and mana is sufficient.' : 'Unlocked but current mana is insufficient.';
        node.setAttribute('aria-label', spell.n + '. ' + spell.d + ' ' + availability + ' Current mana ' + currentMana + ' of ' + maximumMana + '; spell cost ' + spell.mana + '.');
        const img = document.createElement('img');
        img.src = 'assets/derivatives/image-residual-executor-20261007/environment/icons/spells/spell-' + id + '.png';
        img.alt = '';
        const stateBadge = !eligible || !hasMana ? document.createElement('span') : null;
        if (stateBadge) {
          stateBadge.className = 'sigil-lock-badge';
          stateBadge.textContent = eligible ? 'LOW MP' : 'WIS ' + (spell.lv - 1);
        }
        const rank = document.createElement('span');
        rank.className = 'sigil-rank';
        rank.textContent = String(spell.mana);
        const name = document.createElement('span');
        name.className = 'sigil-name';
        name.textContent = spell.n;
        node.append(img, ...(stateBadge ? [stateBadge] : []), name, rank);
        spells.append(node);
      }
      $('choices').append(spells);
    }
  }
  const equipped = GEAR_SLOTS.map(slot => `${slotName[slot]}: ${itemTitle(state.hero.equip[slot])}`).join('; ');
  const offerLine = offer ? ` ${blocked.skills}` : '';
  say(`Attack ${stats.atk}, Defense ${stats.def}, Power ${stats.pow}, Knowledge ${stats.kno}. Mana ${state.hero.mana}/${manaMax(state, data)}. Daily moves ${dailyMoves(state, data)}. Points ${state.hero.points}. ${equipped}.${offerLine}`);
}

function armyCard(src, caption, capCss, attrs, onSelect = null) {
  const card = onSelect ? button('', onSelect, false, attrs['data-stack-caption'] ? `roster:${attrs['data-stack-caption']}` : `catalog:${attrs['data-plate-review']}`) : document.createElement('div');
  card.className = 'board-card';
  if (onSelect) card.setAttribute('aria-label', caption);
  if (src) {
    const img = document.createElement('img');
    img.src = src;
    img.alt = '';
    img.dataset.plate = src;
    const cap = Number.isFinite(capCss) && capCss > 0 ? capCss : 116;
    img.style.height = `min(calc(100% - 1.65em), ${cap}px)`;
    img.style.maxHeight = `min(calc(100% - 1.65em), ${cap}px)`;
    card.append(img);
  }
  const span = document.createElement('span');
  if (attrs['data-stack-caption']) span.className = 'roster-unit-label';
  span.textContent = caption;
  for (const [key, value] of Object.entries(attrs)) span.setAttribute(key, value);
  card.append(span);
  return card;
}
function plateCap(plate, fallback) {
  if (Number.isFinite(plate?.maxVisibleCssPx) && plate.maxVisibleCssPx > 0) return plate.maxVisibleCssPx;
  if (Number.isFinite(plate?.staticMaxHeight) && plate.staticMaxHeight > 0) return plate.staticMaxHeight;
  return fallback;
}
function paintArmy() {
  const world = $('world');
  world.setAttribute('data-roster', '1');
  world.setAttribute('data-army-layout', 'screen');
  const board = $('board');
  if (!board) return;
  board.dataset.armyLayout = 'screen';
  const tutorialRecruitKey = !state.tutorial?.skipped && state.tutorial?.step === 4 ? String(state.id) + ':4' : '';
  if (tutorialRecruitKey !== armyTutorialDefaultedFor) {
    armyTutorialDefaultedFor = tutorialRecruitKey;
    if (tutorialRecruitKey) {
      plateReviewAge = state.age;
      const roleHasStack = role => state.army.some(stack => stack.kind === 'role' && stack.type === role && stack.age === state.age);
      const canRecruit = role => Object.entries(recruitCost(data, role, state.age)).every(([key, amount]) => state.resources[key] >= amount);
      const hasCapacity = state.army.length < 2 + levelOf('barracks');
      const roles = ['melee', 'ranged', 'heavy'];
      const nextRole = roles.find(role => hasCapacity && !roleHasStack(role) && canRecruit(role))
        ?? roles.find(role => roleHasStack(role) && canRecruit(role))
        ?? (hasCapacity ? roles.find(role => !roleHasStack(role)) : roles.find(roleHasStack));
      if (nextRole) {
        selectedRecruitRole = nextRole;
        armyCatalogOpen = true;
        selectedCodexCreature = '';
      }
    }
  }
  const reviewAge = plateReviewAge == null ? state.age : plateReviewAge;
  const selectedStack = rosterSelection(state.army, selectedArmyId);
  selectedArmyId = selectedStack?.id || null;
  const currentRecruitmentStack = state.army.find(stack => stack.kind === 'role' && stack.type === selectedRecruitRole && stack.age === reviewAge) || null;
  const rosterFocusStack = armyCatalogOpen ? currentRecruitmentStack : selectedStack;
  // Use a roster-specific candidate when one exists; otherwise retain the age's current setting.
  const ground = selection.kingdomTerrain[ages[reviewAge]];
  const groundFile = ground?.displayFile || ground?.sourceFile;
  const armyBackdrop = ARMY_BACKDROPS[reviewAge];
  if (groundFile && !armyBackdrop) {
    world.append(element('image', { href: groundFile, x: -260, y: -40, width: 1896, height: 848, preserveAspectRatio: 'xMidYMid slice', opacity: '0.42' }));
  }
  const chamber = armyBackdrop || (reviewAge === 3 ? CHAMBER_BACKDROPS.garrison : groundFile);
  if (chamber) {
    world.append(element('image', { href: chamber, x: -260, y: -40, width: 1896, height: 848, preserveAspectRatio: 'xMidYMid slice', opacity: armyBackdrop ? '0.98' : '0.85', 'data-chamber-backdrop': armyBackdrop ? 'army-muster' : 'garrison' }));
  }
  board.style.backgroundImage = chamber
    ? `linear-gradient(180deg, rgba(12, 17, 21, 0.04) 0%, rgba(12, 17, 21, 0.14) 100%), url("${chamber}")`
    : '';
  board.style.backgroundSize = 'cover';
  board.style.backgroundPosition = 'center 35%';
  board.dataset.armyGround = armyBackdrop || groundFile || 'none';

  const showcase = document.createElement('section');
  showcase.className = 'army-showcase';
  showcase.setAttribute('aria-label', `Available formations in the ${data.AGES[reviewAge].n}`);
  const showcaseTitle = document.createElement('p');
  showcaseTitle.className = 'army-showcase-title';
  showcaseTitle.textContent = `Muster · ${data.AGES[reviewAge].n}`;
  const showcaseUnits = document.createElement('div');
  showcaseUnits.className = 'army-showcase-units';
  for (const role of ['melee', 'ranged', 'heavy']) {
    let plate = troopPlate(reviewAge, role);
    if (!plate?.file) {
      const body = heroBody(ROLE_RIG[role], reviewAge);
      if (body?.file) plate = { file: body.file };
    }
    const roleName = data.ROLES[role].names[reviewAge];
    const model = document.createElement('button');
    model.type = 'button';
    model.className = 'army-showcase-unit';
    model.dataset.armyShowcaseRole = role;
    model.dataset.choice = `army-showcase:${role}`;
    model.setAttribute('aria-label', `${data.AGES[reviewAge].n} ${roleName}. Select recruitment details.`);
    model.setAttribute('aria-pressed', String(armyCatalogOpen && selectedRecruitRole === role));
    model.addEventListener('click', () => { selectedRecruitRole = role; armyCatalogOpen = true; selectedCodexCreature = ''; render(); });
    if (plate?.file) {
      const image = document.createElement('img');
      image.src = plate.file;
      image.alt = '';
      image.draggable = false;
      image.dataset.musterPlate = `${reviewAge}-${role}`;
      model.append(image);
    }
    const name = document.createElement('span');
    name.textContent = roleName;
    model.append(name);
    showcaseUnits.append(model);
  }
  showcase.append(showcaseTitle, showcaseUnits);

  const review = document.createElement('div');
  review.className = 'board-row';
  review.dataset.armyRow = 'review';
  for (const role of ['melee', 'ranged', 'heavy']) {
    let plate = troopPlate(reviewAge, role);
    if (!plate?.file) {
      const classId = ROLE_RIG[role];
      const body = heroBody(classId, reviewAge);
      if (body?.file) {
        plate = { file: body.file, maxVisibleCssPx: 130, staticMaxHeight: 130 };
      }
    }
    const roleName = data.ROLES[role].names[reviewAge];
    const reviewCaption = roleName;
    const card = armyCard(plate?.file || '', reviewCaption, 116, {
      'data-plate-review': `${reviewAge}-${role}`,
    }, () => { selectedRecruitRole = role; armyCatalogOpen = true; selectedCodexCreature = ''; render(); });
    card.setAttribute('aria-label', `${data.AGES[reviewAge].n} ${roleName}. Select to view recruitment details.`);
    card.setAttribute('aria-pressed', String(armyCatalogOpen && selectedRecruitRole === role));
    review.append(card);
  }
  const roster = document.createElement('div');
  roster.className = 'board-row';
  roster.dataset.armyRow = 'roster';
  review.style.gridTemplateColumns = `repeat(${review.children.length}, minmax(0, 1fr))`;
  for (const stack of state.army) {
    let plate = plateForStack(stack);
    if (!plate?.file && stack.kind === 'role') {
      const classId = ROLE_RIG[stack.type];
      const body = heroBody(classId, stack.age ?? state.age);
      if (body?.file) {
        plate = { file: body.file, maxVisibleCssPx: 130, staticMaxHeight: 130 };
      }
    }
    const fullCaption = stackTitle(stack, data);
    // Rank is already represented by the stars on the roster card. Keep the
    // compact visual title on one line while the button name carries the rank.
    const caption = fullCaption.replace(/ rank \d+$/, '');
    const card = armyCard(plate?.file || '', caption, 130, {
      'data-stack-caption': stack.id,
      ...(plate?.semanticLimit ? { 'data-semantic-limit': plate.semanticLimit } : {}),
    }, () => { selectedArmyId = stack.id; armyCatalogOpen = false; selectedCodexCreature = ''; render(); });
    const rank = document.createElement('span');
    rank.className = 'roster-rank-stars';
    rank.setAttribute('aria-hidden', 'true');
    rank.textContent = armyRankStars(stack.rank);
    card.dataset.rosterRank = String(stack.rank);
    card.setAttribute('aria-label', `${caption}. Rank ${stack.rank} of 4 stars.`);
    if (stack.id === rosterFocusStack?.id) card.dataset.rosterFocus = 'true';
    card.insertBefore(rank, card.lastElementChild);
    card.setAttribute('aria-pressed', String(!armyCatalogOpen && selectedStack?.id === stack.id));
    roster.append(card);
  }
  const ageLabel = document.createElement('p');
  ageLabel.className = 'army-recruitment-kicker';
  const recruitCue = state.tutorial?.step === 4 && !state.tutorial.skipped ? cue().trim() : '';
  ageLabel.textContent = recruitCue || `Recruitment · ${data.AGES[reviewAge].n}`;
  if (recruitCue) ageLabel.dataset.tutorialCue = 'recruit';
  const capacity = armyRosterCapacity(state.army.length, 2 + levelOf('barracks'));
  const rosterShelf = document.createElement('section');
  rosterShelf.className = 'army-roster-shelf';
  rosterShelf.setAttribute('aria-label', 'Your army roster');
  const rosterLabel = document.createElement('div');
  rosterLabel.className = 'roster-capacity';
  rosterLabel.textContent = `Your army · ${state.army.length} / ${2 + levelOf('barracks')} formations`;
  const meter = document.createElement('div');
  meter.className = 'roster-capacity-meter';
  meter.setAttribute('role', 'progressbar');
  meter.setAttribute('aria-label', 'Formation capacity');
  meter.setAttribute('aria-valuemin', '0');
  meter.setAttribute('aria-valuemax', String(capacity.max));
  meter.setAttribute('aria-valuenow', String(capacity.value));
  meter.setAttribute('aria-valuetext', capacity.label);
  const fill = document.createElement('span');
  fill.className = 'roster-capacity-fill';
  fill.style.width = `${capacity.ratio * 100}%`;
  meter.append(fill);
  rosterLabel.append(meter);
  rosterShelf.append(rosterLabel, roster);
  const codex = document.createElement('section');
  codex.className = 'army-creature-codex';
  codex.setAttribute('aria-label', `Creature Codex · ${data.AGES[state.age].n}`);
  const codexTitle = document.createElement('h2');
  codexTitle.className = 'army-creature-codex-title';
  codexTitle.textContent = 'Codex';
  const codexGrid = document.createElement('div');
  codexGrid.className = 'army-creature-codex-grid';
  const availableCreatures = new Set(dwellingPool(data, state.age));
  const codexCompactNames = { 'Dire Wolf': 'Wolf', 'Cave Bear': 'Bear', 'Stone Golem': 'Golem', 'Drone Swarm': 'Drone' };
  for (const [type, creature] of Object.entries(data.CREATURES)) {
    const unlocked = availableCreatures.has(type);
    const earliestAge = data.AGES.findIndex((_, age) => dwellingPool(data, age).includes(type));
    const owned = state.army.filter(stack => stack.kind === 'creature' && stack.type === type).reduce((sum, stack) => sum + stack.count, 0);
    const stateLabel = owned ? `Army ×${owned}` : unlocked ? 'Available at a dwelling' : `Unlocks in ${data.AGES[earliestAge].n}`;
    const card = button('', () => { selectedCodexCreature = type; armyCatalogOpen = false; render(); }, false, `army-codex:${type}`);
    card.classList.add('army-codex-creature');
    card.dataset.creatureType = type;
    card.dataset.codexState = owned ? 'owned' : unlocked ? 'available' : 'locked';
    card.setAttribute('aria-label', `${creature.n}. Tier ${creature.t}. ${stateLabel}. Select details; recruitment remains at eligible dwellings.`);
    card.setAttribute('aria-pressed', String(selectedCodexCreature === type));
    const plate = creaturePlate(type);
    if (plate?.file) {
      const image = document.createElement('img');
      image.src = plate.file;
      image.alt = '';
      image.draggable = false;
      card.append(image);
    }
    const name = document.createElement('span');
    name.textContent = codexCompactNames[creature.n] || creature.n;
    name.title = creature.n;
    const status = document.createElement('small');
    status.textContent = owned ? `×${owned}` : unlocked ? 'Available' : 'Locked';
    card.append(name, status);
    codexGrid.append(card);
  }
  codex.append(codexTitle, codexGrid);
  const detail = document.createElement('section');
  detail.className = 'roster-inspector';
  detail.setAttribute('aria-label', 'Recruitment and selected formation');
  detail.append(ageLabel, review);
  const codexSelected = Boolean(selectedCodexCreature && data.CREATURES[selectedCodexCreature]);
  const ownedCodexCount = codexSelected
    ? state.army.filter(stack => stack.kind === 'creature' && stack.type === selectedCodexCreature).reduce((sum, stack) => sum + stack.count, 0)
    : 0;
  const unlockAge = codexSelected ? data.AGES.findIndex((_, age) => dwellingPool(data, age).includes(selectedCodexCreature)) : -1;
  const codexAvailable = codexSelected && availableCreatures.has(selectedCodexCreature);
  const subject = codexSelected
    ? { kind: 'creature', type: selectedCodexCreature, age: state.age, rank: 0, xp: 0, count: Math.max(1, ownedCodexCount) }
    : armyCatalogOpen ? { kind: 'role', type: selectedRecruitRole, age: reviewAge, rank: 0, xp: 0, count: 5 } : selectedStack;
  const existingRecruitmentStack = subject?.kind === 'role'
    ? state.army.find(stack => stack.kind === 'role' && stack.type === subject.type && stack.age === subject.age)
    : null;
  if (subject) {
    const stats = unitStats(subject, data);
    const heading = document.createElement('h2');
    heading.textContent = subject.kind === 'role' ? data.ROLES[subject.type].names[subject.age] : data.CREATURES[subject.type].n;
    const identity = document.createElement('p');
    identity.className = 'roster-identity';
    identity.textContent = codexSelected
      ? `Tier ${data.CREATURES[subject.type].t} · ${codexAvailable ? `Available at a ${data.AGES[state.age].n} dwelling` : `Unlocks in ${data.AGES[unlockAge].n}`} · ${ownedCodexCount ? `Army ×${ownedCodexCount}` : 'Not recruited'}`
      : armyCatalogOpen
        ? `${data.AGES[reviewAge].n} · ${existingRecruitmentStack ? `Reinforce ${data.ROLES[subject.type].names[subject.age]}` : 'Recruit five'}`
        : `${subject.count} troops · Rank ${subject.rank} · ${subject.xp} XP`;
    const values = document.createElement('dl');
    for (const [name, value] of [['Attack', stats.atk], ['Defense', stats.def], ['Damage', `${stats.dmin}–${stats.dmax}`], ['Health', stats.hp], ['Speed', stats.spd], ['Movement', stats.fly ? 'Flying' : 'Ground']]) {
      const metric = document.createElement('div');
      metric.className = 'roster-stat';
      const term = document.createElement('dt');
      const amount = document.createElement('dd');
      term.textContent = name;
      amount.textContent = String(value);
      metric.append(term, amount);
      values.append(metric);
    }
    detail.append(heading, identity);
    if (subject.kind === 'role' && subject.age === state.age) {
      const payment = recruitCost(data, subject.type, state.age);
      const full = state.army.length >= 2 + levelOf('barracks') && !state.army.some(stack => stack.kind === 'role' && stack.type === subject.type && stack.age === state.age);
      const affordable = Object.entries(payment).every(([key, amount]) => state.resources[key] >= amount);
      const reason = levelOf('barracks') < 1 ? 'Build a Barracks in your Kingdom.' : full ? 'Upgrade the Barracks for more formation slots.' : !affordable ? 'Not enough resources.' : '';
      const recruit = costButton(existingRecruitmentStack ? 'Reinforce +5' : 'Recruit 5', payment, () => act('RECRUIT', { role: subject.type }), Boolean(reason), `muster-recruit:${subject.type}`, false, reason);
      detail.append(recruit);
      if (reason) detail.append(sceneCopy(reason, 'recruit-reason'));
      detail.append(values);
    }
  } else detail.append(sceneCopy('Your army is empty. Build a Barracks and recruit a formation.', 'empty-army'));
  board.replaceChildren(showcase, rosterShelf, codex, detail);
  const focusCard = roster.querySelector('.board-card[data-roster-focus="true"]');
  if (focusCard) {
    const rowBounds = roster.getBoundingClientRect();
    const cardBounds = focusCard.getBoundingClientRect();
    if (cardBounds.left < rowBounds.left) roster.scrollLeft -= rowBounds.left - cardBounds.left;
    else if (cardBounds.right > rowBounds.right) roster.scrollLeft += cardBounds.right - rowBounds.right;
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
    const existingRecruitmentStack = state.army.some(stack => stack.kind === 'role' && stack.type === role && stack.age === state.age);
    const payment = recruitCost(data, role, state.age);
    const short = Object.entries(payment).filter(([key, amount]) => state.resources[key] < amount).map(([key, amount]) => `${Math.ceil(amount - state.resources[key])} ${key}`);
    const noBarracks = levelOf('barracks') < 1;
    const full = state.army.length >= capacity && !state.army.some(stack => stack.kind === 'role' && stack.type === role && stack.age === state.age);
    const reason = noBarracks ? 'Barracks required.' : full ? 'Roster is full.' : short.length ? `Need ${short.join(', ')}.` : '';
    const actionLabel = existingRecruitmentStack ? `Reinforce +5 ${data.ROLES[role].n}` : `Recruit 5 ${data.ROLES[role].n}`;
    $('choices').append(costButton(actionLabel, payment, () => act('RECRUIT', { role }), noBarracks || full || short.length > 0, `recruit:${role}`, false, reason));
  }
  for (const [type, creature] of Object.entries(data.CREATURES)) {
    $('choices').append(button(creature.n, () => {
      selectedCodexCreature = type;
      armyCatalogOpen = false;
      render();
    }, false, `codex:${type}`));
  }
  if (auditMode) {
    const reviewAge = plateReviewAge == null ? state.age : plateReviewAge;
    $('choices').append(button(`Show ${data.AGES[(reviewAge + 7) % 8].n} units`, () => { plateReviewAge = (reviewAge + 7) % 8; render(); }, false, 'plate-review-prev'));
    $('choices').append(button(`Show ${data.AGES[(reviewAge + 1) % 8].n} units`, () => { plateReviewAge = (reviewAge + 1) % 8; render(); }, false, 'plate-review-next'));
  }
  say(`Army ${state.army.length}/${capacity}. Capacity is 2 plus Barracks level. Recruitment pays five of the current age.${cue()}`);
}

// Forge (reference 22-forge): smithy backdrop, a state-derived workpiece on the anvil,
// recipe cost and worn-versus-next comparison, and six compact equipment slots.
function paintForge(previewItem = null, previewRole = 'none') {
  const world = $('world');
  const defs = element('defs', {});
  const wall = element('linearGradient', { id: 'forge-wall', x1: 0, y1: 0, x2: 0, y2: 1 });
  wall.append(element('stop', { offset: '0', 'stop-color': '#17130f' }), element('stop', { offset: '1', 'stop-color': '#3a2a1e' }));
  const ember = element('radialGradient', { id: 'forge-ember', cx: '0.48', cy: '0.58', r: '0.52' });
  ember.append(element('stop', { offset: '0', 'stop-color': '#f08a2c', 'stop-opacity': '0.38' }), element('stop', { offset: '1', 'stop-color': '#e07a2a', 'stop-opacity': '0' }));
  defs.append(wall, ember);
  world.append(defs);
  world.append(element('rect', { x: -260, y: -40, width: 1896, height: 848, fill: 'url(#forge-wall)', 'data-backdrop': 'native-svg-smithy' }));
  if (CHAMBER_BACKDROPS.forge) {
    world.append(element('image', {
      href: CHAMBER_BACKDROPS.forge,
      x: -510,
      y: -40,
      width: 1896,
      height: 848,
      preserveAspectRatio: 'xMidYMid slice',
      opacity: '0.96',
      'data-chamber-backdrop': 'forge',
    }));
  }
  world.append(element('rect', { x: -260, y: -40, width: 1896, height: 848, fill: 'url(#forge-ember)' }));
  const previewArt = previewItem?.slot === 'weapon' && previewItem.kind === 'gear'
    ? forgeWeaponPreviewArt(previewItem.age)
    : null;
  const pose = previewArt ? forgeWeaponPreviewPose(previewItem.age) : null;
  if (previewArt && pose) {
    const roleLabel = previewRole === 'craft'
      ? 'Crafting preview; this weapon is not owned yet.'
      : previewRole === 'carried'
        ? `Preview of carried ${itemTitle(previewItem)}.`
        : `Preview of equipped ${itemTitle(previewItem)}.`;
    world.append(element('image', {
      href: previewArt,
      x: pose.x,
      y: pose.y,
      width: pose.width,
      height: pose.height,
      transform: `rotate(${pose.rotation} ${pose.x + pose.width / 2} ${pose.y + pose.height / 2})`,
      preserveAspectRatio: 'xMidYMid meet',
      role: 'img',
      'aria-label': roleLabel,
      'data-forge-preview': previewRole,
      'data-forge-preview-age': previewItem.age,
      'data-forge-preview-slot': previewItem.slot,
    }));
  }
}
function mountForgeChrome(offer, offerError) {
  const host = $('scene-ui');
  host.hidden = false;
  host.className = 'forge';
  const copy = document.createElement('div');
  copy.className = 'copy';
  const worn = state.hero.equip[forgeSlot];
  const nextItem = offer ? { kind: 'gear', slot: forgeSlot, age: state.age, quality: offer.quality } : null;
  const costText = offer ? Object.entries(offer.cost).map(([key, amount]) => `${amount} ${key}`).join(', ') : 'Armory required';
  copy.append(sceneCopy('Forge', 'forgeTitle'));
  const availability = offer
    ? sceneCopy(`Armory level ${levelOf('armory')}. ${data.AGES[state.age].n} patterns. Best quality ${data.QUAL[offer.cap]?.n}.`, 'forgeOffer')
    : sceneCopy(`${(offerError || 'Armory required').replace(/[.!?]+$/, '')}. Build an Armory in the Kingdom to craft gear.`, 'forgeOffer');
  if (!offer) availability.dataset.forgeGate = 'locked';
  copy.append(availability);
  const selectedItem = state.inventory.find(item => item.id === forgePreview) || null;
  const previewItem = selectedItem || nextItem || worn;
  const previewIcon = previewItem ? selectGearIcon(gearIcons.icons, forgeSlot, previewItem) : null;
  if (previewIcon?.file) {
    const image = document.createElement('img');
    image.src = previewIcon.file;
    image.alt = itemTitle(previewItem);
    image.className = 'forge-item-preview';
    image.dataset.gearIcon = previewIcon.id;
    copy.append(image);
  }
  if (selectedItem) {
    copy.append(sceneCopy(`Selected: ${itemTitle(selectedItem)}. ${bonusText(selectedItem)}. Worn: ${itemTitle(worn)}. ${statProjection(selectedItem)}.`, 'forgeSelected'));
  } else {
    copy.append(sceneCopy(`${slotName[forgeSlot]}. Next piece: ${nextItem ? itemTitle(nextItem) : 'none'}. Cost: ${costText}.`, 'forgeNext'));
    copy.append(sceneCopy(`Gain: ${nextItem ? bonusText(nextItem) : 'none'}. Worn: ${itemTitle(worn)} (${bonusText(worn)}).`, 'forgeWorn'));
  }
  const slots = document.createElement('div');
  slots.className = 'col forge-slots';
  for (const slot of GEAR_SLOTS) {
    const item = state.hero.equip[slot];
    const node = button('', () => { forgeSlot = slot; render(); }, false, `scene-forge-slot:${slot}`);
    node.dataset.slot = slot;
    node.dataset.worn = item ? '1' : '0';
    node.dataset.selected = slot === forgeSlot ? '1' : '0';
    if (slot === forgeSlot) node.setAttribute('aria-current', 'true');
    const icon = selectGearIcon(gearIcons.icons, slot, item);
    if (icon?.file && item) {
      const img = document.createElement('img');
      img.src = icon.file;
      img.setAttribute('href', icon.file);
      img.alt = '';
      img.dataset.gearIcon = icon.id;
      img.dataset.gearAge = String(item.age);
      node.append(img);
    } else {
      const preview = selectGearIcon(gearIcons.icons, slot, { kind: 'gear', slot, age: state.age, quality: 0 });
      if (preview?.file) {
        const img = document.createElement('img');
        img.src = preview.file;
        img.setAttribute('href', preview.file);
        img.alt = '';
        img.className = 'slot-preview-art';
        img.dataset.slotPreview = slot;
        node.append(img);
      } else {
        node.append(glyph(slotMark(slot)));
      }
    }
    node.setAttribute('aria-label', `${slotName[slot]}: ${item ? itemTitle(item) : 'Empty'}`);
    const label = document.createElement('span');
    label.className = 'forge-slot-label';
    label.textContent = slot === 'accessory' ? 'Acc.' : slotName[slot];
    label.setAttribute('aria-hidden', 'true');
    node.append(label);
    slots.append(node);
  }
  const inventory = document.createElement('section');
  inventory.className = 'forge-inventory';
  inventory.dataset.empty = String(state.inventory.length === 0);
  inventory.setAttribute('aria-label', 'Carried equipment');
  const inventoryHeading = document.createElement('h3');
  inventoryHeading.textContent = `Carried equipment · ${state.inventory.length}`;
  inventory.append(inventoryHeading);
  if (!state.inventory.length) {
    const empty = document.createElement('p');
    empty.className = 'forge-inventory-empty';
    empty.textContent = 'No carried gear yet. Craft a piece here or find equipment on the adventure map.';
    inventory.append(empty);
    copy.append(sceneCopy('No carried gear is stored yet. Crafted or discovered pieces appear here.', 'forgeInventoryStatus'));
  } else {
    const grid = document.createElement('div');
    grid.className = 'forge-inventory-grid';
    for (const item of state.inventory) {
      const selected = item.id === forgePreview;
      const node = button('', () => {
        forgePreview = item.id;
        forgeSlot = GEAR_SLOTS.includes(item.slot) ? item.slot : 'accessory';
        render();
      }, false, `inventory-item:${item.id}`);
      node.className = 'forge-inventory-card';
      node.dataset.itemId = item.id;
      node.dataset.selected = selected ? '1' : '0';
      node.dataset.quality = String(item.quality ?? 'artifact');
      node.setAttribute('aria-label', `Compare ${itemTitle(item)}. ${bonusText(item)}. ${selected ? 'Selected.' : 'Select to compare.'}`);
      if (selected) node.setAttribute('aria-current', 'true');
      const itemIcon = selectGearIcon(gearIcons.icons, item.slot, item);
      if (itemIcon?.file) {
        const img = document.createElement('img');
        img.src = itemIcon.file;
        img.alt = '';
        img.dataset.gearIcon = itemIcon.id;
        img.dataset.gearAge = String(item.age);
        node.append(img);
      } else {
        const mark = document.createElement('span');
        mark.className = 'forge-inventory-fallback';
        mark.setAttribute('aria-hidden', 'true');
        mark.textContent = slotName[item.slot] || 'Relic';
        node.append(mark);
      }
      const identity = document.createElement('span');
      identity.className = 'forge-item-identity';
      identity.textContent = itemTitle(item);
      const provenance = document.createElement('small');
      provenance.className = 'forge-item-provenance';
      provenance.textContent = `${data.AGES[item.age]?.n || 'Relic'} · ${slotName[item.slot] || 'Artifact'}`;
      node.append(identity, provenance);
      grid.append(node);
    }
    inventory.append(grid);
  }
  host.replaceChildren(copy, slots, inventory);
}
function forge() {
  clearWorld();
  $('selected').textContent = 'Forge';
  let offer = null;
  let offerError = '';
  try { offer = forgeOffer(state.age, levelOf('armory'), null); }
  catch (error) { offerError = error.message; }
  $('app').dataset.forgeLocked = String(!offer);
  let preview = state.inventory.find(item => item.id === forgePreview) || null;
  if (forgePreview && !preview) forgePreview = null;
  const equippedPreview = state.hero.equip[forgeSlot];
  const nextItem = offer ? { kind: 'gear', slot: forgeSlot, age: state.age, quality: offer.quality } : null;
  const displayedItem = preview || nextItem || equippedPreview;
  const displayRole = preview ? 'carried' : nextItem ? 'craft' : equippedPreview ? 'equipped' : 'none';
  paintForge(displayedItem, displayRole);
  mountForgeChrome(offer, offerError);
  const hasEquipment = state.inventory.length > 0 || GEAR_SLOTS.some(slot => Boolean(state.hero.equip[slot]));
  if (!offer && !preview) {
    choiceHeading('Armory required');
    $('choices').append(sceneCopy('Build an Armory in your Kingdom to unlock crafting.', 'forge-locked-copy'));
    $('choices').append(button('Return to Kingdom', () => { view = 'kingdom'; setPanel(false); render(); }, false, 'forge-return-kingdom'));
  }
  if (preview) {
    choiceHeading('Selected comparison');
    const summary = document.createElement('article');
    summary.className = 'forge-selected-summary';
    summary.id = 'forge-selected-summary';
    summary.dataset.forgeSelected = preview.id;
    const icon = selectGearIcon(gearIcons.icons, preview.slot, preview);
    if (icon?.file) {
      const image = document.createElement('img');
      image.src = icon.file;
      image.alt = '';
      image.dataset.gearIcon = icon.id;
      summary.append(image);
    }
    const detail = document.createElement('div');
    detail.className = 'forge-selected-detail';
    const name = document.createElement('strong');
    name.textContent = itemTitle(preview);
    const bonus = document.createElement('span');
    bonus.textContent = bonusText(preview);
    const comparison = document.createElement('small');
    comparison.textContent = `Worn: ${itemTitle(state.hero.equip[preview.slot])} · ${statProjection(preview)}`;
    detail.append(name, bonus, comparison);
    summary.append(detail);
    $('choices').append(summary);
    const decision = document.createElement('div');
    decision.className = 'forge-decision';
    decision.dataset.forgeDecision = '1';
    const confirm = button(`Equip ${itemTitle(preview)}`, () => {
      forgePreview = null;
      act('EQUIP', { itemId: preview.id });
    }, false, `equip-confirm:${preview.id}`, true);
    confirm.setAttribute('aria-describedby', summary.id);
    decision.append(confirm);
    if (state.hero.equip[preview.slot]) {
      decision.append(button(`Unequip ${slotName[preview.slot]}`, () => act('UNEQUIP', { slot: preview.slot }), false, `forge-unequip:${preview.slot}`, true));
    }
    decision.append(button('Cancel comparison', () => { forgePreview = null; render(); }, false, 'equip-cancel'));
    $('choices').append(decision);
  } else {
    if (hasEquipment && state.hero.equip[forgeSlot]) {
      $('choices').append(button(`Unequip ${slotName[forgeSlot]}`, () => act('UNEQUIP', { slot: forgeSlot }), false, `forge-unequip:${forgeSlot}`, true));
    }
    if (offer) {
      choiceHeading('Forge menu');
      const named = data.GEAR[forgeSlot]?.names?.[state.age] || slotName[forgeSlot];
      const nextItem = { kind: 'gear', slot: forgeSlot, age: state.age, quality: offer.quality };
      const quality = data.QUAL[offer.quality]?.n || `quality ${offer.quality}`;
      const summary = document.createElement('article');
      summary.className = 'forge-menu-summary';
      summary.dataset.forgeMenuSummary = forgeSlot;
      const identity = document.createElement('strong');
      identity.textContent = itemTitle(nextItem);
      const meta = document.createElement('span');
      meta.textContent = `${slotName[forgeSlot]} · ${quality}`;
      const comparison = document.createElement('small');
      comparison.textContent = `Gain ${bonusText(nextItem)} · Worn ${itemTitle(state.hero.equip[forgeSlot])}.`;
      summary.append(identity, meta, comparison);
      $('choices').append(summary);

      const armoryLevel = levelOf('armory');
      for (let qualityIndex = 0; qualityIndex <= 3; qualityIndex += 1) {
        const requiredArmory = qualityIndex * 2 + 1;
        const tier = forgeOffer(state.age, Math.max(armoryLevel, requiredArmory), qualityIndex);
        const tierName = data.QUAL[qualityIndex]?.n || `quality ${qualityIndex}`;
        const locked = armoryLevel < requiredArmory;
        const short = Object.entries(tier.cost).filter(([key, amount]) => state.resources[key] < amount).map(([key, amount]) => `${Math.ceil(amount - state.resources[key])} ${key}`);
        const detail = locked ? `Requires Armory level ${requiredArmory}.` : short.length ? `Need ${short.join(', ')}.` : `${bonusText({ kind: 'gear', slot: forgeSlot, age: state.age, quality: qualityIndex })}. The new item goes into your inventory.`;
        const choiceId = qualityIndex === offer.quality ? 'forge-confirm' : `forge-quality:${qualityIndex}`;
        const choice = costButton(`Craft · ${tierName}`, tier.cost, () => previewAction('FORGE', { slot: forgeSlot, quality: qualityIndex }, `Craft ${named} · ${tierName}`, tier.cost, `${bonusText({ kind: 'gear', slot: forgeSlot, age: state.age, quality: qualityIndex })}. The new item goes into your inventory.`, choiceId), locked || short.length > 0, choiceId, false, detail);
        choice.dataset.forgeQuality = String(qualityIndex);
        choice.dataset.requiredArmory = String(requiredArmory);
        if (qualityIndex === offer.quality) choice.dataset.forgeQualityCurrent = 'true';
        if (locked) choice.dataset.forgeQualityLocked = 'true';
        if (locked) {
          const requirement = document.createElement('small');
          requirement.className = 'forge-tier-requirement';
          requirement.textContent = `Armory level ${requiredArmory}`;
          choice.append(requirement);
        }
        $('choices').append(choice);
      }
    }
  }
  const worn = state.hero.equip[forgeSlot];
  say(preview ? '' : (offer
    ? `Selected ${slotName[forgeSlot]}. Worn ${itemTitle(worn)} (${bonusText(worn)}). Crafting quality: ${data.QUAL[offer.quality]?.n}. Bag holds ${state.inventory.length}.`
    : `Inventory: ${state.inventory.length} items.`));
}

function market() {
  kingdom();
  setPanel(true);
  $('selected').textContent = 'Market';
  if (!marketEditing) {
    choiceHeading('Status');
    $('choices').append(sceneCopy(state.age < 1 ? 'Locked · opens in the Bronze Age.' : 'Market · open', 'market-status'));
    $('choices').append(button('Edit', () => { marketEditing = true; render(); }, false, 'market-edit'));
    say(state.age < 1 ? 'Market opens in the Bronze Age.' : 'Market is open. Edit to trade exact batches of 100.');
    return;
  }
  choiceHeading('Trade · batches of 100');
  $('choices').append(button('Back to Market status', () => { marketEditing = false; render(); }, false, 'market-status-back'));
  const locked = state.age < 1;
  for (const resource of ['food', 'wood', 'stone']) {
    const buy = marketQuote('buy', resource);
    const sell = marketQuote('sell', resource);
    const buyShort = state.resources.gold < buy.spend.gold;
    const sellShort = state.resources[resource] < sell.spend[resource];
    $('choices').append(costButton('Buy 100', buy.spend, () => previewAction('MARKET', { side: 'buy', resource }, 'Buy 100 ' + resource, buy.spend, 'Receive 100 ' + resource + '. Cancel spends nothing.', 'market-buy:' + resource), locked || buyShort, 'market-buy:' + resource, false, locked ? 'Opens in the Bronze Age.' : buyShort ? 'Need more gold.' : 'Buy 100 ' + resource + ' for ' + buy.spend.gold + ' gold.'));
    $('choices').append(costButton('Sell 100', sell.spend, () => previewAction('MARKET', { side: 'sell', resource }, 'Sell 100 ' + resource, sell.spend, 'Receive ' + sell.gain.gold + ' gold. Cancel spends nothing.', 'market-sell:' + resource), locked || sellShort, 'market-sell:' + resource, false, locked ? 'Opens in the Bronze Age.' : sellShort ? 'Need more ' + resource + '.' : 'Sell 100 ' + resource + ' for ' + sell.gain.gold + ' gold.'));
  }
  say(state.age < 1 ? 'The market opens in the Bronze Age.' : 'Batches are exactly 100. Gold is the price, not a traded good.');
}
function board(mode) {
  const world = $('world');
  const geo = contract.geometry[mode], matrix = geo.worldToSource;
  const ground = modeGround(mode);
  world.setAttribute('data-board', ground ? `${mode}-painted-v1` : `${mode}-provisional-v1`);
  world.setAttribute('data-registration', modeScenes.registration);
  if (!ground) {
    world.append(element('rect', { width: 1376, height: 768, fill: mode === 'defense' ? '#243028' : '#2a3328' }));
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
}

const ROLE_RIG = {
  melee: 'knight',
  ranged: 'ranger',
  heavy: 'barbarian',
  support: 'healer',
  brute: 'barbarian',
  runner: 'ranger',
  archer: 'ranger',
  sapper: 'barbarian',
  shaman: 'warlock',
};
function drawJointedRole(world, at, role, clip, { scale = 0.08, reduced = false, worn = null, time = animTime() } = {}) {
  const classId = ROLE_RIG[role];
  if (!classId) return null;
  return drawActor(world, element, classId, {
    x: at[0],
    y: at[1],
    scale,
    clip,
    time,
    reduced,
    worn,
  });
}
function drawFigure(world, origin, stack, alive) {
  const plate = plateForStack(stack);
  const reduced = Boolean(state?.settings?.reducedMotion);
  const battle = state?.battle;
  const event = motionFor(battleEvents, battle?.id, stack.id, motionTime, reduced);
  const figureClip = event?.clip || (!alive ? 'death' : 'idle');
  const clipTime = event?.progress ?? animTime();
  if (event?.kind === 'move' && event.sourceId === stack.id && event.from && event.to) {
    const matrix = contract.geometry.tactical.worldToSource;
    const from = project(matrix, [event.from[0] + .5, event.from[1] + .5]);
    const to = project(matrix, [event.to[0] + .5, event.to[1] + .5]);
    origin = [origin[0] + (from[0] - to[0]) * (1 - event.progress), origin[1] + (from[1] - to[1]) * (1 - event.progress)];
  }
  const figGroup = element('g', {
    'data-stack-id': stack.id,
    'data-stack-side': stack.side || 'p',
    'data-clip': figureClip,
    'pointer-events': 'none',
    ...(event?.targetClip ? { 'data-target-clip': event.targetClip } : {}),
    ...(event?.role ? { 'data-spell-role': event.role } : {}),
    ...(event?.spellId ? { 'data-spell-id': event.spellId } : {}),
    ...(event?.effectCategory ? { 'data-spell-category': event.effectCategory } : {}),
    ...(event?.selfTarget ? { 'data-self-target': '1' } : {}),
  });
  world.append(figGroup);
  if (plate && drawPlate(figGroup, element, plate, origin[0], origin[1] + 8, alive ? 54 : 42, {
    opacity: alive ? 1 : 0.35,
    time: clipTime,
    fly: false,
    clip: figureClip,
    reduced,
  })) return;
  if (stack?.kind === 'role' && drawJointedRole(figGroup, [origin[0], origin[1] + 8], stack.type, figureClip, { reduced: reduced || !alive, time: clipTime })) return;
  figGroup.append(element('circle', { cx: origin[0], cy: origin[1], r: 5, fill: alive ? '#d5b573' : '#6d6458' }));
}

function battleTitle(stack) {
  if ((stack.kind === 'creature' || stack.kind === 'role') && Number.isInteger(stack.rank)) {
    try { return stackTitle(stack, data); } catch { /* Enemy stacks can omit a roster kind. */ }
  }
  const creature = data.CREATURES[stack.type];
  if (creature) return `${creature.n} ×${stack.count}`;
  const named = data.ROLES[stack.type]?.names?.[stack.age ?? state.age];
  return named ? `${named} ×${stack.count}` : `${stack.type || stack.id} ×${stack.count}`;
}
const SPELL_PALETTES = {
  damage: { stroke: '#f07148', fill: '#e0482d38', accent: '#ffd29d', motif: 'damage-impact' },
  buff: { stroke: '#ebd07c', fill: '#d5b57338', accent: '#fff1bf', motif: 'buff-crest' },
  heal: { stroke: '#6ddba0', fill: '#3ca37038', accent: '#d8ffea', motif: 'heal-restoration' },
  debuff: { stroke: '#a984eb', fill: '#6e4cb038', accent: '#e5d4ff', motif: 'debuff-bind' },
};
function spellEffectMotif(spellId, category) {
  if (spellId === 'resurrect') return 'resurrect-crown';
  if (spellId === 'slow') return 'slow-shackle';
  return (SPELL_PALETTES[category] || SPELL_PALETTES.damage).motif;
}

function drawTacticalCommittedFeedback(world, matrix, battle, feedbackEvents) {
  for (const ev of feedbackEvents) {
    if (['spell', 'cast'].includes(ev.kind)) {
      const spellName = data.SPELLS[ev.spellId]?.n || ev.spellId || 'Spell';
      const casterStack = battle.stacks.find(s => s.id === ev.sourceId);
      const casterCoord = casterStack?.x != null
        ? [casterStack.x + 0.5, casterStack.y + 0.5]
        : ev.from ? [ev.from[0] + 0.5, ev.from[1] + 0.5] : null;
      const casterCentre = casterCoord ? project(matrix, casterCoord) : null;
      if (casterCentre) {
        const casterGroup = element('g', {
          class: 'tactical-spell-caster',
          'data-committed-feedback': 'spell',
          'data-source-id': ev.sourceId,
          'data-target-id': ev.targetId || '',
          'data-spell-caster': ev.sourceId,
          'data-spell-id': ev.spellId || 'spell',
          'data-spell-category': ev.effectCategory || 'damage',
          'data-self-target': ev.selfTarget ? '1' : '0',
          'data-reduced-motion': ev.reduced ? '1' : '0',
          'pointer-events': 'none',
        });
        casterGroup.append(element('ellipse', {
          cx: casterCentre[0],
          cy: casterCentre[1] + 6,
          rx: 28,
          ry: 13,
          fill: 'none',
          stroke: '#8ec5ff',
          'stroke-width': 2.2,
          'stroke-dasharray': '5 3',
        }));
        world.append(casterGroup);
      }
      for (const targetEntry of ev.affectedTargets || []) {
        const targetStack = battle.stacks.find(s => s.id === targetEntry.id);
        const targetCoord = targetStack?.x != null
          ? [targetStack.x + 0.5, targetStack.y + 0.5]
          : ev.to ? [ev.to[0] + 0.5, ev.to[1] + 0.5] : null;
        const targetCentre = targetCoord ? project(matrix, targetCoord) : null;
        if (!targetCentre) continue;
        const category = targetEntry.effectCategory || ev.effectCategory || 'damage';
        const palette = SPELL_PALETTES[category] || SPELL_PALETTES.damage;
        const motif = spellEffectMotif(ev.spellId, category);
        const isSelf = Boolean(ev.selfTarget && targetEntry.id === ev.sourceId);
        const effectGroup = element('g', {
          class: 'tactical-spell-effect',
          'data-spell-effect': targetEntry.id,
          'data-spell-caster': ev.sourceId,
          'data-spell-id': ev.spellId || 'spell',
          'data-spell-category': category,
          'data-effect-motif': motif,
          'data-self-target': isSelf ? '1' : '0',
          'data-target-died': targetEntry.targetDied ? '1' : '0',
          'data-reduced-motion': ev.reduced ? '1' : '0',
          'pointer-events': 'none',
        });
        if (!isSelf && casterCentre) {
          effectGroup.append(element('line', {
            x1: casterCentre[0],
            y1: casterCentre[1] - 12,
            x2: targetCentre[0],
            y2: targetCentre[1] - 12,
            stroke: palette.stroke,
            'stroke-width': 2.2,
            'stroke-dasharray': category === 'damage' ? 'none' : '6 4',
            opacity: 0.85,
          }));
        }
        effectGroup.append(element('ellipse', {
          cx: targetCentre[0],
          cy: targetCentre[1] + 4,
          rx: isSelf ? 34 : 30,
          ry: isSelf ? 16 : 14,
          fill: palette.fill,
          stroke: palette.stroke,
          'stroke-width': 2.4,
        }));
        if (category === 'damage') {
          effectGroup.append(element('polygon', {
            'data-motif': 'damage-impact',
            points: `${targetCentre[0]},${targetCentre[1] - 28} ${targetCentre[0] + 8},${targetCentre[1] - 14} ${targetCentre[0] + 22},${targetCentre[1] - 14} ${targetCentre[0] + 10},${targetCentre[1] - 4} ${targetCentre[0] + 14},${targetCentre[1] + 10} ${targetCentre[0]},${targetCentre[1] + 1} ${targetCentre[0] - 14},${targetCentre[1] + 10} ${targetCentre[0] - 10},${targetCentre[1] - 4} ${targetCentre[0] - 22},${targetCentre[1] - 14} ${targetCentre[0] - 8},${targetCentre[1] - 14}`,
            fill: palette.fill,
            stroke: palette.stroke,
            'stroke-width': 1.6,
          }));
        } else if (category === 'buff') {
          effectGroup.append(element('path', {
            'data-motif': 'buff-crest',
            d: `M ${targetCentre[0] - 14} ${targetCentre[1] - 8} L ${targetCentre[0]} ${targetCentre[1] - 22} L ${targetCentre[0] + 14} ${targetCentre[1] - 8} M ${targetCentre[0] - 10} ${targetCentre[1]} L ${targetCentre[0]} ${targetCentre[1] - 12} L ${targetCentre[0] + 10} ${targetCentre[1]}`,
            fill: 'none',
            stroke: palette.stroke,
            'stroke-width': 2.2,
          }));
        } else if (category === 'heal') {
          effectGroup.append(element('path', {
            'data-motif': motif,
            d: `M ${targetCentre[0]} ${targetCentre[1] - 24} V ${targetCentre[1] - 4} M ${targetCentre[0] - 10} ${targetCentre[1] - 14} H ${targetCentre[0] + 10}`,
            fill: 'none',
            stroke: palette.stroke,
            'stroke-width': 2.6,
          }));
        } else {
          effectGroup.append(element('ellipse', {
            'data-motif': motif,
            cx: targetCentre[0],
            cy: targetCentre[1] - 10,
            rx: 20,
            ry: 8,
            fill: 'none',
            stroke: palette.stroke,
            'stroke-width': 2,
            'stroke-dasharray': '4 3',
          }));
        }
        const badgeText = category === 'damage'
          ? `${spellName}${targetEntry.hpDelta < 0 ? ` ${targetEntry.hpDelta} HP` : ''}${targetEntry.targetDied ? ' · Slain' : ''}`
          : category === 'heal'
            ? `${spellName}${targetEntry.hpDelta > 0 ? ` +${targetEntry.hpDelta} HP` : ' · Restored'}`
            : category === 'buff'
              ? `${spellName} · ${ev.spellId === 'haste' ? '+Speed' : 'Bless'}`
              : `${spellName} · Slowed`;
        const badge = element('text', {
          x: targetCentre[0],
          y: targetCentre[1] - 62,
          'text-anchor': 'middle',
          fill: palette.accent,
          'font-size': 11,
          'font-weight': 700,
          'data-spell-badge': ev.spellId || 'spell',
        });
        badge.textContent = badgeText;
        effectGroup.append(badge);
        world.append(effectGroup);
      }
    } else if (ev.reduced) {
      const targetOrActorId = ev.targetId || ev.sourceId;
      const stack = battle.stacks.find(s => s.id === targetOrActorId);
      const coord = stack?.x != null
        ? [stack.x + 0.5, stack.y + 0.5]
        : ev.to ? [ev.to[0] + 0.5, ev.to[1] + 0.5] : null;
      const centre = coord ? project(matrix, coord) : null;
      if (centre) {
        const group = element('g', {
          class: 'tactical-action-feedback',
          'data-committed-feedback': ev.kind,
          'data-source-id': ev.sourceId,
          'data-target-id': ev.targetId || '',
          'data-reduced-motion': '1',
          'pointer-events': 'none',
        });
        group.append(element('ellipse', {
          cx: centre[0],
          cy: centre[1] + 4,
          rx: 26,
          ry: 12,
          fill: 'none',
          stroke: ev.kind === 'move' ? '#b8d6bc' : '#f07148',
          'stroke-width': 2,
          'stroke-dasharray': '4 3',
        }));
        world.append(group);
      }
    }
  }
}

function tactical() {
  const world = $('world');
  const geo = contract.geometry.tactical;
  const matrix = geo.worldToSource;
  const battle = state.battle;
  const deployment = battle?.status === 'PENDING' ? battle.deployment : null;
  const active = battle?.status === 'ACTIVE' ? activeStackId(battle) : null;
  const legal = active ? legalTargets(battle, active) : { melee: [], ranged: [], moves: [] };
  const actor = active ? battle.stacks.find(item => item.id === active) : null;
  const spellState = battle ? battleSpellAvailability(battle, data.SPELLS) : { enabled: false, reason: 'unavailable', detail: 'No cast available (1/round)', offers: [], knownSpells: 0, minSpellMana: null };
  const offers = actor?.side === 'p' ? spellState.offers : [];
  if (battle && battle.id !== tacticalBattleId) {
    tacticalBattleId = battle.id;
    tacticalIntent = null;
    deploymentSelection = deployment?.movableIds[0] ?? null;
    attackModeMenuOpen = false;
    battleEvents = battleEvents.filter(event => event.sessionId === battle.id);
    if (retreatArmed) retreatRestorePending = true;
    retreatArmed = false;
  }
  if (!deployment) deploymentSelection = null;
  else if (!deployment.movableIds.includes(deploymentSelection)) deploymentSelection = deployment.movableIds[0] ?? null;
  if (!actor || actor.side !== 'p' || deployment || battle?.pendingSettlement) attackModeMenuOpen = false;
  if ((!battle || battle.status !== 'ACTIVE') && retreatArmed) {
    retreatRestorePending = true;
    retreatArmed = false;
  }
  if (actor?.side === 'p') tacticalIntent = keepIntent(tacticalIntent, legal, offers.length, Boolean(actor.waited), actor.bonusPending === true);
  const ground = modeGround('tactical');
  world.setAttribute('data-board', ground ? 'tactical-painted-v1' : 'tactical-provisional-v1');
  world.setAttribute('data-registration', modeScenes.registration);
  if (!ground) world.append(element('rect', { width: 1376, height: 768, fill: '#243028' }));
  for (let y = 0; y < geo.rows; y++) for (let x = 0; x < geo.cols; x++) {
    const blockedCell = (geo.blocked ?? []).some(cell => cell[0] === x && cell[1] === y) && !(geo.bridges ?? []).some(bridge => bridge.cells.some(cell => cell[0] === x && cell[1] === y));
    const obstacle = (geo.obstacles ?? []).some(cell => cell[0] === x && cell[1] === y);
    const here = battle?.stacks.some(stack => stack.id === active && stack.x === x && stack.y === y);
    const deploymentOpen = Boolean(deployment && deploymentSelection
      && legalDeploymentCells(battle, deploymentSelection).some(cell => cell[0] === x && cell[1] === y));
    const open = deploymentOpen || Boolean(actor?.side === 'p' && tacticalIntent === 'move' && legal.moves.some(cell => cell[0] === x && cell[1] === y));
    const poly = element('polygon', {
      points: cellPoints(matrix, x, y),
      fill: deploymentOpen ? '#b9d6aa55' : open ? '#b8d6bc24' : here ? '#d5b57333' : 'none',
      stroke: deploymentOpen ? '#ecdfaa' : open ? '#d5e5c577' : here ? '#e6ce91' : 'none',
      'stroke-width': here ? 2 : 0.8,
      'data-cell': `${x},${y}`,
      'data-open': open ? '1' : '0',
      ...(deploymentOpen ? { 'data-kind': 'deployment' } : {}),
    });
    if (!blockedCell && !open && !here && !obstacle) poly.setAttribute('pointer-events', 'none');
    if (open) poly.style.cursor = 'pointer';
    world.append(poly);
  }
  $('selected').textContent = deployment ? 'Tactical deployment' : battle ? `Battle round ${battle.round}` : 'No battle';
  if (!battle) {
    if (!worldOnly) {
      $('choices').append(button('Go to Adventure', () => { view = 'adventure'; render(); }, false, 'go-adventure', true));
      $('choices').append(button('Open War', () => { view = 'war'; render(); }, false, 'go-war', true));
      say('No battle is open. Leave town and fight the valley guard, or open War for a skirmish, duel, siege, endless defense or challenge. Gate strength is ' + gateHp(state) + '.');
    }
    return;
  }
  const committedFeedback = activeCommittedFeedback(battleEvents, battle.id, motionTime, Boolean(state.settings.reducedMotion));
  for (const stack of battle.stacks) {
    const activeMotion = motionFor(battleEvents, battle.id, stack.id, motionTime, state.settings.reducedMotion);
    const inFeedback = committedFeedback.some(ev => ev.sourceId === stack.id || ev.targetId === stack.id || ev.affectedTargets?.some(t => t.id === stack.id));
    if (stack.x == null || (stack.dead && !activeMotion && !inFeedback)) continue;
    const centre = project(matrix, [stack.x + 0.5, stack.y + 0.5]);
    const shown = Math.min(6, Math.max(1, stack.maxCount || stack.count));
    const livingFigures = Math.max(0, Math.min(shown, Math.round(shown * stack.count / (stack.maxCount || stack.count))));
    for (let figure = 0; figure < shown; figure++) {
      const column = figure % 3;
      const row = Math.floor(figure / 3);
      drawFigure(world, [centre[0] + (column - 1) * 21, centre[1] + row * 18], stack, figure < livingFigures);
    }
    if (stack.dead) continue;
    const title = battleTitle(stack);
    const health = stackHealth(stack);
    const actionName = stack.id === active ? (actor?.side === 'p' ? (tacticalIntent || 'choose') : 'acting') : '';
    queueLabel(`${title.replace(/ ×\d+$/, '')}  ${stack.count}`, centre[0], centre[1] - 48, { side: stack.side, priority: stack.id === active ? 1 : 0, health: health.maxHp ? health.hp / health.maxHp : 0, fullText: stackCaption({ title, count: stack.count, hp: health.hp, maxHp: health.maxHp, action: actionName }) });
    const hit = targetSourceSize(frameFit.fit.scale || 1);
    const targetKind = tacticalIntent === 'melee' && legal.melee.includes(stack.id) ? 'melee' : tacticalIntent === 'shoot' && legal.ranged.includes(stack.id) ? 'shoot' : '';
    const targetable = actor?.side === 'p' && stack.id !== active && targetKind;
    if (targetable) {
      const pad = element('rect', {
        x: centre[0] - hit / 2, y: centre[1] - hit / 2, width: hit, height: hit, fill: '#c83e3833', stroke: '#f1e9d9',
        'data-target': stack.id,
        'data-kind': targetKind,
      });
      pad.style.cursor = 'pointer';
      world.append(pad);
    }
  }
  drawTacticalCommittedFeedback(world, matrix, battle, committedFeedback);
  if (worldOnly) return;
  if (battle.status === 'ACTIVE' || deployment) paintTacticalHeroPlaque($('stage-field'), battle);
  else $('stage-field').querySelector('.tactical-hero-plaque')?.remove();
  if (battle.status === 'ACTIVE' || deployment) paintTacticalRoundBadge($('stage-field'), battle);
  else $('stage-field').querySelector('.tactical-round-badge')?.remove();
  const spellAllowanceText = actor?.side === 'p' ? ` · Spell: ${spellState.detail}` : '';
  const status = sceneStatus(deployment ? 'Deployment' : battle.pendingSettlement ? (battle.outcome?.winner === 'p' ? 'Victory' : 'Battle ended') : `Round ${battle.round}`, deployment ? 'Arrange your force before combat.' : battle.pendingSettlement ? 'Review the outcome and return to your campaign.' : actor ? `${battleTitle(actor)} · ${actor.side === 'p' ? 'Your turn' : 'Enemy turn'}${spellAllowanceText}` : 'Preparing the next turn', deployment ? 'battle battle-deployment' : 'battle');
  const statusSubtitle = status.querySelector('p') || status;
  statusSubtitle.dataset.spellAllowance = spellState.reason || (spellState.enabled ? 'available' : 'unavailable');
  const initiative = document.createElement('div');
  initiative.className = 'initiative';
  initiative.setAttribute('aria-label', 'Living formations');
  const ordered = battle.queue.map(id => battle.stacks.find(stack => stack.id === id)).filter(stack => stack && !stack.dead);
  for (const stack of ordered) {
    const plate = plateForStack(stack);
    const token = document.createElement('div');
    token.className = 'initiative-token';
    token.dataset.side = stack.side;
    token.dataset.active = stack.id === active ? 'true' : 'false';
    token.title = battleTitle(stack);
    if (plate?.file) {
      const portrait = document.createElement('img');
      portrait.src = plate.file;
      portrait.alt = battleTitle(stack);
      token.append(portrait);
    }
    const count = document.createElement('b');
    count.textContent = String(stack.count);
    token.append(count);
    initiative.append(token);
  }
  status.append(initiative);
  if (deployment) {
    paintDeploymentTray(status, battle);
    say(`Practice deployment. ${deployment.placedIds.length} of ${deployment.movableIds.length} formations placed. No campaign resources or troops are spent.`);
    return;
  }
  if (battle.pendingSettlement) showCombatResult('tactical');
  if (battle.pendingSettlement) $('choices').append(button('Apply the battle result', () => act('SETTLE_BATTLE', {}), false, 'settle-battle'));
  if (active) {
    const stack = actor;
    if (stack.side !== 'p') {
      say('The opponent is acting.');
      return;
    }
    const spellMeta = {
      spells: offers.length,
      castThisRound: battle.castThisRound,
      mana: battle.mana,
      minSpellMana: spellState.minSpellMana,
      knownSpells: spellState.knownSpells,
    };
    const rows = modeRows({ moves: legal.moves, melee: legal.melee, ranged: legal.ranged, waited: stack.waited, bonus: stack.bonusPending === true, ...spellMeta });
    const attacks = rows.filter(row => ['melee', 'shoot'].includes(row.id) && row.enabled);
    const primary = primaryModeRows({ melee: legal.melee, ranged: legal.ranged, waited: stack.waited, bonus: stack.bonusPending === true, ...spellMeta });
    for (const row of primary) {
      const choiceId = ['attack', 'spell'].includes(row.id) ? `intent:${row.id}` : row.id;
      const choose = () => {
        if (retreatArmed) return;
        if (row.id === 'attack') {
          if (attacks.length === 1) {
            attackModeMenuOpen = false;
            tacticalIntent = attacks[0].id;
            render();
          } else if (attacks.length > 1) {
            attackModeMenuOpen = true;
            setPanel(true);
            render();
          }
          return;
        }
        if (row.id === 'defend') { act('BATTLE', { action: 'defend', stackId: active }); return; }
        if (row.id === 'wait') { act('BATTLE', { action: 'wait', stackId: active }); return; }
        if (row.id === 'skip-bonus') { act('BATTLE', { action: 'skip-bonus', stackId: active }); return; }
        tacticalIntent = row.id;
        if (row.id === 'spell') { attackModeMenuOpen = false; menuSheet = false; setPanel(true); }
        render();
      };
      const marks = {
        move: 'M4 11 H15 L11 7 H14 L20 12 L14 17 H11 L15 13 H4 Z',
        melee: 'M11 2 H13 L14 15 H10 Z M7 15 H17 V18 H7 Z',
        attack: 'M11 2 H13 L14 15 H10 Z M7 15 H17 V18 H7 Z',
        shoot: 'M7 4 Q16 12 7 20 H9 Q15 12 9 4 Z',
        spell: 'M12 2 L14 9 L21 12 L14 15 L12 22 L10 15 L3 12 L10 9 Z',
        defend: 'M12 3 L18 7 V13 Q12 20 6 13 V7 Z',
        wait: 'M12 4 A8 8 0 1 0 11.9 4 Z M11 8 H13 V13 H16 V15 H11 Z',
        auto: 'M6 5 H18 V9 H12 V19 H8 V9 H6 Z',
        retreat: 'M18 6 L8 12 L18 18 V14 H21 V10 H18 Z',
        'skip-bonus': 'M6 6 H9 L18 18 H15 Z M18 6 H15 L6 18 H9 Z',
      };
      const dockNode = button('', choose, !row.enabled, choiceId);
      $('dock').append(dockNode);
      dockNode.classList.add('icon-medallion');
      dockNode.classList.add('tactical-action');
      dockNode.dataset.tacticalAction = row.id;
      if (row.reason) dockNode.dataset.spellReason = row.reason;
      dockNode.setAttribute('aria-label', `${row.label}. ${row.detail}`);
      dockNode.title = row.detail;
      if (ACTION_ART[row.id]) {
        const image = document.createElement('img');
        image.src = ACTION_ART[row.id];
        image.alt = '';
        image.className = 'action-art';
        dockNode.append(image);
      } else dockNode.append(glyph(marks[row.id] || marks.auto));
      const visibleLabel = document.createElement('span');
      visibleLabel.className = 'tactical-action-label';
      visibleLabel.textContent = row.label;
      dockNode.append(visibleLabel);
      if (row.id === tacticalIntent || (row.id === 'attack' && ['melee', 'shoot'].includes(tacticalIntent))) dockNode.setAttribute('aria-pressed', 'true');
    }
    if (attackModeMenuOpen) {
      $('choices').append(button('Cancel attack choice', () => { attackModeMenuOpen = false; setPanel(false); render(); }, false, 'cancel-attack-choice'));
      for (const mode of attacks) {
        const label = mode.id === 'melee' ? `Melee attack · ${legal.melee.length} targets` : `Ranged attack · ${legal.ranged.length} targets`;
        $('choices').append(button(label, () => { attackModeMenuOpen = false; tacticalIntent = mode.id; setPanel(false); render(); }, false, `attack-mode:${mode.id}`));
      }
    }
    if (panel.classList.contains('open')) {
      const secondary = secondaryModeRows({ moves: legal.moves });
      for (const row of secondary) {
        const choose = () => {
          if (row.id === 'auto') { attackModeMenuOpen = false; act('BATTLE', { action: 'auto' }); return; }
          if (row.id === 'retreat') { attackModeMenuOpen = false; retreatArmed = true; focusChoice = 'retreat-cancel'; setPanel(false); render(); return; }
          attackModeMenuOpen = false;
          tacticalIntent = 'move';
          setPanel(false);
          render();
        };
        $('choices').append(button(`${row.label} · ${row.detail}`, choose, !row.enabled, `tactical-more:${row.id}`));
      }
      if (!spellState.enabled) {
        $('choices').append(button(`Spell · ${spellState.detail}`, () => {}, true, 'tactical-more:spell-status'));
      }
    }
    if (tacticalIntent === 'move') {
      for (const cell of legal.moves) $('choices').append(button(moveLabel(cell), () => act('BATTLE', { action: 'move', stackId: active, to: cell }), false, `move:${cell[0]},${cell[1]}`));
    }
    if (tacticalIntent === 'melee') {
      for (const target of legal.melee) {
        const enemy = battle.stacks.find(item => item.id === target);
        const payload = meleeCommand(battle, active, target);
        $('choices').append(button(strikeLabel('melee', battleTitle(enemy), enemy.count), () => act('BATTLE', payload), false, `melee:${target}`));
      }
    }
    if (tacticalIntent === 'shoot') {
      for (const target of legal.ranged) {
        const enemy = battle.stacks.find(item => item.id === target);
        $('choices').append(button(strikeLabel('shoot', battleTitle(enemy), enemy.count), () => act('BATTLE', { action: 'strike', stackId: active, targetId: target }), false, `shoot:${target}`));
      }
    }
    if (tacticalIntent === 'spell') {
      const guidanceNode = sceneCopy('Choose one listed cast. Your hero casts once per battle round.', 'spell-guidance');
      guidanceNode.dataset.spellGuidance = '1';
      $('choices').append(guidanceNode);
      $('choices').append(button('Cancel spell selection', () => {
        tacticalIntent = null;
        setPanel(false);
        render();
      }, false, 'cancel-spell-selection'));
      for (const offer of offers) {
        $('choices').append(button(spellLabel(offer.spell.n, battleTitle(offer.target), offer.spell.mana), () => {
          setPanel(false);
          act('BATTLE', { action: 'spell', spell: offer.spellId, targetId: offer.target.id });
        }, false, `spellcast:${offer.spellId}:${offer.target.id}`));
      }
    }
  }
  const last = battle.log?.[battle.log.length - 1];
  const spellGuidance = actor?.side === 'p' && !spellState.enabled ? ` Spell: ${spellState.detail}.` : '';
  const phase = battle.pendingSettlement ? 'The result is waiting. Apply it once.' : active && actor?.side === 'p' ? intentSentence(tacticalIntent, battleTitle(actor), spellState) : active ? 'The opponent is acting.' : 'The round is changing.';
  const modeLine = actor?.side === 'p' ? modeRows({
    moves: legal.moves,
    melee: legal.melee,
    ranged: legal.ranged,
    spells: offers.length,
    waited: actor.waited,
    bonus: actor.bonusPending === true,
    castThisRound: battle.castThisRound,
    mana: battle.mana,
    minSpellMana: spellState.minSpellMana,
    knownSpells: spellState.knownSpells,
  }).find(row => row.id === tacticalIntent)?.detail : '';
  const lastSpellName = last?.type === 'spell' ? (data.SPELLS[last.id]?.n || last.id || 'spell') : '';
  const moraleLine = last?.type === 'morale' && last.outcome === 'bonus'
    ? `High morale — extra action. Chance ${(last.chance * 100).toFixed(1)}%.`
    : last?.type === 'morale'
      ? 'Morale did not grant an action.'
      : last?.type === 'spell'
        ? `Last action spell (${lastSpellName}).`
        : last
          ? 'Last action ' + last.type + '.'
          : 'No action yet.';
  const bonusLine = actor?.bonusPending ? ' This bonus can Move, Melee, Shoot, Defend or Skip. It cannot Wait or grant another action.' : '';
  say(`${battle.practice} battle, round ${battle.round}. ${battle.stacks.filter(item => !item.dead).length} stacks remain. ${moraleLine} ${phase} ${modeLine || ''}${spellGuidance}${bonusLine}`);
}

function defense() {
  board('defense');
  const session = state.defense;
  const world = $('world');
  const matrix = contract.geometry.defense.worldToSource;
  const markers = session ? defenseMarkers(session) : defensePreparationMarkers(state, data);
  const reduced = Boolean(state?.settings?.reducedMotion);
  const now = animTime();
  for (const tower of markers.towers) {
    const at = project(matrix, tower.at);
    const plate = towerPlate(state.age, tower.fam);
    const towerVisual = element('g', { 'data-tower-instance': tower.id, 'data-tower-family': tower.fam });
    if (!drawPlate(towerVisual, element, plate, at[0], at[1] + 8, 52, { opacity: tower.alive ? 1 : 0.4, time: now, clip: 'idle', reduced })) {
      towerVisual.append(element('rect', { x: at[0] - 12, y: at[1] - 20, width: 24, height: 32, fill: '#8c7447' }));
    }
    world.append(towerVisual);
    const name = data.TOWERS[tower.fam]?.names?.[state.age] || tower.fam;
    queueLabel(name, at[0], at[1] - 28, { side: 'p', health: tower.maxHp ? tower.hp / tower.maxHp : 0, fullText: `${name}. ${Math.max(0, Math.round(tower.hp))} of ${tower.maxHp} HP` });
    const runtime = session?.towers.find(entry => entry.id === tower.id);
    if (runtime && defenseTowerId === tower.id) {
      const points = Array.from({ length: 48 }, (_, index) => {
        const angle = index * Math.PI / 24;
        return project(matrix, [tower.at[0] + Math.cos(angle) * runtime.rng, tower.at[1] + Math.sin(angle) * runtime.rng]).join(',');
      });
      world.append(element('polygon', { points: points.join(' '), fill: '#e8cc7c12', stroke: '#e3ce9a', 'stroke-width': 1.5, 'stroke-dasharray': '4 5', 'pointer-events': 'none', 'data-tower-range': tower.id }));
    }
    if (session) {
      const inspect = element('circle', { cx: at[0], cy: at[1] - 12, r: targetSourceSize(frameFit.fit.scale || 1) * 2 / 3, fill: 'transparent', tabindex: 0, role: 'button', 'aria-label': `Inspect ${name}`, 'data-inspect-tower': tower.id });
      const choose = () => { defenseTowerId = tower.id; setPanel(true); render(); };
      inspect.addEventListener('click', choose);
      inspect.addEventListener('keydown', event => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); choose(); } });
      world.append(inspect);
    }
  }
  for (const enemy of markers.enemies) {
    const at = project(matrix, enemy.at);
    const plate = attackerPlate(state.age, enemy.role);
    const height = enemy.boss ? 64 : 40;
    const walking = enemy.entered && !reduced ? 'walk' : 'idle';
    if (drawPlate(world, element, plate, at[0], at[1] + 6, height, { opacity: enemy.entered ? 1 : 0.45, time: now, clip: 'walk', reduced })) {
      /* The attacker plate is this age's role, not one shared class body. */
    } else if (!drawJointedRole(world, [at[0], at[1] + 6], enemy.role, walking, { scale: enemy.boss ? 0.1 : 0.08, reduced })) {
      world.append(element('circle', { cx: at[0], cy: at[1], r: enemy.boss ? 14 : 8, fill: '#c83e38', opacity: enemy.entered ? 1 : 0.45 }));
    }
    if (enemy.telegraphId) world.append(element('circle', { cx: at[0], cy: at[1], r: 18, fill: 'none', stroke: '#f1e9d9', 'stroke-width': 2 }));
  }
  for (const shot of markers.projectiles) {
    const at = project(matrix, shot.at);
    if (!drawPlate(world, element, projectilePlate(shot.fam), at[0], at[1] + 6, 18, { time: now, clip: 'walk', reduced })) {
      world.append(element('circle', { cx: at[0], cy: at[1], r: 3, fill: '#f1e9d9' }));
    }
  }
  if (markers.army) {
    const at = project(matrix, markers.army.at);
    const stack = state.army.find(item => item.id === markers.army.stackId);
    const armyClip = session?.status === 'ACTIVE' && !session.paused && !reduced ? 'walk' : 'idle';
    if (drawPlate(world, element, plateForStack(stack), at[0], at[1] + 8, 48, { time: now, clip: 'idle', reduced })) {
      /* Deployed stack uses its own age plate. */
    } else if (!(stack?.kind === 'role' && drawJointedRole(world, [at[0], at[1] + 8], stack.type, armyClip, { reduced }))) {
      world.append(element('polygon', { points: `${at[0]},${at[1] - 14} ${at[0] + 12},${at[1] + 10} ${at[0] - 12},${at[1] + 10}`, fill: '#9bb7d0' }));
    }
  }
  if (blastAim && session?.status === 'ACTIVE' && session.heroDeployed) {
    for (let y = 0; y < contract.geometry.defense.rows; y++) {
      for (let x = 0; x < contract.geometry.defense.cols; x++) {
        const cell = element('polygon', {
          points: cellPoints(matrix, x, y),
          fill: '#f0a92e22',
          stroke: '#f1e9d9',
          'data-cell': `${x},${y}`,
          'data-open': '1',
          'data-kind': 'blast',
        });
        cell.style.cursor = 'pointer';
        world.append(cell);
      }
    }
  }
  if (session?.status === 'ACTIVE' && (!session.heroDeployed || !session.armyDeployed)) {
    const occupiedPads = new Set(session.towers.map(tower => tower.siteId).filter(Boolean));
    if (session.heroSite) occupiedPads.add(session.heroSite);
    if (session.army?.siteId) occupiedPads.add(session.army.siteId);
    for (const site of contract.geometry.defense.sites) {
      if (occupiedPads.has(site.id)) continue;
      const [x, y, w, h] = site.rect;
      const pad = element('polygon', {
        points: cellPoints(matrix, x, y, w, h),
        fill: defensePad === site.id ? '#70b9c544' : '#d5b57322',
        stroke: '#e6d3a1',
        'data-defense-pad': site.id,
      });
      pad.style.cursor = 'pointer';
      pad.onclick = event => {
        event.stopPropagation();
        defensePad = site.id;
        render();
      };
      world.append(pad);
    }
  }
  if (markers.hero) {
    const at = project(matrix, markers.hero.at);
    const heroFigure = { x: at[0], y: at[1] + 8, clip: 'idle', time: animTime(), reduced: Boolean(state.settings.reducedMotion), worn: wornKit() };
    if (!drawActor(world, element, state.hero.class, { ...heroFigure, scale: 0.12 }) && !drawBoundActor(world, element, state.hero.class, { ...heroFigure, scale: 0.28 })) {
      groundToken(world, at[0], at[1], state.hero.class);
    }
  }
  if (worldOnly) return;
  const summary = defenseSummary(session);
  if (!session) summary.title = defensePlan === 'endless' ? 'Endless preparation' : 'Siege preparation';
  sceneStatus(summary.title, [summary.wave, summary.core].filter(Boolean).join(' · '), 'battle defense-status');
  if (session?.pendingSettlement) showCombatResult('defense');
  if (session && defenseTowerId) {
    const tower = session.towers.find(entry => entry.id === defenseTowerId);
    if (tower) {
      const name = data.TOWERS[tower.fam]?.names?.[state.age] || tower.fam;
      choiceHeading(name);
      $('choices').append(sceneCopy(`HP ${Math.max(0, Math.round(tower.hp))}/${tower.maxHp} · Range ${tower.rng} · Damage ${tower.dmg}`, 'tower-detail'));
      $('choices').append(button('Close range preview', () => { defenseTowerId = null; render(); }, false, 'tower-range-close'));
    }
  }
  const phaseName = !session ? 'Preparation' : session.pendingSettlement ? (session.winner === 'p' ? 'Victory pending' : 'Defeat pending') : session.paused ? 'Paused' : 'Running';
  $('selected').textContent = session ? `${phaseName} · ${session.practice} · ${defenseWaveLabel(session)} · core ${Math.max(0, Math.round(session.core))}` : `${defensePlan === 'endless' ? 'Endless' : 'Campaign Siege'} preparation`;
  if (session?.status === 'ACTIVE') {
    dockIcon(session.paused ? 'Resume' : 'Pause', session.paused ? 'Resume continues this wave' : 'Pause freezes the attackers', session.paused ? 'M8 5 L18 12 L8 19 Z' : 'M7 5 H10 V19 H7 Z M14 5 H17 V19 H14 Z', () => act('DEFENSE', { paused: !session.paused, dt: 0 }), false, 'defense-pause');
    dockIcon(session.speed === 2 ? 'Speed 1×' : 'Speed 2×', 'Changes how fast the wave advances', session.speed === 2 ? 'M8 6 L14 12 L8 18 Z' : 'M6 6 L11 12 L6 18 Z M12 6 L17 12 L12 18 Z', () => act('DEFENSE', { speed: session.speed === 2 ? 1 : 2, paused: session.paused, dt: 0 }), false, 'defense-speed');
    if (session.heroDeployed) {
      const ready = state.hero.mana >= 40 && (session.heroHp ?? 1) > 0;
      const heroAt = markers.hero?.at;
      dockIcon(ready ? 'Aim hero blast' : 'Hero blast', ready ? '40 mana. Choose a cell.' : 'Need 40 mana', 'M12 2 L14 9 L21 12 L14 15 L12 22 L10 15 L3 12 L10 9 Z', () => { blastAim = ready ? !blastAim : false; render(); }, !ready, 'defense-cast');
      if (ready && heroAt) $('choices').append(button('Blast at the hero', () => { blastAim = false; act('DEFENSE_CAST', { x: heroAt[0], y: heroAt[1] }); }, false, 'defense-cast-hero', true));
    }
    const occupied = new Set(session.towers.map(tower => tower.siteId).filter(Boolean));
    if (session.heroSite) occupied.add(session.heroSite);
    if (session.army?.siteId) occupied.add(session.army.siteId);
    if (!session.heroDeployed || !session.armyDeployed) {
      $('choices').append(button(defensePad ? `Placement ${defensePad}` : 'Placement: the lane', () => { defensePad = ''; render(); }, false, 'defense-pad-lane'));
      for (const site of contract.geometry.defense.sites) {
        if (occupied.has(site.id)) continue;
        $('choices').append(button(defensePad === site.id ? `Selected ${site.id}` : `Place on ${site.id}`, () => { defensePad = site.id; render(); }, false, `defense-pad:${site.id}`));
      }
    }
    if (!session.heroDeployed) {
      $('choices').append(button(defensePad ? `Deploy hero on ${defensePad}` : 'Deploy hero on the lane', () => act('DEPLOY_DEFENSE', defensePad ? { siteId: defensePad } : {}), false, 'deploy-hero', true));
    }
    if (!session.armyDeployed) {
      for (const stack of state.army) {
        $('choices').append(button((defensePad ? `Deploy on ${defensePad} ` : 'Deploy ') + stackTitle(stack, data), () => act('DEPLOY_ARMY', defensePad ? { stackId: stack.id, siteId: defensePad } : { stackId: stack.id }), false, `deploy-army:${stack.id}`, true));
      }
    }
    if (session.practice === 'siege') {
      const wave = session.clearedWaves - 1;
      const ready = wave >= 0 && !session.earlyCalls.includes(wave);
      $('choices').append(button(ready ? `Early call wave ${wave + 1}` : 'Early call — clear a wave first', () => act('EARLY_CALL', {}), !ready, 'early-call'));
    }
  }
  if (session?.pendingSettlement) $('choices').append(button('Apply the defense result', () => act('SETTLE_DEFENSE', {}), false, 'settle-defense'));
  if (!session) {
    choiceHeading('Choose defense');
    for (const [practice, label, detail] of [
      ['siege', 'Campaign Siege', 'Five waves. A settled victory pays campaign rewards.'],
      ['endless', 'Endless', 'The assault continues until the core falls.'],
    ]) {
      const mode = button(label, () => { defensePlan = practice; render(); }, false, `defense-mode:${practice}`);
      mode.classList.add('mode-choice');
      mode.setAttribute('aria-pressed', String(defensePlan === practice));
      mode.title = detail;
      $('choices').append(mode);
    }
    const startChoice = button(defensePlan === 'endless' ? 'Start Endless' : 'Start Campaign Siege', () => startDefense(defensePlan), Boolean(state.battle), defensePlan === 'endless' ? 'start-endless' : 'start-siege');
    startChoice.classList.add('defense-start-action');
    $('choices').append(startChoice);
    $('choices').append(button('Return to War', () => { view = 'war'; render(); }, false, 'defense-back-war'));
    $('choices').append(sceneCopy(defensePlan === 'endless'
      ? 'Endless records each cleared wave and ends only when the core falls.'
      : 'Campaign Siege is a five-wave campaign defense. The result settles once.', 'defense-plan-detail'));
    choiceHeading(`Tower roster · ${state.towers.length}/${2 + levelOf('workshop')}`);
    const room = state.towers.length < 2 + levelOf('workshop');
    for (const family of Object.keys(data.TOWERS)) {
      const owned = state.towers.some(tower => tower.fam === family);
      const payment = towerPurchaseCost(data, family, state.age);
      const short = Object.entries(payment).filter(([key, amount]) => state.resources[key] < amount).map(([key, amount]) => `${Math.ceil(amount - state.resources[key])} ${key}`);
      const reason = owned ? 'That family is already built.' : !room ? 'Siege Workshop level adds a tower slot.' : short.length ? `Need ${short.join(', ')}.` : '';
      $('choices').append(costButton(`Buy ${data.TOWERS[family].n}`, payment, () => act('BUY_TOWER', { family }), owned || !room || short.length > 0, `buy-tower:${family}`, family === 'splash', reason));
    }
    for (const tower of state.towers) {
      if (tower.tier === state.age) continue;
      const multiplier = tower.tier + 1;
      const payment = { wood: 120 * multiplier, stone: 100 * multiplier, gold: 80 * multiplier };
      const short = Object.entries(payment).filter(([key, amount]) => state.resources[key] < amount).map(([key, amount]) => `${Math.ceil(amount - state.resources[key])} ${key}`);
      const reason = short.length ? `Need ${short.join(', ')}.` : `Bring ${data.TOWERS[tower.fam].n} from ${data.AGES[tower.tier].n} to ${data.AGES[state.age].n}.`;
      const name = data.TOWERS[tower.fam]?.names?.[state.age] || data.TOWERS[tower.fam]?.n || tower.fam;
      $('choices').append(costButton(`Retrofit ${name}`, payment, () => act('RETROFIT', { towerId: tower.id }), short.length > 0, `retrofit:${tower.id}`, false, reason));
    }
  }
  const upcoming = markers.queue.slice(0, 6).map(enemy => `${enemy.role}${enemy.boss ? ' boss' : ''}`).join(', ');
  const towerLine = markers.towers.map(tower => `${tower.fam} ${Math.max(0, Math.round(tower.hp))}`).join(', ');
  let guidance = !session
    ? 'Preparation. Buy or retrofit towers, deploy a Hero and one army stack, then resume.'
    : 'The starter towers cover the lane. Archers and sappers punish an undefended lane. Deploy the hero and one army stack before resuming.';
  if (session?.pendingSettlement) guidance = session.winner === 'p' ? 'The lane held. Apply the result. The reward is paid once.' : 'The core fell. Apply the result. Losses are recorded once.';
  else if (session?.paused) guidance = 'Paused. Resume continues this same wave. Nothing is caught up while paused.';
  else if (blastAim) guidance = 'Choose a cell on the field. The blast spends 40 mana at that world point and does not move the wave. Pause still freezes the attackers.';
  else if (session) guidance = `Running. Cleared ${session.clearedWaves} of ${session.waves}. Core ${Math.max(0, Math.round(session.core))}. Towers ${towerLine}. ${session.heroDeployed ? 'Hero is deployed.' : 'Deploy the hero.'} ${session.armyDeployed ? 'A stack is deployed.' : 'Deploy one stack.'} Aim the blast or cast it at the hero. Positive morale does not add a turn in Defense or Endless.`;
  const preview = upcoming ? ` Next ${upcoming}.` : '';
  say(guidance + preview);
}

function story() {
  clearWorld();
  paintChamber(storyHeaderTitle(state, data), state.story.rival ? `Rival ${state.story.rival}` : 'Your people. Your choices.', 'story');
  $('selected').textContent = state.story.rival ?? 'Choose a rival';
  if (!state.story.rival || storyQuickFocus === 'rival') {
    choiceHeading(state.story.rival ? `Rival · ${state.story.rival}` : 'Rival');
    $('choices').lastElementChild?.setAttribute('data-story-focus', 'rival');
    if (!state.story.rival) for (const name of RIVALS) $('choices').append(button(name, () => act('CHOOSE_RIVAL', { name })));
  }
  const chapter = data.STORY[state.story.chapter];
  const screen = storyScreen(state, data);
  choiceHeading('Chapter');
  if (screen.choices.length && chapter) {
    for (const [index, choice] of chapter.ch.entries()) $('choices').append(button(choice.t, () => act('STORY_CHOICE', { index })));
  } else if (screen.keepValley) $('choices').append(button('Keep the valley', () => act('ACK_FUTURE', {})));
  choiceHeading('Quests');
  $('choices').lastElementChild?.setAttribute('data-story-focus', 'quests');
  for (const template of data.QUEST_TEMPLATES) {
    const claimed = state.quests[template.id].claimed;
    const ready = questReady(state, data, template.id);
    const title = (claimed ? 'Claimed: ' : ready ? 'Claim: ' : 'Open: ') + template.n;
    const node = button(title, () => act('CLAIM_QUEST', { id: template.id }), claimed || !ready);
    const reward = template.rw || {};
    if (Object.keys(reward).length) {
      node.classList.add('cost-action');
      const costs = document.createElement('span');
      costs.className = 'cost-icons';
      for (const [key, amount] of Object.entries(reward)) {
        const icon = resourceIcon(key);
        if (icon) costs.append(icon);
        const figure = document.createElement('span');
        figure.className = 'cost-amount';
        figure.textContent = String(amount);
        costs.append(figure);
      }
      node.append(costs);
      node.setAttribute('aria-label', `${title}. Reward ${Object.entries(reward).map(([key, amount]) => `${amount} ${key}`).join(', ')}.`);
    }
    $('choices').append(node);
  }
  choiceHeading('Age records');
  for (let age = 0; age <= 7; age++) {
    const claimed = Boolean(state.story.milestones[age]);
    $('choices').append(button((claimed ? 'Recorded: ' : 'Record milestone: ') + data.AGES[age].n, () => act('CLAIM_MILESTONE', { age }), claimed || state.age < age));
  }
  const logs = state.story.choices.map((flag, index) => data.STORY[index]?.ch.find(choice => choice.flag === flag)?.log).filter(Boolean);
  say(screen.text + (logs.length ? ' Saved record: ' + logs.join(' ') : '') + ' Choices, the rival and claims stay in the save. ' + blocked.loot);
}

function draftDescriptor() {
  const parsed = parseChallenge(challengeDraft.seed, challengeDraft.code);
  if (parsed.error) return parsed;
  try { return { descriptor: challengeDescriptor(parsed.seed, parsed.code) }; }
  catch (error) { return { error: error.message }; }
}
function prepareDefense(practice) {
  defensePlan = practice === 'endless' ? 'endless' : 'siege';
  defensePad = '';
  defenseTowerId = null;
  view = 'defense';
  setPanel(true);
  render();
}
function startDefense(practice = defensePlan) {
  const type = practice === 'endless' ? 'START_ENDLESS' : 'START_SIEGE';
  act(type, {});
  if (!state.defense) return;
  act('DEFENSE', { paused: true, dt: 0 });
  view = 'defense';
  setPanel(false);
  render();
}
function war() {
  clearWorld();
  paintChamber('War', 'Siege, duel, endless, skirmish and a local challenge.', 'war');
  $('selected').textContent = 'War';
  choiceHeading('Campaign and practice');
  $('choices').append(button('Skirmish', () => { act('START_SKIRMISH', {}); if (state.battle) { view = 'tactical'; render(); } }));
  $('choices').append(button('Prepare Campaign Siege', () => prepareDefense('siege'), false, 'start-siege'));
  $('choices').append(button('Tactical Duel', () => { act('START_DUEL', {}); if (state.battle) { view = 'tactical'; render(); } }));
  $('choices').append(button('Prepare Endless', () => prepareDefense('endless'), false, 'start-endless'));
  const seedInput = document.createElement('input');
  seedInput.type = 'text';
  seedInput.inputMode = 'numeric';
  seedInput.setAttribute('aria-label', 'Challenge seed');
  seedInput.dataset.choice = 'challenge-seed';
  seedInput.value = challengeDraft.seed;
  seedInput.addEventListener('input', () => { challengeDraft.seed = seedInput.value; challengeDraft.error = ''; });
  const seedField = document.createElement('label');
  seedField.className = 'challenge-field';
  const seedLabel = document.createElement('span');
  seedLabel.textContent = 'Seed';
  seedField.append(seedLabel, seedInput);
  const codeInput = document.createElement('input');
  codeInput.type = 'text';
  codeInput.maxLength = 64;
  codeInput.setAttribute('aria-label', 'Scenario code');
  codeInput.dataset.choice = 'challenge-code';
  codeInput.value = challengeDraft.code;
  codeInput.addEventListener('input', () => { challengeDraft.code = codeInput.value; challengeDraft.error = ''; });
  const codeField = document.createElement('label');
  codeField.className = 'challenge-field';
  const codeLabel = document.createElement('span');
  codeLabel.textContent = 'Scenario code';
  codeField.append(codeLabel, codeInput);
  $('choices').append(seedField, codeField);
  $('choices').append(button('Start challenge', () => {
    const parsed = draftDescriptor();
    if (parsed.error) { challengeDraft.error = parsed.error; render(); return; }
    const before = { gold: state.resources.gold, xp: state.hero.xp, age: state.age, items: state.inventory.length };
    act('START_CHALLENGE', { schema: 1, scenarioId: 'duel-v1', seed: parsed.descriptor.seed, label: parsed.descriptor.label, code: parsed.descriptor.label });
    if (state.resources.gold !== before.gold || state.hero.xp !== before.xp || state.age !== before.age || state.inventory.length !== before.items) {
      say('Challenge must not change campaign gold, experience, age or items.');
      return;
    }
    if (state.battle) { view = 'tactical'; setPanel(false); render(); }
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
  if (challengeDraft.error) say(challengeDraft.error);
  else say('Skirmish and Challenge do not pay campaign gold. Prepare Siege or Endless before starting so you can buy towers first. A challenge uses the seed and label you enter. Siege and Duel settle campaign rewards once.');
}

function openSettings(returnTo = view) {
  settingsReturnView = screens.includes(returnTo) && returnTo !== 'settings' ? returnTo : 'kingdom';
  view = 'settings';
  menuSheet = false;
  setPanel(false);
  render();
}
function closeSettings() {
  view = screens.includes(settingsReturnView) && settingsReturnView !== 'settings' ? settingsReturnView : 'kingdom';
  menuSheet = false;
  setPanel(false);
  render();
}
function settings() {
  clearWorld();
  paintChamber('Settings', 'Local music, sound and reduced motion. No account and no network.', 'settings');
  $('selected').textContent = 'Settings';
  if (!state) { say('Start or import a campaign before changing settings.'); return; }
  const music = Math.round(state.settings.music * 10) / 10;
  const sound = Math.round(state.settings.sfx * 10) / 10;
  $('choices').append(button(state.settings.reducedMotion ? 'Reduced motion on' : 'Reduced motion off', () => act('SETTINGS', { ...state.settings, reducedMotion: !state.settings.reducedMotion })));
  $('choices').append(button(`Music down · ${music}`, () => act('SETTINGS', { ...state.settings, music: Math.max(0, Math.round((state.settings.music - 0.2) * 10) / 10) })));
  $('choices').append(button(`Music up · ${music}`, () => act('SETTINGS', { ...state.settings, music: Math.min(1, Math.round((state.settings.music + 0.2) * 10) / 10) })));
  $('choices').append(button(`Sound down · ${sound}`, () => act('SETTINGS', { ...state.settings, sfx: Math.max(0, Math.round((state.settings.sfx - 0.2) * 10) / 10) })));
  $('choices').append(button(`Sound up · ${sound}`, () => act('SETTINGS', { ...state.settings, sfx: Math.min(1, Math.round((state.settings.sfx + 0.2) * 10) / 10) })));
  $('choices').append(button('Arm local audio', () => { arm(state.settings); blip(); say('Local tones use separate music and sound gains. Nothing is downloaded.'); }));
  say(`Music ${state.settings.music}, sound ${state.settings.sfx}. Local music is a generated motif on its own bus; the click is only the sound bus. Haptics are unavailable. No account or network setting is present.`);
}

function resumeDestination() {
  if (state?.battle) return state.battle.kind === 'defense' ? 'defense' : 'tactical';
  if (state?.defense) return 'defense';
  return isResumableView(lastSavedView) ? lastSavedView : 'kingdom';
}
function openCampaignWorldSelect() {
  if (replacementPending) return;
  if (initial.status === 'UNAVAILABLE') { say(initial.error || 'Campaign storage is unavailable.'); return; }
  campaignWorldSelection = adventureWorlds.some(world => world.id === state?.adventureWorldId)
    ? state.adventureWorldId
    : adventureWorlds.some(world => world.id === campaignWorldSelection) ? campaignWorldSelection : adventureWorlds[0].id;
  view = 'campaignMapSelect';
  menuSheet = false;
  setPanel(true);
  render();
}
async function startSelectedCampaignWorld() {
  if (replacementPending || initial.status === 'UNAVAILABLE') return;
  const world = adventureWorlds.find(entry => entry.id === campaignWorldSelection) || adventureWorlds[0];
  if (state && !confirm('Replace the current campaign on this device?')) return;
  setPanel(false);
  const replaced = await replaceLive(freshCampaign(world.id), 'hero', `${world.title} chosen. Choose a class, then enter the valley.`);
  if (!replaced) {
    view = 'campaignMapSelect';
    setPanel(true);
    render();
  }
}
function campaignMapSelect() {
  clearWorld();
  const chosen = adventureWorlds.find(world => world.id === campaignWorldSelection) || adventureWorlds[0];
  const mapFile = campaignMapImage(chosen);
  showTerrain(mapFile, `${chosen.title} campaign world preview`, chosen.productionMapFile ? 'generated-integrated-world-map-preview' : 'generated-campaign-world-preview');
  $('world').setAttribute('data-campaign-world-preview-source', mapFile);
  $('world').setAttribute('data-screen', 'campaign-world-select');
  $('world').setAttribute('data-selected-world', chosen.id);
  $('world').setAttribute('aria-label', `${chosen.title}. ${chosen.summary}`);
  $('selected').textContent = chosen.title;
  choiceHeading(`Campaign world ${adventureWorlds.findIndex(world => world.id === chosen.id) + 1} of ${adventureWorlds.length}`);
  $('choices').append(sceneCopy(`${chosen.realm} · ${chosen.biome}. ${chosen.summary}`, 'campaign-world-summary'));
  $('choices').append(button(`Begin ${chosen.title}`, startSelectedCampaignWorld, replacementPending || initial.status === 'UNAVAILABLE', 'begin-selected-world', true));
  choiceHeading('Select a world');
  const list = document.createElement('div');
  list.className = 'campaign-world-list';
  list.setAttribute('role', 'group');
  list.setAttribute('aria-label', '12 selectable campaign worlds');
  for (const world of adventureWorlds) {
    const option = button('', () => { campaignWorldSelection = world.id; render(); }, replacementPending, `campaign-world:${world.id}`);
    option.classList.add('campaign-world-option');
    option.setAttribute('aria-label', `Preview ${world.title}, ${world.realm}`);
    option.setAttribute('aria-pressed', String(world.id === chosen.id));
    option.dataset.worldId = world.id;
    const image = document.createElement('img');
    image.src = campaignMapImage(world);
    image.alt = '';
    image.loading = 'lazy';
    const copy = document.createElement('span');
    copy.className = 'campaign-world-copy';
    const title = document.createElement('strong');
    title.textContent = world.title;
    const realm = document.createElement('small');
    realm.textContent = world.realm;
    copy.append(title, realm);
    option.append(image, copy);
    list.append(option);
  }
  $('choices').append(list);
  $('choices').append(button('Return to campaign gate', () => { view = 'home'; setPanel(false); render(); }, false, 'cancel-world-select'));
  say('Choose one of the 12 clean continental maps. The selected world stays with this campaign through all eight ages.');
}
function paintGate() {
  const gate = $('gate');
  gate.hidden = false;
  gate.dataset.campaignState = state ? 'saved' : 'empty';
  const damagedRaw = initial.raw ?? localStorage.getItem(SAVE_KEY);
  const recoveryCopy = damagedSaveRecoveryCopy({ hasBackup: Boolean(initial.backup), hasDamagedBytes: damagedRaw != null });
  const line = initial.status === 'UNAVAILABLE' ? initial.error : !state && initial.status === 'DAMAGED'
    ? recoveryCopy
    : state
      ? `${adventureWorlds.find(world => world.id === state.adventureWorldId)?.title || 'Campaign'} · ${data.AGES[state.age].n}, day ${state.day}. Continue keeps this save.`
      : 'No campaign is stored on this device.';
  $('gate-kicker').textContent = 'Campaign I: The Shattered Kingdom';
  $('gate-line').textContent = line;
  const report = $('gate-report');
  const showResume = shouldShowResumeNote(resumeNote, view, state);
  report.hidden = !showResume;
  $('gate-report-copy').textContent = showResume ? `${resumeNote} Dismissing this report does not credit the clock again.` : '';
  const actions = $('gate-actions');
  actions.replaceChildren();
  const add = (label, choiceId, mark, onClick, isPrimary = false) => {
    const node = document.createElement('button');
    node.type = 'button';
    if (isPrimary) node.className = 'primary';
    node.dataset.choice = choiceId;
    node.setAttribute('aria-label', label);
    node.addEventListener('click', onClick);
    node.append(glyph(mark));
    const text = document.createElement('span');
    text.textContent = label;
    node.append(text);
    actions.append(node);
  };
  if (state) add('Continue', 'continue', 'M8 5 L18 12 L8 19 Z', () => { updateSaveFeedback(); setPanel(false); view = resumeDestination(); render(); }, true);
  add('New campaign', 'new-campaign', navGlyphs.hero, openCampaignWorldSelect, !state);
  add('Save/Load', 'open-load', headerGlyphs.save, () => { setPanel(true); render(); });
  add('Settings', 'open-settings', 'M12 4 L14 8 L18 9 L15 12 L16 17 L12 15 L8 17 L9 12 L6 9 L10 8 Z', () => openSettings('home'));
}
function home() {
  clearWorld();
  const vista = selection.kingdomTerrain.stone.displayFile || selection.kingdomTerrain.stone.sourceFile;
  showTerrain(vista, 'Stone valley at the gate', 'consumer-displayed');
  if (TITLE_BACKDROP) {
    $('world').append(element('image', {
      href: TITLE_BACKDROP,
      x: 0,
      y: 0,
      width: 1376,
      height: 768,
      preserveAspectRatio: 'xMidYMid meet',
      opacity: '1',
      'data-title-backdrop': '1',
    }));
  }
  $('world').setAttribute('data-screen', 'home-gate');
  $('selected').textContent = 'Ages of Dominion';
  paintGate();
  if (!state && initial.status === 'DAMAGED' && initial.backup) $('choices').append(button('Restore valid backup', async () => {
    if (replacementPending) return;
    replacementPending = true;
    render();
    try {
      const next = await idbAdapter.restoreBackup(data);
      initial = await idbAdapter.loadLive(data);
      saveQueue.head = initial.head;
      saveQueue.status = { kind: 'committed', sequence: saveQueue.sequence, head: initial.head };
      state = next;
      view = 'kingdom';
      lastSavedView = 'kingdom';
      replacementPending = false;
      resumeNote = '';
      updateSaveFeedback();
      installLifecycle();
      render();
      say('Restored the last valid backup. Damaged bytes stay stored.');
    } catch (error) {
      replacementPending = false;
      saveFault = error.message;
      render();
    }
  }));
  if (state) $('choices').append(button('Export campaign', () => download('aod-campaign.json', encode(state, data))));
  $('choices').append(button('Import campaign', () => $('import-file').click()));
  if (state) {
    for (let index = 1; index <= 3; index++) {
      $('choices').append(button('Save slot ' + index, async () => { try { await idbAdapter.storeSlot(index, encode(state, data), data); say('Slot ' + index + ' stored.'); } catch (error) { say('Slot was not saved. ' + error.message); } }));
      $('choices').append(button('Load slot ' + index, async () => {
        try {
          const next = await idbAdapter.loadSlot(index, data);
          if (!next) { say('Slot ' + index + ' is empty.'); return; }
          replaceLive(next, 'kingdom', 'Slot ' + index + ' loaded.');
        } catch (error) { saveFault = error.message; render(); }
      }));
    }
  }
  const damagedRaw = initial.raw ?? localStorage.getItem(SAVE_KEY);
  if (!state && initial.status === 'DAMAGED' && damagedRaw != null) $('choices').append(button('Export damaged save', () => {
    const blob = new Blob([damagedRaw], { type: 'application/json' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob); link.download = 'aod-damaged-save.json'; link.click(); URL.revokeObjectURL(link.href);
  }));
  if (state) $('choices').append(button('Continue', () => { updateSaveFeedback(); setPanel(false); view = resumeDestination(); render(); }, false, 'continue-panel'));
  $('choices').append(button('New campaign', openCampaignWorldSelect, initial.status === 'UNAVAILABLE', 'new-campaign-panel'));
  if (saveFault) say(saveFault);
  else if (!state && initial.status === 'DAMAGED') say(initial.error + ' ' + damagedSaveRecoveryCopy({ hasBackup: Boolean(initial.backup), hasDamagedBytes: damagedRaw != null }));
  else if (!state) say('Ages of Dominion. No campaign is stored on this device. Start a new one and choose a class, or import a local file.');
}

function help() {
  clearWorld();
  paintChamber('Help', 'Credits and privacy stay on this device.', 'help');
  $('selected').textContent = 'Help, credits and privacy';
  say('Help: use Kingdom to build, Adventure to travel, Tactical and Defense for battles, and Story for the seven chapters, quests and age records. Positive morale is a Tactical bonus action, once each round, at 4.2% per morale point. The Future conclusion is The Valley We Keep and grants nothing by itself. Credits: Ages of Dominion Reborn is an offline local campaign. Privacy: there is no account, no network request and no device permission. Saves, slots and exports stay on this device.');
}
function download(name, text) {
  const blob = new Blob([text], { type: 'application/json' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob); link.download = name; link.click(); URL.revokeObjectURL(link.href);
  say('Export downloaded. It is a local file, not an upload.');
}
const draw = { home, campaignMapSelect, kingdom, adventure, hero, army, forge, market, tactical, defense, story, war, settings, help };

function setPanel(open) {
  const panel = $('panel');
  const wasOpen = panel.classList.contains('open');
  if (!open) { adventurePanelRequested = false; menuSheet = false; resourceSheet = false; siteChoices = null; kingdomBuildSite = ''; kingdomActionSheet = false; }
  if (open && !wasOpen) panel.scrollTop = 0;
  panel.classList.toggle('open', open);
  $('stage-field')?.classList.toggle('panel-open', open);
  $('context').setAttribute('aria-expanded', String(open));
}
function render() {
  const battleLive = ['PENDING', 'ACTIVE'].includes(state?.battle?.status);
  const defenseLive = state?.defense?.status === 'ACTIVE';
  const sessionOverlay = ['home', 'settings', 'help', 'campaignMapSelect'].includes(view);
  if ((battleLive || state?.battle?.pendingSettlement) && !sessionOverlay) view = 'tactical';
  else if ((defenseLive || state?.defense?.pendingSettlement) && !sessionOverlay) view = 'defense';
  if (battleLive) view = viewDuringRetreat(view, { retreatArmed, battleActive: true });
  if (view !== 'tactical') $('stage-field')?.querySelectorAll('.tactical-hero-plaque, .tactical-round-badge').forEach(node => node.remove());
  if (view && view !== 'home' && view !== 'hero' && view !== 'campaignMapSelect') {
    valleyEntered = true;
  }
  if (state?.story?.flags?.enteredValley === true) valleyEntered = true;
  const panel = $('panel');
  const crossingFocus = view === 'adventure' && state?.adventure
    ? crossingPresentation(state.adventureWorldId, state.adventure, adventureGeometryForCampaign().bridges, travelPreview)
    : null;
  if (shouldAutoCloseCrossingPanel({
    crossingFocus,
    panelOpen: panel.classList.contains('open'),
    menuSheet,
    resourceSheet,
    explicitNavigation: adventurePanelRequested,
  })) setPanel(false);
  $('app').dataset.bridgeFocus = crossingFocus?.bridgeId || '';
  $('stage-field')?.classList.toggle('panel-open', panel.classList.contains('open'));
  panel.dataset.sheet = menuSheet ? 'menu' : resourceSheet ? 'resources' : siteChoices ? 'sites' : kingdomActionSheet ? 'kingdom-actions' : kingdomBuildSite ? 'kingdom-build' : view === 'market' ? 'market-inspector' : view === 'kingdom' && state?.plots.some(plot => plot.id === selected) ? 'kingdom-building' : view === 'defense' ? (state?.defense ? 'defense-session' : 'defense-preparation') : 'content';
  if (view !== 'market') marketEditing = false;
  const viewChanged = lastRenderedView !== view;
  lastRenderedView = view;
  const panelContentKey = JSON.stringify([
    view, panel.classList.contains('open'), menuSheet, resourceSheet, siteChoices, kingdomBuildSite, kingdomActionSheet, marketEditing,
    selected, selectedHeroSlot, forgeSlot, forgePreview, tacticalIntent, defenseTowerId, defensePlan,
    state?.adventure?.atTown ?? null, state?.adventure?.x ?? null, state?.adventure?.y ?? null,
  ]);
  const panelContentChanged = panelContentKey !== lastPanelContentKey;
  lastPanelContentKey = panelContentKey;
  const scroll = viewChanged || panelContentChanged ? 0 : panel.scrollTop;
  const focusId = adventureInteractionFocus() || document.activeElement?.dataset?.choice || '';
  labelQueue = [];
  resources();
  $('choices').replaceChildren();
  $('dock').replaceChildren();
  beginActorFrame();
  clearWorld();
  const nav = $('nav');
  const expected = primaryNav.map(name => `nav:${name}`);
  let navNodes = [...nav.children];
  if (navNodes.length !== expected.length || navNodes.some((node, index) => node.dataset.choice !== expected[index])) {
    nav.replaceChildren();
    navNodes = primaryNav.map(name => {
      const label = name[0].toUpperCase() + name.slice(1);
      const node = button('', () => { view = name; menuSheet = false; setPanel(false); if (state && name !== 'hero') { state.story.flags.enteredValley = true; persist(); } render(); }, false, `nav:${name}`);
      node.classList.add('icon-medallion');
      node.setAttribute('aria-label', label);
      nav.append(node);
      return node;
    });
  }
  navNodes.forEach((node, index) => {
    const name = primaryNav[index];
    if (name === 'hero' && state?.hero?.class) {
      const card = portraitCard(state.hero.class, state.age ?? 0) || heroBody(state.hero.class, state.age ?? 0) || pendingPortrait(state.hero.class, state.age ?? 0);
      if (card?.file && node.querySelector('img')?.getAttribute('src') !== card.file) {
        const img = document.createElement('img');
        img.src = card.file;
        img.alt = '';
        node.replaceChildren(img);
      } else if (!card?.file && !node.querySelector('svg')) node.replaceChildren(glyph(navGlyphs.hero));
    } else if (!node.querySelector('svg')) node.replaceChildren(glyph(navGlyphs[name]));
    if (name === view) node.setAttribute('aria-current', 'true');
    else node.removeAttribute('aria-current');
  });
  if (!state && view !== 'home' && view !== 'settings' && view !== 'help' && view !== 'campaignMapSelect') view = 'home';
  $('app').dataset.view = view;
  $('app').dataset.combat = state?.battle || state?.defense ? '1' : '0';
  if (view !== 'home') $('gate').hidden = true;
  if (state && isResumableView(view)) lastSavedView = view;
  if (view === 'forge' && (forgePreview || viewChanged)) setPanel(true);
  measureFrame();
  if (view !== 'adventure' || !state?.adventure) $('stage-field')?.querySelectorAll('.adventure-hero-panel').forEach(node => node.remove());
  $('adventure-minimap')?.remove();
  $('status').textContent = saveFault && saveFault !== 'saving' ? 'Save failed' : state ? `${data.AGES[state.age].n} · day ${state.day} · ${state.weather}` : initial.status === 'DAMAGED' ? 'Damaged save' : initial.status === 'EMPTY' ? 'No campaign stored' : 'No campaign';
  draw[view]();
  const detailActions = {
    kingdom: ['Manage Kingdom', 'M4 20 V10 L12 4 L20 10 V20 H14 V14 H10 V20 Z', () => { kingdomActionSheet = true; setPanel(true); render(); }],
    tactical: ['More battle actions and targets', navGlyphs.war],
    defense: [state?.defense ? 'Defense actions' : 'Defense preparation', 'M12 4 C6.5 4 2.5 8.2 1 12 C2.5 15.8 6.5 20 12 20 C17.5 20 21.5 15.8 23 12 C21.5 8.2 17.5 4 12 4 Z M12 8 A4 4 0 1 0 12.01 8 Z M12 10 A2 2 0 1 1 11.99 10 Z'],
    adventure: ['Travel and sites', navGlyphs.adventure, () => { adventurePanelRequested = true; setPanel(true); render(); }],
    hero: ['Skills and spellbook', 'M2 5 Q7 3 11.5 6.5 V20 Q7 16.5 2 19 Z M12.5 6.5 Q17 3 22 5 V19 Q17 16.5 12.5 20 Z M11.5 7 H12.5 V19 H11.5 Z M4 8 H9 V9 H4 Z M4 11 H9 V12 H4 Z M15 8 H20 V9 H15 Z M15 11 H20 V12 H15 Z'],
    forge: ['Craft and inventory', 'M5 16 H19 V20 H5 Z M8 16 L12 5 L16 16 Z'],
    army: ['Recruit and inspect army', navGlyphs.army],
    market: ['Trade resources', 'M5 6 H19 L16 19 H8 Z'],
    settings: ['Adjust settings', 'M12 3 L15 8 L21 10 L17 14 L18 21 L12 18 L6 21 L7 14 L3 10 L9 8 Z'],
  };
  if (detailActions[view] && !(view === 'hero' && classChoiceOpen()) && !menuSheet && !resourceSheet && !panel.classList.contains('open')) {
    const [label, mark, customAction] = detailActions[view];
    dockIcon(label, '', mark, customAction || (() => { if (view === 'hero') selectedHeroSlot = null; setPanel(true); render(); }), false, view === 'kingdom' ? 'kingdom-actions-open' : `inspect:${view}`);
  }
  if (sessionOverlay && view !== 'home' && view !== 'campaignMapSelect' && (state?.battle || state?.defense)) {
    dockIcon('Resume session', '', navGlyphs.war, () => { view = state.defense ? 'defense' : 'tactical'; setPanel(false); render(); }, false, 'resume-session');
  }
  const forgeActionOnly = view === 'forge'
    && $('dock').children.length === 1
    && $('dock').firstElementChild.classList.contains('icon-medallion');
  $('app').dataset.forgeActionOnly = String(forgeActionOnly);
  if (saveFault && saveFault !== 'saving' && view !== 'home') say(saveFault);
  if (menuSheet && view !== 'home') {
    $('selected').textContent = 'Menu';
    $('choices').replaceChildren();
    const menuMarks = {
      forge: 'M5 16 H19 V19 H5 Z M8 16 L12 6 L16 16 Z',
      market: 'M6 7 H18 L16 18 H8 Z',
      story: 'M6 4 H15 V20 H6 Z',
      settings: 'M12 4 L14 8 L18 9 L15 12 L16 17 L12 15 L8 17 L9 12 L6 9 L10 8 Z',
      help: 'M12 17 A1.6 1.6 0 1 0 11.9 17 Z M9 8 A3 3 0 1 1 13 11 V14 H11 V10 A1.2 1.2 0 1 0 9 8',
      home: headerGlyphs.save,
    };
    for (const [name, label] of menuDestinations) {
      if ((state?.battle || state?.defense) && !['home', 'settings', 'help'].includes(name)) continue;
      const visibleLabel = name === 'home' && resumeNote && !state?.battle && !state?.defense ? 'Away-time report & saves' : label;
      const node = button('', () => { if (name === 'settings') openSettings(view); else { view = name; menuSheet = false; if (name === 'market') { marketEditing = false; selected = ''; } setPanel(name === 'market'); render(); } }, false, `menu:${name}`);
      node.classList.add('menu-row');
      node.setAttribute('aria-label', visibleLabel);
      node.append(glyph(menuMarks[name]));
      const text = document.createElement('span');
      text.textContent = visibleLabel;
      node.append(text);
      $('choices').append(node);
    }
    $('choices').append(button('Resource details', () => { resourceSheet = true; menuSheet = false; kingdomBuildSite = ''; kingdomActionSheet = false; render(); }, false, 'resource-details'));
    if (view === 'kingdom') $('choices').append(button('Choose a site', () => { siteChoices = state.plots.map(plot=>plot.id); menuSheet = false; render(); }, false, 'site-list'));
    if (state?.defense) $('choices').append(button('Resume Defense', () => { view = 'defense'; setPanel(false); render(); }, false, 'resume-defense'));
    else if (state?.battle) $('choices').append(button('Resume Tactical', () => { view = 'tactical'; setPanel(false); render(); }, false, 'resume-tactical'));
  }
  if (resourceSheet && state) {
    $('selected').textContent = 'Resources';
    $('choices').replaceChildren();
    const income = rates(state);
    for (const key of ['food', 'wood', 'stone', 'gold']) {
      const row = document.createElement('p');
      row.className = 'resource-detail';
      const label = resourceChipLabel(key[0].toUpperCase() + key.slice(1), state.resources[key]);
      row.textContent = `${label.name}: ${state.resources[key].toLocaleString(undefined, { maximumFractionDigits: 3 })} · ${income[key].toLocaleString()} / second`;
      const icon = resourceIcon(key);
      if (icon) row.prepend(icon);
      $('choices').append(row);
    }
    const cap = [8, 7, 6, 5, 4, 3.5, 3, 3][state.age];
    $('choices').append(sceneCopy(`Away production is credited for up to ${cap} hours at this age.`, 'resource-cap'));
  }
  if (siteChoices && state) {
    $('selected').textContent = 'Choose a site';
    $('choices').replaceChildren();
    for (const id of siteChoices) {
      const plot = state.plots.find(item=>item.id===id);
      $('choices').append(button(`${id}: ${plot.type ? kingdomBuildingName(plot.type) : 'Empty site'} · level ${plot.level}`, () => { selected = id; siteChoices = null; render(); }, false, `choose-site:${id}`));
    }
    $('choices').append(button(`Walls and gate · level ${state.walls.level}`, () => { selected = ''; siteChoices = null; render(); }, false, 'choose-walls'));
  }
  if (state && view !== 'home' && !menuSheet && !resourceSheet && !siteChoices) {
    $('choices').append(button(state.tutorial.skipped ? 'Review tutorial' : 'Skip tutorial', () => act(state.tutorial.skipped ? 'TUTORIAL_REVIEW' : 'TUTORIAL_SKIP', {}), false, 'tutorial-toggle'));
    const buildSiteSelected = Boolean(selected && state.plots?.some(plot => plot.id === selected && plot.level === 0 && plot.type == null));
    const mark = tutorialAnchorChoice(state.tutorial.step, { pickerOpen: Boolean(kingdomBuildSite), siteSelected: buildSiteSelected });
    if (mark && !state.tutorial.skipped) {
      const nodes = [
        ...$('choices').querySelectorAll('[data-choice]'),
        ...$('dock').querySelectorAll('[data-choice]'),
        ...$('board').querySelectorAll('[data-choice]'),
        ...$('scene-ui').querySelectorAll('[data-choice]'),
      ];
      for (const node of nodes) {
        const bounds = node.getBoundingClientRect();
        if (!bounds.width || !bounds.height || getComputedStyle(node).visibility === 'hidden') continue;
        if (node.dataset.choice === mark || node.dataset.choice.endsWith(':' + mark) || node.dataset.choice.startsWith(mark)) node.dataset.anchor = 'tutorial';
      }
    }
  }
  fitScene();
  flushLabels();
  paintRetreat();
  paintBuildPreview();
  if (replacementPending) {
    $('stage-field').inert = true;
    document.querySelector('header').inert = true;
    document.querySelector('footer').inert = true;
  }
  if (auditMode) {
    let snapshot = $('audit-snapshot');
    if (!snapshot) { snapshot = document.createElement('script'); snapshot.type = 'application/json'; snapshot.id = 'audit-snapshot'; document.body.append(snapshot); }
    snapshot.textContent = JSON.stringify({ view, state, storage: saveQueue.status, frame: frameFit });
  }
  panel.scrollTop = scroll;
  const decision = panel.querySelector('[data-forge-decision]');
  if (decision) {
    const top = decision.offsetTop;
    const bottom = top + decision.offsetHeight;
    if (top < panel.scrollTop) panel.scrollTop = top;
    else if (bottom > panel.scrollTop + panel.clientHeight) panel.scrollTop = Math.max(0, bottom - panel.clientHeight);
  }
  if (view === 'story' && storyQuickFocus) {
    const target = $('choices').querySelector(`[data-story-focus="${storyQuickFocus}"]`);
    if (target) {
      target.scrollIntoView({ block: 'start' });
      target.setAttribute('tabindex', '-1');
      target.focus({ preventScroll: true });
    }
    storyQuickFocus = '';
  }
  const retreatOpen = Boolean(retreatArmed && view === 'tactical' && state?.battle?.status === 'ACTIVE');
  const focusTarget = retreatFocusTarget({
    open: retreatOpen,
    restoreTrigger: retreatRestorePending && !retreatOpen,
    activeChoice: focusId,
  });
  if (!retreatOpen) retreatRestorePending = false;
  if (focusTarget === 'retreat-cancel') {
    if (document.activeElement !== $('retreat-cancel') && document.activeElement !== $('retreat-confirm')) $('retreat-cancel').focus();
  } else if (focusTarget) {
    const escaped = CSS.escape(focusTarget);
    (panel.querySelector(`[data-choice="${escaped}"]`) || $('dock').querySelector(`[data-choice="${escaped}"]`) || $('scene-ui')?.querySelector(`[data-choice="${escaped}"]`))?.focus();
  }
  const board = $('board');
  if (board) {
    const showBoard = view === 'army' && Boolean(state);
    board.hidden = !showBoard;
    $('frame').hidden = showBoard;
    if (!showBoard) board.replaceChildren();
  }
  const canBack = Boolean(retreatArmed || $('panel')?.classList.contains('open') || (view !== 'home'));
  window.rebornNativeBridge?.setBackActive(canBack);
}

function paintLiveWorld() {
  if (!state || armed || mapArm || worldOnly || retreatArmed) return;
  if (view === 'hero' || view === 'army') return; // Static room/roster: redraw on state or layout changes.
  if (view === 'adventure' && !travelMotion) return;
  if ($('world').contains(document.activeElement)) return;
  if (!['hero', 'army', 'adventure', 'tactical', 'defense', 'kingdom'].includes(view)) return;
  if (view === 'kingdom' && state.buildJobs.length === 0) return;
  worldOnly = true;
  labelQueue = [];
  try {
    beginActorFrame();
    $('world').replaceChildren();
    if (view === 'hero') paintHero();
    else if (view === 'army') paintArmy();
    else draw[view]();
    flushLabels();
  } finally { worldOnly = false; }
}
function installLifecycle() {
  if (!frameClock) {
    frameClock = createFrameClock({
      paused: () => suspended || document.hidden || menuSheet || Boolean(state?.settings?.reducedMotion) || (view === 'defense' && Boolean(state?.defense?.paused)),
      onFrame: sample => {
        motionTime = sample.render;
        if (!sample.paused) paintLiveWorld();
      },
    });
    frameClock.start();
  }
  if (timer) return;
  let durableAt = 0;
  let uiAt = 0;
  timer = setInterval(() => {
    if (!state || suspended || replacementPending) return;
    const now = Date.now();
    try { state = advanceReported(state, now, data).state; }
    catch (error) { saveFault = error.message; }
    if (view === 'defense' && state.defense?.status === 'ACTIVE' && !state.defense.paused && !menuSheet) {
      try { state = advanceActiveDefense(state, 0.25); } catch { /* A rejected step does not invent a later attack. */ }
    }
    if (view === 'tactical' && state.battle?.status === 'ACTIVE' && !retreatArmed && !pendingBuild && !menuSheet) {
      const actor = state.battle.stacks.find(item => item.id === activeStackId(state.battle));
      const playing = !state.settings.reducedMotion && battleEvents.some(event => event.sessionId === state.battle.id && event.start + event.duration > motionTime);
      if (actor?.side === 'e' && !playing) act('BATTLE', { action: 'opponent' });
    }
    // Durable copy of the current campaign. Internal ticks do not add a transaction id.
    if (now - durableAt >= 2000 && saveQueue.status.kind !== 'failed') {
      durableAt = now;
      persist();
    }
    const editingText = ['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement?.tagName);
    if (!armed && !editingText && now - uiAt >= 1000) {
      uiAt = now;
      render();
    }
  }, 250);
}
$('save').onclick = () => {
  if (retreatBlocksBackground({ retreatArmed, inDialog: false })) return;
  if (!state) return;
  const feedback = saveButtonFeedback(saveQueue.status.kind);
  if (feedback.action === 'export-unsaved') {
    try { download('aod-unsaved-campaign.json', encode(state, data)); }
    catch (error) { say('The unsaved campaign could not be exported. ' + error.message); }
    return;
  }
  if (feedback.action !== 'save') return;
  saveFault = 'saving';
  render();
  Promise.resolve(persist()).then(stored => {
    if (!stored && saveFault === 'saving') saveFault = 'Save failed';
    render();
    if (stored) say('Saved locally.');
    else say(saveFault || 'Save failed.');
  });
};
$('context').replaceChildren(glyph(headerGlyphs.menu));
$('save').replaceChildren(glyph(headerGlyphs.save));
$('context').onclick = () => {
  if (retreatBlocksBackground({ retreatArmed, inDialog: false })) return;
  if (view === 'home') {
    setPanel(!$('panel').classList.contains('open'));
    render();
    return;
  }
  menuSheet = !menuSheet;
  if (menuSheet) { resourceSheet = false; kingdomBuildSite = ''; kingdomActionSheet = false; }
  setPanel(menuSheet);
  render();
};
$('panel-close').onclick = () => {
  if (view === 'campaignMapSelect') { view = 'home'; setPanel(false); render(); return; }
  setPanel(false); render(); $('context').focus();
};
$('notification-close').onclick = () => { $('notification').hidden = true; };
$('build-cancel').onclick = closeBuild;
$('build-commit').onclick = () => {
  if (!pendingBuild) return;
  const payload = pendingBuild;
  pendingBuild = null;
  if (payload.command) act(payload.command, payload.payload);
  else act('BUILD', payload);
};
document.addEventListener('pointerup', event => {
  if (!armed) return;
  if (armed.cancelled) { armed = null; suppressClick = true; return; }
  const inDialog = Boolean(event.target?.closest?.('#retreat'));
  if (retreatBlocksBackground({ retreatArmed, inDialog })) {
    const blocked = armed;
    armed = null;
    window.rebornChoice = { armed: blocked.id, released: '', applied: false, blocked: 'retreat' };
    return;
  }
  const released = event.target?.closest?.('button')?.dataset?.choice || '';
  const chosen = armed;
  armed = null;
  window.rebornChoice = { armed: chosen.id, released, applied: armedChoice(chosen.id, released) };
  if (chosen.id && released && chosen.id !== released) {
    suppressClick = true;
  }
});
document.addEventListener('pointermove', event => {
  if (armed && event.pointerId === armed.pointerId && Math.hypot(event.clientX - armed.x, event.clientY - armed.y) > 8) armed.cancelled = true;
});
document.addEventListener('pointercancel', () => { armed = null; mapArm = null; });
document.addEventListener('click', event => {
  if (!suppressClick) return;
  suppressClick = false;
  event.stopPropagation();
  event.preventDefault();
}, true);
function mapHit(node) {
  if (!node?.closest) return null;
  const target = node.closest('[data-target]');
  if (target?.dataset.target && target.dataset.kind) return { key: `${target.dataset.kind}:${target.dataset.target}`, kind: target.dataset.kind, id: target.dataset.target };
  const cell = node.closest('[data-cell]');
  if (!cell || cell.dataset.open !== '1') return null;
  const [x, y] = cell.dataset.cell.split(',').map(Number);
  if (!Number.isInteger(x) || !Number.isInteger(y)) return null;
  if (cell.dataset.kind === 'deployment') return { key: `deployment:${cell.dataset.cell}`, kind: 'deployment', cell: [x, y] };
  if (cell.dataset.kind === 'blast') return { key: `blast:${cell.dataset.cell}`, kind: 'blast', cell: [x, y] };
  return { key: `move:${cell.dataset.cell}`, kind: 'move', cell: [x, y] };
}
function releaseMap(clientX, clientY) {
  const armed = mapArm;
  mapArm = null;
  if (!armed || retreatArmed) return;
  if (view === 'defense') {
    if (!blastAim || !state?.defense || state.defense.status !== 'ACTIVE') return;
    const released = mapHit(document.elementFromPoint(clientX, clientY));
    if (!released || released.kind !== 'blast' || released.key !== armed.key) return;
    blastAim = false;
    swallowMapClick = true;
    act('DEFENSE_CAST', { x: released.cell[0] + 0.5, y: released.cell[1] + 0.5 });
    return;
  }
  if (view !== 'tactical' || !state?.battle) return;
  const released = mapHit(document.elementFromPoint(clientX, clientY));
  if (state.battle.status === 'PENDING' && state.battle.deployment) {
    if (released?.kind !== 'deployment' || !armed || released.key !== armed.key || !deploymentSelection) return;
    act('DEPLOY_BATTLE_STACK', { stackId: deploymentSelection, cell: released.cell });
    return;
  }
  if (state.battle.status !== 'ACTIVE') return;
  const active = activeStackId(state.battle);
  const actor = state.battle.stacks.find(item => item.id === active);
  if (!actor || actor.side !== 'p') return;
  const order = acceptMapActivation({ armed, released, intent: tacticalIntent, legal: legalTargets(state.battle, active) });
  if (!order) return;
  swallowMapClick = true;
  if (order.action === 'move') act('BATTLE', { action: 'move', stackId: active, to: order.to });
  else if (order.action === 'melee') act('BATTLE', meleeCommand(state.battle, active, order.targetId));
  else act('BATTLE', { action: 'strike', stackId: active, targetId: order.targetId });
}
$('world').addEventListener('pointerdown', event => {
  if (retreatArmed) { mapArm = null; return; }
  if (view === 'defense') {
    if (!blastAim) { mapArm = null; return; }
    const hit = mapHit(event.target);
    mapArm = hit?.kind === 'blast' ? { ...hit, pointerId: event.pointerId } : null;
    return;
  }
  if (view !== 'tactical') { mapArm = null; return; }
  const hit = mapHit(event.target);
  mapArm = hit ? { ...hit, pointerId: event.pointerId } : null;
});
$('world').addEventListener('pointerup', event => {
  if (!mapArm || event.pointerId !== mapArm.pointerId) return;
  releaseMap(event.clientX, event.clientY);
});
$('world').addEventListener('pointercancel', () => { mapArm = null; });
$('world').addEventListener('click', event => {
  if (!swallowMapClick) return;
  swallowMapClick = false;
  event.preventDefault();
  event.stopPropagation();
}, true);
$('retreat-cancel').addEventListener('click', () => { retreatArmed = false; retreatRestorePending = true; render(); });
$('retreat-confirm').addEventListener('click', () => confirmRetreat());
window.rebornHandleBack = () => {
  if (pendingBuild) { closeBuild(); return true; }
  if (retreatArmed) {
    retreatArmed = false;
    retreatRestorePending = true;
    render();
    return true;
  }
  if (view === 'campaignMapSelect') {
    view = 'home';
    setPanel(false);
    render();
    return true;
  }
  const panel = $('panel');
  if (panel && panel.classList.contains('open')) {
    setPanel(false);
    render();
    return true;
  }
  if (view && view !== 'kingdom' && view !== 'home') {
    view = 'kingdom';
    render();
    return true;
  }
  if (view === 'kingdom') {
    view = 'home';
    render();
    return true;
  }
  return false;
};
document.addEventListener('keydown', event => {
  if (event.key === 'Escape') {
    if (window.rebornHandleBack && window.rebornHandleBack()) {
      event.preventDefault();
      return;
    }
  }
  if (pendingBuild && event.key === 'Tab') {
    event.preventDefault();
    const next = document.activeElement === $('build-cancel') ? $('build-commit') : $('build-cancel');
    next.focus();
    return;
  }
  if (!retreatArmed) return;
  if (event.key !== 'Tab') return;
  const nodes = [$('retreat-cancel'), $('retreat-confirm')];
  const index = nodes.indexOf(document.activeElement);
  event.preventDefault();
  const step = event.shiftKey ? -1 : 1;
  nodes[(index + step + nodes.length) % nodes.length].focus();
});
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
  if (hit) { selected = hit.id; menuSheet = false; setPanel(true); render(); }
  else { selected = ''; setPanel(false); render(); }
});
function applyBackground(event, hidden) {
  const next = nextSuspended(suspended, event, hidden);
  if (next === suspended) return next && state ? Promise.resolve(persist()).then(ok => ok === true) : Promise.resolve(!state || saveQueue.status.kind === 'committed');
  suspended = next;
  if (next) {
    suspendAudio();
    if (!state) return Promise.resolve(true);
    catchUp(Date.now(), false);
    return Promise.resolve(persist()).then(ok => ok !== false);
  }
  resumeAudio();
  if (state) catchUp(Date.now(), true);
  render();
  return Promise.resolve(true);
}
window.rebornBackground = hidden => applyBackground('visibility', hidden);
window.rebornCommittedHead = () => saveQueue.status.kind === 'committed' ? structuredClone(saveQueue.status.head) : null;
window.addEventListener('blur', () => applyBackground('blur', true));
document.addEventListener('visibilitychange', () => applyBackground('visibility', document.hidden));
window.addEventListener('focus', () => applyBackground('focus', document.hidden));
window.addEventListener('pagehide', () => applyBackground('pagehide', true));
window.addEventListener('resize', () => { armed = null; mapArm = null; render(); });
if (state) {
  catchUp(Date.now(), true);
  if (resumeNote && !state.battle && !state.defense) view = 'home';
  persist();
  installLifecycle();
}
if ($('gate-report-dismiss')) $('gate-report-dismiss').addEventListener('click', () => { resumeNote = ''; render(); });
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
