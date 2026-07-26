[CmdletBinding()]
param(
    [ValidateSet("Benchmark", "Legacy", "Smoke")]
    [string]$Mode = "Benchmark",
    [string]$Scenario = "stable-default-v1",
    [string]$Suite = "b0-quick-v1",
    [string]$OutputRoot = "runs",
    [string]$RunId,
    [switch]$KeepPolicies,
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

Push-Location $repoRoot
try {
    if ($Mode -eq "Legacy") {
        if ($Seeds -lt 1 -or $TrainEpisodes -lt 1 -or $EvalEpisodes -lt 1 -or $GridSize -lt 2) {
            throw "Seeds and episode counts must be positive; GridSize must be at least 2."
        }
        Write-Host "Legacy Phase 3D multi-seed comparison; no contract artifacts are written."
        & $venvPython -m abiogenesis.training.evaluate_q_learning `
            --seed $Seed `
            --seeds $Seeds `
            --train-episodes $TrainEpisodes `
            --eval-episodes $EvalEpisodes `
            --grid-size $GridSize `
            --multi-seed
    }
    else {
        $runnerArguments = @(
            "-m",
            "abiogenesis.benchmark.runner",
            "--scenario",
            $Scenario,
            "--suite",
            $Suite,
            "--output-root",
            $OutputRoot
        )
        if ($Mode -eq "Smoke") {
            $runnerArguments += "--test-smoke"
            Write-Host "Noncanonical R1B smoke run; output cannot be benchmark evidence."
        }
        else {
            Write-Host "Bacterium-0 contract-v1 benchmark run."
        }
        if ($RunId) {
            $runnerArguments += @("--run-id", $RunId)
        }
        if ($KeepPolicies) {
            $runnerArguments += "--keep-policies"
        }
        & $venvPython @runnerArguments
    }
    if ($LASTEXITCODE -ne 0) {
        throw "Benchmark mode $Mode failed with exit code $LASTEXITCODE."
    }
}
finally {
    Pop-Location
}
