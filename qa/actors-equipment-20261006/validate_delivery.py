from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path("c:/dev/ages-of-dominion-reborn")
INTERFACE_P = ROOT / "docs/plan/ACTORS-EQUIPMENT-INTERFACE-2026-10-06.json"
CHECKPOINT_P = ROOT / "qa/actors-equipment-20261006/checkpoint.json"
HTML_P = ROOT / "qa/actors-equipment-20261006/review/index.html"


def main():
    print("=== Validating Actors & Equipment Delivery ===")
    assert INTERFACE_P.exists(), "Interface JSON missing"
    assert CHECKPOINT_P.exists(), "Checkpoint JSON missing"
    assert HTML_P.exists(), "Review HTML missing"

    iface = json.loads(INTERFACE_P.read_text(encoding="utf-8"))
    assert iface["schema"] == 1
    assert iface["producer"] == "ACTORS"
    assert iface["version"] == "actors-equipment-20261006"
    assert iface["wholeDeliveryReady"] is False

    rows = iface["rows"]
    ready_subset = set(iface["readySubset"])
    print(f"Total artifact rows: {len(rows)}")
    print(f"Ready subset count: {len(ready_subset)}")

    missing_paths = []
    hash_mismatches = []
    for r in rows:
        rid = r["id"]
        if r.get("output"):
            p = ROOT / r["output"]["path"]
            if not p.exists():
                missing_paths.append((rid, "output", r["output"]["path"]))
            else:
                h = hashlib.sha256(p.read_bytes()).hexdigest()
                if h != r["output"]["sha256"]:
                    hash_mismatches.append((rid, "output", h, r["output"]["sha256"]))
        if r.get("source") and r["source"].get("path"):
            p = ROOT / r["source"]["path"]
            if not p.exists():
                missing_paths.append((rid, "source", r["source"]["path"]))
            else:
                h = hashlib.sha256(p.read_bytes()).hexdigest()
                if h != r["source"]["sha256"]:
                    hash_mismatches.append((rid, "source", h, r["source"]["sha256"]))

    print(f"Missing paths: {len(missing_paths)}")
    print(f"Hash mismatches: {len(hash_mismatches)}")
    assert len(missing_paths) == 0, f"Missing paths: {missing_paths[:3]}"
    assert len(hash_mismatches) == 0, f"Hash mismatches: {hash_mismatches[:3]}"

    # Check html images
    html = HTML_P.read_text(encoding="utf-8")
    srcs = re.findall(r'src="([^"]+)"', html)
    print(f"Total img tags in gallery: {len(srcs)}")
    missing_imgs = []
    for s in srcs:
        p = (HTML_P.parent / s).resolve()
        if not p.exists():
            missing_imgs.append((s, str(p)))
    print(f"Missing img paths in gallery: {len(missing_imgs)}")
    if missing_imgs:
        print("Sample missing images:", missing_imgs[:5])
    assert len(missing_imgs) == 0, f"Gallery has broken images: {missing_imgs[:3]}"

    # Checkpoint checks
    cp = json.loads(CHECKPOINT_P.read_text(encoding="utf-8"))
    assert cp["status"] == "INCOMPLETE"
    assert "troop-stone-melee" in cp["blockedIds"]
    assert "troop-stone-ranged" in cp["blockedIds"]
    assert "troop-industrial-ranged" in cp["blockedIds"]
    assert "knight-thigh-greave" in cp["failedIds"]
    assert "healer-head-to-torso" in cp["failedIds"]
    assert "healer-skirt-to-leg" in cp["failedIds"]

    print("ALL VALIDATION CHECKS PASSED.")


if __name__ == "__main__":
    main()
