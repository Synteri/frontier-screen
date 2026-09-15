#Requires -Version 5.1
# One-command pipeline run (Windows). Phases execute in order; each phase
# verifies its inputs before running.
$ErrorActionPreference = "Stop"

function Invoke-Step($name, $cmd) {
    Write-Host "`n== $name ==" -ForegroundColor Cyan
    Invoke-Expression $cmd
    if ($LASTEXITCODE -ne 0) { throw "$name failed with exit code $LASTEXITCODE" }
}

Invoke-Step "smoke test" "python scripts/00_smoke_test.py"
# Phase 2+ steps append here as scripts/01_*.py, 02_*.py, ...

Write-Host "`nPipeline complete. Commit results/ back to the repo." -ForegroundColor Green
