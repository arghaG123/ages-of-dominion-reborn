import importlib.util
import json
import io
import tempfile
import urllib.error
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("professional_coordinator", ROOT / "qa/image-unified-reserve-20261009/helpers/coordinator.py")
coordinator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(coordinator)
ledger = json.loads((ROOT / "docs/plan/image-production/budget-ledger.json").read_text())
authority = ledger["professionalRepairAuthority20261018"]
arguments = dict(release=ledger["ownerReserveRelease20261009"], prior_liability_usd=67.8327, other_effective_holds_usd=20, new_reservation_usd=.4, effective_reserve_usd=0, known_attempt_ids=set(), attempt_id="policy-fixture", unknown_outstanding=False, double_subtracted=False)

def rejects(**changes):
    try:
        coordinator.guard_post(**{**arguments, **changes})
    except coordinator.BudgetError:
        return
    raise AssertionError(changes)

rejects()
rejects(hard_cap_usd=100)
rejects(hard_cap_usd=101, ceiling_authority=authority)
rejects(hard_cap_usd=100, ceiling_authority={**authority, "historicalLiabilityRetainedUSD": 0})
rejects(hard_cap_usd=100, ceiling_authority=authority, unknown_outstanding=True)
rejects(hard_cap_usd=100, ceiling_authority=authority, other_effective_holds_usd=32)
rejects(hard_cap_usd=100, ceiling_authority=authority, double_subtracted=True)
assert coordinator.guard_post(**arguments, hard_cap_usd=100, ceiling_authority=authority)["totalUSD"] == 88.2327
assert .3 < coordinator.estimate_upper_bound_usd("4K", 3, 4000) < .4
with tempfile.TemporaryDirectory() as directory:
    temporary = Path(directory)
    mutex = temporary / "mutex.json"
    mutex.write_text(json.dumps({"active": False, "lastState": "RELEASED", "unknownAttempt": "style-barbarian-standing-body-v1-a1"}))
    runner = coordinator.Coordinator(temporary, release=ledger["ownerReserveRelease20261009"], ceiling_authority=authority, hard_cap_usd=100, prior_liability_usd=67.8327, token_provider=lambda: "test-only", mutex_file=mutex, success_gap=20, clock=lambda: 1000)
    runner.acquire_mutex()
    assert json.loads(mutex.read_text())["unknownAttempt"] == "style-barbarian-standing-body-v1-a1"
    wire = b'{}'
    error = urllib.error.HTTPError("https://example.invalid", 429, "fixture", {"Retry-After": "95"}, io.BytesIO(b'{"error":"quota fixture"}'))
    with patch.object(coordinator.urllib.request, "urlopen", side_effect=error):
        try:
            runner.execute_prepared(temporary / "pack", wire, {"id": "quota-fixture", "attemptId": "quota-fixture-a1", "wireBodySHA256": coordinator.sha256_bytes(wire)}, .4)
        except coordinator.QuotaStop:
            pass
        else:
            raise AssertionError("Real HTTP adapter failed to stop after 429")
    assert runner.next_eligible_retry_at == 1095
    assert runner.blocked
    assert runner.release_mutex() is False
    assert json.loads(runner.pacing_file.read_text())["nextEligibleRetryAtTs"] == 1095
    assert runner.reservations[0]["retained"] is True
print(json.dumps({"paidPolicy": "PASS", "newUnknownStillBlocks": True, "historicalLiabilityRetainedUSD": .5, "ceilingUSD": 100}))
