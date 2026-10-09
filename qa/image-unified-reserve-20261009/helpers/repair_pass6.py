"""Remove the pass5 leftovers that pixel dumps separated from the subjects."""
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


def components(mask):
    count, labels = cv2.connectedComponents(mask.astype(np.uint8), connectivity=8)
    return count, labels


def wolf_chroma(rgba):
    rgb = rgba[:, :, :3].astype(np.int16)
    visible = rgba[:, :, 3] > 16
    height = visible.shape[0]
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    band = np.zeros(visible.shape, dtype=bool)
    band[int(height * 0.42):, :] = True
    # Dim chroma pads the r>130 gate left behind. Fur in this band has g around 70.
    chroma = band & visible & (g < 28) & (r > 100) & (b > 90) & (np.abs(r - b) < 55)
    marker_green = band & visible & (g > r + 25) & (g > b + 10) & (g > 70) & (g < 180)
    marker_red = band & visible & (r > 160) & (g < 70) & (b < 80) & ((r - g) > 80)
    remove = chroma.copy()
    for mask, limit in ((marker_green, 2500), (marker_red, 200)):
        count, labels = components(mask)
        for label in range(1, count):
            component = labels == label
            if int(component.sum()) <= limit:
                remove |= component
    return remove_mask(rgba, remove)


def workshop_lawn(rgba):
    rgb = rgba[:, :, :3].astype(np.int16)
    visible = rgba[:, :, 3] > 16
    height, width = visible.shape
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    green = visible & (g > r + 8) & (g > b + 6) & (g > 55) & (g < 190)
    count, labels = components(green)
    remove = np.zeros(visible.shape, dtype=bool)
    for label in range(1, count):
        component = labels == label
        area = int(component.sum())
        if area < 80:
            continue
        ys = np.nonzero(component)[0]
        if float(ys.mean()) < height * 0.26:
            continue
        if float((g - r)[component].mean()) < 8:
            continue
        remove |= component
    # One-pixel same-predicate fringe. Not a threshold flood.
    if remove.any():
        touch = cv2.dilate(remove.astype(np.uint8), np.ones((3, 3), np.uint8), iterations=1).astype(bool)
        remove |= green & touch
    # Thin neutral guide rectangle, not stone texture.
    neutral = visible & (r > 165) & (g > 165) & (b > 165) & ((np.maximum(np.maximum(r, g), b) - np.minimum(np.minimum(r, g), b)) < 35)
    count, labels = components(neutral)
    for label in range(1, count):
        component = labels == label
        area = int(component.sum())
        if area < 40 or area > 12000:
            continue
        ys, xs = np.nonzero(component)
        bw = int(xs.max() - xs.min() + 1)
        bh = int(ys.max() - ys.min() + 1)
        if max(bw, bh) < 90:
            continue
        if float(ys.mean()) < height * 0.30:
            continue
        if area > 0.30 * bw * bh:
            continue
        remove |= component
    return remove_mask(rgba, remove)


def brute_guide(rgba):
    rgb = rgba[:, :, :3].astype(np.int16)
    visible = rgba[:, :, 3] > 16
    height = visible.shape[0]
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    band = np.zeros(visible.shape, dtype=bool)
    band[int(height * 0.62):, :] = True
    # Skin in the loose dump sits near g=120. Feet are dark and almost neutral.
    line = band & visible & (g < 90) & (r > g + 30) & (b > g + 10)
    count, labels = components(line)
    remove = np.zeros(visible.shape, dtype=bool)
    kept = []
    for label in range(1, count):
        component = labels == label
        area = int(component.sum())
        if area < 25 or area > 4000:
            continue
        ys, xs = np.nonzero(component)
        bw = int(xs.max() - xs.min() + 1)
        bh = int(ys.max() - ys.min() + 1)
        if bh > height * 0.22:
            continue
        thin = bh <= 6 or bw <= 6 or area < 0.45 * bw * bh
        if not thin or max(bw, bh) < 36:
            continue
        remove |= component
        kept.append({"area": area, "bbox": [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]})
    out, count_removed = remove_mask(rgba, remove)
    return out, count_removed, kept


def warlock_floor(rgba):
    rgb = rgba[:, :, :3].astype(np.int16)
    visible = rgba[:, :, 3] > 16
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    white = visible & (r > 200) & (g > 200) & (b > 190)
    count, labels = components(white)
    remove = np.zeros(visible.shape, dtype=bool)
    for label in range(1, count):
        component = labels == label
        area = int(component.sum())
        if area < 4000:
            continue
        ys = np.nonzero(component)[0]
        if int(ys.min()) < 1600:
            continue
        remove |= component
    return remove_mask(rgba, remove)


def drone_contract(rgba):
    frames = pl.split_frames(rgba, "creature-drone")
    stale = pl.OUT_ASSETS / "actors/frames/creature-drone/03.png"
    stale_note = None
    if stale.exists() and len(frames) <= 3:
        stale.unlink()
        stale_note = "deleted stale frame 03; current sheet split has three subject components"
    for frame in frames:
        frame["durationMs"] = None
        frame["timing"] = "BLOCKED"
    return frames, stale_note


def recount(name, rgba, kind):
    rgb = rgba[:, :, :3].astype(np.int16)
    visible = rgba[:, :, 3] > 16
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    if kind == "wolf":
        height = visible.shape[0]
        band = np.zeros(visible.shape, dtype=bool)
        band[int(height * 0.42):, :] = True
        mask = band & visible & (g < 28) & (r > 100) & (b > 90)
    elif kind == "workshop":
        mask = visible & (g > r + 8) & (g > b + 6) & (g > 55) & (g < 190)
    elif kind == "warlock":
        mask = visible & (r > 200) & (g > 200) & (b > 190)
        ys = np.nonzero(mask)[0]
        return {"id": name, "whitePixels": int(mask.sum()), "lowestWhiteY": int(ys.min()) if ys.size else None}
    else:
        mask = visible & (g < 90) & (r > g + 30) & (b > g + 10)
    return {"id": name, "remainingMatchedPixels": int(mask.sum())}


def main():
    notes = []
    jobs = [
        ("creature-wolf", pl.OUT_ASSETS / "actors/creatures/creature-wolf.png", wolf_chroma, "creature-wolf-pass6.jpg", "wolf"),
        ("workshop-iron", pl.OUT_ASSETS / "environment/buildings/workshop-iron.png", workshop_lawn, "workshop-iron-pass6.jpg", "workshop"),
        ("class-warlock-standing-body", pl.OUT_ASSETS / "actors/bodies/class-warlock-standing-body.png", warlock_floor, "class-warlock-pass6.jpg", "warlock"),
    ]
    for asset_id, path, fn, preview, kind in jobs:
        rgba = pl.load_rgba(path)
        out, count = fn(rgba)
        pl.save_png(path, out)
        p2.flatten(path, preview)
        notes.append({"id": asset_id, "removed": count, "after": recount(asset_id, out, kind), "preview": f"qa/image-unified-reserve-20261009/review/{preview}"})
    brute_path = pl.OUT_ASSETS / "actors/attackers/attacker-stone-brute.png"
    brute = pl.load_rgba(brute_path)
    bout, bcount, kept = brute_guide(brute)
    pl.save_png(brute_path, bout)
    p2.flatten(brute_path, "attacker-stone-brute-pass6.jpg")
    notes.append({"id": "attacker-stone-brute", "removed": bcount, "components": kept, "after": recount("attacker-stone-brute", bout, "brute")})
    drone = pl.load_rgba(pl.OUT_ASSETS / "actors/creatures/creature-drone.png")
    frames, stale = drone_contract(drone)
    notes.append({"id": "creature-drone", "removed": 0, "staleFrame": stale, "frames": frames, "timing": "BLOCKED", "durationMs": None})
    (pl.QA / "diagnostics/pass6.json").write_text(json.dumps(notes, indent=2), encoding="utf-8")
    brief = []
    for row in notes:
        brief.append({k: row[k] for k in row if k != "frames"})
    print(json.dumps(brief, indent=2))


if __name__ == "__main__":
    main()
