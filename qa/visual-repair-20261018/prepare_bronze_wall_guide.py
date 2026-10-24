import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = ROOT / "src/data/implementation-contract.json"
BASE_GUIDE = ROOT / "docs/plan/image-production/guides/kingdom.png"
OUT_GUIDE = ROOT / "qa/visual-repair-20261018/bronze-wall-guide.png"
OUT_TRACE = ROOT / "qa/visual-repair-20261018/bronze-wall-trace.json"

# One gently irregular, terrain-following perimeter in the contract's logical
# grid. It leaves all owned sites inside and has openings for the right bridge
# and the southern road gate. The openings are visual only; no rules change.
PERIMETER = [
    (0.6, 9.0), (0.3, 6.0), (0.4, 3.0), (1.2, 1.2), (2.4, -0.1),
    (4.0, -0.5), (6.5, -0.6), (9.0, -0.3), (11.0, 0.7), (12.1, 2.4),
    (12.4, 4.4), (12.6, 6.3), (12.6, 7.8), (12.5, 8.6), (12.0, 9.5),
    (11.1, 10.1), (8.2, 10.25), (7.2, 10.25), (4.0, 10.25), (1.8, 9.8),
]
WALL_RUNS = [
    PERIMETER[0:12],
    PERIMETER[12:17],
    PERIMETER[17:] + [PERIMETER[0]],
]
GATES = {
    "river-crossing": ((12.6, 6.3), (12.6, 7.8)),
    "south-road": ((8.2, 10.25), (7.2, 10.25)),
}


def point_in_polygon(point, polygon):
    x, y = point
    inside = False
    previous = polygon[-1]
    for current in polygon:
        xi, yi = current
        xj, yj = previous
        if (yi > y) != (yj > y):
            crossing_x = (xj - xi) * (y - yi) / (yj - yi) + xi
            if x < crossing_x:
                inside = not inside
        previous = current
    return inside


def trace_is_clear(geometry):
    samples = []
    for start, end in zip(PERIMETER, PERIMETER[1:] + PERIMETER[:1]):
        length = ((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2) ** 0.5
        count = max(2, round(length * 200))
        samples.extend(
            (start[0] + (end[0] - start[0]) * step / count,
             start[1] + (end[1] - start[1]) * step / count)
            for step in range(count + 1)
        )

    site_failures = []
    for site in geometry["sites"]:
        x, y, width, height = site["rect"]
        corners = ((x, y), (x + width, y), (x + width, y + height), (x, y + height))
        if not all(point_in_polygon(point, PERIMETER) for point in corners):
            site_failures.append(site["id"])

    path_contacts = []
    for point in samples:
        for site in geometry["sites"]:
            x, y, width, height = site["rect"]
            if x <= point[0] <= x + width and y <= point[1] <= y + height:
                path_contacts.append(site["id"])
    return site_failures, sorted(set(path_contacts))


def create_guide(contract, geometry):
    source = Image.open(BASE_GUIDE).convert("RGB")
    expected = tuple(geometry["sourceSize"])
    if source.size != expected:
        raise ValueError(f"Guide size {source.size} != contract source size {expected}")
    draw = ImageDraw.Draw(source, "RGBA")
    matrix = geometry["worldToSource"]

    def project(x, y):
        a, b, c, d, e, f = matrix
        return (round(a * x + c * y + e), round(b * x + d * y + f))

    for run in WALL_RUNS:
        draw.line([project(*point) for point in run], fill=(188, 24, 27, 255), width=9, joint="curve")
    for name, endpoints in GATES.items():
        start, end = (project(*point) for point in endpoints)
        draw.line((start, end), fill=(255, 207, 58, 255), width=11)
        draw.text((start[0] + 7, start[1] - 16), name.upper(), fill=(25, 20, 16, 255))
    draw.text((16, 18), "RED = SAME-FAMILY WALL PATH; GOLD = OPEN GATE", fill=(25, 20, 16, 255))
    source.save(OUT_GUIDE)
    return {
        "status": "GEOMETRY_CANDIDATE",
        "sourceContract": "src/data/implementation-contract.json",
        "contractSHA256": hashlib.sha256(CONTRACT_PATH.read_bytes()).hexdigest(),
        "baseGuide": str(BASE_GUIDE.relative_to(ROOT)).replace("\\", "/"),
        "baseGuideSHA256": hashlib.sha256(BASE_GUIDE.read_bytes()).hexdigest(),
        "sourceSize": expected,
        "worldToSource": matrix,
        "perimeterGrid": PERIMETER,
        "wallRunsGrid": WALL_RUNS,
        "gateOpeningsGrid": GATES,
        "bridges": geometry["bridges"],
        "roads": geometry["roads"],
        "siteCount": len(geometry["sites"]),
        "trace": {"siteCornersOutsidePerimeter": [], "wallTouchesSites": []},
        "wallContactTrace": "NOT_PERFORMED",
        "imageGeneration": "CANDIDATE_ONLY",
        "runtimeBinding": "NONE",
        "ownerAcceptance": "UNVERIFIED",
    }


def main():
    raw = CONTRACT_PATH.read_bytes()
    contract = json.loads(raw)
    geometry = contract["geometry"]["kingdom"]
    failures, contacts = trace_is_clear(geometry)
    result = create_guide(contract, geometry)
    result["trace"] = {
        "siteCornersOutsidePerimeter": failures,
        "wallTouchesSites": contacts,
        "status": "PASS_BOUNDED" if not failures and not contacts else "FAIL",
        "meaning": "Grid-space perimeter containment and no site intersection only; not a native pixel wall/deck/ground contact trace.",
    }
    if result["trace"]["status"] != "PASS_BOUNDED":
        raise RuntimeError(json.dumps(result["trace"]))
    OUT_TRACE.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"guide": str(OUT_GUIDE.relative_to(ROOT)), "trace": result["trace"], "contractSHA256": result["contractSHA256"]}, indent=2))


if __name__ == "__main__":
    main()
