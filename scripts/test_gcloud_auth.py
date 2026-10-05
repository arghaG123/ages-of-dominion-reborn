import subprocess
import urllib.request
import urllib.parse
import json
import time

project = "project-eaa4c1cc-8f19-4d24-9e6"
account = "arghawork3@gmail.com"
bucket = f"{project}-aod-batch"
lock_object = "design-mocks/active-batch.lock.json"

cmd = [
    "gcloud.cmd",
    "auth",
    "print-access-token",
    f"--account={account}",
    f"--project={project}",
]
res = subprocess.run(cmd, capture_output=True, text=True, check=True)
token = res.stdout.strip()
print("Token acquired successfully. Length:", len(token))

url = f"https://storage.googleapis.com/storage/v1/b/{bucket}/o/{urllib.parse.quote(lock_object, safe='')}?alt=media"
req = urllib.request.Request(url, headers={"Authorization": "Bearer " + token})
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode("utf-8"))
    print("Cloud lock content:")
    print(json.dumps(data, indent=2))

meta_url = f"https://storage.googleapis.com/storage/v1/b/{bucket}/o/{urllib.parse.quote(lock_object, safe='')}"
meta_req = urllib.request.Request(meta_url, headers={"Authorization": "Bearer " + token})
with urllib.request.urlopen(meta_req) as resp:
    meta = json.loads(resp.read().decode("utf-8"))
    print("Cloud lock generation:", meta.get("generation"))
