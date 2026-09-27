# 센서 수신과 TF 점검

센서 사양·장착 좌표·점군 필드와 데이터 사용 범위는 [ROBOT_SPEC.md](../ROBOT_SPEC.md)에 정리했습니다. 이 문서는 실행 중인 센서의 수신과 TF를 확인하는 방법입니다.

## 점검 명령

실행 중인 시뮬레이션과 같은 환경에서 사용합니다.

```bash
# week2-slam/wanjun 폴더에서
source scripts/env.sh
ros2 topic echo /points --once --field header --qos-reliability best_effort
ros2 topic echo /points --once --field height --qos-reliability best_effort
ros2 topic echo /points --once --field fields --qos-reliability best_effort
ros2 topic echo /imu --once --qos-reliability best_effort
ros2 topic hz /points
# Ctrl+C 후
ros2 topic hz /imu
# Ctrl+C 후
ros2 run tf2_ros tf2_echo base_link lidar_3d_link
# Ctrl+C 후
ros2 run tf2_ros tf2_echo base_link imu_link
```

`/points`는 너비 720, 높이 16인 점군이며 장애물이 보이면 유효한 점들이 여러 높이에 분포합니다. 미검출 광선은 무한대 등 유효하지 않은 값으로 표현될 수 있으므로 점군 처리 시 제외합니다. 정지 상태의 IMU는 각속도가 0 근처이고 선형가속도의 Z 성분이 약 +9.8 m/s²여야 합니다. 센서 헤더 시각은 `/clock`을 따릅니다.

센서 위치는 `models/burger_sensors.urdf.xacro`의 joint origin에서 설정합니다. 토픽 변경 시 `config/bridge.yaml`, RViz와 소비 노드의 설정도 함께 맞춥니다.

## 공식 참고 자료

- [ROBOTIS Burger URDF](https://github.com/ROBOTIS-GIT/turtlebot3/blob/jazzy/turtlebot3_description/urdf/turtlebot3_burger.urdf): 본체·바퀴·기존 센서 좌표.
- [Gazebo Harmonic GPU LiDAR 예제](https://github.com/gazebosim/gz-sim/blob/gz-sim8/examples/worlds/gpu_lidar_sensor.sdf): 수평·수직 스캔 설정.
- [ros_gz_bridge](https://github.com/gazebosim/ros_gz/blob/jazzy/ros_gz_bridge/README.md): `PointCloudPacked → PointCloud2`, `IMU → Imu` 변환.
