"""Remove guide rectangles whose ink is one thin component larger than the pass8 cap."""
from __future__ import annotations

import json

import cv2
import numpy as np

import process_local as pl
import repair_pass2 as p2


def remove_mask(rgba, mask, limit):
    count = int(mask.sum())
    if count == 0:
        return rgba, 0
    if count > limit:
        return rgba, -count
    out, safe = pl.apply_removal(rgba, mask)
    if not safe or out is None:
        raise RuntimeError("protected pixels would change")
    return out, count


def thin_ink(rgba, y_ratio, limit):
    rgb = rgba[:, :, :3].astype(np.int16)
    visible = rgba[:, :, 3] > 16
    height = visible.shape[0]
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    band = np.zeros(visible.shape, dtype=bool)
    band[int(height * y_ratio):, :] = True
    line = band & visible & (b > 55) & (b > g + 10) & (g < 55) & (r > g + 20) & (r < 170)
    count, labels = cv2.connectedComponents(line.astype(np.uint8), connectivity=8)
    remove = np.zeros(visible.shape, dtype=bool)
    for label in range(1, count):
        component = labels == label
        area = int(component.sum())
        if area < 6 or area > 8000:
            continue
        ys, xs = np.nonzero(component)
        bw = int(xs.max() - xs.min() + 1)
        bh = int(ys.max() - ys.min() + 1)
        if bh > height * 0.28:
            continue
        if area > 0.45 * bw * bh and min(bw, bh) > 10:
            continue
        remove |= component
    return remove_mask(rgba, remove, limit)


def wolf_dot(rgba):
    rgb = rgba[:, :, :3].astype(np.int16)
    box = np.zeros(rgba.shape[:2], dtype=bool)
    box[700:760, 420:470] = True
    visible = (rgba[:, :, 3] > 16) & box
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    # The surviving marker is a small dark red disk, separate from gray fur.
    dot = visible & (r > g + 25) & (r > b) & (r > 70) & (g < 90)
    count, labels = cv2.connectedComponents(dot.astype(np.uint8), connectivity=8)
    remove = np.zeros(rgba.shape[:2], dtype=bool)
    for label in range(1, count):
        component = labels == label
        if int(component.sum()) <= 80:
            remove |= component
    return remove_mask(rgba, remove, 400)


def workshop_green(rgba):
    rgb = rgba[:, :, :3].astype(np.int16)
    visible = rgba[:, :, 3] > 16
    height, width = visible.shape
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    green = visible & (g > r + 3) & (g >= b) & (g > 22) & (g < 160)
    count, labels = cv2.connectedComponents(green.astype(np.uint8), connectivity=8)
    remove = np.zeros(visible.shape, dtype=bool)
    for label in range(1, count):
        component = labels == label
        area = int(component.sum())
        if area < 8 or area > 4000:
            continue
        ys, xs = np.nonzero(component)
        if float(ys.mean()) < height * 0.28 or float(xs.mean()) > width * 0.62:
            continue
        remove |= component
    return remove_mask(rgba, remove, 4000)


def main():
    notes = []
    for asset_id, path, fn, preview in (
        ("creature-wolf", pl.OUT_ASSETS / "actors/creatures/creature-wolf.png", lambda im: thin_ink(im, 0.60, 2500), "creature-wolf-pass9.jpg"),
        ("attacker-stone-brute", pl.OUT_ASSETS / "actors/attackers/attacker-stone-brute.png", lambda im: thin_ink(im, 0.66, 2500), "attacker-stone-brute-pass9.jpg"),
        ("workshop-iron", pl.OUT_ASSETS / "environment/buildings/workshop-iron.png", workshop_green, "workshop-iron-pass9.jpg"),
    ):
        image = pl.load_rgba(path)
        if asset_id == "creature-wolf":
            image, n1 = fn(image)
            image, n2 = wolf_dot(image)
            removed = None if n1 < 0 or n2 < 0 else n1 + n2
            if removed is None:
                notes.append({"id": asset_id, "skipped": [n1, n2]})
                continue
        else:
            image, removed = fn(image)
            if removed < 0:
                notes.append({"id": asset_id, "skipped": removed})
                continue
        pl.save_png(path, image)
        p2.flatten(path, preview)
        notes.append({"id": asset_id, "removed": removed})
    (pl.QA / "diagnostics/pass9.json").write_text(json.dumps(notes, indent=2), encoding="utf-8")
    print(json.dumps(notes))


if __name__ == "__main__":
    main()
