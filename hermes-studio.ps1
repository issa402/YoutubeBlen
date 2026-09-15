[CmdletBinding(PositionalBinding = $false)]
param(
    [string]$Episode,
    [string]$Task,
    [int]$MaxChars = 12000,
    [switch]$PrepareOnly,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$HermesArguments
)
$ErrorActionPreference = 'Stop'
$taskExecutable = Join-Path $PSScriptRoot '.studio\envs\hermes\Scripts\hermes.exe'
if (-not (Test-Path -LiteralPath $taskExecutable)) { throw 'Run python tools/setup_integrations.py hermes first.' }
if (($Episode -and -not $Task) -or ($Task -and -not $Episode)) { throw '-Episode and -Task must be provided together.' }
if ($PrepareOnly -and -not $Episode) { throw '-PrepareOnly requires -Episode and -Task.' }
$taskInvocation = @($HermesArguments)
if ($Episode) {
    if ($HermesArguments | Where-Object { $_ -match '^(--query-file|--query|-q)(=|$)' }) {
        throw 'Episode mode supplies --query-file; do not also supply a query.'
    }
    $taskPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
    $taskInputDirectory = Join-Path $PSScriptRoot '.studio\handoffs'
    [System.IO.Directory]::CreateDirectory($taskInputDirectory) | Out-Null
    $taskInputFile = Join-Path $taskInputDirectory ('.task-' + [guid]::NewGuid().ToString('N') + '.txt')
    Push-Location $PSScriptRoot
    try {
        # Windows PowerShell 5.1's native argument marshalling can strip embedded
        # quotes. Pass arbitrary creator text through UTF-8, never native argv.
        [System.IO.File]::WriteAllText($taskInputFile, $Task, [System.Text.UTF8Encoding]::new($false))
        $taskPromptJson = & $taskPython -m studio --root $PSScriptRoot hermes-prompt $Episode --task-file $taskInputFile --max-chars $MaxChars
        if ($LASTEXITCODE -ne 0) { throw 'Could not prepare the episode handoff.' }
        $taskPromptEnvelope = ($taskPromptJson -join "`n") | ConvertFrom-Json
        $taskPrompt = $taskPromptEnvelope.result
        if (-not $taskPrompt.path) { throw 'Studio did not return a handoff path.' }
    } finally {
        Pop-Location
        if (Test-Path -LiteralPath $taskInputFile) { Remove-Item -LiteralPath $taskInputFile }
    }
    if ($PrepareOnly) { $taskPromptJson; return }
    $taskInvocation = @('chat', '--query-file', $taskPrompt.path, '--oneshot', '--max-turns', '20') + @($HermesArguments)
}
$taskPreviousHermesHome = $env:HERMES_HOME
$env:HERMES_HOME = Join-Path $PSScriptRoot '.studio\hermes-home'
Push-Location $PSScriptRoot
try {
    & $taskExecutable @taskInvocation
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} finally {
    Pop-Location
    $env:HERMES_HOME = $taskPreviousHermesHome
}
