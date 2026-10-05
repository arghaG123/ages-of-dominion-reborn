"""Repairs and binds all 73 request packs with role-specific prompts and layouts.

Creates dated execution manifest:
docs/plan/IMAGE-LATER73-EXECUTION-MANIFEST-2026-10-04.json

Preserves prior prep-only history, binds real references, corrects:
- knight-mounted-master rider + horse composite.
- Mounts/transports intact limbs/wheels and saddle/rider anchors.
- Rig sheets separated part rectangles and margins for 2D animation mesh.
- Rivals individual identities (Aldric, Corvus, Kane, Morgana, Theron, Valeria).
- Army masters specific era names and roles (Clubman, Axeman, Legionary, Man-at-Arms, etc.).
"""

from pathlib import Path
import json
import hashlib

ROOT = Path("c:/dev/ages-of-dominion-reborn")
PACKS_ROOT = ROOT / "assets/high-res/later73-preparation-packs"
PREP_MANIFEST = ROOT / "docs/plan/IMAGE-LATER73-LOCAL-PREPARATION-MANIFEST-2026-10-04.json"
EXEC_MANIFEST = ROOT / "docs/plan/IMAGE-LATER73-EXECUTION-MANIFEST-2026-10-04.json"

HERO_DESCRIPTIONS = {
    # Ancient
    "portrait-ancient-ranger": "Prehistoric ranger and scout in natural leather tunic, horn-strung hunting bow, feathered headband, quiver of flint-tipped arrows, agile alert posture.",
    "portrait-ancient-warlock": "Shamanic mystic in ritual wolf pelt mantle, bone beads, holding a carved runic wooden totem staff, glowing amber eyes, dark smoke wisps.",
    "portrait-ancient-mage": "Elder elementalist in braided wild grass mantle with polished obsidian focus stone, ancient scrolls, subtle arcane spark illumination.",
    "portrait-ancient-paladin": "Dawn-warden holy champion in hammered bronze-banded cuirass, sun-embossed circular shield, sturdy stone mace, noble resolute gaze.",
    "portrait-ancient-barbarian": "Ferocious tribal berserker with primal ochre war paint, massive two-handed flint greataxe, mammoth hide wraps, roaring battle posture.",
    "portrait-ancient-necromancer": "Bone-keeper sorcerer in blackened rawhide cowl, carrying fossilized animal skull talisman, dark bone wand, pale spectral aura.",
    "portrait-ancient-healer": "Herbalist warden in verdant moss-embroidered tunic, woven pouch belt with medicinal roots, holding a flowering birch staff.",
    # Medieval
    "portrait-medieval-knight": "Chivalric champion in full fluted steel plate armor, emblazoned heraldic tabard, visored bascinet helm, steel longsword at side.",
    "portrait-medieval-ranger": "Woodland master archer in green wool doublet and reinforced leather vambraces, yew longbow, quiver of bodkin arrows, keen eyes.",
    "portrait-medieval-warlock": "Cursed occultist in dark velvet robes embroidered with astrological sigils, holding iron-clasped grimoire and carved ritual dagger.",
    "portrait-medieval-mage": "High wizard in royal indigo robes with gold filigree trim, crowned with crystalline circlet, holding towering spire staff.",
    "portrait-medieval-paladin": "Order templar in radiant silver plate armor over white tabard with crimson cross, holy warhammer, heavy heater shield.",
    "portrait-medieval-barbarian": "Highland raider in studded leather harness and heavy fur cloak, spiked iron pauldrons, wielding two-handed executioner broadsword.",
    "portrait-medieval-necromancer": "Plague scholar in dark hooded mantle, vial bandolier of dark elixirs, necrotic tome and crescent sickle, eerie green soul-light.",
    "portrait-medieval-healer": "Cloistered sanctuary cleric in embroidered linen vestments, silver chalice, soothing holy golden aura and carved prayer beads.",
    # Gunpowder
    "portrait-powder-knight": "Cuirassier cavalry officer in burnished steel breastplate over royal blue coat, tricorn hat, cavalry saber and flintlock pistol.",
    "portrait-powder-ranger": "Frontiersman scout in buckskin coat with long-barrel flintlock rifle, horn flask, coonskin cap, eagle eye sight.",
    "portrait-powder-warlock": "Alchemical conjurer in Victorian frock coat with smoke vials, brass alembic focus, dark alchemical vapors swirling about.",
    "portrait-powder-mage": "Renaissance magus in ornate silk waistcoat, brass sextant and astrolabe focus, crackling electrical voltaic sparks.",
    "portrait-powder-paladin": "Field marshal warden in gilded uniform jacket with sash, dress rapier, and radiant blessed lantern.",
    "portrait-powder-barbarian": "Revolutionary shock assault brawler with heavy bearded boarding axe, scarred bare arms, crossed bandoliers of powder flasks.",
    "portrait-powder-necromancer": "Galvanist reanimator in stained leather apron, lightning electrode rod, surgical saw, crackling arcs of reanimation energy.",
    "portrait-powder-healer": "Field surgeon medic in clean white coat with medical sash, apothecary satchel, surgical instruments, and restorative salves.",
    # Mech
    "portrait-mech-knight": "Cybernetic vanguard in kinetic composite exoskeleton armor, integrated hard-light energy shield generator, glowing plasma broadsword.",
    "portrait-mech-ranger": "Recon scout in active-camo hooded stealth armor with thermal optics visor, modular magnetic railgun sniper rifle.",
    "portrait-mech-warlock": "Void hacker in carbon-fiber trenchcoat with glowing sub-dermal cyberware circuits, floating holographic data glyphs.",
    "portrait-mech-mage": "Energy manipulator in sleek conduit jumpsuit with glowing plasma arcs encircling wrist gauntlets, hovering tech drones.",
    "portrait-mech-paladin": "Heavy aegis sentinel in powered titanium alloy heavy plate, reinforced energy tower shield, heavy hydraulic stun maul.",
    "portrait-mech-barbarian": "Cyber-enhanced brawler with exposed hydraulic pneumatic arm implants, heavy industrial plasma slag-axe, glowing cybernetic eye.",
    "portrait-mech-necromancer": "Corrupt nanite weaver in dark nano-fiber robes, swirling swarm of glowing purple nanite tendrils and cyber-scythe.",
    "portrait-mech-healer": "Nanotech medical officer in clean white combat medic carapace, medical drone hovering on shoulder, dermal laser regenerator."
}

RIVAL_DESCRIPTIONS = {
    "rival-identity-1": "Lord Aldric the Steadfast: stern feudal rival baron in ornate damascened plate armor with fur mantle and heavy gold signet ring, powerful commanding expression, era-appropriate noble regalia.",
    "rival-identity-2": "Arch-Warlock Corvus: shadowy rival sorcerer in raven-feathered cowl with obsidian staff and glowing amethyst eyes, ruthless calculating expression.",
    "rival-identity-3": "Ironmaster Kane: ruthless industrial rival magnate in soot-stained wool coat with leather gloves and brass pocket watch, sharp hawkish gaze.",
    "rival-identity-4": "Enchantress Morgana: mystical rival seeress in flowing silk robes with crystal pendulum and arcane celestial charts, enigmatic haughty expression.",
    "rival-identity-5": "Commander Theron: scarred veteran rival warlord in battle-tested iron breastplate with heavy broadsword at hip, weathered intimidating battle face.",
    "rival-identity-6": "Lady Valeria the Cunning: calculating rival noblewoman diplomat in dark velvet gown embroidered with gold, holding a cipher letter, poised aristocratic smile."
}

MOUNTS_DESCRIPTIONS = {
    "hero-mount-horse": "War horse mount master: muscular destrier steed with intact limbs, sturdy hooves, ornate leather saddle, bridle and stirrup harness with visible rider attachment point.",
    "hero-mount-motor-transport": "Tactical motorized combat transport: rugged mechanical chassis with intact treaded wheels, handlebars, cushioned saddle seat, exhaust, and rider anchor points.",
    "hero-mount-future-transport": "Future anti-gravity assault transport: streamlined aerodynamic hover skimmer with glowing repulsor emitters, lateral steering fins, cockpit saddle seat anchor."
}

ARMY_DESCRIPTIONS = {
    # Stone
    "troop-stone-melee": "Stone Age Clubman: primitive tribal warrior wielding flint/stone club and animal hide wrap, grounded combat posture.",
    "troop-stone-ranged": "Stone Age Slinger: prehistoric skirmisher with leather sling and pouch of river stones, pelt tunic, alert stance.",
    "troop-stone-heavy": "Stone Age Bone Crusher: massive brutish warrior with mammoth bone club and heavy hide mantle, imposing heavy silhouette.",
    # Bronze
    "troop-bronze-melee": "Bronze Age Axeman: warrior with cast bronze crescent axe, leather skirt and bronze-studded buckler, forward combat stance.",
    "troop-bronze-ranged": "Bronze Age Archer: composite bowman in linen cuirass with bronze-tipped arrows and leather quiver, drawing bow.",
    "troop-bronze-heavy": "Bronze Age Charioteer: heavy two-wheeled bronze-plated war chariot with pair of horses and spearman, dynamic combat charge.",
    # Iron
    "troop-iron-melee": "Iron Age Legionary: disciplined soldier with segmented iron lorica, scutum shield, and gladius sword, firm shield-wall posture.",
    "troop-iron-ranged": "Iron Age Crossbowman: marksman with iron-spanned gastraphetes crossbow and standing pavise shield, cocked aiming pose.",
    "troop-iron-heavy": "Iron Age War Elephant: armored pachyderm with iron tusk caps and howdah tower crew, commanding heavy presence.",
    # Medieval
    "troop-medieval-melee": "Medieval Man-at-Arms: armored footman with heater shield and steel broadsword in chainmail and heraldic surcoat.",
    "troop-medieval-ranged": "Medieval Longbowman: yew longbow archer with quiver of bodkin arrows, padded gambeson, steady aim.",
    "troop-medieval-heavy": "Medieval Siege Knight: heavily barded warhorse with knight in fluted full plate armor wielding heavy couched lance.",
    # Gunpowder
    "troop-gunpowder-melee": "Gunpowder Grenadier: soldier in mitre cap with matchlock carbine, saber, and fuse grenades ready to throw.",
    "troop-gunpowder-ranged": "Gunpowder Musketeer: flintlock musket soldier with bandolier of wooden powder charges, feathered hat, firing line stance.",
    "troop-gunpowder-heavy": "Gunpowder Cannon Crew: heavy wheeled bronze field cannon on oak carriage with artillerist holding lighted linstock.",
    # Industrial
    "troop-industrial-melee": "Industrial Rifleman: soldier in wool service uniform with bolt-action rifle, bayonet, and trench spade, ready stance.",
    "troop-industrial-ranged": "Industrial Sharpshooter: scout with scoped precision rifle, camouflaged ghillie cape, prone or kneeling aim.",
    "troop-industrial-heavy": "Industrial Steam Walker: iron-plated bipedal boiler-driven combat walker with pneumatic cannon and exhaust stack.",
    # Modern
    "troop-modern-melee": "Modern Assault Trooper: urban combat operator with composite tactical body armor, helmet, and automatic rifle.",
    "troop-modern-ranged": "Modern Marksman: precision marksman with suppressed high-caliber anti-material rifle and bipod, tactical optics.",
    "troop-modern-heavy": "Modern Battle Tank: main battle tank with composite reactive armor, 120mm smoothbore cannon, and armored treads.",
    # Future
    "troop-future-melee": "Future Plasma Trooper: powered exoskeleton warrior with plasma energy blade and hard-light barrier arm shield.",
    "troop-future-ranged": "Future Laser Sniper: stealth cybernetic operative with focused continuous-beam particle sniper rifle, glowing visor.",
    "troop-future-heavy": "Future Hover Tank: grav-lift armored heavy assault skimmer with twin heavy railguns and glowing energy shield."
}

RIG_PARTS = [
    {"id": "head", "rect": [896, 64, 256, 256]},
    {"id": "torso", "rect": [864, 384, 320, 480]},
    {"id": "arm_l", "rect": [480, 384, 256, 448]},
    {"id": "arm_r", "rect": [1312, 384, 256, 448]},
    {"id": "leg_l", "rect": [640, 960, 256, 640]},
    {"id": "leg_r", "rect": [1152, 960, 256, 640]},
    {"id": "weapon", "rect": [256, 896, 320, 896]},
    {"id": "accessory", "rect": [1472, 896, 320, 640]},
]

def sha256_str(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def build_role_prompt(item_id: str, group: str) -> tuple[str, dict]:
    """Builds specific, rich prompt and layout for each item."""
    if item_id == "knight-mounted-master":
        prompt = (
            "Produce ONE native 2K character illustration for knight-mounted-master. "
            "High aerial three-quarter full-body mounted hero portrait: Knight hero firmly seated in saddle upon a sturdy war horse, "
            "confident noble facial expression, recognizable hero identity, ancient stone hide and reinforced gear, "
            "naturally grounded hooves, detailed saddle and harness attachments. "
            "Upper-left directional key lighting, dark textured atmospheric background, clean intact silhouette, "
            "clear 6-slot equipment visibility. Deliver ONE 2048x2048 PNG image."
        )
        layout = {
            "canvas": [2048, 2048],
            "framing": "mounted rider and horse hero portrait",
            "focalCenter": [1024, 950],
            "silhouettePaddingPx": 96,
            "lighting": "upper-left directional key light with subtle rim",
            "consumer": "Hero/Equipment character sheet and Adventure map avatar",
            "anchors": {"riderSaddle": [1024, 880], "groundPivot": [1024, 1850]}
        }
    elif item_id in HERO_DESCRIPTIONS:
        desc = HERO_DESCRIPTIONS[item_id]
        prompt = (
            f"Produce ONE native 2K character illustration for {item_id}. "
            f"Full-body high-fidelity portrait of the hero: {desc} "
            f"Upper-left key lighting, dark textured atmospheric background, clean intact silhouette. "
            f"Preserve hero facial identity, anatomy proportions, and 6-slot equipment visibility. "
            f"Deliver ONE 2048x2048 PNG image."
        )
        layout = {
            "canvas": [2048, 2048],
            "framing": "full-body character portrait",
            "focalCenter": [1024, 900],
            "silhouettePaddingPx": 96,
            "lighting": "upper-left directional key light with subtle rim",
            "consumer": "Hero/Equipment character sheet and Adventure map avatar"
        }
    elif item_id in RIVAL_DESCRIPTIONS:
        desc = RIVAL_DESCRIPTIONS[item_id]
        prompt = (
            f"Produce ONE native 2K faction rival portrait for {item_id}. "
            f"Expressive high-detail bust-to-waist portrait capturing character personality: {desc} "
            f"Rich dramatic upper-left lighting, dark textured atmospheric background, intact silhouette, "
            f"distinctive noble regalia and rival allegiance crest. "
            f"Deliver ONE 2048x2048 PNG image."
        )
        layout = {
            "canvas": [2048, 2048],
            "framing": "bust and waist rival portrait with crest insignia",
            "focalCenter": [1024, 800],
            "silhouettePaddingPx": 96,
            "lighting": "dramatic upper-left key light with rim contrast",
            "consumer": "Campaign rival portrait and diplomatic encounter dialogue"
        }
    elif item_id in MOUNTS_DESCRIPTIONS:
        desc = MOUNTS_DESCRIPTIONS[item_id]
        prompt = (
            f"Produce ONE native 2K mount master illustration for {item_id}. "
            f"Anatomically correct mount/vehicle master: {desc} "
            f"Clean intact silhouette on neutral untextured background, three-quarter isometric profile, "
            f"consistent upper-left lighting, intact limbs and wheels, visible rider seat anchor. "
            f"Deliver ONE 2048x2048 PNG image."
        )
        layout = {
            "canvas": [2048, 2048],
            "framing": "isometric profile mount with rider saddle anchor",
            "saddleAnchor": [1024, 850],
            "silhouettePaddingPx": 96,
            "lighting": "isometric 3/4 light from upper-left",
            "consumer": "Mounted travel and tactical unit composite base"
        }
    elif item_id.startswith("rig-source-parts-"):
        hero_class = item_id.replace("rig-source-parts-", "")
        prompt = (
            f"Produce ONE native 2K multi-part articulation sheet for {item_id} ({hero_class} class). "
            f"Contains clearly separated anatomical components arranged in non-overlapping layout: "
            f"head, torso, left arm, right arm with weapon hand, left leg, right leg, primary weapon, offhand accessory. "
            f"Clean untextured neutral background (#FF00FF or neutral grey) with distinct 32px margins between parts for skeletal rigging. "
            f"Consistent {hero_class} class identity, color palette, and materials across all parts. "
            f"Deliver ONE 2048x2048 PNG image."
        )
        layout = {
            "canvas": [2048, 2048],
            "framing": "articulation part atlas with 32px part separation",
            "parts": RIG_PARTS,
            "partSeparationPx": 32,
            "consumer": "2D skeletal / frame animation inputs for Code AI"
        }
    elif item_id in ARMY_DESCRIPTIONS:
        desc = ARMY_DESCRIPTIONS[item_id]
        prompt = (
            f"Produce ONE native 2K army unit master sheet for {item_id}. "
            f"Accurate military combat unit depicting correct period armament: {desc} "
            f"Isolated full-figure silhouette on neutral ground, suitable for sprite extraction and tactical token generation. "
            f"Maintain strict historical/fantasy role fidelity, clear silhouette, upper-left daylight. "
            f"Deliver ONE 2048x2048 PNG image."
        )
        layout = {
            "canvas": [2048, 2048],
            "framing": "standing/combat isometric unit presentation",
            "focalCenter": [1024, 1100],
            "silhouettePaddingPx": 80,
            "lighting": "isometric 3/4 light from upper-left",
            "consumer": "Army / Tactical / Defense unit sprite and token master"
        }
    else:
        raise ValueError(f"Unmapped item: {item_id}")

    return prompt, layout

def main():
    prep_data = json.loads(PREP_MANIFEST.read_text(encoding="utf-8"))
    items = prep_data["items"]
    print(f"Loaded {len(items)} items from preparation manifest.")

    exec_items = []
    for it in items:
        cid = it["id"]
        gid = it["group"]
        order = it["order"]
        sources = it.get("sources", [])

        pack_dir = PACKS_ROOT / cid
        pack_dir.mkdir(parents=True, exist_ok=True)

        prompt_str, layout_dict = build_role_prompt(cid, gid)
        prompt_sha = sha256_str(prompt_str)

        # Write prompt.txt
        (pack_dir / "prompt.txt").write_text(prompt_str, encoding="utf-8")
        # Write layout_spec.json
        (pack_dir / "layout_spec.json").write_text(json.dumps(layout_dict, indent=2), encoding="utf-8")

        # Write request_meta.json
        req_meta = {
            "id": cid,
            "group": gid,
            "order": order,
            "model": "gemini-3.1-flash-image",
            "requestedSize": "2K",
            "dimensions": [2048, 2048],
            "purchaseStatus": "AUTHORIZED_QUEUED_ACTIVE_SCOPE",
            "paidCallsAllowed": True,
            "executionState": "READY_FOR_GENERATION",
            "prompt": prompt_str,
            "promptSHA256": prompt_sha,
            "sourceCandidates": sources,
            "layout": layout_dict,
            "consumerNeed": it.get("consumerNeed", ""),
            "reservationUSD": 0.143612
        }
        (pack_dir / "request_meta.json").write_text(json.dumps(req_meta, indent=2), encoding="utf-8")

        exec_item = {
            "group": gid,
            "order": order,
            "id": cid,
            "proposedResolution": "2K",
            "purchaseStatus": "AUTHORIZED_QUEUED_ACTIVE_SCOPE",
            "paidCallsAllowed": True,
            "executionState": "READY_FOR_GENERATION",
            "requestKind": it.get("requestKind", ""),
            "consumerNeed": it.get("consumerNeed", ""),
            "sources": sources,
            "localPackDir": f"assets/high-res/later73-preparation-packs/{cid}",
            "promptSHA256": prompt_sha,
            "layoutPrepared": True,
            "readinessStatus": "READY_FOR_INDIVIDUAL_GENERATION",
            "reservationUSD": 0.143612
        }
        exec_items.append(exec_item)

    exec_manifest_data = {
        "version": "1.0-execution-20261004",
        "scope": "Authorized Later 73 Native 2K Generation Queue",
        "authority": "Owner Start Instruction 2026-10-04 (20s pacing, >=60s 429 retry)",
        "count": len(exec_items),
        "counts": {
            "2K-LATER-A-HERO-32": 32,
            "2K-LATER-B-MOUNTS-RIGS-RIVALS-17": 17,
            "2K-LATER-C-ARMY-24": 24
        },
        "budgetBounds": {
            "boundPerRequestUSD": 0.143612,
            "totalQueueReservationUSD": round(len(exec_items) * 0.143612, 6),
            "retainedPriorExposureUSD": 62.8496,
            "totalCommittedUSD": round(62.8496 + len(exec_items) * 0.143612, 4),
            "hardCapUSD": 80.0,
            "headroomUSD": round(80.0 - (62.8496 + len(exec_items) * 0.143612), 4),
            "protectedReserveUSD": 15.0
        },
        "pacingPolicy": {
            "successPacingSeconds": 20.0,
            "quota429BackoffSeconds": 60.0
        },
        "items": exec_items
    }

    EXEC_MANIFEST.write_text(json.dumps(exec_manifest_data, indent=2), encoding="utf-8")
    print(f"Successfully repaired all 73 packs and created {EXEC_MANIFEST}!")

if __name__ == "__main__":
    main()
