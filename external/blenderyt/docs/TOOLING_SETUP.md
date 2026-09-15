# Tooling Setup

## What Is Installed In This Repo

This repo has a local Python virtual environment:

```text
.venv/
```

Installed for the YouTube/video-analysis lane:

```text
yt-dlp
opencv-python
supervision
scenedetect
```

System tool already available:

```text
ffmpeg
```

## How To Activate

```bash
cd /home/iscjmz/blenderanimations/blenderyt
source .venv/bin/activate
```

## How To Verify

```bash
cd /home/iscjmz/blenderanimations/blenderyt
.venv/bin/python scripts/tools/check_content_toolchain.py
```

## What Each Tool Does

`yt-dlp` gets public video metadata, captions, and downloads when allowed.

`OpenCV` reads frames, detects image differences, extracts colors, and supports motion/scene analysis.

`supervision` gives higher-level computer vision helpers on top of frame/image data.

`scenedetect` helps find cuts and scene boundaries in reference videos.

`ffmpeg` converts, trims, samples, and stitches video/audio files.

## What Is Already Installed Globally

These are already present on the machine from prior work:

```text
last30days skill
agent-reach skill
MemPalace skills
Hermes Agent
Headroom
ECC
GitHub CLI authenticated as issa402
```

## Repo Policy

Do not copy every external repo into `blenderyt` source code.

Use this layout:

```text
/home/iscjmz/blenderanimations/blenderyt       # our production repo
/home/iscjmz/blenderanimations/reference_repos # cloned reference/tool repos
```

Reference repos are for learning, inspection, and borrowing architecture ideas. Production code should be written cleanly inside `blenderyt`.
