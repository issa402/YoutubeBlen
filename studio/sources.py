"""Source provenance and explicit YouTube intake, separate from claim approval."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse
from .core import write_json


def url_checked(url):
    parsed = urlparse(url)
    if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError('Provide an HTTPS source URL without embedded credentials.')
    return parsed


def add_source(studio, episode, url, title, author='', published='', event_date='', quote='', archive='', notes=''):
    url_checked(url)
    if not title.strip():
        raise ValueError('Source title is required.')
    path = studio.require_episode(episode) / 'research/sources.json'
    for value in (published, event_date):
        if value:
            datetime.strptime(value, '%Y-%m-%d')
    records = json.loads(path.read_text(encoding='utf-8-sig')) if path.exists() else []
    source_id = 'S-' + hashlib.sha256(url.encode()).hexdigest()[:12]
    if any(r['id'] == source_id for r in records):
        raise ValueError('Source URL already recorded; edit its record explicitly to revise it.')
    record = dict(id=source_id, url=url, title=title, author=author, publication_date=published,
                  event_date=event_date, quotation=quote, archive_notes=archive, notes=notes,
                  retrieved_at=datetime.now(timezone.utc).isoformat(), status='DISCOVERY',
                  quotation_verified=False, reuse_rights='UNKNOWN')
    write_json(path, records + [record])
    return record


def intake(url, output_dir, download=False):
    parsed = url_checked(url)
    if parsed.hostname not in ('youtube.com', 'www.youtube.com', 'm.youtube.com', 'youtu.be'):
        raise ValueError('Automatic intake currently supports YouTube only; use source for other URLs.')
    destination = Path(output_dir).resolve()
    destination.mkdir(parents=True, exist_ok=False)
    import yt_dlp
    from .media import ffmpeg
    options = dict(skip_download=not download, noplaylist=True, quiet=True, retries=2,
                   socket_timeout=30, ffmpeg_location=str(Path(ffmpeg()).parent),
                   outtmpl=str(destination / '%(id)s.%(ext)s'),
                   writeinfojson=True, writesubtitles=True, writeautomaticsub=True,
                   subtitleslangs=['en'], format='best[height<=720]/best')
    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=True)
        clean = ydl.sanitize_info(info)
    write_json(destination / 'metadata.json', clean)
    write_json(destination / 'provenance.json', {
        'source_url': url, 'retrieved_at': datetime.now(timezone.utc).isoformat(),
        'media_download_requested': download, 'reuse_rights': 'UNKNOWN', 'status': 'DISCOVERY',
    })
    return {'directory': str(destination), 'title': clean.get('title'), 'id': clean.get('id')}
