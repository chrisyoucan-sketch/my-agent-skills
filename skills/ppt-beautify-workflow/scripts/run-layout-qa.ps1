param(
    [Parameter(Mandatory = $true)]
    [string]$InputPath,

    [string]$Output,

    [string]$Report,

    [switch]$AutoFix
)

$ErrorActionPreference = "Stop"

$skillRoot = Split-Path -Parent $PSScriptRoot
$polisherRoot = Join-Path (Split-Path -Parent $skillRoot) "ppt-layout-polisher"
$validateScript = Join-Path $polisherRoot "scripts\validate_ppt_layout.py"
$autoFixScript = Join-Path $polisherRoot "scripts\auto_fix_ppt_layout.py"

if (-not (Test-Path -LiteralPath $InputPath)) {
    throw "Input PPTX not found: $InputPath"
}

if (-not (Test-Path -LiteralPath $validateScript)) {
    throw "Missing validator script: $validateScript"
}

$resolvedInput = (Resolve-Path -LiteralPath $InputPath).Path

if (-not $Report) {
    $baseName = [System.IO.Path]::GetFileNameWithoutExtension($resolvedInput)
    $reportName = "$baseName.layout-report.json"
    $Report = Join-Path (Split-Path -Parent $resolvedInput) $reportName
}

Write-Host "Running layout validation..."
python $validateScript $resolvedInput -o $Report

if ($LASTEXITCODE -ne 0) {
    throw "Layout validation failed."
}

Write-Host "Validation report: $Report"

if ($AutoFix) {
    if (-not (Test-Path -LiteralPath $autoFixScript)) {
        throw "Missing auto-fix script: $autoFixScript"
    }

    if (-not $Output) {
        $baseName = [System.IO.Path]::GetFileNameWithoutExtension($resolvedInput)
        $fixedName = "$baseName.fixed.pptx"
        $Output = Join-Path (Split-Path -Parent $resolvedInput) $fixedName
    }

    $fixReport = [System.IO.Path]::ChangeExtension($Report, ".fix-report.json")

    Write-Host "Running auto-fix..."
    python $autoFixScript $resolvedInput -o $Output --report $fixReport

    if ($LASTEXITCODE -ne 0) {
        throw "Auto-fix failed."
    }

    Write-Host "Fixed deck: $Output"
    Write-Host "Fix report: $fixReport"
}
