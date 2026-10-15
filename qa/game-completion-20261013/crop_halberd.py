"""Guess the knight halberd box from the bottom-left quadrant."""
from pathlib import Path
from PIL import Image, ImageDraw

root = Path(__file__).resolve().parents[2]
image = Image.open(root / "assets/delivery/stone-starter-20261003/derivatives/v2/live/rigs/knight.png").convert("RGBA")
boxes = {
    "a": (250, 580, 240, 160),
    "b": (300, 640, 200, 180),
    "c": (80, 700, 400, 220),
    "d": (180, 620, 300, 200),
    "foot-large": (913, 915, 92, 64),
    "foot-mid": (683, 919, 90, 58),
}
tiles = []
for name, (x, y, w, h) in boxes.items():
    crop = image.crop((x, y, x + w, y + h))
    scale = max(1, int(200 / max(w, h)))
    tile = crop.resize((w * scale, h * scale), Image.Resampling.NEAREST)
    canvas = Image.new("RGBA", (tile.width + 8, tile.height + 18), (0, 0, 0, 255))
    canvas.paste(tile, (4, 16), tile)
    ImageDraw.Draw(canvas).text((4, 2), name, fill=(232, 220, 190, 255))
    tiles.append(canvas)
width = sum(tile.width for tile in tiles)
height = max(tile.height for tile in tiles)
sheet = Image.new("RGBA", (width, height), (0, 0, 0, 255))
cursor = 0
for tile in tiles:
    sheet.paste(tile, (cursor, 0))
    cursor += tile.width
path = Path(__file__).resolve().parent / "rig-crops" / "halberd-guess.png"
sheet.save(path)
print(path)
