"""List elongated knight components so the weapon rect is a weapon."""
import json
from pathlib import Path
from PIL import Image
import extract_rig_limbs as limbs

root = Path(__file__).resolve().parents[2]
image = Image.open(root / "assets/delivery/stone-starter-20261003/derivatives/v2/live/rigs/knight.png")
_rgb, _alpha, parts, _w, _h = limbs.components(image)
long = [part for part in parts if part["box"][2] > part["box"][3] * 1.4 or part["box"][3] > part["box"][2] * 2.2]
long.sort(key=lambda part: part["area"], reverse=True)
print(json.dumps(long[:18], indent=2))
