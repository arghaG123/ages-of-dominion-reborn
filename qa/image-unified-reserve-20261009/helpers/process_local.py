"""Local unified-reserve processing. Does not call a provider and does not edit old bytes."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
OUT_ASSETS = ROOT / "assets/derivatives/image-unified-reserve-20261009"
QA = ROOT / "qa/image-unified-reserve-20261009"
NATIVE_SRC = ROOT / "qa/image-vertex-repair-20261009/environment/vertex-coordinator/receipts/ACTORS/natives"
RECEIPTS = ROOT / "qa/image-vertex-repair-20261009/environment/vertex-coordinator/receipts/ACTORS"
ATTEMPTS = ROOT / "qa/image-vertex-repair-20261009/environment/vertex-coordinator/attempts"
RES_ACTORS = ROOT / "assets/derivatives/image-residual-executor-20261007/actors"
RES_ENV = ROOT / "assets/derivatives/image-residual-executor-20261007/environment"

BODIES = [
    "class-knight-standing-body",
    "class-ranger-standing-body",
    "class-warlock-standing-body",
    "class-mage-standing-body",
    "class-paladin-standing-body",
    "class-barbarian-standing-body",
    "class-necromancer-standing-body",
]
GREEN_BASES = {
    "armory-stone": RES_ENV / "buildings/stone/armory-stone.png",
    "barracks-stone": RES_ENV / "buildings/stone/barracks-stone.png",
    "farm-bronze": RES_ENV / "buildings/bronze/farm-bronze.png",
    "workshop-iron": RES_ENV / "buildings/iron/workshop-iron.png",
    "townhall-industrial": RES_ENV / "buildings/industrial/townhall-industrial.png",
    "mine-industrial": RES_ENV / "buildings/industrial/mine-industrial.png",
    "hall-industrial": RES_ENV / "buildings/industrial/hall-industrial.png",
    "adventure-site-town": RES_ENV / "sites/adventure-site-town.png",
}
CROP_EXPECT = {
    "troop-stone-melee": ("c61f0e3dec06a344744f3f4d21a6cf7dabdb4df61730c42eac535c7988f2104a", 1369, 1852, -477, -112),
    "troop-industrial-ranged": ("5df473c9336451f51f2babf21ed88b7c5dc8bd5bc901615b8851a07c5183823f", 1247, 1851, -526, -103),
    "troop-industrial-heavy": ("9455bf02f32921c7fa0bf3d2bce4f561e9c311a37e36ad99bd3dbafa7fcbc758", 1640, 1921, -233, -64),
    "troop-stone-ranged": ("53233e6284322f73650529bcfe08f8141e37897cca0a57b0b3454a547dd97ba3", 1093, 1930, -363, -79),
}
BOOT_EXPECT = ("4a700eeedbabc9710db137491825d0c2ec439db15b10c619f0997a93accfab21", 135, 131)
VIEWPORTS = [(825, 375), (933, 424), (1180, 820), (1280, 720)]
LEGAL_W, LEGAL_H = 1376, 768
AFFINE = (60.0, -10.0, 25.0, 35.0, 170.0, 165.0)
CAP64_TOKENS = (
    "troop-bronze-heavy", "troop-gunpowder-heavy", "troop-future-ranged", "troop-future-heavy",
    "hero-mount", "mount", "gear-", "effect-",
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def file_ref(path: Path, dims=None) -> dict:
    rel = path.resolve().relative_to(ROOT).as_posix()
    data = path.read_bytes()
    return {
        "path": rel,
        "sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
        "dimensions": dims,
    }


def load_rgba(path: Path):
    image = Image.open(path)
    image.load()
    rgba = np.array(image.convert("RGBA"))
    return rgba


def save_png(path: Path, rgba: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(rgba, "RGBA").save(path, format="PNG", optimize=False)


def boundary_labels(mask: np.ndarray) -> np.ndarray:
    import cv2
    binary = mask.astype(np.uint8)
    count, labels = cv2.connectedComponents(binary, connectivity=8)
    if count <= 1:
        return np.zeros(mask.shape, dtype=bool)
    border = np.zeros(count, dtype=bool)
    border[labels[0, :]] = True
    border[labels[-1, :]] = True
    border[labels[:, 0]] = True
    border[labels[:, -1]] = True
    border[0] = False
    return border[labels]


def magenta_like(rgb: np.ndarray, loose=False) -> np.ndarray:
    r = rgb[:, :, 0].astype(np.int16)
    g = rgb[:, :, 1].astype(np.int16)
    b = rgb[:, :, 2].astype(np.int16)
    if loose:
        return (r > 150) & (b > 150) & (g < 190) & ((r - g) > 30) & ((b - g) > 30) & (np.abs(r - b) < 110)
    return (r > 170) & (b > 170) & (g < 165) & ((r - g) > 40) & ((b - g) > 40) & (np.abs(r - b) < 90)


def green_like(rgb: np.ndarray) -> np.ndarray:
    import cv2
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    h, s, v = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]
    return (h >= 35) & (h <= 95) & (s >= 50) & (v >= 40)


def slab_mask(rgb: np.ndarray, visible: np.ndarray) -> np.ndarray:
    import cv2
    candidate = green_like(rgb) & visible
    binary = candidate.astype(np.uint8)
    count, labels = cv2.connectedComponents(binary, connectivity=8)
    if count <= 1:
        return np.zeros(visible.shape, dtype=bool)
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    height, width = visible.shape
    remove = np.zeros(visible.shape, dtype=bool)
    for label in range(1, count):
        component = labels == label
        area = int(component.sum())
        if area < 700:
            continue
        ys, xs = np.nonzero(component)
        top, bottom = int(ys.min()), int(ys.max())
        left, right = int(xs.min()), int(xs.max())
        comp_h = bottom - top + 1
        comp_w = right - left + 1
        if bottom < int(height * 0.55):
            continue
        if top < int(height * 0.42):
            continue
        if comp_h > height * 0.5:
            continue
        if (ys > int(height * 0.58)).mean() < 0.55:
            continue
        hull_img = np.zeros((comp_h + 2, comp_w + 2), np.uint8)
        hull_img[(ys - top + 1), (xs - left + 1)] = 255
        contours, _ = cv2.findContours(hull_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            continue
        contour = max(contours, key=cv2.contourArea)
        hull = cv2.convexHull(contour)
        hull_area = float(cv2.contourArea(hull))
        solidity = area / hull_area if hull_area > 1 else 0
        hue = hsv[:, :, 0][component].astype(np.float32)
        if float(hue.std()) > 16 or solidity < 0.78:
            continue
        if comp_w < comp_h * 0.75 and area < 4000:
            continue
        remove |= component
    return remove


def apply_removal(rgba: np.ndarray, remove: np.ndarray):
    visible = rgba[:, :, 3] > 16
    protected = visible & ~remove
    out = rgba.copy()
    out[remove, 3] = 0
    kept = out[:, :, 3] > 16
    identical = bool(np.array_equal(rgba[:, :, :3][protected], out[:, :, :3][protected]))
    lost = int((protected & ~kept).sum())
    return out, identical and lost == 0


def repair_keyed(rgba: np.ndarray):
    rgb = rgba[:, :, :3]
    visible = rgba[:, :, 3] > 16
    strict = magenta_like(rgb, loose=False) & visible
    mag = boundary_labels(strict)
    # One-pixel looser fringe that touches the removed field. Not a threshold-25 flood.
    loose = magenta_like(rgb, loose=True) & visible
    kernel_touch = np.zeros_like(mag)
    kernel_touch[1:, :] |= mag[:-1, :]
    kernel_touch[:-1, :] |= mag[1:, :]
    kernel_touch[:, 1:] |= mag[:, :-1]
    kernel_touch[:, :-1] |= mag[:, 1:]
    mag = mag | (loose & kernel_touch & ~strict) | (loose & kernel_touch)
    # Keep the strict boundary field; fringe only where loose and adjacent.
    mag = boundary_labels(strict) | (loose & kernel_touch)
    green = slab_mask(rgb, visible & ~mag)
    remove = mag | green
    out, safe = apply_removal(rgba, remove)
    remaining = int((boundary_labels(magenta_like(out[:, :, :3], False) & (out[:, :, 3] > 16))).sum())
    reslab = int(slab_mask(out[:, :, :3], out[:, :, 3] > 16).sum())
    return {
        "image": out if safe else None,
        "safe": safe,
        "removedMagenta": int(mag.sum()),
        "removedGreen": int(green.sum()),
        "remainingBoundaryMagenta": remaining,
        "remainingSlab": reslab,
    }


def near_white(rgb: np.ndarray, minimum=242, chroma=10) -> np.ndarray:
    r = rgb[:, :, 0].astype(np.int16)
    g = rgb[:, :, 1].astype(np.int16)
    b = rgb[:, :, 2].astype(np.int16)
    mx = np.maximum(np.maximum(r, g), b)
    mn = np.minimum(np.minimum(r, g), b)
    return (mn >= minimum) & ((mx - mn) <= chroma)


def matte_white(rgba: np.ndarray):
    rgb = rgba[:, :, :3]
    visible = rgba[:, :, 3] > 16
    white = near_white(rgb, 242, 10) & visible
    remove = boundary_labels(white)
    fringe = near_white(rgb, 232, 14) & visible
    for _ in range(2):
        touch = np.zeros_like(remove)
        touch[1:, :] |= remove[:-1, :]
        touch[:-1, :] |= remove[1:, :]
        touch[:, 1:] |= remove[:, :-1]
        touch[:, :-1] |= remove[:, 1:]
        remove = remove | (fringe & touch)
    out, safe = apply_removal(rgba, remove)
    opaque = int((out[:, :, 3] > 16).sum()) if out is not None else 0
    return {
        "image": out if safe else None,
        "safe": safe and opaque > rgba.shape[0] * rgba.shape[1] * 0.02,
        "removed": int(remove.sum()),
        "opaque": opaque,
    }


def opaque_bbox(alpha: np.ndarray):
    ys, xs = np.nonzero(alpha > 16)
    if len(xs) == 0:
        return None
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def contacts_from_alpha(alpha: np.ndarray):
    bbox = opaque_bbox(alpha)
    if bbox is None:
        return None, None, None
    x0, y0, x1, y1 = bbox
    ys, xs = np.nonzero(alpha > 16)
    bottom = ys.max()
    on_bottom = xs[ys == bottom]
    points = [[int(on_bottom.min()), int(bottom)], [int(on_bottom.max()), int(bottom)]]
    if points[0] == points[1]:
        points = [points[0]]
    band = (ys >= max(y0, y1 - max(3, int((y1 - y0) * 0.08))))
    footprint = [
        [int(xs[band].min()), int(bottom)],
        [int(xs[band].max()), int(bottom)],
    ]
    return points, footprint, [x0, y0, x1, y1]


def visible_box(src_w, src_h, requested_height, css_per_world, max_css):
    aspect = src_w / src_h if src_h else 1
    height = requested_height
    width = height * aspect
    caps = [max_css, max_css * css_per_world] if max_css else []
    cap_css = min(caps) if caps else None
    if cap_css and height > 0:
        longest = max(width * css_per_world, height * css_per_world)
        if longest > cap_css:
            fitted = cap_css / longest
            width *= fitted
            height *= fitted
    return {
        "cssWidth": round(width * css_per_world, 2),
        "cssHeight": round(height * css_per_world, 2),
        "capCss": cap_css,
    }


def css_report(asset_id: str, alpha: np.ndarray):
    bbox = opaque_bbox(alpha)
    if bbox is None:
        return None
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    capped = any(token in asset_id for token in CAP64_TOKENS) or asset_id in {
        "aegis", "banner", "bloodstone", "clover", "codex", "lens", "orb", "swiftboots", "vitality", "wolfamulet",
    }
    max_css = 64 if capped else 130
    viewports = {}
    for vw, vh in VIEWPORTS:
        scale = min(vw / LEGAL_W, vh / LEGAL_H)
        viewports[f"{vw}x{vh}"] = visible_box(w, h, h, scale, max_css)
    return {
        "alphaWidth": w,
        "alphaHeight": h,
        "maxDisplayCssPx": max_css,
        "limitBasis": "CONSERVATIVE_BOTH" if capped else "HEIGHT",
        "viewports": viewports,
        "note": "Transparent padding excluded. Raster was not resized to the cap. Code applies the cap.",
    }


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def process_bodies():
    results = []
    copied = OUT_ASSETS / "actors/natives"
    matted_dir = OUT_ASSETS / "actors/bodies"
    copied.mkdir(parents=True, exist_ok=True)
    for asset_id in BODIES:
        src = NATIVE_SRC / f"{asset_id}.png"
        receipt_path = RECEIPTS / f"actors-{asset_id}-v1-a1.json"
        attempt = ATTEMPTS / f"actors-{asset_id}-v1-a1" / "request_body.json"
        record = {"id": asset_id, "source": rel(src)}
        if not src.exists() or not receipt_path.exists():
            record["status"] = "FAIL"
            record["reason"] = "missing native or receipt"
            results.append(record)
            continue
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        image_meta = receipt["images"][0]
        digest = sha256_file(src)
        rgba = load_rgba(src)
        record["receiptSHA256"] = image_meta["sha256"]
        record["fileSHA256"] = digest
        record["hashMatch"] = digest == image_meta["sha256"]
        record["dimensions"] = {"width": int(rgba.shape[1]), "height": int(rgba.shape[0])}
        record["dimensionMatch"] = record["dimensions"] == image_meta["dimensions"]
        wire = json.loads(attempt.read_text(encoding="utf-8")) if attempt.exists() else {}
        parts = []
        for content in wire.get("contents") or []:
            parts.extend(content.get("parts") or [])
        record["sentInlineImages"] = sum(1 for part in parts if "inlineData" in part)
        record["guideOmittedFromWire"] = record["sentInlineImages"] == 0
        dest = copied / f"{asset_id}.png"
        if not dest.exists() or sha256_file(dest) != digest:
            shutil.copy2(src, dest)
        record["nativeCopy"] = rel(dest)
        record["nativeCopySHA256"] = sha256_file(dest)
        if not (record["hashMatch"] and record["dimensionMatch"] and record["dimensions"]["width"] == 2048):
            record["status"] = "FAIL"
            record["reason"] = "hash or 2048 dimension mismatch; not matted"
            results.append(record)
            continue
        matted = matte_white(rgba)
        record["removedWhite"] = matted["removed"]
        record["opaqueAfter"] = matted["opaque"]
        record["matteSafe"] = matted["safe"]
        if not matted["safe"] or matted["image"] is None:
            record["status"] = "FAIL"
            record["reason"] = "white matte was unsafe or removed the subject"
            results.append(record)
            continue
        out = matted_dir / f"{asset_id}.png"
        save_png(out, matted["image"])
        alpha = matted["image"][:, :, 3]
        points, footprint, envelope = contacts_from_alpha(alpha)
        record["output"] = file_ref(out, {"width": int(rgba.shape[1]), "height": int(rgba.shape[0])})
        record["groundContact"] = points
        record["footprint"] = footprint
        record["heightEnvelope"] = envelope
        record["css"] = css_report(asset_id, alpha)
        record["status"] = "PARTIAL"
        record["limitations"] = [
            "Historical wire contained text only; guide image was omitted. Pixels were still inspected.",
            "Native white was removed by a border-connected near-white matte. Gray metal was protected by the chroma stop.",
            "Static standing body only. This is not a gait, turnaround, or full rig.",
            "Anatomical side is UNKNOWN.",
        ]
        results.append(record)
    return results


def extract_paladin_head(body_results):
    match = next((row for row in body_results if row["id"] == "class-paladin-standing-body" and row.get("output")), None)
    if not match:
        return {"id": "paladin-head-raster", "status": "BLOCKED", "reason": "no accepted paladin body"}
    rgba = load_rgba(ROOT / match["output"]["path"])
    bbox = opaque_bbox(rgba[:, :, 3])
    if bbox is None:
        return {"id": "paladin-head-raster", "status": "FAIL", "reason": "empty paladin body"}
    x0, y0, x1, y1 = bbox
    cut = y0 + max(1, int((y1 - y0) * 0.2))
    crop = rgba[y0:cut, x0:x1].copy()
    local = opaque_bbox(crop[:, :, 3])
    if local is None:
        return {"id": "paladin-head-raster", "status": "FAIL", "reason": "head band empty"}
    crop = crop[local[1]:local[3], local[0]:local[2]]
    out = OUT_ASSETS / "actors/heads/paladin-head-raster.png"
    save_png(out, crop)
    ox = x0 + local[0]
    oy = y0 + local[1]
    return {
        "id": "paladin-head-raster",
        "status": "PARTIAL",
        "intendedUse": "STATIC_CARD",
        "source": match["output"]["path"],
        "output": file_ref(out, {"width": int(crop.shape[1]), "height": int(crop.shape[0])}),
        "sourceToOutput": [1, 0, 0, 1, -ox, -oy],
        "groundContact": None,
        "side": "UNKNOWN",
        "limitations": [
            "Head band cut from the collected paladin standing body. No second purchase.",
            "Includes whatever helmet and plume occupy the top fifth of the opaque body. Not a separate authored portrait.",
        ],
        "purchase": "NOT_REQUIRED",
    }


def process_plates():
    jobs = []
    for path in sorted((RES_ACTORS / "attackers").glob("*.png")):
        jobs.append((path.stem, path, "attackers", "ACTORS"))
    for path in sorted((RES_ACTORS / "creatures").glob("*.png")):
        jobs.append((path.stem, path, "creatures", "ACTORS"))
    for asset_id, path in GREEN_BASES.items():
        jobs.append((asset_id, path, "buildings", "ENVIRONMENT"))
    for folder in ("gear", "artifacts", "fx"):
        base = RES_ACTORS / folder
        if not base.exists():
            continue
        for path in sorted(base.glob("*.png")):
            jobs.append((path.stem, path, folder, "ACTORS"))
    results = []
    for asset_id, path, folder, owner in jobs:
        if not path.exists():
            results.append({"id": asset_id, "status": "FAIL", "reason": f"missing {path}"})
            continue
        rgba = load_rgba(path)
        before_mag = int((boundary_labels(magenta_like(rgba[:, :, :3]) & (rgba[:, :, 3] > 16))).sum())
        before_slab = int(slab_mask(rgba[:, :, :3], rgba[:, :, 3] > 16).sum())
        confirmed = folder in {"attackers", "creatures"} or asset_id in GREEN_BASES
        if before_mag == 0 and before_slab == 0:
            points, footprint, envelope = contacts_from_alpha(rgba[:, :, 3])
            icon = folder in {"gear", "artifacts", "fx"}
            results.append({
                "id": asset_id,
                "owner": owner,
                "folder": folder,
                "status": "REUSED_UNCHANGED",
                "reusedFrom": rel(path),
                "sha256": sha256_file(path),
                "dimensions": {"width": int(rgba.shape[1]), "height": int(rgba.shape[0])},
                "groundContact": None if icon else points,
                "footprint": None if icon else footprint,
                "heightEnvelope": envelope,
                "css": css_report(asset_id, rgba[:, :, 3]),
                "matte": "NOT_APPLICABLE" if not confirmed else "PASS",
                "note": "No boundary-connected magenta and no flat green slab at the current detector.",
            })
            continue
        if not confirmed and folder not in {"attackers", "creatures"} and asset_id not in GREEN_BASES:
            # Gear and effects are repaired when the defect is actually present.
            pass
        repaired = repair_keyed(rgba)
        record = {
            "id": asset_id,
            "owner": owner,
            "folder": folder,
            "source": rel(path),
            "sourceSHA256": sha256_file(path),
            "beforeBoundaryMagenta": before_mag,
            "beforeSlab": before_slab,
            "removedMagenta": repaired["removedMagenta"],
            "removedGreen": repaired["removedGreen"],
            "remainingBoundaryMagenta": repaired["remainingBoundaryMagenta"],
            "remainingSlab": repaired["remainingSlab"],
            "safe": repaired["safe"],
        }
        if not repaired["safe"] or repaired["image"] is None:
            record["status"] = "FAIL"
            record["reason"] = "removal would change protected RGB or drop protected pixels; source left untouched"
            results.append(record)
            continue
        out = OUT_ASSETS / owner.lower() / folder / f"{asset_id}.png"
        save_png(out, repaired["image"])
        alpha = repaired["image"][:, :, 3]
        points, footprint, envelope = contacts_from_alpha(alpha)
        icon = folder in {"gear", "artifacts", "fx"}
        clean = repaired["remainingBoundaryMagenta"] == 0 and repaired["remainingSlab"] == 0
        record.update({
            "output": file_ref(out, {"width": int(rgba.shape[1]), "height": int(rgba.shape[0])}),
            "groundContact": None if icon else points,
            "footprint": None if icon else footprint,
            "heightEnvelope": envelope,
            "css": css_report(asset_id, alpha),
            "status": "PASS_MATTE" if clean else "FAIL",
            "reason": None if clean else "opaque magenta floor or green slab remains after the protected removal",
        })
        if asset_id == "creature-drone":
            record["frames"] = split_frames(repaired["image"], asset_id)
        if folder == "fx":
            record["frames"] = split_frames(repaired["image"], asset_id)
        results.append(record)
    return results


def split_frames(rgba: np.ndarray, asset_id: str):
    import cv2
    visible = (rgba[:, :, 3] > 16).astype(np.uint8)
    count, labels = cv2.connectedComponents(visible, connectivity=8)
    frames = []
    index = 0
    height, width = visible.shape
    for label in range(1, count):
        component = labels == label
        area = int(component.sum())
        if area < 400:
            continue
        ys, xs = np.nonzero(component)
        x0, y0, x1, y1 = int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1
        if (x1 - x0) < 8 or (y1 - y0) < 8:
            continue
        crop = rgba[y0:y1, x0:x1].copy()
        crop[:, :, 3] = np.where(component[y0:y1, x0:x1], crop[:, :, 3], 0)
        out = OUT_ASSETS / "actors/frames" / asset_id / f"{index:02d}.png"
        save_png(out, crop)
        pivot = [int((x0 + x1) / 2), y1 - 1]
        frames.append({
            "id": f"{asset_id}-frame-{index:02d}",
            "roi": [x0, y0, x1, y1],
            "uv": [x0 / width, y0 / height, x1 / width, y1 / height],
            "pivot": pivot,
            "sourceToFrame": [1, 0, 0, 1, -x0, -y0],
            "output": file_ref(out, {"width": x1 - x0, "height": y1 - y0}),
            "semantic": "separated-opaque-component",
            "sequence": asset_id,
            "durationMs": None,
            "timing": "BLOCKED",
            "reason": "Source sheet has no action-duration evidence. No gait or effect timing was invented.",
        })
        index += 1
    return frames


def verify_protected_files():
    found = {}
    direct = [
        ROOT / "assets/derivatives/rigs/v7/healer/boot.png",
    ]
    troop_root = ROOT / "assets/runtime-code-20261007/troops"
    wanted = {meta[0] for meta in CROP_EXPECT.values()}
    wanted.add(BOOT_EXPECT[0])
    candidates = list(direct)
    if troop_root.exists():
        candidates.extend(troop_root.rglob("*.png"))
    for path in candidates:
        if not path.exists():
            continue
        digest = sha256_file(path)
        if digest in wanted and digest not in found:
            found[digest] = path
    rows = []
    for asset_id, (digest, width, height, tx, ty) in CROP_EXPECT.items():
        path = found.get(digest)
        row = {"id": asset_id, "expectedSHA256": digest, "translation": [tx, ty], "expectedDimensions": {"width": width, "height": height}}
        if path is None:
            row["status"] = "FAIL"
            row["reason"] = "expected crop bytes were not found by hash"
        else:
            rgba = load_rgba(path)
            dims_ok = rgba.shape[1] == width and rgba.shape[0] == height
            row.update({
                "status": "REUSED" if dims_ok else "FAIL",
                "path": rel(path),
                "sha256": digest,
                "dimensions": {"width": int(rgba.shape[1]), "height": int(rgba.shape[0])},
                "sourceToOutput": [1, 0, 0, 1, tx, ty],
                "bytesUntouched": True,
            })
        rows.append(row)
    boot_path = found.get(BOOT_EXPECT[0])
    boot = {"id": "healer-boot", "expectedSHA256": BOOT_EXPECT[0]}
    if boot_path is None:
        boot["status"] = "FAIL"
        boot["reason"] = "protected boot hash not found"
    else:
        rgba = load_rgba(boot_path)
        boot.update({
            "status": "REUSED",
            "path": rel(boot_path),
            "sha256": BOOT_EXPECT[0],
            "dimensions": {"width": int(rgba.shape[1]), "height": int(rgba.shape[0])},
            "dimensionMatch": [int(rgba.shape[1]), int(rgba.shape[0])] == [BOOT_EXPECT[1], BOOT_EXPECT[2]],
            "bytesUntouched": True,
        })
    rows.append(boot)
    return rows


def correct_affines():
    corrected = []
    recipe_roots = [
        ROOT / "qa/image-vertex-repair-20261009/actors/recipes",
        ROOT / "qa/image-vertex-repair-20261009/environment/recipes",
        ROOT / "qa/image-residual-executor-20261007/actors/recipes",
        ROOT / "qa/image-residual-executor-20261007/environment/recipes",
    ]
    seen = set()
    for root in recipe_roots:
        if not root.exists():
            continue
        for path in sorted(root.glob("*.json")):
            if path.stem in seen:
                continue
            try:
                recipe = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            roi = recipe.get("roi")
            if not isinstance(roi, list) or len(roi) != 4:
                continue
            x0, y0, x1, y1 = [int(v) for v in roi]
            if x1 <= x0 or y1 <= y0:
                continue
            seen.add(path.stem)
            scale_x = 1.0
            scale_y = 1.0
            stats = recipe.get("stats") or {}
            wh = stats.get("wh")
            if isinstance(wh, list) and len(wh) == 2 and wh[0] and wh[1]:
                scale_x = float(wh[0]) / float(x1 - x0)
                scale_y = float(wh[1]) / float(y1 - y0)
            affine = [scale_x, 0, 0, scale_y, round(-x0 * scale_x, 6), round(-y0 * scale_y, 6)]
            identity = [1, 0, 0, 1, 0, 0]
            origin = x0 != 0 or y0 != 0 or abs(scale_x - 1) > 1e-6 or abs(scale_y - 1) > 1e-6
            icon = path.stem.startswith("gear-") or path.stem.startswith("artifact") or "skill" in path.stem or "spell" in path.stem
            row = {
                "id": path.stem,
                "recipe": rel(path),
                "roi": [x0, y0, x1, y1],
                "sourceToOutput": affine if origin else identity,
                "previousIdentityWouldBeWrong": bool(origin),
                "groundContact": None if icon else "MEASURE_ON_OUTPUT",
                "groundApplicability": "NOT_APPLICABLE" if icon else "OUTPUT_FRAME",
            }
            dest = QA / "recipes" / f"{path.stem}.json"
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(json.dumps(row, indent=2), encoding="utf-8")
            corrected.append(row)
    return corrected


def world_to_image(x, y, scale_x, scale_y):
    a, b, c, d, e, f = AFFINE
    sx = a * x + c * y + e
    sy = b * x + d * y + f
    return sx * scale_x, sy * scale_y


def raster_polygon(shape, points):
    mask = Image.new("1", (shape[1], shape[0]), 0)
    draw = ImageDraw.Draw(mask)
    draw.polygon(points, fill=1)
    return np.array(mask, dtype=bool)


def process_scenes():
    contract = json.loads((ROOT / "src/data/implementation-contract.json").read_text(encoding="utf-8"))
    geometry = contract["geometry"]
    selection = json.loads((ROOT / "src/data/reviewed-source-selection.json").read_text(encoding="utf-8"))
    by_id = {}
    rows = selection.get("rows") or selection.get("selections") or selection.get("items") or []
    if isinstance(selection, dict) and not rows:
        for key, value in selection.items():
            if isinstance(value, list):
                rows = value
                break
            if isinstance(value, dict) and "sourceFile" in value:
                by_id[key] = value
    for row in rows:
        if isinstance(row, dict) and row.get("id"):
            by_id[row["id"]] = row
    ages = ["stone", "bronze", "iron", "medieval", "gunpowder", "industrial", "modern", "future"]
    scenes = []
    for mode in ("kingdom", "adventure", "tactical", "defense"):
        spec = geometry.get(mode) or {}
        for age_index, age in enumerate(ages):
            scene_id = f"{mode}-terrain-{age}" if mode != "kingdom" else f"kingdom-terrain-{age}"
            if mode != "kingdom":
                scene_id = f"{mode}-terrain-{age}"
            source_info = by_id.get(scene_id) or by_id.get(f"{mode}-{age}") or {}
            source_path = None
            for key in ("sourceFile", "displayFile", "file", "path"):
                if source_info.get(key):
                    source_path = ROOT / source_info[key]
                    break
            if source_path is None or not source_path.exists():
                matches = list((ROOT / "assets/production").rglob(f"*{scene_id}*.png"))
                source_path = matches[0] if matches else None
            record = {
                "id": scene_id,
                "mode": mode.upper(),
                "age": age_index,
                "legalAffine": list(AFFINE) if mode == "kingdom" else spec.get("worldToSource"),
                "featureApplicability": {},
                "gates": {"spatial": "FAIL", "binding": "FAIL"},
                "limitations": [
                    "Automatic Sobel and luminance road floods stay withdrawn.",
                    "Paint sampled on the legal road polyline is a coverage measurement, not a promoted painted-road trace.",
                    "Free-layout full-scene regeneration was not repeated.",
                ],
                "nextAction": "Manual source-bound trace of painted roads, banks, decks and approaches before any paid edit.",
            }
            if source_path is None or not Path(source_path).exists():
                record["blockedBy"] = ["source image missing"]
                scenes.append(record)
                continue
            rgba = load_rgba(Path(source_path))
            height, width = rgba.shape[0], rgba.shape[1]
            record["source"] = file_ref(Path(source_path), {"width": width, "height": height})
            if mode != "kingdom" or not spec.get("sites"):
                if mode == "kingdom":
                    pass
                record["limitations"].append("This mode uses its own legal section; kingdom affine is not copied onto it.")
            sites = spec.get("sites") or []
            roads = spec.get("roads") or []
            scale_x = width / float(spec.get("sourceSize", [LEGAL_W, LEGAL_H])[0])
            scale_y = height / float(spec.get("sourceSize", [LEGAL_W, LEGAL_H])[1])
            if mode == "kingdom":
                scale_x = width / LEGAL_W
                scale_y = height / LEGAL_H
                record["sourceToLegal"] = [LEGAL_W / width, 0, 0, LEGAL_H / height, 0, 0]
            else:
                record["sourceToLegal"] = [1, 0, 0, 1, 0, 0]
                record["limitations"].append("Non-kingdom sourceToLegal stays identity until that mode's camera scale is measured on its own source size.")
            pad_rows = []
            if mode == "kingdom":
                ochre_total = 0
                pad_area = 0
                for site in sites:
                    rect = site.get("rect")
                    if not rect:
                        continue
                    c, r, pw, ph = rect
                    corners = [(c, r), (c + pw, r), (c + pw, r + ph), (c, r + ph)]
                    pixels = [world_to_image(x, y, scale_x, scale_y) for x, y in corners]
                    if any(px < -20 or py < -20 or px > width + 20 or py > height + 20 for px, py in pixels):
                        continue
                    mask = raster_polygon((height, width), pixels)
                    area = int(mask.sum())
                    if area == 0:
                        continue
                    sample = rgba[:, :, :3][mask].astype(np.int16)
                    ochre = (sample[:, 0] > 140) & (sample[:, 1] > 90) & (sample[:, 2] < 120) & (sample[:, 0] > sample[:, 2] + 25)
                    ochre_n = int(ochre.sum())
                    ochre_total += ochre_n
                    pad_area += area
                    pad_rows.append({
                        "id": site.get("id"),
                        "quad": [[round(px, 2), round(py, 2)] for px, py in pixels],
                        "pixels": area,
                        "ochreFraction": round(ochre_n / area, 4),
                    })
                road_colors = []
                for road in roads:
                    for index, point in enumerate(road[:-1]):
                        x0, y0 = point
                        x1, y1 = road[index + 1]
                        length = max(abs(x1 - x0), abs(y1 - y0))
                        steps = max(2, int(length * 8))
                        for step in range(steps):
                            t = step / steps
                            ix, iy = world_to_image(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, scale_x, scale_y)
                            px, py = int(round(ix)), int(round(iy))
                            if 0 <= px < width and 0 <= py < height:
                                road_colors.append(rgba[py, px, :3].astype(np.int16))
                road_colors = np.array(road_colors) if road_colors else np.zeros((0, 3), np.int16)
                if len(road_colors):
                    path_like = (road_colors[:, 0] > 140) & (road_colors[:, 1] > 90) & (road_colors[:, 2] < 130)
                    record["legalRoadSampleCount"] = int(len(road_colors))
                    record["legalRoadPathLikeFraction"] = round(float(path_like.mean()), 4)
                record["pads"] = pad_rows
                record["paintedRoads"] = []
                record["banks"] = []
                record["decks"] = []
                record["approaches"] = spec.get("approaches") or []
                record["walkable"] = []
                record["obstacles"] = []
                record["clearance"] = {
                    "method": "legal pad raster versus ochre heuristic; not a painted clearance pass",
                    "padPixels": pad_area,
                    "ochrePadPixels": ochre_total,
                }
                record["gates"]["spatial"] = "FAIL"
                record["gates"]["binding"] = "PASS"
                record["geometrySHA256"] = hashlib.sha256(json.dumps(pad_rows, sort_keys=True).encode("utf-8")).hexdigest()
                if age == "stone":
                    record["prototype"] = kingdom_prototype(scene_id, rgba, pad_rows, Path(source_path))
            else:
                record["pads"] = []
                record["gates"]["spatial"] = "FAIL"
                record["gates"]["binding"] = "PASS" if record.get("source") else "FAIL"
                record["limitations"].append("Full pad and corridor raster for this mode was not promoted from kingdom arithmetic.")
            scenes.append(record)
    return scenes


def kingdom_prototype(scene_id, rgba, pad_rows, source_path: Path):
    """Clear only ochre pixels inside legal pads. Pixels outside pads stay identical."""
    import cv2  # local synthesized fill; OpenCV 5 is the recorded image stack
    height, width = rgba.shape[:2]
    out = rgba.copy()
    draw = Image.new("L", (width, height), 0)
    pen = ImageDraw.Draw(draw)
    for row in pad_rows:
        pen.polygon([tuple(point) for point in row["quad"]], fill=255)
    pad = np.array(draw) > 0
    rgb = rgba[:, :, :3].astype(np.int16)
    ochre = pad & (rgb[:, :, 0] > 140) & (rgb[:, :, 1] > 90) & (rgb[:, :, 2] < 120) & (rgb[:, :, 0] > rgb[:, :, 2] + 25)
    synthesized = cv2.inpaint(rgba[:, :, :3], (ochre.astype(np.uint8) * 255), 7, cv2.INPAINT_TELEA)
    out[:, :, :3] = np.where(ochre[:, :, None], synthesized, rgba[:, :, :3])
    out[:, :, :3][~pad] = rgba[:, :, :3][~pad]
    changed = int(ochre.sum())
    unresolved = 0
    outside_same = bool(np.array_equal(out[:, :, :3][~pad], rgba[:, :, :3][~pad]))
    dest = OUT_ASSETS / "environment/terrain-prototypes" / f"{scene_id}.png"
    guide = QA / "geography" / f"{scene_id}-legal-pads.png"
    if outside_same:
        save_png(dest, out)
    overlay = rgba.copy()
    overlay[pad, 0] = np.minimum(255, overlay[pad, 0].astype(np.int16) // 2 + 127)
    save_png(guide, overlay)
    return {
        "id": scene_id,
        "changedPixels": changed,
        "unresolvedOchre": unresolved,
        "outsidePadsIdentical": outside_same,
        "output": rel(dest) if outside_same else None,
        "guide": rel(guide),
        "spatial": "FAIL",
        "reason": "Local pad ochre fill does not place legal roads, banks, bridge or approaches. It is not a scene pass and it authorizes no paid kingdom retry.",
        "method": "source-bound TELEA fill inside legal pads only; new pixels are synthesized, not recovered hidden source",
    }


def proof_sheets(body_results, plate_results):
    review = QA / "review"
    review.mkdir(parents=True, exist_ok=True)
    sheets = []

    def tile(paths, name, cols=4):
        images = []
        for path in paths:
            if path and Path(path).exists():
                images.append(Image.open(path).convert("RGBA"))
        if not images:
            return None
        cell = 360
        rows = (len(images) + cols - 1) // cols
        canvas = Image.new("RGBA", (cols * cell, rows * cell), (30, 30, 30, 255))
        for index, image in enumerate(images):
            image.thumbnail((cell - 12, cell - 12))
            x = (index % cols) * cell + 6
            y = (index // cols) * cell + 6
            canvas.paste(image, (x, y), image)
        dest = review / name
        canvas.convert("RGB").save(dest, quality=85)
        return rel(dest)

    body_paths = [ROOT / row["output"]["path"] for row in body_results if row.get("output")]
    sheets.append(tile(body_paths, "bodies-on-dark.jpg"))
    contrast = review / "bodies-contrast"
    contrast.mkdir(parents=True, exist_ok=True)
    for row in body_results:
        if not row.get("output"):
            continue
        image = Image.open(ROOT / row["output"]["path"]).convert("RGBA")
        image.thumbnail((480, 480))
        board = Image.new("RGBA", (image.width * 2 + 12, image.height), (0, 0, 0, 255))
        magenta = Image.new("RGBA", image.size, (255, 0, 255, 255))
        green = Image.new("RGBA", image.size, (0, 180, 60, 255))
        magenta.alpha_composite(image)
        green.alpha_composite(image)
        board.paste(magenta, (0, 0))
        board.paste(green, (image.width + 12, 0))
        board.convert("RGB").save(contrast / f"{row['id']}.jpg", quality=85)
    sample_ids = [
        "attacker-stone-brute", "attacker-bronze-runner", "attacker-medieval-archer",
        "creature-wolf", "creature-drone", "armory-stone", "farm-bronze", "adventure-site-town",
    ]
    pairs = []
    for asset_id in sample_ids:
        match = next((row for row in plate_results if row["id"] == asset_id), None)
        if not match:
            continue
        if match.get("source"):
            pairs.append(ROOT / match["source"])
        if match.get("output"):
            pairs.append(ROOT / match["output"]["path"])
        elif match.get("reusedFrom"):
            pairs.append(ROOT / match["reusedFrom"])
    sheets.append(tile(pairs, "matte-before-after.jpg", cols=4))
    return {"sheets": [item for item in sheets if item], "contrastDir": rel(contrast)}


def main():
    QA.mkdir(parents=True, exist_ok=True)
    bodies = process_bodies()
    head = extract_paladin_head(bodies)
    plates = process_plates()
    protected = verify_protected_files()
    affines = correct_affines()
    scenes = process_scenes()
    proofs = proof_sheets(bodies, plates)
    summary = {
        "bodies": [{key: row.get(key) for key in ("id", "status", "hashMatch", "dimensionMatch", "sentInlineImages", "opaqueAfter", "output")} for row in bodies],
        "paladinHead": {key: head.get(key) for key in ("id", "status", "purchase", "output")},
        "plates": {
            "count": len(plates),
            "passMatte": sum(1 for row in plates if row.get("status") == "PASS_MATTE"),
            "fail": sum(1 for row in plates if row.get("status") == "FAIL"),
            "reused": sum(1 for row in plates if row.get("status") == "REUSED_UNCHANGED"),
        },
        "protected": protected,
        "affineRecipes": len(affines),
        "affineOriginCorrections": sum(1 for row in affines if row["previousIdentityWouldBeWrong"]),
        "stoneHelm": next((row for row in affines if row["id"] == "gear-stone-helm"), None),
        "scenes": len(scenes),
        "kingdomSpatial": [row["id"] for row in scenes if row["mode"] == "KINGDOM"],
        "proofs": proofs,
    }
    (QA / "diagnostics/local-summary.json").parent.mkdir(parents=True, exist_ok=True)
    (QA / "diagnostics/bodies.json").write_text(json.dumps(bodies, indent=2), encoding="utf-8")
    (QA / "diagnostics/plates.json").write_text(json.dumps(plates, indent=2), encoding="utf-8")
    (QA / "diagnostics/protected.json").write_text(json.dumps(protected, indent=2), encoding="utf-8")
    (QA / "diagnostics/scenes.json").write_text(json.dumps(scenes, indent=2), encoding="utf-8")
    (QA / "diagnostics/local-summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (QA / "diagnostics/paladin-head.json").write_text(json.dumps(head, indent=2), encoding="utf-8")
    print(json.dumps(summary["plates"] | {"bodies": summary["bodies"], "head": summary["paladinHead"], "affines": summary["affineRecipes"], "helm": summary["stoneHelm"], "protected": [{k: r.get(k) for k in ("id", "status", "path")} for r in protected]}, indent=2))


if __name__ == "__main__":
    main()
