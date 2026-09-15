$ErrorActionPreference = 'Stop'
$taskIsolatedHome = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '.studio\codex-home'))
$taskConfiguredHome = [Environment]::GetEnvironmentVariable('CODEX_HOME')
if (-not $taskConfiguredHome -or [System.IO.Path]::GetFullPath($taskConfiguredHome) -ne $taskIsolatedHome) {
    throw 'Headroom modifies the active Codex configuration. Launch only from an isolated session whose CODEX_HOME is this project .studio\codex-home. See tools\HEADROOM_AND_3D_GUIDE.md. No configuration was changed.'
}
$taskHeadroom = Join-Path $PSScriptRoot '.venv\Scripts\headroom.exe'
if (-not (Test-Path -LiteralPath $taskHeadroom)) {
    throw 'Headroom is not installed. Run .\tools\setup_studio.ps1.'
}
Push-Location $PSScriptRoot
try {
    # Starts a new isolated Codex CLI through the local compression proxy. Headroom
    # registers its retrieval MCP so compressed originals remain recoverable.
    # We disable the extra Serena server because this project already has a
    # bounded index and Understand-Anything checkout.
    & $taskHeadroom wrap codex --code-memory none --memory -- @args
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} finally { Pop-Location }
