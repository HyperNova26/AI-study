#!/usr/bin/env python3
"""Run JaeDae's Go2 maze with a TorchScript policy and ROS 2 /cmd_vel input."""

from __future__ import annotations

import argparse
import time
from pathlib import Path

from isaaclab.app import AppLauncher

HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description="JaeDae Go2 maze ROS 2 teleoperation")
parser.add_argument("--policy", required=True, help="48->12 TorchScript policy.pt exported in week 3")
parser.add_argument("--cmd-vel-topic", default="/cmd_vel")
parser.add_argument("--command-timeout", type=float, default=0.5)
parser.add_argument("--max-linear-x", type=float, default=0.8)
parser.add_argument("--max-linear-y", type=float, default=0.4)
parser.add_argument("--max-angular-z", type=float, default=1.0)
parser.add_argument("--status-period", type=float, default=2.0)
parser.add_argument("--no-real-time", action="store_true")
AppLauncher.add_app_launcher_args(parser)
parser.set_defaults(visualizer=["kit"])
args = parser.parse_args()
simulation_app = AppLauncher(args).app

# Isaac Sim and ROS modules must be imported only after Kit starts.
import torch
import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy

from isaaclab.envs import ManagerBasedRLEnv
from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper
from isaaclab_tasks.utils.hydra import resolve_presets

from maze_env_cfg import JaeDaeMazeEnvCfg


class CommandReceiver(Node):
    """Keep the latest bounded Twist and return zero when the publisher goes quiet."""

    def __init__(self) -> None:
        super().__init__("jaedae_go2_maze_cmd_vel")
        self.value = torch.zeros(3, dtype=torch.float32)
        self.received_at: float | None = None
        qos = QoSProfile(depth=1, reliability=ReliabilityPolicy.RELIABLE)
        self.create_subscription(Twist, args.cmd_vel_topic, self.callback, qos)
        self.get_logger().info(f"Listening on {args.cmd_vel_topic}; dead-man {args.command_timeout:.1f}s")

    def callback(self, message: Twist) -> None:
        self.value[0] = max(-args.max_linear_x, min(args.max_linear_x, message.linear.x))
        self.value[1] = max(-args.max_linear_y, min(args.max_linear_y, message.linear.y))
        self.value[2] = max(-args.max_angular_z, min(args.max_angular_z, message.angular.z))
        self.received_at = time.monotonic()

    def current(self) -> torch.Tensor:
        if self.received_at is None or time.monotonic() - self.received_at > args.command_timeout:
            return torch.zeros_like(self.value)
        return self.value


def main() -> None:
    policy_path = Path(args.policy).expanduser().resolve()
    if not policy_path.is_file():
        raise FileNotFoundError(f"Policy not found: {policy_path}")
    rclpy.init()
    receiver = CommandReceiver()
    env = None
    try:
        cfg = resolve_presets(JaeDaeMazeEnvCfg())
        if args.device is not None:
            cfg.sim.device = args.device
        env = RslRlVecEnvWrapper(ManagerBasedRLEnv(cfg=cfg))
        policy = torch.jit.load(str(policy_path), map_location=env.unwrapped.device).eval()
        command = env.unwrapped.command_manager.get_command("base_velocity")
        command.zero_()
        env.get_observations()
        next_status = time.monotonic()
        print(f"[INFO] Policy: {policy_path}")
        print(f"[INFO] Maze: {HERE / 'assets' / 'jaedae_three_turn_maze.usda'}")
        print("[INFO] Go2 maze is ready. Start teleop in a second terminal.")
        with torch.inference_mode():
            while simulation_app.is_running() and rclpy.ok():
                start = time.monotonic()
                rclpy.spin_once(receiver, timeout_sec=0.0)
                command[0].copy_(receiver.current().to(command.device))
                observations = env.get_observations()
                env.step(policy(observations["policy"]))
                command[0].copy_(receiver.current().to(command.device))
                observations = env.get_observations()
                if args.status_period and start >= next_status:
                    measured, requested = observations["policy"][0].tolist(), command[0].tolist()
                    print(f"[STATUS] cmd vx={requested[0]:+.2f} wz={requested[2]:+.2f} | "
                          f"measured vx={measured[0]:+.2f} wz={measured[5]:+.2f}")
                    next_status = start + args.status_period
                if not args.no_real_time:
                    time.sleep(max(0.0, env.unwrapped.step_dt - (time.monotonic() - start)))
    except KeyboardInterrupt:
        print("\n[INFO] Stopping Go2 maze teleoperation")
    finally:
        if env is not None:
            env.unwrapped.command_manager.get_command("base_velocity").zero_()
            env.close()
        receiver.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    try:
        main()
    finally:
        simulation_app.close()
