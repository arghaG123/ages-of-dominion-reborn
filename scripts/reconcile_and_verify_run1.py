import json
import hashlib
from pathlib import Path
from PIL import Image

run1 = Path('assets/high-res/interactive-4k-first32-20261003/run-01-20261003-172733')
journal = json.loads((run1 / 'journal.json').read_text(encoding='utf-8'))

print("=== VERIFYING RUN-01 SUCCESSFUL OUTPUTS ===")
succeeded = []
for att in journal['attempts']:
    if att.get('status') == 'SUCCEEDED':
        p = Path(att['outputFile'])
        if not p.exists():
            print(f"ERROR: {p} missing")
            continue
        img = Image.open(p)
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        assert h == att['sha256'], f"Hash mismatch: {p}"
        assert list(img.size) == att['dimensions'], f"Dimension mismatch: {p}"
        succeeded.append(att)
        print(f"[{att['order']:02d}/32] {att['id']:26s} {img.size} {h[:16]}... OK")

print(f"Verified {len(succeeded)} successful 4K outputs.")
