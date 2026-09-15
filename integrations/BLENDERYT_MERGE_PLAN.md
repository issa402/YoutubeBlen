# blenderyt Integration Plan

Source: `https://github.com/issa402/blenderyt.git`

Imported location: `external/blenderyt/`

2026-09-11 transfer decision: preserve the reference files and local edits directly in `YoutubeBlen`, without a submodule dependency. Upstream base commit: `c78af88d67b1e60288289bf61e27d3bcba913635`. The original embedded Git directory is archived locally at `.studio/git-archive/blenderyt-original.git`; it is excluded from the new repository. Root production files remain canonical.

## Verdict

`blenderyt` is an earlier implementation-heavy version of the same soccer documentary project. It should not replace the current repository. The current repository remains canonical because it has clearer computer boundaries, evidence labels, status tracking, and episode organization. Useful `blenderyt` assets should be promoted selectively.

## Adopt

- Both Blender Python scene scripts after Blender-version testing.
- The content-engine lanes: research, claims, style, script, storyboard, animation, and render QA.
- Reference-video analysis using yt-dlp, SceneDetect, OpenCV, and supervision.
- Scene-level narration, visual, evidence, and tone fields.
- Image-prompt continuity rules for short impact-frame sequences.
- Reusable Blender helpers for materials, cameras, figures, text boards, line art, and rendering.

## Adapt

- Merge imported episode materials without overwriting canonical files.
- Reconcile its Messi-versus-Ronaldo thesis with the current present-backlash question.
- Map its five evidence labels onto the canonical six-label system.
- Replace Linux paths with repository-relative paths and manifest-driven settings.
- Split the 695-line and 511-line scripts only after Mac compatibility testing.
- Prefer stylized symbolic figures and review names/likeness cues.

## Reject or defer

- Do not import `.venv`, downloaded reference repos, model files, caches, or renders.
- Do not assume old Linux installations exist on Windows.
- Do not install every starred repo or enable automatic publishing.
- Do not adopt `/home/iscjmz/...` paths.
- Defer code-review-graph until shared Blender modules exist.

## Target architecture

```text
episodes/001-messi-hate/{research,script,storyboard,manifests,scenes}
blender/{lib,scenes,validation}
analysis/{reference_video,render_qa}
external/blenderyt/       # upstream reference, not canonical production code
```

## Integration phases

1. Preserve the import, compare files, clarify ambiguous claims, and choose the episode scope.
2. Merge unique claims into the canonical ledger; add sources and counterarguments; then choose the thesis.
3. Compare hooks, produce one canonical narration draft, build manifests, and choose a 30-60 second proof sequence.
4. Test both scripts on the approved Mac Blender version, promote the best scene, then add relative paths, preview mode, deterministic settings, and validation.
5. Add research, static checks, smoke rendering, render QA, and Hermes automation only after the manual pipeline works once.

## Immediate next action

Run `001_chosen_boy_maradona_shadow.py` as the first Mac compatibility test because it aligns with Episode 001. Render a low-resolution preview before any full render.
