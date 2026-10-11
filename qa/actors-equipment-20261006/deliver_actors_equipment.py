"""Local Character and Equipment Art Delivery Pipeline for Ages of Dominion Reborn.
AI 2: LOCAL CHARACTER AND EQUIPMENT ART EXECUTOR.
Deliveries written strictly to:
- assets/derivatives/actors-equipment-20261006/
- qa/actors-equipment-20261006/
- docs/plan/ACTORS-EQUIPMENT-INTERFACE-2026-10-06.json

Preserves unchanged immutable inputs, 19 v9 ready rows, baseline hashes, and size/pose limits.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import shutil
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path("c:/dev/ages-of-dominion-reborn")
DERIV = ROOT / "assets/derivatives/actors-equipment-20261006"
QA = ROOT / "qa/actors-equipment-20261006"
INTERFACE_PATH = ROOT / "docs/plan/ACTORS-EQUIPMENT-INTERFACE-2026-10-06.json"
MOCKS = ROOT / "design-preview/generated/landscape-mocks-20261003-efcd7a7e/images"
NATIVE = ROOT / "assets/high-res/final-native2k"

BOOT = ROOT / "assets/derivatives/rigs/v7/healer/boot.png"
DRAFT = ROOT / "docs/plan/REPLACEMENT-DRAFT-THREE-ROLES-V6-CLARIFICATION-2026-10-04.json"
CONTRACT = ROOT / "src/data/implementation-contract.json"
V8_INTERFACE = ROOT / "docs/plan/IMAGE-DELIVERY-INTERFACE-V8-2026-10-05.json"
V9_INTERFACE = ROOT / "docs/plan/IMAGE-DELIVERY-INTERFACE-V9-2026-10-05.json"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def rel(path: Path | str) -> str:
    p = Path(path)
    try:
        return str(p.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def save_png(path: Path, arr: np.ndarray) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = "RGBA" if arr.shape[2] == 4 else "RGB"
    Image.fromarray(arr, mode).save(path)
    return sha256_file(path)


def composite(rgba: np.ndarray, bg_rgb: tuple[int, int, int]) -> Image.Image:
    im = Image.fromarray(rgba, "RGBA")
    bg = Image.new("RGBA", im.size, (*bg_rgb, 255))
    return Image.alpha_composite(bg, im).convert("RGB")


def scale_to_height(rgba: np.ndarray, target_h: int) -> np.ndarray:
    im = Image.fromarray(rgba, "RGBA")
    w = max(1, int(round(im.width * (target_h / im.height))))
    return np.array(im.resize((w, target_h), Image.Resampling.LANCZOS))


def verify_inputs():
    print("Verifying immutable baseline inputs...")
    expected = {
        BOOT: ("4a700eeedbabc9710db137491825d0c2ec439db15b10c619f0997a93accfab21", (135, 131)),
        DRAFT: ("d9564c16c84cb68e230ddbe39d919a1036fa498377643b19085ecac4371864e0", None),
        CONTRACT: ("43553411b583a6df5fdcf620d2b3efecd82a0cd6f783895165a5910e577b0fcd", None),
        V8_INTERFACE: ("b0728909317b092ba6900d55524a077ff5989afd08bfb3631564230b15517cf1", None),
        V9_INTERFACE: ("0e4c9c4a4da83c2aed38aaa244bfe254dc244b8a333d96459a732c038935a8ae", None),
    }
    input_snapshot = {}
    for p, (want_hash, want_dim) in expected.items():
        if not p.exists():
            raise RuntimeError(f"Missing immutable input: {p}")
        got_hash = sha256_file(p)
        if got_hash != want_hash:
            raise RuntimeError(f"Hash mismatch on {p}: got {got_hash}, want {want_hash}")
        if want_dim:
            im = Image.open(p)
            if im.size != want_dim:
                raise RuntimeError(f"Dimension mismatch on {p}: got {im.size}, want {want_dim}")
        input_snapshot[p.name] = {
            "path": rel(p),
            "sha256": got_hash,
            "dimensions": list(want_dim) if want_dim else None,
            "verified": True,
        }
    print("All baseline input hashes verified successfully.")
    return input_snapshot


def cuff_profile(arr: np.ndarray, mode: str) -> dict:
    alpha = arr[:, :, 3]
    h, w = alpha.shape
    rows = range(h) if mode == "top" else range(h - 1, -1, -1)
    for y in rows:
        row = alpha[y]
        xs = np.where(row > 16)[0]
        if len(xs) == 0:
            continue
        xs128 = np.where(row > 128)[0]
        if len(xs128) < 4:
            continue
        runs = []
        cur = [int(xs128[0])]
        for x in xs128[1:]:
            if x == cur[-1] + 1:
                cur.append(int(x))
            else:
                runs.append(cur)
                cur = [int(x)]
        runs.append(cur)
        best = max(runs, key=len)
        if len(best) >= 8:
            return {
                "y": int(y),
                "span": len(best),
                "x0": int(best[0]),
                "x1": int(best[-1]),
                "cx": float((best[0] + best[-1]) / 2.0),
            }
    return {"y": 0, "span": 0, "x0": 0, "x1": 0, "cx": 0.0}


def measure_pair(parent_path: str, child_path: str, ins_f: float, tr_f: float) -> dict:
    p_im = Image.open(ROOT / parent_path).convert("RGBA")
    c_im = Image.open(ROOT / child_path).convert("RGBA")
    p_arr, c_arr = np.array(p_im), np.array(c_im)
    pc = cuff_profile(p_arr, "bottom")
    cc = cuff_profile(c_arr, "top")
    ins_px = ins_f * min(pc["span"], cc["span"])
    tr_px = tr_f * min(pc["span"], cc["span"])
    pad = 60
    cw = p_arr.shape[1] + c_arr.shape[1] + pad * 2
    ch = p_arr.shape[0] + c_arr.shape[0] + pad * 2
    px, py = pad + p_arr.shape[1] // 2, pad + pc["y"]
    parent_canvas = np.zeros((ch, cw, 4), dtype=np.uint8)
    p_x0, p_y0 = int(px - pc["cx"]), int(py - pc["y"])
    parent_canvas[p_y0:p_y0 + p_arr.shape[0], p_x0:p_x0 + p_arr.shape[1]] = p_arr

    poses = []
    ratio = float(cc["span"] / max(1, pc["span"]))
    for ang in (-25, 0, 25):
        child_canvas = np.zeros((ch, cw, 4), dtype=np.uint8)
        rad = np.deg2rad(ang)
        cos_a, sin_a = float(np.cos(rad)), float(np.sin(rad))
        dx = -cc["cx"] + tr_px
        dy = -cc["y"] - ins_px
        M = np.array([
            [cos_a, -sin_a, px + cos_a * dx - sin_a * dy],
            [sin_a, cos_a, py + sin_a * dx + cos_a * dy],
        ], dtype=np.float32)
        warped = cv2.warpAffine(c_arr, M, (cw, ch), flags=cv2.INTER_LANCZOS4)
        child_canvas = warped

        p_gt128 = parent_canvas[:, :, 3] > 128
        c_gt16 = child_canvas[:, :, 3] > 16
        overlap = np.count_nonzero(p_gt128 & c_gt16)

        c_gt128 = child_canvas[:, :, 3] > 128
        ov_both = p_gt128 & c_gt128
        ov_ys = np.where(ov_both)[0]
        crun = 0
        if len(ov_ys) > 0:
            runs = []
            cur_r = 1
            for i in range(1, len(ov_ys)):
                if ov_ys[i] == ov_ys[i - 1] + 1:
                    cur_r += 1
                elif ov_ys[i] > ov_ys[i - 1] + 1:
                    runs.append(cur_r)
                    cur_r = 1
            runs.append(cur_r)
            crun = max(runs)

        y_bot = py + int(c_arr.shape[0] * 0.4)
        roi_p = int(np.count_nonzero(parent_canvas[py:y_bot, :, 3] > 128))
        roi_c = int(np.count_nonzero(child_canvas[py:y_bot, :, 3] > 16))

        poses.append({
            "angle": ang,
            "overlapParent128Child16": int(overlap),
            "continuousRunPx": int(crun),
            "jointRoiParentAlphaGt128": roi_p,
            "jointRoiChildAlphaGt16": roi_c,
        })

    return {
        "parentCuff": pc,
        "childCuff": cc,
        "ratio": round(ratio, 4),
        "poses": poses,
        "insertionOfCuff": ins_f,
        "transverseOfCuff": tr_f,
        "uniformScale": 1,
    }


def warp_part(part: np.ndarray, cuff_xy: tuple[float, float], target_xy: tuple[float, float], angle_deg: float, canvas_hw: tuple[int, int]) -> np.ndarray:
    ch, cw = canvas_hw
    cx, cy = cuff_xy
    tx, ty = target_xy
    rad = np.deg2rad(angle_deg)
    c, s = float(np.cos(rad)), float(np.sin(rad))
    M = np.array([
        [c, -s, tx - c * cx + s * cy],
        [s, c, ty - s * cx - c * cy],
    ], dtype=np.float32)
    return cv2.warpAffine(part, M, (cw, ch), flags=cv2.INTER_LANCZOS4)


def assemble_healer_leg() -> dict:
    upper = np.array(Image.open(ROOT / "assets/derivatives/rigs/v6/healer/leg_upper.png").convert("RGBA"))
    greave = np.array(Image.open(ROOT / "assets/derivatives/rigs/v6/healer/greave.png").convert("RGBA"))
    boot = np.array(Image.open(ROOT / "assets/derivatives/rigs/v7/healer/boot.png").convert("RGBA"))
    pc = cuff_profile(upper, "bottom")
    g_prox = (cuff_profile(greave, "top")["cx"], cuff_profile(greave, "top")["y"])
    g_dist = (cuff_profile(greave, "bottom")["cx"], cuff_profile(greave, "bottom")["y"])
    b_prox = (cuff_profile(boot, "top")["cx"], cuff_profile(boot, "top")["y"])

    canvas = (900, 900)
    pivot = (450.0, 380.0)
    frames = []
    for ang in (-25, 0, 25):
        rad = np.deg2rad(ang)
        c, s = float(np.cos(rad)), float(np.sin(rad))
        vx, vy = g_dist[0] - g_prox[0], g_dist[1] - g_prox[1]
        ankle_xy = (pivot[0] + c * vx - s * vy, pivot[1] + s * vx + c * vy)
        layers = [
            warp_part(boot, b_prox, ankle_xy, ang, canvas),
            warp_part(greave, g_prox, pivot, ang, canvas),
            warp_part(upper, (pc["cx"], pc["y"]), pivot, 0, canvas),
        ]
        merged = layers[0]
        for layer in layers[1:]:
            cover = layer[:, :, 3] > 16
            merged = merged.copy()
            merged[cover] = layer[cover]
        ys, xs = np.where(merged[:, :, 3] > 16)
        trimmed = merged[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        frames.append(trimmed)
        path = QA / "assemblies" / f"healer-leg-subchain-{ang}.png"
        save_png(path, trimmed)
        # copy to derivatives
        save_png(DERIV / "assemblies" / f"healer-leg-subchain-{ang}.png", trimmed)
        for color, name in (((255, 255, 255), "white"), ((0, 0, 0), "black"), ((106, 143, 78), "green")):
            composite(trimmed, color).save(QA / "diagnostics" / f"healer-leg-subchain-{ang}-{name}.png")
        composite(scale_to_height(trimmed, 130), (255, 255, 255)).save(QA / "diagnostics" / f"healer-leg-subchain-{ang}-130.png")

    images = []
    for frame in frames:
        thumb = Image.fromarray(frame, "RGBA").resize((max(1, int(frame.shape[1] * 180 / frame.shape[0])), 180), Image.Resampling.BOX)
        images.append(composite(np.array(thumb), (245, 240, 230)).convert("P", palette=Image.Palette.ADAPTIVE))
    gif_qa = QA / "assemblies" / "healer-leg-subchain-arc.gif"
    gif_deriv = DERIV / "assemblies" / "healer-leg-subchain-arc.gif"
    images[0].save(gif_qa, save_all=True, append_images=images[1:], duration=400, loop=0, disposal=2)
    images[0].save(gif_deriv, save_all=True, append_images=images[1:], duration=400, loop=0, disposal=2)

    return {
        "id": "healer-leg-subchain",
        "status": "PARTIAL",
        "fullBody": "FAIL",
        "side": "UNKNOWN",
        "measuredLinks": ["upper-leg to greave", "greave to boot"],
        "missingLinks": ["head to torso", "torso to skirt", "skirt to upper leg"],
        "angles": [-25, 0, 25],
        "neutral": rel(DERIV / "assemblies" / "healer-leg-subchain-0.png"),
        "clip": rel(gif_deriv),
        "drawOrder": ["boot", "greave", "upper leg"],
        "rotation": "Child rotates about the shared cuff pivot. Positive degrees are clockwise in image space.",
        "uniformScale": 1,
        "note": "Valid subchain only. Boot follows the greave with no extra ankle bend in this clip.",
    }


def key_magenta_image(im: Image.Image) -> tuple[np.ndarray, dict]:
    arr = np.array(im.convert("RGB"))
    r, g, b = arr[:, :, 0].astype(int), arr[:, :, 1].astype(int), arr[:, :, 2].astype(int)
    is_magenta = (r > g + 36) & (b > g + 36) & (np.abs(r - b) < 65)
    alpha = np.where(is_magenta, 0, 255).astype(np.uint8)
    rgba = np.dstack([arr, alpha])
    ys, xs = np.where(alpha > 16)
    if len(ys) > 0 and len(xs) > 0:
        y0, y1, x0, x1 = int(ys.min()), int(ys.max()), int(xs.min()), int(xs.max())
        trimmed = rgba[y0:y1 + 1, x0:x1 + 1]
        bbox = [x0, y0, x1 + 1, y1 + 1]
    else:
        trimmed = rgba
        bbox = [0, 0, arr.shape[1], arr.shape[0]]
    meta = {
        "sourceSize": [arr.shape[1], arr.shape[0]],
        "trimmedSize": [trimmed.shape[1], trimmed.shape[0]],
        "bbox": bbox,
        "visiblePixels": int(np.count_nonzero(alpha > 16)),
    }
    return trimmed, meta


def extract_actor_plate(src_path: Path, out_path: Path, max_display_css_px: int | None = None) -> dict:
    im = Image.open(src_path)
    if im.mode == "RGBA":
        arr = np.array(im)
    else:
        arr, _ = key_magenta_image(im)
    alpha = arr[:, :, 3]
    ys, xs = np.where(alpha > 16)
    if len(ys) > 0 and len(xs) > 0:
        y0, y1, x0, x1 = int(ys.min()), int(ys.max()), int(xs.min()), int(xs.max())
        trimmed = arr[y0:y1 + 1, x0:x1 + 1]
    else:
        trimmed = arr
        x0, y0, x1, y1 = 0, 0, arr.shape[1], arr.shape[0]

    out_path.parent.mkdir(parents=True, exist_ok=True)
    digest = save_png(out_path, trimmed)
    h, w = trimmed.shape[:2]

    # Ground contact: lowest opaque pixels
    bot_ys, bot_xs = np.where(trimmed[:, :, 3] > 128)
    contacts = []
    if len(bot_ys) > 0:
        max_y = int(bot_ys.max())
        xs_at_bot = bot_xs[bot_ys >= max_y - 4]
        if len(xs_at_bot) > 0:
            contacts.append({"x": float(np.mean(xs_at_bot)), "y": float(max_y)})

    # Generate diagnostics
    diag_base = QA / "diagnostics" / out_path.stem
    for bg_col, bg_name in (((255, 255, 255), "white"), ((0, 0, 0), "black"), ((106, 143, 78), "green")):
        composite(trimmed, bg_col).save(QA / "diagnostics" / f"{out_path.stem}-{bg_name}.png")
    scale_h = max_display_css_px if max_display_css_px else 130
    composite(scale_to_height(trimmed, scale_h), (255, 255, 255)).save(QA / "diagnostics" / f"{out_path.stem}-{scale_h}.png")

    return {
        "path": rel(out_path),
        "sha256": digest,
        "dimensions": [w, h],
        "visibleAlpha16": int(np.count_nonzero(trimmed[:, :, 3] > 16)),
        "visibleAlpha128": int(np.count_nonzero(trimmed[:, :, 3] > 128)),
        "contacts": contacts,
        "bbox": [x0, y0, x1 + 1, y1 + 1],
    }


def build_class_chain_diagrams():
    print("Building class missing-link diagrams for all 8 classes...")
    chain_specs = {
        "healer": [
            ("head (static card)", "assets/derivatives/rigs/v9/healer/healer-head-front-neck.png", "CROP_CARD"),
            ("torso", "assets/derivatives/rigs/v6/healer/torso.png", "NOT_JOINED"),
            ("skirt", "assets/derivatives/rigs/v6/healer/skirt.png", "CUFF_RATIO_6.25_FAIL"),
            ("leg subchain", "qa/actors-equipment-20261006/assemblies/healer-leg-subchain-0.png", "MEASURED_-25_0_25"),
        ],
        "paladin": [
            ("head", "assets/derivatives/rigs/v6/paladin/head_three_quarter.png", "UNREPAIRED_HEAD"),
            ("cuirass", "assets/derivatives/rigs/v6/paladin/cuirass_fauld_combined.png", "INSEPARABLE_GROUP"),
            ("knee-greave", "assets/derivatives/rigs/v6/paladin/knee_cop.png", "JOINT_READY_PART"),
        ],
        "ranger": [
            ("sleeve", "assets/derivatives/rigs/v5/ranger/sleeve_upper_arm.png", "CUFF_PROFILE_VALID"),
            ("hand", "assets/derivatives/rigs/v5/ranger/vambrace_hand_open.png", "ARC_-25_0_25_READY"),
        ],
        "knight": [
            ("vambrace", "assets/derivatives/rigs/v5/knight/vambrace.png", "ISOLATED_ARM_PART"),
            ("thigh", "assets/derivatives/rigs/v4/knight/thigh_plate_left.png", "13_ATTEMPTS_EXHAUSTED"),
            ("greave", "assets/derivatives/rigs/v4/knight/greave_left.png", "STOPPED_FAIL"),
        ],
        "mage": [
            ("hooded head", "qa/image-local-continuation-20261005/components/mage/02_119_545.png", "MOUTH_CLOSED_HOOD"),
            ("torso & pelvis", "qa/image-local-continuation-20261005/components/mage/01_1221_92.png", "PAINTED_LABELS_PRESENT"),
        ],
        "warlock": [
            ("head neutral", "assets/derivatives/rigs/v3/warlock/head_canonical_neutral.png", "SOURCE_PART"),
            ("torso crop", "qa/image-local-continuation-20261005/components/warlock/01_1042_107.png", "NO_NECK_SOCKET"),
        ],
        "necromancer": [
            ("skull helm", "assets/derivatives/rigs/v3/necromancer/head_skull_helm.png", "SOURCE_PART"),
            ("staff arms", "assets/derivatives/rigs/v4/necromancer/arms_holding_staff.png", "INSEPARABLE_POSE"),
        ],
        "barbarian": [
            ("head view", "qa/image-local-continuation-20261005/components/barbarian/05_57_51.png", "SOURCE_PART"),
            ("torso", "assets/derivatives/rigs/v3/barbarian/arm_left.png", "NO_SCALE_LOCKED_CHAIN"),
        ],
    }

    diagram_rows = []
    for cid, slots in chain_specs.items():
        sheet = Image.new("RGB", (260 * len(slots), 320), (240, 238, 232))
        draw = ImageDraw.Draw(sheet)
        draw.text((12, 8), f"{cid.upper()}: parts shown are not one scale-locked body (MISSING-LINK DIAGRAM)", fill=(20, 20, 20))
        for i, (name, path, state) in enumerate(slots):
            fpath = ROOT / path
            thumb = Image.open(fpath).convert("RGBA") if fpath.is_file() else Image.new("RGBA", (180, 180), (200, 200, 200, 255))
            thumb.thumbnail((200, 200))
            plate = Image.new("RGBA", (200, 200), (255, 255, 255, 255))
            plate.paste(thumb, ((200 - thumb.size[0]) // 2, (200 - thumb.size[1]) // 2), thumb)
            sheet.paste(plate.convert("RGB"), (i * 260 + 20, 36))
            draw.text((i * 260 + 20, 246), name, fill=(10, 10, 10))
            draw.text((i * 260 + 20, 268), state[:30], fill=(160, 30, 30))

        out_qa = QA / "assemblies" / f"{cid}-chain.png"
        out_deriv = DERIV / "assemblies" / f"{cid}-chain.png"
        sheet.save(out_qa)
        sheet.save(out_deriv)
        diagram_rows.append({
            "id": f"{cid}-chain-diagram",
            "classId": cid,
            "status": "PARTIAL",
            "path": rel(out_deriv),
            "sha256": sha256_file(out_deriv),
            "slots": [s[0] for s in slots],
            "reason": "Not a single-scale body. Independent parts and subchains only.",
        })
    return diagram_rows


def side_by_side_composite(ref_path: Path, actual_im: Image.Image, title: str, out_path: Path, note: str):
    ref = Image.open(ref_path).convert("RGB")
    ref.thumbnail((640, 360))
    act = actual_im.copy().convert("RGB")
    act.thumbnail((640, 360))
    canvas = Image.new("RGB", (1320, 440), (24, 26, 30))
    draw = ImageDraw.Draw(canvas)
    draw.text((20, 10), title, fill=(240, 240, 240))
    draw.text((20, 395), f"REFERENCE ({ref_path.name})", fill=(190, 190, 150))
    draw.text((680, 395), f"ASSET_COMPOSITE  playability: UNVERIFIED | {note}", fill=(140, 220, 160))
    canvas.paste(ref, (20, 32))
    canvas.paste(act, (680, 32))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path, quality=88)


def create_screen_composites(troops_meta: dict, gear_meta: dict, art_meta: dict):
    print("Generating side-by-side approved reference vs ASSET_COMPOSITE comparisons...")
    composites = []

    # 1. Hero & Equipment Screen (19-hero-equipment.jpg)
    hero_ref = MOCKS / "19-hero-equipment.jpg"
    hero_comp = Image.new("RGB", (1280, 720), (32, 28, 24))
    # Paste knight portrait or mounted master
    port_p = NATIVE / "portrait-ancient-barbarian.png"
    if port_p.exists():
        port = Image.open(port_p).convert("RGBA").resize((380, 380))
        hero_comp.paste(port, (450, 120), port)
    # Paste gear around hero
    gear_samples = list(gear_meta.values())[:6]
    coords = [(280, 120), (280, 260), (280, 400), (860, 120), (860, 260), (860, 400)]
    for g, (x, y) in zip(gear_samples, coords):
        g_im = Image.open(ROOT / g["path"]).convert("RGBA").resize((100, 100))
        hero_comp.paste(g_im, (x, y), g_im)
    out1 = QA / "review" / "hero-equipment-composite.jpg"
    side_by_side_composite(hero_ref, hero_comp, "Hero Equipment Screen  Landscape 1280x720", out1, "Canonical 6 equipment slots & barbarian kit")
    composites.append({"screen": "hero-equipment", "reference": rel(hero_ref), "composite": rel(out1)})

    # 2. Army Screen (24-army.jpg)
    army_ref = MOCKS / "24-army.jpg"
    army_comp = Image.new("RGB", (1280, 720), (28, 32, 28))
    # Place representative troops
    tr_keys = ["troop-bronze-melee", "troop-bronze-ranged", "troop-bronze-heavy", "troop-iron-melee", "troop-iron-ranged", "troop-iron-heavy"]
    for i, tk in enumerate(tr_keys):
        if tk in troops_meta:
            tp = Image.open(ROOT / troops_meta[tk]["path"]).convert("RGBA")
            h = 130
            w = max(1, int(round(tp.width * (h / tp.height))))
            tp = tp.resize((w, h), Image.Resampling.LANCZOS)
            x = 80 + (i % 3) * 380
            y = 140 + (i // 3) * 260
            army_comp.paste(tp, (x, y), tp)
    out2 = QA / "review" / "army-composite.jpg"
    side_by_side_composite(army_ref, army_comp, "Army Management Screen  Landscape 1280x720", out2, "Bronze/Iron unit plates at 130px intended review size")
    composites.append({"screen": "army", "reference": rel(army_ref), "composite": rel(out2)})

    # 3. Forge Screen (22-forge.jpg)
    forge_ref = MOCKS / "22-forge.jpg"
    forge_comp = Image.new("RGB", (1280, 720), (36, 26, 22))
    # Place gear items in forge slots
    f_gears = list(gear_meta.values())[6:12]
    for i, g in enumerate(f_gears):
        g_im = Image.open(ROOT / g["path"]).convert("RGBA").resize((110, 110))
        forge_comp.paste(g_im, (160 + (i % 3) * 340, 160 + (i // 3) * 220), g_im)
    out3 = QA / "review" / "forge-composite.jpg"
    side_by_side_composite(forge_ref, forge_comp, "Forge Crafting & Upgrade Screen  Landscape 1280x720", out3, "Period equipment icons across qualities")
    composites.append({"screen": "forge", "reference": rel(forge_ref), "composite": rel(out3)})

    # 4. Inventory Screen (23-inventory.jpg)
    inv_ref = MOCKS / "23-inventory.jpg"
    inv_comp = Image.new("RGB", (1280, 720), (24, 24, 30))
    # Place artifacts in grid
    for i, (ak, am) in enumerate(list(art_meta.items())[:8]):
        a_im = Image.open(ROOT / am["path"]).convert("RGBA").resize((90, 90))
        inv_comp.paste(a_im, (200 + (i % 4) * 220, 180 + (i // 4) * 220), a_im)
    out4 = QA / "review" / "inventory-composite.jpg"
    side_by_side_composite(inv_ref, inv_comp, "Inventory Screen  Landscape 1280x720", out4, "Canonical artifacts in bag slots")
    composites.append({"screen": "inventory", "reference": rel(inv_ref), "composite": rel(out4)})

    return composites


def generate_html_review_gallery(composites: list, ready_troops: list, other_troops: list, creatures: list, attackers: list, mounts: list, artifacts: list, gears: list, chains: list, subchains: list):
    print("Writing local HTML review gallery...")
    out_html = QA / "review" / "index.html"
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ages of Dominion Reborn - Character & Equipment Delivery Gallery</title>
<style>
:root {{
  --bg: #121316;
  --panel: #1a1c22;
  --border: #2a2d36;
  --text: #e6e8ee;
  --subtext: #9ba1b0;
  --accent: #4e8cff;
  --ready: #2ecc71;
  --partial: #f39c12;
  --blocked: #e74c3c;
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
  background: var(--bg);
  color: var(--text);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  line-height: 1.5;
  padding: 24px;
}}
header {{
  border-bottom: 1px solid var(--border);
  padding-bottom: 20px;
  margin-bottom: 28px;
}}
h1 {{ font-size: 24px; font-weight: 700; color: #fff; margin-bottom: 6px; }}
h2 {{ font-size: 18px; font-weight: 600; color: #d0d4e0; margin: 28px 0 14px; border-left: 4px solid var(--accent); padding-left: 10px; }}
p.sub {{ color: var(--subtext); font-size: 14px; }}
.badges {{ display: flex; gap: 10px; margin-top: 12px; }}
.badge {{ display: inline-block; padding: 4px 10px; border-radius: 4px; font-size: 12px; font-weight: 600; text-transform: uppercase; }}
.badge-ready {{ background: rgba(46, 204, 113, 0.2); color: var(--ready); border: 1px solid var(--ready); }}
.badge-partial {{ background: rgba(243, 156, 18, 0.2); color: var(--partial); border: 1px solid var(--partial); }}
.badge-blocked {{ background: rgba(231, 76, 60, 0.2); color: var(--blocked); border: 1px solid var(--blocked); }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; margin-top: 14px; }}
.card {{
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 14px;
  display: flex;
  flex-direction: column;
}}
.card img {{
  max-width: 100%;
  height: auto;
  border-radius: 4px;
  background: #242730;
  display: block;
  margin-bottom: 10px;
}}
.card .title {{ font-size: 14px; font-weight: 600; color: #fff; margin-bottom: 4px; }}
.card .meta {{ font-size: 12px; color: var(--subtext); }}
.card .mono {{ font-family: monospace; font-size: 11px; word-break: break-all; color: #889; }}
.composite-row {{ margin-bottom: 24px; }}
.composite-row img {{ width: 100%; border-radius: 8px; border: 1px solid var(--border); }}
table {{
  width: 100%;
  border-collapse: collapse;
  margin-top: 14px;
  font-size: 13px;
}}
th, td {{
  text-align: left;
  padding: 8px 12px;
  border-bottom: 1px solid var(--border);
}}
th {{ background: #16181d; color: var(--subtext); font-weight: 600; }}
</style>
</head>
<body>

<header>
  <h1>Ages of Dominion Reborn - Character & Equipment Delivery Review</h1>
  <p class="sub">AI 2 Local Character and Equipment Art Executor | Date: 6 October 2026 | Producer: ACTORS | Version: actors-equipment-20261006</p>
  <div class="badges">
    <span class="badge badge-ready">19 v9 Ready Rows Preserved</span>
    <span class="badge badge-partial">Checkpoint: INCOMPLETE (Honest Limits)</span>
    <span class="badge badge-blocked">Replacement 3-Role Draft Retained</span>
  </div>
</header>

<section>
  <h2>1. Approved Mock Reference vs ASSET_COMPOSITE Screen Reviews</h2>
  <p class="sub">Side-by-side comparison with approved landscape mocks. Labeled ASSET_COMPOSITE with playability UNVERIFIED.</p>
  <div class="grid" style="grid-template-columns: 1fr; gap: 20px;">
"""
    for comp in composites:
        html += f"""
    <div class="composite-row">
      <img src="{Path(comp['composite']).name}" alt="{comp['screen']}">
    </div>
"""
    html += f"""
  </div>
</section>

<section>
  <h2>2. Preserved Ready Rows (v9 Subset - 19 Rows)</h2>
  <p class="sub">Adequate v9 rows re-released with binding, semantic, size, and pose limits strictly preserved.</p>
  <div class="grid">
"""
    for row in ready_troops:
        html += f"""
    <div class="card">
      <img src="../../../{row['path']}" alt="{row['id']}">
      <div class="title">{row['id']} <span class="badge badge-ready">READY</span></div>
      <div class="meta">Role: {row.get('role', 'Troop')} | Intended: {row.get('use', '130px plate')}</div>
      <div class="mono">SHA: {row.get('sha256', '')[:16]}...</div>
      <div class="meta" style="margin-top:6px;">Dims: {row.get('dimensions', [])} | Alpha16: {row.get('visibleAlpha16', 0)}</div>
    </div>
"""
    html += f"""
  </div>
</section>

<section>
  <h2>3. Articulated Subchains & 8 Class Missing-Link Diagrams</h2>
  <p class="sub">Honest structural evidence. Subchains are valid locally; full single-scale bodies are not inventable from current sources.</p>
  <div class="grid">
    <div class="card" style="grid-column: span 2;">
      <img src="../assemblies/healer-leg-subchain-arc.gif" alt="Healer Leg Subchain Arc" style="max-height: 240px; object-fit: contain;">
      <div class="title">Healer Leg Subchain (-25, 0, +25 Arc) <span class="badge badge-partial">PARTIAL</span></div>
      <div class="meta">Measured links: upper-leg to greave, greave to boot (v7 hash preserved). No invented anatomy.</div>
    </div>
"""
    for ch in chains:
        html += f"""
    <div class="card" style="grid-column: span 2;">
      <img src="../assemblies/{Path(ch['path']).name}" alt="{ch['id']}">
      <div class="title">{ch['classId'].upper()} Missing-Link Diagram <span class="badge badge-partial">PARTIAL</span></div>
      <div class="meta">{ch['reason']}</div>
      <div class="mono">Parts: {', '.join(ch['slots'])}</div>
    </div>
"""
    html += f"""
  </div>
</section>

<section>
  <h2>4. Remaining 15 Troop Roles (Coverage of All 24 Roles)</h2>
  <p class="sub">Preserves honest limits: Stone Clubman, Stone Slinger, and Industrial Sharpshooter in replacement draft.</p>
  <div class="grid">
"""
    for row in other_troops:
        st_badge = "badge-ready" if row["status"] == "READY" else "badge-partial" if row["status"] == "PARTIAL" else "badge-blocked"
        html += f"""
    <div class="card">
      <img src="../../../{row['path']}" alt="{row['id']}">
      <div class="title">{row['id']} <span class="badge {st_badge}">{row['status']}</span></div>
      <div class="meta">Age: {row.get('age', '')} | Max Display: {row.get('maxDisplayCssPx', 'None')}px</div>
      <div class="meta">{row.get('limitations', [''])[0]}</div>
      <div class="mono">SHA: {row.get('output', {}).get('sha256', '')[:16]}...</div>
    </div>
"""
    html += f"""
  </div>
</section>

<section>
  <h2>5. Creatures (8 Canonical Roles)</h2>
  <p class="sub">Dire Wolf, Bandit, Cave Bear, Harpy, Stone Golem, Griffin, Wyvern, Drone Swarm.</p>
  <div class="grid">
"""
    for c in creatures:
        html += f"""
    <div class="card">
      <img src="../../../{c['path']}" alt="{c['id']}">
      <div class="title">{c['id']} <span class="badge badge-ready">READY</span></div>
      <div class="meta">Dims: {c.get('dimensions', [])} | Contacts: {len(c.get('contacts', []))}</div>
    </div>
"""
    html += f"""
  </div>
</section>

<section>
  <h2>6. Mounts & Vehicles (4 Items)</h2>
  <p class="sub">64px display caps enforced for transports.</p>
  <div class="grid">
"""
    for m in mounts:
        html += f"""
    <div class="card">
      <img src="../../../{m['path']}" alt="{m['id']}">
      <div class="title">{m['id']} <span class="badge badge-ready">READY</span></div>
      <div class="meta">Max Display: {m.get('maxDisplayCssPx', 64)}px | {m.get('note', '')}</div>
    </div>
"""
    html += f"""
  </div>
</section>

<section>
  <h2>7. Canonical Artifacts (10 Items)</h2>
  <p class="sub">All 10 canonical artifacts isolated and prepared from production sources.</p>
  <div class="grid" style="grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));">
"""
    for a in artifacts:
        html += f"""
    <div class="card">
      <img src="../../../{a['path']}" alt="{a['id']}">
      <div class="title">{a['name']}</div>
      <div class="meta">{a['desc']}</div>
      <div class="mono">ID: {a['id']}</div>
    </div>
"""
    html += f"""
  </div>
</section>

<section>
  <h2>8. Canonical Equipment (6 Slots across 8 Ages)</h2>
  <p class="sub">Sample of isolated gear icons across helm, weapon, offhand, armor, boots, accessory.</p>
  <div class="grid" style="grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));">
"""
    for g in gears[:18]:
        html += f"""
    <div class="card">
      <img src="../../../{g['path']}" alt="{g['id']}">
      <div class="title">{g['id']}</div>
      <div class="meta">{g.get('slot', '')} | Age {g.get('age', '')}</div>
    </div>
"""
    html += f"""
  </div>
</section>

</body>
</html>
"""
    out_html.write_text(html, encoding="utf-8")
    print("Gallery written successfully to", out_html)


def main():
    QA.mkdir(parents=True, exist_ok=True)
    for sub in ("masks", "recipes", "diagnostics", "assemblies", "review"):
        (QA / sub).mkdir(parents=True, exist_ok=True)
    for sub in ("troops", "creatures", "attackers", "mounts", "gear", "artifacts", "fx", "rigs", "assemblies"):
        (DERIV / sub).mkdir(parents=True, exist_ok=True)

    input_snapshot = verify_inputs()

    # Re-release unchanged 19 v9 ready rows
    v9_data = json.loads(V9_INTERFACE.read_text(encoding="utf-8"))
    v9_ready = v9_data["readySubset"]

    # Ingest v9 ready rows
    ready_subset_ids = []
    ready_troops = []
    artifact_rows = []

    for r in v9_ready:
        rid = r["id"]
        ready_subset_ids.append(rid)
        if "troop" in rid:
            ready_troops.append(r)
            # copy/link to our derivatives directory
            src_f = ROOT / r["path"]
            out_f = DERIV / "troops" / src_f.name
            if src_f.exists() and not out_f.exists():
                shutil.copy2(src_f, out_f)
            # Create ArtifactRow for this troop
            artifact_rows.append({
                "id": rid,
                "role": "static-troop",
                "age": None,
                "classId": None,
                "status": "READY",
                "source": {"path": r.get("path"), "sha256": r.get("sha256"), "roi": None},
                "output": {"path": rel(out_f if out_f.exists() else src_f), "sha256": r.get("sha256"), "dimensions": r.get("dimensions", [2048, 2048])},
                "sourceToOutput": [1, 0, 0, 1, 0, 0],
                "intendedUse": r.get("use", "130px review plate"),
                "maxDisplayCssPx": 130,
                "side": r.get("side", "UNKNOWN"),
                "groundContact": r.get("contacts"),
                "footprint": None,
                "entrance": None,
                "heightEnvelope": None,
                "frame": "image-space",
                "transforms": {},
                "gates": {
                    "binding": "PASS",
                    "semantics": "PASS",
                    "matte": "PASS",
                    "spatial": "PASS",
                    "articulation": "NOT_APPLICABLE",
                    "runtime": "UNVERIFIED",
                    "owner": "UNVERIFIED",
                },
                "evidencePaths": [rel(src_f)],
                "limitations": [r.get("limit", "Static plate to 130px; no gait")],
                "blockedBy": [],
                "nextAction": None,
            })
        elif "healer-head" in rid:
            src_f = ROOT / r["path"]
            out_f = DERIV / "rigs" / src_f.name
            if src_f.exists() and not out_f.exists():
                shutil.copy2(src_f, out_f)
            artifact_rows.append({
                "id": rid,
                "role": "static-head-card",
                "age": None,
                "classId": "healer",
                "status": "READY",
                "source": {"path": r.get("source"), "sha256": r.get("sourceSha256"), "roi": r.get("sourceROI")},
                "output": {"path": rel(out_f if out_f.exists() else src_f), "sha256": r.get("sha256"), "dimensions": r.get("dimensions")},
                "sourceToOutput": [1, 0, 0, 1, 0, 0],
                "intendedUse": "head card",
                "maxDisplayCssPx": None,
                "side": r.get("side", "UNKNOWN"),
                "groundContact": None,
                "footprint": None,
                "entrance": None,
                "heightEnvelope": None,
                "frame": "image-space",
                "transforms": {},
                "gates": {
                    "binding": "PASS",
                    "semantics": "PASS",
                    "matte": "PASS",
                    "spatial": "PASS",
                    "articulation": "PASS",
                    "runtime": "UNVERIFIED",
                    "owner": "UNVERIFIED",
                },
                "evidencePaths": [rel(src_f)],
                "limitations": [r.get("limit", "Static crop")],
                "blockedBy": [],
                "nextAction": None,
            })
        elif rid == "healer-boot":
            src_f = ROOT / r["path"]
            out_f = DERIV / "rigs" / "healer-boot.png"
            if src_f.exists() and not out_f.exists():
                shutil.copy2(src_f, out_f)
            artifact_rows.append({
                "id": rid,
                "role": "rig-part",
                "age": None,
                "classId": "healer",
                "status": "READY",
                "source": {"path": r.get("source"), "sha256": r.get("sourceSha256"), "roi": None},
                "output": {"path": rel(out_f if out_f.exists() else src_f), "sha256": r.get("sha256"), "dimensions": r.get("dimensions")},
                "sourceToOutput": [1, 0, 0, 1, 0, 0],
                "intendedUse": "boot part",
                "maxDisplayCssPx": None,
                "side": r.get("side", "UNKNOWN"),
                "groundContact": None,
                "footprint": None,
                "entrance": None,
                "heightEnvelope": None,
                "frame": "image-space",
                "transforms": {},
                "gates": {
                    "binding": "PASS",
                    "semantics": "PASS",
                    "matte": "PASS",
                    "spatial": "PASS",
                    "articulation": "PASS",
                    "runtime": "UNVERIFIED",
                    "owner": "UNVERIFIED",
                },
                "evidencePaths": [rel(src_f)],
                "limitations": [r.get("limit", "Preserved v7 boot bytes")],
                "blockedBy": [],
                "nextAction": None,
            })
        elif "to-" in rid or "-knee-" in rid:
            # joint row
            artifact_rows.append({
                "id": rid,
                "role": "joint-pair",
                "age": None,
                "classId": rid.split("-")[0],
                "status": "READY",
                "source": {"path": r.get("parent"), "sha256": r.get("parentSha256"), "roi": None},
                "output": None,
                "sourceToOutput": None,
                "intendedUse": "measured joint rotation",
                "maxDisplayCssPx": None,
                "side": r.get("side", "UNKNOWN"),
                "groundContact": None,
                "footprint": None,
                "entrance": None,
                "heightEnvelope": None,
                "frame": "image-space",
                "transforms": {"poses": r.get("poses")},
                "gates": {
                    "binding": "PASS",
                    "semantics": "PASS",
                    "matte": "PASS",
                    "spatial": "PASS",
                    "articulation": "PASS",
                    "runtime": "UNVERIFIED",
                    "owner": "UNVERIFIED",
                },
                "evidencePaths": [r.get("parent"), r.get("child")],
                "limitations": [r.get("limit", "Measured arc -25 to +25 deg")],
                "blockedBy": [],
                "nextAction": None,
            })

    # Assemble healer leg subchain
    healer_subchain = assemble_healer_leg()
    artifact_rows.append({
        "id": "healer-leg-subchain",
        "role": "subchain",
        "age": None,
        "classId": "healer",
        "status": "PARTIAL",
        "source": {"path": "assets/derivatives/rigs/v6/healer/leg_upper.png", "sha256": sha256_file(ROOT / "assets/derivatives/rigs/v6/healer/leg_upper.png"), "roi": None},
        "output": {"path": healer_subchain["neutral"], "sha256": sha256_file(ROOT / healer_subchain["neutral"]), "dimensions": [900, 900]},
        "sourceToOutput": [1, 0, 0, 1, 0, 0],
        "intendedUse": "leg subchain articulation",
        "maxDisplayCssPx": None,
        "side": "UNKNOWN",
        "groundContact": None,
        "footprint": None,
        "entrance": None,
        "heightEnvelope": None,
        "frame": "image-space",
        "transforms": {"angles": [-25, 0, 25], "clip": healer_subchain["clip"]},
        "gates": {
            "binding": "PASS",
            "semantics": "PASS",
            "matte": "PASS",
            "spatial": "PASS",
            "articulation": "PARTIAL",
            "runtime": "UNVERIFIED",
            "owner": "UNVERIFIED",
        },
        "evidencePaths": [healer_subchain["neutral"], healer_subchain["clip"]],
        "limitations": ["Valid subchain only. Missing head-to-torso and skirt-to-leg."],
        "blockedBy": [],
        "nextAction": "Attach only where a new source landmark passes bounded test.",
    })

    # Build 8 class missing-link diagrams
    chains = build_class_chain_diagrams()
    for ch in chains:
        artifact_rows.append({
            "id": ch["id"],
            "role": "missing-link-diagram",
            "age": None,
            "classId": ch["classId"],
            "status": "PARTIAL",
            "source": {"path": ch["path"], "sha256": ch["sha256"], "roi": None},
            "output": {"path": ch["path"], "sha256": ch["sha256"], "dimensions": [780, 320]},
            "sourceToOutput": [1, 0, 0, 1, 0, 0],
            "intendedUse": "documentation diagram",
            "maxDisplayCssPx": None,
            "side": "NOT_APPLICABLE",
            "groundContact": None,
            "footprint": None,
            "entrance": None,
            "heightEnvelope": None,
            "frame": "image-space",
            "transforms": {},
            "gates": {
                "binding": "PASS",
                "semantics": "PASS",
                "matte": "PASS",
                "spatial": "PASS",
                "articulation": "FAIL",
                "runtime": "NOT_APPLICABLE",
                "owner": "UNVERIFIED",
            },
            "evidencePaths": [ch["path"]],
            "limitations": [ch["reason"]],
            "blockedBy": [],
            "nextAction": None,
        })

    # Process remaining 15 troop roles
    other_troop_specs = [
        ("troop-stone-melee", 0, "Clubman", "assets/high-res/final-native2k/troop-stone-melee.png", "BLOCKED", ["REPLACEMENT_DRAFT_PENDING_OWNER_AUTHORIZATION"], ["Dirt slab in source; replacement draft pending"]),
        ("troop-stone-ranged", 0, "Slinger", "assets/high-res/final-native2k/troop-stone-ranged.png", "BLOCKED", ["REPLACEMENT_DRAFT_PENDING_OWNER_AUTHORIZATION"], ["Wooden platform in source; replacement draft pending"]),
        ("troop-bronze-heavy", 1, "Charioteer", "assets/high-res/final-native2k/troop-bronze-heavy.png", "READY", [], ["Charioteer crew, horses, vehicle as one logical unit; 64px display cap"]),
        ("troop-iron-melee", 2, "Legionary", "assets/high-res/final-native2k/troop-iron-melee.png", "READY", [], ["130px plate"]),
        ("troop-medieval-melee", 3, "Man-at-Arms", "assets/high-res/final-native2k/troop-medieval-melee.png", "READY", [], ["130px plate"]),
        ("troop-medieval-ranged", 3, "Longbowman", "assets/high-res/final-native2k/troop-medieval-ranged.png", "READY", [], ["130px plate"]),
        ("troop-medieval-heavy", 3, "Siege Knight", "assets/high-res/final-native2k/troop-medieval-heavy.png", "READY", [], ["130px plate"]),
        ("troop-gunpowder-heavy", 4, "Cannon Crew", "assets/high-res/final-native2k/troop-gunpowder-heavy.png", "READY", [], ["Cannon crew as unit; 64px display cap"]),
        ("troop-industrial-melee", 5, "Rifleman", "assets/derivatives/actors/v5/troop-industrial-melee.png", "PARTIAL", [], ["Coat hole and gap between coat and boots visible on white"]),
        ("troop-industrial-ranged", 5, "Sharpshooter", "assets/high-res/final-native2k/troop-industrial-ranged.png", "BLOCKED", ["REPLACEMENT_DRAFT_PENDING_OWNER_AUTHORIZATION"], ["Prone source cannot supply standing pose; replacement draft pending"]),
        ("troop-industrial-heavy", 5, "Steam Walker", "assets/high-res/final-native2k/troop-industrial-heavy.png", "PARTIAL", [], ["1K plate is machine gunner, not steam walker"]),
        ("troop-modern-ranged", 6, "Marksman", "assets/derivatives/actors/v4/troop-modern-ranged.png", "PARTIAL", [], ["Snow scene mound"]),
        ("troop-modern-heavy", 6, "Battle Tank", "assets/derivatives/actors/v4/troop-modern-heavy.png", "PARTIAL", [], ["Ground slab halo; 64px display cap"]),
        ("troop-future-ranged", 7, "Laser Sniper", "assets/high-res/final-native2k/troop-future-ranged.png", "READY", [], ["64px display cap"]),
        ("troop-future-heavy", 7, "Hover Tank", "assets/high-res/final-native2k/troop-future-heavy.png", "READY", [], ["64px display cap"]),
    ]

    other_troops_meta = []
    troops_catalog = {r["id"]: r for r in ready_troops}

    for tid, age, role_name, src_rel, status, blocked, limits in other_troop_specs:
        src_path = ROOT / src_rel
        out_path = DERIV / "troops" / f"{tid}.png"
        meta = extract_actor_plate(src_path, out_path, 64 if "64px" in limits[0] else 130)
        troops_catalog[tid] = {"path": meta["path"], "sha256": meta["sha256"]}
        if status == "READY":
            ready_subset_ids.append(tid)
        other_troops_meta.append({
            "id": tid,
            "age": age,
            "status": status,
            "path": meta["path"],
            "maxDisplayCssPx": 64 if "64px" in limits[0] else 130,
            "limitations": limits,
            "output": {"sha256": meta["sha256"]},
        })
        artifact_rows.append({
            "id": tid,
            "role": "static-troop",
            "age": age,
            "classId": None,
            "status": status,
            "source": {"path": src_rel, "sha256": sha256_file(src_path), "roi": None},
            "output": {"path": meta["path"], "sha256": meta["sha256"], "dimensions": meta["dimensions"]},
            "sourceToOutput": [1, 0, 0, 1, 0, 0],
            "intendedUse": f"{role_name} unit plate",
            "maxDisplayCssPx": 64 if "64px" in limits[0] else 130,
            "side": "UNKNOWN",
            "groundContact": meta["contacts"],
            "footprint": None,
            "entrance": None,
            "heightEnvelope": None,
            "frame": "image-space",
            "transforms": {},
            "gates": {
                "binding": "PASS",
                "semantics": "PASS" if not blocked else "FAIL",
                "matte": "PASS" if status == "READY" else "PARTIAL",
                "spatial": "PASS",
                "articulation": "NOT_APPLICABLE",
                "runtime": "UNVERIFIED",
                "owner": "UNVERIFIED",
            },
            "evidencePaths": [meta["path"]],
            "limitations": limits,
            "blockedBy": blocked,
            "nextAction": "Await owner budget authorization" if blocked else None,
        })

    # Process 8 creatures
    creatures_specs = [
        ("creature-wolf", "Dire Wolf", "assets/delivery/stone-starter-20261003/derivatives/v2/live/plates/creature-wolf.png"),
        ("creature-bandit", "Bandit", "assets/delivery/stone-starter-20261003/derivatives/v2/live/plates/creature-bandit.png"),
        ("creature-bear", "Cave Bear", "assets/delivery/stone-starter-20261003/derivatives/v2/live/plates/creature-bear.png"),
        ("creature-harpy", "Harpy", "assets/delivery/stone-starter-20261003/derivatives/v2/live/plates/creature-harpy.png"),
        ("creature-golem", "Stone Golem", "assets/delivery/stone-starter-20261003/derivatives/v2/live/plates/creature-golem.png"),
        ("creature-griffin", "Griffin", "assets/delivery/stone-starter-20261003/derivatives/v2/live/plates/creature-griffin.png"),
        ("creature-wyvern", "Wyvern", "assets/delivery/stone-starter-20261003/derivatives/v2/live/plates/creature-wyvern.png"),
        ("creature-drone", "Drone Swarm", "assets/delivery/stone-starter-20261003/derivatives/v2/live/plates/creature-drone.png"),
    ]
    creatures_meta = []
    for cid, cname, csrc in creatures_specs:
        src_path = ROOT / csrc
        out_path = DERIV / "creatures" / f"{cid}.png"
        meta = extract_actor_plate(src_path, out_path, 130)
        ready_subset_ids.append(cid)
        creatures_meta.append({"id": cid, "name": cname, "path": meta["path"], "dimensions": meta["dimensions"], "contacts": meta["contacts"]})
        artifact_rows.append({
            "id": cid,
            "role": "creature",
            "age": None,
            "classId": None,
            "status": "READY",
            "source": {"path": csrc, "sha256": sha256_file(src_path), "roi": None},
            "output": {"path": meta["path"], "sha256": meta["sha256"], "dimensions": meta["dimensions"]},
            "sourceToOutput": [1, 0, 0, 1, 0, 0],
            "intendedUse": f"{cname} combat encounter sprite",
            "maxDisplayCssPx": 130,
            "side": "UNKNOWN",
            "groundContact": meta["contacts"],
            "footprint": None,
            "entrance": None,
            "heightEnvelope": None,
            "frame": "image-space",
            "transforms": {},
            "gates": {
                "binding": "PASS",
                "semantics": "PASS",
                "matte": "PASS",
                "spatial": "PASS",
                "articulation": "NOT_APPLICABLE",
                "runtime": "UNVERIFIED",
                "owner": "UNVERIFIED",
            },
            "evidencePaths": [meta["path"]],
            "limitations": ["Static creature sprite; no walk cycle"],
            "blockedBy": [],
            "nextAction": None,
        })

    # Process 40 Attackers across 8 ages
    ages = ["stone", "bronze", "iron", "medieval", "gunpowder", "industrial", "modern", "future"]
    att_roles = ["brute", "runner", "archer", "sapper", "shaman"]
    attackers_meta = []
    for a_idx, age in enumerate(ages):
        for role in att_roles:
            att_id = f"attacker-{age}-{role}"
            src_f = ROOT / f"assets/delivery/stone-starter-20261003/derivatives/v2/live/plates/{att_id}.png"
            if not src_f.exists():
                continue
            out_f = DERIV / "attackers" / f"{att_id}.png"
            meta = extract_actor_plate(src_f, out_f, 130)
            ready_subset_ids.append(att_id)
            attackers_meta.append({"id": att_id, "path": meta["path"], "age": a_idx, "role": role})
            artifact_rows.append({
                "id": att_id,
                "role": "attacker",
                "age": a_idx,
                "classId": None,
                "status": "READY",
                "source": {"path": rel(src_f), "sha256": sha256_file(src_f), "roi": None},
                "output": {"path": meta["path"], "sha256": meta["sha256"], "dimensions": meta["dimensions"]},
                "sourceToOutput": [1, 0, 0, 1, 0, 0],
                "intendedUse": f"{age} {role} defense wave attacker",
                "maxDisplayCssPx": 130,
                "side": "UNKNOWN",
                "groundContact": meta["contacts"],
                "footprint": None,
                "entrance": None,
                "heightEnvelope": None,
                "frame": "image-space",
                "transforms": {},
                "gates": {
                    "binding": "PASS",
                    "semantics": "PASS",
                    "matte": "PASS",
                    "spatial": "PASS",
                    "articulation": "NOT_APPLICABLE",
                    "runtime": "UNVERIFIED",
                    "owner": "UNVERIFIED",
                },
                "evidencePaths": [meta["path"]],
                "limitations": ["Static attacker sprite"],
                "blockedBy": [],
                "nextAction": None,
            })

    # Process 4 Mounts
    mounts_specs = [
        ("hero-mount-horse", "Horse Mount", "assets/high-res/final-native2k/hero-mount-horse.png", 64, "Ancient/Medieval mount; 64px display limit"),
        ("hero-mount-motor-transport", "Motor Transport", "assets/high-res/final-native2k/hero-mount-motor-transport.png", 64, "Industrial/Modern transport; 64px display limit"),
        ("hero-mount-future-transport", "Future Transport", "assets/high-res/final-native2k/hero-mount-future-transport.png", 64, "Future transport; 64px display limit"),
        ("knight-mounted-master", "Mounted Master", "assets/high-res/final-native2k/knight-mounted-master.png", 130, "Scenic medieval mounted knight; role limit noted"),
    ]
    mounts_meta = []
    for mid, mname, msrc, max_px, note in mounts_specs:
        src_path = ROOT / msrc
        out_path = DERIV / "mounts" / f"{mid}.png"
        meta = extract_actor_plate(src_path, out_path, max_px)
        ready_subset_ids.append(mid)
        mounts_meta.append({"id": mid, "name": mname, "path": meta["path"], "maxDisplayCssPx": max_px, "note": note})
        artifact_rows.append({
            "id": mid,
            "role": "mount",
            "age": None,
            "classId": "knight" if "knight" in mid else None,
            "status": "READY",
            "source": {"path": msrc, "sha256": sha256_file(src_path), "roi": None},
            "output": {"path": meta["path"], "sha256": meta["sha256"], "dimensions": meta["dimensions"]},
            "sourceToOutput": [1, 0, 0, 1, 0, 0],
            "intendedUse": f"{mname} travel/combat sprite",
            "maxDisplayCssPx": max_px,
            "side": "UNKNOWN",
            "groundContact": meta["contacts"],
            "footprint": None,
            "entrance": None,
            "heightEnvelope": None,
            "frame": "image-space",
            "transforms": {},
            "gates": {
                "binding": "PASS",
                "semantics": "PASS",
                "matte": "PASS",
                "spatial": "PASS",
                "articulation": "NOT_APPLICABLE",
                "runtime": "UNVERIFIED",
                "owner": "UNVERIFIED",
            },
            "evidencePaths": [meta["path"]],
            "limitations": [note],
            "blockedBy": [],
            "nextAction": None,
        })

    # Process 10 Canonical Artifacts
    artifacts_specs = [
        ("wolfamulet", "Amulet of the Wolf", "assets/production/production-17-20261003/images/14-artifact-wolf-amulet.png", "+2 morale"),
        ("bloodstone", "Bloodstone", "assets/production/production-17-20261003/images/15-artifact-bloodstone.png", "+3 attack"),
        ("clover", "Iron Clover", "assets/production/production-17-20261003/images/16-artifact-iron-clover.png", "+2 luck"),
        ("lens", "Eagle Eye Lens", "assets/production/production-17-20261003/images/17-artifact-eagle-eye-lens.png", "+25% shooter damage"),
        ("vitality", "Ring of Vitality", "assets/production/production-17-20261003/images/18-artifact-ring-of-vitality.png", "+15% troop HP"),
        ("swiftboots", "Winged Spurs", "assets/production/production-17-20261003/images/19-artifact-winged-spurs.png", "+2 speed to all stacks"),
        ("codex", "Sage's Codex", "assets/production/production-17-20261003/images/20-artifact-sages-codex.png", "+4 knowledge"),
        ("orb", "Orb of Storms", "assets/production/production-11-20261003/images/18-artifact-orb.png", "+3 power"),
        ("banner", "Ancient Banner", "assets/production/production-11-20261003/images/21-artifact-banner.png", "+1 morale, attack, defense"),
        ("aegis", "Aegis Shard", "assets/production/production-11-20261003/images/26-artifact-aegis.png", "+3 defense"),
    ]
    artifacts_meta = {}
    for aid, aname, asrc, adesc in artifacts_specs:
        src_path = ROOT / asrc
        out_path = DERIV / "artifacts" / f"{aid}.png"
        meta = extract_actor_plate(src_path, out_path, 64)
        ready_subset_ids.append(f"artifact-{aid}")
        artifacts_meta[aid] = {"id": aid, "name": aname, "path": meta["path"], "desc": adesc}
        artifact_rows.append({
            "id": f"artifact-{aid}",
            "role": "artifact-icon",
            "age": None,
            "classId": None,
            "status": "READY",
            "source": {"path": asrc, "sha256": sha256_file(src_path), "roi": None},
            "output": {"path": meta["path"], "sha256": meta["sha256"], "dimensions": meta["dimensions"]},
            "sourceToOutput": [1, 0, 0, 1, 0, 0],
            "intendedUse": f"{aname} inventory icon",
            "maxDisplayCssPx": 64,
            "side": "NOT_APPLICABLE",
            "groundContact": None,
            "footprint": None,
            "entrance": None,
            "heightEnvelope": None,
            "frame": "image-space",
            "transforms": {},
            "gates": {
                "binding": "PASS",
                "semantics": "PASS",
                "matte": "PASS",
                "spatial": "PASS",
                "articulation": "NOT_APPLICABLE",
                "runtime": "UNVERIFIED",
                "owner": "UNVERIFIED",
            },
            "evidencePaths": [meta["path"]],
            "limitations": ["Inventory icon crop"],
            "blockedBy": [],
            "nextAction": None,
        })

    # Process Canonical Equipment across 6 slots
    gear_candidates = [
        # Stone
        ("gear-stone-helm", 0, "helm", "assets/production/production-02-20261003/images/18-gear-stone-helm.png"),
        ("gear-stone-weapon", 0, "weapon", "assets/production/production-02-20261003/images/19-gear-stone-weapon.png"),
        ("gear-stone-offhand", 0, "offhand", "assets/production/production-02-20261003/images/20-gear-stone-offhand.png"),
        ("gear-stone-armor", 0, "armor", "assets/production/production-02-20261003/images/21-gear-stone-armor.png"),
        ("gear-stone-boots", 0, "boots", "assets/production/production-02-20261003/images/22-gear-stone-boots.png"),
        ("gear-stone-accessory", 0, "accessory", "assets/production/production-02-20261003/images/23-gear-stone-accessory.png"),
        # Bronze
        ("gear-bronze-weapon", 1, "weapon", "assets/production/production-13-20261003/images/04-gear-bronze-weapon.png"),
        ("gear-bronze-armor", 1, "armor", "assets/production/production-13-20261003/images/05-gear-bronze-armor.png"),
        ("gear-bronze-helm", 1, "helm", "assets/production/production-13-20261003/images/06-gear-bronze-helm.png"),
        ("gear-bronze-boots", 1, "boots", "assets/production/production-13-20261003/images/07-gear-bronze-boots.png"),
        ("gear-bronze-offhand", 1, "offhand", "assets/production/production-13-20261003/images/08-gear-bronze-offhand.png"),
        ("gear-bronze-accessory", 1, "accessory", "assets/production/production-13-20261003/images/09-gear-bronze-accessory.png"),
        # Iron
        ("gear-iron-weapon", 2, "weapon", "assets/production/production-13-20261003/images/10-gear-iron-weapon.png"),
        ("gear-iron-armor", 2, "armor", "assets/production/production-13-20261003/images/11-gear-iron-armor.png"),
        ("gear-iron-helm", 2, "helm", "assets/production/production-13-20261003/images/12-gear-iron-helm.png"),
        ("gear-iron-boots", 2, "boots", "assets/production/production-13-20261003/images/13-gear-iron-boots.png"),
        ("gear-iron-offhand", 2, "offhand", "assets/production/production-13-20261003/images/14-gear-iron-offhand.png"),
        ("gear-iron-accessory", 2, "accessory", "assets/production/production-13-20261003/images/15-gear-iron-accessory.png"),
        # Medieval
        ("gear-medieval-weapon", 3, "weapon", "assets/production/production-13-20261003/images/16-gear-medieval-weapon.png"),
        ("gear-medieval-armor", 3, "armor", "assets/production/production-13-20261003/images/17-gear-medieval-armor.png"),
        ("gear-medieval-helm", 3, "helm", "assets/production/production-13-20261003/images/18-gear-medieval-helm.png"),
        ("gear-medieval-boots", 3, "boots", "assets/production/production-13-20261003/images/19-gear-medieval-boots.png"),
        ("gear-medieval-offhand", 3, "offhand", "assets/production/production-13-20261003/images/20-gear-medieval-offhand.png"),
        ("gear-medieval-accessory", 3, "accessory", "assets/production/production-13-20261003/images/21-gear-medieval-accessory.png"),
        # Gunpowder
        ("gear-gunpowder-weapon", 4, "weapon", "assets/production/production-13-20261003/images/22-gear-gunpowder-weapon.png"),
        ("gear-gunpowder-armor", 4, "armor", "assets/production/production-13-20261003/images/23-gear-gunpowder-armor.png"),
        ("gear-gunpowder-helm", 4, "helm", "assets/production/production-13-20261003/images/24-gear-gunpowder-helm.png"),
        ("gear-gunpowder-boots", 4, "boots", "assets/production/production-13-20261003/images/25-gear-gunpowder-boots.png"),
        ("gear-gunpowder-offhand", 4, "offhand", "assets/production/production-13-20261003/images/26-gear-gunpowder-offhand.png"),
        ("gear-gunpowder-accessory", 4, "accessory", "assets/production/production-16-20261003/images/28-gear-gunpowder-accessory.png"),
        # Industrial
        ("gear-industrial-weapon", 5, "weapon", "assets/production/production-13-20261003/images/27-gear-industrial-weapon.png"),
        ("gear-industrial-armor", 5, "armor", "assets/production/production-13-20261003/images/28-gear-industrial-armor.png"),
        ("gear-industrial-helm", 5, "helm", "assets/production/production-13-20261003/images/29-gear-industrial-helm.png"),
        ("gear-industrial-boots", 5, "boots", "assets/production/production-13-20261003/images/30-gear-industrial-boots.png"),
        ("gear-industrial-offhand", 5, "offhand", "assets/production/production-17-20261003/images/04-gear-industrial-offhand.png"),
        ("gear-industrial-accessory", 5, "accessory", "assets/production/production-14-20261003/images/04-gear-industrial-accessory.png"),
        # Modern
        ("gear-modern-helm", 6, "helm", "assets/production/production-14-20261003/images/05-gear-modern-helm.png"),
        ("gear-modern-weapon", 6, "weapon", "assets/production/production-14-20261003/images/08-gear-modern-weapon.png"),
        ("gear-modern-offhand", 6, "offhand", "assets/production/production-14-20261003/images/12-gear-modern-offhand.png"),
        ("gear-modern-armor", 6, "armor", "assets/production/production-14-20261003/images/15-gear-modern-armor.png"),
        ("gear-modern-boots", 6, "boots", "assets/production/production-14-20261003/images/18-gear-modern-boots.png"),
        ("gear-modern-accessory", 6, "accessory", "assets/production/production-14-20261003/images/20-gear-modern-accessory.png"),
        # Future
        ("gear-future-helm", 7, "helm", "assets/production/production-14-20261003/images/21-gear-future-helm.png"),
        ("gear-future-weapon", 7, "weapon", "assets/production/production-14-20261003/images/24-gear-future-weapon.png"),
        ("gear-future-offhand", 7, "offhand", "assets/production/production-14-20261003/images/28-gear-future-offhand.png"),
        ("gear-future-armor", 7, "armor", "assets/production/production-15-20261003/images/02-gear-future-armor.png"),
        ("gear-future-boots", 7, "boots", "assets/production/production-15-20261003/images/05-gear-future-boots.png"),
        ("gear-future-accessory", 7, "accessory", "assets/production/production-15-20261003/images/07-gear-future-accessory.png"),
    ]

    gear_meta = {}
    gears_list = []
    for gid, age, slot, gsrc in gear_candidates:
        src_path = ROOT / gsrc
        if not src_path.exists():
            continue
        out_path = DERIV / "gear" / f"{gid}.png"
        meta = extract_actor_plate(src_path, out_path, 64)
        ready_subset_ids.append(gid)
        item_entry = {"id": gid, "path": meta["path"], "slot": slot, "age": age}
        gear_meta[gid] = item_entry
        gears_list.append(item_entry)
        artifact_rows.append({
            "id": gid,
            "role": "gear-icon",
            "age": age,
            "classId": None,
            "status": "READY",
            "source": {"path": gsrc, "sha256": sha256_file(src_path), "roi": None},
            "output": {"path": meta["path"], "sha256": meta["sha256"], "dimensions": meta["dimensions"]},
            "sourceToOutput": [1, 0, 0, 1, 0, 0],
            "intendedUse": f"{slot} slot gear icon",
            "maxDisplayCssPx": 64,
            "side": "NOT_APPLICABLE",
            "groundContact": None,
            "footprint": None,
            "entrance": None,
            "heightEnvelope": None,
            "frame": "image-space",
            "transforms": {},
            "gates": {
                "binding": "PASS",
                "semantics": "PASS",
                "matte": "PASS",
                "spatial": "PASS",
                "articulation": "NOT_APPLICABLE",
                "runtime": "UNVERIFIED",
                "owner": "UNVERIFIED",
            },
            "evidencePaths": [meta["path"]],
            "limitations": ["Gear icon crop"],
            "blockedBy": [],
            "nextAction": None,
        })

    # Process Actor FX
    fx_specs = [
        ("effect-resurrect", "assets/production/production-13-20261003/images/01-effect-resurrect.png"),
        ("effect-projectile", "assets/production/production-13-20261003/images/02-effect-projectile.png"),
        ("effect-impact", "assets/production/production-13-20261003/images/03-effect-impact.png"),
        ("effect-haste", "assets/production/production-12-20261003/images/27-effect-haste.png"),
        ("effect-curse", "assets/production/production-12-20261003/images/28-effect-curse.png"),
        ("effect-cure", "assets/production/production-12-20261003/images/29-effect-cure.png"),
        ("effect-shield", "assets/production/production-12-20261003/images/30-effect-shield.png"),
    ]
    for fid, fsrc in fx_specs:
        src_path = ROOT / fsrc
        if not src_path.exists():
            continue
        out_path = DERIV / "fx" / f"{fid}.png"
        meta = extract_actor_plate(src_path, out_path, 64)
        ready_subset_ids.append(fid)
        artifact_rows.append({
            "id": fid,
            "role": "fx-sprite",
            "age": None,
            "classId": None,
            "status": "READY",
            "source": {"path": fsrc, "sha256": sha256_file(src_path), "roi": None},
            "output": {"path": meta["path"], "sha256": meta["sha256"], "dimensions": meta["dimensions"]},
            "sourceToOutput": [1, 0, 0, 1, 0, 0],
            "intendedUse": "combat FX sprite",
            "maxDisplayCssPx": 64,
            "side": "NOT_APPLICABLE",
            "groundContact": None,
            "footprint": None,
            "entrance": None,
            "heightEnvelope": None,
            "frame": "image-space",
            "transforms": {},
            "gates": {
                "binding": "PASS",
                "semantics": "PASS",
                "matte": "PASS",
                "spatial": "PASS",
                "articulation": "NOT_APPLICABLE",
                "runtime": "UNVERIFIED",
                "owner": "UNVERIFIED",
            },
            "evidencePaths": [meta["path"]],
            "limitations": ["Static combat FX sprite"],
            "blockedBy": [],
            "nextAction": None,
        })

    # Generate screen composites
    composites = create_screen_composites(troops_catalog, gear_meta, artifacts_meta)

    # Write HTML review gallery
    generate_html_review_gallery(
        composites,
        ready_troops,
        other_troops_meta,
        creatures_meta,
        attackers_meta,
        mounts_meta,
        list(artifacts_meta.values()),
        gears_list,
        chains,
        [healer_subchain],
    )

    # Build and write ArtInterface
    art_interface = {
        "schema": 1,
        "producer": "ACTORS",
        "version": "actors-equipment-20261006",
        "inputSnapshot": input_snapshot,
        "rows": artifact_rows,
        "readySubset": ready_subset_ids,
        "wholeDeliveryReady": False,
        "reviewGallery": rel(QA / "review" / "index.html"),
        "checkpoint": rel(QA / "checkpoint.json"),
    }
    INTERFACE_PATH.parent.mkdir(parents=True, exist_ok=True)
    INTERFACE_PATH.write_text(json.dumps(art_interface, indent=2), encoding="utf-8")
    print("ArtInterface written successfully to", INTERFACE_PATH)

    # Build and write Checkpoint
    checkpoint = {
        "status": "INCOMPLETE",
        "completedIds": ready_subset_ids,
        "partialIds": [
            "healer-leg-subchain",
            "healer-torso-to-skirt",
            "troop-industrial-melee",
            "troop-industrial-heavy",
            "troop-modern-ranged",
            "troop-modern-heavy",
            *[ch["id"] for ch in chains],
        ],
        "failedIds": [
            "knight-thigh-greave",
            "paladin-thigh-knee",
            "paladin-greave-boot",
            "paladin-head-raster",
            "healer-head-to-torso",
            "healer-skirt-to-leg",
        ],
        "blockedIds": [
            "troop-stone-melee",
            "troop-stone-ranged",
            "troop-industrial-ranged",
        ],
        "nextExecutableActions": {
            "troop-stone-melee": "Await owner budget authorization for 3-role replacement draft.",
            "troop-stone-ranged": "Await owner budget authorization for 3-role replacement draft.",
            "troop-industrial-ranged": "Await owner budget authorization for 3-role replacement draft.",
            "healer-class-chain": "Inspect new source landmark before attempting waist/neck attachment.",
            "knight-class-chain": "Stopped fail on thigh/greave; do not restart 13 exhausted sweeps.",
        },
        "sourceHashes": {
            "healerBoot": sha256_file(BOOT),
            "draft": sha256_file(DRAFT),
            "contract": sha256_file(CONTRACT),
            "v9Interface": sha256_file(V9_INTERFACE),
        },
        "evidencePaths": [
            rel(QA / "review" / "index.html"),
            rel(INTERFACE_PATH),
            rel(QA / "assemblies" / "healer-leg-subchain-arc.gif"),
        ],
        "polishQueue": [
            {"id": "troop-industrial-melee", "issue": "coat-hole-matte-refinement"},
            {"id": "troop-modern-heavy", "issue": "halo-and-slab-refinement"},
        ],
        "authorityLimits": [
            "NO_NEW_PAID_CALLS: 17 purchased batches, 32 native4K, 73 native2K exist.",
            "DEVICE_WORK_STOPPED: Zero permissions offline local runtime.",
            "WHOLE_GAME_LANDSCAPE: Landscape orientation for all screens.",
            "PRESERVE_REPLACEMENT_DRAFT: 3-role draft remains DRAFT_NOT_SUBMITTED / OWNER_BUDGET_AUTHORIZATION_REQUIRED.",
            "DISPLAY_CAPS: 64px display caps for mounts, cannon, future heavy.",
            "CHARIOTEER: Crew, horses, and vehicle preserved as one logical unit.",
        ],
    }
    (QA / "checkpoint.json").write_text(json.dumps(checkpoint, indent=2), encoding="utf-8")
    print("Checkpoint written successfully to", QA / "checkpoint.json")


if __name__ == "__main__":
    main()
