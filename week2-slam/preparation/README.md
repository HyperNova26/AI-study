# TurtleBot3 Burger + 3D LiDAR·IMU 준비 환경

[2주차 인지팀 과제](../turtlebot-nav2-task.md)의 **제공되는 것**을 준비하는 폴더입니다. 개인 제출 코드, 수행 결과, 영상, 스크린샷은 포함하지 않습니다.

## 사용할 환경

| 항목 | 기준 |
| --- | --- |
| OS | Ubuntu 24.04 LTS, 데스크톱 환경 |
| ROS 2 | Jazzy Jalisco |
| Nav2 | Jazzy용 1.3.x, 제공 설정의 기준 버전 **1.3.13** |
| 시뮬레이터 | Gazebo Harmonic (`gz sim` 8.x) |
| 로봇 | TurtleBot3 **Burger**, ROBOTIS `turtlebot3_description` 기반 |
| 추가 센서 | 16채널 3D LiDAR (`/points`) + 200 Hz 설정 IMU (`/imu`) |
| 실습 공간 | `nav2_minimal_tb3_sim/worlds/tb3_sandbox.sdf.xacro` |
| 지도 | 이 폴더의 `maps/tb3_sandbox.yaml` + `.pgm` |
| 위치 추정 | 제공된 지도 + AMCL (`slam:=False`) |
| 기본 계획·제어 | NavFn 전역 경로 계획 + MPPI 경로 추종 |

[Nav2 Jazzy Quickstart](https://docs.nav2.org/jazzy/getting_started/quickstart/quickstart/)의 Nav2 bringup과 sandbox 월드·지도를 사용하고, 로봇은 **Burger + 추가 센서**로 구성합니다. Burger 기본 URDF·메시는 `turtlebot3_description`, 월드는 `nav2_minimal_tb3_sim` 패키지에서 읽습니다. 센서·구동 플러그인과 브리지 설정은 이 폴더에 있습니다. `TURTLEBOT3_MODEL` 설정이나 별도 소스 빌드는 필요하지 않습니다.

기본 2D LDS `/scan`은 Nav2에 사용하고, 추가 3D LiDAR `/points`는 RViz에서 확인합니다. IMU 데이터는 `/imu`로 제공합니다. 사양·장착 좌표·데이터 사용 범위는 [센서 안내](docs/sensors.md)에 정리했습니다.

[Gazebo의 ROS 호환 안내](https://gazebosim.org/docs/harmonic/ros_installation/)에 따라 Jazzy와 Harmonic을 함께 사용합니다. Humble/Gazebo Classic용 `gazebo`, `gazebo_ros`, `turtlebot3_gazebo` 명령과 섞지 마세요. Windows/macOS에서는 Ubuntu 24.04 데스크톱 VM 등으로 이 OS 환경을 먼저 준비하세요. 그래픽 가속과 디스플레이를 사용할 수 있어야 합니다.

## 제공 파일

```text
preparation/
├── README.md                       # 설치·실행 안내
├── launch/simulation.launch.py     # Gazebo + Burger + 센서 + Nav2 + RViz
├── models/burger_sensors.urdf.xacro # Burger + 3D LiDAR·IMU·구동기
├── config/bridge.yaml              # /points·/imu 포함 ROS/Gazebo 변환
├── maps/tb3_sandbox.{yaml,pgm}      # 월드와 대응하는 공식 지도
├── config/nav2_params.yaml         # Nav2 1.3.13 기반 Burger 주행 설정
├── rviz/practice.rviz              # 지도·로봇·센서·경로·costmap 화면
├── scripts/
│   ├── install_dependencies.sh     # Jazzy 설치 후 추가 패키지 설치
│   ├── env.sh                      # 터미널별 ROS 환경
│   ├── check_environment.sh        # 패키지·모델·지도 파일 검사
│   └── run_simulation.sh           # 빌드 없이 실행
├── docs/concepts.md                # Nav2·TF·RViz 교보재
├── docs/sensors.md                 # 센서 사양·장착 TF·점검 명령
├── docs/troubleshooting.md         # 실행 문제 확인 순서
├── THIRD_PARTY.md                  # 공식 자산의 출처·변경 사항
└── licenses/Apache-2.0.txt
```

## 설치

1. Ubuntu 24.04에서 [ROS 2 Jazzy 공식 Debian 패키지 설치 안내](https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html)를 따라 locale, Universe, ROS apt 저장소를 설정하고 `ros-jazzy-desktop`을 설치합니다. 공식 페이지가 접근 차단될 때는 [동일 문서의 GitHub 원문](https://github.com/ros2/ros2_documentation/blob/jazzy/source/Installation/Ubuntu-Install-Debs.rst)을 참고하세요.
2. ROS가 설치된 새 Bash 터미널에서 아래 명령을 실행합니다. Python 가상환경은 비활성화합니다. ROS 패키지는 시스템 Python을 사용합니다.

```bash
# AI-study 저장소 루트에서
cd week2-slam/preparation
./scripts/install_dependencies.sh
./scripts/check_environment.sh
```

설치 스크립트는 `sudo apt-get`으로 Nav2, 최소 TB3 월드, Burger description, `ros_gz`, RViz, TF 도구 등을 설치합니다. 이미 설치한 시스템에서도 사용할 수 있습니다. ROS apt 저장소에서 Jazzy용 패키지를 받으므로 패치 버전은 업데이트 시점에 따라 달라질 수 있습니다. 이 폴더의 지도·Nav2 설정은 1.3.13에서 가져왔으며, 설정에는 공통 시작 위치와 Burger용 크기·속도 제한을 적용했습니다. 설치된 버전은 검사 스크립트로 확인하세요.

## 실행

이하 명령은 `week2-slam/preparation` 폴더 기준입니다.

```bash
./scripts/run_simulation.sh
```

Gazebo와 RViz가 함께 열리고 센서를 탑재한 Burger가 **`x=-2.0 m, y=-0.5 m, yaw=0 rad`**에서 생성됩니다. 로봇 앞쪽은 지도의 +X 방향입니다. 시뮬레이션 시간을 켜고 **AMCL에도 같은 시작 위치를 초기값으로 전달**해 Nav2 lifecycle 노드가 시작됩니다. 목표는 자동 전송하지 않습니다.

`models/burger_sensors.urdf.xacro`에서 생성한 동일한 로봇 정의를 Gazebo와 `robot_state_publisher`에 전달합니다. RViz의 `3D LiDAR`에 점군이 보이며 기본 Orbit 뷰에서 시점을 돌려 높이 방향을 확인할 수 있습니다.

실행 스크립트는 다음 환경을 설정합니다. 다른 터미널에서 ROS 명령을 사용할 때도 같은 `env.sh`를 source해야 합니다.

```bash
source scripts/env.sh
```

- `ROS_DOMAIN_ID=42`: 이 실습의 기본 ROS 통신 도메인입니다.
- `ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST`: 같은 PC 안에서 검색합니다.
- `GZ_PARTITION=aistudy-week2-42`: 이 실습의 Gazebo 통신 영역입니다.

이미 지정한 환경변수는 유지합니다. 같은 PC에서 두 실습을 동시에 실행하려면 각 실습의 **모든 터미널에 서로 다른 `ROS_DOMAIN_ID`와 `GZ_PARTITION`**을 지정하세요. 한 실습에서는 값을 동일하게 유지합니다.

GUI를 줄여 실행할 수도 있습니다. `True`/`False`의 대소문자를 그대로 사용하세요.

```bash
# Gazebo 창만 닫고 RViz는 표시
./scripts/run_simulation.sh headless:=True

# 두 창 모두 생략; GPU LiDAR 때문에 센서 렌더링 환경은 여전히 필요
./scripts/run_simulation.sh headless:=True use_rviz:=False

# 준비된 기본 설정을 살펴보거나 launch 인자 확인
less config/nav2_params.yaml
./scripts/run_simulation.sh --show-args
```

개인 실습에서 수정한 전체 Nav2 설정을 사용하려면 `params_file:=/절대/경로/nav2_params.yaml`을 전달합니다. 기본 지도와 월드는 한 쌍이며, 다른 지도를 사용하려면 실제 월드와의 일치 여부를 별도로 확인해야 합니다.

## RViz에서 시작 위치와 목표 지정

1. Gazebo에서 로봇과 월드를 확인합니다. 일시정지 상태라면 재생 버튼을 누릅니다.
2. RViz의 `Global Options → Fixed Frame`이 `map`인지 확인합니다. `Map` 디스플레이에 `/map`이 표시됩니다.
3. 기본 설정은 AMCL 초기 위치를 자동 적용합니다. 초기 위치 입력을 연습하거나 정합을 다시 맞추려면 상단 **2D Pose Estimate**로 시작 위치 `(-2.0, -0.5)` 부근을 클릭하고 +X 방향으로 드래그합니다. 이는 AMCL에 주는 추정값이며 로봇을 순간이동시키지 않습니다.
4. `RobotModel`과 `LaserScan`을 보고 지도 벽과 스캔이 대략 겹치는지 확인합니다. 센서와 위치 추정이 시작되는 동안 `map` 관련 TF 경고가 잠깐 나올 수 있습니다. 계속 남으면 [문제 해결 안내](docs/troubleshooting.md)를 확인합니다.
5. 상단 **Nav2 Goal**(설치 버전에 따라 `Navigation2 Goal`)로 로봇 근처의 흰색 빈 공간을 클릭하고 도착 방향으로 드래그합니다. 벽·회색 미지 영역·장애물 경계는 피합니다. 목표 위치는 실습자가 선택합니다.
6. `Global Planner → Path`에서 전역 경로를, `Controller`에서 지역 costmap과 경로를 확인합니다. Navigation 2 패널에서 진행 상태를 확인하고 필요하면 취소합니다.

종료할 때는 실행 터미널에서 `Ctrl+C`를 누르고 자식 프로세스가 끝날 때까지 기다립니다. 다시 시작하면 기본 생성 위치와 AMCL 초기값으로 돌아갑니다.

## 실행 상태 점검

시뮬레이션을 켠 상태에서 **별도 터미널**을 열고 실행합니다.

```bash
cd /path/to/AI-study/week2-slam/preparation  # 실제 clone 경로로 변경
source scripts/env.sh

ros2 topic echo /clock --once
ros2 topic echo /scan --once --field header --qos-reliability best_effort
ros2 topic echo /odom --once --field header
ros2 topic echo /points --once --field header --qos-reliability best_effort
ros2 topic echo /imu --once --field header --qos-reliability best_effort
ros2 topic echo /map --once --field info --qos-durability transient_local
ros2 lifecycle get /amcl

# AMCL 초기 위치가 적용된 이후
ros2 run tf2_ros tf2_echo map base_link
# 위 명령은 계속 출력하므로 확인 후 Ctrl+C
ros2 lifecycle get /bt_navigator
ros2 action list -t
```

`/clock` 값이 증가하고 `/scan`, `/points`, `/imu`, `/odom`, `/map`을 수신할 수 있어야 합니다. 초기 위치가 적용된 뒤 `map → base_link` 변환이 조회되고 `/bt_navigator`가 `active`이며 `/navigate_to_pose` action이 보이면 목표를 보낼 준비가 된 것입니다. 노드가 Active라는 사실만으로 목표 도착을 의미하지는 않습니다.

지도는 `0.05 m/pixel`, 원점 `[-10.0, -10.0, 0.0]`입니다. YAML의 `image`는 YAML 파일 위치에 대한 상대 경로이므로 `.pgm`과 `.yaml`을 함께 유지합니다.

먼저 [Nav2·TF·RViz 교보재](docs/concepts.md)를 읽고, 실행이 막히면 [문제 해결 안내](docs/troubleshooting.md)를 순서대로 확인하세요.
