import pathlib,json,hashlib,base64,collections
from PIL import Image
R=pathlib.Path('C:/dev/ages-of-dominion-reborn');O=R/'qa/both-ai-v3-independent-20261004'
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def dump(name,x):(O/name).write_text(json.dumps(x,indent=2)+'\n')
rows=[]
m=json.loads((R/'docs/plan/image-production/native4k-first32-delivery-manifest.json').read_text())
for it in m['items']:
    p=R/it['nativePath']
    with Image.open(p) as im:im.load();dims=list(im.size)
    rows.append({'id':it['canonicalID'],'path':it['nativePath'],'hashMatches':sha(p)==it['nativeSHA256'],'dimensions':dims,'dimensionsMatch':dims==it['dimensions']})
dump('native4k-32-checks.json',rows)
manifest=json.loads((R/'docs/plan/IMAGE-LATER73-EXECUTION-MANIFEST-2026-10-04.json').read_text());rows2=[]
for it in manifest['items']:
    p=R/('assets/high-res/final-native2k/'+it['id']+'.png');pack=R/it['localPackDir'];response=pack/'response.json'
    h=sha(p)
    with Image.open(p) as im:im.load();dims=list(im.size)
    row={'id':it['id'],'nativeHash':h,'dimensions':dims,'packOutputMatches':sha(pack/'output.png')==h,'rawResponseExists':response.exists(),'responseImageMatches':False}
    if response.exists():
        j=json.loads(response.read_text())
        parts=[part for c in j.get('candidates',[]) for part in c.get('content',{}).get('parts',[]) if 'inlineData' in part]
        row['responseImageMatches']=any(hashlib.sha256(base64.b64decode(part['inlineData']['data'])).hexdigest()==h for part in parts)
    rows2.append(row)
dump('native2k-73-response-checks.json',rows2)
v3=json.loads((R/'docs/plan/IMAGE-ROLE-DISPOSITIONS-V3-2026-10-04.json').read_text());bindings=[]
for row in v3['rows']:
    for k in ['source','derivative']:
        rec=row.get(k)
        if isinstance(rec,dict) and 'path' in rec and 'sha256' in rec:
            p=R/rec['path'];b={'id':row['id'],'kind':k,'path':rec['path'],'exists':p.exists()}
            if p.exists():
                b['hashMatches']=sha(p)==rec['sha256']
                with Image.open(p) as im:im.load();b['dimensionsMatch']=list(im.size)==rec['dimensions'];b['modeMatch']=im.mode==rec['mode']
            bindings.append(b)
dump('v3-role-bindings.json',bindings)
base=json.loads((R/'docs/plan/ACCOUNTING-CONSISTENCY-V3-2026-10-04.json').read_text());ledger=json.loads((R/'docs/plan/image-production/budget-ledger.json').read_text())
batchsum=sum(b.get('reconciledCommittedUSD',b.get('reconciledConservativeUSD',0)) or 0 for b in ledger['batches'])
account={'baseComponentSum':sum(v for k,v in base['baseComponentsBreakdownUSD'].items() if k!='sumBaseComponents'),'protectedLater73Sum':sum(base['later73UniqueAttemptReconciliationUSD'][k] for k in ['rawTokensEstimate73UniqueAttempts','ceilingBufferUSD','originalUnknownLiabilities'] if k!='originalUnknownLiabilities')+base['later73UniqueAttemptReconciliationUSD']['originalUnknownLiabilities']['totalRetainedUnknownLiabilitiesUSD'],'nestedBatchTotal':ledger['reconciliationTrail']['reconciledBatches01To17TotalUSD'],'invoiceStatus':base['invoicesStatus'],'total':base['totalProjectCommittedExposureUSD']['totalProtectedExposureUSD']}
dump('accounting-checks.json',account)
print(json.dumps({'native4K':len(rows),'native4KFailures':sum(not x['hashMatches'] or not x['dimensionsMatch'] for x in rows),'native2K':len(rows2),'native2KFailures':sum(not x['packOutputMatches'] or not x['responseImageMatches'] or x['dimensions']!=[2048,2048] for x in rows2),'roleBindings':len(bindings),'roleBindingFailures':sum(not x['exists'] or not x.get('hashMatches') or not x.get('dimensionsMatch') or not x.get('modeMatch') for x in bindings),'accounting':account},indent=2))
