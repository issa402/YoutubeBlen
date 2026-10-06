# Optional full OpenMontage workspace on the personal Windows PC

The project now has **two selectable production paths**. Keep an episode's script, source ledger and approved narration in the YouTube repository in either case.

| Choose | Control and rendering | Best fit |
| --- | --- | --- |
| Current studio | Paperclip agent jobs, Creator Desk review, Blender character scenes, HyperFrames graphics | The existing Same Standard and superhero scenes; precise editable acting and episode evidence |
| OpenMontage | A separate Codex session follows upstream pipeline YAML and director skills; Backlot shows its project checkpoints; Remotion/HyperFrames/Blender/FFmpeg may render | New experiments, stock/archival montage, SVG animation, fast explainer formats |

OpenMontage does **not** replace Paperclip or automatically import its assignments. Start one path per video, then bring any approved output and provenance back to the episode. `openmontage.ps1` is a Windows launcher for the pinned ignored checkout at `.studio/repos/OpenMontage/`. Do not run it on the employer-managed Mac.

## What is installed and verified here

OpenMontage is pinned at `9327439db69021ab4b0e2776729bf3b58fdb5a87`. Its core Python dependencies, Piper package and Remotion composer are installed in the ignored checkout. Its local `config.yaml` is in `cap` mode with `total_usd: 0.0`, and no `.env` file/provider key was added. `doctor` discovered 137 registered tools with no broken Python requirements. Backlot health returned OK at `http://127.0.0.1:4750`. The upstream `world-in-numbers` zero-key demo rendered to `projects/demos/renders/world-in-numbers.mp4`: 23.062 seconds, 1920×1080, 30 fps, H.264/AAC, 4,285,775 bytes. This verifies the local Remotion composition path, **not** a finished soccer documentary, live agent pipeline or paid provider.

Upstream's pinned Remotion lock had three high and two moderate npm advisories. `npm audit fix` updated nine dependencies without changing its package manifest; the patched lock is preserved at `integrations/openmontage/remotion-package-lock.json`. The local composer now reports zero npm advisories. The launcher refuses an upstream lock that differs from this audited overlay.
The isolated Python environment's installer was upgraded to pip 26.2.1; `pip-audit --path` now reports no known vulnerabilities. These are checks at setup time, not a promise that future advisories will never appear.

## Use either path

In PowerShell from the YouTube root:

```powershell
.\paperclip.ps1 run              # Existing Paperclip agent board: http://127.0.0.1:3100
.\creator.ps1 desk               # Existing Creator Desk: http://127.0.0.1:8766
.\openmontage.ps1 doctor         # OpenMontage dependencies, pin and zero-dollar budget
.\openmontage.ps1 board          # Separate Backlot board: http://127.0.0.1:4750
.\openmontage.ps1 start-free     # Separate interactive Codex/OpenMontage session
```

The last command starts an **interactive** Codex CLI session in the OpenMontage checkout. It checks the $0 cap, refuses an OpenMontage `.env`, temporarily removes common media-provider keys from that process, and asks for your video brief and creative approvals. It still uses your Codex account and may consume its model allowance. This interactive agent path has **not** been executed end to end; use the first project as a supervised pilot. Do not tell it a disputed football claim is verified merely because it fits the story.

To see a local render without any AI/provider call:

```powershell
.\openmontage.ps1 demo -Demo world-in-numbers
```

That demo is an upstream graphic sample, not your channel's video. The current Paperclip board does not show Backlot projects, and Backlot does not show Paperclip issues.

## What a polished short may cost

The **software and local render path can cost $0 in media API fees**, using your own footage/art, properly licensed archival footage, Piper/local speech, Blender, Remotion, HyperFrames and FFmpeg. The labor, computer time, and any Codex model usage are separate. Stock footage needs per-asset rights review.

For a 60-second short made entirely of generated motion, OpenMontage's October 2026 provider guide lists illustrative fal.ai rates of **$0.07/second for Kling 2.5 Turbo Pro** and **$0.40/second for Veo 3**. At one accepted second generated per final second, the bare clip-generation math is about **$4.20 or $24**, respectively; two full passes would be about **$8.40 or $48**. Images, premium voice/music, longer unused takes and retry failures add cost. This is an estimate from published example rates, not a quote or guarantee; check the selected provider's live price before turning on a key. OpenMontage's showcase reports $1.33 for one six-clip short and about $4 for another specific project, which are examples, not a repeatable price target.

For this channel, reserve paid video generation for shots where it visibly beats our reusable Blender/SVG scenes. First make a timed animatic with locked narration; approve character appearance and action; then price only the missing shots. The $0 cap currently blocks estimated paid actions in OpenMontage's cost tracker. A future paid project requires an explicit budget and provider setup; `start-free` will refuse that configuration.

## Rebuild on this Windows PC if the ignored checkout is lost

```powershell
.\tools\fetch_studio_repos.ps1
cd .studio\repos\OpenMontage
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install piper-tts
.\.venv\Scripts\python.exe -m pip install --upgrade pip
cd remotion-composer
Copy-Item ..\..\..\..\integrations\openmontage\remotion-package-lock.json package-lock.json -Force
npm.cmd ci --ignore-scripts --no-audit --no-fund
cd ..\..\..\..
```

Then set the ignored OpenMontage `config.yaml` budget to `mode: cap`, `total_usd: 0.0`, and `single_action_approval_usd: 0.0`; leave `.env` absent. Run `.\openmontage.ps1 doctor` before `start-free`. Generated videos, package installs, voice models, local configs and Backlot state remain ignored; Git carries the pinned source reference, launcher and these instructions.
