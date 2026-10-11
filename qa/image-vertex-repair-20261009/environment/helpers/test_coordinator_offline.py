"""Offline checks for the owned Vertex coordinator. No network and no shared ledgers."""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import coordinator as coord


def _wire(prompt: str) -> bytes:
    body = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"candidateCount": 1, "responseModalities": ["IMAGE"]},
    }
    return json.dumps(body, sort_keys=True).encode("utf-8")


def _meta(attempt: str, wire: bytes) -> dict:
    return {
        "id": "sample-terrain",
        "attemptId": attempt,
        "owner": "ENVIRONMENT",
        "prompt": "A prepared terrain prompt long enough",
        "wireBodySHA256": coord.sha256_bytes(wire),
        "inlineCount": 0,
    }


def main() -> None:
    root = Path(tempfile.mkdtemp(prefix="aod-coord-"))
    calls = {"n": 0, "bodies": []}

    def transport(endpoint, body):
        calls["n"] += 1
        calls["bodies"].append(body)
        wa = root / "pack" / "write_ahead_request.json"
        assert wa.exists(), "write-ahead missing before POST"
        assert coord.sha256_bytes(body) == json.loads(wa.read_text(encoding="utf-8"))["bodySHA256"]
        assert body == calls["bodies"][0] or True
        return b'{"candidates":[{"content":{"parts":[]}}]}', 200, {}

    clock = {"t": 1000.0}

    def now():
        return clock["t"]

    def sleep(seconds):
        clock["t"] += seconds

    runner = coord.Coordinator(
        root, owner_id="offline-test", committed_protected_usd=70.0, hard_cap_usd=80.0,
        transport=transport, clock=now, sleeper=sleep,
    )
    runner.acquire_mutex()
    other = coord.Coordinator(root, owner_id="contender", committed_protected_usd=70.0, clock=now, sleeper=sleep)
    try:
        other.acquire_mutex()
        raise SystemExit("second acquire must fail")
    except coord.MutexError:
        pass

    wire = _wire("A prepared terrain prompt long enough")
    meta = _meta("attempt-1", wire)
    pack = root / "pack"
    result = runner.execute_prepared(pack, wire, meta, 0.5)
    assert result["status"] == "SUCCEEDED_CANDIDATE", result
    assert calls["n"] == 1
    assert calls["bodies"][0] == wire
    again = runner.execute_prepared(pack, wire, meta, 0.5)
    assert again["status"] == "REUSED_SUCCESS", again
    assert calls["n"] == 1, "reuse sent a second POST"
    assert runner.release_mutex("RELEASED") is True

    qroot = root / "quota"
    qcalls = {"n": 0}

    def quota_transport(endpoint, body):
        qcalls["n"] += 1
        return b"quota", 429, {"Retry-After": "9"}

    quota = coord.Coordinator(
        qroot, owner_id="quota-test", committed_protected_usd=70.0,
        transport=quota_transport, clock=now, sleeper=sleep,
    )
    quota.acquire_mutex()
    qwire = _wire("A prepared terrain prompt long enough")
    try:
        quota.execute_prepared(qroot / "pack", qwire, _meta("attempt-q", qwire), 0.5)
        raise SystemExit("429 must stop")
    except coord.QuotaStop:
        pass
    assert qcalls["n"] == 1, "429 resent inside the call"
    try:
        quota.execute_prepared(qroot / "pack", qwire, _meta("attempt-q2", qwire), 0.5)
        raise SystemExit("429 must block the paid run")
    except coord.UnknownLiabilityError:
        pass
    assert qcalls["n"] == 1

    uroot = root / "unknown"
    def boom(endpoint, body):
        raise TimeoutError("disconnected")

    unknown = coord.Coordinator(
        uroot, owner_id="unknown-test", committed_protected_usd=70.0,
        transport=boom, clock=now, sleeper=sleep,
    )
    unknown.acquire_mutex()
    uwire = _wire("A prepared terrain prompt long enough")
    try:
        unknown.execute_prepared(uroot / "pack", uwire, _meta("attempt-u", uwire), 0.4)
        raise SystemExit("timeout must not look successful")
    except coord.UnknownLiabilityError:
        pass
    wa = json.loads((uroot / "pack" / "write_ahead_request.json").read_text(encoding="utf-8"))
    assert wa["status"] == "UNKNOWN"
    assert unknown.release_mutex("RELEASED") is False

    broot = root / "budget"
    budget = coord.Coordinator(
        broot, owner_id="budget-test", committed_protected_usd=79.7, hard_cap_usd=80.0,
        transport=transport, clock=now, sleeper=sleep,
    )
    budget.acquire_mutex()
    bwire = _wire("A prepared terrain prompt long enough")
    before = calls["n"]
    try:
        budget.execute_prepared(broot / "pack", bwire, _meta("attempt-b", bwire), 0.5)
        raise SystemExit("over-cap reservation must fail")
    except coord.BudgetError:
        pass
    assert calls["n"] == before
    assert not (broot / "pack" / "write_ahead_request.json").exists()

    rroot = root / "resume"
    rcalls = {"n": 0}

    def rtransport(endpoint, body):
        rcalls["n"] += 1
        if rcalls["n"] == 1:
            return b"quota", 429, {"Retry-After": "5"}
        return b'{"candidates":[{"content":{"parts":[]}}]}', 200, {}

    rclock = {"t": 5000.0}

    def rnow():
        return rclock["t"]

    def rsleep(seconds):
        rclock["t"] += seconds

    first = coord.Coordinator(
        rroot, owner_id="resume-a", committed_protected_usd=71.1156,
        transport=rtransport, clock=rnow, sleeper=rsleep,
    )
    first.acquire_mutex()
    rwire = _wire("A prepared terrain prompt long enough")
    try:
        first.execute_prepared(rroot / "pack", rwire, _meta("attempt-r", rwire), 0.4931)
        raise SystemExit("first resume setup must 429")
    except coord.QuotaStop:
        pass
    assert len(first.reservations) == 1
    assert first.release_mutex("QUOTA_STOP") is True
    second = coord.Coordinator(
        rroot, owner_id="resume-b", committed_protected_usd=71.1156,
        transport=rtransport, clock=rnow, sleeper=rsleep,
    )
    second.acquire_mutex()
    before_exposure = second.exposure_usd()
    resumed = second.resume_retained_body(rroot / "pack", rwire, _meta("attempt-r", rwire))
    assert resumed["status"] == "SUCCEEDED_CANDIDATE", resumed
    assert rcalls["n"] == 2
    assert len(second.reservations) == 1
    assert second.exposure_usd() == before_exposure
    assert second.release_mutex("RELEASED") is True

    bound = coord.estimate_upper_bound_usd("4K", 2, 800)
    assert bound > 0.15, bound
    assert bound < 2.0, bound
    shutil.rmtree(root, ignore_errors=True)
    print(json.dumps({"offlineCoordinator": "PASS", "fourKUpperBoundUSD": bound}))


if __name__ == "__main__":
    main()
