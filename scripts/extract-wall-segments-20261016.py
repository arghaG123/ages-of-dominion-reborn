"""Crop straight runs, corners and gates from the eight age wall sources.

The source plates are isometric compounds. Repeating a whole plate is not a wall.
These boxes keep one reusable face, one join, and one opening per age.
"""
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "assets/derivatives/image-residual-executor-20261007/environment/buildings"
OUT = ROOT / "assets/derivatives/mock-led-20261016/walls"

# Fractions of each source: (x0, y0, x1, y1). Tight on the masonry, not the yard.
BOXES = {
    "stone": {
        "run": (0.36, 0.64, 0.54, 0.84),
        "corner": (0.31, 0.52, 0.44, 0.80),
        "gate": (0.60, 0.30, 0.94, 0.68),
    },
    "bronze": {
        "run": (0.02, 0.22, 0.36, 0.58),
        "corner": (0.34, 0.02, 0.58, 0.40),
        "gate": (0.66, 0.08, 0.98, 0.52),
    },
    "iron": {
        "run": (0.08, 0.12, 0.42, 0.46),
        "corner": (0.02, 0.55, 0.28, 0.90),
        "gate": (0.48, 0.52, 0.76, 0.94),
    },
    "medieval": {
        "run": (0.32, 0.02, 0.62, 0.34),
        "corner": (0.02, 0.02, 0.28, 0.50),
        "gate": (0.58, 0.18, 0.96, 0.72),
    },
    "gunpowder": {
        "run": (0.16, 0.06, 0.40, 0.34),
        "corner": (0.58, 0.02, 0.96, 0.42),
        "gate": (0.28, 0.50, 0.70, 0.96),
    },
    "industrial": {
        "run": (0.02, 0.06, 0.42, 0.40),
        "corner": (0.28, 0.52, 0.58, 0.88),
        "gate": (0.50, 0.02, 0.92, 0.46),
    },
    "modern": {
        "run": (0.02, 0.04, 0.40, 0.46),
        "corner": (0.52, 0.08, 0.76, 0.42),
        "gate": (0.22, 0.52, 0.72, 0.86),
    },
    "future": {
        "run": (0.02, 0.16, 0.48, 0.50),
        "corner": (0.50, 0.02, 0.92, 0.38),
        "gate": (0.46, 0.40, 0.94, 0.78),
    },
}


def trim(image):
    alpha = image.getchannel("A")
    bbox = alpha.getbbox()
    if not bbox:
        raise SystemExit("empty crop")
    return image.crop(bbox)


def main():
    catalog = {"version": "walls-masonry-v3", "ages": {}}
    for age, parts in BOXES.items():
        source = SRC / age / f"walls-{age}.png"
        plate = Image.open(source).convert("RGBA")
        width, height = plate.size
        folder = OUT / age
        folder.mkdir(parents=True, exist_ok=True)
        catalog["ages"][age] = {}
        for name, (x0, y0, x1, y1) in parts.items():
            box = (int(x0 * width), int(y0 * height), int(x1 * width), int(y1 * height))
            piece = trim(plate.crop(box))
            piece.save(folder / f"{name}.png")
            rel = f"assets/derivatives/mock-led-20261016/walls/{age}/{name}.png"
            catalog["ages"][age][name] = {"file": rel, "width": piece.width, "height": piece.height}
            print(f"{age} {name} {piece.size}")
    dest = ROOT / "src/data/wall-segments-20261016.json"
    dest.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
