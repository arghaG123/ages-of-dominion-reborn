# Storage and publication audit - 24 October 2026

Owner authorized checking pushability, removing unnecessary files and QA older than ten days, then commit/push. This authority is scoped to maintenance/publication; no gameplay or image generation changes were made here.

The initial inventory totals 19,803,875,105 bytes (about 19.81 GB / 18.45 GiB). Largest folders: assets 5.85 GB, .git 4.77 GB, qa 4.65 GB, android 2.52 GB, dist 1.20 GB. Most QA volume is from 20-22 October and is inside the requested retention window.

## Push scope

Publish current source, tests, Android source/wrapper, configuration, plans, durable budget/provenance records, compact QA reports, and this audit. Existing Git exclusions retain assets, APKs, generated builds, captures, credentials and archives locally. Added exclusions keep raw image request/response wires local. The local asset SHA256 manifest records 4,082 assets; their bytes are not included in Git. A Git clone alone is insufficient to restore the playable art. Do not discard the local assets.

The eligible-file scan found no private-key/GitHub-token patterns or embedded image payloads; no eligible file exceeded 5 MB. This is a bounded scan, not a general security certification.

## Cleanup outcome

**BLOCKED; zero files deleted and zero bytes reclaimed.** Automatic approval review rejected both the exact manifest deletion and a narrower generated-build-only command, returning only `blocked by policy`. No alternate deletion mechanism was used.

`cleanup-manifest.json` lists 3,133 exact proposed removals totaling 4,267,361,735 bytes: 3,065,893,374 generated build/cache bytes, 1,118,298,112 abandoned Git temporary-object bytes dated before 22 October, 82,978,021 obsolete QA bytes, and 192,228 Python-cache bytes. It is a proposed manifest, not a deletion receipt. Recheck existence, size, active writers and references before any later execution.

The QA cutoff is 14 October 2026, using the run date encoded in each QA folder. Retained older QA includes executable helpers, production receipts/accounting, exact guides, inputs referenced from source/tests/scripts/asset contracts, and their transitive metadata dependencies. Date alone cannot identify those as disposable. Historical documentation can still cite proposed obsolete outputs; they would become intentionally expired evidence after deletion, never current acceptance proof.

Preserve all assets, existing APKs, current QA, source/plans, dependencies, browser state/saves, named Git objects and commit history. No history rewrite, forced push, Git prune, asset deletion, package build, device action, or paid call was performed.

## Validation

`node --test tests/*.test.mjs`: **311 passed, 0 failed**, 24 October 2026. Tests can regenerate their existing QA fixture outputs. This is bounded Node evidence only. No new browser, visual, natural-player, native/device or owner acceptance was performed. The game remains **INCOMPLETE**; future QA must match the current game source.
