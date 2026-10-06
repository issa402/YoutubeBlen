# OpenMontage reference analysis on Windows

OpenMontage is an optional **reference-analysis worker** for this studio. Its pinned source is fetched into ignored `.studio/repos/OpenMontage/`; our adapter invokes its real `SceneDetect` and `FrameSampler` classes. Paperclip remains the agent job board, the episode files remain editorial authority, and Blender/HyperFrames remain the renderers. This integration does not claim to run OpenMontage's full 12-pipeline production system.

From the YouTube project root in PowerShell:

```powershell
.\tools\fetch_studio_repos.ps1
python tools/openmontage_reference.py "C:\path\to\reference.mp4" --output .studio/openmontage/my-reference
```

FFmpeg and ffprobe must be on `PATH` or in `.studio/bin/`. The command refuses an unpinned checkout, limits samples to 60, writes only under ignored `.studio/`, and will not overwrite a populated output directory. It makes no model/API call. It writes `scenes.json`, `frames/*.jpg`, and `reference-report.json`, including source SHA-256 and the OpenMontage commit. When detection returns only one scene, it samples uniformly so the visual review still has coverage; **these timestamps are candidates, not frame-accurate editorial truth**.

Open `frames/` and the original clip. Mark the real action beats, poses, backgrounds and transitions, then give the report path and selected frames to the Paperclip Visual Director. That agent creates a candidate shot plan; you review the animatic and evidence before either renderer runs. Keep the raw reference and report on the personal Windows PC. Do not add someone else's footage to the Git project or treat its animation as match evidence.

The October 5 pilot ran on `R04`, the 6.667-second football reference already cataloged in `ANIMATION_REFERENCE_LIBRARY.md`. OpenMontage's FFmpeg scene detector returned one scene and missed the approximate mid-clip change noted by visual review; the adapter therefore produced 16 evenly spaced frames. This is useful for visual inventory, but the shot boundary still needs human correction. The full OpenMontage agent stack, provider integrations, Backlot board and generated-media pipelines have not been installed or validated here. Its AGPL-3.0 code stays in the ignored checkout and is not copied into this repository.

`claude-mem` is deferred. The current episode-scoped Creator Desk memory saves only explicitly approved/rejected examples, while source files and Git preserve durable decisions. Claude-mem's automatic session observation, worker, SQLite/vector store and optional provider path would add another state owner and process unreviewed chat/tool content. It can be revisited if cross-session retrieval demonstrably fails and after its storage, privacy and token/cost settings are evaluated on an isolated personal profile. No token reduction is claimed for either tool without a measured comparison.
