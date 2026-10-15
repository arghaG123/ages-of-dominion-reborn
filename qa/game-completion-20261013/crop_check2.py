"""Second visual check: sleeve split, healer torso, knight weapon quadrant."""
from pathlib import Path
from PIL import Image, ImageDraw

root = Path(__file__).resolve().parents[2]
out = Path(__file__).resolve().parent / "rig-crops"
healer = Image.open(root / "assets/delivery/stone-starter-20261003/derivatives/v2/live/rigs/healer.png").convert("RGBA")
knight = Image.open(root / "assets/delivery/stone-starter-20261003/derivatives/v2/live/rigs/knight.png").convert("RGBA")
boxes = {
    "healer-torso": healer.crop((559, 200, 559 + 214, 200 + 297)),
    "healer-sleeve-upper": healer.crop((24, 543, 24 + 67, 543 + 133)),
    "healer-sleeve-lower": healer.crop((24, 676, 24 + 67, 543 + 266)),
    "knight-bl": knight.crop((0, 512, 512, 1024)).resize((360, 360), Image.Resampling.BILINEAR),
    "knight-br": knight.crop((512, 512, 1024, 1024)).resize((360, 360), Image.Resampling.BILINEAR),
}
tiles = []
for name, crop in boxes.items():
    scale = 1 if max(crop.size) > 300 else max(1, int(220 / max(crop.size)))
    tile = crop.resize((crop.width * scale, crop.height * scale), Image.Resampling.NEAREST)
    canvas = Image.new("RGBA", (tile.width + 8, tile.height + 22), (0, 0, 0, 255))
    canvas.paste(tile, (4, 20), tile)
    ImageDraw.Draw(canvas).text((4, 2), name, fill=(232, 220, 190, 255))
    tiles.append(canvas)
width = sum(tile.width for tile in tiles)
height = max(tile.height for tile in tiles)
sheet = Image.new("RGBA", (width, height), (0, 0, 0, 255))
cursor = 0
for tile in tiles:
    sheet.paste(tile, (cursor, 0))
    cursor += tile.width
sheet.save(out / "crop-check-2.png")
print(out / "crop-check-2.png")
