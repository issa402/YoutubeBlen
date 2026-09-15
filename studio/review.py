"""Read-only production evidence and an exportable, measured chapter edit plan.

This checks files and internal agreement. It does not judge whether an opinion is
correct, certify cited facts, or treat an existing preview as a completed episode.
"""
import csv
import hashlib
import json
import math
from pathlib import Path, PureWindowsPath
import re
import wave

from .core import write_json
from .episode import read_shots
from .narration import chapter_title, wave_info


def _normal(text):
    return ' '.join(text.split())


def _check(name, status, label, detail):
    return {'id': name, 'status': status, 'label': label, 'detail': detail}


def _json(path):
    value = json.loads(path.read_text(encoding='utf-8-sig'))
    if not isinstance(value, dict):
        raise ValueError('Expected a JSON object.')
    return value


def _relative(root, path):
    return path.relative_to(root).as_posix()


def _asset_path(root, value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError('Asset paths must be nonempty workspace-relative strings.')
    if Path(value).is_absolute() or PureWindowsPath(value).drive:
        raise ValueError('Asset paths must be workspace-relative, not absolute.')
    candidate = (root / value).resolve()
    if not candidate.is_relative_to(root):
        raise ValueError('Asset path escapes workspace.')
    return candidate


def _assets(root, base):
    path = base / 'manifests/production-assets.json'
    if not path.is_file():
        return {}, _check('asset_manifest', 'missing', 'Production assets',
                         'No explicit asset manifest; generated files were not guessed from old runs.')
    fields = {'guide': ('timeline', 'audio', 'report'),
              'opening': ('video', 'verification', 'motion_report', 'poster', 'polished_video', 'polished_poster',
                          'finished_video', 'finished_poster', 'finish_validation', 'alignment', 'voice', 'voice_timeline'),
              'mac': ('readme',)}
    try:
        manifest = _json(path)
        if type(manifest.get('schema_version')) is not int or manifest['schema_version'] != 1:
            raise ValueError('Production asset manifest requires schema_version 1.')
        paths = {}
        for section, names in fields.items():
            group = manifest.get(section, {})
            if not isinstance(group, dict):
                raise ValueError(f'Asset group {section} must be an object.')
            paths |= {f'{section}_{name}': _asset_path(root, group[name]) for name in names if name in group}
        return paths, _check('asset_manifest', 'present', 'Production assets',
                             'Explicit workspace paths loaded; file presence is checked separately.')
    except (ValueError, OSError) as exc:
        return {}, _check('asset_manifest', 'invalid', 'Production assets', str(exc))


def _script(base):
    path = base / 'script/MASTER_PRODUCTION_SCRIPT.md'
    try:
        shots = read_shots(path)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        return shots, digest, _check('master_script', 'present', 'Master script',
                                     f'{len(shots)} chapters with separate narration and production notes.')
    except FileNotFoundError:
        return [], None, _check('master_script', 'missing', 'Master script', 'No master production script yet.')
    except (ValueError, OSError) as exc:
        return [], None, _check('master_script', 'invalid', 'Master script', str(exc))


def _narration(base, shots):
    path = base / 'script/NARRATION.txt'
    expected = _normal(' '.join(shot['voiceover'] for shot in shots))
    expected_sha = hashlib.sha256(expected.encode('utf-8')).hexdigest() if shots else None
    if not path.is_file():
        return expected_sha, _check('narration_agreement', 'missing', 'Recording text',
                                    'Clean NARRATION.txt has not been prepared.')
    try:
        actual = _normal(path.read_text(encoding='utf-8-sig'))
    except (OSError, UnicodeError) as exc:
        return expected_sha, _check('narration_agreement', 'invalid', 'Recording text', str(exc))
    agrees = bool(shots) and actual == expected
    return expected_sha, _check('narration_agreement', 'pass' if agrees else 'stale', 'Recording text',
                                'Clean narration matches the master voiceover passages.' if agrees else
                                'Clean narration differs from the current master; reconcile before recording.')


def _sources(base, shots):
    register = base / 'research/SOURCE_REGISTER.md'
    warnings = []
    try:
        text = register.read_text(encoding='utf-8-sig') if register.is_file() else ''
    except (ValueError, OSError):
        text = ''
        warnings = ['Source register is unreadable.']
    records = re.findall(r'^\|\s*([A-Z]+\d+)\s*\|[^\n]*https?://[^\n]+', text, re.M)
    json_path = base / 'research/sources.json'
    extra = []
    try:
        value = json.loads(json_path.read_text(encoding='utf-8-sig')) if json_path.is_file() else []
        if not isinstance(value, list):
            raise ValueError('Source records must be a list.')
        extra = [item for item in value if isinstance(item, dict)
                 and isinstance(item.get('url'), str) and re.match(r'https?://', item['url'])]
    except (ValueError, OSError):
        warnings = [*warnings, 'Auxiliary sources.json is unreadable; it contributes no source records.']
    ids = sorted(set(records) | {item['id'] for item in extra if isinstance(item.get('id'), str)})
    used = set(re.findall(r'\b[A-Z]{2,}\d+\b', ' '.join(shot.get('evidence', '') for shot in shots)))
    missing = sorted(used - set(ids))
    count = len(set(records)) + len(extra)
    detail = (f'{count} source records found. Presence does not verify a claim, quotation or media rights.'
              if count else 'No source records found. Opinion can remain opinion; factual passages need sources.')
    if missing:
        detail += f" Missing referenced IDs: {', '.join(missing)}."
    if warnings:
        detail += ' ' + ' '.join(warnings)
    return {'record_count': count, 'ids': ids, 'missing_references': missing, 'verified_by_review': False}, _check(
        'source_records', 'missing_references' if missing else ('present' if count else 'missing'),
        'Source records', detail)


def _number(value):
    return isinstance(value, (float, int)) and not isinstance(value, bool) and math.isfinite(value)


def _validate_timeline(timeline, shots, digest, audio):
    if timeline.get('source_sha256') != digest:
        return 'stale', 'Guide script fingerprint differs from the current master; regenerate the guide.', {}
    segments = timeline.get('segments')
    if not isinstance(segments, list) or not segments or not all(isinstance(s, dict) for s in segments):
        return 'invalid', 'Guide timeline has no valid paragraph segments.', {}
    if not all(isinstance(s.get('text'), str) and isinstance(s.get('shot'), str) for s in segments):
        return 'invalid', 'Guide segments need text and chapter IDs.', {}
    expected = [(shot['id'], _normal(p)) for shot in shots
                for p in re.split(r'\n\s*\n', shot['voiceover']) if p.strip()]
    if [(s['shot'], _normal(s['text'])) for s in segments] != expected:
        return 'stale', 'Guide paragraph text or chapter order differs from the current master.', {}
    previous = 0.0
    for segment in segments:
        start, end = segment.get('start_seconds'), segment.get('end_seconds')
        if not (_number(start) and _number(end) and end > start and abs(start - previous) < .01):
            return 'invalid', 'Guide timing must be finite, continuous and in order, beginning at zero.', {}
        previous = float(end)
    duration = timeline.get('duration_seconds')
    if not _number(duration) or abs(duration - previous) > .02:
        return 'invalid', 'Guide duration disagrees with the final paragraph boundary.', {}
    _, actual_duration = wave_info(audio)
    if abs(actual_duration - duration) > .05:
        return 'invalid', 'Guide WAV duration disagrees with its timeline.', {}
    bounds = {shot['id']: {'start_seconds': float(next(s['start_seconds'] for s in segments if s['shot'] == shot['id'])),
                           'end_seconds': float([s['end_seconds'] for s in segments if s['shot'] == shot['id']][-1])}
              for shot in shots}
    return 'pass', ('Measured synthetic guide timing matches the master fingerprint, paragraph text and WAV duration. '
                    'Final performance and word-level caption alignment remain separate.'), bounds


def _timing(paths, shots, digest):
    timeline, audio = paths.get('guide_timeline'), paths.get('guide_audio')
    if not shots or not timeline or not timeline.is_file() or not audio or not audio.is_file():
        return {}, _check('guide_timing', 'missing', 'Guide timing',
                          'A matching timeline and guide WAV are required for measured chapter timings.')
    try:
        data = _json(timeline)
        if data.get('synthetic_guide') is not True:
            raise ValueError('This review supports explicitly identified synthetic guide timelines.')
        status, detail, bounds = _validate_timeline(data, shots, digest, audio)
        return bounds, _check('guide_timing', status, 'Guide timing', detail)
    except (ValueError, OSError, wave.Error, EOFError, ZeroDivisionError) as exc:
        return {}, _check('guide_timing', 'invalid', 'Guide timing', str(exc))


def _chapters(shots, timing):
    chapters = []
    elapsed = 0.0
    for shot in shots:
        words = len(shot['voiceover'].split())
        bounds = timing.get(shot['id'], {'start_seconds': round(elapsed, 3),
                                       'end_seconds': round(elapsed + words / 145 * 60, 3)})
        chapters.append({'id': shot['id'], 'title': chapter_title(shot['section']),
                         'section': shot['section'], 'words': words, **bounds,
                         'timing_kind': 'measured_guide' if timing else 'estimated',
                         'picture_action': shot.get('picture/action', ''),
                         'direction': shot.get('direction', ''), 'evidence': shot.get('evidence', '')})
        elapsed = bounds['end_seconds']
    return chapters


def _next_actions(checks, config):
    state = {item['id']: item['status'] for item in checks}
    candidates = [
        (state['master_script'] != 'present', 'draft_script', 'Draft the master script',
         'Write chapter voiceover from the creator take, with separate picture and evidence notes.'),
        (state['narration_agreement'] != 'pass', 'sync_narration', 'Reconcile the recording text',
         'Make NARRATION.txt agree with the current master voiceover; preserve the creator opinion.'),
        (state['guide_timing'] in ('stale', 'invalid'), 'refresh_guide', 'Regenerate the timing guide',
         'The current guide does not match the script or audio; do not edit to obsolete timings.'),
        (state['source_records'] != 'present', 'review_sources', 'Resolve the source records',
         'Supply missing factual source references and review their scope; presence alone is not clearance.'),
        (config.get('script_approved') is not True, 'review_script', 'Review the narration draft',
         'Check the spoken performance and factual passages, then record your script decision.'),
        (True, 'final_voice', 'Choose and record the final voice',
         'A synthetic guide is a timing reference. Record the intended performance and align captions to that take.'),
        (True, 'finish_visuals', 'Complete the chapter visuals',
         'Use the exported edit timeline to build the remaining chapter shots, source cards and final sequence.'),
        (config.get('publish_approved') is not True, 'final_review', 'Review the completed episode',
         'Review the final voice, picture, sources and packaging together before publishing.'),
    ]
    return [{'id': name, 'label': label, 'detail': detail}
            for needed, name, label, detail in candidates if needed][:3]


def review_episode(studio, episode):
    """Describe one episode using explicit local evidence; never change its state."""
    base = studio.require_episode(episode)
    try:
        config = _json(base / 'production.json')
        config_check = _check('production_config', 'present', 'Episode decisions', 'Existing approval flags read without changes.')
    except (ValueError, OSError) as exc:
        config = {}
        config_check = _check('production_config', 'invalid', 'Episode decisions', str(exc))
    shots, digest, script_check = _script(base)
    narration_digest, narration_check = _narration(base, shots)
    source_data, source_check = _sources(base, shots)
    paths, asset_check = _assets(studio.root, base)
    timing, timing_check = _timing(paths, shots, digest)
    chapters = _chapters(shots, timing)
    opening = bool(paths.get('opening_video') and paths['opening_video'].is_file())
    mac = bool(paths.get('mac_readme') and paths['mac_readme'].is_file())
    checks = [config_check, script_check, narration_check, source_check, asset_check, timing_check,
              _check('opening_video', 'present' if opening else 'missing', 'Opening preview',
                     'Opening video is present; this is a partial episode, not an approved final edit.' if opening else 'No opening preview is linked and present.'),
              _check('mac_package', 'present' if mac else 'missing', 'Mac handoff',
                     'Mac package instructions are present; native execution is not established by this review.' if mac else 'No Mac package instructions are linked and present.')]
    stages = [
        _check('script', 'approved' if shots and config.get('script_approved') is True else ('draft' if shots else 'missing'),
               'Script', 'Approval is an explicit recorded decision; file presence means draft available.'),
        _check('evidence', 'review_needed' if source_data['record_count'] else 'missing',
               'Evidence', 'Source records and internal labels need editorial review; this check does not certify their claims.'),
        _check('narration', 'guide_only' if timing else ('text_only' if shots else 'missing'),
               'Narration', 'Synthetic timing voice does not establish final voice approval.'),
        _check('visuals', 'partial' if opening else 'missing', 'Visuals',
               'The opening is one component; remaining chapters and the final sequence need editing.'),
        _check('publish', 'approval_recorded' if config.get('publish_approved') is True else 'not_approved',
               'Release', 'The stored flag records intent; it does not establish that a final episode exists or was published.'),
    ]
    standard = {'master_script': base / 'script/MASTER_PRODUCTION_SCRIPT.md', 'narration': base / 'script/NARRATION.txt',
                'source_register': base / 'research/SOURCE_REGISTER.md', 'shorts': base / 'script/SHORTS.md',
                'publishing_pack': base / 'script/PUBLISHING_PACK.md'}
    artifacts = {name: _relative(studio.root, path) for name, path in (standard | paths).items() if path.is_file()}
    return {'schema_version': 1, 'episode': episode, 'title': config.get('title', episode),
            'script_sha256': digest, 'narration_sha256': narration_digest,
            'summary': {'word_count': sum(ch['words'] for ch in chapters), 'chapter_count': len(chapters),
                        'timing_kind': 'measured_guide' if timing else 'estimated',
                        'duration_seconds': chapters[-1]['end_seconds'] if chapters else 0},
            'sources': source_data, 'checks': checks, 'stages': stages, 'chapters': chapters,
            'next_actions': _next_actions(checks, config), 'artifacts': artifacts}


def _markdown(report):
    summary = report['summary']
    measured = summary['timing_kind'] == 'measured_guide'
    lines = [f"# Production review — {report['title']}", '',
             f"{summary['word_count']} words · {summary['chapter_count']} chapters · {summary['duration_seconds']:.1f} seconds.", '',
             'Timing: measured synthetic guide; final performance may differ.' if measured else
             'Timing: estimate at 145 words per minute; no matching measured guide.', '',
             'File presence is not evidence clearance or final production approval. Creator opinions are preserved.', '',
             '## Next actions', '']
    lines += [f"- **{item['label']}** — {item['detail']}" for item in report['next_actions']]
    lines += ['', '## Checks', '']
    lines += [f"- **{item['label']} · {item['status']}** — {item['detail']}" for item in report['checks']]
    lines += ['', '## Chapter edit plan', '']
    for chapter in report['chapters']:
        lines += [f"### {chapter['id']} · {chapter['title']}", '',
                  f"{chapter['start_seconds']:.3f}–{chapter['end_seconds']:.3f}s · {chapter['words']} words · {chapter['timing_kind']}", '',
                  f"Picture: {chapter['picture_action']}", '', f"Direction: {chapter['direction']}", '',
                  f"Internal evidence notes: {chapter['evidence']}", '']
    return '\n'.join(lines) + '\n'


def export_review(studio, episode, output):
    """Write a fresh snapshot and editable CSV; refuse overwrites or workspace escape."""
    destination = Path(output)
    destination = (destination if destination.is_absolute() else studio.root / destination).resolve()
    if not destination.is_relative_to(studio.root):
        raise ValueError('Review output must remain inside the workspace.')
    report = review_episode(studio, episode)
    destination.mkdir(parents=True, exist_ok=False)
    write_json(destination / 'review.json', report)
    (destination / 'review.md').write_text(_markdown(report), encoding='utf-8')
    fields = ['id', 'title', 'words', 'start_seconds', 'end_seconds', 'timing_kind', 'picture_action', 'direction', 'evidence']
    with (destination / 'edit-timeline.csv').open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows({key: _csv_text(value) for key, value in chapter.items()}
                         for chapter in report['chapters'])
    return report | {'output': str(destination)}


def _csv_text(value):
    """Keep production prose as text when opening the edit sheet in a spreadsheet."""
    if isinstance(value, str) and value.lstrip().startswith(('=', '+', '-', '@', '\t', '\r')):
        return "'" + value
    return value
