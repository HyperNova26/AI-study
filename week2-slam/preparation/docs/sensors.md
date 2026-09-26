# Burger의 3D LiDAR·IMU

ROBOTIS의 `turtlebot3_description` Burger URDF에 가상 센서를 추가합니다. Gazebo와 `robot_state_publisher`가 **같은 `models/burger_sensors.urdf.xacro` 출력**을 사용하므로 형상과 센서 장착 좌표를 함께 관리합니다. 기존 Waffle 모델은 실행하지 않습니다.

## 탑재 구성

| 센서 | ROS 토픽 / 타입 | 프레임 | 설정 |
| --- | --- | --- | --- |
| 기본 2D LDS | `/scan` / `sensor_msgs/msg/LaserScan` | `base_scan` | 수평 360개, 360° 순환, 5 Hz, 0.12–3.5 m |
| 추가 3D LiDAR | `/points` / `sensor_msgs/msg/PointCloud2` | `lidar_3d_link` | 수평 720개 × 수직 16채널, 10 Hz, 0.10–20 m |
| IMU | `/imu` / `sensor_msgs/msg/Imu` | `imu_link` | 200 Hz 설정, 자세 quaternion·3축 각속도·3축 선형가속도 |

3D LiDAR는 수평 0.5° 간격으로 한 바퀴를 스캔하고 수직 시야각은 **-15°~+15°**입니다. 첫 각도와 마지막 각도를 중복시키지 않습니다. Gazebo `gpu_lidar`의 `/lidar_3d/points`를 `ros_gz_bridge`가 ROS `/points`로 변환합니다. 2D 스캔을 복제한 점군이 아니라, 각 수직 각도에서 월드에 광선을 쏴 얻은 3D 측정입니다.

이 센서는 특정 제조사 제품의 정밀 모델이 아닌 **범용 16채널 시뮬레이션 센서**입니다. 센서 질량은 0.10 kg, 지지대는 0.02 kg으로 설정했습니다. IMU는 Burger의 기존 장착 프레임에 Gazebo 센서를 연결합니다. `sensor_msgs/Imu`에는 자기장 측정이 포함되지 않습니다.

센서 주기는 시뮬레이션 시간 기준 목표값입니다. PC 부하와 전송 지연·드롭에 따라 수신 주파수는 달라질 수 있습니다. IMU 주기를 표현할 수 있도록 준비 launch는 월드의 물리 시간 간격을 1 ms로 설정합니다.

## 센서가 사용되는 곳

- **Nav2/AMCL:** 기존 `/scan`과 `/odom`을 사용합니다. 추가 센서가 켜진 상태에서도 제공 지도에서 2D 자율주행을 연습할 수 있습니다.
- **3D 관찰:** RViz의 `3D LiDAR` 디스플레이에서 `/points`를 높이별 색으로 표시합니다. 기본 뷰는 Orbit이므로 마우스로 시점을 돌려 수직 구조를 확인할 수 있습니다.
- **IMU 관찰:** `/imu`의 자세·각속도·선형가속도를 확인합니다. TF의 `imu_link`는 **장착 관계**를 나타내며 IMU 측정 자세 그래프를 대신하지 않습니다.

3D 점군을 Nav2 costmap에 넣거나 IMU를 EKF에 융합하는 노드는 이번 준비 환경에 포함하지 않습니다. 기본 점군 필드는 `x`, `y`, `z`, `intensity`, `ring`이며, 별도의 포인트별 측정 시간 필드는 제공하지 않습니다. 후속 SLAM에 연결할 때는 해당 알고리즘의 입력 필드 요구사항을 확인해야 합니다.

## 장착 TF

| 변환 | `xyz` (m) | `rpy` (rad) |
| --- | --- | --- |
| `base_link → base_scan` | `[-0.032, 0, 0.172]` | `[0, 0, 0]` |
| `base_link → lidar_3d_link` | `[-0.032, 0, 0.260]` | `[0, 0, 0]` |
| `base_link → imu_link` | `[-0.032, 0, 0.068]` | `[0, 0, 0]` |

3D LiDAR는 기존 LDS 위에 올려 2D 스캔면을 가리지 않게 구성했습니다. IMU·LiDAR 링크의 고정 연결은 Gazebo의 URDF→SDF 변환 과정에서 부모 링크로 합쳐질 수 있습니다. 변환기는 실제 센서 위치를 보존하며, `gz_frame_id`가 ROS 메시지의 센서 프레임을 지정합니다.

## 점검 명령

실행 중인 시뮬레이션과 같은 환경에서 사용합니다.

```bash
# week2-slam/preparation 폴더에서
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

## Burger용 주행 설정

[공식 Burger 사양](https://emanual.robotis.com/docs/en/platform/turtlebot3/features/)의 전진 속도 상한 0.22 m/s에 맞춰 Gazebo 구동기, MPPI, velocity smoother를 구성합니다. 연습용 회전 속도 상한은 2.0 rad/s이며 MPPI는 1.9 rad/s로 더 낮습니다.

- 차륜 간격 0.16 m, 바퀴 반지름 0.033 m.
- 두 costmap의 로봇 반지름 0.13 m, inflation 반경 0.35 m.
- 전진·후진 상한 ±0.22 m/s, 선형 가속·감속 상한 ±0.5 m/s².
- MPPI의 횡방향 속도·가속도는 0이며 `DiffDrive`를 사용합니다.
- 느린 근거리 주행에 맞춰 progress checker를 이동 거리 0.1 m / 제한 시간 20초로 설정합니다.

센서 위치를 바꾸려면 Xacro의 joint origin을 수정합니다. 토픽을 바꿀 때는 `config/bridge.yaml`, RViz 및 필요한 소비 노드의 설정도 맞춰야 합니다.

## 공식 참고 자료

- [ROBOTIS Burger URDF](https://github.com/ROBOTIS-GIT/turtlebot3/blob/jazzy/turtlebot3_description/urdf/turtlebot3_burger.urdf): 본체·바퀴·기존 센서 좌표.
- [Gazebo Harmonic GPU LiDAR 예제](https://github.com/gazebosim/gz-sim/blob/gz-sim8/examples/worlds/gpu_lidar_sensor.sdf): 수평·수직 스캔 설정.
- [ros_gz_bridge](https://github.com/gazebosim/ros_gz/blob/jazzy/ros_gz_bridge/README.md): `PointCloudPacked → PointCloud2`, `IMU → Imu` 변환.
