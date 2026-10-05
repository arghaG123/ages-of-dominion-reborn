"""Offline Test Suite for Repaired Continuity Runner Controls.
All network, credentials, and live paths disabled and redirected into this new sandbox.
"""
import sys, os, json, threading, concurrent.futures, time, io, urllib.request, subprocess
from pathlib import Path
from PIL import Image

ROOT = Path('C:/dev/ages-of-dominion-reborn')
SANDBOX = Path(__file__).parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / 'scripts'))

import interactive_runner_continuity as m

def forbidden(*args, **kwargs):
    raise AssertionError('Network and credentials forbidden')

m.get_gcloud_token = forbidden
m.urllib.request.urlopen = forbidden
m.subprocess.run = forbidden

def cleanup_prefix(prefix):
    for f in SANDBOX.glob(f"{prefix}*"):
        try:
            if f.is_file(): f.unlink()
            elif f.is_dir():
                import shutil
                shutil.rmtree(f)
        except Exception:
            pass

def runner(name):
    return m.ContinuityRunner(
        owner_base=f"test-{name}",
        mutex_file=SANDBOX / f"{name}-mutex.json",
        pacing_file=SANDBOX / f"{name}-pacing.json",
        budget_file=SANDBOX / f"{name}-budget.json",
        local_lock_file=SANDBOX / f"{name}-active.json",
        cloud_lock_enabled=False,
        transport=forbidden
    )

rows = []

# Probe 1: Delayed contender probe with barrier
print("Running Probe 1: Delayed contender exclusive acquisition...")
cleanup_prefix("delayed-race")
barrier = threading.Barrier(2)
first_done = threading.Event()
orig = m.os.replace

def delayed(a, b):
    if str(b).endswith('delayed-race-mutex.json'):
        try:
            barrier.wait(timeout=0.05)
        except Exception:
            pass
        if threading.current_thread().name.endswith('_1'):
            first_done.wait(timeout=5)
    return orig(a, b)

m.os.replace = delayed
rs = [runner('delayed-race'), runner('delayed-race')]

def acquire(pair):
    i, r = pair
    try:
        acq = r.acquire_mutex()
        v = {'contender': i, 'acquired': acq, 'error': None}
    except Exception as e:
        v = {'contender': i, 'acquired': False, 'error': str(e)}
    if i == 0:
        first_done.set()
    return v

with concurrent.futures.ThreadPoolExecutor(2) as pool:
    contenders = list(pool.map(acquire, enumerate(rs)))

m.os.replace = orig
probe1_exclusive = sum(x['acquired'] for x in contenders) == 1
rows.append({
    'probe': 'delayed contender after first verification',
    'contenders': contenders,
    'exclusive': probe1_exclusive,
    'pass': probe1_exclusive
})
print(f"  Probe 1 Result: exclusive={probe1_exclusive}")

# Probe 2: Dead PID UNKNOWN
print("Running Probe 2: Dead PID UNKNOWN...")
cleanup_prefix("dead-unknown")
r = runner('dead-unknown')
r.mutex_file.write_text(json.dumps({'active': True, 'owner': 'dead', 'pid': 2147483647, 'lastState': 'UNKNOWN'}))
try:
    v = r.acquire_mutex()
except Exception:
    v = False
probe2_blocked = not v
rows.append({
    'probe': 'dead PID UNKNOWN',
    'blocked': probe2_blocked,
    'pass': probe2_blocked
})
print(f"  Probe 2 Result: blocked={probe2_blocked}")

# Probe 3: UNKNOWN release denied
print("Running Probe 3: UNKNOWN release denied...")
cleanup_prefix("unknown-release")
r = runner('unknown-release')
r.acquire_mutex()
p = SANDBOX / 'unknown-release-pack'
p.mkdir(exist_ok=True)
(p / 'write_ahead_request.json').write_text(json.dumps({'status': 'UNKNOWN', 'owner': 'old', 'liabilityUSD': 0.143612}))
res = r.execute_request(p, {'id': 'offline-unknown'})
v = r.release_mutex('COMPLETED_CYCLE')
probe3_blocked = not v
rows.append({
    'probe': 'UNKNOWN release denied',
    'result': res,
    'blocked': probe3_blocked,
    'pass': probe3_blocked
})
print(f"  Probe 3 Result: blocked={probe3_blocked}")

# Probe 4: Reuse response/body/output binding
print("Running Probe 4: Reuse response/body/output binding...")
cleanup_prefix("reuse")
r = runner('reuse')
p = SANDBOX / 'reuse-pack'
p.mkdir(exist_ok=True)
Image.new('RGB', (2048, 2048), 'red').save(p / 'output.png')
(p / 'response.json').write_text('{}')
(p / 'write_ahead_request.json').write_text(json.dumps({'status': 'SUCCEEDED', 'sha256': 'wrong', 'bodySHA256': 'wrong'}))
res = r.execute_request(p, {'id': 'offline-corrupt-reuse'})
probe4_rejects = (res.get('status') != 'REUSED_EXISTING_SUCCESS')
rows.append({
    'probe': 'reuse response/body/output binding',
    'result': res,
    'rejectsUnboundOutput': probe4_rejects,
    'pass': probe4_rejects
})
print(f"  Probe 4 Result: rejectsUnboundOutput={probe4_rejects}")

# Probe 5: Subattempt append-only collision
print("Running Probe 5: Subattempt append-only collision...")
cleanup_prefix("history")
r = runner('history')
p = SANDBOX / 'history-pack'
p.mkdir(exist_ok=True)
r.write_ahead_persisted_request(p, 'offline-id', {'a': 1}, 0.1, 1)
before = (p / 'write_ahead_subattempt_1.json').read_bytes()
r.write_ahead_persisted_request(p, 'offline-id', {'a': 2}, 0.1, 1)
probe5_preserved = ((p / 'write_ahead_subattempt_1.json').read_bytes() == before)
rows.append({
    'probe': 'subattempt append-only collision',
    'priorBytesPreserved': probe5_preserved,
    'pass': probe5_preserved
})
print(f"  Probe 5 Result: priorBytesPreserved={probe5_preserved}")

# Probe 6: Run-wide preflight halt on active/UNKNOWN
print("Running Probe 6: Run-wide preflight halt...")
cleanup_prefix("preflight")
r = runner('preflight')
p_good = SANDBOX / 'preflight-good-pack'
p_good.mkdir(exist_ok=True)
p_bad = SANDBOX / 'preflight-bad-pack'
p_bad.mkdir(exist_ok=True)
(p_good / 'write_ahead_request.json').write_text(json.dumps({'status': 'SUCCEEDED', 'itemId': 'item-good', 'sha256': 'abc'}))
(p_bad / 'write_ahead_request.json').write_text(json.dumps({'status': 'UNKNOWN_CRASH_DURING_DISPATCH', 'itemId': 'item-bad'}))

halted = False
try:
    r.preflight_check([p_good, p_bad])
except m.UnknownLiabilityError:
    halted = True
rows.append({
    'probe': 'run-wide preflight halts before next dispatch on UNKNOWN',
    'halted': halted,
    'pass': halted
})
print(f"  Probe 6 Result: halted={halted}")

# Probe 7: Cloud lock state classification (mocked)
print("Running Probe 7: Cloud lock state classification...")
cleanup_prefix("cloud-")
class MockCloudLockRunner(m.ContinuityRunner):
    def __init__(self, mock_cloud_lock, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mock_cloud_lock = mock_cloud_lock
    def _get_cloud_lock(self, token):
        return self.mock_cloud_lock, "12345"
    def _put_cloud_lock(self, lock_data, match_generation, token):
        return "12346"

blocked_states = [
    "JOB_STATE_RUNNING", "JOB_STATE_PENDING", "JOB_STATE_QUEUED",
    "ACTIVE_INDIVIDUAL_GENERATION", "JOB_STATE_UNKNOWN", "UNKNOWN"
]
all_cloud_blocked = True
for state in blocked_states:
    mock_lock = {"state": state, "pid": 9999, "owner": "cloud-worker"}
    cr = MockCloudLockRunner(
        mock_cloud_lock=mock_lock,
        mutex_file=SANDBOX / f"cloud-{state}-mutex.json",
        cloud_lock_enabled=True,
        transport=forbidden
    )
    m.get_gcloud_token = lambda *a, **k: "mock-token"
    try:
        cr.acquire_mutex()
        all_cloud_blocked = False
    except m.MutexError:
        pass

m.get_gcloud_token = forbidden
rows.append({
    'probe': 'cloud state classification covers all active/unknown states',
    'allBlocked': all_cloud_blocked,
    'pass': all_cloud_blocked
})
print(f"  Probe 7 Result: allBlocked={all_cloud_blocked}")

# Probe 8: Malformed pacing fails closed
print("Running Probe 8: Malformed pacing fails closed...")
cleanup_prefix("malformed-pacing")
pacing_file = SANDBOX / "malformed-pacing.json"
pacing_file.write_text("{ corrupt json")
pacing_blocked = False
try:
    r_bad_pacing = m.ContinuityRunner(
        mutex_file=SANDBOX / "bad-pacing-mutex.json",
        pacing_file=pacing_file
    )
except ValueError:
    pacing_blocked = True

rows.append({
    'probe': 'malformed pacing fails closed',
    'blocked': pacing_blocked,
    'pass': pacing_blocked
})
print(f"  Probe 8 Result: blocked={pacing_blocked}")

# Probe 9: Malformed write-ahead fails closed
print("Running Probe 9: Malformed write-ahead fails closed...")
cleanup_prefix("malformed-wa")
r = runner('wa-fail')
p_bad_wa = SANDBOX / 'malformed-wa-pack'
p_bad_wa.mkdir(exist_ok=True)
(p_bad_wa / 'write_ahead_request.json').write_text("not valid json")
wa_blocked = False
try:
    r.preflight_check([p_bad_wa])
except m.UnknownLiabilityError:
    wa_blocked = True

rows.append({
    'probe': 'malformed write-ahead fails closed',
    'blocked': wa_blocked,
    'pass': wa_blocked
})
print(f"  Probe 9 Result: blocked={wa_blocked}")

output_report = {
    'scope': 'OFFLINE NEW SANDBOX (qa/offline-controls-repair-20261004). All network/credentials disabled.',
    'allPassed': all(r['pass'] for r in rows),
    'rows': rows
}

(SANDBOX / 'repaired-controls-report.json').write_text(json.dumps(output_report, indent=2))
print("\n=== FINAL TEST REPORT ===")
print(json.dumps(output_report, indent=2))
