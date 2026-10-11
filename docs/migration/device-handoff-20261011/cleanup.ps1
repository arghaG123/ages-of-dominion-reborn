$ErrorActionPreference = 'Stop'
$taskRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
$qaOut = Join-Path $taskRoot 'qa/planner-device-handoff-20261011'
function Checked-Path([string]$relative) {
    $candidate = [IO.Path]::GetFullPath((Join-Path $taskRoot $relative))
    if (-not $candidate.StartsWith($taskRoot + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) { throw "Outside root: $candidate" }
    if (Test-Path -LiteralPath $candidate) {
        $items = @(Get-Item -LiteralPath $candidate -Force)
        if ($items[0].PSIsContainer) { $items += @(Get-ChildItem -LiteralPath $candidate -Force -Recurse) }
        if ($items | Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint }) { throw "Reparse point: $candidate" }
    }
    return $candidate
}
if (Get-Process git*,java*,gradle* -ErrorAction SilentlyContinue) { throw 'A Git or native build process is active' }
$refsBefore = @(git -C $taskRoot show-ref)
$apkSource = Checked-Path 'android/app/build/outputs/apk/release/ages-of-dominion-reborn-preview-release-unsigned-20261011.apk'
$apkTarget = Checked-Path 'delivery/ages-of-dominion-reborn-preview-4fa30fa0.apk'
$expected = '4fa30fa016f3a8f7cb1751b7624ffbecd924182f51686d920af5b37096a8037c'
if (Test-Path -LiteralPath $apkSource) {
    if ((Get-FileHash -LiteralPath $apkSource -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expected) { throw 'Current APK changed' }
    if (Test-Path -LiteralPath $apkTarget) { throw 'APK destination already exists' }
    Move-Item -LiteralPath $apkSource -Destination $apkTarget
}
if ((Get-FileHash -LiteralPath $apkTarget -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expected) { throw 'APK move readback mismatch' }
$targets = @('dist', 'android/app/src/main/assets/www', 'android/app/build/intermediates', 'android/app/build/tmp', 'scripts/__pycache__', 'tests/__pycache__', 'qa/asset-audit-20261003/__pycache__', 'qa/planner-verifier-v3-20261003/__pycache__')
$garbage = @(Get-ChildItem -LiteralPath (Join-Path $taskRoot '.git/objects') -Filter 'tmp_obj_*' -Recurse -File)
foreach ($item in $garbage) {
    if ($item.LastWriteTimeUtc -gt [datetime]::UtcNow.AddDays(-2)) { throw 'Recent Git temporary file' }
    $targets += [IO.Path]::GetRelativePath($taskRoot, $item.FullName)
}
$deleted = @()
$preserved = @()
# Preflight the complete list before deletion. Preserve tracked historical caches.
$plan = @()
foreach ($relative in $targets) {
    $candidate = Checked-Path $relative
    if (-not (Test-Path -LiteralPath $candidate)) { continue }
    if (@(git -C $taskRoot ls-files -- $relative).Count -ne 0) { $preserved += $relative; continue }
    $item = Get-Item -LiteralPath $candidate -Force
    $files = if ($item.PSIsContainer) { @(Get-ChildItem -LiteralPath $candidate -Recurse -Force -File) } else { @($item) }
    $bytes = ($files | Measure-Object Length -Sum).Sum
    $plan += [pscustomobject]@{path=$relative; files=$files.Count; bytes=[long]$bytes; reason='Reproducible build/cache or abandoned unreferenced Git temporary output'}
}
$plan | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $qaOut 'cleanup-write-ahead.json') -Encoding utf8
foreach ($row in $plan) { Remove-Item -LiteralPath (Checked-Path $row.path) -Recurse -Force; $deleted += $row }
$refsAfter = @(git -C $taskRoot show-ref)
if (Compare-Object $refsBefore $refsAfter) { throw 'Git refs changed during cleanup' }
[pscustomobject]@{date='2026-10-11'; authorization='Owner clarified remove only verified unnecessary files'; firstPass='First invocation removed dist, generated www, Gradle intermediates/tmp and untracked scripts/tests caches; stopped on tracked legacy cache before report write. Preserved both tracked QA caches. Before/after category snapshots quantify total reduction.'; apkMove=[pscustomobject]@{source=[IO.Path]::GetRelativePath($taskRoot,$apkSource);target=[IO.Path]::GetRelativePath($taskRoot,$apkTarget);sha256=$expected;bytes=(Get-Item -LiteralPath $apkTarget).Length;copyMade=$false}; deletedThisPass=$deleted; preservedTrackedCaches=$preserved; deletedBytesThisPass=($deleted | Measure-Object bytes -Sum).Sum; refsUnchanged=$true; productionDeleted=$false} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $qaOut 'cleanup.json') -Encoding utf8
Get-Content -LiteralPath (Join-Path $qaOut 'cleanup.json')
