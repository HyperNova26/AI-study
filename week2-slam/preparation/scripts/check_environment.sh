#!/usr/bin/env bash
set -eo pipefail
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
source "$script_dir/env.sh"

python3 - "$script_dir/.." <<'PY'
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

import yaml
from ament_index_python.packages import get_package_share_directory
import xacro

root = Path(sys.argv[1]).resolve()
packages = [
    "nav2_bringup", "nav2_minimal_tb3_sim", "turtlebot3_description",
    "nav2_amcl", "nav2_map_server", "nav2_navfn_planner", "nav2_mppi_controller",
    "nav2_rviz_plugins", "ros_gz_sim", "ros_gz_bridge", "robot_state_publisher",
    "xacro", "rviz2", "tf2_ros", "tf2_tools",
]
missing = []
shares = {}
for package in packages:
    try:
        share = Path(get_package_share_directory(package))
        shares[package] = share
        version = ET.parse(share / "package.xml").findtext("version")
        print(f"OK {package}: {version}")
    except (LookupError, OSError) as error:
        missing.append(f"{package}: {error}")
if missing:
    sys.exit("\n".join(missing) + "\nscripts/install_dependencies.sh를 실행하세요.")

for path in (
    shares["nav2_bringup"] / "launch/bringup_launch.py",
    shares["nav2_minimal_tb3_sim"] / "worlds/tb3_sandbox.sdf.xacro",
    shares["nav2_minimal_tb3_sim"] / "models/turtlebot3_world/model.sdf",
    shares["turtlebot3_description"] / "urdf/turtlebot3_burger.urdf",
    root / "models/burger_sensors.urdf.xacro",
    root / "launch/simulation.launch.py",
):
    if not path.is_file():
        sys.exit(f"필수 파일이 없습니다: {path}")

robot = ET.fromstring(xacro.process_file(str(root / "models/burger_sensors.urdf.xacro")).toxml())
for mesh in robot.iter("mesh"):
    uri = mesh.attrib["filename"]
    if uri.startswith("package://"):
        package, relative = uri.removeprefix("package://").split("/", 1)
        path = Path(get_package_share_directory(package)) / relative
        if not path.is_file():
            sys.exit(f"모델 메시가 없습니다: {path}")
for sensor in robot.findall("gazebo/sensor"):
    print(f"OK sensor: {sensor.attrib['name']} ({sensor.attrib['type']}, {sensor.findtext('update_rate')} Hz target)")

for relative in ("maps/tb3_sandbox.yaml", "config/nav2_params.yaml", "rviz/practice.rviz"):
    with (root / relative).open() as stream:
        data = yaml.safe_load(stream)
    if not isinstance(data, dict):
        sys.exit(f"YAML 형식을 확인하세요: {relative}")
    if relative.startswith("maps/"):
        image = root / "maps" / data["image"]
        if not image.is_file():
            sys.exit(f"지도 이미지가 없습니다: {image}")
        print(f"OK map: {image.name}, {data['resolution']} m/pixel")
bridge = yaml.safe_load((root / "config/bridge.yaml").read_text())
if not isinstance(bridge, list):
    sys.exit("config/bridge.yaml은 브리지 항목 목록이어야 합니다.")
print("OK bridge topics:", ", ".join(entry.get("ros_topic_name", entry.get("topic_name")) for entry in bridge))
print("준비 파일 확인 완료. 실제 센서·TF 검사는 docs/sensors.md를 참고하세요.")
PY

printf 'ROS_DOMAIN_ID=%s, GZ_PARTITION=%s\n' "$ROS_DOMAIN_ID" "$GZ_PARTITION"
gz sim --versions
