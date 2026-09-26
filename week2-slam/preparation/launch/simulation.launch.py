"""Launch the shared Week 2 TurtleBot3 Waffle practice environment."""

from pathlib import Path
import xml.etree.ElementTree as ET

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def waffle_description(simulation):
    """Resolve the misplaced mesh references shipped in TB3 sim 1.0.1."""
    robot = ET.fromstring((simulation / "urdf/turtlebot3_waffle.urdf").read_text())
    prefix = "package://nav2_minimal_tb3_sim/"
    for mesh in robot.iter("mesh"):
        uri = mesh.attrib["filename"]
        if uri.startswith(prefix) and not (simulation / uri[len(prefix):]).is_file():
            resource = simulation / "models/turtlebot3_model/meshes" / Path(uri).name
            if not resource.is_file():
                raise FileNotFoundError(f"TurtleBot3 mesh is missing: {resource}")
            mesh.set("filename", resource.as_uri())
    return ET.tostring(robot, encoding="unicode")


def generate_launch_description():
    preparation = Path(__file__).resolve().parents[1]
    bringup = Path(get_package_share_directory("nav2_bringup"))
    simulation = Path(get_package_share_directory("nav2_minimal_tb3_sim"))

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="screen",
        parameters=[{
            "use_sim_time": True,
            "robot_description": waffle_description(simulation),
        }],
    )

    arguments = [
        DeclareLaunchArgument(
            "headless", default_value="False", choices=["True", "False"],
            description="Hide the Gazebo GUI (sensors still need rendering).",
        ),
        DeclareLaunchArgument(
            "use_rviz", default_value="True", choices=["True", "False"],
            description="Open the practice RViz view.",
        ),
        DeclareLaunchArgument(
            "params_file", default_value=str(preparation / "config/nav2_params.yaml"),
            description="Full path to a Nav2 Jazzy parameter file.",
        ),
    ]

    # The upstream launch provides the model, ROS/Gazebo bridges, AMCL and Nav2.
    # Keep this map/world pair and spawn pose together for a common starting point.
    simulation_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(str(bringup / "launch/tb3_simulation_launch.py")),
        launch_arguments={
            "headless": LaunchConfiguration("headless"),
            "use_rviz": LaunchConfiguration("use_rviz"),
            "params_file": LaunchConfiguration("params_file"),
            "map": str(preparation / "maps/tb3_sandbox.yaml"),
            "world": str(simulation / "worlds/tb3_sandbox.sdf.xacro"),
            "robot_sdf": str(simulation / "urdf/gz_waffle.sdf.xacro"),
            "rviz_config_file": str(preparation / "rviz/practice.rviz"),
            "robot_name": "turtlebot3_waffle",
            "use_robot_state_pub": "False",
            "use_sim_time": "True",
            "slam": "False",
            "autostart": "True",
            "use_composition": "True",
            "x_pose": "-2.0",
            "y_pose": "-0.5",
            "z_pose": "0.01",
            "yaw": "0.0",
        }.items(),
    )
    return LaunchDescription([*arguments, robot_state_publisher, simulation_launch])
