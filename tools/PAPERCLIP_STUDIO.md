# Paperclip creator studio on the personal Windows PC

Paperclip is the local **agent job board and scheduler**. It owns assignments, runs and handoffs. The existing Creator Desk at `http://127.0.0.1:8766` is an artifact/media review tool; its older SQLite stages do not automatically sync to Paperclip. Episode files and the source ledger remain editorial authority. Blender and HyperFrames render visuals; neither is the agent scheduler.

OpenMontage is also available as a **separate optional production path** with its own Backlot board at `http://127.0.0.1:4750`; choose it per video with [OPENMONTAGE_FULL.md](OPENMONTAGE_FULL.md). Paperclip does not dispatch or sync its stages.

## Start or reproduce

In PowerShell at `C:\Users\Isaac\OneDrive\Desktop\Youtube`:

```powershell
npm ci --prefix integrations/paperclip --no-audit --no-fund
.\paperclip.ps1 run
```

Leave that window open. Open `http://127.0.0.1:3100` on **this Windows PC**. In a second PowerShell window:

```powershell
.\paperclip.ps1 status
.\paperclip.ps1 seed
```

The first-ever setup was `paperclipai onboard --yes --bind loopback --data-dir .studio/paperclip --no-install-service`; a later `run` reuses that ignored local data. If `.studio/paperclip` is absent on a new personal Windows checkout, run:

```powershell
$env:PAPERCLIP_NO_BROWSER = '1'
& .\integrations\paperclip\node_modules\.bin\paperclipai.cmd onboard --yes --bind loopback --data-dir "$(Resolve-Path .)\.studio\paperclip" --no-install-service
```

`seed` is idempotent. On a fresh instance it creates **Football Documentary Studio**, one publishing goal, the **Episode 002 — Same Standard pilot** project, four Codex-backed agents and four backlog issues. On this PC the evidence issue has already advanced to `in_review`. Source and lockfile are tracked. The server database, secrets, logs, Codex run state and generated candidates live under ignored `.studio/`; they are not copied to the Mac by Git. Stop the server with Ctrl+C. No Windows service, cloud Paperclip account or schedule is installed.

## What runs and who decides

| Paperclip agent | Candidate output | Handoff gate |
| --- | --- | --- |
| Evidence Editor | `claim-map.md`: line, label, source, counterpoint, uncertainty | Creator checks source IDs and wording |
| Script Editor | `script-revision.md`: first-person hook and beats | Creator selects the final narration |
| Visual Director | `shot-plan.md`: exact 30 fps ranges and renderer | Creator reviews a low-resolution animatic |
| Release Reviewer | `release-review.md`: evidence, sync, decode and art checks | Creator approves release |

Agents use the installed local Codex CLI and its existing ChatGPT login. The Windows CLI rejected `gpt-6.1-sol` for this account during setup, so the bootstrap leaves `model` unset and the CLI chooses its supported default. Astra in the desktop app does not imply Astra is available to this separate CLI login. Paperclip may report zero dollar cost for a subscription run; that is **not** proof that usage is free or that tokens were saved. The isolated role instructions are versioned in `integrations/paperclip/agents/` and loaded with the repo's editorial rules.

Each agent has timer heartbeats disabled. Assigning an issue or invoking an agent can still start a run. Paperclip's Codex adapter uses the ACP engine with noninteractive permission requests denied, `dangerouslyBypassApprovalsAndSandbox: false`, a five-minute timeout, and the already logged-in `CODEX_HOME`. ACP completed the evidence pilot after the classic Windows sandbox failed to initialize (`SetNamedSecurityInfoW: 5`). The explicit home avoids a Windows symlink failure during Paperclip's first pilot run. It is shared login state, not isolated per-agent credentials. No provider API key is committed. Agents write unapproved candidates under `.studio/paperclip/instances/default/projects/.../_default/` unless a project workspace is later configured differently. The versioned prompt forbids canonical edits, publishing, pushing and agent spawning.

## Pilot in the board

The pilot uses the first **46.112 seconds** of `episodes/002-ronaldo-hate-psychology/shorts/same-standard/`. Its existing `NARRATION.txt`, `EVIDENCE.md` and `timeline.json` are the inputs. Open Paperclip's project. The Evidence Editor has produced `claim-map.md` and placed its issue in review; inspect the candidate file and Paperclip issue comments. Only after accepting the claim map should you assign the script issue; then the visual issue. The release issue waits for an actual preview and verification report. A candidate is not an approved episode claim.

For the original animation, keep `blender/rules_short_scene.py` and `tools/run_same_standard.sh` as the Blender path on the permitted Mac. The creator's Windows PC can use `creator.ps1 media plan`, `media build`, and `media render` with a locked WAV and an edited frame timeline for a new HyperFrames tactical cut. See `tools/CREATOR_SYSTEM.md` for exact media commands. Paperclip dispatches the work; the deterministic renderers and evidence checks make the output. The Mac receives only approved repository content and runs permitted Git/Blender operations.

For a new visual reference, run the pinned local OpenMontage analysis command in [OPENMONTAGE_REFERENCE.md](OPENMONTAGE_REFERENCE.md) on Windows. Attach its ignored report and selected frames to the Visual Director's brief. The command uses OpenMontage's actual `SceneDetect` and `FrameSampler` tools; Paperclip does not launch it automatically, and the report needs visual review before shot timing is adopted.

## Learning and operating cost

The system learns preferences through **explicitly accepted examples**, not model retraining. Save approved/rejected phrasing in Creator Desk, link the accepted artifact in the Paperclip issue, and revise the role instructions only when the preference is durable. Keep raw takes and uncertain claims visible instead of hiding them in a generic summary. Short role files and episode-specific source retrieval limit repeated context, but token savings require a measured comparison. No automatic paid media provider, scheduled publishing, trading or background research routine is configured.

If the server is unavailable, run `.\paperclip.ps1 status`, then restart with `.\paperclip.ps1 run`. If a task fails, inspect its Paperclip run and issue comments before invoking again. The initial Windows failures were an `EPERM` managed-login symlink and an unsupported explicit model; the versioned bootstrap addresses both. Re-running `seed` restores the agent configuration without duplicating the studio or issues.
