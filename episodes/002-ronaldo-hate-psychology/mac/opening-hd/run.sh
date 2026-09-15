#!/bin/bash
set -euo pipefail
packet_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
blender_bin="${BLENDER_BIN:-/Applications/Blender.app/Contents/MacOS/Blender}"
mode="${1:-preview}"
render_args=(--background --python-exit-code 1 --python "$packet_dir/opening_hd.py" -- --manifest "$packet_dir/manifest.json")
case "$mode" in
  preview) render_args+=(--preview) ;;
  render) render_args+=(--render) ;;
  resume) render_args+=(--render --resume) ;;
  build) ;;
  *) printf 'Usage: bash run.sh [preview|build|render|resume]\n' >&2; exit 2 ;;
esac
if [[ ! -x "$blender_bin" ]]; then
  printf 'Blender executable not found: %s\nSet BLENDER_BIN to its approved location.\n' "$blender_bin" >&2
  exit 1
fi
log="$packet_dir/render-$(date +%Y%m%d-%H%M%S)-$$.log"
printf 'Running %s; progress: %s\n' "$mode" "$log"
if "$blender_bin" "${render_args[@]}" > "$log" 2>&1; then
  printf 'Completed. See motion-report.json, previews/ or frames/.\n'
else
  result=$?
  printf 'Blender failed (exit %s). Keep the frames and log; resume verifies both source and output.\n' "$result" >&2
  exit "$result"
fi
