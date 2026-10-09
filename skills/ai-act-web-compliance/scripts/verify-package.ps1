[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $false

$validator = Join-Path $PSScriptRoot 'verify-pack.py'
if (-not (Test-Path -LiteralPath $validator -PathType Leaf)) {
    Write-Error 'Missing package validator: scripts\verify-pack.py' -ErrorAction Continue
    exit 1
}

$pythonCommand = Get-Command -Name python -CommandType Application -ErrorAction SilentlyContinue |
    Select-Object -First 1
if ($null -eq $pythonCommand) {
    Write-Error 'Python with PyYAML is required to validate the skill package.' -ErrorAction Continue
    exit 1
}

& $pythonCommand.Source -B $validator
exit $LASTEXITCODE
