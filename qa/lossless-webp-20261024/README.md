## Publication update - 24 October 2026

Owner authorized scoped commit/push after the earlier hold. The 4,082-file hash check below predates the later owner-approved removal of 150 redundant image copies and compaction of 73 request bodies. Current preservation and size reports are under docs/maintenance/generation-record-*.json; all original image content remains available. Raw image/APK/capture files stay local. The installed snapshot has known visual limits and excludes newer concurrent UI repairs. See docs/maintenance/COMPRESSION-CLEANUP-PUBLICATION-20261024.md.

# Lossless compression - 24 October 2026

Owner closed scope to compression/folder-size reduction only. Further QA and game changes stopped; commit/push held while another AI repairs the game.

584 runtime assets: 837,145,276 to 550,125,668 bytes, saving 287,019,608 bytes (34.3%). 555 lossless conversions, 29 originals retained. Exact RGBA and metadata checks: asset-encoding.json. All 4,082 game originals freshly hash-match the cleanup baseline (5,851,277,465 bytes; zero missing/changed): original-assets-final-verification.json.

Existing preview APK: delivery/ages-of-dominion-reborn-preview-webp-20261024.apk, 551,755,653 bytes. SHA256 a6c71bf60cb70b90cb38c9648c2441e5be3dfcec0bd12e5bdb465bf21c397a0e. Debug signed, zero declared permissions. Concurrent source edits postdate it: snapshot-currentness-final.json. No duplicate rebuild.

Prior bounded checks: 315 Node tests, 2 encoder tests, 604 browser fixture cases. Initial failures and repaired reruns preserved. Native records are PARTIAL: navigation, route preview, Skirmish deployment/Defend/Retreat, Siege resume/pause, save/background/force-stop/reopen. Paused wave 2 / 400 HP persisted. Production package metadata unchanged; private production data not inspected. No preview matches in bounded crash buffer. Not full-game acceptance.

Open installed-snapshot observations: Adventure hero marker green/white crop artifact; spell targets offscreen after one swipe; prior Kingdom overlap. No fixes here and no further QA per owner. Seven representative captures retained as lossless WebP with exact RGBA verification; redundant task-generated captures omitted, all action JSON/XML retained (android/capture-lossless-encoding.json).

Final byte counts and strict <8GB project / <1.5GB Git result: size-final-verification.json. No game-source edits, staging, commit, push or further build in this continuation. Whole game remains INCOMPLETE.

Fresh-chat browser inventory exposed no in-app tabs; prior tabs could not be addressed. Viewport unchanged. Only server found was node scripts/serve.mjs without task-specific ports; left untouched to preserve concurrent work.
