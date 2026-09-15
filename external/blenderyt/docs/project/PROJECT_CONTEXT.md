# Project Context

## Channel identity

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

- Use tools only when they reduce uncertainty or repetitive labor.
- Do not install overlapping tools without a concrete requirement.
- Agents may propose; deterministic code and evidence gates decide.
- Local memory is not the same as authoritative project truth. These Markdown files and Git history are authoritative.
