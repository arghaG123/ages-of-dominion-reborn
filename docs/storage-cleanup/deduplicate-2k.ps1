param([string]$RepositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path)
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path -LiteralPath $RepositoryRoot).Path.TrimEnd('\')
$packRoot = (Resolve-Path -LiteralPath (Join-Path $root 'assets/high-res/later73-preparation-packs')).Path.TrimEnd('\') + '\'
$finalRoot = (Resolve-Path -LiteralPath (Join-Path $root 'assets/high-res/final-native2k')).Path.TrimEnd('\') + '\'
$plan = Import-Csv -LiteralPath (Join-Path $PSScriptRoot 'verified-duplicates-2026-10-04.csv')
$journal = Join-Path $PSScriptRoot 'deduplication-journal-2026-10-04.jsonl'
foreach ($row in $plan) {
    $duplicate = (Resolve-Path -LiteralPath $row.RemovePath).Path
    $retained = (Resolve-Path -LiteralPath $row.RetainedPath).Path
    if (!$duplicate.StartsWith($packRoot, [StringComparison]::OrdinalIgnoreCase) -or
        !$retained.StartsWith($finalRoot, [StringComparison]::OrdinalIgnoreCase) -or
        [IO.Path]::GetFileName($duplicate) -ne 'output.png') { throw 'Unexpected deduplication path' }
    foreach ($path in @($duplicate, $retained)) {
        if ((Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash -ne $row.SHA256 -or
            (Get-Item -LiteralPath $path).Length -ne [long]$row.Bytes) { throw "Changed file: $path" }
    }
    $temporaryLink = $duplicate + '.cleanup-hardlink'
    if (Test-Path -LiteralPath $temporaryLink) { throw "Temporary link exists: $temporaryLink" }
    New-Item -ItemType HardLink -Path $temporaryLink -Target $retained | Out-Null
    try {
        Remove-Item -LiteralPath $duplicate
        Move-Item -LiteralPath $temporaryLink -Destination $duplicate
    } catch {
        if (!(Test-Path -LiteralPath $duplicate)) { Copy-Item -LiteralPath $retained -Destination $duplicate }
        throw
    }
    if ((Get-FileHash -LiteralPath $duplicate -Algorithm SHA256).Hash -ne $row.SHA256) { throw 'Post-deduplication hash mismatch' }
    [ordered]@{Timestamp=[DateTime]::UtcNow.ToString('o');Action='REPLACE_EXACT_DUPLICATE_WITH_HARDLINK';Path=$duplicate;Retained=$retained;Bytes=[long]$row.Bytes;SHA256=$row.SHA256} |
        ConvertTo-Json -Compress | Add-Content -LiteralPath $journal -Encoding utf8
}
"Deduplicated $($plan.Count) files; unchanged paths, bytes and hashes."
