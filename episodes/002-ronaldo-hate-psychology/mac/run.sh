#!/bin/bash
set -euo pipefail
packet_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
blender_bin="${BLENDER_BIN:-/Applications/Blender.app/Contents/MacOS/Blender}"
mode="${1:-preview}"
render_args=(--background --python "$packet_dir/studio_scene.py" -- --manifest "$packet_dir/manifest.json")
case "$mode" in
  preview) render_args+=(--preview) ;;
  render) render_args+=(--render) ;;
  build) ;;
  *) printf 'Usage: bash run.sh [preview|render|build]\n' >&2; exit 2 ;;
esac
if [[ ! -x "$blender_bin" ]]; then
  printf 'Blender executable not found: %s\nSet BLENDER_BIN to its approved location.\n' "$blender_bin" >&2
  exit 1
fi
printf 'Running %s; see %s/render.log for progress.\n' "$mode" "$packet_dir"
if "$blender_bin" "${render_args[@]}" > "$packet_dir/render.log" 2>&1; then
  printf 'Completed. See validation.json and %s output folder.\n' "$mode"
else
  result=$?
  printf 'Blender failed (exit %s). Inspect render.log.\n' "$result" >&2
  exit "$result"
fi
