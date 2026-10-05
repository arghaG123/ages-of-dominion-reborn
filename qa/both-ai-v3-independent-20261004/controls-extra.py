import sys, pathlib, json, hashlib, base64, socket, subprocess
from PIL import Image
sys.dont_write_bytecode=True
ROOT=pathlib.Path('C:/dev/ages-of-dominion-reborn')
OUT=ROOT/'qa/both-ai-v3-independent-20261004'
SB=OUT/'controls-sandbox'
sys.path.insert(0,str(SB))
import interactive_runner_continuity as m
def forbidden(*a,**kw):raise AssertionError('Network/credentials/subprocess/transport prohibited in independent sandbox')
m.get_gcloud_token=forbidden;m.urllib.request.urlopen=forbidden;m.subprocess.run=forbidden;socket.create_connection=forbidden
rows=[]
for mode in ['valid','missing-request-file','missing-response-hash','malformed-body-valid-hash','missing-prompt-in-body','wrong-config-image-size','wrong-model','wrong-endpoint','changed-source-image','wrong-output-dimensions','missing-output-hash']:
    pack=SB/('strong-'+mode);pack.mkdir(exist_ok=True)
    Image.new('RGB',(2048,2048),(90,120,80)).save(pack/'output.png')
    b=(pack/'output.png').read_bytes();h=hashlib.sha256(b).hexdigest()
    payload={'contents':[{'role':'user','parts':[{'text':'original prompt'},{'inlineData':{'mimeType':'image/png','data':base64.b64encode(b).decode()}}]}], 'generationConfig':{'candidateCount':1,'maxOutputTokens':2048,'responseModalities':['IMAGE'],'imageConfig':{'aspectRatio':'1:1','imageSize':'2K'}}}
    if mode=='missing-prompt-in-body':payload['contents'][0]['parts']=[{'inlineData':{'mimeType':'image/png','data':base64.b64encode(b).decode()}}]
    if mode=='wrong-config-image-size':payload['generationConfig']['imageConfig']['imageSize']='1K'
    if mode=='changed-source-image':payload['contents'][0]['parts'][1]['inlineData']['data']=base64.b64encode(b'changed_source_bytes').decode()
    body=b'not JSON' if mode=='malformed-body-valid-hash' else json.dumps(payload,sort_keys=True).encode()
    (pack/'request_body.json').write_bytes(body)
    resp={'candidates':[{'content':{'parts':[{'inlineData':{'mimeType':'image/png','data':base64.b64encode(b).decode()}}]}}]}
    rb=json.dumps(resp).encode();(pack/'response.json').write_bytes(rb)
    wa={'status':'SUCCEEDED','itemId':'test-id','sha256':h,'bodySHA256':hashlib.sha256(body).hexdigest(),'responseSHA256':hashlib.sha256(rb).hexdigest(),'model':m.MODEL,'endpoint':m.ENDPOINT}
    if mode=='missing-request-file':(pack/'request_body.json').unlink()
    if mode=='missing-response-hash':del wa['responseSHA256']
    if mode=='missing-output-hash':del wa['sha256']
    if mode=='wrong-model':wa['model']='wrong-model'
    if mode=='wrong-endpoint':wa['endpoint']='https://invalid.example.test/wrong'
    (pack/'write_ahead_request.json').write_text(json.dumps(wa))
    runner=m.ContinuityRunner(owner_base='independent-'+mode,mutex_file=pack/'mutex.json',pacing_file=pack/'pacing.json',budget_file=pack/'budget.json',local_lock_file=pack/'active.json',cloud_lock_enabled=False,transport=forbidden)
    meta={'id':'test-id','prompt':'original prompt','expectedDimensions':[1024,1024] if mode=='wrong-output-dimensions' else [2048,2048], 'imageSize':'2K','model':m.MODEL,'endpoint':m.ENDPOINT,'sources':[{'mimeType':'image/png','data':base64.b64encode(b).decode()}]}
    try:result=runner.execute_request(pack,meta)
    except Exception as e:result={'status':'EXCEPTION','error':str(e)}
    reused=result.get('status')=='REUSED_EXISTING_SUCCESS'
    rows.append({'probe':mode,'result':result,'pass':reused if mode=='valid' else not reused,'limitation':'Source/config/endpoint fields expose missing request identity validation; this is an offline synthetic contract probe.'})
(OUT/'stronger-reuse-results.json').write_text(json.dumps(rows,indent=2))
print(json.dumps({'pass':sum(r['pass'] for r in rows),'fail':sum(not r['pass'] for r in rows),'rows':[{k:r[k] for k in ['probe','pass']} for r in rows]},indent=2))
