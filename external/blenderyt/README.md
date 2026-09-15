# blenderyt

Blender Python animation experiments for motion-video scenes.

## First Scene: CR7 Slide Tackle + Siu Celebration

Script:

```text
scripts/01_cr7_slide_tackle_siu.py
```

What it builds:

- stylized stadium and football pitch
- upgraded stylized CR7 figure with red #7 kit, Ronaldo name tag, quiff hair, jaw detail, socks, and gold boots
- upgraded stylized Messi figure with blue #10 kit, Messi name tag, rounded hair, beard detail, socks, and blue boots
- CR7 enters through a glowing tunnel/ripple effect
- CR7 rushes in from off screen with speed trails and animated limb poses
- CR7 slide tackles through the action point with grass dust and impact shards
- Messi reacts with animated limbs and gets launched backward in a sports-impact gag
- a football pops and spins away during the collision
- CR7 switches into a celebration figure and jumps into a Siu pose
- stadium banners, LED boards, impact burst, speed trails, stadium lighting, cinematic camera movement

The figures are intentionally stylized primitive models. This avoids needing external copyrighted/realistic character assets and keeps the whole scene generated from code.

## Run On macOS

Interactive Blender preview:

```bash
cd /path/to/blenderyt
/Applications/Blender.app/Contents/MacOS/Blender --python scripts/01_cr7_slide_tackle_siu.py
```

Background render:

```bash
cd /path/to/blenderyt
/Applications/Blender.app/Contents/MacOS/Blender --background --python scripts/01_cr7_slide_tackle_siu.py -- --render
```

Outputs go to:

```text
outputs/cr7_slide_tackle_siu.blend
outputs/cr7_slide_tackle_siu_####.png
```

## How To Improve Next

1. Replace primitive figures with rigged low-poly characters.
2. Add real grass shader and stadium advertisements.
3. Add ball motion and contact timing.
4. Add camera shake at frame 74 impact.
5. Add crowd flash/emissive boards during the Siu celebration.
6. Render a low-res preview first before full quality.
