"""Read-only comparison of v7 blue candidates with widened arithmetic.

Writes planner QA only; neither candidate mask is a geographical annotation.
"""
import json
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
rows = json.loads((ROOT / 'qa/image-local-continuation-20261005/scene-survey-summary.json').read_text())
results = []
for row in rows:
    with Image.open(ROOT / row['path']) as im:
        rgb = np.asarray(im.convert('RGB').resize((1376, 768), Image.Resampling.BOX))
    wide = rgb.astype(np.int16)
    def candidate(a):
        return (a[:, :, 2] > a[:, :, 0] + 18) & (a[:, :, 2] > a[:, :, 1] + 8) & (a[:, :, 2] > 70)
    old, corrected = candidate(rgb), candidate(wide)
    results.append({'id': row['id'], 'path': row['path'], 'grid': [1376, 768],
                    'uint8Candidates': int(old.sum()), 'wideCandidates': int(corrected.sum()),
                    'candidatePixelsChanged': int(np.count_nonzero(old != corrected)),
                    'uint8Only': int(np.count_nonzero(old & ~corrected)),
                    'wideOnly': int(np.count_nonzero(corrected & ~old))})
report = {'scope': 'Actual 32 source images at v7 legal-grid size, candidate mask before component filtering only',
          'limitations': 'Not measured river/bank accuracy, component acceptance, legal geometry or runtime impact.',
          'rows': results, 'changedScenes': sum(r['candidatePixelsChanged'] > 0 for r in results)}
(ROOT / 'qa/planner-verification-20261005/survey-arithmetic-report.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'scenes': len(results), 'changedScenes': report['changedScenes'],
                  'candidatePixelsChanged': sum(r['candidatePixelsChanged'] for r in results)}))
