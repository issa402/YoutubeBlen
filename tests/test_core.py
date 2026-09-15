import json
import pytest
from studio.core import Studio


def test_episode_preserves_take_and_never_overwrites(tmp_path):
    s = Studio(tmp_path)
    result = s.new('003-my-take', 'Football', 'Keep my opinion sharp.')
    assert result['episode'] == '003-my-take'
    assert 'Keep my opinion sharp.' in s.context('003-my-take')
    with pytest.raises(FileExistsError):
        s.new('003-my-take', 'Replacement', 'changed')
    assert 'changed' not in s.context('003-my-take')


@pytest.mark.parametrize('name', ['../escape', '/absolute', 'x/y', '', 'A B', 'a\\b', 'con'])
def test_episode_rejects_unsafe_names(tmp_path, name):
    with pytest.raises(ValueError):
        Studio(tmp_path).new(name, 'title', 'take')


def test_feedback_learn_and_revoke(tmp_path):
    s = Studio(tmp_path)
    s.new('sample', 'Title', 'My take')
    f = s.feedback('sample', 'Keep short punchy sentences', 'voice')
    assert 'Keep short punchy sentences' in s.context('sample')
    s.revoke(f['id'])
    assert 'Keep short punchy sentences' not in s.context('sample')
    with pytest.raises(ValueError):
        s.feedback('sample', '', 'voice')
    with pytest.raises(ValueError):
        s.feedback('sample', 'bad type', 'wrong')


def test_index_excludes_external_and_deleted_files(tmp_path):
    s = Studio(tmp_path)
    s.new('sample', 'Title', 'My unique football thesis')
    excluded = tmp_path / 'external' / 'other.md'
    excluded.parent.mkdir()
    excluded.write_text('secret football')
    assert s.index()['documents'] >= 1
    results = s.search('football')
    assert results and all('external' not in r['path'] for r in results)
    (tmp_path / 'episodes/sample/CREATOR_TAKE.md').unlink()
    s.index()
    assert not s.search('unique')
    assert s.search('" OR *') == []


def test_metrics_validate_and_preserve(tmp_path):
    s = Studio(tmp_path)
    s.new('sample', 'Title', 'Take')
    s.metrics('sample', impressions=1000, ctr=5, retention30=70, hours=8, cost=0)
    assert len(s.metric_records()) == 1
    with pytest.raises(ValueError):
        s.metrics('sample', impressions=-1, ctr=101, retention30=70, hours=8, cost=0)
    assert len(s.metric_records()) == 1


def test_queue_only_known_actions_and_retries(tmp_path):
    s = Studio(tmp_path)
    with pytest.raises(ValueError):
        s.enqueue('shell', {'command': 'anything'})
    j = s.enqueue('index', {})
    assert s.run_next()['status'] == 'success'
    assert s.jobs()[0]['id'] == j['id']
    assert s.jobs()[0]['state'] == 'completed'
    assert s.run_next()['status'] == 'idle'


def test_missing_episode_and_revoke(tmp_path):
    s = Studio(tmp_path)
    with pytest.raises(FileNotFoundError):
        s.context('missing')
    with pytest.raises(ValueError):
        s.revoke('unknown')


def test_dashboard_escapes_and_links_artifacts(tmp_path):
    s = Studio(tmp_path)
    s.new('sample', '<script>alert(1)</script>', '<b>Take</b>')
    out = s.dashboard()
    content = out.read_text(encoding='utf-8')
    assert '<script>alert(1)</script>' not in content
    assert '&lt;script&gt;' in content
    assert 'sample' in content
    assert 'CREATOR_TAKE.md' in content
