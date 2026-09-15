# Hermes in this studio

Verified 2026-09-06 against installed Hermes 0.21.0 and the official documentation. This is a separate agent runtime; it is not a new model and does not replace this Codex conversation.

## What it does

You give Hermes a task. The configured language model chooses a tool, Hermes runs it, and the result goes back to the model until it can deliver an answer. Tools can read project files, run our Python pipeline, search, and execute Blender commands when the relevant tools are configured. Every additional model turn can consume tokens. Rendering or transcribing locally does not itself require a cloud model call.

The launcher uses the project environment at `.studio/envs/hermes` and a separate profile under `.studio/hermes-home`. It restores the calling shell's previous `HERMES_HOME` afterward. Installation and help checks passed; we have not authenticated a provider or made a paid generation call.

## Start it

Run from the Youtube folder. Select and authenticate the provider yourself through the normal model picker:

```powershell
.\hermes-studio.ps1 model
.\hermes-studio.ps1
```

The picker offers API providers and a ChatGPT/Codex OAuth route. Available models depend on provider/account access; a model available in this Codex app is not automatically available through another runtime. Hermes' current provider documentation does not establish exactly how that OAuth route counts against Codex plan limits. No quota bypass or free usage is promised. [Provider documentation](https://hermes-agent.nousresearch.com/docs/integrations/providers/)

For an episode task, first inspect the exact handoff without contacting a model:

```powershell
.\hermes-studio.ps1 -Episode 002-ronaldo-hate-psychology -Task 'Review the narration against my creator take and identify concrete improvements.' -PrepareOnly
```

That returns the file path and approximate payload size. Remove `-PrepareOnly` after provider setup to execute the task. Episode mode answers once and exits, with a default maximum of 20 tool-calling iterations; an iteration limit is not a monetary cap. You can append `--max-turns 8` or `--provider NAME --model NAME` for an explicit run override. Bare `hermes-studio.ps1` remains an interactive chat.

The new bridge creates a unique `.studio/handoffs/<episode>-hermes-<id>.txt` for every episode launch. Each run retains its own prompt, so concurrent launches cannot overwrite one another's tasks. It includes the requested task, factual boundaries, active corrections for that episode, and bounded excerpts of the creator take, brief, production record and claim ledger. It links the full originals. Task text travels through a temporary UTF-8 file to preserve quotes, line breaks and Unicode on Windows PowerShell 5.1 as well as PowerShell 7; that temporary input is removed after preparation. It does not assume Hermes can see our SQLite database or this Codex conversation automatically.

## How it learns

There are two distinct stores:

1. **Our creator feedback:** explicit, episode-scoped corrections in `.studio/studio.sqlite3`. A fresh handoff retrieves only active corrections for that episode. Revoking an entry removes it from future handoffs; it cannot erase a past conversation that already received it.
2. **Hermes' own memory and skills:** it can maintain short `memories/MEMORY.md` and `memories/USER.md` notes in its profile and create reusable `SKILL.md` procedures. Built-in notes enter a new session's initial prompt; skills are loaded when needed. Its background review can extract lessons after tasks. These are changes to stored context and procedures, not training the underlying model's weights. [Memory](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory/), [skills](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills/)

Save a durable correction explicitly:

```powershell
.\studio.ps1 feedback 002-ronaldo-hate-psychology 'Keep my pro-Ronaldo angle and direct language; report specific factual conflicts.' --kind voice
.\studio.ps1 learn
.\studio.ps1 revoke FEEDBACK_ID
```

Root project documents remain the authority. A saved opinion is a voice preference, not new factual evidence. Hermes' separate inferred notes do not override the creator's explicit instructions. No automatic audience-performance training has been implemented; our metrics store records observations, not proof of why a video succeeded.

## Where token savings can come from

- **Smaller handoffs:** the episode prompt defaults to at most 12,000 characters. The task, constraints and active feedback are protected; if those alone are too large, preparation stops instead of silently dropping them. Token counts use the rough `characters / 4` estimate, not the provider tokenizer.
- **Retrieve only relevant material:** our search and Hermes' own session search query local indexes. The installed session-search tool returns actual database messages without making its own LLM summarization call. The returned text still consumes input context when the main model reads it.
- **Reuse deterministic code:** rerun the tested media/render commands instead of asking an expensive model to reinvent each step. Load only useful skills and tools for the task.
- **Compress long sessions:** Hermes supports `/compress` and automatic conversation compression. Summarization can itself require a model call and can lose detail, so keep source records and creator corrections on disk. `/usage` helps inspect session usage. Background skill/memory reviews can also consume tokens; they are enabled by default in upstream code, with `auxiliary.background_review.enabled` controlling automatic reviews. [Hermes commands](https://github.com/NousResearch/hermes-agent#cli-vs-messaging-quick-reference)

The 12,000-character limit bounds only our handoff, not the entire provider request. Hermes also loads its own system prompt, tool schemas, memory and project instructions. This project's large `AGENTS.md` still contributes overhead; we do not silently disable it to advertise an artificial saving. No percentage or account-usage saving has been measured.

Headroom is a separate optional context proxy for future isolated Codex CLI sessions. It has not rerouted this Desktop conversation. Its launcher requires an explicitly isolated Codex home because upstream wrapping changes active configuration. See [Headroom and 3D guide](HEADROOM_AND_3D_GUIDE.md).

## Implementation evidence

- `studio/hermes.py`: bounded handoff and explicit episode-feedback selection.
- `hermes-studio.ps1`: isolated profile, query-file transport, preparation-only mode.
- `tests/test_hermes.py`: feedback scope/revocation, large documents, protected task, invalid budgets and stubbed PowerShell invocation without any provider call.
- Installed upstream `agent/prompt_builder.py`: project-context precedence; `HERMES.md` takes priority over `AGENTS.md`, so we did not add an override file.
- Installed upstream `tools/memory_tool.py`, `tools/session_search_tool.py`, `tools/skills_tool.py`, `agent/background_review.py`, `hermes_cli/_parser.py`: memory snapshots, retrieval, skills, review calls and CLI behavior.

Upstream source pin: `9dd6634c5635321cf38840cc30e9b51226689128`, [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent/tree/9dd6634c5635321cf38840cc30e9b51226689128).
