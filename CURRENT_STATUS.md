# Current Status

Last updated: 2026-09-15

## Current phase

First-release studio, narration and portable Blender code are ready for the GitHub/Mac handoff. Native 1080p diagnostic frames and the local neural opening voice are verified. Full 720-frame HD rendering and final HD voice/caption assembly remain pending. The existing 30-second polished review cut remains available on Windows.

Repository: `https://github.com/issa402/YoutubeBlen.git`, branch `main`. Mac entry point: [tools/MAC_START_HERE.md](tools/MAC_START_HERE.md). Source/text transfer is approximately 0.9 MB before Git compression/metadata; generated models, environments, media and credentials stay ignored.

## Active episode

**Working title:** Why Do Some Messi Fans Hate Ronaldo More Than They Love Messi?

Canonical folder: `episodes/002-ronaldo-hate-psychology/`. Folder ID 002 is retained; release order is 1. Creator take, master production script, source register, claim ledger and Shorts are saved there. Episode 001 remains an earlier separate draft.

## Completed

- New creator-requested `mac/messi-floating/` opening: 12 seconds / 288 frames, original layered cartoon Messi with crossed arms, blue cape deformation, hovering motion and city parallax. Five 960x540 diagnostic frames rendered in Blender 4.5 and motion-state assertions passed; default Mac output is 1920x1080. The new scene opens in camera view with overlays/gizmos hidden. This is a standalone replacement opening clip; narration retiming, integration with the existing 30-second cut, full frame rendering, and native Mac verification remain pending.

- New standalone `mac/opening-hd/` packet: articulated faceless figures, smoother geometry, metallic seamed football/trophy, parented feed typography, three cameras and preserved cuts at frames 357/572. Nine 1920x1080 diagnostic frames actually rendered with Blender 4.5.13 LTS on Windows; motion and PNG integrity checks passed. Full HD rendering and native Mac execution remain pending.
- The first Mac build on Blender 5.2.0 exposed its renamed Eevee engine identifier (`BLENDER_EEVEE` instead of Blender 4.5's `BLENDER_EEVEE_NEXT`). Runtime engine discovery now supports both and fails clearly if Eevee is unavailable. The compatibility path is unit-tested and Windows 4.5 is rechecked; Mac 5.2 still needs the creator's rerun after pulling the fix.
- Local Kokoro ONNX opening voice: exact 80 words, 29.793 seconds, stock American male voice. Model/voices verified against upstream SHA256; CPU runtime isolated. Bounded pitch-preserving fitting preserves speech. See `tools/neural_voice_README.md`.
- ASR caption alignment v2: 80/80 words matched, no interpolated words, estimated speech timestamps. `studio align-captions` preserves the source script and emits JSON/SRT/VTT. `.studio/captions/opening-neural-v2/`.
- `studio finish-opening` checks audio/text hashes, alignment success/coverage, cue timings, 720 frames/24 fps and source HD dimensions. Actual HD fixture encoding/decoding passed; the full Blender HD sequence is not yet rendered.
- Latest full suite: **152 tests passed, 93% studio coverage**. Studio and isolated voice lockfile audits report no known vulnerabilities; both environments pass `pip check`. Candidate source files are under 5 MB; common credential signature scan found no matches. The optional ViMax web lock was excluded after npm audit reported two moderate Vitest findings; build that UI only from a newly generated, audited lock.
- Imported `external/blenderyt/` files and local edits are preserved directly in the main repository; original Git history is archived under ignored `.studio/git-archive/`. One normal clone gets the source; no submodule fetch. Shell scripts use LF through `.gitattributes`.

- Redesigned `.studio/dashboard.html`: current video and narration players, chapter cue playback, visual/evidence directions, next edit actions, searchable files, episode switching and active episode corrections. Static local HTML/CSS/JS; no server, provider call or new runtime package required.
- Polished 30-second opening: `.studio/renders/opening-polished/video.mp4`, chapter typography and phrase captions, original composition and audio preserved. All 720 frames decoded. Source 640x360 picture upscaled into a 1280x720 presentation; approximate phrase caption timing. Original render/Mac source unchanged.
- `studio review EPISODE [--output .studio/reviews/NAME]` checks master/clean text agreement, source references and guide fingerprint/text/timing/WAV duration. Exports Markdown, JSON and chapter edit CSV. Current export `.studio/reviews/episode-002-v1/`. Asset manifest explicitly selects current files.
- Fixed regular context cross-episode feedback leakage and silent last-40 truncation. Long authority excerpts now identify omitted text. Guide generation rejects conflicting NARRATION.txt before speech/output creation.
- Validated reusable ECC workflow at `skills/creator-studio/SKILL.md`, referenced by project docs. Uses selected installed skills; not globally auto-registered and no configuration changes.
- Independent review fixes: malformed episode metadata cannot hide other episodes; chapter selection restores keyboard focus. Browser QA verifies video/audio, nine chapters, cue playback, search/groups, 20 local links, episode empty state, keyboard focus and 375px layout without overflow. Screenshots/report `.studio/qa/dashboard/`.

- Master V2 and clean NARRATION.txt/.md agree exactly: 1,416 words, nine chapters; three Shorts, nine reviewed source records, recording directions and publishing pack complete.
- Full synthetic timing voice: `.studio/audio/episode-guide-v1/narration-guide.wav`, 580.198 seconds (9:40), Microsoft David Desktop. Measured paragraph timeline, guide SRT and chapters alongside. This is not the creator's recorded final performance.
- New voiced opening: `.studio/renders/opening-sequence-voiced/video.mp4`, 30 seconds, 720 frames, 24 fps, 640x360 and AAC guide audio. All frames decoded, cuts at 357/572 verified, narration 29.793 seconds with no truncation/hold. Blender object/camera/light motion and ground contact validated. Earlier eight-second proof retained.
- Portable longer-opening code: `episodes/002-ronaldo-hate-psychology/mac/opening/`; three cameras, geometry, keyframes, self-contained scripts and 1080p default. Identical to canonical Blender source. Native macOS execution remains untested.
- Hermes episode launcher now passes fresh, bounded creator context. Unique immutable query files prevent concurrent-task overwrites; UTF-8 task transport preserves quotes/multiline text in PowerShell 5.1 and 7. Normal interactive mode remains available. See `tools/HERMES_WORKFLOW.md`.
- Studio CLI: episodes, provenance, search, explicit/revocable feedback memory, manual metrics, job queue, dashboard, media preparation/transcription, Blender packets and PNG-to-MP4 assembly.
- Main dependencies and portable Blender installed. Blender ZIP checksum verified before execution. Real speech fixture transcribed successfully; synthetic audio/video and silent media smoke tests passed.
- Corrected eight-second animation: `.studio/renders/intro-motion/video.mp4`, 192 frames, 24 fps, 640x360, no audio. First/middle/last frames inspected and all frames decoded.
- Code-only Mac packet: `episodes/002-ronaldo-hate-psychology/mac/`. 1080p manifest, identical scene source, launch script and error log instructions. Bash syntax passed; actual Mac execution untested.
- First-release production packet: `.studio/packages/first-release-v2/` contains narration.txt, shots.json, earlier reusable Blender source and the new standalone opening sequence. `tools/NARRATION_AND_EDITING.md` contains repeatable voice/mux commands.
- Full suite: **102 passed, 92% studio coverage** on 2026-09-09. Includes real full-video polish/audio preservation, review freshness/path checks, memory isolation, PowerShell/Python task transport and dashboard models. Isolated Chromium browser QA also passes; JavaScript syntax, Python compile and diff whitespace checks pass. Earlier dependency checks clean; no packages added this pass.
- Hermes 0.21.0 installed/CLI checked in isolated env. ViMax dependencies/runtime import/CLI and web build verified. Provider authentication/generation not performed.
- Explicit creator corrections saved and included in future context handoffs; no automatic model retraining or causal audience learning claimed.

- Floating-opening verification: 159 tests and 11 subtests passed, 93% studio coverage; source compilation, Mac packet parity and Bash syntax passed. Five 960x540 frames rendered; middle frame visually inspected. Full sequence and Mac execution remain unverified.
- Floating-opening release audit: no new Python dependencies or external assets. The existing Windows environment audit reports vulnerabilities in its old pip 25.0.1 installer (fixes through 26.2); that environment is not shipped to the Mac. Dependency remediation is outstanding; the code-only Blender packet requires no pip.

## Next actions

1. Review the clean narration and synthetic guide; choose/record final performance. Align the remaining eight chapters' visuals to that take. The completed video is the opening, not the finished ten-minute episode. Full guide's normal-speed opening is 34.283 seconds; standalone opening guide uses rate +1 to fit 30 seconds.
2. Follow `tools/MAC_START_HERE.md` to clone/pull, build, open the editable scene, inspect previews, then render the 720 silent PNGs. Return permitted frames/logs for Windows voice/caption finishing.
3. Configure providers and a spending cap before unattended Hermes/ViMax model calls. No paid calls, publishing, automation schedule or remote agents were started.
4. Understand-Anything is downloaded but not built/analyzed. Local search works. last30days CLI help passed, but no representative fan-sentiment sample was collected.
5. GitHub destination is `issa402/YoutubeBlen`; source publication is explicitly authorized. Generated `.studio/` outputs stay outside Git. Imported reference code is included as ordinary files with local Git history preserved separately.

## Earlier audit snapshot — superseded by implementation above

- Read both supplied repository lists, root project material and relevant imported production documentation.
- Saved `tools/WORKFLOW_BLUEPRINT.md`: stack selection, repo triage, agent roles, animation handoff, automation rollout and audience feedback loop.
- Changed editorial standards and episode brief to preserve creator intent and allow drafting before source lock. Revised the opening/promise as a concrete voice example.
- Root files remain canonical; imported project docs are reference. No imported files were overwritten.
- Python/Git resolve on Windows PATH; Blender/FFmpeg/ffprobe/yt-dlp do not. This is not a full installed-app inventory.
- User confirmed the new Mac is employer-managed and reports personal use is allowed; chip may be M4. Reported 1 TB is ambiguous and may be storage. Exact RAM/chip/Blender version and render-transfer method remain unverified.
- No software installed, paid generation started, automation scheduled, render executed or Git push performed. Root has existing staged/untracked work and no configured remote reported.
- The script's existing 2026 result and disciplinary passages are not verified by this audit. Source-register URLs remain discovery material pending content checks.

## Local studio implementation update

- Headroom 0.37.0 is installed in the project `.venv`, with source downloaded under `.studio/repos/headroom`.
- `codex-headroom.ps1` now requires an explicitly selected isolated `.studio/codex-home` session because upstream wrapping writes active configuration. Current Desktop traffic was not rerouted and no token/account savings were measured.
- Added `tools/HEADROOM_AND_3D_GUIDE.md` documenting image-to-2.5D, generated mesh, photogrammetry and Astra-scripted Blender workflows.

## Earlier episode questions — not part of first release

- Exact meaning of the proposed "2026 was robbed so Lamine and Messi played" claim is unclear.
- Exact match/minute/context for the alleged 2022 Mac Allister handball needs identification.
- An employer-approved method for retrieving Mac render previews must be confirmed.
