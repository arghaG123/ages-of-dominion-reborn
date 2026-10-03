"""Planner read-only project audit; writes only into this QA directory."""
from pathlib import Path
import hashlib, json, collections, datetime
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
def read(p): return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]; batches=[]; issues=[]
for folder in sorted((ROOT/'assets/production').glob('production-*')):
    report=read(str((folder/'collection-report.json').relative_to(ROOT)))
    manifest=read(str((folder/'manifest.json').relative_to(ROOT)))
    requests={x['id']:x for x in manifest['items']}
    job=read(str((folder/'provider-job.json').relative_to(ROOT)))
    for o in report['outputs']:
        p=ROOT/o['file']; req=requests.get(o['id'],{})
        with Image.open(p) as im:
            im.load(); size=list(im.size); mode=im.mode
        match=sha(p)==o['sha256']
        prompt=hashlib.sha256(req.get('prompt','').encode()).hexdigest()
        promptMatch=prompt==o.get('promptSHA256')
        r={**o,'batch':folder.name,'hashMatch':match,'decodeSize':size,'mode':mode,'promptMatch':promptMatch}
        rows.append(r)
        if not match or not promptMatch: issues.append(r)
    batches.append({'id':folder.name,'outputs':len(report['outputs']),'requests':len(manifest['items']),'savedProviderState':job.get('state'),'collectedAt':report.get('collectedAt')})
allocation=read('docs/plan/HIGH-RESOLUTION-UPGRADE-COUNT-2026-10-03.json')['scenarios']['TERRAIN_BACKGROUNDS_ONLY']['items']
ids={r['id'] for r in rows}; required={x['id'] for x in allocation}
ledger=read('docs/plan/image-production/budget-ledger.json')
distIssues=[]; dist=ROOT/'dist'
for p in (ROOT/'src').rglob('*'):
    if p.is_file():
        dp=dist/p.relative_to(ROOT)
        if not dp.exists() or sha(dp)!=sha(p): distIssues.append(str(p.relative_to(ROOT)))
closure=read('qa/recovery-executor-20261003/dist-closure.json')
assetIssues=[]
for x in closure['assets']:
    p=dist/x['file']
    if not p.exists() or sha(p)!=x['sha256']: assetIssues.append(x['file'])
import sys
sys.path.insert(0,str(ROOT/'scripts'))
import review_gates
gates=review_gates.evaluate()
summary={'timeUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'originals':len(rows),'distinctIds':len(ids),'distinctHashes':len({r['sha256'] for r in rows}),'associationIssues':len(issues),'batches':batches,'baselineRequired':len(required),'baselinePresent':len(required&ids),'baselineMissing':sorted(required-ids),'nonBaselineIds':sorted(ids-required),'gearPresent':len({i for i in ids if i.startswith('gear-')}),'selectedResolutionIds':{res:[x['id'] for x in allocation if x['plannedResolution']==res] for res in ['4K','2K']},'distSourceIssues':distIssues,'distAssetIssues':assetIssues,'distAssetCount':len(closure['assets']),'budgetLedger':ledger,'gateSummary':{'rows':len(gates['rows']),'stale':len(gates['stale']),'selected':len(gates['selected']),'runtimeApproved':sum(bool(x['runtimeApproved']) for x in gates['rows']),'ownerAccepted':sum(bool(x['ownerAccepted']) for x in gates['rows']),'scene':gates['scene']},'sourceHashes':{str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'src').rglob('*') if p.is_file()},'limitations':['No provider calls or rebuild','Overview sheets do not approve mattes/rigs/registration','No native/device test']}
(OUT/'inventory.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
(OUT/'originals.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8')
for index in range(0,len(rows),90):
    group=rows[index:index+90]; sheet=Image.new('RGB',(1800,2200),'#263239'); draw=ImageDraw.Draw(sheet)
    for n,row in enumerate(group):
        x=(n%9)*200; y=(n//9)*220
        with Image.open(ROOT/row['file']) as im:
            im=im.convert('RGB'); im.thumbnail((194,187)); sheet.paste(im,(x+(194-im.width)//2,y))
        label=row['batch'].split('-')[1]+' '+row['id']
        draw.text((x+2,y+189),label[:28],fill='white'); draw.text((x+2,y+202),label[28:56],fill='white')
    sheet.save(OUT/f'source-overview-{index//90+1}.jpg',quality=92)
print(json.dumps({k:v for k,v in summary.items() if k not in ['budgetLedger','sourceHashes','selectedResolutionIds','batches']},indent=2))
