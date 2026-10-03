"""Correct the first Stone delivery set without buying or overwriting rejected outputs.

Originals, rejected v1 derivatives, shared guides, collection records and provider
files are not modified. New derivatives, terrain, composites and evidence use new paths.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/delivery/stone-starter-20261003'
EVIDENCE = ROOT / 'qa/recovery-correction-20261003'
A_LIN = np.array([[60.0, 25.0], [-10.0, 35.0]], dtype=np.float64)
A_FULL = np.array([60.0, -10.0, 25.0, 35.0, 170.0, 165.0])
NEUTRAL = (110, 132, 104)
CONTRACT_HASH_SOURCE = ROOT / 'docs/plan/IMPLEMENTATION-CONTRACT.json'

TARGETS = {
    'skill-offense': ('production-03-20261003', 'assets/production/production-03-20261003/images/04-skill-offense.png', '594fc35135244184a2c685ff6ac243dfe4b5ff9c846e8e0a92ea60b816cf11cf', None),
    'resource-food': ('production-01-20261003', 'assets/production/production-01-20261003/images/26-resource-food.png', 'd3287f62b9850e4dbab0f3a132c1abacabfe89932eb9ed9bc76d1496bdb0716f', None),
    'resource-wood': ('production-01-20261003', 'assets/production/production-01-20261003/images/27-resource-wood.png', 'a91c3a395af420fdbc53ecb9b330cc11633bb61b5b46316163ea2331b3bb82d2', None),
    'resource-stone': ('production-01-20261003', 'assets/production/production-01-20261003/images/28-resource-stone.png', '2c819abba15fa22311e039e2ad661a04399791a53ac51aa5f12c9e4dbfef6d5e', None),
    'resource-gold': ('production-01-20261003', 'assets/production/production-01-20261003/images/29-resource-gold.png', 'e8cb7967df838fd84168e87dff6ac98c66c1bdfaab0dfbac84f81d978468f168', None),
    'townhall-stone': ('production-03-20261003', 'assets/production/production-03-20261003/images/03-townhall-stone.png', '2809db2bc0045cfeae0ae73b675b0236b03f0f0f369009c90430af62d22c1b5e', (3.0, 1.5, 'townhall', 10)),
    'farm-stone': ('production-03-20261003', 'assets/production/production-03-20261003/images/27-farm-stone.png', 'a8c004398448e549d9b4e737801e16c5186965e5f35f22d7dd46c61efa3ae0e3', (1.4, 1.2, 'P01', 22)),
    'lumber-stone': ('production-03-20261003', 'assets/production/production-03-20261003/images/28-lumber-stone.png', '63fc579f757d8930a10252db38622ccafab35e93679554e4afcbebd535a0fd38', (1.4, 1.2, 'P04', 12)),
    'quarry-stone': ('production-03-20261003', 'assets/production/production-03-20261003/images/29-quarry-stone.png', 'da5b9d5ccb9c3422d3058dc2a7424da4e74a4732ed72207da7217ec283d6487b', (1.4, 1.2, 'P10', 34)),
    'mine-stone': ('production-03-20261003', 'assets/production/production-03-20261003/images/30-mine-stone.png', 'ff1daba56ba7b3e1f40cdb85bcd9ace519260670017572e1123e74f24aa53731', (1.4, 1.2, 'P14', 30)),
}
V1 = {
    'skill-offense': 'a1454dfb7cc41a97aa63c6f6b3b0095d8d7a381e2c48725dc487268821c162f5',
    'resource-food': '2a4a2809843c099d91d0122fafd9283c2eef6bc2eec40aeaa6a2c5653690fdc9',
    'resource-wood': '2259a27f3425825cfc2ce6750aa441fd5b98829be29c58653bfcfb1ef7fc13e6',
    'resource-stone': 'b06bf8b21b6381cfec8eeb0da5206d1d537ec24d65f9f91dd4988d684e82c189',
    'resource-gold': '254ec836e985bd4cc2d93f15a76a3971e063bcaa2120636771f513c99db21ab3',
    'townhall-stone': '0cac3bd09dbb4c8eb88824f02ee01b951c21d2f6f85f024430e080763794f321',
    'farm-stone': '65dfe0a40a82d142be7e558ea53622d93550b11328e3689525519f35a0070d23',
    'lumber-stone': '6797ecc092a4abb934ee2fbc10d0197bcd53ac8999ab902de757747ad72a868d',
    'quarry-stone': '59b5b26bfc3d6f02353138150351ede4e9395341fec7fbc757859c1f6fbdd30e',
    'mine-stone': 'f82b2258549e601d57725ebd41da69876906e71270378df0d1a796902a23c03f',
}
TERRAIN_V1 = 'caa3c448cc61dd0459642f8c1007205dc0dd60c69894d9baeceb2e14de2cf24e'
TERRAIN_SRC = '6cb13e0d4deaf2924a1b089d57356c973b4998621e59a66a8d3edca1b03daad1'
EDGE_BOXES = {
    'skill-offense': (280, 152, 792, 192),
    'resource-stone': (330, 155, 720, 330),
    'resource-food': (150, 110, 470, 340),
    'resource-wood': (580, 700, 920, 850),
    'resource-gold': (550, 745, 870, 865),
    'farm-stone': (510, 225, 880, 415),
    'lumber-stone': (800, 390, 1000, 550),
    'quarry-stone': (350, 40, 720, 275),
    'mine-stone': (600, 280, 950, 450),
    'townhall-stone': (470, 840, 980, 1010),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def project(x, y):
    a, b, c, d, e, f = A_FULL
    return np.array([a * x + c * y + e, b * x + d * y + f], dtype=np.float64)


def polygon(rect):
    x, y, w, h = rect
    return np.array([project(x, y), project(x + w, y), project(x + w, y + h), project(x, y + h)], np.float64)


def load_rgba(path: Path) -> np.ndarray:
    return np.array(Image.open(path).convert('RGBA'))


def save_rgba(path: Path, rgba: np.ndarray) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(rgba, 'RGBA').save(path)
    return sha256(path)


def magenta_mask(rgb: np.ndarray) -> np.ndarray:
    red = rgb[:, :, 0].astype(np.int16)
    green = rgb[:, :, 1].astype(np.int16)
    blue = rgb[:, :, 2].astype(np.int16)
    # Darkened backdrop still has green collapsed under both red and blue.
    fringe = (green < 70) & (red > 50) & (blue > 35) & (red > green + 28) & (blue > green + 22) & (blue > 45)
    bright = (blue > green + 16) & (blue > 95) & (red > 90) & (green < 180)
    pure = (red > 170) & (blue > 170) & (green < 90)
    return fringe | bright | pure


def repair_cutout(asset_id: str, rgba: np.ndarray, reach: int | None) -> tuple[np.ndarray, dict]:
    """Localized spill and plinth repair. Does not re-key the whole subject."""
    out = rgba.copy()
    red = out[:, :, 0].astype(np.int16)
    green = out[:, :, 1].astype(np.int16)
    blue = out[:, :, 2].astype(np.int16)
    alpha = out[:, :, 3]
    opaque = alpha > 16
    spill = magenta_mask(out[:, :, :3]) & (alpha > 0)
    transparent = (alpha <= 16).astype(np.uint8)
    distance = cv2.distanceTransform(1 - transparent, cv2.DIST_L2, 3)
    # Pure backdrop still attached to transparency is not object color.
    pure = (red > 175) & (blue > 175) & (green < 90) & (alpha > 0)
    knock = (pure & (distance <= 8)) | (spill & (distance <= 2.2) & (blue > green + 35))
    if asset_id == 'resource-gold':
        purple_base = (blue > red) & (blue > green + 12) & (blue > 80) & (alpha > 0)
        amount, labels = cv2.connectedComponents(purple_base.astype(np.uint8), 8)
        border = np.zeros(alpha.shape, bool)
        border[0] = border[-1] = border[:, 0] = border[:, -1] = True
        # Purple that reaches the exterior through the spill is backdrop, including the coin-stand fringe.
        exterior = (alpha <= 16) | knock
        ext_labels = np.unique(labels[cv2.dilate(exterior.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0])
        ext_labels = ext_labels[ext_labels != 0]
        knock = knock | (np.isin(labels, ext_labels) & purple_base & (distance <= 14))
    # Fibres, rope and wheat stay present. Only their reflected blue is reduced.
    if asset_id == 'skill-offense':
        knock = pure | (spill & (distance <= 1.8))
    elif asset_id in ('resource-food', 'resource-wood', 'resource-stone', 'quarry-stone'):
        knock = (pure & (distance <= 3)) | (spill & (distance <= 1.4) & (green < 45) & (blue > 100))
    out[:, :, 3][knock] = 0
    # Despill anywhere the backdrop channel still exceeds the object. Do not scale that
    # excess by the red channel: wheat and coin rims are red and would keep the pink.
    remain = magenta_mask(out[:, :, :3]) & (out[:, :, 3] > 16)
    if asset_id == 'skill-offense':
        remain = remain & (distance <= 2.5)
    elif asset_id not in ('resource-gold', 'resource-food', 'townhall-stone', 'farm-stone', 'lumber-stone', 'mine-stone'):
        remain = remain & (distance <= 5)
    blue_now = out[:, :, 2].astype(np.int16)
    green_now = out[:, :, 1].astype(np.int16)
    red_now = out[:, :, 0].astype(np.int16)
    out[:, :, 2][remain] = np.minimum(blue_now[remain], np.maximum(green_now[remain] - 4, 0)).astype(np.uint8)
    # Reflected magenta on gold reads as red+blue with no green. Move it toward the coin's own red.
    if asset_id == 'resource-gold':
        moved = remain & (green_now < 80)
        out[:, :, 1][moved] = np.maximum(green_now[moved], red_now[moved] // 4).astype(np.uint8)
    if asset_id == 'resource-food':
        hot = (out[:, :, 3] > 16) & (red_now > 190) & (green_now + 24 < red_now) & (distance <= 4)
        out[:, :, 1][hot] = np.minimum(255, (green_now[hot] + red_now[hot]) // 2).astype(np.uint8)
    soil_removed = 0
    if reach is not None:
        out, soil_removed = trim_plinth(out, reach, asset_id)
        # New silhouette can expose another line of key color. Knock only that line.
        alpha = out[:, :, 3]
        spill = magenta_mask(out[:, :, :3]) & (alpha > 16)
        transparent = (alpha <= 16).astype(np.uint8)
        distance = cv2.distanceTransform(1 - transparent, cv2.DIST_L2, 3)
        edge = spill & (distance <= 2.0)
        out[:, :, 3][edge] = 0
        soft = spill & (distance <= 4.0) & (out[:, :, 3] > 16)
        blue = out[:, :, 2].astype(np.int16)
        green = out[:, :, 1].astype(np.int16)
        out[:, :, 2][soft] = np.minimum(blue[soft], green[soft] + 6).astype(np.uint8)
    # Distance to the nearest transparent pixel. A transform of the transparent mask is 0
    # on every opaque pixel, so it cannot be used as an edge test.
    alpha_now = out[:, :, 3]
    distance_now = cv2.distanceTransform((alpha_now > 16).astype(np.uint8), cv2.DIST_L2, 3)
    red_now = out[:, :, 0].astype(np.int16)
    green_now = out[:, :, 1].astype(np.int16)
    blue_now = out[:, :, 2].astype(np.int16)
    dark_fringe = (alpha_now > 16) & (distance_now > 0) & (distance_now <= 2.0) & (red_now > green_now + 18) & (blue_now > green_now + 8) & (green_now < 95) & (red_now > 40)
    protected_interior = (distance_now > 6) & (red_now > 60) & (green_now > 40) & (blue_now < 160)
    dark_fringe = dark_fringe & ~protected_interior
    if asset_id != 'resource-gold':
        out[:, :, 3][dark_fringe] = 0
        knock = knock | dark_fringe
    info = spill_report(out)
    info['plinthPixelsRemoved'] = soil_removed
    info['knockedPixels'] = int(knock.sum())
    return out, info


def trim_plinth(rgba: np.ndarray, reach: int, asset_id: str) -> tuple[np.ndarray, int]:
    color = rgba[:, :, :3]
    alpha = rgba[:, :, 3]
    foreground = alpha > 16
    red = color[:, :, 0].astype(np.int16)
    green = color[:, :, 1].astype(np.int16)
    blue = color[:, :, 2].astype(np.int16)
    rgba = rgba.copy()
    removed = np.zeros(foreground.shape, bool)
    if asset_id in ('townhall-stone', 'lumber-stone'):
        # Border-connected bare earth. Gray stone, timber and thatch are not brown, so the flood stops at the structure.
        brown = foreground & (red > 55) & (green > 35) & (blue < 145) & (red + 6 > green) & (green > blue + 6) & ((red - blue) > 18)
        edge = np.zeros(foreground.shape, bool)
        edge[0] = edge[-1] = edge[:, 0] = edge[:, -1] = True
        marker = (brown & edge).astype(np.uint8)
        allowed = brown.astype(np.uint8)
        kernel = np.ones((3, 3), np.uint8)
        for _ in range(800):
            grown = cv2.bitwise_and(cv2.dilate(marker, kernel), allowed)
            if np.array_equal(grown, marker):
                break
            marker = grown
        removed = marker.astype(bool)
        border = np.zeros(foreground.shape, bool)
        border[:4] = border[-4:] = border[:, :4] = border[:, -4:] = True
        removed = removed | (foreground & border)
        rgba[:, :, 3][removed] = 0
    elif asset_id == 'farm-stone':
        # The planted yard is the subject. Do not cut below the roof lip.
        removed = np.zeros(foreground.shape, bool)
    # Keep the largest remaining component plus nearby structure islands.
    fg = rgba[:, :, 3] > 16
    amount, labels, stats, _ = cv2.connectedComponentsWithStats(fg.astype(np.uint8), 8)
    if amount > 1:
        largest = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
        keep = labels == largest
        for index in range(1, amount):
            if int(stats[index, cv2.CC_STAT_AREA]) > 40:
                keep[labels == index] = True
        rgba[:, :, 3][fg & ~keep] = 0
        removed = removed | (fg & ~keep)
    return rgba, int(removed.sum())


def spill_report(rgba: np.ndarray) -> dict:
    alpha = rgba[:, :, 3]
    transparent = (alpha <= 16).astype(np.uint8)
    distance = cv2.distanceTransform(1 - transparent, cv2.DIST_L2, 3)
    spill = magenta_mask(rgba[:, :, :3]) & (alpha > 16)
    edge = spill & (distance <= 3)
    return {
        'edgeSpillPixels': int(edge.sum()),
        'opaqueSpillPixels': int(spill.sum()),
        'opaqueFraction': round(float((alpha > 16).mean()), 4),
    }


def top_ground_mask(rgba: np.ndarray) -> np.ndarray:
    alpha = rgba[:, :, 3] > 24
    red = rgba[:, :, 0].astype(np.int16)
    green = rgba[:, :, 1].astype(np.int16)
    blue = rgba[:, :, 2].astype(np.int16)
    groundish = alpha & (red > 60) & (green > 40) & (blue < 170) & (green + 25 > blue)
    thatch = alpha & (red > 145) & (green > 105) & (blue < 120) & (red > blue + 30)
    groundish = groundish & ~thatch
    if int(groundish.sum()) < 80:
        groundish = alpha
    height, width = alpha.shape
    lip = np.full(width, height, np.int32)
    ys, xs = np.where(groundish)
    for x, y in zip(xs.tolist(), ys.tolist()):
        if y < lip[x]:
            lip[x] = y
    band = np.zeros_like(groundish)
    for x, y0 in enumerate(lip.tolist()):
        if y0 < height:
            band[y0:min(height, y0 + 10), x] = True
    band &= groundish
    band = cv2.morphologyEx(band.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8)) > 0
    amount, labels, stats, _ = cv2.connectedComponentsWithStats(band.astype(np.uint8), 8)
    if amount > 1:
        largest = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
        band = labels == largest
    return band


def measure_landmarks(rgba: np.ndarray, footprint: tuple[float, float]) -> dict:
    fw, fh = footprint
    alpha = rgba[:, :, 3] > 32
    ys, xs = np.where(alpha)
    if len(xs) < 20:
        raise RuntimeError('No ground surface to measure')
    points = np.column_stack((xs, ys)).astype(np.float64)
    # Tips of the silhouette. On the contract camera a footprint parallelogram has
    # leftmost=q00, topmost=q10, bottommost=q01 and rightmost=q11.
    q00 = points[int(np.argmin(points[:, 0]))]
    q10 = points[int(np.argmin(points[:, 1]))]
    q01 = points[int(np.argmax(points[:, 1]))]
    q11 = points[int(np.argmax(points[:, 0]))]
    red = rgba[:, :, 0].astype(np.int16)
    green = rgba[:, :, 1].astype(np.int16)
    blue = rgba[:, :, 2].astype(np.int16)
    thatch = alpha & (red > 145) & (green > 105) & (blue < 125) & (red > blue + 25)
    ground_idx = np.where(~thatch[ys, xs])[0]
    top_source = 'silhouette-top'
    if len(ground_idx) > 80:
        ground_points = points[ground_idx]
        q10 = ground_points[int(np.argmin(ground_points[:, 1]))]
        top_source = 'highest non-thatch pixel'
    predicted = q00 + (q10 - q00) + (q01 - q00)
    fourth_error = float(np.linalg.norm(predicted - q11))
    b_axis = np.column_stack(((q10 - q00) / fw, (q01 - q00) / fh))
    determinant = float(np.linalg.det(b_axis))
    if abs(determinant) < 1e-6:
        raise RuntimeError('Measured ground axes are degenerate')
    placement = A_LIN @ np.linalg.inv(b_axis)
    singular = np.linalg.svd(placement, compute_uv=False)
    scale_ratio = float(singular.max() / max(singular.min(), 1e-8))
    rotation = nearest_similarity(placement)
    shear = float(np.linalg.norm(placement - rotation) / max(np.linalg.norm(placement), 1e-8))
    bottom = points[points[:, 1] >= np.percentile(points[:, 1], 72)]
    pivot = bottom.mean(axis=0)
    source_width = float(np.linalg.norm(q11 - q00))
    camera_width = float(np.linalg.norm(np.array([60.0, -10.0]) * fw))
    uniform = np.eye(2) * (camera_width / max(source_width, 1.0))
    use_full = fourth_error <= 18 and 0.5 <= scale_ratio <= 1.2 and shear <= 0.08 and float(singular.max()) < 1.5
    used = placement if use_full else uniform
    mode = 'D=A*inverse(B)' if use_full else 'uniform-width-fit'
    return {
        'q00': q00.tolist(),
        'q10': q10.tolist(),
        'q01': q01.tolist(),
        'q11': q11.tolist(),
        'predictedFourth': predicted.tolist(),
        'fourthCornerErrorPx': round(fourth_error, 3),
        'footprintWorld': [fw, fh],
        'sourceAxesB': b_axis.tolist(),
        'placementD': placement.tolist(),
        'placementUsed': used.tolist(),
        'placementMode': mode,
        'scaleRatio': round(scale_ratio, 4),
        'shear': round(shear, 4),
        'singularValues': [round(float(v), 4) for v in singular],
        'groundPivot': [round(float(pivot[0]), 3), round(float(pivot[1]), 3)],
        'guidePivotCopied': False,
        'landmarkMethod': 'Silhouette tips after plinth trim: leftmost q00, highest non-thatch q10, bottommost q01, rightmost q11. ' + top_source + '. Uniform width is recorded when those tips are not the contract parallelogram; it cannot pass registration.',
        'contactPoints': int(len(points)),
    }


def nearest_similarity(matrix: np.ndarray) -> np.ndarray:
    left, _values, right = np.linalg.svd(matrix)
    rotation = left @ right
    if np.linalg.det(rotation) < 0:
        right = right.copy()
        right[-1] *= -1
        rotation = left @ right
    scale = float(np.mean(np.linalg.svd(matrix, compute_uv=False)))
    return rotation * scale


def gate_registration(measurement: dict, placed_bounds, overlap: bool) -> tuple[str, str]:
    reasons = []
    if measurement['placementMode'] != 'D=A*inverse(B)':
        reasons.append(f"mode {measurement['placementMode']}")
    if measurement['fourthCornerErrorPx'] > 18:
        reasons.append(f"fourth corner {measurement['fourthCornerErrorPx']} px")
    if measurement['scaleRatio'] > 1.2:
        reasons.append(f"axis scale ratio {measurement['scaleRatio']}")
    if placed_bounds[1] < 0 or placed_bounds[3] > 768 or placed_bounds[0] < 0 or placed_bounds[2] > 1376:
        reasons.append(f"subject bounds {['%.1f' % v for v in placed_bounds]} leave the terrain")
    if overlap:
        reasons.append('neighbour overlap')
    if reasons:
        return 'FAIL', '; '.join(reasons)
    return 'PASS', 'Measured footprint closes, matches the camera axes, and stays inside the terrain without neighbour overlap.'


def place_matrix(measurement, site_rect):
    x, y, w, h = site_rect
    pivot = np.array(measurement['groundPivot'], dtype=np.float64)
    destination = project(x + w / 2, y + h / 2)
    linear = np.array(measurement['placementUsed'], dtype=np.float64)
    translation = destination - linear @ pivot
    return np.array([
        [linear[0, 0], linear[0, 1], translation[0]],
        [linear[1, 0], linear[1, 1], translation[1]],
    ], dtype=np.float64)


def blit(canvas: np.ndarray, rgba: np.ndarray, matrix: np.ndarray, shadow: np.ndarray | None = None):
    height, width = canvas.shape[:2]
    if shadow is not None:
        warped_shadow = cv2.warpAffine(shadow, matrix.astype(np.float32), (width, height), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
        strength = (warped_shadow.astype(np.float32) / 255.0) * 0.35
        canvas[:] = np.clip(canvas.astype(np.float32) * (1 - strength[..., None]), 0, 255).astype(np.uint8)
    warped = cv2.warpAffine(rgba, matrix.astype(np.float32), (width, height), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    alpha = warped[:, :, 3:4].astype(np.float32) / 255.0
    base = canvas.astype(np.float32)
    canvas[:] = np.clip(warped[:, :, :3].astype(np.float32) * alpha + base * (1 - alpha), 0, 255).astype(np.uint8)
    return warped[:, :, 3] > 16


def contact_shadow(measurement) -> np.ndarray:
    shadow = np.zeros((1024, 1024), np.uint8)
    corners = np.array([measurement[name] for name in ('q00', 'q10', 'q11', 'q01')], np.int32)
    cv2.fillConvexPoly(shadow, corners, 255)
    shadow = cv2.GaussianBlur(shadow, (0, 0), 3)
    return shadow


def placed_bounds(rgba: np.ndarray, matrix: np.ndarray):
    ys, xs = np.where(rgba[:, :, 3] > 16)
    if len(xs) == 0:
        return [0, 0, 0, 0], 0
    ones = np.ones(len(xs))
    placed = matrix @ np.vstack((xs, ys, ones))
    outside = int(((placed[0] < 0) | (placed[0] >= 1376) | (placed[1] < 0) | (placed[1] >= 768)).sum())
    return [float(placed[0].min()), float(placed[1].min()), float(placed[0].max()), float(placed[1].max())], outside


def annotate(rgba: np.ndarray, measurement: dict, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    base = Image.new('RGB', (1024, 1024), (20, 20, 20))
    base.paste(Image.fromarray(rgba, 'RGBA'), mask=Image.fromarray(rgba[:, :, 3]))
    draw = ImageDraw.Draw(base)
    points = [tuple(measurement[name]) for name in ('q00', 'q10', 'q11', 'q01')]
    draw.line(points + [points[0]], fill=(40, 220, 220), width=2)
    for name in ('q00', 'q10', 'q01', 'q11'):
        x, y = measurement[name]
        draw.ellipse((x - 4, y - 4, x + 4, y + 4), fill=(255, 210, 40))
        draw.text((x + 6, y - 12), f"{name} {x:.0f},{y:.0f}", fill=(255, 240, 200))
    px, py = measurement['groundPivot']
    draw.ellipse((px - 3, py - 3, px + 3, py + 3), outline=(255, 80, 80))
    draw.text((8, 8), measurement['placementMode'], fill=(220, 220, 220))
    base.save(path)


def three_backgrounds(rgba: np.ndarray, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    height, width = rgba.shape[:2]
    sheet = Image.new('RGB', (width * 3, height), (0, 0, 0))
    sprite = Image.fromarray(rgba, 'RGBA')
    for index, color in enumerate(((0, 0, 0), (255, 255, 255), NEUTRAL)):
        tile = Image.new('RGB', (width, height), color)
        tile.paste(sprite, mask=sprite.getchannel('A'))
        sheet.paste(tile, (index * width, 0))
    sheet.save(path)


def edge_crop(rgba: np.ndarray, box, path: Path, label: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    sprite = Image.fromarray(rgba, 'RGBA').crop(box)
    width, height = sprite.size
    sheet = Image.new('RGB', (width * 3, height + 22), (28, 28, 28))
    draw = ImageDraw.Draw(sheet)
    for index, color in enumerate(((0, 0, 0), (255, 255, 255), NEUTRAL)):
        tile = Image.new('RGBA', (width, height), color + (255,))
        tile.alpha_composite(sprite)
        sheet.paste(tile.convert('RGB'), (index * width, 22))
        draw.text((index * width + 4, 4), f'{label} {box} RGB{color}', fill=(255, 255, 255))
    sheet.save(path)


def fit_icon(rgba: np.ndarray, target: int) -> Image.Image:
    alpha = rgba[:, :, 3]
    ys, xs = np.where(alpha > 16)
    crop = rgba[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    scale = target / max(crop.shape[0], crop.shape[1])
    resized = cv2.resize(crop, (max(1, round(crop.shape[1] * scale)), max(1, round(crop.shape[0] * scale))), interpolation=cv2.INTER_AREA)
    return Image.fromarray(resized, 'RGBA')


def font(size: int):
    for name in ('segoeui.ttf', 'arial.ttf'):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def draw_ui(resources: dict[str, np.ndarray], offense: np.ndarray, size: tuple[int, int]) -> np.ndarray:
    width, height = size
    image = Image.new('RGB', size, (24, 32, 34))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, width, 28), fill=(18, 26, 28))
    text_font = font(14)
    cursor = 12
    labels = [('Food', 250), ('Wood', 250), ('Stone', 160), ('Gold', 150)]
    keys = ['resource-food', 'resource-wood', 'resource-stone', 'resource-gold']
    for (label, amount), key in zip(labels, keys):
        glyph = fit_icon(resources[key], 18)
        image.paste(glyph, (cursor, 5), glyph)
        draw.text((cursor + 22, 6), f'{label} {amount}', fill=(236, 226, 204), font=text_font)
        cursor += 22 + 8 + int(draw.textlength(f'{label} {amount}', font=text_font)) + 16
    emblem = fit_icon(offense, 64)
    panel_x = max(16, width - 280)
    draw.rounded_rectangle((panel_x, 48, width - 16, 140), radius=6, fill=(28, 38, 40), outline=(116, 98, 64))
    image.paste(emblem, (panel_x + 12, 62), emblem)
    draw.text((panel_x + 88, 78), 'Offense', fill=(236, 226, 204), font=font(16))
    draw.text((panel_x + 88, 100), 'Reference amounts', fill=(196, 176, 132), font=text_font)
    draw.text((12, height - 24), 'Reference start amounts. Owner acceptance is pending.', fill=(168, 160, 140), font=text_font)
    return np.array(image)


def _stamp(image: np.ndarray, comp: np.ndarray, rng: np.random.Generator):
    ring = cv2.dilate(comp, np.ones((17, 17), np.uint8)) & (comp == 0)
    samples = image[ring > 0]
    ys, xs = np.where(comp > 0)
    if len(samples) < 30 or len(ys) == 0:
        return 0
    med = np.median(samples, axis=0)
    noise = rng.normal(0, 5, size=(len(ys), 3))
    image[ys, xs] = np.clip(med + noise, 0, 255).astype(np.uint8)
    return int(len(ys))


def repair_terrain(rgb: np.ndarray, sites: list[dict]) -> tuple[np.ndarray, dict]:
    repaired = rgb.copy()
    height, width = repaired.shape[:2]
    site_mask = np.zeros((height, width), np.uint8)
    polys = []
    for site in sites:
        poly = np.round(polygon(site['rect'])).astype(np.int32)
        polys.append(poly)
        cv2.fillPoly(site_mask, [poly], 255)
    pads = cv2.dilate(site_mask, np.ones((11, 11), np.uint8))
    rng = np.random.default_rng(20261003)
    stamped = _stamp(repaired, pads, rng)
    hull = cv2.convexHull(np.concatenate(polys))
    plateau = np.zeros((height, width), np.uint8)
    cv2.fillConvexPoly(plateau, hull, 255)
    plateau = cv2.dilate(plateau, np.ones((28, 28), np.uint8))
    hsv = cv2.cvtColor(repaired, cv2.COLOR_RGB2HSV)
    hue, sat, val = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]
    thatch = ((hue >= 8) & (hue <= 28) & (sat >= 50) & (val >= 70) & (plateau > 0)).astype(np.uint8)
    thatch = cv2.morphologyEx(thatch, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    amount, labels, stats, _ = cv2.connectedComponentsWithStats(thatch, 8)
    huts = 0
    for index in range(1, amount):
        area = int(stats[index, cv2.CC_STAT_AREA])
        box_w = int(stats[index, cv2.CC_STAT_WIDTH])
        box_h = int(stats[index, cv2.CC_STAT_HEIGHT])
        if 180 <= area <= 9000 and max(box_w, box_h) < 180:
            blob = cv2.dilate((labels == index).astype(np.uint8), np.ones((9, 9), np.uint8)) * 255
            huts += _stamp(repaired, blob, rng)
    red = repaired[:, :, 0].astype(np.int16)
    green = repaired[:, :, 1].astype(np.int16)
    blue = repaired[:, :, 2].astype(np.int16)
    logs = ((red > 95) & (red > green + 10) & (green > blue) & (blue < 110) & (plateau > 0)).astype(np.uint8)
    amount, labels, stats, _ = cv2.connectedComponentsWithStats(logs, 8)
    log_pixels = 0
    for index in range(1, amount):
        area = int(stats[index, cv2.CC_STAT_AREA])
        box_w = int(stats[index, cv2.CC_STAT_WIDTH])
        box_h = int(stats[index, cv2.CC_STAT_HEIGHT])
        short_side = max(1, min(box_w, box_h))
        if 30 <= area <= 1800 and max(box_w, box_h) / short_side > 2.6:
            log_pixels += _stamp(repaired, (labels == index).astype(np.uint8) * 255, rng)
    # Lower raft only. Contract crossing pixels around y=291 stay untouched.
    red = rgb[:, :, 0].astype(np.int16)
    green = rgb[:, :, 1].astype(np.int16)
    blue = rgb[:, :, 2].astype(np.int16)
    lower = np.zeros((height, width), np.uint8)
    lower[450:545, 1080:1290] = 255
    water = (blue > red + 8) & (blue > green) & (blue > 60)
    grass = (green > red + 6) & (green > blue)
    raft = ((lower > 0) & ~water & ~grass).astype(np.uint8) * 255
    raft = cv2.morphologyEx(raft, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    lower_pixels = int((raft > 0).sum())
    if lower_pixels:
        repaired = cv2.inpaint(repaired, raft, 7, cv2.INPAINT_TELEA)
    changed = int((np.abs(repaired.astype(np.int16) - rgb.astype(np.int16)).sum(axis=2) > 12).sum())
    return repaired, {
        'editedPixels': changed,
        'padPixels': stamped,
        'hutPixels': huts,
        'logPixels': log_pixels,
        'lowerCrossingPixels': lower_pixels,
        'method': 'Each contract pad is restamped from its own surrounding ground, including its border. Plateau thatch huts and loose logs are restamped the same way. The lower raft window is restamped from river water. The contract crossing is outside that window.',
        'protectedCrossing': [1150.0, 291.5],
        'removedLowerCrossingWindow': [1060, 440, 1300, 555],
    }


def viewport_fit(image: np.ndarray, size: tuple[int, int]) -> np.ndarray:
    vw, vh = size
    scale = min(vw / 1376, vh / 768)
    fitted = cv2.resize(image, (max(1, round(1376 * scale)), max(1, round(768 * scale))), interpolation=cv2.INTER_AREA)
    canvas = np.zeros((vh, vw, 3), np.uint8)
    canvas[:] = (24, 32, 35)
    y = (vh - fitted.shape[0]) // 2
    x = (vw - fitted.shape[1]) // 2
    canvas[y:y + fitted.shape[0], x:x + fitted.shape[1]] = fitted
    return canvas


def matte_gate(asset_id: str, rgba: np.ndarray, info: dict) -> tuple[str, str]:
    if info['edgeSpillPixels'] > 80:
        return 'FAIL', f"Localized repair left {info['edgeSpillPixels']} magenta-family edge pixels."
    if info['opaqueSpillPixels'] > 400:
        return 'FAIL', f"Localized repair left {info['opaqueSpillPixels']} magenta-family opaque pixels."
    alpha = rgba[:, :, 3]
    opaque = alpha > 16
    if not np.any(opaque):
        return 'FAIL', 'Subject was removed.'
    ys, xs = np.where(opaque)
    if alpha[int(np.median(ys)), int(np.median(xs))] < 200:
        return 'FAIL', 'Subject centre was removed.'
    if asset_id == 'skill-offense' and alpha[int(np.median(ys)), int(np.median(xs))] < 250:
        return 'FAIL', 'Offense plaque centre is not opaque.'
    return 'UNVERIFIED', 'Automated spill count is under the rejection threshold. Pixel acceptance stays a separate visual gate until the lossless sheets are reviewed.'


def main():
    published = OUT / 'derivatives' / 'v2'
    if published.exists() and any(published.glob('*.png')):
        raise SystemExit('Published v2 derivatives are preserved. Run scripts/recover_v3.py for a new version.')
    for asset_id, (_batch, relative, expected, _foot) in TARGETS.items():
        actual = sha256(ROOT / relative)
        if actual != expected:
            raise SystemExit(f'Stale source {asset_id}')
        v1_path = OUT / 'derivatives' / f'{asset_id}.png'
        if sha256(v1_path) != V1[asset_id]:
            raise SystemExit(f'Rejected v1 derivative changed before correction: {asset_id}')
    terrain_src = ROOT / 'assets/production/production-01-20261003/images/01-kingdom-terrain-stone.png'
    terrain_v1 = OUT / 'terrain' / 'kingdom-terrain-stone-repaired.png'
    if sha256(terrain_src) != TERRAIN_SRC or sha256(terrain_v1) != TERRAIN_V1:
        raise SystemExit('Terrain original or rejected repair changed')
    contract = json.loads(CONTRACT_HASH_SOURCE.read_text(encoding='utf-8-sig'))
    camera_hash = hashlib.sha256(json.dumps(contract['geometry']['kingdom']['worldToSource']).encode()).hexdigest()
    contract_hash = sha256(CONTRACT_HASH_SOURCE)
    sites = {site['id']: site for site in contract['geometry']['kingdom']['sites']}
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    records = []
    rgba_assets = {}
    measurements = {}
    for asset_id, (batch, relative, expected, footprint) in TARGETS.items():
        rejected = load_rgba(OUT / 'derivatives' / f'{asset_id}.png')
        reach = footprint[3] if footprint else None
        rgba, info = repair_cutout(asset_id, rejected, reach)
        if sha256(ROOT / relative) != expected or sha256(OUT / 'derivatives' / f'{asset_id}.png') != V1[asset_id]:
            raise SystemExit(f'Source or rejected derivative changed during repair: {asset_id}')
        derivative = OUT / 'derivatives' / 'v2' / f'{asset_id}.png'
        output_hash = save_rgba(derivative, rgba)
        three_backgrounds(rgba, EVIDENCE / 'inspection' / f'{asset_id}-black-white-green.png')
        edge_crop(rgba, EDGE_BOXES[asset_id], EVIDENCE / 'edges' / f'{asset_id}.png', asset_id)
        status, reason = matte_gate(asset_id, rgba, info)
        record = {
            'id': asset_id,
            'batch': batch,
            'sourceFile': relative,
            'sourceSHA256': expected,
            'derivative': str(derivative.relative_to(ROOT)).replace('\\', '/'),
            'derivativeSHA256': output_hash,
            'rejectedDerivative': f'assets/delivery/stone-starter-20261003/derivatives/{asset_id}.png',
            'rejectedDerivativeSHA256': V1[asset_id],
            'version': 2,
            'processing': info,
            'gates': {
                'matte': {'status': status, 'reason': reason},
                'registration': {'status': 'UNVERIFIED', 'reason': 'Not a grounded building.'},
                'composite': {'status': 'UNVERIFIED', 'reason': 'Scene review is bound to the composite hash separately.'},
            },
        }
        if footprint:
            measurement = measure_landmarks(rgba, (footprint[0], footprint[1]))
            measurement['siteId'] = footprint[2]
            measurement['revision'] = hashlib.sha256(json.dumps({
                'corners': [measurement[name] for name in ('q00', 'q10', 'q01', 'q11')],
                'mode': measurement['placementMode'],
            }, sort_keys=True).encode()).hexdigest()
            rgba_assets[asset_id] = rgba
            measurements[asset_id] = measurement
            record['registration'] = measurement
            annotate(rgba, measurement, EVIDENCE / 'registration' / f'{asset_id}.png')
        else:
            rgba_assets[asset_id] = rgba
        records.append(record)

    order = sorted(measurements, key=lambda asset: project(*sites[measurements[asset]['siteId']]['rect'][:2])[1])
    matrices = {}
    occupancy = {}
    for asset_id in order:
        matrix = place_matrix(measurements[asset_id], sites[measurements[asset_id]['siteId']]['rect'])
        measurements[asset_id]['placementMatrix'] = matrix.tolist()
        bounds, outside = placed_bounds(rgba_assets[asset_id], matrix)
        measurements[asset_id]['placedOpaqueBounds'] = [round(v, 3) for v in bounds]
        measurements[asset_id]['opaquePixelsOutsideSource'] = outside
        matrices[asset_id] = matrix
        mask = np.zeros((768, 1376), np.uint8)
        warped = cv2.warpAffine(rgba_assets[asset_id], matrix.astype(np.float32), (1376, 768), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
        occupancy[asset_id] = warped[:, :, 3] > 16

    for asset_id, measurement in measurements.items():
        overlap = False
        for other, other_mask in occupancy.items():
            if other != asset_id and np.any(occupancy[asset_id] & other_mask):
                overlap = True
        measurement['neighbourOverlap'] = overlap
        status, reason = gate_registration(measurement, measurement['placedOpaqueBounds'], overlap)
        record = next(item for item in records if item['id'] == asset_id)
        record['registration'] = measurement
        record['gates']['registration'] = {'status': status, 'reason': reason}

    terrain_rgb = np.array(Image.open(terrain_src).convert('RGB'))
    repaired, terrain_info = repair_terrain(terrain_rgb, list(sites.values()))
    if sha256(terrain_src) != TERRAIN_SRC or sha256(terrain_v1) != TERRAIN_V1:
        raise SystemExit('Terrain bytes changed during repair')
    terrain_file = OUT / 'terrain' / 'kingdom-terrain-stone-repaired-v2.png'
    terrain_file.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(repaired, 'RGB').save(terrain_file)
    terrain_sha = sha256(terrain_file)
    terrain_record = {
        'id': 'kingdom-terrain-stone',
        'batch': 'production-01-20261003',
        'sourceFile': 'assets/production/production-01-20261003/images/01-kingdom-terrain-stone.png',
        'sourceSHA256': TERRAIN_SRC,
        'derivative': str(terrain_file.relative_to(ROOT)).replace('\\', '/'),
        'derivativeSHA256': terrain_sha,
        'rejectedDerivative': 'assets/delivery/stone-starter-20261003/terrain/kingdom-terrain-stone-repaired.png',
        'rejectedDerivativeSHA256': TERRAIN_V1,
        'version': 2,
        'processing': terrain_info,
        'gates': {
            'matte': {'status': 'UNVERIFIED', 'reason': 'Opaque terrain has no alpha matte.'},
            'registration': {'status': 'UNVERIFIED', 'reason': 'Site geography stays on the contract camera. Cleanup quality is a visual gate.'},
            'composite': {'status': 'UNVERIFIED', 'reason': 'Bound when the scene hash is reviewed.'},
        },
    }

    def compose(include: list[str], label_file: Path):
        canvas = repaired.copy()
        for asset_id in order:
            if asset_id not in include:
                continue
            blit(canvas, rgba_assets[asset_id], matrices[asset_id], contact_shadow(measurements[asset_id]))
        label_file.parent.mkdir(parents=True, exist_ok=True)
        Image.fromarray(canvas, 'RGB').save(label_file)
        return canvas, sha256(label_file)

    hall_only, hall_sha = compose(['townhall-stone'], OUT / 'composites' / 'stone-kingdom-hall-only-day1.png')
    proof, proof_sha = compose(['townhall-stone', 'farm-stone', 'lumber-stone', 'quarry-stone', 'mine-stone'], OUT / 'composites' / 'stone-kingdom-producer-placement-proof.png')
    # The old five-object study remains at its original path and hash.
    reference = np.array(Image.open(ROOT / 'design-preview/generated/landscape-mocks-20261003-efcd7a7e/images/03-kingdom-stone.jpg').convert('RGB'))
    reference = cv2.resize(reference, (1376, 768), interpolation=cv2.INTER_AREA)
    viewports = [tuple(size) for size in contract['viewports']]
    viewport_dir = EVIDENCE / 'viewports'
    viewport_dir.mkdir(parents=True, exist_ok=True)
    for name, image in (('hall-only', hall_only), ('producer-proof', proof), ('reference', reference)):
        for vw, vh in viewports:
            fitted = viewport_fit(image, (vw, vh))
            Image.fromarray(fitted, 'RGB').save(viewport_dir / f'{name}-{vw}x{vh}.png')
    constituent = {record['id']: record['derivativeSHA256'] for record in records}
    constituent['kingdom-terrain-stone'] = terrain_sha
    registration_revision = {asset: measurements[asset]['revision'] for asset in measurements}
    scene = {
        'hallOnly': {
            'file': 'assets/delivery/stone-starter-20261003/composites/stone-kingdom-hall-only-day1.png',
            'sha256': hall_sha,
            'label': 'Day-one sparse start: Hall only, seventeen empty pads, no walls.',
            'constituentSHA256': constituent,
            'registrationRevision': registration_revision,
            'camera': A_FULL.tolist(),
            'cameraHash': camera_hash,
            'contractHash': contract_hash,
        },
        'producerProof': {
            'file': 'assets/delivery/stone-starter-20261003/composites/stone-kingdom-producer-placement-proof.png',
            'sha256': proof_sha,
            'label': 'Producer placement proof. Quarry and Mine in this proof do not change starting levels.',
            'constituentSHA256': constituent,
            'registrationRevision': registration_revision,
            'camera': A_FULL.tolist(),
            'cameraHash': camera_hash,
            'contractHash': contract_hash,
        },
        'rejectedComposite': {
            'file': 'assets/delivery/stone-starter-20261003/stone-kingdom-composite.png',
            'sha256': '2be484d16d7d3af6c28ef779931f859c50d68c0f25260f9a7bc6e92b022e70b2',
        },
    }
    ui_hashes = {}
    ui_dir = OUT / 'ui' / 'v2'
    for size in viewports:
        ui = draw_ui(rgba_assets, rgba_assets['skill-offense'], size)
        file = ui_dir / f'ui-resources-offense-{size[0]}x{size[1]}.png'
        file.parent.mkdir(parents=True, exist_ok=True)
        Image.fromarray(ui, 'RGB').save(file)
        ui_hashes[f'{size[0]}x{size[1]}'] = {'file': str(file.relative_to(ROOT)).replace('\\', '/'), 'sha256': sha256(file), 'railPx': 28, 'symbolPx': 18}
    ledger_path = OUT / 'gate-ledger.json'
    previous = json.loads(ledger_path.read_text(encoding='utf-8-sig'))
    ledger = {
        'version': 2,
        'scope': 'Corrected recovery derivatives. Rejected v1 files remain at their original paths. Runtime and owner gates are absent.',
        'camera': A_FULL.tolist(),
        'cameraHash': camera_hash,
        'contractHash': contract_hash,
        'assets': records + [terrain_record],
        'rejectedV1': previous,
        'composites': scene,
        'composite': scene['hallOnly'],
        'ui': ui_hashes,
    }
    (OUT / 'gate-ledger.json').write_text(json.dumps(ledger, indent=2) + '\n', encoding='utf-8')
    (OUT / 'processing-record.json').write_text(json.dumps({'version': 2, 'assets': ledger['assets'], 'composites': scene}, indent=2) + '\n', encoding='utf-8')
    selection_path = ROOT / 'src/data/reviewed-source-selection.json'
    selection = json.loads(selection_path.read_text(encoding='utf-8-sig'))
    if 'stone' in selection.get('kingdomTerrain', {}):
        selection['kingdomTerrain']['stone']['displayFile'] = terrain_record['derivative']
        selection['kingdomTerrain']['stone']['displaySHA256'] = terrain_sha
        selection['kingdomTerrain']['stone']['displayNote'] = 'v2 repaired derivative. Original and rejected v1 repair preserved. runtimeApproved false.'
        selection['kingdomTerrain']['stone']['runtimeApproved'] = False
        selection['kingdomTerrain']['stone']['ownerAcceptance'] = 'UNVERIFIED'
    for record in records:
        selection.setdefault('delivery', {})[record['id']] = {
            'file': record['derivative'],
            'sha256': record['derivativeSHA256'],
            'batch': record['batch'],
            'sourceSHA256': record['sourceSHA256'],
            'runtimeApproved': False,
            'ownerAcceptance': 'UNVERIFIED',
        }
    selection_path.write_text(json.dumps(selection, indent=2) + '\n', encoding='utf-8')
    summary = {
        'matte': {record['id']: record['gates']['matte'] for record in records},
        'registration': {record['id']: record['gates']['registration'] for record in records if 'registration' in record},
        'measurements': {asset: {key: measurements[asset][key] for key in ('q00', 'q10', 'q01', 'q11', 'fourthCornerErrorPx', 'scaleRatio', 'shear', 'placementMode', 'placedOpaqueBounds', 'opaquePixelsOutsideSource', 'neighbourOverlap', 'groundPivot')} for asset in measurements},
        'hashes': {record['id']: record['derivativeSHA256'] for record in records + [terrain_record]},
        'hallOnly': hall_sha,
        'producerProof': proof_sha,
        'terrainEdits': terrain_info['editedPixels'],
        'spill': {record['id']: record['processing'] for record in records},
    }
    (EVIDENCE / 'correction-summary.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
