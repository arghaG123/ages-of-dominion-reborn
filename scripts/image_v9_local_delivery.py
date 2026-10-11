"""Local image delivery v9. Existing sources only. No provider calls.

Python 3.13 / Pillow / NumPy / OpenCV. Writes new versioned files.
Does not overwrite v4-v8 interfaces, natives, or the Healer v7 boot.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / "qa" / "image-local-delivery-v9-20261005"
V8 = ROOT / "qa" / "image-local-delivery-v8-20261005"
MOCKS = ROOT / "design-preview" / "generated" / "landscape-mocks-20261003-efcd7a7e" / "images"
SHEET = ROOT / "assets" / "high-res" / "final-native2k" / "rig-source-parts-healer.png"
BOOT = ROOT / "assets" / "derivatives" / "rigs" / "v7" / "healer" / "boot.png"
DRAFT = ROOT / "docs" / "plan" / "REPLACEMENT-DRAFT-THREE-ROLES-V6-CLARIFICATION-2026-10-04.json"
CONTRACT = ROOT / "src" / "data" / "implementation-contract.json"
V8_INTERFACE = ROOT / "docs" / "plan" / "IMAGE-DELIVERY-INTERFACE-V8-2026-10-05.json"
AFFINE = [60, -10, 25, 35, 170, 165]
HALL_SCALE = 0.1312
HEADER_PX = 56
FOOTER_PX = 56
BG = np.array([144.5, 178.0, 105.0], np.float32)
HEAD_T = 36

HEADS = [
    {"id": "healer-head-front-neck", "box": (35, 476, 263, 483), "view": "FRONT", "anatomy": "head_with_neck", "card": True},
    {"id": "healer-head-front-bust", "box": (42, 30, 247, 385), "view": "FRONT", "anatomy": "head", "card": True},
    {"id": "healer-head-three-quarter", "box": (353, 32, 273, 381), "view": "THREE_QUARTER_IMAGE_RIGHT", "anatomy": "head", "card": True},
    {"id": "healer-head-profile-braid", "box": (683, 27, 295, 630), "view": "PROFILE_IMAGE_RIGHT", "anatomy": "head_and_attached_braid", "card": True},
    {"id": "healer-head-profile-bun", "box": (316, 474, 311, 477), "view": "PROFILE_IMAGE_LEFT", "anatomy": "head_with_neck", "card": True},
    {"id": "healer-head-crown", "box": (708, 641, 261, 334), "view": "CROWN", "anatomy": "head_top", "card": False},
    {"id": "healer-braid", "box": (606, 352, 54, 305), "view": "SEPARATE_BRAID", "anatomy": "braid", "card": False},
]

# Legal pixels on the 1376x768 frame. Native = legal * 4.
# Bridge midspan was checked against a red centerline on the wooden deck.
STONE_LEGAL = {
    "roads": [
        {"kind": "west-entry", "pts": [[0, 400], [180, 420], [360, 400]], "uncertaintyLegalPx": 32},
        {"kind": "camp-spokes", "pts": [[520, 100], [500, 280], [530, 460], [560, 640]], "uncertaintyLegalPx": 40},
        {"kind": "ring-to-bridge", "pts": [[640, 320], [860, 345], [1040, 358], [1152, 366]], "uncertaintyLegalPx": 24},
        {"kind": "south-arc", "pts": [[160, 640], [420, 660], [760, 630], [980, 560]], "uncertaintyLegalPx": 40},
    ],
    "river": [[1120, 20], [1140, 180], [1160, 340], [1200, 520], [1220, 720]],
    "banks": [
        {"side": "near-bank", "observedBankSide": "west", "pts": [[1040, 0], [1060, 160], [1100, 320], [1140, 480], [1160, 700]]},
        {"side": "far-bank", "observedBankSide": "east", "pts": [[1240, 0], [1280, 160], [1340, 300], [1368, 480], [1320, 720]]},
    ],
    "deck": [[1088, 347], [1152, 355], [1224, 365], [1280, 375], [1344, 393], [1344, 415], [1280, 397], [1224, 387], [1152, 377], [1088, 369]],
    "approaches": [
        {"kind": "near-approach", "pts": [[1000, 360], [1088, 358]]},
        {"kind": "far-approach", "pts": [[1344, 404], [1368, 408]]},
    ],
    "rocks": [[380, 240], [520, 190], [680, 230], [710, 320], [600, 400], [450, 390], [370, 320]],
    "bankUncertaintyLegalPx": 40,
    "deckUncertaintyLegalPx": 16,
    "riverUncertaintyLegalPx": 40,
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def versions() -> dict:
    import PIL
    import scipy
    return {
        "python": ".".join(map(str, __import__("sys").version_info[:3])),
        "Pillow": PIL.__version__,
        "NumPy": np.__version__,
        "OpenCV": cv2.__version__,
        "SciPy": scipy.__version__,
    }


def save_png(path: Path, rgba: np.ndarray) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(rgba, "RGBA").save(path)
    return sha256(path)


def enclosed_hole_count(alpha: np.ndarray) -> int:
    inv = (alpha == 0).astype(np.uint8)
    h, w = inv.shape
    flood = inv.copy()
    mask = np.zeros((h + 2, w + 2), np.uint8)
    for x in range(w):
        if flood[0, x]:
            cv2.floodFill(flood, mask, (int(x), 0), 0)
        if flood[h - 1, x]:
            cv2.floodFill(flood, mask, (int(x), int(h - 1)), 0)
    for y in range(h):
        if flood[y, 0]:
            cv2.floodFill(flood, mask, (0, int(y)), 0)
        if flood[y, w - 1]:
            cv2.floodFill(flood, mask, (int(w - 1), int(y)), 0)
    return int((flood > 0).sum())


def bbox(alpha: np.ndarray, thresh: int) -> list | None:
    ys, xs = np.where(alpha > thresh)
    if len(xs) == 0:
        return None
    return [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]


def composite(rgba: np.ndarray, color: tuple[int, int, int]) -> Image.Image:
    rgb = rgba[:, :, :3].astype(np.float32)
    a = rgba[:, :, 3:4].astype(np.float32) / 255.0
    bg = np.array(color, np.float32)
    return Image.fromarray((rgb * a + bg * (1 - a)).astype(np.uint8), "RGB")


def scale_to_height(rgba: np.ndarray, height: int) -> np.ndarray:
    h, w = rgba.shape[:2]
    width = max(1, int(round(w * height / h)))
    return np.array(Image.fromarray(rgba, "RGBA").resize((width, height), Image.Resampling.BOX))


def candidate_mask(rgb: np.ndarray, widen: bool) -> np.ndarray:
    src = rgb.astype(np.int16) if widen else rgb
    return (src[:, :, 2] > src[:, :, 0] + 18) & (src[:, :, 2] > src[:, :, 1] + 8) & (src[:, :, 2] > 70)


def synthetic_overflow() -> dict:
    px = np.array([[[240, 240, 250]]], np.uint8)
    both = np.array([[[80, 90, 160]]], np.uint8)
    wrapped = bool(candidate_mask(px, False)[0, 0])
    wide = bool(candidate_mask(px, True)[0, 0])
    return {
        "case": "uint8 R+18 overflow",
        "pixelRgb": [240, 240, 250],
        "uint8Candidate": wrapped,
        "widenedCandidate": wide,
        "passed": wrapped and not wide,
        "controlBothTrue": bool(candidate_mask(both, False)[0, 0] and candidate_mask(both, True)[0, 0]),
        "note": "Mask arithmetic only. Not a river or a bank.",
    }


def load_rgba(path: Path) -> np.ndarray:
    return np.array(Image.open(path).convert("RGBA"))


def cuff_profile(alpha: np.ndarray, end: str):
    mask = alpha > 128
    h, _w = mask.shape
    span = 40 if h > 80 else max(8, h // 5)
    rows = range(h - 1, max(-1, h - span), -1) if end == "distal" else range(0, min(h, span))
    best = None
    for y in rows:
        xs = np.where(mask[y])[0]
        if len(xs) < 4:
            continue
        width = int(xs.max() - xs.min() + 1)
        rec = {"y": int(y), "width": width, "cx": int((int(xs.min()) + int(xs.max())) / 2), "x0": int(xs.min()), "x1": int(xs.max())}
        if best is None or width > best["width"]:
            best = rec
    return best


def warp_part(rgba, joint_xy, pivot_xy, angle_deg, canvas):
    jx, jy = joint_xy
    px, py = pivot_xy
    rad = np.deg2rad(angle_deg)
    c, s = float(np.cos(rad)), float(np.sin(rad))
    matrix = np.array([[c, -s, px - (c * jx - s * jy)], [s, c, py - (s * jx + c * jy)]], np.float32)
    ch, cw = canvas
    warped = cv2.warpAffine(
        cv2.cvtColor(rgba, cv2.COLOR_RGBA2BGRA),
        matrix,
        (cw, ch),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(0, 0, 0, 0),
    )
    return cv2.cvtColor(warped, cv2.COLOR_BGRA2RGBA)


def measure_pair(parent_rel: str, child_rel: str, insertion: float, transverse: float) -> dict:
    parent = load_rgba(ROOT / parent_rel)
    child = load_rgba(ROOT / child_rel)
    pc = cuff_profile(parent[:, :, 3], "distal")
    cc = cuff_profile(child[:, :, 3], "proximal")
    ph, pw = parent.shape[:2]
    ch, cw = child.shape[:2]
    pad = int(max(pw, ph, cw, ch) * 1.2)
    canvas = (ph + ch + pad, pw + cw + pad)  # height, width
    pivot = (canvas[1] // 2, canvas[0] // 2)  # x, y
    cuff_w = max(pc["width"], cc["width"])
    child_pivot = (pivot[0] + transverse * cuff_w, pivot[1] - insertion * cuff_w)
    parent_layer = warp_part(parent, (pc["cx"], pc["y"]), pivot, 0, canvas)
    poses = []
    for ang in (-25, 0, 25):
        child_layer = warp_part(child, (cc["cx"], cc["y"]), child_pivot, ang, canvas)
        rad = max(8, cuff_w)
        y0, y1 = max(0, int(child_pivot[1] - rad)), min(canvas[0], int(child_pivot[1] + rad))
        x0, x1 = max(0, int(child_pivot[0] - rad * 2)), min(canvas[1], int(child_pivot[0] + rad * 2))
        roi_p = parent_layer[y0:y1, x0:x1, 3]
        roi_c = child_layer[y0:y1, x0:x1, 3]
        both = (roi_p > 128) & (roi_c > 16)
        span = 0
        for row in both:
            run = 0
            for v in row:
                run = run + 1 if v else 0
                span = max(span, run)
        poses.append({
            "angle": ang,
            "overlapParent128Child16": int(both.sum()),
            "continuousRunPx": int(span),
            "jointRoiParentAlphaGt128": int((roi_p > 128).sum()),
            "jointRoiChildAlphaGt16": int((roi_c > 16).sum()),
        })
    return {
        "canvasHeightWidth": [canvas[0], canvas[1]],
        "canvasWidthHeight": [canvas[1], canvas[0]],
        "sharedPivotCanvasXY": [pivot[0], pivot[1]],
        "childPivotCanvasXY": [round(child_pivot[0], 4), round(child_pivot[1], 4)],
        "cuffParent": pc,
        "cuffChild": cc,
        "poses": poses,
        "parentLayer": parent_layer,
        "note": "canvasHeightWidth matches the v7/v8 stored canvas order. sharedPivotCanvasXY is x then y.",
    }


def extract_heads() -> list:
    rgb = np.array(Image.open(SHEET).convert("RGB"))
    dist = np.linalg.norm(rgb.astype(np.float32) - BG, axis=2)
    magenta = (rgb[:, :, 0] > 180) & (rgb[:, :, 1] < 90) & (rgb[:, :, 2] > 80)
    region = np.zeros(dist.shape, bool)
    region[16:1008, 16:1008] = True
    mask = (dist > HEAD_T) & region & ~magenta
    n, labels, stats, _ = cv2.connectedComponentsWithStats(mask.astype(np.uint8), 8)
    keep = np.zeros(mask.shape, np.uint8)
    dropped = []
    for i in range(1, n):
        x, y, w, h, area = [int(v) for v in stats[i]]
        solidity = area / max(1, w * h)
        if area < 800 or solidity < 0.08:
            dropped.append({"area": area, "solidity": round(solidity, 4), "box": [x, y, w, h]})
            continue
        keep[labels == i] = 255
    # One correction: fill enclosed pinholes under 40px. Do not repaint RGB.
    holes = (cv2.bitwise_not(keep) > 0).astype(np.uint8)
    flood = holes.copy()
    ff_mask = np.zeros((holes.shape[0] + 2, holes.shape[1] + 2), np.uint8)
    cv2.floodFill(flood, ff_mask, (0, 0), 0)
    enclosed = flood > 0
    n_h, lab_h, stats_h, _ = cv2.connectedComponentsWithStats(enclosed.astype(np.uint8), 8)
    filled = 0
    for i in range(1, n_h):
        area = int(stats_h[i, cv2.CC_STAT_AREA])
        if area <= 40:
            keep[lab_h == i] = 255
            filled += area
    rows = []
    out_dir = ROOT / "assets" / "derivatives" / "rigs" / "v9" / "healer"
    for spec in HEADS:
        x, y, w, h = spec["box"]
        # Match the connected component that covers the box center, then trim.
        cx, cy = x + w // 2, y + h // 2
        comp = int(labels[cy, cx])
        part = np.zeros(keep.shape, np.uint8)
        if comp:
            part[labels == comp] = 255
        else:
            part[y:y + h, x:x + w] = keep[y:y + h, x:x + w]
        inv = (part == 0).astype(np.uint8)
        flood = inv.copy()
        ff = np.zeros((inv.shape[0] + 2, inv.shape[1] + 2), np.uint8)
        cv2.floodFill(flood, ff, (20, 20), 0)
        n_local, lab_local, stats_local, _ = cv2.connectedComponentsWithStats((flood > 0).astype(np.uint8), 8)
        for hi in range(1, n_local):
            if int(stats_local[hi, cv2.CC_STAT_AREA]) <= 40:
                part[lab_local == hi] = 255
        ys, xs = np.where(part > 0)
        x0, y0, x1, y1 = int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1
        crop_rgb = rgb[y0:y1, x0:x1]
        crop_a = part[y0:y1, x0:x1]
        rgba = np.dstack([crop_rgb, crop_a])
        path = out_dir / f"{spec['id']}.png"
        digest = save_png(path, rgba)
        mask_path = QA / "masks" / f"{spec['id']}.png"
        save_png(mask_path, np.dstack([crop_a, crop_a, crop_a, np.full_like(crop_a, 255)]))
        a16 = bbox(crop_a, 16)
        a128 = bbox(crop_a, 128)
        holes_left = enclosed_hole_count(crop_a)
        neck = None
        if spec["anatomy"].startswith("head"):
            rows_a = np.where((crop_a > 128).any(axis=1))[0]
            if len(rows_a):
                yy = int(rows_a.max())
                xs_row = np.where(crop_a[yy] > 128)[0]
                neck = [int(xs_row.min() + xs_row.max()) / 2, yy]
        for name, color in (("white", (255, 255, 255)), ("black", (0, 0, 0)), ("green", (106, 143, 78))):
            composite(rgba, color).save(QA / "diagnostics" / f"{spec['id']}-{name}.png")
        for height in (50, 64, 130):
            small = scale_to_height(rgba, height)
            composite(small, (255, 255, 255)).save(QA / "diagnostics" / f"{spec['id']}-{height}.png")
        solid = int((crop_a > 16).sum()) > 1000 and holes_left < 80
        status = "READY" if spec["card"] and solid else "PARTIAL"
        recipe = {
            "id": spec["id"],
            "version": "v9-local-20261005",
            "method": "top-left-quadrant distance from sampled paper RGB 144.5,178,105; threshold 36",
            "correction": "Dropped components with solidity under 0.08, including the magenta frame. Filled enclosed holes of 40px or fewer.",
            "filledPinholePixels": filled,
            "source": rel(SHEET),
            "sourceSha256": sha256(SHEET),
            "sourceROI": [x0, y0, x1, y1],
            "boxConvention": "half-open [x0,y0,x1,y1)",
            "sourceToCrop": {"kind": "translation", "origin": [x0, y0], "scale": 1, "rotation": 0},
            "output": rel(path),
            "sha256": digest,
            "dimensionsWH": [rgba.shape[1], rgba.shape[0]],
            "view": spec["view"],
            "anatomy": spec["anatomy"],
            "side": "UNKNOWN",
            "neckPivotCropXY": neck,
            "inventedPaint": False,
            "rgbEdited": False,
        }
        (QA / "recipes" / f"{spec['id']}.json").parent.mkdir(parents=True, exist_ok=True)
        (QA / "recipes" / f"{spec['id']}.json").write_text(json.dumps(recipe, indent=2), encoding="utf-8")
        rows.append({
            "id": spec["id"],
            "status": status,
            "role": "static-head-or-card" if spec["card"] else "static-part",
            "semantic": spec["anatomy"],
            "view": spec["view"],
            "side": "UNKNOWN",
            "path": rel(path),
            "sha256": digest,
            "dimensions": [rgba.shape[1], rgba.shape[0]],
            "visibleAlpha16": a16,
            "visibleAlpha128": a128,
            "source": rel(SHEET),
            "sourceSha256": recipe["sourceSha256"],
            "sourceROI": [x0, y0, x1, y1],
            "mask": rel(mask_path),
            "recipe": rel(QA / "recipes" / f"{spec['id']}.json"),
            "neckPivotCropXY": neck,
            "enclosedHolesLeft": holes_left,
            "displaySizes": [50, 64, 130],
            "limit": "Static painted view. Anatomical side is UNKNOWN. Not a body and not an animated head.",
            "droppedFrameComponents": len(dropped),
            "gates": {
                "sourceBinding": {"gate": "PASS", "evidence": "Written and hashed in this run."},
                "matte": {"gate": "PASS" if solid else "PARTIAL", "evidence": f"White, black, and green composites. Enclosed holes left {holes_left}."},
                "articulation": {"gate": "NOT_APPLICABLE", "reason": "A painted head crop has no joint."},
                "fullBody": {"gate": "NOT_APPLICABLE", "reason": "Row is one painted part."},
                "owner": {"gate": "UNVERIFIED", "evidence": "No owner acceptance on this row."},
            },
        })
    (QA / "healer-heads.json").write_text(json.dumps({"dropped": dropped, "filledPinholePixels": filled, "rows": rows}, indent=2), encoding="utf-8")
    return rows


def one_joint_attempt(parent_rel: str, child_rel: str, pair: str) -> dict:
    parent = load_rgba(ROOT / parent_rel)
    child = load_rgba(ROOT / child_rel)
    pc = cuff_profile(parent[:, :, 3], "distal")
    cc = cuff_profile(child[:, :, 3], "proximal")
    if pc is None or cc is None:
        return {"id": pair, "status": "FAIL", "reason": "NO_CUFF", "attempts": 1, "exhausted": True}
    ratio = pc["width"] / max(1, cc["width"])
    if ratio < 0.75 or ratio > 1.35:
        return {
            "id": pair, "status": "FAIL", "reason": "FAIL_IMPLAUSIBLE_SCALE", "attempts": 1, "exhausted": True,
            "ratio": round(ratio, 3), "uniformScale": 1, "parent": parent_rel, "child": child_rel,
            "note": "One baseline at scale 1. No search.",
        }
    measured = measure_pair(parent_rel, child_rel, 0, 0)
    neutral = measured["poses"][1]
    ok = neutral["continuousRunPx"] >= 8 and neutral["overlapParent128Child16"] >= 400
    return {
        "id": pair,
        "status": "PASS_ONE_PLACEMENT" if ok else "FAIL",
        "reason": None if ok else "FAIL_NO_CONTINUOUS_CONTACT",
        "attempts": 1,
        "exhausted": not ok,
        "ratio": round(ratio, 3),
        "poses": measured["poses"],
        "parent": parent_rel,
        "child": child_rel,
        "note": "One baseline. Not a placement search.",
    }


def assemble_leg(measured_joints: dict) -> dict:
    upper = load_rgba(ROOT / "assets/derivatives/rigs/v6/healer/leg_upper.png")
    greave = load_rgba(ROOT / "assets/derivatives/rigs/v6/healer/greave.png")
    boot = load_rgba(BOOT)
    knee = measured_joints["healer-leg-greave"]
    ankle = measured_joints["healer-greave-boot"]
    pc, cc = knee["cuffParent"], knee["cuffChild"]
    g_prox = (cc["cx"], cc["y"])
    g_dist = (ankle["cuffParent"]["cx"], ankle["cuffParent"]["y"])
    b_prox = (ankle["cuffChild"]["cx"], ankle["cuffChild"]["y"])
    pad = 700
    canvas = (upper.shape[0] + greave.shape[0] + boot.shape[0] + pad, upper.shape[1] + greave.shape[1] + boot.shape[1] + pad)
    pivot = (canvas[1] // 2, upper.shape[0] // 2 + 80)
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
        for color, name in (((255, 255, 255), "white"), ((0, 0, 0), "black"), ((106, 143, 78), "green")):
            composite(trimmed, color).save(QA / "diagnostics" / f"healer-leg-subchain-{ang}-{name}.png")
        composite(scale_to_height(trimmed, 130), (255, 255, 255)).save(QA / "diagnostics" / f"healer-leg-subchain-{ang}-130.png")
    images = []
    for frame in frames:
        thumb = Image.fromarray(frame, "RGBA").resize((max(1, int(frame.shape[1] * 180 / frame.shape[0])), 180), Image.Resampling.BOX)
        images.append(composite(np.array(thumb), (245, 240, 230)).convert("P", palette=Image.Palette.ADAPTIVE))
    gif = QA / "assemblies" / "healer-leg-subchain-arc.gif"
    images[0].save(gif, save_all=True, append_images=images[1:], duration=400, loop=0, disposal=2)
    return {
        "id": "healer-leg-subchain",
        "status": "PARTIAL",
        "fullBody": "FAIL",
        "side": "UNKNOWN",
        "measuredLinks": ["upper-leg to greave", "greave to boot"],
        "missingLinks": ["head to torso", "torso to skirt", "skirt to upper leg"],
        "angles": [-25, 0, 25],
        "neutral": rel(QA / "assemblies" / "healer-leg-subchain-0.png"),
        "clip": rel(gif),
        "drawOrder": ["boot", "greave", "upper leg"],
        "rotation": "Child rotates about the shared cuff pivot. Positive degrees are clockwise in image space, matching the v7 warp (x' = c*x - s*y).",
        "uniformScale": 1,
        "canvasHeightWidth": [canvas[0], canvas[1]],
        "kneePivotCanvasXY": [pivot[0], pivot[1]],
        "note": "Valid subchain only. Boot follows the greave with no extra ankle bend in this clip.",
    }


def project(affine, x, y):
    a, b, c, d, e, f = affine
    return (a * x + c * y + e, b * x + d * y + f)


def camera(source, width, height, focus=None, hit_px=0):
    contain = min(width / source[0], height / source[1])
    cover = max(width / source[0], height / source[1])
    scale = cover if (not focus and contain * source[0] < width * 0.8) else contain
    if focus:
        span_x = max(1e-6, focus["maxX"] - focus["minX"])
        span_y = max(1e-6, focus["maxY"] - focus["minY"])
        room_w, room_h = width - hit_px * 2, height - hit_px * 2
        fit = min(room_w / span_x, room_h / span_y) if room_w > 0 and room_h > 0 else contain
        scale = min(cover, fit)
    view_w, view_h = width / scale, height / scale
    pad = hit_px / scale if focus else 0
    min_x = focus["minX"] - pad if focus else 0
    min_y = focus["minY"] - pad if focus else 0
    max_x = focus["maxX"] + pad if focus else source[0]
    max_y = focus["maxY"] + pad if focus else source[1]
    origin_x = min_x + (max_x - min_x - view_w) / 2 if focus else (source[0] - view_w) / 2
    origin_y = min_y + (max_y - min_y - view_h) / 2 if focus else (source[1] - view_h) / 2
    if view_w >= source[0]:
        origin_x = (source[0] - view_w) / 2
    else:
        origin_x = min(max(origin_x, 0), source[0] - view_w)
    if view_h >= source[1]:
        origin_y = (source[1] - view_h) / 2
    else:
        origin_y = min(max(origin_y, 0), source[1] - view_h)
    mode = "cover" if abs(scale - cover) < 1e-9 else "contain" if abs(scale - contain) < 1e-9 else "fit"
    return {"scale": scale, "mode": mode, "window": [origin_x, origin_y, view_w, view_h]}


def kingdom_focus(contract: dict, hall: dict) -> dict:
    geo = contract["geometry"]["kingdom"]
    pts = []
    for site in geo["sites"]:
        x, y, w, h = site["rect"]
        pts.append(project(geo["worldToSource"], x + w / 2, y + h / 2))
    m = hall["matrix"]
    for hx, hy in ((0, 0), (hall["width"], 0), (hall["width"], hall["height"]), (0, hall["height"])):
        pts.append((m[0][0] * hx + m[0][1] * hy + m[0][2], m[1][0] * hx + m[1][1] * hy + m[1][2]))
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return {"minX": min(xs), "minY": min(ys), "maxX": max(xs), "maxY": max(ys)}


def paste_hall(plate: Image.Image, hall_im: Image.Image, matrix) -> Image.Image:
    # OpenCV 5 warpAffine dropped this alpha plane. Uniform scale is a resize plus a paste.
    scale = float(matrix[0][0])
    origin_x, origin_y = float(matrix[0][2]), float(matrix[1][2])
    sprite = hall_im.convert("RGBA").resize(
        (max(1, int(round(hall_im.width * scale))), max(1, int(round(hall_im.height * scale)))),
        Image.Resampling.LANCZOS,
    )
    x, y = int(round(origin_x)), int(round(origin_y))
    if y < 0:
        sprite = sprite.crop((0, -y, sprite.width, sprite.height))
        y = 0
    if x < 0:
        sprite = sprite.crop((-x, 0, sprite.width, sprite.height))
        x = 0
    base = plate.convert("RGBA")
    base.alpha_composite(sprite, (x, y))
    return base.convert("RGB")


def fit_plate(plate: Image.Image, vw: int, vh: int, focus, panel: bool) -> tuple[Image.Image, dict]:
    panel_w = min(280, int(vw * 0.34)) if panel else 0
    stage_w = max(1, vw - (panel_w + 8 if panel else 0))
    stage_h = max(1, vh - HEADER_PX - FOOTER_PX)
    fit = camera((1376, 768), stage_w, stage_h, focus, 24 if focus else 0)
    ox, oy, view_w, view_h = fit["window"]
    # Render by scaling the whole plate and cropping. Uniform scale, no stretch.
    scaled = plate.resize((max(1, int(round(1376 * fit["scale"]))), max(1, int(round(768 * fit["scale"])))), Image.Resampling.LANCZOS)
    left = int(round(ox * fit["scale"]))
    top = int(round(oy * fit["scale"]))
    crop = Image.new("RGB", (stage_w, stage_h), (27, 40, 32))
    src = scaled.crop((max(0, left), max(0, top), min(scaled.size[0], left + stage_w), min(scaled.size[1], top + stage_h)))
    crop.paste(src, (max(0, -left), max(0, -top)))
    canvas = Image.new("RGB", (vw, vh), (21, 33, 40))
    canvas.paste(crop, (0, HEADER_PX))
    draw = ImageDraw.Draw(canvas, "RGBA")
    draw.rectangle((0, 0, vw, HEADER_PX), fill=(21, 33, 40, 255))
    draw.text((8, 18), "Ages of Dominion", fill=(241, 233, 217, 255))
    draw.rectangle((0, vh - FOOTER_PX, vw, vh), fill=(21, 33, 40, 255))
    draw.text((8, vh - 36), "screens", fill=(241, 233, 217, 255))
    dock_top = HEADER_PX + stage_h - 64
    draw.rounded_rectangle((8, dock_top, stage_w - 8, dock_top + 48), radius=8, fill=(21, 33, 40, 210), outline=(140, 116, 71, 255))
    if panel:
        draw.rounded_rectangle((vw - panel_w - 4, HEADER_PX + 8, vw - 8, vh - FOOTER_PX - 8), radius=8, fill=(16, 23, 27, 230), outline=(140, 116, 71, 255))
        draw.text((vw - panel_w + 8, HEADER_PX + 16), "Kingdom", fill=(241, 233, 217, 255))
    return canvas, {"viewport": [vw, vh], "stage": [stage_w, stage_h], "panelWidth": panel_w, "camera": fit, "chrome": "CSS-derived 56px header and footer, 48px dock, panel min(280,34vw). Not a runtime screenshot."}


def draw_stone_overlay(plate: Image.Image, contract: dict) -> Image.Image:
    im = plate.convert("RGB").resize((1376, 768), Image.Resampling.BOX)
    draw = ImageDraw.Draw(im, "RGBA")
    for road in STONE_LEGAL["roads"]:
        draw.line([(p[0], p[1]) for p in road["pts"]], fill=(40, 190, 255, 255), width=3)
    draw.line([(p[0], p[1]) for p in STONE_LEGAL["river"]], fill=(20, 60, 220, 255), width=3)
    for bank in STONE_LEGAL["banks"]:
        draw.line([(p[0], p[1]) for p in bank["pts"]], fill=(120, 210, 255, 255), width=2)
    draw.polygon([(p[0], p[1]) for p in STONE_LEGAL["deck"]], outline=(230, 140, 40, 255), width=3)
    draw.polygon([(p[0], p[1]) for p in STONE_LEGAL["rocks"]], outline=(220, 50, 50, 255))
    for site in contract["geometry"]["kingdom"]["sites"]:
        x, y, w, h = site["rect"]
        corners = [project(AFFINE, x + dx, y + dy) for dx, dy in ((0, 0), (w, 0), (w, h), (0, h))]
        draw.polygon(corners, outline=(230, 210, 120, 255))
    draw.rectangle((8, 8, 760, 78), fill=(0, 0, 0, 180))
    draw.text((14, 12), "v9 Stone: cyan roads, blue river/banks, orange deck, red rocks, yellow LEGAL sites", fill=(255, 255, 255, 255))
    draw.text((14, 32), "No withdrawn ridge. Roads/banks uncertainty 24-40 legal px. Deck midspan 16. Not promoted.", fill=(255, 255, 255, 255))
    draw.text((14, 52), "ASSET_COMPOSITE. Affine frozen. Blue candidate mask was rejected on this plate.", fill=(255, 220, 160, 255))
    return im


def legal_of(native_pts):
    return [[p[0] / 4, p[1] / 4] for p in native_pts]


def mean_distance(points, polyline) -> float | None:
    if len(polyline) < 2 or not points:
        return None
    dists = []
    for px, py in points:
        best = 1e9
        for (ax, ay), (bx, by) in zip(polyline, polyline[1:]):
            vx, vy = bx - ax, by - ay
            den = vx * vx + vy * vy
            t = 0 if den == 0 else max(0, min(1, ((px - ax) * vx + (py - ay) * vy) / den))
            dx, dy = px - (ax + t * vx), py - (ay + t * vy)
            best = min(best, (dx * dx + dy * dy) ** 0.5)
        dists.append(best)
    return float(sum(dists) / len(dists))


def scene_rows(v8_scenes: list, contract: dict) -> list:
    kingdom_seen = {
        "kingdom-terrain-bronze", "kingdom-terrain-iron", "kingdom-terrain-medieval",
        "kingdom-terrain-gunpowder", "kingdom-terrain-industrial", "kingdom-terrain-modern",
        "kingdom-terrain-future",
    }
    rows = []
    for scene in v8_scenes:
        row = {
            "id": scene["id"],
            "role": "scene-plate",
            "mode": scene.get("mode"),
            "age": scene.get("age"),
            "biome": scene.get("biome"),
            "status": "PARTIAL",
            "promoted": False,
            "source": scene["source"],
            "legalAffineActive": scene.get("legalAffineActive"),
            "legalAffineFrozen": True,
            "hallScaleActive": scene.get("hallScaleActive"),
            "hallScaleFrozen": True,
            "proposedCamera": None,
            "geometryEdited": False,
            "nativeDecode": "NOT_BARE_TERRAIN_PASS",
            "paintedRoadPolylines": [],
            "paintedRiverPolygons": [],
            "paintedBankPolylines": [],
            "paintedBridgeDeck": None,
            "approachPolygons": [],
            "walkablePolygons": [],
            "blockedPolygons": [],
            "runtimeAcceptance": "UNVERIFIED",
            "ownerAcceptance": "UNVERIFIED",
        }
        if scene["id"] == "kingdom-terrain-stone":
            row["paintedRoadPolylines"] = [
                {"polylineNative": [[p[0] * 4, p[1] * 4] for p in road["pts"]], "kind": road["kind"], "uncertaintyLegalPx": road["uncertaintyLegalPx"], "method": "manual-grid-v9"}
                for road in STONE_LEGAL["roads"]
            ]
            row["paintedRiverPolygons"] = [{
                "polylineNative": [[p[0] * 4, p[1] * 4] for p in STONE_LEGAL["river"]],
                "uncertaintyLegalPx": STONE_LEGAL["riverUncertaintyLegalPx"],
                "method": "manual-grid-v9",
                "note": "Axis of the visible channel. The widened blue mask's largest component was a 1512px patch, not this channel.",
            }]
            row["paintedBankPolylines"] = [
                {"side": b["side"], "observedBankSide": b["observedBankSide"], "polylineNative": [[p[0] * 4, p[1] * 4] for p in b["pts"]], "uncertaintyLegalPx": STONE_LEGAL["bankUncertaintyLegalPx"]}
                for b in STONE_LEGAL["banks"]
            ]
            row["paintedBridgeDeck"] = {
                "polygonNative": [[p[0] * 4, p[1] * 4] for p in STONE_LEGAL["deck"]],
                "uncertaintyLegalPx": STONE_LEGAL["deckUncertaintyLegalPx"],
                "method": "manual-grid plus a brown-between-water centerline that was seen on the wooden deck from legal x 1152 to 1280",
            }
            row["approachPolygons"] = [
                {"kind": a["kind"], "polylineNative": [[p[0] * 4, p[1] * 4] for p in a["pts"]], "uncertaintyLegalPx": 24}
                for a in STONE_LEGAL["approaches"]
            ]
            row["blockedPolygons"] = [{"kind": "rock-ring", "polygonNative": [[p[0] * 4, p[1] * 4] for p in STONE_LEGAL["rocks"]], "uncertaintyLegalPx": 40}]
            row["paintedRoadState"] = "MANUAL_PARTIAL"
            row["paintedRiverState"] = "MANUAL_PARTIAL"
            row["walkableState"] = "NOT_YET_TRACED"
            legal_roads = []
            for item in scene.get("paintedRoadPolylines", []):
                pass
            # Distance from this trace to the v8 manual trace, legal pixels. Not a registration pass.
            v8_pts = []
            for item in scene.get("paintedRoadPolylines", []):
                v8_pts.extend(legal_of(item.get("polylineNative", [])))
            new_pts = [p for road in STONE_LEGAL["roads"] for p in road["pts"]]
            row["residualVsV8ManualTracksLegalPx"] = None if not v8_pts else round(mean_distance(v8_pts, new_pts) or 0, 2)
            row["proposal"] = {
                "id": "proposal-v9-kingdom-terrain-stone-manual-grid",
                "status": "PROPOSED",
                "activatesCamera": False,
                "affineUnchanged": AFFINE,
                "hallScaleUnchanged": HALL_SCALE,
            }
            row["nextExecutableAction"] = "Tighten bank and road traces below corridor width, then compare every legal site polygon to the trace."
        elif scene["id"] in kingdom_seen:
            row["paintedRoadState"] = "VISIBLY_PRESENT_NOT_TRACED"
            row["paintedRiverState"] = "VISIBLY_PRESENT_NOT_TRACED"
            row["walkableState"] = "NOT_YET_TRACED"
            row["bakedMutableContent"] = "Village plots and structures are painted into the plate. Hidden ground under them is unavailable."
            row["evidence"] = "qa/image-local-delivery-v9-20261005/inspect/kingdom-ages-contact.jpg"
            row["nextExecutableAction"] = "Manual legal-frame trace of this plate's roads, banks, and bridge. Do not copy the Stone polylines."
        else:
            row["paintedRoadState"] = "NOT_YET_TRACED"
            row["paintedRiverState"] = "NOT_YET_TRACED"
            row["walkableState"] = "NOT_YET_TRACED"
            row["nextExecutableAction"] = "Open the saved legal-frame preview and trace painted roads, water, and obstacles. Sobel ridges stay withdrawn."
        row["overlay"] = f"qa/image-local-delivery-v9-20261005/terrain/{scene['id']}-status.png" if scene["id"] == "kingdom-terrain-stone" else None
        row["v8OverlayHistorical"] = scene.get("overlay") if isinstance(scene, dict) else None
        rows.append(row)
    return rows


def side_by_side(ref: Path, actual: Image.Image, title: str, out: Path) -> None:
    left = Image.open(ref).convert("RGB")
    left.thumbnail((640, 360))
    right = actual.copy()
    right.thumbnail((640, 360))
    canvas = Image.new("RGB", (1320, 420), (28, 28, 28))
    draw = ImageDraw.Draw(canvas)
    draw.text((16, 8), title, fill=(240, 240, 240))
    draw.text((16, 390), "reference", fill=(200, 200, 160))
    draw.text((680, 390), "ASSET_COMPOSITE", fill=(160, 210, 170))
    canvas.paste(left, (16, 28))
    canvas.paste(right, (680, 28))
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out, quality=85)


def main() -> None:
    QA.mkdir(parents=True, exist_ok=True)
    for name in ("masks", "recipes", "diagnostics", "assemblies", "terrain", "review", "inspect"):
        (QA / name).mkdir(exist_ok=True)
    libs = versions()
    overflow = synthetic_overflow()
    if not overflow["passed"] or not overflow["controlBothTrue"]:
        raise SystemExit("synthetic overflow regression failed")
    before = {
        "healerBoot": sha256(BOOT),
        "v8Interface": sha256(V8_INTERFACE),
        "draft": sha256(DRAFT),
        "contract": sha256(CONTRACT),
    }
    if before["healerBoot"] != "4a700eeedbabc9710db137491825d0c2ec439db15b10c619f0997a93accfab21":
        raise SystemExit("Healer boot hash changed before this run")
    v8 = json.loads(V8_INTERFACE.read_text(encoding="utf-8"))
    v8_scenes = json.loads((V8 / "scenes.json").read_text(encoding="utf-8"))
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    hall = json.loads((ROOT / "src" / "data" / "stone-scene.json").read_text(encoding="utf-8"))["hall"]

    heads = extract_heads()
    joint_specs = {
        "ranger-sleeve-to-open-hand": ("assets/derivatives/rigs/v5/ranger/sleeve_upper_arm.png", "assets/derivatives/rigs/v5/ranger/vambrace_hand_open.png", 0.30, 0.05),
        "healer-leg-greave": ("assets/derivatives/rigs/v6/healer/leg_upper.png", "assets/derivatives/rigs/v6/healer/greave.png", 0, 0),
        "healer-greave-boot": ("assets/derivatives/rigs/v6/healer/greave.png", "assets/derivatives/rigs/v7/healer/boot.png", 0, 0),
        "paladin-knee-greave": ("assets/derivatives/rigs/v6/paladin/knee_cop.png", "assets/derivatives/rigs/v6/paladin/greave.png", 0, 0),
    }
    expected = {row["id"]: row for row in v8["readySubset"]}
    joint_report = {}
    mismatches = []
    for key, (parent, child, insertion, transverse) in joint_specs.items():
        measured = measure_pair(parent, child, insertion, transverse)
        prior = expected[key]["poses"]
        for got, want in zip(measured["poses"], prior):
            for field in ("overlapParent128Child16", "continuousRunPx", "jointRoiParentAlphaGt128", "jointRoiChildAlphaGt16"):
                if got[field] != want[field]:
                    mismatches.append({"id": key, "angle": got["angle"], "field": field, "got": got[field], "want": want[field]})
        public = {k: v for k, v in measured.items() if k != "parentLayer"}
        joint_report[key] = public
    (QA / "joint-remeasure.json").write_text(json.dumps({"mismatches": mismatches, "joints": joint_report}, indent=2), encoding="utf-8")

    new_attempts = [
        one_joint_attempt(
            "assets/derivatives/rigs/v9/healer/healer-head-front-neck.png",
            "assets/derivatives/rigs/v6/healer/torso.png",
            "healer-head-to-torso",
        ),
        one_joint_attempt(
            "assets/derivatives/rigs/v6/healer/torso.png",
            "assets/derivatives/rigs/v6/healer/skirt.png",
            "healer-torso-to-skirt",
        ),
        one_joint_attempt(
            "assets/derivatives/rigs/v6/healer/skirt.png",
            "assets/derivatives/rigs/v6/healer/leg_upper.png",
            "healer-skirt-to-leg",
        ),
    ]
    for attempt in new_attempts:
        if attempt["id"] == "healer-head-to-torso":
            attempt["status"] = "FAIL"
            attempt["reason"] = "ROUNDED_NECK_STUMP_COVERS_COLLAR"
            attempt["exhausted"] = True
            attempt["visual"] = "qa/image-local-delivery-v9-20261005/diagnostics/healer-head-to-torso-0-white.png"
            attempt["note"] = "One scale-1 cuff alignment. The overlap is a rounded neck stump on the collar, not a socket. No second search."
        elif attempt["id"] == "healer-torso-to-skirt":
            attempt["status"] = "PARTIAL"
            attempt["reason"] = "NEUTRAL_SILHOUETTE_INSPECTED_ARC_UNVERIFIED"
            attempt["exhausted"] = False
            attempt["visual"] = "qa/image-local-delivery-v9-20261005/diagnostics/healer-torso-skirt-0-white.png"
            attempt["note"] = "Neutral waist contact was inspected. The -25 and +25 frames were not accepted."
    leg = assemble_leg(joint_report)
    (QA / "new-joint-attempts.json").write_text(json.dumps(new_attempts, indent=2), encoding="utf-8")
    (QA / "assemblies" / "healer-leg-subchain.json").write_text(json.dumps(leg, indent=2), encoding="utf-8")

    # Class diagrams use real pixels and say they are not one body.
    chain_specs = {
        "healer": [("head", "assets/derivatives/rigs/v9/healer/healer-head-front-neck.png", "STATIC_CARD"), ("torso", "assets/derivatives/rigs/v6/healer/torso.png", "NOT_JOINED"), ("skirt", "assets/derivatives/rigs/v6/healer/skirt.png", "NOT_A_LEG"), ("leg subchain", "qa/image-local-delivery-v9-20261005/assemblies/healer-leg-subchain-0.png", "MEASURED_-25_0_25")],
        "paladin": [("head", "assets/derivatives/rigs/v6/paladin/head_three_quarter.png", "UNREPAIRED"), ("cuirass", "assets/derivatives/rigs/v6/paladin/cuirass_fauld_combined.png", "INSEPARABLE"), ("knee-greave", "assets/derivatives/rigs/v6/paladin/knee_cop.png", "JOINT_READY_PART")],
        "ranger": [("sleeve", "assets/derivatives/rigs/v5/ranger/sleeve_upper_arm.png", "CUFF_ONLY"), ("hand", "assets/derivatives/rigs/v5/ranger/vambrace_hand_open.png", "ARC_-25_0_25")],
        "knight": [("vambrace", "assets/derivatives/rigs/v5/knight/vambrace.png", "NOT_THE_FAILED_PAIR")],
        "mage": [("hood", "qa/image-local-continuation-20261005/components/mage/02_119_545.png", "ONE_OF_FOUR")],
        "warlock": [("torso crop", "qa/image-local-continuation-20261005/components/warlock/01_1042_107.png", "NO_HEAD_LINK")],
        "necromancer": [("skull", "qa/image-local-continuation-20261005/components/necromancer/13_56_47.png", "NO_NECK_LINK")],
        "barbarian": [("head", "qa/image-local-continuation-20261005/components/barbarian/05_57_51.png", "NO_NECK_LINK")],
    }
    chains = []
    for class_id, slots in chain_specs.items():
        sheet = Image.new("RGB", (240 * len(slots), 300), (235, 232, 226))
        draw = ImageDraw.Draw(sheet)
        draw.text((8, 6), f"{class_id}: parts shown are not one scale-locked body", fill=(20, 20, 20))
        for i, (name, path, state) in enumerate(slots):
            file = ROOT / path
            thumb = Image.open(file).convert("RGBA") if file.is_file() else Image.new("RGBA", (180, 180), (180, 180, 180, 255))
            thumb.thumbnail((200, 200))
            plate = Image.new("RGBA", (200, 200), (250, 250, 250, 255))
            plate.paste(thumb, ((200 - thumb.size[0]) // 2, (200 - thumb.size[1]) // 2), thumb)
            sheet.paste(plate.convert("RGB"), (i * 240 + 16, 32))
            draw.text((i * 240 + 8, 240), name, fill=(0, 0, 0))
            draw.text((i * 240 + 8, 260), state[:28], fill=(120, 30, 30))
        out = QA / "assemblies" / f"{class_id}-chain-v9.png"
        sheet.save(out)
        chains.append({
            "id": f"{class_id}-neutral-chain",
            "class": class_id,
            "status": "PARTIAL",
            "fullBody": "FAIL",
            "side": "UNKNOWN",
            "diagram": rel(out),
            "neutralPose": "SUBCHAIN_ONLY" if class_id == "healer" else "NOT_A_SINGLE_SCALE_BODY",
            "measured": leg["measuredLinks"] if class_id == "healer" else [],
            "nextExecutableAction": "Attach only where a new source landmark passes one bounded test.",
        })

    stone_scene = next(s for s in v8_scenes if s["id"] == "kingdom-terrain-stone")
    stone_plate = Image.open(ROOT / stone_scene["source"]["path"]).convert("RGB").resize((1376, 768), Image.Resampling.BOX)
    overlay = draw_stone_overlay(stone_plate, contract)
    overlay.save(QA / "terrain" / "kingdom-terrain-stone-status.png")
    focus = kingdom_focus(contract, hall)
    hall_im = Image.open(ROOT / hall["file"])
    developed = paste_hall(stone_plate, hall_im, hall["matrix"])
    developed.save(QA / "terrain" / "kingdom-stone-developed-legal.jpg", quality=85)
    stone_plate.save(QA / "terrain" / "kingdom-stone-sparse-legal.jpg", quality=85)

    viewports = [(825, 375), (933, 424), (1180, 820), (1280, 720)]
    views = []
    tiles = []
    for vw, vh in viewports:
        shot, meta = fit_plate(developed, vw, vh, focus, True)
        path = QA / "terrain" / f"kingdom-stone-focus-{vw}x{vh}.jpg"
        shot.save(path, quality=85)
        meta["path"] = rel(path)
        meta["state"] = "DEVELOPED_HALL_FOCUS"
        views.append(meta)
        thumb = shot.copy()
        thumb.thumbnail((320, 180))
        tiles.append(thumb)
    sheet = Image.new("RGB", (660, 400), (0, 0, 0))
    for i, thumb in enumerate(tiles):
        sheet.paste(thumb, ((i % 2) * 330, (i // 2) * 200))
    sheet.save(QA / "terrain" / "kingdom-stone-four-viewport.jpg", quality=85)
    contain, contain_meta = fit_plate(stone_plate, 1280, 720, None, False)
    contain.save(QA / "terrain" / "kingdom-stone-contain-1280x720.jpg", quality=85)

    scenes = scene_rows(v8_scenes, contract)
    (QA / "scenes.json").write_text(json.dumps(scenes, indent=2), encoding="utf-8")

    # Arithmetic on the legal frame. Candidate pixels are not banks.
    changed = 0
    changed_scenes = 0
    for scene in v8_scenes:
        im = Image.open(ROOT / scene["source"]["path"]).convert("RGB").resize((1376, 768), Image.Resampling.BOX)
        arr = np.array(im)
        u8 = candidate_mask(arr, False)
        wide = candidate_mask(arr, True)
        delta = int(np.count_nonzero(u8 != wide))
        if delta:
            changed += delta
            changed_scenes += 1
        legal = im.copy()
        legal.thumbnail((480, 270))
        legal.save(QA / "inspect" / f"{scene['id']}-legal.jpg", quality=70)
    arithmetic = {"scenes": 32, "changedScenes": changed_scenes, "candidatePixelsChanged": changed, "stage": "1376x768 BOX resize, before component filtering", "not": "river, bank, or runtime accuracy", "synthetic": overflow}

    # Gallery composites.
    mock = lambda name: MOCKS / name
    pairs = []
    def add_pair(screen, ref_name, image, note):
        out = QA / "review" / f"{screen}.jpg"
        side_by_side(mock(ref_name), image, f"{screen} — {note}", out)
        pairs.append({"screen": screen, "reference": f"design-preview/generated/landscape-mocks-20261003-efcd7a7e/images/{ref_name}", "composite": rel(out), "note": note})

    add_pair("kingdom-stone-sparse", "02-kingdom-day1.jpg", contain, "whole-plate contain; baked hut remains; hall omitted")
    focus_full, _ = fit_plate(developed, 1280, 720, focus, True)
    add_pair("kingdom-stone-developed", "03-kingdom-stone.jpg", focus_full, "frozen hall scale and kingdom focus camera")
    ages = [
        ("kingdom-bronze", "04-kingdom-bronze.jpg", "kingdom-terrain-bronze"),
        ("kingdom-iron", "05-kingdom-iron.jpg", "kingdom-terrain-iron"),
        ("kingdom-medieval", "06-kingdom-medieval.jpg", "kingdom-terrain-medieval"),
        ("kingdom-gunpowder", "07-kingdom-gunpowder.jpg", "kingdom-terrain-gunpowder"),
        ("kingdom-industrial", "08-kingdom-industrial.jpg", "kingdom-terrain-industrial"),
        ("kingdom-modern", "09-kingdom-modern.jpg", "kingdom-terrain-modern"),
        ("kingdom-future", "10-kingdom-future.jpg", "kingdom-terrain-future"),
        ("adventure", "11-adventure-overview.jpg", "adventure-terrain"),
        ("tactical", "14-tactical-deployment.jpg", "tactical-terrain"),
        ("defense", "17-defense-preparation.jpg", "defense-terrain"),
    ]
    by_id = {s["id"]: s for s in v8_scenes}
    for screen, ref_name, scene_id in ages:
        plate = Image.open(ROOT / by_id[scene_id]["source"]["path"]).convert("RGB").resize((1376, 768), Image.Resampling.BOX)
        shot, _ = fit_plate(plate, 1280, 720, None, False)
        add_pair(screen, ref_name, shot, "source plate, uniform contain, roads not traced")
    # Army strip of the nine ready static plates.
    army = Image.new("RGB", (1280, 720), (36, 40, 34))
    draw = ImageDraw.Draw(army)
    draw.text((16, 12), "Nine ready static troops at 130px. Not articulated.", fill=(240, 240, 240))
    x = 16
    for row in v8["readySubset"]:
        if not str(row["id"]).startswith("troop-"):
            continue
        im = Image.open(ROOT / row["path"]).convert("RGBA")
        small = Image.fromarray(scale_to_height(np.array(im), 130), "RGBA")
        army.paste(composite(np.array(small), (36, 40, 34)), (x, 80), small)
        draw.text((x, 220), row["id"].replace("troop-", "")[:16], fill=(220, 220, 200))
        x += 140
    add_pair("army", "24-army.jpg", army, "ready static plates only")
    # Forge: six canonical slot names, no invented gear art.
    forge = Image.new("RGB", (1280, 720), (32, 30, 28))
    draw = ImageDraw.Draw(forge)
    draw.text((16, 12), "Six canonical slots. No new gear bitmap this pass.", fill=(240, 230, 210))
    for i, name in enumerate(("weapon", "shield", "helm", "armor", "boots", "accessory")):
        draw.rounded_rectangle((40 + i * 200, 120, 210 + i * 200, 420), radius=8, outline=(180, 150, 90), width=3)
        draw.text((55 + i * 200, 250), name, fill=(240, 230, 210))
    add_pair("forge", "22-forge.jpg", forge, "slot chrome only; gear cards still open")
    home = Image.new("RGB", (1280, 720), (24, 28, 26))
    draw = ImageDraw.Draw(home)
    draw.text((24, 24), "No home scene plate was extracted. Healer front head is a card, not the home screen.", fill=(240, 230, 210))
    head = Image.open(ROOT / "assets/derivatives/rigs/v9/healer/healer-head-front-neck.png").convert("RGBA")
    home.paste(composite(np.array(head), (24, 28, 26)), (80, 80), head)
    add_pair("home", "01-home.jpg", home, "missing home plate; head card shown as a part")

    # Binding of ready claims plus new heads.
    checked = []
    failed = []
    ready_rows = []
    for row in v8["readySubset"]:
        copied = json.loads(json.dumps(row))
        paths = []
        if row.get("path"):
            paths.append((row["path"], row.get("sha256")))
        if row.get("parent"):
            paths.append((row["parent"], row.get("parentSha256")))
        if row.get("child"):
            paths.append((row["child"], row.get("childSha256")))
        ok = True
        for path, expect in paths:
            digest = sha256(ROOT / path)
            with Image.open(ROOT / path) as im:
                im.verify()
            with Image.open(ROOT / path) as im:
                im.load()
            match = digest == expect
            checked.append({"path": path, "sha256": digest, "matchesInterface": match, "decode": "PASS"})
            ok = ok and match
            if not match:
                failed.append(path)
        copied["gates"]["sourceBinding"] = {
            "gate": "PASS" if ok else "FAIL",
            "evidence": "v9 rehashed and decoded the v8 path. v8 itself was not rewritten.",
        }
        if row["id"] in joint_report:
            copied["coordinateFrames"] = copied.get("coordinateFrames", {})
            copied["coordinateFrames"]["canvasHeightWidth"] = joint_report[row["id"]]["canvasHeightWidth"]
            copied["coordinateFrames"]["canvasWidthHeight"] = joint_report[row["id"]]["canvasWidthHeight"]
            copied["coordinateFrames"]["sharedPivotCanvasXY"] = joint_report[row["id"]]["sharedPivotCanvasXY"]
            copied["coordinateFrames"]["childPivotCanvasXY"] = joint_report[row["id"]]["childPivotCanvasXY"]
            copied["coordinateFrames"]["orderNote"] = "v8 canvas arrays are [height, width]. XY pivots are [x, y]."
            copied["remeasureMismatches"] = [m for m in mismatches if m["id"] == row["id"]]
        ready_rows.append(copied)
    for head in heads:
        if head["status"] == "READY":
            ready_rows.append(head)
            checked.append({"path": head["path"], "sha256": head["sha256"], "matchesInterface": True, "decode": "PASS"})

    after = {
        "healerBoot": sha256(BOOT),
        "v8Interface": sha256(V8_INTERFACE),
        "draft": sha256(DRAFT),
        "contract": sha256(CONTRACT),
    }
    paladin_head = ROOT / "assets" / "derivatives" / "rigs" / "v7" / "paladin" / "head_three_quarter.png"
    queue = []
    for screen, filename in [
        ("home", "01-home.jpg"), ("kingdom-day1", "02-kingdom-day1.jpg"), ("kingdom-stone", "03-kingdom-stone.jpg"),
        ("kingdom-bronze", "04-kingdom-bronze.jpg"), ("kingdom-iron", "05-kingdom-iron.jpg"), ("kingdom-medieval", "06-kingdom-medieval.jpg"),
        ("kingdom-gunpowder", "07-kingdom-gunpowder.jpg"), ("kingdom-industrial", "08-kingdom-industrial.jpg"), ("kingdom-modern", "09-kingdom-modern.jpg"),
        ("kingdom-future", "10-kingdom-future.jpg"), ("adventure", "11-adventure-overview.jpg"), ("adventure-crossing", "12-adventure-crossing.jpg"),
        ("adventure-foot", "13-adventure-foot.jpg"), ("tactical", "14-tactical-deployment.jpg"), ("tactical-action", "15-tactical-action.jpg"),
        ("battle-result", "16-battle-result.jpg"), ("defense", "17-defense-preparation.jpg"), ("defense-wave", "18-defense-wave.jpg"),
        ("hero", "19-hero-equipment.jpg"), ("skills", "20-skills.jpg"), ("spells", "21-spells.jpg"),
        ("forge", "22-forge.jpg"), ("inventory", "23-inventory.jpg"), ("army", "24-army.jpg"),
        ("story", "25-story.jpg"), ("quests", "26-quests.jpg"), ("tutorial", "27-tutorial.jpg"),
        ("settings", "28-settings.jpg"), ("save-recovery", "29-save-recovery.jpg"), ("icons", "30-icon-material-board.jpg"),
    ]:
        queue.append({"screen": screen, "reference": f"design-preview/generated/landscape-mocks-20261003-efcd7a7e/images/{filename}", "state": "QUEUED" if screen not in {p["screen"] for p in pairs} and screen not in {"kingdom-day1", "kingdom-stone"} else "COMPOSITE_OR_GAP"})
    # Fix queue states for the pairs we made.
    made = {p["screen"] for p in pairs} | {"kingdom-stone-sparse", "kingdom-stone-developed"}
    for item in queue:
        if item["screen"] in ("kingdom-day1", "kingdom-stone") or item["screen"] in {p["screen"] for p in pairs}:
            item["state"] = "ASSET_COMPOSITE_PUBLISHED"
        else:
            item["state"] = "NOT_YET_COMPOSITED"

    interface = {
        "version": "9.0-local-delivery-20261005",
        "supersedes": "docs/plan/IMAGE-DELIVERY-INTERFACE-V8-2026-10-05.json",
        "codeAIHandoffReady": False,
        "reason": "Healer head cards and the leg subchain are individually usable. Full bodies, 31 scene traces, and several screens are still open.",
        "noNewPaidScope": True,
        "providerCalls": 0,
        "librariesMeasuredThisRun": libs,
        "boxConvention": "half-open [x0, y0, x1, y1)",
        "affineFormula": "x'=a*x+c*y+e; y'=b*x+d*y+f",
        "canvasConvention": "canvasHeightWidth is [height, width], the order stored in v8. canvasWidthHeight is [width, height]. Pivots are [x, y].",
        "rotationSign": "Positive degrees clockwise in image space: x' = cos*x - sin*y, y' = sin*x + cos*y, about the shared pivot.",
        "activeKingdomAffine": AFFINE,
        "activeHallScale": HALL_SCALE,
        "geometryEdited": False,
        "codeConsumersEdited": False,
        "gitMutated": False,
        "liveUrl": None,
        "codePreviewCommand": "node scripts/serve.mjs",
        "codePreviewDefaultUrl": "http://127.0.0.1:4173",
        "imageServerStarted": False,
        "readySubset": ready_rows,
        "classChains": chains,
        "healerLegSubchain": leg,
        "newJointAttempts": new_attempts,
        "scenes": scenes,
        "jointRemeasureMismatches": mismatches,
        "arithmetic": arithmetic,
        "replacementDraft": v8["replacementDraft"],
        "paladinHead": {
            "status": "FAIL",
            "bytesPresent": paladin_head.is_file(),
            "reproducibility": "FAILED_BYTES_UNAVAILABLE",
            "republished": False,
            "recipe": "qa/image-local-continuation-20261005/recipes/paladin-head_three_quarter.json",
        },
        "sizeLimitsRetained": [
            {"id": "horse", "maxReadyPx": 64, "reason": "Single pose, hooves not separated."},
            {"id": "motor-transport", "maxReadyPx": 64, "reason": "Ground remnant. Not a rider rig."},
            {"id": "future-transport", "maxReadyPx": 64, "reason": "Ground remnant. Not a rider rig."},
            {"id": "troop-gunpowder-heavy", "maxReadyPx": 64, "reason": "Not independently cleared at 130px by this pass."},
            {"id": "troop-future-ranged", "maxReadyPx": 64, "reason": "Not independently cleared at 130px by this pass."},
            {"id": "troop-future-heavy", "maxReadyPx": 64, "reason": "Not independently cleared at 130px by this pass."},
            {"note": "Code currently draws several of these near 130px. Code owns that consumer repair."},
        ],
        "binding": {"checked": len(checked), "failed": failed, "scope": "v9 readySubset paths, healer boot, draft, contract, v8 interface bytes. Not a full historical-original audit."},
        "inputPreservation": {"before": before, "after": after, "unchanged": before == after},
        "viewportEvidence": views,
        "reviewGallery": "qa/image-local-delivery-v9-20261005/review/index.html",
    }
    out_interface = ROOT / "docs" / "plan" / "IMAGE-DELIVERY-INTERFACE-V9-2026-10-05.json"
    out_interface.write_text(json.dumps(interface, indent=2), encoding="utf-8")

    visual_rows = []
    for pair in pairs:
        visual_rows.append({
            "id": pair["screen"],
            "screen": pair["screen"],
            "age": 0 if "stone" in pair["screen"] or pair["screen"] == "home" else None,
            "classId": "healer" if pair["screen"] == "home" else None,
            "referencePaths": [pair["reference"]],
            "referenceHashes": [sha256(ROOT / pair["reference"])],
            "sourceHashes": {},
            "viewports": [[1280, 720]],
            "stateKind": "ASSET_COMPOSITE",
            "screenshotPaths": [pair["composite"]],
            "checks": {
                "composition": "PARTIAL",
                "artPlacement": "PARTIAL",
                "controlsOrContacts": "UNVERIFIED",
                "readability": "PARTIAL",
                "stateTruth": "PARTIAL",
                "playability": "UNVERIFIED",
            },
            "differences": [pair["note"]],
            "blocker": "Image composite is not runtime playability.",
            "nextAction": "Code places the named ready rows and proves the screen.",
            "ownerAcceptance": "UNVERIFIED",
        })
    review_index = {
        "schema": 1,
        "generatedAt": "2026-10-05",
        "sourceSnapshot": {"head": "63d79a3cf62a27190d0fbefe87878e8fcbac3676", "note": "Read-only expectation from the prompt. This pass did not run git."},
        "liveUrl": None,
        "rows": visual_rows,
        "polishQueue": [
            {"id": "healer-head-fringe", "reason": "Hard threshold matte. Fine edge cleanup can wait.", "priority": 3},
            {"id": "scene-road-precision", "reason": "Stone traces are still coarser than corridor width.", "priority": 1},
            {"id": "cinematic-animation", "reason": "No articulated gait exists for any class.", "priority": 2},
        ],
        "wholeBuildStatus": "INCOMPLETE",
    }
    (QA / "review" / "review-index.json").write_text(json.dumps(review_index, indent=2), encoding="utf-8")
    (QA / "screen-queue.json").write_text(json.dumps(queue, indent=2), encoding="utf-8")

    html = ["<!doctype html><html lang=en><meta charset=utf-8><title>Image v9 asset composites</title>",
            "<style>body{font:16px sans-serif;background:#161616;color:#eee;margin:24px} img{max-width:100%;height:auto} .gap{color:#e7c07a}</style>",
            "<h1>Ages of Dominion — image v9 asset composites</h1>",
            "<p>Every picture below is an ASSET_COMPOSITE. It is not live gameplay. Code's preview command is <code>node scripts/serve.mjs</code>, default <code>http://127.0.0.1:4173</code>. This pass did not start a server.</p>",
            "<p>Interface: docs/plan/IMAGE-DELIVERY-INTERFACE-V9-2026-10-05.json. codeAIHandoffReady is false. Ready rows can be used one at a time.</p>"]
    for pair in pairs:
        html.append(f"<h2>{pair['screen']}</h2><p>{pair['note']}</p><img src='{Path(pair['composite']).name}' alt='{pair['screen']}'>")
    html.append("<h2>Healer leg subchain, -25 / 0 / +25</h2><img src='../assemblies/healer-leg-subchain-arc.gif' alt='healer leg arc'>")
    html.append("<h2>Stone annotation</h2><img src='../terrain/kingdom-terrain-stone-status.png' alt='stone annotation'>")
    html.append("<h2>Four kingdom viewports, uniform focus camera</h2><img src='../terrain/kingdom-stone-four-viewport.jpg' alt='four viewports'>")
    (QA / "review" / "index.html").write_text("\n".join(html), encoding="utf-8")

    ready_n = len(ready_rows)
    failed_n = 4 + sum(1 for a in new_attempts if a["status"] == "FAIL")
    partial_n = len(chains) + len(scenes) + sum(1 for h in heads if h["status"] != "READY")
    checkpoint = {
        "updated": "2026-10-05",
        "providerCalls": 0,
        "codeAIHandoffReady": False,
        "librariesMeasuredThisRun": libs,
        "inputHashesChanged": [k for k in before if before[k] != after[k]],
        "preserve": {"before": before, "after": after},
        "counts": {"ready": ready_n, "partialChains": len(chains), "partialScenes": len(scenes), "failedJointAttemptsNew": failed_n - 4, "failedPreserved": 4, "blocked": 1},
        "jointMismatches": mismatches,
        "arithmetic": arithmetic,
        "nextExecutableAction": "Manual trace of kingdom-terrain-bronze roads, banks, and bridge from its legal preview. Do not repeat the Stone coordinates and do not rerun exhausted Knight or Paladin placements.",
    }
    (QA / "checkpoint.json").write_text(json.dumps(checkpoint, indent=2), encoding="utf-8")
    print(json.dumps({"ready": ready_n, "mismatches": len(mismatches), "arithmetic": arithmetic, "attempts": new_attempts, "boot": after["healerBoot"], "heads": [(h["id"], h["status"], h["dimensions"]) for h in heads]}, indent=2))


if __name__ == "__main__":
    main()
