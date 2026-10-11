"""Print non-brown pixels on the rows where the guide line sits."""
from __future__ import annotations

import json

import numpy as np

import process_local as pl


def rows(path, y0, y1, x0, x1):
    rgba = pl.load_rgba(path)
    found = []
    crop = rgba[y0:y1, x0:x1]
    rgb = crop[:, :, :3].astype(np.int16)
    a = crop[:, :, 3]
    for y in range(crop.shape[0]):
        vis = a[y] > 16
        if int(vis.sum()) == 0 or int(vis.sum()) > 80:
            continue
        cols = np.nonzero(vis)[0]
        sample = rgb[y, cols]
        # Skip rows that are mostly brown feet.
        if float(sample[:, 2].mean()) < 45 and float(sample[:, 0].mean()) < 120:
            continue
        found.append({
            "y": y + y0,
            "n": int(vis.sum()),
            "x0": int(cols.min()) + x0,
            "x1": int(cols.max()) + x0,
            "mean": [round(float(v), 1) for v in sample.mean(axis=0)],
        })
    return found


def main():
    print(json.dumps({
        "brute": rows(pl.OUT_ASSETS / "actors/attackers/attacker-stone-brute.png", 760, 860, 250, 700)[:20],
        "wolf": rows(pl.OUT_ASSETS / "actors/creatures/creature-wolf.png", 760, 900, 340, 560)[:20],
    }, indent=2))


if __name__ == "__main__":
    main()
