# Same game. Same standard.

An 86.4-second vertical opinion short built from the creator's supplied audio, a revised first-person script, original animation and timed captions. This is a separate short; it does not replace the longer episode narration or the superhero crossover.

## What is actually in the voiceover

The opening sentence and “Again, very, very convenient” are excerpts from the supplied recording: 0.00–3.04 and 36.16–38.00 seconds. The remaining words are newly synthesized with the existing local **Kokoro `am_michael` stock voice**. This is a mixed-voice edit, not a clone of the creator. The full recording is preserved outside Git.

The argument now comes from the creator's perspective: frustration at being dismissed, suspicion of how football markets its stars, and a demand for consistent decisions. It uses the protected draw paths and the Egypt/Austria controversies. The precise conditions and FIFA's explanation remain spoken. Secret payments, deliberate fixing and the manipulated Spence image are not presented as established facts. [EVIDENCE.md](EVIDENCE.md) records the supporting critics, counterevidence and open leads.

## Files you edit

| File | Purpose |
|---|---|
| [NARRATION_ADDITIONS.txt](NARRATION_ADDITIONS.txt) | Eight paragraphs of new speech, one per scene. Edit this before resynthesizing. |
| [NARRATION.txt](NARRATION.txt) | Complete spoken edit, including the two recording excerpts; derived from the audio assembly. |
| [edit.json](edit.json) | Recording in/out points, paragraph order, scene labels, factual labels and on-screen source credits. |
| [timeline.json](timeline.json) | Measured audio timing and 2,592-frame budget. Regenerate after any speech edit. |
| [assets/narration.ogg](assets/narration.ogg) | Finished compressed mix bundled for the Mac; regenerate after changing narration. |
| [captions.srt](captions.srt) | Word-anchored phrase subtitles for another editor. |
| [EVIDENCE.md](EVIDENCE.md) | Claim ledger and source register. |
| [../../../../blender/rules_short_scene.py](../../../../blender/rules_short_scene.py) | Blender scene construction, camera cuts and animation. |
| [../../../../blender/rules_short_art.py](../../../../blender/rules_short_art.py) | Procedural stadium, figures, pitch, ball and graphic objects. |
| [../../../../tools/run_same_standard.sh](../../../../tools/run_same_standard.sh) | One-command Mac build and playback with packed narration. |
| [../../../../blender/animation_compat.py](../../../../blender/animation_compat.py) | Reads animation curves across Blender 4.5 and 5.x Action APIs. |
| [../../../../tools/rules_short.py](../../../../tools/rules_short.py) | Audio edit, timing derivation, original sound accents, caption design and MP4 finishing. |

The new supplied video was inspected as an **art/motion reference only**: dramatic dark architecture, purple/navy shadows, bold contours, close-ups and accelerated action. None of its footage, soundtrack or dialogue is in this short. The football action is an editorial illustration, not a forensic recreation of match footage. It cannot establish what happened in a disputed tackle.

## Rebuild on Windows

Run from the repository root in PowerShell. Choose fresh output names for every take; the tools refuse to overwrite previous media.

```powershell
# 1. Generate revised paragraphs with the already-installed local voice runtime.
.studio/envs/voice/Scripts/python.exe tools/neural_voice.py episodes/002-ronaldo-hate-psychology/shorts/same-standard/NARRATION_ADDITIONS.txt --output .studio/shorts/consistent-rules/voice-NEW --speed 1.10 --threads 4

# 2. Set your recording's actual path, then assemble speech and measured scene times.
$recording = Read-Host 'Full path to your source M4A recording'
.venv/Scripts/python.exe tools/rules_short.py audio --edit episodes/002-ronaldo-hate-psychology/shorts/same-standard/edit.json --recording "$recording" --voice .studio/shorts/consistent-rules/voice-NEW --output .studio/shorts/consistent-rules/audio-NEW

# 3. Align the full, newly edited voiceover.
.venv/Scripts/python.exe -m studio align-captions .studio/shorts/consistent-rules/audio-NEW/voiceover.wav --text .studio/shorts/consistent-rules/audio-NEW/NARRATION.txt --output .studio/shorts/consistent-rules/captions-NEW --model tiny

# 4. Render native portrait frames from that exact measured timeline.
& '.studio/bin/blender-4.5.13-windows-x64/blender.exe' --background --factory-startup --python-exit-code 1 --python blender/rules_short_scene.py -- --timeline .studio/shorts/consistent-rules/audio-NEW/timeline.json --audio .studio/shorts/consistent-rules/audio-NEW/mix.wav --output .studio/shorts/consistent-rules/frames-NEW --render --resolution 1080 1920

# 5. Finish audio, designed captions, evidence labels and a playable MP4.
.venv/Scripts/python.exe tools/rules_short.py finish --frames .studio/shorts/consistent-rules/frames-NEW --audio .studio/shorts/consistent-rules/audio-NEW --edit episodes/002-ronaldo-hate-psychology/shorts/same-standard/edit.json --alignment .studio/shorts/consistent-rules/captions-NEW/alignment.json --output .studio/shorts/consistent-rules/final-NEW
```

## Mac: build, open and play with narration

Open **Terminal on the Mac**. Paste these three lines (the first is your existing clone location):

```bash
cd ~/Desktop/Movies/YoutubeBlen
git pull --ff-only
bash tools/run_same_standard.sh
```

The launcher finds Blender in `/Applications/Blender.app`, builds the scene with the included compressed narration, and then opens `output/same-standard-COMMIT/consistent-rules.blend`. Building is quick compared with rendering all frames. No Python packages or model downloads are needed on the Mac. The added narration is only **815 KB**; generated frame sequences and AI models are not in the pull.

1. Once Blender opens, keep the **3D viewport** in camera view. It is saved with overlays and gizmos hidden, using saved flat lighting and texture colors.
2. Move the pointer over the **timeline at the bottom** and press **Space** to play or pause. Playback begins at frame 1 and ends at frame 2,592 (86.4 seconds). Sound must be enabled on your Mac.
3. To return to camera view, use **View > Cameras > Active Camera** in the 3D viewport. If the colors look different, press **Z**, then **R** over that viewport.
4. Save your own edited copy using **File > Save As**. The launcher rebuilds its generated scene; do not keep manual edits only in that generated file.

`bash tools/run_same_standard.sh build` builds without opening the window. `bash tools/run_same_standard.sh render` renders all 2,592 native portrait PNGs into the same output folder. That takes substantially longer. These are frames, not an MP4; the Windows finishing command above adds designed headlines, captions, source credits and the final AAC track. The editable Blender scene already contains the animation and packed narration, but those finishing overlays live in `tools/rules_short.py`.

If Blender closes, the launcher prints the end of `output/same-standard-COMMIT/build.log`. Open that log and send its ending; preserve the generated folder. This revision uses Workbench and the current layered Action API to avoid the old Eevee identifier and removed `Action.fcurves` paths. It builds successfully on Windows Blender 4.5.13; this is not confirmation that the prior native Mac 5.2 crash is resolved.

Git includes source, approved art, text, timing, captions and `assets/narration.ogg`. Original recordings, model files, environments, frame sequences, final MP4s and generated `.blend` files stay ignored. The full finished MP4 is available locally on Windows at `.studio/shorts/consistent-rules/final-hd/same-standard.mp4`; the packed WAV version of the scene is alongside the original frames in `scene-final-hd/`.

## What “synced” means here

Scene lengths come from decoded audio sample counts, not estimated reading speed. The output is padded with silence to an exact video-frame boundary, and animation uses that shared clock. Caption timing uses local Whisper word anchors: 191 of 198 script words matched directly; seven names/compound words required estimated timing. This is not phoneme-level forced alignment or lip-sync. The athletes are not speaking characters.

To sharpen a beat, change the camera/action timing inside its scene while keeping the measured scene boundary. To change the argument or paragraph length, regenerate speech, timeline, captions and frames in that order. Increasing FPS alone does not improve acting: pose changes, contact, anticipation, camera staging and readable silhouettes are what make the motion communicate.

## Memory and tools

Codex performed the writing/research and wrote the animation. Local tools transcribed, synthesized, rendered and encoded. Selected ECC skills guided the process. Hermes did not generate this short or retrain a model; the studio's explicit feedback ledger records the creator's direction for future retrieval. No paid remote video job or automatic social publishing was run.
