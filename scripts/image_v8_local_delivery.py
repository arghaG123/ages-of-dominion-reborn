"""Local v8 delivery. No provider calls, no asset overwrite, no generation.

Python image processing. Versions are measured at runtime and written into the
QA report. Box convention is half-open [x0, y0, x1, y1). Affine is
x' = a*x + c*y + e, y' = b*x + d*y + f, world cell to legal source pixels.
"""
from __future__ import annotations

import hashlib
import json
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / "qa" / "image-local-delivery-v8-20261005"
V7 = ROOT / "qa" / "image-local-continuation-20261005"
CONTRACT = ROOT / "src" / "data" / "implementation-contract.json"
MANIFEST = ROOT / "assets" / "high-res" / "interactive-4k-first32-20261003" / "run-06-kingdom-20261004-023321" / "manifest.json"
DRAFT = ROOT / "docs" / "plan" / "REPLACEMENT-DRAFT-THREE-ROLES-V6-CLARIFICATION-2026-10-04.json"
INTERFACE_V7 = ROOT / "docs" / "plan" / "IMAGE-DELIVERY-INTERFACE-V7-2026-10-05.json"
INTERFACE_V8 = ROOT / "docs" / "plan" / "IMAGE-DELIVERY-INTERFACE-V8-2026-10-05.json"
KINGDOM_AFFINE = [60, -10, 25, 35, 170, 165]
HALL_SCALE = 0.1312
VIEWPORTS = [(825, 375), (933, 424), (1180, 820), (1280, 720)]
AGES = ("stone", "bronze", "iron", "medieval", "gunpowder", "industrial", "modern", "future")

# Visual labels from the v7 component contact sheets. Side is never taken from a filename.
OBSERVED = {
    "mage": {
        "01_1221_92.png": ("torso_and_pelvis", "WITHHELD", "Painted TORSO and PELVIS labels and leader lines are in the crop."),
        "02_119_545.png": ("head_hood", "PARTIAL", "One hooded head. Mouth closed."),
        "03_595_548.png": ("head_hood", "PARTIAL", "One hooded head. Eyes lowered."),
        "04_585_86.png": ("head_hood", "PARTIAL", "One hooded head. Mouth open."),
        "05_116_83.png": ("head_hood", "PARTIAL", "One hooded head. Facing camera."),
        "06_977_1402.png": ("book", "PARTIAL", "Closed book. Not a limb."),
        "07_162_1799.png": ("staff", "PARTIAL", "Staff with a looped head. Not a limb."),
        "08_1549_1076.png": ("leather_tube", "PARTIAL", "Upright leather tube. Boot shaft versus sleeve is not established."),
        "09_1329_1089.png": ("leather_tube", "PARTIAL", "Bent leather tube. Segment identity is not established."),
        "10_130_1114.png": ("leather_tube", "PARTIAL", "Bent leather tube. Segment identity is not established."),
        "11_358_1115.png": ("leather_tube", "PARTIAL", "Bent leather tube. Segment identity is not established."),
        "12_1312_1456.png": ("leather_tube", "PARTIAL", "Upright leather tube with a lighter cuff."),
        "13_1590_1433.png": ("leather_tube", "PARTIAL", "Upright leather tube with a lighter cuff."),
        "14_155_1483.png": ("leather_tube", "PARTIAL", "Horizontal leather tube."),
        "15_395_1420.png": ("leather_tube", "PARTIAL", "Horizontal leather tube."),
        "16_1619_1753.png": ("shoe", "PARTIAL", "One buckled shoe. Side UNKNOWN."),
        "17_591_1124.png": ("hand", "PARTIAL", "Open hand, palm toward camera. Side UNKNOWN."),
        "18_430_1654.png": ("hand", "PARTIAL", "Open hand, back toward camera. Side UNKNOWN."),
        "19_1319_1789.png": ("boot_opening", "PARTIAL", "Boot opening seen from above."),
        "20_708_1499.png": ("hand", "PARTIAL", "Open hand, back toward camera. Side UNKNOWN."),
        "21_792_1136.png": ("skeletal_hand", "PARTIAL", "Skeletal hand. Not a living-hand substitute."),
    },
    "warlock": {
        "01_1042_107.png": ("torso_and_pelvis", "PARTIAL", "Cuirass and fauld in one crop. No head."),
        "02_80_86.png": ("head_group_and_forearm_and_labels", "WITHHELD", "Six heads, one forearm, and HEAD/ARM/LEG label pixels share one component."),
        "03_1087_1087.png": ("leg_pair_with_soles", "WITHHELD", "Two booted legs and two soles are one painted group."),
        "04_48_824.png": ("arms_hands_staff_book_group", "WITHHELD", "Several arms, hands, a staff and a book share the gray panel."),
        "05_483_1629.png": ("book_and_satchel", "WITHHELD", "Book and potion satchel are one component."),
        "06_579_1985.png": ("label_text", "NOT_ANATOMY", "Glyphs read OFFHAND ACCESSORY SET. No limb pixels."),
        "07_1618_1902.png": ("label_text", "NOT_ANATOMY", "Glyphs read BOOT SOLE DETAIL. No limb pixels."),
        "08_192_1985.png": ("label_text", "NOT_ANATOMY", "Glyphs read PRIMARY STAFF. No limb pixels."),
        "09_1432_973.png": ("label_text", "NOT_ANATOMY", "Glyphs read TORSO MAIN. The words are not the torso."),
        "10_264_973.png": ("label_text", "NOT_ANATOMY", "Glyphs read L ARM ASSY. The text does not establish side or a limb."),
        "11_1266_1902.png": ("label_text", "NOT_ANATOMY", "Glyphs read L LEG ASSY. The text does not establish side or a limb."),
    },
    "necromancer": {
        "01_1082_92.png": ("torso_pauldrons_tassets", "WITHHELD", "Torso, pauldrons and tassets are one crop. A detached arm sits in the same component."),
        "02_527_1082.png": ("arm_pair_and_staff", "WITHHELD", "Two arms and a staff share the crop."),
        "03_549_62.png": ("skulls_and_arm", "WITHHELD", "Three skulls and one arm share the crop."),
        "04_1710_87.png": ("backplate_and_tassets", "PARTIAL", "Backplate and tassets. No head."),
        "05_60_1569.png": ("satchel", "PARTIAL", "Skull satchel. Not a limb."),
        "06_1755_1098.png": ("leg_greave_boot", "PARTIAL", "One armored leg through the boot. Side UNKNOWN. Not separated at the knee."),
        "07_1091_1095.png": ("leg_greave_boot", "PARTIAL", "One armored leg through the boot. Side UNKNOWN."),
        "08_1303_1096.png": ("leg_greave_boot", "PARTIAL", "One clothed leg through the boot. Side UNKNOWN."),
        "09_1556_1098.png": ("leg_greave_boot", "PARTIAL", "One armored leg through the boot. Side UNKNOWN."),
        "10_391_51.png": ("skeletal_hand_and_skull", "WITHHELD", "Hand and skull share the crop."),
        "11_57_371.png": ("arm_forearm_hand", "PARTIAL", "Arm through skeletal hand. Side UNKNOWN. Not joint-separated."),
        "12_56_1101.png": ("leg_bent", "PARTIAL", "One bent clothed leg. Side UNKNOWN."),
        "13_56_47.png": ("head_hooded_skull", "PARTIAL", "One hooded skull. Side UNKNOWN."),
        "14_276_1104.png": ("leg_bent", "PARTIAL", "One bent clothed leg. Side UNKNOWN."),
        "15_1655_1898.png": ("boot_sole", "PARTIAL", "Boot sole. Side UNKNOWN. Not a standing leg."),
        "16_1190_1901.png": ("boot_sole", "PARTIAL", "Boot sole. Side UNKNOWN. Not a standing leg."),
    },
    "barbarian": {
        "01_1110_80.png": ("torso_and_skirt", "WITHHELD", "Cuirass and fur skirt share the crop."),
        "02_1502_0.png": ("vest", "PARTIAL", "Fur vest. Magenta panel remains in the crop."),
        "03_1086_1492.png": ("boot_group", "WITHHELD", "Several boots share the crop."),
        "04_1583_501.png": ("fur_skirt", "PARTIAL", "Fur-trimmed skirt. Not a leg."),
        "05_57_51.png": ("head", "PARTIAL", "Bearded head, braids. Side UNKNOWN."),
        "06_69_546.png": ("head", "PARTIAL", "Bearded head. Side UNKNOWN."),
        "07_1788_1092.png": ("bracer", "PARTIAL", "Studded bracer. Side UNKNOWN."),
        "08_1112_1092.png": ("bracer_on_forearm", "PARTIAL", "Bracer on a forearm. Side UNKNOWN."),
        "09_400_1723.png": ("axe_and_hand", "WITHHELD", "Axe and gripping hand share the crop."),
        "10_1595_1135.png": ("bare_limb_segment", "PARTIAL", "Bare limb. Thigh versus upper arm is not established."),
        "11_1315_1132.png": ("bare_limb_segment", "PARTIAL", "Bare limb. Thigh versus upper arm is not established."),
        "12_311_546.png": ("head_profile", "PARTIAL", "Bearded head in profile. Side UNKNOWN."),
        "13_1744_1853.png": ("shoe", "PARTIAL", "One soft shoe. Side UNKNOWN."),
        "14_613_1066.png": ("bare_limb_segment", "PARTIAL", "Bare limb with a strap. Segment UNKNOWN."),
        "15_83_1071.png": ("bare_limb_segment", "PARTIAL", "Bare limb with a strap. Segment UNKNOWN."),
        "16_616_1307.png": ("bracer", "PARTIAL", "Fur-trimmed bracer. Side UNKNOWN."),
        "17_279_1292.png": ("bracer", "PARTIAL", "Fur-trimmed bracer. Side UNKNOWN."),
        "18_54_1335.png": ("bracer", "PARTIAL", "Fur-trimmed bracer. Side UNKNOWN."),
        "19_838_1279.png": ("bracer", "PARTIAL", "Fur-trimmed bracer. Side UNKNOWN."),
        "20_218_1743.png": ("hand", "PARTIAL", "Open hand. Side UNKNOWN."),
        "21_61_1742.png": ("hand", "PARTIAL", "Open hand. Side UNKNOWN."),
        "22_290_1076.png": ("bare_limb_segment", "PARTIAL", "Bare limb. Segment UNKNOWN."),
        "23_826_1067.png": ("bare_limb_segment", "PARTIAL", "Bare limb. Segment UNKNOWN."),
        "24_367_1531.png": ("hand", "PARTIAL", "Open hand. Side UNKNOWN."),
        "25_519_1531.png": ("hand", "PARTIAL", "Open hand. Side UNKNOWN."),
        "26_671_1906.png": ("dagger", "PARTIAL", "Dagger. No hand on this crop."),
        "27_730_1557.png": ("fist", "PARTIAL", "Closed fist. Side UNKNOWN."),
        "28_856_1558.png": ("fist", "PARTIAL", "Closed fist. Side UNKNOWN."),
        "29_81_1586.png": ("fist", "PARTIAL", "Closed fist. Side UNKNOWN."),
        "30_215_1590.png": ("fist", "PARTIAL", "Closed fist. Side UNKNOWN."),
    },
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def versions() -> dict:
    import cv2
    import PIL
    import scipy
    return {
        "python": ".".join(map(str, __import__("sys").version_info[:3])),
        "Pillow": PIL.__version__,
        "NumPy": np.__version__,
        "OpenCV": cv2.__version__,
        "SciPy": scipy.__version__,
    }


def candidate_mask(rgb: np.ndarray, widen: bool) -> np.ndarray:
    src = rgb.astype(np.int16) if widen else rgb
    return (src[:, :, 2] > src[:, :, 0] + 18) & (src[:, :, 2] > src[:, :, 1] + 8) & (src[:, :, 2] > 70)


def synthetic_overflow() -> dict:
    # R=240, G=240, B=250. uint8 240+18 wraps to 2, so B>R+18 is true. int16 250>258 is false.
    px = np.array([[[240, 240, 250]]], np.uint8)
    wrapped = bool(candidate_mask(px, False)[0, 0])
    wide = bool(candidate_mask(px, True)[0, 0])
    both = np.array([[[80, 90, 160]]], np.uint8)
    return {
        "case": "uint8 R+18 overflow",
        "pixelRgb": [240, 240, 250],
        "uint8Candidate": wrapped,
        "widenedCandidate": wide,
        "passed": wrapped and not wide,
        "controlBothTrue": bool(candidate_mask(both, False)[0, 0] and candidate_mask(both, True)[0, 0]),
        "note": "This is mask arithmetic only. It is not a river or a bank.",
    }


def rdp(points: list, eps: float) -> list:
    if len(points) < 3:
        return points
    def d(p, a, b):
        ax, ay = a
        bx, by = b
        px, py = p
        vx, vy = bx - ax, by - ay
        L = (vx * vx + vy * vy) ** 0.5 or 1
        return abs((px - ax) * vy - (py - ay) * vx) / L
    a, b = points[0], points[-1]
    idx, best = 0, 0
    for i, p in enumerate(points[1:-1], 1):
        dist = d(p, a, b)
        if dist > best:
            best, idx = dist, i
    if best <= eps:
        return [a, b]
    return rdp(points[: idx + 1], eps)[:-1] + rdp(points[idx:], eps)


def pca_centerline(comp: np.ndarray, bins: int = 36) -> list:
    ys, xs = np.where(comp)
    if len(xs) < 80:
        return []
    pts = np.stack([xs.astype(np.float32), ys.astype(np.float32)], 1)
    mean = pts.mean(0)
    _, _, vt = np.linalg.svd(pts - mean, full_matrices=False)
    axis = vt[0]
    proj = (pts - mean) @ axis
    edges = np.linspace(float(proj.min()), float(proj.max()), bins + 1)
    line = []
    for i in range(bins):
        sel = (proj >= edges[i]) & (proj < edges[i + 1])
        if int(sel.sum()) < 12:
            continue
        line.append((float(pts[sel, 0].mean()), float(pts[sel, 1].mean())))
    return line


def poly_length(points) -> float:
    total = 0.0
    for a, b in zip(points, points[1:]):
        total += ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5
    return total


def longest_path(binary: np.ndarray) -> list:
    ys, xs = np.where(binary)
    if len(xs) < 16 or len(xs) > 24000:
        return []
    pts = {(int(x), int(y)) for x, y in zip(xs, ys)}
    start = next(iter(pts))

    def far(src):
        parent = {src: None}
        q = deque([src])
        last = src
        while q:
            last = q.popleft()
            x, y = last
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if dx == dy == 0:
                        continue
                    n = (x + dx, y + dy)
                    if n in pts and n not in parent:
                        parent[n] = last
                        q.append(n)
        return last, parent

    a, _ = far(start)
    b, parent = far(a)
    path = []
    cur = b
    while cur is not None:
        path.append(cur)
        cur = parent[cur]
    path.reverse()
    return path


def skeleton(mask: np.ndarray) -> np.ndarray:
    import cv2
    img = (mask.astype(np.uint8) * 255)
    element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    skel = np.zeros_like(img)
    guard = 0
    while cv2.countNonZero(img) and guard < 64:
        opened = cv2.morphologyEx(img, cv2.MORPH_OPEN, element)
        skel = cv2.bitwise_or(skel, cv2.subtract(img, opened))
        img = cv2.erode(img, element)
        guard += 1
    return skel > 0


def scale_poly(points, sx, sy):
    return [[round(x * sx, 2), round(y * sy, 2)] for x, y in points]


def inverse_world(affine, x, y):
    a, b, c, d, e, f = affine
    det = a * d - c * b
    x = x - e
    y = y - f
    return [(d * x - c * y) / det, (-b * x + a * y) / det]


def raster_line(shape, a, b):
    import cv2
    canvas = np.zeros(shape, np.uint8)
    cv2.line(canvas, (int(round(a[0])), int(round(a[1]))), (int(round(b[0])), int(round(b[1]))), 1, 1)
    return canvas > 0


def project(affine, x, y):
    a, b, c, d, e, f = affine
    return (a * x + c * y + e, b * x + d * y + f)


def mode_of(scene_id: str) -> str:
    for mode in ("kingdom", "adventure", "tactical", "defense"):
        if scene_id.startswith(mode):
            return mode
    raise KeyError(scene_id)


def biome_age(scene_id: str, mode: str):
    tail = scene_id[len(mode) + len("-terrain"):].lstrip("-")
    if mode == "kingdom":
        return tail if tail in AGES else None, None
    return None, (tail or "default")


def trace_scene(item, contract) -> dict:
    import cv2
    from scipy import ndimage
    mode = item.get("mode") or mode_of(item["id"])
    geo = contract["geometry"][mode]
    affine = geo["worldToSource"]
    path = ROOT / item["outputFile"]
    age, biome = biome_age(item["id"], mode)
    row = {
        "id": item["id"],
        "role": "scene-plate",
        "mode": mode,
        "age": age,
        "biome": biome,
        "status": "PARTIAL",
        "promoted": False,
        "source": None,
        "legalAffineActive": affine,
        "legalAffineFrozen": mode != "kingdom" or affine == KINGDOM_AFFINE,
        "hallScaleActive": HALL_SCALE if mode == "kingdom" else None,
        "hallScaleFrozen": True,
        "proposedCamera": None,
        "runtimeAcceptance": "UNVERIFIED",
        "ownerAcceptance": "UNVERIFIED",
        "nativeDecode": "NOT_BARE_TERRAIN_PASS",
    }
    if not path.is_file():
        row["status"] = "BLOCKED"
        row["limitations"] = ["Source bytes missing."]
        return row
    digest = sha256(path)
    with Image.open(path) as im:
        w, h = im.size
        im.verify()
    with Image.open(path) as im:
        legal_w, legal_h = geo["sourceSize"]
        small = np.asarray(im.convert("RGB").resize((legal_w, legal_h), Image.Resampling.BOX))
        preview = im.convert("RGB").resize((640, int(640 * h / w)), Image.Resampling.BOX)
    scale = w / legal_w
    row["source"] = {"path": item["outputFile"].replace("\\", "/"), "sha256": digest, "dimensions": [w, h]}
    row["coordinateFrames"] = {
        "boxConvention": "half-open [x0,y0,x1,y1)",
        "native": {"origin": "top-left", "dimensions": [w, h]},
        "legalSource": {"dimensions": [legal_w, legal_h], "nativePerLegal": scale},
        "affine": {"values": affine, "maps": "world xy to legal source pixels", "formula": "x'=a*x+c*y+e; y'=b*x+d*y+f"},
    }
    uint8 = candidate_mask(small, False)
    wide = candidate_mask(small, True)
    row["blueCandidateArithmetic"] = {
        "grid": [legal_w, legal_h],
        "uint8Pixels": int(uint8.sum()),
        "widenedPixels": int(wide.sum()),
        "pixelsChanged": int(np.count_nonzero(uint8 != wide)),
        "meaning": "Candidate color only, before component filtering. Not bank truth.",
    }
    sky = np.zeros_like(wide)
    lab, n = ndimage.label(wide)
    river_specs = []
    for i in range(1, n + 1):
        comp = lab == i
        area = int(comp.sum())
        if area < 80:
            continue
        ys, xs = np.where(comp)
        if ys.mean() < legal_h * 0.18 or ys.min() < legal_h * 0.04:
            sky[comp] = True
            continue
        river_specs.append((area, comp, xs, ys))
    river_specs.sort(key=lambda t: t[0], reverse=True)

    painted_rivers = []
    painted_banks = []
    # Correction of the skeleton cap: the largest component uses a PCA median axis.
    # The baseline skeleton dropped rivers whose thinned mask exceeded 24000 pixels.
    for index, (area, comp, xs, ys) in enumerate(river_specs[:2]):
        path_pts = pca_centerline(comp) if index == 0 else longest_path(skeleton(comp))
        if poly_length(path_pts) >= 40:
            painted_rivers.append({
                "polylineNative": scale_poly(rdp([(int(p[0]), int(p[1])) for p in path_pts], 4), scale, scale),
                "legalPixels": area,
                "method": "pca-median-axis" if index == 0 else "skeleton",
                "uncertainty": "Axis of a widened-blue component below the sky band. Blue roofs, sea and reflections can pass. Not a surveyed bank.",
            })
        contours, _ = cv2.findContours(comp.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            cnt = max(contours, key=cv2.contourArea)
            approx = cv2.approxPolyDP(cnt, 6, True).reshape(-1, 2)
            if len(approx) >= 3:
                cx, cy = xs.mean(), ys.mean()
                left = [(int(p[0]), int(p[1])) for p in approx if p[0] <= cx]
                right = [(int(p[0]), int(p[1])) for p in approx if p[0] > cx]
                for side_name, side_pts in (("lower-x", left), ("higher-x", right)):
                    if len(side_pts) >= 2:
                        painted_banks.append({
                            "side": side_name,
                            "observedBankSide": "UNKNOWN",
                            "polylineNative": scale_poly(side_pts, scale, scale),
                            "uncertainty": "Split of the color contour by component centroid x. This is not a surveyed left or right bank.",
                        })
    if painted_rivers:
        river_state = "TRACED_COLOR_BOUNDARY"
    elif int(wide.sum()) == 0:
        river_state = "NO_WIDENED_BLUE_PIXELS_NOT_PROOF_OF_ABSENCE"
    else:
        river_state = "BLUE_PRESENT_BUT_NO_COMPONENT_PASSED_SKY_FILTER"

    # Baseline relative-luminance regions flooded (often >22% of the frame) and did not
    # follow thin tracks. One correction: keep strong gradient ridges, then elongated components.
    lum = small.astype(np.float32).mean(2)
    gx = cv2.Sobel(lum, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(lum, cv2.CV_32F, 0, 1, ksize=3)
    mag = np.sqrt(gx * gx + gy * gy)
    mag[: int(legal_h * 0.18), :] = 0
    mag[wide] = 0
    thr = float(np.percentile(mag, 93))
    track = mag >= max(thr, 12)
    frac = float(track.mean())
    painted_roads = []
    road_state = "UNRESOLVABLE_BY_GRADIENT_RIDGE_V1"
    road_method = "one correction after relative-luminance flood: Sobel ridges at the 93rd percentile, water and sky excluded"
    if frac > 0.12:
        road_state = "UNRESOLVABLE_RIDGE_MASK_TOO_BROAD"
    elif frac < 0.001:
        road_state = "NO_RIDGE_PIXELS_UNDER_THIS_METHOD_NOT_PROOF_OF_ABSENCE"
    else:
        lab_m, nm = ndimage.label(track)
        lengths = []
        for i in range(1, nm + 1):
            comp = lab_m == i
            area = int(comp.sum())
            if area < 80 or area > 20000:
                continue
            ys, xs = np.where(comp)
            bw = int(xs.max() - xs.min() + 1)
            bh = int(ys.max() - ys.min() + 1)
            if max(bw, bh) < 2.2 * max(1, min(bw, bh)):
                continue
            sk = skeleton(comp)
            pts = longest_path(sk)
            if len(pts) >= 12:
                lengths.append((len(pts), pts))
        lengths.sort(key=lambda t: t[0], reverse=True)
        for length, pts in lengths[:8]:
            painted_roads.append({
                "polylineNative": scale_poly(rdp(pts, 5), scale, scale),
                "skeletonPixels": length,
                "uncertainty": "Gradient-ridge skeleton after the luminance mask flooded. Building edges, rocks and tree lines can enter. Not a surveyed crown.",
            })
        road_state = "TRACED_GRADIENT_RIDGE" if painted_roads else "SKELETON_EMPTY"

    painted_bridge = []
    bridge_state = "NOT_SEPARATED"
    if river_specs:
        river = river_specs[0][1]
        # 9px missed decks that sit just outside the blue boundary. One wider band.
        band = cv2.dilate(river.astype(np.uint8), np.ones((25, 25), np.uint8)) > 0
        brown = band & ~wide & (small[:, :, 0] > small[:, :, 2] + 18) & (small[:, :, 0] > 70)
        lab_b, nb = ndimage.label(brown)
        best = None
        for i in range(1, nb + 1):
            comp = lab_b == i
            area = int(comp.sum())
            if area < 40:
                continue
            ys, xs = np.where(comp)
            span = int(xs.max() - xs.min())
            thick = int(ys.max() - ys.min())
            if span < 18 or thick > span:
                continue
            if best is None or area > best[0]:
                best = (area, comp, xs, ys)
        if best:
            contours, _ = cv2.findContours(best[1].astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                cnt = max(contours, key=cv2.contourArea)
                approx = cv2.approxPolyDP(cnt, 4, True).reshape(-1, 2)
                if len(approx) >= 3:
                    painted_bridge.append({
                        "kind": "deck_candidate",
                        "polygonNative": scale_poly(approx, scale, scale),
                        "uncertainty": "Brown pixels inside the dilated largest blue component. A road crossing or a hull can pass. Approaches were not separated.",
                    })
                    bridge_state = "DECK_CANDIDATE_ONLY"
        else:
            bridge_state = "NO_BROWN_CROSSING_IN_BLUE_BAND_NOT_PROOF_OF_ABSENCE"
    else:
        bridge_state = "NO_RIVER_COMPONENT_SO_CROSSING_UNRESOLVED"

    # Legal geometry residuals on the legal grid.
    def rect_points(rect):
        x, y, rw, rh = rect
        return [project(affine, x, y), project(affine, x + rw, y), project(affine, x + rw, y + rh), project(affine, x, y + rh)]

    legal_roads = []
    road_canvas = np.zeros(track.shape, np.uint8)
    for line in geo.get("roads", []):
        pts = [project(affine, x, y) for x, y in line]
        native = scale_poly(pts, scale, scale)
        legal_roads.append({"polylineNative": [[round(p[0], 2), round(p[1], 2)] for p in native], "label": "LEGAL_CENTERLINE"})
        for p, q in zip(pts, pts[1:]):
            road_canvas |= raster_line(track.shape, p, q).astype(np.uint8)
    residual = {"state": "NOT_MEASURED", "legalRoadToTrackMask": None}
    if road_state == "TRACED_GRADIENT_RIDGE":
        # Distance to nearest track pixel. Zero-valued pixels are the targets.
        dt = cv2.distanceTransform((~track).astype(np.uint8), cv2.DIST_L2, 3)
        samples = dt[road_canvas > 0]
        if samples.size:
            residual = {
                "state": "MEASURED_AGAINST_TRACK_MASK",
                "legalRoadToTrackMask": {
                    "unit": "legal source pixels",
                    "mean": round(float(samples.mean()), 2),
                    "p95": round(float(np.percentile(samples, 95)), 2),
                    "max": round(float(samples.max()), 2),
                    "nativePerLegal": scale,
                },
                "note": "Distance from the legal centerline to the relative-luminance mask, not to a surveyed crown of the road.",
            }
    legal_bridges = []
    bridge_iou = None
    for bridge in geo.get("bridges", []):
        poly = rect_points(bridge["rect"])
        native_poly = [[round(p[0] * scale, 2), round(p[1] * scale, 2)] for p in poly]
        legal_bridges.append({"id": bridge["id"], "polygonNative": native_poly, "label": "LEGAL_RECT"})
        if painted_bridge:
            legal_mask = np.zeros(track.shape, np.uint8)
            cv2.fillPoly(legal_mask, [np.array(poly, np.int32)], 1)
            paint = np.zeros(track.shape, np.uint8)
            pts = np.array([[int(round(p[0] / scale)), int(round(p[1] / scale))] for p in painted_bridge[0]["polygonNative"]], np.int32)
            cv2.fillPoly(paint, [pts], 1)
            inter = int(((legal_mask > 0) & (paint > 0)).sum())
            union = int(((legal_mask > 0) | (paint > 0)).sum())
            bridge_iou = round(inter / union, 4) if union else None
    sites = []
    for site in geo.get("sites", []):
        poly = rect_points(site["rect"])
        sites.append({
            "id": site["id"],
            "polygonNative": [[round(p[0] * scale, 2), round(p[1] * scale, 2)] for p in poly],
            "label": "LEGAL_SITE_RECT",
            "bakedContent": "NOT_SEPARATED",
        })
    blocked = []
    for cell in geo.get("blocked", []):
        poly = rect_points([cell[0], cell[1], 1, 1])
        blocked.append({"cell": cell, "polygonNative": [[round(p[0] * scale, 2), round(p[1] * scale, 2)] for p in poly], "label": "LEGAL_BLOCKED_CELL"})

    proposal = None
    mean_res = (residual.get("legalRoadToTrackMask") or {}).get("mean")
    mismatch = (mean_res is not None and mean_res > 15) or (bridge_iou is not None and bridge_iou < 0.15)
    if mismatch and road_state == "TRACED_GRADIENT_RIDGE":
        world_roads = []
        for road in painted_roads:
            world = []
            for x, y in road["polylineNative"]:
                wx, wy = inverse_world(affine, x / scale, y / scale)
                world.append([round(wx, 3), round(wy, 3)])
            world_roads.append(world)
        proposal = {
            "id": f"proposal-v8-{item['id']}",
            "status": "PROPOSED",
            "proposedCamera": None,
            "activeAffine": affine,
            "activeHallScale": HALL_SCALE if mode == "kingdom" else None,
            "activated": False,
            "proposedRoadWorld": world_roads,
            "affectedIds": [item["id"]],
            "routeImplication": "Movement and picking still use the active contract. These world polylines are the inverse of the luminance traces.",
            "reason": "Legal centerline mean distance to the trace mask exceeds 15 legal pixels, or the legal bridge rectangle overlaps the deck candidate below 0.15.",
        }

    # Overlay.
    draw = ImageDraw.Draw(preview)
    sx, sy = preview.size[0] / w, preview.size[1] / h
    def draw_poly(pts, fill, width=2):
        flat = [(p[0] * sx, p[1] * sy) for p in pts]
        if len(flat) >= 2:
            draw.line(flat, fill=fill, width=width)
    for road in legal_roads:
        draw_poly(road["polylineNative"], (230, 200, 40), 2)
    for bridge in legal_bridges:
        draw.polygon([(p[0] * sx, p[1] * sy) for p in bridge["polygonNative"]], outline=(220, 90, 40))
    for road in painted_roads:
        draw_poly(road["polylineNative"], (220, 40, 180), 2)
    for river in painted_rivers:
        draw_poly(river["polylineNative"], (40, 90, 220), 2)
    for bank in painted_banks:
        draw_poly(bank["polylineNative"], (40, 180, 90), 1)
    for bridge in painted_bridge:
        draw.polygon([(p[0] * sx, p[1] * sy) for p in bridge["polygonNative"]], outline=(255, 255, 255))
    overlay_path = QA / "terrain" / f"{item['id']}-painted-and-legal.png"
    preview.save(overlay_path)

    if proposal:
        sheet = Image.new("RGB", (1280, 860), (20, 20, 20))
        sheet_draw = ImageDraw.Draw(sheet)
        for i, (vw, vh) in enumerate(VIEWPORTS):
            panel = preview.resize((vw // 2, vh // 2), Image.Resampling.BOX)
            sheet.paste(panel, ((i % 2) * 640, (i // 2) * 400 + 24))
            sheet_draw.text(((i % 2) * 640 + 4, (i // 2) * 400 + 4), f"{vw}x{vh} active legal yellow, trace magenta", fill=(240, 240, 240))
        four_path = QA / "terrain" / f"{item['id']}-four-viewport.png"
        sheet.save(four_path)
        proposal["fourViewport"] = str(four_path.relative_to(ROOT)).replace("\\", "/")

    row.update({
        "paintedRoadPolylines": painted_roads,
        "paintedRoadMethod": road_method,
        "paintedRoadState": road_state,
        "paintedRiverPolylines": painted_rivers,
        "paintedRiverState": river_state,
        "paintedBankPolylines": painted_banks,
        "paintedBankState": "CENTROID_SPLIT_OF_BLUE_CONTOUR" if painted_banks else river_state,
        "paintedBridgeDeckPolygons": painted_bridge,
        "paintedBridgeApproachPolygons": [],
        "paintedBridgeApproachState": "NOT_TRACED",
        "paintedBridgeState": bridge_state,
        "walkablePolygons": [],
        "walkableState": "NOT_TRACED",
        "blockedPolygons": blocked,
        "blockedState": "LEGAL_CELLS_ONLY_NOT_PAINTED_OBSTACLES",
        "staticObstacleState": "VISIBLE_ROCKS_OR_STRUCTURES_NOT_POLYGONIZED",
        "mutableContent": "BAKED_INTO_THE_PLATE_NOT_A_SEPARATE_LAYER",
        "legalRoads": legal_roads,
        "legalBridges": legal_bridges,
        "legalSites": sites,
        "residual": residual,
        "legalBridgeVsDeckIou": bridge_iou,
        "proposal": proposal,
        "overlay": str(overlay_path.relative_to(ROOT)).replace("\\", "/"),
        "limitations": [
            "Hash and decode are not a bare-terrain, spatial, runtime, or owner pass.",
            "Empty approach and walkable arrays mean those features were not traced.",
            "Active affine and Hall scale were not edited.",
        ],
    })
    if item["id"] == "kingdom-terrain-stone":
        row["stoneInspection"] = (
            "On this plate the painted dirt tracks form a ring and radials, the river is on the right, "
            "and a wooden bridge sits downstream of the legal bridge rectangle. The legal road cuts the ring. "
            "This sentence is stone-only."
        )
    return row


def thumb(path: Path, box):
    if not path.is_file():
        im = Image.new("RGBA", box, (80, 80, 80, 255))
        return im
    im = Image.open(path).convert("RGBA")
    im.thumbnail(box)
    canvas = Image.new("RGBA", box, (245, 245, 245, 255))
    canvas.paste(im, ((box[0] - im.size[0]) // 2, (box[1] - im.size[1]) // 2), im)
    return canvas


def draw_chain(class_id: str, slots: list, out: Path) -> None:
    w, h = 220 * max(1, len(slots)), 280
    sheet = Image.new("RGB", (w, h), (235, 232, 226))
    draw = ImageDraw.Draw(sheet)
    draw.text((8, 4), class_id + " neutral chain — missing links stay empty", fill=(20, 20, 20))
    for i, slot in enumerate(slots):
        x = i * 220
        panel = thumb(ROOT / slot["path"], (180, 180)) if slot.get("path") else Image.new("RGBA", (180, 180), (210, 210, 210, 255))
        sheet.paste(panel.convert("RGB"), (x + 16, 36))
        draw.text((x + 8, 222), slot["name"][:28], fill=(0, 0, 0))
        draw.text((x + 8, 240), slot["state"][:32], fill=(120, 30, 30))
        if i:
            color = (30, 120, 40) if slot.get("link") == "measured" else (180, 40, 40)
            draw.line((x - 8, 120, x + 12, 120), fill=color, width=4)
    sheet.save(out)


def assemblies() -> list:
    specs = {
        "healer": [
            {"name": "head", "state": "MISSING", "link": "missing"},
            {"name": "torso", "path": "assets/derivatives/rigs/v6/healer/torso.png", "state": "PRESENT", "link": "missing"},
            {"name": "skirt", "path": "assets/derivatives/rigs/v6/healer/skirt.png", "state": "PRESENT_NOT_A_LEG", "link": "missing"},
            {"name": "upper leg", "path": "assets/derivatives/rigs/v6/healer/leg_upper.png", "state": "PRESENT", "link": "missing"},
            {"name": "greave", "path": "assets/derivatives/rigs/v6/healer/greave.png", "state": "JOINT_READY_-25_0_25", "link": "measured"},
            {"name": "boot v7", "path": "assets/derivatives/rigs/v7/healer/boot.png", "state": "JOINT_READY_-25_0_25", "link": "measured"},
        ],
        "paladin": [
            {"name": "head v6", "path": "assets/derivatives/rigs/v6/paladin/head_three_quarter.png", "state": "UNREPAIRED", "link": "missing"},
            {"name": "cuirass+fauld", "path": "assets/derivatives/rigs/v6/paladin/cuirass_fauld_combined.png", "state": "INSEPARABLE", "link": "missing"},
            {"name": "thigh", "path": "assets/derivatives/rigs/v6/paladin/thigh.png", "state": "SCALE_FAIL_TO_KNEE", "link": "failed"},
            {"name": "knee", "path": "assets/derivatives/rigs/v6/paladin/knee_cop.png", "state": "PRESENT", "link": "failed"},
            {"name": "greave", "path": "assets/derivatives/rigs/v6/paladin/greave.png", "state": "JOINT_READY_FROM_KNEE", "link": "measured"},
            {"name": "boot", "path": "assets/derivatives/rigs/v6/paladin/boot.png", "state": "SCALE_FAIL_FROM_GREAVE", "link": "failed"},
        ],
        "ranger": [
            {"name": "cowl", "path": "assets/derivatives/rigs/v3/ranger/head_cowl.png", "state": "FILENAME_ONLY", "link": "missing"},
            {"name": "tunic", "path": "assets/derivatives/rigs/v3/ranger/torso_tunic.png", "state": "FILENAME_ONLY", "link": "missing"},
            {"name": "sleeve v5", "path": "assets/derivatives/rigs/v5/ranger/sleeve_upper_arm.png", "state": "CUFF_JOINT_ONLY", "link": "missing"},
            {"name": "vambrace v5", "path": "assets/derivatives/rigs/v5/ranger/vambrace_hand_open.png", "state": "ARC_-25_0_25", "link": "measured"},
            {"name": "second leg", "state": "NOT_ONE_CHAIN", "link": "missing"},
        ],
        "knight": [
            {"name": "thigh", "state": "EXHAUSTED_12+1", "link": "failed"},
            {"name": "greave", "state": "NO_PASSING_PLACEMENT", "link": "failed"},
            {"name": "vambrace", "path": "assets/derivatives/rigs/v5/knight/vambrace.png", "state": "NOT_IN_THE_FAILED_PAIR", "link": "missing"},
        ],
        "mage": [
            {"name": "hood head", "path": "qa/image-local-continuation-20261005/components/mage/02_119_545.png", "state": "ONE_OF_FOUR", "link": "missing"},
            {"name": "torso+pelvis", "path": "qa/image-local-continuation-20261005/components/mage/01_1221_92.png", "state": "LABELS_ATTACHED", "link": "missing"},
            {"name": "tube", "path": "qa/image-local-continuation-20261005/components/mage/14_155_1483.png", "state": "SEGMENT_UNKNOWN", "link": "missing"},
            {"name": "shoe", "path": "qa/image-local-continuation-20261005/components/mage/16_1619_1753.png", "state": "NO_LEG_LINK", "link": "missing"},
        ],
        "warlock": [
            {"name": "labels", "path": "qa/image-local-continuation-20261005/components/warlock/09_1432_973.png", "state": "TEXT_NOT_TORSO", "link": "missing"},
            {"name": "torso crop", "path": "qa/image-local-continuation-20261005/components/warlock/01_1042_107.png", "state": "NO_HEAD_LINK", "link": "missing"},
            {"name": "leg group", "path": "qa/image-local-continuation-20261005/components/warlock/03_1087_1087.png", "state": "INSEPARABLE", "link": "missing"},
        ],
        "necromancer": [
            {"name": "skull head", "path": "qa/image-local-continuation-20261005/components/necromancer/13_56_47.png", "state": "NO_NECK_LINK", "link": "missing"},
            {"name": "torso group", "path": "qa/image-local-continuation-20261005/components/necromancer/01_1082_92.png", "state": "INSEPARABLE", "link": "missing"},
            {"name": "whole leg", "path": "qa/image-local-continuation-20261005/components/necromancer/06_1755_1098.png", "state": "NOT_JOINTED", "link": "missing"},
        ],
        "barbarian": [
            {"name": "head", "path": "qa/image-local-continuation-20261005/components/barbarian/05_57_51.png", "state": "NO_NECK_LINK", "link": "missing"},
            {"name": "torso+skirt", "path": "qa/image-local-continuation-20261005/components/barbarian/01_1110_80.png", "state": "INSEPARABLE", "link": "missing"},
            {"name": "bare limb", "path": "qa/image-local-continuation-20261005/components/barbarian/10_1595_1135.png", "state": "SEGMENT_UNKNOWN", "link": "missing"},
            {"name": "shoe", "path": "qa/image-local-continuation-20261005/components/barbarian/13_1744_1853.png", "state": "NO_LEG_LINK", "link": "missing"},
        ],
    }
    rows = []
    out_dir = QA / "assemblies"
    out_dir.mkdir(parents=True, exist_ok=True)
    for class_id, slots in specs.items():
        rel = f"qa/image-local-delivery-v8-20261005/assemblies/{class_id}-missing-chain.png"
        draw_chain(class_id, slots, ROOT / rel)
        measured = [s["name"] for s in slots if s.get("link") == "measured"]
        missing = [s["name"] for s in slots if s.get("link") != "measured"]
        rows.append({
            "id": f"{class_id}-neutral-chain",
            "class": class_id,
            "status": "PARTIAL",
            "fullBody": "FAIL",
            "side": "UNKNOWN",
            "measuredLinks": measured,
            "missingOrUnprovenLinks": missing,
            "diagram": rel,
            "diagramSha256": sha256(ROOT / rel),
            "neutralPose": "NOT_A_SINGLE_SCALE_BODY",
            "drawOrder": [s["name"] for s in slots],
            "nextExecutableAction": "A new source-supported separation is required before another joint. Do not rerun exhausted placements.",
        })
    return rows


def semantics() -> list:
    prior = json.loads((V7 / "class-semantics.json").read_text(encoding="utf-8"))
    rows = []
    for rec in prior:
        name = Path(rec["path"]).name
        observed = OBSERVED.get(rec["classId"], {}).get(name)
        if observed is None:
            semantic, status, note = rec.get("semantic"), "UNVERIFIED", "No visual label was recorded for this crop in v8."
        else:
            semantic, status, note = observed
        rows.append({
            "id": rec["id"],
            "class": rec["classId"],
            "status": status,
            "observedAnatomy": semantic,
            "side": "UNKNOWN",
            "supportedPose": "SOURCE_PAINTED_ONLY",
            "source": rec["source"],
            "sourceROI": {"box": rec.get("crop"), "convention": "half-open", "frame": "native sheet pixels"},
            "crop": {"path": rec["path"], "sha256": rec["sha256"], "dimensions": rec["dimensions"]},
            "sourceToCrop": {"kind": "translation", "origin": rec.get("crop", [None, None])[:2], "scale": 1, "rotation": 0},
            "parentChildPivot": None,
            "neutralTransform": None,
            "drawOrder": None,
            "joints": "NOT_RUN",
            "note": note,
            "gates": {
                "semanticInspection": {"gate": "PASS" if observed else "UNVERIFIED", "evidence": "v7 contact sheet plus this label"},
                "articulation": {"gate": "NOT_APPLICABLE", "reason": "Crop is not a measured joint."},
                "fullBody": {"gate": "FAIL", "evidence": "No single-scale chain."},
                "owner": {"gate": "UNVERIFIED", "evidence": "No owner acceptance recorded."},
            },
        })
    (QA / "class-semantics-v8.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    return rows


def binding(interface_rows: list) -> dict:
    checked = []
    failed = []
    for rec in interface_rows:
        path = rec.get("path")
        expect = rec.get("sha256")
        if not path or not expect:
            continue
        file = ROOT / path
        if not file.is_file():
            failed.append({"path": path, "error": "missing"})
            continue
        digest = sha256(file)
        try:
            with Image.open(file) as im:
                im.verify()
            with Image.open(file) as im:
                im.load()
            decode = "PASS"
        except Exception as exc:  # noqa: BLE001 — binding must record the decoder error
            decode = str(exc)
        ok = digest == expect and decode == "PASS"
        checked.append({"path": path, "sha256": digest, "matchesInterface": digest == expect, "decode": decode})
        if not ok:
            failed.append(checked[-1])
    return {"checked": len(checked), "failed": failed, "rows": checked}


def main() -> None:
    QA.mkdir(parents=True, exist_ok=True)
    (QA / "terrain").mkdir(exist_ok=True)
    libs = versions()
    overflow = synthetic_overflow()
    if not overflow["passed"] or not overflow["controlBothTrue"]:
        raise SystemExit("synthetic overflow regression failed")
    (QA / "arithmetic-regression.json").write_text(json.dumps(overflow, indent=2), encoding="utf-8")

    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    contract_hash = sha256(CONTRACT)
    preserve_before = {
        "contract": contract_hash,
        "v7Interface": sha256(INTERFACE_V7),
        "healerBoot": sha256(ROOT / "assets/derivatives/rigs/v7/healer/boot.png"),
        "draft": sha256(DRAFT),
    }
    scenes = []
    changed_pixels = 0
    changed_scenes = 0
    for item in manifest["items"]:
        print("scene", item["id"], flush=True)
        row = trace_scene(item, contract)
        scenes.append(row)
        delta = (row.get("blueCandidateArithmetic") or {}).get("pixelsChanged", 0)
        changed_pixels += delta
        changed_scenes += int(delta > 0)
    arith = {
        "scenes": len(scenes),
        "changedScenes": changed_scenes,
        "candidatePixelsChanged": changed_pixels,
        "stage": "legal-grid candidate mask before connected-component filtering",
        "not": "river, bank, or runtime accuracy",
    }
    (QA / "arithmetic-scene-diff.json").write_text(json.dumps({"summary": arith, "rows": [
        {"id": s["id"], **s.get("blueCandidateArithmetic", {})} for s in scenes
    ]}, indent=2), encoding="utf-8")

    # Contact sheet of overlays for review.
    thumbs = []
    for s in scenes:
        im = Image.open(ROOT / s["overlay"]).convert("RGB")
        im.thumbnail((200, 120))
        thumbs.append((s["id"], im))
    cols = 4
    sheet = Image.new("RGB", (cols * 210, ((len(thumbs) + cols - 1) // cols) * 140), (30, 30, 30))
    draw = ImageDraw.Draw(sheet)
    for i, (name, im) in enumerate(thumbs):
        x, y = (i % cols) * 210, (i // cols) * 140
        sheet.paste(im, (x + 4, y + 16))
        draw.text((x + 4, y + 2), name[-28:], fill=(230, 230, 230))
    sheet.save(QA / "terrain" / "all32-overlay-contact.png")

    chains = assemblies()
    sem = semantics()
    head_attempt = ROOT / "assets/derivatives/rigs/v7/paladin/head_three_quarter.png"
    v7 = json.loads(INTERFACE_V7.read_text(encoding="utf-8"))
    measurements = json.loads((V7 / "measurements.json").read_text(encoding="utf-8"))
    joint_by_pair = {j["pair"]: j for j in measurements.get("joints", [])}
    ranger = measurements.get("rangerConfirm")
    ready = []
    for rec in v7["readySubset"]:
        item = dict(rec)
        pair = {
            "healer-leg-greave": "healer_leg_greave",
            "healer-greave-boot": "healer_greave_boot",
            "paladin-knee-greave": "paladin_knee_greave",
            "ranger-sleeve-vambrace": "ranger_sleeve_vambrace",
        }.get(rec["id"])
        src = joint_by_pair.get(pair) if pair != "ranger_sleeve_vambrace" else ranger
        if src:
            item["coordinateFrames"] = {
                "boxConvention": "half-open",
                "sharedPivotCanvas": src.get("sharedPivot"),
                "canvas": src.get("canvas"),
                "uniformScale": src.get("uniformScale", 1),
                "rotationDegreesTested": src.get("anglesTested"),
                "cuffParent": src.get("cuffParent") or src.get("parentCuff"),
                "cuffChild": src.get("cuffChild") or src.get("childCuff"),
                "insertionOfCuff": src.get("insertionOfCuff"),
                "transverseOfCuff": src.get("transverseOfCuff"),
                "parent": src.get("parent"),
                "child": src.get("child"),
                "drawOrder": "parent over child where parent alpha > 16",
                "side": "UNKNOWN",
            }
            if pair == "ranger_sleeve_vambrace":
                item["coordinateFrames"]["insertionOfCuff"] = 0.30
                item["coordinateFrames"]["transverseOfCuff"] = 0.05
                item["coordinateFrames"]["note"] = "Reused measured placement. No new angle search."
        item["gates"] = {
            "sourceBinding": {"gate": "UNVERIFIED", "evidence": "filled by binding check"},
            "articulation": {"gate": "NOT_APPLICABLE" if "joint" not in rec.get("use", "") and "angles" not in rec else "PASS", "reason": rec.get("limit", "")},
            "fullBody": {"gate": "NOT_APPLICABLE", "reason": "Row is not a whole rig."},
            "owner": {"gate": "UNVERIFIED", "evidence": "No owner acceptance on this row."},
        }
        ready.append(item)

    draft = json.loads(DRAFT.read_text(encoding="utf-8"))
    roles = [r.get("canonicalRole") for r in draft.get("requests", draft.get("roles", []))]
    # The clarification file stores roles in more than one list. Collect canonicalRole values in order.
    found_roles = []
    def walk(node):
        if isinstance(node, dict):
            if "canonicalRole" in node and isinstance(node["canonicalRole"], str):
                found_roles.append(node["canonicalRole"])
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)
    walk(draft)
    unique_roles = []
    for role in found_roles:
        if role not in unique_roles:
            unique_roles.append(role)

    interface = {
        "version": "8.0-local-delivery-20261005",
        "supersedes": "docs/plan/IMAGE-DELIVERY-INTERFACE-V7-2026-10-05.json",
        "codeAIHandoffReady": False,
        "reason": "Ready rows remain individually usable. Whole delivery is false: class chains are incomplete, scene traces are partial color/luminance evidence, and exhausted matte and joint methods stay failed.",
        "noNewPaidScope": True,
        "providerCalls": 0,
        "librariesMeasuredThisRun": libs,
        "accountingHistorical": {"protectedExposureUSD": 70.7012, "unknownLiabilitiesUSD": 0.287224, "invoices": "UNKNOWN"},
        "boxConvention": "half-open [x0, y0, x1, y1)",
        "affineFormula": "x'=a*x+c*y+e; y'=b*x+d*y+f",
        "activeKingdomAffine": KINGDOM_AFFINE,
        "activeHallScale": HALL_SCALE,
        "geometryEdited": False,
        "codeConsumersEdited": False,
        "readySubset": ready,
        "classChains": chains,
        "classSemantics": "qa/image-local-delivery-v8-20261005/class-semantics-v8.json",
        "classSemanticCount": len(sem),
        "scenes": [
            {k: s[k] for k in (
                "id", "mode", "age", "biome", "status", "promoted", "source", "coordinateFrames",
                "paintedRoadState", "paintedRoadMethod", "paintedRoadPolylines", "paintedRiverState", "paintedRiverPolylines",
                "paintedBankState", "paintedBankPolylines", "paintedBridgeState", "paintedBridgeDeckPolygons",
                "paintedBridgeApproachState", "paintedBridgeApproachPolygons", "walkableState", "walkablePolygons",
                "blockedState", "staticObstacleState", "mutableContent", "residual", "legalBridgeVsDeckIou",
                "proposal", "overlay", "proposedCamera", "runtimeAcceptance", "ownerAcceptance", "limitations",
                "stoneInspection", "legalAffineActive", "hallScaleActive",
            ) if k in s}
            for s in scenes
        ],
        "replacementDraft": {
            "path": "docs/plan/REPLACEMENT-DRAFT-THREE-ROLES-V6-CLARIFICATION-2026-10-04.json",
            "sha256": preserve_before["draft"],
            "status": draft.get("status"),
            "gate": "OWNER_BUDGET_AUTHORIZATION_REQUIRED",
            "roles": unique_roles,
            "addedRoles": [],
            "submitted": False,
        },
        "paladinHead": {
            "status": "FAIL",
            "recipe": "qa/image-local-continuation-20261005/recipes/paladin-head_three_quarter.json",
            "recipeNames": "assets/derivatives/rigs/v7/paladin/head_three_quarter.png",
            "bytesPresent": head_attempt.is_file(),
            "reproducibility": "FAILED_BYTES_UNAVAILABLE" if not head_attempt.is_file() else "PRESENT",
            "republished": False,
        },
        "exhausted": [
            {"id": "knight-thigh-greave", "attempts": 13, "method": "12 placements plus one 0.45 cuff correction", "state": "failed"},
            {"id": "paladin-thigh-knee", "attempts": 1, "method": "scale 1 cuff ratio", "state": "failed"},
            {"id": "paladin-greave-boot", "attempts": 1, "method": "scale 1 cuff ratio", "state": "failed"},
            {"id": "troop-industrial-melee-matte", "attempts": 1, "method": "restore dark coat from v5", "state": "partial", "newMethod": None},
            {"id": "troop-modern-heavy", "state": "partial", "newMethod": None},
            {"id": "troop-modern-ranged", "state": "partial", "role": "snow scene illustration"},
        ],
        "arithmetic": arith,
        "checkpoint": "qa/image-local-delivery-v8-20261005/checkpoint.json",
        "guidesStillMissing": [
            {"path": "qa/recovery-executor-20261003/guides/kingdom-stone-day1-composition-v4-guide.png", "bytes": 52050, "sha256": "609d3195018ccf448f339f79e45fe90b9e5adfb2859674e40383144d2106f848"},
            {"path": "qa/recovery-executor-20261003/guides/kingdom-stone-day1-composition-v5-guide.png", "bytes": 33988, "sha256": "673492a6a1c6780eb77d9b0b24f7eefe30a98dc119c7fbee9e3edef088b8c1ff"},
        ],
    }
    # Binding uses ready subset plus scene sources plus boot.
    bind_rows = [{"path": r["path"], "sha256": r["sha256"]} for r in ready if r.get("path") and r.get("sha256")]
    bind_rows.append({"path": "assets/derivatives/rigs/v7/healer/boot.png", "sha256": preserve_before["healerBoot"]})
    for s in scenes:
        if s.get("source"):
            bind_rows.append({"path": s["source"]["path"], "sha256": s["source"]["sha256"]})
    report = binding(bind_rows)
    interface["binding"] = {"checked": report["checked"], "failed": report["failed"], "scope": "v8 readySubset paths, healer boot, and 32 scene sources. Not a full historical-original audit."}
    INTERFACE_V8.write_text(json.dumps(interface, indent=2), encoding="utf-8")

    preserve_after = {
        "contract": sha256(CONTRACT),
        "v7Interface": sha256(INTERFACE_V7),
        "healerBoot": sha256(ROOT / "assets/derivatives/rigs/v7/healer/boot.png"),
        "draft": sha256(DRAFT),
    }
    checkpoint_items = []
    for rec in ready:
        checkpoint_items.append({
            "id": rec["id"], "sourceHash": rec.get("sha256"), "state": "reused",
            "method": "v7 ready row, rebound in v8", "attempts": 0, "exhausted": False,
            "evidence": rec.get("diagnostics", []), "remainingGap": rec.get("limit"),
            "nextExecutableAction": None,
        })
    for chain in chains:
        checkpoint_items.append({
            "id": chain["id"], "sourceHash": chain["diagramSha256"], "state": "partial",
            "method": "visual chain diagram from existing crops", "attempts": 1, "exhausted": False,
            "evidence": [chain["diagram"]], "remainingGap": "full body FAIL",
            "nextExecutableAction": chain["nextExecutableAction"],
        })
    for s in scenes:
        checkpoint_items.append({
            "id": s["id"], "sourceHash": (s.get("source") or {}).get("sha256"), "state": "partial",
            "method": "widened blue component plus one relative-luminance skeleton",
            "attempts": 1, "exhausted": s.get("paintedRoadState", "").startswith("UNRESOLVABLE"),
            "evidence": [s.get("overlay")],
            "remainingGap": s.get("paintedRoadState"),
            "nextExecutableAction": None if s.get("paintedRoadState") == "TRACED_GRADIENT_RIDGE" else "A different source-supported trace is required. Do not threshold-sweep this method.",
        })
    checkpoint_items.append({
        "id": "three-role-draft", "sourceHash": preserve_before["draft"], "state": "blocked",
        "method": "unchanged draft", "attempts": 0, "exhausted": False,
        "evidence": [str(DRAFT.relative_to(ROOT)).replace("\\", "/")],
        "remainingGap": "OWNER_BUDGET_AUTHORIZATION_REQUIRED",
        "nextExecutableAction": None,
    })
    checkpoint = {
        "updated": "2026-10-05",
        "providerCalls": 0,
        "codeAIHandoffReady": False,
        "librariesMeasuredThisRun": libs,
        "inputHashesChanged": [k for k, v in preserve_before.items() if preserve_after[k] != v],
        "preserve": {"before": preserve_before, "after": preserve_after},
        "arithmetic": arith,
        "counts": {
            "reused": sum(i["state"] == "reused" for i in checkpoint_items),
            "partial": sum(i["state"] == "partial" for i in checkpoint_items),
            "failed": 0,
            "blocked": sum(i["state"] == "blocked" for i in checkpoint_items),
            "scenes": len(scenes),
            "proposals": sum(1 for s in scenes if s.get("proposal")),
        },
        "items": checkpoint_items,
    }
    # Exhausted failures are explicit rows even though their state is not in the ready list.
    for row in interface["exhausted"]:
        checkpoint["items"].append({
            "id": row["id"], "sourceHash": None, "state": "failed" if row["state"] == "failed" else "partial",
            "method": row.get("method", "no new method"), "attempts": row.get("attempts", 0),
            "exhausted": True, "evidence": [], "remainingGap": row["state"],
            "nextExecutableAction": None,
        })
    checkpoint["counts"]["failed"] = sum(i["state"] == "failed" for i in checkpoint["items"])
    checkpoint["counts"]["partial"] = sum(i["state"] == "partial" for i in checkpoint["items"])
    (QA / "checkpoint.json").write_text(json.dumps(checkpoint, indent=2), encoding="utf-8")
    (QA / "scenes.json").write_text(json.dumps(scenes, indent=2), encoding="utf-8")
    print(json.dumps({"libs": libs, "arithmetic": arith, "proposals": checkpoint["counts"]["proposals"], "bindingFailed": len(report["failed"]), "preserveChanged": checkpoint["inputHashesChanged"], "roles": unique_roles}, indent=2))


if __name__ == "__main__":
    main()
