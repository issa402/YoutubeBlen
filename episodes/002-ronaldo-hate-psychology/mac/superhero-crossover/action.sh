#!/bin/bash
set -euo pipefail
packet_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
blender_bin="${BLENDER_BIN:-/Applications/Blender.app/Contents/MacOS/Blender}"
mode="${1:-build}"
if [[ $# -gt 1 || ! -x "$blender_bin" ]]; then
  printf 'Usage: bash action.sh [build|preview|render]\nBlender must be installed at BLENDER_BIN or /Applications/Blender.app.\n' >&2
  exit 2
fi
output="$packet_dir/action-output"
case "$mode" in
  build) ;;
  preview|render) output="$packet_dir/action-$mode-$(date +%Y%m%d-%H%M%S)-$$" ;;
  *) printf 'Usage: bash action.sh [build|preview|render]\n' >&2; exit 2 ;;
esac
render_args=(--background --factory-startup --python-exit-code 1 --python "$packet_dir/action_crossover.py" -- --output "$output")
if [[ "$mode" != build ]]; then render_args+=("--$mode"); fi
log="$packet_dir/action-$(date +%Y%m%d-%H%M%S)-$$.log"
printf 'Building %s; progress log: %s\n' "$mode" "$log"
if "$blender_bin" "${render_args[@]}" > "$log" 2>&1; then
  printf 'Completed: %s/action-crossover.blend\n' "$output"
else
  result=$?
  tail -n 60 "$log" >&2 || true
  printf '\nBlender exited %s. Log: %s\n' "$result" "$log" >&2
  exit "$result"
fi
