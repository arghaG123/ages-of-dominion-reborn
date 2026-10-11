"""Geometry utilities for Environment Residual Executor (2026-10-07).
Computes exact polyline/polygon clearances, transformations across Grid, Legal, and Native frames,
and validates full-footprint clearance against uncertainty margins.
"""
import math
from typing import List, Tuple, Dict, Any

# Frozen Kingdom Active Frame
FROZEN_AFFINE = [60.0, -10.0, 25.0, 35.0, 170.0, 165.0]
HALL_SCALE = 0.1312
LEGAL_WH = (1376, 768)
NATIVE_WH = (5504, 3072)
NATIVE_SCALE = 4.0

def grid_to_legal(col: float, row: float, affine: List[float] = FROZEN_AFFINE) -> Tuple[float, float]:
    a, b, c, d, e, f = affine
    x = a * col + c * row + e
    y = b * col + d * row + f
    return (x, y)

def legal_to_native(x_legal: float, y_legal: float) -> Tuple[float, float]:
    return (x_legal * NATIVE_SCALE, y_legal * NATIVE_SCALE)

def native_to_legal(x_native: float, y_native: float) -> Tuple[float, float]:
    return (x_native / NATIVE_SCALE, y_native / NATIVE_SCALE)

def pad_rect_to_legal_polygon(rect: List[float], affine: List[float] = FROZEN_AFFINE) -> List[Tuple[float, float]]:
    col, row, w, h = rect
    c1 = grid_to_legal(col, row, affine)
    c2 = grid_to_legal(col + w, row, affine)
    c3 = grid_to_legal(col + w, row + h, affine)
    c4 = grid_to_legal(col, row + h, affine)
    return [c1, c2, c3, c4]

def point_to_segment_dist(px: float, py: float, x1: float, y1: float, x2: float, y2: float) -> float:
    dx = x2 - x1
    dy = y2 - y1
    if dx == 0 and dy == 0:
        return math.hypot(px - x1, py - y1)
    t = ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))
    proj_x = x1 + t * dx
    proj_y = y1 + t * dy
    return math.hypot(px - proj_x, py - proj_y)

def segments_intersect(x1: float, y1: float, x2: float, y2: float,
                       x3: float, y3: float, x4: float, y4: float) -> bool:
    def ccw(ax, ay, bx, by, cx, cy):
        return (cy - ay) * (bx - ax) > (by - ay) * (cx - ax)
    return (ccw(x1, y1, x3, y3, x4, y4) != ccw(x2, y2, x3, y3, x4, y4)) and \
           (ccw(x1, y1, x2, y2, x3, y3) != ccw(x1, y1, x2, y2, x4, y4))

def segment_to_segment_dist(x1: float, y1: float, x2: float, y2: float,
                            x3: float, y3: float, x4: float, y4: float) -> float:
    if segments_intersect(x1, y1, x2, y2, x3, y3, x4, y4):
        return 0.0
    d1 = point_to_segment_dist(x1, y1, x3, y3, x4, y4)
    d2 = point_to_segment_dist(x2, y2, x3, y3, x4, y4)
    d3 = point_to_segment_dist(x3, y3, x1, y1, x2, y2)
    d4 = point_to_segment_dist(x4, y4, x1, y1, x2, y2)
    return min(d1, d2, d3, d4)

def polyline_to_polygon_dist(polyline: List[Tuple[float, float]], polygon: List[Tuple[float, float]]) -> float:
    min_dist = float("inf")
    poly_edges = []
    n = len(polygon)
    for i in range(n):
        poly_edges.append((polygon[i], polygon[(i + 1) % n]))

    for j in range(len(polyline) - 1):
        p1 = polyline[j]
        p2 = polyline[j + 1]
        for edge in poly_edges:
            e1, e2 = edge
            d = segment_to_segment_dist(p1[0], p1[1], p2[0], p2[1], e1[0], e1[1], e2[0], e2[1])
            if d < min_dist:
                min_dist = d
                if min_dist == 0.0:
                    return 0.0
    return min_dist

def check_clearance(polyline_native: List[List[float]],
                    pad_rect: List[float],
                    corridor_radius_legal: float = 8.0,
                    uncertainty_legal: float = 12.0) -> Dict[str, Any]:
    """Check clearance between a native polyline and a grid-defined pad in legal px."""
    poly_legal = [native_to_legal(pt[0], pt[1]) for pt in polyline_native]
    pad_poly_legal = pad_rect_to_legal_polygon(pad_rect)
    dist_legal = polyline_to_polygon_dist(poly_legal, pad_poly_legal)
    required_clearance = corridor_radius_legal + uncertainty_legal
    passes = dist_legal > required_clearance
    return {
        "distLegal": round(dist_legal, 2),
        "requiredLegal": required_clearance,
        "clearanceMargin": round(dist_legal - required_clearance, 2),
        "passed": passes
    }
