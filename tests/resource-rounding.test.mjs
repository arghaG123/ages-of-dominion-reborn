import test from 'node:test';
import assert from 'node:assert/strict';
import {resourceAmountText} from '../src/client/resource-bar.js';
test('compact balances never round up across unit boundaries or change exact balance',()=>{
  for(const [amount,text] of [[0,'0'],[9999.9,'9999'],[99999,'99.9K'],[999999,'999K'],[999999999,'999M'],[1e12,'1T']]){
    const result=resourceAmountText(amount);
    assert.equal(result.text,text);
    assert.equal(result.full,String(Math.floor(amount)));
  }
});
