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

root = Path(sys.argv[1]).resolve()
packages = [
    "nav2_bringup", "nav2_minimal_tb3_sim", "nav2_amcl", "nav2_map_server",
    "nav2_navfn_planner", "nav2_mppi_controller", "nav2_rviz_plugins",
    "ros_gz_sim", "ros_gz_bridge", "robot_state_publisher", "xacro",
    "rviz2", "tf2_ros", "tf2_tools",
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

files = [
    shares["nav2_bringup"] / "launch/tb3_simulation_launch.py",
    shares["nav2_minimal_tb3_sim"] / "worlds/tb3_sandbox.sdf.xacro",
    shares["nav2_minimal_tb3_sim"] / "urdf/gz_waffle.sdf.xacro",
    shares["nav2_minimal_tb3_sim"] / "urdf/turtlebot3_waffle.urdf",
    shares["nav2_minimal_tb3_sim"] / "models/turtlebot3_world/model.sdf",
    root / "launch/simulation.launch.py",
]
files.extend(
    shares["nav2_minimal_tb3_sim"] / "models/turtlebot3_model/meshes" / mesh
    for mesh in ("waffle_base.dae", "tire.dae", "lds.dae", "r200.dae")
)
for path in files:
    if not path.is_file():
        sys.exit(f"필수 파일이 없습니다: {path}")
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
print("준비 파일과 패키지 확인 완료. 실행 후 센서·TF 확인은 README를 참고하세요.")
PY

printf 'ROS_DOMAIN_ID=%s, GZ_PARTITION=%s\n' "$ROS_DOMAIN_ID" "$GZ_PARTITION"
gz sim --versions
