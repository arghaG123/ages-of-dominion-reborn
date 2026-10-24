import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import { collectAssetDependencies } from './asset-dependencies.mjs';

const hash = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
export async function verifyWebBuild(root) {
  const dist = path.join(root, 'dist');
  const report = JSON.parse(await fs.readFile(path.join(dist, 'dependency-closure.json'), 'utf8'));
  const dependencies = await collectAssetDependencies(root);
  if (dependencies.missing.length || dependencies.unresolvedTemplates.length) throw new Error('Source dependencies unresolved');
  const expected = [...dependencies.files].sort();
  const actual = report.assets.map(row => row.source).sort();
  if (JSON.stringify(expected) !== JSON.stringify(actual)) throw new Error('Build asset set is stale');
  const mapping = JSON.parse(await fs.readFile(path.join(dist, 'src/data/build-assets.json'), 'utf8'));
  for (const row of report.assets) {
    if (row.source.split('/').includes('..') || row.file.split('/').includes('..') || !row.source.startsWith('assets/') || !row.file.startsWith('assets/')) throw new Error('Unsafe asset path');
    if (hash(await fs.readFile(path.join(root, row.source))) !== row.sourceSha256) throw new Error(`Source changed: ${row.source}`);
    if (hash(await fs.readFile(path.join(dist, row.file))) !== row.sha256) throw new Error(`Build changed: ${row.file}`);
    if ((mapping[row.source] || row.source) !== row.file) throw new Error(`Build URL map changed: ${row.source}`);
  }
  async function checkSource(directory) {
    for (const entry of await fs.readdir(path.join(root, directory), { withFileTypes: true })) {
      const relative = path.join(directory, entry.name);
      if (entry.isDirectory()) await checkSource(relative);
      else if (relative.replaceAll('\\', '/') !== 'src/data/build-assets.json') {
        if (!(await fs.readFile(path.join(root, relative))).equals(await fs.readFile(path.join(dist, relative)))) throw new Error(`Built source is stale: ${relative}`);
      }
    }
  }
  await checkSource('src');
  if (!(await fs.readFile(path.join(root, 'index.html'))).equals(await fs.readFile(path.join(dist, 'index.html')))) throw new Error('Built index is stale');
  if (!report.losslessWebp || report.missing.length || report.networkDependency) throw new Error('Lossless build verification is incomplete');
  return { files: report.assets.length, assetBytes: report.assetBytes, sourceAndOutputHashesVerified: true, sourceParity: true };
}
