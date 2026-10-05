from pathlib import Path
import hashlib, json, os
from datetime import datetime, timezone

root = Path('C:/dev/ages-of-dominion-reborn')
qa = root / 'qa/code-art-finish-audit-20261004'
targets = ['CURRENT-STATUS.md', 'docs/SESSION-HANDOFF.md', 'docs/BUILD-PROGRESS.md', 'docs/PLANNER-VERIFIER-HANDOFF.md', 'docs/plan/README.md']
records = []
for name in targets:
    path = root / name
    prefix = 'docs/plan/' if '/' not in name else ('' if name.startswith('docs/plan/') else 'plan/')
    marker = '> **Independent closing Code/Art and image verification — 4 October 2026:**'
    banner = (marker + ' Ready game/art work remains **INCOMPLETE**. Fresh69tests, ten strict migration probes and two replacement-failure probes PASS; legal core Auto journey clears both guards, settles/reloads once and returns to town (construction accelerated; full manual UI journey/visual acceptance unverified). Completed buildings now paint, but Hero shows a parts sheet and Defense/Army consumers remain schematic; existing APK is stale against nine source files and lacks current pad-fit data/new derivatives. Device QA STOPPED; storage/Git preservation destinations remain unresolved for those steps only. Read [Code/Art audit](' + prefix + 'CODE-ART-FINISH-READY-WORK-AUDIT-2026-10-04.md) and [complete ready-work prompt](' + prefix + 'CODE-ART-FINISH-ALL-READY-PROMPT-2026-10-04.txt).\n\n'
        '> **Image closing snapshot:** Owner-reported71 became **73/73 distinct native2048 PNGs** during the audit; all full decodes and recorded source/request/response/native bindings PASS. All are RGB without alpha; content/layout/derivative/runtime/owner acceptance remains incomplete, with scoped wrong-role/stencil/rig failures. Three isolated control probes FAIL (concurrent acquisition, dead-PID UNKNOWN takeover, unresolved UNKNOWN normal release). Two original ambiguous attempts remain unreconciled despite later successes, and cost/hold ledgers disagree. No new paid scope: next Image AI task is local reviews/crops/mattes/measured parts, control/accounting repair and useful Code AI handoff. Read [closing image audit](' + prefix + 'IMAGE-LATER73-INDEPENDENT-CLOSING-AUDIT-2026-10-04.md) and [complete next Image AI task](' + prefix + 'IMAGE-AI-DELIVER73-AND-REPAIR-CONTROLS-PROMPT-2026-10-04.txt). Planner wrote QA/docs only; no provider/project queries, paid calls, production/source/lock/budget/game/build/device/storage/Git mutations, executor messages or delegation. Concurrent executor banners and dated history below are preserved.\n\n')
    before = path.read_bytes()
    if before.decode('utf-8-sig').startswith(marker):
        records.append({'file': name, 'alreadyPublished': True})
        continue
    encoded = banner.encode('utf-8')
    tmp = path.with_name(path.name + '.audit-publication.tmp')
    tmp.write_bytes(encoded + before)
    if path.read_bytes() != before:
        tmp.unlink()
        raise RuntimeError('Concurrent edit: retry after refreshing ' + name)
    os.replace(tmp, path)
    after = path.read_bytes()
    records.append({'file': name, 'priorSHA256': hashlib.sha256(before).hexdigest(), 'publishedSHA256': hashlib.sha256(after).hexdigest(), 'entirePriorBytesPreserved': after[len(encoded):] == before})

artifacts = [root / 'docs/plan' / f for f in ['CODE-ART-FINISH-READY-WORK-AUDIT-2026-10-04.md', 'CODE-ART-FINISH-ALL-READY-PROMPT-2026-10-04.txt', 'IMAGE-LATER73-INDEPENDENT-CLOSING-AUDIT-2026-10-04.md', 'IMAGE-AI-DELIVER73-AND-REPAIR-CONTROLS-PROMPT-2026-10-04.txt']]
result = {'at': datetime.now(timezone.utc).isoformat(), 'pointers': records, 'artifacts': [{'file': str(p.relative_to(root)), 'exists': p.exists(), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in artifacts]}
(qa / 'publication.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps(result, indent=2))
