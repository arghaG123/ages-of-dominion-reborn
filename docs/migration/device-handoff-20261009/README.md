Language/framework/version: JavaScript ES modules, HTML/CSS/SVG; Node >=24, verified24.19.0. Transfer utility: Python3.12+ standard library. Image processing recordedPython3.13.7/Pillow12.3.0/NumPy2.5.3/OpenCV5.0.0/SciPy1.18.1.

The Git repository and local payloads together restore the current development inputs. The game remains INCOMPLETE. Git alone omits art, screenshots and raw provider lineage.

Read [the audit](../../plan/PROJECT-DEVICE-HANDOFF-AUDIT-2026-10-09.md) and give the next engineer [the complete seven-section prompt](../../plan/NEXT-DEVICE-COMPLETE-CONTINUATION-PROMPT-2026-10-09.txt). Exact files/hashes are in [transfer-manifest.json](transfer-manifest.json); publication SHA is the commit containing these files, or use the exact SHA from the owner's final handoff.

Copy these three payloads from the source computer into ONE directory on a USB drive/owner-controlled storage, then into the same directory on the new computer:

| Source path, relative to repository | Size | Purpose |
|---|---:|---|
| `assets.zip` | 5,101,034,547 bytes | All3,647currentasset files; every archive entry matches current disk by SHA256 |
| `output/device-transfer-20261009/qa-and-lineage.zip` | 1,527,831,417 bytes | Current/legacyQA pictures, native Actor receipt images,19rawresponses, healerwire and other excluded review/provider inputs;2,019entries |
| `output/device-transfer-20261009/final-audit-captures.zip` | See manifest | Fourlateviewportcaptures |

All payload entries have been read back and hash-verified locally. There is no remote asset upload or new-device restore proof yet. Keep originals and local payloads until the destination verification succeeds. Provider signatures are preserved as historical opaque response data; login credentials, browser profiles/user saves, signing material, Git internals and generated build copies are excluded.

Source-copy example (replace D:/Reborn-transfer with your actual writable drive; no online upload):

```powershell
Set-Location C:/dev/ages-of-dominion-reborn
New-Item -ItemType Directory -Path D:/Reborn-transfer -Force
Copy-Item -LiteralPath assets.zip -Destination D:/Reborn-transfer/assets.zip
Copy-Item -LiteralPath output/device-transfer-20261009/qa-and-lineage.zip -Destination D:/Reborn-transfer/qa-and-lineage.zip
Copy-Item -LiteralPath output/device-transfer-20261009/final-audit-captures.zip -Destination D:/Reborn-transfer/final-audit-captures.zip
```

Clone and restore on the next computer:

```powershell
git clone --branch main https://github.com/arghaG123/ages-of-dominion-reborn.git C:/dev/ages-of-dominion-reborn
Set-Location C:/dev/ages-of-dominion-reborn
git rev-parse HEAD
node --version
python --version
python docs/migration/device-handoff-20261009/transfer.py restore --payload-dir D:/Reborn-transfer
python docs/migration/device-handoff-20261009/transfer.py verify --payload-dir D:/Reborn-transfer
$testFiles = Get-ChildItem tests/*.test.mjs | ForEach-Object FullName
node --test $testFiles
node scripts/build.mjs
node scripts/serve.mjs --port 4501
```

Use the exact publication SHA from the final handoff if main has moved. Restore refuses unlike destination files and validates each ZIP hash before extraction; the tool also rejects path traversal/reparse points. Don't supply `--force`, alter hashes or silently overwrite new work. Tests currently have two missing-guide failures; restore of available payloads cannot recreate those absent originals. Build needs no Vite/dependency install and writes `dist/` plus a generated QA closure record. Native build requires separate JDK21/SDK36/Gradle setup; no physical device operation is authorized here.

Missing external inputs:

- Two exact historical guides in `qa/recovery-executor-20261003/guides/`: v4 SHA256609d3195018ccf448f339f79e45fe90b9e5adfb2859674e40383144d2106f848,52,050bytes; v5 SHA256673492a6a1c6780eb77d9b0b24f7eefe30a98dc119c7fbee9e3edef088b8c1ff,33,988bytes. Obtain original bytes from an existing previous-device archive.
- 124retiredrawresponse files/4,364,439,366bytes in `docs/asset-provenance/raw-response-archive-index.json`. Neither recorded E:final6ZIP nor C:loosebackup is available on this computer. Their compact metadata and current image references survive, but exact opaque signatures/serialization need the historical backup. This does not block normal game building; strict historical reuse/audit may need specific restored originals.
- Machine-local login/signing/SDK configuration is deliberately absent. Configure authorized access locally; do not put credentials into the transfer or repository.

The 256retired comparison previews can be restored without paid generation via:

```powershell
python docs/storage-cleanup/preview-retirement-20261009/restore-comparison-previews.py --restore
```

That tool preserves old manifest/source hashes and now discovers the repository root relative to itself. Its original exact256-entry regeneration proof and cleanup result are retained beside it. The transform to a relative root did not rerun the whole Image producer. Don't run producer helpers just to restore previews, because they can write art/interfaces/control records.
