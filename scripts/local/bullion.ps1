param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('setup','start','stop','restart','status','test','recover')]
    [string]$Action,
    [ValidateSet('api','ui','db')][string]$Service
)
$ErrorActionPreference = 'Stop'
$RepoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '../..')).Path
$PythonPath = Join-Path $RepoRoot '.venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $PythonPath)) { throw 'Run uv sync before local management.' }
$Arguments = @((Join-Path $PSScriptRoot 'manage.py'), $Action)
if ($Service) { $Arguments += @('--service', $Service) }
& $PythonPath @Arguments
exit $LASTEXITCODE
