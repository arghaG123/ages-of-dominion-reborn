import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "src/data/implementation-contract.json"
PERIMETER = [
    (0.6, 9.0), (0.3, 6.0), (0.4, 3.0), (1.2, 1.2), (2.4, -0.1),
    (4.0, -0.5), (6.5, -0.6), (9.0, -0.3), (11.0, 0.7), (12.1, 2.4),
    (12.4, 4.4), (12.6, 6.3), (12.6, 7.8), (12.5, 8.6), (12.0, 9.5),
    (11.1, 10.1), (8.2, 10.25), (7.2, 10.25), (4.0, 10.25), (1.8, 9.8),
]
WALL_RUNS = [PERIMETER[0:12], PERIMETER[12:17], PERIMETER[17:] + [PERIMETER[0]]]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("image", type=Path, help="Image candidate to inspect")
    parser.add_argument("output", type=Path, help="QA-only overlay path")
    args = parser.parse_args()
    image = args.image if args.image.is_absolute() else ROOT / args.image
    output = args.output if args.output.is_absolute() else ROOT / args.output
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    geometry = contract["geometry"]["kingdom"]
    result = Image.open(image).convert("RGBA")
    sx = result.width / geometry["sourceSize"][0]
    sy = result.height / geometry["sourceSize"][1]
    matrix = geometry["worldToSource"]
    draw = ImageDraw.Draw(result, "RGBA")

    def project(x, y):
        a, b, c, d, e, f = matrix
        return ((a * x + c * y + e) * sx, (b * x + d * y + f) * sy)

    def rect_points(rect):
        x, y, width, height = rect
        return [project(x, y), project(x + width, y), project(x + width, y + height), project(x, y + height)]

    for site in geometry["sites"]:
        points = rect_points(site["rect"])
        draw.polygon(points, fill=(0, 180, 255, 18), outline=(0, 220, 255, 225), width=2)
        draw.text(points[0], site["id"], fill=(255, 255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0, 240))
    for road in geometry["roads"]:
        draw.line([project(*point) for point in road], fill=(255, 20, 220, 230), width=6)
    for bridge in geometry["bridges"]:
        points = rect_points(bridge["rect"])
        draw.polygon(points, fill=(0, 255, 255, 45), outline=(0, 255, 255, 255), width=5)
    for run in WALL_RUNS:
        draw.line([project(*point) for point in run], fill=(255, 20, 20, 230), width=7, joint="curve")
    for name, point in (("RIDGE", geometry["anchors"]["ridge"]), ("GATE", geometry["anchors"]["gate"])):
        x, y = project(*point)
        draw.ellipse((x - 9, y - 9, x + 9, y + 9), fill=(255, 0, 0, 240))
        draw.text((x + 10, y - 10), name, fill=(255, 255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0, 240))
    output.parent.mkdir(parents=True, exist_ok=True)
    result.convert("RGB").save(output)
    print(json.dumps({"input": str(image), "output": str(output), "dimensions": result.size, "meaning": "Visual overlay only; manual trace and natural contact still required."}, indent=2))


if __name__ == "__main__":
    main()
