# Archived generation responses — 4 October 2026

Owner authorized archiving completed responses and removing their bulky working copies. The owner then explicitly said not to create ZIPs. No new ZIP or bundle was created in this phase; the existing verified final6 ZIP was used for restoration checks.

124 raw response/prediction files, 4,364,439,366 bytes, were removed from their former project paths after the complete preservation and image-reference checks passed. Their precise former paths, SHA256, byte counts, archive entries, compact records and image/signature references are in `raw-response-archive-index.json`. The append-only removal journal is `raw-response-retirement-journal.jsonl`.

Two retained copies of every exact original:

1. Existing external archive: `E:\Ages-of-Dominion-Reborn-Migration-2026-10-04\ages-of-dominion-reborn-worktree-2026-10-04-handoff-final6.zip`.
2. Independently restored loose files: `C:\dev\ages-of-dominion-reborn-cleanup-backup-2026-10-04\raw-generation-responses`.

Every external entry was extracted to the second folder and SHA256/size verified against its original before deletion. The full set was checked again before retirement. All surviving image references, metadata SHA256 and independent raw copies passed the post-retirement check. This is an archive/restore verification, not image appearance or game acceptance.

## Small records retained in Git

`raw-response-metadata/` contains 1,562,060 bytes of JSON/JSONL records. All response/request fields survive, with these two exact-data references:

- Image inline data is replaced by a retained local image path, SHA256, byte count and MIME. Images absent from the local catalogs were extracted without changing bytes into `assets/provenance/extracted-response-images/`; this does not approve them as game artwork. One missing image part was retained this way, 1,831,061 bytes.
- Large opaque `thoughtSignature` strings are replaced by their exact archived source path, record number, JSON Pointer, character count and UTF8 SHA256. Their full original strings remain in both raw backups; they are not truncated or recreated.

Each compact record was expanded in memory and compared with its original JSON object, preserving every key/value, including finish state, usage, response IDs, request fields and signatures. Exact original serialization is preserved by the raw backups, independently of semantic reconstruction. Initial direct metadata copies were reduced further because opaque signatures alone consumed about 1.7 GB; no bulky intermediate metadata remains.

Native/output PNGs, input images, request bodies, masks/guides, generation recipes, write-ahead records, lock/mutex/budget and historical evidence remain in place. Historical records deliberately retain original raw paths and hashes; this index resolves those paths to archived bytes.

## Existing readers and future work

The game/build asset pipeline reads PNGs and runtime manifests, not these retired raw responses. Existing image analysis/audit/reuse scripts may still require an original `response.json` or prediction JSONL. Restore the specific exact file before running such a script. Missing working raw files mean ARCHIVED, not a missing generation or permission to regenerate/re-purchase. The continuity runner currently fails closed when a raw reuse response is absent; do not weaken its hash checks.

From the repository root, restore one path:

```powershell
python docs/storage-cleanup/archive-raw-responses.py restore --path "assets/high-res/later73-preparation-packs/troop-stone-melee/response.json"
```

To restore all archived responses, use `restore --path all`. This copies exact original bytes back; it creates no provider call. On another laptop, pass `--backup-root "<downloaded raw-generation-responses folder>"` or `--external-zip "<downloaded final6 ZIP>"` to locate a retained copy. Never overwrite unlike destination files. Use `verify` to check the loose backup, metadata and retained images when the configured backup is available.

These raw responses are optional for normal game development/building but useful for exact historical audits, strict reuse and disaster recovery. Keep at least the two verified retained copies until another durable backup has been verified. The new laptop's normal project transfer can omit this raw-response folder, while a complete provenance transfer should carry it separately.

Moving raw data outside the project reduces project size. The separate local backup still uses C: space; this phase did not claim 4.36 GB of newly free C: space. Existing Git commits/checkpoints may also still contain historical raw data; working-copy retirement does not rewrite history.
