#!/usr/bin/env python3
"""Check the local YouTube/content-engine toolchain for blenderyt.

This script does not download videos or call external services. It only proves
that the local Python packages and command-line tools needed by the planned
video-analysis workflow are importable/available.
"""

from __future__ import annotations

import importlib
import shutil
import subprocess
from dataclasses import dataclass


@dataclass(frozen=True)
class CheckResult:
    name: str
    status: str
    detail: str


def check_python_module(module_name: str) -> CheckResult:
    try:
        module = importlib.import_module(module_name)
        version = getattr(module, "__version__", "version unknown")
        return CheckResult(module_name, "OK", str(version))
    except Exception as exc:
        return CheckResult(module_name, "MISSING", f"{exc.__class__.__name__}: {exc}")


def check_command(command_name: str) -> CheckResult:
    path = shutil.which(command_name)
    if not path:
        return CheckResult(command_name, "MISSING", "not found on PATH")

    try:
        result = subprocess.run(
            [command_name, "--version"],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
        first_line = (result.stdout or result.stderr).strip().splitlines()[0]
        return CheckResult(command_name, "OK", f"{path} ({first_line})")
    except Exception as exc:
        return CheckResult(command_name, "OK", f"{path} (version check failed: {exc})")


def print_result(result: CheckResult) -> None:
    print(f"{result.status:8} {result.name:14} {result.detail}")


def main() -> None:
    print("Blenderyt Content Toolchain Check")
    print("=================================")

    module_checks = [
        check_python_module("yt_dlp"),
        check_python_module("cv2"),
        check_python_module("supervision"),
        check_python_module("scenedetect"),
        check_python_module("numpy"),
    ]

    command_checks = [
        check_command("ffmpeg"),
    ]

    for result in [*module_checks, *command_checks]:
        print_result(result)

    failed = [result for result in [*module_checks, *command_checks] if result.status != "OK"]
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
