import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

root = Path("c:/dev/ages-of-dominion-reborn")
sys.path.append(str(root))
from scripts.verify_layout_geometry import sites

def font(size):
    for name in (r"C:\Windows\Fonts\arial.ttf", r"C:\Windows\Fonts\segoeui.ttf"):
        p = Path(name)
        if p.exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()

def render_kingdom_guide_and_masks(geom):
    width, height = 1376, 768
    matrix = geom["worldToSource"]

    def point(x, y):
        a, b, c, d, e, f = matrix
        return a * x + c * y + e, b * x + d * y + f

    def poly(rect):
        x, y, w, h = rect
        return [
            point(x, y),
            point(x + w, y),
            point(x + w, y + h),
            point(x, y + h),
        ]

    guide_img = Image.new("RGB", (width, height), "#d8d2be")
    draw = ImageDraw.Draw(guide_img)

    mask_change = Image.new("L", (width, height), 0)
    draw_mc = ImageDraw.Draw(mask_change)

    # 1. Blocked / River along column 13
    for cell in geom.get("blocked", []):
        p = poly([*cell, 1, 1])
        draw.polygon(p, fill="#597281", outline="#475e6d")

    # 2. Roads
    for road in geom.get("roads", []):
        pts = [point(x, y) for x, y in road]
        draw.line(pts, fill="#ae9171", width=18)
        draw_mc.line(pts, fill=255, width=18)

    # 3. Bridges
    for bridge in geom.get("bridges", []):
        p = poly(bridge["rect"])
        draw.polygon(p, fill="#c5b397", outline="#5a5349", width=3)
        draw_mc.polygon(p, fill=255)

    # 4. Sites
    f_site = font(16)
    f_th = font(18)
    for site in geom.get("sites", []):
        p = poly(site["rect"])
        is_th = site["id"] == "townhall"
        fill_color = "#a5c184" if is_th else "#91b76b"
        out_color = "#2e541e" if is_th else "#193d19"
        out_width = 4 if is_th else 3
        draw.polygon(p, fill=fill_color, outline=out_color, width=out_width)
        draw_mc.polygon(p, fill=255)
        
        x, y, w, h = site["rect"]
        cx, cy = point(x + w / 2, y + h / 2)
        txt = "TOWNHALL (CIVIC TERRACE)" if is_th else site["id"]
        used_font = f_th if is_th else f_site
        draw.text((cx - (40 if is_th else 14), cy - 9), txt, fill="black", font=used_font)

    # 5. Anchors (gate, ridge)
    f_anchor = font(14)
    for name, cell in geom.get("anchors", {}).items():
        px, py = point(*cell)
        draw.ellipse((px - 7, py - 7, px + 7, py + 7), fill="#c83e38", outline="black", width=2)
        draw.text((px + 10, py - 8), name.upper(), fill="#8b0000", font=f_anchor)
        draw_mc.ellipse((px - 10, py - 10, px + 10, py + 10), fill=255)

    mask_keep = Image.eval(mask_change, lambda val: 255 - val)
    return guide_img, mask_change, mask_keep

# Test guide rendering
geom_test = {
    "worldToSource": [60.0, -10.0, 25.0, 35.0, 170.0, 165.0],
    "sites": sites,
    "blocked": [[13, r] for r in range(11)],
    "roads": [
        [[5.66, 5.4], [5.66, 10.45]],
        [[1.75, 8.05], [11.4, 8.05]],
        [[1.75, 2.9], [1.75, 8.05]],
        [[8.0, 2.6], [8.0, 8.05]],
        [[11.4, 8.05], [12.5, 7.6], [13.15, 7.6]],
    ],
    "bridges": [
        {
            "id": "right-crossing",
            "rect": [12.15, 7.2, 1.55, 0.85],
            "cells": [[13, 7]],
            "approaches": [[12, 7]],
        }
    ],
    "anchors": {
        "gate": [5.66, 10.45],
        "ridge": [5.66, 0.5],
    },
}

guide, mc, mk = render_kingdom_guide_and_masks(geom_test)
guide_path = root / "qa/test_kingdom_v3_guide.png"
guide.save(guide_path)
print("Rendered guide saved to:", guide_path, "size:", guide.size)
