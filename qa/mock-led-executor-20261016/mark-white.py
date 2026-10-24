import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

root = Path(__file__).resolve().parents[2]
cat = json.loads((root / "src/data/hero-bodies-20261011.json").read_text(encoding="utf-8"))
out = root / "qa/mock-led-executor-20261016/body-previews"
for cid in ("ranger", "knight", "paladin", "warlock"):
    body = cat["bodies"][cid]
    im = Image.open(root / body["file"]).convert("RGBA")
    arr = np.asarray(im)
    rgb, alpha = arr[:, :, :3], arr[:, :, 3]
    white = (rgb[:, :, 0] > 230) & (rgb[:, :, 1] > 230) & (rgb[:, :, 2] > 230) & (alpha > 180)
    ys, xs = np.where(white)
    print(cid, "white", len(xs))
    if len(xs):
        print("  x", int(xs.min()), int(xs.max()), "y", int(ys.min()), int(ys.max()), "w", im.size[0], "h", im.size[1])
    mark = im.convert("RGB")
    pix = mark.load()
    step = max(1, len(xs) // 4000)
    for x, y in zip(xs[::step], ys[::step]):
        pix[int(x), int(y)] = (255, 0, 0)
    mark.thumbnail((360, 480))
    mark.save(out / f"{cid}-white.jpg", quality=70)
