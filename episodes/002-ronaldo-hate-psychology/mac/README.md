# Episode 002: portable Blender intro

The current narrated opening uses the newer [30-second three-shot packet](opening/README.md). Start there for the sequence aligned to the opening guide voice. This folder retains the original eight-second visual proof below.

This code-only packet makes an original eight-second visual metaphor: abstract red and cyan football figures, a gold trophy, broadcast screens, colored lights and a moving camera. It depicts no real person's face or factual match event. The figures are stylized and the clip is a production proof, not a photoreal final.

Use Blender 4.5 LTS where these project files and Blender operations are employer-approved. No Python packages, AI agent, external assets, credentials or internet connection are required on the Mac. Blender's bundled Python runs the scene. The packet uses Eevee and does not require CUDA or a manually selected Metal device.

After pulling approved repository content, open Terminal in this folder:

```sh
# Three small preview frames, recommended first.
bash run.sh preview
# Optional: create scene.blend without rendering.
bash run.sh build
# Full 192-frame 1080p PNG sequence after reviewing the previews.
bash run.sh render
```

The launcher resolves its own absolute directory and works with spaces in paths. If Blender is installed somewhere else, use `BLENDER_BIN="/approved/path/to/Blender" bash run.sh preview`. `render.log` captures errors and progress; a failed run exits nonzero. Each run replaces that log and may replace existing render outputs in this packet. Preserve wanted outputs before rerunning.

Preview outputs are `previews/frame_0001.png`, `frame_0096.png`, and `frame_0192.png`. Full outputs are `frames/frame_0001.png` through `frame_0192.png`. `validation.json` records the actual Blender version, frame range, rendered resolution and completed frames. `render_complete` only becomes true when rendering finishes. `scene.blend` remains editable.

To debug, return only approved `render.log`, `validation.json`, and selected preview images. Describe the frame and intended visual change. These generated files are ignored by Git; the scripts and manifest are the handoff. No Mac execution has been tested here; the same scene is tested using Windows Blender 4.5.13 LTS.

For assembly on Windows from approved returned frames:

```powershell
.\.venv\Scripts\python.exe -m studio assemble path/to/frames --output .studio/renders/episode-002-intro --fps 24
```

Canonical reusable source is `blender/studio_scene.py` at repository root. This self-contained copy freezes the scene for the episode; update it deliberately when the canonical source changes.
