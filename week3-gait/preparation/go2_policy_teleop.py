"""Teleoperate a Go2 walking policy in a maze with ROS 2 Twist commands (week 3).

Based on week2-gait/ChanwonJung/go2_maze_ros2.py, which runs on Isaac Sim 6.0.1, Isaac Lab
v3.0.0-beta2 and RSL-RL 5.0.1. Week 3 adds:

* --policy: run an exported TorchScript policy (<run>/exported/policy.pt). The scripted model takes
  the 48-D "policy" observation tensor, so it is called as policy(obs["policy"]).
* --checkpoint / default: the week-2 path. An RSL-RL training checkpoint, or the published
  pretrained Go2 flat checkpoint (the provided policy) when neither option is given.
* --maze-usd / --spawn / --spawn-yaw: any week-2 maze USD and start pose.
* A periodic line comparing the commanded and measured base velocity.

The simulator subscribes to geometry_msgs/msg/Twist on /cmd_vel. The message is interpreted in the
Go2 base frame and written into the policy command [linear.x, linear.y, angular.z].
"""

from __future__ import annotations

import argparse
from pathlib import Path

from isaaclab.app import AppLauncher

HERE = Path(__file__).resolve().parent

parser = argparse.ArgumentParser(description="ROS 2 teleoperation of a Go2 walking policy in a maze")
policy_source = parser.add_mutually_exclusive_group()
policy_source.add_argument("--policy", default=None, help="Exported TorchScript policy (<run>/exported/policy.pt)")
policy_source.add_argument("--checkpoint", default=None,
                           help="RSL-RL training checkpoint (model_<iter>.pt); default: published pretrained policy")
parser.add_argument("--maze-usd", default=str(HERE / "assets" / "sample_maze.usda"), help="Maze USD/USDA file")
parser.add_argument("--spawn", type=float, nargs=3, default=None, metavar=("X", "Y", "Z"),
                    help="Base start position in m (default: sample maze start)")
parser.add_argument("--spawn-yaw", type=float, default=0.0, help="Start heading in degrees, 0 = +x")
parser.add_argument("--cmd-vel-topic", default="/cmd_vel", help="geometry_msgs/Twist input topic")
parser.add_argument("--command-timeout", type=float, default=0.5, help="Stop after this many seconds without a Twist")
parser.add_argument("--max-linear-x", type=float, default=0.8, help="Absolute linear.x limit in m/s")
parser.add_argument("--max-linear-y", type=float, default=0.4, help="Absolute linear.y limit in m/s")
parser.add_argument("--max-angular-z", type=float, default=1.0, help="Absolute angular.z limit in rad/s")
parser.add_argument("--status-period", type=float, default=2.0,
                    help="Seconds between command/velocity printouts (0 disables)")
parser.add_argument("--no-real-time", action="store_true", help="Do not throttle simulation to wall-clock time")
AppLauncher.add_app_launcher_args(parser)
# Open the Kit GUI by default (Isaac Lab 3.0 is headless unless a visualizer is selected); --viz none hides it.
parser.set_defaults(visualizer=["kit"])
args_cli = parser.parse_args()

app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

# Isaac/Omniverse imports must happen after AppLauncher starts Kit.
import hashlib
import time
from importlib import metadata

import torch
from rsl_rl.runners import OnPolicyRunner

try:
    import rclpy
    from geometry_msgs.msg import Twist
    from rclpy.node import Node
    from rclpy.qos import QoSProfile, ReliabilityPolicy
except ImportError as exc:
    simulation_app.close()
    raise RuntimeError(
        "ROS 2 Python modules are unavailable. Start this script with scripts/run_teleop_policy.sh, "
        "which points PYTHONPATH at Isaac Sim's bundled ROS 2 Jazzy rclpy. See README.md."
    ) from exc

from isaaclab.envs import ManagerBasedRLEnv
from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper, handle_deprecated_rsl_rl_cfg
from isaaclab_rl.utils.pretrained_checkpoint import get_published_pretrained_checkpoint
from isaaclab_tasks.manager_based.locomotion.velocity.config.go2.agents.rsl_rl_ppo_cfg import (
    UnitreeGo2FlatPPORunnerCfg,
)
from isaaclab_tasks.utils.hydra import resolve_presets

from maze_env_cfg import SAMPLE_MAZE_SPAWN, Go2MazeEnvCfg, apply_maze_options


TASK = "Isaac-Velocity-Flat-Unitree-Go2-v0"
RL_LIBRARY = "rsl_rl"


class CmdVelSubscriber(Node):
    """Store the newest bounded Twist command and apply a dead-man timeout."""

    def __init__(self) -> None:
        super().__init__("go2_maze_cmd_vel")
        self._command = torch.zeros(3, dtype=torch.float32)
        self._last_message_time: float | None = None
        qos = QoSProfile(depth=1, reliability=ReliabilityPolicy.RELIABLE)
        self.create_subscription(Twist, args_cli.cmd_vel_topic, self._on_twist, qos)
        self.get_logger().info(
            f"Listening on {args_cli.cmd_vel_topic}; timeout={args_cli.command_timeout:.2f}s"
        )

    def _on_twist(self, msg: Twist) -> None:
        self._command[0] = max(-args_cli.max_linear_x, min(args_cli.max_linear_x, msg.linear.x))
        self._command[1] = max(-args_cli.max_linear_y, min(args_cli.max_linear_y, msg.linear.y))
        self._command[2] = max(-args_cli.max_angular_z, min(args_cli.max_angular_z, msg.angular.z))
        self._last_message_time = time.monotonic()

    def command(self) -> torch.Tensor:
        if self._last_message_time is None:
            return torch.zeros_like(self._command)
        if time.monotonic() - self._last_message_time > args_cli.command_timeout:
            return torch.zeros_like(self._command)
        return self._command


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]


def _load_policy(env: RslRlVecEnvWrapper):
    """Return (policy, description); the policy maps the observation TensorDict to joint actions."""
    device = env.unwrapped.device
    if args_cli.policy is not None:
        path = Path(args_cli.policy).expanduser().resolve()
        # play saves the TorchScript file on CPU; move it to the simulation device.
        scripted = torch.jit.load(str(path), map_location=device)
        scripted.eval()
        return (lambda obs: scripted(obs["policy"])), f"exported TorchScript {path} (sha256 {_sha256(path)})"

    agent_cfg = resolve_presets(UnitreeGo2FlatPPORunnerCfg())
    agent_cfg = handle_deprecated_rsl_rl_cfg(agent_cfg, metadata.version("rsl-rl-lib"))
    checkpoint = args_cli.checkpoint
    if checkpoint is None:
        checkpoint = get_published_pretrained_checkpoint(RL_LIBRARY, TASK)
    if not checkpoint:
        raise RuntimeError(
            "No published checkpoint was found for the Go2 flat task. "
            "Pass --policy exported/policy.pt or --checkpoint model_<iter>.pt."
        )
    runner = OnPolicyRunner(env, agent_cfg.to_dict(), log_dir=None, device=device)
    runner.load(checkpoint)
    return runner.get_inference_policy(device=device), f"RSL-RL checkpoint {checkpoint}"


def main() -> None:
    rclpy.init()
    node = CmdVelSubscriber()
    env = None

    try:
        env_cfg = resolve_presets(Go2MazeEnvCfg())
        apply_maze_options(env_cfg, args_cli.maze_usd, args_cli.spawn or SAMPLE_MAZE_SPAWN, args_cli.spawn_yaw)
        if args_cli.device is not None:
            env_cfg.sim.device = args_cli.device
        env = RslRlVecEnvWrapper(ManagerBasedRLEnv(cfg=env_cfg))
        policy, description = _load_policy(env)
        print(f"[INFO] Go2 policy: {description}")
        print(f"[INFO] Maze: {Path(args_cli.maze_usd).expanduser().resolve()}")

        command_buffer = env.unwrapped.command_manager.get_command("base_velocity")
        command_buffer.zero_()
        obs = env.get_observations()
        next_status = time.monotonic()

        print("[INFO] Go2 maze is ready. Publish geometry_msgs/Twist on", args_cli.cmd_vel_topic)
        with torch.inference_mode():
            while simulation_app.is_running() and rclpy.ok():
                step_start = time.monotonic()
                # Process any queued ROS callback without blocking simulation.
                rclpy.spin_once(node, timeout_sec=0.0)

                # Write the ROS command before inference and again after env.step(),
                # because CommandManager may update its internal command each step.
                command_buffer[0].copy_(node.command().to(command_buffer.device))
                obs = env.get_observations()
                actions = policy(obs)
                _, _, _, _ = env.step(actions)
                command_buffer[0].copy_(node.command().to(command_buffer.device))
                obs = env.get_observations()

                if args_cli.status_period > 0 and step_start >= next_status:
                    # policy obs layout: base_lin_vel[0:3], base_ang_vel[3:6], ..., velocity_commands[9:12]
                    measured = obs["policy"][0].tolist()
                    cmd = command_buffer[0].tolist()
                    print(f"[STATUS] cmd vx={cmd[0]:+.2f} vy={cmd[1]:+.2f} wz={cmd[2]:+.2f} | "
                          f"measured vx={measured[0]:+.2f} vy={measured[1]:+.2f} wz={measured[5]:+.2f}")
                    next_status = step_start + args_cli.status_period
                if not args_cli.no_real_time:
                    sleep_time = env.unwrapped.step_dt - (time.monotonic() - step_start)
                    if sleep_time > 0.0:
                        time.sleep(sleep_time)
    except KeyboardInterrupt:
        print("\n[INFO] Stopping Go2 maze teleoperation")
    finally:
        # Stop is local to the policy command and does not publish to other robots.
        if env is not None:
            env.unwrapped.command_manager.get_command("base_velocity").zero_()
            env.close()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    try:
        main()
    finally:
        simulation_app.close()
