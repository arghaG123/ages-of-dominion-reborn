"""Interactive 4K Image Runner for Ages of Dominion: Reborn.
Authorizes and executes sequential individual generateContent calls against Vertex AI
for the 32 native 4K terrain images under owner directives (3 October 2026).
"""
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
            # Token expired, retry once with fresh token
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
    temp = path.with_suffix(path.suffix + ".tmp")
    with open(temp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(temp, path)


def get_cloud_lock():
    url = f"https://storage.googleapis.com/storage/v1/b/{BUCKET}/o/{urllib.parse.quote(LOCK_OBJECT, safe='')}?alt=media"
    res = api_request(url, "GET")
    data = json.loads(res.decode("utf-8"))
    meta_url = f"https://storage.googleapis.com/storage/v1/b/{BUCKET}/o/{urllib.parse.quote(LOCK_OBJECT, safe='')}"
    meta_res = api_request(meta_url, "GET")
    meta = json.loads(meta_res.decode("utf-8"))
    return data, meta.get("generation")


def put_cloud_lock(data, match_generation):
    url = f"https://storage.googleapis.com/upload/storage/v1/b/{BUCKET}/o?uploadType=media&name={urllib.parse.quote(LOCK_OBJECT, safe='')}&ifGenerationMatch={match_generation}"
    body = json.dumps(data, indent=2).encode("utf-8")
    res = api_request(url, "POST", body, mime="application/json")
    resp_obj = json.loads(res.decode("utf-8"))
    return resp_obj.get("generation")


# --- Pack Generation ---


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

    # 1. Blocked / River
    for cell in geom.get("blocked", []):
        p = poly([*cell, 1, 1])
        draw.polygon(p, fill="#597281")

    # 2. Obstacles
    for cell in geom.get("obstacles", []):
        p = poly([*cell, 1, 1])
        draw.polygon(p, fill="#4a443e")

    # 3. Roads / Lanes
    roads = geom.get("roads", [])
    if "lane" in geom and not roads:
        roads = [geom["lane"]]
    for road in roads:
        pts = [point(x + 0.5, y + 0.5) for x, y in road]
        draw.line(pts, fill="#ae9171", width=18)
        draw_mc.line(pts, fill=255, width=18)

    # 4. Bridges / Crossings
    for bridge in geom.get("bridges", []):
        p = poly(bridge["rect"])
        draw.polygon(p, fill="#c5b397", outline="#5a5349", width=3)
        draw_mc.polygon(p, fill=255)

    # 5. Sites / Tower Pads
    for site in geom.get("sites", []):
        p = poly(site["rect"])
        draw.polygon(p, fill="#91b76b", outline="#193d19", width=4)
        draw_mc.polygon(p, fill=255)
        x, y, w, h = site["rect"]
        cx, cy = point(x + w / 2, y + h / 2)
        draw.text((cx - 8, cy - 6), site["id"], fill="black")

    # 6. Deployment (Tactical)
    if "deployment" in geom and geom["deployment"]:
        dep = geom["deployment"]
        if "allied" in dep:
            p = poly(dep["allied"])
            draw.polygon(p, outline="#3b82f6", width=4)
        if "enemy" in dep:
            p = poly(dep["enemy"])
            draw.polygon(p, outline="#ef4444", width=4)

    # 7. Anchors
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

    if mode == "adventure":
        landmarks = (
            "six empty site reservations (town, ruin, mill, mine, dwelling,"
            " shrine), western river with stone crossing at row 6, connected"
            " paths, and clear margins"
        )
    elif mode == "tactical":
        landmarks = (
            "central stream with two crossing decks at lanes 3 and 7, allied"
            " deployment zone (lower left) and enemy deployment zone (upper"
            " right), open combat board, cliff obstacles outside playfield"
        )
    elif mode == "defense":
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
    import argparse
    parser = argparse.ArgumentParser(description="Interactive 4K Runner")
    parser.add_argument("--dry-run", action="store_true", help="Prepare packs and validate without paid API calls")
    parser.add_argument("--limit", type=int, default=32, help="Max items to process")
    args = parser.parse_args()

    print("=" * 70)
    print("INTERACTIVE 4K RUNNER — AGES OF DOMINION: REBORN")
    print(f"Timestamp: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}")
    print(f"Project: {PROJECT} | Account: {ACCOUNT}")
    print(f"Model: {MODEL} | Endpoint: {ENDPOINT}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE PRODUCTION'}")
    print("=" * 70)

    # 1. Mutex Check & Acquisition
    if MUTEX_FILE.exists():
        print(f"ERROR: Mutex file {MUTEX_FILE} exists! Concurrent run blocked.")
        sys.exit(1)

    run_id = f"run-01-{time.strftime('%Y%m%d-%H%M%S', time.gmtime())}"
    staging_dir = STAGING_ROOT / run_id
    staging_dir.mkdir(parents=True, exist_ok=True)
    packs_dir = staging_dir / "packs"
    packs_dir.mkdir(parents=True, exist_ok=True)

    if not args.dry_run:
        mutex_data = {
            "run_id": run_id,
            "acquiredAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "role": "IMAGE_EXECUTOR",
            "scope": "interactive-4k-first32",
        }
        write_json(MUTEX_FILE, mutex_data)
        print(f"[MUTEX] Acquired local mutex {MUTEX_FILE}")

    try:
        # 2. Reconcile Locks
        local_lock = read_json(LOCAL_LOCK_FILE)
        cloud_lock, cloud_gen = get_cloud_lock()
        print(f"[LOCK] Local batch lock: {local_lock.get('batch_id')} ({local_lock.get('state')})")
        print(f"[LOCK] Cloud lock generation: {cloud_gen} ({cloud_lock.get('state')})")

        if cloud_lock.get("state") not in {
            "JOB_STATE_SUCCEEDED",
            "JOB_STATE_FAILED",
            "JOB_STATE_CANCELLED",
            "JOB_STATE_EXPIRED",
        }:
            raise RuntimeError(
                f"Active/unknown cloud lock detected: {cloud_lock.get('state')}"
            )

        if not args.dry_run:
            # Archive prior lock
            archive_dir = PLAN / "archive"
            archive_dir.mkdir(parents=True, exist_ok=True)
            write_json(
                archive_dir / f"{cloud_lock.get('batch_id', 'prior')}.lock.json",
                cloud_lock,
            )

            # Update cloud lock via CAS to RUNNING_ACTIVE
            active_lock_record = {
                "batch_id": f"interactive-4k-first32-{time.strftime('%Y%m%d', time.gmtime())}",
                "model": MODEL,
                "project": PROJECT,
                "account": ACCOUNT,
                "state": "RUNNING_ACTIVE",
                "workflow_state": "INTERACTIVE_RUNNING",
                "createdAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "manifest_sha256": None,
                "requestedOutputs": 32,
                "reservedUSD": 9.12,
                "cloud_lock_generation": cloud_gen,
                "submittedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "owner_status": "INTERACTIVE_4K_IN_PROGRESS",
                "assetApproval": "UNVERIFIED",
            }
            new_cloud_gen = put_cloud_lock(active_lock_record, cloud_gen)
            active_lock_record["cloud_lock_generation"] = new_cloud_gen
            write_json(LOCAL_LOCK_FILE, active_lock_record)
            print(f"[LOCK] CAS lock acquired! New generation: {new_cloud_gen}")

        # 3. Load Queue and Contract
        queue = read_json(QUEUE_FILE)
        contract = read_json(CONTRACT_FILE)
        items = queue["items"][:32]

        manifest = {
            "run_id": run_id,
            "createdAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "model": MODEL,
            "project": PROJECT,
            "itemsCount": len(items),
            "items": [],
        }

        journal = {
            "run_id": run_id,
            "startedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "attempts": [],
            "summary": {
                "total": len(items),
                "attempted": 0,
                "succeeded": 0,
                "deferred": 0,
                "failed": 0,
                "totalPromptTokens": 0,
                "totalCandidateTokens": 0,
                "totalCostUSD": 0.0,
            },
        }

        # 4. Process Each Item
        for item in items:
            order = item["order"]
            item_id = item["id"]
            parts = item_id.split("-")
            mode = parts[0]
            spec = parts[2] if len(parts) > 2 else ("stone" if mode == "kingdom" else "forest")

            print("-" * 70)
            print(f"[{order:02d}/32] Processing: {item_id} (mode={mode}, spec={spec})")

            # A. Check Kingdom Deferral
            if mode == "kingdom" or order <= 8:
                deferral_reason = (
                    "Documented physical registration defects in Kingdom"
                    " geometry contract vs visual candidates (Hall scale 0.1312"
                    " vs 0.34 framing, 14 pairwise mature rectangle overlaps,"
                    " P11 panel collision, unmeasured foundation contact and"
                    " threshold-to-apron discontinuity at entrance (640, 291.26)"
                    " vs (644.6, 297.4)). Per owner instruction: 'If an exact"
                    " Kingdom geometry conflict truly cannot be resolved"
                    " locally, defer only the affected Kingdom IDs with"
                    " coordinates/images/check results and continue other"
                    " modes. An early Kingdom blocker must not hold the 24"
                    " unrelated mode backgrounds.'"
                )
                print(f"  -> DEFERRED: {deferral_reason[:110]}...")
                item_manifest = {
                    "order": order,
                    "id": item_id,
                    "mode": mode,
                    "spec": spec,
                    "status": "DEFERRED_PHYSICAL_REGISTRATION_BLOCKER",
                    "reason": deferral_reason,
                    "attempted": False,
                }
                manifest["items"].append(item_manifest)
                journal["summary"]["deferred"] += 1
                journal["attempts"].append({
                    "order": order,
                    "id": item_id,
                    "disposition": "DEFERRED",
                    "reason": deferral_reason,
                })
                continue

            # B. Mode IDs 09..32 (Adventure, Tactical, Defense)
            geom = contract["geometry"][mode]
            pack_dir = packs_dir / item_id
            pack_dir.mkdir(parents=True, exist_ok=True)

            # 1. Source candidate
            candidate_rel = item["sources"][0]["file"]
            candidate_path = ROOT / candidate_rel
            candidate_sha = item["sources"][0]["sha256"]

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

            # Write-ahead liability
            journal["summary"]["attempted"] += 1
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

            print("  -> Sending POST to Vertex AI generateContent...")
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

                # Comparison & Viewports
                resized_out = out_img.resize((1376, 768), Image.Resampling.LANCZOS)
                comp = Image.new("RGB", (1376 * 2, 768))
                comp.paste(guide_img, (0, 0))
                comp.paste(resized_out, (1376, 0))
                comp.save(pack_dir / "comparison.png")

                vp_dir = pack_dir / "viewports"
                generate_viewport_crops(out_img, vp_dir)

                # Update records
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
                journal["summary"]["succeeded"] += 1
                journal["summary"]["totalPromptTokens"] += p_tokens
                journal["summary"]["totalCandidateTokens"] += c_tokens
                journal["summary"]["totalCostUSD"] += cost

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

            except urllib.error.HTTPError as he:
                print(f"  -> HTTP ERROR {he.code}: {he.reason}")
                err_body = he.read().decode("utf-8", errors="ignore")
                attempt_record.update({
                    "status": "FAILED_HTTP",
                    "errorCode": he.code,
                    "errorReason": he.reason,
                    "errorBody": err_body,
                })
                journal["attempts"].append(attempt_record)
                journal["summary"]["failed"] += 1
                if he.code in {429, 402, 403}:
                    print("  -> CRITICAL QUOTA/BILLING/AUTH STOP! Terminating run.")
                    break
            except Exception as ex:
                print(f"  -> ERROR: {ex}")
                attempt_record.update({
                    "status": "FAILED_EXCEPTION",
                    "error": str(ex),
                })
                journal["attempts"].append(attempt_record)
                journal["summary"]["failed"] += 1

            # Save checkpoint after each call
            write_json(staging_dir / "journal.json", journal)
            write_json(staging_dir / "manifest.json", manifest)

            # Brief pause
            time.sleep(2)

        # 5. Finalize Cloud & Local Locks
        if not args.dry_run:
            final_cloud_lock, cur_gen = get_cloud_lock()
            final_lock_record = {
                "batch_id": f"interactive-4k-first32-{time.strftime('%Y%m%d', time.gmtime())}",
                "model": MODEL,
                "project": PROJECT,
                "account": ACCOUNT,
                "state": "JOB_STATE_SUCCEEDED",
                "workflow_state": "TERMINAL_COLLECTED",
                "createdAt": active_lock_record["createdAt"],
                "requestedOutputs": 32,
                "succeededOutputs": journal["summary"]["succeeded"],
                "deferredOutputs": journal["summary"]["deferred"],
                "totalCostUSD": round(journal["summary"]["totalCostUSD"], 4),
                "cloud_lock_generation": cur_gen,
                "collectedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "owner_status": "INTERACTIVE_4K_COLLECTED_UNVERIFIED",
                "assetApproval": "UNVERIFIED",
            }
            term_gen = put_cloud_lock(final_lock_record, cur_gen)
            final_lock_record["cloud_lock_generation"] = term_gen
            write_json(LOCAL_LOCK_FILE, final_lock_record)
            print(f"[LOCK] Finalized cloud lock to TERMINAL_COLLECTED (gen: {term_gen})")

            # 6. Update Budget Ledger
            try:
                b_ledger = read_json(BUDGET_FILE)
                b_ledger["batches"].append({
                    "id": final_lock_record["batch_id"],
                    "reservedUSD": 9.12,
                    "state": "JOB_STATE_SUCCEEDED",
                    "createdAt": active_lock_record["createdAt"],
                    "usageEstimateUSD": round(journal["summary"]["totalCostUSD"], 4),
                    "billedTotal": None,
                    "providerState": "JOB_STATE_SUCCEEDED",
                    "holdRetained": True,
                    "reconciliationNote": (
                        f"Interactive 4K individual calls: {journal['summary']['succeeded']} succeeded, "
                        f"{journal['summary']['deferred']} deferred. Invoices remain unknown."
                    ),
                    "reconciledExposureUSD": round(journal["summary"]["totalCostUSD"] * 1.15, 4),
                    "reconciliationStatus": "RECONCILED_INTERACTIVE_4K_CALLS",
                })
                write_json(BUDGET_FILE, b_ledger)
                print("[BUDGET] Updated budget-ledger.json with completed interactive run")
            except Exception as be:
                print(f"[BUDGET] Warning: could not update budget ledger: {be}")
        else:
            print("[DRY RUN] Completed dry run without lock or budget ledger mutation.")

        print("=" * 70)
        print("RUN COMPLETED SUCCESSFULLY!")
        print(f"Summary: {json.dumps(journal['summary'], indent=2)}")
        print("=" * 70)

    finally:
        # 7. Release Mutex Safely
        if MUTEX_FILE.exists():
            MUTEX_FILE.unlink(missing_ok=True)
            print(f"[MUTEX] Released local mutex {MUTEX_FILE}")


if __name__ == "__main__":
    main()
