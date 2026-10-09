"""Publish the actor successor interface, packs, gallery, and checkpoint. No provider calls."""
from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(r"C:\dev\ages-of-dominion-reborn")
QA = ROOT / "qa/image-vertex-repair-20261009/actors"
DERIV = ROOT / "assets/derivatives/image-vertex-repair-20261009/actors"
RESIDUAL = ROOT / "docs/plan/ACTORS-EQUIPMENT-RESIDUAL-INTERFACE-2026-10-07.json"
UPPER = 0.40
SPENDABLE = 8.8844
COMMITTED = 71.1156

CODE_REUSE = {
    "troop-stone-melee": {
        "output": "assets/runtime-code-20261007/troops/troop-stone-melee.png",
        "sha": "c61f0e3dec06a344744f3f4d21a6cf7dabdb4df61730c42eac535c7988f2104a",
        "wh": (1369, 1852),
        "affine": [1, 0, 0, 1, -477, -112],
        "source": "assets/high-res/final-native2k/troop-stone-melee.png",
        "source_sha": "9d6d0afb631ca748a31de2f8f33c77f8236a138954fe2d9cf79d607c7911b488",
        "cap": 130,
    },
    "troop-industrial-ranged": {
        "output": "assets/runtime-code-20261007/troops/troop-industrial-ranged.png",
        "sha": "5df473c9336451f51f2babf21ed88b7c5dc8bd5bc901615b8851a07c5183823f",
        "wh": (1247, 1851),
        "affine": [1, 0, 0, 1, -526, -103],
        "source": "assets/high-res/final-native2k/troop-industrial-ranged.png",
        "source_sha": "6e72795f5e73feda122521d85c6ae23a10350ed839e07a852a6d24460600a37c",
        "cap": 130,
    },
    "troop-industrial-heavy": {
        "output": "assets/runtime-code-20261007/troops/troop-industrial-heavy.png",
        "sha": "9455bf02f32921c7fa0bf3d2bce4f561e9c311a37e36ad99bd3dbafa7fcbc758",
        "wh": (1640, 1921),
        "affine": [1, 0, 0, 1, -233, -64],
        "source": "assets/high-res/final-native2k/troop-industrial-heavy.png",
        "source_sha": "4662db518ad44d0dd24507bbd36d064b4cbc825aea455843e724750f3d4ec5e2",
        "cap": 130,
    },
}

REJECT_BACKDROP = {
    "troop-future-heavy",
    "troop-medieval-melee",
    "troop-gunpowder-heavy",
    "hero-mount-motor-transport",
}

ACCEPT_BACKDROP = {
    "troop-bronze-heavy",
    "troop-medieval-heavy",
    "hero-mount-horse",
}

CAP64_EXTRA = {
    "troop-bronze-heavy",
    "troop-gunpowder-heavy",
    "troop-future-ranged",
    "troop-future-heavy",
    "hero-mount-horse",
    "hero-mount-motor-transport",
    "hero-mount-future-transport",
    "knight-mounted-master",
}

PACKS = [
    ("class-knight-standing-body", "Knight standing body", "A single adult Knight in plate, standing, both feet visible, sword lowered, full body inside the frame."),
    ("class-ranger-standing-body", "Ranger standing body", "A single adult Ranger in leather and a cloak, standing, bow lowered, both feet visible, full body inside the frame."),
    ("class-warlock-standing-body", "Warlock standing body", "A single adult Warlock in dark robes, standing, both feet visible, full body inside the frame."),
    ("class-mage-standing-body", "Mage standing body", "A single adult Mage in robes with a staff lowered, standing, both feet visible, full body inside the frame."),
    ("class-paladin-standing-body", "Paladin standing body", "A single adult Paladin in bright plate, standing, both feet visible, full body inside the frame."),
    ("class-barbarian-standing-body", "Barbarian standing body", "A single adult Barbarian in hide and fur, standing, axe lowered, both feet visible, full body inside the frame."),
    ("class-necromancer-standing-body", "Necromancer standing body", "A single adult Necromancer in bone-trimmed robes, standing, both feet visible, full body inside the frame."),
    ("class-healer-standing-body", "Healer standing body", "A single adult Healer in a pale robe and skirt, standing, both feet visible, full body inside the frame."),
    ("troop-iron-melee", "Iron Age swordsman", "A single Iron Age swordsman in colored metal armor with an intact oval shield and sword. Not a gray silhouette. Full body, both feet visible."),
    ("attacker-bronze-runner", "Bronze Age runner", "A single Bronze Age runner with a round shield and short blade, running pose, full body. No castle, no road, no HUD, no buttons, no text."),
    ("attacker-medieval-archer", "Medieval archer", "A single medieval archer drawing a bow, full body, intact gambeson and limbs. Not a pose sheet and not a figure with holes cut through the torso."),
    ("troop-future-ranged", "Future sniper", "A single future-armored sniper standing and aiming, full body. No extra poses, no labels, no inset portrait."),
    ("troop-gunpowder-heavy", "Gunpowder cannon crew", "One gunpowder cannon with its crew and limber as a single unit. No diagram labels, no callout arrows, no second cannon."),
    ("troop-future-heavy", "Future hover tank", "A single future hover tank, isolated, no hangar and no extra vehicles."),
    ("troop-medieval-melee", "Medieval melee soldier", "A single medieval melee soldier with sword and shield, standing, both feet visible, isolated."),
    ("paladin-head-raster", "Paladin head card", "A three-quarter paladin helmeted head and neck on a plain background. No leader lines and no text."),
    ("hero-mount-future-transport", "Future hero transport", "A single future riding machine, isolated, no studio backdrop and no rider unless the machine requires a seated figure."),
    ("hero-mount-motor-transport", "Motor transport", "A single early motor transport vehicle, isolated, no studio floor and no scenery."),
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def file_ref(path: Path) -> dict:
    with Image.open(path) as im:
        w, h = im.size
    return {"path": rel(path), "sha256": sha256_file(path), "bytes": path.stat().st_size, "dimensions": {"width": w, "height": h}}


def contact_and_box(path: Path) -> tuple[list | None, list | None]:
    arr = np.array(Image.open(path).convert("RGBA"))
    a = arr[:, :, 3] > 32
    ys, xs = np.where(a)
    if len(xs) == 0:
        return None, None
    x0, x1, y0, y1 = int(xs.min()), int(xs.max()) + 1, int(ys.min()), int(ys.max()) + 1
    yb = int(ys.max())
    band = a[max(0, yb - 2): yb + 1]
    cols = np.where(band.any(axis=0))[0]
    contact = [[float(cols.min()), float(yb)], [float(cols.max()), float(yb)]] if len(cols) else None
    return contact, [x0, y0, x1, y1]


def cap_for(row_id: str, role: str) -> int | None:
    if role in ("gear-icon", "artifact-icon", "fx-sprite", "mount"):
        return 64
    if row_id in CAP64_EXTRA:
        return 64
    if role in ("attacker", "creature", "static-troop", "static-head-card"):
        return 130
    return None


def visible(width: int, height: int, cap: int) -> dict:
    longest = max(width, height)
    fitted = cap / longest if longest > cap else 1
    css_w = width * fitted
    css_h = height * fitted
    viewports = {}
    for vw, vh in ((1280, 720), (1180, 820), (933, 424), (825, 375)):
        safe = [int(vw * 0.08), int(vh * 0.08), int(vw * 0.92), int(vh * 0.92)]
        viewports[f"{vw}x{vh}"] = {
            "cssWidth": round(css_w, 2),
            "cssHeight": round(css_h, 2),
            "safeArea": safe,
            "fitsSafeArea": css_w <= (safe[2] - safe[0]) and css_h <= (safe[3] - safe[1]),
            "camera": {"uniformScale": 1, "offset": [0, 0]},
        }
    return {"capCss": cap, "limitBasis": "CONSERVATIVE_BOTH", "longest": round(max(css_w, css_h), 2), "viewports": viewports}


def use_of(role: str, kind: str) -> str:
    if kind == "reference":
        return "REFERENCE_ONLY"
    if kind == "joint":
        return "JOINT_METADATA"
    if kind == "card":
        return "STATIC_CARD"
    if kind == "atlas":
        return "ATLAS_FRAME"
    if role in ("gear-icon", "artifact-icon"):
        return "MATERIAL"
    return "SPRITE"


def draw_guide(path: Path, title: str) -> None:
    im = Image.new("RGB", (768, 1024), (18, 22, 28))
    d = ImageDraw.Draw(im)
    d.text((24, 24), title[:42], fill=(240, 220, 160))
    d.text((24, 56), "FRONT STANDING GUIDE. Not a gameplay sprite.", fill=(180, 190, 200))
    cx = 384
    joints = {
        "head": (cx, 180),
        "shoulders": (cx, 280),
        "hips": (cx, 520),
        "kneeL": (cx - 70, 700),
        "kneeR": (cx + 70, 700),
        "footL": (cx - 90, 900),
        "footR": (cx + 90, 900),
        "handL": (cx - 160, 460),
        "handR": (cx + 160, 460),
    }
    lines = [("head", "shoulders"), ("shoulders", "hips"), ("hips", "kneeL"), ("kneeL", "footL"), ("hips", "kneeR"), ("kneeR", "footR"), ("shoulders", "handL"), ("shoulders", "handR")]
    for a, b in lines:
        d.line([joints[a], joints[b]], fill=(220, 220, 210), width=6)
    for name, (x, y) in joints.items():
        d.ellipse((x - 10, y - 10, x + 10, y + 10), fill=(255, 180, 60))
        d.text((x + 14, y - 8), name, fill=(200, 210, 220))
    d.rectangle((cx - 80, 180, cx + 80, 280), outline=(120, 160, 200))
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path)


def write_pack(pack_id: str, title: str, need: str, priority: int) -> dict:
    folder = QA / "regeneration/packs" / pack_id
    folder.mkdir(parents=True, exist_ok=True)
    guide = folder / "guide.png"
    draw_guide(guide, title)
    prompt = (
        "Produce ONE native 2K image. " + need +
        " Isolated subject on a flat white or truly transparent background. "
        "No checkerboard, no magenta backdrop, no ground slab, no plinth, no caption, no HUD, no inset, no second copy. "
        "Full required subject inside the frame. Deliver ONE 2048x2048 image. "
        "The attached guide is a proportion diagram only. Do not draw the stick figure, labels, or diagram style."
    )
    (folder / "prompt.txt").write_text(prompt, encoding="utf-8")
    wire = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "candidateCount": 1,
            "imageConfig": {"aspectRatio": "1:1", "imageSize": "2K"},
            "maxOutputTokens": 2048,
            "responseModalities": ["IMAGE"],
        },
    }
    wire_bytes = json.dumps(wire, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    (folder / "wire_body.json").write_bytes(wire_bytes)
    landmarks = {
        "view": "front",
        "normalized": {
            "head": [0.5, 0.18],
            "shoulders": [0.5, 0.27],
            "hips": [0.5, 0.51],
            "footL": [0.38, 0.88],
            "footR": [0.62, 0.88],
        },
        "note": "Normalized to the guide image. Not measured on a real body.",
    }
    (folder / "landmarks.json").write_text(json.dumps(landmarks, indent=2), encoding="utf-8")
    guide_ref = file_ref(guide)
    pack = {
        "schema": 1,
        "id": pack_id,
        "owner": "ACTORS",
        "canonicalId": pack_id,
        "version": "2026-10-09.1",
        "state": "READY",
        "defect": need,
        "reason": "Existing source has no compatible full subject, or a bounded local matte split or left the required subject unusable.",
        "priorSourceHashes": [],
        "referenceRefs": [guide_ref],
        "base": None,
        "mask": None,
        "guide": guide_ref,
        "landmarks": landmarks,
        "legalGeometrySHA256": None,
        "requestedResolution": "2K",
        "aspectRatio": "1:1",
        "expectedNativeDimensions": {"width": 2048, "height": 2048},
        "project": "project-eaa4c1cc-8f19-4d24-9e6",
        "model": "gemini-3.1-flash-image",
        "promptPath": rel(folder / "prompt.txt"),
        "promptSHA256": sha256_file(folder / "prompt.txt"),
        "wireBodyPath": rel(folder / "wire_body.json"),
        "wireBodySHA256": hashlib.sha256(wire_bytes).hexdigest(),
        "inputTransforms": [{"order": ["prompt text", "guide.png"], "note": "Coordinator attaches guide.png as an image part. Do not invent a mask API field. candidateCount stays 1."}],
        "semanticCriteria": [need, "one subject", "no text", "no checker", "no HUD"],
        "geometryCriteria": [{"fullSubjectInsideFrame": True, "nativeDecoded": "2048x2048", "noUpscaleClaim": True}],
        "maxCandidateCalls": 1,
        "estimatedUpperBoundUSD": UPPER,
        "upperBoundBasis": "Reservation ceiling for one 2K attempt covering about 0.101 output plus inputs, text, reasoning, and one unexpected extra image. Not an invoice.",
        "readinessEvidence": [rel(guide), rel(folder / "prompt.txt")],
        "blockedBy": [],
        "priority": priority,
        "maskApplicability": "No source mask: the request asks for a new complete subject, not an inpaint of a defective plate.",
    }
    (folder / "pack.json").write_text(json.dumps(pack, indent=2), encoding="utf-8")
    return pack


def composite(name: str, viewport: tuple[int, int], layers: list[tuple[Path, int]]) -> dict:
    vw, vh = viewport
    canvas = Image.new("RGBA", (vw, vh), (26, 28, 24, 255))
    safe = (int(vw * 0.08), int(vh * 0.08), int(vw * 0.92), int(vh * 0.92))
    slot_w = (safe[2] - safe[0]) // max(1, len(layers))
    contributors = []
    for i, (path, cap) in enumerate(layers):
        im = Image.open(path).convert("RGBA")
        longest = max(im.size)
        scale = cap / longest
        nw, nh = max(1, int(im.size[0] * scale)), max(1, int(im.size[1] * scale))
        sprite = im.resize((nw, nh), Image.Resampling.LANCZOS)
        x = safe[0] + i * slot_w + (slot_w - nw) // 2
        y = safe[3] - nh - 8
        canvas.alpha_composite(sprite, (x, y))
        a = np.array(sprite)[:, :, 3] > 16
        ys, xs = np.where(a)
        contributors.append({
            "path": rel(path),
            "cap": cap,
            "placedCss": [nw, nh],
            "alphaExtent": [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1] if len(xs) else None,
        })
    out = QA / "composites" / f"{name}-{vw}x{vh}.jpg"
    canvas.convert("RGB").save(out, quality=80)
    return {
        "id": f"{name}-{vw}x{vh}",
        "stateKind": "ASSET_COMPOSITE",
        "viewport": [vw, vh],
        "reference": None,
        "actual": file_ref(out),
        "camera": {"uniformScale": 1, "offset": [0, 0], "safeArea": list(safe)},
        "contributors": contributors,
        "visibleAlphaMeasurements": contributors,
        "differences": ["Neutral test ground. Not a mock screenshot and not gameplay."],
    }


def main() -> None:
    residual = json.loads(RESIDUAL.read_text(encoding="utf-8"))
    metrics = json.loads((QA / "diagnostics/process-metrics.json").read_text(encoding="utf-8"))
    rejected_dir = QA / "diagnostics/rejected"
    rejected_dir.mkdir(parents=True, exist_ok=True)
    for iid in REJECT_BACKDROP:
        for folder in ("troops", "mounts"):
            src = DERIV / folder / f"{iid}.png"
            if src.exists():
                shutil.move(str(src), str(rejected_dir / f"{iid}.png"))
                metrics.pop(iid, None)

    rows_out = []
    decisions = []
    size_report = {}
    for row in residual["rows"]:
        iid = row["id"]
        role = row["role"]
        old_out = (row.get("output") or {}).get("path") if isinstance(row.get("output"), dict) else None
        entry = metrics.get(iid)
        promoted = None
        if iid in CODE_REUSE:
            spec = CODE_REUSE[iid]
            out_path = ROOT / spec["output"]
            ref = file_ref(out_path)
            if ref["sha256"] != spec["sha"] or (ref["dimensions"]["width"], ref["dimensions"]["height"]) != spec["wh"]:
                raise SystemExit(f"code crop mismatch {iid}")
            contact, box = contact_and_box(out_path)
            cap = spec["cap"]
            vis = visible(ref["dimensions"]["width"], ref["dimensions"]["height"], cap)
            size_report[iid] = vis
            rows_out.append({
                "id": iid,
                "producer": "ACTORS",
                "role": role,
                "age": row.get("age"),
                "classId": row.get("classId"),
                "status": "READY",
                "source": {"path": spec["source"], "sha256": spec["source_sha"], "bytes": (ROOT / spec["source"]).stat().st_size, "dimensions": {"width": 2048, "height": 2048}, "roi": None},
                "output": ref,
                "reusedFrom": ref,
                "sourceToOutput": spec["affine"],
                "intendedUse": "SPRITE",
                "maxDisplayCssPx": cap,
                "limitBasis": "CONSERVATIVE_BOTH",
                "side": "UNKNOWN",
                "frame": "OUTPUT_CROP",
                "groundContact": contact,
                "footprint": contact,
                "entrance": None,
                "heightEnvelope": box,
                "sourceGeometry": None,
                "transforms": {"parts": [], "frames": []},
                "gates": {"binding": "PASS", "semantics": "PASS", "matte": "PASS", "spatial": "PASS", "articulation": "NOT_APPLICABLE", "runtime": "UNVERIFIED", "owner": "UNVERIFIED"},
                "recipePath": None,
                "evidencePaths": [spec["output"], spec["source"]],
                "limitations": ["REUSE_UNCHANGED Code crop. Ground contact is the alpha bottom, not a surveyed footprint. Not a gait."],
                "blockedBy": [],
                "nextAction": "Code binds this existing crop. Image did not rewrite it.",
            })
            decisions.append({"id": iid, "owner": "ACTORS", "canonicalRequirement": role, "kind": "REUSE", "defectEvidence": [], "localAttemptEvidence": [], "whyGenerationNecessary": None, "sourceRefs": [], "preserve": [spec["output"]], "requiredOutput": "existing code crop", "priority": 100, "nextAction": "none"})
            continue

        if iid in REJECT_BACKDROP or (entry and iid not in ACCEPT_BACKDROP and role == "static-troop" and iid.startswith("troop-") and "backdrop" in json.dumps(entry) and iid not in metrics):
            pass

        use_new = entry and entry.get("ref") and iid not in REJECT_BACKDROP
        if use_new and role == "static-troop" and iid not in ACCEPT_BACKDROP and iid != "troop-stone-ranged" and iid != "troop-medieval-ranged":
            use_new = False
        if iid == "troop-medieval-ranged":
            use_new = True
        if iid in ("attacker-medieval-archer",):
            use_new = False
        kind = "sprite"
        status = "READY"
        matte = "PASS"
        limitations = list(row.get("limitations") or [])
        next_action = None
        blocked = list(row.get("blockedBy") or [])
        output_ref = None
        reused = None
        affine = row.get("sourceToOutput")
        recipe = None
        frames = []

        if iid == "troop-stone-ranged" and entry and entry.get("ref"):
            output_ref = entry["ref"]
            if "dimensions" in output_ref and isinstance(output_ref["dimensions"], list):
                output_ref["dimensions"] = {"width": output_ref["dimensions"][0], "height": output_ref["dimensions"][1]}
            # refresh hash from disk
            output_ref = file_ref(ROOT / output_ref["path"])
            recipe_doc = json.loads((QA / "recipes/troop-stone-ranged.json").read_text(encoding="utf-8"))
            affine = recipe_doc and [1, 0, 0, 1, -recipe_doc["sourceRoi"][0], -recipe_doc["sourceRoi"][1]]
            status, matte = "READY", "PASS"
            kind = "sprite"
            limitations = [
                "Checker cleared from native 937949e3. Baseline flood plus one enclosed neutral-component correction.",
                "Sling, pouch, stone, hands, and both feet remain. Side UNKNOWN. Not a gait.",
            ]
            recipe = "qa/image-vertex-repair-20261009/actors/recipes/troop-stone-ranged.json"
            next_action = "Code can bind this crop in place of the checker-backed plate."
        elif iid == "troop-medieval-ranged":
            frames_doc = json.loads((QA / "recipes/troop-medieval-ranged-frames.json").read_text(encoding="utf-8"))
            frames = frames_doc["frames"]
            primary = frames[1]["output"]
            output_ref = primary
            affine = [1, 0, 0, 1, -frames[1]["roi"][0], -frames[1]["roi"][1]]
            status, matte, kind = "PARTIAL", "PASS", "atlas"
            limitations = ["Twelve opaque components extracted. Primary is frame 01, a standing candidate. Pose identity is not classified. Not a gait."]
            recipe = "qa/image-vertex-repair-20261009/actors/recipes/troop-medieval-ranged-frames.json"
            next_action = "Code may bind frame 01 as a static back-or-side archer and keep the other frames as an atlas."
        elif use_new and entry.get("ref"):
            output_ref = file_ref(ROOT / entry["ref"]["path"])
            recipe_path = QA / "recipes" / f"{iid}.json"
            stats = {}
            if recipe_path.exists():
                stats = json.loads(recipe_path.read_text(encoding="utf-8")).get("stats") or {}
                recipe = rel(recipe_path)
            comps = stats.get("components", 1)
            border = stats.get("border", 0)
            status = "READY"
            matte = "PASS"
            if comps > 40 or border > 0.04:
                status, matte = "PARTIAL", "PARTIAL"
            if iid in ("gear-stone-boots",):
                status, matte = "PARTIAL", "PARTIAL"
                limitations = ["Pink slab removed. A thin magenta line remains under the soles."]
            elif iid == "gear-stone-helm":
                status, matte = "READY", "PASS"
                limitations = ["Pink slab removed. Circlet opening is transparent. A few edge pixels may remain."]
            elif iid == "troop-bronze-heavy":
                status, matte, kind = "PARTIAL", "PARTIAL", "card"
                limitations = ["Gray backdrop removed. Caption removed. Baked earth patch remains. One charioteer crew, horses, and vehicle. 64 CSS cap."]
            elif iid == "troop-medieval-heavy":
                status, matte, kind = "PARTIAL", "PARTIAL", "sprite"
                limitations = ["White backdrop removed. Oval ground shadow remains. Mounted knight is one plate, not a rider rig."]
            elif iid == "hero-mount-horse":
                status, matte, kind = "PARTIAL", "PARTIAL", "card"
                limitations = ["Studio gray removed. Perspective ground plane remains. 64 CSS cap."]
            elif role in ("gear-icon", "artifact-icon"):
                limitations = ["Pink-slab predicate applied. High component counts mean interior openings are possible, so those rows stay PARTIAL."]
                if comps > 40:
                    limitations.append(f"Opaque components after the predicate: {comps}.")
            elif role in ("attacker", "creature"):
                limitations = ["Only magenta pixels touching transparency were cleared."]
            kind = "card" if kind == "card" else ("sprite" if role not in ("gear-icon", "artifact-icon") else "sprite")
        elif iid in ("effect-resurrect", "effect-curse", "effect-projectile", "effect-impact", "effect-haste", "effect-cure", "effect-shield"):
            if old_out:
                reused = file_ref(ROOT / old_out)
                output_ref = reused
            status, matte, kind = "PARTIAL", "PARTIAL", "atlas"
            recipe = f"qa/image-vertex-repair-20261009/actors/recipes/{iid}-frames.json"
            frames = json.loads((QA / "recipes" / f"{iid}-frames.json").read_text(encoding="utf-8")).get("frames", [])
            limitations = [f"Atlas ROIs recorded for {len(frames)} large components. The whole sheet is not one gameplay frame. Owner is ACTORS."]
            next_action = "Code sequences frames only after picking a semantic order. Image did not invent timing."
        else:
            if old_out and (ROOT / old_out).exists() and role not in ("joint-pair", "missing-link-diagram"):
                reused = file_ref(ROOT / old_out)
                output_ref = reused
            status = row["status"] if row["status"] in ("READY", "PARTIAL", "FAIL", "BLOCKED") else "PARTIAL"
            if role == "missing-link-diagram":
                kind = "reference"
                status = "PARTIAL"
                limitations = ["Diagram only. Not a body sprite."]
            elif role == "joint-pair":
                kind = "joint"
                if row["status"] == "FAIL":
                    status = "FAIL"
                    limitations = list(row.get("limitations") or [])
                    limitations.append("Exhausted or incompatible link preserved. No new search on the old parts.")
                else:
                    status = "PARTIAL"
                    limitations = ["Sampled angles only. Not a swept gait. Side stays as declared."]
            elif role == "subchain":
                kind = "joint"
                status = "PARTIAL"
                limitations = ["203x858 trim is not the 900x900 parent. Sampled -25/0/+25 only. Side UNKNOWN."]
            elif iid in ("attacker-bronze-runner", "attacker-medieval-archer", "troop-iron-melee", "troop-future-ranged", "troop-gunpowder-heavy", "troop-future-heavy", "troop-medieval-melee", "hero-mount-future-transport", "hero-mount-motor-transport", "knight-mounted-master", "paladin-head-raster"):
                kind = "card"
                status = "PARTIAL" if iid != "paladin-head-raster" else "FAIL"
                matte = "FAIL"
                deriv = DERIV / "attackers" / f"{iid}.png"
                if iid == "attacker-medieval-archer" and deriv.exists():
                    output_ref = file_ref(deriv)
                    reused = None
                    limitations = ["Fringe clear did not restore the holes through the archer. Regeneration pack is published."]
                else:
                    limitations = ["Local extraction did not produce a clean single subject. A regeneration pack is published."]
                next_action = "Wait for the matching ACTORS receipt, then process it in this namespace."
            else:
                kind = "sprite" if role not in ("static-head-card",) else "card"
                if status == "READY":
                    limitations = ["Reused existing derivative. Border was not a flat slab in the 9 October survey."]

        if output_ref and isinstance(output_ref.get("dimensions"), dict):
            contact, box = contact_and_box(ROOT / output_ref["path"])
        else:
            contact, box = None, None
        cap = cap_for(iid, role)
        if cap and output_ref:
            size_report[iid] = visible(output_ref["dimensions"]["width"], output_ref["dimensions"]["height"], cap)
        src = row.get("source") or {}
        source_ref = None
        if isinstance(src, dict) and src.get("path"):
            sp = ROOT / src["path"]
            source_ref = {
                "path": src["path"].replace("\\", "/"),
                "sha256": src.get("sha256") or (sha256_file(sp) if sp.exists() else ""),
                "bytes": sp.stat().st_size if sp.exists() else 0,
                "dimensions": {"width": 1, "height": 1},
                "roi": src.get("roi"),
            }
            if sp.exists():
                with Image.open(sp) as im:
                    source_ref["dimensions"] = {"width": im.size[0], "height": im.size[1]}
        if iid == "paladin-head-raster":
            status = "FAIL"
        rows_out.append({
            "id": iid,
            "producer": "ACTORS",
            "role": role,
            "age": row.get("age"),
            "classId": row.get("classId"),
            "status": status,
            "source": source_ref,
            "output": output_ref,
            "reusedFrom": reused,
            "sourceToOutput": affine if kind != "joint" else None,
            "intendedUse": use_of(role, kind),
            "maxDisplayCssPx": cap,
            "limitBasis": "CONSERVATIVE_BOTH",
            "side": row.get("side") or "UNKNOWN",
            "frame": "OUTPUT_CROP" if output_ref and not reused else "SOURCE_NATIVE",
            "groundContact": contact,
            "footprint": contact,
            "entrance": None,
            "heightEnvelope": box,
            "sourceGeometry": None,
            "transforms": {"parts": row.get("transforms", {}).get("parts", []) if isinstance(row.get("transforms"), dict) else [], "frames": frames},
            "gates": {
                "binding": "PASS" if (output_ref or kind in ("joint", "reference")) else "FAIL",
                "semantics": "FAIL" if status == "FAIL" else ("PARTIAL" if status != "READY" else "PASS"),
                "matte": matte if status != "FAIL" else "FAIL",
                "spatial": "PARTIAL" if status != "READY" else "PASS",
                "articulation": "NOT_APPLICABLE" if role not in ("joint-pair", "subchain", "missing-link-diagram") else ("FAIL" if status == "FAIL" else "PARTIAL"),
                "runtime": "UNVERIFIED",
                "owner": "UNVERIFIED",
            },
            "recipePath": recipe,
            "evidencePaths": [p for p in [output_ref["path"] if output_ref else None, recipe] if p],
            "limitations": limitations,
            "blockedBy": blocked,
            "nextAction": next_action,
        })
        if status == "READY" and role in ("gear-icon", "artifact-icon"):
            kind_decision = "LOCAL_REPAIR" if entry else "REUSE"
        elif iid in CODE_REUSE:
            kind_decision = "REUSE"
        else:
            kind_decision = "LOCAL_REPAIR" if entry else ("VERTEX_REPLACEMENT" if any(iid == p[0] or iid.replace("_", "-") == p[0] for p in PACKS) else "REUSE")
        decisions.append({
            "id": iid,
            "owner": "ACTORS",
            "canonicalRequirement": role,
            "kind": "VERTEX_REPLACEMENT" if any(p[0] == iid for p in PACKS) else ("LOCAL_REPAIR" if (entry or iid in ("troop-stone-ranged", "troop-medieval-ranged")) else ("CODE_BINDING_ONLY" if iid in CODE_REUSE else "REUSE")),
            "defectEvidence": limitations[:2],
            "localAttemptEvidence": [recipe] if recipe else [],
            "whyGenerationNecessary": limitations[0] if any(p[0] == iid for p in PACKS) else None,
            "sourceRefs": [source_ref] if source_ref else [],
            "preserve": [old_out] if old_out else [],
            "requiredOutput": kind,
            "priority": 10 if any(p[0] == iid for p in PACKS) else 50,
            "nextAction": next_action or "none",
        })

    pack_objs = []
    for i, (pid, title, need) in enumerate(PACKS, start=1):
        pack_objs.append(write_pack(pid, title, need, i))
    # index last
    index_packs = []
    for pack in pack_objs:
        p = QA / "regeneration/packs" / pack["id"] / "pack.json"
        index_packs.append({"id": pack["id"], "path": rel(p), "sha256": sha256_file(p)})
    ready_index = {
        "schema": 1,
        "owner": "ACTORS",
        "version": "2026-10-09.1",
        "publishedAt": datetime.now(timezone.utc).isoformat(),
        "complete": True,
        "preparationComplete": True,
        "pendingPackIds": [p["id"] for p in pack_objs],
        "estimatedUpperBoundUSD": round(UPPER * len(pack_objs), 4),
        "spendableUnderHardCapUSD": SPENDABLE,
        "packs": index_packs,
    }
    index_path = QA / "regeneration/ready-index.json"
    tmp = index_path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(ready_index, indent=2), encoding="utf-8")
    tmp.replace(index_path)

    # Composites
    slinger = DERIV / "troops/troop-stone-ranged.png"
    melee = ROOT / CODE_REUSE["troop-stone-melee"]["output"]
    heavy = DERIV / "troops/troop-medieval-heavy.png"
    helm = DERIV / "gear/gear-stone-helm.png"
    boots = DERIV / "gear/gear-stone-boots.png"
    weapon = DERIV / "gear/gear-stone-weapon.png"
    horse = DERIV / "mounts/hero-mount-horse.png"
    bronze = DERIV / "troops/troop-bronze-heavy.png"
    brute = DERIV / "attackers/attacker-stone-brute.png"
    composites = []
    families = {
        "army": [(slinger, 130), (melee, 130), (heavy, 130)],
        "hero-equipment": [(helm, 64), (weapon, 64), (boots, 64)],
        "adventure": [(horse, 64), (bronze, 64)],
        "tactical": [(brute, 130), (slinger, 130)],
    }
    for name, layers in families.items():
        layers = [(p, c) for p, c in layers if p.exists()]
        for vp in ((1280, 720), (1180, 820), (933, 424), (825, 375)):
            composites.append(composite(name, vp, layers))
    (QA / "composites/composites.json").write_text(json.dumps(composites, indent=2), encoding="utf-8")

    ready_ids = [r["id"] for r in rows_out if r["status"] == "READY"]
    partial_ids = [r["id"] for r in rows_out if r["status"] == "PARTIAL"]
    failed_ids = [r["id"] for r in rows_out if r["status"] == "FAIL"]
    ages = ["Stone", "Bronze", "Iron", "Medieval", "Gunpowder", "Industrial", "Modern", "Future"]
    classes = ["Knight", "Ranger", "Warlock", "Mage", "Paladin", "Barbarian", "Necromancer", "Healer"]
    coverage = [
        {"family": "ages", "members": ages, "outcome": "represented in troop, attacker, and gear rows"},
        {"family": "classes", "members": classes, "outcome": "static parts and diagrams reused; full standing bodies are regeneration packs, not claimed as rigs"},
        {"family": "troops", "count": 24, "outcome": "three Code crops reused; slinger repaired; other rows reused, cropped, or packed"},
        {"family": "attackers", "count": 40, "outcome": "edge fringe cleared where present; bronze runner and medieval archer packed"},
        {"family": "creatures", "count": 8, "outcome": "existing mattes reused or fringe-cleared; flyers are harpy, griffin, wyvern, drone"},
        {"family": "gear-slots", "slots": ["helm", "weapon", "offhand", "armor", "boots", "accessory"], "outcome": "48 age-slot icons surveyed; pink-slab rows reprocessed; qualities are multipliers, no four new rasters"},
        {"family": "qualities", "members": ["Crude", "Fine", "Master", "Relic"], "outcome": "NO_NEW_IMAGE. Multipliers 1, 1.8, 2.8, 4. Badges do not require new item rasters."},
        {"family": "artifacts", "count": 10, "outcome": "icons reprocessed or reused at 64 CSS"},
        {"family": "mounts", "outcome": "horse extracted with a remaining ground plane; motor and future transport packed; knight-mounted stays a static card"},
        {"family": "effects", "outcome": "ACTORS owns projectile and impact. Frame ROIs published. Timing is a Code dependency."},
    ]
    interface = {
        "schema": 2,
        "producer": "ACTORS",
        "version": "image-vertex-repair-actors-20261009",
        "authorityDate": "2026-10-09",
        "inputSnapshot": "qa/image-vertex-repair-20261009/actors/input_snapshot.json",
        "rows": rows_out,
        "coverage": coverage,
        "readySubset": ready_ids,
        "wholeDeliveryReady": False,
        "reviewGallery": "qa/image-vertex-repair-20261009/actors/review/index.html",
        "checkpoint": "qa/image-vertex-repair-20261009/actors/checkpoint.json",
        "codeDependencies": [
            {"path": "src/data/plate-overrides-20261007.json", "need": "Point troop-stone-ranged at the new crop after Code review. Keep the three reused crops."},
            {"path": "src/data/gear-icons-20261007.json", "need": "46 current gear bindings are not all six slots on every screen."},
            {"path": "src/client/visible-size.js", "need": "Keep conservative longest-side caps. 130 world units are not 130 CSS pixels."},
            {"path": "src/client/actor.js", "need": "Runtime integration is a later Code task. This delivery does not edit src."},
        ],
        "repairDecisions": decisions,
        "regenerationPacks": "qa/image-vertex-repair-20261009/actors/regeneration/ready-index.json",
        "generationReceipts": [],
        "paidCompletedIds": [],
        "paidPendingIds": [p["id"] for p in pack_objs],
        "retainedUnknownIds": [],
        "budgetSnapshot": {
            "totalCommittedProtectedUSD": COMMITTED,
            "protectedReserveUSD": 15,
            "hardCapUSD": 80,
            "marginUnderHardCapUSD": SPENDABLE,
            "packCount": len(pack_objs),
            "perAttemptUpperBoundUSD": UPPER,
            "reservedIfAllFirstAttemptsUSD": round(UPPER * len(pack_objs), 4),
            "headroomAfterFirstAttemptsUSD": round(SPENDABLE - UPPER * len(pack_objs), 4),
            "correctionShortfallIfEveryPackNeedsASecondAttemptUSD": round(max(0, UPPER * len(pack_objs) - (SPENDABLE - UPPER * len(pack_objs))), 4),
            "invoices": "UNKNOWN",
            "note": "Do not spend the 15 reserve. AI1 reserves each attempt before dispatch.",
        },
        "localProcessingComplete": True,
        "imageWorkComplete": False,
        "localCompletionReason": "Feasible local mattes, frame ROIs, reuse rows, and regeneration packs are published. Paid actor receipts are not present, so image work is not complete.",
    }
    iface_path = ROOT / "docs/plan/ACTORS-EQUIPMENT-VERTEX-REPAIR-INTERFACE-2026-10-09.json"
    iface_path.write_text(json.dumps(interface, indent=2), encoding="utf-8")

    (QA / "size-report.json").write_text(json.dumps(size_report, indent=2), encoding="utf-8")
    (QA / "queue.json").write_text(json.dumps({"decisions": decisions, "packs": [p["id"] for p in pack_objs]}, indent=2), encoding="utf-8")

    # Gallery
    parts = ["<!DOCTYPE html><html><head><meta charset='utf-8'><title>Actor repair 2026-10-09</title>",
             "<style>body{font-family:sans-serif;background:#111;color:#eee}img{max-height:180px;background:#0a0}figure{display:inline-block;margin:8px;width:200px}figcaption{font-size:12px}</style></head><body>",
             "<h1>ACTORS vertex-repair review</h1><p>ASSET_COMPOSITE and crops. Not gameplay. Not owner acceptance.</p>"]
    for c in composites:
        if c["viewport"] == [1280, 720]:
            parts.append(f"<h2>{c['id']}</h2><img src='../../../{c['actual']['path']}' style='max-height:240px;background:#222'>")
    parts.append("<h2>Rows</h2>")
    for r in rows_out:
        src = r["output"]["path"] if r.get("output") else ""
        img = f"<img src='../../../{src}'>" if src else "<div>no image</div>"
        parts.append(f"<figure>{img}<figcaption>{r['id']} {r['status']} {r['intendedUse']}</figcaption></figure>")
    parts.append("</body></html>")
    (QA / "review/index.html").write_text("\n".join(parts), encoding="utf-8")

    checkpoint = {
        "status": "INCOMPLETE",
        "authorityDate": "2026-10-09",
        "completedIds": ready_ids,
        "partialIds": partial_ids,
        "failedIds": failed_ids,
        "blockedIds": [],
        "nextExecutableActions": {
            "ai1": "Read qa/image-vertex-repair-20261009/actors/regeneration/ready-index.json and dispatch affordable ACTORS packs through the single coordinator.",
            "ai2-after-receipt": "Copy verified native bytes into assets/derivatives/image-vertex-repair-20261009/actors/native and review them before any derivative.",
            "code": "Bind the slinger crop and keep the three Code crops. Do not treat this file as runtime integration.",
        },
        "sourceHashes": {"inputSnapshot": "qa/image-vertex-repair-20261009/actors/input_snapshot.json"},
        "evidencePaths": [
            "qa/image-vertex-repair-20261009/actors/review/index.html",
            "qa/image-vertex-repair-20261009/actors/diagnostics/troop-stone-ranged-green.jpg",
            "docs/plan/ACTORS-EQUIPMENT-VERTEX-REPAIR-INTERFACE-2026-10-09.json",
        ],
        "polishQueue": [],
        "authorityLimits": [
            "AI2 does not call Vertex and does not write the coordinator.",
            "Hard cap 80 and reserve 15 stay in force.",
            "Device, Git, runtime, and owner acceptance are separate.",
            "Knight 13-attempt search was not rerun. The missing correction PNG is still missing.",
        ],
        "localProcessingComplete": True,
        "imageWorkComplete": False,
        "localCompletionReason": interface["localCompletionReason"],
        "paidCompletedIds": [],
        "paidPendingIds": [p["id"] for p in pack_objs],
        "retainedUnknownIds": [],
        "budgetSnapshot": interface["budgetSnapshot"],
        "repairDecisions": decisions,
        "regenerationPacks": ready_index["packs"] and "qa/image-vertex-repair-20261009/actors/regeneration/ready-index.json",
        "generationReceipts": [],
    }
    (QA / "checkpoint.json").write_text(json.dumps(checkpoint, indent=2), encoding="utf-8")
    handoff = f"""# Actors and equipment handoff — 9 October 2026

Image AI 2 published local repairs and {len(pack_objs)} regeneration packs. No Vertex call was made from this producer. `localProcessingComplete` is true. `imageWorkComplete` is false. `wholeDeliveryReady` is false. Runtime, device, and owner gates stay open.

## Reuse

Code crops kept byte-for-byte:

- troop-stone-melee `{CODE_REUSE['troop-stone-melee']['sha']}` 1369x1852, translation [-477, -112]
- troop-industrial-ranged `{CODE_REUSE['troop-industrial-ranged']['sha']}` 1247x1851, translation [-526, -103]
- troop-industrial-heavy `{CODE_REUSE['troop-industrial-heavy']['sha']}` 1640x1921, translation [-233, -64]

## Local repairs

- Slinger crop `assets/derivatives/image-vertex-repair-20261009/actors/troops/troop-stone-ranged.png` from native `937949e300d24d0b53d5f735cbf03f2a985800b3ef9c110a373b76f100e583f5`. Checker flood plus one enclosed-component correction. Sling and pouch remain.
- Stone helm and stone boots pink slabs cleared. Boots still have a thin sole fringe and stay PARTIAL.
- Other gear and artifact icons with the same pink predicate are in the derivative gear folder. Rows with many opaque components stay PARTIAL.
- Bronze charioteer, medieval heavy cavalry, and the barded horse were separated from flat backdrops. Ground patches or the horse plane remain, so those rows stay PARTIAL. Display cap for the charioteer and the horse is 64 CSS pixels on the longest side.
- Medieval ranged pose sheet split into 12 component frames. Primary review frame is frame 01.
- Effect sheets have component ROIs under `qa/image-vertex-repair-20261009/actors/recipes/`. Projectile and impact belong to ACTORS.

## Not claimed

Full class bodies, iron melee color, bronze runner, medieval archer, future sniper and hover tank, gunpowder cannon crew, medieval melee soldier, paladin head, and two transports are packs for AI1. The Knight thigh search was not repeated. `qa/image-local-solution-20261004/joints/knight_thigh_greave_correction_0.png` is still absent.

Ready rows in this interface: {len(ready_ids)}. Partial: {len(partial_ids)}. Failed: {len(failed_ids)}.

First-attempt reservation for {len(pack_objs)} packs at {UPPER} USD is {round(UPPER * len(pack_objs), 4)} USD against {SPENDABLE} USD headroom. A second attempt on every pack does not fit. Invoices are UNKNOWN. The 15 USD reserve is untouched.

## Code, after both image producers finish

Bind the slinger crop through the plate override path. Keep the three crops above. Use `visible-size.js` conservative caps. Gear icons, artifact icons, mounts, and effect atlases still need explicit screen bindings. This handoff does not edit `src/`.
"""
    (QA / "handoff.md").write_text(handoff, encoding="utf-8")
    print("rows", len(rows_out), "ready", len(ready_ids), "partial", len(partial_ids), "fail", len(failed_ids), "packs", len(pack_objs))


if __name__ == "__main__":
    main()
