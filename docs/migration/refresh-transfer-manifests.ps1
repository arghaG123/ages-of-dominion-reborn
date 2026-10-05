param([string]$RepositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path)
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path $RepositoryRoot).Path.TrimEnd('\')
$migration = Join-Path $root 'docs/migration'
$exclude = @(
  '\.git\', '\node_modules\', '\dist\', '\android\.gradle\',
  '\android\app\build\', '\android\build\', '\android\app\src\main\assets\',
  '\__pycache__\', '\\.pytest_cache\', '\\.mypy_cache\'
)
$secretNames = @('local.properties','key.properties','google-services.json')
$tracked = @(git -C $root ls-files)
$trackedSet = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
foreach ($p in $tracked) { [void]$trackedSet.Add($p) }
$rows = foreach ($file in Get-ChildItem -LiteralPath $root -Recurse -File -Force) {
  $full = $file.FullName
  if ($full.StartsWith($migration, [StringComparison]::OrdinalIgnoreCase)) { continue }
  if ($exclude | Where-Object { $full.Contains($_) }) { continue }
  if ($secretNames -contains $file.Name -or $file.Name -like '.env*' -or $file.Extension -in @('.jks','.keystore','.pyc')) { continue }
  if ($file.Name -in @('Thumbs.db','.DS_Store') -or $file.Name -match '\.sw[px]$') { continue }
  $relative = $full.Substring($root.Length + 1).Replace('\','/')
  $hash = (Get-FileHash -LiteralPath $full -Algorithm SHA256).Hash.ToLowerInvariant()
  [pscustomobject]@{Path=$relative;Bytes=[long]$file.Length;SHA256=$hash;GitTracked=$trackedSet.Contains($relative)}
}
$rows | Sort-Object Path | Export-Csv -LiteralPath (Join-Path $migration 'TRANSFER-INCLUDE-2026-10-04.csv') -NoTypeInformation -Encoding utf8
$include = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
foreach ($p in $tracked) {
  if ($p -like 'assets/*' -or $p -match '(^|/)__pycache__/|\.py[cod]$' -or $p -like 'design-preview/generated/*/provider-output/*' -or $p -match '^qa/.*\.(png|jpe?g|webp|gif|bmp|ico|avif|mp4|webm|zip|apk|pdf|wav|mp3)$') { continue }
  if (Test-Path -LiteralPath (Join-Path $root $p)) { [void]$include.Add($p) }
}
$explicit = @('AGENTS.md','README.md','START-HERE.md','CURRENT-STATUS.md','DECISIONS.md','RESUME-HERE.md','NEXT-CHAT-MAP-PLACEMENT.md','index.html','package.json','package-lock.json')
foreach ($p in $explicit) { if (Test-Path (Join-Path $root $p)) { [void]$include.Add($p) } }
foreach ($dir in @('docs','src','tests')) {
  Get-ChildItem -LiteralPath (Join-Path $root $dir) -Recurse -File -Force | ForEach-Object {
    $p=$_.FullName.Substring($root.Length+1).Replace('\','/')
    if ($p -notlike 'docs/migration/*.csv' -and $p -notmatch '(^|/)__pycache__/|\.py[cod]$') { [void]$include.Add($p) }
  }
}
# Owner: retained helper source belongs in Git, including audit/recovery tools.
$helperExtensions = @('.py','.mjs','.js','.cjs','.ps1','.sh','.cmd','.bat')
foreach ($dir in @('scripts','qa','scratch')) {
  $directory = Join-Path $root $dir
  if (-not (Test-Path -LiteralPath $directory)) { continue }
  Get-ChildItem -LiteralPath $directory -Recurse -File -Force | ForEach-Object {
    $p = $_.FullName.Substring($root.Length+1).Replace('\','/')
    if ($helperExtensions -contains $_.Extension.ToLowerInvariant() -and
        $p -notmatch '(^|/)(__pycache__|node_modules|\.git|\.pytest_cache|\.mypy_cache)/') {
      [void]$include.Add($p)
    }
  }
}
foreach ($p in @('scripts/build.mjs','scripts/serve.mjs','scripts/build-apk.mjs','scripts/dev-port.mjs','scripts/age-progression-matrix.mjs','android/app/build.gradle','android/app/src/main/AndroidManifest.xml','android/gradle/wrapper/gradle-wrapper.properties','android/gradlew','android/gradlew.bat','android/settings.gradle')) { if (Test-Path (Join-Path $root $p)) { [void]$include.Add($p) } }
$allow = foreach ($p in $include) {
  $full = Join-Path $root $p
  if (Test-Path -LiteralPath $full -PathType Leaf) {
    $f=Get-Item -LiteralPath $full
    $h=(Get-FileHash -LiteralPath $full -Algorithm SHA256).Hash.ToLowerInvariant()
    [pscustomobject]@{Path=$p;Bytes=[long]$f.Length;SHA256=$h;State=if($tracked -contains $p){'tracked'}else{'untracked-addition'}}
  }
}
$allow | Sort-Object Path | Export-Csv -LiteralPath (Join-Path $migration 'GIT-ALLOWLIST-2026-10-04.csv') -NoTypeInformation -Encoding utf8
"Transfer files: $(@($rows).Count); bytes: $(($rows | Measure-Object Bytes -Sum).Sum)"
"Git allowlist files: $(@($allow).Count); bytes: $(($allow | Measure-Object Bytes -Sum).Sum)"
$transferOnly = @($rows | Where-Object { -not $include.Contains($_.Path) })
$transferOnly | Sort-Object Path | Export-Csv -LiteralPath (Join-Path $migration 'NON-GIT-TRANSFER-2026-10-04.csv') -NoTypeInformation -Encoding utf8
$transferStats = @($transferOnly | Group-Object {
  if ($_.Path.StartsWith('assets/')) { 'Assets' }
  elseif ($_.Path.StartsWith('qa/')) { 'QA outside Git' }
  else { 'Other local data outside planned Git set' }
} | ForEach-Object {
  [pscustomobject]@{Group=$_.Name;Files=$_.Count;Bytes=[long](($_.Group | Measure-Object Bytes -Sum).Sum)}
})
$transferStats | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $migration 'NON-GIT-TRANSFER-SIZES-2026-10-04.json') -Encoding utf8
"Transfer-only files: $($transferOnly.Count); bytes: $(($transferOnly | Measure-Object Bytes -Sum).Sum)"
