import json,datetime,re,collections
from pathlib import Path
QA=Path(__file__).resolve().parent;ROOT=QA.parent.parent
p=QA/'independent-per-id-status.json';rows=json.loads(p.read_text(encoding='utf-8'))
for r in rows:
    if r['producerStatus']=='FAIL':
        r['independentResult']='FAIL'
        r['reasons'].append('Existing failed link/part gate preserved; no new passing source/rig evidence')
p.write_text(json.dumps(rows,indent=2),encoding='utf-8')
bad=[]
for name in ['IMAGE-COMPLETION-INDEPENDENT-AUDIT-2026-10-09.md']:
    p=ROOT/'docs/plan'/name
    for link in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
        if '://' not in link and not (p.parent/re.sub(r':\d+$','',link.split('#')[0])).resolve().exists():bad.append(link)
v=json.loads((QA/'publication-checks.json').read_text(encoding='utf-8'));v.update(atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),finalReportLinksMissing=bad,independentCounts=dict(collections.Counter(r['independentResult'] for r in rows)),existingFailedRowsPreserved=all(r['independentResult']=='FAIL' for r in rows if r['producerStatus']=='FAIL'))
(QA/'publication-checks.json').write_text(json.dumps(v,indent=2),encoding='utf-8')
print(json.dumps(v,indent=2))
