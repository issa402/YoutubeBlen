# Project Instructions

## Mission

Build an evidence-led soccer documentary channel with compelling narrative structure and original Blender visuals.

## Required session behavior

1. Read `PROJECT_CONTEXT.md`, `CURRENT_STATUS.md`, and `DECISIONS.md` before changing the project.
2. Update `CURRENT_STATUS.md` after meaningful work.
3. Record durable architectural/editorial choices in `DECISIONS.md`.
4. Never convert an allegation into a factual statement without sufficient reliable evidence.
5. Preserve source URLs, publication dates, event dates, authors, quotations, and archive notes.
6. Prefer primary records for match events and official decisions; use reputable independent reporting for interpretation.
7. Treat social posts and fan videos as evidence of sentiment, not proof of match fixing or corruption.
8. Keep Blender automation deterministic and testable. Separate Blender-independent Python from `bpy` code where practical.
9. The work Mac may only receive employer-approved repository content and run Blender/Git operations permitted by policy.
10. Never place company data, credentials, private paths, or work assets in this project.

## Editorial labels

Every material claim must be labeled internally as one of:

- `VERIFIED_FACT`
- `DISPUTED_FACT`
- `ALLEGATION`
- `INFERENCE`
- `OPINION`
- `UNKNOWN`

## Quality gates

- A strong hook does not overstate what the evidence proves.
- Every factual on-screen statement has a source record.
- Direct quotations are checked against the original source.
- Match incidents include competition, match, date, minute, applicable rule, and at least two angles or authoritative descriptions where available.
- Counterarguments receive a fair presentation.
- Blender scripts validate scene objects, cameras, lights, frame range, render settings, output paths, and missing assets.
