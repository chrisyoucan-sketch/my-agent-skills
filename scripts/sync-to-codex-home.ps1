param(
    [string]$SourceRoot = (Join-Path $PSScriptRoot "..\\skills"),
    [string]$TargetRoot = (Join-Path $HOME ".codex\\skills")
)

$sourceRoot = [System.IO.Path]::GetFullPath($SourceRoot)
$targetRoot = [System.IO.Path]::GetFullPath($TargetRoot)

if (-not (Test-Path -LiteralPath $sourceRoot)) {
    throw "Source skills directory not found: $sourceRoot"
}

New-Item -ItemType Directory -Force -Path $targetRoot | Out-Null

$skillDirs = Get-ChildItem -LiteralPath $sourceRoot -Directory -Force | Sort-Object Name

foreach ($skillDir in $skillDirs) {
    $destination = Join-Path $targetRoot $skillDir.Name

    if (Test-Path -LiteralPath $destination) {
        Remove-Item -LiteralPath $destination -Recurse -Force
    }

    Copy-Item -LiteralPath $skillDir.FullName -Destination $destination -Recurse -Force
    Write-Host "Synced $($skillDir.Name)"
}

Write-Host ""
Write-Host "Synced $($skillDirs.Count) tracked skill directories into $targetRoot"
Write-Host "Restart Codex to pick up updated skills."
