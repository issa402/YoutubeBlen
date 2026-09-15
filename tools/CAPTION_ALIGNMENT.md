# Captions aligned to the actual voice

The opening now uses the exact supplied narration with timing anchors estimated
from its actual audio. The approved current grouping is
`.studio/captions/opening-neural-v2/alignment.json`, with companion `captions.srt`
and `captions.vtt`. Every one of the 80 script words matched the locally cached
Whisper tiny model in order; zero words required interpolation. The measured WAV
duration is 29.793 seconds. The captions still need listening/visual review; a
100% text match does not mean frame-perfect or phoneme-level forced alignment.

This uses the project's creator-studio skill and ECC video-editing/verification
workflow: keep the creator's text authoritative, perform repeatable local media
work, inspect timings, and test text preservation and failure cases. It makes no
provider calls and downloads no model. The cached model runs on CPU with two
threads. Other already-cached `base` or `small` models can be explicitly selected.

From the repository root in PowerShell, using a new output folder:

```powershell
.\studio.ps1 align-captions `
  .studio/audio/opening-neural-v1/narration-guide.wav `
  --text episodes/002-ronaldo-hate-psychology/script/OPENING_NARRATION.txt `
  --output .studio/captions/opening-neural-next
```

The Python entry is `studio.captions.align(audio, text_path, output, model='tiny')`.
Input audio must be a PCM WAV, at most one hour, and the English script is limited
to 6,000 whitespace-separated words. Existing artifacts are never overwritten.
The studio CLI restricts outputs to the project's `.studio/` area. The Python
function also supports explicit external output folders for tests/integration.

`alignment.json` contains the exact script tokens, caption phrases and:

- `source_audio_sha256` and `source_text_sha256`: fingerprints of the inputs.
- `asr_match_ratio`: matched supplied script words divided by supplied words.
- `asr_precision`: matched words divided by recognized words, to expose extra
  speech/hallucinations that do not belong to the script.
- `words`: exact text, start/end seconds, zero-based index, recognizer index when
  matched, and `timing_method` equal to `matched` or `interpolated`.
- `cues`: exact joined text, start/end seconds and the half-open word index range
  `word_start` through `word_end`. `ass_text` is an optional safe ASS display
  version that replaces override braces/backslashes with fullwidth characters.
- `full_spoken_word_coverage`: every supplied script token was emitted in order.
  This verifies caption completeness, not that an independent listener confirmed
  every supplied word was spoken. `coverage_meaning` records this distinction.

Normalized word matching ignores punctuation/case/apostrophe differences while
the displayed captions retain the original words and punctuation. ASR errors
never replace the creator's wording. Small unmatched spans receive explicitly
marked interpolated timings; if adjacent anchors leave no gap, their timing may
be adjusted and relabeled too. Either match ratio below 80%, invalid word timing,
unreadable input or missing cached model fails with an explanation. Recognition
failures preserve `alignment.json` diagnostics without publishing subtitle files.

Phrases favor four to six words and punctuation boundaries, avoid dangling
articles/determiners where possible, and prevent a one-word leftover at a long
sentence's end. Short complete sentences remain intact. The final grouping has
18 cues; its closing phrase is “feels like your victory.” Earlier v1 remains as
the original alignment record; v2 reuses those identical word timestamps and
improves grouping without another speech generation or model inference.

SRT and WebVTT text escapes markup. The compositor independently escapes ASS
overrides, validates hashes against the exact voice and script, and checks that
all caption text survives before encoding. Re-align whenever narration text or
audio changes; never reuse timings solely because a filename stayed the same.

Verification: 18 focused tests pass with 96% coverage for `studio.captions`.
Tests use generated WAV fixtures and mocked recognition, covering ASR omissions,
misrecognition, repeated words, invalid timing, coverage failure diagnostics,
formatting injection, source preservation and phrase grouping. The current
neural opening was also aligned using the real cached model.
