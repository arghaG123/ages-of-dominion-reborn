"""Save the proposed limb crops so each box can be checked by eye."""
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
SHEETS = ROOT / "assets/delivery/stone-starter-20261003/derivatives/v2/live/rigs"
OUT = Path(__file__).resolve().parent / "rig-crops" / "labeled" / "proposed.png"

PICKS = {
    "ranger": {
        "head": [184, 38, 139, 205],
        "torso": [562, 40, 386, 432],
        "arm": [38, 547, 77, 151],
        "forearm": [31, 703, 75, 188],
        "thigh": [570, 552, 84, 156],
        "shin": [572, 712, 68, 197],
        "foot": [779, 788, 92, 169],
        "weapon": [377, 531, 93, 472],
    },
    "warlock": {
        "head": [108, 227, 157, 245],
        "torso": [522, 54, 477, 311],
        "arm": [96, 559, 119, 377],
        "forearm": [180, 687, 215, 74],
        "thigh": [555, 556, 120, 180],
        "shin": [555, 736, 120, 202],
        "foot": [798, 780, 62, 144],
        "weapon": [380, 620, 90, 320],
    },
    "mage": {
        "head": [292, 44, 177, 223],
        "torso": [609, 47, 293, 413],
        "arm": [62, 557, 94, 187],
        "forearm": [195, 711, 154, 91],
        "thigh": [663, 544, 97, 178],
        "shin": [653, 728, 75, 163],
        "foot": [657, 894, 63, 79],
        "weapon": [350, 697, 86, 250],
    },
    "paladin": {
        "head": [80, 79, 147, 212],
        "torso": [557, 80, 181, 219],
        "arm": [85, 550, 107, 150],
        "forearm": [90, 708, 83, 79],
        "thigh": [559, 551, 105, 191],
        "shin": [572, 760, 82, 180],
        "foot": [717, 712, 129, 228],
        "altfoot": [858, 760, 78, 180],
        "altfore": [842, 548, 90, 196],
    },
    "barbarian": {
        "head": [30, 26, 140, 238],
        "torso": [557, 42, 209, 441],
        "arm": [42, 536, 63, 132],
        "forearm": [28, 668, 62, 110],
        "thigh": [556, 546, 86, 186],
        "shin": [912, 758, 88, 167],
        "foot": [766, 926, 120, 74],
        "altfoot": [890, 926, 120, 74],
        "weapon": [202, 862, 267, 116],
    },
    "necromancer": {
        "head": [368, 334, 110, 149],
        "torso": [652, 46, 204, 448],
        "arm": [31, 551, 132, 210],
        "forearm": [141, 552, 129, 211],
        "thigh": [880, 549, 112, 160],
        "shin": [880, 709, 112, 160],
        "foot": [880, 869, 112, 79],
        "altfoot": [830, 949, 106, 53],
        "weapon": [267, 700, 80, 280],
    },
}

names_order = []
cell = 150
rows = []
for class_id, parts in PICKS.items():
    image = Image.open(SHEETS / f"{class_id}.png").convert("RGBA")
    row = []
    for name, box in parts.items():
        x, y, w, h = box
        crop = image.crop((x, y, x + w, y + h))
        crop.thumbnail((cell - 8, cell - 22))
        row.append((f"{class_id} {name}", crop))
    rows.append(row)

width = max(len(row) for row in rows) * cell
height = len(rows) * cell
sheet = Image.new("RGB", (width, height), (20, 20, 20))
draw = ImageDraw.Draw(sheet)
for r, row in enumerate(rows):
    for c, (label, crop) in enumerate(row):
        ox, oy = c * cell + 4, r * cell + 16
        sheet.paste(crop, (ox, oy), crop)
        draw.text((c * cell + 4, r * cell + 2), label, fill=(240, 210, 150))
sheet.save(OUT)
print(OUT)
