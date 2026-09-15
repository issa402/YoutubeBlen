param([switch]$RefreshLock)
$ErrorActionPreference = 'Stop'
$studioRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$repoRoot = Join-Path $studioRoot '.studio/repos'
$lockPath = Join-Path $studioRoot '.studio/repos-lock.json'
$baselineLockPath = Join-Path $studioRoot 'integrations/studio/repos-lock.json'
$catalog = @(
    @{ name = 'hermes-agent'; url = 'https://github.com/NousResearch/hermes-agent.git' },
    @{ name = 'ViMax'; url = 'https://github.com/HKUDS/ViMax.git' },
    @{ name = 'Understand-Anything'; url = 'https://github.com/Egonex-AI/Understand-Anything.git' },
    @{ name = 'last30days-skill'; url = 'https://github.com/mvanhorn/last30days-skill.git' }
)
$previous = @{}
$readLockPath = $lockPath
if (-not (Test-Path -LiteralPath $readLockPath)) { $readLockPath = $baselineLockPath }
if (Test-Path -LiteralPath $readLockPath) {
    foreach ($entry in (Get-Content -LiteralPath $readLockPath -Raw | ConvertFrom-Json).repositories) {
        $previous[$entry.name] = $entry
    }
}
New-Item -ItemType Directory -Force -Path $repoRoot | Out-Null
$records = @()
$failed = $false
foreach ($repo in $catalog) {
    $destination = Join-Path $repoRoot $repo.name
    $record = [ordered]@{ name = $repo.name; url = $repo.url; path = ".studio/repos/$($repo.name)"; commit = $null; status = 'error'; error = $null }
    try {
        if (-not (Test-Path -LiteralPath $destination)) {
            & git clone --depth 1 -- $repo.url $destination
            if ($LASTEXITCODE -ne 0) { throw 'git clone failed; existing partial files are preserved.' }
            if ($previous.ContainsKey($repo.name) -and $previous[$repo.name].commit -and -not $RefreshLock) {
                $pin = $previous[$repo.name].commit
                if ($pin -notmatch '^[0-9a-f]{40}$') { throw 'Invalid commit in lock file.' }
                & git -C $destination fetch --depth 1 origin $pin
                if ($LASTEXITCODE -ne 0) { throw 'Could not retrieve pinned commit.' }
                & git -C $destination checkout --detach $pin
                if ($LASTEXITCODE -ne 0) { throw 'Could not check out pinned commit.' }
            }
        }
        if (-not (Test-Path -LiteralPath (Join-Path $destination '.git'))) { throw 'Existing directory is not a Git clone; preserved.' }
        $origin = (& git -C $destination remote get-url origin)
        if ($LASTEXITCODE -ne 0 -or $origin -ne $repo.url) { throw 'Existing clone has an unexpected origin; preserved.' }
        $commit = (& git -C $destination rev-parse HEAD)
        if ($LASTEXITCODE -ne 0 -or $commit -notmatch '^[0-9a-f]{40}$') { throw 'Unable to resolve commit.' }
        $record.commit = $commit
        if ($previous.ContainsKey($repo.name) -and $previous[$repo.name].commit -and $previous[$repo.name].commit -ne $commit -and -not $RefreshLock) {
            throw 'Existing HEAD differs from lock; preserved. Review and use -RefreshLock to record it.'
        }
        $record.status = 'cloned-not-installed'
    } catch {
        $record.error = $_.Exception.Message
        $failed = $true
        Write-Warning "$($repo.name): $($record.error)"
    }
    $records += [pscustomobject]$record
}
$report = [ordered]@{ schema_version = 1; checked_at = [DateTime]::UtcNow.ToString('o'); repositories = $records }
if ($failed) {
    $report | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $studioRoot '.studio/repos-fetch-errors.json') -Encoding UTF8
    Write-Error 'One or more repositories failed verification; original lock preserved. See .studio/repos-fetch-errors.json.'
    exit 1
}
$report | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $lockPath -Encoding UTF8
$records | Format-Table name, status, commit
