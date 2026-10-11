"""Publish the unified reserve ledger record, interface, checkpoint, and handoff.

Does not call a provider. Archives control bytes before the one release append.
"""
from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import coordinator as c
import process_local as pl

ROOT = pl.ROOT
QA = pl.QA
CONTROLS = ROOT / "docs/plan/image-production"
NOW = datetime.now(timezone.utc).isoformat()
QUOTE = c.OWNER_QUOTE


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def archive_controls() -> dict:
    archive = QA / "vertex-coordinator/evidence/archive"
    archive.mkdir(parents=True, exist_ok=True)
    names = [
        "submission.mutex.json",
        "active-batch.lock.json",
        "pacing_state.json",
        "budget-ledger.json",
        "reconciled-accounting-ledger.json",
    ]
    recorded = {}
    for name in names:
        src = CONTROLS / name
        if not src.exists():
            recorded[name] = {"present": False}
            continue
        data = src.read_bytes()
        digest = c.sha256_bytes(data)
        dest = archive / f"{name}.{digest[:16]}"
        if not dest.exists():
            dest.write_bytes(data)
        recorded[name] = {"present": True, "sha256": digest, "bytes": len(data), "archive": dest.relative_to(ROOT).as_posix()}
    return recorded


def release_ledger() -> dict:
    path = CONTROLS / "budget-ledger.json"
    ledger = json.loads(path.read_text(encoding="utf-8"))
    before_reserve = ledger.get("safetyReserve")
    before_protected = ledger["vertexRepair20261009"]["currentCommittedProtectedUSD"]
    record = c.append_release_once(ledger, NOW)
    if ledger.get("safetyReserve") != before_reserve or ledger["vertexRepair20261009"]["currentCommittedProtectedUSD"] != before_protected:
        raise c.BudgetError("historical fields changed")
    tmp = path.with_suffix(".json.tmp-unified")
    tmp.write_text(json.dumps(ledger, indent=2), encoding="utf-8")
    tmp.replace(path)
    return record


def snapshot(archive_info) -> dict:
    paths = [
        "docs/plan/ENVIRONMENT-ART-VERTEX-REPAIR-INTERFACE-2026-10-09.json",
        "docs/plan/ACTORS-EQUIPMENT-VERTEX-REPAIR-INTERFACE-2026-10-09.json",
        "docs/plan/OWNER-RESERVE-RELEASE-SINGLE-IMAGE-AI-2026-10-09.md",
        "docs/plan/FULL-IMPLEMENTATION-SPEC.md",
        "src/data/implementation-contract.json",
        "src/data/stone-scene.json",
        "assets/derivatives/image-vertex-repair-20261009/actors/troops/troop-stone-ranged.png",
        "assets/derivatives/rigs/v7/healer/boot.png",
        "assets/runtime-code-20261007/troops/troop-stone-melee.png",
        "assets/runtime-code-20261007/troops/troop-industrial-ranged.png",
        "assets/runtime-code-20261007/troops/troop-industrial-heavy.png",
    ]
    files = []
    for rel in paths:
        path = ROOT / rel
        if not path.exists():
            files.append({"path": rel, "present": False})
            continue
        files.append({"path": rel, "sha256": pl.sha256_file(path), "bytes": path.stat().st_size, "present": True})
    payload = {
        "recordedAt": NOW,
        "controlsBeforeRelease": archive_info,
        "files": files,
        "note": "Producer, Code, and original bytes were hashed or archived. They were not rewritten except the authorized control ledger append.",
    }
    write_json(QA / "input_snapshot.json", payload)
    return payload


def rows_from_outputs():
    rows = []
    bodies = json.loads((QA / "diagnostics/bodies.json").read_text(encoding="utf-8"))
    for body in bodies:
        output = body.get("output")
        rows.append({
            "id": body["id"],
            "producer": "ACTORS",
            "role": "class-standing-body",
            "status": "PARTIAL",
            "sources": [{"path": body["source"], "sha256": body.get("fileSHA256"), "bytes": None, "dimensions": body.get("dimensions"), "roi": None, "frame": "NATIVE"}],
            "output": output,
            "reusedFrom": None,
            "sourceToOutput": [1, 0, 0, 1, 0, 0],
            "intendedUse": "SPRITE",
            "maxDisplayCssPx": 130,
            "limitBasis": "HEIGHT",
            "side": "UNKNOWN",
            "frame": "STANDING",
            "groundContact": body.get("groundContact"),
            "footprint": body.get("footprint"),
            "entrance": None,
            "heightEnvelope": body.get("heightEnvelope"),
            "transforms": {},
            "gates": {
                "binding": "PASS" if body.get("hashMatch") else "FAIL",
                "semantics": "PARTIAL",
                "matte": "PARTIAL" if body["id"] == "class-warlock-standing-body" else "PASS",
                "spatial": "PARTIAL",
                "articulation": "FAIL",
                "runtime": "UNVERIFIED",
                "owner": "UNVERIFIED",
            },
            "recipePath": None,
            "evidencePaths": ["qa/image-unified-reserve-20261009/review/bodies-on-dark.jpg"],
            "limitations": body.get("limitations") or [],
            "blockedBy": ["full gait and registered guide landmarks"],
            "nextAction": "Use as a static standing plate only. Do not claim a rig.",
        })
    head = json.loads((QA / "diagnostics/paladin-head.json").read_text(encoding="utf-8"))
    rows.append({
        "id": "paladin-head-raster",
        "producer": "ACTORS",
        "role": "class-head-card",
        "status": "PARTIAL",
        "sources": [],
        "output": head.get("output"),
        "reusedFrom": None,
        "sourceToOutput": head.get("sourceToOutput"),
        "intendedUse": "STATIC_CARD",
        "maxDisplayCssPx": 130,
        "limitBasis": "HEIGHT",
        "side": "UNKNOWN",
        "frame": "HEAD_BUST",
        "groundContact": None,
        "footprint": None,
        "entrance": None,
        "heightEnvelope": None,
        "transforms": {},
        "gates": {"binding": "PASS", "semantics": "PARTIAL", "matte": "PASS", "spatial": "NOT_APPLICABLE", "articulation": "NOT_APPLICABLE", "runtime": "UNVERIFIED", "owner": "UNVERIFIED"},
        "recipePath": None,
        "evidencePaths": ["qa/image-unified-reserve-20261009/review/head-on-black.jpg"],
        "limitations": head.get("limitations") or [],
        "blockedBy": [],
        "nextAction": None,
    })
    protected = json.loads((QA / "diagnostics/protected.json").read_text(encoding="utf-8"))
    slinger = ROOT / "assets/derivatives/image-vertex-repair-20261009/actors/troops/troop-stone-ranged.png"
    if slinger.exists() and pl.sha256_file(slinger) == pl.CROP_EXPECT["troop-stone-ranged"][0]:
        for row in protected:
            if row["id"] == "troop-stone-ranged":
                row["status"] = "REUSED"
                row["path"] = "assets/derivatives/image-vertex-repair-20261009/actors/troops/troop-stone-ranged.png"
                row["sha256"] = pl.CROP_EXPECT["troop-stone-ranged"][0]
                row["sourceToOutput"] = [1, 0, 0, 1, -363, -79]
                row["bytesUntouched"] = True
    for item in protected:
        ready = item.get("status") == "REUSED"
        rows.append({
            "id": item["id"],
            "producer": "ACTORS",
            "role": "protected-crop" if item["id"] != "healer-boot" else "rig-part",
            "status": "READY" if ready else "FAIL",
            "sources": [],
            "output": None,
            "reusedFrom": {"path": item.get("path"), "sha256": item.get("sha256") or item.get("expectedSHA256"), "bytes": None, "dimensions": item.get("dimensions")} if item.get("path") else None,
            "sourceToOutput": item.get("sourceToOutput"),
            "intendedUse": "SPRITE",
            "maxDisplayCssPx": 64 if "industrial" in item["id"] else 130,
            "limitBasis": "CONSERVATIVE_BOTH" if "industrial" in item["id"] else "HEIGHT",
            "side": "NOT_APPLICABLE",
            "frame": "STATIC",
            "groundContact": None,
            "footprint": None,
            "entrance": None,
            "heightEnvelope": None,
            "transforms": {},
            "gates": {"binding": "PASS" if ready else "FAIL", "semantics": "PASS" if ready else "UNVERIFIED", "matte": "PASS" if ready else "UNVERIFIED", "spatial": "PASS" if ready else "UNVERIFIED", "articulation": "NOT_APPLICABLE", "runtime": "UNVERIFIED", "owner": "UNVERIFIED"},
            "recipePath": None,
            "evidencePaths": [],
            "limitations": ["Bytes were rehashed and not rewritten."],
            "blockedBy": [] if ready else ["expected bytes were not found"],
            "nextAction": None if ready else "Restore the recorded crop by its hash. Do not regenerate it.",
        })
    blockers = [
        ("attacker-bronze-runner", "Full town illustration with a HUD bar. Local isolation cannot produce a clean runner. No paid request was sent because a validated person mask does not exist."),
        ("attacker-medieval-archer", "Olive field remains and the silhouette has missing interior regions. A constrained edit of this damaged plate was not purchased."),
        ("creature-drone", "Three drone poses plus a purple floor slab remain. Lights on the airframes were kept. Sheet timing was not invented."),
        ("creature-wolf", "Magenta paw pads, a ground rectangle, and a small green/red marker remain. They touch the paws, so the isolated-component rule kept them."),
        ("attacker-stone-brute", "A thin magenta rim remains on the club and a rectangular ground outline remains. The club itself was kept."),
        ("class-healer-standing-body", "No native was collected. Existing head cards and the protected boot were not assembled into a new paid wire in this pass."),
        ("workshop-iron", "The outer pale-green yard was removed and the building, forge, coal, and walls remain. An inner lawn and a hole in that yard remain."),
        ("hall-industrial", "A small green wedge at the lower edge remains."),
    ]
    for asset_id, reason in blockers:
        rows.append({
            "id": asset_id,
            "producer": "ACTORS" if asset_id.startswith(("attacker", "creature", "class")) else "ENVIRONMENT",
            "role": "blocker",
            "status": "FAIL" if asset_id != "class-healer-standing-body" else "BLOCKED",
            "sources": [],
            "output": None,
            "reusedFrom": None,
            "sourceToOutput": None,
            "intendedUse": "SPRITE",
            "maxDisplayCssPx": None,
            "limitBasis": "CONSERVATIVE_BOTH",
            "side": "UNKNOWN",
            "frame": "UNRESOLVED",
            "groundContact": None,
            "footprint": None,
            "entrance": None,
            "heightEnvelope": None,
            "transforms": {},
            "gates": {"binding": "FAIL", "semantics": "PARTIAL", "matte": "FAIL", "spatial": "NOT_APPLICABLE", "articulation": "NOT_APPLICABLE", "runtime": "UNVERIFIED", "owner": "UNVERIFIED"},
            "recipePath": None,
            "evidencePaths": [f"qa/image-unified-reserve-20261009/review/{asset_id}-pass3.jpg", f"qa/image-unified-reserve-20261009/review/{asset_id}-on-black.jpg", f"qa/image-unified-reserve-20261009/review/{asset_id}-pass4.jpg"],
            "limitations": [reason],
            "blockedBy": [reason],
            "nextAction": reason,
        })
    screens = [
        "home-chrome", "class-select-layout", "hero-hall-layout", "forge-layout", "inventory-layout",
        "market-layout", "story-layout", "quest-layout", "tutorial-layout", "battle-result-layout",
        "settings", "help", "credits", "privacy", "music-sfx-controls", "save-import-export",
    ]
    for asset_id in screens:
        rows.append({
            "id": asset_id,
            "producer": "ENVIRONMENT",
            "role": "supporting-screen",
            "status": "NO_NEW_IMAGE_NEEDED",
            "sources": [],
            "output": None,
            "reusedFrom": None,
            "sourceToOutput": None,
            "intendedUse": "CODE_NATIVE",
            "maxDisplayCssPx": None,
            "limitBasis": "HEIGHT",
            "side": "NOT_APPLICABLE",
            "frame": "UI",
            "groundContact": None,
            "footprint": None,
            "entrance": None,
            "heightEnvelope": None,
            "transforms": {},
            "gates": {"binding": "NOT_APPLICABLE", "semantics": "NOT_APPLICABLE", "matte": "NOT_APPLICABLE", "spatial": "NOT_APPLICABLE", "articulation": "NOT_APPLICABLE", "runtime": "UNVERIFIED", "owner": "UNVERIFIED"},
            "recipePath": None,
            "evidencePaths": [],
            "limitations": ["Layout, type, audio, and interaction stay with Code. The 30 landscape JPEGs are references, not screens."],
            "blockedBy": [],
            "nextAction": None,
        })
    return rows


def main():
    archive_info = archive_controls()
    record = release_ledger()
    snap = snapshot(archive_info)
    runner = c.Coordinator(
        QA / "vertex-coordinator",
        release=record,
        mutex_file=CONTROLS / "submission.mutex.json",
        pacing_file=CONTROLS / "pacing_state.json",
        cloud_lock_enabled=False,
    )
    runner.acquire_mutex()
    released = runner.release_mutex("RELEASED_NO_PAID_DISPATCH")
    scenes = json.loads((QA / "diagnostics/scenes.json").read_text(encoding="utf-8"))
    rows = rows_from_outputs()
    ready = [row["id"] for row in rows if row["status"] == "READY" and row.get("reusedFrom")]
    no_new = [row["id"] for row in rows if row["status"] == "NO_NEW_IMAGE_NEEDED"]
    outputs = list((ROOT / "assets/derivatives/image-unified-reserve-20261009").rglob("*.png"))
    healer_bound = c.estimate_upper_bound_usd("2K", 4, 900)
    runner_bound = c.estimate_upper_bound_usd("2K", 3, 700)
    cost = {
        "hardCapUSD": 80,
        "historicalProtectedUSD": 79.8327,
        "effectivePriorLiabilityUSD": 64.8327,
        "effectiveReserveUSD": 0,
        "newHoldsThisRunUSD": 0,
        "invoicedUSD": None,
        "remainingCapacityUSD": 15.1673,
        "pricing": {
            "source": "Vertex AI Gemini 3.1 Flash Image standard tier, image output $60/1M, 1680 tokens at 2K",
            "twoKFourImageWorstCaseUSD": healer_bound,
        },
        "notPurchased": [
            {"id": "class-healer-standing-body", "boundUSD": healer_bound, "reason": "Unattempted. Needs a wire that actually contains the head-card and boot images. Not sent."},
            {"id": "attacker-bronze-runner", "boundUSD": runner_bound, "reason": "HUD scene. No validated mask, so no request."},
            {"id": "attacker-medieval-archer", "boundUSD": runner_bound, "reason": "Damaged silhouette. No validated mask, so no request."},
            {"id": "kingdom-terrain-eight-ages", "boundUSD": None, "reason": "Stone local prototype does not satisfy legal roads. The free-layout method was not repeated and no kingdom image was purchased."},
        ],
    }
    write_json(QA / "cost-plan.json", cost)
    write_json(QA / "queue.json", {"generatedAt": NOW, "paidDispatch": "NONE", "rows": [
        {"id": row["id"], "status": row["status"], "nextAction": row["nextAction"]} for row in rows
    ]})
    write_json(QA / "scenes.json", scenes)
    coverage = {
        "newDerivativePngs": len(outputs),
        "bodyCandidatesAccepted": 7,
        "readyReuse": ready,
        "sceneRows": len(scenes),
        "sceneSpatialPass": 0,
        "kingdomAffine": [60, -10, 25, 35, 170, 165],
        "hallScale": 0.1312,
    }
    write_json(QA / "coverage.json", coverage)
    checkpoint = {
        "status": "INCOMPLETE",
        "completedIds": ready,
        "partialIds": [row["id"] for row in rows if row["status"] == "PARTIAL"],
        "failedIds": [row["id"] for row in rows if row["status"] == "FAIL"],
        "blockedIds": [row["id"] for row in rows if row["status"] == "BLOCKED"],
        "paidCompletedIds": [],
        "paidPendingIds": [],
        "retainedUnknownIds": [],
        "localProcessingComplete": False,
        "imageWorkComplete": False,
        "remainingLocalActions": [
            {"id": "creature-wolf", "action": "Remove paw pads and the ground rectangle without eating fur."},
            {"id": "creature-drone", "action": "Remove the purple slab and publish three timed frames only with source timing."},
            {"id": "attacker-stone-brute", "action": "Remove the club rim and foot rectangle without eating the club."},
            {"id": "workshop-iron", "action": "Fill the yard hole and remove the remaining inner lawn from the source, or keep the source and reject pass4."},
            {"id": "kingdom-terrain-all", "action": "Manual painted-road trace. Do not pay for another free-layout scene."},
            {"id": "class-rigs", "action": "No full gait exists. Do not promote standing bodies to rigs."},
        ],
        "remainingPaidActions": cost["notPurchased"],
        "scopeCoverage": [coverage],
        "budgetSnapshot": cost,
        "sourceHashes": {"inputSnapshot": "qa/image-unified-reserve-20261009/input_snapshot.json"},
        "evidencePaths": [
            "qa/image-unified-reserve-20261009/review/bodies-on-dark.jpg",
            "qa/image-unified-reserve-20261009/review/matte-before-after.jpg",
            "qa/image-unified-reserve-20261009/diagnostics/scenes.json",
        ],
        "nextExecutableActions": {
            "local": "Finish wolf, drone, brute, and workshop residuals before another paid call.",
            "paid": "Prepare one healer 2K wire with real inline images, then one POST if capacity still allows.",
        },
        "polishQueue": [],
        "authorityLimits": [
            "Hard cap remains 80.",
            "Reserve release was recorded once. Effective reserve is 0.",
            "No kingdom repurchase until a local prototype matches legal roads.",
            "Device remains STOPPED. Runtime and owner acceptance are separate.",
        ],
        "localCompletionReason": "Collected bodies were matted and many slabs were reduced, but visible residuals and all 32 scene rows remain unresolved.",
    }
    write_json(QA / "checkpoint.json", checkpoint)
    interface = {
        "schema": 3,
        "producer": "IMAGE_UNIFIED",
        "version": "image-unified-reserve-20261009",
        "authority": QUOTE,
        "inputSnapshot": {"path": "qa/image-unified-reserve-20261009/input_snapshot.json", "sha256": pl.sha256_file(QA / "input_snapshot.json"), "bytes": (QA / "input_snapshot.json").stat().st_size, "dimensions": None},
        "rows": rows,
        "scenes": scenes,
        "coverage": [coverage],
        "readySubset": ready,
        "noNewImageNeeded": no_new,
        "generationReceipts": [],
        "pendingPackIds": ["class-healer-standing-body"],
        "retainedUnknownIds": [],
        "budgetSnapshot": cost,
        "wholeDeliveryReady": False,
        "reviewGallery": "qa/image-unified-reserve-20261009/review/gallery.html",
        "checkpoint": "qa/image-unified-reserve-20261009/checkpoint.json",
        "codeDependencies": [
            {"id": "gear-stone-helm", "sourceToOutput": [1, 0, 0, 1, -82, -208], "groundContact": "NOT_APPLICABLE"},
            {"id": "troop-stone-melee", "sourceToOutput": [1, 0, 0, 1, -477, -112], "reuse": "assets/runtime-code-20261007/troops/troop-stone-melee.png"},
            {"id": "troop-industrial-ranged", "sourceToOutput": [1, 0, 0, 1, -526, -103]},
            {"id": "troop-industrial-heavy", "sourceToOutput": [1, 0, 0, 1, -233, -64]},
            {"id": "troop-stone-ranged", "sourceToOutput": [1, 0, 0, 1, -363, -79], "reuse": "assets/derivatives/image-vertex-repair-20261009/actors/troops/troop-stone-ranged.png"},
            {"id": "css-caps", "note": "Bronze heavy, gunpowder heavy, future ranged, future heavy, mounts, gear, artifacts, and effects stay at a 64 CSS longest-side cap. Ordinary static ceiling is 130. Do not shrink the raster in Image."},
            {"id": "kingdom-camera", "affine": [60, -10, 25, 35, 170, 165], "hallScale": 0.1312},
            {"id": "drone", "note": "Not one sprite. Three poses are visible. Timing is blocked."},
        ],
    }
    write_json(ROOT / "docs/plan/IMAGE-UNIFIED-RESERVE-INTERFACE-2026-10-09.json", interface)
    write_json(QA / "coverage.json", coverage)
    gallery = QA / "review/gallery.html"
    gallery.write_text(
        """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>Unified reserve review</title>
<style>body{font-family:Georgia,serif;background:#1b1b1b;color:#f3efe6;margin:24px} img{max-width:100%;background:#111} figure{margin:0 0 28px}</style>
</head><body>
<h1>Ages of Dominion Reborn — image review composites</h1>
<p>These frames are ASSET_COMPOSITE comparisons. They are not gameplay, not a device build, and not owner acceptance.</p>
<figure><img src="bodies-on-dark.jpg" alt="Seven standing bodies on a dark field"><figcaption>Collected standing bodies after the white or gray matte.</figcaption></figure>
<figure><img src="matte-before-after.jpg" alt="Before and after matte samples"><figcaption>Attacker, creature, and building samples. Green yards and magenta markers that remain are failures.</figcaption></figure>
<figure><img src="armory-stone-pass2.jpg" alt="Armory after green-base removal"><figcaption>Armory stone. Outer green slab reduced. Fringe can remain.</figcaption></figure>
<figure><img src="workshop-iron-pass4.jpg" alt="Workshop after pale-green removal"><figcaption>Workshop iron. Building kept. Inner lawn and a yard hole remain.</figcaption></figure>
</body></html>
""",
        encoding="utf-8",
    )
    handoff = QA / "handoff.md"
    handoff.write_text(
        f"""# Image handoff — unified reserve — {NOW}

Language/framework: JavaScript ES modules game, Python 3.13.7 image tools. This file is the Image handoff. It does not integrate Code.

## Budget

Owner quote recorded once: "{QUOTE}"

Historical safety reserve 15 and historical protected exposure 79.8327 are unchanged. Effective reserve is 0. Prior liability excluding that reserve is 64.8327. Remaining capacity under 80 is 15.1673. This run reserved 0 and spent 0. Invoices remain UNKNOWN.

## What Code can bind

READY reuse, bytes untouched:

- `assets/runtime-code-20261007/troops/troop-stone-melee.png` translation [-477, -112]
- `assets/runtime-code-20261007/troops/troop-industrial-ranged.png` translation [-526, -103]
- `assets/runtime-code-20261007/troops/troop-industrial-heavy.png` translation [-233, -64]
- `assets/derivatives/image-vertex-repair-20261009/actors/troops/troop-stone-ranged.png` translation [-363, -79]
- `assets/derivatives/rigs/v7/healer/boot.png` 135×131

`gear-stone-helm` crop affine is [1, 0, 0, 1, -82, -208]. Gear and icon ground contact is NOT_APPLICABLE.

New derivatives under `assets/derivatives/image-unified-reserve-20261009/` are partial plates. Do not treat them as full rigs or as scene clearance.

## Do not bind as finished

- Kingdom, adventure, tactical, and defense terrain. Spatial gate is FAIL. Affine [60, -10, 25, 35, 170, 165] and Hall scale 0.1312 stay frozen.
- Bronze runner and medieval archer.
- Drone sheet, wolf pads, brute club rim.
- Healer standing body. It was not generated.
- Any row whose producer label was READY solely in an older interface.

CSS: capped roles use 64 on the longest visible side. Ordinary static ceiling is 130. Measure alpha bounds, not transparent padding.

Runtime, owner acceptance, and the device stay separate. The device stays STOPPED. `imageWorkComplete` is false. `wholeDeliveryReady` is false.

Gallery: `qa/image-unified-reserve-20261009/review/gallery.html`
Interface: `docs/plan/IMAGE-UNIFIED-RESERVE-INTERFACE-2026-10-09.json`
Checkpoint: `qa/image-unified-reserve-20261009/checkpoint.json`
""",
        encoding="utf-8",
    )
    print(json.dumps({
        "mutexReleased": released,
        "ready": ready,
        "outputs": len(outputs),
        "scenes": len(scenes),
        "newHolds": 0,
        "remainingCapacityUSD": 15.1673,
        "snapshotFiles": len(snap["files"]),
    }, indent=2))


if __name__ == "__main__":
    main()
