[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$venvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $venvPython -PathType Leaf)) {
    throw "Missing .venv Python. Run .\scripts\bootstrap.ps1 first."
}

Push-Location $repoRoot
try {
    & (Join-Path $PSScriptRoot "test.ps1")
    if ($LASTEXITCODE -ne 0) {
        throw "Test gate failed with exit code $LASTEXITCODE."
    }

    & $venvPython -m ruff check .
    if ($LASTEXITCODE -ne 0) {
        throw "Ruff lint failed with exit code $LASTEXITCODE."
    }

    & $venvPython -m ruff format --check .
    if ($LASTEXITCODE -ne 0) {
        throw "Ruff formatting check failed with exit code $LASTEXITCODE."
    }
}
finally {
    Pop-Location
}

Write-Host "Quality gate complete: pytest, Ruff lint, and Ruff format check passed."
