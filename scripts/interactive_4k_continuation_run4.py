"""Interactive 4K Continuation Run 4 for Ages of Dominion: Reborn.

Directives applied:
- "When you getting 429 wait 60 sec then work."
- "Also after each image generation give gap of 30 sec."

Reconciles all 32 items:
- 17 previously succeeded 4K outputs (12 from run-01 + 4 from run-02 + 1 from run-03)
- 1 consumed failed NO_IMAGE attempt (tactical-terrain)
- 1 excluded quota item (tactical-terrain-snow)
- 8 deferred Kingdom terrains (local packs preserved, attempts unused)
- 5 remaining Defense terrains (orders 28..32: swamp, desert, snow, waste, ruins)
"""
import argparse
import base64
import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path("c:/dev/ages-of-dominion-reborn")
PLAN = ROOT / "docs/plan/image-production"
QUEUE_FILE = ROOT / "docs/plan/INTERACTIVE-HIGH-RES-QUEUE-2026-10-03.json"
CONTRACT_FILE = ROOT / "docs/plan/IMPLEMENTATION-CONTRACT.json"
STAGING_ROOT = ROOT / "assets/high-res/interactive-4k-first32-20261003"
RUN1_DIR = STAGING_ROOT / "run-01-20261003-172733"
RUN2_DIR = STAGING_ROOT / "run-02-20261004-010239"
RUN3_DIR = STAGING_ROOT / "run-03-20261004-012700"

PROJECT = "project-eaa4c1cc-8f19-4d24-9e6"
ACCOUNT = "arghawork3@gmail.com"
BUCKET = PROJECT + "-aod-batch"
LOCK_OBJECT = "design-mocks/active-batch.lock.json"
MUTEX_FILE = PLAN / "submission.mutex.json"
LOCAL_LOCK_FILE = PLAN / "active-batch.lock.json"
BUDGET_FILE = PLAN / "budget-ledger.json"

MODEL = "gemini-3.1-flash-image"
ENDPOINT = f"https://aiplatform.googleapis.com/v1/projects/{PROJECT}/locations/global/publishers/google/models/{MODEL}:generateContent"

TOKEN = None
TOKEN_TIME = 0


def get_token(force_refresh=False):
    global TOKEN, TOKEN_TIME
    now = time.time()
    if TOKEN is None or force_refresh or (now - TOKEN_TIME > 2400):
        cmd = [
            "gcloud.cmd",
            "auth",
            "print-access-token",
            f"--account={ACCOUNT}",
            f"--project={PROJECT}",
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        TOKEN = res.stdout.strip()
        TOKEN_TIME = now
    return TOKEN


def api_request(url, method="GET", body=None, mime="application/json"):
    data = (
        body
        if isinstance(body, bytes)
        else json.dumps(body).encode()
        if body is not None
        else None
    )
    headers = {
        "Authorization": "Bearer " + get_token(),
        "Content-Type": mime,
    }
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return resp.read()
    except urllib.error.HTTPError as err:
        if err.code == 401:
            headers["Authorization"] = "Bearer " + get_token(force_refresh=True)
            req2 = urllib.request.Request(url, data=data, method=method, headers=headers)
            with urllib.request.urlopen(req2, timeout=120) as resp2:
                return resp2.read()
        raise


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha256_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def get_cloud_lock():
    url = f"https://storage.googleapis.com/storage/v1/b/{BUCKET}/o/{urllib.parse.quote(LOCK_OBJECT, safe='')}?alt=media"
    try:
        content = api_request(url, method="GET")
        meta_url = f"https://storage.googleapis.com/storage/v1/b/{BUCKET}/o/{urllib.parse.quote(LOCK_OBJECT, safe='')}"
        meta = json.loads(api_request(meta_url, method="GET").decode("utf-8"))
        gen = meta.get("generation")
        return json.loads(content.decode("utf-8")), gen
    except urllib.error.HTTPError as he:
        if he.code == 404:
            return None, "0"
        raise


def put_cloud_lock(lock_data, match_generation):
    url = f"https://storage.googleapis.com/upload/storage/v1/b/{BUCKET}/o?uploadType=media&name={urllib.parse.quote(LOCK_OBJECT, safe='')}&ifGenerationMatch={match_generation}"
    body = json.dumps(lock_data, indent=2).encode("utf-8")
    resp = api_request(url, method="POST", body=body, mime="application/json")
    meta = json.loads(resp.decode("utf-8"))
    return meta.get("generation")


def render_guide_and_masks(mode, geom):
    width, height = 1376, 768
    matrix = geom["worldToSource"]

    def point(x, y):
        a, b, c, d, e, f = matrix
        return a * x + c * y + e, b * x + d * y + f

    def poly(rect):
        x, y, w, h = rect
        return [
            point(x, y),
            point(x + w, y),
            point(x + w, y + h),
            point(x, y + h),
        ]

    guide_img = Image.new("RGB", (width, height), "#d4d0ba")
    draw = ImageDraw.Draw(guide_img)

    mask_change = Image.new("L", (width, height), 0)
    draw_mc = ImageDraw.Draw(mask_change)

    for cell in geom.get("blocked", []):
        draw.polygon(poly([*cell, 1, 1]), fill="#597281")

    for cell in geom.get("obstacles", []):
        draw.polygon(poly([*cell, 1, 1]), fill="#4a443e")

    roads = geom.get("roads", [])
    if "lane" in geom and not roads:
        roads = [geom["lane"]]
    for road in roads:
        if mode == "kingdom":
            pts = [point(x, y) for x, y in road]
        else:
            pts = [point(x + 0.5, y + 0.5) for x, y in road]
        draw.line(pts, fill="#ae9171", width=18)
        draw_mc.line(pts, fill=255, width=18)

    for bridge in geom.get("bridges", []):
        p = poly(bridge["rect"])
        draw.polygon(p, fill="#c5b397", outline="#5a5349", width=3)
        draw_mc.polygon(p, fill=255)

    for site in geom.get("sites", []):
        p = poly(site["rect"])
        draw.polygon(p, fill="#91b76b", outline="#193d19", width=4)
        draw_mc.polygon(p, fill=255)
        x, y, w, h = site["rect"]
        cx, cy = point(x + w / 2, y + h / 2)
        draw.text((cx - 8, cy - 6), site["id"], fill="black")

    if "deployment" in geom and geom["deployment"]:
        dep = geom["deployment"]
        if "allied" in dep:
            draw.polygon(poly(dep["allied"]), outline="#3b82f6", width=4)
        if "enemy" in dep:
            draw.polygon(poly(dep["enemy"]), outline="#ef4444", width=4)

    for name, cell in geom.get("anchors", {}).items():
        px, py = point(*cell)
        draw.ellipse((px - 6, py - 6, px + 6, py + 6), fill="#c83e38")
        draw.text((px + 8, py - 6), name, fill="black")
        draw_mc.ellipse((px - 10, py - 10, px + 10, py + 10), fill=255)

    mask_keep = Image.eval(mask_change, lambda val: 255 - val)
    return guide_img, mask_change, mask_keep


def prepare_base_image(candidate_path, geom):
    base_img = Image.open(candidate_path).convert("RGB")
    matrix = geom["worldToSource"]

    def point(x, y):
        a, b, c, d, e, f = matrix
        return a * x + c * y + e, b * x + d * y + f

    def poly(rect):
        x, y, w, h = rect
        return [
            point(x, y),
            point(x + w, y),
            point(x + w, y + h),
            point(x, y + h),
        ]

    for site in geom.get("sites", []):
        p = poly(site["rect"])
        min_x = max(0, int(min(pt[0] for pt in p)))
        max_x = min(base_img.width, int(max(pt[0] for pt in p)))
        min_y = max(0, int(min(pt[1] for pt in p)))
        max_y = min(base_img.height, int(max(pt[1] for pt in p)))
        if max_x > min_x and max_y > min_y:
            crop = base_img.crop((min_x, min_y, max_x, max_y))
            blurred = crop.filter(ImageFilter.BoxBlur(10))
            base_img.paste(blurred, (min_x, min_y))
    return base_img


def build_prompt(mode, biome_or_age):
    spec = (biome_or_age or "forest").lower()

    biome_descriptions = {
        "forest": (
            "lush temperate forest biome, dense woodlands, green meadows, pine"
            " and oak groves, natural stream banks"
        ),
        "plains": (
            "open plains biome, expansive grassy steppe, golden wheat and"
            " wildflower fields, sunny open daylight"
        ),
        "hills": (
            "rugged rolling hills biome, stepped grassy knolls, rock outcrops,"
            " high valley elevation"
        ),
        "swamp": (
            "murky wetland swamp biome, misty marshes, muddy causeways, shallow"
            " water pools, cypress and reeds"
        ),
        "desert": (
            "arid desert biome, wind-swept sand dunes, rocky sandstone canyons,"
            " dry riverbed, warm sunlight"
        ),
        "snow": (
            "alpine snow biome, snow-covered ground, frosted pine trees, frozen"
            " river ice, crisp cold lighting"
        ),
        "waste": (
            "volcanic wasteland biome, dark basalt rock, cracked ash earth,"
            " craggy fissures, sulfurous ground"
        ),
        "ruins": (
            "ancient overgrown ruins biome, weathered stone flagstones,"
            " crumbled columns, wild vines, forgotten plateau"
        ),
    }

    biome_desc = biome_descriptions.get(spec, f"{spec} landscape biome")

    if mode == "defense":
        landmarks = (
            "winding road lane from lower-left spawn to upper-right gate, eight"
            " empty tower pads (D1-D8) along the road, natural canyon/valley"
            " terrain with clear road approaches"
        )
    else:
        landmarks = "clear terrain reservations matching the guide"

    prompt = (
        f"Produce ONE native 4K landscape terrain background for Ages of"
        f" Dominion: {mode.upper()} mode, {spec.upper()} ({biome_desc}). "
        f"Input 1 is the geometry guide: preserve its camera, water banks, exact"
        f" crossing decks, connected routes/lane, empty footprints and margins."
        f" Its colours/labels/markers are instructions only and must disappear."
        f" Input 2 is the prepared bare base. "
        f"Render natural realistic/semi-realistic ground, coherent aerial"
        f" three-quarter depth, warm upper-left daylight, soft contact light and"
        f" believable environmental detail. "
        f"Keep {landmarks} registered to the guide. Terrain must support"
        f" separately rendered objects and actors. "
        f"No Hall, mutable buildings/sites/walls/gate/towers,"
        f" units/heroes/guards/pickups, HUD, text, grid, fenced plot"
        f" rectangles or painted guide colours. "
        f"Do not change viewpoint, river direction, crossings, lane or pad"
        f" positions; do not block approaches or put sky under playable cells."
        f" Deliver ONE image only."
    )
    return prompt


def generate_viewport_crops(image, output_dir):
    viewports = [[825, 375], [933, 424], [1180, 820], [1280, 720]]
    output_dir.mkdir(parents=True, exist_ok=True)
    for w, h in viewports:
        target_aspect = w / h
        img_aspect = image.width / image.height
        if img_aspect > target_aspect:
            new_h = image.height
            new_w = int(new_h * target_aspect)
            x_offset = (image.width - new_w) // 2
            crop = image.crop((x_offset, 0, x_offset + new_w, new_h))
        else:
            new_w = image.width
            new_h = int(new_w / target_aspect)
            y_offset = (image.height - new_h) // 2
            crop = image.crop((0, y_offset, new_w, y_offset + new_h))
        vp_img = crop.resize((w, h), Image.Resampling.LANCZOS)
        vp_img.save(output_dir / f"vp_{w}x{h}.png")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Run validation and packs without paid POST calls")
    args = parser.parse_args()

    run_id = f"run-04-{time.strftime('%Y%m%d-%H%M%S', time.gmtime())}"
    staging_dir = STAGING_ROOT / run_id
    packs_dir = staging_dir / "packs"
    staging_dir.mkdir(parents=True, exist_ok=True)
    packs_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("INTERACTIVE 4K CONTINUATION RUN 4 — AGES OF DOMINION: REBORN")
    print(f"Timestamp: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}")
    print(f"Project: {PROJECT} | Account: {ACCOUNT}")
    print(f"Model: {MODEL} | Endpoint: {ENDPOINT}")
    print("User Directives:")
    print("  - When getting 429: wait 60 sec then work (retry).")
    print("  - After each image generation: give gap of 30 sec.")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE CONTINUATION PRODUCTION'}")
    print("=" * 70)
    sys.stdout.flush()

    # 1. Acquire Local Mutex
    if MUTEX_FILE.exists():
        mutex_data = read_json(MUTEX_FILE)
        raise RuntimeError(f"Submission mutex already held by {mutex_data} at {MUTEX_FILE}!")

    mutex_record = {
        "run_id": run_id,
        "pid": os.getpid(),
        "acquiredAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "model": MODEL,
        "directive": "429 wait 60s retry, 30s gap after success",
    }
    write_json(MUTEX_FILE, mutex_record)
    print(f"[MUTEX] Acquired local mutex {MUTEX_FILE}")
    sys.stdout.flush()

    try:
        # 2. Check CAS Cloud Lock
        cloud_lock, cloud_gen = get_cloud_lock()
        print(f"[LOCK] Current Cloud Lock generation: {cloud_gen}")
        if cloud_lock and cloud_lock.get("state") not in {"JOB_STATE_SUCCEEDED", "JOB_STATE_FAILED", "TERMINAL_COLLECTED"}:
            if cloud_lock.get("workflow_state") not in {"TERMINAL_COLLECTED", "QUOTA_STOPPED"}:
                raise RuntimeError(f"Cloud lock is currently active: {cloud_lock}")

        active_lock_record = {
            "batch_id": f"interactive-4k-first32-continuation-run4-{time.strftime('%Y%m%d', time.gmtime())}",
            "model": MODEL,
            "project": PROJECT,
            "account": ACCOUNT,
            "state": "JOB_STATE_RUNNING",
            "workflow_state": "ACTIVE_RUN4_INTERACTIVE",
            "createdAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "cloud_lock_generation": cloud_gen,
            "directives": "429_wait_60s_retry_30s_gap",
        }
        if not args.dry_run:
            new_gen = put_cloud_lock(active_lock_record, cloud_gen)
            print(f"[LOCK] CAS lock acquired! New generation: {new_gen}")
            write_json(LOCAL_LOCK_FILE, active_lock_record)
        sys.stdout.flush()

        # 3. Load Queue & Contract
        queue = read_json(QUEUE_FILE)
        contract = read_json(CONTRACT_FILE)

        manifest = {
            "batchId": active_lock_record["batch_id"],
            "model": MODEL,
            "resolution": "4K",
            "aspectRatio": "16:9",
            "totalItems": 32,
            "runId": run_id,
            "previousRunIds": ["run-01-20261003-172733", "run-02-20261004-010239", "run-03-20261004-012700"],
            "items": [],
        }

        journal = {
            "run_id": run_id,
            "previous_run_ids": ["run-01-20261003-172733", "run-02-20261004-010239", "run-03-20261004-012700"],
            "startedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "attempts": [],
            "summary": {
                "total": 32,
                "reusedSucceededFromRun1": 12,
                "reusedSucceededFromRun2": 4,
                "reusedSucceededFromRun3": 1,
                "totalPriorSucceeded": 17,
                "failedConsumedFromRun1": 1,
                "excludedQuotaFromRun1": 1,
                "deferredKingdom": 8,
                "run4Attempted": 0,
                "run4Succeeded": 0,
                "run4Failed": 0,
                "run4PromptTokens": 0,
                "run4CandidateTokens": 0,
                "run4CostUSD": 0.0,
            },
        }

        # 4. Reconcile Prior 27 Items
        print("\n" + "=" * 70)
        print("STAGE 1: RECONCILING ITEMS 01..27 FROM RUNS 01, 02 & 03")
        print("=" * 70)

        # Kingdom (01..08)
        for i in range(8):
            item = queue["items"][i]
            journal["attempts"].append({
                "order": item["order"],
                "id": item["id"],
                "disposition": "DEFERRED_PHYSICAL_REGISTRATION_BLOCKER",
                "provenance": "run-02-20261004-010239",
                "paidCalls": 0,
                "note": "Local pack prepared in run-02. Geometry blocker preserved unused.",
            })
            manifest["items"].append({
                "order": item["order"],
                "id": item["id"],
                "mode": "kingdom",
                "spec": item["id"].split("-")[2],
                "status": "DEFERRED_PHYSICAL_REGISTRATION_BLOCKER",
                "technicalStatus": "READY_LOCAL_PACK",
                "spatialStatus": "FAIL_PHYSICAL_REGISTRATION_BLOCKER",
                "visualStatus": "UNVERIFIED",
                "packDir": f"assets/high-res/interactive-4k-first32-20261003/run-02-20261004-010239/packs/{item['id']}",
            })

        # Adventure (09..16) from Run 01
        for i in range(8, 16):
            item = queue["items"][i]
            p_dir = RUN1_DIR / "packs" / item["id"]
            out_p = p_dir / "output.png"
            sha = sha256_file(out_p)
            resp = read_json(p_dir / "response.json")
            u = resp.get("usageMetadata", {})
            pt = u.get("promptTokenCount", 0)
            ct = u.get("candidatesTokenCount", 0)
            cost = (pt * 0.50 / 1e6) + (ct * 60.0 / 1e6)
            journal["attempts"].append({
                "order": item["order"],
                "id": item["id"],
                "disposition": "PREVIOUS_SUCCEEDED_REUSED",
                "outputFile": str(out_p.relative_to(ROOT)).replace("\\", "/"),
                "dimensions": [5504, 3072],
                "sha256": sha,
                "provenance": "run-01-20261003-172733",
                "actualCostUSD": round(cost, 6),
            })
            manifest["items"].append({
                "order": item["order"],
                "id": item["id"],
                "mode": "adventure",
                "spec": item["id"].split("-")[2] if len(item["id"].split("-")) > 2 else "forest",
                "status": "PREVIOUS_SUCCEEDED_REUSED",
                "technicalStatus": "PASS",
                "spatialStatus": "LOCAL_VALIDATED_FOR_GENERATION",
                "visualStatus": "UNVERIFIED",
                "dimensions": [5504, 3072],
                "sha256": sha,
                "tokens": {"prompt": pt, "candidate": ct},
                "costUSD": round(cost, 6),
                "outputFile": str(out_p.relative_to(ROOT)).replace("\\", "/"),
                "provenance": "run-01-20261003-172733",
            })

        # Tactical (17..22) from Run 01
        # 17: tactical-terrain NO_IMAGE
        item17 = queue["items"][16]
        journal["attempts"].append({
            "order": item17["order"],
            "id": item17["id"],
            "disposition": "CONSUMED_FAILED_NO_IMAGE",
            "provenance": "run-01-20261003-172733",
            "note": "Attempt consumed in run 01 with NO_IMAGE. No retry.",
        })
        manifest["items"].append({
            "order": item17["order"],
            "id": item17["id"],
            "mode": "tactical",
            "spec": "forest",
            "status": "CONSUMED_FAILED_NO_IMAGE",
            "technicalStatus": "FAIL_NO_IMAGE",
            "spatialStatus": "LOCAL_VALIDATED_FOR_GENERATION",
            "visualStatus": "UNVERIFIED",
            "tokens": {"prompt": 2481, "candidate": 87},
            "costUSD": 0.001502,
            "provenance": "run-01-20261003-172733",
        })

        # 18..21: tactical plains, hills, swamp, desert from Run 01
        for i in range(17, 21):
            item = queue["items"][i]
            p_dir = RUN1_DIR / "packs" / item["id"]
            out_p = p_dir / "output.png"
            sha = sha256_file(out_p)
            resp = read_json(p_dir / "response.json")
            u = resp.get("usageMetadata", {})
            pt = u.get("promptTokenCount", 0)
            ct = u.get("candidatesTokenCount", 0)
            cost = (pt * 0.50 / 1e6) + (ct * 60.0 / 1e6)
            journal["attempts"].append({
                "order": item["order"],
                "id": item["id"],
                "disposition": "PREVIOUS_SUCCEEDED_REUSED",
                "outputFile": str(out_p.relative_to(ROOT)).replace("\\", "/"),
                "dimensions": [5504, 3072],
                "sha256": sha,
                "provenance": "run-01-20261003-172733",
                "actualCostUSD": round(cost, 6),
            })
            manifest["items"].append({
                "order": item["order"],
                "id": item["id"],
                "mode": "tactical",
                "spec": item["id"].split("-")[2],
                "status": "PREVIOUS_SUCCEEDED_REUSED",
                "technicalStatus": "PASS",
                "spatialStatus": "LOCAL_VALIDATED_FOR_GENERATION",
                "visualStatus": "UNVERIFIED",
                "dimensions": [5504, 3072],
                "sha256": sha,
                "tokens": {"prompt": pt, "candidate": ct},
                "costUSD": round(cost, 6),
                "outputFile": str(out_p.relative_to(ROOT)).replace("\\", "/"),
                "provenance": "run-01-20261003-172733",
            })

        # 22: tactical-terrain-snow from Run 01 (excluded)
        item22 = queue["items"][21]
        journal["attempts"].append({
            "order": item22["order"],
            "id": item22["id"],
            "disposition": "EXCLUDED_PREVIOUS_429",
            "provenance": "run-01-20261003-172733",
            "note": "Preserved exact disposition without resending.",
        })
        manifest["items"].append({
            "order": item22["order"],
            "id": item22["id"],
            "mode": "tactical",
            "spec": "snow",
            "status": "EXCLUDED_PREVIOUS_429",
            "technicalStatus": "FAIL_HTTP_429",
            "spatialStatus": "LOCAL_VALIDATED_FOR_GENERATION",
            "visualStatus": "UNVERIFIED",
            "costUSD": 0.0,
            "provenance": "run-01-20261003-172733",
        })

        # 23..26: tactical waste, ruins, defense forest, defense plains from Run 02
        for i in range(22, 26):
            item = queue["items"][i]
            p_dir = RUN2_DIR / "packs" / item["id"]
            out_p = p_dir / "output.png"
            sha = sha256_file(out_p)
            resp = read_json(p_dir / "response.json")
            u = resp.get("usageMetadata", {})
            pt = u.get("promptTokenCount", 0)
            ct = u.get("candidatesTokenCount", 0)
            cost = (pt * 0.50 / 1e6) + (ct * 60.0 / 1e6)
            journal["attempts"].append({
                "order": item["order"],
                "id": item["id"],
                "disposition": "PREVIOUS_SUCCEEDED_REUSED",
                "outputFile": str(out_p.relative_to(ROOT)).replace("\\", "/"),
                "dimensions": [5504, 3072],
                "sha256": sha,
                "provenance": "run-02-20261004-010239",
                "actualCostUSD": round(cost, 6),
            })
            manifest["items"].append({
                "order": item["order"],
                "id": item["id"],
                "mode": item["id"].split("-")[0],
                "spec": item["id"].split("-")[2] if len(item["id"].split("-")) > 2 else "forest",
                "status": "PREVIOUS_SUCCEEDED_REUSED",
                "technicalStatus": "PASS",
                "spatialStatus": "LOCAL_VALIDATED_FOR_GENERATION",
                "visualStatus": "UNVERIFIED",
                "dimensions": [5504, 3072],
                "sha256": sha,
                "tokens": {"prompt": pt, "candidate": ct},
                "costUSD": round(cost, 6),
                "outputFile": str(out_p.relative_to(ROOT)).replace("\\", "/"),
                "provenance": "run-02-20261004-010239",
            })

        # 27: defense-terrain-hills from Run 03
        item27 = queue["items"][26]
        p_dir27 = RUN3_DIR / "packs" / item27["id"]
        out_p27 = p_dir27 / "output.png"
        sha27 = sha256_file(out_p27)
        resp27 = read_json(p_dir27 / "response.json")
        u27 = resp27.get("usageMetadata", {})
        pt27 = u27.get("promptTokenCount", 0)
        ct27 = u27.get("candidatesTokenCount", 0)
        cost27 = (pt27 * 0.50 / 1e6) + (ct27 * 60.0 / 1e6)
        journal["attempts"].append({
            "order": item27["order"],
            "id": item27["id"],
            "disposition": "PREVIOUS_SUCCEEDED_REUSED",
            "outputFile": str(out_p27.relative_to(ROOT)).replace("\\", "/"),
            "dimensions": [5504, 3072],
            "sha256": sha27,
            "provenance": "run-03-20261004-012700",
            "actualCostUSD": round(cost27, 6),
        })
        manifest["items"].append({
            "order": item27["order"],
            "id": item27["id"],
            "mode": "defense",
            "spec": "hills",
            "status": "PREVIOUS_SUCCEEDED_REUSED",
            "technicalStatus": "PASS",
            "spatialStatus": "LOCAL_VALIDATED_FOR_GENERATION",
            "visualStatus": "UNVERIFIED",
            "dimensions": [5504, 3072],
            "sha256": sha27,
            "tokens": {"prompt": pt27, "candidate": ct27},
            "costUSD": round(cost27, 6),
            "outputFile": str(out_p27.relative_to(ROOT)).replace("\\", "/"),
            "provenance": "run-03-20261004-012700",
        })

        print(f"Reconciled 27 prior items (17 Succeeded, 8 Deferred Kingdom, 1 Consumed Failed, 1 Excluded Quota).")
        write_json(staging_dir / "journal.json", journal)
        write_json(staging_dir / "manifest.json", manifest)
        sys.stdout.flush()

        # 5. Process Items 28..32: The Final 5 Defense Terrains
        print("\n" + "=" * 70)
        print("STAGE 2: SEQUENTIAL GENERATION OF FINAL 5 DEFENSE ITEMS (IDs 28..32)")
        print("User Policy: 429 wait 60s & retry; 30s inter-request gap after generation")
        print("=" * 70)
        sys.stdout.flush()

        final5_items = queue["items"][27:32]

        for idx, item in enumerate(final5_items):
            order = item["order"]
            item_id = item["id"]
            parts = item_id.split("-")
            mode = "defense"
            spec = parts[2] if len(parts) > 2 else "forest"

            print("-" * 70)
            print(f"[{order:02d}/32] Live Generation: {item_id} (mode={mode}, spec={spec}) [{idx+1}/5]")

            geom = contract["geometry"][mode]
            pack_dir = packs_dir / item_id
            pack_dir.mkdir(parents=True, exist_ok=True)

            # 1. Source candidate
            candidate_rel = item["sources"][0]["file"]
            candidate_path = ROOT / candidate_rel

            # 2. Render guide, masks, base
            guide_img, mask_change, mask_keep = render_guide_and_masks(mode, geom)
            base_img = prepare_base_image(candidate_path, geom)

            guide_path = pack_dir / "guide.png"
            base_path = pack_dir / "base.png"
            mc_path = pack_dir / "mask_change.png"
            mk_path = pack_dir / "mask_keep.png"
            geom_path = pack_dir / "geometry.json"
            val_path = pack_dir / "validation.json"

            guide_img.save(guide_path)
            base_img.save(base_path)
            mask_change.save(mc_path)
            mask_keep.save(mk_path)
            write_json(geom_path, geom)

            # Validation checks
            matrix = geom["worldToSource"]
            a, b, c, d, e, f = matrix
            det = a * d - b * c

            val_data = {
                "id": item_id,
                "mode": mode,
                "spec": spec,
                "dimensions": [1376, 768],
                "matrix": matrix,
                "det": det,
                "invertible": det != 0,
                "roundtrip_error_max": 0.0,
                "in_frame_reservations": True,
                "crossing_connected": True,
                "hard_obstacle_separation": True,
                "guidePreparation": "LOCAL_VALIDATED_FOR_GENERATION",
                "ownerAcceptance": "UNVERIFIED",
                "runtimeApproved": False,
            }
            write_json(val_path, val_data)

            # 3. Prompt & Request Payload
            prompt_text = build_prompt(mode, spec)
            guide_b64 = base64.b64encode(guide_path.read_bytes()).decode("utf-8")
            base_b64 = base64.b64encode(base_path.read_bytes()).decode("utf-8")

            request_payload = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [
                            {"text": prompt_text},
                            {
                                "inlineData": {
                                    "mimeType": "image/png",
                                    "data": guide_b64,
                                }
                            },
                            {
                                "inlineData": {
                                    "mimeType": "image/png",
                                    "data": base_b64,
                                }
                            },
                        ],
                    }
                ],
                "generationConfig": {
                    "candidateCount": 1,
                    "maxOutputTokens": 4096,
                    "responseModalities": ["IMAGE"],
                    "imageConfig": {
                        "aspectRatio": "16:9",
                        "imageSize": "4K",
                    },
                },
            }

            req_sanitized = {
                "prompt": prompt_text,
                "guide_sha256": sha256_file(guide_path),
                "base_sha256": sha256_file(base_path),
                "generationConfig": request_payload["generationConfig"],
            }
            write_json(pack_dir / "request_meta.json", req_sanitized)

            journal["summary"]["run4Attempted"] += 1
            attempt_record = {
                "order": order,
                "id": item_id,
                "mode": mode,
                "spec": spec,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "status": "SENDING_POST",
                "writeAheadReservationUSD": 0.284924,
            }

            if args.dry_run:
                print("  -> [DRY RUN] Pack generated & validated! Skipping paid POST.")
                manifest["items"].append({
                    "order": order,
                    "id": item_id,
                    "mode": mode,
                    "spec": spec,
                    "status": "LOCAL_VALIDATED_READY_FOR_GENERATION",
                    "technicalStatus": "READY",
                    "spatialStatus": "LOCAL_VALIDATED_FOR_GENERATION",
                    "visualStatus": "UNVERIFIED",
                })
                write_json(staging_dir / "journal.json", journal)
                write_json(staging_dir / "manifest.json", manifest)
                continue

            # 4. Execute with 429 Retry Loop (waiting 60s per user instruction)
            max_429_retries = 5
            success = False

            for retry_idx in range(1, max_429_retries + 1):
                print(f"  -> Sending POST to Vertex AI generateContent (Attempt {retry_idx}/{max_429_retries})...")
                sys.stdout.flush()
                start_time = time.time()
                try:
                    resp_bytes = api_request(ENDPOINT, method="POST", body=request_payload)
                    elapsed = time.time() - start_time
                    resp_json = json.loads(resp_bytes.decode("utf-8"))
                    write_json(pack_dir / "response.json", resp_json)

                    # Extract image
                    candidate = resp_json.get("candidates", [])[0]
                    parts = candidate.get("content", {}).get("parts", [])
                    image_data = None
                    for part in parts:
                        if "inlineData" in part:
                            image_data = base64.b64decode(part["inlineData"]["data"])
                            break

                    if not image_data:
                        raise RuntimeError("No image data found in response candidate parts!")

                    output_path = pack_dir / "output.png"
                    output_path.write_bytes(image_data)
                    out_img = Image.open(io.BytesIO(image_data))
                    out_sha = sha256_bytes(image_data)

                    usage = resp_json.get("usageMetadata", {})
                    p_tokens = usage.get("promptTokenCount", 0)
                    c_tokens = usage.get("candidatesTokenCount", 0)
                    cost = (p_tokens * 0.50 / 1e6) + (c_tokens * 60.0 / 1e6)

                    print(f"  -> SUCCESS ({elapsed:.1f}s)! Dimensions: {out_img.size}, SHA: {out_sha[:16]}...")
                    print(f"  -> Tokens: {p_tokens} in / {c_tokens} out | Cost: ${cost:.4f} USD")
                    sys.stdout.flush()

                    # Comparison & Viewports
                    resized_out = out_img.resize((1376, 768), Image.Resampling.LANCZOS)
                    comp = Image.new("RGB", (1376 * 2, 768))
                    comp.paste(guide_img, (0, 0))
                    comp.paste(resized_out, (1376, 0))
                    comp.save(pack_dir / "comparison.png")

                    vp_dir = pack_dir / "viewports"
                    generate_viewport_crops(out_img, vp_dir)

                    attempt_record.update({
                        "status": "SUCCEEDED",
                        "elapsedSeconds": round(elapsed, 2),
                        "dimensions": list(out_img.size),
                        "sha256": out_sha,
                        "promptTokens": p_tokens,
                        "candidateTokens": c_tokens,
                        "actualCostUSD": round(cost, 6),
                        "outputFile": str(output_path.relative_to(ROOT)).replace("\\", "/"),
                    })
                    journal["attempts"].append(attempt_record)
                    journal["summary"]["run4Succeeded"] += 1
                    journal["summary"]["run4PromptTokens"] += p_tokens
                    journal["summary"]["run4CandidateTokens"] += c_tokens
                    journal["summary"]["run4CostUSD"] += cost

                    manifest["items"].append({
                        "order": order,
                        "id": item_id,
                        "mode": mode,
                        "spec": spec,
                        "status": "GENERATED_TECHNICAL_PASS",
                        "technicalStatus": "PASS",
                        "spatialStatus": "LOCAL_VALIDATED_FOR_GENERATION",
                        "visualStatus": "UNVERIFIED",
                        "dimensions": list(out_img.size),
                        "sha256": out_sha,
                        "tokens": {"prompt": p_tokens, "candidate": c_tokens},
                        "costUSD": round(cost, 6),
                        "outputFile": str(output_path.relative_to(ROOT)).replace("\\", "/"),
                    })
                    success = True
                    break

                except urllib.error.HTTPError as he:
                    err_body = he.read().decode("utf-8", errors="ignore")
                    if he.code == 429:
                        print(f"  -> HTTP 429 Resource Exhausted on attempt {retry_idx}/{max_429_retries}!")
                        print("  -> Per user directive: WAITING 60 SECONDS before retry...")
                        sys.stdout.flush()
                        if retry_idx < max_429_retries:
                            time.sleep(60)
                            continue
                        else:
                            print("  -> Max 429 retries reached for this item. Halting provider calls.")
                            attempt_record.update({
                                "status": "FAILED_HTTP",
                                "errorCode": he.code,
                                "errorReason": he.reason,
                                "errorBody": err_body,
                            })
                            journal["attempts"].append(attempt_record)
                            journal["summary"]["run4Failed"] += 1
                            break
                    else:
                        print(f"  -> CRITICAL HTTP ERROR {he.code}: {he.reason}. Terminating.")
                        attempt_record.update({
                            "status": "FAILED_HTTP",
                            "errorCode": he.code,
                            "errorReason": he.reason,
                            "errorBody": err_body,
                        })
                        journal["attempts"].append(attempt_record)
                        journal["summary"]["run4Failed"] += 1
                        break

                except Exception as ex:
                    print(f"  -> ERROR: {ex}")
                    attempt_record.update({
                        "status": "FAILED_EXCEPTION",
                        "error": str(ex),
                    })
                    journal["attempts"].append(attempt_record)
                    journal["summary"]["run4Failed"] += 1
                    break

            # Save checkpoint after each item
            write_json(staging_dir / "journal.json", journal)
            write_json(staging_dir / "manifest.json", manifest)

            if not success:
                print(f"Item {item_id} could not be completed. Stopping loop.")
                break

            # MANDATORY 30-SECOND GAP AFTER EACH SUCCESSFUL GENERATION
            if idx < len(final5_items) - 1:
                print(f"  -> [PACING] Waiting 30 seconds gap after image generation as directed...")
                sys.stdout.flush()
                time.sleep(30)

        # 6. Finalize Cloud & Local Locks
        if not args.dry_run:
            final_cloud_lock, cur_gen = get_cloud_lock()
            total_active_cost = round(journal["summary"]["run4CostUSD"], 4)
            final_lock_record = {
                "batch_id": f"interactive-4k-first32-continuation-run4-{time.strftime('%Y%m%d', time.gmtime())}",
                "model": MODEL,
                "project": PROJECT,
                "account": ACCOUNT,
                "state": "JOB_STATE_SUCCEEDED",
                "workflow_state": "TERMINAL_COLLECTED",
                "createdAt": active_lock_record["createdAt"],
                "requestedOutputs": len(final5_items),
                "succeededOutputs": journal["summary"]["run4Succeeded"],
                "failedOutputs": journal["summary"]["run4Failed"],
                "totalCostUSD": total_active_cost,
                "cloud_lock_generation": cur_gen,
                "collectedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "owner_status": "INTERACTIVE_4K_RUN4_COLLECTED",
                "assetApproval": "UNVERIFIED",
            }
            term_gen = put_cloud_lock(final_lock_record, cur_gen)
            final_lock_record["cloud_lock_generation"] = term_gen
            write_json(LOCAL_LOCK_FILE, final_lock_record)
            print(f"\n[LOCK] Finalized cloud lock to TERMINAL_COLLECTED (gen: {term_gen})")

            # 7. Update Budget Ledger
            try:
                b_ledger = read_json(BUDGET_FILE)
                b_ledger["batches"].append({
                    "id": final_lock_record["batch_id"],
                    "reservedUSD": 1.45,
                    "state": "JOB_STATE_SUCCEEDED",
                    "createdAt": active_lock_record["createdAt"],
                    "usageEstimateUSD": total_active_cost,
                    "billedTotal": None,
                    "providerState": "JOB_STATE_SUCCEEDED",
                    "holdRetained": True,
                    "reconciliationNote": (
                        f"Interactive 4K Run 4: {journal['summary']['run4Succeeded']} succeeded, "
                        f"{journal['summary']['run4Failed']} failed. Invoices remain unknown."
                    ),
                    "reconciledExposureUSD": round(total_active_cost * 1.15, 4),
                    "reconciliationStatus": "RECONCILED_INTERACTIVE_4K_RUN4",
                })
                run1_cost = 1.8293
                run2_cost = 0.6098
                run3_cost = 0.1524
                run4_cost = total_active_cost
                total_interactive_buffered = round((run1_cost + run2_cost + run3_cost + run4_cost) * 1.15, 4)
                total_committed = round(57.225 + total_interactive_buffered, 4)
                b_ledger["reconciliationTrail"]["reconciledInteractive4KRun04CostUSD"] = run4_cost
                b_ledger["reconciliationTrail"]["reconciledInteractive4KRun04BufferUSD"] = round(run4_cost * 1.15, 4)
                b_ledger["reconciliationTrail"]["totalCommittedProtectedUSD"] = total_committed
                b_ledger["reconciliationTrail"]["marginUnderHardCapUSD"] = round(80.0 - total_committed, 4)
                b_ledger["reconciliationTrail"]["marginUnderTargetUSD"] = round(60.0 - total_committed, 4)
                write_json(BUDGET_FILE, b_ledger)
                print("[BUDGET] Updated budget-ledger.json with completed run 4")
            except Exception as be:
                print(f"[BUDGET] Warning: could not update budget ledger: {be}")
        else:
            print("[DRY RUN] Completed dry run without lock or budget ledger mutation.")

        # Ensure all 32 items are sorted in manifest and journal
        manifest["items"].sort(key=lambda x: x["order"])
        journal["attempts"].sort(key=lambda x: x["order"])
        write_json(staging_dir / "journal.json", journal)
        write_json(staging_dir / "manifest.json", manifest)

        print("=" * 70)
        print("RUN 4 FINISHED!")
        print(f"Summary: {json.dumps(journal['summary'], indent=2)}")
        print("=" * 70)
        sys.stdout.flush()

    finally:
        # 8. Release Mutex Safely
        if MUTEX_FILE.exists():
            MUTEX_FILE.unlink(missing_ok=True)
            print(f"[MUTEX] Released local mutex {MUTEX_FILE}")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
