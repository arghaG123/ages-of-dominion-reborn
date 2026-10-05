$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path.TrimEnd('\')
$dest = 'E:\Ages-of-Dominion-Reborn-Migration-2026-10-04'
$zipPath = Join-Path $dest 'ages-of-dominion-reborn-worktree-2026-10-04-handoff-final6.zip'
if (-not (Test-Path -LiteralPath $dest)) { throw "Destination drive/folder unavailable: $dest" }
if (Test-Path -LiteralPath $zipPath) { throw "Refusing to overwrite existing archive: $zipPath" }
Add-Type -AssemblyName System.IO.Compression
$rows = @(Import-Csv -LiteralPath (Join-Path $PSScriptRoot 'TRANSFER-INCLUDE-2026-10-04.csv'))
$file = [IO.File]::Open($zipPath, [IO.FileMode]::CreateNew, [IO.FileAccess]::ReadWrite, [IO.FileShare]::None)
$archive = [IO.Compression.ZipArchive]::new($file, [IO.Compression.ZipArchiveMode]::Create, $false)
$buffer = [byte[]]::new(1048576)
try {
  foreach ($row in $rows) {
    $source = Join-Path $root ($row.Path -replace '/', '\')
    if (-not (Test-Path -LiteralPath $source -PathType Leaf)) { throw "Missing manifest path: $($row.Path)" }
    $accepted = $false
    for ($attempt=1; $attempt -le 3 -and -not $accepted; $attempt++) {
      $before=Get-Item -LiteralPath $source
      $entry = $archive.CreateEntry($row.Path, [IO.Compression.CompressionLevel]::NoCompression)
      $input = [IO.File]::OpenRead($source); $output = $entry.Open(); $sha = [Security.Cryptography.SHA256]::Create(); [long]$count=0
      try {
        while (($n = $input.Read($buffer, 0, $buffer.Length)) -gt 0) {
          [void]$sha.TransformBlock($buffer, 0, $n, $buffer, 0)
          $output.Write($buffer, 0, $n); $count += $n
        }
        [void]$sha.TransformFinalBlock([byte[]]::new(0), 0, 0)
        $actual=[Convert]::ToHexString($sha.Hash).ToLowerInvariant()
      } finally { $output.Dispose(); $input.Dispose(); $sha.Dispose() }
      $after=Get-Item -LiteralPath $source
      if ($before.Length -eq $after.Length -and $before.LastWriteTimeUtc -eq $after.LastWriteTimeUtc -and $count -eq $after.Length) {
        $row.Bytes=[string]$count; $row.SHA256=$actual; $accepted=$true
      } else {
        $entry.Delete()
        Start-Sleep -Milliseconds 500
      }
    }
    if (-not $accepted) { throw "File remained in motion during three capture attempts: $($row.Path)" }
  }
  $manifestPath=Join-Path $PSScriptRoot 'TRANSFER-INCLUDE-2026-10-04.csv'
  $rows | Sort-Object Path | Export-Csv -LiteralPath $manifestPath -NoTypeInformation -Encoding utf8
  Get-ChildItem -LiteralPath $PSScriptRoot -File -Force | Sort-Object Name | ForEach-Object {
    $relative = 'docs/migration/' + $_.Name
    if ($relative -eq 'docs/migration/TRANSFER-INCLUDE-2026-10-04.csv') { return }
    $entry = $archive.CreateEntry($relative, [IO.Compression.CompressionLevel]::NoCompression)
    $input = [IO.File]::OpenRead($_.FullName); $output = $entry.Open()
    try { $input.CopyTo($output, 1048576) } finally { $output.Dispose(); $input.Dispose() }
  }
  $entry=$archive.CreateEntry('docs/migration/TRANSFER-INCLUDE-2026-10-04.csv',[IO.Compression.CompressionLevel]::NoCompression)
  $output=$entry.Open();try{$csv=$rows|Sort-Object Path|ConvertTo-Csv -NoTypeInformation;$bytes=[Text.UTF8Encoding]::new($false).GetBytes(($csv -join "`r`n")+"`r`n");$output.Write($bytes,0,$bytes.Length)}finally{$output.Dispose()}
} catch {
  $archive.Dispose(); $file.Dispose()
  Remove-Item -LiteralPath $zipPath -Force -ErrorAction SilentlyContinue
  throw
}
$archive.Dispose(); $file.Dispose()
$item = Get-Item -LiteralPath $zipPath
"ZIP=$($item.FullName)"
"ManifestFiles=$($rows.Count)"
"ManifestBytes=$(($rows | Measure-Object {[long]$_.Bytes} -Sum).Sum)"
"ZIPBytes=$($item.Length)"
