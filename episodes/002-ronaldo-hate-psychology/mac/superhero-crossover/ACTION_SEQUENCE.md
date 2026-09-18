# Extended action sequence

Entry point: `action_crossover.py`. This follows the latest reference's **260 frames at 30 fps (8.667 seconds)**, including its added opening action. The previous drafts remain available separately.

## Run on Mac

From this folder in Terminal:

```bash
bash action.sh build
```

After a successful build:

```bash
open -a Blender action-output/action-crossover.blend
```

Use `bash action.sh preview` for diagnostic frames or `bash action.sh render` for the full 1080p PNG sequence. Preview/render use a new output directory each time to preserve existing frames. The launcher prints the actual destination. Generated scenes pack their artwork. No Python packages are needed outside Blender.

The saved viewport uses Solid texture mode to avoid automatically starting material compilation. Render output shows the artwork correctly; Material Preview can be selected manually after opening. The Mac crash remains undiagnosed; Windows verification is not proof it has been fixed.

## Reference timing (zero-based source frames)

| Frames | Beat |
| --- | --- |
| 0–42 | Strike and backward tumble |
| 43–63 | Impact cutaway |
| 64–108 | Wide landing; foreground boots enter at 91 |
| 109–145 | Crossed-arm hover |
| 146–174 | Crouch/recovery |
| 175–207 | Toward-camera point and flash |
| 208–259 | Doorway silhouette, lightning, color reveal |

## What matches and what is reconstructed

The frame count and main shot boundaries follow the reference. City, warehouse and doorway backgrounds are AI reconstructions from reference frames, not exact original pixels. Characters retain the approved visual identities. Motion is layered 2.5D animation with keyframed body transforms, sleeve/elbow articulation, shape deformation and cape movement, not frame-perfect motion transfer or fully rigged 3D models. The Messi strike request was rejected by the image service, so native Blender sleeve/forearm artwork supplements his approved image. Impact anatomy is a stylized cartoon overlay. The preview is silent.

## Asset provenance and prompts

Built-in image generation produced these assets without a new Mac dependency:

- `action-point.png`: preserve approved Mbappe/Turtle identity and costume; redraw a three-quarter close-up with the hand foreshortened toward the camera and left; transparent background, clean cel outlines.
- `action-tumble.png`: preserve the same character in a full-body airborne pose, asymmetrically bent knees and bracing arms; transparent background.
- `action-city.png`: remove the floating character and screen overlays from the reference city frame; reconstruct obscured sky and architecture while retaining framing and colors.
- `action-warehouse.png`: remove the character and overlays from the reference warehouse frame; retain cracks, ceiling, floor perspective and blue-gray palette.
- `reference-doorway.png`: previously generated clean doorway/city plate, reused here.

All generated assets are bundled in `assets/`; originals supplied by the creator remain separately preserved.
