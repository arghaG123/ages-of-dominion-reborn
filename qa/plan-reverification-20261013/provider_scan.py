"""Complete paginated read-only job inventory; retries GET timeouts only."""
import concurrent.futures
import importlib.util
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("v", ROOT / "scripts/vertex-production.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
token = v.auth()  # Never stored or printed.
report = {"at": datetime.now(timezone.utc).isoformat(), "project": v.PROJECT,
          "account": v.ACCOUNT, "generationPOSTs": 0, "controlWrites": 0,
          "locations": [], "jobs": [], "errors": []}

def get(url):
    for attempt in range(2):
        try:
            request = urllib.request.Request(url, headers={"Authorization": "Bearer " + token})
            with urllib.request.urlopen(request, timeout=22) as response:
                return json.load(response)
        except (TimeoutError, urllib.error.URLError) as exc:
            if isinstance(exc, urllib.error.HTTPError) or attempt:
                raise

def pages(url, key):
    found, count = [], 0
    while True:
        data = get(url)
        found.extend(data.get(key, []))
        count += 1
        next_page = data.get("nextPageToken")
        if not next_page:
            return found, count
        url = re.sub(r"&pageToken=[^&]*", "", url) + "&pageToken=" + urllib.parse.quote(next_page, safe="")

def region_scan(region):
    prefix = region + "-" if region != "global" else ""
    url = f"https://{prefix}aiplatform.googleapis.com/v1/projects/{v.PROJECT}/locations/{region}/batchPredictionJobs?pageSize=100"
    try:
        jobs, page_count = pages(url, "batchPredictionJobs")
        return {"location": region, "status": "CHECKED", "pages": page_count,
                "jobs": [{"name": j["name"], "state": j.get("state", "UNKNOWN"),
                          "displayName": j.get("displayName")} for j in jobs]}
    except urllib.error.HTTPError as exc:
        return {"location": region, "status": "UNSUPPORTED_404" if exc.code == 404 else "ERROR", "http": exc.code}
    except Exception as exc:
        return {"location": region, "status": "ERROR", "error": type(exc).__name__}

def save():
    (OUT / "provider-inventory.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

try:
    locations, _ = pages(f"https://aiplatform.googleapis.com/v1/projects/{v.PROJECT}/locations?pageSize=100", "locations")
    regions = {"global", "us", "eu", "us-central1"} | {x["locationId"] for x in locations if re.fullmatch(r"[a-z]+(?:-[a-z]+)+[0-9]+", x["locationId"])}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for row in pool.map(region_scan, sorted(regions, key=lambda x: (x not in {"global", "us-central1"}, x))):
            report["locations"].append({k: value for k, value in row.items() if k != "jobs"})
            report["jobs"].extend(row.get("jobs", []))
            if row["status"] == "ERROR":
                report["errors"].append(row)
            save()
            print(json.dumps({k: value for k, value in row.items() if k != "jobs"}), flush=True)
    metadata = v.storage_meta(v.LOCK_OBJECT)
    report["cloudGeneration"] = metadata["generation"]
    report["cloudLock"] = json.loads(v.storage_get(v.LOCK_OBJECT))
    terminal = v.TERMINAL
    report["nonterminalJobs"] = [j for j in report["jobs"] if j["state"] not in terminal]
    report["status"] = "PASS_METADATA_ONLY" if not report["errors"] and not report["nonterminalJobs"] and report["cloudLock"].get("state") in terminal else "BLOCKED_READINESS"
except Exception as exc:
    report["errors"].append({"error": type(exc).__name__, "reason": str(exc)[:300]})
    report["status"] = "BLOCKED_READINESS"
finally:
    save()
    print(json.dumps({"status": report["status"], "locations": len(report["locations"]), "jobs": len(report["jobs"]), "errors": report["errors"]}), flush=True)
