import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
CATALOG = ROOT / "src/data/adventure-worlds.json"
CONTRACT = ROOT / "src/data/implementation-contract.json"
OUT = ROOT / "qa/game-completion-20261020/visual-review/owner-adventure-map-gallery-review-20261020/all-12-current-geometry-contact.png"
WORLDS = json.loads(CATALOG.read_text(encoding="utf-8"))
GEO = json.loads(CONTRACT.read_text(encoding="utf-8"))["geometry"]["adventure"]
MATRIX = GEO["worldToSource"]
CELL_W, IMAGE_H, CAPTION_H = 480, 270, 26
canvas = Image.new("RGB", (CELL_W * 4, (IMAGE_H + CAPTION_H) * 3), "#10171b")
font_path = Path("C:/Windows/Fonts/seguisb.ttf")
font = ImageFont.truetype(str(font_path), 15) if font_path.exists() else ImageFont.load_default()


def project(point):
    a, b, c, d, e, f = MATRIX
    x, y = point
    return (a * x + c * y + e, b * x + d * y + f)


for index, world in enumerate(WORLDS):
    row, column = divmod(index, 4)
    x, y = column * CELL_W, row * (IMAGE_H + CAPTION_H)
    base = Image.open(ROOT / world["file"]).convert("RGBA")
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    for bx, by in GEO.get("blocked", []):
        corners = [project((bx, by)), project((bx + 1, by)), project((bx + 1, by + 1)), project((bx, by + 1))]
        draw.polygon(corners, fill=(51, 142, 197, 44), outline=(121, 211, 255, 100))

    for road in GEO.get("roads", []):
        draw.line([project((px + 0.5, py + 0.5)) for px, py in road], fill=(255, 224, 103, 160), width=8, joint="curve")

    colors = {"town": (255, 96, 78, 95), "ruin": (222, 84, 74, 84), "mill": (222, 84, 74, 84), "mine": (222, 84, 74, 84), "dwelling": (222, 84, 74, 84), "shrine": (222, 84, 74, 84)}
    for site in GEO["sites"]:
        sx, sy, sw, sh = site["rect"]
        corners = [project((sx, sy)), project((sx + sw, sy)), project((sx + sw, sy + sh)), project((sx, sy + sh))]
        fill = colors.get(site["id"], (220, 84, 74, 84))
        draw.polygon(corners, fill=fill, outline=(255, 78, 66, 230), width=4)
        center = project((sx + sw / 2, sy + sh / 2))
        draw.text((center[0] + 4, center[1] - 12), site["id"], fill=(255, 248, 230, 255), font=font, stroke_width=2, stroke_fill=(20, 14, 12, 255))

    for gx in range(GEO["cols"] + 1):
        draw.line([project((gx, 0)), project((gx, GEO["rows"]))], fill=(255, 255, 255, 54), width=2)
    for gy in range(GEO["rows"] + 1):
        draw.line([project((0, gy)), project((GEO["cols"], gy))], fill=(255, 255, 255, 54), width=2)

    composed = Image.alpha_composite(base, overlay).convert("RGB").resize((CELL_W, IMAGE_H), Image.Resampling.LANCZOS)
    canvas.paste(composed, (x, y))
    draw_canvas = ImageDraw.Draw(canvas)
    draw_canvas.rectangle((x, y, x + CELL_W - 1, y + IMAGE_H - 1), outline="#a98a55", width=1)
    draw_canvas.text((x + 8, y + IMAGE_H + 4), f"{index + 1:02d}  {world['title']}", fill="#f4e8d0", font=font)

canvas.save(OUT, optimize=True)
print(OUT)
