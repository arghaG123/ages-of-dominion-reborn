import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(fileURLToPath(new URL('..', import.meta.url)));
const folders = {};
async function bytesUnder(directory) {
  let bytes = 0;
  for (const entry of await fs.readdir(directory, { withFileTypes: true })) {
    const full = path.join(directory, entry.name);
    if (entry.isDirectory()) bytes += await bytesUnder(full);
    else if (entry.isFile()) bytes += (await fs.stat(full)).size;
  }
  return bytes;
}
for (const entry of await fs.readdir(root, { withFileTypes: true })) {
  const full = path.join(root, entry.name);
  if (entry.isDirectory()) folders[entry.name] = await bytesUnder(full);
  else if (entry.isFile()) folders[entry.name] = (await fs.stat(full)).size;
}
const totalBytes = Object.values(folders).reduce((sum, value) => sum + value, 0);
const report = {
  totalBytes, gitBytes: folders['.git'],
  limits: { totalBytes: 8_000_000_000, gitBytes: 1_500_000_000 },
  pass: totalBytes < 8_000_000_000 && folders['.git'] < 1_500_000_000,
  folders,
};
console.log(JSON.stringify(report, null, 2));
if (!report.pass) process.exitCode = 1;
