#!/usr/bin/env bash
# FAST-LIO2 (provided config + config/fast_lio_overrides.yaml) + odom->camera_init link + RViz.
# Start ../preparation/scripts/run_simulation.sh first and keep the robot still until "IMU Initial Done".
set -eo pipefail
here="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
source "$here/../preparation/scripts/env.sh"
exec ros2 launch "$here/launch/fast_lio_rviz.launch.py" "$@"
