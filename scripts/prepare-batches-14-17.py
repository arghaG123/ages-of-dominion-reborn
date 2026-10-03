"""Prepare manifests for Batches 14, 15, 16, and 17.
Maintains exact 30 useful requests per batch (120 total).
Zero filler. Full compliance with frozen inventory and canonical tables.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/plan/image-production"

def digest(data):
    if isinstance(data, str):
        data = data.encode('utf-8')
    return hashlib.sha256(data).hexdigest()

# Load style references SHA256
STYLE_DIR = ROOT / "design-preview/generated/landscape-mocks-20261003-efcd7a7e/images"
FORGE_SHA = digest((STYLE_DIR / "22-forge.jpg").read_bytes())
KINGDOM_SHA = digest((STYLE_DIR / "02-kingdom-day1.jpg").read_bytes())
INVENTORY_SHA = digest((STYLE_DIR / "23-inventory.jpg").read_bytes())
SPELLS_SHA = digest((STYLE_DIR / "21-spells.jpg").read_bytes())
WAVE_SHA = digest((STYLE_DIR / "18-defense-wave.jpg").read_bytes())

GUIDE_DIR = PLAN / "guides"
KINGDOM_GUIDE_REL = "docs/plan/image-production/guides/kingdom-stone-day1-composition-v4.png"
KINGDOM_GUIDE_SHA = digest((ROOT / KINGDOM_GUIDE_REL).read_bytes())

# Load full purchase inventory to get all gear items
INV = json.loads((PLAN / "full-purchase-inventory.json").read_text(encoding='utf-8'))
manifest_ids = set()
for i in range(1, 14):
    p = PLAN / f"batch-{i:02d}-manifest.json"
    if p.exists():
        m = json.loads(p.read_text(encoding='utf-8'))
        for it in m['items']:
            manifest_ids.add(it['id'])

gear_unrequested = [it for it in INV['items'] if it['category'] == 'gear' and it['id'] not in manifest_ids]
assert len(gear_unrequested) == 95, f"Expected 95 unrequested gear, got {len(gear_unrequested)}"

# Gear details helper
def describe_gear(gid, age):
    parts = gid.split('-')
    # parts e.g. ['gear', 'stone', 'helm', 'hood'] or ['gear', 'modern', 'weapon']
    slot = parts[2]
    subtype = parts[3] if len(parts) > 3 else "standard"
    
    age_cap = age.capitalize()
    
    descriptions = {
        # Stone
        ("stone", "helm", "hood"): ("Stone Age Forager Leather Hood (helm)", "stitched wolf pelt and rawhide hood with bone needle lacing"),
        ("stone", "helm", "circlet"): ("Stone Age Shaman Bone Circlet (helm)", "polished mammoth ivory headband carved with primitive hunting runes"),
        ("stone", "weapon", "ranger"): ("Stone Age Flint Shortbow (weapon)", "flexible yew wood hunting bow with sinew string and flint-tipped river cane arrows"),
        ("stone", "weapon", "caster"): ("Stone Age Shaman Fire Totem (weapon)", "gnarled ash wood walking staff topped with a glowing fire-hardened amber focus"),
        ("stone", "weapon", "barbarian"): ("Stone Age Heavy Flint Cleaver (weapon)", "massive chipped flint hand axe lashed to a sturdy antler haft with leather sinew"),
        ("stone", "offhand", "codex"): ("Stone Age Cave Etching Slate (offhand)", "flat slate rock tablet engraved with ochre tribal star maps and migration symbols"),
        ("stone", "offhand", "focus"): ("Stone Age Ritual Mammoth Fetish (offhand)", "carved mammoth bone talisman bound with eagle feathers and dried sage cord"),
        ("stone", "armor", "field"): ("Stone Age Hunter Rawhide Tunic (armor)", "cured deer hide hunter vest with bone toggle fasteners and fur lining"),
        ("stone", "armor", "robe"): ("Stone Age Shaman Bearskin Wrap (armor)", "heavy cured cave bearskin ceremonial robe draped over shoulders with claws intact"),
        ("stone", "boots", "soft"): ("Stone Age Fur Moccasins (boots)", "supple deer leather moccasins lined with rabbit fur and bound with rawhide cords"),
        
        # Bronze
        ("bronze", "helm", "hood"): ("Bronze Age Padded Linen Arming Hood (helm)", "quilted bleached linen coif hood with reinforced cheek ties"),
        ("bronze", "helm", "circlet"): ("Bronze Age Beaten Gold Diadem (helm)", "hammered sheet gold royal diadem embossed with sun rays and spiral patterns"),
        ("bronze", "weapon", "ranger"): ("Bronze Age Composite Horn Bow (weapon)", "recurved composite bow made of horn, wood and sinew with bronze-tipped reed arrows"),
        ("bronze", "weapon", "caster"): ("Bronze Age Oracle Bronze Scepter (weapon)", "cast bronze ceremonial rod crowned with a lapis lazuli sphere and lotus petals"),
        ("bronze", "weapon", "barbarian"): ("Bronze Age Spiked Bronze War Club (weapon)", "heavy cast bronze socketed mace with flanged ridges on an olive wood handle"),
        ("bronze", "offhand", "codex"): ("Bronze Age Cuneiform Clay Tablet (offhand)", "baked clay legal cuneiform tablet stamped with royal administrative seals"),
        ("bronze", "offhand", "focus"): ("Bronze Age Lapis Divination Stone (offhand)", "polished deep blue lapis lazuli scarab stone inscribed with hieroglyphic sigils"),
        ("bronze", "armor", "field"): ("Bronze Age Scale Linothorax (armor)", "laminated linen cuirass reinforced with overlapping rows of stamped bronze scales"),
        ("bronze", "armor", "robe"): ("Bronze Age Dyed Priest Toga (armor)", "fine purple-dyed woven wool pleated priest robe edged with embroidered gold borders"),
        ("bronze", "boots", "soft"): ("Bronze Age Strapped Leather Sandals (boots)", "thick oxhide sole sandals with crisscrossing calf leather laces and bronze studs"),
        
        # Iron
        ("iron", "helm", "hood"): ("Iron Age Riveted Chainmail Coif (helm)", "interlinked riveted iron ring mail coif hood protecting neck and head"),
        ("iron", "helm", "circlet"): ("Iron Age Chieftain Torc Crown (helm)", "twisted iron and silver alloy neck torc and brow ring with stylized beast terminals"),
        ("iron", "weapon", "ranger"): ("Iron Age Ash Longbow (weapon)", "tall six-foot carved ash longbow with hemp string and iron bodkin arrow quiver"),
        ("iron", "weapon", "caster"): ("Iron Age Druid Oak Staff (weapon)", "ancient knotted gnarled oak druid staff crowned with a glowing mistletoe bough"),
        ("iron", "weapon", "barbarian"): ("Iron Age Two-Handed Iron Dane Axe (weapon)", "broad curved iron bearded battle axe mounted on a sturdy five-foot ash shaft"),
        ("iron", "offhand", "codex"): ("Iron Age Wax Inscribed Diptych (offhand)", "folding wood diptych coated in black wax inscribed with iron stylus runes"),
        ("iron", "offhand", "focus"): ("Iron Age Celtic Amber Talisman (offhand)", "raw Baltic amber pendant encased in knotted iron wire cage on a braided leather thong"),
        ("iron", "armor", "field"): ("Iron Age Studded Leather Brigandine (armor)", "heavy boiled leather jerkin reinforced with internal iron plates and exterior steel rivets"),
        ("iron", "armor", "robe"): ("Iron Age Heavy Wool Cloak (armor)", "tartan woven thick wool mantle fastened with a heavy cast iron annular ring brooch"),
        ("iron", "boots", "soft"): ("Iron Age Turnshoe Leather Boots (boots)", "flexible oiled cowhide turnshoes with lateral leather lace toggles"),
        
        # Medieval
        ("medieval", "helm", "hood"): ("Medieval Quilted Arming Coif (helm)", "padded heavy canvas arming coif hood with chin strap for wearing under a helm"),
        ("medieval", "helm", "circlet"): ("Medieval Jeweled Gold Coronet (helm)", "chased gold nobility coronet set with cabochon rubies and sapphire fleur-de-lis"),
        ("medieval", "weapon", "ranger"): ("Medieval Yew War Longbow (weapon)", "heavy military yew longbow with 120-pound draw weight and sheaf of barbed broadhead arrows"),
        ("medieval", "weapon", "caster"): ("Medieval Inlaid Arcane Wand (weapon)", "carved ebony arcane casting rod tipped with a glowing faceted amethyst crystal"),
        ("medieval", "weapon", "barbarian"): ("Medieval Steel Flanged Mace (weapon)", "solid steel hexagonal flanged war mace with a wire-wrapped handle and pointed spike"),
        ("medieval", "offhand", "codex"): ("Medieval Illuminated Psalter (offhand)", "illuminated manuscript book bound in calf vellum with gilded miniature paintings and brass clasps"),
        ("medieval", "offhand", "focus"): ("Medieval Reliquary Rosary (offhand)", "silver rosary beads holding a polished rock crystal reliquary pendant"),
        ("medieval", "armor", "field"): ("Medieval Reinforced Gambeson (armor)", "multi-layered heavy linen gambeson jacket with vertical quilting and leather arm ties"),
        ("medieval", "armor", "robe"): ("Medieval Embroidered Silk Cassock (armor)", "crimson silk ceremonial scholar robe trimmed with white ermine fur cuffs"),
        ("medieval", "boots", "soft"): ("Medieval Pointed Pouleine Shoes (boots)", "soft dyed calfskin pouleine ankle shoes with elongated pointed toes"),
        
        # Gunpowder
        ("gunpowder", "helm", "hood"): ("Gunpowder Velvet Cavalier Hat (helm)", "wide-brimmed black velvet cavalier hat adorned with a sweeping white ostrich plume"),
        ("gunpowder", "helm", "circlet"): ("Gunpowder Gilded Officer Gorget (helm)", "polished steel and gilt officer neck gorget engraved with royal crest insignia"),
        ("gunpowder", "weapon", "ranger"): ("Gunpowder Wheellock Hunting Rifle (weapon)", "ornate curly walnut-stocked wheellock carbine rifle with engraved lockplate and powder horn"),
        ("gunpowder", "weapon", "caster"): ("Gunpowder Alchemical Glass Retort (weapon)", "handheld blown glass alchemy distillation vessel filled with bubbling volatile alchemical fire"),
        ("gunpowder", "weapon", "barbarian"): ("Gunpowder Boarding Cutlass (weapon)", "heavy curved maritime boarding cutlass with solid brass basket hilt and wooden scabbard"),
        ("gunpowder", "offhand", "codex"): ("Gunpowder Ballistics Field Log (offhand)", "leather-bound artillery gunner notebook containing hand-drawn trajectory tables and firing notes"),
        ("gunpowder", "offhand", "focus"): ("Gunpowder Brass Astrolabe (offhand)", "precision engraved brass mariner astrolabe with rotating rete dial and sighting alidade"),
        ("gunpowder", "armor", "field"): ("Gunpowder Buff Leather Coat (armor)", "thick oiled buff coat made of heavy oxhide tailored with split skirts for riding"),
        ("gunpowder", "armor", "robe"): ("Gunpowder Tailored Wool Justacorps (armor)", "rich blue wool military coat with flared skirts, silver wire braiding and brass buttons"),
        ("gunpowder", "boots", "soft"): ("Gunpowder Buckled Cavalier Shoes (boots)", "squared-toe black leather court shoes with prominent ornate silver tongue buckles"),
        ("gunpowder", "accessory"): ("Gunpowder Brass Pocket Compass (accessory)", "folding brass pocket magnetic dry compass with sun dial lid and compass rose dial"),
        
        # Industrial
        ("industrial", "helm", "hood"): ("Industrial Gas Mask Hood (helm)", "vulcanized black rubber and canvas respirator hood with round glass eye lenses and brass filter"),
        ("industrial", "helm", "circlet"): ("Industrial Brass Welding Goggles (helm)", "heavy brass spectacles with dark tinted glass protective lenses and adjustable leather strap"),
        ("industrial", "weapon", "ranger"): ("Industrial Lever-Action Repeating Carbine (weapon)", "steel tubular magazine lever-action saddle carbine with oiled walnut stock and iron sights"),
        ("industrial", "weapon", "caster"): ("Industrial Galvanic Ley Leyden Battery (weapon)", "copper and blown glass capacitor battery bottle discharging blue electrostatic lightning arcs"),
        ("industrial", "weapon", "barbarian"): ("Industrial Steam Riveting Hammer (weapon)", "heavy cast-iron pneumatically-assisted forging war hammer with ribbed exhaust cylinder"),
        ("industrial", "offhand", "standard"): ("Industrial Steel Trench Buckler (offhand)", "corrugated stamped steel convex trench shield with central vision port and leather arm sling"),
        ("industrial", "offhand", "codex"): ("Industrial Locomotive Blueprints Ledger (offhand)", "bound cloth portfolio containing cyanotype architectural blueprints and steam patent schematics"),
        ("industrial", "offhand", "focus"): ("Industrial Brass Steam Pressure Gauge (offhand)", "calibrated circular brass boiler pressure dial with needle gauge and copper siphon valve"),
        ("industrial", "armor", "field"): ("Industrial Reinforced Miner Canvas Overall (armor)", "heavy waxed duck canvas work vest with steel rivets, tool hooks, and padded shoulder yolk"),
        ("industrial", "armor", "robe"): ("Industrial Wool Inverness Cape (armor)", "charcoal herringbone tweed overcoat with attached weatherproof shoulder storm cape"),
        ("industrial", "boots", "soft"): ("Industrial Oxford Lace-Up Shoes (boots)", "sturdy black cap-toe leather Oxford dress shoes with Goodyear-welted rubber soles"),
        ("industrial", "accessory"): ("Industrial Railway Pocket Watch (accessory)", "stem-winding nickel-plated pocket watch with porcelain dial and heavy linked watch chain"),
        
        # Modern
        ("modern", "helm", "standard"): ("Modern Tactical Ballistic Helmet (helm)", "matte foliage green Kevlar combat helmet with night vision goggle mount and accessory rails"),
        ("modern", "helm", "hood"): ("Modern Flame-Resistant Balaclava (helm)", "Nomex black tactical balaclava hood with anti-fragmentation polycarbonate ballistic eye goggles"),
        ("modern", "helm", "circlet"): ("Modern Tactical Headset Comms (helm)", "electronic noise-cancelling communication headset with boom mic and low-profile headband"),
        ("modern", "weapon", "standard"): ("Modern Modular Assault Carbine (weapon)", "matte black 5.56mm assault carbine with holographic red-dot optic, foregrip and picatinny rails"),
        ("modern", "weapon", "ranger"): ("Modern Anti-Materiel Bolt Sniper (weapon)", "heavy .50 caliber sniper rifle with fluted barrel, massive muzzle brake and high-magnification scope"),
        ("modern", "weapon", "caster"): ("Modern Portable EMP Emitter (weapon)", "compact tactical directed electromagnetic pulse device with glowing neon blue capacitor coils"),
        ("modern", "weapon", "barbarian"): ("Modern Tactical Carbon Breaching Axe (weapon)", "forged carbon-steel tactical tomahawk with textured G10 composite handle and pry spike"),
        ("modern", "offhand", "standard"): ("Modern Polycarbonate Riot Shield (offhand)", "transparent curved ballistic polycarbonate shield with heavy-duty ergonomic rubber handle"),
        ("modern", "offhand", "codex"): ("Modern Ruggedized Tactical Tablet (offhand)", "drop-resistant military battlefield tablet displaying encrypted digital satellite GPS mapping"),
        ("modern", "offhand", "focus"): ("Modern Handheld Laser Target Designator (offhand)", "infrared laser rangefinder and optical target acquisition monocular with digital HUD readouts"),
        ("modern", "armor", "standard"): ("Modern MOLLE Ballistic Plate Carrier (armor)", "multicam Cordura tactical vest with ceramic armor plates, magazine pouches and hydration pack"),
        ("modern", "armor", "field"): ("Modern Ripstop Combat Uniform (armor)", "camouflage ripstop combat shirt and trousers with integrated polymer elbow and knee pads"),
        ("modern", "armor", "robe"): ("Modern Tactical Ghillie Sniper Poncho (armor)", "3D woodland concealment ghillie cape with natural jute burlap strands and synthetic leaves"),
        ("modern", "boots", "standard"): ("Modern Gore-Tex Assault Combat Boots (boots)", "waterproof coyote tan suede tactical combat boots with Vibram aggressive traction lug soles"),
        ("modern", "boots", "soft"): ("Modern Lightweight Recon Shoes (boots)", "silent rubber-sole athletic tactical recon trainers with reinforced abrasion-resistant toe guard"),
        ("modern", "accessory"): ("Modern Tactical Wrist GPS Navigator (accessory)", "shockproof digital smartwatch displaying military grid coordinates, barometric altimeter and compass"),
        
        # Future
        ("future", "helm", "standard"): ("Future Cybernetic Full Visor Helm (helm)", "seamless carbon-fiber full enclosure helmet with reflective gold HUD visor and rebreather vents"),
        ("future", "helm", "hood"): ("Future Hex-Weave Stealth Cowl (helm)", "matte black active-camouflage nano-lattice cowl that distorts light around head and shoulders"),
        ("future", "helm", "circlet"): ("Future Neural Synapse Interface Band (helm)", "sculpted titanium cranial headset ring pulsing with glowing cyan fiber-optic data nodes"),
        ("future", "weapon", "standard"): ("Future Magnetic Coilgun Rifle (weapon)", "ergonomic bullpup magnetic mass accelerator rifle with illuminated blue induction accelerator rails"),
        ("future", "weapon", "ranger"): ("Future Particle Beam Sniper Cannon (weapon)", "slender high-precision particle accelerator sniper rifle with floating holographic reticle scope"),
        ("future", "weapon", "caster"): ("Future Quantum Singularity Scepter (weapon)", "levitating gyroscopic gravitational focus rod with counter-rotating magnetic containment rings"),
        ("future", "weapon", "barbarian"): ("Future Superheated Plasma Claymore (weapon)", "high-frequency vibrating greatsword with glowing orange superheated plasma containment blade edge"),
        ("future", "offhand", "standard"): ("Future Hexagonal Hardlight Barrier (offhand)", "forearm-mounted emitter projector deploying a translucent glowing cyan energy shield"),
        ("future", "offhand", "codex"): ("Future Holographic Data Crystal (offhand)", "floating geometric quantum sapphire crystal matrix projecting animated blue holographic schematics"),
        ("future", "offhand", "focus"): ("Future Zero-Point Energy Conduit (offhand)", "spherical anti-gravity orb housing a pulsating miniature fusion plasma core"),
        ("future", "armor", "standard"): ("Future Powered Exoskeleton Armor (armor)", "carbon-nanotube powered chassis with pneumatic joint servos and reactive energy shield plates"),
        ("future", "armor", "field"): ("Future Smart-Polymer Nanoweave Jumpsuit (armor)", "flexible black thermal-regulating body suit woven with impact-hardening shear-thickening fluid"),
        ("future", "armor", "robe"): ("Future Photonic Energy Mantle (armor)", "flowing iridescent smart-fabric scholar robe woven with bioluminescent fiber-optic patterns"),
        ("future", "boots", "standard"): ("Future Mag-Lev Heavy Combat Greaves (boots)", "titanium motorized combat boots with integrated repulsor jump jets and magnetic sole clamps"),
        ("future", "boots", "soft"): ("Future Sound-Dampening Stealth Soles (boots)", "aerogel-cushioned silent tactical boots with active acoustic cancellation tread pads"),
        ("future", "accessory"): ("Future Sub-Dermal Chrono Wrist Matrix (accessory)", "luminescent holographic wrist projector displaying encrypted spatial coordinates and time-dilation metrics")
    }
    key = (age, slot, subtype)
    if key in descriptions:
        return descriptions[key]
    # Fallback generic
    return (f"{age_cap} Age {slot.capitalize()} ({slot})", f"authentic {age} period strategy game equipment icon with rich materials")

def make_gear_item(pos, gid, age):
    name, desc = describe_gear(gid, age)
    p_text = f"ONE production image for Ages of Dominion. Semi-realistic dense rendered strategy-game materials, warm upper-left daylight, short soft contact shadows. NO text, HUD, buttons, labels, numbers, device frame, watermark, or invented names. Isolated object on pure magenta #FF00FF background. No floor, no background shadow. ONE high-detail equipment icon for Ages of Dominion RPG: {name}. {desc}. Centrally framed inventory object, crisp authentic period materials, warm studio lighting. Pure flat magenta #FF00FF backdrop, no floor, no shadows, no text."
    return {
        "position": pos,
        "id": gid,
        "kind": "gear",
        "mode": None,
        "age": age,
        "aspect": "1:1",
        "prompt": p_text,
        "styleReference": "22-forge.jpg",
        "guide": None,
        "requiredAlpha": True,
        "reviewStatus": "UNVERIFIED",
        "attempt": 1,
        "requestedOutputs": 1,
        "reviewCriteria": f"{age.capitalize()} era, {gid} item identity, clean silhouette, rich materials, clean magenta background.",
        "styleReferenceSHA256": FORGE_SHA,
        "promptSHA256": digest(p_text),
        "guideSHA256": None
    }

# -----------------
# BATCH 14 (30 items)
# -----------------
# 29 equipment items + Position 30 Kingdom scene
# The 29 equipment items: Industrial (4) + Modern (16) + Future (9)
b14_gear_ids = [g['id'] for g in gear_unrequested if g['id'].startswith(('gear-industrial-armor-field', 'gear-industrial-armor-robe', 'gear-industrial-boots-soft', 'gear-industrial-accessory', 'gear-modern-', 'gear-future-helm', 'gear-future-weapon', 'gear-future-offhand'))]
# Limit to 29 items
b14_gear_slice = gear_unrequested[59:88] # indices 59 to 88 inclusive is 29 items: gear-industrial-armor-field through gear-future-offhand-codex
assert len(b14_gear_slice) == 29, f"Slice length: {len(b14_gear_slice)}"

b14_items = []
for idx, g in enumerate(b14_gear_slice):
    age = g['id'].split('-')[1]
    b14_items.append(make_gear_item(idx + 1, g['id'], age))

# Item 30: Kingdom Scene
k_prompt = (
    "Create ONE landscape 16:9/1K, high-detail Stone Age Day1 Kingdom composition reference for Ages of Dominion. "
    "Follow the corrected spatial guide for layout, the approved landscape Day1 mock for material finish/composition only, "
    "and preserved Hall v3 for Stone architecture. Show exactly one completed, dominant timber/hide/thatch/flint Town Hall "
    "on the upper civic terrace, naturally grounded, with intact proportions, full roof/base in frame and a clear entrance. "
    "Show 17 empty natural buildable clearings linked by soil paths, and an unbuilt perimeter: no completed walls/towers/gate. "
    "Keep sites and road/crossing approaches clear of mutable buildings/actors/material stacks. "
    "Follow river-right geography, age-appropriate crossing, hills/rocks/forest margins and the proposed common aerial "
    "three-quarter camera. Warm upper-left daylight; coherent contact shadows and natural continuous ground. "
    "No medieval church/spires, mature city, tiny floating Hall, pasted ground island, stretched roof, missing terrain strips, "
    "guide rectangles/labels/grid, HUD/text/buttons/watermark."
)
b14_items.append({
    "position": 30,
    "id": "kingdom-stone-day1-composition-v4",
    "kind": "kingdom-scene",
    "mode": "kingdom",
    "age": "stone",
    "aspect": "16:9",
    "prompt": k_prompt,
    "styleReference": "02-kingdom-day1.jpg",
    "guide": KINGDOM_GUIDE_REL,
    "requiredAlpha": False,
    "reviewStatus": "UNVERIFIED",
    "attempt": 4,
    "requestedOutputs": 1,
    "reviewCriteria": "Stone identity, Day 1 state (1 completed Hall, 17 empty sites, no walls/towers/church), dominant civic terrace, natural grounding, complete unclipped roof and base, coherent high aerial 3/4 perspective.",
    "styleReferenceSHA256": KINGDOM_SHA,
    "promptSHA256": digest(k_prompt),
    "guideSHA256": KINGDOM_GUIDE_SHA
})
assert len(b14_items) == 30

# -----------------
# BATCH 15 (30 items)
# -----------------
# Remaining Future gear (7 items) + Stone gear (10 items) + Bronze gear (10 items) + Iron gear (first 3 items) = 30 items
b15_gear_slice = gear_unrequested[88:95] + gear_unrequested[0:20] + gear_unrequested[20:23]
assert len(b15_gear_slice) == 30, f"b15 gear slice: {len(b15_gear_slice)}"

b15_items = []
for idx, g in enumerate(b15_gear_slice):
    age = g['id'].split('-')[1]
    b15_items.append(make_gear_item(idx + 1, g['id'], age))

# -----------------
# BATCH 16 (30 items)
# -----------------
# Iron gear (remaining 7 items) + Medieval gear (10 items) + Gunpowder gear (11 items) + Industrial gear (first 2 items) = 30 items
b16_gear_slice = gear_unrequested[23:30] + gear_unrequested[30:40] + gear_unrequested[40:51] + gear_unrequested[51:53]
assert len(b16_gear_slice) == 30, f"b16 gear slice: {len(b16_gear_slice)}"

b16_items = []
for idx, g in enumerate(b16_gear_slice):
    age = g['id'].split('-')[1]
    b16_items.append(make_gear_item(idx + 1, g['id'], age))

# -----------------
# BATCH 17 (30 items)
# -----------------
# Industrial gear (remaining 6 items: indices 53 to 59): gear-industrial-weapon-ranger through gear-industrial-offhand-focus
# + 7 Heavy/Siege corrections
# + 7 Canonical Artifacts
# + 5 Canonical Spell Effects
# + 5 Creature / Mount Rig Attachments
# Total: 6 + 7 + 7 + 5 + 5 = 30 items!
b17_gear_slice = gear_unrequested[53:59]
assert len(b17_gear_slice) == 6, f"b17 gear slice: {len(b17_gear_slice)}"

b17_items = []
for idx, g in enumerate(b17_gear_slice):
    age = g['id'].split('-')[1]
    b17_items.append(make_gear_item(idx + 1, g['id'], age))

# 7 Evidenced Heavy / Siege Corrections
heavy_corrections = [
    {
        "id": "attacker-bronze-heavy",
        "kind": "attacker",
        "mode": "defense",
        "age": "bronze",
        "role": "heavy-attacker",
        "prompt": "ONE production image for Ages of Dominion. Semi-realistic dense rendered strategy-game materials, warm upper-left daylight, short soft contact shadows, coherent camera, high aerial three-quarter view. NO text, HUD, buttons, labels, numbers, device frame, watermark, or invented names. ONE photoreal isolated Bronze Age heavy chariot attacker unit: Bronze Charioteer. Two galloping armored horses pulling a two-wheeled bronze battle chariot carrying a bronze-armored driver and spearman warrior. High aerial three-quarter defense perspective. Grounded on pure flat magenta #FF00FF background, no floor, no shadows on backdrop, no text.",
        "styleReference": "18-defense-wave.jpg",
        "styleSHA": WAVE_SHA,
        "criteria": "Bronze era, heavy chariot unit identity (horses, chariot, warrior crew), defense camera, clean magenta background."
    },
    {
        "id": "attacker-iron-heavy",
        "kind": "attacker",
        "mode": "defense",
        "age": "iron",
        "role": "heavy-attacker",
        "prompt": "ONE production image for Ages of Dominion. Semi-realistic dense rendered strategy-game materials, warm upper-left daylight, short soft contact shadows, coherent camera, high aerial three-quarter view. NO text, HUD, buttons, labels, numbers, device frame, watermark, or invented names. ONE photoreal isolated Iron Age heavy siege beast attacker unit: Iron War Elephant. Massive armored war elephant equipped with iron-sheathed tusk spikes, scale barding, and a wooden howdah tower carrying an iron-armored archer. High aerial three-quarter defense perspective. Grounded on pure flat magenta #FF00FF background, no floor, no shadows on backdrop, no text.",
        "styleReference": "18-defense-wave.jpg",
        "styleSHA": WAVE_SHA,
        "criteria": "Iron era, war elephant unit identity (howdah, iron tusk blades, armor), defense camera, clean magenta background."
    },
    {
        "id": "attacker-gunpowder-heavy",
        "kind": "attacker",
        "mode": "defense",
        "age": "gunpowder",
        "role": "heavy-attacker",
        "prompt": "ONE production image for Ages of Dominion. Semi-realistic dense rendered strategy-game materials, warm upper-left daylight, short soft contact shadows, coherent camera, high aerial three-quarter view. NO text, HUD, buttons, labels, numbers, device frame, watermark, or invented names. ONE photoreal isolated Gunpowder Age heavy siege artillery attacker unit: Gunpowder Cannon Crew. Heavy cast bronze siege bombard cannon mounted on a massive reinforced oak timber wheeled field carriage, accompanied by two uniform-clad gunners with ramrod and powder keg. High aerial three-quarter defense perspective. Grounded on pure flat magenta #FF00FF background, no floor, no shadows on backdrop, no text.",
        "styleReference": "18-defense-wave.jpg",
        "styleSHA": WAVE_SHA,
        "criteria": "Gunpowder era, heavy cannon and crew identity, wheeled carriage, defense camera, clean magenta background."
    },
    {
        "id": "attacker-industrial-heavy",
        "kind": "attacker",
        "mode": "defense",
        "age": "industrial",
        "role": "heavy-attacker",
        "prompt": "ONE production image for Ages of Dominion. Semi-realistic dense rendered strategy-game materials, warm upper-left daylight, short soft contact shadows, coherent camera, high aerial three-quarter view. NO text, HUD, buttons, labels, numbers, device frame, watermark, or invented names. ONE photoreal isolated Industrial Age heavy mechanized attacker unit: Industrial Steam Walker. Heavy bipedal combat walker vehicle of riveted cast iron plates and brass boiler piping, venting white steam plumes, equipped with a forward-facing heavy rotary Gatling cannon. High aerial three-quarter defense perspective. Grounded on pure flat magenta #FF00FF background, no floor, no shadows on backdrop, no text.",
        "styleReference": "18-defense-wave.jpg",
        "styleSHA": WAVE_SHA,
        "criteria": "Industrial era, steam-powered bipedal combat mech walker identity, defense camera, clean magenta background."
    },
    {
        "id": "attacker-modern-heavy",
        "kind": "attacker",
        "mode": "defense",
        "age": "modern",
        "role": "heavy-attacker",
        "prompt": "ONE production image for Ages of Dominion. Semi-realistic dense rendered strategy-game materials, warm upper-left daylight, short soft contact shadows, coherent camera, high aerial three-quarter view. NO text, HUD, buttons, labels, numbers, device frame, watermark, or invented names. ONE photoreal isolated Modern Age heavy armored combat attacker unit: Modern Battle Tank. Heavy tracked armored main battle tank in woodland camouflage, with a rotating turret, 120mm smoothbore gun barrel, smoke grenade dischargers, and composite reactive armor skirts. High aerial three-quarter defense perspective. Grounded on pure flat magenta #FF00FF background, no floor, no shadows on backdrop, no text.",
        "styleReference": "18-defense-wave.jpg",
        "styleSHA": WAVE_SHA,
        "criteria": "Modern era, main battle tank identity (tracks, turret, 120mm barrel), defense camera, clean magenta background."
    },
    {
        "id": "attacker-future-heavy",
        "kind": "attacker",
        "mode": "defense",
        "age": "future",
        "role": "heavy-attacker",
        "prompt": "ONE production image for Ages of Dominion. Semi-realistic dense rendered strategy-game materials, warm upper-left daylight, short soft contact shadows, coherent camera, high aerial three-quarter view. NO text, HUD, buttons, labels, numbers, device frame, watermark, or invented names. ONE photoreal isolated Future Age heavy anti-gravity combat attacker unit: Future Hover Tank. Sleek aerodynamic repulsorlift hover battle tank hovering above ground, with angular composite stealth armor plates, glowing blue anti-gravity underside field, and twin heavy plasma railgun turrets. High aerial three-quarter defense perspective. Grounded on pure flat magenta #FF00FF background, no floor, no shadows on backdrop, no text.",
        "styleReference": "18-defense-wave.jpg",
        "styleSHA": WAVE_SHA,
        "criteria": "Future era, repulsorlift hover tank identity, plasma railguns, defense camera, clean magenta background."
    },
    {
        "id": "tower-iron-splash",
        "kind": "tower",
        "mode": "defense",
        "age": "iron",
        "role": "splash-tower",
        "prompt": "ONE production image for Ages of Dominion. Semi-realistic dense rendered strategy-game materials, warm upper-left daylight, short soft contact shadows, coherent camera, high aerial three-quarter view. NO text, HUD, buttons, labels, numbers, device frame, watermark, or invented names. ONE photoreal isolated Iron Age defensive splash tower structure: Iron Splash Onager. Sturdy timber and iron-reinforced siege onager catapult fortification, with heavy torsion rope bundles, wooden throwing arm holding an iron-banded stone bucket, winches, and an ammunition pile of rough boulders. High aerial three-quarter defense perspective. Grounded on pure flat magenta #FF00FF background, no floor, no shadows on backdrop, no text.",
        "styleReference": "30-icon-material-board.jpg",
        "styleSHA": digest((STYLE_DIR / "30-icon-material-board.jpg").read_bytes()),
        "criteria": "Iron era, onager torsion catapult tower identity (no gunpowder cannon), defense camera, clean magenta background."
    }
]

for hc in heavy_corrections:
    b17_items.append({
        "position": len(b17_items) + 1,
        "id": hc["id"],
        "kind": hc["kind"],
        "mode": hc["mode"],
        "age": hc["age"],
        "aspect": "1:1",
        "prompt": hc["prompt"],
        "styleReference": hc["styleReference"],
        "guide": None,
        "requiredAlpha": True,
        "reviewStatus": "UNVERIFIED",
        "attempt": 2 if "attacker" in hc["id"] or "tower" in hc["id"] else 1,
        "requestedOutputs": 1,
        "reviewCriteria": hc["criteria"],
        "styleReferenceSHA256": hc["styleSHA"],
        "promptSHA256": digest(hc["prompt"]),
        "guideSHA256": None
    })

# 7 Canonical Missing Artifacts
artifacts = [
    ("artifact-wolf-amulet", "Amulet of the Wolf", "carved ancient timber and grey wolf bone talisman with glowing amber wolf eyes and braided sinew cord"),
    ("artifact-bloodstone", "Bloodstone", "faceted deep crimson bloodstone crystal jewel pulsating with crimson veins set in an antique gold filigree pendant"),
    ("artifact-iron-clover", "Iron Clover", "forged wrought-iron four-leaf clover lucky amulet with bevelled steel edges and polished dark metallic sheen"),
    ("artifact-eagle-eye-lens", "Eagle Eye Lens", "precision magnifying brass monocle optic with etched crosshairs and leather head strap"),
    ("artifact-ring-of-vitality", "Ring of Vitality", "glowing emerald green jade signet ring entwined with living golden leaf vine engravings"),
    ("artifact-winged-spurs", "Winged Spurs", "pair of polished golden equestrian boot spurs sculpted with arched feathered angel speed wings"),
    ("artifact-sages-codex", "Sage's Codex", "thick antique leather-bound grimoire book embossed with silver astrological sigils and silk ribbon bookmarks")
]

for aid, aname, adesc in artifacts:
    p_text = f"ONE production image for Ages of Dominion. Semi-realistic dense rendered strategy-game materials, warm upper-left daylight, short soft contact shadows. NO text, HUD, buttons, labels, numbers, device frame, watermark, or invented names. Isolated object on pure magenta #FF00FF background. No floor, no background shadow. ONE high-detail legendary artifact relic icon for Ages of Dominion: {aname}. {adesc}. Centrally framed inventory object, crisp authentic period materials, warm studio lighting. Pure flat magenta #FF00FF backdrop, no floor, no shadows, no text."
    b17_items.append({
        "position": len(b17_items) + 1,
        "id": aid,
        "kind": "artifact",
        "mode": None,
        "age": "all",
        "aspect": "1:1",
        "prompt": p_text,
        "styleReference": "23-inventory.jpg",
        "guide": None,
        "requiredAlpha": True,
        "reviewStatus": "UNVERIFIED",
        "attempt": 1,
        "requestedOutputs": 1,
        "reviewCriteria": f"Canonical artifact {aname}, distinctive silhouette, crisp period materials, clean magenta background.",
        "styleReferenceSHA256": INVENTORY_SHA,
        "promptSHA256": digest(p_text),
        "guideSHA256": None
    })

# 5 Canonical Missing Spell Effects
spells = [
    ("effect-spell-fireball", "Fireball Spell Effect", "roaring flame sphere projectile, radial fiery impact blast wave, burning ember smoke, and blazing impact crater"),
    ("effect-spell-slow", "Slow Debuff Spell Effect", "swirling icy chronomancy ripples, viscous freezing mud ripples, frost crystal snares, and temporal sludge tentacles"),
    ("effect-spell-cure", "Cure Healing Spell Effect", "blooming emerald green curative lotus blossoms, radiant healing dew droplets, soothing leaf swirls, and sacred green light halo"),
    ("effect-spell-haste", "Haste Buff Spell Effect", "whirlwind sonic acceleration ribbons, golden speed blur trails, winged swiftness crest, and kinetic shock aura"),
    ("effect-spell-bless", "Bless Holy Spell Effect", "radiant golden celestial sunburst rays, glowing golden halos, sacred holy dove embers, and divine blessing sparkles")
]

for sid, sname, sdesc in spells:
    p_text = f"ONE production image for Ages of Dominion. Semi-realistic dense rendered strategy-game materials, warm upper-left daylight, short soft contact shadows. NO text, HUD, buttons, labels, numbers, device frame, watermark, or invented names. Isolated object on pure magenta #FF00FF background. No floor, no background shadow. ONE combat spell effects sprite sheet for Ages of Dominion: {sname}. {sdesc}. Four cleanly separated texture quadrants for game animation. Pure flat magenta #FF00FF backdrop, no text."
    b17_items.append({
        "position": len(b17_items) + 1,
        "id": sid,
        "kind": "effect",
        "mode": None,
        "age": "all",
        "aspect": "1:1",
        "prompt": p_text,
        "styleReference": "21-spells.jpg",
        "guide": None,
        "requiredAlpha": True,
        "reviewStatus": "UNVERIFIED",
        "attempt": 1,
        "requestedOutputs": 1,
        "reviewCriteria": f"Combat spell sheet for {sname}, 4 clean quadrants, pure magenta background.",
        "styleReferenceSHA256": SPELLS_SHA,
        "promptSHA256": digest(p_text),
        "guideSHA256": None
    })

# 5 Creature / Mount Rig Attachments
creature_mounts = [
    ("creature-dire-wolf", "creature", "all", "Dire Wolf Beast Unit", "ferocious giant grey dire wolf stalking forward with bared fangs, thick bristling fur, and predatory posture, high aerial three-quarter tactical view"),
    ("creature-cave-bear", "creature", "all", "Cave Bear Beast Unit", "massive grizzly cave bear rearing with armored leather chest strapping and heavy claws, high aerial three-quarter tactical view"),
    ("mount-saddle-harness-horse", "mount", "all", "Equestrian Warhorse Saddle and Harness Plate", "ornate tooled leather warhorse saddle, iron stirrups, studded leather bridle, and riveted barding breastplate strap assembly"),
    ("mount-saddle-harness-motor", "mount", "industrial", "Industrial Motorcycle Saddle and Controls Plate", "molded brown leather motorcycle solo seat, chrome fuel tank mounting bracket, handlebars, and exhaust manifold harness"),
    ("mount-saddle-harness-future", "mount", "future", "Future Repulsorcraft Pilot Console and Harness Plate", "ergonomic composite flight bucket saddle, holographic HUD avionics console, and magnetic repulsor stabilizer clamps")
]

for cid, ckind, cage, cname, cdesc in creature_mounts:
    p_text = f"ONE production image for Ages of Dominion. Semi-realistic dense rendered strategy-game materials, warm upper-left daylight, short soft contact shadows, coherent camera, high aerial three-quarter view. NO text, HUD, buttons, labels, numbers, device frame, watermark, or invented names. ONE photoreal isolated strategy unit asset for Ages of Dominion: {cname}. {cdesc}. Grounded on pure flat magenta #FF00FF background, no floor, no shadows on backdrop, no text."
    b17_items.append({
        "position": len(b17_items) + 1,
        "id": cid,
        "kind": ckind,
        "mode": "tactical" if ckind == "creature" else None,
        "age": cage,
        "aspect": "1:1",
        "prompt": p_text,
        "styleReference": "18-defense-wave.jpg",
        "guide": None,
        "requiredAlpha": True,
        "reviewStatus": "UNVERIFIED",
        "attempt": 1,
        "requestedOutputs": 1,
        "reviewCriteria": f"{cname} identity, clean silhouette, rich materials, clean magenta background.",
        "styleReferenceSHA256": WAVE_SHA,
        "promptSHA256": digest(p_text),
        "guideSHA256": None
    })

assert len(b17_items) == 30, f"b17 items count: {len(b17_items)}"

# Helper to write manifest
def save_manifest(num, items):
    manifest = {
        "id": f"production-{num:02d}-20261003",
        "model": "gemini-3.1-flash-image",
        "project": "project-eaa4c1cc-8f19-4d24-9e6",
        "region": "global",
        "count": 30,
        "status": "PREPARED_READY_FOR_SUBMISSION",
        "items": items,
        "maxOutputTokens": 4096,
        "inputTokenUpperBoundPerRequest": 12000,
        "reservedUSD": 6,
        "pricingSources": [
            "https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing",
            "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/batch-inference",
            "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/3-1-flash-image"
        ]
    }
    p = PLAN / f"batch-{num:02d}-manifest.json"
    p.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding='utf-8')
    print(f"Wrote batch-{num:02d}-manifest.json ({len(items)} items)")

save_manifest(14, b14_items)
save_manifest(15, b15_items)
save_manifest(16, b16_items)
save_manifest(17, b17_items)

print("All 4 manifests written successfully!")
