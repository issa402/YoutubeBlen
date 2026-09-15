"""Local media preparation, scene sampling and CPU speech transcription.

Heavy libraries are imported on demand. Commands never use a shell or overwrite
an existing artifact. Outputs from failed runs remain available for diagnosis;
choose a fresh output directory to retry.
"""
import json
import math
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def ffmpeg() -> str:
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def _run(args: list[str], timeout: int = 1800) -> subprocess.CompletedProcess:
    result = subprocess.run(args, capture_output=True, text=True,
                            encoding="utf-8", errors="replace", timeout=timeout,
                            shell=False)
    if result.returncode:
        raise RuntimeError(f"Media command failed ({result.returncode}): {result.stderr[-4000:]}")
    return result


def _target(input_path: Path, output_dir: Path, names: tuple[str, ...]) -> tuple[Path, Path]:
    source, output = Path(input_path).resolve(), Path(output_dir).resolve()
    if not source.is_file():
        raise FileNotFoundError(f"Media input not found: {source}")
    for name in names:
        if (output / name).exists():
            raise FileExistsError(f"Artifact exists; choose a fresh output directory: {output / name}")
    output.mkdir(parents=True, exist_ok=True)
    return source, output


def _write_json(path: Path, value: dict) -> None:
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, ensure_ascii=False)


def _inspect_video(source: Path) -> dict:
    import cv2
    capture = cv2.VideoCapture(str(source))
    try:
        fps = capture.get(cv2.CAP_PROP_FPS)
        count = capture.get(cv2.CAP_PROP_FRAME_COUNT)
        if not capture.isOpened() or not math.isfinite(fps) or fps <= 0 or count <= 0:
            raise ValueError(f"No readable video stream: {source}")
        duration = count / fps
        # Sample two frames per second to bound analysis cost for long episodes.
        interval = max(1, round(fps / 2))
        previous = None
        scenes = [0.0]
        for index in range(0, int(count), interval):
            capture.set(cv2.CAP_PROP_POS_FRAMES, index)
            success, frame = capture.read()
            if not success:
                break
            thumbnail = cv2.resize(frame, (160, 90))
            hsv = cv2.cvtColor(thumbnail, cv2.COLOR_BGR2HSV)
            hist = cv2.calcHist([hsv], [0, 1], None, [32, 32], [0, 180, 0, 256])
            cv2.normalize(hist, hist)
            if previous is not None and cv2.compareHist(previous, hist, cv2.HISTCMP_BHATTACHARYYA) > 0.65:
                scenes.append(round(index / fps, 3))
            previous = hist
        return {"duration_seconds": round(duration, 3), "fps": fps,
                "width": int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)),
                "height": int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                "scenes": scenes, "scene_detection": "HSV histogram, sampled at about 2 fps; candidate cuts only"}
    finally:
        capture.release()


def prepare(input_path: Path, output_dir: Path) -> dict:
    source, output = _target(input_path, output_dir,
                             ("proxy.mp4", "audio.wav", "contact-sheet.jpg", "analysis.json"))
    analysis = _inspect_video(source)
    binary = ffmpeg()
    common = [binary, "-hide_banner", "-loglevel", "error", "-nostdin", "-n"]
    _run(common + ["-i", str(source), "-map", "0:v:0", "-map", "0:a:0?",
                   "-vf", "scale=-2:720", "-c:v", "libx264", "-preset", "veryfast",
                   "-crf", "25", "-c:a", "aac", "-movflags", "+faststart", str(output / "proxy.mp4")])
    # FFmpeg's null output reports stream inventory without requiring ffprobe.
    probe = _run([binary, "-hide_banner", "-nostdin", "-i", str(source),
                  "-t", "0", "-f", "null", "-"], timeout=60)
    has_audio = bool(re.search(r"Stream #.*Audio:", probe.stderr))
    if has_audio:
        _run(common + ["-i", str(source), "-map", "0:a:0", "-vn", "-ac", "1", "-ar", "16000",
                       "-c:a", "pcm_s16le", str(output / "audio.wav")])
    rate = 12 / max(analysis["duration_seconds"], 0.001)
    _run(common + ["-i", str(source), "-vf", f"fps={rate},scale=320:-2,tile=4x3",
                   "-frames:v", "1", "-update", "1", str(output / "contact-sheet.jpg")])
    result = {**analysis, "input": str(source), "has_audio": has_audio,
              "proxy": str(output / "proxy.mp4"), "audio": str(output / "audio.wav") if has_audio else None,
              "contact_sheet": str(output / "contact-sheet.jpg"), "analysis": str(output / "analysis.json")}
    _write_json(output / "analysis.json", result)
    return result


def _timestamp(seconds: float) -> str:
    millis = max(0, round(seconds * 1000))
    hours, remainder = divmod(millis, 3600000)
    minutes, remainder = divmod(remainder, 60000)
    seconds, milliseconds = divmod(remainder, 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"


def _speech_model(model: str):
    from faster_whisper import WhisperModel
    return WhisperModel(model, device="cpu", compute_type="int8", cpu_threads=4,
                        download_root=str(ROOT / ".studio" / "models"))


def transcribe(input_path: Path, output_dir: Path, model: str = "tiny") -> dict:
    source, output = _target(input_path, output_dir,
                             ("transcript.json", "transcript.srt", "transcript.txt"))
    segments, info = _speech_model(model).transcribe(str(source), beam_size=5, vad_filter=True)
    records = [{"start": float(s.start), "end": float(s.end), "text": s.text.strip()} for s in segments]
    result = {"input": str(source), "model": model, "language": info.language,
              "duration_seconds": float(info.duration), "segments": records,
              "json": str(output / "transcript.json"), "srt": str(output / "transcript.srt"),
              "text": str(output / "transcript.txt")}
    with (output / "transcript.txt").open("x", encoding="utf-8") as handle:
        handle.write("".join(s["text"] + "\n" for s in records))
    with (output / "transcript.srt").open("x", encoding="utf-8") as handle:
        for index, segment in enumerate(records, 1):
            handle.write(f"{index}\n{_timestamp(segment['start'])} --> {_timestamp(segment['end'])}\n{segment['text']}\n\n")
    _write_json(output / "transcript.json", result)
    return result


def demo(output_dir: Path) -> dict:
    output = Path(output_dir).resolve()
    source = output / "synthetic.mp4"
    if source.exists():
        raise FileExistsError(f"Demo already exists: {source}")
    output.mkdir(parents=True, exist_ok=True)
    _run([ffmpeg(), "-hide_banner", "-loglevel", "error", "-nostdin", "-n", "-f", "lavfi",
          "-i", "testsrc2=size=640x360:rate=24:duration=4", "-f", "lavfi", "-i",
          "sine=frequency=440:sample_rate=16000:duration=4", "-c:v", "libx264", "-pix_fmt",
          "yuv420p", "-c:a", "aac", "-shortest", str(source)])
    return prepare(source, output / "prepared")
