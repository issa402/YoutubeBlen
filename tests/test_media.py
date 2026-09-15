"""Media tests use synthetic fixtures and never download speech models."""
import tempfile
import unittest
import importlib.util
from pathlib import Path
from unittest.mock import patch

from studio import media


class MediaTests(unittest.TestCase):
    def test_missing_input_rejected_before_output_creation(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "output"
            with self.assertRaises(FileNotFoundError):
                media.prepare(Path(folder) / "missing.mp4", output)
            self.assertFalse(output.exists())

    def test_existing_artifact_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "source.mp4"
            source.write_bytes(b"placeholder")
            output = root / "output"
            output.mkdir()
            artifact = output / "proxy.mp4"
            artifact.write_bytes(b"keep")
            with self.assertRaises(FileExistsError):
                media.prepare(source, output)
            self.assertEqual(artifact.read_bytes(), b"keep")

    def test_subtitles_round_milliseconds_and_handle_hours(self):
        self.assertEqual(media._timestamp(3599.9999), "01:00:00,000")
        self.assertEqual(media._timestamp(1.25), "00:00:01,250")

    def test_transcript_serialization_without_model_download(self):
        from types import SimpleNamespace
        fake_segment = SimpleNamespace(start=0.125, end=2.0, text=" Hello creator.")
        fake_model = SimpleNamespace(transcribe=lambda *a, **k: (
            iter([fake_segment]), SimpleNamespace(language="en", duration=2.0)))
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "voice.wav"
            source.write_bytes(b"placeholder")
            with patch.object(media, "_speech_model", return_value=fake_model):
                result = media.transcribe(source, root / "out")
            self.assertEqual(result["language"], "en")
            self.assertIn("00:00:00,125 --> 00:00:02,000", (root / "out/transcript.srt").read_text())
            self.assertEqual((root / "out/transcript.txt").read_text(), "Hello creator.\n")


@unittest.skipUnless(importlib.util.find_spec("cv2") and importlib.util.find_spec("imageio_ffmpeg"),
                     "Install the studio media dependencies for synthetic integration tests")
class MediaIntegrationTests(unittest.TestCase):
    def test_actual_video_with_audio_and_silent_video(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            result = media.demo(root / "demo")
            self.assertTrue(result["has_audio"])
            self.assertAlmostEqual(result["duration_seconds"], 4, places=1)
            self.assertEqual(result["fps"], 24)
            for key in ("proxy", "audio", "contact_sheet", "analysis"):
                self.assertGreater(Path(result[key]).stat().st_size, 0)
            silent = root / "silent.mp4"
            media._run([media.ffmpeg(), "-nostdin", "-n", "-i", str(root / "demo/synthetic.mp4"),
                        "-c:v", "copy", "-an", str(silent)])
            silent_result = media.prepare(silent, root / "silent-prepared")
            self.assertFalse(silent_result["has_audio"])
            self.assertIsNone(silent_result["audio"])
            self.assertFalse((root / "silent-prepared/audio.wav").exists())


if __name__ == "__main__":
    unittest.main()
