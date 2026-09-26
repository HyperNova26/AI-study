#!/usr/bin/env python3
"""Send one map-frame goal, observe feedback, and save an honest run report."""

import argparse
from collections import Counter
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import signal
import time

from action_msgs.msg import GoalStatus
from geometry_msgs.msg import Twist
from lifecycle_msgs.srv import GetState
from nav2_msgs.action import NavigateToPose
from nav_msgs.msg import OccupancyGrid, Odometry, Path as NavPath
import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from rclpy.parameter import Parameter
from rclpy.qos import DurabilityPolicy, QoSProfile, qos_profile_sensor_data
from rclpy.signals import SignalHandlerOptions
from rosgraph_msgs.msg import Clock
from sensor_msgs.msg import Imu, LaserScan, PointCloud2
from tf2_ros import Buffer, TransformException, TransformListener
import yaml


ROOT = Path(__file__).resolve().parent
STATUS_NAMES = {
    GoalStatus.STATUS_SUCCEEDED: "SUCCEEDED",
    GoalStatus.STATUS_CANCELED: "CANCELED",
    GoalStatus.STATUS_ABORTED: "ABORTED",
}


def finite_number(value):
    if isinstance(value, bool):
        raise ValueError("Boolean values are not coordinates or timeouts")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("Coordinates and timeouts must be finite")
    return number


def yaw_of(q):
    return math.atan2(2.0 * (q.w * q.z + q.x * q.y), 1.0 - 2.0 * (q.y * q.y + q.z * q.z))


def validate_goal_cell(grid, x, y):
    """Check the static map cell; Nav2 still checks footprint/path feasibility."""
    origin = grid.info.origin
    angle = yaw_of(origin.orientation)
    dx, dy = x - origin.position.x, y - origin.position.y
    col = math.floor((math.cos(angle) * dx + math.sin(angle) * dy) / grid.info.resolution)
    row = math.floor((-math.sin(angle) * dx + math.cos(angle) * dy) / grid.info.resolution)
    if not (0 <= col < grid.info.width and 0 <= row < grid.info.height):
        raise ValueError("Goal is outside the map")
    value = grid.data[row * grid.info.width + col]
    if value != 0:
        raise ValueError(f"Goal is not a known free map cell (occupancy={value})")


class GoalRunner(Node):
    def __init__(self):
        super().__init__("wanjun_goal_runner", parameter_overrides=[Parameter("use_sim_time", value=True)])
        self.stop_signal = 0
        self.messages = {}
        self.received_at = {}
        self.counts = Counter()
        self.feedback_samples = []
        self.last_feedback_log = 0.0
        self.max_linear_command = 0.0
        self.last_clock_ns = 0
        self.clock_changed_at = -math.inf
        self.goal_handle = None
        self.result_future = None
        self.send_future = None
        self.buffer = Buffer()
        self.listener = TransformListener(self.buffer, self)
        self.action = ActionClient(self, NavigateToPose, "/navigate_to_pose")
        self.lifecycle = self.create_client(GetState, "/bt_navigator/get_state")
        topics = [
            ("/clock", Clock), ("/scan", LaserScan), ("/points", PointCloud2),
            ("/imu", Imu), ("/odom", Odometry), ("/plan", NavPath), ("/cmd_vel", Twist),
        ]
        self.subscriptions_ = [
            self.create_subscription(kind, topic, lambda msg, t=topic: self.receive(t, msg), qos_profile_sensor_data)
            for topic, kind in topics
        ]
        self.subscriptions_.append(self.create_subscription(
            OccupancyGrid, "/map", lambda msg: self.receive("/map", msg),
            QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL),
        ))

    def receive(self, topic, message):
        self.messages[topic] = message
        self.received_at[topic] = time.monotonic()
        self.counts[topic] += 1
        if topic == "/clock":
            stamp = message.clock.sec * 1_000_000_000 + message.clock.nanosec
            if stamp > self.last_clock_ns:
                self.clock_changed_at = self.received_at[topic]
            self.last_clock_ns = stamp
        if topic == "/cmd_vel":
            self.max_linear_command = max(self.max_linear_command, abs(message.linear.x))

    def spin_until(self, predicate, timeout, description, interruptible=True):
        deadline = time.monotonic() + timeout
        while not predicate():
            if interruptible and self.stop_signal:
                raise InterruptedError("Stop requested")
            if time.monotonic() >= deadline:
                raise TimeoutError(description)
            rclpy.spin_once(self, timeout_sec=0.1)

    def wait_ready(self, timeout):
        state_future = None
        next_check = 0.0
        active = False

        def ready():
            nonlocal state_future, next_check, active
            now = time.monotonic()
            if state_future is not None and state_future.done():
                active = state_future.result().current_state.label == "active"
                state_future = None
            if not active and state_future is None and now >= next_check and self.lifecycle.service_is_ready():
                state_future = self.lifecycle.call_async(GetState.Request())
                next_check = now + 0.5
            sensors = ("/clock", "/scan", "/points", "/imu", "/odom")
            fresh = all(now - self.received_at.get(topic, -math.inf) < 2.0 for topic in sensors)
            clock_moving = self.counts["/clock"] >= 2 and now - self.clock_changed_at < 2.0
            return (active and fresh and clock_moving and "/map" in self.messages
                    and self.buffer.can_transform("map", "base_link", rclpy.time.Time())
                    and self.action.server_is_ready())

        self.get_logger().info("Waiting for map, sensor streams, TF and active Nav2...")
        self.spin_until(ready, timeout, "Startup timed out: check simulator, sensors, TF and Nav2")

    def pose(self):
        try:
            transform = self.buffer.lookup_transform("map", "base_link", rclpy.time.Time()).transform
            return {"x": transform.translation.x, "y": transform.translation.y, "yaw": yaw_of(transform.rotation)}
        except TransformException:
            return None

    def feedback(self, message):
        now = time.monotonic()
        if now - self.last_feedback_log < 1.0:
            return
        self.last_feedback_log = now
        data = message.feedback
        sample = {
            "distance_remaining_m": float(data.distance_remaining),
            "navigation_time_s": data.navigation_time.sec + data.navigation_time.nanosec / 1e9,
            "recoveries": int(data.number_of_recoveries),
        }
        self.feedback_samples.append(sample)
        self.get_logger().info(f"Remaining {sample['distance_remaining_m']:.2f} m; recoveries {sample['recoveries']}")

    def navigate(self, goal, report):
        self.wait_ready(goal["startup_timeout"])
        validate_goal_cell(self.messages["/map"], goal["x"], goal["y"])
        report["start_pose"] = self.pose()
        request = NavigateToPose.Goal()
        request.pose.header.frame_id = "map"
        request.pose.header.stamp = self.get_clock().now().to_msg()
        request.pose.pose.position.x = goal["x"]
        request.pose.pose.position.y = goal["y"]
        request.pose.pose.orientation.z = math.sin(goal["yaw"] / 2.0)
        request.pose.pose.orientation.w = math.cos(goal["yaw"] / 2.0)
        self.get_logger().info(f"Sending goal: x={goal['x']:.2f}, y={goal['y']:.2f}, yaw={goal['yaw']:.2f}")
        self.send_future = self.action.send_goal_async(request, feedback_callback=self.feedback)
        # Finish the response handshake so an accepted goal can be canceled on Ctrl+C.
        self.spin_until(self.send_future.done, 10.0, "Goal response timed out", interruptible=False)
        self.goal_handle = self.send_future.result()
        if not self.goal_handle.accepted:
            report["status"] = "REJECTED"
            return 1
        self.result_future = self.goal_handle.get_result_async()
        self.spin_until(self.result_future.done, goal["navigation_timeout"], "Navigation timed out")
        response = self.result_future.result()
        report["action_status"] = STATUS_NAMES.get(response.status, str(response.status))
        report["status"] = report["action_status"]
        report["nav2_error_code"] = int(response.result.error_code)
        report["nav2_error_message"] = response.result.error_msg
        return 0 if response.status == GoalStatus.STATUS_SUCCEEDED else 1

    def cancel_owned_goal(self):
        """Cancel only this script's goal and wait for a terminal result."""
        try:
            if self.goal_handle is None and self.send_future is not None:
                self.spin_until(self.send_future.done, 3.0, "Goal response still missing", interruptible=False)
                self.goal_handle = self.send_future.result()
            if self.goal_handle is None or not self.goal_handle.accepted:
                return "NO_ACCEPTED_GOAL"
            if self.result_future is None:
                self.result_future = self.goal_handle.get_result_async()
            if not self.result_future.done():
                canceled = self.goal_handle.cancel_goal_async()
                self.spin_until(canceled.done, 5.0, "Cancellation response missing", interruptible=False)
                self.spin_until(self.result_future.done, 5.0, "Terminal goal result missing", interruptible=False)
            return STATUS_NAMES.get(self.result_future.result().status, "UNKNOWN")
        except (TimeoutError, RuntimeError):
            return "UNKNOWN"


def arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--goal-file", type=Path, default=ROOT / "config/goal.yaml")
    for key in ("x", "y", "yaw"):
        parser.add_argument(f"--{key}", type=float)
    parser.add_argument("--startup-timeout", type=float)
    parser.add_argument("--timeout", type=float, help="Navigation wall-clock deadline in seconds")
    parser.add_argument("--output", type=Path, help="New JSON report path; existing files are not overwritten")
    args = parser.parse_args()
    try:
        goal = yaml.safe_load(args.goal_file.read_text())
        if not isinstance(goal, dict) or goal.get("frame_id") != "map":
            raise ValueError("Goal file must be a mapping with frame_id: map")
        for key in ("x", "y", "yaw", "startup_timeout", "navigation_timeout"):
            override = args.timeout if key == "navigation_timeout" else getattr(args, key, None)
            goal[key] = finite_number(goal[key] if override is None else override)
        if min(goal["startup_timeout"], goal["navigation_timeout"]) <= 0:
            raise ValueError("Timeouts must be positive")
        output = args.output or ROOT / "artifacts" / f"run_{datetime.now(timezone.utc):%Y%m%dT%H%M%S_%fZ}.json"
        if output.exists():
            raise ValueError(f"Output file already exists: {output}")
        output.parent.mkdir(parents=True, exist_ok=True)
    except (OSError, ValueError, TypeError, KeyError, yaml.YAMLError) as error:
        parser.error(str(error))
    return goal, output


def main():
    goal, output = arguments()
    report = {"started_at_utc": datetime.now(timezone.utc).isoformat(), "goal": goal, "status": "STARTING"}
    rclpy.init(signal_handler_options=SignalHandlerOptions.NO)
    node = GoalRunner()
    for signum in (signal.SIGINT, signal.SIGTERM):
        signal.signal(signum, lambda received, _frame: setattr(node, "stop_signal", received))
    started = time.monotonic()
    try:
        code = node.navigate(goal, report)
    except (TimeoutError, InterruptedError, ValueError, RuntimeError) as error:
        report["status"] = "INTERRUPTED" if isinstance(error, InterruptedError) else "TIMED_OUT" if isinstance(error, TimeoutError) else "ERROR"
        report["message"] = str(error)
        report["terminal_state_after_cancel"] = node.cancel_owned_goal()
        code = 128 + node.stop_signal if node.stop_signal else 124 if isinstance(error, TimeoutError) else 2
        if report["terminal_state_after_cancel"] == "UNKNOWN":
            node.get_logger().error("Goal state is UNKNOWN: cancellation could not be confirmed. Check Nav2 before continuing.")
    finally:
        report["elapsed_wall_seconds"] = round(time.monotonic() - started, 3)
        report["final_pose"] = node.pose()
        report["topic_message_counts"] = dict(node.counts)
        report["max_abs_cmd_vel_linear_x"] = node.max_linear_command
        report["feedback"] = node.feedback_samples
        if report["final_pose"]:
            pose = report["final_pose"]
            report["position_error_m"] = math.hypot(pose["x"] - goal["x"], pose["y"] - goal["y"])
            report["yaw_error_rad"] = abs(math.atan2(math.sin(pose["yaw"] - goal["yaw"]), math.cos(pose["yaw"] - goal["yaw"])))
        node.destroy_node()
        rclpy.shutdown()
    with output.open("x") as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")
    print(f"{report['status']} | report: {output}")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
