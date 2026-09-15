# Headroom and AI-to-Blender guide

## Token-aware Codex sessions

Headroom 0.37.0 is installed inside `.venv` and its source is pinned locally under `.studio/repos/headroom`. The earlier launcher description understated its side effects: upstream `wrap codex` modifies the active Codex configuration. The launcher now refuses to run against your normal Codex home. Its runtime has not been validated with an authenticated model call and no savings have been measured.

Use a separate terminal/session configured with `CODEX_HOME` pointing exactly to this repository's `.studio/codex-home`, then authenticate that isolated Codex CLI through its normal login flow. Do not copy authentication files or existing private Codex state into the repository. Once that session is configured, launch with:

```powershell
.\codex-headroom.ps1
```

The launcher requests Headroom's local proxy, reversible retrieval and cross-session memory, without the optional Serena server. Headroom writes provider/MCP configuration in the isolated active Codex home. The guard does not claim to sandbox every Headroom cache or log. Review its settings before live use. From the same isolated session, reverse durable Codex registration with:

```powershell
.\.venv\Scripts\headroom.exe unwrap codex
```

This cannot retrofit the current Codex Desktop conversation or refund tokens already consumed. Savings depend on the workload. Tool output, logs, large JSON, retrieved files and long histories offer the best opportunity; short user messages offer little. Subscription usage and API token billing are separate concepts, so measured context reduction is not a promise of an identical account-usage reduction.

## Choosing the correct visual route

| Input | Result | Camera freedom | Best use |
|---|---|---:|---|
| One generated image | 2D card or camera projection | None or a tiny push/pan | Background, poster, quick atmospheric shot |
| One image split into layers plus a depth map | 2.5D scene | Small parallax | Documentary transitions and establishing shots |
| Multi-view 3D generator | Editable mesh with textures, often requiring cleanup | Moderate to full | Hero props, statues, generic buildings |
| 30–100 overlapping photos or a slow 360-degree video | Photogrammetry / Gaussian reconstruction | Full within captured coverage | A real building or location |
| Dimensions, plans and reference photos | Procedural Blender model written by Astra/Codex | Full | Clean, art-directed architecture and reusable sets |

An image file is enough to texture a surface; it is not a complete 3D object because it contains no reliable geometry for hidden sides. Asking an image model for front, back, left and right views can help, but independent generated views often disagree. For an identifiable real building, capture overlapping real views and at least one known measurement.

## Exact Astra-to-Blender workflow

1. Put reference files in an episode-local, approved asset directory excluded from Git when licensing or privacy requires it. Include a rough height/width and identify what can be invented.
2. Ask Astra to create a `bpy` scene script from those references. Specify Blender version, output aspect ratio, frame rate, duration, visual style, camera move, render engine and maximum render time.
3. Require named objects, real-world scale, deterministic seeds, relative paths, a manifest, validation output and a preview mode that renders the first/middle/last frames.
4. Run the script in Blender. Inspect those frames. Send the images back to Astra with concrete corrections such as facade proportions, window spacing, camera collision, material roughness and lighting direction.
5. Render a short low-resolution motion preview. Check silhouette, parallax and motion before increasing resolution or samples.
6. Render PNG frames on the Mac so an interrupted render can resume. Assemble frames and sound with the studio media tools.

Prompt template:

```text
Create a Blender 4.5 Python scene from the attached front, side and three-quarter
reference images. The building is approximately [width] m by [height] m. Preserve
[recognizable features]. You may invent [hidden areas]. Build clean editable geometry
with named collections; use real-world scale, UVs and physically plausible materials.
Create a [duration]-second, 24 fps [camera move] for a 16:9 documentary shot.
Use deterministic seed 42 and repository-relative assets. Add preview mode at 640x360
for frames 1, midpoint and end; final output is a PNG sequence. Validate camera, lights,
missing assets, frame range, render engine and output path and write validation.json.
Do not claim unseen dimensions came from the references; list every assumption.
```

For a generated fantasy building, one concept image plus permission to invent the unseen structure is enough. For a real building that should match reality, use a multi-view capture or dimensions. Astra supplies the modeling logic and iteration; Blender remains the program that creates and renders the asset.
