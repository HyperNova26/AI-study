# 3주차 인지팀 제공 환경 — FAST-LIO2 + 시뮬레이션 TurtleBot3

[과제 안내](../fastlio2-rviz-task.md)의 "제공되는 것"에 해당하는 시뮬레이션·설정·빌드 스크립트·교보재입니다. 2주차 Burger(16채널 3D LiDAR + IMU)를 그대로 사용하고, FAST-LIO2가 받을 수 있는 센서 형식과 기본 설정을 더했습니다. 개념과 실습 순서는 [3주차 인지팀 안내](../guide.md)를 먼저 읽으세요.

| 과제의 제공 항목 | 이 폴더의 위치 |
| --- | --- |
| 3D LiDAR·IMU의 장착 위치가 정의된 TurtleBot URDF 및 관련 자산 | [models/burger_sensors.urdf.xacro](models/burger_sensors.urdf.xacro) (2주차 모델 + 정답 위치 발행) |
| 센서 데이터가 실제로 생성·발행되는 시뮬레이션 설정 | [launch/simulation.launch.py](launch/simulation.launch.py), [config/bridge.yaml](config/bridge.yaml) |
| FAST-LIO2 입력과 호환되는 센서 데이터 형식 및 시간 설정 | [tools/points_to_fastlio.py](tools/points_to_fastlio.py), [docs/sensors_topics_frames.md](docs/sensors_topics_frames.md) |
| 사용할 FAST-LIO2 구현·버전과 기본 설정 예제 | [scripts/build_fast_lio.sh](scripts/build_fast_lio.sh), [config/fast_lio_burger.yaml](config/fast_lio_burger.yaml) |
| 센서 토픽, 좌표계, FAST-LIO2, RViz 교보재 | [docs/](docs/) |

예시 답안은 [Solution-HJ1](../Solution-HJ1/README.md)에 있습니다.

## 실행 환경

| 항목 | 기준 |
| --- | --- |
| OS / ROS 2 | Ubuntu 24.04, ROS 2 Jazzy (2주차와 같음) |
| 시뮬레이터 | Gazebo Harmonic (Gazebo Sim 8), `ros_gz` |
| 로봇·월드 | TurtleBot3 Burger + 16채널 3D LiDAR + IMU, `nav2_minimal_tb3_sim`의 sandbox 월드, 시작 위치 `(-2.0, -0.5)` |
| FAST-LIO2 | [hku-mars/FAST_LIO](https://github.com/hku-mars/FAST_LIO) `ROS2` 브랜치 커밋 `a4743b0` (2025-01-15) + Jazzy용 C++17 패치 |
| Livox 의존성 | `livox_ros_driver2`의 메시지 정의만 포함한 패키지 (Livox-SDK2 불필요) |
| ROS 통신 기본값 | `ROS_DOMAIN_ID=43`, `GZ_PARTITION=aistudy-week3-43` (2주차 42와 구분) |
| FAST-LIO2 작업공간 | `~/aistudy_fastlio_ws` (`FASTLIO_WS`로 변경, 저장소 밖) |

Nav2는 실행하지 않습니다. 로봇은 키보드 teleop으로 움직이고 FAST-LIO2가 위치를 추정합니다. FAST-LIO2 결과를 Nav2에 연결하는 것은 선택 확장입니다.

## 폴더 구성

```text
week3-slam/preparation/
├── models/burger_sensors.urdf.xacro   # 2주차 모델 + /ground_truth/odom 발행 (시뮬레이터 전용)
├── config/
│   ├── bridge.yaml                    # Gazebo ↔ ROS 토픽 (2주차 + /ground_truth/odom)
│   └── fast_lio_burger.yaml           # FAST-LIO2 기본 설정
├── launch/simulation.launch.py        # Gazebo + 로봇 + 브리지 + points_to_fastlio (+ 센서 확인 RViz)
├── tools/points_to_fastlio.py         # /points → /points_fastlio (무한대 점 제거, 헤더 유지)
├── rviz/
│   ├── sensors.rviz                   # 센서 입력 확인 화면 (Fixed Frame: odom)
│   └── fast_lio.rviz                  # FAST-LIO2 지도·궤적 화면 (Fixed Frame: camera_init)
├── scripts/
│   ├── env.sh                         # 모든 터미널에서 source
│   ├── install_dependencies.sh        # apt 패키지 설치
│   ├── build_fast_lio.sh              # FAST-LIO2 받기·패치·빌드
│   ├── check_environment.sh           # 설치·빌드·파일 점검
│   ├── run_simulation.sh              # 시뮬레이션
│   ├── run_fast_lio.sh                # FAST-LIO2 (기본 설정, 원본 launch 사용)
│   └── run_teleop.sh                  # 키보드 teleop
├── patches/fast_lio_jazzy_cxx17.patch
├── third_party/livox_ros_driver2/     # 메시지 정의만 (MIT)
├── docs/                              # 교보재
└── THIRD_PARTY.md, licenses/
```

## 설치와 빌드 (처음 한 번)

```bash
cd week3-slam/preparation
bash scripts/install_dependencies.sh   # sudo apt-get install ...
bash scripts/build_fast_lio.sh         # ~/aistudy_fastlio_ws에 FAST-LIO2 빌드 (약 2분)
bash scripts/check_environment.sh      # 모두 OK인지 확인 (새 터미널에서)
```

`build_fast_lio.sh`는 고정 커밋을 받고, `patches/`의 C++17 패치를 적용하고, 메시지 전용 `livox_ros_driver2`를 함께 넣어 `colcon build`합니다. 원본 FAST_LIO는 C++14로 고정되어 있어 Jazzy에서 그대로 빌드하면 `std::is_convertible_v` 오류가 납니다.

## 실행

터미널마다 `week3-slam/preparation`에서 실행합니다. 각 스크립트가 `scripts/env.sh`를 불러오므로 도메인·작업공간 설정이 자동으로 맞습니다.

```bash
# 터미널 1: 시뮬레이션 + 센서 확인 RViz
bash scripts/run_simulation.sh            # Gazebo 창 없이: headless:=True

# 터미널 2: FAST-LIO2 (로봇이 정지한 상태에서 시작, "IMU Initial Done" 확인)
bash scripts/run_fast_lio.sh              # FAST-LIO2 RViz 끄기: rviz:=false

# 터미널 3: 키보드 teleop (i 전진, j/l 회전, k 정지, , 후진)
bash scripts/run_teleop.sh
```

로봇을 움직이면 FAST-LIO2 RViz(Fixed Frame `camera_init`)에서 `/path`가 늘어나고 `/Laser_map`이 채워집니다. 직접 만든 launch·RViz 설정으로 바꾸어 가는 예는 [Solution-HJ1](../Solution-HJ1/README.md)을 참고하세요.

## 운영자 사전 검증

2026-10-02, WSL2 Ubuntu 24.04.4 / ROS 2 Jazzy / Gazebo Sim 8.11.0 / RTX 4070 SUPER에서 이 폴더의 파일로 확인했습니다.

| 확인 | 결과 |
| --- | --- |
| FAST-LIO2 빌드 (`a4743b0` + C++17 패치 + 메시지 전용 Livox 패키지) | 성공, 약 1분 40초 |
| C++17 패치 | 원본 커밋에 `git apply` 가능, 재실행 시 "이미 적용" 감지 |
| `/points` | 10.0 Hz, 720 × 16 = 11,520점, `x y z intensity`(float32) + `ring`(uint16), RELIABLE |
| `/points_fastlio` | 10.0 Hz, 약 11,170점(무한대 약 350점 제거), 헤더 시각·프레임 유지 |
| `/imu` | 200.0 Hz, `imu_link`, 정지 시 가속도 z 9.79 m/s² |
| `/ground_truth/odom` | 50.0 Hz, `world → base_footprint`, 시작 `(-2.000, -0.500)` |
| FAST-LIO2 시작 | `IMU Initial Done` → `Initialize the map kdtree`, `/Odometry` 10.0 Hz |
| 15.6 m 경로 주행 (제자리 회전 8회) | 정답 위치 대비 수평 RMSE: FAST-LIO2 0.24 cm, 바퀴 odometry 1.25 cm (예시 답안 영상 주행, [metrics.json](../Solution-HJ1/media/metrics.json)) |
| 학생 순서대로 스크립트 실행 | `check_environment.sh` 전 항목 OK → `run_simulation.sh`(센서 RViz) → `run_fast_lio.sh`(FAST-LIO2 RViz) → 주행, 두 RViz 화면 정상 |

설정별 비교와 해석은 [docs/fastlio2.md](docs/fastlio2.md#7-설정에-따른-차이-운영자-검증-데이터)에 있습니다.

## 다음 문서

- [docs/fastlio2.md](docs/fastlio2.md): FAST-LIO2 입력·출력, 처리 순서, 기본 설정 해설
- [docs/sensors_topics_frames.md](docs/sensors_topics_frames.md): 센서·토픽·QoS·TF·시간, 점검 명령
- [docs/rviz.md](docs/rviz.md): RViz 구성과 스크린샷·영상 촬영
- [docs/troubleshooting.md](docs/troubleshooting.md): 빌드·실행 문제 해결
- [THIRD_PARTY.md](THIRD_PARTY.md): 사용한 외부 코드와 라이선스
