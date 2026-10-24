import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[4]
WORLD_FILE = ROOT / "src/data/adventure-worlds.json"
CONTRACT_FILE = ROOT / "src/data/implementation-contract.json"
OUT = Path(__file__).resolve().parent
OUT.mkdir(parents=True, exist_ok=True)

worlds = json.loads(WORLD_FILE.read_text(encoding="utf-8"))
contract = json.loads(CONTRACT_FILE.read_text(encoding="utf-8"))
base = contract["geometry"]["adventure"]
width, height = base["sourceSize"]


def project(matrix, x, y):
    a, b, c, d, ox, oy = matrix
    return (ox + a * x + c * y, oy + b * x + d * y)


def merge_sites(world):
    authored = world.get("geometry", {})
    overrides = {row["id"]: row for row in authored.get("sites", [])}
    return [{**row, **overrides.get(row["id"], {})} for row in base["sites"]]


def render(world):
    authored = world.get("geometry", {})
    matrix = authored.get("worldToSource", base["worldToSource"])
    source = ROOT / world["mapFile"]
    image = Image.open(source).convert("RGBA").resize((width, height))
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    font = ImageFont.load_default()

    blocked = authored.get("blocked", [])
    for x, y in blocked:
        quad = [project(matrix, x, y), project(matrix, x + 1, y), project(matrix, x + 1, y + 1), project(matrix, x, y + 1)]
        draw.polygon(quad, fill=(26, 111, 170, 44), outline=(112, 218, 255, 145), width=1)

    for crossing in authored.get("bridges", []):
        for x, y in crossing.get("cells", []):
            quad = [project(matrix, x, y), project(matrix, x + 1, y), project(matrix, x + 1, y + 1), project(matrix, x, y + 1)]
            draw.polygon(quad, fill=(25, 184, 108, 76), outline=(139, 255, 185, 235), width=2)

    for x in range(base["cols"] + 1):
        draw.line([project(matrix, x, 0), project(matrix, x, base["rows"])], fill=(255, 255, 255, 94), width=1)
    for y in range(base["rows"] + 1):
        draw.line([project(matrix, 0, y), project(matrix, base["cols"], y)], fill=(255, 255, 255, 94), width=1)

    for site in merge_sites(world):
        x, y, w, h = site["rect"]
        quad = [project(matrix, x, y), project(matrix, x + w, y), project(matrix, x + w, y + h), project(matrix, x, y + h)]
        draw.polygon(quad, fill=(247, 190, 48, 28), outline=(255, 220, 105, 225), width=3)
        name = site["id"].title()
        px, py = project(matrix, x + w / 2, y + h)
        draw.text((px + 4, py + 2), name, font=font, fill=(255, 240, 184, 255), stroke_width=2, stroke_fill=(0, 0, 0, 220))

    colors = {
        "hero": (67, 195, 255, 255),
        "guard-ruin": (255, 91, 83, 255),
        "guard-mine": (255, 91, 83, 255),
        "food": (255, 235, 83, 255),
        "wood": (255, 235, 83, 255),
        "stone": (255, 235, 83, 255),
        "gold": (255, 235, 83, 255),
    }
    anchors = {**base["anchors"], **authored.get("anchors", {})}
    for name, (x, y) in anchors.items():
        px, py = project(matrix, x, y)
        color = colors.get(name, (240, 240, 240, 255))
        draw.ellipse((px - 7, py - 7, px + 7, py + 7), fill=color, outline=(15, 15, 15, 255), width=2)
        draw.text((px + 9, py - 14), name, font=font, fill=(255, 255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0, 220))

    output = OUT / f"{world['id']}-map-registration.png"
    Image.alpha_composite(image, overlay).convert("RGB").save(output, optimize=True)
    return output


outputs = [render(world) for world in worlds if world.get("mapFile")]
thumb_w, thumb_h = 520, 290
columns = 2
rows = (len(outputs) + columns - 1) // columns
contact = Image.new("RGB", (thumb_w * columns, thumb_h * rows), (18, 22, 24))
contact_draw = ImageDraw.Draw(contact)
for index, file in enumerate(outputs):
    thumbnail = Image.open(file).convert("RGB").resize((thumb_w, thumb_h))
    x = (index % columns) * thumb_w
    y = (index // columns) * thumb_h
    contact.paste(thumbnail, (x, y))
    contact_draw.rectangle((x, y, x + 150, y + 20), fill=(0, 0, 0))
    contact_draw.text((x + 5, y + 4), file.stem.replace("-map-registration", ""), fill=(255, 255, 255))

contact_path = OUT / "integrated-map-registration-contact.png"
contact.save(contact_path, optimize=True)
print(json.dumps({"maps": [str(path.relative_to(ROOT)) for path in outputs], "contact": str(contact_path.relative_to(ROOT))}))
