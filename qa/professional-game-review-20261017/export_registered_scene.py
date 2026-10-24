import hashlib
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "qa/professional-art-20261018/tactical-stone-ground-edit-v2"
SOURCE = PACK / "source-bound-registered-candidate.png"
OUTPUT = ROOT / "assets/derivatives/professional-20261018/scenes/tactical-stone.webp"
review = json.loads((PACK / "visual-review.json").read_text())
registration = json.loads((PACK / "source-bound-registration.json").read_text())
if review["status"] != "SOURCE_BOUND_CANDIDATE_BOUNDED_REVIEW" or registration["outputSHA256"] != hashlib.sha256(SOURCE.read_bytes()).hexdigest():
    raise RuntimeError("Candidate has no matching bounded source review")
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
image = Image.open(SOURCE)
image.save(OUTPUT, format="WEBP", quality=94, method=6)
report = {"source": str(SOURCE.relative_to(ROOT)), "sourceSHA256": registration["outputSHA256"], "output": str(OUTPUT.relative_to(ROOT)), "outputSHA256": hashlib.sha256(OUTPUT.read_bytes()).hexdigest(), "bytes": OUTPUT.stat().st_size, "dimensions": list(image.size), "sourceToRuntimeStage": [0.25, 0, 0, 0.25, 0, 0], "ownerAcceptance": "UNVERIFIED", "status": "BOUNDED_RUNTIME_CANDIDATE"}
(PACK / "runtime-export.json").write_text(json.dumps(report, indent=2))
print(json.dumps(report))
