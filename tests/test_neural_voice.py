from pathlib import Path

import pytest

from tools.neural_voice import paragraphs, timeline_rows, validate_options
from tools.neural_voice_setup import verify_file
from tools.neural_voice_fit import tempo_for


def test_exact_paragraphs_are_preserved():
    assert paragraphs(" A.\r\nStill A.\r\n\r\nB.\n") == ["A.\nStill A.", "B."]


def test_empty_script_rejected():
    with pytest.raises(ValueError, match="empty"):
        paragraphs(" \n\n")


def test_timing_uses_samples_without_rounding_drift():
    rows = timeline_rows(["a", "b"], [24001, 48002], 24000)
    assert rows[1]["start_seconds"] == 24001 / 24000
    assert rows[1]["end_seconds"] == 72003 / 24000
    assert rows[1]["wav"] == "paragraph-02.wav"


@pytest.mark.parametrize("speed,threads", [(0.1, 2), (2, 2), (1, 0), (1, 17)])
def test_bad_options_rejected(speed, threads):
    with pytest.raises(ValueError):
        validate_options(speed, threads)


def test_bad_checksum_rejected(tmp_path: Path):
    sample = tmp_path / "model"
    sample.write_bytes(b"bad")
    with pytest.raises(ValueError, match="checksum"):
        verify_file(sample, "0" * 64)


def test_tempo_allows_tail_silence_and_never_cuts_speech():
    assert tempo_for(3, 4) == 1
    assert 1 < tempo_for(4.67, 3.9645) < 1.2
    with pytest.raises(ValueError, match="extend"):
        tempo_for(6, 4)


@pytest.mark.parametrize("duration,target", [(0, 4), (4, -1), (float("nan"), 4)])
def test_invalid_fit_durations(duration, target):
    with pytest.raises(ValueError):
        tempo_for(duration, target)


def test_real_ffmpeg_fit_keeps_all_samples_and_refuses_overwrite(tmp_path):
    import json
    import subprocess
    import wave
    import numpy as np
    import imageio_ffmpeg

    root = Path(__file__).resolve().parents[1]
    python = root / ".studio/envs/voice/Scripts/python.exe"
    if not python.is_file():
        pytest.skip("Optional isolated neural voice runtime is not installed")

    source = tmp_path / "natural"
    source.mkdir()
    rate = 24000
    samples = 0.15 * np.sin(2 * np.pi * 200 * np.arange(rate * 2) / rate)
    with wave.open(str(source / "paragraph-01.wav"), "wb") as stream:
        stream.setparams((1, 2, rate, 0, "NONE", "not compressed"))
        stream.writeframes((samples * 32767).astype("<i2").tobytes())
    (source / "timeline.json").write_text(json.dumps({
        "source_text": "A test sentence.", "sample_rate": rate, "duration_seconds": 2,
        "paragraphs": [{"text": "A test sentence."}]}), encoding="utf-8")
    output = tmp_path / "fitted"
    command = [str(python), str(root / "tools/neural_voice_fit.py"), str(source),
               "--output", str(output), "--targets", "1.85", "--ffmpeg", imageio_ffmpeg.get_ffmpeg_exe()]
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    report = json.loads(result.stdout)
    with wave.open(str(output / "narration-guide.wav"), "rb") as stream:
        actual_rate = stream.getframerate()
        actual = np.frombuffer(stream.readframes(stream.getnframes()), dtype="<i2") / 32768
    assert len(actual) == round(rate * 1.85)
    assert actual_rate == rate
    assert max(abs(actual)) < 0.7081
    assert report["fitting"][0]["padding_seconds"] >= 0
    assert report["paragraphs"][0]["end_seconds"] == 1.85
    rerun = subprocess.run(command, capture_output=True, text=True)
    assert rerun.returncode != 0
    assert "fresh output" in rerun.stderr


def test_synthesis_hash_tracks_spoken_snapshot_when_source_changes(tmp_path, monkeypatch):
    """An editor save during synthesis must not relabel old audio as new text."""
    import hashlib
    import json
    import sys
    from types import SimpleNamespace
    import numpy as np
    from tools.neural_voice import synthesize
    from tools import neural_voice_setup

    source = tmp_path / "script.txt"
    original = b"\xef\xbb\xbfOriginal first paragraph.\r\n\r\nOriginal second paragraph.\r\n"
    source.write_bytes(original)
    spoken = []

    def create(passage, **kwargs):
        spoken.append(passage)
        source.write_text("A changed script saved during generation.", encoding="utf-8")
        return np.ones(2400, dtype="float32") * 0.1, 24000

    class Options:
        pass

    monkeypatch.setitem(sys.modules, "onnxruntime", SimpleNamespace(
        SessionOptions=Options, InferenceSession=lambda *args, **kwargs: object()))
    monkeypatch.setitem(sys.modules, "kokoro_onnx", SimpleNamespace(Kokoro=SimpleNamespace(
        from_session=lambda *args: SimpleNamespace(create=create))))
    monkeypatch.setitem(sys.modules, "soundfile", SimpleNamespace(
        write=lambda path, samples, rate, **kwargs: Path(path).write_bytes(samples.tobytes())))
    monkeypatch.setattr(neural_voice_setup, "ASSETS", {})
    output = tmp_path / "take"
    report = synthesize(source, output, tmp_path / "models")
    assert spoken == ["Original first paragraph.", "Original second paragraph."]
    assert report["source_sha256"] == hashlib.sha256(original).hexdigest()
    assert report["source_sha256"] != hashlib.sha256(source.read_bytes()).hexdigest()
    assert report["source_text"] == original.decode("utf-8-sig")
    assert json.loads((output / "timeline.json").read_text())["source_sha256"] == report["source_sha256"]
