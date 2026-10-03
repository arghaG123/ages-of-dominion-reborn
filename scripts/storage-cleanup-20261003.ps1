param([switch]$Apply)
$ErrorActionPreference = 'Stop'
$workspace = [IO.Path]::GetFullPath('C:/dev/ages-of-dominion-reborn')
$reportPath = Join-Path $workspace 'docs/plan/STORAGE-CLEANUP-REPORT-2026-10-03.json'
$report = Get-Content -Raw -LiteralPath $reportPath | ConvertFrom-Json
$external = @(
 'C:/dev/ages-of-dominion-reborn-cleanup-quarantine-20261003',
 'C:/dev/ages-of-dominion-reborn-unused-draft-2026-10-02',
 'C:/dev/ages-of-dominion-rebuild-handoff.zip',
 'C:/dev/ages-of-dominion-rebuild-handoff'
) | ForEach-Object { [IO.Path]::GetFullPath($_) }
$internal = @(
 'assets/production/production-01-20261003/provider-output/predictions.jsonl',
 'assets/production/production-02-20261003/provider-output/predictions.jsonl',
 'design-preview/generated/landscape-mocks-20261003-efcd7a7e/provider-output/predictions.jsonl',
 'scripts/__pycache__', 'dist', 'NEXT-CHAT-MAP-PLACEMENT.md', 'docs/plan/NEXT-AI-PROMPT.md'
) | ForEach-Object { [IO.Path]::GetFullPath((Join-Path $workspace $_)) }
$targets = @($external) + @($internal)
foreach ($target in $targets) {
 if ($target -eq $workspace) { throw 'Refuse root deletion' }
 if ($external -notcontains $target -and -not $target.StartsWith($workspace + [IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)) { throw "Out of scope: $target" }
 if (-not (Test-Path -LiteralPath $target)) { continue }
 $item = Get-Item -LiteralPath $target -Force
 if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "Refuse link: $target" }
 if ($item.PSIsContainer) {
  $links = @(Get-ChildItem -LiteralPath $target -Recurse -Force | Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint })
  if ($links.Count) { throw "Refuse nested links: $target" }
 }
}
foreach ($property in $report.protectedSHA256.PSObject.Properties) {
 if ([IO.Path]::GetExtension($property.Name).ToLowerInvariant() -notin @('.png','.jpg','.jpeg','.webp','.avif')) { continue }
 if (-not (Test-Path -LiteralPath $property.Name -PathType Leaf) -or (Get-FileHash -LiteralPath $property.Name -Algorithm SHA256).Hash -ne $property.Value) { throw "Protected image changed or missing: $($property.Name)" }
}
foreach ($entry in $report.compactProviderEvidence) {
 if (-not (Test-Path -LiteralPath $entry.metadataFile -PathType Leaf) -or (Get-FileHash -LiteralPath $entry.metadataFile -Algorithm SHA256).Hash -ne $entry.metadataSHA256) { throw "Compact metadata changed/missing: $($entry.metadataFile)" }
 if ((Test-Path -LiteralPath $entry.rawFile -PathType Leaf) -and (Get-FileHash -LiteralPath $entry.rawFile -Algorithm SHA256).Hash -ne $entry.rawSHA256) { throw "Raw output changed; repeat audit: $($entry.rawFile)" }
}
$inventory = @()
foreach ($target in $targets) {
 if (-not (Test-Path -LiteralPath $target)) { continue }
 $item = Get-Item -LiteralPath $target -Force
 $files = if ($item.PSIsContainer) { @(Get-ChildItem -LiteralPath $target -Recurse -File -Force) } else { @($item) }
 $inventory += [pscustomobject]@{path=$target;files=$files.Count;bytes=($files | Measure-Object Length -Sum).Sum}
}
$inventory | Select-Object path,files,@{n='MiB';e={[math]::Round($_.bytes/1MB,2)}} | Format-Table -AutoSize
if (-not $Apply) { Write-Output 'Preview only. Pass -Apply to delete the audited items.'; return }
$completed = @()
try {
 foreach ($entry in $inventory) {
  Remove-Item -LiteralPath $entry.path -Recurse -Force
  if (Test-Path -LiteralPath $entry.path) { throw "Incomplete removal: $($entry.path)" }
  $completed += $entry
  $report | Add-Member -NotePropertyName removed -NotePropertyValue $completed -Force
  $report | Add-Member -NotePropertyName status -NotePropertyValue 'APPLYING' -Force
  $report | ConvertTo-Json -Depth 30 | Set-Content -LiteralPath $reportPath -Encoding utf8
 }
 $report | Add-Member -NotePropertyName status -NotePropertyValue 'APPLIED' -Force
 $report | Add-Member -NotePropertyName grossRemovedBytes -NotePropertyValue (($completed | Measure-Object bytes -Sum).Sum) -Force
 $report | ConvertTo-Json -Depth 30 | Set-Content -LiteralPath $reportPath -Encoding utf8
 $oldLedgerPath = Join-Path $workspace 'docs/plan/CLEANUP-LEDGER.json'
 if (Test-Path -LiteralPath $oldLedgerPath) {
  $oldLedger = Get-Content -Raw -LiteralPath $oldLedgerPath | ConvertFrom-Json
  $oldLedger | Add-Member -NotePropertyName quarantineStatus -NotePropertyValue 'PERMANENTLY_REMOVED_OWNER_REQUEST_2026-10-03' -Force
  $oldLedger | ConvertTo-Json -Depth 30 | Set-Content -LiteralPath $oldLedgerPath -Encoding utf8
 }
 $notes = @(
  '# Storage cleanup - 3 October 2026',
  '',
  'The owner-requested deletion removed the four obsolete external items, redundant encoded provider output, build/cache files and two superseded continuation prompts.',
  '',
  'Original references, saved generated images, source/tests, current plans, usage/provenance metadata, budgets and locks remain. response-metadata.jsonl preserves request/response/usage fields and image SHA256 references; opaque continuation signatures retain length/hash only. These compact records are evidence, not replayable API payloads.',
  '',
  'The former quarantine is no longer recoverable. Historical archive/prompt links are not active recovery instructions. See STORAGE-CLEANUP-REPORT-2026-10-03.json for exact removals.'
 )
 $notes | Set-Content -LiteralPath (Join-Path $workspace 'docs/plan/CLEANUP-NOTES.md') -Encoding utf8
 $indexPath = Join-Path $workspace 'docs/plan/README.md'
 $index = Get-Content -Raw -LiteralPath $indexPath
 $index = $index -replace '10\. NEXT-AI-PROMPT\.md[^\r\n]*','10. ../PLANNER-VERIFIER-HANDOFF.md, FULL-IMPLEMENTATION-SPEC.md and FULL-ASSET-PURCHASE-PLAN.md for the current handoff.'
 $index = '> Storage cleanup: the former quarantine/draft/external handoff and superseded continuation prompts were removed at owner request. See CLEANUP-NOTES.md; older archive statements below are historical.' + [Environment]::NewLine + [Environment]::NewLine + $index
 $index | Set-Content -LiteralPath $indexPath -Encoding utf8
 Write-Output ('Deleted {0} targets; removed {1} MiB before small metadata/report overhead.' -f $completed.Count,[math]::Round($report.grossRemovedBytes/1MB,2))
}
catch {
 $report | Add-Member -NotePropertyName status -NotePropertyValue 'PARTIAL_OR_FAILED' -Force
 $report | Add-Member -NotePropertyName failure -NotePropertyValue $_.Exception.Message -Force
 $report | Add-Member -NotePropertyName removed -NotePropertyValue $completed -Force
 $report | ConvertTo-Json -Depth 30 | Set-Content -LiteralPath $reportPath -Encoding utf8
 throw
}

