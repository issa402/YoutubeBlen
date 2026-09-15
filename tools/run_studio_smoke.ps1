$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path $PSScriptRoot -Parent
$taskPython = Join-Path $taskRoot '.venv\Scripts\python.exe'
$taskRun = 'smoke-' + [DateTime]::UtcNow.ToString('yyyyMMdd-HHmmss')
Push-Location $taskRoot
try {
    & $taskPython -m pytest -q
    if ($LASTEXITCODE -ne 0) { throw 'Tests failed.' }
    & $taskPython -m studio demo --output ".studio/demo/$taskRun"
    if ($LASTEXITCODE -ne 0) { throw 'Media smoke failed.' }
    & $taskPython -m studio index
    if ($LASTEXITCODE -ne 0) { throw 'Index failed.' }
    & $taskPython -m studio dashboard
    if ($LASTEXITCODE -ne 0) { throw 'Dashboard failed.' }
} finally { Pop-Location }
