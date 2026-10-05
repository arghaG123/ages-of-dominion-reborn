import json
import hashlib
from pathlib import Path
from PIL import Image

root = Path("c:/dev/ages-of-dominion-reborn")
run_dir = root / "assets/high-res/interactive-4k-first32-20261003/run-06-kingdom-20261004-023321"
journal = json.loads((run_dir / "journal.json").read_text(encoding="utf-8"))
manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))

print("Auditing Run 06 Kingdom outputs...")
results = []
for item in manifest["items"]:
    if item["mode"] == "kingdom":
        out_rel = item["outputFile"]
        out_path = root / out_rel
        assert out_path.exists(), f"Missing output: {out_path}"
        im = Image.open(out_path)
        sha = hashlib.sha256(out_path.read_bytes()).hexdigest()
        assert im.size == (5504, 3072), f"Bad size: {im.size}"
        assert sha == item["sha256"], f"SHA mismatch: {sha} vs {item['sha256']}"
        
        # Check viewports
        pack_dir = out_path.parent
        vp_dir = pack_dir / "viewports"
        vp_files = list(vp_dir.glob("*.png"))
        comp_file = pack_dir / "comparison.png"
        assert comp_file.exists(), f"Missing comparison: {comp_file}"
        assert len(vp_files) == 4, f"Missing viewports: {len(vp_files)}"

        results.append({
            "order": item["order"],
            "id": item["id"],
            "age": item.get("age", ""),
            "dimensions": list(im.size),
            "sha256": sha,
            "costUSD": item.get("costUSD"),
            "viewportsCount": len(vp_files),
            "comparisonExists": comp_file.exists(),
        })
        print(f"[{item['order']:02d}/32] PASS {item['id']} ({item.get('age')}) -> {im.size}, SHA={sha[:16]}...")

print(f"\nAll {len(results)} Kingdom outputs verified with PASS!")
out_report = root / "qa/kingdom-run6-verification.json"
out_report.write_text(json.dumps(results, indent=2), encoding="utf-8")
print("Saved verification report to:", out_report)
