"""Publish planner pointers, preserving each existing document body verbatim."""
from pathlib import Path
import json,hashlib
ROOT=Path('C:/dev/ages-of-dominion-reborn'); QA=ROOT/'qa/code-art-next-verification-20261004'
report='CODE-ART-REPAIR-COMPLETION-VERIFICATION-2026-10-04.md'
prompt='CODE-ART-IMPLEMENTATION-NEXT-TASK-2026-10-04.txt'
rows=[]
for rel in ['CURRENT-STATUS.md','docs/SESSION-HANDOFF.md','docs/BUILD-PROGRESS.md','docs/PLANNER-VERIFIER-HANDOFF.md','docs/plan/README.md']:
    p=ROOT/rel; original=p.read_bytes()
    prefix='docs/plan/' if rel=='CURRENT-STATUS.md' else '' if rel=='docs/plan/README.md' else 'plan/'
    banner=(f'> **Latest independent Code/Art verification — 4 October 2026:** Full executor assignment remains **INCOMPLETE**. Fresh61tests and normal browser repairs PASS; seven explicit-null migration cases and two replacement failure-injection cases FAIL. Four built plots still use footprints/names, Hero stage is empty, Defense uses shapes;66delivery files unchanged. Old APK remains stale; device testing STOPPED; preservation destination null. Read [{report}]({prefix}{report}) and paste [{prompt}]({prefix}{prompt}) into the owner-selected Code/Art AI. Planner wrote QA/docs only: no code/art/provider/build/device/production/storage/Git mutation or delegation. Conditional image-only production move plus actual proven-redundancy cleanup remains recorded in the existing image handoff; no current first32promotion occurred.\n\n').encode('utf-8')
    if banner in original: raise RuntimeError(f'Already published: {rel}')
    p.write_bytes(banner+original)
    current=p.read_bytes(); rows.append({'file':rel,'originalSHA256':hashlib.sha256(original).hexdigest(),'currentSHA256':hashlib.sha256(current).hexdigest(),'originalBodyPreserved':current[len(banner):]==original})
(QA/'documentation-publication.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
print(json.dumps(rows,indent=2))
