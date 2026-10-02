#!/usr/bin/env bash
# Keyboard teleop on /cmd_vel (i: forward, j/l: turn, k: stop, ,: back; u/o/m/.: arcs).
# Same as week2-gait/ChanwonJung/teleop.sh. speed/turn are the initial command sizes.
set -eo pipefail
ROS_SETUP="${ROS_SETUP:-/opt/ros/jazzy/setup.bash}"
if [[ ! -f "${ROS_SETUP}" ]]; then
    printf 'ROS 2 설정 파일이 없습니다: %s\n' "${ROS_SETUP}" >&2
    exit 1
fi
# shellcheck disable=SC1090
source "${ROS_SETUP}"
set -u
exec ros2 run teleop_twist_keyboard teleop_twist_keyboard \
    --ros-args -r cmd_vel:=/cmd_vel -p speed:=0.5 -p turn:=0.8 "$@"
