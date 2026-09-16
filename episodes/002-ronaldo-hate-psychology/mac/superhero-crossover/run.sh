#!/bin/bash
set -euo pipefail
packet_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
blender_bin="${BLENDER_BIN:-/Applications/Blender.app/Contents/MacOS/Blender}"
mode="${1:-build}"
if [[ $# -gt 1 ]]; then
  printf 'Usage: bash run.sh [build|preview|render|resume]\n' >&2
  exit 2
fi
render_args=(--background --python-exit-code 1 --python "$packet_dir/superhero_crossover.py" -- --output "$packet_dir")
case "$mode" in
  build) ;;
  preview) render_args+=(--preview) ;;
  render) render_args+=(--render) ;;
  resume) render_args+=(--render --resume) ;;
  *) printf 'Usage: bash run.sh [build|preview|render|resume]\n' >&2; exit 2 ;;
esac
if [[ ! -x "$blender_bin" ]]; then
  printf 'Blender executable not found: %s\nSet BLENDER_BIN to its approved location.\n' "$blender_bin" >&2
  exit 1
fi
log="$packet_dir/render-$(date +%Y%m%d-%H%M%S)-$$.log"
printf 'Running %s; progress log: %s\n' "$mode" "$log"
if "$blender_bin" "${render_args[@]}" > "$log" 2>&1; then
  printf 'Completed: %s/superhero-crossover.blend\n' "$packet_dir"
  case "$mode" in
    preview) printf 'Ten preview images: %s/previews/\n' "$packet_dir" ;;
    render|resume) printf 'Animation PNG frames: %s/frames/\n' "$packet_dir" ;;
  esac
else
  result=$?
  printf 'Blender failed (exit %s). Last 80 log lines follow:\n' "$result" >&2
  tail -n 80 "$log" >&2 || true
  printf '\nFull log: %s\nKeep existing frames for resume.\n' "$log" >&2
  exit "$result"
fi
