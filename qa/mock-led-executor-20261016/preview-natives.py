from pathlib import Path

import numpy as np
from PIL import Image

root = Path("assets/derivatives/image-unified-reserve-20261009/actors/natives")
out = Path("qa/mock-led-executor-20261016/body-previews")
for path in sorted(root.glob("class-*-standing-body.png")):
    im = Image.open(path).convert("RGB")
    im.thumbnail((220, 320))
    im.save(out / f"native-{path.name.replace('.png', '.jpg')}", quality=70)
    print(path.name, Image.open(path).size)
