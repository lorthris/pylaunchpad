<#
.SYNOPSIS
Runs PyLaunchpad commands with secrets injected from Vaultwarden through vw-run.

.DESCRIPTION
Maps secrets stored in the mylaunchpad Vaultwarden collection directly into the child process environment.
Prevents plaintext credential exposure on disk or in command-line arguments.

.PARAMETER Arguments
The command and arguments to execute with injected credentials.
#>
param(
    [Parameter(Mandatory = $true, ValueFromRemainingArguments = $true)]
    [string[]]$Arguments
)

$ErrorActionPreference = 'Stop'

$runner = Join-Path $env:USERPROFILE '.claude\tools\vw-run\vw_run.py'
if (-not (Test-Path $runner)) {
    throw "vw-run runner not found at $runner"
}

$vaultArgs = @(
    '-B', $runner,
    '--account', 'mylaunchpad',
    '--env', 'SECRET_KEY=app-security.secret_key',
    '--env', 'DATABASE_URL=database-app.database_url',
    '--env', 'POLAR_ORGANIZATION_ID=polar-billing.organization_id',
    '--env', 'POLAR_ACCESS_TOKEN=polar-billing.access_token',
    '--env', 'POLAR_WEBHOOK_SECRET=polar-billing.webhook_secret',
    '--env', 'POLAR_ENVIRONMENT=polar-billing.environment',
    '--'
) + $Arguments

& python @vaultArgs
exit $LASTEXITCODE
