"""Vertex coordinator for the 9 October 2026 repair.

Adapted from scripts/interactive_runner_continuity.py. Historical hazards removed:
the later-73 batch id, hardcoded 1:1/2K payload, shared-path defaults, and the
in-loop HTTP 429 resend. A definite 429 stops the paid run and keeps the same body.
5xx, timeout, and disconnect become UNKNOWN and block every later send.
This module does not submit anything on import.
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
SUCCESS_GAP_SECONDS = 20.0
BACKOFF_429_SECONDS = 60.0

# Standard global rates inspected with the continuity runner. Output tokens are
# ceilings used only to reserve, not proof of an invoice.
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
    """Worst-case reserve: two output images, declared inputs, text, 2048 thinking tokens, overhead."""
    out_tokens = TOKENS_4K if resolution == "4K" else TOKENS_2K
    output_cost = 2 * out_tokens * IMAGE_PER_1M / 1_000_000
    input_image_cost = max(0, input_images) * INPUT_IMAGE_TOKENS * IMAGE_PER_1M / 1_000_000
    text_cost = (max(prompt_chars, 0) / 4) * INPUT_PER_1M / 1_000_000
    thinking_cost = 2048 * TEXT_PER_1M / 1_000_000
    return round(output_cost + input_image_cost + text_cost + thinking_cost + 0.05, 4)


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


def _body_text_parts(body_json: dict) -> list:
    texts = []
    for content in body_json.get("contents") or []:
        for part in content.get("parts") or []:
            if "text" in part:
                texts.append(part["text"])
    return texts


def _body_inline_parts(body_json: dict) -> list:
    inline = []
    for content in body_json.get("contents") or []:
        for part in content.get("parts") or []:
            if "inlineData" in part:
                inline.append(part["inlineData"])
    return inline


class Coordinator:
    def __init__(
        self,
        work_dir: Path,
        owner_id: str | None = None,
        committed_protected_usd: float = 71.1156,
        hard_cap_usd: float = HARD_CAP_USD,
        cloud_lock_enabled: bool = False,
        mutex_file: Path | None = None,
        pacing_file: Path | None = None,
        transport=None,
        token_provider=None,
        clock=time.time,
        sleeper=time.sleep,
        success_gap: float = SUCCESS_GAP_SECONDS,
        backoff_429: float = BACKOFF_429_SECONDS,
    ):
        self.work_dir = Path(work_dir)
        self.work_dir.mkdir(parents=True, exist_ok=True)
        self.pid = os.getpid()
        self.run_uuid = uuid.uuid4().hex
        self.owner_id = owner_id or f"environment-vertex-20261009-{self.run_uuid[:8]}-pid{self.pid}"
        self.committed_protected_usd = float(committed_protected_usd)
        self.hard_cap_usd = float(hard_cap_usd)
        self.cloud_lock_enabled = cloud_lock_enabled
        self.transport = transport
        self.token_provider = token_provider
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

    def exposure_usd(self) -> float:
        return round(self.committed_protected_usd + sum(r["reservedUSD"] for r in self.reservations if r.get("retained")), 6)

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
            "workflow": "vertex-repair-20261009",
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
            "batch_id": "vertex-repair-20261009",
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
        if self.block_reason == "HTTP 429" and not self.unresolved_items and "UNKNOWN" not in state:
            if self.cloud_lock_enabled and self.cloud_lock_generation:
                try:
                    self.cloud_lock_generation = self._put_cloud_lock({
                        "batch_id": "vertex-repair-20261009",
                        "model": MODEL,
                        "project": PROJECT,
                        "account": ACCOUNT,
                        "state": "QUOTA_STOP_HTTP_429",
                        "workflow_state": "PAID_RUN_STOPPED_DEFINITE_429",
                        "owner": self.owner_id,
                        "releasedAt": datetime.now(timezone.utc).isoformat(),
                        "lastState": "QUOTA_STOP_HTTP_429",
                    }, self.cloud_lock_generation, self._token())
                except Exception as exc:
                    self.blocked = True
                    self.block_reason = f"Cloud lock release failed: {type(exc).__name__}"
                    return False
            data = json.loads(self.mutex_file.read_text(encoding="utf-8"))
            data["active"] = False
            data["lastState"] = "QUOTA_STOP_HTTP_429"
            data["blockReason"] = self.block_reason
            data["releasedAt"] = datetime.now(timezone.utc).isoformat()
            self._atomic_write(self.mutex_file, json.dumps(data, indent=2).encode("utf-8"))
            self._drop_excl()
            self.has_lock = False
            return True
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
                    "batch_id": "vertex-repair-20261009",
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
                row["status"] = status
                row["retained"] = True
                self._save_reservations()
                return
        self.reservations.append({
            "attemptId": attempt_id,
            "reservedUSD": reserved,
            "status": status,
            "retained": True,
            "recordedAt": datetime.now(timezone.utc).isoformat(),
        })
        self._save_reservations()

    def preflight_unknown(self, pack_dirs: list[Path]):
        for pack_dir in pack_dirs:
            wa = pack_dir / "write_ahead_request.json"
            if not wa.exists():
                continue
            data = json.loads(wa.read_text(encoding="utf-8"))
            status = str(data.get("status", ""))
            if status in {"UNKNOWN", "UNKNOWN_CRASH_DURING_DISPATCH", "SENDING_POST"}:
                item = data.get("itemId", pack_dir.name)
                if item not in self.unresolved_items:
                    self.unresolved_items.append(item)
                raise UnknownLiabilityError(f"Unresolved {status} on {item}")

    def execute_prepared(self, pack_dir: Path, wire_bytes: bytes, item_meta: dict, reservation_usd: float) -> dict:
        """Send one prepared body, or reuse a verified success. Never retries inside this call."""
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
        if any(r["attemptId"] == attempt_id for r in self.reservations):
            raise BudgetError(f"Duplicate attempt id {attempt_id}")
        if self.exposure_usd() + float(reservation_usd) > self.hard_cap_usd + 1e-9:
            raise BudgetError(
                f"Reservation {reservation_usd} would put exposure {self.exposure_usd() + reservation_usd} over {self.hard_cap_usd}"
            )
        req_path = pack_dir / "request_body.json"
        sub_path = pack_dir / "write_ahead_subattempt_1.json"
        if sub_path.exists():
            raise BudgetError(f"Subattempt 1 already recorded for {item_id}; refusing duplicate")
        write_ahead = {
            "itemId": item_id,
            "attemptId": attempt_id,
            "ownerQueue": item_meta.get("owner", "ENVIRONMENT"),
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
        except UnknownLiabilityError as exc:
            self._mark_unknown(wa_path, write_ahead, f"AMBIGUOUS_TRANSPORT:{type(exc).__name__}")
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
            return err.read(), err.code, dict(err.headers)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise UnknownLiabilityError(f"Ambiguous transport failure: {type(exc).__name__}") from exc

    def _mark_unknown(self, wa_path: Path, write_ahead: dict, status: str):
        write_ahead["status"] = "UNKNOWN"
        write_ahead["unknownDetail"] = status
        write_ahead["recordedAt"] = datetime.now(timezone.utc).isoformat()
        self._atomic_write(wa_path, json.dumps(write_ahead, indent=2).encode("utf-8"))
        self._retain(write_ahead["attemptId"], write_ahead["reservationUSD"], "UNKNOWN")
        self.unresolved_items.append(write_ahead["itemId"])
        self.blocked = True
        self.block_reason = status

    def _finalize(self, pack_dir: Path, wa_path: Path, write_ahead: dict, resp_bytes: bytes, http_code: int, headers: dict, item_meta: dict):
        clean_headers = {
            str(k): str(v) for k, v in (headers or {}).items()
            if str(k).lower() not in {"authorization", "x-goog-api-key", "cookie", "set-cookie"}
        }
        if http_code == 429:
            retry_after = clean_headers.get("Retry-After") or clean_headers.get("retry-after")
            backoff = max(self.backoff_429, parse_retry_after(retry_after, now_fn=self.clock))
            self.next_eligible_retry_at = self.clock() + backoff
            self._save_pacing()
            write_ahead["status"] = "QUOTA_STOP_HTTP_429"
            write_ahead["backoffSeconds"] = backoff
            write_ahead["httpCode"] = 429
            write_ahead["headers"] = clean_headers
            self._atomic_write(wa_path, json.dumps(write_ahead, indent=2).encode("utf-8"))
            self._retain(write_ahead["attemptId"], write_ahead["reservationUSD"], "QUOTA_STOP_LIABILITY_RETAINED")
            self.blocked = True
            self.block_reason = "HTTP 429"
            raise QuotaStop(f"429 backoff {backoff}s; same body retained; no resend in this call")
        if http_code in {500, 502, 503, 504}:
            self._mark_unknown(wa_path, write_ahead, f"SERVER_ERROR_HTTP_{http_code}")
            (pack_dir / "response.http-error.bin").write_bytes(resp_bytes or b"")
            raise UnknownLiabilityError(f"HTTP {http_code} treated as UNKNOWN")
        if http_code in {401, 403}:
            write_ahead["status"] = f"ACCESS_DENIED_HTTP_{http_code}"
            write_ahead["httpCode"] = http_code
            write_ahead["error"] = (resp_bytes or b"")[:300].decode("utf-8", errors="replace")
            self._atomic_write(wa_path, json.dumps(write_ahead, indent=2).encode("utf-8"))
            self._retain(write_ahead["attemptId"], write_ahead["reservationUSD"], write_ahead["status"])
            self.blocked = True
            self.block_reason = write_ahead["status"]
            raise AuthError(write_ahead["status"])
        if http_code != 200:
            write_ahead["status"] = f"REJECTED_HTTP_{http_code}"
            write_ahead["httpCode"] = http_code
            write_ahead["error"] = (resp_bytes or b"")[:500].decode("utf-8", errors="replace")
            self._atomic_write(wa_path, json.dumps(write_ahead, indent=2).encode("utf-8"))
            self._atomic_write(pack_dir / "response.json", resp_bytes or b"{}")
            self._retain(write_ahead["attemptId"], write_ahead["reservationUSD"], "REJECTED_LIABILITY_RETAINED")
            return {"status": "REJECTED", "itemId": write_ahead["itemId"], "httpCode": http_code, "sent": True}
        resp_path = pack_dir / "response.json"
        self._atomic_write(resp_path, resp_bytes)
        write_ahead["status"] = "SUCCEEDED"
        write_ahead["responseSHA256"] = sha256_bytes(resp_bytes)
        write_ahead["httpCode"] = 200
        self.last_completed_at = self.clock()
        self.next_allowed_post_at = self.last_completed_at + self.success_gap
        self._save_pacing()
        self._atomic_write(wa_path, json.dumps(write_ahead, indent=2).encode("utf-8"))
        self._retain(write_ahead["attemptId"], write_ahead["reservationUSD"], "SUCCEEDED_LIABILITY_RETAINED_UNTIL_INVOICE")
        texts = _body_text_parts(json.loads(wire_text(pack_dir / "request_body.json")))
        inline = _body_inline_parts(json.loads(wire_text(pack_dir / "request_body.json")))
        if item_meta.get("prompt") and item_meta["prompt"] not in texts:
            return {"status": "FAILED_RESPONSE_IDENTITY", "itemId": write_ahead["itemId"], "sent": True}
        if item_meta.get("inlineCount") is not None and len(inline) != item_meta["inlineCount"]:
            return {"status": "FAILED_RESPONSE_IDENTITY", "itemId": write_ahead["itemId"], "sent": True}
        return {
            "status": "SUCCEEDED_CANDIDATE",
            "itemId": write_ahead["itemId"],
            "attemptId": write_ahead["attemptId"],
            "responseSHA256": write_ahead["responseSHA256"],
            "sent": True,
            "reservedUSD": write_ahead["reservationUSD"],
        }

    def resume_retained_body(self, pack_dir: Path, wire_bytes: bytes, item_meta: dict) -> dict:
        """POST one already-reserved body after a definite 429. Does not add a reservation."""
        if not self.has_lock:
            raise MutexError("Cannot resume without the owned mutex")
        if self.blocked or self.unresolved_items:
            raise UnknownLiabilityError(f"Paid dispatch blocked: {self.block_reason or self.unresolved_items}")
        attempt_id = item_meta["attemptId"]
        body_sha = sha256_bytes(wire_bytes)
        if body_sha != item_meta.get("wireBodySHA256"):
            raise BudgetError("Wire bytes do not match the prepared hash")
        pack_dir = Path(pack_dir)
        wa_path = pack_dir / "write_ahead_request.json"
        req_path = pack_dir / "request_body.json"
        if not wa_path.exists() or not req_path.exists():
            raise BudgetError(f"No retained body for {attempt_id}")
        prior = json.loads(wa_path.read_text(encoding="utf-8"))
        if prior.get("status") != "QUOTA_STOP_HTTP_429":
            raise BudgetError(f"Resume refused for status {prior.get('status')}")
        if prior.get("attemptId") != attempt_id or prior.get("bodySHA256") != body_sha:
            raise BudgetError("Retained attempt or body hash does not match")
        if req_path.read_bytes() != wire_bytes:
            raise BudgetError("Persisted body is not the retained body")
        retained = [row for row in self.reservations if row.get("attemptId") == attempt_id and row.get("retained")]
        if len(retained) != 1:
            raise BudgetError(f"Expected one retained reservation for {attempt_id}")
        write_ahead = dict(prior)
        write_ahead["status"] = "SENDING_POST"
        write_ahead["resumedAt"] = datetime.now(timezone.utc).isoformat()
        write_ahead["owner"] = self.owner_id
        self._atomic_write(wa_path, json.dumps(write_ahead, indent=2).encode("utf-8"))
        self._enforce_pacing()
        try:
            if self.transport:
                resp_bytes, http_code, headers = self.transport(ENDPOINT, wire_bytes)
            else:
                resp_bytes, http_code, headers = self._post(wire_bytes)
        except QuotaStop:
            raise
        except UnknownLiabilityError as exc:
            self._mark_unknown(wa_path, write_ahead, f"AMBIGUOUS_TRANSPORT:{type(exc).__name__}")
            raise
        except Exception as exc:
            self._mark_unknown(wa_path, write_ahead, f"DISPATCH_EXCEPTION:{type(exc).__name__}")
            raise UnknownLiabilityError(str(exc)) from exc
        if req_path.read_bytes() != wire_bytes:
            self._mark_unknown(wa_path, write_ahead, "BODY_MUTATED_AFTER_SEND")
            raise UnknownLiabilityError("Wire bytes changed after dispatch")
        return self._finalize(pack_dir, wa_path, write_ahead, resp_bytes, http_code, headers, item_meta)


def wire_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")
