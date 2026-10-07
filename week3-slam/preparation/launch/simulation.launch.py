"""Run Burger with a 2D LDS, 16-channel 3D LiDAR and IMU for FAST-LIO2 practice.

Same robot, sandbox world and bridge as week 2 (week2-slam/wanjun), without Nav2:
the robot is driven with teleop, so no map, AMCL or `map` frame is started. The 3D LiDAR
cloud is also republished on /points_fastlio by tools/points_to_fastlio.py.
"""

from pathlib import Path
import sys
import tempfile
import xml.etree.ElementTree as ET

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    AppendEnvironmentVariable, DeclareLaunchArgument, ExecuteProcess, OpaqueFunction,
    RegisterEventHandler,
)
from launch.event_handlers import OnShutdown
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
import xacro


def launch_setup(context):
    root = Path(__file__).resolve().parents[1]
    simulation = Path(get_package_share_directory("nav2_minimal_tb3_sim"))
    description = Path(get_package_share_directory("turtlebot3_description"))
    headless = LaunchConfiguration("headless").perform(context)
    use_rviz = LaunchConfiguration("use_rviz").perform(context)
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
    with tempfile.NamedTemporaryFile(mode="w", prefix="aistudy_week3_", suffix=".sdf", delete=False) as world:
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
        # A plain script keeps this folder usable without building a ROS package. sys.executable is
        # the interpreter running `ros2 launch`, so an active venv/conda python cannot be picked up.
        ExecuteProcess(
            cmd=[sys.executable, str(root / "tools/points_to_fastlio.py"), "--ros-args",
                 "-p", "use_sim_time:=true", "-p", "input_topic:=/points",
                 "-p", "output_topic:=/points_fastlio", "-p", "min_range:=0.10"],
            name="points_to_fastlio", output="screen",
        ),
    ]
    if headless == "False":
        actions.append(ExecuteProcess(cmd=["gz", "sim", "-g"], output="screen"))
    if use_rviz == "True":
        actions.append(Node(
            package="rviz2", executable="rviz2", name="rviz2", output="screen",
            arguments=["-d", str(root / "rviz/sensors.rviz")],
            parameters=[{"use_sim_time": True}],
        ))
    return actions


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument("headless", default_value="False", choices=["True", "False"],
                              description="Hide the Gazebo GUI; sensors still need rendering."),
        DeclareLaunchArgument("use_rviz", default_value="True", choices=["True", "False"],
                              description="Open the sensor check RViz view (rviz/sensors.rviz)."),
        OpaqueFunction(function=launch_setup),
    ])
