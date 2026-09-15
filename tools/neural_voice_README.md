# Local neural narration

This optional Windows tool uses Kokoro-82M through the CPU ONNX runtime. It generates a generic American English male guide (`am_michael`), not a clone of the creator or a footballer. The original script is read unchanged and stored beside the audio. No account, cloud speech call or per-character payment is used after downloading the dependencies/model.

The main studio environment and full-episode David guide remain intact. The isolated runtime is `.studio/envs/voice/`, and downloaded model data stays in `.studio/models/voice/` outside Git. This is a Windows production tool; the work Mac only needs its approved Blender/Git packet.

## Repeatable setup

Run from the project root in PowerShell. The lock records the tested Windows Python 3.12 environment.

```powershell
.venv/Scripts/python.exe -m venv .studio/envs/voice
.studio/envs/voice/Scripts/python.exe -m pip install -r tools/neural_voice-requirements.lock.txt
.studio/envs/voice/Scripts/python.exe tools/neural_voice_setup.py
```

The setup downloads only two data files from the maintained ONNX wrapper's official GitHub release. It checks both against SHA256 values published in the release API before using them. A verified existing model is reused. It neither executes downloaded scripts nor modifies global configuration.

## Generate and fit the opening

Always select fresh output folder names; existing takes are preserved. The following commands reproduce the current voice settings using new names.

```powershell
.studio/envs/voice/Scripts/python.exe tools/neural_voice.py episodes/002-ronaldo-hate-psychology/script/OPENING_NARRATION.txt --output .studio/audio/opening-neural-natural-v2 --threads 4
.studio/envs/voice/Scripts/python.exe tools/neural_voice_fit.py .studio/audio/opening-neural-natural-v2 --output .studio/audio/opening-neural-v2 --targets 10.8445 3.9645 8.9745 6.0095 --ffmpeg .venv/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe
```

Each take has four paragraph WAVs, a joined `narration-guide.wav`, exact narration text, and `timeline.json`. The report preserves source/audio hashes and measured sample counts. Generation uses four CPU threads and the unquantized 325 MB ONNX model; no GPU/Torch runtime is required.

Fitting uses FFmpeg's pitch-preserving `atempo` only for overlong paragraphs, with a strict 1.2 speed limit. Shorter paragraphs receive tail silence. Speech is never cropped to make it fit; an overrun raises an error. Global peak normalization targets -3 dBFS and reports RMS. This is peak normalization, not a claim of measured streaming loudness compliance.

## Verified opening take

On 2026-09-10, the 80-word opening generated naturally in 18.734 seconds of measured synthesis time, producing 30.944625 seconds of audio. The fitted take is `.studio/audio/opening-neural-v1/narration-guide.wav`, 29.793 seconds, 24 kHz mono PCM16. Paragraphs two and three use tempo factors 1.189125 and 1.090660; the others retain natural speed. Peak is -3 dBFS and RMS approximately -24.14 dBFS. Caption alignment is a separate speech-analysis step; paragraph boundaries alone are not word timestamps.

The voice is a new production candidate, not a recording of the creator. Audition the final mix before selecting it for publication. Only this opening was generated with Kokoro; the roughly ten-minute guide remains the earlier installed-system voice.

## Provenance and licenses

Reviewed official sources on 2026-09-10:

- [Kokoro model card](https://huggingface.co/hexgrad/Kokoro-82M): Hexgrad's 82M model, Apache-2.0 weights; author explicitly welcomes production and commercial deployment. The card also records its training-data attribution. Model licensing permits commercial deployment subject to the license; this does not certify all content added to a finished video.
- [Kokoro voice list](https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md): identifies `am_michael` as an American English male voice. It does not represent the narrator as a specific person.
- [Maintained ONNX wrapper](https://github.com/thewh1teagle/kokoro-onnx): MIT code, Apache-2.0 model, documented Windows/Linux CPU-capable ONNX dependencies and model download example.
- [Pinned release metadata](https://api.github.com/repos/thewh1teagle/kokoro-onnx/releases/tags/model-files-v1.1): the downloaded model hash is `beb0d1848dee9a49da392cc3df26958d46cfa35d321edf434f52949153f0df3a`; voices hash is `bca610b8308e8d99f32e6fe4197e7ec01679264efed0cac9140fe9c29f1fbf7d`.
- Dependency licenses remain in the isolated installation. The eSpeak-ng phonemizer dependency is not the Kokoro neural model; consult its included license before redistributing the runtime. The repository transfers our scripts and a dependency lock, not bundled dependency binaries.

Tests run without model downloads or inference: paragraph/source preservation, sample timing, speed bounds, checksum rejection, a real FFmpeg pitch-preserving fit, output duration/level and overwrite refusal. Actual neural inference is separately verified by the produced WAVs and reports.
