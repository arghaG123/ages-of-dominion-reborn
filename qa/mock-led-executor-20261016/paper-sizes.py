import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

root = Path(__file__).resolve().parents[2]
cat = json.loads((root / "src/data/hero-bodies-20261011.json").read_text(encoding="utf-8"))
# originals are still the pre-repair paths recorded in source fields for most classes
originals = {
    "knight": "assets/derivatives/image-complete-20261011/actors/bodies/class-knight-standing-body.png",
    "ranger": "assets/derivatives/image-complete-20261011/actors/bodies/class-ranger-standing-body.png",
    "warlock": "assets/derivatives/image-complete-20261011/actors/bodies/class-warlock-standing-body.png",
    "mage": "assets/derivatives/image-complete-20261011/actors/bodies/class-mage-standing-body.png",
    "paladin": "assets/derivatives/image-complete-20261011/actors/bodies/class-paladin-standing-body.png",
    "barbarian": "assets/derivatives/image-complete-20261011/actors/bodies/class-barbarian-standing-body.png",
    "necromancer": "assets/derivatives/image-complete-20261011/actors/bodies/class-necromancer-standing-body.png",
    "healer": "assets/derivatives/mock-led-20261016/healer/class-healer-complete-body.png",
}
for cid, rel in originals.items():
    arr = np.asarray(Image.open(root / rel).convert("RGBA"))
    rgb, alpha = arr[:, :, :3], arr[:, :, 3]
    mn, mx = rgb.min(axis=2), rgb.max(axis=2)
    paper = ((mn > 238) & ((mx - mn) < 18) & (alpha > 32)).astype(np.uint8)
    count, labels = cv2.connectedComponents(paper, connectivity=8)
    sizes = np.bincount(labels.ravel())
    order = np.argsort(sizes)[::-1][:6]
    print(cid, [(int(i), int(sizes[i])) for i in order if i != 0])
