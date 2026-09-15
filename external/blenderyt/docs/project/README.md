# Soccer Documentary Channel

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

`episodes/001-messi-hate/`

Working question: **Why is Lionel Messi facing such intense backlash now?**

The episode may examine corruption and rigging allegations, but it must distinguish documented facts, disputed incidents, inference, fan opinion, and the creator's commentary.

## Repository policy

- Commit scripts, manifests, notes, citations, and small approved assets.
- Do not commit credentials, model weights, raw downloaded videos, render sequences, or final videos.
- Do not push or publish without explicit approval.
- Use branches or worktrees for concurrent agent changes.
