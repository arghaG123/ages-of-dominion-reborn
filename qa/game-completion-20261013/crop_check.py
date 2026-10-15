"""Save named crops from the live healer and knight sheets for a visual check."""
from pathlib import Path
from PIL import Image, ImageDraw

root = Path(__file__).resolve().parents[2]
out = Path(__file__).resolve().parent / "rig-crops"
sheets = {
    "healer": root / "assets/delivery/stone-starter-20261003/derivatives/v2/live/rigs/healer.png",
    "knight": root / "assets/delivery/stone-starter-20261003/derivatives/v2/live/rigs/knight.png",
}
boxes = {
    "healer-atlas-arm": ("healer", (854, 24, 146, 171)),
    "healer-atlas-forearm": ("healer", (556, 769, 70, 169)),
    "healer-atlas-weapon": ("healer", (267, 531, 223, 475)),
    "healer-atlas-head": ("healer", (342, 14, 147, 314)),
    "healer-pick-forearm": ("healer", (24, 543, 67, 266)),
    "healer-pick-arm": ("healer", (23, 810, 72, 129)),
    "knight-atlas-foot": ("knight", (855, 916, 53, 50)),
    "knight-atlas-weapon": ("knight", (20, 551, 95, 183)),
    "knight-atlas-head": ("knight", (33, 23, 116, 178)),
    "knight-pick-foot": ("knight", (879, 968, 40, 27)),
    "knight-pick-shin": ("knight", (567, 633, 80, 80)),
    "knight-pick-thigh": ("knight", (565, 551, 84, 81)),
}
tiles = []
for name, (sheet, (x, y, w, h)) in boxes.items():
    image = Image.open(sheets[sheet]).convert("RGBA")
    crop = image.crop((x, y, x + w, y + h))
    scale = max(1, int(180 / max(w, h)))
    tile = crop.resize((w * scale, h * scale), Image.Resampling.NEAREST)
    canvas = Image.new("RGBA", (tile.width + 8, tile.height + 28), (0, 0, 0, 255))
    canvas.paste(tile, (4, 24), tile)
    draw = ImageDraw.Draw(canvas)
    draw.text((4, 4), name, fill=(232, 220, 190, 255))
    tiles.append(canvas)
width = sum(tile.width for tile in tiles)
height = max(tile.height for tile in tiles)
sheet = Image.new("RGBA", (width, height), (0, 0, 0, 255))
cursor = 0
for tile in tiles:
    sheet.paste(tile, (cursor, 0))
    cursor += tile.width
sheet.save(out / "crop-check.png")
print(out / "crop-check.png")
