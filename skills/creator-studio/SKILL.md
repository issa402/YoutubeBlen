---
name: creator-studio
description: Improve this football documentary studio's scripts, episode memory, edit packages and Blender handoffs using its existing working tools and selected ECC workflows.
---

# Creator studio

Use this project skill by reading it through the project documentation. This folder is not registered in Codex's automatic skill discovery. It does not install tools, enable hooks or modify global configuration.

## Start with the current episode

Read [PROJECT_CONTEXT.md](../../PROJECT_CONTEXT.md), [CURRENT_STATUS.md](../../CURRENT_STATUS.md) and [DECISIONS.md](../../DECISIONS.md). Resolve the active episode from those files rather than assuming that its numeric folder ID is its release order. Consult its `PRODUCTION_HANDOFF.md` for actual outputs and remaining production work.

The creator's `CREATOR_TAKE.md` supplies the thesis and voice. `CLAIMS_LEDGER.md` and `research/SOURCE_REGISTER.md` govern factual support. The master script's `### Voiceover` fields and `script/NARRATION.txt` must contain the same spoken text. Reconcile an edit to either before generating a new guide or edit package. Keep source annotations in the master; preserve necessary factual qualifications in speech.

Strengthen the creator's argument through concrete mechanisms, examples and visual contrasts. Flag an unsupported factual premise precisely instead of silently substituting a different thesis. An opinion about envy is not a diagnosis of all fans; a commercial partnership alone does not establish corruption. Retain raw allegations in the creator take while distinguishing them from established facts in the narration.

## Choose the smallest useful ECC workflow

These skills are installed on this Windows environment. Read the selected skill's `SKILL.md` from the live skill catalog; do not load the whole collection or copy its generic examples into the project.

| Work | Relevant installed skill | Project application |
| --- | --- | --- |
| Voice or script revision | `article-writing`, with `brand-voice` when multiple outputs need consistency | Use the creator's actual take and corrections; compare the revision against the original argument. |
| Shorts and packaging | `content-engine` | Adapt one strong claim per Short from the approved episode; retain the same persona. |
| Moving Blender scenes | `blender-motion-state-inspection` | Inspect scene data, camera cuts, contact and transforms as well as rendered frames. |
| Context or API cost changes | `cost-aware-llm-pipeline` | Prefer deterministic local work and bounded retrieval; measure usage before claiming savings. Its example model prices are not current project configuration. |
| Code changes | `verification-loop` | Run the relevant project tests and executable proof; report what was actually exercised. |
| New skill or ECC selection | `ecc-guide` | Inspect the installed files; add a tool only for a concrete unresolved need. |

For independent work, delegate a bounded research, scene or review task with named output ownership. Do not send every agent the entire repository. Keep heavy renders and transcription sequential on this Windows machine.

## Working commands

From the project root in PowerShell:

```powershell
.\studio.ps1 doctor
.\studio.ps1 index
.\studio.ps1 search "rivalry"
.\studio.ps1 review 002-ronaldo-hate-psychology
.\hermes-studio.ps1 -Episode 002-ronaldo-hate-psychology -Task "Review the opening against my take and identify one concrete improvement" -PrepareOnly
.\studio.ps1 dashboard
```

Replace the episode ID for another story. `review` checks narration agreement, source references and guide freshness; add `--output .studio/reviews/NEW_NAME` to export its report and chapter edit CSV. It does not certify sources or artistic quality. `-PrepareOnly` creates an inspectable handoff without a model call. The dashboard is a regenerated snapshot, not a worker. Use the [runbook](../../tools/STUDIO_RUNBOOK.md) for episode/source/feedback commands, the [Hermes guide](../../tools/HERMES_WORKFLOW.md) for agent execution, and [narration/editing](../../tools/NARRATION_AND_EDITING.md) for voice and render commands. Use a fresh `.studio/` output directory for each production run.

## Memory and token discipline

Save explicit user corrections with `studio feedback`; revoke obsolete corrections with `studio revoke`. Retrieve only the active episode's corrections. A preference is not evidence, and observed audience metrics do not establish which editorial choice caused a result. Rebuild a handoff after corrections; a previously generated file is a snapshot.

Hermes handoffs preserve the task and active corrections, then excerpt selected documents within a character budget. Read marked originals when the task needs omitted detail. Character-based token estimates exclude the agent's system prompt, tools and history. Render, transcribe, search and package through local commands instead of asking a model to reproduce their work. Do not claim model retraining, guaranteed quota savings or active Headroom compression without measurements from the actual execution path.

## Verify the artifact that changed

- Narration: compare spoken text against the master; regenerate derived audio/timings only when that text changes. Recheck factual passages against source records.
- Animation: verify structured motion, camera cuts, frame count, render size and audio duration; inspect beginning, transitions and end. Passing a Python test does not establish Blender render success or native Mac execution.
- Studio code: add regression tests for a demonstrated failure, run the affected tests, then the full existing suite for substantial integration changes. Use the runbook's coverage command; inspect the diff.
- Handoff: update `CURRENT_STATUS.md` and durable decisions. Distinguish code generated, render verified, final performance recorded and full episode assembled. Preserve existing user work; generated `.studio/` media is not transferred by Git.

Continue within the user's existing authorization. Provider calls, publishing and Git transfer follow the project's actual boundaries; this skill creates no new permission. The Mac receives only approved code/assets and runs the permitted Git/Blender workflow.
