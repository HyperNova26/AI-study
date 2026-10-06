#!/usr/bin/env bash
# i forward, j/l turn, k stop, comma reverse. Publishes geometry_msgs/Twist to /cmd_vel.
set -eo pipefail

source "${ROS_SETUP:-/opt/ros/jazzy/setup.bash}"

exec ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args \
  -r cmd_vel:=/cmd_vel -p speed:=0.5 -p turn:=0.8