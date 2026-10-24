from pathlib import Path
import json

from PIL import Image, ImageDraw, ImageFont, ImageOps

root = Path(__file__).resolve().parents[3]
report_path = root / "qa/game-completion-20261020/visual-review/kingdom-live/natural-all-age-kingdom-live-20261020.json"
report = json.loads(report_path.read_text(encoding="utf-8"))
ages = []
for age in range(8):
    record = next(item for item in report["screenshots"] if item["scene"]["view"] == "adventure" and item["scene"]["terrainLoaded"] and item["captures"][0]["name"] == f"age-{age}-adventure")
    capture = next(item for item in record["captures"] if item["size"] == "1280x720")
    ages.append((report["ages"][age]["name"], root / capture["file"]))

tile_w, tile_h, label_h, gap, margin = 480, 270, 30, 10, 12
sheet = Image.new("RGB", (margin * 2 + 4 * tile_w + 3 * gap, margin * 2 + 2 * (tile_h + label_h) + gap), "#111820")
draw = ImageDraw.Draw(sheet)
font = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 18)
for index, (label, image_path) in enumerate(ages):
    column, row = index % 4, index // 4
    x = margin + column * (tile_w + gap)
    y = margin + row * (tile_h + label_h + gap)
    with Image.open(image_path) as source:
        tile = ImageOps.fit(source.convert("RGB"), (tile_w, tile_h), method=Image.Resampling.LANCZOS)
    sheet.paste(tile, (x, y))
    draw.text((x + 8, y + tile_h + 4), label, font=font, fill="#f2e5c8")

output = root / "qa/game-completion-20261020/visual-review/adventure-eight-ages-natural-1280x720-contact-20261020.jpg"
sheet.save(output, quality=92, optimize=True)
print(output)
