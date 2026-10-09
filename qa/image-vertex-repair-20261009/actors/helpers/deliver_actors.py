"""Image AI 2 local actor repair and Vertex pack publication. No provider calls."""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

ROOT = Path(r"C:\dev\ages-of-dominion-reborn")
QA = ROOT / "qa/image-vertex-repair-20261009/actors"
DERIV = ROOT / "assets/derivatives/image-vertex-repair-20261009/actors"
RESIDUAL = ROOT / "docs/plan/ACTORS-EQUIPMENT-RESIDUAL-INTERFACE-2026-10-07.json"
UPPER_USD = 0.40
SPENDABLE_USD = 8.8844
COMMITTED_USD = 71.1156

CODE_REUSE = {
    "troop-stone-melee": {
        "output": "assets/runtime-code-20261007/troops/troop-stone-melee.png",
        "sha": "c61f0e3dec06a344744f3f4d21a6cf7dabdb4df61730c42eac535c7988f2104a",
        "wh": (1369, 1852),
        "affine": [1, 0, 0, 1, -477, -112],
        "source": "assets/high-res/final-native2k/troop-stone-melee.png",
        "source_sha": "9d6d0afb631ca748a31de2f8f33c77f8236a138954fe2d9cf79d607c7911b488",
        "cap": 130,
    },
    "troop-industrial-ranged": {
        "output": "assets/runtime-code-20261007/troops/troop-industrial-ranged.png",
        "sha": "5df473c9336451f51f2babf21ed88b7c5dc8bd5bc901615b8851a07c5183823f",
        "wh": (1247, 1851),
        "affine": [1, 0, 0, 1, -526, -103],
        "source": "assets/high-res/final-native2k/troop-industrial-ranged.png",
        "source_sha": "6e72795f5e73feda122521d85c6ae23a10350ed839e07a852a6d24460600a37c",
        "cap": 130,
    },
    "troop-industrial-heavy": {
        "output": "assets/runtime-code-20261007/troops/troop-industrial-heavy.png",
        "sha": "9455bf02f32921c7fa0bf3d2bce4f561e9c311a37e36ad99bd3dbafa7fcbc758",
        "wh": (1640, 1921),
        "affine": [1, 0, 0, 1, -233, -64],
        "source": "assets/high-res/final-native2k/troop-industrial-heavy.png",
        "source_sha": "4662db518ad44d0dd24507bbd36d064b4cbc825aea455843e724750f3d4ec5e2",
        "cap": 130,
    },
}

CAP64 = {
    "troop-bronze-heavy",
    "troop-gunpowder-heavy",
    "troop-future-ranged",
    "troop-future-heavy",
    "hero-mount-horse",
    "hero-mount-motor-transport",
    "hero-mount-future-transport",
    "knight-mounted-master",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_rgba(path: Path) -> np.ndarray:
    return np.array(Image.open(path).convert("RGBA"))


def border_mask(h: int, w: int, t: int = 2) -> np.ndarray:
    m = np.zeros((h, w), dtype=bool)
    m[:t, :] = m[-t:, :] = m[:, :t] = m[:, -t:] = True
    return m


def flood_border(cand: np.ndarray) -> np.ndarray:
    lab, n = ndimage.label(cand)
    if n == 0:
        return np.zeros_like(cand)
    edge = lab[border_mask(*cand.shape)]
    ids = [int(x) for x in np.unique(edge) if x]
    if not ids:
        return np.zeros_like(cand)
    return np.isin(lab, ids)


def pink_mask(arr: np.ndarray) -> np.ndarray:
    rgb = arr[:, :, :3].astype(np.int16)
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    a = arr[:, :, 3] > 16
    return (
        a
        & (r > g + 28)
        & (b > g + 10)
        & (g < 160)
        & (r > 80)
        & (b > 45)
        & ((r - b) < 120)
    )


def slinger_subject(arr: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    rgb = arr[:, :, :3]
    r, g, b = [rgb[:, :, i].astype(np.int16) for i in range(3)]
    chroma = np.maximum(np.maximum(r, g), b) - np.minimum(np.minimum(r, g), b)
    val = (r.astype(np.float32) + g + b) / 3.0
    baseline_bg = flood_border((chroma <= 12) & (val >= 196))
    strict = (chroma <= 8) & (val >= 210)
    lab, n = ndimage.label(strict)
    edge_ids = set(int(x) for x in np.unique(lab[border_mask(*strict.shape)]) if x)
    extra = np.zeros(strict.shape, dtype=bool)
    for i in range(1, n + 1):
        if i in edge_ids:
            continue
        comp = lab == i
        area = int(comp.sum())
        if area < 400:
            continue
        extra |= comp
    corrected_bg = baseline_bg | extra
    return ~baseline_bg, ~corrected_bg


def backdrop_subject(arr: np.ndarray, tol: int = 12) -> np.ndarray | None:
    rgb = arr[:, :, :3].astype(np.int16)
    h, w = rgb.shape[:2]
    edge = border_mask(h, w)
    med = np.median(rgb[edge].reshape(-1, 3), axis=0)
    dist = np.max(np.abs(rgb - med.reshape(1, 1, 3)), axis=2)
    cand = dist <= tol
    if cand[edge].mean() < 0.85:
        return None
    bg = flood_border(cand)
    if bg[edge].mean() < 0.9:
        return None
    subject = ~bg
    if arr[:, :, 3].min() < 250:
        subject &= arr[:, :, 3] > 16
    return subject


def defringe_magenta(arr: np.ndarray) -> np.ndarray:
    rgb = arr[:, :, :3].astype(np.int16)
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    a = arr[:, :, 3]
    mag = (a > 16) & (r > 110) & (b > 110) & (g < 25) & (np.abs(r - b) < 50)
    if mag.sum() == 0 or mag.mean() > 0.02:
        return arr
    near_clear = ndimage.binary_dilation(a <= 16, iterations=2) | border_mask(*a.shape, 1)
    kill = mag & near_clear
    if kill.sum() == 0:
        return arr
    out = arr.copy()
    out[:, :, 3] = np.where(kill, 0, a)
    return out


def crop_subject(arr: np.ndarray, subject: np.ndarray) -> tuple[np.ndarray, list[int]]:
    ys, xs = np.where(subject)
    if len(xs) == 0:
        raise RuntimeError("empty subject")
    x0, x1, y0, y1 = int(xs.min()), int(xs.max()) + 1, int(ys.min()), int(ys.max()) + 1
    cropped = arr[y0:y1, x0:x1].copy()
    mask = subject[y0:y1, x0:x1]
    if cropped.shape[2] == 4:
        cropped[:, :, 3] = np.where(mask, np.maximum(cropped[:, :, 3], 255), 0)
    return cropped, [x0, y0, x1, y1]


def save_png(arr: np.ndarray, path: Path) -> dict:
    path.parent.mkdir(parents=True, exist_ok=True)
    im = Image.fromarray(arr, "RGBA")
    im.save(path, optimize=True)
    return file_ref(path)


def file_ref(path: Path) -> dict:
    with Image.open(path) as im:
        w, h = im.size
    return {"path": rel(path), "sha256": sha256_file(path), "bytes": path.stat().st_size, "dimensions": {"width": w, "height": h}}


def preview(arr: np.ndarray, path: Path, color=(0, 150, 0)) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    im = Image.fromarray(arr, "RGBA")
    scale = 480 / max(im.size)
    small = im.resize((max(1, int(im.size[0] * scale)), max(1, int(im.size[1] * scale))), Image.Resampling.BOX)
    bg = Image.new("RGBA", small.size, (*color, 255))
    Image.alpha_composite(bg, small).convert("RGB").save(path, quality=72)


def alpha_stats(arr: np.ndarray) -> dict:
    a = arr[:, :, 3] > 16
    h, w = a.shape
    ys, xs = np.where(a)
    if len(xs) == 0:
        return {"opaque": 0, "border": 1, "bbox": None, "components": 0}
    x0, x1, y0, y1 = int(xs.min()), int(xs.max()) + 1, int(ys.min()), int(ys.max()) + 1
    crop = a[y0:y1, x0:x1]
    lab, n = ndimage.label(a)
    sizes = ndimage.sum(a, lab, range(1, n + 1)) if n else []
    big = int((np.array(sizes) > 800).sum()) if n else 0
    return {
        "opaque": round(float(a.mean()), 4),
        "border": round(float(a[border_mask(h, w)].mean()), 4),
        "bbox": [x0, y0, x1, y1],
        "cropFill": round(float(crop.mean()), 4),
        "components": int(n),
        "bigComponents": big,
        "wh": [w, h],
    }


def contact_points(arr: np.ndarray) -> list[list[float]] | None:
    a = arr[:, :, 3] > 32
    ys, xs = np.where(a)
    if len(xs) == 0:
        return None
    yb = int(ys.max())
    band = a[max(0, yb - 2): yb + 1]
    cols = np.where(band.any(axis=0))[0]
    if len(cols) == 0:
        return None
    return [[float(cols.min()), float(yb)], [float(cols.max()), float(yb)]]


def visible_box(width: int, height: int, cap: int, css_per_world: float = 1.0) -> dict:
    aspect = width / height if height else 1
    req_h = float(height)
    req_w = req_h * aspect
    longest = max(req_w * css_per_world, req_h * css_per_world)
    fitted = cap / longest if longest > cap else 1.0
    width_u = req_w * fitted
    height_u = req_h * fitted
    return {
        "cssWidth": round(width_u * css_per_world, 3),
        "cssHeight": round(height_u * css_per_world, 3),
        "capCss": cap,
        "longestWithinCap": max(width_u * css_per_world, height_u * css_per_world) <= cap + 0.01,
    }


def use_for(row: dict, kind: str) -> str:
    role = row.get("role")
    if kind == "atlas":
        return "ATLAS_FRAME"
    if role in ("missing-link-diagram",):
        return "REFERENCE_ONLY"
    if role == "joint-pair" and row.get("output") is None and kind != "image":
        return "JOINT_METADATA"
    if role == "gear-icon" or role == "artifact-icon":
        return "MATERIAL"
    if role == "fx-sprite":
        return "ATLAS_FRAME" if kind == "atlas" else "SPRITE"
    if kind == "card":
        return "STATIC_CARD"
    if role in ("static-head-card", "mount") and kind == "card":
        return "STATIC_CARD"
    return "SPRITE"


def write_snapshot(rows_src: list) -> dict:
    paths = [
        "docs/plan/ACTORS-EQUIPMENT-RESIDUAL-INTERFACE-2026-10-07.json",
        "docs/plan/IMAGE-REGENERATION-AUTHORITY-AND-BLOCKER-RECOVERY-2026-10-09.md",
        "docs/plan/image-production/budget-ledger.json",
        "src/data/plate-overrides-20261007.json",
        "src/client/visible-size.js",
        "assets/derivatives/rigs/v7/healer/boot.png",
    ]
    for spec in CODE_REUSE.values():
        paths.append(spec["output"])
        paths.append(spec["source"])
    paths.append("assets/high-res/final-native2k/troop-stone-ranged.png")
    snap = {}
    for p in paths:
        fp = ROOT / p
        if fp.exists():
            snap[p.replace("\\", "/")] = {"sha256": sha256_file(fp), "bytes": fp.stat().st_size}
    (QA / "input_snapshot.json").write_text(json.dumps({"capturedAt": datetime.now(timezone.utc).isoformat(), "files": snap}, indent=2), encoding="utf-8")
    return snap


def largest_components(arr: np.ndarray, min_area: int = 1500, limit: int = 16) -> list[dict]:
    a = arr[:, :, 3] > 32
    lab, n = ndimage.label(a)
    if n == 0:
        return []
    sizes = [(int(ndimage.sum(a, lab, i)), i) for i in range(1, n + 1)]
    sizes.sort(reverse=True)
    frames = []
    for area, i in sizes:
        if area < min_area or len(frames) >= limit:
            break
        comp = lab == i
        ys, xs = np.where(comp)
        x0, x1, y0, y1 = int(xs.min()), int(xs.max()) + 1, int(ys.min()), int(ys.max()) + 1
        w, h = x1 - x0, y1 - y0
        semantic = "standing-figure-candidate" if h > w * 1.4 and area > 8000 else "sheet-component"
        frames.append({"area": area, "roi": [x0, y0, x1, y1], "semantic": semantic, "wh": [w, h]})
    frames.sort(key=lambda f: (f["roi"][1], f["roi"][0]))
    return frames


def main() -> None:
    QA.mkdir(parents=True, exist_ok=True)
    for sub in ("helpers", "recipes", "masks", "diagnostics", "assemblies", "composites", "review", "regeneration/packs", "source-roi"):
        (QA / sub).mkdir(parents=True, exist_ok=True)
    iface = json.loads(RESIDUAL.read_text(encoding="utf-8"))
    snap = write_snapshot(iface["rows"])
    repairs = []
    new_outputs = {}

    # Slinger baseline then one correction.
    native_path = ROOT / "assets/high-res/final-native2k/troop-stone-ranged.png"
    native = load_rgba(native_path)
    base_sub, fix_sub = slinger_subject(native)
    base_crop, base_box = crop_subject(native, base_sub)
    fix_crop, fix_box = crop_subject(native, fix_sub)
    base_ref = save_png(base_crop, DERIV / "troops/troop-stone-ranged-baseline.png")
    fix_ref = save_png(fix_crop, DERIV / "troops/troop-stone-ranged.png")
    mask_img = np.zeros(native.shape[:2], np.uint8)
    mask_img[fix_sub] = 255
    Image.fromarray(mask_img, "L").save(QA / "masks/troop-stone-ranged-mask.png")
    preview(base_crop, QA / "diagnostics/troop-stone-ranged-baseline-green.jpg", (0, 150, 0))
    preview(fix_crop, QA / "diagnostics/troop-stone-ranged-green.jpg", (0, 150, 0))
    preview(fix_crop, QA / "diagnostics/troop-stone-ranged-black.jpg", (0, 0, 0))
    preview(fix_crop, QA / "diagnostics/troop-stone-ranged-white.jpg", (255, 255, 255))
    small = Image.fromarray(fix_crop, "RGBA")
    cap_side = 130
    scale = cap_side / max(small.size)
    small.resize((max(1, int(small.size[0] * scale)), max(1, int(small.size[1] * scale))), Image.Resampling.LANCZOS).save(QA / "diagnostics/troop-stone-ranged-130.png")
    slinger_stats = alpha_stats(fix_crop)
    recipe = {
        "id": "troop-stone-ranged",
        "method": "neutral-light checker border flood, then one correction removing enclosed chroma<=8 value>=210 components of area>=400",
        "forbidden": "floating-range flood fill tolerance 25",
        "baseline": base_ref,
        "baselineRoi": base_box,
        "correction": fix_ref,
        "sourceRoi": fix_box,
        "stats": slinger_stats,
    }
    (QA / "recipes/troop-stone-ranged.json").write_text(json.dumps(recipe, indent=2), encoding="utf-8")
    new_outputs["troop-stone-ranged"] = {
        "ref": fix_ref,
        "affine": [1, 0, 0, 1, -fix_box[0], -fix_box[1]],
        "source_roi": fix_box,
        "kind": "sprite",
        "status": "READY" if slinger_stats["border"] < 0.01 and slinger_stats["cropFill"] > 0.35 else "PARTIAL",
        "matte": "PASS" if slinger_stats["border"] < 0.01 else "PARTIAL",
        "limitations": [
            "Checker removed from native 937949e3 by a neutral-light border flood plus one enclosed-component correction.",
            "Side UNKNOWN. Static standing plate. Not a gait.",
            f"Alpha crop fill {slinger_stats['cropFill']}, border opaque {slinger_stats['border']}.",
        ],
        "recipe": "qa/image-vertex-repair-20261009/actors/recipes/troop-stone-ranged.json",
    }
    print("SLINGER", slinger_stats, new_outputs["troop-stone-ranged"]["status"])

    # Pink gear and any other gear whose border is the same slab.
    for row in iface["rows"]:
        if row["role"] not in ("gear-icon", "artifact-icon"):
            continue
        src = row.get("output") or {}
        if not src.get("path"):
            continue
        path = ROOT / src["path"]
        arr = load_rgba(path)
        pink = pink_mask(arr)
        edge = border_mask(*pink.shape)
        edge_pink = float(pink[edge].mean()) if edge.any() else 0
        if edge_pink < 0.05 and int(pink.sum()) < 500:
            arr2 = defringe_magenta(arr)
            if arr2 is not arr and not np.array_equal(arr2[:, :, 3], arr[:, :, 3]):
                cropped, box = crop_subject(arr2, arr2[:, :, 3] > 16)
                ref = save_png(cropped, DERIV / "gear" / f"{row['id']}.png")
                new_outputs[row["id"]] = {
                    "ref": ref,
                    "affine": [1, 0, 0, 1, -box[0], -box[1]],
                    "source_roi": box,
                    "kind": "sprite",
                    "status": "READY",
                    "matte": "PASS",
                    "limitations": ["Magenta fringe pixels touching transparency were cleared. Subject RGB unchanged."],
                    "recipe": None,
                }
            continue
        subject = (arr[:, :, 3] > 16) & ~pink
        if subject.mean() < 0.04:
            print("PINK SKIP empty", row["id"])
            continue
        cropped, box = crop_subject(arr, subject)
        st = alpha_stats(cropped)
        ref = save_png(cropped, DERIV / "gear" / f"{row['id']}.png")
        preview(cropped, QA / "diagnostics" / f"{row['id']}-green.jpg")
        status = "READY" if st["border"] < 0.02 and st["cropFill"] > 0.25 else "PARTIAL"
        new_outputs[row["id"]] = {
            "ref": ref,
            "affine": [1, 0, 0, 1, -box[0], -box[1]],
            "source_roi": box,
            "kind": "sprite",
            "status": status,
            "matte": "PASS" if status == "READY" else "PARTIAL",
            "limitations": [
                "Pink slab cleared by a fixed pink predicate (R>G+28, B>G+10, G<160). Subject colors kept.",
                f"Border opaque after crop {st['border']}.",
            ],
            "recipe": None,
        }
        (QA / "recipes" / f"{row['id']}.json").write_text(json.dumps({"id": row["id"], "edgePink": edge_pink, "stats": st, "roi": box}, indent=2), encoding="utf-8")
        new_outputs[row["id"]]["recipe"] = f"qa/image-vertex-repair-20261009/actors/recipes/{row['id']}.json"
        print("PINK", row["id"], st, status)

    # Flat backdrop extractions for known full-canvas plates.
    backdrop_ids = [
        "troop-bronze-heavy",
        "troop-medieval-heavy",
        "troop-future-heavy",
        "hero-mount-horse",
        "hero-mount-motor-transport",
        "hero-mount-future-transport",
        "knight-mounted-master",
        "troop-medieval-melee",
        "troop-gunpowder-heavy",
        "troop-future-ranged",
        "troop-iron-melee",
    ]
    by_id = {r["id"]: r for r in iface["rows"]}
    for iid in backdrop_ids:
        row = by_id[iid]
        src = (row.get("output") or {}).get("path")
        if not src:
            continue
        arr = load_rgba(ROOT / src)
        subject = backdrop_subject(arr)
        if subject is None:
            print("BACKDROP FAIL", iid)
            repairs.append({"id": iid, "backdrop": "no-flat-border"})
            continue
        # Drop disconnected caption components under the main mass.
        lab, n = ndimage.label(subject)
        if n > 1:
            sizes = [(int(ndimage.sum(subject, lab, i)), i) for i in range(1, n + 1)]
            sizes.sort(reverse=True)
            main = lab == sizes[0][1]
            ys = np.where(main)[0]
            main_bottom = int(ys.max())
            keep = main
            for area, i in sizes[1:]:
                comp = lab == i
                if int(np.where(comp)[0].min()) >= main_bottom - 8 and area < sizes[0][0] * 0.08:
                    continue
                keep |= comp
            subject = keep
        cropped, box = crop_subject(arr, subject)
        st = alpha_stats(cropped)
        if iid == "troop-iron-melee":
            preview(cropped, QA / "diagnostics/troop-iron-melee-rejected-green.jpg")
            (QA / "recipes/troop-iron-melee-rejected.json").write_text(json.dumps({"stats": st, "note": "Gray key split the light shield. Not promoted."}, indent=2), encoding="utf-8")
            print("IRON REJECT", st)
            continue
        ref = save_png(cropped, DERIV / "troops" / f"{iid}.png" if iid.startswith("troop-") else DERIV / "mounts" / f"{iid}.png")
        preview(cropped, QA / "diagnostics" / f"{iid}-green.jpg")
        forced_partial = iid in {
            "troop-bronze-heavy",
            "hero-mount-horse",
            "hero-mount-motor-transport",
            "hero-mount-future-transport",
            "knight-mounted-master",
            "troop-gunpowder-heavy",
            "troop-future-ranged",
            "troop-future-heavy",
            "troop-medieval-melee",
        }
        status = "PARTIAL" if forced_partial or st["bigComponents"] > 2 or st["cropFill"] > 0.8 else "READY"
        if st["border"] > 0.02:
            status = "PARTIAL"
        new_outputs[iid] = {
            "ref": ref,
            "affine": [1, 0, 0, 1, -box[0], -box[1]],
            "source_roi": box,
            "kind": "card" if forced_partial else "sprite",
            "status": status,
            "matte": "PARTIAL" if forced_partial else "PASS",
            "limitations": [
                "Flat border color removed by a 12-level max-channel flood from the border.",
                "Baked ground, captions, extra poses, or a studio plane may remain.",
            ],
            "recipe": None,
            "stats": st,
        }
        print("BACKDROP", iid, st, status)

    # Medieval ranged sheet: real component frames.
    med = by_id["troop-medieval-ranged"]
    med_arr = load_rgba(ROOT / med["output"]["path"])
    frames = largest_components(med_arr, 2500, 16)
    frame_refs = []
    standing = None
    for i, fr in enumerate(frames):
        x0, y0, x1, y1 = fr["roi"]
        piece = med_arr[y0:y1, x0:x1]
        dest = DERIV / f"troops/troop-medieval-ranged-frame-{i:02d}.png"
        ref = save_png(piece, dest)
        item = {**fr, "output": ref, "index": i}
        frame_refs.append(item)
        if fr["semantic"] == "standing-figure-candidate" and (standing is None or fr["area"] > standing["area"]):
            standing = item
    if standing is None and frame_refs:
        standing = max(frame_refs, key=lambda f: f["area"])
    if standing:
        # Primary plate is the standing candidate, already saved.
        new_outputs["troop-medieval-ranged"] = {
            "ref": standing["output"],
            "affine": [1, 0, 0, 1, -standing["roi"][0], -standing["roi"][1]],
            "source_roi": standing["roi"],
            "kind": "sprite",
            "status": "PARTIAL",
            "matte": "PASS",
            "limitations": [
                f"Pose sheet split into {len(frame_refs)} opaque components. Primary is one standing-figure candidate.",
                "Other poses are atlas frames. This is not a gait cycle.",
            ],
            "recipe": "qa/image-vertex-repair-20261009/actors/recipes/troop-medieval-ranged-frames.json",
            "frames": frame_refs,
        }
        (QA / "recipes/troop-medieval-ranged-frames.json").write_text(json.dumps({"frames": frame_refs}, indent=2), encoding="utf-8")
        preview(med_arr[standing["roi"][1]:standing["roi"][3], standing["roi"][0]:standing["roi"][2]], QA / "diagnostics/troop-medieval-ranged-primary-green.jpg")
        print("MED RANGED frames", len(frame_refs), "primary", standing["roi"])

    # Effect sheets: ROI records for a bounded number of large components.
    for iid in ("effect-resurrect", "effect-curse", "effect-projectile", "effect-impact", "effect-haste", "effect-cure", "effect-shield"):
        row = by_id[iid]
        arr = load_rgba(ROOT / row["output"]["path"])
        frs = largest_components(arr, 2000, 8)
        (QA / "recipes" / f"{iid}-frames.json").write_text(json.dumps({"source": row["output"]["path"], "frames": frs}, indent=2), encoding="utf-8")
        if 2 <= len(frs) <= 8:
            new_outputs[iid] = {
                "ref": None,
                "reuse_output": True,
                "kind": "atlas",
                "status": "PARTIAL",
                "matte": "PARTIAL",
                "limitations": [f"{len(frs)} large components measured as atlas ROIs. Whole-sheet draw is not a frame."],
                "recipe": f"qa/image-vertex-repair-20261009/actors/recipes/{iid}-frames.json",
                "frames": frs,
            }
            print("FX", iid, len(frs))

    # Defringe attackers/creatures only when the magenta test hits.
    for row in iface["rows"]:
        if row["id"] in new_outputs or row["role"] not in ("attacker", "creature"):
            continue
        src = (row.get("output") or {}).get("path")
        if not src:
            continue
        arr = load_rgba(ROOT / src)
        cleaned = defringe_magenta(arr)
        if np.array_equal(cleaned[:, :, 3], arr[:, :, 3]):
            continue
        cropped, box = crop_subject(cleaned, cleaned[:, :, 3] > 16)
        ref = save_png(cropped, DERIV / row["role"] / f"{row['id']}.png")
        new_outputs[row["id"]] = {
            "ref": ref,
            "affine": [1, 0, 0, 1, -box[0], -box[1]],
            "source_roi": box,
            "kind": "sprite",
            "status": "READY",
            "matte": "PASS",
            "limitations": ["Edge magenta fringe cleared. Interior purple costume was not a fringe and was kept."],
            "recipe": None,
        }
        print("DEFRINGE", row["id"])

    metrics_path = QA / "diagnostics/process-metrics.json"
    metrics_path.write_text(json.dumps({k: {"status": v["status"], "matte": v["matte"], "ref": v.get("ref")} for k, v in new_outputs.items()}, indent=2), encoding="utf-8")
    print("outputs", len(new_outputs))
    print("snapshot", len(snap))


if __name__ == "__main__":
    main()
