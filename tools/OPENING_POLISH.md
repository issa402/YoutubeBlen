# Opening visual finish

The current proof is `.studio/renders/opening-polished/video.mp4`. This is the
existing three-shot, thirty-second animation with an editorial frame, three
cut-aligned chapter labels, timed narration phrases and a slight color adjustment.
It preserves all of the original composition and every spoken word. Its original
640x360 picture is upscaled into a 1280x720 frame; this is not a native HD render.

The code follows ECC's video-editing skill: deterministic FFmpeg composition,
separate reusable typography and source preservation. It uses already-installed
FFmpeg, OpenCV and the operating system's Segoe UI font. No downloaded assets,
paid tools, extra service or model call is needed for this step.

Run from the YouTube folder on Windows, choosing a fresh output folder each time:

```powershell
.\.venv\Scripts\python.exe blender/polish_opening.py `
  --source .studio/renders/opening-sequence-voiced/video.mp4 `
  --timeline .studio/audio/opening-guide-v3/timeline.json `
  --output .studio/renders/opening-polished-v2
```

The code refuses to overwrite an existing output directory. It validates all 720
source and output frames at 24 fps. It copies the AAC audio stream and compares
decoded PCM hashes, ensuring the original 29.793 seconds of spoken narration are
preserved exactly. AAC padding makes the decoded audio slightly longer than the
30-second picture; that padding is inherited from the source, not added speech.

Output files:

- `video.mp4`: finished opening proof, with the synthetic voice labeled on screen.
- `poster.png`: a representative frame for the studio review dashboard.
- `frame-0001.png`, `frame-0361.png`, `frame-0464.png`, `frame-0720.png`: review samples.
- `overlay.ass`: editable captions and typography.
- `captions.json`: phrase text and approximate start/end times.
- `validation.json`: frame count, dimensions, hashes and exact scope of validation.
- `ffmpeg.log`: render details and font resolution.

Caption phrases use approximate timings inside the measured paragraph boundaries.
They are not word-level forced alignment. Before publishing, align them to the
creator's final recorded performance. The present voice remains a synthetic
timing guide; the rest of the episode still needs its visuals and final edit.

For a native-resolution final, render the original Mac Blender packet at 1080p,
then adjust this compositor's picture/output dimensions proportionally. Do not
describe the current upscaled proof as native 720p or 1080p Blender footage.

Verification on 2026-09-07: all 720 frames decoded, 24 fps, 30-second picture,
unchanged decoded audio hash. First, middle, last and poster frames were visually
checked; captions sit below the picture and do not obscure its source labels.
