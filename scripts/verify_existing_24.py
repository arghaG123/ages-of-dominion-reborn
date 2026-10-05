import json
import hashlib
from pathlib import Path
from PIL import Image

root = Path("c:/dev/ages-of-dominion-reborn")
outputs_file = root / "qa/kingdom-image-progress-20261004/outputs.json"
data = json.loads(outputs_file.read_text(encoding="utf-8"))
print("Outputs count in qa audit:", len(data))

valid_count = 0
for item in data:
    p = root / item["file"]
    if not p.exists():
        print("MISSING:", item["file"])
        continue
    im = Image.open(p)
    sha = hashlib.sha256(p.read_bytes()).hexdigest()
    if im.size == (5504, 3072) and sha == item["sha256"]:
        valid_count += 1
    else:
        print("MISMATCH for", item["id"], "size:", im.size, "sha_match:", sha == item["sha256"])

print(f"Total verified 5504x3072 outputs: {valid_count} / {len(data)}")
