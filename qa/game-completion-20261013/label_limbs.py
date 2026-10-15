"""Number connected limb pieces on the six class rig sheets. Preview only."""
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
atlas = json.loads((ROOT / "src/data/actor-atlas.json").read_text(encoding="utf-8"))
out = Path(__file__).resolve().parent / "rig-crops" / "labeled"
out.mkdir(parents=True, exist_ok=True)
classes = ["ranger", "warlock", "mage", "paladin", "barbarian", "necromancer"]

for class_id in classes:
    image = Image.open(ROOT / atlas["classes"][class_id]["file"]).convert("RGB")
    rgb = np.asarray(image)
    red = rgb[:, :, 0].astype(np.int16)
    green = rgb[:, :, 1].astype(np.int16)
    blue = rgb[:, :, 2].astype(np.int16)
    magenta = (red > 170) & (blue > 140) & (green < 90) & (red > green + 40)
    panel = (green > 90) & (green > red + 18) & (green > blue + 8) & (red < 180)
    mask = (~magenta & ~panel).astype(np.uint8) * 255
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    count, _labels, stats, centroids = cv2.connectedComponentsWithStats(mask, 8)
    rows = []
    for index in range(1, count):
        x, y, width, height, area = [int(value) for value in stats[index]]
        if area < 800 or width < 12 or height < 12:
            continue
        rows.append({
            "box": [x, y, width, height],
            "area": area,
            "cx": round(float(centroids[index][0]), 1),
            "cy": round(float(centroids[index][1]), 1),
        })
    rows.sort(key=lambda row: (row["cy"] // 80, row["cx"]))
    vis = image.convert("RGBA")
    draw = ImageDraw.Draw(vis)
    for number, row in enumerate(rows):
        x, y, width, height = row["box"]
        draw.rectangle([x, y, x + width, y + height], outline=(255, 220, 40, 255), width=2)
        draw.text((x + 2, y + 2), str(number), fill=(255, 255, 255, 255))
        row["n"] = number
    vis.resize((768, 768), Image.Resampling.NEAREST).save(out / f"{class_id}-labels.png")
    big = sorted(rows, key=lambda row: -row["area"])[:24]
    sheet = Image.new("RGB", (6 * 160, 4 * 180), (30, 30, 30))
    sheet_draw = ImageDraw.Draw(sheet)
    for key, row in enumerate(big):
        x, y, width, height = row["box"]
        crop = image.crop((x, y, x + width, y + height))
        crop.thumbnail((140, 140))
        origin_x = (key % 6) * 160 + 8
        origin_y = (key // 6) * 180 + 24
        sheet.paste(crop, (origin_x, origin_y))
        sheet_draw.text((origin_x, origin_y - 16), f"n{row['n']} {width}x{height}", fill=(240, 220, 160))
    sheet.save(out / f"{class_id}-parts.png")
    print(class_id, "count", len(rows))
    for row in rows:
        print(f"  {row['n']:02d} {row['box']} a={row['area']} c={row['cx']},{row['cy']}")
    print()
