// Kingdom ground and wall state. The painting already contains the wall.
// Stretched run, corner and gate stamps are not the finished wall.
import { wallPresentation } from './presentation.js';

export const KINGDOM_AGES = ['stone', 'bronze', 'iron', 'medieval', 'gunpowder', 'industrial', 'modern', 'future'];

export const WALL_KIND = {
  stone: 'timber-palisade',
  bronze: 'bronze-faced-palisade',
  iron: 'iron-stake-wall',
  medieval: 'stone-curtain',
  gunpowder: 'brick-bastion',
  industrial: 'riveted-plate',
  modern: 'concrete-barrier',
  future: 'composite-barrier',
};

const STONE_FAMILY = 'assets/derivatives/kingdom-stone-populated-20261021';
const AGE_FAMILY = 'assets/derivatives/kingdom-families-20261018';

// Level 0 is open ground. A wall job is scaffold and not a finished wall.
// Level 1 is that age's wall. Level 2 and higher is the same wall, built taller.
export function wallPhase(state) {
  const level = state?.walls?.level || 0;
  const job = Array.isArray(state?.buildJobs) && state.buildJobs.some(item => item.plotId === 'walls');
  if (job) return 'scaffold';
  if (level >= 2) return 'tall';
  if (level === 1) return 'built';
  return 'none';
}

export function kingdomPainting(state) {
  const age = KINGDOM_AGES[state?.age] || 'stone';
  const phase = wallPhase(state);
  const wallKind = phase === 'built' || phase === 'tall' ? WALL_KIND[age] : phase;
  const stoneStateFile = phase === 'scaffold'
    ? 'stone-scaffold.png'
    : phase === 'built'
      ? 'stone-wall.png'
      : phase === 'tall'
        ? 'stone-wall-tall.png'
        : 'stone-ground.png';
  const file = age === 'stone'
    ? `${STONE_FAMILY}/${stoneStateFile}`
    : `${AGE_FAMILY}/${age}/${phase === 'none' ? 'ground' : phase === 'built' ? 'wall' : phase === 'tall' ? 'wall-tall' : phase}.webp`;
  return {
    age,
    phase,
    file,
    wallKind,
    stamps: [],
  };
}

// Attributes for the kingdom wall group. No segment, corner or gate image is attached.
export function wallHostAttrs(state, depth = 'back') {
  const painting = kingdomPainting(state);
  const level = state?.walls?.level || 0;
  return {
    'data-walls': painting.phase === 'none' ? 'unbuilt' : painting.phase === 'scaffold' ? 'scaffold' : 'built',
    'data-walls-phase': painting.phase,
    'data-walls-level': String(level),
    'data-walls-painting': painting.file,
    'data-walls-kind': painting.wallKind,
    'data-wall-stamps': '0',
    'data-wall-depth': depth,
    'pointer-events': 'none',
  };
}

// Building tutorials keep one genuinely empty, idle plot highlighted.
// Steps 0-3 are the four construction actions; later steps target other surfaces.
export function tutorialBuildSiteId(state, sites) {
  const step = state?.tutorial?.step;
  if (state?.tutorial?.skipped || !Number.isInteger(step) || step < 0 || step > 3) return '';
  const plots = new Map((Array.isArray(state?.plots) ? state.plots : []).map(plot => [plot.id, plot]));
  const busy = new Set((Array.isArray(state?.buildJobs) ? state.buildJobs : []).map(job => job.plotId));
  return (Array.isArray(sites) ? sites : []).find(site => {
    if (!site?.id || site.id === 'townhall' || busy.has(site.id)) return false;
    const plot = plots.get(site.id);
    return plot && plot.type == null && plot.level === 0;
  })?.id || '';
}

// Empty ground has no filled pad. One tutorial site may keep a dashed outline.
// A built site contributes its building art and no blank pad.
export function plotPresentation({ plot, job, measured, tutorialSiteId, selected }) {
  if (measured?.file && !job && plot.level) {
    return { state: 'built', art: measured.file, pad: false, outline: selected ? 'selected' : null, clearing: null };
  }
  if (job) return { state: 'scaffold', art: null, pad: false, outline: selected ? 'selected' : null, clearing: null };
  if (plot.level) return { state: 'built', art: null, pad: false, outline: selected ? 'selected' : 'built', clearing: null };
  if (plot.id === tutorialSiteId) return { state: 'empty', art: null, pad: false, outline: 'tutorial', clearing: 'ground' };
  if (plot.id === selected) return { state: 'empty', art: null, pad: false, outline: 'selected', clearing: null };
  return { state: 'empty', art: null, pad: false, outline: null, clearing: 'ground' };
}

export function kingdomWallTrace(geo) {
  return wallPresentation(geo);
}
