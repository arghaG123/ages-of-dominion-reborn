"""Color of the thin guide lines inside the confirmed crops."""
from __future__ import annotations

import json

import cv2
import numpy as np

import process_local as pl


def describe(rgba, box, label):
    x0, y0, x1, y1 = box
    crop = rgba[y0:y1, x0:x1]
    rgb = crop[:, :, :3].astype(np.int16)
    a = crop[:, :, 3]
    vis = a > 10
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    # Non-subject: low green relative to red or blue, or very thin neutral.
    odd = vis & (((r > g + 6) & (b > g)) | ((r > 140) & (g < 80) & (b < 80)))
    count, labels = cv2.connectedComponents(odd.astype(np.uint8), connectivity=8)
    rows = []
    for lab in range(1, count):
        component = labels == lab
        area = int(component.sum())
        if area < 8:
            continue
        ys, xs = np.nonzero(component)
        rows.append({
            "area": area,
            "bbox": [int(xs.min()) + x0, int(ys.min()) + y0, int(xs.max()) + 1 + x0, int(ys.max()) + 1 + y0],
            "mean": [round(float(v), 1) for v in rgb[component].mean(axis=0)],
        })
    rows.sort(key=lambda row: -row["area"])
    small = vis.copy()
    # whole-image subject separation is separate; here report alpha histogram of crop
    return {
        "label": label,
        "opaque": int(vis.sum()),
        "oddPixels": int(odd.sum()),
        "top": rows[:10],
        "alphaBins": {
            "1-40": int(((a > 0) & (a <= 40)).sum()),
            "41-120": int(((a > 40) & (a <= 120)).sum()),
            "121-255": int((a > 120).sum()),
        },
    }


def main():
    wolf = pl.load_rgba(pl.OUT_ASSETS / "actors/creatures/creature-wolf.png")
    brute = pl.load_rgba(pl.OUT_ASSETS / "actors/attackers/attacker-stone-brute.png")
    shop = pl.load_rgba(pl.OUT_ASSETS / "environment/buildings/workshop-iron.png")
    lock = pl.load_rgba(pl.OUT_ASSETS / "actors/bodies/class-warlock-standing-body.png")
    report = [
        describe(wolf, (340, 700, 580, 900), "wolf"),
        describe(brute, (250, 620, 700, 860), "brute"),
        describe(shop, (250, 400, 700, 750), "workshop-left"),
        describe(lock, (1000, 1800, 1700, 2048), "warlock-right"),
    ]
    # Small disconnected specks on the full warlock below y 1700.
    vis = lock[:, :, 3] > 10
    count, labels = cv2.connectedComponents(vis.astype(np.uint8), connectivity=8)
    specks = []
    for lab in range(1, count):
        component = labels == lab
        area = int(component.sum())
        if area > 800:
            continue
        ys, xs = np.nonzero(component)
        if int(ys.min()) < 1700:
            continue
        specks.append(area)
    report.append({"warlockSmallComponentsBelow1700": len(specks), "pixels": int(sum(specks))})
    print(json.dumps(report, indent=2)[:9000])


if __name__ == "__main__":
    main()
