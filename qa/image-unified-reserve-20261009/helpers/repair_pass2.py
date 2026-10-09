"""Second local pass for defects the first color gate missed.

Removes isolated or lower-band magenta markers without a global hue flood,
and removes lower green base components even when a building breaks their convexity.
Studio bodies whose backdrop is light gray are rematted from the native using
distance to the border color, not a walking threshold.
"""
from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

import process_local as pl

ROOT = pl.ROOT


def save(path: Path, rgba: np.ndarray) -> None:
    pl.save_png(path, rgba)


def magenta_components(rgb: np.ndarray, visible: np.ndarray):
    r = rgb[:, :, 0].astype(np.int16)
    g = rgb[:, :, 1].astype(np.int16)
    b = rgb[:, :, 2].astype(np.int16)
    mask = visible & (r > 175) & (b > 145) & (g < 130) & ((r - g) > 35) & ((b - g) > 25) & (np.abs(r - b) < 120)
    count, labels = cv2.connectedComponents(mask.astype(np.uint8), connectivity=8)
    return labels, count, mask


def remove_magenta_markers(rgba: np.ndarray):
    rgb = rgba[:, :, :3]
    visible = rgba[:, :, 3] > 16
    labels, count, mask = magenta_components(rgb, visible)
    subject = visible & ~mask
    remove = np.zeros(visible.shape, dtype=bool)
    height = visible.shape[0]
    for label in range(1, count):
        component = labels == label
        area = int(component.sum())
        if area < 12:
            continue
        ys, xs = np.nonzero(component)
        top, bottom = int(ys.min()), int(ys.max())
        touches_subject = bool(np.any(subject & cv2.dilate(component.astype(np.uint8), np.ones((3, 3), np.uint8), iterations=1)))
        lower = (ys.mean() > height * 0.72) or (top > height * 0.62)
        isolated = not touches_subject
        if isolated or (lower and area < 20000 and (bottom - top) < height * 0.28):
            remove |= component
    # Peel only a strict magenta fringe that already touches transparency. Stop after 3 pixels.
    fringe_source = rgba.copy()
    for _ in range(3):
        alpha = fringe_source[:, :, 3] > 16
        strict = magenta_components(fringe_source[:, :, :3], alpha)[2]
        transparent = ~alpha
        touch = np.zeros(alpha.shape, dtype=bool)
        touch[1:] |= transparent[:-1]
        touch[:-1] |= transparent[1:]
        touch[:, 1:] |= transparent[:, :-1]
        touch[:, :-1] |= transparent[:, 1:]
        peel = strict & touch & alpha
        if not peel.any():
            break
        remove |= peel
        fringe_source[peel, 3] = 0
    out, safe = pl.apply_removal(rgba, remove)
    return out, safe, int(remove.sum())


def remove_green_bases(rgba: np.ndarray):
    rgb = rgba[:, :, :3].astype(np.int16)
    visible = rgba[:, :, 3] > 16
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    green = visible & (g > r + 8) & (g > b + 4) & (g > 55) & (g > 70)
    count, labels = cv2.connectedComponents(green.astype(np.uint8), connectivity=8)
    height = visible.shape[0]
    remove = np.zeros(visible.shape, dtype=bool)
    for label in range(1, count):
        component = labels == label
        area = int(component.sum())
        if area < 1200:
            continue
        ys = np.nonzero(component)[0]
        top = int(ys.min())
        if top < height * 0.45:
            continue
        if float(ys.mean()) < height * 0.62:
            continue
        remove |= component
    out, safe = pl.apply_removal(rgba, remove)
    return out, safe, int(remove.sum())


def rematte_body(native: np.ndarray):
    rgb = native[:, :, :3].astype(np.int16)
    visible = native[:, :, 3] > 16
    border = np.concatenate([
        rgb[0, :, :], rgb[-1, :, :], rgb[:, 0, :], rgb[:, -1, :],
    ])
    median = np.median(border, axis=0)
    chroma = int(median.max() - median.min())
    if median.min() < 200 or chroma > 18:
        return pl.matte_white(native)
    dist = np.max(np.abs(rgb - median.reshape(1, 1, 3)), axis=2)
    pixel_chroma = rgb.max(axis=2) - rgb.min(axis=2)
    mask = visible & (dist <= 12) & (pixel_chroma <= 16)
    # Protect the staff glow: near-white pixels touching saturated orange stay.
    orange = visible & (rgb[:, :, 0] > 190) & (rgb[:, :, 1] > 90) & (rgb[:, :, 2] < 90)
    orange_touch = cv2.dilate(orange.astype(np.uint8), np.ones((9, 9), np.uint8), iterations=1).astype(bool)
    mask &= ~orange_touch
    remove = pl.boundary_labels(mask)
    out, safe = pl.apply_removal(native, remove)
    opaque = int((out[:, :, 3] > 16).sum()) if out is not None else 0
    return {"image": out if safe else None, "safe": safe and opaque > native.shape[0] * native.shape[1] * 0.02, "removed": int(remove.sum()), "opaque": opaque}


def flatten(path: Path, name: str):
    image = Image.open(path).convert("RGBA")
    image.thumbnail((700, 700))
    board = Image.new("RGBA", image.size, (0, 0, 0, 255))
    board.alpha_composite(image)
    dest = pl.QA / "review" / name
    board.convert("RGB").save(dest, quality=85)


def main():
    notes = []
    # Bodies that still show a light backdrop.
    for asset_id in ("class-warlock-standing-body", "class-ranger-standing-body", "class-mage-standing-body"):
        native = pl.load_rgba(pl.NATIVE_SRC / f"{asset_id}.png")
        matted = rematte_body(native)
        record = {"id": asset_id, "safe": matted["safe"], "removed": matted.get("removed"), "opaque": matted.get("opaque")}
        if matted["safe"] and matted["image"] is not None:
            out = pl.OUT_ASSETS / "actors/bodies" / f"{asset_id}.png"
            save(out, matted["image"])
            record["output"] = pl.file_ref(out, {"width": native.shape[1], "height": native.shape[0]})
            flatten(out, f"{asset_id}-pass2.jpg")
        notes.append(record)
    targets = []
    for folder in ("attackers", "creatures"):
        for path in sorted((pl.RES_ACTORS / folder).glob("*.png")):
            targets.append((path.stem, path, pl.OUT_ASSETS / "actors" / folder / f"{path.stem}.png"))
    for asset_id, path in pl.GREEN_BASES.items():
        targets.append((asset_id, path, pl.OUT_ASSETS / "environment/buildings" / f"{asset_id}.png"))
    plate_notes = []
    for asset_id, src, dest in targets:
        rgba = pl.load_rgba(src)
        working = rgba
        mag_out, mag_safe, mag_n = remove_magenta_markers(working)
        if mag_safe and mag_out is not None and mag_n:
            working = mag_out
        green_out, green_safe, green_n = remove_green_bases(working)
        if green_safe and green_out is not None and green_n:
            working = green_out
        changed = mag_n + green_n
        if changed and working is not None:
            save(dest, working)
            plate_notes.append({
                "id": asset_id,
                "removedMagentaMarkers": mag_n,
                "removedGreen": green_n,
                "safe": True,
                "output": pl.file_ref(dest, {"width": rgba.shape[1], "height": rgba.shape[0]}),
            })
        else:
            plate_notes.append({"id": asset_id, "removedMagentaMarkers": mag_n, "removedGreen": green_n, "written": False})
    explicit = {
        "attacker-stone-brute": pl.OUT_ASSETS / "actors/attackers/attacker-stone-brute.png",
        "creature-wolf": pl.OUT_ASSETS / "actors/creatures/creature-wolf.png",
        "creature-drone": pl.OUT_ASSETS / "actors/creatures/creature-drone.png",
        "armory-stone": pl.OUT_ASSETS / "environment/buildings/armory-stone.png",
        "farm-bronze": pl.OUT_ASSETS / "environment/buildings/farm-bronze.png",
        "adventure-site-town": pl.OUT_ASSETS / "environment/buildings/adventure-site-town.png",
    }
    for name, path in explicit.items():
        if path.exists():
            flatten(path, f"{name}-pass2.jpg")
    (pl.QA / "diagnostics/pass2.json").write_text(json.dumps({"bodies": notes, "plates": plate_notes}, indent=2), encoding="utf-8")
    print(json.dumps({
        "bodies": notes,
        "platesWritten": sum(1 for row in plate_notes if row.get("output")),
        "greenRemoved": [row for row in plate_notes if row.get("removedGreen")],
    }, indent=2))


if __name__ == "__main__":
    main()
