"""Read-only Vertex readiness. Never submits generation or changes controls."""
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
sys.stdout.reconfigure(encoding="utf-8")
spec = importlib.util.spec_from_file_location("existing_vertex", ROOT / "scripts/vertex-production.py")
vertex = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vertex)
report = {"at": datetime.now(timezone.utc).isoformat(), "project": vertex.PROJECT,
          "account": vertex.ACCOUNT, "generationPOSTs": 0, "controlWrites": 0,
          "checks": {}, "status": "UNVERIFIED"}
try:
    vertex.auth()
    report["checks"]["tokenRefresh"] = "PASS"
    for key, operation in [("cloudLockMetadata", lambda: vertex.storage_meta(vertex.LOCK_OBJECT)),
                           ("cloudLock", lambda: json.loads(vertex.storage_get(vertex.LOCK_OBJECT))),
                           ("jobs", vertex.list_jobs)]:
        try:
            value = operation()
            if key == "cloudLockMetadata":
                value = {k: value.get(k) for k in ["generation", "updated", "size"]}
            report["checks"][key] = value
        except Exception as exc:
            report["checks"][key] = {"error": type(exc).__name__, "reason": str(exc)[:600]}
        (OUT / "provider-readiness.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    report["locations"] = vertex.SCAN
    checks = report["checks"]
    if isinstance(checks.get("jobs"), list) and "error" not in checks.get("cloudLock", {}):
        report["status"] = "READ_ONLY_METADATA_COLLECTED"
    else:
        report["status"] = "BLOCKED_READINESS"
except Exception as exc:
    # gcloud exception string contains the command, never stdout/token or credential data.
    report["checks"]["tokenRefresh"] = {"error": type(exc).__name__, "reason": str(exc)[:600]}
    report["status"] = "BLOCKED_AUTH_REFRESH"
finally:
    (OUT / "provider-readiness.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
