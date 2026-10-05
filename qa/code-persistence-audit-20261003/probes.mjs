// Planner QA: pure in-memory probes only; no save, runtime, asset or provider writes.
import fs from 'node:fs/promises';
import data from '../../src/data/reference-data.json' with { type: 'json' };
import contract from '../../src/data/implementation-contract.json' with { type: 'json' };
import { newCampaign, validate } from '../../src/core/campaign.js';
import { createDefense, validateDefense, advanceDefense } from '../../src/core/defense.js';
const base = newCampaign(contract, data, 1000);
const defense = createDefense(base, data, { practice: 'siege', waves: 3 });
const edits = [
  ['negative-time', s => { s.time = -1; }],
  ['invalid-queue', s => { s.queue = 'corrupt'; }],
  ['negative-tower-damage', s => { s.towers[0].dmg = -10; }],
  ['empty-active-queue', s => { s.queue = []; }],
  ['false-resolved-victory', s => { s.status = 'RESOLVED'; s.pendingSettlement = true; s.winner = 'p'; }],
];
const rows = edits.map(([id, edit]) => {
  const session = structuredClone(defense); edit(session);
  let directAccepted = false, campaignAccepted = false;
  try { validateDefense(session); directAccepted = true; } catch {}
  try { validate({ ...structuredClone(base), defense: session }, data); campaignAccepted = true; } catch {}
  return { id, directAccepted, campaignAccepted, status: campaignAccepted ? 'FAIL' : 'PASS' };
});
// Expedite only this isolated diagnostic, to expose the finite Endless termination.
let endless = createDefense(base, data, { practice: 'endless', waves: 3 });
endless.towers = [];
for (const enemy of endless.queue) { enemy.spawnAt = 0; enemy.hp = 0; }
endless = advanceDefense(endless, 1 / 60);
const firstExtension = { waves: endless.waves, extensions: endless.extensions, status: endless.status };
for (const enemy of endless.queue) { enemy.spawnAt = 0; enemy.hp = 0; }
endless = advanceDefense(endless, 1 / 60);
const endlessResult = { firstExtension, secondClear: { waves: endless.waves, extensions: endless.extensions, status: endless.status, winner: endless.winner }, status: endless.status === 'RESOLVED' ? 'FAIL' : 'PASS', scope: 'Isolated clear fixture; no campaign writes or balance claim' };
const result = { at: new Date().toISOString(), rows, endless: endlessResult };
await fs.writeFile(new URL('./probes.json', import.meta.url), JSON.stringify(result, null, 2));
console.log(JSON.stringify(result));
