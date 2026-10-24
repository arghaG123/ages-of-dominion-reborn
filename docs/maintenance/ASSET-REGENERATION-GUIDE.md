# Asset regeneration guide

Updated 24 October 2026. This guide and `ASSET-GENERATION-RECIPES-20261024.json` replace only duplicated embedded-image request payloads. They do not replace the original artwork or evidence of actual generation. Current game acceptance remains INCOMPLETE.

## What to keep

Keep original production/high-resolution/reference/mask images, all unique image versions, small prompt/layout/request metadata, generation receipts, write-ahead hashes, ledgers and unknown-call/budget records. These distinguish a prepared request from a completed paid request. Do not infer success or new spending authority from old READY/paidCallsAllowed fields.

The 73 archived request bodies previously repeated reference-image bytes as base64. The compact recipe bundle retains every prompt, content-part order, generation setting, recorded model, original request path/hash/byte count, and exact UTF-8 request template. Each image placeholder identifies an existing reference file by path and SHA256. All 73 templates reconstructed to their exact original request bytes before deletion. No new image files or backup image trees were created.

## Find the right recipe

- `ASSET-GENERATION-RECIPES-20261024.json`: 73 exact archived requests under `assets/high-res/later73-preparation-packs/<id>/`. Each entry contains human-readable prompts and generationConfig, plus reconstruction data.
- The corresponding asset directory still contains `prompt.txt`, `layout_spec.json`, `request_meta.json`, any generated `output.png`, and `write_ahead_request.json` when present. The request metadata records original source candidates, hashes, intended model, dimensions and consumer purpose.
- Earlier production batches: retain `assets/production/production-*/input.jsonl`, `ledger.json`, collection reports and review indices. These contain the earlier prompts, request settings and generation outcomes.
- Other generation history: `docs/maintenance/footprint-20261024/generation-history-index.json` is an older finding aid. Payload paths removed by this compaction now map to this compact bundle; historical hashes remain valid for reconstruction.
- Existing processing code lives in `scripts/`. Identify the script associated with the asset's metadata/history rather than running every historical runner. Reuse its crop, matte, rig, layout and registration rules where applicable.

## Restore one request offline

Historical runners that expect `request_body.json` need that exact file restored before reuse. The compact recipe itself is NOT a provider request. Restore only the needed ID to avoid reintroducing all 123 MB of duplicate payloads. The following standard-library Python code performs no network request, generation, budget update or game change:

```python
from pathlib import Path
import base64, hashlib, json

root = Path(r"C:/dev/ages-of-dominion-reborn").resolve()
requested_id = "portrait-ancient-warlock"  # Change to the required recipe ID.
bundle = json.loads((root / "docs/maintenance/ASSET-GENERATION-RECIPES-20261024.json").read_text(encoding="utf-8"))
records = [row for row in bundle["requests"] if row["id"] == requested_id]
if len(records) != 1:
    raise RuntimeError("Expected exactly one recipe")
row = records[0]
text = row["templateUtf8"]
for ref in row["references"]:
    source = (root / ref["file"]).resolve()
    if not source.is_relative_to(root / "assets"):
        raise RuntimeError("Reference escapes assets")
    blob = source.read_bytes()
    if len(blob) != ref["bytes"] or hashlib.sha256(blob).hexdigest() != ref["sha256"]:
        raise RuntimeError("Reference has changed; recover the recorded version first")
    text = text.replace(json.dumps(ref["token"]), json.dumps(base64.b64encode(blob).decode("ascii")))
raw = text.encode("utf-8")
if len(raw) != row["originalBytes"] or hashlib.sha256(raw).hexdigest() != row["originalSha256"]:
    raise RuntimeError("Restored request does not match original")
target = (root / row["originalPath"]).resolve()
if not target.is_relative_to(root / "assets/high-res/later73-preparation-packs"):
    raise RuntimeError("Output escapes the archived request namespace")
if target.exists():
    if target.read_bytes() != raw:
        raise RuntimeError("Refuse to overwrite a different current request")
else:
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("xb") as handle:
        handle.write(raw)
print("Restored exact request:", row["originalPath"])
```

## Regenerate or repair artwork when authorized

First read the asset's metadata, saved prompt, references and current game consumer. Restore the request if needed. Verify the recorded reference hashes and current processing/geometry rules. Refresh provider/model availability and applicable project/budget/lock state before any separately authorized paid execution; do not blindly rerun old generation scripts or repurchase an existing successful result.

The archived request bytes can be reproduced exactly. A new AI-generated image cannot be guaranteed to match the old pixels, even with the same prompt and settings. Keep originals for this reason. A replacement still needs its own visual, role, matte, scene-registration and runtime review; successful generation is not game acceptance.

## Cleanup evidence

`generation-record-compaction-20261024.json` records every replaced path and original hash, compact-bundle hash, reconstruction checks and byte savings. `generation-record-preservation-20261024.json` verifies the remaining baseline files and reference images. `generation-record-size-20261024.json` records the measured project/Git size after compaction. No game code, provider/budget records, original image bytes, Git staging, commit or push were changed by this task.
