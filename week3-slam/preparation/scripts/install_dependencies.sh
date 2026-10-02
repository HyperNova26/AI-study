#!/usr/bin/env bash
set -eo pipefail

source /etc/os-release
if [[ "$ID" != ubuntu || "$VERSION_ID" != 24.04 ]]; then
    printf '이 시뮬레이션 환경은 Ubuntu 24.04용입니다. 현재 OS: %s\n' "$PRETTY_NAME" >&2
    exit 1
fi
if [[ ! -f /opt/ros/jazzy/setup.bash ]]; then
    printf '먼저 ROS 2 Jazzy 공식 설치 안내로 ros-jazzy-desktop을 설치하세요.\n' >&2
    exit 1
fi

sudo apt-get update
# Simulation (same as week 2, without Nav2), FAST-LIO2 build tools/libraries, teleop and analysis.
sudo apt-get install -y \
    ros-jazzy-ros-gz \
    ros-jazzy-nav2-minimal-tb3-sim \
    ros-jazzy-turtlebot3-description \
    ros-jazzy-robot-state-publisher \
    ros-jazzy-xacro \
    ros-jazzy-rviz2 \
    ros-jazzy-tf2-ros \
    ros-jazzy-tf2-tools \
    ros-jazzy-pcl-ros \
    ros-jazzy-pcl-conversions \
    ros-jazzy-teleop-twist-keyboard \
    ros-jazzy-rosbag2-storage-mcap \
    libpcl-dev \
    libeigen3-dev \
    python3-dev \
    python3-colcon-common-extensions \
    python3-numpy \
    python3-yaml \
    python3-matplotlib \
    build-essential \
    git

printf '설치 완료. 다음으로 scripts/build_fast_lio.sh를 실행하세요.\n'
