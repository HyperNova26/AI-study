#!/usr/bin/env bash
# Build missing robot assets and FAST-LIO2 without changing system packages.
set -eo pipefail
here="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
source "$here/../preparation/scripts/env.sh"
if ! ros2 pkg prefix turtlebot3_description >/dev/null 2>&1; then
    robot_repo="$FASTLIO_WS/vendor/turtlebot3"
    robot_commit=da785b7201d317e6e2a662e41bb3d3fd50ebd503
    mkdir -p "$FASTLIO_WS/vendor" "$FASTLIO_WS/src"
    touch "$FASTLIO_WS/vendor/COLCON_IGNORE"
    if [[ ! -d "$robot_repo" ]]; then
        git clone --depth 1 --branch 2.3.6 https://github.com/ROBOTIS-GIT/turtlebot3.git "$robot_repo"
    fi
    if [[ "$(git -C "$robot_repo" rev-parse HEAD)" != "$robot_commit" ]]; then
        printf 'Unexpected TurtleBot3 revision at %s; preserve it and check manually.\n' "$robot_repo" >&2
        exit 1
    fi
    if [[ ! -e "$FASTLIO_WS/src/turtlebot3_description" ]]; then
        ln -s "$robot_repo/turtlebot3_description" "$FASTLIO_WS/src/turtlebot3_description"
    fi
fi
export CMAKE_BUILD_PARALLEL_LEVEL="${CMAKE_BUILD_PARALLEL_LEVEL:-2}"
export MAKEFLAGS="${MAKEFLAGS:--j2}"
bash "$here/../preparation/scripts/build_fast_lio.sh"
bash "$here/../preparation/scripts/check_environment.sh"
