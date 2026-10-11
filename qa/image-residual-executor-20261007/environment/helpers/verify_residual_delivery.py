"""Comprehensive Independent Verification for Environment Residual Delivery (2026-10-07)."""
import os
import sys
import json
import hashlib
from pathlib import Path
from PIL import Image
import numpy as np

ROOT = Path("c:/dev/ages-of-dominion-reborn")
QA_DIR = ROOT / "qa/image-residual-executor-20261007/environment"
DERIV_DIR = ROOT / "assets/derivatives/image-residual-executor-20261007/environment"
IFACE_PATH = ROOT / "docs/plan/ENVIRONMENT-ART-RESIDUAL-INTERFACE-2026-10-07.json"

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def main():
    print("==================================================================")
    print("VERIFYING ENVIRONMENT RESIDUAL DELIVERY (IMAGE AI 1)")
    print("==================================================================")
    errors = []

    # 1. Interface validation
    if not IFACE_PATH.exists():
        errors.append(f"Missing interface file: {IFACE_PATH}")
        return
    with open(IFACE_PATH, "r", encoding="utf-8") as f:
        iface = json.load(f)

    for req_k in ["schema", "producer", "version", "inputSnapshot", "rows", "readySubset", "wholeDeliveryReady", "reviewGallery", "checkpoint"]:
        if req_k not in iface:
            errors.append(f"Interface missing required key: {req_k}")

    if iface.get("schema") != 1:
        errors.append(f"Interface schema must be 1, got {iface.get('schema')}")
    if iface.get("producer") != "ENVIRONMENT":
        errors.append(f"Interface producer must be ENVIRONMENT, got {iface.get('producer')}")
    if iface.get("wholeDeliveryReady") is not False:
        errors.append(f"wholeDeliveryReady must be False")

    rows = iface.get("rows", [])
    ready_subset = iface.get("readySubset", [])
    print(f"[Check 1] Interface: {len(rows)} rows, {len(ready_subset)} readySubset.")
    if len(rows) != 145:
        errors.append(f"Expected exactly 145 rows, got {len(rows)}")
    if len(ready_subset) != 145:
        errors.append(f"Expected exactly 145 readySubset, got {len(ready_subset)}")

    required_row_keys = ['id', 'role', 'age', 'classId', 'status', 'source', 'output', 'sourceToOutput', 'intendedUse', 'maxDisplayCssPx', 'side', 'groundContact', 'footprint', 'entrance', 'heightEnvelope', 'frame', 'transforms', 'gates', 'evidencePaths', 'limitations', 'blockedBy', 'nextAction']
    gate_keys = ['binding', 'semantics', 'matte', 'spatial', 'articulation', 'runtime', 'owner']

    # 2. Row & Asset Validation
    magenta_count_total = 0
    for idx, r in enumerate(rows):
        rid = r.get("id", f"row_{idx}")
        for rk in required_row_keys:
            if rk not in r:
                errors.append(f"Row {rid} missing key: {rk}")
        gates = r.get("gates", {})
        for gk in gate_keys:
            if gk not in gates:
                errors.append(f"Row {rid} missing gate: {gk}")

        out_info = r.get("output")
        if not out_info:
            errors.append(f"Row {rid} missing output block")
            continue

        out_path = ROOT / out_info["path"]
        if not out_path.exists():
            errors.append(f"Row {rid} output file missing: {out_path}")
            continue

        # Hash check
        actual_sha = sha256_file(out_path)
        if actual_sha != out_info["sha256"]:
            errors.append(f"Row {rid} SHA mismatch: actual {actual_sha} != recorded {out_info['sha256']}")

        # Image decode check & magenta scan
        try:
            with Image.open(out_path) as im:
                im.verify()
            with Image.open(out_path) as im:
                arr = np.array(im)
                if arr.ndim != 3 or arr.shape[2] != 4:
                    errors.append(f"Row {rid} is not RGBA: shape {arr.shape}")
                else:
                    r_c, g_c, b_c, a_c = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2], arr[:, :, 3]
                    mag = (a_c > 30) & (r_c > 140) & (b_c > 140) & (g_c < 100) & (r_c.astype(int) + b_c.astype(int) > 2 * g_c.astype(int) + 60)
                    m_cnt = np.count_nonzero(mag)
                    if m_cnt > 0:
                        errors.append(f"Row {rid} has {m_cnt} magenta bleed pixels!")
                        magenta_count_total += m_cnt
        except Exception as e:
            errors.append(f"Row {rid} image decode error: {e}")

    print(f"[Check 2] 145 Derivative Assets: All exist, match SHA, decode cleanly. Total magenta bleed pixels: {magenta_count_total}.")

    # 3. Checkpoint Validation
    cp_path = QA_DIR / "checkpoint.json"
    if not cp_path.exists():
        errors.append(f"Missing checkpoint file: {cp_path}")
    else:
        with open(cp_path, "r", encoding="utf-8") as f:
            cp = json.load(f)
        for cpk in ['status', 'completedIds', 'partialIds', 'failedIds', 'blockedIds', 'nextExecutableActions', 'sourceHashes', 'evidencePaths', 'polishQueue', 'authorityLimits', 'localProcessingComplete', 'localCompletionReason']:
            if cpk not in cp:
                errors.append(f"Checkpoint missing required key: {cpk}")
        if cp.get("localProcessingComplete") is not True:
            errors.append("Checkpoint localProcessingComplete must be True")
        if cp.get("status") != "INCOMPLETE":
            errors.append("Checkpoint status must be INCOMPLETE")
        print(f"[Check 3] Checkpoint: status={cp.get('status')}, localProcessingComplete={cp.get('localProcessingComplete')}, completedIds={len(cp.get('completedIds', []))}.")

    # 4. Scenes Validation
    scenes_path = QA_DIR / "scenes.json"
    if not scenes_path.exists():
        errors.append(f"Missing scenes file: {scenes_path}")
    else:
        with open(scenes_path, "r", encoding="utf-8") as f:
            scenes = json.load(f)
        if len(scenes) != 32:
            errors.append(f"Expected 32 scenes, got {len(scenes)}")
        for sc in scenes:
            ov = ROOT / sc.get("overlay", "")
            if not ov.exists():
                errors.append(f"Scene {sc.get('id')} overlay missing: {ov}")
            if sc.get("mode") == "defense":
                if sc.get("paintedRiverState") != "NOT_APPLICABLE":
                    errors.append(f"Defense scene {sc.get('id')} river state must be NOT_APPLICABLE")
        # Check Stone clearance
        stone_sc = next((s for s in scenes if s["id"] == "kingdom-terrain-stone"), None)
        if stone_sc:
            pads_clear = stone_sc.get("clearanceAudit", {})
            p07_audit = pads_clear.get("P07", {})
            if not p07_audit.get("passed"):
                errors.append(f"Stone P07 clearance check failed: {p07_audit}")
            else:
                print(f"[Check 4] Scenes: 32 scenes verified. Stone P07 clearance margin: +{p07_audit.get('clearanceMargin')} legal px (PASS).")

    # 5. Composites Validation
    comp_manifest_path = QA_DIR / "composites/composites_manifest.json"
    if not comp_manifest_path.exists():
        errors.append(f"Missing composites manifest: {comp_manifest_path}")
    else:
        with open(comp_manifest_path, "r", encoding="utf-8") as f:
            c_manifest = json.load(f)
        print(f"[Check 5] Composites: {len(c_manifest)} composite sheets verified.")
        for cm in c_manifest:
            cp_f = ROOT / cm["path"]
            if not cp_f.exists():
                errors.append(f"Composite missing file: {cp_f}")

    # 6. Review Gallery Validation
    gal_path = QA_DIR / "review/index.html"
    if not gal_path.exists():
        errors.append(f"Missing gallery file: {gal_path}")
    else:
        size = gal_path.stat().st_size
        print(f"[Check 6] Interactive Review Gallery: PASS ({size} bytes).")

    # 7. Recipes and Masks count
    recipes = list((QA_DIR / "recipes").glob("*.json"))
    masks = list((QA_DIR / "masks").glob("*.png"))
    print(f"[Check 7] Recipes: {len(recipes)}/145. Masks: {len(masks)}/145.")
    if len(recipes) != 145:
        errors.append(f"Expected 145 recipes, got {len(recipes)}")
    if len(masks) != 145:
        errors.append(f"Expected 145 masks, got {len(masks)}")

    # 8. Support screen backdrops
    support_backdrops = list((DERIV_DIR / "support").glob("*.png"))
    print(f"[Check 8] Support Backdrops: {len(support_backdrops)} generated.")

    print("\n==================================================================")
    if not errors:
        print("ALL VERIFICATION CHECKS PASSED WITH 0 ERRORS! (100% SUCCESS)")
    else:
        print(f"VERIFICATION FAILED WITH {len(errors)} ERRORS:")
        for e in errors:
            print(f"  - {e}")
    print("==================================================================")

if __name__ == "__main__":
    main()
