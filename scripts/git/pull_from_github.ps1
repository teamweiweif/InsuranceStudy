$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $repoRoot

function Run-Git {
    param(
        [Parameter(Mandatory = $true)]
        [string[]] $Args
    )

    Write-Host ""
    Write-Host "git $($Args -join ' ')" -ForegroundColor Cyan
    & git @Args
    if ($LASTEXITCODE -ne 0) {
        throw "git $($Args -join ' ') failed with exit code $LASTEXITCODE"
    }
}

if (-not (Test-Path ".git")) {
    throw "This folder is not a git repository: $repoRoot"
}

Write-Host "Repository: $repoRoot" -ForegroundColor Green
Write-Host "Remote: $(git remote get-url origin)"

Run-Git @("fetch", "origin")

$local = (& git rev-parse HEAD).Trim()
$remote = (& git rev-parse origin/main).Trim()

if ($local -eq $remote) {
    Write-Host ""
    Write-Host "Already up to date with origin/main." -ForegroundColor Green
} else {
    Run-Git @("pull", "--rebase", "--autostash", "origin", "main")
}

Write-Host ""
Run-Git @("status", "--short", "--branch")

Write-Host ""
Write-Host "Done. Files created or changed on GitHub are now local." -ForegroundColor Green
