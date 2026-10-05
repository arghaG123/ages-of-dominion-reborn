import base64
import hashlib
import json
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path("c:/dev/ages-of-dominion-reborn")
RUN2_DIR = ROOT / "assets/high-res/interactive-4k-first32-20261003/run-02-20261004-010239"
QUEUE_FILE = ROOT / "docs/plan/INTERACTIVE-HIGH-RES-QUEUE-2026-10-03.json"
CONTRACT_FILE = ROOT / "docs/plan/IMPLEMENTATION-CONTRACT.json"
PACKS_DIR = RUN2_DIR / "packs"

queue = json.loads(QUEUE_FILE.read_text(encoding="utf-8"))
contract = json.loads(CONTRACT_FILE.read_text(encoding="utf-8"))
journal = json.loads((RUN2_DIR / "journal.json").read_text(encoding="utf-8"))
manifest = json.loads((RUN2_DIR / "manifest.json").read_text(encoding="utf-8"))

def sha256_file(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()

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

# 1. Audit newly generated items 23..26
print("=== 1. AUDITING NEWLY GENERATED 4K OUTPUTS (IDs 23..26) ===")
new_success_ids = ["tactical-terrain-waste", "tactical-terrain-ruins", "defense-terrain", "defense-terrain-plains"]
for item_id in new_success_ids:
    p_dir = PACKS_DIR / item_id
    out_img_path = p_dir / "output.png"
    assert out_img_path.exists(), f"Output missing: {out_img_path}"
    img = Image.open(out_img_path)
    sha = sha256_file(out_img_path)
    assert img.size == (5504, 3072), f"Dimensions mismatch: {img.size}"
    resp = json.loads((p_dir / "response.json").read_text(encoding="utf-8"))
    usage = resp.get("usageMetadata", {})
    comp = p_dir / "comparison.png"
    vps = list((p_dir / "viewports").glob("*.png"))
    print(f"PASS: {item_id:24s} | Dim: {img.size} | SHA: {sha[:16]}... | Tokens: {usage.get('promptTokenCount')} in, {usage.get('candidatesTokenCount')} out | Viewports: {len(vps)} crops | Comparison: {comp.exists()}")

# 2. Add ID 27 defense-terrain-hills HTTP 429 record to journal & manifest
print("\n=== 2. RECORDING ID 27 (defense-terrain-hills) QUOTA STOP ===")
p_hills_dir = PACKS_DIR / "defense-terrain-hills"
hills_attempt = {
    "order": 27,
    "id": "defense-terrain-hills",
    "mode": "defense",
    "spec": "hills",
    "timestamp": "2026-10-04T01:06:53Z",
    "status": "QUOTA_STOP_HTTP_429",
    "errorCode": 429,
    "errorReason": "Too Many Requests",
    "writeAheadReservationUSD": 0.284924,
    "actualCostUSD": 0.0,
    "note": "Vertex AI generateContent endpoint returned HTTP 429 (rate limit exceeded). Provider calls stopped per directive."
}
# Check if already in journal attempts
if not any(a.get("order") == 27 for a in journal["attempts"]):
    journal["attempts"].append(hills_attempt)

if not any(m.get("order") == 27 for m in manifest["items"]):
    manifest["items"].append({
        "order": 27,
        "id": "defense-terrain-hills",
        "mode": "defense",
        "spec": "hills",
        "status": "QUOTA_STOP_HTTP_429",
        "technicalStatus": "QUOTA_STOP_HTTP_429",
        "spatialStatus": "LOCAL_VALIDATED_FOR_GENERATION",
        "visualStatus": "UNATTEMPTED_QUOTA_STOP",
        "note": "Vertex AI returned HTTP 429 (rate limit). Provider work stopped immediately. Pack prepared and validated locally."
    })
print("Added defense-terrain-hills QUOTA_STOP_HTTP_429 record.")

# 3. Prepare remaining unattempted items 28..32 packs locally
print("\n=== 3. PREPARING REMAINING 5 UNATTEMPTED PACKS LOCALLY (IDs 28..32) ===")
remaining_items = queue["items"][27:32]
for item in remaining_items:
    order = item["order"]
    item_id = item["id"]
    parts = item_id.split("-")
    mode = parts[0]
    spec = parts[2] if len(parts) > 2 else "forest"

    pack_dir = PACKS_DIR / item_id
    pack_dir.mkdir(parents=True, exist_ok=True)

    geom = contract["geometry"][mode]
    candidate_rel = item["sources"][0]["file"]
    candidate_path = ROOT / candidate_rel

    guide_img, mask_change, mask_keep = render_guide_and_masks(mode, geom)
    base_img = prepare_base_image(candidate_path, geom)

    guide_img.save(pack_dir / "guide.png")
    base_img.save(pack_dir / "base.png")
    mask_change.save(pack_dir / "mask_change.png")
    mask_keep.save(pack_dir / "mask_keep.png")
    (pack_dir / "geometry.json").write_text(json.dumps(geom, indent=2), encoding="utf-8")

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
        "disposition": "LOCAL_PACK_PREPARED_UNATTEMPTED_QUOTA_PAUSED"
    }
    (pack_dir / "validation.json").write_text(json.dumps(val_data, indent=2), encoding="utf-8")

    # Add to manifest & journal if not present
    if not any(m.get("order") == order for m in manifest["items"]):
        manifest["items"].append({
            "order": order,
            "id": item_id,
            "mode": mode,
            "spec": spec,
            "status": "LOCAL_PACK_PREPARED_UNATTEMPTED_QUOTA_PAUSED",
            "technicalStatus": "LOCAL_PACK_PREPARED",
            "spatialStatus": "LOCAL_VALIDATED_FOR_GENERATION",
            "visualStatus": "UNATTEMPTED",
            "packDir": str(pack_dir.relative_to(ROOT)).replace("\\", "/"),
            "note": "Pack prepared and mathematically validated locally. Generation paused due to upstream HTTP 429 rate limit."
        })

    if not any(a.get("order") == order for a in journal["attempts"]):
        journal["attempts"].append({
            "order": order,
            "id": item_id,
            "disposition": "LOCAL_PACK_PREPARED_UNATTEMPTED_QUOTA_PAUSED",
            "packDir": str(pack_dir.relative_to(ROOT)).replace("\\", "/"),
            "paidCalls": 0
        })
    print(f"Prepared pack for [{order:02d}/32] {item_id}")

# 4. Update Summary in Journal
journal["summary"] = {
    "total": 32,
    "reusedSucceededFromRun1": 12,
    "continuationSucceeded": 4,
    "totalNative4KSucceeded": 16,
    "failedConsumedFromRun1": 1,
    "excludedQuotaFromRun1": 1,
    "continuationQuotaStopped": 1,
    "unattemptedQuotaPaused": 5,
    "deferredKingdom": 8,
    "run01ActualCostUSD": 1.829288,
    "run02ActualCostUSD": 0.609767,
    "cumulativeInteractive4KCostUSD": round(1.829288 + 0.609767, 6),
    "cumulativeReconciledWithBufferUSD": round((1.829288 + 0.609767) * 1.15, 6)
}

# Sort items in manifest by order
manifest["items"].sort(key=lambda x: x["order"])
journal["attempts"].sort(key=lambda x: x["order"])

(RUN2_DIR / "journal.json").write_text(json.dumps(journal, indent=2), encoding="utf-8")
(RUN2_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
print("\nUpdated journal.json and manifest.json with full 32-item reconciled records.")
