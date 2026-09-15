"""Offline Kokoro voice: exact text, immutable outputs and sample-based timing."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import time


def paragraphs(text: str) -> list[str]:
    result = [part.strip() for part in re.split(r"\n\s*\n", text.replace("\r\n", "\n")) if part.strip()]
    if not result:
        raise ValueError("Narration is empty")
    return result


def validate_options(speed: float, threads: int) -> None:
    if not math.isfinite(speed) or not 0.8 <= speed <= 1.2:
        raise ValueError("Use a natural speech speed between 0.8 and 1.2")
    if not 1 <= threads <= 16:
        raise ValueError("CPU threads must be between 1 and 16")


def timeline_rows(texts: list[str], lengths: list[int], sample_rate: int) -> list[dict]:
    if len(texts) != len(lengths) or sample_rate <= 0 or any(n <= 0 for n in lengths):
        raise ValueError("Paragraph lengths and sample rate must be valid")
    rows, position = [], 0
    for index, (text, length) in enumerate(zip(texts, lengths, strict=True), 1):
        rows.append({"paragraph": index, "text": text, "wav": f"paragraph-{index:02}.wav",
                     "start_seconds": position / sample_rate,
                     "end_seconds": (position + length) / sample_rate,
                     "duration_seconds": length / sample_rate,
                     "samples": length})
        position += length
    return rows


def synthesize(source: Path, output: Path, models: Path, voice: str = "am_michael",
               speed: float = 1.0, threads: int = 4) -> dict:
    validate_options(speed, threads)
    # Bind provenance to the same immutable bytes used for speech, even if an
    # editor saves a new script while the model is generating this take.
    source_bytes = source.read_bytes()
    text = source_bytes.decode("utf-8-sig")
    texts = paragraphs(text)
    if output.exists():
        raise FileExistsError("Choose a fresh output directory")
    # Lazy imports keep validation and tests free of model/runtime downloads.
    import numpy as np
    import onnxruntime as ort
    import soundfile as sf
    from kokoro_onnx import Kokoro
    if __package__:
        from .neural_voice_setup import ASSETS, file_hash, verify_file
    else:
        from neural_voice_setup import ASSETS, file_hash, verify_file

    for name, digest in ASSETS.items():
        verify_file(models / name, digest)
    options = ort.SessionOptions()
    options.intra_op_num_threads = threads
    options.inter_op_num_threads = 1
    session = ort.InferenceSession(str(models / "kokoro-v1.0.onnx"), sess_options=options,
                                   providers=["CPUExecutionProvider"])
    engine = Kokoro.from_session(session, str(models / "voices-v1.0.bin"))
    output.mkdir(parents=True)
    chunks = []
    started = time.monotonic()
    sample_rate = 24000
    for index, passage in enumerate(texts, 1):
        samples, rate = engine.create(passage, voice=voice, speed=speed, lang="en-us")
        if rate != sample_rate or not len(samples) or not np.isfinite(samples).all():
            raise ValueError("Voice engine returned invalid audio")
        chunks.append(samples)
        sf.write(output / f"paragraph-{index:02}.wav", samples, rate, subtype="PCM_16")
        print(f"Paragraph {index}: {len(samples) / rate:.3f}s", flush=True)
    sf.write(output / "narration-guide.wav", np.concatenate(chunks), sample_rate, subtype="PCM_16")
    report = {"engine": "kokoro-onnx", "voice": voice, "speed": speed,
              "language": "en-us", "sample_rate": sample_rate, "cpu_threads": threads,
              "source_sha256": hashlib.sha256(source_bytes).hexdigest(),
              "source_text": text, "source": source.as_posix(),
              "word_count": len(text.split()), "duration_seconds": sum(map(len, chunks)) / sample_rate,
              "generation_seconds": time.monotonic() - started,
              "audio_sha256": file_hash(output / "narration-guide.wav"),
              "paragraphs": timeline_rows(texts, list(map(len, chunks)), sample_rate),
              "synthetic_guide": True, "timing_method": "measured WAV sample counts"}
    (output / "timeline.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (output / "narration.txt").write_text(text, encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--models", type=Path, default=Path(".studio/models/voice"))
    parser.add_argument("--voice", default="am_michael")
    parser.add_argument("--speed", type=float, default=1.0)
    parser.add_argument("--threads", type=int, default=4)
    args = parser.parse_args()
    print(json.dumps(synthesize(args.source, args.output, args.models, args.voice,
                                args.speed, args.threads), indent=2))
