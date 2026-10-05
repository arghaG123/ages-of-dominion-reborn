"""Image-owned v4 actor and mount mattes.

Local crops only. No blur, smear, clone, warp, or new generation.
v3 derivatives are left in place.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path("C:/dev/ages-of-dominion-reborn")
NATIVE = ROOT / "assets/high-res/final-native2k"
OUT_A = ROOT / "assets/derivatives/actors/v4"
OUT_M = ROOT / "assets/derivatives/mounts/v4"
OUT_S = ROOT / "assets/derivatives/substitutions/v4"
QA = ROOT / "qa/image-v4-repair-20261004/actors"
for p in (OUT_A, OUT_M, OUT_S, QA):
    p.mkdir(parents=True, exist_ok=True)

ROLE_FAIL = {
    "troop-iron-melee": "ROLE_FAIL_MEDIEVAL_STENCIL_NOT_SELECTED_ROLE",
    "troop-industrial-heavy": "ROLE_FAIL_INDUSTRIAL_GUNNER_NOT_SELECTED_ROLE",
    "knight-mounted-master": "ROLE_FAIL_MEDIEVAL_MOUNTED_KNIGHT_NOT_STONE_TRAVEL",
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def corners_magenta(im: np.ndarray) -> bool:
    samples = np.stack([im[4, 4], im[4, -5], im[-5, 4], im[-5, -5]]).astype(np.int16)
    r, g, b = samples[:, 0], samples[:, 1], samples[:, 2]
    return bool(np.all((r > g + 40) & (b > g + 40)))


def background_mask(im: np.ndarray) -> np.ndarray:
    r, g, b = [im[:, :, i].astype(np.int16) for i in range(3)]
    if corners_magenta(im):
        return (r > g + 28) & (b > g + 28) & (np.abs(r - b) < 60)
    border = np.concatenate([
        im[:10, :, :].reshape(-1, 3),
        im[-10:, :, :].reshape(-1, 3),
        im[:, :10, :].reshape(-1, 3),
        im[:, -10:, :].reshape(-1, 3),
    ]).astype(np.float32)
    bg = np.median(border, axis=0)
    dist = np.sqrt(((im.astype(np.float32) - bg) ** 2).sum(axis=2))
    return dist < 22.0


def floor_color(im: np.ndarray) -> np.ndarray:
    r, g, b = [im[:, :, i].astype(np.int16) for i in range(3)]
    lum = (r.astype(np.int32) + g + b) // 3
    chroma = np.maximum(np.maximum(r, g), b) - np.minimum(np.minimum(r, g), b)
    neutral = (chroma < 20) & (lum > 145) & (lum < 230)
    earth = (r > 105) & (r > g + 4) & (g + 12 >= b) & ((r - b) > 18) & (lum > 108) & (lum < 235)
    return neutral | earth


def largest_label(mask: np.ndarray) -> np.ndarray:
    n, lab, stats, _ = cv2.connectedComponentsWithStats(mask.astype(np.uint8), 8)
    if n <= 1:
        return mask
    areas = stats[1:, cv2.CC_STAT_AREA]
    keep = 1 + int(np.argmax(areas))
    return lab == keep


def connected_to_upper(subject: np.ndarray, y0: int) -> np.ndarray:
    n, lab, stats, _ = cv2.connectedComponentsWithStats(subject.astype(np.uint8), 8)
    if n <= 1:
        return subject
    keep = np.zeros(n, dtype=bool)
    for i in range(1, n):
        y = int(stats[i, cv2.CC_STAT_TOP])
        if y < y0:
            keep[i] = True
    return keep[lab]


def _runs(xs: np.ndarray, gap: int = 8):
    if len(xs) == 0:
        return []
    runs = []
    start = prev = int(xs[0])
    for x in xs[1:]:
        x = int(x)
        if x > prev + gap:
            runs.append((start, prev))
            start = x
        prev = x
    runs.append((start, prev))
    return runs


def limb_columns(fg: np.ndarray, lum: np.ndarray) -> tuple[int, list[tuple[int, int]]]:
    """Last row that still has two or more dark limb runs, before the floor widens."""
    h, w = fg.shape
    found = None
    for y in range(int(h * 0.48), int(h * 0.82)):
        dark = fg[y] & (lum[y] < 90)
        runs = [pair for pair in _runs(np.where(dark)[0]) if 28 <= pair[1] - pair[0] <= 220]
        if len(runs) >= 2:
            found = (y, runs)
        elif found and y > found[0] + 24:
            break
    if not found:
        return int(h * 0.7), []
    y, runs = found
    expanded = []
    for a, b in runs:
        expanded.append((max(0, a - 36), min(w - 1, b + 36)))
    return y, expanded


# Reviewed on the native pixel grid. Rects keep boots/hooves; outside them the lower
# floor is dropped. These are source-specific, not a shared horizontal cutoff.
# Polygons are source pixels reviewed against the native grid. They follow boots
# rather than a horizontal cutoff. Order is (x, y).
LOWER_KEEP_POLYGONS = {
    # Full shin-to-sole columns from the native grid. Bright dirt outside them drops.
    "troop-stone-melee": [
        [[860, 1100], [1040, 1100], [1050, 1500], [1010, 1640], [950, 1700], [880, 1680], [870, 1500]],
        [[1045, 1100], [1320, 1100], [1340, 1480], [1280, 1605], [1160, 1655], [1060, 1600], [1035, 1400]],
    ],
    "troop-stone-ranged": [
        [[800, 1180], [1080, 1180], [1100, 1550], [1040, 1720], [900, 1775], [800, 1740], [770, 1500]],
        [[1100, 1180], [1480, 1180], [1500, 1520], [1420, 1685], [1240, 1735], [1120, 1695], [1085, 1450]],
    ],
}

# chroma max, luminance min for the neutral studio plane. Dirt plinths use polygons instead.
NEUTRAL_FLOOR = {
    "troop-bronze-melee": (16, 110),
    "troop-bronze-ranged": (12, 200),
    "troop-iron-ranged": (14, 120),
    "troop-iron-heavy": (14, 120),
    "troop-gunpowder-melee": (14, 140),
    "troop-gunpowder-ranged": (14, 120),
    "troop-modern-melee": (12, 150),
    "troop-modern-ranged": (10, 150),
    "troop-future-melee": (16, 140),
    "troop-future-ranged": (16, 150),
    "troop-future-heavy": (10, 95),
    "troop-industrial-ranged": (24, 150),
    "hero-mount-horse": (14, 145),
    "hero-mount-motor-transport": (12, 125),
    "hero-mount-future-transport": (12, 140),
}


def trace_subject(im: np.ndarray, y_frac: float = 0.62, keep_polygons=None, neutral=None) -> tuple[np.ndarray, dict]:
    """Key the backdrop, then keep lower limbs only inside reviewed boot/hoof polygons."""
    h, w, _ = im.shape
    bg = background_mask(im)
    fg = largest_label(~bg)
    if keep_polygons:
        subject = fg.copy()
        y_cut = min(pt[1] for poly in keep_polygons for pt in poly)
        allowed = np.zeros((h, w), np.uint8)
        cv2.fillPoly(allowed, [np.array(poly, np.int32) for poly in keep_polygons], 1)
        subject[y_cut:] &= allowed[y_cut:].astype(bool)
        subject = largest_label(subject)
        return subject, {
            "method": "reviewed boot/hoof polygons below the floor split; backdrop keyed; no blur",
            "keepPolygons": keep_polygons,
            "blur": False,
            "paintedFootMeasured": False,
            "contactNote": "Polygon follows the visible boot silhouette. The pivot is the lowest retained pixel in each polygon and is not an independent anatomical measurement.",
        }
    r, g, b = [im[:, :, i].astype(np.int16) for i in range(3)]
    lum = (r.astype(np.int32) + g + b) // 3
    chroma = np.maximum(np.maximum(r, g), b) - np.minimum(np.minimum(r, g), b)
    subject = fg.copy()
    # Near-white title bands and paper backdrops.
    subject[lum > 242] = False
    cmax, lmin = neutral if neutral else (14, 128)
    plane = (chroma <= cmax) & (lum >= lmin) & (lum < 242)
    subject[plane] = False
    # Keep the figure. Drop detached captions, scale bars, and extra silhouettes.
    n, lab, stats, _ = cv2.connectedComponentsWithStats(subject.astype(np.uint8), 8)
    if n > 1:
        areas = [(int(stats[i, cv2.CC_STAT_AREA]), i) for i in range(1, n)]
        areas.sort(reverse=True)
        biggest = areas[0][0]
        subject = np.zeros_like(subject)
        for area, i in areas:
            x, y, w, h, _ = [int(v) for v in stats[i]]
            if area < max(2500, int(biggest * 0.04)):
                continue
            if i != areas[0][1] and (w > h * 3 or h < 80):
                continue
            if i != areas[0][1]:
                continue
            subject[lab == i] = True
    notes = {
        "neutralChromaMax": cmax,
        "neutralLumMin": lmin,
        "method": "native backdrop key, neutral studio plane removed, largest remaining figure kept, no blur",
        "blur": False,
        "paintedFootMeasured": False,
    }
    return subject, notes


def foot_landmarks(im: np.ndarray, subject: np.ndarray) -> dict:
    ys, xs = np.where(subject)
    if len(ys) == 0:
        return {"status": "UNVERIFIED", "contacts": [], "uncertaintyPx": None}
    y_max = int(ys.max())
    band = subject & (np.arange(subject.shape[0])[:, None] >= y_max - 70)
    n, lab, stats, cent = cv2.connectedComponentsWithStats(band.astype(np.uint8), 8)
    contacts = []
    for i in range(1, n):
        if stats[i, cv2.CC_STAT_AREA] < 40:
            continue
        x, y, w, h, a = [int(v) for v in stats[i]]
        contacts.append({
            "kind": "lowest_retained_component",
            "sourceFrame": [x, y, x + w - 1, y + h - 1],
            "lowestY": y + h - 1,
            "centerX": int(round(cent[i][0])),
            "areaPx": a,
            "isMeasuredAnatomicalFoot": False,
            "uncertaintyPx": max(4, h // 3),
            "note": "Lowest retained component in the bottom band. Not a painted-foot measurement unless the component is a boot, hoof, or wheel.",
        })
    contacts.sort(key=lambda c: c["centerX"])
    return {
        "status": "ANNOTATED_LOWEST_RETAINED_COMPONENTS",
        "contacts": contacts[:4],
        "pivotIsNotAFoot": True,
    }


def save_rgba(im: np.ndarray, subject: np.ndarray, path: Path) -> None:
    rgba = np.dstack([im, (subject.astype(np.uint8) * 255)])
    Image.fromarray(rgba, "RGBA").save(path)


def qa_sheets(rgba_path: Path, item_id: str) -> dict:
    im = Image.open(rgba_path).convert("RGBA")
    arr = np.array(im)
    opaque = arr[:, :, 3] > 16
    ys, xs = np.where(opaque)
    if len(ys) == 0:
        return {}
    box = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)
    crop = im.crop(box)
    # native detail: lower 30% of the crop, unscaled if small else max width 900
    w, h = crop.size
    detail = crop.crop((0, int(h * 0.62), w, h))
    if detail.width > 900:
        detail = detail.resize((900, max(1, int(900 * detail.height / detail.width))), Image.Resampling.BOX)
    bgs = [("white", (255, 255, 255, 255)), ("black", (0, 0, 0, 255)), ("green", (110, 132, 104, 255))]
    dw, dh = detail.size
    sheet = Image.new("RGB", (dw * 3, dh + 4))
    for i, (_, col) in enumerate(bgs):
        layer = Image.new("RGBA", (dw, dh), col)
        layer.alpha_composite(detail)
        sheet.paste(layer.convert("RGB"), (i * dw, 0))
    detail_path = QA / f"{item_id}_detail_white_black_green.png"
    sheet.save(detail_path)
    thumbs = {}
    for name, col, width in (("64", (255, 255, 255, 255), 64), ("50", (0, 0, 0, 255), 50)):
        tw = width
        th = max(8, int(width * h / w))
        thumb = crop.resize((tw, th), Image.Resampling.BOX)
        canvases = []
        for _, bg in bgs:
            layer = Image.new("RGBA", thumb.size, bg)
            layer.alpha_composite(thumb)
            canvases.append(layer.convert("RGB"))
        row = Image.new("RGB", (tw * 3, th))
        for i, c in enumerate(canvases):
            row.paste(c, (i * tw, 0))
        rel = QA / f"{item_id}_consumer{name}.png"
        row.save(rel)
        thumbs[name] = str(rel.relative_to(ROOT)).replace("\\", "/")
    return {
        "tightBBox": [box[0], box[1], box[2] - 1, box[3] - 1],
        "detailEvidence": str(detail_path.relative_to(ROOT)).replace("\\", "/"),
        "consumerEvidence": thumbs,
    }


Y_FRAC = {
    "troop-stone-melee": 0.60,
    "troop-stone-ranged": 0.60,
    "troop-bronze-melee": 0.72,
    "troop-bronze-ranged": 0.55,
    "troop-iron-ranged": 0.70,
    "troop-iron-heavy": 0.72,
    "troop-gunpowder-melee": 0.74,
    "troop-gunpowder-ranged": 0.72,
    "troop-gunpowder-heavy": 0.58,
    "troop-industrial-ranged": 0.50,
    "troop-modern-melee": 0.62,
    "troop-modern-ranged": 0.62,
    "troop-future-melee": 0.68,
    "troop-future-ranged": 0.62,
    "troop-future-heavy": 0.70,
    "hero-mount-horse": 0.80,
    "hero-mount-motor-transport": 0.62,
    "hero-mount-future-transport": 0.58,
}


def drop_smooth_plane(im: np.ndarray, subject: np.ndarray, cmax: int, lmin: int) -> np.ndarray:
    rgb = im.astype(np.int16)
    chroma = rgb.max(axis=2) - rgb.min(axis=2)
    lum = rgb.sum(axis=2) // 3
    subject = subject & ~((chroma <= cmax) & (lum >= lmin) & (lum < 235))
    return largest_label(subject) if subject.any() else subject


def drop_earth_below(im: np.ndarray, subject: np.ndarray, y0: int, lum_min: int = 125) -> np.ndarray:
    rgb = im.astype(np.int16)
    lum = rgb.sum(axis=2) // 3
    earth = (rgb[:, :, 0] > rgb[:, :, 2] + 12) & (lum > lum_min)
    earth[:y0] = False
    subject = subject & ~earth
    kept = connected_to_upper(subject, y0)
    return largest_label(kept) if kept.any() else kept


def drop_pink_sheet(im: np.ndarray, subject: np.ndarray) -> np.ndarray:
    r, g, b = [im[:, :, i].astype(np.int16) for i in range(3)]
    pink = (r > g + 12) & (b > g + 6) & (r > 145) & (r + 15 > b) & ((r + g + b) // 3 > 140)
    subject = subject & ~pink
    return largest_label(subject) if subject.any() else subject


def split_shadow(im: np.ndarray, subject: np.ndarray):
    rgb = im.astype(np.int16)
    chroma = rgb.max(axis=2) - rgb.min(axis=2)
    lum = rgb.sum(axis=2) // 3
    shadow = subject & (chroma < 18) & (lum > 35) & (lum < 150)
    subject = subject & ~shadow
    return subject, shadow


def remove_thin_lines(subject: np.ndarray) -> np.ndarray:
    """Drop a 1-3px floor outline. Thick legs survive a 7px erosion."""
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    thick = cv2.erode(subject.astype(np.uint8), kernel)
    near = cv2.dilate(thick, kernel).astype(bool)
    h = subject.shape[0]
    lower = np.arange(h)[:, None] >= int(h * 0.62)
    return subject & (near | ~lower)


def process_one(item_id: str, kind: str) -> dict:
    src = NATIVE / f"{item_id}.png"
    im = np.array(Image.open(src).convert("RGB"))
    subject, notes = trace_subject(
        im, Y_FRAC.get(item_id, 0.64), LOWER_KEEP_POLYGONS.get(item_id), NEUTRAL_FLOOR.get(item_id)
    )
    if item_id in {"troop-bronze-melee", "troop-iron-ranged", "troop-iron-heavy", "troop-gunpowder-melee", "troop-gunpowder-ranged"}:
        subject, shadow = split_shadow(im, subject)
        notes = {**notes, "shadowSplit": True, "shadowPixels": int(shadow.sum())}
    if item_id in {"hero-mount-horse", "hero-mount-motor-transport", "hero-mount-future-transport", "troop-future-melee"}:
        subject = remove_thin_lines(subject)
        notes = {**notes, "thinLineRemoval": True}
    plane_pass = {
        "troop-future-melee": (16, 95),
        "troop-future-ranged": (16, 95),
        "troop-future-heavy": (16, 80),
        "troop-modern-melee": (16, 90),
        "troop-modern-ranged": (14, 100),
        "troop-bronze-ranged": (8, 150),
        "hero-mount-horse": (14, 90),
        "hero-mount-motor-transport": (20, 100),
        "hero-mount-future-transport": (18, 100),
    }
    if item_id in plane_pass:
        cmax, lmin = plane_pass[item_id]
        subject = drop_smooth_plane(im, subject, cmax, lmin)
        notes = {**notes, "secondPlane": [cmax, lmin]}
    if item_id in {"troop-stone-melee", "troop-stone-ranged"}:
        subject = drop_earth_below(im, subject, 1500, 155)
        notes = {**notes, "earthBelow": 1500, "earthLumMin": 155}
    if item_id == "troop-bronze-ranged":
        subject[:425, :860] = False
        subject = largest_label(subject)
        notes = {**notes, "titlePlaqueCleared": [0, 0, 860, 425]}
    if item_id == "troop-modern-melee":
        subject[1770:] = False
        notes = {**notes, "insetIconClearedBelow": 1770}
    if item_id == "troop-modern-ranged":
        subject[:640] = False
        subject = largest_label(subject)
        notes = {**notes, "keptForegroundSoldierBelow": 640}
    if item_id == "troop-future-ranged":
        subject[:, :780] = False
        subject[:, 1360:] = False
        # Neighbor card behind the gun arm. The helmet is above this box.
        subject[652:778, 1248:] = False
        subject = largest_label(subject)
        notes = {**notes, "keptPrimaryFigureX": [780, 1360], "neighborRectCleared": [1248, 652, 2048, 778]}
    if item_id == "troop-gunpowder-heavy":
        rgb = im.astype(np.int16)
        lum = rgb.sum(axis=2) // 3
        cool = (rgb[:, :, 2] > rgb[:, :, 0] + 18) & (rgb[:, :, 2] > rgb[:, :, 1] + 6) & (lum < 140) & (lum > 20)
        cool[:900] = False
        subject = largest_label(subject & ~cool)
        notes = {**notes, "coolCobbleBelow": 900}
    if item_id == "hero-mount-motor-transport":
        rgb = im.astype(np.int16)
        lum = rgb.sum(axis=2) // 3
        chroma = rgb.max(axis=2) - rgb.min(axis=2)
        gray = cv2.cvtColor(im, cv2.COLOR_RGB2GRAY).astype(np.float32)
        mean = cv2.blur(gray, (9, 9))
        std = np.sqrt(np.clip(cv2.blur(gray * gray, (9, 9)) - mean * mean, 0, None))
        ground = np.zeros(subject.shape, dtype=bool)
        ground[1550:] = (std[1550:] < 8) & (chroma[1550:] < 42) & (lum[1550:] > 40) & (lum[1550:] < 150)
        subject = largest_label(subject & ~ground)
        notes = {**notes, "lowGroundBelow": 1550}
    if item_id == "hero-mount-future-transport":
        rgb = im.astype(np.int16)
        lum = rgb.sum(axis=2) // 3
        chroma = rgb.max(axis=2) - rgb.min(axis=2)
        gray = cv2.cvtColor(im, cv2.COLOR_RGB2GRAY).astype(np.float32)
        mean = cv2.blur(gray, (11, 11))
        std = np.sqrt(np.clip(cv2.blur(gray * gray, (11, 11)) - mean * mean, 0, None))
        ground = (std < 8) & (chroma < 36) & (lum > 140) & (lum < 210)
        ground[:700] = False
        subject = largest_label(subject & ~ground)
        notes = {**notes, "lightGroundBelow": 700}
    if item_id == "troop-future-melee":
        gray = cv2.cvtColor(im, cv2.COLOR_RGB2GRAY).astype(np.float32)
        mean = cv2.blur(gray, (9, 9))
        std = np.sqrt(np.clip(cv2.blur(gray * gray, (9, 9)) - mean * mean, 0, None))
        rgb = im.astype(np.int16)
        chroma = rgb.max(axis=2) - rgb.min(axis=2)
        lum = rgb.sum(axis=2) // 3
        grid = (std < 8) & (chroma < 24) & (lum > 90) & (lum < 190) & (np.arange(im.shape[0])[:, None] > 1550)
        subject[grid] = False
        subject = largest_label(subject)
        notes = {**notes, "gridCleared": True}
    if item_id == "troop-industrial-ranged":
        subject = drop_pink_sheet(im, subject)
        # Break the thin sheet bridge, restore the soldier, leave the loose rifle behind.
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
        opened = cv2.morphologyEx(subject.astype(np.uint8), cv2.MORPH_OPEN, kernel)
        core = largest_label(opened.astype(bool))
        subject = cv2.dilate(core.astype(np.uint8), kernel).astype(bool) & subject
        subject = drop_pink_sheet(im, subject)
        notes = {**notes, "pinkSheetRemoved": True, "detachedRifleDropped": True, "paintedPose": "prone"}
    out_dir = {"actor": OUT_A, "mount": OUT_M}[kind]
    out = out_dir / f"{item_id}.png"
    save_rgba(im, subject, out)
    evidence = qa_sheets(out, item_id)
    contacts = foot_landmarks(im, subject)
    status = ROLE_FAIL.get(item_id, "LOCAL_MATTE_CANDIDATE_PIXEL_REVIEW_REQUIRED")
    if item_id in ROLE_FAIL:
        content = "FAIL_SELECTED_ROLE"
    else:
        content = "CANDIDATE_SUBJECT_ISOLATED_NOT_BLANKET_CLEAN"
    return {
        "id": item_id,
        "kind": kind,
        "contentStatus": content,
        "matteStatus": "RGBA_HARD_MASK_NO_BLUR",
        "contactStatus": contacts["status"],
        "dispositionStatus": status,
        "ownerAcceptance": "UNVERIFIED",
        "runtimeAcceptance": "UNVERIFIED",
        "source": {
            "path": f"assets/high-res/final-native2k/{item_id}.png",
            "sha256": sha256_file(src),
            "dimensions": [int(im.shape[1]), int(im.shape[0])],
            "mode": "RGB",
        },
        "derivative": {
            "path": str(out.relative_to(ROOT)).replace("\\", "/"),
            "sha256": sha256_file(out),
            "dimensions": [int(im.shape[1]), int(im.shape[0])],
            "mode": "RGBA",
            "recipe": notes,
        },
        "landmarks": contacts,
        "evidence": evidence,
        "preservedV3": f"assets/derivatives/{'actors' if kind=='actor' else 'mounts'}/v3/{item_id}.png",
    }


def copy_fail_rgb(item_id: str) -> dict:
    src = NATIVE / f"{item_id}.png"
    im = Image.open(src)
    out = OUT_M / f"{item_id}.png"
    im.save(out)
    return {
        "id": item_id,
        "kind": "mount",
        "contentStatus": "FAIL_SELECTED_ROLE",
        "matteStatus": "RGB_PRESERVED_NO_WORLD_ALPHA",
        "contactStatus": "NOT_A_MEASURED_CONTACT",
        "dispositionStatus": ROLE_FAIL[item_id],
        "ownerAcceptance": "UNVERIFIED",
        "runtimeAcceptance": "UNVERIFIED",
        "source": {
            "path": f"assets/high-res/final-native2k/{item_id}.png",
            "sha256": sha256_file(src),
            "dimensions": list(im.size),
            "mode": im.mode,
        },
        "derivative": {
            "path": str(out.relative_to(ROOT)).replace("\\", "/"),
            "sha256": sha256_file(out),
            "dimensions": list(im.size),
            "mode": im.mode,
            "recipe": {"method": "byte-preserving RGB copy of the native scenic painting", "blur": False},
        },
        "notes": "Medieval mounted knight stays rejected for the Stone travel role. Not relabeled.",
    }


def main():
    rows = []
    actors = [
        "troop-stone-melee", "troop-stone-ranged", "troop-stone-heavy",
        "troop-bronze-melee", "troop-bronze-ranged", "troop-bronze-heavy",
        "troop-iron-melee", "troop-iron-ranged", "troop-iron-heavy",
        "troop-medieval-melee", "troop-medieval-ranged", "troop-medieval-heavy",
        "troop-gunpowder-melee", "troop-gunpowder-ranged", "troop-gunpowder-heavy",
        "troop-industrial-melee", "troop-industrial-ranged", "troop-industrial-heavy",
        "troop-modern-melee", "troop-modern-ranged", "troop-modern-heavy",
        "troop-future-melee", "troop-future-ranged", "troop-future-heavy",
    ]
    for item_id in actors:
        row = process_one(item_id, "actor")
        rows.append(row)
        print(item_id, row["dispositionStatus"], row["evidence"].get("tightBBox"))
    for item_id in ("hero-mount-horse", "hero-mount-motor-transport", "hero-mount-future-transport"):
        row = process_one(item_id, "mount")
        rows.append(row)
        print(item_id, row["dispositionStatus"])
    rows.append(copy_fail_rgb("knight-mounted-master"))
    report = ROOT / "qa/image-v4-repair-20261004/actors-mounts-v4.json"
    report.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print("wrote", report)


if __name__ == "__main__":
    main()
