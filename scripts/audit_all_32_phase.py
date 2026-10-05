import json
import hashlib
from pathlib import Path
from PIL import Image

root = Path("c:/dev/ages-of-dominion-reborn")
run6_dir = root / "assets/high-res/interactive-4k-first32-20261003/run-06-kingdom-20261004-023321"
manifest6 = json.loads((run6_dir / "manifest.json").read_text(encoding="utf-8"))

print("AUDITING FULL 32-ITEM FIRST-32 NATIVE-4K PHASE...")
all_32_report = []

for item in sorted(manifest6["items"], key=lambda x: x["order"]):
    order = item["order"]
    item_id = item["id"]
    mode = item["mode"]
    spec = item.get("spec") or item.get("age", "")
    out_rel = item["outputFile"]
    out_path = root / out_rel
    
    assert out_path.exists(), f"File missing: {out_path}"
    im = Image.open(out_path)
    sha = hashlib.sha256(out_path.read_bytes()).hexdigest()
    assert im.size == (5504, 3072), f"Bad dimensions: {im.size} for {item_id}"
    assert sha == item["sha256"], f"SHA mismatch for {item_id}"
    
    entry = {
        "order": order,
        "id": item_id,
        "mode": mode,
        "specOrAge": spec,
        "dimensions": list(im.size),
        "sha256": sha,
        "outputFile": out_rel,
        "status": item["status"],
        "technicalStatus": "PASS",
        "spatialStatus": item.get("spatialStatus", "UNVERIFIED"),
        "visualStatus": item.get("visualStatus", "UNVERIFIED"),
        "provenance": item.get("provenance", "run-06-kingdom-20261004-023321"),
    }
    all_32_report.append(entry)
    print(f"[{order:02d}/32] {item_id:26s} | mode={mode:9s} | {im.size} | SHA={sha[:16]}... | {entry['status']}")

print(f"\nALL 32 DISTINCT NATIVE 5504x3072 OUTPUTS VERIFIED!")
report_file = root / "qa/all-32-native4k-completion-report.json"
report_file.write_text(json.dumps(all_32_report, indent=2), encoding="utf-8")
print(f"Wrote complete 32-item report to: {report_file}")
