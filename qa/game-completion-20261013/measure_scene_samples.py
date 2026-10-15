"""Sample legal road pixels against a strict blue-water mask.

This does not accept a scene. It records how often the frozen legal roads
land on saturated blue water after the painting is fitted to 1376x768.
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "scene-trace.json"
contract = json.loads((ROOT / "src/data/implementation-contract.json").read_text(encoding="utf-8"))
modes = json.loads((ROOT / "src/data/mode-scenes.json").read_text(encoding="utf-8"))
selection = json.loads((ROOT / "src/data/reviewed-source-selection.json").read_text(encoding="utf-8"))
ages = ["stone", "bronze", "iron", "medieval", "gunpowder", "industrial", "modern", "future"]

def project(matrix, point):
    a, b, c, d, e, f = matrix
    x, y = point
    return a * x + c * y + e, b * x + d * y + f

def samples(points):
    found = []
    for start, end in zip(points, points[1:]):
        length = max(abs(end[0] - start[0]), abs(end[1] - start[1]))
        steps = max(1, int(length / 12))
        for step in range(steps + 1):
            t = step / steps
            found.append((start[0] + (end[0] - start[0]) * t, start[1] + (end[1] - start[1]) * t))
    return found or points

def water_hits(path, matrix, roads, cell_center):
    image = Image.open(ROOT / path).convert("RGB")
    fitted = np.asarray(image.resize((1376, 768), Image.Resampling.BILINEAR))
    red = fitted[:, :, 0].astype(np.int16)
    green = fitted[:, :, 1].astype(np.int16)
    blue = fitted[:, :, 2].astype(np.int16)
    water = (blue > red + 35) & (blue > green + 15) & (blue > 70)
    hit = 0
    total = 0
    for road in roads:
        points = samples([project(matrix, [p[0] + (0.5 if cell_center else 0), p[1] + (0.5 if cell_center else 0)]) for p in road])
        for x, y in points:
            px, py = int(round(x)), int(round(y))
            if px < 0 or py < 0 or px >= 1376 or py >= 768:
                continue
            total += 1
            if water[py, px]:
                hit += 1
    return {"source": path, "sourceWidth": image.width, "sourceHeight": image.height, "samples": total, "waterHits": hit}

rows = []
for age, name in enumerate(ages):
    chosen = selection["kingdomTerrain"][name]
    path = chosen.get("displayFile") or chosen["sourceFile"]
    rows.append({"scene": "kingdom", "age": age, **water_hits(path, contract["geometry"]["kingdom"]["worldToSource"], contract["geometry"]["kingdom"].get("roads", []), False)})
for mode in ("adventure", "tactical", "defense"):
    matrix = contract["geometry"][mode]["worldToSource"]
    roads = contract["geometry"][mode].get("roads", [])
    for age, path in enumerate(modes[mode]):
        rows.append({"scene": mode, "age": age, **water_hits(path, matrix, roads, mode != "kingdom")})

for row in rows:
    ratio = (row["waterHits"] / row["samples"]) if row["samples"] else 1
    row["waterRatio"] = round(ratio, 4)
    row["geometryGate"] = "FAIL" if ratio > 0.02 or row["samples"] == 0 else "UNVERIFIED"
    row["reviewNotes"] = "Sampled legal-road pixels on a blue-water mask. UNVERIFIED means the sample missed saturated blue water. It is not physical-trace acceptance."

report = {
    "method": "1376x768 fit, frozen worldToSource, strict blue-water sample",
    "acceptance": "NOT_ACCEPTED",
    "fail": sum(row["geometryGate"] == "FAIL" for row in rows),
    "unverified": sum(row["geometryGate"] == "UNVERIFIED" for row in rows),
    "rows": rows,
}
OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
print(f"fail={report['fail']} unverified={report['unverified']} wrote {OUT}")
