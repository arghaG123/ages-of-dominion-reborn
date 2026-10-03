> **Current owner destination / timing — 3 October 2026:** Git destination is https://github.com/arghaG123/ages-of-dominion-reborn. This supersedes unknown repository/account/name in historical proposal below. Commit/push only AFTER replacement code AI next task completes and storage/restore prerequisites pass. Entireassets/ remains outsideGit. External archive plus independent durable-copy destinations/access/cost scope are still missing; no backup/upload/ignore/staging/commit/push performed by planner. Preserve all local originals and history; no move/delete. Read [current code prompt](REPLACEMENT-CODE-AI-PROMPT-2026-10-03.txt) for concrete order.

# Git and asset storage proposal — 3 October 2026

## Owner-selected Git exclusion — 3 October 2026

Owner says: "we can put asset , production folder out of git." The selected policy keeps the entire `assets/` tree, including `assets/production/` and `assets/delivery/`, outside Git. This supersedes the optional Git/LFS working-asset policy below for this tree. Exclusion means omit from Git tracking; it does not authorize moving, deleting or changing asset files.

Git retains independently authored source/tests/scripts, plans and decision history, sanitized asset catalogs with SHA256/size/provenance, and a pinned restore manifest/recipe. External assets must be restored to their expected local paths before offline packaging; the game does not fetch them at runtime. Preserve originals, raw responses, guides, rejected versions and important evidence in a verified archive plus an independent durable copy. Existing durable-copy/restore prerequisites remain; no broad QA or preview exclusion is selected by this decision.

Read-only Git planning inspection: branch `codex/rebuild`, no commits, zero tracked files and no remote. Source/docs/review text measured about 9.02 MiB; retained documentation reference media adds about 25 MiB. A selected initial Git file set is therefore estimated at 30–40 MiB before Git compression, excluding bulky preview/evidence media and all assets. This is not a measured remote pack or a promise that every file outside `assets/` fits that estimate. The asset tree measured 2398.75 MiB; additional QA/preview media still needs explicit classification under the archive policy. Local `.git` measured 887.53 MiB from uncommitted objects and temporary data, not pushed history.

The existing restore manifest remains `PROPOSAL_NO_EXTERNAL_BACKUP_OR_UPLOAD_PERFORMED`, with no destination and verification flags false. This planner records the owner decision only: no `.gitignore`/LFS/config edits, staging, commit, remote creation, upload, push, asset move, deletion, provider call or executor delegation occurred. Hosting/account, repository name/privacy and archive/backup destinations/cost scope remain to be selected. Older size tables below are historical snapshots.

Keep code, specifications and sanitized hash manifests in Git. Keep immutable production originals/raw responses and bulky visual evidence in a verified asset archive with an independent second copy. Use Git LFS only for the working binary set that benefits from revision history, or ordinary Git for a genuinely small stable optimized runtime pack. **Do not ignore assets until their durable copies and restore procedure are verified.** This is a proposal; no remote, upload, backup, LFS installation, ignore change or cleanup was performed.

## Measured local state

Branch `codex/rebuild` has no commits, zero tracked files and no remotes. `.gitignore` covers dependencies/builds/secrets but does not exclude the production/raw asset tree. There is no `.gitattributes` LFS policy. An unrestricted `git add .` would include raw embedded image payloads. Destination owner/account, privacy, remaining storage allowance, access and restore destination are not established.

| Local group | Files | Bytes | Approximate size |
|---|---:|---:|---:|
| assets/production, all eight batches | 321 | 1,331,547,948 | 1.240 GiB |
| Decoded originals, subset of production | 240 | 364,410,352 | 347.53 MiB |
| Raw prediction JSONLs, subset of production | 8 | 965,526,864 | 920.80 MiB |
| assets/delivery including evidence/versions | 57 | 50,394,581 | 48.06 MiB |
| design-preview/generated | 41 | 75,686,917 | 72.18 MiB |
| design-preview/art | 84 | 36,151,569 | 34.48 MiB |
| docs/plan before this audit's additions | 281 | 28,372,997 | 27.06 MiB |

These groups/subsets overlap and must not be added blindly. Existing QA adds large viewing/evidence copies and grows with every review. See the [file/size snapshot](../../qa/full-asset-verifier-20261003/inventory.json) and [restore manifest draft](../../qa/full-asset-verifier-20261003/restore-manifest-draft.json). Future archive capacity must account for originals, rejected/current derivatives, evidence, source guides and version history, not just the final compressed APK asset pack.

Six raw prediction files exceed 100MiB: batches01,03,04,05,06,08. Raw02/07 are still large. Raw files contain embedded images and repeated guides, explaining much of the size. Preserve exact originals for provenance; a smaller sanitized index can accompany them but cannot replace the only original payload copy.

## Options and current public constraints

| Option | Fit here | Constraint/tradeoff |
|---|---|---|
| Ordinary Git for every original/raw response | Poor | GitHub warns above50MiB and blocks individual files above100MiB; repeated binary revisions grow history. Six files already violate that hard limit. [GitHub file limits](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github). |
| Git LFS for working/runtime binary assets | Useful when collaboration/history requires it | Git stores a SHA/size pointer; the actual object must be available during restore. Repository download alone may contain pointers. [LFS model](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-git-large-file-storage). |
| Immutable object archive for raw/original/evidence | Recommended bulk archive | Content-addressed objects deduplicate exact bytes and retain provenance. Access, retention, operations/egress charges and independent backup/restore must be resolved before use. |
| Local working tree alone or ignored-only assets | Insufficient | Ignore is exclusion from Git, not backup; same-device copies cannot cover device loss. |

GitHub Free/Pro currently include10GiB storage and10GiB monthly download bandwidth; Team/Enterprise Cloud include250GiB each. Remaining account allowance is unknown. Every changed LFS binary stores the whole new version; clones, Actions and archive downloads count against the owner's bandwidth. A zero-dollar overage budget can block LFS usage after allowance exhaustion. Ten full1.24GiB production fetches alone would be about12.4GiB, before other assets/repositories. LFS is feasible at this scale but is not a free unlimited archival promise. [Current LFS billing](https://docs.github.com/en/billing/concepts/product-billing/git-lfs).

Google Cloud regional Standard storage in us-central1 is approximately US$0.02/GiB-month from the published hourly rate. At1.24GiB, production data storage alone is aboutUS$0.025/month before free allowances. General transfer to India/Asia is listed atUS$0.12/GiB in the first tier, so a full1.24GiB restore would be aboutUS$0.15 in transfer alone if no exemption applies. Operations, other assets, retained/noncurrent/soft-deleted copies, tax and actual account pricing are additional. These are small-volume estimates, not a billed total or authorization. Standard avoids the retrieval/minimum-duration tradeoffs of colder classes during active recovery. [Cloud Storage pricing](https://cloud.google.com/storage/pricing).

The existing generation output bucket being accessible does not make it an approved durable archive: its current policies/retention/permissions/cost scope were not queried here. No bucket or account settings should be changed as a convenience. Keep storage spending in an explicit scope; the generation ledger still has unknown invoices and a protectedUS$15 reserve.

## Proposed directory policy

1. **Ordinary Git:** independently authored source/tests/build recipes, specifications, decision/review JSON, small stable thumbnails where useful, sanitized source/derivation catalogs, restore metadata and script versions. Review data includes exact hashes and evidence pointers. Do not embed raw provider image payloads or credentials. Record frozen mechanics/reference text needed to implement/reproduce the project.
2. **Working binaries:** a deliberately bounded set of optimized runtime textures/atlases/animations and essential review fixtures. Propose an initial100–200MiB working-pack target, then measure quality/memory/build cost; it is not a new hard game-size requirement. If small and stable, ordinary Git may suffice. If repeatedly revised, use an explicit path-scoped LFS policy rather than blanket `*.png`/`*.jsonl`. Restore LFS objects before offline builds and verify object hashes; pointers alone do not satisfy artifact presence.
3. **Immutable asset archive:** all generated originals, exact raw responses, input manifests/guides, rejected derivatives and important lossless evidence. Store exact bytes under `objects/sha256/<first-two>/<full-hash>` with a versioned catalog. Derivatives never overwrite source objects. Keep a second independent verified durable copy on separate storage; archive access must survive the current workspace/chat.
4. **Regenerable local cache:** temporary contact sheets/thumbnails and build outputs can be excluded only after their original inputs, generation recipes and essential evidence are preserved. Owner rejection/acceptance proof, provider raw response and unique recovered artwork are not casually regenerable cache.

This policy is not applied yet. Do not add broad `assets/`, `qa/`, `design-preview/` or `docs/plan/image-production/` ignores now. Some of those paths contain the only useful bytes or review evidence. No deletion or history rewrite is necessary: there are no existing commits to migrate.

## Manifest and restore contract

The draft records local path, SHA256, byte count and proposed immutable object key. Its `remoteURI` is null and `externalCopyVerified`, `independentBackupVerified`, `restoreVerified` are false. It is local inventory metadata, not proof of upload/backup. Add resolved private archive object/generation identifiers, content type, source attempt/prompt hash, parent hashes, processing recipe/version, usage role, camera/registration/policy revisions and exact evidence links as applicable. Use sanitized persistent identifiers; no credentials, bearer tokens or expiring signed URLs in Git.

Build from a commit plus a pinned versioned asset manifest. An explicit development restore step resolves objects, verifies SHA/size, places each asset at its expected path and fails clearly on missing bytes. Downloads happen before packaging; the game includes local assets and retains zero runtime INTERNET/VIBRATE/other device permissions. Never make the offline APK depend on a cloud URI or asset streaming.

## Concrete execution gate and sequence

First select the exact private repo/archive/backup destination and account, agreed privacy/access/retention and cost scope; produce a dry-run list excluding secrets and provider lock/control prefixes. Preserve both source/art and planning history. Once the owner authorizes that concrete destination/scope, the responsible executor may create/upload immutable copies without replacing existing objects. Hash-verify all uploads and independently copied files. Resolve backup credentials/access separately from provider job controls.

Next restore a fresh isolated directory from the pinned catalog, including representative source/raw payload, guide, current/rejected derivative and essential reference/evidence, then verify all required hashes and a local build's asset completeness within the owner's authorized test scope. A complete release restore checks every required release asset, not just samples. Record missing/unrestorable files honestly. Only after two durable copies and a demonstrated restore should the executor apply narrow ignore/LFS policies, stage explicitly selected files, inspect staged paths/secrets/large-file sizes and create the initial commit. Push only to the approved remote. No cleanup of originals or deletion from either archive is implied.

Maintain referenced immutable objects indefinitely through the agreed project retention window. Any future lifecycle policy must preserve catalog-referenced hashes and independently verified copies. A Git commit or LFS pointer without retrievable bytes never counts as durable asset preservation.
