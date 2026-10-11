"""One stroke trace inside the measured foot and workshop boxes.

Removes long thin components that sit away from the opened subject, plus short
horizontal fragments of the same ground line. Does not run a magenta key, a
green flood, or a second matte pass.
"""
from __future__ import annotations

import json

import cv2
import numpy as np
from PIL import Image

import process_local as pl
import repair_pass2 as p2


def trace_mask(crop: np.ndarray) -> np.ndarray:
    visible = crop[:, :, 3] > 16
    rgb = crop[:, :, :3].astype(np.int16)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    opened = cv2.morphologyEx(visible.astype(np.uint8), cv2.MORPH_OPEN, kernel).astype(bool)
    thin = visible & ~opened
    distance = cv2.distanceTransform((~opened).astype(np.uint8), cv2.DIST_L2, 3)
    far = thin & (distance >= 3)
    count, labels = cv2.connectedComponents(far.astype(np.uint8), connectivity=8)
    keep = np.zeros(visible.shape, dtype=bool)
    for label in range(1, count):
        component = labels == label
        area = int(component.sum())
        ys, xs = np.nonzero(component)
        height = int(ys.max() - ys.min() + 1)
        width = int(xs.max() - xs.min() + 1)
        mean = rgb[component].mean(axis=0)
        long_line = area >= 25 and max(height, width) >= 30 and not (area > 0.4 * height * width and min(height, width) > 8)
        flat_fragment = (
            area >= 8
            and width >= 12
            and height <= 6
            and float(mean[0]) > 85
            and float(mean[1]) < 130
            and float(mean[0]) > float(mean[1])
        )
        if long_line or flat_fragment:
            keep |= component
    return keep


def wolf_dot(crop: np.ndarray, origin) -> np.ndarray:
    x0, y0 = origin
    rgb = crop[:, :, :3].astype(np.int16)
    visible = crop[:, :, 3] > 16
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    opened = cv2.morphologyEx(visible.astype(np.uint8), cv2.MORPH_OPEN, kernel).astype(bool)
    local = np.zeros(visible.shape, dtype=bool)
    local[max(0, 775 - y0) : max(0, 810 - y0), max(0, 455 - x0) : max(0, 490 - x0)] = True
    red = (
        visible
        & local
        & ~opened
        & (rgb[:, :, 0] > 50)
        & (rgb[:, :, 0] > rgb[:, :, 1] + 20)
        & (rgb[:, :, 1] < 80)
        & (rgb[:, :, 2] < rgb[:, :, 0])
    )
    count, labels = cv2.connectedComponents(red.astype(np.uint8), connectivity=8)
    dot = np.zeros(visible.shape, dtype=bool)
    for label in range(1, count):
        component = labels == label
        area = int(component.sum())
        if 3 <= area <= 80:
            dot |= component
    return dot


def apply_box(rgba: np.ndarray, box, cap: int, with_dot: bool):
    height, width = rgba.shape[:2]
    x0, y0, x1, y1 = box
    x1, y1 = min(x1, width), min(y1, height)
    crop = rgba[y0:y1, x0:x1]
    mask = trace_mask(crop)
    dot_count = 0
    if with_dot:
        dot = wolf_dot(crop, (x0, y0))
        dot_count = int(dot.sum())
        mask |= dot
    full = np.zeros(rgba.shape[:2], dtype=bool)
    full[y0:y1, x0:x1] = mask
    count = int(full.sum())
    if count == 0 or count > cap:
        return rgba, count, True, dot_count
    out, safe = pl.apply_removal(rgba, full)
    if not safe or out is None:
        raise RuntimeError("protected pixels would change")
    return out, count, False, dot_count


def workshop_outline(rgba: np.ndarray, cap: int):
    rgb = rgba[:, :, :3].astype(np.int16)
    visible = rgba[:, :, 3] > 16
    distance = cv2.distanceTransform(visible.astype(np.uint8), cv2.DIST_L2, 5)
    core = distance >= 4
    away = cv2.distanceTransform((~core).astype(np.uint8), cv2.DIST_L2, 5)
    far = visible & (distance <= 2.2) & (away >= 8)
    count, labels = cv2.connectedComponents(far.astype(np.uint8), connectivity=8)
    stroke = np.zeros(visible.shape, dtype=bool)
    parts = []
    for label in range(1, count):
        component = labels == label
        area = int(component.sum())
        if area < 40 or area > 2200:
            continue
        mean = rgb[component].mean(axis=0)
        if float(mean.mean()) < 115:
            continue
        ys, xs = np.nonzero(component)
        height = int(ys.max() - ys.min() + 1)
        width = int(xs.max() - xs.min() + 1)
        if area > 0.15 * height * width:
            continue
        stroke |= component
        parts.append({
            "area": area,
            "bbox": [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1],
            "mean": [round(float(v), 1) for v in mean],
        })
    total = int(stroke.sum())
    if total == 0 or total > cap:
        return rgba, total, True, parts
    out, safe = pl.apply_removal(rgba, stroke)
    if not safe or out is None:
        raise RuntimeError("protected pixels would change")
    return out, total, False, parts


def remaining(rgba: np.ndarray, box) -> list:
    height, width = rgba.shape[:2]
    x0, y0, x1, y1 = box
    x1, y1 = min(x1, width), min(y1, height)
    crop = rgba[y0:y1, x0:x1]
    visible = crop[:, :, 3] > 16
    rgb = crop[:, :, :3].astype(np.int16)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    opened = cv2.morphologyEx(visible.astype(np.uint8), cv2.MORPH_OPEN, kernel).astype(bool)
    thin = visible & ~opened
    distance = cv2.distanceTransform((~opened).astype(np.uint8), cv2.DIST_L2, 3)
    far = thin & (distance >= 2)
    count, labels = cv2.connectedComponents(far.astype(np.uint8), connectivity=8)
    rows = []
    for label in range(1, count):
        component = labels == label
        area = int(component.sum())
        if area < 8:
            continue
        ys, xs = np.nonzero(component)
        rows.append({
            "pixels": area,
            "bbox": [int(xs.min()) + x0, int(ys.min()) + y0, int(xs.max()) + 1 + x0, int(ys.max()) + 1 + y0],
            "mean": [round(float(v), 1) for v in rgb[component].mean(axis=0)],
        })
    rows.sort(key=lambda row: -row["pixels"])
    return rows


def flatten_box(path, box, name: str):
    image = Image.open(path).convert("RGBA")
    crop = image.crop(box)
    board = Image.new("RGBA", crop.size, (0, 0, 0, 255))
    board.alpha_composite(crop)
    board.convert("RGB").save(pl.QA / "review" / name, quality=90)


def main():
    notes = []
    wolf_path = pl.OUT_ASSETS / "actors/creatures/creature-wolf.png"
    wolf_box = (340, 700, 580, 900)
    wolf, wolf_n, wolf_skip, dot_n = apply_box(pl.load_rgba(wolf_path), wolf_box, 500, True)
    if not wolf_skip:
        pl.save_png(wolf_path, wolf)
        p2.flatten(wolf_path, "creature-wolf-pass11.jpg")
        flatten_box(wolf_path, wolf_box, "creature-wolf-spot.jpg")
    wolf_left = remaining(pl.load_rgba(wolf_path), wolf_box)
    notes.append({
        "id": "creature-wolf",
        "removed": wolf_n,
        "dot": dot_n,
        "skipped": wolf_skip,
        "box": list(wolf_box),
        "remainingFarThinComponents": wolf_left,
        "remainingPixels": int(sum(row["pixels"] for row in wolf_left)),
    })

    brute_path = pl.OUT_ASSETS / "actors/attackers/attacker-stone-brute.png"
    brute_box = (280, 640, 680, 807)
    brute, brute_n, brute_skip, _ = apply_box(pl.load_rgba(brute_path), brute_box, 600, False)
    if not brute_skip:
        pl.save_png(brute_path, brute)
        p2.flatten(brute_path, "attacker-stone-brute-pass11.jpg")
        flatten_box(brute_path, (250, 620, 700, 807), "brute-feet-spot.jpg")
    brute_left = remaining(pl.load_rgba(brute_path), brute_box)
    notes.append({
        "id": "attacker-stone-brute",
        "removed": brute_n,
        "skipped": brute_skip,
        "box": list(brute_box),
        "remainingFarThinComponents": brute_left,
        "remainingPixels": int(sum(row["pixels"] for row in brute_left)),
    })

    shop_path = pl.OUT_ASSETS / "environment/buildings/workshop-iron.png"
    shop, shop_n, shop_skip, parts = workshop_outline(pl.load_rgba(shop_path), 3000)
    if not shop_skip:
        pl.save_png(shop_path, shop)
        p2.flatten(shop_path, "workshop-iron-pass11.jpg")
    shop_left = []
    if not shop_skip:
        rgb = shop[:, :, :3].astype(np.int16)
        visible = shop[:, :, 3] > 16
        white = visible & (rgb.min(axis=2) > 140) & (np.abs(rgb[:, :, 0] - rgb[:, :, 1]) < 30)
        distance = cv2.distanceTransform(visible.astype(np.uint8), cv2.DIST_L2, 5)
        core = distance >= 4
        away = cv2.distanceTransform((~core).astype(np.uint8), cv2.DIST_L2, 5)
        left = white & (distance <= 2.2) & (away >= 8)
        count, labels = cv2.connectedComponents(left.astype(np.uint8), connectivity=8)
        for label in range(1, count):
            component = labels == label
            area = int(component.sum())
            if area < 15:
                continue
            ys, xs = np.nonzero(component)
            shop_left.append({
                "pixels": area,
                "bbox": [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1],
                "mean": [round(float(v), 1) for v in rgb[component].mean(axis=0)],
            })
    notes.append({
        "id": "workshop-iron",
        "removed": shop_n,
        "skipped": shop_skip,
        "parts": parts,
        "remainingBrightFarComponents": shop_left,
        "remainingPixels": int(sum(row["pixels"] for row in shop_left)),
    })
    (pl.QA / "diagnostics/pass11.json").write_text(json.dumps(notes, indent=2), encoding="utf-8")
    print(json.dumps(notes, indent=2))


if __name__ == "__main__":
    main()
