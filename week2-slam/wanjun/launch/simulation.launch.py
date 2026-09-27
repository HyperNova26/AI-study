"""Run Burger with a 2D LDS, 16-channel 3D LiDAR, IMU and Nav2 Jazzy."""

from pathlib import Path
import tempfile
import xml.etree.ElementTree as ET

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    AppendEnvironmentVariable, DeclareLaunchArgument, ExecuteProcess,
    IncludeLaunchDescription, OpaqueFunction, RegisterEventHandler,
)
from launch.event_handlers import OnShutdown
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
import xacro


def launch_setup(context):
    root = Path(__file__).resolve().parents[1]
    bringup = Path(get_package_share_directory("nav2_bringup"))
    simulation = Path(get_package_share_directory("nav2_minimal_tb3_sim"))
    description = Path(get_package_share_directory("turtlebot3_description"))
    headless = LaunchConfiguration("headless").perform(context)
    use_rviz = LaunchConfiguration("use_rviz").perform(context)
    params = LaunchConfiguration("params_file").perform(context)
    robot_xml = xacro.process_file(str(root / "models/burger_sensors.urdf.xacro")).toxml()
    world_xml = xacro.process_file(
        str(simulation / "worlds/tb3_sandbox.sdf.xacro"),
        mappings={"headless": headless},
    ).toxml()
    # A 1 ms step can represent the 200 Hz IMU period without 3 ms quantization.
    world_tree = ET.fromstring(world_xml)
    world_tree.find("world/physics/max_step_size").text = "0.001"
    world_xml = ET.tostring(world_tree, encoding="unicode")
    # Finish writing the world before Gazebo starts, and remove it on shutdown.
    with tempfile.NamedTemporaryFile(mode="w", prefix="aistudy_week2_", suffix=".sdf", delete=False) as world:
        world.write(world_xml)
        world_path = Path(world.name)

    def cleanup(_context):
        world_path.unlink(missing_ok=True)

    actions = [
        AppendEnvironmentVariable("GZ_SIM_RESOURCE_PATH", str(simulation / "models")),
        AppendEnvironmentVariable("GZ_SIM_RESOURCE_PATH", str(description.parent)),
        RegisterEventHandler(OnShutdown(on_shutdown=[OpaqueFunction(function=cleanup)])),
        ExecuteProcess(cmd=["gz", "sim", "-r", "-s", str(world_path)], output="screen"),
        Node(
            package="robot_state_publisher", executable="robot_state_publisher",
            name="robot_state_publisher", output="screen",
            parameters=[{"use_sim_time": True, "robot_description": robot_xml}],
        ),
        Node(
            package="ros_gz_sim", executable="create", name="spawn_burger", output="screen",
            arguments=["-world", "default", "-name", "turtlebot3_burger", "-string", robot_xml,
                       "-x", "-2.0", "-y", "-0.5", "-z", "0.01", "-Y", "0.0"],
        ),
        Node(
            package="ros_gz_bridge", executable="parameter_bridge", name="gazebo_bridge",
            output="screen", parameters=[{
                "use_sim_time": True, "config_file": str(root / "config/bridge.yaml"),
            }],
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(str(bringup / "launch/bringup_launch.py")),
            launch_arguments={
                "map": str(root / "maps/tb3_sandbox.yaml"), "params_file": params,
                "use_sim_time": "True", "slam": "False", "autostart": "True",
                "use_composition": "False",
            }.items(),
        ),
    ]
    if headless == "False":
        actions.append(ExecuteProcess(cmd=["gz", "sim", "-g"], output="screen"))
    if use_rviz == "True":
        actions.append(IncludeLaunchDescription(
            PythonLaunchDescriptionSource(str(bringup / "launch/rviz_launch.py")),
            launch_arguments={"use_sim_time": "True", "rviz_config": str(root / "rviz/practice.rviz")}.items(),
        ))
    return actions


def generate_launch_description():
    root = Path(__file__).resolve().parents[1]
    return LaunchDescription([
        DeclareLaunchArgument("headless", default_value="False", choices=["True", "False"],
                              description="Hide the Gazebo GUI; sensors still need rendering."),
        DeclareLaunchArgument("use_rviz", default_value="True", choices=["True", "False"],
                              description="Open the practice RViz view."),
        DeclareLaunchArgument("params_file", default_value=str(root / "config/nav2_params.yaml"),
                              description="Full path to a Nav2 Jazzy parameter file."),
        OpaqueFunction(function=launch_setup),
    ])
