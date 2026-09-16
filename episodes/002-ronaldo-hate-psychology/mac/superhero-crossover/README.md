# Messi / Mbappe / Ronaldo superhero crossover

Revised 8-second adaptation of the supplied approximately 4.334-second reference. 192 frames at 24 fps, 1920x1080 by default. Silent; source recording audio and UI are not embedded.

| Frames | Replacement shot |
| --- | --- |
| 1-44 | Messi as Omni-Man, red/white suit, folded arms, hovering over city |
| 45-87 | Mbappe as a Ninja Turtle, crouched on a concrete floor |
| 88-132 | Side-profile Mbappe with a proportionate arm lifting to point toward the next reveal |
| 133-192 | Ronaldo in Superman-style blue suit, red cape and seven crest, emerging from shadow in doorway |

The reference's shot order, compositions and shot order, with longer holds guide this scene. Artwork is an original stylized reconstruction, not pixel-identical footage or a realistic 3D face scan. Ronaldo uses the creator's supplied illustration directly, UV-mapped to a manually outlined silhouette. Messi and both Mbappe poses use matching generated cel illustrations. The Messi cape and side-profile pointing arm use bounded vertex animation. Images are packed into the .blend. No downloads or packages are needed on the Mac.

## Current artwork

Active images: `ronaldo-approved.png`, `messi-omni-matched.png`, `mbappe-crouch-matched.png`, `mbappe-profile-matched.png`. Earlier assets remain for prior versions. Git transfers these images with the code; Blender requires no downloads.

## On the Mac

Run in Terminal:

```bash
cd "$HOME/Desktop/Movies/YoutubeBlen"
git pull --ff-only
cd episodes/002-ronaldo-hate-psychology/mac/superhero-crossover
bash run.sh build
open -a Blender superhero-crossover.blend
```

The Layout viewport opens through the active camera, with overlays hidden. Click the timeline Play triangle. Camera cuts happen automatically. Frames run 1-192. Use View > Cameras > Active Camera if you leave camera view. This packet is separate from the previous openings.

```bash
bash run.sh preview
open previews
bash run.sh render
```

Preview renders ten frames around all cuts and gestures. Render writes 192 silent PNGs under frames/. Use `bash run.sh resume` for an interrupted render with unchanged code/settings. Source fingerprints and PNG integrity protect resume; changed source requires a fresh output folder. Keep a failed run's frames and log for diagnosis. The launcher prints the error automatically.

To choose a fresh output folder or lower resolution:

```bash
"/Applications/Blender.app/Contents/MacOS/Blender" --background --python-exit-code 1 --python superhero_crossover.py -- --output "$HOME/Movies/crossover-review" --preview --resolution 960 540
```

Generated .blend, frames, previews, logs and motion reports remain local. The .blend contains the complete animation; the Python files generate it. Playback speed in the viewport depends on the machine. Windows rendered verification and Mac execution are reported separately in CURRENT_STATUS.md.

## Updating from the old four-second render

`build` creates the revised .blend; reopen it rather than replaying the old file already open in Blender. Existing old frame/preview directories cannot be resumed with revised source. Use a fresh output location for the new render:

```bash
"/Applications/Blender.app/Contents/MacOS/Blender" --background --python-exit-code 1 --python superhero_crossover.py -- --output "$HOME/Movies/crossover-eight-seconds" --render
```

The bundled PNG character assets add several MB to the Git pull. The pointing arm is a controlled deformation of the cutout; the face stays fixed. This is limited 2.5D animation, not full skeletal character acting or a pixel-perfect replica. Ronaldo preserves the supplied design; the matching cast illustrations should be judged visually against that reference.
