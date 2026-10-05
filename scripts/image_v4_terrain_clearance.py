"""Measured clearances for kingdom sources. Does not replace the active contract."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path("C:/dev/ages-of-dominion-reborn")
OUT = ROOT / "qa/image-v4-repair-20261004/terrain"
OUT.mkdir(parents=True, exist_ok=True)

ACTIVE = [60, -10, 25, 35, 170, 165]
CANDIDATE = [58.5, -9.75, 24.375, 34.125, 175.5, 170.625]
REF_W, REF_H = 1376.0, 768.0


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def corners(rect):
    x, y, w, h = rect
    return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]


def project(pt, matrix, sx, sy):
    a, b, c, d, tx, ty = matrix
    wx, wy = pt
    return ((a * wx + c * wy + tx) * sx, (b * wx + d * wy + ty) * sy)


def raster(shape, pts):
    mask = Image.new("L", (shape[1], shape[0]), 0)
    ImageDraw.Draw(mask).polygon([(float(x), float(y)) for x, y in pts], fill=255)
    return np.array(mask) > 0


def feature_masks(im: np.ndarray) -> dict:
    r, g, b = [im[:, :, i].astype(np.int16) for i in range(3)]
    water = (b > r + 18) & (b > g + 8) & (b > 70)
    water = cv2.morphologyEx(water.astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    # Rocks: dark, textured, not vegetation green and not open soil.
    gray = im.mean(axis=2)
    mean = cv2.blur(gray, (9, 9))
    sq = cv2.blur(gray * gray, (9, 9))
    std = np.sqrt(np.clip(sq - mean * mean, 0, None))
    rock = (std > 28) & (gray < 90) & ~((g > r + 10) & (g > b))
    rock = cv2.morphologyEx(rock.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(rock, 8)
    rock_keep = np.zeros(rock.shape, np.uint8)
    rock_blobs = 0
    for i in range(1, n):
        if stats[i, cv2.CC_STAT_AREA] > 400:
            rock_keep[lab == i] = 1
            rock_blobs += 1
    nw, lw, sw, _ = cv2.connectedComponentsWithStats(water, 8)
    water_keep = np.zeros(water.shape, np.uint8)
    water_blobs = 0
    for i in range(1, nw):
        if sw[i, cv2.CC_STAT_AREA] > 800:
            water_keep[lw == i] = 1
            water_blobs += 1
    return {
        "water": water_keep.astype(bool),
        "rock": rock_keep.astype(bool),
        "waterComponents": water_blobs,
        "rockComponents": rock_blobs,
        "method": "blue-connected water; dark high-local-std rock. Not a roof/std collision label. Roads are not inferred from roughness.",
    }


def clearance(site: np.ndarray, obstacle: np.ndarray) -> dict:
    inter = int((site & obstacle).sum())
    if not site.any():
        return {"intersectionPx": 0, "minClearancePx": None, "sitePx": 0}
    if not obstacle.any():
        return {"intersectionPx": 0, "minClearancePx": None, "sitePx": int(site.sum()), "note": "no annotated obstacle of this class"}
    inv = np.where(obstacle, 0, 255).astype(np.uint8)
    dist = cv2.distanceTransform(inv, cv2.DIST_L2, 3)
    inside = dist[site]
    return {
        "intersectionPx": inter,
        "minClearancePx": round(float(inside.min()), 2),
        "sitePx": int(site.sum()),
    }


def evaluate(im, sites, bridges, matrix, label):
    h, w = im.shape[:2]
    sx, sy = w / REF_W, h / REF_H
    feats = feature_masks(im)
    rows = []
    oob = []
    for site in sites:
        pts = [project(p, matrix, sx, sy) for p in corners(site["rect"])]
        outside = [i for i, (x, y) in enumerate(pts) if x < 0 or y < 0 or x >= w or y >= h]
        if outside:
            oob.append({"id": site["id"], "outsideCornerIndexes": outside, "corners": pts})
        mask = raster(im.shape, pts)
        rows.append({
            "id": site["id"],
            "corners": [[round(x, 1), round(y, 1)] for x, y in pts],
            "water": clearance(mask, feats["water"]),
            "rock": clearance(mask, feats["rock"]),
            "openGroundByThisMethod": clearance(mask, feats["rock"])["intersectionPx"] == 0 and clearance(mask, feats["water"])["intersectionPx"] == 0,
        })
    bridge_rows = []
    for bridge in bridges:
        pts = [project(p, matrix, sx, sy) for p in corners(bridge.get("rect", bridge))]
        mask = raster(im.shape, pts)
        bridge_rows.append({
            "id": bridge.get("id", "bridge"),
            "corners": [[round(x, 1), round(y, 1)] for x, y in pts],
            "water": clearance(mask, feats["water"]),
            "rock": clearance(mask, feats["rock"]),
        })
    hall = next((r for r in rows if r["id"] in {"townhall", "hall", "HALL"}), None)
    return {
        "contract": label,
        "matrix": matrix,
        "scale": [round(sx, 4), round(sy, 4)],
        "annotatedWaterComponents": feats["waterComponents"],
        "annotatedRockComponents": feats["rockComponents"],
        "outOfBoundsSites": oob,
        "hall": hall,
        "sites": rows,
        "bridges": bridge_rows,
        "bakedTownhallClaim": False,
        "note": "A hall polygon with no rock/water intersection is open by this annotation. It does not prove a painted townhall, a road, or owner acceptance.",
    }


def main():
    contract = json.loads((ROOT / "docs/plan/IMPLEMENTATION-CONTRACT.json").read_text(encoding="utf-8"))
    candidate = json.loads((ROOT / "qa/recovery-executor-20261003/kingdom-layout-candidate-v2.json").read_text(encoding="utf-8"))
    sites = contract["geometry"]["kingdom"]["sites"]
    bridges = contract["geometry"]["kingdom"].get("bridges", [])
    c_sites = candidate["geometry"]["sites"]
    c_bridges = candidate["geometry"].get("bridges", [])
    manifest = json.loads((ROOT / "docs/plan/image-production/native4k-first32-delivery-manifest.json").read_text(encoding="utf-8"))
    sources = [{
        "id": "stone-day1-composition-v4-1k",
        "path": "assets/production/production-14-20261003/images/30-kingdom-stone-day1-composition-v4.png",
        "kind": "production-1k-reference",
    }]
    for item in manifest["items"]:
        cid = item.get("canonicalID", "")
        if cid.startswith("kingdom-terrain-"):
            sources.append({"id": cid, "path": item.get("nativePath"), "kind": "native-4k"})
    report = []
    for src in sources:
        path = ROOT / src["path"]
        if not path.exists():
            report.append({**src, "status": "MISSING"})
            continue
        im = np.array(Image.open(path).convert("RGB"))
        active = evaluate(im, sites, bridges, ACTIVE, "active-43553411")
        proposed = evaluate(im, c_sites, c_bridges, CANDIDATE, "candidate-v2")
        # Actual painted content inventory, independent of either contract.
        feats = feature_masks(im)
        report.append({
            "id": src["id"],
            "kind": src["kind"],
            "path": src["path"].replace("\\", "/"),
            "sha256": sha256_file(path),
            "dimensions": [int(im.shape[1]), int(im.shape[0])],
            "mode": "RGB",
            "featuresPresent": {
                "waterComponents": feats["waterComponents"],
                "rockComponents": feats["rockComponents"],
                "bakedTownhall": False,
                "roadAnnotated": False,
                "reason": "No source is declared to contain a baked townhall. Roads are not labeled from color thresholds.",
            },
            "activeContract": active,
            "candidateV2": proposed,
            "scenePromotion": "NOT_PROMOTED",
            "ownerAcceptance": "UNVERIFIED",
        })
        print(src["id"], im.shape[1], "water", feats["waterComponents"], "rock", feats["rockComponents"], "hallActive", active["hall"]["id"] if active["hall"] else None)
    dest = OUT / "clearance-v4.json"
    dest.write_text(json.dumps({
        "version": "v4-measured-clearance-20261004",
        "activeMatrix": ACTIVE,
        "activeContractSha256": "43553411b583a6df5fdcf620d2b3efecd82a0cd6f783895165a5910e577b0fcd",
        "candidateMatrix": CANDIDATE,
        "sources": report,
    }, indent=2), encoding="utf-8")
    print("wrote", dest)


if __name__ == "__main__":
    main()
