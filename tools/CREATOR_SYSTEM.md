# Creator Studio: local production system

This is the running architecture in this repository, not a promise of a fully autonomous video factory. The Windows computer is the control desk. The Mac is an approved Git/Blender render workstation. A project advances through research → script → audio → storyboard → animation → finish → review, with a real artifact required at each stage. Nothing publishes automatically.

## Start on Windows

From `C:\Users\Isaac\OneDrive\Desktop\Youtube` in PowerShell:

```powershell
.\creator.ps1 desk
```

Open [Creator Desk](http://127.0.0.1:8766). The server binds only to `127.0.0.1`. Stop it with Ctrl+C. You can create a production, select one or more `R01`–`R04` references, prepare a stage handoff, save an explicit approved/rejected writing example, and play locally generated media. A handoff is an inspectable Markdown prompt in ignored `.studio/creator/projects/`; preparing one makes no model call.

The CLI has the same stages:

```powershell
.\creator.ps1 worker create 002-ronaldo-hate-psychology --brief "Make an evidence-led short that preserves my opinion and uses reference R04" --reference R04
.\creator.ps1 worker list
.\creator.ps1 worker handoff PROJECT_ID research
.\creator.ps1 worker run PROJECT_ID research
```

`run` without `--execute` prepares a worker packet and does **not** contact a model. To request an actual Codex CLI candidate, choose the model explicitly:

```powershell
.\creator.ps1 worker run PROJECT_ID research --execute --model MODEL_NAME --timeout 600
```

This runs a bounded, read-only Codex process through the existing CLI login. Its response is a candidate in `.studio/creator/projects/PROJECT_ID/workers/`, not an approved stage. The provider's actual price/usage depends on your account; the worker records reported token usage but does not guess dollars. Review the candidate and source ledger, then use `complete PROJECT_ID research --artifact episodes/002-ronaldo-hate-psychology/REVIEWED_FILE.md`. Artifacts must be nonempty files inside that episode or the project worker folder. A later stage cannot start until prior stages are completed. `fail` and `retry` handle errors, with a three-attempt limit.

## What each part does

| Component | Technical job | State or output |
| --- | --- | --- |
| `studio/creator_kernel.py` | SQLite stage machine, episode-scoped creator memory, bounded handoffs, artifact checks, cost reservations | Ignored `.studio/creator/creator.sqlite3` and project packets |
| `studio/creator_worker.py` | Optional isolated Codex CLI candidate, timeout, lock, stdout/usage capture | Ignored worker prompt, response and report |
| `studio/creator_server.py` + `studio/creator_web/` | Local browser desk, same-origin actions, media playback | No cloud service or background provider |
| `studio/creator_media.py` | Sample-count audio timing, frame plan, local HyperFrames render and decode check | Ignored composition and MP4 |
| `studio/creator_templates/tactical.html` | Original animated football tactics graphic | Reusable HTML/GSAP scene |
| `integrations/creator/` | Pinned HyperFrames, GSAP and ffprobe install | Source lockfile tracked; `node_modules` ignored |
| `tools/animation-references/` | Short visual contact sheets and reference metadata | Small portable JPEG/JSON records |
| Existing Blender/short tools | Character action, native scenes, recorded voice mixes and longer films | See `PROJECT_CONTEXT.md` and episode handoffs |

The SQLite memory stores **only** examples you explicitly save: raw take, approved wording, rejected wording and why it missed. It is retrieval memory, not model training. A stage handoff retrieves at most three recent examples for that episode plus current project corrections and bounded source excerpts. Approximate token counts use characters/4 and exclude runtime instructions, tools and model reasoning. No token saving is claimed without a measured before/after run.

The project is the orchestrator. Research and writing can use a chosen Codex CLI model when you opt in. Audio and assembly use deterministic local tools. Blender and HyperFrames are renderers, not interchangeable agents. The desk does not need Paperclip or OpenRig to run: both would add another scheduler/agent layer before we have measured a bottleneck. Hermes remains an optional separate agent through `hermes-studio.ps1`; it does not read the new SQLite memory unless we intentionally add an adapter. ViMax is not on the critical path, and the work Mac should receive only approved repository content. Do not run personal agent servers or transfer private/company data there.

## Reproduce the working tactical video proof

The current local proof is `.studio/creator-demo/tactical-r04/final.mp4` (6.133 seconds, 1280×720, 30 fps). It uses a stock Kokoro guide voice, **not** your voice and **not** an episode release. It demonstrates that narration samples set the frame count, captions occupy explicit frame ranges, HTML graphics animate on that clock, and the final encoded clip has synced audio. It is a football tactics graphic, not a character-performance scene.

To make a new version using your own **WAV** and a UTF-8 text file with one caption beat per line:

```powershell
npm ci --prefix integrations/creator --ignore-scripts
.\creator.ps1 media plan .studio/my-audio.wav --captions .studio/my-captions.txt --output .studio/my-timeline.json
.\creator.ps1 media build .studio/my-timeline.json --audio .studio/my-audio.wav --output .studio/my-new-composition
.\creator.ps1 media render .studio/my-new-composition
```

Use a **new** output folder for each render; the tool will not overwrite a finished composition. The first render may download HyperFrames' compatible headless Chrome. On this Windows machine that browser is already cached. Rendering makes no AI-provider call. The CLI checks frame count against the source WAV, verifies its hash, compares encoded duration/FPS, and decodes the entire MP4. The initial equally spaced caption beats are estimates; listen and edit `timeline.json` shot boundaries to match actual speech before the final build. The demo uses an original football pitch design rather than lifted match footage.

## Choosing motion for a shot

- `R01` presenter: layered head/torso/arm artwork, mouth shapes and blinking on speech marks. HyperFrames is useful for titles and charts behind the figure; acting requires drawn poses or a 2D rig.
- `R02` 3D ledge: use Blender geometry, camera, light and a rigged subject; block the path first and render a preview before detail.
- `R03` wireframe acting: animate joint landmarks and silhouette timing in Blender, then add motion blur/line style. Do not confuse a moving still with articulated action.
- `R04` tactical board: HyperFrames/GSAP for passes, arrows, labels and camera moves. This is the style proved by the sample MP4.

For every episode: lock the spoken audio, map beats to frames, draw a rough animatic, inspect motion and camera cuts, then render and finish. The existing Blender `rules_short_scene.py` and action packet remain the character-performance route. The tactical renderer does not replace their meshes, likeness artwork, throw choreography or Blender scenes. A 30 fps export alone does not make movement lifelike; the intermediate poses, easing, impacts, eye direction and camera blocking do.

## Evidence, cost and release gates

The creator thesis is preserved in handoffs. Material claims still need internal labels (`VERIFIED_FACT`, `DISPUTED_FACT`, `ALLEGATION`, `INFERENCE`, `OPINION`, `UNKNOWN`), source records, and fair counterarguments. A social post is sentiment, not proof of fixing. The local desk never posts, pushes, hires, trades or starts a paid job. `reserve_cost` is a guard for future provider adapters; no paid generation adapter is wired. Approval remains a human editorial decision, and playback/research checks remain necessary before release.

Committed source is small: Python, HTML, JSON, JavaScript, contact sheets, and a pinned npm lockfile. Ignored `.studio/` contains the large MP4, SQLite state, copied audio, rendered frames and browser cache; pulling the repository on a Mac does **not** pull those local outputs. The Mac continues using the existing episode-specific Blender launchers after an approved Git transfer.
