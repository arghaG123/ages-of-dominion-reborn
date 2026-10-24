# Compression and cleanup publication - 24 October 2026

The owner requested normal commit/push after the earlier hold. Scope: build-only lossless WebP encoding, URL mapping, stale-web-build verification, scoped tests, cleanup manifests, exact regeneration recipes and verification documentation. This does not publish a game release or accept the whole game.

- 584 runtime assets: 837,145,276 to 550,125,668 bytes (34.3% reduction). The existing debug preview APK remains local and represents the verified earlier snapshot.
- Removed 150 redundant derivative copies with identical retained keepers (239,288,618 bytes). Original source images and every unique image remain.
- Replaced 73 duplicate embedded-image request bodies (123,330,733 bytes) with a 201,907-byte recipe bundle. Every request reconstructs byte-for-byte; receipts, budget and source metadata remain. Restoring originals/assets on another device still needs the locally preserved asset collection; Git excludes image payloads.
- Earlier 315 Node tests, 2 encoder tests and 604 fixture cases are bounded historical snapshot evidence. Fresh publication checks: 4 focused asset mapping/dependency tests and 2 encoder tests pass; compression-only main.js and build helpers parse. No new game/browser/device QA or APK build.
- Only compression edits from src/client/main.js are included, obtained from the verified APK snapshot and compared against HEAD. The shared working file is untouched. Other AI's UI changes in main.js, game.css, polish.css and visual-responsive tests remain uncommitted. Unrelated storage-growth/storage-ordering outputs and scratch files also remain local.
- Binary images, APKs, signing material, raw generation payloads, device-process logs and secrets are excluded. Hash-bound recipe JSON and structured QA reports retain exact bytes via .gitattributes.
- Whole-game acceptance remains INCOMPLETE. Existing Adventure crop and spell-target reachability observations remain open for the separate repair effort.

Publication SHA is the commit containing this document. Final remote/HEAD equality and post-commit folder/Git sizes are verified separately after push.
