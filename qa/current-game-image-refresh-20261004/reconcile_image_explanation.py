"""Planner-only evidence bindings and preserved handoff pointers."""
import datetime, hashlib, json, pathlib

ROOT = pathlib.Path('C:/dev/ages-of-dominion-reborn')
OUT = ROOT / 'qa/current-game-image-refresh-20261004'
paths = [
    'qa/image-matte-decision-20261004/rigs/healer-uncovered.png',
    'qa/image-matte-decision-20261004/inspect/healer-source-900.png',
    'assets/derivatives/rigs/v4/healer/arm_upper_left.png',
    'assets/derivatives/rigs/v4/healer/boot_leg_left.png',
    'qa/image-v4-repair-20261004/rigs-v4.json',
    'src/data/reference-data.json',
    'docs/plan/REPLACEMENT-DRAFT-THREE-ROLES-2026-10-04.json',
]
bindings = []
for name in paths:
    data = (ROOT / name).read_bytes()
    bindings.append({'path': name, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
preserved = []
marker = b'> **Owner-supplied Image explanation reconciled'
for name, prefix in [
    ('CURRENT-STATUS.md', 'docs/plan/'),
    ('docs/SESSION-HANDOFF.md', 'plan/'),
    ('docs/BUILD-PROGRESS.md', 'plan/'),
]:
    p = ROOT / name
    old = p.read_bytes()
    if old.startswith(marker):
        continue
    note = (
        '> **Owner-supplied Image explanation reconciled — 4 October 2026, planner/verifier:** '
        f'[Updated report]({prefix}CURRENT-GAME-AND-IMAGE-SOLUTION-AUDIT-2026-10-04.md) and existing '
        f'[Image brief]({prefix}IMAGE-AI-CONSOLIDATED-LOCAL-SOLUTION-2026-10-04.txt) / '
        f'[Code brief]({prefix}CODE-AI-CURRENT-GAME-COMPLETE-BRIEF-2026-10-04.txt) now reflect source limits, '
        'bounded Healer extraction and corrected anatomy mappings (waist armor mislabeled arm; upper leg mislabeled foot), '
        'measured joint attempts and the canonical Charioteer/Slinger roles. Optional Modern mound trim stays snow-specific. '
        'Three-role replacement remains DRAFT_NOT_SUBMITTED / OWNER_BUDGET_AUTHORIZATION_REQUIRED; no new paid authority. '
        'codeAIHandoffReady remains false; ready Code work continues independently. Planner docs/QA only, no dispatch or production edits. '
        'Device STOPPED. Historical content preserved below.\r\n\r\n'
    ).encode('utf-8')
    p.write_bytes(note + old)
    assert p.read_bytes()[len(note):] == old
    preserved.append({'path': name, 'oldContentPreserved': True, 'oldSha256': hashlib.sha256(old).hexdigest()})
(OUT / 'image-explanation-reconciliation.json').write_text(json.dumps({
    'timeUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'evidenceBindings': bindings,
    'handoffPreservation': preserved,
    'paintedSourceLimits': 'Accepted where required pixels/pose are absent; no replacement authorization.',
    'healer': 'Uncovered painted arms/lower legs/boots exist; two v4 semantic names contradicted by viewed pixels. Clean extraction/joints not yet accepted.',
    'jointMethod': 'Prior crop-edge failure not universal impossibility; bounded measured padded test proposed, not executed.',
    'productionMutations': False,
    'executorDispatch': False,
    'paidAuthorization': False,
}, indent=2), encoding='utf-8')
print(json.dumps({'evidenceBindings': len(bindings), 'handoffsPreserved': preserved}, indent=2))
