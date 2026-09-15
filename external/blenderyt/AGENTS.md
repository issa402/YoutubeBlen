# AGENTS.md — Soccer Documentary Studio

## Mission

Build evidence-led soccer documentaries with strong commentary, exact production scripts, and original Blender animation.

## Start every session

1. Read `docs/project/PROJECT_CONTEXT.md`.
2. Read `docs/project/CURRENT_STATUS.md`.
3. Read `docs/project/DECISIONS.md`.
4. Read the active folder under `episodes/`.
5. Update durable status before ending substantial work.

## Canonical areas

- `episodes/` contains authoritative per-video research, claims, scripts, storyboards, and manifests.
- `editorial/` contains publication and evidence standards.
- `docs/project/` contains durable studio context.
- `scripts/` contains Blender Python and local utilities.
- `docs/videos/` contains legacy drafts retained for comparison; do not let them overwrite canonical episode files.

## Evidence rules

Every material claim must be labeled as one of:

- `VERIFIED_FACT`
- `DISPUTED_FACT`
- `ALLEGATION`
- `INFERENCE`
- `OPINION`
- `UNKNOWN`

Chronology does not prove causation. Commercial incentive does not prove coordination. A disputed call does not prove tournament fixing. Social engagement measures sentiment, not truth. Store the strongest counterargument beside the strongest supporting evidence.

## Production order

```text
idea -> research -> claims ledger -> thesis -> timestamped master script
-> storyboard/manifests -> low-resolution Blender proof -> render QA
-> editorial review -> approved publication package
```

Write narration for the screen. Each production beat needs exact timecode, voiceover, picture/action, camera/edit direction, audio, assets, and evidence IDs.

## Machine boundary

- Personal Windows PC: Codex/Hermes, research, transcription, FFmpeg, OpenCV, scripts, and QA.
- Restricted work Mac: only employer-approved Git and Blender workflows.
- Do not install outside repositories, AI models, scrapers, or project dependency stacks on the work Mac.
- Technical capability is not authorization; follow employer policy.

## Blender standards

- Use repository-relative paths.
- Prefer deterministic, procedural, stylized geometry.
- Use preview settings before final rendering.
- Avoid unlicensed realistic player assets.
- Validate camera, lights, frame range, resolution, asset paths, and output path.
- Generated outputs belong under ignored output directories.

## Git and safety

- Never commit credentials, model weights, raw downloaded media, or full render sequences.
- Preserve unrelated user work.
- Review `git diff --cached` and scan for secrets before every push.
- Do not publish videos or change external services without explicit approval.
