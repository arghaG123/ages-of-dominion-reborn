"""Per-plate metrics for the live override outputs. Metrics are not a matte or subject pass."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
overrides = json.loads((ROOT / "src/data/plate-overrides-20261007.json").read_text(encoding="utf-8"))
reviewed = {
    "5-support": "REPAIRED_FLAT_MAGENTA_FLOOD. Violet and cyan energy copied from the source. Corner alpha is 0.",
    "3-archer": "REPAIRED_FLAT_OLIVE_FLOOD. Subject coat and bow kept. Corner alpha is 0.",
    "1-heavy": "WRONG_SUBJECT. One infantryman on a dirt slab. Not Charioteer crew, horse and vehicle. Pixels were not relabelled.",
}
rows = []
for group, entries in overrides.items():
    if not isinstance(entries, dict):
        continue
    for key, plate in entries.items():
        if not isinstance(plate, dict) or "file" not in plate:
            continue
        image = np.array(Image.open(ROOT / plate["file"]).convert("RGBA"))
        rgb = image[:, :, :3].astype(np.int16)
        alpha = image[:, :, 3]
        opaque = alpha > 16
        magenta = opaque & (rgb[:, :, 0] > 180) & (rgb[:, :, 2] > 180) & (rgb[:, :, 1] < 80)
        count = int(opaque.sum())
        rows.append({
            "group": group,
            "id": key,
            "file": plate["file"],
            "sha256": plate.get("sha256"),
            "opaque": count,
            "magentaOpaque": int(magenta.sum()),
            "magentaFractionOfOpaque": (int(magenta.sum()) / count) if count else None,
            "cornerAlpha": int(alpha[0, 0]),
            "review": reviewed.get(key, "UNREVIEWED. Hash and magenta fraction are not subject, era, rig or matte acceptance."),
        })
out = ROOT / "qa/code-image-repair-20261011/plate-classification.json"
out.write_text(json.dumps({"count": len(rows), "rows": rows}, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"count": len(rows), "reviewed": sorted(reviewed)}))
