"""Publish the v7 delivery interface from measured local evidence. No provider calls."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / "qa" / "image-local-continuation-20261005"

# filename -> semantic, status, note. Side stays UNKNOWN. Joints were not run on these crops.
CLASS_NOTES = {
    "mage/01_1221_92.png": ("torso_and_pelvis", "WITHHELD", "Painted TORSO and PELVIS labels with leader lines are attached. Not promoted."),
    "mage/02_119_545.png": ("head_hood", "PARTIAL", "One hooded head. Side UNKNOWN. No joint."),
    "mage/03_595_548.png": ("head_hood", "PARTIAL", "One hooded head, eyes closed. Side UNKNOWN."),
    "mage/04_585_86.png": ("head_hood", "PARTIAL", "One hooded head, mouth open. Side UNKNOWN."),
    "mage/05_116_83.png": ("head_hood", "PARTIAL", "One hooded head. Side UNKNOWN."),
    "mage/06_977_1402.png": ("book", "PARTIAL", "Closed book. Not a body part."),
    "mage/07_162_1799.png": ("staff", "PARTIAL", "Thin staff. No hand on this crop."),
    "mage/16_1619_1753.png": ("boot", "PARTIAL", "One boot. Side UNKNOWN."),
    "mage/19_1319_1789.png": ("boot_top", "PARTIAL", "Boot seen from above. Side UNKNOWN."),
    "mage/17_591_1124.png": ("hand", "PARTIAL", "Open hand with rings. Side UNKNOWN. Do not duplicate into a rig."),
    "mage/18_430_1654.png": ("hand", "PARTIAL", "Open hand with rings. Side UNKNOWN."),
    "mage/20_708_1499.png": ("hand", "PARTIAL", "Open hand with rings. Side UNKNOWN."),
    "mage/21_792_1136.png": ("skeletal_hand", "WITHHELD", "Skeleton hand is not identified as the mage's painted hand."),
    "warlock/01_1042_107.png": ("torso_group", "PARTIAL", "Cuirass and fauld in one component. Not split."),
    "warlock/02_80_86.png": ("head_grid", "WITHHELD", "Several heads share the crop and the sheet carries head labels."),
    "warlock/03_1087_1087.png": ("leg_group", "PARTIAL", "Both legs, boots, and soles are one component. Sides not separated."),
    "warlock/04_48_824.png": ("arm_weapon_group", "PARTIAL", "Arms, hands, staff, and book share one component."),
    "warlock/05_483_1629.png": ("offhand_group", "PARTIAL", "Book and satchel share one component."),
    "warlock/06_579_1985.png": ("sheet_label", "WITHHELD", "Text label, not anatomy."),
    "warlock/07_1618_1902.png": ("sheet_label", "WITHHELD", "Text label, not anatomy."),
    "warlock/08_192_1985.png": ("sheet_label", "WITHHELD", "Text label, not anatomy."),
    "warlock/09_1432_973.png": ("sheet_label", "WITHHELD", "The crop is the painted text TORSO_MAIN."),
    "warlock/10_264_973.png": ("sheet_label", "WITHHELD", "Text label, not anatomy."),
    "warlock/11_1266_1902.png": ("sheet_label", "WITHHELD", "Text label, not anatomy."),
    "necromancer/01_1082_92.png": ("torso_arm_group", "PARTIAL", "Torso and both arms are one component."),
    "necromancer/02_527_1082.png": ("staff_arm_group", "PARTIAL", "Arms and staff share one component."),
    "necromancer/03_549_62.png": ("skull_group", "PARTIAL", "Several skulls share one component."),
    "necromancer/04_1710_87.png": ("pelvis_tasset", "PARTIAL", "Pelvis and tassets. Side UNKNOWN."),
    "necromancer/05_60_1569.png": ("satchel", "PARTIAL", "Satchel. Not a limb."),
    "necromancer/10_391_51.png": ("hand_skull_group", "PARTIAL", "Hand and skull share one component."),
    "necromancer/11_57_371.png": ("arm", "PARTIAL", "One armored arm and hand. Side UNKNOWN."),
    "necromancer/13_56_47.png": ("head_hooded_skull", "PARTIAL", "One hooded skull. Facing is not an anatomical side proof."),
    "necromancer/14_276_1104.png": ("boot", "PARTIAL", "One boot. Side UNKNOWN."),
    "necromancer/15_1655_1898.png": ("sole", "PARTIAL", "Boot sole."),
    "necromancer/16_1190_1901.png": ("sole", "PARTIAL", "Boot sole."),
    "barbarian/01_1110_80.png": ("torso_skirt_group", "PARTIAL", "Torso and skirt share one component."),
    "barbarian/02_1502_0.png": ("vest", "PARTIAL", "Vest crop still contains magenta background. Not a clean matte."),
    "barbarian/03_1086_1492.png": ("boot_group", "PARTIAL", "Three boots share one component. Not separated."),
    "barbarian/04_1583_501.png": ("skirt", "PARTIAL", "Fur-trimmed skirt."),
    "barbarian/09_400_1723.png": ("axe", "PARTIAL", "Axe with a partial hand. Not a full arm."),
    "barbarian/13_1744_1853.png": ("shoe", "PARTIAL", "One shoe. Side UNKNOWN."),
    "barbarian/26_671_1906.png": ("dagger", "PARTIAL", "Dagger. No hand."),
}


def rel(path: str) -> str:
    return path.replace("\\", "/")


def main() -> None:
    measured = json.loads((QA / "measurements.json").read_text(encoding="utf-8"))
    summary = json.loads((QA / "components" / "summary.json").read_text(encoding="utf-8"))
    boot = json.loads((QA / "recipes" / "healer-boot.json").read_text(encoding="utf-8"))
    draft = json.loads((ROOT / "docs/plan/REPLACEMENT-DRAFT-THREE-ROLES-V6-CLARIFICATION-2026-10-04.json").read_text(encoding="utf-8"))
    mappings = json.loads((ROOT / "qa/image-local-solution-20261004/healer-semantic-mappings-v6.json").read_text(encoding="utf-8"))

    class_rows = []
    for class_id, items in summary.items():
        for item in items:
            path = rel(item["path"])
            key = path.split("components/", 1)[1]
            semantic, status, note = CLASS_NOTES.get(key, ("unseparated_part", "PARTIAL", "Single connected component. Anatomical side UNKNOWN. Not assembled."))
            class_rows.append({
                "id": f"{class_id}-{key.replace('/', '-').replace('.png', '')}",
                "classId": class_id,
                "status": status,
                "semantic": semantic,
                "side": "UNKNOWN",
                "path": path,
                "sha256": item["sha256"],
                "dimensions": item["size"],
                "crop": item["crop"],
                "source": f"assets/high-res/final-native2k/rig-source-parts-{class_id}.png",
                "joints": "NOT_RUN",
                "neutralAssembly": False,
                "note": note,
                "display": "native crop only; not accepted at 50, 64, 130, or full body",
            })
    (QA / "class-semantics.json").write_text(json.dumps(class_rows, indent=2), encoding="utf-8")

    scenes = []
    for scene in measured["scenes"]:
        spec = scene.get("spec") or ""
        blues = len(scene.get("riverCandidates") or [])
        if "snow" in scene["id"] or "snow" in spec:
            blue_note = "Blue components follow snow and ice. They are not rivers."
        elif blues > 15:
            blue_note = "Scattered blue components were not accepted as rivers."
        elif blues == 0:
            blue_note = "No blue component passed the size cutoff."
        else:
            blue_note = "Blue components are color candidates. Banks were not traced."
        baked = sum(1 for site in scene.get("sites") or [] if site.get("bakedMutableCandidate"))
        row = {
            "id": scene["id"],
            "status": "PARTIAL",
            "promoted": False,
            "path": scene.get("path"),
            "sha256": scene.get("sha256"),
            "dimensions": scene.get("dimensions"),
            "legalAffine": scene.get("legalAffine"),
            "roads": "Legal centerlines are in the measurement file. Painted separation was not asserted from color.",
            "roadCount": len(scene.get("roads") or []),
            "bridges": [b.get("id") for b in scene.get("bridges") or []],
            "blockedCellCount": len(scene.get("blockedPolygons") or []),
            "blueCandidateCount": blues,
            "blueNote": blue_note,
            "bakedSiteCandidates": baked,
            "bakedConflict": scene.get("bakedConflict"),
            "proposal": scene.get("proposal"),
            "overlay": f"qa/image-local-continuation-20261005/terrain/{scene['id']}-legal-overlay.png",
            "runtimeAcceptance": "UNVERIFIED",
            "ownerAcceptance": "UNVERIFIED",
        }
        if scene["id"] == "kingdom-terrain-stone":
            row["visualInspection"] = (
                "The painted plate has curving dirt tracks, a rock ring, a river on the right with banks, and a wooden bridge. "
                "The legal road centerline runs straight through the ring and does not follow the tracks. "
                "The legal bridge rectangle sits by the bank rather than on the painted deck. "
                "Baked rocks and a hut conflict with Day-1 empty pads. Affine and Hall scale were not changed."
            )
        scenes.append(row)
    (QA / "scene-survey-summary.json").write_text(json.dumps(scenes, indent=2), encoding="utf-8")

    def joint_row(pair_name, semantic):
        row = next(j for j in measured["joints"] if j["pair"] == pair_name)
        return {
            "id": pair_name.replace("_", "-"),
            "status": "READY" if row["status"] == "PASS_STATIC_AND_LIMITED_ARC" else "FAIL",
            "measuredStatus": row["status"],
            "semantic": semantic,
            "side": "UNKNOWN",
            "parent": row.get("parent"),
            "parentSha256": row.get("parentSha256"),
            "child": row.get("child"),
            "childSha256": row.get("childSha256"),
            "angles": row.get("anglesTested"),
            "insertionOfCuff": row.get("insertionOfCuff"),
            "transverseOfCuff": row.get("transverseOfCuff"),
            "uniformScale": row.get("uniformScale"),
            "ratio": row.get("ratio"),
            "poses": row.get("poses"),
            "displaySizes": [50, 64, 130],
            "fullBody": False,
            "limit": "These three angles only. Not a whole rig. Side UNKNOWN.",
        }

    ready = []
    for row in measured["keepSet"]:
        ready.append({
            "id": Path(row["path"]).stem,
            "status": "READY",
            "use": "static plate to 130px",
            "path": row["path"],
            "sha256": row["sha256"],
            "dimensions": row["dimensions"],
            "visibleAlpha16": row["visibleAlpha16"],
            "visibleAlpha128": row["visibleAlpha128"],
            "contacts": row["contacts"],
            "semantic": "retained static troop",
            "side": "UNKNOWN",
            "rig": "NOT_A_RIG",
            "recreated": False,
            "diagnostics": row["diagnostics"],
            "limit": "Prior static acceptance at 130px. Not an articulated body. Owner acceptance remains unverified.",
        })
    ranger = measured["rangerConfirm"]
    ready.append({
        "id": "ranger-sleeve-to-open-hand",
        "status": "READY",
        "use": "articulation only at -25, 0 and +25 degrees",
        "semantic": "sleeve_to_vambrace",
        "side": "UNKNOWN",
        "parent": ranger["parent"],
        "parentSha256": ranger["parentSha256"],
        "child": ranger["child"],
        "childSha256": ranger["childSha256"],
        "placement": {"insertionOfCuff": 0.30, "transverseOfCuff": 0.05, "uniformScale": 1},
        "poses": ranger["poses"],
        "vambraceInteriorHoles16": ranger["vambraceInteriorHoles16"],
        "priorEvidence": ranger["priorEvidence"],
        "limit": "Recorded placement remeasured once. The 12-placement search was not rerun. Not a whole rig or an arbitrary angle.",
    })
    ready.append({
        "id": "healer-boot",
        "status": "READY",
        "semantic": "boot",
        "side": "UNKNOWN",
        "path": boot["derivative"],
        "sha256": boot["sha256"],
        "dimensions": boot["dimensions"],
        "visibleAlpha16": boot["visibleAlpha16"],
        "visibleAlpha128": boot["visibleAlpha128"],
        "source": boot["source"],
        "sourceSha256": boot["sourceSha256"],
        "mask": boot["mask"],
        "recipe": "qa/image-local-continuation-20261005/recipes/healer-boot.json",
        "removedNeighborPixels": boot["removed"][0]["pixels"],
        "displaySizes": [50, 64, 130],
        "limit": "Disconnected neighboring armor was removed. The largest boot component was not edited. Not a leg rig by itself.",
    })
    ready.append(joint_row("healer_leg_greave", "upper_leg_to_greave"))
    ready.append(joint_row("healer_greave_boot", "greave_to_boot"))
    ready.append(joint_row("paladin_knee_greave", "knee_cop_to_greave"))

    interface = {
        "version": "7.0-local-continuation-20261005",
        "supersedes": "docs/plan/IMAGE-DELIVERY-INTERFACE-V6-2026-10-04.json",
        "codeAIHandoffReady": False,
        "reason": "Ready rows can be consumed one at a time. Whole delivery is false: Industrial melee coat holes, Modern heavy slab, Modern ranged snow, Knight seam, Paladin head, Mage labels, unseparated class groups, and unpromoted terrain remain.",
        "noNewPaidScope": True,
        "providerCalls": 0,
        "python": measured["python"],
        "libraries": measured["libraries"],
        "accounting": {"protectedExposureUSD": 70.7012, "unknownLiabilitiesUSD": 0.287224, "invoices": "UNKNOWN"},
        "checkpoint": "qa/image-local-continuation-20261005/checkpoint.json",
        "measurements": "qa/image-local-continuation-20261005/measurements.json",
        "preserved": {"v4": "unchanged", "v5": "unchanged", "v6": "unchanged", "natives": "unchanged", "inputHashesChanged": measured["inputHashesChanged"]},
        "codeConsumersEdited": False,
        "runtimeRangerBinding": "assets/derivatives/rigs/v3/ranger",
        "sizeContract": {
            "troopStaticPlateHeightPx": 130,
            "transportCapPx": 64,
            "doNotExtend64AcceptanceTo130": ["hero-mount-motor-transport", "hero-mount-future-transport", "hero-mount-horse", "troop-future-heavy", "troop-gunpowder-heavy", "troop-future-ranged"],
        },
        "readySubset": ready,
        "partial": [
            {
                "id": "troop-industrial-melee",
                "status": "PARTIAL",
                "path": "assets/derivatives/actors/v6/troop-industrial-melee.png",
                "sha256": measured["industrial"]["hashes"]["v6"],
                "nativeSha256": measured["industrial"]["hashes"]["native"],
                "v4Sha256": measured["industrial"]["hashes"]["v4"],
                "v5Sha256": measured["industrial"]["hashes"]["v5"],
                "interiorHoles16": measured["industrial"]["v6InteriorHoles16"],
                "holePreview": "qa/image-local-continuation-20261005/diagnostics/industrial-melee-v6-holes-640.png",
                "nativeMatte": "WITHDRAWN",
                "use130": "WITHDRAWN",
                "use64": "NOT_CLEAN",
                "decision": measured["industrial"]["decision"],
                "correction": None,
                "limit": "Coat hole and the gap between coat and boots are visible on white. v5 has no dark foreground pixels left to restore there. Filling them would invent paint.",
            },
            {
                "id": "troop-modern-heavy",
                "status": "PARTIAL",
                "path": measured["modernHeavy"]["path"],
                "sha256": measured["modernHeavy"]["sha256"],
                "dimensions": measured["modernHeavy"]["dimensions"],
                "visibleAlpha16": measured["modernHeavy"]["visibleAlpha16"],
                "groundSlab": "REMAINS",
                "limit": "Helmet halo stays cleared. Slab and track contact remain. v4 retained.",
            },
            {
                "id": "troop-modern-ranged",
                "status": "PARTIAL",
                "path": measured["modernRanged"]["path"],
                "sha256": measured["modernRanged"]["sha256"],
                "role": "SNOW_SCENE_ILLUSTRATION",
                "generalSprite": "FAIL",
                "limit": "Mound trim does not make a clean actor. Snow, bipod, and the prone body stay.",
            },
            {
                "id": "troop-bronze-heavy",
                "status": "PARTIAL",
                "role": "CHARIOTEER",
                "path": "assets/derivatives/actors/v4/troop-bronze-heavy.png",
                "logicalUnit": "crew, horses, and vehicle",
                "inReplacementDraft": False,
            },
            {"id": "healer-remaining-parts", "status": "PARTIAL", "parts": "assets/derivatives/rigs/v6/healer", "mappings": "qa/image-local-solution-20261004/healer-semantic-mappings-v6.json", "side": "UNKNOWN", "limit": "Boot neighbor is cleaned in v7. Other parts were not reassembled into a body. Old arm_upper_left remains waist armor. Old boot_leg files remain upper-leg armor."},
            {"id": "paladin-remaining-parts", "status": "PARTIAL", "parts": "assets/derivatives/rigs/v6/paladin", "side": "UNKNOWN", "mirror": False, "head": "NOT_REPAIRED"},
            {"id": "class-sheets", "status": "PARTIAL", "rows": "qa/image-local-continuation-20261005/class-semantics.json", "missingPriorCrops": "qa/image-local-solution-20261004/components had JSON boxes and no PNGs. Recut from native sheets. This is a missing transfer of the old crops, not a failed generation."},
        ],
        "incomplete": [
            {"id": "troop-medieval-melee", "status": "FAIL", "retained": "assets/derivatives/actors/v5/troop-medieval-melee.png", "attempts": 2, "next": "stop"},
            {"id": "knight-thigh-greave", "status": "FAIL", "attempts": "12 placements plus one 0.45 cuff correction", "next": "stop", "evidence": "qa/image-local-solution-20261004/joints/knight_thigh_greave_correction_0.png"},
            {"id": "paladin-head_three_quarter", "status": "FAIL", "retained": "assets/derivatives/rigs/v6/paladin/head_three_quarter.png", "attempt": "Upward connected paint included a neighboring curved rim. The v7 file was deleted. Four magenta fringe pixels were not a defensible mask. Pink skin rim was left."},
            {"id": "paladin-thigh-knee", "status": "FAIL", "reason": "Cuff width ratio 1.43. Scale stayed 1. No stretch."},
            {"id": "paladin-greave-boot", "status": "FAIL", "reason": "Cuff width ratio 0.73. Scale stayed 1. No stretch."},
            {"id": "troop-stone-melee", "status": "BLOCKED", "role": "Clubman"},
            {"id": "troop-stone-ranged", "status": "BLOCKED", "role": "Slinger"},
            {"id": "troop-industrial-ranged", "status": "BLOCKED", "role": "Sharpshooter", "pose": "standing anatomy absent from the prone sheet"},
            {"id": "mage-torso", "status": "WITHHELD", "path": "qa/image-local-continuation-20261005/components/mage/01_1221_92.png"},
        ],
        "terrain": {
            "survey": "qa/image-local-continuation-20261005/scene-survey-summary.json",
            "detail": "qa/image-local-continuation-20261005/measurements.json",
            "activeKingdomAffine": [60, -10, 25, 35, 170, 165],
            "hallScale": 0.1312,
            "promoted": False,
            "sceneCount": len(scenes),
        },
        "replacementDraft": {
            "path": "docs/plan/REPLACEMENT-DRAFT-THREE-ROLES-V6-CLARIFICATION-2026-10-04.json",
            "status": draft["status"],
            "authorization": draft["authorization"],
            "primaryIds": draft["primaryIds"],
            "edited": False,
        },
        "healerMappingsPreserved": mappings["corrections"],
        "smallStatic": measured["smallStatic"],
        "runtimeAcceptance": "UNVERIFIED",
        "ownerAcceptance": "UNVERIFIED",
        "device": "STOPPED",
    }
    out = ROOT / "docs/plan/IMAGE-DELIVERY-INTERFACE-V7-2026-10-05.json"
    out.write_text(json.dumps(interface, indent=2), encoding="utf-8")
    checkpoint = {
        "updated": "2026-10-05",
        "providerCalls": 0,
        "codeAIHandoffReady": False,
        "python": "3.13.7",
        "inputHashesChanged": [],
        "items": [
            {"id": "keep-set", "state": "reused", "attempts": 0, "next": "none"},
            {"id": "troop-industrial-melee", "state": "partial", "attempts": 1, "next": "stop", "reason": "No restorable dark coat pixels in v5. Native-matte and 130px claim withdrawn."},
            {"id": "troop-modern-heavy", "state": "partial", "attempts": 0, "next": "stop"},
            {"id": "troop-modern-ranged", "state": "partial", "attempts": 0, "next": "stop"},
            {"id": "healer-boot", "state": "complete", "attempts": 1, "next": "none", "output": boot["derivative"]},
            {"id": "healer-leg-greave", "state": "complete", "attempts": 1, "next": "none", "angles": [-25, 0, 25]},
            {"id": "healer-greave-boot", "state": "complete", "attempts": 1, "next": "none", "angles": [-25, 0, 25]},
            {"id": "paladin-knee-greave", "state": "complete", "attempts": 1, "next": "none", "angles": [-25, 0, 25]},
            {"id": "paladin-head", "state": "failed", "attempts": 1, "next": "stop", "reason": "Neighbor rim came in with the upward component. Derivative deleted."},
            {"id": "paladin-thigh-knee", "state": "failed", "attempts": 1, "next": "stop"},
            {"id": "paladin-greave-boot", "state": "failed", "attempts": 1, "next": "stop"},
            {"id": "knight-thigh-greave", "state": "failed", "attempts": 13, "next": "stop"},
            {"id": "class-sheets", "state": "partial", "attempts": 1, "next": "stop", "reason": "Separable crops named. Labels and multi-part groups withheld. No neutral body."},
            {"id": "terrain", "state": "partial", "attempts": 1, "next": "stop", "reason": "32 plates surveyed. Stone legal road and bridge do not match painted geography. Nothing promoted."},
            {"id": "three-role-draft", "state": "blocked", "attempts": 0, "next": "owner authorization", "status": draft["status"]},
        ],
    }
    (QA / "checkpoint.json").write_text(json.dumps(checkpoint, indent=2), encoding="utf-8")
    print("interface", out)
    print("ready", len(ready), "class", len(class_rows), "scenes", len(scenes), "draft", draft["status"])


if __name__ == "__main__":
    main()
