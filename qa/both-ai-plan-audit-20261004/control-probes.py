"""No network, no live controls. Deliberate adverse schedules and corrupt reuse."""
import sys,os,json,threading,concurrent.futures,time,io,urllib.request,subprocess
from pathlib import Path
from PIL import Image
R=Path('C:/dev/ages-of-dominion-reborn');Q=Path(__file__).parent
sys.dont_write_bytecode=True;sys.path.insert(0,str(R/'scripts'))
import interactive_runner_continuity as m
def forbidden(*a,**k):raise AssertionError('Network and credentials forbidden')
m.get_gcloud_token=forbidden;m.urllib.request.urlopen=forbidden;m.subprocess.run=forbidden
def runner(name):return m.ContinuityRunner(mutex_file=Q/(name+'-mutex.json'),pacing_file=Q/(name+'-pacing.json'),budget_file=Q/(name+'-budget.json'),local_lock_file=Q/(name+'-active.json'),cloud_lock_enabled=False,transport=forbidden)
rows=[]
# Both pass original read/check; delay second replacement until first already returned acquired.
barrier=threading.Barrier(2);first_done=threading.Event();orig=m.os.replace
def delayed(a,b):
 if str(b).endswith('delayed-race-mutex.json'):
  barrier.wait(timeout=5)
  if threading.current_thread().name.endswith('_1'):first_done.wait(timeout=5)
 return orig(a,b)
m.os.replace=delayed
rs=[runner('delayed-race'),runner('delayed-race')]
def acquire(pair):
 i,r=pair
 try:v={'contender':i,'acquired':r.acquire_mutex()}
 except Exception as e:v={'contender':i,'acquired':False,'error':str(e)}
 if i==0:first_done.set()
 return v
with concurrent.futures.ThreadPoolExecutor(2) as pool:contenders=list(pool.map(acquire,enumerate(rs)))
m.os.replace=orig
rows.append({'probe':'delayed contender after first verification','contenders':contenders,'exclusive':sum(x['acquired'] for x in contenders)==1})
r=runner('dead-unknown');r.mutex_file.write_text(json.dumps({'active':True,'owner':'dead','pid':2147483647,'lastState':'UNKNOWN'}))
try:v=r.acquire_mutex()
except Exception:v=False
rows.append({'probe':'dead PID UNKNOWN','blocked':not v})
r=runner('unknown-release');r.acquire_mutex();p=Q/'unknown-release-pack';p.mkdir(exist_ok=True);(p/'write_ahead_request.json').write_text(json.dumps({'status':'UNKNOWN','owner':'old','liabilityUSD':.143612}))
res=r.execute_request(p,{'id':'offline-unknown'});v=r.release_mutex('COMPLETED_CYCLE');rows.append({'probe':'UNKNOWN release denied','result':res,'blocked':not v})
# A previously successful file + arbitrary JSON response is accepted even when WA binding is wrong.
r=runner('reuse');p=Q/'reuse-pack';p.mkdir(exist_ok=True);Image.new('RGB',(2048,2048),'red').save(p/'output.png');(p/'response.json').write_text('{}');(p/'write_ahead_request.json').write_text(json.dumps({'status':'SUCCEEDED','sha256':'wrong','bodySHA256':'wrong'}))
res=r.execute_request(p,{'id':'offline-corrupt-reuse'});rows.append({'probe':'reuse response/body/output binding','result':res,'rejectsUnboundOutput':res.get('status')!='REUSED_EXISTING_SUCCESS'})
# Attempt numbering restarts at 1 and replaces the same supposedly append-only path.
r=runner('history');p=Q/'history-pack';p.mkdir(exist_ok=True);r.write_ahead_persisted_request(p,'offline-id',{'a':1},.1,1);before=(p/'write_ahead_subattempt_1.json').read_bytes();r.write_ahead_persisted_request(p,'offline-id',{'a':2},.1,1)
rows.append({'probe':'subattempt append-only collision','priorBytesPreserved':(p/'write_ahead_subattempt_1.json').read_bytes()==before})
(Q/'control-probes.json').write_text(json.dumps({'scope':'NEW QA paths only; all HTTP/token subprocesses forbidden; cloud disabled','rows':rows},indent=2));print(json.dumps(rows,indent=2))
