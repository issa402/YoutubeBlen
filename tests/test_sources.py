"""Provenance tests; network intake is mocked and does not download media."""
import json
from unittest.mock import MagicMock
import pytest
from studio.core import Studio
from studio.sources import add_source, intake, url_checked


@pytest.mark.parametrize('url', ['http://example.com', 'https://a:b@example.com', 'file:///foo', 'invalid'])
def test_reject_unsafe_source_urls(url):
    with pytest.raises(ValueError):
        url_checked(url)


def test_source_provenance_is_preserved_not_auto_verified(tmp_path):
    studio = Studio(tmp_path)
    studio.new('sample', 'Title', 'Creator take')
    record = add_source(studio, 'sample', 'https://example.com/article', 'Original article',
                        author='Author', published='2020-02-29', event_date='2020-01-01',
                        quote='Original words', archive='Archive checked', notes='Discovery only')
    saved = json.loads((tmp_path / 'episodes/sample/research/sources.json').read_text())
    assert saved == [record]
    assert record['status'] == 'DISCOVERY' and record['quotation_verified'] is False
    assert record['quotation'] == 'Original words' and record['publication_date'] == '2020-02-29'
    with pytest.raises(ValueError, match='already recorded'):
        add_source(studio, 'sample', record['url'], 'Replacement')
    with pytest.raises(ValueError):
        add_source(studio, 'sample', 'https://example.com/other', 'Title', published='2020-02-30')
    with pytest.raises(ValueError):
        add_source(studio, 'sample', 'https://example.com/other', '')
    assert json.loads((tmp_path / 'episodes/sample/research/sources.json').read_text()) == saved


def test_intake_metadata_and_explicit_media_switch(tmp_path, monkeypatch):
    import yt_dlp
    downloader = MagicMock()
    session = downloader.return_value.__enter__.return_value
    session.extract_info.return_value = {'id': 'reference', 'title': 'Title'}
    session.sanitize_info.side_effect = lambda value: value
    monkeypatch.setattr(yt_dlp, 'YoutubeDL', downloader)
    result = intake('https://youtu.be/reference', tmp_path / 'metadata')
    assert result['id'] == 'reference'
    assert downloader.call_args.args[0]['skip_download'] is True
    provenance = json.loads((tmp_path / 'metadata/provenance.json').read_text())
    assert provenance['reuse_rights'] == 'UNKNOWN'
    assert provenance['media_download_requested'] is False
    intake('https://youtu.be/reference', tmp_path / 'download', download=True)
    assert downloader.call_args.args[0]['skip_download'] is False
    with pytest.raises(FileExistsError):
        intake('https://youtu.be/reference', tmp_path / 'metadata')
    with pytest.raises(ValueError):
        intake('https://example.com/video', tmp_path / 'unsupported')
    assert not (tmp_path / 'unsupported').exists()
