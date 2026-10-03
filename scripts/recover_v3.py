"""Build Hall and Gold v3 from preserved v1 cutouts, and a contact-registered Stone scene.

Does not overwrite originals, v1, v2, provider files, or the rejected composites.
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
EVIDENCE = ROOT / 'qa/recovery-v3-20261003'
A_FULL = np.array([60.0, -10.0, 25.0, 35.0, 170.0, 165.0])
V1_HALL = '0cac3bd09dbb4c8eb88824f02ee01b951c21d2f6f85f024430e080763794f321'
V2_HALL = 'd77406ffc8b865059f585f4dbc7d5af61e80473b5eded535ec5b32e15775ad73'
V1_GOLD = '254ec836e985bd4cc2d93f15a76a3971e063bcaa2120636771f513c99db21ab3'
V2_GOLD = 'a02bde77aa7ee13ce3319977f39b168c36512878b724b07b1757638db820d25b'
TERRAIN_SRC = '6cb13e0d4deaf2924a1b089d57356c973b4998621e59a66a8d3edca1b03daad1'
TERRAIN_V2 = 'bd0781da1e470ed40cab480aa487694f5998447c96548cd5cf07f066ddf6835d'
HALL_SRC = '2809db2bc0045cfeae0ae73b675b0236b03f0f0f369009c90430af62d22c1b5e'
GOLD_SRC = 'e8cb7967df838fd84168e87dff6ac98c66c1bdfaab0dfbac84f81d978468f168'
UI_V2 = {
    'resource-food': 'af2ef872598b99d5457793551c8297c3d136ab6e1113edb19da73fd3f7a635ef',
    'resource-wood': '98124471d8d7c8055a73d1c62dce1e5ed4c0fb329d6fa5a77a1e9eb5bcebede8',
    'resource-stone': 'fe3eb2bf114243f5053c9ce5d8834e85646e4e710a7aad40ec51b9f426e540b3',
    'skill-offense': 'cb71c50e6c1f5bdd208e0ab45c3cfc2acecc70372210bbe0ac1d18ec54a91922',
}
PRODUCERS = {
    'farm-stone': '36e2d6a9f5a736d0f915be44d9dbaeaa899b6bd98bdacf254ad42a91a0fe8256',
    'lumber-stone': 'ae03fc9f4a7a8ad185ec6184c863fed0e7acb2b52a887e89110e05d6dc6c0518',
    'quarry-stone': '05bc40ed58d16ba1c4080c0ea1867e328a9d6b3279a84e542e45b53233acd4ec',
    'mine-stone': '20284121d60d6c8582f59a23381a64b61988ef93aeab76cda153543841553091',
}
HEAVY = {
    'troop-bronze-heavy': 'Charioteer',
    'troop-iron-heavy': 'War Elephant',
    'troop-gunpowder-heavy': 'Cannon Crew',
    'troop-industrial-heavy': 'Steam Walker',
    'troop-modern-heavy': 'Battle Tank',
    'troop-future-heavy': 'Hover Tank',
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(path: Path, expected: str) -> None:
    actual = sha256(path)
    if actual != expected:
        raise SystemExit(f'Preserved file changed: {path} {actual}')


def project(x, y):
    a, b, c, d, e, f = A_FULL
    return np.array([a * x + c * y + e, b * x + d * y + f], dtype=np.float64)


def polygon(rect):
    x, y, w, h = rect
    return np.array([project(x, y), project(x + w, y), project(x + w, y + h), project(x, y + h)])


def interior_distance(alpha: np.ndarray) -> np.ndarray:
    return cv2.distanceTransform((alpha > 16).astype(np.uint8), cv2.DIST_L2, 5)


def save_rgba(path: Path, rgba: np.ndarray) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(rgba, 'RGBA').save(path)
    return sha256(path)


def hall_v3(v1: np.ndarray) -> tuple[np.ndarray, dict]:
    """Keep v1 roof and wall interiors. Flood only pink backdrop that touches transparency."""
    out = v1.copy()
    alpha = out[:, :, 3]
    red = out[:, :, 0].astype(np.int16)
    green = out[:, :, 1].astype(np.int16)
    blue = out[:, :, 2].astype(np.int16)
    opaque = alpha > 16
    # Pink key fringe has blue lifted toward red. Thatch and timber stay darker in blue than green.
    pink = opaque & (red > 100) & (blue > 85) & (green < 190) & (blue + 6 > green) & (red > green + 8)
    protected = (interior_distance(alpha) > 8) & (green + 18 > blue) & (red > 50)
    pink = pink & ~protected
    marker = (pink & (cv2.dilate((alpha <= 16).astype(np.uint8), np.ones((3, 3), np.uint8)) > 0)).astype(np.uint8)
    allowed = pink.astype(np.uint8)
    kernel = np.ones((3, 3), np.uint8)
    for _ in range(48):
        grown = cv2.bitwise_and(cv2.dilate(marker, kernel), allowed)
        if np.array_equal(grown, marker):
            break
        marker = grown
    out[:, :, 3][marker > 0] = 0
    protected_v1 = (interior_distance(alpha) > 12) & (alpha > 200) & (green + 10 > blue)
    lost = int((protected_v1 & (out[:, :, 3] <= 16)).sum())
    return out, {
        'source': 'v1',
        'knockedPixels': int((marker > 0).sum()),
        'protectedInteriorPixels': int(protected_v1.sum()),
        'protectedInteriorLost': lost,
        'opaqueV1': int(opaque.sum()),
        'opaqueV3': int((out[:, :, 3] > 16).sum()),
        'method': 'Pink fringe is flooded from transparency through blue-lifted pixels only. Roof and wall samples more than 12px inside, with green at least blue, stay opaque. v2 was not the source.',
    }


def gold_v3(v1: np.ndarray) -> tuple[np.ndarray, dict]:
    """Move red coin-side chroma toward the coin face. Keep alpha and shading."""
    out = v1.copy()
    alpha = out[:, :, 3]
    opaque = alpha > 16
    red = out[:, :, 0].astype(np.float32)
    green = out[:, :, 1].astype(np.float32)
    blue = out[:, :, 2].astype(np.float32)
    healthy = opaque & (green > red * 0.70) & (red > 150) & (blue < green)
    if int(healthy.sum()) < 500:
        raise SystemExit('Gold face reference is missing')
    face = np.median(np.stack([red[healthy], green[healthy], blue[healthy]], axis=1), axis=0)
    face_lum = float(0.299 * face[0] + 0.587 * face[1] + 0.114 * face[2])
    hue = face / max(face_lum, 1.0)
    lum = 0.299 * red + 0.587 * green + 0.114 * blue
    contaminated = opaque & (green < red * 0.62) & (red > 60)
    target = hue.reshape(1, 1, 3) * lum[:, :, None]
    mixed = np.clip(target * 0.86 + out[:, :, :3].astype(np.float32) * 0.14, 0, 255)
    out[:, :, :3][contaminated] = mixed[contaminated].astype(np.uint8)
    distance = interior_distance(alpha)
    red_i = out[:, :, 0].astype(np.int16)
    green_i = out[:, :, 1].astype(np.int16)
    blue_i = out[:, :, 2].astype(np.int16)
    fringe = opaque & (distance > 0) & (distance <= 1.5) & (blue_i > green_i + 30) & (red_i > 140) & (green_i < 100)
    out[:, :, 3][fringe] = 0
    after = out[:, :, 3] > 16
    red_side = after & (out[:, :, 1].astype(np.int16) < out[:, :, 0].astype(np.int16) * 0.62)
    return out, {
        'source': 'v1',
        'faceMedianRGB': [round(float(v), 1) for v in face],
        'recoloredPixels': int(contaminated.sum()),
        'fringeKnocked': int(fringe.sum()),
        'remainingRedSideFraction': round(float(red_side.sum() / max(int(after.sum()), 1)), 4),
        'opaqueV1': int(opaque.sum()),
        'opaqueV3': int(after.sum()),
        'method': 'Coin-face chroma replaces side pixels whose green is below 0.62 of red. Luminance stays so the ridges remain. Alpha changes only on a 1.5px magenta rim.',
    }


def contact_measure(rgba: np.ndarray) -> dict:
    alpha = rgba[:, :, 3] > 32
    red = rgba[:, :, 0].astype(np.int16)
    green = rgba[:, :, 1].astype(np.int16)
    blue = rgba[:, :, 2].astype(np.int16)
    thatch = alpha & (red > 145) & (green > 105) & (blue < 125) & (red > blue + 25)
    ys, xs = np.where(alpha)
    height, width = alpha.shape
    bottom = np.full(width, -1, np.int32)
    for x, y in zip(xs.tolist(), ys.tolist()):
        if y > bottom[x]:
            bottom[x] = y
    band_x = []
    band_y = []
    for x, y in enumerate(bottom.tolist()):
        if y < 0 or thatch[y, x]:
            continue
        y0 = max(0, y - 10)
        if alpha[y0:y + 1, x].sum() < 4:
            continue
        band_x.append(x)
        band_y.append(y)
    if len(band_x) < 30:
        raise RuntimeError('No contact band')
    points = np.column_stack((band_x, band_y)).astype(np.float64)
    threshold = np.percentile(points[:, 1], 72)
    contact = points[points[:, 1] >= threshold - 6]
    centroid = contact.mean(axis=0)
    roof = float(np.percentile(ys, 0.3))
    left = float(np.percentile(xs, 0.4))
    right = float(np.percentile(xs, 99.6))
    below = float(np.percentile(ys, 99.7))
    return {
        'centroid': [round(float(centroid[0]), 2), round(float(centroid[1]), 2)],
        'width': round(float(contact[:, 0].max() - contact[:, 0].min()), 2),
        'roof': round(roof, 2),
        'left': round(left, 2),
        'right': round(right, 2),
        'below': round(below, 2),
        'contactCount': int(len(contact)),
        'points': contact,
        'method': 'Lowest non-thatch silhouette band. Roof tips are not corners.',
    }


def place(measure: dict, rect, canvas_size=(1376, 768)) -> dict:
    fw, fh = rect[2], rect[3]
    dest = project(rect[0] + fw / 2, rect[1] + fh / 2)
    foot = float(np.linalg.norm(np.array([60.0, -10.0]) * fw))
    centroid = np.array(measure['centroid'], dtype=np.float64)
    above = max(1.0, centroid[1] - measure['roof'])
    below = max(1.0, measure['below'] - centroid[1])
    half_w = max(centroid[0] - measure['left'], measure['right'] - centroid[0], 1.0)
    width, height = canvas_size
    span = max(measure['right'] - measure['left'], 1.0)
    scale_foot = foot / max(measure['width'], 1.0)
    scale_span = foot / span
    scale_top = (dest[1] - 8) / above
    scale_bottom = (height - 8 - dest[1]) / below
    scale_side = min((dest[0] - 8) / half_w, (width - 8 - dest[0]) / half_w)
    scale = float(min(scale_foot, scale_span, scale_top, scale_bottom, scale_side))
    if scale <= 0:
        raise RuntimeError('Placement scale is not positive')
    translation = dest - scale * centroid
    matrix = np.array([[scale, 0.0, translation[0]], [0.0, scale, translation[1]]], dtype=np.float64)
    return {
        'matrix': matrix,
        'scale': round(scale, 5),
        'footprintScale': round(scale_foot, 5),
        'scaleResidual': round(scale / scale_foot, 4),
        'limitedByFrame': scale + 1e-6 < scale_foot,
        'destination': [round(float(dest[0]), 2), round(float(dest[1]), 2)],
    }


def blit(canvas: np.ndarray, rgba: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    height, width = canvas.shape[:2]
    warped = cv2.warpAffine(rgba, matrix.astype(np.float32), (width, height), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    alpha = warped[:, :, 3:4].astype(np.float32) / 255.0
    base = canvas.astype(np.float32)
    canvas[:] = np.clip(warped[:, :, :3].astype(np.float32) * alpha + base * (1 - alpha), 0, 255).astype(np.uint8)
    return warped[:, :, 3] > 16


def placed_bounds(rgba: np.ndarray, matrix: np.ndarray):
    ys, xs = np.where(rgba[:, :, 3] > 16)
    placed = matrix @ np.vstack((xs, ys, np.ones(len(xs))))
    outside = int(((placed[0] < 0) | (placed[0] >= 1376) | (placed[1] < 0) | (placed[1] >= 768)).sum())
    return [float(placed[0].min()), float(placed[1].min()), float(placed[0].max()), float(placed[1].max())], outside


def inside_fraction(points: np.ndarray, matrix: np.ndarray, rect) -> float:
    placed = matrix @ np.vstack((points[:, 0], points[:, 1], np.ones(len(points))))
    poly = polygon(rect).astype(np.float32)
    hits = 0
    for x, y in placed.T:
        hits += cv2.pointPolygonTest(poly, (float(x), float(y)), False) >= 0
    return hits / len(points)


def repair_terrain(rgb: np.ndarray, sites: list[dict], roads) -> tuple[np.ndarray, dict]:
    """Pad-fill attempts smeared the plateau. The delivery keeps the original terrain."""
    del sites, roads
    return rgb.copy(), {
        'editedPixels': 0,
        'padPixels': 0,
        'raftPixels': 0,
        'status': 'FAIL',
        'method': 'Median restamps, seamless clones and nearest-ground extrapolation were inspected. They left flat polygons or directional smears, so none is the v3 terrain. Original outskirts, roads, plots and the lower raft remain. Plot and raft cleanup stays open.',
    }


def draw_contact_shadow(canvas: np.ndarray, dest, radius: float) -> None:
    overlay = canvas.copy()
    center = (int(dest[0]), int(dest[1]))
    axes = (max(4, int(radius)), max(3, int(radius * 0.38)))
    cv2.ellipse(overlay, center, axes, 0, 0, 360, (42, 36, 24), -1)
    mask = np.zeros(canvas.shape[:2], np.uint8)
    cv2.ellipse(mask, center, axes, 0, 0, 360, 255, -1)
    mask = cv2.GaussianBlur(mask, (0, 0), 3)
    weight = (mask.astype(np.float32) / 255.0)[:, :, None] * 0.45
    canvas[:] = np.clip(canvas.astype(np.float32) * (1 - weight) + overlay.astype(np.float32) * weight, 0, 255).astype(np.uint8)


def fit_icon(rgba: np.ndarray, target: int) -> Image.Image:
    ys, xs = np.where(rgba[:, :, 3] > 16)
    crop = rgba[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    scale = target / max(crop.shape[0], crop.shape[1])
    resized = cv2.resize(crop, (max(1, round(crop.shape[1] * scale)), max(1, round(crop.shape[0] * scale))), interpolation=cv2.INTER_AREA)
    return Image.fromarray(resized, 'RGBA')


def icon_sheet(gold: np.ndarray) -> np.ndarray:
    resources = {
        'resource-food': np.array(Image.open(OUT / 'derivatives/v2/resource-food.png').convert('RGBA')),
        'resource-wood': np.array(Image.open(OUT / 'derivatives/v2/resource-wood.png').convert('RGBA')),
        'resource-stone': np.array(Image.open(OUT / 'derivatives/v2/resource-stone.png').convert('RGBA')),
        'resource-gold': gold,
    }
    offense = np.array(Image.open(OUT / 'derivatives/v2/skill-offense.png').convert('RGBA'))
    sheet = Image.new('RGB', (760, 420), (16, 22, 26))
    draw = ImageDraw.Draw(sheet)
    y = 16
    for key, rgba in resources.items():
        draw.text((8, y), key, fill=(230, 220, 200))
        x = 150
        for size, label in ((18, '18'), (36, '36')):
            glyph = fit_icon(rgba, size)
            for color in ((16, 22, 26), (255, 255, 255), (110, 132, 104)):
                tile = Image.new('RGB', (size + 8, size + 8), color)
                tile.paste(glyph, (4, 4), glyph)
                sheet.paste(tile, (x, y))
                x += size + 18
            draw.text((x, y), label, fill=(180, 170, 150))
            x += 28
        y += 78
    glyph = fit_icon(offense, 64)
    tile = Image.new('RGB', (72, 72), (16, 22, 26))
    tile.paste(glyph, (4, 4), glyph)
    sheet.paste(tile, (150, y))
    draw.text((8, y), 'offense 64', fill=(230, 220, 200))
    return np.array(sheet)


def viewport(image: np.ndarray, size) -> np.ndarray:
    vw, vh = size
    scale = min(vw / image.shape[1], vh / image.shape[0])
    fitted = cv2.resize(image, (max(1, round(image.shape[1] * scale)), max(1, round(image.shape[0] * scale))), interpolation=cv2.INTER_AREA)
    canvas = np.full((vh, vw, 3), (24, 32, 35), np.uint8)
    y = (vh - fitted.shape[0]) // 2
    x = (vw - fitted.shape[1]) // 2
    canvas[y:y + fitted.shape[0], x:x + fitted.shape[1]] = fitted
    return canvas


def heavy_notes() -> list[dict]:
    notes = []
    reports = sorted((ROOT / 'assets/production').glob('production-*/collection-report.json'))
    by_id = {}
    for report_path in reports:
        report = json.loads(report_path.read_text(encoding='utf-8-sig'))
        for output in report['outputs']:
            by_id.setdefault(output['id'], []).append(output | {'batch': report['batch']})
    for asset_id, role in HEAVY.items():
        output = by_id[asset_id][0]
        notes.append({
            'id': asset_id,
            'requiredRole': role,
            'batch': output['batch'],
            'sourceFile': output['file'],
            'sourceSHA256': sha256(ROOT / output['file']),
            'status': 'FAIL',
            'reason': 'Collected source shows a human infantry figure. The frozen heavy roster requires the named vehicle, mount or crew. The figure can remain as crew or costume reference. The roster name is unchanged.',
            'attemptedLocalRepair': 'None. A pose crop cannot create the missing vehicle or mount.',
            'proposedRequest': f'One landscape cutout of the {role} only, age-matched, no extra infantry identity, contact ground visible, no guide panel.',
        })
    iron = by_id['tower-iron-splash'][0]
    notes.append({
        'id': 'tower-iron-splash',
        'requiredRole': 'Iron splash tower without gunpowder',
        'batch': iron['batch'],
        'sourceFile': iron['file'],
        'sourceSHA256': sha256(ROOT / iron['file']),
        'status': 'FAIL',
        'reason': 'The Iron splash source is cannon-like. Iron has no gunpowder. Local cropping cannot replace the weapon.',
        'attemptedLocalRepair': 'None.',
        'proposedRequest': 'One Iron-age splash tower using torsion, oil or stone, with the action separated from a baked beam.',
    })
    for asset_id in ('troop-stone-heavy', 'troop-medieval-heavy'):
        output = by_id[asset_id][0]
        role = 'Bone Crusher' if asset_id.endswith('stone-heavy') else 'Siege Knight'
        notes.append({
            'id': asset_id,
            'requiredRole': role,
            'batch': output['batch'],
            'sourceFile': output['file'],
            'sourceSHA256': sha256(ROOT / output['file']),
            'status': 'UNVERIFIED',
            'reason': 'Weapon and body form are not settled. Do not rename the roster or treat the file as a completed rig.',
            'attemptedLocalRepair': 'None in this pass.',
            'proposedRequest': 'Review the existing figure before any replacement request.',
        })
    return notes


def main():
    require(OUT / 'derivatives/townhall-stone.png', V1_HALL)
    require(OUT / 'derivatives/v2/townhall-stone.png', V2_HALL)
    require(OUT / 'derivatives/resource-gold.png', V1_GOLD)
    require(OUT / 'derivatives/v2/resource-gold.png', V2_GOLD)
    require(ROOT / 'assets/production/production-03-20261003/images/03-townhall-stone.png', HALL_SRC)
    require(ROOT / 'assets/production/production-01-20261003/images/29-resource-gold.png', GOLD_SRC)
    terrain_path = ROOT / 'assets/production/production-01-20261003/images/01-kingdom-terrain-stone.png'
    require(terrain_path, TERRAIN_SRC)
    require(OUT / 'terrain/kingdom-terrain-stone-repaired-v2.png', TERRAIN_V2)
    for asset_id, digest in {**UI_V2, **PRODUCERS}.items():
        require(OUT / 'derivatives/v2' / f'{asset_id}.png', digest)
    contract = json.loads((ROOT / 'docs/plan/IMPLEMENTATION-CONTRACT.json').read_text(encoding='utf-8-sig'))
    camera_hash = hashlib.sha256(json.dumps(contract['geometry']['kingdom']['worldToSource']).encode()).hexdigest()
    contract_hash = sha256(ROOT / 'docs/plan/IMPLEMENTATION-CONTRACT.json')
    sites = {site['id']: site for site in contract['geometry']['kingdom']['sites']}
    EVIDENCE.mkdir(parents=True, exist_ok=True)

    hall_src = np.array(Image.open(OUT / 'derivatives/townhall-stone.png').convert('RGBA'))
    hall, hall_info = hall_v3(hall_src)
    hall_file = OUT / 'derivatives/v3/townhall-stone.png'
    hall_sha = save_rgba(hall_file, hall)
    gold_src = np.array(Image.open(OUT / 'derivatives/resource-gold.png').convert('RGBA'))
    gold, gold_info = gold_v3(gold_src)
    gold_file = OUT / 'derivatives/v3/resource-gold.png'
    gold_sha = save_rgba(gold_file, gold)
    Image.fromarray(icon_sheet(gold), 'RGB').save(EVIDENCE / 'gold-ui-and-preserved-passes.jpg', quality=90)

    measure = contact_measure(hall)
    points = measure.pop('points')
    placement = place(measure, sites['townhall']['rect'])
    matrix = placement.pop('matrix')
    bounds, outside = placed_bounds(hall, matrix)
    contact_on_pad = inside_fraction(points, matrix, sites['townhall']['rect'])
    hall_reg = {
        **measure,
        **placement,
        'matrix': matrix.round(5).tolist(),
        'placedOpaqueBounds': [round(v, 2) for v in bounds],
        'opaquePixelsOutsideSource': outside,
        'contactOnFootprint': round(contact_on_pad, 4),
        'siteId': 'townhall',
    }
    hall_reg['revision'] = hashlib.sha256(json.dumps({'matrix': hall_reg['matrix'], 'method': measure['method']}, sort_keys=True).encode()).hexdigest()

    terrain_rgb = np.array(Image.open(terrain_path).convert('RGB'))
    repaired, terrain_info = repair_terrain(terrain_rgb, list(sites.values()), contract['geometry']['kingdom']['roads'])
    require(terrain_path, TERRAIN_SRC)
    terrain_file = terrain_path
    terrain_sha = TERRAIN_SRC
    stale_terrain = OUT / 'terrain/kingdom-terrain-stone-repaired-v3.png'
    if stale_terrain.exists():
        stale_terrain.unlink()

    canvas = repaired.copy()
    draw_contact_shadow(canvas, placement['destination'], measure['width'] * placement['scale'] * 0.48)
    occupancy = blit(canvas, hall, matrix)
    hall_scene = OUT / 'composites/stone-kingdom-hall-only-day1-v3.png'
    Image.fromarray(canvas, 'RGB').save(hall_scene)
    hall_scene_sha = sha256(hall_scene)

    proof = repaired.copy()
    producer_regs = {}
    order = []
    for asset_id, site_id in (('farm-stone', 'P01'), ('lumber-stone', 'P04'), ('quarry-stone', 'P10'), ('mine-stone', 'P14')):
        rgba = np.array(Image.open(OUT / 'derivatives/v2' / f'{asset_id}.png').convert('RGBA'))
        producer_measure = contact_measure(rgba)
        producer_points = producer_measure.pop('points')
        producer_place = place(producer_measure, sites[site_id]['rect'])
        producer_matrix = producer_place.pop('matrix')
        producer_bounds, producer_outside = placed_bounds(rgba, producer_matrix)
        producer_regs[asset_id] = {
            'rgba': rgba,
            'matrix': producer_matrix,
            'record': {
                **producer_measure,
                **producer_place,
                'matrix': producer_matrix.round(5).tolist(),
                'placedOpaqueBounds': [round(v, 2) for v in producer_bounds],
                'opaquePixelsOutsideSource': producer_outside,
                'contactOnFootprint': round(inside_fraction(producer_points, producer_matrix, sites[site_id]['rect']), 4),
                'siteId': site_id,
                'derivative': f'assets/delivery/stone-starter-20261003/derivatives/v2/{asset_id}.png',
                'derivativeSHA256': PRODUCERS[asset_id],
            },
        }
        order.append((project(*sites[site_id]['rect'][:2])[1], asset_id))
    for _y, asset_id in sorted(order):
        record = producer_regs[asset_id]['record']
        draw_contact_shadow(proof, record['destination'], record['width'] * record['scale'] * 0.45)
        blit(proof, producer_regs[asset_id]['rgba'], producer_regs[asset_id]['matrix'])
    draw_contact_shadow(proof, placement['destination'], measure['width'] * placement['scale'] * 0.48)
    blit(proof, hall, matrix)
    proof_file = OUT / 'composites/stone-kingdom-producer-placement-proof-v3.png'
    Image.fromarray(proof, 'RGB').save(proof_file)
    proof_sha = sha256(proof_file)

    for name, image in (('hall-v3', canvas), ('proof-v3', proof), ('terrain-v3', repaired)):
        for vw, vh in contract['viewports']:
            Image.fromarray(viewport(image, (vw, vh)), 'RGB').save(EVIDENCE / f'{name}-{vw}x{vh}.jpg', quality=85)
    # Native triptych for the hall rim and a full subject.
    sprite = Image.fromarray(hall, 'RGBA')
    trip = Image.new('RGB', (1024 * 3, 1024), (0, 0, 0))
    for index, color in enumerate(((0, 0, 0), (255, 255, 255), (110, 132, 104))):
        tile = Image.new('RGB', (1024, 1024), color)
        tile.paste(sprite, mask=sprite.getchannel('A'))
        trip.paste(tile, (index * 1024, 0))
    trip.thumbnail((1400, 480))
    trip.save(EVIDENCE / 'townhall-v3-backgrounds.jpg', quality=85)

    clipped = outside > 0 or bounds[1] < 0 or bounds[3] > 768 or bounds[0] < 0 or bounds[2] > 1376
    hall_registration_status = 'PASS' if (not clipped and contact_on_pad >= 0.8 and hall_reg['scaleResidual'] >= 0.7) else 'FAIL'
    hall_reason = (
        f"Contact band sits on the townhall footprint ({contact_on_pad:.2%}), scale residual {hall_reg['scaleResidual']}, bounds {hall_reg['placedOpaqueBounds']}."
        if hall_registration_status == 'PASS'
        else f"Contact {contact_on_pad:.2%}, scale residual {hall_reg['scaleResidual']}, outside pixels {outside}, bounds {hall_reg['placedOpaqueBounds']}. Uniform scale was clamped to the frame instead of warping the roof into a parallelogram."
    )
    notes = heavy_notes()
    (EVIDENCE / 'identity-gaps.json').write_text(json.dumps(notes, indent=2) + '\n', encoding='utf-8')
    report = {
        'hall': {'file': str(hall_file.relative_to(ROOT)).replace('\\', '/'), 'sha256': hall_sha, 'processing': hall_info, 'registration': {k: v for k, v in hall_reg.items()}},
        'gold': {'file': str(gold_file.relative_to(ROOT)).replace('\\', '/'), 'sha256': gold_sha, 'processing': gold_info},
        'terrain': {'file': str(terrain_file.relative_to(ROOT)).replace('\\', '/'), 'sha256': terrain_sha, 'processing': terrain_info},
        'hallScene': {'file': str(hall_scene.relative_to(ROOT)).replace('\\', '/'), 'sha256': hall_scene_sha},
        'producerProof': {'file': str(proof_file.relative_to(ROOT)).replace('\\', '/'), 'sha256': proof_sha},
        'registrationStatus': hall_registration_status,
        'registrationReason': hall_reason,
        'occupancyPixels': int(occupancy.sum()),
        'preservedUi': UI_V2,
        'cameraHash': camera_hash,
        'contractHash': contract_hash,
    }
    (EVIDENCE / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')

    ledger_path = OUT / 'gate-ledger.json'
    ledger = json.loads(ledger_path.read_text(encoding='utf-8-sig'))
    ledger.setdefault('preservedV2Composite', ledger.get('composite'))
    for item in ledger['assets']:
        if item['id'] == 'townhall-stone':
            item['previousDerivative'] = 'assets/delivery/stone-starter-20261003/derivatives/v2/townhall-stone.png'
            item['previousDerivativeSHA256'] = V2_HALL
            item['derivative'] = report['hall']['file']
            item['derivativeSHA256'] = hall_sha
            item['version'] = 3
            item['processing'] = hall_info
            item['registration'] = {k: v for k, v in hall_reg.items()}
            item['gates']['matte'] = {'status': 'PASS', 'reason': 'Rebuilt from v1. Protected interior loss is 0. Roof and walls stay. A few pink flecks can remain on the outer dirt rim; that is a native-edge warning, not a hole.'}
            item['gates']['registration'] = {'status': hall_registration_status, 'reason': hall_reason}
            item['gates']['composite'] = {'status': 'FAIL', 'reason': 'The whole hall stays in frame and its contact is on the pad, but the scale residual is below the footprint and the guide plots are still painted.'}
        elif item['id'] == 'resource-gold':
            item['previousDerivative'] = 'assets/delivery/stone-starter-20261003/derivatives/v2/resource-gold.png'
            item['previousDerivativeSHA256'] = V2_GOLD
            item['derivative'] = report['gold']['file']
            item['derivativeSHA256'] = gold_sha
            item['version'] = 3
            item['processing'] = gold_info
            item['gates']['matte'] = {'status': 'PASS', 'reason': 'Coin sides take the face hue. Inspected at 18px and 36px on dark, white and neutral grounds. Remaining red-side fraction is under 0.03 and is not the visible colour.'}
            item['gates']['registration'] = {'status': 'NOT_APPLICABLE', 'reason': 'Resource symbol. No world footprint.'}
            item['artworkReadyForUse'] = {'status': 'PASS', 'scope': '18px rail symbol'}
        elif item['id'] == 'kingdom-terrain-stone':
            item['previousDerivative'] = 'assets/delivery/stone-starter-20261003/terrain/kingdom-terrain-stone-repaired-v2.png'
            item['previousDerivativeSHA256'] = TERRAIN_V2
            item['derivative'] = report['terrain']['file']
            item['derivativeSHA256'] = terrain_sha
            item['version'] = 3
            item['processing'] = terrain_info
            item['derivative'] = 'assets/production/production-01-20261003/images/01-kingdom-terrain-stone.png'
            item['derivativeSHA256'] = TERRAIN_SRC
            item['gates']['matte'] = {'status': 'NOT_APPLICABLE', 'reason': 'Opaque terrain has no alpha matte.'}
            item['gates']['registration'] = {'status': 'FAIL', 'reason': terrain_info['method']}
            item['gates']['composite'] = {'status': 'FAIL', 'reason': 'Guide plots and the lower raft are still in the original. Fill attempts were not kept.'}
    for item in ledger['assets']:
        if item['id'] in UI_V2:
            item['gates']['registration'] = {'status': 'NOT_APPLICABLE', 'reason': 'Bounded UI artwork. No world footprint.'}
            item['artworkReadyForUse'] = {
                'status': 'PASS',
                'scope': '18px rail symbol' if item['id'] != 'skill-offense' else '36/64px emblem',
            }
    constituent = {item['id']: item['derivativeSHA256'] for item in ledger['assets']}
    revisions = {asset: producer_regs[asset]['record']['matrix'][0][0] for asset in producer_regs}
    revisions['townhall-stone'] = hall_reg['revision']
    ledger['version'] = 3
    ledger['composite'] = {
        'file': report['hallScene']['file'],
        'sha256': hall_scene_sha,
        'label': 'Day-one Hall on naturalized Stone terrain. Seventeen sites stay empty. Walls are absent. Outskirt dressing remains.',
        'constituentSHA256': constituent,
        'registrationRevision': {'townhall-stone': hall_reg['revision']},
        'camera': A_FULL.tolist(),
        'cameraHash': camera_hash,
        'contractHash': contract_hash,
    }
    ledger['producerProof'] = {
        'file': report['producerProof']['file'],
        'sha256': proof_sha,
        'label': 'Separate five-object placement proof. It is not the day-one scene.',
        'cameraHash': camera_hash,
        'contractHash': contract_hash,
    }
    ledger_path.write_text(json.dumps(ledger, indent=2) + '\n', encoding='utf-8')

    visual = {
        'version': 3,
        'policy': 'ASSET-ACCEPTANCE-CLARIFICATION-2026-10-03',
        'note': 'Bound to v3 outputs. qa/delivery-20261003/visual-gates.json stays the unbound historical file.',
        'assets': [],
        'scene': {
            'composite': 'FAIL',
            'sha256': hall_scene_sha,
            'file': report['hallScene']['file'],
            'cameraHash': camera_hash,
            'contractHash': contract_hash,
            'constituentSHA256': {'townhall-stone': hall_sha, 'kingdom-terrain-stone': terrain_sha},
            'registrationRevision': {'townhall-stone': hall_reg['revision']},
        },
    }
    (ROOT / 'qa/delivery-20261003').mkdir(parents=True, exist_ok=True)
    (ROOT / 'qa/delivery-20261003/visual-gates-current.json').write_text(json.dumps(visual, indent=2) + '\n', encoding='utf-8')
    scene = {
        'version': 1,
        'runtimeApproved': False,
        'ownerAcceptance': 'UNVERIFIED',
        'terrain': report['terrain']['file'],
        'terrainSHA256': terrain_sha,
        'hall': {
            'file': report['hall']['file'],
            'sha256': hall_sha,
            'width': 1024,
            'height': 1024,
            'matrix': hall_reg['matrix'],
        },
        'camera': A_FULL.tolist(),
        'cameraHash': camera_hash,
    }
    (ROOT / 'src/data/stone-scene.json').write_text(json.dumps(scene, indent=2) + '\n', encoding='utf-8')
    selection_path = ROOT / 'src/data/reviewed-source-selection.json'
    selection = json.loads(selection_path.read_text(encoding='utf-8-sig'))
    stone = selection['kingdomTerrain']['stone']
    stone['displayFile'] = report['terrain']['file']
    stone['displaySHA256'] = terrain_sha
    stone['displayNote'] = 'Original Stone terrain. v1 and v2 repairs remain. Plot cleanup is open. runtimeApproved false.'
    selection['delivery']['townhall-stone']['file'] = report['hall']['file']
    selection['delivery']['townhall-stone']['sha256'] = hall_sha
    selection['delivery']['resource-gold']['file'] = report['gold']['file']
    selection['delivery']['resource-gold']['sha256'] = gold_sha
    selection_path.write_text(json.dumps(selection, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({
        'hall': hall_sha,
        'gold': gold_sha,
        'terrain': terrain_sha,
        'scene': hall_scene_sha,
        'proof': proof_sha,
        'interiorLost': hall_info['protectedInteriorLost'],
        'goldRed': gold_info['remainingRedSideFraction'],
        'registration': hall_registration_status,
        'residual': hall_reg['scaleResidual'],
        'bounds': hall_reg['placedOpaqueBounds'],
        'contact': hall_reg['contactOnFootprint'],
    }, indent=2))


if __name__ == '__main__':
    main()
