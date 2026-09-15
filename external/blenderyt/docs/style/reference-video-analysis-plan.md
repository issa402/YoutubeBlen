# Reference Video Analysis Plan

## Goal

Learn from channels like ChainsFR without copying them.

We want to extract:

- pacing
- hook structure
- cut frequency
- narration rhythm
- text overlay style
- evidence reveal style
- camera movement patterns
- visual metaphor patterns

## Tool Stack

```text
yt-dlp -> public metadata/captions/video where allowed
scenedetect -> cut and scene boundaries
OpenCV -> frame sampling, color, motion, composition
supervision -> annotations and higher-level CV helpers
style docs -> durable memory for Codex/Hermes
```

## Inputs Needed From User

Add reference URLs here:

```text
1. TODO: ChainsFR reference video URL
2. TODO: Another soccer documentary reference
3. TODO: A motion graphics reference
```

## Output Files

```text
docs/style/channel-style-profile.md
docs/style/reference-videos.md
docs/style/visual-rhythm-notes.md
```

## First Analysis Questions

For each reference video:

1. What happens in the first 5 seconds?
2. How often does the visual change?
3. Is the narration calm, aggressive, sarcastic, or documentary?
4. How are claims introduced?
5. How are receipts shown?
6. What type of motion graphics repeat?
7. What should we borrow as structure, not content?

## Status

```text
READY - waiting for reference video URLs
```
