"""Portable HD packet and resumable render integrity contracts."""
import json
from pathlib import Path
import struct
import tempfile
import unittest
import zlib

from blender.hd_spec import render_fingerprint, validate_png, remaining_frames, select_eevee_engine


def tiny_png(path, width=2, height=2):
    def chunk(kind, data):
        return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data))
    path.write_bytes(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>2I5B', width, height, 8, 2, 0, 0, 0))
                     + chunk(b'IDAT', zlib.compress((b'\0' + bytes(width * 3)) * height)) + chunk(b'IEND', b''))


class HdPacketTests(unittest.TestCase):
    def test_eevee_engine_selection_supports_blender_45_and_52(self):
        self.assertEqual(select_eevee_engine({'BLENDER_EEVEE_NEXT', 'CYCLES'}), 'BLENDER_EEVEE_NEXT')
        self.assertEqual(select_eevee_engine({'BLENDER_EEVEE', 'CYCLES'}), 'BLENDER_EEVEE')
        with self.assertRaises(ValueError):
            select_eevee_engine({'BLENDER_WORKBENCH', 'CYCLES'})

    def test_mac_packet_sources_match_canonical_code_and_1080p_contract(self):
        root = Path(__file__).resolve().parents[1]
        packet = root / 'episodes/002-ronaldo-hate-psychology/mac/opening-hd'
        for filename in ('opening_hd.py', 'hd_spec.py', 'sequence_spec.py'):
            self.assertEqual((root / 'blender' / filename).read_bytes(), (packet / filename).read_bytes())
        manifest = json.loads((packet / 'manifest.json').read_text(encoding='utf-8'))
        self.assertEqual(manifest['resolution'], [1920, 1080])
        self.assertEqual((manifest['frame_end'], manifest['fps']), (720, 24))
        self.assertIn('--python-exit-code 1 --python', (packet / 'run.sh').read_text())

    def test_png_checks_dimensions_crc_and_decodable_payload(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'frame_0001.png'
            tiny_png(path)
            self.assertEqual(validate_png(path, [2, 2]), [2, 2])
            with self.assertRaises(ValueError):
                validate_png(path, [1920, 1080])
            data = path.read_bytes()
            path.write_bytes(data[:-5])
            with self.assertRaises(ValueError):
                validate_png(path, [2, 2])

    def test_resume_requires_identical_scene_and_completed_valid_frames(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            frames = root / 'frames'
            frames.mkdir()
            tiny_png(frames / 'frame_0001.png')
            ledger = root / 'render-state.json'
            with self.assertRaises(FileExistsError):
                remaining_frames(frames, ledger, 'abc', [2, 2], False, end=3)
            ledger.write_text(json.dumps({'fingerprint': 'abc', 'completed': [1]}))
            self.assertEqual(remaining_frames(frames, ledger, 'abc', [2, 2], True, end=3), [2, 3])
            with self.assertRaises(ValueError):
                remaining_frames(frames, ledger, 'other', [2, 2], True, end=3)
            tiny_png(frames / 'frame_0002.png')
            with self.assertRaises(ValueError):
                remaining_frames(frames, ledger, 'abc', [2, 2], True, end=3)

    def test_fingerprint_changes_when_source_or_dimensions_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'scene.py'
            source.write_text('one')
            first = render_fingerprint([source], {'resolution': [1920, 1080]})
            self.assertEqual(first, render_fingerprint([source], {'resolution': [1920, 1080]}))
            source.write_text('two')
            self.assertNotEqual(first, render_fingerprint([source], {'resolution': [1920, 1080]}))


if __name__ == '__main__':
    unittest.main()
