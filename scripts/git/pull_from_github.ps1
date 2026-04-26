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

function Run-GitWithRetry {
    param(
        [Parameter(Mandatory = $true)]
        [string[]] $Args,

        [int] $MaxAttempts = 4,
        [int] $DelaySeconds = 5
    )

    for ($attempt = 1; $attempt -le $MaxAttempts; $attempt++) {
        try {
            Run-Git -Args $Args
            return
        } catch {
            if ($attempt -ge $MaxAttempts) {
                throw
            }

            Write-Host ""
            Write-Host "git $($Args -join ' ') failed on attempt $attempt/$MaxAttempts." -ForegroundColor Yellow
            Write-Host "Retrying in $DelaySeconds seconds..." -ForegroundColor Yellow
            Start-Sleep -Seconds $DelaySeconds
        }
    }
}

if (-not (Test-Path ".git")) {
    throw "This folder is not a git repository: $repoRoot"
}

Write-Host "Repository: $repoRoot" -ForegroundColor Green
Write-Host "Remote: $(git remote get-url origin)"

Run-GitWithRetry @("fetch", "origin")

$local = (& git rev-parse HEAD).Trim()
$remote = (& git rev-parse origin/main).Trim()

if ($local -eq $remote) {
    Write-Host ""
    Write-Host "Already up to date with origin/main." -ForegroundColor Green
} else {
    Run-GitWithRetry @("pull", "--rebase", "--autostash", "origin", "main")
}

Write-Host ""
Run-Git @("status", "--short", "--branch")

Write-Host ""
Write-Host "Done. Files created or changed on GitHub are now local." -ForegroundColor Green
