'use strict';
const studio = JSON.parse(document.getElementById('studio-data').textContent);
const byId = (id) => document.getElementById(id);
const node = (tag, text, className) => { const el = document.createElement(tag); if (text !== undefined) el.textContent = text; if (className) el.className = className; return el; };
const clock = (seconds) => Number.isFinite(seconds) ? `${Math.floor(seconds / 60)}:${String(Math.floor(seconds % 60)).padStart(2, '0')}` : '—';
let active = studio.episodes[0] || null;
let selectedChapter = 0;
let group = 'episode';
let visibleFiles = 12;
function setLink(id, url) { const el = byId(id); el.hidden = !url; if (url) el.href = url; else el.removeAttribute('href'); }
function setMedia(id, url) { const media = byId(id); media.pause(); media.hidden = !url; if (url) media.src = url; else media.removeAttribute('src'); media.load(); }
function link(label, url) { const el = node('a', label); el.href = url; return el; }
function renderActions() {
  const target = byId('next-actions'); target.replaceChildren();
  const actions = active.review.next_actions || [];
  for (const action of actions.slice(0, 3)) { const li = node('li'); li.append(node('strong', action.label), node('p', action.detail)); target.append(li); }
  if (!actions.length) target.append(node('li', 'Open the script and choose the next edit.'));
  const quick = byId('quick-links'); quick.replaceChildren();
  for (const [key, label] of [['narration','Read narration'],['sources','Sources'],['mac','Mac render code'],['publishing','Publishing pack']]) if (active.links[key]) quick.append(link(label + ' ↗', active.links[key]));
  const stages = byId('stages'); stages.replaceChildren();
  for (const stage of active.review.stages || []) { const row = node('div', undefined, 'stage-row'); row.title = stage.detail || ''; row.append(node('span', stage.label), node('span', stage.status.replaceAll('_',' '), `stage-status ${['approved','present'].includes(stage.status) ? '' : 'pending'}`)); stages.append(row); }
}
function renderChapters() {
  const chapters = active.review.chapters || [];
  const list = byId('chapter-list'); list.replaceChildren();
  byId('chapter-meta').textContent = `${chapters.length} chapters · ${active.review.summary?.timing_kind === 'measured_guide' ? 'measured guide timing' : 'timing not locked'}`;
  chapters.forEach((chapter, index) => {
    const button = node('button', undefined, 'chapter-button' + (index === selectedChapter ? ' active' : ''));
    button.type = 'button'; button.setAttribute('aria-pressed', String(index === selectedChapter));
    button.append(node('span', String(index+1).padStart(2,'0'),'chapter-index'), node('span',chapter.title), node('span',clock(chapter.start_seconds),'chapter-time'));
    button.addEventListener('click', () => { selectedChapter = index; renderChapters(); byId('chapter-list').querySelectorAll('button')[index].focus({preventScroll:true}); }); list.append(button);
  });
  const detail = byId('chapter-detail'); detail.replaceChildren();
  const chapter = chapters[selectedChapter];
  if (!chapter) { detail.append(node('p','Add Voiceover sections to the master script to build your chapter edit.','muted')); return; }
  detail.append(node('span', `CHAPTER ${String(selectedChapter+1).padStart(2,'0')} / ${chapter.words ?? chapter.word_count ?? 0} WORDS`, 'eyebrow'), node('h3',chapter.title));
  for (const [key,label] of [['picture_action','ON SCREEN'],['direction','EDIT DIRECTION']]) {
    detail.append(node('div',label,'detail-label'),node('p',chapter[key] || 'Visual direction has not been added yet.'));
  }
  const evidence = node('details'); evidence.append(node('summary','Evidence & interpretation'),node('p',chapter.evidence || 'No evidence note attached.')); detail.append(evidence);
  const actions = node('div',undefined,'chapter-actions');
  const cue = node('button',`Play from ${clock(chapter.start_seconds)}`,'secondary-button'); cue.type='button';
  cue.disabled = !active.media.audio || !Number.isFinite(chapter.start_seconds) || chapter.timing_kind !== 'measured_guide';
  const cueStatus = node('span','','fine'); cueStatus.setAttribute('role','status');
  cue.addEventListener('click',async () => {
    const player = byId('guide-audio'); byId('opening-video').pause();
    try { player.currentTime=chapter.start_seconds; await player.play(); cueStatus.textContent='Playing narration guide'; } catch { cueStatus.textContent='Press play on the narration player to listen.'; }
  });
  actions.append(cue); if (active.links.master) actions.append(link('Open full script ↗',active.links.master)); detail.append(actions,cueStatus);
}
function renderFiles() {
  const text = byId('file-search').value.trim().toLocaleLowerCase();
  const source = group === 'episode' ? (active?.files || []) : studio.artifacts;
  const files = source.filter(file => `${file.name} ${file.path}`.toLocaleLowerCase().includes(text));
  const target = byId('file-list'); target.replaceChildren();
  for (const file of files.slice(0,visibleFiles)) { const row = link('', file.href); row.className='file-row'; const description=node('span'); description.append(node('span',file.name,'file-name'),node('span',file.path,'file-path')); row.append(node('span',file.name.split('.').pop().toUpperCase(),'file-type'),description,node('span','↗','file-arrow')); target.append(row); }
  if (!files.length) target.append(node('p','No files match this search.','muted'));
  byId('file-count').textContent = `${files.length} ${files.length === 1 ? 'file' : 'files'}`;
  byId('more-files').hidden=files.length<=visibleFiles;
}
function renderMemory() {
  const list=byId('feedback-list'); list.replaceChildren();
  for (const feedback of active.feedback) { const item=node('li'); item.append(node('span',feedback.kind,'feedback-kind'),node('span',feedback.note)); list.append(item); }
  if (!active.feedback.length) list.append(node('li','No corrections saved for this episode yet.'));
  byId('hermes-command').textContent=`.\\hermes-studio.ps1 -Episode ${active.id} -Task 'Review the next chapter against my creator take.' -PrepareOnly`;
  byId('copy-status').textContent='';
  const checks=byId('checks'); checks.replaceChildren();
  for (const check of active.review.checks || []) { const row=node('div',undefined,'check-row'); row.append(node('strong',`${check.label} · ${check.status}`),node('span',check.detail)); checks.append(row); }
  byId('jobs').textContent=studio.jobs.length ? studio.jobs.map(job=>`${job.action}: ${job.state}`).join(' · ') : 'No queued jobs.';
}
function renderEpisode() {
  if (!active) { byId('video-empty').hidden=false; byId('opening-video').hidden=true; byId('guide-audio').hidden=true; byId('audio-empty').hidden=false; byId('copy-command').disabled=true; return; }
  byId('episode-title').textContent=active.title; byId('episode-number').textContent=String(active.release_order || '—').padStart(2,'0');
  setMedia('opening-video',active.media.video); setMedia('guide-audio',active.media.audio);
  const video=byId('opening-video'); if(active.media.poster) video.poster=active.media.poster; else video.removeAttribute('poster');
  byId('video-empty').hidden=Boolean(active.media.video); byId('audio-empty').hidden=Boolean(active.media.audio); setLink('video-download',active.media.video);
  byId('video-badge').textContent=active.media.finished?'LATEST REVIEW CUT':active.media.polished?'POLISHED REVIEW CUT':'LOCAL PREVIEW';
  byId('media-caption').textContent=active.media.finished?'30-second opening · local neural voice · ASR-timed captions':active.media.polished?'Polished review cut · see edit notes for source resolution':'Local render · synthetic guide voice';
  const summary=active.review.summary || {};
  byId('narration-summary').textContent=`${(summary.word_count || 0).toLocaleString()} words · ${clock(summary.duration_seconds)} ${summary.timing_kind === 'measured_guide' ? 'measured guide' : 'estimated / timing pending'}`;
  selectedChapter=0; visibleFiles=12; renderActions(); renderChapters(); renderFiles(); renderMemory();
}
const picker=byId('episode-select');
for(const episode of studio.episodes){const option=node('option',episode.id);option.value=episode.id;picker.append(option);}
picker.addEventListener('change',()=>{active=studio.episodes.find(e=>e.id===picker.value);renderEpisode();});
byId('file-search').addEventListener('input',()=>{visibleFiles=12;renderFiles();});
for(const button of document.querySelectorAll('[data-filter]'))button.addEventListener('click',()=>{group=button.dataset.filter;visibleFiles=12;document.querySelectorAll('[data-filter]').forEach(b=>{b.classList.toggle('active',b===button);b.setAttribute('aria-pressed',String(b===button));});renderFiles();});
byId('more-files').addEventListener('click',()=>{visibleFiles+=24;renderFiles();});
byId('copy-command').addEventListener('click',async()=>{try{await navigator.clipboard.writeText(byId('hermes-command').textContent);byId('copy-status').textContent=' Copied';}catch{const selection=window.getSelection();const range=document.createRange();range.selectNodeContents(byId('hermes-command'));selection.removeAllRanges();selection.addRange(range);byId('copy-status').textContent=' Selected — press Ctrl+C to copy';}});
byId('opening-video').addEventListener('play',()=>byId('guide-audio').pause());byId('guide-audio').addEventListener('play',()=>byId('opening-video').pause());
for(const item of document.querySelectorAll('.nav-link'))item.addEventListener('click',()=>{document.querySelectorAll('.nav-link').forEach(n=>n.classList.toggle('active',n===item));});
byId('generated').dateTime=studio.generated;byId('generated').textContent=new Date(studio.generated).toLocaleDateString(undefined,{month:'short',day:'numeric'});
setLink('guide-link',studio.guides.runbook);setLink('hermes-guide',studio.guides.hermes);renderEpisode();
