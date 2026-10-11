// Isolated adaptation of scripts/build.mjs; source preserved.
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';
const root = process.cwd();
const dist = path.join(root, 'qa/planner-device-handoff-20261009/static-package');
await fs.rm(dist, { recursive: true, force: true });
await fs.mkdir(dist, { recursive: true });
await fs.cp(path.join(root, 'index.html'), path.join(dist, 'index.html'));
await fs.cp(path.join(root, 'src'), path.join(dist, 'src'), { recursive: true });
const selection = JSON.parse(await fs.readFile(path.join(root, 'src/data/reviewed-source-selection.json'), 'utf8'));
const scene = JSON.parse(await fs.readFile(path.join(root, 'src/data/stone-scene.json'), 'utf8'));
const actorAtlas = JSON.parse(await fs.readFile(path.join(root, 'src/data/actor-atlas.json'), 'utf8'));
const plateCatalog = JSON.parse(await fs.readFile(path.join(root, 'src/data/plate-catalog.json'), 'utf8'));
const ageBuildings = JSON.parse(await fs.readFile(path.join(root, 'src/data/age-buildings.json'), 'utf8'));
const portraitCards = JSON.parse(await fs.readFile(path.join(root, 'src/data/portrait-cards.json'), 'utf8'));
const modeScenes = JSON.parse(await fs.readFile(path.join(root, 'src/data/mode-scenes.json'), 'utf8'));
const plateOverrides = JSON.parse(await fs.readFile(path.join(root, 'src/data/plate-overrides-20261007.json'), 'utf8'));
const gearIcons = JSON.parse(await fs.readFile(path.join(root, 'src/data/gear-icons-20261007.json'), 'utf8'));
const consumerCatalog = JSON.parse(await fs.readFile(path.join(root, 'src/data/consumer-catalog-20261007.json'), 'utf8').catch(() => '{"assets":[]}'));
const files = new Set();
const visit = (value) => {
  if (!value || typeof value !== 'object') return;
  for (const [key, item] of Object.entries(value)) {
    if (typeof item === 'string' && (key === 'file' || key === 'terrain' || key.endsWith('File') || key === 'uiFile' || key === 'sourceFile' || key === 'displayFile')) files.add(item);
    else visit(item);
  }
};
visit(selection);
visit(scene);
visit(actorAtlas);
visit(plateCatalog);
visit(ageBuildings);
visit(portraitCards);
visit(plateOverrides);
visit(gearIcons);
for (const asset of consumerCatalog.assets || []) {
  if (asset.gates?.runtime === 'PASS' && typeof asset.outputPath === 'string') files.add(asset.outputPath);
}
for (const mode of ['adventure', 'tactical', 'defense']) {
  for (const file of modeScenes[mode] || []) files.add(file);
}
const closure = [];
for (const relative of files) {
  const source = path.join(root, relative);
  const target = path.join(dist, relative);
  await fs.mkdir(path.dirname(target), { recursive: true });
  await fs.copyFile(source, target);
  const bytes = await fs.readFile(target);
  closure.push({ file: relative.replaceAll('\\', '/'), sha256: crypto.createHash('sha256').update(bytes).digest('hex') });
}
const textFiles = [];
const walk = async (dir) => {
  for (const entry of await fs.readdir(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) await walk(full);
    else if (/\.(html|js|css|json|mjs)$/.test(entry.name)) textFiles.push(full);
  }
};
await walk(dist);
const escaping = [];
const namespaces = [];
for (const file of textFiles) {
  const text = await fs.readFile(file, 'utf8');
  const urls = text.match(/https?:\/\/[^\s"'`)<>]+/g) || [];
  for (const url of urls) {
    if (url === 'http://www.w3.org/2000/svg') namespaces.push(path.relative(dist, file));
    else escaping.push(path.relative(dist, file) + ' ' + url);
  }
}
const missing = [];
for (const item of closure) if (!await fs.stat(path.join(dist, item.file)).catch(() => null)) missing.push(item.file);
const report = { files: closure.length, assets: closure, missing, escaping, svgNamespaceIdentifiers: namespaces.length, networkDependency: escaping.length > 0 };
await fs.mkdir(path.join(root, 'qa/planner-device-handoff-20261009'), { recursive: true });
await fs.writeFile(path.join(root, 'qa/planner-device-handoff-20261009/dist-closure.json'), JSON.stringify(report, null, 2) + '\n');
if (missing.length || escaping.length) {
  console.error(JSON.stringify(report));
  process.exit(1);
}
console.log('Built standalone dist with ' + closure.length + ' local assets and no network references.');
