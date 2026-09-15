# Creator workflow — 2026-09-05

## Recommendation

Build an opinion-driven football documentary studio around Codex, versioned episode files, Blender, FFmpeg, yt-dlp, one transcription engine, and one editor. Spend effort on a recognizable voice and reusable visuals before adding autonomous publishing or more agent frameworks. These are recommendations, not installation or render claims.

## What the folder actually contains

- Root `episodes/001-messi-hate/` is the editorial authority, as established by the integration plan. `external/blenderyt/` is an imported Git submodule with useful scene prototypes and competing project documentation; treat it as reference until selectively promoted.
- A detailed 12-minute production script already exists. It mixes strong visual ideas with repeated spoken evidence disclaimers. Source IDs are discovery records, not proof that their linked pages were checked.
- Existing Blender prototypes are `external/blenderyt/scripts/01_cr7_slide_tackle_siu.py` and `external/blenderyt/scripts/scenes/001_chosen_boy_maradona_shadow.py`. Their presence does not establish render readiness.
- Python and Git resolve on this Windows shell. Blender, FFmpeg, ffprobe and yt-dlp did not resolve on PATH. They may exist elsewhere; no installation inventory beyond this check is claimed.
- Root Git has staged and untracked work and no remote reported by `git remote -v`. The submodule URL is not the root repository's publishing destination. Do not blindly push or overwrite it.

## Small production stack

| Role | Choice | Why / activation condition |
|---|---|---|
| Producer, writer, coding artist | Codex with existing skills | One coordinator reads canonical files, preserves the creator thesis, assigns bounded tasks and records handoffs. No new harness needed to start. |
| 3D and visual metaphors | Blender | Reusable pitch, trophy, silhouette, camera, lighting and timeline scenes. EEVEE previews; compare Cycles only for shots that benefit. |
| Media preparation | FFmpeg + ffprobe | Audio extraction, proxies, contact sheets, technical output checks and final encoding. |
| Reference acquisition | yt-dlp | Metadata/subtitles and authorized reference media; source and asset provenance stay attached. |
| Transcription | whisper.cpp, start with a small model | CPU fallback and Windows support; benchmark football names and Spanish/English samples. Choose one engine initially. |
| Final edit | Trial DaVinci Resolve Free on proxy footage | Editing, sound and finishing in one tool. Confirm responsiveness on the 4 GB Windows GPU before committing to it; the personal Mac may be a better edit workstation. |
| Research | Available search/browser tools; last30days when needed | Research historical records and current audience language separately. Add wigolo only if retrieval/caching solves a measured gap. |
| QA | FFmpeg first; OpenCV when needed | Add visual analysis only when a recurring inspection task warrants code. |
| Later 2D motion | Remotion | Useful for repeatable caption, stat-card and timeline compositions; add after the first finished episode and review its license for the intended use. |

Primary documentation checked 2026-09-05: [Blender rendering](https://www.blender.org/features/rendering/), [Blender requirements](https://www.blender.org/download/requirements/), [FFmpeg](https://github.com/FFmpeg/FFmpeg), [yt-dlp](https://github.com/yt-dlp/yt-dlp), [whisper.cpp](https://github.com/ggml-org/whisper.cpp), [Resolve](https://www.blackmagicdesign.com/products/davinciresolve), [Remotion](https://github.com/remotion-dev/remotion). No local performance benchmarks yet.

## Disposition of the supplied repos

All supplied lists were read. Star counts and marketing descriptions are not quality scores. The groups below are project-fit decisions; only linked shortlisted projects above and explicitly linked candidates below received live documentation checks. Remaining entries are triage from the supplied descriptions, not security or maintenance audits.

**Use selectively:** yt-dlp, OpenCV, existing ECC, last30days. Keep openai/whisper as model/reference documentation; use whisper.cpp as the initial runtime. PowerToys is an optional Windows convenience rather than a production dependency.

**One bounded trial later:**

- [ViMax](https://github.com/HKUDS/ViMax): test Script2Video on an approved short screenplay. Its pipeline connects multiple generation providers; measure usable seconds, consistency, latency and total provider cost. It must not rewrite the thesis or substitute generated footage for match evidence.
- [OpenCut](https://github.com/OpenCut-app/OpenCut): watch/trial candidate; current README directs users to the classic version while the new architecture develops. Do not make its development branch the only editor.
- [Hermes](https://github.com/NousResearch/hermes-agent): optional future background coordinator after one manual episode works. Avoid two competing producers and memories.
- [Understand-Anything](https://github.com/Egonex-AI/Understand-Anything) or code-review-graph: choose at most one when shared code becomes difficult to navigate. Neither replaces the editorial evidence ledger.
- VibeVoice: benchmark later if transcription/speaker structure or voice generation actually needs it. The prior `VibeVoice-ASR-BitNet` label was not validated as an installed official package; do not build around that assumption. [Official repository](https://github.com/microsoft/VibeVoice).
- wigolo, Agent-Reach, Scrapling, Puppeteer, MediaCrawler: pick one only for a specific retrieval gap; prefer the existing connector/API/browser route first.
- supervision: useful when actual tracking/detection requirements emerge. Datasette: when the evidence catalog outgrows Markdown. llama.cpp: when measured offline model needs justify its memory footprint. modly: only after model-specific GPU requirements and asset quality are tested.
- SkillSpector and Trivy: candidate inspection tools for future imports, not guarantees that an imported agent is safe.

**Reference material; do not bulk-install:** 12-factor-agents, superpowers, mattpocock/skills, agency-agents, pm-skills, addyosmani/agent-skills, taste-skill, marketingskills, awesome-claude-skills, spec-kit, ponytail, system-design-primer, project-based-learning, ClassicComputerScienceProblemsInPython, coding-interview-university, the-book-of-secret-knowledge. Extract a specific useful practice only when the existing skills cannot handle the job.

**Defer overlapping infrastructure:** opencode, jcode, ruflo, claude-octopus, OmniRoute, moltworker, TencentDB-Agent-Memory, MemPalace, headroom, Jenkins. No demonstrated orchestration, routing, memory or CI bottleneck here yet.

**Defer generic content factories:** ShortGPT, MoneyPrinterTurbo, youtube-automation-agent, AiToEarn. Revisit for an isolated caption/export/distribution component after a successful manual episode. Their automation positioning does not establish audience demand, originality, quality or revenue.

**Outside this channel's present needs:** FinceptTerminal, AI-Trader, Quant-Developers-Resources, Kronos, daily_stock_analysis, MiroFish, Cosmos, worldmonitor, Odoo, twenty, chatwoot, Go, imgui, godot, pascalorg/editor, needle, airi, RuView, bitchat, GhostTrack, MasterDnsVPN, hysteria, FreeDomain, rustdesk, iptv, streambert, system-prompts-and-models-of-ai-tools. Revisit only with a concrete production requirement. A second 3D engine or remote desktop layer adds no proven value to this first Blender workflow.

## Creator control and agent roles

Before research, capture the creator's thesis, emotional point, specific incidents and lines worth keeping. An opinion can be selected immediately; factual premises can remain pending. Research should find the strongest honest support and material counterevidence. It must not silently replace the thesis with the internet's preferred interpretation.

Use roles within the existing coordinator, loading only the relevant skills:

1. Producer: reads root context/status/decisions and active episode; names the next deliverable.
2. Writer: uses brand-voice and content-engine; drafts in the creator's direction with claim IDs in production notes.
3. Researcher: records exact sources, dates, excerpts, unresolved premises and counterevidence.
4. Technical artist: uses Blender/motion skills for a specific approved storyboard shot; returns script, settings and previews.
5. Reviewer: checks factual implications, visual readability, source links and preservation of the original argument.

Parallelize independent source gathering or code review. Keep thesis changes, script lock and scene promotion sequential. Handoffs include status, changed files, assumptions, unresolved issues, next action and whether a preview was actually inspected. Completion means the artifact exists and was checked; a plan is not a render.

## Animation across Windows and Mac

Codex can write scene-generation code, camera motion, keyframes, materials, lighting and compositing instructions. Blender executes and renders them. Quality requires repeated visual inspection; selecting a model alone does not guarantee finished animation.

User confirms the new MacBook Pro is employer-managed and reports personal use is permitted; chip may be M4 and actual unified memory remains unconfirmed. The reported 1 TB may refer to storage. Apple Silicon supports Blender's Metal backend, but speed and feasible scene size need a representative benchmark. Preserve the approved Git/Blender boundary; additional editing/transcription software depends on employer approval and compatibility.

First production experiment: a 15–20 second trophy/media-machine sequence, with three reusable shots: a trophy under a spotlight, cameras multiplying around it, and a pullback revealing a football pitch. Stylized metaphor, no invented score or event. Start at 720p/24 fps with low samples; inspect first/middle/last frames and motion before a 1080p pass. Record time per frame and memory, then estimate total render time from measured frames.

Each render job should pin Git commit and Blender version and include scene ID, asset paths, frame range, fps, resolution, engine, samples, seed and output directory. Render PNG sequences so interrupted work can resume. Git carries approved code/manifests/small assets; rendered media uses the approved transfer channel. Windows assembles and checks outputs. Do not put model weights or frame sequences into ordinary Git.

## Automation rollout and revenue feedback

1. Finish one manual loop: creator take → parallel drafting/research → script lock → recorded narration → animatic → selected Blender shots → edit → review → publish.
2. Automate repetitive preparation: metadata capture, proxy generation, transcription, render manifests and output validation. Cache by input/settings hash and retry failures at most twice before recording the blocker.
3. Add scheduling only after tasks have clear inputs, outputs and failure handling. No always-on swarm needed. Keep paid generation behind a per-experiment spending cap chosen by the creator; no paid jobs were opened in this review.
4. Produce one long-form episode and two or three self-contained vertical adaptations as the initial experiment. Treat cadence as a hypothesis, not a mandatory quota.
5. Review YouTube Studio at 48 hours and seven days: impressions and traffic source, CTR, first-30-second retention, average percentage viewed, returning viewers, production hours and spending. These are suggested manual checkpoints; no reminders have been scheduled.
6. Low click-through with healthy retention suggests testing packaging; early abandonment suggests the opening fails the title promise; a dip around a long explanation suggests rewriting that beat. Compare similar traffic sources and enough impressions before deciding. Change one main variable each episode.

Revenue depends on audience response and eligibility, not the number of installed repositories. Prioritize original commentary, recognizable animation and sustainable production cost. YouTube says its inauthentic-content policy addresses repetitive/mass-produced content and does not make all AI-assisted content ineligible: [TeamYouTube clarification](https://support.google.com/youtube/thread/356734251?hl=en&msgid=441497500). Verify current eligibility and disclosure requirements again at publishing time.

## Next implementation order

Confirm the Mac details; audit the first Blender prototype for paths and version compatibility; get a preview working; choose and benchmark the editor/transcriber on a short sample; only then promote reusable scene helpers and add automation. The present session changes the editorial workflow and provides the stack decision, not an installed or fully rendered studio.
