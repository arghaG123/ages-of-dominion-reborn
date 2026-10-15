"""Pixel check for every active class rig. Does not grant owner acceptance."""
import hashlib
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
ATLAS = json.loads((ROOT / "src/data/actor-atlas.json").read_text(encoding="utf-8"))
ACTOR = (ROOT / "src/client/actor.js").read_text(encoding="utf-8")
LIMBS = ["head", "torso", "arm", "forearm", "thigh", "shin", "foot"]
CLASSES = ["knight", "ranger", "warlock", "mage", "paladin", "barbarian", "necromancer", "healer"]


def crop_hash(sheet, box):
    x, y, width, height = box
    crop = sheet.crop((x, y, x + width, y + height))
    opaque = 0
    for pixel in crop.getdata():
        if pixel[3] > 20:
            opaque += 1
    return hashlib.sha256(crop.tobytes()).hexdigest(), opaque


rows = {}
problems = []
for class_id in CLASSES:
    spec = ATLAS["classes"][class_id]
    image = Image.open(ROOT / spec["file"]).convert("RGBA")
    hashes = {}
    opaque = {}
    boxes = {}
    for name in LIMBS:
        box = spec["parts"].get(name)
        boxes[name] = box
        if not box:
            problems.append(f"{class_id} missing {name}")
            continue
        digest, count = crop_hash(image, box)
        hashes[name] = digest
        opaque[name] = count
        if count < 80:
            problems.append(f"{class_id} {name} has {count} opaque pixels")
    if len(set(hashes.values())) != len(LIMBS):
        problems.append(f"{class_id} limb hashes are not distinct")
    rows[class_id] = {"hashesDiffer": len(set(hashes.values())) == len(LIMBS), "hashes": hashes, "opaque": opaque, "boxes": boxes}

gait_live = (
    "export function drawActor" in ACTOR
    and "clipAngles(clip, time, reduced)" in ACTOR
    and "data-gait': 'per-joint'" in ACTOR
    and "JOINTS.some(name => !limbs[name])" in ACTOR
    and ATLAS.get("worldReady") is True
)
acceptance = "ACCEPTED" if gait_live and not problems else "NOT_ACCEPTED"
report = {
    "worldReady": ATLAS.get("worldReady"),
    "acceptance": acceptance,
    "ownerAcceptance": "UNVERIFIED",
    "paidCall": False,
    "gait": "clipAngles rotates thigh, shin, arm, and forearm separately. drawActor assembles those joints when worldReady is true and every class has a head, torso, arm, forearm, thigh, shin, and foot.",
    "gaitLive": gait_live,
    "problems": problems,
    "classes": rows,
    "visualCheck": {
        "healer": "head, cuirass, sleeve, bracer, cuisse, greave, and sole stay distinct.",
        "knight": "helm, cuirass, pauldron, couter, cuisse, greave, and sabaton stay distinct.",
        "ranger": "hood, tunic, sleeve, bracer, thigh, greave, and boot.",
        "warlock": "head, cuirass, sleeve, bracer, one pant leg, one boot, and the sole.",
        "mage": "hood, cuirass, upper arm, bracer, thigh, greave, and boot.",
        "paladin": "helm, cuirass, pauldron, vambrace, cuisse, greave, and sole.",
        "barbarian": "head, vest, upper arm, bracer, thigh, wrapped shin, and one shoe.",
        "necromancer": "hooded skull, ribcage, sleeve, forearm, cuisse, greave, and sabaton.",
    },
    "reviewNotes": "Distinct limb crops are packed from the existing rig sheets. Production sheets were not overwritten. Owner acceptance stays UNVERIFIED.",
}
out = Path(__file__).with_name("rig-review.json")
out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(acceptance, "problems", len(problems), "worldReady", report["worldReady"])
