param(
    [ValidateSet('desk', 'worker', 'media')][string]$Mode = 'desk',
    [Parameter(ValueFromRemainingArguments = $true)][string[]]$Arguments
)

$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$python = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
if (-not (Test-Path $python)) { $python = 'python' }

switch ($Mode) {
    'desk' {
        Write-Host 'Open http://127.0.0.1:8766 in your browser. Press Ctrl+C to stop.'
        & $python -m studio.creator_server @Arguments
    }
    'worker' { & $python -m studio.creator_worker @Arguments }
    'media' { & $python -m studio.creator_media @Arguments }
}
exit $LASTEXITCODE
