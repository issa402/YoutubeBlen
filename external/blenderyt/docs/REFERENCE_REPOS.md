# Reference Repos And Installed Tooling

## Production Repo

```text
/home/iscjmz/blenderanimations/blenderyt
```

This is where our Blender Python scripts, docs, storyboards, claims ledgers, and channel workflow live.

## Reference Repo Folder

```text
/home/iscjmz/blenderanimations/reference_repos
```

These repos were cloned for inspection, architecture ideas, and possible selective integration. They are not automatically part of the production code.

```text
MediaCrawler
MoneyPrinterTurbo
Scrapling
ShortGPT
code-review-graph
supervision
wigolo
youtube-automation-agent
```

## Cloned Reference Repos

| Repo | Local folder | Role |
|---|---|---|
| `KnockOutEZ/wigolo` | `reference_repos/wigolo` | Local-first MCP/web search, fetch, crawl, research layer for Codex. Installed through `npx wigolo init --agents=codex --no-warmup`. |
| `darkzOGx/youtube-automation-agent` | `reference_repos/youtube-automation-agent` | Reference architecture for content strategy, script writer, thumbnail, SEO, production, publishing, analytics agents. |
| `harry0703/MoneyPrinterTurbo` | `reference_repos/MoneyPrinterTurbo` | Reference for automated video generation pipelines. Do not copy blindly. |
| `RayVentura/ShortGPT` | `reference_repos/ShortGPT` | Reference for short-form video workflows. |
| `NanmiCoder/MediaCrawler` | `reference_repos/MediaCrawler` | Reference for crawling social/media platforms. Use carefully and legally. |
| `D4Vinci/Scrapling` | `reference_repos/Scrapling` | Adaptive web scraping/fetching reference. Useful for public web extraction patterns. |
| `roboflow/supervision` | `reference_repos/supervision` | Computer vision helper reference. Also installed in `.venv` as a Python package. |
| `tirth8205/code-review-graph` | `reference_repos/code-review-graph` | Persistent code intelligence graph. More useful once this repo has multiple modules and helpers. |

## Installed Locally For This Repo

Repo-local virtual environment:

```text
/home/iscjmz/blenderanimations/blenderyt/.venv
```

Installed packages:

```text
yt-dlp
opencv-python
supervision
scenedetect
numpy
```

Check command:

```bash
cd /home/iscjmz/blenderanimations/blenderyt
.venv/bin/python scripts/tools/check_content_toolchain.py
```

Verified output should include:

```text
OK yt_dlp
OK cv2
OK supervision
OK scenedetect
OK numpy
OK ffmpeg
```

## Installed / Available Globally

These are already installed outside this repo:

```text
ECC
Hermes Agent
Headroom
MemPalace skills
last30days skill
agent-reach skill
wigolo for Codex through npx/MCP
GitHub CLI authenticated as issa402
```

## Wigolo Status

Initialized with:

```bash
npx -y wigolo init --agents=codex --no-warmup
```

Doctor command:

```bash
npx -y wigolo doctor
```

Current status:

```text
Overall: OK
Browser engine: installed, Chromium OK
Search backend: core
Search engines: multiple OK
Embeddings: lazy, downloads on first use
ML reranker: not installed, lazy/off
LLM synthesis: no key configured
```

Meaning:

- Search/fetch/crawl style functionality is available through the wigolo MCP layer.
- Research/agent synthesis inside wigolo needs an LLM key or local model if we want wigolo itself to write summaries.
- Codex can still synthesize from raw evidence without giving wigolo an LLM key.

## How The Tools Work Together

```text
Research Scout:
  last30days + Agent-Reach + wigolo + Scrapling + MediaCrawler reference

Inspiration Analyzer:
  yt-dlp + OpenCV + supervision + scenedetect

Script / Storyboard:
  ECC content-engine + channel docs + claims ledger

Blender Coding:
  Blender Python + scripts/lib + scripts/scenes

Memory / Repo Intelligence:
  AGENTS.md + docs + Hermes + Headroom + MemPalace + code-review-graph later
```

## What Not To Do

Do not vendor all reference repos into `blenderyt`.

Do not run social/media crawlers against private/login-gated platforms without explicit permission and a legal/safe workflow.

Do not let video automation repos publish to YouTube automatically until we have manual review, account setup, and privacy defaults.

Do not present controversial sports claims as proven fact unless the claims ledger has reliable sources.
