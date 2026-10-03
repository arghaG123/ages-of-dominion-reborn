"""Prepare batch 04 locally: five carried Stone buildings, then the next 25 building identities. No provider call."""
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / 'docs/plan/image-production'
MOCKS = ROOT / 'design-preview/generated/landscape-mocks-20261003-efcd7a7e/images'
GUIDES = PLAN / 'guides'

def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()

def sha_file(path):
    return sha_bytes(path.read_bytes())

COMMON = (
    'ONE production image for Ages of Dominion. Semi-realistic dense inhabited rendered strategy-game materials, '
    'warm upper-left daylight, short soft contact shadows, coherent camera, high aerial three-quarter elevation55 yaw15. '
    'NO text, HUD, buttons, labels, numbers, device frame, watermark, or invented names. '
    'The first image is an exact spatial guide. The second image is material finish only; do not copy its buildings or UI. '
    'A guide mark is a specification, not art to reproduce. Never shift the camera, river, or landmarks. '
)

AGES = {
    'stone': ('03-kingdom-stone.jpg', 'timber, hide, thatch, flint and dirt. No medieval church, towers or steel.'),
    'bronze': ('04-kingdom-bronze.jpg', 'earth, plaster, early stone and bronze. No steel plate or later machinery.'),
    'iron': ('05-kingdom-iron.jpg', 'masonry, tiled roofs and iron. No gunpowder or modern concrete.'),
    'medieval': ('06-kingdom-medieval.jpg', 'coursed stone, timber, slate and terracotta. No firearms or factory yards.'),
}
BUILDINGS = {
    'farm': ('farm plot with planted beds', [1.4, 1.2]),
    'lumber': ('lumber camp with stacked timber', [1.4, 1.2]),
    'quarry': ('quarry works cut into rock', [1.4, 1.2]),
    'mine': ('mine entrance in rock', [1.4, 1.2]),
    'barracks': ('barracks hall', [1.4, 1.2]),
    'workshop': ('workshop yard', [1.4, 1.2]),
    'hall': ('great hall, distinct from the upper Town Hall', [1.4, 1.2]),
    'armory': ('armory store', [1.4, 1.2]),
    'walls': ('modular perimeter sheet: one straight segment, one corner and one gate, separated from each other', [4.2, 1.2]),
}

def object_guide(item_id, footprint):
    contract = json.loads((ROOT / 'docs/plan/IMPLEMENTATION-CONTRACT.json').read_text(encoding='utf-8'))
    source = contract['geometry']['kingdom']['worldToSource']
    image = Image.new('RGB', (1024, 1024), '#ff00ff')
    draw = ImageDraw.Draw(image)
    fw, fh = footprint
    unit = 170 / max(fw, fh)
    a, b, c, d = [v * unit / source[0] for v in source[:4]]
    ox, oy = 512 - (a * fw + c * fh) / 2, 790 - (b * fw + d * fh) / 2
    polygon = [(ox, oy), (ox + a * fw, oy + b * fw), (ox + a * fw + c * fh, oy + b * fw + d * fh), (ox + c * fh, oy + d * fh)]
    draw.polygon(polygon, fill='#91b76b', outline='#193d19')
    draw.ellipse((506, 784, 518, 796), fill='red')
    path = GUIDES / f'{item_id}.png'
    image.save(path)
    return str(path.relative_to(ROOT)).replace('\\', '/'), polygon

def make(position, age, kind):
    style, materials = AGES[age]
    label, footprint = BUILDINGS[kind]
    record = {
        'position': position,
        'id': f'{kind}-{age}',
        'kind': 'building',
        'mode': 'kingdom',
        'age': age,
        'aspect': '1:1',
        'prompt': COMMON + (
            f'ONE photoreal isolated {age} Age object, not a cartoon. ONE {age} Age {label}: {materials} '
            'No people, animals, labels or surrounding town. Aerial three-quarter view matching kingdom terrain. '
            'The green polygon is only the base footprint and the red dot is pivot 512,790. Replace the green with the object base. '
            'Remove every guide mark. Keep the object top above y80. Flat pure magenta #FF00FF backdrop, no floor and no shadow on the backdrop.'
        ),
        'styleReference': style,
        'requiredAlpha': True,
        'reviewStatus': 'UNVERIFIED',
        'attempt': 1,
        'requestedOutputs': 1,
        'reviewCriteria': 'Era, identity, camera, single object or modular wall sheet, no baked actors or HUD, measured pivot.',
    }
    guide, polygon = object_guide(record['id'], footprint)
    record['guide'] = guide
    record['registration'] = {
        'sourceSize': [1024, 1024], 'sourcePivot': [512, 790], 'footprintWorld': footprint,
        'groundPolygonSource': polygon, 'pivotTolerancePx': 12, 'status': 'PROPOSED_REQUIRES_PIXEL_REVIEW',
    }
    style_path = MOCKS / style
    if not style_path.exists():
        raise SystemExit(f'missing style {style_path}')
    record['styleReferenceSHA256'] = sha_file(style_path)
    record['promptSHA256'] = sha_bytes(record['prompt'].encode())
    record['guideSHA256'] = sha_file(ROOT / guide)
    if len(record['prompt'].encode()) > 8000:
        raise SystemExit('prompt too long ' + record['id'])
    return record

def main():
    carried = json.loads((PLAN / 'carried-buildings.json').read_text(encoding='utf-8'))['ids']
    order = [(item_id.rsplit('-', 1)[1], item_id.rsplit('-', 1)[0]) for item_id in carried]
    for age in ('bronze', 'iron'):
        for kind in BUILDINGS:
            order.append((age, kind))
    for kind in ('farm', 'lumber', 'quarry', 'mine', 'barracks', 'workshop', 'hall'):
        order.append(('medieval', kind))
    if len(order) != 30 or len({f'{k}-{a}' for a, k in order}) != 30:
        raise SystemExit(f'expected 30 unique buildings, got {len(order)}')
    items = [make(index, age, kind) for index, (age, kind) in enumerate(order, 1)]
    manifest = {
        'id': 'production-04-20261003',
        'model': 'gemini-3.1-flash-image',
        'project': 'project-eaa4c1cc-8f19-4d24-9e6',
        'region': 'global',
        'count': 30,
        'status': 'PREPARED_NOT_SUBMITTED',
        'items': items,
        'maxOutputTokens': 4096,
        'inputTokenUpperBoundPerRequest': 12000,
        'reservedUSD': 6,
        'carriedFirst': carried,
        'pricingSources': [
            'https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing',
            'https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/batch-inference',
            'https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/3-1-flash-image',
        ],
    }
    path = PLAN / 'batch-04-manifest.json'
    path.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print('Prepared production-04-20261003 with 30 building requests. No provider call.')

if __name__ == '__main__':
    main()
