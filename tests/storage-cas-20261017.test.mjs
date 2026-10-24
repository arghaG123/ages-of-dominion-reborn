import test from 'node:test';
import assert from 'node:assert/strict';
import data from '../src/data/reference-data.json' with { type: 'json' };
import contract from '../src/data/implementation-contract.json' with { type: 'json' };
import { newCampaign } from '../src/core/campaign.js';
import { encode } from '../src/core/save.js';
import { IndexedDBStorageAdapter } from '../src/core/storage-adapter.js';

test('adapter CAS rejects a wrong identity and a stale replacement, and migration keeps both', async () => {
  const a = new IndexedDBStorageAdapter(null);
  await a.open();
  const s = newCampaign(contract, data, 1000);
  s.revision = 100;
  const head = await a.commit(null, encode(s, data), data);
  const t = structuredClone(s);
  t.revision = 101;
  await assert.rejects(() => a.commit({ ...head, checksum: 'wrong-checksum', campaignId: 'wrong-identity' }, encode(t, data), data));
  const liveHead = (await a.loadLive(data)).head;
  const replacement = structuredClone(s);
  replacement.revision = 200;
  await a.replace(liveHead, encode(replacement, data), data);
  const b = new IndexedDBStorageAdapter(null);
  b.memoryDb = a.memoryDb;
  const stale = structuredClone(s);
  stale.revision = 150;
  await assert.rejects(() => b.replace(liveHead, encode(stale, data), data));
  assert.equal((await a.loadLive(data)).state.revision, 200);
  const old = newCampaign(contract, data, 1000);
  old.revision = 1;
  const source = new Map([
    ['aod-reborn-v1', encode(old, data)],
    ['aod-reborn-v1-staged', 'preserve-staged-bytes'],
  ]);
  await a.migrateFromLocalStorage({ getItem: key => source.get(key) ?? null }, data);
  assert.equal((await a.loadLive(data)).state.revision, 200);
  const exported = await a.export();
  assert.equal(Object.values(exported.campaigns).includes('preserve-staged-bytes'), true);
  assert.equal(exported.metadata['migration-marker'].complete, true);

  a.memoryDb.campaigns.set('live', '{corrupted-live-json');
  const damaged = await a.loadLive(data);
  assert.equal(damaged.status, 'DAMAGED');
  assert.equal(damaged.raw, '{corrupted-live-json');
  assert.equal(damaged.backup?.revision, 100);
});

