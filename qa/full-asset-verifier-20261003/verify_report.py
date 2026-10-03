"""Verify this planner report's bindings and preservation; no production/runtime work."""
from pathlib import Path
import hashlib,json,collections
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda:f.read(4*1024*1024),b''):h.update(block)
    return h.hexdigest()
protected=read(OUT/'protected-input-snapshot.json')['files']
changed=[x['file'] for x in protected if not (ROOT/x['file']).is_file() or sha(ROOT/x['file'])!=x['sha256']]
history=read(OUT/'planning-history-preservation.json')
historybad=[x['file'] for x in history if hashlib.sha256((ROOT/x['file']).read_bytes()[x['prefixBytes']:]).hexdigest()!=x['priorSHA256']]
s=read(OUT/'all-source-review.json');d=read(OUT/'current-delivery-review.json');a=read(OUT/'associations.json');i=read(OUT/'inventory.json')
checks={
 'protectedInputsUnchanged':not changed,
 'priorPlanningBytesPreserved':not historybad,
 'all240OverviewRowsPresent':len(s['rows'])==240 and all(x['overviewReviewed'] for x in s['rows']),
 'eachBatchExactly30':set(collections.Counter(x['batch'] for x in s['rows']).values())=={30},
 'all240TechnicalPass':all(x['technical']=='PASS' for x in s['rows']),
 'all240RawRequestPayloadAssociations':a['count']==240 and a['allPass'],
 'delivery55RasterInventory':len(i['deliveryFiles'])==55,
 'current11SourceOutputBindings':len(d['assets'])==11 and all(x['sourceHashMatch'] and x['derivativeHashMatch'] and sha(ROOT/x['derivative'])==x['derivativeSHA256'] for x in d['assets']),
 'fourScopedArtworkPassOnly':sum(x['intendedUseArtwork']=='PASS' for x in d['assets'])==4,
 'noRuntimeOwnerPromotion':all(x['runtime']==x['ownerAcceptance']=='UNVERIFIED' for x in d['assets']),
 'sceneHashBinding':d['scene']['hashMatch'] and sha(ROOT/d['scene']['file'])==d['scene']['sha256'],
 'twoPromptsExist':all((ROOT/'docs/plan'/p).is_file() for p in ['CODING-RECOVERY-AI-NEXT-PROMPT-2026-10-03.txt','BATCH-GENERATION-AI-NEXT-PROMPT-2026-10-03.txt']),
 'restoreDraftNoBackupClaim':all(x['remoteURI'] is None and not x['externalCopyVerified'] and not x['independentBackupVerified'] and not x['restoreVerified'] for x in read(OUT/'restore-manifest-draft.json')['files'])}
for x in s['rows']:
    for p in x['overviewEvidence']:
        if not (ROOT/p).is_file():raise ValueError(p)
for x in d['assets']:
    for p in x['evidence']:
        if not (ROOT/p).is_file():raise ValueError(p)
sizes={}
for name in ['assets/production','assets/delivery','qa/full-asset-verifier-20261003']:
    files=[p for p in (ROOT/name).rglob('*') if p.is_file()]
    sizes[name]={'files':len(files),'bytes':sum(p.stat().st_size for p in files)}
result={'scope':'planner artifact verification only; no game/build/device/provider test','checks':checks,'protectedFileCount':len(protected),'changedProtectedFiles':changed,'planningHistoryChanges':historybad,'currentSizes':sizes,'ordinaryGitOver100MiBRawFiles':[{'file':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size} for p in (ROOT/'assets/production').glob('*/provider-output/predictions.jsonl') if p.stat().st_size>100*1024**2],'gitattributesExists':(ROOT/'.gitattributes').exists()}
(OUT/'final-report-checks.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result))
if not all(checks.values()):raise SystemExit(1)
