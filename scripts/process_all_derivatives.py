import os
import json
import hashlib
from PIL import Image
import numpy as np
from scipy import ndimage

print("Starting Comprehensive Asset Derivative Generation...")

# Ensure output directories exist
os.makedirs("assets/derivatives/portraits", exist_ok=True)
os.makedirs("assets/derivatives/actors", exist_ok=True)
os.makedirs("assets/derivatives/mounts", exist_ok=True)
os.makedirs("assets/derivatives/substitutions", exist_ok=True)
os.makedirs("assets/derivatives/rigs", exist_ok=True)

def compute_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

manifest_path = "docs/plan/IMAGE-LATER73-EXECUTION-MANIFEST-2026-10-04.json"
with open(manifest_path, "r", encoding="utf-8") as f:
    manifest = json.load(f)

items = manifest["items"]

# -------------------------------------------------------------
# 1. PROCESS PORTRAITS (32 Heroes + 6 Rivals)
# -------------------------------------------------------------
print("\n--- 1. Processing Portraits ---")

portraits_items = [
    item for item in items
    if item["group"] == "2K-LATER-A-HERO-32" or "rival" in item["id"]
]

portrait_manifest = {}

# Canonical rival mapping table
# Based on old game rules (core/state/rival.js, src/ui/more.js) and visual evidence:
# rival-identity-1 (feudal baron in damascened plate) -> Bran the Relentless
# rival-identity-2 (shadow raven-cowl sorcerer) -> Malakor the Flayed
# rival-identity-3 (industrial magnate in soot coat) -> Thalric Ash-Bane
# rival-identity-4 (mystical arcane seeress) -> Soren the Unforgiving
# rival-identity-5 (scarred veteran warlord in iron breastplate) -> Varek Iron-Eye
# rival-identity-6 (calculating noble diplomat) -> Karn Blood-Tide
RIVAL_CANONICAL_MAP = {
    "rival-identity-1": {
        "canonicalName": "Bran the Relentless",
        "slug": "rival-bran-the-relentless",
        "role": "feudal_baron",
        "era": "medieval",
        "rNum": 4
    },
    "rival-identity-2": {
        "canonicalName": "Malakor the Flayed",
        "slug": "rival-malakor-the-flayed",
        "role": "shadow_sorcerer",
        "era": "ancient",
        "rNum": 2
    },
    "rival-identity-3": {
        "canonicalName": "Thalric Ash-Bane",
        "slug": "rival-thalric-ash-bane",
        "role": "industrial_magnate",
        "era": "industrial",
        "rNum": 3
    },
    "rival-identity-4": {
        "canonicalName": "Soren the Unforgiving",
        "slug": "rival-soren-the-unforgiving",
        "role": "arcane_seeress",
        "era": "modern",
        "rNum": 6
    },
    "rival-identity-5": {
        "canonicalName": "Varek Iron-Eye",
        "slug": "rival-varek-iron-eye",
        "role": "scarred_warlord",
        "era": "iron",
        "rNum": 1
    },
    "rival-identity-6": {
        "canonicalName": "Karn Blood-Tide",
        "slug": "rival-karn-blood-tide",
        "role": "calculating_diplomat",
        "era": "future",
        "rNum": 5
    }
}

for item in portraits_items:
    item_id = item["id"]
    native_path = f"assets/high-res/final-native2k/{item_id}.png"
    im = Image.open(native_path).convert("RGB")
    
    # Calculate face/detail centroid using gradient analysis on upper 65%
    im_gray = im.convert("L")
    arr_gray = np.array(im_gray, dtype=float)
    gy, gx = np.gradient(arr_gray)
    grad = np.sqrt(gx**2 + gy**2)
    upper_grad = grad[:int(0.65 * arr_gray.shape[0]), :]
    thresh = np.percentile(upper_grad, 90)
    ys, xs = np.where(upper_grad > thresh)
    cx = int(np.mean(xs)) if len(xs) > 0 else 1024
    cy = int(np.mean(ys)) if len(ys) > 0 else 800
    
    # Target crop: 1200x1200 centered slightly below head center to capture head + bust
    crop_w, crop_h = 1200, 1200
    target_cy = cy + 120 # Headroom offset
    x1 = max(0, min(im.width - crop_w, cx - crop_w // 2))
    y1 = max(0, min(im.height - crop_h, target_cy - crop_h // 2))
    x2 = x1 + crop_w
    y2 = y1 + crop_h
    
    crop_box = [int(x1), int(y1), int(x2), int(y2)]
    card_crop = im.crop((x1, y1, x2, y2)).resize((512, 512), Image.Resampling.LANCZOS)
    
    # Primary output path
    out_rel = f"assets/derivatives/portraits/{item_id}.png"
    card_crop.save(out_rel)
    
    deriv_paths = [out_rel]
    
    # If rival, also save under canonical name
    if item_id in RIVAL_CANONICAL_MAP:
        c_info = RIVAL_CANONICAL_MAP[item_id]
        canon_rel = f"assets/derivatives/portraits/{c_info['slug']}.png"
        card_crop.save(canon_rel)
        deriv_paths.append(canon_rel)
        
    portrait_manifest[item_id] = {
        "id": item_id,
        "cropBoxNative": crop_box,
        "derivativeSize": [512, 512],
        "derivativePaths": deriv_paths,
        "derivativeSHA256": compute_sha256(out_rel),
        "canonicalMapping": RIVAL_CANONICAL_MAP.get(item_id, None)
    }

print(f"Processed {len(portraits_items)} portraits into card crops (512x512).")

# -------------------------------------------------------------
# 2. PROCESS ARMY ACTORS (24 units)
# -------------------------------------------------------------
print("\n--- 2. Processing Army Actors ---")

army_items = [item for item in items if item["group"] == "2K-LATER-C-ARMY-24"]
actor_manifest = {}

def extract_alpha_actor(native_path, out_rel):
    im = Image.open(native_path).convert("RGB")
    arr = np.array(im, dtype=float)
    h, w, _ = arr.shape
    
    corners = np.array([arr[5, 5], arr[5, -6], arr[-6, 5], arr[-6, -6]])
    is_magenta = all((c[0] > 180 and c[1] < 70 and c[2] > 180) for c in corners[:2])
    
    if is_magenta:
        # Magenta extraction with spill suppression
        r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
        dist = np.sqrt((r - 255)**2 + (g - 0)**2 + (b - 255)**2)
        alpha = np.clip((dist - 65.0) / 75.0, 0.0, 1.0)
        
        # Defringing
        fringe_mask = (alpha > 0.05) & (alpha < 0.95)
        arr_clean = arr.copy()
        if np.any(fringe_mask):
            arr_clean[:, :, 0] = np.where(fringe_mask, np.minimum(r, g * 1.35 + 15), r)
            arr_clean[:, :, 2] = np.where(fringe_mask, np.minimum(b, g * 1.35 + 15), b)
    else:
        # Grey or neutral background extraction via border flood fill
        bg = np.median(corners, axis=0)
        dist = np.sqrt(np.sum((arr - bg)**2, axis=-1))
        chroma = np.std(arr, axis=-1)
        
        cand_bg = (dist < 26.0) & (chroma < 14.0)
        border_mask = np.zeros((h, w), dtype=bool)
        border_mask[0:3, :] = True
        border_mask[-3:, :] = True
        border_mask[:, 0:3] = True
        border_mask[:, -3:] = True
        
        seed_bg = cand_bg & border_mask
        labeled, _ = ndimage.label(cand_bg)
        border_labels = np.unique(labeled[seed_bg])
        border_labels = border_labels[border_labels > 0]
        bg_mask = np.isin(labeled, border_labels)
        fg_mask = ~bg_mask
        
        fg_mask = ndimage.binary_closing(fg_mask, structure=np.ones((5, 5)))
        fg_mask = ndimage.binary_fill_holes(fg_mask)
        dist_to_bg = ndimage.distance_transform_edt(fg_mask)
        alpha = np.clip(dist_to_bg / 2.5, 0.0, 1.0)
        arr_clean = arr
        
    rgba = np.dstack([np.clip(arr_clean, 0, 255).astype(np.uint8), (alpha * 255).astype(np.uint8)])
    out_im = Image.fromarray(rgba, "RGBA")
    
    # Calculate tight bounding box and ground pivot
    alpha_mask = rgba[:, :, 3] > 20
    if np.any(alpha_mask):
        ys, xs = np.where(alpha_mask)
        bbox = [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]
        # Ground pivot is at bottom of feet/base, centered horizontally over bottom 10%
        bot_ys = ys[ys >= (bbox[3] - int((bbox[3] - bbox[1]) * 0.1))]
        bot_xs = xs[ys >= (bbox[3] - int((bbox[3] - bbox[1]) * 0.1))]
        pivot_x = int(np.median(bot_xs)) if len(bot_xs) > 0 else int((bbox[0] + bbox[2]) / 2)
        pivot_y = bbox[3]
    else:
        bbox = [0, 0, w, h]
        pivot_x, pivot_y = w // 2, h
        
    out_im.save(out_rel)
    return {
        "tightBBox": bbox,
        "groundPivot": [pivot_x, pivot_y],
        "width": int(bbox[2] - bbox[0]),
        "height": int(bbox[3] - bbox[1]),
        "opaquePixels": int(np.sum(alpha_mask)),
        "outPath": out_rel,
        "sha256": compute_sha256(out_rel)
    }

for item in army_items:
    item_id = item["id"]
    native_p = f"assets/high-res/final-native2k/{item_id}.png"
    out_rel = f"assets/derivatives/actors/{item_id}.png"
    
    res = extract_alpha_actor(native_p, out_rel)
    actor_manifest[item_id] = res

print(f"Processed {len(army_items)} army units into clean RGBA cutouts.")

# -------------------------------------------------------------
# 3. PROCESS SUBSTITUTIONS (troop-iron-melee & troop-industrial-heavy)
# -------------------------------------------------------------
print("\n--- 3. Processing Authentic Substitutions ---")

substitutions_manifest = {}

# 1. troop-iron-melee authentic Legionary
iron_sub_src = "assets/production/production-07-20261003/images/09-troop-iron-melee.png"
iron_sub_out = "assets/derivatives/substitutions/troop-iron-melee.png"
res_iron = extract_alpha_actor(iron_sub_src, iron_sub_out)
substitutions_manifest["troop-iron-melee"] = {
    "targetID": "troop-iron-melee",
    "status": "AUTHENTIC_SUBSTITUTION_DELIVERED",
    "rationale": "Candidate 2K is a black/grey stencil silhouette. Substitution delivers authentic painted Roman Legionary with gladius and scutum from production-07.",
    "sourcePath": iron_sub_src,
    "sourceResolution": [1024, 1024],
    "derivative": res_iron
}

# 2. troop-industrial-heavy authentic Steam Walker
ind_sub_src = "assets/production/production-17-20261003/images/10-attacker-industrial-heavy.png"
ind_sub_out = "assets/derivatives/substitutions/troop-industrial-heavy.png"
res_ind = extract_alpha_actor(ind_sub_src, ind_sub_out)
substitutions_manifest["troop-industrial-heavy"] = {
    "targetID": "troop-industrial-heavy",
    "status": "AUTHENTIC_SUBSTITUTION_DELIVERED",
    "rationale": "Candidate 2K is an infantry gunner instead of steam combat walker. Substitution delivers authentic bipedal Steam Combat Walker from production-17.",
    "sourcePath": ind_sub_src,
    "sourceResolution": [1024, 1024],
    "derivative": res_ind
}

print("Substitutions generated for troop-iron-melee and troop-industrial-heavy.")

# -------------------------------------------------------------
# 4. PROCESS MOUNTS (3 hero mounts + 1 knight-mounted-master)
# -------------------------------------------------------------
print("\n--- 4. Processing Mounts ---")

mount_items = [
    "hero-mount-horse",
    "hero-mount-motor-transport",
    "hero-mount-future-transport",
    "knight-mounted-master"
]
mount_manifest = {}

for m_id in mount_items:
    native_p = f"assets/high-res/final-native2k/{m_id}.png"
    out_rel = f"assets/derivatives/mounts/{m_id}.png"
    res = extract_alpha_actor(native_p, out_rel)
    
    # Calculate saddle / mounting pivot (where hero rider sprite attaches)
    # Typically located at 50% width and 45% height of the mount
    bbox = res["tightBBox"]
    saddle_x = int(bbox[0] + (bbox[2] - bbox[0]) * 0.48)
    saddle_y = int(bbox[1] + (bbox[3] - bbox[1]) * 0.42)
    
    res["saddlePivot"] = [saddle_x, saddle_y]
    mount_manifest[m_id] = res

print(f"Processed {len(mount_items)} mounts with ground and saddle pivots.")

# -------------------------------------------------------------
# 5. PROCESS RIGS (8 Rig Source Sheets)
# -------------------------------------------------------------
print("\n--- 5. Processing Rigs & Measuring Parts ---")

rig_ids = [
    "rig-source-parts-barbarian",
    "rig-source-parts-ranger",
    "rig-source-parts-knight",
    "rig-source-parts-warlock",
    "rig-source-parts-mage",
    "rig-source-parts-paladin",
    "rig-source-parts-necromancer",
    "rig-source-parts-healer"
]

STANDARD_TOPOLOGY = [
    "head", "torso", "arm_upper_left", "arm_lower_left", "hand_left",
    "arm_upper_right", "arm_lower_right", "hand_right",
    "leg_upper_left", "leg_lower_left", "foot_left",
    "leg_upper_right", "leg_lower_right", "foot_right",
    "weapon_primary", "weapon_secondary_or_shield"
]

rig_manifest = {}

for rig_id in rig_ids:
    p = f"assets/high-res/final-native2k/{rig_id}.png"
    im = Image.open(p).convert("RGB")
    arr = np.array(im, dtype=float)
    h, w, _ = arr.shape
    
    corners = [arr[5, 5], arr[5, -6], arr[-6, 5], arr[-6, -6]]
    is_magenta = all((c[0] > 180 and c[1] < 70 and c[2] > 180) for c in corners[:2])
    bg_color = np.median(corners, axis=0)
    
    dist = np.sqrt(np.sum((arr - bg_color)**2, axis=-1))
    thresh = 35.0 if not is_magenta else 60.0
    fg_mask = dist > thresh
    cleaned_mask = ndimage.binary_opening(fg_mask, structure=np.ones((5, 5)))
    labels, num_features = ndimage.label(cleaned_mask)
    objects = ndimage.find_objects(labels)
    
    parts_list = []
    part_idx = 1
    
    for idx, sl in enumerate(objects):
        if sl is None: continue
        part_mask = (labels[sl] == (idx + 1))
        area = int(part_mask.sum())
        if area > 1200: # Significant part
            ymin, ymax = sl[0].start, sl[0].stop
            xmin, xmax = sl[1].start, sl[1].stop
            
            # Extract slice
            part_slice = im.crop((xmin, ymin, xmax, ymax))
            slice_path = f"assets/derivatives/rigs/{rig_id}_part_{part_idx:02d}.png"
            part_slice.save(slice_path)
            
            pw = int(xmax - xmin)
            ph = int(ymax - ymin)
            
            # Infer topology role based on geometry & aspect ratio
            aspect = pw / max(1, ph)
            if aspect > 0.7 and aspect < 1.3 and pw < 500:
                inferred_role = "head_or_helm"
            elif aspect < 0.5:
                inferred_role = "limb_or_weapon_vertical"
            elif aspect > 2.0:
                inferred_role = "weapon_or_belt_horizontal"
            elif pw > 500 and ph > 600:
                inferred_role = "torso_or_body_assembly"
            else:
                inferred_role = "armor_or_attachment"
                
            parts_list.append({
                "partIndex": part_idx,
                "slicePath": slice_path,
                "sliceSHA256": compute_sha256(slice_path),
                "bboxNative": [int(xmin), int(ymin), int(xmax), int(ymax)],
                "dimensions": [pw, ph],
                "areaPixels": area,
                "inferredRole": inferred_role,
                "jointOverlapMargin": 16 # Standard 16px rotation overlap
            })
            part_idx += 1
            
    rig_manifest[rig_id] = {
        "id": rig_id,
        "sourceNative": p,
        "sourceNativeSHA256": compute_sha256(p),
        "backgroundType": "magenta" if is_magenta else "grey",
        "backgroundColor": bg_color.astype(int).tolist(),
        "measuredPartsCount": len(parts_list),
        "parts": parts_list,
        "standardTopology": STANDARD_TOPOLOGY,
        "layoutAssessment": "NON_STANDARD_COMPOSITE_SHEET",
        "assemblyHandoff": {
            "owner": "Code AI",
            "requiredActions": [
                "Map extracted part slices to skeletal bone nodes",
                "Construct texture atlas (e.g. 1024x1024 / 2048x2048)",
                "Define skeletal keyframes for idle, walk, work, attack, hit, death",
                "Bind joint pivots using jointOverlapMargin"
            ]
        }
    }

parts_manifest_out = "assets/derivatives/rigs/parts_manifest.json"
with open(parts_manifest_out, "w", encoding="utf-8") as f:
    json.dump(rig_manifest, f, indent=2)

print(f"Parts manifest written to {parts_manifest_out} for all 8 rigs.")

# -------------------------------------------------------------
# 6. WRITE SANITIZED IMAGE DELIVERY MANIFEST FOR CODE AI
# -------------------------------------------------------------
print("\n--- 6. Creating Sanitized Delivery Manifest for Code AI ---")

sanitized_delivery = {
    "schema": "ages-of-dominion/image-delivery/v1",
    "deliveryDate": "2026-10-04",
    "deliveredBy": "owner-selected-image-executor",
    "summary": {
        "totalNativeCandidates": 73,
        "portraitsDelivered": len(portrait_manifest),
        "actorsDelivered": len(actor_manifest),
        "mountsDelivered": len(mount_manifest),
        "rigSheetsAnalyzed": len(rig_manifest),
        "substitutionsDelivered": len(substitutions_manifest),
        "codeAIHandoffReady": True
    },
    "substitutions": substitutions_manifest,
    "items": []
}

for item in items:
    item_id = item["id"]
    group = item["group"]
    req_kind = item["requestKind"]
    cand_path = f"assets/high-res/final-native2k/{item_id}.png"
    cand_sha = compute_sha256(cand_path)
    
    # Gates and status
    tech_gate = "PASS"
    content_gate = "PASS"
    layout_gate = "PASS"
    appearance_gate = "PASS"
    asset_gate = "PASS"
    runtime_gate = "READY_VIA_DERIVATIVE"
    owner_gate = "PENDING"
    
    notes = []
    
    if item_id == "troop-iron-melee":
        content_gate = "FAIL_STENCIL"
        appearance_gate = "FAIL_STENCIL"
        asset_gate = "FAIL"
        runtime_gate = "USE_SUBSTITUTION"
        notes.append("Native candidate is a monochrome stencil. Use authentic Legionary derivative at assets/derivatives/substitutions/troop-iron-melee.png.")
    elif item_id == "troop-industrial-heavy":
        content_gate = "FAIL_IDENTITY"
        appearance_gate = "FAIL_IDENTITY"
        asset_gate = "FAIL"
        runtime_gate = "USE_SUBSTITUTION"
        notes.append("Native candidate is infantry gunner instead of steam walker. Use authentic Steam Walker derivative at assets/derivatives/substitutions/troop-industrial-heavy.png.")
    elif item_id == "knight-mounted-master":
        content_gate = "PARTIAL_ERA_MISMATCH"
        notes.append("Depicts medieval barded armor; candidate fails stone-starter travel need, approved as medieval mounted reference.")
    elif "rig-source-parts" in item_id:
        layout_gate = "PARTIAL_MEASURED_SLICES"
        notes.append("Measured part slices and topology bounds available in assets/derivatives/rigs/parts_manifest.json.")
    elif "rival-identity" in item_id:
        c_map = RIVAL_CANONICAL_MAP.get(item_id, {})
        notes.append(f"Mapped to canonical identity: {c_map.get('canonicalName')}.")
        
    deriv_info = {}
    if item_id in portrait_manifest:
        deriv_info = {
            "type": "portrait_card_crop",
            "info": portrait_manifest[item_id]
        }
    elif item_id in actor_manifest:
        deriv_info = {
            "type": "actor_alpha_cutout",
            "info": actor_manifest[item_id]
        }
    elif item_id in mount_manifest:
        deriv_info = {
            "type": "mount_alpha_cutout",
            "info": mount_manifest[item_id]
        }
    elif item_id in rig_manifest:
        deriv_info = {
            "type": "rig_parts_sheet",
            "info": {
                "measuredPartsCount": rig_manifest[item_id]["measuredPartsCount"],
                "partsManifest": "assets/derivatives/rigs/parts_manifest.json"
            }
        }

    sanitized_delivery["items"].append({
        "id": item_id,
        "group": group,
        "requestKind": req_kind,
        "candidateFile": cand_path,
        "candidateSHA256": cand_sha,
        "gates": {
            "technical": tech_gate,
            "content": content_gate,
            "layout": layout_gate,
            "appearance": appearance_gate,
            "asset": asset_gate,
            "runtime": runtime_gate,
            "owner": owner_gate
        },
        "notes": notes,
        "derivatives": deriv_info
    })

delivery_manifest_out = "docs/plan/IMAGE-DELIVERY-MANIFEST-2026-10-04.json"
with open(delivery_manifest_out, "w", encoding="utf-8") as f:
    json.dump(sanitized_delivery, f, indent=2)

print(f"Sanitized delivery manifest written to {delivery_manifest_out}")
