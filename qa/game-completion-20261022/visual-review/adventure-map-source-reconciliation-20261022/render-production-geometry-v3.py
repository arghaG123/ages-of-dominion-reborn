from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
WORLDS = json.loads((ROOT / 'src/data/adventure-worlds.json').read_text(encoding='utf-8'))
ARCHIVE = json.loads((HERE / 'per-world-map-source-geometry-20261022.json').read_text(encoding='utf-8'))
GEOMETRIES = {row['id']: row['runtimeGeometryV3'] for row in ARCHIVE['worlds']}
FONT = ImageFont.load_default()
TILE_W, TILE_H, TITLE_H = 512, 288, 26
COLS, ROWS = 3, 4
GAP = 10
BACKGROUND = (13, 18, 22)
SITE_COLORS = {
    'town': (255, 211, 93), 'ruin': (255, 93, 110), 'mill': (74, 196, 255),
    'mine': (218, 137, 255), 'dwelling': (101, 231, 153), 'shrine': (255, 131, 214),
}
SITE_LABELS = {'town': 'TOW', 'ruin': 'RUI', 'mill': 'MIL', 'mine': 'MIN', 'dwelling': 'DWE', 'shrine': 'SHR'}
MASK_COLORS = {'water': (58, 162, 255, 84), 'bog': (157, 164, 72, 90), 'lava': (255, 79, 38, 110), 'cliff': (218, 225, 231, 70)}
ANCHOR_COLORS = {'hero': (245, 248, 255), 'food': (107, 226, 127), 'wood': (89, 207, 190), 'stone': (173, 190, 206), 'gold': (255, 207, 55), 'guard-ruin': (255, 77, 80), 'guard-mine': (255, 77, 80)}

def xy(point, geometry):
    source_w, source_h = geometry['sourceSize']
    a, _, _, d, _, _ = geometry['worldToSource']
    return (point[0] * a / source_w * TILE_W, point[1] * d / source_h * TILE_H)

def box(cell, geometry):
    x, y = cell
    x0, y0 = xy((x, y), geometry)
    x1, y1 = xy((x + 1, y + 1), geometry)
    return (x0, y0, x1, y1)

canvas = Image.new('RGB', (COLS * TILE_W + (COLS + 1) * GAP, ROWS * (TILE_H + TITLE_H) + (ROWS + 1) * GAP), BACKGROUND)
for index, world in enumerate(WORLDS):
    geometry = GEOMETRIES[world['id']]
    assert geometry['version'] == 3, world['id']
    assert geometry['sourceFile'] == world['productionMapFile'], world['id']
    image_path = ROOT / world['productionMapFile']
    base = Image.open(image_path).convert('RGB').resize((TILE_W, TILE_H), Image.Resampling.LANCZOS).convert('RGBA')
    overlay = Image.new('RGBA', base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    for kind, cells in geometry.get('terrainMasks', {}).items():
        fill = MASK_COLORS.get(kind)
        if not fill:
            continue
        for cell in cells:
            draw.rectangle(box(cell, geometry), fill=fill)

    for road in geometry.get('roads', []):
        points = [xy((x + 0.5, y + 0.5), geometry) for x, y in road]
        if len(points) > 1:
            draw.line(points, fill=(241, 233, 196, 168), width=2)

    for bridge in geometry.get('bridges', []):
        for cell in bridge.get('cells', []):
            draw.rectangle(box(cell, geometry), fill=(37, 238, 234, 145), outline=(255, 255, 255, 245), width=2)

    for site in geometry.get('sites', []):
        x, y, w, h = site['rect']
        x0, y0 = xy((x, y), geometry)
        x1, y1 = xy((x + w, y + h), geometry)
        color = SITE_COLORS[site['id']]
        draw.rectangle((x0, y0, x1, y1), fill=(*color, 26), outline=(*color, 245), width=3)
        draw.text((x0 + 2, y0 + 2), SITE_LABELS[site['id']], fill=(*color, 255), font=FONT, stroke_width=1, stroke_fill=(0, 0, 0, 220))
        ax, ay = xy((site['approach'][0] + 0.5, site['approach'][1] + 0.5), geometry)
        draw.ellipse((ax - 3.2, ay - 3.2, ax + 3.2, ay + 3.2), fill=(255, 255, 255, 240), outline=(*color, 255), width=2)

    for name, anchor in geometry.get('anchors', {}).items():
        px, py = xy(anchor, geometry)
        color = ANCHOR_COLORS.get(name)
        if not color:
            continue
        radius = 4 if name == 'hero' else 3
        draw.ellipse((px - radius, py - radius, px + radius, py + radius), fill=(*color, 255), outline=(5, 8, 11, 255), width=1)

    base = Image.alpha_composite(base, overlay).convert('RGB')
    row, col = divmod(index, COLS)
    left, top = GAP + col * (TILE_W + GAP), GAP + row * (TILE_H + TITLE_H + GAP)
    canvas.paste(base, (left, top + TITLE_H))
    title = f"{world['id']} | {world['title']} | {len(geometry.get('bridges', []))} crossings"
    ImageDraw.Draw(canvas).text((left + 2, top + 7), title, fill=(239, 233, 216), font=FONT)

output = HERE / 'adventure-map-production-geometry-v3-contact.png'
canvas.save(output, optimize=True)
print(output)
