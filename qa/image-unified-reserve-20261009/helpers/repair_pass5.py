"""Remove the remaining wolf pads, drone slab, brute magenta specks, and workshop lawn."""
from __future__ import annotations

import json

import cv2
import numpy as np

import process_local as pl
import repair_pass2 as p2


def remove_mask(rgba, mask):
    out, safe = pl.apply_removal(rgba, mask)
    if not safe or out is None:
        raise RuntimeError("protected pixels would change")
    return out, int(mask.sum())


def wolf_pads(rgba):
    rgb = rgba[:, :, :3].astype(np.int16)
    visible = rgba[:, :, 3] > 16
    height = visible.shape[0]
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    band = np.zeros(visible.shape, dtype=bool)
    band[int(height * 0.5):, :] = True
    pink = visible & band & (r > 130) & (b > 100) & (g < 160) & ((r + b) > g * 2)
    count, labels = cv2.connectedComponents(pink.astype(np.uint8), connectivity=8)
    remove = np.zeros(visible.shape, dtype=bool)
    for label in range(1, count):
        component = labels == label
        area = int(component.sum())
        if area < 80:
            continue
        ys = np.nonzero(component)[0]
        if (int(ys.max()) - int(ys.min())) > height * 0.16:
            continue
        if float(rgb[:, :, 1][component].mean()) > 40:
            continue
        remove |= component
    return remove_mask(rgba, remove)


def drone_slab(rgba):
    rgb = rgba[:, :, :3].astype(np.int16)
    visible = rgba[:, :, 3] > 16
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    purple = visible & (r > 100) & (b > 100) & (g < 40) & (np.abs(r - b) < 80)
    count, labels = cv2.connectedComponents(purple.astype(np.uint8), connectivity=8)
    height = visible.shape[0]
    remove = np.zeros(visible.shape, dtype=bool)
    for label in range(1, count):
        component = labels == label
        area = int(component.sum())
        ys = np.nonzero(component)[0]
        if area < 800:
            continue
        if float(ys.mean()) < height * 0.7:
            continue
        remove |= component
    return remove_mask(rgba, remove)


def brute_specks(rgba):
    rgb = rgba[:, :, :3].astype(np.int16)
    visible = rgba[:, :, 3] > 16
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    pink = visible & (r > 160) & (b > 120) & (g < 120) & ((r - g) > 40)
    count, labels = cv2.connectedComponents(pink.astype(np.uint8), connectivity=8)
    remove = np.zeros(visible.shape, dtype=bool)
    for label in range(1, count):
        component = labels == label
        if int(component.sum()) < 20:
            remove |= component
    return remove_mask(rgba, remove)


def workshop_lawn(rgba):
    rgb = rgba[:, :, :3].astype(np.int16)
    visible = rgba[:, :, 3] > 16
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    green = visible & (g > r + 6) & (g > b) & (g > 80)
    count, labels = cv2.connectedComponents(green.astype(np.uint8), connectivity=8)
    remove = np.zeros(visible.shape, dtype=bool)
    for label in range(1, count):
        component = labels == label
        area = int(component.sum())
        if area < 2000:
            continue
        if float(g[component].mean()) > 130:
            continue
        remove |= component
    return remove_mask(rgba, remove)


def hall_wedge(rgba):
    rgb = rgba[:, :, :3].astype(np.int16)
    visible = rgba[:, :, 3] > 16
    height = visible.shape[0]
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    band = np.zeros(visible.shape, dtype=bool)
    band[int(height * 0.85):, :] = True
    green = visible & band & (g > r + 4) & (g > b) & (g > 40)
    return remove_mask(rgba, green)


def main():
    notes = []
    jobs = [
        ("creature-wolf", pl.OUT_ASSETS / "actors/creatures/creature-wolf.png", wolf_pads, "creature-wolf-pass5.jpg"),
        ("creature-drone", pl.OUT_ASSETS / "actors/creatures/creature-drone.png", drone_slab, "creature-drone-pass5.jpg"),
        ("attacker-stone-brute", pl.OUT_ASSETS / "actors/attackers/attacker-stone-brute.png", brute_specks, "attacker-stone-brute-pass5.jpg"),
        ("workshop-iron", pl.OUT_ASSETS / "environment/buildings/workshop-iron.png", workshop_lawn, "workshop-iron-pass5.jpg"),
        ("hall-industrial", pl.OUT_ASSETS / "environment/buildings/hall-industrial.png", hall_wedge, "hall-industrial-pass5.jpg"),
    ]
    for asset_id, path, fn, preview in jobs:
        rgba = pl.load_rgba(path)
        out, count = fn(rgba)
        pl.save_png(path, out)
        p2.flatten(path, preview)
        note = {"id": asset_id, "removed": count, "output": pl.file_ref(path, {"width": int(out.shape[1]), "height": int(out.shape[0])})}
        if asset_id == "creature-drone":
            note["frames"] = pl.split_frames(out, asset_id)
        notes.append(note)
    (pl.QA / "diagnostics/pass5.json").write_text(json.dumps(notes, indent=2), encoding="utf-8")
    print(json.dumps([{k: row[k] for k in ("id", "removed")} | {"frames": len(row.get("frames") or [])} for row in notes], indent=2))


if __name__ == "__main__":
    main()
