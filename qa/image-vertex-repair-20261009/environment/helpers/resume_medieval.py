"""Resume the retained medieval v2 body. Does not add a reservation or send any other pack."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import coordinator as coord
import dispatch_actor_index as actors
import dispatch_kingdom as kingdom

ATTEMPT = actors.MEDIEVAL_ATTEMPT
EXPECTED = 79.8327


def main() -> None:
    runner = coord.Coordinator(
        actors.QA / "vertex-coordinator",
        owner_id=f"environment-vertex-medieval-resume-pid{os.getpid()}",
        committed_protected_usd=actors.BASELINE,
        hard_cap_usd=actors.HARD,
        cloud_lock_enabled=True,
        mutex_file=actors.SHARED / "submission.mutex.json",
        pacing_file=actors.SHARED / "pacing_state.json",
        token_provider=kingdom.token,
    )
    if abs(runner.exposure_usd() - EXPECTED) > 1e-9:
        print(json.dumps({"ok": False, "exposure": runner.exposure_usd()}))
        return
    pack = json.loads(actors.MEDIEVAL_PACK.read_text(encoding="utf-8"))
    wire = (actors.ROOT / pack["wireBodyPath"]).read_bytes()
    if coord.sha256_bytes(wire) != "3f48a38cc17fb4763ff44e84fb405a6d39d80a8963a810a38e966b1973d36769":
        raise coord.BudgetError("Medieval body hash is not the retained 429 body")
    meta = actors.wire_meta("kingdom-terrain-medieval", ATTEMPT, "ENVIRONMENT", wire)
    attempt_dir = actors.QA / "vertex-coordinator" / "attempts" / ATTEMPT
    access = kingdom.token()
    evidence = kingdom.probe(access)
    if evidence["blocked"]:
        print(json.dumps({"ok": False, "blocked": evidence["blocked"]}))
        return
    stopped = None
    image_info = {}
    released = False
    before = runner.exposure_usd()
    try:
        runner.acquire_mutex()
        kingdom.write_json(actors.SHARED / "active-batch.lock.json", {
            "batch_id": "vertex-repair-20261009",
            "model": coord.MODEL,
            "project": coord.PROJECT,
            "account": coord.ACCOUNT,
            "state": "JOB_STATE_RUNNING",
            "workflow_state": "ACTIVE_INDIVIDUAL_GENERATION",
            "owner": runner.owner_id,
            "queue": "MEDIEVAL_RESUME",
        })
        result = runner.resume_retained_body(attempt_dir, wire, meta)
        if runner.exposure_usd() != before:
            raise coord.BudgetError("Resume changed exposure")
        native_path = actors.ROOT / "assets/derivatives/image-vertex-repair-20261009/environment/native/kingdom-terrain-medieval-candidate-b.png"
        response_path = attempt_dir / "response.json"
        if result["status"] == "SUCCEEDED_CANDIDATE" and response_path.exists():
            image_info = kingdom.extract_image(response_path.read_bytes(), native_path)
        else:
            image_info = {"status": result["status"], "nativeOk": False}
        actors.update_ledger_status(ATTEMPT, "SUCCEEDED_CANDIDATE" if image_info.get("nativeOk") else result["status"])
        kingdom.write_json(actors.QA / "vertex-coordinator" / "receipts" / "ENVIRONMENT" / f"{ATTEMPT}.json", {
            "id": f"receipt-{ATTEMPT}",
            "canonicalId": "kingdom-terrain-medieval",
            "owner": "ENVIRONMENT",
            "attemptId": ATTEMPT,
            "wireBodySHA256": pack["wireBodySHA256"],
            "status": "SUCCEEDED_CANDIDATE" if image_info.get("nativeOk") else "FAILED",
            "resolution": "4K",
            "newReservation": False,
            "images": [{
                "path": "assets/derivatives/image-vertex-repair-20261009/environment/native/kingdom-terrain-medieval-candidate-b.png",
                "sha256": image_info.get("sha256"),
                "dimensions": image_info.get("dimensions"),
            }] if image_info.get("sha256") else [],
            "reservedUSD": 0.4931,
            "review": "UNREVIEWED_GEOMETRY",
            "nextAction": "Compare with the frozen guide. No third kingdom attempt.",
        })
    except (coord.QuotaStop, coord.AuthError, coord.UnknownLiabilityError, coord.BudgetError, coord.MutexError) as exc:
        stopped = f"{type(exc).__name__}: {exc}"
    finally:
        if runner.has_lock:
            state = "UNKNOWN" if runner.blocked and runner.block_reason != "HTTP 429" else "RELEASED"
            released = runner.release_mutex(state)
        if released and not runner.blocked:
            kingdom.write_json(actors.SHARED / "active-batch.lock.json", {
                "batch_id": "vertex-repair-20261009",
                "state": "JOB_STATE_SUCCEEDED",
                "workflow_state": "TERMINAL_COLLECTED",
                "owner": runner.owner_id,
                "releasedAt": kingdom.now(),
                "medievalResume": image_info.get("status"),
            })
    print(json.dumps({
        "ok": stopped is None and released and not runner.blocked,
        "stopped": stopped,
        "released": released,
        "exposure": runner.exposure_usd(),
        "image": image_info.get("dimensions"),
        "nativeOk": image_info.get("nativeOk"),
        "status": image_info.get("status"),
        "blockReason": runner.block_reason,
    }))


if __name__ == "__main__":
    main()
