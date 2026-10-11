import sys,json,collections,base64,hashlib,datetime
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
ROOT=Path('C:/dev/ages-of-dominion-reborn');QA=Path(__file__).resolve().parent
sys.path.insert(0,str(QA));from audit_common import sha,read,dump
receipts=[];guidefail=[]
for p in (ROOT/'qa/image-vertex-repair-20261009/environment/vertex-coordinator/receipts').rglob('*.json'):
    r=json.loads(p.read_text(encoding='utf-8-sig')); a=ROOT/'qa/image-vertex-repair-20261009/environment/vertex-coordinator/attempts'/r['attemptId']; body=a/'request_body.json'; errors=[]
    contractErrors=[]
    if 'rawResponsePath' not in r:
        contractErrors=['RECEIPT_SCHEMA_RAW_RESPONSE_PATH_MISSING','RECEIPT_SCHEMA_RAW_HASH_MISSING','RECEIPT_SCHEMA_PACK_HASH_MISSING','RECEIPT_SCHEMA_COMPLETE_MISSING']
        wal_recovery=json.loads((a/'write_ahead_request.json').read_text(encoding='utf-8'))
        r['rawResponsePath']=(a/'response.json').relative_to(ROOT).as_posix()
        r['rawResponseSHA256']=wal_recovery['responseSHA256']
        r['usage']=json.loads((a/'response.json').read_text(encoding='utf-8')).get('usageMetadata')
    raw=ROOT/r['rawResponsePath']
    if sha(body)!=r['wireBodySHA256']:errors.append('WIRE_HASH_MISMATCH')
    if sha(raw)!=r['rawResponseSHA256']:errors.append('RAW_HASH_MISMATCH')
    b=json.loads(body.read_text(encoding='utf-8')); response=json.loads(raw.read_text(encoding='utf-8')); images=[]
    for c in response.get('candidates',[]):
        for part in c.get('content',{}).get('parts',[]):
            v=part.get('inlineData') or part.get('inline_data')
            if v and v.get('data'):images.append(hashlib.sha256(base64.b64decode(v['data'])).hexdigest())
    for im in r['images']:
        if im['sha256'] not in images:errors.append('OUTPUT_NOT_RAW_RESPONSE_BYTES')
    parts=[x for c in b.get('contents',[]) for x in c.get('parts',[])]; imgparts=sum('inlineData' in x or 'fileData' in x for x in parts)
    if r['owner']=='ACTORS' and imgparts==0:guidefail.append(r['canonicalId'])
    wal=json.loads((a/'write_ahead_request.json').read_text(encoding='utf-8'))
    receipts.append({'id':r['canonicalId'],'owner':r['owner'],'attempt':r['attemptId'],'wireImageParts':imgparts,'images':r['images'],'errors':errors,'contractErrors':contractErrors,'rawImageHashes':images,'reservedUSD':r['reservedUSD'],'usage':r['usage'],'atUTC':wal.get('resumedAt',wal.get('recordedAt')),'httpCode':wal.get('httpCode'),'status':wal.get('status')})
budget=read('docs/plan/image-production/budget-ledger.json');new=budget['vertexRepair20261009'];reserve=sum(x['reservedUSD'] for x in new['attempts']);recsum=sum(r['reservedUSD'] for r in receipts)
old=read('docs/plan/image-production/reconciled-accounting-ledger.json')
dump('coordinator-checks.json',{'receipts':receipts,'receiptErrors':[r for r in receipts if r['errors']],'actorGuidesNotTransmitted':guidefail,'uniqueAttempts':len(set(x['attemptId'] for x in new['attempts'])),'sumReservationsUSD':round(reserve,4),'sumReceiptReservationsUSD':round(recsum,4),'currentExposureUSD':new['currentCommittedProtectedUSD'],'equationPass':round(new['previousCommittedProtectedUSD']+reserve,4)==new['currentCommittedProtectedUSD'],'headroomUSD':round(80-new['currentCommittedProtectedUSD'],4),'olderLedgerExposureUSD':old['totalReconciledExposureUSD'],'olderVsCurrentDifferenceUSD':round(new['currentCommittedProtectedUSD']-old['totalReconciledExposureUSD'],4),'untouchedReserveUSD':budget['safetyReserve']})
# Per-row transform diagnostics and separately classified point applicability.
geom=[];scope=[]
for owner,prefix in [('environment','ENVIRONMENT-ART'),('actors','ACTORS-EQUIPMENT')]:
    j=read(f'docs/plan/{prefix}-VERTEX-REPAIR-INTERFACE-2026-10-09.json')
    for row in j['rows']:
        recipe=None
        if row.get('recipePath') and (ROOT/row['recipePath']).is_file():recipe=read(row['recipePath'])
        roi=(recipe or {}).get('sourceRoi',(recipe or {}).get('roi'))
        if roi and row.get('sourceToOutput')==[1,0,0,1,0,0] and (roi[0]!=0 or roi[1]!=0):geom.append({'id':row['id'],'status':row['status'],'roi':roi,'actualCropTranslation':[-roi[0],-roi[1]],'declaredAffine':row['sourceToOutput']})
    scope.append({'owner':owner,'coverage':j.get('coverage'),'scenes':[{'id':s.get('id'),'status':s.get('status'),'gates':s.get('gates'),'keys':list(s)} for s in j.get('scenes',[])],'codeDependencies':j.get('codeDependencies'),'imageReview':j.get('imageReview')})
dump('transform-checks.json',geom);dump('scope-checks.json',scope)
# Slinger correction must preserve surviving source RGB and thin sling geometry. Native before/after diagnostics.
a=Image.open(ROOT/'assets/derivatives/image-vertex-repair-20261009/actors/troops/troop-stone-ranged.png').convert('RGBA');n=Image.open(ROOT/'assets/high-res/final-native2k/troop-stone-ranged.png').convert('RGBA') if (ROOT/'assets/high-res/final-native2k/troop-stone-ranged.png').is_file() else None
r=read('qa/image-vertex-repair-20261009/actors/recipes/troop-stone-ranged.json'); roi=r['sourceRoi']
if n:
    ac=np.asarray(a);nc=np.asarray(n.crop(roi));v=ac[:,:,3]>16;dump('slinger-checks.json',{'sourceSize':list(n.size),'cropSize':list(a.size),'rgbIdentityOnVisibleAlpha':bool(np.array_equal(ac[:,:,:3][v],nc[:,:,:3][v])),'visiblePixels':int(v.sum()),'sourceRoi':roi})
    canvas=Image.new('RGB',(1200,850),'#252a32');d=ImageDraw.Draw(canvas)
    for i,(label,im) in enumerate([('Native crop',n.crop(roi)),('Current derivative on green',a)]):
        im.thumbnail((500,800));bg=Image.new('RGBA',im.size,'#587066');bg.alpha_composite(im);canvas.paste(bg.convert('RGB'),(50+i*600,40));d.text((50+i*600,10),label,fill='white')
    canvas.save(QA/'slinger-native-versus-result.jpg',quality=95)
print(json.dumps({'receipts':len(receipts),'rawBindingFailures':len([r for r in receipts if r['errors']]),'missingActorGuideParts':guidefail,'reservationSum':round(reserve,4),'metadataCropAffines':len(geom),'scope':scope},indent=2)[:6500])
