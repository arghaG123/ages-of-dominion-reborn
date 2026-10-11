"""Dump remaining defect components after pass5. Read-only."""
from __future__ import annotations

import json

import cv2
import numpy as np

import process_local as pl


def comps(mask, rgb, limit=12):
    count, labels = cv2.connectedComponents(mask.astype(np.uint8), connectivity=8)
    rows = []
    for label in range(1, count):
        component = labels == label
        area = int(component.sum())
        ys, xs = np.nonzero(component)
        sample = rgb[component].mean(axis=0)
        rows.append({
            "area": area,
            "bbox": [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1],
            "mean": [round(float(v), 1) for v in sample],
            "cy": round(float(ys.mean()), 1),
        })
    rows.sort(key=lambda row: -row["area"])
    return {"components": len(rows), "pixels": int(mask.sum()), "top": rows[:limit]}


def main():
    report = {}
    wolf = pl.load_rgba(pl.OUT_ASSETS / "actors/creatures/creature-wolf.png")
    rgb = wolf[:, :, :3].astype(np.int16)
    vis = wolf[:, :, 3] > 16
    h = vis.shape[0]
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    band = np.zeros(vis.shape, dtype=bool)
    band[int(h * 0.45):, :] = True
    pure = vis & band & (r > 110) & (b > 90) & (g < 50) & (np.abs(r - b) < 90)
    report["wolfPure"] = comps(pure, rgb)
    mid = vis & band & (r > 120) & (b > 80) & (g < 100) & ((r - g) > 30)
    report["wolfMid"] = comps(mid, rgb)

    shop = pl.load_rgba(pl.OUT_ASSETS / "environment/buildings/workshop-iron.png")
    srgb = shop[:, :, :3].astype(np.int16)
    svis = shop[:, :, 3] > 16
    sr, sg, sb = srgb[:, :, 0], srgb[:, :, 1], srgb[:, :, 2]
    green = svis & (sg > sr + 4) & (sg > sb) & (sg > 70)
    report["workshopGreen"] = comps(green, srgb, 16)

    brute = pl.load_rgba(pl.OUT_ASSETS / "actors/attackers/attacker-stone-brute.png")
    brgb = brute[:, :, :3].astype(np.int16)
    bvis = brute[:, :, 3] > 16
    br, bg, bb = brgb[:, :, 0], brgb[:, :, 1], brgb[:, :, 2]
    pink = bvis & (br > 140) & (bb > 90) & (bg < 140) & ((br - bg) > 25)
    report["brutePink"] = comps(pink, brgb)
    bh = bvis.shape[0]
    bottom = np.zeros(bvis.shape, dtype=bool)
    bottom[int(bh * 0.82):, :] = True
    edge = bvis & bottom
    report["bruteBottomMean"] = [round(float(v), 1) for v in brgb[edge].mean(axis=0)] if edge.any() else None
    report["bruteBottomCount"] = int(edge.sum())

    drone = pl.load_rgba(pl.OUT_ASSETS / "actors/creatures/creature-drone.png")
    drgb = drone[:, :, :3].astype(np.int16)
    dvis = drone[:, :, 3] > 16
    dr, dg, db = drgb[:, :, 0], drgb[:, :, 1], drgb[:, :, 2]
    purple = dvis & (dr > 90) & (db > 90) & (dg < 50) & (np.abs(dr - db) < 90)
    report["dronePurple"] = comps(purple, drgb, 20)

    hall = pl.load_rgba(pl.OUT_ASSETS / "environment/buildings/hall-industrial.png")
    hrgb = hall[:, :, :3].astype(np.int16)
    hvis = hall[:, :, 3] > 16
    hr, hg, hb = hrgb[:, :, 0], hrgb[:, :, 1], hrgb[:, :, 2]
    hh = hvis.shape[0]
    hband = np.zeros(hvis.shape, dtype=bool)
    hband[int(hh * 0.8):, :] = True
    hgreen = hvis & hband & (hg > hr) & (hg > hb) & (hg > 30)
    report["hallLowerGreen"] = comps(hgreen, hrgb)

    warlock = pl.load_rgba(pl.OUT_ASSETS / "actors/bodies/class-warlock-standing-body.png")
    wrgb = warlock[:, :, :3].astype(np.int16)
    wvis = warlock[:, :, 3] > 16
    wr, wg, wb = wrgb[:, :, 0], wrgb[:, :, 1], wrgb[:, :, 2]
    white = wvis & (wr > 210) & (wg > 210) & (wb > 200)
    report["warlockWhite"] = comps(white, wrgb, 8)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
