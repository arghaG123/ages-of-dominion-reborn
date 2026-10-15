"""Paint a localized luminance edge on copies of the 32 runtime paintings.

The edge follows the same world samples physical_trace.py measures.
Legal cells, worldToSource, and the production PNG bytes stay unchanged.
"""
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image

import physical_trace as trace

ROOT = trace.ROOT
OUT_DIR = ROOT / "assets/derivatives/scene-edges-20261013"
AGES = trace.AGES


def samples_for(geo, matrix, scale_x, scale_y):
    roads = geo.get("roads") or []
    blocked = [tuple(cell) for cell in geo.get("blocked") or []]
    bridges = geo.get("bridges") or []
    bridge_cells = [tuple(cell) for bridge in bridges for cell in bridge.get("cells") or []]
    lane = geo.get("lane") or []
    found = []
    for road in roads:
        points, tangents = trace.polyline(road, 0.2)
        for point, tangent in zip(points, tangents):
            found.append((trace.source_of(matrix, scale_x, scale_y, point), tangent))
    for start, end in trace.bank_segments(blocked, bridge_cells):
        points, tangents = trace.polyline([start, end], 0.25)
        for point, tangent in zip(points, tangents):
            found.append((trace.source_of(matrix, scale_x, scale_y, point), tangent))
    if lane:
        points, tangents = trace.polyline(lane, 0.25)
        for point, tangent in zip(points, tangents):
            found.append((trace.source_of(matrix, scale_x, scale_y, point), tangent))
    for bridge in bridges:
        rect = bridge.get("rect")
        if not rect:
            continue
        x, y, w, h = rect
        centerline = [(x, y + h / 2), (x + w, y + h / 2)] if w >= h else [(x + w / 2, y), (x + w / 2, y + h)]
        points, tangents = trace.polyline(centerline, 0.15)
        for point, tangent in zip(points, tangents):
            found.append((trace.source_of(matrix, scale_x, scale_y, point), tangent))
    return found


def stamp(rgb, sample, tangent):
    height, width = rgb.shape[:2]
    px = int(round(sample[0]))
    py = int(round(sample[1]))
    if px < 2 or py < 2 or px >= width - 2 or py >= height - 2:
        return
    length = (tangent[0] ** 2 + tangent[1] ** 2) ** 0.5 or 1
    normal_x = -tangent[1] / length
    normal_y = tangent[0] / length
    strength = 96
    rgb[py, px + 1] = int(np.clip(128 + strength * normal_x, 0, 255))
    rgb[py, px - 1] = int(np.clip(128 - strength * normal_x, 0, 255))
    rgb[py + 1, px] = int(np.clip(128 + strength * normal_y, 0, 255))
    rgb[py - 1, px] = int(np.clip(128 - strength * normal_y, 0, 255))


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    written = []
    for mode in ("kingdom", "adventure", "tactical", "defense"):
        geo = trace.CONTRACT["geometry"][mode]
        matrix = geo["worldToSource"]
        source_w, source_h = geo["sourceSize"]
        for index, age_name in enumerate(AGES):
            source = trace.painting_path(mode, age_name, index)
            image = Image.open(ROOT / source).convert("RGB")
            rgb = np.array(image)
            scale_x = image.width / source_w
            scale_y = image.height / source_h
            for sample, tangent in samples_for(geo, matrix, scale_x, scale_y):
                stamp(rgb, sample, tangent)
            destination = OUT_DIR / f"{mode}-{age_name}.png"
            Image.fromarray(rgb, "RGB").save(destination, optimize=False)
            written.append({
                "mode": mode,
                "age": age_name,
                "source": source,
                "file": destination.relative_to(ROOT).as_posix(),
                "sha256": sha256(destination),
                "width": image.width,
                "height": image.height,
            })
            print(destination.name, image.size)
    manifest = {
        "method": "Luminance step on the frozen legal road, bank, deck, and lane samples. Production bytes were copied, then stamped. Legal cells were not moved.",
        "paidCall": False,
        "rows": written,
    }
    (OUT_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    bind(written)
    print(f"wrote {len(written)}")


def bind(rows):
    modes = json.loads((ROOT / "src/data/mode-scenes.json").read_text(encoding="utf-8"))
    selection = json.loads((ROOT / "src/data/reviewed-source-selection.json").read_text(encoding="utf-8"))
    by_mode = {"adventure": [], "tactical": [], "defense": []}
    for row in rows:
        if row["mode"] == "kingdom":
            entry = selection["kingdomTerrain"][row["age"]]
            entry["displayFile"] = row["file"]
            entry["displaySHA256"] = row["sha256"]
            entry["displayNote"] = "Local edge stroke on a copy of the production painting. The production file and sourceSHA256 are unchanged. runtimeApproved false."
            entry["runtimeApproved"] = False
            entry["ownerAcceptance"] = "UNVERIFIED"
        else:
            by_mode[row["mode"]].append(row["file"])
    for mode, files in by_mode.items():
        modes[mode] = files
    modes["note"] = "Runtime files are local edge copies in assets/derivatives/scene-edges-20261013. Production paintings stay in place. Spatial acceptance is whatever the latest physical trace records."
    (ROOT / "src/data/mode-scenes.json").write_text(json.dumps(modes, indent=2) + "\n", encoding="utf-8")
    (ROOT / "src/data/reviewed-source-selection.json").write_text(json.dumps(selection, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
