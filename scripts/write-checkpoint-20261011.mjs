// Assembles the 11 October Code + Image execution checkpoint from the machine-readable evidence
// already written by the verification scripts. Pure aggregation; no re-measurement.
import fs from 'node:fs';
import crypto from 'node:crypto';
import { execSync } from 'node:child_process';

const read = file => JSON.parse(fs.readFileSync(file, 'utf8'));
const sha = file => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const journey = read('qa/code-image-complete-20261011/earned-journey.json');
const pkg = read('qa/code-image-complete-20261011/package-check.json');
const regression = read('qa/code-image-complete-20261011/regression/browser-retreat-army.json');
const despill = read('qa/image-complete-20261011/plate-despill.json');
const bodies = read('src/data/hero-bodies-20261011.json');
const face = read('docs/plan/IMAGE-COMPLETE-INTERFACE-2026-10-11.json');
const rebind = read('qa/image-complete-20261011/native-rebind.json');
const git = execSync('git status --short', { encoding: 'utf8' }).trim().split(/\r?\n/).filter(Boolean);
const head = execSync('git rev-parse HEAD', { encoding: 'utf8' }).trim();
const testOutput = execSync('node --test ' + fs.readdirSync('tests').filter(f => f.endsWith('.test.mjs')).map(f => 'tests/' + f).join(' '), { encoding: 'utf8' });
const tests = { pass: Number(/ℹ pass (\d+)/.exec(testOutput)?.[1]), fail: Number(/ℹ fail (\d+)/.exec(testOutput)?.[1]), total: Number(/ℹ tests (\d+)/.exec(testOutput)?.[1]) };

const matrix = [
  ['REQ-ages', 'Eight ages, three modes, six slots, connected campaign', 'IMPLEMENTED_PARTIALLY_VERIFIED', 'Core rules cover eight ages; earned browser journey verified Stone Age day 1-3 only (build, recruit, guard fight, forge, equip, siege loss, war modes, story, settings, slots).'],
  ['REQ-kingdom', 'Natural Kingdom economy and tutorial', 'VERIFIED_IN_BROWSER', 'Real-time production, scaffold durations and affordability waits (Armory 124 s, forge 174 s) exercised; 17 sites; tutorial steps advance.'],
  ['REQ-hero', 'Realistic Hero equipment room', 'IMPLEMENTED_VERIFIED', 'Seven static standing bodies (hero-bodies-20261011) with six slot cards, class cards, stats; Healer falls back to portrait (body missing).'],
  ['REQ-army', 'Army with reviewed plates and terrain backdrop', 'IMPLEMENTED_VERIFIED', 'Slinger adopted; captions 14 CSS px inside the stage at four sizes; terrain backdrop per age.'],
  ['REQ-forge', 'Forge with anvil composition and quality menu', 'IMPLEMENTED_VERIFIED', 'Six slot rows, selected piece on the anvil, cost/gain/worn lines, lower-quality recipes exposed; forge+equip verified.'],
  ['REQ-adventure', 'Adventure map with town approach, guards, dwelling', 'IMPLEMENTED_VERIFIED', 'Dwelling claim UI added; guard encounter settled once; reload persists exact facts.'],
  ['REQ-tactical', 'Tactical 7x10 battles, Retreat modal', 'VERIFIED_IN_BROWSER', 'Guard, skirmish, duel, challenge flows settle once; programmatic Retreat navigation PASS.'],
  ['REQ-defense', 'Defense 9x15 siege and endless', 'VERIFIED_IN_BROWSER_WITH_LOSS', 'Siege ran with starter towers, hero and one stack; lost after 2 of 5 waves (documented legitimate outcome); endless extends; settlement survives reload.'],
  ['REQ-war', 'Five War flows', 'VERIFIED_IN_BROWSER', 'Skirmish, Campaign Siege, Tactical Duel, Challenge, Endless all exercised.'],
  ['REQ-narrative', 'Story, rival, chapter choice, milestone, saves', 'VERIFIED_IN_BROWSER', 'Rival chosen, chapter choice recorded, milestone recorded, slot save/load round trip.'],
  ['REQ-viewports', 'Four landscape viewports plus portrait guidance', 'VERIFIED_IN_BROWSER', '40 screen/viewport combinations: no broken images, no interactive target under 48 px; portrait shows rotate guidance and keeps state.'],
  ['REQ-image-bodies', 'Seven class bodies processed', 'STATIC_READY_NOT_RIGGED', 'Matte-cleaned static standing bodies; no rigs or atlases; Healer missing.'],
  ['REQ-image-mattes', 'Magenta residue removal on live plates', 'REPAIRED_LOCALLY', `${despill.summary.repaired} plates despilled, ${despill.summary.kept} kept; residual above 1%: ${despill.summary.residualAbove1pct.join(', ')}.`],
  ['REQ-image-scenes', '32 scene spatial registration', 'FAIL_OPEN', 'All 32 scenes remain spatially unregistered; lane/pad overlays do not match painted terrain. No registered terrain edit was produced; paid constrained edits not performed.'],
  ['REQ-image-rigs', 'Articulated rigs/atlases', 'NOT_DONE', 'No new rig work; existing measured-part actors unchanged.'],
  ['REQ-package', 'Web dist and APK parity, zero permissions, preview id', 'VERIFIED', `${pkg.expectedFiles} files identical across source/dist/www/APK; CRC clean; ${pkg.manifestApplicationId}; permissions ${JSON.stringify(pkg.manifestPermissions)}.`],
  ['REQ-device', 'Physical-device install', 'STOPPED', 'Owner permission not renewed; no device work.'],
  ['REQ-owner', 'Owner visual acceptance', 'UNVERIFIED', 'Separate gate.'],
  ['REQ-morale', 'Positive morale behaviour', 'PENDING_OWNER_DECISION', 'No extra turns invented.'],
];

const checkpoint = {
  version: 'code-image-complete-20261011',
  generatedAt: new Date().toISOString(),
  gitHeadBefore: head,
  overall: 'INCOMPLETE',
  openMandatoryGates: ['32 scene spatial registration FAIL', 'rigs/atlases absent', 'Healer body missing', 'eight-age earned play beyond Stone Age not demonstrated', 'owner acceptance UNVERIFIED', 'device STOPPED'],
  tests,
  earnedJourney: { file: 'qa/code-image-complete-20261011/earned-journey.json', ...journey.summary, pass: journey.pass, steps: journey.steps, screens: journey.screens.length },
  regression: { file: 'qa/code-image-complete-20261011/regression/browser-retreat-army.json', checks: regression.checks.map(c => ({ id: c.id, pass: c.pass })), screensFailed: regression.screenChecks.filter(s => !s.pass).length },
  package: { file: 'qa/code-image-complete-20261011/package-check.json', pass: pkg.pass, apk: pkg.apk, apkBytes: pkg.apkBytes, apkSHA256: pkg.apkSHA256, files: pkg.expectedFiles, applicationId: pkg.manifestApplicationId, permissions: pkg.manifestPermissions, signed: pkg.signed, note: 'Gradle packaging replaced the release output directory: the stale 4 October app-release-unsigned.apk (319,425,603 bytes, 02f85e52...) no longer exists; no preservation copy was made (no-backup constraint). The 3 October debug APK remains.' },
  image: {
    interface: { file: 'docs/plan/IMAGE-COMPLETE-INTERFACE-2026-10-11.json', sha256: sha('docs/plan/IMAGE-COMPLETE-INTERFACE-2026-10-11.json'), imageWorkComplete: face.imageWorkComplete, readySubset: face.readySubset },
    nativeRebind: rebind.status ? { status: rebind.status, pointersRebound: rebind.pointersRebound } : rebind,
    bodies: { contract: 'src/data/hero-bodies-20261011.json', ready: Object.keys(bodies.bodies), missing: Object.keys(bodies.missing || {}) },
    plateDespill: despill.summary,
    adoptedPlates: ['troops 0-ranged Slinger (image-vertex-repair-20261009)'],
    paidGeneration: 'NONE performed. No provider, account, IAM, billing or CLI change.',
  },
  budget: { hardCapUsd: 80, reserveReleasedOnce: true, effectiveReserve: 0, priorLiabilityUsd: 64.8327, capacityBeforeLaterLiabilitiesUsd: 15.1673, unknownHoldsUsd: [0.2872, 0.4144], invoices: 'UNKNOWN', changedByThisPass: false },
  constraints: { backupsOrZips: 'none created', originalsModified: false, deviceWork: 'none', gitWriteActions: 'none (no add/commit/push/reset/stash/clean)', moraleDecision: 'PENDING_OWNER_DECISION' },
  requirementMatrix: matrix.map(([id, requirement, status, evidence]) => ({ id, requirement, status, evidence })),
  changedFiles: git,
};
fs.writeFileSync('qa/code-image-complete-20261011/checkpoint.json', JSON.stringify(checkpoint, null, 2) + '\n');
console.log(JSON.stringify({ tests, journey: journey.summary, package: pkg.pass, regression: regression.checks.every(c => c.pass), changed: git.length }));
