"""Build the batch 03 manifest: five revised replacements plus useful new positions. No provider call."""
import hashlib, json
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / 'docs/plan/image-production'
MOCKS = ROOT / 'design-preview/generated/landscape-mocks-20261003-efcd7a7e/images'
GUIDES = PLAN / 'guides'

def sha_bytes(data): return hashlib.sha256(data).hexdigest()
def sha_file(path): return sha_bytes(path.read_bytes())

COMMON = (
    'ONE production image for Ages of Dominion. Semi-realistic dense inhabited rendered strategy-game materials, '
    'warm upper-left daylight, short soft contact shadows, coherent camera, high aerial three-quarter elevation55 yaw15. '
    'NO text, HUD, buttons, labels, numbers, device frame, watermark, or invented names. '
    'The first image is an exact spatial guide. The second image is material finish only; do not copy its buildings or UI. '
    'A guide mark is a specification, not art to reproduce. Never shift the camera, river, or landmarks. '
)

FAIL = (
    'The previous purchase failed and must not be repeated. '
    'Inside every reserved pad there must be ZERO huts, houses, people, animals, logs, crates, stakes, fences, '
    'white outlines, or foundation lines. Pads are bare grass or earth only. '
    'Exactly one river crossing. No second bridge. No baked actors. '
)

def object_guide(item_id, footprint, mode):
    contract = json.loads((ROOT / 'docs/plan/IMPLEMENTATION-CONTRACT.json').read_text(encoding='utf-8'))
    source = contract['geometry'][mode]['worldToSource']
    iw = ih = 1024
    image = Image.new('RGB', (iw, ih), '#ff00ff')
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

def item(position, id, kind, prompt, aspect, style, guide, mode=None, age=None, alpha=False, attempt=1, footprint=None):
    record = {
        'position': position, 'id': id, 'kind': kind, 'mode': mode, 'age': age, 'aspect': aspect,
        'prompt': COMMON + prompt, 'styleReference': style, 'guide': guide, 'requiredAlpha': alpha,
        'reviewStatus': 'UNVERIFIED', 'attempt': attempt, 'requestedOutputs': 1,
        'reviewCriteria': 'Era, identity, camera, empty pads or single object, no baked actors or HUD, measured pivot where isolated.'
    }
    if footprint:
        guide_path, polygon = object_guide(id, footprint, mode)
        record['guide'] = guide_path
        record['registration'] = {
            'sourceSize': [1024, 1024], 'sourcePivot': [512, 790], 'footprintWorld': footprint,
            'groundPolygonSource': polygon, 'pivotTolerancePx': 12, 'status': 'PROPOSED_REQUIRES_PIXEL_REVIEW'
        }
        record['prompt'] += ' The green polygon is only the base footprint and the red dot is pivot 512,790. Replace the green with the object base. Remove every guide mark. Keep the object top above y80. Flat pure magenta #FF00FF backdrop, no floor and no shadow on the backdrop.'
    style_path = MOCKS / record['styleReference']
    if not style_path.exists(): raise SystemExit(f'missing style {style_path}')
    if record['guide'] and not (ROOT / record['guide']).exists(): raise SystemExit(f'missing guide {record["guide"]}')
    record['styleReferenceSHA256'] = sha_file(style_path)
    record['promptSHA256'] = sha_bytes(record['prompt'].encode())
    record['guideSHA256'] = sha_file(ROOT / record['guide']) if record['guide'] else None
    if len(record['prompt'].encode()) > 8000: raise SystemExit(f'prompt too long {id}')
    return record

biomes = [
    ('plains', 'open grass valley, soft fields outside the pads'),
    ('hills', 'rocky highland grass, ridges outside the pads'),
    ('swamp', 'wet reeds and dark pools only outside the pads'),
    ('desert', 'sand and dry scrub, no oasis buildings'),
    ('snow', 'snow field and evergreens outside the pads'),
    ('waste', 'ash and broken ground, no modern debris on pads'),
    ('ruins', 'fallen masonry only outside the pads, pads themselves bare'),
]
modes = {
    'adventure': ('11-adventure-overview.jpg', 'docs/plan/image-production/guides/adventure.png', 'Adventure valley. Keep the six clearings, four pickup pads, two guard pads, western stone crossing, and connected roads empty.'),
    'tactical': ('14-tactical-deployment.jpg', 'docs/plan/image-production/guides/tactical.png', 'Tactical arena. Two stone decks stay on lanes 3 and 7. Banks, approaches, and deployment ground stay empty. No soldiers.'),
    'defense': ('17-defense-preparation.jpg', 'docs/plan/image-production/guides/defense.png', 'Defense valley. The winding lane and eight tower pads stay empty. No towers, army, or attackers.'),
}
buildings = [
    ('farm-stone', 'ONE Stone Age farm plot object: timber and thatch, no animals or people'),
    ('lumber-stone', 'ONE Stone Age lumber camp object: timber yard and axe rack, no people'),
    ('quarry-stone', 'ONE Stone Age quarry works object: flint face and timber crane, no people'),
    ('mine-stone', 'ONE Stone Age gold working object: shallow timber pit, no coins as text and no people'),
]

items = []
items.append(item(1, 'kingdom-terrain-stone', 'terrain', FAIL + 'Bare Stone Age kingdom terrain. Outskirts may use timber, hide, thatch, flint, and dirt only. No medieval church, towers, or steel. Nine upper and eight lower empty pads plus the empty town-hall terrace. Right river, one lower crossing, road spine and gate opening preserved.', '16:9', '03-kingdom-stone.jpg', 'docs/plan/image-production/guides/kingdom.png', 'kingdom', 'stone', False, 2))
items.append(item(2, 'kingdom-terrain-medieval', 'terrain', FAIL + 'Bare Medieval kingdom terrain. Outskirts may use coursed stone, timber, slate, and terracotta. The central pads and town-hall terrace stay empty. Right river, one lower crossing only.', '16:9', '06-kingdom-medieval.jpg', 'docs/plan/image-production/guides/kingdom.png', 'kingdom', 'medieval', False, 2))
items.append(item(3, 'townhall-stone', 'building', 'REVISION. The previous hall was a cartoon and cannot be repeated. ONE photoreal Stone Age civic hall: timber, hide, thatch, and flint. High aerial three-quarter camera. South entrance. One object only. No cartoon outline.', '1:1', '03-kingdom-stone.jpg', None, 'kingdom', 'stone', True, 2, [3, 1.5]))
items.append(item(4, 'skill-offense', 'skill', 'REVISION. The previous plaque was rotated into a diamond. ONE axis-aligned square plaque, edges parallel to the image, crossed melee blades only. Thin material rim. Flat pure magenta #FF00FF. No ground and no cast shadow.', '1:1', '30-icon-material-board.jpg', None, None, None, True, 2))
items.append(item(5, 'gear-stone-weapon', 'gear', 'REVISION. The previous image drew two crossed clubs. Draw ONE flint club only: one stone head and one wooden handle. Stone Age hide binding. No second weapon. Flat pure magenta #FF00FF. No floor.', '1:1', '22-forge.jpg', None, None, None, True, 2))
# Skill and weapon have no footprint guide. Give them a plain square key guide so the model has a shape target.
for record, label in ((items[3], 'SQUARE'), (items[4], 'CLUB')):
    path = GUIDES / f'{record["id"]}.png'
    image = Image.new('RGB', (1024, 1024), '#ff00ff')
    draw = ImageDraw.Draw(image)
    if label == 'SQUARE':
        draw.rectangle((160, 160, 864, 864), outline='#193d19', width=8)
    else:
        draw.line((280, 760, 760, 260), fill='#193d19', width=28)
    image.save(path)
    record['guide'] = str(path.relative_to(ROOT)).replace('\\', '/')
    record['guideSHA256'] = sha_file(path)
    record['prompt'] += ' Follow the guide shape and then remove every guide mark.'
    record['promptSHA256'] = sha_bytes(record['prompt'].encode())

position = 6
for mode, (style, guide, geography) in modes.items():
    for biome, material in biomes:
        items.append(item(position, f'{mode}-terrain-{biome}', 'terrain', FAIL + geography + f' Biome is {biome}: {material}. Same registered camera as the guide.', '16:9', style, guide, mode, None, False, 1))
        position += 1
for id, prompt in buildings:
    items.append(item(position, id, 'building', 'ONE photoreal isolated Stone Age object, not a cartoon. ' + prompt + '. Aerial three-quarter view matching kingdom terrain.', '1:1', '03-kingdom-stone.jpg', None, 'kingdom', 'stone', True, 1, [1.4, 1.2]))
    position += 1

assert len(items) == 30 and len({i['id'] for i in items}) == 30
manifest = {
    'id': 'production-03-20261003', 'model': 'gemini-3.1-flash-image', 'project': 'project-eaa4c1cc-8f19-4d24-9e6',
    'region': 'global', 'count': 30, 'status': 'PREPARED_NOT_SUBMITTED', 'items': items,
    'maxOutputTokens': 4096, 'inputTokenUpperBoundPerRequest': 12000, 'reservedUSD': 6,
    'replacements': ['kingdom-terrain-stone', 'kingdom-terrain-medieval', 'townhall-stone', 'skill-offense', 'gear-stone-weapon'],
    'carriedToNextBuildingBatch': ['barracks-stone', 'workshop-stone', 'hall-stone', 'armory-stone', 'walls-stone'],
    'cause': 'Batch 01 terrains baked structures into pads. Stone hall was cartoon. Offense plaque was rotated. Stone weapon showed two clubs. Prompts now forbid those results. Biome terrains use the corrected empty-pad rule.',
    'pricingSources': ['https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing']
}
(PLAN / 'batch-03-manifest.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
carried = PLAN / 'carried-buildings.json'
carried.write_text(json.dumps({'fromBatch': 3, 'ids': manifest['carriedToNextBuildingBatch'], 'reason': 'Five correction slots used this batch. These identities remain unbought and must be purchased before new building identities.'}, indent=2) + '\n', encoding='utf-8')
print('prepared', len(items), 'replacements', len(manifest['replacements']))
