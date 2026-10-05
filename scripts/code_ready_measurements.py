"""Code-owned measurements. Does not write Image derivative paths or raw art."""
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / "qa" / "code-ready-20261004"
CONSUMER = ROOT / "assets" / "consumers" / "code-20261004"
BINDING = ROOT / "src" / "data" / "anatomy-binding-v1.json"
PROPOSAL = ROOT / "docs" / "plan" / "KINGDOM-SCENE-PROPOSAL-V1-2026-10-04.json"

RANGER = {
    "torso": ("torso_tunic.png", "torso", [0.5, 1.0], 1),
    "head": ("head_cowl.png", "head", [0.5, 0.98], 0.72),
    "quiver": ("arm_upper_left.png", "quiver", [0.45, 0.08], 0.48),
    "bow": ("weapon_longbow.png", "bow", [0.62, 0.46], 0.4),
    "thighL": ("thigh_left.png", "thigh", [0.5, 0.06], 0.82),
    "shinL": ("shin_left.png", "shin", [0.5, 0.05], 0.72),
    "bootL": ("boot_foot_left.png", "boot", [0.5, 0.04], 0.78),
    "thighR": ("thigh_right.png", "thigh", [0.5, 0.06], 0.82),
    "shinR": ("shin_right.png", "shin", [0.5, 0.05], 0.72),
    "bootR": ("boot_foot_right.png", "boot", [0.5, 0.04], 0.78),
}
WITHHELD = [
    {
        "file": "assets/derivatives/rigs/v3/ranger/forearm_hand_left.png",
        "publishedName": "forearm_hand_left",
        "reviewedAs": "greave",
        "reason": "Painted knee and shin plate, not a hand.",
    },
    {
        "file": "assets/derivatives/rigs/v3/ranger/forearm_hand_right.png",
        "publishedName": "forearm_hand_right",
        "reviewedAs": "withheld-until-separate-pixel-pass",
        "reason": "Same canvas family as the left file, which is a greave. Not bound as a hand.",
    },
    {
        "file": "assets/derivatives/rigs/v3/ranger/quiver_cloak.png",
        "publishedName": "quiver_cloak",
        "reviewedAs": "duplicate-head",
        "reason": "Second hooded head, not a cloak or quiver.",
    },
    {
        "file": "assets/derivatives/mounts/v3/hero-mount-horse.png",
        "publishedName": "hero-mount-horse",
        "reviewedAs": "floor-band",
        "reason": "Lowest opaque rows stay a flat band. Not a world mount.",
    },
]


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def part_record(key):
    name, role, pivot, scale = RANGER[key]
    path = ROOT / "assets" / "derivatives" / "rigs" / "v3" / "ranger" / name
    image = Image.open(path)
    return {
        "id": key,
        "role": role,
        "file": path.relative_to(ROOT).as_posix(),
        "sha256": sha256(path),
        "width": image.size[0],
        "height": image.size[1],
        "pivot": pivot,
        "scale": scale,
        "publishedName": name.replace(".png", ""),
    }


def mask(path, scale):
    image = Image.open(ROOT / path).convert("RGBA")
    width = max(1, round(image.size[0] * scale))
    height = max(1, round(image.size[1] * scale))
    image = image.resize((width, height), Image.Resampling.BILINEAR)
    alpha = np.asarray(image.getchannel("A"))
    return alpha > 32


def paste(canvas, part_mask, pivot, dest, angle):
    height, width = part_mask.shape
    sprite = Image.new("L", (width, height), 0)
    sprite.putdata(part_mask.astype(np.uint8).flatten() * 255)
    px, py = pivot
    ox, oy = width * px, height * py
    rotated = sprite.rotate(angle, resample=Image.Resampling.BILINEAR, center=(ox, oy), expand=True)
    # PIL rotate expand keeps the original center. Recompute where the pivot landed.
    cx = (rotated.size[0] / 2) + (ox - width / 2)
    cy = (rotated.size[1] / 2) + (oy - height / 2)
    left = int(round(dest[0] - cx))
    top = int(round(dest[1] - cy))
    base = Image.new("L", (canvas.shape[1], canvas.shape[0]), 0)
    base.paste(rotated, (left, top))
    return np.asarray(base) > 16


def overlap_count(parent, child, parent_pivot, child_pivot, attach, angle):
    pad = 800
    canvas_h, canvas_w = parent.shape[0] + pad, parent.shape[1] + pad
    origin = (pad // 2 + parent.shape[1] * parent_pivot[0], pad // 2 + parent.shape[0] * parent_pivot[1])
    parent_dest = origin
    child_dest = (origin[0] + attach[0], origin[1] + attach[1])
    board = np.zeros((canvas_h, canvas_w), dtype=bool)
    parent_pixels = paste(board, parent, parent_pivot, parent_dest, 0)
    child_pixels = paste(board, child, child_pivot, child_dest, angle)
    return int(np.logical_and(parent_pixels, child_pixels).sum())


def measure_overlap(binding):
    parts = binding["parts"]
    torso = mask(parts["torso"]["file"], parts["torso"]["scale"])
    head = mask(parts["head"]["file"], parts["head"]["scale"])
    thigh = mask(parts["thighL"]["file"], parts["thighL"]["scale"])
    shin = mask(parts["shinL"]["file"], parts["shinL"]["scale"])
    boot = mask(parts["bootL"]["file"], parts["bootL"]["scale"])
    bow = mask(parts["bow"]["file"], parts["bow"]["scale"])
    inset = binding["socketOverlapPx"]
    torso_h = torso.shape[0]
    head_attach = (0, -torso_h + int(torso_h * binding["head"]["attach"][1]) )
    # Head pivot sits on the collar fraction, overlapping the torso.
    head_attach = (
        (binding["head"]["attach"][0] - parts["torso"]["pivot"][0]) * torso.shape[1],
        (binding["head"]["attach"][1] - parts["torso"]["pivot"][1]) * torso.shape[0],
    )
    thigh_h = thigh.shape[0]
    shin_h = shin.shape[0]
    thigh_len = thigh_h * (1 - parts["thighL"]["pivot"][1]) - inset
    shin_len = shin_h * (1 - parts["shinL"]["pivot"][1]) - inset
    bow_attach = (
        (binding["accessories"][1]["attach"][0] - parts["torso"]["pivot"][0]) * torso.shape[1],
        (binding["accessories"][1]["attach"][1] - parts["torso"]["pivot"][1]) * torso.shape[0],
    )
    checks = {
        "head-torso-0": overlap_count(torso, head, parts["torso"]["pivot"], parts["head"]["pivot"], head_attach, 0),
        "head-torso-24": overlap_count(torso, head, parts["torso"]["pivot"], parts["head"]["pivot"], head_attach, 24),
        "head-torso-minus24": overlap_count(torso, head, parts["torso"]["pivot"], parts["head"]["pivot"], head_attach, -24),
        "shin-thigh-0": overlap_count(thigh, shin, parts["thighL"]["pivot"], parts["shinL"]["pivot"], (0, thigh_len), 0),
        "shin-thigh-48": overlap_count(thigh, shin, parts["thighL"]["pivot"], parts["shinL"]["pivot"], (0, thigh_len), 48),
        "shin-thigh-minus48": overlap_count(thigh, shin, parts["thighL"]["pivot"], parts["shinL"]["pivot"], (0, thigh_len), -48),
        "boot-shin-0": overlap_count(shin, boot, parts["shinL"]["pivot"], parts["bootL"]["pivot"], (0, shin_len), 0),
        "boot-shin-36": overlap_count(shin, boot, parts["shinL"]["pivot"], parts["bootL"]["pivot"], (0, shin_len), 36),
        "bow-torso-0": overlap_count(torso, bow, parts["torso"]["pivot"], parts["bow"]["pivot"], bow_attach, 0),
        "bow-torso-70": overlap_count(torso, bow, parts["torso"]["pivot"], parts["bow"]["pivot"], bow_attach, 70),
    }
    return checks


def render_pose(binding, pose, destination):
    parts = binding["parts"]
    images = {}
    preview = 0.42
    for key, part in parts.items():
        image = Image.open(ROOT / part["file"]).convert("RGBA")
        size = (max(1, round(part["width"] * part["scale"] * preview)), max(1, round(part["height"] * part["scale"] * preview)))
        images[key] = image.resize(size, Image.Resampling.BILINEAR)
    canvas = Image.new("RGBA", (900, 1100), (27, 40, 34, 255))

    def draw_part(base, key, joint, angle):
        image = images[key]
        part = parts[key]
        pivot = (image.size[0] * part["pivot"][0], image.size[1] * part["pivot"][1])
        rotated = image.rotate(-angle, resample=Image.Resampling.BILINEAR, center=pivot, expand=True)
        cx = rotated.size[0] / 2 + (pivot[0] - image.size[0] / 2)
        cy = rotated.size[1] / 2 + (pivot[1] - image.size[1] / 2)
        base.alpha_composite(rotated, (int(joint[0] - cx), int(joint[1] - cy)))
        return rotated

    torso = images["torso"]
    hip = (450, 620)
    # Legs first so the tunic hem covers the sockets.
    inset = binding["socketOverlapPx"]
    for side, sign in (("L", -1), ("R", 1)):
        thigh = f"thigh{side}"
        shin = f"shin{side}"
        boot = f"boot{side}"
        origin = (hip[0] + sign * torso.size[0] * (0.18 if side == "L" else 0.14), hip[1])
        draw_part(canvas, thigh, origin, pose[thigh])
        thigh_len = images[thigh].size[1] * (1 - parts[thigh]["pivot"][1]) - inset
        rad = np.deg2rad(pose[thigh])
        knee = (origin[0] + np.sin(rad) * thigh_len, origin[1] + np.cos(rad) * thigh_len)
        draw_part(canvas, shin, knee, pose[thigh] + pose[shin])
        shin_len = images[shin].size[1] * (1 - parts[shin]["pivot"][1]) - inset
        srad = np.deg2rad(pose[thigh] + pose[shin])
        ankle = (knee[0] + np.sin(srad) * shin_len, knee[1] + np.cos(srad) * shin_len)
        draw_part(canvas, boot, ankle, pose[thigh] + pose[shin] + pose[boot])
    quiver = binding["accessories"][0]
    q = images["quiver"]
    q_joint = (hip[0] + (quiver["attach"][0] - 0.5) * torso.size[0], hip[1] + (quiver["attach"][1] - 1) * torso.size[1])
    draw_part(canvas, "quiver", q_joint, 0)
    draw_part(canvas, "torso", hip, 0)
    head = binding["head"]
    h_joint = (hip[0] + (head["attach"][0] - 0.5) * torso.size[0], hip[1] + (head["attach"][1] - 1) * torso.size[1])
    draw_part(canvas, "head", h_joint, pose["head"])
    bow = binding["accessories"][1]
    b_joint = (hip[0] + (bow["attach"][0] - 0.5) * torso.size[0], hip[1] + (bow["attach"][1] - 1) * torso.size[1])
    draw_part(canvas, "bow", b_joint, pose["bow"])
    canvas.save(destination)


def project(matrix, x, y):
    a, b, c, d, e, f = matrix
    return [a * x + c * y + e, b * x + d * y + f]


def rect_gap(a, b):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    dx = max(0, max(ax, bx) - min(ax + aw, bx + bw))
    if ax + aw < bx:
        dx = bx - (ax + aw)
    elif bx + bw < ax:
        dx = ax - (bx + bw)
    else:
        dx = 0
    if ay + ah < by:
        dy = by - (ay + ah)
    elif by + bh < ay:
        dy = ay - (by + bh)
    else:
        dy = 0
    if dx == 0 and dy == 0:
        return 0
    if dx == 0:
        return dy
    if dy == 0:
        return dx
    return (dx * dx + dy * dy) ** 0.5


def kingdom_proposal():
    contract = json.loads((ROOT / "docs" / "plan" / "IMPLEMENTATION-CONTRACT.json").read_text(encoding="utf-8"))
    scene = json.loads((ROOT / "src" / "data" / "stone-scene.json").read_text(encoding="utf-8"))
    kingdom = contract["geometry"]["kingdom"]
    matrix = kingdom["worldToSource"]
    sites = []
    for site in kingdom["sites"]:
        x, y, w, h = site["rect"]
        corners = [project(matrix, px, py) for px, py in ((x, y), (x + w, y), (x + w, y + h), (x, y + h))]
        xs = [point[0] for point in corners]
        ys = [point[1] for point in corners]
        sites.append({
            "id": site["id"],
            "worldRect": site["rect"],
            "referenceCorners": [[round(point[0], 2), round(point[1], 2)] for point in corners],
            "referenceBounds": [round(min(xs), 2), round(min(ys), 2), round(max(xs), 2), round(max(ys), 2)],
        })
    gaps = []
    for index, left in enumerate(kingdom["sites"]):
        for right in kingdom["sites"][index + 1:]:
            gap = rect_gap(left["rect"], right["rect"])
            if gap < 1.2:
                gaps.append({"a": left["id"], "b": right["id"], "worldGap": round(gap, 3)})
    gaps.sort(key=lambda item: item["worldGap"])
    bridge = kingdom["bridges"][0]
    blocked = kingdom.get("blocked", [])
    road_lengths = []
    for road in kingdom["roads"]:
        length = 0
        for start, end in zip(road, road[1:]):
            length += ((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2) ** 0.5
        road_lengths.append(round(length, 3))
    terrain_path = ROOT / scene["terrain"]
    terrain = Image.open(terrain_path).convert("RGB")
    proposal = {
        "version": "kingdom-scene-proposal-v1",
        "status": "PROPOSAL_NOT_ACCEPTED",
        "contractUnchanged": True,
        "activeAffine": matrix,
        "hallScale": scene["hall"]["matrix"][0][0],
        "hallFile": scene["hall"]["file"],
        "terrainFile": scene["terrain"],
        "terrainSHA256": sha256(terrain_path),
        "terrainPixels": list(terrain.size),
        "referencePixels": kingdom["sourceSize"],
        "displayNote": "The live view fills this terrain into the 1376x768 frame. This proposal does not replace that file, stretch a repaired scene, or relabel thresholds as clearance.",
        "river": "The active contract has no separate river polygon. Blocked cells beside the named bridge are listed as contract blocked cells.",
        "bridge": {"id": bridge["id"], "worldRect": bridge["rect"], "referenceCenter": [round(value, 2) for value in project(matrix, bridge["rect"][0] + bridge["rect"][2] / 2, bridge["rect"][1] + bridge["rect"][3] / 2)]},
        "blockedCellCount": len(blocked),
        "blockedSample": blocked[:8],
        "roadWorldLengths": road_lengths,
        "nearestSiteGaps": gaps[:12],
        "sites": sites,
        "limits": [
            "Baked terrain still contains developed structures. It stays data-terrain-status baked-unaccepted.",
            "No obstacle, water, or road mask was painted from pixels, so clearance against scene content is not claimed.",
            "Site gaps below are distances between contract rectangles, not walkable clearance on the painting.",
            "Hall registration remains unaccepted. Hall scale stays 0.1312.",
            "Day 1 logic stays Hall level 1, 17 empty sites, and walls-presentation-v1.",
        ],
    }
    QA.mkdir(parents=True, exist_ok=True)
    before = terrain.copy()
    draw = ImageDraw.Draw(before)
    scale_x = terrain.size[0] / kingdom["sourceSize"][0]
    scale_y = terrain.size[1] / kingdom["sourceSize"][1]
    for site in sites:
        box = site["referenceBounds"]
        draw.rectangle([box[0] * scale_x, box[1] * scale_y, box[2] * scale_x, box[3] * scale_y], outline=(220, 64, 48))
    for road in kingdom["roads"]:
        points = []
        for point in road:
            ref = project(matrix, point[0], point[1])
            points.append((ref[0] * scale_x, ref[1] * scale_y))
        if len(points) > 1:
            draw.line(points, fill=(40, 150, 170), width=3)
    before_path = QA / "kingdom-proposal-before.png"
    before.save(before_path)
    after = Image.new("RGB", kingdom["sourceSize"], (196, 180, 154))
    draw = ImageDraw.Draw(after)
    draw.rectangle([0, 0, 1375, 767], outline=(90, 70, 48))
    for site in sites:
        box = site["referenceBounds"]
        draw.rectangle(box, outline=(90, 48, 36))
        draw.text((box[0] + 4, box[1] + 4), site["id"], fill=(48, 36, 28))
    for road in kingdom["roads"]:
        points = [tuple(project(matrix, point[0], point[1])) for point in road]
        draw.line(points, fill=(90, 110, 120), width=4)
    bridge_box = bridge["rect"]
    corners = [project(matrix, bridge_box[0], bridge_box[1]), project(matrix, bridge_box[0] + bridge_box[2], bridge_box[1] + bridge_box[3])]
    draw.rectangle([corners[0][0], corners[0][1], corners[1][0], corners[1][1]], outline=(40, 80, 120))
    draw.text((24, 24), "PROPOSAL v1 — contract geometry on a neutral field. Not accepted terrain.", fill=(48, 36, 28))
    after_path = QA / "kingdom-proposal-after.png"
    after.save(after_path)
    proposal["beforeImage"] = before_path.relative_to(ROOT).as_posix()
    proposal["afterImage"] = after_path.relative_to(ROOT).as_posix()
    PROPOSAL.write_text(json.dumps(proposal, indent=2) + "\n", encoding="utf-8")
    return proposal


def knight_card():
    source = Path(r"C:\dev\aod-art-src\hero-knight-ancient\attempt-1.png")
    image = Image.open(source).convert("RGB")
    # Bust square around the head and cuirass. Full sheet stays in the read-only source.
    crop = image.crop((450, 470, 1150, 1170))
    CONSUMER.mkdir(parents=True, exist_ok=True)
    target = CONSUMER / "portrait-ancient-knight-pending.png"
    crop.save(target)
    return {
        "file": target.relative_to(ROOT).as_posix(),
        "sha256": sha256(target),
        "width": crop.size[0],
        "height": crop.size[1],
        "source": str(source),
        "sourceSHA256": "eb03424f0a599894dfa5bdcc9124a84221c2959787c3c8fdc18d24636180acf8",
        "crop": [450, 470, 1150, 1170],
        "status": "PENDING_CARD_REVIEW",
    }


def main():
    QA.mkdir(parents=True, exist_ok=True)
    parts = {key: part_record(key) for key in RANGER}
    binding = {
        "version": "anatomy-binding-v1",
        "classId": "ranger",
        "status": "PARTIAL_PAINTED_REVIEW",
        "ownerAcceptance": "UNVERIFIED",
        "displayScale": 0.2,
        "socketOverlapPx": 46,
        "parts": parts,
        "head": {"part": "head", "attach": [0.5, 0.1]},
        "accessories": [
            {"part": "quiver", "attach": [0.1, 0.62], "behind": True, "renamedFrom": "arm_upper_left"},
            {"part": "bow", "attach": [0.78, 0.38], "angleKey": "bow", "missing": "hand", "renamedFrom": "weapon_longbow"},
        ],
        "hips": {"left": [-0.18, 0], "right": [0.14, 0]},
        "legs": {"left": ["thighL", "shinL", "bootL"], "right": ["thighR", "shinR", "bootR"]},
        "missing": ["upperArmLeft", "upperArmRight", "handLeft", "handRight"],
        "withheld": WITHHELD,
        "mount": {
            "status": "WITHHELD",
            "file": "assets/derivatives/mounts/v3/hero-mount-horse.png",
            "reason": "Lowest opaque rows form a flat band. The travel horse stays a labeled schematic.",
        },
        "testedAngles": {"head": 24, "thigh": 48, "shin": 36, "bow": 70},
    }
    checks = measure_overlap(binding)
    binding["overlap"] = checks
    required = [key for key in checks if not key.startswith("bow")]
    failures = [key for key in required if checks[key] < 40]
    binding["overlapPass"] = not failures
    binding["overlapFailures"] = failures
    BINDING.write_text(json.dumps(binding, indent=2) + "\n", encoding="utf-8")
    poses = {
        "idle": {"head": 0, "thighL": 0, "thighR": 0, "shinL": 0, "shinR": 0, "bootL": 0, "bootR": 0, "bow": -8},
        "extreme": {"head": 24, "thighL": 48, "thighR": -48, "shinL": 36, "shinR": -20, "bootL": 0, "bootR": 0, "bow": 70},
    }
    render_pose(binding, poses["idle"], QA / "ranger-idle.png")
    render_pose(binding, poses["extreme"], QA / "ranger-extreme.png")
    card = knight_card()
    (QA / "ancient-knight-card.json").write_text(json.dumps(card, indent=2) + "\n", encoding="utf-8")
    proposal = kingdom_proposal()
    plates = {
        "2-melee": sha256(ROOT / "assets/derivatives/substitutions/v3/troop-iron-melee.png"),
        "5-heavy": sha256(ROOT / "assets/derivatives/substitutions/v3/troop-industrial-heavy.png"),
    }
    (QA / "plate-hashes.json").write_text(json.dumps(plates, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"overlap": checks, "failures": failures, "card": card["sha256"], "plates": plates, "sites": len(proposal["sites"])}, indent=2))
    if failures:
        raise SystemExit(1)


def check():
    binding = json.loads(BINDING.read_text(encoding="utf-8"))
    checks = measure_overlap(binding)
    failures = []
    for key, count in checks.items():
        recorded = binding["overlap"][key]
        if count < 40 and not key.startswith("bow"):
            failures.append(f"{key} overlap {count}")
        if recorded < 40 and not key.startswith("bow"):
            failures.append(f"{key} recorded {recorded}")
        if abs(count - recorded) > max(80, recorded * 0.15):
            failures.append(f"{key} drifted {recorded} -> {count}")
    forbidden = ["shield", "helmet-as-torso", "sleeve-as-hand"]
    for part in binding["parts"].values():
        if part["role"] in {"foot", "hand"} and "shield" in part["file"]:
            failures.append(part["file"])
        if part["role"] == "torso" and "helmet" in part["file"]:
            failures.append(part["file"])
    withheld = " ".join(item["file"] for item in binding["withheld"])
    for name in ("forearm_hand_left", "quiver_cloak", "hero-mount-horse"):
        if name not in withheld:
            failures.append("missing withhold " + name)
    drawn = " ".join(part["file"] for part in binding["parts"].values())
    if "forearm_hand" in drawn or "quiver_cloak" in drawn:
        failures.append("withheld part is drawn")
    if failures:
        raise SystemExit("\n".join(failures + forbidden[:0]))
    print("anatomy overlap check passed")


if __name__ == "__main__":
    import sys
    if "--check" in sys.argv:
        check()
    else:
        main()
