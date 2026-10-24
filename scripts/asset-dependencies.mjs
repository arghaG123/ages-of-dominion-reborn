import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const media = /^assets\/.+\.(png|jpe?g|webp|avif|svg|woff2?|ttf|ogg|wav|mp3|m4a)$/i;
export async function collectAssetDependencies(root, { includeProvenance = false } = {}) {
  const files = new Set(), consumers = new Map(), templates = [];
  function add(value, consumer) {
    if (!media.test(value)) return;
    const normalized = value.replaceAll('\\', '/');
    if (normalized.includes('${')) { templates.push({pattern:normalized,consumer}); return; }
    if (normalized.split('/').some(part => part === '..')) throw new Error(`Asset escapes root: ${value}`);
    files.add(normalized);
    if (!consumers.has(normalized)) consumers.set(normalized, new Set());
    consumers.get(normalized).add(consumer);
  }
  function visit(value, consumer) {
    if (typeof value === 'string') add(value, consumer);
    else if (Array.isArray(value)) for (const child of value) visit(child,consumer);
    else if (value && typeof value === 'object') for (const [key,child] of Object.entries(value)) {
      if (typeof child !== 'string') visit(child,consumer);
      else if (key === 'file' || key === 'uiFile' || key === 'displayFile' ||
        (includeProvenance && (key === 'terrain' || key.endsWith('File') || (key === 'outputPath' && value.gates?.runtime === 'PASS')))) add(child,consumer);
    }
  }
  async function walk(directory) {
    for (const entry of await fs.readdir(directory,{withFileTypes:true})) {
      const full = path.join(directory,entry.name);
      if (entry.isDirectory()) { await walk(full); continue; }
      const consumer = path.relative(root,full).replaceAll('\\','/');
      if (entry.name.endsWith('.json')) {
        const data = JSON.parse(await fs.readFile(full,'utf8'));
        if (!includeProvenance && entry.name === 'consumer-catalog-20261007.json') continue; // main.js uses dimensions, never outputPath.
        if (!includeProvenance && entry.name === 'mode-scenes.json') {
          for (const mode of ['adventure', 'tactical', 'defense']) visit(data[mode], consumer);
        } else if (!includeProvenance && entry.name === 'adventure-worlds.json') {
          // Geometry/reference history stays in JSON; campaignMapImage loads only productionMapFile.
          for (const world of Array.isArray(data) ? data : data.worlds || []) add(world.productionMapFile, consumer);
        } else if (!includeProvenance && entry.name === 'reviewed-source-selection.json') {
          for (const terrain of Object.values(data.kingdomTerrain || {})) add(terrain.displayFile || terrain.sourceFile, consumer);
          for (const item of Object.values(data.delivery || {})) add(item.uiFile || item.file, consumer);
        } else visit(data,consumer);
      }
      else if (/\.(js|css|html)$/.test(entry.name)) {
        const source = await fs.readFile(full,'utf8');
        for (const match of source.matchAll(/['"`](?:\.\/)?(assets\/[^'"`\r\n]+)['"`]/g)) add(match[1],consumer);
      }
    }
  }
  await walk(path.join(root,'src'));
  // Expand every matching template member, rather than accepting one matching file as closure.
  async function mediaUnder(directory) {
    const result = [];
    for (const entry of await fs.readdir(directory, { withFileTypes: true })) {
      const full = path.join(directory, entry.name);
      if (entry.isDirectory()) result.push(...await mediaUnder(full));
      else result.push(path.relative(root, full).replaceAll('\\', '/'));
    }
    return result;
  }
  const available = templates.length ? await mediaUnder(path.join(root, 'assets')) : [];
  for (const { pattern, consumer } of templates) {
    const expression = new RegExp('^' + pattern.split(/\$\{[^}]+\}/).map(part=>part.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')).join('[^/]+') + '$');
    for (const file of available) if (expression.test(file)) add(file, consumer);
  }
  // Runtime phase selection is a real consumer, not a second fixed asset list.
  const { kingdomPainting } = await import(new URL('../src/client/kingdom-view.js',import.meta.url));
  for(let age=0;age<8;age++) for(const phase of ['none','scaffold','built','tall']) {
    const state={age,walls:{level:phase==='tall'?2:phase==='built'?1:0},buildJobs:phase==='scaffold'?[{plotId:'walls'}]:[]};
    add(kingdomPainting(state).file,'src/client/kingdom-view.js');
  }
  const missing = [];
  for (const file of files) if (!(await fs.stat(path.join(root,file)).catch(()=>null))?.isFile()) missing.push(file);
  const unresolvedTemplates = templates.filter(({pattern}) => {
    const expression = new RegExp('^' + pattern.split(/\$\{[^}]+\}/).map(part=>part.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')).join('[^/]+') + '$');
    return ![...files].some(file=>expression.test(file));
  });
  return {files:[...files].sort(),missing,templates,unresolvedTemplates,consumers:Object.fromEntries([...consumers].map(([file,set])=>[file,[...set]]))};
}
if (process.argv[1] && fileURLToPath(import.meta.url) === path.resolve(process.argv[1])) console.log(JSON.stringify(await collectAssetDependencies(path.resolve(fileURLToPath(new URL('..',import.meta.url))))));
