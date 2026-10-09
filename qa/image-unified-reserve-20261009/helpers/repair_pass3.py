"""Targeted cleanup of remaining foot markers, the drone slab, and the warlock floor."""
from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np

import process_local as pl
import repair_pass2 as p2


def bottom_magenta(rgba):
    rgb = rgba[:, :, :3].astype(np.int16)
    visible = rgba[:, :, 3] > 16
    height = visible.shape[0]
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    band = np.zeros(visible.shape, dtype=bool)
    band[int(height * 0.78):, :] = True
    mask = visible & band & (r > 150) & (b > 120) & (g < 140) & ((r - g) > 30) & ((b - g) > 20)
    out, safe = pl.apply_removal(rgba, mask)
    return out, safe, int(mask.sum())


def drone_slab(rgba):
    rgb = rgba[:, :, :3].astype(np.int16)
    visible = rgba[:, :, 3] > 16
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    mask = visible & (r > 130) & (b > 130) & (g < 80) & (np.abs(r - b) < 80)
    count, labels = cv2.connectedComponents(mask.astype(np.uint8), connectivity=8)
    height = visible.shape[0]
    remove = np.zeros(visible.shape, dtype=bool)
    for label in range(1, count):
        component = labels == label
        area = int(component.sum())
        ys = np.nonzero(component)[0]
        if area < 800:
            continue
        if float(ys.mean()) < height * 0.55:
            continue
        remove |= component
    out, safe = pl.apply_removal(rgba, remove)
    return out, safe, int(remove.sum())


def warlock_floor(rgba):
    rgb = rgba[:, :, :3].astype(np.int16)
    visible = rgba[:, :, 3] > 16
    mn = rgb.min(axis=2)
    mx = rgb.max(axis=2)
    white = visible & (mn > 220) & ((mx - mn) < 22)
    orange = visible & (rgb[:, :, 0] > 190) & (rgb[:, :, 1] > 90) & (rgb[:, :, 2] < 100)
    protect = cv2.dilate(orange.astype(np.uint8), np.ones((11, 11), np.uint8)).astype(bool)
    white &= ~protect
    remove = pl.boundary_labels(white)
    out, safe = pl.apply_removal(rgba, remove)
    return out, safe, int(remove.sum())


def green_loose(rgba):
    rgb = rgba[:, :, :3].astype(np.int16)
    visible = rgba[:, :, 3] > 16
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    green = visible & (g > r + 4) & (g > b) & (g > 45)
    count, labels = cv2.connectedComponents(green.astype(np.uint8), connectivity=8)
    height = visible.shape[0]
    remove = np.zeros(visible.shape, dtype=bool)
    for label in range(1, count):
        component = labels == label
        area = int(component.sum())
        ys = np.nonzero(component)[0]
        if area < 1500:
            continue
        if int(ys.min()) < height * 0.5:
            continue
        if float(ys.mean()) < height * 0.7:
            continue
        remove |= component
    out, safe = pl.apply_removal(rgba, remove)
    return out, safe, int(remove.sum())


def write_and_preview(rgba, dest: Path, preview: str):
    pl.save_png(dest, rgba)
    p2.flatten(dest, preview)
    return pl.file_ref(dest, {"width": int(rgba.shape[1]), "height": int(rgba.shape[0])})


def main():
    notes = []
    # Foot markers on every attacker and creature output, falling back to the residual source.
    for folder in ("attackers", "creatures"):
        for src in sorted((pl.RES_ACTORS / folder).glob("*.png")):
            dest = pl.OUT_ASSETS / "actors" / folder / f"{src.stem}.png"
            current = pl.load_rgba(dest if dest.exists() else src)
            out, safe, count = bottom_magenta(current)
            if src.stem == "creature-drone" and safe and out is not None:
                out2, safe2, count2 = drone_slab(out)
                if safe2 and out2 is not None:
                    out, safe, count = out2, safe2, count + count2
            if safe and out is not None and count:
                ref = write_and_preview(out, dest, f"{src.stem}-pass3.jpg") if src.stem in {
                    "attacker-stone-brute", "creature-wolf", "creature-drone",
                } else None
                if ref is None:
                    pl.save_png(dest, out)
                    ref = pl.file_ref(dest, {"width": int(out.shape[1]), "height": int(out.shape[0])})
                notes.append({"id": src.stem, "removed": count, "output": ref})
    for asset_id in ("workshop-iron", "hall-industrial"):
        src = pl.GREEN_BASES[asset_id]
        dest = pl.OUT_ASSETS / "environment/buildings" / f"{asset_id}.png"
        current = pl.load_rgba(dest if dest.exists() else src)
        out, safe, count = green_loose(current)
        if safe and out is not None and count:
            notes.append({"id": asset_id, "removed": count, "output": write_and_preview(out, dest, f"{asset_id}-pass3.jpg")})
        else:
            notes.append({"id": asset_id, "removed": count, "written": False})
    warlock = pl.OUT_ASSETS / "actors/bodies/class-warlock-standing-body.png"
    rgba = pl.load_rgba(warlock)
    out, safe, count = warlock_floor(rgba)
    if safe and out is not None and count:
        notes.append({"id": "class-warlock-standing-body", "removed": count, "output": write_and_preview(out, warlock, "class-warlock-standing-body-pass3.jpg")})
    (pl.QA / "diagnostics/pass3.json").write_text(json.dumps(notes, indent=2), encoding="utf-8")
    print(json.dumps(notes, indent=2)[:4000])


if __name__ == "__main__":
    main()
