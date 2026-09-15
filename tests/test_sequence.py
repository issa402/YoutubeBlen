"""Contract tests for the portable multi-shot Blender sequence."""
import json
from pathlib import Path
import tempfile
import unittest

from blender.sequence_spec import load_manifest, shot_at, safe_output


class SequenceContractTests(unittest.TestCase):
    def test_shots_cover_full_sequence_with_hard_cuts(self):
        self.assertEqual([shot_at(f) for f in (1, 356, 357, 571, 572, 720)],
                         ['notification', 'notification', 'status', 'status', 'rivalry', 'rivalry'])
        for invalid in (0, 721, True, 1.2):
            with self.assertRaises(ValueError):
                shot_at(invalid)

    def test_manifest_is_validated_before_blender_runs(self):
        base = {'schema_version': 1, 'fps': 24, 'frame_start': 1, 'frame_end': 720,
                'resolution': [1920, 1080], 'preview_resolution': [640, 360], 'output': 'frames'}
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'manifest.json'
            path.write_text(json.dumps(base))
            self.assertEqual(load_manifest(path), base)
            for key, value in [('fps', True), ('frame_end', 719), ('resolution', [0, 1080]),
                               ('output', '../escape'), ('schema_version', 2)]:
                path.write_text(json.dumps(base | {key: value}))
                with self.assertRaises(ValueError):
                    load_manifest(path)

    def test_output_paths_are_portable_and_contained(self):
        root = Path(tempfile.gettempdir()).resolve()
        for bad in ('../escape', '/abs', 'C:\\escape', '.', 'x/../../escape'):
            with self.assertRaises(ValueError):
                safe_output(root, bad)
        self.assertEqual(safe_output(root, 'frames'), root / 'frames')


if __name__ == '__main__':
    unittest.main()
