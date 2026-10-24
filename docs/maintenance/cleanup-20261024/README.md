# Storage cleanup and publication - 24 October 2026

**Cleanup COMPLETE.** After the owner updated the session permission mode, the verified deletions succeeded. Removed 3,133 files totaling 4,267,361,735 bytes (4.27 GB / 3.97 GiB). The earlier blocked attempts deleted nothing; their status is superseded by the receipts here.

## What was removed

- Generated `dist`, Android web copies/intermediates/cache: 3,065,893,374 bytes. Existing APK outputs retained.
- Obsolete QA from run folders dated before 14 October: 82,978,021 bytes.
- Untracked Python caches: 192,228 bytes.
- Exactly 80 abandoned Git `tmp_obj_` files dated before 22 October: 1,118,298,112 bytes. Confirmed no Git processes were active before deletion. Newer temporary files remain. No named object, commit, pack or history was removed.

Every file matched its recorded size before removal and every resolved target stayed inside the canonical workspace. `cleanup-manifest.json` lists the exact removal set; the two phase receipts record non-Git removals and Git temporary-file removals. `dist` was removed separately after confirming it held no tracked files. No manifest target remains after the verification suite.

## What was preserved

All 4,082 assets were independently SHA256-checked after cleanup: **zero missing, zero changed**. See `local-asset-sha256.json` and `asset-verification.json`. Current source/work, all APKs, browser state/saves, dependencies, plans and generation accounting/receipts remain. QA dated 14 October or later remains. Required older helpers, fixtures, exact guides and transitive code/asset-contract inputs were retained. The majority of QA volume comes from 20-22 October and falls within the retention window.

Before cleanup the project held 19,803,875,105 bytes (19.80 GB / 18.44 GiB). The immediate post-cleanup inventory was 15,539,829,353 bytes (15.54 GB / 14.47 GiB), including added audit/commit records. The removed-file byte sum is the authoritative reclaimed amount; Git and documentation can grow slightly during publication.

## Git scope and validation

Source, tests, Android source/wrapper, configuration, plans, compact QA reports and durable provenance are versioned. Assets, APKs, captures, archives and raw image request/response wires remain local and excluded from new Git additions. A Git clone alone cannot restore the art; preserve the local asset folder. The earlier eligible-file scan found no credential patterns or embedded image payloads in the publication candidates.

After cleanup, `node --test tests/*.test.mjs`: **311 passed, 0 failed**. This is bounded Node evidence only; no new browser/visual/natural-player/native/device/owner acceptance or package build. The whole game remains **INCOMPLETE**. Future QA must match the current source.

The owner already authorized cleanup and commit/push. No game source/asset repair, paid call, history rewrite, forced push, device action or additional backup/archive was performed in this maintenance pass.
