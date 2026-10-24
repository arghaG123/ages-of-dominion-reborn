import fs from 'node:fs';
import { execSync } from 'node:child_process';
import crypto from 'node:crypto';

function hashFile(p) {
  if (!fs.existsSync(p)) return null;
  const buf = fs.readFileSync(p);
  return crypto.createHash('sha256').update(buf).digest('hex');
}

let gitHead = 'unknown';
let gitBranch = 'unknown';
let gitStatus = '';
try {
  gitHead = execSync('git rev-parse HEAD', { encoding: 'utf8' }).trim();
  gitBranch = execSync('git rev-parse --abbrev-ref HEAD', { encoding: 'utf8' }).trim();
  gitStatus = execSync('git status --porcelain', { encoding: 'utf8' }).trim();
} catch (e) {
  gitStatus = 'git query unavailable';
}

const nodeVersion = process.version;
let pythonVersion = 'unknown';
try {
  pythonVersion = execSync('python --version', { encoding: 'utf8' }).trim();
} catch {}

const keyFiles = [
  'src/client/main.js',
  'src/client/presentation.js',
  'src/client/actor.js',
  'src/client/hero-room.js',
  'src/core/campaign.js',
  'src/core/battle.js',
  'src/core/defense.js',
  'src/core/save.js',
  'src/core/storage-adapter.js',
  'src/data/wall-segments-20261016.json',
  'src/data/hero-bodies-20261011.json',
  'src/data/mode-scenes.json',
  'assets/derivatives/mock-led-20261016/walls/stone/run.png',
  'assets/derivatives/mock-led-20261016/walls/stone/corner.png',
  'assets/derivatives/mock-led-20261016/walls/stone/gate.png',
  'assets/derivatives/mock-led-20261016/bodies/class-healer-standing-body.png'
];

const fileHashes = {};
for (const f of keyFiles) {
  fileHashes[f] = {
    exists: fs.existsSync(f),
    sizeBytes: fs.existsSync(f) ? fs.statSync(f).size : 0,
    sha256: hashFile(f)
  };
}

const baseline = {
  evaluatedAt: new Date().toISOString(),
  environment: {
    gitHead,
    gitBranch,
    nodeVersion,
    pythonVersion,
    workspace: 'C:\\dev\\ages-of-dominion-reborn',
  },
  gitDirtyFiles: gitStatus.split('\n').filter(Boolean),
  repairedAssets: {
    healerStandingBody: {
      path: 'assets/derivatives/mock-led-20261016/bodies/class-healer-standing-body.png',
      sha256: fileHashes['assets/derivatives/mock-led-20261016/bodies/class-healer-standing-body.png']?.sha256,
      matteCleaned: true,
      whiteRemnantBelowStaffRemoved: true
    },
    stoneWalls: {
      run: fileHashes['assets/derivatives/mock-led-20261016/walls/stone/run.png'],
      corner: fileHashes['assets/derivatives/mock-led-20261016/walls/stone/corner.png'],
      gate: fileHashes['assets/derivatives/mock-led-20261016/walls/stone/gate.png'],
      timberPalisadeExtracted: true
    }
  },
  keyFileInventory: fileHashes,
  governingContract: 'docs/plan/ONE-COMPLETE-EXECUTOR-CONTINUATION-2026-10-16.txt',
};

fs.mkdirSync('qa/mock-led-executor-20261016', { recursive: true });
fs.writeFileSync('qa/mock-led-executor-20261016/baseline.json', JSON.stringify(baseline, null, 2));
console.log('Successfully wrote qa/mock-led-executor-20261016/baseline.json');
