from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
R=Path('C:/dev/ages-of-dominion-reborn');Q=R/'qa/code-art-finish-audit-20261004'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
start=json.loads((Q/'protected-start.json').read_text());rows=[]
for x in start['files']:
 p=R/x['file'];h=sha(p) if p.exists() else None;rows.append({'file':x['file'],'startSHA256':x['sha256'],'closingSHA256':h,'unchanged':h==x['sha256']})
originals=[]
for p in sorted((R/'assets/production').glob('production-*/collection-report.json')):
 for v in json.loads(p.read_text())['outputs']:
  f=R/v['file'];originals.append({'id':v['id'],'file':v['file'],'hashMatch':f.exists() and sha(f)==v['sha256']})
out={'at':datetime.now(timezone.utc).isoformat(),'rows':rows,'unchanged':sum(x['unchanged'] for x in rows),'total':len(rows),'changed':[x for x in rows if not x['unchanged']],'originalsCount':len(originals),'originalDistinctIDs':len({x['id'] for x in originals}),'originalHashMatches':sum(x['hashMatch'] for x in originals),'scope':'Source/art/package/control snapshot; concurrent image mutations named, planner QA/doc writes excluded'}
(Q/'protected-closing.json').write_text(json.dumps(out,indent=2));(Q/'originals.json').write_text(json.dumps(originals,indent=2));print(json.dumps({k:v for k,v in out.items() if k!='rows'},indent=2))
