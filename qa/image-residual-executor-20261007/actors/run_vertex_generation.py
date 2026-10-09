"""Standalone robust runner for the 4-role Vertex AI regeneration using gemini-3.1-flash-image.

Adheres strictly to:
- Model: gemini-3.1-flash-image
- Project: project-eaa4c1cc-8f19-4d24-9e6
- Account: arghawork3@gmail.com
- Hard timeout 300s, socket default 300s
- Pacing: 20 seconds between calls
- Promotion to final-native2k
- Flood-fill alpha extraction to assets/derivatives/image-residual-executor-20261007/actors/troops/
- Budget ledger tracking
"""

import sys
import os
import json
import time
import base64
import socket
import urllib.request
import urllib.error
import subprocess
import hashlib
from pathlib import Path
from datetime import datetime, timezone
import cv2
import numpy as np
from PIL import Image

# 300-second network deadline
socket.setdefaulttimeout(300)

ROOT = Path("c:/dev/ages-of-dominion-reborn").resolve()
PROJECT = "project-eaa4c1cc-8f19-4d24-9e6"
ACCOUNT = "arghawork3@gmail.com"
MODEL = "gemini-3.1-flash-image"
ENDPOINT = f"https://aiplatform.googleapis.com/v1/projects/{PROJECT}/locations/global/publishers/google/models/{MODEL}:generateContent"

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

def get_token():
    cmd = ["gcloud.cmd" if sys.platform == "win32" else "gcloud", "auth", "print-access-token", f"--account={ACCOUNT}", f"--project={PROJECT}"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return res.stdout.strip()

def extract_alpha_derivative(src_png_path, out_png_path):
    im = Image.open(src_png_path).convert("RGBA")
    arr = np.array(im, dtype=np.uint8)
    h, w, _ = arr.shape
    a = arr[:, :, 3]

    if np.any(a < 250):
        clean_im = im
    else:
        rgb = np.ascontiguousarray(arr[:, :, :3])
        mask = np.zeros((h + 2, w + 2), dtype=np.uint8)
        corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1), (w // 2, 0), (w // 2, h - 1)]
        diff_range = (25, 25, 25)
        for pt in corners:
            cv2.floodFill(rgb, mask, pt, (0, 0, 0), diff_range, diff_range, flags=8 | (255 << 8) | cv2.FLOODFILL_MASK_ONLY)

        bg_mask = (mask[1:-1, 1:-1] == 255)
        dist = cv2.distanceTransform(bg_mask.astype(np.uint8), cv2.DIST_L2, 3)
        alpha = np.clip(1.0 - (dist / 2.0), 0.0, 1.0)
        alpha[~bg_mask] = 1.0

        out_arr = arr.copy()
        out_arr[:, :, 3] = (alpha * 255).astype(np.uint8)
        clean_im = Image.fromarray(out_arr, mode="RGBA")

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
    aspect = w / h

    t64_h = 64
    t64_w = max(16, int(t64_h * aspect))
    thumb64 = cropped_rgba.resize((t64_w, t64_h), Image.Resampling.LANCZOS)

    t130_h = 130
    t130_w = max(16, int(t130_h * aspect))
    thumb130 = cropped_rgba.resize((t130_w, t130_h), Image.Resampling.LANCZOS)

    bgs = [('white', (255, 255, 255, 255)), ('black', (0, 0, 0, 255)), ('green', (110, 132, 104, 255))]

    c64 = Image.new('RGB', (t64_w * 3, t64_h))
    for i, (_, col) in enumerate(bgs):
        layer = Image.new('RGBA', (t64_w, t64_h), col)
        layer.alpha_composite(thumb64)
        c64.paste(layer.convert('RGB'), (i * t64_w, 0))
    c64.save(QA_DIR / f"{item_id}_qa_64px.png")

    c130 = Image.new('RGB', (t130_w * 3, t130_h))
    for i, (_, col) in enumerate(bgs):
        layer = Image.new('RGBA', (t130_w, t130_h), col)
        layer.alpha_composite(thumb130)
        c130.paste(layer.convert('RGB'), (i * t130_w, 0))
    c130.save(QA_DIR / f"{item_id}_qa_130px.png")

def main():
    print("=" * 80)
    print("VERTEX AI 4-ROLE REGENERATION RUN (gemini-3.1-flash-image)")
    print(f"Time: {datetime.now(timezone.utc).isoformat()}")
    print(f"Project: {PROJECT} | Account: {ACCOUNT} | Model: {MODEL}")
    print("=" * 80)

    PACKS_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_NATIVE2K_DIR.mkdir(parents=True, exist_ok=True)
    TROOP_DERIV_DIR.mkdir(parents=True, exist_ok=True)
    QA_DIR.mkdir(parents=True, exist_ok=True)

    token = get_token()
    print(f"Token acquired, length: {len(token)}")

    results = []
    total_cost = 0.0

    for idx, item in enumerate(TARGET_ROLES):
        item_id = item["id"]
        role = item["role"]
        prompt = item["prompt"]
        p_dir = PACKS_DIR / item_id
        p_dir.mkdir(parents=True, exist_ok=True)

        out_png = p_dir / "output.png"
        reused = False
        if out_png.exists():
            try:
                im_check = Image.open(out_png)
                if im_check.size == (2048, 2048):
                    print(f"  -> Reusing existing 2048x2048 master: {out_png.name}")
                    img_bytes = out_png.read_bytes()
                    reused = True
            except Exception:
                pass

        if not reused:
            if idx > 0:
                print("[PACING] Waiting 20 seconds before next request...")
                time.sleep(20)

            print(f"\n[{idx+1}/4] Dispatching generation for '{item_id}' ({role})...")
            sys.stdout.flush()

            body = {
                "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                "generationConfig": {
                    "candidateCount": 1,
                    "imageConfig": {
                        "aspectRatio": "1:1",
                        "imageSize": "2K"
                    },
                    "maxOutputTokens": 2048,
                    "responseModalities": ["IMAGE"]
                }
            }
            body_bytes = json.dumps(body).encode("utf-8")
            (p_dir / "request_body.json").write_text(json.dumps(body, indent=2), encoding="utf-8")
            (p_dir / "prompt.txt").write_text(prompt, encoding="utf-8")

            # Write-ahead log
            wa_data = {
                "itemId": item_id,
                "status": "SENDING_POST",
                "recordedAt": datetime.now(timezone.utc).isoformat(),
                "model": MODEL,
                "project": PROJECT
            }
            (p_dir / "write_ahead_request.json").write_text(json.dumps(wa_data, indent=2), encoding="utf-8")

            req = urllib.request.Request(ENDPOINT, data=body_bytes, method="POST", headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            })

            t0 = time.time()
            try:
                with urllib.request.urlopen(req, timeout=300) as resp:
                    elapsed = time.time() - t0
                    print(f"  -> HTTP {resp.status} in {elapsed:.1f}s")
                    resp_data = json.loads(resp.read().decode("utf-8"))
            except urllib.error.HTTPError as he:
                err_body = he.read().decode("utf-8")
                print(f"[ERROR] HTTP {he.code}: {err_body}")
                wa_data["status"] = "FAILED_HTTP"
                wa_data["error"] = err_body
                (p_dir / "write_ahead_request.json").write_text(json.dumps(wa_data, indent=2), encoding="utf-8")
                break
            except Exception as e:
                print(f"[ERROR] Request failed: {e}")
                wa_data["status"] = "FAILED_EXCEPTION"
                wa_data["error"] = str(e)
                (p_dir / "write_ahead_request.json").write_text(json.dumps(wa_data, indent=2), encoding="utf-8")
                break

            # Save response JSON
            (p_dir / "response.json").write_text(json.dumps(resp_data, indent=2), encoding="utf-8")

            # Extract image
            candidates = resp_data.get("candidates", [])
            if not candidates:
                print("[ERROR] No candidates in response!")
                break
            parts = candidates[0].get("content", {}).get("parts", [])
            img_b64 = None
            for p in parts:
                if "inlineData" in p:
                    img_b64 = p["inlineData"].get("data")
                    break

            if not img_b64:
                print("[ERROR] No inlineData image in candidate parts!")
                break

            img_bytes = base64.b64decode(img_b64)
            out_png.write_bytes(img_bytes)

            # Verify PIL
            im_check = Image.open(out_png)
            print(f"  -> Output image decoded: {im_check.size}, format: {im_check.format}, bytes: {len(img_bytes)}")
            if im_check.size != (2048, 2048):
                print(f"[WARN] Unexpected dimensions: {im_check.size}")

            # Update write-ahead
            wa_data["status"] = "SUCCEEDED"
            wa_data["completedAt"] = datetime.now(timezone.utc).isoformat()
            wa_data["outputSHA256"] = hashlib.sha256(img_bytes).hexdigest()
            (p_dir / "write_ahead_request.json").write_text(json.dumps(wa_data, indent=2), encoding="utf-8")

        # Promote to final-native2k
        final_png = FINAL_NATIVE2K_DIR / f"{item_id}.png"
        final_png.write_bytes(img_bytes)

        # Extract clean derivative
        deriv_png = TROOP_DERIV_DIR / f"{item_id}.png"
        cropped = extract_alpha_derivative(final_png, deriv_png)
        generate_qa_diagnostics(cropped, item_id)
        deriv_bytes = deriv_png.read_bytes()
        deriv_sha = hashlib.sha256(deriv_bytes).hexdigest()

        cost = 0.1036
        total_cost += cost

        results.append({
            "id": item_id,
            "role": role,
            "status": "READY",
            "finalNative2K": str(final_png),
            "derivative": str(deriv_png),
            "derivativeDimensions": list(cropped.size),
            "derivativeSHA256": deriv_sha,
            "costUSD": cost
        })
        print(f"  -> Successfully generated & saved derivative: {deriv_png.name} ({cropped.size[0]}x{cropped.size[1]})")

    # Save summary manifest
    manifest_file = ROOT / "qa/image-residual-executor-20261007/actors/regeneration-manifest.json"
    manifest_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model": MODEL,
        "project": PROJECT,
        "items": results,
        "totalCostUSD": round(total_cost, 4)
    }
    manifest_file.write_text(json.dumps(manifest_data, indent=2), encoding="utf-8")
    print(f"\nWrote regeneration manifest: {manifest_file}")
    print(f"Total spent: ${total_cost:.4f} USD across {len(results)} roles.")

    # Update budget ledger
    if results and BUDGET_LEDGER_FILE.exists():
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
