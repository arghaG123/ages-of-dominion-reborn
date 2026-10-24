import test from 'node:test';
import assert from 'node:assert/strict';
import data from '../src/data/reference-data.json' with {type:'json'};
import contract from '../src/data/implementation-contract.json' with {type:'json'};
import {newCampaign,command} from '../src/core/campaign.js';

test('local preferences remain usable in active sessions without spending or resolving combat',()=>{
  for(const type of ['START_SKIRMISH','START_SIEGE']){
    const fresh=newCampaign(contract,data,1000);
    const active=command(fresh,{id:'start',type,payload:{}},1000,data);
    const changed=command(active,{id:'sound',type:'SETTINGS',payload:{music:0,sfx:0.4,reducedMotion:true}},1000,data);
    assert.equal(changed.settings.music,0);
    assert.deepEqual(changed.resources,active.resources);
    assert.deepEqual(changed.battle,active.battle);
    assert.deepEqual(changed.defense,active.defense);
    assert.throws(()=>command(active,{id:'buy',type:'BUILD',payload:{plotId:'P01',building:'lumber'}},1000,data),/pending/);
  }
});
