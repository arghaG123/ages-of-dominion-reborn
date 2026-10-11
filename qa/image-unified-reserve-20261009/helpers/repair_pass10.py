"""Remove sparse guide-line pixels inside the measured foot boxes."""
from __future__ import annotations

import json

import cv2
import numpy as np

import process_local as pl
import repair_pass2 as p2


def thin_mask(rgba, box, color_fn, cap):
    x0, y0, x1, y1 = box
    visible = rgba[:, :, 3] > 16
    kernel = np.ones((7, 7), np.uint8)
    density = cv2.filter2D(visible.astype(np.uint8), -1, kernel, borderType=cv2.BORDER_CONSTANT)
    region = np.zeros(visible.shape, dtype=bool)
    region[y0:y1, x0:x1] = True
    rgb = rgba[:, :, :3].astype(np.int16)
    remove = region & visible & (density <= 8) & color_fn(rgb)
    count = int(remove.sum())
    if count == 0 or count > cap:
        return rgba, count if count else 0, count > cap
    out, safe = pl.apply_removal(rgba, remove)
    if not safe or out is None:
        raise RuntimeError("protected pixels would change")
    return out, count, False


def main():
    notes = []
    brute_path = pl.OUT_ASSETS / "actors/attackers/attacker-stone-brute.png"
    brute, n, skipped = thin_mask(
        pl.load_rgba(brute_path),
        (300, 766, 620, 860),
        lambda rgb: (rgb[:, :, 2] > 75) & (rgb[:, :, 1] > 60) & (rgb[:, :, 0] < 190),
        800,
    )
    if not skipped and n:
        pl.save_png(brute_path, brute)
        p2.flatten(brute_path, "attacker-stone-brute-pass10.jpg")
    notes.append({"id": "attacker-stone-brute", "removed": n, "skipped": skipped})

    wolf_path = pl.OUT_ASSETS / "actors/creatures/creature-wolf.png"
    wolf, n, skipped = thin_mask(
        pl.load_rgba(wolf_path),
        (350, 790, 560, 890),
        lambda rgb: (rgb[:, :, 2] > 50) & (rgb[:, :, 0] > rgb[:, :, 1] + 8) & (rgb[:, :, 1] < 120),
        800,
    )
    # Red marker measured beside the paws.
    rgb = wolf[:, :, :3].astype(np.int16)
    visible = wolf[:, :, 3] > 16
    box = np.zeros(visible.shape, dtype=bool)
    box[705:755, 415:465] = True
    dot = box & visible & (rgb[:, :, 0] > 90) & (rgb[:, :, 0] > rgb[:, :, 1] + 20) & (rgb[:, :, 1] < 100)
    dot_n = int(dot.sum())
    if 0 < dot_n <= 80:
        wolf, _ = pl.apply_removal(wolf, dot)
        wolf = wolf if wolf is not None else None
        n += dot_n
    if wolf is not None and not skipped:
        pl.save_png(wolf_path, wolf)
        p2.flatten(wolf_path, "creature-wolf-pass10.jpg")
    notes.append({"id": "creature-wolf", "removed": n, "dot": dot_n, "skipped": skipped})
    (pl.QA / "diagnostics/pass10.json").write_text(json.dumps(notes, indent=2), encoding="utf-8")
    print(json.dumps(notes))


if __name__ == "__main__":
    main()
