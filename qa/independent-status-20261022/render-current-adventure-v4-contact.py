from hashlib import sha256
from pathlib import Path
import json

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
WORLDS = json.loads((ROOT / "src/data/adventure-worlds.json").read_text(encoding="utf-8"))
EVIDENCE = ROOT / "qa/game-completion-20261022/visual-review/adventure-map-source-reconciliation-20261022"
OUT = EVIDENCE / "adventure-map-production-geometry-v4-contact.png"
INDIVIDUAL_DIR = EVIDENCE / "production-geometry-v4-overlays"
TILE_W, TILE_H, TITLE_H = 688, 387, 30
COLS, ROWS, GAP = 3, 4, 10
FONT = ImageFont.load_default()
BACKGROUND = (13, 18, 22)
SITE_COLORS = {
    "town": (255, 211, 93), "ruin": (255, 93, 110), "mill": (74, 196, 255),
    "mine": (218, 137, 255), "dwelling": (101, 231, 153), "shrine": (255, 131, 214),
}
MASK_COLORS = {
    "water": (58, 162, 255, 72), "bog": (157, 164, 72, 80),
    "lava": (255, 79, 38, 95), "cliff": (218, 225, 231, 55),
}
ANCHOR_COLORS = {
    "hero": (245, 248, 255), "food": (107, 226, 127), "wood": (89, 207, 190),
    "stone": (173, 190, 206), "gold": (255, 207, 55),
    "guard-ruin": (255, 77, 80), "guard-mine": (255, 77, 80),
}


def xy(point, geometry):
    source_w, source_h = geometry["sourceSize"]
    a, _, _, d, _, _ = geometry["worldToSource"]
    return point[0] * a / source_w * TILE_W, point[1] * d / source_h * TILE_H


def box(cell, geometry):
    x, y = cell
    return (*xy((x, y), geometry), *xy((x + 1, y + 1), geometry))


canvas = Image.new(
    "RGB",
    (COLS * TILE_W + (COLS + 1) * GAP, ROWS * (TILE_H + TITLE_H) + (ROWS + 1) * GAP),
    BACKGROUND,
)
for index, world in enumerate(WORLDS):
    geometry = world["geometry"]
    assert geometry["version"] == 4, world["id"]
    assert geometry["sourceFile"] == world["productionMapFile"], world["id"]
    image_path = ROOT / world["productionMapFile"]
    assert sha256(image_path.read_bytes()).hexdigest() == geometry["sourceSha256"], world["id"]
    source = Image.open(image_path).convert("RGB")
    assert list(source.size) == geometry["sourceSize"], world["id"]
    base = source.resize((TILE_W, TILE_H), Image.Resampling.LANCZOS).convert("RGBA")
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    for kind, cells in geometry.get("terrainMasks", {}).items():
        fill = MASK_COLORS.get(kind)
        if fill:
            for cell in cells:
                draw.rectangle(box(cell, geometry), fill=fill)

    for road in geometry.get("roads", []):
        points = [xy((x + 0.5, y + 0.5), geometry) for x, y in road]
        if len(points) > 1:
            draw.line(points, fill=(241, 233, 196, 190), width=3)

    for crossing in geometry.get("bridges", []):
        for cell in crossing.get("cells", []):
            draw.rectangle(box(cell, geometry), fill=(37, 238, 234, 125), outline=(255, 255, 255, 240), width=2)

    for site in geometry.get("sites", []):
        x, y, w, h = site["rect"]
        x0, y0 = xy((x, y), geometry)
        x1, y1 = xy((x + w, y + h), geometry)
        color = SITE_COLORS[site["id"]]
        draw.rectangle((x0, y0, x1, y1), fill=(*color, 22), outline=(*color, 245), width=3)
        draw.text((x0 + 3, y0 + 3), site["id"], fill=(*color, 255), font=FONT, stroke_width=1, stroke_fill=(0, 0, 0, 230))
        ax, ay = xy((site["approach"][0] + 0.5, site["approach"][1] + 0.5), geometry)
        draw.ellipse((ax - 4, ay - 4, ax + 4, ay + 4), fill=(255, 255, 255, 245), outline=(*color, 255), width=2)

    for name, anchor in geometry.get("anchors", {}).items():
        color = ANCHOR_COLORS.get(name)
        if color:
            px, py = xy(anchor, geometry)
            radius = 5 if name == "hero" else 4
            draw.ellipse((px - radius, py - radius, px + radius, py + radius), fill=(*color, 255), outline=(5, 8, 11, 255), width=1)

    base = Image.alpha_composite(base, overlay).convert("RGB")
    INDIVIDUAL_DIR.mkdir(parents=True, exist_ok=True)
    base.save(INDIVIDUAL_DIR / f"{world['id']}-production-geometry-v4.png", optimize=True)
    row, col = divmod(index, COLS)
    left, top = GAP + col * (TILE_W + GAP), GAP + row * (TILE_H + TITLE_H + GAP)
    canvas.paste(base, (left, top + TITLE_H))
    title = f"{world['id']} | active geometry v4 | {Path(world['productionMapFile']).name}"
    ImageDraw.Draw(canvas).text((left + 3, top + 8), title, fill=(239, 233, 216), font=FONT)

EVIDENCE.mkdir(parents=True, exist_ok=True)
canvas.save(OUT, optimize=True)
print(OUT)
