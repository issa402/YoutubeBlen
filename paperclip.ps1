param(
    [ValidateSet('run', 'status', 'seed')]
    [string]$Action = 'run'
)

$repo = $PSScriptRoot
$binary = Join-Path $repo 'integrations/paperclip/node_modules/.bin/paperclipai.cmd'
$data = Join-Path $repo '.studio/paperclip'

if ($Action -eq 'status') {
    try {
        $health = Invoke-RestMethod -Uri 'http://127.0.0.1:3100/api/health' -TimeoutSec 5
        Write-Host "Paperclip $($health.version): $($health.status) at http://127.0.0.1:3100"
    } catch {
        Write-Error 'Paperclip is not responding. Run .\paperclip.ps1 run in another PowerShell window.'
        exit 1
    }
    exit 0
}

if ($Action -eq 'seed') {
    & node (Join-Path $repo 'integrations/paperclip/bootstrap.mjs')
    exit $LASTEXITCODE
}

if (-not (Test-Path -LiteralPath $binary)) {
    Write-Error 'Paperclip is not installed. Run npm ci --prefix integrations/paperclip first.'
    exit 1
}

$env:PAPERCLIP_NO_BROWSER = '1'
& $binary run --data-dir $data
exit $LASTEXITCODE
