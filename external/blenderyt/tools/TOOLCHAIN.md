# Toolchain and Responsibilities

## Core tools

### Hermes

Project orchestration, scheduled jobs, profiles, task routing, lightweight durable memory, and notifications.

Recommended eventual profiles:

- `producer` - milestones and handoffs
- `researcher` - evidence collection only
- `developer` - scripts and pipeline code
- `reviewer` - read-only evidence and quality review

Use one queued local model server rather than loading a separate model for each profile.

### Codex

Writes and reviews Python, Blender automation, manifests, media utilities, tests, and documentation.

### last30days

Measures current conversation and backlash across social/video/web sources. Use it for current sentiment, creator reactions, recurring allegations, and audience language. Do not use engagement as proof that an allegation is true.

### wigolo

Retrieves and caches public web evidence, articles, source pages, and quotations. Preserve exact source locations and publication dates.

### yt-dlp

Downloads authorized/publicly accessible research media, subtitles, metadata, and audio. Technical access does not grant republication rights.

### VibeVoice-ASR-BitNet

Creates local transcripts with timestamps and speaker structure. Verify names, match terminology, quotations, and multilingual output.

### FFmpeg

Extracts audio, creates proxies, samples frames, normalizes media, and assembles deliverables.

### OpenCV

Runs only on Windows. Performs shot detection, motion measurement, duplicate-frame checks, thumbnail analysis, contact sheets, and QA on render outputs received through an approved channel.

### Blender

Runs on the work Mac under employer policy. Executes approved repository scripts, produces original animation, and performs Blender-native scene validation.

## Conditional tools

### Puppeteer

Use only for a defined browser interaction, screenshot, preview, or dashboard test that lacks a suitable API. It is not the default research tool.

### Agency Agents

Do not install the entire catalog. If needed, curate roles equivalent to Studio Producer, Content Strategist, Technical Artist, Brand Guardian, Reality Checker, and Trend Researcher.

### Engineering agent skills / ECC

Use a small selected set for specifications, planning, testing, review, security, Git, verification, content strategy, and context handoffs. Avoid duplicate full installations or conflicting instruction layers.

### awesome-claude-skills

Treat as a community catalog. Inspect every skill before use. Do not load large collections globally; copy only audited, project-relevant skills.

### Code review graph

Pending exact repository identification and audit. Intended role is visualizing or structuring code review relationships, not verifying editorial claims.

## Deferred tools

- MemPalace - only after conversation volume justifies it
- Headroom - only after measuring context/token bottlenecks
- Scrapling - only for a permitted structured crawl that wigolo cannot handle
- MoneyPrinterTurbo - optional source of subtitle/TTS/compositing patterns or separate stock-footage experiments
- ViMax - optional cloud-based storyboard/reference experiment
- jcode - unnecessary while Codex is the primary coding harness
- iptv-org - only for a future international broadcast-analysis angle
