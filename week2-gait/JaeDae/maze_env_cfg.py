"""Isaac Lab PLAY environment for JaeDae's custom Go2 maze."""

from __future__ import annotations

import math
from pathlib import Path

import isaaclab.sim as sim_utils
from isaaclab.assets import AssetBaseCfg
from isaaclab.utils.configclass import configclass
from isaaclab_tasks.manager_based.locomotion.velocity.config.go2.flat_env_cfg import (
    UnitreeGo2FlatEnvCfg_PLAY,
)

MAZE_USD = Path(__file__).resolve().parent / "assets" / "jaedae_maze.usda"
SPAWN = (-4.25, -3.25, 0.42)  # lower-left lane, initially facing +x


def maze_cfg(usd_path: str | Path = MAZE_USD) -> AssetBaseCfg:
    """Reference static USDA walls with contact friction appropriate for Go2."""
    return AssetBaseCfg(
        prim_path="{ENV_REGEX_NS}/JaeDaeMaze",
        spawn=sim_utils.UsdFileCfg(
            usd_path=str(Path(usd_path).expanduser().resolve()),
            collision_props=sim_utils.CollisionPropertiesCfg(collision_enabled=True),
            physics_material=sim_utils.RigidBodyMaterialCfg(
                static_friction=0.8, dynamic_friction=0.7, restitution=0.0
            ),
            visual_material=sim_utils.PreviewSurfaceCfg(
                diffuse_color=(0.15, 0.55, 0.34), metallic=0.0, roughness=0.8
            ),
        ),
    )


@configclass
class JaeDaeMazeEnvCfg(UnitreeGo2FlatEnvCfg_PLAY):
    """One deterministic Go2 environment; ROS owns its velocity command."""

    def __post_init__(self) -> None:
        super().__post_init__()
        self.scene.num_envs = 1
        self.scene.env_spacing = 14.0
        self.episode_length_s = 60.0 * 60.0
        self.viewer.eye = (9.5, -11.5, 10.0)
        self.viewer.lookat = (0.0, 0.0, 0.0)
        self.scene.robot.init_state.pos = SPAWN
        self.scene.maze = maze_cfg()

        # Do not let training-time command sampling or random reset poses fight teleop.
        command = self.commands.base_velocity
        command.heading_command = False
        command.rel_heading_envs = 0.0
        command.rel_standing_envs = 0.0
        command.resampling_time_range = (1.0e9, 1.0e9)
        command.ranges.lin_vel_x = (0.0, 0.0)
        command.ranges.lin_vel_y = (0.0, 0.0)
        command.ranges.ang_vel_z = (0.0, 0.0)
        command.ranges.heading = None
        self.events.reset_base.params["pose_range"] = {"yaw": (0.0, 0.0)}
        self.events.reset_base.params["velocity_range"] = {}
        self.events.reset_robot_joints.params["position_range"] = (1.0, 1.0)
        self.curriculum = None


def set_spawn(cfg: JaeDaeMazeEnvCfg, xyz: tuple[float, float, float], yaw_degrees: float) -> None:
    """Optional fixed spawn override for repeatable testing."""
    cfg.scene.robot.init_state.pos = tuple(float(value) for value in xyz)
    yaw = math.radians(yaw_degrees)
    cfg.events.reset_base.params["pose_range"] = {"yaw": (yaw, yaw)}
