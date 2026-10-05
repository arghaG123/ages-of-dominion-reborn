from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
from PIL import Image
root = Path(__file__).resolve().parents[2]
run = root/'assets/high-res/interactive-4k-first32-20261003/run-01-20261003-172733'
journal = json.loads((run/'journal.json').read_text(encoding='utf-8'))
rows=[]
for row in journal['attempts']:
    if row.get('status') != 'SUCCEEDED': continue
    path=root/row['outputFile']
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    with Image.open(path) as im: size=list(im.size); im.verify()
    rows.append({'id':row['id'],'file':row['outputFile'],'sha256':digest,'matchesJournal':digest==row['sha256'],'dimensions':size,'technicalStatus':'PASS' if digest==row['sha256'] and size==[5504,3072] else 'FAIL','visualStatus':'UNVERIFIED','runtimeApproved':False})
result={'at':datetime.now(timezone.utc).isoformat(),'run':run.relative_to(root).as_posix(),'journalSummary':journal['summary'],'successfulOutputs':rows,'scope':'Local successful output dimensions/decode/hash only; provider/billing not queried; no image processing or adoption'}
(Path(__file__).parent/'highres-local-refresh.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'outputs':len(rows),'technicalFailures':[r['id'] for r in rows if r['technicalStatus']=='FAIL'],'journalSummary':journal['summary']}))
