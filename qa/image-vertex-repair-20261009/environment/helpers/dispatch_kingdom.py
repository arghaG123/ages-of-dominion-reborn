"""Submit prepared kingdom terrain packs. Stops on access, quota, unknown, or budget hold."""
from __future__ import annotations

import base64
import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import coordinator as coord

ROOT = Path(r"C:\dev\ages-of-dominion-reborn")
QA = ROOT / "qa" / "image-vertex-repair-20261009" / "environment"
SHARED = ROOT / "docs" / "plan" / "image-production"
INTERFACE = ROOT / "docs" / "plan" / "ENVIRONMENT-ART-VERTEX-REPAIR-INTERFACE-2026-10-09.json"
PROJECT = coord.PROJECT
ACCOUNT = coord.ACCOUNT
BASELINE = 71.1156
HARD = 80.0
# Unspent margin kept for one correction wave and the unpublished actor queue.
# This is not the US$15 reserve, which is already inside BASELINE.
HOLD_REMAINING = 4.90
ORDER = [
    "kingdom-terrain-stone",
    "kingdom-terrain-bronze",
    "kingdom-terrain-iron",
    "kingdom-terrain-medieval",
    "kingdom-terrain-gunpowder",
    "kingdom-terrain-industrial",
    "kingdom-terrain-modern",
    "kingdom-terrain-future",
]
ACTIVE = {
    "JOB_STATE_RUNNING", "JOB_STATE_PENDING", "JOB_STATE_QUEUED",
    "JOB_STATE_UNSPECIFIED", "JOB_STATE_UNKNOWN", "UNKNOWN",
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(payload, indent=2).encode("utf-8")
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_bytes(data)
    os.replace(tmp, path)


def token() -> str:
    gcloud = r"C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd"
    cmd = [gcloud, "auth", "print-access-token", f"--account={ACCOUNT}", f"--project={PROJECT}"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").replace("\n", " ")[:240]
        raise coord.AuthError(f"token refresh failed: {detail}")
    value = result.stdout.strip()
    if not value or " " in value:
        raise coord.AuthError("token refresh returned an empty value")
    return value


def get_json(url: str, access: str):
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + access})
    try:
        with urllib.request.urlopen(req, timeout=40) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        body = err.read().decode("utf-8", errors="replace")[:400]
        return err.code, {"error": body}


def job_summary(payload) -> dict:
    jobs = payload.get("batchPredictionJobs") or []
    states = {}
    active = []
    for job in jobs:
        state = str(job.get("state") or "UNKNOWN")
        states[state] = states.get(state, 0) + 1
        if state in ACTIVE:
            active.append({"name": job.get("name"), "state": state})
    return {
        "count": len(jobs),
        "states": states,
        "active": active,
        "hasNextPage": bool(payload.get("nextPageToken")),
    }


def probe(access: str) -> dict:
    evidence = {"probedAt": now(), "account": ACCOUNT, "project": PROJECT, "model": coord.MODEL, "token": "acquired-not-recorded"}
    regions = {
        "global": f"https://aiplatform.googleapis.com/v1/projects/{PROJECT}/locations/global/batchPredictionJobs?pageSize=100",
        "us-central1": f"https://us-central1-aiplatform.googleapis.com/v1/projects/{PROJECT}/locations/us-central1/batchPredictionJobs?pageSize=100",
    }
    evidence["jobs"] = {}
    blocked = []
    for name, url in regions.items():
        code, payload = get_json(url, access)
        if code != 200:
            evidence["jobs"][name] = {"http": code, "error": payload.get("error")}
            if code in {401, 403}:
                blocked.append(f"{name} batch list HTTP {code}")
            continue
        summary = job_summary(payload)
        evidence["jobs"][name] = summary
        if summary["active"] or summary["hasNextPage"]:
            blocked.append(f"{name} has active jobs or an unread page")
    code, meta = get_json(
        "https://storage.googleapis.com/storage/v1/b/"
        f"{coord.BUCKET}/o/{urllib.parse.quote(coord.LOCK_OBJECT, safe='')}",
        access,
    )
    evidence["cloudLockMeta"] = {"http": code}
    if code == 200:
        evidence["cloudLockMeta"]["generation"] = meta.get("generation")
        media_code, lock = get_json(
            "https://storage.googleapis.com/storage/v1/b/"
            f"{coord.BUCKET}/o/{urllib.parse.quote(coord.LOCK_OBJECT, safe='')}?alt=media",
            access,
        )
        evidence["cloudLock"] = {"http": media_code, "state": lock.get("state"), "workflow": lock.get("workflow_state"), "owner": lock.get("owner")}
        state = str(lock.get("state") or "")
        workflow = str(lock.get("workflow_state") or "")
        if state in ACTIVE or workflow in ACTIVE or "UNKNOWN" in state or "UNKNOWN" in workflow:
            blocked.append(f"cloud lock {state}/{workflow}")
    elif code != 404:
        blocked.append(f"cloud lock metadata HTTP {code}")
        evidence["cloudLockMeta"]["error"] = meta.get("error")
    model_code, model_payload = get_json(
        "https://aiplatform.googleapis.com/v1/projects/"
        f"{PROJECT}/locations/global/publishers/google/models/{coord.MODEL}",
        access,
    )
    evidence["model"] = {"http": model_code, "name": model_payload.get("name") if isinstance(model_payload, dict) else None}
    if model_code in {401, 403}:
        blocked.append(f"model metadata HTTP {model_code}")
    evidence["blocked"] = blocked
    evidence["pricingChecked"] = {
        "source": "https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing?hl=en",
        "checkedOn": "2026-10-09",
        "imageOutput4KApproximateUSD": 0.15,
        "imageOutput2KApproximateUSD": 0.101,
        "inputImageTokens": 1120,
        "output4KTokens": 2520,
        "imageOutputPer1M": 60.0,
        "inputPer1MGlobal": 0.5,
        "note": "Non-200 responses are documented as unbilled. Unknown transport outcomes stay retained.",
    }
    return evidence


def extract_image(response_bytes: bytes, dest: Path) -> dict:
    payload = json.loads(response_bytes.decode("utf-8"))
    parts = (((payload.get("candidates") or [{}])[0].get("content") or {}).get("parts") or [])
    inline = [part["inlineData"] for part in parts if "inlineData" in part]
    if not inline:
        return {"status": "NO_IMAGE", "usage": payload.get("usageMetadata")}
    raw = base64.b64decode(inline[0]["data"])
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(raw)
    with Image.open(dest) as image:
        image.load()
        size = image.size
        fmt = image.format
    long_edge = max(size)
    aspect = size[0] / size[1]
    native_ok = long_edge >= 3840 and abs(aspect - (16 / 9)) < 0.03 and fmt == "PNG"
    return {
        "status": "CANDIDATE" if native_ok else "FAILED_NATIVE_SIZE",
        "dimensions": {"width": size[0], "height": size[1]},
        "format": fmt,
        "sha256": coord.sha256_bytes(raw),
        "bytes": len(raw),
        "usage": payload.get("usageMetadata"),
        "nativeOk": native_ok,
    }


def append_ledger(attempt: dict) -> None:
    ledger_path = SHARED / "budget-ledger.json"
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    section = ledger.setdefault("vertexRepair20261009", {
        "previousCommittedProtectedUSD": BASELINE,
        "note": "Added by the 9 October environment coordinator. reconciliationTrail was not rewritten.",
        "attempts": [],
    })
    section["attempts"].append(attempt)
    retained = sum(row["reservedUSD"] for row in section["attempts"] if row.get("retained"))
    section["addedRetainedUSD"] = round(retained, 4)
    section["currentCommittedProtectedUSD"] = round(BASELINE + retained, 4)
    write_json(ledger_path, ledger)


def publish_receipt(scene_id: str, attempt_id: str, pack: dict, result: dict, image_info: dict, response_path: Path) -> dict:
    receipt = {
        "id": f"receipt-{attempt_id}",
        "canonicalId": scene_id,
        "owner": "ENVIRONMENT",
        "attemptId": attempt_id,
        "requestPackSHA256": coord.sha256_bytes((QA / "regeneration" / "packs" / f"{pack['id']}.json").read_bytes()),
        "wireBodySHA256": pack["wireBodySHA256"],
        "project": PROJECT,
        "model": coord.MODEL,
        "resolution": "4K",
        "status": "SUCCEEDED_CANDIDATE" if image_info.get("status") == "CANDIDATE" else "FAILED",
        "providerOperation": None,
        "rawResponsePath": str(response_path.relative_to(ROOT)).replace("\\", "/"),
        "rawResponseSHA256": coord.sha256_bytes(response_path.read_bytes()) if response_path.exists() else None,
        "images": [],
        "usage": image_info.get("usage"),
        "reservedUSD": pack["estimatedUpperBoundUSD"],
        "actualOrRetainedExposureUSD": pack["estimatedUpperBoundUSD"],
        "complete": True,
        "rejectionEvidence": [],
        "nextAction": "Review candidate pixels before any correction call.",
    }
    if image_info.get("sha256"):
        receipt["images"].append({
            "path": f"assets/derivatives/image-vertex-repair-20261009/environment/native/{scene_id}-candidate-a.png",
            "sha256": image_info["sha256"],
            "bytes": image_info["bytes"],
            "dimensions": image_info["dimensions"],
        })
    if image_info.get("status") != "CANDIDATE":
        receipt["status"] = "FAILED"
        receipt["rejectionEvidence"].append(image_info.get("status") or "no usable image")
        receipt["nextAction"] = "One directed correction is allowed if budget remains. This attempt is preserved."
    out = QA / "vertex-coordinator" / "receipts" / "ENVIRONMENT" / f"{attempt_id}.json"
    write_json(out, receipt)
    return receipt


def main() -> None:
    evidence_dir = QA / "vertex-coordinator" / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    for name in ("submission.mutex.json", "active-batch.lock.json", "pacing_state.json", "budget-ledger.json"):
        source = SHARED / name
        if source.exists():
            (evidence_dir / f"{name}.before").write_bytes(source.read_bytes())
    try:
        access = token()
    except coord.AuthError as exc:
        write_json(evidence_dir / "access.json", {"blocked": [str(exc)], "paidSubmitted": False, "probedAt": now()})
        print(json.dumps({"paidSubmitted": False, "blocked": [str(exc)]}))
        return
    evidence = probe(access)
    write_json(evidence_dir / "access.json", evidence)
    if evidence["blocked"]:
        print(json.dumps({"paidSubmitted": False, "blocked": evidence["blocked"]}))
        return
    actor_index = ROOT / "qa/image-vertex-repair-20261009/actors/regeneration/ready-index.json"
    runner = coord.Coordinator(
        QA / "vertex-coordinator",
        owner_id=f"environment-vertex-20261009-pid{os.getpid()}",
        committed_protected_usd=BASELINE,
        hard_cap_usd=HARD,
        cloud_lock_enabled=True,
        mutex_file=SHARED / "submission.mutex.json",
        pacing_file=SHARED / "pacing_state.json",
        token_provider=token,
    )
    receipts = []
    stopped = None
    try:
        runner.acquire_mutex()
        local_lock = json.loads((SHARED / "active-batch.lock.json").read_text(encoding="utf-8"))
        if str(local_lock.get("state", "")) in ACTIVE or local_lock.get("workflow_state") in ACTIVE:
            raise coord.MutexError("Local active-batch lock is active")
        local_lock_running = {
            "batch_id": "vertex-repair-20261009",
            "model": coord.MODEL,
            "project": PROJECT,
            "account": ACCOUNT,
            "state": "JOB_STATE_RUNNING",
            "workflow_state": "ACTIVE_INDIVIDUAL_GENERATION",
            "owner": runner.owner_id,
            "priorStatePreservedAt": "qa/image-vertex-repair-20261009/environment/vertex-coordinator/evidence/active-batch.lock.json.before",
        }
        write_json(SHARED / "active-batch.lock.json", local_lock_running)
        for scene_id in ORDER:
            pack_path = QA / "regeneration" / "packs" / f"env-{scene_id}-v1.json"
            pack = json.loads(pack_path.read_text(encoding="utf-8"))
            reservation = float(pack["estimatedUpperBoundUSD"])
            if runner.exposure_usd() + reservation > HARD - HOLD_REMAINING + 1e-9:
                stopped = f"Holding remaining margin. Next pack {scene_id} needs {reservation}."
                break
            wire = (QA / "regeneration" / "wire" / f"{scene_id}.json").read_bytes()
            if coord.sha256_bytes(wire) != pack["wireBodySHA256"]:
                raise coord.BudgetError(f"Wire hash drifted for {scene_id}")
            attempt_id = f"{pack['id']}-a1"
            meta = {
                "id": scene_id,
                "attemptId": attempt_id,
                "owner": "ENVIRONMENT",
                "prompt": (QA / "regeneration" / "prompts" / f"{scene_id}.txt").read_text(encoding="utf-8"),
                "wireBodySHA256": pack["wireBodySHA256"],
                "inlineCount": 2,
                "model": coord.MODEL,
                "endpoint": coord.ENDPOINT,
            }
            attempt_dir = QA / "vertex-coordinator" / "attempts" / attempt_id
            try:
                result = runner.execute_prepared(attempt_dir, wire, meta, reservation)
            except coord.QuotaStop as exc:
                stopped = str(exc)
                append_ledger({"attemptId": attempt_id, "scene": scene_id, "reservedUSD": reservation, "retained": True, "status": "QUOTA_STOP", "at": now()})
                break
            except coord.AuthError as exc:
                stopped = str(exc)
                append_ledger({"attemptId": attempt_id, "scene": scene_id, "reservedUSD": reservation, "retained": True, "status": "ACCESS_DENIED", "at": now()})
                break
            except coord.UnknownLiabilityError as exc:
                stopped = str(exc)
                append_ledger({"attemptId": attempt_id, "scene": scene_id, "reservedUSD": reservation, "retained": True, "status": "UNKNOWN", "at": now()})
                break
            response_path = attempt_dir / "response.json"
            image_info = {"status": result["status"]}
            if result["status"] == "SUCCEEDED_CANDIDATE" and response_path.exists():
                image_info = extract_image(
                    response_path.read_bytes(),
                    ROOT / "assets/derivatives/image-vertex-repair-20261009/environment/native" / f"{scene_id}-candidate-a.png",
                )
            receipt = publish_receipt(scene_id, attempt_id, pack, result, image_info, response_path)
            receipts.append({"id": scene_id, "receipt": receipt["status"], "image": image_info.get("dimensions"), "nativeOk": image_info.get("nativeOk")})
            append_ledger({
                "attemptId": attempt_id,
                "scene": scene_id,
                "reservedUSD": reservation,
                "retained": True,
                "status": receipt["status"],
                "at": now(),
            })
            print(json.dumps(receipts[-1]), flush=True)
    except Exception as exc:
        stopped = stopped or f"{type(exc).__name__}: {exc}"
    finally:
        released = False
        if runner.has_lock:
            released = runner.release_mutex("RELEASED" if not runner.blocked else "UNKNOWN")
        if released:
            write_json(SHARED / "active-batch.lock.json", {
                "batch_id": "vertex-repair-20261009",
                "model": coord.MODEL,
                "project": PROJECT,
                "account": ACCOUNT,
                "state": "JOB_STATE_SUCCEEDED" if not runner.blocked else "JOB_STATE_UNKNOWN",
                "workflow_state": "TERMINAL_COLLECTED" if not runner.blocked else "UNKNOWN",
                "owner": runner.owner_id,
                "releasedAt": now(),
                "receipts": [row["id"] for row in receipts],
            })
    actor_present = actor_index.exists()
    write_json(QA / "vertex-coordinator" / "scheduler-state.json", {
        "closed": False,
        "reason": stopped or ("Actor index still absent." if not actor_present else "Actor index appeared and was not fully served in this pass."),
        "actorIndexPresent": actor_present,
        "environmentPacksSubmitted": [row["id"] for row in receipts],
        "stopped": stopped,
        "exposureUSD": runner.exposure_usd(),
        "recordedAt": now(),
    })
    if INTERFACE.exists():
        interface = json.loads(INTERFACE.read_text(encoding="utf-8"))
        interface["generationReceipts"] = [
            f"qa/image-vertex-repair-20261009/environment/vertex-coordinator/receipts/ENVIRONMENT/{pack_id}-a1.json"
            for pack_id in (f"env-{row['id']}-v1" for row in receipts)
        ]
        interface["paidCompletedIds"] = [row["id"] for row in receipts if row["receipt"] == "SUCCEEDED_CANDIDATE"]
        interface["paidPendingIds"] = [scene for scene in ORDER if scene not in interface["paidCompletedIds"]]
        interface["imageWorkComplete"] = False
        interface["budgetSnapshot"]["newSpendReservedUSD"] = round(runner.exposure_usd() - BASELINE, 4)
        interface["budgetSnapshot"]["exposureUSD"] = runner.exposure_usd()
        write_json(INTERFACE, interface)
        checkpoint_path = QA / "checkpoint.json"
        if checkpoint_path.exists():
            checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
            checkpoint["paidCompletedIds"] = interface["paidCompletedIds"]
            checkpoint["paidPendingIds"] = interface["paidPendingIds"]
            checkpoint["imageWorkComplete"] = False
            checkpoint["budgetSnapshot"] = interface["budgetSnapshot"]
            checkpoint["nextExecutableActions"]["paid"] = stopped or "Review native candidates before a correction. Other mode packs remain unsent inside the hold."
            write_json(checkpoint_path, checkpoint)
    print(json.dumps({"submitted": len(receipts), "stopped": stopped, "exposure": runner.exposure_usd(), "released": released}))


if __name__ == "__main__":
    main()
