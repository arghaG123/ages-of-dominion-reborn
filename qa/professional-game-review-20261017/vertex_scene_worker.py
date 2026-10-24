import argparse
import base64
import hashlib
import importlib.util
import io
import json
import subprocess
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / "qa/professional-art-20261018"
PLAN = ROOT / "docs/plan/image-production"
SPEC = importlib.util.spec_from_file_location("professional_coordinator", ROOT / "qa/image-unified-reserve-20261009/helpers/coordinator.py")
coordinator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(coordinator)


def token():
    executable = Path.home() / "AppData/Local/Google/Cloud SDK/google-cloud-sdk/bin/gcloud.cmd"
    result = subprocess.run([str(executable), "auth", "print-access-token", f"--account={coordinator.ACCOUNT}", f"--project={coordinator.PROJECT}"], capture_output=True, text=True)
    if result.returncode or not result.stdout.strip():
        raise coordinator.AuthError("Requested account token unavailable; no generation sent")
    return result.stdout.strip()


def fetch(url, access_token):
    request = urllib.request.Request(url, headers={"Authorization": f"Bearer {access_token}"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read())


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2), encoding="utf-8")


def runner_and_reconciliation():
    ledger = read(PLAN / "budget-ledger.json")
    historical = ledger["vertexRepair20261009"]
    baseline_attempts = {row["attemptId"] for row in historical["attempts"]}
    old_holds = read(ROOT / "qa/image-vertex-repair-20261009/environment/vertex-coordinator/reservations.json")
    if any(row["attemptId"] not in baseline_attempts for row in old_holds if row.get("retained")):
        raise coordinator.BudgetError("Unreconciled retained environment liability")
    authority = ledger["professionalRepairAuthority20261018"]
    style = ledger["styleRepair20261016"]["attempts"]
    exempt = authority["excludedFromActiveRequestLockOnly"]
    unknown = [row["attemptId"] for row in style if "UNKNOWN" in row["status"]]
    if unknown != exempt or not all(row.get("retained") for row in style):
        raise coordinator.BudgetError("Historical unknown or retained liabilities changed")
    baseline = float(ledger["ownerReserveRelease20261009"]["priorLiabilityExcludingReserveUSD"])
    prior = round(baseline + sum(float(row["reservedUSD"]) for row in style if row.get("retained")), 6)
    runner = coordinator.Coordinator(WORK / "coordinator", owner_id="professional-art-20261018", prior_liability_usd=prior, effective_reserve_usd=0, hard_cap_usd=100, release=ledger["ownerReserveRelease20261009"], ceiling_authority=authority, cloud_lock_enabled=True, mutex_file=PLAN / "submission.mutex.json", pacing_file=PLAN / "pacing_state.json", token_provider=token, success_gap=20, backoff_429=60)
    if any("UNKNOWN" in row.get("status", "") or row.get("status") == "RESERVED_BEFORE_POST" for row in runner.reservations):
        raise coordinator.UnknownLiabilityError("New ambiguous reservation blocks generation")
    reconciliation = {"recordedAt": datetime.now(timezone.utc).isoformat(), "historicalProtectedUSD": historical["currentCommittedProtectedUSD"], "releasedReserveUSDCountedOnce": 15, "baselineExcludingReleasedReserveUSD": baseline, "laterRetainedStyleUSD": round(prior - baseline, 6), "priorLiabilityUSD": prior, "newRetainedUSD": runner.other_holds_usd(), "ceilingUSD": 100, "invoiceStatus": "UNKNOWN", "excludedFromLockOnly": exempt, "allHistoricalChargesRetained": True}
    write(WORK / "reconciliation.json", reconciliation)
    return runner, reconciliation


def preflight(runner):
    access_token = token()
    cloud_lock, generation = runner._get_cloud_lock(access_token)
    terminal = {"JOB_STATE_SUCCEEDED", "JOB_STATE_FAILED", "JOB_STATE_CANCELLED", "JOB_STATE_EXPIRED"}
    if cloud_lock and cloud_lock.get("state") not in terminal:
        raise coordinator.MutexError("Cloud lock is not terminal; no generation sent")
    jobs = []
    for location in ("global", "us-central1"):
        page_token = ""
        while True:
            url = f"https://aiplatform.googleapis.com/v1/projects/{coordinator.PROJECT}/locations/{location}/batchPredictionJobs?pageSize=100"
            if page_token:
                url += "&pageToken=" + urllib.parse.quote(page_token, safe="")
            page = fetch(url, access_token)
            for job in page.get("batchPredictionJobs", []):
                jobs.append({"name": job["name"], "state": job.get("state"), "displayName": job.get("displayName")})
            page_token = page.get("nextPageToken", "")
            if not page_token:
                break
    report = {"recordedAt": datetime.now(timezone.utc).isoformat(), "cloudLock": cloud_lock, "cloudGeneration": generation, "jobs": jobs, "allJobsTerminal": all(job["state"] in terminal for job in jobs), "generationSent": False}
    write(WORK / "preflight.json", report)
    if not report["allJobsTerminal"]:
        raise coordinator.MutexError("Active/unknown project batch blocks generation")
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["preflight", "send"])
    parser.add_argument("--pack", default="tactical-stone-registered-v1")
    args = parser.parse_args()
    runner, reconciliation = runner_and_reconciliation()
    report = preflight(runner)
    if args.mode == "preflight":
        print(json.dumps({"preflight": "PASS", "allJobsTerminal": report["allJobsTerminal"], "generationSent": False, "reconciliation": reconciliation}))
        return
    pack = (WORK / args.pack).resolve()
    if pack.parent != WORK.resolve():
        raise ValueError("Pack must be directly within this repair namespace")
    metadata = read(pack / "prepared.json")
    wire = (pack / "prepared-wire.json").read_bytes()
    if hashlib.sha256(wire).hexdigest() != metadata["wireBodySHA256"]:
        raise ValueError("Prepared wire hash drift")
    if hashlib.sha256((ROOT / "src/data/implementation-contract.json").read_bytes()).hexdigest() != metadata["contractSHA256"]:
        raise ValueError("Frozen geometry changed after preparation")
    for source in metadata["inputs"]:
        if hashlib.sha256((ROOT / source["path"]).read_bytes()).hexdigest() != source["sha256"]:
            raise ValueError("Prepared input changed")
    bound = coordinator.estimate_upper_bound_usd(metadata["resolution"], metadata["inputImages"], metadata["promptChars"])
    if metadata["reservationUSD"] < bound:
        raise coordinator.BudgetError("Reservation below conservative output bound")
    runner.acquire_mutex()
    try:
        result = runner.execute_prepared(pack, wire, metadata, metadata["reservationUSD"])
        if result["status"] == "SUCCEEDED":
            response = read(Path(result["rawResponse"]))
            outputs = []
            for candidate in response.get("candidates", []):
                for part in candidate.get("content", {}).get("parts", []):
                    inline = part.get("inlineData")
                    if not inline:
                        continue
                    native = base64.b64decode(inline["data"], validate=True)
                    decoded = Image.open(io.BytesIO(native))
                    decoded.load()
                    extension = ".png" if decoded.format == "PNG" else ".jpg" if decoded.format == "JPEG" else None
                    if extension is None:
                        raise ValueError("Unexpected native image format; raw response retained")
                    destination = pack / f"native-{len(outputs) + 1}{extension}"
                    destination.write_bytes(native)
                    outputs.append({"path": str(destination), "sha256": hashlib.sha256(native).hexdigest(), "size": list(decoded.size), "format": decoded.format})
            result.update({"outputs": outputs, "usageMetadata": response.get("usageMetadata"), "visualAcceptance": "NOT_TESTED", "bindingChanged": False})
        write(pack / "result.json", result)
        print(json.dumps(result))
    finally:
        runner.release_mutex()


if __name__ == "__main__":
    main()
