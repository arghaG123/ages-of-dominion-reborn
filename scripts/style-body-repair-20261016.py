"""One photographic standing-body repair. Reuses the Vertex project and mutex.

Reserves 0.50 USD before the call. Refuses to start when retained exposure
plus this reservation would pass the 100 USD ceiling. Does not rewrite
historical ledger totals.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/plan/image-production"
LEDGER = PLAN / "budget-ledger.json"
MUTEX = PLAN / "submission.mutex.json"
LOCK = PLAN / "style-repair-20261016.lock"
PACK = ROOT / "qa/mock-led-executor-20261016/style-repair"
PROJECT = "project-eaa4c1cc-8f19-4d24-9e6"
ACCOUNT = "arghawork3@gmail.com"
MODEL = "gemini-3.1-flash-image"
ENDPOINT = (
    f"https://aiplatform.googleapis.com/v1/projects/{PROJECT}/locations/global/"
    f"publishers/google/models/{MODEL}:generateContent"
)
CEILING = 100.0
RESERVE = 0.50
REFERENCE = ROOT / "assets/derivatives/image-unified-reserve-20261009/actors/natives/class-knight-standing-body.png"

PROMPTS = {
    "mage": (
        "Use the reference only for photographic realism, studio lighting, camera distance, "
        "and a clean white background. Create a different person: one standing medieval mage. "
        "Natural adult proportions, exactly two arms, two hands, two legs and two feet on the ground. "
        "Layered wool robe, leather belt and plain boots. The right hand holds a simple wooden staff. "
        "No glow, no magic effects, no crown, no text, no labels, no extra people, no scenery, no frame. "
        "This must be a studio photograph, not a painting, illustration, anime or cartoon."
    ),
    "paladin": (
        "Use the reference only for photographic realism, studio lighting, camera distance, "
        "and a clean white background. Create a different person from the reference: one standing paladin. "
        "Natural adult proportions, exactly two arms, two hands, two legs and two feet. "
        "Polished plate armour over a plain cream surcoat with one simple red cross on the chest. "
        "No helmet plume, no lion emblem. The right hand holds a plain steel mace. No shield. "
        "No glow, no text, no labels, no extra people, no scenery. "
        "Studio photograph, not a painting, illustration, anime or cartoon."
    ),
    "barbarian": (
        "Use the reference only for photographic realism, studio lighting, camera distance, "
        "and a clean white background. Create one standing barbarian warrior, a different person. "
        "Natural adult proportions, exactly two arms, two hands, two legs and two feet. "
        "Fur cloak, leather bracers and boots, bare muscular arms. The right hand holds a plain wooden club. "
        "No horns, no oversized weapons, no text, no extra people, no scenery. "
        "Studio photograph, not a painting, illustration, anime or cartoon."
    ),
    "necromancer": (
        "Use the reference only for photographic realism, studio lighting, camera distance, "
        "and a clean white background. Create one standing person in a heavy dark wool robe, hood down. "
        "Natural adult proportions, exactly two arms, two hands, two legs and two feet. "
        "The right hand holds a plain dark wooden staff. Pale skin, no skulls, no bones, no smoke, no glow, "
        "no text, no extra people, no scenery. "
        "Studio photograph, not a painting, illustration, anime or cartoon."
    ),
    "healer": (
        "Use the reference only for photographic realism, studio lighting, camera distance, "
        "and a clean white background. Create one standing bearded herbalist, a different person. "
        "Natural adult proportions, exactly two arms, two hands, two legs and two feet. "
        "Linen hood, leather belt and herb pouches. The left hand holds a woven basket of herbs. "
        "The right hand holds a birch staff that reaches the ground and extends below the boots. "
        "No glow, no bones, no text, no extra people, no scenery. "
        "Studio photograph, not a painting, illustration, anime or cartoon."
    ),
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def token() -> str:
    result = subprocess.run(
        ["gcloud.cmd", "auth", "print-access-token", f"--account={ACCOUNT}", f"--project={PROJECT}"],
        capture_output=True, text=True, check=True,
    )
    return result.stdout.strip()


def exposure() -> float:
    ledger = read_json(LEDGER)
    protected = float(ledger["vertexRepair20261009"]["currentCommittedProtectedUSD"])
    extra = 0.0
    repair = ledger.get("styleRepair20261016", {})
    for attempt in repair.get("attempts", []):
        if attempt.get("retained"):
            extra += float(attempt["reservedUSD"])
    return protected + extra


def acquire() -> None:
    mutex = read_json(MUTEX)
    if mutex.get("active") is True or mutex.get("lastState") not in {
        "RELEASED_NO_PAID_DISPATCH", "RELEASED", "COMPLETED_CYCLE",
    }:
        if mutex.get("active") is True:
            raise SystemExit(f"mutex active: {mutex.get('owner')}")
    try:
        fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        raise SystemExit(f"style repair lock exists: {LOCK}")
    os.write(fd, b"held\n")
    os.close(fd)
    mutex.update({
        "owner": "style-body-repair-20261016",
        "acquiredAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "active": True,
        "lastState": "HELD",
        "workflow": "style-body-repair-20261016",
    })
    write_json(MUTEX, mutex)


def release(state: str) -> None:
    mutex = read_json(MUTEX)
    mutex["active"] = False
    mutex["lastState"] = state
    mutex["releasedAt"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    write_json(MUTEX, mutex)
    if LOCK.exists():
        LOCK.unlink()


def record(attempt: dict) -> None:
    ledger = read_json(LEDGER)
    repair = ledger.setdefault("styleRepair20261016", {
        "authority": "Owner 16 October 2026: up to 20 USD beyond 80, absolute ceiling 100, for style and Healer fixes only.",
        "ceilingUSD": CEILING,
        "attempts": [],
    })
    repair["attempts"].append(attempt)
    repair["retainedUSD"] = round(sum(float(item["reservedUSD"]) for item in repair["attempts"] if item.get("retained")), 4)
    write_json(LEDGER, ledger)


def generate(class_id: str, attempt_n: str) -> None:
    if class_id not in PROMPTS:
        raise SystemExit(f"no prompt for {class_id}")
    current = exposure()
    if current + RESERVE > CEILING:
        raise SystemExit(f"reservation {RESERVE} would pass ceiling {CEILING}; exposure {current}")
    reference = REFERENCE.read_bytes()
    prompt = PROMPTS[class_id]
    pack = PACK / class_id
    pack.mkdir(parents=True, exist_ok=True)
    ahead = {
        "classId": class_id,
        "reservedUSD": RESERVE,
        "referenceSHA256": sha256_bytes(reference),
        "promptSHA256": hashlib.sha256(prompt.encode()).hexdigest(),
        "model": MODEL,
        "imageSize": "2K",
        "aspectRatio": "1:1",
        "writtenAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    write_json(pack / f"write_ahead_request_{attempt_n}.json", ahead)
    attempt = {
        "attemptId": f"style-{class_id}-standing-body-v1-{attempt_n}",
        "scene": f"class-{class_id}-standing-body",
        "reservedUSD": RESERVE,
        "retained": True,
        "status": "RESERVED_UNSENT",
        "at": ahead["writtenAt"],
    }
    record(attempt)
    payload = {
        "contents": [{
            "role": "user",
            "parts": [
                {"text": prompt},
                {"inlineData": {"mimeType": "image/png", "data": base64.b64encode(reference).decode("ascii")}},
            ],
        }],
        "generationConfig": {
            "candidateCount": 1,
            "maxOutputTokens": 4096,
            "responseModalities": ["IMAGE"],
            "imageConfig": {"aspectRatio": "1:1", "imageSize": "2K"},
        },
    }
    attempt["status"] = "SENDING"
    body = json.dumps(payload).encode()
    request = urllib.request.Request(
        ENDPOINT, data=body, method="POST",
        headers={"Authorization": "Bearer " + token(), "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            raw = response.read()
    except urllib.error.HTTPError as err:
        detail = err.read().decode("utf-8", "replace")[:500]
        attempt["status"] = f"HTTP_{err.code}"
        attempt["error"] = detail
        wait = 20
        if err.code == 429:
            attempt["status"] = "HTTP_429_RETAINED"
            retry_after = err.headers.get("Retry-After") if err.headers else None
            wait = max(60, int(retry_after) if retry_after and retry_after.isdigit() else 60)
        record_replace(attempt)
        print(f"FAIL {attempt['attemptId']} wait {wait}s", flush=True)
        time.sleep(wait)
        raise SystemExit(f"HTTP {err.code}: {detail}")
    except (TimeoutError, OSError) as err:
        attempt["status"] = "UNKNOWN_READ_TIMEOUT"
        attempt["error"] = str(err)
        record_replace(attempt)
        print(f"FAIL {attempt['attemptId']} wait 20s", flush=True)
        time.sleep(20)
        raise SystemExit(f"timeout: {err}")
    (pack / "response.json").write_bytes(raw)
    parsed = json.loads(raw)
    image = None
    for part in parsed.get("candidates", [{}])[0].get("content", {}).get("parts", []):
        if "inlineData" in part:
            image = base64.b64decode(part["inlineData"]["data"])
            break
    if not image:
        attempt["status"] = "NO_IMAGE_RETAINED"
        record_replace(attempt)
        raise SystemExit("response contained no image")
    out = pack / "native.png"
    out.write_bytes(image)
    usage = parsed.get("usageMetadata", {})
    attempt.update({
        "status": "SUCCEEDED_CANDIDATE",
        "output": str(out.relative_to(ROOT)).replace("\\", "/"),
        "outputSHA256": sha256_bytes(image),
        "promptTokens": usage.get("promptTokenCount"),
        "candidateTokens": usage.get("candidatesTokenCount"),
    })
    record_replace(attempt)
    print(attempt["outputSHA256"], out)
    time.sleep(20)


def record_replace(attempt: dict) -> None:
    ledger = read_json(LEDGER)
    attempts = ledger["styleRepair20261016"]["attempts"]
    for index, item in enumerate(attempts):
        if item["attemptId"] == attempt["attemptId"] and item.get("status") in {"RESERVED_UNSENT", "SENDING"}:
            attempts[index] = attempt
            break
    else:
        attempts.append(attempt)
    ledger["styleRepair20261016"]["retainedUSD"] = round(
        sum(float(item["reservedUSD"]) for item in attempts if item.get("retained")), 4
    )
    write_json(LEDGER, ledger)


def main() -> None:
    class_id = sys.argv[1]
    attempt_n = sys.argv[2] if len(sys.argv) > 2 else "a1"
    acquire()
    try:
        generate(class_id, attempt_n)
    except Exception:
        release("RELEASED")
        raise
    release("RELEASED")


if __name__ == "__main__":
    main()
