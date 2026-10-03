"""Refresh planner-owned pointers only; retain the initial diagnostic snapshot."""
from pathlib import Path
import hashlib, json

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
changes=[]
def update(relative, pairs):
    p=ROOT/relative; before=p.read_bytes(); s=before.decode('utf-8')
    for old,new in pairs:
        if old not in s: raise ValueError((relative,old))
        s=s.replace(old,new,1)
    p.write_bytes(s.encode('utf-8'))
    changes.append({'file':relative,'beforeSHA256':hashlib.sha256(before).hexdigest(),'afterSHA256':hashlib.sha256(p.read_bytes()).hexdigest()})

for f in ['CURRENT-STATUS.md','START-HERE.md','RESUME-HERE.md','DECISIONS.md','docs/SESSION-HANDOFF.md','docs/BUILD-PROGRESS.md','docs/PLANNER-VERIFIER-HANDOFF.md','docs/plan/README.md','docs/plan/FULL-IMPLEMENTATION-SPEC.md']:
    update(f,[('Snapshot270 originals/265 IDs through09; all current output hashes match','Initial snapshot270 originals/265 IDs through09; incremental refresh at17:50:31 IST confirms300 originals/295 IDs through10; all inspected output hashes match'),('Consumer discovery270/90 historical/180 unreviewed','Refreshed consumer discovery300/90 historical/210 collection-only UNVERIFIED')])

update('docs/plan/RECOVERY-V3-PLANNER-AUDIT-2026-10-03.md',[
    ('Local snapshot: batches01–09, **270 original outputs / 265 distinct IDs**.','Initial local snapshot: batches01–09, **270 original outputs / 265 distinct IDs**.'),
    ('Subsequent collections must be discovered afresh, not inferred from this count.','Subsequent collections must be discovered afresh, not inferred from this count.\n\nFinal incremental refresh at **17:50:31 IST / 12:20:31 UTC** found batch10: **300 originals / 295 distinct IDs through01–10**. All30 new outputs match their collection hashes; the initial270 snapshot remains preserved. The consumer now discovers300 rows,90 historical plus210 collection-only UNVERIFIED, with0 source-stale/output-stale flags and the same correctly bound scene FAIL. See [incremental collection evidence](../../qa/planner-verifier-v3-20261003/incremental-collection-refresh.json). Batch10 adds creatures, attacker variants and portraits; it does not replace the six incorrect heavy identities. Neither09 nor10 received fresh raw-payload/prompt decoding, fine visual approval or rig verification here. No provider query establishes live11–13 state.'),
    ('with270 local originals this condition is false','with the initial270 and refreshed300 local originals this condition is false')
])

update('docs/plan/CODING-RECOVERY-AI-V3-NEXT-PROMPT-2026-10-03.txt',[
    ("The verifier found270 local originals through09,265 distinct IDs, all matching collection hashes; the240 recovery report covers01–08. Discover current collections dynamically.","The verifier's initial snapshot found270 local originals through09/265 distinct IDs; its final17:50:31 IST incremental refresh found300 through10/295 distinct IDs. All inspected output hashes match collection records; the240 recovery report covers01–08. Preserve both snapshots and discover current collections dynamically."),
    ('Batch09 and any later collection have not received fine visual/rig approval.','Batches09/10 and any later collection have not received fresh fine visual/rig approval; hash presence alone is insufficient.'),
    ('Current benchmark len(assets)==240 is false at270','Current benchmark len(assets)==240 is false at300')
])

update('docs/plan/BATCH-GAP-OWNER-HANDOFF-V3-2026-10-03.txt',[
    ('request to repeat production09. Planner local snapshot now contains270 originals through09;09\'s30 images match its collection hashes but have no new fine visual/rig approval.','request to repeat production09/10. Planner final17:50:31 IST refresh contains300 originals/295 distinct IDs through10;09/10 output hashes match collection records but have no new fine visual/rig approval.'),
    ('remaining unsubmitted10–13 manifest','remaining unsubmitted11–13 manifest (live state must be reconciled by you)')
])
(OUT/'final-planning-refresh.json').write_text(json.dumps(changes,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'plannerDocumentsRefreshed':len(changes),'initialSnapshotPreserved':True}))
