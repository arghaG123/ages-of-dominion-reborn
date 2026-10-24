"""Clear paper-white backdrop leaks from standing bodies. Originals stay put."""
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

root = Path(__file__).resolve().parents[2]
cat_path = root / "src/data/hero-bodies-20261011.json"
cat = json.loads(cat_path.read_text(encoding="utf-8"))
dest = root / "assets/derivatives/mock-led-20261016/bodies"
dest.mkdir(parents=True, exist_ok=True)
preview = root / "qa/mock-led-executor-20261016/body-previews"


def paper_mask(rgb, alpha):
    mn = rgb.min(axis=2)
    mx = rgb.max(axis=2)
    return ((mn > 238) & ((mx - mn) < 18) & (alpha > 32)).astype(np.uint8)


def clear_white(arr):
    rgb = arr[:, :, :3]
    alpha = arr[:, :, 3].copy()
    paper = paper_mask(rgb, alpha)
    # Edge and gap leaks are backdrop. A large enclosed paper region is the bow hole.
    # Smaller interior paper stays, so armor highlights are not punched out.
    count, labels = cv2.connectedComponents(paper, connectivity=8)
    edge = np.zeros(count, dtype=bool)
    edge[labels[0, :]] = True
    edge[labels[-1, :]] = True
    edge[labels[:, 0]] = True
    edge[labels[:, -1]] = True
    transparent = alpha < 16
    touch = np.zeros(count, dtype=bool)
    if transparent.any():
        ring = cv2.dilate(transparent.astype(np.uint8), np.ones((3, 3), np.uint8))
        touch_labels = np.unique(labels[ring > 0])
        touch[touch_labels] = True
    sizes = np.bincount(labels.ravel(), minlength=count)
    drop = edge | touch | (sizes >= 3000)
    drop[0] = False
    kill = drop[labels]
    alpha[kill] = 0
    # One-pixel paper fringe left against the new transparency.
    for _ in range(2):
        hole = (alpha < 16).astype(np.uint8)
        near = cv2.dilate(hole, np.ones((3, 3), np.uint8)) > 0
        fringe = near & (paper_mask(rgb, np.full_like(alpha, 255)) > 0) & (alpha > 0)
        alpha[fringe] = 0
    out = arr.copy()
    out[:, :, 3] = alpha
    return out


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
report = []
for cid, body in cat["bodies"].items():
    src = root / originals[cid]
    arr = np.asarray(Image.open(src).convert("RGBA"))
    fixed = clear_white(arr)
    removed = int(((arr[:, :, 3] > 16) & (fixed[:, :, 3] < 16)).sum())
    out_path = dest / f"class-{cid}-standing-body.png"
    Image.fromarray(fixed).save(out_path)
    digest = hashlib.sha256(out_path.read_bytes()).hexdigest()
    body["file"] = out_path.relative_to(root).as_posix()
    body["sha256"] = digest
    body["bytes"] = out_path.stat().st_size
    body["matteRepair"] = body.get("matteRepair") or {}
    body["matteRepair"]["paperWhiteBackdropCleared"] = removed
    report.append((cid, removed, digest[:12]))
    show = Image.new("RGBA", (280, 420), (42, 36, 30, 255))
    thumb = Image.fromarray(fixed)
    thumb.thumbnail((260, 400))
    show.alpha_composite(thumb, ((280 - thumb.width) // 2, 420 - thumb.height - 4))
    show.convert("RGB").save(preview / f"{cid}-matte.jpg", quality=75)

cat_path.write_text(json.dumps(cat, indent=2) + "\n", encoding="utf-8")
for row in report:
    print(*row)
