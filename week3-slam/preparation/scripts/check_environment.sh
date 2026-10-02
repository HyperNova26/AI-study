#!/usr/bin/env bash
set -eo pipefail
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
source "$script_dir/env.sh"

python3 - "$script_dir/.." "$FASTLIO_WS" <<'PY'
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

import yaml
from ament_index_python.packages import get_package_prefix, get_package_share_directory
import xacro

root = Path(sys.argv[1]).resolve()
fastlio_ws = Path(sys.argv[2])
packages = [
    "nav2_minimal_tb3_sim", "turtlebot3_description", "ros_gz_sim", "ros_gz_bridge",
    "robot_state_publisher", "xacro", "rviz2", "tf2_ros", "tf2_tools", "pcl_ros",
    "pcl_conversions", "teleop_twist_keyboard",
]
missing = []
for package in packages:
    try:
        share = Path(get_package_share_directory(package))
        print(f"OK {package}: {ET.parse(share / 'package.xml').findtext('version')}")
    except (LookupError, OSError) as error:
        missing.append(f"{package}: {error}")
if missing:
    sys.exit("\n".join(missing) + "\nscripts/install_dependencies.sh를 실행하세요.")

for package in ("fast_lio", "livox_ros_driver2"):
    try:
        print(f"OK {package}: {get_package_prefix(package)}")
    except LookupError:
        sys.exit(f"{package}를 찾지 못했습니다. scripts/build_fast_lio.sh로 빌드한 뒤 새 터미널에서 다시 실행하세요.")
fast_lio_src = fastlio_ws / "src/FAST_LIO"
if fast_lio_src.is_dir():
    head = subprocess.run(["git", "-C", str(fast_lio_src), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    expected = "a4743b095409588842a5b30ddfa27e29d2f99164"
    print(("OK" if head == expected else "다른 커밋") + f" FAST_LIO commit: {head[:7]} (기준 {expected[:7]})")

import numpy  # noqa: F401  points_to_fastlio.py needs NumPy
print(f"OK numpy: {numpy.__version__}")

robot = ET.fromstring(xacro.process_file(str(root / "models/burger_sensors.urdf.xacro")).toxml())
for mesh in robot.iter("mesh"):
    uri = mesh.attrib["filename"]
    if uri.startswith("package://"):
        package, relative = uri.removeprefix("package://").split("/", 1)
        if not (Path(get_package_share_directory(package)) / relative).is_file():
            sys.exit(f"모델 메시가 없습니다: {uri}")
for sensor in robot.findall("gazebo/sensor"):
    print(f"OK sensor: {sensor.attrib['name']} ({sensor.attrib['type']}, {sensor.findtext('update_rate')} Hz target)")

bridge = yaml.safe_load((root / "config/bridge.yaml").read_text())
print("OK bridge topics:", ", ".join(entry.get("ros_topic_name", entry.get("topic_name")) for entry in bridge))
params = yaml.safe_load((root / "config/fast_lio_burger.yaml").read_text())["/**"]["ros__parameters"]
print(f"OK FAST-LIO2 config: lid_topic={params['common']['lid_topic']}, imu_topic={params['common']['imu_topic']}, "
      f"lidar_type={params['preprocess']['lidar_type']}, extrinsic_T={params['mapping']['extrinsic_T']}")
print("준비 파일 확인 완료. 실행 중 센서·TF 점검은 docs/sensors_topics_frames.md를 참고하세요.")
PY

printf 'ROS_DOMAIN_ID=%s, GZ_PARTITION=%s, FASTLIO_WS=%s\n' "$ROS_DOMAIN_ID" "$GZ_PARTITION" "$FASTLIO_WS"
gz sim --versions
