"""Offline transport and budget-guard checks. No network."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import coordinator as c


def expect(name, fn):
    try:
        fn()
    except c.BudgetError:
        print(json.dumps({"check": name, "rejected": True}))
        return
    raise SystemExit(f"{name} was not rejected")


def main():
    release = c.release_record_template("2026-10-09T00:00:00+00:00")
    base = dict(
        release=release,
        prior_liability_usd=c.PRIOR_LIABILITY_EXCLUDING_RESERVE_USD,
        other_effective_holds_usd=0.0,
        new_reservation_usd=0.55,
        effective_reserve_usd=0.0,
        known_attempt_ids=set(),
        attempt_id="new-1",
        unknown_outstanding=False,
        double_subtracted=False,
    )
    ok = c.guard_post(**base)
    assert ok["authorized"] and ok["totalUSD"] <= 80
    expect("over-cap", lambda: c.guard_post(**{**base, "new_reservation_usd": 20}))
    expect("missing-release", lambda: c.guard_post(**{**base, "release": None}))
    stale = dict(release)
    stale["ownerQuote"] = "spend it"
    expect("stale-release", lambda: c.guard_post(**{**base, "release": stale}))
    expect("double-subtraction", lambda: c.guard_post(**{**base, "double_subtracted": True}))
    expect(
        "double-subtraction-balance",
        lambda: c.guard_post(**{**base, "prior_liability_usd": c.PRIOR_LIABILITY_EXCLUDING_RESERVE_USD - 15}),
    )
    expect("duplicate-hold", lambda: c.guard_post(**{**base, "known_attempt_ids": {"new-1"}}))
    expect("unknown", lambda: c.guard_post(**{**base, "unknown_outstanding": True}))
    expect("insufficient", lambda: c.guard_post(**{**base, "other_effective_holds_usd": 15.0, "new_reservation_usd": 0.5}))

    clock = {"t": 1_000_000.0}
    sleeps = []

    def transport_ok(url, body):
        return b'{"candidates":[]}', 200, {}

    def transport_429(url, body):
        return b"", 429, {"Retry-After": "90"}

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        wire = b'{"contents":[{"parts":[{"text":"x"},{"inlineData":{"mimeType":"image/png","data":"a"}}]}]}'
        meta = {"id": "class-healer-standing-body", "attemptId": "healer-a1", "owner": "ACTORS", "wireBodySHA256": c.sha256_bytes(wire)}
        runner = c.Coordinator(
            root, release=release, cloud_lock_enabled=False,
            transport=transport_ok, clock=lambda: clock["t"], sleeper=lambda s: sleeps.append(s),
        )
        runner.acquire_mutex()
        first = runner.execute_prepared(root / "pack", wire, meta, 0.55)
        assert first["status"] == "SUCCEEDED" and first["sent"] is True
        reused = runner.execute_prepared(root / "pack", wire, meta, 0.55)
        assert reused["status"] == "REUSED_SUCCESS" and reused["sent"] is False
        assert runner.next_allowed_post_at - runner.last_completed_at == 30
        # second new attempt before gap waits
        clock["t"] = runner.last_completed_at + 5
        meta2 = {"id": "other", "attemptId": "other-a1", "owner": "ACTORS", "wireBodySHA256": c.sha256_bytes(wire)}
        runner.execute_prepared(root / "pack2", wire, meta2, 0.55)
        assert sleeps and sleeps[-1] >= 25

        cloud_gen = {"g": "7"}
        store = {"body": {"state": "JOB_STATE_SUCCEEDED", "workflow_state": "TERMINAL_COLLECTED"}, "gen": "7"}

        def get():
            return store["body"], store["gen"]

        def put(payload, match):
            if match != store["gen"]:
                raise c.MutexError("CAS mismatch")
            store["body"] = payload
            store["gen"] = str(int(store["gen"]) + 1)
            return store["gen"]

        cloud_runner = c.Coordinator(
            root / "cloud", release=release, cloud_lock_enabled=True, token_provider=lambda: "tok",
            cloud={"get": get, "put": put}, transport=transport_ok, clock=lambda: clock["t"], sleeper=lambda s: None,
        )
        cloud_runner.acquire_mutex()
        assert store["body"]["workflow_state"] == "ACTIVE_INDIVIDUAL_GENERATION"
        store["gen"] = "1"
        try:
            cloud_runner._put_cloud_lock({"state": "x"}, "999", "tok")
            raise SystemExit("CAS mismatch was accepted")
        except c.MutexError:
            pass

        qroot = root / "quota"
        q = c.Coordinator(
            qroot, release=release, transport=transport_429, clock=lambda: 50_000.0, sleeper=lambda s: None,
        )
        q.acquire_mutex()
        try:
            q.execute_prepared(qroot / "q", wire, {"id": "q", "attemptId": "q-a1", "owner": "ACTORS", "wireBodySHA256": c.sha256_bytes(wire)}, 0.4)
            raise SystemExit("429 did not stop")
        except c.QuotaStop:
            pass
        assert q.blocked and q.next_eligible_retry_at >= 50_000.0 + 90

        uroot = root / "unknown"

        def boom(url, body):
            raise TimeoutError("timeout")

        u = c.Coordinator(uroot, release=release, transport=boom, clock=lambda: 10.0, sleeper=lambda s: None)
        u.acquire_mutex()
        try:
            u.execute_prepared(uroot / "u", wire, {"id": "u", "attemptId": "u-a1", "owner": "ACTORS", "wireBodySHA256": c.sha256_bytes(wire)}, 0.4)
            raise SystemExit("timeout did not become unknown")
        except c.UnknownLiabilityError:
            pass
        assert u.unresolved_items == ["u"]
        try:
            u.execute_prepared(uroot / "u2", wire, {"id": "u2", "attemptId": "u2-a1", "owner": "ACTORS", "wireBodySHA256": c.sha256_bytes(wire)}, 0.4)
            raise SystemExit("unknown did not block the next dispatch")
        except c.UnknownLiabilityError:
            pass
        assert u.release_mutex() is False

    ledger = {"safetyReserve": 15, "vertexRepair20261009": {"currentCommittedProtectedUSD": 79.8327}}
    c.append_release_once(ledger, "2026-10-09T00:00:00+00:00")
    assert ledger["safetyReserve"] == 15
    assert ledger["vertexRepair20261009"]["currentCommittedProtectedUSD"] == 79.8327
    expect("second-release", lambda: c.append_release_once(ledger, "2026-10-09T00:00:01+00:00"))

    bound = c.estimate_upper_bound_usd("2K", 4, 800)
    print(json.dumps({
        "offlineCoordinator": "PASS",
        "twoKFourImageUpperBoundUSD": bound,
        "gapSeconds": c.SUCCESS_GAP_SECONDS,
        "imagePer1M": c.IMAGE_PER_1M,
    }))


if __name__ == "__main__":
    main()
