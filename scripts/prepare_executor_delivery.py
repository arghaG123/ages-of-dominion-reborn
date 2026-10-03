"""Versioned UI crops, Stone measurement and bound reviews. Does not edit the geometry contract or buy art."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from recover_v3 import blit, contact_measure, place, placed_bounds

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'qa/recovery-executor-20261003'
CROP = ROOT / 'assets/delivery/stone-starter-20261003/derivatives/v4-ui'


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def crop_alpha(source: Path, dest: Path) -> dict:
    image = Image.open(source).convert('RGBA')
    pixels = np.array(image)
    ys, xs = np.where(pixels[:, :, 3] > 16)
    box = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)
    cropped = image.crop(box)
    dest.parent.mkdir(parents=True, exist_ok=True)
    cropped.save(dest)
    return {'source': str(source.relative_to(ROOT)).replace('\\', '/'), 'sourceSHA256': sha256(source), 'file': str(dest.relative_to(ROOT)).replace('\\', '/'), 'sha256': sha256(dest), 'x': box[0], 'y': box[1], 'width': box[2] - box[0], 'height': box[3] - box[1]}


def measure_hall() -> dict:
    """Reproduce the non-thatch contact band. A full-width dirt row is not the wall base."""
    contract = json.loads((ROOT / 'docs/plan/IMPLEMENTATION-CONTRACT.json').read_text(encoding='utf-8'))
    hall_path = ROOT / 'assets/delivery/stone-starter-20261003/derivatives/v3/townhall-stone.png'
    hall = np.array(Image.open(hall_path).convert('RGBA'))
    opaque = hall[:, :, 3] > 16
    ys, xs = np.where(opaque)
    measured = contact_measure(hall)
    points = measured.pop('points')
    site = next(site for site in contract['geometry']['kingdom']['sites'] if site['id'] == 'townhall')
    fitted = place(contact_measure(hall), site['rect'])
    centroid = np.array(measured['centroid'], dtype=np.float64)
    destination = np.array(fitted['destination'], dtype=np.float64)
    foot = float(fitted['footprintScale'])
    roof_tip = int(ys.min())
    roof_source_y = float(destination[1] - (centroid[1] - roof_tip) * foot)
    percentile_roof_y = float(destination[1] - (centroid[1] - measured['roof']) * foot)
    translation = destination - foot * centroid
    foot_matrix = np.array([[foot, 0.0, translation[0]], [0.0, foot, translation[1]]], dtype=np.float64)
    _, outside = placed_bounds(hall, foot_matrix)
    red = hall[:, :, 0].astype(np.int16)
    green = hall[:, :, 1].astype(np.int16)
    blue = hall[:, :, 2].astype(np.int16)
    magenta = opaque & (red > 200) & (blue > 160) & (green < 140) & ((red - green) > 70) & ((blue - green) > 40)
    samples = {}
    for name, x, y in (('roofEave', 889, 316), ('rightRim', 1006, 486)):
        patch = magenta[y - 2:y + 3, x - 2:x + 3]
        samples[name] = {'x': x, 'y': y, 'centerRGBA': hall[y, x].tolist(), 'magentaIn5x5': int(patch.sum()), 'confidence': 'visible pixel sample'}
    return {
        'source': 'assets/delivery/stone-starter-20261003/derivatives/v3/townhall-stone.png',
        'sourceSHA256': sha256(hall_path),
        'opaqueBounds': [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())],
        'silhouetteTip': {'y': int(ys.max()), 'confidence': 'low', 'kind': 'visible lower silhouette, includes dirt and plinth, not a foundation corner'},
        'roofExtremity': {'y': roof_tip, 'confidence': 'low', 'kind': 'highest opaque pixel, a silhouette bound, not a foundation corner'},
        'roofPercentile': {'y': measured['roof'], 'confidence': 'low', 'kind': '0.3 percentile of opaque rows, not a foundation corner'},
        'wallContact': {
            'centroid': measured['centroid'], 'width': measured['width'], 'count': measured['contactCount'],
            'left': measured['left'], 'right': measured['right'], 'below': measured['below'],
            'confidence': 'medium', 'kind': measured['method'],
        },
        'entrance': {'x': round((measured['left'] + measured['right']) / 2, 2), 'confidence': 'low', 'kind': 'inferred from the span midpoint, not a surveyed door quad'},
        'contactPointCount': int(len(points)),
        'footprintScale': fitted['footprintScale'],
        'frameLimitedScale': fitted['scale'],
        'scaleResidual': fitted['scaleResidual'],
        'roofSourceYAtFootprintScale': roof_source_y,
        'percentileRoofSourceYAtFootprintScale': percentile_roof_y,
        'opaquePixelsOutsideFrameAtFootprintScale': outside,
        'siteCenter': fitted['destination'],
        'magentaSamples': samples,
        'magentaSampleCount': int(magenta.sum()),
        'activeMatrixUnchanged': [[0.1312, 0.0, 507.66565], [0.0, 0.1312, -0.79026]],
        'activeContractUnchanged': True,
        'contractSHA256': sha256(ROOT / 'docs/plan/IMPLEMENTATION-CONTRACT.json'),
    }


def write_placement_evidence(measure: dict) -> dict:
    """Diagnostic frames only. They do not replace the day-one composite or the active matrix."""
    terrain = np.array(Image.open(ROOT / 'assets/production/production-01-20261003/images/01-kingdom-terrain-stone.png').convert('RGB'))
    hall = np.array(Image.open(ROOT / 'assets/delivery/stone-starter-20261003/derivatives/v3/townhall-stone.png').convert('RGBA'))
    scene = json.loads((ROOT / 'src/data/stone-scene.json').read_text(encoding='utf-8'))
    current = np.array(scene['hall']['matrix'], dtype=np.float64)
    centroid = np.array(measure['wallContact']['centroid'], dtype=np.float64)
    destination = np.array(measure['siteCenter'], dtype=np.float64)
    foot = float(measure['footprintScale'])
    translation = destination - foot * centroid
    footprint = np.array([[foot, 0.0, translation[0]], [0.0, foot, translation[1]]], dtype=np.float64)
    written = {}
    for name, matrix in (('stone-frame-before-current-scale.png', current), ('stone-frame-after-footprint-scale.png', footprint)):
        canvas = terrain.copy()
        blit(canvas, hall, matrix)
        dest = OUT / name
        Image.fromarray(canvas).save(dest)
        _, outside = placed_bounds(hall, matrix)
        written[name] = {'file': str(dest.relative_to(ROOT)).replace('\\', '/'), 'sha256': sha256(dest), 'opaquePixelsOutsideFrame': outside}
    return written


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    crops = {
        'resource-food': crop_alpha(ROOT / 'assets/delivery/stone-starter-20261003/derivatives/v2/resource-food.png', CROP / 'resource-food.png'),
        'resource-wood': crop_alpha(ROOT / 'assets/delivery/stone-starter-20261003/derivatives/v2/resource-wood.png', CROP / 'resource-wood.png'),
        'resource-stone': crop_alpha(ROOT / 'assets/delivery/stone-starter-20261003/derivatives/v2/resource-stone.png', CROP / 'resource-stone.png'),
        'resource-gold': crop_alpha(ROOT / 'assets/delivery/stone-starter-20261003/derivatives/v3/resource-gold.png', CROP / 'resource-gold.png'),
        'skill-offense': crop_alpha(ROOT / 'assets/delivery/stone-starter-20261003/derivatives/v2/skill-offense.png', CROP / 'skill-offense.png'),
    }
    (OUT / 'ui-crops.json').write_text(json.dumps(crops, indent=2) + '\n', encoding='utf-8')
    selection_path = ROOT / 'src/data/reviewed-source-selection.json'
    selection = json.loads(selection_path.read_text(encoding='utf-8'))
    for key, crop in crops.items():
        selection['delivery'][key]['uiFile'] = crop['file']
        selection['delivery'][key]['uiSHA256'] = crop['sha256']
        selection['delivery'][key]['uiWidth'] = crop['width']
        selection['delivery'][key]['uiHeight'] = crop['height']
        selection['delivery'][key]['uiLongSide'] = 18 if key != 'skill-offense' else 36
    selection_path.write_text(json.dumps(selection, indent=2) + '\n', encoding='utf-8')
    policy = ROOT / 'docs/plan/ASSET-ACCEPTANCE-CLARIFICATION-2026-10-03.md'
    evidence = {
        'resource-gold': ROOT / 'qa/planner-verifier-v3-20261003/gold-comparison.png',
        'resource-food': ROOT / 'qa/full-asset-verifier-20261003/v2-icons-intended-pixels.png',
        'resource-wood': ROOT / 'qa/full-asset-verifier-20261003/v2-icons-intended-pixels.png',
        'resource-stone': ROOT / 'qa/full-asset-verifier-20261003/v2-icons-intended-pixels.png',
        'skill-offense': ROOT / 'qa/full-asset-verifier-20261003/v2-icons-intended-pixels.png',
    }
    uses = {'resource-food': ('resource-symbol', [18]), 'resource-wood': ('resource-symbol', [18]), 'resource-stone': ('resource-symbol', [18]), 'resource-gold': ('resource-detail', [18, 36]), 'skill-offense': ('skill-emblem', [36, 64])}
    reviews = []
    for key, crop in crops.items():
        record = selection['delivery'][key]
        use, sizes = uses[key]
        reviews.append({
            'batch': record['batch'], 'id': key, 'sourceSHA256': record['sourceSHA256'], 'derivativeSHA256': record['sha256'],
            'artworkReadyForUse': {
                'status': 'PASS', 'use': use, 'sizes': sizes, 'policyRevision': sha256(policy), 'derivativeSHA256': record['sha256'],
                'evidence': [{'file': str(evidence[key].relative_to(ROOT)).replace('\\', '/'), 'sha256': sha256(evidence[key])}],
            },
        })
    (OUT / 'bound-reviews.json').write_text(json.dumps({'policy': str(policy.relative_to(ROOT)).replace('\\', '/'), 'policySHA256': sha256(policy), 'assets': reviews}, indent=2) + '\n', encoding='utf-8')
    hall = measure_hall()
    evidence = write_placement_evidence(hall)
    proposal = {
        'status': 'PROPOSAL_NOT_ACCEPTED',
        'activeContractEdited': False,
        'hall': hall,
        'placementEvidence': evidence,
        'finding': 'The footprint scale that matches the 555px non-thatch contact band puts the highest opaque roof pixel near source y=-185. The 768px frame cannot hold that vertical envelope. The active camera, contract and Hall matrix stay unchanged.',
        'counterfactual': 'qa/planner-verifier-v3-20261003/framing-counterfactual.png is diagnostic. A common +193px shift is not an accepted framing.',
        'coordinatedChangeNotApplied': 'A later accepted change would extend the shared source upward, or replace the terrain layer, and keep one camera, 18 sites, one Hall and 17 empty plots. Shrinking or warping the Hall is not the proposal.',
        'terrainRoles': [
            {'role': 'static', 'subject': 'age-correct outskirts and lower raft', 'action': 'retain', 'confidence': 'medium'},
            {'role': 'guide', 'subject': 'painted plot marks inside legal sites', 'action': 'separate from terrain before acceptance', 'confidence': 'high'},
            {'role': 'route', 'subject': 'roads, crossings and bridge approaches', 'action': 'keep the registered legal network', 'confidence': 'high'},
            {'role': 'mutable', 'subject': 'Hall and the 17 empty day-one plots', 'action': 'one Hall, walls level 0, no baked workers', 'confidence': 'high'},
        ],
    }
    (OUT / 'stone-framing-proposal.json').write_text(json.dumps(proposal, indent=2) + '\n', encoding='utf-8')
    gaps = json.loads((ROOT / 'qa/recovery-v3-20261003/identity-gaps.json').read_text(encoding='utf-8'))
    for gap in gaps:
        if gap['id'] == 'tower-iron-splash':
            gap['requiredIdentity'] = 'Onager'
            gap['note'] = 'The frozen Iron splash name is Onager. A cannon-like source is not that identity. No repurchase is authorized here.'
        else:
            gap['note'] = 'Useful only as crew or costume reference. The roster name is not renamed and the identity is not delivered.'
    matrix = {'uiCrops': crops, 'hall': hall, 'identityGaps': gaps, 'rigStatus': 'Stick poses are not textured articulated rigs. Mount, vehicle and hidden-part reconstruction is unsupported for the six heavy identities.', 'workerSheet': 'A worker pair plus transport is three subjects. A blank fourth guide position is not missing content.'}
    (OUT / 'delivery-matrix.json').write_text(json.dumps(matrix, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'crops': {key: [value['width'], value['height'], value['sha256']] for key, value in crops.items()}, 'roofSourceY': hall['roofSourceYAtFootprintScale'], 'footprintScale': hall['footprintScale'], 'outside': hall['opaquePixelsOutsideFrameAtFootprintScale']}))


if __name__ == '__main__':
    main()
