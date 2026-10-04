import { mkdir } from 'node:fs/promises';
import { homedir } from 'node:os';
import { resolve, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = resolve(fileURLToPath(new URL('.', import.meta.url)));
const root = resolve(here, '..', '..');
const base = process.env.PAPERCLIP_API_BASE ?? 'http://127.0.0.1:3100/api';
if (new URL(base).hostname !== '127.0.0.1' && new URL(base).hostname !== 'localhost') {
  throw new Error('Bootstrap only targets a local Paperclip instance.');
}

async function api(path, method = 'GET', payload) {
  const response = await fetch(`${base}${path}`, {
    method,
    headers: { 'content-type': 'application/json' },
    body: payload === undefined ? undefined : JSON.stringify(payload),
  });
  const raw = await response.text();
  if (!response.ok) throw new Error(`${method} ${path}: ${response.status} ${raw.slice(0, 800)}`);
  return raw ? JSON.parse(raw) : null;
}

async function ensure(listPath, createPath, find, payload) {
  const existing = (await api(listPath)).find(find);
  return existing ?? api(createPath, 'POST', payload);
}

const health = await api('/health');
if (health.status !== 'ok' || health.deploymentMode !== 'local_trusted') {
  throw new Error('Start the isolated local Paperclip server before bootstrapping.');
}

const company = await ensure('/companies', '/companies',
  (item) => item.name === 'Football Documentary Studio',
  { name: 'Football Documentary Studio', description: 'Evidence-led football documentaries and original animation.' });
const companyPath = `/companies/${company.id}`;
const goal = await ensure(`${companyPath}/goals`, `${companyPath}/goals`,
  (item) => item.title === 'Publish an evidence-led, original football short',
  { title: 'Publish an evidence-led, original football short', level: 'company', status: 'active',
    description: 'Preserve the creator voice, check material claims, and deliver synchronized original animation.' });
const project = await ensure(`${companyPath}/projects`, `${companyPath}/projects`,
  (item) => item.name === 'Episode 002 — Same Standard pilot',
  { name: 'Episode 002 — Same Standard pilot', status: 'in_progress', goalIds: [goal.id],
    description: 'First 46.112 seconds of the existing 86.4-second short: evidence, script, visual beats, and release review.' });

const roles = [
  { name: 'Evidence Editor', role: 'researcher', slug: 'evidence', instructions: 'evidence-editor.md' },
  { name: 'Script Editor', role: 'cmo', slug: 'script', instructions: 'script-editor.md' },
  { name: 'Visual Director', role: 'designer', slug: 'visual', instructions: 'visual-director.md' },
  { name: 'Release Reviewer', role: 'qa', slug: 'review', instructions: 'release-reviewer.md' },
];
const agents = {};
for (const spec of roles) {
  const workdir = join(root, '.studio', 'paperclip-workspaces', spec.slug);
  await mkdir(workdir, { recursive: true });
  const agentPayload = { name: spec.name, role: spec.role, adapterType: 'codex_local',
      adapterConfig: {
        cwd: workdir,
        engine: 'acp',
        model: null,
        modelReasoningEffort: 'medium',
        instructionsFilePath: join(here, 'agents', spec.instructions),
        dangerouslyBypassApprovalsAndSandbox: false,
        nonInteractivePermissions: 'deny',
        warmHandleIdleMs: 0,
        extraArgs: [],
        timeoutSec: 300,
        search: false,
        // Windows may deny Paperclip's managed-home auth symlink. An explicit
        // self-managed home reuses the existing Codex login without copying it.
        env: { CODEX_HOME: process.env.CODEX_HOME ?? join(homedir(), '.codex') },
      },
      runtimeConfig: { heartbeat: { enabled: false } },
    };
  const existing = (await api(`${companyPath}/agents`)).find((item) => item.name === spec.name);
  const agent = existing
    ? await api(`/agents/${existing.id}`, 'PATCH', agentPayload)
    : await api(`${companyPath}/agents`, 'POST', agentPayload);
  agents[spec.slug] = agent;
}

const episode = join(root, 'episodes', '002-ronaldo-hate-psychology', 'shorts', 'same-standard');
const tasks = [
  ['Evidence Editor', 'Map claims and counterevidence for first 46.112 seconds',
    `The repository is ${root}. Read ${join(episode, 'EVIDENCE.md')}, ${join(episode, 'NARRATION.txt')} and ${join(episode, 'timeline.json')}. Produce claim-map.md in your current working directory. Do not rewrite canonical files.`],
  ['Script Editor', 'Sharpen the creator-voice hook after evidence review',
    `The repository is ${root}. Wait for an accepted claim map. Propose script-revision.md for ${episode}; preserve the creator viewpoint and mark unsupported specifics.`],
  ['Visual Director', 'Storyboard and animatic plan for the 46-second pilot',
    `The repository is ${root}. Read ${join(episode, 'timeline.json')} and ${join(root, 'tools', 'ANIMATION_REFERENCE_LIBRARY.md')}. Propose shot-plan.md with 30 fps frame ranges and renderer choices.`],
  ['Release Reviewer', 'Review evidence, sync and animation before release',
    `After a candidate render exists, review source claims, timing, MP4 decode, audio sync and visual framing. Produce release-review.md.`],
];
const existingIssues = await api(`${companyPath}/issues`);
for (const [agentName, title, description] of tasks) {
  const issuePayload = {
    description: `${description}\n\nOwner after manual activation: ${agentName}. Human editorial approval is required between stages.`,
  };
  const existing = existingIssues.find((item) => item.title === title);
  if (existing) {
    if (existing.description !== issuePayload.description) await api(`/issues/${existing.id}`, 'PATCH', issuePayload);
    continue;
  }
  await api(`${companyPath}/issues`, 'POST', {
    title, ...issuePayload,
    status: 'backlog', priority: 'medium', projectId: project.id, goalId: goal.id,
  });
}

console.log(JSON.stringify({ companyId: company.id, projectId: project.id, goalId: goal.id,
  agents: Object.fromEntries(Object.entries(agents).map(([key, value]) => [key, value.id])),
  pilotIssues: tasks.length, server: 'http://127.0.0.1:3100' }, null, 2));
