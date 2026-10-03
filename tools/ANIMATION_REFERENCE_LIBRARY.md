# Animation reference library and production routing

Recorded 2026-10-02; supplied recording filenames are dated 2026-10-03. This is a reference analysis and proposed workflow, not a claim that new animations or integrations have been built. Four new clips were sampled throughout, with denser samples for body/facial motion. Their audio has not been listened to or transcribed in this audit. Original authoring software cannot be established from rendered pixels.

## Find the references

The portable catalog is `animation-references/catalog.json`; contact sheets are beside it. Raw screen recordings remain local. Use the stable reference IDs in briefs instead of sending every video to every agent. Retrieve this guide and the selected contact sheet when needed; these files do not automatically load into every future chat.

| ID | File | Captured duration | Observed visual grammar | Production choice |
|---|---|---:|---|---|
| R01 | 20261003-0002-08.0937913.mp4 | 14.833 s, 445 frames, 30 fps | Caricature professor on stick body, slide board, laboratory backdrop, skeleton diagram, image swaps | HyperFrames + SVG/PNG layers |
| R02 | 20261003-0003-28.4169578.mp4 | 11.667 s, 350 frames, 30 fps | Armored 3D figure recovering on rock ledge; huge rock overhead; camera pulls back to reveal scale | Blender rig + environment + camera |
| R03 | 20261003-0006-32.9394945.mp4 | 9.367 s, 281 frames, 30 fps | Gold/pink wireframe-style people in cyan rooms; hand-to-face acting, facial changes, family tableaux, word captions | Blender rigged characters + wire overlay; HyperFrames captions |
| R04 | 20261003-0007-59.6956792.mp4 | 6.667 s, 200 frames, 30 fps | Football header illustration, zoom, top-down tactical board, moving markers/ball, labels, vertical format | Layered 2D art + HyperFrames tactical board; Blender only for complex performance |

Capture resolution is recorded in the catalog; it is not the source video's original resolution or animation drawing rate. The reference region may occupy only part of the screen recording. Exclude desktop notifications, platform UI, black margins and creator watermarks from our original production.

## R01 — illustrated presenter

Observed approximate beats: slide board/clothes at 0–2 s, lab around 2–6 s, skeleton board around 6–10 s, diagram zoom/label around 10–12 s, sports images near the end. These are sampled beat estimates, not measured frame-exact cut boundaries.

Build an original presenter with separate head, brows, eyes, mouth shapes, torso, upper/lower arms and pointer. Use SVG for limbs/board/arrows and images for backgrounds or photographs. Set pivots at shoulders, elbows and neck; animate joint rotations, blinks, head tilts and several mouth shapes. Use GSAP seekable timelines inside HyperFrames for board changes, push-ins, labels and gestures. Derive mouth cues from audio if lip sync is requested; random mouth swaps are not accurate lip sync. Asset design and expression quality matter more than scene complexity. High confidence in reproducing this visual class with a reusable template.

## R02 — full 3D body action and scale reveal

Observed: the character is low/prone, pushes up into a crouch, stands, changes stance, then appears much smaller as the camera retreats beneath the huge rock. We cannot infer whether the source used mocap, a game engine or manual animation.

Build rock ledge and overhang from meshes, displacement/noise and rock materials; reuse an appropriately licensed humanoid mesh. Add an armature (bone hierarchy) and skin weights (how vertices follow bones). Block prone, push-up, crouch, stand and step poses. Use hand/foot IK to hold contacts, then adjust hip weight shift and knee/elbow bends. Keyframe a camera dolly with target tracking and restrained atmospheric depth. Preview in Workbench/EEVEE before detailed textures. Mocap can seed get-up/walk actions, but retargeting and contact cleanup remain necessary. Python can assemble, key and validate the scene; a crude procedural human will not match a good character asset.

## R03 — wireframe emotional acting

Observed: opening close-up lowers a hand from the face and changes expression; around 4.5 s it cuts to family/tableau views. Gold figures, magenta figure, pale blue environments and bold changing words unify the piece. The wireframe appearance alone does not prove genuine 3D: stylized generated footage could imitate it.

For a controllable reconstruction, use reusable human rigs with facial shape keys (blink, brow, mouth and expression), articulated fingers, gaze targets and layered actions. Use clean quad topology with an edge overlay/duplicate wire mesh so the visible grid follows body deformation. Build a modular room/table/sofa. Apply gold and magenta materials with controlled glow and pale cyan background treatment. Animate hand release, breath, gaze and speaking/gesturing poses; reuse the same rigs across shots. Render characters in Blender, then assemble captions in HyperFrames/FFmpeg. This is feasible, but asset/face/hand work is a larger effort than R01/R04. A moving flat portrait will not deliver the same performance.

## R04 — football illustration plus tactics

Observed: roughly 0–2.6 s is the Ronaldo/opponent/ball header illustration with push-in and pose change; roughly 2.6–6.3 s is a tactical pitch with camera movement, player circles and labels, then a pitch-level transition. A notification overlays the later source frames and is not part of the requested aesthetic.

Make original layered player art: head, torso, upper/lower limbs and ball. Key takeoff, airborne lean, neck/head contact and follow-through. Use alternate poses for foreshortening rather than stretching one PNG. Draw the tactical pitch in SVG. Animate player/ball coordinates from a small event table, draw trails, labels and emphasis rings, and map the pitch group through pan/zoom transforms. HyperFrames is a strong match. If the shot requires turning around the player, create that short performance in Blender and composite it with the tactical graphic. Tie illustrative positions to actual evidence before presenting them as a match reconstruction.

## Older reference memory

| ID | Reference | Preserve | Production route and limits |
|---|---|---|---|
| P01 | Floating Omni-Man city image, 2026-09-15 | Messi identity, crossed arms, hover, city depth | Layered 2D/2.5D, cape rig, parallax; previous `mac/messi-floating/` packet |
| P02 | Approved Ronaldo/Superman image, 2026-09-16 | Approved face/costume, consistent cel palette across Messi and Mbappe | Character model sheet; front/side/three-quarter poses and expressions before action |
| P03 | Superhero ankle-throw reference, 20260917-0318-04.0378117.mp4 | Messi holds ankle and throws Mbappe; impact/drop; hovering approach; defeated Mbappe points screen right; camera reveals Ronaldo | True articulated 2D rig with replacement drawings, or toon-shaded 3D plus Grease Pencil accents. Source was unavailable at supplied TempState path in this audit; sequence is recovered from explicit user corrections and project records |
| P04 | Dark comic reference, 20260924-0207-57.8910603.mp4 | Purple/red city, strong silhouettes, dramatic dialogue angles, comic impact words, speed effects | Source sampled again across its 60.933 s capture. Toon 3D/Grease Pencil hybrid, carefully posed performances, halftone/ink treatment and timed impact typography |

Earlier four-second and extended crossover clips are successive references for P03, not independent mandatory styles. Current source is `blender/action_crossover.py`, `action_motion.py`, `action_art.py`; portable packet is episode 002 `mac/superhero-crossover/`. It uses layered 2.5D assets and native geometry, not a complete facial/body rig. `blender/rules_short_scene.py` and `rules_short_art.py` build stylized anonymous figures for the separate Same Standard commentary short. Neither implementation establishes a match to every reference above.

## Why more frames do not fix stiff movement

Output frame rate and performance quality are different. Thirty frames per second can display the same rigid pose moving across the screen. Natural performance needs anticipation, balanced contact poses, arcs, varying speed, overlap, facial acting and convincing silhouettes. Some excellent drawn animation intentionally holds drawings for two frames. Optical-flow interpolation cannot invent a coherent character rig or repair wrong choreography.

## Narration-first reference workflow

1. Ingest recording and reference separately. Hash them, probe streams and timestamps, preserve originals locally, detect screen/UI crops and generate proxies/contact sheets.
2. Label each reference: art, camera, choreography, edit rhythm, or exact performance timing. A style reference does not dictate the new narration duration.
3. Transcribe the creator's recording with existing faster-whisper. Draft using their intent; mark all rewrites. If narration changes, record/synthesize that new wording before locking animation.
4. Lock the final audio take. Align the approved transcript at word/phrase level; flag football names and uncertain matches for manual review. ASR word timing is not automatically exact forced alignment.
5. Make a shot manifest containing reference_id, audio_start/end, frame_start/end, visual_action, key_pose_times, renderer, asset_ids, source_claim_ids and sync_tolerance. Use integer frames and a single FPS; time-to-frame conversion must be consistent with Blender's frame-one origin.
6. Build a low-resolution animatic: temporary art plus final audio, actual cuts, camera moves and major pose changes. Approve staging and likeness here.
7. Finish only the approved shots. Render short previews first; cache asset/shot hashes; re-render only changed shots. Use isolated output folders.
8. Assemble voice, SFX/music and captions; inspect contact/impact/gesture moments in real-time playback as well as stills. Check encoded frames, audio duration, caption clipping and sync drift.
9. Save approved/rejected examples and the reason. Evaluate cost per accepted shot, not just token count. Do not automatically turn generated observations into creator preferences.

Human motion recordings may provide pose tracks, but 2D pose estimation misses occluded joints/depth/fingers. A cartoon reference cannot automatically produce exact replacement-character motion. Retarget, clean up and visually compare the result. Declare approximations.

## Tools and status

| Component | Technical role | Status/recommendation |
|---|---|---|
| Codex desktop + selected model | Interactive agent harness and reasoning | Existing coordinator |
| Studio Python + Markdown/Git + SQLite FTS | Task commands, evidence, explicit feedback, retrieval | Existing; compact context before adding another memory |
| Selected skills | On-demand workflow instructions | Existing; select narrowly |
| FFmpeg/OpenCV | Decode, timing, contact sheets, compositing, QC | Existing |
| faster-whisper | Local speech recognition | Existing; review alignment uncertainties |
| Creator audio / stock Kokoro | Final performance or synthetic narration | Existing; identify stock voice accurately |
| Blender | Meshes, rigs, cameras, shaders, 2D/3D animation and rendering | Existing; Mac only approved Git/Blender operation |
| HyperFrames | Browser-based seekable HTML/SVG/JS motion rendered through Chrome/FFmpeg | Recommended new graphics layer; not installed by this audit |
| Image generation | Backgrounds, model sheets, layered asset concepts | Optional; image is not a rig |
| Paperclip | Persistent task/agent control plane | Optional bounded pilot after production workflow works |
| Hermes | Separate agent runtime with its own sessions/memory | Existing optional handoff; not automatic memory for this chat |

HyperFrames can host Three.js and 3D assets. It does not automatically rig characters or convert Blender Python into HTML. Share image/video/glTF assets and a timing manifest, not source scripts. For diagrams it is faster to author; for complex character acting Blender is the stronger authoring environment. Neither inherently guarantees better art.

## New repository decisions (upstream checked 2026-10-02)

- **HyperFrames: adopt as a graphics pilot.** https://github.com/heygen-com/hyperframes — HTML/SVG/JS, seekable GSAP/CSS/Three.js/etc., local Chrome + FFmpeg rendering, Apache-2.0. Local renderer has no per-render fee; hosted services/generated assets may cost separately.
- **Impeccable: selective design aid.** https://github.com/pbakaus/impeccable — frontend design guidance, critique/polish and deterministic UI checks. Useful for production desk and typography; not character animation/mocap. Scope to selected design work; do not globally apply UI taste rules to cinematic motion.
- **CodeGraph: conditional navigation pilot.** https://github.com/colbymchenry/codegraph — parses source into local SQLite symbols/call relationships and exposes CLI/MCP retrieval. Helps code lookup, not creator personality or video understanding. Measure against existing search and keep index out of synced/Git media paths where practical; validate freshness.
- **Caveman: optional internal-output experiment.** https://github.com/JuliusBrussee/caveman — terse prose skill plus proxy/middleware for compressing tool responses, with original recovery. Do not apply to narration, source quotes, explanations the creator needs to learn, timing data or approved preferences. The 65% headline is not our measured end-to-end saving. Its own README distinguishes 8.5% output reduction in a cited coding trial and a maintainer-reported 33.2% input reduction in a different proxy trial; workloads differ and raw proxy artifacts are not published. Disable optional telemetry in any approved pilot, compare quality/retries/total cost, and use one compressor at a time.
- **OpenRig: defer on this setup.** https://github.com/mvschwarz/openrig — persistent teams around Codex/Claude/Pi, YAML roles and work ownership. README currently requires Node and tmux on macOS/Linux, says native Windows unsupported and WSL2 untested, and documents hook/trust/config changes. This does not fit the Lenovo plus restricted render-Mac split. Do not install alongside Paperclip/Hermes merely for more agents.
- **Paperclip: optional control plane, not chat brain.** https://github.com/paperclipai/paperclip/blob/master/docs/adapters/codex-local.md — Codex adapter starts CLI workers. Shared repository artifacts can connect our desktop work with those jobs. Current chat history/model access are not automatically inherited. A dashboard plus a bounded local API/CLI bridge would be explicit integration work. Use at most two pilot roles and avoid simultaneous writes to the same files.

## Cost discipline and next proof

Existing local rendering/transcription has compute, storage and electricity costs without mandatory per-call provider charges. Extra CLI workers still consume subscription allowance or separately billed API tokens. No assumed zero price because a dashboard reports zero. Count retries and rework. Token savings are not equal to subscription-quota savings.

Before a long production: make one short R01/R04 graphics proof and one short R02/R03 rigged performance proof with the same chosen narration beat. Compare identity, motion, audio sync, revision effort, render time and accepted quality. Build one reusable rig/style pack after that review. Do not commit to an 86-second high-detail performance before validating the character and motion at low resolution.
