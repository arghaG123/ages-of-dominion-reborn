"""Deterministic preparation of Batches 05, 06, 07, 08 for Ages of Dominion.
Strictly local: creates spatial guides, manifests, and registration metadata.
Zero provider calls.
"""
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / 'docs/plan/image-production'
MOCKS = ROOT / 'design-preview/generated/landscape-mocks-20261003-efcd7a7e/images'
GUIDES = PLAN / 'guides'
GUIDES.mkdir(parents=True, exist_ok=True)

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

CONTRACT = json.loads((ROOT / 'docs/plan/IMPLEMENTATION-CONTRACT.json').read_text(encoding='utf-8'))

AGE_STYLES = {
    'stone': ('03-kingdom-stone.jpg', 'timber, hide, thatch, flint and dirt. No medieval church, towers or steel.'),
    'bronze': ('04-kingdom-bronze.jpg', 'earth, plaster, early stone and bronze. No steel plate or later machinery.'),
    'iron': ('05-kingdom-iron.jpg', 'masonry, tiled roofs and iron. No gunpowder or modern concrete.'),
    'medieval': ('06-kingdom-medieval.jpg', 'coursed stone, timber, slate and terracotta. No firearms or factory yards.'),
    'gunpowder': ('07-kingdom-gunpowder.jpg', 'bastion stone, brick, period civic manor, powder stores, tile roofs. No medieval church, towers, or steel; no modern asphalt or concrete.'),
    'industrial': ('08-kingdom-industrial.jpg', 'red brick, cast iron beams, corrugated metal, slate roofs, pipes, factory yards. No modern plastics, glass curtain walls or future tech.'),
    'modern': ('09-kingdom-modern.jpg', 'reinforced concrete, structural steel, modern industrial cladding, utility piping, asphalt foundation. No sci-fi glow, anti-gravity or laser tech.'),
    'future': ('10-kingdom-future.jpg', 'advanced composite alloys, solar integration, sleek geometric architectural modules, clean power couplings. No crumbling masonry or medieval timber.'),
}

BUILDING_LABELS = {
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

def make_object_guide(item_id, footprint, mode='kingdom'):
    source = CONTRACT['geometry'][mode]['worldToSource']
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

def make_sheet_guide(item_id, slot_count=4):
    image = Image.new('RGB', (1024, 1024), '#ff00ff')
    draw = ImageDraw.Draw(image)
    slots = [
        [(80, 80), (480, 80), (480, 480), (80, 480)],
        [(544, 80), (944, 80), (944, 480), (544, 480)],
        [(80, 544), (480, 544), (480, 944), (80, 944)],
        [(544, 544), (944, 544), (944, 944), (544, 944)],
    ]
    for s in slots[:slot_count]:
        draw.polygon(s, fill='#91b76b', outline='#193d19')
    path = GUIDES / f'{item_id}.png'
    image.save(path)
    return str(path.relative_to(ROOT)).replace('\\', '/'), slots

def make_building_item(position, age, kind):
    style, materials = AGE_STYLES[age]
    label, footprint = BUILDING_LABELS[kind]
    item_id = f'{kind}-{age}'
    prompt = COMMON + (
        f'ONE photoreal isolated {age} Age object, not a cartoon. ONE {age} Age {label}: {materials} '
        'No people, animals, labels or surrounding town or village. Aerial three-quarter view matching kingdom terrain. '
        'The green polygon is only the base footprint and the red dot is pivot 512,790. Replace the green with the object base. '
        'Remove every guide mark. Keep the object top above y80. Flat pure magenta #FF00FF backdrop, no floor, no dirt apron, and no shadow on the backdrop.'
    )
    guide, polygon = make_object_guide(item_id, footprint, 'kingdom')
    record = {
        'position': position,
        'id': item_id,
        'kind': 'building',
        'mode': 'kingdom',
        'age': age,
        'aspect': '1:1',
        'prompt': prompt,
        'styleReference': style,
        'guide': guide,
        'requiredAlpha': True,
        'reviewStatus': 'UNVERIFIED',
        'attempt': 1,
        'requestedOutputs': 1,
        'reviewCriteria': 'Era, identity, camera, single object or modular wall sheet, no baked actors or HUD, measured pivot.',
        'registration': {
            'sourceSize': [1024, 1024], 'sourcePivot': [512, 790], 'footprintWorld': footprint,
            'groundPolygonSource': polygon, 'pivotTolerancePx': 12, 'status': 'PROPOSED_REQUIRES_PIXEL_REVIEW',
        }
    }
    style_path = MOCKS / style
    record['styleReferenceSHA256'] = sha_file(style_path)
    record['promptSHA256'] = sha_bytes(record['prompt'].encode())
    record['guideSHA256'] = sha_file(ROOT / guide)
    return record

def make_town_sheet_item(position, age, sheet_type):
    style, materials = AGE_STYLES[age]
    item_id = f'{sheet_type}-{age}'
    descriptions = {
        'world-props': f'4 to 6 substantial isolated ground and outskirts props for {age} Age: {materials}. Arranged in clean separated slots. NO overlapping pieces, NO connected town.',
        'construction': f'3 to 4 distinct construction pieces, timber or scaffold staging modules, and building framing for {age} Age: {materials}. Separated staging elements.',
        'civilian-transport': f'one worker pair in period clothing and one isolated local transport or cart assembly for {age} Age: {materials}. Cleanly separated subjects.',
    }
    desc = descriptions[sheet_type]
    prompt = COMMON + (
        f'ONE production prop sheet for Ages of Dominion. {age} Age {sheet_type} sheet: {desc} '
        'Each item is an isolated, individual asset placed inside the separated guide regions on a flat pure magenta #FF00FF background. '
        'NO overlapping items, NO connected buildings, NO surrounding town, village, or terrain scene. '
        'Short soft contact shadows under items, clean magenta gutters between items. Remove all green guide marks. '
        'Flat pure magenta #FF00FF backdrop, no floor texture.'
    )
    guide, slots = make_sheet_guide(item_id, 4)
    record = {
        'position': position,
        'id': item_id,
        'kind': 'sheet',
        'mode': 'kingdom',
        'age': age,
        'aspect': '1:1',
        'prompt': prompt,
        'styleReference': style,
        'guide': guide,
        'requiredAlpha': True,
        'reviewStatus': 'UNVERIFIED',
        'attempt': 1,
        'requestedOutputs': 1,
        'reviewCriteria': 'Era, identity, separated sheet elements, clean magenta margins, no full village scene.',
        'registration': {
            'sourceSize': [1024, 1024], 'status': 'SHEET_SOURCE_PROPOSED'
        }
    }
    style_path = MOCKS / style
    record['styleReferenceSHA256'] = sha_file(style_path)
    record['promptSHA256'] = sha_bytes(record['prompt'].encode())
    record['guideSHA256'] = sha_file(ROOT / guide)
    return record

TROOP_ROLES = {
    'stone': {
        'melee': 'primitive flint spearman in animal hide wrap and leather bands',
        'ranged': 'slingshot hunter with hide pouch and flint stones',
        'heavy': 'heavy club fighter with mammoth bone breastplate and thick hide shield',
    },
    'bronze': {
        'melee': 'bronze swordsman with bronze helmet, linen cuirass, and round bronze-rimmed shield',
        'ranged': 'composite bow archer in leather armor with bronze arrows and quiver',
        'heavy': 'heavy bronze spear phalanx warrior with large bronze aspis shield and greaves',
    },
    'iron': {
        'melee': 'iron legionary swordsman with segmented iron armor, crested helmet, and rectangular scutum shield',
        'ranged': 'heavy crossbowman with iron-reinforced crossbow and iron quarrel bolts',
        'heavy': 'armored cataphract vanguard with iron scale mail, iron face guard, and heavy iron spear',
    },
    'medieval': {
        'melee': 'man-at-arms foot soldier in chainmail with heater shield and steel arming sword',
        'ranged': 'yeoman longbowman in padded gambeson with yew longbow and arrows',
        'heavy': 'armored knight in full steel plate armor holding a two-handed poleaxe or greatsword',
    },
    'gunpowder': {
        'melee': 'line infantry soldier with flintlock musket with socket bayonet fixed and tricorn hat',
        'ranged': 'skirmisher rifleman with rifled carbine and powder horn in dark coat',
        'heavy': 'armored cuirassier grenadier with steel cuirass, heavy saber, and grenade satchel',
    },
    'industrial': {
        'melee': 'trench raider assault infantry in heavy greatcoat with trench club and bayonet',
        'ranged': 'marksman with bolt-action scoped service rifle and canvas ammo pouches',
        'heavy': 'heavy shock trooper with portable machine gun and steel brow plate helmet',
    },
    'modern': {
        'melee': 'point-man breaching specialist with tactical shotgun, ballistic shield, and combat vest',
        'ranged': 'assault infantry with modern tactical bullpup rifle, optic sight, and helmet comms',
        'heavy': 'heavy weapons specialist with squad automatic weapon, armored plate carrier, and combat rig',
    },
    'future': {
        'melee': 'exosuit kinetic shock infantry with energized carbon blade and magnetic forearm shield',
        'ranged': 'plasma railgun marksman with targeting visor and high-tech composite armor',
        'heavy': 'powered armor heavy assault juggernaut with micro-missile pod and shoulder railgun',
    },
}

def make_troop_item(position, age, role):
    style, materials = AGE_STYLES[age]
    desc = TROOP_ROLES[age][role]
    item_id = f'troop-{age}-{role}'
    prompt = COMMON + (
        f'ONE photoreal isolated {age} Age recruitable troop unit, not a cartoon. ONE full-body {role} soldier: {desc}. '
        f'Era materials: {materials} High aerial three-quarter view matching tactical board perspective. '
        'Standing grounded combat idle pose facing forward-right. The green polygon in the guide is the ground footprint and red dot is pivot 512,790. '
        'Replace green with grounded boots or feet. Remove all guide marks. NO background scene, NO other soldiers, NO text, NO UI. '
        'Flat pure magenta #FF00FF background, no floor, no cast shadow on background.'
    )
    guide, polygon = make_object_guide(item_id, [1.0, 1.0], 'tactical')
    record = {
        'position': position,
        'id': item_id,
        'kind': 'troop',
        'mode': 'tactical',
        'age': age,
        'aspect': '1:1',
        'prompt': prompt,
        'styleReference': '24-army.jpg',
        'guide': guide,
        'requiredAlpha': True,
        'reviewStatus': 'UNVERIFIED',
        'attempt': 1,
        'requestedOutputs': 1,
        'reviewCriteria': 'Era, role silhouette, tactical camera, grounded single soldier, clean magenta background.',
        'registration': {
            'sourceSize': [1024, 1024], 'sourcePivot': [512, 790], 'footprintWorld': [1.0, 1.0],
            'groundPolygonSource': polygon, 'pivotTolerancePx': 12, 'status': 'PROPOSED_REQUIRES_PIXEL_REVIEW',
        }
    }
    style_path = MOCKS / record['styleReference']
    record['styleReferenceSHA256'] = sha_file(style_path)
    record['promptSHA256'] = sha_bytes(record['prompt'].encode())
    record['guideSHA256'] = sha_file(ROOT / guide)
    return record

TOWER_FAMILIES = {
    'arrow': 'single-target fast projectile tower with elevated platform and firing slit',
    'splash': 'area-of-effect siege/catapult/mortar weapon tower with wide projectile cradle',
    'slow': 'crowd-control slowing trap tower deploying caltrops, sticky pitch, or cryogenic snares',
    'support': 'aura and buff tower providing tactical range and command signal beacon',
}

def make_tower_item(position, age, family):
    style, materials = AGE_STYLES[age]
    fam_desc = TOWER_FAMILIES[family]
    item_id = f'tower-{age}-{family}'
    prompt = COMMON + (
        f'ONE photoreal isolated {age} Age defense tower, not a cartoon. ONE {age} Age {family} tower: {fam_desc}. '
        f'Built from {materials} High aerial three-quarter view matching Defense mode valley. '
        'The green polygon in the guide is the 0.8x0.8 world footprint and red dot is pivot 512,790. '
        'Replace green with tower grounded foundation. Remove all guide marks. NO terrain scene, NO defenders, NO enemies, NO UI, NO labels. '
        'Flat pure magenta #FF00FF background, no floor and no shadow on background.'
    )
    guide, polygon = make_object_guide(item_id, [0.8, 0.8], 'defense')
    record = {
        'position': position,
        'id': item_id,
        'kind': 'tower',
        'mode': 'defense',
        'age': age,
        'aspect': '1:1',
        'prompt': prompt,
        'styleReference': '17-defense-preparation.jpg',
        'guide': guide,
        'requiredAlpha': True,
        'reviewStatus': 'UNVERIFIED',
        'attempt': 1,
        'requestedOutputs': 1,
        'reviewCriteria': 'Era, tower family identity, defense camera, single tower on 0.8 pad, clean magenta background.',
        'registration': {
            'sourceSize': [1024, 1024], 'sourcePivot': [512, 790], 'footprintWorld': [0.8, 0.8],
            'groundPolygonSource': polygon, 'pivotTolerancePx': 12, 'status': 'PROPOSED_REQUIRES_PIXEL_REVIEW',
        }
    }
    style_path = MOCKS / record['styleReference']
    record['styleReferenceSHA256'] = sha_file(style_path)
    record['promptSHA256'] = sha_bytes(record['prompt'].encode())
    record['guideSHA256'] = sha_file(ROOT / guide)
    return record

ATTACKER_DESCRIPTIONS = {
    'brute': 'massive hulking feral primitive warrior with spiked heavy tree branch club and thick hide pelt armor, heavy muscular charging stance',
    'runner': 'agile swift tribal raider with light flint daggers and feather/bone adornments, fast sprinting stance',
}

def make_attacker_item(position, age, role):
    style, materials = AGE_STYLES[age]
    desc = ATTACKER_DESCRIPTIONS[role]
    item_id = f'attacker-{age}-{role}'
    prompt = COMMON + (
        f'ONE photoreal isolated {age} Age wave {role} attacker for tower defense mode, not a cartoon. '
        f'ONE full-body enemy unit: {desc}. High aerial three-quarter view matching defense mode. '
        'The green polygon in the guide is the 1.0x1.0 unit ground footprint and red dot is pivot 512,790. '
        'Replace green with grounded feet. Remove all guide marks. NO terrain scene, NO defenders, NO path markers, NO UI. '
        'Flat pure magenta #FF00FF background, no floor and no shadow on backdrop.'
    )
    guide, polygon = make_object_guide(item_id, [1.0, 1.0], 'defense')
    record = {
        'position': position,
        'id': item_id,
        'kind': 'attacker',
        'mode': 'defense',
        'age': age,
        'aspect': '1:1',
        'prompt': prompt,
        'styleReference': '18-defense-wave.jpg',
        'guide': guide,
        'requiredAlpha': True,
        'reviewStatus': 'UNVERIFIED',
        'attempt': 1,
        'requestedOutputs': 1,
        'reviewCriteria': 'Era, attacker role silhouette, defense camera, grounded enemy unit, clean magenta background.',
        'registration': {
            'sourceSize': [1024, 1024], 'sourcePivot': [512, 790], 'footprintWorld': [1.0, 1.0],
            'groundPolygonSource': polygon, 'pivotTolerancePx': 12, 'status': 'PROPOSED_REQUIRES_PIXEL_REVIEW',
        }
    }
    style_path = MOCKS / record['styleReference']
    record['styleReferenceSHA256'] = sha_file(style_path)
    record['promptSHA256'] = sha_bytes(record['prompt'].encode())
    record['guideSHA256'] = sha_file(ROOT / guide)
    return record

def write_manifest(batch_index, items):
    manifest = {
        'id': f'production-{batch_index:02d}-20261003',
        'model': 'gemini-3.1-flash-image',
        'project': 'project-eaa4c1cc-8f19-4d24-9e6',
        'region': 'global',
        'count': len(items),
        'status': 'PREPARED_NOT_SUBMITTED',
        'items': items,
        'maxOutputTokens': 4096,
        'inputTokenUpperBoundPerRequest': 12000,
        'reservedUSD': 6,
        'pricingSources': [
            'https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing',
            'https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/batch-inference',
            'https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/3-1-flash-image',
        ],
    }
    path = PLAN / f'batch-{batch_index:02d}-manifest.json'
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f'Prepared {manifest["id"]} with {len(items)} items -> {path}')

def main():
    # Batch 05: 30 buildings
    b5_order = [
        ('medieval', 'armory'), ('medieval', 'walls'),
    ]
    for kind in ('farm', 'lumber', 'quarry', 'mine', 'barracks', 'workshop', 'hall', 'armory', 'walls'):
        b5_order.append(('gunpowder', kind))
    for kind in ('farm', 'lumber', 'quarry', 'mine', 'barracks', 'workshop', 'hall', 'armory', 'walls'):
        b5_order.append(('industrial', kind))
    for kind in ('farm', 'lumber', 'quarry', 'mine', 'barracks', 'workshop', 'hall', 'armory', 'walls'):
        b5_order.append(('modern', kind))
    b5_order.append(('future', 'farm'))
    assert len(b5_order) == 30
    b5_items = [make_building_item(i, age, kind) for i, (age, kind) in enumerate(b5_order, 1)]
    write_manifest(5, b5_items)

    # Batch 06: 8 Future buildings + 22 town sheets
    b6_items = []
    pos = 1
    for kind in ('lumber', 'quarry', 'mine', 'barracks', 'workshop', 'hall', 'armory', 'walls'):
        b6_items.append(make_building_item(pos, 'future', kind))
        pos += 1
    # 22 town sheets: stone through modern (21 sheets) + world-props-future (1 sheet)
    for age in ('stone', 'bronze', 'iron', 'medieval', 'gunpowder', 'industrial', 'modern'):
        for sheet_type in ('world-props', 'construction', 'civilian-transport'):
            b6_items.append(make_town_sheet_item(pos, age, sheet_type))
            pos += 1
    b6_items.append(make_town_sheet_item(pos, 'future', 'world-props'))
    assert len(b6_items) == 30
    write_manifest(6, b6_items)

    # Batch 07: 2 remaining town sheets + 24 troops + 4 towers (Stone)
    b7_items = []
    pos = 1
    b7_items.append(make_town_sheet_item(pos, 'future', 'construction')); pos += 1
    b7_items.append(make_town_sheet_item(pos, 'future', 'civilian-transport')); pos += 1
    for age in ('stone', 'bronze', 'iron', 'medieval', 'gunpowder', 'industrial', 'modern', 'future'):
        for role in ('melee', 'ranged', 'heavy'):
            b7_items.append(make_troop_item(pos, age, role))
            pos += 1
    for fam in ('arrow', 'splash', 'slow', 'support'):
        b7_items.append(make_tower_item(pos, 'stone', fam))
        pos += 1
    assert len(b7_items) == 30
    write_manifest(7, b7_items)

    # Batch 08: 28 towers + 2 attackers
    b8_items = []
    pos = 1
    for age in ('bronze', 'iron', 'medieval', 'gunpowder', 'industrial', 'modern', 'future'):
        for fam in ('arrow', 'splash', 'slow', 'support'):
            b8_items.append(make_tower_item(pos, age, fam))
            pos += 1
    b8_items.append(make_attacker_item(pos, 'stone', 'brute')); pos += 1
    b8_items.append(make_attacker_item(pos, 'stone', 'runner')); pos += 1
    assert len(b8_items) == 30
    write_manifest(8, b8_items)

    print('All four manifests 05-08 prepared successfully. Total items: 120.')

if __name__ == '__main__':
    main()
