# Complete architecture and animation guide

This guide teaches how the complete YouTube production system and the current Messi/Mbappe/Ronaldo animation are organized, how the artwork becomes motion, why the animation can still feel like moving cutouts, and how to build your own higher-quality scenes.

The current action clip is a **2.5D illustrated animation**. It renders 260 complete images at 30 frames per second, but most characters begin as one flat drawing. Blender moves, rotates, scales and locally bends those drawings. This is faster and more controllable than building three complete 3D characters, but it cannot produce all the body changes that a hand-drawn animator or skeletal 3D rig creates.

The most important distinction is:

```text
Frame rate = how many finished pictures are shown each second.
Animation detail = how much actually changes inside those pictures.
```

This project already outputs 30 pictures per second. The current limitation is **pose density and articulation**, not a missing frame rate.

## 1. The whole system in one picture

```text
YOUR IDEA AND OPINION
        |
        v
episode brief + creator take + research + script
        |
        v
shot list and reference timing
        |
        +--------------------------+
        |                          |
        v                          v
character/background art      motion design
PNG assets                    frame ranges, arcs,
transparent cutouts           contacts, cameras
        |                          |
        +------------+-------------+
                     v
             Blender scene builder
        action_crossover.py + helpers
                     |
        +------------+-------------+
        |                          |
        v                          v
editable .blend             rendered PNG frames
        |                          |
        |                          v
        |                    FFmpeg/studio assemble
        |                          |
        +--------------------------+
                     v
              silent MP4 / final edit
                     |
                     v
         narration + captions + publishing
```

Codex helps write and inspect the files. Image generation creates selected character poses and clean background plates. Blender creates the actual scene and frames. FFmpeg turns those frames into a video. Hermes is an optional agent runner that can receive a bounded project handoff; it is not required to run Blender and did not secretly animate this sequence.

## 2. Repository map

The repository contains both the overall content studio and the portable Blender scene.

| Path | Purpose |
| --- | --- |
| `PROJECT_CONTEXT.md` | Current channel, hardware, workflow and active production context. Read this first. |
| `CURRENT_STATUS.md` | What has actually been completed, verified or left unresolved. |
| `DECISIONS.md` | Durable choices and the reasons behind them. |
| `AGENTS.md` | Rules for anyone or any agent changing the project. |
| `episodes/` | One folder per video idea or episode. This is where the editorial truth lives. |
| `blender/` | Canonical reusable Blender source and artwork on Windows. This is the development copy. |
| `studio/` | The Python production system: episodes, feedback memory, reviews, packaging, frame assembly, audio and Hermes handoffs. |
| `tools/` | Human-facing setup and operating guides plus voice/media helpers. |
| `tests/` | Automated contracts for motion, packet parity, media handling and the studio. |
| `.studio/` | Local generated state: renders, databases, handoffs, environments and reports. It is generally ignored by Git. |
| `skills/` | Project-specific reusable instructions such as the creator-studio workflow. |
| `external/` | Preserved external reference source. It is not the active scene entry point. |
| `editorial/` | Standards for evidence, claims and creator voice. |
| `schemas/` | Structured-data definitions used by production records. |
| `integrations/` | Optional integrations kept separate from the core animation. |

### Why `.studio/` and `episodes/` are different

`episodes/` contains versioned source material that should travel through Git. `.studio/` contains machine-local outputs and working state. A rendered MP4 in `.studio/renders/` does not automatically reach the Mac through Git. The portable Python and PNG assets under `episodes/.../mac/` do.

## 3. The active episode folder

The active episode is:

```text
episodes/002-ronaldo-hate-psychology/
```

Its important areas are:

| Folder/file | Purpose |
| --- | --- |
| `CREATOR_TAKE.md` | Your original opinion and desired angle. It preserves your voice. |
| `BRIEF.md` | The episode promise, audience and intended structure. |
| `CLAIMS_LEDGER.md` | Internal status of factual claims, allegations, inferences and opinions. |
| `research/` | Sources and evidence records. |
| `script/` | Master production script and clean narration. |
| `manifests/` | Explicit selections of production assets. |
| `mac/` | Portable Blender packets that the Mac can pull and run. |

The superhero sequence lives at:

```text
episodes/002-ronaldo-hate-psychology/mac/superhero-crossover/
```

That folder is a **self-contained delivery packet**. It has copies of the required Python files and images so Blender on the Mac does not need the Windows Python environment.

## 4. Canonical source versus the Mac packet

There are two copies of the active animation source:

```text
blender/                                          development source
episodes/.../mac/superhero-crossover/            portable Mac copy
```

The canonical files are developed in `blender/`. When a version is ready, the required files are copied into the Mac packet. `tests/test_action_sequence.py` compares their bytes so a stale packet is detected.

This duplication is deliberate. Blender runs the packet with its own bundled Python, and all required imports and images sit next to the entry script. The Mac does not need to install packages from the Windows environment.

When editing the animation, change the canonical file first, synchronize its packet copy, then run the parity test. If you change only the packet, the next synchronization can overwrite your work. If you change only `blender/`, the Mac will continue running the old packet.

## 5. Every file in the active Blender system

### Main animation files

| File | Responsibility |
| --- | --- |
| `action_crossover.py` | Main director. Defines frame rate, shot cuts, artwork, cameras, motion, effects, validation, saving and rendering. |
| `action_motion.py` | Pure Python motion math for the ankle throw. It has no `bpy` dependency, so normal pytest can verify it. |
| `action_art.py` | Creates native Blender cel geometry: sleeve, glove, fingers, speed lines and impact debris. |
| `crossover_sprites.py` | Converts a PNG into a textured mesh with UV coordinates and alpha transparency. |
| `crossover_approved.py` | Builds the approved Ronaldo silhouette mesh and maps the supplied image onto it. |
| `reference_crossover.py` | Supplies shared `key`, `plate`, `camera` and masonry helpers. It also contains an older independent draft. |
| `hd_spec.py` | Chooses the correct Eevee engine identifier across supported Blender versions and provides render validation helpers used by other scenes. |
| `crossover_faces.py` | Facial/shape data used by earlier crossover versions. |
| `crossover_spec.py` | Frame-independent timing formulas for an earlier 192-frame version. |
| `floating_spec.py` | Motion specification for the separate floating-Messi scene. |
| `messi_floating.py` | Separate 12-second floating-Messi scene; it is not the active action entry point. |
| `superhero_crossover.py` | Earlier crossover version retained for reference. |
| `REFERENCE_SEQUENCE.md` | Notes for a previous reference reconstruction. |
| `README.md` | Earlier packet overview. Use `ACTION_SEQUENCE.md` for the newest action. |

### Packet operation and documentation

| File | Responsibility |
| --- | --- |
| `action.sh` | Current Mac launcher for `build`, `preview` and `render`. |
| `ACTION_SEQUENCE.md` | Exact current choreography, frame ranges, commands and limitations. |
| `HOW_THIS_ANIMATION_WORKS.md` | Shorter explanation of the implemented clip. |
| `COMPLETE_ARCHITECTURE_AND_ANIMATION_GUIDE.md` | This deeper manual. |
| `run.sh` | Launcher for an earlier version. Use `action.sh` for the active clip. |
| `assets/PROVENANCE.json` | Origin and SHA-256 fingerprint of the bundled artwork. |

One technical wrinkle: `crossover_sprites.py` still imports symbols from `crossover_spec.py` because its older optional rig modes use them. The active action calls the grid/static paths and does not use the old pose timing, but the file must remain in the packet until that import is refactored. Treat it as an import-time dependency and legacy timing source, not the active action specification.

The packet's older `README.md` and `run.sh` describe the 192-frame version. For the current 260-frame scene, use this document, `ACTION_SEQUENCE.md`, `action.sh` and `action_crossover.py`.

### Active assets

| Asset | How it is used |
| --- | --- |
| `messi-omni-matched.png` | Approved Messi/Omni-Man body, face, cape and legs. Native geometry replaces the folded arms during the throw. |
| `action-tumble.png` | Mbappe/Turtle airborne body used for grip, flight, impact and recoil. |
| `action-defeated.png` | Exhausted kneeling reaction after the impact. |
| `action-point-right.png` | Exhausted side-profile/three-quarter pose pointing screen right. |
| `ronaldo-approved.png` | Your supplied Ronaldo/Superman artwork, preserved as the approved final reveal. |
| `action-city.png` | Reconstructed clean city plate for the throw/flight/hover shots. |
| `action-warehouse.png` | Reconstructed clean impact and reaction environment. |
| `reference-doorway.png` | Reconstructed doorway/city plate for Ronaldo's reveal. |

Older pose files remain because older scene versions still reference them. An asset being present does not mean the newest scene uses it.

## 6. How the backgrounds were created

The supplied video frames established the composition: building positions, wall perspective, horizon, doorway and color palette. Characters and interface elements obscured parts of those images. Image generation reconstructed the missing areas and produced clean plates:

```text
reference frame
    -> identify background geometry and palette
    -> remove character/player controls
    -> infer obscured sky, wall, floor or doorway
    -> create clean 16:9 plate
    -> save as PNG in assets/
    -> map PNG onto a Blender plane
```

They are reconstructions, not exact recovered pixels. A hidden wall cannot be recovered from a single image; it must be inferred.

`reference_crossover.py` creates a 16-by-9 plane with `plate()`. It assigns an emission material so the image keeps its drawn color without depending on scene lights. UV coordinates map the four corners of the PNG to the four plane corners. `backdrop()` in `action_crossover.py` selects the correct plate for each shot and adds overscan so camera shake or a pan does not reveal an empty edge.

### Making your own background

1. Choose a clean reference frame with the correct camera angle.
2. Write down its horizon, vanishing direction, subject position and palette.
3. Generate or paint an empty plate with no character, text or controls.
4. Use 16:9 at sufficient resolution; 1920×1080 is a practical minimum.
5. Put it in both canonical and packet `assets/` folders.
6. Record its origin and hash in `assets/PROVENANCE.json`.
7. Add its filename to `backdrop()` or a new shot-specific asset map.
8. Render the first, middle and last camera positions to confirm the plate covers the frame.

For real depth, split the background into layers: foreground rubble, midground wall, distant buildings and sky. Put the layers at different Y positions and move the camera slightly. Near layers then travel faster than far layers, producing parallax.

## 7. How the characters were created

### Messi and Mbappe

Separate transparent PNG poses were generated in the approved cel style. A useful prompt defines:

- identity and costume;
- exact body pose and screen direction;
- facial expression;
- camera/framing;
- transparent background;
- invariants such as “no smile” or “entire pointing finger inside frame.”

One image cannot show every unseen angle. A frontal drawing does not contain a side profile, the back of a shell or a correctly bent hidden arm. This is why the project uses multiple pose drawings.

### Ronaldo

The supplied Ronaldo art is mapped to a custom silhouette mesh in `crossover_approved.py`. The mesh follows the visible outline instead of showing the whole rectangular source image. Its triangle faces are stored explicitly for predictable behavior across Blender versions.

### How transparency works

`crossover_sprites.py` builds a material with:

```text
PNG color -> emission shader
PNG alpha -> threshold -> mix transparent and visible shaders
```

The threshold removes faint generator halos. The source image is also packed into the `.blend`, so the editable scene can carry its images after construction.

Packing is a snapshot. If you edit a source PNG after the `.blend` was built, the already-packed copy inside that `.blend` may still show the old art. Rebuild the scene from `action_crossover.py` after changing an asset.

## 8. How a PNG becomes a Blender character

The `sprite()` function performs five jobs:

1. It loads and packs the image.
2. It creates a flat mesh in the X/Z picture plane.
3. It creates UV coordinates from 0 to 1.
4. It assigns the image/alpha material.
5. It optionally creates a dense 40×24 grid for local deformation.

A static sprite has four vertices. A deformable sprite has 1,025 vertices:

```text
(40 + 1) × (24 + 1) = 1,025
```

The extra vertices do not create new artwork. They only give Blender places to bend the existing pixels.

The `artwork()` helper preserves the PNG's aspect ratio:

```python
display_width = display_height * image_pixel_width / image_pixel_height
```

That prevents a face from being widened merely because a requested box used different dimensions.

## 9. The coordinate system

The active cameras look along Blender's Y axis.

```text
X = screen left/right
Z = screen up/down
Y = depth/layer order
```

Characters and effects use slightly different Y values so they layer correctly. The background is behind the characters; native arms or flashes sit in front. Rotation around Y looks like a 2D tilt in the finished frame.

Each shot is staged around a different X offset, approximately 40 scene units apart. In Blender's free viewport you can see several sets next to each other. The active camera and timeline markers ensure only one set appears in the render.

### Local coordinates, world coordinates and pivots

Every mesh vertex begins in **local coordinates**, relative to its object origin. Moving the object changes its world transform without rewriting every local vertex. Parenting adds another layer: a child's final world transform includes its parent's location, rotation and scale.

For a limb, put the object origin at the joint that should rotate:

```text
upper-arm origin -> shoulder
forearm origin   -> elbow
hand origin      -> wrist
```

If the origin is in the middle of the image, rotating the arm makes it orbit incorrectly. The native throw arm avoids this by generating capsule geometry along local +X, placing its origin at the starting joint and rotating/scaling it toward the next joint.

The difference matters during validation. A vertex's local position is converted through `matrix_world` before comparing it with a world-space grip or floor contact.

## 10. How the shot timeline works

At the top of `action_crossover.py`:

```python
FPS = 30
END = 260
CUTS = (
    ("throw", 1, 13),
    ("city tumble", 14, 32),
    ...
    ("reveal", 209, 260),
)
```

`FPS` tells Blender to play 30 frames each second. `END` sets the final frame. `CUTS` assigns each continuous range to a named camera. `PREVIEWS` selects beginning, middle and end frames from every shot.

Timeline markers switch the active camera at each shot's start. This is effectively an edit timeline constructed inside one `.blend`.

The current beats are:

| Frames | Seconds | Beat |
| --- | ---: | --- |
| 1–5 | 0.00–0.17 | Mbappe held upside down by the ankle |
| 6–10 | 0.17–0.33 | Accelerating swing |
| 11–13 | 0.33–0.43 | Release and follow-through |
| 14–43 | 0.43–1.43 | Flight from city toward wall |
| 44–64 | 1.43–2.13 | Stylized impact close-up |
| 65–109 | 2.13–3.63 | Recoil, fall and Messi arrival |
| 110–146 | 3.63–4.87 | Messi hover close shot |
| 147–175 | 4.87–5.83 | Defeated Mbappe looks up |
| 176–208 | 5.83–6.93 | Arm lifts and points right |
| 209–260 | 6.93–8.67 | Ronaldo silhouette and reveal |

The start time of Blender frame `f` is `(f - 1) / FPS`. At 30 fps, one frame lasts 33.3 ms and a two-frame impact accent lasts about 66.7 ms.

## 11. How the ankle throw works

`action_motion.py` is the most reusable example of good motion architecture because it separates motion math from Blender scene construction.

`ThrowPose` stores:

```text
shoulder, elbow, grip, victim center, victim angle, scale, held/released
```

For frames 1–10, the ankle is attached exactly to the same grip target used by Messi's hand:

```text
victim center = grip - rotated ankle landmark
```

If the victim rotates, the local ankle offset rotates too. Subtracting that transformed offset places the ankle back at the hand.

The arm uses a simple two-link inverse-kinematics calculation. Shoulder and grip are known. The intersection of two circles finds an elbow that leaves both arm segments 1.4 units long. `action_art.py` then places and rotates the sleeve capsules between shoulder → elbow → grip.

At frame 11, the victim releases. Position and velocity are continuous across the release boundary. After release:

```text
x(t) = release_x + velocity_x × t
z(t) = release_z + velocity_z × t - 0.5 × gravity × t²
```

The hand follows through and the fingers open. This relationship is why the throw now reads as one cause and effect rather than a character moving independently after a gesture.

## 12. How other motion is made

### Whole-object transforms

The main script keyframes:

- `location` for travel and hovering;
- `rotation_euler` for tumble or camera roll;
- `scale` for moving toward or away from the camera;
- `hide_render` for pose changes and effect timing;
- camera `ortho_scale` for zoom/framing.

The shared `key()` helper sets a property and inserts a Blender keyframe.

Many loops in the current scene explicitly insert values at every integer frame. Therefore there is already a transform sample for each rendered frame. Blender's F-curves mainly describe the property between those samples and at subframes. That produces smooth card travel, but it does not redraw anatomy inside the card.

### Shape keys

A shape key stores an alternate set of mesh vertex positions. Blender blends between the neutral and alternate positions. The scene uses them for:

- cape ripple;
- landing compression;
- lifting the pointing arm while keeping the head fixed.

Weight masks select a region by its normalized UV-like position. This is useful for small changes. Large anatomical changes require separate layers, a rig or another drawing.

The first shape key is the **Basis**: the neutral vertex layout. Each target shape stores alternate vertex positions. A value of 0 shows the Basis; a value of 1 applies the full target. Protecting the head means the head vertices must be identical in both layouts.

### Procedural secondary motion

Sine waves create repeating hover and cape movement. Exponentially decaying motion gives landings or impacts a quick shake that settles. Procedural curves draw lightning and speed lines. Small triangle meshes become impact debris.

### Camera motion

Each shot has an orthographic camera. Orthographic projection keeps flat drawings from distorting with depth. Camera position, scale and roll add energy. The pointing camera moves right and the Ronaldo camera begins with the same directional motion so the gesture motivates the reveal.

Orthographic projection and emission materials are intentional cel-animation choices: objects do not shrink naturally with camera distance, and textures do not react to realistic lighting. They provide visual consistency, but they also remove depth cues. A perspective camera, separated depth layers, controlled lights and shadows create more dimensional motion.

The point-to-Ronaldo move is a matched directional edit across two sets that are 40 units apart. The camera is not continuously traveling through one complete building.

## 13. Why it can still look stiff

The scene really does render every frame. It looks less lifelike because the character art often stays unchanged inside those frames.

| Current limitation | What the viewer perceives |
| --- | --- |
| One PNG for a whole body | Body moves like one card |
| Few distinct poses | Movement jumps between readable stills rather than flowing anatomy |
| No full skeleton/skin weights | Elbows, shoulders, hips and spine do not articulate naturally |
| Flat orthographic sprites | Little depth rotation or foreshortening |
| Limited facial poses | Emotion stays fixed during a shot |
| Interpolation without breakdown poses | Motion can feel floaty or mechanical |
| Little overlap/drag | Cape, shell, head and limbs stop together instead of following weight |
| No true contact deformation | Wall/floor impact has effects but limited body compression |

Adding more frames alone will not fix these issues. If the exact same PNG is translated across 60 frames, it is smoother translation of the same card.

## 14. The four upgrade levels

### Level 1 — improve the existing 2.5D cutout

Use the current system, but add better key poses and timing. This is the fastest improvement.

- Add anticipation before a major action.
- Add a clear contact pose, release pose and follow-through.
- Add overshoot and settle instead of stopping instantly.
- Animate on arcs rather than straight lines.
- Offset cape, head and shell by two to four frames.
- Add one or two breakdown poses between extremes.
- Use fewer generic flashes and stronger readable silhouettes.
- Add motion blur only after poses read clearly.

Best for: shorts, narration inserts, dramatic reveals and shots under about ten seconds.

### Level 2 — layered 2D puppet

Create separate transparent artwork for:

```text
head
torso
upper arm L/R
forearm L/R
hand L/R
thigh L/R
shin L/R
foot L/R
cape front/back
shell or costume overlays
eyes, brows and mouth poses
```

Place each layer on its own Blender plane. Parent parts through an armature or empties. Put pivots at shoulder, elbow, wrist, hip, knee and ankle. Add mesh deformation around joints so rotations do not look like paper hinges.

This creates true per-limb animation while retaining your generated cel artwork.

During blocking, key only the major storytelling poses. If you key every property on every frame too early, the Graph Editor becomes crowded and timing changes become difficult. Once the keys, contacts and arcs work, add breakdowns and smaller overlapping motion.

Best for: this channel's current style when you want more motion without modeling full 3D characters.

### Level 3 — hand-drawn or Grease Pencil animation

Draw key poses, breakdowns and in-betweens. At 30 fps you do not need 30 unique drawings each second. Traditional animation often holds each drawing for two frames, producing 15 drawings per second, and uses ones for fast action.

Example for a one-second throw:

```text
frame 1     anticipation key
frame 5     deepest wind-up
frame 8     fast passing pose
frame 10    release key
frame 12    overshoot
frame 18    recovery
frame 24    settle
frame 30    held final pose
```

The most important drawings are the keys and breakdowns. Software can interpolate some transitions, but an animator controls the silhouette and spacing.

Best for: close-ups, exaggerated superhero action and shots whose appeal depends on drawn anatomy.

### Level 4 — fully rigged 3D characters

Build or obtain legal character models, create skeletons, skin meshes with weights, add facial controls, cloth/cape simulation and lighting. Use inverse kinematics for hands/feet, constraints for contacts, and optionally retarget motion capture.

Best for: long sequences, rotating cameras, repeated characters and many angles.

This requires more setup but is the only level that naturally supports viewing a character from arbitrary directions.

A typical full-3D pipeline is:

```text
modeled or licensed mesh
 -> retopology
 -> UV unwrap and textures
 -> armature
 -> skin weights
 -> facial shape keys/controls
 -> IK/FK controller rig
 -> hand animation or motion-capture retarget
 -> contact/foot-slide cleanup
 -> cape/cloth and collision
 -> perspective camera, lighting and compositing
```

A single PNG cannot be converted into all of that unseen geometry automatically. An AI-generated 3D model can provide a starting mesh, but it still needs topology, rigging, weights, materials and animation cleanup.

## 15. Recommended path for this channel

For the next few videos, use a hybrid:

```text
wide/explainer shots       current 2.5D cards and parallax
medium acting shots        layered 2D puppet
important impact closeups  4–8 hand-drawn/generated key poses
complex rotating action    rigged 3D character or prebuilt legal asset
```

This avoids turning every ten-second insert into a month-long 3D project while improving the shots viewers notice most.

## 16. Making motion feel real

Realistic motion is built from observable principles.

### Weight

A heavy body accelerates and decelerates visibly. Show the force starting in the hips/torso, then reaching the arm. After impact, the body compresses before rebounding.

### Arcs

Hands, feet and heads usually travel along curves because limbs rotate around joints. Plot important positions and avoid accidental straight-line movement.

### Spacing

Timing says how long an action takes. Spacing says how far the object moves between each frame. Increasing spacing means acceleration; decreasing spacing means deceleration.

```text
even spacing:       |  |  |  |  |    constant speed
ease out:           || |  |   |     accelerating
ease in:            |   |  | ||      decelerating
impact:             | |     |||      fast arrival, compressed stop
```

### Anticipation

Move briefly opposite the main action. A throw reads better if the arm/body loads before release.

### Follow-through and overlap

The throwing hand continues after release. The cape and mask tails react later. The head, torso and shell should not all reverse on the same frame.

### Contact

Lock contact points. A held ankle must occupy the same world position as the hand. A planted foot should not slide. A body pinned to a wall should not drift through it.

### Silhouette

Pause at important frames and view the character as a black shape. If the grip, point or defeat is not understandable without details, improve the pose.

### Camera motivation

The camera should respond to the action: follow the thrown body, shake on impact, hold for emotion, then move in the direction of the pointing hand.

## 17. Blender interpolation and keyframe control

Blender normally interpolates between keyframes. The default Bezier interpolation can add soft ease-in/out, which is useful for hovering but can make impacts mushy.

Use interpolation deliberately:

| Motion | Suggested interpolation |
| --- | --- |
| Held pose | Constant |
| Mechanical camera move | Linear or carefully eased Bezier |
| Hover/settle | Bezier or sine formula |
| Fast release/contact | Linear through contact, then sharp ease/overshoot |
| Hand-drawn stepped poses | Constant, with drawings held for 1–2 frames |

In code, you can change a keyframe's interpolation after inserting it:

```python
for curve in obj.animation_data.action.fcurves:
    for point in curve.keyframe_points:
        point.interpolation = "BEZIER"  # or LINEAR / CONSTANT
```

For production, select interpolation per action rather than setting every curve globally.

Blender stores animated property curves as **F-curves**. The Dope Sheet is best for moving whole poses earlier or later. The Graph Editor is best for changing acceleration, overshoot and easing. Check individual X/Z curves when a character takes an accidental detour or floats through an impact.

## 18. How to edit the current animation safely

### Change the duration or cuts

Edit `FPS`, `END` and `CUTS` in `action_crossover.py`. Every frame from 1 through `END` must belong to exactly one cut. Update tests and documentation when timing changes.

### Move a character

Find the relevant frame loop inside `build()`. Change X for screen direction, Z for height and Y only for layer order. Render the start, middle and end frames of that loop.

### Change a pose image

Add the transparent PNG to canonical and packet assets. Update the asset selection in `build()`. Preserve aspect ratio and confirm alpha edges in a real render.

### Change a facial expression

Use a new pose asset or separate face layers. Do not expect whole-card transforms to change a smile into defeat.

### Change the throw

Edit constants or formulas in `action_motion.py`, then run `tests/test_action_motion.py`. Keep ankle contact through the held frames and velocity continuity at release.

### Change native arms/effects

Edit `action_art.py`. Verify the actual rendered palm still touches the ankle, speed lines are hidden outside their shot and foreground geometry is layered in front of the torso.

### Change the camera

Edit camera position or `ortho_scale` in `action_crossover.py`. Increase background overscan before large pans. Render the first and last frame of the move to catch exposed edges.

### Change the art deformation

Edit the region weights in `artwork()`. Use normalized `u`/`v` coordinates. Add a validation that protected regions such as the head do not move.

## 19. Creating a new scene from scratch

Use this repeatable sequence.

### Step 1: write the beat sheet

Describe only visible actions:

```text
0.0–0.4 s: character loads weight and grips target
0.4–0.7 s: fast action and release
0.7–1.2 s: target travels on an arc
1.2–1.5 s: impact and compression
1.5–2.5 s: reaction and emotional hold
```

### Step 2: choose the animation level

Decide whether each shot needs a whole-card sprite, layered puppet, drawn poses or 3D rig. Do this before generating artwork.

### Step 3: design the shot list

For each shot record:

```text
start/end frame
camera size and angle
background
character pose(s)
contact points
main movement arc
secondary motion
transition into next shot
```

### Step 4: create clean assets

Generate or draw characters on transparent backgrounds and environments without characters. Use consistent outline width, lighting direction, palette and proportions.

### Step 5: write pure motion first

For contacts, trajectories or reusable timing, make a Blender-independent module like `action_motion.py`. Test important invariants before building visual geometry.

### Step 6: build one shot

Create its backdrop, camera, characters and keyframes. Render three diagnostic frames. Do not build all nine shots before checking the first one.

### Step 7: add secondary motion

Add cape drag, mask-tail delay, camera response, debris and lighting accents after the primary action reads clearly.

### Step 8: validate structure and visuals

Run tests, build the `.blend`, render diagnostics and inspect actual images. A passing test does not prove that a pose looks good.

Sparse preview stills do not prove motion continuity. Before the expensive full-resolution render, render the entire sequence at 960×540 or another low resolution, encode it at the final fps and watch it at normal speed and frame by frame.

### Step 9: full render and encode

Render PNG frames to a fresh directory. Decode the resulting MP4 and confirm frame count, frame rate and resolution.

## 20. Build, preview and render lifecycle

On the Mac, from the packet folder:

```bash
bash action.sh build
```

This launches Blender in background mode, runs `action_crossover.py`, validates the scene and saves:

```text
action-output/action-crossover.blend
action-output/motion-report.json
```

It does not render every frame.

```bash
bash action.sh preview
```

This creates a new timestamped output folder with selected diagnostic PNGs.

```bash
bash action.sh render
```

This creates a new timestamped folder containing all 260 PNG frames, the `.blend` and the report. The active action launcher does not resume a partial render.

To open the scene:

```bash
open -a Blender action-output/action-crossover.blend
```

Inside Blender choose **View → Cameras → Active Camera**, set frame 1 and press Play. Viewport playback may be slower than 30 fps; that does not change the final rendered timing.

## 21. Turning PNG frames into video

The Mac packet renders silent PNGs. On Windows, the studio assembler verifies a consecutive frame sequence and invokes FFmpeg:

```powershell
.\studio.ps1 assemble PATH_TO_FRAMES --output .studio/renders/MY-SHOT --fps 30
```

Use `--fps 30` for this sequence. The assembler's default is 24 fps. Passing the wrong value changes playback speed.

The output contains:

```text
video.mp4
assembly.json
```

Adding narration is a separate editing step. The Blender scene itself is silent.

## 22. What validation proves

`validate()` in the Blender script checks scene structure and important motion facts:

- correct camera at cut boundaries;
- valid resolution and final frame;
- character mesh/material presence;
- ankle and intended grip agreement;
- actual visible palm and ankle agreement;
- pointing finger remains right of the head and inside frame;
- head vertices remain unchanged by pointing-arm deformation.

`tests/test_action_motion.py` checks the pure throw math:

- held ankle contact;
- constant upper-arm and forearm lengths;
- correct left-to-right swing;
- continuous release position and velocity;
- continued rightward travel after release;
- input validation.

`tests/test_action_sequence.py` checks:

- full 1–260 frame coverage;
- expected major cut starts;
- canonical/packet source parity;
- required PNG signatures and asset parity.

These checks prevent specific technical failures. They cannot judge acting, likeness, visual taste or whether the finished motion feels powerful. That requires rendered-frame and playback review.

`tests/test_crossover.py` primarily protects older crossover timing plus the approved Ronaldo mesh. It remains useful regression coverage, but it is not the main behavioral test for the active ankle-throw choreography.

## 23. The studio and Hermes architecture

The animation packet can run without the studio, but the repository contains a broader content system.

| Component | Role |
| --- | --- |
| `studio/core.py` | Episodes, explicit feedback, metrics, search and durable jobs. |
| `studio/hermes.py` | Creates bounded, immutable episode handoffs without calling a model. |
| `studio/episode.py` | Parses production scripts, packages episodes and assembles PNG frames into MP4. |
| `studio/review.py` | Checks script/source/audio agreement and creates review exports. |
| `studio/captions.py` | Aligns words and produces caption formats. |
| `studio/narration.py` | Guide narration timing and audio operations. |
| `studio/finish.py` | Validates and finishes opening video/audio/captions. |
| `studio/media.py` | Safe media/FFmpeg helpers. |
| `studio/dashboard.py` and `studio/web/` | Local production dashboard. |
| `studio.ps1` | Windows command-line entry to the studio. |
| `hermes-studio.ps1` | Starts isolated Hermes or prepares an episode handoff. |

Your explicit correction is stored in the local feedback database. A fresh Hermes handoff retrieves active corrections for that episode and selected document excerpts. This is context retrieval, not model retraining.

Hermes can coordinate an agent task after a provider is configured. It does not reduce tokens automatically, and it is not required for Blender. Token savings come from bounded handoffs, targeted retrieval and rerunning deterministic local code instead of asking a model to recreate work.

## 24. A practical learning plan

### Week 1: understand and modify

1. Build the current `.blend`.
2. Change one hover amplitude.
3. Change one camera zoom.
4. Render previews and compare them.
5. Restore or commit the preferred values.

### Week 2: create one original 2.5D shot

1. Write a two-second beat sheet.
2. Create one background and two transparent character poses.
3. Copy the scene pattern into a new Python file.
4. Animate location, rotation and scale.
5. Add anticipation, overshoot and secondary motion.

### Week 3: layered puppet

1. Split one character into head, torso and arm layers.
2. Set correct pivots.
3. Parent the parts.
4. Animate one reach with shoulder/elbow/wrist arcs.
5. Add eyes or mouth pose switching.

### Week 4: choose specialization

- Learn Grease Pencil if you want expressive drawn superhero animation.
- Learn rigging/weight painting if you want reusable 3D characters and moving cameras.
- Learn compositing and editing if you want to combine short hero shots efficiently into long documentary videos.

## 25. Quality checklist for every new shot

Before the full render, confirm:

- The action is understandable from silhouettes.
- The screen direction never reverses accidentally across a cut.
- Held objects and planted feet do not slide.
- The character anticipates, acts and follows through.
- Limbs follow arcs.
- Head, torso, hands and cloth do not all stop simultaneously.
- The face matches the required emotion.
- The camera move is motivated by the action.
- Background coverage survives every camera position.
- The first, contact, extreme and final frames have been rendered and inspected.
- The source and Mac packet match.
- The full frame count and fps are correct.
- The final encoded video decodes from beginning to end.

## 26. Common mistakes

**“I increased FPS, but it still looks stiff.”** More display frames do not create new anatomy or better poses. Improve key poses, spacing and articulation.

**“Blender shows three scenes beside each other.”** Those are separate shot sets arranged in one world. Enter active camera view to see the edit.

**“The animation is slow in Blender.”** Viewport performance is not the final video rate. Rendered frames encoded at 30 fps play at 30 fps.

**“The image has black or glowing edges.”** The input may lack true alpha or contain a faint halo. Inspect the PNG alpha and material threshold.

**“The character looks defeated only because I moved him down.”** Expression comes from the drawing or face rig. Use a defeated pose/expression asset.

**“The arm bends but the hand disconnects.”** Shoulder, elbow, hand and target were animated independently. Drive them from one shared target or use IK.

**“The camera pan exposes black space.”** The background plane has insufficient overscan. Enlarge it or reduce the move.

**“I edited the Windows source but the Mac did not change.”** Synchronize the portable packet and pull the new Git commit.

## 27. Where to start editing

If you want to change the existing clip, use this order:

1. Read `ACTION_SEQUENCE.md` for the active timing.
2. Read `action_crossover.py` from `FPS` through `CUTS`, then jump to `build()`.
3. Read `action_motion.py` to understand the throw contract.
4. Read `action_art.py` to understand native drawn geometry.
5. Read `crossover_sprites.py` to understand PNG meshes and alpha.
6. Change one shot only.
7. Run the focused tests.
8. Synchronize the Mac packet.
9. Build and render previews.
10. Review moving playback before committing a full render.

The strongest next improvement would be to create a layered Mbappe and Messi puppet for medium shots, while keeping the current generated poses for extremes and close-up expressions. That gives you substantially better life and control without requiring complete photorealistic 3D models.


## 28. Safe production cookbook

Use this order for every serious revision:

1. Preserve the previous render and choose a fresh output directory.
2. Edit the canonical files under `blender/`.
3. Run Blender-independent tests first.
4. Copy the exact active source and assets into the Mac packet.
5. Run packet parity tests.
6. Build the `.blend` and inspect structured validation.
7. Render grip, release, impact, reaction, point and reveal diagnostics.
8. Render and watch a low-resolution full-motion version.
9. Inspect timing in the Dope Sheet and curves in the Graph Editor.
10. Render the full sequence to a fresh folder.
11. Assemble it with explicit `--fps 30`.
12. Decode the output and confirm frame count, fps, resolution and duration.
13. Update `CURRENT_STATUS.md` and record durable choices in `DECISIONS.md`.

The current active action renderer does not support resume. Do not confuse it with older launchers in this repository that have different resume behavior.