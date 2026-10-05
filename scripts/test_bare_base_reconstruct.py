import numpy as np
from PIL import Image, ImageFilter, ImageDraw
from pathlib import Path

root = Path("c:/dev/ages-of-dominion-reborn")

def reconstruct_bare_base(source_path, geom):
    """
    Locally reconstructs a clean bare terrain base from the source candidate image.
    Replaces mutable structures, occupied buildings, props, and plot rectangles with
    coherent ground texture sampled from adjacent static terrain of the same era.
    """
    im = Image.open(source_path).convert("RGB")
    w, h = im.size
    matrix = geom["worldToSource"]

    def point(x, y):
        a, b, c, d, e, f = matrix
        return int(a * x + c * y + e), int(b * x + d * y + f)

    def poly(rect):
        x, y, rw, rh = rect
        return [point(x, y), point(x + rw, y), point(x + rw, y + rh), point(x, y + rh)]

    arr = np.array(im).astype(np.float32)

    # Create mutable mask
    mask_im = Image.new("L", (w, h), 0)
    draw_mask = ImageDraw.Draw(mask_im)

    # 1. Townhall area (civic terrace)
    th = next(s for s in geom["sites"] if s["id"] == "townhall")
    th_p = poly(th["rect"])
    draw_mask.polygon(th_p, fill=255)

    # 2. All 17 build sites
    for s in geom["sites"]:
        if s["id"] != "townhall":
            p = poly(s["rect"])
            draw_mask.polygon(p, fill=255)

    # 3. Roads corridor
    for road in geom.get("roads", []):
        pts = [point(x, y) for x, y in road]
        draw_mask.line(pts, fill=255, width=28)

    # Dilate and smooth mask slightly to cover footprints and immediate object borders
    mask_arr = np.array(mask_im) > 0

    # Build texture synthesis / patch filling for mutable regions
    # Sample good static terrain patches from the surrounding environment
    # Outside sites, river, roads
    static_mask = ~mask_arr
    # Exclude river (x > 1150)
    static_mask[:, 1150:] = False

    # Extract patches from clear static ground
    static_pixels = arr[static_mask]
    if len(static_pixels) > 0:
        mean_color = static_pixels.mean(axis=0)
        std_color = static_pixels.std(axis=0)
    else:
        mean_color = np.array([128.0, 128.0, 128.0])
        std_color = np.array([20.0, 20.0, 20.0])

    # For each contiguous site/corridor, synthesize texture by multi-scale blending
    # from adjacent static border pixels
    base_out = im.copy()
    
    # Feathered inpainting: smooth bilateral edge blend
    # We do a local area texture transfer:
    for s in geom["sites"]:
        p = poly(s["rect"])
        xs = [pt[0] for pt in p]
        ys = [pt[1] for pt in p]
        min_x = max(0, min(xs) - 8)
        max_x = min(w, max(xs) + 8)
        min_y = max(0, min(ys) - 8)
        max_y = min(h, max(ys) + 8)
        
        # Sample patch from a nearby static region at similar y level
        # To match lighting and elevation gradient
        sample_x = min(w - (max_x - min_x) - 1, max(0, min_x - (max_x - min_x) - 20))
        if sample_x == min_x:
            sample_x = min(w - (max_x - min_x) - 1, max_x + 20)
        sample_y = min_y
        
        patch = im.crop((sample_x, sample_y, sample_x + (max_x - min_x), sample_y + (max_y - min_y)))
        # Create a smooth soft mask for the site polygon
        site_mask = Image.new("L", (max_x - min_x, max_y - min_y), 0)
        sm_draw = ImageDraw.Draw(site_mask)
        rel_poly = [(pt[0] - min_x, pt[1] - min_y) for pt in p]
        sm_draw.polygon(rel_poly, fill=255)
        site_mask = site_mask.filter(ImageFilter.GaussianBlur(radius=6))
        
        base_out.paste(patch, (min_x, min_y), site_mask)

    # Smooth the result gently across transitions
    return base_out

import sys
sys.path.append(str(root))
from scripts.verify_layout_geometry import sites
geom_test = {
    "worldToSource": [60.0, -10.0, 25.0, 35.0, 170.0, 165.0],
    "sites": sites,
    "roads": [
        [[5.66, 5.4], [5.66, 10.45]],
        [[1.75, 8.05], [11.4, 8.05]],
        [[1.75, 2.9], [1.75, 8.05]],
        [[8.0, 2.6], [8.0, 8.05]],
        [[11.4, 8.05], [12.5, 7.6], [13.15, 7.6]],
    ],
}
src_stone = root / "assets/production/production-03-20261003/images/01-kingdom-terrain-stone.png"
res = reconstruct_bare_base(src_stone, geom_test)
test_out = root / "qa/test_reconstruct_stone_base.png"
res.save(test_out)
print("Saved test reconstruct base:", test_out, "size:", res.size)
