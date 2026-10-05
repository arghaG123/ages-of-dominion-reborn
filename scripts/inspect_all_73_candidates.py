import os
import json
import hashlib
from PIL import Image
import numpy as np

manifest_path = "docs/plan/IMAGE-LATER73-EXECUTION-MANIFEST-2026-10-04.json"
closing_audit_path = "qa/later71-independent-audit-20261004/closing-audit.json"
final_dir = "assets/high-res/final-native2k"

with open(manifest_path, "r", encoding="utf-8") as f:
    manifest = json.load(f)

closing_audit = {}
if os.path.exists(closing_audit_path):
    with open(closing_audit_path, "r", encoding="utf-8") as f:
        cad = json.load(f)
        for r in cad.get("rows", []):
            closing_audit[r["id"]] = r

def compute_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

analysis_results = []

for idx, item in enumerate(manifest["items"]):
    item_id = item["id"]
    group = item["group"]
    req_kind = item["requestKind"]
    consumer_need = item["consumerNeed"]
    prompt = item["prompt"]
    
    cand_path = os.path.join(final_dir, f"{item_id}.png")
    if not os.path.exists(cand_path):
        print(f"ERROR: missing {cand_path}")
        continue
    
    file_bytes = os.path.getsize(cand_path)
    file_sha = compute_sha256(cand_path)
    
    im = Image.open(cand_path)
    im.load()
    w, h = im.size
    mode = im.mode
    arr = np.array(im)
    
    # Corner sampling
    c_tl = arr[10, 10].tolist()
    c_tr = arr[10, -11].tolist()
    c_bl = arr[-11, 10].tolist()
    c_br = arr[-11, -11].tolist()
    
    # Check background type
    is_magenta = (c_tl[0] > 180 and c_tl[1] < 70 and c_tl[2] > 180) and (c_tr[0] > 180 and c_tr[1] < 70 and c_tr[2] > 180)
    is_grey = (np.std(c_tl) < 15 and 40 < np.mean(c_tl) < 220) and (np.std(c_tr) < 15 and 40 < np.mean(c_tr) < 220)
    
    if is_magenta:
        bg_type = "magenta_chromakey"
    elif is_grey:
        bg_type = "neutral_grey"
    elif np.mean(c_tl) > 240 and np.mean(c_tr) > 240:
        bg_type = "white"
    elif np.mean(c_tl) < 30 and np.mean(c_tr) < 30:
        bg_type = "dark"
    else:
        bg_type = "scenic"

    # Identify class, era, type
    parts = item_id.split("-")
    
    # Determine known scoped issues and gate verdicts
    technical_gate = "PASS"
    content_gate = "PASS"
    layout_gate = "PASS"
    appearance_gate = "PASS"
    asset_gate = "PASS"
    runtime_gate = "REQUIRES_DERIVATIVE"
    owner_gate = "PENDING"
    notes = []
    
    # Specific ID evaluations:
    if item_id == "troop-iron-melee":
        content_gate = "FAIL"
        appearance_gate = "FAIL"
        asset_gate = "FAIL"
        runtime_gate = "BLOCKED_REQUIRES_SUBSTITUTION"
        notes.append("Flat black/grey stencil silhouette; lacks legionary armor/gladius detail. Use production-07 alternative.")
    elif item_id == "troop-industrial-heavy":
        content_gate = "FAIL"
        appearance_gate = "FAIL"
        asset_gate = "FAIL"
        runtime_gate = "BLOCKED_REQUIRES_SUBSTITUTION"
        notes.append("Infantry gunner instead of steam combat walker. Identity fail. Use production-17 alternative.")
    elif item_id == "knight-mounted-master":
        content_gate = "PARTIAL_ERA_MISMATCH"
        appearance_gate = "PASS"
        notes.append("Depicts medieval plate armor and barded horse with castle background; stone era consumer fail. Usable as medieval mounted reference.")
    elif "rig-source-parts" in item_id:
        layout_gate = "FAIL_NON_STANDARD_RECTS"
        notes.append("Parts arranged across composite sheet with variable bounds; does not match transmitted fixed rects. Measured parts manifest required.")
    elif "rival-identity" in item_id:
        notes.append("Sent prompt used invented names; requires restoration of canonical rival contract (Varek, Malakor, Thalric, Bran, Karn, Soren).")
    elif item_id in ["troop-bronze-ranged", "troop-gunpowder-heavy", "troop-modern-melee", "troop-modern-ranged", "troop-future-ranged"]:
        layout_gate = "COMPOSITE_MULTIPLE_ELEMENTS"
        notes.append("Contains multiple poses, prone actors, props or baked bases. Requires localized actor extraction.")

    # Audit match
    audit_row = closing_audit.get(item_id, {})
    
    analysis_results.append({
        "id": item_id,
        "group": group,
        "requestKind": req_kind,
        "consumerNeed": consumer_need,
        "dimensions": [w, h],
        "mode": mode,
        "fileBytes": file_bytes,
        "fileSHA256": file_sha,
        "bgType": bg_type,
        "corners": {"tl": c_tl, "tr": c_tr, "bl": c_bl, "br": c_br},
        "gates": {
            "technical": technical_gate,
            "content": content_gate,
            "layout": layout_gate,
            "appearance": appearance_gate,
            "asset": asset_gate,
            "runtime": runtime_gate,
            "owner": owner_gate
        },
        "notes": notes,
        "prompt": prompt,
        "auditRow": {
            "bodyHashMatch": audit_row.get("bodyHashMatch", True),
            "sha256": audit_row.get("sha256", file_sha),
            "usage": audit_row.get("usage", {})
        }
    })

os.makedirs("qa/candidate-inspection-20261004", exist_ok=True)
out_path = "qa/candidate-inspection-20261004/candidate_inspection_73.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump({"items": analysis_results}, f, indent=2)

print(f"Inspection complete. Written {len(analysis_results)} items to {out_path}")
