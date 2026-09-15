# Narration and first edit

The first-release source is `episodes/002-ronaldo-hate-psychology/script/NARRATION.txt`.
It matches all nine Voiceover sections of the master script exactly: 1,416 words.
`OPENING_NARRATION.txt` is its 80-word opening. `RECORDING_GUIDE.md` covers delivery;
`PUBLISHING_PACK.md` contains titles, description, sources and a thumbnail concept.

## Listen and inspect

Local generated files:

- `.studio/audio/episode-guide-v1/narration-guide.wav`: complete synthetic timing read, **9:40.198**.
- `.studio/audio/episode-guide-v1/timeline.json`: measured paragraph start/end times with script hash.
- `.studio/audio/episode-guide-v1/chapters.txt`: measured chapter starts, with old target timestamps removed.
- `.studio/audio/episode-guide-v1/guide-paragraphs.srt`: paragraph timing reference, not polished release captions.
- `.studio/audio/opening-guide-v3/narration-guide.wav`: **29.793 seconds**, slightly faster opening read.

These use Microsoft David Desktop, an installed Windows voice. No voice cloning or paid
provider is involved. The synthetic guide helps assess structure and build an edit;
pronunciation, emotion and final delivery still need review. The full guide reads the opening
at normal speed (34.283 seconds), while the standalone opening uses rate +1 to fit the 30-second
sequence. These are alternative timing takes; do not concatenate both openings.

## Recreate guide audio

From the Youtube folder on Windows:

```powershell
.\studio.ps1 voice-guide 002-ronaldo-hate-psychology --output .studio/audio/episode-new
.\studio.ps1 voice-guide 002-ronaldo-hate-psychology --opening --rate 1 --output .studio/audio/opening-new
```

Choose a fresh output folder on every run. Existing audio is preserved. Use `--voice 'Installed Voice Name'`
for another installed Windows voice. The command reads only spoken text, creates each paragraph as PCM audio,
joins those files without resampling, and measures the actual durations. A restricted execution sandbox may
block Windows voice initialization even when the voice is listed; run the command in your normal permitted
Windows terminal. No extra software is required on the Mac.

## Render and combine

The code-only Mac sequence is under `episodes/002-ronaldo-hate-psychology/mac/opening/`:

```sh
bash run.sh preview
bash run.sh draft
# Or, in a fresh output folder, full 1080p:
bash run.sh render
```

Return the frames through the permitted transfer workflow. On Windows:

```powershell
.\studio.ps1 assemble PATH_TO_FRAMES --fps 24 --output .studio/renders/opening-silent
.\studio.ps1 mux-guide .studio/renders/opening-silent/video.mp4 .studio/audio/opening-guide-v3/narration-guide.wav --output .studio/renders/opening-voiced
```

`mux-guide` uses the full narration WAV. If narration exceeds the video, it holds the last frame and reports
that hold rather than silently cutting words. If the narration ends first, the remaining picture gets silence.
This is for guide review; revise the performance or the shot timing for the final edit.

The Blender sequence creates geometry, lights, keyframes and three camera shots. It is an original stylized
metaphor, not a realistic simulation of either footballer. It is the opening, not ten minutes of completed 3D.
The remaining eight chapters have visual direction in the master script and need their source cards and shots assembled.

## Editorial handoff

1. Listen to the guide while reading NARRATION.txt. Save precise corrections through `studio feedback`.
2. Record your final performance, or configure and choose a licensed synthetic voice if desired.
3. Replace guide timings with the final recording's timings before locking the edit or description chapters.
4. Use original Blender visuals and dated source cards. Add footage/music only after checking rights.
5. Inspect the final audio, captions, factual labels and export before publishing.

No paid generation, publishing or Git push happens through these commands.
