$ErrorActionPreference = 'Stop'
$taskPython = Join-Path $PSScriptRoot '.studio\envs\vimax\Scripts\python.exe'
$taskRepo = Join-Path $PSScriptRoot '.studio\repos\ViMax'
if (-not (Test-Path -LiteralPath $taskPython)) { throw 'Run python tools/setup_integrations.py vimax first.' }
Push-Location $taskRepo
try {
    & $taskPython main_agent.py @args
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} finally { Pop-Location }
