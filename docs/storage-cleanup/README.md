# Owner-authorized storage cleanup — 4 October 2026

> **Later QA cleanup:** Eight superseded QA APK copies (1,852,000,645 bytes) were removed after two verified plain-folder backups; 269 QA media paths (167,221,193 bytes) were removed from the Git index. Current/referenced media stays local; compact reports and helpers remain in Git. See [QA cleanup and restore](QA-CLEANUP-2026-10-04.md). No ZIP, commit, push or history rewrite. Earlier statements about tracked QA media and preserved APK copies below are historical.

> **Subsequent owner-authorized response retirement:** 124 bulky response/prediction files (4,364,439,366 bytes) have now been removed from working paths after two-copy/exact-restore/reference verification. See `docs/asset-provenance/README.md`. The earlier statement below that raw working files were untouched is historical. Original images and useful preparation remain. This phase created no ZIPs, per the owner's latest instruction.

The owner explicitly authorized local removal and Git storage cleanup in this chat. This extends this chat's authority to these storage operations; game implementation, paid generation, builds, device work and executor dispatch remain outside this cleanup.

## Completed

- Repacked Git without expiring reflogs or changing any reference. Verified `git fsck` before and after retirement. `main`, `origin/main`, the Codex checkpoint and HEAD remain unchanged.
- Archived 1,632 unreachable loose Git objects and 20 stale temporary files (3,282,518,639 bytes). Every archive entry was extracted into a separate local backup and SHA256/size verified before Git retired it. A fixed Unix timestamp and an unchanged dry-run inventory bounded pruning; newer objects were excluded. The original initial ISO timestamp produced an incomplete expiry selection and was replaced with the recorded Unix cutoff before any pruning.
- Removed 67 asset paths, two raw provider payload paths and six Python cache paths from the Git index. All 69 unique asset/payload files remain in place, were verified against the external migration archive, and have an independently copied local backup plus a clean external restore. Six cache files are reproducible. These deletions are staged; no commit or push was made.
- Excluded the entire `assets/` tree, Python caches, raw mock provider output and new bulky QA capture media from future Git discovery. Existing tracked QA/reference media and old commits remain preserved. Updated the migration allowlist generator to exclude assets, provider output and Python caches.
- Replaced 73 exact duplicate preparation-pack PNG copies with NTFS hard links to the retained native2K originals. All 73 pairs have matching SHA256/size and two verified link paths. This avoids about 381 MiB of duplicate image storage while preserving every existing lookup path. File-count/ordinary folder-size totals still count both paths.
- Deleted 15 Python cache files (442,421 bytes) and 1,032 regenerable Android intermediate/temp files (680,731,801 bytes). The signed/unsigned APK outputs, dist, native www, sources and unique QA evidence remain present. No rebuild or game tests were run.
- Applied reversible NTFS compression to 196 response/request/prediction files, checking SHA256 before and after. It saved only 30,219 bytes on this filesystem, so no meaningful compression saving is claimed.

The before/after measurements are in `before-2026-10-04.json` and `after-2026-10-04.json`. Git immediately after pruning occupied 2,175,635,064 bytes; newer tool objects can increase that while chats are active. `main` reachable objects occupy 341,689,903 packed bytes, separate from the larger preserved local Codex checkpoint. This is a local object measurement, not an estimate of the next network push; the configured remote already has the current HEAD.

## Archives and restore

External retired-object archive:
`E:\Ages-of-Dominion-Reborn-Migration-2026-10-04\git-unreachable-objects-preserved-2026-10-04.zip`

SHA256: `a64897d172df0ee65add54dbf22c7b06552de0ab2c76b31795dd0bf3253d30d0`.

Independent restored object bytes:
`C:\dev\ages-of-dominion-reborn-cleanup-backup-2026-10-04\retired-git-objects`.

Unique files excluded from the index also have `preserved-files` and `external-restore` directories under that local backup root. Their exact paths/hashes and external restore checks are in `untracking-preservation-2026-10-04.csv`. The external final6 migration ZIP remains unchanged.

Retired objects are recoverable by copying the selected verified `.git/objects/<prefix>/<suffix>` files back to the corresponding repository object directory while Git is idle. Do not restore `tmp_obj_*` garbage. Their presence does not itself recreate a reference or checkout; the object catalog allows a deliberate future recovery.

For a fresh game checkout, restore assets from the final6 migration ZIP and documented supplements to their original paths before building. Git alone intentionally omits assets after the staged removal is committed. Use the migration start guide and pinned archive hashes; no runtime downloading is introduced.

## Remaining boundaries

Unique original/raw response/guide/rejected/evidence files have not been deleted. The original image paths and approval states have not been changed. Production promotion still requires its recorded artwork acceptance checks.

NTFS hard links share one file's contents. The original-image preservation rule still applies: do not edit either linked original in place. Future regenerated output must be written to a new file and replace its path, or explicitly break the link first. ZIP transfers materialize ordinary separate files, so a restored laptop may need a fresh deduplication review; do not blindly rerun the original script.

No branch history rewrite or checkpoint-reference removal occurred. Assets removed from the index still exist in historical commits until a separately authorized history migration; this cleanup keeps shared history intact.

Archived Git objects were relocated outside the workspace onto both C: and E:. The workspace reduction is larger than the C: free-space gain, because the independent local recovery copy also consumes disk space. Exact per-file retirement, deletion and deduplication journals are beside this report.
