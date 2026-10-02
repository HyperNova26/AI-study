#!/usr/bin/env bash
# Run a policy in the week-2 maze with ROS 2 teleop (terminal 2: bash ../preparation/scripts/teleop.sh).
#   bash run_maze.sh              # own policy (policy/policy.pt)
#   bash run_maze.sh --provided   # provided pretrained policy, for comparison
# This example uses the week-2 gait maze in this repository (week2-gait/ChanwonJung) and its start pose.
# Students pass their own week-2 maze, e.g. --maze-usd <maze.usda> --spawn X Y 0.42 --spawn-yaw DEG
# (later options win).
set -eo pipefail
here="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
maze=(--maze-usd "$here/../../week2-gait/ChanwonJung/assets/go2_maze.usda" --spawn -4.15 -3.2 0.42 --spawn-yaw 0)
if [[ "${1:-}" == "--provided" ]]; then
    shift
    exec bash "$here/../preparation/scripts/run_teleop_policy.sh" "${maze[@]}" "$@"
fi
exec bash "$here/../preparation/scripts/run_teleop_policy.sh" --policy "$here/policy/policy.pt" "${maze[@]}" "$@"
