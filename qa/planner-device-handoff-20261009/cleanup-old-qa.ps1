# PowerShell 7; owner-authorized OLD QA only. Source/evidence/current namespaces retained.
$ErrorActionPreference = 'Stop'
$workspaceRoot = (Resolve-Path -LiteralPath 'C:/dev/ages-of-dominion-reborn').Path
$qaRoot = Join-Path $workspaceRoot 'qa'
$auditRoot = Join-Path $qaRoot 'planner-device-handoff-20261009'
$targets = @(
 'qa/environment-art-20261006/__pycache__',
 'qa/image-residual-executor-20261007/environment/helpers/__pycache__'
)
$tracked = @(git -C $workspaceRoot ls-files)
if ($LASTEXITCODE -ne 0) { throw 'Tracked set unavailable' }
$beforeDeletes = @(git -C $workspaceRoot diff --name-only --diff-filter=D)
$beforeFree = ([System.IO.DriveInfo]::new('C:/')).AvailableFreeSpace
$allowlist = @()
foreach ($relative in $targets) {
 $target = [System.IO.Path]::GetFullPath((Join-Path $workspaceRoot $relative))
 if (-not $target.StartsWith($qaRoot + [System.IO.Path]::DirectorySeparatorChar,[System.StringComparison]::OrdinalIgnoreCase)) { throw 'Escaped QA root' }
 if (-not (Test-Path -LiteralPath $target)) { continue }
 $resolved = (Resolve-Path -LiteralPath $target).Path
 if ($resolved -ne $target) { throw 'Unexpected resolved target' }
 $parents = @((Get-Item -LiteralPath $target))
 $current = (Get-Item -LiteralPath $target).Parent
 while ($current -and $current.FullName.StartsWith($workspaceRoot)) { $parents += $current; $current = $current.Parent }
 $items = @(Get-ChildItem -LiteralPath $target -Recurse -Force)
 if (@($parents + $items | Where-Object { $_.Attributes -band [System.IO.FileAttributes]::ReparsePoint }).Count) { throw 'Reparse point' }
 if (@($tracked | Where-Object { $_.StartsWith($relative + '/') }).Count) { throw 'Tracked files under cleanup target' }
 $files = @($items | Where-Object { -not $_.PSIsContainer })
 if (@($files | Where-Object { $_.Extension -ne '.pyc' }).Count) { throw 'Non-cache content' }
 $records = @()
 foreach ($file in $files) {
  $links = @(fsutil hardlink list $file.FullName)
  if ($LASTEXITCODE -ne 0 -or @($links | Where-Object { $_.Trim() }).Count -ne 1) { throw 'Hardlink count unavailable or shared' }
  $records += [pscustomobject]@{ Path=$file.FullName; Bytes=$file.Length; Sha256=(Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant(); Hardlinks=1 }
 }
 $allowlist += [pscustomobject]@{ Relative=$relative; Resolved=$resolved; Reason='Obsolete CPython bytecode; retained Python source recreates cache, no asset/provenance/visual evidence'; Files=$records; Bytes=($files | Measure-Object Length -Sum).Sum }
}
$allowlist | ConvertTo-Json -Depth 7 | Set-Content -LiteralPath (Join-Path $auditRoot 'cleanup-allowlist.json') -Encoding utf8
# All preflight checks precede the first mutation; PowerShell stays end-to-end.
foreach ($entry in $allowlist) { Remove-Item -LiteralPath $entry.Resolved -Recurse -Force }
$afterDeletes = @(git -C $workspaceRoot diff --name-only --diff-filter=D)
$newDeletes = @($afterDeletes | Where-Object { $_ -notin $beforeDeletes })
$afterFree = ([System.IO.DriveInfo]::new('C:/')).AvailableFreeSpace
$report = [pscustomobject]@{ Scope='OLD QA bytecode only'; Targets=$allowlist; ReclaimedLogicalBytes=($allowlist | Measure-Object Bytes -Sum).Sum; RemovedFiles=($allowlist | ForEach-Object { $_.Files.Count } | Measure-Object -Sum).Sum; RemainingTargets=@($allowlist | Where-Object { Test-Path -LiteralPath $_.Resolved } | ForEach-Object Relative); NewTrackedDeletions=$newDeletes; DriveFreeBefore=$beforeFree; DriveFreeAfter=$afterFree; DriveDeltaIsNotIsolated=$true; Preserved='All source, raw responses, receipts, current QA, historical guides, candidates, original art, browser profiles, APK and financial/control/history'; IncomingReferences='Only historical inventory/cache exclusion mentions; no source/runtime/test/producer dependency on CPython bytecode'; AllocatedReclaimedBytes='Not independently measured; logical bytes only' }
$report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $auditRoot 'cleanup-result.json') -Encoding utf8
if ($newDeletes.Count -or $report.RemainingTargets.Count) { throw 'Post-cleanup verification failed' }
$report | Select-Object ReclaimedLogicalBytes,RemovedFiles,NewTrackedDeletions
