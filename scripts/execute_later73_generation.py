"""Executes the Authorized 73 Native 2K Generation Queue against Vertex AI.

Strict compliance:
- 20 seconds post-generation pacing.
- Definite HTTP 429 retry after >=60s or longer Retry-After.
- Atomic mutex and conditional GCS cloud lock CAS.
- Exact write-ahead body persistence and hash matching.
- Reuses existing successes without repurchasing.
- Role-specific pack checks (no terrain geometry for actor portraits).
- Independent asset promotion to assets/high-res/final-native2k/.
- Full crash durability and journal updates.
"""

from pathlib import Path
import json
import time
import os
import sys
import argparse
from datetime import datetime, timezone
from PIL import Image

ROOT = Path("c:/dev/ages-of-dominion-reborn")
sys.path.insert(0, str(ROOT / "scripts"))

from interactive_runner_continuity import (
    ContinuityRunner,
    MutexError,
    AuthError,
    UnknownLiabilityError,
    sha256_file,
    sha256_bytes,
    PLAN_PROD,
    MUTEX_FILE,
    PACING_FILE,
    BUDGET_FILE,
    PROJECT,
    ACCOUNT,
    BUCKET,
    LOCK_OBJECT,
    MODEL,
    ENDPOINT
)

EXEC_MANIFEST_FILE = ROOT / "docs/plan/IMAGE-LATER73-EXECUTION-MANIFEST-2026-10-04.json"
JOURNAL_FILE = PLAN_PROD / "interactive-2k-later73-journal.json"
FINAL_NATIVE2K_DIR = ROOT / "assets/high-res/final-native2k"

def main():
    parser = argparse.ArgumentParser(description="Execute Later 73 Native 2K Generation")
    parser.add_argument("--limit", type=int, default=73, help="Max items to process in this run")
    parser.add_argument("--start-order", type=int, default=1, help="Order index to start from")
    parser.add_argument("--dry-run", action="store_true", help="Validate without live API dispatch")
    parser.add_argument("--retry-unknown", action="store_true", help="Authorize execution of items currently in UNKNOWN or crash state")
    parser.add_argument("--target-ids", type=str, default=None, help="Comma-separated list of specific item IDs to process")
    args = parser.parse_args()

    print("=" * 80)
    print(f"STARTING LATER 73 NATIVE 2K GENERATION RUN: {datetime.now(timezone.utc).isoformat()}")
    print(f"Project: {PROJECT} | Account: {ACCOUNT} | Model: {MODEL}")
    print(f"Pacing: 20s gap | 429 Retry: >=60s | Target: 2048x2048 1:1")
    print(f"Limit: {args.limit} | Start Order: {args.start_order} | Dry run: {args.dry_run}")
    print("=" * 80)
    sys.stdout.flush()

    if not EXEC_MANIFEST_FILE.exists():
        print(f"[ERROR] Execution manifest missing: {EXEC_MANIFEST_FILE}")
        sys.exit(1)

    exec_manifest = json.loads(EXEC_MANIFEST_FILE.read_text(encoding="utf-8"))
    items = exec_manifest.get("items", [])
    print(f"Loaded {len(items)} items from execution manifest.")

    FINAL_NATIVE2K_DIR.mkdir(parents=True, exist_ok=True)

    # Load or initialize durable journal
    if JOURNAL_FILE.exists():
        try:
            journal = json.loads(JOURNAL_FILE.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"[FATAL ERROR] Journal file exists but is malformed JSON: {e}")
            raise RuntimeError(f"Journal file exists but is malformed JSON: {e}. Fail closed to prevent history reset.")
    else:
        journal = {
            "runId": f"run-later73-{int(time.time())}",
            "startedAt": datetime.now(timezone.utc).isoformat(),
            "attempts": [],
            "summary": {
                "totalSelected": len(items),
                "generated": 0,
                "reused": 0,
                "consumedFailed": 0,
                "blocked": 0,
                "unfunded": 0,
                "unknown": 0,
                "totalCostUSD": 0.0,
                "promptTokens": 0,
                "candidateTokens": 0
            }
        }

    # Initialize runner
    runner = ContinuityRunner(
        owner_base="image-executor-later73",
        cloud_lock_enabled=not args.dry_run
    )

    # Acquire atomic mutex & cloud CAS
    print(f"Acquiring atomic mutex (Owner: {runner.owner_id})...")
    sys.stdout.flush()
    try:
        runner.acquire_mutex()
        print(f"[MUTEX ACQUIRED] Lock active on PID {runner.pid}")
    except MutexError as me:
        print(f"[ABORT] Cannot acquire mutex: {me}")
        sys.exit(1)

    processed_count = 0
    halt_reason = None

    try:
        for idx, item in enumerate(items):
            gid = item["group"]
            order = item["order"]
            cid = item["id"]

            if order < args.start_order:
                continue
            if args.target_ids:
                targets = [t.strip() for t in args.target_ids.split(",") if t.strip()]
                if cid not in targets:
                    continue
            if processed_count >= args.limit:
                print(f"\n[LIMIT REACHED] Processed limit of {args.limit} items reached.")
                break

            print("\n" + "-" * 70)
            print(f"[{processed_count + 1}/{args.limit}] Processing: {cid} (Group: {gid}, Order: {order})")
            sys.stdout.flush()

            pack_dir = ROOT / item["localPackDir"]
            pack_dir.mkdir(parents=True, exist_ok=True)

            # 1. Role-specific Pack Validation
            role_chk = runner.check_role_pack(pack_dir, item)
            if not role_chk["pass"]:
                print(f"  -> [BLOCKED] Pack checks failed: {role_chk['reason']}")
                journal["summary"]["blocked"] += 1
                journal["attempts"].append({
                    "id": cid,
                    "order": order,
                    "group": gid,
                    "status": "BLOCKED_PACK_VALIDATION_FAILURE",
                    "reason": role_chk["reason"],
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
                continue

            # 2. Check Budget Headroom Before Call
            # Current ledger + this reservation must be <= $80.00
            current_committed = 62.8496 + journal["summary"]["totalCostUSD"]
            if current_committed + 0.143612 > 80.00:
                print(f"  -> [UNFUNDED] Hard cap $80.00 would be breached! Current committed: ${current_committed:.4f}")
                journal["summary"]["unfunded"] += 1
                halt_reason = "BUDGET_HARD_CAP_HEADROOM_EXHAUSTED"
                break

            if args.dry_run:
                print(f"  -> [DRY RUN] Pack validated. Skipping API call.")
                processed_count += 1
                continue

            # 3. Execute Request via Continuity Runner
            try:
                res = runner.execute_request(
                    pack_dir=pack_dir,
                    item_meta=item,
                    reservation_usd=0.143612,
                    retry_unknown=args.retry_unknown
                )
            except AuthError as ae:
                print(f"  -> [AUTH HALT] {ae}")
                halt_reason = f"AUTH_ERROR: {ae}"
                break
            except UnknownLiabilityError as ue:
                print(f"  -> [UNKNOWN HALT] {ue}")
                journal["summary"]["unknown"] += 1
                halt_reason = f"UNKNOWN_LIABILITY: {ue}"
                break
            except Exception as ex:
                print(f"  -> [ERROR] Unexpected execution failure: {ex}")
                halt_reason = f"UNEXPECTED_ERROR: {ex}"
                break

            status = res.get("status")
            if status == "REUSED_EXISTING_SUCCESS":
                journal["summary"]["reused"] += 1
                # Copy to final-native2k if not already there
                final_path = FINAL_NATIVE2K_DIR / f"{cid}.png"
                out_path = pack_dir / "output.png"
                if not final_path.exists() and out_path.exists():
                    final_path.write_bytes(out_path.read_bytes())
                journal["attempts"].append({
                    "id": cid,
                    "order": order,
                    "group": gid,
                    "status": "REUSED_EXISTING_SUCCESS",
                    "sha256": res.get("sha256"),
                    "costUSD": 0.0,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
                processed_count += 1

            elif status == "SUCCEEDED":
                journal["summary"]["generated"] += 1
                cost = res.get("costUSD", 0.0)
                journal["summary"]["totalCostUSD"] += cost
                journal["summary"]["promptTokens"] += res.get("promptTokens", 0)
                journal["summary"]["candidateTokens"] += res.get("candidateTokens", 0)

                # Independent Asset Promotion to final-native2k
                out_path = pack_dir / "output.png"
                final_path = FINAL_NATIVE2K_DIR / f"{cid}.png"
                if out_path.exists():
                    final_path.write_bytes(out_path.read_bytes())
                    print(f"  -> [PROMOTED] Canonical 2K image promoted to {final_path.relative_to(ROOT)}")

                journal["attempts"].append({
                    "id": cid,
                    "order": order,
                    "group": gid,
                    "status": "SUCCEEDED",
                    "dimensions": res.get("dimensions"),
                    "sha256": res.get("sha256"),
                    "costUSD": cost,
                    "promptTokens": res.get("promptTokens"),
                    "candidateTokens": res.get("candidateTokens"),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
                processed_count += 1

            elif status == "CONSUMED_FAILED_NO_IMAGE":
                journal["summary"]["consumedFailed"] += 1
                cost = res.get("costUSD", 0.0)
                journal["summary"]["totalCostUSD"] += cost
                journal["attempts"].append({
                    "id": cid,
                    "order": order,
                    "group": gid,
                    "status": "CONSUMED_FAILED_NO_IMAGE",
                    "finishReason": res.get("finishReason"),
                    "costUSD": cost,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
                processed_count += 1

            elif status == "UNKNOWN_RETAINED_LIABILITY":
                journal["summary"]["unknown"] += 1
                journal["attempts"].append({
                    "id": cid,
                    "order": order,
                    "group": gid,
                    "status": "UNKNOWN_RETAINED_LIABILITY",
                    "costUSD": res.get("costUSD", 0.143612),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "note": "Unresolved in-flight crash from previous run; liability retained, skipped to avoid duplication."
                })
                processed_count += 1

            else:
                print(f"  -> Non-terminal or failed status: {status}")
                journal["attempts"].append({
                    "id": cid,
                    "order": order,
                    "group": gid,
                    "status": status,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })

            # Save journal atomically after each item
            temp_j = JOURNAL_FILE.with_suffix(JOURNAL_FILE.suffix + f".tmp.{os.getpid()}")
            temp_j.write_text(json.dumps(journal, indent=2), encoding="utf-8")
            os.replace(temp_j, JOURNAL_FILE)

    finally:
        # Compute reconciled unique ID status across attempts
        unique_status = {}
        for a in journal.get("attempts", []):
            cid = a.get("id")
            st = a.get("status")
            if st in ("SUCCEEDED", "REUSED_EXISTING_SUCCESS"):
                unique_status[cid] = "SUCCEEDED"
            elif cid not in unique_status:
                unique_status[cid] = st
        journal["summary"]["uniqueCompleted"] = sum(1 for s in unique_status.values() if s == "SUCCEEDED")
        journal["summary"]["uniqueTotal"] = len(unique_status)

        # Finalize atomically
        temp_j = JOURNAL_FILE.with_suffix(JOURNAL_FILE.suffix + f".tmp.{os.getpid()}")
        temp_j.write_text(json.dumps(journal, indent=2), encoding="utf-8")
        os.replace(temp_j, JOURNAL_FILE)

        if (halt_reason and "UNKNOWN" in halt_reason) or runner.unresolved_items or runner.has_retained_liabilities:
            print(f"\n[WARNING] Halting under UNKNOWN state or with unresolved items ({runner.unresolved_items})! Mutex and cloud lock will NOT be released.")
            runner.release_mutex(state="UNKNOWN")
        else:
            print(f"\nReleasing mutex cleanly (state: COMPLETED_CYCLE)...")
            runner.release_mutex(state="COMPLETED_CYCLE")

    print("\n" + "=" * 80)
    print("LATER 73 GENERATION EXECUTION SUMMARY:")
    print(f"Processed Count: {processed_count}")
    print(f"Generated (New): {journal['summary']['generated']}")
    print(f"Reused (Existing): {journal['summary']['reused']}")
    print(f"Consumed Failed (NO_IMAGE): {journal['summary']['consumedFailed']}")
    print(f"Blocked (Pack checks): {journal['summary']['blocked']}")
    print(f"Unfunded: {journal['summary']['unfunded']}")
    print(f"Unknown (Ambiguous): {journal['summary']['unknown']}")
    print(f"Run Spend: ${journal['summary']['totalCostUSD']:.4f} USD")
    print(f"Halt Reason: {halt_reason or 'NORMAL_COMPLETION'}")
    print("=" * 80)
    sys.stdout.flush()

if __name__ == "__main__":
    main()
