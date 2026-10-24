import test from 'node:test';
import assert from 'node:assert/strict';
import data from '../src/data/reference-data.json' with {type:'json'};
import contract from '../src/data/implementation-contract.json' with {type:'json'};
import {newCampaign} from '../src/core/campaign.js';
import {encode} from '../src/core/save.js';
import {IndexedDBStorageAdapter} from '../src/core/storage-adapter.js';
import {SaveQueue} from '../src/core/save-queue.js';

test('queued autosave cannot overwrite a replacement with the same identity and lower revision', async()=>{
  const adapter=new IndexedDBStorageAdapter(null), q=new SaveQueue(adapter,data);
  const s=newCampaign(contract,data,1000); s.revision=200;
  const queued=q.write(encode(s,data),'kingdom');
  s.revision=1;
  const replaced=q.write(encode(s,data),'hero',true);
  assert.equal(q.status.kind,'pending');
  assert.equal(await queued,false);
  assert.equal(await replaced,true);
  assert.equal((await adapter.loadLive(data)).state.revision,1);
  assert.equal(q.status.kind,'committed');
});
test('failure preserves backup, unsaved candidate, and failed acknowledgement',async()=>{
  const adapter=new IndexedDBStorageAdapter(null);
  const s=newCampaign(contract,data,1000);
  const h=await adapter.commit(null,encode(s,data),data);
  const q=new SaveQueue(adapter,data,h);
  s.revision=2; await adapter.commit(h,encode(s,data),data);
  s.revision=3; const raw=encode(s,data);
  await assert.rejects(q.write(raw,'kingdom'),/CAS head mismatch/);
  assert.equal(q.status.kind,'failed');
  assert.equal((await adapter.loadLive(data)).state.revision,2);
  assert.equal(JSON.parse(JSON.parse(raw).payload).revision,3);
});
test('damaged live restores valid backup with a new epoch and retains damaged bytes',async()=>{
  const adapter=new IndexedDBStorageAdapter(null), s=newCampaign(contract,data,1000);
  const h=await adapter.commit(null,encode(s,data),data);
  s.revision=1; await adapter.commit(h,encode(s,data),data);
  adapter.memoryDb.campaigns.set('live','damaged-original');
  const restored=await adapter.restoreBackup(data);
  assert.equal(restored.revision,0);
  assert.equal((await adapter.loadLive(data)).status,'VALID');
  assert.ok(Object.values((await adapter.export()).campaigns).includes('damaged-original'));
});
test('coalescing waits for the newest durable snapshot and never acknowledges an older completion as newest',async()=>{
  let release, calls=0;
  const waiting=new Promise(resolve=>{release=resolve;});
  const adapter={async commit(_head,raw){calls++;await waiting;return {revision:Number(raw)};}};
  const queue=new SaveQueue(adapter,{});
  const one=queue.write('1','kingdom');
  const two=queue.write('2','kingdom');
  const three=queue.write('3','kingdom');
  await Promise.resolve();
  assert.equal(calls,1);
  assert.equal(queue.status.kind,'pending');
  release();
  assert.deepEqual(await Promise.all([one,two,three]),[true,true,true]);
  assert.equal(queue.status.head.revision,3);
});
