"""Sample the leftovers still visible after pass6."""
from __future__ import annotations

import json

import cv2
import numpy as np

import process_local as pl


def top(mask, rgb, limit=8):
    count, labels = cv2.connectedComponents(mask.astype(np.uint8), connectivity=8)
    rows = []
    for label in range(1, count):
        component = labels == label
        area = int(component.sum())
        if area < 12:
            continue
        ys, xs = np.nonzero(component)
        sample = rgb[component].mean(axis=0)
        rows.append({
            "area": area,
            "bbox": [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1],
            "mean": [round(float(v), 1) for v in sample],
            "a": round(float(component.sum() and 0)),
        })
    rows.sort(key=lambda row: -row["area"])
    return rows[:limit]


def main():
    report = {}
    wolf = pl.load_rgba(pl.OUT_ASSETS / "actors/creatures/creature-wolf.png")
    rgb = wolf[:, :, :3].astype(np.int16)
    a = wolf[:, :, 3]
    vis = a > 16
    h, w = vis.shape
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    band = np.zeros(vis.shape, dtype=bool)
    band[int(h * 0.55):, :] = True
    green = band & vis & (g > r + 4) & (g > b) & (g > 35)
    report["wolfGreen"] = top(green, rgb)
    # Any opaque pixel in the lower-center paw box from the last pure-pad location.
    box = np.zeros(vis.shape, dtype=bool)
    box[500:900, 330:520] = True
    sel = box & vis
    report["wolfPawBox"] = {
        "count": int(sel.sum()),
        "mean": [round(float(v), 1) for v in rgb[sel].mean(axis=0)] if sel.any() else None,
    }
    # Low-alpha fringe in that box.
    fringe = box & (a > 0) & (a <= 16)
    report["wolfPawFringeA"] = int(fringe.sum())

    brute = pl.load_rgba(pl.OUT_ASSETS / "actors/attackers/attacker-stone-brute.png")
    brgb = brute[:, :, :3].astype(np.int16)
    ba = brute[:, :, 3]
    bvis = ba > 8
    bh = bvis.shape[0]
    # Rows near the feet: count opaque pixels per row and report sparse rows.
    row_counts = bvis.sum(axis=1)
    sparse = []
    for y in range(int(bh * 0.75), bh):
        if 8 < int(row_counts[y]) < 180:
            xs = np.nonzero(bvis[y])[0]
            sample = brgb[y, xs].mean(axis=0)
            sparse.append({"y": y, "n": int(row_counts[y]), "x0": int(xs.min()), "x1": int(xs.max()), "mean": [round(float(v), 1) for v in sample]})
    report["bruteSparseRows"] = sparse[:25]
    report["bruteSparseCount"] = len(sparse)

    lock = pl.load_rgba(pl.OUT_ASSETS / "actors/bodies/class-warlock-standing-body.png")
    wrgb = lock[:, :, :3].astype(np.int16)
    wa = lock[:, :, 3]
    wvis = wa > 16
    wh, ww = wvis.shape
    wr, wg, wb = wrgb[:, :, 0], wrgb[:, :, 1], wrgb[:, :, 2]
    dust = np.zeros(wvis.shape, dtype=bool)
    dust[int(wh * 0.82):, int(ww * 0.45):] = True
    light = dust & wvis & (wr > 90) & (wg > 90) & (wb > 90) & (wr < 230)
    report["warlockDust"] = top(light, wrgb, 6)
    report["warlockDustPixels"] = int(light.sum())
    bright = dust & wvis & (wr > 140) & (wg > 140) & (wb > 140)
    report["warlockDustBright"] = int(bright.sum())
    print(json.dumps(report, indent=2)[:8000])


if __name__ == "__main__":
    main()
