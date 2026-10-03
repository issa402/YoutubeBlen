"use strict";

let current = null;
const $ = (id) => document.getElementById(id);
const node = (tag, className, content) => {
  const element = document.createElement(tag);
  if (className) element.className = className;
  if (content !== undefined) element.textContent = String(content);
  return element;
};
const mediaURL = (path) => `/media?path=${encodeURIComponent(path)}`;
const clear = (element) => element.replaceChildren();

function toast(message) {
  const element = $("toast");
  element.textContent = message;
  element.classList.add("show");
  window.setTimeout(() => element.classList.remove("show"), 5200);
}

async function request(path, body) {
  const response = await fetch(path, {
    method: "POST",
    headers: {"Content-Type": "application/json", "X-Creator-Token": current.csrf_token},
    body: JSON.stringify(body)
  });
  const value = await response.json();
  if (!response.ok) throw Error(value.error || "Local action failed.");
  return value.result;
}

function selectEpisodes(episodes) {
  for (const id of ["episode", "memory-episode"]) {
    const select = $(id);
    const selected = select.value;
    clear(select);
    for (const episode of episodes) {
      const option = node("option", "", `${episode.episode} — ${episode.title}`);
      option.value = episode.episode;
      select.append(option);
    }
    if (selected) select.value = selected;
  }
}

function actionButton(label, onClick) {
  const button = node("button", "", label);
  button.type = "button";
  button.addEventListener("click", async () => {
    button.disabled = true;
    try { await onClick(); await refresh(); }
    catch (error) { toast(error.message); }
    finally { button.disabled = false; }
  });
  return button;
}

function renderProjects(projects) {
  const list = $("projects-list");
  clear(list);
  if (!projects.length) list.append(node("p", "", "No productions yet. Start with one creative brief above."));
  for (const project of projects) {
    const card = node("article", "project-card");
    card.append(node("div", "meta", `${project.episode} · ${project.id.slice(0, 8)}`));
    card.append(node("h3", "", project.brief));
    if (project.reference_ids.length) card.append(node("p", "", `References: ${project.reference_ids.join(", ")}`));
    const stages = node("div", "stages");
    for (const stage of project.stages) {
      const item = node("div", `stage ${stage.state}`);
      item.append(node("b", "", stage.stage));
      item.append(node("small", "", stage.state));
      if (stage.artifact) item.append(node("small", "", stage.artifact));
      if (stage.error) item.append(node("small", "", stage.error));
      if (stage.state === "pending") {
        item.append(actionButton("Prepare", async () => {
          const result = await request("/api/handoff", {project_id: project.id, stage: stage.stage});
          toast(`Handoff saved: ${result.path} (${result.estimated_tokens} estimated tokens).`);
        }));
      } else if (stage.state === "running") {
        if (stage.handoff) {
          item.append(node("small", "", "Agent handoff ready"));
          item.append(node("code", "worker-command", `.\\creator.ps1 worker run ${project.id} ${stage.stage} --backend hermes --execute --model YOUR_MODEL`));
        }
        item.append(actionButton("Complete", async () => {
          const artifact = window.prompt("Project-relative path to the completed, reviewed file:");
          if (!artifact) return;
          await request("/api/complete", {project_id: project.id, stage: stage.stage, artifact});
          toast(`${stage.stage} marked complete.`);
        }));
        item.append(actionButton("Mark failed", async () => {
          const error = window.prompt("What went wrong?");
          if (!error) return;
          await request("/api/fail", {project_id: project.id, stage: stage.stage, error});
        }));
      } else if (stage.state === "failed") {
        item.append(actionButton("Retry", () => request("/api/retry", {project_id: project.id, stage: stage.stage})));
      }
      stages.append(item);
    }
    card.append(stages);
    list.append(card);
  }
}

function renderReferences(references) {
  const list = $("reference-list");
  clear(list);
  for (const reference of references) {
    const card = node("article", "reference-card");
    const picture = node("img");
    picture.src = mediaURL(`tools/animation-references/${reference.contact_sheet}`);
    picture.alt = `${reference.id} visual contact sheet`;
    picture.loading = "lazy";
    card.append(picture);
    card.append(node("div", "meta", `${reference.id} · ${reference.duration.toFixed(1)}s · ${reference.fps} fps`));
    card.append(node("h3", "", reference.style.replaceAll("-", " ")));
    card.append(node("p", "", `${reference.width} × ${reference.height} reference · ${reference.analysis}`));
    list.append(card);
  }
}

function renderMemories(memories) {
  const list = $("memory-list");
  clear(list);
  for (const memory of memories) {
    const card = node("article", "memory-card");
    card.append(node("div", "meta", memory.episode));
    card.append(node("strong", "", memory.approved));
    card.append(node("p", "", `Reason: ${memory.reason}`));
    list.append(card);
  }
}

function renderOutputs(artifacts) {
  const list = $("output-list");
  clear(list);
  if (!artifacts.length) list.append(node("p", "", "No local video or audio outputs found yet."));
  for (const artifact of artifacts) {
    const card = node("article", "output-card");
    card.append(node("div", "meta", artifact.type.toUpperCase()));
    card.append(node("h3", "", artifact.name));
    card.append(node("p", "", `${(artifact.size / 1048576).toFixed(1)} MB · ${artifact.path}`));
    const player = node(artifact.type === "video" ? "video" : "audio");
    player.controls = true;
    player.preload = "metadata";
    player.src = mediaURL(artifact.path);
    card.append(player);
    list.append(card);
  }
}

async function refresh() {
  const response = await fetch("/api/state", {cache: "no-store"});
  if (!response.ok) throw Error("Could not load local studio state.");
  current = await response.json();
  $("server-status").textContent = "LOCAL · READY";
  $("count-projects").textContent = current.projects.length;
  $("count-memory").textContent = current.memory_count;
  $("count-assets").textContent = current.artifacts.length;
  $("budget-value").textContent = current.budget.cap_usd === null ? "Not set" : `$${current.budget.remaining_usd.toFixed(2)}`;
  selectEpisodes(current.episodes);
  renderProjects(current.projects);
  renderReferences(current.references || []);
  renderMemories(current.memories || []);
  renderOutputs(current.artifacts || []);
  const integrations = $("integrations");
  clear(integrations);
  for (const item of current.integrations) integrations.append(node("span", "integration", `${item.name}: ${item.status}`));
}

$("project-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    const reference_ids = $("refs").value.split(",").map(v => v.trim().toUpperCase()).filter(Boolean);
    await request("/api/project", {episode: $("episode").value, brief: $("brief").value, reference_ids});
    $("brief").value = "";
    toast("Production created. Prepare the research handoff when ready.");
    await refresh();
  } catch (error) { toast(error.message); }
});

$("memory-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    await request("/api/memory", {episode: $("memory-episode").value, raw: $("raw").value,
      approved: $("approved").value, rejected: $("rejected").value, reason: $("reason").value});
    event.target.reset();
    toast("Approved example saved for this episode.");
    await refresh();
  } catch (error) { toast(error.message); }
});

refresh().catch(error => { $("server-status").textContent = "LOCAL · ERROR"; toast(error.message); });
