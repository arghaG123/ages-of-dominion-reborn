"""Clear the measured leftovers: wolf green pads, workshop fringe, warlock dust, brute guide."""
from __future__ import annotations

import json

import cv2
import numpy as np

import process_local as pl
import repair_pass2 as p2


def remove_mask(rgba, mask):
    if int(mask.sum()) == 0:
        return rgba, 0
    out, safe = pl.apply_removal(rgba, mask)
    if not safe or out is None:
        raise RuntimeError("protected pixels would change")
    return out, int(mask.sum())


def select_components(mask, predicate):
    count, labels = cv2.connectedComponents(mask.astype(np.uint8), connectivity=8)
    remove = np.zeros(mask.shape, dtype=bool)
    notes = []
    for label in range(1, count):
        component = labels == label
        area = int(component.sum())
        ys, xs = np.nonzero(component)
        if ys.size == 0:
            continue
        bbox = [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]
        if predicate(component, area, bbox):
            remove |= component
            notes.append({"area": area, "bbox": bbox})
    return remove, notes


def wolf(rgba):
    rgb = rgba[:, :, :3].astype(np.int16)
    visible = rgba[:, :, 3] > 16
    height = visible.shape[0]
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    band = np.zeros(visible.shape, dtype=bool)
    band[int(height * 0.55):, :] = True
    green = band & visible & (g > r + 4) & (g > b) & (g > 30)
    remove, notes = select_components(green, lambda component, area, bbox: 12 <= area <= 4000)
    out, count = remove_mask(rgba, remove)
    return out, count, notes


def workshop(rgba):
    rgb = rgba[:, :, :3].astype(np.int16)
    visible = rgba[:, :, 3] > 16
    height = visible.shape[0]
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    green = visible & (g > r + 8) & (g > b + 6) & (g > 50) & (g < 190)
    def lawn(component, area, bbox):
        if area < 12 or area > 20000:
            return False
        ys = np.nonzero(component)[0]
        return float(ys.mean()) >= height * 0.26
    remove, notes = select_components(green, lawn)
    chroma = np.maximum(np.maximum(r, g), b) - np.minimum(np.minimum(r, g), b)
    neutral = visible & (r > 115) & (g > 115) & (b > 115) & (chroma < 28)
    def guide(component, area, bbox):
        bw = bbox[2] - bbox[0]
        bh = bbox[3] - bbox[1]
        if area < 30 or area > 8000 or max(bw, bh) < 80:
            return False
        if area > 0.22 * bw * bh:
            return False
        return bbox[1] > height * 0.28
    extra, extra_notes = select_components(neutral, guide)
    remove |= extra
    out, count = remove_mask(rgba, remove)
    return out, count, notes[:8] + extra_notes[:8]


def warlock(rgba):
    rgb = rgba[:, :, :3].astype(np.int16)
    visible = rgba[:, :, 3] > 16
    height, width = visible.shape
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    dust = np.zeros(visible.shape, dtype=bool)
    dust[int(height * 0.90):, :] = True
    light = dust & visible & (r > 120) & (g > 120) & (b > 120)
    remove, notes = select_components(light, lambda component, area, bbox: area >= 20)
    out, count = remove_mask(rgba, remove)
    return out, count, notes[:8]


def brute(rgba):
    rgb = rgba[:, :, :3].astype(np.int16)
    visible = rgba[:, :, 3] > 16
    height = visible.shape[0]
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    band = np.zeros(visible.shape, dtype=bool)
    band[int(height * 0.72):, :] = True
    # Pale guide ink. Feet in this band are brown with blue under 50.
    line = band & visible & (r > 130) & (g > 110) & (b > 120)
    def guide(component, area, bbox):
        bw = bbox[2] - bbox[0]
        bh = bbox[3] - bbox[1]
        if area < 20 or area > 5000:
            return False
        if bh > height * 0.2:
            return False
        return bh <= 8 or bw <= 8 or area < 0.5 * max(bw * bh, 1)
    remove, notes = select_components(line, guide)
    out, count = remove_mask(rgba, remove)
    return out, count, notes


def main():
    notes = []
    jobs = [
        ("creature-wolf", pl.OUT_ASSETS / "actors/creatures/creature-wolf.png", wolf, "creature-wolf-pass7.jpg"),
        ("workshop-iron", pl.OUT_ASSETS / "environment/buildings/workshop-iron.png", workshop, "workshop-iron-pass7.jpg"),
        ("class-warlock-standing-body", pl.OUT_ASSETS / "actors/bodies/class-warlock-standing-body.png", warlock, "class-warlock-pass7.jpg"),
        ("attacker-stone-brute", pl.OUT_ASSETS / "actors/attackers/attacker-stone-brute.png", brute, "attacker-stone-brute-pass7.jpg"),
    ]
    for asset_id, path, fn, preview in jobs:
        rgba = pl.load_rgba(path)
        out, count, detail = fn(rgba)
        pl.save_png(path, out)
        p2.flatten(path, preview)
        notes.append({"id": asset_id, "removed": count, "detail": detail, "preview": f"qa/image-unified-reserve-20261009/review/{preview}"})
    (pl.QA / "diagnostics/pass7.json").write_text(json.dumps(notes, indent=2), encoding="utf-8")
    print(json.dumps([{k: row[k] for k in ("id", "removed")} | {"parts": len(row["detail"])} for row in notes], indent=2))


if __name__ == "__main__":
    main()
