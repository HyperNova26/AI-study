#!/usr/bin/env bash
# Record raw inputs only; replay must not inject an earlier FAST-LIO2 estimate.
set -eo pipefail
here="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
source "$here/../preparation/scripts/env.sh"
output="${1:-$here/results/bag_$(date +%Y%m%d_%H%M%S)}"
exec ros2 bag record -s mcap -o "$output" /clock /points_fastlio /imu /odom /ground_truth/odom
