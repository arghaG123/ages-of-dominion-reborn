"""Deterministic preparation of Batches 10, 11, 12, 13 for Ages of Dominion.
Creates spatial guides, manifests with exact SHA256 hashes and pricing configs,
and updates the budget ledger with reconciled historical exposure.
Zero paid provider calls.
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

PROJECT = 'project-eaa4c1cc-8f19-4d24-9e6'
CONTRACT = json.loads((ROOT / 'docs/plan/IMPLEMENTATION-CONTRACT.json').read_text(encoding='utf-8'))

def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())

COMMON = (
    'ONE production image for Ages of Dominion. Semi-realistic dense inhabited rendered strategy-game materials, '
    'warm upper-left daylight, short soft contact shadows, coherent camera, high aerial three-quarter elevation55 yaw15. '
    'NO text, HUD, buttons, labels, numbers, device frame, watermark, or invented names. '
    'The first image is an exact spatial guide. The second image is material finish only; do not copy its buildings or UI. '
    'A guide mark is a specification, not art to reproduce. Never shift the camera, river, or landmarks. '
)

PORTRAIT_COMMON = (
    'ONE production image for Ages of Dominion. Semi-realistic dense rendered strategy-game materials, '
    'warm upper-left daylight, short soft contact shadows. '
    'NO text, HUD, buttons, labels, numbers, device frame, watermark, or invented names. '
    'High-resolution character identity painting, grounded standing combat idle, plain magenta #FF00FF backdrop. '
    'No floor, no cast shadow on background. '
)

PROP_COMMON = (
    'ONE production image for Ages of Dominion. Semi-realistic dense rendered strategy-game materials, '
    'warm upper-left daylight, short soft contact shadows. '
    'NO text, HUD, buttons, labels, numbers, device frame, watermark, or invented names. '
    'Isolated object on pure magenta #FF00FF background. No floor, no background shadow. '
)

def make_object_guide(item_id, footprint, mode='tactical'):
    source = CONTRACT['geometry'][mode]['worldToSource']
    image = Image.new('RGB', (1024, 1024), '#ff00ff')
    draw = ImageDraw.Draw(image)
    fw, fh = footprint
    unit = 170 / max(fw, fh)
    a, b, c, d = [v * unit / source[0] for v in source[:4]]
    ox, oy = 512 - (a * fw + c * fh) / 2, 790 - (b * fw + d * fh) / 2
    polygon = [
        (ox, oy),
        (ox + a * fw, oy + b * fw),
        (ox + a * fw + c * fh, oy + b * fw + d * fh),
        (ox + c * fh, oy + d * fh),
    ]
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

def write_manifest(batch_index, items):
    manifest = {
        'id': f'production-{batch_index:02d}-20261003',
        'model': 'gemini-3.1-flash-image',
        'project': PROJECT,
        'region': 'global',
        'count': len(items),
        'status': 'PREPARED_READY_FOR_SUBMISSION',
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
    print(f'Wrote batch-{batch_index:02d}-manifest.json with {len(items)} items.')
    return manifest

# ----------------- BATCH 10 -----------------
def prepare_batch_10():
    items = []
    style_defense = '18-defense-wave.jpg'
    style_defense_sha = sha_file(MOCKS / style_defense)
    style_army = '24-army.jpg'
    style_army_sha = sha_file(MOCKS / style_army)
    style_hero = '19-hero-equipment.jpg'
    style_hero_sha = sha_file(MOCKS / style_hero)
    
    # 1. 8 Attackers
    attackers = [
        ('modern', 'archer', 'ghillie-suit military sniper with heavy anti-material rifle and bipod'),
        ('modern', 'sapper', 'military demolition expert in combat gear carrying C4 plastic explosives and shaped charges'),
        ('modern', 'shaman', 'electronic warfare specialist with tactical field uplink backpack and target designator'),
        ('future', 'brute', 'cybernetic heavy cyborg combatant with heavy ceramic-titanium armor plates and power fist'),
        ('future', 'runner', 'holographic stealth infiltrator in optical camo suit with monomolecular blades'),
        ('future', 'archer', 'advanced heavy railgun marksman with holographic HUD visor and shoulder stabilizer'),
        ('future', 'sapper', 'combat nanite saboteur with plasma cutting torch and quantum shaped-charge breacher'),
        ('future', 'shaman', 'psionic cyber-weaver with glowing neural cranial implants and energy focus glove'),
    ]
    for age, role, desc in attackers:
        item_id = f'attacker-{age}-{role}'
        prompt = COMMON + (
            f'ONE photoreal isolated {age} Age wave {role} attacker for tower defense mode, not a cartoon. '
            f'ONE full-body enemy unit: {desc}. High aerial three-quarter view matching defense mode. '
            'The green polygon in the guide is the 1.0x1.0 unit ground footprint and red dot is pivot 512,790. '
            'Replace green with grounded boots or feet. Remove all guide marks. NO terrain scene, NO defenders, NO path markers, NO UI. '
            'Flat pure magenta #FF00FF background, no floor and no shadow on backdrop.'
        )
        guide_rel, poly = make_object_guide(item_id, [1.0, 1.0], 'defense')
        items.append({
            'position': len(items) + 1, 'id': item_id, 'kind': 'attacker', 'mode': 'defense', 'age': age,
            'aspect': '1:1', 'prompt': prompt, 'styleReference': style_defense, 'guide': guide_rel,
            'requiredAlpha': True, 'reviewStatus': 'UNVERIFIED', 'attempt': 1, 'requestedOutputs': 1,
            'reviewCriteria': f'{age.capitalize()} era, attacker {role} silhouette, defense camera, grounded enemy unit, clean magenta background.',
            'registration': {'sourceSize': [1024, 1024], 'sourcePivot': [512, 790], 'footprintWorld': [1.0, 1.0], 'groundPolygonSource': poly, 'pivotTolerancePx': 12, 'status': 'PROPOSED_REQUIRES_PIXEL_REVIEW'},
            'styleReferenceSHA256': style_defense_sha, 'promptSHA256': sha_bytes(prompt.encode('utf-8')), 'guideSHA256': sha_file(ROOT / guide_rel)
        })
        
    # 2. 8 Neutral Creatures
    creatures = [
        ('wolf', 'Dire Wolf', 'snarling predatory gray wolf beast with thick coarse fur, bared fangs, low charging stance', [1.0, 1.0]),
        ('bandit', 'Bandit', 'roguish woodland highwayman outlaw in ragged leather jerkin and hood, holding shortbow and dagger', [1.0, 1.0]),
        ('bear', 'Cave Bear', 'massive ferocious brown cave bear rearing up on hind legs with deadly razor claws and thick hide', [1.2, 1.2]),
        ('harpy', 'Harpy', 'monstrous feathered winged creature with woman torso and sharp raptor talons, outstretched wings', [1.0, 1.0]),
        ('golem', 'Stone Golem', 'towering ancient animated stone monolith constructed from carved mossy boulders with runic cracks', [1.4, 1.4]),
        ('griffin', 'Griffin', 'majestic winged mythological beast with eagle head and foreclaws, feathered wings, and golden lion body', [1.2, 1.2]),
        ('wyvern', 'Wyvern', 'two-legged draconic reptilian flyer with leathery bat wings, horned head, and venomous barbed tail', [1.3, 1.3]),
        ('drone', 'Drone Swarm', 'trio of hovering tactical military surveillance and assault quadcopters with sensor pods and thruster glow', [1.0, 1.0]),
    ]
    for cid, name, desc, fp in creatures:
        item_id = f'creature-{cid}'
        prompt = COMMON + (
            f'ONE photoreal isolated neutral creature unit for Ages of Dominion, not a cartoon. ONE full-body {name}: {desc}. '
            'High aerial three-quarter view matching tactical board perspective. '
            'The green polygon in the guide is the ground footprint and red dot is pivot 512,790. '
            'Replace green with grounded feet or shadow contact. Remove all guide marks. NO background scene, NO other units, NO text, NO UI. '
            'Flat pure magenta #FF00FF background, no floor, no cast shadow on background.'
        )
        guide_rel, poly = make_object_guide(item_id, fp, 'tactical')
        items.append({
            'position': len(items) + 1, 'id': item_id, 'kind': 'creature', 'mode': 'tactical', 'age': 'neutral',
            'aspect': '1:1', 'prompt': prompt, 'styleReference': style_army, 'guide': guide_rel,
            'requiredAlpha': True, 'reviewStatus': 'UNVERIFIED', 'attempt': 1, 'requestedOutputs': 1,
            'reviewCriteria': f'Creature {name} identity, tactical camera, grounded neutral unit, clean magenta background.',
            'registration': {'sourceSize': [1024, 1024], 'sourcePivot': [512, 790], 'footprintWorld': fp, 'groundPolygonSource': poly, 'pivotTolerancePx': 12, 'status': 'PROPOSED_REQUIRES_PIXEL_REVIEW'},
            'styleReferenceSHA256': style_army_sha, 'promptSHA256': sha_bytes(prompt.encode('utf-8')), 'guideSHA256': sha_file(ROOT / guide_rel)
        })

    # 3. 14 Hero Paintings (8 Medieval + 6 Gunpowder)
    heroes = [
        ('medieval', 'knight', 'chivalric feudal knight in ornate steel harness with heraldic surcoat and longsword'),
        ('medieval', 'ranger', 'woodland master archer in forest leather with longbow and hunting falchion'),
        ('medieval', 'warlock', 'dark occult invoker in embroidered velvet robes with grimoire and scythe'),
        ('medieval', 'mage', 'arcane scholar in high-collared azure vestments with glowing runic staff'),
        ('medieval', 'paladin', 'holy crusader in engraved silvered plate with warhammer and reliquary'),
        ('medieval', 'barbarian', 'highlander chieftain in tartan and studded leather with two-handed claymore'),
        ('medieval', 'necromancer', 'crypt lord in bone-trimmed cowl with obsidian athame and spirit chalice'),
        ('medieval', 'healer', 'monastic warden in simple robes with herbal satchel, sacred bell, and quarterstaff'),
        ('powder', 'knight', 'heavy cavalry dragoon commander in steel breastplate, sash, and cavalry saber'),
        ('powder', 'ranger', 'frontiersman scout in buckskin coat with scoped rifled musket and hunting knife'),
        ('powder', 'warlock', 'esoteric alchemist in dark frock coat with brass astrolabe and fulminate vials'),
        ('powder', 'mage', 'voltaic sage in brass-riveted leather coat with electrostatic Leyden wand'),
        ('powder', 'paladin', 'inquisitor captain in morion helm, steel cuirass, and wheel-lock pistol with rapier'),
        ('powder', 'barbarian', 'naval privateer captain in ruffled shirt and sash with boarding axe and flintlock'),
    ]
    for era, cls, desc in heroes:
        item_id = f'portrait-{era}-{cls}'
        prompt = PORTRAIT_COMMON + (
            f'ONE {era} era full-body {cls} hero identity portrait for Ages of Dominion. {desc}. '
            'Distinct class silhouette, era-accurate clothing and implements; recognizable consistent human face, no names, no stats, no HUD. '
            'Plain magenta #FF00FF backdrop.'
        )
        items.append({
            'position': len(items) + 1, 'id': item_id, 'kind': 'portrait', 'mode': None, 'age': era,
            'aspect': '1:1', 'prompt': prompt, 'styleReference': style_hero, 'guide': None,
            'requiredAlpha': True, 'reviewStatus': 'UNVERIFIED', 'attempt': 1, 'requestedOutputs': 1,
            'reviewCriteria': f'{era.capitalize()} era, hero {cls} identity, full-body portrait, clean magenta background.',
            'styleReferenceSHA256': style_hero_sha, 'promptSHA256': sha_bytes(prompt.encode('utf-8')), 'guideSHA256': None
        })
        
    return write_manifest(10, items)

# ----------------- BATCH 11 -----------------
def prepare_batch_11():
    items = []
    style_hero = '19-hero-equipment.jpg'
    style_hero_sha = sha_file(MOCKS / style_hero)
    style_adv = '11-adventure-overview.jpg'
    style_adv_sha = sha_file(MOCKS / style_adv)
    style_forge = '22-forge.jpg'
    style_forge_sha = sha_file(MOCKS / style_forge)
    style_army = '24-army.jpg'
    style_army_sha = sha_file(MOCKS / style_army)
    style_home = '01-home.jpg'
    style_home_sha = sha_file(MOCKS / style_home)
    
    # 1. 10 Hero Portraits (2 Gunpowder + 8 Mech/Modern)
    heroes = [
        ('powder', 'necromancer', 'plague anatomist in raven mask with surgical saw and embalming salts'),
        ('powder', 'healer', 'field surgeon in apothecary coat with medical bag and soothing poultice'),
        ('mech', 'knight', 'special forces tactical breacher in modern body armor with assault carbine'),
        ('mech', 'ranger', 'military recon scout in digital camo with thermal-scoped sniper rifle'),
        ('mech', 'warlock', 'black-hat cyber warfare operator with tactical tablet and EMP device'),
        ('mech', 'mage', 'quantum physicist in hazard exosuit with localized particle emitter'),
        ('mech', 'paladin', 'combat paramedic warden with ballistic shield and defibrillator trauma kit'),
        ('mech', 'barbarian', 'mechanized riot berserker with powered exoskeleton and shock hammer'),
        ('mech', 'necromancer', 'bio-hazard nanite plague specialist with hazmat injector harness'),
        ('mech', 'healer', 'combat field doctor with trauma nano-spray and biometric monitor'),
    ]
    for era, cls, desc in heroes:
        item_id = f'portrait-{era}-{cls}'
        prompt = PORTRAIT_COMMON + (
            f'ONE {era} era full-body {cls} hero identity portrait for Ages of Dominion. {desc}. '
            'Distinct class silhouette, era-accurate clothing and implements; recognizable consistent human face, no names, no stats, no HUD. '
            'Plain magenta #FF00FF backdrop.'
        )
        items.append({
            'position': len(items) + 1, 'id': item_id, 'kind': 'portrait', 'mode': None, 'age': era,
            'aspect': '1:1', 'prompt': prompt, 'styleReference': style_hero, 'guide': None,
            'requiredAlpha': True, 'reviewStatus': 'UNVERIFIED', 'attempt': 1, 'requestedOutputs': 1,
            'reviewCriteria': f'{era.capitalize()} era, hero {cls} identity, full-body portrait, clean magenta background.',
            'styleReferenceSHA256': style_hero_sha, 'promptSHA256': sha_bytes(prompt.encode('utf-8')), 'guideSHA256': None
        })

    # 2. 6 Adventure Sites
    sites = [
        ('treasure', 'Treasure Cache', 'ancient stone treasure chest overflowing with gold relics and gemstones embedded in carved masonry', [1.4, 1.2]),
        ('rest', 'Rest Shelter', 'peaceful adventurer wayside campsite with stone hearth fire, canvas lean-to shelter, and water barrel', [1.4, 1.2]),
        ('exit', 'Region Boundary Arch', 'ancient monumental carved stone archway boundary portal framing the pass to distant lands', [1.5, 1.2]),
        ('rival', 'Rival Forward Camp', 'fortified frontier military pavilion with heraldic war banner standard and weapon racks', [1.5, 1.2]),
        ('human', 'Woodland Dwelling', 'secluded thatched woodland cottage hermitage with stone chimney, wooden fence, and herb garden', [1.5, 1.2]),
        ('guard', 'Watchtower Outpost', 'fortified stone checkpoint tower with heavy timber palisade gate and arrow slits', [1.4, 1.4]),
    ]
    for sid, name, desc, fp in sites:
        item_id = f'site-{sid}'
        prompt = COMMON + (
            f'ONE photoreal isolated adventure site structure for Ages of Dominion, not a cartoon. ONE {name}: {desc}. '
            'High aerial three-quarter view matching adventure mode perspective. '
            'The green polygon in the guide is the ground footprint and red dot is pivot 512,790. '
            'Replace green with grounded foundation. Remove all guide marks. NO surrounding village, NO text, NO UI. '
            'Flat pure magenta #FF00FF background, no floor, no cast shadow on backdrop.'
        )
        guide_rel, poly = make_object_guide(item_id, fp, 'adventure')
        items.append({
            'position': len(items) + 1, 'id': item_id, 'kind': 'site', 'mode': 'adventure', 'age': 'all',
            'aspect': '1:1', 'prompt': prompt, 'styleReference': style_adv, 'guide': guide_rel,
            'requiredAlpha': True, 'reviewStatus': 'UNVERIFIED', 'attempt': 1, 'requestedOutputs': 1,
            'reviewCriteria': f'Site {name} identity, adventure camera, grounded structure, clean magenta background.',
            'registration': {'sourceSize': [1024, 1024], 'sourcePivot': [512, 790], 'footprintWorld': fp, 'groundPolygonSource': poly, 'pivotTolerancePx': 12, 'status': 'PROPOSED_REQUIRES_PIXEL_REVIEW'},
            'styleReferenceSHA256': style_adv_sha, 'promptSHA256': sha_bytes(prompt.encode('utf-8')), 'guideSHA256': sha_file(ROOT / guide_rel)
        })

    # 3. 10 Artifacts
    artifacts = [
        ('chalice', 'Holy Chalice of Restoration', 'ornate golden jewel-encrusted ceremonial goblet with embossed filigree vines and polished ruby gemstones'),
        ('orb', 'Dragonfire Orb', 'swirling mystical crimson glass sphere radiating inner dragonflame and ancient draconic runes'),
        ('crown', 'Crown of the Ancient King', 'radiant golden royal crown with nine spiked peaks set with emeralds and sapphires'),
        ('tome', 'Tome of Arcane Secrets', 'ancient heavy leather-bound grimoire with brass corner brackets and illuminated runic page edges'),
        ('banner', 'War Banner of Victory', 'flowing heraldic silk battle pennant on carved spear pole with gold-threaded lion crest'),
        ('horn', 'Horn of the North Wind', 'carved mammoth ivory war horn with engraved silver bands, mouthpiece, and leather strap'),
        ('mirror', 'Scrying Mirror of Truth', 'oval polished dark obsidian mirror held in ornate silver filigree vine frame'),
        ('compass', 'Wayfinder Lodestone', 'antique brass gimballed maritime magnetic compass with intricate etched star navigation dial'),
        ('ring', 'Signet Ring of Dominion', 'heavy gold signet ring engraved with royal seal and set with a deep blue star sapphire'),
        ('aegis', 'Aegis of the Sun God', 'radiant embossed golden sunburst shield with central divine sun face and protective runes'),
    ]
    for aid, name, desc in artifacts:
        item_id = f'artifact-{aid}'
        prompt = PROP_COMMON + (
            f'ONE high-detail photoreal artifact icon for Ages of Dominion strategy RPG. ONE {name}: {desc}. '
            'Centrally framed inventory item view, rich authentic materials, warm studio lighting. '
            'Pure flat magenta #FF00FF backdrop, no floor, no shadows.'
        )
        items.append({
            'position': len(items) + 1, 'id': item_id, 'kind': 'artifact', 'mode': None, 'age': 'all',
            'aspect': '1:1', 'prompt': prompt, 'styleReference': style_forge, 'guide': None,
            'requiredAlpha': True, 'reviewStatus': 'UNVERIFIED', 'attempt': 1, 'requestedOutputs': 1,
            'reviewCriteria': f'Artifact {name} identity, clean silhouette, rich materials, clean magenta background.',
            'styleReferenceSHA256': style_forge_sha, 'promptSHA256': sha_bytes(prompt.encode('utf-8')), 'guideSHA256': None
        })

    # 4. 3 Mount / Transport Masters
    mounts = [
        ('horse', 'Armored Destrier Horse', 'magnificent warhorse with leather saddle, bridle, stirrups, and decorative cloth barding, grounded standing idle', [1.4, 1.0]),
        ('motor', 'Industrial Steam Utility Vehicle', 'early industrial steam-powered utility truck vehicle with riveted boiler, iron frame, and spoked wheels', [1.5, 1.2]),
        ('future', 'Repulsor Sky-Speeder', 'sleek aerodynamic futuristic anti-gravity hovercraft transport with composite chassis and glowing repulsor thrusters', [1.5, 1.2]),
    ]
    for mid, name, desc, fp in mounts:
        item_id = f'mount-{mid}'
        prompt = COMMON + (
            f'ONE photoreal isolated transport master unit for Ages of Dominion, not a cartoon. ONE {name}: {desc}. '
            'High aerial three-quarter view matching game perspective. '
            'The green polygon in the guide is the ground footprint and red dot is pivot 512,790. '
            'Replace green with grounded wheels, hooves, or thruster pads. Remove all guide marks. NO riders, NO background scene, NO UI. '
            'Flat pure magenta #FF00FF background, no floor, no cast shadow on background.'
        )
        guide_rel, poly = make_object_guide(item_id, fp, 'tactical')
        items.append({
            'position': len(items) + 1, 'id': item_id, 'kind': 'mount', 'mode': 'tactical', 'age': 'all',
            'aspect': '1:1', 'prompt': prompt, 'styleReference': style_army, 'guide': guide_rel,
            'requiredAlpha': True, 'reviewStatus': 'UNVERIFIED', 'attempt': 1, 'requestedOutputs': 1,
            'reviewCriteria': f'Mount {name} master identity, aerial perspective, grounded transport unit, clean magenta background.',
            'registration': {'sourceSize': [1024, 1024], 'sourcePivot': [512, 790], 'footprintWorld': fp, 'groundPolygonSource': poly, 'pivotTolerancePx': 12, 'status': 'PROPOSED_REQUIRES_PIXEL_REVIEW'},
            'styleReferenceSHA256': style_army_sha, 'promptSHA256': sha_bytes(prompt.encode('utf-8')), 'guideSHA256': sha_file(ROOT / guide_rel)
        })

    # 5. 1 Title Background (16:9)
    item_id = 'supporting-title'
    prompt = (
        'ONE production title background artwork for Ages of Dominion strategy game. '
        'Breathtaking high-angle cinematic wide landscape panorama of the sacred valley homeland through history. '
        'Winding river, lush forested valley floor, terraced upper cliffs where an ancient fortress and civic settlement rise. '
        'Golden late-afternoon sunlight breaking through clouds, warm majestic atmosphere. '
        'NO text, NO logo, NO title, NO buttons, NO UI overlays, NO characters in foreground. Coherent realistic painterly style.'
    )
    items.append({
        'position': len(items) + 1, 'id': item_id, 'kind': 'supporting', 'mode': None, 'age': 'all',
        'aspect': '16:9', 'prompt': prompt, 'styleReference': style_home, 'guide': None,
        'requiredAlpha': False, 'reviewStatus': 'UNVERIFIED', 'attempt': 1, 'requestedOutputs': 1,
        'reviewCriteria': 'Cinematic title background panorama, warm lighting, no text or UI.',
        'styleReferenceSHA256': style_home_sha, 'promptSHA256': sha_bytes(prompt.encode('utf-8')), 'guideSHA256': None
    })
    
    return write_manifest(11, items)

# ----------------- BATCH 12 -----------------
def prepare_batch_12():
    items = []
    style_home = '01-home.jpg'
    style_home_sha = sha_file(MOCKS / style_home)
    style_hero = '19-hero-equipment.jpg'
    style_hero_sha = sha_file(MOCKS / style_hero)
    style_icon = '30-icon-material-board.jpg'
    style_icon_sha = sha_file(MOCKS / style_icon)
    style_army = '24-army.jpg'
    style_army_sha = sha_file(MOCKS / style_army)
    
    # 1. 8 Chapter Artworks (16:9)
    chapters = [
        (1, 'First Fire', 'Stone Age tribe gathered on valley hill at dusk, taming first fire with flint hearth, timber shelters, and starry sky'),
        (2, 'Metal and Debt', 'Bronze Age river harbor and marketplace with bronze smelters casting tools, clay tablets, and cargo boats'),
        (3, 'Iron Road', 'Iron Age stone highway cutting through wild valleys with marching iron legionaries and fortified watchposts'),
        (4, 'Crown and Keep', 'Medieval walled castle citadel with stone battlements, colorful heraldic pennants, and bustling town square'),
        (5, 'Powder and Consequence', 'Gunpowder Age bastion star-fortress shrouded in cannon smoke, artillery crews, and naval river warships'),
        (6, 'Smoke Over the Valley', 'Industrial Age boomtown with red brick factory chimneys, iron railway bridges, and steam locomotives'),
        (7, 'Modern Crown', 'Modern thriving metropolis with illuminated concrete spires, asphalt highway interchanges, and airport terminal'),
        (8, 'The Valley We Keep', 'Future utopian sustainable civilization with gleaming solar arcologies, green sky-gardens, and clean river valley'),
    ]
    for num, title, desc in chapters:
        item_id = f'supporting-chapter-{num}'
        prompt = (
            f'ONE production chapter story illustration for Ages of Dominion: Chapter {num} - {title}. {desc}. '
            'Cinematic wide landscape composition, rich historical atmosphere, evocative lighting. '
            'NO text, NO numbers, NO labels, NO UI frames, NO watermarks. 16:9 widescreen format.'
        )
        items.append({
            'position': len(items) + 1, 'id': item_id, 'kind': 'supporting', 'mode': None, 'age': num,
            'aspect': '16:9', 'prompt': prompt, 'styleReference': style_home, 'guide': None,
            'requiredAlpha': False, 'reviewStatus': 'UNVERIFIED', 'attempt': 1, 'requestedOutputs': 1,
            'reviewCriteria': f'Chapter {num} illustration, narrative storytelling, 16:9 format, no text.',
            'styleReferenceSHA256': style_home_sha, 'promptSHA256': sha_bytes(prompt.encode('utf-8')), 'guideSHA256': None
        })

    # 2. 6 Persistent Rivals
    rivals = [
        ('aldric', 'Lord Aldric the Steadfast', 'stern feudal rival baron in ornate damascened plate armor with fur mantle and heavy signet ring'),
        ('valeria', 'Lady Valeria the Cunning', 'calculating rival noblewoman diplomat in dark velvet gown embroidered with gold, holding a cipher letter'),
        ('corvus', 'Arch-Warlock Corvus', 'shadowy rival sorcerer in raven-feathered cowl with obsidian staff and glowing amethyst eyes'),
        ('theron', 'Commander Theron', 'scarred veteran rival warlord in battle-tested iron breastplate with heavy broadsword at hip'),
        ('morgana', 'Enchantress Morgana', 'mystical rival seeress in flowing silk robes with crystal pendulum and arcane celestial charts'),
        ('kane', 'Ironmaster Kane', 'ruthless industrial rival magnate in soot-stained wool coat with leather gloves and brass pocket watch'),
    ]
    for rid, name, desc in rivals:
        item_id = f'supporting-rival-{rid}'
        prompt = PORTRAIT_COMMON + (
            f'ONE persistent campaign rival portrait for Ages of Dominion. {name}: {desc}. '
            'Upper-body to full-body portrait, powerful commanding expression, era-appropriate attire. Plain magenta #FF00FF backdrop.'
        )
        items.append({
            'position': len(items) + 1, 'id': item_id, 'kind': 'supporting', 'mode': None, 'age': 'all',
            'aspect': '1:1', 'prompt': prompt, 'styleReference': style_hero, 'guide': None,
            'requiredAlpha': True, 'reviewStatus': 'UNVERIFIED', 'attempt': 1, 'requestedOutputs': 1,
            'reviewCriteria': f'Rival {name} identity, personality portrait, clean magenta background.',
            'styleReferenceSHA256': style_hero_sha, 'promptSHA256': sha_bytes(prompt.encode('utf-8')), 'guideSHA256': None
        })

    # 3. 1 UI Materials Sheet
    item_id = 'supporting-ui-materials'
    guide_rel, slots = make_sheet_guide(item_id, 4)
    prompt = PROP_COMMON + (
        'ONE UI design system material texture sheet for Ages of Dominion strategy game. '
        'Separated modular UI panel materials in four quadrants: '
        'Quadrant 1: dark hammered slate stone header bar with beveled rivets; '
        'Quadrant 2: burnished brass metallic frame border with engraved ornamental filigree; '
        'Quadrant 3: polished carved oak wooden button and parchment scroll backing; '
        'Quadrant 4: ornamental brass corner brackets and gem socket flourishes. '
        'Flat pure magenta #FF00FF background separating all quadrants cleanly, no labels, no text.'
    )
    items.append({
        'position': len(items) + 1, 'id': item_id, 'kind': 'supporting', 'mode': None, 'age': 'all',
        'aspect': '1:1', 'prompt': prompt, 'styleReference': style_icon, 'guide': guide_rel,
        'requiredAlpha': True, 'reviewStatus': 'UNVERIFIED', 'attempt': 1, 'requestedOutputs': 1,
        'reviewCriteria': 'UI material sheet, 4 distinct clean quadrants, rich game materials, clean magenta separators.',
        'styleReferenceSHA256': style_icon_sha, 'promptSHA256': sha_bytes(prompt.encode('utf-8')), 'guideSHA256': sha_file(ROOT / guide_rel)
    })

    # 4. 8 Class Rig Plates
    classes = ['knight', 'ranger', 'warlock', 'mage', 'paladin', 'barbarian', 'necromancer', 'healer']
    for cls in classes:
        item_id = f'rig-{cls}'
        guide_rel, slots = make_sheet_guide(item_id, 4)
        prompt = PROP_COMMON + (
            f'ONE separated joint articulation source plate for {cls} character animation rig in Ages of Dominion. '
            'Four cleanly separated anatomical component clusters arranged in quadrants: '
            'Quadrant 1: head and facial expression angles; '
            'Quadrant 2: torso, chest armor, and pelvis; '
            'Quadrant 3: upper arms, forearms, and posable hands holding primary weapon/implement; '
            'Quadrant 4: upper thighs, shins, and boots with foot ground contact pads. '
            'Clean flat pure magenta #FF00FF background between all separated body parts, no overlapping limbs, no text.'
        )
        items.append({
            'position': len(items) + 1, 'id': item_id, 'kind': 'rig-sheet', 'mode': None, 'age': 'all',
            'aspect': '1:1', 'prompt': prompt, 'styleReference': style_army, 'guide': guide_rel,
            'requiredAlpha': True, 'reviewStatus': 'UNVERIFIED', 'attempt': 1, 'requestedOutputs': 1,
            'reviewCriteria': f'Rig source plate for {cls}, 4 separated quadrants, clean joint parts, pure magenta background.',
            'styleReferenceSHA256': style_army_sha, 'promptSHA256': sha_bytes(prompt.encode('utf-8')), 'guideSHA256': sha_file(ROOT / guide_rel)
        })

    # 5. 7 Spell Effects
    effects = [
        ('arrow', 'Magic Arrow', 'magic missile projectile flight trails, energy arrowheads, and spark impact bursts'),
        ('bolt', 'Lightning Bolt', 'branching electrostatic lightning bolt arcs, electric discharge sparks, and ionized flash bursts'),
        ('bless', 'Holy Bless', 'golden celestial blessing radiance rays, halo sparkles, and shimmering divine aura particles'),
        ('haste', 'Wind Haste', 'swirling translucent wind gusts, speed blur streak lines, and feather-light motion trails'),
        ('curse', 'Shadow Curse', 'dark violet necrotic miasma smoke tendrils, skull-shaped spirit wisps, and corruption hexes'),
        ('cure', 'Restorative Cure', 'emerald botanical healing sparkles, soothing water droplet glints, and radiant leaf auras'),
        ('shield', 'Energy Shield', 'hexagonal translucent crystalline barrier shield plates and shimmering kinetic deflection flares'),
    ]
    for eid, name, desc in effects:
        item_id = f'effect-{eid}'
        guide_rel, slots = make_sheet_guide(item_id, 4)
        prompt = PROP_COMMON + (
            f'ONE visual effects sprite material sheet for Ages of Dominion spell casting: {name}. {desc}. '
            'Four cleanly separated particle and texture phases arranged in quadrants: start cast glow, traveling projectile, impact explosion, and residual ambient aura. '
            'Flat pure magenta #FF00FF backdrop separating all effect elements cleanly, no black clipping, no text.'
        )
        items.append({
            'position': len(items) + 1, 'id': item_id, 'kind': 'effect', 'mode': None, 'age': 'all',
            'aspect': '1:1', 'prompt': prompt, 'styleReference': style_icon, 'guide': guide_rel,
            'requiredAlpha': True, 'reviewStatus': 'UNVERIFIED', 'attempt': 1, 'requestedOutputs': 1,
            'reviewCriteria': f'Visual effect sheet for {name}, clean quadrant phases, rich particle textures, clean magenta background.',
            'styleReferenceSHA256': style_icon_sha, 'promptSHA256': sha_bytes(prompt.encode('utf-8')), 'guideSHA256': sha_file(ROOT / guide_rel)
        })

    return write_manifest(12, items)

# ----------------- BATCH 13 -----------------
def prepare_batch_13():
    items = []
    style_icon = '30-icon-material-board.jpg'
    style_icon_sha = sha_file(MOCKS / style_icon)
    style_forge = '22-forge.jpg'
    style_forge_sha = sha_file(MOCKS / style_forge)
    
    # 1. 3 Remaining Spell/Combat Effects
    effects = [
        ('resurrect', 'Divine Resurrection', 'golden divine ankh emblem, rising phoenix soul embers, and sacred pillar of light aura'),
        ('projectile', 'Ballistic Projectiles', 'flying flaming catapult boulder, cast iron cannonball, smoking mortar shell, and missile plume'),
        ('impact', 'Combat Impacts', 'ground explosion blast crater, flying stone rubble debris, dust shockwave, and fiery sparks'),
    ]
    for eid, name, desc in effects:
        item_id = f'effect-{eid}'
        guide_rel, slots = make_sheet_guide(item_id, 4)
        prompt = PROP_COMMON + (
            f'ONE combat effects sprite sheet for Ages of Dominion: {name}. {desc}. '
            'Four cleanly separated texture quadrants for game animation. Pure flat magenta #FF00FF backdrop, no text.'
        )
        items.append({
            'position': len(items) + 1, 'id': item_id, 'kind': 'effect', 'mode': None, 'age': 'all',
            'aspect': '1:1', 'prompt': prompt, 'styleReference': style_icon, 'guide': guide_rel,
            'requiredAlpha': True, 'reviewStatus': 'UNVERIFIED', 'attempt': 1, 'requestedOutputs': 1,
            'reviewCriteria': f'Combat effect sheet for {name}, 4 clean quadrants, pure magenta background.',
            'styleReferenceSHA256': style_icon_sha, 'promptSHA256': sha_bytes(prompt.encode('utf-8')), 'guideSHA256': sha_file(ROOT / guide_rel)
        })

    # 2. 27 Core Canonical Equipment Items (Bronze to Industrial)
    gear = [
        # Bronze (6)
        ('bronze', 'weapon', 'Bronze Sword', 'leaf-bladed cast bronze broadsword with leather-wrapped grip and bronze pommel'),
        ('bronze', 'armor', 'Bronze Cuirass', 'muscled cast bronze breastplate with engraved pectoral lines and leather shoulder straps'),
        ('bronze', 'helm', 'Bronze Helm', 'corinthian-style cast bronze helmet with cheek guards and horsehair crest mount'),
        ('bronze', 'boots', 'Leather Sandals', 'heavy studded calf-high leather marching sandals with bronze buckles and greaves'),
        ('bronze', 'offhand', 'Bronze Aspis', 'circular bronze-faced concave wooden shield with embossed sun medallion boss'),
        ('bronze', 'accessory', 'Bronze Torc', 'heavy twisted bronze neck torc with sculpted lion head terminals'),
        # Iron (6)
        ('iron', 'weapon', 'Iron Gladius', 'double-edged iron thrusting gladius with carved bone hilt and spherical brass pommel'),
        ('iron', 'armor', 'Iron Lorica', 'segmented iron plate lorica segmentata armor with brass hinges and tie rings'),
        ('iron', 'helm', 'Iron Sallet', 'close-fitting iron sallet war helm with articulated neck lobster tail and eye slit'),
        ('iron', 'boots', 'Studded Caligae', 'iron-hobnailed military march caligae boots with reinforced rawhide straps'),
        ('iron', 'offhand', 'Iron Scutum', 'tall curved rectangular wooden legionary scutum shield with heavy iron central boss'),
        ('iron', 'accessory', 'Iron Signet', 'solid forged iron signet ring set with carved red carnelian war eagle intaglio'),
        # Medieval (6)
        ('medieval', 'weapon', 'Knight Longsword', 'tempered steel cruciform two-handed longsword with wire-bound grip and wheel pommel'),
        ('medieval', 'armor', 'Plate Harness', 'mirror-polished articulated steel plate harness with fluted cuirass and faulds'),
        ('medieval', 'helm', 'Great Helm', 'cylindrical steel knight great helm with brass cross reinforcement and ventilation holes'),
        ('medieval', 'boots', 'Steel Sabatons', 'articulated steel plate sabaton foot armor over soft calfskin riding boots'),
        ('medieval', 'offhand', 'Heater Shield', 'pointed triangular hardwood heater shield with polished steel rim and heraldic lion field'),
        ('medieval', 'accessory', 'Gold Signet Ring', 'heavy solid gold royal signet ring set with cabochon deep blue sapphire'),
        # Gunpowder (5)
        ('gunpowder', 'weapon', 'Flintlock Brace', 'pair of finely crafted flintlock holster pistols with walnut stocks and carved brass locks'),
        ('gunpowder', 'armor', 'Musketeer Coat', 'stout buff leather military coat with reinforced steel throat gorget and sash'),
        ('gunpowder', 'helm', 'Tricorn Hat', 'stiff black wool felt tricorn military officer hat with cockade and gold wire trim'),
        ('gunpowder', 'boots', 'Riding Boots', 'tall black polished leather cavalry jackboots with brass spurs and turnover cuffs'),
        ('gunpowder', 'offhand', 'Target Buckler', 'steel round target buckler with integral center spike and screw-in pistol rest'),
        # Industrial (4)
        ('industrial', 'weapon', 'Repeating Carbine', 'blued steel lever-action repeating service carbine with oil-finished walnut stock'),
        ('industrial', 'armor', 'Riveted Vest', 'heavy canvas tactical vest containing overlapping hardened riveted steel ballistic plates'),
        ('industrial', 'helm', 'Field Cap', 'structured wool officer field peaked cap with leather visor and stamped brass badge'),
        ('industrial', 'boots', 'Marching Boots', 'heavy hobnailed trench combat boots with double buckle leather gaiters'),
    ]
    for age, slot, name, desc in gear:
        item_id = f'gear-{age}-{slot}'
        prompt = PROP_COMMON + (
            f'ONE high-detail equipment icon for Ages of Dominion RPG: {age.capitalize()} Age {name} ({slot}). {desc}. '
            'Centrally framed inventory object, crisp authentic period materials, warm studio lighting. '
            'Pure flat magenta #FF00FF backdrop, no floor, no shadows, no text.'
        )
        items.append({
            'position': len(items) + 1, 'id': item_id, 'kind': 'gear', 'mode': None, 'age': age,
            'aspect': '1:1', 'prompt': prompt, 'styleReference': style_forge, 'guide': None,
            'requiredAlpha': True, 'reviewStatus': 'UNVERIFIED', 'attempt': 1, 'requestedOutputs': 1,
            'reviewCriteria': f'{age.capitalize()} era, {slot} item identity, clean silhouette, rich materials, clean magenta background.',
            'styleReferenceSHA256': style_forge_sha, 'promptSHA256': sha_bytes(prompt.encode('utf-8')), 'guideSHA256': None
        })

    return write_manifest(13, items)

# ----------------- RECONCILE BUDGET LEDGER -----------------
def reconcile_budget():
    budget = json.loads((PLAN / 'budget-ledger.json').read_text(encoding='utf-8'))
    
    # Measured token usage from 240 collected records across batches 01-08:
    # 555,443 input tokens, 270,271 output tokens
    # Standard rates: input $0.50/1M, candidate tokens $60/1M => $16.494 USD
    # Add 15% buffer for storage, API overhead, non-inference operations => $18.97 USD total
    reconciled_per_batch = 2.37  # 8 * 2.37 = 18.96 USD
    
    for b in budget['batches']:
        if b['id'] in [f'production-{i:02d}-20261003' for i in range(1, 9)]:
            b['reconciledExposureUSD'] = reconciled_per_batch
            b['reconciliationStatus'] = 'RECONCILED_UPPER_BOUND_STANDARD_RATES'
            
    budget['reconciliationTrail'] = {
        'reconciledAt': '2026-10-03T16:55:00+05:30',
        'policy': 'EVIDENCE_BOUNDED_STANDARD_RATE_CEILING_WITH_OVERHEAD',
        'tariffSource': 'https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing',
        'standardTariff': {'inputPer1M': 0.50, 'imageOutputPer1M': 60.00},
        'measuredCompletedUsageTokens': {'inputTokens': 555443, 'outputTokens': 270271, 'totalTokens': 825714},
        'tokenStandardCostUSD': 16.494,
        'overheadAndStorageBufferUSD': 2.474,
        'reconciledBatches01To08TotalUSD': 18.968,
        'historicalMockReservationUSD': 2.00,
        'safetyReserveUSD': 15.00,
        'baseCommittedProtectedUSD': 35.968,
        'futureBatchHoldUSD': 6.00,
        'projectedFiveBatchTotalUSD': 35.968 + (5 * 6.00), # 65.968 USD <= 80.00 USD
        'hardCapUSD': 80.00,
        'projectedMarginUnderHardCapUSD': 80.00 - (35.968 + (5 * 6.00)), # 14.032 USD
        'invoiceStatus': 'BILLED_TOTAL_REMAINS_UNKNOWN_HOLDS_RECONCILED'
    }
    
    (PLAN / 'budget-ledger.json').write_text(json.dumps(budget, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print('Updated budget-ledger.json with reconciled liability trail.')

if __name__ == '__main__':
    prepare_batch_10()
    prepare_batch_11()
    prepare_batch_12()
    prepare_batch_13()
    reconcile_budget()
    print('Batches 10, 11, 12, 13 prepared successfully and budget reconciled.')
