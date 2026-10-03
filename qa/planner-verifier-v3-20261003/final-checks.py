"""Read-only final preservation/link checks, written to this audit directory."""
from pathlib import Path
import hashlib,json,re,datetime
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
def sha(b): return hashlib.sha256(b).hexdigest()
snapshot=json.loads((OUT/'protected-input-snapshot.json').read_text(encoding='utf-8-sig'))
rows=[]
for r in snapshot:
    p=ROOT/r['file'];actual=sha(p.read_bytes()) if p.is_file() else None
    rows.append({'file':r['file'],'expectedSHA256':r['sha256'],'actualSHA256':actual,'unchanged':actual==r['sha256']})
changes=[r for r in rows if not r['unchanged']]
protected=[r for r in rows if r['file'].startswith(('src/','tests/','dist/','assets/delivery/'))]
protected_initial={r['file'] for r in protected}
protected_current={str(p.relative_to(ROOT)).replace('\\','/') for folder in ['src','tests','dist','assets/delivery'] for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts}
history=[]
for r in json.loads((OUT/'planning-updates.json').read_text(encoding='utf-8-sig')):
    if 'historicalSuffixPreserved' in r:
        b=(ROOT/r['file']).read_bytes();suffix=b.split(b'\n\n',1)[1]
        history.append({'file':r['file'],'originalHistoricalSHA256':r['beforeSHA256'],'currentHistoricalSHA256':sha(suffix),'preserved':sha(suffix)==r['beforeSHA256']})
documents=['docs/plan/RECOVERY-V3-PLANNER-AUDIT-2026-10-03.md','docs/plan/SOURCE-EQUATIONS-ADDENDUM-2026-10-03.md','docs/plan/CODING-RECOVERY-AI-V3-NEXT-PROMPT-2026-10-03.txt','docs/plan/BATCH-GAP-OWNER-HANDOFF-V3-2026-10-03.txt']+[r['file'] for r in history]
links=[]
for f in documents:
    p=ROOT/f
    for target in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8-sig')):
        if '://' in target or target.startswith('#'):continue
        link=(p.parent/target.split('#')[0]).resolve()
        links.append({'document':f,'target':target,'exists':link.exists()})
ledger=json.loads((ROOT/'docs/plan/DATA-ADOPTION-LEDGER.json').read_text(encoding='utf-8-sig'))
adopt=[r for v in ledger.values() if isinstance(v,list) for r in v if isinstance(r,dict) and r.get('planningHistory')]
refresh=json.loads((OUT/'incremental-collection-refresh.json').read_text(encoding='utf-8-sig'))
result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Planner documents and isolated QA only; no provider calls/builds/device tests',
        'initialSnapshotFiles':len(rows),'protectedSourceDeliveryTestsDistFiles':len(protected),'protectedChanges':[r for r in protected if not r['unchanged']],
        'protectedAddedFiles':sorted(protected_current-protected_initial),'protectedRemovedFiles':sorted(protected_initial-protected_current),
        'otherPreexistingFileChanges':changes,'historicalSuffixChecks':history,'localLinkChecks':links,
        'planningHistoryRows':len(adopt),'correctedRowsRemainUnimplemented':all(r.get('implemented') is False for r in adopt),
        'finalCollectionSnapshotFile':'incremental-collection-refresh.json','consumerRows':refresh['consumerRows'],'collectionOnlyUnverified':refresh['collectionOnly'],
        'documentSHA256':{f:sha((ROOT/f).read_bytes()) for f in documents}}
(OUT/'final-report-checks.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'protectedFiles':len(protected),'protectedChanges':len(result['protectedChanges']),'otherChanges':len(changes),'historicalSuffixesPreserved':all(r['preserved'] for r in history),'localLinks':len(links),'brokenLocalLinks':[r for r in links if not r['exists']],'ledgerHistoryRows':len(adopt),'runtimeImplementationNotClaimed':result['correctedRowsRemainUnimplemented'],'consumerRows':refresh['consumerRows']}))
