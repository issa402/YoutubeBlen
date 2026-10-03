"""Loopback-only Creator Desk. No shell commands or paid calls are exposed."""
from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import mimetypes
from pathlib import Path
import re
import secrets
import threading
from urllib.parse import parse_qs, urlsplit

WEB_ROOT = Path(__file__).with_name('creator_web')
MEDIA_ROOTS = ('.studio/renders', '.studio/audio', '.studio/shorts',
               '.studio/creator', '.studio/creator-demo', 'tools/animation-references')
MEDIA_TYPES = {'.mp4', '.webm', '.wav', '.mp3', '.m4a', '.ogg', '.png', '.jpg', '.jpeg', '.vtt'}


def media_path(root, relative):
    """Resolve a media path without exposing project documents or credentials."""
    if not isinstance(relative, str) or not relative or '\\' in relative or ':' in relative:
        raise ValueError('Invalid media path.')
    candidate = Path(relative)
    if candidate.is_absolute() or '..' in candidate.parts:
        raise ValueError('Invalid media path.')
    root = Path(root).resolve()
    resolved = (root / candidate).resolve()
    allowed = any(resolved.is_relative_to(root / folder) for folder in MEDIA_ROOTS)
    if not allowed or resolved.suffix.lower() not in MEDIA_TYPES or not resolved.is_file():
        raise FileNotFoundError('Media is unavailable.')
    return resolved


def byte_range(header, length):
    if not header:
        return 0, length - 1, False
    match = re.fullmatch(r'bytes=(\d*)-(\d*)', header)
    if not match or not any(match.groups()) or length <= 0:
        raise ValueError('Unsupported range.')
    first, last = match.groups()
    start = int(first) if first else max(0, length - int(last))
    end = min(int(last), length - 1) if first and last else length - 1
    if start >= length or end < start:
        raise ValueError('Range outside file.')
    return start, end, True


def presentation_state(root, kernel):
    state = kernel.dashboard_snapshot()
    state['memories'] = kernel.get_memory()[:20]
    from .core import Studio
    from .dashboard_data import episode_records
    state['episodes'] = episode_records(Studio(root))
    artifacts = []
    for folder in MEDIA_ROOTS[:5]:
        directory = Path(root) / folder
        if not directory.is_dir():
            continue
        for path in directory.rglob('*'):
            if path.suffix.lower() not in {'.mp4', '.webm', '.wav', '.mp3', '.ogg'}:
                continue
            relative = path.relative_to(root).as_posix()
            try:
                valid = media_path(root, relative)
            except (ValueError, FileNotFoundError):
                continue
            artifacts.append({'name': path.name, 'path': relative, 'size': valid.stat().st_size,
                              'modified': valid.stat().st_mtime,
                              'type': 'video' if path.suffix in {'.mp4', '.webm'} else 'audio'})
    state['artifacts'] = sorted(artifacts, key=lambda item: item['modified'], reverse=True)[:24]
    catalog = Path(root) / 'tools/animation-references/catalog.json'
    if catalog.is_file():
        state['references'] = json.loads(catalog.read_text(encoding='utf-8-sig')).get('references', [])
    if 'integrations' not in state:
        state['integrations'] = [{'name': name, 'status': 'source present' if (Path(root) / '.studio/repos' / folder).is_dir() else 'not installed'}
                                 for name, folder in [('HyperFrames', 'hyperframes'), ('Hermes', 'hermes-agent'),
                                                      ('ViMax', 'ViMax'), ('Headroom', 'headroom')]]
    return state


class CreatorServer(ThreadingHTTPServer):
    daemon_threads = True
    request_queue_size = 16

    def __init__(self, root, port=8766, kernel=None):
        self.root = Path(root).resolve()
        if kernel is None:
            from .creator_kernel import CreatorKernel
            kernel = CreatorKernel(self.root)
        self.kernel = kernel
        self.token = secrets.token_urlsafe(32)
        self.mutation_lock = threading.Lock()
        self.connection_slots = threading.BoundedSemaphore(32)
        super().__init__(('127.0.0.1', port), CreatorHandler)
        self.server_port = self.server_address[1]

    def process_request(self, request, client_address):
        if not self.connection_slots.acquire(blocking=False):
            request.close()
            return
        try:
            super().process_request(request, client_address)
        except BaseException:
            self.connection_slots.release()
            raise

    def process_request_thread(self, request, client_address):
        try:
            super().process_request_thread(request, client_address)
        finally:
            self.connection_slots.release()


class CreatorHandler(BaseHTTPRequestHandler):
    server_version = 'CreatorDesk/1.0'

    def setup(self):
        super().setup()
        self.connection.settimeout(15)

    def log_message(self, format, *args):
        pass

    def _trusted_request(self):
        port = self.server.server_port
        hosts = {f'127.0.0.1:{port}', f'localhost:{port}'}
        host = self.headers.get('Host', '')
        origin = self.headers.get('Origin')
        return (host in hosts and (origin is None or origin == f'http://{host}')
                and self.headers.get('Sec-Fetch-Site', '') not in ('cross-site',))

    def end_headers(self):
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; media-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
        super().end_headers()

    def _json(self, status, data):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if not self._trusted_request():
            return self._json(403, {'error': 'Only same-origin loopback requests are accepted.'})
        request = urlsplit(self.path)
        try:
            if request.path == '/api/state':
                with self.server.mutation_lock:
                    state = presentation_state(self.server.root, self.server.kernel)
                return self._json(200, state | {'csrf_token': self.server.token})
            if request.path == '/media':
                relative = parse_qs(request.query).get('path', [''])[0]
                return self._file(media_path(self.server.root, relative))
            static = {'/': 'index.html', '/app.js': 'app.js', '/style.css': 'style.css'}
            if request.path in static:
                return self._file(WEB_ROOT / static[request.path])
            return self._json(404, {'error': 'Not found.'})
        except (ValueError, FileNotFoundError) as exc:
            return self._json(404, {'error': str(exc)})
        except Exception:
            return self._json(500, {'error': 'Could not load the desk. Check local project state.'})

    def _file(self, path):
        length = path.stat().st_size
        try:
            start, end, partial = byte_range(self.headers.get('Range'), length)
        except ValueError:
            self.send_response(416)
            self.send_header('Content-Range', f'bytes */{length}')
            self.send_header('Content-Length', '0')
            self.end_headers()
            return
        self.send_response(206 if partial else 200)
        self.send_header('Content-Type', mimetypes.guess_type(path.name)[0] or 'application/octet-stream')
        self.send_header('Content-Length', str(max(0, end - start + 1)))
        self.send_header('Accept-Ranges', 'bytes')
        if partial:
            self.send_header('Content-Range', f'bytes {start}-{end}/{length}')
        self.end_headers()
        try:
            with path.open('rb') as stream:
                stream.seek(start)
                remaining = end - start + 1
                while remaining > 0:
                    block = stream.read(min(256 * 1024, remaining))
                    if not block:
                        break
                    self.wfile.write(block)
                    remaining -= len(block)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def do_POST(self):
        if not self._trusted_request() or not secrets.compare_digest(self.headers.get('X-Creator-Token', ''), self.server.token):
            return self._json(403, {'error': 'Refresh the desk before submitting a local action.'})
        if self.headers.get('Content-Type', '').split(';')[0] != 'application/json':
            return self._json(415, {'error': 'JSON is required.'})
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if length < 1 or length > 65536:
                return self._json(413, {'error': 'Request must be between 1 and 65536 bytes.'})
            body = json.loads(self.rfile.read(length))
            if not isinstance(body, dict):
                raise ValueError('JSON object required.')
            with self.server.mutation_lock:
                result = self._action(urlsplit(self.path).path, body)
            return self._json(200, {'result': result})
        except (ValueError, TypeError, KeyError, FileNotFoundError, RuntimeError) as exc:
            return self._json(400, {'error': str(exc)})
        except Exception:
            return self._json(500, {'error': 'Action failed. No external job was launched.'})

    def _action(self, route, data):
        kernel = self.server.kernel
        if route == '/api/project':
            return kernel.create_project(data['episode'], data['brief'], data.get('reference_ids', []))
        if route == '/api/handoff':
            return kernel.prepare_handoff(data['project_id'], data['stage'])
        if route == '/api/complete':
            return kernel.complete_stage(data['project_id'], data['stage'], data['artifact'])
        if route == '/api/memory':
            return kernel.add_memory(data['episode'], data['raw'], data['approved'], data.get('rejected', ''), data['reason'])
        if route == '/api/retry':
            return kernel.retry_stage(data['project_id'], data['stage'])
        if route == '/api/fail':
            return kernel.fail_stage(data['project_id'], data['stage'], data['error'])
        raise ValueError('Unknown action.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--port', type=int, default=8766)
    args = parser.parse_args()
    server = CreatorServer(args.root, args.port)
    print(f'Creator Desk: http://127.0.0.1:{server.server_port}', flush=True)
    print('Local preparation and review. No model calls or background agents are started.', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
