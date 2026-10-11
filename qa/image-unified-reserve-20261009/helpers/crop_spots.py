"""Write tight black-flattened crops of the remaining spots."""
from __future__ import annotations

from PIL import Image

import process_local as pl

spots = [
    ("creature-wolf-spot.jpg", pl.OUT_ASSETS / "actors/creatures/creature-wolf.png", (340, 700, 580, 900)),
    ("brute-feet-spot.jpg", pl.OUT_ASSETS / "actors/attackers/attacker-stone-brute.png", (250, 620, 700, 860)),
    ("workshop-court-spot.jpg", pl.OUT_ASSETS / "environment/buildings/workshop-iron.png", (400, 450, 800, 800)),
    ("warlock-dust-spot.jpg", pl.OUT_ASSETS / "actors/bodies/class-warlock-standing-body.png", (850, 1750, 1600, 2048)),
]
for name, path, box in spots:
    image = Image.open(path).convert("RGBA")
    crop = image.crop(box)
    board = Image.new("RGBA", crop.size, (0, 0, 0, 255))
    board.alpha_composite(crop)
    board.convert("RGB").save(pl.QA / "review" / name, quality=90)
    print(name, crop.size)
