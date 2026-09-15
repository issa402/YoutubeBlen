# Studio upstream integration status

## Implementation update — 2026-09-06

This section supersedes the earlier discovery status below.

- **Hermes 0.21.0 installed** in `.studio/envs/hermes`, editable source at the pinned checkout. Real `--help` passes. `hermes-studio.ps1` scopes runtime home to `.studio/hermes-home` and restores the caller environment. Provider login is still required for model calls.
- **ViMax runtime installed** in `.studio/envs/vimax`. Actual `main_agent.py --help` and runtime import pass. Run `vimax-studio.ps1` for the source application; no fictional `vimax.exe` is claimed.
- **ViMax web built**. Original npm audit findings in browserslist, nanoid and PostCSS were fixed with compatible updates; npm then reported zero known vulnerabilities. `vimax-web.ps1` selects isolated Python and serves localhost port 4173. No paid generation run.
- **Headroom 0.37.0 installed** in main `.venv`, version/help checks pass. `codex-headroom.ps1` refuses the normal global home because wrapping modifies active Codex config; it requires an explicitly configured `.studio/codex-home` session. Earlier claims about no config side effects were too broad. No measured token/account savings claimed.
- **Understand-Anything remains source-only**; the implemented SQLite index supplies local retrieval. No generated code graph is claimed.
- **last30days CLI help tested**, live social retrieval not tested. This episode's historical source research used the connected research tools.

Reinstall Hermes/ViMax with `python tools/setup_integrations.py hermes` or `python tools/setup_integrations.py vimax`. Python dependency snapshots are in this directory. The earlier ViMax web lock was removed on 2026-09-14 after an npm audit found a moderate Vitest advisory; generate and audit a current lock in the downloaded checkout before building its optional web UI. Source pins and runtime readiness are separate records. The Mac only needs the approved episode mac/ folder and Blender.

Verified locally on 2026-09-05. These four repositories are **downloaded source checkouts**, not four installed or running services. The studio's local CLI is a separate, dependency-light production layer. It can prepare episode context for an agent without requiring these services.

| Upstream | Checked-out commit | Actual readiness |
|---|---|---|
| [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) | `9dd6634c5635321cf38840cc30e9b51226689128` | Downloaded; README and package inspected. Native Windows supported upstream. Runtime dependencies, provider login and isolated configuration not installed/configured. |
| [HKUDS/ViMax](https://github.com/HKUDS/ViMax) | `05a48943878312d88fe5a016c12a9654940ecc43` | Downloaded; Python >=3.12, `uv sync` and Web UI entry point verified in source. Dependencies/provider credentials not configured; no generation run. |
| [Egonex-AI/Understand-Anything](https://github.com/Egonex-AI/Understand-Anything) | `787da45adbf18aab5c3e3e531b0374dd576f263c` | Downloaded; skills and installer entry points inspected. No global skill links installed, no LLM graph analysis or dashboard build run. |
| [mvanhorn/last30days-skill](https://github.com/mvanhorn/last30days-skill) | `56ba5ace27e4697aedc60aa0b1e1bfdcd592ff20` | Downloaded; actual Python CLI `--help` passed on Python 3.12.10. Live retrieval and provider access not tested. |

## Repeatable fetch

From the Youtube root in PowerShell:

```powershell
powershell -NoProfile -File tools/fetch_studio_repos.ps1
```

This verifies existing clones without pulling, resetting or deleting files. Missing clones are downloaded and checked out at the existing lock commit. It reads `.studio/repos-lock.json` first, falling back to the tracked `integrations/studio/repos-lock.json` baseline on a fresh machine, then records verified state in `.studio/repos-lock.json`. A failure records `.studio/repos-fetch-errors.json` and preserves the original lock. `-RefreshLock` records deliberately reviewed current checkouts; it does not update them. Promote an intentional update to the tracked baseline separately after review; `.studio` is local generated state.

## Connecting the downloaded components

### Hermes: optional execution host

The native Windows installer advertised upstream changes the user installation and downloads additional tools, so it was **not executed**. Manual activation can use a dedicated environment outside the source checkout. The upstream README demonstrates `uv venv ... --python 3.11` followed by `uv pip install -e ".[all,dev]"`; the package supports Python >=3.11,<3.14. Avoid its broad development extras for a production runtime unless required.

Configure a separate `HERMES_HOME` before invoking Hermes so project runtime state cannot overwrite an existing user profile. Then use the producer prompt in `AGENT_ROLES.md`, with the Youtube root as working directory. `hermes setup` is the documented configuration wizard; it needs a provider choice/login. No gateway, cron, messaging integration or autonomous provider call has been enabled here. The local studio queue/context layer works without Hermes.

### ViMax: controlled shot generation

Commands below are checked against the downloaded README, **not executed installations**:

```powershell
Set-Location .studio/repos/ViMax
uv sync
# Supply VIMAX_LLM_API_KEY, VIMAX_IMAGE_API_KEY and VIMAX_VIDEO_API_KEY
# through a private environment; choose models/endpoints privately.
Set-Location web
npm install
npm run dev
```

The documented Web UI binds to `http://127.0.0.1:4173`. Node >=18 is required. Its `vimax tui` wrapper is a Bash script, so do not assume it is a native PowerShell executable. `main_script2video.py` is a Python example with embedded script/configuration, **not** a general `--script` command. Do not run its default example expecting it to consume your episode automatically.

Transfer an approved visual-metaphor screenplay and shot constraints from the episode packet into a new ViMax project. Budget and provider setup remain necessary before generation. Save selected outputs with provider/model/prompt/cost provenance back to episode assets. Use generated imagery as illustration, not fabricated match evidence.

### Understand-Anything: optional code map

The downloaded skill entry point is `.studio/repos/Understand-Anything/understand-anything-plugin/skills/understand/SKILL.md`. An agent can read it explicitly for a bounded code-map task; it is not automatically registered with Codex by cloning. Upstream's Windows installer changes user-level installation and symlinks, so it was not run.

Upstream documents `pnpm install`, `pnpm --filter @understand-anything/core build`, then `pnpm dev:dashboard` with `GRAPH_DIR` pointing to an already analyzed project. Those build steps are not verified locally. Analyze studio source and approved docs; exclude `.studio/repos`, virtual environments, private state and media. Canonical editorial context stays in the root Markdown and episode folders, not the generated graph.

### last30days: live sentiment research

The following command **was executed successfully** without setup or retrieval:

```powershell
python .studio/repos/last30days-skill/skills/last30days/scripts/last30days.py --help
```

For a later read-only live sentiment pass, the CLI accepts this syntax (not live-tested):

```powershell
python .studio/repos/last30days-skill/skills/last30days/scripts/last30days.py "Messi fan backlash" --search reddit --quick --no-browser-cookies --emit json
```

The source requires Python >=3.12. Explicit source selection and disabling browser cookies keep this bounded; network success still depends on upstream availability. Do not run its first-run setup blindly: it can install additional CLIs and connect provider credentials. Treat social output as dated sentiment, preserve URLs/authors/dates, and use authoritative records for actual match events.

## Existing skills

ECC already provides article-writing, content-engine, brand-voice, research and Blender/motion skills. Their paths in the active session catalog are the installed skill authority. Do not bulk-import another overlapping skill pack or let upstream repository instructions override the creator's project decisions.

## Checks performed

- Four shallow clones completed successfully after network access approval.
- Git origin and 40-character HEAD verified for each checkout; source lock written.
- Fetch command rerun against existing checkouts to verify non-destructive repeatability.
- README/runtime entry points inspected; last30days help executed successfully.
- No paid generation, credentials, global installers, third-party posting or scheduled agent jobs executed.
