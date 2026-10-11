"""Remove the thin guide ink now that its color is measured."""
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


def ink(rgba, y_start_ratio, max_g, min_r):
    rgb = rgba[:, :, :3].astype(np.int16)
    visible = rgba[:, :, 3] > 16
    height = visible.shape[0]
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    band = np.zeros(visible.shape, dtype=bool)
    band[int(height * y_start_ratio):, :] = True
    # Measured guide ink is about RGB 90,25,75. Subject fur and skin are not.
    line = band & visible & (g < max_g) & (r > min_r) & (b > g + 12) & (r > g + 28) & (r < 160)
    count, labels = cv2.connectedComponents(line.astype(np.uint8), connectivity=8)
    remove = np.zeros(visible.shape, dtype=bool)
    for label in range(1, count):
        component = labels == label
        area = int(component.sum())
        if 6 <= area <= 600:
            remove |= component
    return remove_mask(rgba, remove)


def wolf_dot(rgba):
    rgb = rgba[:, :, :3].astype(np.int16)
    visible = rgba[:, :, 3] > 16
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    box = np.zeros(visible.shape, dtype=bool)
    box[690:760, 410:470] = True
    dot = box & visible & (r > 190) & (g > 130) & (b > 150) & (r > g)
    count, labels = cv2.connectedComponents(dot.astype(np.uint8), connectivity=8)
    remove = np.zeros(visible.shape, dtype=bool)
    for label in range(1, count):
        component = labels == label
        if int(component.sum()) <= 40:
            remove |= component
    return remove_mask(rgba, remove)


def workshop(rgba):
    rgb = rgba[:, :, :3].astype(np.int16)
    visible = rgba[:, :, 3] > 16
    height = visible.shape[0]
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    green = visible & (g > r + 6) & (g > b + 4) & (g > 45) & (g < 200)
    count, labels = cv2.connectedComponents(green.astype(np.uint8), connectivity=8)
    remove = np.zeros(visible.shape, dtype=bool)
    for label in range(1, count):
        component = labels == label
        area = int(component.sum())
        if area < 8 or area > 8000:
            continue
        ys = np.nonzero(component)[0]
        if float(ys.mean()) < height * 0.30:
            continue
        remove |= component
    chroma = np.maximum(np.maximum(r, g), b) - np.minimum(np.minimum(r, g), b)
    neutral = visible & (r > 80) & (g > 80) & (b > 80) & (chroma < 26)
    count, labels = cv2.connectedComponents(neutral.astype(np.uint8), connectivity=8)
    for label in range(1, count):
        component = labels == label
        area = int(component.sum())
        ys, xs = np.nonzero(component)
        bw = int(xs.max() - xs.min() + 1)
        bh = int(ys.max() - ys.min() + 1)
        if area < 20 or area > 6000 or max(bw, bh) < 70:
            continue
        if float(ys.mean()) < height * 0.25:
            continue
        if area > 0.18 * bw * bh:
            continue
        remove |= component
    return remove_mask(rgba, remove)


def warlock_specks(rgba):
    visible = rgba[:, :, 3] > 16
    count, labels = cv2.connectedComponents(visible.astype(np.uint8), connectivity=8)
    remove = np.zeros(visible.shape, dtype=bool)
    for label in range(1, count):
        component = labels == label
        area = int(component.sum())
        if area < 1 or area > 120:
            continue
        ys = np.nonzero(component)[0]
        if int(ys.min()) < 1760:
            continue
        remove |= component
    return remove_mask(rgba, remove)


def main():
    notes = []
    wolf_path = pl.OUT_ASSETS / "actors/creatures/creature-wolf.png"
    wolf = pl.load_rgba(wolf_path)
    wolf, n1 = ink(wolf, 0.62, 48, 60)
    wolf, n2 = wolf_dot(wolf)
    pl.save_png(wolf_path, wolf)
    p2.flatten(wolf_path, "creature-wolf-pass8.jpg")
    notes.append({"id": "creature-wolf", "removed": n1 + n2})

    brute_path = pl.OUT_ASSETS / "actors/attackers/attacker-stone-brute.png"
    brute, n3 = ink(pl.load_rgba(brute_path), 0.68, 42, 70)
    pl.save_png(brute_path, brute)
    p2.flatten(brute_path, "attacker-stone-brute-pass8.jpg")
    notes.append({"id": "attacker-stone-brute", "removed": n3})

    shop_path = pl.OUT_ASSETS / "environment/buildings/workshop-iron.png"
    shop, n4 = workshop(pl.load_rgba(shop_path))
    pl.save_png(shop_path, shop)
    p2.flatten(shop_path, "workshop-iron-pass8.jpg")
    notes.append({"id": "workshop-iron", "removed": n4})

    lock_path = pl.OUT_ASSETS / "actors/bodies/class-warlock-standing-body.png"
    lock, n5 = warlock_specks(pl.load_rgba(lock_path))
    pl.save_png(lock_path, lock)
    p2.flatten(lock_path, "class-warlock-pass8.jpg")
    notes.append({"id": "class-warlock-standing-body", "removed": n5})
    (pl.QA / "diagnostics/pass8.json").write_text(json.dumps(notes, indent=2), encoding="utf-8")
    print(json.dumps(notes))


if __name__ == "__main__":
    main()
