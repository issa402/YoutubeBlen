#!/bin/bash
set -euo pipefail
packet_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
blender_bin="${BLENDER_BIN:-/Applications/Blender.app/Contents/MacOS/Blender}"
mode="${1:-preview}"
render_args=(--background --python "$packet_dir/opening_sequence.py" -- --manifest "$packet_dir/manifest.json")
case "$mode" in
  preview) render_args+=(--preview) ;;
  render) render_args+=(--render) ;;
  draft) render_args+=(--render --lowres) ;;
  build) ;;
  *) printf 'Usage: bash run.sh [preview|build|draft|render]\n' >&2; exit 2 ;;
esac
if [[ ! -x "$blender_bin" ]]; then
  printf 'Blender executable not found: %s\nSet BLENDER_BIN to its approved location.\n' "$blender_bin" >&2
  exit 1
fi
printf 'Running %s; see render.log for progress.\n' "$mode"
if "$blender_bin" "${render_args[@]}" > "$packet_dir/render.log" 2>&1; then
  printf 'Completed. See motion-report.json, previews/ or frames/.\n'
else
  result=$?
  printf 'Blender failed (exit %s). Inspect render.log.\n' "$result" >&2
  exit "$result"
fi
