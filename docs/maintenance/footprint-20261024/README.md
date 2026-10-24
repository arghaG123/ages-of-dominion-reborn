# Project footprint and packaging repair - 24 October 2026

**Both strict decimal limits pass:** approximately 7.60 GB for the entire project, including assets and Git; 1.13 GB for `.git`. Limits are 8,000,000,000 and 1,500,000,000 bytes. Run `node scripts/check-project-size.mjs` for current sizes; publication can add a small amount of metadata.

## Owner decision and completed cleanup

The broad unused-art deletion proposal was rejected by automatic review. The owner then selected **Keep assets; remove only listed QA captures**. No asset files were deleted or recompressed. The original `content-cleanup-manifest.json` is a historical proposal: its 2,060 asset-deletion entries were NOT executed. Do not execute that whole manifest. Only its exact 4,934-file QA subset was approved and removed.

- Removed 4,934 redundant/regenerable QA captures: 4,177,117,174 bytes. Current independent dossier, cited current captures, latest 23 October repair evidence, exact guides, source/test inputs and structured findings were retained.
- Removed 1,478 loose Git blobs/trees: 2,523,705,303 bytes. `git fsck` independently reported them unreachable, with no unreachable commits. Compared all refs/reflogs before removal, protected the index, checked no Git processes were active, and passed connectivity afterward. No branch, commit, reflog, pack, remote history or source file was removed. No history rewrite or force push.
- Removed all three stale APKs: 1,246,081,446 bytes. The owner also explicitly requested removal for regeneration. All mismatched current source (39, 55 and 37 missing/different source files respectively). Exact package hashes and mismatch lists remain in `obsolete-apk-manifest.json`. There is currently **no retained APK**; a future completed-game snapshot must be rebuilt and verified through the existing release gates.
- Removed the temporary verification web build after measuring it. Existing source and assets remain.

These three cleanup sets total **7,946,903,923 bytes**, excluding removal of the temporary test build. All deletions used explicit preflighted paths and hash/size checks; no blanket asset-folder deletion.

All **4,082 assets / 5,851,277,465 bytes** match their original SHA256 hashes: zero missing, zero changed. Current source/work, approved mocks, generation receipts, unknown-call liabilities, prompts, provenance and source images were kept. `generation-history-index.json` indexes retained production/provenance records. Earlier hash manifests remain history, not a substitute for native bytes.

## What the actual game weighs

| Component | Measured size |
| --- | ---: |
| Game source, including JSON/config and styles | 1.97 MB |
| Conservative pre-repair build image list | 1231.28 MB / 810 files |
| Verified revised build image payload | 828.72 MB / 577 files |
| Retained asset workspace (all versions and sources) | 5.85 GB |

The entire project size includes Git, unused source art, QA, dependencies, historical transfer material and docs. Those bytes are not the runtime game size. Source is tiny; artwork dominates. Most of the former non-asset/non-Git volume was QA and APK copies.

## Build changes and evidence

The previous build included every runtime-PASS `consumer-catalog` output even though the current game reads that catalog only for dimensions. It also packaged provenance-only source/reference paths. The collector now distinguishes loaded image fields from provenance, selects the same display/fallback images used by consumers, includes production Adventure maps rather than reference examples, expands skill templates to all matching assets, and enumerates every Kingdom age/wall phase. The build now uses this single closure instead of a second manual copy list.

The verified uncompressed image payload is reduced by **402.56 MB (32.7%)**. No game source/data/geometry or source pixels changed. `build-closure.json` records each packaged path, byte count and SHA256. The standalone web build passed missing-file and no-network checks. Two new closure tests cover all production maps, skills, 32 wall phases and exclusion of review-only outputs.

After a future successful APK build, `build-apk.mjs` now removes duplicate `dist`, Android generated web copies, and intermediates/tmp by default while retaining the resulting APK. `--keep-intermediates` retains them for diagnosis. This cleanup path was syntax-checked, but **no new APK/Gradle build was run here**, so native packaging and the new post-APK cleanup remain unverified at runtime.

## Further APK reduction: measured, not yet adopted

The old 616.30 MB APK contained 615.05 MB of PNGs; DEX was only 0.85 MB. Native code shrinking cannot materially solve that asset volume. Android lint does not scan the `assets/` folder, which is why the explicit web dependency closure matters. [Android size guidance](https://developer.android.com/topic/performance/reduce-apk-size).

A five-image lossless WebP experiment reduced 53.24 MB to 37.42 MB (29.7%), with exact decoded RGBA equality and identical dimensions, including transparency. No converted images were stored or bound into the game. Lossless PNG re-encoding sometimes increased size, so a blanket recompression is not justified. [WebP format documentation](https://developers.google.com/speed/webp/).

A future lossless WebP pass must update dynamic filenames, source bindings and package hashes together and verify browser/WebView image loading. Downscaling, lossy conversion and visual changes were not performed. The sample result is not a whole-game saving estimate or APK measurement. The current game has more art than the old APK; comparing the revised web payload directly with that stale APK would be misleading.

Keeping every source asset means a future generated APK/build can temporarily push this folder over 8 GB. The size checker includes generated copies and APKs; it does not hide them or count an external relocation as deletion. The APK build now cleans redundant successful-build copies, but final package/image optimization and storage remeasurement are still required at release.

## Validation and acceptance

**313 Node tests passed / 0 failed after cleanup**, including two new package closure tests. Source syntax checks and Git connectivity passed. All 4,082 asset hashes remain identical. `size-verification.json` records both byte-limit gates. No paid call, new APK, device action or new visual/owner acceptance was performed; whole-game acceptance remains **INCOMPLETE**.

Qodo identity succeeded outside the sandbox, but the installed CLI rejected this skill's rules-search flags; no Qodo standards were loaded. A passive skill-update notice was left untouched. No tool or dependency was installed or updated.
