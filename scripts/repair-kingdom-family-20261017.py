"""Rebuild Kingdom grounds from the sharp production paintings and draw wall phases on that ground.

The previous derivatives filled every empty plot with a wide blur. This keeps the source grain,
removes only the baked plot frame, and draws scaffold / built / taller walls along the registered
perimeter instead of stamping a screen-aligned fence.
"""
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = json.loads((ROOT / "src/data/implementation-contract.json").read_text(encoding="utf-8"))
GEO = CONTRACT["geometry"]["kingdom"]
A, B, C, D, E, F = GEO["worldToSource"]
OUT = ROOT / "assets/derivatives/mock-led-20261016/kingdom"
PROD = ROOT / "assets/production/production-01-20261003/images"
AGES = ["stone", "bronze", "iron", "medieval", "gunpowder", "industrial", "modern", "future"]
SOURCES = {age: PROD / f"{index:02d}-kingdom-terrain-{age}.png" for index, age in enumerate(AGES, 1)}

# BGR body, highlight. Era material only; the perimeter is shared.
# OpenCV BGR. Stone reads as timber. Future reads cooler than that timber.
MATERIAL = {
    "stone": ((42, 72, 128), (70, 110, 176)),
    "bronze": ((48, 78, 112), (78, 118, 158)),
    "iron": ((70, 74, 82), (110, 114, 124)),
    "medieval": ((88, 90, 96), (140, 142, 150)),
    "gunpowder": ((54, 58, 96), (80, 88, 142)),
    "industrial": ((52, 54, 58), (90, 92, 98)),
    "modern": ((108, 110, 114), (160, 162, 168)),
    "future": ((214, 168, 96), (236, 196, 120)),
}


def logical_to_source(x, y):
    return np.array([A * x + C * y + E, B * x + D * y + F], dtype=np.float32)


def site_polygon(rect, pad=0.0):
    x, y, w, h = rect
    x -= pad
    y -= pad
    w += pad * 2
    h += pad * 2
    return np.array([
        logical_to_source(x, y + h),
        logical_to_source(x + w, y + h),
        logical_to_source(x + w, y),
        logical_to_source(x, y),
    ], dtype=np.int32)


def plot_masks(shape):
    fill = np.zeros(shape, np.uint8)
    for site in GEO["sites"]:
        if site["id"] == "townhall":
            continue
        cv2.fillPoly(fill, [site_polygon(site["rect"])], 255)
    inner = cv2.erode(fill, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
    # The painted rope sits outside the logical rectangle.
    outer = cv2.dilate(fill, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31)))
    border = cv2.subtract(outer, inner)
    return inner, border


def repair_ground(src):
    """Lift only the painted plot rope. The rest of the production painting stays untouched."""
    height, width = src.shape[:2]
    fill = np.zeros((height, width), np.uint8)
    for site in GEO["sites"]:
        if site["id"] == "townhall":
            continue
        cv2.fillPoly(fill, [site_polygon(site["rect"])], 255)
    zone = cv2.dilate(fill, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (21, 21)))
    zone = cv2.subtract(zone, cv2.erode(fill, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))))
    edges = cv2.Canny(cv2.cvtColor(src, cv2.COLOR_BGR2GRAY), 30, 90)
    rope = cv2.dilate(cv2.bitwise_and(edges, zone), np.ones((3, 3), np.uint8))
    return cv2.inpaint(src, rope, 3, cv2.INPAINT_NS)


def clearing_loop():
    """Pixel loop around the plot clearing, just outside the pads and inside the huts."""
    mask = np.zeros((768, 1376), np.uint8)
    for site in GEO["sites"]:
        cv2.fillPoly(mask, [site_polygon(site["rect"])], 255)
    mask = cv2.dilate(mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (56, 56)))
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contour = max(contours, key=cv2.contourArea)
    smooth = cv2.approxPolyDP(contour, 12, True).reshape(-1, 2).astype(np.float32)
    return np.vstack([smooth, smooth[:1]])


def stake_color(age, along, height_t):
    body, lite = MATERIAL[age]
    mix = 0.35 + 0.65 * height_t
    shade = 0.82 + 0.18 * ((along * 5) % 1)
    color = tuple(int(min(255, (body[i] * (1 - mix) + lite[i] * mix) * shade)) for i in range(3))
    return color


# These production paintings already contain their fortification and gate.
# A second procedural fence fights that city.
# Gunpowder, Industrial, and Future already contain their boundary.
# On Bronze, Iron, Medieval, and Modern the contour fence lands on the pads.
# Stone's plots form one clearing, so the palisade stays there.
PAINTED_BOUNDARY = {"gunpowder", "industrial", "future"}
PAD_FENCE = {"bronze", "iron", "medieval", "modern"}
ALREADY_WALLED = PAINTED_BOUNDARY | PAD_FENCE


def draw_wall(base, age, phase):
    if age in ALREADY_WALLED:
        return base.copy()
    canvas = base.copy()
    loop = clearing_loop()
    gap_center = logical_to_source(7.7, 9.35)
    spacing = 30 if phase == "scaffold" else 18
    posts = []
    carried = 0.0
    for index in range(len(loop) - 1):
        start = loop[index]
        end = loop[index + 1]
        length = float(np.hypot(*(end - start)))
        if length < 1:
            continue
        direction = (end - start) / length
        distance = carried
        while distance < length:
            ground = start + direction * distance
            if float(np.hypot(*(ground - gap_center))) > 36:
                posts.append((ground, direction))
            distance += spacing
        carried = distance - length
    posts.sort(key=lambda item: float(item[0][1]))
    centroid = loop[:-1].mean(axis=0)
    overlay = canvas.copy()
    placed = []
    for index, (ground, direction) in enumerate(posts):
        inward = centroid - ground
        length = float(np.hypot(*(inward)))
        if length > 1:
            ground = ground + inward / length * 46
        y = float(ground[1])
        height = 22 + (y / 768) * 28
        if phase == "tall":
            height *= 1.55
        elif phase == "scaffold":
            height *= 0.62
        foot = (int(round(float(ground[0]))), int(round(y)))
        if not (2 <= foot[0] < canvas.shape[1] - 2 and 2 <= foot[1] < canvas.shape[0] - 2):
            continue
        blocked = 0
        checked = 0
        for dy in range(10, int(height), 6):
            yy = foot[1] - dy
            if yy < 2:
                break
            checked += 1
            blue, green, red = [int(v) for v in canvas[yy, foot[0]]]
            if green > red + 18 or red < 40 or (red > 165 and green > 145 and blue < 130):
                blocked += 1
        if checked and blocked / checked > 0.3:
            height = max(16, height * (1 - blocked / checked))
        patch = canvas[foot[1] - 2:foot[1] + 3, foot[0] - 2:foot[0] + 3].astype(np.int16)
        blue, green, red = patch.mean(axis=(0, 1))
        # Skip feet on foliage or pale thatch so the posts stay on the dirt.
        if green > red + 18 and green > 70:
            continue
        if red > 165 and green > 145 and blue < 130:
            continue
        cv2.ellipse(overlay, (foot[0], foot[1] + 2), (6, 3), 0, 0, 360, (18, 14, 10), -1)
        for offset in range(-4, 5, 2):
            tone = 0.08 if (offset // 2) % 2 else 1.0
            color = stake_color(age, index + offset, tone)
            origin = (int(foot[0] + direction[0] * offset), foot[1])
            cv2.line(overlay, origin, (origin[0], int(origin[1] - height)), color, 2, cv2.LINE_AA)
        placed.append((foot, height))
    if len(placed) > 2:
        placed.sort(key=lambda item: float(np.arctan2(item[0][1] - centroid[1], item[0][0] - centroid[0])))
        rail = stake_color(age, 1, 0.65)
        for index, (foot, height) in enumerate(placed):
            other, other_height = placed[(index + 1) % len(placed)]
            span = float(np.hypot(other[0] - foot[0], other[1] - foot[1]))
            if span > 44:
                continue
            if phase != "scaffold":
                cv2.line(overlay, (foot[0], foot[1] + 3), (other[0], other[1] + 3), (36, 28, 18), 2, cv2.LINE_AA)
            levels = (0.7,) if phase == "scaffold" else (0.4, 0.75)
            for level in levels:
                start = (foot[0], int(foot[1] - height * level))
                end = (other[0], int(other[1] - other_height * level))
                cv2.line(overlay, start, end, rail, 2, cv2.LINE_AA)
        gate = logical_to_source(7.7, 9.35)
        left = min((item for item in placed if item[0][0] < gate[0]), key=lambda item: abs(item[0][0] - gate[0]), default=None)
        right = min((item for item in placed if item[0][0] > gate[0]), key=lambda item: abs(item[0][0] - gate[0]), default=None)
        jamb = stake_color(age, 2, 1)
        for item in (left, right):
            if not item:
                continue
            foot, height = item
            cv2.line(overlay, foot, (foot[0], int(foot[1] - height * 1.2)), jamb, 5, cv2.LINE_AA)
    alpha = 1.0 if phase == "scaffold" else 0.94
    cv2.addWeighted(overlay, alpha, canvas, 1 - alpha, 0, canvas)
    return canvas


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    hashes = {}
    for age in AGES:
        src = cv2.imread(str(SOURCES[age]), cv2.IMREAD_COLOR)
        if src is None or src.shape[1] != 1376 or src.shape[0] != 768:
            raise SystemExit(f"unexpected source {age} {None if src is None else src.shape}")
        ground = repair_ground(src)
        ground_path = OUT / f"kingdom-{age}-ground.png"
        cv2.imwrite(str(ground_path), ground)
        cv2.imwrite(str(OUT / f"kingdom-{age}-scaffold.png"), draw_wall(ground, age, "scaffold"))
        cv2.imwrite(str(OUT / f"kingdom-{age}-wall.png"), draw_wall(ground, age, "built"))
        cv2.imwrite(str(OUT / f"kingdom-{age}-wall-tall.png"), draw_wall(ground, age, "tall"))
        hashes[age] = sha(ground_path)
        print(age, hashes[age])
    catalog_path = ROOT / "src/data/reviewed-source-selection.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    for age, digest in hashes.items():
        entry = catalog["kingdomTerrain"][age]
        entry["displaySHA256"] = digest
        if age in PAINTED_BOUNDARY:
            entry["displayNote"] = "Sharp production ground. The boundary is already in the painting, so scaffold, built, and taller use that same ground. runtimeApproved false."
        elif age in PAD_FENCE:
            entry["displayNote"] = "Sharp production ground. A generated fence landed on the plots, so scaffold, built, and taller use this ground until a wall can sit off the pads. runtimeApproved false."
        else:
            entry["displayNote"] = "Sharp production ground with the thin plot-rope fill. Built and taller phases add a railed palisade on the clearing. Scaffold is spaced posts. runtimeApproved false."
    catalog_path.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")
    print("catalog-updated")


if __name__ == "__main__":
    main()
