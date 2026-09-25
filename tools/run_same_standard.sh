#!/usr/bin/env bash
# Run from anywhere inside the clone. No Python packages or downloads required.
set -euo pipefail
root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
blender_bin="${BLENDER_BIN:-/Applications/Blender.app/Contents/MacOS/Blender}"
mode="${1:-open}"
if [[ ! -x "$blender_bin" ]]; then
  printf 'Blender not found: %s\nSet BLENDER_BIN to your Blender executable.\n' "$blender_bin" >&2
  exit 1
fi
if [[ "$mode" != open && "$mode" != build && "$mode" != render ]]; then
  printf 'Usage: bash tools/run_same_standard.sh [open|build|render]\n' >&2
  exit 2
fi
cd "$root"
packet="episodes/002-ronaldo-hate-psychology/shorts/same-standard"
revision="$(git rev-parse --short HEAD)"
output="output/same-standard-$revision"
mkdir -p "$output"
flag=--build
[[ "$mode" == render ]] && flag=--render
printf 'Building animation with packed audio. Log: %s/build.log\n' "$output"
if ! "$blender_bin" --background --factory-startup --python-exit-code 1 \
  --python blender/rules_short_scene.py -- \
  --timeline "$packet/timeline.json" --audio "$packet/assets/narration.ogg" \
  --output "$output" "$flag" --resolution 1080 1920 > "$output/build.log" 2>&1; then
  tail -n 50 "$output/build.log" >&2
  exit 1
fi
printf 'Ready: %s/consistent-rules.blend\n' "$output"
if [[ "$mode" == open ]]; then
  "$blender_bin" "$output/consistent-rules.blend"
fi
