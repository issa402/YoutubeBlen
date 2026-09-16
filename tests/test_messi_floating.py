"""Floating opener motion and portable Mac handoff contracts."""
from pathlib import Path
import math
import os
import shutil
import subprocess
import tempfile
import unittest

from blender.floating_spec import pose_at

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / 'episodes/002-ronaldo-hate-psychology/mac/messi-floating'


class MessiFloatingTests(unittest.TestCase):
    def test_motion_is_deterministic_and_finite_throughout_sequence(self):
        for frame in range(1, 289):
            pose = pose_at(frame)
            self.assertEqual(pose, pose_at(frame))
            self.assertTrue({'height', 'cape_phase', 'camera_x', 'camera_scale'} <= pose.keys())
            self.assertTrue(all(math.isfinite(pose[key]) for key in
                                ('height', 'cape_phase', 'camera_x', 'camera_scale')))
            self.assertGreater(pose['camera_scale'], 0)

    def test_motion_rejects_frames_outside_the_sequence(self):
        for frame in (-1, 0, 289, 1000):
            with self.subTest(frame=frame), self.assertRaises(ValueError):
                pose_at(frame)

    def test_float_cape_and_camera_have_visible_motion(self):
        poses = [pose_at(frame) for frame in range(1, 289)]
        for key, minimum_span in (('height', 0.05), ('cape_phase', 0.5),
                                  ('camera_x', 0.05), ('camera_scale', 0.1)):
            values = [pose[key] for pose in poses]
            with self.subTest(channel=key):
                self.assertGreater(max(values) - min(values), minimum_span)

    def test_mac_packet_is_identical_to_canonical_sources(self):
        for filename in ('messi_floating.py', 'floating_spec.py', 'hd_spec.py'):
            with self.subTest(filename=filename):
                self.assertEqual((ROOT / 'blender' / filename).read_bytes(),
                                 (PACKET / filename).read_bytes())

    def test_launcher_returns_blender_failure_and_surfaces_traceback(self):
        bash = shutil.which('bash')
        if not bash and Path('C:/Program Files/Git/bin/bash.exe').exists():
            bash = 'C:/Program Files/Git/bin/bash.exe'
        if not bash:
            self.skipTest('Bash is unavailable on this test host')
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            launcher = directory / 'run.sh'
            launcher.write_bytes((PACKET / 'run.sh').read_bytes())
            executable = directory / 'fake-blender'
            executable.write_text('#!/bin/bash\nprintf "Traceback: test failure\\n" >&2\nexit 23\n',
                                  encoding='utf-8')
            executable.chmod(0o755)
            result = subprocess.run([bash, str(launcher), 'build'], capture_output=True,
                                    text=True, timeout=20,
                                    env={**os.environ, 'BLENDER_BIN': executable.as_posix()})
            self.assertEqual(result.returncode, 23, result.stdout + result.stderr)
            self.assertIn('Traceback: test failure', result.stderr)
            self.assertIn('Full log:', result.stderr)
            self.assertEqual(len(list(directory.glob('render-*.log'))), 1)

    def test_launcher_propagates_blender_python_errors_and_prints_log_tail(self):
        script = (PACKET / 'run.sh').read_text(encoding='utf-8')
        self.assertIn('--python-exit-code 1 --python', script)
        self.assertIn('tail -n 80 "$log"', script)
        self.assertIn('exit "$result"', script)
        self.assertIn('resume) render_args+=(--render --resume)', script)
        self.assertNotIn('\r', script)


if __name__ == '__main__':
    unittest.main()
