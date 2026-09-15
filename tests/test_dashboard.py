import json
from pathlib import Path

from studio.core import Studio
from studio.dashboard import build
from studio.dashboard_data import build_data


def test_dashboard_episode_data_is_local_scoped_and_html_safe(tmp_path):
    s = Studio(tmp_path)
    s.new('sample', '</script><script>alert(1)</script>', 'My view')
    s.new('second', 'Other episode', 'Another view')
    s.feedback('sample', 'Keep my angle', 'voice')
    s.feedback('second', 'Other correction', 'voice')
    data = build_data(s)
    sample = next(e for e in data['episodes'] if e['id'] == 'sample')
    assert [f['note'] for f in sample['feedback']] == ['Keep my angle']
    assert sample['links']['take'].endswith('CREATOR_TAKE.md')
    html = build(s).read_text(encoding='utf-8')
    assert '</script><script>alert(1)</script>' not in html
    assert 'type="application/json"' in html
    assert 'Search studio files' in html
    assert (s.state / 'dashboard-assets/app.js').is_file()
    assert (s.state / 'dashboard-assets/style.css').is_file()


def test_dashboard_missing_or_escaping_assets_are_never_linked(tmp_path):
    s = Studio(tmp_path); s.new('sample', 'Title', 'Take')
    manifest = s.episode('sample') / 'manifests/production-assets.json'
    manifest.write_text(json.dumps({'schema_version': 1, 'opening': {
        'video': '../outside.mp4', 'poster': 'https://example.com/tracker.png'},
        'guide': {'audio': '.studio/missing.wav'}}))
    episode = build_data(s)['episodes'][0]
    assert not episode['media']['video']
    assert not episode['media']['poster']
    assert not episode['media']['audio']


def test_dashboard_artifacts_skip_raw_frames_and_use_verified_selection(tmp_path):
    s = Studio(tmp_path); s.new('sample', 'Title', 'Take')
    frames = s.state / 'renders/old/frames'; frames.mkdir(parents=True)
    (frames / 'frame_0001.png').write_bytes(b'fake')
    current = s.state / 'renders/current'; current.mkdir()
    (current / 'video.mp4').write_bytes(b'placeholder')
    record = s.episode('sample') / 'production.json'
    record.write_text(json.dumps({'episode': 'sample', 'title': 'Title', 'stage': 'draft', 'release_order': 1}))
    manifest = s.episode('sample') / 'manifests/production-assets.json'
    manifest.write_text(json.dumps({'schema_version': 1, 'opening': {
        'video': '.studio/renders/current/video.mp4'}}))
    data = build_data(s)
    assert data['episodes'][0]['media']['video'] == 'renders/current/video.mp4'
    assert all('frame_0001' not in a['path'] for a in data['artifacts'])
    assert len(data['artifacts']) <= 150


def test_one_broken_episode_does_not_hide_other_work(tmp_path):
    s = Studio(tmp_path); s.new('good', 'Good episode', 'Keep this')
    s.new('broken', 'Broken', 'Keep this too')
    (s.episode('broken') / 'production.json').write_text('{malformed')
    data = build_data(s)
    assert {episode['id'] for episode in data['episodes']} == {'good', 'broken'}
    broken = next(episode for episode in data['episodes'] if episode['id'] == 'broken')
    assert broken['title'] == 'broken'
    assert next(c for c in broken['review']['checks'] if c['id'] == 'production_config')['status'] == 'invalid'


def test_finished_cut_and_matching_mac_packet_take_priority(tmp_path):
    s = Studio(tmp_path); s.new('sample', 'Title', 'Take')
    for relative in ('.studio/renders/hd/video.mp4', '.studio/renders/hd/poster.png',
                     '.studio/renders/old/video.mp4', 'episodes/sample/mac/opening-hd/README.md'):
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('fixture')
    manifest = s.episode('sample') / 'manifests/production-assets.json'
    manifest.write_text(json.dumps({'schema_version': 1, 'opening': {
        'finished_video': '.studio/renders/hd/video.mp4', 'finished_poster': '.studio/renders/hd/poster.png',
        'polished_video': '.studio/renders/old/video.mp4'},
        'mac': {'readme': 'episodes/sample/mac/opening-hd/README.md'}}))
    episode = build_data(s)['episodes'][0]
    assert episode['media']['video'] == 'renders/hd/video.mp4'
    assert episode['media']['poster'] == 'renders/hd/poster.png'
    assert episode['media']['finished']
    assert episode['links']['mac'].endswith('mac/opening-hd/README.md')
