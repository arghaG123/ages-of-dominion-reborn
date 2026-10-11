"""
Independent Verification Script for ACTORS/EQUIPMENT Residual Delivery (7 Oct 2026)
"""

import sys
import json
import hashlib
from pathlib import Path
from PIL import Image

ROOT = Path("c:/dev/ages-of-dominion-reborn").resolve()
IFACE_P = ROOT / "docs/plan/ACTORS-EQUIPMENT-RESIDUAL-INTERFACE-2026-10-07.json"
CHECKPOINT_P = ROOT / "qa/image-residual-executor-20261007/actors/checkpoint.json"

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def test_interface():
    print("Test 1: Validating Interface Schema and Counts...")
    assert IFACE_P.exists(), f"Interface missing: {IFACE_P}"
    with open(IFACE_P, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data.get("schema") == 1
    assert data.get("producer") == "ACTORS"
    assert data.get("version") == "image-residual-executor-20261007"

    rows = data["rows"]
    assert len(rows) == 167, f"Expected exactly 167 rows, got {len(rows)}"

    ready_rows = [r for r in rows if r["status"] == "READY"]
    partial_rows = [r for r in rows if r["status"] == "PARTIAL"]
    fail_rows = [r for r in rows if r["status"] == "FAIL"]
    blocked_rows = [r for r in rows if r["status"] == "BLOCKED"]

    assert len(ready_rows) == 148, f"Expected 148 READY rows, got {len(ready_rows)}"
    assert len(partial_rows) == 13, f"Expected 13 PARTIAL rows, got {len(partial_rows)}"
    assert len(fail_rows) == 6, f"Expected 6 FAIL rows, got {len(fail_rows)}"
    assert len(blocked_rows) == 0, f"Expected 0 BLOCKED rows, got {len(blocked_rows)}"

    ready_ids = [r["id"] for r in ready_rows]
    ready_subset = data["readySubset"]
    assert set(ready_subset) == set(ready_ids), "readySubset does not match READY rows!"
    assert len(ready_subset) == 148, f"readySubset length mismatch: {len(ready_subset)}"

    # Check unique IDs
    all_ids = [r["id"] for r in rows]
    assert len(all_ids) == len(set(all_ids)), "Duplicate row IDs found!"

    # Check healer-leg-greave and healer-greave-boot
    for jid in ["healer-leg-greave", "healer-greave-boot"]:
        matches = [r for r in rows if r["id"] == jid]
        assert len(matches) == 1, f"Missing {jid} in rows"
        assert matches[0]["status"] == "READY", f"{jid} status should be READY"
        assert matches[0]["transforms"].get("poses") is not None, f"{jid} missing poses"

    # Check 6 failed IDs
    failed_expected = [
        "healer-head-to-torso", "healer-skirt-to-leg", "knight-thigh-greave",
        "paladin-greave-boot", "paladin-head-raster", "paladin-thigh-knee"
    ]
    for fid in failed_expected:
        matches = [r for r in rows if r["id"] == fid]
        assert len(matches) == 1, f"Missing failed ID {fid}"
        assert matches[0]["status"] == "FAIL", f"{fid} status should be FAIL"
        assert len(matches[0]["blockedBy"]) > 0 or len(matches[0]["limitations"]) > 0

    # Check partial waist link
    matches = [r for r in rows if r["id"] == "healer-torso-to-skirt"]
    assert len(matches) == 1, "Missing healer-torso-to-skirt"
    assert matches[0]["status"] == "PARTIAL", "healer-torso-to-skirt should be PARTIAL"

    # Check 4 regenerated roles
    regen_expected = ["troop-stone-melee", "troop-stone-ranged", "troop-industrial-ranged", "troop-industrial-heavy"]
    for rid in regen_expected:
        matches = [r for r in rows if r["id"] == rid]
        assert len(matches) == 1, f"Missing regenerated ID {rid}"
        assert matches[0]["status"] == "READY", f"{rid} should be READY"
        assert matches[0]["output"] is not None, f"{rid} output should not be None"
        out_p = ROOT / matches[0]["output"]["path"]
        assert out_p.exists(), f"Output file missing for {rid}: {out_p}"

    print("Interface Schema and Counts: PASS")

def test_decoded_dimensions_and_hashes():
    print("Test 2: Validating Decoded Image Dimensions and SHA256 Hashes...")
    with open(IFACE_P, "r", encoding="utf-8") as f:
        data = json.load(f)

    for r in data["rows"]:
        out = r.get("output")
        if out is not None:
            out_p = ROOT / out["path"]
            assert out_p.exists(), f"Output file does not exist: {out_p} for row {r['id']}"
            h = sha256_file(out_p)
            assert h == out["sha256"], f"Hash mismatch for {r['id']}: expected {out['sha256']}, got {h}"

            im = Image.open(out_p)
            w, h = im.size
            exp_w, exp_h = out["dimensions"]
            assert (w, h) == (exp_w, exp_h), f"Dimension mismatch for {r['id']}: expected {exp_w}x{exp_h}, got {w}x{h}"

    # Specific dimension checks
    expected_dims = {
        "healer-leg-subchain": [203, 858],
        "healer-chain-diagram": [1040, 320],
        "ranger-chain-diagram": [520, 320],
        "mage-chain-diagram": [520, 320],
        "warlock-chain-diagram": [520, 320],
        "necromancer-chain-diagram": [520, 320],
        "barbarian-chain-diagram": [520, 320],
        "knight-chain-diagram": [780, 320],
        "paladin-chain-diagram": [780, 320],
    }

    row_map = {r["id"]: r for r in data["rows"]}
    for k, v in expected_dims.items():
        assert k in row_map, f"Missing {k}"
        dims = row_map[k]["output"]["dimensions"]
        assert dims == v, f"{k} dimensions mismatch: expected {v}, got {dims}"
        assert row_map[k]["sourceToOutput"] is None, f"{k} sourceToOutput should be null"

    print("Decoded Image Dimensions and Hashes: PASS")

def test_checkpoint():
    print("Test 3: Validating Checkpoint Consistency...")
    with open(CHECKPOINT_P, "r", encoding="utf-8") as f:
        cp = json.load(f)

    with open(IFACE_P, "r", encoding="utf-8") as f:
        iface = json.load(f)

    assert cp["localProcessingComplete"] is True
    assert cp["status"] == "IMAGE_RESIDUAL_EXECUTOR_20261007_COMPLETE"

    ready_ids = [r["id"] for r in iface["rows"] if r["status"] == "READY"]
    partial_ids = [r["id"] for r in iface["rows"] if r["status"] == "PARTIAL"]
    failed_ids = [r["id"] for r in iface["rows"] if r["status"] == "FAIL"]
    blocked_ids = [r["id"] for r in iface["rows"] if r["status"] == "BLOCKED"]

    assert set(cp["completedIds"]) == set(ready_ids)
    assert set(cp["partialIds"]) == set(partial_ids)
    assert set(cp["failedIds"]) == set(failed_ids)
    assert set(cp["blockedIds"]) == set(blocked_ids)

    print("Checkpoint Consistency: PASS")

def test_composites():
    print("Test 4: Validating Multi-Viewport Composites...")
    comp_dir = ROOT / "qa/image-residual-executor-20261007/actors/composites"
    expected_files = [
        "hero-equipment-825x375.jpg", "hero-equipment-933x424.jpg", "hero-equipment-1180x820.jpg", "hero-equipment-1280x720.jpg",
        "army-825x375.jpg", "army-933x424.jpg", "army-1180x820.jpg", "army-1280x720.jpg",
        "forge-825x375.jpg", "forge-933x424.jpg", "forge-1180x820.jpg", "forge-1280x720.jpg",
        "battle-825x375.jpg", "battle-933x424.jpg", "battle-1180x820.jpg", "battle-1280x720.jpg"
    ]
    for ef in expected_files:
        p = comp_dir / ef
        assert p.exists(), f"Composite missing: {ef}"
        assert p.stat().st_size > 1000, f"Composite too small: {ef}"

    print("Multi-Viewport Composites: PASS")

def test_repaired_troops():
    print("Test 5: Validating Repaired Troops...")
    diag_dir = ROOT / "qa/image-residual-executor-20261007/actors/diagnostics"
    recipe_dir = ROOT / "qa/image-residual-executor-20261007/actors/recipes"
    mask_dir = ROOT / "qa/image-residual-executor-20261007/actors/masks"

    for tid in ["troop-industrial-melee", "troop-modern-ranged", "troop-modern-heavy"]:
        ba = diag_dir / f"{tid}-before-after.png"
        assert ba.exists(), f"Missing before/after comparison for {tid}"
        recipe = recipe_dir / f"{tid}-repair.json"
        assert recipe.exists(), f"Missing recipe for {tid}"
        mask = mask_dir / f"{tid}-mask.png"
        assert mask.exists(), f"Missing mask for {tid}"

    print("Repaired Troops: PASS")

if __name__ == "__main__":
    print("=" * 60)
    print("Running Independent Delivery Validation...")
    print("=" * 60)
    test_interface()
    test_decoded_dimensions_and_hashes()
    test_checkpoint()
    test_composites()
    test_repaired_troops()
    print("=" * 60)
    print("ALL 5 VALIDATION SUITES PASSED PERFECTLY!")
    print("=" * 60)
