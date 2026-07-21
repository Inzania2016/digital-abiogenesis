[CmdletBinding()]
param(
    [switch]$Generated
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$repoPrefix = $repoRoot.TrimEnd([System.IO.Path]::DirectorySeparatorChar) + [System.IO.Path]::DirectorySeparatorChar
$cleanupFailures = [System.Collections.Generic.List[string]]::new()

function Remove-ProjectItem {
    param(
        [Parameter(Mandatory)]
        [string]$Path
    )

    $fullPath = [System.IO.Path]::GetFullPath($Path)
    if (-not $fullPath.StartsWith($repoPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to remove a path outside the repository: $fullPath"
    }
    if (Test-Path -LiteralPath $fullPath) {
        try {
            Remove-Item -LiteralPath $fullPath -Recurse -Force
            Write-Host "Removed $fullPath"
        }
        catch {
            $message = "Could not remove ${fullPath}: $($_.Exception.Message)"
            $cleanupFailures.Add($message)
            Write-Warning $message
        }
    }
}

foreach ($relativePath in @(".pytest_cache", ".pytest-tmp", ".ruff_cache", "build", "dist")) {
    Remove-ProjectItem -Path (Join-Path $repoRoot $relativePath)
}

$scanRoots = @("src", "tests", "tools", "scripts") |
    ForEach-Object { Join-Path $repoRoot $_ } |
    Where-Object { Test-Path -LiteralPath $_ -PathType Container }

$cacheDirectories = foreach ($scanRoot in $scanRoots) {
    Get-ChildItem -LiteralPath $scanRoot -Directory -Recurse -Force -ErrorAction Stop |
        Where-Object { $_.Name -eq "__pycache__" -or $_.Name -like "*.egg-info" }
}
$cacheDirectories |
    Sort-Object -Property FullName -Unique -Descending |
    ForEach-Object { Remove-ProjectItem -Path $_.FullName }

foreach ($scanRoot in $scanRoots) {
    Get-ChildItem -LiteralPath $scanRoot -File -Recurse -Force -Filter "*.pyc" -ErrorAction Stop |
        ForEach-Object { Remove-ProjectItem -Path $_.FullName }
}

if ($Generated) {
    foreach ($relativePath in @("runs", "artifacts", "outputs", "output")) {
        Remove-ProjectItem -Path (Join-Path $repoRoot $relativePath)
    }
    Write-Host "Generated run/artifact output was included. Local models were preserved."
}

Write-Host "Clean complete. The .venv and source assets were preserved."
if ($cleanupFailures.Count -gt 0) {
    throw "Clean was incomplete; $($cleanupFailures.Count) target(s) could not be removed."
}
