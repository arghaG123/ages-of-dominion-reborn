"""One evidence-directed correction for the eight rejected kingdom candidates."""
from __future__ import annotations

import base64
import hashlib
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import coordinator as coord
import dispatch_kingdom as dispatch

ROOT = Path(r"C:\dev\ages-of-dominion-reborn")
QA = ROOT / "qa" / "image-vertex-repair-20261009" / "environment"
SHARED = ROOT / "docs" / "plan" / "image-production"
ORDER = dispatch.ORDER
BASELINE_NOW = 71.1156
HARD = 80.0
HOLD = 0.90


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(payload, indent=2).encode("utf-8")
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_bytes(data)
    os.replace(tmp, path)


def build(scene_id: str) -> dict:
    v1 = json.loads((QA / "regeneration" / "packs" / f"env-{scene_id}-v1.json").read_text(encoding="utf-8"))
    review = {
        "id": scene_id,
        "attempt": "a1",
        "imageStatus": "FAIL",
        "nativeDimensions": {"width": 5504, "height": 3072},
        "defects": [
            "Camera and pad placement do not match the frozen legal guide.",
            "The hall terrace was painted as a platform or building.",
            "Roads, walls, or props still enter reserved pads.",
            "Iron additionally painted the guide strokes as visible white lines.",
        ],
        "reviewedAt": now(),
    }
    write_json(QA / "review" / f"{scene_id}-candidate-a-review.json", review)
    clearance = json.loads((QA / "geography" / f"{scene_id}-clearance.json").read_text(encoding="utf-8"))
    guide = Image.new("RGB", (1376, 768), (40, 40, 40))
    draw = ImageDraw.Draw(guide)
    scene = json.loads((QA / "scenes.json").read_text(encoding="utf-8"))
    scene_row = next(row for row in scene if row["id"] == scene_id)
    for pad in scene_row["fullFootprints"]:
        polygon = [(pt[0], pt[1]) for pt in pad["polygon"]]
        color = (220, 180, 60) if pad["id"] == "townhall" else (80, 200, 90)
        draw.line(polygon + [polygon[0]], fill=color, width=2)
    for road in scene_row["roads"]:
        points = [(pt[0], pt[1]) for pt in road["polyline"]]
        if len(points) >= 2:
            draw.line(points, fill=(20, 20, 20), width=2)
    guide_path = QA / "geography" / "guides" / f"{scene_id}-legal-guide-v2.png"
    guide.save(guide_path)
    prompt = (
        "ONE natural landscape, native 4K, 16:9, one image only. "
        "The first image is a dark wireframe diagram and must not appear in the result. "
        "Do not paint rectangles, colored outlines, white lines, gray diagram fill, text, numbers, or a legend. "
        "Replace the whole diagram with a semi-realistic strategy-game valley in warm upper-left daylight. "
        "Every outlined rectangle becomes bare flat ground of the requested age, empty of buildings, walls, crates, rails, pipes, people, and animals. "
        "The gold outline is an empty dirt terrace, not a building. "
        "Keep the river on the right and one bridge only. Roads are dirt tracks that stay outside the former rectangles. "
        f"Age materials: {scene_id}. No HUD and no device frame. "
        f"The previous candidate failed because it redrew the diagram and moved the sites. This correction keeps the site positions and removes the diagram."
    )
    prompt_path = QA / "regeneration" / "prompts" / f"{scene_id}-v2.txt"
    prompt_path.write_text(prompt, encoding="utf-8")
    ref = QA / "regeneration" / "refs" / f"{scene_id}-appearance.jpg"
    parts = [{"text": prompt}]
    for image_path, mime in ((guide_path, "image/png"), (ref, "image/jpeg")):
        parts.append({
            "inlineData": {
                "mimeType": mime,
                "data": base64.b64encode(image_path.read_bytes()).decode("ascii"),
            }
        })
    body = {
        "contents": [{"role": "user", "parts": parts}],
        "generationConfig": {
            "candidateCount": 1,
            "maxOutputTokens": 2048,
            "responseModalities": ["IMAGE"],
            "imageConfig": {"aspectRatio": "16:9", "imageSize": "4K"},
        },
    }
    wire = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    wire_path = QA / "regeneration" / "wire" / f"{scene_id}-v2.json"
    wire_path.write_bytes(wire)
    pack = dict(v1)
    pack.update({
        "id": f"env-{scene_id}-v2",
        "version": "v2",
        "state": "READY",
        "defect": "Candidate A redrew the guide and did not keep frozen pad positions. Conflict count remains " + str(clearance.get("conflictCount")),
        "reason": "One directed correction. The wireframe must not be copied, and reserved rectangles stay empty natural ground.",
        "guide": {
            "path": str(guide_path.relative_to(ROOT)).replace("\\", "/"),
            "sha256": hashlib.sha256(guide_path.read_bytes()).hexdigest(),
            "bytes": guide_path.stat().st_size,
            "dimensions": {"width": 1376, "height": 768},
        },
        "promptPath": str(prompt_path.relative_to(ROOT)).replace("\\", "/"),
        "promptSHA256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        "wireBodyPath": str(wire_path.relative_to(ROOT)).replace("\\", "/"),
        "wireBodySHA256": hashlib.sha256(wire).hexdigest(),
        "priorAttempt": f"env-{scene_id}-v1-a1",
        "blockedBy": [],
    })
    write_json(QA / "regeneration" / "packs" / f"{pack['id']}.json", pack)
    return pack


def main() -> None:
    packs = [build(scene_id) for scene_id in ORDER]
    entries = []
    for pack in packs:
        path = QA / "regeneration" / "packs" / f"{pack['id']}.json"
        entries.append({"id": pack["id"], "path": str(path.relative_to(ROOT)).replace("\\", "/"), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    write_json(QA / "regeneration" / "ready-index.json", {
        "schema": 1,
        "owner": "ENVIRONMENT",
        "version": "2026-10-09-v2",
        "publishedAt": now(),
        "complete": True,
        "preparationComplete": True,
        "pendingPackIds": [],
        "packs": entries,
    })
    access = dispatch.token()
    evidence = dispatch.probe(access)
    write_json(QA / "vertex-coordinator" / "evidence" / "access-correction.json", evidence)
    if evidence["blocked"]:
        print(json.dumps({"correctionsSubmitted": 0, "blocked": evidence["blocked"]}))
        return
    runner = coord.Coordinator(
        QA / "vertex-coordinator",
        owner_id=f"environment-vertex-correction-pid{os.getpid()}",
        committed_protected_usd=BASELINE_NOW,
        hard_cap_usd=HARD,
        cloud_lock_enabled=True,
        mutex_file=SHARED / "submission.mutex.json",
        pacing_file=SHARED / "pacing_state.json",
        token_provider=dispatch.token,
    )
    receipts = []
    stopped = None
    released = False
    try:
        runner.acquire_mutex()
        for pack in packs:
            scene_id = pack["canonicalId"]
            reservation = float(pack["estimatedUpperBoundUSD"])
            if runner.exposure_usd() + reservation > HARD - HOLD:
                stopped = f"Correction hold reached before {scene_id}"
                break
            wire = (ROOT / pack["wireBodyPath"]).read_bytes()
            attempt_id = f"{pack['id']}-a1"
            meta = {
                "id": scene_id,
                "attemptId": attempt_id,
                "owner": "ENVIRONMENT",
                "prompt": (ROOT / pack["promptPath"]).read_text(encoding="utf-8"),
                "wireBodySHA256": pack["wireBodySHA256"],
                "inlineCount": 2,
            }
            attempt_dir = QA / "vertex-coordinator" / "attempts" / attempt_id
            result = runner.execute_prepared(attempt_dir, wire, meta, reservation)
            info = {"status": result["status"]}
            response_path = attempt_dir / "response.json"
            if result["status"] == "SUCCEEDED_CANDIDATE":
                info = dispatch.extract_image(
                    response_path.read_bytes(),
                    ROOT / "assets/derivatives/image-vertex-repair-20261009/environment/native" / f"{scene_id}-candidate-b.png",
                )
            receipt = dispatch.publish_receipt(scene_id, attempt_id, pack, result, info, response_path)
            dispatch.append_ledger({
                "attemptId": attempt_id,
                "scene": scene_id,
                "reservedUSD": reservation,
                "retained": True,
                "status": receipt["status"],
                "at": now(),
            })
            receipts.append({"id": scene_id, "status": receipt["status"], "dimensions": info.get("dimensions")})
            print(json.dumps(receipts[-1]), flush=True)
    except Exception as exc:
        stopped = f"{type(exc).__name__}: {exc}"
    finally:
        if runner.has_lock:
            released = runner.release_mutex("RELEASED" if not runner.blocked else "UNKNOWN")
    print(json.dumps({
        "correctionsSubmitted": len(receipts),
        "stopped": stopped,
        "exposure": runner.exposure_usd(),
        "released": released,
    }))


if __name__ == "__main__":
    main()
