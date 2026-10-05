"""Offline controls probes. No provider transport, token calls, or live control writes."""
import os,sys,json,threading,concurrent.futures,hashlib,collections
from pathlib import Path
R=Path('C:/dev/ages-of-dominion-reborn');Q=R/'qa/later71-independent-audit-20261004'
sys.dont_write_bytecode=True;sys.path.insert(0,str(R/'scripts'))
import interactive_runner_continuity as mod
results=[]
# Force both contenders to reach replacement after their read/check. All paths are new QA files.
barrier=threading.Barrier(2);original=mod.os.replace
def gated(a,b):
 if str(b).endswith('race-mutex.json'):barrier.wait(timeout=5)
 return original(a,b)
mod.os.replace=gated
runners=[mod.ContinuityRunner(mutex_file=Q/'race-mutex.json',pacing_file=Q/f'race-pacing-{i}.json',cloud_lock_enabled=False) for i in range(2)]
def attempt(r):
 try:return {'owner':r.owner_id,'acquired':r.acquire_mutex()}
 except Exception as e:return {'owner':r.owner_id,'error':str(e)}
with concurrent.futures.ThreadPoolExecutor(2) as pool:acquired=list(pool.map(attempt,runners))
mod.os.replace=original
results.append({'probe':'simultaneous-check-before-replace','contenders':acquired,'exclusive':sum(bool(x.get('acquired')) for x in acquired)==1})
dead=Q/'dead-unknown-mutex.json';dead.write_text(json.dumps({'active':True,'owner':'offline-crashed-owner','pid':2147483647,'lastState':'UNKNOWN'}))
r=mod.ContinuityRunner(mutex_file=dead,pacing_file=Q/'dead-pacing.json',cloud_lock_enabled=False)
try:deadAcquire=r.acquire_mutex()
except Exception:deadAcquire=False
results.append({'probe':'dead-PID-with-unresolved-UNKNOWN','acquired':deadAcquire,'blocked':not deadAcquire})
pack=Q/'unknown-pack';pack.mkdir(exist_ok=True);(pack/'write_ahead_request.json').write_text(json.dumps({'status':'UNKNOWN','owner':'possibly-sent','itemId':'offline-id','liabilityUSD':.143612}))
def forbidden(*a,**k):raise AssertionError('No transport is permitted in this probe')
r=mod.ContinuityRunner(mutex_file=Q/'unknown-skip-mutex.json',pacing_file=Q/'unknown-skip-pacing.json',cloud_lock_enabled=False,transport=forbidden);r.acquire_mutex()
res=r.execute_request(pack,{'id':'offline-id'});released=r.release_mutex('COMPLETED_CYCLE')
results.append({'probe':'unresolved-item-does-not-enforce-run-exclusion','executeResult':res,'normalReleaseSucceeded':released,'safe':not released})
usage=json.loads((Q/'usage.json').read_text());tot=collections.Counter()
for v in usage:
 u=v['usage'];tot['input']+=u.get('promptTokenCount',0);tot['thinking']+=u.get('thoughtsTokenCount',0)
 for x in u.get('candidatesTokensDetails',[]):tot[x['modality']]+=x['tokenCount']
cost=tot['input']*.5/1e6+tot['IMAGE']*60/1e6+(tot['TEXT']+tot['thinking'])*3/1e6
accounting={'ratesUSDPerMillion':{'input':.5,'image':60,'textThinking':3},'usageTokens':dict(tot),'rawModalityEstimatedCostUSD':cost,'sumJournalUniqueSuccessfulUSD':sum(v['journalCost'] for v in usage),'journalTotalUSD':json.loads((R/'docs/plan/image-production/interactive-2k-later73-journal.json').read_text())['summary']['totalCostUSD'],'retainedUnknownLiabilities':2*.143612,'priorExposureProvisional':62.8496,'arithmeticExposureBeforeUncoveredLiabilitiesUSD':62.8496+cost+2*.143612,'invoices':'UNKNOWN','releaseOfFundsAuthorized':False,'rateSource':'https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing'}
(Q/'controls.json').write_text(json.dumps({'scope':'Only fresh QA files; cloud disabled; no transport or live mutex/ledger changes','probes':results,'accounting':accounting},indent=2));print(json.dumps({'probes':results,'accounting':accounting},indent=2))
