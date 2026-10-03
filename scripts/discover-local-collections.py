"""Read-only count of local production originals. Writes one QA discovery file.

Does not call a provider, edit a manifest, lock, guide, or the budget ledger.
"""
from pathlib import Path
import hashlib, json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "qa/recovery-executor-20261003/collection-discovery-post-candidate.json"

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

rows = []
mismatches = []
batches = []
for batch in sorted((ROOT / "assets/production").iterdir()):
    if not batch.is_dir():
        continue
    report_path = batch / "collection-report.json"
    images = list((batch / "images").glob("*")) if (batch / "images").is_dir() else []
    entry = {"batch": batch.name, "imageFiles": len(images), "report": report_path.exists()}
    if report_path.exists():
        report = json.loads(report_path.read_text(encoding="utf-8"))
        entry["outputs"] = len(report.get("outputs", []))
        for output in report.get("outputs", []):
            path = ROOT / output["file"]
            digest = sha(path) if path.exists() else None
            match = digest == output["sha256"]
            if not match:
                mismatches.append({"batch": batch.name, "id": output["id"], "file": output["file"]})
            rows.append({"batch": batch.name, "id": output["id"], "sha256": output["sha256"], "hashMatch": match})
    batches.append(entry)

ids = {row["id"] for row in rows}
ledger = json.loads((ROOT / "docs/plan/image-production/budget-ledger.json").read_text(encoding="utf-8"))
lock_path = ROOT / "docs/plan/image-production/active-batch.lock.json"
lock = json.loads(lock_path.read_text(encoding="utf-8")) if lock_path.exists() else {}
holds = ledger["historicalMock"]["conservativeReservation"] + sum(item["reservedUSD"] for item in ledger["batches"])
discovery = {
    "visualStatus": "UNVERIFIED",
    "ownerAcceptance": "NOT_OWNER_ACCEPTED",
    "runtimeApproved": False,
    "originals": len(rows),
    "distinctIds": len(ids),
    "hashMismatches": len(mismatches),
    "mismatchRows": mismatches,
    "batches": batches,
    "ledgerBatches": [item["id"] for item in ledger["batches"]],
    "holdsUSD": holds,
    "safetyReserveUSD": ledger["safetyReserve"],
    "hardCapUSD": ledger["hardCap"],
    "holdsPlusReserveUSD": holds + ledger["safetyReserve"],
    "billedTotal": ledger.get("billedTotal"),
    "billingStatus": ledger.get("billingStatus"),
    "reconciliationCovers": "01-13" if "reconciledBatches01To13TotalUSD" in ledger.get("reconciliationTrail", {}) else "unknown",
    "lock": {
        "batch_id": lock.get("batch_id"),
        "state": lock.get("state"),
        "workflow_state": lock.get("workflow_state"),
        "submittedAt": lock.get("submittedAt"),
        "reservedUSD": lock.get("reservedUSD"),
    },
    "note": "Counts come from local collection reports and file hashes. They are not visual approval and not a live provider query.",
}
OUT.write_text(json.dumps(discovery, indent=2) + "\n", encoding="utf-8")
print(json.dumps({k: discovery[k] for k in ("originals", "distinctIds", "hashMismatches", "holdsPlusReserveUSD", "lock")}, indent=2))
