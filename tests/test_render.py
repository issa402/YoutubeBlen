import json
import importlib.util
import tempfile
import unittest
from pathlib import Path
from types import ModuleType
from unittest.mock import patch

from studio.render import create_package


class RenderPackageTests(unittest.TestCase):
    def test_portable_package_in_path_with_spaces(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / 'render package'
            result = create_package(output, seconds=8)
            manifest = json.loads((output / 'manifest.json').read_text())
            self.assertEqual(manifest['frame_end'], 192)
            self.assertEqual(manifest['fps'], 24)
            self.assertEqual(manifest['output'], 'frames')
            self.assertTrue((output / 'studio_scene.py').is_file())
            self.assertIn('--preview', (output / 'README.md').read_text())
            self.assertEqual(Path(result['package']), output.resolve())

    def test_invalid_duration_leaves_no_output(self):
        with tempfile.TemporaryDirectory() as temp:
            for duration in (0, -1, 121, 2.5, True, '8'):
                output = Path(temp) / 'invalid'
                with self.assertRaises(ValueError):
                    create_package(output, duration)
                self.assertFalse(output.exists())

    def test_collision_preserves_existing_content(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / 'existing'
            output.mkdir()
            existing = output / 'manifest.json'
            existing.write_text('keep')
            with self.assertRaises(FileExistsError):
                create_package(output)
            self.assertEqual(existing.read_text(), 'keep')

    def test_scene_rejects_nonportable_and_escaping_paths(self):
        fake_math = ModuleType('mathutils')
        fake_math.Vector = object
        source = Path(__file__).resolve().parents[1] / 'blender' / 'studio_scene.py'
        spec = importlib.util.spec_from_file_location('scene_validation_test', source)
        module = importlib.util.module_from_spec(spec)
        with patch.dict('sys.modules', {'bpy': ModuleType('bpy'), 'mathutils': fake_math}):
            spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            for invalid in ('../escape', '/tmp/outside', 'C:\\outside', '.', 'x/../../escape'):
                with self.assertRaises(ValueError):
                    module.safe_output(root, invalid)
            self.assertEqual(module.safe_output(root, 'frames'), root / 'frames')
            create_package(root / 'valid')
            manifest_path = root / 'valid' / 'manifest.json'
            manifest = module.load_manifest(manifest_path)
            manifest['fps'] = True
            manifest_path.write_text(json.dumps(manifest))
            with self.assertRaises(ValueError):
                module.load_manifest(manifest_path)


if __name__ == '__main__':
    unittest.main()
