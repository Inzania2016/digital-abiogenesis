[CmdletBinding()]
param(
    [string]$OutputPath = "dist\digital-abiogenesis-source.zip"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Add-Type -AssemblyName System.IO.Compression

$repoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
if (-not [System.IO.Path]::IsPathRooted($OutputPath)) {
    $OutputPath = Join-Path $repoRoot $OutputPath
}
$OutputPath = [System.IO.Path]::GetFullPath($OutputPath)

$excludedDirectories = [System.Collections.Generic.HashSet[string]]::new(
    [System.StringComparer]::OrdinalIgnoreCase
)
foreach ($name in @(
    ".git", ".venv", ".pytest_cache", ".pytest-tmp", ".ruff_cache", ".mypy_cache",
    ".vscode", "__pycache__", "build", "dist", "models", "runs", "artifacts",
    "outputs", "output", "screenshots"
)) {
    [void]$excludedDirectories.Add($name)
}

function Get-SourceFiles {
    param(
        [Parameter(Mandatory)]
        [string]$Directory
    )

    foreach ($item in Get-ChildItem -LiteralPath $Directory -Force -ErrorAction Stop) {
        if ($item.PSIsContainer) {
            if (-not $excludedDirectories.Contains($item.Name) -and $item.Name -notlike "*.egg-info") {
                Get-SourceFiles -Directory $item.FullName
            }
            continue
        }

        if ($item.Extension -eq ".pyc") {
            continue
        }
        $relative = [System.IO.Path]::GetRelativePath($repoRoot, $item.FullName)
        if ($relative -ieq ".obsidian\workspace.json") {
            continue
        }
        $item
    }
}

$outputDirectory = Split-Path -Parent $OutputPath
[System.IO.Directory]::CreateDirectory($outputDirectory) | Out-Null
if (Test-Path -LiteralPath $OutputPath) {
    Remove-Item -LiteralPath $OutputPath -Force
}

$archive = [System.IO.Compression.ZipFile]::Open(
    $OutputPath,
    [System.IO.Compression.ZipArchiveMode]::Create
)
try {
    $files = @(Get-SourceFiles -Directory $repoRoot | Sort-Object -Property FullName)
    foreach ($file in $files) {
        $relative = [System.IO.Path]::GetRelativePath($repoRoot, $file.FullName).Replace("\", "/")
        $entry = $archive.CreateEntry(
            $relative,
            [System.IO.Compression.CompressionLevel]::Optimal
        )
        $entry.LastWriteTime = $file.LastWriteTime
        $sourceStream = $file.OpenRead()
        $targetStream = $entry.Open()
        try {
            $sourceStream.CopyTo($targetStream)
        }
        finally {
            $targetStream.Dispose()
            $sourceStream.Dispose()
        }
    }
}
finally {
    $archive.Dispose()
}

Write-Host "Created source archive: $OutputPath"
Write-Host "Excluded virtual environments, caches, build output, models, runs, artifacts, screenshots, and user workspace state."
