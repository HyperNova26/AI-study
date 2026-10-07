#!/usr/bin/env bash
# Keyboard teleop for the simulated Burger (i: forward, j/l: turn, k: stop, ,: back).
set -eo pipefail
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
source "$script_dir/env.sh"
exec ros2 run teleop_twist_keyboard teleop_twist_keyboard \
    --ros-args -r cmd_vel:=/cmd_vel -p speed:=0.15 -p turn:=0.6 "$@"
