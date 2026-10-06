#!/usr/bin/env bash
# Start Isaac Sim's ROS 2 runtime and JaeDae's custom maze.  Week 3 policy is read-only input.
set -euo pipefail
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
isaaclab_root="${ISAACLAB_ROOT:-$HOME/IsaacLab}"
policy_default="$script_dir/../../week3-gait/JaeDae/policy/policy.pt"
policy="${1:-$policy_default}"
if [[ ! -x "$isaaclab_root/isaaclab.sh" ]]; then
  printf 'Isaac Lab not found: %s/isaaclab.sh\n' "$isaaclab_root" >&2; exit 1
fi
if [[ ! -f "$policy" ]]; then
  printf 'Week 3 policy not found: %s\n' "$policy" >&2; exit 1
fi
sim_root="$(readlink -f "$isaaclab_root/_isaac_sim")"
ros_core="$sim_root/exts/isaacsim.ros2.core/jazzy"
if [[ ! -d "$ros_core/rclpy" ]]; then
  printf 'Isaac Sim bundled ROS 2 was not found: %s\n' "$ros_core" >&2; exit 1
fi
unset AMENT_PREFIX_PATH COLCON_PREFIX_PATH PYTHONPATH LD_LIBRARY_PATH
export ROS_DISTRO=jazzy ROS_VERSION=2 ROS_PYTHON_VERSION=3 RMW_IMPLEMENTATION=rmw_fastrtps_cpp
export PYTHONPATH="$ros_core/rclpy"
export LD_LIBRARY_PATH="$ros_core/lib:$HOME/IsaacLab/env_isaaclab/lib/python3.12/site-packages/nvidia/cu13/lib"
exec "$isaaclab_root/isaaclab.sh" -p "$script_dir/go2_maze_ros2.py" --policy "$policy"
