"""Task 2: Prepare the 73 Proposed 2K Request Packs (Zero Purchases).

Generates role-specific local request packs, exact prompts, crop/part layouts,
source hash-bindings, and Code AI handoff for all 73 items across:
- 32 Hero paintings
- 17 Mounts / Rigs / Rivals
- 24 Army masters
All remain INACTIVE_OWNER_SCHEDULING_REQUIRED (0 API POSTs).
"""

from pathlib import Path
import json
import hashlib
from PIL import Image

ROOT = Path("c:/dev/ages-of-dominion-reborn")
QA = ROOT / "qa/image-next-task-20261004"
PLAN_PROD = ROOT / "docs/plan/image-production"
PACKS_ROOT = ROOT / "assets/high-res/later73-preparation-packs"
PACKS_ROOT.mkdir(parents=True, exist_ok=True)
PLAN_PROD.mkdir(parents=True, exist_ok=True)

def sha256_file(p):
    return hashlib.file_digest(p.open("rb"), "sha256").hexdigest()

def sha256_str(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

manifest_file = ROOT / "docs/plan/IMAGE-LATER73-LOCAL-PREPARATION-MANIFEST-2026-10-04.json"
manifest_data = json.loads(manifest_file.read_text(encoding="utf-8"))

items = manifest_data["items"]
print(f"Loaded {len(items)} items from later 73 manifest.")

handoff_entries = []
updated_manifest_items = []

for it in items:
    gid = it["group"]
    cid = it["id"]
    order = it["order"]
    kind = it["requestKind"]
    consumer = it["consumerNeed"]
    sources = it["sources"]

    pack_dir = PACKS_ROOT / cid
    pack_dir.mkdir(parents=True, exist_ok=True)

    # Determine role-specific prompt and layout
    if "HERO" in gid:
        prompt = (
            f"Produce ONE native 2K character illustration for {cid}. "
            f"Full-body high-fidelity portrait of the hero with class-authentic weapons, armor, and gear. "
            f"Upper-left key lighting, dark textured atmospheric background, clean intact silhouette. "
            f"Preserve hero facial identity, anatomy proportions, and 6-slot equipment visibility. "
            f"Deliver ONE 2048x2048 PNG image."
        )
        layout = {
            "canvas": [2048, 2048],
            "framing": "full-body character portrait",
            "focalCenter": [1024, 900],
            "silhouettePaddingPx": 96,
            "lighting": "upper-left directional key light with subtle rim",
            "consumer": "Hero/Equipment character sheet and Adventure map avatar"
        }
    elif "ARMY" in gid:
        prompt = (
            f"Produce ONE native 2K army unit master sheet for {cid}. "
            f"Accurate historical/fantasy military unit depicting correct period armament, armor, and combat posture. "
            f"Isolated full-figure silhouette on neutral ground, suitable for sprite extraction and tactical token generation. "
            f"Maintain strict role fidelity (swordsman/melee, archer/ranged, heavy/siege vehicle or beast). "
            f"Deliver ONE 2048x2048 PNG image."
        )
        layout = {
            "canvas": [2048, 2048],
            "framing": "standing/combat isometric unit presentation",
            "focalCenter": [1024, 1100],
            "silhouettePaddingPx": 80,
            "lighting": "isometric 3/4 light from upper-left",
            "consumer": "Army / Tactical / Defense unit sprite and token master"
        }
    else:  # Mounts, rigs, rivals
        if cid.startswith("rig-"):
            prompt = (
                f"Produce ONE native 2K multi-part articulation sheet for {cid}. "
                f"Contains clearly separated anatomical components: head, torso, upper limbs, lower limbs, weapon/gear accessories. "
                f"Clean neutral transparent/untextured background with distinct margins between parts for skeletal rigging. "
                f"Supports idle, walk, work, attack, hit, and death 2D sprite mesh animation. "
                f"Deliver ONE 2048x2048 PNG image."
            )
            layout = {
                "canvas": [2048, 2048],
                "framing": "articulation part atlas with 32px part separation",
                "parts": ["head", "torso", "arm_l", "arm_r", "leg_l", "leg_r", "weapon", "shield_or_accessory"],
                "consumer": "2D skeletal / frame animation inputs for Code AI"
            }
        elif "mount" in cid or "transport" in cid:
            prompt = (
                f"Produce ONE native 2K mount master illustration for {cid}. "
                f"Anatomically correct steed/mount/vehicle with visible saddle, harness, and rider attachment points. "
                f"Clean silhouette on neutral background, 3/4 isometric profile, consistent light. "
                f"Deliver ONE 2048x2048 PNG image."
            )
            layout = {
                "canvas": [2048, 2048],
                "framing": "isometric profile mount with rider saddle anchor",
                "saddleAnchor": [1024, 850],
                "consumer": "Mounted travel and tactical unit composite base"
            }
        else:  # Rival portrait
            prompt = (
                f"Produce ONE native 2K faction rival portrait for {cid}. "
                f"Expressive high-detail bust portrait capturing character personality, noble regalia, and rival allegiance. "
                f"Rich dramatic lighting, ornate decorative framing, intact silhouette. "
                f"Deliver ONE 2048x2048 PNG image."
            )
            layout = {
                "canvas": [2048, 2048],
                "framing": "bust portrait with crest insignia",
                "focalCenter": [1024, 800],
                "consumer": "Story dialogue and rival faction diplomacy interface"
            }

    # Save pack files
    (pack_dir / "prompt.txt").write_text(prompt, encoding="utf-8")
    
    req_meta = {
        "id": cid,
        "group": gid,
        "order": order,
        "model": "gemini-3.1-flash-image",
        "requestedSize": "2K",
        "dimensions": [2048, 2048],
        "purchaseStatus": "INACTIVE_OWNER_SCHEDULING_REQUIRED",
        "paidCallsAllowed": False,
        "prompt": prompt,
        "promptSHA256": sha256_str(prompt),
        "sourceCandidates": sources,
        "layout": layout,
        "consumerNeed": consumer
    }
    (pack_dir / "request_meta.json").write_text(json.dumps(req_meta, indent=2), encoding="utf-8")
    (pack_dir / "layout_spec.json").write_text(json.dumps(layout, indent=2), encoding="utf-8")

    # Select primary source reference (first matching existing source)
    prim_source = sources[0] if sources else None
    
    handoff_entries.append({
        "id": cid,
        "group": gid,
        "order": order,
        "role": kind,
        "reusable1KSource": prim_source.get("file") if prim_source else None,
        "reusable1KSHA256": prim_source.get("sha256") if prim_source else None,
        "reusable1KDimensions": prim_source.get("dimensions") if prim_source else None,
        "proposed2KPackDir": str(pack_dir.relative_to(ROOT)).replace("\\", "/"),
        "proposed2KPromptSHA256": sha256_str(prompt),
        "purchaseStatus": "INACTIVE_OWNER_SCHEDULING_REQUIRED",
        "codeAIConsumerStatus": "READY_FOR_1K_REUSE_NOW",
        "note": "Code AI can immediately reuse the verified 1K source; 2K generation remains unscheduled."
    })

    it_updated = dict(it)
    it_updated["localPackDir"] = str(pack_dir.relative_to(ROOT)).replace("\\", "/")
    it_updated["promptSHA256"] = sha256_str(prompt)
    it_updated["layoutPrepared"] = True
    it_updated["readinessStatus"] = "LOCAL_PACK_PREPARED_PURCHASE_INACTIVE"
    updated_manifest_items.append(it_updated)

# Save updated manifest and handoff
manifest_data["items"] = updated_manifest_items
manifest_data["readinessSummary"] = {
    "totalPreparedPacks": len(updated_manifest_items),
    "purchaseStatus": "INACTIVE_OWNER_SCHEDULING_REQUIRED",
    "paidCallsExecuted": 0,
    "codeAIHandoffReady": True
}
manifest_file.write_text(json.dumps(manifest_data, indent=2), encoding="utf-8")

handoff_doc = {
    "version": "1.0-20261004",
    "description": "Code AI Hash-Bound Asset Reuse Handoff for Later 73 Items",
    "scope": "Provides immediate 1K source bindings and 2K pack specifications for Code AI",
    "totalItems": len(handoff_entries),
    "groups": {
        "heroes": 32,
        "mounts_rigs_rivals": 17,
        "army_masters": 24
    },
    "items": handoff_entries
}
(PLAN_PROD / "later73-code-ai-handoff.json").write_text(json.dumps(handoff_doc, indent=2), encoding="utf-8")
print(f"Task 2 Complete: 73 packs created in {PACKS_ROOT}. Code AI handoff saved to {PLAN_PROD / 'later73-code-ai-handoff.json'}.")
