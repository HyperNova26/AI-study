#!/usr/bin/env python3
"""Drive the simulated Burger around a fixed loop so that every run sees the same motion.

Adapted from Solution-HJ1: lower recording speeds, stop on stale odometry,
and enforce a wall-clock timeout so interrupted simulation cannot drive indefinitely.

Optional helper for recording: keyboard teleop works just as well. Waypoints are given in
the sandbox `map`/Gazebo world frame and converted to `odom` with the spawn pose, then
followed with /odom feedback only (FAST-LIO2 output is never used for control).
"""

import argparse
import math
import time

import rclpy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.signals import SignalHandlerOptions

# Corridors between the 3x3 pillars of the sandbox (pillars at +-1.1 m, radius 0.15 m).
# Every segment keeps >= 0.3 m from the obstacles in maps/tb3_sandbox.pgm of week 2.
ROUTE = [(-1.6, -0.55), (1.6, -0.55), (1.6, 0.55), (-0.55, 0.55), (-0.55, 1.6),
         (0.55, 1.6), (0.55, -1.6), (-1.6, -1.6), (-1.6, -0.55), (-2.0, -0.5)]


def wrap(angle):
    return math.atan2(math.sin(angle), math.cos(angle))


class RouteDriver(Node):
    def __init__(self, args):
        super().__init__("drive_route")
        self.args = args
        cos0, sin0 = math.cos(args.spawn[2]), math.sin(args.spawn[2])
        self.goals = []
        for _ in range(args.loops):
            for x, y in ROUTE:
                dx, dy = x - args.spawn[0], y - args.spawn[1]
                self.goals.append((cos0 * dx + sin0 * dy, -sin0 * dx + cos0 * dy))
        self.pose = None
        self.last_odom_time = None
        self.started = time.monotonic()
        self.index = 0
        self.cmd = self.create_publisher(Twist, "/cmd_vel", 10)
        self.create_subscription(Odometry, "/odom", self.on_odom, 10)
        self.timer = self.create_timer(0.05, self.step)
        self.done = False

    def on_odom(self, msg):
        self.last_odom_time = time.monotonic()
        q = msg.pose.pose.orientation
        yaw = math.atan2(2.0 * (q.w * q.z + q.x * q.y), 1.0 - 2.0 * (q.y * q.y + q.z * q.z))
        self.pose = (msg.pose.pose.position.x, msg.pose.pose.position.y, yaw)

    def step(self):
        if self.pose is None or self.done:
            return
        if self.index >= len(self.goals):
            self.cmd.publish(Twist())
            self.get_logger().info("route finished")
            self.done = True
            return
        x, y, yaw = self.pose
        gx, gy = self.goals[self.index]
        distance = math.hypot(gx - x, gy - y)
        if distance < self.args.tolerance:
            self.cmd.publish(Twist())
            self.index += 1
            self.get_logger().info(f"waypoint {self.index}/{len(self.goals)} reached")
            return
        heading_error = wrap(math.atan2(gy - y, gx - x) - yaw)
        twist = Twist()
        twist.angular.z = max(-self.args.max_turn, min(self.args.max_turn, 1.5 * heading_error))
        if abs(heading_error) < 0.25:  # turn in place first, then drive
            twist.linear.x = min(self.args.max_speed, 0.6 * distance + 0.05)
        self.cmd.publish(twist)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--loops", type=int, default=1)
    parser.add_argument("--max-speed", type=float, default=0.15, help="m/s, Burger limit is 0.22")
    parser.add_argument("--max-turn", type=float, default=0.6, help="rad/s")
    parser.add_argument("--timeout", type=float, default=300.0, help="wall-clock seconds")
    parser.add_argument("--tolerance", type=float, default=0.05, help="waypoint radius (m)")
    parser.add_argument("--spawn", type=float, nargs=3, default=(-2.0, -0.5, 0.0),
                        metavar=("X", "Y", "YAW"), help="spawn pose in the world frame")
    args, _ = parser.parse_known_args()  # leave --ros-args ... to rclpy
    if args.loops < 1 or not 0 < args.max_speed <= 0.22 or args.max_turn <= 0 or args.tolerance <= 0 or args.timeout <= 0:
        parser.error("loops, speeds, tolerance and timeout must be positive; max-speed <= 0.22")
    # Without rclpy's own SIGINT handler, Ctrl+C raises KeyboardInterrupt while the context is still
    # valid, so the stop command below can still be sent. Gazebo's DiffDrive keeps the last /cmd_vel.
    rclpy.init(signal_handler_options=SignalHandlerOptions.NO)
    node = RouteDriver(args)
    try:
        while rclpy.ok() and not node.done:
            rclpy.spin_once(node, timeout_sec=0.1)
            now = time.monotonic()
            if now - node.started > args.timeout:
                raise RuntimeError("Route timed out before completion")
            if node.last_odom_time is not None and now - node.last_odom_time > 1.0:
                raise RuntimeError("Odometry stopped for more than one second; stopping")
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        if rclpy.ok():
            for _ in range(3):
                node.cmd.publish(Twist())
                rclpy.spin_once(node, timeout_sec=0.05)
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == "__main__":
    main()
