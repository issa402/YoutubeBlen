# Soccer Documentary Channel

**On the Mac, start here: [exact Terminal and Blender steps](tools/MAC_START_HERE.md).** Clone `https://github.com/issa402/YoutubeBlen.git`, then use the standalone `episodes/002-ronaldo-hate-psychology/mac/opening-hd/` packet. It requires Git and Blender only.

## Start the studio

Open the generated `.studio/dashboard.html` for the production desk: video, narration, chapter cues, next edit actions and searchable files. Regenerate it with `.\studio.ps1 dashboard`. The current polished opening is `.studio/renders/opening-polished/video.mp4`.

First release: [Why Do Some Messi Fans Hate Ronaldo More Than They Love Messi?](episodes/002-ronaldo-hate-psychology/script/MASTER_PRODUCTION_SCRIPT.md). Folder ID 002 is preserved; release order is 1.

```powershell
.\studio.ps1 doctor
.\studio.ps1 dashboard
.\studio.ps1 context 002-ronaldo-hate-psychology --save
.\studio.ps1 episode-package 002-ronaldo-hate-psychology --output .studio/packages/my-release
```

Open `.studio/dashboard.html` for episode files, saved creator corrections and rendered artifacts. Read [the operating guide](tools/STUDIO_RUNBOOK.md) for source intake, transcripts, feedback, queue and exports. Use a new output directory for each production run so earlier results remain intact.

Use [production review](tools/PRODUCTION_REVIEW.md) to check script/audio agreement and export the measured chapter edit sheet. The reusable [creator-studio skill](skills/creator-studio/SKILL.md) connects this project to selected ECC writing, content, motion and verification workflows; agents read it through these project docs.

The current Mac code-only render instructions are in [MAC_START_HERE.md](tools/MAC_START_HERE.md). Generated `.studio/` media and downloaded tools stay outside Git; source Python, episode text, source records and the `mac/` folder are included. `external/blenderyt/` contains preserved reference source, including its local edits, as regular files rather than a required submodule.

Optional agents: `hermes-studio.ps1` (isolated project home), `vimax-studio.ps1` (CLI) and `vimax-web.ps1` (local web UI) require provider setup before AI requests. Installed dependencies are not a promise of authenticated generation. See [integration status](integrations/studio/REPOS.md).

The [Hermes guide](tools/HERMES_WORKFLOW.md) explains the agent loop, token costs and memory, and the episode-aware launcher passes fresh creator corrections. The [narration and editing guide](tools/NARRATION_AND_EDITING.md) links the complete 9:40 synthetic guide voice, measured timings and three-shot 30-second animation. The [recording script](episodes/002-ronaldo-hate-psychology/script/NARRATION.md) contains spoken text only. Render the longer opening from `episodes/002-ronaldo-hate-psychology/mac/opening/`.

An evidence-led soccer storytelling channel combining strong commentary, sourced reporting, and original Blender animation.

## Production architecture

```text
Personal Windows PC
Research, transcripts, scripts, Blender Python, media analysis, QA
                         |
                         v
                    Git repository
                         |
                         v
Restricted work Mac
Pull approved repository content, run Blender, render
```

No third-party project dependencies, AI models, credentials, research caches, or private source media belong on the work Mac. Follow employer policy at all times.

## Start every session

Read these files in order:

1. `PROJECT_CONTEXT.md`
2. `CURRENT_STATUS.md`
3. `DECISIONS.md`
4. The active episode folder under `episodes/`

## Current episode

`episodes/002-ronaldo-hate-psychology/`

Working question: **Why Do Some Messi Fans Hate Ronaldo More Than They Love Messi?**

The episode develops the creator's pro-Ronaldo view through status, rivalry and commercial promotion. It distinguishes documented events from interpretations. Episode 001 remains an earlier separate draft.

## Repository policy

- Commit scripts, manifests, notes, citations, and small approved assets.
- Do not commit credentials, model weights, raw downloaded videos, render sequences, or final videos.
- Do not push or publish without explicit approval.
- Use branches or worktrees for concurrent agent changes.
