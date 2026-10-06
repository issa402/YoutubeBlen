# Current Status

Last updated: 2026-10-05

## Optional full OpenMontage workspace — October 5

Installed the pinned OpenMontage core Python dependencies, Piper package and Remotion composer in the ignored Windows checkout. Its local configuration has a zero-dollar `cap` and no `.env` provider keys. Added `openmontage.ps1` for doctor, Backlot, zero-key demo and a separate interactive free-mode Codex session. `doctor` reports 137 registered tools and `pip check` passes. Backlot is live on loopback port 4750; health returned OK. The upstream `world-in-numbers` zero-key Remotion demo rendered and probed as a 23.062-second 1920×1080/30 fps H.264/AAC MP4. This validates local composition, not a live agent-run soccer video or paid-model quality. `start-free` has not been executed; it would use Codex account allowance and requires a supervised first pilot. See `tools/OPENMONTAGE_FULL.md` for route selection and cost math. Paperclip/Creator Desk remain separate.
Upstream Remotion dependencies initially had three high and two moderate npm advisories; a patched lock overlay is tracked and cleanly reinstalled with zero npm audit findings. The isolated Python environment initially had pip advisories; pip 26.2.1 and a `pip-audit --path` check now report no known findings. The demo MP4 passed a full FFmpeg decode.

## OpenMontage reference pilot — October 5

Fetched OpenMontage at pinned commit `9327439db69021ab4b0e2776729bf3b58fdb5a87` into ignored `.studio/repos/OpenMontage/`. Added `tools/openmontage_reference.py`, which invokes upstream `SceneDetect` and `FrameSampler` with local FFmpeg/ffprobe and writes an ignored scene/frame report. No full OpenMontage producer, provider, Backlot or render pipeline was installed. The R04 pilot verified the source hash, extracted 16 frames and returned a report. Its FFmpeg scene detector found only one scene, missing the visually noted mid-clip change; the adapter fell back to even frame sampling and does not claim precise cut detection. `tools/OPENMONTAGE_REFERENCE.md` contains the run command and boundaries; the Paperclip Visual Director can use a supplied report as a candidate input, but it is not auto-dispatched. `claude-mem` was evaluated and deferred because episode-scoped explicit memory already exists and no token-saving comparison has been measured.

The Python regression suite passed: 218 tests and 17 subtests. Pytest reported one cache-write warning under `.pytest_cache`; tests still completed. Python compile and `git diff --check` passed.

## Paperclip agent control plane — October 3

Installed pinned `paperclipai@2026.1001.0` under `integrations/paperclip/`, with a lockfile and patched transitive overrides (`@grpc/grpc-js@1.14.5`, `svix@1.99.1`). The production npm audit now reports zero findings. Paperclip is running on the personal Windows PC at `http://127.0.0.1:3100`, bound to loopback. Its embedded PostgreSQL, secrets, logs and candidates are isolated in ignored `.studio/paperclip/`; no service or Mac installation was created. Start/reproduce with `paperclip.ps1` and `tools/PAPERCLIP_STUDIO.md`.

The real Paperclip company **Football Documentary Studio** now has a publishing goal, an episode-002 Same Standard pilot project, four Codex-backed agents (evidence, script, visual direction, release review) and four staged issues. Timer heartbeats are off. Agents use ACP with noninteractive permission requests denied and sandbox bypass explicitly false. The first Windows classic-CLI attempt failed at sandbox setup (`SetNamedSecurityInfoW: 5`); the managed Codex-home auth symlink also failed (`EPERM`), and a forced `gpt-6.1-sol` was unsupported by this ChatGPT CLI login. The bootstrap uses the working ACP engine, existing self-managed Codex login and no model override.

One live Paperclip evidence run succeeded. It produced an unapproved 10-row candidate `claim-map.md` in the ignored project workspace for 0–46.112 seconds, with source IDs, counterpoints and verification gaps; the Paperclip issue is `in_review`. It reused existing source records and did not newly verify the linked primary material. The other three issues remain backlog; script/visual/release agents are configured but have not been executed. Paperclip and the older Creator Desk do not auto-sync; Paperclip owns agent dispatch, while Creator Desk remains a media/artifact review workflow. No publishing, paid media job or automatic Mac operation was started. Bootstrap was rerun without duplicate records; launcher health, JS/PowerShell syntax and full repository regression passed (218 tests and 17 subtests) using a workspace-local pytest temp directory. Production npm audit is clean. The older Python venv still reports 28 advisories in three packages; the new Paperclip runtime does not use it.

## Hermes Agent connection — October 3

After creator feedback that the new desk had used a custom stage manager rather than the suggested orchestration repos, added a genuine selectable Hermes Agent backend to `studio/creator_worker.py`. The installed Hermes CLI v0.21.0 receives a project-stage handoff through `--query-file` and an isolated `.studio/hermes-home` profile, requesting `web` tools only, eight tool turns and a finite run budget. An environment allowlist prevents inherited Hermes dispatcher and bypass flags from widening that request. `--backend hermes` without `--execute` prepares only; actual inference still requires an explicit model and provider setup in that profile or an allowed provider API key. Candidate stdout, which may include session information, stays unapproved. The desk now shows the exact Hermes command for a prepared stage. No paid Hermes call was made, so provider authentication, model quality and cost remain unverified. The full suite passed 217 tests and 17 subtests before the environment hardening; 28 targeted tests and six subtests passed afterward. Paperclip was not installed at that point; the later section above records its completed setup. Updated `tools/CREATOR_SYSTEM.md` to make the current boundary explicit.

## Creator Studio orchestration — October 2

Built a local Creator Desk (`.\creator.ps1 desk`) with a SQLite stage machine, episode-scoped approved writing examples, bounded handoffs, optional read-only Codex CLI worker packets, a browser production board and local media review. Stages are research, script, audio, storyboard, animation, finish and review. Completed stages require a real file in the active episode or worker folder. The desk itself makes no model, paid, publishing or Git calls. A worker only calls Codex with explicit `--execute --model`; provider cost is unknown until reported by the account. See `tools/CREATOR_SYSTEM.md`.

Pinned HyperFrames, GSAP and ffprobe under `integrations/creator/`; npm audit reported zero findings. A local original `R04` tactical board proof with stock Kokoro guide speech rendered at `.studio/creator-demo/tactical-r04/final.mp4`: 6.133 seconds, 1280×720, 30 fps. It passed full MP4 decode, duration/FPS checks, AAC audio-stream inspection and midpoint visual inspection. This is a style and audio-clock proof, not a replacement for existing Blender character animation or an episode release. The browser/API returned two episodes, four references and ranged media playback. Focused suite passed 25 tests and six subtests; full suite passed 212 tests and 17 subtests before a targeted security fix, after which 12 relevant tests and six subtests passed. JavaScript syntax passed. Security review found and fixed a concurrent budget-reservation race and bounded local HTTP connections. The existing Python environment audit found 28 advisories in pip, PyJWT and urllib3; the new Creator Studio source does not use those packages. Mac execution and browser visual automation remain unverified. Large outputs and local database are ignored by Git.

## Reference and workflow audit — October 2

Added `tools/ANIMATION_REFERENCE_LIBRARY.md` and portable `tools/animation-references/catalog.json` with four new clip hashes, dimensions, durations, contact sheets and per-style production recipes. Re-sampled the September 24 dark comic reference; September 17 raw action recording was unavailable at its supplied temporary path, so prior corrections/project records anchor that entry. Audio was not transcribed or evaluated this turn. Defined narration-first animatic/shot timing, honest 2.5D versus rigged-motion limits, and repository decisions for HyperFrames, Impeccable, CodeGraph, Caveman, OpenRig and Paperclip. No new renderer, integration, provider call or animation was installed/run; these are documented recommendations. Existing video source preserved.

## Completed short — Same Standard, September 25

Source and Mac guide: `episodes/002-ronaldo-hate-psychology/shorts/same-standard/README.md`. Finished video: `.studio/shorts/consistent-rules/final-hd/same-standard.mp4` — 86.4 seconds, native 1080x1920, 30 fps, 2,592 frames, 16,630,514 bytes. All encoded frames decoded successfully. Nine encoded opening/middle/ending samples were inspected. The final AAC stream decoded to exactly 4,147,200 samples at 48 kHz; no truncation or decode error. `validation.json` preserves the video hash and timing results.

Voiceover contains 4.88 seconds of the supplied recording and named stock Kokoro speech for the revised first-person argument; it is not a voice clone. 191 of 198 script words matched ASR directly; seven timings are estimated. The mix measures -16.55 LUFS and -1.48 dB true peak. Creator preference is saved in explicit local feedback; Hermes did not execute generation.

Canonical Blender: `blender/rules_short_scene.py`, `rules_short_art.py`, `animation_compat.py`. The 21-camera scene uses articulated anonymous figures and an original packed background. Figures are stylized illustrations, not exact player likenesses or forensic match replays. The full WAV-packed editable scene remains in `.studio/shorts/consistent-rules/scene-final-hd/consistent-rules.blend`. The Mac launcher `bash tools/run_same_standard.sh` rebuilds from source using the included 815 KB `assets/narration.ogg`, packs the audio at frame 1, and opens Blender. Native Mac execution remains unverified; the removed Blender 5 Action.fcurves dependency has been replaced with layered channelbag traversal.

184 tests and 11 subtests passed before the final compatibility fix; nine targeted tests now pass, including three new action traversal regressions. The rebuilt compressed-audio packet passed native Blender 4.5.13 checks with exactly 2,592 audio frames packed. The source package, compact narration and Mac guide are ready; the final delivery response records the pushed commit. Existing pip audit reports 12 findings in the installed pip package; no dependencies were added. Full studio coverage previously measured 93%.

## Latest animation revision — September 18

Active visual task: the corrected ankle throw in `episodes/002-ronaldo-hate-psychology/mac/superhero-crossover/`. Read `ACTION_SEQUENCE.md` and the new `HOW_THIS_ANIMATION_WORKS.md` first. This replaces the previous punch/independent-tumble choreography.

New creator manual: `COMPLETE_ARCHITECTURE_AND_ANIMATION_GUIDE.md` maps the repository, active and legacy packet files, asset creation, 2.5D mesh/material/motion code, throw math, cameras, rendering, studio/Hermes roles, validation, editing recipes and three paths to lifelike motion (layered puppet, Grease Pencil or full 3D). The legacy packet README now points to the active 260-frame workflow.

Implemented: connected grip through frame 10, release at 11, flight toward the warehouse, wall recoil/drop, hovering arrival, new defeated Mbappe artwork, right-pointing profile pose and directional camera move into Ronaldo. Pure motion math is separate from native cel geometry. Blender verifies transformed ankle/palm contact, finger direction/framing and stable head vertices.

Complete playable result: `.studio/renders/action-throw-final-hd/action-crossover.mp4`, 1920x1080, 30 fps, 260 frames, 8.667 seconds, silent, 6.82 MB. Every encoded frame decoded successfully. Two diagnostic rounds and final encoded key frames were visually inspected. The generated `.blend`, frame PNGs, motion report and validation report are alongside the video. Full tests: 178 passed plus 11 subtests, 93% studio coverage; dedicated throw math tests reached 100% module coverage. Pip check and Bash syntax pass. Existing pip installer vulnerabilities remain in the Windows environment; this change adds no dependencies. Mac execution remains unverified and its prior crash is unresolved. This is reconstructed 2.5D animation, not exact source motion transfer. Hermes did not run live generation. The new creator correction is saved in local feedback, and a fresh preparation-only handoff includes it (9,157 characters; approximate 2,290 payload tokens excluding runtime overhead).

## Earlier studio phase

First-release studio, narration and portable Blender code are ready for the GitHub/Mac handoff. Native 1080p diagnostic frames and the local neural opening voice are verified. Full 720-frame HD rendering and final HD voice/caption assembly remain pending. The existing 30-second polished review cut remains available on Windows.

Repository: `https://github.com/issa402/YoutubeBlen.git`, branch `main`. Mac entry point: [tools/MAC_START_HERE.md](tools/MAC_START_HERE.md). Source/text transfer is approximately 0.9 MB before Git compression/metadata; generated models, environments, media and credentials stay ignored.

## Active episode

**Working title:** Why Do Some Messi Fans Hate Ronaldo More Than They Love Messi?

Canonical folder: `episodes/002-ronaldo-hate-psychology/`. Folder ID 002 is retained; release order is 1. Creator take, master production script, source register, claim ledger and Shorts are saved there. Episode 001 remains an earlier separate draft.

## Completed

- Earlier Mac compatibility experiment: Ronaldo's 76 stored mesh triangles pass Windows checks. Continued native Mac crashes were reported afterward. Tessellation was not established as their cause; the Mac crash remains undiagnosed.

- Shared-art revision: the creator's supplied Ronaldo/Superman illustration is preserved byte-for-byte as `ronaldo-approved.png`, mapped onto an outlined Blender mesh. Messi/Omni-Man and both Mbappe poses now use matching cel artwork. Ten 720p diagnostic frames rendered and visually checked together. Native 1920x1080 eight-second render completed: `.studio/renders/crossover-v6-hd/superhero-crossover.mp4`. All 192 frames decoded at 24 fps; silent preview. 164 tests and 11 subtests passed (93% studio coverage). Actual Mac execution remains unverified.

- Crossover revision: 192 frames / eight seconds, separate Messi/Ronaldo cel faces, matched generated Mbappe crouch/profile cutouts, and a proportionate connected pointing arm whose vertex animation leaves the head fixed. Assets are versioned and packed into the .blend. Complete 1280x720 preview: `.studio/renders/crossover-v4/superhero-crossover.mp4`; all 192 frames decoded and final shots inspected. 164 tests and 11 subtests pass (93% studio coverage). Mac/1080p execution remains unverified. Old four-second frames cannot resume under new source; use a fresh output directory.

- New `mac/superhero-crossover/` packet recreates the creator's supplied 4.334-second recording as 104 frames / 24 fps: Omni-Man Messi hover, Ninja Turtle Mbappe crouch, exaggerated pointing-hand close-up, then Superman-style Ronaldo doorway reveal. Default 1920x1080; original editable 2.5D polygons. Ten diagnostic frames rendered; camera cuts verified at 24, 47 and 72. Complete 960x540 preview rendered and encoded at `.studio/renders/crossover-v2/superhero-crossover.mp4`; all 104 frames decoded, corrected shot images visually inspected. Full suite: 163 tests and 11 subtests passed, 93% studio coverage. Mac execution and native 1080p render remain unverified. Existing local pip audit findings remain unchanged; this packet adds no dependencies.

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

## September 16 latest video adaptation — incomplete visual match

New `blender/reference_crossover.py` and matching Mac packet retain the current cast and add the reference's five-shot order, 162 frames at 30 fps. First diagnostic pass rendered; corrected a flash plane intersecting the pointing sprite. Full 720p comparison rendered and decoded: `.studio/renders/reference-v3/reference-comparison.mp4`, all 162 frames at 30 fps verified. Background generation hit its usage limit after one doorway plate; the city is a crop of that plate and the warehouse is procedural. The toward-camera pointing pose is not achieved: the existing profile sprite remains. Exact background/motion match requires further asset work. See the packet's `REFERENCE_SEQUENCE.md`.

Mac crash cause remains unconfirmed. Earlier statements that runtime tessellation caused SIGTRAP were hypotheses, not established diagnoses. The user reports continued crashes, potentially including the factory-startup command; a native Mac crash report is needed.
## September 17 extended action sequence

The latest supplied reference has 260 decoded frames at uniform 30 fps (8.6667 seconds). `blender/action_crossover.py` and the matching Mac packet implement the full timeline: strike, tumble, impact cutaway, landing/foreground boots, hover, crouch, foreshortened point, lightning reveal. New generated point/tumble sprites preserve the approved character direction; city and warehouse plates reconstruct the reference framing. Native sleeve/elbow articulation supplements the approved Messi artwork because the image service rejected the strike pose request. These are approximate 2.5D character performances, not frame-perfect motion transfer.

Native 1080p full render completed and inspected at `.studio/renders/action-final-hd/action-crossover.mp4`: all 260 frames decoded at 30 fps, 8.6667 seconds, silent, 6.74 MB. Full suite: 167 tests and 11 subtests passed; 93% studio coverage. Mac launcher syntax and generated-output ignore rules passed. Multiple diagnostic passes were visually inspected; fixed stale cuts, stretched sprite aspect ratios, crossed-arm overlap and dithered flash overlays. `ACTION_SEQUENCE.md` and `action.sh` are the Mac entry points. No new runtime dependency is needed on the Mac. The local dependency audit still flags the pre-existing pip25.0.1 installer; no dependency was added in this update. Mac crash cause remains unconfirmed.
