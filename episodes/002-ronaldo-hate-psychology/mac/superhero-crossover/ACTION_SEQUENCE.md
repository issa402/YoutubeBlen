# Ankle throw and Ronaldo reveal

September 18 revision: **Messi holds Mbappe by the ankle, swings and releases him; Mbappe flies into the warehouse wall, recoils and drops; Messi arrives hovering; an exhausted Mbappe looks up and points screen right; the camera follows toward Ronaldo.**

The sequence remains **260 frames at 30 fps (8.667 seconds)**. Main impact/reaction/reveal cuts retain the reference timing. Backgrounds and character performances are reconstructed 2.5D animation, not pixel-exact replacement or motion capture.

Read [HOW_THIS_ANIMATION_WORKS.md](HOW_THIS_ANIMATION_WORKS.md) for the beginner walkthrough of the code, artwork, motion, Hermes, token usage and two-computer workflow.

## Mac commands

Run in Terminal:

```bash
cd "$HOME/Desktop/Movies/YoutubeBlen"
git pull --ff-only
cd episodes/002-ronaldo-hate-psychology/mac/superhero-crossover
bash action.sh build
open -a Blender action-output/action-crossover.blend
```

Inside Blender choose **View > Cameras > Active Camera**, set frame 1 and click the timeline Play triangle. The saved viewport uses Solid texture mode. **Render > Render Image** shows final alpha/material appearance. Material Preview is optional. The prior native Mac SIGTRAP crash remains undiagnosed; Windows verification does not establish a Mac fix.

`bash action.sh preview` creates selected diagnostic stills. `bash action.sh render` creates all 1080p PNG frames. Both print new timestamped output folders and log paths. They do not create MP4s or automatically resume partial renders. The tutorial explains Windows video assembly. No additional Python packages are needed on Mac.

## Timeline (Blender frames, starting at 1)

| Frames | Action |
| --- | --- |
| 1–5 | Overhead ankle grip; Mbappe upside down |
| 6–10 | Accelerating swing with the ankle attached to Messi's hand |
| 11–13 | Release, opening fingers and follow-through |
| 14–32 | Close victim recedes toward warehouse; camera rolls |
| 33–43 | Flight reaches wall and contact flash |
| 44–64 | Close stylized impact cutaway, compression, shake and debris |
| 65–79 | Wall recoil and drop |
| 80–109 | Defeated kneel; Messi enters from above and hovers |
| 110–146 | Crossed-arm Messi hover |
| 147–175 | Exhausted Mbappe looks up toward Messi |
| 176–183 | Right arm lifts into the side-profile pointing pose |
| 184–208 | Hold point; camera moves right from frame 201 |
| 209–260 | Matched directional camera move, Ronaldo silhouette and color reveal |

## Implementation and checks

`action_motion.py` calculates the throw independently of Blender. Tests cover contact, fixed arm lengths, release continuity and travel direction. `action_art.py` draws editable sleeve/glove geometry, fingers, debris and speed lines. `action_crossover.py` constructs the shots, textures, shape keys, cameras and output.

`motion-report.json` records actual Blender camera samples, ankle-to-grip and visible-palm distances, rightward finger/head checks, head stability during the arm lift, frame count and render completion. These technical checks supplement visual inspection; they cannot certify artistic quality.

Ronaldo keeps the approved original image. Messi keeps the approved face/cape/legs, supplemented by native throwing-arm/torso geometry. The scene uses layered cel artwork rather than fully modeled skeletal characters. The preview is silent. The stylized rib overlay is not anatomical motion capture.

## New artwork

Built-in image generation produced these transparent poses while preserving the approved Mbappe/Turtle identity, blue mask, green limbs, gold chest, brown shell/straps, cropped hair and cel outlines:

- `action-point-right.png`: waist-up side-profile/three-quarter pose, face left, anatomically connected arm and index finger pointing screen right; exhausted, humbled, serious expression, no smile.
- `action-defeated.png`: full-body exhausted kneel, supporting hand on floor, eyes up-left, mouth closed, no smile. The alpha threshold removes the generated faint halo.

These are the final prompt directions; both used the built-in image tool. Existing inputs are `action-tumble.png`, `messi-omni-matched.png`, `ronaldo-approved.png`, `action-city.png`, `action-warehouse.png` and `reference-doorway.png`. The background plates were generated from reference frames with characters removed and obscured scenery reconstructed. Origins and SHA-256 hashes are in `assets/PROVENANCE.json`; older artwork remains for previous drafts.

Codex edited the project, the image tool supplied pose artwork, and Blender rendered the deterministic scene. No live Hermes generation call is required to build or play it.
