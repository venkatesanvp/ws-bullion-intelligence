# Update the currently checked-out application; no Git fetch/merge or credential changes.
$ErrorActionPreference = 'Stop'
& (Join-Path $PSScriptRoot 'bullion.ps1') -Action start
exit $LASTEXITCODE
