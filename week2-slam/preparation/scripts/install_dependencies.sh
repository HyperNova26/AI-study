#!/usr/bin/env bash
set -eo pipefail

source /etc/os-release
if [[ "$ID" != ubuntu || "$VERSION_ID" != 24.04 ]]; then
    printf '이 준비 환경은 Ubuntu 24.04용입니다. 현재 OS: %s\n' "$PRETTY_NAME" >&2
    exit 1
fi
if [[ ! -f /opt/ros/jazzy/setup.bash ]]; then
    printf '먼저 README의 공식 설치 안내로 ros-jazzy-desktop을 설치하세요.\n' >&2
    exit 1
fi

sudo apt-get update
sudo apt-get install -y \
    ros-jazzy-navigation2 \
    ros-jazzy-nav2-bringup \
    ros-jazzy-nav2-minimal-tb3-sim \
    ros-jazzy-ros-gz \
    ros-jazzy-rviz2 \
    ros-jazzy-tf2-tools \
    ros-jazzy-tf2-ros \
    python3-yaml \
    graphviz

printf '설치 완료. 다음으로 scripts/check_environment.sh를 실행하세요.\n'
