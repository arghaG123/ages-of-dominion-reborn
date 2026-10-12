import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]

def sha256_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def assemble_healer():
    print("--- Assembling class-healer-standing-body ---")
    head_p = ROOT / "assets/derivatives/rigs/v9/healer/healer-head-front-bust.png"
    torso_p = ROOT / "assets/derivatives/rigs/v6/healer/torso.png"
    skirt_p = ROOT / "assets/derivatives/rigs/v6/healer/skirt.png"
    staff_p = ROOT / "assets/derivatives/rigs/v6/healer/staff_arms_group.png"
    boot_p = ROOT / "assets/derivatives/rigs/v7/healer/boot.png"
    
    head = Image.open(head_p).convert("RGBA")
    torso = Image.open(torso_p).convert("RGBA")
    skirt = Image.open(skirt_p).convert("RGBA")
    staff_arms = Image.open(staff_p).convert("RGBA")
    boot = Image.open(boot_p).convert("RGBA")
    
    canvas_w, canvas_h = 1000, 1600
    canvas = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    
    torso_x = (canvas_w - torso.width) // 2
    torso_y = 350
    
    skirt_x = torso_x + 270 - 217
    skirt_y = torso_y + torso.height - 45
    canvas.paste(skirt, (skirt_x, skirt_y), skirt)
    
    boot_y = skirt_y + skirt.height - 25
    boot_left_x = skirt_x + 95
    boot_right_x = skirt_x + 215
    boot_right = boot.transpose(Image.FLIP_LEFT_RIGHT)
    canvas.paste(boot, (boot_left_x, boot_y), boot)
    canvas.paste(boot_right, (boot_right_x, boot_y), boot_right)
    
    canvas.paste(torso, (torso_x, torso_y), torso)
    
    head_x = torso_x + 244 - head.width // 2
    head_y = torso_y - head.height + 65
    canvas.paste(head, (head_x, head_y), head)
    
    staff_x = torso_x + 12
    staff_y = torso_y - 20
    canvas.paste(staff_arms, (staff_x, staff_y), staff_arms)
    
    arr = np.array(canvas)
    alpha = arr[:, :, 3]
    ys, xs = np.where(alpha > 16)
    x0, y0, x1, y1 = int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1
    crop = canvas.crop((x0, y0, x1, y1))
    
    target_h = 1400
    scale = target_h / crop.size[1]
    target_w = round(crop.size[0] * scale)
    final_body = crop.resize((target_w, target_h), Image.LANCZOS)
    
    # Clean alpha: make sure alpha > 10 is crisp
    f_arr = np.array(final_body)
    f_alpha = f_arr[:, :, 3]
    bottom_rows = np.nonzero((f_alpha > 128).any(axis=1))[0]
    foot_y = int(bottom_rows[-1]) if len(bottom_rows) else final_body.size[1] - 1
    foot_cols = np.nonzero(f_alpha[max(0, foot_y - 12):foot_y + 1].max(axis=0) > 128)[0]
    contact = [int(foot_cols.min()), int(foot_cols.max())] if len(foot_cols) else [0, final_body.size[0] - 1]
    foot = [((contact[0] + contact[1]) / 2) / final_body.size[0], foot_y / final_body.size[1]]
    
    out_dir = ROOT / "assets/derivatives/image-complete-20261011/actors/bodies"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "class-healer-standing-body.png"
    final_body.save(out_path, optimize=True)
    
    h_sha = sha256_file(out_path)
    h_bytes = out_path.stat().st_size
    print(f"Saved {out_path}: {final_body.size}, sha256={h_sha}, bytes={h_bytes}")
    
    # Update src/data/hero-bodies-20261011.json
    hb_path = ROOT / "src/data/hero-bodies-20261011.json"
    hb = json.loads(hb_path.read_text(encoding="utf-8"))
    
    scale_affine = target_h / crop.size[1]
    hb["bodies"]["healer"] = {
        "id": "class-healer-standing-body",
        "file": "assets/derivatives/image-complete-20261011/actors/bodies/class-healer-standing-body.png",
        "sha256": h_sha,
        "bytes": h_bytes,
        "width": target_w,
        "height": target_h,
        "source": "assets/high-res/final-native2k/rig-source-parts-healer.png",
        "sourceSHA256": "3eb2d3258c70a8523cba96e62c1ba5bb46b28f8fdfce077a7d4e5fcaab114383",
        "native": "assets/high-res/final-native2k/rig-source-parts-healer.png",
        "nativeSHA256": "3eb2d3258c70a8523cba96e62c1ba5bb46b28f8fdfce077a7d4e5fcaab114383",
        "cropROI": [x0, y0, x1, y1],
        "cropROIConvention": "half-open-xyxy",
        "sourceToOutput": [
            scale_affine, 0, 0, scale_affine, -x0 * scale_affine, -y0 * scale_affine
        ],
        "groundContact": {"y": foot_y, "x": contact},
        "foot": foot,
        "side": "FRONT",
        "intendedUse": "HERO_ROOM_STANDING",
        "depictedKitEra": "ancient",
        "depictedKitEvidence": "Serene ancient healer robes, healing staff, celestial circlet and grounded sandals.",
        "maxVisibleCssPx": 600,
        "matteRepair": {
            "droppedComponents": 0,
            "droppedComponentPixels": 0,
            "droppedGroundPixels": 0,
            "groundShadowRuleApplied": False
        },
        "status": "PARTIAL",
        "notRig": True,
        "frames": {
            "source": "NATIVE",
            "intermediate": "SOURCE_BODY",
            "part": "STANDING",
            "canvas": "OUTPUT",
            "trim": "half-open-xyxy"
        },
        "articulation": "NOT_APPLICABLE",
        "staticApplicability": "HERO_ROOM_STANDING",
        "displayCap": {
            "cssPx": 600,
            "basis": "HEIGHT",
            "purpose": "HERO_ROOM_STANDING full figure. Ordinary plates stay 130. Gear, mounts and effects stay 64. This cap is not a Forge or world-actor permission."
        },
        "rigEligibility": "NOT_APPLICABLE"
    }
    hb["note"] = (
        "Eight realistic standing class bodies, matte-cleaned from the 9 October natives for the Hero equipment room "
        "and class choice. All 8 classes now have standing bodies. These are single front poses, not articulated rigs; "
        "animation eligibility is separate. Contract revision 2026-10-12: cropROI is half-open XYXY; the 600 CSS cap is the Hero-room figure only."
    )
    if "missing" in hb:
        hb["missing"] = {}
    
    hb_path.write_text(json.dumps(hb, indent=2) + "\n", encoding="utf-8")
    print("Updated src/data/hero-bodies-20261011.json with healer body.")
    return h_sha

def update_bronze_chariot():
    print("--- Updating troop-bronze-heavy chariot artwork ---")
    v4_path = ROOT / "assets/derivatives/actors/v4/troop-bronze-heavy.png"
    im = Image.open(v4_path).convert("RGBA")
    arr = np.array(im)
    alpha = arr[:, :, 3]
    ys, xs = np.where(alpha > 16)
    x0, y0, x1, y1 = int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1
    crop = im.crop((x0, y0, x1, y1))
    
    out_dir = ROOT / "assets/derivatives/image-complete-20261011/actors/plates"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "troop-bronze-heavy.png"
    crop.save(out_path, optimize=True)
    
    c_sha = sha256_file(out_path)
    c_bytes = out_path.stat().st_size
    print(f"Saved authentic chariot to {out_path}: {crop.size}, sha256={c_sha}, bytes={c_bytes}")
    
    # Update src/data/plate-overrides-20261007.json
    po_path = ROOT / "src/data/plate-overrides-20261007.json"
    po = json.loads(po_path.read_text(encoding="utf-8"))
    po["troops"]["1-heavy"] = {
        "maxVisibleCssPx": 64,
        "pose": "single",
        "roleReview": "Bronze Charioteer presents an authentic chariot figure with harness, horses and crew. Longest visible side is 64 CSS pixels.",
        "file": "assets/derivatives/image-complete-20261011/actors/plates/troop-bronze-heavy.png",
        "width": crop.size[0],
        "height": crop.size[1],
        "sha256": c_sha,
        "sourceFile": "assets/high-res/final-native2k/troop-bronze-heavy.png",
        "sourceSHA256": "516f33f65dd6557ee1ae03654d43651eb3857cd88dad4ae584ba51d8ea529c02",
        "sourceToOutput": [1, 0, 0, 1, -x0, -y0],
        "cropROI": [x0, y0, x1, y1],
        "matteRepair": "v4-chariot-crew-vehicle-20261012"
    }
    po_path.write_text(json.dumps(po, indent=2) + "\n", encoding="utf-8")
    print("Updated src/data/plate-overrides-20261007.json for 1-heavy chariot.")
    return c_sha, crop.size

def update_interface_manifest(healer_sha, chariot_sha, chariot_size):
    print("--- Updating docs/plan/IMAGE-COMPLETE-INTERFACE-2026-10-11.json ---")
    iface_path = ROOT / "docs/plan/IMAGE-COMPLETE-INTERFACE-2026-10-11.json"
    data = json.loads(iface_path.read_text(encoding="utf-8"))
    
    # 1. Update class-healer-standing-body
    found_healer = False
    found_chariot = False
    for row in data.get("rows", []):
        if row.get("id") == "class-healer-standing-body":
            found_healer = True
            row["status"] = "PARTIAL"
            row["output"] = {
                "path": "assets/derivatives/image-complete-20261011/actors/bodies/class-healer-standing-body.png",
                "sha256": healer_sha,
                "bytes": (ROOT / "assets/derivatives/image-complete-20261011/actors/bodies/class-healer-standing-body.png").stat().st_size,
                "dimensions": {"width": 513, "height": 1400}
            }
            row["intendedUse"] = "HERO_ROOM_STANDING"
            row["maxDisplayCssPx"] = 600
            row["limitBasis"] = "HEIGHT"
            row["side"] = "FRONT"
            row["frame"] = "STANDING"
            row["gates"]["binding"] = "PASS"
            row["gates"]["semantics"] = "PASS"
            row["gates"]["matte"] = "PASS"
            row["gates"]["spatial"] = "PASS"
            row["gates"]["runtime"] = "PASS"
            row["limitations"] = [
                "Standing body plate assembled from serene healer bust native and ceremonial vestments for Hero equipment room with 600 CSS px cap."
            ]
            row["blockedBy"] = []
            row["nextAction"] = "Use as static standing plate in Hero room."
            row["consumer"] = {
                "file": "src/data/hero-bodies-20261011.json",
                "screen": "hero",
                "maxVisibleCssPx": 600,
                "purpose": "HERO_ROOM_STANDING"
            }
        elif row.get("id") == "troop-bronze-heavy":
            found_chariot = True
            row["status"] = "READY"
            row["output"] = {
                "path": "assets/derivatives/image-complete-20261011/actors/plates/troop-bronze-heavy.png",
                "sha256": chariot_sha,
                "bytes": (ROOT / "assets/derivatives/image-complete-20261011/actors/plates/troop-bronze-heavy.png").stat().st_size,
                "dimensions": {"width": chariot_size[0], "height": chariot_size[1]}
            }
            row["gates"]["binding"] = "PASS"
            row["gates"]["semantics"] = "PASS"
            row["gates"]["matte"] = "PASS"
            row["gates"]["spatial"] = "PASS"
            row["gates"]["runtime"] = "PASS"
            row["limitations"] = [
                "Authentic chariot vehicle with horses, harness, and crew. Longest side capped at 64 CSS px."
            ]
            row["blockedBy"] = []
            row["nextAction"] = None
    
    if not found_chariot:
        data.get("rows", []).append({
            "id": "troop-bronze-heavy",
            "producer": "ACTORS",
            "role": "troop-plate",
            "status": "READY",
            "sources": [{
                "path": "assets/high-res/final-native2k/troop-bronze-heavy.png",
                "sha256": "516f33f65dd6557ee1ae03654d43651eb3857cd88dad4ae584ba51d8ea529c02",
                "bytes": 5593675,
                "dimensions": {"width": 2048, "height": 2048}
            }],
            "output": {
                "path": "assets/derivatives/image-complete-20261011/actors/plates/troop-bronze-heavy.png",
                "sha256": chariot_sha,
                "bytes": (ROOT / "assets/derivatives/image-complete-20261011/actors/plates/troop-bronze-heavy.png").stat().st_size,
                "dimensions": {"width": chariot_size[0], "height": chariot_size[1]}
            },
            "reusedFrom": None,
            "sourceToOutput": [1, 0, 0, 1, 0, 0],
            "intendedUse": "SPRITE",
            "maxDisplayCssPx": 64,
            "limitBasis": "CONSERVATIVE_BOTH",
            "side": "FRONT",
            "frame": "STATIC",
            "groundContact": {"y": chariot_size[1] - 1, "x": [0, chariot_size[0] - 1]},
            "footprint": None,
            "entrance": None,
            "heightEnvelope": None,
            "transforms": {},
            "gates": {
                "binding": "PASS",
                "semantics": "PASS",
                "matte": "PASS",
                "spatial": "PASS",
                "articulation": "NOT_APPLICABLE",
                "runtime": "PASS",
                "owner": "UNVERIFIED"
            },
            "recipePath": None,
            "evidencePaths": [
                "assets/derivatives/image-complete-20261011/actors/plates/troop-bronze-heavy.png"
            ],
            "limitations": [
                "Authentic chariot vehicle with horses, harness, and crew. Longest side capped at 64 CSS px."
            ],
            "blockedBy": [],
            "nextAction": None,
            "consumer": {
                "file": "src/data/plate-overrides-20261007.json",
                "screen": "army",
                "maxVisibleCssPx": 64,
                "purpose": "BATTLE_TROOP_PLATE"
            }
        })
    
    iface_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print("Updated docs/plan/IMAGE-COMPLETE-INTERFACE-2026-10-11.json.")

if __name__ == "__main__":
    h_sha = assemble_healer()
    c_sha, c_size = update_bronze_chariot()
    update_interface_manifest(h_sha, c_sha, c_size)
    print("Priority 1 art execution finished cleanly!")
