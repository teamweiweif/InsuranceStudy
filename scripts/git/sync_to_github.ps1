param(
    [string] $Message = ""
)

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

Run-Git @("status", "--short", "--branch")

$dirtyBeforeAdd = (& git status --porcelain)
if ($dirtyBeforeAdd) {
    Run-Git @("add", "-A")

    $maxBytes = 50MB
    $largeStaged = @()
    $stagedNames = (& git diff --cached --name-only)
    foreach ($name in $stagedNames) {
        if (Test-Path -LiteralPath $name) {
            $item = Get-Item -LiteralPath $name
            if ($item.Length -gt $maxBytes) {
                $largeStaged += [PSCustomObject]@{
                    Path = $name
                    MB = [Math]::Round($item.Length / 1MB, 2)
                }
            }
        }
    }

    if ($largeStaged.Count -gt 0) {
        Write-Host ""
        Write-Host "Large staged files were detected. Nothing was committed." -ForegroundColor Red
        $largeStaged | Format-Table -AutoSize
        Run-Git @("reset")
        throw "Aborted to avoid pushing large data. Add an ignore rule or move these files out of git scope."
    }

    if (-not $Message) {
        $stamp = Get-Date -Format "yyyy-MM-dd HH:mm"
        $Message = "Sync local workspace $stamp"
    }

    Run-Git @("commit", "-m", $Message)
} else {
    Write-Host ""
    Write-Host "No local changes to commit." -ForegroundColor Yellow
}

Run-GitWithRetry @("fetch", "origin")
Run-GitWithRetry @("pull", "--rebase", "--autostash", "origin", "main")
Run-GitWithRetry @("push", "origin", "main")

Write-Host ""
Run-Git @("status", "--short", "--branch")

Write-Host ""
Write-Host "Done. Local tracked changes are committed and pushed to GitHub." -ForegroundColor Green
