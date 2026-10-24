import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / "qa/game-completion-20261020/visual-review/adventure-worlds-live-20261020"
CATALOG = ROOT / "src/data/adventure-worlds.json"
OUT = EVIDENCE / "all-12-campaign-worlds-contact.png"
WORLDS = json.loads(CATALOG.read_text(encoding="utf-8"))
CELL_W, IMAGE_H, CAPTION_H = 320, 180, 26
image = Image.new("RGB", (CELL_W * 4, (IMAGE_H + CAPTION_H) * 3), "#10171b")
draw = ImageDraw.Draw(image)
font_path = Path("C:/Windows/Fonts/seguisb.ttf")
font = ImageFont.truetype(str(font_path), 13) if font_path.exists() else ImageFont.load_default()

for index, world in enumerate(WORLDS):
    row, column = divmod(index, 4)
    x, y = column * CELL_W, row * (IMAGE_H + CAPTION_H)
    capture = Image.open(EVIDENCE / f"picker-{world['id']}-1280x720.png").convert("RGB")
    capture = capture.resize((CELL_W, IMAGE_H), Image.Resampling.LANCZOS)
    image.paste(capture, (x, y))
    draw.rectangle((x, y, x + CELL_W - 1, y + IMAGE_H - 1), outline="#a98a55", width=1)
    draw.text((x + 8, y + IMAGE_H + 5), f"{index + 1:02d}  {world['title']}", fill="#f4e8d0", font=font)

image.save(OUT, optimize=True)
print(OUT)
