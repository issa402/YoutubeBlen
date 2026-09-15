$ErrorActionPreference = 'Stop'
$taskPython = Join-Path $PSScriptRoot '.studio\envs\vimax\Scripts\python.exe'
$taskWeb = Join-Path $PSScriptRoot '.studio\repos\ViMax\web'
if (-not (Test-Path -LiteralPath $taskPython)) { throw 'Run python tools/setup_integrations.py vimax first.' }
if (-not (Test-Path -LiteralPath (Join-Path $taskWeb 'dist'))) { throw 'Build ViMax web first: npm ci --ignore-scripts then npm run build in its web folder.' }
$taskPriorPython = $env:VIMAX_PYTHON_CMD
$env:VIMAX_PYTHON_CMD = $taskPython
Push-Location $taskWeb
try { & node server.mjs } finally { Pop-Location; $env:VIMAX_PYTHON_CMD = $taskPriorPython }
