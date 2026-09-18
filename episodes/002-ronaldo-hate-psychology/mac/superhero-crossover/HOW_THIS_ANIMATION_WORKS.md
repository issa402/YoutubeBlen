# How this animation is made — and how to change it

This is an illustrated **2.5D Blender animation**: character drawings are placed on editable meshes, arranged in front of illustrated backgrounds, and moved by Python code. Blender calculates and renders the frames. Codex writes and revises the code and uses image generation for selected artwork. Hermes is an optional separate agent launcher; it did not secretly create or animate this clip.

The creative target is your sequence: **Messi grips and throws Mbappe → Mbappe takes the impact → Messi approaches and hovers → a defeated Mbappe looks at him and points to his right → the camera reveals Ronaldo.** That causal order matters more than adding flashes to an unclear action. The main timeline is 260 frames at 30 fps, or about 8.67 seconds. This is a reconstruction of your reference, not automatic, frame-perfect replacement of its characters.

## 1. The files to understand first

Paths in this table start at the repository root, except the packet-local entry points explicitly marked below.

| File | What it does |
| --- | --- |
| `blender/action_crossover.py` | Builds this action sequence: artwork, shots, transforms, shape deformation, effects, validation and frame output. This is the main source to study. |
| `blender/action_motion.py` | Pure Python throw calculations: shoulder, elbow, grip, attached ankle, release and outgoing trajectory. It can be tested without starting Blender. |
| `blender/action_art.py` | Creates editable cel sleeve/glove geometry, opening fingers, debris and speed lines. It uses the positions calculated by `action_motion.py`. |
| `blender/crossover_sprites.py` | Loads character PNGs, creates textured meshes, maps the image onto them and hides transparent areas. |
| `blender/crossover_approved.py` | Places the original approved Ronaldo image on a mesh traced around his silhouette. |
| `blender/reference_crossover.py` | Supplies reusable image-plate, camera and keyframe helpers. Its older standalone sequence is a separate draft. |
| `blender/hd_spec.py` | Includes the render-engine selection helper shared by the packets. |
| `blender/assets/` | Character and background image inputs used by the canonical scripts. |
| `episodes/002-ronaldo-hate-psychology/mac/superhero-crossover/` | Portable Mac packet. It contains copies of the scripts and assets needed to run this scene with Blender's Python. |
| `action.sh` inside that packet | Mac Terminal launcher. `build` creates a `.blend`; `preview` renders selected stills; `render` renders all frames. |
| `ACTION_SEQUENCE.md` inside that packet | Current sequence notes, timing and asset direction. |
| `assets/PROVENANCE.json` inside that packet | Records where bundled artwork came from and its SHA-256 fingerprint. |

The canonical source and Mac packet must stay synchronized. Editing just `blender/action_crossover.py` will not change the separate copy that `action.sh` launches. The tests check important source and asset parity.

## 2. How the characters and backgrounds were made

**Ronaldo:** you supplied the approved Superman-style illustration. Its PNG is preserved as `ronaldo-approved.png`. The code traces his visible outline with image-coordinate points, fills that outline with triangles, and maps the original image onto those triangles. The surrounding rectangular city image therefore does not have to appear with him. His face is from your supplied image; it is not a new face sculpted in Blender. The final render still filters the texture when scaling it.

**Messi and Mbappe:** image generation produced separate cel-style character drawings guided by your approved visual direction. The current action uses `messi-omni-matched.png` and `action-tumble.png`, plus the newly generated `action-defeated.png` for the exhausted reaction and `action-point-right.png` for the rightward pointing pose. Earlier crouch/profile images remain in the asset folder for previous drafts. Some poses need separate artwork because one frontal drawing does not contain a hidden side, a bent elbow or an expression that was never drawn. The script determines which pose files are actually used; an older image remaining in `assets/` does not mean it appears in the latest cut.

**Backgrounds:** representative frames from your screen recording supplied the composition, palette and architecture. Image generation reconstructed clean city, warehouse and doorway plates, removing characters and filling the obscured areas. The resulting files include `action-city.png`, `action-warehouse.png` and `reference-doorway.png`. They are new reconstructions; the hidden wall or sky is inferred, so these are not exact original background pixels. Your recording's player controls and audio are not part of the scene.

An image-generation prompt for this workflow describes five things: the approved reference, character identity and costume, specific pose or expression, framing, and a transparent background for a character or a clean empty background for a set. A useful pose request is concrete: “side view, exhausted expression, shoulder low, index finger extending screen right.” “Make it epic” alone does not define the anatomy or action.

The image generator returns artwork. It does **not** return Blender motion, a working skeleton or the entire video. Python supplies the timing and movement afterward.

## 3. How a flat PNG becomes an editable Blender object

The sprite helper performs these steps:

1. Load the PNG and pack it into the Blender file, so the saved scene carries its image data.
2. Create a flat mesh facing the camera. A simple sprite can use one rectangle; an animated grid uses 40 by 24 cells, giving it enough vertices to bend locally.
3. Assign UV coordinates. These tell Blender which point of the image belongs on each vertex or face corner: `u=0` is the left edge and `u=1` is the right edge.
4. Connect the image color to an emission material, preserving the flat illustrated colors without requiring a complex lighting setup.
5. Use the PNG's alpha channel to make the outside of the drawing transparent. The helper thresholds very faint alpha to remove unwanted translucent fringes.

The dimensions preserve the image's aspect ratio. For example, a 1,000-by-1,500 image displayed six scene units tall must be four units wide. Stretching that image to six units wide would also widen the face and body.

In this scene, X is the horizontal screen direction and Z is vertical. The camera looks along Y. Small differences in Y place one drawing in front of another. This is why an arm, character, background and flash can overlap without becoming one flattened image.

## 4. Where the motion actually comes from

There are several different kinds of motion working together.

**Object transforms move the whole drawing.** Changing `location` translates it, `rotation_euler` rotates it, and `scale` changes its size. These make the body fly, tumble, settle or hover. For this camera arrangement, rotation around Y tilts the drawing within the picture.

The shared helper is essentially:

```python
def key(obj, field, value, frame):
    setattr(obj, field, value)
    obj.keyframe_insert(field, frame=frame)
```

For example, this isolated teaching snippet would move an existing object called `character` to the right between frames 1 and 16:

```python
key(character, "location", (-2.0, -0.5, 0.0), 1)
key(character, "location", ( 2.0, -0.5, 0.0), 16)
```

That is only translation. A convincing throw also requires a visible grip, the correct release instant, a trajectory continuing from that release, and an impact at the end. If the victim starts flying before the hand lets go, or suddenly changes screen direction at a cut, adding more keyframes will not fix the story. Those relationships must be designed and checked.

**The throw now has a shared grip target.** `action_motion.py` defines a frozen `ThrowPose` dataclass: a small record containing the shoulder, elbow, grip, victim's center, angle, scale and whether the grip is still held. `throw_pose(frame)` calculates that record for a requested frame. The main script places Mbappe from this result, while `action_art.py` places Messi's arm and hand from the same result. They do not independently guess where the contact should be.

For frames **1–10**, a calibrated ankle landmark on the five-unit-high tumble drawing is attached to the grip. The calculation is:

```text
victim center = grip position - rotated ankle offset
```

That subtraction means changing the body's angle still keeps the ankle at the hand. Frames 1–5 hold the pose; frames 6–10 accelerate the swing. **Frame 11 releases the ankle.** The outgoing path starts from the release position and its calculated velocity, then applies stylized gravity. The fingers open while the hand follows through. This is choreographed motion, not a physics simulation of a full body.

**Two-link inverse kinematics keeps the arm connected.** “IK” means calculating joint positions from a desired endpoint. The helper fixes the shoulder and grip, then calculates the elbow so the upper arm and forearm each remain 1.4 units long. `action_art.py` draws rounded sleeve/glove shapes, places each segment at its starting joint, turns it toward the next joint and gives it the required length. The approved face, cape and legs remain image artwork; new torso/arm marks are editable Blender geometry. This avoids treating the whole folded-arm image as if it already contained a throwing arm.

The saved `motion-report.json` contains `inspection.grip_contacts`. Blender checks the actual transformed ankle against the intended grip for every held frame and raises an error if the X/Z distance exceeds `0.0001` scene units. This tests attachment in the picture plane. It does not prove the illustrated hand looks natural; that still requires inspecting rendered frames.

**Shape keys bend part of the image mesh.** A shape key stores a second set of vertex positions. Its value blends between the original grid and the deformed grid: 0 uses the original positions, 1 uses the alternate positions. The script applies weights to specific regions so cape edges can move while the face stays steady. Similar bounded deformation can add a small arm extension or landing compression. It cannot invent a convincing rear view from a front-facing image.

The revised pointing image has Mbappe's head on the **left** and his arm extending **right**. The pointing shape key weights the right-hand region and leaves the head region unchanged. Here the alternate shape lowers the arm, so the key starts at 1 and drops to 0 over **frames 176–183**: the lowered arm lifts into the drawn pointing pose. The defeated expression comes from the new image, rather than trying to turn a smiling face into a tired one by moving the entire card.

**Curves control the character of the movement.** The smoothstep function used here is:

```python
def smooth(value):
    value = min(1.0, max(0.0, value))
    return value * value * (3 - 2 * value)
```

It changes a normalized progress value from 0 to 1 with a gentle start and stop. A sine wave provides small repeated hover or cape motion. A decaying wave can make a landing settle rather than bounce forever. Different beats need different timing: an impact should be abrupt; a threatening hover can be nearly still.

**Effects reinforce movement.** Short flashes, drawn energy curves, impact accents and restrained camera shake emphasize a release, hit or reveal. `action_art.py` also creates small polygon debris pieces whose paths spread outward and fall, plus animated speed-line curves. These are procedural Blender geometry, not modifications to the PNGs. Effects should follow the action rather than hide an unclear pose. Rendering this scene creates silent picture frames; the scene does not generate or attach a voice track.

## 5. How the shots become one sequence

The main script sets the frame rate and end frame. Frame 1 represents the start, frame 31 is one second later, and 260 displayed frames at 30 fps last about 8.67 seconds. The last frame starts at 259/30 seconds; it still occupies its own frame interval.

Each shot has a camera. Timeline markers bind cameras to cut frames. The renderer uses the active camera for each frame, so separate staged sets become a single edited sequence. This explains the multiple scenes you saw beside one another in the 3D viewport: they are shot setups in one Blender scene, arranged apart so they do not overlap. They are not meant to appear simultaneously in the final picture.

The cameras are orthographic, which keeps the cel artwork's proportions stable. Changing `ortho_scale` changes framing: a smaller value crops closer. Moving the camera shifts the visible part of the set. In the revised sequence, the pointing camera moves right during frames **201–208**. After the cut at **209**, the reveal camera continues a rightward move into Ronaldo and settles by **217**. This is a matched directional move across two separate shot setups, not one continuous camera flying through a complete 3D building. It connects the pointing direction to the reveal while retaining the approximate reference staging.

The intended performance has three distinct stages after the impact: Mbappe is visibly beaten, Messi controls the space while hovering, and Mbappe directs attention toward Ronaldo. Holding those readable poses briefly is often more effective than moving everything continuously.

## 6. Run it on your Mac, then press Play

Run these commands in **macOS Terminal**, not in Blender's Python Console:

```bash
cd "$HOME/Desktop/Movies/YoutubeBlen"
git pull --ff-only
cd episodes/002-ronaldo-hate-psychology/mac/superhero-crossover
bash action.sh build
open -a Blender action-output/action-crossover.blend
```

`build` executes the Python script inside Blender, constructs the objects and keyframes, and saves the editable file. It does not render the entire movie. Opening the `.blend` afterward lets you inspect it interactively.

Inside Blender:

1. Make sure you are viewing the active camera: **View → Cameras → Active Camera**. This avoids the need for a Mac numpad.
2. Set the timeline to frame 1. Use the timeline's **Play triangle** to play or pause.
3. Keep viewport overlays disabled to hide grids, outlines and helper lines. Overlays do not appear in a normal render anyway.
4. If Solid view shows rough material/alpha results, a rendered still is the reliable picture check. Use **Render → Render Image** for the current frame. Material Preview is optional and can take time to compile shaders.

The saved viewport starts in Solid texture mode to avoid forcing material compilation immediately. Viewport playback may drop frames or run slowly; it is not proof that the encoded video will stutter.

For selected diagnostic stills, return to Terminal in the same packet folder:

```bash
bash action.sh preview
```

For the complete 1080p PNG sequence:

```bash
bash action.sh render
```

The launcher prints the actual output folder and a log path. Preview and render use new timestamped folders. `preview` is a set of stills, not a playable video. `render` creates consecutively numbered PNGs, not an MP4. It also saves a `.blend` and a motion report. The current action renderer does not automatically resume a partially completed frame directory.

The Mac requires Blender and permitted Git operations, not a separate installation of Python packages, Hermes, image-generation tools or the Windows environment. The earlier Mac SIGTRAP crash is not diagnosed by a successful Windows render; if Blender still quits, preserve that run's log and the Mac crash report.

## 7. How a playable MP4 is produced

On Windows, the existing studio assembler uses FFmpeg to encode consecutive PNGs. For example, after permitted transfer of the Mac frames into `.studio/returned-action/frames/`, run this from the Youtube project root in PowerShell:

```powershell
.\studio.ps1 assemble .studio/returned-action/frames --output .studio/returned-action-video --fps 30
```

This creates `.studio/returned-action-video/video.mp4` and an assembly report. The destination must be new; choose a different output name for another attempt. Use the complete consecutive `frames/` folder, not sparse diagnostic `previews/`. Omitting `--fps 30` would use the assembler's 24 fps default and make this sequence play at the wrong speed.

Git transfers the source code and versioned artwork. Large `.blend`, render frames, MP4s, local AI environments and caches are ignored. Pulling this update therefore does not download the Windows Blender installation or all rendered media. Asset changes still add data; the exact transfer depends on which commits and files your Mac already has.

## 8. What Codex, skills and Hermes each do

**Codex is doing the work in this conversation.** It reads your reference and project files, writes Blender code, invokes image-generation tools where needed, runs local rendering/tests and reviews outputs. Blender renders the animation; the image tool produces selected drawings. A model's coding ability is separate from the render engine.

**Skills are reusable working instructions.** The project's `skills/creator-studio/SKILL.md` selects relevant workflows. The Blender motion inspection skill calls for checking cameras, timing, object motion and actual frames. The verification workflow checks code and runnable results. Loading a skill does not install a new AI model or automatically improve every frame.

**Hermes is an optional agent runtime already installed in an isolated Windows environment.** Its model can choose tools, receive their results and continue working. The project launcher is `hermes-studio.ps1`; context preparation is implemented in `studio/hermes.py`. Installed CLI/help and preparation behavior have been checked. Provider authentication and a live Hermes generation run have not been established for this animation. This clip was not produced by an unattended Hermes team.

**You do not need Hermes to run this animation.** `bash action.sh build` and Blender playback operate directly from the saved scripts and artwork. There is no live AI model required while Blender evaluates the keyframes or renders the pictures.

You can prepare a real task handoff without contacting a model:

```powershell
.\hermes-studio.ps1 -Episode 002-ronaldo-hate-psychology -Task 'Review the current animation code against the throw, impact, hover, defeated right-point and Ronaldo reveal sequence. Report concrete mismatches.' -PrepareOnly
```

The result includes the path of a unique text file under `.studio/handoffs/`. Read it to see exactly what Hermes would receive. It contains your task, active corrections for this episode, constraints and bounded document excerpts. It does not automatically import this whole Codex chat.

After separately setting up an authorized provider, removing `-PrepareOnly` runs that task through Hermes. The launcher defaults to a one-shot task with up to 20 tool-calling iterations. That limit bounds iterations, not dollars, token usage or guaranteed completion. See `tools/HERMES_WORKFLOW.md` for the installed integration's details.

## 9. What “learning” and “saving tokens” mean here

The studio remembers explicit corrections in `.studio/studio.sqlite3` and exports readable preferences. This command records the visual direction for future episode handoffs:

```powershell
.\studio.ps1 feedback 002-ronaldo-hate-psychology 'Show Messi gripping and throwing Mbappe before the impact. Then show Messi hovering, Mbappe defeated and pointing screen right, followed by the Ronaldo reveal. Preserve approved character identities.' --kind visual
.\studio.ps1 learn
```

`feedback` stores the note; **`learn` lists the stored feedback records**. It does not retrain a model or automatically fix a scene. Avoid recording the same correction repeatedly. To retire an obsolete correction, use `studio.ps1 revoke` with its returned feedback ID. Generate a fresh handoff after a change: an old handoff is an immutable snapshot.

Hermes also has its own memory/skill facilities, separate from this database. Those store context and reusable procedures; they do not change the underlying model's weights. We have not verified automatic audience learning, autonomous creative improvement, or an increase in earnings.

Token savings come from doing less unnecessary model work:

- Prepare a bounded episode handoff instead of pasting every repository and the entire chat. The default is at most 12,000 characters for our handoff, with the task and active corrections protected.
- Read the relevant files and selected logs. A character-based estimate is approximate and excludes Hermes' system prompt, tool definitions and later conversation.
- Rerun deterministic Python, Blender and FFmpeg commands. Those local computations do not themselves need model tokens, although asking an agent to inspect their outputs does.
- Reuse a tested procedure and approved artwork instead of repeatedly regenerating the same material.

No percentage saving or shared Codex-account quota saving has been measured. Headroom is a separate optional proxy for an isolated CLI setup; it has not compressed this Desktop conversation. Talking through Hermes does not inherently make the same model work free.

## 10. How to improve the next shot yourself

Work in this order:

1. **Write the observable action.** For example: “His hand grips the ankle until release; Mbappe continues screen right; the wall impact happens at the end of that flight.”
2. **Choose or create the required poses.** Check expression, hand shape and silhouette before animating. A smiling face will not read as defeated just because the body moves slowly.
3. **Change the code and synchronize the packet.** Start with one parameter: release timing, body position, camera framing or cape amplitude.
4. **Render the important frames.** Inspect the grip, release, impact, defeated expression, pointing hand and first Ronaldo reveal. Watch a short motion preview too; stills cannot prove continuity.
5. **Run structural checks, then the final render.** Check frame count, camera cuts, missing assets and source/packet parity. Decode the finished MP4 to verify it plays. Code tests cannot judge whether the throw looks convincing.
6. **Save the useful correction.** Update the project notes and explicit feedback, so the next task starts with the corrected direction.

For a future shot requiring a character to turn around, fight through many angles or move limbs freely, use a properly modeled and rigged 3D character or a fuller set of layered animation drawings. This current mesh-and-image approach is useful for controlled cel-style shots, but an ordinary PNG does not contain the unseen body geometry needed for unrestricted 3D animation.
