#!/usr/bin/env bash
# Run FAST-LIO2 with the provided base config through the upstream launch file (mapping.launch.py).
# Start scripts/run_simulation.sh first and keep the robot still until "IMU Initial Done".
# RViz: rviz/fast_lio.rviz (Fixed Frame camera_init); pass rviz:=false to skip it.
set -eo pipefail
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
prep_dir="$(cd -- "$script_dir/.." && pwd)"
source "$script_dir/env.sh"
exec ros2 launch fast_lio mapping.launch.py \
    config_path:="$prep_dir/config" \
    config_file:=fast_lio_burger.yaml \
    rviz_cfg:="$prep_dir/rviz/fast_lio.rviz" \
    use_sim_time:=true "$@"
