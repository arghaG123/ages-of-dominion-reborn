"""Source-preserving matte cleanup for the seven class standing bodies.

Input: assets/derivatives/image-unified-reserve-20261009/actors/bodies/*.png (RGBA, binary alpha,
white background residue: speckles, orb glow, Ranger ground shadow splat).
Output: assets/derivatives/image-complete-20261011/actors/bodies/*.png trimmed to the subject,
resized so the longest side is at most 1400 px, plus src/data/hero-bodies-20261011.json with
per-ID recipe, sourceToOutput affine, ground contact and hashes.

Rules (recorded, reversible):
- keep the largest alpha component as the subject;
- drop detached components that are near-white (min RGB >= 190) and smaller than 1500 px;
- Ranger only: in the lowest 30 % of the subject box, drop near-white low-saturation regions larger than
  300 px that touch transparency (the pale ground shadow). The earlier note said 6 %; the code uses 30 %.
  Pale clothing and sabatons on other classes are protected by keeping this rule Ranger-only.
- never recolour or add pixels; alpha is only ever reduced.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "assets" / "derivatives" / "image-unified-reserve-20261009" / "actors" / "bodies"
NATIVE = ROOT / "assets" / "derivatives" / "image-unified-reserve-20261009" / "actors" / "natives"
OUT = ROOT / "assets" / "derivatives" / "image-complete-20261011" / "actors" / "bodies"
CONTRACT = ROOT / "src" / "data" / "hero-bodies-20261011.json"
QA = ROOT / "qa" / "image-complete-20261011"
CLASSES = ["knight", "ranger", "warlock", "mage", "paladin", "barbarian", "necromancer"]
MAX_SIDE = 1400


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def near_white(rgb: np.ndarray) -> np.ndarray:
    mn = rgb.min(axis=2)
    mx = rgb.max(axis=2)
    return (mn >= 190) & ((mx - mn) <= 30)


# Per-ID: only the Ranger native carries a pale ground shadow under the boots. Applying the band rule to the
# steel-footed Knight/Paladin removed sabaton highlights (verified by pixel review), so it is Ranger-only.
GROUND_SHADOW_IDS = {"ranger"}


def clean(arr: np.ndarray, ground_rule: bool) -> tuple[np.ndarray, dict]:
    rgb = arr[:, :, :3].astype(np.int16)
    alpha = arr[:, :, 3].copy()
    log = {"droppedComponents": 0, "droppedComponentPixels": 0, "droppedGroundPixels": 0}
    labels, count = ndimage.label(alpha > 8)
    if count == 0:
        raise ValueError("empty matte")
    sizes = ndimage.sum(np.ones_like(alpha, dtype=np.int32), labels, range(1, count + 1))
    main = int(np.argmax(sizes)) + 1
    white = near_white(rgb)
    for index in range(1, count + 1):
        if index == main:
            continue
        mask = labels == index
        size = int(sizes[index - 1])
        if size < 1500 and white[mask].mean() > 0.6:
            alpha[mask] = 0
            log["droppedComponents"] += 1
            log["droppedComponentPixels"] += size
    body = labels == main
    ys = np.nonzero(body.any(axis=1))[0]
    top, bottom = int(ys[0]), int(ys[-1])
    # Lower 30 % of the subject box: near-white regions that touch transparency are background
    # (ground shadow and the enclosed floor between the legs), not paint on dark boots.
    band_start = bottom - int(0.30 * (bottom - top))
    band = np.zeros_like(body)
    band[band_start:, :] = True
    candidate = body & band & white & (alpha > 0) if ground_rule else np.zeros_like(body)
    clabels, ccount = ndimage.label(candidate)
    if ccount:
        exterior = ndimage.binary_dilation(alpha == 0, iterations=2)
        csizes = ndimage.sum(np.ones_like(alpha, dtype=np.int32), clabels, range(1, ccount + 1))
        touching = ndimage.maximum(exterior.astype(np.uint8), clabels, range(1, ccount + 1))
        for index in range(1, ccount + 1):
            if csizes[index - 1] > 300 and touching[index - 1]:
                mask = clabels == index
                alpha[mask] = 0
                log["droppedGroundPixels"] += int(csizes[index - 1])
    out = arr.copy()
    out[:, :, 3] = alpha
    return out, log


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    QA.mkdir(parents=True, exist_ok=True)
    rows = {}
    for name in CLASSES:
        src = SRC / f"class-{name}-standing-body.png"
        image = Image.open(src).convert("RGBA")
        arr = np.array(image)
        cleaned, log = clean(arr, name in GROUND_SHADOW_IDS)
        log["groundShadowRuleApplied"] = name in GROUND_SHADOW_IDS
        alpha = cleaned[:, :, 3]
        ys, xs = np.nonzero(alpha > 0)
        x0, y0, x1, y1 = int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1
        crop = Image.fromarray(cleaned).crop((x0, y0, x1, y1))
        scale = min(1.0, MAX_SIDE / max(crop.size))
        size = (max(1, round(crop.size[0] * scale)), max(1, round(crop.size[1] * scale)))
        if scale < 1.0:
            crop = crop.resize(size, Image.LANCZOS)
        out = OUT / f"class-{name}-standing-body.png"
        crop.save(out, optimize=True)
        out_alpha = np.array(crop)[:, :, 3]
        bottom_rows = np.nonzero((out_alpha > 128).any(axis=1))[0]
        foot_y = int(bottom_rows[-1]) if len(bottom_rows) else crop.size[1] - 1
        foot_cols = np.nonzero(out_alpha[max(0, foot_y - 12):foot_y + 1].max(axis=0) > 128)[0]
        contact = [int(foot_cols.min()), int(foot_cols.max())] if len(foot_cols) else [0, crop.size[0] - 1]
        rel = out.relative_to(ROOT).as_posix()
        rows[name] = {
            "id": f"class-{name}-standing-body",
            "file": rel,
            "sha256": sha256(out),
            "bytes": out.stat().st_size,
            "width": crop.size[0],
            "height": crop.size[1],
            "source": src.relative_to(ROOT).as_posix(),
            "sourceSHA256": sha256(src),
            "native": (NATIVE / f"class-{name}-standing-body.png").relative_to(ROOT).as_posix(),
            "nativeSHA256": sha256(NATIVE / f"class-{name}-standing-body.png"),
            "cropROI": [x0, y0, x1, y1],
            "cropROIConvention": "half-open-xyxy",
            "sourceToOutput": [scale, 0, 0, scale, -x0 * scale, -y0 * scale],
            "groundContact": {"y": foot_y, "x": contact},
            "foot": [((contact[0] + contact[1]) / 2) / crop.size[0], foot_y / crop.size[1]],
            "side": "FRONT",
            "intendedUse": "HERO_ROOM_STANDING",
            "maxVisibleCssPx": 600,
            "matteRepair": log,
            "status": "READY_STATIC_STANDING",
            "notRig": True,
        }
        print(name, crop.size, log)
    contract = {
        "version": "hero-bodies-20261011",
        "status": "STATIC_STANDING_BODIES_NOT_RIGS",
        "note": (
            "Seven realistic standing class bodies, matte-cleaned from the 9 October natives for the Hero equipment room "
            "and class choice. Healer has no body native and stays on its portrait card. These are single front poses, "
            "not articulated rigs; animation eligibility is separate."
        ),
        "maxVisibleCssPx": 600,
        "bodies": rows,
        "missing": {"healer": "no standing-body native exists; portrait card remains the Hero presentation"},
    }
    CONTRACT.write_text(json.dumps(contract, indent=2) + "\n", encoding="utf-8")
    (QA / "body-matte-repair.json").write_text(json.dumps({"bodies": {k: v["matteRepair"] for k, v in rows.items()}, "contract": CONTRACT.relative_to(ROOT).as_posix()}, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
