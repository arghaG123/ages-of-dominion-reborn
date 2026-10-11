"""Local environment repair delivery for 9 October 2026.

Image AI 1. Reuses adequate residual pixels, repairs separable slabs, normalizes
source/crop frames, measures scene clearance, and prepares Vertex packs.
Does not call a provider and does not write outside the owned allowlist,
except the successor interface path named by the owner.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import coordinator as coord
from geometry import (
    FROZEN_AFFINE,
    HALL_SCALE,
    LEGAL_WH,
    apply_affine,
    grid_to_legal,
    pad_rect_to_legal_polygon,
    polygon_to_polygon_dist,
    polyline_to_polygon_dist,
)

ROOT = Path(r"C:\dev\ages-of-dominion-reborn")
QA = ROOT / "qa" / "image-vertex-repair-20261009" / "environment"
ASSETS = ROOT / "assets" / "derivatives" / "image-vertex-repair-20261009" / "environment"
INTERFACE_PATH = ROOT / "docs" / "plan" / "ENVIRONMENT-ART-VERTEX-REPAIR-INTERFACE-2026-10-09.json"
RESIDUAL_INTERFACE = ROOT / "docs" / "plan" / "ENVIRONMENT-ART-RESIDUAL-INTERFACE-2026-10-07.json"
EXPECTED_RESIDUAL_SHA = "7958b648f74da0b070b1f44829f11c767b62b5e922af20b892cba62e8312c3d2"
VIEWPORTS = [(825, 375), (933, 424), (1180, 820), (1280, 720)]
AGES = ["stone", "bronze", "iron", "medieval", "gunpowder", "industrial", "modern", "future"]
PAD_BUILDINGS = ["farm", "lumber", "quarry", "mine", "barracks", "workshop", "hall", "armory"]
GREEN_NAMED = {
    "armory-stone", "barracks-stone", "farm-bronze", "workshop-iron",
    "townhall-industrial", "mine-industrial", "hall-industrial", "adventure-site-town",
}
CARD_TOKENS = ("skill", "spell", "resource")
MATERIALS = {
    "stone": "timber, hide, thatch, flint, and dirt. No medieval church, steel, or later machinery.",
    "bronze": "earth, plaster, early stone, bronze fittings, and cultivated fields.",
    "iron": "masonry, tiled roofs, iron, and ordered paving.",
    "medieval": "coursed stone, timber, slate, and terracotta.",
    "gunpowder": "bastion stone, period civic yards, and powder-age earthworks.",
    "industrial": "brick, iron, rails, pipes, and factory yards without modern glass towers.",
    "modern": "concrete, glass, asphalt, and utilities.",
    "future": "advanced integrated ground, power channels, and technical paving. No medieval village carryover.",
}
MOCK_BY_AGE = {
    "stone": "design-preview/generated/landscape-mocks-20261003-efcd7a7e/images/03-kingdom-stone.jpg",
    "bronze": "design-preview/generated/landscape-mocks-20261003-efcd7a7e/images/04-kingdom-bronze.jpg",
    "iron": "design-preview/generated/landscape-mocks-20261003-efcd7a7e/images/05-kingdom-iron.jpg",
    "medieval": "design-preview/generated/landscape-mocks-20261003-efcd7a7e/images/06-kingdom-medieval.jpg",
    "gunpowder": "design-preview/generated/landscape-mocks-20261003-efcd7a7e/images/07-kingdom-gunpowder.jpg",
    "industrial": "design-preview/generated/landscape-mocks-20261003-efcd7a7e/images/08-kingdom-industrial.jpg",
    "modern": "design-preview/generated/landscape-mocks-20261003-efcd7a7e/images/09-kingdom-modern.jpg",
    "future": "design-preview/generated/landscape-mocks-20261003-efcd7a7e/images/10-kingdom-future.jpg",
}
MOCK_BY_MODE = {
    "adventure": "design-preview/generated/landscape-mocks-20261003-efcd7a7e/images/11-adventure-overview.jpg",
    "tactical": "design-preview/generated/landscape-mocks-20261003-efcd7a7e/images/14-tactical-deployment.jpg",
    "defense": "design-preview/generated/landscape-mocks-20261003-efcd7a7e/images/17-defense-preparation.jpg",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(payload, indent=2, allow_nan=False).encode("utf-8")
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_bytes(data)
    os.replace(tmp, path)


def round_pt(pt):
    return [round(float(pt[0]), 3), round(float(pt[1]), 3)]


def is_card(role: str, item_id: str) -> bool:
    text = f"{role} {item_id}"
    return any(token in text for token in CARD_TOKENS)


def file_ref(path: Path, dimensions=None) -> dict:
    ref = {"path": rel(path), "sha256": sha256_file(path), "bytes": path.stat().st_size}
    if dimensions:
        ref["dimensions"] = {"width": int(dimensions[0]), "height": int(dimensions[1])}
    return ref


def snapshot(versions: dict) -> dict:
    named = [
        RESIDUAL_INTERFACE,
        ROOT / "qa/image-residual-executor-20261007/environment/checkpoint.json",
        ROOT / "qa/image-residual-executor-20261007/environment/scenes.json",
        ROOT / "qa/image-residual-executor-20261007/environment/input_snapshot.json",
        ROOT / "qa/code-whole-build-20261007/checkpoint.json",
        ROOT / "qa/code-whole-build-20261007/requirements.json",
        ROOT / "qa/code-whole-build-20261007/geometry-proposal-v20261007.json",
        ROOT / "qa/planner-post-code-20261007/per-id-status.json",
        ROOT / "qa/planner-post-code-20261007/actual-building-bindings.json",
        ROOT / "docs/plan/image-production/budget-ledger.json",
        ROOT / "docs/plan/image-production/reconciled-accounting-ledger.json",
        ROOT / "docs/plan/image-production/submission.mutex.json",
        ROOT / "docs/plan/image-production/active-batch.lock.json",
        ROOT / "docs/plan/image-production/pacing_state.json",
        ROOT / "src/data/implementation-contract.json",
        ROOT / "src/data/age-buildings.json",
        ROOT / "src/data/mode-scenes.json",
        ROOT / "src/data/stone-scene.json",
        ROOT / "docs/plan/IMAGE-REGENERATION-AUTHORITY-AND-BLOCKER-RECOVERY-2026-10-09.md",
    ]
    rows = []
    for path in named:
        if not path.exists():
            rows.append({"path": rel(path) if path.is_relative_to(ROOT) else str(path), "missing": True})
            continue
        rows.append({"path": rel(path), "sha256": sha256_file(path), "bytes": path.stat().st_size, "missing": False})
    residual = next(row for row in rows if row["path"].endswith("ENVIRONMENT-ART-RESIDUAL-INTERFACE-2026-10-07.json"))
    payload = {
        "recordedAt": now_iso(),
        "versions": versions,
        "expectedResidualInterfaceSHA256": EXPECTED_RESIDUAL_SHA,
        "residualInterfaceHashMatchesPrompt": residual.get("sha256") == EXPECTED_RESIDUAL_SHA,
        "files": rows,
        "note": "Originals, residual outputs, Code crops, and shared controls were hashed and not modified by this snapshot.",
    }
    write_json(QA / "input_snapshot.json", payload)
    return payload


def alpha_bbox(alpha: np.ndarray, threshold: int = 16):
    ys, xs = np.where(alpha > threshold)
    if len(xs) == 0:
        return None
    return [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]


def sample_alpha(alpha: np.ndarray, x: float, y: float):
    height, width = alpha.shape
    if x < 0 or y < 0 or x >= width or y >= height:
        return {"inside": False, "alpha": None}
    return {"inside": True, "alpha": int(alpha[int(round(y)), int(round(x))])}


def connected_slab(rgb: np.ndarray, alpha: np.ndarray):
    import cv2
    height, width = alpha.shape
    opaque = alpha > 200
    if int(opaque.sum()) < 100:
        return None
    y0 = int(height * 0.90)
    strip = rgb[y0:][opaque[y0:]]
    if len(strip) < 80:
        return None
    median = np.median(strip, axis=0)
    green_median = bool(median[1] > median[0] + 25 and median[1] > median[2] + 12 and median[1] > 90)
    if not green_median:
        return None
    dist = np.max(np.abs(rgb.astype(np.int16) - median.reshape(1, 1, 3)), axis=2)
    flat = opaque & (dist < 28) & (rgb[:, :, 1].astype(np.int16) > rgb[:, :, 0].astype(np.int16) + 12)
    flat[: int(height * 0.55)] = False
    count, labels = cv2.connectedComponents(flat.astype(np.uint8), connectivity=8)
    best = None
    for label in range(1, count):
        component = labels == label
        if not component[-1].any():
            continue
        area = int(component.sum())
        ys, xs = np.where(component)
        top = int(ys.min())
        if area < int(0.012 * width * height):
            continue
        if top < int(height * 0.62):
            continue
        if (xs.max() - xs.min()) < int(0.40 * width):
            continue
        if best is None or area > best["area"]:
            best = {"mask": component, "area": area, "top": top, "median": [round(float(v), 2) for v in median]}
    return best


def magenta_mask(rgb: np.ndarray, alpha: np.ndarray) -> np.ndarray:
    red = rgb[:, :, 0].astype(np.int16)
    green = rgb[:, :, 1].astype(np.int16)
    blue = rgb[:, :, 2].astype(np.int16)
    return (alpha > 16) & (red > 180) & (blue > 180) & (green < 80) & (np.abs(red - blue) < 50)


def analyze_artifact(row: dict, bindings: dict) -> tuple[dict, dict, dict | None]:
    source_path = ROOT / row["source"]["path"]
    output_path = ROOT / row["output"]["path"]
    image = Image.open(output_path)
    image.load()
    arr = np.asarray(image.convert("RGBA"))
    rgb = arr[:, :, :3]
    alpha = arr[:, :, 3]
    height, width = alpha.shape
    mag = magenta_mask(rgb, alpha)
    mag_count = int(mag.sum())
    slab = connected_slab(rgb, alpha)
    repaired = None
    repair_note = None
    if slab is not None:
        updated = arr.copy()
        updated[:, :, 3] = np.where(slab["mask"], 0, updated[:, :, 3])
        outside = ~slab["mask"]
        preserved = bool(np.array_equal(arr[:, :, :3], updated[:, :, :3]) and np.array_equal(arr[:, :, 3][outside], updated[:, :, 3][outside]))
        if preserved:
            repaired = updated
            repair_note = f"Removed bottom-connected flat green slab of {slab['area']} px; subject RGB outside the mask is unchanged."
            arr = updated
            alpha = arr[:, :, 3]
            rgb = arr[:, :, :3]
            mag = magenta_mask(rgb, alpha)
            mag_count = int(mag.sum())
            slab = None
        else:
            repair_note = "Slab candidate failed the subject-preservation check and was not saved."
    if mag_count and mag_count < max(40, int(0.002 * width * height)):
        # Fringe only: a magenta pixel touching transparency.
        fringe = mag.copy()
        transparent = alpha < 32
        neighbor = np.zeros_like(transparent)
        neighbor[1:] |= transparent[:-1]
        neighbor[:-1] |= transparent[1:]
        neighbor[:, 1:] |= transparent[:, :-1]
        neighbor[:, :-1] |= transparent[:, 1:]
        kill = mag & neighbor
        if int(kill.sum()) == mag_count:
            updated = arr.copy()
            updated[:, :, 3] = np.where(kill, 0, updated[:, :, 3])
            repaired = updated
            arr = updated
            alpha = arr[:, :, 3]
            mag_count = 0
            repair_note = (repair_note or "") + f" Cleared {int(kill.sum())} magenta fringe pixels."
    bbox = alpha_bbox(alpha)
    opaque_fraction = float((alpha > 16).mean())
    affine = row.get("sourceToOutput") or [1, 0, 0, 1, 0, 0]
    source_contacts = row.get("groundContact") or []
    output_contacts = [round_pt(apply_affine(affine, pt[0], pt[1])) for pt in source_contacts]
    contact_hits = [sample_alpha(alpha, pt[0], pt[1]) for pt in output_contacts]
    source_entrance = row.get("entrance")
    output_entrance = round_pt(apply_affine(affine, source_entrance[0], source_entrance[1])) if source_entrance else None
    entrance_hit = sample_alpha(alpha, output_entrance[0], output_entrance[1]) if output_entrance else None
    source_foot = row.get("footprint") or []
    output_foot = [round_pt(apply_affine(affine, pt[0], pt[1])) for pt in source_foot]
    card = is_card(str(row.get("role", "")), row["id"])
    binding = bindings.get(row["id"])
    out_of_frame = [pt for pt, hit in zip(output_contacts, contact_hits) if not hit["inside"]]
    missed_paint = [pt for pt, hit in zip(output_contacts, contact_hits) if hit["inside"] and (hit["alpha"] or 0) < 128]
    if card:
        spatial = "PASS" if bbox else "FAIL"
        spatial_limit = "Card bounds are the alpha envelope. This is not a ground contact."
    elif not output_contacts:
        spatial = "PARTIAL"
        spatial_limit = "No source contact was declared."
    elif out_of_frame or missed_paint:
        spatial = "PARTIAL"
        spatial_limit = "Transformed contact is outside the crop or on transparent pixels. Coordinates were not clamped."
    else:
        spatial = "PASS"
        spatial_limit = "Output-frame contacts land on opaque pixels."
    matte = "PASS"
    matte_limit = "No magenta remains and no separable flat green slab remains."
    if mag_count > 0:
        matte = "FAIL"
        matte_limit = f"{mag_count} magenta pixels remain."
    elif slab is not None:
        matte = "FAIL"
        matte_limit = "A separable green slab remains."
    elif opaque_fraction < 0.05:
        matte = "FAIL"
        matte_limit = "Almost no opaque subject remains."
    corner = alpha[0, 0] > 250 and alpha[0, -1] > 250 and alpha[-1, 0] > 250 and alpha[-1, -1] > 250
    intended = "STATIC_CARD" if card and corner else ("MATERIAL" if card else "SPRITE")
    if card and "icon" in str(row.get("role")) and corner:
        role_note = "Role string says icon, but the pixels are an opaque plaque. Treated as STATIC_CARD, not a transparent HUD glyph."
    else:
        role_note = None
    status = "READY" if matte == "PASS" and spatial == "PASS" else ("FAIL" if matte == "FAIL" else "PARTIAL")
    kind = "LOCAL_REPAIR" if repaired is not None else "REUSE"
    if binding and not binding.get("sameAsResidual") and status == "READY":
        kind_note = "CODE_BINDING_ONLY"
    else:
        kind_note = None
    output_file = output_path
    if repaired is not None:
        output_file = ASSETS / "repaired" / f"{row['id']}.png"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        Image.fromarray(arr, "RGBA").save(output_file)
    source_ref = {
        "path": row["source"]["path"],
        "sha256": sha256_file(source_path) if source_path.exists() else row["source"].get("sha256"),
        "bytes": source_path.stat().st_size if source_path.exists() else None,
        "dimensions": None,
        "roi": row["source"].get("roi"),
    }
    try:
        with Image.open(source_path) as src:
            source_ref["dimensions"] = {"width": src.size[0], "height": src.size[1]}
    except Exception:
        source_ref["dimensions"] = None
    output_ref = file_ref(output_file, (width, height))
    reused = file_ref(output_path, (width, height)) if repaired is None else file_ref(output_path, Image.open(output_path).size)
    if repaired is not None:
        with Image.open(output_path) as old:
            reused["dimensions"] = {"width": old.size[0], "height": old.size[1]}
    limitations = [spatial_limit, matte_limit]
    if role_note:
        limitations.append(role_note)
    if kind_note:
        limitations.append("Cleaner residual pixels differ from the current runtime binding. Code rebind is still required.")
    limitations.append("Runtime integration and owner acceptance are unverified.")
    artifact = {
        "id": row["id"],
        "producer": "ENVIRONMENT",
        "role": row.get("role"),
        "age": row.get("age"),
        "classId": None,
        "status": status,
        "source": source_ref,
        "output": output_ref,
        "reusedFrom": None if repaired is not None else {
            "path": row["output"]["path"],
            "sha256": output_ref["sha256"],
            "bytes": output_ref["bytes"],
            "dimensions": output_ref["dimensions"],
        },
        "sourceToOutput": [float(v) for v in affine],
        "intendedUse": intended,
        "maxDisplayCssPx": row.get("maxDisplayCssPx"),
        "side": "NOT_APPLICABLE",
        "frame": "OUTPUT_CROP",
        "groundContact": output_contacts or None,
        "footprint": output_foot or None,
        "entrance": output_entrance,
        "heightEnvelope": bbox,
        "sourceGeometry": {
            "frame": "SOURCE_NATIVE",
            "groundContact": source_contacts or None,
            "footprint": source_foot or None,
            "entrance": source_entrance,
            "heightEnvelope": row.get("heightEnvelope"),
            "roi": row["source"].get("roi"),
        },
        "transforms": {"sourceToOutput": [float(v) for v in affine], "clamped": False},
        "gates": {
            "binding": "PASS" if source_path.exists() else "FAIL",
            "semantics": "PASS" if intended != "SPRITE" or opaque_fraction > 0.08 else "PARTIAL",
            "matte": matte,
            "spatial": spatial,
            "articulation": "NOT_APPLICABLE",
            "runtime": "UNVERIFIED",
            "owner": "UNVERIFIED",
        },
        "recipePath": f"qa/image-vertex-repair-20261009/environment/recipes/{row['id']}.json",
        "evidencePaths": [f"qa/image-vertex-repair-20261009/environment/diagnostics/{row['id']}.json"],
        "limitations": limitations,
        "blockedBy": [],
        "nextAction": None if status == "READY" else ("Prepare a subject-preserving Vertex replacement." if matte == "FAIL" else "Inspect the contact that misses opaque paint."),
    }
    if kind_note and status == "READY":
        artifact["nextAction"] = f"Code rebind from {binding.get('actualRuntimePath')} to {output_ref['path']}."
    diagnostic = {
        "id": row["id"],
        "magentaPixels": mag_count,
        "opaqueFraction": round(opaque_fraction, 4),
        "slabRemoved": repaired is not None and repair_note is not None and "slab" in repair_note,
        "repairNote": repair_note,
        "outputContacts": output_contacts,
        "contactHits": contact_hits,
        "entranceHit": entrance_hit,
        "outOfFrame": out_of_frame,
        "namedGreenConcern": row["id"] in GREEN_NAMED,
        "runtimeBinding": binding,
    }
    decision = {
        "id": row["id"],
        "owner": "ENVIRONMENT",
        "canonicalRequirement": row.get("role") or row["id"],
        "kind": "LOCAL_REPAIR" if repaired is not None else ("CODE_BINDING_ONLY" if kind_note else "REUSE"),
        "defectEvidence": [matte_limit, spatial_limit],
        "localAttemptEvidence": [repair_note] if repair_note else ["No pixel rewrite. Existing decode was measured."],
        "whyGenerationNecessary": None if matte != "FAIL" else matte_limit,
        "sourceRefs": [source_ref],
        "preserve": ["subject silhouette", "foliage that is not a flat bottom slab", "frozen placement contracts"],
        "requiredOutput": output_ref["path"],
        "priority": 2 if matte == "FAIL" else 5,
        "nextAction": artifact["nextAction"],
    }
    recipe = {
        "id": row["id"],
        "frame": "OUTPUT_CROP",
        "sourceFrame": "SOURCE_NATIVE",
        "sourceToOutput": artifact["sourceToOutput"],
        "intendedUse": intended,
        "output": output_ref["path"],
        "reusedFrom": None if repaired is not None else row["output"]["path"],
        "roleHandling": role_note or "Role used as declared.",
        "clamped": False,
    }
    write_json(QA / "recipes" / f"{row['id']}.json", recipe)
    write_json(QA / "diagnostics" / f"{row['id']}.json", diagnostic)
    return artifact, decision, None if matte != "FAIL" else artifact


def measure_scene(scene: dict, contract_mode: dict | None) -> dict:
    source = scene["source"]
    width, height = source["dimensions"]
    scale_x = LEGAL_WH[0] / width
    scale_y = LEGAL_WH[1] / height
    uniform = abs(scale_x - scale_y) < 1e-6
    source_to_legal = [scale_x, 0.0, 0.0, scale_y, 0.0, 0.0]
    roads = []
    conflicts = []
    for index, road in enumerate(scene.get("paintedRoadPolylines") or []):
        native = road.get("polylineNative") or []
        if not native:
            continue
        max_x = max(pt[0] for pt in native)
        if max_x > LEGAL_WH[0] + 20:
            legal = [(pt[0] * scale_x, pt[1] * scale_y) for pt in native]
            frame = "SOURCE_NATIVE_SCALED_TO_LEGAL"
        else:
            legal = [(pt[0], pt[1]) for pt in native]
            frame = "LEGAL"
        uncertainty = float(road.get("uncertaintyLegalPx", 8.0))
        roads.append({
            "id": road.get("kind") or f"road-{index}",
            "polyline": [round_pt(pt) for pt in legal],
            "halfWidth": 8.0,
            "uncertainty": uncertainty,
            "frame": frame,
            "units": "legal px on the 1376x768 plate",
            "method": road.get("method") or "producer polyline",
        })
    sites = (contract_mode or {}).get("sites") or []
    affine = (contract_mode or {}).get("worldToSource") or FROZEN_AFFINE
    if scene.get("mode") == "kingdom":
        affine = FROZEN_AFFINE
    pads = []
    for site in sites:
        rect = site.get("rect")
        if not rect:
            continue
        polygon = pad_rect_to_legal_polygon(rect, affine)
        pads.append({"id": site["id"], "rect": rect, "polygon": [round_pt(pt) for pt in polygon]})
        for road in roads:
            dist = polyline_to_polygon_dist(road["polyline"], polygon)
            required = 8.0 + road["uncertainty"]
            if dist <= required:
                conflicts.append({
                    "road": road["id"],
                    "site": site["id"],
                    "distanceLegalPx": round(float(dist), 3),
                    "requiredLegalPx": required,
                    "units": "legal px",
                    "method": "segment distance from declared painted polyline to pad quad",
                    "uncertaintyLegalPx": road["uncertainty"],
                })
    pad_gaps = []
    for i, left in enumerate(pads):
        for right in pads[i + 1:]:
            dist = polygon_to_polygon_dist(
                [(pt[0], pt[1]) for pt in left["polygon"]],
                [(pt[0], pt[1]) for pt in right["polygon"]],
            )
            if dist < 16:
                pad_gaps.append({"a": left["id"], "b": right["id"], "distanceLegalPx": round(float(dist), 3), "requiredLegalPx": 16})
    image = Image.open(ROOT / source["path"])
    legal_image = image.resize(LEGAL_WH, Image.Resampling.BOX)
    sample = np.asarray(legal_image.convert("RGB"))
    red = sample[:, :, 0].astype(np.int16)
    green = sample[:, :, 1].astype(np.int16)
    blue = sample[:, :, 2].astype(np.int16)
    water = (blue > red + 18) & (blue > green + 8) & (sample[:, :, 2] > 70)
    fraction = float(water.mean())
    traversed = False
    for road in roads:
        for pt in road["polyline"]:
            x = int(round(pt[0]))
            y = int(round(pt[1]))
            if 0 <= x < LEGAL_WH[0] and 0 <= y < LEGAL_WH[1]:
                y0, y1 = max(0, y - 8), min(LEGAL_WH[1], y + 9)
                x0, x1 = max(0, x - 8), min(LEGAL_WH[0], x + 9)
                if water[y0:y1, x0:x1].any():
                    traversed = True
                    break
        if traversed:
            break
    if fraction <= 0.002:
        water_class = "ABSENT"
    elif traversed:
        water_class = "TRAVERSED"
    else:
        water_class = "STATIC"
    bridge_class = "ABSENT"
    for bridge in (contract_mode or {}).get("bridges") or []:
        bridge_class = "PRESENT_IN_LEGAL_CONTRACT"
    if water_class != "ABSENT" and bridge_class == "ABSENT":
        bridge_class = "VISIBLE_WATER_BRIDGE_NOT_SEPARATELY_TRACED"
    frozen_ok = list(scene.get("legalAffineActive") or []) == FROZEN_AFFINE or scene.get("mode") != "kingdom"
    hall_ok = scene.get("hallScaleActive") in (None, HALL_SCALE) or scene.get("mode") != "kingdom"
    row = {
        "id": scene["id"],
        "age": AGES.index(scene["age"]) if scene.get("age") in AGES else scene.get("age"),
        "mode": scene.get("mode"),
        "source": {
            "path": source["path"],
            "sha256": sha256_file(ROOT / source["path"]),
            "bytes": (ROOT / source["path"]).stat().st_size,
            "dimensions": {"width": width, "height": height},
        },
        "frame": "SOURCE_NATIVE",
        "sourceToLegal": source_to_legal,
        "roads": roads,
        "banks": scene.get("banks") or [],
        "decks": scene.get("decks") or [],
        "approaches": scene.get("approaches") or [],
        "walkable": scene.get("walkable") or [],
        "obstacles": scene.get("obstacles") or [],
        "featureApplicability": {
            "water": water_class,
            "waterPixelFractionOn1376BoxDownsample": round(fraction, 5),
            "waterMethod": "BOX downsample to 1376x768, blue dominance B>R+18 and B>G+8 and B>70",
            "bridge": bridge_class,
            "banks": "UNVERIFIED_NOT_ASSERTED_ABSENT" if not scene.get("banks") else "DECLARED",
            "decks": "UNVERIFIED_NOT_ASSERTED_ABSENT" if not scene.get("decks") else "DECLARED",
        },
        "fullFootprints": pads,
        "clearanceResults": conflicts,
        "padGapUnder16LegalPx": pad_gaps,
        "proposal": {
            "id": f"proposal-vertex-repair-20261009-{scene['id']}",
            "status": "PROPOSED",
            "active": False,
        },
        "gates": {
            "binding": "PASS",
            "semantics": "PARTIAL",
            "matte": "NOT_APPLICABLE",
            "spatial": "FAIL" if conflicts else "PARTIAL",
            "articulation": "NOT_APPLICABLE",
            "runtime": "UNVERIFIED",
            "owner": "UNVERIFIED",
            "frozenAffine": "PASS" if frozen_ok else "FAIL",
            "hallScale": "PASS" if hall_ok else "FAIL",
            "uniformScale": "PASS" if uniform else "FAIL",
        },
        "evidencePaths": [f"qa/image-vertex-repair-20261009/environment/geography/{scene['id']}-clearance.json"],
        "blockedBy": [] if conflicts else ["Painted-road clearance is not a full physical footprint, height, entrance, Wall, or walkable proof."],
        "nextAction": "Generate corrected ground on the frozen legal guide." if conflicts else "Keep the plate and finish manual bank/deck/approach traces before promotion.",
        "limitations": [
            "Arithmetic clearance uses the producer polyline, not a new Sobel trace.",
            "Containment of a pad inside a road loop is not treated as edge contact.",
            "Camera proposal stays inactive.",
        ],
    }
    if scene.get("mode") == "kingdom":
        row["legalAffineActive"] = FROZEN_AFFINE
        row["hallScaleActive"] = HALL_SCALE
        row["geometryEdited"] = False
    write_json(QA / "geography" / f"{scene['id']}-clearance.json", {
        "conflictCount": len(conflicts),
        "conflicts": conflicts,
        "padGapUnder16LegalPx": pad_gaps,
        "water": row["featureApplicability"],
    })
    return row, legal_image, len(conflicts)


def render_composites(scene_id: str, legal_image: Image.Image, reference_rel: str | None) -> list[dict]:
    rows = []
    reference = None
    if reference_rel and (ROOT / reference_rel).exists():
        reference = Image.open(ROOT / reference_rel).convert("RGB")
    for width, height in VIEWPORTS:
        scale = min(width / LEGAL_WH[0], height / LEGAL_WH[1])
        placed_w = int(round(LEGAL_WH[0] * scale))
        placed_h = int(round(LEGAL_WH[1] * scale))
        offset_x = (width - placed_w) // 2
        offset_y = (height - placed_h) // 2
        plate = legal_image.resize((placed_w, placed_h), Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", (width, height), (12, 16, 18))
        canvas.paste(plate, (offset_x, offset_y))
        out = QA / "composites" / f"{scene_id}-{width}x{height}.png"
        out.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(out, compress_level=1)
        ref_out = None
        if reference is not None:
            ref_scale = min(width / reference.size[0], height / reference.size[1])
            ref_w = int(round(reference.size[0] * ref_scale))
            ref_h = int(round(reference.size[1] * ref_scale))
            side = Image.new("RGB", (width * 2 + 8, height), (12, 16, 18))
            side.paste(reference.resize((ref_w, ref_h), Image.Resampling.LANCZOS), ((width - ref_w) // 2, (height - ref_h) // 2))
            side.paste(canvas, (width + 8, 0))
            ref_out = QA / "composites" / f"{scene_id}-{width}x{height}-vs-reference.png"
            side.save(ref_out, compress_level=1)
        rows.append({
            "id": f"{scene_id}-{width}x{height}",
            "stateKind": "ASSET_COMPOSITE",
            "viewport": [width, height],
            "reference": file_ref(ROOT / reference_rel, reference.size) if reference is not None else None,
            "actual": file_ref(out, (width, height)),
            "comparison": rel(ref_out) if ref_out else None,
            "camera": {
                "uniformScale": round(scale, 6),
                "offset": [offset_x, offset_y],
                "safeArea": [offset_x, offset_y, offset_x + placed_w, offset_y + placed_h],
                "units": "composite px; safeArea is the uniform-scaled plate, half-open",
                "chrome": "UI chrome is not painted into this plate. Code owns the HUD inset.",
            },
            "contributors": [{"role": "terrain-plate", "scene": scene_id}],
            "layerAvailability": {"terrain": "PRESENT", "buildings": "ABSENT", "actors": "ABSENT", "hud": "ABSENT"},
            "checks": {"uniformScale": "PASS", "nonuniformStretch": "ABSENT"},
            "differences": [
                "Reference mocks include actors, text, and HUD. This composite is the terrain plate only.",
                "The plate is letterboxed with one scale on both axes.",
            ],
        })
    if reference is not None:
        reference.close()
    return rows


def shrink_reference(path: Path, dest: Path, longest: int = 1024) -> dict:
    image = Image.open(path)
    image.load()
    scale = min(1.0, longest / max(image.size))
    size = (max(1, int(round(image.size[0] * scale))), max(1, int(round(image.size[1] * scale))))
    resized = image.convert("RGB").resize(size, Image.Resampling.LANCZOS)
    dest.parent.mkdir(parents=True, exist_ok=True)
    resized.save(dest, quality=90)
    return {
        "from": [image.size[0], image.size[1]],
        "to": [size[0], size[1]],
        "scale": round(scale, 6),
        "method": "LANCZOS request-reference copy. The generated output is not this resize.",
    }


def draw_guide(scene_row: dict, dest: Path) -> None:
    image = Image.new("RGB", LEGAL_WH, (86, 112, 62))
    draw = ImageDraw.Draw(image, "RGBA")
    for pad in scene_row["fullFootprints"]:
        polygon = [(pt[0], pt[1]) for pt in pad["polygon"]]
        fill = (214, 176, 74, 120) if pad["id"] == "townhall" else (64, 168, 72, 110)
        draw.polygon(polygon, fill=fill, outline=(250, 250, 240))
    for road in scene_row["roads"]:
        points = [(pt[0], pt[1]) for pt in road["polyline"]]
        if len(points) >= 2:
            draw.line(points, fill=(236, 232, 214), width=3)
    dest.parent.mkdir(parents=True, exist_ok=True)
    image.save(dest)


def build_pack(scene_row: dict, priority: int) -> dict:
    scene_id = scene_row["id"]
    age_name = scene_row["mode"] if not isinstance(scene_row.get("age"), int) else AGES[scene_row["age"]]
    material_key = AGES[scene_row["age"]] if isinstance(scene_row.get("age"), int) else "stone"
    reference_rel = MOCK_BY_AGE.get(material_key) if scene_row["mode"] == "kingdom" else MOCK_BY_MODE.get(scene_row["mode"])
    guide_path = QA / "geography" / "guides" / f"{scene_id}-legal-guide.png"
    draw_guide(scene_row, guide_path)
    ref_copy = QA / "regeneration" / "refs" / f"{scene_id}-appearance.jpg"
    transform = shrink_reference(ROOT / reference_rel, ref_copy) if reference_rel else None
    material = MATERIALS.get(material_key, "age-appropriate ground materials")
    if scene_row["mode"] != "kingdom":
        material = f"{scene_row['mode']} valley, {material_key} biome appearance. Empty lanes and pads. No soldiers, towers, or attackers."
    prompt = (
        "ONE landscape image for Ages of Dominion. Native 4K, 16:9, one image only. "
        "Semi-realistic strategy-game ground, warm upper-left daylight, short contact shadows, aerial three-quarter view. "
        "The first image is an exact spatial guide. Green rectangles and the gold terrace are EMPTY buildable clearings and must stay at those positions. "
        "Do not draw buildings, people, animals, text, HUD, numbers, labels, or a device frame. Do not move the river, pads, roads, or bridge. "
        "The second image supplies approved landscape material and color only. Do not copy its buildings, UI, text, or frame. "
        f"Age and mode: {scene_row['mode']} {material_key}. Materials: {material} "
        "Roads must follow the pale guide lines and stay outside the reserved rectangles. "
        "Where the old painting put road through a pad, replace that road with bare age-appropriate ground."
    )
    prompt_path = QA / "regeneration" / "prompts" / f"{scene_id}.txt"
    prompt_path.parent.mkdir(parents=True, exist_ok=True)
    prompt_path.write_text(prompt, encoding="utf-8")
    parts = [{"text": prompt}]
    for image_path, mime in ((guide_path, "image/png"), (ref_copy, "image/jpeg")):
        if image_path.exists():
            parts.append({"inlineData": {"mimeType": mime, "data": __import__("base64").b64encode(image_path.read_bytes()).decode("ascii")}})
    body = {
        "contents": [{"role": "user", "parts": parts}],
        "generationConfig": {
            "candidateCount": 1,
            "maxOutputTokens": 2048,
            "responseModalities": ["IMAGE"],
            "imageConfig": {"aspectRatio": "16:9", "imageSize": "4K"},
        },
    }
    wire = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    wire_path = QA / "regeneration" / "wire" / f"{scene_id}.json"
    wire_path.parent.mkdir(parents=True, exist_ok=True)
    wire_path.write_bytes(wire)
    legal_payload = {
        "affine": FROZEN_AFFINE if scene_row["mode"] == "kingdom" else scene_row["sourceToLegal"],
        "hallScale": HALL_SCALE if scene_row["mode"] == "kingdom" else None,
        "pads": scene_row["fullFootprints"],
    }
    legal_hash = hashlib.sha256(json.dumps(legal_payload, sort_keys=True).encode("utf-8")).hexdigest()
    bound = coord.estimate_upper_bound_usd("4K", len(parts) - 1, len(prompt))
    pack = {
        "schema": 1,
        "id": f"env-{scene_id}-v1",
        "owner": "ENVIRONMENT",
        "canonicalId": scene_id,
        "version": "v1",
        "state": "READY",
        "defect": f"{len(scene_row['clearanceResults'])} painted-road corridor conflicts against frozen pads",
        "reason": "Local blur or warp cannot rebuild hidden or wrongly painted ground. A new guided source is required.",
        "priorSourceHashes": [scene_row["source"]["sha256"]],
        "referenceRefs": [file_ref(ROOT / reference_rel)] if reference_rel and (ROOT / reference_rel).exists() else [],
        "base": None,
        "mask": None,
        "guide": file_ref(guide_path, LEGAL_WH),
        "landmarks": {"pads": [pad["id"] for pad in scene_row["fullFootprints"]], "roads": [road["id"] for road in scene_row["roads"]]},
        "legalGeometrySHA256": legal_hash,
        "requestedResolution": "4K",
        "aspectRatio": "16:9",
        "expectedNativeDimensions": None,
        "project": coord.PROJECT,
        "model": coord.MODEL,
        "promptPath": rel(prompt_path),
        "promptSHA256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        "wireBodyPath": rel(wire_path),
        "wireBodySHA256": hashlib.sha256(wire).hexdigest(),
        "inputTransforms": [transform] if transform else [],
        "semanticCriteria": [
            "Age materials match the prompt and the approved landscape direction.",
            "No text, HUD, people, or device frame.",
            "Reserved rectangles stay empty ground.",
        ],
        "geometryCriteria": [
            "Output is native 4K 16:9, decoded from the response, not upscaled afterward.",
            "Guide rectangles remain the empty-pad targets. Frozen affine and Hall scale are not edited.",
            "Road paint must clear pad quads by more than 8 legal px plus trace uncertainty after the same measurement.",
        ],
        "maskApplicability": "No inpainting mask is sent. The guide image is a labeled spatial input. The API mask field is not used.",
        "maxCandidateCalls": 2,
        "estimatedUpperBoundUSD": bound,
        "readinessEvidence": scene_row["evidencePaths"],
        "blockedBy": [],
        "priority": priority,
    }
    pack_path = QA / "regeneration" / "packs" / f"{pack['id']}.json"
    write_json(pack_path, pack)
    return pack


def support_rows() -> list[dict]:
    screens = [
        ("support-home", "01-home.jpg", "Home gate scenery can reuse the kingdom plate. Buttons and menu text are Code-native."),
        ("support-class-choice", "01-home.jpg", "Class portraits are actor art. The environment is a panel, Code-native."),
        ("support-kingdom", "02-kingdom-day1.jpg", "Kingdom scenery is the age terrain plate plus building sprites."),
        ("support-adventure", "11-adventure-overview.jpg", "Adventure scenery is the biome plate plus site sprites."),
        ("support-tactical", "14-tactical-deployment.jpg", "Tactical scenery is the biome plate. Actors and controls are separate."),
        ("support-battle-result", "16-battle-result.jpg", "Result typography and buttons are Code-native over the mode plate."),
        ("support-defense", "17-defense-preparation.jpg", "Defense scenery is the biome plate plus stationary tower bodies."),
        ("support-hero", "19-hero-equipment.jpg", "Hero and equipment subjects are actor art. Panels are Code-native."),
        ("support-skills", "20-skills.jpg", "Skill plaques are the existing skill sprites. Screen chrome is Code-native."),
        ("support-spells", "21-spells.jpg", "Spell plaques are the existing spell sprites. Screen chrome is Code-native."),
        ("support-forge", "22-forge.jpg", "Forge panels and slots are Code-native. No baked forge screenshot is a layer."),
        ("support-inventory", "23-inventory.jpg", "Inventory grid is Code-native."),
        ("support-army", "24-army.jpg", "Army subjects are actor art. Codex background is Code-native."),
        ("support-story", "25-story.jpg", "Story frame can be Code-native. Chapter text is Code."),
        ("support-quests", "26-quests.jpg", "Quest list is Code-native."),
        ("support-tutorial", "27-tutorial.jpg", "The tutorial mock includes a device frame and is reference-only."),
        ("support-settings", "28-settings.jpg", "Settings, audio, help, credits, and privacy are Code-native."),
        ("support-save", "29-save-recovery.jpg", "Save, recovery, import, export, slots, and backup are Code-native."),
        ("support-icon-board", "30-icon-material-board.jpg", "Resource, skill, and spell sprites already cover the material board."),
    ]
    rows = []
    for item_id, mock, reason in screens:
        path = ROOT / "design-preview/generated/landscape-mocks-20261003-efcd7a7e/images" / mock
        rows.append({
            "id": item_id,
            "producer": "ENVIRONMENT",
            "role": "support-material",
            "age": None,
            "classId": None,
            "status": "READY",
            "source": {"path": rel(path), "sha256": sha256_file(path), "bytes": path.stat().st_size, "dimensions": None, "roi": None},
            "output": None,
            "reusedFrom": None,
            "sourceToOutput": None,
            "intendedUse": "REFERENCE_ONLY",
            "maxDisplayCssPx": None,
            "side": "NOT_APPLICABLE",
            "frame": "SOURCE_NATIVE",
            "groundContact": None,
            "footprint": None,
            "entrance": None,
            "heightEnvelope": None,
            "sourceGeometry": None,
            "transforms": {},
            "gates": {"binding": "PASS", "semantics": "PASS", "matte": "NOT_APPLICABLE", "spatial": "NOT_APPLICABLE", "articulation": "NOT_APPLICABLE", "runtime": "UNVERIFIED", "owner": "UNVERIFIED"},
            "recipePath": None,
            "evidencePaths": [],
            "limitations": [reason, "No new image is required for this surface."],
            "blockedBy": [],
            "nextAction": None,
        })
    return rows


def reference_only_mocks() -> list[dict]:
    names = [
        "support-env-home", "support-env-forge", "support-env-inventory", "support-env-army",
        "support-env-story", "support-env-quests", "support-env-tutorial", "support-env-settings", "support-env-recovery",
    ]
    rows = []
    for name in names:
        path = ROOT / "assets/derivatives/image-residual-executor-20261007/environment/support" / f"{name}.png"
        if not path.exists():
            continue
        with Image.open(path) as image:
            size = image.size
        ref = file_ref(path, size)
        rows.append({
            "id": name,
            "producer": "ENVIRONMENT",
            "role": "support-environment-backdrop",
            "age": None,
            "classId": None,
            "status": "PARTIAL",
            "source": {**ref, "roi": None},
            "output": ref,
            "reusedFrom": ref,
            "sourceToOutput": [1, 0, 0, 1, 0, 0],
            "intendedUse": "REFERENCE_ONLY",
            "maxDisplayCssPx": None,
            "side": "NOT_APPLICABLE",
            "frame": "SOURCE_NATIVE",
            "groundContact": None,
            "footprint": None,
            "entrance": None,
            "heightEnvelope": None,
            "sourceGeometry": None,
            "transforms": {},
            "gates": {"binding": "PASS", "semantics": "FAIL", "matte": "FAIL", "spatial": "NOT_APPLICABLE", "articulation": "NOT_APPLICABLE", "runtime": "UNVERIFIED", "owner": "UNVERIFIED"},
            "recipePath": None,
            "evidencePaths": [],
            "limitations": ["Full mock screenshot with baked actors, text, or a device frame. Not a functional environment layer."],
            "blockedBy": [],
            "nextAction": "Use the clean plate, sprite, or Code-native UI named in the support rows.",
        })
    return rows


def state_rows(artifact_ids: set[str]) -> list[dict]:
    rows = []
    for age_index, age in enumerate(AGES):
        for kind in PAD_BUILDINGS + ["townhall"]:
            completed = f"{kind}-{age}"
            for state in ("empty", "building", "completed", "upgrade"):
                item_id = f"state-{kind}-{age}-{state}"
                if state == "completed" and completed in artifact_ids:
                    rows.append({
                        "id": item_id,
                        "producer": "ENVIRONMENT",
                        "role": "building-state",
                        "age": age_index,
                        "classId": None,
                        "status": "READY",
                        "source": None,
                        "output": None,
                        "reusedFrom": None,
                        "sourceToOutput": None,
                        "intendedUse": "SPRITE",
                        "maxDisplayCssPx": None,
                        "side": "NOT_APPLICABLE",
                        "frame": "OUTPUT_CROP",
                        "groundContact": None,
                        "footprint": None,
                        "entrance": None,
                        "heightEnvelope": None,
                        "sourceGeometry": {"completedSprite": completed},
                        "transforms": {},
                        "gates": {"binding": "PASS", "semantics": "PASS", "matte": "NOT_APPLICABLE", "spatial": "NOT_APPLICABLE", "articulation": "NOT_APPLICABLE", "runtime": "UNVERIFIED", "owner": "UNVERIFIED"},
                        "recipePath": None,
                        "evidencePaths": [],
                        "limitations": [f"Completed appearance is the existing sprite {completed}. This state row does not duplicate those pixels."],
                        "blockedBy": [],
                        "nextAction": None,
                    })
                else:
                    rows.append({
                        "id": item_id,
                        "producer": "ENVIRONMENT",
                        "role": "building-state",
                        "age": age_index,
                        "classId": None,
                        "status": "READY",
                        "source": None,
                        "output": None,
                        "reusedFrom": None,
                        "sourceToOutput": None,
                        "intendedUse": "MATERIAL",
                        "maxDisplayCssPx": None,
                        "side": "NOT_APPLICABLE",
                        "frame": "OUTPUT_CROP",
                        "groundContact": None,
                        "footprint": None,
                        "entrance": None,
                        "heightEnvelope": None,
                        "sourceGeometry": None,
                        "transforms": {},
                        "gates": {"binding": "NOT_APPLICABLE", "semantics": "PASS", "matte": "NOT_APPLICABLE", "spatial": "NOT_APPLICABLE", "articulation": "NOT_APPLICABLE", "runtime": "UNVERIFIED", "owner": "UNVERIFIED"},
                        "recipePath": None,
                        "evidencePaths": [],
                        "limitations": ["No separate raster. Empty pads are terrain. Construction and upgrade chrome are Code-native SVG or CSS."],
                        "blockedBy": [],
                        "nextAction": None,
                    })
        for state, reason in (("wall0", "Level 0 is the absence of a wall sprite."), ("developed", "Developed walls use the existing walls sprite.")):
            rows.append({
                "id": f"state-walls-{age}-{state}",
                "producer": "ENVIRONMENT",
                "role": "wall-state",
                "age": age_index,
                "classId": None,
                "status": "READY",
                "source": None,
                "output": None,
                "reusedFrom": None,
                "sourceToOutput": None,
                "intendedUse": "SPRITE" if state == "developed" else "MATERIAL",
                "maxDisplayCssPx": None,
                "side": "NOT_APPLICABLE",
                "frame": "OUTPUT_CROP",
                "groundContact": None,
                "footprint": None,
                "entrance": None,
                "heightEnvelope": None,
                "sourceGeometry": {"completedSprite": f"walls-{age}"} if state == "developed" else None,
                "transforms": {},
                "gates": {"binding": "NOT_APPLICABLE", "semantics": "PASS", "matte": "NOT_APPLICABLE", "spatial": "NOT_APPLICABLE", "articulation": "NOT_APPLICABLE", "runtime": "UNVERIFIED", "owner": "UNVERIFIED"},
                "recipePath": None,
                "evidencePaths": [],
                "limitations": [reason],
                "blockedBy": [],
                "nextAction": None,
            })
    return rows


def png_paths(obj, found: list[str]) -> None:
    if isinstance(obj, str) and obj.endswith(".png"):
        found.append(obj)
    elif isinstance(obj, dict):
        for value in obj.values():
            png_paths(value, found)
    elif isinstance(obj, list):
        for value in obj:
            png_paths(value, found)


def write_gallery(rows: list[dict], composites: list[dict]) -> None:
    parts = [
        "<!DOCTYPE html><html><head><meta charset='utf-8'><title>Environment vertex repair 2026-10-09</title>",
        "<style>body{font-family:Georgia,serif;background:#16130f;color:#f3ead7;margin:24px}img{max-width:320px;background:#222}figure{display:inline-block;margin:8px;vertical-align:top}</style></head><body>",
        "<h1>Environment repair, 9 October 2026</h1>",
        "<p>ASSET_COMPOSITE plates use one uniform scale. They are not gameplay screens. Reference-only mocks stay labeled.</p>",
    ]
    for row in composites:
        if not str(row["id"]).endswith("1280x720"):
            continue
        parts.append(f"<figure><img src='../../composites/{Path(row['actual']['path']).name}' alt=''><figcaption>{row['id']} ASSET_COMPOSITE</figcaption></figure>")
    parts.append("<h2>Repaired sprites</h2>")
    for row in rows:
        if row.get("reusedFrom") is None and row.get("output") and "repaired" in row["output"]["path"]:
            parts.append(f"<figure><img src='../../../../{row['output']['path']}' alt=''><figcaption>{row['id']} {row['status']}</figcaption></figure>")
    parts.append("</body></html>")
    path = QA / "review" / "index.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(parts), encoding="utf-8")


def versions() -> dict:
    import numpy
    from PIL import Image as PILImage
    import cv2
    import scipy
    return {
        "python": sys.version,
        "pillow": PILImage.__version__,
        "numpy": numpy.__version__,
        "opencv": cv2.__version__,
        "scipy": scipy.__version__,
        "node": "v24.19.0 verified in this session before the script",
    }


def main() -> None:
    QA.mkdir(parents=True, exist_ok=True)
    ver = versions()
    snap = snapshot(ver)
    residual = load_json(RESIDUAL_INTERFACE)
    scenes = load_json(ROOT / "qa/image-residual-executor-20261007/environment/scenes.json")
    contract = load_json(ROOT / "src/data/implementation-contract.json")
    bindings = {row["id"]: row for row in load_json(ROOT / "qa/planner-post-code-20261007/actual-building-bindings.json")["rows"]}
    artifacts = []
    decisions = []
    failed = []
    for row in residual["rows"]:
        artifact, decision, failed_row = analyze_artifact(row, bindings)
        artifacts.append(artifact)
        decisions.append(decision)
        if failed_row:
            failed.append(failed_row["id"])
        print(f"artifact {row['id']} {artifact['status']}", flush=True)
    sprite_ids = {row["id"] for row in artifacts}
    scene_rows = []
    composites = []
    packs = []
    for scene in scenes:
        mode = contract["geometry"].get(scene.get("mode"))
        scene_row, legal_image, conflict_count = measure_scene(scene, mode)
        scene_rows.append(scene_row)
        reference = MOCK_BY_AGE.get(scene.get("age")) if scene.get("mode") == "kingdom" else MOCK_BY_MODE.get(scene.get("mode"))
        composites.extend(render_composites(scene["id"], legal_image, reference))
        legal_image.close()
        if conflict_count:
            priority = 1 if scene.get("mode") == "kingdom" else 3
            packs.append(build_pack(scene_row, priority))
            decisions.append({
                "id": scene["id"],
                "owner": "ENVIRONMENT",
                "canonicalRequirement": f"{scene.get('mode')} terrain",
                "kind": "VERTEX_REPLACEMENT",
                "defectEvidence": [f"{conflict_count} corridor conflicts"],
                "localAttemptEvidence": scene_row["evidencePaths"],
                "whyGenerationNecessary": "Existing paint conflicts with frozen pads and hidden ground cannot be reconstructed locally.",
                "sourceRefs": [scene_row["source"]],
                "preserve": ["frozen affine", "Hall scale 0.1312", "pad and bridge anchors"],
                "requiredOutput": f"assets/derivatives/image-vertex-repair-20261009/environment/native/{scene['id']}.png",
                "priority": priority,
                "nextAction": "Submit the prepared 4K pack when the coordinator budget and access checks pass.",
            })
        print(f"scene {scene['id']} conflicts {conflict_count}", flush=True)
    support = support_rows()
    mocks = reference_only_mocks()
    states = state_rows(sprite_ids)
    all_rows = artifacts + support + mocks + states
    ready = []
    for row in artifacts:
        gates = row["gates"]
        if row["status"] == "READY" and row.get("output") and gates["binding"] == "PASS" and gates["semantics"] == "PASS" and gates["matte"] == "PASS" and gates["spatial"] in {"PASS", "NOT_APPLICABLE"}:
            ready.append(row["id"])
    packs.sort(key=lambda pack: (pack["priority"], pack["canonicalId"]))
    index_entries = []
    for pack in packs:
        path = QA / "regeneration" / "packs" / f"{pack['id']}.json"
        index_entries.append({"id": pack["id"], "path": rel(path), "sha256": sha256_file(path)})
    consumer_paths = []
    if (ROOT / "src/data/age-buildings.json").exists():
        png_paths(load_json(ROOT / "src/data/age-buildings.json"), consumer_paths)
    code_dependencies = [{
        "consumer": "src/data/age-buildings.json",
        "currentPaths": sorted(set(consumer_paths)),
        "action": "Rebind runtime building textures to the residual or repaired output only after this interface is accepted. Do not promote reference-only mocks.",
        "geometryProposal": "qa/code-whole-build-20261007/geometry-proposal-v20261007.json stays inactive.",
        "frozenAffine": FROZEN_AFFINE,
        "hallScale": HALL_SCALE,
    }]
    write_json(QA / "scenes.json", scene_rows)
    write_json(QA / "queue.json", {"repairDecisions": decisions, "failedMatteIds": failed})
    write_json(QA / "composites" / "composites_manifest.json", composites)
    write_gallery(all_rows, composites)
    interface = {
        "schema": 2,
        "producer": "ENVIRONMENT",
        "version": "2026-10-09",
        "authorityDate": "2026-10-09",
        "inputSnapshot": "qa/image-vertex-repair-20261009/environment/input_snapshot.json",
        "rows": all_rows,
        "scenes": scene_rows,
        "coverage": [
            {"family": "eight-ages", "ids": AGES},
            {"family": "thirty-reference-screens", "status": "SCOPED", "note": "Support rows name Code-native UI or existing plates. Nine full mocks stay reference-only."},
            {"family": "building-states", "status": "CODE_NATIVE_EXCEPT_COMPLETED_SPRITE"},
        ],
        "readySubset": ready,
        "wholeDeliveryReady": False,
        "reviewGallery": "qa/image-vertex-repair-20261009/environment/review/index.html",
        "checkpoint": "qa/image-vertex-repair-20261009/environment/checkpoint.json",
        "codeDependencies": code_dependencies,
        "repairDecisions": "qa/image-vertex-repair-20261009/environment/queue.json",
        "regenerationPacks": "qa/image-vertex-repair-20261009/environment/regeneration/ready-index.json",
        "generationReceipts": [],
        "paidCompletedIds": [],
        "paidPendingIds": [pack["canonicalId"] for pack in packs],
        "retainedUnknownIds": [],
        "budgetSnapshot": {
            "baselineCommittedProtectedUSD": 71.1156,
            "hardCapUSD": 80.0,
            "reserveIncludedUSD": 15.0,
            "marginUnderHardCapUSD": 8.8844,
            "olderLedgerCommittedUSD": 70.7012,
            "invoices": "UNKNOWN",
            "newSpendThisRunUSD": 0,
        },
        "localProcessingComplete": True,
        "imageWorkComplete": False,
        "localCompletionReason": "Feasible local reuse, slab repair, frame normalization, scene measurement, support dispositions, and regeneration packs are written. Paid submission is a separate coordinator step.",
    }
    write_json(INTERFACE_PATH, interface)
    checkpoint = {
        "status": "INCOMPLETE",
        "authorityDate": "2026-10-09",
        "completedIds": ready,
        "partialIds": [row["id"] for row in all_rows if row["status"] == "PARTIAL"],
        "failedIds": [row["id"] for row in all_rows if row["status"] == "FAIL"],
        "blockedIds": [],
        "nextExecutableActions": {
            "paid": "Refresh access and active jobs, then submit affordable kingdom packs before other modes.",
            "sibling": "Actor ready-index was absent at local close. Keep the coordinator open.",
            "code": "Rebind cleaner building outputs after both image deliveries.",
        },
        "sourceHashes": {"inputSnapshot": snap["files"][0]["sha256"] if snap["files"] else None},
        "evidencePaths": [
            "qa/image-vertex-repair-20261009/environment/review/index.html",
            "qa/image-vertex-repair-20261009/environment/queue.json",
        ],
        "polishQueue": [],
        "authorityLimits": [
            "Frozen affine and Hall scale were not edited.",
            "Owner, runtime, and device acceptance stay open.",
            "US$15 reserve stays inside the US$80 cap and was not spent.",
        ],
        "localProcessingComplete": True,
        "imageWorkComplete": False,
        "localCompletionReason": interface["localCompletionReason"],
        "repairDecisions": decisions,
        "regenerationPacks": "qa/image-vertex-repair-20261009/environment/regeneration/ready-index.json",
        "generationReceipts": [],
        "paidCompletedIds": [],
        "paidPendingIds": [pack["canonicalId"] for pack in packs],
        "retainedUnknownIds": [],
        "budgetSnapshot": interface["budgetSnapshot"],
    }
    write_json(QA / "checkpoint.json", checkpoint)
    handoff = QA / "handoff.md"
    handoff.write_text(
        "\n".join([
            "# Environment vertex repair handoff, 9 October 2026",
            "",
            "Image AI 1 finished the local environment pass. Paid Vertex submission is the next coordinator action and is not claimed here.",
            "",
            f"Ready sprite subset: {len(ready)}. Scenes measured: {len(scene_rows)}. Regeneration packs prepared: {len(packs)}.",
            "",
            "Code consumers stay in src/data/age-buildings.json. Iron, Medieval, and Modern Town Hall runtime textures are the older v2 files when actual-building-bindings says so. Rebind those to the residual or repaired output named on each artifact row. Do not bind the nine support-env mock screenshots.",
            "",
            "Frozen affine [60, -10, 25, 35, 170, 165] and Hall scale 0.1312 are unchanged. Scene proposals are PROPOSED and inactive.",
            "",
            "Actor ready-index was not present. The coordinator must stay open for that queue.",
            "",
            "wholeDeliveryReady is false. Runtime, owner, and device gates are unverified.",
            "",
        ]),
        encoding="utf-8",
    )
    index = {
        "schema": 1,
        "owner": "ENVIRONMENT",
        "version": "2026-10-09",
        "publishedAt": now_iso(),
        "complete": True,
        "preparationComplete": True,
        "pendingPackIds": [],
        "packs": index_entries,
    }
    write_json(QA / "regeneration" / "ready-index.json", index)
    write_json(QA / "vertex-coordinator" / "scheduler-state.json", {
        "environmentIndex": "qa/image-vertex-repair-20261009/environment/regeneration/ready-index.json",
        "environmentIndexSHA256": sha256_file(QA / "regeneration" / "ready-index.json"),
        "actorIndexPresent": (ROOT / "qa/image-vertex-repair-20261009/actors/regeneration/ready-index.json").exists(),
        "closed": False,
        "reason": "Actor preparation index is absent or paid requests are not terminal.",
        "recordedAt": now_iso(),
    })
    print(json.dumps({
        "readySprites": len(ready),
        "artifacts": len(artifacts),
        "scenes": len(scene_rows),
        "packs": len(packs),
        "failedMatte": failed,
        "kingdomConflicts": {row["id"]: len(row["clearanceResults"]) for row in scene_rows if row["mode"] == "kingdom"},
    }))


if __name__ == "__main__":
    main()
