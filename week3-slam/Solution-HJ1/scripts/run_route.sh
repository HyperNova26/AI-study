#!/usr/bin/env bash
# Optional: drive the fixed loop around the sandbox pillars (same motion every run). Teleop works too.
set -eo pipefail
here="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
source "$here/../preparation/scripts/env.sh"
exec python3 "$here/tools/drive_route.py" "$@" --ros-args -p use_sim_time:=true
