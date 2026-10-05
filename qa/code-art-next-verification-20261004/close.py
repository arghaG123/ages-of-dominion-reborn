"""Read-only closure and binding verification; writes this audit directory only."""
from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
ROOT=Path('C:/dev/ages-of-dominion-reborn'); QA=ROOT/'qa/code-art-next-verification-20261004'
def sha(p):
    with p.open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(n,x): (QA/n).write_text(json.dumps(x,indent=2),encoding='utf-8')
old=read(ROOT/'qa/code-art-followup-20261004/protected-closing.json')['rows']
delivery=[]
for row in old:
    if row['file'].startswith('assets/delivery/'):
        p=ROOT/row['file']; current=sha(p) if p.is_file() else None
        delivery.append({'file':row['file'],'priorSHA256':row['closingSHA256'],'currentSHA256':current,'unchanged':current==row['closingSHA256']})
selection=read(ROOT/'src/data/reviewed-source-selection.json'); bindings=[]
for identity,row in selection['delivery'].items():
    for key,hkey in [('file','sha256'),('uiFile','uiSHA256')]:
        if key in row:
            p=ROOT/row[key]; bindings.append({'id':identity,'role':key,'file':row[key],'hashMatch':p.is_file() and sha(p)==row.get(hkey)})
for identity,row in selection['kingdomTerrain'].items():
    p=ROOT/row['sourceFile']; bindings.append({'id':'kingdom-'+identity,'role':'terrain','file':row['sourceFile'],'hashMatch':p.is_file() and sha(p)==row['sourceSHA256'],'runtimeApproved':row['runtimeApproved']})
write('art-bindings.json',{'at':datetime.now(timezone.utc).isoformat(),'deliveryRows':len(delivery),'unchangedDeliveryRows':sum(r['unchanged'] for r in delivery),'delivery':delivery,'bindings':bindings,'scope':'Exact SHA binding only. No visual/runtime/owner promotion.'})
start=read(QA/'protected-start.json'); closing=[]
for row in start['files']:
    p=ROOT/row['file']; current=sha(p) if p.is_file() else None
    closing.append({'file':row['file'],'startSHA256':row['sha256'],'closingSHA256':current,'unchanged':current==row['sha256']})
write('protected-closing.json',{'at':datetime.now(timezone.utc).isoformat(),'rows':closing,'unchanged':sum(r['unchanged'] for r in closing),'total':len(closing),'changed':[r for r in closing if not r['unchanged']]})
browser=read(QA/'browser.json'); print('Browser keys:',list(browser))
print(json.dumps({'protected':len(closing),'unchanged':sum(r['unchanged'] for r in closing),'changes':[r['file'] for r in closing if not r['unchanged']],'deliveryRows':len(delivery),'deliveryUnchanged':sum(r['unchanged'] for r in delivery),'bindingFailures':[r for r in bindings if not r['hashMatch']],'browserErrors':browser['errors'],'screenshotBytes':sum(p.stat().st_size for p in QA.glob('*.png'))},indent=2))
for key,value in browser.items():
    if key not in ('rows','errors'): print(key, str(value)[:500])
