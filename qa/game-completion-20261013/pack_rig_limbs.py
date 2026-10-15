"""Pack one real limb crop per joint for the six unaccepted classes.

Healer and knight keep the boxes already accepted in the atlas. Production
sheets are read and never overwritten. A transparent 1024 sheet is written
only with --commit.
"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
ATLAS_PATH = ROOT / "src/data/actor-atlas.json"
OUT_DIR = ROOT / "assets/derivatives/rig-limbs-20261013/rigs"
PROOF = Path(__file__).resolve().parent / "rig-crops" / "labeled" / "packed-proof.png"
LIMBS = ["head", "torso", "arm", "forearm", "thigh", "shin", "foot"]
SLOT = {
    "head": (16, 16, 300, 420),
    "torso": (340, 16, 400, 460),
    "weapon": (760, 16, 240, 460),
    "arm": (16, 500, 200, 240),
    "forearm": (230, 500, 200, 240),
    "thigh": (450, 500, 180, 240),
    "shin": (650, 500, 170, 240),
    "foot": (840, 760, 160, 220),
}
WINDOWS = {
    "ranger": {
        "head": [184, 38, 139, 205],
        "torso": [562, 40, 386, 432],
        "arm": [38, 547, 77, 151],
        "forearm": [31, 703, 75, 188],
        "thigh": [570, 552, 84, 156],
        "shin": [572, 712, 68, 197],
        "foot": [779, 788, 92, 169],
        "weapon": [377, 531, 93, 472],
    },
    "warlock": {
        "head": [108, 227, 157, 245],
        "torso": [522, 54, 477, 311],
        "arm": [96, 559, 72, 210],
        "forearm": [180, 687, 215, 74],
        "thigh": [582, 670, 48, 110],
        "shin": [568, 805, 70, 140],
        "foot": [798, 780, 62, 144],
        "weapon": [405, 555, 70, 380],
    },
    "mage": {
        "head": [292, 44, 177, 223],
        "torso": [609, 47, 293, 413],
        "arm": [62, 557, 94, 187],
        "forearm": [195, 711, 154, 91],
        "thigh": [663, 544, 97, 178],
        "shin": [653, 728, 75, 163],
        "foot": [657, 894, 63, 79],
        "weapon": [368, 800, 46, 140],
    },
    "paladin": {
        "head": [80, 79, 147, 212],
        "torso": [557, 80, 181, 219],
        "arm": [85, 550, 107, 150],
        "forearm": [155, 782, 150, 62],
        "thigh": [559, 551, 105, 191],
        "shin": [572, 760, 82, 180],
        "foot": [858, 760, 78, 180],
        "weapon": [248, 525, 130, 210],
    },
    "barbarian": {
        "head": [30, 26, 140, 238],
        "torso": [557, 42, 209, 441],
        "arm": [42, 536, 63, 132],
        "forearm": [28, 668, 62, 110],
        "thigh": [556, 546, 86, 186],
        "shin": [912, 758, 88, 167],
        "foot": [905, 950, 105, 58],
        "weapon": [190, 855, 240, 95],
    },
    "necromancer": {
        "head": [368, 334, 110, 149],
        "torso": [652, 46, 204, 448],
        "arm": [25, 548, 100, 200],
        "forearm": [145, 548, 115, 200],
        "thigh": [880, 549, 112, 160],
        "shin": [880, 709, 112, 160],
        "foot": [880, 869, 112, 79],
        "weapon": [405, 545, 70, 430],
    },
}


def foreground(rgb):
    red = rgb[:, :, 0].astype(np.int16)
    green = rgb[:, :, 1].astype(np.int16)
    blue = rgb[:, :, 2].astype(np.int16)
    magenta = (red > 150) & (blue > 90) & (green < 150) & (red > green + 20) & (blue > green + 12)
    panel = (green > 85) & (green > red + 12) & (green > blue + 6) & (red < 200)
    return ~(magenta | panel)


def tighten(image, window):
    x, y, width, height = window
    crop = np.asarray(image.crop((x, y, x + width, y + height)).convert("RGB"))
    mask = foreground(crop)
    ys, xs = np.where(mask)
    if len(xs) < 80:
        return None
    return [int(x + xs.min()), int(y + ys.min()), int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1)]


def keyed(image, box):
    x, y, width, height = box
    crop = image.crop((x, y, x + width, y + height)).convert("RGBA")
    array = np.array(crop)
    keep = foreground(array[:, :, :3])
    array[:, :, 3] = np.where(keep, array[:, :, 3], 0)
    ys, xs = np.where(array[:, :, 3] > 0)
    if len(xs) < 80:
        return None
    trimmed = array[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    return Image.fromarray(trimmed)


def fit(crop, bounds):
    x, y, max_w, max_h = bounds
    scale = min(max_w / crop.width, max_h / crop.height, 1)
    size = (max(1, int(crop.width * scale)), max(1, int(crop.height * scale)))
    fitted = crop.resize(size, Image.Resampling.LANCZOS)
    return fitted, [x, y, fitted.width, fitted.height]


def digest(image):
    return hashlib.sha256(image.tobytes()).hexdigest()


def build_class(class_id, spec):
    image = Image.open(ROOT / spec["file"]).convert("RGBA")
    windows = WINDOWS[class_id]
    crops = {}
    source_boxes = {}
    for name, window in windows.items():
        box = tighten(image, window)
        if box is None:
            continue
        part = keyed(image, box)
        if part is None:
            continue
        crops[name] = part
        source_boxes[name] = box
    return crops, source_boxes


def main():
    commit = "--commit" in sys.argv
    atlas = json.loads(ATLAS_PATH.read_text(encoding="utf-8"))
    for class_id in ("knight", "healer"):
        WINDOWS[class_id] = {name: list(box) for name, box in atlas["classes"][class_id]["parts"].items()}
    proof_rows = []
    packed_rows = []
    for class_id, spec in atlas["classes"].items():
        crops, source_boxes = build_class(class_id, spec)
        missing = [name for name in LIMBS if name not in crops]
        hashes = {name: digest(crops[name]) for name in LIMBS if name in crops}
        unique = not missing and len(set(hashes.values())) == len(LIMBS)
        rects = None
        written = None
        if unique:
            sheet = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
            rects = {}
            for name, part in crops.items():
                fitted, rect = fit(part, SLOT[name])
                sheet.alpha_composite(fitted, (rect[0], rect[1]))
                rects[name] = rect
            packed_hashes = {}
            for name in LIMBS:
                rect = rects[name]
                packed_hashes[name] = digest(sheet.crop((rect[0], rect[1], rect[0] + rect[2], rect[1] + rect[3])))
            unique = len(set(packed_hashes.values())) == len(LIMBS)
            if unique and commit:
                OUT_DIR.mkdir(parents=True, exist_ok=True)
                written = OUT_DIR / f"{class_id}.png"
                sheet.save(written)
        proof_rows.append((class_id, crops))
        packed_rows.append({
            "classId": class_id,
            "missing": missing,
            "unique": unique,
            "sourceBoxes": source_boxes,
            "rects": rects,
            "opaque": {name: int(np.array(crops[name])[:, :, 3].sum() > 0 and np.count_nonzero(np.array(crops[name])[:, :, 3])) for name in crops},
        })
        print(class_id, "missing", missing, "unique", unique)
    cell = 120
    names = LIMBS + ["weapon"]
    sheet = Image.new("RGB", (len(names) * cell, len(proof_rows) * cell), (16, 16, 16))
    draw = ImageDraw.Draw(sheet)
    for row_index, (class_id, crops) in enumerate(proof_rows):
        for col, name in enumerate(names):
            draw.text((col * cell + 4, row_index * cell + 2), f"{class_id[:3]} {name[:4]}", fill=(230, 200, 140))
            part = crops.get(name)
            if part is None:
                continue
            thumb = part.copy()
            thumb.thumbnail((cell - 8, cell - 18))
            sheet.paste(thumb, (col * cell + 4, row_index * cell + 16), thumb)
    sheet.save(PROOF)
    ready = all(row["unique"] for row in packed_rows)
    if commit and ready:
        for row in packed_rows:
            spec = atlas["classes"][row["classId"]]
            spec["file"] = f"assets/derivatives/rig-limbs-20261013/rigs/{row['classId']}.png"
            spec["parts"] = {name: rect for name, rect in row["rects"].items()}
        atlas["worldReady"] = True
        atlas["gait"] = "per-joint"
        atlas["status"] = "DISTINCT_LIMB_CROPS_OWNER_UNVERIFIED"
        ATLAS_PATH.write_text(json.dumps(atlas, indent=2) + "\n", encoding="utf-8")
    print("ready", ready, "proof", PROOF)


if __name__ == "__main__":
    main()
