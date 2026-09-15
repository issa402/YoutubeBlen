# Touchline Studio runbook

Run PowerShell commands from the YouTube folder. `studio.ps1` uses the local `.venv`; generated assets go under ignored `.studio/`. Creator scripts and source records live in `episodes/`. Downloaded upstream source is not evidence that its provider integration works.

Current first release: `002-ronaldo-hate-psychology`. See [Hermes workflow](HERMES_WORKFLOW.md) for the episode-aware agent handoff and [narration/editing](NARRATION_AND_EDITING.md) for the complete synthetic voice guide, timings and 30-second Blender opening. Examples below use the current episode.

## Check and start

The redesigned desk puts the current preview, audio player, chapter edit directions and episode memory in one place. Chapter buttons can play the matching guide audio from that point. See [production review](PRODUCTION_REVIEW.md) for validation and CSV export, [opening polish](OPENING_POLISH.md) for the styled cut, and the project [creator-studio skill](../skills/creator-studio/SKILL.md) for the ECC workflow.

```powershell
.\studio.ps1 doctor
.\studio.ps1 review 002-ronaldo-hate-psychology
.\studio.ps1 context 002-ronaldo-hate-psychology --save
.\studio.ps1 index
.\studio.ps1 search "rivalry"
.\studio.ps1 dashboard
```

Open `.studio/dashboard.html` for a local snapshot. Regenerate after new work. The dashboard never launches jobs. To recreate installed dependencies, run `tools/setup_studio.ps1`; this downloads pinned packages and can require network approval.

## Your voice and learning

```powershell
.\studio.ps1 new 002-new-story --title "My next football story" --take "My actual opinion in my own words"
.\studio.ps1 feedback 002-ronaldo-hate-psychology "Keep my sentences direct and retain my metaphors" --kind voice
.\studio.ps1 learn
.\studio.ps1 context 002-ronaldo-hate-psychology --save
.\studio.ps1 revoke FEEDBACK_ID
```

Feedback is an explicit, reversible preference ledger retrieved into future handoffs. It does not train the model, infer facts from your preferences or automatically improve an unattended agent. Pass the saved handoff to Codex when starting a new task. The dashboard and JSON history expose the stored corrections.

Record real audience experiments after publication:

```powershell
.\studio.ps1 metrics 002-ronaldo-hate-psychology --impressions 1000 --ctr 5 --retention30 70 --hours 8 --cost 0
```

CTR/retention use percentages, not fractions. `hours` means production hours and `cost` means production cost in your consistently chosen currency. Metrics are recorded observations; recommendations still require interpretation and do not promise revenue.

## Sources and media

```powershell
.\studio.ps1 source 002-ronaldo-hate-psychology --url "https://example.com/article" --title "Replace with real article" --author "Author" --published 2026-09-05 --notes "Why this source matters"
.\studio.ps1 intake "https://www.youtube.com/watch?v=VIDEO_ID" --output .studio/media/reference-001
.\studio.ps1 prepare "C:\approved-media\clip.mp4" --output .studio/media/clip-001
.\studio.ps1 transcribe "C:\approved-media\voice.wav" --output .studio/media/narration-001 --model tiny
.\studio.ps1 demo --output .studio/demo/smoke-001
```

Replace example URLs/paths before use. Intake fetches available metadata/subtitles; media download requires `--download` and your right to obtain the material. Source registration never marks a quote verified or grants reuse rights. Transcription's first invocation downloads its speech model; it is not a fully offline first run. `demo` creates a synthetic video and exercises real FFmpeg/OpenCV preparation without web access.

## Windows to Mac animation

```powershell
.\studio.ps1 render-package --output .studio/packages/trophy-001 --seconds 8
.\studio.ps1 episode-package 002-ronaldo-hate-psychology --output .studio/packages/episode-001
```

The generic package has scene code, manifest and Mac commands in its README. The episode package includes episode-specific narration and shot instructions. These are production inputs; a finished narrated documentary still requires recording, render inspection and assembly. Follow the package README on the employer-approved Mac. Transfer only approved code/assets/previews through the permitted method. `.studio/` is ignored: generating a package does not automatically commit or push it. To use Git, deliberately copy/review the intended package into an approved versioned location first.

Once approved render frames are back on Windows:

```powershell
.\studio.ps1 assemble "C:\approved-renders\frames" --output .studio/renders/shot-001 --fps 24 --audio "C:\approved-media\voice.wav"
```

## Durable local queue and recovery

```powershell
.\studio.ps1 enqueue index
.\studio.ps1 enqueue dashboard
.\studio.ps1 run-next
.\studio.ps1 jobs
.\studio.ps1 retry JOB_ID
```

Each `run-next` executes one queued job. There is no background daemon or schedule. Claiming a job is transactional, so two workers cannot claim it simultaneously. Failed jobs allow at most three attempts. Fix the missing input before retrying. If a failed job already produced partial outputs, enqueue a replacement with a fresh output folder; retry preserves the original arguments and outputs. Running jobs cannot be retried while their worker might still be alive. After confirming an interrupted worker has exited, enqueue a replacement using a fresh output folder; the original running row remains as an audit record.

## Verification and optional integrations

```powershell
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m pytest --cov=studio --cov-report=term-missing --cov-fail-under=80
```

Tests use temporary workspaces and mocked network intake; media integration uses real synthetic FFmpeg/OpenCV processing. They do not establish live YouTube availability, speech-model download success, Mac rendering, publishing, provider authentication or paid generation success. See the integration registry for actual downloaded/installed/configured states. Headroom's guarded launcher and limitations are documented in `tools/HEADROOM_AND_3D_GUIDE.md`.
