import os, shutil, json, hashlib
from PIL import Image
import numpy as np

ROOT = 'C:/dev/ages-of-dominion-reborn'
QA_DIR = f'{ROOT}/qa/offline-controls-repair-20261004/portraits_qa'
os.makedirs(QA_DIR, exist_ok=True)
os.makedirs(f'{ROOT}/assets/derivatives/portraits/v1_archived', exist_ok=True)
os.makedirs(f'{ROOT}/assets/derivatives/portraits/v2', exist_ok=True)

def compute_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

# 1. Archive existing v1 crops if not already archived
v1_files = [f for f in os.listdir(f'{ROOT}/assets/derivatives/portraits') if f.endswith('.png')]
for vf in v1_files:
    src = f'{ROOT}/assets/derivatives/portraits/{vf}'
    dst = f'{ROOT}/assets/derivatives/portraits/v1_archived/{vf}'
    if not os.path.exists(dst):
        shutil.copy2(src, dst)
print(f"Preserved {len(v1_files)} v1 portrait crops into assets/derivatives/portraits/v1_archived/")

# 2. Load calibrated landmarks
calib = json.load(open(f'{ROOT}/qa/offline-controls-repair-20261004/calibrated-portrait-landmarks.json'))

# Canonical rival map
RIVAL_CANONICAL_MAP = {
    "rival-identity-1": {
        "canonicalName": "Bran the Relentless",
        "slug": "rival-bran-the-relentless",
        "role": "feudal_baron",
        "era": "medieval",
        "rNum": 4,
        "promptArchetype": "Lord Aldric the Steadfast: stern feudal rival baron in ornate damascened plate armor",
        "mappingStatus": "PROPOSED_IDENTITY_MAPPING_UNVERIFIED_BY_OWNER",
        "alternativeBaseline": "C:/dev/ages-of-dominion/public/art/rival-4.webp"
    },
    "rival-identity-2": {
        "canonicalName": "Malakor the Flayed",
        "slug": "rival-malakor-the-flayed",
        "role": "shadow_sorcerer",
        "era": "ancient",
        "rNum": 2,
        "promptArchetype": "Arch-Warlock Corvus: shadowy rival sorcerer in raven-feathered cowl with obsidian staff",
        "mappingStatus": "PROPOSED_IDENTITY_MAPPING_UNVERIFIED_BY_OWNER",
        "alternativeBaseline": "C:/dev/ages-of-dominion/public/art/rival-2.webp"
    },
    "rival-identity-3": {
        "canonicalName": "Thalric Ash-Bane",
        "slug": "rival-thalric-ash-bane",
        "role": "industrial_magnate",
        "era": "industrial",
        "rNum": 3,
        "promptArchetype": "Ironmaster Kane: ruthless industrial rival magnate in soot-stained wool coat",
        "mappingStatus": "PROPOSED_IDENTITY_MAPPING_UNVERIFIED_BY_OWNER",
        "alternativeBaseline": "C:/dev/ages-of-dominion/public/art/rival-3.webp"
    },
    "rival-identity-4": {
        "canonicalName": "Soren the Unforgiving",
        "slug": "rival-soren-the-unforgiving",
        "role": "arcane_seeress",
        "era": "modern",
        "rNum": 6,
        "promptArchetype": "Enchantress Morgana: mystical rival seeress in flowing silk robes with crystal pendulum",
        "mappingStatus": "PROPOSED_IDENTITY_MAPPING_UNVERIFIED_BY_OWNER",
        "alternativeBaseline": "C:/dev/ages-of-dominion/public/art/rival-6.webp"
    },
    "rival-identity-5": {
        "canonicalName": "Varek Iron-Eye",
        "slug": "rival-varek-iron-eye",
        "role": "scarred_warlord",
        "era": "iron",
        "rNum": 1,
        "promptArchetype": "Commander Theron: scarred veteran rival warlord in battle-tested iron breastplate",
        "mappingStatus": "PROPOSED_IDENTITY_MAPPING_UNVERIFIED_BY_OWNER",
        "alternativeBaseline": "C:/dev/ages-of-dominion/public/art/rival-1.webp"
    },
    "rival-identity-6": {
        "canonicalName": "Karn Blood-Tide",
        "slug": "rival-karn-blood-tide",
        "role": "calculating_diplomat",
        "era": "future",
        "rNum": 5,
        "promptArchetype": "Lady Valeria the Cunning: calculating rival noblewoman diplomat in dark velvet gown",
        "mappingStatus": "PROPOSED_IDENTITY_MAPPING_UNVERIFIED_BY_OWNER",
        "alternativeBaseline": "C:/dev/ages-of-dominion/public/art/rival-5.webp"
    }
}

corrected_manifest = {}
review_crops = []

for c in calib:
    iid = c['id']
    src_p = f'{ROOT}/assets/high-res/final-native2k/{iid}.png'
    im = Image.open(src_p).convert('RGB')
    
    x1, y1, x2, y2 = c['cropBox']
    crop = im.crop((x1, y1, x2, y2))
    card_crop = crop.resize((512, 512), Image.Resampling.LANCZOS)
    
    # Save to v2 and main portraits folder
    v2_rel = f'assets/derivatives/portraits/v2/{iid}.png'
    main_rel = f'assets/derivatives/portraits/{iid}.png'
    card_crop.save(f'{ROOT}/{v2_rel}')
    card_crop.save(f'{ROOT}/{main_rel}')
    
    deriv_paths = [main_rel, v2_rel]
    
    # If rival, also save under canonical name
    canon_info = RIVAL_CANONICAL_MAP.get(iid)
    if canon_info:
        canon_slug = canon_info['slug']
        v2_canon = f'assets/derivatives/portraits/v2/{canon_slug}.png'
        main_canon = f'assets/derivatives/portraits/{canon_slug}.png'
        card_crop.save(f'{ROOT}/{v2_canon}')
        card_crop.save(f'{ROOT}/{main_canon}')
        deriv_paths.extend([main_canon, v2_canon])
        
    corrected_manifest[iid] = {
        'id': iid,
        'recipeVersion': 'v2-calibrated-landmarks',
        'cropBoxNative': [x1, y1, x2, y2],
        'headTopNative': c['headTopY'],
        'headCenterNative': c['headCenterX'],
        'headroomNative': c['headroom'],
        'derivativeDimensions': [512, 512],
        'derivativeMode': 'RGB',
        'intendedUse': 'card_bust_portrait',
        'travelUse': 'UNSUITABLE_CARD_BUST_ONLY',
        'isKnightMountedMaster': (iid == 'knight-mounted-master'),
        'stoneTravelStatus': 'STONE_FAIL_ERA_MISMATCH' if (iid == 'knight-mounted-master') else 'N_A',
        'derivativePaths': deriv_paths,
        'derivativeSHA256': compute_sha256(f'{ROOT}/{main_rel}'),
        'canonicalRivalInfo': canon_info
    }
    review_crops.append((iid, card_crop))

# 3. Create review contact sheets on Black, White, and Neutral Green
cols = 8
rows = (len(review_crops) + cols - 1) // cols
cell_w, cell_h = 256, 256
sheet_w = cols * cell_w
sheet_h = rows * cell_h

for bg_name, bg_color in [('black', (0, 0, 0)), ('white', (255, 255, 255)), ('green', (0, 177, 64))]:
    sheet = Image.new('RGB', (sheet_w, sheet_h), bg_color)
    for idx, (iid, crop_512) in enumerate(review_crops):
        r = idx // cols
        c = idx % cols
        thumb = crop_512.resize((cell_w, cell_h), Image.Resampling.LANCZOS)
        sheet.paste(thumb, (c * cell_w, r * cell_h))
    sheet_path = f'{QA_DIR}/portraits-review-sheet-{bg_name}.png'
    sheet.save(sheet_path)
    print(f"Saved review contact sheet: {sheet_path}")

# 4. Save corrected portraits manifest
with open(f'{ROOT}/qa/offline-controls-repair-20261004/corrected-portraits-manifest.json', 'w') as f:
    json.dump(corrected_manifest, f, indent=2)

print("\nStep 4: All 38 portraits successfully processed into v2 calibrated crops!")
