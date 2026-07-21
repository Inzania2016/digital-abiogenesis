[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$venvPath = Join-Path $repoRoot ".venv"
$venvPython = Join-Path $venvPath "Scripts\python.exe"

function Invoke-Checked {
    param(
        [Parameter(Mandatory)]
        [scriptblock]$Command,

        [Parameter(Mandatory)]
        [string]$FailureMessage
    )

    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw "$FailureMessage (exit code $LASTEXITCODE)."
    }
}

if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
    throw "Python Launcher 'py' was not found. Install Python 3.13 with the Windows launcher."
}

Invoke-Checked -FailureMessage "Python 3.13 is unavailable through 'py -3.13'" -Command {
    & py -3.13 -c "import sys; raise SystemExit(0 if sys.version_info[:2] == (3, 13) else 1)"
}

if (-not (Test-Path -LiteralPath $venvPython -PathType Leaf)) {
    Write-Host "Creating Python 3.13 virtual environment at $venvPath"
    Invoke-Checked -FailureMessage "Failed to create the Python 3.13 virtual environment" -Command {
        & py -3.13 -m venv $venvPath
    }
}

Invoke-Checked -FailureMessage "The existing .venv is not using Python 3.13" -Command {
    & $venvPython -c "import sys; raise SystemExit(0 if sys.version_info[:2] == (3, 13) else 1)"
}

Invoke-Checked -FailureMessage "Failed to upgrade packaging tools" -Command {
    & $venvPython -m pip install --upgrade pip setuptools wheel
}

Push-Location $repoRoot
try {
    Invoke-Checked -FailureMessage "Failed to install development and renderer dependencies" -Command {
        & $venvPython -m pip install --editable ".[dev,render]"
    }
}
finally {
    Pop-Location
}

Write-Host "Bootstrap complete: $(& $venvPython --version)"
