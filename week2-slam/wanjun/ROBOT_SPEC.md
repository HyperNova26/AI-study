# TurtleBot3 Burger 시뮬레이션 사양

`week2-slam/wanjun`의 실제 모델·브리지·Nav2 설정을 기준으로 정리한 정보입니다. 설치·실행은 [SETUP.md](SETUP.md)와 [README.md](README.md), 자산 출처는 [THIRD_PARTY.md](THIRD_PARTY.md)를 참고합니다.

## 환경과 버전

2026-09-26에 확인한 버전입니다. 설치 스크립트는 Jazzy apt 배포 채널을 사용하므로 아래 패치 버전을 고정 설치하는 구성은 아닙니다.

| 항목 | 확인한 버전 / 구성 |
| --- | --- |
| OS | Ubuntu 24.04 LTS |
| ROS 2 | Jazzy Jalisco |
| Nav2 | `nav2_bringup`, AMCL, map server, NavFn, MPPI, RViz 플러그인 **1.3.13** |
| Gazebo | Harmonic, Gazebo Sim **8.15.0** |
| 로봇 description | `turtlebot3_description` **2.3.6** |
| 실습 월드 패키지 | `nav2_minimal_tb3_sim` **1.0.1** |
| ROS–Gazebo 연결 | `ros_gz_sim`, `ros_gz_bridge` **1.0.24** |
| RViz | `rviz2` **14.1.23** |
| 로봇 TF 발행 | `robot_state_publisher` **3.3.4** |
| Xacro | **2.1.1** |
| TF 도구 | `tf2_ros`, `tf2_tools` **0.36.22** |
| Python | 시스템 Python **3.12.3** |
| ROS 시간 | `use_sim_time=True`, Gazebo `/clock` 사용 |
| 물리 시간 간격 | **0.001 s** (1 ms) |
| ROS 통신 기본값 | `ROS_DOMAIN_ID=42`, `ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST` |
| Gazebo 통신 기본값 | `GZ_PARTITION=aistudy-week2-42`; 지정한 domain에 맞춰 기본값 생성 |

환경변수를 미리 지정하면 `scripts/env.sh`는 그 값을 유지합니다. 모든 실행 터미널에서 같은 ROS 도메인과 Gazebo partition을 사용합니다. GPU LiDAR는 Gazebo GUI를 생략해도 센서 렌더링 환경이 필요합니다.

## 로봇과 구동

| 항목 | 설정 |
| --- | --- |
| 모델 | TurtleBot3 **Burger**, 차동 구동 |
| 기본 URDF | 설치된 `turtlebot3_description/urdf/turtlebot3_burger.urdf` |
| 확장 모델 | [models/burger_sensors.urdf.xacro](models/burger_sensors.urdf.xacro) |
| 차륜 간격 / 바퀴 반지름 | **0.16 m / 0.033 m** |
| 생성 위치 | `x=-2.0 m`, `y=-0.5 m`, `z=0.01 m`, `yaw=0 rad` |
| AMCL 초기 위치 | `map` 기준 `x=-2.0 m`, `y=-0.5 m`, `yaw=0 rad` |
| 구동 플러그인 | `gz::sim::systems::DiffDrive` |
| 구동기 선속도 범위 | **-0.22 ~ +0.22 m/s** |
| 구동기 각속도 범위 | **-2.0 ~ +2.0 rad/s** |
| 선형 / 각 가속도 범위 | **±0.5 m/s² / ±2.0 rad/s²** |
| odometry 발행 설정 | **30 Hz**, `odom → base_footprint` |

Gazebo와 `robot_state_publisher`는 같은 Xacro 출력으로 로봇 형상과 장착 TF를 공유합니다. 본체·바퀴 메시와 sandbox 월드는 설치 패키지에서 읽습니다.

## 탑재 센서

아래 주파수는 시뮬레이션 시간 기준 설정값이며 실제 수신 속도는 실행 부하와 통신 상황에 따라 달라질 수 있습니다.

| 센서 | Gazebo 센서 이름 / 종류 | ROS 토픽 | 프레임 | 설정 |
| --- | --- | --- | --- | --- |
| 기본 2D LDS | `burger_2d_lidar` / `gpu_lidar` | `/scan` | `base_scan` | 360개 수평 샘플, 1° 간격으로 한 바퀴, **5 Hz**, **0.12–3.5 m** |
| 추가 3D LiDAR | `burger_3d_lidar` / `gpu_lidar` | `/points` | `lidar_3d_link` | 수평 720 × 수직 16채널, **10 Hz**, **0.10–20 m** |
| IMU | `burger_imu` / `imu` | `/imu` | `imu_link` | **200 Hz**, 자세 quaternion·3축 각속도·3축 선형가속도 |

3D LiDAR는 특정 제조사 제품의 정밀 모델이 아닌 **범용 16채널 센서**입니다. 수평 0.5° 간격으로 한 바퀴를 스캔하고 수직 시야각은 **-15°~+15°**입니다. 양 끝 방향이 겹치지 않도록 수평 마지막 각도는 첫 각도 + 359.5°로 설정합니다. 각 수직 각도에서 월드에 광선을 쏴 측정하므로 실제 높이 차이를 가진 점군을 생성합니다.

| 추가 정보 | 값 |
| --- | --- |
| 3D LiDAR 센서 / 지지대 질량 | **0.10 kg / 0.02 kg** |
| 2D 거리 분해능 / 노이즈 표준편차 | **0.015 m / 0.01 m** |
| 3D 거리 분해능 / 노이즈 표준편차 | **0.01 m / 0.01 m** |
| IMU 각속도 노이즈 표준편차 | 축별 **0.0002 rad/s** |
| IMU 선형가속도 노이즈 표준편차 | 축별 **0.017 m/s²** |
| 점군 구조 | `width=720`, `height=16` |
| 점군 필드 | `x`, `y`, `z`, `intensity`, `ring` |
| 포인트별 측정 시간 | 별도 필드 없음 |
| IMU 자기장 데이터 | 없음; `sensor_msgs/msg/Imu` 사용 |

미검출 광선은 무한대 등 유효하지 않은 좌표를 포함할 수 있습니다. 점군을 처리할 때는 유효한 좌표만 사용합니다.

## ROS–Gazebo 브리지 토픽

[config/bridge.yaml](config/bridge.yaml)의 전체 브리지 목록입니다. 방향에서 GZ는 Gazebo, ROS는 ROS 2를 뜻합니다. 각 항목은 브리지 하나로 연결합니다.

| ROS 토픽 | ROS 메시지 타입 | Gazebo 토픽 | Gazebo 메시지 타입 | 방향 |
| --- | --- | --- | --- | --- |
| `/clock` | `rosgraph_msgs/msg/Clock` | `/clock` | `gz.msgs.Clock` | GZ → ROS |
| `/joint_states` | `sensor_msgs/msg/JointState` | `/joint_states` | `gz.msgs.Model` | GZ → ROS |
| `/odom` | `nav_msgs/msg/Odometry` | `/odom` | `gz.msgs.Odometry` | GZ → ROS |
| `/tf` | `tf2_msgs/msg/TFMessage` | `/tf` | `gz.msgs.Pose_V` | GZ → ROS |
| `/scan` | `sensor_msgs/msg/LaserScan` | `/scan` | `gz.msgs.LaserScan` | GZ → ROS |
| `/points` | `sensor_msgs/msg/PointCloud2` | `/lidar_3d/points` | `gz.msgs.PointCloudPacked` | GZ → ROS |
| `/imu` | `sensor_msgs/msg/Imu` | `/imu` | `gz.msgs.IMU` | GZ → ROS |
| `/cmd_vel` | `geometry_msgs/msg/Twist` | `/cmd_vel` | `gz.msgs.Twist` | ROS → GZ |

RViz와 목표 실행 코드는 센서 토픽을 Best Effort로 구독합니다. 이는 구독 측 설정이며 브리지 발행 QoS와 구분합니다. `/cmd_vel`은 `TwistStamped`가 아닌 **`Twist`**입니다.

## 주요 ROS 토픽과 인터페이스

| 이름 | 타입 | 역할 / 주요 발행자 |
| --- | --- | --- |
| `/robot_description` | `std_msgs/msg/String` | URDF 로봇 설명, `robot_state_publisher` |
| `/tf_static` | `tf2_msgs/msg/TFMessage` | 몸체·센서 고정 TF, `robot_state_publisher` |
| `/map` | `nav_msgs/msg/OccupancyGrid` | 저장된 점유 지도, `map_server` |
| `/amcl_pose` | `geometry_msgs/msg/PoseWithCovarianceStamped` | 지도 기준 추정 위치, AMCL |
| `/particle_cloud` | `nav2_msgs/msg/ParticleCloud` | AMCL 위치 가설 분포 |
| `/initialpose` | `geometry_msgs/msg/PoseWithCovarianceStamped` | AMCL 초기 위치 입력; RViz 2D Pose Estimate |
| `/plan` | `nav_msgs/msg/Path` | NavFn 전역 계획 경로 |
| `/transformed_global_plan` | `nav_msgs/msg/Path` | MPPI 제어 프레임으로 변환한 전역 경로 |
| `/optimal_trajectory` | `nav_msgs/msg/Path` | MPPI가 선택한 제어 궤적의 시각화 |
| `/global_costmap/costmap` | `nav_msgs/msg/OccupancyGrid` | 전역 장애물 비용 지도 |
| `/local_costmap/costmap` | `nav_msgs/msg/OccupancyGrid` | 로봇 주변 장애물 비용 지도 |
| `/cmd_vel_nav` | `geometry_msgs/msg/Twist` | controller / behavior server의 속도 명령 |
| `/cmd_vel_smoothed` | `geometry_msgs/msg/Twist` | velocity smoother를 거친 명령 |
| `/cmd_vel` | `geometry_msgs/msg/Twist` | collision monitor를 거친 최종 구동 명령 |
| `/navigate_to_pose` | **action:** `nav2_msgs/action/NavigateToPose` | 목표 위치·방향 전송, 피드백·결과 확인 |
| `/bt_navigator/get_state` | **service:** `lifecycle_msgs/srv/GetState` | Nav2 준비 상태 확인 |

`/map`, `/robot_description`, `/tf_static`은 늦게 연결해도 보존된 값을 받을 수 있도록 Transient Local로 구독합니다. 표는 실습에서 사용하는 주요 인터페이스이며 ROS가 생성하는 모든 진단·파라미터·action 내부 토픽을 나열한 것은 아닙니다.

## TF와 센서 장착 좌표

주요 연결은 `map → odom → base_footprint → base_link → 센서 링크`입니다.

| 변환 | 발행 주체 |
| --- | --- |
| `map → odom` | AMCL |
| `odom → base_footprint` | Gazebo DiffDrive + 브리지 |
| `base_footprint → base_link` | `robot_state_publisher` |
| `base_link → 센서 링크` | `robot_state_publisher` |

장착 좌표는 `base_link` 기준이며 단위는 위치 m, 회전 rad입니다.

| 센서 링크 | `xyz` | `rpy` |
| --- | --- | --- |
| `base_scan` | `[-0.032, 0, 0.172]` | `[0, 0, 0]` |
| `lidar_3d_link` | `[-0.032, 0, 0.260]` | `[0, 0, 0]` |
| `imu_link` | `[-0.032, 0, 0.068]` | `[0, 0, 0]` |

3D LiDAR는 기본 2D LDS 위에 설치합니다. URDF→SDF 변환 시 고정 링크가 부모에 합쳐져도 센서 위치는 보존되며 `gz_frame_id`가 ROS 메시지 프레임을 지정합니다. `imu_link` TF는 장착 관계이며 IMU의 측정 자세를 표현하는 별도 필터 출력은 아닙니다.

## 지도와 Nav2 설정

| 항목 | 값 |
| --- | --- |
| 월드 | 설치 패키지의 `nav2_minimal_tb3_sim/worlds/tb3_sandbox.sdf.xacro` |
| 지도 | [maps/tb3_sandbox.yaml](maps/tb3_sandbox.yaml) + [PGM](maps/tb3_sandbox.pgm) |
| 지도 해상도 / 원점 | **0.05 m/pixel** / `[-10.0, -10.0, 0.0]` |
| 지도 임계값 | `occupied_thresh=0.65`, `free_thresh=0.196`, `negate=0` |
| 위치 추정 | 저장된 지도 + AMCL, `slam=False` |
| 전역 계획기 | `nav2_navfn_planner::NavfnPlanner` |
| 경로 추종기 | `nav2_mppi_controller::MPPIController`, `DiffDrive` |
| 실행 방식 | Nav2 개별 프로세스, `use_composition=False`, 자동 lifecycle 활성화 |
| 예제 목표 | `map` 기준 `x=1.5 m`, `y=-0.5 m`, `yaw=0 rad` |
| 시작 준비 / 주행 제한 시간 | **60초 / 180초**, 실제 경과 시간 기준 |

`run_base_simulation.sh`는 [nav2_params.yaml](config/nav2_params.yaml)만 적용합니다. 기본 제출 실행인 `run_simulation.sh`는 여기에 [nav2_overrides.yaml](config/nav2_overrides.yaml)을 병합합니다.

| 설정 | Burger 기본값 | 개인 제출 적용값 |
| --- | --- | --- |
| MPPI·velocity smoother 선속도 | ±0.22 m/s | **±0.18 m/s** |
| 위치 도착 허용 오차 | 0.25 m | **0.15 m** |
| 방향 도착 허용 오차 | 0.25 rad | **0.15 rad** |
| MPPI / smoother 각속도 상한 | 1.9 / 2.0 rad/s | 동일 |
| 두 costmap의 로봇 반지름 | 0.13 m | 동일 |
| inflation 반경 | 0.35 m | 동일 |
| progress checker | 0.1 m / 20초 | 동일 |
| 횡방향 속도·가속도 | 0, 차동 구동 | 동일 |

Nav2는 **2D `/scan`과 `/odom`**을 사용합니다. 3D `/points`와 `/imu`는 함께 발행하고 목표 실행 전 수신을 확인하며, RViz에서는 점군을 높이별 색으로 표시합니다. **3D 점군의 Nav2 costmap 입력, IMU EKF 융합, FAST-LIO 연결은 구성하지 않았습니다.**
