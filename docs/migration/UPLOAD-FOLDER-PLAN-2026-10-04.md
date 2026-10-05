> **Latest QA cleanup snapshot — 4 October 2026:** No ZIPs created. Eight old QA APK copies (1.852 GB) retired to verified C:/E: plain-folder recovery stores. Retained QA media is excluded from Git; helpers/reports stay included. Refreshed planned Git set: 1,261 files / 102,547,285 bytes (working-file bytes, not .git or push size). Transfer-only snapshot: assets 3,655,992,046 bytes; retained QA 623,655,302 bytes; one other local data file 96,017 bytes. The qa-retired folders are optional historical recovery. Latest changes are local/staged until committed and pushed; earlier size tables are historical. See docs/storage-cleanup/QA-CLEANUP-2026-10-04.md.

# Drive transfer folder choices — 4 October 2026

> **Latest owner helper correction:** All retained helper source under `scripts/`, `qa/` and `scratch/` is now selected for Git and staged. These helpers no longer require separate ZIP transfer once the Git delivery is pushed. `refresh-transfer-manifests.ps1` automatically refreshes the transfer-only set after subtracting the updated Git selection. Current totals are in `NON-GIT-TRANSFER-SIZES-2026-10-04.json`; earlier helper-row/count figures below are historical. Any residual non-asset/non-QA transfer rows are local data/notes, not omitted helper code. No ZIP, commit or push occurred here.

Owner instruction: do not create any ZIPs yet; list the folders first so the owner can decide who packages them. No ZIP/bundle or cloud upload was created in this response-retirement phase.

> **Latest owner correction — Git plus transfer-only files:** Source/config/docs should come from Git after the latest approved file set is committed and pushed. A fresh `git ls-remote` still shows `main` at `cff552880ae15c892b736ac7847f6753787ca58f`; 256 tracked paths differ locally, with additional untracked work. The latest code and cleanup have NOT been pushed, so Git alone cannot yet restore the current project. Do not package project source twice once that push has been verified. No push or ZIP was performed here.

## Selected plan after the latest Git delivery

Use Git for the intended repository file set in `GIT-ALLOWLIST-2026-10-04.csv`. Transfer only the other project files listed in `NON-GIT-TRANSFER-2026-10-04.csv`:

| Transfer group | Files | Current approximate size |
|---|---:|---:|
| Entire assets folder, intentionally outside the future Git index | 2,752 | 3.63 GB |
| QA/evidence paths outside the planned Git set, listed individually | 1,609 | 2.25 GB |
| Other local files outside that planned set: 100 small analysis/capture/preparation scripts, saved provider metadata and scratch notes | 102 | 0.94 MB |

The measured transfer-only set is 4,463 paths / 5,876,447,972 bytes (about 5.88 GB). Preserve their original repository-relative paths. Include the small companion transfer CSVs from `docs/migration/` as verification indexes; these manifests are excluded from their own hash lists and the proposed Git set. The optional 4.36 GB raw-response backup remains separate, as described below.

QA grew while another executor continued working. The transfer-only list excludes QA already in the planned Git delivery, including old tracked proof/reference files. The simple option is the entire QA folder, with some repeated files; the exact minimal duplication option is the CSV-selected QA paths. The small extra scripts currently outside the proposed Git selection must also travel unless a later Git delivery explicitly adds them.

This split is CONDITIONAL: verify the pushed commit and that its selected files match the intended snapshot before omitting source/docs from the archive. If a file is not actually in the pushed commit, it must travel as a local difference. After future executor changes or a changed Git selection, regenerate the lists. `GIT-TRANSFER-READINESS-2026-10-04.json` records the current not-yet-pushed state.

## Earlier full-worktree fallback (historical)

The source ZIP in the older fallback below was for migration before the latest Git delivery. It is unnecessary after the code/docs are correctly pushed; it remains a recovery fallback while that delivery is pending. Older measured counts/sizes below are dated snapshots.

Current transfer content is about 5.49 GB before ZIP compression: project files about 0.10 GB, assets about 3.63 GB, QA about 1.76 GB. The measured CSV scope contains 5,708 paths / 5,487,072,267 bytes; add the small `docs/migration/` folder, which is deliberately outside its own hash CSV to avoid self-reference. This is a current snapshot, not a promise that later executor work is already included.

## Full-worktree fallback before Git delivery

| Suggested future ZIP | Select from `C:\dev\ages-of-dominion-reborn` | Current approximate input size |
|---|---|---:|
| `project-source.zip` | Root project/config/status files, `src/`, `scripts/`, `tests/`, `docs/`, `design-preview/`, `scratch/`, and Android source/build configuration as below | 0.10 GB |
| `assets.zip` | Entire `assets/` folder, including production originals, high-res originals, preparation inputs, derivatives, consumers/delivery and the extracted provenance image | 3.63 GB |
| `qa-evidence.zip` | Entire `qa/` folder, retaining reviewed/failure/history evidence and preserved artifact records | 1.76 GB |

Keep these root-relative paths inside the packages, or extract each selected top-level folder back into the same new repository root. `docs/` includes the small response metadata/index, storage restore helper and migration manifests. `assets/` contains the image bytes referenced by source and those records. QA is part of the development/evidence handoff, not the APK's normal runtime input.

Android source/config means `android/app/src/` **except** `android/app/src/main/assets/`, plus `android/app/build.gradle`, root Android Gradle settings/properties, `android/gradle/`, `android/gradlew` and `android/gradlew.bat`, and any other retained non-generated configuration. The included Android source includes Java/resources/manifest; do not select only the Gradle files. Build scripts reconstruct the generated native www before APK packaging.

Retain root files such as `.gitignore`, `.gitattributes`, `AGENTS.md`, `START-HERE.md`, `CURRENT-STATUS.md`, `DECISIONS.md`, `README.md`, `RESUME-HERE.md`, `NEXT-CHAT-MAP-PLACEMENT.md`, `index.html`, `package.json` and `package-lock.json` where present. The exact transfer CSV is authoritative for additional retained root/config paths; do not omit a root file merely because this example list is short.

## Optional separate historical-response backup

Folder:
`C:\dev\ages-of-dominion-reborn-cleanup-backup-2026-10-04\raw-generation-responses`

Its 124 original payload files total 4,364,439,366 bytes (4.36 GB), plus a small archive index and README. They are optional for ordinary game coding/building; retain/transfer this folder separately when exact raw audits, signatures, strict old-request reuse or complete provenance are needed. Do not merge these raws into the normal project ZIP and inflate it again. On restore, pass this downloaded folder as the helper's `--backup-root`.

The same exact raws already exist in the preserved external final6 ZIP. Keep existing copies until a newly uploaded/downloaded Drive copy passes SHA256 and restore checks. This new folder choice does not instruct uploading every older intermediate migration ZIP.

## Exclude from the project transfer

- `.git/` — if Git history is needed, use the configured repository or separately retain the existing verified bundle. The existing 2.16 GB bundle also contains a local Codex checkpoint; it is optional for ordinary code continuation. Never upload the Git directory as part of the source ZIP.
- `node_modules/`, `dist/`, `android/.gradle/`, `android/**/build/`, `android/app/src/main/assets/`.
- `__pycache__/`, `*.pyc`, `.pytest_cache/`, `.mypy_cache/` and OS temporary files.
- `.env*`, `android/local.properties`, `key.properties`, `google-services.json`, `*.jks`, `*.keystore`, account/browser profiles, tokens and SDK/runtime caches. Configure device-local tools separately.
- Local recovery directories outside the repository, including retired Git objects. Do not add them to the normal source/assets/evidence ZIPs.

The latest standalone unsigned APK may be copied separately only if the owner wants that existing preview artifact: `android/app/build/outputs/apk/release/app-release-unsigned.apk`, 297,724,620 bytes. It is optional for development restore and does not establish game/device acceptance.

## Restore and verification

Restore source, assets and QA under one new `ages-of-dominion-reborn` root. Restore dependency/tool configuration locally using the recorded requirements; do not copy machine credentials or `node_modules`. Use the transfer SHA256/size CSV to check content after download. Read `docs/asset-provenance/README.md` before running a legacy raw-response auditor or reuse runner; missing raw working paths mean archived, not permission to regenerate.

The existing Git bundle preserves the previous commit/index state, not this dirty working tree. If cloning from the configured repository or bundle, deliberately replay the documented index exclusions in `docs/storage-cleanup/untracking-preservation-2026-10-04.csv` before a later commit; ignore rules alone do not untrack historical assets. No commit/push occurred here.

If any executor changes files after this snapshot, refresh transfer manifests and review changed paths before packaging. No new ZIPs are needed until the owner decides to create them.
