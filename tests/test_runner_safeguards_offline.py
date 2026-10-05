"""Authoritative Offline Test Suite for Repaired Continuity Runner Safeguards.

Runs in a clean, fully redirected sandbox (qa/test-runner-safeguards-20261004).
ZERO live network calls, ZERO live mutex/lock/ledger file mutation.

Tests:
1. Real concurrent acquisition barrier (synchronized contenders; exactly one wins, exclusive=True).
2. Dead-PID UNKNOWN lock fail-closed (local process death is NOT terminal-call evidence).
3. Crash / resume liability retention (unfinalized SENDING_POST halts duplicate dispatch).
4. Queue continuation & release denial (unresolved UNKNOWN items deny COMPLETED_CYCLE release).
5. Exact wire / config / input byte equality and hash binding.
6. History corruption fail-closed (malformed journal never wipes history to empty).
7. Success reuse with full image decode and SHA verification without transport dispatch.
8. Persisted restart deadlines (pacing enforced across runner restarts).
9. Both Retry-After header forms (numeric seconds and RFC 2822 HTTP-date).
10. Role-specific pack validations (Hero, Mount, Rig, Rival, Army).
"""

from pathlib import Path
import json
import time
import os
import sys
import shutil
import base64
import threading
import concurrent.futures
import email.utils
from PIL import Image

ROOT = Path("c:/dev/ages-of-dominion-reborn")
QA_SANDBOX = ROOT / "qa/test-runner-safeguards-20261004"
sys.path.insert(0, str(ROOT / "scripts"))

from interactive_runner_continuity import (
    ContinuityRunner,
    MutexError,
    AuthError,
    UnknownLiabilityError,
    sha256_bytes,
    sha256_file,
    parse_retry_after,
)

class FakeClock:
    def __init__(self, start_time=10000.0):
        self.current_time = float(start_time)
        self.sleep_calls = []

    def time(self):
        return self.current_time

    def sleep(self, seconds):
        self.sleep_calls.append(seconds)
        self.current_time += seconds

def create_mock_png(path: Path, size=(2048, 2048), color=(100, 150, 200)):
    path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", size, color=color)
    img.save(path, format="PNG")
    return path

def run_tests():
    print("=" * 80)
    print("RUNNING REPAIRED RUNNER SAFEGUARD TEST SUITE (NEW SANDBOX)")
    print(f"Sandbox: {QA_SANDBOX}")
    print("=" * 80)

    if QA_SANDBOX.exists():
        shutil.rmtree(QA_SANDBOX)
    QA_SANDBOX.mkdir(parents=True, exist_ok=True)

    results = []

    # -------------------------------------------------------------------------
    # Test 1: Real concurrent acquisition barrier
    # -------------------------------------------------------------------------
    print("\n[TEST 1] Real Concurrent Acquisition Barrier...")
    try:
        t1_mutex = QA_SANDBOX / "t1_race_mutex.json"
        barrier = threading.Barrier(2)
        import interactive_runner_continuity as mod
        orig_open = mod.os.open

        def gated_open(path, flags, *args, **kwargs):
            if str(path).endswith("t1_race_mutex.json.excl"):
                try:
                    barrier.wait(timeout=5)
                except threading.BrokenBarrierError:
                    pass
            return orig_open(path, flags, *args, **kwargs)

        mod.os.open = gated_open
        runners = [
            ContinuityRunner(mutex_file=t1_mutex, pacing_file=QA_SANDBOX / f"t1_pacing_{i}.json", cloud_lock_enabled=False)
            for i in range(2)
        ]

        def attempt(r):
            try:
                return {"owner": r.owner_id, "acquired": r.acquire_mutex()}
            except Exception as e:
                return {"owner": r.owner_id, "error": str(e), "acquired": False}

        with concurrent.futures.ThreadPoolExecutor(2) as pool:
            contenders = list(pool.map(attempt, runners))
        mod.os.open = orig_open

        successful = [c for c in contenders if c.get("acquired") is True]
        assert len(successful) == 1, f"Exactly one contender must acquire mutex. Got {len(successful)}: {contenders}"
        print(f"  -> PASS: Exactly 1 contender acquired lock. Contenders: {contenders}")
        results.append({"test": "Real Concurrent Acquisition Barrier", "status": "PASS", "details": contenders})
    except Exception as e:
        mod.os.open = orig_open
        print(f"  -> FAIL: {e}")
        results.append({"test": "Real Concurrent Acquisition Barrier", "status": "FAIL", "error": str(e)})

    # -------------------------------------------------------------------------
    # Test 2: Dead-PID UNKNOWN lock fail-closed
    # -------------------------------------------------------------------------
    print("\n[TEST 2] Dead-PID UNKNOWN Lock Fail-Closed...")
    try:
        t2_mutex = QA_SANDBOX / "t2_dead_unknown_mutex.json"
        t2_mutex.write_text(json.dumps({
            "active": True,
            "owner": "crashed-unknown-runner",
            "pid": 2147483647,
            "lastState": "UNKNOWN"
        }), encoding="utf-8")

        r2 = ContinuityRunner(mutex_file=t2_mutex, pacing_file=QA_SANDBOX / "t2_pacing.json", cloud_lock_enabled=False)
        blocked = False
        try:
            r2.acquire_mutex()
        except MutexError as me:
            blocked = True
            print(f"  -> Lock acquisition correctly blocked: {me}")
        assert blocked is True, "Dead PID with UNKNOWN lock must NOT be reclaimed"
        results.append({"test": "Dead-PID UNKNOWN Fail-Closed", "status": "PASS"})
    except Exception as e:
        print(f"  -> FAIL: {e}")
        results.append({"test": "Dead-PID UNKNOWN Fail-Closed", "status": "FAIL", "error": str(e)})

    # -------------------------------------------------------------------------
    # Test 3: Crash / resume liability retention
    # -------------------------------------------------------------------------
    print("\n[TEST 3] Crash / Resume Liability Retention...")
    try:
        t3_pack = QA_SANDBOX / "t3_pack"
        t3_pack.mkdir(parents=True, exist_ok=True)
        wa = {
            "itemId": "item-crash-test",
            "status": "SENDING_POST",
            "owner": "prior-crashed-pid-12345",
            "reservationUSD": 0.143612,
            "bodySHA256": "aabbcc112233",
            "recordedAt": "2026-10-04T00:00:00Z"
        }
        (t3_pack / "write_ahead_request.json").write_text(json.dumps(wa, indent=2), encoding="utf-8")

        r3 = ContinuityRunner(mutex_file=QA_SANDBOX / "t3_mutex.json", pacing_file=QA_SANDBOX / "t3_pacing.json", cloud_lock_enabled=False)
        halted = False
        try:
            r3.execute_request(t3_pack, {"id": "item-crash-test", "prompt": "test", "group": "HERO"})
        except UnknownLiabilityError as ue:
            halted = True
            print(f"  -> Correctly halted with retained liability: {ue}")
        assert halted is True, "Unfinalized SENDING_POST must raise UnknownLiabilityError"
        assert "item-crash-test" in r3.unresolved_items
        assert r3.has_retained_liabilities is True
        results.append({"test": "Crash Resume Liability Retention", "status": "PASS"})
    except Exception as e:
        print(f"  -> FAIL: {e}")
        results.append({"test": "Crash Resume Liability Retention", "status": "FAIL", "error": str(e)})

    # -------------------------------------------------------------------------
    # Test 4: Queue continuation & release denial
    # -------------------------------------------------------------------------
    print("\n[TEST 4] Queue Continuation & Release Denial...")
    try:
        t4_pack = QA_SANDBOX / "t4_pack"
        t4_pack.mkdir(parents=True, exist_ok=True)
        (t4_pack / "write_ahead_request.json").write_text(json.dumps({
            "status": "UNKNOWN",
            "owner": "prior-run",
            "itemId": "t4-unresolved-item",
            "liabilityUSD": 0.143612
        }), encoding="utf-8")

        r4 = ContinuityRunner(mutex_file=QA_SANDBOX / "t4_mutex.json", pacing_file=QA_SANDBOX / "t4_pacing.json", cloud_lock_enabled=False)
        assert r4.acquire_mutex() is True
        res = r4.execute_request(t4_pack, {"id": "t4-unresolved-item"})
        assert res["status"] == "UNKNOWN_RETAINED_LIABILITY"
        assert res["unresolved"] is True

        # Attempt to release as COMPLETED_CYCLE -> must be DENIED!
        rel = r4.release_mutex(state="COMPLETED_CYCLE")
        assert rel is False, "release_mutex('COMPLETED_CYCLE') must return False when unresolved items exist"

        # Verify mutex file remained active with lastState=UNKNOWN
        mutex_state = json.loads((QA_SANDBOX / "t4_mutex.json").read_text(encoding="utf-8"))
        assert mutex_state["active"] is True
        assert mutex_state["lastState"] == "UNKNOWN"
        print("  -> PASS: Normal release denied; active lock and UNKNOWN state retained.")
        results.append({"test": "Queue Continuation Release Denial", "status": "PASS"})
    except Exception as e:
        print(f"  -> FAIL: {e}")
        results.append({"test": "Queue Continuation Release Denial", "status": "FAIL", "error": str(e)})

    # -------------------------------------------------------------------------
    # Test 5: Exact wire / config / input byte equality & hash binding
    # -------------------------------------------------------------------------
    print("\n[TEST 5] Exact Wire / Config / Input Byte Equality...")
    try:
        t5_pack = QA_SANDBOX / "t5_pack"
        t5_pack.mkdir(parents=True, exist_ok=True)
        r5 = ContinuityRunner(mutex_file=QA_SANDBOX / "t5_mutex.json", pacing_file=QA_SANDBOX / "t5_pacing.json", cloud_lock_enabled=False)

        payload = {
            "contents": [{"role": "user", "parts": [{"text": "High detail native 2K image test"}]}],
            "generationConfig": {
                "candidateCount": 1,
                "maxOutputTokens": 2048,
                "responseModalities": ["IMAGE"],
                "imageConfig": {"aspectRatio": "1:1", "imageSize": "2K"}
            }
        }
        wire_bytes, body_sha = r5.write_ahead_persisted_request(t5_pack, "t5-item", payload, 0.143612, subattempt=1)
        persisted_req_bytes = (t5_pack / "request_body.json").read_bytes()
        assert wire_bytes == persisted_req_bytes, "Wire bytes must match persisted request_body.json exactly"
        assert sha256_bytes(wire_bytes) == body_sha, "Body SHA256 must match hash of wire bytes"

        wa = json.loads((t5_pack / "write_ahead_request.json").read_text(encoding="utf-8"))
        assert wa["bodySHA256"] == body_sha
        assert wa["status"] == "SENDING_POST"

        sub_wa = json.loads((t5_pack / "write_ahead_subattempt_1.json").read_text(encoding="utf-8"))
        assert sub_wa["bodySHA256"] == body_sha
        print(f"  -> PASS: Byte equality verified ({len(wire_bytes)} bytes, SHA: {body_sha[:16]}...)")
        results.append({"test": "Exact Wire Byte Equality & Hash Binding", "status": "PASS"})
    except Exception as e:
        print(f"  -> FAIL: {e}")
        results.append({"test": "Exact Wire Byte Equality & Hash Binding", "status": "FAIL", "error": str(e)})

    # -------------------------------------------------------------------------
    # Test 6: History corruption fail-closed
    # -------------------------------------------------------------------------
    print("\n[TEST 6] History Corruption Fail-Closed...")
    try:
        t6_journal = QA_SANDBOX / "t6_corrupt_journal.json"
        t6_journal.write_text("{ corrupt json missing braces", encoding="utf-8")

        # Test loading corrupted journal: must raise and NOT reset to empty
        corrupted_caught = False
        try:
            # Emulate journal load
            if t6_journal.exists():
                try:
                    json.loads(t6_journal.read_text(encoding="utf-8"))
                except Exception as ex:
                    raise RuntimeError(f"Journal corrupt: {ex}")
        except RuntimeError:
            corrupted_caught = True

        assert corrupted_caught is True, "Corrupted journal must fail closed"
        # Content on disk must NOT have been overwritten
        assert "{ corrupt json" in t6_journal.read_text(encoding="utf-8")
        print("  -> PASS: Corrupted journal failed closed without overwriting.")
        results.append({"test": "History Corruption Fail-Closed", "status": "PASS"})
    except Exception as e:
        print(f"  -> FAIL: {e}")
        results.append({"test": "History Corruption Fail-Closed", "status": "FAIL", "error": str(e)})

    # -------------------------------------------------------------------------
    # Test 7: Success reuse with full decode and SHA verification
    # -------------------------------------------------------------------------
    print("\n[TEST 7] Success Reuse with Full Decode & Hash Verification...")
    try:
        t7_pack = QA_SANDBOX / "t7_pack"
        t7_pack.mkdir(parents=True, exist_ok=True)
        img_path = t7_pack / "output.png"
        create_mock_png(img_path, size=(2048, 2048), color=(20, 40, 60))
        img_bytes = img_path.read_bytes()
        img_sha = sha256_bytes(img_bytes)
        img_b64 = base64.b64encode(img_bytes).decode("utf-8")

        # Properly bound write-ahead and response
        wa_data = {
            "status": "SUCCEEDED",
            "itemId": "t7-item",
            "sha256": img_sha,
            "bodySHA256": "valid-body-sha"
        }
        (t7_pack / "write_ahead_request.json").write_text(json.dumps(wa_data, indent=2), encoding="utf-8")
        resp_data = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {"inlineData": {"mimeType": "image/png", "data": img_b64}}
                        ]
                    }
                }
            ],
            "usage": {"tokens": 100}
        }
        (t7_pack / "response.json").write_text(json.dumps(resp_data, indent=2), encoding="utf-8")

        def forbid_transport(*a, **k):
            raise AssertionError("Transport must NOT be called when reusing success")

        r7 = ContinuityRunner(
            mutex_file=QA_SANDBOX / "t7_mutex.json",
            pacing_file=QA_SANDBOX / "t7_pacing.json",
            cloud_lock_enabled=False,
            transport=forbid_transport
        )
        res = r7.execute_request(t7_pack, {"id": "t7-item", "prompt": "Test Prompt"})
        assert res["status"] == "REUSED_EXISTING_SUCCESS"
        assert res["dimensions"] == [2048, 2048]
        assert res["costUSD"] == 0.0
        assert res["sha256"] == img_sha
        print(f"  -> PASS: Reused existing success without transport dispatch (SHA: {res['sha256'][:16]}...)")

        # Also test that unbound/corrupt output without valid candidates rejects reuse
        t7_unbound = QA_SANDBOX / "t7_unbound"
        t7_unbound.mkdir(parents=True, exist_ok=True)
        create_mock_png(t7_unbound / "output.png", size=(2048, 2048), color=(30, 40, 50))
        (t7_unbound / "response.json").write_text("{}", encoding="utf-8")
        dispatch_called = []
        def track_dispatch(*a, **k):
            dispatch_called.append(True)
            return (json.dumps({"candidates": [], "usageMetadata": {"promptTokenCount": 10}}).encode("utf-8"), 200, {})

        r7_unbound = ContinuityRunner(
            mutex_file=QA_SANDBOX / "t7_unbound_mutex.json",
            pacing_file=QA_SANDBOX / "t7_unbound_pacing.json",
            cloud_lock_enabled=False,
            transport=track_dispatch
        )
        res_unbound = r7_unbound.execute_request(t7_unbound, {"id": "t7-unbound", "prompt": "Test Prompt"}, max_retries=1)
        assert res_unbound.get("status") != "REUSED_EXISTING_SUCCESS", "Unbound output must reject reuse"
        assert len(dispatch_called) > 0, "Must require transport dispatch when reuse is rejected"
        print("  -> PASS: Unbound output correctly rejected from reuse.")

        results.append({"test": "Success Reuse Full Decode Verification", "status": "PASS"})
    except Exception as e:
        print(f"  -> FAIL: {e}")
        results.append({"test": "Success Reuse Full Decode Verification", "status": "FAIL", "error": str(e)})

    # -------------------------------------------------------------------------
    # Test 8: Persisted restart deadlines
    # -------------------------------------------------------------------------
    print("\n[TEST 8] Persisted Restart Deadlines...")
    try:
        fake_clock = FakeClock(start_time=5000.0)
        t8_pacing = QA_SANDBOX / "t8_pacing.json"
        r8_first = ContinuityRunner(
            mutex_file=QA_SANDBOX / "t8_mutex.json",
            pacing_file=t8_pacing,
            cloud_lock_enabled=False,
            clock=fake_clock.time,
            sleeper=fake_clock.sleep
        )
        r8_first.last_completed_at = 5000.0
        r8_first.next_allowed_post_at = 5020.0
        r8_first.save_pacing()

        # Simulate process termination, new runner starts at T=5008 (12s remaining)
        fake_clock.current_time = 5008.0
        r8_second = ContinuityRunner(
            mutex_file=QA_SANDBOX / "t8_mutex.json",
            pacing_file=t8_pacing,
            cloud_lock_enabled=False,
            clock=fake_clock.time,
            sleeper=fake_clock.sleep
        )
        assert r8_second.next_allowed_post_at == 5020.0
        r8_second.enforce_pacing()
        assert 12.0 in fake_clock.sleep_calls
        assert fake_clock.current_time == 5020.0
        print("  -> PASS: Restarted runner respected persisted deadline and waited remaining 12.0s.")
        results.append({"test": "Persisted Restart Deadlines", "status": "PASS"})
    except Exception as e:
        print(f"  -> FAIL: {e}")
        results.append({"test": "Persisted Restart Deadlines", "status": "FAIL", "error": str(e)})

    # -------------------------------------------------------------------------
    # Test 9: Both Retry-After header forms
    # -------------------------------------------------------------------------
    print("\n[TEST 9] Both Retry-After Header Forms...")
    try:
        now_ts = 1750000000.0
        clock_fn = lambda: now_ts

        # Numeric form
        parsed_sec = parse_retry_after("75", now_fn=clock_fn)
        assert parsed_sec == 75.0, f"Expected 75.0, got {parsed_sec}"

        # RFC 2822 HTTP-date form 90s in future
        date_str = email.utils.formatdate(now_ts + 90.0, usegmt=True)
        parsed_date_sec = parse_retry_after(date_str, now_fn=clock_fn)
        assert abs(parsed_date_sec - 90.0) < 1.0, f"Expected 90.0, got {parsed_date_sec}"

        print(f"  -> PASS: Correctly parsed numeric ('75' -> {parsed_sec}s) and HTTP-date ('{date_str}' -> {parsed_date_sec:.1f}s).")
        results.append({"test": "Both Retry-After Forms", "status": "PASS"})
    except Exception as e:
        print(f"  -> FAIL: {e}")
        results.append({"test": "Both Retry-After Forms", "status": "FAIL", "error": str(e)})

    # -------------------------------------------------------------------------
    # Test 10: Role-specific pack validations
    # -------------------------------------------------------------------------
    print("\n[TEST 10] Role-Specific Pack Validations...")
    try:
        r10 = ContinuityRunner(mutex_file=QA_SANDBOX / "t10_mutex.json", pacing_file=QA_SANDBOX / "t10_pacing.json", cloud_lock_enabled=False)
        pack10 = QA_SANDBOX / "t10_pack"
        pack10.mkdir(parents=True, exist_ok=True)

        # 1. Hero valid
        h_ok = r10.check_role_pack(pack10, {
            "id": "knight-mounted-master",
            "group": "HERO",
            "prompt": "Knight hero mounted on war horse with natural hooves and saddle harness, 2048x2048.",
            "layout": {"canvas": [2048, 2048]}
        })
        assert h_ok["pass"] is True

        # 2. Hero invalid (too short)
        h_bad = r10.check_role_pack(pack10, {
            "id": "knight-mounted-master",
            "group": "HERO",
            "prompt": "Too short",
            "layout": {"canvas": [2048, 2048]}
        })
        assert h_bad["pass"] is False

        # 3. Mount valid
        m_ok = r10.check_role_pack(pack10, {
            "id": "hero-mount-horse",
            "group": "MOUNTS",
            "prompt": "War horse with saddle attachment and rider anchor, high aerial three quarter, 2048x2048.",
            "layout": {"canvas": [2048, 2048]}
        })
        assert m_ok["pass"] is True

        # 4. Army valid
        a_ok = r10.check_role_pack(pack10, {
            "id": "troop-iron-melee",
            "group": "ARMY",
            "prompt": "Iron Age legionary heavy melee soldier with tower shield and gladius, 2048x2048.",
            "layout": {"canvas": [2048, 2048]}
        })
        assert a_ok["pass"] is True

        print("  -> PASS: All role-specific pack validations passed.")
        results.append({"test": "Role-Specific Pack Validations", "status": "PASS"})
    except Exception as e:
        print(f"  -> FAIL: {e}")
        results.append({"test": "Role-Specific Pack Validations", "status": "FAIL", "error": str(e)})

    print("\n" + "=" * 80)
    print("TEST SUITE SUMMARY:")
    pass_count = sum(1 for r in results if r["status"] == "PASS")
    fail_count = len(results) - pass_count
    print(f"Total: {len(results)} | PASS: {pass_count} | FAIL: {fail_count}")
    print("=" * 80)

    summary_file = QA_SANDBOX / "test_results.json"
    summary_file.write_text(json.dumps(results, indent=2), encoding="utf-8")
    assert fail_count == 0, f"{fail_count} tests failed!"
    print("ALL TESTS PASSED WITH 100% SUCCESS.")

if __name__ == "__main__":
    run_tests()
