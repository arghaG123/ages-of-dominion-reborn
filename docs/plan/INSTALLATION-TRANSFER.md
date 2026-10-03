> **LATEST OWNER CORRECTION — planner/verifier only, 3 October 2026:** This chat creates the specification, execution instructions, acceptance criteria and reports. Another AI must execute image batches, game code, builds, collection and regeneration. Do not resume execution or delegate it from this chat. This supersedes previous implementation/production execution authorization interpreted for this chat. Approved landscape appearance direction, full scope and budget constraints persist. Read the current report at `docs/PLANNER-VERIFIER-HANDOFF.md`; older execution status below is historical.

> **CURRENT OWNER AUTHORITY — 3 October 2026:** generated landscape mock direction approved despite synchronization defects; fresh implementation and useful Vertex `gemini-3.1-flash-image` batches authorized. Whole game LANDSCAPE. Hard US$80/aim$60, useful30 per batch, one active/unknown in supplied project; once terminal submit next prepared useful batch BEFORE fetching previous. Old no-code/portrait/Flash-Lite/collect-before-next instructions below are HISTORICAL. Canonical complete spec: [FULL-IMPLEMENTATION-SPEC.md](FULL-IMPLEMENTATION-SPEC.md). Technical/asset/composite/game/native acceptance remain separate.

# Android installation and environment transfer

**Planning record: 2 October 2026. No native transfer, dependency install, sync, APK build or installation is part of this documentation-only deliverable.**

## Purpose and source boundaries

Canonical docs-only project: `C:/dev/ages-of-dominion-reborn`. Existing reference project: `C:/dev/ages-of-dominion`. Preserve the old project and its player saves. The unused new-code attempt was moved to `C:/dev/ages-of-dominion-reborn-unused-draft-2026-10-02`; it is not an adopted foundation. No remote repository or publication is required. All native work waits for owner section feedback and the coding instruction. Known installed paths/tools/settings are in `INSTALLED-ENVIRONMENT.md`; use that record rather than asking the owner to repeat it.

The owner authorizes a fresh implementation that carries installation settings and reviewed art. This allows safe Android shell/config/resource reuse; it does not call for copying old JavaScript gameplay, all build outputs, personal credentials, signing keys or app data.

## Verified existing settings

| Setting | Source | Existing value / fresh treatment |
|---|---|---|
| Release application ID | `capacitor.config.json`, `android/app/build.gradle` | `com.agesofdominion.game`; keep for release continuity |
| App display name | Capacitor config, `res/values/strings.xml` | Ages of Dominion |
| Native namespace / MainActivity | Gradle and `android/app/src/main/java/com/agesofdominion/game/MainActivity.java` | `com.agesofdominion.game`; BridgeActivity shell only, safe reference |
| Web output directory | `capacitor.config.json` | `dist`; future Vite output must match |
| Minimum Android SDK | `android/variables.gradle` |24 |
| Compile/target SDK | `android/variables.gradle` |36 /36 |
| Gradle wrapper | `android/gradle/wrapper/gradle-wrapper.properties` |8.11.1 distribution; wrapper can be transferred after inspection |
| Android Gradle plugin | `android/build.gradle` |8.7.2; evaluate compatibility with fresh chosen Capacitor/toolchain rather than upgrade blindly |
| AndroidX / JVM settings | `android/gradle.properties` |AndroidX enabled; JVM heap1536m; compileSDK36 suppression |
| Runtime network | Product/Capacitor config |Offline; mixed content false; no remote `server.url`, analytics, streaming or network data |
| Device permissions | Current main manifest |Zero ANY declared/granted device permissions, including normal INTERNET/VIBRATE; VIBRATE has explicit merger removal. Audit all uses-permission entries in merged and packaged manifests after dependencies. |
| Icons/splash/colors | `android/app/src/main/res/` |Reuse reviewed original brand resources; verify portrait/landscape scale and modern splash behavior |
| Existing version | `android/app/build.gradle` |versionCode1/versionName1.0; preserve as installation metadata; local preview can be independent. Store/version publishing is outside current scope. |
| Storage | Old project native Preferences/browser storage |Do not copy data. Fresh save namespace and schema; explicit legacy import can be specified later. |

Current main manifest contains a FileProvider and orientation/size lifecycle configuration on MainActivity. Its existence is not evidence that every provider is required by the fresh app. Reuse only components needed by selected local backup/export functionality. Preserve exported activity/provider attributes correctly; no exported provider or permission broadening.

## Safe transfer allowlist and exclusions

| Candidate | Transfer policy | Required check |
|---|---|---|
| `android/gradlew`, `gradlew.bat`, `gradle/wrapper/*` |Reviewed Gradle wrapper only |Known paths/hash and distribution configuration |
| `android/variables.gradle`, `gradle.properties` |Settings may be reauthored/transferred |SDK/JDK/dependency compatibility; no personal paths/secrets |
| `android/settings.gradle`, root/app Gradle |Use as configuration reference; preferably generate fresh Capacitor shell and reconcile settings |Remove obsolete projects, old generated web asset links, optional Google-services setup and unused dependencies |
| MainActivity |Minimal BridgeActivity wrapper can be reused |No old gameplay/native business logic embedded |
| `res/mipmap-*`, drawable splash, values colors/styles/strings, required XML resources |Copy reviewed branding/native resources |No stale unrelated branding or placeholder resources; validate installed appearance |
| `capacitor.config.json` |Author a fresh config using reviewed ID/name/webDir/background/offline values |No old server URL or plugin options without installed plugins |
| npm package versions/lock |Toolchain reference only; create fresh dependencies and compatible lock |No unnecessary old runtime package carry-over; avoid symlinked node_modules |
| `local.properties` |Never copy machine path blindly |Regenerate from locally installed SDK only |
| `key.properties`, keystore/JKS, `google-services.json`, tokens, `.env` |Exclude |Fresh tree secret audit; release signing requires separate credential handling |
| `build/`, `.gradle/`, `dist/`, node_modules, generated Capacitor plugin projects |Exclude old generated/cached output |Generate from new project; no old bundle packaged accidentally |
| Old native/browser app data, backups, Preferences DB |Exclude |New namespace, no automatic old-save reset/migration |
| Old `client/`, `src/`, `core/`, executable scripts and conflicting handoffs |Exclude from new application source |No imports/symlinks pointing back to the old game |

No source or native files were copied into the documentation package as an installation claim. The package’s art/reference records specify any reviewed media copies separately.

## Coexistence and app identity

Release ID is permanent, but installing a build with the same application ID would replace the old installed app. A new save namespace does **not** make same-ID apps coexist. The next AI must use a debug/preview `applicationIdSuffix` such as `.reborn.preview` (full preview ID `com.agesofdominion.game.reborn.preview`) with clear preview labeling while retaining the release ID. Keep native namespace consistent; provider authorities use the actual `${applicationId}`. Audit final debug application ID before any device install. Do not install over the old app during visual calibration.

The future installer produces an isolated offline local-test preview APK. Cloud/account, Play Store/upload, release publication and release branding are outside the current game-build scope. The permanent ID and reviewed native settings remain recorded for continuity. Native orientation should support portrait kingdom and landscape/adaptive adventure/combat. If orientation control requires a plugin, list that dependency and its merged-manifest consequences; do not add device permissions for a UI preference.

## Future setup and verification sequence

1. After the owner preview-feedback/coding gate, use the existing docs-only new project and local `codex/rebuild` repository. Preserve its plan and references; no remote/commit/push is required automatically.
2. Choose the existing compatible JavaScript ES module +Vite +Vitest +Capacitor stack. Record exact installed versions. Developer-tool downloads are distinct from the game's zero-network runtime rule.
3. Install fresh dependencies and lock them. Add only the native adapters needed for durable local storage, lifecycle, local import/export and sound. No cloud/analytics/network runtime packages.
4. Generate a fresh Android shell and reconcile allowlisted SDK/name/ID/brand settings. Exclude secrets and old generated files. Add isolated debug identity.
5. Build the fresh web app, run unit/integration tests, sync Android, then compile the preview APK with the compatible locally installed JDK/SDK.
6. Read the merged debug manifest and packaged APK, checking actual application ID, SDK levels, zero ANY declared/granted device permissions (normal and dangerous; no uses-permission entries), local web assets and absence of network endpoints/old bundle. Save logs, hashes and a transfer ledger.
7. Only when device installation is intended, preserve the old app and install the distinct preview ID. Verify target viewport/DPR/insets/gestureback/orientation/lifecycle, real local save/export/recovery and an airplane-mode shared gameplay loop.
8. Report web build, Android sync, APK compilation and physical-device acceptance separately. A successful sync is not an APK and an APK is not device verification.

## Transfer ledger required from the builder

For every transferred native/media file record: source path, destination path, type (`branding`, `wrapper`, `setting`, `art`), source hash, destination hash, reason, changed fields and validation. Declare excluded secret/cache/app-data paths. For independently reauthored configuration, name the old settings used as reference without claiming byte-for-byte transfer. The archived draft remains unverified and is not evidence of a completed fresh build.

Optional haptics may work only on a verified platform path requiring no device permission. Android VIBRATE removal prevents promising native vibration; otherwise disable haptics with an availability reason. Never add a permission to make the setting work.

