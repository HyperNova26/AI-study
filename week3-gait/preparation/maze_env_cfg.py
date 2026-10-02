"""Load a maze USD into the Isaac Lab Go2 flat locomotion task for ROS 2 teleop.

Based on week2-gait/ChanwonJung/maze_env_cfg.py (Isaac Lab v3.0.0-beta2). Week 3 changes:
the maze USD and spawn pose are runtime options, and the reset events no longer randomize the
start pose, so the robot always starts at the given spawn pose and heading.
"""

from __future__ import annotations

import math
from pathlib import Path

import isaaclab.sim as sim_utils
from isaaclab.assets import AssetBaseCfg
from isaaclab.utils.configclass import configclass
from isaaclab_tasks.manager_based.locomotion.velocity.config.go2.flat_env_cfg import (
    UnitreeGo2FlatEnvCfg_PLAY,
)

SAMPLE_MAZE_USD = Path(__file__).resolve().parent / "assets" / "sample_maze.usda"
SAMPLE_MAZE_SPAWN = (-3.0, -2.0, 0.42)  # south-west corridor of assets/sample_maze.usda, facing +x


def maze_asset_cfg(usd_path: str | Path) -> AssetBaseCfg:
    """Static maze walls with collisions, as in the week-2 example."""
    return AssetBaseCfg(
        prim_path="{ENV_REGEX_NS}/Maze",
        spawn=sim_utils.UsdFileCfg(
            usd_path=str(usd_path),
            collision_props=sim_utils.CollisionPropertiesCfg(collision_enabled=True),
            physics_material=sim_utils.RigidBodyMaterialCfg(
                static_friction=0.8, dynamic_friction=0.7, restitution=0.0
            ),
            visual_material=sim_utils.PreviewSurfaceCfg(
                diffuse_color=(0.18, 0.42, 0.72), metallic=0.05, roughness=0.75
            ),
        ),
    )


@configclass
class Go2MazeEnvCfg(UnitreeGo2FlatEnvCfg_PLAY):
    """Single Go2 on a flat floor inside a referenced maze; ROS 2 owns the velocity command."""

    def __post_init__(self):
        super().__post_init__()

        self.scene.num_envs = 1
        self.scene.env_spacing = 12.0
        self.episode_length_s = 60.0 * 60.0
        self.viewer.eye = (7.5, -9.0, 8.5)
        self.viewer.lookat = (0.0, 0.0, 0.0)
        self.scene.robot.init_state.pos = SAMPLE_MAZE_SPAWN

        # ROS 2 owns the velocity command. Prevent random command changes (same as week 2).
        self.commands.base_velocity.heading_command = False
        self.commands.base_velocity.rel_heading_envs = 0.0
        self.commands.base_velocity.rel_standing_envs = 0.0
        self.commands.base_velocity.resampling_time_range = (1.0e9, 1.0e9)
        self.commands.base_velocity.ranges.lin_vel_x = (0.0, 0.0)
        self.commands.base_velocity.ranges.lin_vel_y = (0.0, 0.0)
        self.commands.base_velocity.ranges.ang_vel_z = (0.0, 0.0)
        self.commands.base_velocity.ranges.heading = None

        # Training resets the robot at a random offset (+-0.5 m) and heading (+-pi); in a maze that can
        # start it facing a wall. Missing pose/velocity keys mean "no offset" for reset_root_state_uniform.
        self.events.reset_base.params["pose_range"] = {}
        self.events.reset_base.params["velocity_range"] = {}
        self.events.reset_robot_joints.params["position_range"] = (1.0, 1.0)

        self.curriculum = None
        self.scene.maze = maze_asset_cfg(SAMPLE_MAZE_USD)


def apply_maze_options(cfg: Go2MazeEnvCfg, maze_usd: str | Path, spawn_xyz, spawn_yaw_deg: float) -> Go2MazeEnvCfg:
    """Select the maze USD and the spawn pose (heading in degrees, 0 = +x)."""
    cfg.scene.maze = maze_asset_cfg(Path(maze_usd).expanduser().resolve())
    cfg.scene.robot.init_state.pos = tuple(float(v) for v in spawn_xyz)
    yaw = math.radians(spawn_yaw_deg)
    cfg.events.reset_base.params["pose_range"] = {"yaw": (yaw, yaw)}
    return cfg
