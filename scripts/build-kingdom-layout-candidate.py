"""Build the Stone Kingdom layout candidate, Hall survey, and v4 spatial guide.

Does not edit the active contract, the live scene, batch files, or the budget ledger.
"""
from pathlib import Path
import hashlib, json
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
HALL = ROOT / "assets/delivery/stone-starter-20261003/derivatives/v3/townhall-stone.png"
TERRAIN = ROOT / "assets/production/production-01-20261003/images/01-kingdom-terrain-stone.png"
CONTRACT = ROOT / "docs/plan/IMPLEMENTATION-CONTRACT.json"
SCENE = ROOT / "src/data/stone-scene.json"
OUT = ROOT / "qa/recovery-executor-20261003"
GUIDE_DIR = OUT / "guides"
PREVIEW = ROOT / "design-preview"
CAM = (60.0, -10.0, 25.0, 35.0, 170.0, 165.0)
SOURCE = (1376, 768)
SCALE = 0.34
# Image cobble (700, 760) lands on source (640, roof-consistent y). Roof tip image y=21 -> source y=40.
TY = 40.0 - SCALE * 21.0
TX = 640.0 - SCALE * 700.0
VIEWPORTS = ((825, 375), (933, 424), (1180, 820), (1280, 720))

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def project(x, y, cam=CAM):
    a, b, c, d, e, f = cam
    return (a * x + c * y + e, b * x + d * y + f)

def inverse(sx, sy, cam=CAM):
    a, b, c, d, e, f = cam
    det = a * d - b * c
    return ((d * (sx - e) - c * (sy - f)) / det, (-b * (sx - e) + a * (sy - f)) / det)

def font(size):
    for name in (r"C:\Windows\Fonts\arial.ttf", r"C:\Windows\Fonts\segoeui.ttf"):
        path = Path(name)
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()

def rect_poly(rect):
    x, y, w, h = rect
    return [project(x, y), project(x + w, y), project(x + w, y + h), project(x, y + h)]

def overlap(a, b):
    return max(a[0], b[0]) < min(a[0] + a[2], b[0] + b[2]) and max(a[1], b[1]) < min(a[1] + a[3], b[1] + b[3])

def point_in(pt, poly):
    x, y = pt
    inside = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi + 1e-9) + xi:
            inside = not inside
        j = i
    return inside

def survey(im):
    px = im.load()
    w, h = im.size
    opaque = [[px[x, y][3] > 16 for x in range(w)] for y in range(h)]
    top, bot = [], []
    for x in range(w):
        ys = [y for y in range(h) if opaque[y][x]]
        top.append(ys[0] if ys else None)
        bot.append(ys[-1] if ys else None)
    peaks = []
    for x in range(16, w - 16):
        if top[x] is None:
            continue
        window = [v for v in top[x - 16:x + 17] if v is not None]
        if top[x] == min(window) and (not peaks or x - peaks[-1][0] > 18):
            peaks.append([x, top[x]])
    contour = [[x, top[x]] for x in range(0, w, 8) if top[x] is not None]
    dirt = [[x, bot[x]] for x in range(0, w, 8) if bot[x] is not None]
    return {
        "imageSize": [w, h],
        "opaqueBounds": [0, min(v for v in top if v is not None), w - 1, max(v for v in bot if v is not None)],
        "roofContour": contour,
        "roofPeaks": peaks,
        "highestRoof": [int(top.index(min(v for v in top if v is not None))), min(v for v in top if v is not None)],
        "dirtSilhouette": dirt,
        "dirtBottomMedian": sorted(v for v in bot if v is not None)[sum(v is not None for v in bot) // 2],
    }

def main():
    hall = Image.open(HALL).convert("RGBA")
    measured = survey(hall)
    hall_sha = digest(HALL)
    contract_sha = digest(CONTRACT)
    scene = json.loads(SCENE.read_text(encoding="utf-8"))
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert contract["geometry"]["kingdom"]["worldToSource"] == list(CAM)
    assert scene["hall"]["matrix"][0][0] == 0.1312
    anchor_world = inverse(640.0, TY + SCALE * 760.0)
    townhall = [round(anchor_world[0] - 1.9, 3), round(anchor_world[1] - 1.9, 3), 3.8, 1.9]
    # Keep the front-center exactly on the surveyed cobble after rounding.
    front = (townhall[0] + townhall[2] / 2, townhall[1] + townhall[3])
    landed = project(*front)
    assert abs(landed[0] - 640) < 1.5 and abs(landed[1] - (TY + SCALE * 760)) < 1.5

    plots = {
        "P01": (0.30, 2.30, 1.4, 1.2, "upper"),
        "P02": (0.30, 3.70, 1.4, 1.2, "upper"),
        "P03": (0.30, 6.45, 1.4, 1.2, "upper"),
        "P04": (0.30, 8.55, 1.4, 1.2, "lower"),
        "P05": (8.70, 2.45, 1.4, 1.2, "upper"),
        "P06": (8.70, 4.30, 1.4, 1.2, "upper"),
        "P07": (8.70, 6.15, 1.4, 1.2, "upper"),
        "P08": (8.70, 8.55, 1.4, 1.2, "lower"),
        "P09": (10.30, 2.45, 1.4, 1.2, "upper"),
        "P10": (10.30, 4.40, 1.4, 1.2, "upper"),
        "P11": (10.30, 6.30, 1.4, 1.2, "upper"),
        "P12": (8.35, 9.80, 1.4, 1.2, "lower"),
        "P13": (2.05, 8.55, 1.4, 1.2, "lower"),
        "P14": (3.65, 8.55, 1.4, 1.2, "lower"),
        "P15": (6.75, 8.55, 1.4, 1.2, "lower"),
        "P16": (2.05, 9.80, 1.4, 1.2, "lower"),
        "P17": (6.20, 9.80, 1.4, 1.2, "lower"),
    }
    sites = [{"id": "townhall", "rect": townhall, "role": "civic-hall"}]
    sites += [{"id": k, "region": v[4], "rect": [v[0], v[1], v[2], v[3]], "day1": "empty"} for k, v in plots.items()]
    rects = [tuple(s["rect"]) for s in sites]
    for i, a in enumerate(rects):
        assert a[0] >= 0 and a[1] >= 0 and a[0] + a[2] <= 14 and a[1] + a[3] <= 11, a
        for b in rects[i + 1:]:
            assert not overlap(a, b), (a, b)
    sprite = (TX, 40.0, TX + SCALE * 1023, TY + SCALE * 999)
    sprite_poly = [(sprite[0], sprite[1]), (sprite[2], sprite[1]), (sprite[2], sprite[3]), (sprite[0], sprite[3])]
    for site in sites:
        if site["id"] == "townhall":
            continue
        x, y, w, h = site["rect"]
        for i in range(7):
            for j in range(7):
                sx, sy = project(x + w * i / 6, y + h * j / 6)
                assert not point_in((sx, sy), sprite_poly), site["id"]

    roads = [
        [[5.66, 5.40], [5.66, 10.45]],
        [[2.05, 8.05], [11.40, 8.05]],
        [[2.05, 2.90], [2.05, 8.05]],
        [[8.20, 2.60], [8.20, 8.05]],
        [[11.40, 8.05], [12.50, 7.60], [13.15, 7.60]],
    ]
    pads = Image.new("1", SOURCE)
    road_im = Image.new("1", SOURCE)
    dp, dr = ImageDraw.Draw(pads), ImageDraw.Draw(road_im)
    for site in sites:
        if not site["id"].startswith("P"):
            continue
        dp.polygon(rect_poly(site["rect"]), fill=1)
    for road in roads:
        dr.line([project(x, y) for x, y in road], fill=1, width=16)
    from PIL import ImageChops
    assert ImageChops.logical_and(pads, road_im).getbbox() is None, "road enters a plot"

    fixture_h = {
        "P01": 120, "P02": 100, "P03": 88, "P04": 96, "P05": 136, "P06": 112, "P07": 92,
        "P08": 104, "P09": 78, "P10": 128, "P11": 90, "P12": 98, "P13": 144, "P14": 108,
        "P15": 116, "P16": 84, "P17": 94,
    }
    fixtures = []
    for site in sites:
        if site["id"] == "townhall":
            continue
        x, y, w, h = site["rect"]
        left = project(x, y + h)
        right = project(x + w, y + h)
        cx, cy = (left[0] + right[0]) / 2, (left[1] + right[1]) / 2
        width = max(36.0, ((right[0] - left[0]) ** 2 + (right[1] - left[1]) ** 2) ** 0.5 * 0.72)
        height = fixture_h[site["id"]]
        box = [round(cx - width / 2, 2), round(cy - height, 2), round(width, 2), height]
        fixtures.append({"id": site["id"], "label": "FIXTURE", "envelope": box, "heightPx": height, "note": "Mature-city height check. Not campaign progression."})

    # Panel occlusion in source pixels. Header+footer are 112px in the measured client.
    safe = []
    for vw, vh in VIEWPORTS:
        frame_h = vh - 112
        frame_w = vw
        short = vh <= 450
        panel_w = min(240 if short else 280, (0.40 if short else 0.34) * vw)
        scale = min(frame_w / SOURCE[0], frame_h / SOURCE[1])
        ox = (frame_w - SOURCE[0] * scale) / 2
        oy = (frame_h - SOURCE[1] * scale) / 2
        panel_x = frame_w - 8 - panel_w
        source_x = (panel_x - ox) / scale
        safe.append({"viewport": [vw, vh], "frame": [frame_w, frame_h], "scale": round(scale, 4), "panelLeftSourceX": round(source_x, 1)})
        for site in sites:
            x, y, w, h = site["rect"]
            sx, sy = project(x + w / 2, y + h / 2)
            assert sx < source_x - 8, (site["id"], vw, sx, source_x)

    missing = {
        "id": "civic-terrace-and-entrance-apron",
        "sourceRect": [416, 284, 742, 373],
        "existing": "incompatible",
        "finding": "Pixels exist here but they are painted guide plots, log piles and crossing dirt. They are not a clear raised terrace or entrance apron. Do not blur, clone or flat-fill them.",
    }
    points = [
        {"id": "roof-tip", "image": [448, 21], "confidence": "high", "kind": "highest opaque ridge stick, part of the roof silhouette"},
        {"id": "roof-ridge-stick", "image": [399, 25], "confidence": "high", "kind": "adjacent ridge stick on the main roof"},
        {"id": "plinth-front-stone", "image": [400, 820], "confidence": "medium-high", "kind": "crosshair sits on the lower course of the front stone plinth"},
        {"id": "plinth-left-of-door", "image": [540, 770], "confidence": "medium-high", "kind": "stone plinth immediately left of the left door post, not the post base"},
        {"id": "entrance-cobble", "image": [700, 760], "confidence": "medium", "kind": "cobble in the entrance approach, in front of the curtained opening; not a surveyed door-frame midpoint"},
        {"id": "entrance-right-cobble", "image": [800, 755], "confidence": "medium", "kind": "cobble beside the right curtain, outside the opening"},
        {"id": "dirt-not-foundation", "image": [160, 800], "confidence": "high", "kind": "bare dirt in front of the plinth; a negative example, not a foundation corner"},
    ]
    for point in points:
        ix, iy = point["image"]
        point["source"] = [round(TX + SCALE * ix, 2), round(TY + SCALE * iy, 2)]

    matrix = [[SCALE, 0.0, round(TX, 4)], [0.0, SCALE, round(TY, 4)]]
    candidate = {
        "status": "READY_FOR_REVIEW",
        "ownerAcceptance": "NOT_OWNER_ACCEPTED",
        "runtimeApproved": False,
        "activeContractEdited": False,
        "activeSceneEdited": False,
        "activeContractSHA256": contract_sha,
        "id": "kingdom-layout-candidate-v1",
        "requestId": "kingdom-stone-day1-composition-v4",
        "camera": list(CAM),
        "sourceSize": list(SOURCE),
        "scaleRule": "Uniform 0.34. The whole opaque envelope, from the ridge stick at image y=21 to the dirt at image y=999, maps inside source y=40..373 with the entrance cobble on the terrace front. The scale is not 0.1312 and is not taken from the 555px non-thatch band or from 0.3288. It is not reduced to hide clipping: the roof is inside the frame. A larger scale would still fit vertically and would cover neighbouring plots.",
        "rejectedTranslationApplied": False,
        "hall": {
            "file": "assets/delivery/stone-starter-20261003/derivatives/v3/townhall-stone.png",
            "sha256": hall_sha,
            "width": 1024,
            "height": 1024,
            "matrix": matrix,
            "uniform": True,
            "anchorImage": [700, 760],
            "anchorKind": "entrance cobble, medium confidence",
            "spriteSourceRect": [round(sprite[0], 2), round(sprite[1], 2), round(sprite[2], 2), round(sprite[3], 2)],
        },
        "geometry": {
            "cols": 14,
            "rows": 11,
            "sites": sites,
            "roads": roads,
            "blocked": [[13, r] for r in range(11)],
            "bridges": [{"id": "right-crossing", "rect": [12.15, 7.20, 1.55, 0.85], "cells": [[13, 7]], "approaches": [[12, 7]]}],
            "anchors": {"gate": [5.66, 10.45], "entrance": [5.66, 5.40]},
            "perimeter": "unbuilt",
            "wallsLevel": 0,
        },
        "fixtures": fixtures,
        "missingTerrain": missing,
        "viewportSafe": safe,
        "surveyPoints": points,
    }

    # Annotated Hall plate.
    plate = Image.alpha_composite(Image.new("RGBA", hall.size, (255, 0, 255, 255)), hall).convert("RGB")
    draw = ImageDraw.Draw(plate)
    small, label = font(16), font(18)
    roof_pts = [(x, y) for x, y in measured["roofContour"]]
    draw.line(roof_pts, fill=(220, 30, 30), width=2)
    draw.line([(x, y) for x, y in measured["dirtSilhouette"]], fill=(0, 160, 255), width=2)
    colors = {"high": (255, 220, 0), "medium-high": (255, 140, 0), "medium": (80, 220, 80)}
    for point in points:
        x, y = point["image"]
        col = colors[point["confidence"]]
        draw.ellipse((x - 7, y - 7, x + 7, y + 7), outline=col, width=2)
        draw.line((x - 14, y, x + 14, y), fill=col)
        draw.line((x, y - 14, x, y + 14), fill=col)
        draw.text((x + 10, y - 18), point["id"], fill=(0, 0, 0), font=small)
    draw.rectangle((8, 8, 620, 78), fill=(0, 0, 0))
    draw.text((16, 12), "Hall v3 survey  " + hall_sha[:12], fill=(255, 255, 255), font=label)
    draw.text((16, 36), "Red: roof silhouette. Blue: dirt edge, not foundation.", fill=(255, 255, 255), font=small)
    draw.text((16, 54), "Marks are surveyed points. The 555px band is not a foundation.", fill=(255, 220, 80), font=small)
    OUT.mkdir(parents=True, exist_ok=True)
    ann_path = OUT / "hall-v3-annotated.png"
    plate.save(ann_path)
    display = hall.resize((348, 348), Image.Resampling.LANCZOS)
    disp_path = OUT / "hall-v3-at-proposed-348px.png"
    Image.alpha_composite(Image.new("RGBA", display.size, (90, 110, 70, 255)), display).convert("RGB").save(disp_path)
    magenta = 0
    dp = display.load()
    for y in range(348):
        for x in range(348):
            r, g, b, a = dp[x, y]
            if a > 16 and r > 190 and b > 120 and g < 90 and r > g + 70:
                magenta += 1

    # Spatial guide, same 1376x768 source frame as kingdom.png.
    guide = Image.new("RGB", SOURCE, (214, 198, 166))
    g = ImageDraw.Draw(guide)
    title, body = font(22), font(15)
    for x, y in candidate["geometry"]["blocked"]:
        g.polygon(rect_poly((x, y, 1, 1)), fill=(126, 164, 184))
    g.polygon(rect_poly(candidate["geometry"]["bridges"][0]["rect"]), fill=(120, 96, 64))
    for road in roads:
        g.line([project(x, y) for x, y in road], fill=(92, 70, 48), width=14)
    g.rectangle((24, 24, SOURCE[0] - 24, SOURCE[1] - 24), outline=(60, 70, 40), width=2)
    panel_x = min(item["panelLeftSourceX"] for item in safe)
    g.rectangle((panel_x, 24, SOURCE[0] - 24, SOURCE[1] - 24), outline=(150, 50, 40), width=2)
    g.rectangle(missing["sourceRect"], outline=(180, 40, 40), width=3)
    src_roof = [(TX + SCALE * x, TY + SCALE * y) for x, y in measured["roofContour"]]
    g.line(src_roof, fill=(70, 32, 12), width=4)
    g.rectangle(sprite, outline=(70, 32, 12), width=3)
    # Sides and ridge only. Bottom plots occupy the lower edge, so the gate is the road's south end.
    for chain in ([[0.15, 1.85], [12.05, 1.85], [12.05, 7.40]], [[0.15, 1.85], [0.15, 10.90]]):
        pts = [project(x, y) for x, y in chain]
        for i in range(len(pts) - 1):
            g.line([pts[i], pts[i + 1]], fill=(70, 50, 30), width=3)
    for site in sites:
        poly = rect_poly(site["rect"])
        fill = (176, 132, 72) if site["id"] == "townhall" else (232, 220, 190)
        g.polygon(poly, outline=(40, 32, 24), fill=fill)
        cx = sum(p[0] for p in poly) / 4
        cy = sum(p[1] for p in poly) / 4
        g.text((cx - 18, cy - 8), site["id"], fill=(20, 16, 12), font=body)
    for point in points:
        if point["id"] == "dirt-not-foundation":
            continue
        sx, sy = point["source"]
        g.ellipse((sx - 4, sy - 4, sx + 4, sy + 4), fill=(200, 40, 40))
    g.rectangle((28, 588, 620, 742), fill=(255, 248, 230), outline=(40, 32, 24))
    g.text((40, 598), "GUIDE kingdom-stone-day1-composition-v4", fill=(20, 16, 12), font=title)
    g.text((40, 628), "READY_FOR_REVIEW / NOT_OWNER_ACCEPTED", fill=(140, 40, 20), font=body)
    g.text((40, 652), "Labels are guide marks. They must not appear in the painting.", fill=(20, 16, 12), font=body)
    g.text((40, 674), "Gold: Hall ground. Dark line: full roof silhouette. Blue: river.", fill=(20, 16, 12), font=body)
    g.text((40, 696), "Red box: terrace the current terrain does not provide. Brown edge: unbuilt perimeter.", fill=(140, 40, 20), font=body)
    g.text((40, 718), "Right red frame: strip covered by the open panel at 1180x820.", fill=(20, 16, 12), font=body)
    GUIDE_DIR.mkdir(parents=True, exist_ok=True)
    guide_path = GUIDE_DIR / "kingdom-stone-day1-composition-v4-guide.png"
    guide.save(guide_path)
    guide_sha = digest(guide_path)

    measurements = {
        "source": str(HALL.relative_to(ROOT)).replace("\\", "/"),
        "sourceSHA256": hall_sha,
        "annotated": "qa/recovery-executor-20261003/hall-v3-annotated.png",
        "annotatedSHA256": digest(ann_path),
        "displayPlate": "qa/recovery-executor-20261003/hall-v3-at-proposed-348px.png",
        "magentaLikePixelsAt348px": magenta,
        "matteRepair": "none — flecks at this display size are not a new interior hole",
        "opaqueBounds": measured["opaqueBounds"],
        "highestRoof": measured["highestRoof"],
        "roofPeaks": measured["roofPeaks"],
        "dirtBottomMedian": measured["dirtBottomMedian"],
        "points": points,
        "notUsedAsFoundation": {
            "band": "555px lowest non-thatch silhouette",
            "reason": "That band includes dirt and the plinth. Point (160, 800) is dirt. Scale 0.3288 is not the candidate scale.",
        },
        "scaleNotAuthoritative": 0.3288,
    }
    (OUT / "hall-v3-physical-measurements.json").write_text(json.dumps(measurements, indent=2) + "\n", encoding="utf-8")
    candidate["guide"] = {
        "file": "qa/recovery-executor-20261003/guides/kingdom-stone-day1-composition-v4-guide.png",
        "sha256": guide_sha,
        "size": list(SOURCE),
        "aspect": "1376x768 shared kingdom source frame (same size as kingdom.png; 16:9-class landscape, ratio 1.792)",
        "status": "READY_FOR_REVIEW",
        "ownerAcceptance": "NOT_OWNER_ACCEPTED",
        "labelsAllowed": True,
        "labelsMustNotAppearInFinalArt": True,
    }
    candidate["checks"] = {"sites": 18, "upper": 9, "lower": 8, "roadClearOfPlots": True, "hallEnvelopeInsideFrame": True, "uniformScale": SCALE}
    (OUT / "kingdom-layout-candidate.json").write_text(json.dumps(candidate, indent=2) + "\n", encoding="utf-8")
    data = {"candidate": candidate, "current": {"camera": contract["geometry"]["kingdom"]["worldToSource"], "sourceSize": contract["geometry"]["kingdom"]["sourceSize"], "sites": contract["geometry"]["kingdom"]["sites"], "roads": contract["geometry"]["kingdom"]["roads"], "blocked": contract["geometry"]["kingdom"]["blocked"], "bridges": contract["geometry"]["kingdom"]["bridges"], "hall": scene["hall"], "terrain": scene["terrain"]}}
    # Roof contour is large; the preview uses the sprite rect and survey points.
    preview_data = json.loads(json.dumps(data))
    (PREVIEW / "kingdom-layout-candidate-data.js").write_text("globalThis.KINGDOM_CANDIDATE = " + json.dumps(preview_data) + ";\n", encoding="utf-8")
    meta = {
        "requestId": "kingdom-stone-day1-composition-v4",
        "status": "READY_FOR_REVIEW",
        "ownerAcceptance": "NOT_OWNER_ACCEPTED",
        "guide": candidate["guide"],
        "camera": list(CAM),
        "sourceSize": list(SOURCE),
        "hall": candidate["hall"],
        "surveyPoints": points,
        "sites": sites,
        "roads": roads,
        "bridges": candidate["geometry"]["bridges"],
        "blockedRiverColumn": 13,
        "missingTerrain": missing,
        "viewportSafe": safe,
        "safeFrame": [24, 24, SOURCE[0] - 24, SOURCE[1] - 24],
        "note": "Input guide only. The batch AI copies an accepted guide into its own records later. This file is not a batch submission.",
    }
    (GUIDE_DIR / "kingdom-stone-day1-composition-v4-guide.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"guide": guide_sha[:16], "contractUnchanged": contract_sha[:16], "magenta348": magenta, "sites": 18}, indent=2))

if __name__ == "__main__":
    main()
