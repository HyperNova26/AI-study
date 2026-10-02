#!/usr/bin/env bash
# Start the maze + Go2 policy + ROS 2 /cmd_vel subscriber (go2_policy_teleop.py) with Isaac Lab.
#
#   bash scripts/run_teleop_policy.sh                                   # provided pretrained policy
#   bash scripts/run_teleop_policy.sh --policy /path/to/policy.pt       # your exported policy
#   bash scripts/run_teleop_policy.sh --policy p.pt --maze-usd my_maze.usda --spawn -4.15 -3.2 0.42
#
# Same environment handling as week2-gait/ChanwonJung/isaaclab.sh: use Isaac Sim's bundled ROS 2 Jazzy
# rclpy instead of /opt/ros, so Kit's protobuf and ROS libraries are not mixed.
set -eo pipefail
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ISAACLAB_ROOT="${ISAACLAB_ROOT:-$HOME/IsaacLab}"
if [[ ! -x "${ISAACLAB_ROOT}/isaaclab.sh" ]]; then
    printf 'Isaac Lab을 찾지 못했습니다: %s/isaaclab.sh\nISAACLAB_ROOT=/경로/IsaacLab 으로 지정하세요.\n' "$ISAACLAB_ROOT" >&2
    exit 1
fi
ISAAC_SIM_ROOT="$(readlink -f "${ISAACLAB_ROOT}/_isaac_sim")"
ROS_CORE="${ISAAC_SIM_ROOT}/exts/isaacsim.ros2.core/jazzy"
if [[ ! -d "${ROS_CORE}/rclpy" ]]; then
    printf 'Isaac Sim 내장 ROS 2 Jazzy를 찾지 못했습니다: %s\n' "$ROS_CORE" >&2
    exit 1
fi

unset AMENT_PREFIX_PATH COLCON_PREFIX_PATH PYTHONPATH LD_LIBRARY_PATH
export ROS_DISTRO=jazzy
export ROS_VERSION=2
export ROS_PYTHON_VERSION=3
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
export PYTHONPATH="${ROS_CORE}/rclpy"
export LD_LIBRARY_PATH="${ROS_CORE}/lib"
# Relative --policy/--maze-usd paths are resolved from the current directory. The provided pretrained
# checkpoint is downloaded to .pretrained_checkpoints/ there (git-ignored in week3-gait/).
exec "${ISAACLAB_ROOT}/isaaclab.sh" -p "${script_dir}/../go2_policy_teleop.py" "$@"
