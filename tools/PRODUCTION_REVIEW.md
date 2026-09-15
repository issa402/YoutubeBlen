# Review the episode before another edit

From the Youtube folder:

```powershell
.\studio.ps1 review 002-ronaldo-hate-psychology
.\studio.ps1 review 002-ronaldo-hate-psychology --output .studio/reviews/my-next-review
.\studio.ps1 dashboard
```

`review` checks the current files without changing the script, decisions or feedback.
The optional export creates `review.md`, `review.json` and `edit-timeline.csv` in a fresh folder.
Existing output is preserved. The current first-release export is `.studio/reviews/episode-002-v1/`.

The report checks that clean narration matches the master voiceover, that referenced source IDs exist,
and that the audio timing matches the master fingerprint, paragraph order/text and actual WAV duration.
When a guide becomes stale, the report labels the timing as estimated and identifies the mismatch.
The dashboard disables chapter playback cues when matching measured timing is unavailable.

Each chapter's edit sheet includes its words, measured or estimated time range, picture/action, direction
and internal evidence notes. The next three actions follow the files and recorded decisions. File presence
does not establish factual accuracy, source permission, an approved final voice or a completed episode.
Opinions remain opinions; the report does not replace the creator's thesis with a model's judgment.

The episode's `manifests/production-assets.json` selects the current audio, timing, opening and Mac instructions
using paths relative to the project root. Explicit selection prevents an old experiment from being silently
treated as the current release. Update these paths after making a new intended take, then regenerate the desk.

The desk is local and works without a running server. It includes video/audio controls, chapter navigation,
file search, episode switching and active creator corrections. It does not launch agents or paid jobs when opened.

## Verification

```powershell
.venv\Scripts\python.exe -m pytest --cov=studio --cov-report=term-missing -q
node --check studio/web/app.js
```

`tools/qa_dashboard.cjs` adds isolated Playwright checks when Playwright/Chromium are available. Point `NODE_PATH`
at the installed package directory and optionally `STUDIO_CHROMIUM` at a local Chromium executable. It opens
only the local generated desk, blocks external HTTP requests, and tests media, chapter cues, file search,
episode switching, keyboard focus and mobile overflow. Screenshots/report go to `.studio/qa/dashboard/`.
It never attaches to a personal browser profile.
