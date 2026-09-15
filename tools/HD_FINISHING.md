# Finish the native HD opening on Windows

The Mac packet builds the original three-shot animation. Windows combines the rendered frames with the unchanged 80-word opening, a local stock neural voice and ASR-timed captions. The full episode still requires the remaining chapter visuals and final editorial review.

Current verified voice: `.studio/audio/opening-neural-v1/narration-guide.wav`, 29.793 seconds. Current captions: `.studio/captions/opening-neural-v2/`, all 80 script words matched with no interpolated timing. These are ASR estimates, not manually checked phoneme alignment. See [neural voice setup](neural_voice_README.md) and [caption alignment](CAPTION_ALIGNMENT.md).

From the Windows repository root, after placing the Mac's approved rendered `frames` folder under `.studio/packages/mac-opening/`:

```powershell
.\studio.ps1 assemble .studio/packages/mac-opening/frames --output .studio/renders/mac-opening-silent --fps 24
.\studio.ps1 align-captions .studio/audio/opening-neural-v1/narration-guide.wav --text episodes/002-ronaldo-hate-psychology/script/OPENING_NARRATION.txt --output .studio/captions/mac-opening
.\studio.ps1 finish-opening .studio/renders/mac-opening-silent/video.mp4 --audio .studio/audio/opening-neural-v1/narration-guide.wav --alignment .studio/captions/mac-opening/alignment.json --text episodes/002-ronaldo-hate-psychology/script/OPENING_NARRATION.txt --output .studio/renders/mac-opening-finished
```

Every output must be fresh. If the existing v2 alignment is for the same exact WAV/text, use its `alignment.json` directly instead of realigning. The source images must form a complete 720-frame sequence; finishing accepts only 1280×720 or 1920×1080 at 24 fps. It preserves source dimensions, adds chapter labels and readable captions, pads the final silence, and encodes H.264/AAC without cutting speech.

`validation.json` records decoded frame count, dimensions, audio length and source hashes. `poster.png` and nine sample PNGs support visual inspection. Stale text/audio fingerprints, failed alignment, low ASR coverage, invalid cue timing or speech longer than 30 seconds stop finishing.

Generated voice, captions and renders live under ignored `.studio/` and are not delivered by Git. These paths refer to existing Windows assets; a fresh Windows installation first follows the setup/voice guides. The Mac can render from code without them.
