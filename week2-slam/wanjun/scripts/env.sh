#!/usr/bin/env bash
# Source this file in every terminal used for this practice environment.
if [[ -n "${ROS_DISTRO:-}" && "$ROS_DISTRO" != jazzy ]]; then
    printf '다른 ROS 배포판이 활성화되어 있습니다: %s. 새 터미널에서 Jazzy를 사용하세요.\n' "$ROS_DISTRO" >&2
    return 1
fi
if [[ ! -f /opt/ros/jazzy/setup.bash ]]; then
    printf 'ROS 2 Jazzy가 없습니다. week2-slam/wanjun/SETUP.md의 설치 안내를 확인하세요.\n' >&2
    return 1
fi
# ROS setup files may reference unset variables; source before enabling nounset.
source /opt/ros/jazzy/setup.bash || return 1
export ROS_DOMAIN_ID="${ROS_DOMAIN_ID:-42}"
export ROS_AUTOMATIC_DISCOVERY_RANGE="${ROS_AUTOMATIC_DISCOVERY_RANGE:-LOCALHOST}"
export GZ_PARTITION="${GZ_PARTITION:-aistudy-week2-${ROS_DOMAIN_ID}}"
