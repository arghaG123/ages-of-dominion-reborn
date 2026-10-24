> LATEST OWNER CORRECTION: compression/folder-size work only. Stop further QA and game changes. No commit/push while another AI repairs the game. Compression complete; see qa/lossless-webp-20261024/README.md. Earlier QA/publication checklist below is superseded.

# Lossless WebP continuation — 24 October 2026

Owner requested a fresh chat FIRST to reduce context usage, then finish this exact task. This is an execution handoff, not completion. Work in C:\dev\ages-of-dominion-reborn, shared existing checkout. Preserve all dirty work. Do not start a worktree or delegate unless owner asks.

## Authority and scope

Owner authorized cleanup, normal commit/push, lossless WebP build compression, regenerated APK, and connected Android preview touch QA. Keep ALL original assets and current work. Explicit deletion choice was KEEP ASSETS, remove only the listed old QA captures; later owner authorized old APK removal. Never execute the declined asset-deletion manifest. Prior planner restrictions are superseded only for this explicitly authorized work. No paid image calls, production release publication, history rewrite, broad staging, or production phone-app/data changes.

Mobile game safety is essential. Test real touch/navigation/save/resume on preview package only. User has approved preview install and most recently replied 'Ready—run the preview touch checks'; no repeat permission needed. Whole-game acceptance remains INCOMPLETE; fixture rendering and compression checks do not prove all natural journeys or owner acceptance.

## Completed cleanup and publication

Prior cleanup pushed main commit 09bcf504634e5984420b001f6038d38b0a8aa110 to https://github.com/arghaG123/ages-of-dominion-reborn.git. Removed 4,934 listed QA captures (4.177 GB), unreachable loose blobs/trees (2.524 GB, no refs/commits/reflogs removed), and three old APKs (1.246 GB). Kept all 4,082 original assets, 5,851,277,465 bytes. Detailed manifests: docs/maintenance/footprint-20261024/README.md. Current compression changes are UNCOMMITTED.

Later, verified and removed duplicate 73,779,502-byte transfer ZIP (all 99 asset entries match originals), preserving its two metadata documents. Removed 30 old Git tmp_obj garbage files (113,524,736 bytes), connectivity passed. See current QA duplicate-archive and git-temp-cleanup JSONs. Overall project with new APK was about 7.967 GB before bounded native captures; strict target <8,000,000,000 bytes, Git <1,500,000,000 (currently about 1.016 GB). Tight headroom: no duplicate build trees/archives or bulk videos.

## Implementation already done

- scripts/build-lossless-webp.py: build-only PNG->lossless WebP, exact=True, RGBA pixel comparison plus dimensions/ICC/EXIF preservation; retains originals for unsupported/high-bit/animated/gamma-only files or when conversion is larger. Resume only with matching original and output hashes of previously verified rows.
- src/data/build-assets.json source placeholder {}. Build writes generated URL mapping only to dist copy.
- src/client/asset-url.js resolves relative/absolute/query/hash paths, including Android's double /assets/ URL prefix. src/client/main.js and actor.js route dynamic images/SVG/CSS/crops through resolver. Fixed Defense absolute crop lookup. Spell icon template now discoverable for all eight spells.
- scripts/build.mjs defaults lossless conversion; --original-images baseline option. scripts/verify-web-build.mjs verifies fresh source/asset hashes and closure. scripts/build-apk.mjs --use-existing-web verifies instead of reencoding; successful normal build cleans intermediates.
- tests/asset-url.test.mjs, tests/test_lossless_webp.py, expanded asset-dependencies tests.
- scripts/android-webp-smoke.py preview-only native accessibility inspection/taps, focus checks before/after dump and immediately before tap; rejects non-preview focus, ambiguous labels and zero-bounds targets. Screenshots opt-in.

## Verified results

QA root qa/lossless-webp-20261024/:

- 315/315 Node tests pass (node-tests.log); 2 Python encoder tests pass (encoder-tests.log), including transparent hidden RGB/ICC, corrupt resume derivative, animated/16-bit byte preservation.
- 584 runtime assets: 837,145,276 source bytes -> 550,125,668 packaged bytes; 555 converted, 29 retained. Saves 287,019,608 bytes (34.3%). All originals unchanged on last hash verification.
- Built-in isolated browser localhost:4175: 196 cases at 1280x720, 204 at 825x375, 204 at 933x424 = 604 fixture render cases. All 584 images decoded, zero errors in final reports. Eight ages, 14 main views (wide first run had 13), wall states, class/era heroes, skills/spells/inventory and 12 maps. Initial Defense resolver and harness resume timing failures are retained and fixed; do not erase history or call these natural journeys.
- Reports browser-verification.json, browser-825x375.json, browser-933x424.json. browser.html/mjs are harness, future-hero-webp.png actual browser capture.
- Final APK delivery/ages-of-dominion-reborn-preview-webp-20261024.apk = 551,755,653 bytes; SHA256 a6c71bf60cb70b90cb38c9648c2441e5be3dfcec0bd12e5bdb465bf21c397a0e. Existing Android Debug certificate v2/v3 signed, not production release signing. All 584 assets CRC/hash verified, source parity verified (except expected generated mapping). Zero declared Android permissions. apk-verification.json, apk-permissions.txt, apk-signature.txt and apk-build-final.log.
- dist, android generated www/intermediates/tmp were removed after verification to fit storage. Browser harness cannot rerun without rebuilding. Keep only this one APK; do not generate checkpoint APKs.

## Android currently active — continue here

ADB: C:\Users\pupan\AppData\Local\Android\Sdk\platform-tools\adb.exe. Discover serial live with adb devices; do not save serial in reports. CPH2767, Android16/API36, WebView155.0.8059.43. Physical landscape2800x1272, density560. Preview package com.agesofdominion.game.reborn.preview, activity com.agesofdominion.game.MainActivity. Production com.agesofdominion.game MUST remain untouched (metadata recorded production-package-before.txt).

Installation succeeded after owner approved phone prompt. Cold launch TotalTime324ms. Fresh disposable preview campaign: Stone Knight, Sunlit Riverlands, day1, starter resources250/250/160/150 and12melee/8ranged. Home, new campaign/world selection, class choice, Kingdom, Army and Hero touched. Home, class and Kingdom artwork inspected; old Kingdom Hall/HUD overlap means no blanket visual acceptance. Current screen: Hero 'Skills and spellbook' was just tapped. Last action saved qa/lossless-webp-20261024/android/09-hero-tabs.json and XML. Inspect fresh state before further taps; DO NOT blindly repeat tap. Last output truncated; action likely completed. Current native steps01–09 are preserved as JSON/XML, selected PNG only.

Use helper (requires host/hardware escalation): python scripts/android-webp-smoke.py --serial LIVE_SERIAL --name 10-descriptive-name [--tap-label 'EXACT observed text or content-desc'] [--screenshot]. Prints many nodes; cap output or filter saved JSON for clickable buttons. Helper reads actual accessibility tree, uses observed bounds, checks preview foreground each time. At initial attempt user switched into Settings; helper stopped; owner subsequently said Ready, no further issue. Never navigate Settings, change phone security, enable CDP, clear data, uninstall or update production app. No WebView debugging bypass.

Continue scoped native Hero spellbook, Adventure map/touch, Forge, locked Stone Market, Story, War, Skirmish/deployment/Tactical and Defense where naturally reachable. Read current Menu labels. Test Save and preview-only background/force-stop/cold reopen persistence. Retain bounded representative screenshots and inspect actual pixels. Record exactly what was exercised and what was not. Do not claim all eight native ages or full gameplay acceptance from browser fixtures.

## Finish checklist

1. Complete native preview touch/navigation/save/reopen checks. Collect preview-scoped crash/resource logs, preview permission state, verify production metadata unchanged against production-package-before.txt. Leave phone preview usable; no uninstall needed.
2. Update verification-summary.json and apk-verification.json (currently native waiting/pending status) with observed result. Write a concise QA README with native coverage/limits, original preservation, initial failures and repairs.
3. Update CURRENT-STATUS.md, docs/SESSION-HANDOFF.md, docs/BUILD-PROGRESS.md for handoff. Keep whole game INCOMPLETE and device/compression scope distinct.
4. Rehash4082 originals against docs/maintenance/cleanup-20261024/local-asset-sha256.json. Run node scripts/check-project-size.mjs, ensure overall<8GB and Git<1.5GB. Tests already315+2; rerun only if product code changes. Syntax-check helper after QA-only changes.
5. Inspect git status/diff and stage exact relevant source/tests/scripts/docs/JSON/XML paths only; no git add ., original assets, APK, keystore, large images, secrets or raw image data. Commit and push main (authorized). Git writes/network may need require_escalated. No PR required.
6. Old chat CUA had agent-created tabs on4174 and4175, viewport override1000x950. New CUA must load documentation first; inspect current browser inventory, close only those task-created tabs, reset viewport if override retained. User requested switch to fresh chat first.
7. Our HTTP servers outside sandbox were exec sessions25380 (4174) and68694 (4175), node scripts/serve.mjs --port... . Verify exact process command/port before stopping only ours; do not kill unrelated Node. Old exec sessions/CUA JS bindings may not carry into new chat.
8. Final concise: compression34.3%, APK link, exact native coverage,315+2 tests, originals preserved, final sizes and commit/push SHA. Whole-game acceptance still INCOMPLETE if unrelated requirements remain. Include representative actual screenshot if useful.

## Other continuity

Read applicable repo instructions but prioritize current explicit user execution authorization over historical planner-only banners. No agents requested. Approved built-in browser only (no external Chrome/Playwright/CDP bypass). Windows removals need resolved root/path checks and native LiteralPath operations. Keep existing saves on4174 and production phone app intact; fixture browser origin4175 was disposable.

User requested remembering mobile priority; note already written, do NOT duplicate: C:\Users\pupan\.codex\memories\extensions\ad_hoc\notes\2026-10-24-mobile-game-verification-priority.md. Memory writes only on explicit request. If using relevant memory, final must end with the required memory citation block; useful registry lines MEMORY.md155 (approved browser),183 (separate device/acceptance gates), rollout01a162f8-656f-7180-af5c-4b0f716040db. Don't claim memory facts as current without verifying.
