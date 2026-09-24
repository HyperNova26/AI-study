#!/usr/bin/env bash
set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ISAACLAB_ROOT="${ISAACLAB_ROOT:-/home/chanwonjung/IsaacLab}"

if [[ ! -x "${ISAACLAB_ROOT}/isaaclab.sh" ]]; then
    echo "Isaac Lab launcher not found: ${ISAACLAB_ROOT}/isaaclab.sh" >&2
    echo "Set ISAACLAB_ROOT to your IsaacLab checkout." >&2
    exit 1
fi

ISAAC_SIM_ROOT="$(readlink -f "${ISAACLAB_ROOT}/_isaac_sim")"
ROS_CORE="${ISAAC_SIM_ROOT}/exts/isaacsim.ros2.core/jazzy"

if [[ ! -d "${ROS_CORE}/rclpy" ]]; then
    echo "Isaac Sim bundled ROS 2 Jazzy was not found: ${ROS_CORE}" >&2
    exit 1
fi

# Avoid mixing /opt/ros libraries with Kit's bundled protobuf and ROS libs.
unset AMENT_PREFIX_PATH COLCON_PREFIX_PATH PYTHONPATH LD_LIBRARY_PATH
export ROS_DISTRO=jazzy
export ROS_VERSION=2
export ROS_PYTHON_VERSION=3
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
export PYTHONPATH="${ROS_CORE}/rclpy"
export LD_LIBRARY_PATH="${ROS_CORE}/lib"
set -u

exec "${ISAACLAB_ROOT}/isaaclab.sh" -p \
    "${SCRIPT_DIR}/go2_maze_ros2.py" "$@"
