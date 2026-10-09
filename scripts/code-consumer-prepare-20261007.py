"""Code-owned consumer crops. Reads hash-bound native bytes and writes a new namespace."""
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(r"C:/dev/ages-of-dominion-reborn")
OUT = ROOT / "assets/runtime-code-20261007/troops"
QA = ROOT / "qa/code-whole-build-20261007"
ACTORS = ROOT / "docs/plan/ACTORS-EQUIPMENT-RESIDUAL-INTERFACE-2026-10-07.json"
REPAIR_IDS = {
    "troop-stone-melee": "Clubman",
    "troop-stone-ranged": "Slinger",
    "troop-industrial-ranged": "Sharpshooter",
    "troop-industrial-heavy": "SteamWalker",
}


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def segment(rgb):
    height, width = rgb.shape[:2]
    border = np.concatenate([rgb[0], rgb[-1], rgb[:, 0], rgb[:, -1]], axis=0)
    reference = np.median(border, axis=0)
    distance = np.linalg.norm(rgb.astype(np.float32) - reference.astype(np.float32), axis=2)
    spread = float(border.std())
    threshold = 22.0 if spread < 12 else 34.0
    background = distance < threshold
    labels, _count = ndimage.label(background)
    edge = np.unique(np.concatenate([labels[0], labels[-1], labels[:, 0], labels[:, -1]]))
    edge = edge[edge != 0]
    connected = np.isin(labels, edge) if len(edge) else np.zeros_like(background)
    alpha = np.where(connected, 0, 255).astype(np.uint8)
    definite = distance > 40
    definite_count = int(definite.sum())
    kept = int((definite & (alpha > 0)).sum())
    opaque = alpha > 0
    opaque_count = int(opaque.sum())
    interior = ndimage.binary_erosion(opaque, iterations=5)
    interior_count = int(interior.sum())
    reasons = []
    if definite_count < 1000 or kept / definite_count < 0.92:
        reasons.append("definite body pixels were removed")
    if opaque_count < 1000 or interior_count / opaque_count < 0.40:
        reasons.append("matte is an outline")
    ys, xs = np.where(opaque)
    if len(xs) == 0:
        return None, {"subjectPreserved": False, "reasons": ["no opaque subject"], "threshold": threshold, "borderStd": spread}
    pad = 2
    x0 = max(0, int(xs.min()) - pad)
    y0 = max(0, int(ys.min()) - pad)
    x1 = min(width, int(xs.max()) + 1 + pad)
    y1 = min(height, int(ys.max()) + 1 + pad)
    crop_alpha = alpha[y0:y1, x0:x1]
    crop_opaque = int((crop_alpha > 0).sum())
    crop_area = crop_alpha.size
    if crop_opaque / crop_area < 0.12:
        reasons.append("crop is mostly empty")
    return (x0, y0, x1, y1, alpha), {
        "subjectPreserved": not reasons,
        "reasons": reasons,
        "threshold": threshold,
        "borderStd": round(spread, 3),
        "definiteKept": kept / definite_count if definite_count else 0,
        "interiorFraction": interior_count / opaque_count if opaque_count else 0,
        "opaqueFraction": crop_opaque / crop_area if crop_area else 0,
    }


def repair_one(row):
    source = ROOT / row["source"]["path"]
    actual = sha256(source)
    record = {
        "id": row["id"],
        "sourcePath": row["source"]["path"],
        "declaredSourceSha256": row["source"]["sha256"],
        "actualSourceSha256": actual,
        "hashMatch": actual == row["source"]["sha256"],
        "subjectPreserved": False,
    }
    if not record["hashMatch"]:
        record["reasons"] = ["source hash does not match the residual interface"]
        return record
    rgb = np.asarray(Image.open(source).convert("RGB"))
    crop, metrics = segment(rgb)
    record.update(metrics)
    if not crop or not metrics["subjectPreserved"]:
        return record
    x0, y0, x1, y1, alpha = crop
    rgba = np.dstack([rgb[y0:y1, x0:x1], alpha[y0:y1, x0:x1]])
    OUT.mkdir(parents=True, exist_ok=True)
    target = OUT / f"{row['id']}.png"
    Image.fromarray(rgba, "RGBA").save(target)
    preview_dir = QA / "matte-previews"
    preview_dir.mkdir(parents=True, exist_ok=True)
    preview = Image.fromarray(rgba, "RGBA")
    preview.thumbnail((480, 480))
    for name, color in (("black", (0, 0, 0)), ("white", (255, 255, 255)), ("neutral", (128, 128, 128))):
        board = Image.new("RGBA", preview.size, color + (255,))
        board.alpha_composite(preview)
        board.convert("RGB").save(preview_dir / f"{row['id']}-{name}.jpg", quality=80)
    output_hash = sha256(target)
    record.update({
        "outputPath": str(target.relative_to(ROOT)).replace("\\", "/"),
        "outputSha256": output_hash,
        "dimensions": {"width": int(x1 - x0), "height": int(y1 - y0)},
        "sourceToOutput": [1, 0, 0, 1, -x0, -y0],
        "cropOffset": [x0, y0],
        "groundContact": [[(x1 - x0) / 2, y1 - y0 - 1]],
        "heightEnvelope": [0, 0, int(x1 - x0), int(y1 - y0)],
        "bytes": target.stat().st_size,
    })
    return record


def pixel_row(row):
    path = row.get("output", {}).get("path")
    if not path:
        return None
    file_path = ROOT / path
    if not file_path.exists():
        return {"pass": False, "reason": "missing output"}
    image = Image.open(file_path)
    rgba = np.asarray(image.convert("RGBA"))
    rgb = rgba[:, :, :3].astype(np.int16)
    alpha = rgba[:, :, 3]
    opaque = alpha > 16
    count = int(opaque.sum())
    if count == 0:
        return {"pass": False, "opaqueFraction": 0, "magentaFraction": 0, "reason": "empty"}
    magenta = (rgb[:, :, 0] > 180) & (rgb[:, :, 2] > 180) & (rgb[:, :, 1] < 90) & opaque
    opaque_fraction = count / opaque.size
    magenta_fraction = float(magenta.sum()) / count
    return {
        "pass": opaque_fraction > 0.04 and magenta_fraction < 0.01,
        "opaqueFraction": opaque_fraction,
        "magentaFraction": magenta_fraction,
        "width": int(image.width),
        "height": int(image.height),
    }


def main():
    QA.mkdir(parents=True, exist_ok=True)
    actors = json.loads(ACTORS.read_text(encoding="utf-8"))
    repairs = []
    for row in actors["rows"]:
        if row["id"] in REPAIR_IDS:
            repairs.append(repair_one(row))
    pixels = {}
    for row in actors["rows"]:
        role = row.get("role") or ""
        if not any(token in role for token in ("gear", "artifact", "resource", "skill", "spell", "material", "icon")):
            continue
        measured = pixel_row(row)
        if measured:
            pixels[row["id"]] = measured
    report = {"repairs": repairs, "materials": pixels}
    (QA / "pixel-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"repairs": [{k: item.get(k) for k in ("id", "subjectPreserved", "reasons", "outputPath", "cropOffset")} for item in repairs], "materials": len(pixels)}, indent=2))


if __name__ == "__main__":
    main()
