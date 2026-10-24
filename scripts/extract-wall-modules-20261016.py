"""Cut isometric wall modules from the eight age plates.

Replaces flat frontal crops. Each age gets a straight run, an outside
corner, and a gate whose posts and opening are in the art.
"""
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PLATES = ROOT / "assets/derivatives/image-residual-executor-20261007/environment/buildings"
OUT = ROOT / "assets/derivatives/mock-led-20261016/walls"
DATA = ROOT / "src/data/wall-segments-20261016.json"

# Boxes are on the source plate: left, top, right, bottom.
BOXES = {
    "stone": {
        "run": (270, 470, 640, 865),
        "corner": (250, 480, 430, 760),
        "gate": (560, 330, 930, 780),
    },
    "bronze": {
        "run": (100, 50, 900, 360),
        "corner": (360, 120, 700, 520),
        "gate": (700, 160, 990, 560),
    },
    "iron": {
        "run": (0, 64, 632, 480),
        "corner": (124, 464, 540, 816),
        "gate": (544, 364, 820, 716),
    },
    "medieval": {
        "run": (340, 24, 640, 210),
        "corner": (160, 320, 540, 655),
        "gate": (540, 160, 970, 650),
    },
    "gunpowder": {
        "run": (0, 0, 755, 418),
        "corner": (552, 20, 944, 384),
        "gate": (280, 470, 700, 830),
    },
    "industrial": {
        "run": (0, 56, 772, 435),
        "corner": (196, 476, 756, 872),
        "gate": (524, 8, 968, 532),
    },
    "modern": {
        "run": (0, 52, 739, 435),
        "corner": (456, 0, 928, 488),
        "gate": (112, 412, 800, 872),
    },
    "future": {
        "run": (8, 90, 500, 400),
        "corner": (470, 8, 955, 360),
        "gate": (160, 350, 950, 710),
    },
}


def tight(im):
    box = im.getbbox()
    return im.crop(box) if box else im


def main():
    catalog = {
        "version": "walls-isometric-v4",
        "ages": {},
    }
    for age, parts in BOXES.items():
        plate = Image.open(next((PLATES / age).glob("walls-*.png"))).convert("RGBA")
        dest = OUT / age
        dest.mkdir(parents=True, exist_ok=True)
        catalog["ages"][age] = {}
        for name, box in parts.items():
            image = tight(plate.crop(box))
            image.save(dest / f"{name}.png")
            rel = f"assets/derivatives/mock-led-20261016/walls/{age}/{name}.png"
            catalog["ages"][age][name] = {
                "file": rel,
                "width": image.width,
                "height": image.height,
            }
            print(f"{age} {name} {image.size}")
    DATA.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")
    print(f"Updated {DATA}")


if __name__ == "__main__":
    main()
