#!/usr/bin/env bash
set -eo pipefail

ROS_SETUP="${ROS_SETUP:-/opt/ros/jazzy/setup.bash}"

if [[ ! -f "${ROS_SETUP}" ]]; then
    echo "ROS 2 setup file not found: ${ROS_SETUP}" >&2
    exit 1
fi

# shellcheck disable=SC1090
source "${ROS_SETUP}"
set -u

exec ros2 run teleop_twist_keyboard teleop_twist_keyboard \
    --ros-args -r cmd_vel:=/cmd_vel "$@"

