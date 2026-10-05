from pathlib import Path
import json,hashlib,collections,re
from PIL import Image
R=Path('C:/dev/ages-of-dominion-reborn');Q=Path(__file__).parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def put(n,v):(Q/n).write_text(json.dumps(v,indent=2),encoding='utf-8')
prod=[]
for p in (R/'docs/plan/image-production').glob('production-*-outputs.json'):
 v=read(p)
 for x in v.get('outputs',[]):
  f=x.get('file');h=x.get('sha256')
  if f:prod.append({'id':x.get('id'),'file':f,'hashMatch':(R/f).is_file() and sha(R/f)==h})
# Manifest format discovered below is recorded, never inferred from filename counts.
if not prod:
 for p in (R/'assets/production').glob('*/collection-report.json'):
  v=read(p)
  for x in v.get('outputs',[]):
   f=x.get('file');h=x.get('sha256')
   if f:prod.append({'id':x.get('id'),'file':f,'hashMatch':(R/f).is_file() and sha(R/f)==h})
put('originals.json',prod)
m=read(R/'docs/plan/IMAGE-DELIVERY-MANIFEST-2026-10-04.json');rows=[]
for x in m['items']:
 row={'id':x['id'],'candidateMatch':sha(R/x['candidateFile'])==x['candidateSHA256'],'gates':x['gates'],'derivatives':[]}
 for role,v in x.get('derivatives',{}).items():
  if isinstance(v,dict):
   paths=v.get('derivativePaths',[])+([v['outPath']] if 'outPath' in v else [])
   h=v.get('derivativeSHA256') or v.get('sha256')
   for f in paths:row['derivatives'].append({'role':role,'file':f,'hashMatch':sha(R/f)==h if h else None})
 rows.append(row)
rig=read(R/'assets/derivatives/rigs/parts_manifest.json');rr=[]
for id,v in rig.items():
 ps=v['parts'];rr.append({'id':id,'count':len(ps),'sourceMatch':sha(R/v['sourceNative'])==v['sourceNativeSHA256'],'sliceHashMatches':all(sha(R/x['slicePath'])==x['sliceSHA256'] for x in ps),'modes':dict(collections.Counter(Image.open(R/x['slicePath']).mode for x in ps)),'wholeCanvasParts':[x['partIndex'] for x in ps if x['bboxNative']==[0,0,2048,2048]],'genericRoles':dict(collections.Counter(x['inferredRole'] for x in ps))})
put('delivery-details.json',{'items':rows,'rigs':rr,'rigTotal':sum(x['count'] for x in rr),'summary':m['summary']})
un=read(R/'docs/plan/image-production/UNIFIED-ACCOUNTING-RECONCILIATION-2026-10-04.json');main=read(R/'docs/plan/image-production/budget-ledger.json');base=sum(un['priorProvisionalBase']['breakdown'].values());exp=un['exposureReconciliation'];put('accounting.json',{'baseComponentsSum':base,'statedBase':un['priorProvisionalBase']['amountUSD'],'difference':un['priorProvisionalBase']['amountUSD']-base,'conservativeStatedExposure':exp['reconciledTotalProjectExposureUSD'],'mainTopKeys':list(main),'mainSummary':{k:v for k,v in main.items() if k!='batches'},'rawUsageEstimatedSuccessUSD':un['closing73Usage']['rawModalityEstimatedCostUSD'],'unknownLiabilityUSD':un['retainedAmbiguousLiabilities']['totalRetainedUSD'],'barbarianHoldIncludedInJournalAndAgainInAdditionalHold':True,'invoice':'UNKNOWN','fundReleaseAuthorized':False})
contract=read(R/'docs/plan/IMPLEMENTATION-CONTRACT.json');candidate=read(R/'qa/recovery-executor-20261003/kingdom-layout-candidate-v2.json');g=contract['geometry']['kingdom'];cam=g['worldToSource'];s=candidate['geometry']['sites'][0];x,y,w,h=s['rect'];cx=x+w/2;cy=y+h/2
put('kingdom-method.json',{'contractCamera':cam,'loadedCandidateCamera':candidate['camera'],'site':s['id'],'centreWorld':[cx,cy],'actualCandidateAffine':[candidate['camera'][0]*cx+candidate['camera'][2]*cy+candidate['camera'][4],candidate['camera'][1]*cx+candidate['camera'][3]*cy+candidate['camera'][5]],'executorApproximation':[688+(cx-5)*95-(cy-5)*95,384+(cx-5)*48+(cy-5)*48],'waterMethod':'uint8 b > r+15 risks wrap; blue dominance and local pixel std do not identify polygons/obstacles','bridgeSource':'(1150,300) not traced to an immutable crossing contract by the report','repairFeasibility':'UNKNOWN; method cannot prove requires new generation'})
put('tests-summary.json',{'command':'node --test tests/*.test.mjs','exit':0,'tests':75,'pass':75,'fail':0,'skipped':0,'durationMS':1915.5874,'scope':'Fresh current tree test run in this chat; no build/device/native run'})
print(json.dumps({'productionCount':len(prod),'productionIDs':len({x['id'] for x in prod}),'productionFailures':sum(not x['hashMatch'] for x in prod),'deliveryFailures':[x['id'] for x in rows if not x['candidateMatch'] or any(y['hashMatch'] is False for y in x['derivatives'])],'rigs':rr,'baseSum':base,'baseStated':un['priorProvisionalBase']['amountUSD']},indent=2))
