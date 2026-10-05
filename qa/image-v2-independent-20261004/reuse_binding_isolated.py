import json,sys,hashlib,base64
from pathlib import Path
from PIL import Image
OUT=Path(__file__).parent/'controls-sandbox';sys.dont_write_bytecode=True;sys.path.insert(0,str(OUT))
import interactive_runner_continuity as m
def forbidden(*a,**k):raise AssertionError('Forbidden transport/credentials/subprocess')
m.get_gcloud_token=forbidden;m.urllib.request.urlopen=forbidden;m.subprocess.run=forbidden
rows=[]
for mode in ['valid-baseline','missing-body-hash','invented-body-hash','changed-prompt','wrong-mime']:
 p=OUT/('isolated-'+mode);p.mkdir();Image.new('RGB',(2048,2048),(90,120,80)).save(p/'output.png');b=(p/'output.png').read_bytes();h=hashlib.sha256(b).hexdigest()
 payload={'contents':[{'role':'user','parts':[{'text':'original prompt'}]}],'generationConfig':{'candidateCount':1,'maxOutputTokens':2048,'responseModalities':['IMAGE'],'imageConfig':{'aspectRatio':'1:1','imageSize':'2K'}}}
 body=json.dumps(payload,indent=2,sort_keys=True).encode();(p/'request_body.json').write_bytes(body)
 wa={'status':'SUCCEEDED','itemId':'test-id','sha256':h,'bodySHA256':hashlib.sha256(body).hexdigest()}
 if mode=='missing-body-hash':del wa['bodySHA256']
 if mode=='invented-body-hash':wa['bodySHA256']='a'*64
 resp={'candidates':[{'content':{'parts':[{'inlineData':{'mimeType':'image/jpeg' if mode=='wrong-mime' else 'image/png','data':base64.b64encode(b).decode()}}]}}]}
 respb=json.dumps(resp).encode();(p/'response.json').write_bytes(respb);wa['responseSHA256']=hashlib.sha256(respb).hexdigest();(p/'write_ahead_request.json').write_text(json.dumps(wa))
 r=m.ContinuityRunner(mutex_file=OUT/(mode+'-iso-mutex.json'),pacing_file=OUT/(mode+'-iso-pace.json'),budget_file=OUT/(mode+'-iso-budget.json'),local_lock_file=OUT/(mode+'-iso-lock.json'),transport=forbidden)
 result=r.execute_request(p,{'id':'test-id','prompt':'different prompt' if mode=='changed-prompt' else 'original prompt'})
 rows.append({'probe':mode,'result':result,'pass':(result['status']=='REUSED_EXISTING_SUCCESS')==(mode=='valid-baseline')})
(OUT/'isolated-reuse-binding-results.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
