# Ages of Dominion reborn: new-laptop start here

**Prepared 4 October 2026.** This is the current migration entry point. The Git base is `main` at `cff552880ae15c892b736ac7847f6753787ca58f` (`origin/main`); substantial current executor work is dirty/untracked and is not in that commit. Use the archive manifest, not a clone alone, to recover this device's complete current state.

## Game origin and scope

This is an independently authored offline rebuild of Ages of Dominion. The original checkout `C:/dev/ages-of-dominion` and raw art/config tree `C:/dev/aod-art-src` are read-only references. Do not import their executable gameplay/client/core. Preserve the permanent app id as reference and use `com.agesofdominion.game.reborn.preview` for any separately authorized preview installation. The whole game is LANDSCAPE and includes all eight ages (Stone, Bronze, Iron, Medieval, Gunpowder, Industrial, Modern, Future), connected Kingdom/Adventure/Tactical modes, eight hero classes, six functional equipment slots, and the full supporting campaign, economy, building, army, defense, story, tutorial, save and native-offline requirements. See `docs/plan/FULL-IMPLEMENTATION-SPEC.md`, `MASTER-PLAN.md`, and `REQUIREMENTS-MATRIX-CANONICAL-2026-10-04.md`.

## First read and current evidence

1. `AGENTS.md`, `START-HERE.md`, `CURRENT-STATUS.md`, `DECISIONS.md`, `docs/SESSION-HANDOFF.md`, `docs/BUILD-PROGRESS.md`, and `docs/PLANNER-VERIFIER-HANDOFF.md`.
2. `docs/plan/README.md`, `docs/plan/INSTALLED-ENVIRONMENT.md`, `docs/plan/FULL-IMPLEMENTATION-SPEC.md`, `docs/plan/REQUIREMENTS-MATRIX-CANONICAL-2026-10-04.md`, and `docs/plan/BOTH-AI-V3-INDEPENDENT-VERIFICATION-2026-10-04.md`.
3. Current independent prompts: `docs/plan/CODE-AI-AFTER-V3-AUDIT-2026-10-04.txt` and `docs/plan/IMAGE-AI-AFTER-V3-AUDIT-2026-10-04.txt`. The latest image-side local repair handoff is `docs/plan/IMAGE-V4-LOCAL-REPAIR-HANDOFF-2026-10-04.md`; latest code continuation is also recorded in `docs/plan/CODE-AI-RESUME-2026-10-04.md`.
4. Evidence is in `qa/both-ai-v3-independent-20261004/`, with related executor evidence in the QA directories named by the current reports. Read actual screenshots/pixels when judging visual work.

As of the report: fresh 82-test suite PASS; bounded four-landscape-size placement/picking PASS; static 261-file APK web closure PASS for SHA256 `90d0687844321ef1e0964da884e4e3906b0e7d5d465a94a1c5598da9db46ce75` / 296,625,603 bytes. Full game, visual acceptance, manual journeys, native runtime, owner acceptance remain INCOMPLETE/UNVERIFIED. Physical device testing is STOPPED. Image delivery has useful improvements but named actor/rig/terrain/interface defects remain. Accounting retains unknown liabilities/invoices; no new paid scope is authorized by migration. Do not treat the old APK under build output as current without checking its manifest/hash against current source.

## Role boundaries for any new AI

- **Planner/verifier:** inventory, specifications, independent evidence review, acceptance criteria and scoped prompts only. Do not execute provider, game, build, native/device, archive upload or Git delivery work unless the owner changes that role.
- **Code AI:** use the Code prompt; continue authorized local game/source work, preserve contracts and prior evidence, and record tested vs visual vs owner-accepted status separately. No provider operations, device tests, deploy/publish, destructive storage cleanup or Git commit/push without separate authority.
- **Image AI:** use the Image prompt; continue local source/derivative/interface repairs and follow its current paid-scope/budget/lock instructions. The account being configured on this laptop does not prove job status, billing, ownership or invoice reconciliation. Do not query providers or start a paid request based only on this transfer packet.
- Never let art/device/morale/storage gates stop unrelated ready work. No blanket acceptance inferred from hashes, filenames, decoding or tests.

## Transfer and restore

Use `docs/migration/TRANSFER-INCLUDE-2026-10-04.csv` for exact project files and bytes, and `TRANSFER-EXCLUDE-2026-10-04.txt` for regenerable/local-secret exclusions. A ZIP and complete-history Git bundle were created on external drive `E:\Ages-of-Dominion-Reborn-Migration-2026-10-04`; see `docs/migration/README.md` and the adjacent `ARCHIVE-CHECKSUMS.txt` for exact names and SHA256. No credentials, tokens, `.env`, account/browser caches, signing keys, local.properties or old saves belong in the transfer. The external drive is only one copy; make and verify an independent second copy, then perform a clean restore on the new laptop before wiping the old device.

### Clean restore sequence

1. Copy the ZIP, bundle, checksum file and CSV manifests to the new laptop. Check the ZIP and bundle SHA256 against `ARCHIVE-CHECKSUMS.txt` before opening them.
2. Clone branch `main` from the bundle into a fresh target folder, for example `git clone --branch main E:/Ages-of-Dominion-Reborn-Migration-2026-10-04/ages-of-dominion-reborn-main.bundle D:/AgesOfDominion/ages-of-dominion-reborn`. Set `origin` to the recorded GitHub URL only if that remote is wanted on the new device; do not push.
3. Extract the ZIP over that clone, preserving its relative paths and allowing the ZIP files to replace matching base files. The ZIP has no `.git`, so the cloned history remains intact. This overlay restores dirty edits and untracked executor work.
4. Verify every CSV path exists with its recorded byte count and SHA256; compare `git status --short --branch` with `GIT-WORKTREE-STATUS-2026-10-04.txt`, allowing only later authorized changes. Reopen the current report and linked evidence, and confirm at least representative originals, raw responses, derivatives, mock images, and QA screenshots open correctly.
5. Reinstall dependencies and verify current tools/SDKs on that machine. Keep both old and new devices until the independent second copy and this clean restore are complete and owner-checked.

## Path portability

Some dated docs intentionally preserve historical `C:/dev/...` evidence. Several current analysis scripts also hardcode the old checkout root; update only those scripts to resolve their root relative to `__file__`/repository root before running them on another drive. Search `C:/dev/`, `C:\\dev\\`, absolute interpreter paths and `python3.13` in the new checkout. Replace path assumptions with repository-relative paths; keep old reference paths as documented optional read-only inputs. Existing bundled workspace runtimes on this device are not transfer dependencies. No tokens or local account configuration are copied.

## Status of this migration preparation

Prepared: this entry point, separate planner/Code/Image resume prompts, exact include/exclude list, Git allowlist proposal, verified ZIP and Git bundle. Pending: hash-verified independent second copy, clean restore on the new laptop, and owner confirmation before old-device wipe. No source files were deleted, ignored, committed, pushed, or uploaded for this migration.

