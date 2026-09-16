# Messi / Mbappe / Ronaldo superhero crossover

Original editable 2.5D recreation of the supplied approximately 4.334-second reference. 104 frames at 24 fps (4.333 seconds), 1920x1080 by default. Silent; source recording audio and UI are not embedded.

| Frames | Replacement shot |
| --- | --- |
| 1-23 | Messi as Omni-Man, red/white suit, folded arms, hovering over city |
| 24-46 | Mbappe as a Ninja Turtle, crouched on a concrete floor |
| 47-71 | Foreshortened turtle hand pointing toward the next reveal |
| 72-104 | Ronaldo in Superman-style blue suit, red cape and seven crest, emerging from shadow in doorway |

The reference's shot order, approximate timing and compositions guide this scene. Artwork is an original stylized reconstruction, not pixel-identical footage or a realistic 3D face scan. Character models use layered polygons and ink curves; no third-party downloads are needed.

## On the Mac

Run in Terminal:

```bash
cd "$HOME/Desktop/Movies/YoutubeBlen"
git pull --ff-only
cd episodes/002-ronaldo-hate-psychology/mac/superhero-crossover
bash run.sh build
open -a Blender superhero-crossover.blend
```

The Layout viewport opens through the active camera, with overlays hidden. Click the timeline Play triangle. Camera cuts happen automatically. Frames run 1-104. Use View > Cameras > Active Camera if you leave camera view. This packet is separate from the previous openings.

```bash
bash run.sh preview
open previews
bash run.sh render
```

Preview renders ten frames around all cuts and gestures. Render writes 104 silent PNGs under frames/. Use `bash run.sh resume` for an interrupted render with unchanged code/settings. Source fingerprints and PNG integrity protect resume; changed source requires a fresh output folder. Keep a failed run's frames and log for diagnosis. The launcher prints the error automatically.

To choose a fresh output folder or lower resolution:

```bash
"/Applications/Blender.app/Contents/MacOS/Blender" --background --python-exit-code 1 --python superhero_crossover.py -- --output "$HOME/Movies/crossover-review" --preview --resolution 960 540
```

Generated .blend, frames, previews, logs and motion reports remain local. The .blend contains the complete animation; the Python files generate it. Playback speed in the viewport depends on the machine. Windows rendered verification and Mac execution are reported separately in CURRENT_STATUS.md.
