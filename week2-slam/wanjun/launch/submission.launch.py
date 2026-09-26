"""Run the local Burger simulator with the student's Nav2 overrides."""

from pathlib import Path
import tempfile

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction, RegisterEventHandler
from launch.event_handlers import OnShutdown
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
import yaml


def merge_parameters(base, overrides, prefix=""):
    """Reject misspelled keys instead of silently adding unused ROS parameters."""
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
    baseline = yaml.safe_load((student / "config/nav2_params.yaml").read_text())
    overrides = yaml.safe_load((student / "config/nav2_overrides.yaml").read_text())
    params = merge_parameters(baseline, overrides)
    with tempfile.NamedTemporaryFile(mode="w", prefix="wanjun_nav2_", suffix=".yaml", delete=False) as stream:
        yaml.safe_dump(params, stream, sort_keys=False)
        params_path = Path(stream.name)

    def cleanup(_context):
        params_path.unlink(missing_ok=True)

    return [
        RegisterEventHandler(OnShutdown(on_shutdown=[OpaqueFunction(function=cleanup)])),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(str(student / "launch/simulation.launch.py")),
            launch_arguments={
                "params_file": str(params_path),
                "headless": LaunchConfiguration("headless"),
                "use_rviz": LaunchConfiguration("use_rviz"),
            }.items(),
        ),
    ]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument("headless", default_value="False", choices=["True", "False"]),
        DeclareLaunchArgument("use_rviz", default_value="True", choices=["True", "False"]),
        OpaqueFunction(function=launch_setup),
    ])
