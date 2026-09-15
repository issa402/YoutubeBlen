# Blender Visual Plan

## Visual identity

Use a cinematic evidence-board/chess-match language rather than a generic slideshow.

### Recurring visual systems

- **Timeline tunnel:** Years appear as stadium tunnels the camera travels through.
- **Chessboard:** Institutions, tournaments, sponsors, teams, and players appear as labeled pieces. Use it as a metaphor, not literal proof of a conspiracy.
- **Trophy constellation:** International trophies illuminate along a timeline.
- **Evidence table:** Each disputed incident becomes a 3D case file with rule, angle, claim, and counterclaim.
- **Scale of certainty:** Visual meter moves among fact, dispute, allegation, and unknown.
- **Network map:** Commercial and institutional relationships appear only when supported by sources.

## Proof-of-concept sequence

Target: 30-60 seconds.

1. Dark stadium with distant crowd noise.
2. A penalty ball stops beside the year `2016`.
3. Camera follows Messi-like silhouette down a tunnel labeled `RETIREMENT` without using an unlicensed likeness asset.
4. Tunnel transforms into a chessboard.
5. Trophy pieces illuminate: `2021`, `2022`, `2022`, `2024`.
6. Red strings appear, then snap into evidence cards labeled `FACT`, `DISPUTED`, and `ALLEGATION`.
7. End on the question: `MIRACLE, PROTECTION, OR A STORY WE WANTED TO BELIEVE?`

## Technical requirements

- Procedural geometry where practical
- Text and colors driven from a JSON scene manifest
- 16:9 master composition
- Title-safe guides for later 9:16 crops
- Camera and lighting names validated by script
- Low-resolution preview mode
- Deterministic seed for procedural placement
- No downloaded add-ons required on the Mac

## Blender-native validation on Mac

- Required collections and objects exist
- Active camera exists
- At least one light exists
- Frame range matches manifest
- Resolution and FPS match manifest
- External asset paths resolve
- Render output path is approved
- Preview render completes
