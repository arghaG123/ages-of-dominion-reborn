"""Reconcile stale Image hashes and false missing scene sources.

Preserves the 9 October interface bytes. Writes a new revision under
docs/plan and qa/image-reconcile-20261011. Does not edit pixels, geometry,
ledgers, or receipts, and does not promote a spatial FAIL to PASS.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "qa" / "image-reconcile-20261011"
INTERFACE = ROOT / "docs" / "plan" / "IMAGE-UNIFIED-RESERVE-INTERFACE-2026-10-09.json"
SCENES = ROOT / "qa" / "image-unified-reserve-20261009" / "scenes.json"
PLATES = ROOT / "qa" / "image-unified-reserve-20261009" / "diagnostics" / "plates.json"
BODIES = ROOT / "qa" / "image-unified-reserve-20261009" / "diagnostics" / "bodies.json"
MODES = ROOT / "src" / "data" / "mode-scenes.json"
GUIDES = [
    (
        "qa/recovery-executor-20261003/guides/kingdom-stone-day1-composition-v4-guide.png",
        "609d3195018ccf448f339f79e45fe90b9e5adfb2859674e40383144d2106f848",
        52050,
    ),
    (
        "qa/recovery-executor-20261003/guides/kingdom-stone-day1-composition-v5-guide.png",
        "673492a6a1c6780eb77d9b0b24f7eefe30a98dc119c7fbee9e3edef088b8c1ff",
        33988,
    ),
]
PROTECTED = [
    ("assets/runtime-code-20261007/troops/troop-stone-melee.png", "c61f0e3dec06a344744f3f4d21a6cf7dabdb4df61730c42eac535c7988f2104a"),
    ("assets/runtime-code-20261007/troops/troop-industrial-ranged.png", "5df473c9336451f51f2babf21ed88b7c5dc8bd5bc901615b8851a07c5183823f"),
    ("assets/runtime-code-20261007/troops/troop-industrial-heavy.png", "9455bf02f32921c7fa0bf3d2bce4f561e9c311a37e36ad99bd3dbafa7fcbc758"),
    ("assets/derivatives/image-vertex-repair-20261009/actors/troops/troop-stone-ranged.png", "53233e6284322f73650529bcfe08f8141e37897cca0a57b0b3454a547dd97ba3"),
    ("assets/derivatives/rigs/v7/healer/boot.png", "4a700eeedbabc9710db137491825d0c2ec439db15b10c619f0997a93accfab21"),
]
MODE_KEY = {"ADVENTURE": "adventure", "TACTICAL": "tactical", "DEFENSE": "defense"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def dimensions(path: Path):
    if path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp", ".gif"}:
        return None
    with Image.open(path) as image:
        image.load()
        return {"width": image.size[0], "height": image.size[1]}


def file_ref(rel: str) -> dict:
    path = ROOT / rel
    raw = path.read_bytes()
    return {
        "path": rel.replace("\\", "/"),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "bytes": len(raw),
        "dimensions": dimensions(path),
    }


def refresh_ref(node: dict, stale: list) -> None:
    rel = node.get("path")
    recorded = node.get("sha256")
    if not isinstance(rel, str) or not isinstance(recorded, str):
        return
    path = ROOT / rel
    if not path.is_file():
        stale.append({"path": rel, "status": "MISSING", "recorded": recorded})
        return
    actual = file_ref(rel)
    hash_match = actual["sha256"] == recorded
    bytes_match = node.get("bytes") in (None, actual["bytes"])
    dims_match = node.get("dimensions") in (None, actual["dimensions"])
    if hash_match and bytes_match and dims_match:
        if node.get("bytes") is None:
            node["bytes"] = actual["bytes"]
        if node.get("dimensions") is None and actual["dimensions"] is not None:
            node["dimensions"] = actual["dimensions"]
        return
    stale.append({
        "path": rel,
        "status": "STALE" if not hash_match else "METADATA",
        "recorded": recorded,
        "actual": actual["sha256"],
        "recordedBytes": node.get("bytes"),
        "actualBytes": actual["bytes"],
    })
    if not hash_match:
        node["sha256"] = actual["sha256"]
    node["bytes"] = actual["bytes"]
    if actual["dimensions"] is not None and node.get("dimensions") != actual["dimensions"]:
        node["dimensions"] = actual["dimensions"]


def walk(node, stale: list) -> None:
    if isinstance(node, dict):
        if "path" in node and "sha256" in node and isinstance(node["path"], str):
            refresh_ref(node, stale)
        for value in node.values():
            walk(value, stale)
    elif isinstance(node, list):
        for value in node:
            walk(value, stale)


def bind_scenes(rows: list, catalog: dict) -> dict:
    bound = 0
    still_missing = []
    for row in rows:
        mode = MODE_KEY.get(row.get("mode"))
        age = row.get("age")
        blocked = row.get("blockedBy") or []
        if mode is None or "source image missing" not in blocked:
            continue
        paths = catalog.get(mode) or []
        if not isinstance(age, int) or age < 0 or age >= len(paths):
            still_missing.append(row.get("id"))
            continue
        rel = paths[age]
        path = ROOT / rel
        if not path.is_file():
            still_missing.append({"id": row.get("id"), "path": rel})
            continue
        row["source"] = file_ref(rel)
        row["sources"] = [row["source"]]
        row["blockedBy"] = [item for item in blocked if item != "source image missing"]
        row.setdefault("gates", {})
        row["gates"]["binding"] = "PASS"
        row["gates"]["spatial"] = row["gates"].get("spatial", "FAIL")
        note = "Source path is the existing biome catalog file. Spatial, road, bank, deck, and approach gates stay FAIL."
        limits = row.setdefault("limitations", [])
        if note not in limits:
            limits.append(note)
        bound += 1
    return {"bound": bound, "stillMissing": still_missing}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    interface = json.loads(INTERFACE.read_text(encoding="utf-8"))
    scenes = json.loads(SCENES.read_text(encoding="utf-8"))
    plates = json.loads(PLATES.read_text(encoding="utf-8"))
    bodies = json.loads(BODIES.read_text(encoding="utf-8"))
    catalog = json.loads(MODES.read_text(encoding="utf-8"))
    stale = []
    walk(interface, stale)
    walk(scenes, stale)
    walk(plates, stale)
    walk(bodies, stale)
    scene_bind = bind_scenes(interface.get("scenes") or [], catalog)
    scene_file_bind = bind_scenes(scenes, catalog)
    guides = []
    for rel, expected, size in GUIDES:
        path = ROOT / rel
        if not path.is_file():
            guides.append({"path": rel, "status": "BLOCKED", "expected": expected, "bytes": size})
            continue
        actual = sha256_file(path)
        guides.append({
            "path": rel,
            "status": "PASS" if actual == expected and path.stat().st_size == size else "FAIL",
            "expected": expected,
            "actual": actual,
        })
    protected = []
    for rel, expected in PROTECTED:
        path = ROOT / rel
        if not path.is_file():
            protected.append({"path": rel, "status": "MISSING"})
            continue
        actual = sha256_file(path)
        protected.append({"path": rel, "status": "PASS" if actual == expected else "FAIL", "sha256": actual})
    interface["schema"] = 4
    interface["version"] = "image-reconcile-20261011"
    interface["priorInterface"] = "docs/plan/IMAGE-UNIFIED-RESERVE-INTERFACE-2026-10-09.json"
    interface["imageWorkComplete"] = False
    interface["localProcessingComplete"] = False
    interface["note"] = (
        "Hash fields were refreshed from current bytes. Scene binding uses src/data/mode-scenes.json. "
        "Spatial FAIL, standing bodies, and missing exact guides are unchanged. No pixels were rewritten."
    )
    report = {
        "status": "INCOMPLETE",
        "staleOrMissingRefs": len(stale),
        "stale": stale,
        "interfaceSceneBinding": scene_bind,
        "scenesFileBinding": scene_file_bind,
        "guides": guides,
        "protected": protected,
        "spatialPassCount": sum(1 for row in interface.get("scenes") or [] if (row.get("gates") or {}).get("spatial") == "PASS"),
        "sceneBindingPassCount": sum(1 for row in interface.get("scenes") or [] if (row.get("gates") or {}).get("binding") == "PASS"),
        "bindingPassAdded": scene_bind["bound"],
    }
    (OUT / "hash-reconciliation.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (OUT / "scenes.json").write_text(json.dumps(scenes, indent=2), encoding="utf-8")
    (OUT / "plates.json").write_text(json.dumps(plates, indent=2), encoding="utf-8")
    (OUT / "bodies.json").write_text(json.dumps(bodies, indent=2), encoding="utf-8")
    dest = ROOT / "docs" / "plan" / "IMAGE-RECONCILE-INTERFACE-2026-10-11.json"
    dest.write_text(json.dumps(interface, indent=2), encoding="utf-8")
    print(json.dumps({
        "staleOrMissingRefs": len(stale),
        "bound": scene_bind["bound"],
        "stillMissing": scene_bind["stillMissing"],
        "guides": guides,
        "protected": [row["status"] for row in protected],
        "spatialPassCount": report["spatialPassCount"],
    }, indent=2))


if __name__ == "__main__":
    main()
