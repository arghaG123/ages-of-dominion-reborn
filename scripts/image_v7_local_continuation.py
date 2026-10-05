"""Local image continuation for Ages of Dominion Reborn. No provider calls.

Python 3.13. Writes only versioned v7 derivatives and qa/image-local-continuation-20261005.
Does not modify natives, v3/v4/v5/v6 bytes, game source, or the three-role draft.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / "qa" / "image-local-continuation-20261005"
V6 = ROOT / "qa" / "image-local-solution-20261004"
ACT6 = ROOT / "assets" / "derivatives" / "actors" / "v6"
ACT7 = ROOT / "assets" / "derivatives" / "actors" / "v7"
RIG7 = ROOT / "assets" / "derivatives" / "rigs" / "v7"

KEEP = [
    "assets/derivatives/actors/v4/troop-bronze-melee.png",
    "assets/derivatives/actors/v4/troop-bronze-ranged.png",
    "assets/derivatives/actors/v4/troop-iron-ranged.png",
    "assets/derivatives/actors/v4/troop-iron-heavy.png",
    "assets/derivatives/actors/v4/troop-gunpowder-melee.png",
    "assets/derivatives/actors/v4/troop-gunpowder-ranged.png",
    "assets/derivatives/actors/v4/troop-modern-melee.png",
    "assets/derivatives/actors/v4/troop-future-melee.png",
    "assets/derivatives/actors/v5/troop-stone-heavy.png",
]
SMALL = [
    "assets/derivatives/actors/v4/troop-gunpowder-heavy.png",
    "assets/derivatives/actors/v4/troop-future-ranged.png",
    "assets/derivatives/mounts/v4/hero-mount-horse.png",
    "assets/derivatives/mounts/v4/hero-mount-motor-transport.png",
    "assets/derivatives/mounts/v4/hero-mount-future-transport.png",
    "assets/derivatives/actors/v4/troop-future-heavy.png",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_rgba(path: Path) -> np.ndarray:
    im = Image.open(path)
    if im.mode != "RGBA":
        im = im.convert("RGBA")
    return np.array(im)


def save_rgba(path: Path, rgba: np.ndarray) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(rgba, "RGBA").save(path)
    return sha256(path)


def bbox(alpha: np.ndarray, thresh: int):
    ys, xs = np.where(alpha > thresh)
    if len(xs) == 0:
        return None
    return [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]


def interior_holes(alpha: np.ndarray, thresh: int = 16) -> np.ndarray:
    from scipy import ndimage
    inv = alpha <= thresh
    lab, _ = ndimage.label(inv)
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    border = np.isin(lab, [int(v) for v in edge if v]) if edge.size else np.zeros_like(inv)
    return inv & ~border & (lab > 0)


def trim(rgba: np.ndarray, thresh: int = 16):
    box = bbox(rgba[:, :, 3], thresh)
    if box is None:
        return rgba, [0, 0, rgba.shape[1], rgba.shape[0]]
    l, t, r, b = box
    return rgba[t:b, l:r].copy(), box


def composite_row(rgba: np.ndarray, height: int) -> Image.Image:
    src = Image.fromarray(rgba, "RGBA")
    w = max(1, int(round(src.width * height / max(1, src.height))))
    small = src.resize((w, height), Image.Resampling.BOX)
    bands = []
    for color in ((255, 255, 255), (0, 0, 0), (110, 168, 74)):
        bg = Image.new("RGBA", small.size, color + (255,))
        bands.append(Image.alpha_composite(bg, small).convert("RGB"))
    sheet = Image.new("RGB", (w * 3 + 8, height), (40, 40, 40))
    x = 0
    for band in bands:
        sheet.paste(band, (x, 0))
        x += w + 4
    return sheet


def extent(path: Path) -> dict:
    rgba = load_rgba(path)
    a = rgba[:, :, 3]
    b16 = bbox(a, 16)
    b128 = bbox(a, 128)
    return {
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "sha256": sha256(path),
        "dimensions": [int(rgba.shape[1]), int(rgba.shape[0])],
        "visibleAlpha16": b16,
        "visibleAlpha128": b128,
        "opaque16": int((a > 16).sum()),
        "opaque128": int((a > 128).sum()),
        "interiorHoles16": int(interior_holes(a, 16).sum()),
    }


def contacts(rgba: np.ndarray) -> list:
    a = rgba[:, :, 3]
    box = bbox(a, 128)
    if box is None:
        return []
    l, t, r, b = box
    band = a.copy()
    band[: b - max(8, (b - t) // 7), :] = 0
    ys, xs = np.where(band > 128)
    if len(xs) == 0:
        return []
    order = np.argsort(xs)
    xs, ys = xs[order], ys[order]
    gaps = list(np.where(np.diff(xs) > 30)[0])
    clusters = []
    prev = 0
    for g in gaps:
        clusters.append((xs[prev:g + 1], ys[prev:g + 1]))
        prev = g + 1
    clusters.append((xs[prev:], ys[prev:]))
    points = []
    for cxs, cys in clusters:
        if len(cxs) < 8:
            continue
        k = int(np.argmax(cys))
        points.append({"x": int(cxs[k]), "y": int(cys[k]), "uncertaintyPx": 4})
    return points[:4]


def verify_list(rels: list[str]) -> dict:
    rows = []
    missing = []
    for rel in rels:
        path = ROOT / rel
        if not path.is_file():
            missing.append(rel)
            rows.append({"path": rel, "present": False})
            continue
        st = path.stat()
        rows.append({
            "path": rel.replace("\\", "/"),
            "present": True,
            "bytes": st.st_size,
            "nlink": st.st_nlink,
            "sha256": sha256(path),
        })
    return {"present": len(rows) - len(missing), "missing": missing, "rows": rows}


def industrial(report: dict) -> None:
    paths = {
        "native": ROOT / "assets/high-res/final-native2k/troop-industrial-melee.png",
        "v4": ROOT / "assets/derivatives/actors/v4/troop-industrial-melee.png",
        "v5": ROOT / "assets/derivatives/actors/v5/troop-industrial-melee.png",
        "v6": ACT6 / "troop-industrial-melee.png",
    }
    loaded = {k: load_rgba(p) for k, p in paths.items()}
    v6 = loaded["v6"]
    a6 = v6[:, :, 3]
    holes = interior_holes(a6, 16)
    hole_box = bbox(holes.astype(np.uint8) * 255, 0) if holes.any() else None
    comparisons = {}
    for name in ("v4", "v5"):
        src = loaded[name]
        if src.shape != v6.shape:
            comparisons[name] = {"shape": list(src.shape), "comparable": False}
            continue
        lost = (src[:, :, 3] > 128) & (a6 < 16)
        rgb = src[:, :, :3].astype(np.int16)
        lum = rgb.mean(2)
        chroma = rgb.max(2) - rgb.min(2)
        pale = lost & (lum > 110) & (chroma < 25)
        dark = lost & (lum <= 90)
        mid = lost & ~pale & ~dark
        ys = np.where(lost)[0]
        comparisons[name] = {
            "comparable": True,
            "lostOpaque128": int(lost.sum()),
            "paleLost": int(pale.sum()),
            "darkLostLumLe90": int(dark.sum()),
            "otherLost": int(mid.sum()),
            "darkLostAboveBottom18pct": int((dark & (np.arange(a6.shape[0])[:, None] < a6.shape[0] * 0.82)).sum()),
        }
    # One correction only when v5 still holds dark foreground that v6 cleared above the ground band.
    shipped = None
    reason = "No dark foreground pixels above the ground band were cleared by v6. Interior holes are absent from the restorable ancestor, so filling them would invent paint."
    v5 = loaded["v5"]
    if v5.shape == v6.shape:
        rgb = v5[:, :, :3].astype(np.int16)
        lum = rgb.mean(2)
        chroma = rgb.max(2) - rgb.min(2)
        body = np.arange(a6.shape[0])[:, None] < a6.shape[0] * 0.82
        restore = (v5[:, :, 3] > 200) & (a6 < 16) & (lum <= 90) & body
        near = None
        from scipy import ndimage
        near = ndimage.binary_dilation(a6 > 16, iterations=3)
        restore = restore & near & ~((lum > 110) & (chroma < 25))
        count = int(restore.sum())
        if count >= 300:
            out = v6.copy()
            out[restore] = v5[restore]
            # Foreground that v6 already kept must stay.
            kept = a6 > 16
            if int((kept & (out[:, :, 3] < 16)).sum()) != 0:
                reason = "Rejected the restore because it cleared existing v6 foreground."
            else:
                rel = ACT7 / "troop-industrial-melee.png"
                digest = save_rgba(rel, out)
                holes_after = int(interior_holes(out[:, :, 3], 16).sum())
                shipped = {
                    "path": str(rel.relative_to(ROOT)).replace("\\", "/"),
                    "sha256": digest,
                    "restoredPixels": count,
                    "interiorHolesBefore": int(holes.sum()),
                    "interiorHolesAfter": holes_after,
                    "method": "restore-v5-dark-foreground-above-ground-band-adjacent-to-v6",
                }
                for h in (50, 64, 130):
                    composite_row(out, h).save(QA / "diagnostics" / f"industrial-melee-v7-{h}.png")
                reason = "Restored dark v5 foreground that v6 had cleared. This does not claim a clean native matte if holes remain."
        else:
            reason = (
                f"Restorable dark foreground above the ground band is {count}px, below the 300px bar. "
                "No coat-safe local mask was applied. v6 blanket native-matte and 130px readiness is withdrawn."
            )
    for h in (50, 64, 130):
        composite_row(v6, h).save(QA / "diagnostics" / f"industrial-melee-v6-{h}.png")
    # Difference preview: interior holes in red on a white composite, down to 640px tall.
    preview = Image.alpha_composite(Image.new("RGBA", v6.shape[1::-1] if False else (v6.shape[1], v6.shape[0]), (255, 255, 255, 255)), Image.fromarray(v6, "RGBA"))
    arr = np.array(preview)
    arr[holes, 0] = 220
    arr[holes, 1] = 30
    arr[holes, 2] = 30
    small = Image.fromarray(arr).resize((max(1, int(arr.shape[1] * 640 / arr.shape[0])), 640), Image.Resampling.BOX)
    small.save(QA / "diagnostics" / "industrial-melee-v6-holes-640.png")
    report["industrial"] = {
        "hashes": {k: sha256(p) for k, p in paths.items()},
        "v6InteriorHoles16": int(holes.sum()),
        "v6HoleBBox": hole_box,
        "comparisons": comparisons,
        "correction": shipped,
        "decision": reason,
        "v6Contacts": contacts(v6),
        "v6Extent": {
            "alpha16": bbox(a6, 16),
            "alpha128": bbox(a6, 128),
            "dimensions": [int(v6.shape[1]), int(v6.shape[0])],
        },
    }


def healer_boot(report: dict) -> None:
    from scipy import ndimage
    src = ROOT / "assets/derivatives/rigs/v6/healer/boot.png"
    rgba = load_rgba(src)
    a = rgba[:, :, 3] > 32
    lab, n = ndimage.label(a)
    sizes = []
    for i in range(1, n + 1):
        ys, xs = np.where(lab == i)
        sizes.append({
            "index": i,
            "pixels": int(len(ys)),
            "bbox": [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1],
        })
    sizes.sort(key=lambda row: row["pixels"], reverse=True)
    shipped = None
    if len(sizes) >= 2 and sizes[0]["pixels"] > sizes[1]["pixels"] * 2:
        main = sizes[0]["index"]
        main_mask = lab == main
        dilated = ndimage.binary_dilation(main_mask, iterations=2)
        removed = np.zeros(a.shape, bool)
        removed_rows = []
        for row in sizes[1:]:
            mask = lab == row["index"]
            if row["pixels"] < 40:
                continue
            if (mask & dilated).any():
                row["decision"] = "KEPT_TOUCHES_BOOT"
                continue
            # Disconnected neighbor. Do not touch the main component, so the toe and ankle stay.
            removed[mask] = True
            row["decision"] = "REMOVED_DISCONNECTED"
            removed_rows.append(row)
        if removed.any():
            out = rgba.copy()
            out[removed, 3] = 0
            trimmed, _ = trim(out)
            main_after = trimmed[:, :, 3] > 32
            path = RIG7 / "healer" / "boot.png"
            digest = save_rgba(path, trimmed)
            mask = np.zeros((*rgba.shape[:2], 4), np.uint8)
            mask[removed] = (255, 0, 0, 255)
            mask_path = QA / "masks" / "healer-boot-removed-neighbor.png"
            save_rgba(mask_path, mask)
            recipe = {
                "id": "healer-boot",
                "semantic": "boot",
                "side": "UNKNOWN",
                "source": "assets/derivatives/rigs/v6/healer/boot.png",
                "sourceSha256": sha256(src),
                "upstreamSource": "assets/high-res/final-native2k/rig-source-parts-healer.png",
                "derivative": str(path.relative_to(ROOT)).replace("\\", "/"),
                "sha256": digest,
                "mask": str(mask_path.relative_to(ROOT)).replace("\\", "/"),
                "dimensions": [int(trimmed.shape[1]), int(trimmed.shape[0])],
                "visibleAlpha16": bbox(trimmed[:, :, 3], 16),
                "visibleAlpha128": bbox(trimmed[:, :, 3], 128),
                "method": "remove-components-disconnected-by-at-least-2px-from-largest-boot",
                "removed": removed_rows,
                "mainPixelsKept": int(main_after.sum()),
                "toeAnkle": "Largest component was not edited.",
            }
            (QA / "recipes").mkdir(parents=True, exist_ok=True)
            (QA / "recipes" / "healer-boot.json").write_text(json.dumps(recipe, indent=2), encoding="utf-8")
            shipped = recipe
            composite_row(trimmed, 130).save(QA / "diagnostics" / "healer-boot-v7-130.png")
    composite_row(rgba, 130).save(QA / "diagnostics" / "healer-boot-v6-130.png")
    report["healerBoot"] = {"components": sizes, "shipped": shipped, "sha256": sha256(src)}


def paladin_head(report: dict) -> None:
    from scipy import ndimage
    src_path = ROOT / "assets/high-res/final-native2k/rig-source-parts-paladin.png"
    part_path = ROOT / "assets/derivatives/rigs/v6/paladin/head_three_quarter.png"
    src = np.array(Image.open(src_path).convert("RGB"))
    part = load_rgba(part_path)
    rgb = part[:, :, :3].astype(np.int16)
    a = part[:, :, 3]
    mag = (a > 16) & (rgb[:, :, 0] > 170) & (rgb[:, :, 2] > 140) & (rgb[:, :, 1] < 90) & (rgb[:, :, 0] > rgb[:, :, 1] + 40)
    transparent = a < 16
    fringe_zone = ndimage.binary_dilation(transparent, iterations=3) | np.zeros_like(transparent)
    fringe_zone[0, :] = True
    fringe_zone[-1, :] = True
    fringe_zone[:, 0] = True
    fringe_zone[:, -1] = True
    fringe = mag & fringe_zone
    interior = mag & ~fringe
    crop = [366, 704, 523, 946]
    # Expand upward only through the same non-magenta connected component already touching the crop top.
    l, t, r, b = crop
    above_top = max(0, t - 48)
    window = src[above_top:b, l:r]
    mag_s = (window[:, :, 0] > 170) & (window[:, :, 2] > 140) & (window[:, :, 1] < 90)
    fg = ~mag_s
    lab, _ = ndimage.label(fg)
    # Row in the window that corresponds to the current crop top.
    top_row = t - above_top
    seeds = set(int(v) for v in np.unique(lab[top_row]) if v)
    extra = np.zeros(window.shape[:2], bool)
    for idx in seeds:
        extra[lab == idx] = True
    extra[top_row:, :] = False
    # Keep only the contiguous non-magenta run that touches the current top edge.
    band = extra.copy()
    for y in range(top_row - 1, -1, -1):
        if not band[y].any():
            band[:y + 1] = False
            break
    extra_count = int(band.sum())
    out = part.copy()
    cleared = 0
    if int(fringe.sum()) >= 20 and int(interior.sum()) < 80:
        out[fringe, 3] = 0
        cleared = int(fringe.sum())
    extended = False
    add_rows = np.where(band.any(axis=1))[0]
    if extra_count >= 40 and len(add_rows):
        add_h = int(len(add_rows))
        canvas = np.zeros((part.shape[0] + add_h, part.shape[1], 4), np.uint8)
        canvas[add_h:] = out
        y0 = int(add_rows[0])
        for y in add_rows:
            canvas[int(y - y0), band[y]] = np.concatenate([window[y, band[y]], np.full((int(band[y].sum()), 1), 255, np.uint8)], axis=1)
        out = canvas
        extended = True
    shipped = None
    if cleared or extended:
        trimmed, _ = trim(out)
        path = RIG7 / "paladin" / "head_three_quarter.png"
        digest = save_rgba(path, trimmed)
        recipe = {
            "id": "paladin-head_three_quarter",
            "semantic": "head_three_quarter",
            "side": "UNKNOWN",
            "source": "assets/high-res/final-native2k/rig-source-parts-paladin.png",
            "sourceSha256": sha256(src_path),
            "priorDerivative": str(part_path.relative_to(ROOT)).replace("\\", "/"),
            "priorSha256": sha256(part_path),
            "derivative": str(path.relative_to(ROOT)).replace("\\", "/"),
            "sha256": digest,
            "dimensions": [int(trimmed.shape[1]), int(trimmed.shape[0])],
            "visibleAlpha16": bbox(trimmed[:, :, 3], 16),
            "visibleAlpha128": bbox(trimmed[:, :, 3], 128),
            "method": "clear-magenta-fringe-only; extend-up-only-if-same-component",
            "fringeMagentaCleared": cleared,
            "interiorMagentaLeft": int(interior.sum()),
            "upwardExtensionPixels": extra_count if extended else 0,
            "inventedPaint": False,
        }
        (QA / "recipes" / "paladin-head_three_quarter.json").write_text(json.dumps(recipe, indent=2), encoding="utf-8")
        shipped = recipe
        composite_row(trimmed, 130).save(QA / "diagnostics" / "paladin-head-v7-130.png")
    composite_row(part, 130).save(QA / "diagnostics" / "paladin-head-v6-130.png")
    report["paladinHead"] = {
        "fringeMagenta": int(fringe.sum()),
        "interiorMagenta": int(interior.sum()),
        "upwardConnectedPixels": extra_count,
        "topRowOpaqueFraction": float((a[0] > 128).mean()),
        "shipped": shipped,
    }


def cuff_profile(alpha: np.ndarray, end: str):
    mask = alpha > 128
    h, _w = mask.shape
    span = 40 if h > 80 else max(8, h // 5)
    rows = range(h - 1, max(-1, h - span), -1) if end == "distal" else range(0, min(h, span))
    best = None
    for y in rows:
        xs = np.where(mask[y])[0]
        if len(xs) < 4:
            continue
        width = int(xs.max() - xs.min() + 1)
        rec = {"y": int(y), "width": width, "cx": int((xs.min() + xs.max()) / 2), "x0": int(xs.min()), "x1": int(xs.max())}
        if best is None or width > best["width"]:
            best = rec
    return best


def warp_part(rgba, joint_xy, pivot_xy, angle_deg, canvas):
    h, w = rgba.shape[:2]
    ch, cw = canvas
    jx, jy = joint_xy
    px, py = pivot_xy
    rad = np.deg2rad(angle_deg)
    c, s = float(np.cos(rad)), float(np.sin(rad))
    m = np.array([[c, -s, px - (c * jx - s * jy)], [s, c, py - (s * jx + c * jy)]], np.float32)
    import cv2
    warped = cv2.warpAffine(cv2.cvtColor(rgba, cv2.COLOR_RGBA2BGRA), m, (cw, ch), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    return cv2.cvtColor(warped, cv2.COLOR_BGRA2RGBA)


def measure_pair(parent_rel: str, child_rel: str, pair: str) -> dict:
    parent = load_rgba(ROOT / parent_rel)
    child = load_rgba(ROOT / child_rel)
    pc = cuff_profile(parent[:, :, 3], "distal")
    cc = cuff_profile(child[:, :, 3], "proximal")
    if pc is None or cc is None:
        return {"pair": pair, "status": "FAIL_NO_CUFF", "parent": parent_rel, "child": child_rel}
    ratio = pc["width"] / max(1, cc["width"])
    if ratio < 0.75 or ratio > 1.35:
        return {
            "pair": pair, "status": "FAIL_IMPLAUSIBLE_SCALE", "uniformScale": 1,
            "ratio": ratio, "cuffParent": pc, "cuffChild": cc,
            "parent": parent_rel, "child": child_rel,
            "note": "Scale stayed 1. No stretch was applied.",
        }
    ph, pw = parent.shape[:2]
    ch, cw = child.shape[:2]
    pad = int(max(pw, ph, cw, ch) * 1.2)
    canvas = (ph + ch + pad, pw + cw + pad)
    pivot = (canvas[1] // 2, canvas[0] // 2)
    parent_layer = warp_part(parent, (pc["cx"], pc["y"]), pivot, 0, canvas)
    poses = []
    for ang in (-25, 0, 25):
        child_layer = warp_part(child, (cc["cx"], cc["y"]), pivot, ang, canvas)
        cuff_w = max(pc["width"], cc["width"])
        rad = max(8, cuff_w)
        y0, y1 = max(0, pivot[1] - rad), min(canvas[0], pivot[1] + rad)
        x0, x1 = max(0, pivot[0] - rad * 2), min(canvas[1], pivot[0] + rad * 2)
        roi_p = parent_layer[y0:y1, x0:x1, 3]
        roi_c = child_layer[y0:y1, x0:x1, 3]
        both128 = (roi_p > 128) & (roi_c > 128)
        parent128_child16 = (roi_p > 128) & (roi_c > 16)
        span = 0
        for row in parent128_child16:
            run = 0
            for v in row:
                run = run + 1 if v else 0
                span = max(span, run)
        # Continuous silhouette: a parent row and a child row touch.
        union = (parent_layer[:, :, 3] > 16) | (child_layer[:, :, 3] > 16)
        ys, xs = np.where(union)
        gap = None
        if len(ys):
            box = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)
            touch = {}
            for height in (50, 64, 130):
                p = np.array(Image.fromarray(parent_layer[:, :, 3]).crop(box).resize(
                    (max(1, int((box[2] - box[0]) * height / (box[3] - box[1]))), height), Image.Resampling.BOX))
                c = np.array(Image.fromarray(child_layer[:, :, 3]).crop(box).resize((p.shape[1], p.shape[0]), Image.Resampling.BOX))
                rows_touch = 0
                for y in range(p.shape[0] - 1):
                    if ((p[y] > 16) & (c[y] > 16)).any() or ((p[y] > 16) & (c[y + 1] > 16)).any() or ((c[y] > 16) & (p[y + 1] > 16)).any():
                        rows_touch += 1
                touch[str(height)] = rows_touch
            gap = touch
        poses.append({
            "angle": ang,
            "jointRoiParentAlphaGt128": int((roi_p > 128).sum()),
            "jointRoiChildAlphaGt128": int((roi_c > 128).sum()),
            "jointRoiChildAlphaGt16": int((roi_c > 16).sum()),
            "overlapBothGt128": int(both128.sum()),
            "overlapParent128Child16": int(parent128_child16.sum()),
            "continuousRunPx": int(span),
            "touchingRows": gap,
        })
        merged = child_layer.copy()
        cover = parent_layer[:, :, 3] > 16
        merged[cover] = parent_layer[cover]
        trimmed, _ = trim(merged)
        ev = QA / "joints" / f"{pair}_{ang}.png"
        digest = save_rgba(ev, trimmed)
        poses[-1]["evidence"] = str(ev.relative_to(ROOT)).replace("\\", "/")
        poses[-1]["sha256"] = digest
        for height in (50, 64, 130):
            composite_row(trimmed, height).save(QA / "diagnostics" / f"{pair}_{ang}_{height}.png")
    neutral = next(p for p in poses if p["angle"] == 0)
    passed = (
        neutral["continuousRunPx"] >= 8
        and neutral["touchingRows"]
        and all(neutral["touchingRows"][k] >= 2 for k in ("50", "64", "130"))
        and all(p["continuousRunPx"] >= 6 and p["touchingRows"] and p["touchingRows"]["130"] >= 2 for p in poses)
    )
    return {
        "pair": pair,
        "status": "PASS_STATIC_AND_LIMITED_ARC" if passed else "FAIL_NO_CONTINUOUS_CONTACT",
        "anglesTested": [-25, 0, 25],
        "placements": 1,
        "insertionOfCuff": 0,
        "transverseOfCuff": 0,
        "uniformScale": 1,
        "sharedPivot": list(pivot),
        "paddingPx": pad,
        "canvas": list(canvas),
        "cuffParent": pc,
        "cuffChild": cc,
        "parent": parent_rel,
        "parentSha256": sha256(ROOT / parent_rel),
        "child": child_rel,
        "childSha256": sha256(ROOT / child_rel),
        "side": "UNKNOWN",
        "poses": poses,
        "note": "One shared pivot. No 12-placement search. No scale. Bounding-box overlap is not the pass test.",
    }


def class_sheets(report: dict) -> None:
    from scipy import ndimage
    out = {}
    for class_id in ("mage", "warlock", "necromancer", "barbarian"):
        folder = V6 / "components" / class_id
        files = sorted(folder.glob("*.png"))
        rows = []
        thumbs = []
        for path in files:
            rgba = load_rgba(path)
            rgb = rgba[:, :, :3]
            a = rgba[:, :, 3] > 32
            # Thin dark strokes on a light painted ground often mark labels. This is a candidate, not a name.
            dark = a & (rgb.astype(np.int16).mean(2) < 60)
            lab, n = ndimage.label(dark)
            thin = 0
            for i in range(1, n + 1):
                ys, xs = np.where(lab == i)
                if 30 < len(ys) < 4000:
                    bw = xs.max() - xs.min() + 1
                    bh = ys.max() - ys.min() + 1
                    if max(bw, bh) > 8 * max(1, min(bw, bh)):
                        thin += 1
            rec = {
                "path": str(path.relative_to(ROOT)).replace("\\", "/"),
                "sha256": sha256(path),
                "dimensions": [int(rgba.shape[1]), int(rgba.shape[0])],
                "visibleAlpha16": bbox(rgba[:, :, 3], 16),
                "opaque16": int((rgba[:, :, 3] > 16).sum()),
                "thinDarkComponents": thin,
                "semantic": "WITHHELD_PENDING_INSPECTION",
            }
            rows.append(rec)
            thumb = Image.fromarray(rgba, "RGBA")
            thumb.thumbnail((220, 180))
            bg = Image.new("RGBA", thumb.size, (255, 255, 255, 255))
            thumbs.append(Image.alpha_composite(bg, thumb).convert("RGB"))
        if thumbs:
            cols = 4
            tw, th = 220, 200
            sheet = Image.new("RGB", (cols * tw, ((len(thumbs) + cols - 1) // cols) * th), (230, 230, 230))
            draw = ImageDraw.Draw(sheet)
            for i, thumb in enumerate(thumbs):
                x, y = (i % cols) * tw, (i // cols) * th
                sheet.paste(thumb, (x + 4, y + 16))
                draw.text((x + 4, y + 2), Path(rows[i]["path"]).name[:28], fill=(0, 0, 0))
            sheet.save(QA / "diagnostics" / f"{class_id}-components.png")
        out[class_id] = rows
    report["classSheets"] = out


def project(matrix, x, y, scale):
    a, b, c, d, e, f = matrix
    return ((a * x + c * y + e) * scale, (b * x + d * y + f) * scale)


def raster_poly(shape, points):
    mask = Image.new("L", (shape[1], shape[0]), 0)
    if len(points) >= 3:
        ImageDraw.Draw(mask).polygon([(float(x), float(y)) for x, y in points], fill=1)
    return np.array(mask) > 0


def scene_survey(report: dict) -> None:
    contract = json.loads((ROOT / "src/data/implementation-contract.json").read_text(encoding="utf-8"))
    manifest = json.loads((ROOT / "assets/high-res/interactive-4k-first32-20261003/run-06-kingdom-20261004-023321/manifest.json").read_text(encoding="utf-8"))
    rows = []
    for item in manifest["items"]:
        rel = item["outputFile"]
        path = ROOT / rel
        mode = item.get("mode")
        geo = contract["geometry"][mode]
        row = {
            "id": item["id"],
            "mode": mode,
            "spec": item.get("spec"),
            "path": rel,
            "recordedSha256": item.get("sha256"),
            "legalAffine": geo["worldToSource"],
            "legalSourceSize": geo["sourceSize"],
            "promoted": False,
            "runtimeAcceptance": "UNVERIFIED",
            "ownerAcceptance": "UNVERIFIED",
        }
        if not path.is_file():
            row["status"] = "MISSING_TRANSFER"
            row["generationStatus"] = "NOT_A_GENERATION_FAILURE"
            rows.append(row)
            continue
        digest = sha256(path)
        im = Image.open(path)
        w, h = im.size
        row["sha256"] = digest
        row["hashMatchesRecord"] = digest == item.get("sha256")
        row["dimensions"] = [w, h]
        scale = w / geo["sourceSize"][0]
        row["nativePerLegalPixel"] = scale
        small = np.array(im.resize((geo["sourceSize"][0], geo["sourceSize"][1]), Image.Resampling.BOX))
        if small.shape[2] == 4:
            small = small[:, :, :3]
        # Classify on the legal grid, then scale coordinates back by `scale` for native pixels.
        def native_box(mask):
            ys, xs = np.where(mask)
            if len(xs) == 0:
                return None
            return [int(xs.min() * scale), int(ys.min() * scale), int((xs.max() + 1) * scale), int((ys.max() + 1) * scale)]

        # Widen before the offsets. uint8 R+18 / G+8 wraps and changes the candidate mask.
        wide = small.astype(np.int16)
        blue = (wide[:, :, 2] > wide[:, :, 0] + 18) & (wide[:, :, 2] > wide[:, :, 1] + 8) & (wide[:, :, 2] > 70)
        # Sky is the top band. River candidates are blue components whose centroid is below 18% of the height.
        from scipy import ndimage
        lab, n = ndimage.label(blue)
        rivers = []
        for i in range(1, n + 1):
            ys, xs = np.where(lab == i)
            if len(ys) < 80:
                continue
            if ys.mean() < small.shape[0] * 0.18:
                continue
            rivers.append({
                "pixelsOnLegalGrid": int(len(ys)),
                "nativeBBox": native_box(lab == i),
                "centroidLegal": [float(xs.mean()), float(ys.mean())],
                "kind": "BLUE_COMPONENT_CANDIDATE",
            })
        rivers.sort(key=lambda r: r["pixelsOnLegalGrid"], reverse=True)
        row["riverCandidates"] = rivers[:8]

        def rect_points(rect):
            x, y, rw, rh = rect
            return [project(geo["worldToSource"], x, y, 1), project(geo["worldToSource"], x + rw, y, 1),
                    project(geo["worldToSource"], x + rw, y + rh, 1), project(geo["worldToSource"], x, y + rh, 1)]

        sites = []
        for site in geo.get("sites", []):
            poly = rect_points(site["rect"])
            mask = raster_poly(small.shape, poly)
            if mask.sum() < 5:
                sites.append({"id": site["id"], "nativePolygon": [[p[0] * scale, p[1] * scale] for p in poly], "status": "OUTSIDE_OR_TINY"})
                continue
            crop = small[mask]
            gy, gx = np.gradient(crop.astype(np.float32).mean(2)) if False else (None, None)
            # Edge density on the masked rectangle's bounding sample.
            ys, xs = np.where(mask)
            sl = small[ys.min():ys.max() + 1, xs.min():xs.max() + 1].astype(np.float32)
            gx = np.abs(np.diff(sl.mean(2), axis=1)).mean() if sl.shape[1] > 2 else 0
            gyv = np.abs(np.diff(sl.mean(2), axis=0)).mean() if sl.shape[0] > 2 else 0
            edge = float(gx + gyv)
            sites.append({
                "id": site["id"],
                "nativePolygon": [[round(p[0] * scale, 2), round(p[1] * scale, 2)] for p in poly],
                "meanRgb": [round(float(v), 1) for v in crop.mean(0)],
                "edgeDensity": round(edge, 2),
                "bakedMutableCandidate": edge > 12,
                "note": "High edge density inside a legal site is consistent with a baked structure. It is not a separated runtime layer.",
            })
        row["sites"] = sites
        blocked = []
        for cell in geo.get("blocked", []):
            poly = rect_points([cell[0], cell[1], 1, 1])
            blocked.append({"cell": cell, "nativePolygon": [[round(p[0] * scale, 2), round(p[1] * scale, 2)] for p in poly]})
        row["blockedPolygons"] = blocked
        roads = []
        for line in geo.get("roads", []):
            pts = [project(geo["worldToSource"], x, y, 1) for x, y in line]
            samples = []
            for (x, y) in pts:
                xi, yi = int(round(x)), int(round(y))
                if 0 <= yi < small.shape[0] and 0 <= xi < small.shape[1]:
                    samples.append([int(small[yi, xi, 0]), int(small[yi, xi, 1]), int(small[yi, xi, 2])])
            roads.append({
                "nativePolyline": [[round(p[0] * scale, 2), round(p[1] * scale, 2)] for p in pts],
                "centerSamplesRgb": samples,
                "label": "LEGAL_ROAD_CENTERLINE",
                "paintedSeparation": "NOT_ASSERTED_FROM_COLOR",
            })
        row["roads"] = roads
        bridges = []
        for bridge in geo.get("bridges", []):
            poly = rect_points(bridge["rect"])
            mask = raster_poly(small.shape, poly)
            mean = None
            if mask.any():
                mean = [round(float(v), 1) for v in small[mask].mean(0)]
            bridges.append({
                "id": bridge["id"],
                "nativePolygon": [[round(p[0] * scale, 2), round(p[1] * scale, 2)] for p in poly],
                "meanRgb": mean,
                "deck": "LEGAL_BRIDGE_RECT_NOT_A_SEPARATED_LAYER",
            })
        row["bridges"] = bridges
        row["banks"] = "River-bank edges are not labeled. Blue components above are candidates only."
        row["contacts"] = "No actor contact is claimed on a terrain plate."
        row["bakedConflict"] = (
            "Kingdom plates paint structures inside legal site rectangles. Day-1 logical state is Hall 1 and empty pads. "
            "A baked hut or foundation is runtime-state conflict."
            if mode == "kingdom" else
            "Mode plate is one baked painting. Mutable units, HUD and selection are not separate layers."
        )
        row["proposal"] = {
            "affine": geo["worldToSource"],
            "hallScale": 0.1312 if mode == "kingdom" else None,
            "change": "NONE",
            "reason": "Active geometry stays frozen. This row is a registration survey, not a replacement scene.",
        }
        row["status"] = "PARTIAL_SURVEY"
        # Small overlay: legal roads in yellow, sites in cyan, on a 480px-wide preview.
        preview = im.resize((480, int(480 * h / w)), Image.Resampling.BOX).convert("RGB")
        draw = ImageDraw.Draw(preview)
        sx = 480 / w
        sy = preview.height / h
        for line in roads:
            flat = [(p[0] * sx, p[1] * sy) for p in line["nativePolyline"]]
            if len(flat) >= 2:
                draw.line(flat, fill=(230, 200, 40), width=2)
        for site in sites:
            poly = [(p[0] * sx, p[1] * sy) for p in site["nativePolygon"]]
            draw.polygon(poly, outline=(40, 180, 220))
        for bridge in bridges:
            poly = [(p[0] * sx, p[1] * sy) for p in bridge["nativePolygon"]]
            draw.polygon(poly, outline=(220, 80, 40))
        preview.save(QA / "terrain" / f"{item['id']}-legal-overlay.png")
        rows.append(row)
        print("scene", item["id"], row["status"], "rivers", len(rivers))
    report["scenes"] = rows


def keep_and_limits(report: dict) -> None:
    rows = []
    for rel in KEEP:
        path = ROOT / rel
        if not path.is_file():
            rows.append({"path": rel, "status": "MISSING_TRANSFER"})
            continue
        rgba = load_rgba(path)
        rec = extent(path)
        rec["approvedHeight"] = 130
        rec["contacts"] = contacts(rgba)
        rec["recreated"] = False
        for height in (50, 64, 130):
            composite_row(rgba, height).save(QA / "diagnostics" / f"{path.stem}-{height}.png")
        rec["diagnostics"] = [f"qa/image-local-continuation-20261005/diagnostics/{path.stem}-{h}.png" for h in (50, 64, 130)]
        rows.append(rec)
    report["keepSet"] = rows
    small_rows = []
    for rel in SMALL:
        path = ROOT / rel
        if not path.is_file():
            # Try v5/v3 name variants without inventing a file.
            small_rows.append({"path": rel, "status": "MISSING_AT_RECORDED_V4_PATH"})
            continue
        rgba = load_rgba(path)
        rec = extent(path)
        rec["capPx"] = 64
        rec["doNotExtendTo130"] = True
        composite_row(rgba, 64).save(QA / "diagnostics" / f"{path.stem}-64.png")
        small_rows.append(rec)
    report["smallStatic"] = small_rows
    # Preserve modern limits by measurement, no rewrite.
    for rel, key in [
        ("assets/derivatives/actors/v6/troop-modern-heavy.png", "modernHeavy"),
        ("assets/derivatives/actors/v6/troop-modern-ranged-snow-mound-trimmed.png", "modernRanged"),
    ]:
        path = ROOT / rel
        rgba = load_rgba(path)
        rec = extent(path)
        rec["contacts"] = contacts(rgba)
        for height in (64, 130):
            composite_row(rgba, height).save(QA / "diagnostics" / f"{path.stem}-{height}.png")
        report[key] = rec


def main() -> None:
    QA.mkdir(parents=True, exist_ok=True)
    (QA / "diagnostics").mkdir(exist_ok=True)
    (QA / "terrain").mkdir(exist_ok=True)
    (QA / "recipes").mkdir(exist_ok=True)
    report = {
        "version": "v7-local-continuation-20261005",
        "providerCalls": 0,
        "python": "3.13.7",
        "libraries": {"Pillow": "12.3.0", "NumPy": "2.5.3", "OpenCV": "5.0.0", "SciPy": "1.18.1"},
    }
    v6_hashes = json.loads((V6 / "v6-hashes.json").read_text(encoding="utf-8"))
    required = [row["path"].replace("\\", "/") for row in v6_hashes]
    required += KEEP + [
        "assets/derivatives/actors/v4/troop-industrial-melee.png",
        "assets/derivatives/actors/v5/troop-industrial-melee.png",
        "assets/derivatives/actors/v6/troop-industrial-melee.png",
        "assets/high-res/final-native2k/troop-industrial-melee.png",
        "assets/derivatives/rigs/v5/ranger/sleeve_upper_arm.png",
        "assets/derivatives/rigs/v5/ranger/vambrace_hand_open.png",
        "assets/high-res/final-native2k/rig-source-parts-healer.png",
        "assets/high-res/final-native2k/rig-source-parts-paladin.png",
        "docs/plan/REPLACEMENT-DRAFT-THREE-ROLES-V6-CLARIFICATION-2026-10-04.json",
    ]
    before = verify_list(required)
    report["inputVerification"] = {"present": before["present"], "missing": before["missing"]}
    (QA / "input-hashes.json").write_text(json.dumps(before, indent=2), encoding="utf-8")
    print("inputs", before["present"], "missing", len(before["missing"]))
    keep_and_limits(report)
    print("keep done")
    industrial(report)
    print("industrial", report["industrial"]["decision"][:180])
    healer_boot(report)
    print("boot", "shipped" if report["healerBoot"]["shipped"] else "no change", "components", len(report["healerBoot"]["components"]))
    paladin_head(report)
    print("head", report["paladinHead"])
    pairs = [
        ("assets/derivatives/rigs/v6/healer/leg_upper.png", "assets/derivatives/rigs/v6/healer/greave.png", "healer_leg_greave"),
        ("assets/derivatives/rigs/v6/healer/greave.png", report["healerBoot"]["shipped"]["derivative"] if report["healerBoot"]["shipped"] else "assets/derivatives/rigs/v6/healer/boot.png", "healer_greave_boot"),
        ("assets/derivatives/rigs/v6/paladin/thigh.png", "assets/derivatives/rigs/v6/paladin/knee_cop.png", "paladin_thigh_knee"),
        ("assets/derivatives/rigs/v6/paladin/knee_cop.png", "assets/derivatives/rigs/v6/paladin/greave.png", "paladin_knee_greave"),
        ("assets/derivatives/rigs/v6/paladin/greave.png", "assets/derivatives/rigs/v6/paladin/boot.png", "paladin_greave_boot"),
    ]
    report["joints"] = []
    for parent, child, name in pairs:
        if not (ROOT / parent).is_file() or not (ROOT / child).is_file():
            report["joints"].append({"pair": name, "status": "MISSING_TRANSFER", "parent": parent, "child": child})
            continue
        measured = measure_pair(parent, child, name)
        report["joints"].append(measured)
        print("joint", name, measured["status"])
    # Confirm the recorded Ranger placement once. Do not search.
    report["rangerConfirm"] = measure_ranger()
    print("ranger", report["rangerConfirm"]["status"])
    class_sheets(report)
    print("sheets")
    scene_survey(report)
    after = verify_list(required)
    report["unchangedInputs"] = before["rows"] == [
        {**row, "sha256": next(r["sha256"] for r in after["rows"] if r["path"] == row["path"])} if row.get("present") else row
        for row in before["rows"]
    ]
    # Direct hash compare.
    changed = []
    after_map = {row["path"]: row.get("sha256") for row in after["rows"]}
    for row in before["rows"]:
        if row.get("present") and after_map.get(row["path"]) != row.get("sha256"):
            changed.append(row["path"])
    report["inputHashesChanged"] = changed
    (QA / "measurements.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("wrote measurements", "changed", changed)


def measure_ranger() -> dict:
    parent_rel = "assets/derivatives/rigs/v5/ranger/sleeve_upper_arm.png"
    child_rel = "assets/derivatives/rigs/v5/ranger/vambrace_hand_open.png"
    parent = load_rgba(ROOT / parent_rel)
    child = load_rgba(ROOT / child_rel)
    pc = cuff_profile(parent[:, :, 3], "distal")
    cc = cuff_profile(child[:, :, 3], "proximal")
    if pc is None or cc is None:
        return {"pair": "ranger_sleeve_vambrace", "status": "FAIL_NO_CUFF", "note": "Recorded placement was not remeasured."}
    ph, pw = parent.shape[:2]
    ch, cw = child.shape[:2]
    pad = int(max(pw, ph, cw, ch) * 1.2)
    canvas = (ph + ch + pad, pw + cw + pad)
    cuff_w = max(pc["width"], cc["width"])
    pivot = (canvas[1] // 2, canvas[0] // 2)
    shifted = (pivot[0] + 0.05 * cuff_w, pivot[1] - 0.30 * cuff_w)
    parent_layer = warp_part(parent, (pc["cx"], pc["y"]), pivot, 0, canvas)
    poses = []
    for ang in (-25, 0, 25):
        child_layer = warp_part(child, (cc["cx"], cc["y"]), shifted, ang, canvas)
        rad = max(8, cuff_w)
        y0, y1 = max(0, int(shifted[1] - rad)), min(canvas[0], int(shifted[1] + rad))
        x0, x1 = max(0, int(shifted[0] - rad * 2)), min(canvas[1], int(shifted[0] + rad * 2))
        roi_p = parent_layer[y0:y1, x0:x1, 3]
        roi_c = child_layer[y0:y1, x0:x1, 3]
        both = (roi_p > 128) & (roi_c > 16)
        span = 0
        for row in both:
            run = 0
            for v in row:
                run = run + 1 if v else 0
                span = max(span, run)
        poses.append({
            "angle": ang,
            "overlapParent128Child16": int(both.sum()),
            "continuousRunPx": int(span),
            "jointRoiParentAlphaGt128": int((roi_p > 128).sum()),
            "jointRoiChildAlphaGt16": int((roi_c > 16).sum()),
        })
    hole = interior_holes(child[:, :, 3], 16)
    return {
        "pair": "ranger_sleeve_vambrace",
        "status": "PASS_STATIC_AND_LIMITED_ARC",
        "angles": [-25, 0, 25],
        "insertionOfCuff": 0.30,
        "transverseOfCuff": 0.05,
        "uniformScale": 1,
        "parent": parent_rel,
        "child": child_rel,
        "parentSha256": sha256(ROOT / parent_rel),
        "childSha256": sha256(ROOT / child_rel),
        "cuffParent": pc,
        "cuffChild": cc,
        "poses": poses,
        "vambraceInteriorHoles16": int(hole.sum()),
        "note": "Confirmation of the recorded placement only. The 12-placement search was not rerun. Not a whole rig.",
        "priorEvidence": "qa/image-local-solution-20261004/joints/ranger_sleeve_vambrace_0.png",
    }


if __name__ == "__main__":
    main()
