"""Local v6 image delivery. No provider, no original overwrite.

Foreground-protected masks and padded joint placement from
docs/plan/IMAGE-AI-CONSOLIDATED-LOCAL-SOLUTION-2026-10-04.txt.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / "qa" / "image-local-solution-20261004"
RIG = ROOT / "assets" / "derivatives" / "rigs" / "v6"
ACT = ROOT / "assets" / "derivatives" / "actors" / "v6"
NATIVE = ROOT / "assets" / "high-res" / "final-native2k"
GREEN_BG = (110, 132, 104)
HEALER_GREEN = np.array([144, 178, 104], np.float32)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_rgb(path: Path) -> np.ndarray:
    return np.array(Image.open(path).convert("RGB"))


def load_rgba(path: Path) -> np.ndarray:
    return np.array(Image.open(path).convert("RGBA"))


def save_rgba(path: Path, rgba: np.ndarray) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(rgba, "RGBA").save(path)
    return sha256(path)


def alpha_bbox(a: np.ndarray, thresh: int = 16):
    ys, xs = np.where(a > thresh)
    if len(xs) == 0:
        return None
    return [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]


def trim(rgba: np.ndarray):
    box = alpha_bbox(rgba[:, :, 3])
    if box is None:
        return rgba, [0, 0, rgba.shape[1], rgba.shape[0]]
    l, t, r, b = box
    return rgba[t:b, l:r].copy(), box


def composite(rgba: np.ndarray, color, height: int) -> Image.Image:
    im = Image.fromarray(rgba, "RGBA")
    subject = alpha_bbox(rgba[:, :, 3])
    if subject is None:
        return Image.new("RGB", (height, height), color)
    l, t, r, b = subject
    crop = im.crop((l, t, r, b))
    scale = height / crop.size[1]
    size = (max(1, int(round(crop.size[0] * scale))), height)
    crop = crop.resize(size, Image.Resampling.BOX)
    bg = Image.new("RGB", size, color)
    bg.paste(crop, mask=crop.getchannel("A"))
    return bg


def sheet3(rgba: np.ndarray, height: int, path: Path):
    panels = [composite(rgba, c, height) for c in ((255, 255, 255), (0, 0, 0), GREEN_BG)]
    w = sum(p.size[0] for p in panels) + 8
    h = height
    out = Image.new("RGB", (w, h), (20, 20, 20))
    x = 0
    for p in panels:
        out.paste(p, (x, 0))
        x += p.size[0] + 4
    path.parent.mkdir(parents=True, exist_ok=True)
    out.save(path)


def flood_border(mask: np.ndarray) -> np.ndarray:
    lab, _ = ndimage_label(mask)
    h, w = mask.shape
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    keep = [int(v) for v in edge if v]
    if not keep:
        return np.zeros_like(mask)
    return np.isin(lab, keep)


def ndimage_label(mask: np.ndarray):
    from scipy import ndimage
    return ndimage.label(mask)


def grabcut_protected(rgb: np.ndarray, fg: np.ndarray, bg: np.ndarray):
    """Five GrabCut iterations. Definite foreground is forced back on."""
    mask = np.full(fg.shape, cv2.GC_PR_FGD, np.uint8)
    mask[bg] = cv2.GC_BGD
    mask[fg] = cv2.GC_FGD
    if not fg.any() or not bg.any():
        alpha = np.where(fg, 255, 0).astype(np.uint8)
        return alpha, {"grabcut": False, "reason": "missing seed"}
    bgd = np.zeros((1, 65), np.float64)
    fgd = np.zeros((1, 65), np.float64)
    cv2.grabCut(rgb, mask, None, bgd, fgd, 5, cv2.GC_INIT_WITH_MASK)
    alpha = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)
    alpha[fg] = 255
    alpha[bg] = 0
    lost = int((fg & (alpha == 0)).sum())
    return alpha, {"grabcut": True, "iterations": 5, "definiteForegroundLost": lost}


def healer_extract(src: np.ndarray, box, name: str):
    l, t, r, b = box
    rgb = src[t:b, l:r]
    dist = np.linalg.norm(rgb.astype(np.float32) - HEALER_GREEN, axis=2)
    magenta = (rgb[:, :, 0] > 200) & (rgb[:, :, 2] > 200) & (rgb[:, :, 1] < 80)
    near = (dist < 28) | magenta
    bg = flood_border(near)
    fg = (dist > 42) & ~magenta & ~bg
    alpha, meta = grabcut_protected(rgb, fg, bg)
    rgba = np.dstack([rgb, alpha])
    trimmed, local = trim(rgba)
    rel = [l + local[0], t + local[1], l + local[2], t + local[3]]
    out = RIG / "healer" / f"{name}.png"
    digest = save_rgba(out, trimmed)
    mask_path = QA / "masks" / "healer" / f"{name}.png"
    save_rgba(mask_path, np.dstack([alpha, alpha, alpha, np.full_like(alpha, 255)]))
    recipe = {
        "id": f"healer-{name}",
        "semantic": name,
        "source": "assets/high-res/final-native2k/rig-source-parts-healer.png",
        "sourceSha256": "0f576da0a5adce8ece30be32b487f58b20c7900001bfe6d31d80f8005b70aca1",
        "searchBox": box,
        "crop": rel,
        "derivative": str(out.relative_to(ROOT)).replace("\\", "/"),
        "sha256": digest,
        "dimensions": [trimmed.shape[1], trimmed.shape[0]],
        "mode": "RGBA",
        "method": "v6-healer-green-flood-grabcut",
        "parameters": {
            "backgroundDistanceLt": 28,
            "foregroundDistanceGt": 42,
            "greenReference": [144, 178, 104],
            "grabCutIterations": 5,
            **meta,
        },
        "side": "UNKNOWN",
        "definiteForegroundPixels": int(fg.sum()),
        "opaquePixels": int((trimmed[:, :, 3] > 16).sum()),
    }
    (QA / "recipes").mkdir(parents=True, exist_ok=True)
    (QA / "recipes" / f"healer-{name}.json").write_text(json.dumps(recipe, indent=2), encoding="utf-8")
    return recipe


def component_boxes(rgb: np.ndarray, bg: np.ndarray, min_px: int):
    from scipy import ndimage
    lab, n = ndimage.label(bg)
    h, w = bg.shape
    edge = set(int(v) for v in np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])) if v)
    fg = ~np.isin(lab, list(edge)) if edge else ~bg
    lab2, n2 = ndimage.label(fg)
    rows = []
    for i in range(1, n2 + 1):
        ys, xs = np.where(lab2 == i)
        if len(ys) < min_px:
            continue
        rows.append((int(len(ys)), int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1, i))
    rows.sort(reverse=True)
    return rows, lab2


def cut_component(src: np.ndarray, lab, idx, box):
    l, t, r, b, = box
    sl = lab[t:b, l:r] == idx
    rgb = src[t:b, l:r]
    alpha = np.where(sl, 255, 0).astype(np.uint8)
    rgba = np.dstack([rgb, alpha])
    return trim(rgba)


def paladin_parts(src: np.ndarray):
    mag = (src[:, :, 0] > 170) & (src[:, :, 2] > 140) & (src[:, :, 1] < 90)
    rows, lab = component_boxes(src, mag, 6000)
    # Names checked against the component contact sheet. Title banner excluded.
    named = {
        "helmet": (130, 158, 457, 728),
        "cuirass_front": (649, 161, 1017, 652),
        "cuirass_fauld_combined": (1114, 161, 1485, 974),
        "pauldron_upper": (1590, 157, 1830, 461),
        "forearm_gauntlet": (1720, 580, 1910, 1015),
        "gauntlet_open": (1558, 796, 1703, 1007),
        "sword_hand_assembly": (304, 671, 769, 1872),
        "shield": (785, 1369, 1074, 1877),
        "head_profile": (143, 694, 321, 938),
        "head_three_quarter": (366, 704, 523, 946),
        "rerebrace": (170, 1099, 384, 1399),
        "couter": (180, 1417, 346, 1574),
        "thigh": (1118, 1103, 1328, 1485),
        "thigh_alternate": (1684, 1097, 1864, 1489),
        "knee_cop": (1414, 1098, 1602, 1398),
        "greave": (1144, 1519, 1308, 1880),
        "boot": (1434, 1425, 1690, 1880),
        "sole": (1717, 1520, 1871, 1879),
    }
    # One coherent set. Alternates stay in the recipe, not as extra required limbs.
    ship = [
        "helmet", "cuirass_fauld_combined", "head_three_quarter", "forearm_gauntlet",
        "sword_hand_assembly", "shield", "thigh", "knee_cop", "greave", "boot",
    ]
    out = []
    for name, box in named.items():
        if name not in ship:
            continue
        hits = [row for row in rows if row[1] >= box[0] - 30 and row[2] >= box[1] - 30 and row[3] <= box[2] + 30 and row[4] <= box[3] + 40]
        if not hits:
            hits = [row for row in rows if abs(row[1] - box[0]) < 40 and abs(row[2] - box[1]) < 40]
        if not hits:
            out.append({"id": f"paladin-{name}", "status": "MISS", "box": list(box)})
            continue
        _n, l, t, r, b, idx = hits[0]
        trimmed, local = cut_component(src, lab, idx, (l, t, r, b))
        path = RIG / "paladin" / f"{name}.png"
        digest = save_rgba(path, trimmed)
        recipe = {
            "id": f"paladin-{name}",
            "semantic": name,
            "assembly": "COMBINED" if name in ("cuirass_fauld_combined", "sword_hand_assembly", "forearm_gauntlet") else "SINGLE",
            "side": "UNKNOWN",
            "source": "assets/high-res/final-native2k/rig-source-parts-paladin.png",
            "sourceSha256": "a6bafe602378104b1e6de8a77b900342590457a2019ed11d43fbf0a1899e7e55",
            "crop": [l, t, r, b],
            "derivative": str(path.relative_to(ROOT)).replace("\\", "/"),
            "sha256": digest,
            "dimensions": [trimmed.shape[1], trimmed.shape[0]],
            "method": "v6-magenta-border-component",
            "titleExcluded": True,
            "note": "Screen position is not anatomical left/right. No mirror was applied.",
        }
        (QA / "recipes" / f"paladin-{name}.json").write_text(json.dumps(recipe, indent=2), encoding="utf-8")
        out.append(recipe)
    return out


def grey_components(src: np.ndarray, class_id: str, corner_tol: int = 18):
    bg_color = src[8, 8].astype(np.int16)
    dist = np.abs(src.astype(np.int16) - bg_color).sum(axis=2)
    bg = dist < corner_tol
    rows, lab = component_boxes(src, bg, 4000)
    # Drop the title/text band if it sits on the top edge and is very wide.
    kept = []
    for row in rows:
        _n, l, t, r, b, idx = row
        if t < 20 and (r - l) > 800:
            continue
        trimmed, _local = cut_component(src, lab, idx, (l, t, r, b))
        kept.append({
            "pixels": row[0],
            "crop": [l, t, r, b],
            "size": [trimmed.shape[1], trimmed.shape[0]],
        })
        path = QA / "components" / class_id / f"{len(kept):02d}_{l}_{t}.png"
        save_rgba(path, trimmed)
    (QA / "recipes").mkdir(parents=True, exist_ok=True)
    (QA / "components" / f"{class_id}-boxes.json").write_text(json.dumps(kept, indent=2), encoding="utf-8")
    return kept


def cuff_profile(alpha: np.ndarray, end: str):
    a = alpha > 128
    h, w = a.shape
    span = 40 if h > 80 else max(8, h // 5)
    rows = range(h - 1, h - span, -1) if end == "distal" else range(0, span)
    best = None
    for y in rows:
        xs = np.where(a[y])[0]
        if len(xs) < 4:
            continue
        width = int(xs.max() - xs.min() + 1)
        cx = int((xs.min() + xs.max()) / 2)
        rec = {"y": int(y), "width": width, "cx": cx, "x0": int(xs.min()), "x1": int(xs.max())}
        if best is None or width > best["width"]:
            best = rec
    return best


def warp_part(rgba: np.ndarray, joint_xy, pivot_xy, angle_deg, scale, canvas):
    h, w = rgba.shape[:2]
    ch, cw = canvas
    jx, jy = joint_xy
    px, py = pivot_xy
    rad = np.deg2rad(angle_deg)
    c, s = np.cos(rad) * scale, np.sin(rad) * scale
    # dest = R * (src - joint) * scale + pivot
    # [c -s; s c] * (src - joint) + pivot
    m = np.array([[c, -s, px - (c * jx - s * jy)], [s, c, py - (s * jx + c * jy)]], np.float32)
    bgr = cv2.cvtColor(rgba, cv2.COLOR_RGBA2BGRA)
    warped = cv2.warpAffine(bgr, m, (cw, ch), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    return cv2.cvtColor(warped, cv2.COLOR_BGRA2RGBA)


def overlap_span(parent_a, child_a, pivot, cuff_w):
    px, py = int(pivot[0]), int(pivot[1])
    rad = max(8, int(cuff_w))
    y0, y1 = max(0, py - rad), min(parent_a.shape[0], py + rad)
    x0, x1 = max(0, px - rad * 2), min(parent_a.shape[1], px + rad * 2)
    both = (parent_a[y0:y1, x0:x1] > 128) & (child_a[y0:y1, x0:x1] > 16)
    if not both.any():
        return 0, 0
    best = 0
    for row in both:
        run = 0
        for v in row:
            run = run + 1 if v else 0
            best = max(best, run)
    return int(both.sum()), int(best)


def scaled_gap(parent_a, child_a, height):
    """Gap at display height: a transparent row between the two silhouettes."""
    pa = Image.fromarray(parent_a)
    ca = Image.fromarray(child_a)
    ys, xs = np.where((parent_a > 16) | (child_a > 16))
    if len(ys) == 0:
        return None
    box = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)
    pa = pa.crop(box).resize((max(1, int((box[2] - box[0]) * height / (box[3] - box[1]))), height), Image.Resampling.BOX)
    ca = ca.crop(box).resize(pa.size, Image.Resampling.BOX)
    p = np.array(pa) > 16
    c = np.array(ca) > 16
    touch = 0
    for y in range(p.shape[0] - 1):
        if (p[y] & c[y]).any() or (p[y] & c[y + 1]).any() or (c[y] & p[y + 1]).any():
            touch += 1
    return {"height": height, "touchingRows": int(touch), "size": list(pa.size)}


def joint_search(parent_rgba, child_rgba, pair_name):
    pc = cuff_profile(parent_rgba[:, :, 3], "distal")
    cc = cuff_profile(child_rgba[:, :, 3], "proximal")
    if pc is None or cc is None:
        return {"pair": pair_name, "status": "FAIL_NO_CUFF"}
    cuff_w = max(pc["width"], cc["width"])
    scale = 1.0
    ratio = pc["width"] / max(1, cc["width"])
    if ratio < 0.75 or ratio > 1.35:
        scale = pc["width"] / cc["width"]
        if scale < 0.7 or scale > 1.4:
            return {
                "pair": pair_name,
                "status": "FAIL_IMPLAUSIBLE_SCALE",
                "cuffParent": pc,
                "cuffChild": cc,
                "scale": scale,
            }
    ph, pw = parent_rgba.shape[:2]
    ch, cw = child_rgba.shape[:2]
    pad = int(max(pw, ph, cw, ch) * 1.2)
    canvas = (ph + ch + pad, pw + cw + pad)
    pivot = (canvas[1] // 2, canvas[0] // 2)
    parent_joint = (pc["cx"], pc["y"])
    child_joint = (cc["cx"], cc["y"])
    parent_layer = warp_part(parent_rgba, parent_joint, pivot, 0, 1.0, canvas)
    results = []
    for ins in (0.0, 0.10, 0.20, 0.30):
        for trans in (-0.05, 0.0, 0.05):
            # Inward insertion moves the child joint up into the sleeve (negative y).
            shifted = (pivot[0] + trans * cuff_w, pivot[1] - ins * cuff_w)
            pose = []
            for ang in (-25, 0, 25):
                child_layer = warp_part(child_rgba, child_joint, shifted, ang, scale, canvas)
                # Occlusion: distal limb behind the sleeve, so overlap is measured on masks before cover.
                count, span = overlap_span(parent_layer[:, :, 3], child_layer[:, :, 3], shifted, cuff_w)
                gap = scaled_gap(parent_layer[:, :, 3], child_layer[:, :, 3], 130)
                pose.append({"angle": ang, "overlapPx": count, "spanPx": span, "at130": gap})
            results.append({"insertion": ins, "transverse": trans, "poses": pose, "childPivot": [shifted[0], shifted[1]]})
    def score(row):
        neutral = next(p for p in row["poses"] if p["angle"] == 0)
        return (neutral["spanPx"], neutral["at130"]["touchingRows"] if neutral["at130"] else 0, neutral["overlapPx"])
    ranked = sorted(results, key=score, reverse=True)
    best = ranked[0]
    neutral = next(p for p in best["poses"] if p["angle"] == 0)
    status = "FAIL_NO_CONTINUOUS_CONTACT"
    if neutral["spanPx"] >= 8 and neutral["at130"] and neutral["at130"]["touchingRows"] >= 2:
        status = "PASS_STATIC_AND_LIMITED_ARC" if all(p["spanPx"] >= 6 for p in best["poses"]) else "PASS_STATIC_ROTATION_UNVERIFIED"
    # Save the best neutral and the three angles. Child behind parent.
    evidence = []
    for ang in (-25, 0, 25):
        child_layer = warp_part(child_rgba, child_joint, tuple(best["childPivot"]), ang, scale, canvas)
        merged = child_layer.copy()
        cover = parent_layer[:, :, 3] > 16
        merged[cover] = parent_layer[cover]
        trimmed, _box = trim(merged)
        path = QA / "joints" / f"{pair_name}_{ang}.png"
        digest = save_rgba(path, trimmed)
        evidence.append({"angle": ang, "path": str(path.relative_to(ROOT)).replace("\\", "/"), "sha256": digest})
        sheet3(trimmed, 130, QA / "joints" / f"{pair_name}_{ang}_130.png")
    return {
        "pair": pair_name,
        "status": status,
        "cuffParent": pc,
        "cuffChild": cc,
        "uniformScale": scale,
        "scaleRejected": False,
        "canvas": list(canvas),
        "padding": pad,
        "parentJointInPart": [pc["cx"], pc["y"]],
        "childJointInPart": [cc["cx"], cc["y"]],
        "sharedPivotOnCanvas": best["childPivot"],
        "best": best,
        "placementsTested": 12,
        "evidence": evidence,
        "method": "padded-affine-child-behind-parent",
    }


def locate_template(native_rgb, part_rgba):
    gray_n = cv2.cvtColor(native_rgb, cv2.COLOR_RGB2GRAY)
    gray_p = cv2.cvtColor(part_rgba[:, :, :3], cv2.COLOR_RGB2GRAY)
    mask = np.where(part_rgba[:, :, 3] > 128, 255, 0).astype(np.uint8)
    if mask.sum() < 50:
        return None
    res = cv2.matchTemplate(gray_n, gray_p, cv2.TM_CCOEFF_NORMED, mask=mask)
    _minv, maxv, _minl, maxl = cv2.minMaxLoc(res)
    h, w = gray_p.shape
    return {"score": float(maxv), "crop": [int(maxl[0]), int(maxl[1]), int(maxl[0] + w), int(maxl[1] + h)]}


def separate_shadow(rgba: np.ndarray, name: str):
    """Remove a pale cast shadow that is not boot leather. Keep a rejected copy."""
    a = rgba[:, :, 3]
    rgb = rgba[:, :, :3].astype(np.int16)
    lum = rgb.mean(axis=2)
    chroma = rgb.max(axis=2) - rgb.min(axis=2)
    pale = (a > 16) & (lum > 135) & (chroma < 28)
    dark = (a > 100) & (lum < 115)
    from scipy import ndimage
    # Boots/body are the dark core. Do not flood through them.
    protect = ndimage.binary_dilation(dark, iterations=2)
    seed = pale & ~protect
    lab, _n = ndimage.label(seed)
    # Keep pale components whose centroid is low (ground), not helmet highlights.
    shadow = np.zeros(a.shape, bool)
    h = a.shape[0]
    for i in range(1, int(lab.max()) + 1):
        ys, xs = np.where(lab == i)
        if len(ys) < 400:
            continue
        if ys.mean() > h * 0.55:
            shadow[lab == i] = True
    candidate = rgba.copy()
    candidate[shadow, 3] = 0
    # Boot check: dark pixels in the lower third must survive.
    low = np.zeros(a.shape, bool)
    low[int(h * 0.62):, :] = True
    boots = dark & low
    lost = int((boots & (candidate[:, :, 3] == 0)).sum())
    shadow_layer = np.zeros_like(rgba)
    shadow_layer[shadow] = rgba[shadow]
    return candidate, shadow_layer, {"shadowPixels": int(shadow.sum()), "bootPixelsLost": lost, "bootPixels": int(boots.sum())}


def modern_heavy(rgba: np.ndarray):
    a = rgba[:, :, 3]
    rgb = rgba[:, :, :3]
    mag = (a > 16) & (rgb[:, :, 0] > 160) & (rgb[:, :, 2] > 120) & (rgb[:, :, 1] < 110) & ((rgb[:, :, 0].astype(int) - rgb[:, :, 1].astype(int)) > 70)
    protect = (a > 16) & ~mag
    from scipy import ndimage
    # Ground slab: pale neutral pixels in the lower band, outside the protected vehicle core.
    lum = rgb.astype(np.int16).mean(2)
    pale = (a > 16) & (lum > 95) & (lum < 170) & (np.abs(rgb[:, :, 0].astype(int) - rgb[:, :, 2].astype(int)) < 30)
    low = np.zeros(a.shape, bool)
    low[1100:, :] = True
    ground_seed = pale & low & ~ndimage.binary_dilation(protect & (lum < 90), iterations=1)
    lab, _ = ndimage.label(ground_seed)
    ground = np.zeros(a.shape, bool)
    for i in range(1, int(lab.max()) + 1):
        ys, xs = np.where(lab == i)
        if len(ys) > 1500 and xs.min() < 80:
            ground[lab == i] = True
    # Do not delete protected pixels.
    ground = ground & ~protect
    mag = mag & ~protect
    out = rgba.copy()
    out[mag | ground, 3] = 0
    lost = int((protect & (out[:, :, 3] == 0)).sum())
    return out, {"magentaCleared": int(mag.sum()), "groundCleared": int(ground.sum()), "protectedLost": lost}


def modern_mound(rgba: np.ndarray):
    """Optional bright mound in front of the bipod. Keep the under-body sheet."""
    a = rgba[:, :, 3]
    rgb = rgba[:, :, :3].astype(np.int16)
    lum = rgb.mean(2)
    bright = (a > 16) & (lum > 185)
    body = (a > 16) & (lum < 150)
    from scipy import ndimage
    body_d = ndimage.binary_dilation(body, iterations=3)
    lab, _ = ndimage.label(bright & ~body_d)
    mound = np.zeros(a.shape, bool)
    chosen = None
    for i in range(1, int(lab.max()) + 1):
        ys, xs = np.where(lab == i)
        if len(ys) < 800 or len(ys) > 80000:
            continue
        # In front of the bipod: lower-middle, not the sheet under the torso (higher and wider).
        if ys.mean() < 1000:
            continue
        if (body_d[lab == i]).any():
            continue
        mound[lab == i] = True
        chosen = {"pixels": int(len(ys)), "crop": [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]}
        break
    out = rgba.copy()
    if chosen:
        out[mound, 3] = 0
    return out, {"separated": bool(chosen), "mound": chosen, "generalSprite": "FAIL", "role": "SNOW_SCENE_ILLUSTRATION"}


def visible_extent(path: Path):
    rgba = load_rgba(path)
    box = alpha_bbox(rgba[:, :, 3])
    return {
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "sha256": sha256(path),
        "canvas": [rgba.shape[1], rgba.shape[0]],
        "visibleSubject": box,
        "visibleHeight": None if box is None else box[3] - box[1],
        "visibleWidth": None if box is None else box[2] - box[0],
    }


def contact_points(path: Path):
    rgba = load_rgba(path)
    a = rgba[:, :, 3]
    box = alpha_bbox(a, 128)
    if box is None:
        return None
    l, t, r, b = box
    # Lowest opaque row per x-column in the bottom 15% of the subject, ignoring a wide pale skirt.
    band = a.copy()
    band[: b - max(8, (b - t) // 7), :] = 0
    ys, xs = np.where(band > 128)
    if len(xs) == 0:
        return {"path": str(path.relative_to(ROOT)).replace("\\", "/"), "contact": "NONE"}
    # Two clusters: split at median x if the gap is wide.
    order = np.argsort(xs)
    xs_s, ys_s = xs[order], ys[order]
    gaps = np.where(np.diff(xs_s) > 30)[0]
    clusters = []
    start = 0
    cuts = list(gaps) + [len(xs_s) - 1]
    prev = 0
    for g in gaps:
        clusters.append((xs_s[prev:g + 1], ys_s[prev:g + 1]))
        prev = g + 1
    clusters.append((xs_s[prev:], ys_s[prev:]))
    points = []
    for cxs, cys in clusters:
        if len(cxs) < 8:
            continue
        k = int(np.argmax(cys))
        points.append({"x": int(cxs[k]), "y": int(cys[k]), "uncertaintyPx": 4})
    return {
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "subject": box,
        "contacts": points[:4],
        "note": "Lowest opaque pixel in the bottom band. A shadow can still sit below this if it was not removed.",
    }


def drop_edge_fragment(path: Path, side: str = "right"):
    rgba = load_rgba(path)
    a = rgba[:, :, 3] > 32
    from scipy import ndimage
    lab, n = ndimage.label(a)
    if n < 2:
        return None
    h, w = a.shape
    sizes = [(int((lab == i).sum()), i) for i in range(1, n + 1)]
    sizes.sort(reverse=True)
    keep = sizes[0][1]
    dropped = 0
    for count, i in sizes[1:]:
        ys, xs = np.where(lab == i)
        if side == "right" and xs.mean() > w * 0.82 and count < sizes[0][0] * 0.15:
            rgba[lab == i, 3] = 0
            dropped += count
    if dropped == 0:
        return None
    trimmed, _box = trim(rgba)
    digest = save_rgba(path, trimmed)
    return {"droppedPixels": dropped, "sha256": digest, "dimensions": [trimmed.shape[1], trimmed.shape[0]]}


def shadow_correction(src_rel: str, aid: str, seed_box, lum_min, chroma_max, protect_lum):
    rgba = load_rgba(ROOT / src_rel)
    a = rgba[:, :, 3]
    rgb = rgba[:, :, :3].astype(np.int16)
    lum = rgb.mean(2)
    chroma = rgb.max(2) - rgb.min(2)
    l, t, r, b = seed_box
    seed = np.zeros(a.shape, bool)
    seed[t:b, l:r] = (a[t:b, l:r] > 16) & (lum[t:b, l:r] > lum_min) & (chroma[t:b, l:r] < chroma_max)
    from scipy import ndimage
    walk = (a > 16) & (lum > lum_min) & (chroma < chroma_max) & (lum > protect_lum)
    protect = (a > 100) & (lum <= protect_lum)
    walk = walk & ~ndimage.binary_dilation(protect, iterations=1)
    lab, _n = ndimage.label(walk)
    shadow = np.zeros(a.shape, bool)
    seeds = np.unique(lab[seed])
    for i in seeds:
        if i == 0:
            continue
        if (lab == i).sum() < 300:
            continue
        shadow[lab == i] = True
    out = rgba.copy()
    out[shadow, 3] = 0
    low = np.zeros(a.shape, bool)
    low[int(a.shape[0] * 0.7):, :] = True
    boots = protect & low
    lost = int((boots & (out[:, :, 3] == 0)).sum())
    layer = np.zeros_like(rgba)
    layer[shadow] = rgba[shadow]
    return out, layer, {"shadowPixels": int(shadow.sum()), "bootPixelsLost": lost, "bootPixels": int(boots.sum())}


def halo_correction(rgba: np.ndarray):
    a = rgba[:, :, 3]
    rgb = rgba[:, :, :3].astype(np.int16)
    pink = (
        (a > 16)
        & (rgb[:, :, 0] > 140)
        & (rgb[:, :, 2] > 100)
        & (rgb[:, :, 0] > rgb[:, :, 1] + 25)
        & (rgb[:, :, 2] > rgb[:, :, 1] + 15)
    )
    from scipy import ndimage
    core = ndimage.binary_erosion((a > 16) & ~pink, iterations=6)
    clear = pink & ~core
    out = rgba.copy()
    out[clear, 3] = 0
    lost = int((core & (out[:, :, 3] == 0)).sum())
    return out, {"pinkCleared": int(clear.sum()), "coreLost": lost}


def mound_correction(rgba: np.ndarray):
    a = rgba[:, :, 3] > 16
    rgb = rgba[:, :, :3].astype(np.int16)
    lum = rgb.mean(2)
    chroma = rgb.max(2) - rgb.min(2)
    snow = a & (lum > 155) & (chroma < 30)
    body = a & ~snow
    from scipy import ndimage
    body_d = ndimage.binary_dilation(body, iterations=2)
    lab, _n = ndimage.label(snow & ~body_d)
    mound = np.zeros(a.shape, bool)
    chosen = None
    for i in range(1, int(lab.max()) + 1):
        ys, xs = np.where(lab == i)
        if not (800 < len(ys) < 80000):
            continue
        if ys.mean() < 1100:
            continue
        mound[lab == i] = True
        chosen = {"pixels": int(len(ys)), "crop": [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]}
    out = rgba.copy()
    if chosen:
        out[mound, 3] = 0
    return out, chosen


def knight_correction():
    thigh = load_rgba(ROOT / "assets/derivatives/rigs/v4/knight/thigh_plate_left.png")
    greave = load_rgba(ROOT / "assets/derivatives/rigs/v4/knight/greave_left.png")
    pc = cuff_profile(thigh[:, :, 3], "distal")
    cc = cuff_profile(greave[:, :, 3], "proximal")
    cuff_w = max(pc["width"], cc["width"])
    ph, pw = thigh.shape[:2]
    ch, cw = greave.shape[:2]
    pad = int(max(pw, ph, cw, ch) * 1.2)
    canvas = (ph + ch + pad, pw + cw + pad)
    pivot = (canvas[1] // 2, canvas[0] // 2 + int(0.45 * cuff_w))
    parent_joint = (pc["cx"], pc["y"])
    child_joint = (cc["cx"], cc["y"])
    parent_layer = warp_part(thigh, parent_joint, (canvas[1] // 2, canvas[0] // 2), 0, 1.0, canvas)
    child_layer = warp_part(greave, child_joint, pivot, 0, 1.0, canvas)
    count, span = overlap_span(parent_layer[:, :, 3], child_layer[:, :, 3], pivot, cuff_w)
    merged = child_layer.copy()
    cover = parent_layer[:, :, 3] > 16
    merged[cover] = parent_layer[cover]
    trimmed, _box = trim(merged)
    path = QA / "joints" / "knight_thigh_greave_correction_0.png"
    digest = save_rgba(path, trimmed)
    return {
        "pair": "knight_thigh_greave",
        "correction": "insertion 0.45 of measured cuff after the 12-placement search still left a visible gap",
        "spanPx": span,
        "overlapPx": count,
        "evidence": str(path.relative_to(ROOT)).replace("\\", "/"),
        "sha256": digest,
        "cuffParent": pc,
        "cuffChild": cc,
    }


def corrections():
    extra = {}
    torso = RIG / "healer" / "torso.png"
    extra["healerTorsoFragment"] = drop_edge_fragment(torso)
    print("torso", extra["healerTorsoFragment"])
    extra["knightCorrection"] = knight_correction()
    print("knight correction", extra["knightCorrection"]["spanPx"], extra["knightCorrection"]["overlapPx"])
    for aid, src, seed, lum_min, chroma, protect in [
        ("troop-medieval-melee", "assets/derivatives/actors/v5/troop-medieval-melee.png", (0, 1440, 120, 1750), 110, 35, 85),
        ("troop-industrial-melee", "assets/derivatives/actors/v5/troop-industrial-melee.png", (0, 1780, 200, 1960), 70, 18, 55),
    ]:
        cleaned, layer, meta = shadow_correction(src, aid, seed, lum_min, chroma, protect)
        qa_path = QA / "actors" / f"{aid}-candidate-b.png"
        save_rgba(qa_path, cleaned)
        sheet3(cleaned, 64, QA / "actors" / f"{aid}-candidate-b-64.png")
        extra[aid] = {**meta, "qa": str(qa_path.relative_to(ROOT)).replace("\\", "/")}
        if meta["bootPixelsLost"] == 0 and meta["shadowPixels"] > 2000:
            path = ACT / f"{aid}.png"
            digest = save_rgba(path, cleaned)
            save_rgba(ACT / f"{aid}-shadow-optional.png", layer)
            extra[aid]["shipped"] = str(path.relative_to(ROOT)).replace("\\", "/")
            extra[aid]["sha256"] = digest
        print(aid, meta)
    heavy = load_rgba(ROOT / "assets/derivatives/actors/v4/troop-modern-heavy.png")
    heavy_b, heavy_meta = halo_correction(heavy)
    save_rgba(QA / "actors" / "troop-modern-heavy-candidate-b.png", heavy_b)
    Image.fromarray(heavy_b).crop((700, 80, 1450, 700)).save(QA / "actors" / "troop-modern-heavy-helmet-b.png")
    sheet3(heavy_b, 64, QA / "actors" / "troop-modern-heavy-b-64.png")
    extra["modernHeavyB"] = heavy_meta
    print("halo", heavy_meta)
    ranged = load_rgba(ROOT / "assets/derivatives/actors/v4/troop-modern-ranged.png")
    mound, chosen = mound_correction(ranged)
    extra["mound"] = chosen
    if chosen:
        path = ACT / "troop-modern-ranged-snow-mound-trimmed.png"
        digest = save_rgba(path, mound)
        sheet3(mound, 64, QA / "actors" / "troop-modern-ranged-mound-64.png")
        Image.fromarray(mound).crop((700, 1050, 1500, 1600)).save(QA / "actors" / "troop-modern-ranged-mound-detail.png")
        extra["moundPath"] = str(path.relative_to(ROOT)).replace("\\", "/")
        extra["moundSha"] = digest
    print("mound", chosen)
    (QA / "corrections.json").write_text(json.dumps(extra, indent=2), encoding="utf-8")


def main():
    QA.mkdir(parents=True, exist_ok=True)
    (QA / "recipes").mkdir(parents=True, exist_ok=True)
    report = {"version": "v6-local-solution-20261004", "providerCalls": 0}
    healer_src = NATIVE / "rig-source-parts-healer.png"
    assert sha256(healer_src) == "0f576da0a5adce8ece30be32b487f58b20c7900001bfe6d31d80f8005b70aca1"
    healer = load_rgb(healer_src)
    healer_rows = []
    for name, box in [
        ("arm_long_straight_a", [25, 1060, 215, 1895]),
        ("arm_long_straight_b", [205, 1060, 385, 1895]),
        ("arm_sleeve_forearm_hand", [385, 1050, 625, 1895]),
        ("staff_arms_group", [525, 1025, 990, 2020]),
        ("torso", [1060, 20, 1570, 390]),
        ("skirt", [1090, 390, 1570, 1005]),
        ("leg_upper", [1055, 1060, 1315, 1535]),
        ("greave", [1060, 1530, 1305, 1885]),
        ("boot", [1050, 1840, 1320, 2015]),
    ]:
        healer_rows.append(healer_extract(healer, box, name))
        print("healer", name, healer_rows[-1]["opaquePixels"], healer_rows[-1]["dimensions"])
    report["healer"] = healer_rows

    paladin_src = NATIVE / "rig-source-parts-paladin.png"
    assert sha256(paladin_src) == "a6bafe602378104b1e6de8a77b900342590457a2019ed11d43fbf0a1899e7e55"
    report["paladin"] = paladin_parts(load_rgb(paladin_src))
    print("paladin", len(report["paladin"]))

    ranger_native = load_rgb(NATIVE / "rig-source-parts-ranger.png")
    assert sha256(NATIVE / "rig-source-parts-ranger.png") == "61ae71558e1ce5b744f957cc6c72ef30bb0d5efc3ab2a914f727bf79d66423f4"
    sleeve = load_rgba(ROOT / "assets/derivatives/rigs/v5/ranger/sleeve_upper_arm.png")
    vambrace = load_rgba(ROOT / "assets/derivatives/rigs/v5/ranger/vambrace_hand_open.png")
    ranger_joint = joint_search(sleeve, vambrace, "ranger_sleeve_vambrace")
    ranger_joint["parentLocate"] = locate_template(ranger_native, sleeve)
    ranger_joint["childLocate"] = locate_template(ranger_native, vambrace)
    report["rangerJoint"] = ranger_joint
    print("ranger", ranger_joint["status"], ranger_joint.get("best", {}).get("poses"))

    knight_native = load_rgb(NATIVE / "rig-source-parts-knight.png")
    assert sha256(NATIVE / "rig-source-parts-knight.png") == "6533e35255cb1def5f6d095d166ab5e89d1ad27c6d942c5d4f6a0d4ccbd9584c"
    thigh = load_rgba(ROOT / "assets/derivatives/rigs/v4/knight/thigh_plate_left.png")
    greave = load_rgba(ROOT / "assets/derivatives/rigs/v4/knight/greave_left.png")
    knight_joint = joint_search(thigh, greave, "knight_thigh_greave")
    knight_joint["parentLocate"] = locate_template(knight_native, thigh)
    knight_joint["childLocate"] = locate_template(knight_native, greave)
    report["knightJoint"] = {k: v for k, v in knight_joint.items() if k != "best"}
    report["knightJoint"]["best"] = knight_joint.get("best")
    print("knight", knight_joint["status"])

    # Actors
    actor_rows = []
    for aid, src_rel in [
        ("troop-medieval-melee", "assets/derivatives/actors/v5/troop-medieval-melee.png"),
        ("troop-industrial-melee", "assets/derivatives/actors/v5/troop-industrial-melee.png"),
    ]:
        rgba = load_rgba(ROOT / src_rel)
        cleaned, shadow, meta = separate_shadow(rgba, aid)
        if meta["bootPixelsLost"] == 0 and meta["shadowPixels"] > 500:
            path = ACT / f"{aid}.png"
            digest = save_rgba(path, cleaned)
            sp = ACT / f"{aid}-shadow-optional.png"
            save_rgba(sp, shadow)
            sheet3(cleaned, 64, QA / "actors" / f"{aid}-64.png")
            sheet3(cleaned, 130, QA / "actors" / f"{aid}-130.png")
            actor_rows.append({"id": aid, "status": "SHADOW_SEPARATED", "output": str(path.relative_to(ROOT)).replace("\\", "/"), "sha256": digest, **meta, "source": src_rel})
        else:
            actor_rows.append({"id": aid, "status": "UNRESOLVED_SHADOW_BOOT_RISK", **meta, "retained": src_rel})
        print(aid, actor_rows[-1]["status"], meta)

    heavy = load_rgba(ROOT / "assets/derivatives/actors/v4/troop-modern-heavy.png")
    heavy_out, heavy_meta = modern_heavy(heavy)
    if heavy_meta["protectedLost"] == 0 and heavy_meta["magentaCleared"] > 1000:
        path = ACT / "troop-modern-heavy.png"
        digest = save_rgba(path, heavy_out)
        sheet3(heavy_out, 64, QA / "actors" / "troop-modern-heavy-64.png")
        sheet3(heavy_out, 130, QA / "actors" / "troop-modern-heavy-130.png")
        # helmet crop for inspection
        Image.fromarray(heavy_out).crop((700, 80, 1450, 700)).save(QA / "actors" / "troop-modern-heavy-helmet.png")
        actor_rows.append({"id": "troop-modern-heavy", "status": "CANDIDATE_A", "output": str(path.relative_to(ROOT)).replace("\\", "/"), "sha256": digest, **heavy_meta, "retainedIfRejected": "assets/derivatives/actors/v4/troop-modern-heavy.png"})
    else:
        actor_rows.append({"id": "troop-modern-heavy", "status": "UNRESOLVED", **heavy_meta})
    print("modern heavy", actor_rows[-1]["status"], heavy_meta)

    ranged = load_rgba(ROOT / "assets/derivatives/actors/v4/troop-modern-ranged.png")
    mound_out, mound_meta = modern_mound(ranged)
    if mound_meta["separated"]:
        path = ACT / "troop-modern-ranged-snow-mound-trimmed.png"
        digest = save_rgba(path, mound_out)
        sheet3(mound_out, 64, QA / "actors" / "troop-modern-ranged-mound-64.png")
        actor_rows.append({"id": "troop-modern-ranged", "status": "OPTIONAL_MOUND_TRIMMED_STILL_SNOW_SCENE", "output": str(path.relative_to(ROOT)).replace("\\", "/"), "sha256": digest, **mound_meta})
    else:
        actor_rows.append({"id": "troop-modern-ranged", "status": "SNOW_SCENE_RETAINED", **mound_meta, "retained": "assets/derivatives/actors/v4/troop-modern-ranged.png"})
    print("modern ranged", actor_rows[-1]["status"], mound_meta)
    report["actors"] = actor_rows

    keep_paths = [
        "assets/derivatives/actors/v4/troop-bronze-melee.png",
        "assets/derivatives/actors/v4/troop-bronze-ranged.png",
        "assets/derivatives/actors/v4/troop-iron-ranged.png",
        "assets/derivatives/actors/v4/troop-iron-heavy.png",
        "assets/derivatives/actors/v4/troop-gunpowder-melee.png",
        "assets/derivatives/actors/v4/troop-gunpowder-ranged.png",
        "assets/derivatives/actors/v4/troop-modern-melee.png",
        "assets/derivatives/actors/v4/troop-future-melee.png",
        "assets/derivatives/actors/v4/troop-gunpowder-heavy.png",
        "assets/derivatives/actors/v4/troop-future-ranged.png",
        "assets/derivatives/mounts/v4/hero-mount-horse.png",
        "assets/derivatives/mounts/v4/hero-mount-motor-transport.png",
        "assets/derivatives/mounts/v4/hero-mount-future-transport.png",
        "assets/derivatives/actors/v4/troop-future-heavy.png",
        "assets/derivatives/actors/v5/troop-stone-heavy.png",
        "assets/derivatives/actors/v4/troop-bronze-heavy.png",
        "assets/derivatives/actors/v4/troop-medieval-heavy.png",
        "assets/derivatives/actors/v4/troop-medieval-ranged.png",
    ]
    report["extents"] = [visible_extent(ROOT / p) for p in keep_paths]
    report["contacts"] = [contact_points(ROOT / p) for p in [
        "assets/derivatives/actors/v5/troop-stone-heavy.png",
        "assets/derivatives/actors/v4/troop-bronze-heavy.png",
        "assets/derivatives/mounts/v4/hero-mount-horse.png",
    ]]

    for class_id in ("mage", "warlock", "necromancer", "barbarian"):
        src = load_rgb(NATIVE / f"rig-source-parts-{class_id}.png")
        boxes = grey_components(src, class_id)
        print(class_id, "components", len(boxes))
        report.setdefault("greyComponents", {})[class_id] = boxes[:12]

    (QA / "run-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("wrote", QA / "run-report.json")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "corrections":
        corrections()
    else:
        main()
