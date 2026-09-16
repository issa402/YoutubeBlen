# Floating Messi opening

A separate 12-second animated opening inspired by the supplied floating-superhero composition: a stylized Messi figure with folded arms, a blue cape and a city skyline. The character floats, the cape moves and the camera shifts. It uses layered 2.5D artwork built in Blender, with depth between layers; it is not a photorealistic face model.

The sequence is silent, 1920 x 1080, 24 fps, frames 1-288. It is a standalone opening option, not yet a replacement edit inside the existing narrated 30-second opening.

## Build on your Mac

Run these in **Terminal**, using your existing clone location:

```bash
cd "$HOME/Desktop/Movies/YoutubeBlen"
git pull --ff-only
cd episodes/002-ronaldo-hate-psychology/mac/messi-floating
bash run.sh build
open -a Blender messi-floating.blend
```

Only Git and Blender are required. No Python package install is needed. If Blender is installed elsewhere, set `BLENDER_BIN` to that executable's full path before running the launcher.

## Play inside Blender

The saved file is configured for the camera view with viewport overlays hidden. In the **Layout** workspace, set the timeline to frame **1** and click its **Play triangle**. Click it again to pause. Live playback may be slower than 24 fps while Blender draws the scene.

If you leave the camera view, use the 3D Viewport's **View > Cameras > Active Camera** menu. If grid or guide lines appear, turn off **Show Overlays**, the button with two overlapping circles near the viewport's upper-right corner. The camera border is an editor guide and does not appear in rendered frames.

To inspect the final lighting on one frame, use **Render > Render Image**. To render the whole sequence, use the Terminal command below. The launcher saves a diagnostic log and supports resuming verified frames.

## Render previews or the complete sequence

From the same `messi-floating` directory:

```bash
bash run.sh preview
open previews
```

This renders five sample frames: 1, 72, 144, 216 and 288. After reviewing them:

```bash
bash run.sh render
```

The output is a sequence of PNG images in `frames/`, not an MP4 with narration. After an interrupted render:

```bash
bash run.sh resume
```

Resume validates existing output against the current source and settings. Do not mix frames from different versions. A changed scene should be rendered to a fresh directory using the Python command below.

## Files and troubleshooting

- `messi_floating.py`: builds and animates the scene.
- `floating_spec.py`: deterministic motion definitions.
- `hd_spec.py`: render compatibility and output validation helpers.
- `messi-floating.blend`: generated editable scene to open in Blender.
- `motion-report.json`: generated scene/motion validation report.
- `previews/`, `frames/`, `render-*.log`: local render output and diagnostics.

Generated scene/render files remain local and are excluded from Git. Pulling this packet transfers code; rendering creates the larger files on your Mac.

If Blender fails, the launcher prints the last 80 lines of the log automatically. Send that traceback for diagnosis. Do not delete completed frames just because rendering failed.

Advanced example, rendering smaller previews to a separate directory:

```bash
"/Applications/Blender.app/Contents/MacOS/Blender" --background --python-exit-code 1 --python messi_floating.py -- --output "$HOME/Movies/messi-floating-review" --preview --resolution 960 540
```
