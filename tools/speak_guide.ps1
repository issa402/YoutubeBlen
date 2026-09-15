param([Parameter(Mandatory=$true)][string]$Manifest)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Speech
$taskManifestPath = (Resolve-Path -LiteralPath $Manifest).Path
$taskFolder = Split-Path -Parent $taskManifestPath
$taskData = Get-Content -LiteralPath $taskManifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
if ($taskData.rate -lt -10 -or $taskData.rate -gt 10) { throw 'Invalid speech rate.' }
$taskSpeaker = New-Object System.Speech.Synthesis.SpeechSynthesizer
try {
    $taskSpeaker.SelectVoice([string]$taskData.voice)
    $taskSpeaker.Rate = [int]$taskData.rate
    $taskFormat = New-Object System.Speech.AudioFormat.SpeechAudioFormatInfo -ArgumentList 24000,([System.Speech.AudioFormat.AudioBitsPerSample]::Sixteen),([System.Speech.AudioFormat.AudioChannel]::Mono)
    foreach ($taskSegment in $taskData.segments) {
        if ($taskSegment.audio_file -notmatch '^segment_[0-9]{4}\.wav$') { throw 'Invalid segment filename.' }
        $taskOutput = Join-Path $taskFolder $taskSegment.audio_file
        if (Test-Path -LiteralPath $taskOutput) { throw "Audio already exists: $taskOutput" }
        $taskSpeaker.SetOutputToWaveFile($taskOutput, $taskFormat)
        $taskSpeaker.Speak([string]$taskSegment.text)
        $taskSpeaker.SetOutputToNull()
    }
} finally {
    $taskSpeaker.Dispose()
}
