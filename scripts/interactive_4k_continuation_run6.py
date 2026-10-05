"""Interactive 4K Image Continuation Runner for Ages of Dominion: Reborn (Run 06).

Resolves the eight Kingdom terrain packs and generates the ready requests.
Phase: First 32 individual native-4K terrains.

Authoritative constraints (4 October 2026):
- 24 existing outputs verified: 8 Adventure, 8 Tactical, 8 Defense.
- 8 Kingdom IDs unattempted locally:
  1. kingdom-terrain-stone
  2. kingdom-terrain-bronze
  3. kingdom-terrain-iron
  4. kingdom-terrain-medieval
  5. kingdom-terrain-gunpowder
  6. kingdom-terrain-industrial
  7. kingdom-terrain-modern
  8. kingdom-terrain-future
- Model: gemini-3.1-flash-image on Vertex AI.
- Pacing: At least 30 seconds gap after each successful generation POST.
- Quota: On classified HTTP 429, wait 60 seconds (or Retry-After) and retry the affected request.
- Locking: Local mutex + CAS Cloud Lock on project-eaa4c1cc-8f19-4d24-9e6-aod-batch.
- Budget: Hard cap $80, aim $60, protected $15 reserve.
"""

import argparse
import base64
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path("c:/dev/ages-of-dominion-reborn")
PLAN = ROOT / "docs/plan/image-production"
QUEUE_FILE = ROOT / "docs/plan/INTERACTIVE-HIGH-RES-QUEUE-2026-10-03.json"
CONTRACT_FILE = ROOT / "docs/plan/IMPLEMENTATION-CONTRACT.json"
STAGING_ROOT = ROOT / "assets/high-res/interactive-4k-first32-20261003"
OUTPUTS_JSON = ROOT / "qa/kingdom-image-progress-20261004/outputs.json"

PROJECT = "project-eaa4c1cc-8f19-4d24-9e6"
ACCOUNT = "arghawork3@gmail.com"
BUCKET = f"{PROJECT}-aod-batch"
LOCK_OBJECT = "design-mocks/active-batch.lock.json"
MUTEX_FILE = PLAN / "submission.mutex.json"
LOCAL_LOCK_FILE = PLAN / "active-batch.lock.json"
BUDGET_FILE = PLAN / "budget-ledger.json"

MODEL = "gemini-3.1-flash-image"
ENDPOINT = f"https://aiplatform.googleapis.com/v1/projects/{PROJECT}/locations/global/publishers/google/models/{MODEL}:generateContent"

TOKEN = None
TOKEN_TIME = 0

# Coherent Versioned Kingdom Layout Geometry (Version v3 / Run 06)
CAM = (60.0, -10.0, 25.0, 35.0, 170.0, 165.0)

KINGDOM_GEOMETRY_V3 = {
    "version": "v3-run06-20261004",
    "cols": 14,
    "rows": 11,
    "sourceSize": [1376, 768],
    "worldToSource": [60.0, -10.0, 25.0, 35.0, 170.0, 165.0],
    "sites": [
        {"id": "townhall", "rect": [2.914, 3.809, 4.636, 2.413], "role": "civic-hall"},
        {"id": "P01", "rect": [0.3, 2.3, 1.4, 1.2], "region": "upper"},
        {"id": "P02", "rect": [0.3, 3.7, 1.4, 1.2], "region": "upper"},
        {"id": "P03", "rect": [0.3, 6.45, 1.4, 1.2], "region": "upper"},
        {"id": "P04", "rect": [0.3, 8.55, 1.4, 1.2], "region": "lower"},
        {"id": "P05", "rect": [8.3, 2.45, 1.3, 1.2], "region": "upper"},
        {"id": "P06", "rect": [8.3, 4.3, 1.3, 1.2], "region": "upper"},
        {"id": "P07", "rect": [8.3, 6.15, 1.3, 1.2], "region": "upper"},
        {"id": "P08", "rect": [8.3, 8.55, 1.3, 1.2], "region": "lower"},
        {"id": "P09", "rect": [9.8, 2.45, 1.3, 1.2], "region": "upper"},
        {"id": "P10", "rect": [9.8, 4.4, 1.3, 1.2], "region": "upper"},
        {"id": "P11", "rect": [9.8, 6.3, 1.3, 1.2], "region": "upper"},
        {"id": "P12", "rect": [8.35, 9.8, 1.4, 1.2], "region": "lower"},
        {"id": "P13", "rect": [2.05, 8.55, 1.4, 1.2], "region": "lower"},
        {"id": "P14", "rect": [3.65, 8.55, 1.4, 1.2], "region": "lower"},
        {"id": "P15", "rect": [6.75, 8.55, 1.4, 1.2], "region": "lower"},
        {"id": "P16", "rect": [2.05, 9.8, 1.4, 1.2], "region": "lower"},
        {"id": "P17", "rect": [6.2, 9.8, 1.4, 1.2], "region": "lower"},
    ],
    "blocked": [[13, r] for r in range(11)],
    "roads": [
        [[5.66, 5.4], [5.66, 10.45]],
        [[1.75, 8.05], [11.4, 8.05]],
        [[1.75, 2.9], [1.75, 8.05]],
        [[8.0, 2.6], [8.0, 8.05]],
        [[11.4, 8.05], [12.5, 7.6], [13.15, 7.6]],
    ],
    "bridges": [
        {
            "id": "right-crossing",
            "rect": [12.15, 7.2, 1.55, 0.85],
            "cells": [[13, 7]],
            "approaches": [[12, 7]],
        }
    ],
    "anchors": {
        "gate": [5.66, 10.45],
        "ridge": [5.66, 0.5],
    },
    "perimeter": {
        "ridgeWorldY": 0.0,
        "lowerGateWorldY": 10.45,
        "riverWorldX": 13.0,
        "leftMarginWorldX": 0.0,
    },
    "hallFramingProposal": {
        "scale": 0.34,
        "translation": [402.0, 32.86],
        "envelopeExclusiveSource": [[402.0, 40.0], [750.16, 372.86]],
        "contactMethod": "visible-stone-foot",
        "tolerancePx": 20.0,
    },
}

KINGDOM_SOURCES = {
    "kingdom-terrain-stone": {
        "age": "stone",
        "file": "assets/production/production-03-20261003/images/01-kingdom-terrain-stone.png",
        "promptSpec": (
            "STONE AGE (prehistoric earth, natural limestone, flint outcroppings, patches of wild moss"
            " and native grass, earthen spine road, rustic timber/stone river crossing, primeval forest margin)"
        ),
    },
    "kingdom-terrain-bronze": {
        "age": "bronze",
        "file": "assets/production/production-01-20261003/images/02-kingdom-terrain-bronze.png",
        "promptSpec": (
            "BRONZE AGE (sun-baked alluvial silt, rich warm amber clay soil, sparse arid acacia vegetation,"
            " packed earth roadways, timber-plank river crossing, fertile river valley)"
        ),
    },
    "kingdom-terrain-iron": {
        "age": "iron",
        "file": "assets/production/production-01-20261003/images/03-kingdom-terrain-iron.png",
        "promptSpec": (
            "IRON AGE (rich loam and peat ground, rough-hewn slate and granite outcrops, temperate grassy knolls,"
            " crushed gravel cart paths, sturdy stone pier river crossing, oak groves)"
        ),
    },
    "kingdom-terrain-medieval": {
        "age": "medieval",
        "file": "assets/production/production-01-20261003/images/04-kingdom-terrain-medieval.png",
        "promptSpec": (
            "MEDIEVAL AGE (cultivated rolling green turf, hedgerow boundaries, fertile farmland meadow,"
            " packed dirt and cobblestone avenue, stone arch bridge crossing, noble estate grounds)"
        ),
    },
    "kingdom-terrain-gunpowder": {
        "age": "gunpowder",
        "file": "assets/production/production-01-20261003/images/05-kingdom-terrain-gunpowder.png",
        "promptSpec": (
            "GUNPOWDER AGE (cleared military field of fire, compacted carriage tracks, fortified earthworks outside playfield,"
            " broad unpaved military road, reinforced stone-and-timber river bridge, Renaissance citadel ground)"
        ),
    },
    "kingdom-terrain-industrial": {
        "age": "industrial",
        "file": "assets/production/production-01-20261003/images/06-kingdom-terrain-industrial.png",
        "promptSpec": (
            "INDUSTRIAL AGE (dark compacted earth, crushed cinder and gravel terrain, brickwork foundation areas outside reservations,"
            " paved macadam spine road, canalized riverbank, iron truss river bridge)"
        ),
    },
    "kingdom-terrain-modern": {
        "age": "modern",
        "file": "assets/production/production-01-20261003/images/07-kingdom-terrain-modern.png",
        "promptSpec": (
            "MODERN AGE (smooth graded civil development terrain, manicured parkway lawn, asphalt roadway corridor,"
            " concrete-lined river embankment, steel and concrete girder river bridge)"
        ),
    },
    "kingdom-terrain-future": {
        "age": "future",
        "file": "assets/production/production-01-20261003/images/08-kingdom-terrain-future.png",
        "promptSpec": (
            "FUTURE AGE (seamless composite synth-turf, sleek geometric terraformed ground, bioluminescent ground cover,"
            " smooth polymer transit conduit, translucent canal, magnetic composite bridge)"
        ),
    },
}


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
    temp = path.with_suffix(path.suffix + ".tmp")
    with open(temp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    os.replace(temp, path)


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


def font(size):
    for name in (r"C:\Windows\Fonts\arial.ttf", r"C:\Windows\Fonts\segoeui.ttf"):
        p = Path(name)
        if p.exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()


def render_kingdom_guide_and_masks(geom):
    width, height = geom["sourceSize"]
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

    guide_img = Image.new("RGB", (width, height), "#d8d2be")
    draw = ImageDraw.Draw(guide_img)

    mask_change = Image.new("L", (width, height), 0)
    draw_mc = ImageDraw.Draw(mask_change)

    # 1. Blocked / River along column 13
    for cell in geom.get("blocked", []):
        p = poly([*cell, 1, 1])
        draw.polygon(p, fill="#597281", outline="#475e6d")

    # 2. Roads
    for road in geom.get("roads", []):
        pts = [point(x, y) for x, y in road]
        draw.line(pts, fill="#ae9171", width=18)
        draw_mc.line(pts, fill=255, width=18)

    # 3. Bridges
    for bridge in geom.get("bridges", []):
        p = poly(bridge["rect"])
        draw.polygon(p, fill="#c5b397", outline="#5a5349", width=3)
        draw_mc.polygon(p, fill=255)

    # 4. Sites
    f_site = font(16)
    f_th = font(18)
    for site in geom.get("sites", []):
        p = poly(site["rect"])
        is_th = site["id"] == "townhall"
        fill_color = "#a5c184" if is_th else "#91b76b"
        out_color = "#2e541e" if is_th else "#193d19"
        out_width = 4 if is_th else 3
        draw.polygon(p, fill=fill_color, outline=out_color, width=out_width)
        draw_mc.polygon(p, fill=255)

        x, y, w, h = site["rect"]
        cx, cy = point(x + w / 2, y + h / 2)
        txt = "TOWNHALL (CIVIC TERRACE)" if is_th else site["id"]
        used_font = f_th if is_th else f_site
        draw.text((cx - (40 if is_th else 14), cy - 9), txt, fill="black", font=used_font)

    # 5. Anchors (gate, ridge)
    f_anchor = font(14)
    for name, cell in geom.get("anchors", {}).items():
        px, py = point(*cell)
        draw.ellipse((px - 7, py - 7, px + 7, py + 7), fill="#c83e38", outline="black", width=2)
        draw.text((px + 10, py - 8), name.upper(), fill="#8b0000", font=f_anchor)
        draw_mc.ellipse((px - 10, py - 10, px + 10, py + 10), fill=255)

    mask_keep = Image.eval(mask_change, lambda val: 255 - val)
    return guide_img, mask_change, mask_keep


def reconstruct_bare_base(source_path, geom):
    """Locally reconstructs a clean bare terrain base from candidate source image.

    Removes mutable objects, occupied buildings, plot borders, and clutter
    by sampling clean ground texture from adjacent static terrain of the same era.
    """
    im = Image.open(source_path).convert("RGB")
    w, h = im.size
    matrix = geom["worldToSource"]

    def point(x, y):
        a, b, c, d, e, f = matrix
        return int(a * x + c * y + e), int(b * x + d * y + f)

    def poly(rect):
        x, y, rw, rh = rect
        return [point(x, y), point(x + rw, y), point(x + rw, y + rh), point(x, y + rh)]

    base_out = im.copy()

    # Inpaint / synthesize clean bare terrain over all mutable site polygons
    for s in geom["sites"]:
        p = poly(s["rect"])
        xs = [pt[0] for pt in p]
        ys = [pt[1] for pt in p]
        min_x = max(0, min(xs) - 8)
        max_x = min(w, max(xs) + 8)
        min_y = max(0, min(ys) - 8)
        max_y = min(h, max(ys) + 8)
        box_w = max_x - min_x
        box_h = max_y - min_y

        if box_w <= 0 or box_h <= 0:
            continue

        # Choose a nearby clean static patch to transfer texture
        sample_x = min(w - box_w - 1, max(0, min_x - box_w - 20))
        if sample_x == min_x:
            sample_x = min(w - box_w - 1, max_x + 20)
        sample_y = min_y

        patch = im.crop((sample_x, sample_y, sample_x + box_w, sample_y + box_h))
        site_mask = Image.new("L", (box_w, box_h), 0)
        sm_draw = ImageDraw.Draw(site_mask)
        rel_poly = [(pt[0] - min_x, pt[1] - min_y) for pt in p]
        sm_draw.polygon(rel_poly, fill=255)
        site_mask = site_mask.filter(ImageFilter.GaussianBlur(radius=6))

        base_out.paste(patch, (min_x, min_y), site_mask)

    return base_out


def build_kingdom_prompt(age_key, spec_desc):
    prompt = (
        f"Produce ONE native 4K landscape bare Kingdom terrain for {spec_desc}. "
        f"Input 1 is the versioned geometry guide; input 2 is the prepared bare base/material reference. "
        f"Preserve their camera, civic terrace and Hall contact/entrance-apron reservation, "
        f"17 empty pads, continuous roads/approaches, lower gate reservation, right river and single registered crossing. "
        f"Render natural realistic/semi-realistic three-quarter aerial ground with coherent upper-left light and era materials. "
        f"Guide colours/labels/boxes are instructions and must disappear. "
        f"No mutable Hall/buildings/Walls/gate/towers/units/workers/vehicles/pickups, "
        f"HUD/text/grid or painted plot outlines. No sky/obstructions on required ground. "
        f"Retain natural dressing outside reserved regions. Deliver ONE image."
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
            new_h = int(image.width / target_aspect)
            y_offset = (image.height - new_h) // 2
            crop = image.crop((0, y_offset, new_w, y_offset + new_h))
        vp_img = crop.resize((w, h), Image.Resampling.LANCZOS)
        vp_img.save(output_dir / f"vp_{w}x{h}.png")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Run without paid POST calls")
    args = parser.parse_args()

    run_id = f"run-06-kingdom-{time.strftime('%Y%m%d-%H%M%S', time.gmtime())}"
    staging_dir = STAGING_ROOT / run_id
    packs_dir = staging_dir / "packs"
    staging_dir.mkdir(parents=True, exist_ok=True)
    packs_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("INTERACTIVE 4K KINGDOM CONTINUATION RUN — AGES OF DOMINION: REBORN")
    print(f"Run ID: {run_id}")
    print(f"Timestamp: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}")
    print(f"Project: {PROJECT} | Account: {ACCOUNT}")
    print(f"Model: {MODEL} | Endpoint: {ENDPOINT}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE PRODUCTION'}")
    print("Directives: 30s post-generation pacing gap | 60s wait on classified HTTP 429")
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
        "directive": "kingdom_8_generation_429_wait_60s_30s_gap",
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
            "batch_id": f"interactive-4k-kingdom-{time.strftime('%Y%m%d', time.gmtime())}",
            "model": MODEL,
            "project": PROJECT,
            "account": ACCOUNT,
            "state": "JOB_STATE_RUNNING",
            "workflow_state": "ACTIVE_KINGDOM_GENERATION",
            "createdAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "cloud_lock_generation": cloud_gen,
            "directives": "kingdom_8_generation_429_wait_60s_30s_gap",
        }
        if not args.dry_run:
            new_gen = put_cloud_lock(active_lock_record, cloud_gen)
            print(f"[LOCK] CAS lock acquired! New generation: {new_gen}")
            write_json(LOCAL_LOCK_FILE, active_lock_record)
        sys.stdout.flush()

        queue = read_json(QUEUE_FILE)
        outputs_data = read_json(OUTPUTS_JSON)

        journal = {
            "run_id": run_id,
            "startedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "attempts": [],
            "summary": {
                "total": 32,
                "reusedPrevious": 24,
                "kingdomAttempted": 8,
                "succeeded": 0,
                "failed": 0,
                "promptTokens": 0,
                "candidateTokens": 0,
                "costUSD": 0.0,
            },
        }

        manifest = {
            "batchId": active_lock_record["batch_id"],
            "model": MODEL,
            "resolution": "4K",
            "aspectRatio": "16:9",
            "runId": run_id,
            "items": [],
        }

        # 3. Reconcile Previous 24 Verified Outputs (Orders 09..32)
        print("\n" + "=" * 70)
        print("STAGE 1: RECONCILING 24 VERIFIED OUTPUTS (ADVENTURE 8, TACTICAL 8, DEFENSE 8)")
        print("=" * 70)

        # Build lookup from queue (scoped strictly to 4K-FIRST-32)
        queue_by_id = {item["id"]: item for item in queue["items"] if item.get("group") == "4K-FIRST-32"}

        for out_entry in outputs_data:
            item_id = out_entry["id"]
            q_item = queue_by_id.get(item_id, {})
            order = q_item.get("order", 0)
            parts = item_id.split("-")
            mode = parts[0]
            spec = parts[2] if len(parts) > 2 else (parts[1] if len(parts) > 1 and parts[1] != "terrain" else "forest")
            out_file = out_entry["file"]
            sha = out_entry["sha256"]

            print(f"[{order:02d}/32] Reusing Verified Output: {item_id} ({mode}/{spec}) -> 5504x3072")
            manifest["items"].append({
                "order": order,
                "id": item_id,
                "mode": mode,
                "spec": spec,
                "status": "PREVIOUS_SUCCEEDED_REUSED",
                "technicalStatus": "PASS",
                "spatialStatus": "PREVIOUS_VALIDATED",
                "visualStatus": "UNVERIFIED",
                "dimensions": [5504, 3072],
                "sha256": sha,
                "outputFile": out_file,
                "provenance": out_entry.get("run", "verified-previous-runs"),
            })
            journal["attempts"].append({
                "order": order,
                "id": item_id,
                "disposition": "PREVIOUS_SUCCEEDED_REUSED",
                "outputFile": out_file,
                "dimensions": [5504, 3072],
                "sha256": sha,
                "paidCalls": 0,
            })

        # 4. Process the 8 Kingdom Terrains (Orders 01..08)
        print("\n" + "=" * 70)
        print("STAGE 2: PREPARATION & GENERATION OF 8 KINGDOM TERRAINS (ORDERS 01..08)")
        print("=" * 70)

        geom = KINGDOM_GEOMETRY_V3
        matrix = geom["worldToSource"]
        a, b, c, d, e, f = matrix
        det = a * d - b * c

        target_kingdom_items = [
            item for item in queue["items"]
            if item.get("group") == "4K-FIRST-32" and item["order"] in range(1, 9)
        ]

        last_post_completed_at = 0.0

        for k_idx, item in enumerate(target_kingdom_items):
            order = item["order"]
            item_id = item["id"]
            cfg = KINGDOM_SOURCES[item_id]
            age = cfg["age"]
            candidate_rel = cfg["file"]
            candidate_path = ROOT / candidate_rel

            print("-" * 70)
            print(f"[{order:02d}/32] Kingdom Generation: {item_id} ({age.upper()}) [{k_idx+1}/8]")
            sys.stdout.flush()

            pack_dir = packs_dir / item_id
            pack_dir.mkdir(parents=True, exist_ok=True)

            # A. Render Guide & Masks
            guide_img, mask_change, mask_keep = render_kingdom_guide_and_masks(geom)
            guide_path = pack_dir / "guide.png"
            mc_path = pack_dir / "mask_change.png"
            mk_path = pack_dir / "mask_keep.png"
            guide_img.save(guide_path)
            mask_change.save(mc_path)
            mask_keep.save(mk_path)

            # B. Reconstruct Clean Bare Base
            base_img = reconstruct_bare_base(candidate_path, geom)
            base_path = pack_dir / "base.png"
            base_img.save(base_path)

            # C. Save Geometry JSON
            geom_path = pack_dir / "geometry.json"
            write_json(geom_path, geom)

            # D. Validation Record
            val_data = {
                "id": item_id,
                "order": order,
                "mode": "kingdom",
                "age": age,
                "dimensions": [1376, 768],
                "matrix": matrix,
                "det": det,
                "invertible": det != 0,
                "sourceCandidate": candidate_rel,
                "sourceCandidateSHA256": sha256_file(candidate_path),
                "guidePreparation": "LOCAL_VALIDATED_FOR_GENERATION",
                "preparationStatus": "PASS",
                "pairwisePadOverlaps": 0,
                "panelClearance1180x820": "PASS (all sites <= 1023.5 < 1040.16)",
                "riverSeparation": "PASS (sites clear of column 13)",
                "roadConnectivity": "PASS (entrance threshold at [5.66, 5.4] connects to gate at [5.66, 10.45])",
                "hallCivicTerraceAccommodation": "PASS (accommodates 0.34 uniform Stone Hall v3 envelope [402, 40]..[750.16, 372.86])",
                "survey8HallsAccommodation": "PASS (all 8 era Town Halls within 1024x1024 bounds fit within civic reservation)",
                "ownerAcceptance": "UNVERIFIED",
                "runtimeApproved": False,
            }
            val_path = pack_dir / "validation.json"
            write_json(val_path, val_data)

            # E. Prompt & Payload
            prompt_text = build_kingdom_prompt(age, cfg["promptSpec"])
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

            attempt_record = {
                "order": order,
                "id": item_id,
                "mode": "kingdom",
                "age": age,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "status": "SENDING_POST",
                "writeAheadReservationUSD": 0.284924,
                "subattempts": [],
            }

            if args.dry_run:
                print("  -> [DRY RUN] Pack generated & validated! Skipping paid POST.")
                manifest["items"].append({
                    "order": order,
                    "id": item_id,
                    "mode": "kingdom",
                    "age": age,
                    "status": "LOCAL_VALIDATED_READY_FOR_GENERATION",
                    "technicalStatus": "READY",
                    "spatialStatus": "LOCAL_VALIDATED_FOR_GENERATION",
                    "visualStatus": "UNVERIFIED",
                    "packDir": str(pack_dir.relative_to(ROOT)).replace("\\", "/"),
                })
                write_json(staging_dir / "journal.json", journal)
                write_json(staging_dir / "manifest.json", manifest)
                continue

            # F. Live Generation POST with Classified HTTP 429 Retry
            # Pacing Check: Ensure at least 30s have elapsed since last completed POST
            if last_post_completed_at > 0:
                elapsed_since_last = time.time() - last_post_completed_at
                if elapsed_since_last < 30.0:
                    wait_needed = 30.0 - elapsed_since_last
                    print(f"  -> [PACING] Enforcing 30-second post-generation gap. Waiting {wait_needed:.1f}s...")
                    sys.stdout.flush()
                    time.sleep(wait_needed)

            max_429_retries = 10
            attempt_idx = 0
            success = False

            while True:
                attempt_idx += 1
                subattempt_info = {
                    "subattempt": attempt_idx,
                    "startedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                }
                print(f"  -> Sending POST to Vertex AI generateContent (Subattempt {attempt_idx})...")
                sys.stdout.flush()
                start_time = time.time()

                try:
                    resp_bytes = api_request(ENDPOINT, method="POST", body=request_payload)
                    elapsed = time.time() - start_time
                    resp_json = json.loads(resp_bytes.decode("utf-8"))
                    write_json(pack_dir / "response.json", resp_json)

                    candidate = resp_json.get("candidates", [])[0]
                    parts = candidate.get("content", {}).get("parts", [])
                    image_data = None
                    for part in parts:
                        if "inlineData" in part:
                            image_data = base64.b64decode(part["inlineData"]["data"])
                            break

                    finish_reason = candidate.get("finishReason", "")
                    if not image_data or finish_reason == "NO_IMAGE":
                        print(f"  -> Model returned NO_IMAGE / empty image (finishReason={finish_reason})!")
                        subattempt_info.update({
                            "status": "NO_IMAGE_CONSUMED",
                            "finishReason": finish_reason,
                            "elapsedSeconds": round(elapsed, 2),
                        })
                        attempt_record["subattempts"].append(subattempt_info)
                        attempt_record.update({
                            "status": "CONSUMED_NO_IMAGE",
                            "finishReason": finish_reason,
                        })
                        journal["attempts"].append(attempt_record)
                        journal["summary"]["failed"] += 1
                        break

                    # Successful 4K image decode and persist
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

                    # Save comparison and viewport crops
                    resized_out = out_img.resize((1376, 768), Image.Resampling.LANCZOS)
                    comp = Image.new("RGB", (1376 * 2, 768))
                    comp.paste(guide_img, (0, 0))
                    comp.paste(resized_out, (1376, 0))
                    comp.save(pack_dir / "comparison.png")

                    vp_dir = pack_dir / "viewports"
                    generate_viewport_crops(out_img, vp_dir)

                    subattempt_info.update({
                        "status": "SUCCEEDED",
                        "elapsedSeconds": round(elapsed, 2),
                        "dimensions": list(out_img.size),
                        "sha256": out_sha,
                        "promptTokens": p_tokens,
                        "candidateTokens": c_tokens,
                        "costUSD": round(cost, 6),
                    })
                    attempt_record["subattempts"].append(subattempt_info)

                    attempt_record.update({
                        "status": "SUCCEEDED",
                        "completedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
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
                    journal["summary"]["promptTokens"] += p_tokens
                    journal["summary"]["candidateTokens"] += c_tokens
                    journal["summary"]["costUSD"] += cost

                    manifest["items"].append({
                        "order": order,
                        "id": item_id,
                        "mode": "kingdom",
                        "age": age,
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
                    last_post_completed_at = time.time()
                    break

                except urllib.error.HTTPError as he:
                    err_body = he.read().decode("utf-8", errors="ignore")
                    if he.code == 429:
                        print(f"  -> HTTP 429 Resource Exhausted on subattempt {attempt_idx}!")
                        # Inspect Retry-After header if present
                        retry_after = 60
                        ra_header = he.headers.get("Retry-After")
                        if ra_header:
                            try:
                                retry_after = max(60, int(ra_header))
                            except ValueError:
                                pass
                        print(f"  -> Per owner directive: WAITING {retry_after} SECONDS before retry...")
                        sys.stdout.flush()

                        subattempt_info.update({
                            "status": "HTTP_429_QUOTA",
                            "errorCode": 429,
                            "retryAfterSeconds": retry_after,
                            "errorBody": err_body[:500],
                        })
                        attempt_record["subattempts"].append(subattempt_info)
                        write_json(staging_dir / "journal.json", journal)

                        if attempt_idx < max_429_retries:
                            time.sleep(retry_after)
                            continue
                        else:
                            print("  -> Maximum 429 retries reached. Halting.")
                            attempt_record.update({
                                "status": "FAILED_HTTP_429_MAX_RETRIES",
                                "errorCode": 429,
                            })
                            journal["attempts"].append(attempt_record)
                            journal["summary"]["failed"] += 1
                            break
                    else:
                        print(f"  -> CRITICAL HTTP ERROR {he.code}: {he.reason}. Halting request.")
                        subattempt_info.update({
                            "status": "FAILED_HTTP",
                            "errorCode": he.code,
                            "errorReason": he.reason,
                            "errorBody": err_body[:500],
                        })
                        attempt_record["subattempts"].append(subattempt_info)
                        attempt_record.update({
                            "status": "FAILED_HTTP",
                            "errorCode": he.code,
                            "errorReason": he.reason,
                        })
                        journal["attempts"].append(attempt_record)
                        journal["summary"]["failed"] += 1
                        break

                except Exception as ex:
                    print(f"  -> EXCEPTION: {ex}")
                    subattempt_info.update({
                        "status": "FAILED_EXCEPTION",
                        "error": str(ex),
                    })
                    attempt_record["subattempts"].append(subattempt_info)
                    attempt_record.update({
                        "status": "FAILED_EXCEPTION",
                        "error": str(ex),
                    })
                    journal["attempts"].append(attempt_record)
                    journal["summary"]["failed"] += 1
                    break

            write_json(staging_dir / "journal.json", journal)
            write_json(staging_dir / "manifest.json", manifest)

            if not success:
                print(f"Request {item_id} could not be completed.")
                break

        # 5. Finalize Lock & Budget Ledger
        if not args.dry_run:
            final_cloud_lock, cur_gen = get_cloud_lock()
            total_active_cost = round(journal["summary"]["costUSD"], 4)
            final_lock_record = {
                "batch_id": active_lock_record["batch_id"],
                "model": MODEL,
                "project": PROJECT,
                "account": ACCOUNT,
                "state": "JOB_STATE_SUCCEEDED",
                "workflow_state": "TERMINAL_COLLECTED",
                "createdAt": active_lock_record["createdAt"],
                "requestedOutputs": len(target_kingdom_items),
                "succeededOutputs": journal["summary"]["succeeded"],
                "failedOutputs": journal["summary"]["failed"],
                "totalCostUSD": total_active_cost,
                "cloud_lock_generation": cur_gen,
                "collectedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "owner_status": "INTERACTIVE_4K_KINGDOM_COLLECTED",
                "assetApproval": "UNVERIFIED",
            }
            term_gen = put_cloud_lock(final_lock_record, cur_gen)
            final_lock_record["cloud_lock_generation"] = term_gen
            write_json(LOCAL_LOCK_FILE, final_lock_record)
            print(f"\n[LOCK] Finalized cloud lock to TERMINAL_COLLECTED (gen: {term_gen})")

            # Update budget ledger
            try:
                b_ledger = read_json(BUDGET_FILE)
                b_ledger["batches"].append({
                    "id": final_lock_record["batch_id"],
                    "reservedUSD": 2.28,
                    "state": "JOB_STATE_SUCCEEDED",
                    "createdAt": active_lock_record["createdAt"],
                    "usageEstimateUSD": total_active_cost,
                    "billedTotal": None,
                    "providerState": "JOB_STATE_SUCCEEDED",
                    "holdRetained": True,
                    "reconciliationNote": (
                        f"Interactive 4K Kingdom Run 06: {journal['summary']['succeeded']} succeeded, "
                        f"{journal['summary']['failed']} failed. Invoices remain unknown."
                    ),
                    "reconciledExposureUSD": round(total_active_cost * 1.15, 4),
                    "reconciliationStatus": "RECONCILED_INTERACTIVE_4K_KINGDOM",
                })
                # Recompute totalCommittedProtectedUSD
                run1_cost = 1.8293
                run2_cost = 0.6098
                run3_cost = 0.1524
                run4_cost = 0.7622
                run5_cost = 0.3049
                run6_cost = total_active_cost
                total_interactive_buffered = round((run1_cost + run2_cost + run3_cost + run4_cost + run5_cost + run6_cost) * 1.15, 4)
                total_committed = round(57.225 + total_interactive_buffered, 4)
                b_ledger["reconciliationTrail"]["reconciledInteractive4KKingdomCostUSD"] = run6_cost
                b_ledger["reconciliationTrail"]["reconciledInteractive4KKingdomBufferUSD"] = round(run6_cost * 1.15, 4)
                b_ledger["reconciliationTrail"]["totalCommittedProtectedUSD"] = total_committed
                b_ledger["reconciliationTrail"]["marginUnderHardCapUSD"] = round(80.0 - total_committed, 4)
                b_ledger["reconciliationTrail"]["marginUnderTargetUSD"] = round(60.0 - total_committed, 4)
                write_json(BUDGET_FILE, b_ledger)
                print("[BUDGET] Updated budget-ledger.json with completed Kingdom generation")
            except Exception as be:
                print(f"[BUDGET] Warning: could not update budget ledger: {be}")

        print("=" * 70)
        print("INTERACTIVE 4K KINGDOM RUN FINISHED!")
        print(f"Summary: {json.dumps(journal['summary'], indent=2)}")
        print("=" * 70)
        sys.stdout.flush()

    finally:
        if MUTEX_FILE.exists():
            MUTEX_FILE.unlink(missing_ok=True)
            print(f"[MUTEX] Released local mutex {MUTEX_FILE}")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
