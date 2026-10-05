"""Measure 1K sources and write live actor/plate/building catalogs.

Does not call a provider, edit locks, or replace prior derivative hashes.
Industrial heavy is omitted: the 1K plate is a rifleman, not a steam walker.
Native-2K iron melee stencil is not used; the 1K legionary is.
"""
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
PROD = ROOT / "assets/production"
OUT = ROOT / "assets/delivery/stone-starter-20261003/derivatives/v2/live"
DATA = ROOT / "src/data"
QA = ROOT / "qa/code-art-assembly-20261004"
AGES = ["stone", "bronze", "iron", "medieval", "gunpowder", "industrial", "modern", "future"]
ROLES = ["melee", "ranged", "heavy"]
ATTACKERS = ["brute", "runner", "archer", "sapper", "shaman"]
TOWERS = ["arrow", "splash", "slow", "support"]
CREATURES = ["wolf", "bandit", "bear", "harpy", "golem", "griffin", "wyvern", "drone"]
CLASSES = ["knight", "ranger", "warlock", "mage", "paladin", "barbarian", "necromancer", "healer"]
BUILDINGS = ["townhall", "farm", "lumber", "quarry", "mine", "barracks", "workshop", "hall", "armory", "walls"]
REJECTED = {
    "troop-industrial-heavy": "1K plate is a rifleman with a machine gun, not a steam walker",
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def find_token(token):
    hits = [p for p in PROD.glob(f"**/*{token}.png") if p.name.endswith(token + ".png") or p.stem.endswith(token)]
    hits = [p for p in hits if p.name.endswith(token + ".png")]
    if not hits:
        return None
    hits.sort(key=lambda p: str(p))
    return hits[-1]


def load_rgba(path):
    return np.asarray(Image.open(path).convert("RGBA")).copy()


def matte(arr):
    r, g, b, a = arr[:,:,0].astype(np.int16), arr[:,:,1].astype(np.int16), arr[:,:,2].astype(np.int16), arr[:,:,3]
    magenta = (r > 170) & (b > 170) & (g < 100)
    green = (g > 115) & (r < 220) & (b < 200) & (g > r + 12) & (g > b + 12) & (g < 250)
    drop = magenta | green | (a < 8)
    arr = arr.copy()
    arr[drop, 3] = 0
    return arr


def foreground(arr):
    return arr[:,:,3] > 16


def components(fg, min_area):
    labels, _ = ndimage.label(fg)
    out = []
    for lab, sl in enumerate(ndimage.find_objects(labels), start=1):
        if sl is None:
            continue
        area = int((labels[sl] == lab).sum())
        if area < min_area:
            continue
        ys, xs = sl
        x0, y0, x1, y1 = int(xs.start), int(ys.start), int(xs.stop - 1), int(ys.stop - 1)
        out.append({
            "x": x0, "y": y0, "w": x1 - x0 + 1, "h": y1 - y0 + 1, "area": area,
            "cx": (x0 + x1) / 2, "cy": (y0 + y1) / 2,
        })
    out.sort(key=lambda b: -b["area"])
    return out


def box_of(b):
    return [int(b["x"]), int(b["y"]), int(b["w"]), int(b["h"])]


def split_vertical(fg, box, frac=(0.35, 0.7)):
    x, y, w, h = box["x"], box["y"], box["w"], box["h"]
    crop = fg[y:y + h, x:x + w]
    counts = crop.sum(axis=1)
    if h < 40:
        return None
    lo, hi = int(h * frac[0]), int(h * frac[1])
    if hi <= lo:
        return None
    neck = lo + int(np.argmin(counts[lo:hi]))
    if counts[neck] > max(8, counts.max() * 0.72):
        return None
    upper = {**box, "h": neck, "cy": y + neck / 2, "area": int(counts[:neck].sum())}
    lower = {**box, "y": y + neck, "h": h - neck, "cy": y + neck + (h - neck) / 2, "area": int(counts[neck:].sum())}
    if upper["h"] < 16 or lower["h"] < 16:
        return None
    return upper, lower


def solidity(box):
    return box["area"] / max(1, box["w"] * box["h"])


def choose_humanoid(boxes, shape):
    height, width = shape
    torso_pool = [b for b in boxes if b["cx"] > width * 0.52 and b["cy"] < height * 0.5 and solidity(b) > 0.45]
    if not torso_pool:
        raise RuntimeError("no torso")
    torso = max(torso_pool, key=lambda b: b["area"])
    heads = [b for b in boxes if b["cx"] < width * 0.5 and b["cy"] < height * 0.5 and 3500 < b["area"] < 55000 and b["h"] < height * 0.36 and solidity(b) > 0.45]
    if not heads:
        raise RuntimeError("no head")
    head = max(heads, key=lambda b: b["area"])
    # A sparse spear bundle stays out. A dense single weapon or a tall blade can attach.
    weapons = [b for b in boxes if b is not head and b["cx"] < width * 0.5 and b["cy"] > height * 0.4 and b["area"] > 2500 and (solidity(b) >= 0.45 or (solidity(b) >= 0.28 and b["h"] > b["w"] * 2))]
    weapon = max(weapons, key=lambda b: b["area"]) if weapons else None
    arms = [b for b in boxes if b is not torso and b is not weapon and 70 < b["h"] < height * 0.24 and b["w"] < width * 0.16 and solidity(b) > 0.5 and b["area"] > 4000]
    arm = max(arms, key=lambda b: solidity(b)) if arms else None
    forearms = [b for b in arms if b is not arm and b["cy"] > height * 0.45]
    forearm = max(forearms, key=lambda b: solidity(b)) if forearms else None
    thighs = [b for b in boxes if b["cx"] > width * 0.5 and height * 0.48 < b["cy"] < height * 0.74 and b["h"] < height * 0.22 and b["w"] < width * 0.16 and solidity(b) > 0.55]
    shins = [b for b in boxes if b["cx"] > width * 0.5 and b["cy"] > height * 0.72 and b["h"] < height * 0.26 and b["w"] < width * 0.16 and solidity(b) > 0.4 and b["h"] > height * 0.08]
    feet = [b for b in boxes if b["cx"] > width * 0.5 and b["cy"] > height * 0.88 and 600 < b["area"] < 8000 and b["h"] < height * 0.12 and solidity(b) > 0.45]
    thigh = max(thighs, key=lambda b: solidity(b)) if thighs else None
    shin = max(shins, key=lambda b: solidity(b)) if shins else None
    foot = max(feet, key=lambda b: solidity(b)) if feet else None
    return {"torso": torso, "head": head, "weapon": weapon, "arm": arm, "forearm": forearm, "thigh": thigh, "shin": shin, "foot": foot}


def save_sheet(arr, rel):
    path = OUT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(arr).save(path)
    return "assets/delivery/stone-starter-20261003/derivatives/v2/live/" + rel.replace("\\", "/")


def trim_plate(arr):
    fg = foreground(arr)
    if not fg.any():
        return arr
    ys, xs = np.where(fg)
    pad = 8
    y0, y1 = max(0, ys.min() - pad), min(arr.shape[0], ys.max() + 1 + pad)
    x0, x1 = max(0, xs.min() - pad), min(arr.shape[1], xs.max() + 1 + pad)
    return arr[y0:y1, x0:x1]


def foot_fraction(arr):
    fg = foreground(arr)
    ys, xs = np.where(fg)
    if len(ys) == 0:
        return [0.5, 1], [arr.shape[1], arr.shape[0]]
    band = ys >= np.percentile(ys, 97)
    return [float(xs[band].mean() / arr.shape[1]), float(ys[band].mean() / arr.shape[0])], [int(arr.shape[1]), int(arr.shape[0])]


def row_runs(row):
    count, start = 0, None
    for value in row:
        if value and start is None:
            start = 1
            count += 1
        elif not value:
            start = None
    return count


def narrow_runs(row):
    runs, start = [], None
    for i, value in enumerate(row):
        if value and start is None:
            start = i
        elif not value and start is not None:
            if i - start >= 18:
                runs.append((start, i - start))
            start = None
    if start is not None and len(row) - start >= 18:
        runs.append((start, len(row) - start))
    return [run for run in runs if run[1] <= 100]


def horse_parts(fg):
    ys, xs = np.where(fg)
    y0, y1, x0, x1 = int(ys.min()), int(ys.max()), int(xs.min()), int(xs.max())
    best = None
    for y in range(y0 + 200, y1):
        runs = narrow_runs(fg[y, x0:x1 + 1])
        if len(runs) != 4:
            continue
        spread = runs[-1][0] - runs[0][0]
        if best is None or spread > best[0]:
            best = (spread, y, runs)
    if best is None:
        return None
    _, seed_y, runs = best
    legs = []
    for start, width in runs:
        center = start + width / 2
        half = max(18, width * 0.7)
        left = int(max(0, center - half))
        right = int(min(x1 - x0, center + half))
        top = seed_y
        while top > y0 + 40:
            band = fg[top - 1, x0 + left:x0 + right + 1]
            if band.sum() < 12 or narrow_runs(fg[top - 1, x0:x1 + 1]) == []:
                break
            # Stop when this column merges into a mass wider than a leg.
            row = fg[top - 1, x0:x1 + 1]
            merged = False
            run_start = None
            for i, value in enumerate(row):
                if value and run_start is None:
                    run_start = i
                if (not value or i == len(row) - 1) and run_start is not None:
                    end = i if not value else i
                    if run_start <= center <= end and end - run_start > 110:
                        merged = True
                    run_start = None
            if merged:
                break
            top -= 1
        bottom = seed_y
        while bottom < y1:
            band = fg[bottom + 1, x0 + left:x0 + right + 1]
            if band.sum() < 8:
                break
            bottom += 1
        slab = fg[top:bottom + 1, x0 + left:x0 + right + 1]
        if slab.sum() < 300:
            continue
        ys2, xs2 = np.where(slab)
        legs.append({
            "x": int(x0 + left + xs2.min()),
            "y": int(top + ys2.min()),
            "w": int(xs2.max() - xs2.min() + 1),
            "h": int(ys2.max() - ys2.min() + 1),
        })
    body = {"x": x0, "y": y0, "w": x1 - x0 + 1, "h": y1 - y0 + 1}
    return {"body": body, "legs": legs, "cut": min(leg["y"] for leg in legs)}


def compose_preview(sheet, parts, path):
    canvas = Image.new("RGBA", (480, 640), (20, 28, 24, 255))
    order = ["thigh", "shin", "foot", "torso", "head", "arm", "forearm", "weapon"]
    anchors = {
        "torso": (230, 250, 0.50, 0.92, 200),
        "head": (230, 118, 0.50, 0.90, 100),
        "arm": (300, 175, 0.50, 0.12, 90),
        "forearm": (318, 250, 0.50, 0.10, 80),
        "weapon": (340, 300, 0.50, 0.15, 120),
        "thigh": (200, 300, 0.50, 0.10, 100),
        "shin": (202, 400, 0.50, 0.08, 100),
        "foot": (204, 500, 0.50, 0.15, 64),
    }
    for name in order:
        part = parts.get(name)
        if not part:
            continue
        x, y, w, h = part
        crop = Image.fromarray(sheet[y:y + h, x:x + w])
        ax, ay, px, py, target = anchors[name]
        scale = target / max(w, h)
        crop = crop.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.Resampling.BILINEAR)
        canvas.alpha_composite(crop, (int(ax - crop.size[0] * px), int(ay - crop.size[1] * py)))
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    QA.mkdir(parents=True, exist_ok=True)
    record = []
    atlas = {"version": "measured-parts-v1", "status": "MEASURED_NOT_OWNER_ACCEPTED", "classes": {}, "mounts": {}}

    for class_id in CLASSES:
        source = find_token(f"rig-{class_id}")
        if source is None:
            raise SystemExit(f"missing rig {class_id}")
        raw = load_rgba(source)
        arr = matte(raw)
        fg = foreground(arr)
        boxes = components(fg, 700)
        chosen = choose_humanoid(boxes, fg.shape)
        parts = {}
        for key, box in chosen.items():
            if box is None:
                continue
            parts[key] = box_of(box)
        if "thigh" not in parts or "shin" not in parts:
            tall = [b for b in boxes if b["cx"] > fg.shape[1] * 0.5 and b["cy"] > fg.shape[0] * 0.5 and b["h"] > fg.shape[0] * 0.25]
            if tall:
                split = split_vertical(fg, tall[0])
                if split:
                    parts["thigh"] = box_of(split[0])
                    parts["shin"] = box_of(split[1])
        rel = save_sheet(arr, f"rigs/{class_id}.png")
        atlas["classes"][class_id] = {
            "file": rel,
            "source": str(source.relative_to(ROOT)).replace("\\", "/"),
            "sourceSHA256": sha256(source),
            "parts": parts,
            "pivots": {
                "torso": [0.5, 0.92], "head": [0.5, 0.9], "arm": [0.5, 0.12], "forearm": [0.5, 0.1],
                "weapon": [0.5, 0.15], "thigh": [0.5, 0.1], "shin": [0.5, 0.08], "foot": [0.5, 0.15],
            },
        }
        record.append({"id": f"rig-{class_id}", "source": atlas["classes"][class_id]["source"], "sha256": atlas["classes"][class_id]["sourceSHA256"], "parts": list(parts)})
        if class_id in ("knight", "mage"):
            compose_preview(arr, parts, QA / f"preview-{class_id}.png")

    horse_path = find_token("mount-horse")
    horse = matte(load_rgba(horse_path))
    split = horse_parts(foreground(horse))
    horse_file = save_sheet(horse, "mounts/horse.png")
    mount = {"file": horse_file, "source": str(horse_path.relative_to(ROOT)).replace("\\", "/"), "sourceSHA256": sha256(horse_path), "body": None, "legs": [], "bodyFile": None}
    if split:
        body_px = horse.copy()
        for leg in split["legs"]:
            body_px[leg["y"]:leg["y"] + leg["h"], leg["x"]:leg["x"] + leg["w"], 3] = 0
        mount["bodyFile"] = save_sheet(body_px, "mounts/horse-body.png")
        mount["body"] = [split["body"]["x"], split["body"]["y"], split["body"]["w"], split["body"]["h"]]
        mount["legs"] = [[leg["x"], leg["y"], leg["w"], leg["h"]] for leg in split["legs"]]
        preview = Image.new("RGBA", (640, 480), (20, 28, 24, 255))
        bx, by, bw, bh = mount["body"]
        body = Image.fromarray(horse[by:by + bh, bx:bx + bw])
        body.thumbnail((420, 280))
        preview.alpha_composite(body, (80, 20))
        for index, leg in enumerate(mount["legs"]):
            crop = Image.fromarray(horse[leg[1]:leg[1] + leg[3], leg[0]:leg[0] + leg[2]])
            crop.thumbnail((70, 160))
            preview.alpha_composite(crop, (40 + index * 80, 300))
        preview.save(QA / "preview-horse.png")
    atlas["mounts"]["horse"] = mount

    plates = {
        "version": "live-plates-v1",
        "status": "SOURCE_BOUND_NOT_OWNER_ACCEPTED",
        "rejected": REJECTED,
        "creatures": {},
        "troops": {},
        "attackers": {},
        "towers": {},
        "projectiles": {},
    }

    def put_plate(group, key, token):
        if token in REJECTED:
            plates[group][key] = None
            record.append({"id": token, "rejected": REJECTED[token]})
            return
        source = find_token(token)
        if source is None:
            plates[group][key] = None
            record.append({"id": token, "missing": True})
            return
        trimmed = trim_plate(matte(load_rgba(source)))
        rel = save_sheet(trimmed, f"plates/{token}.png")
        plates[group][key] = {"file": rel, "source": str(source.relative_to(ROOT)).replace("\\", "/"), "sourceSHA256": sha256(source), "width": trimmed.shape[1], "height": trimmed.shape[0]}
        record.append({"id": token, "file": rel, "sha256": plates[group][key]["sourceSHA256"]})

    for creature in CREATURES:
        put_plate("creatures", creature, f"creature-{creature}")
    for age, age_name in enumerate(AGES):
        for role in ROLES:
            put_plate("troops", f"{age}-{role}", f"troop-{age_name}-{role}")
        for role in ATTACKERS:
            put_plate("attackers", f"{age}-{role}", f"attacker-{age_name}-{role}")
        for family in TOWERS:
            put_plate("towers", f"{age}-{family}", f"tower-{age_name}-{family}")
    for key, token in {"arrow": "effect-arrow", "splash": "effect-spell-fireball", "slow": "effect-spell-slow", "support": "effect-bless"}.items():
        put_plate("projectiles", key, token)

    buildings = {"version": "measured-opaque-foot-v1", "status": "MEASURED_NOT_OWNER_ACCEPTED", "note": "Uniform scale. Foot is the centroid of the lowest 3 percent of opaque pixels after matte. Terrain files and the Stone Hall matrix are unchanged.", "ages": {}}
    for age_name in AGES:
        buildings["ages"][age_name] = {}
        for building in BUILDINGS:
            token = f"{building}-{age_name}"
            source = find_token(token)
            if source is None:
                buildings["ages"][age_name][building] = None
                continue
            trimmed = trim_plate(matte(load_rgba(source)))
            foot, _ = foot_fraction(trimmed)
            rel = save_sheet(trimmed, f"buildings/{token}.png")
            buildings["ages"][age_name][building] = {
                "file": rel,
                "source": str(source.relative_to(ROOT)).replace("\\", "/"),
                "sourceSHA256": sha256(source),
                "width": int(trimmed.shape[1]),
                "height": int(trimmed.shape[0]),
                "foot": foot,
            }
            record.append({"id": token, "file": rel, "foot": foot})

    DATA.mkdir(parents=True, exist_ok=True)
    (DATA / "actor-atlas.json").write_text(json.dumps(atlas, indent=2) + "\n", encoding="utf-8")
    (DATA / "plate-catalog.json").write_text(json.dumps(plates, indent=2) + "\n", encoding="utf-8")
    (DATA / "age-buildings.json").write_text(json.dumps(buildings, indent=2) + "\n", encoding="utf-8")
    (QA / "processing.json").write_text(json.dumps({"recipe": "magenta-and-green-pad-matte-v1", "items": record}, indent=2) + "\n", encoding="utf-8")
    print(f"classes {len(atlas['classes'])} horseLegs {len(mount['legs'])} plates creatures {sum(1 for v in plates['creatures'].values() if v)}")


if __name__ == "__main__":
    main()
