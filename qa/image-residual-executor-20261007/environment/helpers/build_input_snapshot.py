"""Build immutable input snapshot for Environment Residual Executor (2026-10-07)."""
import os
import json
import hashlib
from pathlib import Path

ROOT = Path("c:/dev/ages-of-dominion-reborn")

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def main():
    snapshot = {
        "timestamp": "2026-10-07T11:00:00Z",
        "producer": "ENVIRONMENT",
        "canonicalAuthority": {},
        "productionBatches": {},
        "highResPlates": {},
        "referenceDelivery": {}
    }

    canonical_files = [
        "docs/plan/FULL-IMPLEMENTATION-SPEC.md",
        "docs/plan/MASTER-PLAN.md",
        "docs/plan/IMPLEMENTATION-CONTRACT.json",
        "docs/plan/GAME-DATA-REFERENCE.json",
        "docs/plan/DATA-ADOPTION-LEDGER.json",
        "docs/plan/SOURCE-EQUATIONS-ADDENDUM-2026-10-03.md",
        "docs/plan/REQUIREMENTS-MATRIX-CANONICAL-2026-10-04.md",
        "docs/plan/WHOLE-PLAN-INDEPENDENT-AUDIT-2026-10-04.md",
        "docs/plan/IMAGE-RESIDUAL-INDEPENDENT-AUDIT-2026-10-07.md",
        "qa/image-residual-20261007/per-id-status.json",
    ]

    for rel in canonical_files:
        p = ROOT / rel
        if p.exists():
            snapshot["canonicalAuthority"][rel] = {
                "sha256": sha256_file(p),
                "bytes": p.stat().st_size
            }

    # Reference 20261006 delivery interface & checkpoint
    ref_files = [
        "docs/plan/ENVIRONMENT-ART-INTERFACE-2026-10-06.json",
        "qa/environment-art-20261006/checkpoint.json",
        "qa/environment-art-20261006/scenes.json"
    ]
    for rel in ref_files:
        p = ROOT / rel
        if p.exists():
            snapshot["referenceDelivery"][rel] = {
                "sha256": sha256_file(p),
                "bytes": p.stat().st_size
            }

    # 145 production sources from 20261006 interface
    with open(ROOT / "docs/plan/ENVIRONMENT-ART-INTERFACE-2026-10-06.json", "r", encoding="utf-8") as f:
        iface = json.load(f)

    for row in iface["rows"]:
        src_path = row["source"]["path"]
        p = ROOT / src_path
        if p.exists():
            snapshot["productionBatches"][src_path] = {
                "id": row["id"],
                "sha256": sha256_file(p),
                "bytes": p.stat().st_size
            }

    # 32 high-res scene plates
    with open(ROOT / "qa/environment-art-20261006/scenes.json", "r", encoding="utf-8") as f:
        scenes = json.load(f)

    for s in scenes:
        src_path = s["source"]["path"]
        p = ROOT / src_path
        if p.exists():
            snapshot["highResPlates"][src_path] = {
                "id": s["id"],
                "sha256": sha256_file(p),
                "bytes": p.stat().st_size,
                "dimensions": s["source"]["dimensions"]
            }

    out_path = ROOT / "qa/image-residual-executor-20261007/environment/input_snapshot.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2)

    print(f"Snapshot written to {out_path}:")
    print(f"  Canonical authorities: {len(snapshot['canonicalAuthority'])}")
    print(f"  Reference delivery: {len(snapshot['referenceDelivery'])}")
    print(f"  Production sources: {len(snapshot['productionBatches'])}")
    print(f"  High-res scene plates: {len(snapshot['highResPlates'])}")

if __name__ == "__main__":
    main()
