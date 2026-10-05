"""Publish the v4 delivery interface without overwriting v3."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path("C:/dev/ages-of-dominion-reborn")

# Pixel check qa/image-v4-repair-20261004/requirement-check-v4.json. Not owner acceptance.
REVIEWED = {
    "troop-stone-melee": "BOOTS_CONNECTED_RESIDUAL_DIRT",
    "troop-stone-ranged": "BOOTS_INTACT_WOOD_AND_GRAVEL_REMAIN",
    "hero-mount-horse": "HOOVES_INTACT_PLANE_GONE_HAIRLINE_REMAINS",
    "troop-industrial-ranged": "PRONE_LOOSE_RIFLE_DROPPED_PINK_SMEAR_REMAINS",
    "hero-mount-motor-transport": "WHEELS_INTACT_GROUND_NOT_GONE",
    "hero-mount-future-transport": "WHEELS_INTACT_GROUND_NOT_GONE",
    "troop-bronze-melee": "LOCAL_REQUIREMENT_MET_NOT_OWNER_ACCEPTED",
    "troop-bronze-ranged": "LOCAL_REQUIREMENT_MET_NOT_OWNER_ACCEPTED",
    "troop-iron-ranged": "LOCAL_REQUIREMENT_MET_NOT_OWNER_ACCEPTED",
    "troop-iron-heavy": "LOCAL_REQUIREMENT_MET_NOT_OWNER_ACCEPTED",
    "troop-gunpowder-melee": "LOCAL_REQUIREMENT_MET_NOT_OWNER_ACCEPTED",
    "troop-gunpowder-ranged": "LOCAL_REQUIREMENT_MET_NOT_OWNER_ACCEPTED",
    "troop-gunpowder-heavy": "COBBLE_PLANE_REMOVED_SMALL_SHADOW_REMAINS",
    "troop-modern-melee": "LOCAL_REQUIREMENT_MET_NOT_OWNER_ACCEPTED",
    "troop-modern-ranged": "ONE_SNIPER_SNOW_REMAINS",
    "troop-future-melee": "LOCAL_REQUIREMENT_MET_NOT_OWNER_ACCEPTED",
    "troop-future-ranged": "NEIGHBOR_RECT_REMOVED_GROUND_SHADOW_REMAINS",
    "troop-future-heavy": "THRUSTERS_KEPT_DARK_SHADOW_REMAINS",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def literal_source(path: str) -> tuple[str, str | None]:
    note = None
    if " (" in path and path.endswith(")"):
        path = path.rsplit(" (", 1)[0]
        note = "dimensions removed from the path string; see dimensions"
    if path.startswith("production-"):
        path = "assets/production/" + path
        note = (note or "") + " assets/production prefix added"
    return path.replace("\\", "/"), note


def main():
    v3 = json.loads((ROOT / "docs/plan/IMAGE-ROLE-DISPOSITIONS-V3-2026-10-04.json").read_text(encoding="utf-8"))
    actors = json.loads((ROOT / "qa/image-v4-repair-20261004/actors-mounts-v4.json").read_text(encoding="utf-8"))
    by_id = {row["id"]: row for row in actors}
    missing = []
    rows = []
    for row in v3["rows"]:
        source = dict(row.get("source") or {})
        path, note = literal_source(source.get("path", ""))
        source["path"] = path
        if note:
            source["pathNote"] = note.strip()
        if path and not (ROOT / path).exists():
            missing.append(path)
        item = {
            "id": row["id"],
            "category": row.get("category"),
            "v3ContentMatte": row.get("contentMatte"),
            "v4ContentStatus": REVIEWED.get(row["id"], row.get("contentMatte")),
            "technical": "PASS_FILE_EXISTS" if path and (ROOT / path).exists() else row.get("technical"),
            "runtime": "UNVERIFIED",
            "owner": "UNVERIFIED",
            "source": source,
            "v3Derivative": row.get("derivative"),
        }
        if row["id"] in by_id:
            v4 = by_id[row["id"]]
            item["v4Derivative"] = v4.get("derivative")
            item["v4Evidence"] = v4.get("evidence")
            item["v4Landmarks"] = v4.get("landmarks")
            item["v4Disposition"] = REVIEWED.get(row["id"], v4.get("dispositionStatus"))
            dpath = (v4.get("derivative") or {}).get("path")
            if dpath and not (ROOT / dpath).exists():
                missing.append(dpath)
        if row["id"] in {"troop-iron-melee", "troop-industrial-heavy", "knight-mounted-master"}:
            item["selectedRole"] = "FAIL"
        rows.append(item)
    aliases = [
        {
            "advertisedPath": "assets/derivatives/substitutions/v3/troop-iron-melee-legionary-1k.png",
            "exists": False,
            "actualPath": "assets/derivatives/substitutions/v3/troop-iron-melee.png",
            "v4Path": "assets/derivatives/substitutions/v3/troop-iron-melee.png",
            "ids": ["substitution-troop-iron-melee", "troop-iron-melee"],
        },
        {
            "advertisedPath": "assets/derivatives/substitutions/v3/troop-industrial-heavy-steamwalker-1k.png",
            "exists": False,
            "actualPath": "assets/derivatives/substitutions/v3/troop-industrial-heavy.png",
            "ids": ["substitution-troop-industrial-heavy", "troop-industrial-heavy"],
        },
        {
            "v2RowCount": 76,
            "v3DistinctRoles": 75,
            "note": "The extra v2 row was a duplicate mountedKnight, not a missing paid identity.",
        },
    ]
    # Preserve substitution files as separately identified 1k sources.
    for alias in aliases:
        actual = alias.get("actualPath")
        if actual:
            alias["actualExists"] = (ROOT / actual).exists()
            if alias["actualExists"]:
                alias["sha256"] = sha256_file(ROOT / actual)
    card = json.loads((ROOT / "qa/image-v4-repair-20261004/ancient-knight-card-v4.json").read_text(encoding="utf-8"))
    if not (ROOT / card["crop"]["path"]).exists():
        missing.append(card["crop"]["path"])
    bounded = [
        {"id": "troop-stone-melee", "status": REVIEWED["troop-stone-melee"], "use": "Code may review this sample. It is not a clean accepted world sprite."},
        {"id": "hero-mount-horse", "status": REVIEWED["hero-mount-horse"], "use": "Hooves are present. A grey hairline can remain. Not an accepted mount."},
    ]
    doc = {
        "version": "4.0-image-interface-20261004",
        "codeAIHandoffReady": False,
        "usableWorldSpriteCount": None,
        "reason": "No blanket usable count. Only the bounded review rows below were inspected closely enough to name.",
        "roleRowCount": len(rows),
        "v3RoleRowCount": v3["summary"]["totalRows"],
        "idAliases": aliases,
        "boundedReviewSamples": bounded,
        "additions": [card],
        "missingReferencedFiles": missing,
        "rows": rows,
        "gates": {
            "owner": "UNVERIFIED",
            "runtime": "UNVERIFIED",
            "newPaidScope": False,
        },
    }
    dest = ROOT / "docs/plan/IMAGE-DELIVERY-INTERFACE-V4-2026-10-04.json"
    dest.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    print("rows", len(rows), "missing", len(missing))
    if missing[:8]:
        print("missing sample", missing[:8])


if __name__ == "__main__":
    main()
