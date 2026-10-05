"""Interactive Continuity Runner with Measured Checks and Atomic Mutex.

Authoritative image runner architecture:
- Atomic exclusive local acquisition with unique run/process ownership (PID + UUID).
- Fail closed on malformed or unresolved lock ownership. Never force-clear another run.
- Conditional cloud shared lock with GCS CAS (ifGenerationMatch).
- Write-ahead persistence: exact wire body bytes and SHA-256 committed BEFORE any POST.
- Transport sends identical serialized bytes; logs never expose auth tokens.
- Enforces pacing: >= 20s gap after successful image request, durably persisted.
- Definite HTTP 429 backoff: >= 60s or longer Retry-After (numeric or HTTP-date). Retries SAME ID/body.
- No SDK/transport automatic inference retries, no hidden 401 resend.
- Ambiguous sent calls stay UNKNOWN with retained liability and lock denial.
- Rehashes and reuses known successes without repurchase.
- Role-specific pack verification (terrain geometry irrelevant for actors/portraits).
"""

from pathlib import Path
import json
import hashlib
import time
import os
import sys
import uuid
import email.utils
import base64
import urllib.request
import urllib.error
import urllib.parse
import subprocess
from datetime import datetime, timezone
from PIL import Image

ROOT = Path('C:\\dev\\ages-of-dominion-reborn\\qa\\both-ai-v3-independent-20261004\\controls-sandbox')
PLAN_PROD = ROOT / "docs/plan/image-production"
MUTEX_FILE = PLAN_PROD / "submission.mutex.json"
LOCAL_LOCK_FILE = PLAN_PROD / "active-batch.lock.json"
BUDGET_FILE = PLAN_PROD / "budget-ledger.json"
PACING_FILE = PLAN_PROD / "pacing_state.json"

PROJECT = "project-eaa4c1cc-8f19-4d24-9e6"
ACCOUNT = "arghawork3@gmail.com"
BUCKET = f"{PROJECT}-aod-batch"
LOCK_OBJECT = "design-mocks/active-batch.lock.json"
MODEL = "gemini-3.1-flash-image"
ENDPOINT = f"https://aiplatform.googleapis.com/v1/projects/{PROJECT}/locations/global/publishers/google/models/{MODEL}:generateContent"

DEFAULT_SUCCESS_PACING_SECONDS = 20.0
DEFAULT_429_BACKOFF_SECONDS = 60.0

# Official standard rates
INPUT_TOKEN_RATE_PER_1M = 0.50
TEXT_TOKEN_RATE_PER_1M = 3.00
IMAGE_TOKEN_RATE_PER_1M = 60.00
NATIVE_2K_IMAGE_TOKENS = 1680

class MutexError(Exception):
    pass

class AuthError(Exception):
    pass

class UnknownLiabilityError(Exception):
    pass

def is_pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    if sys.platform == "win32":
        import ctypes
        handle = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)
        if not handle:
            return False
        exit_code = ctypes.c_ulong()
        res = ctypes.windll.kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code))
        ctypes.windll.kernel32.CloseHandle(handle)
        return bool(res and exit_code.value == 259)
    else:
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def sha256_file(p: Path) -> str:
    return hashlib.file_digest(p.open("rb"), "sha256").hexdigest()

def parse_retry_after(header_val, now_fn=time.time) -> float:
    if not header_val:
        return 0.0
    val_str = str(header_val).strip()
    try:
        return float(val_str)
    except ValueError:
        pass
    try:
        dt = email.utils.parsedate_to_datetime(val_str)
        target_ts = dt.timestamp()
        return max(0.0, target_ts - now_fn())
    except Exception:
        return 0.0

def get_gcloud_token(account=ACCOUNT, project=PROJECT):
    cmd_name = "gcloud.cmd" if sys.platform == "win32" else "gcloud"
    cmd = [cmd_name, "auth", "print-access-token", f"--account={account}", f"--project={project}"]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return res.stdout.strip()
    except Exception as e:
        raise AuthError(f"Failed to obtain GCP access token: {e}")

class ContinuityRunner:
    def __init__(
        self,
        owner_id=None,
        owner_base="image-ai-continuity-runner",
        success_gap=DEFAULT_SUCCESS_PACING_SECONDS,
        backoff_429=DEFAULT_429_BACKOFF_SECONDS,
        mutex_file=MUTEX_FILE,
        pacing_file=PACING_FILE,
        budget_file=BUDGET_FILE,
        local_lock_file=LOCAL_LOCK_FILE,
        cloud_lock_enabled=False,
        cloud_lock_bucket=BUCKET,
        cloud_lock_object=LOCK_OBJECT,
        transport=None,
        clock=time.time,
        sleeper=time.sleep,
    ):
        self.pid = os.getpid()
        self.run_uuid = uuid.uuid4().hex[:8]
        if owner_id:
            self.owner_id = owner_id
        else:
            self.owner_id = f"{owner_base}-{self.run_uuid}-pid{self.pid}"

        self.success_gap = float(success_gap)
        self.backoff_429 = float(backoff_429)
        self.mutex_file = Path(mutex_file)
        self.pacing_file = Path(pacing_file)
        self.budget_file = Path(budget_file)
        self.local_lock_file = Path(local_lock_file)
        self.cloud_lock_enabled = cloud_lock_enabled
        self.cloud_lock_bucket = cloud_lock_bucket
        self.cloud_lock_object = cloud_lock_object
        self.cloud_lock_generation = None
        self.transport = transport
        self.clock = clock
        self.sleeper = sleeper

        self.has_lock = False
        self.unresolved_items = []
        self.has_retained_liabilities = False
        self.last_completed_at = 0.0
        self.next_allowed_post_at = 0.0
        self.next_eligible_retry_at = 0.0

        self.load_pacing()

    def load_pacing(self):
        """Loads persisted pacing and retry deadlines. Fails closed if malformed."""
        if self.pacing_file.exists():
            content = self.pacing_file.read_text(encoding="utf-8").strip()
            if not content:
                raise ValueError(f"Pacing file exists but is empty: {self.pacing_file}. Failing closed.")
            try:
                data = json.loads(content)
            except Exception as e:
                raise ValueError(f"Pacing file exists and is malformed JSON: {e}. Failing closed.")
            self.next_allowed_post_at = float(data.get("nextAllowedPOSTAtTs", 0.0))
            self.next_eligible_retry_at = float(data.get("nextEligibleRetryAtTs", 0.0))
            self.last_completed_at = float(data.get("lastCompletedAtTs", 0.0))

    def save_pacing(self):
        """Persists pacing state durably."""
        self.pacing_file.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "lastCompletedAtTs": self.last_completed_at,
            "lastCompletedAt": datetime.fromtimestamp(self.last_completed_at, tz=timezone.utc).isoformat() if self.last_completed_at > 0 else None,
            "nextAllowedPOSTAtTs": self.next_allowed_post_at,
            "nextAllowedPOSTAt": datetime.fromtimestamp(self.next_allowed_post_at, tz=timezone.utc).isoformat() if self.next_allowed_post_at > 0 else None,
            "nextEligibleRetryAtTs": self.next_eligible_retry_at,
            "nextEligibleRetryAt": datetime.fromtimestamp(self.next_eligible_retry_at, tz=timezone.utc).isoformat() if self.next_eligible_retry_at > 0 else None,
            "updatedAt": datetime.now(timezone.utc).isoformat(),
            "owner": self.owner_id,
        }
        temp = self.pacing_file.with_suffix(self.pacing_file.suffix + f".tmp.{self.pid}")
        temp.write_text(json.dumps(data, indent=2), encoding="utf-8")
        os.replace(temp, self.pacing_file)

    def acquire_mutex(self, force=False):
        """Acquires atomic mutex. Fails closed on malformed or active lock."""
        self.mutex_file.parent.mkdir(parents=True, exist_ok=True)

        if self.mutex_file.exists():
            content = self.mutex_file.read_text(encoding="utf-8").strip()
            if not content:
                raise MutexError("Mutex file exists but is empty/malformed")
            try:
                data = json.loads(content)
            except Exception as e:
                raise MutexError(f"Mutex file exists and is malformed JSON: {e}")

            if data.get("lastState") in ("UNKNOWN", "UNKNOWN_CRASH_DURING_DISPATCH") or "UNKNOWN" in str(data.get("lastState", "")):
                raise MutexError(f"Mutex held with unresolved UNKNOWN state by '{data.get('owner')}'. Manual/owner reconciliation required before acquiring.")

            if data.get("active") is True:
                existing_owner = data.get("owner")
                existing_pid = data.get("pid")
                raise MutexError(f"Mutex actively held by '{existing_owner}' (PID {existing_pid}). Failing closed.")

        # Pre-check: fail closed if exclusive token already exists
        excl_token = self.mutex_file.with_suffix(self.mutex_file.suffix + ".excl")
        if excl_token.exists():
            raise MutexError(f"Mutex acquisition collision: exclusive token {excl_token.name} is already held.")

        # Atomic OS-level mutual exclusion token registration FIRST
        try:
            fd = os.open(str(excl_token), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            token_payload = f"{self.owner_id}:{self.pid}:{self.run_uuid}".encode("utf-8")
            os.write(fd, token_payload)
            os.close(fd)
        except FileExistsError:
            # Another contender acquired first and holds the exclusive token!
            raise MutexError(f"Mutex acquisition collision: exclusive token {excl_token.name} already held by an active contender.")

        # Atomic file creation / update under exclusive token ownership
        lock_data = {
            "owner": self.owner_id,
            "pid": self.pid,
            "runUuid": self.run_uuid,
            "acquiredAt": datetime.now(timezone.utc).isoformat(),
            "active": True,
            "lastState": "ACQUIRED",
        }

        temp_mutex = self.mutex_file.with_suffix(self.mutex_file.suffix + f".{self.run_uuid}.tmp")
        temp_mutex.write_text(json.dumps(lock_data, indent=2), encoding="utf-8")
        os.replace(temp_mutex, self.mutex_file)

        # Verification of exclusive acquisition
        try:
            verified = json.loads(self.mutex_file.read_text(encoding="utf-8"))
            if verified.get("owner") != self.owner_id or verified.get("pid") != self.pid:
                try:
                    if excl_token.exists():
                        os.remove(excl_token)
                except Exception:
                    pass
                raise MutexError(f"Mutex acquisition collision: overwritten by contender '{verified.get('owner')}'")
        except MutexError:
            raise
        except Exception as e:
            try:
                if excl_token.exists():
                    os.remove(excl_token)
            except Exception:
                pass
            raise MutexError(f"Mutex verification failed after write: {e}")

        # Cloud CAS lock check if enabled
        if self.cloud_lock_enabled:
            token = get_gcloud_token()
            c_lock, gen = self._get_cloud_lock(token)
            if c_lock:
                c_state = str(c_lock.get("state", "")).upper()
                c_workflow = str(c_lock.get("workflow_state", "")).upper()
                ACTIVE_OR_UNKNOWN_CLOUD_STATES = {
                    "JOB_STATE_RUNNING", "JOB_STATE_PENDING", "JOB_STATE_QUEUED",
                    "ACTIVE_INDIVIDUAL_GENERATION", "JOB_STATE_UNKNOWN", "UNKNOWN",
                    "UNKNOWN_CRASH_DURING_DISPATCH", "SENDING_POST"
                }
                if c_state in ACTIVE_OR_UNKNOWN_CLOUD_STATES or c_workflow in ACTIVE_OR_UNKNOWN_CLOUD_STATES or not c_state:
                    cloud_pid = c_lock.get("pid")
                    cloud_owner = c_lock.get("owner")
                    try:
                        if excl_token.exists():
                            os.remove(excl_token)
                    except Exception:
                        pass
                    raise MutexError(f"Cloud lock is currently active/unknown ({c_state}/{c_workflow}) by owner '{cloud_owner}' (PID {cloud_pid}). Cannot reclaim active cloud lock.")
            # Update cloud lock to RUNNING
            c_data = {
                "batch_id": f"interactive-2k-later73-{datetime.now(timezone.utc).strftime('%Y%m%d')}",
                "model": MODEL,
                "project": PROJECT,
                "account": ACCOUNT,
                "state": "JOB_STATE_RUNNING",
                "workflow_state": "ACTIVE_INDIVIDUAL_GENERATION",
                "owner": self.owner_id,
                "pid": self.pid,
                "createdAt": datetime.now(timezone.utc).isoformat(),
            }
            new_gen = self._put_cloud_lock(c_data, gen, token)
            self.cloud_lock_generation = new_gen

        self.has_lock = True
        return True

    def release_mutex(self, state="RELEASED"):
        """Releases mutex ONLY if safe. Never releases if state is UNKNOWN or unresolved items exist."""
        if not self.has_lock:
            return False

        if self.unresolved_items or self.has_retained_liabilities or state == "UNKNOWN" or "UNKNOWN" in str(state):
            print(f"[WARN] Mutex NOT released: ambiguous outcome UNKNOWN or unresolved items ({self.unresolved_items}) must retain lock and liability.")
            if self.mutex_file.exists():
                try:
                    data = json.loads(self.mutex_file.read_text(encoding="utf-8"))
                    data["lastState"] = "UNKNOWN"
                    data["active"] = True  # Must stay active!
                    data["unresolvedItems"] = list(self.unresolved_items)
                    data["unknownAt"] = datetime.now(timezone.utc).isoformat()
                    temp = self.mutex_file.with_suffix(self.mutex_file.suffix + f".unk.{self.pid}.tmp")
                    temp.write_text(json.dumps(data, indent=2), encoding="utf-8")
                    os.replace(temp, self.mutex_file)
                except Exception:
                    pass
            # Exclusive token file stays locked!
            return False

        if self.mutex_file.exists():
            try:
                data = json.loads(self.mutex_file.read_text(encoding="utf-8"))
                if data.get("owner") != self.owner_id:
                    raise MutexError(f"Cannot release mutex owned by '{data.get('owner')}'; current runner is '{self.owner_id}'")
                data["active"] = False
                data["lastState"] = state
                data["releasedAt"] = datetime.now(timezone.utc).isoformat()
                temp = self.mutex_file.with_suffix(self.mutex_file.suffix + f".rel.{self.pid}.tmp")
                temp.write_text(json.dumps(data, indent=2), encoding="utf-8")
                os.replace(temp, self.mutex_file)
            except Exception as e:
                print(f"[ERROR] Failed to update mutex on release: {e}")
                return False

        excl_token = self.mutex_file.with_suffix(self.mutex_file.suffix + ".excl")
        if excl_token.exists():
            try:
                os.remove(excl_token)
            except Exception:
                pass

        if self.cloud_lock_enabled and self.cloud_lock_generation:
            try:
                token = get_gcloud_token()
                c_data = {
                    "batch_id": f"interactive-2k-later73-{datetime.now(timezone.utc).strftime('%Y%m%d')}",
                    "model": MODEL,
                    "project": PROJECT,
                    "account": ACCOUNT,
                    "state": "JOB_STATE_SUCCEEDED",
                    "workflow_state": "TERMINAL_COLLECTED",
                    "owner": self.owner_id,
                    "releasedAt": datetime.now(timezone.utc).isoformat(),
                    "lastState": state,
                }
                self._put_cloud_lock(c_data, self.cloud_lock_generation, token)
            except Exception as e:
                print(f"[WARN] Failed to release cloud lock: {e}")

        self.has_lock = False
        return True

    def _get_cloud_lock(self, token):
        meta_url = f"https://storage.googleapis.com/storage/v1/b/{self.cloud_lock_bucket}/o/{urllib.parse.quote(self.cloud_lock_object, safe='')}"
        meta_req = urllib.request.Request(meta_url, headers={"Authorization": "Bearer " + token})
        try:
            with urllib.request.urlopen(meta_req, timeout=30) as meta_resp:
                meta = json.loads(meta_resp.read().decode("utf-8"))
            gen = str(meta.get("generation"))
            media_url = f"{meta_url}?alt=media&ifGenerationMatch={gen}"
            media_req = urllib.request.Request(media_url, headers={"Authorization": "Bearer " + token})
            with urllib.request.urlopen(media_req, timeout=30) as media_resp:
                content = json.loads(media_resp.read().decode("utf-8"))
            return content, gen
        except urllib.error.HTTPError as he:
            if he.code == 404:
                return None, "0"
            raise

    def _put_cloud_lock(self, lock_data, match_generation, token):
        url = f"https://storage.googleapis.com/upload/storage/v1/b/{self.cloud_lock_bucket}/o?uploadType=media&name={urllib.parse.quote(self.cloud_lock_object, safe='')}&ifGenerationMatch={match_generation}"
        body = json.dumps(lock_data, indent=2).encode("utf-8")
        req = urllib.request.Request(url, data=body, method="POST", headers={
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json"
        })
        with urllib.request.urlopen(req, timeout=30) as resp:
            meta = json.loads(resp.read().decode("utf-8"))
            return str(meta.get("generation"))

    def check_role_pack(self, pack_dir: Path, item_meta: dict):
        """Role-specific pack checks (Hero, Mount, Rig, Rival, Army).
        Terrain geometry is irrelevant for actor portraits and is not checked.
        """
        item_id = item_meta.get("id", pack_dir.name)
        group = item_meta.get("group", "")
        prompt = item_meta.get("prompt", "")

        # Fallback to pack files if not directly in item_meta
        if not prompt and (pack_dir / "request_meta.json").exists():
            try:
                rm = json.loads((pack_dir / "request_meta.json").read_text(encoding="utf-8"))
                prompt = rm.get("prompt", "")
                if "layout" not in item_meta and "layout" in rm:
                    item_meta["layout"] = rm["layout"]
            except Exception:
                pass
        if not prompt and (pack_dir / "prompt.txt").exists():
            try:
                prompt = (pack_dir / "prompt.txt").read_text(encoding="utf-8").strip()
            except Exception:
                pass

        item_meta["prompt"] = prompt

        # 1. Prompt check: Reject generic templates
        if not prompt or len(prompt) < 40:
            return {"pass": False, "reason": f"Prompt missing or too short for {item_id}"}

        # 2. Canvas check
        layout = item_meta.get("layout", {})
        if not layout and (pack_dir / "layout_spec.json").exists():
            try:
                layout = json.loads((pack_dir / "layout_spec.json").read_text(encoding="utf-8"))
                item_meta["layout"] = layout
            except Exception:
                pass

        canvas = layout.get("canvas", [2048, 2048])
        if canvas != [2048, 2048]:
            return {"pass": False, "reason": f"Canvas {canvas} is not native 2K square [2048, 2048]"}

        # 3. Role-specific content checks
        if "HERO" in group or item_id == "knight-mounted-master":
            if item_id == "knight-mounted-master":
                if "horse" not in prompt.lower() and "mount" not in prompt.lower():
                    return {"pass": False, "reason": "knight-mounted-master prompt missing rider and horse composite"}
            else:
                if "portrait" not in prompt.lower() and "hero" not in prompt.lower():
                    return {"pass": False, "reason": "Hero painting missing character portrait specification"}

        elif "MOUNTS" in group or "RIGS" in group or "RIVALS" in group:
            if item_id.startswith("hero-mount-"):
                if "saddle" not in prompt.lower() and "rider" not in prompt.lower() and "attachment" not in prompt.lower():
                    return {"pass": False, "reason": "Mount master missing saddle/rider anchor specification"}
            elif item_id.startswith("rig-"):
                parts = layout.get("parts", [])
                if len(parts) < 4:
                    return {"pass": False, "reason": "Rig sheet missing explicit separated part list"}
            elif item_id.startswith("rival-"):
                if not any(name in prompt for name in ["Aldric", "Corvus", "Kane", "Morgana", "Theron", "Valeria"]):
                    return {"pass": False, "reason": "Rival portrait missing specific rival identity"}

        elif "ARMY" in group:
            if not any(kw in prompt.lower() for kw in ["melee", "ranged", "heavy", "unit", "soldier", "trooper", "archer", "crusher", "tank", "cannon"]):
                return {"pass": False, "reason": "Army master missing combat role specification"}

        # 4. Source candidate reference files
        sources = item_meta.get("sources", item_meta.get("sourceCandidates", []))
        for s in sources:
            src_file = s.get("file")
            if src_file:
                p = ROOT / src_file
                if not p.exists():
                    return {"pass": False, "reason": f"Source reference file missing: {src_file}"}

        return {"pass": True, "role": group, "itemId": item_id}

    def write_ahead_persisted_request(self, pack_dir: Path, item_id: str, payload: dict, reservation_usd: float, subattempt=1):
        """Persists exact request body, hashes, reservation BEFORE any POST.
        Ensures byte-level equality between written body and SHA256.
        """
        pack_dir.mkdir(parents=True, exist_ok=True)
        body_bytes = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")
        body_sha = hashlib.sha256(body_bytes).hexdigest()

        # Write exact wire bytes atomically
        req_body_file = pack_dir / "request_body.json"
        temp_body = req_body_file.with_suffix(req_body_file.suffix + f".tmp.{self.pid}")
        temp_body.write_bytes(body_bytes)
        os.replace(temp_body, req_body_file)

        now_iso = datetime.now(timezone.utc).isoformat()
        write_ahead = {
            "itemId": item_id,
            "bodySHA256": body_sha,
            "reservationUSD": reservation_usd,
            "subattempt": subattempt,
            "recordedAt": now_iso,
            "status": "SENDING_POST",
            "endpoint": ENDPOINT,
            "project": PROJECT,
            "model": MODEL,
            "owner": self.owner_id,
            "cloudGeneration": self.cloud_lock_generation,
        }
        wa_file = pack_dir / "write_ahead_request.json"
        temp_wa = wa_file.with_suffix(wa_file.suffix + f".tmp.{self.pid}")
        temp_wa.write_text(json.dumps(write_ahead, indent=2), encoding="utf-8")
        os.replace(temp_wa, wa_file)

        # Durable append-only subattempt record - preserve prior bytes on collision
        subattempt_file = pack_dir / f"write_ahead_subattempt_{subattempt}.json"
        if subattempt_file.exists():
            collision_file = pack_dir / f"write_ahead_subattempt_{subattempt}_collision_{self.run_uuid}_{uuid.uuid4().hex[:6]}.json"
            collision_file.write_text(json.dumps(write_ahead, indent=2), encoding="utf-8")
        else:
            subattempt_file.write_text(json.dumps(write_ahead, indent=2), encoding="utf-8")
        return body_bytes, body_sha

    def preflight_check(self, queue_packs):
        """Scans all queue pack directories for unresolved UNKNOWN or ambiguous states.
        Halts immediately before ANY dispatch if any unresolved UNKNOWN attempt exists.
        """
        for p in queue_packs:
            pack_dir = Path(p)
            wa_file = pack_dir / "write_ahead_request.json"
            if wa_file.exists():
                content = wa_file.read_text(encoding="utf-8").strip()
                if not content:
                    raise UnknownLiabilityError(f"Preflight error: empty write-ahead in {pack_dir}")
                try:
                    wa = json.loads(content)
                except Exception as e:
                    raise UnknownLiabilityError(f"Preflight error: malformed write-ahead in {pack_dir}: {e}")
                status = wa.get("status")
                if status in ("UNKNOWN", "UNKNOWN_CRASH_DURING_DISPATCH", "SENDING_POST"):
                    item_id = wa.get("itemId", pack_dir.name)
                    if item_id not in self.unresolved_items:
                        self.unresolved_items.append(item_id)
                    self.has_retained_liabilities = True
                    raise UnknownLiabilityError(
                        f"Run-wide preflight HALT: Item '{item_id}' in {pack_dir.name} has unresolved status "
                        f"'{status}'. Queue halted before ANY dispatch to avoid duplicate charges."
                    )

    def enforce_pacing(self):
        """Enforces 20s post-success pacing and 60s+ 429 retry backoff."""
        self.load_pacing()
        now = self.clock()
        wait_needed = 0.0

        if now < self.next_allowed_post_at:
            gap_wait = self.next_allowed_post_at - now
            if gap_wait > wait_needed:
                wait_needed = gap_wait

        if now < self.next_eligible_retry_at:
            retry_wait = self.next_eligible_retry_at - now
            if retry_wait > wait_needed:
                wait_needed = retry_wait

        if wait_needed > 0.0:
            print(f"  -> [PACING] Waiting {wait_needed:.2f}s before next POST...")
            self.sleeper(wait_needed)

    def execute_request(self, pack_dir: Path, item_meta: dict, reservation_usd=0.143612, max_retries=100, retry_unknown=False):
        """Executes a single image generation request.
        Handles:
        - Strict success reuse (never repurchase unbound outputs).
        - Write-ahead durability.
        - Pacing (20s gap) & 429 backoff (>=60s).
        - No hidden 401 retry.
        - NO_IMAGE consumed failure without auto-retry.
        - UNKNOWN state on ambiguous network failure.
        - Authorized retry of prior UNKNOWN items when retry_unknown=True.
        """
        item_id = item_meta["id"]
        output_png = pack_dir / "output.png"
        resp_json_file = pack_dir / "response.json"
        write_ahead_file = pack_dir / "write_ahead_request.json"

        # Check if unresolved UNKNOWN liabilities exist on the runner
        if self.unresolved_items or self.has_retained_liabilities:
            raise UnknownLiabilityError(f"Dispatch blocked: unfinalized UNKNOWN items exist ({self.unresolved_items}).")

        # 1. Check existing valid success for reuse with strict binding verification
        if write_ahead_file.exists():
            try:
                wa_content = write_ahead_file.read_text(encoding="utf-8").strip()
                if not wa_content:
                    raise UnknownLiabilityError("Write-ahead file is empty")
                wa = json.loads(wa_content)
                if wa.get("status") == "SUCCEEDED":
                    # Item ID binding
                    if wa.get("itemId") != item_id:
                        print(f"  -> [REUSE FAIL CLOSED] Item ID mismatch: requested '{item_id}' vs recorded '{wa.get('itemId')}'. Failing closed.")
                        return {
                            "status": "FAILED_REUSE_ITEM_ID_MISMATCH",
                            "itemId": item_id,
                            "error": f"Item ID mismatch: requested '{item_id}' vs recorded '{wa.get('itemId')}'",
                            "costUSD": 0.0
                        }

                    # Output file checks
                    if not output_png.exists():
                        print(f"  -> [REUSE FAIL CLOSED] output.png missing for item '{item_id}'. Failing closed.")
                        return {
                            "status": "FAILED_REUSE_OUTPUT_PNG_MISSING",
                            "itemId": item_id,
                            "error": "output.png missing",
                            "costUSD": 0.0
                        }
                    if not resp_json_file.exists():
                        print(f"  -> [REUSE FAIL CLOSED] response.json missing for item '{item_id}'. Failing closed.")
                        return {
                            "status": "FAILED_REUSE_RESPONSE_JSON_MISSING",
                            "itemId": item_id,
                            "error": "response.json missing",
                            "costUSD": 0.0
                        }

                    # Request body wire and hash binding
                    recorded_body_sha = wa.get("bodySHA256")
                    if not recorded_body_sha:
                        print(f"  -> [REUSE FAIL CLOSED] Missing bodySHA256 in write-ahead for item '{item_id}'. Failing closed.")
                        return {
                            "status": "FAILED_REUSE_MISSING_BODY_HASH",
                            "itemId": item_id,
                            "error": "Missing bodySHA256 in write-ahead record",
                            "costUSD": 0.0
                        }

                    req_body_file = pack_dir / "request_body.json"
                    if req_body_file.exists():
                        body_bytes = req_body_file.read_bytes()
                        actual_body_sha = hashlib.sha256(body_bytes).hexdigest()
                        if actual_body_sha != recorded_body_sha:
                            print(f"  -> [REUSE FAIL CLOSED] Request body SHA256 mismatch for item '{item_id}'. Failing closed.")
                            return {
                                "status": "FAILED_REUSE_BODY_HASH_MISMATCH",
                                "itemId": item_id,
                                "error": f"Body SHA256 mismatch: recorded {recorded_body_sha} vs wire {actual_body_sha}",
                                "costUSD": 0.0
                            }
                        req_prompt = item_meta.get("prompt")
                        if req_prompt:
                            try:
                                body_json = json.loads(body_bytes.decode("utf-8"))
                                contents = body_json.get("contents", [])
                                saved_prompt = None
                                if contents and "parts" in contents[0]:
                                    for part in contents[0]["parts"]:
                                        if "text" in part:
                                            saved_prompt = part["text"]
                                            break
                                if saved_prompt is not None and saved_prompt != req_prompt:
                                    print(f"  -> [REUSE FAIL CLOSED] Prompt mismatch for item '{item_id}'. Failing closed.")
                                    return {
                                        "status": "FAILED_REUSE_PROMPT_MISMATCH",
                                        "itemId": item_id,
                                        "error": f"Prompt mismatch: requested '{req_prompt}' vs saved '{saved_prompt}'",
                                        "costUSD": 0.0
                                    }
                            except Exception as e:
                                return {
                                    "status": "FAILED_REUSE_CORRUPT_REQUEST_BODY",
                                    "itemId": item_id,
                                    "error": str(e),
                                    "costUSD": 0.0
                                }

                    # Response wire bytes and content binding
                    resp_bytes = resp_json_file.read_bytes()
                    if not resp_bytes.strip() or resp_bytes.strip() == b"{}":
                        print(f"  -> [REUSE FAIL CLOSED] response.json empty for item '{item_id}'. Failing closed.")
                        return {
                            "status": "FAILED_REUSE_EMPTY_RESPONSE_JSON",
                            "itemId": item_id,
                            "error": "response.json is empty",
                            "costUSD": 0.0
                        }
                    if wa.get("responseSHA256"):
                        calc_resp_sha = hashlib.sha256(resp_bytes).hexdigest()
                        if calc_resp_sha != wa.get("responseSHA256"):
                            print(f"  -> [REUSE FAIL CLOSED] Response SHA256 mismatch for item '{item_id}'. Failing closed.")
                            return {
                                "status": "FAILED_REUSE_RESPONSE_HASH_MISMATCH",
                                "itemId": item_id,
                                "error": f"Response SHA256 mismatch: recorded {wa.get('responseSHA256')} vs actual {calc_resp_sha}",
                                "costUSD": 0.0
                            }

                    try:
                        resp_json = json.loads(resp_bytes.decode("utf-8"))
                    except Exception as e:
                        return {
                            "status": "FAILED_REUSE_CORRUPT_RESPONSE_JSON",
                            "itemId": item_id,
                            "error": str(e),
                            "costUSD": 0.0
                        }

                    candidates = resp_json.get("candidates", [])
                    if not candidates:
                        return {
                            "status": "FAILED_REUSE_NO_CANDIDATES",
                            "itemId": item_id,
                            "error": "No candidates in response",
                            "costUSD": 0.0
                        }
                    parts = candidates[0].get("content", {}).get("parts", [])
                    inline_parts = [p for p in parts if "inlineData" in p]
                    if not inline_parts:
                        return {
                            "status": "FAILED_REUSE_NO_INLINE_DATA",
                            "itemId": item_id,
                            "error": "No inlineData in response",
                            "costUSD": 0.0
                        }

                    inline_data = inline_parts[0]["inlineData"]
                    mime_type = inline_data.get("mimeType", "")
                    if mime_type != "image/png":
                        print(f"  -> [REUSE FAIL CLOSED] Unsupported MIME '{mime_type}' for item '{item_id}'. Failing closed.")
                        return {
                            "status": "FAILED_REUSE_UNSUPPORTED_MIME",
                            "itemId": item_id,
                            "error": f"Invalid MIME '{mime_type}', expected 'image/png'",
                            "costUSD": 0.0
                        }

                    try:
                        raw_bytes = base64.b64decode(inline_data["data"])
                    except Exception as e:
                        return {
                            "status": "FAILED_REUSE_INVALID_BASE64",
                            "itemId": item_id,
                            "error": str(e),
                            "costUSD": 0.0
                        }

                    # Image bytes and SHA256 checks
                    img_bytes = output_png.read_bytes()
                    img_sha = hashlib.sha256(img_bytes).hexdigest()
                    if hashlib.sha256(raw_bytes).hexdigest() != img_sha:
                        print(f"  -> [REUSE FAIL CLOSED] Decoded base64 hash does not match output.png for item '{item_id}'. Failing closed.")
                        return {
                            "status": "FAILED_REUSE_IMAGE_SHA_MISMATCH",
                            "itemId": item_id,
                            "error": "Decoded inlineData SHA256 does not match output.png SHA256",
                            "costUSD": 0.0
                        }
                    if wa.get("sha256") and wa.get("sha256") != img_sha:
                        print(f"  -> [REUSE FAIL CLOSED] Write-ahead SHA256 does not match output.png for item '{item_id}'. Failing closed.")
                        return {
                            "status": "FAILED_REUSE_WA_SHA_MISMATCH",
                            "itemId": item_id,
                            "error": f"Recorded SHA256 {wa.get('sha256')} does not match output.png SHA256 {img_sha}",
                            "costUSD": 0.0
                        }

                    # Full image decode and dimensions check
                    try:
                        img = Image.open(output_png)
                        img.load()
                        if img.format != "PNG":
                            return {
                                "status": "FAILED_REUSE_INVALID_FORMAT",
                                "itemId": item_id,
                                "error": f"Image format is '{img.format}', expected PNG",
                                "costUSD": 0.0
                            }
                        expected_dims = item_meta.get("expectedDimensions")
                        if expected_dims and list(img.size) != expected_dims:
                            return {
                                "status": "FAILED_REUSE_DIMENSION_MISMATCH",
                                "itemId": item_id,
                                "error": f"Image dimensions {list(img.size)} do not match expected {expected_dims}",
                                "costUSD": 0.0
                            }
                    except Exception as e:
                        return {
                            "status": "FAILED_REUSE_DECODE_ERROR",
                            "itemId": item_id,
                            "error": str(e),
                            "costUSD": 0.0
                        }

                    print(f"  -> [REUSE] Item '{item_id}' validated and verified (SHA: {img_sha[:16]}...). Reusing existing output.")
                    return {
                        "status": "REUSED_EXISTING_SUCCESS",
                        "itemId": item_id,
                        "dimensions": list(img.size),
                        "sha256": img_sha,
                        "costUSD": 0.0,
                    }
            except UnknownLiabilityError:
                raise
            except Exception as e:
                print(f"  -> [REUSE EXCEPTION FAIL CLOSED] Exception checking reuse for '{item_id}': {e}")
                return {
                    "status": "FAILED_REUSE_EXCEPTION",
                    "itemId": item_id,
                    "error": str(e),
                    "costUSD": 0.0
                }

        # 2. Check unfinalized crash state
        if write_ahead_file.exists():
            try:
                content = write_ahead_file.read_text(encoding="utf-8").strip()
                if not content:
                    raise UnknownLiabilityError("Write-ahead file is empty. Failing closed.")
                wa = json.loads(content)
                if wa.get("status") in ("UNKNOWN", "UNKNOWN_CRASH_DURING_DISPATCH"):
                    if not retry_unknown:
                        print(f"  -> [UNKNOWN RETAINED] Item '{item_id}' has recorded UNKNOWN status from {wa.get('owner')}. Retaining liability and halting queue.")
                        self.unresolved_items.append(item_id)
                        self.has_retained_liabilities = True
                        return {
                            "status": "UNKNOWN_RETAINED_LIABILITY",
                            "itemId": item_id,
                            "costUSD": wa.get("liabilityUSD", wa.get("reservationUSD", 0.143612)),
                            "unresolved": True
                        }
                    else:
                        print(f"  -> [AUTHORIZED RETRY] Owner authorized execution of UNKNOWN item '{item_id}'. Archiving unfinalized state...")
                        archive_wa = pack_dir / f"write_ahead_request.unresolved_archive_{int(time.time())}.json"
                        archive_wa.write_text(json.dumps(wa, indent=2), encoding="utf-8")
                elif wa.get("status") == "SENDING_POST" and wa.get("owner") != self.owner_id:
                    if not retry_unknown:
                        self.unresolved_items.append(item_id)
                        self.has_retained_liabilities = True
                        raise UnknownLiabilityError(
                            f"Item '{item_id}' has unfinalized SENDING_POST from previous run {wa.get('owner')}. "
                            "State is UNKNOWN; retaining liability and halting duplicate call."
                        )
                    else:
                        print(f"  -> [AUTHORIZED RETRY] Owner authorized execution of unfinalized SENDING_POST item '{item_id}'. Archiving unfinalized state...")
                        archive_wa = pack_dir / f"write_ahead_request.unresolved_archive_{int(time.time())}.json"
                        archive_wa.write_text(json.dumps(wa, indent=2), encoding="utf-8")
            except UnknownLiabilityError:
                raise
            except Exception:
                pass

        # 3. Construct Vertex payload
        prompt_text = item_meta.get("prompt", "")
        if not prompt_text:
            return {"status": "FAILED_MISSING_PROMPT", "itemId": item_id, "error": "Prompt missing or invalid"}
        parts = [{"text": prompt_text}]

        # Attach reference image if available
        sources = item_meta.get("sources", item_meta.get("sourceCandidates", []))
        for s in sources:
            src_file = s.get("file")
            if src_file:
                src_path = ROOT / src_file
                if src_path.exists():
                    ref_bytes = src_path.read_bytes()
                    ref_b64 = base64.b64encode(ref_bytes).decode("utf-8")
                    mime = "image/png" if src_path.suffix.lower() == ".png" else "image/jpeg"
                    parts.append({
                        "inlineData": {
                            "mimeType": mime,
                            "data": ref_b64
                        }
                    })
                    break  # Compact: 1 primary reference image (1120 tokens)

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": parts,
                }
            ],
            "generationConfig": {
                "candidateCount": 1,
                "maxOutputTokens": 2048,
                "responseModalities": ["IMAGE"],
                "imageConfig": {
                    "aspectRatio": "1:1",
                    "imageSize": "2K",
                },
            },
        }

        subattempt = 0
        while subattempt < max_retries:
            subattempt += 1

            # Durably commit write-ahead BEFORE post
            body_bytes, body_sha = self.write_ahead_persisted_request(
                pack_dir=pack_dir,
                item_id=item_id,
                payload=payload,
                reservation_usd=reservation_usd,
                subattempt=subattempt
            )

            # Enforce pacing gap
            self.enforce_pacing()

            post_start = self.clock()
            print(f"  -> Dispatching POST for '{item_id}' (Subattempt {subattempt})...")

            # Execute transport
            try:
                if self.transport:
                    resp_bytes, http_code, headers = self.transport(ENDPOINT, body_bytes)
                else:
                    token = get_gcloud_token()
                    headers = {
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json",
                    }
                    req = urllib.request.Request(ENDPOINT, data=body_bytes, method="POST", headers=headers)
                    with urllib.request.urlopen(req, timeout=180) as resp:
                        resp_bytes = resp.read()
                        http_code = resp.status
                        headers = dict(resp.headers)

            except urllib.error.HTTPError as err:
                http_code = err.code
                headers = dict(err.headers)
                resp_bytes = err.read()

                if http_code == 401:
                    # Halt immediately! No hidden inference resend.
                    wa_data = {
                        "itemId": item_id,
                        "status": "HALTED_HTTP_401",
                        "error": "Authentication expired. Halt for credential repair.",
                        "subattempt": subattempt,
                        "recordedAt": datetime.now(timezone.utc).isoformat(),
                    }
                    temp_wa = write_ahead_file.with_suffix(write_ahead_file.suffix + f".tmp.{self.pid}")
                    temp_wa.write_text(json.dumps(wa_data, indent=2), encoding="utf-8")
                    os.replace(temp_wa, write_ahead_file)
                    sub_f = pack_dir / f"write_ahead_subattempt_{subattempt}_401.json"
                    sub_f.write_text(json.dumps(wa_data, indent=2), encoding="utf-8")
                    raise AuthError("HTTP 401 Unauthorized received. Halt for credential repair with no hidden resend.")

                elif http_code == 429:
                    retry_after_hdr = headers.get("Retry-After") or headers.get("retry-after")
                    retry_sec = parse_retry_after(retry_after_hdr, now_fn=self.clock)
                    backoff = max(self.backoff_429, retry_sec)
                    self.next_eligible_retry_at = self.clock() + backoff
                    self.save_pacing()

                    clean_headers = {str(k): str(v) for k, v in headers.items() if str(k).lower() not in ("authorization", "x-goog-api-key", "token", "cookie", "set-cookie")}
                    wa_data = {
                        "itemId": item_id,
                        "bodySHA256": body_sha,
                        "subattempt": subattempt,
                        "status": "QUOTA_STOP_HTTP_429",
                        "httpCode": 429,
                        "backoffSeconds": backoff,
                        "nextEligibleRetryAt": datetime.fromtimestamp(self.next_eligible_retry_at, tz=timezone.utc).isoformat(),
                        "retryAfterHeader": retry_after_hdr,
                        "headers": clean_headers,
                        "recordedAt": datetime.now(timezone.utc).isoformat(),
                    }
                    temp_wa = write_ahead_file.with_suffix(write_ahead_file.suffix + f".tmp.{self.pid}")
                    temp_wa.write_text(json.dumps(wa_data, indent=2), encoding="utf-8")
                    os.replace(temp_wa, write_ahead_file)
                    sub_f = pack_dir / f"write_ahead_subattempt_{subattempt}_429.json"
                    sub_f.write_text(json.dumps(wa_data, indent=2), encoding="utf-8")
                    print(f"  -> [HTTP 429] Rate limit hit. Backoff {backoff:.1f}s scheduled. Waiting...")
                    continue  # Loop retries SAME request after backoff

                else:
                    # Other HTTP error (e.g. 400, 403, 500)
                    err_text = resp_bytes.decode("utf-8", errors="replace")
                    status_label = f"HTTP_ERROR_{http_code}"
                    if http_code == 403:
                        status_label = "ACCESS_DENIED_HTTP_403"
                    elif http_code in (500, 502, 503, 504):
                        status_label = f"SERVER_ERROR_HTTP_{http_code}"
                    wa_data = {
                        "itemId": item_id,
                        "bodySHA256": body_sha,
                        "subattempt": subattempt,
                        "status": status_label,
                        "httpCode": http_code,
                        "error": err_text[:500],
                        "recordedAt": datetime.now(timezone.utc).isoformat(),
                    }
                    temp_wa = write_ahead_file.with_suffix(write_ahead_file.suffix + f".tmp.{self.pid}")
                    temp_wa.write_text(json.dumps(wa_data, indent=2), encoding="utf-8")
                    os.replace(temp_wa, write_ahead_file)
                    sub_f = pack_dir / f"write_ahead_subattempt_{subattempt}_error_{http_code}.json"
                    sub_f.write_text(json.dumps(wa_data, indent=2), encoding="utf-8")
                    return {
                        "status": status_label,
                        "itemId": item_id,
                        "error": err_text,
                    }

            except Exception as e:
                # Connection dropped, timeout, etc. -> UNKNOWN!
                print(f"  -> [UNKNOWN] Network / transport error during dispatch: {e}")
                self.unresolved_items.append(item_id)
                self.has_retained_liabilities = True
                wa_data = {
                    "itemId": item_id,
                    "bodySHA256": body_sha,
                    "subattempt": subattempt,
                    "status": "UNKNOWN",
                    "error": str(e),
                    "retainLiability": True,
                    "liabilityUSD": reservation_usd,
                    "recordedAt": datetime.now(timezone.utc).isoformat(),
                }
                temp_wa = write_ahead_file.with_suffix(write_ahead_file.suffix + f".tmp.{self.pid}")
                temp_wa.write_text(json.dumps(wa_data, indent=2), encoding="utf-8")
                os.replace(temp_wa, write_ahead_file)
                sub_f = pack_dir / f"write_ahead_subattempt_{subattempt}_unknown.json"
                sub_f.write_text(json.dumps(wa_data, indent=2), encoding="utf-8")
                raise UnknownLiabilityError(f"Ambiguous outcome UNKNOWN for {item_id}: {e}")

            # Process HTTP 200 response
            resp_json_file.write_bytes(resp_bytes)
            try:
                resp_json = json.loads(resp_bytes.decode("utf-8"))
            except Exception as e:
                raise UnknownLiabilityError(f"Malformed response JSON from provider: {e}")

            candidates = resp_json.get("candidates", [])
            candidate = candidates[0] if candidates else {}
            finish_reason = candidate.get("finishReason", "")
            parts_out = candidate.get("content", {}).get("parts", [])

            image_data = None
            out_text = ""
            for p in parts_out:
                if "inlineData" in p:
                    image_data = base64.b64decode(p["inlineData"]["data"])
                if "text" in p:
                    out_text += p["text"]

            usage = resp_json.get("usageMetadata", {})
            prompt_tokens = usage.get("promptTokenCount", 0)
            candidate_tokens = usage.get("candidatesTokenCount", 0)

            # Check NO_IMAGE
            if not image_data or finish_reason == "NO_IMAGE":
                # Consumed attempt, text tariff applied, no auto-retry
                cost = (prompt_tokens * INPUT_TOKEN_RATE_PER_1M / 1e6) + (candidate_tokens * TEXT_TOKEN_RATE_PER_1M / 1e6)
                wa_data = {
                    "itemId": item_id,
                    "bodySHA256": body_sha,
                    "subattempt": subattempt,
                    "status": "CONSUMED_FAILED_NO_IMAGE",
                    "finishReason": finish_reason,
                    "promptTokens": prompt_tokens,
                    "candidateTokens": candidate_tokens,
                    "costUSD": round(cost, 6),
                    "outputText": out_text[:500],
                    "recordedAt": datetime.now(timezone.utc).isoformat(),
                }
                temp_wa = write_ahead_file.with_suffix(write_ahead_file.suffix + f".tmp.{self.pid}")
                temp_wa.write_text(json.dumps(wa_data, indent=2), encoding="utf-8")
                os.replace(temp_wa, write_ahead_file)
                sub_f = pack_dir / f"write_ahead_subattempt_{subattempt}_no_image.json"
                sub_f.write_text(json.dumps(wa_data, indent=2), encoding="utf-8")
                self.last_completed_at = self.clock()
                self.next_allowed_post_at = self.last_completed_at + self.success_gap
                self.save_pacing()
                print(f"  -> [CONSUMED NO_IMAGE] Item '{item_id}' returned NO_IMAGE. Cost: ${cost:.6f}. Advancing to next ready item.")
                return {
                    "status": "CONSUMED_FAILED_NO_IMAGE",
                    "itemId": item_id,
                    "finishReason": finish_reason,
                    "costUSD": round(cost, 6),
                    "tokens": {"prompt": prompt_tokens, "candidate": candidate_tokens},
                }

            # Succeeded image
            output_png.write_bytes(image_data)
            out_img = Image.open(output_png)
            out_sha = sha256_bytes(image_data)

            # Billable rate: candidate tokens are images @ $60/M
            cost = (prompt_tokens * INPUT_TOKEN_RATE_PER_1M / 1e6) + (candidate_tokens * IMAGE_TOKEN_RATE_PER_1M / 1e6)

            wa_data = {
                "itemId": item_id,
                "bodySHA256": body_sha,
                "subattempt": subattempt,
                "status": "SUCCEEDED",
                "completedAt": datetime.now(timezone.utc).isoformat(),
                "dimensions": list(out_img.size),
                "sha256": out_sha,
                "promptTokens": prompt_tokens,
                "candidateTokens": candidate_tokens,
                "actualCostUSD": round(cost, 6),
                "outputFile": str(output_png.relative_to(ROOT)).replace("\\", "/"),
            }
            temp_wa = write_ahead_file.with_suffix(write_ahead_file.suffix + f".tmp.{self.pid}")
            temp_wa.write_text(json.dumps(wa_data, indent=2), encoding="utf-8")
            os.replace(temp_wa, write_ahead_file)
            sub_f = pack_dir / f"write_ahead_subattempt_{subattempt}_success.json"
            sub_f.write_text(json.dumps(wa_data, indent=2), encoding="utf-8")

            self.last_completed_at = self.clock()
            self.next_allowed_post_at = self.last_completed_at + self.success_gap
            self.save_pacing()

            print(f"  -> [SUCCESS] Item '{item_id}' generated! Dimensions: {out_img.size}, SHA: {out_sha[:16]}..., Cost: ${cost:.4f} USD")
            return {
                "status": "SUCCEEDED",
                "itemId": item_id,
                "dimensions": list(out_img.size),
                "sha256": out_sha,
                "promptTokens": prompt_tokens,
                "candidateTokens": candidate_tokens,
                "costUSD": round(cost, 6),
                "outputFile": str(output_png.relative_to(ROOT)).replace("\\", "/"),
            }

        return {"status": "EXHAUSTED_RETRIES", "itemId": item_id}

    # Backward compatibility mock helper for test compatibility
    def execute_mock_request(self, item_id, mock_behavior="SUCCEED", retry_count=0):
        now = self.clock()
        if now < self.next_allowed_post_at:
            wait_needed = self.next_allowed_post_at - now
            self.sleeper(wait_needed)

        if mock_behavior == "SUCCEED":
            self.last_completed_at = self.clock()
            self.next_allowed_post_at = self.last_completed_at + self.success_gap
            self.save_pacing()
            return {
                "status": "SUCCEEDED",
                "completedAt": datetime.now(timezone.utc).isoformat(),
                "nextAllowedPOSTAt": datetime.fromtimestamp(self.next_allowed_post_at, tz=timezone.utc).isoformat(),
                "costUSD": 0.1524,
                "tokens": {"input": 2435, "output": 2520}
            }
        elif mock_behavior == "429_RETRY_ONCE":
            if retry_count == 0:
                self.next_eligible_retry_at = self.clock() + self.backoff_429
                self.save_pacing()
                return {
                    "status": "QUOTA_STOP_HTTP_429",
                    "httpCode": 429,
                    "backoffSeconds": self.backoff_429,
                    "nextEligibleRetryAt": datetime.fromtimestamp(self.next_eligible_retry_at, tz=timezone.utc).isoformat(),
                    "retryable": True
                }
            else:
                self.last_completed_at = self.clock()
                self.next_allowed_post_at = self.last_completed_at + self.success_gap
                self.save_pacing()
                return {
                    "status": "SUCCEEDED",
                    "completedAt": datetime.now(timezone.utc).isoformat(),
                    "costUSD": 0.1524,
                    "tokens": {"input": 2435, "output": 2520}
                }
        elif mock_behavior == "NO_IMAGE":
            text_cost = (2484 * 0.50 / 1e6) + (87 * 3.00 / 1e6)
            return {
                "status": "CONSUMED_FAILED_NO_IMAGE",
                "finishReason": "NO_IMAGE",
                "autoRetry": False,
                "costUSD": text_cost,
                "tokens": {"input": 2484, "output": 87},
                "tariffApplied": "TEXT_TARIFF"
            }
        elif mock_behavior == "UNKNOWN_TIMEOUT":
            return {
                "status": "UNKNOWN",
                "reason": "Connection dropped after POST sent; outcome ambiguous",
                "retainLiability": True,
                "releaseMutex": False
            }
        return {"status": "FAILED"}
