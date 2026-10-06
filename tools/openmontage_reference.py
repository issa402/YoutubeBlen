"""Run pinned OpenMontage local shot analysis on a reference video.

The upstream checkout stays ignored in .studio/repos. This adapter invokes its
SceneDetect and FrameSampler tools directly; no producer agent or API is run.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = ROOT / ".studio" / "repos" / "OpenMontage"
PIN = "9327439db69021ab4b0e2776729bf3b58fdb5a87"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ensure_upstream() -> None:
    if not (UPSTREAM / "tools" / "analysis" / "scene_detect.py").is_file():
        raise RuntimeError("OpenMontage missing. Run tools/fetch_studio_repos.ps1 first.")
    head = subprocess.run(
        ["git", "-C", str(UPSTREAM), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    if head != PIN:
        raise RuntimeError(f"OpenMontage checkout is {head}; expected pinned {PIN}.")


def ensure_ffmpeg() -> None:
    local_bin = ROOT / ".studio" / "bin"
    os.environ["PATH"] = str(local_bin) + os.pathsep + os.environ.get("PATH", "")
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise RuntimeError("FFmpeg and ffprobe are required on PATH or in .studio/bin.")


def analyze(source: Path, output: Path, max_frames: int, threshold: float) -> Path:
    source = source.resolve(strict=True)
    if not source.is_file():
        raise ValueError("Source must be a video file.")
    output = output.resolve()
    studio = (ROOT / ".studio").resolve()
    if not output.is_relative_to(studio):
        raise ValueError("Output must be inside ignored .studio/.")
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"Output already contains files: {output}")
    ensure_upstream()
    ensure_ffmpeg()
    sys.path.insert(0, str(UPSTREAM))
    from tools.analysis.frame_sampler import FrameSampler  # type: ignore[import-not-found]
    from tools.analysis.scene_detect import SceneDetect  # type: ignore[import-not-found]

    output.mkdir(parents=True, exist_ok=True)
    scenes_path = output / "scenes.json"
    detected = SceneDetect().execute({
        "input_path": str(source),
        "method": "content",
        "threshold": threshold,
        "min_scene_length_seconds": 0.35,
        "output_path": str(scenes_path),
    })
    if not detected.success:
        raise RuntimeError(f"OpenMontage scene detection failed: {detected.error}")
    scenes = detected.data["scenes"]
    sample_strategy = "scene_guided" if len(scenes) > 1 else "count"
    sampled = FrameSampler().execute({
        "input_path": str(source),
        "strategy": sample_strategy,
        "scene_boundaries": scenes,
        "count": max_frames,
        "max_frames": max_frames,
        "output_dir": str(output / "frames"),
        "format": "jpg",
    })
    if not sampled.success or not sampled.data["frames"]:
        raise RuntimeError(f"OpenMontage frame sampling failed: {sampled.error}")
    report = {
        "source": str(source),
        "source_sha256": sha256(source),
        "upstream": "https://github.com/calesthio/OpenMontage",
        "upstream_commit": PIN,
        "scene_method": detected.data["method"],
        "sample_strategy": sample_strategy,
        "scene_count": len(scenes),
        "scenes": scenes,
        "sample_count": len(sampled.data["frames"]),
        "samples": sampled.data["frames"],
        "editorial_status": "candidate cuts and frames; human visual review required",
    }
    report_path = output / "reference-report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Local reference video")
    parser.add_argument("--output", type=Path, required=True, help="New directory under .studio/")
    parser.add_argument("--max-frames", type=int, default=16)
    parser.add_argument("--threshold", type=float, default=0.3)
    args = parser.parse_args()
    if not 1 <= args.max_frames <= 60:
        parser.error("--max-frames must be 1..60")
    if not 0.01 <= args.threshold <= 0.99:
        parser.error("--threshold must be 0.01..0.99")
    try:
        print(analyze(args.source, args.output, args.max_frames, args.threshold))
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"OpenMontage analysis failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
