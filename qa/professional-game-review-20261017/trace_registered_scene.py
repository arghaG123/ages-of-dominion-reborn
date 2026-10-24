import json
import argparse
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser()
parser.add_argument("--pack", default="tactical-stone-registered-v1")
parser.add_argument("--image", default="native-1.png")
args = parser.parse_args()
PACK = ROOT / "qa/professional-art-20261018" / args.pack
geometry = json.loads((ROOT / "src/data/implementation-contract.json").read_text())["geometry"]["tactical"]
matrix = geometry["worldToSource"]


def point(column, row):
    return (matrix[0] * column + matrix[2] * row + matrix[4], matrix[1] * column + matrix[3] * row + matrix[5])


image = Image.open(PACK / args.image).convert("RGB").resize(tuple(geometry["sourceSize"]), Image.Resampling.LANCZOS)
draw = ImageDraw.Draw(image)
for column in range(geometry["cols"] + 1):
    draw.line([point(column, 0), point(column, geometry["rows"])], fill="#ffffaa", width=1)
for row in range(geometry["rows"] + 1):
    draw.line([point(0, row), point(geometry["cols"], row)], fill="#ffffaa", width=1)
for bridge in geometry["bridges"]:
    column, row, width, height = bridge["rect"]
    corners = [point(column, row), point(column + width, row), point(column + width, row + height), point(column, row + height)]
    draw.line(corners + [corners[0]], fill="#00ffff", width=3)
    for column, row in bridge["approaches"]:
        horizontal, vertical = point(column + .5, row + .5)
        draw.ellipse((horizontal - 14, vertical - 9, horizontal + 14, vertical + 9), outline="#ff66ff", width=2)
for name, anchor in geometry["anchors"].items():
    horizontal, vertical = point(*anchor)
    draw.rectangle((horizontal - 14, vertical - 60, horizontal + 14, vertical), outline="#ffffff", width=2)
    draw.text((horizontal + 16, vertical - 20), name, fill="#ffffff")
output = PACK / ("qa-registered-overlay.png" if args.image != "native-1.png" else "qa-geometry-overlay.png")
image.save(output)
print(str(output))
