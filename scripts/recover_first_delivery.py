"""Recover the first Stone delivery set from collected originals.

Originals, provider responses, locks and collection reports are not modified.
Derivatives are written under assets/delivery/stone-starter-20261003/.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/delivery/stone-starter-20261003'
A_LIN = np.array([[60.0, 25.0], [-10.0, 35.0]], dtype=np.float64)
A_FULL = np.array([60.0, -10.0, 25.0, 35.0, 170.0, 165.0])
NEUTRAL_GREEN = (110, 132, 104)
TARGETS = {
    'skill-offense': ('production-03-20261003', 'assets/production/production-03-20261003/images/04-skill-offense.png', '594fc35135244184a2c685ff6ac243dfe4b5ff9c846e8e0a92ea60b816cf11cf', None),
    'resource-food': ('production-01-20261003', 'assets/production/production-01-20261003/images/26-resource-food.png', 'd3287f62b9850e4dbab0f3a132c1abacabfe89932eb9ed9bc76d1496bdb0716f', None),
    'resource-wood': ('production-01-20261003', 'assets/production/production-01-20261003/images/27-resource-wood.png', 'a91c3a395af420fdbc53ecb9b330cc11633bb61b5b46316163ea2331b3bb82d2', None),
    'resource-stone': ('production-01-20261003', 'assets/production/production-01-20261003/images/28-resource-stone.png', '2c819abba15fa22311e039e2ad661a04399791a53ac51aa5f12c9e4dbfef6d5e', None),
    'resource-gold': ('production-01-20261003', 'assets/production/production-01-20261003/images/29-resource-gold.png', 'e8cb7967df838fd84168e87dff6ac98c66c1bdfaab0dfbac84f81d978468f168', None),
    'townhall-stone': ('production-03-20261003', 'assets/production/production-03-20261003/images/03-townhall-stone.png', '2809db2bc0045cfeae0ae73b675b0236b03f0f0f369009c90430af62d22c1b5e', (3.0, 1.5, 'townhall')),
    'farm-stone': ('production-03-20261003', 'assets/production/production-03-20261003/images/27-farm-stone.png', 'a8c004398448e549d9b4e737801e16c5186965e5f35f22d7dd46c61efa3ae0e3', (1.4, 1.2, 'P01')),
    'lumber-stone': ('production-03-20261003', 'assets/production/production-03-20261003/images/28-lumber-stone.png', '63fc579f757d8930a10252db38622ccafab35e93679554e4afcbebd535a0fd38', (1.4, 1.2, 'P04')),
    'quarry-stone': ('production-03-20261003', 'assets/production/production-03-20261003/images/29-quarry-stone.png', 'da5b9d5ccb9c3422d3058dc2a7424da4e74a4732ed72207da7217ec283d6487b', (1.4, 1.2, 'P10')),
    'mine-stone': ('production-03-20261003', 'assets/production/production-03-20261003/images/30-mine-stone.png', 'ff1daba56ba7b3e1f40cdb85bcd9ace519260670017572e1123e74f24aa53731', (1.4, 1.2, 'P14')),
}
TERRAIN = ('production-01-20261003', 'assets/production/production-01-20261003/images/01-kingdom-terrain-stone.png', '6cb13e0d4deaf2924a1b089d57356c973b4998621e59a66a8d3edca1b03daad1')


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_rgb(path: Path) -> np.ndarray:
    return np.array(Image.open(path).convert('RGB'))


def save_rgba(path: Path, rgba: np.ndarray) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(rgba, 'RGBA').save(path)
    return sha256(path)


def project(x, y):
    a, b, c, d, e, f = A_FULL
    return np.array([a * x + c * y + e, b * x + d * y + f], dtype=np.float64)


def matte(rgb: np.ndarray) -> tuple[np.ndarray, dict]:
    """Border-connected background model. Not a global chroma deletion."""
    image = rgb.astype(np.float32)
    height, width = image.shape[:2]
    border = np.concatenate([
        image[:4].reshape(-1, 3), image[-4:].reshape(-1, 3),
        image[:, :4].reshape(-1, 3), image[:, -4:].reshape(-1, 3),
    ])
    median = np.median(border, axis=0)
    mad = np.median(np.abs(border - median), axis=0) + 1.0
    delta = (image - median) / (mad * 6.0)
    normalized = np.linalg.norm(delta, axis=2)
    raw = np.linalg.norm(image - median, axis=2)
    green_cap = float(median[1] + max(36.0, 5.0 * mad[1]))
    candidate = (normalized < 1.45) & (raw < 96) & (image[:, :, 1] <= green_cap)
    strict = (normalized < 0.9) & (raw < 52) & (image[:, :, 1] <= green_cap)
    count, labels = cv2.connectedComponents(strict.astype(np.uint8), connectivity=4)
    border_labels = np.unique(np.concatenate([labels[0], labels[-1], labels[:, 0], labels[:, -1]]))
    border_labels = border_labels[border_labels != 0]
    background = np.isin(labels, border_labels)
    allowed = candidate.astype(np.uint8)
    marker = background.astype(np.uint8)
    kernel = np.ones((3, 3), np.uint8)
    for _ in range(64):
        grown = cv2.bitwise_and(cv2.dilate(marker, kernel), allowed)
        if np.array_equal(grown, marker):
            break
        marker = grown
    background = marker.astype(bool)
    red, green, blue = image[:, :, 0], image[:, :, 1], image[:, :, 2]
    shadow = (green < 78) & (red > 110) & (blue > 110) & (green + 10 < np.minimum(red, blue) * 0.48)
    allowed_shadow = (candidate | shadow).astype(np.uint8)
    marker = background.astype(np.uint8)
    for _ in range(96):
        grown = cv2.bitwise_and(cv2.dilate(marker, kernel), allowed_shadow)
        if np.array_equal(grown, marker):
            break
        marker = grown
    background = marker.astype(bool)
    luminance = image.mean(axis=2)
    median_luminance = float(np.mean(median)) + 1e-3
    direction = np.linalg.norm(image / (luminance[..., None] + 1e-3) - (median / median_luminance), axis=2)
    hue_shadow = (direction < 0.26) & (luminance > 18) & (luminance < median_luminance * 1.2)
    allowed_hue = (candidate | shadow | hue_shadow).astype(np.uint8)
    marker = background.astype(np.uint8)
    for _ in range(128):
        grown = cv2.bitwise_and(cv2.dilate(marker, kernel), allowed_hue)
        if np.array_equal(grown, marker):
            break
        marker = grown
    background = marker.astype(bool)
    enclosed = hue_shadow & ~background
    amount, hole_labels, stats, _ = cv2.connectedComponentsWithStats(enclosed.astype(np.uint8), 8)
    for index in range(1, amount):
        area = int(stats[index, cv2.CC_STAT_AREA])
        if 8 <= area <= 0.08 * height * width:
            background[hole_labels == index] = True
    holes = strict & ~background
    amount, hole_labels, stats, _ = cv2.connectedComponentsWithStats(holes.astype(np.uint8), 8)
    for index in range(1, amount):
        area = int(stats[index, cv2.CC_STAT_AREA])
        if area < 2 or area > 0.12 * height * width:
            holes[hole_labels == index] = False
    background = background | holes
    foreground = ~background
    # Drop isolated specks that are not part of the subject.
    amount, labels, stats, _ = cv2.connectedComponentsWithStats(foreground.astype(np.uint8), 8)
    if amount > 1:
        largest = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
        keep = labels == largest
        for index in range(1, amount):
            if int(stats[index, cv2.CC_STAT_AREA]) > 80:
                keep[labels == index] = True
        foreground = keep
        background = ~foreground
    distance = cv2.distanceTransform(foreground.astype(np.uint8), cv2.DIST_L2, 3)
    fringe = foreground & (distance <= 2.2)
    alpha = np.ones((height, width), np.float32)
    alpha[background] = 0
    alpha_fringe = np.clip((raw - 16.0) / 58.0, 0.12, 1.0)
    alpha[fringe] = alpha_fringe[fringe]
    color = image.copy()
    safe = np.clip(alpha, 0.18, 1.0)
    unmixed = np.clip((image - (1.0 - alpha)[..., None] * median) / safe[..., None], 0, 255)
    color[fringe] = unmixed[fringe]
    # Rim-only reflected-magenta suppression. Interior object color is left alone.
    rim = foreground & (distance <= 3.5) & (color[:, :, 0] > 165) & (color[:, :, 1] > 75) & (color[:, :, 2] > color[:, :, 1] + 16)
    color[:, :, 2] = np.where(rim, color[:, :, 1] + (color[:, :, 2] - color[:, :, 1]) * 0.35, color[:, :, 2])
    # Pixels still dominated by the backdrop and touching transparency are fringe, not object color.
    near = foreground & (distance <= 8)
    backdrop_fringe = (color[:, :, 2] > 145) & (color[:, :, 2] > color[:, :, 1] + 28) & (color[:, :, 0] > 100)
    alpha[near & backdrop_fringe] = 0
    foreground = alpha > 0.05
    rgba = np.dstack([color.astype(np.uint8), (alpha * 255).astype(np.uint8)])
    edge = np.zeros((height, width), bool)
    edge[:3] = edge[-3:] = edge[:, :3] = edge[:, -3:] = True
    rgba, soil_pixels = trim_border_soil(rgba)
    exterior = rgba[:, :, 3] <= 16
    gap_count, gap_labels = cv2.connectedComponents(exterior.astype(np.uint8), connectivity=4)
    gap_border = np.unique(np.concatenate([gap_labels[0], gap_labels[-1], gap_labels[:, 0], gap_labels[:, -1]]))
    interior_gaps = exterior & ~np.isin(gap_labels, gap_border)
    info = {
        'method': 'border-connected normalized background growth; connected magenta-family shadow; enclosed near-background holes; border soil trim; 2px fringe unmix; rim-only magenta suppression',
        'borderSoilPixelsRemoved': soil_pixels,
        'backgroundMedian': [round(float(v), 2) for v in median],
        'backgroundMAD': [round(float(v), 2) for v in mad],
        'greenCap': round(green_cap, 2),
        'opaqueFraction': round(float((rgba[:, :, 3] > 16).mean()), 4),
        'edgeMeanAlpha': round(float(rgba[:, :, 3][edge].mean()), 3),
        'enclosedHolePixels': int(interior_gaps.sum()),
        'globalChromaThreshold': False,
    }
    return rgba, info


def trim_border_soil(rgba: np.ndarray) -> tuple[np.ndarray, int]:
    """Remove smooth dirt that stays attached to the canvas edge. Textured structure stops the flood."""
    color = rgba[:, :, :3]
    foreground = rgba[:, :, 3] > 16
    edge = np.zeros(foreground.shape, bool)
    edge[0] = edge[-1] = edge[:, 0] = edge[:, -1] = True
    if not np.any(foreground & edge):
        return rgba, 0
    gray = cv2.cvtColor(color, cv2.COLOR_RGB2GRAY)
    texture = np.abs(cv2.Laplacian(gray, cv2.CV_16S)) > 24
    red, green, blue = color[:, :, 0], color[:, :, 1], color[:, :, 2]
    soil = foreground & ~texture & (red > 85) & (green > 50) & (blue < 155) & (red + 6 > green) & (green + 6 > blue)
    marker = (soil & edge).astype(np.uint8)
    allowed = soil.astype(np.uint8)
    kernel = np.ones((3, 3), np.uint8)
    for _ in range(500):
        grown = cv2.bitwise_and(cv2.dilate(marker, kernel), allowed)
        if np.array_equal(grown, marker):
            break
        marker = grown
    removed = marker.astype(bool)
    rgba = rgba.copy()
    rgba[:, :, 3][removed] = 0
    return rgba, int(removed.sum())


def measure_base(rgba: np.ndarray, footprint: tuple[float, float]) -> dict:
    fw, fh = footprint
    alpha = rgba[:, :, 3]
    foreground = alpha > 32
    amount, labels, stats, _ = cv2.connectedComponentsWithStats(foreground.astype(np.uint8), 8)
    if amount <= 1:
        raise RuntimeError('No foreground to measure')
    largest = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    mask = labels == largest
    eroded = cv2.erode(mask.astype(np.uint8), np.ones((3, 3), np.uint8))
    boundary = mask & (eroded == 0)
    ys, xs = np.where(mask)
    y0, y1 = int(ys.min()), int(ys.max())
    lower = ys >= y0 + 0.80 * (y1 - y0)
    points = np.column_stack((xs[lower], ys[lower])).astype(np.float64)
    if len(points) > 6000:
        points = points[:: max(1, len(points) // 6000)]
    inverse = np.linalg.inv(A_LIN)
    ab = (inverse @ points.T).T
    a0, a1 = float(ab[:, 0].min()), float(ab[:, 0].max())
    b0, b1 = float(ab[:, 1].min()), float(ab[:, 1].max())
    q00 = A_LIN @ np.array([a0, b0])
    q10 = A_LIN @ np.array([a1, b0])
    q01 = A_LIN @ np.array([a0, b1])
    q11 = A_LIN @ np.array([a1, b1])
    observed = []
    fitted = [q00, q10, q01, q11]
    for corner in fitted:
        observed.append(points[np.argmin(np.linalg.norm(points - corner, axis=1))])
    o00, o10, o01, o11 = observed
    predicted = o00 + (o10 - o00) + (o01 - o00)
    fourth_error = float(np.linalg.norm(predicted - o11))
    measured_fw = a1 - a0
    measured_fh = b1 - b0
    b_axis = np.column_stack(((q10 - q00) / fw, (q01 - q00) / fh))
    placement = A_LIN @ np.linalg.inv(b_axis)
    scale_x = measured_fw / fw
    scale_y = measured_fh / fh
    ratio = max(scale_x, scale_y) / min(scale_x, scale_y)
    pivot = (q00 + q10 + q01 + q11) / 4
    corner_gap = fourth_error
    if ratio <= 1.2 and corner_gap <= 18:
        used = placement
        mode = 'D=A*inverse(B)'
    else:
        # Match measured ground width to the pad. A non-fitting quad is not sheared onto the roof.
        used = np.eye(2) * float(fw / measured_fw)
        mode = 'uniform-width-fit'
    return {
        'q00': q00.tolist(), 'q10': q10.tolist(), 'q01': q01.tolist(), 'q11': q11.tolist(),
        'observedCorners': [p.tolist() for p in observed],
        'fourthCornerErrorPx': round(fourth_error, 3),
        'footprintWorld': [fw, fh],
        'measuredWorldSpan': [round(measured_fw, 4), round(measured_fh, 4)],
        'sourceAxesB': b_axis.tolist(),
        'placementD': placement.tolist(),
        'placementUsed': used.tolist(),
        'placementMode': mode,
        'scaleRatio': round(float(ratio), 4),
        'groundPivot': [round(float(pivot[0]), 3), round(float(pivot[1]), 3)],
        'guidePivotCopied': False,
        'contactPoints': int(len(points)),
    }


def gate_registration(measurement: dict) -> str:
    if measurement['placementMode'] != 'D=A*inverse(B)':
        return 'FAIL'
    if measurement['fourthCornerErrorPx'] > 36 or measurement['scaleRatio'] > 1.35:
        return 'FAIL'
    if measurement['fourthCornerErrorPx'] > 18 or measurement['scaleRatio'] > 1.2:
        return 'UNVERIFIED'
    return 'PASS'


def automated_matte_gate(asset_id: str, rgba: np.ndarray, info: dict) -> tuple[str, str]:
    alpha = rgba[:, :, 3]
    opaque = alpha > 16
    if info['edgeMeanAlpha'] > 8:
        return 'FAIL', 'Background remains on the image edge.'
    red, green, blue = rgba[:, :, 0], rgba[:, :, 1], rgba[:, :, 2]
    leftover = (opaque & (green < 80) & (red > 140) & (blue > 140)).astype(np.uint8)
    amount, _labels, stats, _ = cv2.connectedComponentsWithStats(leftover, 8)
    large = max((int(stats[i, cv2.CC_STAT_AREA]) for i in range(1, amount)), default=0)
    if large > 500:
        return 'FAIL', 'A magenta contact shadow is still opaque.'
    if info['opaqueFraction'] < 0.05 or info['opaqueFraction'] > 0.82:
        return 'FAIL', f"Opaque fraction {info['opaqueFraction']} is outside the expected subject range."
    ys, xs = np.where(opaque)
    cy, cx = int(np.median(ys)), int(np.median(xs))
    if alpha[cy, cx] < 200:
        return 'FAIL', 'Subject centre was removed.'
    if asset_id == 'resource-food' and info['enclosedHolePixels'] < 20:
        return 'FAIL', 'Basket and rope gaps were not retained as interior transparency.'
    if asset_id == 'skill-offense' and alpha[cy, cx] < 250:
        return 'FAIL', 'Offense plaque centre is not opaque.'
    if asset_id == 'resource-gold':
        gold = rgba[opaque][:, 1].mean()
        if gold < 110:
            return 'FAIL', 'Gold green channel collapsed; object color was damaged.'
    return 'PASS', 'Edge is clear, subject centre remains, and the hole/color checks for this asset passed.'


def inspection(rgba: np.ndarray, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    height, width = rgba.shape[:2]
    sheet = np.zeros((height, width * 3, 3), np.uint8)
    for index, color in enumerate(((0, 0, 0), (255, 255, 255), NEUTRAL_GREEN)):
        tile = np.empty((height, width, 3), np.uint8)
        tile[:] = color
        alpha = rgba[:, :, 3:4].astype(np.float32) / 255.0
        tile = (rgba[:, :, :3] * alpha + tile * (1 - alpha)).astype(np.uint8)
        sheet[:, index * width:(index + 1) * width] = tile
    Image.fromarray(sheet, 'RGB').save(path)


def polygon(rect):
    x, y, w, h = rect
    return np.array([project(x, y), project(x + w, y), project(x + w, y + h), project(x, y + h)], np.int32)


def repair_terrain(rgb: np.ndarray, sites) -> tuple[np.ndarray, dict]:
    height, width = rgb.shape[:2]
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    local = cv2.medianBlur(gray, 31)
    bright = ((gray.astype(np.int16) - local.astype(np.int16)) > 20).astype(np.uint8)
    bulky = cv2.morphologyEx(bright, cv2.MORPH_OPEN, np.ones((7, 7), np.uint8))
    lines = cv2.subtract(bright, bulky) * 255
    band = np.zeros((height, width), np.uint8)
    interior = np.zeros((height, width), np.uint8)
    polys = []
    for site in sites:
        poly = polygon(site['rect'])
        polys.append(poly)
        cv2.fillPoly(interior, [poly], 1)
        cv2.polylines(band, [poly], True, 1, 12)
    mark = np.where((lines > 0) & (band > 0), 255, 0).astype(np.uint8)
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB).astype(np.int16)
    gray_full = gray
    structures = np.zeros((height, width), np.uint8)
    for poly in polys:
        mask = np.zeros((height, width), np.uint8)
        cv2.fillPoly(mask, [poly], 1)
        inner = cv2.erode(mask, np.ones((5, 5), np.uint8))
        if inner.sum() < 40:
            continue
        calm = inner.astype(bool) & (np.abs(cv2.Laplacian(gray_full, cv2.CV_16S)) < 14)
        samples = lab[calm] if int(calm.sum()) > 40 else lab[inner > 0]
        median = np.median(samples, axis=0)
        distance = np.linalg.norm(lab - median, axis=2)
        structures[(inner > 0) & (distance > 16)] = 255
        edge_band = cv2.dilate(mask, np.ones((9, 9), np.uint8)) & (1 - cv2.erode(mask, np.ones((9, 9), np.uint8)))
        structures[edge_band > 0] = 255
    structures = cv2.morphologyEx(structures, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    full = cv2.bitwise_or(mark, structures)
    repaired = cv2.inpaint(rgb, full, 4, cv2.INPAINT_TELEA)
    changed = int((np.abs(repaired.astype(np.int16) - rgb.astype(np.int16)).sum(axis=2) > 12).sum())
    return repaired, {'editedPixels': changed, 'maskPixels': int((full > 0).sum()), 'method': 'Site-edge bright lines and interior pixels far from the surrounding ground were inpainted. River, bridge and outskirts outside the 18 footprints were not targeted.'}


def blit(canvas: np.ndarray, rgba: np.ndarray, matrix: np.ndarray):
    height, width = canvas.shape[:2]
    warped = cv2.warpAffine(rgba, matrix.astype(np.float32), (width, height), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    alpha = warped[:, :, 3:4].astype(np.float32) / 255.0
    base = canvas.astype(np.float32)
    canvas[:] = np.clip(warped[:, :, :3].astype(np.float32) * alpha + base * (1 - alpha), 0, 255).astype(np.uint8)


def keep_structure_island(rgba: np.ndarray, reach: int = 32) -> tuple[np.ndarray, int]:
    """Drop loose soil farther than `reach` pixels from textured structure."""
    foreground = rgba[:, :, 3] > 16
    gray = cv2.cvtColor(rgba[:, :, :3], cv2.COLOR_RGB2GRAY)
    texture = np.abs(cv2.Laplacian(gray, cv2.CV_16S)) > 11
    core = foreground & texture
    if int(core.sum()) < 80:
        return rgba, 0
    marker = core.astype(np.uint8)
    allowed = foreground.astype(np.uint8)
    kernel = np.ones((3, 3), np.uint8)
    for _ in range(reach):
        marker = cv2.bitwise_and(cv2.dilate(marker, kernel), allowed)
    removed = foreground & (marker == 0)
    rgba = rgba.copy()
    rgba[:, :, 3][removed] = 0
    return rgba, int(removed.sum())


def place_matrix(measurement, site_rect):
    x, y, w, h = site_rect
    pivot = np.array(measurement['groundPivot'])
    destination = project(x + w / 2, y + h / 2)
    d = np.array(measurement['placementUsed'])
    translation = destination - d @ pivot
    return np.array([[d[0, 0], d[0, 1], translation[0]], [d[1, 0], d[1, 1], translation[1]]], dtype=np.float64)


def draw_ui(resources: dict[str, np.ndarray], offense: np.ndarray, size: tuple[int, int]) -> np.ndarray:
    width, height = size
    image = Image.new('RGB', size, (24, 32, 34))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, width, 36), fill=(18, 26, 28))
    cursor = 16
    labels = [('Food', 250), ('Wood', 250), ('Stone', 160), ('Gold', 150)]
    keys = ['resource-food', 'resource-wood', 'resource-stone', 'resource-gold']
    for (label, amount), key in zip(labels, keys):
        icon = resources[key]
        glyph = fit_icon(icon, 18)
        image.paste(glyph, (cursor, 9), glyph)
        draw.text((cursor + 22, 10), f'{label} {amount}', fill=(236, 226, 204))
        cursor += 22 + 8 + len(f'{label} {amount}') * 7 + 18
    emblem = fit_icon(offense, 64)
    panel_x = width - 280
    draw.rounded_rectangle((panel_x, 64, width - 24, 168), radius=6, fill=(28, 38, 40), outline=(116, 98, 64))
    image.paste(emblem, (panel_x + 16, 84), emblem)
    draw.text((panel_x + 96, 96), 'Offense', fill=(236, 226, 204))
    draw.text((panel_x + 96, 118), 'Recovered plaque', fill=(196, 176, 132))
    draw.text((16, height - 28), 'Reference start amounts. Owner acceptance is pending.', fill=(168, 160, 140))
    return np.array(image)


def fit_icon(rgba: np.ndarray, target: int) -> Image.Image:
    alpha = rgba[:, :, 3]
    ys, xs = np.where(alpha > 16)
    crop = rgba[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    scale = target / max(crop.shape[0], crop.shape[1])
    resized = cv2.resize(crop, (max(1, int(crop.shape[1] * scale)), max(1, int(crop.shape[0] * scale))), interpolation=cv2.INTER_AREA)
    return Image.fromarray(resized, 'RGBA')


def side_by_side(before: np.ndarray, after_rgba: np.ndarray, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    height = 360
    scale = height / before.shape[0]
    bw, bh = int(before.shape[1] * scale), height
    left = cv2.resize(before, (bw, bh), interpolation=cv2.INTER_AREA)
    preview = np.zeros_like(after_rgba[:, :, :3])
    preview[:] = NEUTRAL_GREEN
    alpha = after_rgba[:, :, 3:4].astype(np.float32) / 255.0
    composited = (after_rgba[:, :, :3] * alpha + preview * (1 - alpha)).astype(np.uint8)
    right = cv2.resize(composited, (bw, bh), interpolation=cv2.INTER_AREA)
    gap = np.full((bh, 8, 3), 40, np.uint8)
    Image.fromarray(np.concatenate([left, gap, right], axis=1), 'RGB').save(path)


def main():
    originals = {}
    for asset_id, (batch, relative, expected, _foot) in TARGETS.items():
        path = ROOT / relative
        actual = sha256(path)
        if actual != expected:
            raise SystemExit(f'Stale source hash for {asset_id}: {actual}')
        originals[asset_id] = sha256(path)
    terrain_batch, terrain_rel, terrain_sha = TERRAIN
    terrain_path = ROOT / terrain_rel
    if sha256(terrain_path) != terrain_sha:
        raise SystemExit('Stale Stone terrain hash')
    contract = json.loads((ROOT / 'docs/plan/IMPLEMENTATION-CONTRACT.json').read_text(encoding='utf-8-sig'))
    sites = {site['id']: site for site in contract['geometry']['kingdom']['sites']}
    registry = json.loads((ROOT / 'docs/plan/image-production/RECOVERY-SOURCE-REGISTRY-20261003.json').read_text(encoding='utf-8-sig'))
    preferred = {item['id']: item for item in registry['sources']}
    if preferred['townhall-stone']['sourceSHA256'] != TARGETS['townhall-stone'][2]:
        raise SystemExit('Registry no longer selects the batch 03 Hall')
    if preferred['skill-offense']['sourceSHA256'] != TARGETS['skill-offense'][2]:
        raise SystemExit('Registry no longer selects the batch 03 Offense plaque')
    if 'production-01-20261003:townhall-stone' in preferred['townhall-stone']['preferredReviewCandidateKey']:
        raise SystemExit('Refusing batch 01 Hall as the selected candidate')

    OUT.mkdir(parents=True, exist_ok=True)
    records = []
    rgba_assets = {}
    measurements = {}
    for asset_id, (batch, relative, expected, footprint) in TARGETS.items():
        rgb = read_rgb(ROOT / relative)
        before_hash = sha256(ROOT / relative)
        rgba, info = matte(rgb)
        if sha256(ROOT / relative) != before_hash:
            raise SystemExit(f'Original changed during matte: {asset_id}')
        if footprint:
            rgba, removed_soil = keep_structure_island(rgba)
            info['structureIslandPixelsRemoved'] = removed_soil
            edge = np.zeros(rgba.shape[:2], bool)
            edge[:3] = edge[-3:] = edge[:, :3] = edge[:, -3:] = True
            info['opaqueFraction'] = round(float((rgba[:, :, 3] > 16).mean()), 4)
            info['edgeMeanAlpha'] = round(float(rgba[:, :, 3][edge].mean()), 3)
        derivative = OUT / 'derivatives' / f'{asset_id}.png'
        output_hash = save_rgba(derivative, rgba)
        inspection(rgba, OUT / 'inspection' / f'{asset_id}-black-white-green.jpg')
        side_by_side(rgb, rgba, OUT / 'before-after' / f'{asset_id}.jpg')
        status, reason = automated_matte_gate(asset_id, rgba, info)
        record = {
            'id': asset_id,
            'batch': batch,
            'sourceFile': relative.replace('\\', '/'),
            'sourceSHA256': expected,
            'derivative': str(derivative.relative_to(ROOT)).replace('\\', '/'),
            'derivativeSHA256': output_hash,
            'processing': info,
            'gates': {
                'matte': {'status': status, 'reason': reason},
                'registration': {'status': 'UNVERIFIED', 'reason': 'Not a grounded building.'},
                'composite': {'status': 'UNVERIFIED', 'reason': 'Waiting for the assembled preview inspection.'},
            },
        }
        if footprint:
            fw, fh, site_id = footprint
            measurement = measure_base(rgba, (fw, fh))
            measurement['siteId'] = site_id
            measurement['placementMatrix'] = place_matrix(measurement, sites[site_id]['rect']).tolist()
            record['registration'] = measurement
            reg_status = gate_registration(measurement)
            record['gates']['registration'] = {
                'status': reg_status,
                'reason': f"Fourth-corner error {measurement['fourthCornerErrorPx']} px; axis scale ratio {measurement['scaleRatio']}.",
            }
            measurements[asset_id] = measurement
        records.append(record)
        rgba_assets[asset_id] = rgba

    terrain_rgb = read_rgb(terrain_path)
    repaired, terrain_info = repair_terrain(terrain_rgb, list(sites.values()))
    terrain_file = OUT / 'terrain' / 'kingdom-terrain-stone-repaired.png'
    terrain_file.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(repaired, 'RGB').save(terrain_file)
    terrain_derivative_sha = sha256(terrain_file)
    if sha256(terrain_path) != terrain_sha:
        raise SystemExit('Terrain original changed')

    composite = repaired.copy()
    order = sorted(measurements, key=lambda asset: project(*sites[measurements[asset]['siteId']]['rect'][:2])[1])
    for asset_id in order:
        blit(composite, rgba_assets[asset_id], np.array(measurements[asset_id]['placementMatrix']))
    composite_file = OUT / 'stone-kingdom-composite.png'
    Image.fromarray(composite, 'RGB').save(composite_file)
    # Debug quads on a copy, not on the review composite.
    debug = composite.copy()
    for asset_id, measurement in measurements.items():
        matrix = np.array(measurement['placementMatrix'])
        corners = []
        for name in ('q00', 'q10', 'q11', 'q01'):
            point = np.array(measurement[name] + [1])
            corners.append(tuple(np.round(matrix @ point).astype(int)))
        cv2.polylines(debug, [np.array(corners, np.int32)], True, (40, 220, 220), 1)
    Image.fromarray(debug, 'RGB').save(OUT / 'stone-kingdom-placement-debug.png')

    ui_dir = OUT / 'ui'
    ui_dir.mkdir(parents=True, exist_ok=True)
    ui_hashes = {}
    for size in ((825, 375), (933, 424), (1180, 820), (1280, 720)):
        ui = draw_ui(rgba_assets, rgba_assets['skill-offense'], size)
        file = ui_dir / f'ui-resources-offense-{size[0]}x{size[1]}.png'
        Image.fromarray(ui, 'RGB').save(file)
        ui_hashes[f'{size[0]}x{size[1]}'] = {'file': str(file.relative_to(ROOT)).replace('\\', '/'), 'sha256': sha256(file)}

    (OUT / 'comparison').mkdir(parents=True, exist_ok=True)
    reference = ROOT / 'design-preview/generated/landscape-mocks-20261003-efcd7a7e/images/03-kingdom-stone.jpg'
    if reference.exists():
        ref = np.array(Image.open(reference).convert('RGB'))
        ref = cv2.resize(ref, (688, 384), interpolation=cv2.INTER_AREA)
        comp = cv2.resize(composite, (688, 384), interpolation=cv2.INTER_AREA)
        gap = np.full((384, 8, 3), 20, np.uint8)
        Image.fromarray(np.concatenate([ref, gap, comp], axis=1), 'RGB').save(OUT / 'comparison' / 'stone-reference-and-composite.jpg')

    for record in records:
        record['gates']['composite'] = {
            'status': 'UNVERIFIED',
            'reason': 'Composite and UI rasters exist. Visual fidelity against the Stone appearance reference is not an automated pass.',
        }
    terrain_record = {
        'id': 'kingdom-terrain-stone',
        'batch': terrain_batch,
        'sourceFile': terrain_rel,
        'sourceSHA256': terrain_sha,
        'derivative': str(terrain_file.relative_to(ROOT)).replace('\\', '/'),
        'derivativeSHA256': terrain_derivative_sha,
        'processing': terrain_info,
        'gates': {
            'matte': {'status': 'UNVERIFIED', 'reason': 'Terrain is opaque. This gate records footprint cleanup, not alpha.'},
            'registration': {'status': 'UNVERIFIED', 'reason': 'Cleanup keeps source bounds and contract footprints. Pixel registration of every pad remains a visual gate.'},
            'composite': {'status': 'UNVERIFIED', 'reason': 'Used as the base of the Stone composite. Owner acceptance is separate.'},
        },
    }
    ledger = {
        'version': 1,
        'scope': 'First recovered delivery set. Runtime and owner gates are intentionally absent here.',
        'camera': A_FULL.tolist(),
        'assets': records + [terrain_record],
        'composite': {'file': str(composite_file.relative_to(ROOT)).replace('\\', '/'), 'sha256': sha256(composite_file)},
        'ui': ui_hashes,
        'originalsUnchanged': originals | {'kingdom-terrain-stone': sha256(terrain_path)},
    }
    (OUT / 'processing-record.json').write_text(json.dumps({'version': 1, 'assets': ledger['assets']}, indent=2) + '\n', encoding='utf-8')
    (OUT / 'gate-ledger.json').write_text(json.dumps(ledger, indent=2) + '\n', encoding='utf-8')
    selection = {'version': 1, 'note': 'Explicit reviewed-candidate paths. runtimeApproved is false. Owner acceptance is UNVERIFIED.', 'kingdomTerrain': {}, 'delivery': {}}
    for item in registry['sources']:
        if item['id'].startswith('kingdom-terrain-'):
            age = item['id'].removeprefix('kingdom-terrain-')
            entry = {'batch': item['preferredReviewCandidateKey'].split(':')[0], 'id': item['id'], 'sourceFile': item['sourceFile'], 'sourceSHA256': item['sourceSHA256'], 'runtimeApproved': False, 'ownerAcceptance': 'UNVERIFIED'}
            if age == 'stone':
                entry['displayFile'] = terrain_record['derivative']
                entry['displaySHA256'] = terrain_derivative_sha
                entry['displayNote'] = 'Repaired derivative of the batch 01 candidate. Original preserved.'
            selection['kingdomTerrain'][age] = entry
    for record in records:
        selection['delivery'][record['id']] = {'file': record['derivative'], 'sha256': record['derivativeSHA256'], 'batch': record['batch'], 'sourceSHA256': record['sourceSHA256'], 'runtimeApproved': False, 'ownerAcceptance': 'UNVERIFIED'}
    (ROOT / 'src/data/reviewed-source-selection.json').write_text(json.dumps(selection, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({
        'derivatives': len(records),
        'matte': {r['id']: r['gates']['matte']['status'] for r in records},
        'registration': {r['id']: r['gates']['registration']['status'] for r in records if 'registration' in r},
        'composite': ledger['composite']['sha256'][:12],
        'terrainEdits': terrain_info['editedPixels'],
    }, indent=2))


if __name__ == '__main__':
    main()
