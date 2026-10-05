// Reborn preview APK. Builds web assets, syncs generated www, then assembles the unsigned release.
import { spawn } from 'node:child_process';
import crypto from 'node:crypto';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(fileURLToPath(new URL('..', import.meta.url)));
const dist = path.join(root, 'dist');
const www = path.join(root, 'android', 'app', 'src', 'main', 'assets', 'www');
const preserveDir = path.join(root, 'qa', 'code-ready-20261004', 'preserved-apk');

function run(command, args, cwd) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, { cwd, stdio: 'inherit', shell: false });
    child.on('error', reject);
    child.on('exit', code => {
      if (code === 0) resolve();
      else reject(new Error(`${path.basename(command)} ${args.join(' ')} exited ${code}`));
    });
  });
}

async function preserveExisting() {
  await fs.mkdir(preserveDir, { recursive: true });
  const candidates = [
    ['android', 'app', 'build', 'outputs', 'apk', 'release', 'app-release-unsigned.apk'],
    ['android', 'app', 'build', 'outputs', 'apk', 'debug', 'app-debug.apk'],
  ];
  const kept = [];
  for (const parts of candidates) {
    const source = path.join(root, ...parts);
    try {
      await fs.access(source);
    } catch {
      continue;
    }
    const bytes = await fs.readFile(source);
    const hash = crypto.createHash('sha256').update(bytes).digest('hex').slice(0, 8);
    const named = path.join(preserveDir, `${hash}-${parts.at(-1)}`);
    try { await fs.access(named); }
    catch { await fs.copyFile(source, named); }
    const generic = path.join(preserveDir, parts.at(-1));
    let genericHash = '';
    try { genericHash = crypto.createHash('sha256').update(await fs.readFile(generic)).digest('hex').slice(0, 8); }
    catch { genericHash = ''; }
    if (genericHash && genericHash !== hash) {
      const retired = path.join(preserveDir, `${genericHash}-${parts.at(-1)}`);
      try { await fs.access(retired); }
      catch { await fs.copyFile(generic, retired); }
    }
    const stat = await fs.stat(named);
    kept.push({ file: path.relative(root, named), bytes: stat.size, sha256_8: hash });
  }
  return kept;
}

async function filesUnder(dir, prefix = '') {
  const found = [];
  let entries = [];
  try {
    entries = await fs.readdir(dir, { withFileTypes: true });
  } catch {
    return found;
  }
  for (const entry of entries) {
    const relative = prefix ? `${prefix}/${entry.name}` : entry.name;
    if (entry.isDirectory()) found.push(...await filesUnder(path.join(dir, entry.name), relative));
    else found.push(relative.replaceAll('\\', '/'));
  }
  return found;
}

async function syncWww() {
  await fs.mkdir(www, { recursive: true });
  const next = new Set(await filesUnder(dist));
  const previous = await filesUnder(www);
  for (const relative of previous) {
    if (!next.has(relative)) await fs.rm(path.join(www, relative), { force: true });
  }
  for (const relative of next) {
    const source = path.join(dist, relative);
    const target = path.join(www, relative);
    await fs.mkdir(path.dirname(target), { recursive: true });
    await fs.copyFile(source, target);
  }
  return { copied: next.size, removed: previous.filter(file => !next.has(file)).length };
}

const preserved = await preserveExisting();
console.log('Preserved existing APK copies: ' + (preserved.length ? JSON.stringify(preserved) : 'none present'));
await run(process.execPath, [path.join(root, 'scripts', 'build.mjs')], root);
const sync = await syncWww();
console.log(`Synchronized ${sync.copied} generated files into android www. Removed ${sync.removed} stale www files.`);
const androidDir = path.join(root, 'android');
if (process.platform === 'win32') {
  await run(process.env.ComSpec || 'cmd.exe', ['/d', '/c', 'gradlew.bat assembleRelease'], androidDir);
} else {
  await run(path.join(androidDir, 'gradlew'), ['assembleRelease'], androidDir);
}
const apk = path.join(root, 'android', 'app', 'build', 'outputs', 'apk', 'release', 'app-release-unsigned.apk');
const stat = await fs.stat(apk);
console.log(`Preview APK: ${apk} (${stat.size} bytes). Unsigned. Not installed.`);
