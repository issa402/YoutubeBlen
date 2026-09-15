"""Small, episode-scoped view model for the local production desk."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
from urllib.parse import quote


def local_file(studio, relative):
    if not isinstance(relative, str) or ':' in relative or '\\' in relative:
        return None
    candidate = Path(relative)
    if candidate.is_absolute() or '..' in candidate.parts:
        return None
    path = (studio.root / candidate).resolve()
    return path if path.is_relative_to(studio.root) and path.is_file() else None


def href(studio, path):
    return quote(Path(os.path.relpath(path, studio.state)).as_posix(), safe='/') if path else None


def episode_data(studio, record):
    folder = studio.require_episode(record['episode'])
    links = {name: href(studio, path) if path.is_file() else None for name, relative in {
        'take': 'CREATOR_TAKE.md', 'narration': 'script/NARRATION.md',
        'master': 'script/MASTER_PRODUCTION_SCRIPT.md', 'sources': 'research/SOURCE_REGISTER.md',
        'claims': 'CLAIMS_LEDGER.md', 'shorts': 'script/SHORTS.md',
        'publishing': 'script/PUBLISHING_PACK.md', 'handoff': 'PRODUCTION_HANDOFF.md',
        'mac': 'mac/opening/README.md', 'recording': 'script/RECORDING_GUIDE.md'
    }.items() for path in [folder / relative]}
    manifest_path = folder / 'manifests/production-assets.json'
    try:
        manifest = json.loads(manifest_path.read_text(encoding='utf-8-sig')) if manifest_path.is_file() else {}
    except (ValueError, OSError):
        manifest = {}
    if not isinstance(manifest, dict):
        manifest = {}
    opening = manifest.get('opening', {})
    guide = manifest.get('guide', {})
    opening = opening if isinstance(opening, dict) else {}
    guide = guide if isinstance(guide, dict) else {}
    mac = manifest.get('mac', {})
    mac_readme = local_file(studio, mac.get('readme')) if isinstance(mac, dict) else None
    if mac_readme:
        links = links | {'mac': href(studio, mac_readme)}
    finished = local_file(studio, opening.get('finished_video'))
    polished = local_file(studio, opening.get('polished_video'))
    video = finished or polished or local_file(studio, opening.get('video'))
    poster = local_file(studio, opening.get('finished_poster')) if finished else None
    poster = poster or (local_file(studio, opening.get('polished_poster')) if polished else None)
    poster = poster or local_file(studio, opening.get('poster'))
    from .review import review_episode
    review = review_episode(studio, record['episode'])
    feedback = [r for r in studio.feedback_records() if r['active'] and r['episode'] == record['episode']]
    metrics = [r for r in studio.metric_records() if r['episode'] == record['episode']]
    files = [{'name': path.name, 'path': path.relative_to(studio.root).as_posix(), 'href': href(studio, path)}
             for path in sorted(folder.rglob('*')) if path.is_file() and not path.is_symlink()
             and path.resolve().is_relative_to(studio.root) and path.suffix in ('.md', '.txt', '.json')
             and not any(part in ('frames', 'previews') for part in path.relative_to(folder).parts)]
    return {'id': record['episode'], 'title': record['title'], 'stage': record.get('stage', 'Draft'),
            'release_order': record.get('release_order'), 'links': links, 'review': review,
            'media': {'video': href(studio, video), 'poster': href(studio, poster),
                      'audio': href(studio, local_file(studio, guide.get('audio'))),
                      'polished': bool(polished), 'finished': bool(finished)},
            'feedback': feedback, 'metrics': metrics, 'files': files}


def episode_records(studio):
    base = studio.root / 'episodes'
    records = []
    for folder in sorted(base.iterdir()) if base.is_dir() else []:
        if not folder.is_dir() or not folder.resolve().is_relative_to(studio.root):
            continue
        try:
            studio.require_episode(folder.name)
        except ValueError:
            continue
        try:
            record = json.loads((folder / 'production.json').read_text(encoding='utf-8-sig'))
            if not isinstance(record, dict):
                raise ValueError('Episode record must be an object.')
        except (ValueError, OSError):
            record = {'stage': 'Episode details need review'}
        title = record.get('title')
        order = record.get('release_order')
        records.append(record | {'episode': folder.name, 'title': title if isinstance(title, str) else folder.name,
                                  'release_order': order if type(order) is int and order > 0 else None})
    return sorted(records, key=lambda r: (r.get('release_order') or 999, r['episode']))


def build_data(studio):
    records = episode_records(studio)
    episodes = [episode_data(studio, r) for r in records]
    artifacts = []
    for directory in ('renders', 'audio', 'reviews', 'media', 'packages'):
        base = studio.state / directory
        for path in sorted(base.rglob('*')):
            if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(studio.root):
                continue
            if any(part in ('frames', 'previews') for part in path.relative_to(base).parts):
                continue
            if path.name.startswith('segment_') or path.suffix not in ('.mp4', '.wav', '.md', '.srt', '.csv'):
                continue
            artifacts.append({'name': path.name, 'path': path.relative_to(studio.state).as_posix(), 'href': href(studio, path)})
    return {'generated': datetime.now(timezone.utc).isoformat(), 'episodes': episodes,
            'artifacts': artifacts[:150], 'jobs': studio.jobs()[-20:],
            'guides': {name: href(studio, studio.root / relative) for name, relative in {
                'hermes': 'tools/HERMES_WORKFLOW.md', 'editing': 'tools/NARRATION_AND_EDITING.md',
                'runbook': 'tools/STUDIO_RUNBOOK.md'}.items()}}
