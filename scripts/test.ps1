[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments)]
    [string[]]$PytestArguments
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$venvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"
$pytestTemp = Join-Path $repoRoot ".pytest-tmp"

if (-not (Test-Path -LiteralPath $venvPython -PathType Leaf)) {
    throw "Missing .venv Python. Run .\scripts\bootstrap.ps1 first."
}

Push-Location $repoRoot
try {
    & $venvPython -m pytest -p no:cacheprovider "--basetemp=$pytestTemp" @PytestArguments
    if ($LASTEXITCODE -ne 0) {
        throw "pytest failed with exit code $LASTEXITCODE."
    }
}
finally {
    Pop-Location
}
