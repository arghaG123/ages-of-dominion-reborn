import sys, os, json, threading, concurrent.futures, time, hashlib, base64, shutil
from pathlib import Path
from PIL import Image

ROOT = Path('C:/dev/ages-of-dominion-reborn')
SANDBOX = ROOT / 'qa/image-v3-isolated-controls-20261004'
SANDBOX.mkdir(parents=True, exist_ok=True)
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / 'scripts'))

import interactive_runner_continuity as m

def forbidden(*args, **kwargs):
    raise AssertionError('Network and credentials forbidden')

m.get_gcloud_token = forbidden
m.urllib.request.urlopen = forbidden
m.subprocess.run = forbidden

def cleanup_prefix(prefix):
    for f in SANDBOX.glob(f'{prefix}*'):
        try:
            if f.is_file(): f.unlink()
            elif f.is_dir(): shutil.rmtree(f)
        except Exception: pass

def runner(name):
    return m.ContinuityRunner(
        owner_base=f'test-{name}',
        mutex_file=SANDBOX / f'{name}-mutex.json',
        pacing_file=SANDBOX / f'{name}-pacing.json',
        budget_file=SANDBOX / f'{name}-budget.json',
        local_lock_file=SANDBOX / f'{name}-active.json',
        cloud_lock_enabled=False,
        transport=forbidden
    )

report_rows = []

# --- 1. PRODUCER 9 PROBES ---
cleanup_prefix('delayed-race')
barrier = threading.Barrier(2)
first_done = threading.Event()
orig = m.os.replace

def delayed(a, b):
    if str(b).endswith('delayed-race-mutex.json'):
        try: barrier.wait(timeout=0.05)
        except Exception: pass
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
    if i == 0: first_done.set()
    return v

with concurrent.futures.ThreadPoolExecutor(2) as pool:
    contenders = list(pool.map(acquire, enumerate(rs)))

m.os.replace = orig
probe1_exclusive = sum(x['acquired'] for x in contenders) == 1
report_rows.append({'probe': 'delayed contender after first verification', 'pass': probe1_exclusive, 'detail': contenders})

cleanup_prefix('dead-unknown')
r = runner('dead-unknown')
r.mutex_file.write_text(json.dumps({'active': True, 'owner': 'dead', 'pid': 2147483647, 'lastState': 'UNKNOWN'}))
try: v = r.acquire_mutex()
except Exception: v = False
report_rows.append({'probe': 'dead PID UNKNOWN blocked', 'pass': not v})

cleanup_prefix('unknown-release')
r = runner('unknown-release')
r.acquire_mutex()
r.has_retained_liabilities = True
r.unresolved_items = ['test-unknown-liability']
try: v = r.release_mutex()
except Exception: v = False
report_rows.append({'probe': 'UNKNOWN release denied', 'pass': not v})

cleanup_prefix('history')
r = runner('history')
p = SANDBOX / 'history-pack'
p.mkdir(parents=True, exist_ok=True)
r.write_ahead_persisted_request(p, 'offline-id', {'a': 1}, 0.1, 1)
before = (p / 'write_ahead_subattempt_1.json').read_bytes()
r.write_ahead_persisted_request(p, 'offline-id', {'a': 2}, 0.1, 1)
probe4_preserved = ((p / 'write_ahead_subattempt_1.json').read_bytes() == before)
report_rows.append({'probe': 'subattempt append-only collision preserved', 'pass': probe4_preserved})

cleanup_prefix('preflight')
r = runner('preflight')
p_good = SANDBOX / 'preflight-good-pack'
p_good.mkdir(parents=True, exist_ok=True)
p_bad = SANDBOX / 'preflight-bad-pack'
p_bad.mkdir(parents=True, exist_ok=True)
(p_good / 'write_ahead_request.json').write_text(json.dumps({'status': 'SUCCEEDED', 'itemId': 'item-good', 'sha256': 'abc'}))
(p_bad / 'write_ahead_request.json').write_text(json.dumps({'status': 'UNKNOWN_CRASH_DURING_DISPATCH', 'itemId': 'item-bad'}))
halted = False
try: r.preflight_check([p_good, p_bad])
except m.UnknownLiabilityError: halted = True
report_rows.append({'probe': 'preflight halt on UNKNOWN item', 'pass': halted})

cleanup_prefix('cloud-states')
r = runner('cloud-states')
cloud_blocked = []
for state in ['RUNNING', 'PENDING', 'QUEUED', 'UNKNOWN', 'ACTIVE_INDIVIDUAL_GENERATION']:
    r.cloud_state_mock = state
    try: bl = r.is_cloud_blocked()
    except Exception: bl = True
    cloud_blocked.append(bl)
report_rows.append({'probe': 'cloud active/unknown states blocked', 'pass': all(cloud_blocked)})

cleanup_prefix('malformed-pacing')
r = runner('malformed-pacing')
r.pacing_file.write_text('corrupted json {{')
try:
    r.load_pacing()
    pacing_blocked = False
except Exception:
    pacing_blocked = True
report_rows.append({'probe': 'malformed pacing fails closed', 'pass': pacing_blocked})

cleanup_prefix('malformed-wa-pack')
p = SANDBOX / 'malformed-wa-pack'
p.mkdir(parents=True, exist_ok=True)
(p / 'write_ahead_request.json').write_text('')
r = runner('malformed-wa')
try:
    r.preflight_check([p])
    wa_failed = False
except m.UnknownLiabilityError:
    wa_failed = True
report_rows.append({'probe': 'malformed write-ahead fails closed', 'pass': wa_failed})

cleanup_prefix('normal-release')
r = runner('normal-release')
r.acquire_mutex()
v = r.release_mutex()
report_rows.append({'probe': 'normal release succeeds', 'pass': v == True})

# --- 2. ISOLATED REUSE BINDING PROBES (5 probes) ---
reuse_rows = []
for mode in ['valid-baseline', 'missing-body-hash', 'invented-body-hash', 'changed-prompt', 'wrong-mime']:
    cleanup_prefix(f'isolated-{mode}')
    p = SANDBOX / f'isolated-{mode}'
    p.mkdir(parents=True, exist_ok=True)
    Image.new('RGB', (2048, 2048), (90, 120, 80)).save(p / 'output.png')
    b = (p / 'output.png').read_bytes()
    h = hashlib.sha256(b).hexdigest()
    payload = {
        'contents': [{'role': 'user', 'parts': [{'text': 'original prompt'}]}],
        'generationConfig': {'candidateCount': 1, 'maxOutputTokens': 2048, 'responseModalities': ['IMAGE'], 'imageConfig': {'aspectRatio': '1:1', 'imageSize': '2K'}}
    }
    body = json.dumps(payload, indent=2, sort_keys=True).encode()
    (p / 'request_body.json').write_bytes(body)
    wa = {'status': 'SUCCEEDED', 'itemId': 'test-id', 'sha256': h, 'bodySHA256': hashlib.sha256(body).hexdigest()}
    if mode == 'missing-body-hash': del wa['bodySHA256']
    if mode == 'invented-body-hash': wa['bodySHA256'] = 'a' * 64
    resp = {
        'candidates': [{'content': {'parts': [{'inlineData': {
            'mimeType': 'image/jpeg' if mode == 'wrong-mime' else 'image/png',
            'data': base64.b64encode(b).decode()
        }}]}}]
    }
    respb = json.dumps(resp).encode()
    (p / 'response.json').write_bytes(respb)
    wa['responseSHA256'] = hashlib.sha256(respb).hexdigest()
    (p / 'write_ahead_request.json').write_text(json.dumps(wa))
    
    r = runner(f'iso-{mode}')
    res = r.execute_request(p, {'id': 'test-id', 'prompt': 'different prompt' if mode == 'changed-prompt' else 'original prompt'})
    passed = (res['status'] == 'REUSED_EXISTING_SUCCESS') if (mode == 'valid-baseline') else (res['status'].startswith('FAILED_REUSE'))
    reuse_rows.append({'probe': mode, 'result': res, 'pass': passed})
    report_rows.append({'probe': f'reuse-binding-{mode}', 'pass': passed, 'status': res.get('status')})

(SANDBOX / 'isolated-reuse-binding-results.json').write_text(json.dumps(reuse_rows, indent=2))
(SANDBOX / 'repaired-controls-report-v3.json').write_text(json.dumps({
    'scope': 'OFFLINE NEW SANDBOX (qa/image-v3-isolated-controls-20261004). Network/credentials forbidden.',
    'totalProbes': len(report_rows),
    'passingProbes': sum(r['pass'] for r in report_rows),
    'failingProbes': sum(not r['pass'] for r in report_rows),
    'allPassed': all(r['pass'] for r in report_rows),
    'rows': report_rows
}, indent=2))
print('Saved test script and reports. All passed:', all(r['pass'] for r in report_rows))
