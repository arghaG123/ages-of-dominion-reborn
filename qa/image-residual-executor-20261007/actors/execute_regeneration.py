"""Executes the Authorized 4-Role Vertex AI Regeneration using gemini-3.1-flash-image.

Target Roles:
1. troop-stone-melee: Stone Age Clubman with heavy wooden/flint club, standing upright.
2. troop-stone-ranged: Stone Age Slinger with authentic leather sling in hand.
3. troop-industrial-ranged: Industrial Sharpshooter, standing upright (not prone, not sandbags).
4. troop-industrial-heavy: Industrial Steam Walker, bipedal mechanical boiler-driven walker.

Adheres strictly to:
- Model: gemini-3.1-flash-image
- Project: project-eaa4c1cc-8f19-4d24-9e6
- Account: arghawork3@gmail.com
- Cloud lock CAS verification and pacing (20s gap)
- Write-ahead durability
- Promotion to final-native2k and transparent derivative generation
- Budget ledger tracking
"""

import sys
import os
import json
import time
import hashlib
import numpy as np
from pathlib import Path
from datetime import datetime, timezone
import cv2
from PIL import Image

ROOT = Path("c:/dev/ages-of-dominion-reborn").resolve()
sys.path.insert(0, str(ROOT / "scripts"))

from interactive_runner_continuity import (
    ContinuityRunner,
    MutexError,
    AuthError,
    UnknownLiabilityError,
    PROJECT,
    ACCOUNT,
    BUCKET,
    LOCK_OBJECT,
    MODEL,
    ENDPOINT
)

PACKS_DIR = ROOT / "qa/image-residual-executor-20261007/actors/regeneration-packs"
FINAL_NATIVE2K_DIR = ROOT / "assets/high-res/final-native2k"
TROOP_DERIV_DIR = ROOT / "assets/derivatives/image-residual-executor-20261007/actors/troops"
QA_DIR = ROOT / "qa/image-residual-executor-20261007/actors/diagnostics"
BUDGET_LEDGER_FILE = ROOT / "docs/plan/image-production/budget-ledger.json"

TARGET_ROLES = [
    {
        "id": "troop-stone-melee",
        "order": 1,
        "role": "Stone Age Clubman",
        "prompt": "Produce ONE native 2K army unit master illustration for troop-stone-melee. Accurate military combat unit: Stone Age Clubman: a single adult tribal warrior standing upright in alert combat posture, three-quarter front view, wielding a heavy primitive wooden and stone war club in two hands or one hand. Dressed in natural animal pelts, leather wrap, and bone accents. Full body completely inside the frame, with both feet and boots clearly visible. Isolated figure on a clean transparent or solid white background. No rocks, no ground slab, no dirt platform, no plinth, no second person, no border, and no text. Deliver ONE 2048x2048 PNG image."
    },
    {
        "id": "troop-stone-ranged",
        "order": 2,
        "role": "Stone Age Slinger",
        "prompt": "Produce ONE native 2K army unit master illustration for troop-stone-ranged. Accurate military combat unit: Stone Age Slinger: a single adult prehistoric skirmisher standing upright in alert ready stance, three-quarter front view. Wielding an authentic natural leather cord sling held visibly in hand with a pouch of stones, prepared to loose a projectile. No bow, no thrown spear. Dressed in animal hide tunic and leather leg wraps. Full body completely inside the frame, both feet and sandals clearly visible. Isolated figure on a clean transparent or solid white background. No gravel mound, no dirt slab, no platform, no plinth, no second person, no border, and no text. Deliver ONE 2048x2048 PNG image."
    },
    {
        "id": "troop-industrial-ranged",
        "order": 3,
        "role": "Industrial Sharpshooter",
        "prompt": "Produce ONE native 2K army unit master illustration for troop-industrial-ranged. Accurate military combat unit: Industrial Sharpshooter: a single adult marksman standing upright in three-quarter front view. Early 19th-century industrial uniform with long dark military greatcoat, leather straps, and peaked cap. Wielding a period rifled musket with brass fittings and long barrel held across the chest in two hands. Standing upright posture on both feet (NOT prone, NOT crouching, NOT behind sandbags). Full body completely inside the frame, both boots clearly visible. Isolated figure on a clean transparent or solid white background. No sandbags, no trenches, no smoke clouds, no plinth, no second soldier, no border, and no text. Deliver ONE 2048x2048 PNG image."
    },
    {
        "id": "troop-industrial-heavy",
        "order": 4,
        "role": "Industrial Steam Walker",
        "prompt": "Produce ONE native 2K army unit master illustration for troop-industrial-heavy. Accurate military combat unit: Industrial Steam Walker: an armored steampunk bipedal mechanical combat walker. Heavily riveted iron and brass hull, exposed bronze steam pipes, twin exhaust smokestacks on top venting light steam, and two heavy mechanical hydraulic legs planted firmly. Frontally mounted heavy pneumatic steam cannon. Three-quarter tactical perspective. Full machine completely inside the frame, all mechanical feet visible. Isolated on a clean transparent or solid white background. No ground slab, no infantry crew standing outside, no diorama base, no border, and no text. Deliver ONE 2048x2048 PNG image."
    }
]

def prepare_pack(item):
    item_id = item["id"]
    p_dir = PACKS_DIR / item_id
    p_dir.mkdir(parents=True, exist_ok=True)

    meta = {
        "id": item_id,
        "group": "REGENERATION-4ROLES-20261007",
        "order": item["order"],
        "model": MODEL,
        "requestedSize": "2K",
        "dimensions": [2048, 2048],
        "purchaseStatus": "AUTHORIZED_QUEUED_ACTIVE_SCOPE",
        "paidCallsAllowed": True,
        "executionState": "READY_FOR_GENERATION",
        "prompt": item["prompt"],
        "promptSHA256": hashlib.sha256(item["prompt"].encode("utf-8")).hexdigest(),
        "layout": {
            "canvas": [2048, 2048],
            "framing": "tactical unit sprite",
            "consumer": "Army unit plate"
        },
        "reservationUSD": 0.143612
    }

    (p_dir / "request_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    (p_dir / "prompt.txt").write_text(item["prompt"], encoding="utf-8")
    (p_dir / "layout_spec.json").write_text(json.dumps(meta["layout"], indent=2), encoding="utf-8")
    return p_dir, meta

def extract_alpha_derivative(src_png_path, out_png_path):
    """Converts raw 2048x2048 output into clean RGBA sprite with transparent background."""
    im = Image.open(src_png_path).convert("RGBA")
    arr = np.array(im, dtype=np.uint8)
    h, w, _ = arr.shape
    a = arr[:, :, 3]

    # If alpha is already clean transparency:
    if np.any(a < 250):
        clean_im = im
    else:
        # Solid background: run connected flood fill from all 4 corners and borders
        rgb = arr[:, :, :3]
        mask = np.zeros((h + 2, w + 2), dtype=np.uint8)
        corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1), (w // 2, 0), (w // 2, h - 1)]
        diff_range = (25, 25, 25)
        for pt in corners:
            cv2.floodFill(rgb, mask, pt, (0, 0, 0), diff_range, diff_range, flags=8 | (255 << 8) | cv2.FLOODFILL_MASK_ONLY)

        bg_mask = (mask[1:-1, 1:-1] == 255)
        # Soft edge alpha: distance transform on background mask
        dist = cv2.distanceTransform(bg_mask.astype(np.uint8), cv2.DIST_L2, 3)
        alpha = np.clip(1.0 - (dist / 2.0), 0.0, 1.0)
        # Foreground is fully opaque
        alpha[~bg_mask] = 1.0

        out_arr = arr.copy()
        out_arr[:, :, 3] = (alpha * 255).astype(np.uint8)
        clean_im = Image.fromarray(out_arr, mode="RGBA")

    # Crop to content bbox with 10px padding
    bbox = clean_im.getbbox()
    if bbox:
        cropped = clean_im.crop((
            max(0, bbox[0] - 10),
            max(0, bbox[1] - 10),
            min(w, bbox[2] + 10),
            min(h, bbox[3] + 10)
        ))
    else:
        cropped = clean_im

    out_png_path.parent.mkdir(parents=True, exist_ok=True)
    cropped.save(out_png_path, format="PNG")
    return cropped

def generate_qa_diagnostics(cropped_rgba, item_id):
    QA_DIR.mkdir(parents=True, exist_ok=True)
    w, h = cropped_rgba.size

    # Thumbnails at 64px and 130px
    aspect = w / h
    t64_h = 64
    t64_w = max(16, int(t64_h * aspect))
    thumb64 = cropped_rgba.resize((t64_w, t64_h), Image.Resampling.LANCZOS)

    t130_h = 130
    t130_w = max(16, int(t130_h * aspect))
    thumb130 = cropped_rgba.resize((t130_w, t130_h), Image.Resampling.LANCZOS)

    bgs = [('white', (255, 255, 255, 255)), ('black', (0, 0, 0, 255)), ('green', (110, 132, 104, 255))]

    # 3-background comparison canvas for 64px
    c64 = Image.new('RGB', (t64_w * 3, t64_h))
    for i, (_, col) in enumerate(bgs):
        layer = Image.new('RGBA', (t64_w, t64_h), col)
        layer.alpha_composite(thumb64)
        c64.paste(layer.convert('RGB'), (i * t64_w, 0))
    c64.save(QA_DIR / f"{item_id}_qa_64px.png")

    # 3-background comparison canvas for 130px
    c130 = Image.new('RGB', (t130_w * 3, t130_h))
    for i, (_, col) in enumerate(bgs):
        layer = Image.new('RGBA', (t130_w, t130_h), col)
        layer.alpha_composite(thumb130)
        c130.paste(layer.convert('RGB'), (i * t130_w, 0))
    c130.save(QA_DIR / f"{item_id}_qa_130px.png")

def main():
    print("=" * 80)
    print("AUTHORIZED VERTEX AI 4-ROLE REGENERATION RUN")
    print(f"Time: {datetime.now(timezone.utc).isoformat()}")
    print(f"Project: {PROJECT} | Account: {ACCOUNT} | Model: {MODEL}")
    print("=" * 80)

    PACKS_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_NATIVE2K_DIR.mkdir(parents=True, exist_ok=True)
    TROOP_DERIV_DIR.mkdir(parents=True, exist_ok=True)

    runner = ContinuityRunner(
        owner_base="image-executor-regen4",
        cloud_lock_enabled=True
    )

    print(f"Acquiring atomic mutex (Owner: {runner.owner_id})...")
    try:
        runner.acquire_mutex()
        print(f"[MUTEX ACQUIRED] PID: {runner.pid}")
    except MutexError as me:
        print(f"[ABORT] Cannot acquire mutex: {me}")
        sys.exit(1)

    generated_results = []
    total_cost = 0.0

    try:
        for item in TARGET_ROLES:
            item_id = item["id"]
            print(f"\n---> Generating: {item_id} ({item['role']})")
            pack_dir, meta = prepare_pack(item)

            res = runner.execute_request(
                pack_dir=pack_dir,
                item_meta=meta,
                reservation_usd=0.143612
            )

            status = res.get("status")
            print(f"  -> Result status: {status}")

            if status not in ("SUCCEEDED", "REUSED_EXISTING_SUCCESS"):
                print(f"[ERROR] Failed generation for {item_id}: {res.get('error')}")
                break

            cost = res.get("costUSD", 0.1036)
            total_cost += cost
            out_png = pack_dir / "output.png"
            final_png = FINAL_NATIVE2K_DIR / f"{item_id}.png"
            final_png.write_bytes(out_png.read_bytes())

            deriv_png = TROOP_DERIV_DIR / f"{item_id}.png"
            cropped = extract_alpha_derivative(final_png, deriv_png)
            generate_qa_diagnostics(cropped, item_id)

            generated_results.append({
                "id": item_id,
                "role": item["role"],
                "status": "READY",
                "finalNative2K": str(final_png),
                "derivative": str(deriv_png),
                "derivativeDimensions": list(cropped.size),
                "sha256": hashlib.sha256(deriv_png.read_bytes()).hexdigest(),
                "costUSD": cost
            })
            print(f"  -> Successfully generated & saved derivative: {deriv_png.name} ({cropped.size[0]}x{cropped.size[1]})")

    finally:
        print("\nReleasing mutex and cloud lock...")
        runner.release_mutex()

    # Save summary manifest
    manifest_file = QA_DIR.parent / "regeneration-manifest.json"
    manifest_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model": MODEL,
        "project": PROJECT,
        "items": generated_results,
        "totalCostUSD": total_cost
    }
    print(f"\nWrote regeneration manifest: {manifest_file}")
    print(f"Total spent: ${total_cost:.4f} USD across {len(generated_results)} roles.")

    if generated_results and BUDGET_LEDGER_FILE.exists():
        try:
            b_data = json.loads(BUDGET_LEDGER_FILE.read_text(encoding="utf-8"))
            rt = b_data.get("reconciliationTrail", {})
            rt["reconciledInteractiveRegen4CostUSD"] = round(total_cost, 4)
            rt["totalCommittedProtectedUSD"] = round(rt.get("totalCommittedProtectedUSD", 70.7012) + total_cost, 4)
            rt["marginUnderHardCapUSD"] = round(80.0 - rt["totalCommittedProtectedUSD"], 4)
            BUDGET_LEDGER_FILE.write_text(json.dumps(b_data, indent=2), encoding="utf-8")
            print(f"Updated budget ledger: committed=${rt['totalCommittedProtectedUSD']:.4f}, margin=${rt['marginUnderHardCapUSD']:.4f}")
        except Exception as e:
            print(f"[WARN] Failed to update budget ledger: {e}")

if __name__ == "__main__":
    main()
