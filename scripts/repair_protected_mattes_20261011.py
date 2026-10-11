"""Protected matte repairs for plates the 11 October global despill damaged or left on a flat floor.

Industrial support: rebuild alpha from the immutable source. Only border-connected, low-variance
pixels near pure magenta become transparent. Violet and cyan energy stay source pixels.

Medieval archer: clear the border-connected flat olive rectangle. Textured clothing stays.

Neither pass recolours RGB. Damaged outputs stay in place. Successors are new files.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "derivatives" / "image-repair-20261011" / "actors" / "plates"
QA = ROOT / "qa" / "image-repair-20261011"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def local_std(rgb: np.ndarray) -> np.ndarray:
    values = rgb.astype(np.float32)
    mean = ndimage.uniform_filter(values, size=(5, 5, 1))
    square = ndimage.uniform_filter(values * values, size=(5, 5, 1))
    return np.sqrt(np.maximum(square - mean * mean, 0)).mean(axis=2)


def border_flood(candidate: np.ndarray) -> np.ndarray:
    labels, count = ndimage.label(candidate)
    if count == 0:
        return np.zeros(candidate.shape, dtype=bool)
    border = np.zeros(candidate.shape, dtype=bool)
    border[0, :] = border[-1, :] = border[:, 0] = border[:, -1] = True
    touch = ndimage.maximum(border.astype(np.uint8), labels, range(1, count + 1))
    mask = np.zeros(candidate.shape, dtype=bool)
    for index in range(1, count + 1):
        if touch[index - 1]:
            mask |= labels == index
    return mask


def save_rgba(path: Path, rgb: np.ndarray, alpha: np.ndarray) -> None:
    out = np.dstack([rgb, alpha.astype(np.uint8)])
    Image.fromarray(out, "RGBA").save(path, optimize=True)


def repair_support() -> dict:
    source = ROOT / "assets/delivery/stone-starter-20261003/derivatives/v2/live/plates/tower-industrial-support.png"
    damaged = ROOT / "assets/derivatives/image-complete-20261011/actors/plates/tower-industrial-support.png"
    src = np.array(Image.open(source).convert("RGBA"))
    rgb = src[:, :, :3]
    magenta = np.array([255, 0, 255], dtype=np.int16)
    distance = np.linalg.norm(rgb.astype(np.int16) - magenta, axis=2)
    flat = local_std(rgb) < 14
    # Flat backdrop only. High-contrast violet bolts and the cyan ring stay.
    mask = border_flood((distance < 90) & flat)
    alpha = np.where(mask, 0, 255).astype(np.uint8)
    OUT.mkdir(parents=True, exist_ok=True)
    dest = OUT / "tower-industrial-support.png"
    save_rgba(dest, rgb, alpha)
    damaged_alpha = np.array(Image.open(damaged).convert("RGBA"))[:, :, 3]
    restored = int(((damaged_alpha < 16) & (alpha > 250) & ~mask).sum())
    return {
        "id": "5-support",
        "file": dest.relative_to(ROOT).as_posix(),
        "sha256": sha256(dest),
        "bytes": dest.stat().st_size,
        "width": int(rgb.shape[1]),
        "height": int(rgb.shape[0]),
        "source": source.relative_to(ROOT).as_posix(),
        "damagedKept": damaged.relative_to(ROOT).as_posix(),
        "backgroundPixels": int(mask.sum()),
        "opaquePixels": int((alpha > 250).sum()),
        "restoredFromNearlyTransparent": restored,
        "method": "border-connected flat magenta from the immutable source; RGB copied, not recoloured",
    }


def repair_archer() -> dict:
    source = ROOT / "assets/derivatives/image-complete-20261011/actors/plates/attacker-medieval-archer.png"
    src = np.array(Image.open(source).convert("RGBA"))
    rgb = src[:, :, :3]
    alpha = src[:, :, 3]
    opaque = alpha > 16
    std = local_std(rgb)
    border_colours = rgb[opaque]
    # The rectangle is a near-constant olive. Use the median of the low-variance border band.
    edge = np.zeros(opaque.shape, dtype=bool)
    edge[:8, :] = edge[-8:, :] = edge[:, :8] = edge[:, -8:] = True
    sample = rgb[edge & opaque & (std < 8)]
    if len(sample) < 50:
        raise SystemExit("medieval archer border is not a flat field; refusing a colour delete")
    median = np.median(sample.astype(np.int16), axis=0)
    distance = np.linalg.norm(rgb.astype(np.int16) - median, axis=2)
    mask = border_flood(opaque & (distance < 18) & (std < 10))
    # Keep a one-pixel subject cushion so the coat edge is not eaten.
    subject = opaque & ~mask
    cushion = ndimage.binary_dilation(subject, iterations=1)
    mask &= ~cushion
    new_alpha = alpha.copy()
    new_alpha[mask] = 0
    dest = OUT / "attacker-medieval-archer.png"
    save_rgba(dest, rgb, new_alpha)
    return {
        "id": "3-archer",
        "file": dest.relative_to(ROOT).as_posix(),
        "sha256": sha256(dest),
        "bytes": dest.stat().st_size,
        "width": int(rgb.shape[1]),
        "height": int(rgb.shape[0]),
        "source": source.relative_to(ROOT).as_posix(),
        "floorPixelsCleared": int(mask.sum()),
        "medianBorderRGB": [int(v) for v in median],
        "method": "border-connected flat olive rectangle; subject dilated by 1 px and kept; RGB not recoloured",
    }


def main() -> None:
    QA.mkdir(parents=True, exist_ok=True)
    report = {"support": repair_support(), "archer": repair_archer()}
    (QA / "protected-matte.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
