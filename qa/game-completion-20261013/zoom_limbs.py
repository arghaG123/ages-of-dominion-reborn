"""Zoom the ambiguous source regions."""
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
SHEETS = ROOT / "assets/delivery/stone-starter-20261003/derivatives/v2/live/rigs"
OUT = Path(__file__).resolve().parent / "rig-crops" / "labeled"

regions = {
    "warlock-legs": ("warlock", [540, 540, 280, 420]),
    "warlock-arm": ("warlock", [80, 540, 160, 420]),
    "warlock-staff": ("warlock", [270, 540, 220, 420]),
    "paladin-arm": ("paladin", [70, 520, 360, 460]),
    "necro-arms": ("necromancer", [10, 520, 280, 480]),
    "necro-staff": ("necromancer", [250, 520, 250, 480]),
    "barb-feet": ("barbarian", [740, 900, 270, 110]),
    "barb-weapon": ("barbarian", [180, 840, 300, 160]),
    "paladin-legs": ("paladin", [540, 520, 460, 480]),
}
for name, (class_id, box) in regions.items():
    image = Image.open(SHEETS / f"{class_id}.png").convert("RGB")
    x, y, w, h = box
    crop = image.crop((x, y, x + w, y + h))
    scale = 2 if max(w, h) < 400 else 1
    if scale > 1:
        crop = crop.resize((w * scale, h * scale), Image.Resampling.NEAREST)
    draw = ImageDraw.Draw(crop)
    draw.text((4, 4), f"{name} origin {x},{y}", fill=(255, 220, 80))
    crop.save(OUT / f"{name}.png")
    print(name, crop.size)
