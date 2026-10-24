from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont

root = Path.cwd()
out = root / "qa/game-completion-20261021/visual-review/owner-map-source-grid-audit-20261021"
worlds = json.loads((root / "src/data/adventure-worlds.json").read_text(encoding="utf-8"))
wanted = {world["id"] for world in worlds}
font = ImageFont.load_default()
rows = []

for world in worlds:
    if world["id"] not in wanted:
        continue
    source = root / world["file"]
    image = Image.open(source).convert("RGBA")
    width, height = image.size
    cols, row_count = 16, 10
    cell_w, cell_h = width / cols, height / row_count
    geo = world["geometry"]
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")

    for x, y in geo.get("blocked", []):
        x0, y0 = round(x * cell_w), round(y * cell_h)
        x1, y1 = round((x + 1) * cell_w), round((y + 1) * cell_h)
        draw.rectangle((x0, y0, x1, y1), fill=(220, 35, 30, 95), outline=(255, 238, 215, 210), width=2)

    for obstacle in geo.get("obstacles", []):
        if isinstance(obstacle, dict):
            rect = obstacle.get("rect", [])
            if len(rect) != 4:
                continue
            x, y, w, h = rect
        elif isinstance(obstacle, (list, tuple)) and len(obstacle) == 2:
            x, y = obstacle
            w = h = 1
        else:
            continue
        box = (round(x * cell_w), round(y * cell_h), round((x + w) * cell_w), round((y + h) * cell_h))
        draw.rectangle(box, fill=(112, 48, 170, 80), outline=(227, 193, 255, 230), width=3)

    for bridge in geo.get("bridges", []):
        x, y, w, h = bridge.get("rect", [0, 0, 1, 1])
        box = (round(x * cell_w), round(y * cell_h), round((x + w) * cell_w), round((y + h) * cell_h))
        draw.rectangle(box, fill=(0, 220, 120, 90), outline=(140, 255, 190, 240), width=4)
        draw.text((box[0] + 4, box[1] + 4), bridge.get("id", "bridge"), font=font, fill=(0, 30, 10, 255), stroke_width=2, stroke_fill=(210, 255, 225, 255))

    for site in geo.get("sites", []):
        x, y, w, h = site["rect"]
        box = (round(x * cell_w), round(y * cell_h), round((x + w) * cell_w), round((y + h) * cell_h))
        draw.rectangle(box, outline=(255, 224, 0, 245), width=4)
        draw.text((box[0] + 3, box[1] + 3), site["id"], font=font, fill=(15, 12, 0, 255), stroke_width=2, stroke_fill=(255, 255, 230, 255))
        ax, ay = site["approach"]
        cx, cy = round((ax + 0.5) * cell_w), round((ay + 0.5) * cell_h)
        draw.ellipse((cx - 7, cy - 7, cx + 7, cy + 7), fill=(255, 220, 0, 230), outline=(25, 20, 0, 255), width=2)

    for x in range(cols + 1):
        px = round(x * cell_w)
        draw.line((px, 0, px, height), fill=(255, 255, 255, 95), width=2)
    for y in range(row_count + 1):
        py = round(y * cell_h)
        draw.line((0, py, width, py), fill=(255, 255, 255, 95), width=2)

    for y in range(row_count):
        for x in range(cols):
            label = f"{x},{y}"
            cx, cy = round((x + 0.5) * cell_w), round((y + 0.5) * cell_h)
            bbox = draw.textbbox((0, 0), label, font=font)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            draw.rectangle((cx - tw // 2 - 3, cy - th // 2 - 2, cx + tw // 2 + 3, cy + th // 2 + 2), fill=(0, 0, 0, 145))
            draw.text((cx - tw // 2, cy - th // 2), label, font=font, fill=(255, 255, 255, 245))

    composite = Image.alpha_composite(image, overlay).convert("RGB")
    output = out / f"{world['id']}-owner-source-16x10-grid.png"
    composite.save(output, optimize=True)
    rows.append({
        "worldId": world["id"],
        "ownerFile": world["file"],
        "runtimeFile": world.get("runtimeFile"),
        "runtimeMatchesOwner": world.get("runtimeFile") == world["file"],
        "generatedMapFile": world.get("mapFile"),
        "dimensions": [width, height],
        "worldToSource": geo.get("worldToSource"),
        "blockedCells": geo.get("blocked", []),
        "bridgeDefinitions": geo.get("bridges", []),
        "sites": geo.get("sites", []),
        "output": str(output.relative_to(root)).replace("\\\\", "/"),
        "note": "Coordinate grid follows the current flat transform; this overlay is diagnostic only and does not certify complete per-world registration."
    })

(out / "report.json").write_text(json.dumps({
    "classification": "OWNER_MAP_COORDINATE_GRID_DIAGNOSTIC",
    "worldCount": len(rows),
    "runtimeOwnerBoundWorlds": sum(1 for row in rows if row["runtimeMatchesOwner"]),
    "worlds": rows
}, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"output": str(out), "runtimeOwnerBoundWorlds": sum(1 for row in rows if row["runtimeMatchesOwner"]), "worlds": [row["worldId"] for row in rows]}))