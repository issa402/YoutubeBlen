# September 16 reference sequence — work in progress

`reference_crossover.py` is a separate five-shot adaptation of the latest supplied 5.3876-second recording. It retains the approved character images. The previous eight-second scene remains available through `run.sh`.

This is **not an exact replacement** of the reference. It implements foreground boots arriving, city hover, crouch, pointing push-in/flash, and doorway reveal. The warehouse is procedural, the city is a crop of a generated doorway plate, and the point still uses the approved side-profile image. A new foreshortened arm/hand pose and accurate clean background plates remain required. Image generation reached its usage limit after creating the doorway plate. No source audio is included.

## Build on Mac

From this folder in Terminal:

```bash
"/Applications/Blender.app/Contents/MacOS/Blender" --background --factory-startup --python-exit-code 1 --python reference_crossover.py -- --output reference-output
```

Only after it finishes successfully:

```bash
open -a Blender reference-output/reference-crossover.blend
```

The viewport starts in Solid texture mode. Material Preview or rendering displays the artwork's transparency and lighting correctly. Mac crashes are still undiagnosed; passing Windows builds does not establish Mac compatibility. If the factory-startup test itself crashes, capture the Mac DiagnosticReports report before repeating scene builds.

Add `--render` to produce 162 PNG frames at 30 fps (5.4 seconds). Use a fresh output directory for each render; overwriting frames is refused. Default resolution is 1920×1080. Generated output stays local.

## Background provenance

`assets/reference-doorway.png` was generated with the built-in image tool using the supplied video's contact sheet as reference. Prompt: reconstruct the final shot's dark concrete warehouse doorway, blue glass city, cloudy sky and side crates; remove the character and interface overlays; preserve the composition and muted animated style. The result approximates the source composition and does not contain exact original background pixels.
