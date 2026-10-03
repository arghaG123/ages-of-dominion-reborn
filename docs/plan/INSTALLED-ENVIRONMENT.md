> **LATEST OWNER CORRECTION — planner/verifier only, 3 October 2026:** This chat creates the specification, execution instructions, acceptance criteria and reports. Another AI must execute image batches, game code, builds, collection and regeneration. Do not resume execution or delegate it from this chat. This supersedes previous implementation/production execution authorization interpreted for this chat. Approved landscape appearance direction, full scope and budget constraints persist. Read the current report at `docs/PLANNER-VERIFIER-HANDOFF.md`; older execution status below is historical.

> **CURRENT OWNER AUTHORITY — 3 October 2026:** generated landscape mock direction approved despite synchronization defects; fresh implementation and useful Vertex `gemini-3.1-flash-image` batches authorized. Whole game LANDSCAPE. Hard US$80/aim$60, useful30 per batch, one active/unknown in supplied project; once terminal submit next prepared useful batch BEFORE fetching previous. Old no-code/portrait/Flash-Lite/collect-before-next instructions below are HISTORICAL. Canonical complete spec: [FULL-IMPLEMENTATION-SPEC.md](FULL-IMPLEMENTATION-SPEC.md). Technical/asset/composite/game/native acceptance remain separate.

> **Latest authority — 3 October 2026:** whole-game LANDSCAPE confirmed; original Vertex design mocks authorized, reuse optional for this scope. Read [the new plan](LANDSCAPE-ORIGINAL-MOCK-PLAN-2026-10-03.md). Older portrait/reuse/no-generation instructions are historical. Exactly30/single-active/unknown-job restrictions and feedback-before-coding persist. Thirty briefs are drafted; zero generated. Supplied project access awaits local account sign-in; remote operations remain UNKNOWN.

# Installed environment and safe tooling handoff

Verified 2 October 2026 using read-only local version/path probes and sanitized cloud metadata. This is a snapshot, not a permanent credential guarantee. The new project currently contains planning documents and a design preview only: it has no game package, installed application dependencies, compiled APK or implemented gameplay.

## Use what is already installed

| Tool | Verified version / location | Treatment for the next AI |
|---|---|---|
| System Node.js | 24.19.0; `C:/Program Files/nodejs/node.exe` | Already on PATH. Do not reinstall unnecessarily. |
| System npm | 11.17.0; `C:/Program Files/nodejs/npm.ps1` | Available; fresh game dependency installation is a later implementation step. |
| Git | 2.37.0.windows.1; `C:/Program Files/Git/cmd/git.exe` | New standalone repository is separate from the old game. |
| System Python | 3.13.15; `C:/Users/pupan/AppData/Local/Programs/Python/Python313/python.exe` | Available for inspection/document/image processing where permitted. |
| Java/JDK | Microsoft OpenJDK 21.0.12.1; `C:/Program Files/Microsoft/jdk-21.0.12.101-hotspot` | Existing `JAVA_HOME`; no new JDK needed for the reviewed native stack. |
| Android SDK | `C:/Users/pupan/AppData/Local/Android/Sdk` | `ANDROID_HOME` and `ANDROID_SDK_ROOT` both point here; platform android-36, build-tools 34.0.0/36.0.0, cmdline-tools/latest and platform-tools exist. |
| ADB | 1.0.41, package 37.0.1-15733141; WinGet Google.PlatformTools path on PATH | Installed. No device inventory, APK installation or hardware acceptance performed by this review. |
| Chrome | 153.0.8010.53; `C:/Program Files/Google/Chrome/Application/chrome.exe` | Installed although `chrome` is not on PATH. Design-only preview is distinct from a game browser test. |
| Google Cloud SDK | 585.0.0; `C:/Users/pupan/AppData/Local/Google/Cloud SDK/google-cloud-sdk/bin/gcloud.ps1` | Installed on PATH; `gsutil.cmd` is also present. |
| Android Studio | Not found in common install paths or checked Windows uninstall registry entries | Do not claim installed. Existing JDK/SDK/Gradle command-line tooling may suffice for eventual builds; Studio is not required to review this plan. |

The Codex workspace dependency provider returned bundle 26.909.11814. Its Node is also 24.19.0 at `C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe`; its Python is **3.12.14** at `C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`. System Python and bundled Python are different runtimes. Bundled Node packages live under `dependencies/node/node_modules`, and bundled Python packages under `dependencies/python`. Its bundled Git path is `dependencies/native/git/cmd/git.exe`; fallback pnpm is `dependencies/bin/fallback/pnpm.cmd`. Ask the provider again if these paths change.

Exact-path revalidation confirms bundled Playwright **1.62.1** and playwright-core **1.62.1** under `C:/Users/pupan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules`, with `playwright/index.mjs` available. The earlier broad search missed these packages and has been corrected. Use the bundled Node and explicit Playwright import with the installed Chrome executable for design-preview QA; no new dependency install is needed. A local ms-playwright browser cache was not found, so do not assume bundled Chromium is installed. The permitted Codex browser-control tool is another available option. Preview checks remain separate from game browser tests. No missing tool requires the owner to repeat the game requirements. The `modern-web-guidance` skill remains unavailable in the checked skill locations; explicit responsive/accessibility requirements are in the plan.

## Existing old-project dependencies are reference only

Read-only package inspection verified Vite 6.4.3, Vitest 2.1.9, Capacitor core/android/cli 7.6.9, app 7.1.2, filesystem 7.1.8, haptics 7.0.5, preferences 7.0.4 and share 7.0.4 under `C:/dev/ages-of-dominion/node_modules`. These packages are installed **in the old game**, not in this new root. Do not symlink/copy its node_modules or imply a new game build passed. Author a compatible fresh lock after owner feedback permits implementation.

Old reviewed native configuration uses Gradle wrapper 8.11.1, Android Gradle plugin 8.7.2, minSdk24 and compile/targetSdk36. `INSTALLATION-TRANSFER.md` defines the safe transfer allowlist, preview application ID, zero ANY device permissions and offline runtime rule. Existing package availability is not a native compatibility/build test. Cloud Save, account login and Play Store publishing are deferred outside current milestones.

## Vertex connection: actual state and unresolved billing

| Read-only probe | Result |
|---|---|
| Configured gcloud project | `project-1aeea929-1dae-45bb-bf5`; obtained from current gcloud configuration, not guessed from the bucket |
| Active credentials | One active CLI credential; access-token refresh succeeded. Only a boolean was reported; no token, account identity or credential file was copied. |
| Existing bucket | `gs://project-1aeea929-1dae-45bb-bf5-aod-batch`; old `scripts/artgen/batch_gen.mjs` DEFAULT_BUCKET provenance; bucket describe succeeded, location US-CENTRAL1 |
| Vertex global batch metadata | GET of the configured project's global batchPredictionJobs returned HTTP403 / PERMISSION_DENIED, reason **BILLING_DISABLED**, service aiplatform.googleapis.com |
| Active batch jobs | **UNKNOWN**, not zero: billing failure prevented metadata verification |
| CLI support | `gcloud ai batch-prediction-jobs` is not available in this installed SDK; use the documented authorized metadata endpoint with credentials kept only in memory rather than assuming that subcommand exists |

The API explanation states billing must be enabled for that project; if changed recently, propagation can take time. This review did not enable billing/APIs, modify IAM, switch projects, alter global gcloud configuration, upload requests, submit jobs or retrieve outputs. A valid CLI token and readable storage bucket do not prove Vertex generation is usable. Revalidate the intended project, billing and metadata access before any future generation. If a different already-authorized project is intended, record that consequential configuration decision instead of silently switching it. Never print access tokens or copy .env/service-account/signing files into this package.

The owner's latest batch contract is **exactly 30 image requests per batch, at most one active image batch across this project workflow, and no supplemental or progressive image calls while it is in flight**. Before any submission, inspect remote jobs and the shared submission ledger; if active state is unknown, fail closed and do not submit. Complete/failed/cancelled jobs must be reconciled before scheduling the next batch. Credential presence is time-sensitive; tokens expire and permissions/billing may change. Revalidation is not permission to submit a test generation call.

The current design preview uses existing images and needs no Vertex job. New image production remains a later controlled action governed by `ART-REUSE.md` and the updated exact-30 manifest; the first calibration images are members of that batch, not a separate two-request submission. Verify current official model/batch size constraints immediately before production; no model inference call was used to prove support in this planning task.

## Revalidation and reporting rules

Use existing tools first and record the exact interpreter path/version for any future action. Keep dependency install, web tests/build, Android sync, APK compilation and physical-device verification as separate statuses. Do not run them to imply progress while this task is planning/design only. The root `START-HERE.md`, `CURRENT-STATUS.md`, decision/progress ledger and `docs/SESSION-HANDOFF.md` preserve what has happened and what remains so the owner need not restate it.

Official Google model and batch documentation were independently rechecked on 2 October2026: stable gemini-3.1-flash-image supports batch inference; the batch documentation currently limits image outputs to default1K (2K/4K unsupported). These are documentation facts, not successful inference/API evidence. [Model documentation](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/3-1-flash-image), [batch documentation](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/batch-inference).

