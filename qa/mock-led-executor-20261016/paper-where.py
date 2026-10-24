from pathlib import Path

import cv2
import numpy as np
from PIL import Image

root = Path(__file__).resolve().parents[2]
originals = {
    "knight": "assets/derivatives/image-complete-20261011/actors/bodies/class-knight-standing-body.png",
    "ranger": "assets/derivatives/image-complete-20261011/actors/bodies/class-ranger-standing-body.png",
    "paladin": "assets/derivatives/image-complete-20261011/actors/bodies/class-paladin-standing-body.png",
    "warlock": "assets/derivatives/image-complete-20261011/actors/bodies/class-warlock-standing-body.png",
    "necromancer": "assets/derivatives/image-complete-20261011/actors/bodies/class-necromancer-standing-body.png",
}
for cid, rel in originals.items():
    arr = np.asarray(Image.open(root / rel).convert("RGBA"))
    rgb, alpha = arr[:, :, :3], arr[:, :, 3]
    mn, mx = rgb.min(axis=2), rgb.max(axis=2)
    paper = ((mn > 238) & ((mx - mn) < 18) & (alpha > 32)).astype(np.uint8)
    count, labels = cv2.connectedComponents(paper, connectivity=8)
    h, w = labels.shape
    edge_ids = set(labels[0, :].tolist() + labels[-1, :].tolist() + labels[:, 0].tolist() + labels[:, -1].tolist())
    sizes = np.bincount(labels.ravel())
    print(cid)
    for i in np.argsort(sizes)[::-1]:
        if i == 0 or sizes[i] < 400:
            continue
        ys, xs = np.where(labels == i)
        print(" ", int(sizes[i]), "edge" if i in edge_ids else "inner", "bbox", int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max()))
