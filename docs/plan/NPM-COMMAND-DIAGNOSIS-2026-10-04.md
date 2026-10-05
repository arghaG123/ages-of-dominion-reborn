# Development and APK command diagnosis — 4 October 2026

Planner/verifier inspection only. No server started/stopped, game/package edits, dependency install, web/APK build, device action, provider query, Git/storage operation or executor dispatch occurred. Existing server received one local HTTP read for diagnosis (repeated once to expose structured output).

## Confirmed development cause

Owner supplied `Error: listen EADDRINUSE: address already in use 127.0.0.1:4173` from `npm run dev`. Current reborn `package.json` defines `dev` as `node scripts/serve.mjs`; server line 14 fixes the bind to loopback port 4173 and has no alternate-port handling. An existing Node listener (PID 27276 at inspection, a transient snapshot) runs `scripts/serve.mjs`. HTTP GET `/` returns 200 and content exactly matching reborn root `index.html`. The game server is already available at http://127.0.0.1:4173/. Use it, or stop its original terminal with Ctrl+C before restarting. No missing dependency, alias, Node-version or shell-policy failure explains the supplied dev error. Current Node v24.19.0 meets package >=24; both npm and npm.cmd version probes returned 11.17.0.

Previous read-only repository `C:/dev/ages-of-dominion` defines `dev` as `vite`, with configured default port 5173 and optional PORT. Reborn's server is a fixed-port static server, without Vite's port selection or hot module replacement. Setting PORT or passing --port does not change this current script.

Development command from PowerShell:

```powershell
Set-Location 'C:\dev\ages-of-dominion-reborn'
npm run dev
```

Direct equivalent: `node scripts/serve.mjs`. Open the printed address, keep its terminal running, and refresh after edits.

## Confirmed APK alias gap

Previous package defines `build:apk` and `apk` as `node scripts/build-apk.mjs`, which builds Vite, syncs Capacitor Android, and calls assembleDebug. Reborn defines neither alias, and has no scripts/build-apk.mjs. Read-only `npm.cmd run` confirms its available scripts are dev, test, build, benchmark and benchmark:render. `npm run build` means web dist only.

Reborn has a direct Android WebView wrapper, loading assets/www/index.html through WebViewAssetLoader. Gradle has no task linking freshly built dist into that assets directory. A current APK therefore requires web build, asset synchronization, then Gradle compilation.

Source/configuration-verified PowerShell sequence for an authorized executor; NOT RUN here. Robocopy /MIR mirrors dist into the generated www directory, removing stale generated entries there. Stop on failure before proceeding:

```powershell
Set-Location 'C:\dev\ages-of-dominion-reborn'
npm.cmd run build
if ($LASTEXITCODE -ne 0) { throw 'Web build failed' }
robocopy '.\dist' '.\android\app\src\main\assets\www' /MIR
if ($LASTEXITCODE -ge 8) { throw 'Android asset synchronization failed' }
Push-Location '.\android'
try {
    .\gradlew.bat assembleDebug
    if ($LASTEXITCODE -ne 0) { throw 'APK build failed' }
} finally {
    Pop-Location
}
```

Debug output: C:/dev/ages-of-dominion-reborn/android/app/build/outputs/apk/debug/app-debug.apk. With assembleRelease instead, current configuration outputs app-release-unsigned.apk in the release sibling directory. Existing debug/release APKs do not establish a newly successful build. Native/device acceptance remains unverified; device testing stays STOPPED.

Current JAVA_HOME and Android SDK environment variables point to the installed Microsoft JDK21 and C:/Users/pupan/AppData/Local/Android/Sdk; android/local.properties agrees. Configuration presence does not prove a future Gradle build passes. Older README/installed-environment statements that no game/package/APK exists are historical and contradicted by current local files.

To restore familiar one-command behavior, Code AI can independently implement a reborn build:apk wrapper that builds web assets, synchronizes generated Android assets and invokes Gradle with failure propagation, and make the dev server honor a selected port or handle occupied ports. This diagnosis does not implement or dispatch those changes. Full product, visual and owner acceptance remain incomplete.


## Command correction — 4 October 2026, Code executor

`npm run dev` is `node scripts/serve.mjs`. `--port` wins over `PORT`; the default is 4173. The process binds `127.0.0.1` only. If that port is taken it prints the selected port, says no other process was stopped, and exits 1. It does not move to the next port. `npm run build:apk` is `node scripts/build-apk.mjs`: preserve existing release and debug APK copies, build `dist`, copy only generated files into `android/app/src/main/assets/www`, then `gradlew.bat assembleRelease` through `cmd.exe` on Windows. A direct spawn of the `.bat` file returns `EINVAL` and does not compile. The unsigned output is `android/app/build/outputs/apk/release/app-release-unsigned.apk`. Packaging is not a device launch.

## Implemented correction — 4 October 2026

The report above records the state inspected before the correction. Vite 8.3.2 is now a local dev dependency, and package.json runs ite --host 127.0.0.1 --port 4173 for 
pm run dev. Vite's default port behavior advances to the next available port when 4173 is busy. Confirmed by starting 
pm run dev while the existing 4173 service was present: Vite announced 4174 and became ready; the temporary second server was then stopped. uild and uild:apk are unchanged; no APK build or device testing was performed.
