# Delivery verification — 2026-09-25

The completed local file is `.studio/shorts/consistent-rules/final-hd/same-standard.mp4`.

| Check | Actual result |
|---|---|
| Picture | 1080 × 1920, 30 fps, 2,592 frames, 86.4 seconds |
| Encoding | H.264 / yuv420p, AAC mono at 48 kHz; 16,630,514 bytes |
| Complete decode | Every video frame decoded; audio decoded to exactly 4,147,200 samples |
| Visual inspection | Nine encoded opening/middle/ending frames inspected, plus earlier design and motion samples |
| Voice mix | −16.55 LUFS, −1.48 dB true peak before AAC encoding; decoded AAC peak approximately −1.5 dB |
| Caption anchors | 191/198 words directly matched; seven estimated timings |
| Mac source build | Built and reopened in Windows Blender 4.5.13; OGG packed at frame 1 for 2,592 frames |
| Action compatibility | 1,750 real curves found through channelbags; all sampled keyframe interpolation settings linear |
| Viewport | Flat lighting, texture color, camera view, hidden overlays/gizmos survive reopening |
| Picture after compatibility fix | Frame 112 visually unchanged; mean absolute channel difference 0.000036 on a 0–255 scale |

MP4 SHA-256: `33f5593ab927d1cd01d55e3c6ae1ef9ea397714ac5837c9666ff1efae6d437b0`.

The original recording contributes 4.88 seconds. Additional speech uses the named Kokoro stock voice, not voice cloning. The figures are articulated, stylized anonymous illustrations. This is not exact reference motion transfer, identifiable player facial animation, or lip-sync. Scene changes share measured narration timing; ASR caption timing is not phoneme-level forced alignment.

Native Mac 5.2 execution remains unverified. The removed legacy Action API has been replaced, but the earlier Mac native crash cannot be declared resolved from Windows. The final captions and source labels are added during MP4 finishing, not stored as Blender viewport text.

No dependencies were added. The existing environment audit still reports twelve findings in its installed pip package; that Windows environment is not shipped in the Mac packet.
