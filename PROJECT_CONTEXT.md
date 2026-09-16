# Project Context

## Channel identity

Newest visual request: `mac/superhero-crossover/` under episode 002. Revised eight-second four-shot adaptation of the creator's video: Omni-Man Messi, Ninja Turtle Mbappe crouch/side-profile point, Superman-style Ronaldo doorway reveal. This supersedes the single floating shot as the current visual request; earlier packets remain available.

Latest visual direction (2026-09-15): the creator requested a cartoon Messi floating above a city with crossed arms, based on an attached superhero pose. New standalone 12-second scene: `episodes/002-ronaldo-hate-psychology/mac/messi-floating/`. Its README is the entry point for this clip. The existing 30-second opening below remains available for editing; its voice/finishing timing is not automatically compatible with the new 12-second clip.

Current upgraded render packet: `episodes/002-ronaldo-hate-psychology/mac/opening-hd/`. Follow `tools/MAC_START_HERE.md` for the user-selected `https://github.com/issa402/YoutubeBlen.git` clone/pull workflow. Nine native 1080p samples are verified; full HD rendering remains pending. Local neural opening voice and v2 ASR captions are ready under `.studio/`; Windows finishing commands are in `tools/HD_FINISHING.md`. Imported `external/blenderyt/` is ordinary preserved reference source, not a required submodule.

Current first release: `episodes/002-ronaldo-hate-psychology/`, titled "Why Do Some Messi Fans Hate Ronaldo More Than They Love Messi?" Folder ID 002 is historical; release order is 1. Its CREATOR_TAKE.md preserves the creator's direction, and its master script/source register are the working authority. Episode 001 remains a separate earlier draft.

Recording-ready text is `script/NARRATION.txt`; current V2 has 1,416 words. The 30-second three-shot opening is in `mac/opening/`; the older `mac/` scene is an eight-second reusable motif. Synthetic guide audio and validated local renders are linked by the episode's `PRODUCTION_HANDOFF.md`. Use `hermes-studio.ps1 -Episode ... -Task ...` for fresh creator-memory handoffs; bare Hermes chat does not automatically import this conversation or the studio database.

Read `skills/creator-studio/SKILL.md` when continuing studio work. It is the project-specific entry to installed ECC workflows, discovered through this document rather than a global plugin change. The local production desk is `.studio/dashboard.html`; `studio review EPISODE` checks current script/source/audio agreement and can export the chapter edit CSV. Current assets are explicitly selected by the episode's `manifests/production-assets.json`.

The channel covers soccer through story-driven documentary commentary. Its advantage should be the combination of:

- Strong, clearly identified opinion
- Evidence visible on screen
- Narrative time travel and open loops
- Original Blender animation and visual metaphors
- Transparent treatment of uncertainty and disputed incidents

The desired voice is conversational and direct: bring the viewer into a mystery, travel backward to the origin, reveal evidence in stages, test competing explanations, and return to the opening question.

## Hardware and execution boundaries

### Personal Windows Lenovo

- AMD Ryzen 7 6800HS
- Approximately 14 GB usable RAM
- RTX 3050 Laptop GPU with 4 GB VRAM
- Runs Codex/Hermes, research tools, local transcription, OpenCV, FFmpeg, yt-dlp, and project management
- Heavy local tasks should run sequentially

### Restricted work Mac

- Runs only approved Git and Blender workflows
- Pulls Blender scripts and approved assets from the repository
- Does not install outside repositories, AI tools, OpenCV, web scrapers, or project-specific package stacks
- Must comply with employer policy; technical capability is not authorization

## Core pipeline

```text
Current-sentiment research + historical sourcing
                       |
                       v
Evidence ledger -> narrative outline -> script -> storyboard
                       |
                       v
Codex writes Blender Python + manifests + validation
                       |
                       v
Git -> Mac Blender render -> approved preview/output transfer
                       |
                       v
Windows visual QA -> editorial review -> final assembly/publish review
```

## Tool principles

Current workflow decisions: `tools/WORKFLOW_BLUEPRINT.md` and `editorial/EDITORIAL_STANDARDS.md`. Root episode files remain canonical; imported `external/blenderyt/` project instructions are reference material. Draft from the creator's provisional thesis while research proceeds; evidence clearance applies before factual passages are locked, not before creative drafting begins.

The creator reported a new MacBook Pro on 2026-09-05. The user confirmed it is employer-managed and reports personal use is permitted. Chip may be M4; actual unified memory is unknown, and the reported 1 TB may be storage. Continue the approved Git/Blender workflow.

- Use tools only when they reduce uncertainty or repetitive labor.
- Do not install overlapping tools without a concrete requirement.
- Agents may propose; deterministic code and evidence gates decide.
- Local memory is not the same as authoritative project truth. These Markdown files and Git history are authoritative.
