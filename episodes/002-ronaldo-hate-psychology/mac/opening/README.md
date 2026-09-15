# Thirty-second opening sequence

Three actual animated shots, 720 frames at 24 fps. The sequence uses original geometric figures and invented screen graphics. It represents the narration's hypothetical feed and status/rivalry argument, not footage of a real match or identifiable supporters.

| Time | Shot | Animated action |
| --- | --- | --- |
| 00:00–00:14.833 | The rival becomes the main character | Camera push, sliding notification cards, rising reaction bars |
| 00:14.833–00:23.792 | The whole package | Rotating trophy, warm spotlight pulse, athlete arm gesture, camera movement |
| 00:23.792–00:30 | Rival camps | Red/cyan crowd arm gestures, gold attention ball crossing the divide, camera movement |

The cuts at frames 357 and 572 are real Blender camera changes aligned to the guide narration's status and rivalry paragraphs (within one frame). The script creates editable objects, keyframes, three cameras and lights. It requires no downloads, external assets, Python packages or AI account on the Mac; run with Blender 4.5 LTS under the permitted Git/Blender workflow.

```sh
# Open Terminal in this folder after pulling the approved code.
bash run.sh preview  # Nine sample frames at 640x360; motion data validated first.
bash run.sh build    # Editable opening-sequence.blend, no render.
bash run.sh render   # Full 1920x1080 PNG sequence, frames 0001–0720.
# Optional full-sequence 640x360 render instead of the full-resolution render:
bash run.sh draft
```

Use either `draft` or `render` in a fresh copy. The script refuses to overwrite an existing full PNG sequence. Preview frames and render.log are replaced on repeated preview runs. The saved .blend is always configured at 1080p even when the diagnostic render uses a smaller resolution.

`motion-report.json` samples nine frames including both sides of each camera cut. It records camera positions, trophy/ball/card/arm motion, light changes, foot clearance, inventory and completed render frames. `render_complete` is true only after all 720 frames finish. Blender errors go to render.log. Return permitted logs and frames for debugging; this is more useful than descriptions alone.

Windows assembly (the root studio has FFmpeg):

```powershell
.\studio.ps1 assemble path/to/frames --output .studio/renders/opening-final --fps 24
# Add the locally created guide voice when available, or your final narration:
.\studio.ps1 assemble path/to/frames --output .studio/renders/opening-with-voice --fps 24 --audio path/to/opening.wav
```

The code defaults to a fixed 30 seconds. Use a narration take no longer than that for this opening, or revise the shot contract and keyframes before lengthening it. Guide narration is for timing and review. Final performance and the rest of the episode still need editing.

Canonical reusable sources are `blender/opening_sequence.py` and `blender/sequence_spec.py`; this packet contains identical standalone copies. Windows rendering is verified separately; actual macOS execution is not implied by it.
