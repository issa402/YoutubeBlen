# First-release review desk

## Watch and listen

- [Production desk](../../.studio/dashboard.html): video, full narration player, chapter cues, next actions, files and saved episode corrections.
- [Polished opening](../../.studio/renders/opening-polished/video.mp4): branded presentation, chapter titles and phrase captions. The complete original audio is preserved. The 360p source picture is upscaled into a 720p frame; captions approximate phrase timing within measured paragraphs.
- [Chapter edit sheet](../../.studio/reviews/episode-002-v1/edit-timeline.csv) and [current production review](../../.studio/reviews/episode-002-v1/review.md).

- [Voiced 30-second opening](../../.studio/renders/opening-sequence-voiced/video.mp4): three animated shots, 720 frames at 24 fps, local 640x360 review render. Camera changes align with the guide's status and rivalry paragraphs.
- [Complete guide narration](../../.studio/audio/episode-guide-v1/narration-guide.wav): 9:40, installed synthetic voice for pacing review.
- [Clean recording text](script/NARRATION.md): 1,416 words. [Plain text](script/NARRATION.txt).
- [Measured chapter times](../../.studio/audio/episode-guide-v1/chapters.txt) and [paragraph timeline](../../.studio/audio/episode-guide-v1/timeline.json).

The audio is a timing guide, not the creator's voice. The full read uses a slower opening than the standalone 30-second cut; do not combine both openings. Guide captions use paragraph boundaries and need release-caption editing.

## Code and production files

- [Start on the Mac: exact clone, build, open and render commands](../../tools/MAC_START_HERE.md). Upgraded packet: [mac/opening-hd](mac/opening-hd/README.md). Nine native 1080p samples are verified; the full HD sequence is still to render.
- [Local neural opening voice](../../.studio/audio/opening-neural-v1/narration-guide.wav), [ASR captions](../../.studio/captions/opening-neural-v2/captions.srt), and [HD finishing commands](../../tools/HD_FINISHING.md). Windows local assets are excluded from Git.

- [Mac opening code and commands](mac/opening/README.md): build, preview, draft, full 1080p render. Run with Blender 4.5 LTS through the permitted Mac workflow. No AI tools or package installation on the Mac.
- [Reusable narration and assembly commands](../../tools/NARRATION_AND_EDITING.md).
- [Master script and visual direction](script/MASTER_PRODUCTION_SCRIPT.md).
- [Recording directions](script/RECORDING_GUIDE.md), [three Shorts](script/SHORTS.md), [titles/description/thumbnail concept](script/PUBLISHING_PACK.md).
- [Sources](research/SOURCE_REGISTER.md) and [claim ledger](CLAIMS_LEDGER.md).
- [Hermes setup, memory and token explanation](../../tools/HERMES_WORKFLOW.md).

## Verified and remaining

All 720 frames of the voiced opening and polished cut decode. H.264 video and AAC audio are present; narration is not truncated. Polished audio matches the source after decoding. Blender's motion report checks camera/object/light changes and foot clearance. The source and Mac packet match. Full local suite: 102 tests passed, 92% studio coverage. Desktop/mobile browser QA passed for the new production desk.

The visual style is original geometric illustration. The prior opening sequence is complete; the newer native-HD sequence has nine verified samples and still needs its full render. Neither is a photoreal football reenactment or the complete ten-minute film. Review the narration, choose the final voice, assemble remaining chapters and inspect the full export. GitHub destination is user-authorized `issa402/YoutubeBlen`; no video publishing or paid generation was performed.

Links into `.studio/` work on this Windows workspace. Generated media is ignored by Git and does not arrive on the Mac simply by pulling the code.
