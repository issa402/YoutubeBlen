"""Fit guide paragraphs to measured shot budgets without cutting speech."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess


def tempo_for(duration: float, target: float) -> float:
    if not all(math.isfinite(value) and value > 0 for value in (duration, target)):
        raise ValueError("Durations must be finite and positive")
    # Allow ~35ms for atempo's sample-window boundary variation.
    tempo = max(1.0, duration / (target - 0.035)) if target > 0.035 else math.inf
    if tempo > 1.2:
        raise ValueError("Narration would need more than 20% acceleration; extend the shot")
    return tempo


def fit(source: Path, output: Path, targets: list[float], ffmpeg: Path) -> dict:
    import numpy as np
    import soundfile as sf
    if __package__:
        from .neural_voice import timeline_rows
    else:
        from neural_voice import timeline_rows
    report = json.loads((source / "timeline.json").read_text(encoding="utf-8"))
    texts = [row["text"] for row in report["paragraphs"]]
    if len(targets) != len(texts):
        raise ValueError("Supply one target duration per paragraph")
    natural = [sf.read(source / f"paragraph-{index:02}.wav", dtype="float32")
               for index in range(1, len(texts) + 1)]
    sample_rate = report["sample_rate"]
    if any(rate != sample_rate or samples.ndim != 1 or not np.isfinite(samples).all()
           for samples, rate in natural):
        raise ValueError("Expected mono paragraphs at the recorded sample rate")
    tempos = [tempo_for(len(samples) / rate, target)
              for (samples, rate), target in zip(natural, targets, strict=True)]
    if output.exists():
        raise FileExistsError("Choose a fresh output directory")
    output.mkdir(parents=True)
    padded = []
    fit_rows = []
    for index, ((samples, rate), target, tempo) in enumerate(zip(natural, targets, tempos, strict=True), 1):
        if tempo > 1:
            command = [str(ffmpeg.resolve()), "-hide_banner", "-loglevel", "error", "-nostdin",
                       "-i", str((source / f"paragraph-{index:02}.wav").resolve()),
                       "-af", f"atempo={tempo:.9f}", "-f", "f32le", "-ac", "1", "-ar", str(rate), "pipe:1"]
            result = subprocess.run(command, check=True, capture_output=True)
            fitted = np.frombuffer(result.stdout, dtype="<f4")
        else:
            fitted = samples
        count = round(target * rate)
        if not len(fitted) or not np.isfinite(fitted).all():
            raise ValueError(f"Paragraph {index} has invalid audio")
        if len(fitted) > count:
            raise ValueError(f"Paragraph {index} exceeds budget; no speech was truncated")
        padded.append(np.pad(fitted, (0, count - len(fitted))))
        fit_rows.append({"paragraph": index, "natural_duration": len(samples) / rate,
                         "atempo": tempo, "spoken_duration": len(fitted) / rate,
                         "padding_seconds": (count - len(fitted)) / rate})
    combined = np.concatenate(padded)
    peak = float(np.max(np.abs(combined)))
    if not math.isfinite(peak) or peak < 1e-8:
        raise ValueError("Generated voice is silent or invalid")
    gain = (10 ** (-3 / 20)) / peak
    combined = combined * gain
    for index, samples in enumerate(padded, 1):
        sf.write(output / f"paragraph-{index:02}.wav", samples * gain, sample_rate, subtype="PCM_16")
    audio_path = output / "narration-guide.wav"
    sf.write(audio_path, combined, sample_rate, subtype="PCM_16")
    rms = float(np.sqrt(np.mean(combined.astype("float64") ** 2)))
    final = {**report, "duration_seconds": len(combined) / sample_rate,
             "audio_sha256": hashlib.sha256(audio_path.read_bytes()).hexdigest(),
             "paragraphs": timeline_rows(texts, list(map(len, padded)), sample_rate),
             "natural_duration_seconds": report["duration_seconds"], "fitting": fit_rows,
             "level": {"peak_dbfs": -3, "rms_dbfs": 20 * math.log10(rms),
                       "gain_db": 20 * math.log10(gain), "method": "global peak normalization"},
             "timing_method": "sample-based paragraph placement, mild pitch-preserving atempo, tail silence only"}
    (output / "timeline.json").write_text(json.dumps(final, indent=2), encoding="utf-8")
    (output / "narration.txt").write_text(report["source_text"], encoding="utf-8")
    return final


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--targets", type=float, nargs="+", required=True)
    parser.add_argument("--ffmpeg", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(fit(args.source, args.output, args.targets, args.ffmpeg), indent=2))
