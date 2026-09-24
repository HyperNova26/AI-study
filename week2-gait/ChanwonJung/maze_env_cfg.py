"""Load the submitted USD maze into the Isaac Lab Go2 locomotion task."""

from __future__ import annotations

from pathlib import Path

import isaaclab.sim as sim_utils
from isaaclab.assets import AssetBaseCfg
from isaaclab.utils.configclass import configclass
from isaaclab_tasks.manager_based.locomotion.velocity.config.go2.flat_env_cfg import (
    UnitreeGo2FlatEnvCfg_PLAY,
)


MAZE_USD_PATH = Path(__file__).resolve().parent / "assets" / "go2_maze.usda"

MAZE_CFG = AssetBaseCfg(
    prim_path="{ENV_REGEX_NS}/Maze",
    spawn=sim_utils.UsdFileCfg(
        usd_path=str(MAZE_USD_PATH),
        collision_props=sim_utils.CollisionPropertiesCfg(collision_enabled=True),
        physics_material=sim_utils.RigidBodyMaterialCfg(
            static_friction=0.8,
            dynamic_friction=0.7,
            restitution=0.0,
        ),
        visual_material=sim_utils.PreviewSurfaceCfg(
            diffuse_color=(0.18, 0.42, 0.72), metallic=0.05, roughness=0.75
        ),
    ),
)


@configclass
class Go2MazeEnvCfg(UnitreeGo2FlatEnvCfg_PLAY):
    """Single-environment Go2 scene with a flat floor and a referenced USD maze."""

    def __post_init__(self):
        super().__post_init__()

        self.scene.num_envs = 1
        self.scene.env_spacing = 12.0
        self.episode_length_s = 60.0 * 60.0
        self.viewer.eye = (7.5, -9.0, 8.5)
        self.viewer.lookat = (0.0, 0.0, 0.0)

        # Spawn in the south-west part of the maze, facing +x.
        self.scene.robot.init_state.pos = (-4.15, -3.2, 0.42)

        # ROS 2 owns the velocity command. Prevent random command changes.
        self.commands.base_velocity.heading_command = False
        self.commands.base_velocity.rel_heading_envs = 0.0
        self.commands.base_velocity.rel_standing_envs = 0.0
        self.commands.base_velocity.resampling_time_range = (1.0e9, 1.0e9)
        self.commands.base_velocity.ranges.lin_vel_x = (0.0, 0.0)
        self.commands.base_velocity.ranges.lin_vel_y = (0.0, 0.0)
        self.commands.base_velocity.ranges.ang_vel_z = (0.0, 0.0)
        self.commands.base_velocity.ranges.heading = None

        self.curriculum = None
        self.scene.maze = MAZE_CFG
