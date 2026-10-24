import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { spawn } from 'node:child_process';
import { collectAssetDependencies } from './asset-dependencies.mjs';
const root = path.resolve(fileURLToPath(new URL('..', import.meta.url)));
const dependencies = await collectAssetDependencies(root);
if (dependencies.missing.length || dependencies.unresolvedTemplates.length) throw new Error('Unresolved current dependencies: ' + JSON.stringify({missing:dependencies.missing,templates:dependencies.unresolvedTemplates}));
const dist = path.join(root, 'dist');
await fs.rm(dist, { recursive: true, force: true });
await fs.mkdir(dist, { recursive: true });
await fs.cp(path.join(root, 'index.html'), path.join(dist, 'index.html'));
await fs.cp(path.join(root, 'src'), path.join(dist, 'src'), { recursive: true });
const closure = [];
const originalImages = process.argv.includes('--original-images');
if (!originalImages) {
  const inputPath = path.join(dist, 'asset-inputs.json');
  await fs.writeFile(inputPath, JSON.stringify(dependencies.files));
  await new Promise((resolve, reject) => {
    const child = spawn(process.env.PYTHON || 'python', [path.join(root, 'scripts/build-lossless-webp.py'), '--root', root, '--dist', dist, '--inputs', inputPath], { cwd: root, stdio: 'inherit', shell: false });
    child.on('error', reject);
    child.on('exit', code => code === 0 ? resolve() : reject(new Error(`Lossless asset verification failed: ${code}`)));
  });
  await fs.unlink(inputPath);
  const encoding = JSON.parse(await fs.readFile(path.join(dist, 'asset-encoding.json'), 'utf8'));
  closure.push(...encoding.assets);
}
for (const relative of originalImages ? dependencies.files : []) {
  const source = path.join(root, relative);
  const target = path.join(dist, relative);
  await fs.mkdir(path.dirname(target), { recursive: true });
  await fs.copyFile(source, target);
  const bytes = await fs.readFile(target);
  closure.push({ source: relative, file: relative.replaceAll('\\', '/'), sourceBytes: bytes.length, bytes: bytes.length, sha256: crypto.createHash('sha256').update(bytes).digest('hex') });
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
const report = { files: closure.length, sourceAssetBytes: closure.reduce((sum, item) => sum + item.sourceBytes, 0), assetBytes: closure.reduce((sum, item) => sum + item.bytes, 0), losslessWebp: !originalImages, provenanceImagesIncluded: false, assets: closure, missing, escaping, svgNamespaceIdentifiers: namespaces.length, networkDependency: escaping.length > 0 };
const reportPath = path.resolve(root, process.env.DIST_CLOSURE_OUT || 'dist/dependency-closure.json');
await fs.mkdir(path.dirname(reportPath), { recursive: true });
await fs.writeFile(reportPath, JSON.stringify(report, null, 2) + '\n');
if (missing.length || escaping.length) {
  console.error(JSON.stringify(report));
  process.exit(1);
}
console.log('Built standalone dist with ' + closure.length + ' local assets and no network references.');
