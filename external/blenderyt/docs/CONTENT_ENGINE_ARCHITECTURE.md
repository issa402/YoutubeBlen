# Content Engine Architecture

## Goal

This repo should become a repeatable YouTube production system, not just one Blender script.

The target output is cinematic soccer commentary with:

- evidence-backed sports argumentation
- motion graphics and Blender fight choreography
- scene-by-scene visual planning
- repeatable research workflows
- style learning from inspiration videos
- reusable Blender code and prompt packs
- memory/context so future Codex sessions do not restart from zero

The channel can begin with soccer, especially Messi/Ronaldo narrative videos, but the architecture should support any later niche.

## Core Principle

Separate the work into lanes.

Bad workflow:

```text
random idea -> ask AI for script -> random Blender code -> forgotten context
```

Target workflow:

```text
idea -> research -> claims ledger -> style analysis -> script -> storyboard -> Blender plan -> assets/prompts -> animation code -> render -> review -> publish package
```

Each lane has a clear job. This keeps the repo useful as it grows.

## High-Level System

```text
User Idea
  -> Project Architect
  -> Content Planner
  -> Research Scout
  -> Claims Ledger
  -> Inspiration/Style Analyzer
  -> Script Writer
  -> Storyboard Director
  -> Asset Prompt Director
  -> Blender Animation Engineer
  -> Render QA
  -> Memory + Code Graph
```

## 1. Project Architect

Purpose:

Design the repo so it does not become a pile of random scripts.

Responsibilities:

- Decide folder structure.
- Decide where research, scripts, storyboards, assets, renders, and helpers live.
- Decide which external repos/plugins are tools versus dependencies.
- Keep controversial claims separated from animation code.
- Keep the system repeatable for every future video.

Useful tools:

- `ECC`: workflow/skills discipline.
- `superpowers`: planning and execution methodology.
- `code-review-graph`: becomes more useful as the repo grows because it builds a persistent map of code relationships.
- `Understand-Anything`: useful later for visualizing the repo and onboarding future sessions.

Current recommendation:

Use `code-review-graph` once the repo has multiple helper modules, not while it only has one script. It becomes valuable when we have shared Blender helpers, tests, render pipelines, and many scene files.

## 2. Content Planner

Purpose:

Turn a broad video idea into a production-ready plan.

Responsibilities:

- Define the thesis.
- Define the target audience.
- Break video into chapters.
- Decide what the first 10 seconds shows.
- Decide the argument progression.
- Decide which claims need proof.
- Decide which scenes need Blender animation.

Example for first video:

```text
Title: Why Did The Hate Miraculously Shift To Messi?
Hook: show a trophy race machine where public criticism switches direction as the scoreboard changes.
Core question: did the narrative change naturally, or did football media/business incentives shape it?
```

Output files:

```text
docs/videos/001-messi-hate-shift/plan.md
docs/videos/001-messi-hate-shift/outline.md
```

## 3. Research Scout

Purpose:

Find sources, quotes, timelines, clips, posts, controversy summaries, and counterarguments.

Responsibilities:

- Find reliable sources.
- Separate facts from allegations.
- Gather counterarguments so the video does not sound weak or one-sided.
- Collect links for every major claim.
- Use social/reddit/youtube/web tools for public discourse analysis.

Useful repos/tools:

- `mvanhorn/last30days-skill`: researches topics across Reddit, X, YouTube, HN, Polymarket, and web, then synthesizes grounded summaries.
- `Panniantong/Agent-Reach`: gives AI agents search/read access across Twitter/X, Reddit, YouTube, GitHub, Bilibili, XiaoHongShu without normal API-heavy setup.
- `NanmiCoder/MediaCrawler`: reference for social/media crawling patterns.
- `D4Vinci/Scrapling`: adaptive scraping and web extraction.
- `KnockOutEZ/wigolo`: local-first search/fetch/crawl/research over MCP, useful as the agent's web layer.

Important boundary:

Do not scrape private or login-gated sources unless access is explicitly provided and allowed. Prefer public pages, captions, articles, and official records.

Output file:

```text
docs/videos/001-messi-hate-shift/research-notes.md
```

## 4. Claims Ledger

Purpose:

Protect the video from becoming unsupported accusations.

Every important claim gets a label:

```text
FACT: directly documented by reliable source
SOURCE CLAIM: reported by a named outlet/person/source
ALLEGATION: claimed but disputed or not fully proven
OPINION: user's interpretation/narrative framing
VISUAL METAPHOR: animation idea, not factual claim
```

Example format:

```text
Claim: Barcelona paid companies connected to Jose Maria Enriquez Negreira.
Type: FACT / SOURCE CLAIM depending on source wording
Source: link
Video use: establish context, not prove every match was rigged.
Visual: referee silhouette receiving spotlight while documents stack up.
```

Output file:

```text
docs/videos/001-messi-hate-shift/claims-ledger.md
```

## 5. Inspiration / Style Analyzer

Purpose:

Study creators like ChainsFR or other reference videos and extract the style without copying the content.

Responsibilities:

- Analyze pacing.
- Analyze scene length.
- Analyze visual rhythm.
- Analyze intro hooks.
- Analyze transitions.
- Analyze narration tone.
- Analyze recurring visual devices.
- Build a reusable style profile.

Useful tools:

- `yt-dlp`: get public captions, metadata, and video files where allowed.
- `opencv/opencv`: low-level video frame analysis.
- `roboflow/supervision`: higher-level computer vision utilities built on top of OpenCV-style workflows.
- `yt-dlp + OpenCV + supervision`: best stack for video structure analysis.
- `Hermes` / memory docs: persist style findings over time.

What `supervision` can help with:

- sampling frames from reference videos
- detecting scene changes if paired with OpenCV logic
- annotating frames and visual elements
- tracking objects if we later analyze motion patterns
- building visual summaries of pacing and composition

What it does not do by itself:

- It does not magically understand YouTube taste.
- It does not replace scriptwriting.
- It needs video frames, captions, or extracted metadata as input.

Output files:

```text
docs/style/reference-videos.md
docs/style/channel-style-profile.md
docs/style/visual-rhythm-notes.md
```

## 6. Script Writer

Purpose:

Turn the claims ledger and style profile into a watchable video script.

Responsibilities:

- Write a hook that shows tension immediately.
- Write narration that matches the channel voice.
- Keep one claim per beat.
- Include timestamps.
- Include visual direction with each line.
- Include source notes or citation IDs.
- Include counterarguments where needed.

Script format:

```text
00:00-00:08
Narration: ...
Visual: ...
Evidence: CL-001, CL-002
Tone: sharp, suspicious, controlled

00:08-00:22
Narration: ...
Visual: ...
Evidence: CL-003
Tone: build tension
```

Output file:

```text
docs/videos/001-messi-hate-shift/script.md
```

## 7. Storyboard Director

Purpose:

Convert the written script into visual scenes.

Responsibilities:

- Decide what is Blender animation.
- Decide what is motion graphics.
- Decide what is evidence-board/document visual.
- Decide what is image-frame animation.
- Decide what is text overlay.
- Decide camera movement and shot composition.

Storyboard format:

```text
Scene ID: S001
Time: 00:00-00:08
Purpose: hook
Visual: trophy machine, media cameras, hate-meter needle switches direction
Assets needed: trophy model, media lights, scoreboard text
Blender code: yes
Image prompt frames: optional
```

Output file:

```text
docs/videos/001-messi-hate-shift/storyboard.md
```

## 8. Asset Prompt Director

Purpose:

Write prompts for generated images or frame sequences that can become animation assets.

The user wants a workflow where 10 generated images can act as sequential frames. Each image is shown for about 0.02 seconds or another chosen duration to create motion.

Important correction:

At 0.02 seconds each, 10 images is only 0.2 seconds of animation. That can work for quick smear frames, impact flashes, transformations, or stylized punch effects. For longer motion, use more frames or combine with Blender camera/object animation.

Prompt-pack format:

```text
Shot: S004 Messi media-myth transformation
Frame count: 10
Duration per frame: 0.02s
Consistency anchor: same character silhouette, same lighting, same background perspective
Prompt frame 01: ...
Prompt frame 02: ...
...
Prompt frame 10: ...
```

Rules:

- Keep character descriptions consistent across frames.
- Ask for same camera angle unless the motion requires a camera change.
- Use frame numbers and explicit incremental movement.
- Keep all generated assets in `assets/generated/` if added to repo.

Output files:

```text
docs/videos/001-messi-hate-shift/image-prompts.md
assets/generated/
```

## 9. Blender Animation Engineer

Purpose:

Write the Python code that creates the video visuals.

Responsibilities:

- Build reusable scene helpers.
- Animate symbolic football scenes.
- Add camera moves, lighting, speed lines, labels, and impact effects.
- Turn storyboard scenes into renderable Blender scripts.
- Keep generated outputs under `outputs/`.

Current script:

```text
scripts/01_cr7_slide_tackle_siu.py
```

Future structure:

```text
scripts/scenes/001_intro_hate_shift.py
scripts/scenes/002_chosen_one_origin.py
scripts/scenes/003_maradona_shadow.py
scripts/scenes/004_trophy_race_machine.py
scripts/lib/materials.py
scripts/lib/camera.py
scripts/lib/football_figures.py
scripts/lib/line_art.py
scripts/lib/text_boards.py
scripts/lib/render.py
```

Near-term coding priorities:

1. Extract reusable materials and object helpers from the current script.
2. Add a line-art/sketch helper.
3. Add reusable football-character primitives.
4. Add scene templates with camera and lights.
5. Add a preview-render mode before full render.

## 10. Render QA

Purpose:

Make sure outputs are not broken before wasting time on full renders.

Responsibilities:

- Run syntax checks on Python scripts.
- Open or inspect generated `.blend` output when possible.
- Render low-res frames first.
- Check camera framing.
- Check text readability.
- Check that assets are loaded.

Output files:

```text
outputs/previews/
outputs/final/
docs/videos/001-messi-hate-shift/render-notes.md
```

## 11. Memory and Context Layer

Purpose:

Make future Codex/Hermes sessions remember the channel direction, style, and architecture.

Use:

- `AGENTS.md`: permanent project instructions.
- `docs/CONTENT_ENGINE_ARCHITECTURE.md`: this architecture.
- `docs/style/channel-style-profile.md`: learned style memory.
- `docs/videos/*`: per-video research and scripts.
- `Hermes`: possible persistent/background task memory or future research loops.
- `Headroom`: context/token efficiency.
- `MemPalace`: memory system reference.
- `code-review-graph`: persistent code map once the repo has real structure.

Do not rely only on chat memory. Put durable decisions in repo docs.

## Recommended Folder Structure

```text
blenderyt/
  AGENTS.md
  README.md
  docs/
    CONTENT_ENGINE_ARCHITECTURE.md
    style/
      reference-videos.md
      channel-style-profile.md
      visual-rhythm-notes.md
    videos/
      001-messi-hate-shift/
        plan.md
        research-notes.md
        claims-ledger.md
        storyboard.md
        script.md
        image-prompts.md
        render-notes.md
  scripts/
    01_cr7_slide_tackle_siu.py
    lib/
      materials.py
      camera.py
      football_figures.py
      line_art.py
      text_boards.py
      render.py
    scenes/
      001_intro_hate_shift.py
  assets/
    reference/
    generated/
  outputs/
    previews/
    final/
```

## External Repo Usage Policy

Do not vendor every starred repo into this repo.

Use this rule:

```text
Tool/plugin used by Codex globally -> install/configure outside repo
Python/Blender helper code we write -> keep in this repo
Downloaded/reference assets -> keep out of git unless small and allowed
Research notes/scripts/storyboards -> keep in docs/
Generated renders -> outputs/, usually not committed unless tiny previews
```

## What To Build First

Start small and useful:

1. Create `docs/videos/001-messi-hate-shift/claims-ledger.md`.
2. Create `docs/videos/001-messi-hate-shift/storyboard.md`.
3. Refactor current Blender script into reusable helpers.
4. Build a 10-20 second proof-of-style intro.
5. Add a frame-sequence prompt pack for one impact shot.

The first proof-of-style should not try to be the whole video. It should prove the look:

```text
dramatic narration beat + trophy/media machine + Ronaldo/Messi visual metaphor + sharp camera movement
```
