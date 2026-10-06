param(
    [ValidateSet('doctor', 'board', 'demo', 'start-free')]
    [string]$Command = 'doctor',
    [string]$Demo = 'world-in-numbers'
)

$ErrorActionPreference = 'Stop'
$projectRoot = [IO.Path]::GetFullPath($PSScriptRoot)
$upstream = Join-Path $projectRoot '.studio/repos/OpenMontage'
$python = Join-Path $upstream '.venv/Scripts/python.exe'
$composer = Join-Path $upstream 'remotion-composer/node_modules'
$composerLock = Join-Path $upstream 'remotion-composer/package-lock.json'
$auditedLock = Join-Path $projectRoot 'integrations/openmontage/remotion-package-lock.json'
$expected = '9327439db69021ab4b0e2776729bf3b58fdb5a87'
$ffmpegDir = Join-Path $projectRoot '.studio/bin'

if (-not (Test-Path -LiteralPath $python)) {
    throw 'OpenMontage runtime missing. See tools/OPENMONTAGE_FULL.md for setup.'
}
$head = (& git -C $upstream rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $head -ne $expected) {
    throw "OpenMontage commit differs from the tested pin: $head"
}
if (-not (Test-Path -LiteralPath $composerLock) -or
    (Get-FileHash -Algorithm SHA256 -LiteralPath $composerLock).Hash -ne
    (Get-FileHash -Algorithm SHA256 -LiteralPath $auditedLock).Hash) {
    throw 'OpenMontage Remotion lock differs from the audited overlay. See tools/OPENMONTAGE_FULL.md.'
}

$priorPath = $env:PATH
$env:PATH = "$ffmpegDir;$priorPath"
Push-Location $upstream
try {
    if ($Command -eq 'doctor') {
        & $python -c "from lib.config_model import OpenMontageConfig; from tools.tool_registry import registry; c=OpenMontageConfig.load(); registry.discover(); print('OpenMontage:', '$expected'); print('Budget:', c.budget.mode.value, c.budget.total_usd); print('Registered tools:', len(registry.list_all()))"
        if ($LASTEXITCODE -ne 0) { throw 'OpenMontage Python doctor failed.' }
        & $python -m pip check
        if ($LASTEXITCODE -ne 0) { throw 'OpenMontage Python dependencies are inconsistent.' }
        if (-not (Test-Path -LiteralPath $composer)) { throw 'Remotion composer missing; run npm ci in its directory.' }
        & (Join-Path $ffmpegDir 'ffprobe.exe') -version | Select-Object -First 1
        Write-Host 'Paperclip and the existing Blender/HyperFrames workflow remain separate.'
    } elseif ($Command -eq 'board') {
        & $python -m backlot open
        if ($LASTEXITCODE -ne 0) { throw 'Backlot failed to start.' }
    } elseif ($Command -eq 'demo') {
        & $python render_demo.py $Demo
        if ($LASTEXITCODE -ne 0) { throw 'OpenMontage demo failed.' }
    } else {
        & $python -c "from lib.config_model import OpenMontageConfig; c=OpenMontageConfig.load(); assert c.budget.mode.value == 'cap' and c.budget.total_usd == 0.0, 'Set OpenMontage budget to cap / 0 USD before start-free'"
        if ($LASTEXITCODE -ne 0) { throw 'The free-mode budget is not capped at zero.' }
        if (Test-Path -LiteralPath (Join-Path $upstream '.env')) {
            throw 'Remove provider keys from the OpenMontage .env before start-free.'
        }
        $keyNames = @('FAL_KEY','ATLASCLOUD_API_KEY','KLING_API_KEY','ARK_API_KEY','HEYGEN_API_KEY','RUNWAY_API_KEY','MINIMAX_API_KEY','OPENAI_API_KEY','GOOGLE_API_KEY','ELEVENLABS_API_KEY','XAI_API_KEY','SUNO_API_KEY')
        $saved = @{}
        foreach ($name in $keyNames) {
            $saved[$name] = [Environment]::GetEnvironmentVariable($name, 'Process')
            [Environment]::SetEnvironmentVariable($name, $null, 'Process')
        }
        try {
            & codex.cmd -C $upstream -s workspace-write 'Read AGENT_GUIDE.md and PROJECT_CONTEXT.md. I will give you a soccer video brief. Use the OpenMontage pipeline and Backlot checkpoints. This session is zero-paid-provider mode: do not call paid media APIs, sign up for services, or change the $0 budget. Keep claims labeled and sourced, preserve my first-person viewpoint, and ask me for the brief and creative approvals. Produce a proposal before assets or rendering.'
            if ($LASTEXITCODE -ne 0) { throw 'Codex CLI exited with an error.' }
        } finally {
            foreach ($name in $keyNames) { [Environment]::SetEnvironmentVariable($name, $saved[$name], 'Process') }
        }
    }
} finally {
    Pop-Location
    $env:PATH = $priorPath
}
