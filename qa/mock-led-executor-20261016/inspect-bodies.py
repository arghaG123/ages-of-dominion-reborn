import json
from pathlib import Path

import numpy as np
from PIL import Image

root = Path(__file__).resolve().parents[2]
cat = json.loads((root / "src/data/hero-bodies-20261011.json").read_text(encoding="utf-8"))
out = root / "qa/mock-led-executor-20261016/body-previews"
out.mkdir(parents=True, exist_ok=True)
for cid, body in cat["bodies"].items():
    im = Image.open(root / body["file"]).convert("RGBA")
    arr = np.asarray(im)
    rgb, alpha = arr[:, :, :3], arr[:, :, 3]
    white = int(((rgb[:, :, 0] > 235) & (rgb[:, :, 1] > 235) & (rgb[:, :, 2] > 235) & (alpha > 200)).sum())
    near = int(((rgb.min(axis=2) > 210) & (alpha > 160)).sum())
    print(cid, im.size, "white", white, "near", near)
    preview = Image.new("RGBA", (280, 420), (42, 36, 30, 255))
    thumb = im.copy()
    thumb.thumbnail((260, 400))
    preview.alpha_composite(thumb, ((280 - thumb.width) // 2, 420 - thumb.height - 4))
    preview.convert("RGB").save(out / f"{cid}.jpg", quality=75)
