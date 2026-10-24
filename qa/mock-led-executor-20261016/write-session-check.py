import json
from pathlib import Path

root = Path(__file__).resolve().parent
leaves = json.loads((root / "open-leaves-to-check.json").read_text(encoding="utf-8"))

STONE_SCENES = {
    "SCENE-KINGDOM-STONE",
    "SCENE-ADVENTURE-STONE",
    "SCENE-TACTICAL-STONE",
    "SCENE-DEFENSE-STONE",
}
SHOWN_SCREENS = {
    "kingdom", "adventure", "army", "war", "forge", "market",
    "tactical", "defense", "story", "settings", "help", "home", "hero",
}

def judge(leaf):
    lid = leaf["id"]
    typ = leaf["type"]
    text = f"{leaf.get('name') or ''} {leaf.get('outcome') or ''}".lower()
    if typ == "PHYSICAL_SCENE":
        if lid == "SCENE-KINGDOM-STONE":
            return "FAIL", "This session shows kingdom-stone-ground.png with bare plot rectangles and a full palisade while the alert says Walls level 1, Hall 1, 17 empty sites, day 1."
        if lid in STONE_SCENES:
            return "SHOWN_ONLY", "The Stone scene image for this mode was on screen. No route, deck, or footprint trace was measured in this session."
        return "NOT_REACHED", "The campaign stayed Stone Age day 1. This age's scene was not displayed."
    if typ == "CLASS_KIT_ROW":
        if lid.endswith("-STONE"):
            notes = {
                "KIT-KNIGHT-STONE": "Knight caption: the plate is medieval kit, not worn ancient gear. Empty slots stay empty.",
                "KIT-HEALER-STONE": "Healer caption: static pose, not a worn attachment.",
            }
            return "FAIL", notes.get(lid, "Caption: the era of this standing plate is unverified and it is not proof of worn gear.")
        return "NOT_REACHED", "Only the Stone ancient kit was opened. This later kit was not on screen."
    if typ == "PLAYER_JOURNEY":
        if lid == "J01":
            return "FAIL", "Day 1 Stone session is not the required sparse start: walls level 1, wood 210, stone 40, gold 150, and the plot rectangles are visible."
        return "NOT_REACHED", "The journey was not played in this session. Related screens were opened, and no journey result was produced."
    if typ == "MOCK_TARGET":
        if lid in ("M01", "M02"):
            return "FAIL", "Home used the kingdom ground, and the Day 1 kingdom still shows the plot rectangles and a built wall ring."
        return "SHOWN_ONLY", "A live screen was opened in this session. It was not held against this mock's pixels."
    if lid == "OC02":
        return "FAIL", "Alert: Hall 1, 17 empty, Walls level 1, day 1. Supplies are food 250, wood 210, stone 40, gold 150. Plot rectangles remain visible."
    if lid == "OC01":
        return "FAIL", "The opened kingdom, home, and hero screens do not match the finished mock look."
    if lid == "OC04":
        return "NOT_REACHED", "Only the four Stone mode images appeared. The other 28 scenes were not shown, and none were traced."
    if lid in ("OC05", "OC07", "OC08"):
        return "FAIL", "All eight classes were opened on the Stone kit. Knight is the wrong era, Healer is a static pose, the other plates say their era is unverified, and all six slots are empty."
    if lid in ("OC10", "OC11", "OC12", "OC13", "OC14", "OC15", "OC17", "OC18"):
        return "NOT_REACHED", "The entry screen was opened. The required play, later ages, or layout measurements were not completed in this session."
    seen = {
        "OWN-02": ("SHOWN_ONLY", "Kingdom, Adventure, and Tactical all opened. Tactical had no battle."),
        "OWN-03": ("SHOWN_ONLY", "War showed Campaign Siege, Tactical Duel, Endless, Skirmish, and Start challenge. None was started."),
        "OWN-07": ("SHOWN_ONLY", "The resume report credited 0m 0s and no production. No producer is built."),
        "OWN-08": ("SHOWN_ONLY", "Army shows Clubman, Slinger, and Heavy recruit buttons, plus a Future plate review. Age stayed Stone."),
        "OWN-09": ("SHOWN_ONLY", "Dire Wolf, Bandit, Cave Bear, Harpy, Stone Golem, Griffin, Wyvern, and Drone Swarm are listed. None was claimed."),
        "OWN-10": ("SHOWN_ONLY", "All nine skills are listed at 0/3. No point was spent."),
        "OWN-11": ("SHOWN_ONLY", "Eight spell names are listed. Wisdom is 0/3 and none was cast."),
        "OWN-13": ("SHOWN_ONLY", "Chapter I and six rivals are on the Story screen. No chapter was finished."),
        "OWN-14": ("SHOWN_ONLY", "Six quests and eight milestone buttons are listed as open. None was claimed."),
        "OWN-15": ("SHOWN_ONLY", "Market says it opens in the Bronze Age. Buy and sell buttons are visible and the age did not change."),
        "OWN-16": ("SHOWN_ONLY", "The tutorial says Next: Build a Lumber Camp, and Skip tutorial is available. The camp was not built."),
        "SYS-13": ("SHOWN_ONLY", "Stone draws 46 run segments, 4 corners, and 1 gate. Walls are level 1 on an empty day-1 town."),
        "SYS-14": ("FAIL", "Empty plots are still bare rectangles on kingdom-stone-ground.png while nothing is built."),
        "G02": ("FAIL", "Day 1 has Walls level 1, wood 210, and stone 40. The required start is walls 0 and 250/250/160/150."),
        "G04": ("SHOWN_ONLY", "Adventure shows saved movement 5 and Leave town. The party did not travel."),
        "G05": ("SHOWN_ONLY", "Tactical says no battle is open and gate strength is 580."),
        "G06": ("SHOWN_ONLY", "Defense is on the preparation screen. No wave was fought."),
        "G07": ("SHOWN_ONLY", "All five War choices are on screen. None was played."),
        "G09": ("SHOWN_ONLY", "Nine skills at 0/3 and eight spell names are visible. None was used."),
        "G11": ("SHOWN_ONLY", "Stone troops and eight creature names are listed. Capacity is 2/2 and Barracks is required."),
        "G12": ("SHOWN_ONLY", "Story is on Chapter I. The Future conclusion was not reached."),
        "G13": ("SHOWN_ONLY", "The market screen says it opens in the Bronze Age."),
        "G14": ("SHOWN_ONLY", "Skip tutorial is present. The anchored lumber-camp step was not completed."),
    }
    if lid in seen:
        return seen[lid]
    if typ == "MASTER_PLAN_STEP":
        return "NOT_REACHED", f"The ledger only says '{leaf.get('outcome')}'. This session did not verify that step."
    if "eight age" in text or ("future" in text and "conclusion" in text):
        return "NOT_REACHED", "Age stayed Stone. Advance age returned Town Hall level too low."
    if "wall" in text and "level 0" in text:
        return "FAIL", "Walls are level 1 and 46 run segments, 4 corners, and 1 gate are drawn."
    if any(k in text for k in ("worn", "equip", "forge", "six slot", "gear")):
        return "FAIL", "Forge says Armory required and the bag holds 0. All six hero slots are empty, with no worn art."
    if any(k in text for k in ("scene", "32")):
        return "NOT_REACHED", "Only Stone kingdom, adventure, tactical, and defense images were displayed."
    if any(k in text for k in ("journey", "natural", "pointer")):
        return "NOT_REACHED", "No full player journey was completed in this session."
    if any(k in text for k in ("class", "kit", "healer", "knight")):
        return "FAIL", "Eight Stone plates were shown, and their own captions reject era or worn-gear acceptance."
    return "NOT_REACHED", "This Stone day-1 session did not produce the required state."

rows = []
for leaf in leaves:
    verdict, reason = judge(leaf)
    rows.append({
        "id": leaf["id"],
        "type": leaf["type"],
        "name": leaf.get("name"),
        "verdict": verdict,
        "reason": reason,
    })

summary = {}
for row in rows:
    summary[row["verdict"]] = summary.get(row["verdict"], 0) + 1

out = {
    "session": "http://127.0.0.1:4517/",
    "checkedAt": "2026-10-17",
    "campaign": {
        "status": "Stone Age day 1",
        "alert": "Hall level 1, 17 of 17 sites empty, Walls level 1",
        "resources": {"food": 250, "wood": 210, "stone": 40, "gold": 150},
        "advanceAge": "Town Hall level too low",
        "hallUpgrade": "disabled, needs 30 stone",
    },
    "openedScreens": sorted(SHOWN_SCREENS),
    "openLeavesChecked": len(rows),
    "summary": summary,
    "leaves": rows,
}
(root / "session-check-263.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
print(len(rows), summary)
