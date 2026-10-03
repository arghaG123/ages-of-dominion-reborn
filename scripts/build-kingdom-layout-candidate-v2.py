"""Measured Stone Kingdom candidate v2.

Does not edit the active contract, the live scene, submitted batch 14, or the budget ledger.
"""
from pathlib import Path
import hashlib, json
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
HALL = ROOT / "assets/delivery/stone-starter-20261003/derivatives/v3/townhall-stone.png"
TERRAIN = ROOT / "assets/production/production-01-20261003/images/01-kingdom-terrain-stone.png"
PAINT = ROOT / "assets/production/production-14-20261003/images/30-kingdom-stone-day1-composition-v4.png"
SUBMITTED_GUIDE = ROOT / "docs/plan/image-production/guides/kingdom-stone-day1-composition-v4.png"
RECOVERY_GUIDE = ROOT / "qa/recovery-executor-20261003/guides/kingdom-stone-day1-composition-v4-guide.png"
CONTRACT = ROOT / "docs/plan/IMPLEMENTATION-CONTRACT.json"
SCENE = ROOT / "src/data/stone-scene.json"
V1 = ROOT / "qa/recovery-executor-20261003/kingdom-layout-candidate.json"
OUT = ROOT / "qa/recovery-executor-20261003"
GUIDE = OUT / "guides/kingdom-stone-day1-composition-v5-guide.png"
CAM = (60.0, -10.0, 25.0, 35.0, 170.0, 165.0)
SCALE = 0.34
TX = 402.0
TY = 32.86
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

def overlap(a, b):
    return max(a[0], b[0]) < min(a[0] + a[2], b[0] + b[2]) and max(a[1], b[1]) < min(a[1] + a[3], b[1] + b[3])

def source_of(ix, iy):
    return (TX + SCALE * ix, TY + SCALE * iy)

def dist_point_segment(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    length = dx * dx + dy * dy
    if length == 0:
        return ((px - ax) ** 2 + (py - ay) ** 2) ** 0.5
    t = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / length))
    qx, qy = ax + t * dx, ay + t * dy
    return ((px - qx) ** 2 + (py - qy) ** 2) ** 0.5

def survey(im):
    px = im.load()
    w, h = im.size
    def mason(x, y):
        if not (0 <= x < w and 0 <= y < h):
            return False
        r, g, b, a = px[x, y]
        return a > 16 and (r + g + b) / 3 > 145 and (r - b) < 78 and r > 125 and g > 95 and b > 70
    raw = []
    for x in range(0, w, 4):
        runs, start, end = [], None, None
        for y in range(640, h):
            if mason(x, y):
                if start is None:
                    start = y
                end = y
            elif start is not None:
                if end - start >= 6:
                    runs.append((start, end))
                start = None
        if start is not None and end is not None and end - start >= 6:
            runs.append((start, end))
        if runs:
            raw.append((x, runs[0][1]))
    values = [point[1] for point in raw]
    smooth = []
    for index, (x, _) in enumerate(raw):
        window = sorted(values[max(0, index - 8):index + 9])
        smooth.append((x, window[len(window) // 2]))
    samples = []
    for x, y0 in smooth:
        last, gap = y0, 0
        for y in range(y0, min(h - 1, y0 + 80)):
            if mason(x, y):
                last, gap = y, 0
            else:
                gap += 1
                if gap > 14:
                    break
        samples.append([x, last])
    gaps = []
    for index in range(1, len(samples)):
        if samples[index][0] - samples[index - 1][0] > 24 or abs(samples[index][1] - samples[index - 1][1]) > 70:
            gaps.append({"from": samples[index - 1], "to": samples[index], "confidence": "occluded", "kind": "break in the visible front wall; hidden threshold or corner, not an invented point"})
    pink = []
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a > 16 and r > 180 and b > 140 and g < 110:
                pink.append((x, y))
    fringe = 0
    for x, y in pink:
        if any(px[nx, ny][3] <= 16 for nx in range(max(0, x - 2), min(w, x + 3)) for ny in range(max(0, y - 2), min(h, y + 3))):
            fringe += 1
    window = [point for point in pink if abs(point[0] - 1006) <= 40 and abs(point[1] - 486) <= 40]
    return {
        "samples": samples[::2],
        "gaps": gaps,
        "chains": 1 if samples else 0,
        "pinkOpaque": len(pink),
        "pinkTouchingTransparency": fringe,
        "pinkNear1006x486": len(window),
        "matteRepair": "none",
    }

def panel_source(vw, vh, chrome):
    stage_h = vh - chrome
    scale = min(vw / 1376, stage_h / 768)
    offset_x = (vw - 1376 * scale) / 2
    narrow = vh <= 450
    panel_w = min(240 if narrow else 280, (0.40 if narrow else 0.34) * vw)
    panel_left = vw - 8 - panel_w
    return {
        "viewport": [vw, vh],
        "chromePx": chrome,
        "stageHeight": stage_h,
        "scale": round(scale, 5),
        "offsetX": round(offset_x, 2),
        "panelLeftCss": round(panel_left, 2),
        "panelLeftSourceX": round((panel_left - offset_x) / scale, 2),
    }

def rect_source_bounds(rect):
    x, y, w, h = rect
    corners = [project(x, y), project(x + w, y), project(x + w, y + h), project(x, y + h)]
    xs = [p[0] for p in corners]
    ys = [p[1] for p in corners]
    return min(xs), min(ys), max(xs), max(ys)

def main():
    v1 = json.loads(V1.read_text(encoding="utf-8"))
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    scene = json.loads(SCENE.read_text(encoding="utf-8"))
    assert digest(CONTRACT) == "43553411b583a6df5fdcf620d2b3efecd82a0cd6f783895165a5910e577b0fcd"
    assert scene["hall"]["matrix"][0][0] == 0.1312
    hall = Image.open(HALL).convert("RGBA")
    measured = survey(hall)
    world_points = []
    source_points = []
    for ix, iy in measured["samples"]:
        sx, sy = source_of(ix, iy)
        wx, wy = inverse(sx, sy)
        source_points.append([round(sx, 2), round(sy, 2)])
        world_points.append([round(wx, 4), round(wy, 4)])
    xs = [p[0] for p in world_points]
    ys = [p[1] for p in world_points]
    aabb = [round(min(xs), 3), round(min(ys), 3), round(max(xs) - min(xs), 3), round(max(ys) - min(ys), 3)]
    plots = [site for site in v1["geometry"]["sites"] if site["id"] != "townhall"]
    use_aabb = all(not overlap(aabb, site["rect"]) for site in plots) and aabb[0] >= 0 and aabb[1] >= 0 and aabb[0] + aabb[2] <= 14 and aabb[1] + aabb[3] <= 11
    townhall_rect = aabb if use_aabb else v1["geometry"]["sites"][0]["rect"]
    sites = [{"id": "townhall", "rect": townhall_rect, "role": "civic-hall"}] + plots
    plinth = (400, 820)
    cobble = (700, 760)
    def nearest(ix, iy):
        sx, sy = source_of(ix, iy)
        best = min(dist_point_segment(sx, sy, *source_points[i], *source_points[i + 1]) for i in range(len(source_points) - 1))
        return round(best, 2)
    plinth_px = nearest(*plinth)
    cobble_px = nearest(*cobble)
    # The known plinth is several pixels off the polyline, and the right corner still changes course.
    # A 4px band would exclude that measured residual.
    tolerance_px = max(20, int(plinth_px) + 1)
    roof_y = round(TY + SCALE * 21, 2)
    dirt_y = round(TY + SCALE * 999, 2)
    review = [panel_source(*size, 92) for size in VIEWPORTS]
    runtime = [panel_source(*size, 112) for size in VIEWPORTS]
    hall_height = max(p[1] for p in source_points) - roof_y
    hall_width = max(p[0] for p in source_points) - min(p[0] for p in source_points)
    structures = []
    for site in plots:
        left, top, right, bottom = rect_source_bounds(site["rect"])
        width = max(8, right - left)
        height = hall_height * (width / hall_width)
        door = project(site["rect"][0] + site["rect"][2] / 2, site["rect"][1] + site["rect"][3])
        structures.append({
            "id": site["id"],
            "art": "NO_ISOLATED_STONE_SPRITE",
            "silhouette": "uniform scale of the measured Hall v3 contact-to-roof height; not an arbitrary fixture box",
            "door": [round(door[0], 2), round(door[1], 2)],
            "body": [round(left, 2), round(door[1] - height, 2), round(width, 2), round(height, 2)],
            "depth": round(door[1], 2),
        })
    structures.sort(key=lambda item: item["depth"])
    relations = []
    for i, near in enumerate(structures):
        nx, ny, nw, nh = near["body"]
        for far in structures[:i]:
            fx, fy = far["door"]
            body_hits = nx <= fx <= nx + nw and ny <= fy <= ny + nh
            ox = max(nx, far["body"][0]) < min(nx + nw, far["body"][0] + far["body"][2])
            oy = max(ny, far["body"][1]) < min(ny + nh, far["body"][1] + far["body"][3])
            if body_hits:
                relations.append({"near": near["id"], "far": far["id"], "class": "blocking", "reason": "The nearer body covers the far door."})
            elif ox and oy:
                relations.append({"near": near["id"], "far": far["id"], "class": "acceptable", "reason": "Source envelopes overlap, and the far door stays outside the nearer body."})
    for entry in review:
        entry["occludedSites"] = []
        for structure in structures:
            left, top, right, bottom = structure["body"][0], structure["body"][1], structure["body"][0] + structure["body"][2], structure["body"][1] + structure["body"][3]
            site = next(site for site in plots if site["id"] == structure["id"])
            _, _, site_right, _ = rect_source_bounds(site["rect"])
            if site_right > entry["panelLeftSourceX"]:
                entry["occludedSites"].append({"id": structure["id"], "centreClear": project(site["rect"][0] + site["rect"][2] / 2, site["rect"][1] + site["rect"][3] / 2)[0] < entry["panelLeftSourceX"], "footprintCrossesPanel": True})
    paint = Image.open(PAINT).convert("RGBA")
    submitted = Image.open(SUBMITTED_GUIDE).convert("RGBA")
    blue_rows = []
    step = max(1, paint.size[1] // 180)
    pixels = paint.load()
    for y in range(0, paint.size[1], step):
        blue = 0
        for x in range(0, paint.size[0], 6):
            r, g, b, _ = pixels[x, y]
            if b > 70 and b > r + 12 and b > g:
                blue += 1
        if blue > paint.size[0] / 6 / 12:
            blue_rows.append(y)
    painting = {
        "file": "assets/production/production-14-20261003/images/30-kingdom-stone-day1-composition-v4.png",
        "sha256": digest(PAINT),
        "size": list(paint.size),
        "submittedGuide": "docs/plan/image-production/guides/kingdom-stone-day1-composition-v4.png",
        "submittedGuideSHA256": digest(SUBMITTED_GUIDE),
        "submittedGuideSize": list(submitted.size),
        "recoveryGuideSHA256": digest(RECOVERY_GUIDE),
        "guidesMatch": digest(SUBMITTED_GUIDE) == digest(RECOVERY_GUIDE),
        "ownerAcceptance": "NOT_OWNER_ACCEPTED",
        "resampledByProvider": list(paint.size) != [1376, 768],
        "blueRowSpan": [min(blue_rows), max(blue_rows)] if blue_rows else None,
        "spatialFidelity": "FAIL",
        "usableSiteCount": "UNVERIFIED",
        "visibleClearings": "About twelve bare dirt pads are visible around the painted hall. The review legend covers the lower left, so this is not a count of seventeen usable sites.",
        "finding": "Preserved as a composition reference. The file is 1376x768 and its hash matches the collected batch 14 output. The painted hall is a different timber building, not Hall v3. The river is a wide right-hand channel with two foreground log spans, not the candidate's single upper-right crossing. Spatial fidelity FAIL. It was not adopted, repurchased, or turned into playable terrain.",
    }
    candidate = {
        "status": "READY_FOR_REVIEW",
        "ownerAcceptance": "NOT_OWNER_ACCEPTED",
        "runtimeApproved": False,
        "activeContractEdited": False,
        "activeSceneEdited": False,
        "activeContractSHA256": digest(CONTRACT),
        "liveHallScale": scene["hall"]["matrix"][0][0],
        "id": "kingdom-layout-candidate-v2",
        "supersedes": "kingdom-layout-candidate-v1",
        "requestId": "kingdom-stone-day1-composition-v4",
        "camera": list(CAM),
        "sourceSize": [1376, 768],
        "scaleRule": "Uniform 0.34 is retained from v1 so the roof stays at source y=40 and the dirt apron ends at source y=372.52. That framing is not physical registration. The contact polygon is the visible stone foot, not a rectangle constructed around the entrance cobble.",
        "rejectedTranslationApplied": False,
        "hall": v1["hall"],
        "contact": {
            "method": "visible-stone-foot",
            "builtAroundCobble": False,
            "confidence": "medium",
            "tolerancePx": tolerance_px,
            "toleranceReason": "The band contains the front-plinth residual and the right-corner course jitter. Rear corners stay unmarked.",
            "imageSamples": measured["samples"],
            "sourceSamples": source_points,
            "worldSamples": world_points,
            "gaps": measured["gaps"],
            "hidden": "The rear wall foot and the two far corners are hidden by the building. They are not given invented coordinates.",
            "aabb": aabb,
            "aabbUsedAsSite": use_aabb,
            "plinthImage": [400, 820],
            "plinthDistanceToContactPx": plinth_px,
            "cobbleImage": [700, 760],
            "cobbleRole": "entrance approach, not a doorway midpoint",
            "cobbleDistanceToContactPx": cobble_px,
            "doorPosts": "The curtain opening has no measured threshold midpoint. Post bases remain partly hidden by the plinth and cobbles.",
            "pinkOpaque": measured["pinkOpaque"],
            "pinkTouchingTransparency": measured["pinkTouchingTransparency"],
            "pinkNear1006x486": measured["pinkNear1006x486"],
            "matteRepair": "none. The pink near image (1006, 486) sits in the dirt apron and is surrounded by opaque ground. Clearing it would invent apron pixels. Hall v3 interior was not repainted.",
        },
        "geometry": {**v1["geometry"], "sites": sites},
        "mature": {
            "art": "NO_ISOLATED_STONE_SPRITE",
            "structures": structures,
            "relations": relations,
            "blocking": sum(item["class"] == "blocking" for item in relations),
            "acceptable": sum(item["class"] == "acceptable" for item in relations),
            "note": "Rectangles alone are not treated as proof. Door coverage is blocking. Envelope overlap that leaves the door clear is acceptable and still depends on a later real sprite.",
        },
        "viewport": {
            "reviewChromePx": 92,
            "runtimeChromeBudgetPx": 112,
            "identical": False,
            "review": review,
            "runtimeBudget": runtime,
            "accessibleSelection": "A site list in the layers panel is the 48px target. Map polygons are not given a second overlapping hit box.",
        },
        "missingTerrain": v1["missingTerrain"],
        "painting": painting,
        "guide": {
            "file": "qa/recovery-executor-20261003/guides/kingdom-stone-day1-composition-v5-guide.png",
            "status": "READY_FOR_REVIEW",
            "ownerAcceptance": "NOT_OWNER_ACCEPTED",
            "submittedGuideUnchanged": True,
            "legend": "outside the roof and the contact samples",
        },
        "decision": "Adopt the kingdom-layout-candidate-v2 spatial arrangement, or revise it. Adopting it does not accept the batch 14 painting, this guide, the runtime scene, a native build, or any spend.",
        "deliveryPlan": {
            "recoverableReference": "Batch 14 lighting, stone material, full roof and natural ground can guide a later separated painting.",
            "unavailable": "Seventeen clear sites, the guide crossing, and the Hall v3 subject are not in the collected painting. Hidden pixels were not invented.",
            "localProcessing": "Overlay and measurement only. No inpaint, blur, flat fill, or new matte.",
            "repurchase": "not requested",
        },
    }
    candidate["hall"]["spriteSourceRect"] = [round(TX, 2), roof_y, round(TX + SCALE * 1023, 2), dirt_y]
    out_json = OUT / "kingdom-layout-candidate-v2.json"
    out_json.write_text(json.dumps(candidate, indent=2) + "\n", encoding="utf-8")
    plate = Image.new("RGBA", (1400, 1024), (16, 23, 27, 255))
    plate.paste(hall, (0, 0), hall)
    draw = ImageDraw.Draw(plate)
    ink = font(18)
    if len(measured["samples"]) > 1:
        draw.line([tuple(p) for p in measured["samples"]], fill=(112, 185, 197, 255), width=3)
    for point in measured["samples"][::8]:
        draw.ellipse((point[0] - 4, point[1] - 4, point[0] + 4, point[1] + 4), outline=(241, 233, 217, 255))
    draw.text((1048, 40), "Legend outside\nthe measured hall.\nCyan: visible stone\nfoot. Rear corners\nare hidden.\nCobble is approach,\nnot the door centre.\nNo matte repair.", fill=(241, 233, 217, 255), font=ink)
    plate.convert("RGB").save(OUT / "hall-v2-contact-plate.png")
    guide = Image.new("RGBA", (1376, 768), (28, 36, 32, 255))
    g = ImageDraw.Draw(guide)
    label = font(16)
    for road in candidate["geometry"]["roads"]:
        g.line([project(*p) for p in road], fill=(156, 136, 112, 255), width=10)
    for site in sites:
        poly = [project(site["rect"][0], site["rect"][1]), project(site["rect"][0] + site["rect"][2], site["rect"][1]), project(site["rect"][0] + site["rect"][2], site["rect"][1] + site["rect"][3]), project(site["rect"][0], site["rect"][1] + site["rect"][3])]
        g.polygon(poly, outline=(213, 181, 115, 255))
    if len(source_points) > 1:
        g.line([tuple(p) for p in source_points], fill=(112, 185, 197, 255), width=3)
    missing = candidate["missingTerrain"]["sourceRect"]
    g.rectangle(missing, outline=(200, 62, 56, 255), width=3)
    g.rectangle((24, 620, 760, 748), fill=(16, 23, 27, 230), outline=(201, 163, 91, 255))
    g.text((36, 632), "v5 guide  NOT_OWNER_ACCEPTED\nLegend is below the hall roof.\nCyan line: measured stone foot, gaps are hidden.\nRed box: missing terrace, not repaired.\nSites and roads are the v2 arrangement.\nThis file is not the submitted batch 14 guide.", fill=(241, 233, 217, 255), font=label)
    guide.convert("RGB").save(GUIDE)
    candidate["guide"]["sha256"] = digest(GUIDE)
    out_json.write_text(json.dumps(candidate, indent=2) + "\n", encoding="utf-8")
    overlay = paint.copy()
    if overlay.size != (1376, 768):
        overlay = overlay.resize((1376, 768), Image.Resampling.LANCZOS)
    od = ImageDraw.Draw(overlay)
    for site in sites:
        poly = [project(site["rect"][0], site["rect"][1]), project(site["rect"][0] + site["rect"][2], site["rect"][1]), project(site["rect"][0] + site["rect"][2], site["rect"][1] + site["rect"][3]), project(site["rect"][0], site["rect"][1] + site["rect"][3])]
        od.line(poly + [poly[0]], fill=(213, 181, 115, 255), width=2)
    if len(source_points) > 1:
        od.line([tuple(p) for p in source_points], fill=(112, 185, 197, 255), width=3)
    od.rectangle((24, 620, 820, 748), fill=(16, 23, 27, 220))
    od.text((36, 632), "Collected batch 14 painting with the v2 overlay.\nResize is only for this plate when the file is not 1376x768.\nSpatial fidelity FAIL. Not adopted. Not repurchased.\nCyan: measured Hall v3 foot, which this painting does not contain.", fill=(241, 233, 217, 255), font=label)
    overlay.convert("RGB").save(OUT / "batch14-painting-v2-overlay.png")
    current = {
        "camera": contract["geometry"]["kingdom"]["worldToSource"],
        "sourceSize": contract["geometry"]["kingdom"]["sourceSize"],
        "sites": contract["geometry"]["kingdom"]["sites"],
        "roads": contract["geometry"]["kingdom"]["roads"],
        "blocked": contract["geometry"]["kingdom"]["blocked"],
        "bridges": contract["geometry"]["kingdom"]["bridges"],
        "hall": {
            "file": scene["hall"]["file"],
            "sha256": scene["hall"]["sha256"],
            "width": scene["hall"]["width"],
            "height": scene["hall"]["height"],
            "matrix": scene["hall"]["matrix"],
        },
        "terrain": scene["terrain"],
        "painting": str(PAINT.relative_to(ROOT)).replace("\\", "/"),
    }
    data_js = ROOT / "design-preview/kingdom-layout-candidate-data.js"
    data_js.write_text("globalThis.KINGDOM_CANDIDATE = " + json.dumps({"candidate": candidate, "current": current}) + ";\n", encoding="utf-8")
    print(json.dumps({
        "samples": len(measured["samples"]),
        "aabbUsed": use_aabb,
        "plinthPx": plinth_px,
        "cobblePx": cobble_px,
        "tolerancePx": tolerance_px,
        "blocking": candidate["mature"]["blocking"],
        "acceptable": candidate["mature"]["acceptable"],
        "paint": list(paint.size),
        "blue": painting["blueRowSpan"],
        "pink": [measured["pinkOpaque"], measured["pinkTouchingTransparency"], measured["pinkNear1006x486"]],
        "guide": candidate["guide"]["sha256"],
    }, indent=2))

if __name__ == "__main__":
    main()
