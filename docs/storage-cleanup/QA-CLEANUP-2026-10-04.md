# Owner-authorized QA cleanup — 4 October 2026

Owner authorized deletion of unnecessary QA and reducing Git size, while retaining helper source in Git. No ZIP was created, no game/provider/helper test was run, and no commit, push or history rewrite was performed.

## Completed

- Removed eight superseded QA APK copies: **1,852,000,645 bytes**. These represent six distinct older packages, including two exact duplicate copies totaling 335,596,926 bytes. The current APK under `android/app/build/outputs/apk/release/` was not selected or modified.
- Removed **269 QA media paths, 167,221,193 bytes**, from the Git index. Existing unique/current screenshots, recordings, fixture images and other retained media stay at their original local paths. Small QA reports, manifests and helper sources remain in Git. The new staged exclusions keep future QA binaries/media out of Git.
- Preserved every selected APK and tracked-media file as hash-addressed objects in two independent folders, verified by SHA256 and byte count before deletion/untracking. Shared identical content is stored once per backup. No ZIPs or uploads.
- Kept duplicate screenshot/fixture paths, because relative and glob references may depend on them. Age alone did not qualify unique evidence for deletion. Current v4/v5 delivery evidence and unresolved-defect records remain available.

## Recovery

Backups:

- `E:\Ages-of-Dominion-Reborn-Migration-2026-10-04\qa-retired`
- `C:\dev\ages-of-dominion-reborn-cleanup-backup-2026-10-04\qa-retired`

Each has `index.json` and `objects/<SHA256>`. For an old historical report's APK path, use the exact matching index row; bytes were archived, not regenerated. Example:

```powershell
./docs/storage-cleanup/restore-qa.ps1 -RelativePath 'qa/code-ready-20261004/preserved-apk/04c66255-app-release-unsigned.apk'
```

Pass `-BackupRoot '<downloaded qa-retired folder>'` on another device. The helper verifies the archive and restored file and refuses to overwrite an existing path. Retired APK locations in prior reports are historical; this index supersedes their physical-location claims.

## Git and transfer implications

The removals/exclusions are staged for the next authorized commit. Old commits still contain their old QA objects. The local repository's large retained Codex checkpoint also remains. Untracking stops future commits from adding this media; it does not purge existing history or immediately shrink `.git`.

The migration allowlist now excludes QA media even if previously tracked. Retained QA media belongs in the non-Git transfer list only when needed on the other device. The new `qa-retired` backups are optional historical recovery, not required game content. Assets are still transferred separately. Git must be committed/pushed before the other device can pull these current changes.

The workspace shrank by 1.85 GB from these deletions. The local preservation copy consumes C: space outside the project, so this is not a claim of 1.85 GB additional C: free space.

Per-file plan, deletion journal, result and preservation checks are alongside this report. Future builds may preserve a previous APK into QA again; ignore rules cover those new files, but this cleanup helper uses the fixed reviewed hashes and must not silently delete a new/current APK.

## Preservation check

All 1,434 retained media paths remain present; 1,424 match the initial SHA256 snapshot. Ten `qa/code-playable-20261004/` captures were rewritten during concurrent work. Their current bytes were kept; the cleanup deletion scope contains only the eight reviewed APKs. All 108 QA helper sources match their initial hashes. Current APK SHA256 remains `02f85e52c5c1aab755e42374bfd2c166f7ba0d5e23519314830de0e00b5694bd`, 319,425,603 bytes. Zero QA media paths remain tracked. This storage check is not a game test or visual acceptance.
