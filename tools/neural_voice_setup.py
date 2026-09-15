"""Download pinned Kokoro data files; execute no downloaded scripts."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import urllib.request
import uuid

BASE = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.1/"
ASSETS = {
    "kokoro-v1.0.onnx": "beb0d1848dee9a49da392cc3df26958d46cfa35d321edf434f52949153f0df3a",
    "voices-v1.0.bin": "bca610b8308e8d99f32e6fe4197e7ec01679264efed0cac9140fe9c29f1fbf7d",
}


def file_hash(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def verify_file(path: Path, expected: str) -> None:
    if file_hash(path) != expected:
        raise ValueError(f"Model checksum mismatch: {path.name}")


def fetch_models(directory: Path) -> dict:
    directory.mkdir(parents=True, exist_ok=True)
    for name, digest in ASSETS.items():
        target = directory / name
        if target.exists():
            verify_file(target, digest)
            continue
        temporary = directory / f".{name}.{uuid.uuid4().hex}.part"
        try:
            request = urllib.request.Request(BASE + name, headers={"User-Agent": "CreatorStudio/1.0"})
            with urllib.request.urlopen(request, timeout=60) as response, temporary.open("xb") as output:
                while chunk := response.read(1024 * 1024):
                    output.write(chunk)
            verify_file(temporary, digest)
            temporary.rename(target)
        finally:
            temporary.unlink(missing_ok=True)
        print(f"Verified {name}", flush=True)
    manifest = {"release": "model-files-v1.1", "assets": [
        {"name": name, "sha256": digest, "url": BASE + name} for name, digest in ASSETS.items()
    ]}
    (directory / "provenance.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--models", type=Path, default=Path(".studio/models/voice"))
    print(json.dumps(fetch_models(parser.parse_args().models), indent=2))
