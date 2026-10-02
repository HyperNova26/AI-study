"""Connect FAST-LIO2 to the week-3 simulation and show its odometry and map in RViz.

Start ../preparation/scripts/run_simulation.sh first and keep the robot still until FAST-LIO2
prints "IMU Initial Done": it estimates gravity and IMU biases from a static start.

* Parameters: ../preparation/config/fast_lio_burger.yaml merged with config/fast_lio_overrides.yaml
  (or another file: overrides_file:=config/experiments/voxel_0.2.yaml). With pcd_save_en, `ros2 service call /map_save std_srvs/srv/Trigger` writes results/fastlio_map.pcd.
* odom -> camera_init (static): camera_init is the IMU pose at the moment FAST-LIO2 starts. With the
  robot still at the odom origin that is imu_link in base_footprint, (-0.032, 0, 0.078) in the URDF.
  The link puts FAST-LIO2 (camera_init -> body) and wheel odometry (odom -> base_footprint) in one tree.
"""

from pathlib import Path
import tempfile

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction, RegisterEventHandler
from launch.event_handlers import OnShutdown
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
import yaml


def merge_parameters(base, overrides, prefix=""):
    """Reject misspelled keys instead of silently adding unused ROS parameters (week 2 approach)."""
    for key, value in overrides.items():
        path = f"{prefix}.{key}" if prefix else key
        if key not in base:
            raise ValueError(f"Unknown parameter: {path}")
        if isinstance(value, dict):
            if not isinstance(base[key], dict):
                raise ValueError(f"Parameter is not a mapping: {path}")
            merge_parameters(base[key], value, path)
        else:
            base[key] = value
    return base


def launch_setup(context):
    student = Path(__file__).resolve().parents[1]
    preparation = student.parent / "preparation"
    baseline = yaml.safe_load((preparation / "config/fast_lio_burger.yaml").read_text())
    overrides_file = Path(LaunchConfiguration("overrides_file").perform(context)).expanduser().resolve()
    overrides = yaml.safe_load(overrides_file.read_text()) or {}
    params = merge_parameters(baseline, overrides)
    node_params = params["/**"]["ros__parameters"]
    if node_params["pcd_save"]["pcd_save_en"] and not node_params["map_file_path"]:
        # /map_save writes here; FAST-LIO2 does not create missing directories.
        (student / "results").mkdir(exist_ok=True)
        node_params["map_file_path"] = str(student / "results" / "fastlio_map.pcd")
    with tempfile.NamedTemporaryFile(mode="w", prefix="hj1_fast_lio_", suffix=".yaml", delete=False) as stream:
        yaml.safe_dump(params, stream, sort_keys=False)
        params_path = Path(stream.name)

    def cleanup(_context):
        params_path.unlink(missing_ok=True)

    actions = [
        RegisterEventHandler(OnShutdown(on_shutdown=[OpaqueFunction(function=cleanup)])),
        Node(
            package="tf2_ros", executable="static_transform_publisher", name="odom_to_camera_init",
            arguments=["--x", "-0.032", "--y", "0.0", "--z", "0.078",
                       "--frame-id", "odom", "--child-frame-id", "camera_init"],
        ),
        Node(
            package="fast_lio", executable="fastlio_mapping", name="laser_mapping", output="screen",
            parameters=[str(params_path), {"use_sim_time": True}],
        ),
    ]
    if LaunchConfiguration("use_rviz").perform(context) == "True":
        actions.append(Node(
            package="rviz2", executable="rviz2", name="rviz2", output="screen",
            arguments=["-d", str(student / "rviz/fast_lio.rviz")],
            parameters=[{"use_sim_time": True}],
        ))
    return actions


def generate_launch_description():
    student = Path(__file__).resolve().parents[1]
    return LaunchDescription([
        DeclareLaunchArgument("use_rviz", default_value="True", choices=["True", "False"],
                              description="Open rviz/fast_lio.rviz."),
        DeclareLaunchArgument("overrides_file", default_value=str(student / "config/fast_lio_overrides.yaml"),
                              description="Changes merged into the provided FAST-LIO2 config, e.g. config/experiments/*.yaml"),
        OpaqueFunction(function=launch_setup),
    ])
