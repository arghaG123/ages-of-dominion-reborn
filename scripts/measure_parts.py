"""Measure opaque parts on class rig sheets. Prints boxes; writes nothing."""
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
RIGS = {
    "knight": ROOT / "assets/production/production-12-20261003/images/16-rig-knight.png",
    "mage": ROOT / "assets/production/production-12-20261003/images/19-rig-mage.png",
    "ranger": ROOT / "assets/production/production-12-20261003/images/17-rig-ranger.png",
}


def mask_of(path):
    im = Image.open(path).convert("RGBA")
    arr = np.asarray(im)
    r, g, b, a = arr[:,:,0], arr[:,:,1], arr[:,:,2], arr[:,:,3]
    magenta = (r > 180) & (g < 80) & (b > 180)
    fg = (a > 16) & ~magenta
    return fg


def components(fg, min_area=600):
    labels, count = ndimage.label(fg)
    out = []
    for lab, sl in enumerate(ndimage.find_objects(labels), start=1):
        if sl is None:
            continue
        ys, xs = sl
        area = int((labels[sl] == lab).sum())
        if area < min_area:
            continue
        x0, y0, x1, y1 = xs.start, ys.start, xs.stop - 1, ys.stop - 1
        out.append({"x": x0, "y": y0, "w": x1 - x0 + 1, "h": y1 - y0 + 1, "area": area, "cx": (x0 + x1) / 2, "cy": (y0 + y1) / 2})
    out.sort(key=lambda b: -b["area"])
    return out


def main():
    names = sys.argv[1:] or list(RIGS)
    for name in names:
        path = RIGS.get(name) or Path(name)
        fg = mask_of(path)
        # downsample 2x for speed
        small = fg[::2, ::2]
        boxes = components(small, 200)
        print(f"\n== {name} {fg.shape} parts {len(boxes)}")
        for i, b in enumerate(boxes[:24]):
            print(f"{i:02d} x={b['x']*2:4d} y={b['y']*2:4d} w={b['w']*2:4d} h={b['h']*2:4d} a={b['area']*4:7d} c=({b['cx']*2:.0f},{b['cy']*2:.0f})")


if __name__ == "__main__":
    main()
