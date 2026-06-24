param(
    [Parameter(Position = 0)]
    [ValidateSet("status", "start", "review", "test")]
    [string]$Command = "status",

    [Parameter(Position = 1)]
    [string]$BranchName
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Assert-RepoRoot {
    if (-not (Test-Path ".git")) {
        throw "Run this script from the repository root."
    }
}

function Invoke-Git {
    param(
        [Parameter(ValueFromRemainingArguments = $true)]
        [string[]]$GitArgs
    )

    & git @GitArgs

    if ($LASTEXITCODE -ne 0) {
        throw "git $($GitArgs -join ' ') failed with exit code $LASTEXITCODE."
    }
}

function Get-ShortStatus {
    $status = & git status -sb

    if ($LASTEXITCODE -ne 0) {
        throw "git status failed."
    }

    return $status
}

function Assert-CleanMain {
    $status = Get-ShortStatus

    if ($status -ne "## main...origin/main") {
        Write-Host $status
        throw "Expected clean main: ## main...origin/main"
    }
}

function Invoke-ProjectTests {
    & python scripts\validate_all_evidence_packs.py

    if ($LASTEXITCODE -ne 0) {
        throw "Evidence pack validation failed."
    }

    & python scripts\test_evidence_pack_validator_failures.py

    if ($LASTEXITCODE -ne 0) {
        throw "Validator failure regression tests failed."
    }
}

Assert-RepoRoot

switch ($Command) {
    "status" {
        Get-ShortStatus
    }

    "start" {
        if ([string]::IsNullOrWhiteSpace($BranchName)) {
            throw "Usage: .\tools\task.ps1 start <branch-name>"
        }

        Assert-CleanMain
        Invoke-Git switch main
        Invoke-Git pull --ff-only
        Assert-CleanMain
        Invoke-Git switch -c $BranchName
        Get-ShortStatus
    }

    "review" {
        Invoke-Git diff --stat
        Invoke-Git diff --
        Get-ShortStatus
    }

    "test" {
        Invoke-ProjectTests
        Get-ShortStatus
        Write-Host "Tests passed."
    }
}