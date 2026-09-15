$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path $PSScriptRoot -Parent
$taskEnv = Join-Path $taskRoot '.venv'
$taskPython = Join-Path $taskEnv 'Scripts\python.exe'
if (-not (Test-Path -LiteralPath $taskPython)) {
    & python -m venv $taskEnv
    if ($LASTEXITCODE -ne 0) { throw 'Virtual environment creation failed.' }
}
$taskRequirements = Join-Path $PSScriptRoot 'studio-requirements.lock.txt'
& $taskPython -m pip install -r $taskRequirements
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
Push-Location $taskRoot
try {
    & $taskPython -m studio doctor
    if ($LASTEXITCODE -ne 0) { throw 'Studio tool check failed.' }
} finally { Pop-Location }
