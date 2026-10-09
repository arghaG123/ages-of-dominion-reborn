"""Serve the published actor ready-index, then resume the retained medieval body.

Reads AI2 packs. Writes only the environment coordinator namespace, the shared
mutex, lock, pacing file, and budget ledger. Does not edit AI2 directories.
Stops before any new reservation that would pass US$80. The medieval resume
reuses the existing 0.4931 reservation and does not add another one.
"""
from __future__ import annotations

import base64
import json
import os
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import coordinator as coord
import dispatch_kingdom as kingdom

ROOT = kingdom.ROOT
QA = kingdom.QA
SHARED = kingdom.SHARED
INTERFACE = kingdom.INTERFACE
BASELINE = kingdom.BASELINE
HARD = kingdom.HARD
ACTOR_INDEX = ROOT / "qa" / "image-vertex-repair-20261009" / "actors" / "regeneration" / "ready-index.json"
RESULT_PATH = QA / "vertex-coordinator" / "actor-wave-result.json"
MEDIEVAL_ATTEMPT = "env-kingdom-terrain-medieval-v2-a1"
MEDIEVAL_PACK = QA / "regeneration" / "packs" / "env-kingdom-terrain-medieval-v2.json"


def append_ledger(attempt: dict) -> None:
    ledger_path = SHARED / "budget-ledger.json"
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    section = ledger["vertexRepair20261009"]
    section["attempts"].append(attempt)
    retained = sum(row["reservedUSD"] for row in section["attempts"] if row.get("retained"))
    section["addedRetainedUSD"] = round(retained, 4)
    section["currentCommittedProtectedUSD"] = round(BASELINE + retained, 4)
    kingdom.write_json(ledger_path, ledger)


def update_ledger_status(attempt_id: str, status: str) -> None:
    ledger_path = SHARED / "budget-ledger.json"
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    for row in ledger["vertexRepair20261009"]["attempts"]:
        if row["attemptId"] == attempt_id:
            row["status"] = status
            row["updatedAt"] = kingdom.now()
            break
    kingdom.write_json(ledger_path, ledger)


def pin_actors() -> list[dict]:
    if not ACTOR_INDEX.exists():
        raise coord.BudgetError("Actor ready-index is absent")
    index = json.loads(ACTOR_INDEX.read_text(encoding="utf-8"))
    if index.get("preparationComplete") is not True or index.get("owner") != "ACTORS":
        raise coord.BudgetError("Actor index is not a complete ACTORS publication")
    pinned = []
    seen = []
    for row in index["packs"]:
        pack_path = ROOT / row["path"]
        raw = pack_path.read_bytes()
        if coord.sha256_bytes(raw) != row["sha256"]:
            raise coord.BudgetError(f"Pack hash drifted: {row['id']}")
        pack = json.loads(raw.decode("utf-8"))
        if pack["id"] != row["id"]:
            raise coord.BudgetError(f"Pack id mismatch: {row['id']}")
        if float(pack["estimatedUpperBoundUSD"]) != 0.4:
            raise coord.BudgetError(f"Unexpected bound for {pack['id']}")
        if pack.get("requestedResolution") != "2K" or pack.get("aspectRatio") != "1:1":
            raise coord.BudgetError(f"Unexpected actor format for {pack['id']}")
        wire_path = ROOT / pack["wireBodyPath"]
        wire = wire_path.read_bytes()
        if coord.sha256_bytes(wire) != pack["wireBodySHA256"]:
            raise coord.BudgetError(f"Wire hash drifted: {pack['id']}")
        prompt_path = ROOT / pack["promptPath"]
        if coord.sha256_bytes(prompt_path.read_bytes()) != pack["promptSHA256"]:
            raise coord.BudgetError(f"Prompt hash drifted: {pack['id']}")
        guide = pack["guide"]
        if coord.sha256_bytes((ROOT / guide["path"]).read_bytes()) != guide["sha256"]:
            raise coord.BudgetError(f"Guide hash drifted: {pack['id']}")
        pinned.append({"pack": pack, "wire": wire, "packPath": pack_path})
        seen.append(pack["id"])
    if seen != index["pendingPackIds"]:
        raise coord.BudgetError("Index order does not match pack rows")
    return pinned


def wire_meta(item_id: str, attempt_id: str, owner: str, wire: bytes) -> dict:
    body = json.loads(wire.decode("utf-8"))
    texts = coord._body_text_parts(body)
    if len(texts) != 1:
        raise coord.BudgetError(f"{item_id} wire does not have one text part")
    return {
        "id": item_id,
        "attemptId": attempt_id,
        "owner": owner,
        "prompt": texts[0],
        "wireBodySHA256": coord.sha256_bytes(wire),
        "inlineCount": len(coord._body_inline_parts(body)),
    }


def extract_actor(response_bytes: bytes, dest: Path) -> dict:
    payload = json.loads(response_bytes.decode("utf-8"))
    usage = payload.get("usageMetadata")
    parts = (((payload.get("candidates") or [{}])[0].get("content") or {}).get("parts") or [])
    inline = [part["inlineData"] for part in parts if "inlineData" in part]
    if not inline:
        return {"status": "NO_IMAGE", "usage": usage}
    raw = base64.b64decode(inline[0]["data"])
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(raw)
    with Image.open(dest) as image:
        image.load()
        size = image.size
        fmt = image.format
    native_ok = fmt == "PNG" and size == (2048, 2048)
    preview = QA / "review" / "candidates" / "actors" / f"{dest.stem}.jpg"
    preview.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(dest) as image:
        image.convert("RGB").resize((512, 512)).save(preview, quality=85)
    return {
        "status": "CANDIDATE" if native_ok else "FAILED_NATIVE_CONTRACT",
        "dimensions": {"width": size[0], "height": size[1]},
        "format": fmt,
        "sha256": coord.sha256_bytes(raw),
        "bytes": len(raw),
        "nativeOk": native_ok,
        "usage": usage,
        "preview": str(preview.relative_to(ROOT)).replace("\\", "/"),
    }


def publish_actor_receipt(pack: dict, attempt_id: str, result: dict, image_info: dict, response_path: Path, native_path: Path) -> dict:
    receipt = {
        "id": f"receipt-{attempt_id}",
        "canonicalId": pack["id"],
        "owner": "ACTORS",
        "attemptId": attempt_id,
        "requestPackSHA256": coord.sha256_bytes((ROOT / "qa/image-vertex-repair-20261009/actors/regeneration/packs" / pack["id"] / "pack.json").read_bytes()),
        "wireBodySHA256": pack["wireBodySHA256"],
        "project": coord.PROJECT,
        "model": coord.MODEL,
        "resolution": "2K",
        "status": "SUCCEEDED_CANDIDATE" if image_info.get("nativeOk") else "FAILED",
        "providerOperation": None,
        "rawResponsePath": str(response_path.relative_to(ROOT)).replace("\\", "/"),
        "rawResponseSHA256": coord.sha256_bytes(response_path.read_bytes()) if response_path.exists() else None,
        "images": [],
        "usage": image_info.get("usage"),
        "reservedUSD": 0.4,
        "actualOrRetainedExposureUSD": 0.4,
        "complete": True,
        "rejectionEvidence": [],
        "nextAction": "AI2 reviews this candidate. Coordinator did not write AI2 directories or mark the sprite READY.",
        "review": "UNREVIEWED_BY_OWNER",
    }
    if image_info.get("sha256"):
        receipt["images"].append({
            "path": str(native_path.relative_to(ROOT)).replace("\\", "/"),
            "sha256": image_info["sha256"],
            "bytes": image_info["bytes"],
            "dimensions": image_info["dimensions"],
            "format": image_info.get("format"),
        })
    if not image_info.get("nativeOk"):
        receipt["status"] = "FAILED"
        receipt["rejectionEvidence"].append(image_info.get("status") or result.get("status") or "no usable image")
    out = QA / "vertex-coordinator" / "receipts" / "ACTORS" / f"{attempt_id}.json"
    kingdom.write_json(out, receipt)
    return receipt


def finish_documents(runner: coord.Coordinator, receipts: list[dict], stopped: str | None, medieval: dict, unsent: list[str]) -> None:
    exposure = runner.exposure_usd()
    margin = round(HARD - exposure, 4)
    kingdom.write_json(QA / "vertex-coordinator" / "scheduler-state.json", {
        "closed": False,
        "reason": "Affordable actor prefix and the retained medieval resume were attempted. Remaining packs do not fit under the hard cap, or a stop left them unsent. Coordinator stays open.",
        "actorIndexPresent": True,
        "actorPacksSubmitted": [row["id"] for row in receipts],
        "actorPacksUnsent": unsent,
        "medievalResume": medieval,
        "stopped": stopped,
        "exposureUSD": exposure,
        "marginUnderHardCapUSD": margin,
        "recordedAt": kingdom.now(),
    })
    if not INTERFACE.exists():
        return
    interface = json.loads(INTERFACE.read_text(encoding="utf-8"))
    interface["actorReceipts"] = [
        f"qa/image-vertex-repair-20261009/environment/vertex-coordinator/receipts/ACTORS/actors-{row['id']}-v1-a1.json"
        for row in receipts
    ]
    interface["imageWorkComplete"] = False
    interface["wholeDeliveryReady"] = False
    interface["budgetSnapshot"]["addedRetainedUSD"] = round(exposure - BASELINE, 4)
    interface["budgetSnapshot"]["currentCommittedProtectedUSD"] = exposure
    interface["budgetSnapshot"]["marginUnderHardCapUSD"] = margin
    interface["budgetSnapshot"]["note"] = (
        "Actor packs use their declared 0.4 reserve. Medieval v2 keeps its existing 0.4931 reserve. "
        "Unsent packs are budget-blocked. Invoices remain unknown."
    )
    interface["paidBlockedIds"] = unsent + [
        "kingdom-terrain-gunpowder-correction",
        "kingdom-terrain-industrial-correction",
        "kingdom-terrain-modern-correction",
        "kingdom-terrain-future-correction",
        "adventure-and-defense-packs",
    ]
    kingdom.write_json(INTERFACE, interface)


def main() -> None:
    pinned = pin_actors()
    evidence_dir = QA / "vertex-coordinator" / "evidence" / "actor-wave"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    for name in ("submission.mutex.json", "active-batch.lock.json", "pacing_state.json", "budget-ledger.json"):
        source = SHARED / name
        if source.exists():
            (evidence_dir / f"{name}.before").write_bytes(source.read_bytes())
    try:
        access = kingdom.token()
    except coord.AuthError as exc:
        kingdom.write_json(RESULT_PATH, {"ok": False, "blocked": [str(exc)], "paidSubmitted": False})
        print(json.dumps({"ok": False, "blocked": [str(exc)]}))
        return
    evidence = kingdom.probe(access)
    kingdom.write_json(evidence_dir / "access.json", evidence)
    if evidence["blocked"]:
        kingdom.write_json(RESULT_PATH, {"ok": False, "blocked": evidence["blocked"], "paidSubmitted": False})
        print(json.dumps({"ok": False, "blocked": evidence["blocked"]}))
        return
    runner = coord.Coordinator(
        QA / "vertex-coordinator",
        owner_id=f"environment-vertex-actors-pid{os.getpid()}",
        committed_protected_usd=BASELINE,
        hard_cap_usd=HARD,
        cloud_lock_enabled=True,
        mutex_file=SHARED / "submission.mutex.json",
        pacing_file=SHARED / "pacing_state.json",
        token_provider=kingdom.token,
    )
    expected = round(BASELINE + sum(row["reservedUSD"] for row in runner.reservations if row.get("retained")), 6)
    if abs(runner.exposure_usd() - expected) > 1e-9 or abs(expected - 77.0327) > 1e-9:
        kingdom.write_json(RESULT_PATH, {"ok": False, "blocked": [f"exposure {runner.exposure_usd()} != 77.0327"]})
        print(json.dumps({"ok": False, "exposure": runner.exposure_usd()}))
        return
    receipts = []
    unsent = [row["pack"]["id"] for row in pinned]
    stopped = None
    medieval = {"attempted": False}
    released = False
    try:
        runner.acquire_mutex()
        local_lock = json.loads((SHARED / "active-batch.lock.json").read_text(encoding="utf-8"))
        if str(local_lock.get("state", "")) in kingdom.ACTIVE or local_lock.get("workflow_state") in kingdom.ACTIVE:
            raise coord.MutexError("Local active-batch lock is active")
        kingdom.write_json(SHARED / "active-batch.lock.json", {
            "batch_id": "vertex-repair-20261009",
            "model": coord.MODEL,
            "project": coord.PROJECT,
            "account": coord.ACCOUNT,
            "state": "JOB_STATE_RUNNING",
            "workflow_state": "ACTIVE_INDIVIDUAL_GENERATION",
            "owner": runner.owner_id,
            "queue": "ACTORS",
        })
        runner.preflight_unknown([QA / "vertex-coordinator" / "attempts" / MEDIEVAL_ATTEMPT])
        for item in pinned:
            pack = item["pack"]
            reservation = float(pack["estimatedUpperBoundUSD"])
            if runner.exposure_usd() + reservation > HARD + 1e-9:
                stopped = f"Hard cap. Next pack {pack['id']} needs {reservation}; exposure {runner.exposure_usd()}."
                break
            attempt_id = f"actors-{pack['id']}-v1-a1"
            meta = wire_meta(pack["id"], attempt_id, "ACTORS", item["wire"])
            attempt_dir = QA / "vertex-coordinator" / "attempts" / attempt_id
            try:
                result = runner.execute_prepared(attempt_dir, item["wire"], meta, reservation)
            except coord.QuotaStop as exc:
                stopped = str(exc)
                append_ledger({
                    "attemptId": attempt_id, "scene": pack["id"], "ownerQueue": "ACTORS",
                    "reservedUSD": reservation, "retained": True, "status": "QUOTA_STOP_HTTP_429", "at": kingdom.now(),
                })
                unsent = unsent[unsent.index(pack["id"]) + 1:]
                break
            except (coord.AuthError, coord.UnknownLiabilityError) as exc:
                stopped = f"{type(exc).__name__}: {exc}"
                append_ledger({
                    "attemptId": attempt_id, "scene": pack["id"], "ownerQueue": "ACTORS",
                    "reservedUSD": reservation, "retained": True, "status": type(exc).__name__, "at": kingdom.now(),
                })
                unsent = unsent[unsent.index(pack["id"]) + 1:]
                break
            native_path = QA / "vertex-coordinator" / "receipts" / "ACTORS" / "natives" / f"{pack['id']}.png"
            response_path = attempt_dir / "response.json"
            image_info = {"status": result["status"], "nativeOk": False}
            if result["status"] == "SUCCEEDED_CANDIDATE" and response_path.exists():
                image_info = extract_actor(response_path.read_bytes(), native_path)
            receipt = publish_actor_receipt(pack, attempt_id, result, image_info, response_path, native_path)
            receipts.append({
                "id": pack["id"], "receipt": receipt["status"],
                "image": image_info.get("dimensions"), "nativeOk": image_info.get("nativeOk"),
            })
            append_ledger({
                "attemptId": attempt_id, "scene": pack["id"], "ownerQueue": "ACTORS",
                "reservedUSD": reservation, "retained": True, "status": receipt["status"], "at": kingdom.now(),
            })
            unsent = [name for name in unsent if name != pack["id"]]
            print(json.dumps(receipts[-1]), flush=True)
        if stopped is None and not runner.blocked:
            pack = json.loads(MEDIEVAL_PACK.read_text(encoding="utf-8"))
            wire = (ROOT / pack["wireBodyPath"]).read_bytes()
            if coord.sha256_bytes(wire) != pack["wireBodySHA256"]:
                raise coord.BudgetError("Medieval wire hash drifted")
            if pack["wireBodySHA256"] != "3f48a38cc17fb4763ff44e84fb405a6d39d80a8963a810a38e966b1973d36769":
                raise coord.BudgetError("Medieval body is not the retained 429 body")
            meta = wire_meta("kingdom-terrain-medieval", MEDIEVAL_ATTEMPT, "ENVIRONMENT", wire)
            attempt_dir = QA / "vertex-coordinator" / "attempts" / MEDIEVAL_ATTEMPT
            before = runner.exposure_usd()
            medieval["attempted"] = True
            try:
                result = runner.resume_retained_body(attempt_dir, wire, meta)
            except (coord.QuotaStop, coord.AuthError, coord.UnknownLiabilityError) as exc:
                stopped = f"medieval resume {type(exc).__name__}: {exc}"
                medieval["status"] = type(exc).__name__
                if runner.exposure_usd() != before:
                    raise coord.BudgetError("Medieval resume changed exposure")
            else:
                if runner.exposure_usd() != before:
                    raise coord.BudgetError("Medieval resume changed exposure")
                response_path = attempt_dir / "response.json"
                image_info = {"status": result["status"]}
                native_path = ROOT / "assets" / "derivatives" / "image-vertex-repair-20261009" / "environment" / "native" / "kingdom-terrain-medieval-candidate-b.png"
                if result["status"] == "SUCCEEDED_CANDIDATE" and response_path.exists():
                    image_info = kingdom.extract_image(response_path.read_bytes(), native_path)
                medieval["status"] = image_info.get("status")
                medieval["dimensions"] = image_info.get("dimensions")
                medieval["nativeOk"] = image_info.get("nativeOk")
                update_ledger_status(MEDIEVAL_ATTEMPT, "SUCCEEDED_CANDIDATE" if image_info.get("nativeOk") else result["status"])
                receipt_path = QA / "vertex-coordinator" / "receipts" / "ENVIRONMENT" / f"{MEDIEVAL_ATTEMPT}.json"
                kingdom.write_json(receipt_path, {
                    "id": f"receipt-{MEDIEVAL_ATTEMPT}",
                    "canonicalId": "kingdom-terrain-medieval",
                    "owner": "ENVIRONMENT",
                    "attemptId": MEDIEVAL_ATTEMPT,
                    "wireBodySHA256": pack["wireBodySHA256"],
                    "status": "SUCCEEDED_CANDIDATE" if image_info.get("nativeOk") else "FAILED",
                    "resolution": "4K",
                    "images": [{
                        "path": "assets/derivatives/image-vertex-repair-20261009/environment/native/kingdom-terrain-medieval-candidate-b.png",
                        "sha256": image_info.get("sha256"),
                        "dimensions": image_info.get("dimensions"),
                    }] if image_info.get("sha256") else [],
                    "reservedUSD": 0.4931,
                    "newReservation": False,
                    "review": "UNREVIEWED_GEOMETRY",
                    "nextAction": "Measure the candidate against the frozen guide before any further kingdom call. No third attempt.",
                })
                print(json.dumps({"medieval": medieval}), flush=True)
    except Exception as exc:
        stopped = stopped or f"{type(exc).__name__}: {exc}"
        if "UNKNOWN" in stopped or isinstance(exc, coord.UnknownLiabilityError):
            runner.blocked = True
    finally:
        if runner.has_lock:
            release_state = "UNKNOWN" if runner.blocked and runner.block_reason != "HTTP 429" else "RELEASED"
            released = runner.release_mutex(release_state)
        if released and not runner.blocked:
            kingdom.write_json(SHARED / "active-batch.lock.json", {
                "batch_id": "vertex-repair-20261009",
                "model": coord.MODEL,
                "project": coord.PROJECT,
                "account": coord.ACCOUNT,
                "state": "JOB_STATE_SUCCEEDED",
                "workflow_state": "TERMINAL_COLLECTED",
                "owner": runner.owner_id,
                "releasedAt": kingdom.now(),
                "actorReceipts": [row["id"] for row in receipts],
                "medievalResume": medieval,
            })
        elif released and runner.block_reason == "HTTP 429":
            kingdom.write_json(SHARED / "active-batch.lock.json", {
                "batch_id": "vertex-repair-20261009",
                "model": coord.MODEL,
                "project": coord.PROJECT,
                "account": coord.ACCOUNT,
                "state": "QUOTA_STOP_HTTP_429",
                "workflow_state": "PAID_RUN_STOPPED_DEFINITE_429",
                "owner": runner.owner_id,
                "releasedAt": kingdom.now(),
                "actorReceipts": [row["id"] for row in receipts],
            })
    payload = {
        "ok": stopped is None and released and not runner.unresolved_items,
        "submitted": len(receipts),
        "receipts": receipts,
        "unsent": unsent,
        "medieval": medieval,
        "stopped": stopped,
        "exposure": runner.exposure_usd(),
        "released": released,
        "blocked": runner.blocked,
        "blockReason": runner.block_reason,
    }
    finish_documents(runner, receipts, stopped, medieval, unsent)
    kingdom.write_json(RESULT_PATH, payload)
    print(json.dumps({k: payload[k] for k in ("ok", "submitted", "stopped", "exposure", "released", "unsent")}), flush=True)


if __name__ == "__main__":
    main()
