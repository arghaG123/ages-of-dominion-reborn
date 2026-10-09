"""Frozen-frame geometry for the 9 October 2026 environment repair.

Adapted from the read-only residual helper. Affine and Hall scale stay byte-identical.
x' = a*x + c*y + e; y' = b*x + d*y + f; +y down.
"""
from __future__ import annotations

import math
from typing import Any, Dict, List, Sequence, Tuple

FROZEN_AFFINE = [60.0, -10.0, 25.0, 35.0, 170.0, 165.0]
HALL_SCALE = 0.1312
LEGAL_WH = (1376, 768)
NATIVE_WH = (5504, 3072)
NATIVE_SCALE = 4.0


def grid_to_legal(col: float, row: float, affine: Sequence[float] = FROZEN_AFFINE) -> Tuple[float, float]:
    a, b, c, d, e, f = affine
    return (a * col + c * row + e, b * col + d * row + f)


def legal_to_native(x_legal: float, y_legal: float) -> Tuple[float, float]:
    return (x_legal * NATIVE_SCALE, y_legal * NATIVE_SCALE)


def native_to_legal(x_native: float, y_native: float) -> Tuple[float, float]:
    return (x_native / NATIVE_SCALE, y_native / NATIVE_SCALE)


def apply_affine(affine: Sequence[float], x: float, y: float) -> Tuple[float, float]:
    a, b, c, d, e, f = affine
    return (a * x + c * y + e, b * x + d * y + f)


def pad_rect_to_legal_polygon(rect: Sequence[float], affine: Sequence[float] = FROZEN_AFFINE) -> List[Tuple[float, float]]:
    col, row, w, h = rect
    return [
        grid_to_legal(col, row, affine),
        grid_to_legal(col + w, row, affine),
        grid_to_legal(col + w, row + h, affine),
        grid_to_legal(col, row + h, affine),
    ]


def point_to_segment_dist(px: float, py: float, x1: float, y1: float, x2: float, y2: float) -> float:
    dx = x2 - x1
    dy = y2 - y1
    if dx == 0 and dy == 0:
        return math.hypot(px - x1, py - y1)
    t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))


def segments_intersect(x1, y1, x2, y2, x3, y3, x4, y4) -> bool:
    def ccw(ax, ay, bx, by, cx, cy):
        return (cy - ay) * (bx - ax) > (by - ay) * (cx - ax)

    return (ccw(x1, y1, x3, y3, x4, y4) != ccw(x2, y2, x3, y3, x4, y4)) and (
        ccw(x1, y1, x2, y2, x3, y3) != ccw(x1, y1, x2, y2, x4, y4)
    )


def segment_to_segment_dist(x1, y1, x2, y2, x3, y3, x4, y4) -> float:
    if segments_intersect(x1, y1, x2, y2, x3, y3, x4, y4):
        return 0.0
    return min(
        point_to_segment_dist(x1, y1, x3, y3, x4, y4),
        point_to_segment_dist(x2, y2, x3, y3, x4, y4),
        point_to_segment_dist(x3, y3, x1, y1, x2, y2),
        point_to_segment_dist(x4, y4, x1, y1, x2, y2),
    )


def polyline_to_polygon_dist(polyline: Sequence[Tuple[float, float]], polygon: Sequence[Tuple[float, float]]) -> float:
    if len(polyline) < 2 or len(polygon) < 2:
        return float("inf")
    min_dist = float("inf")
    n = len(polygon)
    edges = [(polygon[i], polygon[(i + 1) % n]) for i in range(n)]
    for j in range(len(polyline) - 1):
        p1, p2 = polyline[j], polyline[j + 1]
        for e1, e2 in edges:
            d = segment_to_segment_dist(p1[0], p1[1], p2[0], p2[1], e1[0], e1[1], e2[0], e2[1])
            if d < min_dist:
                min_dist = d
                if min_dist == 0.0:
                    return 0.0
    return min_dist


def polygon_to_polygon_dist(poly_a: Sequence[Tuple[float, float]], poly_b: Sequence[Tuple[float, float]]) -> float:
    """Edge distance. Zero when an edge pair intersects. Does not treat full containment as zero."""
    return min(polyline_to_polygon_dist(list(poly_a) + [poly_a[0]], poly_b), polyline_to_polygon_dist(list(poly_b) + [poly_b[0]], poly_a))
