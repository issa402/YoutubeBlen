# Decision Log
## 2026-09-17 - Reference-length action adaptation

Use all 260 source frames at their actual 30 fps cadence. Preserve reference main cut boundaries; subdivide the opening flight for camera staging. Keep previous eight-second and 5.4-second drafts separate. Version the generated toward-camera pointing/tumbling artwork and reconstructed city/warehouse plates; retain original supplied Ronaldo artwork. Native sleeve/elbow and cape deformation provide deterministic movement. This is a layered 2.5D adaptation with explicit limits, not exact footage replacement. Mac execution remains unverified and prior triangulation crash attribution remains only a hypothesis.

## 2026-09-16 - Precomputed Ronaldo mesh faces for Blender 5.2

**Decision:** Store the approved Ronaldo silhouette's 76 validated triangle faces in source. Do not call Blender's polygon tessellator while constructing this asset.

**Reason:** The first Mac run of the shared-art revision aborted Blender 5.2 with SIGTRAP/exit 133 before Python produced a traceback, while Blender itself passed a factory-startup check. Removing the only newly introduced native geometry operation preserves identical geometry and avoids that version-sensitive path. Windows clean-start construction and regression checks pass; Mac confirmation is still required.

## 2026-09-16 - Shared cast art from supplied Ronaldo reference

**Decision:** Treat the user-provided Ronaldo/Superman illustration as the approved visual reference. Preserve its original pixels on a manually outlined Blender mesh; no substitute face. Generate Messi/Omni-Man and Mbappe crouch/profile illustrations in the same clean cel style. Maintain the eight-second four-shot timing, profile arm gesture and clean camera viewport.

**Implementation:** Version and pack all artwork. Deform only outer lower portions of the Messi cape and the Mbappe pointing arm; retain the profile head stability check. The image service rejected Ronaldo background removal, so the original image is directly UV-mapped to its silhouette. Source and asset fingerprints protect resume; old renders require a fresh output directory. The generated characters approximate the shared style, while Ronaldo uses supplied artwork.


## 2026-09-15 - Longer sequence and readable profile gesture

**Decision:** Creator rejected the oversized hand and generic likenesses. Extend to eight seconds with cuts at frames 45/88/133. Preserve reference shot order while honoring the explicit side-profile correction. Replace the giant hand with a proportionate connected pointing arm, animated through a bounded mesh deformation; assert that the profile head remains unchanged. Messi and Ronaldo receive distinct smooth cel facial drawings.

**Assets:** Two generated Mbappe PNG cutouts are versioned with source, alpha-composited in Blender and packed into saved scenes; source fingerprints include asset bytes. Generated Messi/Ronaldo sprite requests were rejected by the image service, so those characters retain manually revised native artwork. Do not represent these faces as exact reproductions or the limited 2.5D staging as full character animation.




## 2026-09-15 - Four-shot superhero crossover

**Decision:** Recreate the creator-supplied screen recording's shot order and approximate timing: Messi as Omni-Man, Mbappe as a Ninja Turtle replacing Spider-Man, and Cristiano Ronaldo in a Superman-style role replacing Thor. The source is 4.334 seconds; use 104 frames at 24 fps (4.333 seconds) and cuts at 24/47/72. Retain a large foreshortened pointing hand followed by the doorway reveal.

**Art and delivery:** Original editable 2.5D artwork in a standalone `mac/superhero-crossover/` packet, with deterministic animation, clean camera viewport, and code-only Git transfer. This is a stylized reconstruction, not pixel-identical replacement footage. Source audio/UI are not copied. Original screen recording remains local, and existing openings stay available. No factual claim or narration revision is introduced.


## 2026-09-15 - Illustrated floating Messi opening

**Decision:** Follow the creator's supplied floating superhero reference with an original stylized Messi illustration, crossed arms, Argentina-inspired kit, blue cape and layered city. Use editable polygon/ink layers in Blender, deterministic cape vertex animation and a slow orthographic push-in. This is 2.5D artwork, not a fully sculpted likeness. The fictional pose is a visual metaphor, not a factual event.

**Delivery:** New standalone `mac/messi-floating/` packet, 12 seconds at 24 fps, clean camera viewport. Preserve the previous 30-second scene for editing. The existing 30-second narration and finish-opening contract do not automatically fit this shorter clip; editorial assembly remains separate. Five diagnostic frames and structured motion are verified on Windows; Mac execution and full sequence render remain pending.


## 2026-09-14 - Runtime-selected Eevee engine

**Decision:** Select Eevee from the identifiers Blender exposes at runtime, preferring `BLENDER_EEVEE_NEXT` for Blender 4.x and falling back to `BLENDER_EEVEE` for Blender 5.x. Fail with the available engine list when neither exists.

**Reason:** The first real Mac build on Blender 5.2.0 LTS rejected the Blender 4.5 identifier before scene construction. Blender's official 5.2 API documents `BLENDER_EEVEE`; the remaining scene sampling API is still available. Runtime discovery keeps the same scene portable without silently switching to Workbench or Cycles.

**Validation boundary:** Both identifier sets are covered by Blender-independent tests and the Blender 4.5 scene build is rechecked locally. The creator must rerun `build` on the Mac to establish successful Blender 5.2 execution.

## 2026-09-11 - One-repository Mac handoff and HD upgrade

**Decision:** Publish source, episode documents, tests, setup locks and standalone Blender packets to user-selected `issa402/YoutubeBlen`. Track imported `external/blenderyt` reference files directly, including local edits, and preserve its original Git metadata under ignored `.studio/git-archive/`. Use LF shell files and one normal clone/pull.

**Reason:** A staged gitlink omitted local imported changes. Source is approximately 0.9 MB; model/runtime/render data remains local. The Mac needs only permitted Git and Blender operations. `tools/MAC_START_HERE.md` gives exact Terminal commands and distinguishes silent frame output from the finished voiced MP4.

**Decision:** Use a new native-1080p scene, local stock Kokoro voice and canonical-script captions anchored to ASR timestamps. Preserve prior guides and the completed lower-resolution opening. Voice fitting is bounded and never crops speech; finishing refuses mismatched hashes or invalid timing and preserves input resolution.

**Validation boundary:** Nine native HD diagnostic frames are rendered and inspected; the full HD sequence and actual Mac execution remain pending. ASR matching is not perfect forced alignment, and a completed opening is not a completed episode.

## 2026-09-09 - ECC production desk and explicit review

**Decision:** Use a static, local production desk with episode switching, native video/audio controls, measured chapter cues, source/direction notes, searchable files and episode-scoped memory. Reuse installed ECC skills through `skills/creator-studio/SKILL.md`; no global instruction or plugin changes.

**Reason:** The next bottleneck is editing and finding the right current artifact. A visual desk and deterministic review reduce repeated file hunting and stale-context mistakes without requiring paid calls or a web service.

**Implementation:** `studio review` checks master/clean narration agreement, source IDs, master fingerprint, paragraph order/timing and WAV duration. Explicit asset manifests select current media. Reports distinguish file presence, draft decisions and complete production. Regular context now isolates active episode feedback and preserves all its corrections; long authority excerpts are marked. Guide generation refuses to silently ignore a conflicting clean narration file.

**Visual decision:** Preserve the original 3D composition and voice while adding restrained chapter typography and phrase captions to a separate polished cut. Its 720p frame contains upscaled 360p picture; this is not described as a new native-HD render. Caption phrase timing is approximate; decoded source audio is identical.

## 2026-09-07 - Recording text, motion sequence and Hermes bridge

**Decision:** Keep the creator's strong thesis in a clean recording script with source/evidence notes in the master. Generate an offline installed-voice guide and measured paragraph timings for review. Build a genuine three-camera 30-second opening, with cuts timed to the guide, while preserving the earlier eight-second scene.

**Implementation:** 1,416-word narration; full guide 580.198 seconds; opening guide 29.793 seconds; 720-frame voiced preview rendered/decoded. Blender creates original geometric silhouettes, not real-person likenesses. Mac code is standalone and defaults to 1080p; Windows proof is 640x360. Final performance and full-episode edit remain separate production work.

**Decision:** Pass Hermes a freshly generated, bounded episode handoff using unique query files. Transport task text through UTF-8 files to preserve literal quotes in Windows PowerShell. Retain all active episode corrections and the requested task; raise on an insufficient protected-context budget.

**Reason:** Installed Hermes did not automatically read the studio's feedback ledger. Immutable inputs prevent concurrent task mix-ups. Retrieval and deterministic local tools reduce unnecessary context; model retraining, active Desktop compression and a measured quota saving are not claimed.

## 2026-09-06 - First release and implemented studio

**Decision:** Promote the creator's Ronaldo-rivalry psychology angle to the first release in root `episodes/002-ronaldo-hate-psychology/`. Keep the historic ID and older 001 draft. Preserve raw opinion separately from sourced factual narration; do not fabricate corruption evidence or diagnose a fanbase.

**Reason:** The user explicitly selected this episode and pro-Ronaldo direction. Psychology and commercial records support narrower claims and forceful commentary without invented proof.

**Implementation:** CLI, explicit feedback memory, retrieval, queue, media preparation, transcripts, source records, episode packets and Blender export implemented/tested. Ship a code-only Mac folder and a locally rendered eight-second motion proof. Full episode requires recorded voiceover and final editing.

## 2026-09-06 - Integration readiness and Headroom correction

**Decision:** Hermes/ViMax use separate project environments and dependency locks. Authenticated generation requires provider configuration and a spending cap. Headroom wrapping requires an explicitly selected isolated Codex home because it writes active configuration.

**Reason:** Downloads/help checks do not imply a live provider workflow. Earlier Headroom global-side-effect description was incomplete; its guard now prevents accidental normal-profile changes.

## 2026-09-05 - Project-local Headroom launcher

**Decision:** Use Headroom through `codex-headroom.ps1` for future Codex CLI sessions. Keep creator corrections in the studio's explicit, reversible feedback ledger; do not enable automatic rewriting of project instructions from inferred failures.

**Reason:** Large tool outputs and retrieved context can be compressed locally, while explicit preferences remain reviewable. Context compression is not represented as guaranteed subscription savings.

## 2026-09-05 - Creator-led drafts and targeted source lock

**Decision:** The creator chooses the provisional opinion before research completes. Draft and research proceed together. Evidence reviewers correct particular factual premises and surface material counterevidence without silently replacing the thesis. Routine evidence checks stay in production notes; necessary qualifications remain in narration.

**Reason:** Preserve the creator's voice and momentum while keeping factual claims accurate. This supersedes instructions to wait for complete research before drafting or selecting any thesis.

## 2026-09-05 - Minimal studio and canonical files

**Decision:** Root episode/context files govern this workspace; imported blenderyt remains reference. Start with Codex, Blender, FFmpeg, yt-dlp, one transcription runtime and one editor. Hermes and other orchestration/memory frameworks are conditional. Full selection and activation criteria are in `tools/WORKFLOW_BLUEPRINT.md`.

**Reason:** The observed bottlenecks are conflicting documentation, script voice and an unverified render loop, not lack of agent frameworks. Supersedes the earlier recommendation to begin with every tool in the selective-tools list.

## 2026-09-05 - Mac hardware clarification

**Decision:** The new Mac is employer-managed; the creator reports permitted personal use. Continue the approved Git/Blender workflow. Verify actual chip, unified memory and Blender version before hardware-specific configuration; 1 TB is not treated as confirmed RAM.

**Reason:** Ownership is clarified, but hardware capacity and the permitted scope of additional software are not established.

## 2026-08-01 - Split-computer architecture

**Decision:** Windows performs research, AI orchestration, coding, transcription, and media analysis. The work Mac only pulls approved repository content and runs Blender.

**Reason:** Preserve Windows resources while using the Mac for Blender, without installing outside projects on the restricted machine.

## 2026-08-01 - Evidence-led opinion format

**Decision:** Strong opinions are allowed, but corruption and rigging claims remain allegations unless supported by reliable evidence.

**Reason:** Protect credibility, improve the story, and reduce legal/platform risk. The tension between allegation and proof can itself drive the narrative.

## 2026-08-01 - Canonical memory

**Decision:** Versioned Markdown and Git are the canonical project memory. Hermes memory, MemPalace, and chat archives are supplementary.

**Reason:** Searchable memory can retrieve stale or contradictory material; versioned decisions need a clear authority.

## 2026-08-01 - Selective tools

**Decision:** Begin with Hermes, last30days, wigolo, yt-dlp, VibeVoice ASR, FFmpeg, OpenCV, Codex, Git, and Blender. Add Puppeteer or additional agent packs only for defined requirements.

**Reason:** Avoid overlapping tools, instruction conflicts, excess RAM use, and maintenance burden.
