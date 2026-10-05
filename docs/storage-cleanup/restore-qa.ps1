param(
  [Parameter(Mandatory=$true)][string]$RelativePath,
  [string]$BackupRoot = 'E:\Ages-of-Dominion-Reborn-Migration-2026-10-04\qa-retired'
)
$ErrorActionPreference = 'Stop'
$repository = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path.TrimEnd('\')
$index = Get-Content -LiteralPath (Join-Path $BackupRoot 'index.json') -Raw | ConvertFrom-Json
$row = @($index.Rows | Where-Object Path -eq $RelativePath)
if ($row.Count -ne 1) { throw 'Select one exact Path from the archive index' }
$target = [IO.Path]::GetFullPath((Join-Path $repository $RelativePath))
if (-not $target.StartsWith((Join-Path $repository 'qa') + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Target must remain inside QA' }
$source = Join-Path (Join-Path $BackupRoot 'objects') $row[0].SHA256
if ((Get-Item -LiteralPath $source).Length -ne $row[0].Bytes -or (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash.ToLowerInvariant() -ne $row[0].SHA256) { throw 'Archive verification failed' }
if (Test-Path -LiteralPath $target) { throw 'Target already exists; no overwrite performed' }
$parent = [IO.DirectoryInfo]::new([IO.Path]::GetDirectoryName($target))
while ($parent.FullName.StartsWith($repository, [StringComparison]::OrdinalIgnoreCase)) {
  if ($parent.Exists -and ($parent.Attributes -band [IO.FileAttributes]::ReparsePoint)) { throw 'Reparse parent rejected' }
  $parent = $parent.Parent
}
New-Item -ItemType Directory -Path ([IO.Path]::GetDirectoryName($target)) -Force | Out-Null
Copy-Item -LiteralPath $source -Destination $target
if ((Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash.ToLowerInvariant() -ne $row[0].SHA256) { throw 'Restored hash mismatch' }
Write-Output "Restored: $RelativePath"
