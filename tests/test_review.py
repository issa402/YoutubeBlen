"""Production review must describe actual state rather than score editorial opinion."""
import csv
import hashlib
import json
import wave

import pytest

from studio.core import Studio, write_json
from studio.review import export_review, review_episode


MASTER = ('# Football\n\n## 00:00–00:10 — My opening\n### Voiceover\n'
          'My strong opinion.\n\nAnother thought.\n### Picture/action\n'
          'Red figure and a trophy.\n### Direction\nHold the final shot.\n'
          '### Evidence\nC01 OPINION\n\n## 00:10–00:20 — Follow the record\n'
          '### Voiceover\nThe announcement exists.\n### Picture/action\nShow the dated source.\n'
          '### Evidence\nC02 VERIFIED_FACT SRC01\n')
TEXT = 'My strong opinion.\n\nAnother thought.\n\nThe announcement exists.\n'


@pytest.fixture
def episode(tmp_path):
    studio = Studio(tmp_path)
    studio.new('sample', 'Football', 'I admire visible ambition.')
    base = studio.episode('sample')
    (base / 'script/MASTER_PRODUCTION_SCRIPT.md').write_text(MASTER, encoding='utf-8')
    (base / 'script/NARRATION.txt').write_text(TEXT, encoding='utf-8')
    (base / 'research/SOURCE_REGISTER.md').write_text(
        '| SRC01 | [Announcement](https://example.org/announcement) | Limits |\n', encoding='utf-8')
    return studio


def make_guide(studio):
    folder = studio.state / 'audio/guide'
    folder.mkdir(parents=True)
    with wave.open(str(folder / 'guide.wav'), 'wb') as stream:
        stream.setnchannels(1)
        stream.setsampwidth(2)
        stream.setframerate(8000)
        stream.writeframes(b'\0\0' * 8000 * 6)
    timeline = {
        'synthetic_guide': True, 'duration_seconds': 6,
        'source_sha256': hashlib.sha256((studio.episode('sample') / 'script/MASTER_PRODUCTION_SCRIPT.md').read_bytes()).hexdigest(),
        'segments': [
            {'shot': 'SH01', 'text': 'My strong opinion.', 'start_seconds': 0, 'end_seconds': 1},
            {'shot': 'SH01', 'text': 'Another thought.', 'start_seconds': 1, 'end_seconds': 3},
            {'shot': 'SH02', 'text': 'The announcement exists.', 'start_seconds': 3, 'end_seconds': 6},
        ],
    }
    write_json(folder / 'timeline.json', timeline)
    write_json(folder / 'report.json', {'synthetic_guide': True, 'final_voice_approved': False})
    manifest = {'schema_version': 1, 'guide': {
        'timeline': '.studio/audio/guide/timeline.json',
        'audio': '.studio/audio/guide/guide.wav',
        'report': '.studio/audio/guide/report.json',
    }}
    write_json(studio.episode('sample') / 'manifests/production-assets.json', manifest)
    return timeline, manifest


def check(report, name):
    return next(item for item in report['checks'] if item['id'] == name)


def stage(report, name):
    return next(item for item in report['stages'] if item['id'] == name)


def test_review_is_read_only_and_distinguishes_presence_from_approval(episode):
    before = {str(p): p.read_bytes() for p in episode.root.rglob('*') if p.is_file()}
    result = review_episode(episode, 'sample')
    assert result['summary']['word_count'] == 8
    assert result['summary']['chapter_count'] == 2
    assert result['summary']['timing_kind'] == 'estimated'
    assert check(result, 'narration_agreement')['status'] == 'pass'
    assert check(result, 'source_records')['status'] == 'present'
    assert stage(result, 'script')['status'] == 'draft'
    assert stage(result, 'evidence')['status'] == 'review_needed'
    assert result['sources']['verified_by_review'] is False
    assert 'quality_score' not in result
    assert result['chapters'][0]['title'] == 'My opening'
    assert result['chapters'][0]['picture_action'] == 'Red figure and a trophy.'
    assert result['chapters'][0]['evidence'] == 'C01 OPINION'
    assert len(result['next_actions']) == 3
    assert before == {str(p): p.read_bytes() for p in episode.root.rglob('*') if p.is_file()}


def test_valid_guide_uses_measured_chapter_times_not_script_labels(episode):
    make_guide(episode)
    result = review_episode(episode, 'sample')
    assert result['summary']['duration_seconds'] == 6
    assert result['summary']['timing_kind'] == 'measured_guide'
    assert result['chapters'][0]['end_seconds'] == 3
    assert result['chapters'][1]['start_seconds'] == 3
    assert check(result, 'guide_timing')['status'] == 'pass'
    assert stage(result, 'narration')['status'] == 'guide_only'


def test_changed_master_fingerprint_invalidates_old_guide(episode):
    make_guide(episode)
    path = episode.episode('sample') / 'script/MASTER_PRODUCTION_SCRIPT.md'
    path.write_text(MASTER.replace('Hold the final shot.', 'Move the camera.'), encoding='utf-8')
    result = review_episode(episode, 'sample')
    assert check(result, 'guide_timing')['status'] == 'stale'
    assert 'fingerprint' in check(result, 'guide_timing')['detail'].lower()
    assert result['summary']['timing_kind'] == 'estimated'


@pytest.mark.parametrize('damage', ['text', 'shot', 'nan', 'overlap', 'gap', 'duration', 'hash', 'shape'])
def test_bad_or_stale_timeline_never_becomes_measured_timing(episode, damage):
    timeline, _ = make_guide(episode)
    if damage == 'text': timeline['segments'][0]['text'] = 'An obsolete opinion.'
    if damage == 'shot': timeline['segments'][0]['shot'] = 'SH02'
    if damage == 'nan': timeline['segments'][0]['end_seconds'] = float('nan')
    if damage == 'overlap': timeline['segments'][1]['start_seconds'] = 0.5
    if damage == 'gap': timeline['segments'][1]['start_seconds'] = 1.5
    if damage == 'duration': timeline['duration_seconds'] = 40
    if damage == 'hash': timeline['source_sha256'] = '0' * 64
    if damage == 'shape': timeline['segments'] = ['not a segment']
    write_json(episode.state / 'audio/guide/timeline.json', timeline)
    result = review_episode(episode, 'sample')
    assert check(result, 'guide_timing')['status'] in ('invalid', 'stale')
    assert result['summary']['timing_kind'] == 'estimated'


def test_recording_text_conflict_is_explicit_and_actionable(episode):
    (episode.episode('sample') / 'script/NARRATION.txt').write_text('A different view.')
    result = review_episode(episode, 'sample')
    assert check(result, 'narration_agreement')['status'] == 'stale'
    assert result['next_actions'][0]['id'] == 'sync_narration'


def test_empty_episode_and_malformed_config_return_honest_state(tmp_path):
    studio = Studio(tmp_path)
    studio.new('new', 'New idea', 'My view')
    (studio.episode('new') / 'production.json').write_text('{broken')
    result = review_episode(studio, 'new')
    assert result['summary']['word_count'] == 0
    assert stage(result, 'script')['status'] == 'missing'
    assert check(result, 'production_config')['status'] == 'invalid'
    assert result['next_actions'][0]['id'] == 'draft_script'


@pytest.mark.parametrize('path', ['../secret.wav', 'C:/outside/secret.wav', '/tmp/secret.wav'])
def test_asset_references_cannot_escape_workspace(episode, path):
    _, manifest = make_guide(episode)
    manifest['guide']['audio'] = path
    write_json(episode.episode('sample') / 'manifests/production-assets.json', manifest)
    result = review_episode(episode, 'sample')
    assert check(result, 'asset_manifest')['status'] == 'invalid'
    assert result['summary']['timing_kind'] == 'estimated'


def test_approval_flags_do_not_verify_sources_or_synthetic_voice(episode):
    make_guide(episode)
    write_json(episode.episode('sample') / 'production.json', {
        'title': 'Football', 'script_approved': True, 'publish_approved': True})
    result = review_episode(episode, 'sample')
    assert stage(result, 'script')['status'] == 'approved'
    assert stage(result, 'publish')['status'] == 'approval_recorded'
    assert stage(result, 'evidence')['status'] == 'review_needed'
    assert stage(result, 'narration')['status'] == 'guide_only'


def test_export_delivers_editable_timeline_and_preserves_existing_output(episode):
    make_guide(episode)
    output = episode.state / 'reviews/first'
    result = export_review(episode, 'sample', output)
    assert result['summary']['timing_kind'] == 'measured_guide'
    assert (output / 'review.md').is_file()
    assert (output / 'review.json').is_file()
    with (output / 'edit-timeline.csv').open(encoding='utf-8-sig', newline='') as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 2
    assert rows[1]['start_seconds'] == '3.0'
    assert rows[0]['evidence'] == 'C01 OPINION'
    assert 'synthetic guide' in (output / 'review.md').read_text(encoding='utf-8').lower()
    with pytest.raises(FileExistsError):
        export_review(episode, 'sample', output)


def test_review_rejects_unknown_episode_and_export_escape(episode, tmp_path):
    with pytest.raises(FileNotFoundError):
        review_episode(episode, 'absent')
    with pytest.raises(ValueError, match='workspace'):
        export_review(episode, 'sample', tmp_path.parent / 'outside-review')


def test_missing_referenced_sources_and_invalid_auxiliary_records_are_visible(episode):
    base = episode.episode('sample')
    (base / 'research/SOURCE_REGISTER.md').write_text('No source rows yet.')
    (base / 'research/sources.json').write_text('{invalid')
    result = review_episode(episode, 'sample')
    assert result['sources']['missing_references'] == ['SRC01']
    assert check(result, 'source_records')['status'] == 'missing_references'
    assert 'unreadable' in check(result, 'source_records')['detail'].lower()


def test_audio_changed_independently_invalidates_timing(episode):
    make_guide(episode)
    path = episode.state / 'audio/guide/guide.wav'
    with wave.open(str(path), 'wb') as stream:
        stream.setnchannels(1)
        stream.setsampwidth(2)
        stream.setframerate(8000)
        stream.writeframes(b'\0\0' * 8000)
    result = review_episode(episode, 'sample')
    assert check(result, 'guide_timing')['status'] == 'invalid'
    assert 'WAV duration' in check(result, 'guide_timing')['detail']


def test_csv_export_does_not_turn_source_text_into_spreadsheet_formulas(episode):
    path = episode.episode('sample') / 'script/MASTER_PRODUCTION_SCRIPT.md'
    path.write_text(MASTER.replace('My opening', '=1+1'), encoding='utf-8')
    output = episode.state / 'reviews/formula'
    export_review(episode, 'sample', output)
    with (output / 'edit-timeline.csv').open(encoding='utf-8-sig', newline='') as stream:
        row = next(csv.DictReader(stream))
    assert row['title'] == "'=1+1"
