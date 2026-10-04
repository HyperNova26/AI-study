#!/usr/bin/env bash
# Record /odom, /Odometry and /ground_truth/odom until Ctrl+C, then write results/<time>/ (CSV, metrics, plot).
set -eo pipefail
here="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
source "$here/../preparation/scripts/env.sh"
exec python3 "$here/tools/odom_compare.py" --output-dir "$here/results/$(date +%Y%m%d_%H%M%S)" "$@" \
    --ros-args -p use_sim_time:=true
