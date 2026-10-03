"""HTTP and media boundary checks for the loopback Creator Desk."""
import http.client
import json
from pathlib import Path
import tempfile
import threading
import unittest

from studio.core import Studio
from studio.creator_server import CreatorServer, byte_range, media_path


class CreatorServerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        Studio(self.root).new('episode-one', 'One', 'A creator take')
        media = self.root / '.studio/creator-demo/final.mp4'
        media.parent.mkdir(parents=True)
        media.write_bytes(b'1234567890')
        self.server = CreatorServer(self.root, 0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)

    def call(self, method, path, body=None, headers=None):
        connection = http.client.HTTPConnection('127.0.0.1', self.server.server_port)
        header = {'Host': f'127.0.0.1:{self.server.server_port}', **(headers or {})}
        connection.request(method, path, body, headers=header)
        response = connection.getresponse()
        result = response.status, dict(response.getheaders()), response.read()
        connection.close()
        return result

    def test_loopback_state_and_mutation_token(self):
        status, _, content = self.call('GET', '/api/state')
        self.assertEqual(status, 200)
        state = json.loads(content)
        self.assertEqual(state['episodes'][0]['episode'], 'episode-one')
        body = json.dumps({'episode': 'episode-one', 'brief': 'Make a sourced short.'})
        headers = {'Content-Type': 'application/json'}
        self.assertEqual(self.call('POST', '/api/project', body, headers)[0], 403)
        headers['X-Creator-Token'] = state['csrf_token']
        self.assertEqual(self.call('POST', '/api/project', body, headers)[0], 200)
        self.assertEqual(len(json.loads(self.call('GET', '/api/state')[2])['projects']), 1)
        self.assertEqual(self.call('GET', '/', headers={'Origin': 'http://evil.example'})[0], 403)

    def test_media_range_and_private_path_denial(self):
        status, headers, content = self.call('GET', '/media?path=.studio%2Fcreator-demo%2Ffinal.mp4', headers={'Range': 'bytes=2-5'})
        self.assertEqual((status, content), (206, b'3456'))
        self.assertEqual(headers['Content-Range'], 'bytes 2-5/10')
        self.assertEqual(self.call('GET', '/media?path=..%2F.env')[0], 404)
        self.assertEqual(self.call('GET', '/media?path=.studio%2Fcreator-demo%2Ffinal.mp4', headers={'Range': 'bytes=20-30'})[0], 416)

    def test_path_and_range_helpers(self):
        self.assertEqual(byte_range('bytes=-3', 10), (7, 9, True))
        with self.assertRaises(ValueError):
            media_path(self.root, '../outside.mp4')
        with self.assertRaises(FileNotFoundError):
            media_path(self.root, '.studio/creator-demo/secrets.txt')


if __name__ == '__main__':
    unittest.main()
