import crypto from 'node:crypto';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { adaptProducerRow } from '../src/client/consumer-adapter.js';

const root = path.resolve(fileURLToPath(new URL('..', import.meta.url)));
const qa = path.join(root, 'qa/code-whole-build-20261007');
const node = process.execPath;

async function sha256(relative) {
  const bytes = await fs.readFile(path.join(root, relative));
  return { sha256: crypto.createHash('sha256').update(bytes).digest('hex'), bytes: bytes.length };
}

const environment = JSON.parse(await fs.readFile(path.join(root, 'docs/plan/ENVIRONMENT-ART-RESIDUAL-INTERFACE-2026-10-07.json'), 'utf8'));
const actors = JSON.parse(await fs.readFile(path.join(root, 'docs/plan/ACTORS-EQUIPMENT-RESIDUAL-INTERFACE-2026-10-07.json'), 'utf8'));
const audit = JSON.parse(await fs.readFile(path.join(root, 'qa/planner-final-images-20261007/per-id-status.json'), 'utf8'));
const scenes = JSON.parse(await fs.readFile(path.join(root, 'qa/image-residual-executor-20261007/environment/scenes.json'), 'utf8'));
const pixels = JSON.parse(await fs.readFile(path.join(qa, 'pixel-report.json'), 'utf8'));
const auditById = new Map(audit.rows.map(row => [row.id, row]));
const repairById = new Map(pixels.repairs.map(row => [row.id, row]));

async function hashOk(row) {
  if (!row?.source?.path || !row?.source?.sha256) return false;
  try {
    const source = await sha256(row.source.path);
    if (source.sha256 !== row.source.sha256) return false;
  } catch {
    return false;
  }
  if (!row.output?.path) return true;
  try {
    const output = await sha256(row.output.path);
    return output.sha256 === row.output.sha256;
  } catch {
    return false;
  }
}

const assets = [];
for (const row of environment.rows) {
  const ok = await hashOk(row);
  assets.push(adaptProducerRow(row, { producer: 'ENVIRONMENT', audit: auditById.get(row.id), hashOk: ok }));
}
for (const row of environment.supportRows || []) {
  const ok = await hashOk(row);
  assets.push(adaptProducerRow(row, { producer: 'ENVIRONMENT', support: true, audit: auditById.get(row.id), hashOk: ok }));
}
for (const scene of scenes) {
  assets.push(adaptProducerRow({
    id: scene.id,
    role: scene.role || 'scene-plate',
    status: scene.status || 'PARTIAL',
    age: null,
    source: scene.source,
    output: null,
    limitations: ['Inactive scene proposal. Legal affine and Hall scale stay frozen.'],
  }, { producer: 'ENVIRONMENT', scene: true }));
}
for (const row of actors.rows) {
  const ok = await hashOk(row);
  const material = pixels.materials?.[row.id];
  const repair = repairById.get(row.id);
  const asset = adaptProducerRow(row, {
    producer: 'ACTORS',
    audit: auditById.get(row.id),
    hashOk: ok,
    repair: repair?.subjectPreserved ? repair : null,
  });
  if (material && !material.pass && asset.gates.runtime === 'PASS') {
    asset.gates.matte = 'FAIL';
    asset.gates.runtime = 'BLOCKED';
    asset.blockedBy.push(material.reason || 'magenta or empty material');
    asset.limitations.push(`opaque ${material.opaqueFraction}, magenta ${material.magentaFraction}`);
  }
  assets.push(asset);
}

const summary = {
  total: assets.length,
  runtimePass: assets.filter(asset => asset.gates.runtime === 'PASS').map(asset => asset.id),
  matteFail: assets.filter(asset => asset.gates.matte === 'FAIL').map(asset => asset.id),
  blocked: assets.filter(asset => asset.gates.runtime === 'BLOCKED').length,
  partial: assets.filter(asset => asset.gates.runtime === 'PARTIAL').length,
};
await fs.mkdir(qa, { recursive: true });
await fs.writeFile(path.join(root, 'src/data/consumer-catalog-20261007.json'), JSON.stringify({
  version: 'code-consumer-20261007',
  node,
  generatedFrom: [
    'docs/plan/ENVIRONMENT-ART-RESIDUAL-INTERFACE-2026-10-07.json',
    'docs/plan/ACTORS-EQUIPMENT-RESIDUAL-INTERFACE-2026-10-07.json',
  ],
  assets,
}, null, 2));
await fs.writeFile(path.join(qa, 'catalog-summary.json'), JSON.stringify(summary, null, 2));

const ages = ['stone', 'bronze', 'iron', 'medieval', 'gunpowder', 'industrial', 'modern', 'future'];
const slots = ['helm', 'weapon', 'offhand', 'armor', 'boots', 'accessory'];
const icons = [];
for (const asset of assets) {
  if (asset.gates.runtime !== 'PASS' || asset.use !== 'MATERIAL' || !asset.id.startsWith('gear-')) continue;
  const parts = asset.id.split('-');
  const slot = parts.at(-1);
  const ageName = parts[1];
  if (!slots.includes(slot)) continue;
  icons.push({
    id: asset.id,
    slot,
    age: ages.indexOf(ageName),
    file: asset.outputPath,
    width: asset.dimensions?.width || 64,
    height: asset.dimensions?.height || 64,
  });
}
await fs.writeFile(path.join(root, 'src/data/gear-icons-20261007.json'), JSON.stringify({
  version: 'code-gear-icons-20261007',
  icons,
}, null, 2));

const overrides = JSON.parse(await fs.readFile(path.join(root, 'src/data/plate-overrides-20261007.json'), 'utf8'));
const troopKeys = {
  'troop-stone-melee': '0-melee',
  'troop-stone-ranged': '0-ranged',
  'troop-industrial-ranged': '5-ranged',
  'troop-industrial-heavy': '5-heavy',
};
for (const [id, key] of Object.entries(troopKeys)) {
  const asset = assets.find(item => item.id === id && item.producer === 'CODE' || (item.id === id && item.gates.runtime === 'PASS' && item.outputPath?.includes('runtime-code-20261007')));
  const repair = repairById.get(id);
  if (!repair?.subjectPreserved || !asset || asset.gates.runtime !== 'PASS') continue;
  overrides.troops[key] = {
    ...(overrides.troops[key] || {}),
    file: repair.outputPath,
    width: repair.dimensions.width,
    height: repair.dimensions.height,
    source: repair.sourcePath,
    sourceSHA256: repair.actualSourceSha256,
    sha256: repair.outputSha256,
    pose: 'single',
    maxVisibleCssPx: 130,
    provisional: 'Code consumer crop from the hash-bound native. The outline derivative is not used.',
  };
}
await fs.writeFile(path.join(root, 'src/data/plate-overrides-20261007.json'), JSON.stringify(overrides, null, 2));
console.log(JSON.stringify({ runtimePass: summary.runtimePass.length, matteFail: summary.matteFail.length, icons: icons.length, repairs: pixels.repairs.map(item => [item.id, item.subjectPreserved]) }, null, 2));
