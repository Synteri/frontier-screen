#Requires -Version 5.1
# Frontier Screen — one-command pipeline (Windows).
# Phase 2 order: pull -> clean -> screen(logic test).
#
# GATE: 03_screen.py runs the FULL approved-drug ranking ONLY with
# --i-have-reviewed-the-prereg (human sign-off on the target's preregistration file).
# This script runs 03 in test mode (--max-drugs 100) as a logic check.
# The full ranking run happens after the human reviews the pre-registration.
param([string]$Target = "CNR2")
$ErrorActionPreference = "Stop"

function Invoke-Step($name, $cmd) {
    Write-Host "`n== $name ==" -ForegroundColor Cyan
    Invoke-Expression $cmd
    if ($LASTEXITCODE -ne 0) { throw "$name failed with exit code $LASTEXITCODE" }
}

Invoke-Step "smoke test"        "python scripts/00_smoke_test.py"
Invoke-Step "01 pull data"      "python scripts/01_pull_data.py --target $Target"
Invoke-Step "02 clean data"     "python scripts/02_clean_data.py --target $Target"
Invoke-Step "03 screen (test)"  "python scripts/03_screen.py --target $Target --max-drugs 100"

Write-Host "`nPipeline logic verified on 100-drug subset." -ForegroundColor Green
$Prereg = "preregistration/$Target.md"
Write-Host "Full ranking run (after the human reviews $Prereg):" -ForegroundColor Yellow
Write-Host "  python scripts/03_screen.py --target $Target --i-have-reviewed-the-prereg" -ForegroundColor Yellow
Write-Host "Commit results/ back to the repo when done." -ForegroundColor Yellow
