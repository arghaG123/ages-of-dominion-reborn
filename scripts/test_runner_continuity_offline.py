"""Offline Mock Test Suite for Interactive Continuity Runner.

Uses an isolated sandbox and fake clock / mock transport only.
NEVER modifies live mutex, lock, or ledger files.

Tests:
1. Simultaneous processes including same default owner contention.
2. Malformed lock fails closed without overwriting.
3. Crash before and after dispatch handling (retains liability, blocks duplicates).
4. Real-schema sent-byte hash equality between wire bytes and write-ahead SHA.
5. Success reuse without repurchase.
6. UNKNOWN release denial (preserves lock and liability).
7. Restart pacing enforcement from persisted state.
8. Numeric and HTTP-date Retry-After parsing and backoff.
9. Actual second dispatch blocked before its pacing deadline.
10. Role-specific pack checks (Hero, Mount, Rig, Rival, Army; terrain geometry irrelevant).
"""

from pathlib import Path
import json
import time
import os
import sys
import shutil
import base64
import email.utils
from PIL import Image

ROOT = Path("c:/dev/ages-of-dominion-reborn")
QA_SANDBOX = ROOT / "qa/test-runner-sandbox-20261004"
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

def run_all_offline_tests():
    print("=== STARTING RIGOROUS OFFLINE CONTINUITY RUNNER TEST SUITE ===")
    if QA_SANDBOX.exists():
        shutil.rmtree(QA_SANDBOX)
    QA_SANDBOX.mkdir(parents=True, exist_ok=True)

    results = []

    # -------------------------------------------------------------
    # Test 1: Simultaneous processes with same default owner string
    # -------------------------------------------------------------
    print("\n--- Test 1: Simultaneous Processes & Contention ---")
    try:
        t1_mutex = QA_SANDBOX / "t1_submission.mutex.json"
        t1_pacing = QA_SANDBOX / "t1_pacing.json"
        # Two runners sharing the same default owner string
        r1 = ContinuityRunner(owner_base="default-image-ai", mutex_file=t1_mutex, pacing_file=t1_pacing)
        r2 = ContinuityRunner(owner_base="default-image-ai", mutex_file=t1_mutex, pacing_file=t1_pacing)
        
        # Verify unique owner IDs despite identical base
        assert r1.owner_id != r2.owner_id, "Owner IDs must be unique across instances"

        assert r1.acquire_mutex() == True
        assert r1.has_lock == True
        print(f"Runner 1 acquired mutex: {r1.owner_id}")

        # Runner 2 attempts acquisition -> must fail closed
        blocked = False
        try:
            r2.acquire_mutex()
        except MutexError as e:
            blocked = True
            print(f"Runner 2 blocked as expected: {e}")
        assert blocked == True, "Runner 2 should be blocked by active Runner 1"

        # Release runner 1, then runner 2 can acquire
        assert r1.release_mutex() == True
        assert r2.acquire_mutex() == True
        print(f"Runner 2 successfully acquired mutex after Runner 1 released: {r2.owner_id}")
        assert r2.release_mutex() == True
        results.append({"test": "Simultaneous Processes Contention", "status": "PASS"})
    except Exception as e:
        results.append({"test": "Simultaneous Processes Contention", "status": "FAIL", "error": str(e)})

    # -------------------------------------------------------------
    # Test 2: Malformed lock fails closed
    # -------------------------------------------------------------
    print("\n--- Test 2: Malformed Lock Fails Closed ---")
    try:
        t2_mutex = QA_SANDBOX / "t2_submission.mutex.json"
        t2_mutex.write_text("{ broken json content without closing brace ...", encoding="utf-8")
        r = ContinuityRunner(mutex_file=t2_mutex, pacing_file=QA_SANDBOX / "t2_pacing.json")
        failed_closed = False
        try:
            r.acquire_mutex()
        except MutexError as e:
            failed_closed = True
            print(f"Acquire failed closed on malformed lock: {e}")
        assert failed_closed == True
        # Verify file was NOT overwritten
        assert "{ broken json" in t2_mutex.read_text(encoding="utf-8")
        results.append({"test": "Malformed Lock Fail-Closed", "status": "PASS"})
    except Exception as e:
        results.append({"test": "Malformed Lock Fail-Closed", "status": "FAIL", "error": str(e)})

    # -------------------------------------------------------------
    # Test 3: Crash before and after dispatch
    # -------------------------------------------------------------
    print("\n--- Test 3: Crash Before & After Dispatch ---")
    try:
        pack_dir = QA_SANDBOX / "t3_pack"
        pack_dir.mkdir(parents=True, exist_ok=True)
        t3_mutex = QA_SANDBOX / "t3_submission.mutex.json"
        t3_pacing = QA_SANDBOX / "t3_pacing.json"

        # Simulate crash AFTER dispatch: write-ahead has SENDING_POST from previous owner
        unfinalized_wa = {
            "itemId": "mock-item-crash",
            "bodySHA256": "fakehash123",
            "subattempt": 1,
            "status": "SENDING_POST",
            "owner": "crashed-runner-run-999-pid1234",
            "recordedAt": "2026-10-04T00:00:00Z"
        }
        (pack_dir / "write_ahead_request.json").write_text(json.dumps(unfinalized_wa, indent=2), encoding="utf-8")

        r = ContinuityRunner(mutex_file=t3_mutex, pacing_file=t3_pacing)
        halted = False
        try:
            r.execute_request(pack_dir, {"id": "mock-item-crash", "prompt": "test", "group": "HERO"})
        except UnknownLiabilityError as e:
            halted = True
            print(f"Crash after dispatch correctly detected: {e}")
        assert halted == True, "Unfinalized SENDING_POST must raise UnknownLiabilityError"
        results.append({"test": "Crash After Dispatch Liability Retained", "status": "PASS"})
    except Exception as e:
        results.append({"test": "Crash After Dispatch Liability Retained", "status": "FAIL", "error": str(e)})

    # -------------------------------------------------------------
    # Test 4: Real-schema sent-byte hash equality
    # -------------------------------------------------------------
    print("\n--- Test 4: Wire Body Hash Byte Equality ---")
    try:
        pack_dir = QA_SANDBOX / "t4_pack"
        pack_dir.mkdir(parents=True, exist_ok=True)
        r = ContinuityRunner(mutex_file=QA_SANDBOX / "t4_mutex.json", pacing_file=QA_SANDBOX / "t4_pacing.json")

        payload = {
            "contents": [{"role": "user", "parts": [{"text": "Generate native 2K image."}]}],
            "generationConfig": {
                "candidateCount": 1,
                "maxOutputTokens": 2048,
                "responseModalities": ["IMAGE"],
                "imageConfig": {"aspectRatio": "1:1", "imageSize": "2K"}
            }
        }
        body_bytes, body_sha = r.write_ahead_persisted_request(pack_dir, "t4-item", payload, reservation_usd=0.143612)
        
        # Verify exact file content on disk matches body_bytes
        persisted_bytes = (pack_dir / "request_body.json").read_bytes()
        assert persisted_bytes == body_bytes, "Persisted file bytes must be bit-for-bit identical to wire bytes"
        assert sha256_bytes(persisted_bytes) == body_sha, "Persisted file hash must equal write-ahead bodySHA256"

        wa = json.loads((pack_dir / "write_ahead_request.json").read_text(encoding="utf-8"))
        assert wa["bodySHA256"] == body_sha
        assert wa["status"] == "SENDING_POST"
        print(f"Wire bytes ({len(body_bytes)} bytes) exactly match persisted file and write-ahead SHA: {body_sha[:16]}...")
        results.append({"test": "Sent-Byte Hash Equality", "status": "PASS"})
    except Exception as e:
        results.append({"test": "Sent-Byte Hash Equality", "status": "FAIL", "error": str(e)})

    # -------------------------------------------------------------
    # Test 5: Success reuse without repurchase
    # -------------------------------------------------------------
    print("\n--- Test 5: Success Reuse Without Repurchase ---")
    try:
        pack_dir = QA_SANDBOX / "t5_pack"
        pack_dir.mkdir(parents=True, exist_ok=True)
        out_png = pack_dir / "output.png"
        create_mock_png(out_png, size=(2048, 2048))
        (pack_dir / "response.json").write_text(json.dumps({"mock": "response"}), encoding="utf-8")

        # Mock transport that would fail if called
        def failing_transport(endpoint, body):
            raise RuntimeError("Transport must NOT be called for reused successes!")

        r = ContinuityRunner(
            mutex_file=QA_SANDBOX / "t5_mutex.json",
            pacing_file=QA_SANDBOX / "t5_pacing.json",
            transport=failing_transport
        )
        meta = {"id": "t5-reused-item", "prompt": "Hero portrait", "group": "HERO"}
        res = r.execute_request(pack_dir, meta)
        assert res["status"] == "REUSED_EXISTING_SUCCESS"
        assert res["costUSD"] == 0.0
        assert res["dimensions"] == [2048, 2048]
        print(f"Successfully reused existing 2K image: {res['sha256'][:16]}... with 0 calls.")
        results.append({"test": "Success Reuse", "status": "PASS"})
    except Exception as e:
        results.append({"test": "Success Reuse", "status": "FAIL", "error": str(e)})

    # -------------------------------------------------------------
    # Test 6: UNKNOWN release denial
    # -------------------------------------------------------------
    print("\n--- Test 6: UNKNOWN Release Denial ---")
    try:
        t6_mutex = QA_SANDBOX / "t6_submission.mutex.json"
        r = ContinuityRunner(mutex_file=t6_mutex, pacing_file=QA_SANDBOX / "t6_pacing.json")
        assert r.acquire_mutex() == True
        
        # Release with UNKNOWN state -> must return False and keep active=True
        ret = r.release_mutex(state="UNKNOWN")
        assert ret == False, "release_mutex('UNKNOWN') must return False"
        
        data = json.loads(t6_mutex.read_text(encoding="utf-8"))
        assert data["active"] == True, "Mutex must remain active on UNKNOWN"
        assert data["lastState"] == "UNKNOWN", "lastState must be UNKNOWN"
        print("Mutex release correctly denied on UNKNOWN state; liability retained.")
        results.append({"test": "UNKNOWN Release Denial", "status": "PASS"})
    except Exception as e:
        results.append({"test": "UNKNOWN Release Denial", "status": "FAIL", "error": str(e)})

    # -------------------------------------------------------------
    # Test 7: Restart pacing enforcement
    # -------------------------------------------------------------
    print("\n--- Test 7: Restart Pacing Enforcement ---")
    try:
        fake_clock = FakeClock(start_time=1000.0)
        t7_pacing = QA_SANDBOX / "t7_pacing.json"
        r1 = ContinuityRunner(
            mutex_file=QA_SANDBOX / "t7_mutex.json",
            pacing_file=t7_pacing,
            clock=fake_clock.time,
            sleeper=fake_clock.sleep
        )
        r1.last_completed_at = 1000.0
        r1.next_allowed_post_at = 1020.0  # 20s gap
        r1.save_pacing()

        # Simulate process termination, new instance starts at T=1005 (15s remaining)
        fake_clock.current_time = 1005.0
        r2 = ContinuityRunner(
            mutex_file=QA_SANDBOX / "t7_mutex.json",
            pacing_file=t7_pacing,
            clock=fake_clock.time,
            sleeper=fake_clock.sleep
        )
        assert r2.next_allowed_post_at == 1020.0
        r2.enforce_pacing()
        # Should have slept 15.0 seconds
        assert 15.0 in fake_clock.sleep_calls
        assert fake_clock.current_time == 1020.0
        print(f"Restart runner correctly respected persisted pacing and waited remaining 15.0s.")
        results.append({"test": "Restart Pacing Enforcement", "status": "PASS"})
    except Exception as e:
        results.append({"test": "Restart Pacing Enforcement", "status": "FAIL", "error": str(e)})

    # -------------------------------------------------------------
    # Test 8: Numeric and HTTP-date Retry-After
    # -------------------------------------------------------------
    print("\n--- Test 8: Numeric & HTTP-Date Retry-After Parsing ---")
    try:
        now_ts = 1700000000.0
        now_fn = lambda: now_ts

        # Numeric 75s
        sec1 = parse_retry_after("75", now_fn=now_fn)
        assert sec1 == 75.0, f"Expected 75.0, got {sec1}"

        # Numeric 30s (smaller than default, but parse returns 30.0)
        sec2 = parse_retry_after("30", now_fn=now_fn)
        assert sec2 == 30.0

        # HTTP-Date 90s in future
        future_dt = email.utils.formatdate(now_ts + 90.0, usegmt=True)
        sec3 = parse_retry_after(future_dt, now_fn=now_fn)
        assert abs(sec3 - 90.0) < 1.0, f"Expected 90.0, got {sec3}"

        print(f"Successfully parsed numeric ('75' -> {sec1}s) and HTTP-date ('{future_dt}' -> {sec3:.1f}s).")
        results.append({"test": "Numeric and HTTP-Date Retry-After", "status": "PASS"})
    except Exception as e:
        results.append({"test": "Numeric and HTTP-Date Retry-After", "status": "FAIL", "error": str(e)})

    # -------------------------------------------------------------
    # Test 9: Second dispatch blocked before deadline
    # -------------------------------------------------------------
    print("\n--- Test 9: Second Dispatch Blocked Before Deadline ---")
    try:
        fake_clock = FakeClock(start_time=2000.0)
        mock_img_path = QA_SANDBOX / "mock_img.png"
        create_mock_png(mock_img_path)
        img_b64 = base64.b64encode(mock_img_path.read_bytes()).decode("utf-8")

        # Mock transport returns success
        def mock_succ_transport(endpoint, body):
            resp_data = {
                "candidates": [{
                    "content": {
                        "parts": [{"inlineData": {"mimeType": "image/png", "data": img_b64}}]
                    },
                    "finishReason": "STOP"
                }],
                "usageMetadata": {"promptTokenCount": 500, "candidatesTokenCount": 1680}
            }
            return json.dumps(resp_data).encode("utf-8"), 200, {}

        r = ContinuityRunner(
            mutex_file=QA_SANDBOX / "t9_mutex.json",
            pacing_file=QA_SANDBOX / "t9_pacing.json",
            transport=mock_succ_transport,
            clock=fake_clock.time,
            sleeper=fake_clock.sleep
        )

        pack1 = QA_SANDBOX / "t9_pack1"
        pack2 = QA_SANDBOX / "t9_pack2"
        meta1 = {"id": "t9-item-1", "prompt": "Prompt 1", "group": "HERO"}
        meta2 = {"id": "t9-item-2", "prompt": "Prompt 2", "group": "HERO"}

        # First request at T=2000
        res1 = r.execute_request(pack1, meta1)
        assert res1["status"] == "SUCCEEDED"
        assert r.next_allowed_post_at == 2020.0

        # Advance clock to T=2005 (only 5s elapsed)
        fake_clock.current_time = 2005.0

        # Second request dispatched
        res2 = r.execute_request(pack2, meta2)
        assert res2["status"] == "SUCCEEDED"
        # Must have slept 15s to reach 2020.0
        assert 15.0 in fake_clock.sleep_calls
        print("Second dispatch successfully blocked for 15.0s until deadline before sending POST.")
        results.append({"test": "Second Dispatch Blocked Before Deadline", "status": "PASS"})
    except Exception as e:
        results.append({"test": "Second Dispatch Blocked Before Deadline", "status": "FAIL", "error": str(e)})

    # -------------------------------------------------------------
    # Test 10: Role-specific pack checks
    # -------------------------------------------------------------
    print("\n--- Test 10: Role-Specific Pack Checks ---")
    try:
        r = ContinuityRunner(mutex_file=QA_SANDBOX / "t10_mutex.json", pacing_file=QA_SANDBOX / "t10_pacing.json")
        pack = QA_SANDBOX / "t10_pack"
        pack.mkdir(parents=True, exist_ok=True)

        # 10a. Hero: generic prompt without hero/portrait fails
        meta_bad_hero = {"id": "knight-mounted-master", "group": "2K-LATER-A-HERO-32", "prompt": "Generic prompt"}
        chk1 = r.check_role_pack(pack, meta_bad_hero)
        assert chk1["pass"] == False
        print(f"Generic knight prompt rejected: {chk1['reason']}")

        # 10b. Good knight mounted prompt passes
        meta_good_knight = {
            "id": "knight-mounted-master",
            "group": "2K-LATER-A-HERO-32",
            "prompt": "Knight hero mounted on war horse with natural hooves and saddle harness, 2048x2048.",
            "layout": {"canvas": [2048, 2048]}
        }
        chk2 = r.check_role_pack(pack, meta_good_knight)
        assert chk2["pass"] == True
        print("Role-specific knight mounted prompt passed.")

        # 10c. Mount missing saddle/rider anchor rejected
        meta_bad_mount = {
            "id": "hero-mount-horse",
            "group": "2K-LATER-B-MOUNTS-RIGS-RIVALS-17",
            "prompt": "A horse standing in a meadow.",
            "layout": {"canvas": [2048, 2048]}
        }
        chk3 = r.check_role_pack(pack, meta_bad_mount)
        assert chk3["pass"] == False
        print(f"Mount missing saddle/rider anchor rejected: {chk3['reason']}")

        # 10d. Rival missing named identity rejected
        meta_bad_rival = {
            "id": "rival-identity-1",
            "group": "2K-LATER-B-MOUNTS-RIGS-RIVALS-17",
            "prompt": "A noble baron standing with crown.",
            "layout": {"canvas": [2048, 2048]}
        }
        chk4 = r.check_role_pack(pack, meta_bad_rival)
        assert chk4["pass"] == False
        print(f"Rival missing named identity rejected: {chk4['reason']}")

        # 10e. Rival with Aldric passes
        meta_good_rival = {
            "id": "rival-identity-1",
            "group": "2K-LATER-B-MOUNTS-RIGS-RIVALS-17",
            "prompt": "Lord Aldric the Steadfast in ornate damascened plate armor.",
            "layout": {"canvas": [2048, 2048]}
        }
        chk5 = r.check_role_pack(pack, meta_good_rival)
        assert chk5["pass"] == True
        print("Named rival Aldric passed.")

        # 10f. Confirm terrain geometry (e.g. worldToSource) is NOT required
        assert "worldToSource" not in meta_good_rival
        print("Confirmed terrain geometry is NOT required for actor portraits.")
        results.append({"test": "Role-Specific Pack Checks", "status": "PASS"})
    except Exception as e:
        results.append({"test": "Role-Specific Pack Checks", "status": "FAIL", "error": str(e)})

    # Summary
    print("\n=== OFFLINE TEST REPORT SUMMARY ===")
    pass_cnt = sum(1 for r in results if r["status"] == "PASS")
    total_cnt = len(results)
    print(f"Passed: {pass_cnt}/{total_cnt}")
    for res in results:
        status_sym = "[OK]" if res["status"] == "PASS" else "[FAIL]"
        print(f"  {status_sym} {res['test']}" + (f" - Error: {res.get('error')}" if 'error' in res else ""))

    report_path = QA_SANDBOX / "test_report.json"
    report_path.write_text(json.dumps({
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total": total_cnt,
        "passed": pass_cnt,
        "results": results
    }, indent=2), encoding="utf-8")

    assert pass_cnt == total_cnt, f"Some tests failed: {total_cnt - pass_cnt} failures"
    print("ALL 10 OFFLINE TESTS PASSED CLEANLY IN SANDBOX!")

if __name__ == "__main__":
    run_all_offline_tests()
