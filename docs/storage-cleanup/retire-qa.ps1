param([switch]$Execute)
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path.TrimEnd('\')
$qaRoot = [IO.Path]::GetFullPath((Join-Path $root 'qa')).TrimEnd('\')
$backupRoots = @(
  'C:\dev\ages-of-dominion-reborn-cleanup-backup-2026-10-04\qa-retired',
  'E:\Ages-of-Dominion-Reborn-Migration-2026-10-04\qa-retired'
)
$planPath = Join-Path $PSScriptRoot 'qa-retirement-plan-2026-10-04.json'
$journalPath = Join-Path $PSScriptRoot 'qa-retirement-journal-2026-10-04.jsonl'
$mediaExtensions = @('.png','.jpg','.jpeg','.webp','.gif','.bmp','.ico','.avif','.mp4','.webm','.zip','.apk','.pdf','.wav','.mp3')
function Get-Sha([string]$Path) { (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant() }
function Get-CheckedTarget([string]$Relative) {
  $target = [IO.Path]::GetFullPath((Join-Path $root $Relative))
  if (-not $target.StartsWith($qaRoot + '\', [StringComparison]::OrdinalIgnoreCase)) { throw "Outside QA: $Relative" }
  if ((Get-Item -LiteralPath $target -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "Reparse target: $Relative" }
  $parent = [IO.DirectoryInfo]::new([IO.Path]::GetDirectoryName($target))
  while ($parent.FullName.StartsWith($qaRoot, [StringComparison]::OrdinalIgnoreCase)) {
    if ($parent.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "Reparse parent: $Relative" }
    $parent = $parent.Parent
  }
  $target
}
if (-not $Execute) {
  # Referenced images stay at their original paths. APKs are superseded binaries;
  # compact historical records are kept with an explicit archive/restore index.
  $tracked = @(git -C $root ls-files -- 'qa')
  if ($LASTEXITCODE -ne 0) { throw 'Git inventory failed' }
  $trackedMedia = @($tracked | Where-Object { $mediaExtensions -contains [IO.Path]::GetExtension($_).ToLowerInvariant() })
  $references = [System.Collections.Generic.List[string]]::new()
  foreach ($dir in @('docs','src','scripts','tests','qa')) {
    Get-ChildItem -LiteralPath (Join-Path $root $dir) -Recurse -File | Where-Object {
      $_.Extension -in @('.md','.txt','.json','.mjs','.js','.py','.ps1','.html','.css') -and $_.Length -lt 8000000 -and
      $_.FullName -notlike '*\storage-cleanup\*' -and $_.FullName -notlike '*\migration\*'
    } | ForEach-Object {
      $references.Add(([IO.File]::ReadAllText($_.FullName)).Replace('\','/'))
    }
  }
  foreach ($file in Get-ChildItem -LiteralPath $root -File -Filter '*.md') { $references.Add([IO.File]::ReadAllText($file.FullName).Replace('\','/')) }
  $rows = @(Get-ChildItem -LiteralPath $qaRoot -Recurse -File | Where-Object {
    $mediaExtensions -contains $_.Extension.ToLowerInvariant()
  } | ForEach-Object {
    $rel = $_.FullName.Substring($root.Length+1).Replace('\','/')
    $suffix = $rel.Substring(3)
    $referenced = $false
    foreach ($text in $references) {
      if ($text.Contains($rel) -or $text.Contains($suffix)) { $referenced=$true; break }
    }
    [pscustomobject]@{Path=$rel;Bytes=[long]$_.Length;SHA256=(Get-Sha $_.FullName);Tracked=($trackedMedia -contains $rel);Referenced=$referenced;Action='KEEP';Reason='Current or unique evidence'}
  })
  # Fixed reviewed hashes: excludes future/current packages and newly produced QA.
  $oldApkHashes = @('27d2791ac2778510706b0d9488b5621924183ce04ceedc2899e939787fda3bf4','04c662556e21f3ca6f25752c8f44427756481d59fc5e05949409bc118594de1a','6eec617b3513f3b0bd687cd5acf21e78ed77526ba1ce36946420e666ad4f3e0a','90d0687844321ef1e0964da884e4e3906b0e7d5d465a94a1c5598da9db46ce75','fbe989b58240bcd7981b993efb6ed4accb894fbf4ae42c73731a2e92efe830db','789c85d777dfe6ff93aa46f1ff1739cd3411e8fd123c9ade5c919e147c46e465')
  foreach ($row in $rows) {
    if ($row.Path.EndsWith('.apk') -and $oldApkHashes -contains $row.SHA256) { $row.Action='RETIRE'; $row.Reason='Superseded APK; two verified archive copies retained' }
  }
  foreach ($group in $rows | Where-Object { -not $_.Path.EndsWith('.apk') } | Group-Object SHA256) {
    if ($group.Count -le 1) { continue }
    $ordered = @($group.Group | Sort-Object @{Expression='Referenced';Descending=$true},Path)
    foreach ($row in $ordered | Select-Object -Skip 1) {
      # Local fixture/ledger filenames and glob references can be relative.
      # Retain these paths; excluding all capture media from Git removes their
      # future Git cost without breaking historical reports or helper inputs.
      $row.Reason="Exact duplicate of $($ordered[0].Path); retained for relative fixture/report references"
    }
  }
  [pscustomobject]@{CreatedUtc=[DateTime]::UtcNow.ToString('o');Repository=$root;BackupRoots=$backupRoots;Rows=$rows;UntrackPaths=$trackedMedia} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $planPath -Encoding utf8
  [pscustomobject]@{MediaFiles=$rows.Count;RetireFiles=@($rows | Where-Object Action -eq 'RETIRE').Count;RetireBytes=($rows | Where-Object Action -eq 'RETIRE' | Measure-Object Bytes -Sum).Sum;UntrackFiles=$trackedMedia.Count;UntrackBytes=($rows | Where-Object Tracked | Measure-Object Bytes -Sum).Sum} | ConvertTo-Json
  exit
}
$plan = Get-Content -LiteralPath $planPath -Raw | ConvertFrom-Json
if ($plan.Repository -ne $root) { throw 'Wrong repository in plan' }
$selected = @($plan.Rows | Where-Object { $_.Action -eq 'RETIRE' -or $_.Tracked })
# First verify the whole bounded set, then make two independently checked copies.
foreach ($row in $selected) {
  $target = Get-CheckedTarget $row.Path
  if ((Get-Item -LiteralPath $target).Length -ne $row.Bytes -or (Get-Sha $target) -ne $row.SHA256) { throw "Changed since plan: $($row.Path)" }
}
foreach ($backup in $backupRoots) {
  $objects = Join-Path $backup 'objects'
  New-Item -ItemType Directory -Path $objects -Force | Out-Null
  foreach ($row in $selected | Sort-Object SHA256 -Unique) {
    $destination = Join-Path $objects $row.SHA256
    if (-not (Test-Path -LiteralPath $destination)) { Copy-Item -LiteralPath (Get-CheckedTarget $row.Path) -Destination $destination }
    if ((Get-Item -LiteralPath $destination).Length -ne $row.Bytes -or (Get-Sha $destination) -ne $row.SHA256) { throw "Backup mismatch: $destination" }
  }
  Copy-Item -LiteralPath $planPath -Destination (Join-Path $backup 'index.json') -Force
}
foreach ($row in $selected | Where-Object Action -eq 'RETIRE') {
  $target = Get-CheckedTarget $row.Path
  if ((Get-Sha $target) -ne $row.SHA256) { throw "Concurrent change: $target" }
  foreach ($backup in $backupRoots) {
    if ((Get-Sha (Join-Path (Join-Path $backup 'objects') $row.SHA256)) -ne $row.SHA256) { throw 'Backup no longer matches' }
  }
  Remove-Item -LiteralPath $target -Force
  [pscustomobject]@{Utc=[DateTime]::UtcNow.ToString('o');Path=$row.Path;Bytes=$row.Bytes;SHA256=$row.SHA256;Reason=$row.Reason;Deleted=(-not (Test-Path -LiteralPath $target))} | ConvertTo-Json -Compress | Add-Content -LiteralPath $journalPath -Encoding utf8
}
# Exact literal paths only; retained media stays local, reports/helper code stays indexed.
foreach ($relative in $plan.UntrackPaths) {
  if (-not $relative.StartsWith('qa/') -or $mediaExtensions -notcontains [IO.Path]::GetExtension($relative).ToLowerInvariant()) { throw 'Unsafe untrack entry' }
  git -C $root --literal-pathspecs rm --cached --ignore-unmatch -- $relative | Out-Null
  if ($LASTEXITCODE -ne 0) { throw "Untrack failed: $relative" }
}
$missing = @($plan.Rows | Where-Object Action -eq 'RETIRE' | Where-Object { -not (Test-Path -LiteralPath (Join-Path $root $_.Path)) })
[pscustomobject]@{CompletedUtc=[DateTime]::UtcNow.ToString('o');RemovedFiles=$missing.Count;RemovedBytes=($missing | Measure-Object Bytes -Sum).Sum;UntrackedFiles=$plan.UntrackPaths.Count;BackupRoots=$backupRoots;ZipCreated=$false;CommitOrPush=$false} | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'qa-retirement-result-2026-10-04.json') -Encoding utf8
Get-Content -LiteralPath (Join-Path $PSScriptRoot 'qa-retirement-result-2026-10-04.json')
