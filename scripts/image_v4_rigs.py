"""Re-identify rig crops into v4. Knight is the measured pilot.

Does not overwrite v3. Does not paint missing anatomy.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path("C:/dev/ages-of-dominion-reborn")
NATIVE = ROOT / "assets/high-res/final-native2k"
V3 = ROOT / "assets/derivatives/rigs/v3"
OUT = ROOT / "assets/derivatives/rigs/v4"
QA = ROOT / "qa/image-v4-repair-20261004/rigs"
OUT.mkdir(parents=True, exist_ok=True)
QA.mkdir(parents=True, exist_ok=True)

# old v3 part name -> actual painted content. Not a whole-limb substitute.
RELABEL = {
    "knight": {
        "torso_breastplate": ("head_helmet_second_view", "HEAD", "POSE_ALTERNATIVE", "The v3 torso crop is a helmet."),
        "shield_heater": ("torso_cuirass_and_fauld", "TORSO", "COMBINED_ASSEMBLY", "The v3 shield crop is the breastplate and fauld."),
        "boot_foot_pair": ("shield_heater", "SHIELD", "ACCESSORY", "The v3 boot-pair crop is a heater shield."),
    },
    "mage": {
        "hand_left": ("sleeve_segment_a", "SLEEVE", "NOT_A_HAND", "Painted sleeve, not a hand."),
        "hand_right": ("sleeve_segment_b", "SLEEVE", "NOT_A_HAND", "Painted sleeve, not a hand."),
        "boot_foot_left": ("sleeve_segment_c", "SLEEVE", "NOT_A_FOOT", "Painted sleeve, not a foot."),
        "boot_foot_right": ("sleeve_segment_d", "SLEEVE", "NOT_A_FOOT", "Painted sleeve, not a foot."),
    },
    "ranger": {
        "quiver_cloak": ("head_cowl_second_view", "HEAD", "POSE_ALTERNATIVE", "The v3 quiver crop is another head."),
        "arm_upper_left": ("quiver", "ACCESSORY", "ACCESSORY", "The v3 upper-arm crop is a quiver."),
    },
    "warlock": {
        "head_canonical_neutral": ("head_with_neighbours", "HEAD", "NEIGHBOURS_RETAINED", "Crop still contains expression-grid neighbours."),
        "head_variant_focused": ("head_with_neighbours_variant", "HEAD", "NEIGHBOURS_RETAINED", "Crop still contains neighbours."),
        "weapon_staff_sleeve": ("sheet_region", "SHEET_REGION", "NOT_A_WEAPON", "Crop is a sheet region, not an isolated staff."),
        "hand_focus_casting": ("book_or_bag", "ACCESSORY", "ACCESSORY", "Crop is a book or bag, not a casting hand."),
    },
    "necromancer": {
        "weapon_scythe": ("torso_pelvis_armor", "TORSO", "COMBINED_ASSEMBLY", "The v3 scythe crop is torso and pelvis armor."),
        "robes_lower": ("arms_holding_staff", "ARM_ASSEMBLY", "COMBINED_ASSEMBLY", "The v3 lower-robe crop is arms holding a staff."),
    },
    "barbarian": {
        "head_horned_helm": ("lower_garment", "GARMENT", "NOT_A_HEAD", "The v3 head crop is a garment."),
        "weapon_great_axe": ("head_view_a", "HEAD", "POSE_ALTERNATIVE", "The v3 axe crop is a head view."),
        "arm_left": ("head_view_b", "HEAD", "POSE_ALTERNATIVE", "The v3 arm crop is a head view."),
        "arm_right": ("head_view_c", "HEAD", "POSE_ALTERNATIVE", "The v3 arm crop is a head view."),
        "boot_foot_left": ("hand_a", "HAND", "NOT_A_BOOT", "The v3 boot crop is a hand."),
        "boot_foot_right": ("hand_b", "HAND", "NOT_A_BOOT", "The v3 boot crop is a hand."),
    },
    "paladin": {
        "shield_sun_heraldic": ("torso_pelvis", "TORSO", "COMBINED_ASSEMBLY", "The v3 shield crop is torso and pelvis."),
        "pauldron_right": ("forearm_hand", "ARM_LOWER", "COMBINED_ASSEMBLY", "The v3 pauldron crop is a forearm and hand."),
        "thigh_right": ("sole_detail", "SOLE_DETAIL", "NOT_A_THIGH", "A sole detail, not a thigh."),
        "greave_boot_left": ("shield", "SHIELD", "ACCESSORY", "The v3 left greave crop is the shield."),
    },
    "healer": {
        "torso_bodice": ("skirt", "GARMENT", "NOT_A_TORSO", "The v3 torso crop is a skirt."),
        "arm_upper_right": ("backpack", "ACCESSORY", "ACCESSORY", "The v3 right-arm crop is a backpack."),
        "skirt_robes_lower": ("staff_arms_group", "ARM_ASSEMBLY", "COMBINED_ASSEMBLY", "Grouped arms holding a staff, not a skirt."),
        "weapon_holy_staff": ("arm", "ARM", "NOT_A_STAFF", "The v3 staff crop is an arm."),
    },
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def alpha_of(im: np.ndarray) -> np.ndarray:
    r, g, b = [im[:, :, i].astype(np.int16) for i in range(3)]
    if r[4, 4] > g[4, 4] + 40 and b[4, 4] > g[4, 4] + 40:
        return ~((r > g + 28) & (b > g + 28) & (np.abs(r - b) < 60))
    border = np.median(np.stack([im[4, 4], im[4, -5], im[-5, 4]]), axis=0)
    dist = np.sqrt(((im.astype(np.float32) - border) ** 2).sum(axis=2))
    return dist > 22


def save_part(im, mask, box, dest: Path) -> dict:
    x, y, w, h = box
    crop = im[y:y + h, x:x + w]
    m = mask[y:y + h, x:x + w]
    rgba = np.dstack([crop, np.where(m, 255, 0).astype(np.uint8)])
    Image.fromarray(rgba, "RGBA").save(dest)
    return {"sha256": sha256_file(dest), "dimensions": [int(w), int(h)], "mode": "RGBA"}


def knight_pilot(rows: list) -> None:
    im = np.array(Image.open(NATIVE / "rig-source-parts-knight.png").convert("RGB"))
    fg = alpha_of(im).astype(np.uint8)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(fg, 8)
    dest_dir = OUT / "knight"
    dest_dir.mkdir(parents=True, exist_ok=True)
    parts = []
    for i in range(1, n):
        x, y, w, h, area = [int(v) for v in stats[i]]
        if area < 2500 or w < 40 or h < 40:
            continue
        kind = "DISCRETE_PAINTED_PIECE"
        if area > 180000:
            kind = "COMBINED_ASSEMBLY_NOT_ONE_LIMB"
        name = f"piece_{x}_{y}"
        role = "UNCLASSIFIED_PAINTED_REGION"
        # Stable names for the separated pieces used by the pilot chain.
        if 1080 < x < 1200 and 1050 < y < 1250 and h > 200:
            name, role = "thigh_plate_left", "LEG_UPPER"
        elif 1080 < x < 1250 and 1500 < y < 1750 and h > 180:
            name, role = "greave_left", "LEG_LOWER"
        elif 1100 < x < 1300 and 1800 < y < 2000:
            name, role = "sabaton_left", "FOOT"
        elif 60 < x < 200 and 40 < y < 120 and h > 250:
            name, role = "helmet_front_mail", "HEAD"
        elif 1300 < x < 1500 and y < 120 and h > 600:
            name, role = "cuirass_fauld_assembly", "TORSO"
            kind = "COMBINED_ASSEMBLY_NOT_ONE_LIMB"
        path = dest_dir / f"{name}.png"
        if path.exists() and name.startswith("piece_"):
            path = dest_dir / f"{name}_{i}.png"
        meta = save_part(im, lab == i, (x, y, w, h), path)
        parts.append({
            "partName": path.stem,
            "semanticRole": role,
            "countAsWholeLimb": role in {"LEG_UPPER", "LEG_LOWER", "FOOT", "HEAD"} and kind == "DISCRETE_PAINTED_PIECE",
            "assemblyKind": kind,
            "handedness": "LEFT" if "left" in name else "CENTER",
            "parentPart": "thigh_plate_left" if name == "greave_left" else ("greave_left" if name == "sabaton_left" else None),
            "sourceBBox": [x, y, x + w - 1, y + h - 1],
            "derivativePath": str(path.relative_to(ROOT)).replace("\\", "/"),
            **meta,
            "rotationStatus": "NOT_THIS_PAIR",
        })
    chain = rotation_pilot(dest_dir, parts)
    rows.append({
        "classId": "knight",
        "role": "PILOT",
        "source": "assets/high-res/final-native2k/rig-source-parts-knight.png",
        "sourceSHA256": sha256_file(NATIVE / "rig-source-parts-knight.png"),
        "parts": parts,
        "rotationPilot": chain,
        "note": "Separated by magenta-family connectivity. Large touching groups stay combined assemblies. Names are painted-content names.",
    })


def rotation_pilot(dest_dir: Path, parts: list) -> dict:
    by = {p["partName"]: p for p in parts}
    parent_name, child_name = "thigh_plate_left", "greave_left"
    if parent_name not in by or child_name not in by:
        return {"status": "UNVERIFIED", "reason": "Pilot thigh/greave pair was not both recovered as separate parts."}
    parent = np.array(Image.open(ROOT / by[parent_name]["derivativePath"]).convert("RGBA"))
    child = np.array(Image.open(ROOT / by[child_name]["derivativePath"]).convert("RGBA"))
    overlays = {}
    measures = {}
    for angle in (0, -25, 25):
        canvas, stats = place_pair(parent, child, angle)
        rel = QA / f"knight_thigh_greave_{angle}.png"
        Image.fromarray(canvas, "RGBA").save(rel)
        overlays[str(angle)] = {"path": str(rel.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256_file(rel), **stats}
        measures[str(angle)] = stats
    # A painted socket would overlap at the shared edge. Zero overlap is a failed proof.
    meaningful = all(measures[k]["overlapPx"] > 40 for k in measures)
    status = (
        "UNVERIFIED_VIRTUAL_PLACEMENT_NOT_A_PAINTED_SOCKET"
        if meaningful else "FAIL_NO_PAINTED_OVERLAP"
    )
    for p in parts:
        if p["partName"] in (parent_name, child_name):
            p["rotationStatus"] = status
    return {
        "parent": parent_name,
        "child": child_name,
        "anglesDeg": [-25, 0, 25],
        "limitsDeg": [-25, 25],
        "status": status,
        "pivots": "virtual placement at parent bottom-center and child top-center; not a painted socket",
        "overlays": overlays,
        "runtimeBinding": "UNVERIFIED_CODE_OWNS_LIVE_MOTION",
    }


def place_pair(parent: np.ndarray, child: np.ndarray, angle: float):
    """Nearest-neighbour placement for measurement. Source files are not rewritten."""
    pa = parent[:, :, 3] > 16
    ca = child[:, :, 3] > 16
    pys, pxs = np.where(pa)
    cys, cxs = np.where(ca)
    if len(pys) == 0 or len(cys) == 0:
        return parent, {"overlapPx": 0, "holePx": 0, "clippingPx": 0, "status": "EMPTY"}
    parent_joint = (int(np.median(pxs[pys >= pys.max() - 6])), int(pys.max()))
    child_joint = (int(np.median(cxs[cys <= cys.min() + 6])), int(cys.min()))
    M = cv2.getRotationMatrix2D((float(child_joint[0]), float(child_joint[1])), angle, 1.0)
    rotated = cv2.warpAffine(
        child, M, (child.shape[1], child.shape[0]),
        flags=cv2.INTER_NEAREST, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0),
    )
    ph, pw = parent.shape[:2]
    ch, cw = rotated.shape[:2]
    canvas = np.zeros((ph + ch, pw + cw, 4), np.uint8)
    ox, oy = cw // 2, ch // 2
    canvas[oy:oy + ph, ox:ox + pw] = parent
    dest_x = ox + parent_joint[0] - child_joint[0]
    dest_y = oy + parent_joint[1] - child_joint[1]
    parent_m = np.zeros(canvas.shape[:2], bool)
    child_m = np.zeros(canvas.shape[:2], bool)
    parent_m[oy:oy + ph, ox:ox + pw] = pa
    x0, y0 = max(0, dest_x), max(0, dest_y)
    x1, y1 = min(canvas.shape[1], dest_x + cw), min(canvas.shape[0], dest_y + ch)
    if x1 > x0 and y1 > y0:
        src = rotated[y0 - dest_y:y1 - dest_y, x0 - dest_x:x1 - dest_x]
        child_m[y0:y1, x0:x1] = src[:, :, 3] > 16
        region = canvas[y0:y1, x0:x1]
        use = src[:, :, 3:4] > 16
        region[:] = np.where(use, src, region)
    overlap = int((parent_m & child_m).sum())
    # Hole: parent pixels along the bottom edge with no child pixel within 6px.
    bottom = np.zeros_like(parent_m)
    bottom[oy + pys.max() - 4: oy + pys.max() + 1, ox:ox + pw] = parent_m[oy + pys.max() - 4: oy + pys.max() + 1, ox:ox + pw]
    near_child = cv2.dilate(child_m.astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool)
    hole = int((bottom & ~near_child).sum())
    parent_box = parent_m.copy()
    parent_box = cv2.dilate(parent_box.astype(np.uint8), np.ones((9, 9), np.uint8)).astype(bool)
    clipping = int((child_m & ~parent_box).sum())
    return canvas, {
        "overlapPx": overlap,
        "holePx": hole,
        "clippingPx": clipping,
        "angleDeg": angle,
        "pivot": "virtual bottom-center of parent to top-center of child",
        "paintedSocket": False,
    }


def relabel_v3(rows: list) -> None:
    manifest = json.loads((V3 / "parts_manifest_v3.json").read_text(encoding="utf-8"))
    for class_id, mapping in RELABEL.items():
        class_rows = []
        for part in manifest[class_id]["parts"]:
            old = part["partName"]
            if old not in mapping and class_id == "knight":
                continue
            if old in mapping:
                new_name, role, kind, note = mapping[old]
            else:
                new_name, role, kind, note = old, part.get("semanticRole", "UNREVIEWED"), "UNREVIEWED_V3_CROP", "Not in the named failure list. Identity not re-proved."
            src = ROOT / part["derivativePath"]
            if not src.exists():
                class_rows.append({"partName": old, "status": "MISSING_V3_FILE", "path": part["derivativePath"]})
                continue
            dest_dir = OUT / class_id
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest = dest_dir / f"{new_name}.png"
            # Copy pixels; do not repaint. Knight pilot parts are separate files.
            if class_id == "knight":
                dest = dest_dir / f"v3crop_{new_name}.png"
            dest.write_bytes(src.read_bytes())
            class_rows.append({
                "v3Name": old,
                "partName": dest.stem,
                "semanticRole": role,
                "assemblyKind": kind,
                "countAsWholeLimb": False,
                "note": note,
                "derivativePath": str(dest.relative_to(ROOT)).replace("\\", "/"),
                "sha256": sha256_file(dest),
                "dimensions": part.get("derivativeDimensions"),
                "mode": "RGBA",
                "sourceBBox": part.get("cropBBoxSource"),
                "rotationStatus": "FAIL_NOT_A_ROTATED_PARENT_CHILD_TEST",
                "v3Claim": part.get("overlapValidationStatus"),
            })
        rows.append({"classId": class_id, "role": "RELABELLED_V3_CROPS", "parts": class_rows})


def main():
    rows = []
    knight_pilot(rows)
    relabel_v3(rows)
    report = {
        "version": "v4-rig-content-20261004",
        "rotationOverlapVerified": False,
        "allPartsDiscrete": False,
        "classes": rows,
    }
    path = ROOT / "qa/image-v4-repair-20261004/rigs-v4.json"
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("wrote", path)


if __name__ == "__main__":
    main()
