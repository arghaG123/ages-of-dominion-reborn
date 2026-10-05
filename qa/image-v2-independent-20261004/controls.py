import json, sys, base64, hashlib
from pathlib import Path
from PIL import Image
ROOT=Path('C:/dev/ages-of-dominion-reborn'); OUT=Path(__file__).parent/'controls-sandbox'; OUT.mkdir()
sys.dont_write_bytecode=True
src=(ROOT/'scripts/interactive_runner_continuity.py').read_text()
src=src.replace('ROOT = Path("c:/dev/ages-of-dominion-reborn")',f'ROOT = Path({str(OUT)!r})')
(OUT/'interactive_runner_continuity.py').write_text(src)
test=(ROOT/'qa/offline-controls-repair-20261004/test_repaired_controls.py').read_text()
test=test.replace("sys.path.insert(0, str(ROOT / 'scripts'))",'sys.path.insert(0, str(SANDBOX))')
(OUT/'rerun-producer.py').write_text(test)
exec(compile(test,str(OUT/'rerun-producer.py'),'exec'),{'__file__':str(OUT/'rerun-producer.py'),'__name__':'__main__'})
import interactive_runner_continuity as m
def forbidden(*a,**k): raise AssertionError('No network, credentials or subprocess permitted')
m.get_gcloud_token=forbidden;m.urllib.request.urlopen=forbidden;m.subprocess.run=forbidden
results=[]
for mode in ['missing-body-hash','invented-body-hash','changed-prompt','wrong-mime']:
 p=OUT/mode;p.mkdir();Image.new('RGB',(2048,2048),(90,120,80)).save(p/'output.png')
 b=(p/'output.png').read_bytes();h=hashlib.sha256(b).hexdigest()
 wa={'status':'SUCCEEDED','itemId':'test-id','sha256':h}
 if mode!='missing-body-hash':wa['bodySHA256']='a'*64
 (p/'write_ahead_request.json').write_text(json.dumps(wa))
 (p/'request_body.json').write_text('{"contents":[{"parts":[{"text":"old prompt"}]}]}')
 resp={'candidates':[{'content':{'parts':[{'inlineData':{'mimeType':'image/jpeg' if mode=='wrong-mime' else 'image/png','data':base64.b64encode(b).decode()}}]}}]}
 (p/'response.json').write_text(json.dumps(resp))
 r=m.ContinuityRunner(mutex_file=OUT/(mode+'-mutex.json'),pacing_file=OUT/(mode+'-pace.json'),budget_file=OUT/(mode+'-budget.json'),local_lock_file=OUT/(mode+'-lock.json'),transport=forbidden)
 result=r.execute_request(p,{'id':'test-id','prompt':'different new prompt'})
 results.append({'probe':mode,'result':result,'pass':result.get('status')!='REUSED_EXISTING_SUCCESS'})
(OUT/'independent-additional-probes.json').write_text(json.dumps(results,indent=2))
print('ADDITIONAL PROBES',json.dumps(results,indent=2))
