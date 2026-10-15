import json
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
atlas = json.loads((ROOT / "src/data/actor-atlas.json").read_text(encoding="utf-8"))
report = json.loads((Path(__file__).resolve().parent / "rig-crops/report.json").read_text(encoding="utf-8"))
out = Path(__file__).resolve().parent / "rig-crops"
for row in report["rows"]:
    if row["classId"] not in {"healer", "knight"}:
        continue
    image = Image.open(ROOT / atlas["classes"][row["classId"]]["file"]).convert("RGBA")
    names = ["head", "torso", "arm", "forearm", "thigh", "shin", "foot"]
    sheet = Image.new("RGBA", (len(names) * 180, 220), (0, 0, 0, 255))
    draw = ImageDraw.Draw(sheet)
    for index, name in enumerate(names):
        box = row["boxes"][name]
        draw.text((index * 180 + 4, 4), name, fill=(240, 220, 180, 255))
        if not box:
            continue
        x, y, w, h = box
        crop = image.crop((x, y, x + w, y + h))
        crop.thumbnail((160, 170))
        sheet.alpha_composite(crop, (index * 180 + 8, 28))
    sheet.save(out / f"{row['classId']}-boxes.png")
print("wrote box sheets")
