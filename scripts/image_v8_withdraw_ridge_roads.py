"""Withdraw the failed ridge-road traces and record one Stone grid reading.

The Sobel correction marked vegetation and field edges. It is not a painted road.
Stone was read on the 100px legal grid. Uncertainty is 40 legal pixels.
No asset bytes are rewritten.
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / "qa" / "image-local-delivery-v8-20261005"
SCENES = QA / "scenes.json"
INTERFACE = ROOT / "docs" / "plan" / "IMAGE-DELIVERY-INTERFACE-V8-2026-10-05.json"
SCALE = 4.0
AFFINE = [60, -10, 25, 35, 170, 165]

RING = [(500, 300), (680, 290), (780, 360), (820, 480), (780, 580), (620, 640), (420, 650), (300, 560), (340, 430), (420, 330), (500, 300)]
RADIAL = [(700, 340), (900, 380), (1100, 420)]
NORTH = [(560, 120), (580, 220), (620, 300)]
RIVER = [(1080, 20), (1120, 150), (1160, 300), (1200, 420), (1240, 560), (1280, 720)]
WEST = [(1000, 10), (1040, 160), (1100, 320), (1120, 430), (1080, 560), (1120, 740)]
EAST = [(1240, 10), (1280, 180), (1320, 320), (1370, 450), (1340, 620), (1360, 750)]
DECK = [(1100, 400), (1376, 415), (1376, 470), (1110, 455)]
APPROACH = [(1000, 390), (1100, 420)]
NOTE = "Read from the 100px legal grid on kingdom-terrain-stone. Uncertainty is about 40 legal pixels. Not a subpixel survey."


def native(points):
    return [[round(x * SCALE, 2), round(y * SCALE, 2)] for x, y in points]


def inverse_world(x, y):
    a, b, c, d, e, f = AFFINE
    det = a * d - c * b
    x, y = x - e, y - f
    return [round((d * x - c * y) / det, 3), round((-b * x + a * y) / det, 3)]


def main() -> None:
    scenes = json.loads(SCENES.read_text(encoding="utf-8"))
    for row in scenes:
        row["rejectedRidgePolylines"] = row.get("paintedRoadPolylines") or []
        row["rejectedRidgeReason"] = (
            "Sobel 93rd-percentile ridges were checked on kingdom-terrain-stone, "
            "kingdom-terrain-medieval and adventure-terrain. They followed vegetation, rocks and field edges."
        )
        row["paintedRoadPolylines"] = []
        row["paintedRoadState"] = "UNRESOLVABLE_RIDGE_METHOD_FAILED_VISUAL_CHECK"
        if row.get("residual", {}).get("state") == "MEASURED_AGAINST_TRACK_MASK":
            row["residual"] = {
                "state": "NOT_A_PAINTED_ROAD_DISTANCE",
                "rejectedRidgeDistance": row["residual"].get("legalRoadToTrackMask"),
                "note": "The number is distance to the rejected ridge mask.",
            }
        row["proposal"] = None
        if row.get("paintedBridgeState") == "DECK_CANDIDATE_ONLY":
            row["paintedBridgeState"] = "BROWN_BAND_CANDIDATE_NOT_CONFIRMED_AS_DECK"
        if row["id"] == "kingdom-terrain-stone":
            roads = [
                {"polylineNative": native(RING), "uncertainty": NOTE, "kind": "ring"},
                {"polylineNative": native(RADIAL), "uncertainty": NOTE, "kind": "radial-to-bridge"},
                {"polylineNative": native(NORTH), "uncertainty": NOTE, "kind": "north-track"},
            ]
            row["paintedRoadPolylines"] = roads
            row["paintedRoadState"] = "MANUAL_GRID_READING"
            row["paintedRiverPolylines"] = [{
                "polylineNative": native(RIVER),
                "uncertainty": NOTE + " The automatic filter dropped this channel because it touches the top edge.",
                "method": "manual-grid",
            }]
            row["paintedRiverState"] = "MANUAL_GRID_READING"
            row["paintedBankPolylines"] = [
                {"side": "west-bank-observed", "observedBankSide": "west", "polylineNative": native(WEST), "uncertainty": NOTE},
                {"side": "east-bank-observed", "observedBankSide": "east", "polylineNative": native(EAST), "uncertainty": NOTE},
            ]
            row["paintedBankState"] = "MANUAL_GRID_READING"
            row["paintedBridgeDeckPolygons"] = [{"kind": "wooden-deck", "polygonNative": native(DECK), "uncertainty": NOTE + " The deck continues to the right frame edge."}]
            row["paintedBridgeApproachPolygons"] = [{"polylineNative": native(APPROACH), "uncertainty": NOTE}]
            row["paintedBridgeApproachState"] = "MANUAL_GRID_READING"
            row["paintedBridgeState"] = "MANUAL_GRID_READING"
            row["staticObstacleState"] = "ROCK_RING_VISIBLE_NOT_POLYGONIZED"
            # Residual of the legal centerline against the manual tracks.
            import cv2
            mask = np.zeros((768, 1376), np.uint8)
            for line in (RING, RADIAL, NORTH):
                for a, b in zip(line, line[1:]):
                    cv2.line(mask, a, b, 1, 3)
            dt = cv2.distanceTransform((mask == 0).astype(np.uint8), cv2.DIST_L2, 3)
            legal = np.zeros_like(mask)
            for road in row.get("legalRoads", []):
                pts = [(int(round(p[0] / SCALE)), int(round(p[1] / SCALE))) for p in road["polylineNative"]]
                for a, b in zip(pts, pts[1:]):
                    cv2.line(legal, a, b, 1, 1)
            samples = dt[legal > 0]
            mean = round(float(samples.mean()), 2) if samples.size else None
            row["residual"] = {
                "state": "LEGAL_CENTERLINE_TO_MANUAL_TRACK",
                "legalRoadToPaintedTrack": {
                    "unit": "legal source pixels",
                    "mean": mean,
                    "p95": round(float(np.percentile(samples, 95)), 2) if samples.size else None,
                    "max": round(float(samples.max()), 2) if samples.size else None,
                    "uncertainty": "Manual tracks are about 40 legal pixels coarse, and the distance uses a 3px stroke.",
                },
            }
            world = []
            for line in (RING, RADIAL, NORTH):
                world.append([inverse_world(x, y) for x, y in line])
            deck_world = [inverse_world(x, y) for x, y in DECK]
            four = QA / "terrain" / "kingdom-terrain-stone-four-viewport.png"
            row["proposal"] = {
                "id": "proposal-v8-kingdom-terrain-stone-manual-tracks",
                "status": "PROPOSED",
                "proposedCamera": None,
                "activeAffine": AFFINE,
                "activeHallScale": 0.1312,
                "activated": False,
                "proposedRoadWorld": world,
                "proposedBridgeWorld": deck_world,
                "affectedIds": ["kingdom-terrain-stone"],
                "routeImplication": "Picking and movement still use the active contract. These world points are the inverse of the coarse painted tracks.",
                "reason": "On Stone the legal centerline crosses the rock ring and the legal bridge rectangle is not the wooden deck.",
                "fourViewport": "qa/image-local-delivery-v8-20261005/terrain/kingdom-terrain-stone-four-viewport.png",
                "legalRoadMeanDistance": mean,
            }
            # Redraw overlay from the source preview.
            src = Image.open(ROOT / row["source"]["path"]).convert("RGB")
            preview = src.resize((640, int(640 * src.size[1] / src.size[0])), Image.Resampling.BOX)
            draw = ImageDraw.Draw(preview)
            sx, sy = preview.size[0] / src.size[0], preview.size[1] / src.size[1]
            def poly(pts, fill, width=3):
                flat = [(p[0] * sx, p[1] * sy) for p in pts]
                if len(flat) >= 2:
                    draw.line(flat, fill=fill, width=width)
            for road in row.get("legalRoads", []):
                poly(road["polylineNative"], (230, 200, 40), 2)
            for bridge in row.get("legalBridges", []):
                draw.polygon([(p[0] * sx, p[1] * sy) for p in bridge["polygonNative"]], outline=(220, 90, 40))
            for road in roads:
                poly(road["polylineNative"], (220, 40, 180), 3)
            poly(native(RIVER), (40, 90, 220), 3)
            poly(native(WEST), (40, 180, 90), 2)
            poly(native(EAST), (40, 180, 90), 2)
            draw.polygon([(p[0] * sx, p[1] * sy) for p in native(DECK)], outline=(255, 255, 255))
            overlay = QA / "terrain" / "kingdom-terrain-stone-painted-and-legal.png"
            preview.save(overlay)
            sheet = Image.new("RGB", (1280, 860), (20, 20, 20))
            sd = ImageDraw.Draw(sheet)
            for i, (vw, vh) in enumerate(((825, 375), (933, 424), (1180, 820), (1280, 720))):
                panel = preview.resize((vw // 2, vh // 2), Image.Resampling.BOX)
                sheet.paste(panel, ((i % 2) * 640, (i // 2) * 400 + 24))
                sd.text(((i % 2) * 640 + 4, (i // 2) * 400 + 4), f"{vw}x{vh} yellow legal, magenta manual track", fill=(240, 240, 240))
            sheet.save(four)
            row["overlay"] = "qa/image-local-delivery-v8-20261005/terrain/kingdom-terrain-stone-painted-and-legal.png"

    SCENES.write_text(json.dumps(scenes, indent=2), encoding="utf-8")
    interface = json.loads(INTERFACE.read_text(encoding="utf-8"))
    keys = (
        "id", "mode", "age", "biome", "status", "promoted", "source", "coordinateFrames",
        "paintedRoadState", "paintedRoadMethod", "paintedRoadPolylines", "rejectedRidgeReason",
        "paintedRiverState", "paintedRiverPolylines", "paintedBankState", "paintedBankPolylines",
        "paintedBridgeState", "paintedBridgeDeckPolygons", "paintedBridgeApproachState",
        "paintedBridgeApproachPolygons", "walkableState", "walkablePolygons", "blockedState",
        "staticObstacleState", "mutableContent", "residual", "legalBridgeVsDeckIou", "proposal",
        "overlay", "proposedCamera", "runtimeAcceptance", "ownerAcceptance", "limitations",
        "stoneInspection", "legalAffineActive", "hallScaleActive",
    )
    interface["scenes"] = [{k: s[k] for k in keys if k in s} for s in scenes]
    interface["proposalsWithdrawn"] = (
        "Eleven ridge-based proposals were removed after the Stone, Medieval and Adventure visual check. "
        "Only the Stone manual-track proposal remains, and it is PROPOSED."
    )
    interface["codeAIHandoffReady"] = False
    INTERFACE.write_text(json.dumps(interface, indent=2), encoding="utf-8")
    checkpoint = json.loads((QA / "checkpoint.json").read_text(encoding="utf-8"))
    for item in checkpoint["items"]:
        if item["id"] == "kingdom-terrain-stone":
            item["method"] = "manual 100px legal-grid reading after ridge failure"
            item["attempts"] = 2
            item["exhausted"] = False
            item["remainingGap"] = "Coarse tracks only. Rocks are not polygonized. Full-body terrain is not promoted."
            item["nextExecutableAction"] = "Code may review the PROPOSED world tracks. Do not activate the affine."
        elif item["state"] == "partial" and item["id"].endswith("terrain") or (
            isinstance(item["id"], str) and "terrain" in item["id"] and item["id"] != "kingdom-terrain-stone"
        ):
            if "terrain" in item["id"] and item["id"] != "kingdom-terrain-stone":
                item["method"] = "ridge roads rejected after the Stone visual check; river color-axis kept where present"
                item["remainingGap"] = "Painted roads were not traced. Empty road arrays mean unresolved, not absent."
                item["exhausted"] = True
                item["nextExecutableAction"] = "A different road method is required. Do not sweep the Sobel percentile."
    checkpoint["counts"]["proposals"] = 1
    checkpoint["ridgeRoadsWithdrawn"] = True
    (QA / "checkpoint.json").write_text(json.dumps(checkpoint, indent=2), encoding="utf-8")
    stone = next(s for s in scenes if s["id"] == "kingdom-terrain-stone")
    print(json.dumps({"stoneResidual": stone["residual"], "proposal": stone["proposal"]["id"], "roadsKept": sum(1 for s in scenes if s["paintedRoadPolylines"])}, indent=2))


if __name__ == "__main__":
    main()
