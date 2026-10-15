"""Project legal roads, banks, decks, obstacles, approaches, and lanes
through the frozen worldToSource onto each runtime painting's own pixels.

A colour sample is recorded and is never the pass predicate. This script
does not move legal cells and does not call the colour-mask closer.
"""
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "scene-trace.json"
AGES = ["stone", "bronze", "iron", "medieval", "gunpowder", "industrial", "modern", "future"]
CONTRACT = json.loads((ROOT / "src/data/implementation-contract.json").read_text(encoding="utf-8"))
MODES = json.loads((ROOT / "src/data/mode-scenes.json").read_text(encoding="utf-8"))
SELECTION = json.loads((ROOT / "src/data/reviewed-source-selection.json").read_text(encoding="utf-8"))


def project(matrix, point):
    a, b, c, d, e, f = matrix
    x, y = point
    return (a * x + c * y + e, b * x + d * y + f)


def scale_point(point, scale_x, scale_y):
    return (point[0] * scale_x, point[1] * scale_y)


def polyline(points, step):
    found = []
    tangents = []
    for start, end in zip(points, points[1:]):
        length = math.hypot(end[0] - start[0], end[1] - start[1])
        count = max(1, int(math.ceil(length / step)))
        for index in range(count):
            t = index / count
            x = start[0] + (end[0] - start[0]) * t
            y = start[1] + (end[1] - start[1]) * t
            found.append((x, y))
            tangents.append((end[0] - start[0], end[1] - start[1]))
    if points:
        found.append(tuple(points[-1]))
        if tangents:
            tangents.append(tangents[-1])
        else:
            tangents.append((1, 0))
    return found, tangents


def cell_contains(cell, point):
    return cell[0] <= point[0] < cell[0] + 1 and cell[1] <= point[1] < cell[1] + 1


def rect_contains(rect, point):
    x, y, w, h = rect
    return x <= point[0] < x + w and y <= point[1] < y + h


def bank_segments(blocked, bridge_cells):
    blocked_set = {tuple(cell) for cell in blocked}
    bridge = {tuple(cell) for cell in bridge_cells}
    segments = []
    for cell in blocked_set:
        if cell in bridge:
            continue
        x, y = cell
        for neighbor, start, end in (
            ((x - 1, y), (x, y), (x, y + 1)),
            ((x + 1, y), (x + 1, y), (x + 1, y + 1)),
            ((x, y - 1), (x, y), (x + 1, y)),
            ((x, y + 1), (x, y + 1), (x + 1, y + 1)),
        ):
            if neighbor not in blocked_set:
                segments.append((start, end))
    return segments


def source_of(matrix, scale_x, scale_y, point):
    return scale_point(project(matrix, point), scale_x, scale_y)


def edge_agreement(gray, samples, tangents):
    height, width = gray.shape
    gradient_y, gradient_x = np.gradient(gray.astype(np.float32))
    compared = 0
    aligned = 0
    control_compared = 0
    control_strong = 0
    rgb_note = []
    for (x, y), tangent in zip(samples, tangents):
        px = int(round(x))
        py = int(round(y))
        if px < 1 or py < 1 or px >= width - 1 or py >= height - 1:
            continue
        compared += 1
        tx, ty = tangent
        length = math.hypot(tx, ty) or 1
        normal_x, normal_y = -ty / length, tx / length
        gx = float(gradient_x[py, px])
        gy = float(gradient_y[py, px])
        magnitude = math.hypot(gx, gy)
        alignment = abs(gx * normal_x + gy * normal_y) / (magnitude + 1e-6)
        if magnitude > 18 and alignment > 0.75:
            aligned += 1
        cx = int(round(x + normal_x * 22))
        cy = int(round(y + normal_y * 22))
        if 1 <= cx < width - 1 and 1 <= cy < height - 1:
            control_compared += 1
            if math.hypot(float(gradient_x[cy, cx]), float(gradient_y[cy, cx])) > 18:
                control_strong += 1
    agreement = (aligned / compared) if compared else 0
    control = (control_strong / control_compared) if control_compared else 1
    return {
        "samples": compared,
        "aligned": aligned,
        "agreement": round(agreement, 4),
        "controlAgreement": round(control, 4),
        "localized": compared >= 8 and agreement >= 0.35 and agreement > control + 0.12,
    }


def median_rgb(rgb, samples):
    height, width = rgb.shape[:2]
    picked = []
    for x, y in samples[:: max(1, len(samples) // 24)]:
        px = int(round(x))
        py = int(round(y))
        if 0 <= px < width and 0 <= py < height:
            picked.append(rgb[py, px])
    if not picked:
        return None
    stack = np.stack(picked)
    return [int(value) for value in np.median(stack, axis=0)]


def trace_features(geo, matrix, scale_x, scale_y, rgb, gray):
    roads = geo.get("roads") or []
    obstacles = [tuple(cell) for cell in geo.get("obstacles") or []]
    blocked = [tuple(cell) for cell in geo.get("blocked") or []]
    bridges = geo.get("bridges") or []
    bridge_cells = [tuple(cell) for bridge in bridges for cell in bridge.get("cells") or []]
    lane = geo.get("lane") or []
    road_world, road_tangent = [], []
    for road in roads:
        points, tangents = polyline(road, 0.2)
        road_world.extend(points)
        road_tangent.extend(tangents)
    road_source = [source_of(matrix, scale_x, scale_y, point) for point in road_world]
    obstacle_hits = []
    blocked_hits = []
    for point, source in zip(road_world, road_source):
        if any(cell_contains(cell, point) for cell in obstacles):
            obstacle_hits.append([round(source[0], 2), round(source[1], 2)])
        if any(cell_contains(cell, point) for cell in blocked) and not any(cell_contains(cell, point) for cell in bridge_cells):
            blocked_hits.append([round(source[0], 2), round(source[1], 2)])
    banks = bank_segments(blocked, bridge_cells)
    bank_world, bank_tangent = [], []
    for start, end in banks:
        points, tangents = polyline([start, end], 0.25)
        bank_world.extend(points)
        bank_tangent.extend(tangents)
    bank_source = [source_of(matrix, scale_x, scale_y, point) for point in bank_world]
    lane_world, lane_tangent = polyline(lane, 0.25) if lane else ([], [])
    lane_source = [source_of(matrix, scale_x, scale_y, point) for point in lane_world]
    lane_obstacle = []
    for point, source in zip(lane_world, lane_source):
        if any(cell_contains(cell, point) for cell in obstacles):
            lane_obstacle.append([round(source[0], 2), round(source[1], 2)])
    decks = []
    for bridge in bridges:
        rect = bridge.get("rect")
        if not rect:
            continue
        x, y, w, h = rect
        centerline = [(x, y + h / 2), (x + w, y + h / 2)] if w >= h else [(x + w / 2, y), (x + w / 2, y + h)]
        deck_world, deck_tangent = polyline(centerline, 0.15)
        deck_source = [source_of(matrix, scale_x, scale_y, point) for point in deck_world]
        road_inside = []
        for point, source in zip(road_world, road_source):
            if rect_contains(rect, point):
                road_inside.append([round(source[0], 2), round(source[1], 2)])
        decks.append({
            "id": bridge.get("id"),
            "rect": rect,
            "approaches": bridge.get("approaches") or [],
            "roadIntersections": road_inside[:12],
            "roadIntersectionCount": len(road_inside),
            "edge": edge_agreement(gray, deck_source, deck_tangent),
            "medianRgb": median_rgb(rgb, deck_source),
        })
    approaches = []
    for site in geo.get("sites") or []:
        anchor = site.get("approach")
        if anchor is None and site.get("rect"):
            rect = site["rect"]
            anchor = [rect[0] + rect[2] / 2, rect[1] + rect[3]]
        if anchor is None:
            continue
        source = source_of(matrix, scale_x, scale_y, anchor)
        nearest = None
        if road_source:
            nearest = min(math.hypot(source[0] - other[0], source[1] - other[1]) for other in road_source)
        approaches.append({
            "id": site.get("id"),
            "world": anchor,
            "source": [round(source[0], 2), round(source[1], 2)],
            "nearestRoadPx": None if nearest is None else round(nearest, 2),
        })
    road_edge = edge_agreement(gray, road_source, road_tangent)
    bank_edge = edge_agreement(gray, bank_source, bank_tangent) if bank_source else None
    lane_edge = edge_agreement(gray, lane_source, lane_tangent) if lane_source else None
    return {
        "roads": {
            "polylines": len(roads),
            "samples": len(road_source),
            "obstacleIntersections": obstacle_hits[:12],
            "obstacleIntersectionCount": len(obstacle_hits),
            "blockedIntersections": blocked_hits[:12],
            "blockedIntersectionCount": len(blocked_hits),
            "edge": road_edge,
            "medianRgb": median_rgb(rgb, road_source),
        },
        "banks": {
            "segments": len(banks),
            "samples": len(bank_source),
            "edge": bank_edge,
            "medianRgb": median_rgb(rgb, bank_source) if bank_source else None,
        },
        "decks": decks,
        "obstacles": {"cells": len(obstacles)},
        "approaches": approaches,
        "lanes": {
            "present": bool(lane),
            "samples": len(lane_source),
            "obstacleIntersections": lane_obstacle[:12],
            "obstacleIntersectionCount": len(lane_obstacle),
            "edge": lane_edge,
            "medianRgb": median_rgb(rgb, lane_source) if lane_source else None,
        },
    }


def agrees(features):
    roads = features["roads"]
    if roads["samples"] < 8:
        return False, "The legal road has fewer than 8 paintable samples."
    if roads["obstacleIntersectionCount"] or roads["blockedIntersectionCount"]:
        return False, "Legal road samples intersect an obstacle or a blocked cell outside a bridge deck."
    if not roads["edge"]["localized"]:
        return False, "The painting has no localized edge along the legal road."
    banks = features["banks"]
    if banks["samples"] and not banks["edge"]["localized"]:
        return False, "The painting has no localized edge along the legal bank."
    lanes = features["lanes"]
    if lanes["present"] and not (lanes["edge"] and lanes["edge"]["localized"]):
        return False, "The painting has no localized edge along the legal lane."
    if lanes["obstacleIntersectionCount"]:
        return False, "Legal lane samples intersect an obstacle cell."
    for deck in features["decks"]:
        if not deck["edge"]["localized"]:
            return False, f"The painting has no localized edge along deck {deck['id']}."
    return True, "Legal roads, banks, decks, and lanes meet localized edges on this painting."


def painting_path(mode, age_name, index):
    if mode == "kingdom":
        chosen = SELECTION["kingdomTerrain"][age_name]
        return chosen.get("displayFile") or chosen["sourceFile"]
    return MODES[mode][index]


def main():
    rows = []
    for mode in ("kingdom", "adventure", "tactical", "defense"):
        geo = CONTRACT["geometry"][mode]
        matrix = geo["worldToSource"]
        source_w, source_h = geo["sourceSize"]
        for index, age_name in enumerate(AGES):
            path = painting_path(mode, age_name, index)
            file_path = ROOT / path
            row = {"scene": mode, "age": index, "ageName": age_name, "source": path}
            if not file_path.is_file():
                row.update({
                    "geometryGate": "BLOCKED",
                    "reviewNotes": "Named runtime painting is absent. No paid call. Live budget, lock, and UNKNOWN jobs were not treated as spendable.",
                    "paidCall": False,
                })
                rows.append(row)
                continue
            image = Image.open(file_path).convert("RGB")
            rgb = np.asarray(image)
            gray = np.asarray(image.convert("L"))
            scale_x = image.width / source_w
            scale_y = image.height / source_h
            features = trace_features(geo, matrix, scale_x, scale_y, rgb, gray)
            passed, reason = agrees(features)
            row.update({
                "nativeWidth": image.width,
                "nativeHeight": image.height,
                "worldToSource": matrix,
                "sourceScale": [scale_x, scale_y],
                "features": features,
                "geometryGate": "PASS" if passed else "FAIL",
                "reviewNotes": reason,
                "colourUsedAsPassPredicate": False,
            })
            rows.append(row)
    passed = sum(row["geometryGate"] == "PASS" for row in rows)
    report = {
        "method": "Each runtime painting's own pixels. Frozen worldToSource. Legal roads, bank edges, bridge decks, obstacles, site approaches, and lanes. Localized edge agreement is the pass predicate. Median RGB is recorded and cannot promote a row.",
        "predecessor": "1376x768 blue-water sample, rejected. A missing saturated-blue hit is not acceptance.",
        "closerScriptRun": False,
        "legalCellsMoved": False,
        "paidCall": False,
        "acceptance": "PASS" if passed == len(rows) else "NOT_ACCEPTED",
        "pass": passed,
        "fail": sum(row["geometryGate"] == "FAIL" for row in rows),
        "blocked": sum(row["geometryGate"] == "BLOCKED" for row in rows),
        "rows": rows,
    }
    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"pass={report['pass']} fail={report['fail']} blocked={report['blocked']} acceptance={report['acceptance']}")


if __name__ == "__main__":
    main()
