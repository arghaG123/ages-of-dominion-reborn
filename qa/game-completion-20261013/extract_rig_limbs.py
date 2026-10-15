"""Cut distinct limb crops from the class rig sheets already on disk.

The production sheets stay in place. A transparent derivative is written
only when torso, head, arm, forearm, thigh, shin, and foot are different
components. Repeated rectangles are not given new names.
"""
import hashlib
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
ATLAS_PATH = ROOT / "src/data/actor-atlas.json"
OUT_DIR = ROOT / "assets/derivatives/rigs/executor-20261013"
PREVIEW = Path(__file__).resolve().parent / "rig-crops"
LIMBS = ["head", "torso", "arm", "forearm", "thigh", "shin", "foot"]
SLOT = {
    "head": (16, 16, 300, 460),
    "torso": (340, 16, 400, 470),
    "weapon": (760, 16, 240, 470),
    "arm": (16, 520, 200, 480),
    "forearm": (230, 540, 180, 460),
    "thigh": (430, 520, 200, 480),
    "shin": (650, 540, 180, 460),
    "foot": (850, 820, 160, 180),
}


def foreground_mask(rgb):
    red = rgb[:, :, 0].astype(np.int16)
    green = rgb[:, :, 1].astype(np.int16)
    blue = rgb[:, :, 2].astype(np.int16)
    magenta = (red > 110) & (blue > 100) & (green < 80) & (red > green + 40) & (blue > green + 30)
    panel = (green > 90) & (green > red + 12) & (green > blue + 8) & (red < 200)
    corners = np.concatenate([
        rgb[2:8, 2:8].reshape(-1, 3),
        rgb[2:8, -8:-2].reshape(-1, 3),
        rgb[-8:-2, 2:8].reshape(-1, 3),
        rgb[-8:-2, -8:-2].reshape(-1, 3),
    ]).astype(np.float32)
    background = np.median(corners, axis=0)
    distance = np.linalg.norm(rgb.astype(np.float32) - background, axis=2)
    mask = ((distance > 42) & ~magenta & ~panel).astype(np.uint8) * 255
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    distance_map = cv2.distanceTransform(mask, cv2.DIST_L2, 5)
    peak = (distance_map > 7) & (distance_map >= cv2.dilate(distance_map, np.ones((13, 13), np.uint8)) - 0.01)
    count, markers = cv2.connectedComponents(peak.astype(np.uint8))
    if count < 3:
        return mask
    marker_map = np.zeros(mask.shape, np.int32)
    marker_map[mask == 0] = 1
    marker_map[markers > 0] = markers[markers > 0] + 1
    flooded = cv2.watershed(cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR), marker_map)
    split = np.zeros_like(mask)
    split[flooded > 1] = 255
    return split


def component_rows(mask):
    count, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, 8)
    found = []
    for index in range(1, count):
        x, y, w, h, area = [int(value) for value in stats[index]]
        if area < 500 or w < 10 or h < 10:
            continue
        found.append({
            "box": [x, y, w, h],
            "area": area,
            "cx": float(centroids[index][0]),
            "cy": float(centroids[index][1]),
        })
    return found


def components(image):
    rgb = np.asarray(image.convert("RGB"))
    height, width = rgb.shape[:2]
    mask = foreground_mask(rgb)
    return rgb, None, component_rows(mask), width, height


def region(parts, test):
    return [part for part in parts if test(part)]


def largest(parts):
    return max(parts, key=lambda part: part["area"]) if parts else None


def take(parts, chosen):
    if chosen is None:
        return None
    parts.remove(chosen)
    return chosen["box"]


def within(part, max_w, max_h, min_h=40):
    _x, _y, w, h = part["box"]
    return w <= max_w and min_h <= h <= max_h


def skin_like(rgb, box):
    x, y, w, h = box
    sample = rgb[y:y + h, x:x + w]
    if sample.size == 0:
        return False
    mean = sample.reshape(-1, 3).mean(axis=0)
    return mean[0] > mean[2] + 12 and mean[0] > 80 and mean[1] > 40


def pick(parts, width, height, rgb):
    pool = list(parts)
    heads = region(pool, lambda part: part["cx"] < width * 0.48 and part["cy"] < height * 0.48 and within(part, 240, 300, 70))
    heads.sort(key=lambda part: (skin_like(rgb, part["box"]), part["area"]), reverse=True)
    head = take(pool, heads[0] if heads else None)
    torsos = region(pool, lambda part: part["cx"] >= width * 0.45 and part["cy"] < height * 0.4 and part["box"][2] >= 140 and part["box"][3] >= 150 and part["box"][2] <= 480)
    torso = take(pool, min(torsos, key=lambda part: part["cy"]) if torsos else None)
    arms = region(pool, lambda part: part["cx"] < width * 0.5 and part["cy"] >= height * 0.48 and part["box"][3] > part["box"][2] * 1.15 and within(part, 180, 420, 90))
    arms.sort(key=lambda part: part["cx"])
    arm = take(pool, arms[0] if arms else None)
    forearms = [part for part in arms[1:] if part in pool]
    forearm = take(pool, forearms[0] if forearms else None)
    leg_pieces = region(pool, lambda part: part["cx"] >= width * 0.5 and part["cy"] >= height * 0.48 and part["box"][3] >= part["box"][2] * 0.8 and within(part, 200, 420, 80))
    leg_pieces.sort(key=lambda part: part["cy"])
    thigh_part = leg_pieces[0] if leg_pieces else None
    thigh = take(pool, thigh_part)
    shins = [part for part in leg_pieces[1:] if part in pool and thigh_part and part["cy"] > thigh_part["cy"] + 70]
    shin = take(pool, shins[0] if shins else None)
    feet = region(pool, lambda part: part["cx"] >= width * 0.48 and part["cy"] > height * 0.7 and within(part, 240, 220, 20))
    foot = take(pool, max(feet, key=lambda part: part["cy"]) if feet else None)
    if shin and foot is None and shin[3] > 180:
        shin_box = shin
        foot = [shin_box[0], shin_box[1] + int(shin_box[3] * 0.62), shin_box[2], shin_box[3] - int(shin_box[3] * 0.62)]
        shin = [shin_box[0], shin_box[1], shin_box[2], int(shin_box[3] * 0.62)]
    weapons = region(pool, lambda part: part["box"][2] > part["box"][3] * 1.6 and part["box"][2] > 100)
    weapon = largest(weapons)
    return {
        "head": head, "torso": torso, "arm": arm, "forearm": forearm,
        "thigh": thigh, "shin": shin, "foot": foot,
        "weapon": None if weapon is None else weapon["box"],
    }


def crop_rgba(image, box):
    x, y, w, h = box
    rgba = image.convert("RGBA")
    return rgba.crop((x, y, x + w, y + h))


def keyed(crop):
    array = np.array(crop)
    red = array[:, :, 0].astype(np.int16)
    green = array[:, :, 1].astype(np.int16)
    blue = array[:, :, 2].astype(np.int16)
    magenta = (red > 110) & (blue > 100) & (green < 80) & (red > green + 40) & (blue > green + 30)
    panel = (green > 90) & (green > red + 12) & (green > blue + 8) & (red < 200)
    array[:, :, 3] = np.where(magenta | panel, 0, array[:, :, 3])
    return Image.fromarray(array)


def fit(crop, bounds):
    x, y, max_w, max_h = bounds
    scale = min(max_w / crop.width, max_h / crop.height, 1)
    size = (max(1, int(crop.width * scale)), max(1, int(crop.height * scale)))
    fitted = crop.resize(size, Image.Resampling.LANCZOS)
    return fitted, (x, y, fitted.width, fitted.height)


def digest(image):
    return hashlib.sha256(image.tobytes()).hexdigest()


def build(class_id, spec, commit):
    path = ROOT / spec["file"]
    image = Image.open(path)
    _rgb, _labels, parts, width, height = components(image)
    chosen = pick(parts, width, height, _rgb)
    missing = [name for name in LIMBS if not chosen.get(name)]
    preview = Image.new("RGBA", (8 * 170, 230), (0, 0, 0, 255))
    draw = ImageDraw.Draw(preview)
    hashes = {}
    crops = {}
    for index, name in enumerate(LIMBS + ["weapon"]):
        box = chosen.get(name)
        draw.text((index * 170 + 8, 8), name if box else f"{name} missing", fill=(240, 220, 180, 255))
        if not box:
            continue
        part = keyed(crop_rgba(image, box))
        thumb = part.copy()
        thumb.thumbnail((150, 180))
        preview.alpha_composite(thumb, (index * 170 + 8, 32))
        crops[name] = part
        hashes[name] = digest(part)
    PREVIEW.mkdir(parents=True, exist_ok=True)
    preview.save(PREVIEW / f"{class_id}.png")
    unique = len(missing) == 0 and len({hashes[name] for name in LIMBS}) == len(LIMBS)
    written = None
    rects = None
    if commit and unique:
        sheet = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
        rects = {}
        for name, part in crops.items():
            fitted, rect = fit(part, SLOT[name])
            sheet.alpha_composite(fitted, (rect[0], rect[1]))
            rects[name] = list(rect)
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        written = OUT_DIR / f"{class_id}.png"
        sheet.save(written)
        packed = {name: digest(sheet.crop(tuple(rect))) for name, rect in rects.items() if name in LIMBS}
        unique = len(set(packed.values())) == len(LIMBS)
        if not unique:
            written.unlink(missing_ok=True)
            written = None
            rects = None
    return {
        "classId": class_id,
        "sourceFile": spec["file"],
        "sheet": [width, height],
        "components": len(parts),
        "missing": missing,
        "hashesDiffer": unique and not missing,
        "boxes": chosen,
        "written": str(written.relative_to(ROOT)).replace("\\", "/") if written else None,
        "rects": rects,
    }


def main():
    commit = "--commit" in sys.argv
    atlas = json.loads(ATLAS_PATH.read_text(encoding="utf-8"))
    rows = [build(class_id, spec, commit) for class_id, spec in atlas["classes"].items()]
    if commit:
        ready = all(row["written"] and row["hashesDiffer"] for row in rows)
        for row in rows:
            if not row["written"]:
                continue
            spec = atlas["classes"][row["classId"]]
            spec["file"] = row["written"]
            spec["sheetSize"] = [1024, 1024]
            for name, rect in row["rects"].items():
                if name == "weapon" and "weapon" not in spec["parts"]:
                    continue
                spec["parts"][name] = rect
        atlas["worldReady"] = ready
        atlas["gait"] = "articulated-joints"
        atlas["status"] = "DISTINCT_LIMB_CROPS" if ready else "MEASURED_NOT_OWNER_ACCEPTED"
        ATLAS_PATH.write_text(json.dumps(atlas, indent=2) + "\n", encoding="utf-8")
    report = {"commit": commit, "rows": rows}
    (PREVIEW / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps([{k: row[k] for k in ("classId", "missing", "hashesDiffer", "components", "written")} for row in rows], indent=2))


if __name__ == "__main__":
    main()
