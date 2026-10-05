"""Offline v4 reuse probes. Sandbox paths are rewritten before import."""
import base64
import hashlib
import json
import shutil
import socket
import sys
import threading
import concurrent.futures
from pathlib import Path

from PIL import Image

REPO = Path("C:/dev/ages-of-dominion-reborn")
SANDBOX = REPO / "qa/image-v4-isolated-controls-20261004"
ROOT = SANDBOX / "root"
ROOT.mkdir(parents=True, exist_ok=True)
src = (REPO / "scripts/interactive_runner_continuity.py").read_text(encoding="utf-8")
src = src.replace(
    'ROOT = Path("c:/dev/ages-of-dominion-reborn")',
    f'ROOT = Path(r"{ROOT.as_posix()}")',
)
runner_path = SANDBOX / "interactive_runner_continuity.py"
runner_path.write_text(src, encoding="utf-8")
sys.path.insert(0, str(SANDBOX))
sys.dont_write_bytecode = True
import interactive_runner_continuity as m


def forbidden(*args, **kwargs):
    raise AssertionError("Network, credentials, subprocess, and transport are forbidden")


m.get_gcloud_token = forbidden
m.urllib.request.urlopen = forbidden
m.subprocess.run = forbidden
socket.create_connection = forbidden

PACK = SANDBOX / "packs"
if PACK.exists():
    shutil.rmtree(PACK)
PACK.mkdir()


def runner(name):
    return m.ContinuityRunner(
        owner_base=f"v4-{name}",
        mutex_file=PACK / f"{name}-mutex.json",
        pacing_file=PACK / f"{name}-pacing.json",
        budget_file=PACK / f"{name}-budget.json",
        local_lock_file=PACK / f"{name}-active.json",
        cloud_lock_enabled=False,
        transport=forbidden,
    )


rows = []

# Producer probes that already passed, replayed against the stricter runner.
barrier = threading.Barrier(2)
first_done = threading.Event()
orig = m.os.replace


def delayed(a, b):
    if str(b).endswith("delayed-race-mutex.json"):
        try:
            barrier.wait(timeout=0.05)
        except Exception:
            pass
        if threading.current_thread().name.endswith("_1"):
            first_done.wait(timeout=5)
    return orig(a, b)


m.os.replace = delayed
rs = [runner("delayed-race"), runner("delayed-race")]


def acquire(pair):
    i, r = pair
    try:
        acq = r.acquire_mutex()
        v = {"contender": i, "acquired": acq}
    except Exception as e:
        v = {"contender": i, "acquired": False, "error": str(e)}
    if i == 0:
        first_done.set()
    return v


with concurrent.futures.ThreadPoolExecutor(2) as pool:
    contenders = list(pool.map(acquire, enumerate(rs)))
m.os.replace = orig
rows.append({"probe": "delayed contender after first verification", "pass": sum(x["acquired"] for x in contenders) == 1})

r = runner("dead-unknown")
r.mutex_file.write_text(json.dumps({"active": True, "owner": "dead", "pid": 2147483647, "lastState": "UNKNOWN"}))
try:
    v = r.acquire_mutex()
except Exception:
    v = False
rows.append({"probe": "dead PID UNKNOWN blocked", "pass": not v})

r = runner("unknown-release")
r.acquire_mutex()
r.has_retained_liabilities = True
r.unresolved_items = ["test-unknown-liability"]
try:
    v = r.release_mutex()
except Exception:
    v = False
rows.append({"probe": "UNKNOWN release denied", "pass": not v})

r = runner("history")
p = PACK / "history-pack"
p.mkdir(parents=True, exist_ok=True)
r.write_ahead_persisted_request(p, "offline-id", {"a": 1}, 0.1, 1)
before = (p / "write_ahead_subattempt_1.json").read_bytes()
r.write_ahead_persisted_request(p, "offline-id", {"a": 2}, 0.1, 1)
rows.append({"probe": "subattempt append-only collision preserved", "pass": (p / "write_ahead_subattempt_1.json").read_bytes() == before})

r = runner("preflight")
p_good, p_bad = PACK / "preflight-good", PACK / "preflight-bad"
p_good.mkdir(parents=True, exist_ok=True)
p_bad.mkdir(parents=True, exist_ok=True)
(p_good / "write_ahead_request.json").write_text(json.dumps({"status": "SUCCEEDED", "itemId": "item-good", "sha256": "abc"}))
(p_bad / "write_ahead_request.json").write_text(json.dumps({"status": "UNKNOWN_CRASH_DURING_DISPATCH", "itemId": "item-bad"}))
halted = False
try:
    r.preflight_check([p_good, p_bad])
except m.UnknownLiabilityError:
    halted = True
rows.append({"probe": "preflight halt on UNKNOWN item", "pass": halted})

r = runner("cloud-states")
blocked = []
for state in ["RUNNING", "PENDING", "QUEUED", "UNKNOWN", "ACTIVE_INDIVIDUAL_GENERATION"]:
    r.cloud_state_mock = state
    try:
        blocked.append(r.is_cloud_blocked())
    except Exception:
        blocked.append(True)
rows.append({"probe": "cloud active/unknown states blocked", "pass": all(blocked)})

r = runner("malformed-pacing")
r.pacing_file.write_text("corrupted json {{")
try:
    r.load_pacing()
    pacing_blocked = False
except Exception:
    pacing_blocked = True
rows.append({"probe": "malformed pacing fails closed", "pass": pacing_blocked})

p = PACK / "malformed-wa"
p.mkdir(parents=True, exist_ok=True)
(p / "write_ahead_request.json").write_text("")
r = runner("malformed-wa")
try:
    r.preflight_check([p])
    wa_failed = False
except m.UnknownLiabilityError:
    wa_failed = True
rows.append({"probe": "malformed write-ahead fails closed", "pass": wa_failed})

r = runner("normal-release")
r.acquire_mutex()
rows.append({"probe": "normal release succeeds", "pass": r.release_mutex() is True})

for mode in ["valid-baseline", "missing-body-hash", "invented-body-hash", "changed-prompt", "wrong-mime"]:
    p = PACK / f"iso-{mode}"
    p.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (64, 64), (90, 120, 80)).save(p / "output.png")
    b = (p / "output.png").read_bytes()
    h = hashlib.sha256(b).hexdigest()
    payload = {
        "contents": [{"role": "user", "parts": [{"text": "original prompt"}]}],
        "generationConfig": {"imageConfig": {"aspectRatio": "1:1", "imageSize": "2K"}},
    }
    body = json.dumps(payload, sort_keys=True).encode()
    (p / "request_body.json").write_bytes(body)
    resp = {"candidates": [{"content": {"parts": [{"inlineData": {
        "mimeType": "image/jpeg" if mode == "wrong-mime" else "image/png",
        "data": base64.b64encode(b).decode(),
    }}]}}]}
    respb = json.dumps(resp).encode()
    (p / "response.json").write_bytes(respb)
    wa = {
        "status": "SUCCEEDED", "itemId": "test-id", "sha256": h,
        "bodySHA256": hashlib.sha256(body).hexdigest(),
        "responseSHA256": hashlib.sha256(respb).hexdigest(),
    }
    if mode == "missing-body-hash":
        del wa["bodySHA256"]
    if mode == "invented-body-hash":
        wa["bodySHA256"] = "a" * 64
    (p / "write_ahead_request.json").write_text(json.dumps(wa))
    res = runner(f"iso-{mode}").execute_request(
        p, {"id": "test-id", "prompt": "different prompt" if mode == "changed-prompt" else "original prompt"}
    )
    passed = res["status"] == "REUSED_EXISTING_SUCCESS" if mode == "valid-baseline" else res["status"].startswith("FAILED_REUSE")
    rows.append({"probe": f"reuse-binding-{mode}", "pass": passed, "status": res.get("status")})

source_png = base64.b64encode(b"source-image-bytes").decode()
other_png = base64.b64encode(b"other-source-bytes").decode()

def strong(mode):
    p = PACK / f"strong-{mode}"
    p.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (32, 32), (20, 40, 60)).save(p / "output.png")
    raw = (p / "output.png").read_bytes()
    h = hashlib.sha256(raw).hexdigest()
    parts = [
        {"text": "original prompt"},
        {"inlineData": {"mimeType": "image/png", "data": source_png}},
    ]
    image_size = "2K"
    if mode == "missing-prompt-in-body":
        parts = [{"inlineData": {"mimeType": "image/png", "data": source_png}}]
    if mode == "wrong-config-image-size":
        image_size = "1K"
    if mode == "changed-source-image":
        parts[1]["inlineData"]["data"] = base64.b64encode(b"changed_source_bytes").decode()
    if mode == "swapped-source-order":
        parts = [
            {"inlineData": {"mimeType": "image/png", "data": other_png}},
            {"text": "original prompt"},
            {"inlineData": {"mimeType": "image/png", "data": source_png}},
        ]
    if mode == "wrong-aspect":
        aspect = "16:9"
    else:
        aspect = "1:1"
    payload = {"contents": [{"role": "user", "parts": parts}], "generationConfig": {"imageConfig": {"aspectRatio": aspect, "imageSize": image_size}}}
    body = b"not JSON" if mode == "malformed-body-valid-hash" else json.dumps(payload, sort_keys=True).encode()
    if mode != "missing-request-file":
        (p / "request_body.json").write_bytes(body)
    resp = {"candidates": [{"content": {"parts": [{"inlineData": {"mimeType": "image/png", "data": base64.b64encode(raw).decode()}}]}}]}
    rb = json.dumps(resp).encode()
    (p / "response.json").write_bytes(rb)
    wa = {
        "status": "SUCCEEDED", "itemId": "test-id", "sha256": h,
        "bodySHA256": hashlib.sha256(body).hexdigest(),
        "responseSHA256": hashlib.sha256(rb).hexdigest(),
        "model": m.MODEL, "endpoint": m.ENDPOINT,
    }
    if mode == "missing-response-hash":
        del wa["responseSHA256"]
    if mode == "missing-output-hash":
        del wa["sha256"]
    if mode == "wrong-model":
        wa["model"] = "wrong-model"
    if mode == "wrong-endpoint":
        wa["endpoint"] = "https://invalid.example.test/wrong"
    (p / "write_ahead_request.json").write_text(json.dumps(wa))
    meta = {
        "id": "test-id",
        "prompt": "original prompt",
        "expectedDimensions": [8, 8] if mode == "wrong-output-dimensions" else [32, 32],
        "imageSize": "2K",
        "aspectRatio": "1:1",
        "model": m.MODEL,
        "endpoint": m.ENDPOINT,
        "sources": [{"mimeType": "image/png", "data": source_png}],
        "partOrder": ["text", "inline"],
    }
    try:
        result = runner(f"s-{mode}").execute_request(p, meta)
    except Exception as e:
        result = {"status": "EXCEPTION", "error": str(e)}
    reused = result.get("status") == "REUSED_EXISTING_SUCCESS"
    return {"probe": mode, "pass": reused if mode == "valid" else not reused, "status": result.get("status")}

for mode in [
    "valid", "missing-request-file", "missing-response-hash", "malformed-body-valid-hash",
    "missing-prompt-in-body", "wrong-config-image-size", "wrong-model", "wrong-endpoint",
    "changed-source-image", "wrong-output-dimensions", "missing-output-hash",
    "swapped-source-order", "wrong-aspect",
]:
    rows.append(strong(mode))

report = {
    "sandbox": str(SANDBOX.relative_to(REPO)).replace("\\", "/"),
    "rootRedirectedBeforeImport": str(ROOT.relative_to(REPO)).replace("\\", "/"),
    "networkForbidden": True,
    "passing": sum(r["pass"] for r in rows),
    "failing": sum(not r["pass"] for r in rows),
    "rows": rows,
}
(SANDBOX / "v4-controls-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps({"passing": report["passing"], "failing": report["failing"], "fail": [r for r in rows if not r["pass"]]}, indent=2))
