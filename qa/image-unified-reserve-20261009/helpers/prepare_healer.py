"""Build one healer 2K wire from real pixels, then send one POST if the gates pass.

Does not append a reserve release. Does not mark the result READY.
A text-only wire is not sent. Auth failure on the single lock/jobs list stops dispatch.
"""
from __future__ import annotations

import base64
import hashlib
import json
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path

from PIL import Image

import coordinator as c
import process_local as pl

ROOT = pl.ROOT
BUST = ROOT / "assets/derivatives/image-residual-executor-20261007/actors/rigs/healer-head-front-bust.png"
NECK = ROOT / "assets/derivatives/image-residual-executor-20261007/actors/rigs/healer-head-front-neck.png"
BOOT = ROOT / "assets/derivatives/rigs/v7/healer/boot.png"
BOOT_SHA = "4a700eeedbabc9710db137491825d0c2ec439db15b10c619f0997a93accfab21"
LEDGER = ROOT / "docs/plan/image-production/budget-ledger.json"
MUTEX = ROOT / "docs/plan/image-production/submission.mutex.json"
PACING = ROOT / "docs/plan/image-production/pacing_state.json"
PACK = pl.QA / "vertex-coordinator/healer-class-standing-body"
PROMPT = (
    "Paint one still standing healer, full body, square, transparent background. "
    "Use the first image as the front bust and the second image as the front neck and head. "
    "Keep that face, hood, braid, and colors. "
    "Use the third image as the boot and put that same boot on both feet. "
    "The fourth image is a placement guide pasted from those real pixels, head above and boot below. "
    "Complete the torso, arms, hands, and legs between them. The figure stands facing forward, weight on both feet. "
    "No ground rectangle, no floor, no cast shadow, no text, no frame, and no second figure."
)


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def png_b64(path: Path) -> str:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError(f"not a png: {path}")
    return base64.b64encode(data).decode("ascii")


def build_guide() -> Path:
    bust = Image.open(BUST).convert("RGBA")
    neck = Image.open(NECK).convert("RGBA")
    boot = Image.open(BOOT).convert("RGBA")
    canvas = Image.new("RGBA", (560, 760), (0, 0, 0, 0))
    canvas.paste(bust, (16, 16), bust)
    canvas.paste(neck, (280, 16), neck)
    canvas.paste(boot, (212, 600), boot)
    dest = PACK / "guide-from-real-pixels.png"
    dest.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(dest, format="PNG")
    return dest


def build_wire(guide: Path) -> bytes:
    parts = [{"text": PROMPT}]
    for path in (BUST, NECK, BOOT, guide):
        parts.append({"inlineData": {"mimeType": "image/png", "data": png_b64(path)}})
    body = {
        "contents": [{"role": "user", "parts": parts}],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "candidateCount": 1,
            "imageConfig": {"aspectRatio": "1:1", "imageSize": "2K"},
        },
    }
    return json.dumps(body, separators=(",", ":")).encode("utf-8")


def decode_wire(wire: bytes, guide: Path) -> dict:
    parsed = json.loads(wire.decode("utf-8"))
    parts = []
    for content in parsed.get("contents") or []:
        parts.extend(content.get("parts") or [])
    images = [part["inlineData"] for part in parts if isinstance(part.get("inlineData"), dict)]
    decoded = []
    expected = [sha_file(BUST), sha_file(NECK), sha_file(BOOT), sha_file(guide)]
    for index, inline in enumerate(images):
        raw = base64.b64decode(inline["data"])
        if raw[:8] != b"\x89PNG\r\n\x1a\n":
            raise RuntimeError("inline part did not decode to a png")
        image = Image.open(BytesIO(raw))
        image.load()
        decoded.append({
            "index": index,
            "mimeType": inline.get("mimeType"),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "matchesSource": hashlib.sha256(raw).hexdigest() == expected[index],
            "size": list(image.size),
        })
    report = {
        "inlineImageCount": len(images),
        "textParts": sum(1 for part in parts if "text" in part),
        "decoded": decoded,
        "textOnly": len(images) == 0,
    }
    if report["textOnly"] or any(not row["matchesSource"] for row in decoded):
        raise RuntimeError("wire failed offline decode")
    return report


def confirm_ledger() -> dict:
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    if float(ledger.get("safetyReserve", -1)) != 15:
        raise c.BudgetError("historical safetyReserve changed")
    if float(ledger.get("hardCap", -1)) != 80:
        raise c.BudgetError("hard cap changed")
    repair = ledger.get("vertexRepair20261009") or {}
    if float(repair.get("currentCommittedProtectedUSD", -1)) != 79.8327:
        raise c.BudgetError("historical protected exposure changed")
    release = ledger.get("ownerReserveRelease20261009")
    c.assert_release_authority(release)
    policy = ledger.get("effectivePolicy20261009") or {}
    if float(policy.get("priorLiabilityExcludingReserveUSD", -1)) != 64.8327:
        raise c.BudgetError("prior liability changed")
    if float(policy.get("effectiveProtectedReserveUSD", -1)) != 0:
        raise c.BudgetError("effective reserve changed")
    return release


def token() -> str:
    gcloud = r"C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd"
    try:
        completed = subprocess.run(
            [gcloud, "auth", "print-access-token"],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
    except OSError as exc:
        raise c.AuthError(str(exc)) from exc
    if completed.returncode != 0:
        raise c.AuthError((completed.stderr or completed.stdout or "gcloud auth failed").strip()[:2000])
    value = completed.stdout.strip()
    if not value:
        raise c.AuthError("empty access token")
    return value


def get_json(url: str, access: str):
    request = urllib.request.Request(url, headers={"Authorization": "Bearer " + access})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        body = err.read().decode("utf-8", "replace")[:2000]
        if err.code == 404:
            return 404, None
        raise c.AuthError(f"HTTP {err.code} {body}") from err


def list_once(access: str) -> dict:
    lock_url = (
        "https://storage.googleapis.com/storage/v1/b/"
        f"{c.BUCKET}/o/{urllib.parse.quote(c.LOCK_OBJECT, safe='')}"
    )
    status, meta = get_json(lock_url, access)
    generation = "0"
    content = None
    if status != 404:
        generation = str(meta.get("generation"))
        code, content = get_json(lock_url + "?alt=media", access)
        if code == 404:
            content = None
    jobs_url = (
        "https://aiplatform.googleapis.com/v1/projects/"
        f"{c.PROJECT}/locations/global/batchPredictionJobs?pageSize=100"
        "&filter=" + urllib.parse.quote(
            'state="JOB_STATE_RUNNING" OR state="JOB_STATE_PENDING" OR state="JOB_STATE_QUEUED" OR state="JOB_STATE_UNSPECIFIED"'
        )
    )
    _status, jobs = get_json(jobs_url, access)
    rows = (jobs or {}).get("batchPredictionJobs") or []
    return {"lockStatus": status, "generation": generation, "lock": content, "activeJobs": rows}


def lock_is_terminal(lock) -> bool:
    if not lock:
        return True
    state = str(lock.get("state", "")).upper()
    workflow = str(lock.get("workflow_state", "")).upper()
    active = {
        "JOB_STATE_RUNNING", "JOB_STATE_PENDING", "JOB_STATE_QUEUED",
        "ACTIVE_INDIVIDUAL_GENERATION", "JOB_STATE_UNKNOWN", "UNKNOWN",
        "UNKNOWN_CRASH_DURING_DISPATCH", "SENDING_POST",
    }
    return bool(state) and state not in active and workflow not in active


def main():
    PACK.mkdir(parents=True, exist_ok=True)
    sources = {
        "bust": {"path": str(BUST.relative_to(ROOT)).replace("\\", "/"), "sha256": sha_file(BUST), "size": list(Image.open(BUST).size)},
        "secondHead": {"path": str(NECK.relative_to(ROOT)).replace("\\", "/"), "sha256": sha_file(NECK), "size": list(Image.open(NECK).size)},
        "boot": {"path": str(BOOT.relative_to(ROOT)).replace("\\", "/"), "sha256": sha_file(BOOT), "size": list(Image.open(BOOT).size)},
    }
    if sources["boot"]["sha256"] != BOOT_SHA:
        raise RuntimeError("boot hash does not match the protected crop")
    release = confirm_ledger()
    guide = build_guide()
    wire = build_wire(guide)
    decoded = decode_wire(wire, guide)
    if decoded["inlineImageCount"] <= 0:
        raise RuntimeError("refusing a text-only wire")
    bound = c.estimate_upper_bound_usd("2K", decoded["inlineImageCount"], len(PROMPT))
    guard = c.guard_post(
        release=release,
        prior_liability_usd=64.8327,
        other_effective_holds_usd=0.0,
        new_reservation_usd=bound,
        effective_reserve_usd=0.0,
        known_attempt_ids=set(),
        attempt_id="class-healer-standing-body-v1-a1",
        unknown_outstanding=False,
        double_subtracted=False,
    )
    report = {
        "sources": sources,
        "guide": str(guide.relative_to(ROOT)).replace("\\", "/"),
        "decoded": decoded,
        "wireSHA256": c.sha256_bytes(wire),
        "boundUSD": bound,
        "guard": guard,
        "posted": False,
        "recordedAt": datetime.now(timezone.utc).isoformat(),
    }
    (PACK / "decode-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (PACK / "request_body.json").write_bytes(wire)
    try:
        access = token()
    except c.AuthError as exc:
        report["dispatch"] = "STOPPED_AUTH"
        report["error"] = str(exc)
        (PACK / "decode-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(json.dumps(report, indent=2))
        return
    try:
        remote = list_once(access)
    except (c.AuthError, urllib.error.URLError, TimeoutError) as exc:
        report["dispatch"] = "STOPPED_AUTH"
        report["error"] = str(exc)[:2000]
        (PACK / "decode-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(json.dumps(report, indent=2))
        return
    lock_summary = None if not remote["lock"] else {
        "state": remote["lock"].get("state"),
        "workflow_state": remote["lock"].get("workflow_state"),
        "owner": remote["lock"].get("owner"),
    }
    report["cloudLock"] = {"http": remote["lockStatus"], "generation": remote["generation"], "summary": lock_summary}
    report["activeJobCount"] = len(remote["activeJobs"])
    report["activeJobs"] = [
        {"name": row.get("name"), "state": row.get("state"), "displayName": row.get("displayName")}
        for row in remote["activeJobs"]
    ]
    if not lock_is_terminal(remote["lock"]) or remote["activeJobs"]:
        report["dispatch"] = "STOPPED_REMOTE_NOT_TERMINAL"
        (PACK / "decode-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(json.dumps(report, indent=2))
        return
    cached = {"content": remote["lock"], "generation": remote["generation"]}

    def cloud_get():
        return cached["content"], cached["generation"]

    def cloud_put(lock_data, match_generation):
        url = (
            "https://storage.googleapis.com/upload/storage/v1/b/"
            f"{c.BUCKET}/o?uploadType=media&name={urllib.parse.quote(c.LOCK_OBJECT, safe='')}"
            f"&ifGenerationMatch={match_generation}"
        )
        body = json.dumps(lock_data, indent=2).encode("utf-8")
        request = urllib.request.Request(
            url, data=body, method="POST",
            headers={"Authorization": "Bearer " + access, "Content-Type": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            meta = json.loads(response.read().decode("utf-8"))
        cached["generation"] = str(meta.get("generation"))
        cached["content"] = lock_data
        return cached["generation"]

    runner = c.Coordinator(
        PACK,
        owner_id="image-unified-reserve-20261009-healer",
        release=release,
        cloud_lock_enabled=True,
        mutex_file=MUTEX,
        pacing_file=PACING,
        token_provider=lambda: access,
        cloud={"get": cloud_get, "put": cloud_put},
    )
    meta = {
        "id": "class-healer-standing-body",
        "attemptId": "class-healer-standing-body-v1-a1",
        "owner": "ACTORS",
        "wireBodySHA256": c.sha256_bytes(wire),
    }
    try:
        runner.acquire_mutex()
        result = runner.execute_prepared(PACK, wire, meta, bound)
        report["dispatch"] = result.get("status")
        report["posted"] = bool(result.get("sent"))
        report["result"] = {key: result[key] for key in result if key != "rawResponse"}
        report["rawResponse"] = result.get("rawResponse")
    except c.QuotaStop as exc:
        report["dispatch"] = "STOPPED_429"
        report["posted"] = True
        report["error"] = str(exc)[:2000]
    except (c.AuthError, c.UnknownLiabilityError, c.MutexError, c.BudgetError) as exc:
        report["dispatch"] = type(exc).__name__
        report["error"] = str(exc)[:2000]
        report["posted"] = isinstance(exc, c.UnknownLiabilityError)
        if not runner.has_lock and MUTEX.exists():
            current = json.loads(MUTEX.read_text(encoding="utf-8"))
            if current.get("active") is True and current.get("owner") == runner.owner_id:
                current["active"] = False
                current["lastState"] = "RELEASED_NO_PAID_DISPATCH"
                current["releasedAt"] = datetime.now(timezone.utc).isoformat()
                MUTEX.write_text(json.dumps(current, indent=2), encoding="utf-8")
                runner._drop_excl()
    finally:
        if runner.has_lock:
            state = "RELEASED_AFTER_HEALER_ATTEMPT" if report.get("posted") else "RELEASED_NO_PAID_DISPATCH"
            runner.release_mutex(state)
    holds = runner.other_holds_usd()
    report["holdsUSD"] = holds
    report["capacityBeforeUSD"] = 15.1673
    (PACK / "decode-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({key: report[key] for key in report if key != "decoded"}, indent=2))
    print("INLINE", decoded["inlineImageCount"])


if __name__ == "__main__":
    main()
