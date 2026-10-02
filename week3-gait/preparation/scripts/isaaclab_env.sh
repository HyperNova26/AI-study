#!/usr/bin/env bash
# Sourced by the week-3 gait scripts. Locates Isaac Lab and keeps training output outside the repository.
ISAACLAB_ROOT="${ISAACLAB_ROOT:-$HOME/IsaacLab}"
if [[ ! -x "$ISAACLAB_ROOT/isaaclab.sh" ]]; then
    printf 'Isaac Lab을 찾지 못했습니다: %s/isaaclab.sh\nISAACLAB_ROOT=/경로/IsaacLab 으로 지정하세요.\n' "$ISAACLAB_ROOT" >&2
    return 1
fi
export ISAACLAB_ROOT
# isaaclab.sh train/play write logs/rsl_rl/... under the current directory, so run them from here.
export GO2_RUNS_DIR="${GO2_RUNS_DIR:-$HOME/aistudy_go2_runs}"
mkdir -p "$GO2_RUNS_DIR"
# Training and export need no ROS. A sourced /opt/ros/jazzy would mix its Python and libraries with
# Isaac Sim's bundled ones (the week-2 launcher clears them for the same reason).
unset AMENT_PREFIX_PATH COLCON_PREFIX_PATH PYTHONPATH LD_LIBRARY_PATH CMAKE_PREFIX_PATH
