from pathlib import Path
from PIL import Image
root = Path(__file__).resolve().parents[2]
image = Image.open(root / "assets/delivery/stone-starter-20261003/derivatives/v2/live/rigs/knight.png")
image.crop((512, 820, 1024, 1024)).save(Path(__file__).resolve().parent / "rig-crops/knight-feet-strip.png")
print(image.size)
