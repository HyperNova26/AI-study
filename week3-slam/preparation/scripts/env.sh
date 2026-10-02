#!/usr/bin/env bash
# Source this file in every terminal used for the week-3 FAST-LIO2 practice.
if [[ -n "${ROS_DISTRO:-}" && "$ROS_DISTRO" != jazzy ]]; then
    printf '다른 ROS 배포판이 활성화되어 있습니다: %s. 새 터미널에서 Jazzy를 사용하세요.\n' "$ROS_DISTRO" >&2
    return 1
fi
if [[ ! -f /opt/ros/jazzy/setup.bash ]]; then
    printf 'ROS 2 Jazzy가 없습니다. week3-slam/preparation/README.md의 설치 안내를 확인하세요.\n' >&2
    return 1
fi
# ROS setup files may reference unset variables; source before enabling nounset.
source /opt/ros/jazzy/setup.bash || return 1
# FAST-LIO2 is built outside the repository by scripts/build_fast_lio.sh.
export FASTLIO_WS="${FASTLIO_WS:-$HOME/aistudy_fastlio_ws}"
if [[ -f "$FASTLIO_WS/install/setup.bash" ]]; then
    source "$FASTLIO_WS/install/setup.bash" || return 1
fi
# Week 2 used domain 42; a different default keeps a leftover week-2 run from mixing in.
export ROS_DOMAIN_ID="${ROS_DOMAIN_ID:-43}"
export ROS_AUTOMATIC_DISCOVERY_RANGE="${ROS_AUTOMATIC_DISCOVERY_RANGE:-LOCALHOST}"
export GZ_PARTITION="${GZ_PARTITION:-aistudy-week3-${ROS_DOMAIN_ID}}"
