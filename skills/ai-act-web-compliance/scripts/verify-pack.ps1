[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$validator = Join-Path $PSScriptRoot 'verify-pack.py'
if (-not (Test-Path -LiteralPath $validator -PathType Leaf)) {
    Write-Error 'Missing package validator: scripts\verify-pack.py'
    exit 1
}

$pythonCommand = Get-Command python -ErrorAction SilentlyContinue
if ($null -eq $pythonCommand) {
    Write-Error 'Python with PyYAML is required to validate the skill package.'
    exit 1
}

& $pythonCommand.Source -B $validator
exit $LASTEXITCODE
