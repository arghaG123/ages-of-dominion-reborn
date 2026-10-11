"""Sole Vertex coordinator for the 9 October 2026 unified reserve pass.

Adapted from the vertex-repair coordinator. This module does not submit on import.
Historical safetyReserve 15 and protected exposure 79.8327 stay in the ledger.
Effective policy for this task is protected reserve 0 and prior liability 64.8327.
Successful-call gap is 30 seconds. Implicit HTTP retries are not used.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

PROJECT = "project-eaa4c1cc-8f19-4d24-9e6"
ACCOUNT = "arghawork3@gmail.com"
MODEL = "gemini-3.1-flash-image"
BUCKET = f"{PROJECT}-aod-batch"
LOCK_OBJECT = "design-mocks/active-batch.lock.json"
ENDPOINT = (
    f"https://aiplatform.googleapis.com/v1/projects/{PROJECT}/locations/global/"
    f"publishers/google/models/{MODEL}:generateContent"
)
HARD_CAP_USD = 80.0
HISTORICAL_PROTECTED_USD = 79.8327
HISTORICAL_RESERVE_USD = 15.0
PRIOR_LIABILITY_EXCLUDING_RESERVE_USD = 64.8327
REMAINING_HEADROOM_USD = 15.1673
SUCCESS_GAP_SECONDS = 30.0
BACKOFF_429_SECONDS = 60.0
OWNER_QUOTE = "use $15 reserve and instruct remain work and solution to do for one AI with a prompt."
AUTHORITY_DOCUMENT = "docs/plan/OWNER-RESERVE-RELEASE-SINGLE-IMAGE-AI-2026-10-09.md"

# Vertex pricing page, Gemini 3.1 Flash Image, standard tier, read 9 October 2026:
# input text/image $0.50 / 1M, text output $3 / 1M, image output $60 / 1M.
# Input image 1120 tokens. Output 1680 tokens at 2K ($0.1008) and 2520 at 4K ($0.1512).
INPUT_PER_1M = 0.50
TEXT_PER_1M = 3.00
IMAGE_PER_1M = 60.00
TOKENS_2K = 1680
TOKENS_4K = 2520
INPUT_IMAGE_TOKENS = 1120


class MutexError(Exception):
    pass


class AuthError(Exception):
    pass


class UnknownLiabilityError(Exception):
    pass


class QuotaStop(Exception):
    pass


class BudgetError(Exception):
    pass


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def estimate_upper_bound_usd(resolution: str, input_images: int, prompt_chars: int) -> float:
    """Worst case: two image outputs, declared inputs, text, 2048 thinking tokens, overhead."""
    out_tokens = TOKENS_4K if resolution == "4K" else TOKENS_2K
    output_cost = 2 * out_tokens * IMAGE_PER_1M / 1_000_000
    input_image_cost = max(0, input_images) * INPUT_IMAGE_TOKENS * IMAGE_PER_1M / 1_000_000
    text_cost = (max(prompt_chars, 0) / 4) * INPUT_PER_1M / 1_000_000
    thinking_cost = 2048 * TEXT_PER_1M / 1_000_000
    return round(output_cost + input_image_cost + text_cost + thinking_cost + 0.05, 4)


def release_record_template(recorded_at: str) -> dict:
    return {
        "id": "OWNER_RESERVE_RELEASE_20261009",
        "recordedAt": recorded_at,
        "ownerQuote": OWNER_QUOTE,
        "authorityDocument": AUTHORITY_DOCUMENT,
        "releasedReserveUSD": HISTORICAL_RESERVE_USD,
        "effectiveProtectedReserveUSD": 0.0,
        "priorProtectedExposureUSD": HISTORICAL_PROTECTED_USD,
        "priorLiabilityExcludingReserveUSD": PRIOR_LIABILITY_EXCLUDING_RESERVE_USD,
        "remainingHeadroomUSD": REMAINING_HEADROOM_USD,
        "hardCapUSD": HARD_CAP_USD,
        "historicalSafetyReservePreservedUSD": HISTORICAL_RESERVE_USD,
        "historicalCurrentCommittedProtectedUSD": HISTORICAL_PROTECTED_USD,
        "invoiceStatus": "UNKNOWN",
        "note": (
            "Effective reserve is 0 for this authorized task. "
            "Do not subtract 15 from a balance that already excludes it. "
            "Historical safetyReserve and 79.8327 exposure stay in place."
        ),
    }


def append_release_once(ledger: dict, recorded_at: str) -> dict:
    """Append the effective policy once. Historical reserve and exposure fields stay."""
    if float(ledger.get("safetyReserve", -1)) != HISTORICAL_RESERVE_USD:
        raise BudgetError("historical safetyReserve is missing or was changed")
    section = ledger.get("vertexRepair20261009")
    if not isinstance(section, dict) or float(section.get("currentCommittedProtectedUSD", -1)) != HISTORICAL_PROTECTED_USD:
        raise BudgetError("historical currentCommittedProtectedUSD is missing or was changed")
    existing = ledger.get("ownerReserveRelease20261009")
    record = release_record_template(recorded_at)
    if existing is not None:
        raise BudgetError("reserve release already recorded; refusing a second subtraction")
    ledger["ownerReserveRelease20261009"] = record
    ledger["effectivePolicy20261009"] = {
        "effectiveProtectedReserveUSD": 0.0,
        "priorLiabilityExcludingReserveUSD": PRIOR_LIABILITY_EXCLUDING_RESERVE_USD,
        "hardCapUSD": HARD_CAP_USD,
        "remainingHeadroomAtReleaseUSD": REMAINING_HEADROOM_USD,
        "consumers": "image-unified-reserve-20261009 coordinator guard_post",
    }
    return record


def assert_release_authority(record: dict | None) -> dict:
    if not isinstance(record, dict):
        raise BudgetError("missing release authority")
    if record.get("ownerQuote") != OWNER_QUOTE:
        raise BudgetError("stale or missing release authority")
    if record.get("authorityDocument") != AUTHORITY_DOCUMENT:
        raise BudgetError("stale release authority document")
    if float(record.get("releasedReserveUSD", -1)) != HISTORICAL_RESERVE_USD:
        raise BudgetError("stale releasedReserveUSD")
    if float(record.get("effectiveProtectedReserveUSD", -1)) != 0.0:
        raise BudgetError("effective reserve is not 0")
    if float(record.get("priorLiabilityExcludingReserveUSD", -1)) != PRIOR_LIABILITY_EXCLUDING_RESERVE_USD:
        raise BudgetError("prior liability does not match the single release")
    if float(record.get("hardCapUSD", -1)) != HARD_CAP_USD:
        raise BudgetError("hard cap is not 80")
    return record


def guard_post(
    *,
    release: dict | None,
    prior_liability_usd: float,
    other_effective_holds_usd: float,
    new_reservation_usd: float,
    effective_reserve_usd: float,
    known_attempt_ids: set[str],
    attempt_id: str,
    unknown_outstanding: bool,
    double_subtracted: bool,
) -> dict:
    """Reject unsafe POSTs. Returns the exposure breakdown when the POST may be reserved."""
    assert_release_authority(release)
    if double_subtracted:
        raise BudgetError("double subtraction of the released reserve")
    if unknown_outstanding:
        raise BudgetError("unknown dispatch blocks paid work")
    if attempt_id in known_attempt_ids:
        raise BudgetError(f"duplicate hold {attempt_id}")
    if new_reservation_usd <= 0:
        raise BudgetError("reservation must be a positive worst-case bound")
    # A caller that already removed the reserve and then passes prior_liability
    # below the reconciled 64.8327 is treating the release twice.
    if prior_liability_usd < PRIOR_LIABILITY_EXCLUDING_RESERVE_USD - 1e-6:
        raise BudgetError("prior liability is below the reconciled release balance")
    if abs(effective_reserve_usd - float(release["effectiveProtectedReserveUSD"])) > 1e-9:
        raise BudgetError("effective reserve does not match the release record")
    total = round(prior_liability_usd + other_effective_holds_usd + new_reservation_usd + effective_reserve_usd, 6)
    headroom = round(HARD_CAP_USD - (prior_liability_usd + other_effective_holds_usd + effective_reserve_usd), 6)
    if new_reservation_usd > headroom + 1e-9 or total > HARD_CAP_USD + 1e-9:
        raise BudgetError(
            f"insufficient worst-case funds: reservation {new_reservation_usd} total {total} cap {HARD_CAP_USD}"
        )
    return {"totalUSD": total, "headroomBeforeUSD": headroom, "authorized": True}


def parse_retry_after(header_val, now_fn=time.time) -> float:
    if header_val is None:
        return 0.0
    text = str(header_val).strip()
    try:
        return max(0.0, float(text))
    except ValueError:
        pass
    try:
        when = parsedate_to_datetime(text)
        if when.tzinfo is None:
            when = when.replace(tzinfo=timezone.utc)
        return max(0.0, when.timestamp() - now_fn())
    except Exception:
        return 0.0


class Coordinator:
    def __init__(
        self,
        work_dir: Path,
        owner_id: str | None = None,
        prior_liability_usd: float = PRIOR_LIABILITY_EXCLUDING_RESERVE_USD,
        effective_reserve_usd: float = 0.0,
        hard_cap_usd: float = HARD_CAP_USD,
        release: dict | None = None,
        cloud_lock_enabled: bool = False,
        mutex_file: Path | None = None,
        pacing_file: Path | None = None,
        transport=None,
        token_provider=None,
        cloud=None,
        clock=time.time,
        sleeper=time.sleep,
        success_gap: float = SUCCESS_GAP_SECONDS,
        backoff_429: float = BACKOFF_429_SECONDS,
    ):
        self.work_dir = Path(work_dir)
        self.work_dir.mkdir(parents=True, exist_ok=True)
        self.pid = os.getpid()
        self.run_uuid = uuid.uuid4().hex
        self.owner_id = owner_id or f"image-unified-reserve-20261009-{self.run_uuid[:8]}-pid{self.pid}"
        self.prior_liability_usd = float(prior_liability_usd)
        self.effective_reserve_usd = float(effective_reserve_usd)
        self.hard_cap_usd = float(hard_cap_usd)
        self.release = release
        self.cloud_lock_enabled = cloud_lock_enabled
        self.transport = transport
        self.token_provider = token_provider
        self.cloud = cloud
        self.clock = clock
        self.sleeper = sleeper
        self.success_gap = float(success_gap)
        self.backoff_429 = float(backoff_429)
        self.mutex_file = Path(mutex_file) if mutex_file else self.work_dir / "submission.mutex.json"
        self.pacing_file = Path(pacing_file) if pacing_file else self.work_dir / "pacing_state.json"
        self.reservation_file = self.work_dir / "reservations.json"
        self.cloud_lock_generation = None
        self.has_lock = False
        self.blocked = False
        self.block_reason = None
        self.unresolved_items: list[str] = []
        self._load_pacing()
        self._load_reservations()

    def other_holds_usd(self) -> float:
        return round(sum(r["reservedUSD"] for r in self.reservations if r.get("retained")), 6)

    def _load_reservations(self):
        if self.reservation_file.exists():
            self.reservations = json.loads(self.reservation_file.read_text(encoding="utf-8"))
        else:
            self.reservations = []

    def _save_reservations(self):
        self._atomic_write(self.reservation_file, json.dumps(self.reservations, indent=2).encode("utf-8"))

    def _atomic_write(self, path: Path, data: bytes):
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + f".tmp.{self.pid}.{uuid.uuid4().hex[:6]}")
        tmp.write_bytes(data)
        os.replace(tmp, path)

    def _load_pacing(self):
        self.next_allowed_post_at = 0.0
        self.next_eligible_retry_at = 0.0
        self.last_completed_at = 0.0
        if not self.pacing_file.exists():
            return
        content = self.pacing_file.read_text(encoding="utf-8").strip()
        if not content:
            raise ValueError(f"Pacing file is empty: {self.pacing_file}")
        data = json.loads(content)
        self.next_allowed_post_at = float(data.get("nextAllowedPOSTAtTs", 0.0))
        self.next_eligible_retry_at = float(data.get("nextEligibleRetryAtTs", 0.0))
        self.last_completed_at = float(data.get("lastCompletedAtTs", 0.0))

    def _save_pacing(self):
        data = {
            "lastCompletedAtTs": self.last_completed_at,
            "nextAllowedPOSTAtTs": self.next_allowed_post_at,
            "nextEligibleRetryAtTs": self.next_eligible_retry_at,
            "successGapSeconds": self.success_gap,
            "updatedAt": datetime.now(timezone.utc).isoformat(),
            "owner": self.owner_id,
        }
        self._atomic_write(self.pacing_file, json.dumps(data, indent=2).encode("utf-8"))

    def acquire_mutex(self):
        self.mutex_file.parent.mkdir(parents=True, exist_ok=True)
        if self.mutex_file.exists():
            content = self.mutex_file.read_text(encoding="utf-8").strip()
            if not content:
                raise MutexError("Mutex file exists but is empty")
            data = json.loads(content)
            state = str(data.get("lastState", ""))
            if "UNKNOWN" in state:
                raise MutexError(f"Mutex retains UNKNOWN state from {data.get('owner')}")
            if data.get("active") is True:
                raise MutexError(f"Mutex actively held by {data.get('owner')} pid {data.get('pid')}")
        excl = self.mutex_file.with_suffix(self.mutex_file.suffix + ".excl")
        if excl.exists():
            raise MutexError(f"Exclusive token already held: {excl.name}")
        try:
            fd = os.open(str(excl), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError as exc:
            raise MutexError("Exclusive token collision") from exc
        os.write(fd, f"{self.owner_id}:{self.pid}:{self.run_uuid}".encode("utf-8"))
        os.close(fd)
        lock_data = {
            "owner": self.owner_id,
            "pid": self.pid,
            "runUuid": self.run_uuid,
            "acquiredAt": datetime.now(timezone.utc).isoformat(),
            "active": True,
            "lastState": "ACQUIRED",
            "workflow": "image-unified-reserve-20261009",
            "historicalOwnerPreserved": True,
        }
        self._atomic_write(self.mutex_file, json.dumps(lock_data, indent=2).encode("utf-8"))
        verified = json.loads(self.mutex_file.read_text(encoding="utf-8"))
        if verified.get("owner") != self.owner_id or verified.get("pid") != self.pid:
            self._drop_excl()
            raise MutexError("Mutex overwritten by another owner")
        if self.cloud_lock_enabled:
            self._acquire_cloud_lock()
        self.has_lock = True
        return True

    def _drop_excl(self):
        excl = self.mutex_file.with_suffix(self.mutex_file.suffix + ".excl")
        if excl.exists():
            try:
                os.remove(excl)
            except OSError:
                pass

    def _token(self) -> str:
        if self.token_provider:
            return self.token_provider()
        raise AuthError("No token provider configured")

    def _acquire_cloud_lock(self):
        token = self._token()
        current, generation = self._get_cloud_lock(token)
        if current:
            state = str(current.get("state", "")).upper()
            workflow = str(current.get("workflow_state", "")).upper()
            active = {
                "JOB_STATE_RUNNING", "JOB_STATE_PENDING", "JOB_STATE_QUEUED",
                "ACTIVE_INDIVIDUAL_GENERATION", "JOB_STATE_UNKNOWN", "UNKNOWN",
                "UNKNOWN_CRASH_DURING_DISPATCH", "SENDING_POST",
            }
            if state in active or workflow in active or not state:
                self._drop_excl()
                raise MutexError(f"Cloud lock active or unknown ({state}/{workflow}) owner {current.get('owner')}")
        payload = {
            "batch_id": "image-unified-reserve-20261009",
            "model": MODEL,
            "project": PROJECT,
            "account": ACCOUNT,
            "state": "JOB_STATE_RUNNING",
            "workflow_state": "ACTIVE_INDIVIDUAL_GENERATION",
            "owner": self.owner_id,
            "pid": self.pid,
            "createdAt": datetime.now(timezone.utc).isoformat(),
        }
        self.cloud_lock_generation = self._put_cloud_lock(payload, generation, token)

    def _get_cloud_lock(self, token: str):
        if self.cloud:
            return self.cloud["get"]()
        meta_url = (
            "https://storage.googleapis.com/storage/v1/b/"
            f"{BUCKET}/o/{urllib.parse.quote(LOCK_OBJECT, safe='')}"
        )
        req = urllib.request.Request(meta_url, headers={"Authorization": "Bearer " + token})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                meta = json.loads(resp.read().decode("utf-8"))
            generation = str(meta.get("generation"))
            media = urllib.request.Request(meta_url + "?alt=media", headers={"Authorization": "Bearer " + token})
            with urllib.request.urlopen(media, timeout=30) as resp:
                content = json.loads(resp.read().decode("utf-8"))
            return content, generation
        except urllib.error.HTTPError as err:
            if err.code == 404:
                return None, "0"
            raise

    def _put_cloud_lock(self, lock_data: dict, match_generation: str, token: str) -> str:
        if self.cloud:
            return self.cloud["put"](lock_data, match_generation)
        url = (
            "https://storage.googleapis.com/upload/storage/v1/b/"
            f"{BUCKET}/o?uploadType=media&name={urllib.parse.quote(LOCK_OBJECT, safe='')}"
            f"&ifGenerationMatch={match_generation}"
        )
        body = json.dumps(lock_data, indent=2).encode("utf-8")
        req = urllib.request.Request(
            url, data=body, method="POST",
            headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            meta = json.loads(resp.read().decode("utf-8"))
        return str(meta.get("generation"))

    def release_mutex(self, state: str = "RELEASED"):
        if not self.has_lock:
            return False
        if self.unresolved_items or "UNKNOWN" in state or self.blocked:
            data = json.loads(self.mutex_file.read_text(encoding="utf-8"))
            data["active"] = True
            data["lastState"] = "UNKNOWN" if self.unresolved_items or "UNKNOWN" in state else state
            data["unresolvedItems"] = list(self.unresolved_items)
            data["blockReason"] = self.block_reason
            self._atomic_write(self.mutex_file, json.dumps(data, indent=2).encode("utf-8"))
            return False
        data = json.loads(self.mutex_file.read_text(encoding="utf-8"))
        data["active"] = False
        data["lastState"] = state
        data["releasedAt"] = datetime.now(timezone.utc).isoformat()
        self._atomic_write(self.mutex_file, json.dumps(data, indent=2).encode("utf-8"))
        self._drop_excl()
        if self.cloud_lock_enabled and self.cloud_lock_generation:
            try:
                self._put_cloud_lock({
                    "batch_id": "image-unified-reserve-20261009",
                    "model": MODEL,
                    "project": PROJECT,
                    "account": ACCOUNT,
                    "state": "JOB_STATE_SUCCEEDED",
                    "workflow_state": "TERMINAL_COLLECTED",
                    "owner": self.owner_id,
                    "releasedAt": datetime.now(timezone.utc).isoformat(),
                    "lastState": state,
                }, self.cloud_lock_generation, self._token())
            except Exception as exc:
                self.blocked = True
                self.block_reason = f"Cloud lock release failed: {type(exc).__name__}"
                return False
        self.has_lock = False
        return True

    def _enforce_pacing(self):
        self._load_pacing()
        now = self.clock()
        wait = 0.0
        if now < self.next_allowed_post_at:
            wait = max(wait, self.next_allowed_post_at - now)
        if now < self.next_eligible_retry_at:
            wait = max(wait, self.next_eligible_retry_at - now)
        if wait > 0:
            self.sleeper(wait)

    def _retain(self, attempt_id: str, reserved: float, status: str):
        for row in self.reservations:
            if row["attemptId"] == attempt_id:
                raise BudgetError(f"duplicate hold {attempt_id}")
        self.reservations.append({
            "attemptId": attempt_id,
            "reservedUSD": reserved,
            "status": status,
            "retained": True,
            "recordedAt": datetime.now(timezone.utc).isoformat(),
        })
        self._save_reservations()

    def execute_prepared(self, pack_dir: Path, wire_bytes: bytes, item_meta: dict, reservation_usd: float) -> dict:
        if not self.has_lock:
            raise MutexError("Cannot send without the owned mutex")
        item_id = item_meta["id"]
        attempt_id = item_meta["attemptId"]
        body_sha = sha256_bytes(wire_bytes)
        if body_sha != item_meta.get("wireBodySHA256"):
            raise BudgetError("Wire bytes do not match the prepared hash")
        pack_dir = Path(pack_dir)
        pack_dir.mkdir(parents=True, exist_ok=True)
        wa_path = pack_dir / "write_ahead_request.json"
        if wa_path.exists():
            prior = json.loads(wa_path.read_text(encoding="utf-8"))
            if prior.get("status") == "SUCCEEDED" and prior.get("bodySHA256") == body_sha and prior.get("attemptId") == attempt_id:
                return {"status": "REUSED_SUCCESS", "itemId": item_id, "attemptId": attempt_id, "costUSD": 0.0, "sent": False}
            if prior.get("status") in {"UNKNOWN", "SENDING_POST", "UNKNOWN_CRASH_DURING_DISPATCH"}:
                self.unresolved_items.append(item_id)
                self.blocked = True
                self.block_reason = f"Existing {prior.get('status')} for {item_id}"
                raise UnknownLiabilityError(self.block_reason)
        if self.blocked or self.unresolved_items:
            raise UnknownLiabilityError(f"Paid dispatch blocked: {self.block_reason or self.unresolved_items}")
        guard_post(
            release=self.release,
            prior_liability_usd=self.prior_liability_usd,
            other_effective_holds_usd=self.other_holds_usd(),
            new_reservation_usd=float(reservation_usd),
            effective_reserve_usd=self.effective_reserve_usd,
            known_attempt_ids={r["attemptId"] for r in self.reservations},
            attempt_id=attempt_id,
            unknown_outstanding=bool(self.unresolved_items),
            double_subtracted=False,
        )
        req_path = pack_dir / "request_body.json"
        sub_path = pack_dir / "write_ahead_subattempt_1.json"
        if sub_path.exists():
            raise BudgetError(f"Subattempt 1 already recorded for {item_id}; refusing duplicate")
        write_ahead = {
            "itemId": item_id,
            "attemptId": attempt_id,
            "ownerQueue": item_meta.get("owner", "ACTORS"),
            "bodySHA256": body_sha,
            "reservationUSD": reservation_usd,
            "subattempt": 1,
            "status": "SENDING_POST",
            "endpoint": ENDPOINT,
            "project": PROJECT,
            "model": MODEL,
            "owner": self.owner_id,
            "recordedAt": datetime.now(timezone.utc).isoformat(),
        }
        self._atomic_write(req_path, wire_bytes)
        if sha256_bytes(req_path.read_bytes()) != body_sha:
            raise BudgetError("Persisted body hash drifted before send")
        self._atomic_write(wa_path, json.dumps(write_ahead, indent=2).encode("utf-8"))
        self._atomic_write(sub_path, json.dumps(write_ahead, indent=2).encode("utf-8"))
        self._retain(attempt_id, reservation_usd, "RESERVED_BEFORE_POST")
        self._enforce_pacing()
        try:
            if self.transport:
                resp_bytes, http_code, headers = self.transport(ENDPOINT, wire_bytes)
            else:
                resp_bytes, http_code, headers = self._post(wire_bytes)
        except QuotaStop:
            raise
        except UnknownLiabilityError:
            self._mark_unknown(wa_path, write_ahead, "AMBIGUOUS_TRANSPORT")
            raise
        except Exception as exc:
            self._mark_unknown(wa_path, write_ahead, f"DISPATCH_EXCEPTION:{type(exc).__name__}")
            raise UnknownLiabilityError(str(exc)) from exc
        if req_path.read_bytes() != wire_bytes:
            self._mark_unknown(wa_path, write_ahead, "BODY_MUTATED_AFTER_SEND")
            raise UnknownLiabilityError("Wire bytes changed after dispatch")
        return self._finalize(pack_dir, wa_path, write_ahead, resp_bytes, http_code, headers, item_meta)

    def _post(self, wire_bytes: bytes):
        token = self._token()
        req = urllib.request.Request(
            ENDPOINT, data=wire_bytes, method="POST",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                return resp.read(), resp.status, dict(resp.headers)
        except urllib.error.HTTPError as err:
            body = err.read()
            headers = dict(err.headers or {})
            if err.code == 429:
                raise QuotaStop(json.dumps({"code": 429, "headers": headers, "body": body.decode("utf-8", "replace")[:4000]}))
            if err.code in {401, 403}:
                raise AuthError(f"HTTP {err.code}")
            if err.code >= 500:
                raise UnknownLiabilityError(f"HTTP {err.code}")
            return body, err.code, headers
        except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
            raise UnknownLiabilityError(type(exc).__name__) from exc

    def _mark_unknown(self, wa_path: Path, write_ahead: dict, reason: str):
        write_ahead["status"] = "UNKNOWN"
        write_ahead["reason"] = reason
        self._atomic_write(wa_path, json.dumps(write_ahead, indent=2).encode("utf-8"))
        self.unresolved_items.append(write_ahead["itemId"])
        self.blocked = True
        self.block_reason = reason
        for row in self.reservations:
            if row["attemptId"] == write_ahead["attemptId"]:
                row["status"] = "UNKNOWN"
                row["retained"] = True
        self._save_reservations()

    def _finalize(self, pack_dir, wa_path, write_ahead, resp_bytes, http_code, headers, item_meta):
        sub_id = f"{write_ahead['attemptId']}-sub1"
        raw_path = pack_dir / "responses" / f"{sub_id}.json"
        self._atomic_write(raw_path, resp_bytes if isinstance(resp_bytes, bytes) else bytes(resp_bytes))
        if int(http_code) == 429:
            retry_after = parse_retry_after(headers.get("Retry-After") or headers.get("retry-after"), self.clock)
            backoff = max(self.backoff_429, retry_after)
            self.next_eligible_retry_at = self.clock() + backoff
            self._save_pacing()
            write_ahead["status"] = "REJECTED"
            write_ahead["http"] = 429
            write_ahead["backoffSeconds"] = backoff
            self._atomic_write(wa_path, json.dumps(write_ahead, indent=2).encode("utf-8"))
            for row in self.reservations:
                if row["attemptId"] == write_ahead["attemptId"]:
                    row["status"] = "QUOTA_STOP_LIABILITY_RETAINED"
            self._save_reservations()
            self.blocked = True
            self.block_reason = "HTTP 429"
            raise QuotaStop(f"definite 429 backoff {backoff}")
        if int(http_code) >= 500:
            self._mark_unknown(wa_path, write_ahead, f"HTTP {http_code}")
            raise UnknownLiabilityError(f"HTTP {http_code}")
        if int(http_code) != 200:
            write_ahead["status"] = "FAILED"
            write_ahead["http"] = int(http_code)
            self._atomic_write(wa_path, json.dumps(write_ahead, indent=2).encode("utf-8"))
            for row in self.reservations:
                if row["attemptId"] == write_ahead["attemptId"]:
                    row["status"] = "FAILED_LIABILITY_RETAINED"
            self._save_reservations()
            self.last_completed_at = self.clock()
            self.next_allowed_post_at = self.last_completed_at + self.success_gap
            self._save_pacing()
            return {
                "status": "FAILED",
                "itemId": item_meta["id"],
                "attemptId": write_ahead["attemptId"],
                "subattemptId": sub_id,
                "rawResponse": str(raw_path),
                "sent": True,
            }
        write_ahead["status"] = "SUCCEEDED"
        write_ahead["rawResponse"] = raw_path.as_posix()
        self._atomic_write(wa_path, json.dumps(write_ahead, indent=2).encode("utf-8"))
        for row in self.reservations:
            if row["attemptId"] == write_ahead["attemptId"]:
                row["status"] = "SUCCEEDED_LIABILITY_RETAINED_UNTIL_INVOICE"
        self._save_reservations()
        self.last_completed_at = self.clock()
        self.next_allowed_post_at = self.last_completed_at + self.success_gap
        self._save_pacing()
        return {
            "status": "SUCCEEDED",
            "itemId": item_meta["id"],
            "attemptId": write_ahead["attemptId"],
            "subattemptId": sub_id,
            "rawResponse": raw_path.as_posix(),
            "sent": True,
            "reservedUSD": write_ahead["reservationUSD"],
        }
