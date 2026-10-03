import json
import tempfile
import unittest
import wave
from pathlib import Path

from studio.creator_media import plan_audio, validate_timeline, build_composition


class CreatorMediaTests(unittest.TestCase):
    def test_sample_clock_covers_audio_without_truncation(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with wave.open(str(root / 'voice.wav'), 'wb') as f:
                f.setparams((1, 2, 24000, 0, 'NONE', 'not compressed'))
                f.writeframes(b'\x00\x00' * 24001)
            plan = plan_audio(root / 'voice.wav', ['Look at the space.', 'Now follow the run.'])
            self.assertEqual(plan['frames'], 31)
            self.assertEqual(plan['shots'][-1]['end_frame'], 31)
            self.assertEqual(plan['shots'][1]['start_frame'], plan['shots'][0]['end_frame'])
            self.assertEqual(plan['timing_method'], 'estimated equal-duration beats; review against audio')

    def test_reject_gaps_and_nonfinite_timing(self):
        p = {'fps': 30, 'frames': 60, 'shots': [{'start_frame': 1, 'end_frame': 60, 'caption': 'x'}]}
        with self.assertRaises(ValueError):
            validate_timeline(p)
        p['fps'] = float('nan')
        with self.assertRaises(ValueError):
            validate_timeline(p)

    def test_html_escapes_script_and_refuses_existing_output(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            dep = root / 'integrations/creator/node_modules/gsap/dist'
            dep.mkdir(parents=True)
            (dep / 'gsap.min.js').write_text('// fixture')
            plan = {'fps': 30, 'frames': 60, 'shots': [{'start_frame': 0, 'end_frame': 60, 'caption': '</script><script>alert(1)</script>'}]}
            out = root / '.studio/proof'
            build_composition(root, plan, out)
            html = (out / 'index.html').read_text()
            self.assertNotIn('</script><script>alert(1)', html)
            self.assertIn('gsap.min.js', html)
            with self.assertRaises(FileExistsError):
                build_composition(root, plan, out)
            with self.assertRaises(ValueError):
                build_composition(root, plan, root / 'outside-state')


if __name__ == '__main__':
    unittest.main()
