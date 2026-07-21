[CmdletBinding()]
param(
    [int]$Seed = 21,
    [int]$Seeds = 3,
    [int]$TrainEpisodes = 200,
    [int]$EvalEpisodes = 20,
    [int]$GridSize = 10
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$venvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $venvPython -PathType Leaf)) {
    throw "Missing .venv Python. Run .\scripts\bootstrap.ps1 first."
}
if ($Seeds -lt 1 -or $TrainEpisodes -lt 1 -or $EvalEpisodes -lt 1 -or $GridSize -lt 2) {
    throw "Seeds and episode counts must be positive; GridSize must be at least 2."
}

Write-Host "R0 benchmark wrapper: generic multi-seed comparison. R1 will replace this with named scenarios."

Push-Location $repoRoot
try {
    & $venvPython -m abiogenesis.training.evaluate_q_learning `
        --seed $Seed `
        --seeds $Seeds `
        --train-episodes $TrainEpisodes `
        --eval-episodes $EvalEpisodes `
        --grid-size $GridSize `
        --multi-seed
    if ($LASTEXITCODE -ne 0) {
        throw "Benchmark failed with exit code $LASTEXITCODE."
    }
}
finally {
    Pop-Location
}
